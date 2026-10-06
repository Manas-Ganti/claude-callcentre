---
id: verifying-isaac-lab-physics-silent-failures-dominate-so-prob-57db
kind: convention
title: 'Verifying Isaac Lab physics: silent failures dominate, so probe every study axis with a forced-condition
  test'
domain:
- isaac-sim
- env
- eval
stack:
  isaacsim: 4.5.0 (pip)
  isaaclab: v2.1.0
  gpu: 1x L40S
  cluster: VT ARC Falcon
symptoms:
- Isaac Lab / PhysX results look plausible but a study axis (friction, slope, payload) has no effect
- How to check that randomization / physics settings actually took effect
- Spread checks fail after running probes
root_cause: ''
fix: Most Isaac/PhysX bugs produce plausible wrong numbers and no exception. For every study axis, add
  a forced-condition probe that measures the physical response (friction slip at high vs low mu, slope
  rest height, forward/turn probe for wheel sign and radius) and read values back with root_physx_view.get_*.
  Probes force all envs to one condition, so snapshot spread checks BEFORE running probes. Diagnose from
  collected evidence before changing code, and batch fixes per sbatch round.
failed_attempts:
- Running spread checks after probes (3 false FAILs)
- 'Guessing a fix before reading the collected data: cost a queue round when the cause was visible in
  the data'
verify: ''
status: verified
uses: 1
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: '2026-09-26'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Verifying Isaac Lab physics: silent failures dominate, so probe every study axis with a forced-condition test

> [!success] convention · verified · used 1×, failed 0× · last verified 2026-09-26
> #isaac-sim #env #eval #kind/convention #status/verified

## Symptoms
```text
Isaac Lab / PhysX results look plausible but a study axis (friction, slope, payload) has no effect
How to check that randomization / physics settings actually took effect
Spread checks fail after running probes
```

## Convention
Most Isaac/PhysX bugs produce plausible wrong numbers and no exception. For every study axis, add a forced-condition probe that measures the physical response (friction slip at high vs low mu, slope rest height, forward/turn probe for wheel sign and radius) and read values back with root_physx_view.get_*. Probes force all envs to one condition, so snapshot spread checks BEFORE running probes. Diagnose from collected evidence before changing code, and batch fixes per sbatch round.

## Failed attempts
- Running spread checks after probes (3 false FAILs)
- Guessing a fix before reading the collected data: cost a queue round when the cause was visible in the data

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 (pip) |
| isaaclab | v2.1.0 |
| gpu | 1x L40S |
| cluster | VT ARC Falcon |

<small>created 2026-10-06 · id `verifying-isaac-lab-physics-silent-failures-dominate-so-prob-57db`</small>

## Notes

<!-- callcentre:end -->
From robotics-rl-payload-transport docs/ISAAC_SIM_PLAYBOOK.md (agent rtn-playbook-export); verified on ARC Falcon L40S during bring-up 2026-09-24/26.

Throughput reference (Carter, 2048 envs, L40S): 28-36k env-steps/s; PPO 3000 it x 24 steps = 147M steps in 74-81 min; collection-bound by CPU terrain gen + A*, hence --cpus-per-task=16 (see [[running-isaac-sim-4-5-isaac-lab-2-1-on-vt-arc-falcon-l40s-sl-790a]]).
