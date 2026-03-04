# SCA Academic Positioning — Steps 2–4 Specification

**Date:** 2026-03-04
**Context:** ADR-013, SCA gap analysis for Roman Republic (Q17167)
**Problem:** `sca_federation_positioning.py` implements Step 1 (POSITIONED_AS edges via Wikidata traversal) but stops there. Steps 2–4 — LCC/LCSH linkage, bibliography source binding, and facet assignment — were never built. Additionally, the bootstrap cypher (`bootstrap_subject_concept_agents.cypher`) targeted `subj_roman_republic_q17167` but the actual node has `subject_id: subj_q17167`, so none of its LCSH/FAST/LCC/facet writes landed.

**Immediate fix:** `scripts/neo4j/seed_roman_republic_subject_concept.cypher` completes the seed manually. This spec covers the general-purpose SCA script that should replace manual seeds.

---

## Current state — what Step 1 does

`sca_federation_positioning.py` already:

1. Queries Wikidata SPARQL for P31/P279/P361/P122/P527/P460/P1269 targets (1-hop)
2. For each target, fetches classification properties: P1149 (LCC), P244 (LCSH), P2163 (FAST), P227 (GND), P1036 (Dewey)
3. Builds a `position_map` dict with anchor_type, hops, confidence
4. Writes POSITIONED_AS edges from SubjectConcept → Entity/ClassificationAnchor
5. Writes PROVIDES_ANCHOR from SYS_FederationSource → anchor

**The classification data is fetched but discarded.** Lines 711–716 print LCC/LCSH/FAST IDs to stdout; they're in the position_map but never written as graph relationships.

---

## What Steps 2–4 need to do

### Step 2: LCC/LCSH/FAST linkage

**Input:** The `self_classification` dict and `parent_properties` already returned by Step 1.

**Logic:**

```
For self_classification (hops=0):
  if lcc value exists:
    MATCH (lcc:LCC_Class) where value falls in lcc.code range
    MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'primary', hops: 0}]->(lcc)
  if lcsh_id exists:
    MERGE (lcsh:LCSH_Subject {lcsh_id: value})
    ON CREATE SET lcsh.uri, lcsh.heading (fetch from id.loc.gov API)
    MERGE (sc)-[:HAS_LCSH_AUTHORITY]->(lcsh)
  if fast_id exists:
    MERGE (fast:FAST_Subject {fast_id: value})
    ON CREATE SET fast.uri, fast.preferred_label
    MERGE (sc)-[:HAS_FAST_AUTHORITY]->(fast)

For each parent_property (hops=1):
  if parent has lcc value:
    Find LCC_Class nodes where parent's lcc falls in code range
    MERGE (sc)-[:CLASSIFIED_BY_LCC {scope: 'cross_schedule', hops: 1, via_qid: parent_qid}]->(lcc)
```

**LCC range matching:** LCC_Class nodes have `code` (e.g. 'DG221-239'), `prefix` (e.g. 'DG'), `start` (221.0), `end` (239.0). A Wikidata LCC value like 'DG241' matches by: split prefix, parse number, find LCC_Class where prefix matches AND start <= number <= end.

**Key design point:** The LCC_Class hierarchy already has 4,490 nodes with BROADER_THAN edges. Step 2 links the SubjectConcept into this existing hierarchy — it does not create new LCC_Class nodes (unless a narrower node is missing, in which case it creates one and wires BROADER_THAN to the nearest existing parent).

### Step 3: Bibliography source binding

**Input:** The SubjectConcept's domain (inferred from POSITIONED_AS anchor_types) and the existing BibliographySource nodes in the graph.

**Logic:**

```
MATCH (bib:BibliographySource)
For each bib:
  Evaluate whether bib.domain_scope overlaps with sc's anchor_types
  If yes: MERGE (sc)-[:HAS_BIBLIOGRAPHY_AUTHORITY {scope, domain}]->(bib)
```

For the Roman Republic proof-of-concept this is trivial (DPRR covers persons, Broughton covers magistracies, Zmeskal covers families). For a general SCA, this needs a mapping table — D-table candidate:

| BibliographySource.id | anchor_type_match | scope |
|------------------------|-------------------|-------|
| DPRR | HistoricalPeriod + HistoricalCountry + qid_range(Q17167) | primary |
| Broughton_MRR | HistoricalPeriod + FormOfGovernment(republic) | secondary_academic |
| Zmeskal_Adfinitas | HistoricalPeriod + FormOfGovernment(republic) | secondary_academic |

This table is small and stable — could be a SYS_Policy or a simple config file read at agent startup.

### Step 4: Facet assignment

**Input:** The SubjectConcept's POSITIONED_AS anchors and CLASSIFIED_BY_LCC codes.

**Logic:** This is D8 (DETERMINE SFA facet assignment). The SCA should:

1. Read the LCC codes attached in Step 2
2. Map LCC prefix+range to candidate facets using the existing LCC→facet mapping in `output/neo4j/lcc_load.cypher`
3. Run D8 to filter forbidden facets (NoTemporalFacet, NoClassificationFacet)
4. Set `sc.primary_facet` and `sc.related_facets`

For Roman Republic:
- DG (History of Italy) → POLITICAL primary
- DG89 (Constitution), DG91 (Political institutions) → POLITICAL, LEGAL
- DG105 (Army) → MILITARY
- DG65 (Religion) → RELIGIOUS
- DG125 (Family) → SOCIAL
- KJA (Roman Law) → LEGAL
- CJ (Numismatics) → ECONOMIC

The mapping from LCC code prefix to facet should be a table (D-table candidate D35: DETERMINE LCC-to-facet mapping).

---

## Implementation approach

### Option A: Extend `sca_federation_positioning.py` (recommended)

Add three functions to the existing script:

```python
def write_authority_links(driver, seed_qid, position_map, self_classification):
    """Step 2: Write LCSH_Subject, FAST_Subject, CLASSIFIED_BY_LCC edges."""

def write_bibliography_bindings(driver, seed_qid, position_map):
    """Step 3: Wire SubjectConcept to BibliographySource nodes."""

def write_facet_assignments(driver, seed_qid, lcc_codes):
    """Step 4: Compute and write primary_facet + related_facets."""
```

Call them from `position_in_federated_schemas()` after the existing Step 4 write.

**Why extend rather than new script:** The data needed (self_classification, parent_properties, position_map) is already computed by Step 1. A separate script would re-fetch it.

### Option B: Separate `sca_academic_positioning.py`

A new script that takes a SubjectConcept subject_id, reads its POSITIONED_AS edges, and runs Steps 2–4. Cleaner separation but requires a graph read to recover what Step 1 already computed.

---

## subject_id mismatch fix

The bootstrap cypher uses `subj_roman_republic_q17167`. The SCA positioning script creates `subj_q17167`. This divergence happened because:

1. `bootstrap_subject_concept_agents.cypher` was written as a design doc with hand-chosen IDs
2. `sca_federation_positioning_write.py` generates subject_id as `subj_{qid}` programmatically

**Fix:** The programmatic convention (`subj_{qid}`) should be canonical. The bootstrap cypher should be updated to match, or (better) the bootstrap cypher should be deprecated in favour of the SCA script running Steps 1–4 end-to-end.

---

## Verification

After running the seed cypher or the eventual SCA Steps 2–4:

```cypher
MATCH (sc:SubjectConcept {qid: 'Q17167'})-[r]->(n)
RETURN type(r) AS rel, count(*) AS cnt ORDER BY cnt DESC
```

Expected:
| rel | count |
|-----|-------|
| CLASSIFIED_BY_LCC | 12+ (period + thematic + cross-schedule) |
| POSITIONED_AS | 6 (existing from Step 1) |
| HAS_BIBLIOGRAPHY_AUTHORITY | 3 (DPRR, Broughton, Zmeskal) |
| HAS_LCSH_AUTHORITY | 1 |
| HAS_FAST_AUTHORITY | 1 |
| STARTS_IN_YEAR | 1 |
| ENDS_IN_YEAR | 1 |
| HAS_SUBJECT_REGISTRY | 1 |

---

## Impact on family tree work

With the seed complete, persons inheriting from this SubjectConcept get:

1. **LCC classification context:** A person CITIZEN_OF Roman Republic → person's scholarly literature is in DG201-365 (and subdivisions). When a user asks "find me all scholarly works about this person," the system knows to search DG + KJA + CN.

2. **Bibliography authority scoping:** DPRR is the primary authority for Roman Republican persons. When federation scoring evaluates a person, DPRR evidence outranks Wikidata (per ADR-007 §8 authority tiers). The HAS_BIBLIOGRAPHY_AUTHORITY edge makes this traversable.

3. **Facet inheritance:** A person under POLITICAL primary facet with MILITARY, LEGAL, SOCIAL related facets → the SubjectFacetAgents know which lenses to apply when analysing that person's claims.

4. **Temporal range:** The SubjectConcept's 509 BCE – 27 BCE temporal tether gives D33 (temporal bridge track) a reference frame for validating family relationships. "Is a 200-year gap plausible?" depends on knowing the period span.
