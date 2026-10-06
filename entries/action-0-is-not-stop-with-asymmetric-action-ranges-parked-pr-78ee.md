---
id: action-0-is-not-stop-with-asymmetric-action-ranges-parked-pr-78ee
kind: fix
title: Action 0 is not 'stop' with asymmetric action ranges -- parked probes actually drove
domain:
- env
- eval
stack:
  isaaclab: v2.1.0
symptoms:
- '''Parked'' robots drift/drive during a stop or slide test'
- Slide/drift probe FAILs that look like friction bugs
root_cause: Asymmetric velocity limits + linear rescaling of normalized actions.
fix: 'Each action dim maps [-1,1] onto [lo,hi], so 0 is the midpoint (lin [-0.5,1.5] -> 0.5 m/s). Probes
  must send the normalized action that maps to zero velocity: a0 = -(hi+lo)/(hi-lo) per dim.'
failed_attempts: []
verify: Parked drift on flat ground ~0 (observed 0.008 m after fix).
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Action 0 is not 'stop' with asymmetric action ranges -- parked probes actually drove

> [!note] fix · unverified · used 0×, failed 0×
> #env #eval #kind/fix #status/unverified

## Symptoms
```text
'Parked' robots drift/drive during a stop or slide test
Slide/drift probe FAILs that look like friction bugs
```

## Root cause
Asymmetric velocity limits + linear rescaling of normalized actions.

## Fix
Each action dim maps [-1,1] onto [lo,hi], so 0 is the midpoint (lin [-0.5,1.5] -> 0.5 m/s). Probes must send the normalized action that maps to zero velocity: a0 = -(hi+lo)/(hi-lo) per dim.

## Verify
Parked drift on flat ground ~0 (observed 0.008 m after fix).

## Stack
| | |
|---|---|
| isaaclab | v2.1.0 |

<small>created 2026-10-06 · id `action-0-is-not-stop-with-asymmetric-action-ranges-parked-pr-78ee`</small>

<!-- callcentre:end -->
