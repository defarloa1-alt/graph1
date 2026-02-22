# Deprecation Notice

**Date:** December 10, 2025  
**Status:** Files in this folder are DEPRECATED

---

## Deprecated Files

### 1. `Relationshp Types Table.csv`

**Original Purpose:** Roman Republic-specific relationship types  
**Deprecated Reason:** Merged into canonical_relationship_types.csv  
**Replacement:** Use `../canonical_relationship_types.csv`

**What was unique:**
- 12 Roman Republic domain-specific relationships
- Simple schema without directionality, parent relationships, or backbone alignment

**Migration Path:**
All relationships from this file have been integrated into the canonical list with proper:
- Directionality (forward/inverse/symmetric)
- Parent relationship hierarchy
- Backbone alignment (LCC/LCSH/FAST)
- Wikidata property mappings

---

### 2. `neo4j_relationships_deduplicated.csv`

**Original Purpose:** Streamlined relationship list  
**Deprecated Reason:** Missing critical metadata needed for Baseline Core 3.1 compliance  
**Replacement:** Use `../canonical_relationship_types.csv`

**What was missing:**
- Directionality information
- Parent relationship hierarchy
- Specificity levels
- Backbone alignment (LCC/LCSH/FAST)
- Status and versioning metadata

**Migration Path:**
Use the canonical CSV which includes all relationships with complete metadata.

---

## Why Deprecate?

### Problem: Multiple Sources of Truth
- 3+ different CSV files defining relationships
- Inconsistent Wikidata property mappings
- No clear canonical source
- Missing backbone alignment required by Baseline Core 3.1.md

### Solution: Single Canonical Source
- `canonical_relationship_types.csv` is now the **single source of truth**
- All relationships consolidated with:
  - ✅ Backbone alignment (LCC/LCSH/FAST)
  - ✅ Full Wikidata property mappings
  - ✅ Hierarchical structure (parent relationships)
  - ✅ Directionality metadata
  - ✅ Status and versioning
  - ✅ 236 total relationship types

---

## Migration Guide

### For Developers

**Old Code:**
```python
# Reading deprecated file
with open('relations/Relationshp Types Table.csv') as f:
    relationships = csv.DictReader(f)
```

**New Code:**
```python
# Reading canonical file
with open('relations/canonical_relationship_types.csv') as f:
    relationships = csv.DictReader(f)
```

### For Neo4j Queries

**Old:**
```cypher
// Direct relationship without registry
(source)-[:CONTROLLED]->(target)
```

**New:**
```cypher
// Relationship linked to PropertyRegistry
MATCH (reg:PropertyRegistry {property_id: 'REL_CONTROLLED'})
MATCH (source)-[rel:CONTROLLED]->(target)
CREATE (rel)-[:DEFINED_BY]->(registry)
```

### For Scripts

Run the loader to populate PropertyRegistry:
```bash
python relations/scripts/load_relationship_registry.py
```

---

## File Retention Policy

These deprecated files are kept for:
- **Historical reference** - Understanding evolution of schema
- **Audit trail** - Compliance and documentation
- **Rollback** - Emergency fallback if needed

**Do not use these files for new development.**

---

## Questions?

See:
- `../RELATIONSHIP_TYPES_AUDIT.md` - Full audit analysis
- `../TEMPORAL_GEO_RELATIONSHIPS_ANALYSIS.md` - Temporal/geographic corrections
- `../canonical_relationship_types.csv` - The canonical source
- `../scripts/load_relationship_registry.py` - Neo4j loader


