---
id: unpinned-wandb-pulls-protobuf-5-and-breaks-isaac-lab-2-1-isa-d0f3
kind: fix
title: Unpinned wandb pulls protobuf>=5 and breaks Isaac Lab 2.1 (isaaclab_rl / isaaclab_tasks)
domain:
- infra
- isaac-sim
- python-env
stack:
  isaacsim: 4.5.0
  isaaclab: v2.1.0
  wandb: 0.28 (works)
  python: '3.10'
symptoms:
- pip warns (does not fail) about protobuf conflict with isaaclab_rl / isaaclab_tasks after installing
  wandb
- wandb 0.30 installed, protobuf 7.x installed
root_cause: wandb 0.30 requires protobuf>=5; Isaac Lab 2.1 extensions need protobuf<5. pip only warns
  about the conflict.
fix: Pin `protobuf>=3.20.2,<5` in requirements.txt; pip then resolves wandb to 0.28. Make setup verification
  run `pip check` and fail on conflicts involving isaac*/rsl* packages.
failed_attempts:
- Uninstalling wandb 0.30 blindly -- leaves orphans (opentelemetry-*, googleapis-common-protos); check
  `pip show <pkg> | grep Required-by` before removing
verify: pip check | grep -Ei 'isaac|rsl|protobuf'  (empty) ; python -c "import google.protobuf as p; print(p.__version__)"  (<5)
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Unpinned wandb pulls protobuf>=5 and breaks Isaac Lab 2.1 (isaaclab_rl / isaaclab_tasks)

> [!note] fix · unverified · used 0×, failed 0×
> #infra #isaac-sim #python-env #kind/fix #status/unverified

## Symptoms
```text
pip warns (does not fail) about protobuf conflict with isaaclab_rl / isaaclab_tasks after installing wandb
wandb 0.30 installed, protobuf 7.x installed
```

## Root cause
wandb 0.30 requires protobuf>=5; Isaac Lab 2.1 extensions need protobuf\<5. pip only warns about the conflict.

## Fix
Pin `protobuf>=3.20.2,<5` in requirements.txt; pip then resolves wandb to 0.28. Make setup verification run `pip check` and fail on conflicts involving isaac*/rsl* packages.

## Failed attempts
- Uninstalling wandb 0.30 blindly -- leaves orphans (opentelemetry-*, googleapis-common-protos); check `pip show <pkg> | grep Required-by` before removing

## Verify
pip check | grep -Ei 'isaac|rsl|protobuf'  (empty) ; python -c "import google.protobuf as p; print(p.__version__)"  (\<5)

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 |
| isaaclab | v2.1.0 |
| wandb | 0.28 (works) |
| python | 3.10 |

<small>created 2026-10-06 · id `unpinned-wandb-pulls-protobuf-5-and-breaks-isaac-lab-2-1-isa-d0f3`</small>

<!-- callcentre:end -->
