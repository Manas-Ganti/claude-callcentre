---
tags: [callcentre/domain]
---
# rl-training

> [!info] Generated: 17 entries and 1 open issues tagged `rl-training`. Back to [[INDEX|the index]].
> #rl-training #callcentre/domain

## Open issues (1)
- 🔴 [[trl-grpo-multi-turn-vlm-rollouts-are-sequential-per-prompt-4-5ea1|TRL GRPO multi-turn VLM rollouts are sequential per prompt — ~401 s/step on 8xA100, runs underpowered]] · 3 attempts

## Entries (17)
- 🆕 [[8-gpu-grpo-run-oom-killed-by-slurm-cgroup-exactly-at-checkpo-1883|8-GPU GRPO run OOM-killed by SLURM cgroup exactly at checkpoint save — --mem cap too low; add resume_from_checkpoint]]
- ✅ [[before-training-a-robot-policy-check-the-robot-can-do-the-ta-eae8|Before training a robot policy: check the robot can do the task, and run the eval sanity triad]] · used 1×
- 🆕 [[custom-grpo-lora-trainer-next-to-vllm-keeps-ooming-slice-log-af5e|Custom GRPO LoRA trainer next to vLLM keeps OOMing: slice logits before log_softmax, ref pass first, own GPU + set_device]]
- 🆕 [[deepspeed-optimizer-offload-dies-with-missingcudaexception-d-c1ef|DeepSpeed optimizer offload dies with MissingCUDAException (DeepSpeedCPUAdam needs nvcc) on ARC compute nodes — use offload_param only for LoRA]]
- 🆕 [[isaac-lab-directrlenv-calls-get-dones-before-get-rewards-ter-6780|Isaac Lab DirectRLEnv calls _get_dones before _get_rewards: terminal rewards one step late and double-counted]]
- 🆕 [[multi-turn-grpo-with-hf-generate-no-stop-condition-so-every-9156|Multi-turn GRPO with HF generate: no stop condition, so every turn runs to max_new_tokens and the 32B rambles past its action]]
- 🆕 [[rsl-rl-ppo-with-clipped-continuous-actions-entropy-coef-0-00-59ca|rsl_rl PPO with clipped continuous actions: entropy_coef 0.005 makes action std grow; use 0.001]]
- 🆕 [[sft-targets-for-a-grammar-constrained-policy-must-byte-match-ea9a|SFT targets for a grammar-constrained policy must BYTE-match what the decoder emits (key order, value types, separators)]]
- 🆕 [[slurm-job-output-persist-results-to-files-wandb-not-stdout-a-26a9|SLURM job output: persist results to files / wandb, not stdout; avoid rich-table logs]]
- 🆕 [[slurm-wall-clock-kill-skips-python-finally-and-end-of-script-148f|SLURM wall-clock kill skips Python `finally` and end-of-script requeue: trap SIGTERM via --signal=B:TERM@300]]
- 🆕 [[token-caps-truncate-silently-check-max-vs-p90-of-generated-l-7835|Token caps truncate silently — check max vs p90 of generated lengths, and keep max_new_tokens identical across distill/SFT/GRPO/eval]]
- ✅ [[transformers-5-x-renamed-trainingarguments-fields-warmup-rat-1740|transformers 5.x renamed TrainingArguments fields (warmup_ratio) — TRL SFTConfig/GRPOConfig crash after queueing]] · used 1×
- ✅ [[trl-import-fails-is-trackio-available-vllm-0-8-5-and-trl-1-9-e6e8|trl import fails 'is_trackio_available' — vLLM 0.8.5 and TRL 1.9.2 need separate conda envs; guard with an import check at job start]] · used 1×
- 🆕 [[vllm-structured-output-api-renamed-guideddecodingparams-stru-c271|vLLM structured-output API renamed (GuidedDecodingParams -> StructuredOutputsParams): detect from SamplingParams signature]]
- 🆕 [[vllm-xgrammar-ignores-json-schema-maxlength-minimum-maximum-0f65|vLLM/xgrammar ignores JSON-schema maxLength/minimum/maximum (and likely maxItems): bind with `pattern` instead]]
- 🆕 [[zero-3-still-ooms-loading-a-32b-model-on-80gb-a100s-every-ra-83eb|ZeRO-3 still OOMs loading a 32B model on 80GB A100s — every rank materialises the full model in from_pretrained]]
- 🆕 [[20-structured-output-truncation-from-inter-token-whitespace-ded5|~20% structured-output truncation from inter-token whitespace runaway: set disable_any_whitespace with backend named explicitly]]
