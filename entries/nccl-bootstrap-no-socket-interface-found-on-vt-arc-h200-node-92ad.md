---
id: nccl-bootstrap-no-socket-interface-found-on-vt-arc-h200-node-92ad
kind: fix
title: 'NCCL "Bootstrap : no socket interface found" on VT ARC H200 nodes — hardcoded NCCL_SOCKET_IFNAME=ib0'
domain:
- infra
- distributed
- vt-arc
stack:
  cluster: VT ARC (Tinkercliffs)
  partition: h200_normal_q (tc-xe[001-006], 8xH200) vs a100_normal_q
  deepspeed: 0.19.5
  nodes: 1 node, 8 GPUs
symptoms:
- 'ncclInternalError: Internal check failed.'
- 'Last error: Bootstrap : no socket interface found'
- Multi-GPU DeepSpeed job on h200_normal_q (tc-xe*) dies at DeepSpeed init ~10 min in, after every rank
  has loaded its weights (62 GB each for Qwen2.5-VL-32B)
root_cause: NCCL bootstrap is TCP even when InfiniBand carries the data, so NCCL_SOCKET_IFNAME must name
  an interface that is UP and has an IPv4 address. ib0 is addressed on the A100 nodes but on the H200
  nodes (tc-xe*) it EXISTS in /sys/class/net with NO IPv4 address.
fix: "Don't hardcode the interface. In the job env script, pick an interface that actually has an IPv4\
  \ address:\n  _nccl_pick(){ want=$1; if [ -n \"$want\" ] && ip -o -4 addr show dev \"$want\" 2>/dev/null\
  \ | grep -q ' inet '; then echo $want; return 0; fi\n    for n in $(ip -o -4 addr show | awk '{print\
  \ $2}' | sort -u); do case $n in lo|docker*|virbr*|veth*|br-*|cni*|flannel*) continue;; esac; echo $n;\
  \ return 0; done; return 1; }\n  if i=$(_nccl_pick \"${NCCL_SOCKET_IFNAME:-ib0}\"); then export NCCL_SOCKET_IFNAME=$i;\
  \ else unset NCCL_SOCKET_IFNAME; fi\nOn H200 this resolves to eth0 (NCCL_SOCKET_IFNAME=eth0 also works\
  \ explicitly); on A100 leave it to the probe. Log the choice."
failed_attempts:
- Checking that /sys/class/net/ib0 exists before using it — passes on tc-xe003 (the device is present)
  and NCCL fails identically, because it has no IPv4 address
verify: 'srun --jobid=<id> --overlap ip -o -4 addr show   # the chosen NCCL_SOCKET_IFNAME must appear
  with an inet address; job log should print [arc_env] NCCL_SOCKET_IFNAME=<name>'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# NCCL "Bootstrap : no socket interface found" on VT ARC H200 nodes — hardcoded NCCL_SOCKET_IFNAME=ib0

> [!note] fix · unverified · used 0×, failed 0×
> #infra #distributed #vt-arc #kind/fix #status/unverified

## Symptoms
```text
ncclInternalError: Internal check failed.
Last error: Bootstrap : no socket interface found
Multi-GPU DeepSpeed job on h200_normal_q (tc-xe*) dies at DeepSpeed init ~10 min in, after every rank has loaded its weights (62 GB each for Qwen2.5-VL-32B)
```

## Root cause
NCCL bootstrap is TCP even when InfiniBand carries the data, so NCCL_SOCKET_IFNAME must name an interface that is UP and has an IPv4 address. ib0 is addressed on the A100 nodes but on the H200 nodes (tc-xe*) it EXISTS in /sys/class/net with NO IPv4 address.

## Fix
Don't hardcode the interface. In the job env script, pick an interface that actually has an IPv4 address:
  _nccl_pick(){ want=\$1; if [ -n "\$want" ] && ip -o -4 addr show dev "\$want" 2>/dev/null | grep -q ' inet '; then echo \$want; return 0; fi
    for n in \$(ip -o -4 addr show | awk '{print \$2}' | sort -u); do case \$n in lo|docker*|virbr*|veth*|br-*|cni*|flannel*) continue;; esac; echo \$n; return 0; done; return 1; }
  if i=\$(_nccl_pick "\${NCCL_SOCKET_IFNAME:-ib0}"); then export NCCL_SOCKET_IFNAME=\$i; else unset NCCL_SOCKET_IFNAME; fi
On H200 this resolves to eth0 (NCCL_SOCKET_IFNAME=eth0 also works explicitly); on A100 leave it to the probe. Log the choice.

## Failed attempts
- Checking that /sys/class/net/ib0 exists before using it — passes on tc-xe003 (the device is present) and NCCL fails identically, because it has no IPv4 address

## Verify
srun --jobid=\<id> --overlap ip -o -4 addr show   # the chosen NCCL_SOCKET_IFNAME must appear with an inet address; job log should print [arc_env] NCCL_SOCKET_IFNAME=\<name>

## Stack
| | |
|---|---|
| cluster | VT ARC (Tinkercliffs) |
| partition | h200_normal_q (tc-xe[001-006], 8xH200) vs a100_normal_q |
| deepspeed | 0.19.5 |
| nodes | 1 node, 8 GPUs |

<small>created 2026-10-06 · id `nccl-bootstrap-no-socket-interface-found-on-vt-arc-h200-node-92ad`</small>

## Notes

<!-- callcentre:end -->
Source: VLM-RL-aicontent-detection commits 17c95d6, 1b827f1; docs/arc_runbook.md 'NCCL: ib0 is an A100 name'. General lesson: anything in a job env script that names hardware is suspect when moving between partitions.
