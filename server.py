# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2,<3", "pyyaml>=6"]
# ///
"""Agent call centre: a shared, file-backed knowledge base exposed over MCP.

Source of truth: one markdown file per entry in $CALLCENTRE_HOME/entries/ (YAML frontmatter).
Derived index:   $CALLCENTRE_HOME/.index.db (SQLite FTS5), rebuilt incrementally from file mtimes.

Every Claude Code session starts its own stdio copy of this server, so all shared state lives
in files; writes are serialised with a file lock and land via atomic rename.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import json
import os
import re
import secrets
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path

import yaml
try:  # mcp 2.x
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

HOME = Path(os.environ.get("CALLCENTRE_HOME", "~/claude-callcentre")).expanduser()
ENTRIES = HOME / "entries"
INDEX_DB = HOME / ".index.db"
LOCK_FILE = HOME / ".lock"

STALE_AFTER_FAILURES = 2      # consecutive failed reuses before an entry is marked stale
DUP_THRESHOLD = 0.55          # token Jaccard on title+symptoms above which submit refuses
REVIEW_DUP_THRESHOLD = 0.35   # lower bar for pairs the curator's `review` asks a human/agent to look at
MIN_OVERLAP = 0.2             # share of query terms an entry must contain to be returned
STRONG_OVERLAP = 0.4          # below this, hits are labelled WEAK
STOPWORDS = set("""a an and are as at be but by for from has have in is it its of on or that the
this to was were when with after before during into not no than then there these they""".split())

INSTRUCTIONS = """Shared knowledge base of problems already solved on this machine (RL training,
post-training evals, cluster/infra, environments), plus open issues nobody has solved yet.
Policy:
1. Before debugging any non-trivial failure or making a setup/config decision, call `search` with the
   error text or a symptom description. Results are compact; call `get` only for promising hits.
2. If you use an entry, call `report_outcome` afterwards (worked or not). This keeps fixes trustworthy.
3. If you solve something new and non-obvious, call `submit` with the MINIMAL fix and what did NOT work.
4. If you give up or hand off, call `open_issue` (or `log_attempt` on an existing one) so the next agent
   does not repeat your dead ends.
5. Learned something useful but can't write a clean entry? Call `report` with the raw details; a
   curator files it.
Domain tags (reuse these; add a new short one only if none fits): rl-training, sft, eval, infra, slurm, vt-arc, distributed, deepspeed, structured-output,
isaac-sim, env (RL / simulation environments), python-env (conda, pip, package versions and
installs), dataviz, observable."""

mcp = _Server("callcentre", instructions=INSTRUCTIONS)


# ----------------------------------------------------------------------------- storage

def _today() -> str:
    return dt.date.today().isoformat()


def _now() -> dt.datetime:
    return dt.datetime.now().replace(microsecond=0)


def _ensure_dirs() -> None:
    ENTRIES.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.touch(exist_ok=True)


@contextmanager
def _write_lock():
    _ensure_dirs()
    with open(LOCK_FILE, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
            _refresh_views()
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60].rstrip("-") or "entry"


def _inbox() -> Path:
    """Raw agent reports awaiting the curator (not indexed, not searchable)."""
    return HOME / "inbox"


def _new_id(title: str, folder: Path | None = None) -> str:
    """Random suffix, retried until unused. Caller must hold _write_lock."""
    while True:
        eid = f"{_slug(title)}-{secrets.token_hex(2)}"
        if not _path(eid, folder).exists():
            return eid


def _path(entry_id: str, folder: Path | None = None) -> Path:
    if not re.fullmatch(r"[a-z0-9-]+", entry_id):
        raise ValueError(f"invalid id: {entry_id!r}")
    return (folder or ENTRIES) / f"{entry_id}.md"


def _read(path: Path) -> tuple[dict, str]:
    """(frontmatter, notes). The generated human-readable view is dropped: it's derived."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), _GENERATED.sub("", m.group(2), count=1).strip()


def _write(entry: dict, notes: str = "", folder: Path | None = None) -> Path:
    """Atomic write. Caller must hold _write_lock. Entries get a rendered body for humans
    (Obsidian); the frontmatter stays the only source of truth."""
    path = _path(entry["id"], folder)
    path.parent.mkdir(parents=True, exist_ok=True)
    front = yaml.safe_dump(entry, sort_keys=False, allow_unicode=True, width=100)
    view = _render_entry(entry, bool(notes.strip())) if folder is None else ""
    body = f"---\n{front}---\n{view}" + (f"{notes.strip()}\n" if notes.strip() else "")
    _atomic_write(path, body)
    return path


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


# ----------------------------------------------------------------------------- human view
# Entries are read by agents through `get` (frontmatter as YAML) and by humans in Obsidian. The
# body between the markers is regenerated from the frontmatter on every write; notes follow it.

_BEGIN = "<!-- callcentre:begin (generated from the properties above: edit those, not this) -->"
_END = "<!-- callcentre:end -->"
_GENERATED = re.compile(r"<!-- callcentre:begin.*?<!-- callcentre:end -->\n?", re.S)
_CALLOUT = {"verified": "success", "unverified": "note", "stale": "warning", "open": "bug",
            "claimed": "bug"}
INDEX_NOTE = "INDEX.md"


def _md(text) -> str:
    """Neutralise Obsidian syntax that agent prose trips over ($..$ math, <tag> HTML, #tags),
    leaving `code spans` verbatim."""
    parts = re.split(r"(`+[^`]*?`+)", str(text))
    for i in range(0, len(parts), 2):
        p = parts[i].replace("\\", "\\\\").replace("$", "\\$").replace("<", "\\<")
        parts[i] = re.sub(r"(^|\s)#(?=[A-Za-z])", r"\1\\#", p, flags=re.M)
    return "".join(parts)


def _fence(lines: list[str], lang: str = "text") -> str:
    body = "\n".join(str(l) for l in lines)
    ticks = "`" * max(3, max((len(r) for r in re.findall(r"`+", body)), default=0) + 1)
    return f"{ticks}{lang}\n{body}\n{ticks}"


def _bullets(items) -> str:
    return "\n".join("- " + _md(x).replace("\n", "\n  ") for x in _as_list(items))


def _tag(x) -> str:
    t = re.sub(r"[^\w/-]+", "-", str(x)).strip("-")
    return t if re.search(r"[A-Za-z_]", t) else f"t-{t}"


def _link(eid: str, title) -> str:
    return f"[[{eid}|{re.sub(r'[][|#^]+', ' ', str(title)).strip()}]]"


def _render_entry(e: dict, has_notes: bool) -> str:
    kind, status = e.get("kind") or "fix", e.get("status") or "unverified"
    badge = [kind.replace("_", " "), status]
    if kind == "open_issue":
        badge.append(f"{len(_as_list(e.get('attempts')))} attempts logged")
        if e.get("claimed_by"):
            badge.append(f"claimed by {e['claimed_by']} until {e.get('claim_expires')}")
    else:
        badge.append(f"used {int(e.get('uses') or 0)}×, failed {int(e.get('failures') or 0)}×")
        if e.get("last_verified"):
            badge.append(f"last verified {e['last_verified']}")
    tags = [f"#{_tag(d)}" for d in _as_list(e.get("domain"))] + [f"#kind/{kind}", f"#status/{status}"]
    out = [_BEGIN, f"# {_md(e.get('title', e.get('id', '')))}", "",
           f"> [!{_CALLOUT.get(status, 'info')}] {' · '.join(_md(b) for b in badge)}",
           f"> {' '.join(tags)}", ""]

    def section(name, content):
        if content:
            out.extend([f"## {name}", content, ""])

    section("Symptoms", _fence(_as_list(e.get("symptoms"))) if e.get("symptoms") else "")
    section("Repro", _md(e.get("repro") or ""))
    section("Root cause", _md(e.get("root_cause") or ""))
    section("Convention" if kind == "convention" else "Fix", _md(e.get("fix") or ""))
    section("Attempts so far", _bullets(e.get("attempts")))
    section("Failed attempts", _bullets(e.get("failed_attempts")))
    section("Verify", _md(e.get("verify") or ""))
    stack = e.get("stack") or {}
    if isinstance(stack, dict) and stack:
        rows = [f"| {_md(k)} | {_md(_flatten(v)).replace('|', '/')} |" for k, v in stack.items()]
        section("Stack", "\n".join(["| | |", "|---|---|", *rows]))
    elif stack:
        section("Stack", _md(_flatten(stack)))
    section("Outcome reports", _bullets(e.get("outcome_notes")))
    meta = [f"created {e['created']}"] if e.get("created") else []
    if e.get("resolved_by"):
        meta.append(f"resolved by {e['resolved_by']}")
    if e.get("merged_from"):
        meta.append("merged from " + ", ".join(f"`{m}`" for m in _as_list(e["merged_from"])))
    meta.append(f"id `{e.get('id', '')}`")
    out.extend([f"<small>{' · '.join(meta)}</small>", ""])
    if has_notes:
        out.extend(["## Notes", ""])
    out.append(_END)
    return "\n".join(out) + "\n"


_MARK = {"verified": "✅", "unverified": "🆕", "stale": "⚠️"}
DOMAINS_DIR = "domains"
# Obsidian graph: colour groups per domain (+ open issues), and a filter that hides non-knowledge notes.
GRAPH_FILTER = "-path:inbox -path:commands -file:README -file:CLAUDE -file:INDEX"
_OPEN_COLOR = 0xE5484D
_PALETTE = [0x4E79A7, 0xF28E2B, 0x59A14F, 0xB07AA1, 0xEDC948, 0x76B7B2, 0xFF9DA7, 0x9C755F,
            0x8CD17D, 0x86BCB6, 0xD4A6C8, 0xF1CE63, 0x499894, 0xBAB0AC]


def _view_rows() -> list[dict]:
    rows = []
    for p in sorted(ENTRIES.glob("*.md")) if ENTRIES.exists() else []:
        e = _meta_or_empty(p)
        if e:
            e.setdefault("id", p.stem)
            rows.append(e)
    return sorted(rows, key=lambda e: str(e.get("title", "")).lower())


def _entry_line(e: dict) -> str:
    if e.get("kind") == "open_issue":
        return f"- 🔴 {_link(e['id'], e.get('title', ''))} · {len(_as_list(e.get('attempts')))} attempts"
    line = f"- {_MARK.get(e.get('status') or 'unverified', '•')} {_link(e['id'], e.get('title', ''))}"
    return line + (f" · used {e['uses']}×" if e.get("uses") else "")


def _domains_of(e: dict) -> list[str]:
    return [_tag(d) for d in _as_list(e.get("domain"))] or ["untagged"]


def _render_index(rows: list[dict]) -> str:
    """INDEX.md: the vault's home note. Deterministic, so unchanged data means no git churn."""
    issues = [e for e in rows if e.get("kind") == "open_issue"]
    by_domain: dict[str, list[str]] = {}
    for e in rows:
        if e.get("kind") != "open_issue":
            for d in _domains_of(e):
                by_domain.setdefault(d, []).append(_entry_line(e))
    inbox = sorted(_inbox().glob("*.md")) if _inbox().exists() else []
    out = ["---", "tags: [callcentre/index]", "---", "# Call centre", "",
           "> [!info] Generated by server.py on every change; don't edit by hand.",
           f"> {len(rows) - len(issues)} entries · {len(issues)} open issues · {len(inbox)} inbox "
           "items awaiting curation", "> ✅ verified · 🆕 unverified · ⚠️ stale (hidden from search) · 🔴 open", ""]
    if issues:
        out += [f"## Open issues ({len(issues)})", *map(_entry_line, issues), ""]
    for d in sorted(by_domain, key=lambda d: (d == "untagged", -len(by_domain[d]), d)):
        out += [f"## [[{DOMAINS_DIR}/{d}|{d}]] ({len(by_domain[d])})", *by_domain[d], ""]
    if inbox:
        out += [f"## Inbox ({len(inbox)})"]
        out += [f"- {_link(p.stem, _meta_or_empty(p).get('title', p.stem))}" for p in inbox]
        out.append("")
    return "\n".join(out)


def _render_domain(d: str, entries: list[dict]) -> str:
    """One hub note per domain: entries cluster around it in Obsidian's graph."""
    issues = [e for e in entries if e.get("kind") == "open_issue"]
    fixes = [e for e in entries if e.get("kind") != "open_issue"]
    tag = "" if d == "untagged" else f" #{d}"
    out = ["---", "tags: [callcentre/domain]", "---", f"# {d}", "",
           f"> [!info] Generated: {len(fixes)} entries and {len(issues)} open issues tagged "
           f"`{d}`. Back to [[INDEX|the index]].", f">{tag} #callcentre/domain", ""]
    if issues:
        out += [f"## Open issues ({len(issues)})", *map(_entry_line, issues), ""]
    if fixes:
        out += [f"## Entries ({len(fixes)})", *map(_entry_line, fixes), ""]
    return "\n".join(out)


def _graph_config(cfg: dict, counts: dict[str, int]) -> dict:
    """Merge our colour groups into Obsidian's graph.json: keep colours the user picked for our
    queries, keep the user's own non-tag groups, and set the filter only if it's empty/ours."""
    old = [g for g in cfg.get("colorGroups") or [] if isinstance(g, dict)]
    existing = {g.get("query"): g for g in old}
    # A domain gets a group once it has 2+ notes, and keeps it (and its colour) after that.
    wanted = [d for d in sorted(counts, key=lambda d: (-counts[d], d))
              if counts[d] >= 2 or f"tag:#{d}" in existing]
    managed = {"tag:#kind/open_issue", *(f"tag:#{d}" for d in wanted)}
    user = [g for g in old if g.get("query") not in managed]  # never drop someone else's group
    colors: dict[str, int] = {}
    for d in wanted:  # colours stick to a domain once assigned
        g = existing.get(f"tag:#{d}")
        if g and isinstance(g.get("color"), dict) and "rgb" in g["color"]:
            colors[d] = g["color"]["rgb"]
    free = [c for c in _PALETTE if c not in colors.values()]
    for d in wanted:
        if d not in colors and free:
            colors[d] = free.pop(0)
    q = "tag:#kind/open_issue"
    ours = [existing.get(q) or {"query": q, "color": {"a": 1, "rgb": _OPEN_COLOR}}]
    # Obsidian colours a node by the FIRST matching group: most specific (rarest) domains first.
    for d in sorted(colors, key=lambda d: (counts[d], d)):
        ours.append({"query": f"tag:#{d}", "color": {"a": 1, "rgb": colors[d]}})
    out = {**cfg, "colorGroups": ours + user}
    if out.get("search", "") in ("", GRAPH_FILTER):
        out["search"] = GRAPH_FILTER
    return out


def _refresh_views() -> None:
    """INDEX.md, domains/*.md and (if the vault is open in Obsidian) graph colours."""
    try:
        rows = _view_rows()
        by_domain: dict[str, list[dict]] = {}
        for e in rows:
            for d in _domains_of(e):
                by_domain.setdefault(d, []).append(e)
        _write_if_changed(HOME / INDEX_NOTE, _render_index(rows))
        ddir = HOME / DOMAINS_DIR
        if by_domain:
            ddir.mkdir(exist_ok=True)
        for d, es in by_domain.items():
            _write_if_changed(ddir / f"{d}.md", _render_domain(d, es))
        for p in ddir.glob("*.md") if ddir.exists() else []:
            if p.stem not in by_domain:
                p.unlink()
        graph = HOME / ".obsidian" / "graph.json"
        if graph.exists():
            cfg = json.loads(graph.read_text(encoding="utf-8") or "{}")
            counts = {d: len(es) for d, es in by_domain.items() if d != "untagged"}
            new = _graph_config(cfg, counts)
            if new != cfg:
                _atomic_write(graph, json.dumps(new, indent=2))
    except Exception as err:  # never fail a write over the derived views; stdout is the MCP pipe
        print(f"callcentre: could not refresh views: {err}", file=sys.stderr)


def _write_if_changed(path: Path, text: str) -> None:
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        _atomic_write(path, text)


def _render_all() -> str:
    """Rewrite every entry in the current layout (frontmatter and notes unchanged)."""
    n, bad = _rerender(sorted(ENTRIES.glob("*.md")) if ENTRIES.exists() else [])
    return f"rendered {n} entries" + (f"; skipped unparseable: {', '.join(bad)}" if bad else "")


def _render_missing() -> int:
    """Render entries whose view is missing or from another layout version (e.g. written by an
    older server still running in some session). Runs at server start; a no-op when all current."""
    if not ENTRIES.exists():
        return 0
    todo = [p for p in sorted(ENTRIES.glob("*.md")) if _BEGIN not in p.read_text(encoding="utf-8")]
    return _rerender(todo)[0] if todo else 0


def _rerender(paths: list[Path]) -> tuple[int, list[str]]:
    n, bad = 0, []
    with _write_lock():
        for p in paths:
            try:
                e, notes = _read(p)
                if not isinstance(e, dict) or e.get("id") != p.stem:
                    raise ValueError("missing or mismatched id")
            except Exception:
                bad.append(p.name)
                continue
            _write(e, notes)
            n += 1
    return n, bad


def _locate(entry_id: str, folder: Path | None = None) -> Path:
    folder = folder or ENTRIES
    path = _path(entry_id, folder)
    if path.exists():
        return path
    hits = sorted(folder.glob(f"{entry_id}*.md"))  # allow unique prefix match
    if not hits:  # merged away by the curator: follow the redirect
        hits = [p for p in folder.glob("*.md") if entry_id in p.read_text(encoding="utf-8")
                and entry_id in _as_list(_meta_or_empty(p).get("merged_from"))]
    if len(hits) != 1:
        raise FileNotFoundError(f"no unique entry for id {entry_id!r}")
    return hits[0]


def _meta_or_empty(path: Path) -> dict:
    try:
        e = _read(path)[0]
    except Exception:
        return {}
    return e if isinstance(e, dict) else {}


def _load(entry_id: str) -> tuple[dict, str]:
    return _read(_locate(entry_id))


# ----------------------------------------------------------------------------- index

def _db() -> sqlite3.Connection:
    _ensure_dirs()
    con = sqlite3.connect(INDEX_DB, timeout=10)
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript("""
        CREATE TABLE IF NOT EXISTS meta(
            id TEXT PRIMARY KEY, mtime INTEGER, kind TEXT, status TEXT, domain TEXT,
            title TEXT, oneline TEXT, uses INTEGER, failures INTEGER, last_verified TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(
            id UNINDEXED, title, symptoms, body, tokenize='porter unicode61');
    """)
    return con


def _as_list(x) -> list:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def _flatten(x) -> str:
    if isinstance(x, dict):
        return " ".join(f"{k} {_flatten(v)}" for k, v in x.items())
    if isinstance(x, list):
        return " ".join(_flatten(v) for v in x)
    return "" if x is None else str(x)


def _oneline(e: dict) -> str:
    if e.get("kind") == "open_issue":
        who = e.get("claimed_by")
        n = len(_as_list(e.get("attempts")))
        state = f"claimed by {who}" if who and not _lease_expired(e) else "unclaimed"
        return f"OPEN ({state}, {n} attempts logged)"
    text = str(e.get("fix") or "").strip().splitlines()
    first = text[0] if text else ""
    return first[:160] + ("…" if len(first) > 160 else "")


def _sync(con: sqlite3.Connection) -> None:
    """Bring the index in line with the files on disk (cheap: stat-only for unchanged files)."""
    on_disk = {p.stem: p for p in ENTRIES.glob("*.md")}
    indexed = dict(con.execute("SELECT id, mtime FROM meta").fetchall())
    with con:
        for gone in set(indexed) - set(on_disk):
            con.execute("DELETE FROM meta WHERE id=?", (gone,))
            con.execute("DELETE FROM fts WHERE id=?", (gone,))
        for eid, p in on_disk.items():
            mtime = p.stat().st_mtime_ns
            if indexed.get(eid) == mtime:
                continue
            try:
                e, notes = _read(p)
            except Exception:
                continue  # malformed hand edit: skip rather than break search
            con.execute("DELETE FROM fts WHERE id=?", (eid,))
            con.execute(
                "INSERT OR REPLACE INTO meta VALUES (?,?,?,?,?,?,?,?,?,?)",
                (eid, mtime, e.get("kind"), e.get("status"), " ".join(_as_list(e.get("domain"))),
                 e.get("title", ""), _oneline(e), int(e.get("uses") or 0),
                 int(e.get("failures") or 0), str(e.get("last_verified") or "")))
            body = _flatten({k: e.get(k) for k in
                             ("root_cause", "fix", "failed_attempts", "attempts", "repro",
                              "verify", "domain", "stack")}) + " " + notes
            con.execute("INSERT INTO fts VALUES (?,?,?,?)",
                        (eid, e.get("title", ""), _norm_symptoms(e), body))


def _tokens(text: str) -> list[str]:
    toks = [t.lower() for t in re.findall(r"[A-Za-z0-9_]+", text)]
    seen, out = set(), []
    for t in toks:
        if len(t) < 2 or t in STOPWORDS or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out[:40]


def _search(query: str, domain: str | None, kind: str | None, limit: int,
            include_stale: bool) -> list[dict]:
    toks = _tokens(query)
    if not toks:
        return []
    match = " OR ".join(f'"{t}"' for t in toks)
    sql = """SELECT m.id, m.kind, m.status, m.title, m.oneline, m.uses, m.failures,
                    m.last_verified, bm25(fts, 10.0, 6.0, 1.0) AS score
             FROM fts JOIN meta m ON m.id = fts.id WHERE fts MATCH ?"""
    args: list = [match]
    if domain:
        sql += " AND m.domain LIKE ?"
        args.append(f"%{domain}%")
    if kind:
        sql += " AND m.kind = ?"
        args.append(kind)
    if not include_stale:
        sql += " AND (m.status IS NULL OR m.status != 'stale')"  # hand-written entries may lack status
    sql += " ORDER BY score LIMIT ?"
    args.append(limit)
    con = _db()
    try:
        _sync(con)
        rows = con.execute(sql, args).fetchall()
    finally:
        con.close()
    cols = ["id", "kind", "status", "title", "summary", "uses", "failures", "last_verified", "_s"]
    hits = [{k: v for k, v in zip(cols, r) if k != "_s"} for r in rows]
    for h in hits:
        h["status"] = h["status"] or "unverified"
    return hits


def _jaccard(a: str, b: str) -> float:
    sa, sb = set(_tokens(a)), set(_tokens(b))
    return len(sa & sb) / len(sa | sb) if sa and sb else 0.0


def _find_duplicates(title: str, symptoms: list[str]) -> list[dict]:
    probe = f"{title} {' '.join(symptoms)}"
    out = []
    for hit in _search(probe, None, None, 5, include_stale=True):
        e, _ = _load(hit["id"])
        sim = _jaccard(probe, f"{e.get('title', '')} {_flatten(e.get('symptoms'))}")
        if sim >= DUP_THRESHOLD:
            out.append({"id": hit["id"], "title": hit["title"], "status": hit["status"],
                        "similarity": round(sim, 2)})
    return out


def _lease_expired(e: dict) -> bool:
    exp = e.get("claim_expires")
    if not exp:
        return True
    try:
        return dt.datetime.fromisoformat(str(exp)) < _now()
    except ValueError:
        return True


def _fmt_hits(hits: list[dict]) -> str:
    if not hits:
        return "No matches. If you solve this, call `submit`; if you get stuck, call `open_issue`."
    lines = []
    for h in hits:
        trust = f"{h['status']}, used {h['uses']}x, failed {h['failures']}x"
        if h.get("last_verified"):
            trust += f", last verified {h['last_verified']}"
        lines.append(f"- [{h['id']}] ({h['kind']}; {trust})\n  {h['title']}\n  → {h['summary']}")
    return "\n".join(lines) + "\n\nCall `get(id)` for full details on a promising hit."


# ----------------------------------------------------------------------------- query normalisation

_NOISE = [
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?"), " "),   # timestamps
    (re.compile(r"\b\d{2}:\d{2}:\d{2}(?:[.,]\d+)?\b"), " "),
    (re.compile(r"\[(?:rank|default)?\d+\]:?", re.I), " "),                    # [rank3]: prefixes
    (re.compile(r"0x[0-9a-f]+", re.I), " "),                                    # addresses
    (re.compile(r"(?:/[\w.\-]+)+/([\w.\-]+\.py)"), r"\1"),                      # paths -> file.py
    (re.compile(r"(?:/[\w.\-]+){2,}/?"), " "),                                  # other paths
    (re.compile(r"\b[a-z]+-[a-z]+\d{2,}\b", re.I), " "),                      # hostnames: tc-gpu017
    (re.compile(r"\b\d+(\.\d+)?\b"), " "),                                      # bare numbers
    (re.compile(r"\s+"), " "),
]


# Wrapper lines present in nearly every failed job: shown for context, never used for matching
# (unless they are the only signal, e.g. a job killed purely for hitting its time limit).
_GENERIC = re.compile(r"(srun: error: .*exit(ed)? with exit code|slurmstepd: error: \*+ JOB ON CANCELLED AT"
                      r"|^exit code$|^Aborted)", re.I)


def _specific(lines: list[str]) -> list[str]:
    """Drop generic wrapper lines unless nothing else is left."""
    lines = [str(l) for l in lines]
    return [l for l in lines if not _GENERIC.search(_normalize(l))] or lines


def _norm_symptoms(e: dict) -> str:
    """Symptoms as matched: generic wrapper lines dropped, run-specific noise stripped."""
    lines = _specific([str(x) for x in _as_list(e.get("symptoms"))])
    return " ".join(_normalize(l) for l in lines)


def _normalize(line: str) -> str:
    for pat, rep in _NOISE:
        line = pat.sub(rep, line)
    return line.strip(" :-|>")



# ----------------------------------------------------------------------------- tools


@mcp.tool()
def search(query: str, domain: str | None = None, kind: str | None = None,
           limit: int = 5, include_stale: bool = False) -> str:
    """Search solved problems, conventions and open issues. Pass the error lines or symptom
    description you were given (job ids, hostnames, ranks and numbers are stripped automatically).
    Optional filters: domain (e.g. 'rl-training', 'eval', 'infra', 'python-env', 'isaac-sim'),
    kind ('fix' | 'convention' | 'open_issue'). Returns compact one-line summaries; use `get` for
    details. Hits marked WEAK share only part of the query's terms: read before trusting."""
    lines = [l for l in (_normalize(x) for x in query.splitlines()) if l]
    probe_text = " ".join(_specific(lines)) if lines else query
    probe = set(_tokens(probe_text))
    if not probe:
        return "Query has no searchable terms."
    kept = []
    for h in _search(probe_text, domain, kind, 15, include_stale):
        e, _ = _load(h["id"])
        if e.get("kind") == "open_issue":  # claim state depends on the clock, not just the file
            h["status"] = "claimed" if e.get("claimed_by") and not _lease_expired(e) else "open"
            h["summary"] = _oneline(e)
        syms = _norm_symptoms(e)
        doc = set(_tokens(f"{e.get('title', '')} {syms} {e.get('root_cause') or ''}"))
        overlap = len(probe & doc) / len(probe)
        if overlap < MIN_OVERLAP:
            continue  # BM25 always returns something; this drops hits sharing only generic words
        if overlap < STRONG_OVERLAP:
            h["status"] = f"WEAK match; {h['status']}"
        kept.append(h)
        if len(kept) >= max(1, min(limit, 10)):
            break
    return _fmt_hits(kept)


@mcp.tool()
def get(id: str) -> str:
    """Fetch the full entry (symptoms, root cause, minimal fix, failed attempts, verify step)."""
    try:
        e, notes = _load(id)
    except (FileNotFoundError, ValueError) as err:
        return str(err)
    e = {k: v for k, v in e.items() if v not in (None, "", [], {})
         and k not in ("consecutive_failures", "claim_expires")}  # drop empties: saves tokens
    out = yaml.safe_dump(e, sort_keys=False, allow_unicode=True, width=100)
    return out + (f"\nnotes:\n{notes}" if notes else "")


@mcp.tool()
def submit(kind: str, title: str, symptoms: list[str], fix: str,
           root_cause: str = "", failed_attempts: list[str] | None = None, verify: str = "",
           domain: list[str] | None = None, stack: dict | None = None, notes: str = "",
           verified_now: bool = False, force: bool = False) -> str:
    """Record a newly solved problem (kind='fix') or a working convention (kind='convention',
    e.g. the canonical way to run an eval harness). Write the MINIMAL fix, not the debugging story.
    symptoms: exact error strings and/or observable behaviour. failed_attempts: plausible things
    that did NOT work. verify: a command or check that confirms the fix. stack: relevant versions,
    e.g. {"trl": "0.x", "vllm": "0.x"}. domain: reuse the tags in the server instructions, e.g.
    ["rl-training", "python-env"]; `env` means RL/simulation environments, `python-env` means
    conda/pip/package versions. Set verified_now=True only if you confirmed it worked in this
    session. Refuses near-duplicates unless force=True (prefer report_outcome on the existing entry)."""
    if kind not in ("fix", "convention"):
        return "kind must be 'fix' or 'convention' (use open_issue for unsolved problems)."
    if not fix.strip() or not symptoms:
        return "fix and at least one symptom are required."
    symptoms = _specific(symptoms)
    with _write_lock():
        dups = _find_duplicates(title, symptoms)
        if dups and not force:
            return ("Not saved: looks like an existing entry. Use report_outcome on it, or resubmit "
                    f"with force=True if genuinely different.\n{yaml.safe_dump(dups, sort_keys=False)}")
        entry = {
            "id": _new_id(title), "kind": kind, "title": title,
            "domain": domain or [], "stack": stack or {}, "symptoms": symptoms,
            "root_cause": root_cause, "fix": fix, "failed_attempts": failed_attempts or [],
            "verify": verify, "status": "verified" if verified_now else "unverified",
            "uses": 1 if verified_now else 0, "failures": 0, "consecutive_failures": 0,
            "created": _today(), "last_verified": _today() if verified_now else None,
        }
        _write(entry, notes)
    return f"Saved as {entry['id']} ({entry['status']})."


@mcp.tool()
def report_outcome(id: str, worked: bool, note: str = "") -> str:
    """Report whether applying an entry's fix/convention worked. Always call this after using an
    entry: successes mark it verified; repeated failures mark it stale so others stop trusting it."""
    with _write_lock():
        try:
            e, notes = _load(id)
        except (FileNotFoundError, ValueError) as err:
            return str(err)
        if e.get("kind") == "open_issue":
            return "That is an open issue; use log_attempt or resolve_issue instead."
        if worked:
            e["uses"] = int(e.get("uses") or 0) + 1
            e["consecutive_failures"] = 0
            e["last_verified"] = _today()
            e["status"] = "verified"
        else:
            e["failures"] = int(e.get("failures") or 0) + 1
            e["consecutive_failures"] = int(e.get("consecutive_failures") or 0) + 1
            if e["consecutive_failures"] >= STALE_AFTER_FAILURES:
                e["status"] = "stale"
        if note.strip():
            e.setdefault("outcome_notes", []).append(
                f"{_today()} {'OK' if worked else 'FAILED'}: {note.strip()}")
            e["outcome_notes"] = e["outcome_notes"][-10:]
        _write(e, notes)
    return f"Recorded. {e['id']} is now {e['status']} (uses={e.get('uses')}, failures={e.get('failures')})."


@mcp.tool()
def open_issue(title: str, symptoms: list[str], repro: str = "",
               attempts: list[str] | None = None, domain: list[str] | None = None,
               stack: dict | None = None, force: bool = False) -> str:
    """Log an unsolved problem so other agents can pick it up. Include everything you tried in
    attempts (with the result of each) so nobody repeats your dead ends. domain: reuse the tags in
    the server instructions."""
    symptoms = _specific(symptoms)
    with _write_lock():
        dups = _find_duplicates(title, symptoms)
        if dups and not force:
            return ("Not saved: a similar entry exists. Use log_attempt on it (if open) or "
                    f"resubmit with force=True.\n{yaml.safe_dump(dups, sort_keys=False)}")
        entry = {
            "id": _new_id(title), "kind": "open_issue", "title": title,
            "domain": domain or [], "stack": stack or {}, "symptoms": symptoms,
            "repro": repro, "attempts": attempts or [], "status": "open",
            "claimed_by": None, "claim_expires": None, "created": _today(),
        }
        _write(entry)
    return f"Opened {entry['id']}."


@mcp.tool()
def claim_issue(id: str, agent: str, lease_minutes: int = 120) -> str:
    """Claim an open issue before working on it so two agents don't duplicate effort. The claim
    expires after lease_minutes; re-claim to extend. agent: any stable label for yourself."""
    with _write_lock():
        try:
            e, notes = _load(id)
        except (FileNotFoundError, ValueError) as err:
            return str(err)
        if e.get("kind") != "open_issue":
            return "Not an open issue."
        holder = e.get("claimed_by")
        if holder and holder != agent and not _lease_expired(e):
            return f"Already claimed by {holder} until {e['claim_expires']}."
        e["claimed_by"] = agent
        e["claim_expires"] = (_now() + dt.timedelta(minutes=lease_minutes)).isoformat()
        e["status"] = "claimed"
        _write(e, notes)
    return f"Claimed {e['id']} until {e['claim_expires']}."


@mcp.tool()
def log_attempt(id: str, attempt: str, result: str, agent: str = "unknown") -> str:
    """Append something you tried on an open issue and what happened, even if it failed."""
    with _write_lock():
        try:
            e, notes = _load(id)
        except (FileNotFoundError, ValueError) as err:
            return str(err)
        if e.get("kind") != "open_issue":
            return "Not an open issue."
        e.setdefault("attempts", []).append(f"[{_today()} {agent}] {attempt} → {result}")
        _write(e, notes)
    return f"Logged ({len(e['attempts'])} attempts on {e['id']})."


@mcp.tool()
def resolve_issue(id: str, fix: str, root_cause: str = "", verify: str = "",
                  agent: str = "unknown") -> str:
    """Close an open issue with its solution. Converts it into a verified 'fix' entry; previously
    logged attempts are kept as failed_attempts. Only call after confirming the fix works."""
    with _write_lock():
        try:
            e, notes = _load(id)
        except (FileNotFoundError, ValueError) as err:
            return str(err)
        if e.get("kind") != "open_issue":
            return "Not an open issue."
        resolved = {
            "id": e["id"], "kind": "fix", "title": e["title"], "domain": e.get("domain", []),
            "stack": e.get("stack", {}), "symptoms": e.get("symptoms", []),
            "root_cause": root_cause, "fix": fix, "failed_attempts": e.get("attempts", []),
            "verify": verify, "repro": e.get("repro", ""), "status": "verified", "uses": 1,
            "failures": 0, "consecutive_failures": 0, "created": e.get("created"),
            "resolved_by": agent, "last_verified": _today(),
        }
        _write(resolved, notes)
    return f"Resolved {e['id']} → verified fix."


@mcp.tool()
def report(title: str, details: str, agent: str = "unknown", project: str = "",
           domain: list[str] | None = None) -> str:
    """Send raw findings to the curator's inbox when you learned something reusable but can't
    write a clean entry (no time, root cause unclear, observations or gotchas rather than a fix).
    details: paste error lines verbatim, what you tried and what happened, versions, commands.
    project: repo or job it came from. domain: tags from the server instructions, if obvious.
    A curator turns reports into proper entries; until then
    they are NOT searchable, so prefer `submit` / `open_issue` when you can fill them in."""
    if not title.strip() or not details.strip():
        return "title and details are required."
    with _write_lock():
        item = {"id": _new_id(title, _inbox()), "title": title.strip(), "agent": agent,
                "project": project, "domain": domain or [], "created": _now().isoformat()}
        _write(item, details, _inbox())
    return f"Queued {item['id']} for the curator (not searchable until filed)."


# ----------------------------------------------------------------------------- curation
# CLI-only: ordinary agents don't see these. All writes take the lock, so curating is safe while
# other sessions are reading and writing.

def _union(*lists) -> list:
    out: list = []
    for x in lists:
        for v in _as_list(x):
            if v not in out:
                out.append(v)
    return out


def _close_inbox(item_id: str, **fields) -> str:
    with _write_lock():
        try:
            src = _locate(item_id, _inbox())
        except (FileNotFoundError, ValueError) as err:
            return str(err).replace("entry", "inbox item")
        item, details = _read(src)
        item.update(fields, closed=_now().isoformat())
        _write(item, details, _inbox() / "done")
        src.unlink()
    return f"Closed inbox item {item['id']}."


def _file_inbox(item_id: str, entry_ids: list[str]) -> str:
    """Record which entries an inbox item became and move it to inbox/done/."""
    try:
        full = [_load(e)[0]["id"] for e in entry_ids]
    except (FileNotFoundError, ValueError) as err:
        return f"Not filed: {err}"
    return _close_inbox(item_id, filed_as=full)


def _dismiss_inbox(item_id: str, reason: str) -> str:
    if not reason.strip():
        return "Give a reason for dismissing."
    return _close_inbox(item_id, dismissed=reason.strip())


def _retag(entry_id: str, domains: list[str]) -> str:
    with _write_lock():
        try:
            path = _locate(entry_id)
        except (FileNotFoundError, ValueError) as err:
            return str(err)
        e, notes = _read(path)
        e["domain"] = domains
        _write(e, notes)
    return f"{e['id']} domain = {domains}."


_STATUSES = {"fix": ("verified", "unverified", "stale"), "convention": ("verified", "unverified", "stale"),
             "open_issue": ("open", "claimed")}


def _set_field(entry_id: str, field: str, raw: str) -> str:
    """Curator correction of one frontmatter field. raw is YAML (`null` clears; dates stay strings)."""
    if field in ("id", "kind"):
        return f"{field} can't be changed with set (use submit/merge/resolve_issue)."
    if not re.fullmatch(r"[a-z_]+", field):
        return f"invalid field: {field!r}"
    try:
        value = yaml.safe_load(raw) if raw.strip() else None
    except yaml.YAMLError as err:
        return f"value is not valid YAML: {err}"
    if isinstance(value, (dt.date, dt.datetime)):
        value = value.isoformat()
    with _write_lock():
        try:
            path = _locate(entry_id)
        except (FileNotFoundError, ValueError) as err:
            return str(err)
        e, notes = _read(path)
        allowed = _STATUSES.get(e.get("kind"), ())
        if field == "status" and value not in allowed:
            return f"status for a {e.get('kind')} must be one of {list(allowed)}."
        old = e.get(field)
        e[field] = value
        _write(e, notes)
    return f"{e['id']} {field}: {old!r} -> {value!r}."


def _merge(keep_id: str, drop_id: str) -> str:
    """Fold drop into keep: union symptoms/attempts/domains, sum trust counters, keep both fixes,
    delete drop. Old ids keep resolving via merged_from."""
    with _write_lock():
        try:
            kpath, dpath = _locate(keep_id), _locate(drop_id)
        except (FileNotFoundError, ValueError) as err:
            return str(err)
        if kpath == dpath:
            return "Cannot merge an entry into itself."
        keep, knotes = _read(kpath)
        drop, dnotes = _read(dpath)
        if keep.get("kind") == "open_issue":
            return "keep must be a fix or convention (resolve_issue the open issue first)."
        keep["domain"] = _union(keep.get("domain"), drop.get("domain"))
        keep["symptoms"] = _union(keep.get("symptoms"), drop.get("symptoms"))
        keep["failed_attempts"] = _union(keep.get("failed_attempts"), drop.get("failed_attempts"),
                                         drop.get("attempts"))
        keep["stack"] = {**(drop.get("stack") or {}), **(keep.get("stack") or {})}
        extra = []
        for k in ("root_cause", "verify", "repro"):
            dv = str(drop.get(k) or "").strip()
            if not keep.get(k) and dv:
                keep[k] = drop[k]
            elif dv and dv != str(keep.get(k) or "").strip():  # both set: don't lose drop's
                extra.append(f"{k.replace('_', ' ').capitalize()} from merged "
                             f"{drop.get('id', dpath.stem)}: {dv}")
        for k in ("uses", "failures"):
            keep[k] = int(keep.get(k) or 0) + int(drop.get(k) or 0)
        verified = [str(x) for x in (keep.get("last_verified"), drop.get("last_verified")) if x]
        keep["last_verified"] = max(verified) if verified else None
        if keep.get("status") != "verified" and drop.get("status") == "verified":
            keep["status"], keep["consecutive_failures"] = "verified", 0
        if keep.get("outcome_notes") or drop.get("outcome_notes"):
            keep["outcome_notes"] = _union(keep.get("outcome_notes"), drop.get("outcome_notes"))[-10:]
        keep["merged_from"] = _union(keep.get("merged_from"), [drop.get("id", dpath.stem)],
                                     drop.get("merged_from"))
        dfix = str(drop.get("fix") or "").strip()
        if dfix and dfix != str(keep.get("fix") or "").strip():
            extra.append(f"Alternative fix from merged {drop.get('id', dpath.stem)}: {dfix}")
        if dnotes:
            extra.append(dnotes)
        _write(keep, "\n\n".join([knotes, *extra]).strip())
        dpath.unlink()
    return f"Merged {drop.get('id', dpath.stem)} into {keep['id']}."


def _review() -> str:
    """Everything the curator should look at, most actionable first."""
    entries, broken = [], []
    for p in sorted(ENTRIES.glob("*.md")) if ENTRIES.exists() else []:
        try:
            e, _ = _read(p)
        except Exception:
            e = None
        if not isinstance(e, dict) or not e:
            broken.append(p.name)
            continue
        e.setdefault("id", p.stem)
        entries.append(e)
    inbox = []
    for p in sorted(_inbox().glob("*.md")) if _inbox().exists() else []:
        item = _meta_or_empty(p)
        inbox.append(f"[{p.stem}] {item.get('title', '?')}  ({item.get('agent', '?')}"
                     + (f", {item['project']}" if item.get("project") else "")
                     + f", {str(item.get('created', '?'))[:10]})")
    dups = []
    keyed = [(e, f"{e.get('title', '')} {_flatten(e.get('symptoms'))}") for e in entries]
    for i, (a, ta) in enumerate(keyed):
        for b, tb in keyed[i + 1:]:
            sim = _jaccard(ta, tb)
            if sim >= REVIEW_DUP_THRESHOLD:
                dups.append((sim, f"{a['id']} ~ {b['id']}  (similarity {sim:.2f})"))
    fixes = [e for e in entries if e.get("kind") != "open_issue"]
    issues = [e for e in entries if e.get("kind") == "open_issue"]
    sections = [
        ("Inbox", inbox),
        ("Possible duplicates", [d for _, d in sorted(dups, reverse=True)]),
        ("Unparseable files", broken),
        ("Untagged (no domain)", [f"[{e['id']}] {e.get('title', '')}" for e in entries
                                  if not e.get("domain")]),
        ("Stale", [f"[{e['id']}] {e.get('title', '')}  (failed {e.get('failures', 0)}x)"
                   for e in fixes if e.get("status") == "stale"]),
        ("Unverified", [f"[{e['id']}] {e.get('title', '')}  (since {e.get('created', '?')})"
                        for e in fixes if e.get("status") in (None, "unverified")]),
        ("Open issues", [f"[{e['id']}] {e.get('title', '')}  {_oneline(e)}" for e in issues]),
    ]
    out = [f"## {name} ({len(rows)})\n" + "\n".join(f"- {r}" for r in rows)
           for name, rows in sections if rows]
    if not out:
        return "Nothing to review."
    counts: dict[str, int] = {}
    for e in entries:
        for d in _as_list(e.get("domain")):
            counts[str(d)] = counts.get(str(d), 0) + 1
    if counts:
        out.append("Domains in use: " + ", ".join(f"{d} ({n})" for d, n in
                                                  sorted(counts.items(), key=lambda x: -x[1])))
    return "\n\n".join(out)


# ----------------------------------------------------------------------------- CLI

USAGE = """usage: server.py <command>   (no args: run MCP server)
  search <text>                      get <id>
  open                               reindex
  report <title> [--agent A] [--project P] [--domain a,b]   (details on stdin)
curator:
  review                             render
  file <inbox-id> <entry-id>...      dismiss <inbox-id> <reason>
  merge <keep-id> <drop-id>          retag <id> <domain,domain>
  set <id> <field> <yaml value>      (e.g. set <id> last_verified 2026-09-26)"""


def _csv(x: str | None) -> list[str]:
    return [d.strip() for d in (x or "").split(",") if d.strip()]


def _cli(argv: list[str]) -> None:
    cmd, args = argv[0], argv[1:]
    rest = " ".join(args)
    if cmd == "search":
        print(search(rest))
    elif cmd == "get":
        print(get(rest))
    elif cmd == "open":
        rows = _open_issues()
        print("\n".join(f"- [{i}] {t}" for i, t in rows) or "No open issues.")
    elif cmd == "reindex":
        INDEX_DB.unlink(missing_ok=True)
        con = _db(); _sync(con); n = con.execute("SELECT count(*) FROM meta").fetchone()[0]
        con.close(); print(f"indexed {n} entries")
    elif cmd == "report":
        opts, words, it = {}, [], iter(args)
        for a in it:
            if a in ("--agent", "--project", "--domain"):
                opts[a[2:]] = next(it, "")
            else:
                words.append(a)
        details = "" if sys.stdin.isatty() else sys.stdin.read()
        print(report(" ".join(words), details, agent=opts.get("agent", "cli"),
                     project=opts.get("project", ""), domain=_csv(opts.get("domain"))))
    elif cmd == "review":
        print(_review())
    elif cmd == "render":
        print(_render_all())
    elif cmd == "file" and len(args) >= 2:
        print(_file_inbox(args[0], args[1:]))
    elif cmd == "dismiss" and len(args) >= 2:
        print(_dismiss_inbox(args[0], " ".join(args[1:])))
    elif cmd == "merge" and len(args) == 2:
        print(_merge(*args))
    elif cmd == "retag" and len(args) == 2:
        print(_retag(args[0], _csv(args[1])))
    elif cmd == "set" and len(args) >= 3:
        print(_set_field(args[0], args[1], " ".join(args[2:])))
    else:
        print(USAGE)


def _open_issues() -> list[tuple[str, str]]:
    con = _db()
    try:
        _sync(con)
        return con.execute("SELECT id, title FROM meta WHERE kind='open_issue' "
                           "ORDER BY id").fetchall()
    finally:
        con.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        _cli(sys.argv[1:])
    else:
        try:
            _render_missing()
        except Exception as err:  # never block startup on the human view; stdout is the MCP pipe
            print(f"callcentre: render at startup failed: {err}", file=sys.stderr)
        mcp.run()  # stdio transport
