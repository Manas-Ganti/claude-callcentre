---
id: reds-lab-project-reasoning-sft-llm-readme-setup-gotchas-yaml-2191
kind: fix
title: 'reds-lab Project-Reasoning-SFT-LLM: README setup gotchas (YAML comments, clone, SLURM limit, cutoff_len,
  skipped benchmarks)'
domain:
- eval
- sft
stack:
  repo: reds-lab/Project-Reasoning-SFT-LLM @ 4d31bfc
symptoms:
- Sample YAML config fails to parse (uses // comments)
- '`git depth -1 clone` is not a git command'
- Full SFT killed by the 1 h SLURM time limit from the README
- SFT model stops without \boxed{} on long problems
- eval silently skips a benchmark
root_cause: README examples are wrong in places; cutoff_len 16384 silently truncates long R1 traces, so
  the model learns to stop before \boxed{}; eval skips any benchmark whose per-benchmark jsonl already
  exists in OUTPUT_DIR.
fix: Use `#` comments in YAML; `git clone --depth 1`; request far more than 1 h for full SFT; raise cutoff_len
  to cover the longest traces (check max vs p90 of token lengths) or filter long traces; clear OUTPUT_DIR
  (or the benchmark's jsonl) before re-running eval.
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
# reds-lab Project-Reasoning-SFT-LLM: README setup gotchas (YAML comments, clone, SLURM limit, cutoff_len, skipped benchmarks)

> [!note] fix · unverified · used 0×, failed 0×
> #eval #sft #kind/fix #status/unverified

## Symptoms
```text
Sample YAML config fails to parse (uses // comments)
`git depth -1 clone` is not a git command
Full SFT killed by the 1 h SLURM time limit from the README
SFT model stops without \boxed{} on long problems
eval silently skips a benchmark
```

## Root cause
README examples are wrong in places; cutoff_len 16384 silently truncates long R1 traces, so the model learns to stop before \\boxed{}; eval skips any benchmark whose per-benchmark jsonl already exists in OUTPUT_DIR.

## Fix
Use `#` comments in YAML; `git clone --depth 1`; request far more than 1 h for full SFT; raise cutoff_len to cover the longest traces (check max vs p90 of token lengths) or filter long traces; clear OUTPUT_DIR (or the benchmark's jsonl) before re-running eval.

## Stack
| | |
|---|---|
| repo | reds-lab/Project-Reasoning-SFT-LLM @ 4d31bfc |

<small>created 2026-10-06 · id `reds-lab-project-reasoning-sft-llm-readme-setup-gotchas-yaml-2191`</small>

## Notes

<!-- callcentre:end -->
From acereasoning-sft100k (agent acereason-sft-claude), recorded 2026-10-05; not re-verified. Related: [[token-caps-truncate-silently-check-max-vs-p90-of-generated-l-7835]] (token caps truncate silently).
