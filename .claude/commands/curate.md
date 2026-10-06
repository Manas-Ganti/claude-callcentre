---
description: Organise the call centre: file the inbox, merge duplicates, tidy tags
---
You are the curator of the shared knowledge base in this repo. `entries/` and `inbox/` are live
data that other Claude Code sessions are reading and writing right now. Change them only through
the `mcp__callcentre__*` tools and the curator CLI below (they take the write lock and write
atomically). Never edit or delete those files by hand, and never touch code in this pass.

Curator CLI (run from this repo): `uv run server.py <cmd>`
`review` · `render` · `file <inbox-id> <entry-id>...` · `dismiss <inbox-id> <reason>` ·
`merge <keep-id> <drop-id>` · `retag <id> <a,b>` · `set <id> <field> <yaml value>`

1. Run `uv run server.py review` and read all of it.
2. **Inbox**, one item at a time: `cat inbox/<id>.md`, then decide:
   - A solved problem or a working convention: `search` with its key lines first.
     - Already covered: `report_outcome` on the existing entry if the report confirms it worked
       or failed. If the report adds symptoms, failed attempts or a better fix, `submit` it with
       `force=True`, then `merge <existing> <new>`.
     - New: `submit` it. Keep the agent's error lines verbatim as `symptoms`, cut the fix to the
       minimum, move dead ends into `failed_attempts`, use existing domain tags (the review lists
       them). `verified_now=True` only if the report says the fix was confirmed working.
   - Still unsolved: `log_attempt` on the matching open issue, or `open_issue`.
   - One report can become several entries.
   Then `file <inbox-id> <entry-id>...`. If nothing in it is reusable (or it's already fully
   covered), `dismiss <inbox-id> <reason>` instead.
3. **Possible duplicates**: `get` both. If they're the same problem, `merge` the weaker one into
   the clearer / more-used one (old ids keep resolving). If they're genuinely different, leave
   them and say so in your summary.
4. **Tags**: `retag` untagged entries, and entries whose tags drift from the vocabulary in
   README.md "Domain tags" (`env` = RL/sim environments, `python-env` = conda/pip/package versions).
   Use `set` for other one-field corrections (e.g. a wrong `last_verified` date).
5. **Stale**: if a newer entry supersedes it, `merge <newer> <stale>`; otherwise leave it (stale
   entries are already hidden from search).
6. **Unparseable files, open issues with expired claims or many attempts, and anything you're unsure
   about**: don't fix them; list them for the human.
7. If `review` or the files show entries without the `callcentre:begin` view (older layout),
   run `uv run server.py render`. `INDEX.md` refreshes itself; check it reads well.
8. Commit the data on its own, separate from code:
   `git add entries inbox INDEX.md && git commit -m "kb: curate <date>: <counts>"`

Finish with a short summary: filed / dismissed / submitted / merged / retagged counts, then
anything that needs a human.

$ARGUMENTS
