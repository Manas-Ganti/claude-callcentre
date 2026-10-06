---
id: deepspeed-optimizer-offload-dies-with-missingcudaexception-d-c1ef
kind: fix
title: DeepSpeed optimizer offload dies with MissingCUDAException (DeepSpeedCPUAdam needs nvcc) on ARC
  compute nodes — use offload_param only for LoRA
domain:
- infra
- rl-training
- deepspeed
- vt-arc
stack:
  deepspeed: 0.19.5
  transformers: 5.15.0
  trl: 1.9.2
  peft: 0.20.0
  accelerate: 1.14.0
  gpu: A100-80GB
  model: Qwen2.5-VL-32B + LoRA
symptoms:
- 'MissingCUDAException: CUDA_HOME does not exist, unable to compile CUDA op(s)'
- Dies before the first training step when using a ZeRO-3 config with offload_optimizer to cpu
root_cause: offload_optimizer forces DeepSpeedCPUAdam, a JIT-compiled CUDA extension that needs nvcc via
  CUDA_HOME; VT ARC compute nodes don't expose nvcc. Optional fused ops just warn and fall back, but CPUAdam
  is mandatory for optimizer offload, so it is fatal.
fix: "For LoRA, don't offload the optimizer — the adapter's Adam state is a few hundred MB; it's the frozen\
  \ base params that must leave the GPU. ZeRO-3 config:\n  \"zero_force_ds_cpu_optimizer\": false,\n \
  \ \"zero_optimization\": {\"stage\": 3, \"offload_param\": {\"device\": \"cpu\", \"pin_memory\": true},\
  \ \"overlap_comm\": true, \"contiguous_gradients\": true, \"stage3_gather_16bit_weights_on_model_save\"\
  : true, ...}\n(no offload_optimizer block). Request --mem=300G or more for pinned host memory."
failed_attempts:
- Full offload config (offload_param + offload_optimizer to cpu) — MissingCUDAException
- Plain ZeRO-3 without offload on A100-80GB — OOM (see separate entry)
verify: 'grep offload_optimizer <ds_config>.json returns nothing; job reaches step 1. Measured: Qwen2.5-VL-32B
  LoRA SFT on 2xA100-80GB completed in 3.9 h.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# DeepSpeed optimizer offload dies with MissingCUDAException (DeepSpeedCPUAdam needs nvcc) on ARC compute nodes — use offload_param only for LoRA

> [!note] fix · unverified · used 0×, failed 0×
> #infra #rl-training #deepspeed #vt-arc #kind/fix #status/unverified

## Symptoms
```text
MissingCUDAException: CUDA_HOME does not exist, unable to compile CUDA op(s)
Dies before the first training step when using a ZeRO-3 config with offload_optimizer to cpu
```

## Root cause
offload_optimizer forces DeepSpeedCPUAdam, a JIT-compiled CUDA extension that needs nvcc via CUDA_HOME; VT ARC compute nodes don't expose nvcc. Optional fused ops just warn and fall back, but CPUAdam is mandatory for optimizer offload, so it is fatal.

## Fix
For LoRA, don't offload the optimizer — the adapter's Adam state is a few hundred MB; it's the frozen base params that must leave the GPU. ZeRO-3 config:
  "zero_force_ds_cpu_optimizer": false,
  "zero_optimization": {"stage": 3, "offload_param": {"device": "cpu", "pin_memory": true}, "overlap_comm": true, "contiguous_gradients": true, "stage3_gather_16bit_weights_on_model_save": true, ...}
(no offload_optimizer block). Request --mem=300G or more for pinned host memory.

## Failed attempts
- Full offload config (offload_param + offload_optimizer to cpu) — MissingCUDAException
- Plain ZeRO-3 without offload on A100-80GB — OOM (see separate entry)

## Verify
grep offload_optimizer \<ds_config>.json returns nothing; job reaches step 1. Measured: Qwen2.5-VL-32B LoRA SFT on 2xA100-80GB completed in 3.9 h.

## Stack
| | |
|---|---|
| deepspeed | 0.19.5 |
| transformers | 5.15.0 |
| trl | 1.9.2 |
| peft | 0.20.0 |
| accelerate | 1.14.0 |
| gpu | A100-80GB |
| model | Qwen2.5-VL-32B + LoRA |

<small>created 2026-10-06 · id `deepspeed-optimizer-offload-dies-with-missingcudaexception-d-c1ef`</small>

## Notes

<!-- callcentre:end -->
Source commits d8bce3c, 7433ef3; configs/deepspeed_zero3_offload_param.json. Gotcha: don't patch JSON configs via heredoc with escape sequences — a literal \n broke the JSON once (ff89115).
