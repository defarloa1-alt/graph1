# Prosopographic Federation Design
## Chrystallum Knowledge Graph — Authority Extension

---

## What changed and why

The original 10 federations cover identity (Wikidata), bibliography (WorldCat, MARC),
geography (Pleiades, GeoNames), time (PeriodO), concepts (LCSH, FAST, LCC), and
language (BabelNet). What was missing: a dedicated person authority for ancient history.

Wikidata covers named elites — emperors, consuls, generals. It does not cover the
social history layer: freedmen, soldiers, merchants, local officials, non-elite women,
provincial figures. For ancient historical research this is a significant gap.

Two live APIs fill it. One standard explains how they relate to each other and to
existing federations.

---

## The three additions

### 1. Trismegistos (`mode: api`)

**What it is:** KU Leuven's interdisciplinary portal for ancient world texts,
people, and places. BC 800 – AD 800, Eastern Mediterranean.

**Coverage:** 575,000+ person attestations. 64,000+ places. 964,000+ texts.
Includes Latin and Greek inscriptions, papyri, epigraphic material.

**Why it matters for Chrystallum:**
- Covers non-elite persons invisible in Wikidata
- Live JSON/RDF API with stable TM PER_IDs
- GeoRelations crossmatcher links TM place IDs to Pleiades (already federated)
  — this creates automatic crosswalk between Trismegistos and Pleiades
- TexRelations crossmatcher links to 79 partner projects
- CC BY-SA 4.0 license — fully open

**API endpoints:**
```
Person JSON : https://www.trismegistos.org/dataservices/per/index.php?id={id}&format=json
Person RDF  : https://www.trismegistos.org/dataservices/rdf/per/index.php?id={id}
Geo crossmatch: https://www.trismegistos.org/dataservices/georelations/{tm_geo_id}
Text crossmatch: https://www.trismegistos.org/dataservices/texrelations/{tm_id}
```

**Crosswalk path into Chrystallum:**
```
Entity (Wikidata QID)
  → Wikidata P1696 → TM PER_ID
  → Trismegistos PerResponder
  → person name, dates, place, attestations
  → TM Geo crossmatcher → Pleiades ID (already in graph)
```

---

### 2. LGPN (`mode: api`)

**What it is:** Lexicon of Greek Personal Names. Oxford University, British Academy
Major Research Project. Almost 400,000 ancient Greeks, 8 published volumes by region.

**Coverage:** Greek-speaking world from Marseilles to India, 8th c BCE – 6th c CE.
Sources: tombstones, dedications, civic decrees, treaties, inscriptions, papyri,
coins, graffiti.

**Why it matters for Chrystallum:**
- Strongest authority for Greek personal names with scholarly editorial control
- Stable URIs per person: `http://www.lgpn.ox.ac.uk/id/{volume}-{id}`
- OpenAPI-compliant programmatic access
- Complements Trismegistos: TM is stronger on documentary/papyrological sources,
  LGPN is stronger on literary/epigraphic Greek

**Crosswalk path into Chrystallum:**
```
Entity (Wikidata QID)
  → Wikidata P1838 → LGPN ID (format: V1-12345, V2-67890, etc.)
  → LGPN API → name, volume, region, dates, attestation sources
```

---

### 3. SNAP:DRGN (`mode: standard`)

**What it is:** Standards for Networking Ancient Prosopographies.
A UK AHRC-funded project (2014–2015) that produced an interchange format
and ontology for sharing person data between prosopographical projects.

**Critical fact:** The SNAP triplestore (650,000 records, 16M RDF triples)
is defunct. The service-level agreement expired. There is no live endpoint.

**What SNAP:DRGN provides IN Chrystallum:**
- The interchange standard that Trismegistos and LGPN both implement
- The `snap:Person`, `snap:Bond`, `snap:PersonalRelationship` ontology classes
- A conceptual bridge between prosopographic sources
- Recorded as `crosswalk_standard` on both Trismegistos and LGPN federation nodes

**What SNAP:DRGN does NOT provide:**
- A queryable endpoint
- Live URIs
- Any data not obtainable from Trismegistos or LGPN directly

SNAP lives in the graph as institutional knowledge — "these federations speak
the same language because they implement this standard."

---

## Updated Federation count

| Name          | Type           | Mode     | Coverage    |
|---------------|----------------|----------|-------------|
| Pleiades      | geographic     | local    | 41,993      |
| PeriodO       | temporal       | local    | 8,959       |
| Wikidata      | universal      | hub_api  | —           |
| GeoNames      | geographic     | hybrid   | —           |
| BabelNet      | linguistic     | api      | —           |
| WorldCat      | bibliographic  | api      | —           |
| LCSH          | conceptual     | local    | —           |
| FAST          | topical        | local    | —           |
| LCC           | classification | local    | —           |
| MARC          | bibliographic  | local    | —           |
| **Trismegistos** | **prosopographic** | **api** | **575,000** |
| **LGPN**      | **prosopographic** | **api** | **400,000** |
| **SNAP:DRGN** | **prosopographic** | **standard** | **0 (standard only)** |

Total: **13 federations** (10 original + 3 new)
FederationRoot count updates to 13 automatically via the Cypher.

---

## Pipeline integration

The crosswalk runs as an enrichment step AFTER cluster_assignment:

```
find_anchors → validate → harvest → facet_classify → cluster_assign
                                                          ↓
                                              prosopographic_crosswalk
                                                          ↓
                                              Entity nodes enriched with:
                                                - trismegistos_id
                                                - trismegistos_name
                                                - trismegistos_dates
                                                - trismegistos_place
                                                - lgpn_id
                                                - viaf_id
```

The crosswalk is opportunistic — it only enriches entities where Wikidata
carries P1696 (TM ID) or P1838 (LGPN ID). Coverage will be partial,
concentrated on named individuals who appear in both Wikidata and
prosopographic databases. That's the right coverage: exactly the persons
where cross-authority disambiguation is most valuable.

---

## Self-describing system implications

These federation additions should trigger a SystemDescription regeneration.
The bootstrap narrative gains:

- "Person authority coverage spans Wikidata (named elites), Trismegistos
  (575,000 documentary attestations), and LGPN (400,000 Greek personal names)"
- "Prosopographic federations implement the SNAP:DRGN interchange standard,
  enabling cross-project person disambiguation"
- "Geographic crosswalk: Trismegistos place IDs link to Pleiades via
  GeoRelations matcher, creating automatic bridge between person and place authorities"

This is the graph describing its own authority coverage in terms a scholar
would recognize and trust.

---

## Design decisions recorded

| Decision | Rationale |
|----------|-----------|
| SNAP:DRGN as standard not federation | Triplestore defunct; SNAP is an interchange format, not a data source |
| Trismegistos over PIR/RE directly | Live API, open license, broadest coverage; PIR/RE have no machine-readable API |
| LGPN included separately from TM | Different source base (epigraphic/literary vs documentary), different IDs, both valuable |
| Crosswalk via Wikidata P-properties | Wikidata already carries TM and LGPN IDs for well-known persons — no new matching logic needed |
| Enrichment not bulk import | TM has 575,000 records; bulk import would flood graph with unrelated data. Targeted enrichment of entities already in the graph is correct. |
