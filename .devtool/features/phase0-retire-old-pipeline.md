---
id: "phase0-retire-old-pipeline-2026-02-26"
status: "todo"
priority: "low"
assignee: null
dueDate: null
created: "2026-02-26T00:00:00.000Z"
modified: "2026-02-26T00:00:00.000Z"
completedAt: null
labels: ["dev", "phase-0"]
order: "e0"
---
# Housekeeping: Retire old SubjectConcept pipeline

Rename `enrich_subject_concept_authority_ids.py` → `validate_wikidata_authority_properties.py`, make read-only. Document bad data (Dewey-in-P1149, LCNAF-in-P244, Q1234567, Q1541). Archive `subject_concept_anchors_qid_canonical.json`.
