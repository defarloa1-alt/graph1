# Domain Quick Reference

**Chrystallum Domain Architecture — One-Page Cheat Sheet**

---

## Domain Hierarchy

```
SubjectConceptRegistry
├── ROMAN_REPUBLIC (v0.1.0) — 93 SubjectConcepts
│   └── DEPENDS_ON → MILITARY_THEORY @ ^1.0.0
├── MILITARY_THEORY (v1.1.0) — 32 theory nodes
└── GEOGRAPHY (v1.0.0) — 4 geo SubjectConcepts
```

---

## Core Concepts

| Concept | What | Example |
|---------|------|---------|
| **Domain** | Top-level versioned subgraph | ROMAN_REPUBLIC |
| **SubjectConcept** | Topic within domain | sc_military |
| **Version** | Semantic version (X.Y.Z) | 1.1.0 |
| **Dependency** | Domain A references Domain B | ROMAN_REPUBLIC → MILITARY_THEORY |

---

## Domain vs SubjectConcept

| Aspect | Domain | SubjectConcept |
|--------|--------|----------------|
| **Scope** | Broad (e.g., "Roman Republic") | Narrow (e.g., "Roman Military") |
| **Versioned** | ✅ Yes | ❌ No (tracked at domain level) |
| **Contains** | SubjectConcepts, claims, entities | Claims, entities |
| **Analogy** | GitHub repository | Folder in repository |

---

## Semantic Versioning

```
v 2  .  5  .  1
  │    │    │
  │    │    └─ PATCH: Bug fixes (1.1.0 → 1.1.1)
  │    └────── MINOR: New features (1.0.0 → 1.1.0)
  └─────────── MAJOR: Breaking changes (1.x.x → 2.0.0)
```

**When to Bump:**
- **Major:** Removed SubjectConcepts, restructured
- **Minor:** Added SubjectConcepts, new claims
- **Patch:** Fixed errors, corrected data

---

## Version Specifications

| Spec | Meaning | Allows |
|------|---------|--------|
| `1.0.0` | Exact | Only 1.0.0 |
| `^1.0.0` | Compatible 1.x | 1.0.0, 1.1.0, 1.9.9 ✓ / 2.0.0 ✗ |
| `*` | Any | All versions |

---

## Common Commands

### Check Status
```bash
python scripts/system/version_cli.py status military_theory
```

### Bump Version
```bash
# Minor (new features)
python scripts/system/version_cli.py bump military_theory minor "Added content"

# Major (breaking)
python scripts/system/version_cli.py bump military_theory major "Restructured"

# Patch (fixes)
python scripts/system/version_cli.py bump military_theory patch "Fixed errors"
```

### Dependencies
```bash
# Show dependencies
python scripts/system/version_cli.py deps roman_republic

# Check compatibility
python scripts/system/version_cli.py check military_theory 2.0.0

# Link domains
python scripts/system/version_cli.py link roman_republic military_theory --spec "^1.0.0"
```

### History
```bash
python scripts/system/version_cli.py history military_theory
```

---

## Python API

```python
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)

# Initialize
manager.initialize_version('domain_id', '1.0.0')

# Bump
manager.bump_version('domain_id', 'minor', changes=['Added X'])

# Dependency
manager.add_dependency('domain_a', 'domain_b', '^1.0.0')

# Check
compat = manager.check_compatibility('domain_id', '2.0.0')

# History
history = manager.get_version_history('domain_id')
```

---

## Cypher Queries

```cypher
-- Show all domains
MATCH (scr:SubjectConceptRegistry)-[:TRACKS_DOMAIN]->(d:Domain)
RETURN d.domain_id, d.label, d.version

-- Domain contents
MATCH (d:Domain {domain_id: 'roman_republic'})-[:CONTAINS]->(child)
RETURN labels(child)[0], count(*)

-- Dependencies
MATCH (d1:Domain)-[dep:DEPENDS_ON]->(d2:Domain)
RETURN d1.label, d2.label, dep.version_spec

-- Version history
MATCH (d:Domain {domain_id: 'X'})-[:HAS_VERSION]->(v:Version)
RETURN v.version, v.created_at, v.changes
ORDER BY v.created_at DESC
```

---

## Current Domains

| Domain | Version | Scope | Children | Dependencies |
|--------|---------|-------|----------|--------------|
| ROMAN_REPUBLIC | v0.1.0 | historical | 93 | military_theory @ ^1.0.0 |
| MILITARY_THEORY | v1.1.0 | theoretical | 32 | none |
| GEOGRAPHY | v1.0.0 | spatial | 4 | none |

---

## Workflow Examples

### Safe Minor Update
```bash
# Add content → Bump minor → Dependents auto-compatible ✓
python scripts/system/version_cli.py bump military_theory minor "Added Sun Tzu"
```

### Breaking Major Update
```bash
# 1. Check impact
python scripts/system/version_cli.py check military_theory 2.0.0

# 2. Generate migration guide
python scripts/system/generate_migration_guide.py military_theory 1.1.0 2.0.0

# 3. Update dependent code

# 4. Update dependency
python scripts/system/version_cli.py link roman_republic military_theory --spec "^2.0.0"

# 5. Bump
python scripts/system/version_cli.py bump military_theory major "Restructured"
```

---

## SFA Integration

```python
class MilitarySFA:
    def __init__(self, driver):
        self.domain_id = 'roman_republic'
        self.version_manager = DomainVersionManager(driver)
        
        # Check dependencies
        deps = self.version_manager.get_dependencies('roman_republic')
        theory = next(d for d in deps if d['dependency'] == 'military_theory')
        
        if not theory['compatible']:
            raise ValueError("Incompatible military_theory version")
    
    def link_to_theory(self, event, principle):
        # Safe - dependency checked in __init__
        self.submit_cross_domain_claim(event, principle)
```

---

## Key Files

```
scripts/system/
├── domain_version_manager.py      # Core manager
└── version_cli.py                  # CLI tool

docs/
├── DOMAIN_MANAGEMENT_GUIDE.md     # Full domain guide
├── VERSION_MANAGEMENT_GUIDE.md    # Full version guide
├── SFA_DOMAIN_INTEGRATION.md      # SFA integration
├── DOMAIN_QUICK_REFERENCE.md      # This file
└── VERSION_CLI_REFERENCE.md       # CLI reference
```

---

## Best Practices

✅ **DO:**
- Version at domain level, not SubjectConcept level
- Check dependencies before cross-domain references
- Bump version after significant changes
- Use `^X.Y.Z` for flexible dependencies
- Check compatibility before major bumps

❌ **DON'T:**
- Create domains < 5 SubjectConcepts (too granular)
- Skip version bumps after changes
- Reference domains without dependencies
- Use `*` for version specs (too loose)
- Make breaking changes without migration plan

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Domain not found | Check spelling, verify exists in Neo4j |
| Version not updating | Check `versioned: true` property |
| Dependency conflict | Update dependent code, change version_spec |
| Breaking change | Generate migration guide, update dependents |

---

**Full Docs:** `docs/DOMAIN_MANAGEMENT_GUIDE.md`  
**Architecture:** `docs/ARCHITECTURE_CURRENT.md`
