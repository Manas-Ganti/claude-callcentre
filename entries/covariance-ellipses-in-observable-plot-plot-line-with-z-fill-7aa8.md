---
id: covariance-ellipses-in-observable-plot-plot-line-with-z-fill-7aa8
kind: convention
title: 'Covariance ellipses in Observable Plot: Plot.line with z + fill draws closed outlines'
domain:
- dataviz
- observable
stack:
  '@observablehq/plot': '0.6'
  platform: observablehq.com classic notebooks
symptoms:
- How to draw a covariance / confidence ellipse per group in Observable Plot
root_cause: ''
fix: 'Per group compute sdX, sdY and r; generate the 1-SD contour as outline points (73 per group works)
  and draw with `Plot.line(points, {x, y, z, fill: "r", fillOpacity})`, which fills closed outlines. For
  95% multiply the SDs by 2.45. Drop groups with one member (undefined SD and r, e.g. District of Columbia
  in US county data).'
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
# Covariance ellipses in Observable Plot: Plot.line with z + fill draws closed outlines

> [!success] convention · verified · used 1×, failed 0× · last verified 2026-10-01
> #dataviz #observable #kind/convention #status/verified

## Symptoms
```text
How to draw a covariance / confidence ellipse per group in Observable Plot
```

## Convention
Per group compute sdX, sdY and r; generate the 1-SD contour as outline points (73 per group works) and draw with `Plot.line(points, {x, y, z, fill: "r", fillOpacity})`, which fills closed outlines. For 95% multiply the SDs by 2.45. Drop groups with one member (undefined SD and r, e.g. District of Columbia in US county data).

## Stack
| | |
|---|---|
| @observablehq/plot | 0.6 |
| platform | observablehq.com classic notebooks |

<small>created 2026-10-06 · id `covariance-ellipses-in-observable-plot-plot-line-with-z-fill-7aa8`</small>

## Notes

<!-- callcentre:end -->
From Info-vis/observable (agent observable-code-agent). Verified with Plot 0.6 on 2026-10-01; the user confirmed the chart in the browser.
