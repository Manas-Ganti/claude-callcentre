---
id: before-training-a-robot-policy-check-the-robot-can-do-the-ta-eae8
kind: convention
title: 'Before training a robot policy: check the robot can do the task, and run the eval sanity triad'
domain:
- isaac-sim
- eval
- rl-training
stack:
  isaacsim: 4.5.0 (pip)
  isaaclab: v2.1.0
  gpu: 1x L40S
  cluster: VT ARC Falcon
symptoms:
- Policy never reaches commanded speed / task looks impossible
- How to sanity-check an RL eval harness
root_cause: ''
fix: 'Check feasibility first: drive the robot open-loop to the task''s commands with payload. Then run
  one harness on three policies: random (the floor), a classical baseline (must succeed in-distribution
  first), and the trained policy.'
failed_attempts:
- 'JetBot (2 kg, 3 cm wheels) reached 0.38 of a 1.5 m/s command with payload: replaced by Carter'
- Nav2 baseline had ~20% collisions on flat ground until the wheel-radius fix
verify: ''
status: verified
uses: 1
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: '2026-09-26'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Before training a robot policy: check the robot can do the task, and run the eval sanity triad

> [!success] convention · verified · used 1×, failed 0× · last verified 2026-09-26
> #isaac-sim #eval #rl-training #kind/convention #status/verified

## Symptoms
```text
Policy never reaches commanded speed / task looks impossible
How to sanity-check an RL eval harness
```

## Convention
Check feasibility first: drive the robot open-loop to the task's commands with payload. Then run one harness on three policies: random (the floor), a classical baseline (must succeed in-distribution first), and the trained policy.

## Failed attempts
- JetBot (2 kg, 3 cm wheels) reached 0.38 of a 1.5 m/s command with payload: replaced by Carter
- Nav2 baseline had ~20% collisions on flat ground until the wheel-radius fix

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 (pip) |
| isaaclab | v2.1.0 |
| gpu | 1x L40S |
| cluster | VT ARC Falcon |

<small>created 2026-10-06 · id `before-training-a-robot-policy-check-the-robot-can-do-the-ta-eae8`</small>

## Notes

<!-- callcentre:end -->
From robotics-rl-payload-transport docs/ISAAC_SIM_PLAYBOOK.md (agent rtn-playbook-export); verified on ARC Falcon L40S during bring-up 2026-09-24/26. Related: [[wrong-robot-geometry-from-usd-bounding-boxes-stale-extent-hi-a22b]] (the wheel-radius fix).
