---
id: isaac-lab-directrlenv-calls-get-dones-before-get-rewards-ter-6780
kind: fix
title: 'Isaac Lab DirectRLEnv calls _get_dones before _get_rewards: terminal rewards one step late and
  double-counted'
domain:
- env
- rl-training
- isaac-sim
stack:
  isaaclab: v2.1.0
symptoms:
- Terminations happen one step after goal/collision
- Terminal rewards (goal bonus, collision penalty) counted twice per episode
- Per-step state (goal reached, collision) computed in _get_rewards
root_cause: DirectRLEnv.step() evaluates dones first; state computed in _get_rewards is stale (previous
  step) when dones are decided.
fix: Compute per-step state (distances, goal/collision flags) in _get_dones() and cache it on self; _get_rewards()
  only reads the cache. Step order is _get_dones -> _get_rewards -> _reset_idx -> _get_observations.
failed_attempts: []
verify: 'Unit/smoke: force a goal-reaching env and assert the goal reward appears exactly once and on
  the same step as terminated=True.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab DirectRLEnv calls _get_dones before _get_rewards: terminal rewards one step late and double-counted

> [!note] fix · unverified · used 0×, failed 0×
> #env #rl-training #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
Terminations happen one step after goal/collision
Terminal rewards (goal bonus, collision penalty) counted twice per episode
Per-step state (goal reached, collision) computed in _get_rewards
```

## Root cause
DirectRLEnv.step() evaluates dones first; state computed in _get_rewards is stale (previous step) when dones are decided.

## Fix
Compute per-step state (distances, goal/collision flags) in _get_dones() and cache it on self; _get_rewards() only reads the cache. Step order is _get_dones -> _get_rewards -> _reset_idx -> _get_observations.

## Verify
Unit/smoke: force a goal-reaching env and assert the goal reward appears exactly once and on the same step as terminated=True.

## Stack
| | |
|---|---|
| isaaclab | v2.1.0 |

<small>created 2026-10-06 · id `isaac-lab-directrlenv-calls-get-dones-before-get-rewards-ter-6780`</small>

<!-- callcentre:end -->
