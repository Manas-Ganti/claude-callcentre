---
id: zero-3-still-ooms-loading-a-32b-model-on-80gb-a100s-every-ra-83eb
kind: fix
title: ZeRO-3 still OOMs loading a 32B model on 80GB A100s — every rank materialises the full model in
  from_pretrained
domain:
- infra
- rl-training
- deepspeed
- vt-arc
stack:
  deepspeed: 0.19.5
  transformers: 5.15.0
  trl: 1.9.2
  gpu: A100-80GB x2-8
  model: Qwen2.5-VL-32B LoRA
symptoms:
- CUDA out of memory while loading Qwen2.5-VL-32B (~66 GB bf16) on A100-80GB under DeepSpeed ZeRO-3, before
  training starts
- ZeRO-3 appears not to shard parameters at load time
root_cause: On this stack each rank materialises the whole model during from_pretrained before DeepSpeed
  partitions anything (ZeRO-3 init only partitions at load if the HF DeepSpeed config / TrainingArguments
  is constructed BEFORE the model; even so it did not fit here).
fix: Construct TrainingArguments/SFTConfig/GRPOConfig BEFORE from_pretrained (so is_deepspeed_zero3_enabled()
  is true at load), and use ZeRO-3 with offload_param to CPU (parameters only, no optimizer offload),
  --mem=300G+. On H200 (141 GB) a 32B fits on one GPU and plain ZeRO-2 is fine.
failed_attempts:
- deepspeed_zero3.json (no offload) on A100-80GB — OOM
- full ZeRO-3 offload (param+optimizer) — MissingCUDAException from DeepSpeedCPUAdam
verify: Job reaches step 1; nvidia-smi per-GPU memory well under 80 GB after load.
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# ZeRO-3 still OOMs loading a 32B model on 80GB A100s — every rank materialises the full model in from_pretrained

> [!note] fix · unverified · used 0×, failed 0×
> #infra #rl-training #deepspeed #vt-arc #kind/fix #status/unverified

## Symptoms
```text
CUDA out of memory while loading Qwen2.5-VL-32B (~66 GB bf16) on A100-80GB under DeepSpeed ZeRO-3, before training starts
ZeRO-3 appears not to shard parameters at load time
```

## Root cause
On this stack each rank materialises the whole model during from_pretrained before DeepSpeed partitions anything (ZeRO-3 init only partitions at load if the HF DeepSpeed config / TrainingArguments is constructed BEFORE the model; even so it did not fit here).

## Fix
Construct TrainingArguments/SFTConfig/GRPOConfig BEFORE from_pretrained (so is_deepspeed_zero3_enabled() is true at load), and use ZeRO-3 with offload_param to CPU (parameters only, no optimizer offload), --mem=300G+. On H200 (141 GB) a 32B fits on one GPU and plain ZeRO-2 is fine.

## Failed attempts
- deepspeed_zero3.json (no offload) on A100-80GB — OOM
- full ZeRO-3 offload (param+optimizer) — MissingCUDAException from DeepSpeedCPUAdam

## Verify
Job reaches step 1; nvidia-smi per-GPU memory well under 80 GB after load.

## Stack
| | |
|---|---|
| deepspeed | 0.19.5 |
| transformers | 5.15.0 |
| trl | 1.9.2 |
| gpu | A100-80GB x2-8 |
| model | Qwen2.5-VL-32B LoRA |

<small>created 2026-10-06 · id `zero-3-still-ooms-loading-a-32b-model-on-80gb-a100s-every-ra-83eb`</small>

## Notes

<!-- callcentre:end -->
Source: docs/arc_quickref.md, results/what_we_know.md §6. Root cause is as documented in the repo, not independently reproduced.
