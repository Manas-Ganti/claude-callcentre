---
id: workflow-conventions-for-agents-writing-copy-paste-code-for-ec77
title: Workflow conventions for agents writing copy-paste code for a user's Observable notebook
agent: observable-code-agent
project: Info-vis/observable
domain:
- dataviz
- observable
- agent-workflow
created: '2026-10-06T01:09:14'
filed_as:
- agents-writing-copy-paste-code-for-a-user-s-observable-noteb-0f0a
closed: '2026-10-06T01:12:09'
---
Lessons from sessions on 2026-10-01 and 2026-10-03, where the agent can't run the notebook and the user pastes the code:
- One code block = one Observable cell. Before sending, trace every referenced name and field back to a cell the user currently has. If an upstream cell must change, flag it as "REPLACE Cell N" and add a check item, such as "state[0] has totalPopulation".
- Prefer new cells that derive directly from source data over cells that rely on edits to old cells, because missing upstream edits fail silently in Plot.
- For structural or layout rewrites, propose a plan first (what stays, what changes, which cells get replaced or deleted) and wait for approval. The user explicitly asked to "think before committing to code generation".
- When explaining a statistic, state which two variables it's between and at what level of aggregation (for example, counties within a state vs. state averages).
- A single "drill-down" block cell holding state on its root node (restored through `this`) worked well for keeping multiple linked D3 views in one cell.
