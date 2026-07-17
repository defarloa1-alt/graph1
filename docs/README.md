# Chrystallum documentation

**Canonical graph:** Neo4j Aura `ac63a8e5`. Do not trust static node counts in markdown — query live.

## Read order

1. [EPISTEMIC_MODEL.md](EPISTEMIC_MODEL.md) — claims, confidence, lifecycle
2. [FACET_TRAINING_CONTRACT.md](FACET_TRAINING_CONTRACT.md) — binding rules for all facet SFA training
3. [ARCHITECTURE_CURRENT.md](ARCHITECTURE_CURRENT.md) — system architecture (supersedes older docs)
4. [AGENTS.md](AGENTS.md) — agent constraints

## Three tracks (do not conflate)

| Track | What | Review surface |
|-------|------|----------------|
| **Subject concepts** | Thematic decomposition under facet umbrellas | Viewer → Review Queue; `output/di_proposals/` |
| **Canonical graph** | Edges the system treats as in-graph (DPRR, forward harvest) | Neo4j Browser / System Map |
| **Claims** | Staged Wikidata assertions awaiting enrichment + human sign-off | Viewer → Bio Claims; `proposal_review_api.py` |

Biographic factual work: [BIOGRAPHIC_CLAIM_PIPELINE.md](BIOGRAPHIC_CLAIM_PIPELINE.md)

## Active docs by area

### Core
- [ARCHITECTURE_CURRENT.md](ARCHITECTURE_CURRENT.md)
- [EPISTEMIC_MODEL.md](EPISTEMIC_MODEL.md)
- [DATA_DICTIONARY.md](DATA_DICTIONARY.md)
- [NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md](NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md)
- [DEPRECATED_CHRYSTAL_2.0.md](DEPRECATED_CHRYSTAL_2.0.md)

### Domain & baseline
- [BASELINE_Q17167_FACET_HIERARCHY_2026-07-15.md](BASELINE_Q17167_FACET_HIERARCHY_2026-07-15.md)
- [DOMAIN_INITIATOR.md](DOMAIN_INITIATOR.md)
- [DOMAIN_MANAGEMENT_GUIDE.md](DOMAIN_MANAGEMENT_GUIDE.md)
- [DOMAIN_QUICK_REFERENCE.md](DOMAIN_QUICK_REFERENCE.md)
- [VERSION_MANAGEMENT_GUIDE.md](VERSION_MANAGEMENT_GUIDE.md)
- [VERSION_CLI_REFERENCE.md](VERSION_CLI_REFERENCE.md)
- [SFA_DOMAIN_INTEGRATION.md](SFA_DOMAIN_INTEGRATION.md)
- [SCA_ACTIVATION_CHECKLIST.md](SCA_ACTIVATION_CHECKLIST.md)
- [SCA_SFA_CONTRACT.md](SCA_SFA_CONTRACT.md)
- [SUBJECT_DOMAIN_CONCEPTUAL_MODEL.md](SUBJECT_DOMAIN_CONCEPTUAL_MODEL.md)

### Biographic & claims
- [BIOGRAPHIC_CLAIM_PIPELINE.md](BIOGRAPHIC_CLAIM_PIPELINE.md)
- [HARVESTING_PROCESS_GUIDE.md](HARVESTING_PROCESS_GUIDE.md)
- [BIO_BACKLINK_REVERSAL_PLAN.md](BIO_BACKLINK_REVERSAL_PLAN.md) (completed — see pipeline doc)
- [BACKLINK_QID_VERIFICATION_ALGORITHM.md](BACKLINK_QID_VERIFICATION_ALGORITHM.md)
- [BACKLINK_ENTITY_TYPE_PROPERTIES.md](BACKLINK_ENTITY_TYPE_PROPERTIES.md)
- [PERSON_LOGICAL_MODEL.md](PERSON_LOGICAL_MODEL.md)
- [PERSON_SOURCES_PLAN.md](PERSON_SOURCES_PLAN.md)
- [BIO_CENTURY_PRECISION_DPRR_CROSSCHECK.md](BIO_CENTURY_PRECISION_DPRR_CROSSCHECK.md)
- [POSITION_ACTIVE_IN_YEAR_GAP.md](POSITION_ACTIVE_IN_YEAR_GAP.md)
- Code: `scripts/agents/biographic/HARVEST_SCOPE.md`

### Federation & logical models
- [FEDERATION_ARCHITECTURE.md](FEDERATION_ARCHITECTURE.md)
- [FEDERATION_REGISTRY_REBUILD_SPEC.md](FEDERATION_REGISTRY_REBUILD_SPEC.md)
- [PLACE_LOGICAL_MODEL.md](PLACE_LOGICAL_MODEL.md)
- [DISCIPLINE_LOGICAL_MODEL.md](DISCIPLINE_LOGICAL_MODEL.md)
- [federations/](federations/) — import and property mapping guides

### Agents & ops
- [FACET_TRAINING_CONTRACT.md](FACET_TRAINING_CONTRACT.md) — **start here before any facet training writes**
- [agents/](agents/) — SCA instructions, harvest schema, MCP quick start
- [setup/DEV_AGENT_SCHEMA_EXECUTION_GUIDE.md](setup/DEV_AGENT_SCHEMA_EXECUTION_GUIDE.md)
- [API_KEYS_AND_USAGE.md](API_KEYS_AND_USAGE.md)
- [process/QID_TO_RICH_DATA_FLOW.md](process/QID_TO_RICH_DATA_FLOW.md)
- Neo4j scripts: [`Cypher/README.md`](../Cypher/README.md) (`schema/`, `bootstrap/`, `operations/`, `queries/`)

### Architecture specs (active)
- [architecture/BACKLINKS_EXTRACTION_GUIDE.md](architecture/BACKLINKS_EXTRACTION_GUIDE.md)
- [architecture/SCA_FEDERATION_POSITIONING_SPEC_v2.md](architecture/SCA_FEDERATION_POSITIONING_SPEC_v2.md)
- [architecture/D9_SFA_CONSTITUTION_SPEC.md](architecture/D9_SFA_CONSTITUTION_SPEC.md)
- [architecture/SUBJECT_CONCEPT_CREATION_AND_AUTHORITY.md](architecture/SUBJECT_CONCEPT_CREATION_AND_AUTHORITY.md)
- [architecture/QID_TO_SFA_LEARNING_FLOW.md](architecture/QID_TO_SFA_LEARNING_FLOW.md)
- [architecture/SUBJECT_FACET_AGENT_CONSOLE_SPEC.md](architecture/SUBJECT_FACET_AGENT_CONSOLE_SPEC.md)
- [architecture/TAXONOMY_HARVESTER_AGENT_SPEC.md](architecture/TAXONOMY_HARVESTER_AGENT_SPEC.md)
- [architecture/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md](architecture/ENTITY_CIPHER_FOR_VERTEX_JUMPS.md)

## Archive

Superseded handoffs, phase completion reports, root session dumps, and duplicates (cleaned 2026-07-16):

`Archive/docs-2026-07/`

| Folder | Contents |
|--------|----------|
| `handoffs/` | Session handoffs (non-authoritative) |
| `sessions/` | Phase reports, military/diplomatic drafts, transcripts |
| `project-management/` | Roadmaps and status snapshots |
| `architecture-discovery/` | Multi-agent / IGAR early notes |
| `agents/` | Superseded SFA prompt/quick-ref drafts |
| `security/` | Security audit reports (may contain credential strings) |
| `misc/` | Empty stubs and one-offs |

Do not use archived docs for current design without verifying against `ARCHITECTURE_CURRENT.md` and `FACET_TRAINING_CONTRACT.md`.

**Full map:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)  
**Root keepers only:** `README.md`, `REQUIREMENTS.md`, `DECISIONS.md`