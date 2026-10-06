---
id: heredoc-patching-a-json-config-wrote-a-literal-n-and-broke-t-9e8c
kind: fix
title: Heredoc-patching a JSON config wrote a literal \n and broke the DeepSpeed config
domain:
- infra
- deepspeed
stack: {}
symptoms:
- DeepSpeed config fails to load after editing it with a heredoc containing escape sequences
root_cause: ''
fix: Validate every edited JSON config with `python -m json.tool <file>` before submitting.
failed_attempts: []
verify: ''
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Heredoc-patching a JSON config wrote a literal \\n and broke the DeepSpeed config

> [!note] fix · unverified · used 0×, failed 0×
> #infra #deepspeed #kind/fix #status/unverified

## Symptoms
```text
DeepSpeed config fails to load after editing it with a heredoc containing escape sequences
```

## Fix
Validate every edited JSON config with `python -m json.tool <file>` before submitting.

<small>created 2026-10-06 · id `heredoc-patching-a-json-config-wrote-a-literal-n-and-broke-t-9e8c`</small>

## Notes

<!-- callcentre:end -->
From VLM-RL-aicontent-detection docs/arc_runbook.md + git history (agent vrr-arc-repo-mining); not reproduced in-session. Source commit ff89115.
