# SubjectConcept Creation — How It Works and Authority Design

**Date:** 2026-02-26  
**Purpose:** Clarify how SubjectConcepts are created and how they relate to authority sources (LCSH, FAST, LCC).

---

## 1. How SubjectConcepts Are Created (Current State)

### The 61 Roman Republic SubjectConcepts

**Creation path:** Wikidata discovery → manual curation → JSON → Neo4j load

1. **Discovery:** SCA agents (e.g. `sca_comprehensive_builder.py`, `wikidata_lateral_exploration.py`) traverse Wikidata from seed Q17167 (Roman Republic). They extract related QIDs and classify them.

2. **Curation:** LLM + human curation produce `subject_concept_anchors_qid_canonical.json` — 61 rows with `qid`, `label`, `primary_facet`, `confidence`.

3. **Load:** `load_subject_concepts_qid_canonical.py` reads that JSON + `subject_concept_hierarchy.json` and creates `SubjectConcept` nodes in Neo4j via `MERGE` on `qid`.

**Schema at load time:**
- `qid` (required) — Wikidata anchor
- `label` (required) — human-readable
- `primary_facet` — POLITICAL, MILITARY, etc.
- `harvest_status` — from backlink reports (confirmed/unconfirmed)
- `fast_id`, `lcsh_id`, `lcc_id` — **not populated at load**

So: **SubjectConcepts are created as domain-specific concepts that *map to* authority headings, not as authority headings themselves.** The QID is the Wikidata anchor; authority IDs are added later (or not yet).

---

## 2. Federation Sources: LCSH/FAST/LCC — "Operational" Means What?

### Two Different Structures

| Structure | Location | Purpose |
|----------|----------|---------|
| **Federation:AuthoritySystem** | `create_authority_federations.cypher` | Conceptual registry of authority systems (LCSH, FAST, LCC, etc.). Metadata only (URLs, Wikidata properties). |
| **SYS_FederationSource** | `FEDERATION_REGISTRY_REBUILD_SPEC.md` | Self-describing subgraph. One row per source. `status: "operational"` = "we use this source in our pipeline." |

### What "Operational" Means in Practice

**LCSH/FAST/LCC** listed as `operational` in the spec means:
- The federation source node exists and is marked as phase1_complete / phase2_complete.
- **There is no LC SRU harvester or FAST API harvester** that queries id.loc.gov or fast.oclc.org and populates SubjectConcepts automatically.

**What actually exists:**
- `Python/lcsh/scripts/enrich_lcsh_from_wikidata.py` — fetches LCSH/FAST/LCC **from Wikidata** (P244, P2163, P1149) for entities that already have them.
- `scripts/backbone/subject/create_subject_nodes.py` — creates `:Subject` nodes from **PropertyRegistry** (LCSH headings from relationship types), not from LC SRU.
- `scripts/tools/extract_lcsh_relationships.py` — SKOS crosswalks for LCSH/FAST.
- **No script** that queries LC SRU or FAST API to resolve a label → LCSH/FAST ID.

So: **"Operational" = the source is in our registry and we have *some* integration (e.g. Wikidata enrichment).** It does **not** mean "we have a live harvester that queries LC SRU or FAST API."

---

## 3. Design Intent: Domain-Specific vs Authority-Backed

### Current Design: Domain-Specific Concepts That Map to Authorities

The 61 SubjectConcepts are **domain-specific thematic anchors**:
- They were discovered from Wikidata (e.g. "Roman Republic" → related QIDs for magistracies, religion, etc.).
- They have custom labels and facets.
- Authority IDs (FAST, LCSH, LCC) are **intended to be added** but are optional and not yet populated.

**Evidence:** Phase 3 pre-work: "61 SubjectConcepts, 0 FAST IDs, 0 LCSH IDs."

### Alternative: Authority-Backed SubjectConcepts

If SubjectConcepts were **authority headings with custom labels**:
- The canonical identity would be the authority ID (e.g. `lcsh_id` or `fast_id`).
- The QID would be the Wikidata bridge.
- All three (LCSH, FAST, LCC) would be present as parallel identifiers.

**Current state does not match this.** The 61 anchors are QID-first; authority IDs are a secondary enrichment.

---

## 4. What "Right" Could Look Like

### Option A: Parallel Properties (Current Direction)

Each SubjectConcept has:
- `qid` — Wikidata anchor (primary identity today)
- `fast_id`, `lcsh_id`, `lcc_id` — parallel properties, resolved when possible

**Pros:** Simple, matches current schema.  
**Cons:** Manual or one-off resolution (e.g. FAST resolution JSON). No live federation lookup.

### Option B: Resolved from Federation Sources

When a SubjectConcept is created or updated:
1. Query LC SRU / FAST API for the label.
2. Resolve to LCSH ID, FAST ID, LCC code.
3. Set all three.

**Requires:** LC SRU client, FAST API client (or id.loc.gov search). Not currently wired.

### Option C: Structural — SubjectConcepts Link to Authority Nodes

Instead of storing IDs on SubjectConcept:
- `(:SubjectConcept)-[:ALIGNED_TO]->(:LCSH_Heading {id: "sh85115114"})`
- `(:SubjectConcept)-[:ALIGNED_TO]->(:FAST_Heading {id: "fst01204885"})`

**Pros:** Clean separation; authority nodes can be shared.  
**Cons:** More schema; more queries; need to create/maintain authority nodes.

---

## 5. Summary

| Question | Answer |
|----------|--------|
| **How are SubjectConcepts created?** | JSON (qid, label, facet) → `load_subject_concepts_qid_canonical.py` → Neo4j. Discovery via Wikidata traversal + curation. |
| **LCSH/FAST/LCC operational?** | Registry nodes exist; no LC SRU or FAST API harvester. Enrichment via Wikidata (P244, P2163, P1149) for entities that have them. |
| **Domain-specific or authority-backed?** | Domain-specific. QID anchors; authority IDs are added later (Phase 3 A1 FAST). |
| **Right approach?** | Unresolved. Options: parallel properties (A), federation-resolved (B), or structural authority nodes (C). |

---

## 6. References

- `scripts/backbone/subject/load_subject_concepts_qid_canonical.py` — load flow
- `output/subject_concepts/subject_concept_anchors_qid_canonical.json` — 61 anchors
- `docs/FEDERATION_REGISTRY_REBUILD_SPEC.md` — SYS_FederationSource spec
- `scripts/federation/create_authority_federations.cypher` — conceptual registry
- `output/PHASE3_PREWORK_QUERIES.md` — live graph state (0 FAST, 0 LCSH on SubjectConcepts)
