# SFA-Domain Integration Guide

**Last Updated:** July 16, 2026  
**Architecture:** Subject-Facet Agents (SFAs) + Domain Versioning

---

## Table of Contents

1. [Overview](#overview)
2. [Which Domain, Which SFA](#which-domain-which-sfa)
3. [Domain Awareness for SFAs](#domain-awareness-for-sfas)
4. [Cross-Domain Claims](#cross-domain-claims)
5. [Dependency Management](#dependency-management)
6. [Versioning Integration](#versioning-integration)
7. [Implementation Patterns](#implementation-patterns)
8. [Examples](#examples)

---

## Overview

Subject-Facet Agents (SFAs) operate **within domains** and must be aware of:
- Which domain they're working in
- What dependencies that domain has
- Version compatibility when making cross-domain references

### Architecture Context

```
SubjectConceptRegistry
├── Domain:ROMAN_REPUBLIC (v0.1.0)
│   ├── SubjectConcept: sc_military
│   │   └── SFA: military_sfa_001 (MILITARY facet)
│   ├── SubjectConcept: sc_diplomacy
│   │   └── SFA: diplomatic_sfa_001 (DIPLOMATIC facet)
│   └── SubjectConcept: sc_economy
│       └── SFA: economic_sfa_001 (ECONOMIC facet)
│
└── Domain:MILITARY_THEORY (v1.1.0)
    ├── MilitaryPrinciple: OODA Loop
    └── Concept: decision cycle
```

### Key Principles

1. **SFAs work within a domain** — Each SFA is scoped to SubjectConcepts within a specific domain
2. **Cross-domain references must check dependencies** — Before referencing another domain
3. **Version compatibility matters** — Ensure referenced domain version is compatible
4. **Claims track domain provenance** — Each claim records which domain it came from

---

## Which Domain, Which SFA

### Domain-SFA Mapping

| Domain | SFAs | Focus |
|--------|------|-------|
| **ROMAN_REPUBLIC** | Military, Political, Geographic, Religious, Economic, Diplomatic, Cultural, Legal, Social, Biographic, Intellectual, Material, Technological, Environmental, Prosopographic | Historical Roman Republic (509-27 BCE) |
| **MILITARY_THEORY** | Military Theory SFA | Universal military principles (Boyd, Clausewitz, Sun Tzu) |
| **GEOGRAPHY** | Geographic SFA | Place classification and spatial concepts |

### SFA Scope by Domain

#### ROMAN_REPUBLIC SFAs (18 facets)

Each SFA works on specific facet within Roman Republic domain:

```python
# Military SFA
class MilitarySFA:
    domain = 'roman_republic'
    facet = 'MILITARY'
    subject_concepts = ['sc_military', 'sc_q17167_facet_military']
```

**Example SubjectConcepts:**
- `sc_military` — Roman Army & Military Campaigns
- `sc_diplomacy` — Roman Diplomacy & Foreign Relations
- `sc_economy` — Roman Economy, Finance & Trade
- `sc_religion` — Roman Religion & Religious Institutions

#### MILITARY_THEORY SFA

Works on theoretical military principles:

```python
class MilitaryTheorySFA:
    domain = 'military_theory'
    scope = 'theoretical'
    content = ['MilitaryPrinciple', 'Concept', 'Mechanism']
```

**Content:**
- Boyd's OODA Loop
- Clausewitz's friction and trinity
- Sun Tzu's principles (planned)

#### GEOGRAPHY SFA

Infrastructure domain for place classification:

```python
class GeographicSFA:
    domain = 'geography'
    scope = 'spatial'
    subject_concepts = [
        'GEO_PHYS_FEATURES',
        'GEO_HYDROGRAPHY',
        'GEO_ADMIN_DIVISIONS',
        'GEO_POLITICAL_ENTITIES'
    ]
```

---

## Domain Awareness for SFAs

SFAs must be aware of their operating domain.

### SFA Configuration

```python
class MilitarySFA(SubjectConceptFacetAgent):
    """Military SFA working in ROMAN_REPUBLIC domain."""
    
    def __init__(self, neo4j_driver, **kwargs):
        super().__init__(
            facet_key="MILITARY",
            facet_label="Military",
            neo4j_driver=neo4j_driver,
            **kwargs
        )
        
        # Domain configuration
        self.domain_id = 'roman_republic'
        self.domain_version_manager = DomainVersionManager(neo4j_driver)
        
        # Check domain exists and is versioned
        self._verify_domain()
    
    def _verify_domain(self):
        """Ensure domain exists and is properly configured."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                RETURN d.version as version, d.versioned as versioned
            """, domain_id=self.domain_id)
            
            record = result.single()
            if not record:
                raise ValueError(f"Domain not found: {self.domain_id}")
            
            if not record['versioned']:
                raise ValueError(f"Domain not versioned: {self.domain_id}")
            
            self.domain_version = record['version']
```

### Claim Submission with Domain Context

```python
def submit_military_claim(self, entity, predicate, confidence, **kwargs):
    """Submit claim with domain context."""
    
    claim_id = self.claim_registry.submit_claim(
        entity=entity,
        predicate=predicate,
        facet="MILITARY",
        agent_id=self.agent_id,
        confidence=confidence,
        domain=self.domain_id,  # Track which domain claim came from
        domain_version=self.domain_version,  # Track domain version
        **kwargs
    )
    
    return claim_id
```

---

## Cross-Domain Claims

When an SFA needs to reference content from another domain:

### Example: Roman Event → Military Theory

```
Roman Republic Domain (v0.1.0)
  Event: Battle of Cannae
    ↓
  References → Military Theory Domain (v1.1.0)
    Principle: OODA Loop
```

### Check Dependencies First

```python
class MilitarySFA:
    def link_event_to_theory(self, event_cipher, principle_label):
        """
        Link Roman Republic event to Military Theory principle.
        Must check domain dependency before creating link.
        """
        
        # 1. Check that ROMAN_REPUBLIC depends on MILITARY_THEORY
        deps = self.domain_version_manager.get_dependencies('roman_republic')
        
        theory_dep = next(
            (d for d in deps if d['dependency'] == 'military_theory'),
            None
        )
        
        if not theory_dep:
            raise ValueError(
                "ROMAN_REPUBLIC does not declare dependency on MILITARY_THEORY. "
                "Add dependency first."
            )
        
        # 2. Check version compatibility
        if not theory_dep['compatible']:
            raise ValueError(
                f"Version incompatibility: "
                f"ROMAN_REPUBLIC requires {theory_dep['version_spec']}, "
                f"but MILITARY_THEORY is at {theory_dep['dep_version']}"
            )
        
        # 3. Safe to create cross-domain claim
        self.submit_cross_domain_claim(
            source_domain='roman_republic',
            source_entity=event_cipher,
            target_domain='military_theory',
            target_entity=principle_label,
            predicate='demonstrates_principle',
            confidence=0.85
        )
```

### Cross-Domain Claim Structure

```cypher
// Cross-domain claim
(:Entity {cipher: 'ent_event_battle_cannae'})
  -[:DEMONSTRATES_PRINCIPLE {
    source_domain: 'roman_republic',
    source_version: '0.1.0',
    target_domain: 'military_theory',
    target_version: '1.1.0',
    facet: 'MILITARY',
    confidence: 0.85,
    agent_id: 'military_sfa_001'
  }]->
(:MilitaryPrinciple {label: 'OODA Loop'})
```

---

## Dependency Management

### Declare Dependencies

When an SFA needs to reference another domain, declare the dependency:

```python
# One-time setup
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)

# Declare that ROMAN_REPUBLIC depends on MILITARY_THEORY
manager.add_dependency(
    dependent_id='roman_republic',
    dependency_id='military_theory',
    version_spec='^1.0.0'  # Compatible with 1.x
)
```

### Check Dependencies at Runtime

```python
class MilitarySFA:
    def __init__(self, driver):
        self.driver = driver
        self.domain_id = 'roman_republic'
        self.version_manager = DomainVersionManager(driver)
        
        # Load dependencies
        self.dependencies = self._load_dependencies()
    
    def _load_dependencies(self):
        """Load and cache domain dependencies."""
        deps = self.version_manager.get_dependencies(self.domain_id)
        
        return {
            dep['dependency']: {
                'version_spec': dep['version_spec'],
                'current_version': dep['dep_version'],
                'compatible': dep['compatible']
            }
            for dep in deps
        }
    
    def can_reference_domain(self, domain_id):
        """Check if this SFA can reference another domain."""
        if domain_id not in self.dependencies:
            return False
        
        return self.dependencies[domain_id]['compatible']
```

### Dependency Validation

```python
def validate_dependencies(self):
    """Validate all dependencies are satisfied."""
    
    deps = self.version_manager.get_dependencies(self.domain_id)
    
    issues = []
    for dep in deps:
        if not dep['compatible']:
            issues.append({
                'dependency': dep['dependency'],
                'required': dep['version_spec'],
                'current': dep['dep_version'],
                'issue': 'Version incompatibility'
            })
    
    if issues:
        raise DependencyError(
            f"Dependency issues in {self.domain_id}",
            issues=issues
        )
```

---

## Versioning Integration

### Version Awareness

SFAs should track which domain version they're working with:

```python
class MilitarySFA:
    def __init__(self, driver):
        self.domain_id = 'roman_republic'
        self.domain_version = self._get_domain_version()
    
    def _get_domain_version(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Domain {domain_id: $domain_id})
                RETURN d.version as version
            """, domain_id=self.domain_id)
            return result.single()['version']
```

### Version Compatibility Checks

Before making cross-domain claims:

```python
def check_theory_compatibility(self, required_version='1.0.0'):
    """Check if MILITARY_THEORY version is sufficient."""
    
    deps = self.version_manager.get_dependencies('roman_republic')
    theory = next(d for d in deps if d['dependency'] == 'military_theory')
    
    from packaging import version
    
    if version.parse(theory['dep_version']) < version.parse(required_version):
        raise ValueError(
            f"MILITARY_THEORY {required_version}+ required, "
            f"but {theory['dep_version']} available"
        )
```

### Claim Version Metadata

Track version in claims:

```python
claim_metadata = {
    'domain': 'roman_republic',
    'domain_version': '0.1.0',
    'dependency_domain': 'military_theory',
    'dependency_version': '1.1.0',
    'version_checked': True
}
```

---

## Implementation Patterns

### Pattern 1: Single-Domain SFA

Works entirely within one domain:

```python
class DiplomaticSFA(SubjectConceptFacetAgent):
    """Works only in ROMAN_REPUBLIC domain."""
    
    def __init__(self, driver):
        super().__init__(
            facet_key="DIPLOMATIC",
            facet_label="Diplomatic",
            neo4j_driver=driver
        )
        self.domain_id = 'roman_republic'
        # No cross-domain dependencies needed
    
    def submit_diplomatic_claim(self, entity, predicate, confidence):
        """Submit claim within ROMAN_REPUBLIC domain."""
        return self.claim_registry.submit_claim(
            entity=entity,
            predicate=predicate,
            facet="DIPLOMATIC",
            domain=self.domain_id,
            confidence=confidence
        )
```

### Pattern 2: Cross-Domain SFA

References multiple domains:

```python
class MilitarySFA(SubjectConceptFacetAgent):
    """Works in ROMAN_REPUBLIC, references MILITARY_THEORY."""
    
    def __init__(self, driver):
        super().__init__(
            facet_key="MILITARY",
            facet_label="Military",
            neo4j_driver=driver
        )
        self.domain_id = 'roman_republic'
        self.version_manager = DomainVersionManager(driver)
        
        # Verify dependencies
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Ensure MILITARY_THEORY dependency exists."""
        deps = self.version_manager.get_dependencies('roman_republic')
        
        theory_dep = next(
            (d for d in deps if d['dependency'] == 'military_theory'),
            None
        )
        
        if not theory_dep:
            raise ValueError("Missing military_theory dependency")
        
        if not theory_dep['compatible']:
            raise ValueError("Incompatible military_theory version")
    
    def link_event_to_principle(self, event, principle):
        """Create cross-domain link."""
        # Safe because dependencies checked in __init__
        return self.submit_cross_domain_claim(
            source_domain='roman_republic',
            source_entity=event,
            target_domain='military_theory',
            target_entity=principle
        )
```

### Pattern 3: Theory SFA

Provides concepts to other domains:

```python
class MilitaryTheorySFA:
    """Provides universal military principles."""
    
    def __init__(self, driver):
        self.driver = driver
        self.domain_id = 'military_theory'
        self.version_manager = DomainVersionManager(driver)
    
    def add_principle(self, principle_data):
        """Add new military principle."""
        # Add to MILITARY_THEORY domain
        with self.driver.session() as session:
            session.run("""
                MATCH (d:Domain {domain_id: 'military_theory'})
                CREATE (p:MilitaryPrinciple {
                    label: $label,
                    description: $description
                })
                CREATE (d)-[:CONTAINS]->(p)
            """, **principle_data)
        
        # Bump version (minor - new feature)
        self.version_manager.bump_version(
            'military_theory',
            bump_type='minor',
            changes=[f"Added principle: {principle_data['label']}"]
        )
```

---

## Examples

### Example 1: Military SFA (Cross-Domain)

```python
class MilitarySFA(SubjectConceptFacetAgent):
    def __init__(self, neo4j_driver):
        super().__init__(
            facet_key="MILITARY",
            facet_label="Military",
            neo4j_driver=neo4j_driver
        )
        
        # Domain configuration
        self.domain_id = 'roman_republic'
        self.version_manager = DomainVersionManager(neo4j_driver)
        self.agent_id = "military_sfa_001"
        
        # Initialize services
        self.claim_registry = ClaimRegistry(neo4j_driver)
        
        # Check dependencies
        self._verify_military_theory_dependency()
    
    def _verify_military_theory_dependency(self):
        """Ensure MILITARY_THEORY is available."""
        deps = self.version_manager.get_dependencies('roman_republic')
        
        theory = next(
            (d for d in deps if d['dependency'] == 'military_theory'),
            None
        )
        
        if not theory or not theory['compatible']:
            raise ValueError(
                "MILITARY_THEORY dependency not satisfied. "
                "Declare dependency: "
                "manager.add_dependency('roman_republic', 'military_theory', '^1.0.0')"
            )
    
    def analyze_battle(self, battle_cipher):
        """Analyze battle using military theory."""
        
        # 1. Get battle data (within ROMAN_REPUBLIC)
        battle_data = self._get_battle_data(battle_cipher)
        
        # 2. Reference MILITARY_THEORY principles (cross-domain)
        relevant_principles = self._find_relevant_principles(battle_data)
        
        # 3. Create cross-domain claims
        for principle in relevant_principles:
            self.claim_registry.submit_claim(
                entity={'cipher': battle_cipher},
                predicate='demonstrates_principle',
                object={'label': principle['label']},
                facet="MILITARY",
                domain='roman_republic',
                target_domain='military_theory',
                confidence=principle['confidence'],
                agent_id=self.agent_id
            )
```

### Example 2: Diplomatic SFA (Single-Domain)

```python
class DiplomaticSFA(SubjectConceptFacetAgent):
    def __init__(self, neo4j_driver):
        super().__init__(
            facet_key="DIPLOMATIC",
            facet_label="Diplomatic",
            neo4j_driver=neo4j_driver
        )
        
        # Single domain
        self.domain_id = 'roman_republic'
        self.agent_id = "diplomatic_sfa_001"
        self.claim_registry = ClaimRegistry(neo4j_driver)
        
        # No cross-domain dependencies needed
    
    def analyze_treaty(self, treaty_cipher):
        """Analyze treaty (stays within ROMAN_REPUBLIC)."""
        
        # All data within ROMAN_REPUBLIC domain
        treaty_data = self._get_treaty_data(treaty_cipher)
        parties = self._get_treaty_parties(treaty_cipher)
        
        # Submit claim within domain
        self.claim_registry.submit_claim(
            entity={'cipher': treaty_cipher},
            predicate='involves_parties',
            object=parties,
            facet="DIPLOMATIC",
            domain='roman_republic',
            confidence=0.90,
            agent_id=self.agent_id
        )
```

### Example 3: Version Bump After SFA Work

```python
# After Military SFA adds significant content
from scripts.system.domain_version_manager import DomainVersionManager

manager = DomainVersionManager(driver)

# SFA added 50 new claims about Roman military
manager.bump_version(
    'roman_republic',
    bump_type='minor',
    changes=[
        'Added 50 military claims from Polybius',
        'Enhanced battle analysis',
        'Added legion organization data'
    ],
    description='Military SFA: Polybius corpus integration'
)
```

---

## Best Practices

### Domain Configuration

**DO:**
- ✅ Explicitly declare domain in SFA __init__
- ✅ Verify domain exists before operation
- ✅ Check dependencies at initialization
- ✅ Track domain version in claims

**DON'T:**
- ❌ Hard-code domain assumptions
- ❌ Reference other domains without checking dependencies
- ❌ Ignore version compatibility
- ❌ Skip dependency validation

### Cross-Domain References

**DO:**
- ✅ Check dependency exists before reference
- ✅ Verify version compatibility
- ✅ Track source and target domains in claims
- ✅ Document cross-domain relationships

**DON'T:**
- ❌ Create references without dependencies
- ❌ Assume other domains are always available
- ❌ Ignore version mismatches
- ❌ Create circular dependencies

### Version Management

**DO:**
- ✅ Bump domain version after significant SFA work
- ✅ Use minor bumps for new content
- ✅ Document what the SFA added
- ✅ Check dependent domains before major bumps

**DON'T:**
- ❌ Forget to bump version after changes
- ❌ Use major bumps for additive changes
- ❌ Break dependencies without migration plan
- ❌ Skip changelog documentation

---

## Related Documentation

- **Domain Management Guide:** `docs/DOMAIN_MANAGEMENT_GUIDE.md`
- **Version Management Guide:** `docs/VERSION_MANAGEMENT_GUIDE.md`
- **SCA-SFA Contract:** `docs/SCA_SFA_CONTRACT.md`
- **Military SFA Implementation:** `MILITARY_SFA_IMPLEMENTATION.md`

---

## Summary

**Key Takeaways:**
- SFAs work within specific domains
- Cross-domain references require declared dependencies
- Version compatibility must be checked
- Claims track domain provenance
- Domain versions bump after significant SFA work

**Implementation Checklist:**
- [ ] Declare domain in SFA configuration
- [ ] Verify domain exists
- [ ] Check dependencies if cross-domain
- [ ] Validate version compatibility
- [ ] Track domain/version in claims
- [ ] Bump domain version after changes
