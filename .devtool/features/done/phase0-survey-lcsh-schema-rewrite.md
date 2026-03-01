---
id: "phase0-survey-lcsh-schema-rewrite-2026-02-26"
status: "done"
priority: "high"
assignee: null
dueDate: null
created: "2026-02-26T00:00:00.000Z"
modified: "2026-02-26T00:00:00.000Z"
completedAt: null
labels: ["dev", "phase-0"]
order: "c0"
---
# Phase 0a: Rewrite survey_lcsh_domain.py to use schema contract

Import `federation_node_schema.new_node`, `new_survey`, `FederationSurvey`. For each LCSH heading: `new_node()` with `concept_ref`=heading URI, `temporal_range`=parse_temporal_from_lcsh(label), `spatial_anchor`=None. Output: `output/nodes/lcsh_roman_republic.json` as `FederationSurvey`. Run: `python scripts/backbone/subject/survey_lcsh_domain.py --seed sh85115114`
