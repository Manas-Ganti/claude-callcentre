---
id: isaac-sim-4-5-asset-urls-404-when-copied-from-current-5-x-do-1b05
kind: fix
title: Isaac Sim 4.5 asset URLs 404 when copied from current (5.x) docs; robot falls through floor without
  USD sub-files
domain:
- env
- isaac-sim
stack:
  isaacsim: 4.5.0
  isaaclab: v2.1.0
symptoms:
- HTTP 404 for .../Assets/Isaac/4.5/Isaac/Robots/NVIDIA/<Name>/...
- Robot (Carter) falls through the floor when only the top-level carter_v1.usd was copied locally
root_cause: Online docs target Isaac Sim 5.x whose content layout is Robots/NVIDIA/<Name>; the 4.5 content
  server uses Robots/<Name>. USD references are relative and silently unresolved when missing.
fix: 'Use the 4.5 layout Isaac/Robots/<Name>/... e.g. BASE=https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac
  ; Robots/Jetbot/jetbot.usd, Robots/Carter/carter_v1.usd. When copying locally also copy referenced sub-files
  (Carter: Props/carter_main.usd, carter_wheel_left/right/center.usd, carter_backwheel_caster.usd) --
  they hold the collision shapes. Props/materials.usd is visual-only. isaaclab_assets has no JetBot/Carter
  cfg: define ArticulationCfg inline and actuate only the drive joints (joint_names_expr=[left_wheel,right_wheel]),
  not ''.*'' (would drive passive casters).'
failed_attempts: []
verify: 'curl -s -o /dev/null -w ''%{http_code}'' "$BASE/Robots/Carter/carter_v1.usd" -> 200 ; usd-core
  venv on login node: list unresolved layer dependencies of the local copy (should be none besides materials).'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Sim 4.5 asset URLs 404 when copied from current (5.x) docs; robot falls through floor without USD sub-files

> [!note] fix · unverified · used 0×, failed 0×
> #env #isaac-sim #kind/fix #status/unverified

## Symptoms
```text
HTTP 404 for .../Assets/Isaac/4.5/Isaac/Robots/NVIDIA/<Name>/...
Robot (Carter) falls through the floor when only the top-level carter_v1.usd was copied locally
```

## Root cause
Online docs target Isaac Sim 5.x whose content layout is Robots/NVIDIA/\<Name>; the 4.5 content server uses Robots/\<Name>. USD references are relative and silently unresolved when missing.

## Fix
Use the 4.5 layout Isaac/Robots/\<Name>/... e.g. BASE=https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5/Isaac ; Robots/Jetbot/jetbot.usd, Robots/Carter/carter_v1.usd. When copying locally also copy referenced sub-files (Carter: Props/carter_main.usd, carter_wheel_left/right/center.usd, carter_backwheel_caster.usd) -- they hold the collision shapes. Props/materials.usd is visual-only. isaaclab_assets has no JetBot/Carter cfg: define ArticulationCfg inline and actuate only the drive joints (joint_names_expr=[left_wheel,right_wheel]), not '.*' (would drive passive casters).

## Verify
curl -s -o /dev/null -w '%{http_code}' "\$BASE/Robots/Carter/carter_v1.usd" -> 200 ; usd-core venv on login node: list unresolved layer dependencies of the local copy (should be none besides materials).

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 |
| isaaclab | v2.1.0 |

<small>created 2026-10-06 · id `isaac-sim-4-5-asset-urls-404-when-copied-from-current-5-x-do-1b05`</small>

## Notes

<!-- callcentre:end -->
Harmless noise for Carter: UsdPreviewSurface.mdl warnings, 'omni.isaac.dynamic_control is deprecated', improvePatchFriction deprecation, 'Not all actuators are configured! 2 != 4'.
