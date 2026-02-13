# Facet Consolidation

## Canonical Files
- `Facets/facet_registry_master.json`
- `Facets/facet_registry_master.csv`
- `Facets/facet_node_schema_proposal.md`
- `Facets/star-pattern-claims.md`
- `Facets/Scripts/period_facet_tagger.py`

## Archived Files
- `Archive/Facets/Latest Facets.raw.json`
- `Archive/Facets/Ref facets.raw.json`
- `Archive/Facets/Ref_Anchors.raw.json`
- `Archive/Facets/facet_nodes_extended.csv`
- `Archive/Facets/facet_links_extended.csv`
- `Archive/Facets/future anchor decomp.csv`
- `Archive/Facets/facets.periodo_importer_snapshot.txt`

## Registry Summary
- Facets consolidated: 16
- Anchor rows consolidated: 86
- Facets with quality flags: 15
- Source precedence: latest > ref > anchors

## Notes
- `Latest Facets.json` and `Ref facets.json` were prefixed with non-JSON text; parsed from first JSON token.
- `Ref_Anchors.json` contains malformed trailing structure; only first valid JSON block was used.
- `period_facet_tagger.py` now resolves paths robustly and supports optional output path.

