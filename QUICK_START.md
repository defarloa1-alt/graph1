# Chrystallum: Quick Start Guide

**Last Updated:** February 14, 2026  
**Purpose:** 5-minute overview for new agents deploying Chrystallum  
**Audience:** AI agents, custom GPT instances, human operators

---

## What is Chrystallum?

Chrystallum is a **federated knowledge graph system** designed to capture historical claims—particularly genealogical, political, military, and social relationships—with:

- ✅ **Multi-source authority tracking** (Wikidata, LCSH, FAST, custom)
- ✅ **Phase-based claim validation** (Metrics-only promotion, fallacy flagging)
- ✅ **Multi-faceted claims** (Same relationship can be evaluated across 17 different contexts)
- ✅ **Deep relationship discovery** (Non-obvious connections, 6-8 hops deep)
- ✅ **Federated returns** (QIDs, multilingual labels, CIDOC-CRM types, CRMinf belief tracking)

**Example:** "Caesar married Calpurnia" isn't just a genealogical fact—it's also a political alliance (different confidence baselines), economic partnership (dowry implications), and social/demographic record. Chrystallum captures all 4 perspectives.

---

## 4 Core Concepts

### 1. **QIDs (Wikidata Identifiers)**
Each person, place, or event has a Wikidata ID (e.g., Q1048 = Julius Caesar).

- System resolves mentions like "Caesar" → Q1048 (LLM-assisted Wikidata search)
- If no Wikidata match: Creates **provisional QID** (`local_entity_{hash}`) with note
- Authority tracking: Also captures LCSH (sh-prefix) and FAST (fst-prefix) IDs

**For agents:** Treat QIDs as unique identifiers; use `authority_ids` JSON field for non-Wikidata sources.

### 2. **Facets (Multi-Context Evaluation)**
17 facets represent different evaluation perspectives:

| Facet | Use Case | Example |
|-------|----------|---------|
| `genealogical` | Parentage, siblings, marriage | "Parent of" relationships |
| `military` | Conflicts, commands, participation | "Fought with/against" |
| `political` | Offices, authority, alliances | "Held office", "Supported" |
| `social` | Social class, gens membership | "Member of gens Julia" |
| `demographic` | Birth/death, age, population | Death year, birthplace |
| `diplomatic` | Treaties, negotiations | "Negotiated peace" |
| `cultural` | Language, customs, identity | "Spoke Latin" |
| `communication` | Messaging, propaganda, rhetoric | "Gave speech about..." |
| `religious` | Priesthoods, beliefs, worship | "Priest of Jupiter" |
| `intellectual` | Education, philosophy, authored | "Taught at Academy" |
| `economic` | Commerce, land, wealth | "Owned estates" |
| `temporal` | Time periods, calendars, eras | "Served during Punic Wars" |
| `classification` | Categories, taxonomies | "Categorized as: patrician" |
| `spatial` | Geography, territories, distances | "Governed province" |
| `technological` | Tools, techniques, innovation | "Used Roman roads" |
| `organizational` | Groups, hierarchies, ranks | "Member of Senate" |
| `patronage` | Supporting relationships, mentorship | "Supported by Caesar" |

**For agents:** Choose 1-4 most relevant facets per claim; use per-facet confidence baselines.

### 3. **Roles (Edge Qualifiers)**
Relationships are qualified with roles from a **70+ canonical registry**:

- Military roles: `commander`, `legate`, `centurion`, `soldier`
- Political roles: `consul`, `tribune`, `censor`, `praetor`, `senator`,`dictator`
- Religious roles: `priest`, `pontifex`, `augur`, `vestal`
- Family roles: `parent`, `child`, `sibling`, `spouse`, `guardian`
- Social roles: `patron`, `client`, `ally`, `rival`, `servant`
- Intellectual roles: `teacher`, `student`, `author`, `philosopher`

**For agents:** Validate roles against registry; fuzzy matching if exact term not found. System flags unrecognized roles and suggests alternatives.

### 4. **Authority (Source Tracking)**
Every claim captures its source:

- `authority_source`: "Wikidata", "Wikipedia", "LCSH", "Custom", "Scholarly", "AI-generated"
- `authority_ids`: JSON array of external IDs
  ```json
  {
    "wikidata": ["Q1048"],
    "lcsh": ["sh89002184"],
    "fast": ["fst00064326"],
    "wikipedia": ["Julius_Caesar"]
  }
  ```
- `confidence`: AI system's confidence (0.0–1.0)
- `posterior_probability`: Bayesian belief after reconciling with other sources
- `minf_belief_id`: CRMinf belief node ID (for multi-source justification tracking)

**For agents:** Always capture source; multiple authorities increase posterior probability.

---

## 5 Quick Examples

### Example 1: Simple Genealogy
```
INPUT:  "Marcus Brutus was son of Servilia"
OUTPUT:
  relationship: PARENT_OF (inverse: CHILD_OF)
  from: Q2176 (Servilia)
  to: Q83416 (Marcus Brutus)
  facets: [genealogical, demographic, social]
  confidence: 0.95
  posterior: 0.98 (Wikidata + Wikipedia agree)
  authority: Wikidata
  promoted: true (metrics-only)
```

### Example 2: Political Position with Role
```
INPUT:  "Caesar was consul in 59 BC"
OUTPUT:
  relationship: HELD_OFFICE
  entity: Q1048 (Julius Caesar)
  role: consul
  temporal: {start_year: -59, end_year: -59}
  facets: [political, social, temporal]
  confidence: 0.98
  posterior: 1.0 (High consensus)
  authority: Wikidata
  promoted: true
```

### Example 3: Multi-Facet Claim
```
INPUT:  "Caesar's marriage to Calpurnia was political alliance"
OUTPUT:
  relationship: SPOUSE_OF
  from: Q1048 (Julius Caesar)
  to: Q2297 (Calpurnia)
  facets: {
    genealogical: {confidence: 0.92, baseline: 0.92},
    political: {confidence: 0.88, baseline: 0.92},
    social: {confidence: 0.85, baseline: 0.90},
    economic: {confidence: 0.75, baseline: 0.85}
  }
  avg_confidence: 0.85
  posterior: 0.82
  authority: Wikidata + Scholarly consensus
  promoted: true (all >= 0.90? No → still true; metrics-only)
```

### Example 4: Provisional QID (No Wikidata Match)
```
INPUT:  "Titus Labienus was Caesar's legate"
OUTPUT:
  entity: local_entity_8a3f2e10
  label: "Titus Labienus"
  reason: No Wikidata match above 0.75 threshold
  note: "Minor historical figure, mentioned in Wikidata entries about Caesar"
  authority_source: "Wikipedia article about Caesar's generals"
  confidence: 0.68
  posterior: 0.71 (One source)
  promoted: false (posterior < 0.90)
  next_steps: "Flag for historian review" OR "Search LCSH/FAST"
```

### Example 5: Fallacy Detected (Flagged, Not Blocked)
```
INPUT:  "Hannibal's arrival in Italy triggered the Second Punic War"
OUTPUT:
  relationship: TRIGGERED_WAR (inferred from article narrative)
  from: Q8458 (Hannibal)
  to: Q210089 (Second Punic War)
  confidence: 0.62
  posterior: 0.58
  fallacy_detected: {
    type: "Post hoc ergo propter hoc",
    intensity: "HIGH",
    reasoning: "Assumes temporal causality without establishing direct cause-effect"
  }
  promoted: false (posterior < 0.90)
  note: "HIGH-intensity fallacy flagged. Flag for human review. Relationship not blocked."
  action: "Human reviewer decides: (a) Keep as claim + flag, (b) Separate into temporal + causal components, (c) Reject"
```

---

## Common Patterns: Do's & Don'ts

### ✅ DO:
- Capture exact year/date if available (e.g., `birth_year: -100`)
- Use canonical role names (`consul`, not `chief magistrate`)
- Include multiple facets when relevant (genealogy + politics)
- Provide authority sources (increases posterior)
- Flag high-confidence spatial relationships (geography is stable)

### ❌ DON'T:
- Use ad-hoc roles (system will fuzzy match; provide canonical first)
- Create claims without temporal anchors (missing context)
- Ignore fallacy flags (they're informational; promote anyway if metrics support)
- Mix interpretive claims with descriptive (label clearly)
- Assume provisional QIDs are errors (note for historian review, continue)

### 🤔 UNCERTAIN:
- Speculative historical claims? Capture with lower confidence (0.50–0.75); flag intensity HIGH
- Multiple conflicting sources? Use posterior probability (system reconciles)
- Role variations across regions? Capture all variants; map to canonical in post-processing
- Anchronistic relationships (e.g., "Caesar met Napoleon")? Create separate temporal periods; flag if crossing

---

## Reference & Details

For comprehensive information, consult:

| Document | Purpose |
|----------|---------|
| [SCHEMA_REFERENCE.md](SCHEMA_REFERENCE.md) | Complete node types, properties, constraints, 17-facet definitions |
| [RELATIONSHIP_TYPES_SAMPLE.md](RELATIONSHIP_TYPES_SAMPLE.md) | 312+ relationships with P-values, per-facet baselines, aliases |
| [AGENT_EXAMPLES.md](AGENT_EXAMPLES.md) | 11 detailed usage examples with input/output patterns |
| [ARCHITECTURE_OPTIMIZATION_REVIEW.md](ARCHITECTURE_OPTIMIZATION_REVIEW.md) | Phase 2 roadmap, Neo4j optimization strategies, processing pipelines |
| [role_qualifier_reference.json](role_qualifier_reference.json) | 70+ canonical roles with CIDOC-CRM types, context facets, aliases |
| [relationship_facet_baselines.json](relationship_facet_baselines.json) | 50+ relationships with per-facet confidence overrides |
| [PHASE_1_DECISIONS_LOCKED.md](PHASE_1_DECISIONS_LOCKED.md) | Phase 1 architectural decisions with rationale |

---

## Integration Checklist

**Getting Started:**

- [ ] Read this Quick Start (5 mins)
- [ ] Review [AGENT_EXAMPLES.md](AGENT_EXAMPLES.md) Examples 1–5 (10 mins)
- [ ] Load [role_qualifier_reference.json](role_qualifier_reference.json) into memory (1 min)
- [ ] Load [relationship_facet_baselines.json](relationship_facet_baselines.json) as lookup table (1 min)
- [ ] Implement basic claim ingestion:
  - [ ] Entity → QID resolution (trust Wikidata first; use provisional as fallback)
  - [ ] Relationship type detection (match against 312 registry)
  - [ ] Facet selection (1–4 most relevant)
  - [ ] Role validation (fuzzy match against 70+ canonical)
  - [ ] Authority capture (source + IDs)
  - [ ] Confidence scoring (0.0–1.0)

**Advanced (Phase 2+):**

- [ ] Implement Bayesian posterior probability
- [ ] CRMinf belief node tracking
- [ ] CIDOC-CRM entity type mapping
- [ ] Temporal index queries
- [ ] Discovery mode (variable-length path traversal)
- [ ] Fallacy detection (HIGH vs. LOW intensity)

---

## Troubleshooting

**Q: I get a provisional QID—is this an error?**  
A: No. Provisional QIDs are normal for obscure historical figures. They're flagged for human review; continue processing. If pattern repeats, escalate to historian.

**Q: Role fuzzy match returns 0.67—promote or reject?**  
A: Check relationship confidence. If overall confidence ≥ 0.90 AND posterior ≥ 0.90 → promote. Fallacies are flagged, not blocked.

**Q: Should I fill all 17 facets?**  
A: No. Use 1–4 most relevant facets. Per-facet baselines apply only to selected facets.

**Q: How do I handle conflicting sources?**  
A: Capture all sources in `authority_ids`. System computes posterior probability (Bayesian reconciliation). Higher consensus = higher posterior.

**Q: What's the difference between `confidence` and `posterior`?**  
A: `confidence` = initial belief (single source). `posterior` = reconciled belief after accounting for all sources and fallacy flags.

---

## Deduplication Workflow (CRITICAL)

**ALWAYS deduplicate before creating claims.** This prevents duplicate edges and reconciles conflicting sources.

### Step 1: Query for Existing Claim

Before creating any relationship, search for it by (source QID, relationship type, target QID, temporal context):

```cypher
// Query pattern: Check if claim exists
MATCH (from:Human {qid: $from_qid})-[rel:PARTICIPATED_IN {facet: $facet}]->(to {qid: $to_qid})
WHERE (rel.start_year IS NULL OR rel.start_year = $start_year)
  AND (rel.end_year IS NULL OR rel.end_year = $end_year)
RETURN rel, rel.confidence, rel.posterior_probability, rel.authority_ids

// Example: Did Caesar participate in Battle of Pharsalus?
MATCH (from:Human {qid: "Q1048"})-[rel:PARTICIPATED_IN {facet: "military"}]->(to {qid: "Q193492"})
WHERE rel.start_year = -48 AND rel.end_year = -48
RETURN rel
```

### Step 2: Decision Logic

**If claim exists:**
- Reconcile confidences (see Bayesian merging below)
- Append new authority source
- Update posterior probability
- Flag if sources conflict (confidence drop)

**If claim doesn't exist:**
- Create new relationship
- Set confidence, posterior, authority_ids
- Assign facet & role

### Step 3: Bayesian Confidence Merging

When merging two sources for the same claim:

```
prior_confidence = existing_rel.posterior_probability (or 0.50 if none)
new_confidence = incoming_claim.confidence
agreement_factor = 1.0 if sources agree, 0.7-0.9 if slight conflict, 0.3-0.5 if major conflict

merged_confidence = (prior_confidence + new_confidence) / 2 * agreement_factor

posterior = merged_confidence if agreement_factor >= 0.8
posterior = merged_confidence * 0.85 if agreement_factor < 0.8 (apply penalty)
```

**Example:**
- Existing: Wikidata says Caesar was at Pharsalus (confidence 0.95, posterior 0.95)
- New: Wikipedia article says Caesar participated (confidence 0.92)
- Agreement: Both say same thing (agreement_factor = 1.0)
- Merged: (0.95 + 0.92) / 2 * 1.0 = **0.935 posterior**
- Authority: Now has both Wikidata + Wikipedia

**Example with conflict:**
- Existing: Wikidata says Caesar died at -44 (confidence 0.98)
- New: AI says Caesar died at -43 (confidence 0.65, from ambiguous source)
- Agreement: Different years (agreement_factor = 0.4)
- Merged: (0.98 + 0.65) / 2 * 0.4 = **0.326 posterior**
- Flag: "Conflicting sources detected: -44 vs -43"
- Action: Human review required

### Step 4: Authority Reconciliation

Update `authority_ids` JSON:

```json
// Before:
{
  "wikidata": ["Q1048"],
  "confidence_source": "Wikidata"
}

// After adding Wikipedia:
{
  "wikidata": ["Q1048"],
  "wikipedia": ["Julius_Caesar"],
  "confidence_source": "Wikidata + Wikipedia (reconciled)"
}
```

### Common Deduplication Patterns

**Genealogical Claims (high temporal specificity required):**
```cypher
MATCH (parent:Human {qid: $parent_qid})-[rel:PARENT_OF]->(child:Human {qid: $child_qid})
WHERE rel.facet = "genealogical"
RETURN rel
// Temporal context: birth/death years must align
```

**Political Offices (time-bounded):**
```cypher
MATCH (person:Human {qid: $person_qid})-[rel:HELD_OFFICE {role: $role}]->(office:Position)
WHERE rel.start_year <= $query_year AND rel.end_year >= $query_year
RETURN rel
// Example: Was Caesar consul in -59?
```

**Battle Participation (specific event):**
```cypher
MATCH (person:Human {qid: $person_qid})-[rel:PARTICIPATED_IN {facet: "military"}]->(battle {qid: $battle_qid})
WHERE rel.role IS NOT NULL
RETURN rel
// No need to time-bound: battle has fixed date
```

**Gens Membership (lifetime relationship):**
```cypher
MATCH (person:Human {qid: $person_qid})-[rel:MEMBER_OF_GENS]->(gens {qid: $gens_qid})
RETURN rel
// No temporal bounds: lifetime membership
```

### When Deduplication Fails

**Q: What if I find a partial match (same entities, different facet)?**

```
A: Don't merge; keep both. Example:
   - SPOUSE_OF {facet: "genealogical"} = personal marriage
   - SPOUSE_OF {facet: "political"}   = political alliance
   These are independent claims. System tracks both.

Cypher:
   MATCH (a)-[rel:SPOUSE_OF]->(b) RETURN DISTINCT rel.facet
   // May return: ["genealogical", "political", "social"]
```

**Q: What if sources substantially disagree (e.g., +/- 5 years)?**

```
A: Flag for human review; don't auto-merge:

   IF |new_year - existing_year| > 3 THEN
     anterior_probability = 0.50  # Express maximum uncertainty
     flag_intensity = "HIGH"
     action = "Escalate to historian"
   ELSE
     # Assume minor data variance; merge normally
```

**Q: Temporal overlap but different outcomes?**

```
Example: "Caesar defeated Pompey" vs "Pompey defeated Caesar" (same battle, different outcome)

A: Create BOTH as separate claims:
   1. Caesar-[DEFEATED]->Pompey (outcome: victory)
   2. Pompey-[DEFEATED_BY]->Caesar (inverse, same outcome)

   Don't try to merge. Keep both for audit trail.
   Flag: "Contradictory claim outcomes" for human review
```

---

## Support & Escalation

- **Schema questions:** See [SCHEMA_REFERENCE.md](SCHEMA_REFERENCE.md)
- **Relationship questions:** See [RELATIONSHIP_TYPES_SAMPLE.md](RELATIONSHIP_TYPES_SAMPLE.md) + [relationship_facet_baselines.json](relationship_facet_baselines.json)
- **Role questions:** See [role_qualifier_reference.json](role_qualifier_reference.json)
- **Example-based:** See [AGENT_EXAMPLES.md](AGENT_EXAMPLES.md)
- **Architecture/Phase 2:** See [ARCHITECTURE_OPTIMIZATION_REVIEW.md](ARCHITECTURE_OPTIMIZATION_REVIEW.md)

---

**Estimated First Ingestion Time:** 30–60 minutes  
**Estimated Integration Time:** 2–4 hours (basic), 1–2 weeks (advanced with Phase 2 features)
