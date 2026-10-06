---
id: isaac-lab-contactsensor-wildcard-filter-fails-silently-net-f-b424
kind: fix
title: 'Isaac Lab ContactSensor: wildcard filter fails silently; net_forces_w flags ground contact as
  collision'
domain:
- env
- isaac-sim
stack:
  isaaclab: v2.1.0
  isaacsim: 4.5.0
  gpu: L40S
symptoms:
- 'At sim start: `Filter pattern ... expected 64, found 3072` (64 envs x 48 obstacles) logged as an error,
  NOT raised'
- force_matrix_w stays empty/zero -> collision sensor dead, no collisions ever detected
- 'Using net_forces_w instead: every step flagged as a collision (first-step terminations)'
root_cause: filter_prim_paths_expr is resolved per-expression with the expectation of one match per env;
  a wildcard matching N prims per env mismatches the count and the filter is dropped with only a log line.
fix: '1) spawn cfg: activate_contact_sensors=True. 2) filter_prim_paths_expr must be a list with ONE expression
  per filtered prim, each matching exactly one prim per env (e.g. ["{ENV_REGEX_NS}/Obstacle_0", ..., "{ENV_REGEX_NS}/Obstacle_47"]),
  not one wildcard matching all obstacles. 3) Read obstacle contacts from data.force_matrix_w, never net_forces_w
  (includes ground support force).'
failed_attempts:
- Wildcard '{ENV_REGEX_NS}/Obstacle_.*' in filter_prim_paths_expr
- net_forces_w magnitude threshold as collision signal
verify: 'Smoke test: drive robots into obstacles and assert force_matrix_w nonzero; assert zero collision
  terminations on step 1; grep job log for ''Filter pattern''.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab ContactSensor: wildcard filter fails silently; net_forces_w flags ground contact as collision

> [!note] fix · unverified · used 0×, failed 0×
> #env #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
At sim start: `Filter pattern ... expected 64, found 3072` (64 envs x 48 obstacles) logged as an error, NOT raised
force_matrix_w stays empty/zero -> collision sensor dead, no collisions ever detected
Using net_forces_w instead: every step flagged as a collision (first-step terminations)
```

## Root cause
filter_prim_paths_expr is resolved per-expression with the expectation of one match per env; a wildcard matching N prims per env mismatches the count and the filter is dropped with only a log line.

## Fix
1) spawn cfg: activate_contact_sensors=True. 2) filter_prim_paths_expr must be a list with ONE expression per filtered prim, each matching exactly one prim per env (e.g. ["{ENV_REGEX_NS}/Obstacle_0", ..., "{ENV_REGEX_NS}/Obstacle_47"]), not one wildcard matching all obstacles. 3) Read obstacle contacts from data.force_matrix_w, never net_forces_w (includes ground support force).

## Failed attempts
- Wildcard '{ENV_REGEX_NS}/Obstacle_.*' in filter_prim_paths_expr
- net_forces_w magnitude threshold as collision signal

## Verify
Smoke test: drive robots into obstacles and assert force_matrix_w nonzero; assert zero collision terminations on step 1; grep job log for 'Filter pattern'.

## Stack
| | |
|---|---|
| isaaclab | v2.1.0 |
| isaacsim | 4.5.0 |
| gpu | L40S |

<small>created 2026-10-06 · id `isaac-lab-contactsensor-wildcard-filter-fails-silently-net-f-b424`</small>

## Notes

<!-- callcentre:end -->
Also: spawning creates only the leaf prim, so '/World/envs/env_.*/Obstacles/Obstacle_k' fails if Obstacles/ doesn't exist -- spawn flat as env_.*/Obstacle_k.
