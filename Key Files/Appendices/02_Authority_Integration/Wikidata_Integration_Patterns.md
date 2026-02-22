# Appendix K: Wikidata Integration Patterns

**Version:** 3.2 Decomposed  
**Date:** February 19, 2026  
**Source:** Extracted from Consolidated Architecture Document

---

## Navigation

**Main Architecture:**
- [ARCHITECTURE_CORE.md](../../ARCHITECTURE_CORE.md)
- [ARCHITECTURE_ONTOLOGY.md](../../ARCHITECTURE_ONTOLOGY.md)
- [ARCHITECTURE_IMPLEMENTATION.md](../../ARCHITECTURE_IMPLEMENTATION.md)
- [ARCHITECTURE_GOVERNANCE.md](../../ARCHITECTURE_GOVERNANCE.md)

**Appendices Index:** [README.md](../README.md)

---

# **Appendix K: Wikidata Integration Patterns**

## **K.1 Scope**

Normative federation architecture is defined in Section 4.4 and Section 8.6. This appendix provides operational query patterns.

## **K.2 Authoritative Files**

- `md/Architecture/Wikidata_SPARQL_Patterns.md`
- `md/Architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`

## **K.3 Core SPARQL Patterns**

### Direct property bundle resolution

```sparql
SELECT ?lcsh ?fast ?lcc ?viaf ?tgn ?pleiades ?trismegistos WHERE {
  BIND(wd:Q1048 AS ?item)
  OPTIONAL { ?item wdt:P244  ?lcsh }
  OPTIONAL { ?item wdt:P2163 ?fast }
  OPTIONAL { ?item wdt:P1149 ?lcc }
  OPTIONAL { ?item wdt:P214  ?viaf }
  OPTIONAL { ?item wdt:P1667 ?tgn }
  OPTIONAL { ?item wdt:P1584 ?pleiades }
  OPTIONAL { ?item wdt:P1958 ?trismegistos }
}
```

### Backlink enrichment (reverse-link context expansion)

```sparql
SELECT ?source ?sourceLabel ?property ?propertyLabel WHERE {
  BIND(wd:Q1048 AS ?target)
  ?source ?property ?target .
  VALUES ?property { wdt:P710 wdt:P1441 wdt:P138 wdt:P112 }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 500
```

## **K.4 Pipeline Contract**

1. Resolve label -> QID.
2. Pull authority property bundle.
3. Optionally run backlink expansion for context discovery.
4. Classify results by source entity type (`P31`, bounded `P279`) and ingest with provenance.
5. Route every statement through the dispatcher (`datatype + value_type`).
6. Apply the temporal precision gate before temporal anchoring.
7. Apply the frontier eligibility guard before recursive expansion.
8. Quarantine unsupported or malformed statements with explicit reason.

## **K.5 Property Lookup Contract (Reference-Book Pattern)**

Chrystallum MUST NOT ingest the full Wikidata property universe as graph nodes for runtime reasoning.  
Use a tool-backed property catalog lookup pattern instead (local reference store + deterministic filtering).

### Authoritative lookup assets

- `Relationships/relationship_types_registry_master.csv` (approved canonical mappings first)
- `CSV/wikiPvalues.csv` (Wikidata property catalog)
- `scripts/tools/enrich_wikidata_properties_from_api.py` (optional metadata enrichment pass)
- `scripts/tools/generate_wikidata_property_candidates_from_catalog.py` (candidate generation)

### Required lookup sequence

1. Attempt exact canonical mapping from `relationship_types_registry_master.csv`.
2. If unmapped, query local property catalog (label + description + aliases).
3. Apply datatype gate before ranking candidates.
4. Rank candidates using label match + alias match + description overlap.
5. Auto-apply only if confidence threshold is met; otherwise emit review queue entry.

### Datatype gate (hard filter)

- Candidate datatype MUST be compatible with relationship semantics.
- Examples:
  - Person/group/place/event relations -> prefer `wikibase-item`
  - Date/time relations -> `time`
  - Numeric indicator relations -> `quantity`
  - Media/file relations -> `commonsMedia`
  - Identifier relations -> `external-id`

### Alias handling (`propertyAltLabels`)

- Parse `propertyAltLabels` as pipe-delimited (`|`), normalize casing/whitespace, de-duplicate.
- Score exact alias matches strongly (same as exact label-class signals).
- Use aliases only after datatype compatibility is satisfied.

### Safety rule

- No low-confidence property mappings may be written directly to canonical registry.
- Low-confidence results MUST be written to review backlog and human-approved first.
- Identifier handling constraints in Appendix M still apply (tool resolution only, no LLM free-form ID generation).

## **K.6 Dispatcher and Backlink Operations**

Canonical scripts:
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/wikidata_backlink_profile.py`

Canonical report location:
- `JSON/wikidata/backlinks/`

Required report fields (minimum):
- `route_counts`
- `quarantine_reasons`
- `unsupported_pair_rate`
- `unresolved_class_rate`
- `frontier_eligible`
- `frontier_excluded`

---

**(End of Appendix K)**

---

