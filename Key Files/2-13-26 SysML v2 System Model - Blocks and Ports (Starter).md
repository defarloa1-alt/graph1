# 2-13-26 SysML v2 System Model - Blocks and Ports (Starter)

## Purpose
Define Chrystallum as a system-of-systems model where:
- SysML v2 describes runtime and integration contracts (blocks, ports, connectors).
- Neo4j remains the semantic truth store (entities, periods, subjects, claims, reviews).

## Modeling stance
- Use SysML for service boundaries, data contracts, lifecycle states, and federation flows.
- Do not replace ontology semantics with SysML connectors.
- Treat Wikidata as a federation broker, then fan out to provider authorities.

## Block catalog (initial)

| Block | Responsibility | Key data produced/consumed |
|---|---|---|
| `Orchestrator` | Routes tasks and claim workflows | claim tasks, routing decisions |
| `SubjectFederationService` | Resolve subject chain (QID/LCC/LCSH/FAST/CIP) | subject links, authority IDs |
| `TemporalFederationService` | Resolve year/period/PeriodO mappings | period links, year anchors |
| `GeographicFederationService` | Resolve place identity across authorities | place IDs, hierarchy, coordinates |
| `RelationshipSemanticsService` | Map relationship types to canonical vocab + CIDOC/CRMinf/Wikidata properties | relationship type mappings |
| `ClaimLifecycleService` | Create claims, reviews, consensus, promotion state | claim/review/synthesis records |
| `GraphPersistenceService` | Schema-constrained Neo4j writes/reads | persisted nodes/edges |
| `AgentRuntime` | Specialist agent execution and tools | proposed claims, analyses |
| `AgentRAGStore` | Per-agent retrieval index (private) | passage retrieval sets |
| `ExternalFederationGateway` | Outbound authority/API resolution and normalization | provider responses, normalized assertions |
| `GovernancePolicyService` | Validation rules, confidence thresholds, conflict policy | policy decisions, gate results |

## Port contracts (initial)

| Port | Direction | Contract (minimum) |
|---|---|---|
| `claimIn` | in | claim text, source context, request id |
| `routeOut` | out | target agents, domain rationale, priority |
| `subjectResolve` | in/out | input terms/ids -> normalized subject authority bundle |
| `temporalResolve` | in/out | input dates/period labels -> year/period bundle |
| `geographicResolve` | in/out | input place terms/ids -> canonical place bundle |
| `relationTypeResolve` | in/out | input relation phrase -> canonical relationship mapping |
| `federationQuery` | out | provider target, query payload, retry policy |
| `federationResult` | in | provider assertion set with provenance |
| `graphWrite` | out | constrained write payload |
| `graphRead` | in/out | query + typed result set |
| `reviewIn` | in | claim package for reviewer agents |
| `consensusOut` | out | consensus score, state transition recommendation |
| `policyCheck` | in/out | rule evaluation request -> pass/fail + explanation |

## External federation providers (through gateway)

| Provider class | Primary role | Typical outbound links to exploit |
|---|---|---|
| Wikidata | Broker/discovery + crosswalk IDs | LoC, FAST, VIAF, GND, Getty, GeoNames, Wikipedia, Period resources |
| Library of Congress (LCSH/LCC) | Subject hierarchy and canonical heading metadata | related authority records |
| FAST | Subject authority IDs and subject linking | worldcat authority references |
| PeriodO | Temporal authority alignment | dataset period URIs and scope metadata |
| Getty TGN | Place authority and hierarchy | geographic authority crosslinks |
| VIAF/GND/ISNI/BnF | Name/identity authority enrichment | additional authority identifiers |

## Connector map (starter)

1. `Orchestrator.claimIn -> AgentRuntime.routeOut`
2. `AgentRuntime.subjectResolve -> SubjectFederationService`
3. `AgentRuntime.temporalResolve -> TemporalFederationService`
4. `AgentRuntime.geographicResolve -> GeographicFederationService`
5. `AgentRuntime.relationTypeResolve -> RelationshipSemanticsService`
6. `SubjectFederationService.federationQuery -> ExternalFederationGateway`
7. `TemporalFederationService.federationQuery -> ExternalFederationGateway`
8. `GeographicFederationService.federationQuery -> ExternalFederationGateway`
9. `ExternalFederationGateway.federationResult -> {Subject|Temporal|Geographic}FederationService`
10. `{all federation services}.graphWrite -> GraphPersistenceService`
11. `ClaimLifecycleService.reviewIn -> AgentRuntime`
12. `ClaimLifecycleService.policyCheck -> GovernancePolicyService`
13. `ClaimLifecycleService.graphWrite -> GraphPersistenceService`

## SysML v2 textual sketch (pseudo-starter)

```sysml
package ChrystallumSystem {
  part def Orchestrator;
  part def AgentRuntime;
  part def SubjectFederationService;
  part def TemporalFederationService;
  part def GeographicFederationService;
  part def RelationshipSemanticsService;
  part def ClaimLifecycleService;
  part def GraphPersistenceService;
  part def ExternalFederationGateway;
  part def GovernancePolicyService;

  port def ClaimIn;
  port def FederationQuery;
  port def FederationResult;
  port def GraphWrite;
  port def GraphRead;
  port def PolicyCheck;

  connector c1 from Orchestrator.claimIn to AgentRuntime.claimIn;
  connector c2 from AgentRuntime.subjectResolve to SubjectFederationService.subjectResolve;
  connector c3 from SubjectFederationService.federationQuery to ExternalFederationGateway.federationQuery;
  connector c4 from ExternalFederationGateway.federationResult to SubjectFederationService.federationResult;
  connector c5 from SubjectFederationService.graphWrite to GraphPersistenceService.graphWrite;
}
```

## Neo4j mapping guidance

| SysML concern | Neo4j representation |
|---|---|
| Subject resolution outputs | `:Subject`, `:SubjectConcept`, authority id properties |
| Temporal resolution outputs | `:Year`, `:Period`, period alignment edges |
| Geographic resolution outputs | `:Place`, geographic hierarchy and identity edges |
| Relationship semantics outputs | canonical relationship nodes/mapping properties |
| Claim lifecycle outputs | `:Claim`, `:Review`, `:Belief`, synthesis/provenance edges |

## Initial rules

1. Every external assertion must include `source`, `retrieved_at`, and provider-specific ID.
2. Every promoted claim must pass `GovernancePolicyService` checks.
3. Every federation service writes normalized data only via `GraphPersistenceService`.
4. Agent private RAG outputs are evidence inputs, not direct truth writes.
5. Wikidata is discovery/crosswalk first; provider authorities are canonical in their specialty.

## Suggested next iteration

1. Define strict JSON schemas for each port payload.
2. Add state machines for claim promotion (`proposed -> reviewed -> validated/disputed/rejected`).
3. Add SLA/retry/error contracts on `ExternalFederationGateway` ports.
4. Model capability registry for deterministic agent routing by LCC/facet/period/place scopes.
