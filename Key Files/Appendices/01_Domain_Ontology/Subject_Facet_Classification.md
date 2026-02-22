# Appendix D: Subject Facet Classification

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

# **Appendix D: Subject Facet Classification**

## **D.1 Purpose**

Defines facet classes and anchor concepts used by the star-pattern architecture.

## **D.2 Authoritative Files**

- Registry: `Facets/facet_registry_master.csv`
- Consolidation note: `Facets/FACETS_CONSOLIDATION_2026-02-12.md`
- Pattern note: `Facets/star-pattern-claims.md`

## **D.3 Current Registry Snapshot**

From `Facets/facet_registry_master.csv`:

- Total facet-anchor rows: `86`
- Facet classes: `16`
- Facet keys: `16`

Facet classes:

- `ArchaeologicalFacet`
- `ArtisticFacet`
- `CulturalFacet`
- `DemographicFacet`
- `DiplomaticFacet`
- `EconomicFacet`
- `EnvironmentalFacet`
- `GeographicFacet`
- `IntellectualFacet`
- `LinguisticFacet`
- `MilitaryFacet`
- `PoliticalFacet`
- `ReligiousFacet`
- `ScientificFacet`
- `SocialFacet`
- `TechnologicalFacet`

## **D.4 Structural Contract**

```cypher
(:Claim)-[:HAS_ANALYSIS_RUN]->(:AnalysisRun)-[:HAS_FACET_ASSESSMENT]->(:FacetAssessment)-[:ASSESSES_FACET]->(:Facet)
(:Facet)-[:IN_FACET_CATEGORY]->(:FacetCategory)
```

## **D.5 Quality and Promotion Rules**

- Resolve anchor `qid` conflicts before promotion.
- Keep `facet_key` stable; evolve labels, not keys.
- Treat facet confidence as independent dimensions, not one global confidence.

---

**(End of Appendix D)**

---

