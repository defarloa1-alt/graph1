# Unmapped Edges Analysis

**Total PID edges:** 21,229
**Canonicalized (in registry):** 16,901 (79.6%)
**Unmapped:** 4,328 (20.4%)

## Top Unmapped PIDs by Edge Count

| PID | Edge Count | Action |
|-----|------------|--------|
| P6104 | 312 | Add to registry if Wikidata property |
| P5008 | 228 | Add to registry if Wikidata property |
| P190 | 172 | Add to registry if Wikidata property |
| P2348 | 144 | Add to registry if Wikidata property |
| P6216 | 137 | Add to registry if Wikidata property |
| P156 | 110 | Add to registry if Wikidata property |
| P155 | 109 | Add to registry if Wikidata property |
| P937 | 109 | Add to registry if Wikidata property |
| P36 | 103 | Add to registry if Wikidata property |
| P1269 | 101 | Add to registry if Wikidata property |
| P1376 | 85 | Likely historian-level; CRM cross-ref |
| P123 | 81 | Likely historian-level; CRM cross-ref |
| P291 | 76 | Likely historian-level; CRM cross-ref |
| P1552 | 72 | Likely historian-level; CRM cross-ref |
| P1622 | 63 | Likely historian-level; CRM cross-ref |
| P2853 | 60 | Likely historian-level; CRM cross-ref |
| P460 | 59 | Likely historian-level; CRM cross-ref |
| P103 | 58 | Likely historian-level; CRM cross-ref |
| P205 | 58 | Likely historian-level; CRM cross-ref |
| P403 | 57 | Likely historian-level; CRM cross-ref |

## Interpretation

- **ADMIN_NOISE (P971, P6104, P5008, P6216):** Wikimedia category/curation metadata. Do not add to registry.
- **High-frequency unmapped (e.g. >500 edges):** Likely Wikidata PIDs not yet in registry. Add to `relationship_types_registry_master.csv`.
- **Low-frequency unmapped:** Likely Chrystallum-native historian predicates (220 in `registry_unmapped_to_wikidata.txt`). Need CRM/CRMinf cross-ref at type level; 19% canonicalization ceiling until RelationshipType work.

**Registry:** 65 PIDs mapped. **Historian types:** 220 in unmapped list.