---
id: isaac-lab-domain-randomization-of-friction-mass-via-physx-vi-45d8
kind: fix
title: 'Isaac Lab domain randomization of friction/mass via PhysX views: writes misassign envs or don''t
  affect dynamics'
domain:
- env
- isaac-sim
stack:
  isaaclab: v2.1.0
  isaacsim: 4.5.0
symptoms:
- Randomized friction/mass has no measurable effect, or the wrong envs get the values
- Mass changed but robot dynamics barely change (inertia stale)
root_cause: The view APIs expect full-size CPU tensors indexed by env ids; partial tensors are misaligned.
  PhysX treats mass and inertia independently.
fix: 'For root_physx_view.set_material_properties / set_masses / set_inertias: get the FULL (N, ...) tensor,
  on CPU, modify the reset rows, write back the full tensor with indices (same pattern as Isaac Lab''s
  built-in randomizers). Write inertia alongside mass -- PhysX does not rescale inertia. Confirm by reading
  back with root_physx_view.get_* (never trust your own buffers).'
failed_attempts: []
verify: After reset, read get_material_properties()/get_masses() and compare to sampled values per env.
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab domain randomization of friction/mass via PhysX views: writes misassign envs or don't affect dynamics

> [!note] fix · unverified · used 0×, failed 0×
> #env #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
Randomized friction/mass has no measurable effect, or the wrong envs get the values
Mass changed but robot dynamics barely change (inertia stale)
```

## Root cause
The view APIs expect full-size CPU tensors indexed by env ids; partial tensors are misaligned. PhysX treats mass and inertia independently.

## Fix
For root_physx_view.set_material_properties / set_masses / set_inertias: get the FULL (N, ...) tensor, on CPU, modify the reset rows, write back the full tensor with indices (same pattern as Isaac Lab's built-in randomizers). Write inertia alongside mass -- PhysX does not rescale inertia. Confirm by reading back with root_physx_view.get_* (never trust your own buffers).

## Verify
After reset, read get_material_properties()/get_masses() and compare to sampled values per env.

## Stack
| | |
|---|---|
| isaaclab | v2.1.0 |
| isaacsim | 4.5.0 |

<small>created 2026-10-06 · id `isaac-lab-domain-randomization-of-friction-mass-via-physx-vi-45d8`</small>

<!-- callcentre:end -->
