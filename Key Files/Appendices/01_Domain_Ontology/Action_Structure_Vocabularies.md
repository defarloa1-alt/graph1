# Appendix B: Action Structure Vocabularies

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

# **Appendix B: Action Structure Vocabularies**

## **B.1 Purpose**

Defines controlled vocabularies for relationship-level action semantics:

- goal (`goal_type`)
- trigger (`trigger_type`)
- action (`action_type`)
- result (`result_type`)

## **B.2 Authoritative Files**

- Vocabulary registry: `CSV/action_structure_vocabularies.csv`
- Wikidata alignment: `CSV/action_structure_wikidata_mapping.csv`
- Reference explainer: `md/Reference/Action_Structure_Vocabularies.md`

## **B.3 Vocabulary Counts**

From `CSV/action_structure_vocabularies.csv` (`54` total entries):

| Component | Count |
|---|---:|
| Goal Type | 10 |
| Trigger Type | 10 |
| Action Type | 15 |
| Result Type | 19 |

## **B.4 Example Codes**

| Component | Code | Meaning |
|---|---|---|
| Goal | `POL` | Political objective |
| Goal | `MIL` | Military objective |
| Trigger | `POL_TRIGGER` | Political trigger |
| Trigger | `EXT_THREAT` | External threat |
| Action | `MIL_ACT` | Military action |
| Action | `DIPL_ACT` | Diplomatic action |
| Result | `POL_TRANS` | Political transformation |
| Result | `CONQUEST` | Conquest outcome |

## **B.5 Usage Contract**

- Store codes on relationships.
- Keep human-readable descriptions in companion properties.
- Validate code membership before write.
- Use code-to-QID alignment from `CSV/action_structure_wikidata_mapping.csv` for federation.

Example:

```cypher
MATCH (a:Human {label: 'Julius Caesar'}), (b:Event {label: 'Roman Civil War'})
MERGE (a)-[r:CAUSED]->(b)
SET r.goal_type = 'POL',
    r.trigger_type = 'POL_TRIGGER',
    r.action_type = 'MIL_ACT',
    r.result_type = 'POL_TRANS';
```

---

**(End of Appendix B)**

---

