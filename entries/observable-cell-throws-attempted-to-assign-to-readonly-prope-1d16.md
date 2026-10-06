---
id: observable-cell-throws-attempted-to-assign-to-readonly-prope-1d16
kind: fix
title: Observable cell throws "Attempted to assign to readonly property" when stashing data on an <svg>
  node as .x/.y/.width/.height
domain:
- dataviz
- observable
stack:
  platform: observablehq.com classic notebooks
  d3: '7'
  browser: Safari/WebKit-style message
symptoms:
- 'RuntimeError: Attempted to assign to readonly property'
- Error surfaces in the cell that CALLS the builder function (e.g. `explorer`), not the builder that does
  the assignment
- Same code passes in Node + jsdom tests
root_cause: SVGSVGElement.x/y/width/height are built-in read-only getters (SVGAnimatedLength) in real
  browsers, and Observable evaluates cells in strict mode, so assignment throws. jsdom doesn't implement
  these getters, so tests silently pass.
fix: Rename the custom property to something non-built-in, e.g. `node.xScale = x` instead of `node.x =
  x` (and update every reader). Never attach custom props named x, y, width, height, style, title, id,
  value, etc. to DOM nodes.
failed_attempts:
- 'Testing in jsdom without strict mode / without stubbing the getters: tests passed, browser failed'
verify: 'In a jsdom harness: `for (const p of ["x","y","width","height"]) Object.defineProperty(dom.window.SVGSVGElement.prototype,
  p, {get(){return {}}, configurable:true})` and run cell bodies via `new Function(..., ''"use strict";''
  + body)`; the old code then throws, the renamed code does not.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Observable cell throws "Attempted to assign to readonly property" when stashing data on an \<svg> node as .x/.y/.width/.height

> [!note] fix · unverified · used 0×, failed 0×
> #dataviz #observable #kind/fix #status/unverified

## Symptoms
```text
RuntimeError: Attempted to assign to readonly property
Error surfaces in the cell that CALLS the builder function (e.g. `explorer`), not the builder that does the assignment
Same code passes in Node + jsdom tests
```

## Root cause
SVGSVGElement.x/y/width/height are built-in read-only getters (SVGAnimatedLength) in real browsers, and Observable evaluates cells in strict mode, so assignment throws. jsdom doesn't implement these getters, so tests silently pass.

## Fix
Rename the custom property to something non-built-in, e.g. `node.xScale = x` instead of `node.x = x` (and update every reader). Never attach custom props named x, y, width, height, style, title, id, value, etc. to DOM nodes.

## Failed attempts
- Testing in jsdom without strict mode / without stubbing the getters: tests passed, browser failed

## Verify
In a jsdom harness: `for (const p of ["x","y","width","height"]) Object.defineProperty(dom.window.SVGSVGElement.prototype, p, {get(){return {}}, configurable:true})` and run cell bodies via `new Function(..., '"use strict";' + body)`; the old code then throws, the renamed code does not.

## Stack
| | |
|---|---|
| platform | observablehq.com classic notebooks |
| d3 | 7 |
| browser | Safari/WebKit-style message |

<small>created 2026-10-06 · id `observable-cell-throws-attempted-to-assign-to-readonly-prope-1d16`</small>

## Notes

<!-- callcentre:end -->
User confirmed in the browser on 2026-10-03 that the fix worked.
