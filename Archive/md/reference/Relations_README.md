# Canonical Relationship Types

**Status:** ✅ Production Ready  
**Version:** 1.0  
**Last Updated:** December 10, 2025

---

## Quick Start

### 1. **Use the Canonical CSV**

The **single source of truth** for all relationship types:

```
relations/canonical_relationship_types.csv
```

**Contains:**
- 236 relationship types across 26 categories
- Full backbone alignment (LCC/LCSH/FAST)
- Wikidata property mappings
- Hierarchical structure (parent relationships, specificity levels)
- Directionality metadata (forward/inverse/symmetric/unidirectional)

### 2. **Load into Neo4j PropertyRegistry**

```bash
# From relations/scripts/ directory
python load_relationship_registry.py

# Or with custom Neo4j credentials
python load_relationship_registry.py \
  --neo4j-uri bolt://localhost:7687 \
  --username neo4j \
  --password your_password
```

This creates `PropertyRegistry` nodes implementing §5.y from Baseline Core 3.1.md

### 3. **Verify Registry**

```bash
python load_relationship_registry.py --verify-only
```

---

## File Structure

```
relations/
├── canonical_relationship_types.csv          # CANONICAL SOURCE (use this!)
├── canonical_relationship_types_summary.json # Generation metadata
├── neo4j_relationships_bidirectional.csv     # Source file (kept for reference)
├── neo4j_entity_hierarchy.csv                # Entity types
├── README.md                                  # This file
├── RELATIONSHIP_TYPES_AUDIT.md               # Full consolidation analysis
├── TEMPORAL_GEO_RELATIONSHIPS_ANALYSIS.md    # Temporal/geographic validation
├── scripts/
│   ├── create_canonical_relationships.py     # Generator script
│   └── load_relationship_registry.py         # Neo4j loader
├── deprecated/
│   ├── Relationshp Types Table.csv           # DEPRECATED
│   ├── neo4j_relationships_deduplicated.csv  # DEPRECATED
│   └── DEPRECATION_NOTICE.md                 # Migration guide
└── docs/
    ├── 7-Relationship Types.md                
    ├── 7.1 Persisting Relationship Types as Registry Nodes.md
    ├── Clarification_Actions_vs_Relationship_Types.md
    └── Action_Structure_With_Wikidata_Example.md
```

---

## Key Corrections Applied

### 1. **Temporal Relationships** (PART_OF Issue Fixed)

❌ **Before:** "509 BCE" PART_OF "Roman Republic" (semantically wrong)

✅ **After:**
- `SUB_PERIOD_OF` / `CONTAINS_PERIOD` - period hierarchy
- `DURING` / `CONTAINS_EVENT` - event in period
- `OVERLAPS_WITH` - temporal overlap
- `WITHIN_TIMESPAN` - entity existence bounds

### 2. **Geographic Relationships** (Clarity Improved)

⚠️ **PART_OF** now documented with usage restrictions:
- Use only for true structural/administrative parthood
- Prefer `LOCATED_IN` for most geographic containment
- Added `RENAMED` / `RENAMED_TO` for place name changes

### 3. **New Relationships Added**

From Osci extraction experiment (26 new):
- **Linguistic:** SPOKE_LANGUAGE, LANGUAGE_OF
- **Cultural:** ASSIMILATED_TO, ASSIMILATED
- **Diplomatic:** APPEALED_TO, ACCEPTED_OFFER, SENT_ENVOYS_TO, etc.
- **Military:** GARRISONED, LEVELLED, SALLIED_FROM
- **Economic:** SOLD_INTO_SLAVERY, DISTRIBUTED_LAND_TO
- **Political:** SUBJUGATED, LOST_SOVEREIGNTY

From Roman Republic CSV (14 new):
- **Political:** VETOED, ADVISED, GOVERNED, OPPOSED, etc.
- **Social:** PATRON_OF, CLIENT_OF, OWNED, FREED_BY
- **Economic:** TAXED
- **Legal:** APPEALED_TO
- **Geographic:** CAMPAIGN_IN, FOUNDED

---

## Category Breakdown (Top 10)

| Rank | Category | Count |
|------|----------|-------|
| 1 | Political | 39 relationships |
| 2 | Military | 23 relationships |
| 3 | Geographic | 18 relationships |
| 4 | Familial | 13 relationships |
| 5 | Legal | 13 relationships |
| 6 | Authorship | 12 relationships |
| 7 | Diplomatic | 12 relationships |
| 8 | Economic | 12 relationships |
| 9 | Attribution | 11 relationships |
| 10 | Institutional | 9 relationships |

**Total:** 236 relationships across 26 categories

---

## Backbone Alignment

All relationship types are aligned to Library of Congress standards per Baseline Core 3.1.md:

| Standard | Purpose | Example |
|----------|---------|---------|
| **LCC** | Classification | "JA" (Political science) |
| **LCSH** | Subject headings | "Political science" |
| **FAST** | Faceted search | "1069263" |
| **Wikidata** | Global IDs | "P39" (position held) |

---

## Usage Examples

### Query PropertyRegistry in Neo4j

```cypher
// Get all geographic relationships
MATCH (reg:PropertyRegistry {category: 'Geographic'})
RETURN reg.relationship_type, reg.description, reg.wikidata_property
ORDER BY reg.relationship_type

// Get relationships with Wikidata properties
MATCH (reg:PropertyRegistry)
WHERE reg.wikidata_property <> ''
RETURN reg.category, count(reg) as count
ORDER BY count DESC

// Find hierarchical relationships
MATCH (reg:PropertyRegistry)
WHERE reg.parent_relationship <> ''
RETURN reg.relationship_type, reg.parent_relationship, reg.specificity_level
ORDER BY reg.specificity_level
```

### Use in Python

```python
import csv

# Read canonical relationships
with open('relations/canonical_relationship_types.csv') as f:
    reader = csv.DictReader(f)
    for rel in reader:
        print(f"{rel['relationship_type']} ({rel['category']})")
        print(f"  LCC: {rel['lcc_code']}")
        print(f"  FAST: {rel['fast_id']}")
        print(f"  Wikidata: {rel['wikidata_property']}")
```

### Link Relationships to Registry (LangGraph)

```python
# In your LangGraph persist node
def persist_to_neo4j(state):
    # ... node creation ...
    
    # Link relationship to PropertyRegistry
    query = """
    MATCH (registry:PropertyRegistry {property_id: $property_id})
    MATCH (source {id: $source_id})
    MATCH (target {id: $target_id})
    CREATE (source)-[rel:CONTROLLED {
      property_id: $property_id,
      confidence: $confidence,
      created_by_agent: $agent_id,
      timestamp: datetime()
    }]->(target)
    CREATE (rel)-[:DEFINED_BY]->(registry)
    """
```

---

## Geographic Relationships for Geo Folder

All geographic Cypher files should use these **canonical types only**:

### Location/Position
- `LOCATED_IN` / `LOCATION_OF` (P131)
- `BORN_IN` / `BIRTHPLACE_OF` (P19)
- `DIED_IN` / `DEATH_PLACE_OF` (P20)
- `LIVED_IN` / `RESIDENCE_OF`
- `CAPITAL_OF` / `HAS_CAPITAL` (P36)

### Movement
- `FLED_TO` / `FLED_FROM`
- `MIGRATED_TO` / `MIGRATED_FROM`
- `EXILED_TO` / `EXILED_FROM`

### Spatial
- `BORDERS` / `ADJACENT_TO` (P47)

### Historical
- `FOUNDED` / `FOUNDED_BY` (P112)
- `RENAMED` / `RENAMED_TO` (P1448)
- `CAMPAIGN_IN` (military geography)

---

## Temporal Relationships for Temporal Folder

Use these **canonical temporal types** (not PART_OF):

### Chronological Sequence
- `PRECEDED_BY` (P155)
- `FOLLOWED_BY` (P156)

### Period Containment
- `SUB_PERIOD_OF` - smaller period within larger
- `CONTAINS_PERIOD` - larger period contains smaller

### Event-Period
- `DURING` - event occurred during period
- `CONTAINS_EVENT` - period contains event

### Other
- `CONTEMPORARY_OF` - co-temporal (symmetric)
- `OVERLAPS_WITH` - temporal overlap (symmetric)
- `WITHIN_TIMESPAN` - entity bounded by timespan

**Note:** `start_time`, `end_time`, `point_in_time` are **node properties**, not relationships.

---

## Governance

### Single Source of Truth

**ONLY** `canonical_relationship_types.csv` is authoritative.

**DO NOT:**
- Create relationships not in canonical list
- Modify deprecated CSV files
- Use multiple sources

**DO:**
- Query PropertyRegistry for metadata
- Propose new relationships via pull request
- Update canonical CSV and regenerate registry

### Adding New Relationships

1. Edit `canonical_relationship_types.csv`
2. Run `python scripts/create_canonical_relationships.py` to validate
3. Run `python scripts/load_relationship_registry.py` to update Neo4j
4. Update documentation

### Versioning

- **Version:** Stored in CSV `version` column
- **Status:** `active`, `deprecated`, `proposed`
- **Audit Trail:** Git history + PropertyRegistry timestamps

---

## Architecture Alignment

This implementation follows **Baseline Core 3.1.md**:

### §3 Backbone Architecture
✅ LCC/LCSH/FAST/MARC alignment for all relationships

### §4 Hybrid ID System  
✅ Wikidata properties as canonical IDs where available

### §5 Agent Architecture
✅ PropertyRegistry nodes for agent lookup and validation

### §5.y Property & Edge Registry
✅ Relationships stored as registry nodes with metadata

---

## References

- **Baseline Core 3.1.md** - Core architecture specification
- **RELATIONSHIP_TYPES_AUDIT.md** - Full consolidation analysis
- **TEMPORAL_GEO_RELATIONSHIPS_ANALYSIS.md** - Semantic validation
- **7.1 Persisting Relationship Types as Registry Nodes.md** - Implementation pattern

---

## Support

For questions or issues:
1. Check `RELATIONSHIP_TYPES_AUDIT.md` for analysis
2. Review `deprecated/DEPRECATION_NOTICE.md` for migration
3. See `TEMPORAL_GEO_RELATIONSHIPS_ANALYSIS.md` for temporal/geo usage

---

**Last Generated:** December 10, 2025  
**Generator:** `scripts/create_canonical_relationships.py`  
**Source Commit:** [Your commit hash]


