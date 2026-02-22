# Appendix H: Architectural Decision Records Overview

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

# **Appendix H: Architectural Decision Records**

## **H.1 ADR Index**

| ADR | Title | Status | Primary Section |
|---|---|---|---|
| ADR-001 | Two-stage architecture (LLM extraction -> reasoning validation) | Adopted | 1.2.1 |
| ADR-002 | Structure vs topics separation (LCC vs FAST) | Adopted | 1.2.3 |
| ADR-003 | LCC as primary classification backbone | Adopted | 1.4.1 |
| ADR-004 | Two-level agent granularity (FAST + LCC) | Adopted | 1.4.2, 5.4 |
| ADR-005 | CIDOC-CRM foundation with Chrystallum extensions | Adopted | 1.2.4 |
| ADR-006 | Hybrid architecture: traversable entities + content-addressable claims | Adopted | 6.4 |
| ADR-007 | Calendar normalization for historical dates | Adopted | 1.4.3, 3.4 |

## **H.2 ADR-006 (Detailed)**

Decision:

- Entities remain traversal-first in Neo4j for exploratory graph analytics.
- Claims use content-addressable `cipher` identity for immutability, deduplication, and verification.

Why:

- Traversal and discovery are essential for entity-layer research questions.
- Claim verification and provenance integrity require immutable claim identity.

Consequence:

- Mixed architecture by design; each layer optimized for its function.

## **H.3 ADR-007 (Detailed)**

Decision:

- Store normalized canonical dates plus original source dates and calendar metadata.

Why:

- Prevent false contradiction from Julian/Gregorian mismatches.
- Preserve source fidelity while enabling deterministic timeline queries.

Consequence:

- Temporal ingestion requires normalization step before confidence scoring.

## **H.4 Primary ADR Sources**

- `md/Architecture/ONTOLOGY_PRINCIPLES.md`
- `md/Architecture/LCC_AGENT_ROUTING.md`
- `md/Architecture/Subject_Agent_Granularity_Strategy.md`
- `md/CIDOC/CIDOC-CRM_vs_Chrystallum_Comparison.md`
- `md/Architecture/Historical_Dating_Schema_Disambiguation.md`

---

**(End of Appendix H)**

---

