---
id: slurm-job-output-persist-results-to-files-wandb-not-stdout-a-26a9
kind: convention
title: 'SLURM job output: persist results to files / wandb, not stdout; avoid rich-table logs'
domain:
- infra
- slurm
- rl-training
stack: {}
symptoms:
- Probe / gate numbers only exist in logs/slurm/*.out and must be recovered by hand
- GRPO .out files of 58-277 MB from rich-table trajectory logging
root_cause: ''
fix: Write results to a file (e.g. results/<dataset>/*.json) and/or wandb.init. Log trajectories to JSONL
  instead of printing rich tables to stdout.
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
# SLURM job output: persist results to files / wandb, not stdout; avoid rich-table logs

> [!note] convention · unverified · used 0×, failed 0×
> #infra #slurm #rl-training #kind/convention #status/unverified

## Symptoms
```text
Probe / gate numbers only exist in logs/slurm/*.out and must be recovered by hand
GRPO .out files of 58-277 MB from rich-table trajectory logging
```

## Convention
Write results to a file (e.g. results/\<dataset>/*.json) and/or wandb.init. Log trajectories to JSONL instead of printing rich tables to stdout.

<small>created 2026-10-06 · id `slurm-job-output-persist-results-to-files-wandb-not-stdout-a-26a9`</small>

## Notes

<!-- callcentre:end -->
From VLM-RL-aicontent-detection docs/arc_runbook.md + git history (agent vrr-arc-repo-mining); not reproduced in-session.
