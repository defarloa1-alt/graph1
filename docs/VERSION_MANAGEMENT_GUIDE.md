# Version Management Guide

**Last Updated:** July 16, 2026  
**System:** Chrystallum Domain Versioning

---

## Table of Contents

1. [Overview](#overview)
2. [Semantic Versioning](#semantic-versioning)
3. [Version Operations](#version-operations)
4. [CLI Usage](#cli-usage)
5. [Python API](#python-api)
6. [Version History](#version-history)
7. [Breaking Changes](#breaking-changes)
8. [Migration Workflows](#migration-workflows)
9. [Best Practices](#best-practices)

---

## Overview

Chrystallum uses **semantic versioning** at the domain level to track changes, manage dependencies, and prevent breaking updates.

### What Gets Versioned

**Versioned:**
- ✅ Domains (ROMAN_REPUBLIC, MILITARY_THEORY, etc.)

**Not Versioned:**
- ❌ Individual SubjectConcepts
- ❌ Individual claims
- ❌ Individual entities

### Why Domain-Level Versioning?

Think of a domain as a **package** or **library**:

```
Domain          = npm package / Python library
Version         = package version
Dependencies    = package.json / requirements.txt
Version bump    = Publishing new release
```

When you:
- Add SubjectConcepts → Minor version bump
- Add claims → Patch version bump
- Restructure domain → Major version bump

---

## Semantic Versioning

Format: **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)

### Version Components

```
v 2  .  5  .  1
  │    │    │
  │    │    └─ PATCH: Bug fixes, corrections
  │    └────── MINOR: New features, backwards compatible
  └─────────── MAJOR: Breaking changes
```

### Bump Rules

| Change Type | Bump | Example | Breaks Dependents? |
|-------------|------|---------|-------------------|
| **Major** | X.0.0 | Restructure SPO model | ✅ Yes |
| | | Remove SubjectConcepts | ✅ Yes |
| | | Rename core concepts | ✅ Yes |
| **Minor** | 0.X.0 | Add SubjectConcepts | ❌ No |
| | | Add new claims | ❌ No |
| | | Enhance structure | ❌ No |
| **Patch** | 0.0.X | Fix typos | ❌ No |
| | | Correct data | ❌ No |
| | | Update metadata | ❌ No |

### Decision Tree

```
Will this change break existing code/queries that use this domain?
│
├─ YES → Major bump (X.0.0)
│
└─ NO → Does this add new features/content?
        │
        ├─ YES → Minor bump (0.X.0)
        │
        └─ NO → Patch bump (0.0.X)
```

---

## Version Operations

### Initialize Version Tracking

When creating a new domain:

```python
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)

# Initialize versioning
manager.initialize_version(
    domain_id='diplomatic_history',
    version='1.0.0',
    description='Initial release of Diplomatic History domain'
)
```

**Result:**
- Domain node gets `version` property
- Version node created with changelog
- Linked via `:HAS_VERSION` relationship

### Bump Version

After making changes:

```python
# Minor bump (add features)
manager.bump_version(
    domain_id='military_theory',
    bump_type='minor',
    changes=[
        'Added Clausewitz friction principle',
        'Added trinity concept',
        'Enhanced SPO structure'
    ],
    description='Added Clausewitz principles'
)
```

**Bump Types:**
- `'major'` — Breaking changes
- `'minor'` — New features
- `'patch'` — Bug fixes

**Result:**
- Domain version updated (1.0.0 → 1.1.0)
- New Version node created
- Changelog recorded
- Timestamp captured

---

## CLI Usage

The CLI tool provides convenient commands for version management.

### Installation

```bash
# No installation needed - uses project's Neo4j driver
cd c:\Projects\Graph1
```

### Commands

#### Status

Show current version and metadata:

```bash
python scripts/system/version_cli.py status military_theory
```

**Output:**
```
Domain: military_theory
Label: Military Theory
Version: 1.1.0
Scope: theoretical
Period: timeless
Versioned: True
Created: 2026-07-16T14:30:00Z
Updated: 2026-07-16T15:45:00Z
```

#### Bump Version

Increment version after changes:

```bash
# Minor bump
python scripts/system/version_cli.py bump military_theory minor \
  "Added Clausewitz principles"

# Major bump (breaking)
python scripts/system/version_cli.py bump roman_republic major \
  "Restructured SubjectConcept hierarchy"

# Patch bump (fixes)
python scripts/system/version_cli.py bump geography patch \
  "Fixed place type classifications"
```

#### Dependencies

Show what a domain depends on:

```bash
python scripts/system/version_cli.py deps roman_republic
```

**Output:**
```
roman_republic (v0.1.0) depends on:
  - military_theory @ ^1.0.0 (current: v1.1.0) ✓ compatible
```

#### Compatibility Check

Check impact of version change before applying:

```bash
python scripts/system/version_cli.py check military_theory 2.0.0
```

**Output:**
```
Compatibility Check: military_theory 1.1.0 → 2.0.0

WARNING: Breaking change detected!

Dependents affected: 1
  - roman_republic (requires ^1.0.0, would break with 2.0.0)

Recommendation:
  1. Generate migration guide
  2. Update roman_republic to support v2.0.0
  3. Update dependency: ^1.0.0 → ^2.0.0
  4. Then bump to 2.0.0
```

#### Version History

Show complete changelog:

```bash
python scripts/system/version_cli.py history military_theory
```

**Output:**
```
Version History: military_theory

v1.1.0 (2026-07-16 15:45:00)
  Type: minor
  Description: Added Clausewitz principles
  Changes:
    - Added Clausewitz friction principle
    - Added trinity concept
    - Enhanced SPO structure

v1.0.0 (2026-07-16 14:30:00)
  Type: initial
  Description: Boyd OODA principles with SPO structure
  Changes:
    - Initial release
```

#### Initialize Domain

Set up version tracking for existing domain:

```bash
python scripts/system/version_cli.py init diplomatic_history \
  --version 1.0.0 \
  --desc "Initial release"
```

#### Create Dependency

Declare dependency between domains:

```bash
python scripts/system/version_cli.py link \
  diplomatic_history military_theory \
  --spec "^1.0.0"
```

---

## Python API

For programmatic access and integration with SFAs:

### Basic Operations

```python
from scripts.system.domain_version_manager import DomainVersionManager

# Initialize
manager = DomainVersionManager(driver)

# Check current version
with driver.session() as session:
    result = session.run("""
        MATCH (d:Domain {domain_id: 'military_theory'})
        RETURN d.version as version
    """)
    current_version = result.single()['version']

# Bump version
new_version = manager.bump_version(
    'military_theory',
    bump_type='minor',
    changes=['Added new principles']
)
print(f"Bumped to {new_version['new_version']}")
```

### Dependency Management

```python
# Add dependency
manager.add_dependency(
    dependent_id='roman_republic',
    dependency_id='military_theory',
    version_spec='^1.0.0'
)

# Get dependencies
deps = manager.get_dependencies('roman_republic')
for dep in deps:
    print(f"Depends on {dep['dependency']} @ {dep['version_spec']}")

# Check compatibility
compat = manager.check_compatibility('military_theory', '2.0.0')
if compat['breaking_changes'] > 0:
    print("Breaking changes detected!")
    for issue in compat['issues']:
        print(f"  {issue['dependent']}: {issue['issue']}")
```

### Version History

```python
# Get full history
history = manager.get_version_history('military_theory')

for version in history:
    print(f"v{version['version']} - {version['description']}")
    for change in version['changes']:
        print(f"  - {change}")
```

### SFA Integration

```python
class MilitarySFA:
    def __init__(self, driver):
        self.driver = driver
        self.version_manager = DomainVersionManager(driver)
        self.domain = 'roman_republic'
    
    def check_dependencies_before_claim(self, principle_label):
        """Check that required theory domain is available."""
        deps = self.version_manager.get_dependencies(self.domain)
        
        theory_dep = next(
            (d for d in deps if d['dependency'] == 'military_theory'),
            None
        )
        
        if not theory_dep:
            raise ValueError("military_theory dependency not declared")
        
        if not theory_dep['compatible']:
            raise ValueError(
                f"Incompatible version: "
                f"requires {theory_dep['version_spec']}, "
                f"got {theory_dep['dep_version']}"
            )
        
        return True
```

---

## Version History

### Storage

Version history stored as `:Version` nodes:

```cypher
(:Domain {domain_id: 'military_theory', version: '1.1.0'})
  -[:HAS_VERSION]->
    (:Version {
      version: '1.1.0',
      created_at: datetime(),
      description: 'Added Clausewitz',
      changes: ['Added friction', 'Added trinity'],
      bump_type: 'minor'
    })
```

### Query History

```cypher
// Get version history
MATCH (d:Domain {domain_id: 'military_theory'})-[:HAS_VERSION]->(v:Version)
RETURN v.version, v.created_at, v.description, v.changes
ORDER BY v.created_at DESC

// Find specific version
MATCH (d:Domain {domain_id: 'military_theory'})-[:HAS_VERSION]->(v:Version {version: '1.0.0'})
RETURN v
```

### Changelog Format

Each version records:
- **Version number** (1.1.0)
- **Timestamp** (when created)
- **Description** (summary)
- **Changes** (list of changes)
- **Bump type** (major/minor/patch)

---

## Breaking Changes

Breaking changes require special handling to avoid breaking dependent domains.

### What is a Breaking Change?

Changes that would cause existing queries or code to fail:

**Examples:**
- Removing SubjectConcepts
- Renaming core concepts
- Changing relationship structure
- Removing properties
- Changing data types

**Non-Breaking:**
- Adding SubjectConcepts
- Adding properties
- Adding relationships
- Enhancing existing content

### Detection

Use compatibility check before major bumps:

```python
compat = manager.check_compatibility('military_theory', '2.0.0')

if compat['breaking_changes'] > 0:
    print(f"⚠️ {compat['dependents_count']} dependent(s) affected")
    
    for issue in compat['issues']:
        print(f"  - {issue['dependent']}")
        print(f"    Issue: {issue['issue']}")
        print(f"    Breaking: {issue['breaking']}")
```

### Migration Process

1. **Check Compatibility**
   ```bash
   python scripts/system/version_cli.py check military_theory 2.0.0
   ```

2. **Generate Migration Guide**
   ```bash
   python scripts/system/generate_migration_guide.py \
     military_theory 1.1.0 2.0.0 \
     --output docs/MIGRATION_GUIDE_MILITARY_THEORY_2.0.md
   ```

3. **Review Guide**
   - Read generated migration guide
   - Identify affected code
   - Plan updates

4. **Update Dependents**
   - Update roman_republic code to handle v2.0.0
   - Test thoroughly
   - Document changes

5. **Update Dependencies**
   ```bash
   python scripts/system/version_cli.py link \
     roman_republic military_theory --spec "^2.0.0"
   ```

6. **Bump Version**
   ```bash
   python scripts/system/version_cli.py bump military_theory major \
     "Restructured SPO model"
   ```

---

## Migration Workflows

### Workflow 1: Safe Minor Update

No breaking changes, backwards compatible.

```bash
# 1. Make changes (add SubjectConcepts, claims, etc.)

# 2. Bump version
python scripts/system/version_cli.py bump military_theory minor \
  "Added Sun Tzu principles"

# 3. Dependents automatically compatible ✓
```

**Example:**
```
BEFORE: MILITARY_THEORY v1.1.0
        ROMAN_REPUBLIC depends on ^1.0.0

CHANGE: Added Sun Tzu principles

AFTER:  MILITARY_THEORY v1.2.0
        ROMAN_REPUBLIC still compatible (^1.0.0 allows 1.2.0) ✓
```

### Workflow 2: Breaking Major Update

Breaking changes, requires migration.

```bash
# 1. Check impact BEFORE making changes
python scripts/system/version_cli.py check military_theory 2.0.0
# Output: 1 dependent affected

# 2. Generate migration guide
python scripts/system/generate_migration_guide.py \
  military_theory 1.1.0 2.0.0 \
  --output docs/MIGRATION_GUIDE_MILITARY_THEORY_2.0.md

# 3. Review guide, plan updates

# 4. Make breaking changes

# 5. Update dependent code (roman_republic)

# 6. Test thoroughly

# 7. Update dependency
python scripts/system/version_cli.py link \
  roman_republic military_theory --spec "^2.0.0"

# 8. Bump version
python scripts/system/version_cli.py bump military_theory major \
  "Restructured SPO model"
```

**Example:**
```
BEFORE: MILITARY_THEORY v1.1.0
        ROMAN_REPUBLIC depends on ^1.0.0

CHANGE: Restructured SPO model (breaking)

MIGRATE: Update roman_republic code
         Update dependency ^1.0.0 → ^2.0.0

AFTER:  MILITARY_THEORY v2.0.0
        ROMAN_REPUBLIC compatible (^2.0.0) ✓
```

### Workflow 3: Patch Bug Fix

Minor corrections, no feature changes.

```bash
# 1. Fix bug/typo

# 2. Bump patch version
python scripts/system/version_cli.py bump military_theory patch \
  "Fixed Clausewitz friction description"

# 3. Dependents automatically compatible ✓
```

---

## Best Practices

### When to Bump

**After Each Significant Change:**
- ✅ Added 5+ SubjectConcepts → Minor bump
- ✅ Restructured domain → Major bump
- ✅ Fixed data errors → Patch bump
- ✅ Added new theory nodes → Minor bump

**Not Needed:**
- ❌ Single claim added
- ❌ Minor property update
- ❌ Ongoing development (bump at milestones)

### Version Number Guidelines

**Starting Version:**
- New domain → `1.0.0` (if complete)
- Early development → `0.1.0` (signals unstable)
- Experimental → `0.0.1` (very early)

**Version Progression:**
```
0.1.0 → 0.2.0 → ... → 0.9.0 → 1.0.0 (stable release)
1.0.0 → 1.1.0 → 1.2.0 → ... → 2.0.0 (major update)
```

### Documentation

**Always Document:**
- Summary of changes
- Breaking changes (if any)
- Migration steps (for major bumps)
- Rationale for version bump

**Changelog Example:**
```python
manager.bump_version(
    'military_theory',
    bump_type='minor',
    changes=[
        'Added Sun Tzu strategic principles',
        'Added 8 new Concept nodes',
        'Enhanced attack/defense taxonomy',
        'Added references to Art of War'
    ],
    description='Expanded Eastern military philosophy coverage'
)
```

### Dependency Management

**Be Specific:**
- ❌ `version_spec='*'` (too loose)
- ✅ `version_spec='^1.0.0'` (appropriate)
- ✅ `version_spec='1.2.0'` (when exact version needed)

**Review Regularly:**
- Check dependency versions monthly
- Update to latest minor versions
- Plan major version migrations
- Remove unused dependencies

---

## Troubleshooting

### Version Not Updating

**Problem:** Bump command succeeds but version unchanged

**Solutions:**
1. Check domain exists: `MATCH (d:Domain {domain_id: 'X'}) RETURN d.version`
2. Verify versioning enabled: `d.versioned = true`
3. Check for errors in output

### Dependency Conflicts

**Problem:** Cannot update dependency due to version mismatch

**Solutions:**
1. Check current versions of all dependencies
2. Update dependent code to support new version
3. Use migration guide
4. Consider pinning to exact version temporarily

### Lost Version History

**Problem:** Version history missing or incomplete

**Solutions:**
1. Check Version nodes: `MATCH (v:Version) WHERE v.domain_id = 'X' RETURN v`
2. Verify `:HAS_VERSION` relationships exist
3. Reconstruct from git history if needed

---

## Examples

### Example 1: MILITARY_THEORY Evolution

```
v1.0.0 (2026-07-15)
├─ Initial release
├─ Boyd OODA principles
└─ SPO structure (Concept, Mechanism, Effect)

v1.1.0 (2026-07-16)
├─ Minor bump
├─ Added Clausewitz friction principle
├─ Added Clausewitz trinity concept
└─ Backwards compatible ✓

v1.2.0 (planned)
├─ Minor bump
├─ Add Sun Tzu principles
└─ Expand Eastern philosophy coverage

v2.0.0 (future)
├─ Major bump (breaking)
├─ Restructure SPO model
├─ Add Process and Target nodes
└─ Requires migration
```

### Example 2: ROMAN_REPUBLIC Development

```
v0.1.0 (2026-07-15)
├─ Initial release
├─ Early development
├─ 93 SubjectConcepts
└─ Depends on military_theory @ ^1.0.0

v0.2.0 (planned)
├─ Minor bump
├─ Add diplomatic content
├─ Add 500+ claims
└─ Still depends on military_theory @ ^1.0.0

v1.0.0 (future)
├─ Major milestone
├─ Stable release
├─ Comprehensive coverage
└─ Production ready
```

---

## Related Documentation

- **Domain Management Guide:** `docs/DOMAIN_MANAGEMENT_GUIDE.md`
- **CLI Reference:** [VERSION_CLI_REFERENCE.md](VERSION_CLI_REFERENCE.md)
- **Quick Reference:** [DOMAIN_QUICK_REFERENCE.md](DOMAIN_QUICK_REFERENCE.md)
- **Migration Guide Example:** `docs/MIGRATION_GUIDE_MILITARY_THEORY_2.0.md`

---

## Summary

**Key Concepts:**
- Semantic versioning (major.minor.patch)
- Version at domain level, not SubjectConcept level
- Check compatibility before breaking changes
- Generate migration guides for major bumps
- Track complete version history

**Tools:**
- `DomainVersionManager` (Python API)
- `version_cli.py` (Command line)
- `generate_migration_guide.py` (Documentation)

**Best Practices:**
- Bump after significant changes
- Document changes in changelog
- Check compatibility before major bumps
- Test dependents after updates
- Use appropriate version specs
