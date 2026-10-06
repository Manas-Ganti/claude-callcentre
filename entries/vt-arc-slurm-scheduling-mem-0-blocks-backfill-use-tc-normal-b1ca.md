---
id: vt-arc-slurm-scheduling-mem-0-blocks-backfill-use-tc-normal-b1ca
kind: convention
title: 'VT ARC SLURM scheduling: --mem=0 blocks backfill, use tc_*_normal_short QOS, never preemptable,
  account/mail flags'
domain:
- infra
- vt-arc
- slurm
stack:
  cluster: VT ARC Tinkercliffs
  a100_normal_q: 14 nodes tc-dgx[001-010], tc-gpu[001-004], 8xA100-80GB
  h200_normal_q: 6 nodes tc-xe[001-006], 8xH200-141GB
symptoms:
- Small 1-GPU jobs pend for a full day with reason Priority/Resources
- '#SBATCH --mem=0 in launcher headers'
- SLURM mail never arrives with only --mail-user
root_cause: Partitions have MaxTime=UNLIMITED so backfill can't plan around running jobs; being small,
  short and in the high-priority QOS is the only reliable way through.
fix: "Known-good small-job submit (1xH200 probe):\n  sbatch --account=<alloc> --partition=h200_normal_q\
  \ --qos=tc_h200_normal_short --gres=gpu:h200:1 --cpus-per-task=8 --mem=96G --time=00:30:00 --mail-type=BEGIN,END,FAIL,TIME_LIMIT_80\
  \ --mail-user=<you>@vt.edu script.slurm\nRules: (1) never --mem=0 on a partial-node job — it means ALL\
  \ node memory and can only start on an idle node; DO use --mem=0 on full 8-GPU jobs. (2) QOS tc_h200_normal_short\
  \ = priority 2000, MaxWall 1 day (highest on cluster; moved priority 1330->2312); _base = 1000/7d, _long\
  \ = 500/14d. A100: tc_a100_normal_short 1500/1d. Put everything <24h in short. (3) Don't fall back to\
  \ *_preemptable_q — normal_q is PriorityTier 16 PreemptMode OFF, preemptable is tier 8 and evicted by\
  \ normal. (4) #SBATCH lines cannot read env vars; pass --partition/--account on the CLI. (5) --mail-type\
  \ is required; --mail-user alone sends nothing; check Outlook Junk. (6) sinfo 'mix' != free GPUs — check\
  \ AllocTRES gres/gpu. (7) Prefer --nodes=1: a100_normal_q mixes tc-dgx and tc-gpu nodes whose IB can't\
  \ talk."
failed_attempts: []
verify: sacctmgr show qos format=name%28,priority,maxwall ; squeue -j <id> -o "%.10i %.9T %.11M %.22R
  %N" ; scontrol show config | grep -i mail
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# VT ARC SLURM scheduling: --mem=0 blocks backfill, use tc_*_normal_short QOS, never preemptable, account/mail flags

> [!note] convention · unverified · used 0×, failed 0×
> #infra #vt-arc #slurm #kind/convention #status/unverified

## Symptoms
```text
Small 1-GPU jobs pend for a full day with reason Priority/Resources
#SBATCH --mem=0 in launcher headers
SLURM mail never arrives with only --mail-user
```

## Root cause
Partitions have MaxTime=UNLIMITED so backfill can't plan around running jobs; being small, short and in the high-priority QOS is the only reliable way through.

## Convention
Known-good small-job submit (1xH200 probe):
  sbatch --account=\<alloc> --partition=h200_normal_q --qos=tc_h200_normal_short --gres=gpu:h200:1 --cpus-per-task=8 --mem=96G --time=00:30:00 --mail-type=BEGIN,END,FAIL,TIME_LIMIT_80 --mail-user=\<you>@vt.edu script.slurm
Rules: (1) never --mem=0 on a partial-node job — it means ALL node memory and can only start on an idle node; DO use --mem=0 on full 8-GPU jobs. (2) QOS tc_h200_normal_short = priority 2000, MaxWall 1 day (highest on cluster; moved priority 1330->2312); _base = 1000/7d, _long = 500/14d. A100: tc_a100_normal_short 1500/1d. Put everything \<24h in short. (3) Don't fall back to *_preemptable_q — normal_q is PriorityTier 16 PreemptMode OFF, preemptable is tier 8 and evicted by normal. (4) \#SBATCH lines cannot read env vars; pass --partition/--account on the CLI. (5) --mail-type is required; --mail-user alone sends nothing; check Outlook Junk. (6) sinfo 'mix' != free GPUs — check AllocTRES gres/gpu. (7) Prefer --nodes=1: a100_normal_q mixes tc-dgx and tc-gpu nodes whose IB can't talk.

## Verify
sacctmgr show qos format=name%28,priority,maxwall ; squeue -j \<id> -o "%.10i %.9T %.11M %.22R %N" ; scontrol show config | grep -i mail

## Stack
| | |
|---|---|
| cluster | VT ARC Tinkercliffs |
| a100_normal_q | 14 nodes tc-dgx[001-010], tc-gpu[001-004], 8xA100-80GB |
| h200_normal_q | 6 nodes tc-xe[001-006], 8xH200-141GB |

<small>created 2026-10-06 · id `vt-arc-slurm-scheduling-mem-0-blocks-backfill-use-tc-normal-b1ca`</small>

## Notes

<!-- callcentre:end -->
H200 141 GB fits Qwen2.5-VL-32B (~66 GB) on ONE GPU for vLLM at max_model_len 16384 / gpu_memory_utilization 0.90 — set TP equal to the GPU count when requesting a partial node. Source: docs/arc_runbook.md §2, §5; commits aff112f, fb11a31.
