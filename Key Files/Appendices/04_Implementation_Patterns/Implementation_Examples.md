# Appendix J: Implementation Examples

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

# **Appendix J: Implementation Examples**

## **J.1 Subject-Centric Retrieval**

```cypher
MATCH (s:SubjectConcept {fast_id: 'fst01204885'})<-[:HAS_SUBJECT_CONCEPT]-(e)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(c:Claim)
RETURN e.label AS entity, count(c) AS supporting_claims
ORDER BY supporting_claims DESC
LIMIT 50;
```

## **J.2 Claim Verification by Cipher**

```cypher
MATCH (c:Claim {cipher: $cipher})
OPTIONAL MATCH (c)<-[:REVIEWED]-(r:Review)
RETURN c.status, c.confidence, collect(r.verdict) AS verdicts;
```

## **J.3 Identifier-Safe Ingestion Skeleton**

```python
# Stage 1: LLM extracts natural-language labels
labels = extractor.extract(text)

# Stage 2: deterministic tools resolve identifiers
qid = wikidata.resolve(labels["entity_label"])
fast_id = fast.resolve(labels["subject_label"])

# Stage 3: persist both label and atomic IDs
record = {
    "label": labels["entity_label"],
    "qid": qid,
    "fast_id": fast_id,
}
```

## **J.4 Script Operations Reference**

- Script registry: `md/Reference/SCRIPT_REGISTRY_2026-02-13.md`
- Registry CSV: `md/Reference/SCRIPT_REGISTRY_2026-02-13.csv`

---

**(End of Appendix J)**

---

