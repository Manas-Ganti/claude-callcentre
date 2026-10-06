---
id: vt-arc-job-environment-export-hf-home-and-wandb-dir-explicit-cd71
kind: convention
title: 'VT ARC job environment: export HF_HOME and WANDB_DIR explicitly on every submit'
domain:
- infra
- vt-arc
- slurm
stack: {}
symptoms:
- Model re-downloads (or is not found) in jobs although it's cached in your home dir
- wandb fails writing to /projects/$USER
- 'FutureWarning: HF_HUB_ENABLE_HF_TRANSFER is deprecated'
root_cause: 'Launcher defaults guessed the wrong paths: HF_HOME=/projects/$USER/hf_cache while the cache
  was /home/<user>/hf_cache (68 GB Qwen2.5-VL-32B), and /projects/$USER is not writable for wandb.'
fix: Export HF_HOME=<your real cache> and WANDB_DIR=$HOME/wandb on every submit (or in the env script).
  The HF_HUB_ENABLE_HF_TRANSFER FutureWarning is harmless noise (use HF_XET_HIGH_PERFORMANCE).
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
# VT ARC job environment: export HF_HOME and WANDB_DIR explicitly on every submit

> [!note] convention · unverified · used 0×, failed 0×
> #infra #vt-arc #slurm #kind/convention #status/unverified

## Symptoms
```text
Model re-downloads (or is not found) in jobs although it's cached in your home dir
wandb fails writing to /projects/$USER
FutureWarning: HF_HUB_ENABLE_HF_TRANSFER is deprecated
```

## Root cause
Launcher defaults guessed the wrong paths: HF_HOME=/projects/\$USER/hf_cache while the cache was /home/\<user>/hf_cache (68 GB Qwen2.5-VL-32B), and /projects/\$USER is not writable for wandb.

## Convention
Export HF_HOME=\<your real cache> and WANDB_DIR=\$HOME/wandb on every submit (or in the env script). The HF_HUB_ENABLE_HF_TRANSFER FutureWarning is harmless noise (use HF_XET_HIGH_PERFORMANCE).

<small>created 2026-10-06 · id `vt-arc-job-environment-export-hf-home-and-wandb-dir-explicit-cd71`</small>

## Notes

<!-- callcentre:end -->
From VLM-RL-aicontent-detection docs/arc_runbook.md + git history (agent vrr-arc-repo-mining); not reproduced in-session. Related: [[gatedrepoerror-401-in-jobs-despite-hf-auth-login-token-lives-c49d]] (token lives at $HF_HOME/token).
