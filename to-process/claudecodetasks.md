# Claude Code Task Brief: Chrystallum Agent Self-Onboarding Infrastructure

## Context

Chrystallum is a federated knowledge graph in Neo4j with ~100k nodes. It has
a 5.5-layer authority stack, 13 policies, 24 thresholds, 18 facets, 14 entity
types, and 3 stub agent nodes. The goal is to make the graph **fully
self-describing** so that an AI agent can onboard itself by querying the graph
alone — no external documentation required.

Four Cypher scripts have been prepared. Your job is to execute them, validate
the results, and then handle the follow-on work that requires access to the
codebase and live Neo4j instance.

---

## Phase 1: Execute the Prepared Scripts (In Order)

### 1.1  `10_agent_meta_schema.cypher`
**What it does:** Creates `SYS_AuthorityTier` (6 nodes), `SYS_RelationshipType`
(22 nodes), `SYS_WikidataProperty` (7 nodes), `SYS_QueryPattern` (2 nodes),
`SYS_ValidationRule` (9 nodes). Enriches existing `EntityType` nodes with
`required_properties`, `canonical_outbound`, `identity_keys`, `tier`, etc.

**Validate:**
```cypher
MATCH (at:SYS_AuthorityTier) RETURN count(at);          -- expect 6
MATCH (rt:SYS_RelationshipType) RETURN count(rt);       -- expect 22
MATCH (et:EntityType) WHERE et.tier IS NOT NULL RETURN count(et);  -- expect 12+
```

### 1.2  `11_decision_table_bodies.cypher`
**What it does:** Creates `SYS_DecisionTable` (8 tables) and
`SYS_DecisionRow` (21 rows). Links policies → tables via `GOVERNED_BY`,
tables → rows via `HAS_ROW`, tables → thresholds via `USES_THRESHOLD`.

**Validate:**
```cypher
MATCH (dt:SYS_DecisionTable)-[:HAS_ROW]->(r) RETURN dt.table_id, count(r);
MATCH (p:SYS_Policy)-[:GOVERNED_BY]->(dt) RETURN p.name, dt.table_id;
MATCH (dt:SYS_DecisionTable)-[:USES_THRESHOLD]->(t) RETURN dt.table_id, t.name;
```

### 1.3  `12_claim_lifecycle_and_agents.cypher`
**What it does:**
- Creates `SYS_ClaimStatus` (10 states) with `CAN_TRANSITION_TO` edges
- Creates `SYS_AgentType` (5 types) and links existing agents
- Creates the **golden exemplar trace**: 1 RetrievalContext + 1 Claim +
  1 ProposedEdge + 1 AnalysisRun + 1 FacetAssessment, all wired together

**Validate:**
```cypher
-- State machine
MATCH (s:SYS_ClaimStatus)-[t:CAN_TRANSITION_TO]->(n) RETURN count(t);  -- expect 11
-- Golden trace
MATCH path = (a:Agent)-[:PERFORMED]->(ar)-[:PRODUCED]->(fa)
WHERE ar.is_exemplar = true RETURN length(path);  -- expect 2
MATCH path = (pe:ProposedEdge)-[:EVIDENCED_BY]->(c:Claim)-[:HAS_TRACE]->(rc)
WHERE c.is_exemplar = true RETURN length(path);  -- expect 2
```

### 1.4  `13_onboarding_protocol.cypher`
**What it does:** Creates `SYS_OnboardingProtocol` root + 10
`SYS_OnboardingStep` nodes with `NEXT_STEP` chain. Each step carries an
executable Cypher query and an explanation.

**Validate:**
```cypher
MATCH (p:SYS_OnboardingProtocol)-[:HAS_STEP]->(s)
RETURN count(s);  -- expect 10
MATCH (s1:SYS_OnboardingStep)-[:NEXT_STEP]->(s2)
RETURN count(*);  -- expect 9
```

---

## Phase 2: Follow-On Work (Requires Codebase Access)

### 2.1  Deduplicate Facet Nodes
The live graph has 36 Facet nodes (18 unique keys × 2 duplicates each). Find
and merge the duplicates:
```cypher
MATCH (f:Facet)
WITH f.key AS key, collect(f) AS nodes
WHERE size(nodes) > 1
-- keep the one with the most relationships, delete the other
```

### 2.2  Populate Federation Source Metadata
The 13 `SYS_FederationSource` nodes have null `pid` and null `scoping_weight`.
Look at the Python pipeline code (likely in `scripts/` or `pipeline/`) to find:
- Endpoint URLs or SPARQL endpoints for each source
- Rate limits
- Authentication method (API key, open, etc.)
- Response format (JSON-LD, RDF, CSV)

Then enrich each source:
```cypher
MATCH (fs:SYS_FederationSource {name: 'Wikidata'})
SET fs.endpoint = 'https://query.wikidata.org/sparql',
    fs.format = 'JSON',
    fs.rate_limit = '5/second',
    fs.auth = 'none',
    fs.scoping_weight = 1.0;
```

Also deduplicate — the federation sources have the same duplication issue
as facets (26 nodes for 13 sources).

### 2.3  Add `is_exemplar` Indexes
```cypher
CREATE INDEX claim_exemplar IF NOT EXISTS FOR (c:Claim) ON (c.is_exemplar);
CREATE INDEX analysis_run_exemplar IF NOT EXISTS FOR (ar:AnalysisRun) ON (ar.is_exemplar);
```

### 2.4  Wire FederationPositioningHopsSemantics Policy
There's one policy (`FederationPositioningHopsSemantics`) with null `active`
and null `decision_table`. Investigate what it's supposed to do and either:
- Wire it to an existing decision table
- Create a new table for it
- Mark it as `active: false` with a TODO description

### 2.5  Rejection Taxonomy (Future)
Create `SYS_RejectionReason` nodes for each way a claim can fail:
- `low_confidence` — below threshold
- `missing_provenance` — no RetrievalContext
- `human_rejected` — reviewer said no
- `out_of_scope` — D5 rejected
- `literal_heavy` — D6 rejected
- `budget_exceeded` — D7 throttled
- `excluded_facet` — D8 policy exclusion
- `duplicate_entity` — D14 flagged
Link these to the decision rows that produce them.

---

## Phase 3: End-to-End Test

Once all scripts are loaded, run the onboarding protocol as an agent would:

```python
# Pseudocode for the test
steps = session.run("""
    MATCH (p:SYS_OnboardingProtocol {protocol_id: 'onboard_v1'})-[:HAS_STEP]->(s)
    RETURN s.step_order AS step, s.query AS query, s.explanation AS explanation
    ORDER BY s.step_order
""")

for step in steps:
    print(f"\n=== Step {step['step']}: {step['explanation']} ===")
    result = session.run(step['query'], parameters={
        'agent_name': 'SFA_MILITARY_RR',
        'my_tables': ['D8_DETERMINE_SFA_facet_assignment']
    })
    for record in result:
        print(record.data())
```

Every step should return non-empty results. If any step returns empty, the
prerequisite script didn't load correctly.

---

## File Inventory

| File | Nodes Created | Edges Created |
|------|--------------|---------------|
| `10_agent_meta_schema.cypher` | ~47 | ~5 (FEEDS_INTO) |
| `11_decision_table_bodies.cypher` | ~29 | ~40+ (GOVERNED_BY, HAS_ROW, USES_THRESHOLD) |
| `12_claim_lifecycle_and_agents.cypher` | ~22 | ~20+ (CAN_TRANSITION_TO, INSTANCE_OF_TYPE, exemplar chain) |
| `13_onboarding_protocol.cypher` | ~11 | ~19 (HAS_STEP, NEXT_STEP) |

**Total new infrastructure:** ~109 nodes, ~84 edges

---

## Design Principles

1. **Everything is queryable.** No configuration lives outside the graph.
2. **MERGE everywhere.** Scripts are idempotent — safe to re-run.
3. **SYS_ prefix.** All system/infrastructure nodes use the `SYS_` prefix
   to distinguish from domain content.
4. **Decision tables ARE the spec.** Agents read the table rows to know
   what to do — there is no separate implementation.
5. **Golden trace teaches by example.** Agents pattern-match from the
   exemplar, not from instructions.