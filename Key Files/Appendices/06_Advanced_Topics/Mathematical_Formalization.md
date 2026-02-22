# Appendix I: Mathematical Formalization

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

# **Appendix I: Mathematical Formalization**

## **I.1 Confidence Components**

Source confidence:

```text
T_confidence = T_tier + delta_recency - delta_contradiction
```

Claim confidence (weighted by relevance):

```text
C_confidence = sum(T_confidence_i * relevance_i) / sum(relevance_i)
```

Facet enrichment score:

```text
FES = (facets_present / 16) * 100
```

## **I.2 Temporal Decay Function**

For time-sensitive claims:

```text
decay(t) = exp(-lambda * t)
```

Where:

- `t` = years since claim assertion or source timestamp
- `lambda` is domain-specific decay rate

## **I.3 Practical Bounds**

- Confidence values are bounded to `[0.0, 1.0]`.
- Contradiction penalties should never drive score below `0.0`.
- Use explicit null/unknown handling for missing components.

---

**(End of Appendix I)**

---

