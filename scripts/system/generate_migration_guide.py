"""
Generate Migration Guide for Breaking Version Changes

When a SubjectConcept gets a major version bump, this tool generates
a migration guide for dependent subgraphs.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
from neo4j import GraphDatabase
from scripts.system.subgraph_version_manager import SubgraphVersionManager

load_dotenv()


class MigrationGuideGenerator:
    """Generate migration guides for breaking changes."""
    
    def __init__(self, driver):
        self.driver = driver
        self.manager = SubgraphVersionManager(driver)
    
    def generate_guide(
        self,
        subject_id: str,
        from_version: str,
        to_version: str
    ) -> str:
        """
        Generate a migration guide.
        
        Args:
            subject_id: SubjectConcept being updated
            from_version: Current version
            to_version: Target version (major bump)
        
        Returns:
            Markdown migration guide
        """
        # Check compatibility
        compat = self.manager.check_compatibility(subject_id, to_version)
        
        # Get version history between versions
        history = self._get_version_range(subject_id, from_version, to_version)
        
        # Get affected dependents
        dependents = self.manager.get_dependents(subject_id)
        
        # Generate guide
        guide = self._build_guide(
            subject_id,
            from_version,
            to_version,
            history,
            dependents,
            compat
        )
        
        return guide
    
    def _get_version_range(
        self,
        subject_id: str,
        from_version: str,
        to_version: str
    ) -> List[Dict]:
        """Get all versions between from and to."""
        all_versions = self.manager.get_version_history(subject_id)
        
        # Filter to range (simplified - assumes semantic versioning)
        return [v for v in all_versions if v['version'] > from_version]
    
    def _build_guide(
        self,
        subject_id: str,
        from_version: str,
        to_version: str,
        history: List[Dict],
        dependents: List[Dict],
        compat: Dict
    ) -> str:
        """Build markdown migration guide."""
        
        guide = f"""# Migration Guide: {subject_id} v{from_version} -> v{to_version}

## Overview

This is a **BREAKING CHANGE** that requires manual migration.

**Affected SubjectConcepts:** {len(dependents)}

## What Changed

"""
        
        # List all changes
        for version in history:
            guide += f"### v{version['version']} - {version['description']}\n\n"
            if version.get('changes'):
                for change in version['changes']:
                    guide += f"- {change}\n"
                guide += "\n"
        
        guide += f"""## Breaking Changes

The following changes may break existing code:

"""
        
        # List breaking changes (would be specified in version metadata)
        guide += f"""- **Schema changes**: SPO structure may have changed
- **Principle renames**: Core principles may have new labels
- **Relationship changes**: :DEFINES_CONCEPT structure may differ

## Migration Checklist

"""
        
        # Generate checklist for each dependent
        for dep in dependents:
            guide += f"### {dep['dependent']} (currently requires {dep['version_spec']})\n\n"
            guide += f"""1. **Review changes** - Understand what changed in {subject_id}
2. **Update queries** - Check all Cypher queries referencing {subject_id}
3. **Update claims** - Verify cross-domain claims still valid
4. **Test thoroughly** - Run integration tests
5. **Update dependency** - Change version spec to `^{to_version}`

"""
        
        guide += f"""## Example Updates

### Before (v{from_version})

```cypher
MATCH (principle:MilitaryPrinciple {{label: 'OODA Loop'}})
RETURN principle
```

### After (v{to_version})

```cypher
// Check if principle structure changed
MATCH (principle:MilitaryPrinciple {{label: 'OODA Loop'}})
RETURN principle, 
       [(principle)-[:DEFINES_CONCEPT]->(c) | c.name] as concepts
```

## Update Dependency

After migration, update your dependency specification:

```python
# In your SFA initialization or config
manager.add_dependency(
    dependent_id='{dependents[0]['dependent'] if dependents else 'your_subgraph'}',
    dependency_id='{subject_id}',
    version_spec='^{to_version}'  # Update to new major version
)
```

## Rollback Plan

If migration fails, you can rollback by:

1. Keeping dependency pinned to v{from_version}
2. Not updating to v{to_version}
3. Waiting for bug fixes in v{to_version} patch releases

## Need Help?

- Review changelog: `python scripts/system/version_cli.py history {subject_id}`
- Check compatibility: `python scripts/system/version_cli.py check {subject_id} {to_version}`
- View dependencies: `python scripts/system/version_cli.py deps <your_subgraph>`

## Timeline

1. **Review** - Read this guide thoroughly
2. **Test** - Test in dev environment
3. **Migrate** - Update code and dependencies
4. **Verify** - Run integration tests
5. **Deploy** - Update to v{to_version}

---

Generated: {self._timestamp()}
"""
        
        return guide
    
    def _timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate migration guide for breaking changes'
    )
    parser.add_argument('subject_id', help='SubjectConcept being updated')
    parser.add_argument('from_version', help='Current version')
    parser.add_argument('to_version', help='Target version (major bump)')
    parser.add_argument(
        '--output',
        default='MIGRATION_GUIDE.md',
        help='Output file (default: MIGRATION_GUIDE.md)'
    )
    
    args = parser.parse_args()
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    try:
        generator = MigrationGuideGenerator(driver)
        
        guide = generator.generate_guide(
            args.subject_id,
            args.from_version,
            args.to_version
        )
        
        # Write to file
        with open(args.output, 'w') as f:
            f.write(guide)
        
        print(f"\n[OK] Migration guide written to: {args.output}\n")
        
    finally:
        driver.close()


if __name__ == "__main__":
    main()
