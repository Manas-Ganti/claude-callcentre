---
id: isaac-lab-physx-wheel-ground-contact-grips-far-more-than-the-b806
kind: open_issue
title: Isaac Lab/PhysX wheel-ground contact grips far more than the ground friction setting (Carter v1)
domain:
- env
- isaac-sim
stack:
  isaacsim: 4.5.0
  isaaclab: v2.1.0
  gpu: L40S
  robot: Carter v1
symptoms:
- 'Slide test on 10 deg slope with true STOP: mu 0.1 drifted 0.159 m vs 0.134 m at mu 0.9 -- nearly identical'
- Launch slip 0.48 at mu 0.9 vs 0.60 at mu 0.1 -- axis live but much weaker than rigid-body physics predicts
- Eval drive times identical from mu 0.9 to 0.1
repro: robotics-rl-payload-transport smoke test friction probe / slide test (training/train.py --smoke-test),
  Carter v1 on kinematic cuboid ground, ground friction_combine_mode='min'.
attempts:
- Ground combine 'min' + randomized ground mu -> inert (Carter tyre material is low friction, always the
  min)
- Tyre friction fixed at 1.0 on all robot contact shapes -> live but weak (0.48 vs 0.60)
- Tyre friction = sampled ground mu each episode ('match_ground', commit 9a51405) -> pushed, not yet measured
- 'Suspects not yet tested: PhysX convex approximation of cylinder wheels; deprecated improvePatchFriction
  flag on Carter materials; caster contact carrying load'
status: open
claimed_by: null
claim_expires: null
created: '2026-10-06'
related:
- '[[friction-randomization-inert-in-isaac-lab-robot-tyre-materia-735f]]'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab/PhysX wheel-ground contact grips far more than the ground friction setting (Carter v1)

> [!bug] open issue · open · 4 attempts logged
> #env #isaac-sim #kind/open_issue #status/open

## Symptoms
```text
Slide test on 10 deg slope with true STOP: mu 0.1 drifted 0.159 m vs 0.134 m at mu 0.9 -- nearly identical
Launch slip 0.48 at mu 0.9 vs 0.60 at mu 0.1 -- axis live but much weaker than rigid-body physics predicts
Eval drive times identical from mu 0.9 to 0.1
```

## Repro
robotics-rl-payload-transport smoke test friction probe / slide test (training/train.py --smoke-test), Carter v1 on kinematic cuboid ground, ground friction_combine_mode='min'.

## Attempts so far
- Ground combine 'min' + randomized ground mu -> inert (Carter tyre material is low friction, always the min)
- Tyre friction fixed at 1.0 on all robot contact shapes -> live but weak (0.48 vs 0.60)
- Tyre friction = sampled ground mu each episode ('match_ground', commit 9a51405) -> pushed, not yet measured
- Suspects not yet tested: PhysX convex approximation of cylinder wheels; deprecated improvePatchFriction flag on Carter materials; caster contact carrying load

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 |
| isaaclab | v2.1.0 |
| gpu | L40S |
| robot | Carter v1 |

<small>created 2026-10-06 · id `isaac-lab-physx-wheel-ground-contact-grips-far-more-than-the-b806`</small>

<!-- callcentre:end -->
