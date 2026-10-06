---
id: rsl-rl-ppo-with-clipped-continuous-actions-entropy-coef-0-00-59ca
kind: convention
title: 'rsl_rl PPO with clipped continuous actions: entropy_coef 0.005 makes action std grow; use 0.001'
domain:
- rl-training
stack:
  rsl-rl-lib: 2.3.1
  isaaclab: v2.1.0
  num_envs: 2048
  gpu: L40S
symptoms:
- Policy action noise std grows during training (1.0 -> 1.96) instead of shrinking
- Policy leans on action clipping
root_cause: With clipped actions, extra noise beyond the clip is free for the return, so the entropy bonus
  keeps pushing std up.
fix: Set algo.ppo.algorithm.entropy_coef=0.001 (std converged to 0.21, reward ~240). Use --resume auto
  + a fixed --run-name to survive SLURM walltime kills.
failed_attempts: []
verify: 'W&B: Policy/mean_noise_std decreasing over iterations.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# rsl_rl PPO with clipped continuous actions: entropy_coef 0.005 makes action std grow; use 0.001

> [!note] convention · unverified · used 0×, failed 0×
> #rl-training #kind/convention #status/unverified

## Symptoms
```text
Policy action noise std grows during training (1.0 -> 1.96) instead of shrinking
Policy leans on action clipping
```

## Root cause
With clipped actions, extra noise beyond the clip is free for the return, so the entropy bonus keeps pushing std up.

## Convention
Set algo.ppo.algorithm.entropy_coef=0.001 (std converged to 0.21, reward ~240). Use --resume auto + a fixed --run-name to survive SLURM walltime kills.

## Verify
W&B: Policy/mean_noise_std decreasing over iterations.

## Stack
| | |
|---|---|
| rsl-rl-lib | 2.3.1 |
| isaaclab | v2.1.0 |
| num_envs | 2048 |
| gpu | L40S |

<small>created 2026-10-06 · id `rsl-rl-ppo-with-clipped-continuous-actions-entropy-coef-0-00-59ca`</small>

<!-- callcentre:end -->
