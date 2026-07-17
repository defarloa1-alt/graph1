# SFA Training Workbook

**Hands-on exercises for training and refining Subject Facet Agents**

---

## 🎯 Goal

By the end of this workbook, you will:
1. Understand how to refine SFA prompts
2. Know how to calibrate evaluation scoring
3. Be able to measure SFA performance
4. Have practical experience with peer review training

---

## Exercise 1: Facet Scope Definition

### Instructions
Define what your SFA should and should not analyze.

### Your Facet: _________________ (e.g., Military, Political, Economic)

### Task 1.1: List Inclusions
**What entities SHOULD this facet analyze?**

1. _______________________________________
2. _______________________________________
3. _______________________________________
4. _______________________________________
5. _______________________________________
6. _______________________________________
7. _______________________________________
8. _______________________________________
9. _______________________________________
10. ______________________________________
... (continue to 20)

### Task 1.2: List Exclusions
**What entities should this facet NOT analyze? (Belongs to other facets)**

1. _______________________________________ → Goes to: __________
2. _______________________________________ → Goes to: __________
3. _______________________________________ → Goes to: __________
4. _______________________________________ → Goes to: __________
5. _______________________________________ → Goes to: __________
... (continue to 20)

### Task 1.3: Identify Edge Cases
**What entities overlap with other facets?**

| Entity | Your Facet Claims | Other Facet Claims |
|--------|-------------------|-------------------|
| Example: Treaty of Versailles | Includes military disarmament | Diplomatic treaty, Political regime change, Economic reparations |
| 1. | | |
| 2. | | |
| 3. | | |
| 4. | | |
| 5. | | |

---

## Exercise 2: Predicate Definition

### Instructions
Define the relationships your SFA will assert.

### Task 2.1: Brainstorm Predicates
**List ALL potential predicates (aim for 40-50):**

1. _______________________________________
2. _______________________________________
3. _______________________________________
... (continue)

### Task 2.2: Group and Deduplicate
**Group similar predicates together:**

| Group | Predicates | Keep |
|-------|-----------|------|
| Example: Command | commanded_army, led_forces, directed_operations | commanded_campaign |
| Group 1: | | |
| Group 2: | | |
| Group 3: | | |

### Task 2.3: Final Predicate List (20-30)
**Your refined predicates:**

```python
YOUR_FACET_PREDICATES = [
    '___________________________',
    '___________________________',
    '___________________________',
    # ... 20-30 total
]
```

---

## Exercise 3: Wikidata Property Selection

### Instructions
Identify Wikidata properties that provide context for your facet.

### Task 3.1: Research Properties
**For each test entity, list available Wikidata properties:**

Test Entity 1: _________________ (QID: ________)
- P___: _________________ (coverage: ___%)
- P___: _________________ (coverage: ___%)
- P___: _________________ (coverage: ___%)

Test Entity 2: _________________ (QID: ________)
- P___: _________________ (coverage: ___%)
- P___: _________________ (coverage: ___%)

### Task 3.2: Prioritize by Coverage
**Sort by data availability:**

| Property | ID | Coverage | Priority |
|----------|-----|----------|----------|
| Example: conflict | P607 | 85% | HIGH |
| | | | |
| | | | |

### Task 3.3: Final Property List (10-20)

```python
YOUR_FACET_PROPERTIES = [
    'P___',  # _______________
    'P___',  # _______________
    'P___',  # _______________
    # ... 10-20 total
]
```

---

## Exercise 4: Prompt Engineering

### Instructions
Iterate on prompts to improve output quality.

### Task 4.1: Baseline Prompt
**Write your initial prompt:**

```
Analyze this subject concept from a _________ perspective:

Subject: {label} (Wikidata {qid})

Questions:
1. _______________________________________?
2. _______________________________________?
3. _______________________________________?
4. _______________________________________?
5. Confidence (0-1)?
```

### Task 4.2: Test Baseline
**Test entity:** _________________ (QID: ________)

**Claude response:**
```
(Paste response here)
```

**Quality scores:**
- Relevance (0-1): ______
- Specificity (0-1): ______
- Actionability (0-1): ______
- **Average: ______**

### Task 4.3: Iteration 1 - Add Specificity
**Modified prompt:**
```
(Write your improved prompt here)
```

**Test again with same entity**

**Quality scores:**
- Relevance (0-1): ______
- Specificity (0-1): ______
- Actionability (0-1): ______
- **Average: ______**

**Change:** ±______ (improvement or decline)

### Task 4.4: Iteration 2 - Add Examples
**Modified prompt:**
```
(Write your improved prompt here)
```

**Quality scores:**
- Relevance (0-1): ______
- Specificity (0-1): ______
- Actionability (0-1): ______
- **Average: ______**

**Change:** ±______ (improvement or decline)

### Task 4.5: Iteration 3 - Add Constraints
**Modified prompt:**
```
(Write your improved prompt here)
```

**Quality scores:**
- Relevance (0-1): ______
- Specificity (0-1): ______
- Actionability (0-1): ______
- **Average: ______**

**Change:** ±______ (improvement or decline)

### Task 4.6: Select Best Prompt
**Best prompt (highest average):** Iteration _____

---

## Exercise 5: Evaluation Scoring

### Instructions
Define and calibrate your significance scoring logic.

### Task 5.1: Define Factors
**What increases significance for your facet?**

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Example: Scale | 0.3 | Larger = more significant |
| Factor 1: | ___ | |
| Factor 2: | ___ | |
| Factor 3: | ___ | |
| Factor 4: | ___ | |
| Factor 5: | ___ | |

**Total weights should sum to ~1.0**

### Task 5.2: Ground Truth Test Set
**Collect 20 entities with known significance:**

| Entity | QID | Ground Truth | Your Score | Difference |
|--------|-----|--------------|------------|------------|
| High: | | 0.9 | | |
| High: | | 0.85 | | |
| High: | | 0.9 | | |
| Medium: | | 0.65 | | |
| Medium: | | 0.7 | | |
| Medium: | | 0.6 | | |
| Low: | | 0.3 | | |
| Low: | | 0.25 | | |
| Low: | | 0.35 | | |

### Task 5.3: Calculate Correlation
```python
import numpy as np

ground_truth = [0.9, 0.85, 0.9, 0.65, 0.7, 0.6, 0.3, 0.25, 0.35, ...]
your_scores = [___, ___, ___, ___, ___, ___, ___, ___, ___, ...]

correlation = np.corrcoef(ground_truth, your_scores)[0,1]
print(f"Correlation: {correlation:.2f}")
```

**Your correlation:** ______

**Target:** > 0.85

### Task 5.4: Refine Weights
**If correlation < 0.85, adjust weights and retest:**

| Factor | Old Weight | New Weight | Reason |
|--------|------------|------------|--------|
| | | | |
| | | | |

**New correlation:** ______

---

## Exercise 6: Threshold Calibration

### Instructions
Find the optimal confidence threshold for claim submission.

### Task 6.1: Test Set
**Collect 100 entities: 50 relevant, 50 irrelevant**

Relevant entities (ground truth = 1):
1. _____________ (QID: _______)
2. _____________ (QID: _______)
... (50 total)

Irrelevant entities (ground truth = 0):
51. _____________ (QID: _______)
52. _____________ (QID: _______)
... (50 total)

### Task 6.2: Test Multiple Thresholds

**Threshold 0.5:**
```
True Positives (TP): _____ (relevant & accepted)
False Positives (FP): _____ (irrelevant & accepted)
True Negatives (TN): _____ (irrelevant & rejected)
False Negatives (FN): _____ (relevant & rejected)

Precision = TP / (TP + FP) = _____
Recall = TP / (TP + FN) = _____
F1 = 2 * (P * R) / (P + R) = _____
```

**Threshold 0.6:**
```
TP: _____ | FP: _____ | TN: _____ | FN: _____
Precision: _____ | Recall: _____ | F1: _____
```

**Threshold 0.7:**
```
TP: _____ | FP: _____ | TN: _____ | FN: _____
Precision: _____ | Recall: _____ | F1: _____
```

**Threshold 0.8:**
```
TP: _____ | FP: _____ | TN: _____ | FN: _____
Precision: _____ | Recall: _____ | F1: _____
```

**Threshold 0.9:**
```
TP: _____ | FP: _____ | TN: _____ | FN: _____
Precision: _____ | Recall: _____ | F1: _____
```

### Task 6.3: Select Optimal Threshold
**Best threshold (highest F1):** _____

**Update in your SFA:**
```python
DEFAULT_CONFIDENCE_THRESHOLD = _____
```

---

## Exercise 7: SPARQL Query Refinement

### Instructions
Optimize your Wikidata discovery queries.

### Task 7.1: Baseline Query
**Write initial query:**

```sparql
SELECT ?item ?itemLabel
WHERE {
  ?item wdt:P___ wd:Q___ .  # Your facet property
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```

**Results:** _____ entities returned
**Precision (relevant / total):** _____

### Task 7.2: Add Filters Iteratively

**Iteration 1: Time period filter**
```sparql
SELECT ?item ?itemLabel
WHERE {
  ?item wdt:P___ wd:Q___ .
  ?item wdt:P569 ?birth .
  FILTER(YEAR(?birth) >= ____ && YEAR(?birth) <= ____)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
```
**Precision:** _____

**Iteration 2: Geographic filter**
```sparql
(Add geographic constraint)
```
**Precision:** _____

**Iteration 3: Relationship filter**
```sparql
(Add relationship to known entities)
```
**Precision:** _____

### Task 7.3: Select Best Query
**Best query (precision > 0.8):** Iteration _____

---

## Exercise 8: Peer Review Training

### Instructions
Train your SFA to validate other facets' claims.

### Task 8.1: Create Test Cases
**Select 20 entities with multi-facet claims:**

| Entity | Your Facet Claim | Other Facet Claim | Should Agree? |
|--------|------------------|-------------------|---------------|
| 1. | | | ☐ Yes ☐ No |
| 2. | | | ☐ Yes ☐ No |
... (20 total)

### Task 8.2: Run Reviews
**For each entity, have your SFA review the other facet's claim:**

```python
review = your_sfa.review_peer_claims(entity_cipher)
```

| Entity | Expected Agreement | Actual Agreement | Correct? |
|--------|-------------------|------------------|----------|
| 1. | Yes | | ☐ ✓ ☐ ✗ |
| 2. | No | | ☐ ✓ ☐ ✗ |
... (20 total)

### Task 8.3: Calculate Accuracy
```
Correct reviews: _____ / 20
Accuracy: _____% 

Target: > 85%
```

### Task 8.4: Error Analysis
**For incorrect reviews, analyze why:**

| Entity | Error Type | Root Cause | Fix |
|--------|-----------|------------|-----|
| | False agreement | | |
| | False disagreement | | |

---

## Exercise 9: Monthly Performance Report

### Instructions
Track your SFA's performance over time.

### Task 9.1: Collect Statistics
```cypher
// Run these queries in Neo4j

// 1. Total claims submitted
MATCH (a:Agent {agent_id: 'YOUR_AGENT_ID'})-[c:ASSERTS]->()
RETURN count(c) as total_claims

// 2. Claims by status
MATCH (a:Agent {agent_id: 'YOUR_AGENT_ID'})-[c:ASSERTS]->()
RETURN c.status, count(*) as count
ORDER BY count DESC

// 3. Average confidence
MATCH (a:Agent {agent_id: 'YOUR_AGENT_ID'})-[c:ASSERTS]->()
RETURN avg(c.confidence) as avg_confidence

// 4. Average agreement score
MATCH (a:Agent {agent_id: 'YOUR_AGENT_ID'})-[c:ASSERTS]->()
WHERE c.agreement_score IS NOT NULL
RETURN avg(c.agreement_score) as avg_agreement

// 5. Contested claims
MATCH (a:Agent {agent_id: 'YOUR_AGENT_ID'})-[c:ASSERTS]->()
WHERE c.status = 'CONTESTED'
RETURN count(c) as contested_count
```

### Task 9.2: Fill Report Template

**Month:** _____________ (e.g., July 2026)

| Metric | Value | Change from Last Month |
|--------|-------|------------------------|
| Total claims | | |
| TBD claims | | |
| PROPOSED claims | | |
| CONFIRMED claims | | |
| CONTESTED claims | | |
| Avg confidence | | |
| Avg agreement | | |
| Precision | | |
| Recall | | |
| F1 score | | |

### Task 9.3: Identify Improvements
**What improved this month?**
1. _______________________________________
2. _______________________________________

**What needs work?**
1. _______________________________________
2. _______________________________________

**Action items for next month:**
1. _______________________________________
2. _______________________________________

---

## Exercise 10: Complete Training Cycle

### Instructions
Run a complete training cycle from baseline to refinement.

### Week 1: Baseline
**Day 1:** Define scope, predicates, properties
**Day 2:** Write baseline prompt
**Day 3:** Test on 10 entities
**Day 4:** Measure baseline performance
**Day 5:** Document baseline

**Baseline metrics:**
- Precision: _____
- Recall: _____
- F1: _____

### Week 2: First Refinement
**Day 1:** Analyze baseline errors
**Day 2:** Refine prompts
**Day 3:** Refine evaluation logic
**Day 4:** Test on 20 entities
**Day 5:** Measure improvement

**After refinement:**
- Precision: _____ (Δ: _____)
- Recall: _____ (Δ: _____)
- F1: _____ (Δ: _____)

### Week 3: Second Refinement
**Day 1:** Analyze remaining errors
**Day 2:** Tune thresholds
**Day 3:** Optimize SPARQL
**Day 4:** Test on 30 entities
**Day 5:** Measure improvement

**After refinement:**
- Precision: _____ (Δ: _____)
- Recall: _____ (Δ: _____)
- F1: _____ (Δ: _____)

### Week 4: Validation
**Day 1:** Test on 100 new entities
**Day 2:** Run peer review training
**Day 3:** Measure final performance
**Day 4:** Document changes
**Day 5:** Deploy to production

**Final metrics:**
- Precision: _____ (Δ from baseline: _____)
- Recall: _____ (Δ from baseline: _____)
- F1: _____ (Δ from baseline: _____)

**Target improvement:** +10% F1 score

---

## Completion Checklist

Mark each as complete:

### Phase 1: Setup
- [ ] Defined facet scope (20 include, 20 exclude)
- [ ] Defined predicates (20-30)
- [ ] Selected Wikidata properties (10-20)
- [ ] Created baseline prompt

### Phase 2: Prompt Engineering
- [ ] Tested 3+ prompt variants
- [ ] Measured quality scores
- [ ] Selected best prompt

### Phase 3: Evaluation Tuning
- [ ] Defined scoring factors
- [ ] Tested on ground truth (20 entities)
- [ ] Achieved correlation > 0.85

### Phase 4: Threshold Calibration
- [ ] Tested 5 threshold values
- [ ] Measured precision/recall/F1
- [ ] Selected optimal threshold

### Phase 5: Query Optimization
- [ ] Wrote baseline SPARQL query
- [ ] Refined with filters (3+ iterations)
- [ ] Achieved precision > 0.8

### Phase 6: Peer Review Training
- [ ] Created 20 test cases
- [ ] Ran reviews
- [ ] Achieved accuracy > 85%

### Phase 7: Performance Tracking
- [ ] Set up monthly reporting
- [ ] Documented baseline metrics
- [ ] Created improvement plan

### Phase 8: Complete Cycle
- [ ] Ran 4-week training cycle
- [ ] Achieved +10% F1 improvement
- [ ] Documented all changes

---

## Next Steps

After completing this workbook:

1. **Deploy your trained SFA** to production
2. **Monitor performance** monthly
3. **Continue refinement** iteratively
4. **Share learnings** with team
5. **Train next SFA** using this template

---

## Resources

- **Training Guide:** `SFA_TRAINING_GUIDE.md`
- **Prompts Guide:** `SFA_PROMPTS_AND_PROCEDURES.md`
- **Quick Reference:** `SFA_QUICK_REFERENCE.md`
- **Military SFA:** `scripts/agents/military/agent.py` (example)
- **Diplomatic SFA:** `scripts/agents/diplomatic/agent.py` (example)

---

**Good luck with your SFA training!** 🚀
