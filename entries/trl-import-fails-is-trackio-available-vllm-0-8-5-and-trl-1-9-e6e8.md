---
id: trl-import-fails-is-trackio-available-vllm-0-8-5-and-trl-1-9-e6e8
kind: fix
title: trl import fails 'is_trackio_available' — vLLM 0.8.5 and TRL 1.9.2 need separate conda envs; guard
  with an import check at job start
domain:
- infra
- python-env
- rl-training
- vt-arc
stack:
  vllm: 0.8.5
  transformers_infer: 4.51.3
  transformers_train: 5.15.0
  trl: 1.9.2
  torch: 2.6.0+cu124
symptoms:
- 'ImportError: cannot import name ''is_trackio_available'' from ''transformers'''
- 'RuntimeError: Failed to import trl.trainer.sft_trainer'
- Happens ~20 min into an 8-GPU SFT job after the model loads
root_cause: The inference env (vLLM 0.8.5) pins transformers 4.51.3; trl 1.9.2 requires transformers>=4.56.2.
  The SFT job was submitted with the inference env. Env activation succeeded (all envs import PIL etc.),
  so nothing caught it early.
fix: 'Keep two envs and never unify them: inference/vLLM env (vllm 0.8.5, transformers 4.51.3, torch 2.6.0+cu124)
  and training env (trl 1.9.2, transformers 5.15.0, peft 0.20.0, accelerate 1.14.0, deepspeed 0.19.5).
  Each launcher asserts its stage''s imports in seconds at job start, e.g. "$PY" -c ''import trl, peft''
  (SFT/GRPO) or ''import vllm'' (eval/distill), exiting with the env to resubmit with.'
failed_attempts:
- Asserting only that sys.executable is inside $CONDA_ENV and PIL imports — true in every env, so it can't
  catch the wrong env
- Unifying the envs — vLLM's transformers pin and TRL's minimum cannot coexist
verify: '$ENV/bin/python -c "from transformers import TrainerCallback, AutoProcessor, AutoModelForImageTextToText;
  from transformers.integrations.deepspeed import is_deepspeed_zero3_enabled; from trl import SFTConfig,
  SFTTrainer; from peft import LoraConfig; print(''ALL PRESENT'')"  (don''t import deepspeed on a login
  node: Triton raises ''RuntimeError: 0 active drivers'' without a GPU — that''s the node, not the env)'
status: verified
uses: 1
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: '2026-10-06'
outcome_notes:
- '2026-10-06 OK: Independent confirmation from healthcare_RL pyproject.toml/commit 1dad516, not re-run
  this session: vLLM pins transformers ~4.51 and TRL needs >=4.56, so the repo uses two venvs (.venv for
  vLLM, .venv-train for TRL). Same ImportError ''is_trackio_available''. Gotcha: gitignore the second
  venv too. Also, on ARC, python3 -m venv can exit 0 without pip (ensurepip stripped); repair with python
  -m ensurepip --upgrade and install via python -m pip.'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# trl import fails 'is_trackio_available' — vLLM 0.8.5 and TRL 1.9.2 need separate conda envs; guard with an import check at job start

> [!success] fix · verified · used 1×, failed 0× · last verified 2026-10-06
> #infra #python-env #rl-training #vt-arc #kind/fix #status/verified

## Symptoms
```text
ImportError: cannot import name 'is_trackio_available' from 'transformers'
RuntimeError: Failed to import trl.trainer.sft_trainer
Happens ~20 min into an 8-GPU SFT job after the model loads
```

## Root cause
The inference env (vLLM 0.8.5) pins transformers 4.51.3; trl 1.9.2 requires transformers>=4.56.2. The SFT job was submitted with the inference env. Env activation succeeded (all envs import PIL etc.), so nothing caught it early.

## Fix
Keep two envs and never unify them: inference/vLLM env (vllm 0.8.5, transformers 4.51.3, torch 2.6.0+cu124) and training env (trl 1.9.2, transformers 5.15.0, peft 0.20.0, accelerate 1.14.0, deepspeed 0.19.5). Each launcher asserts its stage's imports in seconds at job start, e.g. "\$PY" -c 'import trl, peft' (SFT/GRPO) or 'import vllm' (eval/distill), exiting with the env to resubmit with.

## Failed attempts
- Asserting only that sys.executable is inside \$CONDA_ENV and PIL imports — true in every env, so it can't catch the wrong env
- Unifying the envs — vLLM's transformers pin and TRL's minimum cannot coexist

## Verify
\$ENV/bin/python -c "from transformers import TrainerCallback, AutoProcessor, AutoModelForImageTextToText; from transformers.integrations.deepspeed import is_deepspeed_zero3_enabled; from trl import SFTConfig, SFTTrainer; from peft import LoraConfig; print('ALL PRESENT')"  (don't import deepspeed on a login node: Triton raises 'RuntimeError: 0 active drivers' without a GPU — that's the node, not the env)

## Stack
| | |
|---|---|
| vllm | 0.8.5 |
| transformers_infer | 4.51.3 |
| transformers_train | 5.15.0 |
| trl | 1.9.2 |
| torch | 2.6.0+cu124 |

## Outcome reports
- 2026-10-06 OK: Independent confirmation from healthcare_RL pyproject.toml/commit 1dad516, not re-run this session: vLLM pins transformers ~4.51 and TRL needs >=4.56, so the repo uses two venvs (.venv for vLLM, .venv-train for TRL). Same ImportError 'is_trackio_available'. Gotcha: gitignore the second venv too. Also, on ARC, python3 -m venv can exit 0 without pip (ensurepip stripped); repair with python -m ensurepip --upgrade and install via python -m pip.

<small>created 2026-10-06 · id `trl-import-fails-is-trackio-available-vllm-0-8-5-and-trl-1-9-e6e8`</small>

## Notes

<!-- callcentre:end -->
Source commits 4ba4224, 4c94a2a. pip check in the vLLM env reports 'trl 1.9.2 requires transformers>=4.56.2' — harmless there if the vLLM path never imports trl. huggingface-hub 1.x is rejected by transformers 4.51 (<1.0): pin the leaf (huggingface-hub 0.36.2) rather than bumping transformers.
