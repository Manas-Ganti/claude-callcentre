---
id: isaac-lab-wheeled-robot-carter-thrown-launched-on-tilted-kin-7af7
kind: open_issue
title: Isaac Lab wheeled robot (Carter) thrown/launched on tilted kinematic-cuboid ground at 5 and 15
  deg but not 10 deg
domain:
- env
- isaac-sim
stack:
  isaacsim: 4.5.0
  isaaclab: v2.1.0
  gpu: L40S
  robot: Carter v1 (76 kg + 10-45 kg payload deck link)
  num_envs: 64
symptoms:
- 'Smoke test: robots move max 1.57 m (5 deg) / 4.71 m (15 deg) in 1 s while parked; height spread 0.14
  / 0.12 m; 0.000 at 0 and 10 deg'
- 26-29 of 64 envs thrown at 5 and 15 deg, identical on repeat visits; ~2.5 m/s upward
- 'Eval: 0% success for RL, Nav2 AND random policy at 5 deg; fine at 10/12 deg'
- '15 deg: airborne within 0.1 s of spawn, thrown robots face ACROSS slope; 5 deg: rest normally ~1.3
  s then sink ~6 cm while driving and get launched'
repro: Per-env sloped ground = kinematic RigidObject cuboid rotated R_y(-theta) via write_root_pose_to_sim;
  Carter v1 spawned level 5 cm above; run training/train.py --smoke-test --num-envs 64 (throw sweep 2..18
  deg).
attempts:
- Reset joint state (wheel spin, caster angle) on reset -- guessed fix, no change
- Edge-band start sampling (robot overhanging patch edge) -- fixed a different tipping bug, not this one
- 'Ruled out: obstacles (1-6 m away), payload, reset height (exactly 0.300)'
- 'Hypothesis A (15 deg): level robot dropped above tilted floor puts uphill wheel 0.269*tan15=7.2 cm
  up, i.e. 2.2 cm inside ground -> PhysX ejection (10 deg: 4.7 cm, just clear). Fix pushed (commit f1057e5):
  spawn tilted to slope q_tilt (x) q_yaw, spawn height 0.26 m along the normal. NOT YET CONFIRMED BY A
  RUN.'
- 'Hypothesis B (5 deg): ground slab only 0.1 m thick; >5 cm penetration resolves through the wrong face.
  Fix pushed: ground_thickness_m 1.0, slab rotated about its TOP-surface centre (old centre rotation also
  left ~2 mm offset). NOT YET CONFIRMED.'
- 'Open suspect: convex-hull (polygonal) wheel colliders resting on an edge at certain tilts (pattern
  repeats rather than growing with angle)'
status: open
claimed_by: null
claim_expires: null
created: '2026-10-06'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab wheeled robot (Carter) thrown/launched on tilted kinematic-cuboid ground at 5 and 15 deg but not 10 deg

> [!bug] open issue · open · 6 attempts logged
> #env #isaac-sim #kind/open_issue #status/open

## Symptoms
```text
Smoke test: robots move max 1.57 m (5 deg) / 4.71 m (15 deg) in 1 s while parked; height spread 0.14 / 0.12 m; 0.000 at 0 and 10 deg
26-29 of 64 envs thrown at 5 and 15 deg, identical on repeat visits; ~2.5 m/s upward
Eval: 0% success for RL, Nav2 AND random policy at 5 deg; fine at 10/12 deg
15 deg: airborne within 0.1 s of spawn, thrown robots face ACROSS slope; 5 deg: rest normally ~1.3 s then sink ~6 cm while driving and get launched
```

## Repro
Per-env sloped ground = kinematic RigidObject cuboid rotated R_y(-theta) via write_root_pose_to_sim; Carter v1 spawned level 5 cm above; run training/train.py --smoke-test --num-envs 64 (throw sweep 2..18 deg).

## Attempts so far
- Reset joint state (wheel spin, caster angle) on reset -- guessed fix, no change
- Edge-band start sampling (robot overhanging patch edge) -- fixed a different tipping bug, not this one
- Ruled out: obstacles (1-6 m away), payload, reset height (exactly 0.300)
- Hypothesis A (15 deg): level robot dropped above tilted floor puts uphill wheel 0.269*tan15=7.2 cm up, i.e. 2.2 cm inside ground -> PhysX ejection (10 deg: 4.7 cm, just clear). Fix pushed (commit f1057e5): spawn tilted to slope q_tilt (x) q_yaw, spawn height 0.26 m along the normal. NOT YET CONFIRMED BY A RUN.
- Hypothesis B (5 deg): ground slab only 0.1 m thick; >5 cm penetration resolves through the wrong face. Fix pushed: ground_thickness_m 1.0, slab rotated about its TOP-surface centre (old centre rotation also left ~2 mm offset). NOT YET CONFIRMED.
- Open suspect: convex-hull (polygonal) wheel colliders resting on an edge at certain tilts (pattern repeats rather than growing with angle)

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 |
| isaaclab | v2.1.0 |
| gpu | L40S |
| robot | Carter v1 (76 kg + 10-45 kg payload deck link) |
| num_envs | 64 |

<small>created 2026-10-06 · id `isaac-lab-wheeled-robot-carter-thrown-launched-on-tilted-kin-7af7`</small>

<!-- callcentre:end -->
