# Military Subject Facet Agent (Military SFA)

**Facet**: MILITARY  
**Status**: Registry-backed training (FACET_TRAINING_CONTRACT)  
**Agent ID**: `SFA_sc_q17167_military_wars_campaigns_MILITARY`

**Binding rules:** `docs/FACET_TRAINING_CONTRACT.md`

---

## Overview

The Military SFA analyzes SubjectConcepts from a military perspective using **only** relationship types from `relationship_types_registry_master.csv` (`lifecycle_status=implemented`).

Do **not** use `agent_enhanced.py` for writes — theory discovery / snake_case predicates are disabled.

## Source directories (not ingested corpus)

Bookmark lists for training research (passages must still be cited into claims):

- [`corpus/MILITARY_RESOURCES.md`](corpus/MILITARY_RESOURCES.md)
- [`corpus/NAVAL_RESOURCES.md`](corpus/NAVAL_RESOURCES.md)
- [`corpus/ROMAN_REPUBLIC_FEDERATION_SYNTHESIS.md`](corpus/ROMAN_REPUBLIC_FEDERATION_SYNTHESIS.md)

Event location geo: `python scripts/system/ensure_event_place_geo.py --event-qid <QID>`

---

## Training pilot (Claims track)

```powershell
python -m scripts.agents.military.training_pilot --dry-run
python -m scripts.agents.military.training_pilot --write
```

Creates staged `Claim` + `ProposedEdge` with registry type `FOUGHT_IN`, scoped to `sc_q17167_military_wars_campaigns`.

---

## Usage

### Initialize

```python
from scripts.agents.military.agent import MilitarySFA, create_military_sfa

military_sfa = create_military_sfa(uri, user, password)
```

### Submit Military Claims (ASSERTS path)

```python
cipher = military_sfa.submit_military_claim(
    entity={'type': 'PERSON', 'qid': 'Q315274', 'label': 'C. Terentius Varro'},
    relationship_type='FOUGHT_IN',  # registry type — not snake_case gloss
    confidence=0.88,
    source_qid='Q179591',
)
```

### Review Peer Claims

```python
# Review claims from other facets
reviews = military_sfa.review_peer_claims(
    entity_cipher='ent_per_Q1048'
)

for review in reviews:
    print(f"{review['reviewed_facet']} claim: {review['agrees']}")
```

### Analyze Military Context

```python
# Analyze entity from military perspective
result = military_sfa.analyze_military_context(
    entity_qid='Q1048',
    submit_claims=True
)

print(f"Military significance: {result['analysis']['significance']}")
print(f"Claims submitted: {len(result['claims_submitted'])}")
```

---

## Military-Specific Evaluation Logic

The Military SFA applies specialized evaluation when reviewing peer claims:

### High Trust (Agrees)
- High-confidence claims about military predicates (e.g., `commanded_legion`, `fought_at`)
- Geographic claims about battle locations (confidence ≥ 0.80)
- Temporal claims about conflict dates

### Moderate Trust
- Medium-confidence claims about military actions (0.70-0.85)
- Cross-facet claims with military relevance

### Low Trust (Questions)
- Vague or uncertain military actions
- Inconsistent geographic/temporal data
- Low-confidence claims (< 0.70)

**Example Evaluation**:
```python
# Claim from Political SFA: "Caesar crossed Rubicon in -49"
# Confidence: 0.90

# Military SFA evaluation:
{
    'agrees': True,
    'confidence': 0.95,
    'note': 'Military facet: High-confidence claim about crossed_rubicon'
}
```

---

## Military Predicates

Specialized military predicates:

```python
MILITARY_PREDICATES = [
    "crossed_rubicon",
    "commanded_legion",
    "fought_at",
    "besieged",
    "fortified",
    "retreated_from",
    "advanced_to",
    "naval_battle",
    "land_battle",
    "military_alliance",
    "military_opposition",
    "supplied_forces",
    "recruited_troops",
]
```

---

## Wikidata Integration

Military-specific Wikidata properties:

| Property | Label | Description |
|----------|-------|-------------|
| P607 | conflict | Conflict entity participated in |
| P361 | part_of | Part of campaign/war |
| P710 | participant | Participant in event |
| P276 | location | Location of battle |
| P585 | point_in_time | When battle occurred |
| P1344 | participant_in | Participant in |
| P828 | has_cause | Cause of conflict |
| P1120 | number_of_deaths | Casualties |

---

## Testing

Run tests:

```bash
python -m pytest scripts/tests/test_military_sfa.py -v
```

**Test Coverage**:
- Basic SFA initialization
- Claim submission via ClaimRegistry
- Facet assignment verification
- Peer review workflow
- Military-specific evaluation logic
- Full integration workflow

---

## Integration with Other Facets

The Military SFA collaborates with:

**POLITICAL Facet**:
- Political outcomes of battles
- Military appointments
- War declarations

**GEOGRAPHIC Facet**:
- Battle locations
- Strategic terrain
- Fortification sites

**ECONOMIC Facet**:
- Military logistics
- Supply chains
- War financing

**BIOGRAPHIC Facet**:
- Military careers
- Command appointments
- Battle participation

---

## Example: Caesar's Military Context

```python
# Analyze Julius Caesar from military perspective
result = military_sfa.analyze_military_context(
    entity_qid='Q1048',
    submit_claims=True
)

# Result:
{
    'entity_qid': 'Q1048',
    'facet': 'MILITARY',
    'claims_submitted': [
        {
            'cipher': 'ent_per_Q1048',
            'predicate': 'commanded_legion',
            'confidence': 0.95
        },
        {
            'cipher': 'ent_evt_Q40979',
            'predicate': 'fought_at',
            'confidence': 0.90
        }
    ],
    'analysis': {
        'significance': 'high',
        'claim_count': 2,
        'has_military_context': True,
        'evaluation': 'Major military figure/event'
    }
}
```

---

## Architecture

```
MilitarySFA
    ↓
    ├─ ClaimRegistry (Phase 1: Submit claims)
    │   └─ Creates: (Agent)-[:ASSERTS {facet:'MILITARY'}]->(Entity)
    │
    └─ PeerReviewer (Phase 2: Review claims)
        └─ Creates: (Agent)-[:REVIEWED {agrees:bool}]->(Entity)
```

---

## Files

- `agent.py` - Main Military SFA implementation
- `README.md` - This documentation
- `../tests/test_military_sfa.py` - Test suite

---

## Next Steps

1. **Wikidata Integration**: Connect to live Wikidata API
2. **Advanced Evaluation**: ML-based confidence scoring
3. **IGAR Integration**: Military decision modeling
4. **Temporal Validation**: Check date consistency
5. **Geographic Validation**: Verify location plausibility

---

## See Also

- [Phase 2 Completion Summary](../../../PHASE_2_COMPLETION_SUMMARY.md)
- [ClaimRegistry](../claim_registry.py)
- [PeerReviewer](../peer_reviewer.py)
- [SFA Status Summary](../../../SFA_STATUS_SUMMARY.md)
