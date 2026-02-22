# Geographic Consolidation

## Canonical Files
- `Geographic/COORDINATES.out` (Getty TGN raw coordinates source)
- `Geographic/TERM.out` (Getty TGN raw term/name source)
- `Geographic/ASSOCIATIVE_RELS.out` (TGN relationship source table)
- `Geographic/ASSOCIATIVE_RELS_TYPE.out` (relationship type lookup)
- `Geographic/CONTRIB.out` (contributor source table)
- `Geographic/CONTRIB_RELS_NOTE.out` (contributor-note links)
- `Geographic/CONTRIB_RELS_SUBJECT.out` (contributor-subject links)
- `Geographic/CONTRIB_RELS_TERM.out` (contributor-term links)
- `Geographic/LANGUAGE_RELS.out` (language linkage table)
- `Geographic/PTYPE_ROLE.out` (place-type role lookup)
- `Geographic/PTYPE_ROLE_RELS.out` (place-type role relations)
- `Geographic/REVISION_HISTORY_SOURCE.out` (source revision history)
- `Geographic/SCOPE_NOTES.out` (scope notes/definitions)
- `Geographic/SOURCE.out` (source/citation table)
- `Geographic/SOURCE_RELS_NOTE.out` (source-note links)
- `Geographic/SOURCE_RELS_SUBJECT.out` (source-subject links)
- `Geographic/SOURCE_RELS_TERM.out` (source-term links)
- `Geographic/SUBJECT.out` (subject table)
- `Geographic/SUBJECT_MERGE.out` (subject merge mapping)
- `Geographic/SUBJECT_RELS.out` (subject relations)
- `Geographic/ontology.rdf` (Getty ontology reference)
- `Geographic/geographic_registry_master.csv` (curated place-to-facet mapping; renamed from `label,qid,preferred_label,score,match_in.csv`)
- `Geographic/tgn_7011179-place.rdf` (sample TGN RDF payload for structure reference)
- `Geographic/geographic_hierarchy.png` (visual reference)

## Archived Files
- `Archive/Geographic/Neo4j.md` (stub outline; no executable or canonical content)
- `Archive/Geographic/geo chat 2.js` (chat/prototype notes, superseded by Facets canonical assets)
- `Archive/Geographic/Facets creation.lua` (facet prototype script; belongs to Facets workstream)
- `Archive/Geographic/Facets Subclasses.md` (facet decomposition prompt notes)
- `Archive/Geographic/perplexity change on geo.md` (process narrative notes)
- `Archive/Geographic/Populate Vectors.txt` (planning note)

## Why This Set
- The `.out` files are the authoritative Getty export snapshot and should remain intact as base ingestion material.
- `ontology.rdf` and sample RDF support semantic mapping and parser validation.
- `geographic_registry_master.csv` is the only curated file in this directory with explicit classification value.
- Archived files are mostly chat/process drafts and are not runtime dependencies.

## Ideas Captured Beyond Current Golden Architecture
- Regionalized temporal truth for period labels should be modeled as `(period_qid, region_qid) -> bounds` rather than one global date range per period.
- Geographic facet assignment can be explicitly split into `pure_spatial`, `political`, and `cultural_geographic` classes (already present in `geographic_registry_master.csv` data).
- CIDOC mapping opportunity: represent geographic/demographic facet concepts as `E55 Type`, and quantitative measures as `E54 Dimension`.

## Follow-up Risk
- `Python/extract_getty_tgn_places.py` currently assumes wrong source columns for both `COORDINATES.out` and `TERM.out`. It should be corrected before relying on its output.
