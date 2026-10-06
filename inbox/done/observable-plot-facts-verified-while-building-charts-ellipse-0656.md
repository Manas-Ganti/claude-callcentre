---
id: observable-plot-facts-verified-while-building-charts-ellipse-0656
title: Observable Plot facts verified while building charts (ellipses, size legend, diverging midpoint)
agent: observable-code-agent
project: Info-vis/observable
domain:
- dataviz
- observable
created: '2026-10-06T01:09:05'
filed_as:
- covariance-ellipses-in-observable-plot-plot-line-with-z-fill-7aa8
- observable-plot-scales-diverging-color-with-a-visible-midpoi-8820
closed: '2026-10-06T01:12:09'
---
Verified with @observablehq/plot 0.6 (2026-10-01), and the user confirmed the charts in the browser:
- `Plot.line(points, {x, y, z, fill: "r", fillOpacity})` fills closed outlines. This works for drawing ellipses (for example, a 1-SD covariance ellipse with 73 outline points per group).
- Plot has no built-in legend for the `r` (size) scale. Explain size in the subtitle or caption instead.
- `Plot.dot` drops points whose `r` is undefined or NaN, silently (see the separate fix entry on the empty chart).
- Diverging color with a visible midpoint: `color: {type: "linear", domain: [-1, 0, 1], range: [red, gray, blue]}`. Prefer this over the RdBu scheme, whose white midpoint vanishes on a white background.
- In jsdom tests, `legend: true` on a continuous color scale crashes (no canvas). Disable it only in tests.
- Covariance-ellipse math: for each group compute sdX, sdY and r. The ellipse is the 1-SD contour; for 95%, multiply the SDs by 2.45. Groups with 1 member (for example District of Columbia in the US county data) have undefined SD and r, so drop them.
