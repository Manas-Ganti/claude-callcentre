---
id: multi-node-nccl-fails-net-ib-vendor-err-249-on-vt-arc-2-node-23b7
kind: fix
title: 'Multi-node NCCL fails "NET/IB ... vendor err 249" on VT ARC: 2-node request mixed DGX + standard
  GPU node'
domain:
- infra
- distributed
- vt-arc
stack:
  cluster: VT ARC
  partition: a100_normal_q
  gpus: 8xA100-80GB per node
  workload: TRL GRPO, DeepSpeed ZeRO-2, Qwen2.5-VL-32B LoRA
symptoms:
- NET/IB ... vendor err 249 (Recv)
- All 16 ranks load the model and build the trainer, then the first BROADCAST fails; the remaining ranks
  sit in a 600s NCCL watchdog timeout before the job aborts
- Allocation was tc-dgx001 + tc-gpu002 on a100_normal_q
root_cause: 'ARC''s a100_normal_q is heterogeneous: tc-dgx[001-010] (DGX) and tc-gpu[001-004] (standard)
  nodes, whose InfiniBand HCAs cannot reach each other. SLURM happily gives a --nodes=2 job one of each.
  Invisible until the first collective.'
fix: Run on ONE 8-GPU node (#SBATCH --nodes=1) so every collective stays on NVLink. If 2 nodes are truly
  needed, pin a single node type with --constraint (or --nodelist within tc-dgx*), and have NCCL_IB_DISABLE=1
  ready as a TCP fallback.
failed_attempts:
- Default --nodes=2 with no constraint — reproducibly fails at the first collective whenever the scheduler
  mixes node types
verify: squeue -j <id> -o "%N" — node list must be all tc-dgx* or all tc-gpu*; or confirm --nodes=1 in
  the launcher
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Multi-node NCCL fails "NET/IB ... vendor err 249" on VT ARC: 2-node request mixed DGX + standard GPU node

> [!note] fix · unverified · used 0×, failed 0×
> #infra #distributed #vt-arc #kind/fix #status/unverified

## Symptoms
```text
NET/IB ... vendor err 249 (Recv)
All 16 ranks load the model and build the trainer, then the first BROADCAST fails; the remaining ranks sit in a 600s NCCL watchdog timeout before the job aborts
Allocation was tc-dgx001 + tc-gpu002 on a100_normal_q
```

## Root cause
ARC's a100_normal_q is heterogeneous: tc-dgx[001-010] (DGX) and tc-gpu[001-004] (standard) nodes, whose InfiniBand HCAs cannot reach each other. SLURM happily gives a --nodes=2 job one of each. Invisible until the first collective.

## Fix
Run on ONE 8-GPU node (#SBATCH --nodes=1) so every collective stays on NVLink. If 2 nodes are truly needed, pin a single node type with --constraint (or --nodelist within tc-dgx*), and have NCCL_IB_DISABLE=1 ready as a TCP fallback.

## Failed attempts
- Default --nodes=2 with no constraint — reproducibly fails at the first collective whenever the scheduler mixes node types

## Verify
squeue -j \<id> -o "%N" — node list must be all tc-dgx* or all tc-gpu*; or confirm --nodes=1 in the launcher

## Stack
| | |
|---|---|
| cluster | VT ARC |
| partition | a100_normal_q |
| gpus | 8xA100-80GB per node |
| workload | TRL GRPO, DeepSpeed ZeRO-2, Qwen2.5-VL-32B LoRA |

<small>created 2026-10-06 · id `multi-node-nccl-fails-net-ib-vendor-err-249-on-vt-arc-2-node-23b7`</small>

## Notes

<!-- callcentre:end -->
Source commit 6155f22. One node also halves the allocation, which queues much faster — 8-GPU slots on ARC are often days deep.
