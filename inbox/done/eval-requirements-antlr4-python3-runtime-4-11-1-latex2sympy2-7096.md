---
id: eval-requirements-antlr4-python3-runtime-4-11-1-latex2sympy2-7096
title: 'eval requirements: antlr4-python3-runtime==4.11.1 + latex2sympy2==1.9.1 ResolutionImpossible'
agent: acereason-sft-claude
project: acereasoning-sft100k
domain:
- env
- eval
created: '2026-10-06T00:48:51'
filed_as:
- pip-resolutionimpossible-antlr4-python3-runtime-4-11-1-vs-la-e05a
closed: '2026-10-06T01:11:12'
---
SOURCE: earlier session (2026-10-05), recorded in repo CLAUDE.md; not re-verified now.
Symptom: pip install -r eval/requirements.txt (reds-lab/Project-Reasoning-SFT-LLM, commit 4d31bfc) fails with ResolutionImpossible: antlr4-python3-runtime==4.11.1 conflicts with latex2sympy2==1.9.1's pin.
Fix used: install latex2sympy2 with --no-deps and antlr4-python3-runtime==4.9.3 (the course main README route).
Stack: Python 3.11, vllm<=0.6.1, sympy==1.12, VT ARC.
