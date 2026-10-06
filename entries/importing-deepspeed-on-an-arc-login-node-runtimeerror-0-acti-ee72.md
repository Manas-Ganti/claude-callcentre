---
id: importing-deepspeed-on-an-arc-login-node-runtimeerror-0-acti-ee72
kind: fix
title: 'Importing deepspeed on an ARC login node: RuntimeError 0 active drivers (not a broken env)'
domain:
- infra
- deepspeed
- vt-arc
stack: {}
symptoms:
- 'RuntimeError: 0 active drivers, raised by `import deepspeed` on the login node'
root_cause: Triton finds no GPU driver on the login node.
fix: 'Nothing to fix: test deepspeed imports on a GPU node.'
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
# Importing deepspeed on an ARC login node: RuntimeError 0 active drivers (not a broken env)

> [!note] fix · unverified · used 0×, failed 0×
> #infra #deepspeed #vt-arc #kind/fix #status/unverified

## Symptoms
```text
RuntimeError: 0 active drivers, raised by `import deepspeed` on the login node
```

## Root cause
Triton finds no GPU driver on the login node.

## Fix
Nothing to fix: test deepspeed imports on a GPU node.

<small>created 2026-10-06 · id `importing-deepspeed-on-an-arc-login-node-runtimeerror-0-acti-ee72`</small>

## Notes

<!-- callcentre:end -->
From VLM-RL-aicontent-detection docs/arc_runbook.md + git history (agent vrr-arc-repo-mining); not reproduced in-session.
