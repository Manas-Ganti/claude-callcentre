---
id: wrong-robot-geometry-from-usd-bounding-boxes-stale-extent-hi-a22b
kind: fix
title: Wrong robot geometry from USD bounding boxes (stale extent hint; rotated cylinder wheel radius)
domain:
- env
- isaac-sim
stack:
  usd-core: pip in throwaway venv on login node
  isaacsim: 4.5.0
  robot: Carter v1
symptoms:
- UsdGeom.BBoxCache reports a ~3 km robot for Carter v1
- Wheel radius from bbox 0.278/0.271 m vs true 0.24 m -> every velocity command runs at ~87% speed
root_cause: Carter primitives carry stale authored extent hints; an axis-aligned bbox of a rotated cylinder
  overstates its radius.
fix: 'Compute extents with UsdGeom.Boundable.ComputeExtentFromPlugins (ignores stale authored ''extent'')
  and transform corners to world. For cylinders read the ''radius'' attribute x world scale (Carter: 0.5
  x 0.48 = 0.24 m). Ground-truth with a physical measurement: resting root height above flat ground =
  wheel radius for Carter (0.240 m).'
failed_attempts: []
verify: 'Run a forward probe: measured speed / commanded speed ~1.0.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Wrong robot geometry from USD bounding boxes (stale extent hint; rotated cylinder wheel radius)

> [!note] fix · unverified · used 0×, failed 0×
> #env #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
UsdGeom.BBoxCache reports a ~3 km robot for Carter v1
Wheel radius from bbox 0.278/0.271 m vs true 0.24 m -> every velocity command runs at ~87% speed
```

## Root cause
Carter primitives carry stale authored extent hints; an axis-aligned bbox of a rotated cylinder overstates its radius.

## Fix
Compute extents with UsdGeom.Boundable.ComputeExtentFromPlugins (ignores stale authored 'extent') and transform corners to world. For cylinders read the 'radius' attribute x world scale (Carter: 0.5 x 0.48 = 0.24 m). Ground-truth with a physical measurement: resting root height above flat ground = wheel radius for Carter (0.240 m).

## Verify
Run a forward probe: measured speed / commanded speed ~1.0.

## Stack
| | |
|---|---|
| usd-core | pip in throwaway venv on login node |
| isaacsim | 4.5.0 |
| robot | Carter v1 |

<small>created 2026-10-06 · id `wrong-robot-geometry-from-usd-bounding-boxes-stale-extent-hi-a22b`</small>

## Notes

<!-- callcentre:end -->
Tool: robotics-rl-payload-transport/arc/inspect_usd.py. Carter v1 measured: 76.2 kg total, wheel r 0.24, track 0.538, footprint 0.443, maxForce=inf on drives (set effort_limit_sim for a finite torque cap).
