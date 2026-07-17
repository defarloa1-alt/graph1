# SFA Training Guide

**How Subject Facet Agents Learn and Improve Over Time**

---

## Important: SFAs Are Not ML Models

**SFAs are LLM-powered reasoning agents, not trainable models.**

They don't "train" in the machine learning sense (gradient descent, backpropagation, etc.). Instead, they **improve through**:

1. **Prompt refinement** (better instructions)
2. **Graph knowledge accumulation** (richer context)
3. **Threshold tuning** (better decision boundaries)
4. **Decision table evolution** (refined rules)
5. **Peer review feedback** (cross-facet validation)
6. **Tool enhancement** (better graph queries)

Think of SFA "training" as **iterative refinement of a reasoning system**, not model training.

---

## Training Methodology

### Phase 1: Initial Setup (Bootstrap)

#### 1.1 Define Facet Scope
```
Question: What does this facet analyze?

Example (Military SFA):
✅ Military campaigns, battles, sieges
✅ Military commands, orders, training
✅ Strategic and tactical analysis
❌ Political causes of wars (→ Political SFA)
❌ Economic impacts (→ Economic SFA)
❌ Diplomatic treaties (→ Diplomatic SFA)
```

**Training Exercise:**
- List 20 entities your facet SHOULD analyze
- List 20 entities your facet should NOT analyze
- Identify edge cases (overlap with other facets)

#### 1.2 Define Predicates (20-30)
```
Question: What relationships does this facet assert?

Example (Military SFA):
- commanded_campaign
- participated_in_battle
- military_training
- strategic_victory
- tactical_innovation
```

**Training Exercise:**
- Review 100 historical entities in your domain
- Extract common military relationships
- Group similar predicates (avoid redundancy)
- Verify each predicate is distinct and necessary

#### 1.3 Select Wikidata Properties (10-20)
```
Question: Which Wikidata properties provide context?

Example (Military SFA):
- P607: conflict
- P241: military branch
- P598: commander of
- P642: of (qualifier)
```

**Training Exercise:**
- Query Wikidata for sample entities
- Inspect available properties
- Prioritize properties with high data coverage
- Test SPARQL queries with these properties

---

### Phase 2: Prompt Engineering (Iterative)

#### 2.1 Baseline Prompt
Start with the generic prompt template, then refine.

**Initial Prompt (Generic):**
```
Analyze this subject concept from a {Facet} perspective:

Subject: {label} (Wikidata {qid})

Questions:
1. What are the key {facet} aspects?
2. What related {facet} topics should be explored?
3. What entities are relevant?
4. Confidence (0-1)?
```

#### 2.2 Refinement Iterations

**Iteration 1: Add Specificity**
```diff
  Analyze this subject concept from a Military perspective:
  
  Subject: Battle of Cannae (Q36456)
  
  Questions:
  1. What are the key military aspects?
+ 2. What were the military strategies and tactics employed?
+ 3. What was the force composition (infantry, cavalry, etc.)?
+ 4. What was the strategic context (campaign objectives)?
+ 5. What were the military consequences?
- 2. What related military topics should be explored?
  3. What entities are relevant?
  4. Confidence (0-1)?
```

**Iteration 2: Add Examples**
```diff
  Questions:
  1. What are the key military aspects?
+    (e.g., tactics, strategy, force composition, terrain, weather)
  2. What were the military strategies employed?
+    (e.g., double envelopment, feint, ambush, siege, blockade)
```

**Iteration 3: Add Constraints**
```diff
  Questions:
+ NOTE: Focus ONLY on military aspects. Do not analyze:
+ - Political motivations (→ Political SFA)
+ - Economic costs (→ Economic SFA)
+ - Diplomatic consequences (→ Diplomatic SFA)
+
  1. What are the key military aspects?
```

**Training Exercise:**
Run the same entity through 5 prompt variations:
1. Generic prompt
2. Specific questions
3. With examples
4. With constraints
5. With negative examples

Compare outputs and measure:
- Relevance (0-1)
- Specificity (0-1)
- Actionability (0-1)

---

### Phase 3: Evaluation Scoring (Tuning)

#### 3.1 Define Scoring Factors

**Example: Military Significance**

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Scale of engagement | 0.3 | Larger battles more significant |
| Strategic impact | 0.25 | Changed course of war/campaign |
| Tactical innovation | 0.2 | Introduced new methods |
| Historical precedent | 0.15 | First of its kind |
| Documentation quality | 0.1 | Well-attested in sources |

**Training Exercise:**
Test on 20 known entities with ground truth significance:
```
High significance (0.8-1.0): Cannae, Zama, Alesia
Medium significance (0.5-0.8): Smaller battles, skirmishes
Low significance (0.0-0.5): Minor engagements, raids
```

Adjust weights until correlation with ground truth > 0.85.

#### 3.2 Threshold Calibration

**System Thresholds (from Neo4j):**
```cypher
MATCH (t:SYS_Threshold)
RETURN t.name, t.value, t.description
```

**Key Thresholds:**
- `sfa_proposal_confidence_default`: 0.75 (proposal submission threshold)
- `peer_review_agreement_threshold`: 0.7 (consensus threshold)
- `claim_promotion_threshold`: 0.8 (TBD → PROPOSED → CONFIRMED)

**Training Exercise:**
1. Start with default thresholds
2. Run 100 evaluations
3. Measure precision/recall:
   - False positives (low-quality accepted)
   - False negatives (high-quality rejected)
4. Adjust thresholds to optimize F1 score
5. Record threshold changes in `SYS_Threshold` nodes

---

### Phase 4: Graph Knowledge Accumulation

#### 4.1 Bootstrap Initial Graph

**Seed the graph with high-quality entities:**
```cypher
// Example: Military commanders
CREATE (hannibal:Entity:Person {
    qid: 'Q5471',
    label: 'Hannibal Barca',
    entity_cipher: 'ent_per_Q5471',
    dprr_id: 'hannibal_1',
    created_at: datetime()
})

// High-confidence claims
MERGE (agent:Agent {agent_id: 'military_sfa_001'})
CREATE (agent)-[:ASSERTS {
    facet: 'MILITARY',
    predicate: 'commanded_campaign',
    confidence: 0.95,
    status: 'CONFIRMED',
    source_qid: 'Q123456'
}]->(hannibal)
```

**Training Exercise:**
Bootstrap 100 high-confidence entities:
- 30 military commanders
- 30 major battles
- 20 military campaigns
- 20 military innovations

#### 4.2 Iterative Expansion

**Training Loop:**
```
1. SFA discovers new entity (from Wikidata)
2. SFA evaluates relevance
3. If confidence > threshold:
   a. Submit claim via ClaimRegistry
   b. Create entity if new
   c. Add to graph
4. Repeat
```

**Monitoring:**
```cypher
// Track growth
MATCH (e:Entity)
WHERE e.created_at > datetime() - duration({days: 7})
RETURN count(e) as new_entities_last_week

// Track claim status distribution
MATCH (a:Agent)-[c:ASSERTS]->()
RETURN c.status, count(*) as count
ORDER BY count DESC
```

---

### Phase 5: Peer Review Training

#### 5.1 Cross-Facet Validation

**Scenario:** Military SFA finds a claim from Diplomatic SFA

```
Entity: Treaty of Versailles (Q8683)
Diplomatic Claim: "signed_treaty" (confidence: 0.95)

Military SFA Review:
1. Query graph for entity context
2. Check if treaty has military consequences
3. Evaluate diplomatic claim from military perspective:
   - Does treaty affect military operations? ✅
   - Does treaty include military provisions? ✅
   - Is treaty related to war conclusion? ✅
4. Submit review:
   - agrees: true
   - confidence: 0.90
   - reasoning: "Treaty concluded WWI, included military disarmament clauses"
```

**Training Exercise:**
Create 50 test cases:
- 20 agreements (both facets agree)
- 20 disagreements (facets disagree)
- 10 contested (multiple facets disagree)

Measure:
- Agreement rate
- Contested claim rate
- False agreement rate (both facets wrong)

#### 5.2 Feedback Loop

```
Graph State
    ↓
SFA A submits claim
    ↓
SFA B reviews claim
    ↓
If disagreement:
    ↓
    1. Flag as CONTESTED
    2. Human review (ground truth)
    3. Update evaluation logic
    4. Record pattern in decision table
    ↓
Improved SFA behavior
```

**Training Exercise:**
Run 20 contested cases through human review:
```
Entity: Battle of Cannae
Military Claim: "strategic_victory" (0.95)
Political Claim: "regime_destabilizing" (0.85)

Human Review:
✅ Military: Correct (tactical masterpiece)
✅ Political: Correct (threatened Roman Republic)

Action: Both facets correct, no adjustment needed
```

---

### Phase 6: Decision Table Evolution

#### 6.1 Initial Decision Tables

**Example: D8 - Proposal Confidence Rules**

| Condition | Confidence | Action |
|-----------|------------|--------|
| Wikidata P607 present | +0.2 | Increase confidence |
| Multiple sources agree | +0.15 | Increase confidence |
| Source is primary | +0.1 | Increase confidence |
| Entity well-documented | +0.05 | Increase confidence |

**Training Exercise:**
Create decision table for your facet:
1. List conditions that increase/decrease confidence
2. Assign weights based on importance
3. Test on 50 entities
4. Refine weights

#### 6.2 Table Refinement

**Iteration Process:**
```
Week 1: Initial table (10 rules)
    ↓ Test on 100 entities
Week 2: Add 5 new rules based on errors
    ↓ Test on 100 entities
Week 3: Refine weights based on precision/recall
    ↓ Test on 100 entities
Week 4: Validate on 200 new entities
```

**Store in Neo4j:**
```cypher
CREATE (dt:SYS_DecisionTable {
    table_id: 'D_MILITARY_001',
    label: 'Military Significance Scoring',
    description: 'Rules for evaluating military significance',
    version: '1.2',
    last_updated: datetime()
})

CREATE (dt)-[:HAS_ROW]->(row:SYS_DecisionRow {
    condition: 'P607 (conflict) present in Wikidata',
    weight: 0.2,
    action: 'increase_confidence',
    rationale: 'Direct military conflict marker'
})
```

---

### Phase 7: SPARQL Query Optimization

#### 7.1 Initial Queries (Broad)

**Example: Find military commanders**
```sparql
SELECT ?item ?itemLabel
WHERE {
  ?item wdt:P106 wd:Q294414 .  # occupation: military commander
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```

**Problems:**
- Too broad (includes all time periods)
- Missing context (no connection to subject)
- Low precision (includes irrelevant commanders)

#### 7.2 Refined Queries (Specific)

**Iteration 1: Add time period filter**
```sparql
SELECT ?item ?itemLabel
WHERE {
  ?item wdt:P106 wd:Q294414 .
  ?item wdt:P569 ?birth .
  FILTER(YEAR(?birth) >= -500 && YEAR(?birth) <= 100)  # Roman period
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```

**Iteration 2: Add geographic filter**
```sparql
SELECT ?item ?itemLabel
WHERE {
  ?item wdt:P106 wd:Q294414 .
  ?item wdt:P27 wd:Q1747689 .  # country: Roman Republic
  ?item wdt:P569 ?birth .
  FILTER(YEAR(?birth) >= -500 && YEAR(?birth) <= 100)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```

**Iteration 3: Add relationship to known entities**
```sparql
SELECT ?item ?itemLabel ?battleLabel
WHERE {
  ?item wdt:P106 wd:Q294414 .
  ?item wdt:P27 wd:Q1747689 .
  ?item wdt:P607 ?battle .  # participated in conflict
  ?battle wdt:P361 wd:Q35947 .  # part of: Second Punic War
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```

**Training Exercise:**
1. Start with broad query
2. Measure precision (relevant / total)
3. Add filters iteratively
4. Test on each iteration
5. Stop when precision > 0.8

---

## Training Workflows

### Workflow 1: New SFA First Week

**Day 1: Setup**
- [ ] Define facet scope (20 include, 20 exclude examples)
- [ ] Define predicates (20-30)
- [ ] Select Wikidata properties (10-20)
- [ ] Create initial prompt template

**Day 2-3: Prompt Refinement**
- [ ] Test on 10 entities
- [ ] Iterate prompts (3-5 versions)
- [ ] Measure quality (relevance, specificity)
- [ ] Lock in best prompt

**Day 4-5: Evaluation Tuning**
- [ ] Define scoring factors
- [ ] Test on 20 ground truth entities
- [ ] Adjust weights
- [ ] Validate on 20 new entities

**Day 6-7: Integration**
- [ ] Bootstrap 100 high-confidence entities
- [ ] Run peer review on 20 contested cases
- [ ] Refine based on feedback
- [ ] Document patterns

---

### Workflow 2: Monthly Refinement

**Week 1: Data Collection**
```cypher
// Collect claim statistics
MATCH (a:Agent {agent_id: 'military_sfa_001'})-[c:ASSERTS]->()
RETURN 
    c.status,
    count(*) as count,
    avg(c.confidence) as avg_confidence,
    avg(c.agreement_score) as avg_agreement
ORDER BY c.status
```

**Week 2: Error Analysis**
```cypher
// Find contested claims
MATCH (a:Agent {agent_id: 'military_sfa_001'})-[c:ASSERTS]->(e)
WHERE c.status = 'CONTESTED'
RETURN e.label, c.predicate, c.confidence, c.agreement_score
LIMIT 20
```

Analyze patterns:
- Are certain predicates contested more?
- Are certain entity types problematic?
- Are confidence scores miscalibrated?

**Week 3: Refinement**
- Update prompts based on error patterns
- Adjust scoring weights
- Refine decision tables
- Update SPARQL queries

**Week 4: Validation**
- Test on 100 new entities
- Measure improvement:
  - Precision before/after
  - Recall before/after
  - Agreement rate before/after
- Document changes

---

### Workflow 3: Peer Review Training

**Setup:**
```
Entity: Battle of Zama (Q10843)

Agent A (Military): "decisive_battle" (0.95)
Agent B (Political): "regime_stabilizing" (0.85)
Agent C (Diplomatic): "treaty_precipitating" (0.80)
```

**Training Steps:**

1. **Each agent reviews others' claims**
```python
# Military reviews Political claim
military_sfa.review_peer_claims('ent_con_Q10843')
# Result: agrees=True, confidence=0.90

# Political reviews Military claim
political_sfa.review_peer_claims('ent_con_Q10843')
# Result: agrees=True, confidence=0.85
```

2. **Check agreement scores**
```cypher
MATCH (e {entity_cipher: 'ent_con_Q10843'})<-[c:ASSERTS]-()
RETURN c.predicate, c.agreement_score
```

3. **Identify patterns**
- High agreement (>0.8): Both facets correct
- Medium agreement (0.5-0.8): Partial overlap
- Low agreement (<0.5): Different perspectives or error

4. **Refine based on patterns**
- High agreement: Reinforce this pattern
- Medium agreement: Clarify facet boundaries
- Low agreement: Human review needed

---

## Training Metrics

### Quality Metrics

```python
# Precision: Relevant claims / Total claims
precision = correct_claims / total_claims

# Recall: Relevant claims / Total relevant entities
recall = correct_claims / total_relevant

# F1 Score: Harmonic mean
f1 = 2 * (precision * recall) / (precision + recall)

# Agreement Rate: Cross-facet consensus
agreement_rate = agreed_reviews / total_reviews

# Contested Rate: Claims flagged for review
contested_rate = contested_claims / total_claims
```

### Performance Metrics

```python
# Response Time: Average time per evaluation
avg_response_time = sum(response_times) / len(response_times)

# Token Usage: Average tokens per evaluation
avg_tokens = (total_input_tokens + total_output_tokens) / num_evaluations

# Tool Call Efficiency: Average tool calls per evaluation
avg_tool_calls = total_tool_calls / num_evaluations
```

### Growth Metrics

```cypher
// Entities added per week
MATCH (e:Entity)
WHERE e.created_at > datetime() - duration({weeks: 1})
RETURN count(e) as weekly_growth

// Claims by status
MATCH ()-[c:ASSERTS]->()
RETURN c.status, count(*) as count

// Agent activity
MATCH (a:Agent)-[c:ASSERTS]->()
RETURN a.agent_id, count(c) as claims_submitted
ORDER BY claims_submitted DESC
```

---

## Training Best Practices

### 1. Start Small, Iterate Fast
```
❌ Don't: Try to perfect everything upfront
✅ Do: Start with 10 entities, iterate weekly
```

### 2. Measure Everything
```
❌ Don't: "It feels better"
✅ Do: Track precision, recall, F1 before/after changes
```

### 3. Use Ground Truth
```
❌ Don't: Trust SFA outputs blindly
✅ Do: Validate against 20-50 known entities
```

### 4. Document Patterns
```
❌ Don't: Make ad-hoc adjustments
✅ Do: Record patterns in decision tables
```

### 5. Cross-Validate
```
❌ Don't: Train in isolation
✅ Do: Use peer review to catch errors
```

---

## Training Exercises

### Exercise 1: Prompt A/B Testing
**Goal:** Find the best prompt variant

```
Test Entity: Battle of Cannae (Q36456)

Variant A (Generic):
"Analyze this from a military perspective"

Variant B (Specific):
"What were the military tactics, strategy, and force composition?"

Variant C (Constrained):
"Analyze ONLY military aspects. Exclude political/diplomatic."

Measure:
- Relevance (0-1)
- Specificity (0-1)
- Actionability (0-1)

Best: Variant with highest average score
```

### Exercise 2: Threshold Calibration
**Goal:** Find optimal confidence threshold

```
Test Set: 100 entities (50 relevant, 50 irrelevant)

Threshold 0.6: Precision=0.70, Recall=0.95, F1=0.81
Threshold 0.7: Precision=0.80, Recall=0.85, F1=0.82
Threshold 0.8: Precision=0.90, Recall=0.70, F1=0.79

Best: 0.7 (highest F1)
```

### Exercise 3: Peer Review Simulation
**Goal:** Train agents to validate each other

```
20 Entities with ground truth
5 agents (Military, Political, Diplomatic, Economic, Geographic)

Each agent submits claims
Each agent reviews others' claims

Measure:
- True agreement rate (both correct)
- False agreement rate (both wrong)
- True disagreement rate (correct disagreement)

Refine until:
- True agreement > 0.85
- False agreement < 0.05
```

---

## Next Steps

1. **Read this guide** ✅ (you are here)
2. **Review existing SFAs** (Military, Diplomatic)
3. **Choose your focus:**
   - Prompt refinement
   - Evaluation tuning
   - Graph bootstrapping
   - Peer review training
4. **Run training exercises**
5. **Measure and iterate**

---

## Resources

- **SFA Base Class:** `scripts/agents/subject_concept_facet_agents.py`
- **Military SFA:** `scripts/agents/military/agent.py` (example)
- **Diplomatic SFA:** `scripts/agents/diplomatic/agent.py` (example)
- **ClaimRegistry:** `scripts/agents/claim_registry.py`
- **PeerReviewer:** `scripts/agents/peer_reviewer.py`
- **Prompts Guide:** `SFA_PROMPTS_AND_PROCEDURES.md`
- **Quick Reference:** `SFA_QUICK_REFERENCE.md`

---

**Remember:** SFAs improve through **iterative refinement**, not model training. Focus on better prompts, richer context, and tighter validation loops.
