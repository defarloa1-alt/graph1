# Domain Initiator (DI)

Harvest both directions from a seed QID, classify by facet, produce per-facet deltas for the SCA.

## Rule

**Never pass PID or QID without its label.** All output includes `label` alongside `pid` and `value_label` alongside `value_qid`.

## Pipeline

```
harvest.py  -->  {seed}_di_harvest.json  (full universe: forward + backward links)
                       |
classify.py -->  {seed}_di_classify.json (per-facet deltas for SCA routing)
                       |
                  SCA router  -->  18 SFAs
```

## Harvest

```bash
python scripts/agents/domain_initiator/harvest.py --seed Q17167
```

**Output:** `output/di_harvest/Q17167_di_harvest.json`

Harvests both link directions from the seed QID to create the full Wikidata universe:

- **Forward links** (seed --> X): entities the seed points to, tagged with connecting PID+label (e.g. P793 "significant event" --> Punic Wars, P36 "capital" --> Rome)
- **Backlinks** (X --> seed): entities that reference the seed via P31/P279/P361/P1344/P793/P17/P131/P276/P706
- **Both**: entities linked in both directions
- **Subject backbone**: FAST, Dewey, LCNAF from seed + all candidates
- **External IDs**: Pleiades, GeoNames, VIAF, GND, FAST, Dewey, LCNAF on every candidate

Each candidate carries: qid, label, link_direction, connecting_properties (for forward), instance_of, subclass_of, geo_properties, external_ids, recommended_actions.

Re-running periodically produces a diff: new QIDs, new federation anchors, new backbone links.

### Q17167 stats

109 candidates (29 forward + 75 backlink + 5 both), 39 backbone links (18 LCNAF + 14 Dewey + 7 FAST), 571 PIDs resolved, 1102 QID labels resolved.

## Classify

```bash
python scripts/agents/domain_initiator/classify.py --harvest output/di_harvest/Q17167_di_harvest.json
```

**Output:** `output/di_classify/Q17167_di_classify.json`

Three-tier routing:

1. **Tier 1 (type match)**: instance_of/subclass_of QIDs + self-QID matched against facet registry anchors + domain-specific type extensions (weight 8x)
2. **Tier 2 (property)**: PIDs on geo_properties matched against SYS_PropertyMapping from graph (falls back to static map). Deduplicated by PID per facet. (weight 1x)
3. **Tier 3 (federation)**: external ID PIDs matched against federation source routing table (weight 2x)

Output structure:
- `subject_resolution`: domain tether (LCSH) + sub-subjects from backbone
- `facet_deltas[]`: per-facet bundles with candidates (primary/secondary), federation sources, evidence signals
- `temporal_entities`: period subdivisions (not routed to SFA)
- `classification_summary`: counts for audit

### Q17167 stats

15 facets activated, 96 routed, 11 temporal, 2 unrouted. Military 19p, Economic 27p, Political 10p, Geographic 29p+62s, Linguistic 2p, Religious 1p.

## Discipline Traversal & Corpus Discovery

The harvest traverses from the seed QID to academic disciplines, then discovers corpus endpoints for SFA training.

### Traversal path

```
Seed QID
  → P361 (part of), P31 (instance of), P279 (subclass of), P2348 (time period)
    → hop-2 P361 from those targets
      → P2579 (studied in) on all context parents
        → academic disciplines
          → P527 (has part) = sub-disciplines
          → P279 children = specialized fields
```

Each discipline carries authority IDs (LCSH, Dewey, FAST, LCC) harvested from Wikidata.

### Corpus endpoints (14 sources)

| Source | Query type | Description |
|--------|-----------|-------------|
| **OpenAlex** | topic+keyword | Academic works ranked by citations (probed live) |
| **Internet Archive** | LCSH subject | Full-text books, especially pre-1928 public domain (probed live) |
| **Open Library** | subject+keyword | Open-access book metadata and lending (probed live) |
| **WorldCat** | LCSH subject | Global library holdings |
| **Perseus** | keyword | Classical primary sources with full text |
| **JSTOR** | keyword | Academic journal articles |
| **Google Books** | LCSH subject | Book metadata and previews |
| **HathiTrust** | OCLC+LCSH | Digitized library collections |
| **Open Syllabus** | keyword | Most-assigned academic texts by field |
| **Wikidata P921** | SPARQL | Works whose main_subject = seed or discipline QID |
| **Library of Congress** | LCSH ID | Authority records, subject heading hierarchy |
| **FAST** | FAST ID | Faceted subject headings from OCLC |
| **VIAF** | keyword | Virtual authority file linking national libraries |
| **GND** | keyword | German authority file with subject relationships |

### Q17167 stats

4 disciplines (ancient history, classical philology, Classical Greek and Roman history, Roman studies) + 10 sub-disciplines (incl. history of ancient Rome, papyrology, Latin studies, Roman historiography). 4 LCSH IDs, 3 Dewey codes harvested. OpenAlex: 7,309 works; Internet Archive: 309 texts; Open Library: 121 books.

### SFA training flow

Each SFA receives its facet delta (candidates + signals) AND the corpus endpoints. It filters the corpus by its facet keywords, trains on the top works, then evaluates candidates with disciplinary grounding.

## Cipher Address Space

The harvest creates a complete cipher manifest for the domain. Each candidate is addressable as `QID + PID + value_QID = deterministic cipher key`. The classifier partitions this address space by facet -- each SFA gets its subset and jumps O(1) to its assigned vertices.

## Related

- `docs/DOMAIN_INITIATOR.md` -- architecture
- `docs/SCA_SFA_CONTRACT.md` -- SCA / SFA division of labor
- `Facets/facet_registry_master.json` -- 18 canonical facets (anchor QIDs for Tier 1)
- `scripts/sca/build_subject_schema.py` -- LLM-based SubjectConcept proposal (detached, not consuming harvest)
- `scripts/sca/write_subject_concepts.py` -- writes SubjectConcepts to Neo4j
