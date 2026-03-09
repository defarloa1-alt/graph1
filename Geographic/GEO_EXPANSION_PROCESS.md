# Geographic Expansion Process

**Purpose:** Expand Place coverage beyond the Pleiades backbone by traversing Wikidata backlinks from a domain anchor (e.g. Roman Republic) and harvesting items with geographic data.

---

## Overview

```
Domain QID (Roman Republic)
    → Traverse backlinks
    → Filter for geo-type data
    → Enrich & federate
    → Expanded Place backbone
```

---

## Phase 1: Establish the Backbone

**Prerequisites** (from FEDERATION_HAPPY_PATH.md):

1. Pleiades import → Place nodes with `pleiades_id`
2. Crosswalk build → `pleiades_geonames_wikidata_tgn_crosswalk_v1.csv`
3. Enrich from crosswalk → `Place.geonames_id`, `Place.qid`, `Place.tgn_id`
4. GeoNames hierarchy → `link_place_admin_hierarchy_geonames.py`
5. Wikidata hierarchy → `link_place_admin_hierarchy.py`
6. Wikidata geo enrichment → `enrich_places_from_wikidata_geo.py`
7. Link Pleiades_Place → Place → `link_pleiades_place_to_geo_backbone.py`

**Result:** Place backbone with pleiades + geonames + wikidata + temporal + geographic hierarchy. Agent can map each Pleiades row to backbone via graph queries.

---

## Phase 2: Backlink Discovery

**Input:** Domain QID (e.g. Q17167 = Roman Republic)

**Exploratory script (minimal constraints):**

```bash
python scripts/backbone/geographic/geo_backlink_discovery.py --seed Q17167
# Output: output/geo_discovery/Q17167_geo_candidates.json
```

Run first to see what it returns; then assess quality and add constraints.

**Process:**

1. **Query Wikidata backlinks** — Items that reference the domain via:
   - P31 (instance of)
   - P279 (subclass of)
   - P361 (part of)
   - P1344 (participated in)
   - P793 (significant event)
   - P17 (country), P131 (located in) — when domain is a place
   - Other relevant predicates

2. **Filter for geo-type data** — Among backlinks, keep items with any of:
   - P625 (coordinate location)
   - P131 (located in administrative entity)
   - P17 (country)
   - P3896 (geoshape)
   - P1584 (Pleiades ID)
   - P1566 (GeoNames ID)
   - P276 (location)
   - P706 (located in/on physical feature)

3. **Output:** Candidate QIDs with geo properties — potential Place-like entities.

---

## Phase 3a: Geo Agent (LLM) Classification

**Input:** JSON from `geo_backlink_discovery.py` (seed + candidates with qid, label, instance_of, subclass_of, geo_properties).

**Process:**

1. **Classify** each candidate as `place_core`, `place_noncore`, `event`, or `other`.
2. For **place_core** / **place_noncore**: propose `CREATE_OR_ENRICH_PLACE` deltas (keyed by P1584, P1566, or qid).
3. For **event**: propose `ATTACH_EVENT_TO_PLACE` deltas (event→place from P276); no new Place nodes.
4. For **other**: no deltas.

**Output:** Classification + deltas JSON. See `md/Agents/geo_agent_classification_prompt.md` and `Geographic/GEO_AGENT_DELTA_SCHEMA.md`.

---

## Phase 3b: Delta Applier (Python)

For each `CREATE_OR_ENRICH_PLACE` delta from the Geo Agent:

| place_key | Action |
|-----------|--------|
| **pleiades_id** | Lookup Place by `pleiades_id`; MERGE or CREATE; set properties |
| **geonames_id** | Lookup Place by `geonames_id`; MERGE or CREATE; set properties |
| **qid** (no external IDs) | Create Place keyed by qid; set coords, label, base_type_hint |

For `ATTACH_EVENT_TO_PLACE`: store event→place for Event Agent; do not create Place nodes.

---

## Phase 4: Approximation Match (No Direct Link)

When candidate has **no** P1584 or P1566:

1. **Label search** — Wikidata Search API by place name
2. **Coordinate proximity** — SPARQL for items with P625 within radius of candidate coords
3. **Hierarchy constraint** — If P131 parent has qid, search for items in that region
4. **Confidence score** — Combine label match + coord distance + hierarchy overlap
5. **Propose qid** — Above threshold (e.g. 0.9): auto-suggest; below: flag for review

---

## Phase 5: Logical Model Integration

For time-spanned data:

- **PlaceGeometry** — One node per P625 or P3896 with P580/P582/P585 qualifiers
- **PlaceName** — From Wikidata labels/aliases (future: temporal names)
- **LOCATED_IN** — Admin hierarchy from P131/P17

Geoshape is key: multiple P3896 statements with qualifiers → multiple PlaceGeometry nodes with `start_year`/`end_year` for time-slider maps.

---

## Phase 6: Agent Gathers All Properties

For each discovered Place:

1. **Fetch full entity** — `wbgetentities` with `props=labels|descriptions|aliases|claims|sitelinks`
2. **Parse claims** — P625, P3896, P131, P17, P30, P36, P276, P706, P47, P1376, P421, P150, P31, P279, P361
3. **External IDs** — P1566, P1584, P1667, P214, P227, P244, P402, etc.
4. **Temporal qualifiers** — P580, P582, P585 on all geo claims
5. **Map to graph** — Place properties, PlaceGeometry, PlaceName, LOCATED_IN

---

## Summary Flow

```
1. Domain QID (Roman Republic)
2. Backlinks → filter geo-type
3. Candidate QIDs (JSON bundle)
4. Geo Agent (LLM): classify (place/event/other), propose deltas
5. Delta Applier: apply CREATE_OR_ENRICH_PLACE to Neo4j
6. Enrich: full property harvest, temporal geoshapes
7. Expanded Place backbone
```

---

## Federation Score

Place with **pleiades + geonames + wikidata + temporal + geographic backbone** = high federation score.

Expansion adds places that:
- Have geo data but no Pleiades ID (Wikidata-first)
- Are in Roman Republic context (domain-scoped)
- Can be linked via approximation when no direct crosswalk

---

## Related

- [FEDERATION_HAPPY_PATH.md](FEDERATION_HAPPY_PATH.md) — Phase 1 pipeline
- [LOGICAL_MODEL.md](LOGICAL_MODEL.md) — Place, PlaceGeometry, PlaceName
- [chrystallum_geographic_constitution.jsx](../Key%20Files/chrystallum_geographic_constitution.jsx) — GEO_RULES, GEO_FED
