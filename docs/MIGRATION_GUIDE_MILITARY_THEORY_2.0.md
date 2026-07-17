# Migration Guide: military_theory v1.0.0 -> v2.0.0

## Overview

This is a **BREAKING CHANGE** that requires manual migration.

**Affected SubjectConcepts:** 1

## What Changed

### v1.1.0 - Added Clausewitz principles

- Added Clausewitz friction principle
- Added Clausewitz trinity concept
- Enhanced SPO structure

## Breaking Changes

The following changes may break existing code:

- **Schema changes**: SPO structure may have changed
- **Principle renames**: Core principles may have new labels
- **Relationship changes**: :DEFINES_CONCEPT structure may differ

## Migration Checklist

### roman_republic (currently requires ^1.0.0)

1. **Review changes** - Understand what changed in military_theory
2. **Update queries** - Check all Cypher queries referencing military_theory
3. **Update claims** - Verify cross-domain claims still valid
4. **Test thoroughly** - Run integration tests
5. **Update dependency** - Change version spec to `^2.0.0`

## Example Updates

### Before (v1.0.0)

```cypher
MATCH (principle:MilitaryPrinciple {label: 'OODA Loop'})
RETURN principle
```

### After (v2.0.0)

```cypher
// Check if principle structure changed
MATCH (principle:MilitaryPrinciple {label: 'OODA Loop'})
RETURN principle, 
       [(principle)-[:DEFINES_CONCEPT]->(c) | c.name] as concepts
```

## Update Dependency

After migration, update your dependency specification:

```python
# In your SFA initialization or config
manager.add_dependency(
    dependent_id='roman_republic',
    dependency_id='military_theory',
    version_spec='^2.0.0'  # Update to new major version
)
```

## Rollback Plan

If migration fails, you can rollback by:

1. Keeping dependency pinned to v1.0.0
2. Not updating to v2.0.0
3. Waiting for bug fixes in v2.0.0 patch releases

## Need Help?

- Review changelog: `python scripts/system/version_cli.py history military_theory`
- Check compatibility: `python scripts/system/version_cli.py check military_theory 2.0.0`
- View dependencies: `python scripts/system/version_cli.py deps <your_subgraph>`

## Timeline

1. **Review** - Read this guide thoroughly
2. **Test** - Test in dev environment
3. **Migrate** - Update code and dependencies
4. **Verify** - Run integration tests
5. **Deploy** - Update to v2.0.0

---

Generated: 2026-07-16T15:35:08.307215+00:00
