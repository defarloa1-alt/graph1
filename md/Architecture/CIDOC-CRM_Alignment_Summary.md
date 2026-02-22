# CIDOC-CRM Alignment Summary

## Overview

Successfully added CIDOC-CRM property and class alignments to the canonical relationship types CSV, enabling triple alignment: **Chrystallum | Wikidata | CIDOC-CRM**.

## Statistics

- **Total relationship types**: 236
- **With CIDOC-CRM alignment**: 55 (23.3%)
- **Without CIDOC-CRM alignment**: 181

## Alignment Coverage

### Well-Aligned Categories

**Temporal** (100% coverage):
- `PART_OF` â†’ `P86_falls_within`
- `DURING` â†’ `P4_has_time-span`
- `START_EDGE` â†’ `P82a_begin_of_the_begin`
- `END_EDGE` â†’ `P82b_end_of_the_end`
- `CONTAINS_EVENT` â†’ `P10i_contains`
- `SUB_PERIOD_OF` â†’ `P10_falls_within`

**Spatial** (High coverage):
- `LOCATED_IN` â†’ `P7_took_place_at`
- `BORN_IN` â†’ `P7_took_place_at` (E67_Birth)
- `DIED_IN` â†’ `P7_took_place_at` (E69_Death)
- `LIVED_IN` â†’ `P74_has_current_or_former_residence`

**Participants** (High coverage):
- `PARTICIPATED_IN` â†’ `P11_had_participant`
- `COMMANDED` â†’ `P11_had_participant` (with role qualifier)
- `BATTLED_IN` â†’ `P11_had_participant`

**Causal** (High coverage):
- `CAUSED` â†’ `P15_was_influenced_by`
- `CONTRIBUTED_TO` â†’ `P15_was_influenced_by`
- `RESULTED_IN` â†’ `P10i_contains`

**Authorship** (High coverage):
- `AUTHOR` â†’ `P14_carried_out_by` (E12_Production)
- `CREATOR` â†’ `P14_carried_out_by` (E12_Production)
- `WORK_OF` â†’ `P108i_was_produced_by` (E12_Production)

### Categories Needing More Alignment

**Diplomatic**: Most relationships don't have direct CIDOC-CRM equivalents (use generic E7_Activity)

**Economic**: Some relationships map to E8_Acquisition, but many are Chrystallum-specific

**Legal**: Some relationships could map to E7_Activity with qualifiers

**Social**: Relationships like patron-client are Chrystallum-specific

## CSV Structure

The `canonical_relationship_types.csv` now includes:

1. **Existing columns**:
   - `category`, `relationship_type`, `description`
   - `wikidata_property` (P-id)
   - `directionality`, `parent_relationship`, `specificity_level`
   - `status`, `note`, `source`, `version`

2. **New CIDOC-CRM columns**:
   - `cidoc_crm_property`: CIDOC-CRM property ID (e.g., "crm:P11", "crm:P7", "crm:P4")
   - `cidoc_crm_class`: CIDOC-CRM class if relationship maps to event class (e.g., "E67_Birth", "E12_Production")
   - `cidoc_crm_notes`: Notes on alignment (role qualifiers, inverse properties, etc.)

## Usage Examples

### Query by CIDOC-CRM Property

```cypher
// Find all relationships using CIDOC-CRM crm:P11 (had participant)
MATCH (e:Event)-[r]->(p)
WHERE r.cidoc_crm_property = "P11_had_participant"
RETURN e, r, p
```

### Query by CIDOC-CRM Class

```cypher
// Find all birth events (E67_Birth)
MATCH (e:Event)
WHERE e.cidoc_crm_class = "E67_Birth"
RETURN e
```

### Triple Alignment Query

```cypher
// Query using any of the three alignment types
MATCH (e:Event)-[r]->(p:Human)
WHERE r.wikidata_property = "P710" 
   OR r.cidoc_crm_property = "P11_had_participant"
   OR type(r) = "PARTICIPATED_IN"
RETURN e, r, p
```

## Next Steps

1. **Expand Mappings**: Add more CIDOC-CRM alignments for remaining 181 relationship types
2. **Entity Alignment**: Add CIDOC-CRM class properties to entity nodes
3. **Query Tools**: Create utility functions for CIDOC-CRM-aligned queries
4. **Export Functions**: Add RDF/OWL export using CIDOC-CRM properties
5. **Documentation**: Create query examples for museum/archival integration

## Files

- **`Relationships/relationship_types_registry_master.csv`**: Updated with CIDOC-CRM columns
- **`scripts/backbone/relations/add_cidoc_crm_alignment.py`**: Script to add alignments
- **`Docs/architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`**: Full strategy document

## References

- CIDOC-CRM Specification: https://www.cidoc-crm.org/
- ISO 21127:2023 Standard
- CIDOC-CRM Explanation: `arch/Cidoc/CIDOC-CRM_Explanation.md`



