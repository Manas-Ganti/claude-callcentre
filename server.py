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
   does not repeat your dead ends."""

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
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60].rstrip("-") or "entry"


def _new_id(title: str) -> str:
    """Random suffix, retried until unused. Caller must hold _write_lock."""
    while True:
        eid = f"{_slug(title)}-{secrets.token_hex(2)}"
        if not _path(eid).exists():
            return eid


def _path(entry_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9-]+", entry_id):
        raise ValueError(f"invalid id: {entry_id!r}")
    return ENTRIES / f"{entry_id}.md"


def _read(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2).strip()


def _write(entry: dict, notes: str = "") -> Path:
    """Atomic write. Caller must hold _write_lock."""
    path = _path(entry["id"])
    front = yaml.safe_dump(entry, sort_keys=False, allow_unicode=True, width=100)
    body = f"---\n{front}---\n{notes.strip()}\n" if notes.strip() else f"---\n{front}---\n"
    tmp = path.with_suffix(".md.tmp")
    tmp.write_text(body, encoding="utf-8")
    os.replace(tmp, path)
    return path


def _load(entry_id: str) -> tuple[dict, str]:
    path = _path(entry_id)
    if not path.exists():
        # allow unique prefix match
        hits = sorted(ENTRIES.glob(f"{entry_id}*.md"))
        if len(hits) != 1:
            raise FileNotFoundError(f"no unique entry for id {entry_id!r}")
        path = hits[0]
    return _read(path)


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
        sql += " AND m.status != 'stale'"
    sql += " ORDER BY score LIMIT ?"
    args.append(limit)
    con = _db()
    try:
        _sync(con)
        rows = con.execute(sql, args).fetchall()
    finally:
        con.close()
    cols = ["id", "kind", "status", "title", "summary", "uses", "failures", "last_verified", "_s"]
    return [{k: v for k, v in zip(cols, r) if k != "_s"} for r in rows]


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
    Optional filters: domain (e.g. 'rl-training', 'eval', 'infra', 'env'),
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
    e.g. {"trl": "0.x", "vllm": "0.x"}. Set verified_now=True only if you confirmed it worked in this
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
    attempts (with the result of each) so nobody repeats your dead ends."""
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


# ----------------------------------------------------------------------------- CLI

def _cli(argv: list[str]) -> None:
    cmd, rest = argv[0], " ".join(argv[1:])
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
    else:
        print("usage: server.py [search <text> | get <id> | open | reindex]  (no args: run MCP server)")


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
        mcp.run()  # stdio transport
