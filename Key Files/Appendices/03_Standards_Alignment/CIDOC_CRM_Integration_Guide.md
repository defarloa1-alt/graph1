# Appendix L: CIDOC CRM Integration Guide

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

# **Appendix L: CIDOC-CRM Integration Guide**

## **L.1 Scope**

Defines triple alignment approach: Chrystallum relation type <-> Wikidata property <-> CIDOC-CRM property/class.

## **L.2 Authoritative Files**

- `md/CIDOC/CIDOC-CRM_vs_Chrystallum_Comparison.md`
- `md/Architecture/CIDOC-CRM_Alignment_Summary.md`
- `md/Architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`

## **L.3 High-Value Mappings**

| Chrystallum | Wikidata | CIDOC-CRM |
|---|---|---|
| `PARTICIPATED_IN` | `P710` | `P11_had_participant` |
| `LOCATED_IN` | `P131` | `P7_took_place_at` |
| `PART_OF` | n/a | `P86_falls_within` |
| `CAUSED` | `P828` | `P15_was_influenced_by` |
| `AUTHOR` | `P50` | `P14_carried_out_by` via `E12_Production` |

## **L.4 Entity Class Alignment**

| Chrystallum Node | CIDOC-CRM Class |
|---|---|
| Event | `E5_Event` |
| Human | `E21_Person` |
| Place | `E53_Place` |
| Organization | `E74_Group` / `E40_Legal_Body` |
| TimeSpan | `E52_Time-Span` |

## **L.5 Implementation Rule**

CIDOC-CRM alignment is additive. Chrystallum-specific capabilities (library backbones, action-structure vocabularies, identifier safety) remain first-class and are not dropped for standards compatibility.

---

**(End of Appendix L)**

---

