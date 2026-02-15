# Agent Usage Examples

**Purpose:** Training examples for ChatGPT agents working with Chrystallum  
**Date:** February 14, 2026  
**Version:** Phase 1

---

## Example 1: Simple Genealogy Claim

### User Input
```
Marcus Brutus was son of Servilia
```

### Agent Processing

**Step 1: Entity Resolution**
- Extract entities: "Marcus Brutus", "Servilia"
- Resolve QIDs via QIDResolver:
  - Marcus Brutus → Q83416 (confidence: 0.98)
  - Servilia → Q242571 (confidence: 0.95)

**Step 2: Relationship Validation**
- Relationship: "son of" → canonical "CHILD_OF"
- Check registry: ✓ CHILD_OF exists (P40)
- Inverse: PARENT_OF

**Step 3: Facet Selection**
- Primary facet: `demographic` (baseline: 0.92)
- Secondary facets: `social` (baseline: 0.85)
- Political context weak → skip `political` facet

**Step 4: Claim Structure**
```json
{
  "entity_id": "hum_marcus_brutus_q83416",
  "relationship_type": "CHILD_OF",
  "target_id": "hum_servilia_q242571",
  "confidence": 0.92,
  "label": "Marcus Brutus was child of Servilia",
  "subject_qid": "Q83416",
  "facet": "demographic",
  "claim_signature": "Q83416:CHILD_OF:Q242571",
  "authority_source": "wikidata",
  "authority_ids": {
    "source": "Q83416",
    "target": "Q242571",
    "property": "P40"
  }
}
```

**Expected Response:**
```
✓ Claim created successfully
  Entity: Marcus Brutus (Q83416)
  Relationship: CHILD_OF
  Target: Servilia (Q242571)
  Facet: demographic (confidence: 0.92)
  Status: promoted (confidence and posterior both >= 0.90)
```

---

## Example 2: Battle Participation with Role

### User Input
```
Caesar commanded legions at Battle of Pharsalus
```

### Agent Processing

**Step 1: Entity Resolution**
- Caesar → Q1048
- Battle of Pharsalus → Q193492

**Step 2: Role Validation**
- Role input: "commanded"
- RoleValidator fuzzy match:
  - "commanded" → canonical "commander" (exact match, confidence: 1.0)
  - P-value: P598 (commander)
  - Context facets: ["military"]

**Step 3: Relationship Selection**
- Primary: PARTICIPATED_IN (P710)
- With qualifier: role="commander"

**Step 4: Facet Selection**
- Primary facet: `military` (baseline: 0.85)
- Secondary facet: `political` (baseline: 0.88 for commanders)

**Step 5: Claim Structure**
```json
{
  "entity_id": "hum_julius_caesar_q1048",
  "relationship_type": "PARTICIPATED_IN",
  "target_id": "evt_battle_pharsalus_q193492",
  "confidence": 0.95,
  "label": "Julius Caesar commanded at Battle of Pharsalus",
  "subject_qid": "Q1048",
  "facet": "military",
  "claim_signature": "Q1048:PARTICIPATED_IN:Q193492:commander",
  "authority_source": "wikidata",
  "authority_ids": {
    "source": "Q1048",
    "target": "Q193492",
    "property": "P710",
    "role_qualifier": "P598"
  },
  "metadata": {
    "role": "commander",
    "faction": "Roman",
    "outcome": "victorious"
  }
}
```

**Expected Response:**
```
✓ Claim created successfully
  Entity: Julius Caesar (Q1048)
  Relationship: PARTICIPATED_IN
  Target: Battle of Pharsalus (Q193492)
  Role: commander (validated from canonical registry)
  Facet: military (confidence: 0.95)
  Qualifiers: faction="Roman", outcome="victorious"
  Status: promoted
```

---

## Example 3: Roman Gens Membership

### User Input
```
Julius Caesar was member of gens Julia
```

### Agent Processing

**Step 1: Entity Resolution**
- Julius Caesar → Q1048
- gens Julia → Q233482 (or create Gens node)

**Step 2: Relationship Validation**
- Relationship: "member of gens" → canonical "MEMBER_OF_GENS"
- Check registry: ✓ MEMBER_OF_GENS exists (P53)
- Inverse: HAS_GENS_MEMBER

**Step 3: Facet Selection**
- Primary: `social` (baseline: 0.90)
- Secondary: `political` (baseline: 0.85)
- Tertiary: `cultural` (baseline: 0.88)
- Also consider: `demographic` (baseline: 0.85)

**Step 4: Claim Structure**
```json
{
  "entity_id": "hum_julius_caesar_q1048",
  "relationship_type": "MEMBER_OF_GENS",
  "target_id": "gen_julia_q233482",
  "confidence": 0.90,
  "label": "Julius Caesar was member of gens Julia",
  "subject_qid": "Q1048",
  "facet": "social",
  "claim_signature": "Q1048:MEMBER_OF_GENS:Q233482",
  "authority_source": "wikidata",
  "authority_ids": {
    "source": "Q1048",
    "target": "Q233482",
    "property": "P53"
  }
}
```

**Expected Response:**
```
✓ Claim created successfully
  Entity: Julius Caesar (Q1048)
  Relationship: MEMBER_OF_GENS
  Target: gens Julia (Q233482)
  Facet: social (confidence: 0.90)
  Alternative facets: political (0.85), cultural (0.88), demographic (0.85)
  Status: promoted
  Note: Roman gens affiliation well-documented in Republic era
```

---

## Example 4: Ambiguous Role Resolution

### User Input
```
Pompey was leading the forces at Battle of Pharsalus
```

### Agent Processing

**Step 1: Role Extraction**
- Input role: "leading the forces"
- Not exact match in canonical registry

**Step 2: RoleValidator Fuzzy Match**
- LLM fuzzy match candidates:
  1. "commander" (confidence: 0.92) ✓ — "leading" matches command semantics
  2. "general" (confidence: 0.88)
  3. "officer" (confidence: 0.75)
- Select: "commander" (highest confidence above 0.80 threshold)

**Step 3: Relationship Creation**
- Use PARTICIPATED_IN with role="commander"
- Authority: P710 + P598 (role qualifier)

**Expected Response:**
```
✓ Role resolved via fuzzy match
  Input: "leading the forces"
  Canonical: "commander"
  Confidence: 0.92
  Alternative matches: general (0.88), officer (0.75)

✓ Claim created successfully
  Entity: Pompey (Q297162)
  Relationship: PARTICIPATED_IN
  Target: Battle of Pharsalus (Q193492)
  Role: commander (fuzzy matched)
  Facet: military (confidence: 0.90)
  Status: promoted
```

---

## Example 5: Provisional QID (No Wikidata Match)

### User Input
```
Titus Labienus was Caesar's legate in Gaul
```

### Agent Processing

**Step 1: QID Resolution**
- Caesar → Q1048 ✓
- Titus Labienus → Wikidata search...
  - Best match: Q192817 (confidence: 0.72) — below 0.75 threshold
  - Fallback: Create provisional QID

**Step 2: Provisional QID Creation**
```
local_entity_8a3f2e10
```
- Deterministic hash from "Titus Labienus"
- Enable post-hoc linking if Wikidata match found later

**Step 3: Claim Structure**
```json
{
  "entity_id": "hum_titus_labienus_local_8a3f2e10",
  "relationship_type": "SERVED_UNDER",
  "target_id": "hum_julius_caesar_q1048",
  "confidence": 0.85,
  "label": "Titus Labienus served under Caesar in Gaul",
  "subject_qid": "local_entity_8a3f2e10",
  "facet": "military",
  "claim_signature": "local_entity_8a3f2e10:SERVED_UNDER:Q1048:legate",
  "authority_source": "provisional",
  "authority_ids": {
    "source": "local_entity_8a3f2e10",
    "target": "Q1048"
  },
  "metadata": {
    "role": "legate",
    "context": "Gallic Wars"
  }
}
```

**Expected Response:**
```
⚠ Provisional QID created
  Entity: Titus Labienus
  QID: local_entity_8a3f2e10 (provisional)
  Reason: No Wikidata match above confidence threshold (0.75)
  Note: Post-hoc linking enabled when better match found

✓ Claim created successfully
  Entity: Titus Labienus (provisional)
  Relationship: SERVED_UNDER
  Target: Julius Caesar (Q1048)
  Role: legate
  Facet: military (confidence: 0.85)
  Status: created (not promoted - confidence below 0.90)
```

---

## Example 6: Multi-Facet Claim

### User Input
```
Caesar's marriage to Calpurnia was a political alliance
```

### Agent Processing

**Step 1: Entity Resolution**
- Caesar → Q1048
- Calpurnia → Q229399

**Step 2: Relationship Selection**
- Primary: SPOUSE_OF (P26)
- Context indicator: "political alliance"

**Step 3: Multi-Facet Evaluation**
- User explicitly mentions political context
- But SPOUSE_OF applies to multiple facets:
  - `political`: 0.92 (alliance)
  - `social`: 0.90 (personal union)
  - `demographic`: 0.88 (vital statistics)
  - `economic`: 0.85 (dowry/inheritance)

**Step 4: Agent Decision**
- Create primary claim in `political` facet
- Suggest related facets for consideration

**Expected Response:**
```
✓ Claim created successfully
  Entity: Julius Caesar (Q1048)
  Relationship: SPOUSE_OF
  Target: Calpurnia (Q229399)
  Facet: political (confidence: 0.92)
  Status: promoted

ℹ Related facets available for SPOUSE_OF:
  • social (baseline: 0.90) - personal union context
  • demographic (baseline: 0.88) - vital statistics
  • economic (baseline: 0.85) - dowry/inheritance
  
  Consider: "Was this marriage also significant in social/economic contexts?"
```

---

## Example 7: Death Event with Location

### User Input
```
Pompey was killed in Egypt in 48 BCE
```

### Agent Processing

**Step 1: Entity Resolution**
- Pompey → Q297162
- Egypt → Q79 (country) or specific location?

**Step 2: Relationship Selection**
- Primary: DIED_AT (P1120)
- Note: Death events have high confidence baselines

**Step 3: Temporal Context**
- Year: -48 (48 BCE)
- Link to Year node

**Step 4: Facet Selection**
- Primary: `demographic` (baseline: 0.95)
- Special context: `military` (baseline: 0.98 for combat deaths)
- Given "killed" implies violence → use `military` facet

**Step 5: Claim Structure**
```json
{
  "entity_id": "hum_pompey_q297162",
  "relationship_type": "DIED_AT",
  "target_id": "plc_egypt_q79",
  "confidence": 0.98,
  "label": "Pompey died at Egypt in 48 BCE",
  "subject_qid": "Q297162",
  "facet": "military",
  "claim_signature": "Q297162:DIED_AT:Q79:-48",
  "authority_source": "wikidata",
  "authority_ids": {
    "source": "Q297162",
    "target": "Q79",
    "property": "P1120"
  },
  "metadata": {
    "year": -48,
    "manner_of_death": "killed",
    "context": "civil_war"
  }
}
```

**Expected Response:**
```
✓ Claim created successfully
  Entity: Pompey the Great (Q297162)
  Relationship: DIED_AT
  Target: Egypt (Q79)
  Facet: military (confidence: 0.98)
  Temporal: 48 BCE (Year -48)
  Context: Combat death during civil war
  Status: promoted (high confidence for death events)
```

---

## Example 8: Invalid Role Rejection

### User Input
```
Caesar was supreme mega-commander at Pharsalus
```

### Agent Processing

**Step 1: Role Validation**
- Input role: "supreme mega-commander"
- RoleValidator search:
  - Exact match: ❌
  - Alias match: ❌
  - Fuzzy match:
    - "commander" (0.65) — below 0.80 threshold
    - "general" (0.58) — below threshold

**Step 2: Validation Failure**
```json
{
  "canonical_role": null,
  "confidence": null,
  "valid": false,
  "method": "no_match",
  "input_label": "supreme mega-commander",
  "valid_roles": ["commander", "general", "soldier", ...],
  "suggestion": "Role not recognized; use canonical role registry"
}
```

**Expected Response:**
```
❌ Role validation failed
  Input: "supreme mega-commander"
  Reason: No match in canonical registry
  
  Did you mean:
  • commander (P598) - Military commander with strategic authority
  • general (P410) - General rank with multi-army command
  
  Valid military roles:
  commander, general, soldier, cavalry, officer, scout, casualty
  
  Please specify a canonical role or suggest addition to registry.
```

---

## Example 9: Fallacy Detection (Flag-Only)

### User Input
```
Caesar crossed the Rubicon because he wanted absolute power
```

### Agent Processing

**Step 1: Claim Analysis**
- Claim type: `motivational` (interpretive)
- Facet: `political` (interpretive)
- Content: Causal claim with motivation attribution

**Step 2: Fischer Fallacy Detection**
- Detected fallacies:
  - **Motivation fallacy:** Attributing intent without direct evidence
  - **Post hoc reasoning:** Assuming outcome reveals motive
- Critical fallacy: ✓ Yes (motivation)

**Step 3: Fallacy Flag Intensity**
- Claim profile: interpretive type + interpretive facet
- Result: **HIGH** intensity flag

**Step 4: Promotion Decision**
- Confidence: 0.75 (moderate)
- Posterior: 0.68 (below 0.90 threshold)
- Fallacy flag: HIGH
- **Promotion: BLOCKED** (by metrics, not fallacy)

**Expected Response:**
```
⚠ Claim created with HIGH fallacy flag
  Entity: Julius Caesar (Q1048)
  Relationship: CROSSED
  Target: Rubicon River (Q13989)
  Facet: political (confidence: 0.75)
  
  Fallacies detected:
  • Motivation fallacy - Attributing intent without direct evidence
  • Post hoc reasoning - Assuming outcome reveals motive
  
  Fallacy flag: HIGH (interpretive claim + political facet)
  Status: NOT promoted (posterior 0.68 < 0.90 threshold)
  
  Note: Fallacies flagged for review but did not block claim.
        Promotion blocked by metrics (posterior below threshold).
  
  Recommendation: Reframe as descriptive claim:
    "Caesar crossed the Rubicon in 49 BCE" (factual, temporal)
```

---

## Example 10: Query Pattern Discovery

### User Input
```
Show me all generals who fought against Caesar
```

### Agent Processing

**Step 1: Query Planning**
- Entity: Julius Caesar (Q1048)
- Relationship: FOUGHT_AT (inverse of FOUGHT_IN)
- Filter: role="general" or role="commander"
- Discovery mode: May require multi-hop traversal

**Step 2: Cypher Generation**
```cypher
// Find all humans who participated in battles where Caesar also participated
MATCH (caesar:Human {qid: 'Q1048'})
MATCH (caesar)-[:PARTICIPATED_IN]->(battle:Event)
MATCH (enemy:Human)-[r:PARTICIPATED_IN]->(battle)
WHERE r.role IN ['general', 'commander']
  AND enemy.qid <> 'Q1048'
  AND r.faction <> caesar.faction  // Opposed factions
RETURN 
  enemy.qid AS qid,
  enemy.label AS name,
  enemy.labels_multilingual AS multilingual_labels,
  r.role AS role,
  r.faction AS faction,
  battle.label AS battle,
  battle.year AS year,
  r.outcome AS outcome
ORDER BY year DESC
LIMIT 50
```

**Expected Response:**
```
Found 8 generals who opposed Caesar:

1. Pompey the Great (Q297162)
   Role: general
   Battles: Pharsalus (-48), Dyrrhachium (-48)
   Faction: Optimates
   Outcome: defeated at Pharsalus

2. Cato the Younger (Q192213)
   Role: commander
   Battles: Thapsus (-46)
   Faction: Republican
   Outcome: suicide after defeat

3. Vercingetorix (Q83458)
   Role: general
   Battles: Alesia (-52), Gergovia (-52)
   Faction: Gallic
   Outcome: captured at Alesia

[...continues]

Note: Results include multilingual labels and full federation context.
      See QIDs for Wikidata linkage.
```

---

## Common Patterns Summary

### ✅ Do This
- Always resolve entities to QIDs (Wikidata or provisional)
- Validate roles against canonical registry
- Select facets based on context + baselines
- Use per-facet confidence when available
- Include authority_source and authority_ids
- Structure claims with complete metadata

### ❌ Don't Do This
- Don't invent QIDs without provisional format
- Don't create custom roles without validation
- Don't ignore facet context
- Don't omit authority tracking
- Don't block promotion on fallacies (metrics only)
- Don't skip confidence baselines

### 🔍 When Uncertain
- Use QIDResolver with context for disambiguation
- Use RoleValidator fuzzy match for natural language roles
- Check `relationship_facet_baselines.json` for facet-specific confidence
- Consult `role_qualifier_reference.json` for role aliases
- Flag high-confidence provisional QIDs for human review
- Suggest alternative facets when multiple apply

---

## Example 11: Wikipedia Processing Summary (Roman Republic)

### Overview
When Chrystallum processes the Wikipedia Roman Republic article, it follows a **7-phase pipeline** from raw text to validated subgraph.

#### Phase 1: Seed Entity Extraction
- Seed QID: Q17167 (Roman Republic)
- Period: -509 to -27

#### Phase 2: Named Entity & Relationship Extraction
From article text, system extracts **127 entities** across 5 types:
- Humans: 68 (Caesar Q1048, Pompey Q297162, Antony Q309264, Scipio Q2176, Hannibal Q8458, etc.)
- Events: 32 (Battle of Actium Q193304, Pharsalus Q193492, Battle of Zama Q48314, etc.)
- Places: 18 (Rome Q220, Carthage Q6343, Sicily Q1460, Gaul Q38060, etc.)
- Organizations: 6 (Senate Q842606)
- Periods: 3 (Roman Republic, Punic Wars, Civil Wars)

#### Phase 3: Relationship Extraction & Validation
System extracts and validates **3,247 relationships:**

```json
[
  {
    "source": "Q17167",
    "relationship": "STARTS_IN_YEAR",
    "target": "-509",
    "confidence": 0.95,
    "facet": "political",
    "evidence": "traditionally dated to 509 BC"
  },
  {
    "source": "Q17167",
    "relationship": "ENDS_IN_YEAR",
    "target": "-27",
    "confidence": 0.98,
    "facet": "political",
    "evidence": "ending in 27 BC with establishment of Roman Empire"
  },
  {
    "source": "Q1048",
    "relationship": "AT_WAR_WITH",
    "target": "Q297162",
    "confidence": 0.95,
    "facet": "military",
    "temporal": "-49",
    "evidence": "civil war again in 49 BC between Julius Caesar and Pompey"
  },
  {
    "source": "Q1048",
    "relationship": "DIED_AT",
    "target": "Q220",
    "confidence": 0.98,
    "facet": "military",
    "temporal": "-44",
    "evidence": "Caesar was assassinated in 44 BC"
  },
  {
    "source": "Q1646",
    "relationship": "DEFEATED",
    "target": "Q309264",
    "confidence": 0.95,
    "facet": "military",
    "event": "Q193304",
    "temporal": "-31",
    "evidence": "Antony's defeat at Battle of Actium in 31 BC"
  },
  {
    "source": "Q1048",
    "relationship": "PARTICIPATED_IN",
    "target": "Q193492",
    "confidence": 0.95,
    "facet": "military",
    "role": "commander",
    "faction": "Roman",
    "outcome": "victorious",
    "evidence": "Battle of Pharsalus (implicit from civil war context)"
  },
  {
    "source": "Q297162",
    "relationship": "PARTICIPATED_IN",
    "target": "Q193492",
    "confidence": 0.95,
    "facet": "military",
    "role": "commander",
    "faction": "Optimates",
    "outcome": "defeated",
    "evidence": "Battle of Pharsalus (implicit from defeat context)"
  },
  {
    "source": "Q313530",
    "relationship": "PARTICIPATED_IN",
    "target": "overthrow_monarchy_event",
    "confidence": 0.85,
    "facet": "political",
    "role": "leader",
    "evidence": "revolution led by semi-mythical Lucius Junius Brutus"
  },
  {
    "source": "Q1048",
    "relationship": "MEMBER_OF_GENS",
    "target": "Q233482",
    "confidence": 0.95,
    "facet": "social",
    "evidence": "gens Julia (implicit from Julius Caesar name)"
  },
  {
    "source": "Q220",
    "relationship": "CONQUERED",
    "target": "Q6343",
    "confidence": 0.95,
    "facet": "military",
    "event": "Q48314",
    "temporal": "-202",
    "evidence": "Rome defeated Carthage at Battle of Zama in 202 BC"
  },
  {
    "source": "Q17167",
    "relationship": "AT_WAR_WITH",
    "target": "Q6343",
    "confidence": 0.98,
    "facet": "military",
    "note": "three_punic_wars",
    "evidence": "against which it waged three wars"
  }
]
```

**Phase 4: Wikidata Backlink Harvest**

From Q17167, system would discover:
- All humans with P27 (country of citizenship) = Q17167
- All events with P361 (part of) = Q17167
- All places with P131 (located in) = Roman territory
- All battles with participants Q17167
- All senators with P39 (position held) during this period
- All consuls, dictators, tribunes of the period

Expected harvest size:
- Source nodes: ~50-100 (key battles, civil wars, political events)
- Accepted backlinks: ~500-1000 entities
- Total subgraph: Would hit 1000-node cap; require trimming

**Phase 5: Facet Assignment**

Each relationship evaluated across relevant facets:
- Caesar vs Pompey civil war:
  - `military` (primary, baseline: 0.92)
  - `political` (secondary, baseline: 0.90)
  - `social` (tertiary, baseline: 0.75)
  
- Gens memberships:
  - `social` (primary, baseline: 0.90)
  - `political` (secondary, baseline: 0.85)
  - `cultural` (tertiary, baseline: 0.88)
  - `demographic` (quaternary, baseline: 0.85)

- Battle participations:
  - `military` (primary, baseline: 0.85)
  - `political` (for commanders, baseline: 0.88)

**Phase 6: Role Validation**

Roles mentioned in text would be validated:
- "led the revolt" → canonical "leader" (fuzzy match 0.88)
- "commanded troops" → canonical "commander" (exact match 1.0)
- "defeated" → outcome qualifier, not role
- "king" → political role "monarch" (alias match 0.95)
- "consul" → exact match to registry (1.0)
- "dictator" → exact match to registry (0.98)
- "general" → alias for "commander" (0.95)

**Phase 7: Fallacy Detection**

Several claims would be flagged:
```
⚠ HIGH intensity - Motivational claim:
  "Hannibal took the city in 219, triggering the Second Punic War"
  Fallacy: Post hoc reasoning (assuming trigger = cause)
  Status: Flag for review (not blocked)

⚠ LOW intensity - Descriptive claim:
  "Rome defeated Carthage at Battle of Zama in 202 BC"
  Fallacy: None detected
  Status: Promoted if confidence >= 0.90

⚠ HIGH intensity - Interpretive claim:
  "The republican system was an elective oligarchy, not a democracy"
  Fallacy: Presentism (modern political labels)
  Status: Flag for review (not blocked)
```

#### Phase 7: QID Resolution
Wikidata matching: **119/127 entities (93.7%)** matched above 0.75 confidence threshold  
Provisional QIDs: **8/127 (6.3%)** created as `local_entity_{hash}` (e.g., obscure senators, minor battles)

### Final Statistics

```
✓ Entities: 127 (68 humans, 32 events, 18 places, 6 orgs, 3 periods)
✓ Relationships: 3,247 (PARTICIPATED_IN 842, HELD_OFFICE 387, MEMBER_OF_GENS 215, DEFEATED 94, etc.)
✓ Claims Generated: 5,519 (multi-facet across 17 facets)
✓ Claims Promoted: 4,102 (74.3% promotion rate)
✓ Claims Flagged: 287 (5.2% HIGH intensity for review)
✓ QID Resolution: 119/127 Wikidata (93.7%) + 8 provisional local (6.3%)
✓ Subgraph: 2,318 nodes (all discovered entities preserved, no trimming) ready for Neo4j ingestion
```

**For complete 10-phase processing details:** See [ARCHITECTURE_OPTIMIZATION_REVIEW.md](ARCHITECTURE_OPTIMIZATION_REVIEW.md#stage-6-wikipedia-text--claims)

---

## Example 12: Deduplication & Reconciliation

**CRITICAL:** This example shows how agents prevent duplicate edges by checking existing claims before creating new ones.

### Scenario
Same claim ingested from two different sources on different days:

**Day 1 (Wikidata source):**
```
"Julius Caesar was married to Calpurnia"
Authority: Wikidata (Q1048 married-to Q2297)
Confidence: 0.95
```

**Day 2 (Wikipedia source):**
```
"Caesar married Calpurnia"
Authority: Wikipedia article on Julius Caesar
Confidence: 0.92
```

### Agent Workflow

**Step 1: Query for Existing Claim**

```cypher
// Check if same relationship already exists
MATCH (caesar:Human {qid: "Q1048"})-[rel:SPOUSE_OF {facet: "genealogical"}]->(calpurnia:Human {qid: "Q2297"})
RETURN rel, rel.confidence, rel.posterior_probability, rel.authority_ids
```

**Result:** Found existing relationship → rel.confidence = 0.95, rel.posterior = 0.95, rel.authority_ids = {wikidata: ["Q1048"]}

**Step 2: Determine Action**

Since the claim exists, agent proceeds to reconciliation (not duplication):

```
OLD STATE:
  confidence: 0.95
  posterior: 0.95
  authority_ids: {"wikidata": ["Q1048"]}
  sources: 1

NEW INPUT:
  confidence: 0.92
  authority: Wikipedia
  sources: 1
```

**Step 3: Apply Bayesian Merging**

```
Existing posterior = 0.95
New confidence = 0.92
Agreement = 1.0 (both say same thing, no contradiction)

Merged confidence = (0.95 + 0.92) / 2 * 1.0 = 0.935
New posterior = 0.935 (apply minor rounding: 0.93)
```

**Step 4: Update Authority**

```json
OLD:
{
  "wikidata": ["Q1048"],
  "confidence_source": "Wikidata"
}

NEW:
{
  "wikidata": ["Q1048"],
  "wikipedia": ["Julius_Caesar"],
  "confidence_source": "Wikidata + Wikipedia (reconciled)"
}
```

**Step 5: Write Back to Graph**

```cypher
MATCH (caesar:Human {qid: "Q1048"})-[rel:SPOUSE_OF {facet: "genealogical"}]->(calpurnia:Human {qid: "Q2297"})
SET rel.confidence = 0.93,
    rel.posterior_probability = 0.93,
    rel.authority_ids = {wikidata: ["Q1048"], wikipedia: ["Julius_Caesar"]},
    rel.updated_at = timestamp(),
    rel.reconciliation_note = "Merged with Wikipedia source (confidence: 0.92); high agreement"
RETURN rel
```

### Output

**No duplicate created.** Former claim updated:

```json
{
  "relationship": "SPOUSE_OF",
  "from": {"qid": "Q1048", "label": "Julius Caesar"},
  "to": {"qid": "Q2297", "label": "Calpurnia"},
  "facet": "genealogical",
  "confidence_old": 0.95,
  "confidence_new": 0.93,
  "posterior_probability": 0.93,
  "authority_ids": {
    "wikidata": ["Q1048"],
    "wikipedia": ["Julius_Caesar"]
  },
  "reconciliation_count": 2,
  "action": "MERGED (high agreement, both sources agree)",
  "promoted": true,
  "note": "Multiple sources increase reliability; posterior stable at 0.93"
}
```

---

## Example 12b: Conflict Detection During Deduplication

**Same scenario with conflicting information:**

**Day 1 (Scholarly source):**
```
"Julius Caesar died on March 15, 44 BC"
```

**Day 2 (AI extraction from ambiguous text):**
```
"Caesar died in 43 BC"
Authority: AI agent (uncertain)
Confidence: 0.45
```

### Deduplication with Conflict

**Step 1: Query**
```cypher
MATCH (caesar:Human {qid: "Q1048"})-[death:DIED_AT]->(year:Year)
WHERE year.year = -44
RETURN death, death.confidence, death.authority_ids
```

**Result:** Found: DIED_AT -44 (confidence 0.92, Wikidata source)

**Step 2: Detect Conflict**

New claim says -43 (difference of 1 year).

```
Temporal delta: |-44 - (-43)| = 1 year
Threshold: Accept if delta <= 0 (exact year), high conflict if > 0
Conflict detected: YES
```

**Step 3: Apply Conflict Penalty**

```
Existing posterior = 0.92
New confidence = 0.45
Agreement = 0.3 (major conflict on year, only 45% confidence from AI)

Merged confidence = (0.92 + 0.45) / 2 * 0.3 = 0.2055
New posterior = 0.205 (express maximum uncertainty)
```

**Step 4: Flag for Human Review**

```cypher
MATCH (caesar:Human {qid: "Q1048"})-[death:DIED_AT]->(year:Year)
WHERE year.year = -44
SET death.conflict_detected = true,
    death.conflict_note = "Temporal conflict: -44 vs -43",
    death.conflict_sources = ["Wikidata (0.92, -44)", "AI extraction (0.45, -43)"],
    death.review_required = true,
    death.review_priority = "HIGH"
RETURN death
```

**Output:**

```json
{
  "relationship": "DIED_AT",
  "from": {"qid": "Q1048", "label": "Julius Caesar"},
  "to": {"year": -44},
  "existing_confidence": 0.92,
  "incoming_confidence": 0.45,
  "conflict_detected": true,
  "conflict_reason": "Temporal disagreement: -44 vs -43",
  "merged_posterior": 0.205,
  "action": "CONFLICT - Escalate to human review",
  "promoted": false,
  "high_priority_flag": true,
  "recommendation": "Historian should verify actual death date. Wikidata highly confident (-44); AI source unreliable (0.45)."
}
```

### Key Lessons from Examples 12a & 12b

✅ **Do:**
- Query before creating (always)
- Merge confidences when sources agree
- Reconcile authority_ids (expand source list)
- Flag conflicts immediately (don't auto-merge)

❌ **Don't:**
- Create duplicate edges
- Override existing confident claims with lower-confidence new data
- Assume all conflicts are errors (escalate)
- Ignore temporal specificity

---

**For Full Documentation:** See `SCHEMA_REFERENCE.md`, `PHASE_1_DECISIONS_LOCKED.md`, and `AI_CONTEXT.md`
