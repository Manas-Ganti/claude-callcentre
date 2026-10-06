---
id: running-isaac-sim-4-5-isaac-lab-2-1-on-vt-arc-falcon-l40s-sl-790a
kind: convention
title: Running Isaac Sim 4.5 / Isaac Lab 2.1 on VT ARC (Falcon L40S, SLURM, pip install)
domain:
- infra
- isaac-sim
- python-env
stack:
  isaacsim: 4.5.0
  isaaclab: v2.1.0
  python: '3.10'
  torch: 2.5.1+cu121
  gpu: 1x L40S 48GB
  nodes: 1
  cluster: VT ARC Falcon
symptoms:
- Setting up Isaac Lab training on VT ARC
- Which GPU/partition for Isaac Sim on ARC
- Env vars passed as VAR=x sbatch ignored
- Jobs 'succeed' in 2 s
root_cause: ''
fix: 'GPU: L40S (RT cores) on Falcon; submit from falcon1/falcon2; partition l40s_normal_q, --gres=gpu:l40s:1,
  explicit --mem (never --mem=0), --cpus-per-task=16 (CPU-side resets). A100/H200 (Tinkercliffs) = headless
  physics only. Install: dedicated conda env, python 3.10, torch 2.5.1+cu121 first, then isaacsim[all,extscache]==4.5.0
  (extscache avoids ext downloads on compute nodes), Isaac Lab v2.1.0 tag, numpy<2, protobuf<5, setuptools<75.
  Login-node TMPDIR=$HOME/tmp. One GPU per job; seeds via --array. Pass settings as argparse after the
  script (`sbatch ... train.slurm --set k=v`), not VAR=x. mkdir logs/slurm before sbatch. Launcher should
  use absolute env python and assert `python -V` prints (a 0-byte interpreter once made jobs exit OK in
  2 s), check stack with find_spec (importing isaaclab submodules before AppLauncher is an error), set
  EULA env vars, and grep the log for ''PhysX error'' on exit. W&B online works from Falcon compute nodes.'
failed_attempts: []
verify: Smoke test job (64 envs, 45 min) completes with 0 'PhysX error' lines; throughput ~28-36k env-steps/s
  at 2048 envs (Carter), first launch builds caches 5-15 min.
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Running Isaac Sim 4.5 / Isaac Lab 2.1 on VT ARC (Falcon L40S, SLURM, pip install)

> [!note] convention · unverified · used 0×, failed 0×
> #infra #isaac-sim #python-env #kind/convention #status/unverified

## Symptoms
```text
Setting up Isaac Lab training on VT ARC
Which GPU/partition for Isaac Sim on ARC
Env vars passed as VAR=x sbatch ignored
Jobs 'succeed' in 2 s
```

## Convention
GPU: L40S (RT cores) on Falcon; submit from falcon1/falcon2; partition l40s_normal_q, --gres=gpu:l40s:1, explicit --mem (never --mem=0), --cpus-per-task=16 (CPU-side resets). A100/H200 (Tinkercliffs) = headless physics only. Install: dedicated conda env, python 3.10, torch 2.5.1+cu121 first, then isaacsim[all,extscache]==4.5.0 (extscache avoids ext downloads on compute nodes), Isaac Lab v2.1.0 tag, numpy\<2, protobuf\<5, setuptools\<75. Login-node TMPDIR=\$HOME/tmp. One GPU per job; seeds via --array. Pass settings as argparse after the script (`sbatch ... train.slurm --set k=v`), not VAR=x. mkdir logs/slurm before sbatch. Launcher should use absolute env python and assert `python -V` prints (a 0-byte interpreter once made jobs exit OK in 2 s), check stack with find_spec (importing isaaclab submodules before AppLauncher is an error), set EULA env vars, and grep the log for 'PhysX error' on exit. W&B online works from Falcon compute nodes.

## Verify
Smoke test job (64 envs, 45 min) completes with 0 'PhysX error' lines; throughput ~28-36k env-steps/s at 2048 envs (Carter), first launch builds caches 5-15 min.

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 |
| isaaclab | v2.1.0 |
| python | 3.10 |
| torch | 2.5.1+cu121 |
| gpu | 1x L40S 48GB |
| nodes | 1 |
| cluster | VT ARC Falcon |

<small>created 2026-10-06 · id `running-isaac-sim-4-5-isaac-lab-2-1-on-vt-arc-falcon-l40s-sl-790a`</small>

## Notes

<!-- callcentre:end -->
Full playbook: robotics-rl-payload-transport/docs/ISAAC_SIM_PLAYBOOK.md; launchers arc/*.slurm, arc/arc_env.sh, arc/setup_env.sh. Env ~30-35 GB + 5-10 GB kit caches; check `quota`, not df.
