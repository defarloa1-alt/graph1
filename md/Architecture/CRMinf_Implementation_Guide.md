# CRMinf Implementation Guide

## Overview

This guide documents the implementation of CRMinf (CIDOC-CRM Inference Extension) in the Chrystallum knowledge graph, enabling explicit modeling of reasoning chains, beliefs, and evidence.

## Architecture

### Hybrid Approach

Chrystallum uses a **hybrid approach**:
- **Simple facts** (high confidence, clear evidence) → Use Chrystallum properties (`confidence`, `sources`)
- **Complex reasoning** (uncertain, disputed, multiple interpretations) → Use CRMinf explicit chains

### Decision Logic

Use CRMinf when:
- ✅ Confidence < 0.8 with multiple sources
- ✅ Conflicting views exist
- ✅ Explicit reasoning chain required
- ✅ Very low confidence (< 0.6)

Use Chrystallum when:
- ✅ High confidence (≥ 0.9)
- ✅ Single source, clear evidence
- ✅ Simple, uncontested facts

## Schema Components

### Entity Types

**Added to `data/schemas/chrystallum_schema.json`:**

1. **Belief** (`E2_Belief`)
   - Represents beliefs or assumptions about facts
   - Properties: `label`, `type`, `certainty`, `uncertainty`, `cidoc_crm_class`

2. **InferenceMaking** (`E5_Inference_Making`)
   - Represents the process of making inferences
   - Properties: `label`, `type`, `note`, `uncertainty`, `cidoc_crm_class`

3. **BeliefRevision** (`E13_Belief_Revision`)
   - Represents changes to beliefs over time
   - Properties: `label`, `type`, `cidoc_crm_class`

### Relationship Types

**Added to `Relationships/relationship_types_registry_master.csv`:**

1. **I1_INFERRED_FROM** (`crminf:I1_inferred_from`)
   - Links evidence to inference
   - Direction: Evidence → Inference

2. **I2_BELIEVED_TO_HOLD** (`crminf:I2_believed_to_hold`)
   - Links inference/belief to conclusion
   - Direction: Inference → Belief → Fact

3. **I3_HAS_NOTE** (`crminf:I3_has_note`)
   - Notes about inference
   - Direction: Inference → Note (string)

4. **I4_HAS_UNCERTAINTY** (`crminf:I4_has_uncertainty`)
   - Uncertainty quantification
   - Direction: Inference/Belief → Uncertainty

5. **I7_HAS_OBJECT** (`crminf:I7_has_object`)
   - Old belief being revised
   - Direction: Revision → Old Belief

6. **I8_HAS_RESULT** (`crminf:I8_has_result`)
   - New/revised belief
   - Direction: Revision → New Belief

## Implementation Files

### Core Utilities

**`scripts/utils/crminf_utils.py`**
- `CRMinfBuilder` class for creating reasoning chains
- Methods: `create_belief()`, `create_inference()`, `create_reasoning_chain()`

### Agent Integration

**`scripts/agents/crminf_agent_tool.py`**
- `CRMinfAgentTool` for Langraph agents
- `should_use_crminf()` decision logic
- `create_reasoning_for_entity()` method

**`scripts/agents/reasoning_decision.py`**
- Decision logic for CRMinf vs. Chrystallum
- `get_approach_recommendation()` with explanations

### Neo4j Schema

**`cypher/setup/create_crminf_schema.cypher`**
- Indexes for Belief, InferenceMaking, BeliefRevision
- Constraints to ensure correct types

### Query Patterns

**`cypher/queries/crminf_query_patterns.cypher`**
- 10 common query patterns for reasoning chains
- Evidence tracing, conflicting beliefs, belief revisions

## Usage Examples

### Example 1: Simple Fact (Chrystallum)

```python
# High confidence, single source - use Chrystallum
event = {
    "label": "Caesar's Birth",
    "qid": "Q_CAESAR_BIRTH",
    "confidence": 0.95,
    "sources": ["Q_SOURCE1"]
}
# No CRMinf needed - simple property approach
```

### Example 2: Complex Reasoning (CRMinf)

```python
from scripts.agents.crminf_agent_tool import CRMinfAgentTool

tool = CRMinfAgentTool("bolt://localhost:7687", "neo4j", "password")

result = tool.create_reasoning_for_entity(
    entity_label="Crossing of Rubicon",
    entity_qid="Q_CROSSING",
    evidence_sources=["Q_SOURCE1", "Q_SOURCE2"],
    confidence=0.75,
    note="Multiple sources with some disagreement",
    has_conflicting_views=False
)

# Returns:
# {
#     "approach": "crminf",
#     "inference": {...},
#     "belief": {...},
#     "confidence": 0.75,
#     "certainty": "medium",
#     "uncertainty": "medium"
# }
```

### Example 3: Conflicting Views (CRMinf)

```python
result = tool.create_reasoning_for_entity(
    entity_label="Date of Event",
    entity_qid="Q_EVENT",
    evidence_sources=["Q_SOURCE1", "Q_SOURCE2", "Q_SOURCE3"],
    confidence=0.85,
    has_conflicting_views=True,
    note="Scholars disagree on exact date"
)
# Always uses CRMinf when conflicting views exist
```

## Reasoning Chain Structure

### Complete Chain

```
Evidence (Document/Observation)
  ↓ I1_INFERRED_FROM
InferenceMaking (Reasoning Process)
  ↓ I2_BELIEVED_TO_HOLD
Belief (Conclusion)
  ↓ I2_BELIEVED_TO_HOLD
Fact (Event/Human/Place/etc.)
```

### Example in Neo4j

```cypher
// Evidence
(source1:Document {qid: "Q_SOURCE1", label: "Suetonius - Life of Caesar"})
(source2:Document {qid: "Q_SOURCE2", label: "Plutarch - Life of Caesar"})

// Inference
(inference:InferenceMaking {
    label: "Inference about Rubicon crossing",
    note: "Two independent primary sources agree",
    uncertainty: "low"
})

// Belief
(belief:Belief {
    label: "Belief that Caesar crossed Rubicon",
    certainty: "high"
})

// Fact
(crossing:Event {
    label: "Crossing of the Rubicon",
    qid: "Q_CROSSING"
})

// Relationships
(source1)-[:I1_INFERRED_FROM]->(inference)
(source2)-[:I1_INFERRED_FROM]->(inference)
(inference)-[:I2_BELIEVED_TO_HOLD]->(belief)
(belief)-[:I2_BELIEVED_TO_HOLD]->(crossing)
```

## Query Examples

### Find All Evidence for a Fact

```cypher
MATCH (fact {qid: $fact_qid})
MATCH (belief:Belief)-[:I2_BELIEVED_TO_HOLD]->(fact)
MATCH (inference:InferenceMaking)-[:I2_BELIEVED_TO_HOLD]->(belief)
MATCH (evidence)-[:I1_INFERRED_FROM]->(inference)
RETURN evidence, inference, belief
```

### Find Conflicting Beliefs

```cypher
MATCH (belief1:Belief)-[:I2_BELIEVED_TO_HOLD]->(fact)
MATCH (belief2:Belief)-[:I2_BELIEVED_TO_HOLD]->(fact)
WHERE belief1 <> belief2
RETURN fact, belief1, belief2
```

### Find Belief Revisions

```cypher
MATCH (oldBelief:Belief)<-[:I7_HAS_OBJECT]-
      (revision:BeliefRevision)-[:I8_HAS_RESULT]->
      (newBelief:Belief)
RETURN oldBelief, revision, newBelief
```

## Integration with Langraph Agents

### Agent Workflow

1. **Extract Entity**: Agent extracts entity from text
2. **Assess Confidence**: Determine confidence score
3. **Check Sources**: Count evidence sources
4. **Decision**: Use `should_use_crminf()` to decide approach
5. **Create**: Use appropriate approach (Chrystallum or CRMinf)

### Example Agent Code

```python
from scripts.agents.crminf_agent_tool import CRMinfAgentTool
from scripts.agents.reasoning_decision import should_use_crminf

# In agent extraction workflow
def extract_entity_with_reasoning(text, entity_type):
    # ... extract entity ...
    confidence = calculate_confidence(text, sources)
    source_count = len(sources)
    
    if should_use_crminf(confidence, source_count):
        # Use CRMinf
        tool = CRMinfAgentTool(neo4j_uri, user, password)
        result = tool.create_reasoning_for_entity(
            entity_label=entity.label,
            entity_qid=entity.qid,
            evidence_sources=[s.qid for s in sources],
            confidence=confidence
        )
    else:
        # Use simple Chrystallum
        entity.confidence = confidence
        entity.sources = sources
```

## Benefits

1. **Explicit Reasoning**: Clear chains from evidence to conclusions
2. **Multiple Beliefs**: Can model competing interpretations
3. **Belief Evolution**: Track how beliefs change over time
4. **Transparency**: Full audit trail of reasoning
5. **Standards Compliance**: CRMinf alignment for interoperability

## Next Steps

1. ✅ Schema foundation complete
2. ✅ Core utilities implemented
3. ✅ Agent tools created
4. ⏳ **Integration**: Update agent extraction workflows
5. ⏳ **Testing**: Test with real historical data
6. ⏳ **Documentation**: Add to agent training materials

## References

- CRMinf Specification: https://www.cidoc-crm.org/crminf/
- CRMinf Technical Implementation: `arch/Cidoc/CRMinf_Technical_Implementation.md`
- CIDOC-CRM Alignment: `Docs/architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`


