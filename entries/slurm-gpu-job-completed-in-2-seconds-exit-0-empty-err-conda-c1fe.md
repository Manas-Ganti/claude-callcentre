---
id: slurm-gpu-job-completed-in-2-seconds-exit-0-empty-err-conda-c1fe
kind: fix
title: SLURM GPU job "COMPLETED" in 2 seconds, exit 0, empty .err — conda env's python binary was a 0-byte
  file
domain:
- infra
- python-env
- vt-arc
- slurm
stack:
  cluster: VT ARC /home
  python: 3.11.15
  conda: personal miniconda3
symptoms:
- State=COMPLETED ExitCode=0:0 after ~2 s on a GPU job
- Empty .err; .out contains only the shell echo lines
- Every python invocation prints nothing and exits 0, whatever the arguments
- type -a python looks correct and [ -x ... ] passes
root_cause: envs/<env>/bin/python3.11 was 0 bytes (`file` says empty); python/python3 symlink to it. execve
  on an empty file returns ENOEXEC, so bash runs it as an (empty) shell script, which exits 0. Why the
  file was truncated is UNKNOWN — not quota (334/640 GB used), permissions and symlinks intact, mtime
  matched a job's run minute but nothing in the launchers writes there.
fix: "Restore the byte-identical interpreter from conda's package cache (not hardlinked in this case):\n\
  \  ls -la ~/miniconda3/pkgs/python-3.11*/bin/python3.11   # confirm non-zero\n  cp -p ~/miniconda3/pkgs/python-3.11.15-h17756b0_1/bin/python3.11\
  \ <env>/bin/python3.11\nThen re-verify the stack: <env>/bin/python -c \"import torch, vllm, PIL, transformers;\
  \ print(torch.__version__, vllm.__version__)\". If the cache copy is also 0 bytes (shared inode), conda\
  \ install -p <env> --force-reinstall \"python=3.11.15\" and re-check imports."
failed_attempts:
- Hours debugging launcher scripts, PATH ordering, heredocs and sitecustomize — none relevant
- Forcing conda activation by absolute path and calling $CONDA_ENV/bin/python explicitly — good hygiene
  but did not fix it, the binary itself was empty
verify: '<env>/bin/python -V; echo "exit=$?"   # a real CPython always prints a version. No output = broken
  binary. Extent: find <env>/bin -type f -size 0; find <env>/lib -name "*.so*" -size 0'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# SLURM GPU job "COMPLETED" in 2 seconds, exit 0, empty .err — conda env's python binary was a 0-byte file

> [!note] fix · unverified · used 0×, failed 0×
> #infra #python-env #vt-arc #slurm #kind/fix #status/unverified

## Symptoms
```text
State=COMPLETED ExitCode=0:0 after ~2 s on a GPU job
Empty .err; .out contains only the shell echo lines
Every python invocation prints nothing and exits 0, whatever the arguments
type -a python looks correct and [ -x ... ] passes
```

## Root cause
envs/\<env>/bin/python3.11 was 0 bytes (`file` says empty); python/python3 symlink to it. execve on an empty file returns ENOEXEC, so bash runs it as an (empty) shell script, which exits 0. Why the file was truncated is UNKNOWN — not quota (334/640 GB used), permissions and symlinks intact, mtime matched a job's run minute but nothing in the launchers writes there.

## Fix
Restore the byte-identical interpreter from conda's package cache (not hardlinked in this case):
  ls -la ~/miniconda3/pkgs/python-3.11*/bin/python3.11   # confirm non-zero
  cp -p ~/miniconda3/pkgs/python-3.11.15-h17756b0_1/bin/python3.11 \<env>/bin/python3.11
Then re-verify the stack: \<env>/bin/python -c "import torch, vllm, PIL, transformers; print(torch.__version__, vllm.__version__)". If the cache copy is also 0 bytes (shared inode), conda install -p \<env> --force-reinstall "python=3.11.15" and re-check imports.

## Failed attempts
- Hours debugging launcher scripts, PATH ordering, heredocs and sitecustomize — none relevant
- Forcing conda activation by absolute path and calling \$CONDA_ENV/bin/python explicitly — good hygiene but did not fix it, the binary itself was empty

## Verify
\<env>/bin/python -V; echo "exit=\$?"   # a real CPython always prints a version. No output = broken binary. Extent: find \<env>/bin -type f -size 0; find \<env>/lib -name "*.so*" -size 0

## Stack
| | |
|---|---|
| cluster | VT ARC /home |
| python | 3.11.15 |
| conda | personal miniconda3 |

<small>created 2026-10-06 · id `slurm-gpu-job-completed-in-2-seconds-exit-0-empty-err-conda-c1fe`</small>

## Notes

<!-- callcentre:end -->
Rule: if a job completes in seconds with an empty .err, run `python -V` on the env's interpreter before debugging anything else. If it recurs, it's an ARC /home support ticket. Source: docs/arc_runbook.md 'A zero-byte interpreter', commit 90a2386.
