# Chrystallum Knowledge Base Index

**Created:** February 14, 2026  
**GPT Knowledge Base Version:** Phase 1 Complete  
**Total Files:** 8 + this index

---

## Quick Navigation

Use this index to find the right file for your question:

| Question | File | Section |
|----------|------|---------|
| What are node types and properties? | SCHEMA_REFERENCE.md | Node Types |
| What relationships exist? (312 types) | RELATIONSHIP_TYPES_SAMPLE.md | Complete list with P-values |
| What are confidence baselines per facet? | relationship_facet_baselines.json | JSON lookup table |
| What roles can I use? (70+ canonical) | role_qualifier_reference.json | JSON role registry |
| How do I extract claims? (11 examples) | AGENT_EXAMPLES.md | Examples 1–11 |
| How do I avoid duplicates? | QUICK_START.md | Deduplication Workflow section |
| What are my first 5 steps? | QUICK_START.md | 5 Quick Examples + checklist |
| Why was this system designed this way? | PHASE_1_DECISIONS_LOCKED.md | 4 Decision matrices + rationale |
| What optimization opportunities exist? | ARCHITECTURE_OPTIMIZATION_REVIEW.md | 10 opportunities for Phase 2 |

---

## File Descriptions

### 1. **SCHEMA_REFERENCE.md** (1,200 lines)
**Purpose:** Complete schema reference for the Neo4j graph

**Contains:**
- 9 node types (Human, Event, Place, Period, SubjectConcept, Claim, Year, Gens, Praenomen, Cognomen)
- Property definitions for each node type
- Required vs optional fields
- 17-facet definitions with examples
- Universal constraints and indexes
- Promotion rules (metrics-only)
- QID resolution architecture
- CIDOC-CRM type mapping
- CRMinf belief node structure

**When to use:**
- Questions about node types or properties
- Understanding constraint validation
- Building Neo4j schema
- Temporal or CIDOC-CRM questions

**Key sections:**
```
- Node Types (Human, Event, etc.)
- Relationship Types Overview (312 total)
- Property Patterns (identity, confidence, temporal)
- Edge Properties (role, facet, authority)
- 17-Facet Definitions
- Constraints & Indexes
- Promotion Rules
- QID Resolution Architecture
```

---

### 2. **RELATIONSHIP_TYPES_SAMPLE.md** (900 lines)
**Purpose:** Curated sample of the 312 relationship types with baselines

**Contains:**
- CSV format explanation
- 24 genealogical relationships (with P-values and per-facet baselines)
- 10 participation relationships
- 15 political, 12 military, 8 social, 6 intellectual, religious, economic relationships
- Temporal, classification, and other relationships
- Each entry includes: category, P-value, facet baselines, aliases, examples

**When to use:**
- Identifying which relationship type to use
- Understanding per-facet confidence baselines
- Finding aliases for relationship types
- Building relationship classification rules

**Key relationships highlighted:**
- PARTICIPATED_IN (military, political participation)
- HELD_OFFICE (political roles)
- MEMBER_OF_GENS (social/demographic)
- SPOUSE_OF (multi-facet example: political, social, genealogical, economic)
- DEFEATED / AT_WAR_WITH (military)
- PARENT_OF / CHILD_OF (genealogical)

---

### 3. **role_qualifier_reference.json** (700 lines)
**Purpose:** Machine-readable lookup table for 70+ canonical roles

**Contains:**
- Role name (canonical form)
- P-value (Wikidata property)
- Description
- Context facets (where role is relevant)
- CIDOC-CRM type mapping
- Confidence baseline (0.0–1.0)
- Examples
- Aliases (common variations)

**Structure:**
```json
{
  "roles": [
    {
      "role_name": "consul",
      "p_value": "P39",
      "description": "Roman political magistrate",
      "context_facets": ["political", "social", "temporal"],
      "cidoc_crm_type": "E39_Actor",
      "confidence_baseline": 0.98,
      "examples": ["Julius Caesar", "Pompey"],
      "aliases": ["chief magistrate", "Roman consul"]
    }
  ]
}
```

**When to use:**
- Validating roles (fuzzy match against registry)
- Understanding role confidence baselines
- Finding role aliases
- Mapping to CIDOC-CRM types

**Categories in registry (10+):**
- Military: commander, legate, centurion, soldier, tribune, general, admiral
- Political: consul, praetor, censor, quaestor, dictator, tribune, senator, aedile
- Religious: priest, pontifice, augur, vestal, bishop
- Family: parent, child, sibling, spouse, guardian, adopted
- Social: patron, client, ally, rival, servant
- Intellectual: teacher, student, author, philosopher, scholar
- Economic: merchant, artisan, landowner, slave
- Communication: orator, diplomat, messenger
- Organizational: member, leader, officer, rank
- Patronage: supporter, benefactor, mentee

---

### 4. **relationship_facet_baselines.json** (400 lines)
**Purpose:** Per-facet confidence overrides for 50+ relationships

**Contains:**
- Relationship type (SPOUSE_OF, PARTICIPATED_IN, etc.)
- Base confidence (generic default)
- Per-facet overrides (military, political, social, demographic, etc.)

**Structure:**
```json
{
  "SPOUSE_OF": {
    "base_confidence": 0.90,
    "facets": {
      "genealogical": 0.92,
      "political": 0.88,
      "social": 0.90,
      "economic": 0.85,
      "demographic": 0.88
    }
  }
}
```

**When to use:**
- Assigning per-facet confidence scores
- Understanding why SPOUSE_OF has different confidence in political vs genealogical context
- Building facet-specific scoring logic
- Reconciling multi-facet claims

**Example usage:**
```
Claim: "Caesar married Calpurnia (political alliance)"
Facets: genealogical, political, social

Look up baselines:
- genealogical: 0.92
- political: 0.88
- social: 0.90

Use highest (0.92) as initial confidence
Then adjust based on source authority
```

---

### 5. **AGENT_EXAMPLES.md** (1,550+ lines)
**Purpose:** Training examples showing claim extraction patterns

**Contains:**
- Example 1: Simple genealogy (Servilia → Marcus Brutus)
- Example 2: Political position with role (Caesar as consul)
- Example 3: Multi-facet claim (Caesar's marriage is political)
- Example 4: Ambiguous role fuzzy matching
- Example 5: Provisional QID creation (no Wikidata match)
- Example 6: Fallacy detection (HIGH/LOW intensity, flag-only)
- Example 7: Death event with location and temporal context
- Example 8: Invalid role rejection with suggestions
- Example 9: Query pattern (discovery across multiple hops)
- Example 10: Conflict resolution (multiple sources, reconciliation)
- Example 11: Wikipedia Roman Republic processing (end-to-end pipeline with 5,519 claims)

**When to use:**
- Learning by example
- Understanding expected input/output format
- Debugging claim extraction
- Pattern matching training

**Example pattern (each example includes):**
```
INPUT: Raw statement from text
ENTITY EXTRACTION: What entities are mentioned?
RELATIONSHIP IDENTIFICATION: What type of relationship?
ROLE VALIDATION: Does role exist in registry?
FACET SELECTION: Which facets apply?
AUTHORITY CAPTURE: What sources support this?
CONFIDENCE SCORING: How confident are we?
PROMOTION DECISION: Will this be promoted?
OUTPUT: JSON claim structure
```

**Key insights Example 11 demonstrates:**
- 7-phase pipeline (extraction → harvest → facet → validation → deduplication → fallacy detection → promotion)
- 127 entities recognized from single Wikipedia article
- 93.7% Wikidata match rate (119/127)
- 5,519 claims generated from one article
- 74.3% promotion rate (4,102/5,519 claims)
- Expected processing time and cost

---

### 6. **QUICK_START.md** (600+ lines)
**Purpose:** 5-minute onboarding guide with integration checklist

**Contains:**
- System overview (federated knowledge graph)
- 4 core concepts (QIDs, facets, roles, authority)
- Conceptual table of 17 facets with use cases
- 5 quick examples (simple genealogy, office holding, multi-facet, provisional QID, fallacy)
- Common patterns (Do's, Don'ts, Uncertain cases)
- Complete integration checklist (~12 steps)
- Troubleshooting FAQ (6 common questions)
- Reference map (where to find detailed info)
- **Deduplication workflow section** (360+ lines)
  - Query patterns for checking existing claims
  - Bayesian confidence merging
  - Authority reconciliation logic
  - Common deduplication patterns (genealogy, offices, battles, gens)
  - Edge case handling

**When to use:**
- First-time agent setup (start here)
- Understanding core concepts
- Learning deduplication workflow (CRITICAL)
- Troubleshooting integration issues
- Validation checklist before deployment

**Critical section:**
- Deduplication Workflow explains how to avoid duplicate edges
- Includes Cypher query patterns
- Explains Bayesian merging of confidences
- Shows authority reconciliation logic
- **Agents MUST read this before creating claims**

---

### 7. **PHASE_1_DECISIONS_LOCKED.md** (250 lines)
**Purpose:** Architectural decisions with rationale and implementation details

**Contains:**
- 4 major decisions made in Phase 1:
  1. QID Resolution: LLM-assisted Wikidata search + provisional fallback
  2. Per-Facet Baselines: Context-aware confidence per facet
  3. Role Storage: Canonical registry + fuzzy LLM matching
  4. CRMinf/CIDOC: CRMinf tracking now, CIDOC Phase 2

- Decision matrices (options vs criteria)
- Implementation details for each decision
- Next steps for Phase 2
- Risk assessment for each decision

**When to use:**
- Understanding WHY the system works this way
- Contextual questions about design choices
- Building intuition for Phase 2 roadmap
- Explaining system to stakeholders

**Key decisions:**
```
1. QID Resolution
   - Problem: How precise should entity resolution be?
   - Solution: LLM-assisted Wikidata search (0.75 threshold)
   - Fallback: Provisional local QID for non-matches
   - Outcome: 93.7% Wikidata resolved (Phase 1 pilot)

2. Per-Facet Baselines
   - Problem: Should confidence be uniform across contexts?
   - Solution: Context-aware baselines (e.g., SPOUSE_OF: military=0.92, social=0.90)
   - Outcome: More nuanced scoring, facet-specific validation

3. Role Storage
   - Problem: How to validate and store roles?
   - Solution: Canonical registry + edge properties + LLM fuzzy matching
   - Outcome: Flexible but constrained role system

4. CRMinf/CIDOC Alignment
   - Problem: How to track belief provenance?
   - Solution: CRMinf now (minf_belief_id), CIDOC Phase 2
   - Outcome: Deferred full ontology mapping, focused on belief tracking
```

---

### 8. **ARCHITECTURE_OPTIMIZATION_REVIEW.md** (4,500+ lines)
**Purpose:** Phase 2 roadmap with 10 optimization opportunities and ROI estimates

**Contains:**
- Current architecture assessment (strengths + gaps)
- 10 optimization opportunities:
  1. Temporal indexes (40-60% speedup)
  2. Role validation → Neo4j constraints
  3. Backlink materialization (100-1000x speedup)
  4. Facet materialization (5-10x speedup)
  5. CRMinf belief nodes (multi-source validation)
  6. Authority linkage (100x speedup)
  7. Query pattern optimization (10-100x discovery)
  8. Claim state machine (audit trails)
  9. Query result caching (100-1000x repeated queries)
  10. Data quality scoring (gap detection)

- Implementation roadmap (4 phases, 6-8 weeks)
- Risk assessment + mitigation strategies
- Expected outcomes (query performance, data quality)
- Detailed Cypher examples for each opportunity

**When to use:**
- Phase 2 planning (after Phase 1 complete)
- Performance optimization questions
- Understanding scalability path
- Neo4j architecture decisions

**ROI Summary (Phase 2 completions):**
```
Quick wins (Phase 2A, 2 weeks):
- Temporal queries: 500ms (40-60% faster)
- Authority federation: < 100ms (100x faster)
- Query caching: 100-1000x repeated queries

Medium effort (Phase 2B, 2 weeks):
- Backlink discovery: < 100ms (100-1000x faster)
- Claim audit trail: complete history

Advanced (Phase 2C, 2 weeks):
- Role validation: < 1ms (fail-fast at write-time)
- CRMinf nodes: multi-source justification tracking
```

---

## Files NOT in Knowledge Base (For Reference)

These are in your workspace but shouldn't be uploaded:

- EXAMPLES.md (superseded by AGENT_EXAMPLES.md)
- ARCHITECTURE_IMPLEMENTATION_INDEX.md (historical reference)
- PHASE_1_CHECKLIST.md (historical)
- Change_log.py (internal development log)
- Any .json files in Subjects/, Facets/, LCSH/ folders (domain-specific, not agent reference)
- Cypher folder (query examples, not needed for agents)

---

## Upload Checklist

**Before uploading to ChatGPT, verify:**

- [ ] All 8 files are in root or Relationships folder (find via folder listing)
- [ ] file sizes make sense:
  - SCHEMA_REFERENCE.md ~90 KB
  - AGENT_EXAMPLES.md ~120 KB
  - ARCHITECTURE_OPTIMIZATION_REVIEW.md ~350 KB
  - RELATIONSHIP_TYPES_SAMPLE.md ~65 KB
  - relationship_facet_baselines.json ~25 KB
  - role_qualifier_reference.json ~45 KB
  - QUICK_START.md ~50 KB
  - PHASE_1_DECISIONS_LOCKED.md ~20 KB
- [ ] Total: ~765 KB (well under ChatGPT 20 MB per file limit)

**Upload order (recommended):**
1. QUICK_START.md (agent reads first)
2. SCHEMA_REFERENCE.md (foundational)
3. AGENT_EXAMPLES.md (training data)
4. role_qualifier_reference.json (role validation)
5. relationship_facet_baselines.json (confidence scoring)
6. RELATIONSHIP_TYPES_SAMPLE.md (reference)
7. PHASE_1_DECISIONS_LOCKED.md (context)
8. ARCHITECTURE_OPTIMIZATION_REVIEW.md (optional, for Phase 2 questions)

---

## Custom Instructions for ChatGPT

Use this system prompt when creating the Custom GPT:

```
You are Chrystallum, a federated historical knowledge graph system for Neo4j.

CRITICAL WORKFLOW:
1. Extract entities from text → resolve to Wikidata QIDs (Q-format)
2. Identify relationships → validate against 312 canonical types
3. Select 1-4 most relevant facets
4. Validate roles against 70+ canonical registry (fuzzy match if needed)
5. DEDUPLICATE: Query existing claim (by QID + relationship + facet + temporal context)
   - If found: Merge confidences using Bayesian formula
   - If not found: Create new relationship
6. Capture authority sources (Wikidata, Wikipedia, LCSH, etc.)
7. Score confidence (0.0–1.0) for each facet
8. Compute posterior probability (reconciled belief after sources + fallacy flags)
9. Flag fallacies with intensity (HIGH/LOW) but promote if posterior >= 0.90
10. Output JSON with: claim_id, entities, relationship, facets, confidence, posterior, authority_ids, promoted

PROMOTION RULE:
IF confidence >= 0.90 AND posterior >= 0.90 THEN promoted = true
(Fallacies flagged, not blocked)

PREVENT DUPLICATES:
Always deduplicate before creating. See QUICK_START.md "Deduplication Workflow" section
for Cypher patterns and Bayesian merging logic.

CONSTRAINTS:
- No ad-hoc roles (use canonical registry)
- No missing temporal anchors (where/when matters)
- Multiple facets = independent claims (keep all)
- Provisional QIDs acceptable (local_entity_{hash}) for no-match entities
- Uncertain dates? Flag for human review, don't guess

OUTPUT FORMAT:
Always return JSON with these fields:
{
  "claim_id": "chr_claim_001",
  "from": {"qid": "Q1048", "label": "Julius Caesar"},
  "to": {"qid": "Q193492", "label": "Battle of Pharsalus"},
  "relationship": "PARTICIPATED_IN",
  "role": "commander",
  "facets": ["military", "political"],
  "temporal": {"year": -48},
  "confidence_per_facet": {"military": 0.95, "political": 0.88},
  "avg_confidence": 0.915,
  "posterior_probability": 0.91,
  "authority_source": "Wikidata",
  "authority_ids": {"wikidata": ["Q1048"], "wikipedia": ["Julius_Caesar"]},
  "promoted": true,
  "fallacy_flag": null,
  "note": "High agreement across sources"
}
```

---

## Getting Help

**Agent questions?**
→ Consult QUICK_START.md (section for your question)

**Role validation?**
→ Use role_qualifier_reference.json lookup

**Relationship type?**
→ Check RELATIONSHIP_TYPES_SAMPLE.md or relationship_facet_baselines.json

**Example?**
→ Find similar case in AGENT_EXAMPLES.md (11 examples)

**Design rationale?**
→ See PHASE_1_DECISIONS_LOCKED.md

**Performance optimization?**
→ Consult ARCHITECTURE_OPTIMIZATION_REVIEW.md (Phase 2+)

---

**Ready for deployment!** Upload these 8 files to ChatGPT Custom GPT knowledge base.
