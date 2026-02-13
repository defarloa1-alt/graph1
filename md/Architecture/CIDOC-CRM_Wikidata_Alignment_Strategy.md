# CIDOC-CRM and Wikidata Alignment Strategy

## Overview

This document outlines the strategy for aligning Chrystallum's relationship types and entity schema with both **CIDOC-CRM** (ISO 21127 standard for cultural heritage) and **Wikidata** properties, enabling interoperability with museum systems and linked data.

## Alignment Goals

1. **Triple Alignment**: Each relationship type should have:
   - Chrystallum relationship type (our native type)
   - Wikidata property (P-id) when available
   - CIDOC-CRM property when applicable

2. **Entity Alignment**: Each entity should have:
   - Chrystallum node type (Event, Human, Place, etc.)
   - Wikidata Q-id for the entity
   - CIDOC-CRM class (E5_Event, E21_Person, E53_Place, etc.)

3. **Preserve Chrystallum Features**: 
   - Keep our action structure (Goal/Trigger/Action/Result)
   - Maintain backbone alignment (FAST/LCC/LCSH/MARC)
   - Retain temporal/geographic backbone integration

## Relationship Type Alignment

### Mapping Strategy

For each relationship type in `canonical_relationship_types.csv`, we add:
- `cidoc_crm_property`: CIDOC-CRM property ID (e.g., "crm:P11", "crm:P7", "crm:P4")
- `cidoc_crm_class`: CIDOC-CRM class if relationship maps to an event class

### Key Mappings

#### Temporal Relationships

| Chrystallum | Wikidata | CIDOC-CRM | Notes |
|-------------|----------|-----------|-------|
| `WITHIN_TIMESPAN` | - | `P4_has_time-span` | Event → Time-Span |
| `DURING` | - | `P4_has_time-span` | Event → Time-Span |
| `START_EDGE` | - | `P82a_begin_of_the_begin` | Time-Span property |
| `END_EDGE` | - | `P82b_end_of_the_end` | Time-Span property |

#### Spatial Relationships

| Chrystallum | Wikidata | CIDOC-CRM | Notes |
|-------------|----------|-----------|-------|
| `LOCATED_IN` | `P131` | `P7_took_place_at` | Event → Place |
| `BORN_IN` | `P19` | `P7_took_place_at` (via E67_Birth) | Birth event → Place |
| `DIED_IN` | `P20` | `P7_took_place_at` (via E69_Death) | Death event → Place |
| `LIVED_IN` | - | `P74_has_current_or_former_residence` | Person → Place |

#### Participant Relationships

| Chrystallum | Wikidata | CIDOC-CRM | Notes |
|-------------|----------|-----------|-------|
| `PARTICIPATED_IN` | `P710` | `P11_had_participant` | Event → Person/Group |
| `COMMANDED` | - | `P11_had_participant` (with role) | Event → Person (role: commander) |
| `SERVED_UNDER` | - | `P11_had_participant` (with role) | Event → Person (role: subordinate) |

#### Causal Relationships

| Chrystallum | Wikidata | CIDOC-CRM | Notes |
|-------------|----------|-----------|-------|
| `CAUSED` | `P828` | `P15_was_influenced_by` | Effect → Cause (inverse) |
| `CAUSED_BY` | `P828` | `P15_was_influenced_by` | Effect → Cause |
| `RESULTED_IN` | - | `P10i_contains` | Super-event → Sub-event |
| `CONTRIBUTED_TO` | `P828` | `P15_was_influenced_by` | Contributing factor |

#### Authorship/Creation Relationships

| Chrystallum | Wikidata | CIDOC-CRM | Notes |
|-------------|----------|-----------|-------|
| `AUTHOR` | `P50` | `P14_carried_out_by` (via E12_Production) | Production event → Person |
| `CREATOR` | `P170` | `P14_carried_out_by` (via E12_Production) | Production event → Person |
| `ARCHITECT` | `P84` | `P14_carried_out_by` (via E12_Production) | Production event → Person |
| `WORK_OF` | `P50` | `P108i_was_produced_by` | Work → Production event |

#### Political/Control Relationships

| Chrystallum | Wikidata | CIDOC-CRM | Notes |
|-------------|----------|-----------|-------|
| `CONTROLLED` | `P17` | `P53_has_former_or_current_location` | Object → Place (for territories) |
| `GOVERNED` | - | `P11_had_participant` (via E7_Activity) | Governance activity → Person |
| `APPOINTED` | `P39` | `P11_had_participant` (via E7_Activity) | Appointment event → Person |

#### Familial Relationships

| Chrystallum | Wikidata | CIDOC-CRM | Notes |
|-------------|----------|-----------|-------|
| `CHILD_OF` | `P40` | `P98_was_born` (via E67_Birth) | Birth event → Parent |
| `SPOUSE_OF` | `P26` | `P11_had_participant` (via E7_Activity) | Marriage event → Person |
| `PARENT_OF` | `P40` | `P98_was_born` (via E67_Birth) | Birth event → Child |

## Entity Class Alignment

### Core Entity Mappings

| Chrystallum | Wikidata Type | CIDOC-CRM Class | Notes |
|-------------|---------------|-----------------|-------|
| `Event` | `Q1190554` (event) | `E5_Event` | Base event class |
| `Human` | `Q5` (human) | `E21_Person` | Individual person |
| `Organization` | `Q43229` (organization) | `E74_Group` or `E40_Legal_Body` | Groups/organizations |
| `Place` | `Q2221906` (place) | `E53_Place` | Geographic location |
| `Concept` | `Q151885` (concept) | `E28_Conceptual_Object` | Ideas, concepts |
| `Position` | `Q4164871` (position) | `E55_Type` | Types/positions |

### Specialized Event Classes

| Chrystallum Event Type | CIDOC-CRM Class | Notes |
|------------------------|-----------------|-------|
| Birth events | `E67_Birth` | Birth of person |
| Death events | `E69_Death` | Death of person |
| Production events | `E12_Production` | Creation of objects/works |
| Acquisition events | `E8_Acquisition` | Ownership changes |
| Move events | `E9_Move` | Spatial movement |
| Joining events | `E85_Joining` | Joining groups |
| Leaving events | `E86_Leaving` | Leaving groups |

## Implementation Strategy

### Phase 1: Add CIDOC-CRM Columns to CSV

Update `canonical_relationship_types.csv` to include:
- `cidoc_crm_property`: CIDOC-CRM property ID
- `cidoc_crm_class`: CIDOC-CRM class if relationship is an event
- `cidoc_crm_notes`: Notes on alignment

### Phase 2: Entity Property Alignment

Add to entity nodes:
```cypher
(entity:Event {
  // Chrystallum properties
  label: "Crossing of Rubicon",
  start_date: "-0049-01-10",
  
  // Wikidata alignment
  qid: "Q123456",
  
  // CIDOC-CRM alignment
  cidoc_crm_class: "E5_Event",
  cidoc_crm_properties: {
    "P4_has_time-span": "E52_Time-Span",
    "P7_took_place_at": "E53_Place",
    "P11_had_participant": ["E21_Person", "E74_Group"]
  }
})
```

### Phase 3: Relationship Alignment

Add to relationships:
```cypher
(event:Event)-[r:PARTICIPATED_IN {
  // Chrystallum properties
  role: "Commander",
  
  // Wikidata alignment
  wikidata_property: "P710",
  
  // CIDOC-CRM alignment
  cidoc_crm_property: "P11_had_participant",
  cidoc_crm_role: "P14.1_in_the_role_of"
}]->(person:Human)
```

## Benefits

### 1. Museum/Archival Interoperability
- Export/import CIDOC-CRM data
- Integrate with museum collection systems
- Share data with cultural heritage institutions

### 2. Linked Data Integration
- Query using CIDOC-CRM properties
- Export RDF/OWL compatible data
- Interoperate with semantic web tools

### 3. Standard Compliance
- ISO 21127:2023 compliance
- Academic research compatibility
- Tool ecosystem support

### 4. Query Flexibility
- Query by Chrystallum relationship types
- Query by Wikidata properties
- Query by CIDOC-CRM properties
- All three views available simultaneously

## Example: Complete Alignment

### "Caesar Crossed the Rubicon"

**Chrystallum Representation:**
```cypher
(crossing:Event {
  label: "Crossing of Rubicon",
  start_date: "-0049-01-10",
  qid: "Q_CROSSING_RUBICON",
  cidoc_crm_class: "E5_Event"
})

(caesar:Human {
  label: "Julius Caesar",
  qid: "Q1047",
  cidoc_crm_class: "E21_Person"
})

(rubicon:Place {
  label: "Rubicon River",
  qid: "Q_RUBICON",
  cidoc_crm_class: "E53_Place"
})

(crossing)-[:PARTICIPATED_IN {
  role: "Commander",
  wikidata_property: "P710",
  cidoc_crm_property: "P11_had_participant",
  cidoc_crm_role: "P14.1_in_the_role_of"
}]->(caesar)

(crossing)-[:LOCATED_IN {
  wikidata_property: "P131",
  cidoc_crm_property: "P7_took_place_at"
}]->(rubicon)

(crossing)-[:WITHIN_TIMESPAN {
  cidoc_crm_property: "P4_has_time-span"
}]->(timeSpan:TimeSpan {
  cidoc_crm_class: "E52_Time-Span",
  P82a_begin_of_the_begin: "-0049-01-10T00:00:00",
  P82b_end_of_the_end: "-0049-01-10T23:59:59"
})
```

**Query Examples:**

```cypher
// Query by Chrystallum type
MATCH (e:Event)-[:PARTICIPATED_IN]->(p:Human)
RETURN e, p

// Query by Wikidata property
MATCH (e)-[r]->(p)
WHERE r.wikidata_property = "P710"
RETURN e, r, p

// Query by CIDOC-CRM property
MATCH (e:E5_Event)-[r]->(p)
WHERE r.cidoc_crm_property = "P11_had_participant"
RETURN e, r, p
```

## Next Steps

1. **Update CSV**: Add `cidoc_crm_property` and `cidoc_crm_class` columns
2. **Create Mapping Script**: Generate alignment mappings programmatically
3. **Update Entity Creation**: Add CIDOC-CRM properties to entity nodes
4. **Update Relationship Creation**: Add CIDOC-CRM properties to relationships
5. **Documentation**: Create query examples for all three alignment types

## References

- CIDOC-CRM Specification: https://www.cidoc-crm.org/
- ISO 21127:2023 Standard
- Wikidata Property Documentation: https://www.wikidata.org/wiki/Wikidata:List_of_properties
- CIDOC-CRM Alignment Guide: See `arch/Cidoc/CIDOC-CRM_Explanation.md`


