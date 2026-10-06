---
id: token-caps-truncate-silently-check-max-vs-p90-of-generated-l-7835
kind: convention
title: Token caps truncate silently — check max vs p90 of generated lengths, and keep max_new_tokens identical
  across distill/SFT/GRPO/eval
domain:
- rl-training
- eval
stack:
  vllm: 0.8.5
  model: Qwen2.5-VL-32B
  diffusers: SDXL (CLIP 77 tokens)
symptoms:
- Distillation rejected 80.4% of episodes as malformed vs 0.2% wrong verdicts (18% keep rate)
- 'Generated-turn word lengths: median 191, p90 231, max 249 at max_new_tokens=320 — distribution pressed
  against a wall'
- SDXL captions silently cut at CLIP's 77 tokens
- Group-variance gate answer rate fell 99.8% -> 75.8% when the prompt asked for more writing per turn
root_cause: A cap doesn't raise; it removes the end of the text. In multi-turn agent rollouts the trailing
  ACTION line is what gets cut, so the turn is unparseable and one bad turn kills the episode (~28% per-turn
  truncation -> ~80% episode loss). A mismatch (eval 640 vs train 320) means the policy is penalised in
  training for a limit it can't perceive.
fix: Raise max_new_tokens (320 -> 640; 900 when prompts ask for more text) and set it identically in every
  stage (distill, GRPO rollouts, shared helpers, eval) and plumb it through the SLURM launcher. Check
  max_model_len (vLLM 16384) still covers overview + one image per reveal + all prior text, and limit_mm_per_prompt
  = max_inspects + 4. For SDXL prompts, ask for ~50 words, clutter first, and audit with the pipeline's
  own tokenizer.
failed_attempts: []
verify: python -c "import json,statistics; rows=[json.loads(l) for l in open('traces.jsonl')]; L=sorted(len(a.split())
  for r in rows for a in r['actions']); print('median',statistics.median(L),'p90',L[int(.9*len(L))],'max',L[-1])"  —
  max near the cap with small p90 gap = truncation (and this only sees survivors).
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Token caps truncate silently — check max vs p90 of generated lengths, and keep max_new_tokens identical across distill/SFT/GRPO/eval

> [!note] convention · unverified · used 0×, failed 0×
> #rl-training #eval #kind/convention #status/unverified

## Symptoms
```text
Distillation rejected 80.4% of episodes as malformed vs 0.2% wrong verdicts (18% keep rate)
Generated-turn word lengths: median 191, p90 231, max 249 at max_new_tokens=320 — distribution pressed against a wall
SDXL captions silently cut at CLIP's 77 tokens
Group-variance gate answer rate fell 99.8% -> 75.8% when the prompt asked for more writing per turn
```

## Root cause
A cap doesn't raise; it removes the end of the text. In multi-turn agent rollouts the trailing ACTION line is what gets cut, so the turn is unparseable and one bad turn kills the episode (~28% per-turn truncation -> ~80% episode loss). A mismatch (eval 640 vs train 320) means the policy is penalised in training for a limit it can't perceive.

## Convention
Raise max_new_tokens (320 -> 640; 900 when prompts ask for more text) and set it identically in every stage (distill, GRPO rollouts, shared helpers, eval) and plumb it through the SLURM launcher. Check max_model_len (vLLM 16384) still covers overview + one image per reveal + all prior text, and limit_mm_per_prompt = max_inspects + 4. For SDXL prompts, ask for ~50 words, clutter first, and audit with the pipeline's own tokenizer.

## Verify
python -c "import json,statistics; rows=[json.loads(l) for l in open('traces.jsonl')]; L=sorted(len(a.split()) for r in rows for a in r['actions']); print('median',statistics.median(L),'p90',L[int(.9*len(L))],'max',L[-1])"  — max near the cap with small p90 gap = truncation (and this only sees survivors).

## Stack
| | |
|---|---|
| vllm | 0.8.5 |
| model | Qwen2.5-VL-32B |
| diffusers | SDXL (CLIP 77 tokens) |

<small>created 2026-10-06 · id `token-caps-truncate-silently-check-max-vs-p90-of-generated-l-7835`</small>

## Notes

<!-- callcentre:end -->
Source: docs/arc_runbook.md §8, commits 0148026, 01fe4f7, 91ca4b1. Look at the maximum, not the mean.
