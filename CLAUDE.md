# callcentre: build and test spec

This repo is the shared knowledge base ("call centre") that every Claude Code session on this Mac
reaches over MCP. `server.py` and `README.md` already exist and are the source of truth for
behaviour. Your job is to turn them into a tested repo: scaffold the layout, write the test suite
below, make it pass, then wire the server into Claude Code.

Do not change what the server does to make a test pass. If a test reveals a real bug, fix the bug
in `server.py`, say what you changed, and keep the test. If a spec item below turns out to be
wrong about current behaviour, stop and report it rather than editing the test to match.

## Hard rules

- **Never touch the real knowledge base during tests.** `server.py` reads `CALLCENTRE_HOME` once at
  import and builds `HOME`, `ENTRIES`, `INDEX_DB`, `LOCK_FILE` as module globals. Every test must
  run against a `tmp_path` home. Setting the env var after import does nothing; the fixture must
  patch the module globals (see conftest below). Subprocess tests must pass `CALLCENTRE_HOME` in
  their environment.
- Before running anything, check that `~/claude-callcentre/entries/` is empty or doesn't exist yet. If it
  already contains entries, do not delete, move or rewrite them.
- Keep `server.py` a single file runnable with `uv run server.py`. Its inline `# /// script` header
  is how the MCP registration gets its dependencies; don't remove it.
- Python 3.10+, macOS (uses `fcntl`). No new runtime dependencies.

## Step 1: scaffold

Target layout:

```
~/claude-callcentre/
├── CLAUDE.md
├── README.md
├── server.py
├── pyproject.toml
├── .gitignore
├── INDEX.md                        # generated (data), Obsidian home note
├── domains/                        # generated (data), one hub note per domain
├── entries/.gitkeep
├── inbox/.gitkeep
├── commands/callcentre-send.md     # user-scope /callcentre-send (installed to ~/.claude/commands/)
├── .claude/commands/curate.md      # project-scope /curate
└── tests/
    ├── conftest.py
    ├── test_storage.py
    ├── test_search.py
    ├── test_lifecycle.py
    ├── test_issues.py
    ├── test_concurrency.py
    ├── test_cli.py
    ├── test_curation.py
    ├── test_obsidian.py
    └── test_mcp_stdio.py
```

- `.gitignore`: `.index.db*`, `.lock`, `*.tmp`, `.venv/`, `__pycache__/`, `.pytest_cache/`
- `pyproject.toml`: project `callcentre`, `requires-python = ">=3.10"`, dependencies
  `mcp>=1.2,<3` and `pyyaml>=6`, a `dev` dependency group with `pytest>=8`, and
  `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and `pythonpath = ["."]`.
  It exists only so `uv run pytest` works; it is not a packaging target.
- `git init` if this isn't already a repo.

One known defect to fix while scaffolding: in `server.py` the comment for `DUP_THRESHOLD`
("token Jaccard on title+symptoms above which submit refuses") got appended to the
`STRONG_OVERLAP` line. Move it back next to `DUP_THRESHOLD`. Comment-only change.

## Step 2: test suite

Use plain pytest. No pytest-asyncio: the one async test wraps its body in `asyncio.run`.

### tests/conftest.py

- `cc` fixture: `monkeypatch.setenv("CALLCENTRE_HOME", str(tmp_path))`, import `server`, then
  `monkeypatch.setattr` on `server.HOME`, `server.ENTRIES`, `server.INDEX_DB`, `server.LOCK_FILE`
  to the matching `tmp_path` paths. Return the module.
- Helpers used across files:
  - `nccl_fix(cc)`: submits the reference NCCL entry below with `verified_now=True`, returns its id.
  - `eval_fix(cc)`: submits the reference eval entry below with `verified_now=True`, returns its id.
  - `ids(result_text)`: extracts the `[id]` values from a `search` result.

Reference entries (taken from cases already verified by hand against this server):

```python
NCCL = dict(kind="fix",
    title="GRPO multi-node NCCL watchdog timeout during vLLM generation",
    symptoms=[
        "[rank3]: Watchdog caught collective operation timeout: WorkNCCL(SeqNum=883, OpType=ALLREDUCE) ran for 1800043 milliseconds",
        "job 48812345 on tc-gpu017, 2 nodes x 4 H200, hangs at first rollout",
        "slurmstepd: error: *** JOB 48812345 ON tc-gpu017 CANCELLED AT 2026-09-20T10:32:01 ***"],
    fix="Launch vLLM engine before DDP init; raise c10d store timeout",
    domain=["rl-training", "infra"])

EVAL = dict(kind="fix",
    title="Eval accuracy drops while GRPO reward rises",
    symptoms=["reward rises steadily but gsm8k accuracy falls after a few hundred steps"],
    fix="Use the training chat template in the eval harness",
    root_cause="chat template mismatch between training and lm-eval",
    domain=["rl-training", "eval"])
```

### tests/test_storage.py: files are the source of truth

1. `submit` writes exactly one `entries/<id>.md` with YAML frontmatter that round-trips through
   `_read` to the same fields.
2. Ids are lowercase slug plus 4 hex chars; title text with spaces and punctuation slugifies.
3. `get` rejects unsafe ids: `get("../../etc/passwd")` returns a string starting `invalid id`,
   and no file outside `ENTRIES` is read.
4. `get` accepts a unique id prefix (`get("grpo-multi")` returns the NCCL entry). An ambiguous
   prefix returns the `no unique entry` message.
5. `get` output omits empty fields and the internal `consecutive_failures` / `claim_expires` keys.
6. Generic SLURM wrapper lines are dropped from stored symptoms: after `nccl_fix`, the stored
   symptoms do not contain `CANCELLED AT`. The other two lines are stored verbatim, job id and
   hostname included (normalisation happens at match time, not write time).
7. A symptoms list made only of generic lines is kept as-is rather than emptied.
8. Writes are atomic: no `*.md.tmp` files remain after any write operation.
9. Index sync follows the files:
   - hand-editing an entry's `fix` on disk changes what `search` returns, without `reindex`
     (bump the mtime explicitly with `os.utime` in case the edit lands in the same tick);
   - deleting an entry file removes it from search results;
   - a malformed file (`---\nkey: [unclosed\n---\n`) in `entries/` is skipped and search over the
     other entries still works.
10. Deleting `.index.db` loses nothing: the next `search` rebuilds it and finds the same entries.

### tests/test_search.py: matching quality

Seed with `nccl_fix` and `eval_fix`, then assert:

| query | expected |
|---|---|
| `job 49900001 on tc-dgx003 (4 nodes) hung. rank0: Watchdog caught collective operation timeout, OpType=ALLREDUCE, ran for 1800012 milliseconds` | NCCL entry returned, not labelled WEAK |
| `torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 2.00 GiB` + newline + `slurmstepd: error: *** JOB 499 ON tc-gpu002 CANCELLED AT 2026-10-04T11:00:01 ***` | no match |
| `slurmstepd: error: *** JOB 1234567 ON tc-gpu002 CANCELLED AT 2026-10-04T11:00:01 DUE TO TIME LIMIT ***` | no match |
| `GRPO reward keeps going up but gsm8k accuracy is dropping` | eval entry returned |
| `training job failed with an error` | every hit (if any) labelled `WEAK` |
| whitespace only | `Query has no searchable terms.` |

Plus:

- `_normalize` unit cases: removes job ids, `tc-gpu017`-style hostnames, `[rank3]:` prefixes,
  timestamps, hex addresses, bare numbers; turns `/long/path/to/grpo_trainer.py` into
  `grpo_trainer.py`; **keeps** `H200`, `A100`, `bf16`, `fp16`, `gsm8k`.
- `domain` filter: `search(<eval query>, domain="infra")` does not return the eval entry.
- `kind` filter: with an open issue present, `kind="open_issue"` returns only open issues.
- Stale entries are hidden by default and shown with `include_stale=True`.
- `limit` is respected and clamped to 1..10.
- Result size stays compact: a 5-hit `search` result is under 2,000 characters.

### tests/test_lifecycle.py: trust signals

1. `submit` with `verified_now=False` → status `unverified`, `uses` 0, no `last_verified`.
2. `report_outcome(worked=True)` → `verified`, `uses` +1, `last_verified` today,
   `consecutive_failures` reset to 0.
3. One failure keeps the status. Two consecutive failures → `stale`. A success after that →
   `verified` again.
4. Failures separated by a success never go stale (the counter is consecutive, not total).
5. `outcome_notes` keeps only the last 10 notes.
6. Duplicate guard: resubmitting the NCCL entry is refused with the existing id in the message
   and no new file. The same call with `force=True` succeeds.
7. A genuinely different entry (OOM fix) is not flagged as a duplicate of the NCCL entry.
8. Input validation: `kind="open_issue"` via `submit` is refused; empty `fix` or empty
   `symptoms` is refused; nothing is written in either case.
9. `report_outcome` on an open issue is refused with a pointer to `log_attempt` / `resolve_issue`.

### tests/test_issues.py: open-issue queue

1. `open_issue` creates `kind: open_issue`, `status: open`, and shows up in `search` as
   `OPEN (unclaimed, N attempts logged)`.
2. Agent A claims it; agent B's claim is refused with A's name in the message; A re-claiming
   extends the lease.
3. Lease expiry: monkeypatch `server._now` forward past the lease and B's claim succeeds. Do not
   use `sleep`.
4. `log_attempt` appends `[date agent] attempt → result` lines; the search summary's attempt
   count updates.
5. `resolve_issue` turns it into `kind: fix`, `status: verified`, `uses: 1`, keeps the same id,
   moves logged attempts into `failed_attempts`, and the same symptom query now returns it as
   a fix.
6. `claim_issue`, `log_attempt`, `resolve_issue` on a non-issue entry are refused and leave the
   file unchanged.
7. Duplicate guard applies to `open_issue` too (and `force=True` overrides it).

### tests/test_concurrency.py: many sessions, one store

Every Claude Code session runs its own server process, so concurrency is across processes, not
threads. Use `subprocess` or `multiprocessing` with the `spawn` context, each child with
`CALLCENTRE_HOME` set to the test's tmp home.

1. 20 processes each call `report_outcome(id, True)` on the same entry at once → final `uses`
   equals starting `uses` + 20 exactly. No lost updates.
2. 8 processes each `submit` a distinct convention at once → 8 new files, all parse, no `.tmp`
   leftovers.
3. Searches running while writes happen never raise (SQLite `database is locked` must not
   surface to the caller).

Mark these `@pytest.mark.slow` (register the marker in `pyproject.toml`) but run them by default.

### tests/test_cli.py: the bash path

Run `python server.py ...` as a subprocess with `CALLCENTRE_HOME` set:

- `search <text>` prints hits; `get <id>` prints the entry; `open` lists open issues or prints
  `No open issues.`; `reindex` prints `indexed N entries` with the right N; an unknown command
  prints the usage line. Exit code 0 in all cases.

### tests/test_mcp_stdio.py: the real integration path

Spawn `server.py` with `mcp.client.stdio.stdio_client` (`StdioServerParameters`, command
`sys.executable`, env including `CALLCENTRE_HOME` and `PATH`) and in one `asyncio.run`:

1. `initialize` returns instructions that mention `search` and `report_outcome`.
2. `list_tools` returns exactly: `search`, `get`, `submit`, `report_outcome`, `open_issue`,
   `claim_issue`, `log_attempt`, `resolve_issue`, `report`.
3. Every tool has a non-empty description (Claude Code may defer tool schemas, but the
   descriptions are what it sees once loaded).
4. `call_tool("submit", ...)` then `call_tool("search", ...)` round-trips: the submitted entry
   comes back.
5. List-typed and dict-typed arguments (`symptoms`, `stack`) survive JSON transport.
6. `call_tool("report", ...)` lands one file in `inbox/`.
7. Instructions carry the shared domain vocabulary (`python-env` etc.), and a legacy-format entry
   seeded before startup has been rendered by the time `initialize` returns.

This test must pass on whichever `mcp` major version `uv` resolves (1.x uses `FastMCP`, 2.x
uses `MCPServer`; the import shim in `server.py` handles both).

### tests/test_curation.py: inbox and curator

`report` writes to `inbox/` (never to `entries/`, never searchable) and needs title + details.
Curator operations are CLI-only (not MCP tools) and take the write lock:

- `file <inbox-id> <entry-id>...` moves the item to `inbox/done/` with `filed_as` (full ids,
  prefixes resolved); an unknown entry id refuses and leaves the item in place.
- `dismiss <inbox-id> <reason>` requires a reason and records it.
- `retag <id> a,b` replaces `domain`.
- `set <id> <field> <yaml>` changes one frontmatter field (dates stay strings, `null` clears);
  refuses `id` / `kind`, invalid field names, invalid YAML and statuses not valid for the kind,
  leaving the file untouched.
- `merge <keep> <drop>`: union of domain / symptoms / failed_attempts (an open issue's
  `attempts` included), stack merged with keep winning, empty root_cause / verify / repro
  filled from drop, uses and failures summed, verified if either was, drop's differing fix and
  notes appended to keep's notes, `merged_from` records drop, drop's file is deleted. The old
  id still resolves in `get` / `report_outcome`. Refuses self-merge and an open issue as keep.
- `review` lists Inbox, Possible duplicates (Jaccard >= `REVIEW_DUP_THRESHOLD`), Unparseable
  files, Untagged, Stale, Unverified, Open issues, then domain counts; `Nothing to review.`
  when empty.

### tests/test_obsidian.py: the human view

Entry files are frontmatter (source of truth) + a body generated from it between
`callcentre:begin` / `callcentre:end` markers + free-form notes. `_read` drops the generated part,
so `get`, search and duplicate checks see exactly the frontmatter and notes; rewriting an entry
never duplicates the view or loses notes. Prose is escaped for Obsidian (`$`, `<`, `#word`) but
code spans and the fenced symptoms block are verbatim. `INDEX.md` lists open issues, entries
by domain (most-used domain first, untagged last) and the inbox as `[[id|title]]` links; it is
refreshed after every locked operation and not rewritten when unchanged. Section headings link
`domains/<tag>.md` hub notes (tagged with their domain, open issues first, removed when the domain
disappears). If `.obsidian/graph.json` exists, colour groups are merged in: open issues first, then
domains with 2+ notes rarest-first; a user-chosen colour or user-added group is never overwritten
or dropped, the filter is set only when empty, and nothing is written when unchanged. Without
`.obsidian/` nothing is created. `render` upgrades
legacy files without touching their fields or notes, and skips unparseable ones. At MCP server
start, `_render_missing` re-renders only entries whose view is missing or outdated.

## Step 3: run

```bash
uv run --group dev pytest -q
```

All tests must pass. Report the count, the wall time of the slow tests, and any bug you fixed in
`server.py` along the way. Then do a final manual check against a scratch home:

```bash
CALLCENTRE_HOME=$(mktemp -d) uv run server.py search "test"
# expected: No matches. If you solve this, call `submit`; ...
```

Commit with a message describing the scaffold and test suite.

## Step 4: wire into Claude Code

Only after tests pass:

1. `claude mcp add --scope user callcentre -- uv run ~/claude-callcentre/server.py`
   (skip if `claude mcp list` already shows it).
2. In `~/.claude/settings.json`, add `"mcp__callcentre"` to `permissions.allow`, merging with
   any existing entries. Show me the diff before writing.
3. Append the "Call centre (shared knowledge base)" block from `README.md` to
   `~/.claude/CLAUDE.md` if it isn't there already. Show me the diff before writing.
4. Tell me to open a new session and run `/mcp` to confirm `callcentre` shows 9 tools.

## Working on this repo later

- Run the full suite before every commit that touches `server.py`.
- A change to matching (`_NOISE`, `_GENERIC`, `MIN_OVERLAP`, `STRONG_OVERLAP`, `DUP_THRESHOLD`)
  needs a new row in the `test_search.py` table showing the case that motivated it.
- `entries/`, `inbox/`, `domains/` and `INDEX.md` are data, not code. Commits to them are knowledge-base updates and
  should be separate from code commits. Curate them with `/curate`, not by hand-editing.