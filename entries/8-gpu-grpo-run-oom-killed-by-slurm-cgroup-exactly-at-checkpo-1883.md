---
id: 8-gpu-grpo-run-oom-killed-by-slurm-cgroup-exactly-at-checkpo-1883
kind: fix
title: 8-GPU GRPO run OOM-killed by SLURM cgroup exactly at checkpoint save — --mem cap too low; add resume_from_checkpoint
domain:
- infra
- rl-training
- vt-arc
- slurm
stack:
  trl: 1.9.2
  transformers: 5.15.0
  deepspeed: 0.19.5 ZeRO-2
  gpu: 8xA100-80GB, 1 node
  model: Qwen2.5-VL-32B LoRA
symptoms:
- GRPO job 7520138 killed by the SLURM cgroup OOM killer at step 100 of 140, after 9h58m, with 4h28m left
  in a 24h wall
- Kill lands exactly when save_steps=100 fires
- 'Restart starts from step 0: trainer.train() never given resume_from_checkpoint'
root_cause: 'Consolidating/saving optimizer + model state across 8 ranks spikes HOST RAM. The job was
  submitted with --mem=300G (carried over from the param-offload SFT, where 300G was a FLOOR for pinned
  memory) on a node with far more RAM, overriding the launcher''s #SBATCH --mem=0.'
fix: 'For full-node jobs use --mem=0 (whole node''s memory). Add a --resume flag: trainer.train(resume_from_checkpoint=<path
  or True for newest in output_dir>) so optimizer, scheduler and global step are restored and paid-for
  rollouts aren''t re-run. Expose it on the launcher (RESUME=<path>).'
failed_attempts:
- --mem=300G on a full 8-GPU node — cgroup OOM at save
verify: sacct -j <id> --format=JobID,State,MaxRSS,ReqTRES%40 — State should not be OUT_OF_MEMORY and ReqTRES
  mem should be the node's full memory; on resume the log shows the global step continuing from N.
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# 8-GPU GRPO run OOM-killed by SLURM cgroup exactly at checkpoint save — --mem cap too low; add resume_from_checkpoint

> [!note] fix · unverified · used 0×, failed 0×
> #infra #rl-training #vt-arc #slurm #kind/fix #status/unverified

## Symptoms
```text
GRPO job 7520138 killed by the SLURM cgroup OOM killer at step 100 of 140, after 9h58m, with 4h28m left in a 24h wall
Kill lands exactly when save_steps=100 fires
Restart starts from step 0: trainer.train() never given resume_from_checkpoint
```

## Root cause
Consolidating/saving optimizer + model state across 8 ranks spikes HOST RAM. The job was submitted with --mem=300G (carried over from the param-offload SFT, where 300G was a FLOOR for pinned memory) on a node with far more RAM, overriding the launcher's \#SBATCH --mem=0.

## Fix
For full-node jobs use --mem=0 (whole node's memory). Add a --resume flag: trainer.train(resume_from_checkpoint=\<path or True for newest in output_dir>) so optimizer, scheduler and global step are restored and paid-for rollouts aren't re-run. Expose it on the launcher (RESUME=\<path>).

## Failed attempts
- --mem=300G on a full 8-GPU node — cgroup OOM at save

## Verify
sacct -j \<id> --format=JobID,State,MaxRSS,ReqTRES%40 — State should not be OUT_OF_MEMORY and ReqTRES mem should be the node's full memory; on resume the log shows the global step continuing from N.

## Stack
| | |
|---|---|
| trl | 1.9.2 |
| transformers | 5.15.0 |
| deepspeed | 0.19.5 ZeRO-2 |
| gpu | 8xA100-80GB, 1 node |
| model | Qwen2.5-VL-32B LoRA |

<small>created 2026-10-06 · id `8-gpu-grpo-run-oom-killed-by-slurm-cgroup-exactly-at-checkpo-1883`</small>

## Notes

<!-- callcentre:end -->
Source commit 4657854. Related: a run killed by walltime leaves only checkpoint-N/ subdirs — the top-level adapter is written by the final save, which a timeout skips (GRPO run 1 hit the 24h wall at step 696/1258, ~120 s/step; checkpoint-600 was the usable adapter). Size --max-steps to the wall.
