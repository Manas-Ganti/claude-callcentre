---
id: agents-writing-copy-paste-code-for-a-user-s-observable-noteb-0f0a
kind: convention
title: 'Agents writing copy-paste code for a user''s Observable notebook: one block = one cell, trace
  every name'
domain:
- dataviz
- observable
- agent-workflow
stack: {}
symptoms:
- Agent can't run the notebook; the user pastes the code cell by cell
- Pasted cell fails or renders empty because an upstream cell was never updated
root_cause: ''
fix: One code block = one Observable cell. Before sending, trace every referenced name and field back
  to a cell the user currently has; if an upstream cell must change, flag it as "REPLACE Cell N" with
  a check item (e.g. "state[0] has totalPopulation"). Prefer new cells that derive directly from source
  data over edits to old cells (missing upstream edits fail silently in Plot). For structural or layout
  rewrites, propose a plan first (what stays, what changes, which cells are replaced or deleted) and wait
  for approval. When explaining a statistic, state which two variables and which level of aggregation
  (counties within a state vs state averages). A single drill-down block cell holding state on its root
  node (restored through `this`) keeps multiple linked D3 views in one cell.
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
# Agents writing copy-paste code for a user's Observable notebook: one block = one cell, trace every name

> [!note] convention · unverified · used 0×, failed 0×
> #dataviz #observable #agent-workflow #kind/convention #status/unverified

## Symptoms
```text
Agent can't run the notebook; the user pastes the code cell by cell
Pasted cell fails or renders empty because an upstream cell was never updated
```

## Convention
One code block = one Observable cell. Before sending, trace every referenced name and field back to a cell the user currently has; if an upstream cell must change, flag it as "REPLACE Cell N" with a check item (e.g. "state[0] has totalPopulation"). Prefer new cells that derive directly from source data over edits to old cells (missing upstream edits fail silently in Plot). For structural or layout rewrites, propose a plan first (what stays, what changes, which cells are replaced or deleted) and wait for approval. When explaining a statistic, state which two variables and which level of aggregation (counties within a state vs state averages). A single drill-down block cell holding state on its root node (restored through `this`) keeps multiple linked D3 views in one cell.

<small>created 2026-10-06 · id `agents-writing-copy-paste-code-for-a-user-s-observable-noteb-0f0a`</small>

## Notes

<!-- callcentre:end -->
From Info-vis/observable (agent observable-code-agent). Lessons from sessions 2026-10-01 and 2026-10-03; the user explicitly asked to "think before committing to code generation". Related: [[observable-plot-chart-renders-axes-but-no-dots-r-or-other-ch-6668]], [[classic-observable-runtimeerror-x-is-not-defined-cascading-a-cec1]].
