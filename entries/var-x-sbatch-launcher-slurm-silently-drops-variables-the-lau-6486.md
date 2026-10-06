---
id: var-x-sbatch-launcher-slurm-silently-drops-variables-the-lau-6486
kind: convention
title: '`VAR=x sbatch launcher.slurm` silently drops variables the launcher doesn''t read; .slurm is snapshotted
  at submit time'
domain:
- infra
- slurm
- vt-arc
stack: {}
symptoms:
- MAX_INSPECTS=6, GRAD_ACCUM, MAX_NEW_TOKENS passed on the sbatch line were accepted with no warning and
  ignored; job ran on Python defaults
- Editing a .slurm file had no effect on an already-queued job
- 'An #SBATCH directive edited on the laptop ''did nothing'' because the job ran from the cluster checkout'
root_cause: Shell env vars are only meaningful if the script references them; nothing validates unknown
  names.
fix: '(1) Before relying on an env var, grep -n ''VARNAME'' scripts/<launcher>.slurm; prefer passthrough
  args after the script name (sbatch ... launcher.slurm --max-inspects 6) which reach argparse and fail
  loudly on typos. (2) sbatch copies the .slurm to the spool at SUBMIT time — cancel and resubmit after
  editing it; Python files and sourced env scripts are read at RUN time, so a git pull under a pending
  job does take effect. (3) With separate laptop/cluster checkouts: commit, push, and `git pull --ff-only`
  on the cluster before submitting; confirm which commit actually ran.'
failed_attempts: []
verify: grep -n '<VAR>' scripts/*.slurm ; job log should echo every effective knob at start
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# `VAR=x sbatch launcher.slurm` silently drops variables the launcher doesn't read; .slurm is snapshotted at submit time

> [!note] convention · unverified · used 0×, failed 0×
> #infra #slurm #vt-arc #kind/convention #status/unverified

## Symptoms
```text
MAX_INSPECTS=6, GRAD_ACCUM, MAX_NEW_TOKENS passed on the sbatch line were accepted with no warning and ignored; job ran on Python defaults
Editing a .slurm file had no effect on an already-queued job
An #SBATCH directive edited on the laptop 'did nothing' because the job ran from the cluster checkout
```

## Root cause
Shell env vars are only meaningful if the script references them; nothing validates unknown names.

## Convention
(1) Before relying on an env var, grep -n 'VARNAME' scripts/\<launcher>.slurm; prefer passthrough args after the script name (sbatch ... launcher.slurm --max-inspects 6) which reach argparse and fail loudly on typos. (2) sbatch copies the .slurm to the spool at SUBMIT time — cancel and resubmit after editing it; Python files and sourced env scripts are read at RUN time, so a git pull under a pending job does take effect. (3) With separate laptop/cluster checkouts: commit, push, and `git pull --ff-only` on the cluster before submitting; confirm which commit actually ran.

## Verify
grep -n '\<VAR>' scripts/*.slurm ; job log should echo every effective knob at start

<small>created 2026-10-06 · id `var-x-sbatch-launcher-slurm-silently-drops-variables-the-lau-6486`</small>

## Notes

<!-- callcentre:end -->
Cost here: a GRPO run trained at an inspect budget the gate never measured, and an eval branch that still ignores MAX_INSPECTS so no policy was evaluated at its training budget. Source commits dfaa49d, 7433ef3, 91ca4b1.
