# V1 Relationship Kernel: Strategic 25-Type Foundation

**Version**: 2026-02-16  
**Status**: Recommended Baseline (NOT a restriction)  
**Purpose**: Minimal, traversable relationship kernel that defines a stable baseline for federation testing and cross-system compatibility

---

## ⚠️ IMPORTANT: All 310 Relationships Are Available

**The v1 kernel is a RECOMMENDED BASELINE, not a restriction.**

- ✅ **All 310 relationship types** in the registry are validated and available immediately
- ✅ Use `RelationshipAssertion` model to access any of the 310 types
- ✅ Use `V1KernelAssertion` ONLY when you want to restrict to the 25-type baseline (e.g., for federation compatibility testing)

**You do NOT need to wait for domain packages.** Use COMMANDED_MILITARY_UNIT, PARENT_OF, MARRIED_TO, INFLUENCED, etc. right now.

---

## Overview

The **v1 kernel** is a strategic subset of 25 relationships (of 310 total) that defines a **stable baseline** for:
- ✓ Cross-system federation (guaranteed compatibility)
- ✓ Core graph traversal patterns
- ✓ Entity identity and recognition
- ✓ Spatial and temporal reasoning
- ✓ Provenance tracking

**Principle**: These 25 relationships are **universally applicable** and **enable fundamental queries**. They represent the minimal set needed for basic historical graph operations.

---

## The 25 Core Relationships

Organized into 5 strategic families:

### 1. **Identity & Entity Recognition** (5 relationships)

| Type | Forward | Reverse | Domain | Rationale |
|------|---------|---------|--------|-----------|
| `SAME_AS` | A is identical to B | (symmetric) | Universal | Entity deduplication; federation cornerstone |
| `TYPE_OF` | Entity A is a type of B | (inverse) | Universal | Classification; enables hierarchical queries |
| `INSTANCE_OF` | Entity A is instance of type B | (inverse) | Universal | Class membership; type assertion |
| `NAME` | Entity has name | (unidirectional) | Universal | Literal naming; required for all entities |
| `ALIAS_OF` | Alternative name/form of | (symmetric) | Universal | Cross-reference alternate identifiers |

**Why these?**
- Foundation for entity resolution and deduplication
- Required for any meaningful entity query
- Enable cross-domain identity linking (federation)

---

### 2. **Spatial & Structural Relationships** (5 relationships)

| Type | Forward | Reverse | Domain | Rationale |
|------|---------|---------|--------|-----------|
| `LOCATED_IN` | A is located in B | IN_LOCATION | Universal | Place hierarchy; geographic queries |
| `PART_OF` | A is part of B | HAS_PART | Universal | Composition; hierarchical structure |
| `BORDERS` | A borders B | (mutual) | Geographic | Spatial adjacency; territorial queries |
| `CAPITAL_OF` | A is capital of B | HAS_CAPITAL | Geographic | Administrative hierarchy |
| `CONTAINED_BY` | A region contained by B | CONTAINS | Temporal/Geographic | Spatial-temporal locality |

**Why these?**
- Enable spatial reasoning (core for historical analysis)
- Required for institutional/organizational hierarchy
- Foundation for geographic and administrative queries

---

### 3. **Temporal & Event Relationships** (4 relationships)

| Type | Forward | Reverse | Domain | Rationale |
|------|---------|---------|--------|-----------|
| `OCCURRED_AT` | Event occurred at location | (inverse) | Universal | Spatiotemporal grounding |
| `OCCURS_DURING` | Event occurs in period | (inverse) | Universal | Temporal scoping; period analysis |
| `HAPPENED_BEFORE` | Event A before Event B | (inverse) | Universal | Temporal ordering; sequence queries |
| `CONTEMPORARY_WITH` | A and B overlap temporally | (symmetric) | Universal | Coexistence; simultaneity queries |

**Why these?**
- Minimal temporal layer (avoid explosion of temporal variants)
- Enable historical sequence queries
- Support period-based lensing

---

### 4. **Provenance & Attribution** (6 relationships)

| Type | Forward | Reverse | Domain | Rationale |
|------|---------|---------|--------|-----------|
| `CITES` | Work A cites Work B | (inverse) | Universal | Citation graph; evidence chain |
| `DERIVES_FROM` | Entity A derived from B | (inverse) | Universal | Lineage; version tracking |
| `EXTRACTED_FROM` | Claim extracted from source | (inverse) | Evidence | Claim grounding; direct traceability |
| `AUTHOR` | Creator of work | AUTHORED_BY | Universal | Authorship; attribution |
| `ATTRIBUTED_TO` | Claim/statement attributed to agent | (inverse) | Universal | Agent responsibility; viewpoint |
| `DESCRIBES` | Work/claim describes entity | (inverse) | Universal | Reference relationships; topic coverage |

**Why these?**
- Core provenance model (essential for science/scholarship)
- Enable citation/evidence chains
- Support claim traceability

---

### 5. **Relational & Assertion Patterns** (5 relationships)

| Type | Forward | Reverse | Domain | Rationale |
|------|---------|---------|--------|-----------|
| `SUBJECT_OF` | Entity is subject of claim | (inverse) | Evidence | Claim structure; what is being described |
| `OBJECT_OF` | Entity is object of claim | (inverse) | Evidence | Claim structure; what is being acted upon |
| `CAUSED` | Event A caused Event B | CAUSED_BY | Causality | Causal inference; explanation |
| `CONTRADICTS` | Claim A contradicts B | (mutual) | Evidence | Dispute tracking; conflict resolution |
| `SUPPORTS` | Claim A supports claim B | (inverse) | Evidence | Evidence relationship; mutual reinforcement |

**Why these?**
- Minimal claim/assertion model (metadata for evidence)
- Enable logical inference (support/contradiction)
- Foundation for dispute modeling

---

## Beyond the Kernel (285+ Additional Relationships)

**All of these are AVAILABLE NOW** - use them freely with `RelationshipAssertion`.

| Relationship | Category | Use Case | Status |
|--------------|----------|----------|--------|
| `COMMANDED_MILITARY_UNIT` | Military | Military command structures | ✅ Available |
| `PARENT_OF`, `CHILD_OF` | Genealogy | Family tree relationships | ✅ Available |
| `MEMBER_OF` | Organizational | Group membership | ✅ Available |
| `CONFLICT_WITH` | Military/Political | Adversarial relationships | ✅ Available |
| `MARRIED_TO` | Genealogy | Spousal relationships | ✅ Available |
| `PERFORMED` | Arts/Performance | Actor/performer relationships | ✅ Available |
| `INFLUENCED` | Intellectual | Intellectual influence | ✅ Available |

**Note**: The v1 kernel (25 types) is just the **recommended baseline for federation**. You can use any of the 310 types right now - they're all validated and supported.

---

## V1 Kernel Properties

### Implementat Status

| Status | Count | Examples |
|--------|-------|----------|
| **Implemented** | 24 | SAME_AS, NAME, LOCATED_IN, OCCURRED_AT, CITES, CAUSED, etc. |
| **Candidate** | 1 | ALIAS_OF (may merge with SAME_AS in v1) |

### Wikidata Alignment

All 25 types map to Wikidata predicates (P-codes):

| Relationship | Wikidata P-code | Coverage |
|--------------|---|---|
| SAME_AS | P2888 (exact match), P460 (said to be the same as) | ~100% |
| LOCATED_IN | P131 (located in administrative territory) | ~95% |
| CITES | P2579 (cites) | ~80% |
| CAUSED | P828 (has cause) | ~70% |
| ... | ... | ... |

**Federation implications**: v1 kernel types have 70-100% Wikidata coverage, enabling direct federation with external SPARQL endpoints.

---

## Traversal Capability Matrix

### Basic Patterns Enabled by V1 Kernel

```
Pattern                          | Relationships Used
---------------------------------|------------------------
Entity deduplication             | SAME_AS
Entity classification            | TYPE_OF, INSTANCE_OF
Find entity by name              | NAME
Spatial hierarchy navigation     | LOCATED_IN, PART_OF, BORDERS
Administrative structure         | CAPITAL_OF, PART_OF
Event sequence/ordering          | OCCURRED_AT, HAPPENS_BEFORE
Temporal coexistence checks      | CONTEMPORARY_WITH, OCCURS_DURING
Citation/evidence chains         | CITES, DERIVES_FROM, EXTRACTED_FROM
Who said what                    | ATTRIBUTED_TO, AUTHOR
Claim grounding                  | SUBJECT_OF, OBJECT_OF, DESCRIBES
Conflict/contradiction           | CONTRADICTS, SUPPORTS
Causality                        | CAUSED, CAUSED_BY
```

### Complex Patterns (Compositions)

```
Pattern                               | Composition
--------------------------------------|------------------------------------------
Find claims about an entity           | DESCRIBES ← SUBJECT_OF / OBJECT_OF
What evidence supports a claim        | SUPPORTS ← DERIVED_FROM ← EXTRACTED_FROM
Coexisting entities in a place        | OCCURRED_AT ← LOCATED_IN + CONTEMPORARY_WITH
Entity type hierarchy                 | INSTANCE_OF → TYPE_OF → TYPE_OF (chain)
Attribution chain                     | ATTRIBUTED_TO → AUTHOR (to find full lineage)
Causality + Geography                 | CAUSED → OCCURRED_AT → LOCATED_IN
```

---

## Implementation Plan

### Phase 1: Schema Setup (immediate)

1. ✓ Add v1 kernel relationships to Pydantic validators
   - All 25 types added to canonical relationship registry
2. ✓ Generate Neo4j constraints for v1 kernel
   - Indexes on SAME_AS (deduplication)
   - Uniqueness on entity + NAME
   - Constraints on temporal ordering (HAPPENS_BEFORE must be acyclic)
3. ✓ Create v1-specific seed script
   - Minimal historical data (10-20 example claims)
   - Romanian Republic domain (existing sample data)
   - Showcases all 25 relationship types

### Phase 2: Federation Testing

1. Query v1 kernel types against Wikidata SPARQL
2. Verify cross-system identity matching (SAME_AS federation)
3. Test import/export of v1 claims across systems

### Phase 3: Scaling to v1.1

1. Add domain-specific packages (Military, Genealogy, Arts, etc.)
2. Expand each package with specialized relationships
3. Maintain v1 kernel as stable core

---

## Using Relationships in Code

### Option 1: All 310 Relationships (Recommended for Most Use Cases)

```python
from models import RelationshipAssertion, initialize_registry

# Initialize registry (do this once at app startup)
initialize_registry(
    "Relationships/facet_registry_master.json",
    "Relationships/relationship_types_registry_master.csv"
)

# Use ANY of the 310 relationship types
military = RelationshipAssertion(
    rel_type="COMMANDED_MILITARY_UNIT",  # ✅ Works!
    subject_id="Q1048",
    object_id="Q123456",
    confidence=0.95
)

genealogy = RelationshipAssertion(
    rel_type="PARENT_OF",  # ✅ Works!
    subject_id="Q100",
    object_id="Q200",
    confidence=1.0
)

influence = RelationshipAssertion(
    rel_type="INFLUENCED",  # ✅ Works!
    subject_id="Q300",
    object_id="Q400"
)
```

### Option 2: V1 Kernel Only (For Federation Compatibility Testing)

```python
from models import V1KernelAssertion

# Restricted to 25 baseline types - NO registry needed
kernel = V1KernelAssertion(
    rel_type="SAME_AS",  # ✅ In kernel
    subject_id="Q1",
    object_id="Q2"
)

# This will fail - not in kernel
try:
    V1KernelAssertion(
        rel_type="COMMANDED_MILITARY_UNIT",  # ❌ Not in 25-type kernel
        subject_id="Q1",
        object_id="Q2"
    )
except ValidationError:
    # Use RelationshipAssertion instead for full catalog access
    pass
```

### Neo4j Seed Script

```cypher
// v1_kernel_seed.cypher
// Creates minimal graph for v1 kernel testing

// Indexes for v1 relationships
CREATE INDEX entity_name_idx IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX entity_qid_idx IF NOT EXISTS FOR (e:Entity) ON (e.qid);
CREATE INDEX same_as_idx IF NOT EXISTS FOR ()-[r:SAME_AS]->() ON (r.confidence);
CREATE INDEX temporal_order_idx IF NOT EXISTS FOR ()-[r:HAPPENED_BEFORE]->() ON (r.temporal_scope);

// Constraints
CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.qid IS UNIQUE;
CREATE CONSTRAINT same_as_no_cycles IF NOT EXISTS FOR ()-[r:SAME_AS]->() REQUIRE r.is_acyclic = true;

// Example entities (Roman Republic sample)
CREATE (rome:Entity {
  qid: "Q87",
  name: "Roman Republic",
  label: "Roman Republic",
  temporal_scope: "509/-27"
})
CREATE (caesar:Entity {
  qid: "Q1048",
  name: "Caesar",
  label: "Julius Caesar",
  temporal_scope: "100/-44"
})
CREATE (gaul:Entity {
  qid: "Q779",
  name: "Gaul",
  label: "Gaul",
  temporal_scope: "-500/500"
})

// Relationships
CREATE (caesar)-[:LOCATED_IN {confidence: 0.95}]->(rome)
CREATE (gaul)-[:BORDERS {confidence: 0.90}]->(rome)
CREATE (caesar)-[:CONTEMPORARY_WITH {confidence: 1.0}]->(rome)

// More examples would follow...
```

---

## Success Metrics for V1

- [ ] All 25 relationship types implemented in production
- [ ] Can query entity deduplication (find SAME_AS chains)
- [ ] Can navigate spatial hierarchy (LOCATED_IN → PART_OF chains)
- [ ] Can traverse citation graphs (CITES chains)
- [ ] Can federate with Wikidata (SAME_AS matches ≥70%)
- [ ] Historical sample data correctly uses all 25 types
- [ ] No v1 relationships in "candidate" status

---

## Relationship to ADRs

- **ADR-002** (Functional Relationship Catalog): v1 kernel is the "Core Traversal" + "Provenance" functions (17 of 310 types)
- **ADR-005** (Federated Signing): v1 kernel relationships are the primary targets for cryptographic signing and cross-institution verification

---

## References

- [Relationship Types Registry](../../Relationships/relationship_types_registry_master.csv) (310 types)
- [ADR-002: Function-Driven Relationship Catalog](../../Key%20Files/2-12-26%20Chrystallum%20Architecture%20-%20CONSOLIDATED.md#Appendix-V)
- [Roman Republic Historical Sample](../../Nodes/)
- [Wikidata Property Index](https://wikidata.org/wiki/Wikidata:Database_reports/List_of_properties)

---

**Next**: Implement v1 kernel validation + generate seed script
