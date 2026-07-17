# Node Type Cleanup Investigation Report

**Date:** July 16, 2026  
**Investigation:** Complete node type audit and cleanup preparation

---

## Executive Summary

Comprehensive investigation of Neo4j node types revealed:
- **16 empty node types** ready for cleanup (excluding Material/Object as requested)
- **ProposedEdge** nodes (5,667) are ACTIVE architecture, NOT legacy - **DO NOT DELETE**
- **2 PERSON nodes** ready for consolidation → Person (have incoming relationships)
- **6 EVENT nodes** ready for consolidation → Event (some have incoming relationships)

---

## 1. Empty Node Types Investigation

### Found: 16 Empty Types (0 nodes each)

**Safe to remove** (will automatically disappear from schema when unused):

1. Activity
2. Dynasty
3. FacetCategory
4. FacetClaim
5. FacetedEntity
6. Geometry
7. Human
8. Institution
9. LegalRestriction
10. Location
11. Organization
12. PlaceVersion
13. PropertyMapping
14. PropertyType
15. TemporalAnchor
16. Work

### Status: Material and Object

As requested, **Material** and **Object** were excluded from this list and will be kept for future use.

**Verification:**
```cypher
MATCH (m:Material) RETURN count(m) as count  // Returns: 0
MATCH (o:Object) RETURN count(o) as count    // Returns: 0
```

### Action Required

**None** - Neo4j will automatically remove these label types from the schema when no nodes use them. They exist only as potential labels in the current schema but have no impact on performance or queries.

Optional: Update documentation to remove references to these unused types.

---

## 2. ProposedEdge Investigation - CRITICAL FINDINGS

### Status: **ACTIVE ARCHITECTURE - DO NOT DELETE**

### Key Facts

- **Total ProposedEdge nodes:** 5,667
- **Total Claim nodes:** 5,667  
- **Counts match:** YES (one ProposedEdge per Claim)
- **Orphaned nodes:** 0 (all have relationships)
- **Overlapping IDs:** 0 (separate ID spaces)
- **Created:** July 15, 2026 (18:10 - 19:08) - **Yesterday!**

### ProposedEdge Properties

All ProposedEdge nodes contain:
```
- claim_id              // Links to Claim node
- confidence            // Confidence score
- status                // Status tracking
- created_at            // Timestamp
- updated_at            // Timestamp
- edge_id               // Unique edge identifier
- relationship_type     // Type of relationship
- source_agent          // Which agent created it
- facet                 // Which facet
- source_entity_id      // Source entity
- target_entity_id      // Target entity
- claim_label           // Human-readable label
```

### Relationship Patterns

**Outgoing relationships:**
- `FROM` → source entity
- `TO` → target entity
- `EVIDENCED_BY` → evidence nodes

**Incoming relationships:**
- `ASSERTS_EDGE` ← Claim nodes

### Architecture Analysis

ProposedEdge represents **proposed relationships between entities** that are being claimed by the system. The architecture is:

```
Claim -[ASSERTS_EDGE]-> ProposedEdge -[FROM]-> Entity (source)
                                     -[TO]-> Entity (target)
                                     -[EVIDENCED_BY]-> Evidence
```

This is a **reification pattern** where the relationship itself is represented as a node so it can have:
- Properties (confidence, status, timestamps)
- Relationships to evidence
- Claim provenance tracking

### Recommendation: **KEEP ALL ProposedEdge NODES**

**Rationale:**
1. Created yesterday (July 15, 2026) - this is current, active architecture
2. All 5,667 nodes are connected (not orphaned)
3. They form a critical part of the claim/edge assertion system
4. Deleting them would break the claim-to-entity relationship structure

**This is NOT legacy architecture** - it's the current Phase 2 claim system in active use.

---

## 3. Duplicate Node Type Consolidation

### 3.1 PERSON → Person

**Current state:**
- `PERSON` (uppercase): 2 nodes
- `Person` (propercase): 5,630 nodes
- Nodes with both labels: 0

**PERSON Node Details:**

**Node 1:**
- Properties: `qid`, `entity_type`, `label`, `entity_cipher`, `created_at`
- Incoming relationships: 3
- Outgoing relationships: 0

**Node 2:**
- Properties: `qid`, `entity_type`, `label`, `description`, `entity_cipher`, `created_at`
- Incoming relationships: 9
- Outgoing relationships: 0

**Status:** ✅ Safe to consolidate

Both PERSON nodes have incoming relationships (3 and 9 respectively), meaning other nodes reference them. The consolidation will preserve all relationships.

**Consolidation Impact:**
- Total Person nodes after consolidation: 5,632
- Incoming relationships preserved: 12 total
- Outgoing relationships preserved: 0
- Risk: **Low** - simple label change

---

### 3.2 EVENT → Event

**Current state:**
- `EVENT` (uppercase): 6 nodes
- `Event` (propercase): 71 nodes
- Nodes with both labels: 0

**EVENT Node Details:**

**Node 1:** 
- Properties: `entity_type`, `label`, `entity_cipher`, `created_at`
- Relationships: 0 in, 0 out (orphaned)

**Node 2:**
- Properties: `qid`, `entity_type`, `label`, `entity_cipher`, `created_at`
- Relationships: 4 in, 0 out

**Node 3:**
- Properties: `qid`, `entity_type`, `label`, `entity_cipher`, `created_at`
- Relationships: 1 in, 0 out

**Node 4:**
- Properties: `qid`, `entity_type`, `label`, `entity_cipher`, `created_at`
- Relationships: 1 in, 0 out

**Node 5:**
- Properties: `qid`, `entity_type`, `label`, `entity_cipher`, `created_at`
- Relationships: 2 in, 0 out

**Node 6:**
- Properties: `qid`, `label`, `entity_cipher`, `date`, `subject`
- Relationships: 2 in, 0 out

**Status:** ✅ Safe to consolidate

5 of 6 EVENT nodes have incoming relationships. One node is orphaned but harmless.

**Consolidation Impact:**
- Total Event nodes after consolidation: 77
- Incoming relationships preserved: 10 total
- Outgoing relationships preserved: 0
- Risk: **Low** - simple label change

---

## 4. Cleanup Plan & Scripts

### Phase 1: Consolidate Duplicates ✅ READY

**Step 1: PERSON → Person**

Dry run available:
```bash
python node_cleanup.py --consolidate-person
```

This will:
1. Show preview of all 2 nodes to be consolidated
2. Ask for confirmation
3. Execute consolidation: `SET p:Person REMOVE p:PERSON`
4. Verify results

**Step 2: EVENT → Event**

Dry run available:
```bash
python node_cleanup.py --consolidate-event
```

This will:
1. Show preview of all 6 nodes to be consolidated
2. Ask for confirmation
3. Execute consolidation: `SET e:Event REMOVE e:EVENT`
4. Verify results

### Phase 2: Empty Node Types ⚠️ NO ACTION NEEDED

The 16 empty node types will automatically disappear from the schema once they have no nodes. Since they already have 0 nodes, they are effectively removed.

Optional documentation cleanup to remove references to:
- Activity, Dynasty, FacetCategory, FacetClaim, FacetedEntity
- Geometry, Human, Institution, LegalRestriction, Location
- Organization, PlaceVersion, PropertyMapping, PropertyType
- TemporalAnchor, Work

### Phase 3: ProposedEdge 🛑 DO NOT DELETE

**No action to be taken.** ProposedEdge is active, current architecture created yesterday.

---

## 5. Risk Assessment

### Low Risk (Proceed with confidence)
- ✅ PERSON → Person consolidation (2 nodes, 12 relationships)
- ✅ EVENT → Event consolidation (6 nodes, 10 relationships)

### No Risk (No action needed)
- ✅ Empty node types (already at 0 nodes)

### High Risk (Action: KEEP)
- 🛑 ProposedEdge deletion would break claim architecture
- 🛑 Material/Object deletion (user wants to keep for future use)

---

## 6. Rollback Strategy

### If Consolidation Issues Occur

**Problem:** PERSON consolidation causes issues
**Solution:** The original PERSON label can be restored if needed (though unlikely to be necessary)

**Problem:** EVENT consolidation causes issues
**Solution:** The original EVENT label can be restored if needed (though unlikely to be necessary)

**Best Practice:** Neo4j supports multiple labels per node, so the old labels can coexist with new ones temporarily if needed during transition.

---

## 7. Next Steps

### Immediate Actions (Ready to Execute)

1. ✅ **Run PERSON consolidation**
   ```bash
   python node_cleanup.py --consolidate-person
   ```
   Expected: 2 nodes consolidated, 5,632 total Person nodes

2. ✅ **Run EVENT consolidation**
   ```bash
   python node_cleanup.py --consolidate-event
   ```
   Expected: 6 nodes consolidated, 77 total Event nodes

3. ✅ **Verify consolidation**
   ```cypher
   MATCH (p:PERSON) RETURN count(p)  // Should return 0
   MATCH (e:EVENT) RETURN count(e)   // Should return 0
   MATCH (p:Person) RETURN count(p)  // Should return 5,632
   MATCH (e:Event) RETURN count(e)   // Should return 77
   ```

### Documentation Updates

1. Update schema documentation to remove 16 empty node types
2. Document ProposedEdge as active claim architecture (not legacy)
3. Update naming conventions to enforce CamelCase (Person, Event)

---

## 8. Summary Statistics

| Category | Before | After | Change |
|----------|--------|-------|--------|
| **PERSON nodes** | 2 | 0 | Consolidated → Person |
| **Person nodes** | 5,630 | 5,632 | +2 from PERSON |
| **EVENT nodes** | 6 | 0 | Consolidated → Event |
| **Event nodes** | 71 | 77 | +6 from EVENT |
| **Empty types** | 16 | 0 (auto-removed) | No action needed |
| **ProposedEdge** | 5,667 | 5,667 | **KEEP - Active architecture** |
| **Total cleanup** | 24 nodes | 24 nodes | Simple label changes |

---

## Appendix: Investigation Details

**Full investigation data:** `node_cleanup_investigation_report.json`

**Cypher scripts available:**
- `Cypher/node_cleanup_investigation.cypher` - Manual investigation queries
- `Cypher/node_consolidation.cypher` - Consolidation queries with dry-run mode

**Python script:**
- `node_cleanup.py` - Automated investigation and consolidation tool

**Database connection:** Configured via `.env` file
- NEO4J_URI: neo4j+s://ac63a8e5.databases.neo4j.io
- NEO4J_DATABASE: neo4j

---

**Report generated:** July 16, 2026  
**Investigator:** Automated Node Type Cleanup System  
**Status:** Investigation complete, ready for consolidation execution
