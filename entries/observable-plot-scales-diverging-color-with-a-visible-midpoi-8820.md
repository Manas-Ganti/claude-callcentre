---
id: observable-plot-scales-diverging-color-with-a-visible-midpoi-8820
kind: convention
title: 'Observable Plot scales: diverging color with a visible midpoint; no legend for the r (size) scale'
domain:
- dataviz
- observable
stack:
  '@observablehq/plot': '0.6'
  platform: observablehq.com classic notebooks
symptoms:
- RdBu diverging midpoint disappears on a white background
- Plot shows no legend for dot size (r)
root_cause: ''
fix: 'Diverging color: `color: {type: "linear", domain: [-1, 0, 1], range: [red, gray, blue]}` instead
  of the RdBu scheme, whose white midpoint vanishes. Plot has no built-in legend for r: explain size in
  the subtitle or caption.'
failed_attempts: []
verify: ''
status: verified
uses: 1
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: '2026-10-01'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Observable Plot scales: diverging color with a visible midpoint; no legend for the r (size) scale

> [!success] convention · verified · used 1×, failed 0× · last verified 2026-10-01
> #dataviz #observable #kind/convention #status/verified

## Symptoms
```text
RdBu diverging midpoint disappears on a white background
Plot shows no legend for dot size (r)
```

## Convention
Diverging color: `color: {type: "linear", domain: [-1, 0, 1], range: [red, gray, blue]}` instead of the RdBu scheme, whose white midpoint vanishes. Plot has no built-in legend for r: explain size in the subtitle or caption.

## Stack
| | |
|---|---|
| @observablehq/plot | 0.6 |
| platform | observablehq.com classic notebooks |

<small>created 2026-10-06 · id `observable-plot-scales-diverging-color-with-a-visible-midpoi-8820`</small>

## Notes

<!-- callcentre:end -->
From Info-vis/observable (agent observable-code-agent). Verified with Plot 0.6 on 2026-10-01; the user confirmed the charts in the browser. Related: [[observable-plot-chart-renders-axes-but-no-dots-r-or-other-ch-6668]] (undefined r drops dots silently), [[testing-observable-notebook-cells-plot-d3-htl-inputs-headles-bccf]] (legend:true crashes in jsdom).
