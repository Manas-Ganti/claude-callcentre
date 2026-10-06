---
id: custom-grpo-lora-trainer-next-to-vllm-keeps-ooming-slice-log-af5e
kind: fix
title: 'Custom GRPO LoRA trainer next to vLLM keeps OOMing: slice logits before log_softmax, ref pass
  first, own GPU + set_device'
domain:
- rl-training
- infra
- vt-arc
stack:
  model: Qwen-family 7B bf16 + LoRA (vocab 152064)
  vllm: '0.28'
  peft: '>=0.12'
  torch: '>=2.4'
  gpu: 2x A100-80GB, then H200-141GB
  cluster: VT ARC
symptoms:
- 'OOM at first backward: vLLM EngineCore 45.58 GiB, trainer 27.32 GiB, free 6.33 GiB, needed 6.88 more'
- Trainer at 45.4 GiB for a 7B LoRA (expected ~17)
- 'After moving the trainer to cuda:1 via device_map: torch.AcceleratorError: CUDA error: an illegal memory
  access was encountered (traceback points at empty_cache())'
- '''expandable_segments: memory mapping failed ... free: 20840448'' mid-step'
- Later OOM at 77.68 GiB on a card the trainer had to itself, as episodes grew longer
root_cause: (1) logits.float().log_softmax(-1) over the full T=4000 x vocab=152064 sequence materialises
  ~4.5 GiB per forward when only ~300 completion positions are read. (2) The reference forward ran while
  the policy graph was alive, so peak = graph + ref. (3) Sharing one card with vLLM's preallocated KV
  cache moves pressure back and forth. (4) device_map={'':'cuda:1'} places weights, but the CURRENT device
  stays cuda:0, so unnamed allocations land on vLLM's card and fault asynchronously. (5) Sequence length
  grows during training as the policy acts more.
fix: Slice hidden/logits to completion positions BEFORE softmax and use F.cross_entropy(reduction='none')
  for token logprobs. Compute reference logprobs FIRST, under no_grad via model.disable_adapter() (not
  a separate aliased base), and free them before the policy forward. Put vLLM and the trainer on separate
  GPUs and call torch.cuda.set_device(trainer_dev) on entry to every trainer method. Accumulate per sequence,
  scaling the loss by each sequence's share of the step's tokens. Use gradient checkpointing with use_reentrant=False
  and use_cache=False. Set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True and call empty_cache() every
  ~16 sequences. Cap gradient tokens (e.g. 6144), counting and logging skipped sequences. Print memory
  at each load stage instead of guessing.
failed_attempts:
- 'Guessing the dtype was fp32: the memory ladder showed the model loaded at 14.19 GiB bf16, so the guess
  was wrong'
- 'Micro-batching alone (micro_batch_size=2): batching 4k-token sequences just doubles the logits tensor'
- 'Lowering vLLM gpu_memory_utilization to 0.40 on a shared card: moved the OOM to the trainer'
- 'use_reentrant=True checkpointing with a frozen base + LoRA: skips segments whose inputs don''t require
  grad, so it may save nothing'
verify: The step log reports per-stage allocation and [rollout/grad/sync] timings. A 100-step run completes
  with no 'memory mapping failed' lines, and skipped-sequence counts are reported.
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Custom GRPO LoRA trainer next to vLLM keeps OOMing: slice logits before log_softmax, ref pass first, own GPU + set_device

> [!note] fix · unverified · used 0×, failed 0×
> #rl-training #infra #vt-arc #kind/fix #status/unverified

## Symptoms
```text
OOM at first backward: vLLM EngineCore 45.58 GiB, trainer 27.32 GiB, free 6.33 GiB, needed 6.88 more
Trainer at 45.4 GiB for a 7B LoRA (expected ~17)
After moving the trainer to cuda:1 via device_map: torch.AcceleratorError: CUDA error: an illegal memory access was encountered (traceback points at empty_cache())
'expandable_segments: memory mapping failed ... free: 20840448' mid-step
Later OOM at 77.68 GiB on a card the trainer had to itself, as episodes grew longer
```

## Root cause
(1) logits.float().log_softmax(-1) over the full T=4000 x vocab=152064 sequence materialises ~4.5 GiB per forward when only ~300 completion positions are read. (2) The reference forward ran while the policy graph was alive, so peak = graph + ref. (3) Sharing one card with vLLM's preallocated KV cache moves pressure back and forth. (4) device_map={'':'cuda:1'} places weights, but the CURRENT device stays cuda:0, so unnamed allocations land on vLLM's card and fault asynchronously. (5) Sequence length grows during training as the policy acts more.

## Fix
Slice hidden/logits to completion positions BEFORE softmax and use F.cross_entropy(reduction='none') for token logprobs. Compute reference logprobs FIRST, under no_grad via model.disable_adapter() (not a separate aliased base), and free them before the policy forward. Put vLLM and the trainer on separate GPUs and call torch.cuda.set_device(trainer_dev) on entry to every trainer method. Accumulate per sequence, scaling the loss by each sequence's share of the step's tokens. Use gradient checkpointing with use_reentrant=False and use_cache=False. Set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True and call empty_cache() every ~16 sequences. Cap gradient tokens (e.g. 6144), counting and logging skipped sequences. Print memory at each load stage instead of guessing.

## Failed attempts
- Guessing the dtype was fp32: the memory ladder showed the model loaded at 14.19 GiB bf16, so the guess was wrong
- Micro-batching alone (micro_batch_size=2): batching 4k-token sequences just doubles the logits tensor
- Lowering vLLM gpu_memory_utilization to 0.40 on a shared card: moved the OOM to the trainer
- use_reentrant=True checkpointing with a frozen base + LoRA: skips segments whose inputs don't require grad, so it may save nothing

## Verify
The step log reports per-stage allocation and [rollout/grad/sync] timings. A 100-step run completes with no 'memory mapping failed' lines, and skipped-sequence counts are reported.

## Stack
| | |
|---|---|
| model | Qwen-family 7B bf16 + LoRA (vocab 152064) |
| vllm | 0.28 |
| peft | >=0.12 |
| torch | >=2.4 |
| gpu | 2x A100-80GB, then H200-141GB |
| cluster | VT ARC |

<small>created 2026-10-06 · id `custom-grpo-lora-trainer-next-to-vllm-keeps-ooming-slice-log-af5e`</small>

## Notes

<!-- callcentre:end -->
Sourced from healthcare_RL git history (ca13f0f, 7778335, 92f19c7, 898019b, 0b54227, 683fe47), not reproduced this session. The final config ran 99 GRPO steps at ~8 min/step. Related gotcha (d1fa88d): get_peft_model injects LoRA IN PLACE, so keeping `ref = base` aliases the adapted model and KL reads exactly 0 all run. Use disable_adapter() for the reference. Also note that with one inner epoch the PPO clip is inert (ratio == 1).
