# Geo Agent — Design Document for Review

**Version:** Draft  
**Date:** 2026-03-06  
**Status:** For review (design validated; delta-based write path adopted)

---

## Review Summary

Design validated as strong; aligns with backbone-first, settlement-centric approach. Key strengths: graph as source of truth, federation score as operational filter, incremental script-backed pipeline, backlink harvesting from domain QID, approximate federation with confidence scoring, Place/PlaceGeometry/PlaceName logical model. Write path: keep MCP read-only; Geo Agent returns structured deltas; Python delta applier validates and applies.

---

## Executive Summary

The **Geo Agent** is responsible for building and maintaining the geographic backbone of the Chrystallum graph. It starts from a thinly populated backbone (Pleiades + crosswalk) and expands it by discovering geo-type items from Wikidata backlinks, federating them to Place nodes, and enriching with coordinates, geoshapes, and admin hierarchy. Once the backbone is sufficiently populated, the Subject Facet Agent (SFA) can train on geography and make claims about the geographical facets of the Roman Republic.

---

## 1. The Geographic Backbone

### 1.1 Definition

The **geo backbone** = Place nodes with `place_scope = 'v1_core'` (settlements, regions, villas, forts, colonies, etc.). It provides:

- **Identity** — Stable Place nodes across time
- **Temporal resolution** — Names and geometries with date ranges
- **Admin hierarchy** — town → city → region → country via `LOCATED_IN`
- **Cross-authority links** — Pleiades, GeoNames, Wikidata

### 1.2 Federation Score

A Place has a **high federation score** when it has:

| Dimension | Property / Edge |
|-----------|-----------------|
| Pleiades | `pleiades_id` |
| GeoNames | `geonames_id` |
| Wikidata | `qid` |
| Temporal backbone | PlaceName / PlaceGeometry with `start_year` / `end_year` |
| Geographic backbone | `LOCATED_IN` → town → city → region → country |

This combination creates a strong **federation signature** — the place is well-anchored across authorities and suitable for agent reasoning.

### 1.3 Current State: Thinly Populated

The backbone is currently **thin**:

- Pleiades foundation exists (~44k Place nodes)
- Crosswalk provides some geonames_id and qid
- Many geo-type items from Wikidata backlinks are **not yet** in the graph

The Geo Agent must **build out** the backbone when it encounters new items.

---

## 2. Agent as Guardrail

### 2.1 Graph as Source of Truth

The agent does **not** rely on LLM world knowledge for geography. Instead:

- It **queries the graph** for Place identity and hierarchy
- It **traverses** `LOCATED_IN` to resolve town → city → region → country
- Its answers are **grounded** in graph data

The backbone is the **guardrail**: the agent's mapping comes from the graph, not from internal model knowledge.

### 2.2 Bootstrap Loop

When the agent discovers a geo-type item that has no Place node:

```
Discover geo item (no Place) → Create Place node → Enrich from Wikidata → Add LOCATED_IN → Backbone grows
```

The agent both **enriches** existing Places and **creates** new ones.

---

## 3. Process Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 1: Establish initial backbone (Pleiades + crosswalk + federation)     │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 2: Domain QID (Roman Republic) → Traverse backlinks                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 3: Filter for geo-type data (P625, P131, P17, P3896, P1584, P1566)   │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 3b: Geo Agent (LLM) — Classify candidates, propose deltas             │
│  Script gathers; LLM reasons (place vs event); Python applier writes         │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 4: Delta Applier → Create/enrich Place nodes from Geo Agent output    │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 5: Full property harvest (coords, geoshapes, temporal qualifiers)    │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Result: Expanded Place backbone → SFA can train on geography               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Revised Pipeline: LLM in the Loop

| Step | Component | Role |
|------|-----------|------|
| 1 | `geo_backlink_discovery.py` | Gather backlinks, filter by geo properties; output JSON bundle |
| 2 | **Geo Agent (LLM)** | Classify candidates (place_core, place_noncore, event, other); propose deltas |
| 3 | Delta Applier (Python) | Apply CREATE_OR_ENRICH_PLACE to Neo4j |
| 4 | Event Agent (later) | Consume ATTACH_EVENT_TO_PLACE deltas |

**Why the LLM:** The script cannot generalize that "ancient city" and "archaeological site" are Place-like while "battle" and "civil war" are Events. The LLM does ontological reasoning; the applier maintains invariants.

---

## 4. Phase 1: Establish the Backbone

**Prerequisites and pipeline** (see `Geographic/FEDERATION_HAPPY_PATH.md`):

| Step | Script | Effect |
|------|--------|--------|
| 1 | `build_pleiades_geonames_crosswalk.py` | Pleiades → GeoNames mapping |
| 2 | `build_geonames_wikidata_bridge.py` | GeoNames → Wikidata; merged crosswalk |
| 3 | `enrich_places_from_crosswalk.py` | Place.geonames_id, Place.qid, Place.tgn_id |
| 4 | `link_place_admin_hierarchy_geonames.py` | GeoNames parents; LOCATED_IN |
| 5 | `link_place_admin_hierarchy.py` | Wikidata P131/P17 parents; LOCATED_IN |
| 6 | `enrich_places_from_wikidata_geo.py` | P625, P3896, coords, geoshapes |
| 7 | `link_pleiades_place_to_geo_backbone.py` | ALIGNED_WITH_GEO_BACKBONE |

**Result:** Agent can map each Pleiades row to backbone via graph queries.

---

## 5. Phase 2–3: Backlink Discovery and Geo Filter

**Input:** Domain QID (e.g. Q17167 = Roman Republic)

**Process:**

1. **Query Wikidata backlinks** — Items that reference the domain via P31, P279, P361, P1344, P793, P17, P131, etc.

2. **Filter for geo-type data** — Keep items with any of:
   - **P625** — coordinate location
   - **P131** — located in administrative entity
   - **P17** — country
   - **P3896** — geoshape (key for regions; can be time-spanned)
   - **P1584** — Pleiades ID
   - **P1566** — GeoNames ID
   - **P276** — location
   - **P706** — located in/on physical feature

3. **Output:** Candidate QIDs — potential Place-like entities to add to the backbone.

---

## 6. Phase 4: Federation Path per Candidate

For each candidate QID:

| Has | Action |
|-----|--------|
| **P1584** | Link to existing Place by `pleiades_id`; enrich if missing |
| **P1566** | Link to GeoNames backbone; create Place(geonames_id) if needed |
| **P625** | Set lat/long; create PlaceGeometry if temporal qualifiers (P580/P582/P585) |
| **P3896** | Set geoshape_commons; create PlaceGeometry with start_year/end_year |
| **P131** | Create LOCATED_IN edges to parent Place |
| **P17** | Set country_qid |

### 6.1 Approximation Match (No Direct Link)

When candidate has **no** P1584 or P1566:

1. **Label search** — Wikidata Search API by place name
2. **Coordinate proximity** — SPARQL for items with P625 within radius
3. **Hierarchy constraint** — If P131 parent has qid, search in that region
4. **Confidence score** — Combine label match + coord distance + hierarchy overlap
5. **Propose qid** — Above threshold (e.g. 0.9): auto-suggest; below: flag for review

---

## 7. Phase 5: Full Property Harvest

For each discovered Place, the agent gathers **all** relevant Wikidata properties:

### 7.1 Geographic Properties

| PID | Name |
|-----|------|
| P625 | coordinate location |
| P3896 | geoshape |
| P131 | located in administrative entity |
| P17 | country |
| P30 | continent |
| P36 | capital |
| P276 | location |
| P706 | located in/on physical feature |
| P47 | shares border with |
| P1376 | capital of |
| P421 | located in timezone |
| P150 | contains administrative entity |

### 7.2 External Identifiers

| PID | Name |
|-----|------|
| P1566 | GeoNames ID |
| P1584 | Pleiades ID |
| P1667 | Getty TGN ID |
| P214 | VIAF |
| P227 | GND |
| P244 | LCNAF |
| P402 | OpenStreetMap ID |

### 7.3 Temporal Qualifiers

| PID | Name | Used with |
|-----|------|-----------|
| P580 | start time | P625, P3896 |
| P582 | end time | P625, P3896 |
| P585 | point in time | P625, P3896 |

**Geoshape is key:** Multiple P3896 statements with qualifiers → multiple PlaceGeometry nodes with `start_year`/`end_year` for time-slider maps.

---

## 8. Logical Model Integration

- **Place** — Identity anchor (stable across time)
- **PlaceGeometry** — One node per P625 or P3896 with P580/P582/P585 qualifiers
- **PlaceName** — From Wikidata labels/aliases (future: temporal names)
- **LOCATED_IN** — Admin hierarchy from P131/P17

---

## 9. Downstream: SFA Training

Once the backbone is sufficiently populated:

- The **Subject Facet Agent (SFA)** can begin general training in geography
- The SFA can make claims about the **geographical facets of the Roman Republic**
- Grounded in the expanded Place backbone

---

## 10. Related Documents

| Document | Purpose |
|----------|---------|
| `Geographic/FEDERATION_HAPPY_PATH.md` | Phase 1 pipeline; happy/unhappy path |
| `Geographic/GEO_EXPANSION_PROCESS.md` | Detailed expansion phases |
| `Geographic/GEO_AGENT_DELTA_SCHEMA.md` | Geo Agent delta types and output format |
| `md/Agents/geo_agent_classification_prompt.md` | Geo Agent prompt (classification + deltas) |
| `scripts/agents/geo/README.md` | Geo Agent overview |
| `Geographic/LOGICAL_MODEL.md` | Place, PlaceGeometry, PlaceName |
| `Key Files/chrystallum_geographic_constitution.jsx` | GEO_RULES, GEO_FED, agent bootstrap |

---

## 11. Graph Read/Write Model

### 11.1 Current State

| Path | Mechanism | Capability |
|------|------------|------------|
| **Read** | MCP `run_cypher_readonly` | MATCH only; 500 char limit; 500 row cap |
| **Write** | Python scripts (neo4j driver) | Full CREATE/MERGE/SET; batch jobs |

The LLM (Geo Agent, SFAs) is **read-only** at the graph level. All mutation is via Python scripts.

### 11.2 Recommended: Delta-Based Writes

**Keep MCP read-only.** Do not expose `run_cypher_mutation` to the LLM.

**Geo Agent (and SFAs) return structured deltas, not Cypher:**

| Delta type | Purpose |
|------------|---------|
| `CREATE_OR_ENRICH_PLACE` | New Place node or enrich existing (keyed by pleiades_id, geonames_id, or qid) |
| `ATTACH_EVENT_TO_PLACE` | Event→Place relationship (OCCURRED_AT); for Event Agent later |
| `CREATE_GEOMETRY` | PlaceGeometry node with temporal bounds (future) |
| `CREATE_LOCATED_IN` | LOCATED_IN edge (future) |

See `Geographic/GEO_AGENT_DELTA_SCHEMA.md` and `md/Agents/geo_agent_classification_prompt.md` for the Geo Agent output format.

Deltas are JSON; they do not touch Neo4j directly.

**Delta applier (Python script):**

1. Reads batch of deltas from file/queue
2. Validates (ID strategy, place_scope rules, federation thresholds)
3. Translates to Cypher CREATE/MERGE/SET via neo4j driver
4. Optional: human review for low-confidence or high-impact deltas

**Rationale:**

- LLM = proposes; Python = enforces invariants and writes
- Audit trail: each applied delta logged with agent and justification
- Later: wrap delta applier as MCP tool if autonomous online updates are desired

---

## 12. Gaps / Open Questions (Tightened)

1. **Confidence thresholds & review workflow** — Concrete numbers; store for "candidate matches awaiting review" so SFAs don't treat low-confidence links as facts.
2. **Place creation policy** — Encode preference order: prefer Pleiades-anchored when ancient; prefer GeoNames-anchored when modern; allow dual anchoring if both exist.
3. **place_scope = 'v1_core' scope** — Explicitly: v1 focuses on settlements and immediate political centers; natural features (rivers, coasts) only when required by use case.
4. **SFA handoff criterion** — Metric: e.g. "≥ X% of Pleiades settlements relevant to Roman Republic have federation score ≥ Y" before SFAs treat geography as reliable facet.
5. **Delta schema** — ✅ Defined in `Geographic/GEO_AGENT_DELTA_SCHEMA.md` (CREATE_OR_ENRICH_PLACE, ATTACH_EVENT_TO_PLACE). Future: CREATE_GEOMETRY, CREATE_LOCATED_IN in same style as SFA graph deltas.
