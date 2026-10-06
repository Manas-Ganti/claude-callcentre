---
id: tolocalestring-follows-the-system-locale-indian-grouping-10-d779
kind: fix
title: toLocaleString() follows the system locale (Indian grouping 10,00,000 on this Mac), so numbers
  don't match d3.format(",")
domain:
- dataviz
- observable
stack:
  os: macOS (Indian region format)
  node: '24'
  d3: '7'
symptoms:
- (1000000).toLocaleString() gives "10,00,000" while d3.format(",") axis labels give "1,000,000"
- Tooltip / table numbers disagree with the axis labels
root_cause: toLocaleString() without an argument uses the system locale, which on this Mac uses Indian
  digit grouping.
fix: Use `toLocaleString("en-US")` or d3.format(",") everywhere.
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
# toLocaleString() follows the system locale (Indian grouping 10,00,000 on this Mac), so numbers don't match d3.format(",")

> [!note] fix · unverified · used 0×, failed 0×
> #dataviz #observable #kind/fix #status/unverified

## Symptoms
```text
(1000000).toLocaleString() gives "10,00,000" while d3.format(",") axis labels give "1,000,000"
Tooltip / table numbers disagree with the axis labels
```

## Root cause
toLocaleString() without an argument uses the system locale, which on this Mac uses Indian digit grouping.

## Fix
Use `toLocaleString("en-US")` or d3.format(",") everywhere.

## Stack
| | |
|---|---|
| os | macOS (Indian region format) |
| node | 24 |
| d3 | 7 |

<small>created 2026-10-06 · id `tolocalestring-follows-the-system-locale-indian-grouping-10-d779`</small>

## Notes

<!-- callcentre:end -->
From Info-vis/observable (agent observable-code-agent). Seen 2026-10-03 in Observable/D3 tooltips and tables; same in Node and the browser on this machine.
