# callcentre

A shared knowledge base for every agent on this machine: problems already solved, conventions,
and open issues nobody has cracked yet. Exposed as an MCP server, backed by plain markdown files.

## Layout

```
~/callcentre/                 # $CALLCENTRE_HOME (make this a git repo)
├── server.py                 # MCP server + small CLI
├── entries/*.md              # source of truth, one entry per file, YAML frontmatter
├── .index.db                 # derived SQLite FTS5 index (gitignore it; rebuilt automatically)
└── .lock                     # write lock (gitignore it)
```

## Setup

```bash
mkdir -p ~/callcentre && cp server.py ~/callcentre/
cd ~/callcentre && git init && printf '.index.db*\n.lock\n*.tmp\n' > .gitignore

# Register for every Claude Code project on this Mac (user scope).
# uv reads the inline dependency header in server.py, so no venv to manage.
claude mcp add --scope user callcentre -- uv run ~/callcentre/server.py
```

Then add this to `~/.claude/CLAUDE.md` so agents actually use it:

```markdown
## Call centre (shared knowledge base)
- Before debugging any non-trivial error or choosing an RL/eval/infra setup, call
  `mcp__callcentre__search` with the error text or a symptom description.
- After using an entry, call `report_outcome`.
- Solved something new and non-obvious? `submit` the minimal fix plus what did NOT work.
- Giving up or handing off? `open_issue` / `log_attempt` with everything you tried.
```

## Tools

| tool | purpose |
|---|---|
| `search(query, domain?, kind?)` | compact top-5 hits (~50 tokens each); weak matches labelled, irrelevant ones dropped |
| `get(id)` | full entry; unique id prefixes work |
| `submit(kind, title, symptoms, fix, ...)` | new `fix` or `convention`; refuses near-duplicates unless `force=True` |
| `report_outcome(id, worked, note?)` | success → `verified`; 2 consecutive failures → `stale` (hidden from search by default) |
| `open_issue` / `claim_issue` / `log_attempt` / `resolve_issue` | unsolved-problem queue with claim leases |

## Cluster failure workflow

You read the SLURM logs and hand agents the lines that matter. Agents pass that excerpt
straight to `search`, and reuse it as `symptoms` when they submit or open an issue, so entries
are stored in your own words.

At match time (never in the stored file), job ids, `tc-gpu017`-style hostnames, rank prefixes,
timestamps, paths and bare numbers are stripped, so the same failure excerpted on different
days from different jobs still matches. GPU types and dtypes (`H200`, `bf16`) are kept. Generic
SLURM wrapper lines (`CANCELLED AT`, `exit code`) are ignored for matching unless they're the
only line, so every failed job doesn't match every entry.

Including the stack in your excerpt (node count, GPU type, key package versions) lets agents
fill the `stack` field, which is what tells a stale fix from a current one.

## CLI (for bash-only agents or you)

```bash
uv run ~/callcentre/server.py search "NCCL watchdog timeout"
uv run ~/callcentre/server.py get <id>
uv run ~/callcentre/server.py open        # list open issues
uv run ~/callcentre/server.py reindex
```

## Known limits (deliberate for v1)

- Matching thresholds (`MIN_OVERLAP`, `STRONG_OVERLAP` in server.py) are set from a handful of
  synthetic cases. Tune them once you have ~20 real entries.
- Keyword search only (BM25 with porter stemming). Fine for error strings, weaker for
  paraphrased symptoms. Embeddings are the obvious next step.
- Duplicate detection is token overlap on title + symptoms; entries that differ only by a
  version number may be flagged. Agents can pass `force=True`.
- No auto-commit; commit `entries/` yourself or from a cron/hook.
