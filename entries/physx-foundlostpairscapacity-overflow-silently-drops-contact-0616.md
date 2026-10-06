---
id: physx-foundlostpairscapacity-overflow-silently-drops-contact-0616
kind: fix
title: PhysX foundLostPairsCapacity overflow silently drops contacts at scale (Isaac Lab, 2048 envs)
domain:
- env
- isaac-sim
stack:
  isaaclab: v2.1.0
  isaacsim: 4.5.0
  gpu: L40S
  num_envs: 2048
symptoms:
- 'PhysX error: ... increase ... foundLostPairsCapacity to 2312192, otherwise the simulation will miss
  interactions'
- Run completes with no exception; contacts silently missed
root_cause: Default GPU pair buffer sized for smaller scenes; 2048 envs x 48 kinematic obstacles exceeds
  it.
fix: SimulationCfg.physx = PhysxCfg(gpu_found_lost_pairs_capacity=4194304) (round up the logged value).
  Grep every job log for 'PhysX error' at job end since PhysX errors are log lines, not exceptions.
failed_attempts: []
verify: grep -c "PhysX error" logs/slurm/<job>.out   -> 0
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# PhysX foundLostPairsCapacity overflow silently drops contacts at scale (Isaac Lab, 2048 envs)

> [!note] fix · unverified · used 0×, failed 0×
> #env #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
PhysX error: ... increase ... foundLostPairsCapacity to 2312192, otherwise the simulation will miss interactions
Run completes with no exception; contacts silently missed
```

## Root cause
Default GPU pair buffer sized for smaller scenes; 2048 envs x 48 kinematic obstacles exceeds it.

## Fix
SimulationCfg.physx = PhysxCfg(gpu_found_lost_pairs_capacity=4194304) (round up the logged value). Grep every job log for 'PhysX error' at job end since PhysX errors are log lines, not exceptions.

## Verify
grep -c "PhysX error" logs/slurm/\<job>.out   -> 0

## Stack
| | |
|---|---|
| isaaclab | v2.1.0 |
| isaacsim | 4.5.0 |
| gpu | L40S |
| num_envs | 2048 |

<small>created 2026-10-06 · id `physx-foundlostpairscapacity-overflow-silently-drops-contact-0616`</small>

<!-- callcentre:end -->
