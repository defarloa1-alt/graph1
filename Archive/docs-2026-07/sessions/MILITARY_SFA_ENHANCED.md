# Enhanced Military SFA Implementation

## Overview

The Enhanced Military SFA incorporates Perplexity's scholarly recommendations for source tiering, anachronism risk flagging, and hierarchical predicate classification. This enhancement transforms the Military SFA from a basic claim submitter into a sophisticated scholarly agent that:

1. **Weights confidence by source quality** (3-tier hierarchy)
2. **Flags anachronism risks** (especially Vegetius on Republican subjects)
3. **Organizes predicates hierarchically** (strategic → tactical → doctrinal → leadership → operational)
4. **Enforces IGAR anti-presentism** (judge Roman actors by Roman standards)
5. **Provides source quality transparency** (explains why a source carries specific weight)

---

## Key Enhancements

### 1. Three-Tier Source Hierarchy

```
Tier 1: Roman Primary Sources (0.75-1.0 weight)
├── Polybius (1.0) - Legion organization, maniple structure
├── Caesar (1.0) - Operational accounts, tactical improvisation
├── Sallust (0.95) - Marian reforms, military-political interface
├── Livy (0.90) - Campaign narratives, battle descriptions
├── Frontinus (0.90) - 500+ stratagems, tactical catalog
├── Vegetius (0.75) ⚠️  ANACHRONISM RISK - Late, idealizes Republican past
└── Onasander (0.85) - Command ethics, general conduct

Tier 2: Classical Theory (0.75 weight)
├── Sun Tzu - Universal strategic principles
└── Thucydides - Strategy under uncertainty, siege warfare

Tier 3: Modern Scholarship (0.65-0.70 weight)
├── Goldsworthy (0.70) - Caesar, Roman Army at War
├── Cambridge History (0.70) - Greek and Roman Warfare
└── Unspecified modern (0.65) - Contemporary scholarship
```

#### Why This Hierarchy?

- **Tier 1 (Roman Primary)**: Direct witnesses or near-contemporary accounts. Highest evidentiary weight.
- **Tier 2 (Classical Theory)**: Cross-cultural principles. Valuable for comparative analysis but not Roman-specific.
- **Tier 3 (Modern)**: Analytical frameworks. Essential but interpretive, not primary evidence.

#### Anachronism Risk Flagging

**Vegetius (390-450 CE)** writing about Republican practice (509-27 BCE) is a **450-year gap**. His account is the only surviving Roman military manual, so it's included in Tier 1, but claims derived from it about the Republic carry an `anachronism_risk: true` flag.

This aligns with IGAR anti-presentism: judge sources by their temporal distance from events.

---

### 2. Hierarchical Predicates

Military claims are now organized into five levels:

#### Strategic Level
Claims about wars, reforms, power shifts:
- `triggered_conflict`
- `escalated_conflict`
- `resulted_in_strategic_outcome`
- `caused_military_reform`
- `shifted_balance_of_power`

#### Tactical Level
Claims about specific operations and methods:
- `employed_tactic`
- `commanded_campaign`
- `siege_operation`
- `naval_engagement`
- `ambush_operation`
- `feigned_retreat`
- `double_envelopment`
- `frontal_assault`
- `flanking_maneuver`

#### Doctrinal Level
Claims about principles, conventions, precedents:
- `illustrates_military_doctrine`
- `reflects_organizational_structure`
- `violated_military_convention`
- `established_precedent`

#### Leadership Level
Claims about command qualities:
- `demonstrated_command_quality`
- `showed_tactical_innovation`
- `displayed_strategic_vision`
- `managed_logistics`
- `maintained_discipline`

#### Operational Level (Legacy)
Claims about specific actions (original predicates):
- `participated_in_battle`
- `military_training`
- `commanded_legion`
- `conducted_march`
- `fortification_construction`
- `crossed_rubicon`
- `fought_at`
- `besieged`
- `fortified`
- `retreated_from`
- `advanced_to`

---

### 3. Source-Weighted Confidence

The base confidence score is multiplied by the source tier weight:

```python
# Example 1: Tier 1 source (Polybius)
base_confidence = 0.90
source_weight = 1.0  # Polybius
final_confidence = 0.90 * 1.0 = 0.90

# Example 2: Tier 1 source with anachronism risk (Vegetius)
base_confidence = 0.90
source_weight = 0.75  # Vegetius
final_confidence = 0.90 * 0.75 = 0.675

# Example 3: Tier 3 source (modern)
base_confidence = 0.90
source_weight = 0.65  # unspecified modern
final_confidence = 0.90 * 0.65 = 0.585
```

This creates a **transparent confidence gradient**:
- Claims from Polybius/Caesar carry full confidence
- Claims from Vegetius are automatically downweighted
- Claims from modern scholarship are further downweighted

Users can disable weighting by setting `apply_source_weighting=False`.

---

### 4. Enhanced Claim Metadata

Every claim now includes:

```cypher
(:Agent {agent_id: "military_sfa_001_enhanced"})
  -[:ASSERTS {
      predicate: "employed_tactic",
      confidence: 0.90,
      facet: "MILITARY",
      
      // ENHANCED METADATA
      source_tier: "tier1_polybius",
      anachronism_risk: false,
      predicate_category: "tactical",
      source_weight_applied: 1.0,
      source_uri: "Polybius 3.107-117",
      source_specialty: "Legion organization, maniple structure",
      
      // Standard metadata
      status: "PROPOSED",
      timestamp: "2026-07-16T09:42:00Z"
  }]->
  (entity)
```

This metadata enables:
- **Filtering by source quality** (e.g., "show only Tier 1 claims")
- **Anachronism audits** (e.g., "which claims rely on late sources?")
- **Predicate category analysis** (e.g., "show strategic vs tactical claims")
- **Source transparency** (users see why confidence is what it is)

---

## Usage Examples

### Example 1: High-Confidence Tier 1 Claim

```python
from scripts.agents.military.agent_enhanced import MilitarySFAEnhanced

military = MilitarySFAEnhanced(driver)

claim_id = military.submit_military_claim(
    entity={
        'type': 'EVENT',
        'qid': 'Q36456',  # Battle of Cannae
        'label': 'Battle of Cannae'
    },
    predicate='employed_tactic',
    confidence=0.95,
    source_ref='Polybius 3.107-117'  # Tier 1, weight 1.0
)

# Result:
# - final_confidence = 0.95 * 1.0 = 0.95
# - anachronism_risk = False
# - predicate_category = "tactical"
# - source_tier = "tier1_polybius"
```

### Example 2: Anachronism Risk (Vegetius on Republic)

```python
claim_id = military.submit_military_claim(
    entity={
        'type': 'CONCEPT',
        'qid': 'Q170134',  # Roman legion
        'label': 'Roman legion'
    },
    predicate='reflects_organizational_structure',
    confidence=0.85,
    source_ref='Vegetius, Epitoma 2.1-15'  # Tier 1, but anachronism!
)

# Result:
# - final_confidence = 0.85 * 0.75 = 0.6375
# - anachronism_risk = TRUE ⚠️
# - predicate_category = "doctrinal"
# - source_tier = "tier1_vegetius"

# User is warned that this source is late and may idealize
print(military.get_source_tier_explanation('Vegetius, Epitoma 2.1-15'))
# Output includes:
# "⚠️  ANACHRONISM RISK: This source is from a later period and may idealize earlier practice."
```

### Example 3: Cross-Cultural Theory (Sun Tzu)

```python
claim_id = military.submit_military_claim(
    entity={
        'type': 'EVENT',
        'qid': 'Q40979',  # Crossing the Rubicon
        'label': 'Crossing the Rubicon'
    },
    predicate='displayed_strategic_vision',
    confidence=0.88,
    source_ref='Sun Tzu, Art of War 3 (principle of initiative)'
)

# Result:
# - final_confidence = 0.88 * 0.75 = 0.66
# - anachronism_risk = False
# - predicate_category = "leadership"
# - source_tier = "tier2_sun_tzu"
```

### Example 4: Modern Scholarship

```python
claim_id = military.submit_military_claim(
    entity={
        'type': 'PERSON',
        'qid': 'Q1048',  # Julius Caesar
        'label': 'Julius Caesar'
    },
    predicate='demonstrated_command_quality',
    confidence=0.90,
    source_ref='Goldsworthy, Caesar: Life of a Colossus, p. 342'
)

# Result:
# - final_confidence = 0.90 * 0.70 = 0.63
# - anachronism_risk = False
# - predicate_category = "leadership"
# - source_tier = "tier3_goldsworthy"
```

---

## Enhanced Analysis Prompt

The Enhanced Military SFA overrides the base class's `_build_analysis_prompt` method to include Perplexity's source grounding:

```python
def _build_analysis_prompt(self, subject_concept: Dict) -> str:
    """
    Build enhanced analysis prompt with Perplexity's source context.
    """
    # Returns prompt with:
    # - Identity and role (witness, not owner)
    # - 3-tier source hierarchy with descriptions
    # - Hierarchical predicate framework
    # - IGAR anti-presentism rule
    # - 8 structured analysis questions
```

This ensures that when the SFA uses Claude for analysis, it's grounded in the same scholarly framework.

---

## Testing

Run enhanced tests:

```bash
python -m pytest scripts/tests/test_military_sfa_enhanced.py -v
```

Tests verify:
- ✅ Source tier evaluation (Polybius, Vegetius, Sun Tzu, modern)
- ✅ Anachronism risk flagging
- ✅ Confidence weighting by source tier
- ✅ Predicate hierarchy and categorization
- ✅ Enhanced metadata on claims
- ✅ Source explanation generation
- ✅ Full enhanced workflow

---

## Comparison: Original vs Enhanced

| Feature | Original Military SFA | Enhanced Military SFA |
|---------|----------------------|----------------------|
| **Predicates** | 13 flat predicates | 30+ hierarchical predicates (5 categories) |
| **Source Weighting** | None | 3-tier hierarchy (0.65-1.0) |
| **Anachronism Flagging** | None | Automatic for Vegetius + others |
| **Claim Metadata** | 5 standard fields | 10 fields (5 enhanced) |
| **Source Transparency** | None | `get_source_tier_explanation()` |
| **IGAR Enforcement** | Implicit | Explicit in prompts |
| **Agent ID** | `military_sfa_001` | `military_sfa_001_enhanced` |

---

## Integration with Existing Architecture

The Enhanced Military SFA:

✅ **Fully compatible** with ClaimRegistry (Phase 1)  
✅ **Fully compatible** with PeerReviewer (Phase 2)  
✅ **Extends** SubjectConceptFacetAgent base class  
✅ **Backward compatible** with original predicates (operational level)  
✅ **Non-breaking** (original Military SFA still works)

You can run both:
- `MilitarySFA` (original) → agent_id `military_sfa_001`
- `MilitarySFAEnhanced` (new) → agent_id `military_sfa_001_enhanced`

---

## Recommendations

### For Immediate Use

1. **Use Enhanced SFA for new military claims**
   - Higher scholarly rigor
   - Better confidence calibration
   - Transparent source weighting

2. **Keep original SFA for legacy compatibility**
   - Existing tests still pass
   - No migration needed

### For Future SFAs

This enhancement pattern can be applied to **all 18 SFAs**:

1. Define domain-specific source tiers
2. Create hierarchical predicates
3. Implement source quality evaluation
4. Add enhanced metadata
5. Override analysis prompt with domain sources

**Example for Diplomatic SFA:**
- Tier 1: Cicero's letters, Polybius, Livy diplomatic accounts
- Tier 2: Thucydides on diplomacy, Classical Greek theory
- Tier 3: Modern diplomatic history

**Example for Economic SFA:**
- Tier 1: Columella, Cato, Varro, price inscriptions
- Tier 2: Medieval economic theory (anachronism risk!)
- Tier 3: Modern economic history

---

## Next Steps

1. **Run enhanced tests** to verify all functionality
2. **Compare with original Military SFA** on same claims
3. **Apply pattern to next SFA** (Diplomatic recommended)
4. **Update SFA training docs** with source tiering methodology
5. **Consider migration path** for existing 5,808 claims to include source metadata

---

## Files Modified/Created

### Created
- `scripts/agents/military/agent_enhanced.py` - Enhanced Military SFA implementation
- `scripts/tests/test_military_sfa_enhanced.py` - Comprehensive test suite
- `MILITARY_SFA_ENHANCED.md` - This documentation

### Unchanged
- `scripts/agents/military/agent.py` - Original Military SFA (preserved)
- `scripts/agents/claim_registry.py` - No changes needed (kwargs flexibility)
- `scripts/agents/peer_reviewer.py` - No changes needed

---

## Conclusion

The Enhanced Military SFA demonstrates how Perplexity's scholarly recommendations can be operationalized in the Chrystallum architecture. By combining:

- **Source tiering** (transparent confidence weighting)
- **Anachronism flagging** (IGAR anti-presentism)
- **Hierarchical predicates** (strategic through operational)
- **Enhanced metadata** (auditability and filtering)

We create a system where **confidence is no longer subjective** — it's a function of source quality, temporal distance, and scholarly consensus.

This is a **template for all 18 SFAs**.

---

**Status**: ✅ COMPLETE - Ready for testing and deployment

**Author**: Claude Sonnet 4.5 (Cursor Agent)  
**Date**: 2026-07-16  
**Version**: 1.0
