---
id: "subj-rr-refactor-2026-02-24"
status: "completed"
priority: "critical"
assignee: null
dueDate: null
created: "2026-02-24T00:00:00.000Z"
modified: "2026-02-21T00:00:00.000Z"
completedAt: "2026-02-21T00:00:00.000Z"
labels: ["Core Subject", "Architecture"]
order: "a0"
---
# SubjectConcept ID Refactor (subj_rr_* → QID-canonical)

**Done:** QID-canonical model implemented. Identity = qid (no slug). DOMAIN_OF → KnowledgeDomain, BROADER_THAN for hierarchy.

**Delivered:**
- `migrate_anchors_to_qid_canonical.py` — anchors + hierarchy JSON
- `subject_concept_anchors_qid_canonical.json` (61 QIDs)
- `load_subject_concepts_qid_canonical.py` — SubjectConcept(qid), DOMAIN_OF, BROADER_THAN
- harvest_all_anchors, cluster_assignment updated for qid
- `output/neo4j/migrate_subject_concepts_to_qid_canonical.cypher` — drop legacy, add constraint

**Completed:** SubjectConcepts already clean. cluster_assignment run: 5,405 MEMBER_OF edges, 5,287 entities, 45 SubjectConcepts.

**Optional:** Agent scripts (facet_agents, workflow) still use subject_id — update when needed.
