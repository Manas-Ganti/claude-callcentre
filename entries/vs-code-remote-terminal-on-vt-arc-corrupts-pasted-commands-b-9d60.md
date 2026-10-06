---
id: vs-code-remote-terminal-on-vt-arc-corrupts-pasted-commands-b-9d60
kind: fix
title: VS Code remote terminal on VT ARC corrupts pasted commands (bracketed-paste markers)
domain:
- infra
- vt-arc
stack: {}
symptoms:
- Stray `~` appended to filenames (manifest.jsonl~)
- Literal `[200~` prefix on a pasted command
- Pasted variable assignments never take effect; heredocs swallow the next command
- '`env FOO=1 $V -c ...` prints the environment and exits 0 (a mangled V=... left $V empty)'
root_cause: The VS Code remote terminal leaks bracketed-paste escape markers into the shell on ARC.
fix: 'Per shell: `bind ''set enable-bracketed-paste off''`. Otherwise paste single-line commands only,
  or write the commands to a file and run it.'
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
# VS Code remote terminal on VT ARC corrupts pasted commands (bracketed-paste markers)

> [!note] fix · unverified · used 0×, failed 0×
> #infra #vt-arc #kind/fix #status/unverified

## Symptoms
```text
Stray `~` appended to filenames (manifest.jsonl~)
Literal `[200~` prefix on a pasted command
Pasted variable assignments never take effect; heredocs swallow the next command
`env FOO=1 $V -c ...` prints the environment and exits 0 (a mangled V=... left $V empty)
```

## Root cause
The VS Code remote terminal leaks bracketed-paste escape markers into the shell on ARC.

## Fix
Per shell: `bind 'set enable-bracketed-paste off'`. Otherwise paste single-line commands only, or write the commands to a file and run it.

<small>created 2026-10-06 · id `vs-code-remote-terminal-on-vt-arc-corrupts-pasted-commands-b-9d60`</small>

## Notes

<!-- callcentre:end -->
From VLM-RL-aicontent-detection docs/arc_runbook.md + git history (agent vrr-arc-repo-mining); not reproduced in-session.
