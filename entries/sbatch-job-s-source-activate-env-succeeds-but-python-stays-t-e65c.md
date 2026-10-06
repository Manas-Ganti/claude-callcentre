---
id: sbatch-job-s-source-activate-env-succeeds-but-python-stays-t-e65c
kind: fix
title: sbatch job's `source activate <env>` succeeds but python stays the Miniconda module's base 3.13
  (VT ARC)
domain:
- infra
- python-env
- vt-arc
- slurm
stack:
  cluster: VT ARC Tinkercliffs
  conda: Miniconda3 module + personal ~/miniconda3 (auto_activate_base)
  cuda: 12.6.0 module
symptoms:
- '`module load Miniconda3; source activate <env>` succeeds inside the sbatch job, but `python` is still
  the module''s base Python 3.13 (sys.executable not inside the env)'
- '`conda env list` / `conda info` on the login node look correct'
root_cause: The login shell had a personal ~/miniconda3 base active (conda init + auto_activate_base)
  and sbatch copies that environment into the job. `conda activate` only strips the PREVIOUS prefix's
  PATH entries, so the module's bin (prepended by `module load`) stays in front of the new env.
fix: 'Submit from a conda-clean shell (CONDA_SHLVL=0: deactivate fully or strip CONDA_* vars before sbatch)
  and pass the env as an absolute path. For your own jobs skip activate entirely: set PATH and CONDA_PREFIX
  from the env path, call the env''s python by absolute path, export PYTHONNOUSERSITE=1, and assert a
  sentinel import at job start.'
failed_attempts:
- 'Trusting `conda env list` / `conda info` on the login node: they look right while the job runs the
  wrong python'
verify: 'Inside the job: `python -c ''import sys; print(sys.executable)''` points into the env'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# sbatch job's `source activate <env>` succeeds but python stays the Miniconda module's base 3.13 (VT ARC)

> [!note] fix · unverified · used 0×, failed 0×
> #infra #python-env #vt-arc #slurm #kind/fix #status/unverified

## Symptoms
```text
`module load Miniconda3; source activate <env>` succeeds inside the sbatch job, but `python` is still the module's base Python 3.13 (sys.executable not inside the env)
`conda env list` / `conda info` on the login node look correct
```

## Root cause
The login shell had a personal ~/miniconda3 base active (conda init + auto_activate_base) and sbatch copies that environment into the job. `conda activate` only strips the PREVIOUS prefix's PATH entries, so the module's bin (prepended by `module load`) stays in front of the new env.

## Fix
Submit from a conda-clean shell (CONDA_SHLVL=0: deactivate fully or strip CONDA_* vars before sbatch) and pass the env as an absolute path. For your own jobs skip activate entirely: set PATH and CONDA_PREFIX from the env path, call the env's python by absolute path, export PYTHONNOUSERSITE=1, and assert a sentinel import at job start.

## Failed attempts
- Trusting `conda env list` / `conda info` on the login node: they look right while the job runs the wrong python

## Verify
Inside the job: `python -c 'import sys; print(sys.executable)'` points into the env

## Stack
| | |
|---|---|
| cluster | VT ARC Tinkercliffs |
| conda | Miniconda3 module + personal ~/miniconda3 (auto_activate_base) |
| cuda | 12.6.0 module |

<small>created 2026-10-06 · id `sbatch-job-s-source-activate-env-succeeds-but-python-stays-t-e65c`</small>

## Notes

<!-- callcentre:end -->
From acereasoning-sft100k (agent acereason-sft-claude), recorded 2026-10-05; not re-verified. Repo scripts: launch/test_activation.sh, env/clean_conda.sh, env/arc_env.sh.

Related (same symptom family, different causes): [[conda-env-silently-falls-through-to-base-inside-slurm-batch-65e5]] (module conda can't see personal envs), [[slurm-gpu-job-completed-in-2-seconds-exit-0-empty-err-conda-c1fe]] (0-byte python binary).
