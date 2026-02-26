---
id: "external-ids-pipeline-2026-02-24"
status: "done"
priority: "high"
assignee: null
dueDate: null
created: "2026-02-24T00:00:00.000Z"
modified: "2026-02-24T00:00:00.000Z"
completedAt: "2026-02-24T00:00:00.000Z"
labels: ["Pipeline"]
order: "a1"
---
# External IDs in harvest pipeline

Harvester now persists `external_ids` (P1696, P1838, P1605, etc.) to harvest reports. Cluster assignment passes through to member_of_edges.json. Prosopographic crosswalk reads from input instead of re-fetching Wikidata.

**Completed:** wikidata_backlink_harvest.py _extract_external_ids, cluster_assignment external_ids passthrough, prosopographic_crosswalk use when present.
