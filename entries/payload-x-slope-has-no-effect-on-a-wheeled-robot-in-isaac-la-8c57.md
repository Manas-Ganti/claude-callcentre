---
id: payload-x-slope-has-no-effect-on-a-wheeled-robot-in-isaac-la-8c57
kind: fix
title: 'Payload x slope has no effect on a wheeled robot in Isaac Lab: USD drive maxForce=inf; set effort_limit_sim'
domain:
- isaac-sim
- env
stack:
  isaacsim: 4.5.0 (pip)
  isaaclab: v2.1.0
  gpu: 1x L40S
  cluster: VT ARC Falcon
symptoms:
- Payload mass and slope angle don't change wheeled-robot performance
root_cause: The USD's default drive maxForce is inf, so implicit actuators have unlimited torque.
fix: Set effort_limit_sim on the actuator config (the physics torque cap for implicit actuators; velocity_limit
  is ignored, effort_limit is a deprecated alias). Mark physically infeasible OOD cells and exclude them
  from degradation metrics.
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
# Payload x slope has no effect on a wheeled robot in Isaac Lab: USD drive maxForce=inf; set effort_limit_sim

> [!success] fix · verified · used 1×, failed 0× · last verified 2026-09-26
> #isaac-sim #env #kind/fix #status/verified

## Symptoms
```text
Payload mass and slope angle don't change wheeled-robot performance
```

## Root cause
The USD's default drive maxForce is inf, so implicit actuators have unlimited torque.

## Fix
Set effort_limit_sim on the actuator config (the physics torque cap for implicit actuators; velocity_limit is ignored, effort_limit is a deprecated alias). Mark physically infeasible OOD cells and exclude them from degradation metrics.

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 (pip) |
| isaaclab | v2.1.0 |
| gpu | 1x L40S |
| cluster | VT ARC Falcon |

<small>created 2026-10-06 · id `payload-x-slope-has-no-effect-on-a-wheeled-robot-in-isaac-la-8c57`</small>

## Notes

<!-- callcentre:end -->
From robotics-rl-payload-transport docs/ISAAC_SIM_PLAYBOOK.md (agent rtn-playbook-export); verified on ARC Falcon L40S during bring-up 2026-09-24/26.
