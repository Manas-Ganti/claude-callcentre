---
id: slurm-wall-clock-kill-skips-python-finally-and-end-of-script-148f
kind: fix
title: 'SLURM wall-clock kill skips Python `finally` and end-of-script requeue: trap SIGTERM via --signal=B:TERM@300'
domain:
- infra
- rl-training
- vt-arc
- slurm
stack:
  scheduler: SLURM (VT ARC, tc_h200_normal_short 24h cap)
  python: '3.11'
symptoms:
- trainer_state.json said step 9 after a 12h job that actually completed ~89 more steps (steps.jsonl showed
  99)
- Job hit the 12h wall and never resumed, even though a self-requeue line existed at the end of the sbatch
  script
- A resume would have silently redone 89 steps
root_cause: 'Python''s default SIGTERM action exits without unwinding, so `finally: save_state()` never
  runs. State was also only saved every save_every=100 steps. The bash requeue sat at the end of the script,
  which a wall kill never reaches.'
fix: '#SBATCH --signal=B:TERM@300 (SIGTERM 5 min before the kill). In bash: trap a TERM handler that forwards
  the signal to the python child, waits, and resubmits if steps remain (run python in the background +
  wait so the trap fires). In Python: signal.signal(SIGTERM, handler) that writes state and sys.exit(143).
  Write the small state file (step, RNG, curriculum, monitors) EVERY step via temp file + rename. Keep
  expensive adapter snapshots on save_every. Flush per-step metrics jsonl every step.'
failed_attempts:
- 'Saving state in a `finally` block: not executed on SIGTERM'
- 'Self-requeue at the end of the sbatch script: unreachable after a wall kill'
- 'Reading progress from trainer_state.json: it was stale, which led to a 30x wrong step-time estimate'
verify: Submit with --time short enough to hit the wall. The log should show the TERM handler firing,
  trainer_state.json step should equal the last steps.jsonl step, and a new job id should be queued.
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# SLURM wall-clock kill skips Python `finally` and end-of-script requeue: trap SIGTERM via --signal=B:TERM@300

> [!note] fix · unverified · used 0×, failed 0×
> #infra #rl-training #vt-arc #slurm #kind/fix #status/unverified

## Symptoms
```text
trainer_state.json said step 9 after a 12h job that actually completed ~89 more steps (steps.jsonl showed 99)
Job hit the 12h wall and never resumed, even though a self-requeue line existed at the end of the sbatch script
A resume would have silently redone 89 steps
```

## Root cause
Python's default SIGTERM action exits without unwinding, so `finally: save_state()` never runs. State was also only saved every save_every=100 steps. The bash requeue sat at the end of the script, which a wall kill never reaches.

## Fix
\#SBATCH --signal=B:TERM@300 (SIGTERM 5 min before the kill). In bash: trap a TERM handler that forwards the signal to the python child, waits, and resubmits if steps remain (run python in the background + wait so the trap fires). In Python: signal.signal(SIGTERM, handler) that writes state and sys.exit(143). Write the small state file (step, RNG, curriculum, monitors) EVERY step via temp file + rename. Keep expensive adapter snapshots on save_every. Flush per-step metrics jsonl every step.

## Failed attempts
- Saving state in a `finally` block: not executed on SIGTERM
- Self-requeue at the end of the sbatch script: unreachable after a wall kill
- Reading progress from trainer_state.json: it was stale, which led to a 30x wrong step-time estimate

## Verify
Submit with --time short enough to hit the wall. The log should show the TERM handler firing, trainer_state.json step should equal the last steps.jsonl step, and a new job id should be queued.

## Stack
| | |
|---|---|
| scheduler | SLURM (VT ARC, tc_h200_normal_short 24h cap) |
| python | 3.11 |

<small>created 2026-10-06 · id `slurm-wall-clock-kill-skips-python-finally-and-end-of-script-148f`</small>

## Notes

<!-- callcentre:end -->
Sourced from healthcare_RL git history (9e6dc49, ab7da55), not reproduced this session. Related SLURM gotchas from the same repo (3fd6e8e): put `set -euo pipefail` in each job script itself, not in a sourced env.sh. If the source fails, the script loses error handling and prints success. Find the repo root by walking up from $SLURM_SUBMIT_DIR, because $0/BASH_SOURCE point at the spool copy. In sourced scripts use `return`, not `exit`.
