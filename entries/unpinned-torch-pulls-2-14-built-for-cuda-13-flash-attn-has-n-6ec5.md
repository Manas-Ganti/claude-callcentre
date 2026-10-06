---
id: unpinned-torch-pulls-2-14-built-for-cuda-13-flash-attn-has-n-6ec5
kind: fix
title: 'Unpinned torch pulls 2.14 built for CUDA 13: flash-attn has no wheel and won''t build against
  CUDA 12.6'
domain:
- python-env
- infra
- vt-arc
stack:
  cluster: VT ARC
  cuda: 12.6.0 module
  python: '3.10'
  gpu: A100 / H200
symptoms:
- pip install of LLaMA-Factory requirements with unpinned torch installs torch 2.14 built for CUDA 13.0
- flash-attn then has no prebuilt wheel, and the source build fails against module CUDA/12.6.0
root_cause: ''
fix: Pin torch==2.6.0+cu126 from the cu126 index BEFORE installing flash-attn (install flash-attn after
  torch, with --no-build-isolation).
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
# Unpinned torch pulls 2.14 built for CUDA 13: flash-attn has no wheel and won't build against CUDA 12.6

> [!note] fix · unverified · used 0×, failed 0×
> #python-env #infra #vt-arc #kind/fix #status/unverified

## Symptoms
```text
pip install of LLaMA-Factory requirements with unpinned torch installs torch 2.14 built for CUDA 13.0
flash-attn then has no prebuilt wheel, and the source build fails against module CUDA/12.6.0
```

## Fix
Pin torch==2.6.0+cu126 from the cu126 index BEFORE installing flash-attn (install flash-attn after torch, with --no-build-isolation).

## Stack
| | |
|---|---|
| cluster | VT ARC |
| cuda | 12.6.0 module |
| python | 3.10 |
| gpu | A100 / H200 |

<small>created 2026-10-06 · id `unpinned-torch-pulls-2-14-built-for-cuda-13-flash-attn-has-n-6ec5`</small>

## Notes

<!-- callcentre:end -->
From acereasoning-sft100k (agent acereason-sft-claude), recorded 2026-10-05; not re-verified.
