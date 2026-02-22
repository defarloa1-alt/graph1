# Appendix A: Canonical Relationship Types

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

# **Appendix A: Canonical Relationship Types**

## **A.1 Purpose**

Defines the canonical relationship registry used to normalize edge semantics, directionality, and external mappings.
`lcc_code`, `lcsh_heading`, and `fast_id` are registry-level classification metadata for governance/routing, not properties stored on graph edge instances.

## **A.2 Authoritative Files**

- Primary registry: `Relationships/relationship_types_registry_master.csv`
- Historical duplicate archived: `Archive/Key Files/1-14-26-Canonical_relationship_types.archived-2026-02-13.csv`
- Seed script: `Relationships/relationship_types_seed.cypher`

## **A.3 Current Registry Snapshot**

From `Relationships/relationship_types_registry_master.csv`:

- Total relationship types: `300`
- Categories: `31`
- Lifecycle status: `192 implemented`, `108 candidate`
- Active status: `300 active`

Top categories by volume:

| Category | Count |
|---|---:|
| Political | 39 |
| Familial | 30 |
| Military | 23 |
| Geographic | 20 |
| Economic | 16 |
| Legal | 13 |
| Authorship | 12 |
| Diplomatic | 12 |

## **A.4 Registry Fields (Required Core)**

| Field | Meaning |
|---|---|
| `category` | Semantic family (`Political`, `Military`, etc.) |
| `relationship_type` | Canonical edge label (`PARTICIPATED_IN`, `LOCATED_IN`, etc.) |
| `directionality` | `forward`, `inverse`, or `symmetric` |
| `wikidata_property` | Optional direct Wikidata `P` property |
| `parent_relationship` | Optional inheritance parent |
| `specificity_level` | Relative abstraction level |
| `lcc_code` / `lcsh_heading` / `fast_id` | Library alignment metadata |
| `lifecycle_status` | `implemented` or `candidate` |

## **A.5 Governance Rules**

1. Do not add ad hoc relationship labels directly in code.
2. Add candidate relationships to registry first, with source and rationale.
3. Promote candidate to implemented only after:
- domain/range validation
- directionality review
- external mapping check (if available)
4. Keep inverse forms explicit where required for query ergonomics.

## **A.6 Query Pattern**

```cypher
MATCH ()-[r]->()
WITH type(r) AS rel, count(*) AS n
RETURN rel, n
ORDER BY n DESC;
```

---

**(End of Appendix A)**

---

