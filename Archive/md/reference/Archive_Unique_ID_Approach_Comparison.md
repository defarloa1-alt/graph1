# Unique ID Approach Comparison

## Question

Which approach is better for generating unique IDs?

1. **Current Approach**: Hash or concatenation of (id, type, label, properties)
2. **Alternative Approach**: QID + concatenation of all Wikidata properties

---

## Approach 1: Current System (Hash/Concatenation)

### Current Implementation

**Mathematical Definition:**
$$unique\_id = f(id, type, label, P) = H(id \parallel type \parallel label \parallel sorted(P))$$

**Alternative (Readable Format):**
$$unique\_id = id \parallel "\_" \parallel type \parallel "\_" \parallel normalize(label)$$

### Examples

```
unique_id: 'Q11457_PRODUCT_COTTON'
unique_id: 'Q156138_HUM_BRUTUS'
unique_id: 'Q220_CITY_ROME'
unique_id: 'C_DICTATOR_POS_ROMANREPUBLIC'  // Chrystallum-only entities
```

### Pros

✅ **Works for all entities**
   - Supports both Wikidata entities (QIDs) and Chrystallum-only entities (C_*)
   - Not dependent on Wikidata existence

✅ **Human-readable**
   - Format: `QID_TYPE_LABEL` or `CID_TYPE_LABEL`
   - Easy to interpret and debug
   - Can identify entity type at a glance

✅ **Stable and deterministic**
   - Same entity → same unique_id
   - Doesn't change if Wikidata properties change
   - Predictable generation

✅ **Controlled length**
   - Concatenation approach: ~30-50 characters typically
   - Hash approach: Fixed length (32-64 chars)
   - Database-friendly

✅ **Property-independent**
   - Works even if properties are incomplete
   - Doesn't require fetching Wikidata data
   - Can be generated immediately during extraction

✅ **Schema evolution friendly**
   - Adding new properties doesn't break existing unique_ids
   - Easy to migrate

### Cons

❌ **May not catch subtle duplicates**
   - Different labels for same entity ("Rome" vs "Roma" vs "Roma, Italy")
   - Same entity with slightly different properties

❌ **Property changes don't affect uniqueness**
   - If entity properties change significantly, unique_id stays same
   - Could mask that entity definition has evolved

---

## Approach 2: QID + All Wikidata Properties

### Proposed Implementation

```python
unique_id = qid + "_" + hash(all_wikidata_properties)
# or
unique_id = qid + "_" + sorted(concatenated_properties)
```

### Example

```
Q11457_PROP1_VALUE1_PROP2_VALUE2_PROP3_VALUE3_...
Q156138_P31_Q5_P569_-509_P570_-509_P734_...
```

### Pros

✅ **More granular uniqueness**
   - Captures all Wikidata attributes
   - Different property sets → different unique_ids
   - Better for entities that evolve over time

✅ **Wikidata-aligned**
   - Directly reflects Wikidata's representation
   - Changes in Wikidata → unique_id changes
   - Can detect when entity definition has changed

✅ **Richer semantic information**
   - Unique ID encodes property information
   - Can extract some entity information from ID itself

### Cons

❌ **Only works for Wikidata entities**
   - Doesn't work for Chrystallum-only entities (C_*)
   - Would need separate system for non-Wikidata entities

❌ **Extremely long and unwieldy**
   - Wikidata entities can have 100+ properties
   - Unique IDs could be 1000+ characters
   - Database performance issues (indexing, storage)
   - Hard to read/debug

❌ **Unstable/unpredictable**
   - Changes when Wikidata updates properties
   - Same entity, different time → different unique_id
   - Breaks referential integrity if properties change

❌ **Requires Wikidata API calls**
   - Must fetch all properties from Wikidata first
   - Slow generation
   - Depends on external service availability
   - Cost (API rate limits)

❌ **Property order matters**
   - Must sort properties consistently
   - Complex normalization required
   - Edge cases with multi-valued properties

❌ **Schema evolution nightmare**
   - New Wikidata properties added → unique_id changes
   - Existing references break
   - Migration complexity

❌ **Over-specified**
   - Most use cases don't need property-level uniqueness
   - Entity-level uniqueness is usually sufficient
   - Adds complexity without proportional benefit

---

## Hybrid Approach

### Option 3: QID + Key Properties Only

```python
# Include only identity-determining properties
key_properties = ['P31', 'P569', 'P570', 'P373']  # instance of, birth, death, label
unique_id = qid + "_" + hash(sorted(key_properties))
```

**Pros:**
- More granular than current
- Still manageable length
- Captures essential identity information

**Cons:**
- Must decide which properties are "key"
- Still longer than current approach
- Still unstable if key properties change

---

## Recommendation: Current Approach (with enhancements)

### Why Current Approach is Better

1. ✅ **Works universally** - Handles both Wikidata and Chrystallum entities
2. ✅ **Human-readable** - Easy to understand and debug
3. ✅ **Performance** - Short, indexable, fast lookups
4. ✅ **Stable** - Doesn't change unexpectedly
5. ✅ **Practical** - Good enough uniqueness for most cases

### Suggested Enhancements

#### Enhancement 1: Normalize Labels More Aggressively

```python
def normalize_label(label):
    """Better normalization to catch duplicates."""
    # Remove accents, convert to lowercase
    normalized = unidecode(label).lower()
    # Remove common suffixes
    normalized = re.sub(r'\s+\(.*?\)', '', normalized)  # Remove parentheses
    normalized = re.sub(r',\s*(the|a|an)$', '', normalized)  # Remove articles
    return normalized.strip()
```

#### Enhancement 2: Content Hash for Deduplication

Keep `unique_id` simple, but add `content_hash` for deduplication:

```cypher
CREATE (entity {
  id: 'Q11457',
  unique_id: 'Q11457_PRODUCT_COTTON',  // Simple, stable, readable
  content_hash: 'abc123def456...',      // Hash of all properties for deduplication
  ...
})
```

**Query for duplicates:**
```cypher
MATCH (e)
WHERE e.content_hash = 'abc123def456...'
AND e.unique_id <> 'Q11457_PRODUCT_COTTON'
RETURN e
```

#### Enhancement 3: Multi-Level Uniqueness Check

```python
def check_entity_exists(entity):
    # Check 1: By unique_id (fast lookup)
    if exists_by_unique_id(entity.unique_id):
        return True
    
    # Check 2: By content_hash (catches property variations)
    if exists_by_content_hash(entity.content_hash):
        return True
    
    # Check 3: By QID + label (catches label variations)
    if exists_by_qid_and_label(entity.qid, entity.label):
        return True
    
    return False
```

---

## Comparison Table

| Criteria | Current Approach | QID + All Properties | QID + Key Properties |
|----------|-----------------|---------------------|---------------------|
| **Uniqueness** | Good | Excellent | Very Good |
| **Readability** | ✅ Excellent | ❌ Poor | ⚠️ Fair |
| **Length** | ✅ Short (30-50 chars) | ❌ Very Long (1000+ chars) | ⚠️ Medium (100-200 chars) |
| **Stability** | ✅ Stable | ❌ Unstable | ⚠️ Moderate |
| **Performance** | ✅ Fast | ❌ Slow | ⚠️ Moderate |
| **Universal** | ✅ Works for all | ❌ Wikidata only | ⚠️ Wikidata only |
| **Simplicity** | ✅ Simple | ❌ Complex | ⚠️ Moderate |
| **Maintainability** | ✅ Easy | ❌ Hard | ⚠️ Moderate |
| **API Dependency** | ✅ None | ❌ Required | ⚠️ Required |

---

## Real-World Example

### Entity: Cotton (Q11457)

**Current Approach:**
```
unique_id: "Q11457_PRODUCT_COTTON"
```
- ✅ Readable: Immediately know it's product "COTTON" with QID Q11457
- ✅ Short: 25 characters
- ✅ Stable: Won't change
- ✅ Fast: Can be generated instantly

**QID + All Properties Approach:**
```
unique_id: "Q11457_P31_Q11457_P279_Q11173_P361_P279_Q11173_P910_Q4167836_P1552_Q202864_P2579_Q373949... (continues for 500+ chars)"
```
- ❌ Unreadable: Can't interpret
- ❌ Extremely long: 500+ characters
- ❌ Unstable: Changes if Wikidata updates properties
- ❌ Slow: Requires Wikidata API call first

---

## Conclusion

**Recommendation: Keep Current Approach with Enhancements**

### Current Approach Wins Because:

1. ✅ **Practical superiority** - Good enough uniqueness for 99% of use cases
2. ✅ **Universal applicability** - Works for all entities, not just Wikidata
3. ✅ **Performance** - Fast, indexable, efficient
4. ✅ **Human-friendly** - Readable and debuggable
5. ✅ **Stability** - Doesn't break when external data changes

### Enhance Current Approach By:

1. **Better label normalization** - Catch "Rome" vs "Roma" duplicates
2. **Content hash for deduplication** - Detect property-level duplicates
3. **Multi-level existence checks** - Check unique_id, content_hash, and qid+label

### Don't Use QID + All Properties Because:

1. ❌ **Over-engineering** - Solves a problem that doesn't need solving
2. ❌ **Performance killer** - Long IDs hurt database performance
3. ❌ **Fragility** - Breaks when Wikidata updates
4. ❌ **Limited scope** - Only works for Wikidata entities

---

## Implementation Recommendation

```python
class Entity:
    def __init__(self, id, type, label, properties, qid=None):
        self.id = id
        self.type = type
        self.label = label
        self.properties = properties
        self.qid = qid
        
        # Primary unique ID (simple, stable, readable)
        self.unique_id = self._generate_unique_id()
        
        # Content hash for deduplication (detailed, property-aware)
        self.content_hash = self._generate_content_hash()
    
    def _generate_unique_id(self):
        """Simple, human-readable unique ID."""
        normalized_label = normalize_label(self.label)
        return f"{self.id}_{self.type}_{normalized_label}"
    
    def _generate_content_hash(self):
        """Hash of all properties for deduplication."""
        import hashlib
        content = f"{self.id}|{self.type}|{self.label}|{sorted(self.properties.items())}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def check_exists(self, db):
        """Multi-level existence check."""
        # Check 1: unique_id (fast)
        if db.exists_by_unique_id(self.unique_id):
            return True
        
        # Check 2: content_hash (catches variations)
        if db.exists_by_content_hash(self.content_hash):
            return True
        
        # Check 3: qid + normalized label (catches label variations)
        if self.qid and db.exists_by_qid_and_label(self.qid, self.label):
            return True
        
        return False
```

This gives you:
- ✅ Fast, readable unique_id for primary identification
- ✅ Detailed content_hash for deduplication
- ✅ Multi-level duplicate detection
- ✅ Best of both worlds without the downsides




