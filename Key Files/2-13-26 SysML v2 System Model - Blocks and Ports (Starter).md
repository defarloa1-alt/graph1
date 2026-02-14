# 2-13-26 SysML v2 System Model - Blocks and Ports (Starter)

## Source Of Truth
This SysML v2 model is normatively aligned to:
- `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

Use consolidated section numbering for all implementation crosswalks.
- Entity layer: Section 3
- Subject layer + authorities: Section 4
- Agent architecture: Section 5
- Claims lifecycle: Section 6
- Relationship layer: Section 7
- Orchestration + federation dispatcher: Section 8 (especially 8.6)
- Workflows: Section 9

## Modeling stance
- SysML defines runtime boundaries, contracts, states, and connectors.
- Neo4j remains semantic truth storage.
- Backlink/federation processing must pass the dispatcher control plane (Section 8.6).

## Block catalog (aligned)

| Block | Responsibility | Consolidated reference |
|---|---|---|
| `Orchestrator` | End-to-end workflow orchestration and phase transitions | Sections 8, 9 |
| `AgentRouter` | Deterministic routing by `SubjectConcept` + facet + temporal/geographic scope | Sections 4, 5 |
| `SubjectFederationService` | Subject authority resolution and normalization (LCSH/FAST/LCC/CIP/Wikidata) | Section 4 |
| `TemporalFederationService` | Temporal normalization (bbox fields + Year anchors + period alignment) | Sections 3.4, 4.3 |
| `GeographicFederationService` | Place normalization (TGN/Pleiades/GeoNames/Wikidata) | Sections 3.1.2, 4.4 |
| `RelationshipSemanticsService` | Canonical relationship mapping (registry + P-value alignment) | Section 7 |
| `FederationDispatcher` | Route-by-`datatype+value_type`, class gates, frontier controls, quarantine | Section 8.6 |
| `ClaimLifecycleService` | Claim creation, review intake, consensus scoring, state transitions, promotion signals | Section 6 |
| `GraphPersistenceService` | Constraint-safe reads/writes to Neo4j schema layer | Section 3 + schema files |
| `AgentRuntime` | Facet/domain specialist execution and extraction | Section 5 |
| `AgentRAGStore` | Per-agent private retrieval context, evidence chunks | Sections 5, 6 |
| `GovernancePolicyService` | Validation policy gates and promotion/deny decisions | Sections 6, 10 |
| `ExternalFederationGateway` | Bounded external API access and normalization envelope | Sections 4.3, 4.4, 4.5, 8.6 |

## Port payload schemas (minimum contracts)

### `claimIn` (in -> `Orchestrator`)
```json
{
  "request_id": "string",
  "source_agent": "string",
  "text": "string",
  "subject_hints": ["string"],
  "evidence_refs": ["string"],
  "timestamp": "ISO-8601"
}
```

### `routeOut` (out <- `AgentRouter`)
```json
{
  "request_id": "string",
  "target_agents": ["string"],
  "routing_basis": {
    "subject_concept_ids": ["string"],
    "facet_keys": ["string"],
    "lcc_ranges": ["string"],
    "time_bbox": {"start_min": "string", "end_max": "string"},
    "place_qids": ["string"]
  },
  "priority": "low|medium|high"
}
```

### `federationQuery` (out -> `ExternalFederationGateway`)
```json
{
  "request_id": "string",
  "seed_qid": "Q...",
  "mode": "production|discovery",
  "depth": 0,
  "property_surface": ["P..."],
  "budget": {"sparql_limit": 0, "max_sources": 0, "max_new_nodes": 0}
}
```

### `federationResult` (in <- `ExternalFederationGateway`)
```json
{
  "request_id": "string",
  "provider": "wikidata|loc|getty|periodo|...",
  "assertions": [
    {
      "property": "P...",
      "datatype": "string",
      "value_type": "string",
      "value": "any",
      "qualifiers": [],
      "references": []
    }
  ],
  "provenance": {"source": "string", "retrieved_at": "ISO-8601"}
}
```

### `dispatcherDecision` (in/out -> `FederationDispatcher`)
```json
{
  "request_id": "string",
  "route": "edge_candidate|federation_id|temporal_anchor|node_property|quarantine",
  "reason": "string",
  "frontier_eligible": true,
  "class_gate": "pass|fail",
  "temporal_precision_gate": "pass|fail"
}
```

### `claimStateUpdate` (out <- `ClaimLifecycleService`)
```json
{
  "claim_id": "string",
  "cipher": "string",
  "from_state": "proposed|validated|disputed|rejected",
  "to_state": "proposed|validated|disputed|rejected",
  "consensus_score": 0.0,
  "review_count": 0,
  "timestamp": "ISO-8601"
}
```

## Federation flows (aligned to consolidated)

1. `AgentRuntime -> FederationDispatcher`: send candidate assertions and backlink candidates.
2. `FederationDispatcher -> ExternalFederationGateway`: only routed/allowed assertions are queried or expanded.
3. `ExternalFederationGateway -> FederationDispatcher`: normalized assertion envelope returns with provenance.
4. `FederationDispatcher -> {Subject|Temporal|Geographic|Relationship}FederationService`: typed dispatch by route category.
5. `{FederationServices} -> GraphPersistenceService`: only normalized, policy-cleared writes.
6. `GraphPersistenceService -> ClaimLifecycleService`: materialized claim/evidence links for lifecycle transitions.

Control requirements:
- No bypass path around `FederationDispatcher`.
- No silent drop; every dropped statement must emit reason metrics.
- Discovery mode uses expanded budgets but still records gate outcomes.

## Claim lifecycle states (normative)

`proposed -> validated | disputed | rejected`

Lifecycle controls:
- Creation requires `claim_id`, `cipher`, `text`, `source_agent`, `confidence`, `status`.
- Reviews update `review_count` and `consensus_score`.
- Promotion eligibility is policy-controlled, not agent-authoritative.
- `cipher` is the content-addressable cluster key.

## Agent routing logic (deterministic policy)

Routing priority order:
1. `SubjectConcept` anchor match (authority-backed)
2. Facet specialization match
3. Temporal scope overlap (bbox + Year anchors)
4. Geographic scope overlap
5. Workload/priority balancing

Routing outputs:
- Primary owner agent
- Secondary reviewer set (for cross-facet validation)
- Escalation flag when confidence or coverage thresholds fail

## Neo4j mapping guidance

| SysML concern | Neo4j representation |
|---|---|
| Subject resolution outputs | `:SubjectConcept` + authority IDs/properties |
| Temporal outputs | `:Year`, `:Period` + bbox properties + year-anchor edges |
| Geographic outputs | `:Place` (+ `:PlaceVersion`/`:Geometry` as needed) |
| Relationship semantics outputs | Canonical relationship types + mapped P-values |
| Claim lifecycle outputs | `:Claim`, `:Review`, `:ReasoningTrace`, `:Synthesis` |

## Initial rules

1. Every external assertion must carry `source` and `retrieved_at`.
2. Every graph write must pass constraints and policy checks.
3. Agents can propose; only lifecycle + governance gates can promote.
4. `Communication` is a facet/domain axis, not a first-class node label.

## Next iteration tasks

1. Generate strict JSON schemas per port contract.
2. Generate executable SysML v2 package from these blocks/ports/connectors.
3. Add error/retry SLA contracts on gateway and dispatcher ports.
4. Add conformance tests: one test per route category and claim transition.
