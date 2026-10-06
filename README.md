# callcentre

A shared knowledge base for every agent on this machine: problems already solved, conventions,
and open issues nobody has cracked yet. Exposed as an MCP server, backed by plain markdown files.

## Layout

```
~/claude-callcentre/          # $CALLCENTRE_HOME (make this a git repo)
├── server.py                 # MCP server + small CLI
├── entries/*.md              # source of truth, one entry per file, YAML frontmatter
├── inbox/*.md                # raw agent reports awaiting the curator (inbox/done/ once handled)
├── INDEX.md                  # generated home note: every entry, by domain, as [[wikilinks]]
├── domains/*.md              # generated hub note per domain (graph clusters form around these)
├── .index.db                 # derived SQLite FTS5 index (gitignore it; rebuilt automatically)
└── .lock                     # write lock (gitignore it)
```

## Setup

```bash
mkdir -p ~/claude-callcentre && cp server.py ~/claude-callcentre/
cd ~/claude-callcentre && git init && printf '.index.db*\n.lock\n*.tmp\n' > .gitignore

# Register for every Claude Code project on this Mac (user scope).
# uv reads the inline dependency header in server.py, so no venv to manage.
claude mcp add --scope user callcentre -- uv run ~/claude-callcentre/server.py
```

Then add this to `~/.claude/CLAUDE.md` so agents actually use it:

```markdown
## Call centre (shared knowledge base)
- Before debugging any non-trivial error or choosing an RL/eval/infra setup, call
  `mcp__callcentre__search` with the error text or a symptom description.
- After using an entry, call `report_outcome`.
- Solved something new and non-obvious? `submit` the minimal fix plus what did NOT work.
- Giving up or handing off? `open_issue` / `log_attempt` with everything you tried.
- Learned something useful but no time for a clean entry? `report` the raw details.
```

## Tools

| tool | purpose |
|---|---|
| `search(query, domain?, kind?)` | compact top-5 hits (~50 tokens each); weak matches labelled, irrelevant ones dropped |
| `get(id)` | full entry; unique id prefixes work |
| `submit(kind, title, symptoms, fix, ...)` | new `fix` or `convention`; refuses near-duplicates unless `force=True` |
| `report_outcome(id, worked, note?)` | success → `verified`; 2 consecutive failures → `stale` (hidden from search by default) |
| `open_issue` / `claim_issue` / `log_attempt` / `resolve_issue` | unsolved-problem queue with claim leases |
| `report(title, details, agent?, project?, domain?)` | raw findings into `inbox/` for the curator; not searchable until filed |

## Domain tags

Reuse these (they're in the server instructions every agent receives); add a new short tag only
if none fits: `rl-training`, `sft`, `eval`, `infra`, `slurm`, `vt-arc`, `distributed`,
`deepspeed`, `structured-output`, `isaac-sim`, `env` (RL / simulation environments),
`python-env` (conda, pip, package versions and installs), `dataviz`, `observable`.

## Feeding it and organising it

Two ways in, one curator pass:

- **Structured**: agents that solved something cleanly call `submit` / `open_issue` themselves.
  These are searchable immediately.
- **Raw**: anything else goes to `report`, which drops it into `inbox/`.

To make an agent send what it learned, run `/callcentre-send` at the end of its session (source:
`commands/callcentre-send.md`, installed to `~/.claude/commands/`). Bash-only agents use
`server.py report` (below).

To organise, open a Claude Code session in this repo and run `/curate`
(`.claude/commands/curate.md`). It reads `server.py review`, turns inbox items into entries,
merges duplicates, retags, and commits `entries/` + `inbox/` as a data-only commit. The curator
commands are CLI-only so ordinary agents never see them, and they take the same write lock as the
tools, so curating is safe while other sessions are live. `merge` keeps the old id resolving
(`merged_from`), so agents holding it can still `get` / `report_outcome`.

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

## Reading it in Obsidian

Open `~/claude-callcentre` as an Obsidian vault and start from `INDEX.md`.

- Each entry's YAML frontmatter shows as Properties and is the only source of truth. Below it the
  server writes a readable view (title, status callout, `#domain` / `#kind/…` / `#status/…` tags,
  Symptoms, Root cause, Fix, Failed attempts, Verify, Stack) between
  `<!-- callcentre:begin -->` / `<!-- callcentre:end -->`. That view is regenerated on every write:
  edit the Properties, not the view. Free-form notes go below the end marker and are kept.
- `INDEX.md` and `domains/*.md` are regenerated whenever anything changes (only rewritten if their
  content changed). Each domain hub links its entries, so the graph view clusters by domain.
- Graph view: once the vault has been opened (`.obsidian/graph.json` exists), the server keeps one
  colour group per domain with 2+ notes, plus red for open issues. A node takes the colour of its
  most specific (rarest) tag, because Obsidian colours by the first matching group. Recolour any
  group in Obsidian and the server keeps your colour; groups you add yourself are left alone. The
  graph filter defaults to `-path:inbox -path:commands -file:README -file:CLAUDE -file:INDEX`
  and is only set while empty, so your own filter wins. `.obsidian/` stays out of git.
- Prose is escaped so agent text renders literally (`$VAR` isn't math, `<env>` isn't HTML,
  `#word` isn't a tag); `code spans` are left verbatim.
- `server.py render` rewrites every entry in the current layout (fields and notes unchanged).
  Every MCP server also renders any entry with a missing or outdated view when it starts, so
  entries written by sessions still running an older server get fixed by the next session.

Agents never need the view: `get` returns the frontmatter plus notes, exactly as before.

## CLI (for bash-only agents or you)

```bash
uv run ~/claude-callcentre/server.py search "NCCL watchdog timeout"
uv run ~/claude-callcentre/server.py get <id>
uv run ~/claude-callcentre/server.py open        # list open issues
uv run ~/claude-callcentre/server.py reindex
echo "<raw details>" | uv run ~/claude-callcentre/server.py report "<title>" --agent X --project P --domain a,b

# curator
uv run ~/claude-callcentre/server.py review                       # what needs attention
uv run ~/claude-callcentre/server.py render                       # re-render all entry bodies
uv run ~/claude-callcentre/server.py file <inbox-id> <entry-id>... # inbox item became these entries
uv run ~/claude-callcentre/server.py dismiss <inbox-id> <reason>
uv run ~/claude-callcentre/server.py merge <keep-id> <drop-id>
uv run ~/claude-callcentre/server.py retag <id> rl-training,infra
uv run ~/claude-callcentre/server.py set <id> last_verified 2026-09-26   # fix one field (YAML value)
```

## Known limits (deliberate for v1)

- Matching thresholds (`MIN_OVERLAP`, `STRONG_OVERLAP` in server.py) are set from a handful of
  synthetic cases. Tune them once you have ~20 real entries.
- Keyword search only (BM25 with porter stemming). Fine for error strings, weaker for
  paraphrased symptoms. Embeddings are the obvious next step.
- Duplicate detection is token overlap on title + symptoms; entries that differ only by a
  version number may be flagged. Agents can pass `force=True`.
- No auto-commit; commit `entries/` yourself or from a cron/hook.
