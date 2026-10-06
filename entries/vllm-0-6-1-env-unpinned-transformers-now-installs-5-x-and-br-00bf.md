---
id: vllm-0-6-1-env-unpinned-transformers-now-installs-5-x-and-br-00bf
kind: fix
title: 'vllm 0.6.1 env: unpinned transformers now installs 5.x and breaks vllm; pin transformers==4.44.2'
domain:
- python-env
- eval
stack:
  vllm: 0.6.1
  transformers: 4.44.2
  python: 3.11 (eval), 3.10 (training)
  cuda: '12.6'
symptoms:
- Installing requirements with vllm<=0.6.1 and unpinned transformers pulls transformers 5.x, which vllm
  0.6.1 predates (import / generation breaks)
root_cause: ''
fix: Install in stages and pin transformers==4.44.2; install flash_attn after torch with --no-build-isolation.
failed_attempts:
- 'Leaving vllm unpinned in a training env: it also drags in transformers 5.x'
verify: ''
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# vllm 0.6.1 env: unpinned transformers now installs 5.x and breaks vllm; pin transformers==4.44.2

> [!note] fix · unverified · used 0×, failed 0×
> #python-env #eval #kind/fix #status/unverified

## Symptoms
```text
Installing requirements with vllm<=0.6.1 and unpinned transformers pulls transformers 5.x, which vllm 0.6.1 predates (import / generation breaks)
```

## Fix
Install in stages and pin transformers==4.44.2; install flash_attn after torch with --no-build-isolation.

## Failed attempts
- Leaving vllm unpinned in a training env: it also drags in transformers 5.x

## Stack
| | |
|---|---|
| vllm | 0.6.1 |
| transformers | 4.44.2 |
| python | 3.11 (eval), 3.10 (training) |
| cuda | 12.6 |

<small>created 2026-10-06 · id `vllm-0-6-1-env-unpinned-transformers-now-installs-5-x-and-br-00bf`</small>

## Notes

<!-- callcentre:end -->
From acereasoning-sft100k (agent acereason-sft-claude), recorded 2026-10-05; not re-verified.

Also: current hiyouga/LLaMA-Factory main needs Python>=3.11, so a py3.10 training env must use an older LLaMA-Factory snapshot. Related: [[transformers-5-x-renamed-trainingarguments-fields-warmup-rat-1740]].
