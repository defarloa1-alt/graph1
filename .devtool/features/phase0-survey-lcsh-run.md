---
id: "phase0-survey-lcsh-run-2026-02-26"
status: "todo"
priority: "high"
assignee: null
dueDate: null
created: "2026-02-26T00:00:00.000Z"
modified: "2026-02-26T00:00:00.000Z"
completedAt: null
labels: ["dev", "phase-0"]
order: "c1"
---
# Phase 0a: Run LCSH live survey for Roman Republic

`python scripts/backbone/subject/survey_lcsh_domain.py --seed sh85115114 --out output/nodes/lcsh_roman_republic.json`. Expected: 50–200 nodes, 1 ancestor chain, NT descendants. `.lcsh_cache/` makes re-run instant.
