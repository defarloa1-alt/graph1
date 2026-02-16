2-16-26-ArchReview2
According to a document from February 12, 2026 (with appendices updated through February 16, 2026), your update pass did land several of the “structural correctness” fixes that matter most, especially around claim identity/provenance and operational orchestration.

What looks materially improved

1. Claim identity is now explicitly “content-only” (ADR-001), and you’ve separated mutable provenance from immutable identity. That resolves the earlier internal contradiction and makes cross-agent dedup possible in principle.

2. You integrated the CIDOC-CRM enrichment work as an operational capability (not just an ontology note): prompt updates across facets, plus explicit workflow touchpoints in enrichment + claim generation methods, and storage fields for CIDOC class + confidence.

3. The two-phase SCA/SFA framing is clearer: “training claims” (abstract discipline ontology) are accepted without cross-facet queueing, while “concrete claims” can be selectively routed for multi-facet review. That’s the right shape for scalability.

High-priority issues still present (these will bite later)

A) Cipher contents still appear internally inconsistent with your own consensus goal.
Your ADR text says the cipher includes `facet_id`, but elsewhere you rely on “different facets independently extract same claim → same cipher” to compute consensus across facets.
If `facet_id` is in the hash input, cross-facet consensus collapses into multiple claim nodes.

A clean fix is to define two identifiers:

* AssertionCipher (facet-agnostic): subject/object/predicate/temporal/source/passage hash (+ normalization)
* PerspectiveID (facet-specific): AssertionCipher + facet_key (+ agent_id if you want stable per-agent perspectives)

That preserves dedup/verification while still letting you keep facet-specific interpretations.

B) You now have two parallel “facet opinion” constructs that need an explicit division of labor.
ADR-001 describes persistent “FacetPerspective nodes” for provenance and confidence evolution.
But the star-pattern UI model introduces `AnalysisRun -> FacetAssessment -> Facet` (and `EVALUATED_BY -> Agent`) as the main evaluative structure.
This can be fine, but only if you state unambiguously:

* FacetPerspective = durable, claim-attached, accumulative provenance record(s)
* FacetAssessment = ephemeral (or versioned) run output used for UI/tabbed presentation and A/B comparisons

Right now it reads like two competing ways to represent “facet confidence.”

C) Counts/registries are drifting: relationships and facets both show mismatched totals.

* Relationship catalog is described as “311 types” with specific mapped counts in Appendix V.
* Elsewhere you show “Total Relationship Types: 300” with different alignment numbers.
  Similarly, facet counts flip between 16/17/18 in different places (e.g., “18 facets: 16 core + biographic + communication” vs “17 analytical dimensions”).

If you want this spec to function as a build contract, pick one canonical source of truth (you already cite master registries), and make the narrative sections *derive from* those numbers.

D) Minor but pervasive: encoding artifacts (“â†’”) reduce credibility and will pollute copy/paste into code/docs. You’ll want to fix file encoding or the conversion pipeline in the consolidated doc sections that show arrows and bullets.

E) You’ve correctly flagged a lingering doc inconsistency (“Computed with confidence=0.85”)—it’s small, but it directly touches identity semantics, so it should be eliminated everywhere it appears to avoid future regressions.

Core vs “package-like” concepts (for astronomy / chemistry / law)

Your own executive framing says the system can generalize to other domains “by swapping the underlying ontology.”  Practically, that swap only works cleanly if you formalize what’s truly invariant.

Core (should remain stable across domains)

* Claim identity + normalization + content-addressable verification (ADR-001 principles)
* Evidence/provenance chain model (source work, passage anchoring, extraction metadata)
* Agent orchestration mechanics (state, routing, validation workflow, logging)
* A small, domain-neutral entity kernel (Agent, Claim, Work/Source, Evidence/Passage, Concept/Entity, TimeSpan, Place as optional)
* A domain-neutral quality/validation layer (completeness checks, rule execution, review tagging)

Packages (domain plug-ins; should be versioned and swappable)

* Subject ontology / taxonomies (e.g., “Roman Republic” vs “Stellar astrophysics”)
* Relationship catalogs and action-structure vocabularies (domain-specific predicates and role frames)
* Authority/federation adapters (Wikidata always, then: ADS/SIMBAD for astronomy; PubChem/CAS-ish mappings for chemistry; court/opinion databases + internal doc stores for law)
* Facet sets and facet categories (historiography facets vs lab-science facets vs legal-analysis facets)
* Validation rule packs (e.g., unit consistency for chemistry, citation precedence rules for law)

A concrete diagram (Claim + facet subgraph)

This merges what the doc currently describes (Claim identity + facet run “star pattern” + persistent provenance) and also highlights where you need to disambiguate Assessment vs Perspective:

```text
                         (cat:FacetCategory)
                               ^
                               | IN_FACET_CATEGORY
                               |
(claim:Claim) <--- PERSPECTIVE_ON --- (fp:FacetPerspective) --- EVALUATED_BY ---> (agent:Agent)
    ^
    | HAS_ANALYSIS_RUN
    |
(run:AnalysisRun) --- HAS_FACET_ASSESSMENT ---> (fa:FacetAssessment) --- ASSESSES_FACET ---> (f:Facet)
                                         \
                                          \--- EVALUATED_BY ---> (agent:Agent)
```

* The top line (FacetPerspective) corresponds to “provenance tracked separately” in the cipher ADR language.
* The bottom star is the UI/reporting model for per-run facet evaluations and tab grouping.

If you want, I can mark up (in-place) the exact sentences/sections that should be rewritten to (1) split AssertionCipher vs PerspectiveID and (2) formally separate FacetPerspective vs FacetAssessment so the model isn’t duplicative.
