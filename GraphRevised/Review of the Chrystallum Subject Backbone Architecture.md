# Review of the Chrystallum Subject Backbone Architecture

> **Note (2026-10-16).** An external review of the legacy subject-backbone
> design, kept for reference. Overtaken where it builds on that design: the
> SCA and SFA are retired ([25](25-LIVES-AND-PLAYGROUND.md) §11), the runtime is
> the Anthropic SDK rather than LangGraph, SubjectConcept is now Subject
> ([02](02-GRAPH-MODEL.md)), and numeric confidence is never stored (attestation
> is computed in words, 25 §6). Still useful: CIDOC CRM as an interoperability
> profile (25 L2b), SKOS for Subjects, PROV-O, and idempotent writes.

## Executive assessment
The plan is conceptually strong, internally coherent, and unusually disciplined about separating **entities**, **subject concepts**, **inquiry contexts**, **source observations**, and **scholarly claims**. Its most important achievement is preventing five frequent category errors: treating labels as identities, treating Wikidata as the local ontology, treating bibliographic subjects as historical entities, flattening qualified claims into bare edges, and allowing agents to mutate the durable graph without adjudication.[^1]

It should be described as a **proprietary application architecture composed from standards-based patterns**, not as a new foundational ontology. The distinctive Chrystallum contribution is the assembled control model: Wikidata-centered federation, progressive enrichment, the Entity/SubjectConcept separation, FacetApplications, SCA-governed reconciliation, structured SFA proposals, and claim-cluster promotion. Its semantic foundations overlap substantially with SKOS, CIDOC CRM, PROV-O, authority control, reconciliation systems, and agentic workflow patterns.[^2][^3][^4]

The stack is appropriate, but several parts should be delegated to existing libraries and standards. The application should build its distinctive historical-research semantics and adjudication policy, while reusing proven infrastructure for entity reconciliation, structured agent output, workflow durability, graph APIs, RDF interoperability, validation, visualization, and provenance.
## What the plan gets right
### Separation of concerns
The architecture’s four questions—what is mentioned, which authorities describe it, what knowledge is organized around it, and what claims should be developed—form a sound decomposition. This separation is stronger than a conventional knowledge-graph ingestion pipeline because it distinguishes source data from the system’s interpretation and distinguishes both from subject organization.[^1]

The Entity/SubjectConcept distinction is especially valuable. SKOS provides an established model for concept schemes, hierarchical relations, and mappings such as `exactMatch` and `closeMatch`; Chrystallum’s SubjectConcept can therefore use SKOS-compatible semantics without pretending that a subject concept is the same thing as its real-world focus.[^4][^5]
### Epistemic discipline
The sequence `SourceObservation -> NormalizedClaim -> ScholarlyClaim` is one of the plan’s strongest elements. It resembles established provenance and nanopublication patterns, where an assertion is separated from provenance and publication metadata, while leaving room for Chrystallum’s additional normalization and adjudication stages.[^1][^6]

The requirements that observations remain immutable, external revisions be preserved, and rejected or superseded proposals remain auditable are appropriate for historical research. PROV-O can supply a standard vocabulary for entities, activities, agents, derivation, attribution, and generation rather than requiring a wholly local provenance vocabulary.[^3]
### Bounded agency
The SFA-proposes/SCA-reconciles rule is a good write-safety boundary. It gives agents analytical freedom without allowing unreviewed model output to become durable truth, and the use of inquiry budgets and stopping conditions addresses recursive graph explosion.[^1]

LangGraph maps well to this design: an SCA can be a parent graph, each SFA a reusable subgraph, and reconciliation a gated node. LangGraph subgraphs are explicitly intended for multi-agent systems and reusable independently developed components, provided their state interfaces are respected.[^7]
### Federation strategy
Using Wikidata as a multilingual federation and discovery hub, while retaining Pleiades, PeriodO, LC, FAST, and domain authorities in their native roles, is sound. Wikidata provides direct entity access through a REST API and relationship-oriented querying through WDQS; however, the public SPARQL endpoint has operational constraints, including a 60-second query runtime limit, so caching and bounded query templates are necessary.[^1][^8][^9][^10]
## Required clarifications
### Normalize relationship direction
The document sometimes describes a SubjectConcept as pointing to an entity through `subjectFocus`, but the example graph later appears to use `event hasSubjectFocus subject`. Choose one canonical direction, such as:

```text
(:SubjectConcept)-[:HAS_SUBJECT_FOCUS]->(:Entity)
```

Generate inverse wording only in the API or user interface. The same rule should apply to every relationship: define canonical direction, domain, range, cardinality, inverse label, and whether the relation may carry qualifiers.[^1]
### Separate workflow state
LangGraph checkpoints, graph-domain audit records, and historical knowledge are different kinds of state and should not be collapsed into Neo4j.

- **Neo4j:** durable domain graph, claims, proposals, decisions, provenance links.
- **PostgreSQL checkpointer:** agent execution state, interrupts, retries, pending work.
- **Object storage:** raw API payloads, source documents, large extracted passages.
- **Redis or equivalent:** short-lived caches, locks, rate-limit coordination.

LangGraph provides production Postgres checkpoint savers, while its in-memory saver is for testing and SQLite is positioned for lightweight use. Keeping workflow state outside the research graph prevents operational replay data from contaminating historical semantics.[^11][^12]
### Make all side effects idempotent
LangGraph resumes at node boundaries; after an interrupt or retry, the affected node runs again from the beginning, so side effects executed before the pause may repeat. Every write-capable node therefore needs:[^13]

- deterministic `proposalId` and `observationId` values;
- uniqueness constraints in Neo4j;
- `MERGE`-based or compare-and-set writes;
- an outbox or command ledger;
- source revision/hash checks;
- a transaction boundary after reconciliation, not inside free-running SFA nodes.

This requirement should become a sixteenth architectural invariant: **no agentic side effect may depend on exactly-once execution**.
### Define validation contracts
The YAML examples should become versioned Pydantic models and JSON Schemas for `AuthorityAssertion`, `SourceObservation`, `NormalizedClaim`, `ScholarlyClaim`, `Proposal`, `Decision`, `FacetApplication`, `LocationAssertion`, and `PeriodAlignment`. Pydantic AI supports typed dependencies and schema-validated structured outputs; it can be used inside LangGraph nodes without replacing LangGraph as the workflow engine.[^14][^15]

Add semantic validation separately. JSON Schema validates payload shape, while graph rules must validate constraints such as permissible node types, evidence requirements, lifecycle transitions, and whether a predicate permits temporal or spatial qualifiers. If RDF export matters, SHACL and `pySHACL` provide a standard validation path for RDF projections.[^16]
### Formalize lifecycle machines
Statuses are listed, but allowable transitions are not. Define explicit state machines, for example:

```text
SubjectConcept:
ephemeral -> candidate -> provisional -> validated
candidate -> rejected
provisional -> merged | deprecated
validated -> deprecated | needs_reverification

Proposal:
draft -> submitted -> validating -> accepted | rejected | deferred | contested
accepted -> committed
committed -> superseded
```

Each transition should identify the actor, required evidence, permitted prior states, timestamp, reason, and resulting side effects. This will prevent status strings from acquiring inconsistent meanings across agents and UI code.
### Add source licensing policy
The architecture discusses provenance but not redistribution rights. Store license, attribution requirements, retrieval conditions, and whether the payload, extracted facts, labels, or geometry may be republished. Wikidata’s role as a hub does not imply that every linked authority shares Wikidata’s reuse terms.
### Add access control
The design needs roles for reader, agent, curator, ontology administrator, and system service. At minimum, agents should be able to submit proposals but not bypass reconciliation; curators should approve or edit proposals; and only schema administrators should modify predicate definitions, mapping rules, or lifecycle machines.
## Standards alignment
| Chrystallum construct | Closest established model | Recommendation |
|---|---|---|
| SubjectConcept | SKOS Concept | Reuse SKOS labels, broader/narrower/related, schemes, and mapping relations.[^4] |
| Entity/event/object/place | CIDOC CRM | Use CRM as an interoperability profile, not necessarily as the native Neo4j schema.[^2] |
| SourceObservation provenance | PROV-O | Map source retrieval and transformations to `prov:Entity`, `Activity`, and `Agent`.[^3] |
| Small evidence-bearing assertion | Nanopublication pattern | Consider export as assertion + provenance + publication-info graphs.[^6] |
| Entity matching | W3C/OpenRefine Reconciliation API | Use the protocol for candidate services and curator review.[^17] |
| Authority mappings | SKOS mapping properties | Retain local role and lifecycle metadata around each mapping.[^4] |
| Agent workflow | LangGraph parent/subgraphs | SCA parent graph; SFA subgraphs; interrupts for review.[^7][^18] |
| Graph validation | SHACL/pySHACL | Validate RDF projections; retain Pydantic and Cypher constraints for native writes.[^16] |

CIDOC CRM is the nearest domain reference model because it is expressly designed as semantic glue for evidence-based cultural-heritage integration and is recognized as ISO 21127:2023. Nevertheless, implementing CRM classes directly as the entire operational graph would likely make agent writes and UI queries cumbersome. A pragmatic design is a concise native property-graph model with maintained mappings to CRM, SKOS, and PROV-O.[^2]
## Is it proprietary?
There are three different questions behind “proprietary”:

1. **Is the architecture original?** The combination and governance pattern are distinctive, especially the SCA/SFA division, progressive enrichment budgets, SubjectConcept promotion, and source-to-normalized-to-scholarly claim pipeline.[^1]
2. **Is it based on established models?** Yes. It follows recognizable patterns from SKOS, CIDOC CRM, PROV-O, authority control, nanopublications, entity reconciliation, knowledge graphs, and durable agent workflows.[^2][^3][^4][^6]
3. **Is the underlying idea legally exclusive?** Not by copyright alone. The U.S. Copyright Office states that copyright protects expression and software but not ideas, systems, processes, or methods of operation. Patentability is a separate, fact-specific question requiring eligible subject matter and a concrete claimed implementation; generic application of an abstract idea is not enough.[^19][^20][^21]

Accordingly, describe it publicly as **the Chrystallum Subject Backbone: a standards-aligned, proprietary implementation architecture**. Protectable assets can include the code, documentation, mapping tables, prompts, evaluation corpus, curation policies, UI, brand, and potentially narrowly claimed technical inventions after legal review. This is technical product guidance, not legal advice.
## Reuse matrix
| Need | Reuse | Build locally |
|---|---|---|
| Wikidata lookup | Wikibase REST API for entity records; WDQS for bounded relationship queries.[^9][^8] | Cache, source observations, QID/PID-to-local predicate mappings |
| Entity reconciliation | OpenRefine/W3C Reconciliation API; Wikidata reconciliation supports types, properties, labels, aliases, and augmentation.[^22][^17] | Historical scoring features, ambiguity policy, curator decisions |
| Wikibase access in Python | `WikibaseIntegrator` for object-oriented reading/writing if a client library is preferable.[^23] | Adapters and immutable response capture |
| Neo4j access | Official `neo4j` Python driver.[^24] | Repository and transaction layer |
| RDF/linked-data interchange | Neosemantics (`n10s`) for RDF import/preview and URI mapping.[^25] | Curated mappings; do not indiscriminately mirror RDF into the operational graph |
| API layer | FastAPI for command endpoints; optionally Neo4j GraphQL for generated read/query APIs | Reconciliation commands, workflow actions, authorization rules |
| Generated graph API | Neo4j GraphQL can generate executable queries/mutations from type definitions and translates requests to Cypher.[^26][^27] | Restrict mutation surface; custom resolvers for claims and review actions |
| Agent orchestration | LangGraph checkpoints, interrupts, parent/subgraphs.[^18][^7][^11] | SCA/SFA state machines, routing, budgets, adjudication |
| Structured agent output | Pydantic/Pydantic AI.[^14][^15] | Domain models and semantic validators |
| RDF validation | SHACL + `pySHACL`.[^16] | Chrystallum shapes and severity policy |
| Provenance | PROV-O.[^3] | Domain-specific evidence and confidence semantics |
| Subject semantics | SKOS.[^4][^5] | Subject lifecycle, facet applications, promotion criteria |
| Cultural-heritage mapping | CIDOC CRM.[^2] | Native operational projection and mappings |
| Visualization | Cytoscape.js core and layout extensions; Edgehandles for graphical relation creation.[^28][^29][^30] | Semantic styling, review overlays, evidence panels, graph-delta UX |
| Graph analytics | Neo4j GDS Python client for projections, algorithms, and ML pipelines.[^31][^32] | Promotion/routing features and domain interpretation |
## Stack blueprint
```text
React + TypeScript
  |- Cytoscape.js graph canvas
  |- proposal/evidence inspector
  |- authority candidate review
  |- LangGraph interrupt review UI
  `- map/timeline panels

API / command layer
  |- FastAPI: commands, workflow control, authority adapters
  `- optional Neo4j GraphQL: read-heavy graph API

LangGraph
  |- SCA parent workflow
  |- SFA subgraphs
  |- resolver/enrichment tools
  |- validation gate
  |- human interrupt gate
  `- commit command

Typed domain layer
  |- Pydantic models + JSON Schema
  |- predicate registry
  |- mapping-rule registry
  |- lifecycle transition rules
  `- confidence/evidence policy

Persistence
  |- Neo4j: durable research graph
  |- PostgreSQL: LangGraph checkpoints + job/outbox records
  |- object storage: raw authority payloads and documents
  `- Redis: cache, locks, rate limits

Interoperability
  |- SKOS subject export
  |- CIDOC CRM projection
  |- PROV-O provenance export
  |- SHACL validation
  `- JSON-LD/nanopublication-style packages
```

Neo4j GraphQL is attractive for quickly exposing typed read APIs, but direct unrestricted mutations would conflict with the SFA-proposes/SCA-commits invariant. Mutations that affect durable knowledge should remain command operations routed through validation and reconciliation.[^26]
## Cytoscape guidance
Cytoscape.js is suitable for the envisioned interface and already has a large extension ecosystem, including layout extensions such as ELK and Dagre. Do not attempt to show the full knowledge graph at once. Render inquiry-specific subgraphs and encode epistemic state visually:[^29]

- node shape: entity, SubjectConcept, claim, observation, proposal, authority record;
- border: accepted, provisional, contested, rejected, superseded;
- edge style: asserted, inferred, mapping, aboutness, evidence, conflict;
- facet color: current FacetApplication, not permanent ontology;
- overlays: “proposed delta” versus “committed graph”;
- click-through: source, passage, revision, agent, decision reason.

`cytoscape-edgehandles` can support curator-created edges, but every drawn edge should create a proposal, not a committed relationship. The older expand/collapse extension can manage compound graphs, but its repository states that it is no longer maintained, so it should be treated cautiously or replaced with locally controlled complexity-management behavior.[^33][^30]
## Minimal vertical slice
The document’s Actium-first implementation plan is correct, but the slice should prove a complete transaction rather than maximize domain breadth:[^1]

1. Resolve “Battle of Actium” through Wikidata and one specialist authority.
2. Create/reuse the Event and SubjectConcept.
3. Preserve the raw authority response and immutable SourceObservations.
4. Run Military and Political SFA subgraphs with strict typed outputs.
5. Validate proposals structurally and semantically.
6. Interrupt for curator review of one ambiguous identity and one interpretive claim.
7. Reconcile and commit idempotently.
8. Render before/after graph deltas in Cytoscape.
9. Explain each accepted or rejected change.
10. Export the resulting SubjectConcept as SKOS, provenance as PROV-O, and selected entities/events through a CIDOC CRM profile.

Success criteria should include duplicate prevention, replay safety, provenance completeness, reproducible authority retrieval, proposal precision, curator correction rate, graph-delta explainability, and multilingual label rendering—not only answer quality.
## Priority decisions
Before implementation, freeze these contracts:

1. Canonical node labels and relationship directions.
2. The predicate registry and mapping-rule versioning format.
3. Pydantic schemas for all agent inputs and outputs.
4. Lifecycle transition tables.
5. Idempotency-key construction and uniqueness constraints.
6. Evidence minimums for automatic acceptance versus human review.
7. The boundary between Neo4j, checkpoints, cache, and raw payload storage.
8. External-source licensing and payload-retention policy.
9. Access-control roles and which operations require interrupts.
10. Evaluation fixtures for Actium, including intentionally ambiguous and conflicting cases.

The central recommendation is to **retain the architecture, narrow the first implementation, and standardize the interfaces**. Build the differentiating parts—subject governance, facet reasoning, claim normalization, adjudication, and explainable graph growth—while adopting existing tools for the mechanics around them.

---

## References

1. SUBJECT_BACKBONE_ARCHITECTURE.md (file uploaded to the Perplexity session; expiring signed link removed) - Status Agreed architecture Audience Developers, data modelers, agent authors, curators, and readers ...

2. [CIDOC CRM: Home](https://cidoc-crm.org/) - The CIDOC Conceptual Reference Model (CRM) is a theoretical and practical tool for information integ...

3. [5. Provenance information](https://fairplus.github.io/the-fair-cookbook/content/recipes/reusability/provenance.html) - The PROV-O Provenance Ontology 2 is a W3C-vetted specification of the Provenance Data Model as an OW...

4. [SKOS Simple Knowledge Organization System Primer](https://www.w3.org/TR/skos-primer/) - Whenever a concept X is broader than another concept Y, then Y is a narrower concept of X according ...

5. [SKOS Simple Knowledge Organization System ...](https://www.w3.org/2004/02/skos/core) - Mapping Properties. Label: has broader match. Super-properties: skos:broader skos:mappingRelation. I...

6. [A Framework for Citing Nanopublications](https://research.vu.nl/files/233638147/A_Framework_for_Citing_Nanopublications.pdf) - by E Fabris · 2019 · Cited by 18 — The provenance graph contains all the information about the origi...

7. [Subgraphs - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/use-subgraphs) - This guide explains the mechanics of using subgraphs. A subgraph is a graph that is used as a node i...

8. [Wikidata:SPARQL query service/Wikidata Query Help](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/Wikidata_Query_Help) - The Wikidata Query Service provides a SPARQL endpoint including a powerful Web-GUI. SPARQL (pronounc...

9. [Wikidata:REST API](https://www.wikidata.org/wiki/Wikidata:REST_API) - The Wikibase REST API is an OpenAPI-based interface that allows users to interact with, retrieve and...

10. [Wikidata Query Service/User Manual](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual) - Wikidata Query Service (WDQS) is a software package and public service designed to provide a SPARQL ...

11. [checkpoints | langgraph](https://reference.langchain.com/python/langgraph/checkpoints) - Checkpoints allow LangGraph agents to persist their state within and across multiple interactions. A...

12. [langgraph.checkpoint.postgres](https://reference.langchain.com/python/langgraph.checkpoint.postgres) - This library provides a Postgres implementation of LangGraph's checkpoint saver. Use it when you wan...

13. [Graph API overview - Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/graph-api)

14. [Pydantic AI | Pydantic Docs](https://pydantic.dev/docs/ai/overview/) - Pydantic AI is the Python AI SDK: a typed, extensible agent loop. Structured outputs, typed dependen...

15. [pydantic_ai.output | Pydantic Docs](https://pydantic.dev/docs/ai/api/pydantic-ai/output/) - Marker class to use the model's native structured outputs functionality for outputs and optionally c...

16. [pyshacl](https://pypi.org/project/pyshacl/0.9.5/) - A Python validator for SHACL. This is a pure Python module which allows for the validation of RDF gr...

17. [Reconciliation API](https://openrefine.org/docs/technical-reference/reconciliation-api) - This is a technical description of the mechanisms behind the reconciliation system in OpenRefine. A ...

18. [Human-in-the-loop - Docs by LangChain](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop) - Deep Agents support human-in-the-loop workflows through LangGraph's interrupt capabilities. You can ...

19. [2106-Patent Subject Matter Eligibility](https://www.uspto.gov/web/offices/pac/mpep/s2106.html) - First, the claimed invention must be to one of the four statutory categories. 35 U.S.C. 101 defines ...

20. [Copyright in General (FAQ) | U.S. Copyright Office](https://www.copyright.gov/help/faq/faq-general.html) - Copyright does not protect facts, ideas, systems, or methods of operation, although it may protect t...

21. [Circular 33 Works Not Protected by Copyright](https://www.copyright.gov/circs/circ33.pdf) - Methods, and Systems Copyright law expressly excludes copyright protection for “any idea, procedure,...

22. [Reconciling with Wikibase](https://openrefine.org/docs/manual/wikibase/reconciling) - The Wikidata reconciliation service for OpenRefine supports: You can find documentation and further ...

23. [WikibaseIntegrator](https://pypi.org/project/WikibaseIntegrator/) - Wikibase Integrator is a python package whose purpose is to manipulate data present on a Wikibase in...

24. [Build applications with Neo4j and Python](https://neo4j.com/docs/python-manual/current/) - The Neo4j Python Driver is the official library to interact with a Neo4j instance through a Python a...

25. [Getting Started with Neosemantics - Neo4j Labs](https://neo4j.com/labs/neosemantics/tutorial/) - In this tutorial, we will begin with a basic RDF document containing a few triples in Turtle format....

26. [Introduction - Neo4j GraphQL Library](https://neo4j.com/docs/graphql/current/) - The Neo4j GraphQL Library requires a set of type definitions that describes the shape of your graph ...

27. [Open Source GraphQL API Library](https://neo4j.com/product/graphql-library/) - Neo4j GraphQL is available as a service in AuraDB or in library format. You can quickly build API-dr...

28. [Using layouts](https://blog.js.cytoscape.org/2020/05/11/layouts/) - All layouts in Cytoscape.js are extensions. A number of layout extensions are included in the defaul...

29. [Cytoscape.js 2023 update: a graph theory library for ...](https://academic.oup.com/bioinformatics/article/39/1/btad031/6988031) - by M Franz · 2023 · Cited by 225 — 2.4 Extensions. Extensions are a key component of Cytoscape.js. T...

30. [cytoscape-edgehandles](https://github.com/cytoscape/cytoscape.js-edgehandles) - Edge creation UI extension for Cytoscape.js. Contribute to cytoscape/cytoscape.js-edgehandles develo...

31. [Python client - Neo4j Graph Data Science](https://neo4j.com/docs/graph-data-science/current/python-client/) - To help users of GDS who work with Python as their primary language and environment, there is an off...

32. [Introduction - Neo4j Graph Data Science Client](https://neo4j.com/docs/graph-data-science-client/current/) - The Neo4j Graph Data Science Python client is the official Neo4j Python library to run algorithms an...

33. [iVis-at-Bilkent/cytoscape.js-expand-collapse](https://github.com/iVis-at-Bilkent/cytoscape.js-expand-collapse) - This extension provides an interface to expand/collapse nodes and edges for better management of com...
