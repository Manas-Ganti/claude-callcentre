---
id: vlm-probe-gates-use-auc-not-argmax-accuracy-and-check-file-g-f83b
kind: convention
title: 'VLM probe gates: use AUC, not argmax accuracy, and check file geometry doesn''t predict the label'
domain:
- eval
stack: {}
symptoms:
- VLM probe gate fails on accuracy although the model separates the classes
- Probe looks good but may be using a shortcut
root_cause: ''
fix: 'Gate on AUC (accuracy 0.600 vs AUC 0.874 on the same model and data). Before any GPU probe, check
  that file geometry (aspect ratio, size) doesn''t predict the label: it did (area AUC 0.850).'
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
# VLM probe gates: use AUC, not argmax accuracy, and check file geometry doesn't predict the label

> [!note] convention · unverified · used 0×, failed 0×
> #eval #kind/convention #status/unverified

## Symptoms
```text
VLM probe gate fails on accuracy although the model separates the classes
Probe looks good but may be using a shortcut
```

## Convention
Gate on AUC (accuracy 0.600 vs AUC 0.874 on the same model and data). Before any GPU probe, check that file geometry (aspect ratio, size) doesn't predict the label: it did (area AUC 0.850).

<small>created 2026-10-06 · id `vlm-probe-gates-use-auc-not-argmax-accuracy-and-check-file-g-f83b`</small>

## Notes

<!-- callcentre:end -->
From VLM-RL-aicontent-detection docs/arc_runbook.md + git history (agent vrr-arc-repo-mining); not reproduced in-session.
