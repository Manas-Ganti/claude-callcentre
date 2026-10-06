---
id: vllm-structured-output-api-renamed-guideddecodingparams-stru-c271
kind: fix
title: 'vLLM structured-output API renamed (GuidedDecodingParams -> StructuredOutputsParams): detect from
  SamplingParams signature'
domain:
- infra
- rl-training
- vt-arc
- structured-output
- python-env
stack:
  vllm: 0.28 on cluster; code originally written for ~0.6
  cluster: VT ARC, A100
symptoms:
- 'ImportError: cannot import name ''GuidedDecodingParams'' from ''vllm.sampling_params'''
- Code written against vLLM ~0.6 (guided_decoding=GuidedDecodingParams(...)) run on a cluster with vLLM
  0.28
- Several further API-shape mismatches on vLLM output objects / config each cost a full queue cycle
root_cause: vLLM renamed guided_decoding=GuidedDecodingParams to structured_outputs=StructuredOutputsParams,
  and keeps moving config classes and output attributes between releases.
fix: 'Inspect inspect.signature(SamplingParams).parameters: if ''structured_outputs'' in it, use StructuredOutputsParams,
  elif ''guided_decoding'', use GuidedDecodingParams, else raise with the names found. Never fall back
  to unconstrained generation silently. Pass engine-level configs as plain dicts, not imported classes.
  Use getattr for non-essential output attributes (prompt, token_ids, finish_reason), keeping .text as
  a hard access. Run a cheap gpu_smoke job that probes the API before any long job.'
failed_attempts:
- 'Pinning the import name: breaks at the next rename'
- 'Importing the structured-outputs config class directly: wrong path aborts engine startup'
verify: python -c "import inspect, vllm; print(vllm.__version__, [p for p in inspect.signature(vllm.SamplingParams).parameters
  if 'guided' in p or 'structured' in p])"
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# vLLM structured-output API renamed (GuidedDecodingParams -> StructuredOutputsParams): detect from SamplingParams signature

> [!note] fix · unverified · used 0×, failed 0×
> #infra #rl-training #vt-arc #structured-output #python-env #kind/fix #status/unverified

## Symptoms
```text
ImportError: cannot import name 'GuidedDecodingParams' from 'vllm.sampling_params'
Code written against vLLM ~0.6 (guided_decoding=GuidedDecodingParams(...)) run on a cluster with vLLM 0.28
Several further API-shape mismatches on vLLM output objects / config each cost a full queue cycle
```

## Root cause
vLLM renamed guided_decoding=GuidedDecodingParams to structured_outputs=StructuredOutputsParams, and keeps moving config classes and output attributes between releases.

## Fix
Inspect inspect.signature(SamplingParams).parameters: if 'structured_outputs' in it, use StructuredOutputsParams, elif 'guided_decoding', use GuidedDecodingParams, else raise with the names found. Never fall back to unconstrained generation silently. Pass engine-level configs as plain dicts, not imported classes. Use getattr for non-essential output attributes (prompt, token_ids, finish_reason), keeping .text as a hard access. Run a cheap gpu_smoke job that probes the API before any long job.

## Failed attempts
- Pinning the import name: breaks at the next rename
- Importing the structured-outputs config class directly: wrong path aborts engine startup

## Verify
python -c "import inspect, vllm; print(vllm.__version__, [p for p in inspect.signature(vllm.SamplingParams).parameters if 'guided' in p or 'structured' in p])"

## Stack
| | |
|---|---|
| vllm | 0.28 on cluster; code originally written for ~0.6 |
| cluster | VT ARC, A100 |

<small>created 2026-10-06 · id `vllm-structured-output-api-renamed-guideddecodingparams-stru-c271`</small>

## Notes

<!-- callcentre:end -->
Sourced from healthcare_RL git history (5df1b80, 4250bea, 1db892a, 7890f6e), not reproduced this session. Related, from the same cluster: engine warmup died with 'RuntimeError: Could not find nvcc and default cuda_home='/usr/local/cuda' doesn't exist'. The FlashInfer sampler JIT-compiles at startup and the compute nodes have no toolkit. Set VLLM_USE_FLASHINFER_SAMPLER=0 before importing vllm. Also, HF_HUB_ENABLE_HF_TRANSFER is deprecated; use HF_XET_HIGH_PERFORMANCE.
