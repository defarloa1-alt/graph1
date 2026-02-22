# Appendix F: Geographic Authority Integration

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

# **Appendix F: Geographic Authority Integration**

## **F.1 Scope**

Normative geographic federation logic is in Section 4.4. This appendix is the source and ingestion reference.

## **F.2 Authoritative Files**

- Raw authority snapshots: `Geographic/*.out`
- Curated registry: `Geographic/geographic_registry_master.csv`
- RDF references: `Geographic/ontology.rdf`, `Geographic/tgn_7011179-place.rdf`
- Consolidation note: `Geographic/GEOGRAPHIC_CONSOLIDATION_2026-02-12.md`

## **F.3 Curated Registry Snapshot**

From `Geographic/geographic_registry_master.csv`:

- Rows: `20`
- Facet assignments observed:
- `cultural_geographic`: 8
- `pure_spatial`: 3
- `political`: 2
- unassigned/blank: 7

## **F.4 Ingestion Rules**

1. Use authority place IDs (TGN/Pleiades/GeoNames) as atomic identifiers.
2. Keep historical names and modern names as separate properties.
3. Preserve hierarchy and containment relations independently of political regime naming.
4. Do not collapse culturally-defined regions into purely geometric regions.

---

**(End of Appendix F)**

---

