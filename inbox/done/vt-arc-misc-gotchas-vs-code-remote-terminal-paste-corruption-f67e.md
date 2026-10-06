---
id: vt-arc-misc-gotchas-vs-code-remote-terminal-paste-corruption-f67e
title: 'VT ARC misc gotchas: VS Code remote terminal paste corruption, stdout-only gate results, HF_HOME
  default, Telegram job notify'
agent: vrr-arc-repo-mining
project: VLM-RL-aicontent-detection
domain:
- infra
- vt-arc
created: '2026-10-06T00:53:19'
filed_as:
- vs-code-remote-terminal-on-vt-arc-corrupts-pasted-commands-b-9d60
- heredoc-patching-a-json-config-wrote-a-literal-n-and-broke-t-9e8c
- vt-arc-job-environment-export-hf-home-and-wandb-dir-explicit-cd71
- slurm-job-output-persist-results-to-files-wandb-not-stdout-a-26a9
- telegram-notifications-from-slurm-jobs-start-line-tail-full-b46b
- vlm-probe-gates-use-auc-not-argmax-accuracy-and-check-file-g-f83b
- importing-deepspeed-on-an-arc-login-node-runtimeerror-0-acti-ee72
closed: '2026-10-06T01:11:12'
---
Mined from docs/arc_runbook.md and git history (not reproduced this session).

1. VS Code remote terminal leaks bracketed-paste markers on ARC: stray `~` appended to filenames (manifest.jsonl~), literal `[200~` prefix, assignments that never take effect, heredocs swallowing the next command. A mangled V=... left $V empty so `env FOO=1 $V -c ...` ran bare `env` (prints environment, exit 0) — looked like a different failure. Fix per shell: bind 'set enable-bracketed-paste off'. Otherwise single-line commands, or write to a file and run it.

2. Heredoc-patching JSON with escape sequences wrote a literal \n and broke a DeepSpeed config (commit ff89115). Validate with python -m json.tool after editing configs.

3. Probe/gate scripts wrote results only to SLURM stdout (logs/slurm/*.out) — numbers had to be recovered from logs by hand. Persist results to a file (results/<ds>/*.json) and/or wandb.init. Also WANDB_DIR must be set to $HOME/wandb on ARC: /projects/$USER is not writable.

4. arc_env.sh defaulted HF_HOME=/projects/$USER/hf_cache which is wrong for this user (cache at /home/<user>/hf_cache, 68 GB Qwen2.5-VL-32B); must pass/export HF_HOME on every submit. HF_HUB_ENABLE_HF_TRANSFER is now deprecated in huggingface_hub (FutureWarning, use HF_XET_HIGH_PERFORMANCE) — harmless noise in .err.

5. Useful pattern: Telegram notify from SLURM jobs — START line + on exit (trap) the last 30 lines and the whole stdout as a document; every curl `|| true`, no-op when token unset, re-return captured $? so the trap doesn't mask exit code, cut lines to 180 chars before tailing (progress bars), get stdout path from `scontrol show job`. Secrets in ~/.config/vrr/secrets.env chmod 600.

6. Rich-table trajectory logging to stdout produced 58-277 MB .out files per GRPO run (grpo-7263147.out 277 MB) — consider logging traces to JSONL instead.

7. Gate design: don't accept argmax-accuracy gates for VLM probes — use AUC; accuracy 0.600 vs AUC 0.874 on the same model/data. And check that file geometry (aspect/size) doesn't predict the label before any GPU probe (it did: area AUC 0.850).

8. Login-node: importing deepspeed raises `RuntimeError: 0 active drivers` (Triton, no GPU) — not a broken env.
