---
id: robots-drive-off-floating-ground-patches-or-tip-at-the-edge-09cd
kind: fix
title: Robots drive off floating ground patches or tip at the edge in Isaac Lab
domain:
- isaac-sim
- env
stack:
  isaacsim: 4.5.0 (pip)
  isaaclab: v2.1.0
  gpu: 1x L40S
  cluster: VT ARC Falcon
symptoms:
- Robot drives off the edge of a floating ground patch
- Caster overhangs the edge and the robot tips (7/64 envs every run)
root_cause: ''
fix: Terminate on out-of-bounds. Sample start, goal and A* paths inside an edge band of one robot radius.
failed_attempts: []
verify: ''
status: verified
uses: 1
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: '2026-09-26'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Robots drive off floating ground patches or tip at the edge in Isaac Lab

> [!success] fix · verified · used 1×, failed 0× · last verified 2026-09-26
> #isaac-sim #env #kind/fix #status/verified

## Symptoms
```text
Robot drives off the edge of a floating ground patch
Caster overhangs the edge and the robot tips (7/64 envs every run)
```

## Fix
Terminate on out-of-bounds. Sample start, goal and A* paths inside an edge band of one robot radius.

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 (pip) |
| isaaclab | v2.1.0 |
| gpu | 1x L40S |
| cluster | VT ARC Falcon |

<small>created 2026-10-06 · id `robots-drive-off-floating-ground-patches-or-tip-at-the-edge-09cd`</small>

## Notes

<!-- callcentre:end -->
From robotics-rl-payload-transport docs/ISAAC_SIM_PLAYBOOK.md (agent rtn-playbook-export); verified on ARC Falcon L40S during bring-up 2026-09-24/26.
