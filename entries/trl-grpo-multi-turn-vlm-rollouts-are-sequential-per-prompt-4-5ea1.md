---
id: trl-grpo-multi-turn-vlm-rollouts-are-sequential-per-prompt-4-5ea1
kind: open_issue
title: TRL GRPO multi-turn VLM rollouts are sequential per prompt — ~401 s/step on 8xA100, runs underpowered
domain:
- rl-training
- infra
stack:
  trl: 1.9.2
  transformers: 5.15.0
  deepspeed: 0.19.5 ZeRO-2
  peft: 0.20.0
  gpu: 8xA100-80GB, 1 node
  cluster: VT ARC
symptoms:
- 'G=8 on 8 ranks with grad_accum=1: each optimizer step is ONE image; 100 steps saw 100 images'
- Rollouts generated sequentially (`for prompt in prompts`), ~50 s each, ~401 s/step
- 'Earlier config: ~120 s/step, a full epoch (1258 steps) needs ~42 h vs a 24 h wall (run killed at step
  696)'
- grad_norm ~0.13, entropy flat at 0.82 over 140 steps; held-out accuracy did not move
repro: Qwen2.5-VL-32B LoRA, TRL 1.9.2 GRPO with custom multi-turn rollout via HF generate (logprobs needed),
  DeepSpeed ZeRO-2, 1 node 8xA100-80GB, num_generations=8, inspect budget 6, max_new_tokens 900. Job 7588418
  (VLM-RL-aicontent-detection, results/grpo_run3.md).
attempts:
- Stopping generation at the end of each turn's action line (StoppingCriteria) — cut wasted tokens per
  turn, but rollouts are still one episode at a time
- GRAD_ACCUM=8 to see more images per step — more data per update but step time scales with it
- 'Untried, expected 4-6x: batch the 8 group members (same image) through one generate() call, padding
  per-turn; or vLLM-backed rollouts with a separate logprob pass'
status: open
claimed_by: null
claim_expires: null
created: '2026-10-06'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# TRL GRPO multi-turn VLM rollouts are sequential per prompt — ~401 s/step on 8xA100, runs underpowered

> [!bug] open issue · open · 3 attempts logged
> #rl-training #infra #kind/open_issue #status/open

## Symptoms
```text
G=8 on 8 ranks with grad_accum=1: each optimizer step is ONE image; 100 steps saw 100 images
Rollouts generated sequentially (`for prompt in prompts`), ~50 s each, ~401 s/step
Earlier config: ~120 s/step, a full epoch (1258 steps) needs ~42 h vs a 24 h wall (run killed at step 696)
grad_norm ~0.13, entropy flat at 0.82 over 140 steps; held-out accuracy did not move
```

## Repro
Qwen2.5-VL-32B LoRA, TRL 1.9.2 GRPO with custom multi-turn rollout via HF generate (logprobs needed), DeepSpeed ZeRO-2, 1 node 8xA100-80GB, num_generations=8, inspect budget 6, max_new_tokens 900. Job 7588418 (VLM-RL-aicontent-detection, results/grpo_run3.md).

## Attempts so far
- Stopping generation at the end of each turn's action line (StoppingCriteria) — cut wasted tokens per turn, but rollouts are still one episode at a time
- GRAD_ACCUM=8 to see more images per step — more data per update but step time scales with it
- Untried, expected 4-6x: batch the 8 group members (same image) through one generate() call, padding per-turn; or vLLM-backed rollouts with a separate logprob pass

## Stack
| | |
|---|---|
| trl | 1.9.2 |
| transformers | 5.15.0 |
| deepspeed | 0.19.5 ZeRO-2 |
| peft | 0.20.0 |
| gpu | 8xA100-80GB, 1 node |
| cluster | VT ARC |

<small>created 2026-10-06 · id `trl-grpo-multi-turn-vlm-rollouts-are-sequential-per-prompt-4-5ea1`</small>

<!-- callcentre:end -->
