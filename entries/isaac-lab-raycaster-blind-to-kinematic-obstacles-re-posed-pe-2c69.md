---
id: isaac-lab-raycaster-blind-to-kinematic-obstacles-re-posed-pe-2c69
kind: fix
title: Isaac Lab RayCaster blind to kinematic obstacles re-posed per episode
domain:
- env
- isaac-sim
stack:
  isaaclab: v2.1.0
symptoms:
- Lidar/RayCaster returns max range through obstacles that are visibly present
- Obstacles are kinematic RigidObjects moved with write_root_pose_to_sim each reset
root_cause: RayCaster bakes static mesh geometry into a warp BVH at init; it doesn't track moving prims.
fix: 'RayCaster only hits static meshes (older versions: a single mesh). For procedurally re-posed obstacles,
  use an analytic lidar: exact ray-circle (or ray-box) casting in torch against the episode''s obstacle
  spec. Keep one implementation shared by numpy unit tests and torch so sim, planner and sensor agree.'
failed_attempts: []
verify: 'Smoke: compare analytic ranges vs known obstacle positions (pose error 0.000 m sim-vs-spec confirms
  kinematic poses do land).'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab RayCaster blind to kinematic obstacles re-posed per episode

> [!note] fix · unverified · used 0×, failed 0×
> #env #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
Lidar/RayCaster returns max range through obstacles that are visibly present
Obstacles are kinematic RigidObjects moved with write_root_pose_to_sim each reset
```

## Root cause
RayCaster bakes static mesh geometry into a warp BVH at init; it doesn't track moving prims.

## Fix
RayCaster only hits static meshes (older versions: a single mesh). For procedurally re-posed obstacles, use an analytic lidar: exact ray-circle (or ray-box) casting in torch against the episode's obstacle spec. Keep one implementation shared by numpy unit tests and torch so sim, planner and sensor agree.

## Verify
Smoke: compare analytic ranges vs known obstacle positions (pose error 0.000 m sim-vs-spec confirms kinematic poses do land).

## Stack
| | |
|---|---|
| isaaclab | v2.1.0 |

<small>created 2026-10-06 · id `isaac-lab-raycaster-blind-to-kinematic-obstacles-re-posed-pe-2c69`</small>

## Notes

<!-- callcentre:end -->
Reference impl: robotics-rl-payload-transport/env/lidar.py. Related: cloned colliders can't be rescaled per env, so use a fixed obstacle pool with per-slot fixed radii.
