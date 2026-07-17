# scripts/v2 — DEPRECATED (Chrystal 2.0)

**Do not use against the canonical Chrystallum graph.**

These scripts targeted Aura instance `0da8c4a3` (Chrystal 2.0), deprecated 2026-07-14.
Canonical Neo4j: `ac63a8e5`. See `docs/DEPRECATED_CHRYSTAL_2.0.md`.

| Script | Was for |
|--------|---------|
| `facet_registry.py` | FacetRegistry bootstrap |
| `facet_curriculum.py` | Facet → DisciplineSource edges |
| `curriculum_topics.py` | CurriculumTopic nodes |
| `write_curricula_graph.py` | Full curriculum graph write |
| `wiki_concept_map.py` | Wikipedia section → concept harvest |
| `classify_concept_map.py` | Predicate classification |
| `write_concept_graph.py` | WikiConcept layer write |
| `domain_bootstrap.py` | Domain → ACTIVATES → CurriculumTopic |

**Still useful offline:** `output/wiki_concept_maps/*_classified.json` — re-route through DI / canonical ingest if concept maps are needed again.
