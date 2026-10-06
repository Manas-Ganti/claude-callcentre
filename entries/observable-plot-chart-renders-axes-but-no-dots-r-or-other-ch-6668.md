---
id: observable-plot-chart-renders-axes-but-no-dots-r-or-other-ch-6668
kind: fix
title: 'Observable Plot chart renders axes but no dots: r (or other) channel field is undefined'
domain:
- dataviz
- observable
stack:
  '@observablehq/plot': '0.6'
  platform: observablehq.com classic notebooks
symptoms:
- Plot.dot chart shows axes/frame but zero circles, no error message
- Happened after re-emitting an upstream cell that added a field (totalPopulation) which the user never
  pasted
root_cause: Plot silently drops marks whose channel value is undefined or NaN (r, x, y, ...). It throws
  no error, so a missing field looks like an empty chart.
fix: 'Make sure the field used in the channel (e.g. `r: "totalPopulation"`) exists in the data the user
  currently has: either re-paste the upstream cell that defines it (flag it as ''REPLACE Cell N''), or
  derive the field inside the new cell directly from the source data so it doesn''t depend on edits to
  old cells. Quick check: `data[0].totalPopulation !== undefined`.'
failed_attempts: []
verify: 'In jsdom: render `Plot.plot({document, marks:[Plot.dot(data,{x,y,r})]})` and count `circle` elements;
  0 means the channel is missing.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Observable Plot chart renders axes but no dots: r (or other) channel field is undefined

> [!note] fix · unverified · used 0×, failed 0×
> #dataviz #observable #kind/fix #status/unverified

## Symptoms
```text
Plot.dot chart shows axes/frame but zero circles, no error message
Happened after re-emitting an upstream cell that added a field (totalPopulation) which the user never pasted
```

## Root cause
Plot silently drops marks whose channel value is undefined or NaN (r, x, y, ...). It throws no error, so a missing field looks like an empty chart.

## Fix
Make sure the field used in the channel (e.g. `r: "totalPopulation"`) exists in the data the user currently has: either re-paste the upstream cell that defines it (flag it as 'REPLACE Cell N'), or derive the field inside the new cell directly from the source data so it doesn't depend on edits to old cells. Quick check: `data[0].totalPopulation !== undefined`.

## Verify
In jsdom: render `Plot.plot({document, marks:[Plot.dot(data,{x,y,r})]})` and count `circle` elements; 0 means the channel is missing.

## Stack
| | |
|---|---|
| @observablehq/plot | 0.6 |
| platform | observablehq.com classic notebooks |

<small>created 2026-10-06 · id `observable-plot-chart-renders-axes-but-no-dots-r-or-other-ch-6668`</small>

<!-- callcentre:end -->
