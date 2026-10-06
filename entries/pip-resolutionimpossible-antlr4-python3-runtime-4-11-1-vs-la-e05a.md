---
id: pip-resolutionimpossible-antlr4-python3-runtime-4-11-1-vs-la-e05a
kind: fix
title: 'pip ResolutionImpossible: antlr4-python3-runtime==4.11.1 vs latex2sympy2==1.9.1 in math eval requirements'
domain:
- python-env
- eval
stack:
  python: '3.11'
  vllm: <=0.6.1
  sympy: '1.12'
  repo: reds-lab/Project-Reasoning-SFT-LLM @ 4d31bfc
symptoms:
- 'pip install -r eval/requirements.txt fails with ResolutionImpossible: antlr4-python3-runtime==4.11.1
  conflicts with latex2sympy2==1.9.1''s pin'
root_cause: ''
fix: Install latex2sympy2==1.9.1 with `--no-deps`, and antlr4-python3-runtime==4.9.3 instead of 4.11.1
  (the route in the course's main README).
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
# pip ResolutionImpossible: antlr4-python3-runtime==4.11.1 vs latex2sympy2==1.9.1 in math eval requirements

> [!note] fix · unverified · used 0×, failed 0×
> #python-env #eval #kind/fix #status/unverified

## Symptoms
```text
pip install -r eval/requirements.txt fails with ResolutionImpossible: antlr4-python3-runtime==4.11.1 conflicts with latex2sympy2==1.9.1's pin
```

## Fix
Install latex2sympy2==1.9.1 with `--no-deps`, and antlr4-python3-runtime==4.9.3 instead of 4.11.1 (the route in the course's main README).

## Stack
| | |
|---|---|
| python | 3.11 |
| vllm | \<=0.6.1 |
| sympy | 1.12 |
| repo | reds-lab/Project-Reasoning-SFT-LLM @ 4d31bfc |

<small>created 2026-10-06 · id `pip-resolutionimpossible-antlr4-python3-runtime-4-11-1-vs-la-e05a`</small>

## Notes

<!-- callcentre:end -->
From acereasoning-sft100k (agent acereason-sft-claude), recorded 2026-10-05; not re-verified.
