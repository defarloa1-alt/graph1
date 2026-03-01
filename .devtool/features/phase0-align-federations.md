---
id: "phase0-align-federations-2026-02-26"
status: "todo"
priority: "high"
assignee: null
dueDate: null
created: "2026-02-26T00:00:00.000Z"
modified: "2026-02-26T00:00:00.000Z"
completedAt: null
labels: ["dev", "phase-0"]
order: "d0"
---
# Phase 0b: Write align_federations.py

Input: all `output/nodes/*.json`. Find Wikidata QID via label lookup or concordance. Group by shared QID (confirmed neighbours) and overlapping temporal_range + spatial_anchor (probable). Output: `output/aligned/roman_republic_aligned.json`. Wikidata = alignment only, not authority.
