# AGENTS.md — Chrystallum Project Context for AI Coding Agents

**Purpose:** Context file for autonomous agents (Cloud Agent, Cursor agents). Read this and `DECISIONS.md` before any build task. The task description only needs to say *what* to do; constraints live here.

---

## DO NOT — Read This First

**Do not make autonomous infrastructure decisions.** The following are prohibited unless explicitly listed in the task:

- **Do not** add Docker, Dockerfile, docker-compose, or container config.
- **Do not** add Node.js, npm, package.json, or JavaScript tooling.
- **Do not** add start commands, dev servers, or HTTP servers unless the task explicitly requires them.
- **Do not** infer dependencies from the codebase — use `requirements.txt` only. If a dependency is missing, report it; do not add it without a task.
- **Do not** create files, directories, or config not listed in the task. If the task says "modify only these files," do not create anything else.
- **Do not** refactor, reorganize, or "improve" code outside the task scope.
- **Do not** add new scripts, tests, or CI config unless the task specifies them.

**Environment:** Use `.cursor/environment.json` — `pip install -r requirements.txt`. No other setup.

**Task discipline:** Every Cloud Agent run must reference a specific task file (e.g. `tasks/ROUND3_D10_D8_REFACTOR.md`) and DECISIONS.md entry (e.g. D-032). Do exactly what the task says. No open-ended inference.

---

## First Reads

| File | When |
|------|------|
| `AGENTS.md` (this file) | Always — constraints and process |
| `DECISIONS.md` | Always — why decisions were made, topical index |
| `sysml/BLOCK_CATALOG_RECONCILED.md` | Before touching any block — structural truth |
| `sysml/DMN_DECISION_TABLES.md` | Before touching thresholds, policies, or decision logic |
| `output/PROCESS_MODEL_FIRST_CHANGE_COMMUNICATION.md` | Before any structural change — model-first sequence |

---

## Model-First Rule

**Every structural change is recorded in the block catalog or DMN tables *before* a build spec goes to dev.**

1. Architect updates `BLOCK_CATALOG_RECONCILED.md` or `DMN_DECISION_TABLES.md`
2. Build spec references catalog entries by block name and port name
3. Dev implements against the spec
4. Acceptance test verifies implementation matches the catalog
5. Commit

If a block name appears in a spec but not in the catalog — **flag it before building**. Do not invent structure.

---

## Threshold and Policy Rules

- **SYS_Threshold** and **SYS_Policy** nodes in Neo4j are the single source of truth.
- Scripts must read from graph (direct Neo4j or MCP `get_threshold` / `get_policy`). No hardcoding.
- When adding a new threshold: add SYS_Threshold node, add row to DMN table, update block catalog, refactor script, acceptance test (grep confirms no hardcode).

---

## Key Scripts and Their DMN Tables

| Script | Primary DMN tables |
|--------|--------------------|
| `claim_ingestion_pipeline.py` | D10 (claim promotion), D14 (entity resolution) |
| `subject_concept_facet_agents.py` | D8 (SFA facet assignment) |
| `sca_agent.py` | D8 (SFA facet assignment) |
| `wikidata_backlink_harvest.py` | D5, D6, D7 |
| `cluster_assignment.py` | D5, D8 |

---

## Round 3 Scope (First Cloud Agent Task)

- **D10** claim promotion: refactor `claim_ingestion_pipeline.py` to read `claim_promotion_confidence`, `claim_promotion_posterior`, and `ApprovalRequired` from graph.
- **D8** SFA confidence: refactor `subject_concept_facet_agents.py` (and `sca_agent.py` if needed) to read `sfa_proposal_confidence_default` from SYS_Threshold. FORBIDDEN_FACETS already refactored (D-031).

---

## Constraints

- No agent writes directly to Neo4j except via approved scripts (cluster_assignment, harvester, etc.).
- Neo4j credentials: use `config_loader`; never expose in MCP or logs.
- Catalog gap: if you discover something in graph or code that doesn't appear in the catalog — report before touching.
