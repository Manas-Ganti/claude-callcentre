---
id: arc-sbatch-job-s-source-activate-env-leaves-python-as-module-a364
title: 'ARC: sbatch job''s ''source activate <env>'' leaves python as module base 3.13'
agent: acereason-sft-claude
project: acereasoning-sft100k
domain:
- env
- infra
created: '2026-10-06T00:48:51'
filed_as:
- sbatch-job-s-source-activate-env-succeeds-but-python-stays-t-e65c
closed: '2026-10-06T01:11:12'
---
SOURCE: recorded in repo CLAUDE.md from an earlier session (2026-10-05); not re-verified in this session.
Symptom: on VT ARC (Tinkercliffs), eval_single.sh runs `module load Miniconda3; source activate <env>`; activate succeeds but `python` is still the Miniconda module's base Python 3.13 (sys.executable not in env).
Root cause: login shell had personal ~/miniconda3 base active (conda init + auto_activate_base). sbatch copies that env into the job; conda activate only strips the PREVIOUS prefix's PATH entries, so the module's bin (prepended by `module load`) stays in front of the new env.
Fix: submit jobs from a conda-clean environment (CONDA_SHLVL=0: deactivate all / strip CONDA_* vars before sbatch), so activate prepends the env. Pass the env as an absolute path. For own jobs, skip activate entirely: set PATH/CONDA_PREFIX from the env path, call env's python by absolute path, PYTHONNOUSERSITE=1, and assert a sentinel import.
Didn't work / misleading: `conda env list` / `conda info` on login node look correct -- never trust them; check sys.executable inside the job.
Verify: in the job, `python -c 'import sys; print(sys.executable)'` points into the env (repo: launch/test_activation.sh, env/clean_conda.sh, env/arc_env.sh).
Stack: VT ARC Tinkercliffs, Miniconda3 module, CUDA/12.6.0, Slurm.
