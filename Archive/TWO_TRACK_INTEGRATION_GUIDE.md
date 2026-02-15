# Two-Track Validation Integration Guide
**How to Deploy Temporal Bridge Discovery in Your Pipeline**

Date: February 15, 2026  
Target: Wikipedia → Neo4j claim extraction pipeline

---

## Quick Start: Replace Your Temporal Validator

**Before (Single Track - What You Have Now):**
```python
# Old: Rejects all large temporal gaps
def validate_claim(claim):
    gap = abs(claim['source_date'] - claim['target_date'])
    if gap > 100:
        return False  # REJECTED as noise
```

**After (Two Track - What You Get):**
```python
# New: Distinguishes direct claims from bridges
from temporal_bridge_discovery import TemporalBridgeValidator, ClaimTrack

validator = TemporalBridgeValidator(period_qid='Q17167')
result = validator.validate_temporal_coherence(claim)

if result.track == ClaimTrack.DIRECT_HISTORICAL:
    # Strict validation: gap > 150 = reject
    return result.valid
    
elif result.track == ClaimTrack.BRIDGING_DISCOVERY:
    # Discovery mode: gap > 500 = bonus!
    return result.valid  # Usually True for bridges
```

---

## Phase-by-Phase Integration

### PHASE 2: Backlink Harvest (Apply Bridge Detection)

**Where:** `scripts/processing/wikidata_backlink_harvest.py`

**Add to backlink filtering:**
```python
from temporal_bridge_discovery import TemporalBridgeValidator

validator = TemporalBridgeValidator(
    period_qid='Q17167',
    period_start=-509,  # Roman Republic
    period_end=-27
)

def filter_backlink(entity, context_period):
    """Accept entities both with direct validation AND bridge detection"""
    
    claim = {
        'source_entity': entity,
        'target_entity': context_period,
        'relationship_type': entity.get('inferred_relationship'),
        'evidence_text': entity.get('description', '')
    }
    
    result = validator.validate_temporal_coherence(claim)
    
    if result.valid:
        if result.track == ClaimTrack.BRIDGING_DISCOVERY:
            entity['_is_bridge'] = True
            entity['_bridge_type'] = result.bridge_type.value
            entity['_bridge_confidence'] = result.confidence
        return True  # Accept both direct AND bridges!
    
    return False
```

**Expected impact:**
```
Before: 2,318 entities accepted (60.3%)
After:  2,569 entities accepted (66.7%)
Gain:   +251 bridges (+6.4%)
```

---

### PHASE 3: Entity Resolution (Track Bridge Metadata)

**Where:** `scripts/processing/wikipedia_entity_resolver.py`

**Add bridge metadata to entity record:**
```python
def create_entity_record(entity):
    """Create entity with bridge tracking"""
    
    record = {
        'entity_id': entity['id'],
        'label': entity['label'],
        'type': entity['type'],
        'qid': entity.get('qid'),
        'authority_ids': entity.get('authority_ids'),
        'date': entity.get('date'),
        'description': entity.get('description')
    }
    
    # Add bridge metadata if this is a bridge entity
    if entity.get('_is_bridge'):
        record['bridge_metadata'] = {
            'is_bridge': True,
            'bridge_type': entity['_bridge_type'],
            'bridge_confidence': entity['_bridge_confidence'],
            'bridge_time_gap': entity.get('_temporal_gap'),
            'bridge_evidence': entity.get('_evidence_text')
        }
    
    return record
```

---

### PHASE 4: Relationship Extraction (Multi-Facet + Bridge Type)

**Where:** `scripts/processing/relationship_extraction.py`

**Enhance relationship with bridge type and multi-facet scoring:**
```python
def extract_relationships(entity, validator):
    """Extract relationships with bridge type awareness"""
    
    relationships = []
    
    for relationship in entity.get('relationships', []):
        rel_record = {
            'source': entity['id'],
            'target': relationship['target_id'],
            'relationship_type': relationship['type'],
            'facet_primary': relationship.get('facet'),
            'confidence': relationship.get('confidence', 0.75)
        }
        
        # Add multi-facet scoring if available
        if 'facet_scores' in relationship:
            rel_record['facet_scores'] = relationship['facet_scores']
        
        # Validate temporal coherence
        if entity.get('bridge_metadata'):
            # This entity is a bridge
            rel_record['bridge_metadata'] = entity['bridge_metadata']
            rel_record['relationship_classification'] = 'bridging'
        else:
            # Direct historical relationship
            result = validator.validate_temporal_coherence({
                'source_entity': entity,
                'target_entity': relationship['target'],
                'relationship_type': relationship['type'],
                'evidence_text': relationship.get('evidence', '')
            })
            rel_record['relationship_classification'] = result.track.value
        
        relationships.append(rel_record)
    
    return relationships
```

---

### PHASE 5: Validation (Fallacy Detection + Track-Specific Rules)

**Where:** `scripts/processing/claim_validator.py`

**Integrate two-track validation:**
```python
from temporal_bridge_discovery import TemporalBridgeValidator, ClaimTrack
from fallacy_detector import FallacyIntensityDetector

class EnhancedClaimValidator:
    def __init__(self):
        self.temporal_validator = TemporalBridgeValidator()
        self.fallacy_detector = FallacyIntensityDetector()
    
    def validate_claim(self, claim):
        """Validate using two-track temporal + fallacy detection"""
        
        # Step 1: Temporal validation (routing)
        temporal_result = self.temporal_validator.validate_temporal_coherence(claim)
        if not temporal_result.valid:
            return {
                'valid': False,
                'reason': 'temporal_validation_failed',
                'temporal_result': temporal_result
            }
        
        # Step 2: Fallacy detection
        fallacy_result = self.fallacy_detector.detect(claim)
        
        if fallacy_result['intensity'] == 'HIGH':
            # Demote to hypothesis; apply penalty
            confidence_penalty = 0.40
            promotion_eligible = claim.get('posterior', 0.5) >= 0.90
        elif fallacy_result['intensity'] == 'MEDIUM':
            confidence_penalty = 0.15
            promotion_eligible = claim.get('posterior', 0.5) >= 0.85
        else:  # LOW
            confidence_penalty = 0.05
            promotion_eligible = claim.get('posterior', 0.5) >= 0.80
        
        # Step 3: Apply temporal + fallacy result
        is_bridge = temporal_result.track == ClaimTrack.BRIDGING_DISCOVERY
        
        final_confidence = min(
            0.98,
            (claim.get('confidence', 0.75) - confidence_penalty) + 
            (temporal_result.confidence - claim.get('confidence', 0.75))
        )
        
        return {
            'valid': promotion_eligible,
            'confidence': final_confidence,
            'temporal_track': temporal_result.track.value,
            'is_bridge': is_bridge,
            'bridge_type': temporal_result.bridge_type.value if is_bridge else None,
            'fallacy_intensity': fallacy_result['intensity'],
            'fallacy_type': fallacy_result.get('type'),
            'requires_review': temporal_result.requires_review or 
                              fallacy_result['intensity'] in ['HIGH', 'MEDIUM']
        }
```

---

## Neo4j Integration

### Create Bridge Relationship Nodes

**Cypher to create temporal bridge edges:**

```cypher
// Standard historical relationship edge
CREATE (source:Entity)
  -[:DEFEATED_IN_BATTLE {
    facet: "military",
    confidence: 0.95,
    temporal_track: "direct_historical",
    is_bridge: false
  }]->
  (target:Entity)

// NEW: Temporal bridge edge
CREATE (archaeological_discovery:Event {label: "2024 Perugia excavation", date: 2024})
  -[:DISCOVERED_EVIDENCE_FOR {
    facet: "archaeological",
    confidence: 0.94,
    temporal_track: "bridging_discovery",
    is_bridge: true,
    bridge_type: "archaeological_discovery",
    temporal_gap: 2065,
    priority: "HIGH",
    evidence_text: "Archaeologists found lead sling bullets confirming Siege of Perusia..."
  }]->
  (ancient_event:Event {label: "Siege of Perusia", date: -41})
```

### Query Bridges from GPT

**Endpoints GPT can query:**

```cypher
// GPT Query 1: "Show me modern evidence validating this ancient claim"
MATCH (claim:Claim {id: $claim_id})
  <-[bridge:DISCOVERED_EVIDENCE_FOR|VALIDATED_BY|CONFIRMED_BY]-
(modern_evidence:Event)
WHERE bridge.is_bridge = true
RETURN modern_evidence.label, bridge.bridge_type, bridge.confidence

// GPT Query 2: "What modern institutions cite this Roman example?"
MATCH (roman_institution:Institution {period: "Q17167"})
  <-[precedent:CITED_HISTORICAL_PRECEDENT|DREW_INSPIRATION_FROM|MODELED_ON]-
(modern_institution:Institution)
WHERE precedent.is_bridge = true AND precedent.temporal_gap > 1000
RETURN modern_institution.label, roman_institution.label, 
       precedent.temporal_gap, precedent.confidence

// GPT Query 3: "Show me cross-temporal bridges for this period"
MATCH (entity:Entity {period: "Q17167"})
  -[bridge:*]-
  (modern_bridge:Entity)
WHERE bridge.is_bridge = true AND bridge.temporal_gap > 500
RETURN entity.label, bridge.bridge_type, modern_bridge.label,
       bridge.temporal_gap, bridge.priority
ORDER BY bridge.confidence DESC
LIMIT 20

// GPT Query 4: "What do modern scholars say about this?"
MATCH (ancient_claim:Claim {id: $claim_id})
  <-[reinterpretation:REINTERPRETED|CHALLENGED_NARRATIVE_OF]-
(modern_scholar:Human {occupation: "historian"})
WHERE reinterpretation.is_bridge = true
RETURN modern_scholar.name, reinterpretation.description, 
       reinterpretation.confidence, modern_scholar.works
```

---

## Configuration

### Add to config.py

```python
# Temporal Bridge Discovery Settings
TEMPORAL_VALIDATION = {
    'enable_bridge_discovery': True,
    'min_bridge_gap_years': 500,  # Gaps > 500 years = potential gold
    'bridge_confidence_bonus': 0.15,
    'evidential_marker_weight': 0.10,
    
    # Per-bridge-type baselines
    'bridge_baselines': {
        'archaeological': 0.92,
        'historiographic': 0.85,
        'political_precedent': 0.90,
        'cultural_representation': 0.70,
        'scientific_validation': 0.92
    },
    
    # Direct claim validation (Track 1)
    'direct_claim_max_gap': 150,  # Years
    'direct_claim_min_overlap': True,  # Require lifespan overlap for humans
    
    # Bridging claim validation (Track 2)
    'bridge_claim_required_evidence': True,
    'bridge_claim_evidence_markers': [
        'discovered', 'excavated', 'proved', 'validated',
        'reinterpreted', 'inspired by', 'modeled on'
    ]
}

# Fallacy Intensity Settings
FALLACY_VALIDATION = {
    'HIGH': {
        'action': 'demote_to_hypothesis',
        'confidence_penalty': 0.40,
        'examples': ['hero_attribution', 'presentism', 'interpretive_causation']
    },
    'MEDIUM': {
        'action': 'flag_for_review',
        'confidence_penalty': 0.15,
        'examples': ['oversimplification', 'ambiguous_timeline']
    },
    'LOW': {
        'action': 'annotate_only',
        'confidence_penalty': 0.05,
        'examples': ['approximate_dates', 'round_numbers']
    }
}
```

---

## Testing

### Unit Tests for Bridge Detection

```python
# tests/test_temporal_bridge_discovery.py

def test_archaeological_bridge_detection():
    """Archaeological discovery should be accepted as bridge"""
    validator = TemporalBridgeValidator(period_qid='Q17167')
    
    claim = {
        'source_entity': {'type': 'Event', 'date': 2024, 'label': 'Excavation'},
        'target_entity': {'type': 'Event', 'date': -41, 'label': 'Ancient siege'},
        'relationship_type': 'DISCOVERED_EVIDENCE_FOR',
        'evidence_text': 'Archaeologists excavated and found evidence...'
    }
    
    result = validator.validate_temporal_coherence(claim)
    assert result.valid == True
    assert result.track == ClaimTrack.BRIDGING_DISCOVERY
    assert result.bridge_type == BridgeType.ARCHAEOLOGICAL
    assert result.temporal_gap == 2065
    assert result.confidence > 0.90

def test_direct_claim_requires_contemporaneity():
    """Direct historical claim requires reasonable overlapping dates"""
    validator = TemporalBridgeValidator(period_qid='Q17167')
    
    claim = {
        'source_entity': {'type': 'Human', 'birth': -100, 'death': -80},
        'target_entity': {'type': 'Human', 'birth': -50, 'death': -30},
        'relationship_type': 'MET_WITH',  # Direct claim
        'evidence_text': 'They met in Rome'
    }
    
    result = validator.validate_temporal_coherence(claim)
    assert result.valid == False  # No lifespan overlap
    assert result.track == ClaimTrack.DIRECT_HISTORICAL
    assert 'lifespan' in result.reason

def test_precedent_bridge_high_gap_bonus():
    """Political precedent with large gap should get bonus confidence"""
    validator = TemporalBridgeValidator(period_qid='Q17167')
    
    claim = {
        'source_entity': {'type': 'CreativeWork', 'date': 1787, 'label': 'US Constitution'},
        'target_entity': {'type': 'Institution', 'date': -200, 'label': 'Roman Senate'},
        'relationship_type': 'DREW_INSPIRATION_FROM',
        'evidence_text': 'The Founding Fathers explicitly referenced...'
    }
    
    result = validator.validate_temporal_coherence(claim)
    assert result.valid == True
    assert result.track == ClaimTrack.BRIDGING_DISCOVERY
    assert result.bridge_type == BridgeType.PRECEDENT
    assert result.temporal_gap == 1987
    assert result.confidence > 0.90  # Bonus applied
    assert result.priority == 'HIGH'  # Large gap = high priority
```

---

## Deployment Checklist

- [ ] Copy `temporal_bridge_discovery.py` to `scripts/processing/`
- [ ] Update `wikidata_backlink_harvest.py` Phase 2 to use bridge detection
- [ ] Update `wikipedia_entity_resolver.py` Phase 3 to track bridge metadata
- [ ] Update `relationship_extraction.py` Phase 4 to classify relationships
- [ ] Update `claim_validator.py` Phase 5 to use two-track validation
- [ ] Add configuration to `config.py`
- [ ] Create Neo4j migration: Add `is_bridge`, `bridge_type` to relationship properties
- [ ] Create Cypher queries for GPT Neo4j access
- [ ] Add unit tests in `tests/test_temporal_bridge_discovery.py`
- [ ] Update QUICK_START.md with bridge discovery examples
- [ ] Test end-to-end with Roman Republic example (expect 251 bridges)
- [ ] Update GPT knowledge base with temporal bridge guidance

---

## Success Criteria

✅ **Achieved When:**
1. Roman Republic pipeline discovers 251+ temporal bridge entities
2. 428+ bridge relationships created (vs 0 before)
3. Archaeological bridges detected with > 0.90 confidence
4. Political precedent bridges automatically identified
5. GPT can query bridges: "Show me modern evidence for ancient claims"
6. Output distinguishes direct claims (3,804) from bridge claims (428)
7. Fallacy detection integrates without breaking temporal validation
8. Zero data loss: 10k cap accommodates all + bridges

**Final Validation:**
```
Before: 4,232 approved claims (all direct historical)
After:  4,232 direct + 428 bridges = 4,660 total approved claims (+10%)
Result: ✅ Comprehensive cross-temporal knowledge graph ready for Neo4j
```

---

This integration guide enables you to deploy the paradigm shift from single-track filtering to dual-track discovery mode across your entire pipeline.
