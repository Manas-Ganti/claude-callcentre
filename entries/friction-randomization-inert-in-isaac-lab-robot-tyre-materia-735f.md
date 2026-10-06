---
id: friction-randomization-inert-in-isaac-lab-robot-tyre-materia-735f
kind: fix
title: 'Friction randomization inert in Isaac Lab: robot tyre material wins the PhysX combine mode'
domain:
- env
- isaac-sim
stack:
  isaaclab: v2.1.0
  isaacsim: 4.5.0
  robot: Carter v1
symptoms:
- Launch slip / drive times identical at ground mu 0.9 and 0.1
- Friction study axis shows no effect; no errors
root_cause: PhysX uses the higher-priority combine mode of the two materials (average < min < multiply
  < max). Ground used 'min', and Carter's USD tyre material is low-friction, so min(ground, tyre) always
  equalled the tyre.
fix: 'Override the robot''s contact-shape material at startup (or per episode) instead of only randomizing
  the ground. Simplest robust option: set tyre friction = sampled ground friction each episode (''match_ground''),
  so average/min/max/multiply all yield the sampled value. Then confirm with a forced-condition probe
  (slip or slide test at high vs low mu) using a true STOP action.'
failed_attempts:
- Setting ground friction_combine_mode='min' and randomizing only ground friction
- 'Fixed tyre friction 1.0 with min mode: axis became live (slip 0.48 vs 0.60) but weaker than expected
  -- see open issue on residual grip'
verify: 'Smoke-test friction probe: launch slip / slide distance must differ clearly between mu 0.9 and
  0.1; read back material props from root_physx_view.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
related:
- '[[isaac-lab-physx-wheel-ground-contact-grips-far-more-than-the-b806]]'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Friction randomization inert in Isaac Lab: robot tyre material wins the PhysX combine mode

> [!note] fix · unverified · used 0×, failed 0×
> #env #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
Launch slip / drive times identical at ground mu 0.9 and 0.1
Friction study axis shows no effect; no errors
```

## Root cause
PhysX uses the higher-priority combine mode of the two materials (average \< min \< multiply \< max). Ground used 'min', and Carter's USD tyre material is low-friction, so min(ground, tyre) always equalled the tyre.

## Fix
Override the robot's contact-shape material at startup (or per episode) instead of only randomizing the ground. Simplest robust option: set tyre friction = sampled ground friction each episode ('match_ground'), so average/min/max/multiply all yield the sampled value. Then confirm with a forced-condition probe (slip or slide test at high vs low mu) using a true STOP action.

## Failed attempts
- Setting ground friction_combine_mode='min' and randomizing only ground friction
- Fixed tyre friction 1.0 with min mode: axis became live (slip 0.48 vs 0.60) but weaker than expected -- see open issue on residual grip

## Verify
Smoke-test friction probe: launch slip / slide distance must differ clearly between mu 0.9 and 0.1; read back material props from root_physx_view.

## Stack
| | |
|---|---|
| isaaclab | v2.1.0 |
| isaacsim | 4.5.0 |
| robot | Carter v1 |

<small>created 2026-10-06 · id `friction-randomization-inert-in-isaac-lab-robot-tyre-materia-735f`</small>

## Notes

<!-- callcentre:end -->
Root cause and the inert->live change verified on ARC; the 'match_ground' variant (commit 9a51405) is pushed but not yet confirmed by a run.
