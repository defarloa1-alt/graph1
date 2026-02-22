# Appendix C: Entity Type Taxonomies

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

# **Appendix C: Entity Taxonomies and Subject Authority Tiers**

## **C.1 Core Entity Families**

Primary entity families are defined in Section 3 and include:

- Person and group entities (`Human`, `Organization`, `Institution`, `Dynasty`)
- Spatiotemporal entities (`Place`, `PlaceVersion`, `Period`, `Year`, `Event`)
- Knowledge/provenance entities (`Work`, `Claim`, `Review`, `Synthesis`)
- Domain-specific entities (Roman naming and office structures)

## **C.2 Subject Authority Tier Policy**

Subject concepts are classified by authority confidence:

| Tier | Criteria | Usage |
|---|---|---|
| `TIER_1` | Strong authority grounding + stable coverage | Default production |
| `TIER_2` | Valid but narrower or less complete coverage | Included with caution |
| `TIER_3` | Provisional or sparse authority support | Include with explicit confidence |
| `EXCLUDED` | Fails authority threshold | Do not ingest |

## **C.3 Required Identifier Backbone by Entity Type**

| Entity Type | Required IDs | Preferred IDs |
|---|---|---|
| Human | `qid` | `viaf_id`, `isni`, `lcsh_id` |
| Place | `qid` | `tgn_id`, `pleiades_id`, `geonames_id` |
| Period | `qid` or local canonical id | `periodo_uri`, `lcsh_id`, `fast_id` |
| Work | `qid` or catalog id | `worldcat_id`, `viaf_id` |
| SubjectConcept | `fast_id` or `lcsh_id` | `qid`, `lcc_code`, `marc_id` |

## **C.4 Consistency Rules**

1. Labels are natural language.
2. Identifiers are atomic strings.
3. Every canonical entity written to graph must include provenance linkage.
4. Subject assignment must not be inferred from entity type alone; use FAST/LCSH/LCC mappings.

---

**(End of Appendix C)**

---

