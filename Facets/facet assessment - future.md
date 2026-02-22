Fact assessment system: recommended graph shape for claim + per-facet analysis
hat “claim hub + per-facet analysis spokes” is a really good fit for your current setup (year vector + facet subgraphs). You don’t need a new “facet superclass node” for the *facet taxonomy* (you already have `:Facet` + `:FacetCategory`), but you **do** need a clean structure for **facet evaluations** so the UI can show “analysis by facet” for each claim.

## Recommended graph shape for a claim’s star-pattern analysis

### Keep your existing facet taxonomy

* `(:FacetCategory {key:"POLITICAL"})`
* `(:Facet:PoliticalFacet {unique_id:"POLITICALFACET_Q..."})-[:IN_FACET_CATEGORY]->(:FacetCategory)`

### Add a separate “assessment layer”

You don’t want to hang scores/evidence directly on the facet value nodes (those are reusable). Instead:

**Nodes**

* `:Claim` — the proposition (e.g., “Caesar crossed the Rubicon”)
* `:AnalysisRun` — one execution of your evaluation pipeline (so you can rerun and compare)
* `:FacetAssessment` — the per-facet output (score, rationale, evidence pointers, etc.)
* `:Agent` — evaluator (human, model, tool) responsible for a facet/category

**Relationships**

* `(claim)-[:HAS_ANALYSIS_RUN]->(run)`
* `(run)-[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)`
* `(fa)-[:ASSESSES_FACET]->(facetValue:Facet)`  ✅ ties assessment to a facet value
* `(fa)-[:EVALUATED_BY]->(agent:Agent)`         ✅ which agent did it
* Optional: `(agent)-[:OWNS_CATEGORY]->(cat:FacetCategory)` ✅ “agents assigned to each facet”

This preserves your “star” (Claim → many FacetAssessments), and each assessment points to the facet value it assessed.

---

## Concrete Cypher template (creates the star pattern)

```cypher
// Example: create a claim + one run + 3 facet assessments
MERGE (c:Claim {claim_id:"CLAIM_CAESAR_RUBICON"})
SET c.text = "Caesar crossed the Rubicon",
    c.created_at = coalesce(c.created_at, datetime()),
    c.updated_at = datetime()

MERGE (run:AnalysisRun {run_id:"RUN_2026_01_14_001"})
SET run.created_at = coalesce(run.created_at, datetime()),
    run.updated_at = datetime(),
    run.pipeline_version = "v1"
MERGE (c)-[:HAS_ANALYSIS_RUN]->(run)

// Make sure the facet values already exist in your taxonomy
MATCH (pol:Facet:PoliticalFacet {unique_id:"POLITICALFACET_Q3624078"})
MATCH (mil:Facet:MilitaryFacet  {unique_id:"MILITARYFACET_Q198"})
MATCH (geo:Facet:GeographicFacet {unique_id:"GEOGRAPHICFACET_Q170526"})

// Agents (examples)
MERGE (a_pol:Agent {agent_id:"AGENT_POLITICAL_V1"}) SET a_pol.label="Political evaluator"
MERGE (a_mil:Agent {agent_id:"AGENT_MILITARY_V1"})  SET a_mil.label="Military evaluator"
MERGE (a_geo:Agent {agent_id:"AGENT_GEO_V1"})       SET a_geo.label="Geography evaluator"

// Create facet assessments (the spokes)
CREATE (fa1:FacetAssessment {
  assessment_id: "FA_CAESAR_POL_001",
  score: 0.92,
  rationale: "High confidence based on primary and secondary sources.",
  status: "supported",
  created_at: datetime()
})
CREATE (fa2:FacetAssessment {
  assessment_id: "FA_CAESAR_MIL_001",
  score: 0.85,
  rationale: "Consistent with military and political context of 49 BCE.",
  status: "supported",
  created_at: datetime()
})
CREATE (fa3:FacetAssessment {
  assessment_id: "FA_CAESAR_GEO_001",
  score: 0.78,
  rationale: "Rubicon identification/interpretation has some scholarly nuance.",
  status: "mostly_supported",
  created_at: datetime()
})

MERGE (run)-[:HAS_FACET_ASSESSMENT]->(fa1)
MERGE (run)-[:HAS_FACET_ASSESSMENT]->(fa2)
MERGE (run)-[:HAS_FACET_ASSESSMENT]->(fa3)

MERGE (fa1)-[:ASSESSES_FACET]->(pol)
MERGE (fa2)-[:ASSESSES_FACET]->(mil)
MERGE (fa3)-[:ASSESSES_FACET]->(geo)

MERGE (fa1)-[:EVALUATED_BY]->(a_pol)
MERGE (fa2)-[:EVALUATED_BY]->(a_mil)
MERGE (fa3)-[:EVALUATED_BY]->(a_geo);
```

---

## UI query: show analysis grouped by facet category

Because `FacetValue -> FacetCategory` already exists, the UI grouping becomes easy:

```cypher
MATCH (c:Claim {claim_id:"CLAIM_CAESAR_RUBICON"})-[:HAS_ANALYSIS_RUN]->(run:AnalysisRun)
MATCH (run)-[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)-[:ASSESSES_FACET]->(f:Facet)-[:IN_FACET_CATEGORY]->(cat:FacetCategory)
OPTIONAL MATCH (fa)-[:EVALUATED_BY]->(a:Agent)
RETURN
  cat.key    AS facet_category,
  cat.label  AS category_label,
  collect({
    facet_id: f.unique_id,
    facet_label: f.label,
    score: fa.score,
    status: fa.status,
    rationale: fa.rationale,
    agent: a.label
  }) AS assessments
ORDER BY facet_category;
```

That’s basically your “tabs per facet category” endpoint.

---

## Do you need a “superclass of facets” node?

Not for the taxonomy—you already have it via the `:Facet` label.

But for your claim-analysis workflow, it *is* useful to add a **Run node** (like `:AnalysisRun`) as the “parent” of the per-facet assessments, because:

* you can re-run and compare,
* you can show “latest run” vs “previous run,”
* you can store pipeline version / prompt set / model config once per run.

---

## One more helpful piece: “Agents assigned to each facet”

If you want explicit assignment:

```cypher
MATCH (a:Agent {agent_id:"AGENT_POLITICAL_V1"})
MATCH (cat:FacetCategory {key:"POLITICAL"})
MERGE (a)-[:OWNS_CATEGORY]->(cat);
```

Then the UI can show “who evaluated / who owns this facet.”

If you tell me what fields you want per facet in the UI (score only vs score+rationale+citations+links), I’ll tighten the `FacetAssessment` property set and the exact queries you’ll use most.
