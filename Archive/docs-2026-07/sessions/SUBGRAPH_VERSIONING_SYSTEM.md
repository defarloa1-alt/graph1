# SubjectConcept Versioning System

**Chrystallum as "GitHub for Knowledge Graphs"**

## Overview

The SubjectConcept Versioning System treats each SubjectConcept (e.g., `MILITARY_THEORY`, `ROMAN_REPUBLIC`) as an independent, versionable knowledge module. SubjectConcepts can depend on each other, and version changes are tracked with semantic versioning.

This enables:
- **Independent development** of knowledge domains
- **Dependency management** between domains
- **Change tracking** with version history
- **Breaking change detection** for dependent domains
- **Semantic versioning** (major.minor.patch)

## Key Concepts

### 1. SubjectConcept as a Module

Each `SubjectConcept` node is a versioned knowledge module:

```cypher
(:SubjectConcept {
  subject_id: 'military_theory',
  label: 'Military Theory',
  version: '1.1.0',
  versioned: true,
  schema_version: 'spo_v1'
})
```

### 2. Version Nodes

Each version creates a `Version` node:

```cypher
(:SubjectConcept)-[:HAS_VERSION]->(:Version {
  version: '1.1.0',
  created_at: datetime(),
  description: 'Added Clausewitz principles',
  changes: ['Added friction', 'Added trinity'],
  bump_type: 'minor'
})
```

### 3. Dependency Links

SubjectConcepts can depend on others:

```cypher
(:SubjectConcept {subject_id: 'roman_republic'})
  -[:DEPENDS_ON {
    version_spec: '^1.0.0',
    pinned: false
  }]->
(:SubjectConcept {subject_id: 'military_theory'})
```

### 4. Version Specifications

Version specs follow npm/cargo conventions:

| Spec | Meaning | Example |
|------|---------|---------|
| `1.0.0` | Exact version | Must be exactly 1.0.0 |
| `^1.0.0` | Compatible with 1.x | 1.0.0, 1.1.0, 1.2.3 OK; 2.0.0 breaks |
| `*` | Any version | Always compatible |

## Semantic Versioning Rules

Following semver conventions:

- **Major bump (X.0.0)**: Breaking changes
  - Changed SPO structure
  - Removed principles
  - Renamed core concepts
  
- **Minor bump (0.X.0)**: New features, backwards compatible
  - Added new principles
  - Enhanced existing structure
  - New relationships
  
- **Patch bump (0.0.X)**: Bug fixes, backwards compatible
  - Fixed typos
  - Clarified descriptions
  - Minor corrections

## Architecture

```
SubjectConcept Versioning System
├── SubgraphVersionManager (Core manager)
│   ├── initialize_version()
│   ├── bump_version()
│   ├── add_dependency()
│   ├── check_compatibility()
│   └── get_version_history()
│
├── Version CLI (Command-line tool)
│   ├── status
│   ├── bump
│   ├── deps
│   ├── check
│   └── history
│
└── Neo4j Schema
    ├── :SubjectConcept nodes (with version)
    ├── :Version nodes
    └── :DEPENDS_ON relationships
```

## Usage

### CLI Commands

```bash
# Show status
python scripts/system/version_cli.py status military_theory

# Bump version
python scripts/system/version_cli.py bump military_theory minor "Added Clausewitz"

# Show dependencies
python scripts/system/version_cli.py deps roman_republic

# Check compatibility before updating
python scripts/system/version_cli.py check military_theory 2.0.0

# Show version history
python scripts/system/version_cli.py history military_theory

# Initialize version tracking
python scripts/system/version_cli.py init military_theory --version 1.0.0

# Create dependency link
python scripts/system/version_cli.py link roman_republic military_theory --spec "^1.0.0"
```

### Python API

```python
from scripts.system.subgraph_version_manager import SubgraphVersionManager

manager = SubgraphVersionManager(driver)

# Initialize version
manager.initialize_version('military_theory', version='1.0.0')

# Declare dependency
manager.add_dependency(
    dependent_id='roman_republic',
    dependency_id='military_theory',
    version_spec='^1.0.0'
)

# Bump version
result = manager.bump_version(
    'military_theory',
    bump_type='minor',
    changes=['Added Clausewitz friction']
)

# Check compatibility
compat = manager.check_compatibility('military_theory', '2.0.0')
if compat['breaking_changes'] > 0:
    print("WARNING: Breaking changes detected!")
```

## Example Workflow

### 1. Initial Setup

```python
# Initialize MILITARY_THEORY
manager.initialize_version('military_theory', '1.0.0', 'Boyd principles')

# Initialize ROMAN_REPUBLIC
manager.initialize_version('roman_republic', '0.1.0', 'Early stage')

# Declare dependency
manager.add_dependency(
    'roman_republic',
    'military_theory',
    version_spec='^1.0.0'  # Compatible with 1.x
)
```

### 2. Minor Update (Safe)

```python
# Add Clausewitz to MILITARY_THEORY
manager.bump_version(
    'military_theory',
    bump_type='minor',  # 1.0.0 -> 1.1.0
    changes=['Added Clausewitz friction', 'Added trinity'],
    description='Added Clausewitz principles'
)

# roman_republic still compatible (^1.0.0 allows 1.1.0)
```

### 3. Major Update (Breaking)

```python
# Check before breaking change
compat = manager.check_compatibility('military_theory', '2.0.0')
# Returns: breaking_changes=1, affects roman_republic

# Notify user
print("Breaking change will affect:")
for issue in compat['issues']:
    print(f"  - {issue['dependent']}")

# User must:
# 1. Review changes
# 2. Update roman_republic code
# 3. Update dependency: version_spec='^2.0.0'
```

## Current State

After demo execution:

### MILITARY_THEORY
- Version: `1.1.0`
- Versions:
  - `1.0.0`: Boyd OODA principles with SPO structure
  - `1.1.0`: Added Clausewitz principles
- Dependents: `roman_republic`

### ROMAN_REPUBLIC
- Version: `0.1.0`
- Dependencies: `military_theory @ ^1.0.0`

## Dependency Graph

```
┌─────────────────┐
│ ROMAN_REPUBLIC  │
│   v0.1.0        │
└─────────────────┘
        │
        │ DEPENDS_ON
        │ (^1.0.0)
        ▼
┌─────────────────┐
│ MILITARY_THEORY │
│   v1.1.0        │
└─────────────────┘
```

## Future Enhancements

1. **Automated Notifications**
   - Notify dependent SFAs when dependency updates
   - Email/Slack integration

2. **Version Pinning Strategy**
   - Lock file for reproducibility
   - Conflict resolution

3. **Change Impact Analysis**
   - Show what claims would be affected
   - Migration scripts

4. **Subgraph Publishing**
   - Export subgraph with version
   - Import from other Chrystallum instances

5. **Dependency Resolution**
   - Handle transitive dependencies
   - Version constraint solver

## Integration with SFAs

SFAs should check dependency versions before making cross-domain claims:

```python
class MilitarySFAEnhanced:
    def link_event_to_theory(self, event_cipher, principle_label):
        # Check that MILITARY_THEORY is available
        deps = manager.get_dependencies('roman_republic')
        theory_dep = next(d for d in deps if d['dependency'] == 'military_theory')
        
        # Check compatibility
        if theory_dep['dep_version'] >= '1.0.0':
            # Safe to use OODA Loop, Operational Tempo, etc.
            self.submit_theory_claim(...)
```

## Files

```
scripts/system/
├── subgraph_version_manager.py    # Core version manager
└── version_cli.py                  # Command-line interface

scripts/demos/
└── demo_subgraph_versioning.py    # Full demo

SUBGRAPH_VERSIONING_SYSTEM.md      # This file
```

## Summary

The SubjectConcept Versioning System enables Chrystallum to function as a **"GitHub for knowledge graphs"**, where:

- Each SubjectConcept is an independent, versioned module
- SFAs can depend on other SubjectConcepts with version specs
- Breaking changes are detected and flagged
- Version history is tracked
- Dependency graph is explicit and queryable

This architecture supports **modular knowledge development** where domains can evolve independently while maintaining compatibility with dependent systems.
