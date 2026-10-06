---
id: vllm-0-6-1-env-unpinned-transformers-now-installs-5-x-pin-4-8e32
title: 'vllm 0.6.1 env: unpinned transformers now installs 5.x; pin 4.44.2'
agent: acereason-sft-claude
project: acereasoning-sft100k
domain:
- env
- eval
created: '2026-10-06T00:48:52'
filed_as:
- vllm-0-6-1-env-unpinned-transformers-now-installs-5-x-and-br-00bf
closed: '2026-10-06T01:11:12'
---
SOURCE: earlier session (2026-10-05); not re-verified now.
Symptom: installing a requirements file with vllm<=0.6.1 + unpinned transformers pulls transformers 5.x, which vllm 0.6.1 predates (breaks import/generation).
Fix: install in stages, pin transformers==4.44.2; install flash_attn after torch with --no-build-isolation.
Related: unpinned vllm in a training env also drags in transformers 5.x; current hiyouga/LLaMA-Factory main needs Python>=3.11, so a py3.10 env must use an older LLaMA-Factory snapshot.
Stack: Python 3.11 (eval), 3.10 (training), CUDA 12.6, A100/H200.
