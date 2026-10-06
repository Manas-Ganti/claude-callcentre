---
id: per-env-slopes-in-isaac-lab-from-tilted-kinematic-cuboids-wr-42a6
kind: convention
title: Per-env slopes in Isaac Lab from tilted kinematic cuboids (write_root_pose_to_sim; R_y(-theta)
  = +x uphill)
domain:
- isaac-sim
- env
stack:
  isaacsim: 4.5.0 (pip)
  isaaclab: v2.1.0
  gpu: 1x L40S
  cluster: VT ARC Falcon
symptoms:
- How to give each env its own slope angle in Isaac Lab
- Do kinematic RigidObject pose writes actually move the body
root_cause: ''
fix: Kinematic RigidObject poses written with write_root_pose_to_sim do move (0.000 m error). A tilted
  kinematic cuboid works as a per-env slope; rotation R_y(-theta) makes +x uphill.
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
# Per-env slopes in Isaac Lab from tilted kinematic cuboids (write_root_pose_to_sim; R_y(-theta) = +x uphill)

> [!success] convention · verified · used 1×, failed 0× · last verified 2026-09-26
> #isaac-sim #env #kind/convention #status/verified

## Symptoms
```text
How to give each env its own slope angle in Isaac Lab
Do kinematic RigidObject pose writes actually move the body
```

## Convention
Kinematic RigidObject poses written with write_root_pose_to_sim do move (0.000 m error). A tilted kinematic cuboid works as a per-env slope; rotation R_y(-theta) makes +x uphill.

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 (pip) |
| isaaclab | v2.1.0 |
| gpu | 1x L40S |
| cluster | VT ARC Falcon |

<small>created 2026-10-06 · id `per-env-slopes-in-isaac-lab-from-tilted-kinematic-cuboids-wr-42a6`</small>

## Notes

<!-- callcentre:end -->
From robotics-rl-payload-transport docs/ISAAC_SIM_PLAYBOOK.md (agent rtn-playbook-export); verified on ARC Falcon L40S during bring-up 2026-09-24/26.

See the open issue [[isaac-lab-wheeled-robot-carter-thrown-launched-on-tilted-kin-7af7]]: Carter is launched at 5 and 15 deg on this setup.
