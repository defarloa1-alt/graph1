# Appendix G: Legacy Implementation Patterns

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

# **Appendix G: Legacy Implementation Patterns**

## **G.1 Purpose**

Documents deprecated patterns to prevent accidental reintroduction.

## **G.2 Deprecated vs Current**

| Legacy Pattern | Problem | Current Pattern |
|---|---|---|
| Flat subject tagging without facets | No multidimensional analysis | Star-pattern facets with per-facet confidence |
| Treating short crises as periods | Temporal ambiguity | Period/Event distinction with classification workflow |
| Identifier handling through LLM prompts | Tokenization breakage | Two-stage: LLM labels -> tool ID resolution |
| Ad hoc relationship labels | Query fragmentation | Registry-first relationship governance |

## **G.3 Migration Note**

All new implementations should follow Sections 3-8 plus appendices A, B, D, and M.

---

**(End of Appendix G)**

---

