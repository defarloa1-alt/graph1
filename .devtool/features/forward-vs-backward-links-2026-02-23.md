---
id: "forward-vs-backward-links-2026-02-23"
status: "todo"
priority: "critical"
assignee: null
dueDate: null
created: "2026-02-24T01:26:22.229Z"
modified: "2026-02-24T13:19:37.060Z"
completedAt: null
labels: ["Core Subject"]
order: "a4"
---
# forward vs backward links

## **orward links (forward traversal) — not implemented**

**Definition:** Outbound triples ?source ?property ?target where source = seed QID.

“What entities does this seed point TO?”

**Implementation:** None. Only planned.

**Planned use:** Handle dead anchors (zero backlinks):

AnchorBacklinksIssueQ2916317 (Military roles & command structure)0Too abstract; nothing points to itForward neighbors—Q2916317 → P361 → Q1114493 (Roman army) etc.

**Docs:** PIPELINE_LAYERS_AND_PROPERTY\_[ALLOWLIST.md](http://ALLOWLIST.md), Federation/CHRYSTALLUM\_[HANDOFF.md](http://HANDOFF.md):

&gt; "Forward traversal (the Q2916317 / zero-backlinks case) closes most of that gap without opening the harvester's property gate to structural properties."

&gt; "Dead anchors (zero backlinks) where the concept QID is too abstract to attract backlinks but has rich forward neighbors (e.g. Q2916317 military roles → Q1114493 Roman army). Fix is forward traversal."

---

## **Summary**

DirectionStatusImplementation**Backward** (inbound)Implementedwikidata_backlink\_[harvest.py](http://harvest.py) — reverse triples**Forward** (outbound)**Not implemented**Planned for dead anchors

---

## **Forward traversal (planned)**

1. **Trigger:** Anchor has zero backlinks (e.g. Q2916317).


1) **Query:** ?seed ?prop ?target for seed QID (P361, P527, P31, etc.).


1. **Output:** Entities the seed points to (e.g. Q1114493 Roman army).


1) **Merge:** Treat as discovered entities, same as backlink results.

---

## **Dead anchors (current state)**

MetricSourceQ2916317 harvestbacklink_rows: 0, accepted: 0Anchors with zero backlinksIdentified in harvest_run_summary / completed

Forward traversal would allow discovery of entities that are only reachable via outbound links from these anchors.