# Quick Reference: Using All 310 Relationship Types

**Updated**: 2026-02-16  
**Key Point**: ✅ All 310 relationship types are available NOW - no restrictions

---

## The Bottom Line

```python
# For NORMAL work - use RelationshipAssertion (access all 310 types)
from models import RelationshipAssertion, initialize_registry

# Initialize once at startup
initialize_registry(
    "Facets/facet_registry_master.json",
    "Relationships/relationship_types_registry_master.csv"
)

# Use ANY of the 310 types
military = RelationshipAssertion(
    rel_type="COMMANDED",  # ✅ Works
    subject_id="Q1048",
    object_id="Q123456"
)

genealogy = RelationshipAssertion(
    rel_type="PARENT_OF",  # ✅ Works
    subject_id="Q100",
    object_id="Q200"
)

intellectual = RelationshipAssertion(
    rel_type="INFLUENCED",  # ✅ Works
    subject_id="Q300",
    object_id="Q400"
)
```

---

## What is the V1 Kernel?

The **v1 kernel** is a **recommended baseline** of 25 relationship types for:
- Federation compatibility testing
- Cross-system baseline validation
- Guaranteed interoperability

**It is NOT a restriction.** Think of it as a "lowest common denominator" for federation.

---

## When to Use What

### Use `RelationshipAssertion` (99% of the time)

**For**: Normal work, any domain, any relationship type

```python
from models import RelationshipAssertion

# Works with ANY of the 310 types
rel = RelationshipAssertion(
    rel_type="COMMANDED",           # Military
    # OR rel_type="PARENT_OF",      # Genealogy
    # OR rel_type="INFLUENCED",     # Intellectual
    # OR rel_type="COMPOSER",       # Arts
    # OR rel_type="MEMBER_OF",      # Organizational
    subject_id="Q1",
    object_id="Q2",
    confidence=0.95
)
```

**Requirements**:
- Must call `initialize_registry()` once at startup
- Registry validates against actual relationship types in CSV

---

### Use `V1KernelAssertion` (Rarely - federation testing only)

**For**: Testing federation baseline compatibility

```python
from models import V1KernelAssertion

# Only accepts 25 baseline types
kernel_rel = V1KernelAssertion(
    rel_type="SAME_AS",        # ✅ In kernel
    # OR rel_type="LOCATED_IN", # ✅ In kernel
    # OR rel_type="CITES",      # ✅ In kernel
    subject_id="Q1",
    object_id="Q2"
)

# This will fail:
# V1KernelAssertion(rel_type="COMMANDED", ...)  # ❌ Not in 25-type kernel
# ^ Use RelationshipAssertion instead for COMMANDED
```

**Requirements**:
- Does NOT need registry initialization (self-contained)
- Validates against hardcoded 25-type set

---

## Available Relationship Types by Domain

### All 310 Types Are Available - Here Are Some Examples

**Military** (✅ Available):
- COMMANDED, FOUGHT_IN, ALLIED_WITH, CONQUERED, DEFEATED, BESIEGED, ...

**Genealogy** (✅ Available):
- PARENT_OF, CHILD_OF, SPOUSE_OF, SIBLING_OF, GRANDPARENT_OF, ...

**Intellectual/Influence** (✅ Available):
- INFLUENCED, DISPUTED, REFUTED, CITES_THEORY, ...

**Organizational** (✅ Available):
- MEMBER_OF, FOUNDED, DEPARTMENT_OF, REPORTS_TO, ...

**Arts/Performance** (✅ Available):
- COMPOSER, CREATOR, CREATION_OF, DESIGNED, ILLUSTRATED, ...

**Geographic** (✅ Available - includes v1 kernel):
- LOCATED_IN, BORDERS, CAPITAL_OF, CONTAINED_BY, PART_OF, ...

**Temporal** (✅ Available - includes v1 kernel):
- OCCURRED_AT, OCCURS_DURING, HAPPENED_BEFORE, CONTEMPORARY_WITH, ...

**Provenance** (✅ Available - includes v1 kernel):
- CITES, DERIVES_FROM, EXTRACTED_FROM, AUTHOR, ATTRIBUTED_TO, ...

**Total**: 310 types across all domains

---

## Demo: Multi-Domain Claim

```python
from models import Claim, RelationshipAssertion, FacetAssignment

# Mix relationship types freely - no restrictions
claim = Claim(
    claim_id="claim_caesar_001",
    cipher="abc123...",
    content="Julius Caesar commanded legions and influenced Roman politics",
    facets=[
        FacetAssignment(facet="military", confidence=0.95),
        FacetAssignment(facet="political", confidence=0.90),
    ],
    relationships=[
        RelationshipAssertion(
            rel_type="COMMANDED",      # Military domain
            subject_id="Q1048",
            object_id="Q123456"
        ),
        RelationshipAssertion(
            rel_type="INFLUENCED",     # Intellectual domain
            subject_id="Q1048",
            object_id="Q87"
        ),
        RelationshipAssertion(
            rel_type="MEMBER_OF",      # Organizational domain
            subject_id="Q1048",
            object_id="Q87"
        ),
    ],
    created_by="seed_agent"
)

# ✅ All relationship types validated
# ✅ No domain restrictions
```

---

## Registry Statistics

```
Total relationship types:  310
V1 kernel baseline:         25 (8.1% of total)
Additional types:          285 (91.9% of total)

✅ All 310 types validated and available
✅ No gates, no packages required
✅ Use any type immediately
```

---

## Testing Your Relationship Types

Run the full catalog demo to verify:

```powershell
python Python/models/demo_full_catalog.py
```

This demonstrates:
- ✅ Military relationships (COMMANDED, FOUGHT_IN, etc.)
- ✅ Genealogy relationships (PARENT_OF, SPOUSE_OF, etc.)
- ✅ Intellectual relationships (INFLUENCED, etc.)
- ✅ Organizational relationships (MEMBER_OF, FOUNDED, etc.)
- ✅ Arts relationships (CREATOR, COMPOSER, etc.)
- ✅ Multi-domain claims mixing relationship types
- ✅ V1 kernel vs full catalog comparison

---

## Summary

| Aspect | Status |
|--------|--------|
| Total relationship types | 310 ✅ |
| Available immediately | All 310 ✅ |
| Need domain packages | No ❌ |
| V1 kernel restriction | No - it's a baseline ⚠️ |
| Use for normal work | `RelationshipAssertion` ✅ |
| Use for federation testing | `V1KernelAssertion` (25 types) ⚠️ |

**You can use any of the 310 relationship types right now!**

---

## Files Reference

- **Main validation model**: [Python/models/validation_models.py](../Python/models/validation_models.py)
- **Registry loader**: [Python/models/registry_loader.py](../Python/models/registry_loader.py)
- **Full catalog demo**: [Python/models/demo_full_catalog.py](../Python/models/demo_full_catalog.py)
- **V1 kernel spec**: [Relationships/v1_kernel_specification.md](../Relationships/v1_kernel_specification.md)
- **Relationship registry**: [Relationships/relationship_types_registry_master.csv](../Relationships/relationship_types_registry_master.csv)
