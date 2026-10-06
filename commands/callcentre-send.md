---
description: Send what this session learned to the shared call centre knowledge base
---
Go back over this whole session and send anything another agent on this machine could reuse
to the call centre (`mcp__callcentre__*` tools). Do this now, before anything else.

1. **Entries you used.** Every call-centre entry you relied on this session gets a
   `report_outcome` (worked or not), with a short note if something differed.
2. **Problems you solved** where the fix was non-obvious:
   - `search` first with the key error lines. If an entry already covers it, `report_outcome`
     on that entry instead of submitting a new one.
   - Otherwise `submit`: `kind="fix"` (or `"convention"` for a setup / way of doing things that
     worked). `symptoms` = the exact error lines or observed behaviour, verbatim (job ids and
     hostnames are fine; they're stripped at match time). `fix` = the MINIMAL change, not the
     story. Also fill `root_cause`, `failed_attempts` (things that looked right but didn't work),
     `verify` (a command that confirms it), `stack` (relevant versions, GPU type, node count) and
     `domain` (reuse the tags listed in the call centre's server instructions: e.g. `rl-training`,
     `eval`, `infra`, `slurm`, `isaac-sim`; `env` = RL/sim environments, `python-env` =
     conda/pip/package versions).
     `verified_now=True` only if you saw it work in this session.
3. **Problems still unsolved.** `search` with `kind="open_issue"`; if one exists, `log_attempt`
   for each thing you tried, otherwise `open_issue` with symptoms, repro and every attempt + result.
4. **Anything else worth keeping** that doesn't fit cleanly: observations, gotchas, suspected but
   unconfirmed causes, useful commands. Send it with `report` (raw details are fine; set `agent`
   to a stable label for yourself and `project` to this repo). A curator files it later.

Skip trivia (typos, one-off path mistakes, things specific to this conversation only).
Finish with one line per item sent: tool, id, title.

$ARGUMENTS
