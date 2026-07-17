# Node Type Review

**Date:** July 16, 2026  
**Total Node Types:** 151  
**Total Nodes:** ~156,000

## Summary by Category

| Category | Types | Nodes | Notes |
|----------|-------|-------|-------|
| **Geographic** | 5 | 115,100 | Place, PlaceName, Pleiades (core infrastructure) |
| **Bibliographic** | 5 | 7,073 | LCC, LCSH, VIAF, GND (authority files) |
| **Temporal** | 2 | 5,148 | Year, Periodo (temporal anchors) |
| **Domain/Meta** | 4 | 121 | Domain, SubjectConcept, Facet, Registry |
| **Knowledge** | 3 | 20,330 | Entity, Claim, Agent (core content) |
| **Classification** | 5 | 1,575 | Anchors, Disciplines (LCSH classification) |
| **Theory** | 7 | 32 | Military theory SPO structure |
| **System** | 37 | 1,293 | SYS_* metadata nodes |
| **Proposed/Temp** | 2 | 5,667 | ProposedEdge (5,667!), TemporalAnchor |
| **Other** | 83 | 15,270 | Mixed (authorities, people, events, etc.) |

## Recommendations for Deprecation/Cleanup

### 1. EMPTY NODE TYPES (46 types, 0 nodes)
**Recommendation: DELETE schema definitions**

These were probably planned but never used:
```
Activity, Geometry, Human, Institution, Dynasty, LegalRestriction, Work, 
Material, Object, Organization, FacetCategory, Location, FacetedEntity, 
FacetClaim, TemporalAnchor, PropertyMapping, PropertyType, PlaceVersion
```

**Action:** Remove from schema, clean up any code references.

### 2. PROPOSED/TEMP NODES
**ProposedEdge: 5,667 nodes**
- Same count as `Claim` nodes (5,667)
- Probably legacy architecture where claims were proposed edges
- **Recommendation:** Review if still needed with new Phase 2 claim architecture
- If obsolete, migrate to new format and delete

### 3. DUPLICATE PERSON/ENTITY TYPES
**Current state:**
- `Person`: 5,630 nodes
- `Entity`: 14,637 nodes (includes Person)
- `PERSON`: 2 nodes (?)
- `MythologicalPerson`: 3 nodes

**Recommendation:**
- Consolidate `Person` and `PERSON` (2 node type)
- Consider if `MythologicalPerson` should be `Person` with `is_mythological` property

### 4. MULTIPLE AUTHORITY SOURCES (25+ types)
**Current state:**
- VIAF, GND, LCNAF, BnF, ISNI, OpenLibrary, Perseus, Trismegistos, etc.
- Each authority has separate node types
- Total: ~5,000 authority nodes

**Recommendation:**
- These are probably correct (federated authority system)
- But verify they're all actively used
- Consider consolidating rarely-used ones

### 5. SYSTEM METADATA (37 SYS_* types)
**Large ones:**
- `SYS_RelationshipType`: 624 nodes
- `SYS_DecisionRow`: 145 nodes
- `SYS_NodeType`: 94 nodes
- `SYS_RoutingRule`: 81 nodes

**Recommendation:**
- Review if all are actively used
- Some might be from abandoned architectures
- Keep essential ones (RelationshipType, DecisionTable, Policy)

### 6. SFA TRAINING NODES
**Current state:**
- `SFA_TrainingInsight`: 46 nodes
- `SFA_TrainingRun`: 14 nodes
- `SFA_Claim`: 28 nodes
- `SFA_SubScope`: 33 nodes

**Recommendation:**
- These look active and aligned with current SFA architecture
- KEEP

### 7. ANALYSIS/WORKFLOW NODES
**Current state:**
- `AnalysisRun`: 257 nodes
- `FacetAssessment`: 257 nodes
- `RetrievalContext`: 257 nodes

**Recommendation:**
- All have 257 nodes (same count suggests linked pipeline)
- Check if this is legacy or active
- If legacy, consider deprecating

### 8. EVENT vs Event
**Current state:**
- `EVENT`: 6 nodes (all caps)
- `Event`: 71 nodes (proper case)

**Recommendation:**
- Consolidate into single `Event` type
- Migrate 6 `EVENT` nodes to `Event`

### 9. THEORY NODES (Military Theory)
**Current state:**
- `MilitaryPrinciple`: 3 nodes
- `Concept`: 4 nodes
- `Mechanism`: 10 nodes
- `Effect`: 8 nodes
- `Condition`: 3 nodes
- `Process`: 1 node
- `Target`: 3 nodes
- Total: 32 nodes (matches Domain:MILITARY_THEORY children count ✓)

**Recommendation:**
- KEEP - these are core to MILITARY_THEORY domain
- Aligned with new architecture

### 10. VERSIONING NODES
**Current state:**
- `Version`: 3 nodes

**Recommendation:**
- KEEP - these are the version tracking nodes we just created

## Priority Actions

### HIGH PRIORITY
1. **Delete 46 empty node types** - cleanup schema
2. **Review ProposedEdge (5,667)** - determine if legacy or migrate
3. **Consolidate PERSON (2) into Person (5,630)**
4. **Consolidate EVENT (6) into Event (71)**

### MEDIUM PRIORITY
5. **Review AnalysisRun/FacetAssessment pipeline** - active or legacy?
6. **Audit SYS_* metadata nodes** - which are still used?
7. **Review authority sources** - consolidate rarely-used ones

### LOW PRIORITY
8. **Document remaining node types** - create schema documentation
9. **Enforce naming conventions** - CamelCase for all node types

## Alignment with New Architecture

### ✅ ALIGNED
- `Domain` (3) - NEW, core architecture
- `SubjectConcept` (99) - organized under domains
- `SubjectConceptRegistry` (1) - tracks domains
- `Facet` (18) - SFA facets
- `Agent` (26) - SFA agents
- `Claim` (5,667) - claim nodes
- `Entity` (14,637) - canonical entities
- Theory nodes (32) - MILITARY_THEORY content
- `Version` (3) - versioning system

### ❓ NEEDS REVIEW
- `ProposedEdge` (5,667) - same count as Claim, overlap?
- `AnalysisRun` (257) - legacy pipeline?
- `CorpusWork` (265) - what is this?
- `FacetUmbrella` (15) - still used?

### ❌ LIKELY DEPRECATED
- 46 empty node types
- `PERSON` (2 nodes) - should be `Person`
- `EVENT` (6 nodes) - should be `Event`

## Cypher Queries for Cleanup

### Delete empty node types
```cypher
// Run for each empty label
// (Manual list needed - Neo4j doesn't support dynamic label deletion)
```

### Consolidate PERSON → Person
```cypher
MATCH (p:PERSON)
SET p:Person
REMOVE p:PERSON
```

### Consolidate EVENT → Event
```cypher
MATCH (e:EVENT)
SET e:Event
REMOVE e:EVENT
```

### Find orphaned ProposedEdge nodes
```cypher
MATCH (pe:ProposedEdge)
WHERE NOT (pe)-[]-()
RETURN count(pe)
```

## Next Steps

1. Review this document
2. Confirm which node types to deprecate
3. Run cleanup queries
4. Update schema documentation
5. Enforce conventions going forward
