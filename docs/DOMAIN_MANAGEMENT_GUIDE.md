# Domain Management Guide

**Last Updated:** July 16, 2026  
**Architecture:** Chrystallum as "GitHub for Subgraphs"

---

## Table of Contents

1. [What is a Domain?](#what-is-a-domain)
2. [Domain vs SubjectConcept](#domain-vs-subjectconcept)
3. [Domain Hierarchy](#domain-hierarchy)
4. [Creating New Domains](#creating-new-domains)
5. [Domain Lifecycle](#domain-lifecycle)
6. [Dependency Management](#dependency-management)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

---

## What is a Domain?

A **Domain** is a versioned, top-level knowledge subgraph in Chrystallum. Think of it as a **repository** in GitHub — an independent, versioned collection of related knowledge that can evolve separately from other domains.

### Key Characteristics

- **Versioned:** Each domain has semantic version (major.minor.patch)
- **Independent:** Can evolve without affecting other domains
- **Composable:** Domains can depend on other domains
- **Trackable:** Complete version history and changelog
- **Bounded:** Clear scope and purpose

### Domain Structure

```cypher
(:Domain {
  domain_id: 'roman_republic',
  label: 'Roman Republic',
  version: '0.1.0',
  scope: 'historical',
  period: '509-27 BCE',
  versioned: true,
  version_created: datetime(),
  description: 'All knowledge about the Roman Republic'
})
```

---

## Domain vs SubjectConcept

Understanding the difference is critical:

### Domain

- **What:** Top-level knowledge container
- **Scope:** Broad (e.g., "Roman Republic", "Military Theory")
- **Versioned:** Yes — tracks changes to entire domain
- **Contains:** SubjectConcepts, theory nodes, claims
- **Example:** `ROMAN_REPUBLIC` (contains 93 SubjectConcepts)

### SubjectConcept

- **What:** Specific topic or area within a domain
- **Scope:** Narrow (e.g., "Roman Military", "Roman Diplomacy")
- **Versioned:** No — version tracked at domain level
- **Contained by:** A Domain (via `:CONTAINS` relationship)
- **Example:** `sc_military` (within ROMAN_REPUBLIC domain)

### Analogy

```
Domain          = GitHub Repository
SubjectConcept  = Folder/module in repository
Version         = Git tag/release
Dependencies    = package.json dependencies
```

---

## Domain Hierarchy

The complete hierarchy from registry to entities:

```
SubjectConceptRegistry (singleton)
├── TRACKS_DOMAIN → Domain:ROMAN_REPUBLIC (v0.1.0)
│   ├── CONTAINS → sc_military
│   ├── CONTAINS → sc_diplomacy
│   ├── CONTAINS → sc_economy
│   ├── CONTAINS → sc_q17167_facet_military
│   └── ... (93 SubjectConcepts total)
│   
├── TRACKS_DOMAIN → Domain:MILITARY_THEORY (v1.1.0)
│   ├── CONTAINS → MilitaryPrinciple:OODA Loop
│   ├── CONTAINS → Concept:decision cycle
│   ├── CONTAINS → Mechanism nodes
│   └── ... (32 theory nodes total)
│   
└── TRACKS_DOMAIN → Domain:GEOGRAPHY (v1.0.0)
    ├── CONTAINS → GEO_ADMIN_DIVISIONS
    ├── CONTAINS → GEO_HYDROGRAPHY
    ├── CONTAINS → GEO_PHYS_FEATURES
    └── CONTAINS → GEO_POLITICAL_ENTITIES
```

### Query the Hierarchy

```cypher
// Show all domains
MATCH (scr:SubjectConceptRegistry)-[:TRACKS_DOMAIN]->(d:Domain)
RETURN d.domain_id, d.label, d.version, d.scope
ORDER BY d.domain_id

// Show domain contents
MATCH (d:Domain {domain_id: 'roman_republic'})-[:CONTAINS]->(child)
RETURN labels(child)[0] as type, count(*) as count

// Visualize full hierarchy
MATCH (scr:SubjectConceptRegistry)-[:TRACKS_DOMAIN]->(d:Domain)
OPTIONAL MATCH (d)-[:CONTAINS]->(child)
RETURN scr, d, child
LIMIT 100
```

---

## Creating New Domains

### When to Create a New Domain

Create a new domain when you have:

1. **Distinct scope:** Different subject matter (historical, theoretical, spatial)
2. **Independent evolution:** Content that will change independently
3. **Significant size:** At least 10+ SubjectConcepts or substantial content
4. **Clear boundaries:** Well-defined scope and purpose

### Step-by-Step Process

#### 1. Create Domain Node

```cypher
CREATE (d:Domain {
  domain_id: 'diplomatic_history',
  label: 'Diplomatic History',
  scope: 'historical',
  period: '800 BCE - 600 CE',
  description: 'Inter-state relations, treaties, and diplomatic practices',
  created_at: datetime(),
  versioned: false
})
```

#### 2. Link to Registry

```cypher
MATCH (scr:SubjectConceptRegistry)
MATCH (d:Domain {domain_id: 'diplomatic_history'})
CREATE (scr)-[:TRACKS_DOMAIN]->(d)
```

#### 3. Initialize Versioning

```python
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)
manager.initialize_version(
    domain_id='diplomatic_history',
    version='1.0.0',
    description='Initial release of Diplomatic History domain'
)
```

#### 4. Add Content

```cypher
// Add SubjectConcepts or other nodes
MATCH (d:Domain {domain_id: 'diplomatic_history'})
MATCH (sc:SubjectConcept {subject_id: 'sc_treaties'})
CREATE (d)-[:CONTAINS]->(sc)
```

#### 5. Declare Dependencies (if needed)

```python
# If this domain references concepts from another domain
manager.add_dependency(
    dependent_id='diplomatic_history',
    dependency_id='roman_republic',
    version_spec='^0.1.0'
)
```

---

## Domain Lifecycle

### Phase 1: Creation

```
[Planning] → [Cypher Creation] → [Registry Link] → [Version Init]
```

**Checklist:**
- [ ] Domain purpose and scope defined
- [ ] Domain ID chosen (lowercase_underscore)
- [ ] Domain node created in Neo4j
- [ ] Linked to SubjectConceptRegistry
- [ ] Version initialized (1.0.0)

### Phase 2: Population

```
[Empty] → [Add Content] → [Organize] → [Version Bump]
```

**Checklist:**
- [ ] SubjectConcepts created/moved
- [ ] Content nodes organized
- [ ] Initial claims added
- [ ] Version bumped (1.0.0 → 1.1.0)

### Phase 3: Maturation

```
[Active Development] → [Stable] → [Mature]
```

**Indicators:**
- **Active:** v0.x.x — frequent changes
- **Stable:** v1.x.x — established structure, incremental updates
- **Mature:** v2.x.x+ — well-defined, occasional refinements

### Phase 4: Maintenance

```
[Minor Updates] → [Bug Fixes] → [Occasional Major Updates]
```

**Version pattern:**
- Patch bumps (1.1.0 → 1.1.1) — corrections
- Minor bumps (1.1.0 → 1.2.0) — new content
- Major bumps (1.x.x → 2.0.0) — restructuring

---

## Dependency Management

### Why Dependencies?

Domains often reference concepts from other domains:

- **ROMAN_REPUBLIC** events may reference **MILITARY_THEORY** principles
- **DIPLOMATIC_HISTORY** may reference **ROMAN_REPUBLIC** actors
- **GEOGRAPHY** provides spatial concepts to multiple domains

### Declaring Dependencies

```python
manager.add_dependency(
    dependent_id='roman_republic',
    dependency_id='military_theory',
    version_spec='^1.0.0'  # Compatible with 1.x
)
```

### Version Specifications

| Spec | Meaning | Example |
|------|---------|---------|
| `1.0.0` | Exact version | Only 1.0.0 works |
| `^1.0.0` | Compatible with 1.x | 1.0.0, 1.1.0, 1.9.9 OK; 2.0.0 breaks |
| `^1.2.0` | Compatible with 1.x, min 1.2.0 | 1.2.0+, not 1.1.0 |
| `*` | Any version | Always compatible |

### Checking Dependencies

```python
# Get all dependencies for a domain
deps = manager.get_dependencies('roman_republic')

for dep in deps:
    print(f"{dep['dependent']} depends on {dep['dependency']} @ {dep['version_spec']}")
    print(f"  Current version: {dep['dep_version']}")
    print(f"  Compatible: {dep['compatible']}")
```

### Dependency Graph

```cypher
// Visualize dependencies
MATCH (d1:Domain)-[dep:DEPENDS_ON]->(d2:Domain)
RETURN d1.label as dependent,
       d2.label as dependency,
       dep.version_spec as spec,
       d2.version as current_version
```

### Breaking Changes

When a dependency undergoes a major version bump:

```python
# Check impact before bumping MILITARY_THEORY from 1.x to 2.0
compat = manager.check_compatibility('military_theory', '2.0.0')

if compat['breaking_changes'] > 0:
    print(f"WARNING: {compat['breaking_changes']} dependent(s) affected:")
    for issue in compat['issues']:
        print(f"  - {issue['dependent']}: {issue['issue']}")
```

---

## Best Practices

### Domain Design

**DO:**
- Create domains for distinct knowledge areas
- Version domains, not individual SubjectConcepts
- Use semantic versioning consistently
- Document breaking changes in version history
- Declare dependencies explicitly

**DON'T:**
- Create overly granular domains (< 5 SubjectConcepts)
- Mix historical and theoretical content in same domain
- Make breaking changes without checking dependents
- Skip version bumps after significant changes
- Create circular dependencies

### Naming Conventions

**Domain IDs:**
- Lowercase with underscores: `roman_republic`, `military_theory`
- Descriptive: `diplomatic_history` not `dip_hist`
- Consistent: `roman_republic` not `romanrepublic`

**Domain Labels:**
- Title Case: "Roman Republic", "Military Theory"
- Human-readable: "Diplomatic History" not "Diplomacy Domain"

### Scope Guidelines

| Scope | Purpose | Example |
|-------|---------|---------|
| `historical` | Time-bound historical knowledge | ROMAN_REPUBLIC (509-27 BCE) |
| `theoretical` | Timeless theories/principles | MILITARY_THEORY (universal) |
| `spatial` | Geographic/spatial concepts | GEOGRAPHY (place types) |
| `methodological` | Research methods | PROSOPOGRAPHY (techniques) |

---

## Examples

### Example 1: Historical Domain (ROMAN_REPUBLIC)

```cypher
(:Domain {
  domain_id: 'roman_republic',
  label: 'Roman Republic',
  version: '0.1.0',
  scope: 'historical',
  period: '509-27 BCE',
  description: 'All knowledge about the Roman Republic',
  versioned: true
})
```

**Contains:**
- 93 SubjectConcepts (`sc_military`, `sc_diplomacy`, etc.)
- Facet-specific concepts (`sc_q17167_facet_*`)
- Historical entities (People, Events, Places)
- Claims about Roman Republic

**Dependencies:**
- `military_theory @ ^1.0.0` (references universal military principles)

### Example 2: Theoretical Domain (MILITARY_THEORY)

```cypher
(:Domain {
  domain_id: 'military_theory',
  label: 'Military Theory',
  version: '1.1.0',
  scope: 'theoretical',
  period: 'timeless',
  description: 'Universal military principles and theories',
  versioned: true
})
```

**Contains:**
- MilitaryPrinciple nodes (OODA Loop, etc.)
- SPO structure (Concept, Mechanism, Effect)
- Theory graphs (Boyd, Clausewitz)

**Dependents:**
- `roman_republic` (uses these principles)

**Version History:**
- v1.0.0: Boyd OODA principles
- v1.1.0: Added Clausewitz friction and trinity

### Example 3: Infrastructure Domain (GEOGRAPHY)

```cypher
(:Domain {
  domain_id: 'geography',
  label: 'Geography',
  version: '1.0.0',
  scope: 'spatial',
  period: 'timeless',
  description: 'Geographic classification and concepts',
  versioned: true
})
```

**Contains:**
- `GEO_PHYS_FEATURES` (2,282 Places)
- `GEO_HYDROGRAPHY` (2,155 Places)
- `GEO_ADMIN_DIVISIONS` (1,137 Places)
- `GEO_POLITICAL_ENTITIES` (1,604 Places)

**Purpose:**
- Organize 44,193 Place nodes
- Provide geographic concepts to other domains

---

## Working with Domains

### Python API

```python
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)

# Create and initialize
manager.initialize_version('new_domain', '1.0.0')

# Add content (via Cypher)
with driver.session() as session:
    session.run("""
        MATCH (d:Domain {domain_id: 'new_domain'})
        MATCH (sc:SubjectConcept {subject_id: 'sc_new_topic'})
        CREATE (d)-[:CONTAINS]->(sc)
    """)

# Bump version after changes
manager.bump_version(
    'new_domain',
    bump_type='minor',
    changes=['Added 10 new SubjectConcepts', 'Enhanced structure']
)

# Check status
history = manager.get_version_history('new_domain')
deps = manager.get_dependencies('new_domain')
```

### Cypher Queries

```cypher
// Show all domains with stats
MATCH (d:Domain)
OPTIONAL MATCH (d)-[:CONTAINS]->(child)
RETURN d.domain_id, d.label, d.version, count(child) as children
ORDER BY d.domain_id

// Find domains by scope
MATCH (d:Domain {scope: 'historical'})
RETURN d.domain_id, d.label, d.period

// Check dependencies
MATCH (d1:Domain {domain_id: 'roman_republic'})-[dep:DEPENDS_ON]->(d2:Domain)
RETURN d2.label as depends_on,
       dep.version_spec as required,
       d2.version as current
```

---

## Troubleshooting

### Problem: Domain Not Found

**Symptom:** `ValueError: Domain not found: domain_id`

**Solutions:**
1. Check domain ID spelling (case-sensitive)
2. Verify domain exists: `MATCH (d:Domain {domain_id: 'X'}) RETURN d`
3. Check if domain linked to registry

### Problem: Version Incompatibility

**Symptom:** Dependent domain breaks after dependency update

**Solutions:**
1. Check compatibility before bumping: `manager.check_compatibility()`
2. Generate migration guide: `scripts/system/generate_migration_guide.py`
3. Update dependent's version_spec to new major version
4. Review breaking changes and update code

### Problem: Circular Dependencies

**Symptom:** Domain A depends on B, B depends on A

**Solutions:**
1. Refactor: Extract shared concepts to third domain
2. Make dependency one-way only
3. Review domain boundaries — may be too granular

---

## Related Documentation

- **Version Management Guide:** [VERSION_MANAGEMENT_GUIDE.md](VERSION_MANAGEMENT_GUIDE.md)
- **SFA-Domain Integration:** [SFA_DOMAIN_INTEGRATION.md](SFA_DOMAIN_INTEGRATION.md)
- **Quick Reference:** [DOMAIN_QUICK_REFERENCE.md](DOMAIN_QUICK_REFERENCE.md)
- **CLI Reference:** [VERSION_CLI_REFERENCE.md](VERSION_CLI_REFERENCE.md)
- **Architecture:** [ARCHITECTURE_CURRENT.md](ARCHITECTURE_CURRENT.md)

---

## Summary

**Key Takeaways:**
- Domains are versioned top-level knowledge containers
- SubjectConcepts are organizational units within domains
- Version at domain level, not SubjectConcept level
- Use semantic versioning and declare dependencies
- Check compatibility before breaking changes

**Next Steps:**
1. Read [Version Management Guide](VERSION_MANAGEMENT_GUIDE.md)
2. Review [Quick Reference](DOMAIN_QUICK_REFERENCE.md)
3. Explore existing domains in Neo4j
4. Plan your domain structure
