# Domain Architecture - CORRECTED

**Status:** ✅ RESTRUCTURED  
**Date:** July 16, 2026

## Problem Identified

The initial versioning implementation was incorrect:
- ❌ Versioning individual SubjectConcept nodes (105 of them)
- ❌ Flat structure with no hierarchy
- ❌ SubjectConceptRegistry empty (no relationships)
- ❌ No clear domain/subgraph boundaries

## Correct Architecture

**Versioning at DOMAIN/SUBGRAPH level** (as user intended):

```
SubjectConceptRegistry
├── TRACKS_DOMAIN -> Domain:ROMAN_REPUBLIC (v0.1.0)
│   ├── CONTAINS -> sc_military
│   ├── CONTAINS -> sc_diplomacy
│   ├── CONTAINS -> sc_economy
│   ├── CONTAINS -> sc_q17167_facet_military
│   └── ... (93 SubjectConcepts total)
│
├── TRACKS_DOMAIN -> Domain:MILITARY_THEORY (v1.1.0)
│   ├── CONTAINS -> MilitaryPrinciple:OODA Loop
│   ├── CONTAINS -> Concept:decision cycle
│   ├── CONTAINS -> Mechanism nodes
│   └── ... (32 theory nodes total)
│
└── TRACKS_DOMAIN -> Domain:GEOGRAPHY (v1.0.0)
    ├── CONTAINS -> GEO_ADMIN_DIVISIONS
    ├── CONTAINS -> GEO_HYDROGRAPHY
    ├── CONTAINS -> GEO_PHYS_FEATURES
    └── CONTAINS -> GEO_POLITICAL_ENTITIES
```

## Current State After Restructure

### Domain Nodes

| Domain ID | Label | Version | Scope | Children | Type |
|-----------|-------|---------|-------|----------|------|
| `roman_republic` | Roman Republic | v0.1.0 | historical | 93 | SubjectConcepts |
| `military_theory` | Military Theory | v1.1.0 | theoretical | 32 | Theory nodes |
| `geography` | Geography | v1.0.0 | spatial | 4 | SubjectConcepts |

### Domain Dependencies

```
roman_republic (v0.1.0)
  └── DEPENDS_ON -> military_theory @ ^1.0.0
```

### SubjectConceptRegistry

Now properly populated:
- 3 domains tracked via `:TRACKS_DOMAIN` relationships
- Each domain contains its child nodes via `:CONTAINS`

## Key Changes Made

### 1. Created Domain Nodes

Created `:Domain` label for top-level subgraphs:

```cypher
(:Domain {
  domain_id: 'roman_republic',
  label: 'Roman Republic',
  version: '0.1.0',
  scope: 'historical',
  period: '509-27 BCE',
  versioned: true
})
```

### 2. Organized Hierarchy

All SubjectConcept nodes organized under domains:

- **ROMAN_REPUBLIC** contains:
  - All `sc_*` prefixed SubjectConcepts (93 total)
  - Topics like military, diplomacy, economy, etc.
  - All `sc_q17167_*` facet-specific concepts

- **MILITARY_THEORY** contains:
  - MilitaryPrinciple nodes (OODA Loop, etc.)
  - SPO structure nodes (Concept, Mechanism, Effect, etc.)
  - Total: 32 theory nodes

- **GEOGRAPHY** contains:
  - GEO_ADMIN_DIVISIONS
  - GEO_HYDROGRAPHY
  - GEO_PHYS_FEATURES
  - GEO_POLITICAL_ENTITIES

### 3. Linked to Registry

SubjectConceptRegistry now tracks all domains:

```cypher
(SubjectConceptRegistry)-[:TRACKS_DOMAIN]->(Domain)
```

### 4. Migrated Dependencies

Moved `DEPENDS_ON` from SubjectConcept to Domain level:

```cypher
// Old (wrong)
(SubjectConcept {subject_id: 'roman_republic'})
  -[:DEPENDS_ON]->
(SubjectConcept {subject_id: 'military_theory'})

// New (correct)
(Domain {domain_id: 'roman_republic'})
  -[:DEPENDS_ON {version_spec: '^1.0.0'}]->
(Domain {domain_id: 'military_theory'})
```

## Version Management

### New Tool: DomainVersionManager

Located at `scripts/system/domain_version_manager.py`

Works with **Domain** nodes, not SubjectConcept nodes:

```python
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)

# Bump domain version
manager.bump_version('roman_republic', 'minor', 
                     changes=['Added new claims'])

# Add dependency
manager.add_dependency('roman_republic', 'military_theory', '^1.0.0')

# Check compatibility
compat = manager.check_compatibility('military_theory', '2.0.0')
```

### CLI Tool Update Needed

The existing `version_cli.py` still queries SubjectConcept nodes. Need to update it to use DomainVersionManager and query Domain nodes.

## Conceptual Model

### What is a Domain?

A **Domain** is a versioned, top-level knowledge subgraph:

- **ROMAN_REPUBLIC**: All knowledge about the Roman Republic
  - Contains 93 subject areas (military, political, economic, etc.)
  - Historical scope, 509-27 BCE
  - Version: 0.1.0 (early stage)

- **MILITARY_THEORY**: Universal military principles
  - Contains discovered theories (Boyd, Clausewitz, etc.)
  - Theoretical scope, timeless
  - Version: 1.1.0 (Boyd + Clausewitz)
  - Discovery-based (grows as SFAs read literature)

- **GEOGRAPHY**: Spatial and geographic concepts
  - Contains geographic taxonomies
  - Spatial scope, timeless
  - Version: 1.0.0

### What is a SubjectConcept?

A **SubjectConcept** is a topic or area **within** a domain:

- `sc_military`: Roman Army & Military Campaigns (within ROMAN_REPUBLIC)
- `sc_diplomacy`: Roman Diplomacy & Foreign Relations (within ROMAN_REPUBLIC)
- `sc_q17167_facet_military`: Military facet (within ROMAN_REPUBLIC)
- `GEO_HYDROGRAPHY`: Water bodies (within GEOGRAPHY)

### What Gets Versioned?

**DOMAINS** get versioned, not individual SubjectConcepts:

- When you add new claims to `sc_military`, you bump `roman_republic` version
- When you add a new Clausewitz principle, you bump `military_theory` version
- SubjectConcepts are organizational units, not version units

## Queries

### Show all domains

```cypher
MATCH (scr:SubjectConceptRegistry)-[:TRACKS_DOMAIN]->(d:Domain)
RETURN d.domain_id, d.label, d.version, d.scope
ORDER BY d.domain_id
```

### Show domain contents

```cypher
MATCH (d:Domain {domain_id: 'roman_republic'})-[:CONTAINS]->(child)
RETURN d.label, labels(child)[0] as child_type, count(*) as count
```

### Show dependencies

```cypher
MATCH (d1:Domain)-[dep:DEPENDS_ON]->(d2:Domain)
RETURN d1.label as dependent,
       d2.label as dependency,
       dep.version_spec as spec
```

### Visualize domain graph

```cypher
MATCH (scr:SubjectConceptRegistry)-[:TRACKS_DOMAIN]->(d:Domain)
OPTIONAL MATCH (d)-[dep:DEPENDS_ON]->(d2:Domain)
RETURN scr, d, dep, d2
```

## Integration with SFAs

SFAs should be aware of which domain they're working in:

```python
class MilitarySFAEnhanced:
    def __init__(self, driver):
        self.driver = driver
        self.domain = 'roman_republic'  # This SFA works in ROMAN_REPUBLIC domain
        
    def submit_claim(self, ...):
        # Claims are associated with the domain
        # When enough claims accumulate, domain version bumps
        pass
```

When making cross-domain claims:

```python
# MilitarySFA linking ROMAN_REPUBLIC event to MILITARY_THEORY principle
def link_event_to_theory(self, event_cipher, principle_label):
    # Check that ROMAN_REPUBLIC depends on MILITARY_THEORY
    deps = domain_manager.get_dependencies('roman_republic')
    theory_dep = next(d for d in deps if d['dependency'] == 'military_theory')
    
    # Verify version compatibility
    if theory_dep['version_spec'] allows current version:
        # Safe to create cross-domain claim
        self.submit_cross_domain_claim(...)
```

## Next Steps

1. ✅ Create Domain nodes
2. ✅ Organize SubjectConcepts under domains
3. ✅ Link domains to SubjectConceptRegistry
4. ✅ Migrate dependencies to Domain level
5. ✅ Create DomainVersionManager
6. ⏳ Update version_cli.py to use DomainVersionManager
7. ⏳ Update documentation
8. ⏳ Test domain versioning workflows

## Files

```
scripts/system/
├── domain_version_manager.py          [NEW] Version manager for Domain nodes
├── restructure_domain_hierarchy.py    [NEW] One-time migration script
├── migrate_dependency_to_domain.py    [NEW] Migrate DEPENDS_ON to Domain
├── subgraph_version_manager.py        [OLD] Was for SubjectConcept (incorrect)
└── version_cli.py                     [NEEDS UPDATE] To use DomainVersionManager

tmp/
├── visualize_domain_structure.py      [NEW] Show current domain hierarchy
└── check_domain_hierarchy.py          [NEW] Diagnostic queries
```

## Summary

Successfully corrected the architecture to version at the **domain/subgraph level** as user intended:

- ✅ 3 domains created and versioned
- ✅ 130 nodes organized under domains (93 + 32 + 4 + 1 registry)
- ✅ SubjectConceptRegistry now populated
- ✅ Dependencies at domain level
- ✅ Proper hierarchy: Registry → Domain → SubjectConcepts/nodes

**Chrystallum now works as "GitHub for subgraphs"** where:
- Domains = repositories (versioned, independent)
- SubjectConcepts = modules/files within repositories
- Dependencies = package.json dependencies
- Versioning = semantic versioning at repo level
