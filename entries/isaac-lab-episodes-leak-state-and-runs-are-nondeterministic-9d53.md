---
id: isaac-lab-episodes-leak-state-and-runs-are-nondeterministic-9d53
kind: fix
title: 'Isaac Lab episodes leak state and runs are nondeterministic: reset joint state and set env_cfg.seed'
domain:
- isaac-sim
- env
stack:
  isaacsim: 4.5.0 (pip)
  isaaclab: v2.1.0
  gpu: 1x L40S
  cluster: VT ARC Falcon
symptoms:
- Wheel spin / caster angle carry over from the previous episode after reset
- '''Seed not set'' warning; runs not reproducible'
root_cause: ''
fix: 'On reset also write joint state: robot.write_joint_state_to_sim(default_joint_pos, default_joint_vel,
  env_ids=...). Seed through env_cfg.seed.'
failed_attempts: []
verify: ''
status: verified
uses: 1
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: '2026-09-26'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab episodes leak state and runs are nondeterministic: reset joint state and set env_cfg.seed

> [!success] fix · verified · used 1×, failed 0× · last verified 2026-09-26
> #isaac-sim #env #kind/fix #status/verified

## Symptoms
```text
Wheel spin / caster angle carry over from the previous episode after reset
'Seed not set' warning; runs not reproducible
```

## Fix
On reset also write joint state: robot.write_joint_state_to_sim(default_joint_pos, default_joint_vel, env_ids=...). Seed through env_cfg.seed.

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 (pip) |
| isaaclab | v2.1.0 |
| gpu | 1x L40S |
| cluster | VT ARC Falcon |

<small>created 2026-10-06 · id `isaac-lab-episodes-leak-state-and-runs-are-nondeterministic-9d53`</small>

## Notes

<!-- callcentre:end -->
From robotics-rl-payload-transport docs/ISAAC_SIM_PLAYBOOK.md (agent rtn-playbook-export); verified on ARC Falcon L40S during bring-up 2026-09-24/26.
