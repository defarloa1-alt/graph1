# Confidence Scoring Rubric for Agent Claims

## Purpose

This document defines the confidence scoring framework for agent-generated claims in the Chrystallum knowledge graph. Confidence scores determine:
- Whether to use CRMinf explicit reasoning chains vs. simple Chrystallum properties
- How to resolve conflicts between multiple agent claims
- When to trigger multi-SME debates
- Claim persistence eligibility

---

## Source Quality Tiers

### Tier Definitions

| Tier | Confidence Range | Examples | Notes |
|------|------------------|----------|-------|
| **Primary Source** | 0.85-1.0 | Roman legal documents, inscriptions, coins, contemporary records | Direct evidence, minimal interpretation |
| **Secondary Source (Academic)** | 0.75-0.90 | Peer-reviewed journal, monograph by subject expert | Interpreted by expert, citable |
| **Secondary Source (Populist)** | 0.65-0.75 | Wikipedia articles, general history books | Well-researched but broader audience |
| **Tertiary/Synthesis** | 0.50-0.70 | Textbooks, survey articles, synthesis works | Accurate but at distance from sources |
| **LLM Synthesis (High Consensus)** | 0.70-0.85 | LLM trained on multiple expert sources, no contradictions | Generated knowledge, no primary source risk |
| **LLM Synthesis (Conflicting)** | 0.40-0.60 | LLM trained on contradictory sources, interpretive question | Epistemic uncertainty embedded |
| **Inference/Reconstruction** | 0.30-0.50 | Plausible but not directly sourced (e.g., social structures) | Reasonable inference, could be wrong |
| **Speculation** | 0.10-0.30 | Historian's educated guess, admitted as such | Not suitable for graph without debate |

---

## Confidence Calculation Formula

### Base Confidence

Start with the **midpoint of the source tier range**:

```python
def get_base_confidence(source_tier):
    tier_midpoints = {
        "primary": 0.925,
        "secondary_academic": 0.825,
        "secondary_populist": 0.70,
        "tertiary": 0.60,
        "llm_high_consensus": 0.775,
        "llm_conflicting": 0.50,
        "inference": 0.40,
        "speculation": 0.20
    }
    return tier_midpoints.get(source_tier, 0.50)
```

### Modifiers

Apply these modifiers to base confidence:

| Modifier | Value | Condition |
|----------|-------|-----------|
| Multiple independent sources agree | +0.05 | 3+ sources with same claim |
| Primary source ambiguous | -0.10 | Source admits uncertainty |
| Archaeological evidence supports | +0.10 | Material evidence confirms |
| Historiographical consensus weak | -0.15 | Scholars disagree |
| Source is contemporary | +0.05 | Written during event period |
| Source is later interpretation | -0.05 | Written centuries later |
| Multiple conflicting sources | -0.20 | Sources contradict each other |

### Final Calculation

```python
final_confidence = clamp(base_confidence + sum(modifiers), 0.0, 1.0)
```

---

## Decision Thresholds

### Claim Resolution Rules

| Decision | Threshold | Example |
|----------|-----------|---------|
| **ACCEPT (no debate)** | New ≥ 0.80 AND (Existing = 0 OR New > Existing + 0.15) | New=0.85, Existing=0.65 → REPLACE |
| **ADDITIVE (coexist)** | 0.20 < difference < 0.15 OR both ≥ 0.60 | New=0.70, Existing=0.65 → DEBATE |
| **REJECT** | New < Existing - 0.15 AND Existing ≥ 0.60 | New=0.50, Existing=0.70 → REJECT |
| **ESCALATE TO DEBATE** | Difference < 0.15 AND both ≥ 0.50 AND topics overlap | Both ~0.70 → INVOKE DEBATE |

### CRMinf vs. Chrystallum Decision

Based on `scripts/agents/reasoning_decision.py`:

| Condition | Approach | Reason |
|-----------|----------|--------|
| Confidence ≥ 0.80, single source, no conflicts | Chrystallum | Simple high-confidence fact |
| Confidence < 0.60 | CRMinf | Low confidence requires explicit reasoning |
| Multiple sources, confidence < 0.80 | CRMinf | Uncertainty requires evidence chain |
| Conflicting views exist | CRMinf | Must preserve competing interpretations |
| Explicit reasoning required | CRMinf | User/system requires reasoning chain |

---

## Examples

### Example 1: High Confidence Primary Source

**Claim:** "Julius Caesar was assassinated on March 15, 44 BCE"

**Source:** Suetonius, "Life of Caesar" (primary source, contemporary)

**Calculation:**
- Base: 0.925 (primary source)
- Modifier: +0.05 (multiple sources agree - also in Plutarch, Dio Cassius)
- Final: 0.975

**Decision:** ACCEPT, use Chrystallum (simple property)

---

### Example 2: Medium Confidence with Conflict

**Claim:** "Caesar's height was 5'11\" (183cm)"

**Source:** Suetonius mentions height, but vague

**Calculation:**
- Base: 0.825 (secondary academic - Suetonius interpretation)
- Modifier: -0.10 (primary source ambiguous)
- Modifier: -0.15 (historiographical consensus weak - sources disagree)
- Final: 0.575

**Decision:** Use CRMinf (low confidence, conflicting sources)

---

### Example 3: LLM Synthesis with High Consensus

**Claim:** "The Gracchi Land Reforms began in 133 BCE"

**Source:** LLM trained on multiple academic sources, all agree

**Calculation:**
- Base: 0.775 (LLM high consensus)
- Modifier: +0.05 (multiple sources agree)
- Final: 0.825

**Decision:** ACCEPT, use Chrystallum

---

### Example 4: Conflicting Interpretations

**Claim A (Military Historian):** "Siege of Alesia was militarily decisive" (confidence: 0.88)

**Claim B (Political Historian):** "Siege of Alesia was primarily political consolidation" (confidence: 0.82)

**Analysis:**
- Both ≥ 0.50: ✓
- Difference < 0.15: ✓ (0.06 difference)
- Topics overlap: ✓ (same event, different perspectives)

**Decision:** ESCALATE TO DEBATE, then ADDITIVE (both perspectives valid)

---

## Integration with Existing Code

### Current Implementation

The confidence scoring is already partially implemented in:
- `scripts/agents/reasoning_decision.py` - CRMinf vs Chrystallum decision
- `scripts/agents/crminf_agent_tool.py` - CRMinf structure creation

### Usage in Agents

```python
from scripts.agents.reasoning_decision import should_use_crminf, get_approach_recommendation

# Determine approach based on confidence
confidence = 0.75
source_count = 2
has_conflicts = True

recommendation = get_approach_recommendation(
    confidence=confidence,
    source_count=source_count,
    has_conflicting_views=has_conflicts
)

# Returns: {"approach": "crminf", "reasons": [...], "recommendation": "..."}
```

---

## Best Practices

### For Agent Developers

1. **Always justify confidence scores** - Document source tier and modifiers
2. **Be conservative** - When in doubt, use lower confidence
3. **Consider source quality** - Primary sources > Secondary > Tertiary
4. **Note conflicts** - If sources disagree, lower confidence and flag for debate
5. **Use CRMinf for uncertainty** - Low confidence claims need explicit reasoning chains

### For Multi-Agent Systems

1. **Compare confidence scores** - Use thresholds to determine duplicate/additive/replacement
2. **Trigger debates** - When scores are close and topics overlap
3. **Preserve perspectives** - Don't suppress conflicting interpretations
4. **Record provenance** - Always track which agent made which claim

---

## Related Documents

- `scripts/agents/reasoning_decision.py` - Implementation of CRMinf decision logic
- `scripts/agents/crminf_agent_tool.py` - CRMinf structure creation
- `Agents/Prompts/extraction_agent.txt` - Agent prompt with confidence rules
- `Docs/architecture/CRMinf_Implementation_Guide.md` - CRMinf architecture

---

*Version: 1.0*  
*Last Updated: 2025-12-12*  
*Related: reasoning_decision.py, crminf_agent_tool.py*


