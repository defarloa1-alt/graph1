# SFA (Subject-Facet Agent) Status Summary

**Date**: July 16, 2026  
**Total Canonical Facets**: 18  
**Current Status**: Framework complete, specialized implementations in progress

---

## The 18 Canonical Facets

From `scripts/agents/subject_concept_facet_agents.py`:

```python
CANONICAL_FACETS = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHIC", "COMMUNICATION",
    "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
    "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
    "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
    "SOCIAL", "TECHNOLOGICAL"
]
```

---

## Current Implementation Status

### ✅ Fully Implemented

**1. BIOGRAPHIC SFA** (`scripts/agents/biographic/agent.py`)
- Harvests biographical context for Person nodes
- Forward properties (birth/death dates, places, events)
- Backlinks (items referencing the person)
- Spouse qualifiers with temporal bounds
- External IDs (VIAF, GND, LCNAF, etc.)
- **Status**: Production-ready, actively used

### ✅ Framework Ready (All 18)

**Base Class**: `SubjectConceptFacetAgent` (`scripts/agents/subject_concept_facet_agents.py`)
- Claude API integration with tool-use for reasoning
- Graph tools: `query_graph`, `get_threshold`, `get_decision_table`
- Wikidata SPARQL enrichment
- Neo4j persistence
- **On-demand creation**: Factory can create any of the 18 facets

**Factory Method**:
```python
from scripts.agents.subject_concept_facet_agents import SubjectConceptAgentFactory

# Create single agent
military_agent = SubjectConceptAgentFactory.create_agent(
    facet_key="MILITARY",
    neo4j_driver=driver
)

# Create all 18 agents
all_agents = SubjectConceptAgentFactory.create_all_agents(
    neo4j_driver=driver
)
```

### 🚧 Partially Implemented

**2. GEO SFA** (`scripts/agents/geo/`)
- Geographic/spatial analysis
- Location relationships
- **Status**: Under development

**3. DOMAIN INITIATOR** (`scripts/agents/domain_initiator/`)
- Facet umbrellas
- Domain-level organization
- **Status**: Experimental

---

## What's Needed to Complete All 18

### Phase 3 Integration Tasks (Current)

From Phase 2 completion, the next step is **SFA Integration**:

**1. Update SFA Base Class** (Priority 1)
- Add `submit_claim()` wrapper that calls `ClaimRegistry`
- Add `review_peer_claims()` method for Phase 2 peer review
- Integrate with PeerReviewer service

**Example Implementation**:
```python
class SubjectConceptFacetAgent:
    def submit_claim_to_registry(self, entity, predicate, confidence, **kwargs):
        """Submit claim via ClaimRegistry instead of direct Neo4j write."""
        from scripts.agents.claim_registry import ClaimRegistry
        
        registry = ClaimRegistry(self.driver)
        return registry.submit_claim(
            entity=entity,
            predicate=predicate,
            facet=self.facet_key,
            agent_id=self.agent_id,
            confidence=confidence,
            **kwargs
        )
    
    def review_peer_claims(self, entity_cipher):
        """Phase 2: Review claims from other facets."""
        from scripts.agents.peer_reviewer import PeerReviewer
        
        reviewer = PeerReviewer(self.driver)
        return reviewer.review_entity_claims(
            entity_cipher=entity_cipher,
            reviewing_facet=self.facet_key,
            reviewing_agent=self.agent_id
        )
```

**2. Facet-Specific Evaluation Logic** (Priority 2)

Each facet should have custom logic for evaluating peer claims:

```python
class MilitarySFA(SubjectConceptFacetAgent):
    def evaluate_peer_claim(self, claim):
        """Military-specific claim evaluation."""
        # Military facet trusts high-confidence claims about battles
        if claim['predicate'] in ['crossed_rubicon', 'battle_at']:
            if claim['confidence'] >= 0.85:
                return {'agrees': True, 'note': 'High military confidence'}
        
        # Defer to base class for other claims
        return super().evaluate_peer_claim(claim)
```

**3. Migration Script for Legacy Data** (Priority 3)

```python
# scripts/agents/migrate_legacy_claims.py
"""
Migrate existing claims to new Canonical Entity + Facet-Scoped Claims model.

Steps:
1. Find all existing claims (old format)
2. For each claim:
   - Generate entity cipher
   - Check if canonical entity exists
   - Create canonical entity if needed
   - Rewrite claim as :ASSERTS edge with facet metadata
   - Preserve provenance
3. Mark old claims as migrated
"""
```

**4. Specialized SFA Implementations** (Priority 4)

Each of the 18 facets should have specialized implementation like BIOGRAPHIC:

**Required Files per Facet**:
```
scripts/agents/{facet_name}/
├── agent.py          # Main SFA implementation
├── README.md         # Documentation
├── prompts.py        # Facet-specific prompts
└── tests.py          # Unit tests
```

**Example: MILITARY SFA**
```python
# scripts/agents/military/agent.py
class MilitarySFA(SubjectConceptFacetAgent):
    """Military facet agent - battles, conflicts, strategies"""
    
    FACET_SPECIFIC_PROPERTIES = [
        "P607",  # conflict
        "P361",  # part of
        "P710",  # participant
        "P585",  # point in time
        "P276",  # location
    ]
    
    def analyze_subject_concept(self, subject_concept_id):
        """Analyze from military perspective."""
        # Military-specific analysis logic
        pass
    
    def harvest_military_context(self, entity_qid):
        """Harvest military-specific Wikidata properties."""
        pass
```

**5. Control Shell (Optional, Priority 5)**

Orchestrate multi-agent workflows:

```python
# scripts/agents/control_shell.py
class ControlShell:
    """Orchestrate multi-agent processing."""
    
    def orchestrate_subject_concept(self, subject_concept_id, facets=None):
        """
        Run all 18 SFAs (or selected facets) on a subject concept.
        
        Phase 1: Knowledge Acquisition
        - Each SFA analyzes and submits claims (status: TBD)
        
        Phase 2: Peer Review
        - Each SFA reviews claims from other facets
        - Write :REVIEWED edges
        
        Phase 3: Promotion
        - Auto-promote high-agreement claims to CONFIRMED
        - Flag contested claims
        """
        if facets is None:
            facets = CANONICAL_FACETS
        
        # Phase 1: Knowledge Acquisition
        for facet in facets:
            agent = SubjectConceptAgentFactory.create_agent(facet, self.driver)
            agent.analyze_subject_concept(subject_concept_id)
        
        # Phase 2: Peer Review
        for facet in facets:
            agent = SubjectConceptAgentFactory.create_agent(facet, self.driver)
            agent.review_peer_claims(entity_cipher)
        
        # Phase 3: Promotion
        reviewer = PeerReviewer(self.driver)
        reviewer.promote_high_agreement_claims()
        reviewer.flag_contested_claims()
```

---

## Implementation Roadmap

### Immediate (Phase 3)

**Week 1-2: Core Integration**
1. Update `SubjectConceptFacetAgent` base class with:
   - `submit_claim_to_registry()` wrapper
   - `review_peer_claims()` method
   - Facet-specific evaluation hooks

2. Update BIOGRAPHIC SFA to use new architecture:
   - Replace direct Neo4j writes with `ClaimRegistry`
   - Add peer review logic
   - Test end-to-end

**Week 3-4: Specialized Implementations**
3. Implement priority facets (based on project needs):
   - MILITARY (battles, conflicts)
   - POLITICAL (governance, offices)
   - GEOGRAPHIC (places, locations)
   - RELIGIOUS (beliefs, practices)
   - ECONOMIC (trade, resources)

4. Create facet-specific prompts and evaluation logic

### Medium-Term (Phases 4-5)

**Month 2-3: Remaining Facets**
5. Implement remaining 13 facets:
   - ARCHAEOLOGICAL, ARTISTIC, COMMUNICATION
   - CULTURAL, DEMOGRAPHIC, DIPLOMATIC
   - ENVIRONMENTAL, INTELLECTUAL, LINGUISTIC
   - SCIENTIFIC, SOCIAL, TECHNOLOGICAL

6. Comprehensive testing across all facets

**Month 3-4: Production Deployment**
7. Migration script for legacy data
8. Control Shell for orchestration
9. Message Bus for async coordination (optional)
10. Performance optimization
11. Production deployment

---

## Current Architecture Advantage

**Good News**: The framework is already built!

- ✅ Base class supports all 18 facets
- ✅ Factory can create any facet on-demand
- ✅ Claude API integration ready
- ✅ Graph tools operational
- ✅ ClaimRegistry ready for use
- ✅ PeerReviewer ready for use

**What's Needed**: Specialized implementations per facet (like BIOGRAPHIC)

---

## Testing Strategy

**Per-Facet Tests**:
```python
# scripts/agents/{facet}/tests.py
def test_military_sfa_submit_claim():
    """Test Military SFA submits claims via ClaimRegistry."""
    sfa = MilitarySFA(driver)
    result = sfa.submit_claim_to_registry(
        entity={'type': 'EVENT', 'qid': 'Q40979', 'label': 'Battle of Actium'},
        predicate='occurred_during',
        confidence=0.95
    )
    assert result is not None

def test_military_sfa_peer_review():
    """Test Military SFA reviews peer claims."""
    sfa = MilitarySFA(driver)
    reviews = sfa.review_peer_claims('ent_evt_Q40979')
    assert len(reviews) >= 0
```

---

## Summary

**Current State**:
- 18 facets defined ✅
- Base framework complete ✅
- 1 specialized SFA (BIOGRAPHIC) production-ready ✅
- ClaimRegistry operational ✅
- PeerReviewer operational ✅

**To Get All 18 Active**:
1. Integrate base class with ClaimRegistry/PeerReviewer (1-2 weeks)
2. Implement 5 priority facets (2-3 weeks each)
3. Implement remaining 13 facets (1-2 weeks each)
4. Migration script (1 week)
5. Production testing & deployment (2 weeks)

**Estimated Total**: 3-4 months for all 18 fully specialized + production-ready

**Recommended Approach**: Incremental deployment
1. Start with 5 priority facets (MILITARY, POLITICAL, GEOGRAPHIC, RELIGIOUS, ECONOMIC)
2. Deploy to production with Phase 2 peer review
3. Add remaining facets as needed based on data priorities
