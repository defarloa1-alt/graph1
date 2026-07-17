# System Tools

**Domain Version Management and System Utilities**

---

## Domain Version Management

### Core Tools

#### `domain_version_manager.py`

**Purpose:** Python API for managing domain versions and dependencies.

**Usage:**
```python
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)

# Initialize versioning
manager.initialize_version('domain_id', '1.0.0')

# Bump version
manager.bump_version('domain_id', 'minor', changes=['Added X'])

# Add dependency
manager.add_dependency('domain_a', 'domain_b', '^1.0.0')

# Check compatibility
compat = manager.check_compatibility('domain_id', '2.0.0')

# Get version history
history = manager.get_version_history('domain_id')

# Get dependencies
deps = manager.get_dependencies('domain_id')
```

**API Reference:**
- `initialize_version(domain_id, version='1.0.0', description=None)` — Initialize version tracking
- `bump_version(domain_id, bump_type, changes=[], description=None)` — Increment version
- `add_dependency(dependent_id, dependency_id, version_spec='*', pinned=False)` — Declare dependency
- `check_compatibility(domain_id, new_version)` — Check breaking changes
- `get_version_history(domain_id)` — Get changelog
- `get_dependencies(domain_id)` — Get dependencies

---

#### `version_cli.py`

**Purpose:** Command-line interface for domain version management.

**Commands:**
```bash
# Status
python scripts/system/version_cli.py status <domain_id>

# Bump version
python scripts/system/version_cli.py bump <domain_id> <major|minor|patch> <description>

# Dependencies
python scripts/system/version_cli.py deps <domain_id>

# Check compatibility
python scripts/system/version_cli.py check <domain_id> <new_version>

# Version history
python scripts/system/version_cli.py history <domain_id>

# Initialize versioning
python scripts/system/version_cli.py init <domain_id> [--version X.Y.Z] [--desc "..."]

# Create dependency
python scripts/system/version_cli.py link <dependent_id> <dependency_id> [--spec "^X.Y.Z"]
```

**Examples:**
```bash
# Check status
python scripts/system/version_cli.py status military_theory

# Bump minor version
python scripts/system/version_cli.py bump military_theory minor "Added Sun Tzu principles"

# Show dependencies
python scripts/system/version_cli.py deps roman_republic

# Check breaking changes
python scripts/system/version_cli.py check military_theory 2.0.0

# View history
python scripts/system/version_cli.py history military_theory

# Initialize new domain
python scripts/system/version_cli.py init naval_theory --version 1.0.0

# Link domains
python scripts/system/version_cli.py link roman_republic military_theory --spec "^1.0.0"
```

---

#### `generate_migration_guide.py`

**Purpose:** Generate migration guides for breaking version changes.

**Usage:**
```bash
python scripts/system/generate_migration_guide.py \
  <domain_id> <from_version> <to_version> \
  [--output <output_file>]
```

**Example:**
```bash
python scripts/system/generate_migration_guide.py \
  military_theory 1.1.0 2.0.0 \
  --output docs/MIGRATION_GUIDE_MILITARY_THEORY_2.0.md
```

**Output:**
- Comprehensive markdown migration guide
- What changed
- Breaking changes list
- Migration checklist for each dependent
- Before/after code examples
- Rollback plan

---

## Migration Scripts (One-Time)

These scripts were used to implement the domain versioning system. **Not needed for regular use.**

#### `restructure_domain_hierarchy.py`

**Purpose:** One-time migration to restructure SubjectConcepts under Domains.

**What it did:**
- Created Domain nodes (ROMAN_REPUBLIC, MILITARY_THEORY, GEOGRAPHY)
- Linked domains to SubjectConceptRegistry via `:TRACKS_DOMAIN`
- Organized SubjectConcepts under domains via `:CONTAINS`

**Status:** ✅ Complete (July 16, 2026)

---

#### `migrate_dependency_to_domain.py`

**Purpose:** One-time migration to move `:DEPENDS_ON` from SubjectConcept to Domain level.

**What it did:**
- Moved `DEPENDS_ON` relationships from SubjectConcept nodes to Domain nodes
- Updated version_spec properties
- Cleaned up old relationships

**Status:** ✅ Complete (July 16, 2026)

---

## Deprecated Tools

#### `subgraph_version_manager.py`

**Status:** ❌ Deprecated (July 16, 2026)

**Reason:** This tool versioned individual SubjectConcept nodes (incorrect approach).

**Replaced by:** `domain_version_manager.py` (versions Domain nodes, not SubjectConcept nodes)

**Do not use.** Use `domain_version_manager.py` instead.

---

## Common Workflows

### Workflow 1: Set Up New Domain

```bash
# 1. Create Domain node in Neo4j (Cypher)
CREATE (d:Domain {
  domain_id: 'new_domain',
  label: 'New Domain',
  scope: 'historical',
  description: '...',
  created_at: datetime()
})

# 2. Link to registry
MATCH (scr:SubjectConceptRegistry)
MATCH (d:Domain {domain_id: 'new_domain'})
CREATE (scr)-[:TRACKS_DOMAIN]->(d)

# 3. Initialize versioning
python scripts/system/version_cli.py init new_domain --version 1.0.0

# 4. Add dependencies (if needed)
python scripts/system/version_cli.py link new_domain military_theory --spec "^1.0.0"
```

---

### Workflow 2: Bump Version After Changes

```bash
# 1. Check current status
python scripts/system/version_cli.py status military_theory

# 2. Bump version (choose appropriate type)
# Minor bump (new features)
python scripts/system/version_cli.py bump military_theory minor "Added Sun Tzu principles"

# Major bump (breaking changes) - check first!
python scripts/system/version_cli.py check military_theory 2.0.0

# 3. Verify
python scripts/system/version_cli.py history military_theory
```

---

### Workflow 3: Handle Breaking Changes

```bash
# 1. Check impact before making changes
python scripts/system/version_cli.py check military_theory 2.0.0
# Output: WARNING - 1 dependent affected

# 2. Generate migration guide
python scripts/system/generate_migration_guide.py \
  military_theory 1.1.0 2.0.0 \
  --output docs/MIGRATION_GUIDE_MILITARY_THEORY_2.0.md

# 3. Make breaking changes

# 4. Update dependent code (e.g., roman_republic)

# 5. Update dependency version spec
python scripts/system/version_cli.py link \
  roman_republic military_theory --spec "^2.0.0"

# 6. Bump version
python scripts/system/version_cli.py bump military_theory major \
  "Restructured SPO model"
```

---

### Workflow 4: Check Dependencies

```bash
# Show what a domain depends on
python scripts/system/version_cli.py deps roman_republic

# Check compatibility of an update
python scripts/system/version_cli.py check military_theory 2.0.0

# View dependency graph (Cypher)
MATCH (d1:Domain)-[dep:DEPENDS_ON]->(d2:Domain)
RETURN d1.label, d2.label, dep.version_spec, d2.version
```

---

## Python API Integration

### In SFAs

```python
from scripts.system.domain_version_manager import DomainVersionManager

class MilitarySFA:
    def __init__(self, driver):
        self.driver = driver
        self.domain_id = 'roman_republic'
        self.version_manager = DomainVersionManager(driver)
        
        # Check dependencies at initialization
        self._verify_dependencies()
    
    def _verify_dependencies(self):
        """Ensure required dependencies are satisfied."""
        deps = self.version_manager.get_dependencies(self.domain_id)
        
        theory_dep = next(
            (d for d in deps if d['dependency'] == 'military_theory'),
            None
        )
        
        if not theory_dep or not theory_dep['compatible']:
            raise ValueError("military_theory dependency not satisfied")
    
    def can_reference_theory(self):
        """Check if we can safely reference MILITARY_THEORY."""
        deps = self.version_manager.get_dependencies(self.domain_id)
        theory = next(d for d in deps if d['dependency'] == 'military_theory')
        return theory['compatible']
```

---

## Configuration

**Environment Variables:**

Uses `.env` file in project root:
```
NEO4J_URI=neo4j+s://...
NEO4J_USER=...
NEO4J_PASS=...
```

**Dependencies:**

- neo4j-driver
- python-dotenv

---

## Troubleshooting

### Domain Not Found

**Error:** `ValueError: Domain not found: domain_id`

**Solutions:**
1. Check domain ID spelling
2. Verify domain exists: `MATCH (d:Domain {domain_id: 'X'}) RETURN d`
3. Check if domain linked to registry

---

### Version Not Updating

**Error:** Version bump succeeds but version unchanged

**Solutions:**
1. Check domain has `versioned: true` property
2. Verify `:HAS_VERSION` relationships exist
3. Check for errors in output

---

### Dependency Conflicts

**Error:** Cannot update dependency due to version mismatch

**Solutions:**
1. Check compatibility: `version_cli.py check domain_id new_version`
2. Update dependent code to support new version
3. Generate migration guide
4. Update version_spec to match

---

## Related Documentation

- **Domain Management Guide:** `docs/DOMAIN_MANAGEMENT_GUIDE.md`
- **Version Management Guide:** `docs/VERSION_MANAGEMENT_GUIDE.md`
- **CLI Reference:** `VERSION_CLI_REFERENCE.md`
- **Quick Reference:** `DOMAIN_QUICK_REFERENCE.md`

---

## File Inventory

**Active Tools:**
- `domain_version_manager.py` (320 lines) — Core manager
- `version_cli.py` (220 lines) — CLI tool
- `generate_migration_guide.py` (180 lines) — Migration guides
- `README.md` (this file) — Documentation

**Migration Scripts (Complete):**
- `restructure_domain_hierarchy.py` — One-time domain restructure
- `migrate_dependency_to_domain.py` — One-time dependency migration

**Deprecated:**
- `subgraph_version_manager.py` — Use `domain_version_manager.py` instead

---

**Last Updated:** July 16, 2026
