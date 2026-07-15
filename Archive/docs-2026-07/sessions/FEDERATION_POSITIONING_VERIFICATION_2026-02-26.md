# Federation Positioning Verification — 2026-02-26

**For:** Architect  
**From:** Dev  
**Status:** Write complete. 4a passed. 4e modified (PROVIDES_ANCHOR issue).

---

## Summary

Q17167 federation positioning write completed successfully via Cypher in Neo4j Browser (Python blocked by DNS from dev machine). All 7 steps ran cleanly. Verification 4a passed. Verification 4e failed on original query; simplified version runs.

---

## What Was Written

- **SYS_Policy:** `FederationPositioningHopsSemantics` (hops definition)
- **6 POSITIONED_AS edges** from SubjectConcept Q17167 to Entity nodes:

| target_qid | rel_type | confidence |
|------------|----------|------------|
| Q1747689 (Ancient Rome) | COMPOSITIONAL_PARENT | HIGH |
| Q11514315 (historical period) | INSTANCE_OF_CLASS | HIGH |
| Q1307214 (form of government) | INSTANCE_OF_CLASS | HIGH |
| Q48349 (empire) | INSTANCE_OF_CLASS | MEDIUM |
| Q3024240 (historical country) | INSTANCE_OF_CLASS | HIGH |
| Q666680 (aristocratic republic) | TYPE_ANCHOR | HIGH |

All edges: `federation=wikidata`, `policy_ref=FederationPositioningHopsSemantics`, `hops=1`.

---

## 4a — Addressability (passed)

Query returned 6 rows as expected. Q17167 is reachable from multiple federation coordinates via typed POSITIONED_AS edges. **Addressability claim validated.**

---

## 4e — Independence (PROVIDES_ANCHOR issue)

**Original 4e query failed:**
```
Relationship type does not exist: PROVIDES_ANCHOR
```

**Cause:** All 6 targets are Entity nodes (already in graph from harvest). The stubbed write wrote POSITIONED_AS directly to Entity. No ClassificationAnchor nodes were created. PROVIDES_ANCHOR exists only between SYS_FederationSource and ClassificationAnchor — so the relationship type has never been created in this graph.

**Workaround:** Run 4e without the PROVIDES_ANCHOR join:
```cypher
MATCH (sc:SubjectConcept {qid: 'Q17167'})
OPTIONAL MATCH (sc)-[r:POSITIONED_AS]->(target)
RETURN sc.label, target.qid, target.label, labels(target), r.rel_type, r.hops, r.confidence
ORDER BY r.hops, r.rel_type
```

**Implication for v3:** When targets are Entity nodes, the container view is POSITIONED_AS → Entity only. PROVIDES_ANCHOR applies when we create ClassificationAnchor nodes (for targets not yet in the graph). The v3 spec should clarify:
- When do we write to Entity vs ClassificationAnchor?
- When does PROVIDES_ANCHOR get created?
- Is the container view complete without PROVIDES_ANCHOR when all anchors are Entity?

---

## Architect Analysis (2026-02-26)

**What the 4e issue reveals:** The spec assumed some target QIDs would not exist as Entity nodes and therefore ClassificationAnchor nodes would be created — triggering PROVIDES_ANCHOR edges to Wikidata. But all 5 of Q17167's direct parents already exist as Entity nodes in the graph. So POSITIONED_AS edges went to Entities, ClassificationAnchor nodes were never created, and PROVIDES_ANCHOR had nothing to point to.

The container exists and is addressable. But the federation handle — the live wire back to Wikidata — is missing.

**What v3 needs to decide — two options:**

| Option | Approach | Implication |
|--------|----------|-------------|
| **1** | PROVIDES_ANCHOR goes to Entity nodes too, not just ClassificationAnchor | Simple fix. Wikidata FederationSource gets wired to every target from a Wikidata traversal. SFAs always have a live handle. |
| **2** | Entity nodes don't need PROVIDES_ANCHOR — provenance is implicit via QID | Cleaner. PROVIDES_ANCHOR reserved for ClassificationAnchor (notation coordinates with no QID). Aligns with ConceptAnchor vs NotationAnchor split: NotationAnchors always get PROVIDES_ANCHOR; ConceptAnchors that are Entity nodes don't. |

**This is the first concrete data point for v3.** Architect to draft v3 incorporating review feedback plus this finding.

---

## Acceptance Test Outcome

- **4a (addressability):** Passed — clean, legible output.
- **4e (independence):** Modified query runs; original fails on PROVIDES_ANCHOR. The container view (SubjectConcept + POSITIONED_AS + target labels) is available and an SFA could orient from it. The PROVIDES_ANCHOR gap is a schema-design question for v3.

---

## Files

- Write: `scripts/neo4j/federation_positioning_q17167_step_by_step.md` (run in Neo4j Browser)
- Runbook: `md/Architecture/DEV_RUNBOOK_FEDERATION_POSITIONING.md`
- Spec: `docs/architecture/SCA_FEDERATION_POSITIONING_SPEC_v2.md`
