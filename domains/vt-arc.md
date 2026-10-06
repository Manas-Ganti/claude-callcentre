---
tags: [callcentre/domain]
---
# vt-arc

> [!info] Generated: 19 entries and 0 open issues tagged `vt-arc`. Back to [[INDEX|the index]].
> #vt-arc #callcentre/domain

## Entries (19)
- 🆕 [[8-gpu-grpo-run-oom-killed-by-slurm-cgroup-exactly-at-checkpo-1883|8-GPU GRPO run OOM-killed by SLURM cgroup exactly at checkpoint save — --mem cap too low; add resume_from_checkpoint]]
- 🆕 [[var-x-sbatch-launcher-slurm-silently-drops-variables-the-lau-6486|`VAR=x sbatch launcher.slurm` silently drops variables the launcher doesn't read; .slurm is snapshotted at submit time]]
- 🆕 [[conda-env-silently-falls-through-to-base-inside-slurm-batch-65e5|Conda env silently falls through to base inside SLURM batch jobs on ARC (module load Miniforge3 can't see personal ~/miniconda3)]]
- 🆕 [[custom-grpo-lora-trainer-next-to-vllm-keeps-ooming-slice-log-af5e|Custom GRPO LoRA trainer next to vLLM keeps OOMing: slice logits before log_softmax, ref pass first, own GPU + set_device]]
- 🆕 [[deepspeed-optimizer-offload-dies-with-missingcudaexception-d-c1ef|DeepSpeed optimizer offload dies with MissingCUDAException (DeepSpeedCPUAdam needs nvcc) on ARC compute nodes — use offload_param only for LoRA]]
- 🆕 [[gatedrepoerror-401-in-jobs-despite-hf-auth-login-token-lives-c49d|GatedRepoError 401 in jobs despite `hf auth login` — token lives at $HF_HOME/token, jobs set a different HF_HOME]]
- 🆕 [[importing-deepspeed-on-an-arc-login-node-runtimeerror-0-acti-ee72|Importing deepspeed on an ARC login node: RuntimeError 0 active drivers (not a broken env)]]
- 🆕 [[multi-node-nccl-fails-net-ib-vendor-err-249-on-vt-arc-2-node-23b7|Multi-node NCCL fails "NET/IB ... vendor err 249" on VT ARC: 2-node request mixed DGX + standard GPU node]]
- 🆕 [[nccl-bootstrap-no-socket-interface-found-on-vt-arc-h200-node-92ad|NCCL "Bootstrap : no socket interface found" on VT ARC H200 nodes — hardcoded NCCL_SOCKET_IFNAME=ib0]]
- 🆕 [[sbatch-job-s-source-activate-env-succeeds-but-python-stays-t-e65c|sbatch job's `source activate <env>` succeeds but python stays the Miniconda module's base 3.13 (VT ARC)]]
- 🆕 [[slurm-gpu-job-completed-in-2-seconds-exit-0-empty-err-conda-c1fe|SLURM GPU job "COMPLETED" in 2 seconds, exit 0, empty .err — conda env's python binary was a 0-byte file]]
- 🆕 [[slurm-wall-clock-kill-skips-python-finally-and-end-of-script-148f|SLURM wall-clock kill skips Python `finally` and end-of-script requeue: trap SIGTERM via --signal=B:TERM@300]]
- ✅ [[trl-import-fails-is-trackio-available-vllm-0-8-5-and-trl-1-9-e6e8|trl import fails 'is_trackio_available' — vLLM 0.8.5 and TRL 1.9.2 need separate conda envs; guard with an import check at job start]] · used 1×
- 🆕 [[unpinned-torch-pulls-2-14-built-for-cuda-13-flash-attn-has-n-6ec5|Unpinned torch pulls 2.14 built for CUDA 13: flash-attn has no wheel and won't build against CUDA 12.6]]
- 🆕 [[vllm-structured-output-api-renamed-guideddecodingparams-stru-c271|vLLM structured-output API renamed (GuidedDecodingParams -> StructuredOutputsParams): detect from SamplingParams signature]]
- 🆕 [[vs-code-remote-terminal-on-vt-arc-corrupts-pasted-commands-b-9d60|VS Code remote terminal on VT ARC corrupts pasted commands (bracketed-paste markers)]]
- 🆕 [[vt-arc-job-environment-export-hf-home-and-wandb-dir-explicit-cd71|VT ARC job environment: export HF_HOME and WANDB_DIR explicitly on every submit]]
- 🆕 [[vt-arc-slurm-scheduling-mem-0-blocks-backfill-use-tc-normal-b1ca|VT ARC SLURM scheduling: --mem=0 blocks backfill, use tc_*_normal_short QOS, never preemptable, account/mail flags]]
- 🆕 [[zero-3-still-ooms-loading-a-32b-model-on-80gb-a100s-every-ra-83eb|ZeRO-3 still OOMs loading a 32B model on 80GB A100s — every rank materialises the full model in from_pretrained]]
