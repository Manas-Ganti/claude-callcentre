---
id: tolocalestring-uses-the-system-locale-indian-grouping-10-00-3a50
title: toLocaleString() uses the system locale (Indian grouping 10,00,000 on this Mac), so numbers don't
  match d3 format(",")
agent: observable-code-agent
project: Info-vis/observable
domain:
- dataviz
- observable
created: '2026-10-06T01:09:00'
filed_as:
- tolocalestring-follows-the-system-locale-indian-grouping-10-d779
closed: '2026-10-06T01:12:09'
---
Observed: `(1000000).toLocaleString()` gives "10,00,000" on this machine (Indian digit grouping), while d3.format(",") on the axes gives "1,000,000". Tooltip and table numbers then disagree with the axis labels.
Fix: use `toLocaleString("en-US")` or d3.format(",") everywhere for consistency.
Seen while building Observable/D3 tooltips and tables (2026-10-03). macOS, Node 24, and the browser on the same machine.
