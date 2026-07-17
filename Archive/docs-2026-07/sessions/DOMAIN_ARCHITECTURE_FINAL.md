# Domain Architecture - Final State

**Date:** July 16, 2026  
**Status:** ✅ OPERATIONAL

## Three Domains

### 1. ROMAN_REPUBLIC (v0.1.0)
**Scope:** Historical (509-27 BCE)  
**Children:** 93 SubjectConcepts  
**Status:** Active development  
**SFAs:** Military, Diplomatic, Biographic (18 total planned)  
**Dependencies:** `military_theory @ ^1.0.0`

Contains all Roman Republic knowledge:
- `sc_military` - Roman Army & Military Campaigns
- `sc_diplomacy` - Roman Diplomacy & Foreign Relations
- `sc_economy` - Roman Economy, Finance & Trade
- `sc_q17167_facet_*` - 15 facet-specific concepts
- ... (93 total)

### 2. MILITARY_THEORY (v1.1.0)
**Scope:** Theoretical (timeless)  
**Children:** 32 theory nodes  
**Status:** Active development (discovery-based)  
**Content:** Boyd OODA, Clausewitz (SPO structure)  
**Dependents:** `roman_republic`

Contains universal military principles:
- MilitaryPrinciple nodes (OODA Loop, etc.)
- SPO structure (Concept, Mechanism, Effect, Condition, Process, Target)
- Discovered from theoretical literature

### 3. GEOGRAPHY (v1.0.0)
**Scope:** Spatial (timeless)  
**Children:** 4 SubjectConcepts  
**Status:** Infrastructure (Place classification system)  
**Training:** TBD - to be discussed later  

Contains geographic classification nodes:
- `GEO_PHYS_FEATURES` - Mountains, rivers, islands (2,282 Places)
- `GEO_HYDROGRAPHY` - Water bodies (2,155 Places)
- `GEO_ADMIN_DIVISIONS` - Provinces, regions (1,137 Places)
- `GEO_POLITICAL_ENTITIES` - States, empires (1,604 Places)

Originally created by `bootstrap_geo_subject_concepts.py` to organize 44,193 Place nodes.

## Domain Structure

```
SubjectConceptRegistry
├─ TRACKS_DOMAIN → ROMAN_REPUBLIC (v0.1.0)
│  └─ DEPENDS_ON → MILITARY_THEORY @ ^1.0.0
│
├─ TRACKS_DOMAIN → MILITARY_THEORY (v1.1.0)
│
└─ TRACKS_DOMAIN → GEOGRAPHY (v1.0.0)
```

## Version Management

**Tool:** `DomainVersionManager` (Python API)  
**Location:** `scripts/system/domain_version_manager.py`

```python
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)

# Check status
deps = manager.get_dependencies('roman_republic')
history = manager.get_version_history('military_theory')

# Bump version
manager.bump_version('roman_republic', 'minor', 
                     changes=['Added diplomatic claims'])

# Check compatibility
compat = manager.check_compatibility('military_theory', '2.0.0')
```

## Key Files

```
scripts/system/
├── domain_version_manager.py              [Core version manager]
├── restructure_domain_hierarchy.py        [One-time migration]
└── migrate_dependency_to_domain.py        [Dependency migration]

DOMAIN_ARCHITECTURE_CORRECTED.md           [Implementation details]
DOMAIN_ARCHITECTURE_FINAL.md               [This file]
```

## Next Steps

### Immediate
- ✅ Domain hierarchy established
- ✅ Versioning at domain level
- ✅ SubjectConceptRegistry populated
- ✅ Dependencies migrated to Domain level

### Future (To Discuss)
- Geographic SFA responsibility and scope
- Training material for geographic knowledge
- Whether GEO domains should be under ROMAN_REPUBLIC or independent
- Integration with existing 44,193 Place nodes

## Summary

Successfully restructured to version at the **domain/subgraph level**:

| Domain | Version | Children | Status | Training |
|--------|---------|----------|--------|----------|
| ROMAN_REPUBLIC | v0.1.0 | 93 | Active | SFA training ongoing |
| MILITARY_THEORY | v1.1.0 | 32 | Active | Boyd, Clausewitz corpus |
| GEOGRAPHY | v1.0.0 | 4 | Infrastructure | TBD |

**Architecture:** Chrystallum as "GitHub for subgraphs" ✅
