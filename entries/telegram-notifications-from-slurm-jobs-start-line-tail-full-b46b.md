---
id: telegram-notifications-from-slurm-jobs-start-line-tail-full-b46b
kind: convention
title: Telegram notifications from SLURM jobs (start line, tail + full stdout on exit)
domain:
- infra
- slurm
stack: {}
symptoms:
- How to get notified when a SLURM job starts / ends / fails
root_cause: ''
fix: Send a START line; on exit (trap) send the last 30 lines and the whole stdout as a document. Make
  every curl `|| true` and a no-op when the token is unset; re-return the captured $? so the trap doesn't
  mask the exit code; cut lines to 180 chars before tailing (progress bars); get the stdout path from
  `scontrol show job`. Keep secrets in ~/.config/<project>/secrets.env, chmod 600.
failed_attempts: []
verify: ''
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Telegram notifications from SLURM jobs (start line, tail + full stdout on exit)

> [!note] convention · unverified · used 0×, failed 0×
> #infra #slurm #kind/convention #status/unverified

## Symptoms
```text
How to get notified when a SLURM job starts / ends / fails
```

## Convention
Send a START line; on exit (trap) send the last 30 lines and the whole stdout as a document. Make every curl `|| true` and a no-op when the token is unset; re-return the captured \$? so the trap doesn't mask the exit code; cut lines to 180 chars before tailing (progress bars); get the stdout path from `scontrol show job`. Keep secrets in ~/.config/\<project>/secrets.env, chmod 600.

<small>created 2026-10-06 · id `telegram-notifications-from-slurm-jobs-start-line-tail-full-b46b`</small>

## Notes

<!-- callcentre:end -->
From VLM-RL-aicontent-detection docs/arc_runbook.md + git history (agent vrr-arc-repo-mining); not reproduced in-session.
