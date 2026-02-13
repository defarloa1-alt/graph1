# Fact Validation and Scoring: Lessons from India Cotton Trade Validation

## Overview

The validation exercise on the India cotton trade text revealed critical insights about how Chrystallum should validate, score, and handle facts before and after they enter the knowledge graph.

---

## Key Lessons Learned

### 1. **Source Attribution Alone Is Not Enough**

**What We Learned:**
- The text cited legitimate sources (Steven Johnson, Strabo, Keay)
- Yet still contained at least one critical factual error (Ajanta Caves date)
- Having sources ≠ claims are automatically accurate

**Implications for Chrystallum:**
- ✅ Store source citations with every fact
- ⚠️ **But also**: Implement independent fact-checking mechanisms
- 🔍 Cross-reference claims against multiple authoritative sources
- 📊 Score confidence based on both source quality AND verification

---

### 2. **Ambiguity Requires Interpretation Layers**

**What We Learned:**
- The phrase "too wealthy for X to resist" was initially misinterpreted
- Same words can mean different things in different contexts
- Interpretation requires domain knowledge and historical context

**Implications for Chrystallum:**
- ✅ Store multiple interpretations/meanings where ambiguity exists
- 📝 Capture narrative context, not just structured data
- 🤔 Enable multi-agent debate for ambiguous claims
- 📊 Lower confidence scores for ambiguous statements

---

### 3. **Temporal Facts Need Rigorous Validation**

**What We Learned:**
- The Ajanta Caves date error was ~2000 years off
- Temporal claims are high-stakes (affect entire historical narratives)
- Easy to confuse or conflate different time periods

**Implications for Chrystallum:**
- ✅ **Strict validation** for all temporal properties (`start_date`, `end_date`)
- 🔍 Cross-reference temporal claims against multiple sources
- ⚠️ Flag temporal inconsistencies automatically
- 📊 Lower confidence if temporal sources conflict
- 🚫 **Block or flag** claims with impossible temporal relationships

---

### 4. **Confidence Scoring Should Be Multi-Factor**

**What We Learned:**
- Not all facts are created equal
- Source quality matters
- Independent verification matters
- Claim specificity matters
- Historical consensus matters

**Implications for Chrystallum:**

**Confidence Score Components:**
```
confidence = f(
    source_quality,        // Authoritative vs. secondary
    source_count,          // Multiple independent sources
    verification_status,   // Verified vs. unverified
    claim_specificity,     // Vague vs. specific
    temporal_certainty,    // Precise date vs. approximate
    consensus_status,      // Agreed vs. disputed
    logical_consistency    // Fits with other known facts
)
```

**Example Scoring:**
- **High Confidence (0.9-1.0)**: Multiple authoritative sources, independently verified, specific details, logical consistency
- **Medium Confidence (0.6-0.8)**: Single authoritative source, plausible, fits context, some verification
- **Low Confidence (0.3-0.5)**: Secondary source, vague, unverified, may conflict with other facts
- **Very Low (0.0-0.2)**: Single source, contradictory, logically inconsistent, flagged for review

---

### 5. **Flagging and Dispute Mechanisms Are Critical**

**What We Learned:**
- Errors can slip through even with good sources
- Need mechanisms to flag questionable claims
- Need ways to dispute and correct facts

**Implications for Chrystallum:**

**Validation Flags:**
- 🚩 **Temporal Inconsistency**: Dates don't align with known facts
- 🚩 **Logical Inconsistency**: Claim contradicts established facts
- 🚩 **Single Source**: Only one source, needs verification
- 🚩 **Ambiguous**: Multiple interpretations possible
- 🚩 **Unverified**: No independent confirmation
- 🚩 **Disputed**: Multiple agents/sources disagree

**Dispute Resolution:**
- Multi-agent debate for conflicting claims
- Source hierarchy (primary > secondary > tertiary)
- Consensus building through agent negotiation
- Human-in-the-loop for high-stakes claims

---

### 6. **Context and Narrative Are Essential**

**What We Learned:**
- The "narrative_summary" helped clarify ambiguous claims
- Context reveals meaning that structured data alone cannot capture
- Historical context matters for interpretation

**Implications for Chrystallum:**
- ✅ **Always store narrative summaries** alongside structured facts
- 📝 Capture full context, not just triples
- 🔗 Link facts to broader narratives/events
- 📚 Store interpretation guidelines with ambiguous entities

---

### 7. **Validation Should Happen at Multiple Stages**

**What We Learned:**
- Errors can enter at extraction stage
- Errors can propagate if not caught early
- Need validation at multiple checkpoints

**Implications for Chrystallum:**

**Validation Stages:**

1. **Pre-Extraction Validation**
   - Validate source credibility
   - Check source date vs. claim date (can't cite future sources for past events)
   - Flag potential issues before LLM extraction

2. **Extraction Validation**
   - Validate against schema (entity types, relationship types)
   - Check temporal logic (end_date > start_date)
   - Verify QID mappings exist in Wikidata
   - Check against existing graph facts

3. **Post-Extraction Validation**
   - Cross-reference with existing entities
   - Check for duplicates
   - Verify logical consistency
   - Flag conflicts with established facts

4. **Ongoing Validation**
   - Periodic fact-checking
   - Re-validate when new sources appear
   - Update confidence scores based on new evidence
   - Flag for review if new information contradicts

---

### 8. **Source Hierarchy and Quality Metrics**

**What We Learned:**
- Steven Johnson (popular science writer) ≠ Keay (professional historian)
- Strabo (primary source, ancient) vs. modern historians (secondary sources)
- Different source types have different reliability

**Implications for Chrystallum:**

**Source Quality Tiers:**
- **Tier 1**: Primary sources (contemporary documents, archaeological evidence)
- **Tier 2**: Authoritative secondary sources (professional historians, peer-reviewed)
- **Tier 3**: Popular/tertiary sources (popular books, general references)
- **Tier 4**: Unverified/unknown sources

**Source Metadata to Store:**
- Source type (primary/secondary/tertiary)
- Author credentials/expertise
- Publication date
- Peer review status
- Citation count (if applicable)
- Consensus status (widely accepted vs. disputed)

---

## Recommended Confidence Scoring System

### Confidence Score Formula

```python
def calculate_confidence(entity_or_relationship):
    """
    Multi-factor confidence scoring based on validation exercise lessons.
    """
    
    base_confidence = 0.5  # Neutral starting point
    
    # Source quality factor (0.0 - 0.3)
    source_factor = {
        'primary_source': 0.3,
        'authoritative_secondary': 0.25,
        'peer_reviewed': 0.2,
        'professional_historian': 0.15,
        'popular_source': 0.1,
        'unknown': 0.0
    }[source_quality]
    
    # Source count factor (0.0 - 0.2)
    source_count_factor = min(0.2, (source_count - 1) * 0.05)
    # +0.05 for each additional independent source, max +0.2
    
    # Verification factor (0.0 - 0.2)
    verification_factor = {
        'independently_verified': 0.2,
        'cross_referenced': 0.15,
        'single_source': 0.05,
        'unverified': 0.0
    }[verification_status]
    
    # Specificity factor (0.0 - 0.1)
    specificity_factor = {
        'highly_specific': 0.1,  # Exact dates, precise details
        'specific': 0.07,
        'general': 0.04,
        'vague': 0.0
    }[claim_specificity]
    
    # Temporal certainty factor (0.0 - 0.1)
    temporal_factor = {
        'exact_date': 0.1,
        'approximate_date': 0.06,
        'period_only': 0.03,
        'uncertain': 0.0
    }[temporal_certainty]
    
    # Consistency factor (0.0 - 0.1)
    consistency_factor = {
        'fully_consistent': 0.1,
        'mostly_consistent': 0.06,
        'minor_conflicts': 0.02,
        'major_conflicts': -0.2  # Penalty for conflicts
    }[logical_consistency]
    
    # Calculate final confidence
    confidence = base_confidence + source_factor + source_count_factor + \
                 verification_factor + specificity_factor + temporal_factor + \
                 consistency_factor
    
    # Apply penalties for flags
    if has_flag('temporal_inconsistency'):
        confidence -= 0.3
    if has_flag('logical_inconsistency'):
        confidence -= 0.3
    if has_flag('single_source_unverified'):
        confidence -= 0.2
    if has_flag('disputed'):
        confidence -= 0.15
    
    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, confidence))
```

### Confidence Score Interpretation

| Score Range | Interpretation | Action |
|-------------|----------------|--------|
| 0.9 - 1.0 | **Highly Reliable** | Accept, can be used in reasoning |
| 0.7 - 0.89 | **Reliable** | Accept with minor verification |
| 0.5 - 0.69 | **Moderately Reliable** | Accept but flag for additional verification |
| 0.3 - 0.49 | **Questionable** | Flag for review, require additional sources |
| 0.0 - 0.29 | **Unreliable** | Reject or mark as disputed, require verification |

---

## Validation Workflow Recommendations

### Agent Fact Validation Workflow

1. **Extract Fact** (LLM extraction)
2. **Initial Validation**
   - Check schema compliance
   - Validate temporal logic
   - Check QID exists (if applicable)
   - Compare to existing facts
3. **Source Attribution**
   - Record source(s)
   - Assign source quality tier
   - Check source date vs. claim date
4. **Confidence Scoring**
   - Calculate multi-factor confidence
   - Apply penalties for flags
5. **Conflict Detection**
   - Check for contradictory facts
   - Flag if conflicts exist
6. **Decision Point**
   - High confidence (>0.7): Accept
   - Medium confidence (0.5-0.7): Accept with flag
   - Low confidence (<0.5): Flag for review or dispute resolution
7. **Dispute Resolution** (if needed)
   - Multi-agent debate
   - Source hierarchy comparison
   - Consensus building
   - Human-in-the-loop for critical decisions

---

## Metadata Schema Enhancements

### Enhanced Entity/Relationship Properties

```cypher
{
  // Existing properties
  confidence: 0.85,
  
  // New validation properties
  validation_status: "verified" | "flagged" | "disputed" | "unverified",
  
  // Source information
  sources: [
    {
      source_id: "...",
      source_type: "primary" | "authoritative_secondary" | "tertiary",
      source_title: "...",
      source_author: "...",
      source_date: "...",
      page_reference: "...",
      citation: "...",
      source_quality_tier: 1-4
    }
  ],
  
  // Verification metadata
  verification_status: "independently_verified" | "cross_referenced" | "single_source" | "unverified",
  verification_date: "...",
  verified_by_agent: "...",
  
  // Flags
  flags: [
    {
      flag_type: "temporal_inconsistency" | "logical_inconsistency" | "single_source" | "ambiguous" | "disputed",
      flag_severity: "critical" | "major" | "minor",
      flag_description: "...",
      flagged_by: "...",
      flagged_date: "..."
    }
  ],
  
  // Dispute information
  dispute_status: "none" | "active" | "resolved",
  dispute_participants: [...],  // Agent IDs involved in dispute
  dispute_resolution: "...",
  
  // Temporal validation
  temporal_certainty: "exact" | "approximate" | "period_only" | "uncertain",
  temporal_validated: true | false,
  
  // Consistency checks
  consistency_status: "fully_consistent" | "mostly_consistent" | "minor_conflicts" | "major_conflicts",
  conflicting_facts: [...],  // IDs of conflicting entities/relationships
}
```

---

## Key Takeaways

1. ✅ **Multi-factor confidence scoring** is essential (not just binary)
2. ✅ **Source attribution alone insufficient** - need independent verification
3. ✅ **Temporal facts need rigorous validation** - high-stakes errors
4. ✅ **Flagging and dispute mechanisms** critical for quality
5. ✅ **Narrative context** helps clarify ambiguous claims
6. ✅ **Validation at multiple stages** prevents error propagation
7. ✅ **Source hierarchy** matters for reliability assessment
8. ✅ **Ambiguity requires interpretation layers** and debate mechanisms

---

## Next Steps

1. **Implement confidence scoring system** in Chrystallum agents
2. **Add validation flags** to entity/relationship schema
3. **Create dispute resolution workflow** for conflicting facts
4. **Build source quality assessment** mechanism
5. **Develop temporal validation** checks
6. **Implement multi-stage validation** pipeline

---

**Status**: Recommendations based on validation exercise  
**Date**: Based on India cotton trade text validation  
**Next**: Implementation in Chrystallum architecture




