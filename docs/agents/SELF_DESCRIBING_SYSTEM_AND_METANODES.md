# Self-Describing System and Metanodes — Agent Guide

**Purpose:** Explain to a new agent what the self-describing system is, what metanodes exist, and how they relate.

---

## 1. What Is the Self-Describing System?

Chrystallum uses a **self-describing system architecture**: the knowledge graph models its own structure as queryable graph nodes. Instead of hardcoding labels, relationship types, or config in scripts, agents **discover** them by querying the graph.

**Why it matters:**
- Agents can answer "what labels exist?", "what properties does Entity have?", "which federations does GEOGRAPHIC use?" purely by querying Neo4j
- No guessing or hallucinating structure — the graph is the executable contract
- Thresholds, policies, and schema live in the graph; scripts read them at runtime
- Single source of truth: change a SYS_Threshold node, and all consumers pick it up

**Core idea:** The system describes itself. An agent boots by querying the meta-layer first, then operates on domain data.

---

## 2. Root Structure

```
(:Chrystallum {name: "Chrystallum", version: "..."})   // System root
  -[:HAS_SCHEMA]->        (:SYS_SchemaRegistry)        // Data dictionary
  -[:HAS_FEDERATION]->    (:SYS_FederationRegistry)   // Federation sources
  -[:HAS_BIBLIOGRAPHY]->  (:SYS_BibliographyRegistry)  // Bibliography sources
  -[:HAS_PROCESS]->       (:SYS_ProcessRegistry)      // ADRs, pipeline, KANBAN
  -[:HAS_FEDERATION_ROOT]-> (:FederationRoot)         // Legacy: federation list
  -[:HAS_FACET_ROOT]->    (:FacetRoot)                // Facet hierarchy
```

**Label hygiene:** All system/metadata nodes use `SYS_` prefix and `{system: true}`. Domain queries exclude them:

```cypher
MATCH (n) WHERE n.system IS NULL ...   // excludes SYS_ nodes
```

---

## 3. Metanodes and Their Relations

### 3.1 SYS_Threshold

**Role:** Numeric configuration values for DMN decision tables. Scripts must read these at runtime — no hardcoding.

**Properties:** `name`, `value`, `unit`, `decision_table`, `rationale`, `last_reviewed`, `system`

**Examples:**
| name | value | decision_table |
|------|-------|----------------|
| `claim_promotion_confidence` | 0.90 | D10_DETERMINE_claim_promotion_eligibility |
| `scoping_confidence_temporal_med` | 0.85 | D5_DETERMINE_federation_scope_match |
| `sfa_proposal_confidence_default` | 0.75 | D8_DETERMINE_SFA_facet_assignment |
| `max_hops_p279` | 4 | D7_DETERMINE_harvest_allowlist_eligibility |

**Relations:** Referenced by DMN decision tables (D1–D14). No graph edges — scripts query by `name`.

**Usage:**
```cypher
MATCH (t:SYS_Threshold {name: 'claim_promotion_confidence'}) RETURN t.value
```

---

### 3.2 SYS_Policy

**Role:** Governance rules and policy names. Includes forbidden facets, approval flags, and rule semantics.

**Properties:** `name`, `description`, `decision_table`, `active`, `system`, `facet_key` (for forbidden-facet policies)

**Examples:**
| name | purpose |
|------|---------|
| `NoTemporalFacet` | Forbidden facet — SFA must not assign TEMPORAL |
| `NoClassificationFacet` | Forbidden facet — SFA must not assign CLASSIFICATION |
| `ApprovalRequired` | Claim promotion requires manual approval |
| `LocalFirstCanonicalAuthorities` | Federation routing policy |
| `HarvestModeBudgets` | Discovery vs production budget selection |

**Relations:** Referenced by DMN tables. SFA/SCA agents read forbidden facets from SYS_Policy nodes with `facet_key` property.

**Usage:**
```cypher
MATCH (p:SYS_Policy {active: true}) WHERE p.facet_key IS NOT NULL RETURN p.facet_key
```

---

### 3.3 SYS_PropertyMapping

**Role:** Wikidata property IDs (P-codes) → Facet mapping. Used by pipeline to route properties to facets.

**Properties:** `property_id`, `system`, plus `HAS_PRIMARY_FACET` edge to `:Facet`

**Count:** ~706 nodes

**Relations:**
```
(:SYS_PropertyMapping)-[:HAS_PRIMARY_FACET]->(:Facet)
```

**Usage:**
```cypher
MATCH (pm:SYS_PropertyMapping {property_id: 'P31'})-[:HAS_PRIMARY_FACET]->(f:Facet) RETURN f.key
```

---

### 3.4 SYS_SubjectConceptRoot

**Role:** Root anchor for the SubjectConcept hierarchy. Single node (Q17167 = Roman Republic).

**Properties:** `qid`, `label`, `system`

**Relations:**
```
(:SYS_SubjectConceptRoot)-[:DOMAIN_OF]->(:SubjectConcept)
```

**Note:** Migrated from `KnowledgeDomain` (D-029). Replaces the old KnowledgeDomain label.

---

### 3.5 SYS_FederationSource (in SYS_FederationRegistry)

**Role:** External authority sources (DPRR, Pleiades, Wikidata, LCSH, etc.). Each knows its status, scoping role, and Wikidata property.

**Properties:** `name`, `source_id`, `status`, `active`, `priority`, `scoping_role`, `evidence_type`, `license`, `wikidata_property`, `pid`

**Relations:**
```
(:SYS_FederationRegistry)-[:CONTAINS]->(:SYS_FederationSource)
(:SYS_FederationSource)-[:SCOPES]->(:EntityType)      // federation can scope this entity type
(:SYS_FederationSource)-[:PROVIDES]->(:EvidenceType)
(:SYS_FederationSource)-[:PROVIDES_ANCHOR]->(:Entity)  // federation provides identity anchor
```

**Examples:** DPRR (P6863), Pleiades (P1584), Wikidata (hub), LCSH, PeriodO, LGPN (P1047), Trismegistos (P1696).

---

### 3.6 SYS_NodeType, SYS_EdgeType (SchemaRegistry — planned)

**Role:** Machine-readable data dictionary. Every domain label and relationship type described as a node.

**SYS_NodeType:** Entity, Claim, Period, SubjectConcept, Place, Office, etc.  
**Properties:** `name`, `description`, `pk`, `abstract`, `deprecated`

**SYS_EdgeType:** MEMBER_OF, POSITION_HELD, OCCURRED_DURING, etc.  
**Properties:** `name`, `description`, `directed`, `deprecated`

**Relations (design):**
```
(:SYS_NodeType)-[:HAS_PROPERTY]->(:SYS_PropertyDefinition)
(:SYS_EdgeType)-[:FROM]->(:SYS_NodeType)
(:SYS_EdgeType)-[:TO]->(:SYS_NodeType)
```

**Status:** Design complete; build priority 2 (after FederationRegistry).

---

### 3.7 FacetRoot and Facet

**Role:** 18 facet dimensions (GEOGRAPHIC, POLITICAL, MILITARY, etc.). Facets use federations.

**Relations:**
```
(:Chrystallum)-[:HAS_FACET_ROOT]->(:FacetRoot)
(:FacetRoot)-[:HAS_FACET]->(:Facet)
(:Facet)-[:USES_FEDERATION]->(:Federation)   // or SYS_FederationSource
```

**Facet keys:** ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL

---

### 3.8 FederationRoot and Federation (legacy / transitional)

**Role:** Pre–SYS_ federation list. Some scripts still use `FederationRoot`-[:HAS_FEDERATION]->`Federation`.

**Migration:** D-014 replaces with SYS_FederationRegistry + SYS_FederationSource. Until rebuild, both may exist.

---

## 4. Key Relationships Summary

| From | Relationship | To |
|------|--------------|-----|
| Chrystallum | HAS_SCHEMA | SYS_SchemaRegistry |
| Chrystallum | HAS_FEDERATION | SYS_FederationRegistry |
| Chrystallum | HAS_FEDERATION_ROOT | FederationRoot |
| Chrystallum | HAS_FACET_ROOT | FacetRoot |
| FederationRoot | HAS_FEDERATION | Federation |
| FacetRoot | HAS_FACET | Facet |
| Facet | USES_FEDERATION | Federation |
| SYS_SubjectConceptRoot | DOMAIN_OF | SubjectConcept |
| SYS_PropertyMapping | HAS_PRIMARY_FACET | Facet |
| SYS_FederationSource | SCOPES | EntityType |
| SYS_FederationSource | PROVIDES | EvidenceType |
| SYS_FederationSource | PROVIDES_ANCHOR | Entity |

---

## 5. Agent Bootstrap Sequence

**Recommended order for a new agent:**

1. **Discover federations:** `MATCH (sys:Chrystallum)-[:HAS_FEDERATION]->(fr)-[:CONTAINS]->(f:SYS_FederationSource) RETURN f` (or legacy HAS_FEDERATION_ROOT path)
2. **Discover facets:** `MATCH (sys)-[:HAS_FACET_ROOT]->(fr)-[:HAS_FACET]->(facet:Facet) RETURN facet.key`
3. **Read thresholds:** `MATCH (t:SYS_Threshold) RETURN t.name, t.value` (for any DMN logic)
4. **Read forbidden facets:** `MATCH (p:SYS_Policy) WHERE p.facet_key IS NOT NULL RETURN p.facet_key`
5. **Discover schema (when built):** `MATCH (nt:SYS_NodeType) RETURN nt.name`

---

## 6. References

| Document | Purpose |
|----------|---------|
| `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN.md` | Full design, cleanup phases |
| `docs/architecture/SYSTEM_SUBGRAPH_ARCHITECTURE_2026-02-19.md` | Federation/Facet tree |
| `sysml/BLOCK_CATALOG_RECONCILED.md` | SysML blocks, SYS_ registries |
| `scripts/neo4j/add_dmn_threshold_policy_nodes.cypher` | SYS_Threshold, SYS_Policy population |
| `scripts/neo4j/add_sys_properties_and_relabel_d029.cypher` | D-029 relabeling |
| `scripts/analysis/run_self_describing_diagnostics.py` | Diagnostic queries |

---

*Last updated: 2026-02-27*
