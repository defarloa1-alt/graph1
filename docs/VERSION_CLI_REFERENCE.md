# Version CLI Reference

**Command-Line Tool for Domain Version Management**

---

## Installation

```bash
cd c:\Projects\Graph1
# Uses project's Neo4j connection (no installation needed)
```

---

## Commands

### status

Show current version and metadata for a domain.

```bash
python scripts/system/version_cli.py status <domain_id>
```

**Example:**
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

---

### bump

Increment version after making changes.

```bash
python scripts/system/version_cli.py bump <domain_id> <bump_type> <description>
```

**Bump Types:**
- `major` — Breaking changes (X.0.0)
- `minor` — New features, backwards compatible (0.X.0)
- `patch` — Bug fixes (0.0.X)

**Examples:**
```bash
# Minor bump (new features)
python scripts/system/version_cli.py bump military_theory minor \
  "Added Clausewitz principles"

# Major bump (breaking)
python scripts/system/version_cli.py bump roman_republic major \
  "Restructured SubjectConcept hierarchy"

# Patch bump (fixes)
python scripts/system/version_cli.py bump geography patch \
  "Fixed place type classifications"
```

---

### deps

Show dependencies for a domain.

```bash
python scripts/system/version_cli.py deps <domain_id>
```

**Example:**
```bash
python scripts/system/version_cli.py deps roman_republic
```

**Output:**
```
roman_republic (v0.1.0) depends on:
  - military_theory @ ^1.0.0 (current: v1.1.0) ✓ compatible
```

---

### check

Check compatibility impact of version change **before** applying.

```bash
python scripts/system/version_cli.py check <domain_id> <new_version>
```

**Example:**
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

---

### history

Show complete version history and changelog.

```bash
python scripts/system/version_cli.py history <domain_id>
```

**Example:**
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

---

### init

Initialize version tracking for an existing domain.

```bash
python scripts/system/version_cli.py init <domain_id> [options]
```

**Options:**
- `--version VERSION` — Starting version (default: 1.0.0)
- `--desc DESCRIPTION` — Version description

**Examples:**
```bash
# Default (1.0.0)
python scripts/system/version_cli.py init diplomatic_history

# Custom version
python scripts/system/version_cli.py init diplomatic_history \
  --version 0.1.0 \
  --desc "Early development release"
```

---

### link

Create dependency between domains.

```bash
python scripts/system/version_cli.py link <dependent_id> <dependency_id> [options]
```

**Options:**
- `--spec VERSION_SPEC` — Version specification (default: ^X.Y.Z of current)

**Examples:**
```bash
# Default (uses current version with ^)
python scripts/system/version_cli.py link roman_republic military_theory

# Custom spec
python scripts/system/version_cli.py link diplomatic_history roman_republic \
  --spec "^0.1.0"

# Exact version
python scripts/system/version_cli.py link domain_a domain_b \
  --spec "1.2.3"
```

---

## Common Workflows

### New Domain Setup

```bash
# 1. Create domain in Neo4j (Cypher)
# 2. Initialize versioning
python scripts/system/version_cli.py init new_domain --version 1.0.0

# 3. Add dependencies
python scripts/system/version_cli.py link new_domain military_theory
```

### After Making Changes

```bash
# 1. Check current status
python scripts/system/version_cli.py status military_theory

# 2. Bump version
python scripts/system/version_cli.py bump military_theory minor "Added content"

# 3. Verify
python scripts/system/version_cli.py history military_theory
```

### Before Breaking Change

```bash
# 1. Check impact
python scripts/system/version_cli.py check military_theory 2.0.0

# 2. Generate migration guide
python scripts/system/generate_migration_guide.py \
  military_theory 1.1.0 2.0.0 \
  --output docs/MIGRATION_GUIDE_MILITARY_THEORY_2.0.md

# 3. Update dependent code

# 4. Update dependencies
python scripts/system/version_cli.py link roman_republic military_theory \
  --spec "^2.0.0"

# 5. Bump version
python scripts/system/version_cli.py bump military_theory major "Restructured"
```

### Check Dependencies

```bash
# Show what domain depends on
python scripts/system/version_cli.py deps roman_republic

# Check compatibility
python scripts/system/version_cli.py check military_theory 2.0.0
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Domain not found |
| 2 | Invalid version format |
| 3 | Dependency conflict |
| 4 | Breaking change detected (with `check`) |

---

## Version Specifications

| Spec | Meaning | Example |
|------|---------|---------|
| `1.0.0` | Exact version | Only 1.0.0 |
| `^1.0.0` | Compatible with 1.x | 1.0.0, 1.1.0, 1.9.9 ✓ / 2.0.0 ✗ |
| `^1.2.0` | Compatible with 1.x, min 1.2.0 | 1.2.0+ ✓ / 1.1.0 ✗ |
| `*` | Any version | Always compatible |

---

## Environment

**Configuration:**
- Uses `.env` file for Neo4j connection
- Requires `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASS`

**Dependencies:**
- neo4j-driver
- python-dotenv

---

## Troubleshooting

### Domain Not Found

```bash
python scripts/system/version_cli.py status nonexistent_domain
# Error: Domain not found: nonexistent_domain
```

**Solution:** Check domain ID spelling, verify exists in Neo4j

### Version Format Error

```bash
python scripts/system/version_cli.py init domain --version 1.0
# Error: Invalid version format. Use X.Y.Z
```

**Solution:** Use semantic version format (1.0.0)

### Dependency Already Exists

```bash
python scripts/system/version_cli.py link domain_a domain_b
# Error: Dependency already exists
```

**Solution:** Use Cypher to update existing dependency or remove and recreate

---

## Related Tools

### Migration Guide Generator

```bash
python scripts/system/generate_migration_guide.py \
  <domain_id> <from_version> <to_version> \
  --output <output_file>
```

**Example:**
```bash
python scripts/system/generate_migration_guide.py \
  military_theory 1.1.0 2.0.0 \
  --output docs/MIGRATION_GUIDE_MILITARY_THEORY_2.0.md
```

### Python API

```python
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)
manager.bump_version('domain_id', 'minor', changes=['Added X'])
```

---

## Examples

### Example 1: Check Status

```bash
$ python scripts/system/version_cli.py status military_theory

Domain: military_theory
Label: Military Theory
Version: 1.1.0
Scope: theoretical
Period: timeless
Versioned: True
```

### Example 2: Bump Minor Version

```bash
$ python scripts/system/version_cli.py bump military_theory minor "Added Sun Tzu principles"

✓ Version bumped: 1.1.0 → 1.2.0
  Changes:
    - Added Sun Tzu principles
```

### Example 3: Check Dependencies

```bash
$ python scripts/system/version_cli.py deps roman_republic

roman_republic (v0.1.0) depends on:
  - military_theory @ ^1.0.0 (current: v1.1.0) ✓ compatible
```

### Example 4: Breaking Change Check

```bash
$ python scripts/system/version_cli.py check military_theory 2.0.0

⚠️ WARNING: Breaking change detected!

Dependents affected: 1
  - roman_republic (requires ^1.0.0, would break with 2.0.0)

Recommendation:
  1. Generate migration guide
  2. Update roman_republic code
  3. Update dependency: ^1.0.0 → ^2.0.0
  4. Then bump to 2.0.0
```

---

## Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `status` | Show version info | `status military_theory` |
| `bump` | Increment version | `bump domain minor "desc"` |
| `deps` | Show dependencies | `deps roman_republic` |
| `check` | Check compatibility | `check domain 2.0.0` |
| `history` | Show changelog | `history military_theory` |
| `init` | Initialize versioning | `init domain --version 1.0.0` |
| `link` | Create dependency | `link domain_a domain_b` |

---

**Full Guide:** `docs/VERSION_MANAGEMENT_GUIDE.md`  
**Domain Guide:** `docs/DOMAIN_MANAGEMENT_GUIDE.md`
