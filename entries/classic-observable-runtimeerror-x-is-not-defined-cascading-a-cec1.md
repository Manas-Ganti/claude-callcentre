---
id: classic-observable-runtimeerror-x-is-not-defined-cascading-a-cec1
kind: fix
title: 'Classic Observable "RuntimeError: X is not defined" cascading across cells = a cell was never
  pasted, not a code bug'
domain:
- dataviz
- observable
stack:
  '@observablehq/parser': '6'
  platform: observablehq.com classic notebooks
symptoms:
- 'RuntimeError: layout is not defined'
- 'RuntimeError: binSeries is not defined (shown on every downstream cell)'
root_cause: In classic Observable, a name is defined only by a cell. If a helper cell is missing or failed
  to paste as a separate cell, every cell that references it fails with "is not defined".
fix: 'Find the cell that defines X and paste it as its own cell (one code block = one cell). Don''t change
  the code. When an answer has helper cells at the end, warn up front: "Paste all N cells; cells show
  ''X is not defined'' until the cell defining X exists", and give a table mapping each missing name to
  its cell number.'
failed_attempts:
- 'Rewriting the referencing cell: pointless, because the code was valid'
verify: '`npm i @observablehq/parser@6`; `parseCell(code)` on each cell, then print `c.id.name` (what
  it defines) and `c.references` (what it reads). Every reference should be defined by some cell or be
  a built-in.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# Classic Observable "RuntimeError: X is not defined" cascading across cells = a cell was never pasted, not a code bug

> [!note] fix · unverified · used 0×, failed 0×
> #dataviz #observable #kind/fix #status/unverified

## Symptoms
```text
RuntimeError: layout is not defined
RuntimeError: binSeries is not defined (shown on every downstream cell)
```

## Root cause
In classic Observable, a name is defined only by a cell. If a helper cell is missing or failed to paste as a separate cell, every cell that references it fails with "is not defined".

## Fix
Find the cell that defines X and paste it as its own cell (one code block = one cell). Don't change the code. When an answer has helper cells at the end, warn up front: "Paste all N cells; cells show 'X is not defined' until the cell defining X exists", and give a table mapping each missing name to its cell number.

## Failed attempts
- Rewriting the referencing cell: pointless, because the code was valid

## Verify
`npm i @observablehq/parser@6`; `parseCell(code)` on each cell, then print `c.id.name` (what it defines) and `c.references` (what it reads). Every reference should be defined by some cell or be a built-in.

## Stack
| | |
|---|---|
| @observablehq/parser | 6 |
| platform | observablehq.com classic notebooks |

<small>created 2026-10-06 · id `classic-observable-runtimeerror-x-is-not-defined-cascading-a-cec1`</small>

<!-- callcentre:end -->
