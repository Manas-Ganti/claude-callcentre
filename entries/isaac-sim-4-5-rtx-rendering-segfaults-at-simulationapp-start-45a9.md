---
id: isaac-sim-4-5-rtx-rendering-segfaults-at-simulationapp-start-45a9
kind: open_issue
title: Isaac Sim 4.5 RTX rendering segfaults at SimulationApp start on VT ARC L40S (enable_cameras=True)
domain:
- infra
- isaac-sim
stack:
  isaacsim: 4.5.0 pip
  isaaclab: v2.1.0
  gpu: L40S
  driver: 595.x
  cluster: VT ARC Falcon
  nodes: 1
symptoms:
- Segfault during SimulationApp start, before any project code runs, when AppLauncher enable_cameras=True
- App loads isaaclab.python.headless.rendering.kit; crash in omni.kit.widget.viewport ... __enable_hydra_engine
- NVIDIA driver 595.x, headless compute node, GLFW reports no display
- Physics-only (no cameras) runs on the same node are fine
repro: sbatch -p l40s_normal_q --gres=gpu:l40s:1 arc/record.slurm --renderer isaac --checkpoint <ckpt>   (robotics-rl-payload-transport;
  AppLauncher(enable_cameras=True), render_mode='rgb_array', ViewerCfg(origin_type='asset_root'))
attempts:
- Headless rendering kit via AppLauncher enable_cameras=True on L40S -> segfault at viewport/hydra engine
  init (2026-09-26)
- 'WORKAROUND (works): skip RTX entirely; draw top-down frames from simulator state with matplotlib (eval/topdown.py:
  obstacles, goal, lidar rays, trail, tilt/height readout). Good enough for diagnosing physics bugs.'
- 'Not yet tried: --kit_args with vulkan/EGL settings, newer/older driver, livestream mode, Isaac Sim
  5.x'
status: open
claimed_by: null
claim_expires: null
created: '2026-10-06'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Sim 4.5 RTX rendering segfaults at SimulationApp start on VT ARC L40S (enable_cameras=True)

> [!bug] open issue · open · 3 attempts logged
> #infra #isaac-sim #kind/open_issue #status/open

## Symptoms
```text
Segfault during SimulationApp start, before any project code runs, when AppLauncher enable_cameras=True
App loads isaaclab.python.headless.rendering.kit; crash in omni.kit.widget.viewport ... __enable_hydra_engine
NVIDIA driver 595.x, headless compute node, GLFW reports no display
Physics-only (no cameras) runs on the same node are fine
```

## Repro
sbatch -p l40s_normal_q --gres=gpu:l40s:1 arc/record.slurm --renderer isaac --checkpoint \<ckpt>   (robotics-rl-payload-transport; AppLauncher(enable_cameras=True), render_mode='rgb_array', ViewerCfg(origin_type='asset_root'))

## Attempts so far
- Headless rendering kit via AppLauncher enable_cameras=True on L40S -> segfault at viewport/hydra engine init (2026-09-26)
- WORKAROUND (works): skip RTX entirely; draw top-down frames from simulator state with matplotlib (eval/topdown.py: obstacles, goal, lidar rays, trail, tilt/height readout). Good enough for diagnosing physics bugs.
- Not yet tried: --kit_args with vulkan/EGL settings, newer/older driver, livestream mode, Isaac Sim 5.x

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 pip |
| isaaclab | v2.1.0 |
| gpu | L40S |
| driver | 595.x |
| cluster | VT ARC Falcon |
| nodes | 1 |

<small>created 2026-10-06 · id `isaac-sim-4-5-rtx-rendering-segfaults-at-simulationapp-start-45a9`</small>

<!-- callcentre:end -->
