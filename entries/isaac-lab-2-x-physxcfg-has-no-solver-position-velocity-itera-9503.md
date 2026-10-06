---
id: isaac-lab-2-x-physxcfg-has-no-solver-position-velocity-itera-9503
kind: fix
title: 'Isaac Lab 2.x: PhysxCfg has no solver_position/velocity_iteration_count (TypeError)'
domain:
- env
- isaac-sim
stack:
  isaaclab: v2.1.0
  isaacsim: 4.5.0
symptoms:
- 'TypeError: PhysxCfg.__init__() got an unexpected keyword argument ''solver_position_iteration_count'''
- same for solver_velocity_iteration_count when building SimulationCfg(physx=PhysxCfg(...))
root_cause: In Isaac Lab 2.x solver iteration counts are per-actor properties, not scene-wide PhysX settings
  (older Orbit/Isaac Gym examples put them on the scene).
fix: 'Move the iteration counts to the robot: robot_cfg.spawn.articulation_props = sim_utils.ArticulationRootPropertiesCfg(solver_position_iteration_count=...,
  solver_velocity_iteration_count=...). PhysxCfg keeps only min/max clamps and gpu_* buffer sizes. Validate
  YAML keys against PhysxCfg.__dataclass_fields__ before constructing.'
failed_attempts: []
verify: python -c "from isaaclab.sim import PhysxCfg; print([f for f in PhysxCfg.__dataclass_fields__
  if 'iteration' in f])"  (only min/max clamps)
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab 2.x: PhysxCfg has no solver_position/velocity_iteration_count (TypeError)

> [!note] fix · unverified · used 0×, failed 0×
> #env #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
TypeError: PhysxCfg.__init__() got an unexpected keyword argument 'solver_position_iteration_count'
same for solver_velocity_iteration_count when building SimulationCfg(physx=PhysxCfg(...))
```

## Root cause
In Isaac Lab 2.x solver iteration counts are per-actor properties, not scene-wide PhysX settings (older Orbit/Isaac Gym examples put them on the scene).

## Fix
Move the iteration counts to the robot: robot_cfg.spawn.articulation_props = sim_utils.ArticulationRootPropertiesCfg(solver_position_iteration_count=..., solver_velocity_iteration_count=...). PhysxCfg keeps only min/max clamps and gpu_* buffer sizes. Validate YAML keys against PhysxCfg.__dataclass_fields__ before constructing.

## Verify
python -c "from isaaclab.sim import PhysxCfg; print([f for f in PhysxCfg.__dataclass_fields__ if 'iteration' in f])"  (only min/max clamps)

## Stack
| | |
|---|---|
| isaaclab | v2.1.0 |
| isaacsim | 4.5.0 |

<small>created 2026-10-06 · id `isaac-lab-2-x-physxcfg-has-no-solver-position-velocity-itera-9503`</small>

<!-- callcentre:end -->
