# Appendix Y: ADR 006 Bootstrap Scaffold Contract

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

## **Appendix Y: v0 Bootstrap Scaffolding Contract (2026-02-17 Decisions)**

**Status:** Normative for v0 bootstrap and scaffold/promotion boundaries.  
**Source Input:** `md/Architecture/2-17-26-CHRYSTALLUM_v0_AGENT_BOOTSTRAP_SPEC.md`

### **Y.1 Scope and precedence**

For v0 bootstrap workflows, this appendix supersedes conflicting legacy examples in this consolidated file.

### **Y.2 Canonical vs scaffold boundary**

- Canonical writes are promotion-gated.
- Bootstrap and SFA pre-promotion writes are scaffold-only.
- Scaffold labels are distinct from canonical labels.

### **Y.3 Required scaffold labels**

- `:ScaffoldNode`
- `:ScaffoldEdge`
- `:AnalysisRun` (canonical run anchor reused)

### **Y.4 Required scaffold edge contract**

Scaffold edge-as-node pattern:

```cypher
(e:ScaffoldEdge)-[:FROM]->(s:ScaffoldNode)
(e:ScaffoldEdge)-[:TO]->(o:ScaffoldNode)
```

Required ScaffoldEdge properties:
- `edge_id`
- `analysis_run_id`
- `relationship_type`
- `wd_property`
- `direction`
- `confidence`
- `created_at`

### **Y.5 Bootstrap traversal controls (v0 defaults)**

- Upward P31/P279 depth: `4`
- Lateral mapped-property hops: `2` (mapped properties only)
- Downward inverse P279 depth: `2`
- Inverse P31: sampling only (bounded)
- Hard caps and NOT-filters must be logged with truncation metadata

### **Y.6 Canonical facet topology**

```cypher
(:Claim)-[:HAS_ANALYSIS_RUN]->(:AnalysisRun)-[:HAS_FACET_ASSESSMENT]->(:FacetAssessment)-[:ASSESSES_FACET]->(:Facet)
```

### **Y.7 Promotion contract**

Promotion service:
1. Validates candidates against filter/meta-ceiling policy.
2. Merges canonical nodes.
3. Creates canonical relationships (registry-approved types only).
4. Creates/attaches canonical claims and evidence where needed.
5. Records a promotion event linking promoted artifacts to `analysis_run_id` and source scaffold artifacts.

### **Y.8 Occupation/profession policy**

- No first-class `:Occupation` node label in canonical model.
- Profession/occupation concepts canonize as `:SubjectConcept` when approved.
- Human-profession assertions require temporal bounding.

---

