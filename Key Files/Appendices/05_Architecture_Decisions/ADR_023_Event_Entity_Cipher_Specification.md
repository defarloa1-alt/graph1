# ADR 023: Event Entity Cipher Specification

**Status:** Proposed  
**Date:** 2026-07-16  
**Authors:** Chrystallum Architecture Team  
**Depends On:** ADR 020 (Chrystallum Classification System), ADR 022 (Multi-Agent Canonical Entity Claims)  

## Context

ADR 022 establishes the **Canonical Entity + Facet-Scoped Claims** architecture, which requires **entity deduplication** before SFAs write to the graph. The existing **3-tier entity cipher system** (ADR 020, `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md`) provides:

- **Tier 1 (Entity Cipher):** `ent_{type_prefix}_{resolved_id}` — cross-subgraph join key
- **Tier 2 (Faceted Entity Cipher):** `fent_{facet_prefix}_{base_qid}_{subjectconcept_id}` — subgraph address
- **Tier 3 (Claim Cipher):** Assertion-specific identifier (see `CLAIM_ID_ARCHITECTURE.md`)

**Current limitation:** Entity cipher formats are defined for Person, Place, Concept, but **not for Events, Periods, or Works**.

**Requirement:** Extend the entity cipher system to support **all first-class Chrystallum entity types** to enable canonical deduplication.

## Decision

### Entity Type Taxonomy

Chrystallum recognizes **six first-class entity types**:

| Entity Type | CIDOC-CRM Class | Examples | Cipher Prefix |
|-------------|-----------------|----------|---------------|
| **Person** | E21_Person | Julius Caesar, Cicero, Cleopatra | `per` |
| **Place** | E53_Place | Rome, Rubicon, Forum | `plc` |
| **Event** | E5_Event | Battle of Pharsalus, Crossing Rubicon | `evt` |
| **Period** | E4_Period | Roman Republic, Julio-Claudian Dynasty | `prd` |
| **Concept** | E55_Type / E89_Propositional_Object | Land reform, dignitas, optimates | `con` |
| **Work** | E73_Information_Object | De Bello Gallico, Ab Urbe Condita | `wrk` |

### Tier 1 Entity Cipher Format

**General Pattern:**
```
ent_{type_prefix}_{resolved_id}
```

Where `resolved_id` follows the **authority cascade**:
1. **Wikidata QID** (if available) — e.g., `Q40979`
2. **Content-based hash** (if no QID) — e.g., SHA256 of canonical properties

### Authority Cascade Specification

For entities **with** Wikidata QIDs:

```python
def generate_entity_cipher_with_qid(entity_type: str, qid: str) -> str:
    """
    Generate Tier 1 entity cipher for entities with Wikidata QIDs.
    
    Args:
        entity_type: One of PERSON, PLACE, EVENT, PERIOD, CONCEPT, WORK
        qid: Wikidata QID (e.g., 'Q40979')
    
    Returns:
        Entity cipher (e.g., 'ent_evt_Q40979')
    """
    type_prefix = ENTITY_TYPE_PREFIXES[entity_type]
    return f"ent_{type_prefix}_{qid}"

# Examples:
# Person: ent_per_Q1048 (Julius Caesar)
# Place: ent_plc_Q220 (Rome)
# Event: ent_evt_Q40979 (Crossing Rubicon)
# Period: ent_prd_Q17167 (Roman Republic)
# Concept: ent_con_Q186290 (optimates)
# Work: ent_wrk_Q214304 (De Bello Gallico)
```

For entities **without** Wikidata QIDs:

```python
import hashlib
from typing import Dict, Any

def generate_entity_cipher_content_hash(
    entity_type: str, 
    canonical_properties: Dict[str, Any]
) -> str:
    """
    Generate Tier 1 entity cipher for entities without Wikidata QIDs.
    Uses SHA256 hash of canonical properties.
    
    Args:
        entity_type: One of PERSON, PLACE, EVENT, PERIOD, CONCEPT, WORK
        canonical_properties: Dictionary of identifying properties
    
    Returns:
        Entity cipher (e.g., 'ent_evt_8a3f2b1c...')
    """
    type_prefix = ENTITY_TYPE_PREFIXES[entity_type]
    
    # Canonical property sets by type
    canonical_keys = {
        'PERSON': ['name', 'birth_date', 'birth_place'],
        'PLACE': ['name', 'latitude', 'longitude', 'feature_type'],
        'EVENT': ['name', 'date', 'location', 'participants'],
        'PERIOD': ['name', 'start_date', 'end_date', 'geographic_scope'],
        'CONCEPT': ['label', 'definition', 'domain'],
        'WORK': ['title', 'author', 'date', 'work_type']
    }
    
    # Extract canonical values in sorted order for deterministic hashing
    keys = canonical_keys.get(entity_type, [])
    values = [str(canonical_properties.get(k, '')) for k in sorted(keys)]
    
    # Generate hash
    content = '|'.join(values).encode('utf-8')
    hash_digest = hashlib.sha256(content).hexdigest()[:16]  # First 16 chars
    
    return f"ent_{type_prefix}_{hash_digest}"

# Example:
# Event without QID:
# canonical_properties = {
#     'name': 'Caesar addresses troops at Rubicon',
#     'date': '-49-01-10',
#     'location': 'Rubicon River',
#     'participants': 'Caesar, Legio XIII Gemina'
# }
# Result: ent_evt_8a3f2b1c4d5e6f7g
```

### Event-Specific Cipher Rules

Events have unique challenges:
1. **Granularity**: Events can be atomic (Caesar crosses Rubicon) or aggregate (Gallic Wars)
2. **Date precision**: Dates may be exact, approximate, or ranges
3. **Location**: Some events are point-based, others span regions
4. **Participants**: Actor-centric vs. structural events

**Canonical Properties for Event Cipher (when QID unavailable):**

```python
EVENT_CANONICAL_PROPERTIES = [
    'name',           # Primary name/label
    'date',           # ISO date or date range (e.g., '-49-01-10' or '-58/-50')
    'location',       # Primary location name or coordinate
    'participants'    # Key actors (semicolon-separated, sorted alphabetically)
]

# Example 1: Point event
{
    'name': 'Caesar crossing the Rubicon',
    'date': '-49-01-10',
    'location': 'Rubicon River',
    'participants': 'Caesar; Legio XIII Gemina'
}
# Cipher: ent_evt_<hash_of_above>

# Example 2: Aggregate event
{
    'name': 'Gallic Wars',
    'date': '-58/-50',
    'location': 'Gaul',
    'participants': 'Caesar; Gallic tribes; Roman legions'
}
# Cipher: ent_evt_<hash_of_above>
```

**Date normalization:**
- Point dates: ISO format (YYYY-MM-DD) with BCE years as negative: `-49-01-10`
- Date ranges: `<start>/<end>` format: `-58/-50`
- Approximate dates: `~<year>` format: `~100` (circa 100 CE)
- Unknown precision: Use available precision, pad with zeros: `-49-01-00` (January 49 BCE, day unknown)

### Period-Specific Cipher Rules

Periods are temporal spans with cultural/political significance.

**Canonical Properties for Period Cipher (when QID unavailable):**

```python
PERIOD_CANONICAL_PROPERTIES = [
    'name',              # Primary name
    'start_date',        # ISO date or year
    'end_date',          # ISO date or year (may be 'ongoing' for current periods)
    'geographic_scope'   # Geographic extent (e.g., 'Rome and Italy', 'Mediterranean')
]

# Example:
{
    'name': 'Late Roman Republic',
    'start_date': '-133',
    'end_date': '-27',
    'geographic_scope': 'Rome and territories'
}
# Cipher: ent_prd_<hash_of_above>
```

### Work-Specific Cipher Rules

Works are information objects (texts, inscriptions, documents).

**Canonical Properties for Work Cipher (when QID unavailable):**

```python
WORK_CANONICAL_PROPERTIES = [
    'title',      # Primary title
    'author',     # Author name (normalized)
    'date',       # Composition or publication date
    'work_type'   # E.g., 'literary_work', 'inscription', 'law', 'speech'
]

# Example:
{
    'title': 'Commentarii de Bello Gallico',
    'author': 'Caesar',
    'date': '-51',
    'work_type': 'literary_work'
}
# Cipher: ent_wrk_<hash_of_above>
```

## Implementation

### Update `scripts/tools/entity_cipher.py`

Add entity type prefixes and canonical property definitions:

```python
# Entity type prefixes (extend existing)
ENTITY_TYPE_PREFIXES = {
    "PERSON": "per",
    "PLACE": "plc",
    "EVENT": "evt",       # NEW
    "PERIOD": "prd",      # NEW
    "CONCEPT": "con",
    "WORK": "wrk",        # NEW
    "POLITY": "pol",      # Alias for political entity (subtype of CONCEPT)
}

# Canonical properties by entity type
CANONICAL_PROPERTIES = {
    "PERSON": ['name', 'birth_date', 'birth_place'],
    "PLACE": ['name', 'latitude', 'longitude', 'feature_type'],
    "EVENT": ['name', 'date', 'location', 'participants'],
    "PERIOD": ['name', 'start_date', 'end_date', 'geographic_scope'],
    "CONCEPT": ['label', 'definition', 'domain'],
    "WORK": ['title', 'author', 'date', 'work_type'],
}

def generate_entity_cipher(
    entity_type: str,
    qid: Optional[str] = None,
    canonical_properties: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate Tier 1 entity cipher.
    
    Priority:
    1. If qid provided: ent_{type_prefix}_{qid}
    2. If canonical_properties provided: ent_{type_prefix}_{content_hash}
    3. Otherwise: raise ValueError
    """
    if entity_type not in ENTITY_TYPE_PREFIXES:
        raise ValueError(f"Unknown entity_type: {entity_type}")
    
    type_prefix = ENTITY_TYPE_PREFIXES[entity_type]
    
    # Priority 1: QID
    if qid:
        return f"ent_{type_prefix}_{qid}"
    
    # Priority 2: Content hash
    if canonical_properties:
        keys = CANONICAL_PROPERTIES.get(entity_type, [])
        values = [str(canonical_properties.get(k, '')) for k in sorted(keys)]
        content = '|'.join(values).encode('utf-8')
        hash_digest = hashlib.sha256(content).hexdigest()[:16]
        return f"ent_{type_prefix}_{hash_digest}"
    
    raise ValueError("Must provide either qid or canonical_properties")
```

### Entity Deduplication Query

Before creating an entity, check for existing cipher:

```cypher
// Check for existing entity
MATCH (e)
WHERE e.entity_cipher = $cipher
   OR (e.qid IS NOT NULL AND e.qid = $qid)
RETURN e

// If not found, create canonical entity
CREATE (e:Event {
  entity_cipher: $cipher,
  qid: $qid,
  label: $name,
  date: $date,
  location: $location,
  cidoc_class: 'E5_Event',
  created_at: timestamp()
})
```

## Testing Strategy

### Unit Tests

```python
def test_event_cipher_with_qid():
    cipher = generate_entity_cipher('EVENT', qid='Q40979')
    assert cipher == 'ent_evt_Q40979'

def test_event_cipher_content_hash():
    props = {
        'name': 'Caesar crossing the Rubicon',
        'date': '-49-01-10',
        'location': 'Rubicon River',
        'participants': 'Caesar; Legio XIII Gemina'
    }
    cipher1 = generate_entity_cipher('EVENT', canonical_properties=props)
    cipher2 = generate_entity_cipher('EVENT', canonical_properties=props)
    
    # Same properties should generate same cipher (deterministic)
    assert cipher1 == cipher2
    assert cipher1.startswith('ent_evt_')

def test_event_cipher_collision_resistance():
    props1 = {'name': 'Event A', 'date': '-49-01-10', 'location': 'Rome', 'participants': 'Caesar'}
    props2 = {'name': 'Event B', 'date': '-49-01-10', 'location': 'Rome', 'participants': 'Caesar'}
    
    cipher1 = generate_entity_cipher('EVENT', canonical_properties=props1)
    cipher2 = generate_entity_cipher('EVENT', canonical_properties=props2)
    
    # Different names should generate different ciphers
    assert cipher1 != cipher2
```

### Integration Tests

```python
def test_entity_deduplication_neo4j():
    """Test that duplicate entities are prevented."""
    # Create first event
    cipher1 = generate_entity_cipher('EVENT', qid='Q40979')
    create_event_node(cipher1, label='Caesar crossing Rubicon')
    
    # Attempt to create duplicate
    cipher2 = generate_entity_cipher('EVENT', qid='Q40979')
    result = create_event_node(cipher2, label='Caesar crossing Rubicon')
    
    # Should return existing node, not create new one
    assert result.existing_node == True
    
    # Graph should have exactly 1 node
    count = query_neo4j("MATCH (e:Event {qid: 'Q40979'}) RETURN count(e)")
    assert count == 1
```

## Consequences

### Positive

1. **Enables Entity Deduplication**: SFAs can check for existing entities via cipher
2. **Uniform Pattern**: All entity types follow same cipher logic
3. **QID Priority**: Wikidata QIDs provide highest-authority deduplication key
4. **Content-Addressable**: Entities without QIDs still get stable ciphers
5. **Deterministic**: Same properties always generate same cipher (reproducible)

### Negative

1. **Hash Collisions**: Content-based ciphers have theoretical collision risk (mitigated by SHA256)
2. **Property Normalization Required**: Canonical properties must be consistently formatted
3. **Cipher Changes**: If canonical properties change, cipher changes (versioning needed)

### Neutral

1. **16-char Hash Limit**: Chosen for readability vs. collision resistance trade-off

## Monitoring

Track cipher generation and collision rates:

```python
METRICS = {
    'ciphers_generated_total': Counter,
    'ciphers_with_qid': Counter,
    'ciphers_with_content_hash': Counter,
    'deduplication_hits': Counter,
    'deduplication_misses': Counter,
}
```

## References

1. **ADR 020** - Chrystallum Classification System
2. **ADR 022** - Multi-Agent Canonical Entity Claims Architecture
3. **ENTITY_CIPHER_FOR_VERTEX_JUMPS.md** - Original 3-tier cipher specification
4. **CIDOC-CRM** - Cultural heritage ontology (E5 Event, E4 Period, E73 Work)

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-16 | 0.1 | Initial draft |

## Appendix: Complete Entity Type Mapping

| Chrystallum Type | CIDOC-CRM | Wikidata Class | Cipher Prefix | Example |
|------------------|-----------|----------------|---------------|---------|
| PERSON | E21_Person | Q5 (human) | `per` | ent_per_Q1048 (Caesar) |
| PLACE | E53_Place | Q82794 (geographic location) | `plc` | ent_plc_Q220 (Rome) |
| EVENT | E5_Event | Q1656682 (event) | `evt` | ent_evt_Q40979 (Rubicon) |
| PERIOD | E4_Period | Q186081 (time period) | `prd` | ent_prd_Q17167 (Republic) |
| CONCEPT | E55_Type / E89_Propositional_Object | Q151885 (concept) | `con` | ent_con_Q186290 (optimates) |
| WORK | E73_Information_Object | Q386724 (work) | `wrk` | ent_wrk_Q214304 (De Bello Gallico) |
