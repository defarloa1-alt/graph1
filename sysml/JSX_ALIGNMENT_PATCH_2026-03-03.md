# JSX Architecture Diagram — Alignment Patch

**Date:** 2026-03-03
**Source of truth:** Graph census via `run_cypher_readonly` + `sysml/BLOCK_CATALOG_RECONCILED.md` v1.2 + `sysml/DMN_DECISION_TABLES.md` D1–D17
**Applies to:** Both `chrystallum_architecture.jsx` (Platform) and Logical Architecture JSX (Top-Down)
**Nomisma decision:** Mark as "future design intent" — no SYS_FederationSource node in graph

---

## Logical Architecture JSX (Top-Down) — 5 fixes

### L1. Header node count

```diff
- NEO4J GRAPH (~103,000 nodes · 93 relationship types)
+ NEO4J GRAPH (105,559 nodes · 97 relationship types)
```

### L2. Bottom stats bar (3 occurrences of "93")

```diff
- →~103,000 total nodes
+ →105,559 total nodes

- 93 rel types
+ 97 rel types
```

Also in the "Chrystallum vs. Native Neo4j" comparison table:

```diff
- Relationships: All 93 types registered in SYS_RelationshipType with domain/range
+ Relationships: All 97 types registered in SYS_RelationshipType with domain/range
```

### L3. Header federation operational count

```diff
- 17 registered · 5 operational · 2 partial · 1 blocked · 9 planned
+ 17 registered · 6 operational · 2 partial · 1 blocked · 8 planned
```

LGPN is `operational` in graph (not partial). Nomisma has no graph node, so planned = 8.

### L4. Nomisma status annotation

```diff
- Nomisma  planned
+ Nomisma  future (no graph node)
```

### L5. Onboarding step count (2 occurrences)

In the Query & Access Layer section:

```diff
- Onboarding: 14-step protocol
+ Onboarding: 26-step protocol (SYS_OnboardingStep nodes)
```

In the Chrystallum vs. Native Neo4j comparison:

```diff
- Self-description: 14-step onboarding protocol; graph explains itself to agents
+ Self-description: 26-step onboarding protocol; graph explains itself to agents
```

### L5a. (Optional) HistoricalPolity count

The JSX shows `:HistoricalPolity 9` but the graph has 20 `Entity:Polity` nodes. The label mismatch needs investigation — if `:HistoricalPolity` is a distinct label from `:Polity`, the count may be correct. If they're the same, update to 20.

### L5b. (Optional) Add D15–D17 to Layer 2 agent section

After "ConflictNote drafting for human review" add:

```
D15 person label gate (3 gates + veto)
D16 conflict type classification (Types 1–4)
D17 conflict resolution ladder (Type 4 escalation)
```

### L5c. (Optional) Add edge count to bottom stats

```
107,888 edges
```

---

## Platform Architecture JSX (Core vs. Domain Pack) — 12 fixes

### P1. SYS_RelationshipType count

```diff
- SYS_RelationshipType  All 93 rel types with domain + range constraints
+ SYS_RelationshipType  All 97 rel types with domain + range constraints
```

### P2. Onboarding protocol step count

```diff
- SYS_OnboardingProtocol  14-step self-explanation protocol for agent bootstrapping
+ SYS_OnboardingProtocol  26-step self-explanation protocol for agent bootstrapping
```

### P3. Add SYS_* types to SELF-DESCRIBING SYSTEM LAYER

After the existing SYS_* entries, add:

```
SYS_DecisionTable      23 decision tables registered as graph nodes
SYS_DecisionRow        128 decision rows linked to tables
SYS_Threshold          25 named thresholds (claim_promotion_confidence, etc.)
SYS_Policy             13 named policies (ApprovalRequired, NoTemporalFacet, etc.)
SYS_WikidataProperty   22 P-code → relationship type mappings
SYS_HarvestPlan        Audit trail for agent reasoning cycles (ADR-008)
```

### P4. Add D15–D17 to DECISION TABLE ENGINE

```diff
  D10    Claim promotion — confidence ≥ threshold + ApprovalRequired policy
+ D10    now includes domain_scope column — ancient_person → 0.75 (vs global 0.90)
  D-scope  Entity scoping — federation score + temporal overlap + hub rejection
  D-harvest  Budget ctrl — depth limits · result caps · new node limits per run
  D-route  Source routing — local canonical → remote · Wikidata universal fallback
  D-validate  Entity validation — literal-heavy rejection · temporal precision floor
+ D15    Person label gate — 3 gates (DPRR authority, Wikidata P31, namespace) + veto
+ D16    Conflict type classification — Types 1–4 taxonomy per ADR-007 §7.1
+ D17    Conflict resolution ladder — authority tier → tiebreaker → human escalation
```

### P5. D10 domain_scope annotation

Covered in P4 above — the D10 line now notes the domain_scope extension.

### P6. Add PersonSubsystem to DOMAIN PACK A — Roman Republic

After the existing "Domain-specific Harvest Agent (ADR-008)" section, replace/expand:

```
PersonSubsystem (ADR-007, ADR-008)
  DPRRLabelParser          Layer 1: grammar-based tria nomina + filiation extraction
  PersonReasoningAgent     Layer 2: cross-federation name reconciliation (7 sources)
  PersonHarvestExecutor    Layer 3: 13-step idempotent writes (resumable)
  OnomasticStore           Gens(585) Praenomen(24) Nomen(917) Cognomen(993) Tribe(29)
  ConflictResolutionService  Types 1–4 · CHALLENGES_CLAIM edge · ConflictNote node
```

### P7. Add onomastic + relationship counts to RR domain ontology

Expand the Domain Ontology table:

```diff
  :Person                    5,152 nodes
  :MythologicalPerson        3
  :Gens / :Nomen / :Cognomen tria nomina
  :Praenomen / :Tribe        onomastic
+ :Gens                      585 nodes
+ :Praenomen                 24 nodes
+ :Nomen                     917 nodes
+ :Cognomen                  993 nodes
+ :Tribe                     29 nodes
  :HistoricalPolity          time-scoped state
  :Position                  magistracy
  :StatusType                eques / senator
  CITIZEN_OF / FATHER_OF / SPOUSE_OF    family + civic
  POSITION_HELD + start/end year        7,342 edges
+ MEMBER_OF_GENS             4,749 edges
+ HAS_NOMEN                  4,531 edges
+ HAS_COGNOMEN               3,758 edges
+ HAS_PRAENOMEN              3,581 edges
+ MEMBER_OF_TRIBE            345 edges
+ FATHER_OF                  2,155 edges
+ SIBLING_OF                 2,144 edges
+ HAS_STATUS                 1,919 edges
+ MOTHER_OF                  634 edges
+ SPOUSE_OF                  600 edges
+ CITIZEN_OF                 5,049 edges
```

### P8. Expand RR federation sources

```diff
  ● DPRR          primary — blocked/snapshot
  ● Wikidata      secondary populist
  ● Pleiades      places + geography
  ● PeriodO       named periods
  ● LCSH/FAST     subject headings
  ● Trismegistos  papyrological
  ● LGPN          Greek prosopography
- ○ Nomisma       numismatic (planned)
+ ◐ VIAF          authority records (partial)
+ ◐ Getty AAT     art & architecture thesaurus (partial)
+ ○ EDH           epigraphic (planned)
+ ○ OCD           classical dictionary (planned)
+ ○ Nomisma       numismatic (future — no graph node yet)
```

### P9. Fix ConflictNote scope

In CLAIM & PROVENANCE MODEL:

```diff
- ConflictNote for irreconcilable conflicts (Type 4) — domain-agnostic structure
+ ConflictNote for unresolved conflicts (any type; Type 4 always escalates to human) — domain-agnostic structure
```

### P10. Add Asserted to claim lifecycle

```diff
- Proposed → Under Review → Accepted / Rejected (every claim, every domain)
+ Proposed → Under Review → Accepted / Rejected / Asserted (every claim, every domain)
```

`Asserted` = auto-promoted claims that pass D10 threshold without human review.

### P11. Add missing platform blocks

In the hierarchy (after Agent Orchestration Framework or as new sections):

```
TOOLING SUBSYSTEM (D-031)
  ChrystallumMCPServer     read-only MCP: get_policy, get_threshold, run_cypher_readonly
                            Claude.ai direct connector via HTTP transport

VISUALIZATION SUBSYSTEM
  GraphMLExporter           5 filtered subgraph views → Cytoscape Desktop
  CytoscapeWebViewer        FastAPI + cytoscape.js · parameterised endpoints · 2000-node cap

LIBRARY AUTHORITY SUBSYSTEM (D-025)
  FASTImporter              FAST subject headings
  LCSHMapper                LCSH authority IDs → entity enrichment
  VIAFLinker                VIAF cluster IDs (partial)
  LCSRUBridge               LC SRU API → MARC record retrieval
```

### P12. Mark installation model

```diff
  INSTALLATION MODEL
+ (Future design intent — not yet implemented)
  1. Deploy Platform Core
     pip install chrystallum-core
     ...
```

---

## Cross-reference: D-table informal names → DMN IDs

For the Platform JSX Decision Table Engine section, these are the D-number mappings:

| JSX informal name | DMN ID(s) | Primary consumer |
|-------------------|-----------|------------------|
| D-scope | D5, D6 | wikidata_backlink_harvest.py |
| D-harvest | D7 | wikidata_backlink_harvest.py |
| D-route | D4 | ExternalFederationGateway |
| D-validate | D6 | wikidata_backlink_harvest.py |
| D10 | D10 | claim_ingestion_pipeline.py |
| (new) D15 | D15 | adr007_apply_person_label.py |
| (new) D16 | D16 | person_harvest_agent.py |
| (new) D17 | D17 | person_harvest_agent.py |

---

## Verified correct — no changes needed

- Cipher engine (SHA-256, ADR-001)
- 3-layer agent architecture (ADR-008)
- Temporal backbone (Year + FOLLOWED_BY + IN_PERIOD)
- 18 canonical facets
- Wikidata backlink capture (10-bucket taxonomy)
- Core vs. domain pack separation
- Legal Firm domain pack (hypothetical)
- Concept mapping table (cross-domain)
- POSITION_HELD: 7,342
- SYS_PropertyMapping: 500
- SYS_AuthorityTier: 6 (exists as graph nodes)
- SYS_ConfidenceTier: 8 (exists as graph nodes)
- SYS_QueryPattern: 5 (exists as graph nodes)
- DPRR persons: 4,772
- Person + MythologicalPerson sum: 5,152
- CIDOC-CRM / GEDCOM 7.0 / LOD alignment
- Agent constraints list
- PersonHarvestPlan fields
