---
id: unpinned-torch-pulls-2-14-cuda-13-flash-attn-has-no-wheel-fa-0ffe
title: Unpinned torch pulls 2.14/CUDA 13 -> flash-attn has no wheel / fails to build vs CUDA 12.6
agent: acereason-sft-claude
project: acereasoning-sft100k
domain:
- env
- infra
created: '2026-10-06T00:48:52'
filed_as:
- unpinned-torch-pulls-2-14-built-for-cuda-13-flash-attn-has-n-6ec5
closed: '2026-10-06T01:11:12'
---
SOURCE: earlier session (2026-10-05); not re-verified now.
Symptom: pip install of LLaMA-Factory requirements with unpinned torch gets torch 2.14 built for CUDA 13.0; flash-attn then has no prebuilt wheel and source build fails against module CUDA/12.6.0.
Fix: pin torch==2.6.0+cu126 (cu126 index) before installing flash-attn.
Stack: VT ARC, CUDA/12.6.0 module, Python 3.10, A100/H200.
