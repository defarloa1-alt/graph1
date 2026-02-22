# Appendix M: Identifier Safety Reference

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

# **Appendix M: Identifier Safety Reference**

## **M.1 Core Rule**

Never pass atomic identifiers to LLMs for interpretation.

Use two-stage processing:

1. LLM extracts natural language labels.
2. Deterministic tools resolve and validate identifiers.

## **M.2 Decision Table**

| Input Type | Example | LLM-safe | Handling |
|---|---|---|---|
| Natural-language label | `Roman Republic` | Yes | LLM extraction/classification |
| Wikidata QID | `Q17193` | No | Tool lookup only |
| FAST ID | `1145002` | No | Tool lookup only |
| LCC code | `DG241-269` | No | Tool lookup only |
| MARC authority ID | `sh85115058` | No | Tool lookup only |
| Pleiades ID | `423025` | No | Tool lookup only |
| ISO date with negative year | `-0509-01-01` | No | Store/format with temporal tool |

## **M.3 Authoritative References**

- `md/Reference/IDENTIFIER_ATOMICITY_AUDIT.md`
- `md/Reference/IDENTIFIER_CHEAT_SHEET.md`
- Section 8.5 in this architecture document

## **M.4 Pre-Prompt Validation Checklist**

Before any LLM call:

- remove QIDs and catalog IDs
- replace with human-readable labels
- keep numeric/scalar fields only when they are true numeric values
- run identifier validator where available

---

**(End of Appendix M)**

---

