<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# building chrystallum a knowledge graph of history we are developing a standardization, trying to map to wikidata as much as possible, but where we think more granularity is needed, we do it anyway with our graph structure.  is this common practice in a graph? are we overlooking something? our system is driven by a backbone that requires each node to map to a single lcc/lcsh/fast backbone to tie them all togher where each subject manages llms in that subject and returns a subgraph to persist the lllm response. look at this from different perspectives and advise

Excellentâ€”let me analyze your Chrystallum architecture from multiple perspectives. You've built something sophisticated. Here are my observations:

## ARCHITECTURE ASSESSMENT

### âœ… WHAT YOU'RE DOING RIGHT

**1. Controlled Proliferation with Purpose**
Your model *is* standard practice in mature knowledge graphs. You're not blindly replicating Wikidataâ€”you're extending it where historical knowledge demands finer granularity. This is exactly what major projects do:

- **Library of Congress** - Maps to LC classification but creates local subject headings
- **Europeana** - Uses Wikidata + custom cultural properties
- **CIDOC-CRM** - Maintains Wikidata compatibility while adding domain-specific depth
- **NEH projects** - Routinely augment Dublin Core with discipline-specific vocabularies

Your "where think more granularity is needed, we do it anyway" is professional practice.

**2. The LCC/LCSH/FAST Backbone is Smart**
This is your *single point of consensus*. Each node maps to exactly one library standard = single LLM subject authority. This solves:

- **Version control** - All claims about "Roman military tactics" funnel through one FAST ID
- **Disambiguation** - Caesar the person â‰  Caesar as title, but they connect through the same backbone entry
- **Scalability** - 100 LLMs debating "Politics" all return subgraphs to the same subject node

**3. Subgraph Persistence Design is Solid**
Your architecture of LLM response â†’ subgraph â†’ persistent layer is correct. This means:

- LLM hallucinations don't corrupt the backbone
- Conflicting claims stay localized
- You preserve reasoning chains (which fact source supports which claim)

***

## âš ï¸ POTENTIAL BLIND SPOTS

### 1. **The Many-to-Many Problem You Haven't Yet Named**

Your current model assumes:

```
Node â†’ Single LCSH/FAST â†’ Single Subject Authority
```

But historical reality often breaks this:

**Example: The Gracchi Brothers' Land Reforms (Roman History)**

- LCSH: "Land reformâ€”Rome"
- LCSH: "Agrarian lawsâ€”Rome"
- LCSH: "Social conflictâ€”Rome"
- LCSH: "Populismâ€”Rome" (anachronistic but used)

Your current architecture maps one node to **one** backbone entry. What happens when historical reality requires **simultaneous** representation in multiple frameworks?

**The Risk:** You force choosing primary subject (politics? economics? social history?) when the truth is multiplicative.

**Solution Already in Your Designs:**
Your relationship CSV has this partially solved with:

- `parent_relationship` field (specificity hierarchy)
- `specificity_level` (1-3, lets you traverse up/down)
- Multi-label capability in your schemas

**But You Need:** Explicit many-to-many mapping documentation. When should a node have 1 backbone link vs. 3?

***

### 2. **The Granularity Governance Question (Unmarked)**

You have ~23 subjects, 86 periods, 36 places in your backbone. Good start. But:

**Question You Haven't Documented:**

- What decides "this needs its own Period node" vs. "this is a sub-period"?
- What decides "this needs custom relationship" vs. "LCSH RELATED_TO is enough"?

**Current Risk:** The granularity decision becomes tribal knowledge. Six months from now, agent A creates node type X, agent B creates competing node type Y, and reconciliation is expensive.

**What to Add:**
A decision matrix:


| Decision | Criterion | Example |
| :-- | :-- | :-- |
| Create new Period | Unique geopolitical entity + distinct events + named by sources | "Late Roman Republic" separate from "Roman Republic" âœ“ |
| Create new Relationship | Cannot be expressed via parent + property | "CONDEMNED_WITHOUT_TRIAL" â‰  parent "LEGAL_ACTION" + property |
| Create custom Concept | Concept appears in primary sources + LCSH gap + 3+ events reference it | "Liberti" (freed slaves) in Roman law |
| Use existing standard | LCSH/FAST/CIDOC covers it already | Use CIDOC E21_Person, don't create PERSON_TYPE |


***

### 3. **The Subgraph Boundary Problem**

Your SUBGRAPH_STRUCTURE defines subject + entities + time + geography. But:

**What's the **boundary** of a subgraph about "Sulla's Dictatorship"?**

Does it include:

- âœ… Sulla (person)
- âœ… Events during dictatorship
- âœ… Organizations reformed
- â“ Military predecessors who influenced Sulla?
- â“ Later figures who reacted to him?
- â“ Civil war causes vs. dictatorship itself?

**Current State:** Your docs say "3 events = 3 subgraph vertices" but don't define stopping rules.

**The Practical Problem:**
Two agents on same subject might return subgraphs of wildly different sizes. Agent A returns "just the dictatorship itself" (tight boundary), Agent B returns "civil war context + aftermath" (loose boundary). Both valid, but conflict resolution becomes messy.

**What You Need:**
Boundary specification in your subject node:

```json
{
  "subject": "Sulla's Dictatorship",
  "scope": {
    "temporal": "82-79 BCE (inclusive)",
    "spatial": "Italian Peninsula + civil war theaters",
    "thematic": "Political authority + military transformation + institutional reform",
    "exclusions": "Pre-civil war Sullan family politics, Post-restoration Sullan legacy"
  }
}
```


***

### 4. **LLM Subject Authority: You Haven't Solved Consensus**

You say "each subject manages LLMs in that subject and returns a subgraph."

But what happens here:

**Military historian LLM says:** "Siege of Alesia (52 BCE) was militarily decisive, psychologically devastating to Gauls"

**Political historian LLM says:** "Siege of Alesia was primarily a political statementâ€”consolidating Roman authority over Gaul"

**Economic historian LLM says:** "Siege of Alesia redistributed wealth from Gallic elite to Roman treasury"

All three are writing subgraphs to the same event node. Your architecture *persists* these competing claims (good), but you haven't documented:

1. **Merge strategy** - Do all three subgraphs coexist? Do you take union of all claims?
2. **Confidence scoring** - How do you weight military expert vs. economic expert?
3. **Conflict markers** - When historians disagree fundamentally, how is that surfaced?

**Wikidata solution:** `rank: preferred/normal/deprecated` + source citations
**CIDOC-CRM solution:** `P16_used_specific_object_of_type` with belief/uncertainty properties
**Your system:** Not documented yet

***

### 5. **The Temporal Backbone Looks Thin**

You have 86 periods. For Roman history alone, this seems light if you're trying to support granular history. That might be by design (coarse-grained periods only, events fill detail), but:

**Question:** Are your periods like Library of Congress subject period subdivisions ("Roman Republicâ€”To 30 B.C.") or like proper chronological entities (Event-independent Period nodes)?

**This Matters For:**

- How you relate events to multiple overlapping periods
- Whether "period" is data or metadata
- How you support partial overlaps (e.g., "this battle happened in the overlap of two period definitions")

***

## ðŸŽ¯ WHAT YOU'RE OVERLOOKING

### **1. Lineage \& Provenance**

You're building an LLM-sourced knowledge graph but I don't see:

- **Claim provenance** - Which LLM created which fact? With what confidence?
- **Revision history** - When did understanding change? Why?
- **Source citation** - What textual evidence supports this subgraph?

**This is critical for historical knowledge** because:

- Primary sources often conflict
- Historiography matters (Marxist vs. Postcolonial vs. Military history lens)
- "LLM hallucinated this" should be detectable

Add to every claim:

```
ATTRIBUTED_TO â†’ (LLM_Agent | Historical_Source)
I7_HAS_OBJECT â†’ (Prior_Belief | null)  // CIDOC-CRM for revisions
confidence_score â†’ 0.0-1.0
```


***

### **2. Semantic Versioning of the Graph**

Your graph is evolving. LLMs will:

- Add new entities
- Refine relationships
- Correct errors
- Discover new periods/places

**You need:**

```
Graph version: 1.2.3
- Backbone (LCC/LCSH/FAST) version: stable
- Custom extensions version: 2.1
- Last updated: 2025-12-12
- Breaking changes: [list]
```

Without this, in 6 months you won't know if query results changed due to real history or schema drift.

***

### **3. The "Custom Extension Registry"**

You're creating granularity beyond Wikidata. Where's the registry?

**What I'd add:**

```
custom_relationships.md:
- CONDEMNED_WITHOUT_TRIAL (created by Roman specialist, date, rationale)
- LAND_DISTRIBUTED_TO (created by economic historian, date, rationale)
- GRANTED_IMMUNITY (edge case, rarely used, needed for trial records)

custom_properties.md:
- goal_type: enum {POL, MIL, ECO, REL, SOC}
- trigger_type: enum {OPPORT, THREAT, CRISIS, SUCCESSION}
- belief_certainty: 0.0-1.0

rationale_for_custom_extension.md:
- Why not use Wikidata P828 (caused by)?
- When do we prefer your CAUSED vs. CONTRIBUTED_TO?
```


***

### **4. Conflict Resolution Workflow**

Two LLMs disagree. Now what?

**You haven't documented:**

1. **Detection** - How do you know they conflict? (Same event, different dates/locations?)
2. **Escalation** - Does this go to human domain expert? Automatic voting?
3. **Resolution** - Mark one `deprecated`? Keep both with `confidence`? Flag for review?
4. **Appeal** - If expert overrides LLM, how is that fed back?

**Suggest:**

```cypher
(event:Event)-[:HAS_CLAIM {confidence: 0.85, llm_agent: "military", date_asserted: "2025-12-12"}]â†’(claim:Claim)
(claim)-[:CONFLICTS_WITH]â†’(other_claim:Claim {confidence: 0.65, llm_agent: "political"})
(conflict:Conflict)-[:RESOLUTION_STATUS {status: "unresolved|expert_pending|resolved"}]
```


***

## ðŸš€ STRATEGIC RECOMMENDATIONS

### **Priority 1: Document Granularity Governance**

Add a decision matrix to md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md that explains when to create custom nodes/relationships vs. using Wikidata standards.

### **Priority 2: Formalize Subgraph Boundaries**

Your SUBGRAPH_STRUCTURE should specify:

- Temporal boundary (inclusive/exclusive dates)
- Spatial extent (places included)
- Thematic scope (what counts as "about" this subgraph)
- Stopping rules for related entities


### **Priority 3: Add Provenance Layer**

Every subgraph should carry:

```json
{
  "provenance": {
    "created_by": "llm_agent_name",
    "timestamp": "2025-12-12T...",
    "sources": ["URL", "citation"],
    "confidence_overall": 0.87,
    "conflicts": ["subgraph_id_that_contradicts_this"]
  }
}
```


### **Priority 4: Semantic Versioning**

Add VERSION.json to your schema:

```json
{
  "graph_version": "1.0.0",
  "backbone_version": "stable",
  "extensions_version": "2.1",
  "last_breaking_change": "2025-12-10",
  "compatible_with": ["wikidata_2025-12", "cidoc-crm_7.1"]
}
```


### **Priority 5: Conflict Management SOP**

Document the workflow:

- How conflicts are detected
- Which agent/human decides
- How resolution is recorded
- Appeal/override mechanism

***

## FINAL THOUGHT: COMMON PRACTICE CHECK

**Yes, you're doing something common:**

- DBpedia extends Wikipedia/Wikidata âœ“
- YAGO extends Wikipedia + Wikidata âœ“
- WikidataWD-plus projects routinely add custom properties âœ“
- CIDOC-CRM users always add domain specializations âœ“

**But you're NOT seeing it often documented because most projects treat it as:**

1. Private extensions (not published)
2. Implicit governance (tribal knowledge)
3. One-off decisions (not systematized)

**You're being more rigorous than average.** What you're missing is making that rigor *explicit and documented* so future you (and your team) can maintain consistency.

The backbone is brilliant. The subgraph structure is sound. What's missing is the **governance framework** that lets you scale without chaos.

Want me to build out a formal **Governance Decision Matrix** or **Conflict Resolution SOP** as a living document?
<span style="display:none">[^1_1][^1_2][^1_3]</span>

<div align="center">â‚</div>

[^1_1]: md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md

[^1_2]: canonical_relationship_types.csv

[^1_3]: SUBGRAPH_STRUCTURE.md


---

# we have an agent that decides - is it a duplicate, additive or a replacement because of confidence - if needed debates can get implemented before any graph update is permitted. true on multiplicity of subjects and i think some form of interagent ie different subject smes might be possibe

Perfect. Now let me detail what you have working and what needs formalization:

***

## WHAT YOU'VE GOT RIGHT

### **1. Three-Outcome Triage System**

Your agent correctly identifies:

- **DUPLICATE** - Same claim, same confidence (why ingest twice?)
- **ADDITIVE** - Different angles on same fact (military + political lens)
- **REPLACEMENT** - New claim with higher confidence (better scholarship)

This is exactly the pattern used by:

- Wikidata (preferred rank / normal rank / deprecated rank)
- Wikipedia dispute resolution (conflicting sources coexist)
- Academic publishing (superseded by newer evidence)


### **2. Confidence-Driven Decisions**

You're using confidence as **arbiter**, not boolean truth. This is sophisticated because:

- Historian A says Caesar was 5'11" (confidence 0.4 - Roman sources vague)
- Historian B says Caesar was 5'7" (confidence 0.3 - same vague sources)
- Neither is "right"; you record both with confidence bounds
- Future LLM can say "Caesar's height unknown, historians disagree, sources silent"


### **3. Multi-SME Debate Architecture**

You mention "interagent debates"â€”this is the missing piece most KGs don't have. This means:

- Military historian generates subgraph about Alesia
- Political historian generates conflicting subgraph
- Before graph update, they debate
- Debate is *recorded* as part of the claim provenance

**This is novel.** Most systems suppress the debate; you're preserving it.

***

## WHAT NEEDS FORMALIZATION

### **1. Confidence Scoring Rubric (MISSING)**

You have confidence scores but I don't see documented:

**What is 0.95 vs 0.65?**

Propose this framework:

```markdown
# Confidence Scoring Rubric

## Source Quality Tiers

| Tier | Confidence Range | Examples | Notes |
|------|------------------|----------|-------|
| Primary Source | 0.85-1.0 | Roman legal documents, inscriptions, coins | Direct evidence, minimal interpretation |
| Secondary Source (Academic) | 0.75-0.90 | Peer-reviewed journal, monograph by subject expert | Interpreted by expert, citable |
| Secondary Source (Populist) | 0.65-0.75 | Wikipedia articles, general history books | Well-researched but broader audience |
| Tertiary/Synthesis | 0.50-0.70 | Textbooks, survey articles, synthesis works | Accurate but at distance from sources |
| LLM Synthesis (High Consensus) | 0.70-0.85 | LLM trained on multiple expert sources, no contradictions | Generated knowledge, no primary source risk |
| LLM Synthesis (Conflicting) | 0.40-0.60 | LLM trained on contradictory sources, interpretive question | Epistemic uncertainty embedded |
| Inference/Reconstruction | 0.30-0.50 | Plausible but not directly sourced (e.g., social structures) | Reasonable inference, could be wrong |
| Speculation | 0.10-0.30 | Historian's educated guess, admitted as such | Not suitable for graph without debate |

## Confidence Calculation Formula

```

Base Confidence = Source Tier Midpoint
Modifiers:

+ 0.05 if multiple independent sources agree
- 0.10 if primary source ambiguous
+ 0.10 if archaeological evidence supports
- 0.15 if historiographical consensus weak

Final = clamp(Base + Modifiers, 0.0, 1.0)

```

## Decision Thresholds

| Decision | Threshold | Example |
|----------|-----------|---------|
| ACCEPT (no debate) | New â‰¥ 0.80 AND (Existing = 0 OR New > Existing + 0.15) | New=0.85, Existing=0.65 â†’ REPLACE |
| ADDITIVE (coexist) | 0.20 < difference < 0.15 OR both â‰¥ 0.60 | New=0.70, Existing=0.65 â†’ DEBATE |
| REJECT | New < Existing - 0.15 AND Existing â‰¥ 0.60 | New=0.50, Existing=0.70 â†’ REJECT |
| ESCALATE TO DEBATE | Difference < 0.15 AND both â‰¥ 0.50 AND topics overlap | Both ~0.70 â†’ INVOKE DEBATE |
```


***

### **2. Multi-SME Debate Protocol (PARTIALLY SKETCHED)**

You mention debates can be implemented. Here's what needs specification:

```markdown
# Multi-SME Debate Protocol

## When is Debate Triggered?

Automatic triggers:
1. Same entity + same backbone subject
2. Confidence scores within 15% of each other
3. Both scores â‰¥ 0.50 (too low = mutual skepticism)
4. Different LLM agents (different expertise domains)

Optional manual triggers:
- Domain expert requests debate
- Historiographical significance (this matters a lot historically)
- Community flagging

## Debate Structure

### Round 1: Evidence Presentation (each agent gets 1)
- Agent A: "I claim Caesar's height was 5'11\". Evidence: [sources]"
- Agent B: "I claim Caesar was 5'7\". Evidence: [sources]"

### Round 2: Counter-Evidence (each agent gets 1)
- Agent A: "Your sources don't distinguish..." 
- Agent B: "But your sources conflate..."

### Round 3: Mutual Adjustment (optional)
- Can either agent revise confidence up/down?
- Example: Agent A says "OK, I lower to 0.70 but stand by it"

### Resolution Voting
- Third-party expert judges? YES/NO
- Pure algorithmic? (majority confidence wins)
- Historiographical weight? (if topic is settled scholarship)

## Debate Outcome Recording

```

{
"debate_id": "debate_20251212_001",
"timestamp": "2025-12-12T16:30:00Z",
"claims": [
{
"claim_id": "claim_001",
"agent": "military_historian_llm",
"entity": "Caesar height",
"value": "5'11\" (183cm)",
"initial_confidence": 0.75,
"final_confidence": 0.70,
"evidence": ["Suetonius, Life of Caesar", "Pliny Natural History"],
"adjusted": true,
"reasoning": "Concede ambiguity in source interpretation"
},
{
"claim_id": "claim_002",
"agent": "social_historian_llm",
"value": "5'7\" (170cm)",
"initial_confidence": 0.65,
"final_confidence": 0.68,
"evidence": ["Comparison to armor measurements", "Plutarch"],
"adjusted": true,
"reasoning": "Slightly increased after A's concession"
}
],
"resolution": "ADDITIVE_WITH_NOTE",
"final_verdict": "Sources ambiguous; both heights plausible. Mark as historiographical dispute.",
"expert_review_requested": false
}

```

## Resolution Outcomes

| Outcome | Condition | Graph Action | Notes |
|---------|-----------|--------------|-------|
| REPLACE | One agent revises down, other wins | Mark loser `deprecated` | Rare; happens when new evidence found |
| ADDITIVE | Both maintain confidence within range | Both claims persist, cross-linked | Flag as historiographical dispute |
| EXPERT_ESCALATE | Agents deadlock | Send to domain expert for judgment | Human makes final call |
| BOTH_REJECTED | Both agents lower â‰¤ 0.40 | Remove both, mark "insufficient evidence" | Claim needs new research |
| SYNTHESIZE | Agents find middle ground | Create new claim at negotiated confidence | E.g., "Caesar 5'7\"-5'11\", exact height unknown" |

```


***

### **3. Multi-Subject Multiplicities (YOU FLAGGED THIS)**

You're right that different SMEs might generate claims linked to *different backbone subjects*. This is critical:

**Example: The Gracchi Land Reforms (133 BCE)**

Military SME creates:

```
Event: "Tiberius Gracchus assassination"
Subject: "Political violence"
Confidence: 0.88
```

Economic SME creates:

```
Event: "Land redistribution program"
Subject: "Agrarian economics"
Confidence: 0.85
```

Political SME creates:

```
Event: "Constitutional crisis"
Subject: "Political institutions"
Confidence: 0.90
```

**Current architecture question:** Are these:

- **A) Three separate events?** (Assassination â‰  Redistribution â‰  Crisis)
- **B) One event, three subject angles?** (Same historical moment, different lenses)
- **C) One event, three claims about it?** (Gracchi reforms *caused* political instability, etc.)

**This matters because your decision logic changes:**

```markdown
# Multi-Subject Claim Handling

## Case A: Genuinely Different Events
â†’ ADDITIVE (no conflict, different entities)
â†’ Create edges linking them (PRECEDED_BY, CAUSED, etc.)
â†’ No debate needed

## Case B: Same Event, Different Subject Angles
â†’ Check: Do claims conflict OR complement?
  
  Complement (Event happened for multiple reasons):
    â†’ ADDITIVE 
    â†’ Create multiple (Event)-[:SUBJECT_OF]-(Subject) edges
    â†’ All perspectives preserved
    
  Conflict (Incompatible causal claims):
    â†’ DEBATE required
    â†’ Example: "Reforms were voluntary" vs. "Reforms were coercive"
    
## Case C: One Event Linked to Multiple Subjects
â†’ Automatic ADDITIVE
â†’ This is graph design feature, not conflict
â†’ All SMEs are correct simultaneously

## Detection Algorithm

```

def classify_multi_subject_claim(new_claim, existing_claim):
\# Same entity + same backbone subject + same date range
if (new_claim.entity_id == existing_claim.entity_id and
new_claim.primary_subject == existing_claim.primary_subject and
date_overlap(new_claim.date, existing_claim.date)):
return "SAME_EVENT_SAME_SUBJECT" â†’ debate_required

    # Same entity + different backbone subjects
    elif (new_claim.entity_id == existing_claim.entity_id and
          new_claim.primary_subject != existing_claim.primary_subject):
        
        # Check if claims are complementary or contradictory
        if claims_compatible(new_claim, existing_claim):
            return "SAME_EVENT_MULTI_SUBJECT" â†’ additive
        else:
            return "SAME_EVENT_CONFLICTING_ANGLES" â†’ debate_required
    
    # Different entities, same subject
    else:
        return "DIFFERENT_EVENT" â†’ additive
    ```

```


***

### **4. Debate Agent Specification (NEEDS BUILDING)**

Right now you mention debates are possible. You need to specify *which agent arbitrates*:

```markdown
# Debate Arbitration Specification

## Three Models to Choose From

### Model 1: Peer Review (Symmetric)
```

Military SME â†” Political SME
â†“
Debate recorded
â†“
Confidence scores adjusted
â†“
Both sign off OR escalate to expert

```

**Pros:** Egalitarian, scholarly, preserves reasoning  
**Cons:** Slow, could deadlock equally-confident agents

### Model 2: Hierarchical Expertise
```

Claim 1: Military expert (confidence 0.88)
Claim 2: Social historian (confidence 0.82)
â†“
Route to: "Military during social change" expert
â†“
Expert SME decides:

- Is military aspect primary? (weight claim 1 more)
- Is social aspect primary? (weight claim 2 more)
- Are they describing same event? (keep both)

```

**Pros:** Fast, leverages domain-specific expertise  
**Cons:** Requires third-party expert, adds latency

### Model 3: Historiographical Authority
```

Both claims vetted against:

- Current historiographical consensus
- Publication frequency in top journals
- Expert citation patterns

Highest alignment wins, others marked "minority view"

```

**Pros:** Grounds in scholarship  
**Cons:** Conservative, might suppress new interpretations

## Recommendation for Chrystallum

**Use hybrid: Model 1 â†’ Model 2**
1. Agents debate (Peer Review) for 1-2 rounds
2. If deadlock, escalate to domain-specialized expert
3. Record full debate chain as provenance
```


***

### **5. Graph Update Lock Until Resolution (YOU MENTIONED)**

This is perfect practice. Formalize it:

```markdown
# Graph Update Freeze Protocol

## Status: Claim Processing States

| State | Meaning | Can be queried? | Edges created? | Can transition to |
|-------|---------|-----------------|-----------------|-------------------|
| INGESTED | New claim received, awaiting triage | NO | NO (temp only) | DUPLICATE / ADDITIVE / DEBATE |
| DEBATE_PENDING | Conflict detected, awaiting resolution | NO | NO | DEBATE_IN_PROGRESS |
| DEBATE_IN_PROGRESS | Active debate | NO | NO (temp) | DEBATE_RESOLVED / EXPERT_ESCALATE |
| EXPERT_REVIEW | Sent to human expert | NO | NO | EXPERT_APPROVED / EXPERT_REJECTED |
| APPROVED | Ready for graph | YES | YES | ACTIVE |
| ACTIVE | In graph, canonical | YES | YES | DEPRECATED (if replaced) |
| DEPRECATED | Superseded by newer claim | YES | YES (historical) | DELETED (optional) |
| REJECTED | Did not meet criteria | NO | NO | DELETED (clean up) |

## Transition Rules

```

// Only these edges trigger graph update
MATCH (claim:Claim {status: "APPROVED"})
CREATE (claim)-[:PERSISTED_TO]->(graph:Graph)

// No edges created until status = APPROVED
MATCH (claim:Claim {status: "INGESTED|DEBATE_PENDING"})
RETURN "No edges created, claim in limbo"

// Debate must complete before ANY persistence
MATCH (debate:Debate)-[:INVOLVES]->(claim:Claim)
WHERE debate.status = "UNRESOLVED"
RETURN "Claim locked until debate resolved"

```

## Conflict Lock Example

```

{
"claim_id": "claim_sulla_dictatorship_001",
"entity": "Sulla's Dictatorship",
"status": "DEBATE_PENDING",
"locked_until": "debate_resolved",
"blocking_reason": [
{
"conflict_with": "claim_sulla_dictatorship_002",
"confidence_diff": 0.08,
"both_scores_high": true,
"subject_overlap": true,
"requires": "multi_sme_debate"
}
],
"timestamp_created": "2025-12-12T15:45:00Z",
"timestamp_locked": "2025-12-12T15:47:30Z",
"estimated_resolution": "2025-12-13T10:00:00Z"
}

```

---

## OPERATIONAL QUESTIONS FOR YOUR TEAM

Now that you have the decision agent, answer these:

### **Question 1: Confidence Threshold Values**
What are YOUR thresholds for:
- "High confidence enough to REPLACE?" (your 0.15 difference rule?)
- "Similar enough to require DEBATE?" (your current threshold?)
- "Too low, reject outright?" (below 0.40?)

### **Question 2: Multi-SME Debate Trigger**
When exactly is debate triggered?
- Only same event + same subject + score overlap?
- Also: same event + different subjects + conflicting interpretations?
- Also: historiographically significant events (always debate)?

### **Question 3: Expert Arbitration**
If agents deadlock, who decides?
- Domain expert human? (slow but authoritative)
- Third expert LLM? (faster, but which expert?)
- Historiographical voting? (scalable)
- Consensus requirement? (both agents must agree to resolution)

### **Question 4: Debate Record Preservation**
When debate is resolved, do you:
- Keep full debate transcript? (audit trail, but bloats graph)
- Keep only final confidence + note? (cleaner)
- Link to external debate document? (best of both)

### **Question 5: Deprecated Claims**
When claim is replaced, do you:
- Delete old claim? (lossy, can't see history)
- Mark deprecated? (preserves historiography)
- Keep both with note? (too verbose for some queries)

---

## PROPOSAL: Formalize Decision Agent as Spec Document

I'd recommend creating:

```

decision_agent_spec.md
â”œâ”€â”€ Confidence Scoring Rubric (your values, not defaults)
â”œâ”€â”€ Decision Thresholds Matrix
â”œâ”€â”€ Duplicate Detection Algorithm
â”œâ”€â”€ Multi-SME Debate Protocol
â”œâ”€â”€ Conflict Lock Mechanism
â”œâ”€â”€ Debate Arbitration Models
â””â”€â”€ Claim Status State Machine

```

This becomes the **operational manual** your agent(s) follow. It also becomes **testable**: 
- Given claim X + claim Y with scores, what decision should agent make?
- Does agent match spec? If not, log deviation.

Want me to template out that spec doc in full? Or focus on one section (the debate protocol seems most critical)?

---

# good response. i only gave u very partial artifacts. regarding multisubject gracchi - well to me it is one event, which different personal perspectives. pick the most granular, and edge out to the other events

Perfectâ€”**that's the right call**. Let me formalize what you just articulated:

![Agent Decision Framework: From Ingestion to Graph Update](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/4a8dddda26d6d29519168cfe15a1b53c/84c3dbce-b749-430a-a77b-52a776cb702c/f323ea8d.png)

Agent Decision Framework: From Ingestion to Graph Update

***

## YOUR DESIGN PRINCIPLE: "MOST GRANULAR EVENT AS ANCHOR"

### The Rule

```

When multiple perspectives describe the same historical moment:

1. Pick the MOST GRANULAR event as the primary node
2. Create edges from that event to broader/related interpretations
3. All perspectives persist, but hierarchy is explicit
```

### Why This Works

**1. Graph Queries Become Tractable**
- Start at atomic event â†’ traverse outward to context
- Don't start at "Roman Republic Period" â†’ traverse to 10,000 events
- Bounded search space

**2. Preserves Historiographical Nuance**
- The assassination IS a discrete event (E5_Event)
- The land reform IS economic policy (linked via CAUSED / PART_OF)
- The constitutional crisis IS political interpretation (linked via INTERPRETED_AS)
- You don't force choosing one "true" framing

**3. Aligns with CIDOC-CRM Event-Centric Philosophy**
The CRM explicitly models this:[^3_1]
> "Events are the most powerful tool for inference... The object points us towards the events that brought it into existence, modified it and/or led to its destruction"

Your approach mirrors this: start with the discrete observable event, build context from there.

***

## FORMALIZED PATTERN: EVENT GRANULARITY HIERARCHY

### The Gracchi Example (133 BCE)

```cypher
// MOST GRANULAR EVENT (atomic, observable)
CREATE (assassination:Event {
  qid: "Q...",
  label: "Assassination of Tiberius Gracchus",
  date_iso8601: "-0133-06",
  cidoc_class: "E5_Event",
  unique_id: "Q..._EVENT_TIBERIUS_ASSASSINATION",
  granularity: "atomic"  // <--- NEW PROPERTY
})

// SUBJECT ANCHORS (multiple perspectives)
CREATE (assassination)-[:SUBJECT_OF]->(political_violence:Subject {
  label: "Political violence",
  fast_id: "1069240"
})

CREATE (assassination)-[:SUBJECT_OF]->(political_transitions:Subject {
  label: "Political transitions", 
  fast_id: "1069263"
})

// BROADER CONTEXTUAL EVENTS (composite/interpreted)
CREATE (land_reform:Event {
  label: "Gracchi Land Reforms",
  start_date: "-0133",
  end_date: "-0121",
  granularity: "composite"  // <--- Spans multiple atomic events
})

CREATE (constitutional_crisis:Event {
  label: "Late Republic Constitutional Crisis",
  start_date: "-0133",
  end_date: "-0027",
  granularity: "period_event"  // <--- Interpretive, long-duration
})

// EDGES: ATOMIC â†’ COMPOSITE
CREATE (assassination)-[:PART_OF]->(land_reform)
CREATE (assassination)-[:TRIGGERED]->(constitutional_crisis)

// CAUSAL CHAINS
CREATE (land_reform)-[:CAUSED {
  confidence: 0.85,
  agent: "economic_historian",
  reasoning: "Redistribution threatened Senate landholdings"
}]->(assassination)

CREATE (assassination)-[:INTERPRETED_AS {
  confidence: 0.78,
  agent: "political_historian",
  reasoning: "Senate response to populist challenge"
}]->(constitutional_crisis)
```


### Key Properties

| Property | Values | Purpose |
| :-- | :-- | :-- |
| `granularity` | `atomic`, `composite`, `period_event`, `macro_event` | Query optimization + historical clarity |
| Atomic | Single discrete moment, direct observation | E.g., assassination, battle, decree |
| Composite | Multiple atomic events grouped | E.g., "Gallic Wars" = 8 years of battles |
| Period_event | Interpretive construct, historiographical | E.g., "Fall of Republic", "Crisis of Third Century" |
| Macro_event | Abstract causal claim | E.g., "Roman Expansion" (not a single event) |


***

## OPERATIONAL RULES FOR AGENT DECISION

### Rule 1: When Multiple Perspectives Arrive, Identify Granularity

```python
def classify_event_granularity(event_claim):
    """
    Classify event granularity to decide anchor point.
    """
    # Atomic: Single date/moment, specific participants, observable
    if (event_claim.has_specific_date() and 
        event_claim.duration_days <= 7 and
        event_claim.has_named_participants()):
        return "atomic"
    
    # Composite: Explicit start/end, collection of sub-events
    elif (event_claim.has_date_range() and 
          event_claim.duration_days > 7 and
          event_claim.references_sub_events()):
        return "composite"
    
    # Period_event: Historiographical construct, vague boundaries
    elif (event_claim.duration_years > 5 and
          event_claim.is_interpretive_label()):
        return "period_event"
    
    # Macro_event: Abstract, no specific dates
    else:
        return "macro_event"
```


### Rule 2: Always Create Atomic Event First

When agent receives claims about "Gracchi Land Reforms":

```markdown
Step 1: Extract atomic events from narrative
- "Tiberius Gracchus proposes lex agraria" (atomic)
- "Senate debates land bill" (atomic)
- "Tiberius assassinated" (atomic)
- "Gaius Gracchus elected tribune" (atomic)
- "Gaius Gracchus dies" (atomic)

Step 2: Create composite event
- "Gracchi Land Reforms" = collection of above

Step 3: Create edges
- Each atomic event -[:PART_OF]-> composite event
- Composite event -[:SUBJECT_OF]-> "Agrarian economics"
- Composite event -[:SUBJECT_OF]-> "Political reform"
- Atomic events each -[:SUBJECT_OF]-> specific subjects

Step 4: Link to broader interpretations
- Composite -[:CONTRIBUTED_TO]-> "Late Republic Crisis"
```


### Rule 3: Edge Direction = Granularity Flow

```
ATOMIC_EVENT -[:PART_OF]-> COMPOSITE_EVENT -[:PART_OF]-> PERIOD_EVENT

Example:
(Rubicon crossing) -[:PART_OF]-> (Caesar's Civil War) -[:PART_OF]-> (Fall of Republic)
```

**Query Advantage:**

```cypher
// Find all atomic events in "Fall of Republic"
MATCH (atomic:Event {granularity: "atomic"})-[:PART_OF*1..3]->(fall:Event {label: "Fall of Roman Republic"})
RETURN atomic.label, atomic.date_iso8601
ORDER BY atomic.date_iso8601

// Returns: Rubicon (49 BCE), Pharsalus (48 BCE), Ides of March (44 BCE), etc.
```


***

## HANDLING MULTI-PERSPECTIVE CLAIMS: THE DECISION MATRIX

### Scenario: Three Agents Generate Competing Claims

**Military Historian Agent:**

```json
{
  "event": "Battle of Alesia",
  "label": "Decisive military victory",
  "granularity": "atomic",
  "date": "-52-09",
  "primary_subject": "Military tactics",
  "confidence": 0.88
}
```

**Political Historian Agent:**

```json
{
  "event": "Alesia Campaign",
  "label": "Political consolidation of Gaul",
  "granularity": "composite",
  "date_range": "-52-06 to -52-09",
  "primary_subject": "Imperial expansion",
  "confidence": 0.82
}
```

**Economic Historian Agent:**

```json
{
  "event": "Wealth redistribution from Gallic siege",
  "label": "Economic transfer from Gaul to Rome",
  "granularity": "atomic",
  "date": "-52-09 to -51",
  "primary_subject": "War economy",
  "confidence": 0.75
}
```


### Decision Agent Logic

```python
def resolve_multi_perspective_event(claims):
    """
    Given multiple claims about same historical moment,
    identify anchor event and create perspective edges.
    """
    # Step 1: Group by date overlap
    overlapping_claims = group_by_temporal_overlap(claims)
    
    # Step 2: Identify most granular (atomic preferred)
    anchor = min(overlapping_claims, key=lambda c: c.granularity_rank)
    # granularity_rank: atomic=1, composite=2, period_event=3
    
    # Step 3: Check if other claims are genuinely different events
    # or just different perspectives on same event
    for claim in overlapping_claims:
        if claim == anchor:
            continue
        
        # Same date range + same location = perspective
        if same_spatiotemporal_scope(anchor, claim):
            relationship = "INTERPRETED_AS" if claim.granularity > anchor.granularity else "CAUSED_BY"
            create_edge(anchor, claim, relationship, metadata={
                "perspective": claim.primary_subject,
                "confidence": claim.confidence,
                "agent": claim.agent_id
            })
        
        # Different scope = separate but related event
        else:
            create_edge(anchor, claim, "PART_OF" if anchor.is_subset_of(claim) else "RELATED_TO")
    
    # Step 4: Persist anchor as primary node
    persist_to_graph(anchor, status="APPROVED")
    
    # Step 5: Link perspectives to anchor
    for claim in overlapping_claims:
        if claim != anchor:
            link_as_perspective(anchor, claim)
    
    return anchor
```


### Result in Graph

```cypher
// ANCHOR (most granular)
(battle:Event {
  label: "Battle of Alesia",
  granularity: "atomic",
  date_iso8601: "-0052-09",
  primary_subject_fast: "1020874"  // Military history
})

// PERSPECTIVES (edges to other interpretations)
(battle)-[:INTERPRETED_AS {
  perspective: "political",
  agent: "political_historian_llm",
  confidence: 0.82,
  interpretation: "Political consolidation act"
}]->(political_consolidation:SubjectConcept)

(battle)-[:ECONOMIC_CONSEQUENCE {
  perspective: "economic", 
  agent: "economic_historian_llm",
  confidence: 0.75,
  interpretation: "Wealth transfer event"
}]->(wealth_transfer:SubjectConcept)

// COMPOSITE CONTEXT
(battle)-[:PART_OF]->(alesia_campaign:Event {
  granularity: "composite",
  start: "-0052-06",
  end: "-0052-09"
})

(alesia_campaign)-[:PART_OF]->(gallic_wars:Event {
  granularity: "composite",
  start: "-0058",
  end: "-0050"
})
```


***

## ADVANTAGES OF YOUR APPROACH

### 1. **Query Efficiency**

Start specific, expand to context:

```cypher
// Fast: Find atomic event, traverse outward
MATCH (e:Event {label: "Assassination of Tiberius Gracchus", granularity: "atomic"})
OPTIONAL MATCH (e)-[:PART_OF*1..2]->(context:Event)
RETURN e, context

// Slow: Start at period, traverse inward to thousands of events
MATCH (period:Event {label: "Late Roman Republic"})
MATCH (period)<-[:PART_OF*1..5]-(event:Event)
RETURN event  // Returns 10,000+ events
```


### 2. **Historiographical Transparency**

Competing interpretations are **visible**, not suppressed:

```cypher
MATCH (e:Event {label: "Battle of Alesia"})
MATCH (e)-[r:INTERPRETED_AS]->(interpretation)
RETURN r.perspective, r.confidence, r.agent
```

Output:


| Perspective | Confidence | Agent |
| :-- | :-- | :-- |
| Political consolidation | 0.82 | political_historian |
| Wealth transfer | 0.75 | economic_historian |
| Military dominance | 0.88 | military_historian |

User sees: "Historians view this event from multiple angles, all preserved."

### 3. **Provenance Clarity**

Each perspective edge records **who made the claim**:

```json
{
  "edge": {
    "type": "INTERPRETED_AS",
    "from": "battle_alesia",
    "to": "political_consolidation_concept",
    "metadata": {
      "agent": "political_historian_llm_v2",
      "timestamp": "2025-12-12T16:45:00Z",
      "sources": ["Plutarch Life of Caesar", "Dio Cassius"],
      "confidence": 0.82,
      "reasoning": "Caesar's Gallic campaigns served to enhance political standing in Rome"
    }
  }
}
```


### 4. **Scales to Complexity**

Single event can have 5+ perspectives without graph bloat:

```
(atomic_event)-[:SUBJECT_OF]->(subject_1)
              -[:SUBJECT_OF]->(subject_2)
              -[:INTERPRETED_AS]->(concept_1)
              -[:INTERPRETED_AS]->(concept_2)
              -[:PART_OF]->(composite_event)
              -[:CAUSED]->(outcome_event)
```

All queryable, all attributed, no duplicates.

***

## FORMALIZATION: Add to md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md

```markdown
## Event Granularity Property

All Event nodes MUST include `granularity` property:

| Value | Definition | Example | Agent Behavior |
|-------|------------|---------|----------------|
| `atomic` | Single discrete moment, observable, short duration (â‰¤7 days) | "Assassination of Julius Caesar" | **Default anchor for multi-perspective claims** |
| `composite` | Collection of atomic events, explicit start/end | "Gallic Wars", "Punic Wars" | Link atomic events via -[:PART_OF]-> |
| `period_event` | Historiographical construct, interpretive, vague boundaries | "Fall of Roman Republic", "Crisis of Third Century" | Use only when sources explicitly frame it as period |
| `macro_event` | Abstract causal/thematic grouping, no specific dates | "Roman Expansion", "Hellenization" | Avoid; use Period nodes instead |

## Multi-Perspective Event Resolution Rule

When multiple agents generate claims about overlapping spatiotemporal scope:

1. **Identify most granular event** (atomic > composite > period_event)
2. **Create anchor node** from most granular claim
3. **Create perspective edges** from anchor to other interpretations:
   - Use `-[:INTERPRETED_AS]->` for historiographical framing
   - Use `-[:PART_OF]->` for composite events containing anchor
   - Use `-[:CAUSED]->` or `-[:PRECEDED_BY]->` for causal sequences
4. **Preserve all perspective metadata** (agent, confidence, reasoning)
5. **Link all perspectives to appropriate Subject nodes**

### Example Decision Flow

```

Input: 3 claims about "Gracchi reforms"

Claim A: "Assassination of Tiberius" (atomic, -133-06)
Claim B: "Land redistribution program" (composite, -133 to -121)
Claim C: "Constitutional crisis" (period_event, -133 to -27)

Decision:

1. Anchor = Claim A (most granular)
2. Create node: (assassination:Event {granularity: "atomic"})
3. Create edges:
    - (assassination)-[:PART_OF]->(land_reform:Event {granularity: "composite"})
    - (assassination)-[:TRIGGERED]->(crisis:Event {granularity: "period_event"})
4. Multi-subject links:
    - (assassination)-[:SUBJECT_OF]->(political_violence:Subject)
    - (land_reform)-[:SUBJECT_OF]->(agrarian_economics:Subject)
    - (crisis)-[:SUBJECT_OF]->(constitutional_law:Subject)
```

---

## NEXT STEP: Update Decision Agent Spec

Add to your `decision_agent_spec.md`:

```


## Multi-Perspective Event Resolution

### Detection

When claims have:

- Temporal overlap â‰¥ 50% of shorter event's duration
- Same primary location
- Different primary subjects OR different granularities


### Action

1. Classify each claim's granularity (atomic/composite/period_event/macro_event)
2. Select **atomic** event as anchor (if present)
3. If no atomic event, select most specific (shortest duration)
4. Create anchor node with status="APPROVED"
5. Create perspective edges from anchor to other claims
6. Record all agent perspectives in edge metadata
7. Link each claim to appropriate Subject backbone

### Edge Types for Perspectives

- `INTERPRETED_AS`: Historiographical framing (economic vs political lens)
- `PART_OF`: Anchor is subset of composite event
- `CAUSED`: Causal relationship between events
- `TRIGGERED`: Anchor initiated broader process
- `RELATED_TO`: Thematically connected but distinct events

```

---

This is **elegant** because:
1. No forced choice of "true" interpretation
2. Atomic events are queryable entry points
3. All historiographical perspectives preserved
4. Graph structure enforces clarity about granularity
5. Scales to complex multi-agent scenarios

Want me to draft the full `event_granularity_specification.md` with examples from your Roman Republic domain?
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_17][^3_18][^3_19][^3_2][^3_20][^3_21][^3_22][^3_23][^3_24][^3_25][^3_26][^3_27][^3_28][^3_29][^3_3][^3_30][^3_31][^3_32][^3_33][^3_34][^3_35][^3_36][^3_37][^3_38][^3_4][^3_5][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">â‚</div>

[^3_1]: https://masa.hypotheses.org/files/2019/10/1.-CIDOC-CRM-Intro-5.pdf
[^3_2]: https://academic.oup.com/jcde/article/12/1/53/7917624
[^3_3]: https://aclanthology.org/2024.emnlp-main.298
[^3_4]: https://ieeexplore.ieee.org/document/10150587/
[^3_5]: https://www.tandfonline.com/doi/full/10.1080/00207543.2023.2219345
[^3_6]: https://arxiv.org/abs/2408.15293
[^3_7]: https://ieeexplore.ieee.org/document/10319698/
[^3_8]: https://www.techscience.com/csse/v44n3/49146
[^3_9]: https://arxiv.org/abs/2305.18675
[^3_10]: https://www.semanticscholar.org/paper/6d62164a2c0c8a0407710971d45b6db1cc3868f6
[^3_11]: https://dl.acm.org/doi/10.1145/3543507.3587428
[^3_12]: http://arxiv.org/pdf/2309.12908.pdf
[^3_13]: https://arxiv.org/html/2409.10294
[^3_14]: https://arxiv.org/pdf/2404.16405.pdf
[^3_15]: https://arxiv.org/html/2503.11227v2
[^3_16]: http://arxiv.org/pdf/2210.10709v4.pdf
[^3_17]: https://aclanthology.org/2021.acl-long.60.pdf
[^3_18]: http://arxiv.org/pdf/2404.00209.pdf
[^3_19]: http://arxiv.org/pdf/2409.04452.pdf
[^3_20]: https://knowledgegraph.dev/article/Top_10_Ontology_Design_Patterns_for_Knowledge_Graphs.html
[^3_21]: https://arxiv.org/html/2409.10294v1
[^3_22]: https://www.falkordb.com/blog/how-to-build-a-knowledge-graph/
[^3_23]: https://www.sciencedirect.com/science/article/abs/pii/S0957417423014550
[^3_24]: https://aclanthology.org/2024.emnlp-main.298.pdf
[^3_25]: https://arxiv.org/abs/2005.14552
[^3_26]: http://www.loa.istc.cnr.it/wp-content/uploads/2021/05/FOIS2020.pdf
[^3_27]: https://www.nature.com/articles/s41598-025-00446-z
[^3_28]: https://research.tue.nl/files/174980069/Esser_Fahland2021_Article_Multi_DimensionalEventDataInGr.pdf
[^3_29]: https://linked.art/model/profile/class_analysis/
[^3_30]: https://neo4j.com/blog/knowledge-graph/what-is-knowledge-graph/
[^3_31]: http://arxiv.org/pdf/2005.14552.pdf
[^3_32]: https://dl.acm.org/doi/10.1007/978-981-96-6591-4_7
[^3_33]: https://hanvanderaa.com/wp-content/uploads/2022/09/ICPMWS2022-multi-perspective-identification-of-event-groups-for-event-abstraction.pdf
[^3_34]: https://cidoc-crm.org/cidoc-crm/
[^3_35]: https://kodu.ut.ee/~dumas/pubs/er2018comparison.pdf
[^3_36]: https://cidoc-crm.org/html/cidoc_crm_v6.2.1.html
[^3_37]: https://dl.acm.org/doi/10.1145/2813448.2813520
[^3_38]: https://cidoc-crm.org/sites/default/files/CIDOC%20CRM_v.7.0.1_%2018-10-2020.pdf

---

# Event Granularity Specification for Chrystallum

## Top-Level Takeaway

Model **one core historical event** at the **most granular level that is historically meaningful**, then connect all broader narratives and perspectives to that event via well-typed edges. This keeps queries anchored, preserves historiographical nuance, and scales across agents and subjects.

***

## 1. Goals of the Granularity Spec

This specification defines how Chrystallum:

- Decides **what counts as â€œone eventâ€**
- Chooses the **anchor event** when multiple perspectives exist
- Connects **composite, period-wide, and macro interpretations** to that anchor
- Handles **multi-subject and multi-agent** contributions without duplication or loss of nuance

Target domain example: **Roman Republic**, but the patterns are general.

***

## 2. Event Granularity Levels

All `:Event` nodes MUST carry a `granularity` property.

### 2.1 Allowed Granularity Values

| Value           | Definition                                                     | Typical Duration              | Example (Roman)                            |
|----------------|-----------------------------------------------------------------|-------------------------------|--------------------------------------------|
| `atomic`       | Single discrete, historically observable happening              | Seconds to days (â‰¤ 7 days)    | Assassination of Caesar (44 BCE); Crossing the Rubicon (49 BCE) |
| `composite`    | Named grouping of multiple atomic events                        | Weeks to years                | Gallic Wars; Gracchi Land Reforms         |
| `period_event` | Historiographical construct spanning larger intervals           | Years to decades              | Fall of the Roman Republic; Crisis of the Third Century |
| `macro_event`  | High-level, abstract process with no sharp temporal boundaries  | Decades to centuries          | Roman Expansion; Hellenization             |

In Cypher:

```cypher
CREATE (e:Event {
  qid: "Q161954",
  label: "Crossing of the Rubicon",
  date_iso8601: "-0049-01-10",
  cidoc_class: "E5_Event",
  granularity: "atomic",
  unique_id: "Q161954_EVENT_RUBICON"
});
```


***

## 3. Classification Rules for Agents

Agents that propose new events MUST classify granularity using these rules.

### 3.1 Classification Algorithm (Conceptual)

Inline pseudo-logic:

```python
def classify_event_granularity(event):
    if event.has_specific_datetime() and event.duration_days <= 7:
        return "atomic"
    if event.references_multiple_sub_events() and event.duration_days > 7:
        return "composite"
    if event.is_historiographical_label() and event.duration_years >= 5:
        return "period_event"
    if event.is_abstract_process() and not event.has_precise_dates():
        return "macro_event"
    # Fallback: choose most conservative, lower granularity
    return "atomic"
```

Key tests:

- **Atomic**: specific date or very narrow range; specific participants; direct action.
- **Composite**: explicit start/end, multiple parts; commonly used as a â€œcampaignâ€ or â€œreform programâ€.
- **Period-event**: historians name a span as â€œX crisis/eraâ€; used as interpretive container.
- **Macro-event**: very broad processes (often better represented as Period nodes instead).

***

## 4. Anchor Event Principle

When multiple claims describe what is essentially the same historical happening:

1. Identify **all overlapping claims** (time + place overlap).
2. Pick the **most granular** event as the **anchor**:
    - Prefer `atomic` over `composite` over `period_event` over `macro_event`.
    - If multiple `atomic` events conflict, trigger debate/duplicate logic (your existing decision agent).
3. All other events become **context, perspectives, or containers** around the anchor.

### 4.1 Example: The Gracchi (133 BCE)

Claims:

- Claim A (Political SME): â€œAssassination of Tiberius Gracchusâ€ â€“ `atomic`
- Claim B (Economic SME): â€œGracchi Land Reformsâ€ â€“ `composite`
- Claim C (Constitutional SME): â€œOnset of Late Republic Constitutional Crisisâ€ â€“ `period_event`

Resolution:

- **Anchor** = Assassination event (`atomic`)
- `Gracchi Land Reforms` = composite, containing multiple atomic events (including the assassination)
- `Constitutional Crisis` = period_event, interpretive backdrop

Cypher sketch:

```cypher
// Anchor
CREATE (assassination:Event {
  label: "Assassination of Tiberius Gracchus",
  date_iso8601: "-0133-06-10",
  granularity: "atomic",
  cidoc_class: "E5_Event"
});

// Composite context
CREATE (reforms:Event {
  label: "Gracchi Land Reforms",
  start_year: -133,
  end_year: -121,
  granularity: "composite"
});

// Period-level interpretation
CREATE (crisis:Event {
  label: "Late Republic Constitutional Crisis",
  start_year: -133,
  end_year: -27,
  granularity: "period_event"
});

// Granularity edges
CREATE (assassination)-[:PART_OF]->(reforms);
CREATE (assassination)-[:TRIGGERED]->(crisis);
```


***

## 5. Multi-Subject, Multi-Perspective Modeling

Different SMEs and subjects (political, economic, military, social) can all speak about the **same anchor event**.

### 5.1 Multi-Subject Linking

For anchor `assassination`:

```cypher
MATCH (assassination:Event {label: "Assassination of Tiberius Gracchus"})

// Political violence subject
CREATE (assassination)-[:SUBJECT_OF]->(:Subject {
  label: "Political violence",
  fast_id: "1069240"
});

// Agrarian reform subject
CREATE (reforms:Subject {
  label: "Agrarian reform",
  fast_id: "HB_agrarian"
});
CREATE (assassination)-[:SUBJECT_OF]->(reforms);
```

The same event is legitimately â€œaboutâ€ multiple subjects.

### 5.2 Perspective Edges

Different SME agents contribute **interpretive perspectives** as edges, not new duplicate events.

```cypher
// Political interpretation
CREATE (assassination)-[:INTERPRETED_AS {
  perspective: "political",
  confidence: 0.86,
  agent: "political_historian_llm",
  reasoning: "Senateâ€™s violent response to popular sovereignty challenge"
}]->(:SubjectConcept {label: "Constitutional crisis"});

// Economic interpretation
CREATE (assassination)-[:ECONOMIC_CONSEQUENCE {
  perspective: "economic",
  confidence: 0.78,
  agent: "economic_historian_llm",
  reasoning: "Conflict over redistribution of ager publicus"
}]->(:SubjectConcept {label: "Elite wealth protection"});
```

The anchor remains a single event node; perspectives grow as **edges and attached concepts**.

***

## 6. Event Hierarchy Patterns

To standardize how events relate across granularities, use these relationship patterns.

### 6.1 Granularity Hierarchy

- `(:Event {granularity: "atomic"})-[:PART_OF]->(:Event {granularity: "composite"})`
- `(:Event {granularity: "composite"})-[:PART_OF]->(:Event {granularity: "period_event"})`
- `(:Event {granularity: "period_event"})-[:PART_OF]->(:Period)` (your Period backbone)

Example: Caesarâ€™s civil war chain:

```cypher
// Atomic
CREATE (rubicon:Event { label: "Crossing of the Rubicon", granularity: "atomic" });
CREATE (pharsalus:Event { label: "Battle of Pharsalus", granularity: "atomic" });

// Composite
CREATE (civil_war:Event { label: "Caesar's Civil War", granularity: "composite" });

// Period
MATCH (late_republic:Period { label: "Late Roman Republic" });

// Edges
CREATE (rubicon)-[:PART_OF]->(civil_war);
CREATE (pharsalus)-[:PART_OF]->(civil_war);
CREATE (civil_war)-[:PART_OF]->(late_republic);
```


### 6.2 Temporal \& Causal Chains

Combine granularity with your existing causal edges:

```cypher
CREATE (rubicon)-[:PRECEDED_BY]->(previous_event);
CREATE (rubicon)-[:CAUSED {confidence: 0.92}]->(civil_war);
CREATE (civil_war)-[:CAUSED {confidence: 0.88}]->(republic_fall:Event { label: "Fall of the Roman Republic", granularity: "period_event" });
```


***

## 7. Agent Resolution Logic for Overlapping Claims

When multiple agents propose overlapping events, the **decision agent** applies granularity logic.

### 7.1 Input Pattern

Agents submit JSON like:

```json
{
  "entity_type": "Event",
  "label": "Gracchi Land Reforms",
  "temporal": { "start_year": -133, "end_year": -121 },
  "location_qid": "Q220", 
  "granularity_hint": "composite",
  "subject_fast": "HB_agrarian",
  "confidence": 0.84,
  "agent": "economic_historian_llm"
}
```

Another agent:

```json
{
  "entity_type": "Event",
  "label": "Assassination of Tiberius Gracchus",
  "date_iso8601": "-0133-06-10",
  "location_qid": "Q220",
  "granularity_hint": "atomic",
  "subject_fast": "political_violence",
  "confidence": 0.90,
  "agent": "political_historian_llm"
}
```


### 7.2 Resolution Steps (Conceptual)

1. **Group by temporal + spatial overlap**
    - Same place, overlapping dates â†’ candidate group.
2. **Classify each claimâ€™s granularity** (using rules in Â§3).
3. **Choose anchor**:
    - If any `atomic` present â†’ pick highest-confidence `atomic`.
    - Else pick shortest duration event.
4. **For non-anchor claims**:
    - If their timespan contains anchor â†’ `anchor-[:PART_OF]->composite`.
    - If they are historiographical/periodic â†’ `anchor-[:TRIGGERED|CAUSED]->period_event`.
    - If they are clearly distinct episodes â†’ keep as separate events, connected with `PRECEDED_BY/RELATED_TO`.

This logic plugs into your existing duplicate/additive/replacement decision agent; granularity is an additional axis it uses.

***

## 8. Query Patterns Enabled

### 8.1 â€œShow me everything about the Gracchi crisis, but keep it manageableâ€

```cypher
MATCH (crisis:Event {label: "Late Republic Constitutional Crisis"})
MATCH (atomic:Event {granularity: "atomic"})-[:PART_OF*1..2]->(crisis)
RETURN atomic.label, atomic.date_iso8601
ORDER BY atomic.date_iso8601;
```


### 8.2 â€œGive me all perspectives on Alesiaâ€

```cypher
MATCH (battle:Event {label: "Battle of Alesia"})
OPTIONAL MATCH (battle)-[r]->(concept:SubjectConcept)
WHERE type(r) IN ["INTERPRETED_AS", "ECONOMIC_CONSEQUENCE"]
RETURN r.perspective, r.confidence, concept.label, r.agent;
```


### 8.3 â€œList composite events in Late Roman Republicâ€

```cypher
MATCH (period:Period {label: "Late Roman Republic"})
MATCH (e:Event {granularity: "composite"})-[:PART_OF]->(period)
RETURN e.label, e.start_year, e.end_year;
```


***

## 9. Integration with Your Backbone

This spec must align with:

- **Period backbone** â€“ Periods are temporal containers, often above `period_event`.
- **Place backbone** â€“ Place hierarchies apply at all granularities.
- **Subject backbone (LCC/LCSH/FAST)** â€“ Multiple subject links per event allowed and encouraged.

Example of full integration for a single anchor event:

```cypher
MATCH (period:Period {label: "Late Roman Republic"})
MATCH (rome:Place {label: "Rome"})
MATCH (subject1:Subject {label: "Political violence"})
MATCH (subject2:Subject {label: "Agrarian reform"})

CREATE (assassination:Event {
  qid: "QXXXX",
  label: "Assassination of Tiberius Gracchus",
  date_iso8601: "-0133-06-10",
  granularity: "atomic",
  cidoc_class: "E5_Event"
});

CREATE (assassination)-[:DURING]->(period);
CREATE (assassination)-[:LOCATED_IN]->(rome);
CREATE (assassination)-[:SUBJECT_OF]->(subject1);
CREATE (assassination)-[:SUBJECT_OF]->(subject2);
```


***

## 10. Implementation Checklist

To operationalize this spec:

- Add `granularity` as **required** property in the Event node schema.
- Extend the **decision agent**:
    - Incorporate granularity classification.
    - Use granularity in duplicate/additive/replacement decisions.
- Update agent prompts:
    - Tell SME agents to propose `granularity_hint` and explain why.
- Add tests:
    - Given a set of overlapping Roman events, verify the anchor selection and edge wiring is as specified.
- Document examples:
    - Gracchi, Rubicon, Sullaâ€™s dictatorship, Caesarâ€™s assassination as canonical patterns.

***

If you want, the next step could be a concrete **`event_granularity_spec.md` file** in your repo with this content slimmed into repo-ready form (headings/phrasing tailored to your style) plus 2â€“3 more worked Roman examples.


