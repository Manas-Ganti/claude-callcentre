---
id: testing-observable-notebook-cells-plot-d3-htl-inputs-headles-bccf
kind: convention
title: Testing Observable notebook cells (Plot / D3 / htl / Inputs) headlessly in Node + jsdom when no
  browser is available
domain:
- dataviz
- observable
- testing
stack:
  node: '24'
  jsdom: latest
  d3: '7'
  '@observablehq/plot': '0.6'
  htl: '0.3'
  '@observablehq/inputs': '0.12'
  os: macOS
symptoms:
- 'Playwright MCP fails: Chrome not installed on this machine'
- Need to verify Observable cell code before the user pastes it into observablehq.com
root_cause: Without a browser, jsdom is the closest approximation. It differs from browsers in several
  ways, which are listed in failed_attempts.
fix: 'In the scratchpad, run `npm i jsdom d3@7 @observablehq/plot@0.6 htl@0.3 @observablehq/inputs@0.12
  @observablehq/parser@6`. Create a JSDOM with `pretendToBeVisual:true`. Copy window, document, Event,
  Element, Node, SVGElement, HTMLElement, NodeList, HTMLCollection, DocumentFragment, Text, HTMLInputElement,
  CustomEvent, getComputedStyle and requestAnimationFrame onto globalThis. Pass `{document}` to Plot.plot.
  Run each cell''s exact text with `new Function(...cellNames, ''"use strict";'' + body)`: strip the `{
  }` for block cells, and use `return (expr)` for expression cells. Call it with `this` = the previous
  value to simulate re-runs, and strip `viewof x` keys from the parameter names. Stub read-only SVGSVGElement.prototype
  x/y/width/height getters to match the browser. Count circle/path elements to confirm marks render. Reference
  implementation: Fall-2026/Info-vis/observable/memory/tools/observable-cell-harness.mjs and parse-cells.mjs.'
failed_attempts:
- 'Playwright MCP: no Chrome installed, so don''t retry'
- 'Plot `legend: true` on a continuous color scale crashes in jsdom (no canvas). Set legend:false only
  in the test; it works in the browser'
- Assigning globalThis.navigator throws on Node 24 (getter-only), so skip it
- Without strict mode + read-only SVG getter stubs, jsdom hides 'Attempted to assign to readonly property'
  bugs
verify: '`node harness.mjs` renders each cell; then check, e.g., `document.querySelectorAll("circle").length
  > 0`.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Testing Observable notebook cells (Plot / D3 / htl / Inputs) headlessly in Node + jsdom when no browser is available

> [!note] convention · unverified · used 0×, failed 0×
> #dataviz #observable #testing #kind/convention #status/unverified

## Symptoms
```text
Playwright MCP fails: Chrome not installed on this machine
Need to verify Observable cell code before the user pastes it into observablehq.com
```

## Root cause
Without a browser, jsdom is the closest approximation. It differs from browsers in several ways, which are listed in failed_attempts.

## Convention
In the scratchpad, run `npm i jsdom d3@7 @observablehq/plot@0.6 htl@0.3 @observablehq/inputs@0.12 @observablehq/parser@6`. Create a JSDOM with `pretendToBeVisual:true`. Copy window, document, Event, Element, Node, SVGElement, HTMLElement, NodeList, HTMLCollection, DocumentFragment, Text, HTMLInputElement, CustomEvent, getComputedStyle and requestAnimationFrame onto globalThis. Pass `{document}` to Plot.plot. Run each cell's exact text with `new Function(...cellNames, '"use strict";' + body)`: strip the `{ }` for block cells, and use `return (expr)` for expression cells. Call it with `this` = the previous value to simulate re-runs, and strip `viewof x` keys from the parameter names. Stub read-only SVGSVGElement.prototype x/y/width/height getters to match the browser. Count circle/path elements to confirm marks render. Reference implementation: Fall-2026/Info-vis/observable/memory/tools/observable-cell-harness.mjs and parse-cells.mjs.

## Failed attempts
- Playwright MCP: no Chrome installed, so don't retry
- Plot `legend: true` on a continuous color scale crashes in jsdom (no canvas). Set legend:false only in the test; it works in the browser
- Assigning globalThis.navigator throws on Node 24 (getter-only), so skip it
- Without strict mode + read-only SVG getter stubs, jsdom hides 'Attempted to assign to readonly property' bugs

## Verify
`node harness.mjs` renders each cell; then check, e.g., `document.querySelectorAll("circle").length > 0`.

## Stack
| | |
|---|---|
| node | 24 |
| jsdom | latest |
| d3 | 7 |
| @observablehq/plot | 0.6 |
| htl | 0.3 |
| @observablehq/inputs | 0.12 |
| os | macOS |

<small>created 2026-10-06 · id `testing-observable-notebook-cells-plot-d3-htl-inputs-headles-bccf`</small>

<!-- callcentre:end -->
