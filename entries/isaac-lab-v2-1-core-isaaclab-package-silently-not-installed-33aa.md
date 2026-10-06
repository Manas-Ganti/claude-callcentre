---
id: isaac-lab-v2-1-core-isaaclab-package-silently-not-installed-33aa
kind: fix
title: Isaac Lab v2.1 core `isaaclab` package silently not installed (flatdict build fails on pkg_resources)
domain:
- infra
- isaac-sim
- python-env
stack:
  isaacsim: 4.5.0 (pip, isaacsim[all,extscache])
  isaaclab: v2.1.0 git tag
  python: '3.10'
  torch: 2.5.1+cu121
  cluster: VT ARC Falcon, conda env, no Docker
symptoms:
- Isaac Lab extensions (isaaclab_rl, isaaclab_tasks) import-check fine via find_spec, but `pip show isaaclab`
  shows nothing / import isaaclab fails
- 'flatdict==4.0.1 build failure: setup.py does `import pkg_resources` -> ModuleNotFoundError: No module
  named ''pkg_resources'' in pip''s isolated build env'
- isaaclab.sh --install appears to complete; failure only visible scrolling back through the log
root_cause: pip's isolated build env pulls the newest setuptools, which no longer ships pkg_resources;
  flatdict 4.0.1's setup.py imports it, so the core isaaclab package install fails while its extensions
  install fine.
fix: pip install "setuptools<75" && pip install flatdict==4.0.1 --no-build-isolation && pip install -e
  source/isaaclab  (from the IsaacLab checkout)
failed_attempts:
- Checking install success with importlib.util.find_spec on the extension packages only -- passes even
  though core isaaclab is missing
- Re-running the full installer -- reinstalls torch and isaacsim (~20 GB, slow) and hits the same failure
verify: pip show isaaclab && pip check | grep -Ei 'isaac|rsl' (must be empty)
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Isaac Lab v2.1 core `isaaclab` package silently not installed (flatdict build fails on pkg_resources)

> [!note] fix · unverified · used 0×, failed 0×
> #infra #isaac-sim #python-env #kind/fix #status/unverified

## Symptoms
```text
Isaac Lab extensions (isaaclab_rl, isaaclab_tasks) import-check fine via find_spec, but `pip show isaaclab` shows nothing / import isaaclab fails
flatdict==4.0.1 build failure: setup.py does `import pkg_resources` -> ModuleNotFoundError: No module named 'pkg_resources' in pip's isolated build env
isaaclab.sh --install appears to complete; failure only visible scrolling back through the log
```

## Root cause
pip's isolated build env pulls the newest setuptools, which no longer ships pkg_resources; flatdict 4.0.1's setup.py imports it, so the core isaaclab package install fails while its extensions install fine.

## Fix
pip install "setuptools\<75" && pip install flatdict==4.0.1 --no-build-isolation && pip install -e source/isaaclab  (from the IsaacLab checkout)

## Failed attempts
- Checking install success with importlib.util.find_spec on the extension packages only -- passes even though core isaaclab is missing
- Re-running the full installer -- reinstalls torch and isaacsim (~20 GB, slow) and hits the same failure

## Verify
pip show isaaclab && pip check | grep -Ei 'isaac|rsl' (must be empty)

## Stack
| | |
|---|---|
| isaacsim | 4.5.0 (pip, isaacsim[all,extscache]) |
| isaaclab | v2.1.0 git tag |
| python | 3.10 |
| torch | 2.5.1+cu121 |
| cluster | VT ARC Falcon, conda env, no Docker |

<small>created 2026-10-06 · id `isaac-lab-v2-1-core-isaaclab-package-silently-not-installed-33aa`</small>

## Notes

<!-- callcentre:end -->
Verified on ARC in an earlier session (2026-09-24). Script: robotics-rl-payload-transport/arc/setup_env.sh. Also: login-node /tmp is 20 GB, too small for isaacsim wheels -> export TMPDIR=$HOME/tmp/... and delete after (~20 GB quota).
