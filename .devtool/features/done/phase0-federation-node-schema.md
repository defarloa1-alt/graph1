---
id: "phase0-federation-node-schema-2026-02-26"
status: "done"
priority: "high"
assignee: null
dueDate: null
created: "2026-02-26T00:00:00.000Z"
modified: "2026-02-26T00:00:00.000Z"
completedAt: null
labels: ["dev", "phase-0"]
order: "b0"
---
# Phase 0: federation_node_schema.py

Contract written and validated. Alignment-field-first: `temporal_range`, `spatial_anchor`, `concept_ref`, `person_ref`, `text_ref`, `event_ref`. Dimensions derived from fields + federation defaults. `adjacency()` method, round-trip serialisation tested. **Deploy to:** `scripts/backbone/subject/federation_node_schema.py`
