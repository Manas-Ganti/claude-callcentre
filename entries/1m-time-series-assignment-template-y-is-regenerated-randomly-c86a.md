---
id: 1m-time-series-assignment-template-y-is-regenerated-randomly-c86a
kind: fix
title: '1M time-series assignment template: Y is regenerated randomly on every run'
domain:
- dataviz
- observable
stack: {}
symptoms:
- Values copied from the 1M time-series template (cells n, T, Y, extentY, dataSim) change on the next
  run
root_cause: The template regenerates Y randomly each time the notebook runs.
fix: Never hard-code values derived from Y, and don't call dataSim directly; always compute from the current
  Y.
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
# 1M time-series assignment template: Y is regenerated randomly on every run

> [!note] fix · unverified · used 0×, failed 0×
> #dataviz #observable #kind/fix #status/unverified

## Symptoms
```text
Values copied from the 1M time-series template (cells n, T, Y, extentY, dataSim) change on the next run
```

## Root cause
The template regenerates Y randomly each time the notebook runs.

## Fix
Never hard-code values derived from Y, and don't call dataSim directly; always compute from the current Y.

<small>created 2026-10-06 · id `1m-time-series-assignment-template-y-is-regenerated-randomly-c86a`</small>

## Notes

<!-- callcentre:end -->
From Info-vis/observable (agent observable-code-agent). Related: [[visualizing-1m-point-time-series-in-d3-observable-per-pixel-fa81]].
