---
id: conda-env-silently-falls-through-to-base-inside-slurm-batch-65e5
kind: fix
title: Conda env silently falls through to base inside SLURM batch jobs on ARC (module load Miniforge3
  can't see personal ~/miniconda3)
domain:
- infra
- python-env
- vt-arc
- slurm
stack:
  cluster: VT ARC
  module: Miniforge3
  conda: personal ~/miniconda3
symptoms:
- EnvironmentNameNotFound for a CONDA_ENV=<name> that activates fine on the login node
- 'OR: `source activate` reports success in the non-interactive batch shell without switching interpreters;
  job runs in base and dies with ModuleNotFoundError: No module named ''PIL'''
root_cause: '`module reset; module load Miniforge3` swaps in the cluster''s conda, which cannot see envs
  under a personal ~/miniconda3 root. Activation can also no-op without error in batch shells, so a `||
  fallback` never fires.'
fix: 'Pass CONDA_ENV as an ABSOLUTE path, prepend "$CONDA_ENV/bin" to PATH, export PY="$CONDA_ENV/bin/python"
  and call "$PY" everywhere (never bare `python`). Then assert at job start: "$PY" -c ''import sys; print(sys.executable)''
  must be inside $CONDA_ENV, else exit with a readable message.'
failed_attempts:
- Relying on conda activate / source activate exit status in sbatch scripts
verify: 'Job log near the top shows: [arc_env] python=/home/<user>/miniconda3/envs/<env>/bin/python'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Conda env silently falls through to base inside SLURM batch jobs on ARC (module load Miniforge3 can't see personal ~/miniconda3)

> [!note] fix · unverified · used 0×, failed 0×
> #infra #python-env #vt-arc #slurm #kind/fix #status/unverified

## Symptoms
```text
EnvironmentNameNotFound for a CONDA_ENV=<name> that activates fine on the login node
OR: `source activate` reports success in the non-interactive batch shell without switching interpreters; job runs in base and dies with ModuleNotFoundError: No module named 'PIL'
```

## Root cause
`module reset; module load Miniforge3` swaps in the cluster's conda, which cannot see envs under a personal ~/miniconda3 root. Activation can also no-op without error in batch shells, so a `|| fallback` never fires.

## Fix
Pass CONDA_ENV as an ABSOLUTE path, prepend "\$CONDA_ENV/bin" to PATH, export PY="\$CONDA_ENV/bin/python" and call "\$PY" everywhere (never bare `python`). Then assert at job start: "\$PY" -c 'import sys; print(sys.executable)' must be inside \$CONDA_ENV, else exit with a readable message.

## Failed attempts
- Relying on conda activate / source activate exit status in sbatch scripts

## Verify
Job log near the top shows: [arc_env] python=/home/\<user>/miniconda3/envs/\<env>/bin/python

## Stack
| | |
|---|---|
| cluster | VT ARC |
| module | Miniforge3 |
| conda | personal ~/miniconda3 |

<small>created 2026-10-06 · id `conda-env-silently-falls-through-to-base-inside-slurm-batch-65e5`</small>

## Notes

<!-- callcentre:end -->
Source commits cef7d8f, c7b1665. Caveat from the repo: in that incident the REAL cause turned out to be a zero-byte python binary (separate entry) — run `$CONDA_ENV/bin/python -V` first. The absolute-path + assertion pattern is still worth keeping.
