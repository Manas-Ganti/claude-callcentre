---
id: visualizing-1m-point-time-series-in-d3-observable-per-pixel-fa81
kind: convention
title: 'Visualizing 1M-point time series in D3/Observable: per-pixel min/max/mean binning + linked overview→context→detail'
domain:
- dataviz
- observable
stack:
  d3: '7'
  platform: observablehq.com classic notebooks
symptoms:
- Need an accurate overview of ~1,000,000 points without rendering 1M marks
- Random sampling hides outlier peaks/valleys
root_cause: Rendering all points is slow and overplots. Sampling loses extremes. Per-pixel aggregation
  is exact at screen resolution.
fix: 'For each horizontal pixel column, scan all points in that bin and keep min, max and mean. Draw the
  min–max as an area band and the mean as a line. This takes about 10 ms for 1M points, which is fast
  enough to re-bin on every brush move. Link the views in three levels: Overview (all points) → Context
  (~50k window, brushed from the overview) → Detail (~1k raw points as dots, switching back to band mode
  above ~3,000), with hover tooltips and click-to-pin for exact values. Mark the top-k peaks and valleys
  with minimum spacing (n/50) so outliers stay visible. When one brush moves, rebuild only the views below
  it. Keep UI state on the root node and restore it through `this` on re-run, so a resize keeps the selection.
  Reference code: Fall-2026/Info-vis/observable/memory/code/timeseries-explorer-v2.js (binSeries, explorer).'
failed_attempts:
- 'Sampled overview (the template''s default): misses spikes'
- 'Keyhole detail view without context: users lose their place'
verify: Time binSeries on 1M points (should be about 10 ms); check that the band's global max equals d3.max(Y).
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Visualizing 1M-point time series in D3/Observable: per-pixel min/max/mean binning + linked overview→context→detail

> [!note] convention · unverified · used 0×, failed 0×
> #dataviz #observable #kind/convention #status/unverified

## Symptoms
```text
Need an accurate overview of ~1,000,000 points without rendering 1M marks
Random sampling hides outlier peaks/valleys
```

## Root cause
Rendering all points is slow and overplots. Sampling loses extremes. Per-pixel aggregation is exact at screen resolution.

## Convention
For each horizontal pixel column, scan all points in that bin and keep min, max and mean. Draw the min–max as an area band and the mean as a line. This takes about 10 ms for 1M points, which is fast enough to re-bin on every brush move. Link the views in three levels: Overview (all points) → Context (~50k window, brushed from the overview) → Detail (~1k raw points as dots, switching back to band mode above ~3,000), with hover tooltips and click-to-pin for exact values. Mark the top-k peaks and valleys with minimum spacing (n/50) so outliers stay visible. When one brush moves, rebuild only the views below it. Keep UI state on the root node and restore it through `this` on re-run, so a resize keeps the selection. Reference code: Fall-2026/Info-vis/observable/memory/code/timeseries-explorer-v2.js (binSeries, explorer).

## Failed attempts
- Sampled overview (the template's default): misses spikes
- Keyhole detail view without context: users lose their place

## Verify
Time binSeries on 1M points (should be about 10 ms); check that the band's global max equals d3.max(Y).

## Stack
| | |
|---|---|
| d3 | 7 |
| platform | observablehq.com classic notebooks |

<small>created 2026-10-06 · id `visualizing-1m-point-time-series-in-d3-observable-per-pixel-fa81`</small>

## Notes

<!-- callcentre:end -->
The user confirmed it works in the browser (2026-10-03).
