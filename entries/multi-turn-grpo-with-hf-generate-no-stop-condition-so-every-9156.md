---
id: multi-turn-grpo-with-hf-generate-no-stop-condition-so-every-9156
kind: fix
title: 'Multi-turn GRPO with HF generate: no stop condition, so every turn runs to max_new_tokens and
  the 32B rambles past its action'
domain:
- rl-training
stack:
  trl: 1.9.2
  transformers: 5.15.0
  model: Qwen2.5-VL-32B LoRA
  rollouts: HF generate (logprobs needed)
symptoms:
- Rollout reasons well, emits 'INSPECT 2', then generates five near-identical '### Turn 2 (Final Correction)'
  blocks; scores -0.87 for trailing noise
- Every turn uses the full max_new_tokens (640) whether finished or not; ~2/3 of each 130 s step spent
  on unwanted tokens
root_cause: The HF generate rollout path had only max_new_tokens and a repetition penalty — no stopping
  criterion at the end of a turn's action line.
fix: 'Add a StoppingCriteria that stops GENERATION (don''t post-hoc truncate text, or token ids/logprobs
  stop matching what the reward scores) when the decoded tail matches the completed action line. Each
  regex alternative must end one character PAST the value: e.g. r''INSPECT\s+\d+\D'' (else ''INSPECT 1''
  stops before the model writes ''12'') and for confidence exclude ''.'' from the terminator (a decimal
  point doesn''t prove the number ended).'
failed_attempts:
- Relying on repetition_penalty + max_new_tokens — turns still fill the cap with restarts
verify: Per-turn generated token counts drop well below max_new_tokens; parsed trajectories contain no
  duplicated turn headers; step time falls.
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Multi-turn GRPO with HF generate: no stop condition, so every turn runs to max_new_tokens and the 32B rambles past its action

> [!note] fix · unverified · used 0×, failed 0×
> #rl-training #kind/fix #status/unverified

## Symptoms
```text
Rollout reasons well, emits 'INSPECT 2', then generates five near-identical '### Turn 2 (Final Correction)' blocks; scores -0.87 for trailing noise
Every turn uses the full max_new_tokens (640) whether finished or not; ~2/3 of each 130 s step spent on unwanted tokens
```

## Root cause
The HF generate rollout path had only max_new_tokens and a repetition penalty — no stopping criterion at the end of a turn's action line.

## Fix
Add a StoppingCriteria that stops GENERATION (don't post-hoc truncate text, or token ids/logprobs stop matching what the reward scores) when the decoded tail matches the completed action line. Each regex alternative must end one character PAST the value: e.g. r'INSPECT\\s+\\d+\\D' (else 'INSPECT 1' stops before the model writes '12') and for confidence exclude '.' from the terminator (a decimal point doesn't prove the number ended).

## Failed attempts
- Relying on repetition_penalty + max_new_tokens — turns still fill the cap with restarts

## Verify
Per-turn generated token counts drop well below max_new_tokens; parsed trajectories contain no duplicated turn headers; step time falls.

## Stack
| | |
|---|---|
| trl | 1.9.2 |
| transformers | 5.15.0 |
| model | Qwen2.5-VL-32B LoRA |
| rollouts | HF generate (logprobs needed) |

<small>created 2026-10-06 · id `multi-turn-grpo-with-hf-generate-no-stop-condition-so-every-9156`</small>

## Notes

<!-- callcentre:end -->
Source commit 26ed6a8 (training/common.py).
