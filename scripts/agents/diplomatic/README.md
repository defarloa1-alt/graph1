# Diplomatic Subject Facet Agent

**Facet:** DIPLOMATIC  
**Agent ID:** `diplomatic_sfa_001`  
**Status:** ✅ Production-ready (Phase 2 integrated)

## Overview

The Diplomatic SFA analyzes entities from a **diplomatic perspective**, focusing on:
- Treaties, alliances, and peace agreements
- Diplomatic missions, embassies, and envoys
- International relations and negotiations  
- Declarations of war and peace
- State visits, summits, and diplomatic correspondence
- Territorial exchanges and border agreements

## Phase 2 Integration

The Diplomatic SFA is fully integrated with the Phase 2 multi-agent architecture:

### 1. ClaimRegistry
- **Entity Deduplication**: Uses QID-based lookup to prevent duplicate entity nodes
- **Claim Submission**: Stores claims as `:ASSERTS` relationship properties from Agent to Entity
- **Metadata Support**: Includes source provenance, confidence, IGAR chains

### 2. PeerReviewer
- **Cross-Facet Validation**: Reviews claims from other SFAs
- **Agreement Scoring**: Tracks consensus across facets
- **Conflict Detection**: Identifies contested claims requiring arbitration

## Usage

### Basic Claim Submission

```python
from neo4j import GraphDatabase
from scripts.agents.diplomatic.agent import DiplomaticSFA

# Initialize
driver = GraphDatabase.driver(uri, auth=(user, password))
diplomatic_sfa = DiplomaticSFA(driver)

# Submit a claim about a treaty
claim_id = diplomatic_sfa.submit_diplomatic_claim(
    entity={
        'type': 'EVENT',
        'qid': 'Q170185',  # Treaty of Rome
        'label': 'Treaty of Rome'
    },
    predicate='signed_treaty',
    confidence=0.95,
    source_qid='Q123456'  # Source document
)
```

### Peer Review

```python
# Get entity cipher
with driver.session() as session:
    result = session.run("""
        MATCH (e {qid: 'Q170185'})
        RETURN e.entity_cipher as cipher
    """)
    entity_cipher = result.single()['cipher']

# Review claims from other SFAs
review_summary = diplomatic_sfa.review_peer_claims(entity_cipher)
print(f"Reviewed {review_summary['reviews_submitted']} claims")
print(f"Found {review_summary['contested_count']} contested claims")
```

### Diplomatic Significance Evaluation

```python
# Evaluate an entity's diplomatic significance
evaluation = diplomatic_sfa.evaluate_diplomatic_significance(
    entity={
        'type': 'EVENT',
        'qid': 'Q170185',
        'label': 'Treaty of Rome'
    },
    wikidata_props={
        'P710': ['Q1', 'Q2', 'Q3'],  # Multiple participants
        'P793': ['Q123'],  # Significant event marker
        'P1542': ['Q456']  # Lasting effects
    }
)

print(f"Confidence: {evaluation['confidence']}")
print(f"Factors: {evaluation['factors']}")
print(f"Suggested predicates: {evaluation['suggested_predicates']}")
```

## Evaluation Logic

The Diplomatic SFA scores diplomatic significance based on:

| Factor | Score Boost | Description |
|--------|-------------|-------------|
| **Multilateral treaty** | +0.3 | 10+ participating nations |
| **Multiple parties** | +0.2 | 3-9 participating nations |
| **Bilateral agreement** | +0.1 | 2 participating nations |
| **Significant event marker** | +0.15 | Wikidata P793 property |
| **Lasting effects** | +0.1 | Documented consequences (P1542) |
| **Diplomatic incident** | +0.1 | Treaty violations (P1399) |
| **Event entity** | +0.1 | Type is EVENT |

**Base confidence:** 0.5  
**Maximum confidence:** 1.0

## Diplomatic Predicates

The Diplomatic SFA recognizes 20 diplomatic-specific predicates:

### Treaties & Agreements
- `signed_treaty` - Formal international agreement
- `formed_alliance` - Military or political alliance
- `declared_peace` - Formal end of conflict
- `non_aggression_pact` - Non-aggression agreement
- `trade_agreement` - Economic treaty
- `border_agreement` - Territorial boundary agreement
- `territorial_exchange` - Territory transfer

### Diplomatic Actions
- `declared_war` - Formal declaration of hostilities
- `sent_envoy` - Diplomatic representative dispatched
- `received_embassy` - Diplomatic mission established
- `state_visit` - Official state-level visit
- `summit_participation` - International summit attendance
- `diplomatic_correspondence` - Official communication

### Negotiations & Processes
- `negotiated_agreement` - Diplomatic negotiation
- `peace_conference` - Peace negotiation meeting
- `mediation_effort` - Third-party mediation

### Incidents & Events
- `diplomatic_recognition` - Official recognition of state/government
- `treaty_violation` - Breach of diplomatic agreement
- `diplomatic_incident` - Diplomatic crisis or controversy
- `diplomatic_mission` - General diplomatic activity

## Wikidata Integration

The Diplomatic SFA enriches claims with Wikidata properties:

| Property | ID | Purpose |
|----------|-----|---------|
| significant event | P793 | Diplomatic importance marker |
| participant | P710 | Treaty signatories, participants |
| part of | P361 | Larger diplomatic context |
| described by source | P1343 | Historical sources |
| point in time | P585 | Event date |
| start time | P580 | Treaty start date |
| end time | P582 | Treaty end date |
| location | P276 | Location of event |
| product or material produced | P1056 | Treaty documents |
| subject has role | P2868 | Participant roles |
| convicted of | P1399 | Treaty violations |
| has cause | P828 | Diplomatic causes |
| has effect | P1542 | Diplomatic consequences |
| series ordinal | P2512 | Treaty sequence |
| dedicated to | P825 | Purpose/dedication |

## Testing

The Diplomatic SFA includes 13 comprehensive tests:

```bash
pytest scripts/tests/test_diplomatic_sfa.py -v
```

### Test Coverage
- ✅ Initialization and Phase 2 integration
- ✅ Claim submission with metadata
- ✅ Predicate validation
- ✅ Facet verification
- ✅ Peer review functionality
- ✅ Significance evaluation logic
- ✅ Wikidata property handling
- ✅ Predicate suggestion
- ✅ Entity deduplication
- ✅ Full workflow integration

**All 13 tests passing!**

## Architecture Pattern

The Diplomatic SFA follows the standard SFA pattern:

```python
class DiplomaticSFA(SubjectConceptFacetAgent):
    """
    Extends: SubjectConceptFacetAgent
    Integrates: ClaimRegistry, PeerReviewer
    """
    
    # 1. Facet-specific predicates
    DIPLOMATIC_PREDICATES = [...]
    
    # 2. Relevant Wikidata properties
    DIPLOMATIC_PROPERTIES = [...]
    
    # 3. Initialization
    def __init__(self, driver):
        super().__init__(facet_key="DIPLOMATIC", ...)
        self.claim_registry = ClaimRegistry(driver)
        self.peer_reviewer = PeerReviewer(driver)
    
    # 4. Claim submission
    def submit_diplomatic_claim(...):
        return self.claim_registry.submit_claim(...)
    
    # 5. Peer review
    def review_peer_claims(...):
        return self.peer_reviewer.review_entity_claims(...)
    
    # 6. Facet-specific evaluation
    def evaluate_diplomatic_significance(...):
        # Score based on diplomatic factors
        return {'confidence': ..., 'factors': ...}
    
    # 7. Wikidata enrichment
    def enrich_from_wikidata(...):
        # Fetch diplomatic-relevant properties
        return {...}
```

## Replication Template

To create a new SFA, copy this structure and adapt:

1. **Replace facet name**: `DIPLOMATIC` → `YOUR_FACET`
2. **Define predicates**: List facet-specific actions/events
3. **Define properties**: List relevant Wikidata properties
4. **Update evaluation logic**: Implement facet-specific scoring
5. **Update predicate suggestions**: Map entity patterns to predicates
6. **Create tests**: Adapt test suite to your facet
7. **Update README**: Document your facet's specifics

## Next Priority SFAs

Following the Diplomatic SFA implementation, these SFAs should be next:

### 1. Political SFA
- **Overlap**: Wars, treaties have political causes/effects
- **Focus**: Governance, elections, political movements
- **Synergy**: Complements military and diplomatic facets

### 2. Geographic SFA
- **Overlap**: Territories, locations, campaigns
- **Focus**: Physical spaces, borders, regions
- **Synergy**: Supports military, diplomatic, demographic

### 3. Economic SFA
- **Overlap**: Trade agreements, resource control
- **Focus**: Finance, commerce, resources
- **Synergy**: Complements diplomatic and political

## Files

### Core Implementation
- `scripts/agents/diplomatic/__init__.py` - Package exports
- `scripts/agents/diplomatic/agent.py` - Main Diplomatic SFA class (420 lines)

### Tests
- `scripts/tests/test_diplomatic_sfa.py` - Test suite (340 lines, 13 tests)

### Documentation
- `scripts/agents/diplomatic/README.md` - This file

## Dependencies

- `neo4j` - Graph database driver
- `scripts.agents.subject_concept_facet_agents` - Base SFA class
- `scripts.agents.claim_registry` - Entity/claim management
- `scripts.agents.peer_reviewer` - Cross-facet validation
- `requests` - Wikidata API calls

## Production Readiness

✅ **The Diplomatic SFA is production-ready:**
- All tests passing (13/13)
- Phase 2 integration complete
- Entity deduplication verified
- ClaimRegistry integration working
- PeerReviewer integration working
- Wikidata enrichment functional
- Comprehensive documentation

## Conclusion

The Diplomatic SFA successfully extends the Phase 2 architecture and serves as a proven template for implementing the remaining 16 Subject Facet Agents. Its integration with ClaimRegistry and PeerReviewer demonstrates the viability of the multi-agent claim submission and validation workflow.
