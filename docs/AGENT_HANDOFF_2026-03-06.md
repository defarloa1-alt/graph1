# Agent Handoff — 2026-03-06

**Purpose:** Orient a new agent to the Chrystallum codebase. Read this first, then the docs below.

---

## First Reads (in order)

| File | Purpose |
|------|---------|
| `docs/AGENTS.md` | Constraints, DO NOT rules, model-first discipline |
| `DECISIONS.md` | Why decisions were made; topical index |
| `docs/AGENT_HANDOFF_2026-03-06.md` | This file — current state and to-do |
| `docs/PRACTICAL_ALIGNMENT_2026-03-03.md` | Completed vs remaining alignment work |
| `sysml/DMN_DECISION_TABLES.md` | Before touching thresholds, policies, or decision logic |
| `sysml/BLOCK_CATALOG_RECONCILED.md` | Before touching any block — structural truth |

---

## Important Docs by Domain

### Architecture & System
- `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN_2026-02-25.md` — Graph self-description, SYS_ nodes
- `docs/FEDERATION_ARCHITECTURE.md` — Federation sources, scoping
- `docs/architecture/D9_SFA_CONSTITUTION_SPEC.md` — SFA constitution layer (D-040)
- `docs/NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md` — Node/edge schema

### Biographic / Person
- `docs/BIO_BACKLINK_REVERSAL_PLAN.md` — Backlinks decoupled from harvest; standalone backlink run
- `docs/BIO_CENTURY_PRECISION_DPRR_CROSSCHECK.md` — Wikidata century precision; DPRR cross-check when birth=death
- `docs/POSITION_ACTIVE_IN_YEAR_GAP.md` — Position ↔ Year backbone; ACTIVE_IN_YEAR edges

### Edges & Relationships
- `Relationships/relationship_types_registry_master.csv` — Canonical PID → relationship type mapping
- `Cypher/list_pid_relationships.cypher` — Query to list PID-typed edges
- `docs/BLOOM_SHOW_EDGE_LABELS.md` — Edge labels; migration script for PID → readable types

### Setup & Scripts
- `docs/API_KEYS_AND_USAGE.md` — Credentials
- `docs/setup/CURSOR_MCP_SETUP.md` — MCP setup
- `.env` — Neo4j credentials (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

---

## Recently Completed (This Session)

### Edge labels
- **`scripts/tools/canonicalize_edges.py`** — Stamps `r.label`, `r.wikidata_pid`, `r.canonical_type` on PID edges. Registry-mapped edges get human-readable labels from CSV.
- **`scripts/maintenance/enrich_edge_labels.py`** — Fetches Wikidata property labels for unmapped PIDs; sets `r.label` on edges that lack it.
- **Run order:** `canonicalize_edges.py` then `enrich_edge_labels.py`. Requires `.env` with NEO4J_*.

### Import path fix
- `canonicalize_edges.py` and `enrich_edge_labels.py` now add `scripts/` to `sys.path` so `config_loader` loads `.env` correctly.

---

## To-Do List (Priority Order)

### High
1. **SYS_ gaps** — Add ADR-007, ADR-008 to SYS_ADR; set `layer` on SYS_AgentType; register missing SYS_NodeType; add SYS_HarvestPlan. See `docs/PRACTICAL_ALIGNMENT_2026-03-03.md` §3.
2. **JSX import** — When build supports it, have JSX import `output/jsx_architecture_data.json` (or equivalent path).
3. **D-042 Biographical SFA scope** — Open decision. Person/biographical scripts could be consolidated under Biographical SFA. See DECISIONS.md D-042.

### Medium
4. **BIO century precision** — When Wikidata P569/P570 have precision 7 (century), avoid writing birth_year=death_year. Consider DPRR cross-check. See `docs/BIO_CENTURY_PRECISION_DPRR_CROSSCHECK.md`.
5. **Property pattern mining** — `Python/wikidata_property_pattern_miner.py` and `Python/fetch_historical_samples.py` are experimental; integration pending. See `md/Architecture/PROPERTY_PATTERN_MINING_INTEGRATION.md`.

### Optional cleanup
6. **Remove `config/historical_entity_type_mapping.json`** — Unused; produced by `fetch_historical_samples.py`. No consumers.
7. **Remove `Python/fetch_historical_samples.py`** — Optional; not required for main pipeline. Miner has `--sample diverse` and `--file`.

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/tools/canonicalize_edges.py` | Stamp labels on PID edges (registry + wikidata_pid) |
| `scripts/maintenance/enrich_edge_labels.py` | Fetch Wikidata labels for unmapped PIDs |
| `scripts/tools/graph_census.py` | Query SYS_*, domain counts, relationship counts |
| `scripts/tools/export_jsx_data.py` | Dump JSON for JSX architecture data |
| `scripts/agents/biographic/` | CLI, agent, backlink harvest |
| `scripts/federation/dprr_import.py` | DPRR person/position import |
| `scripts/neo4j/import_relationships_comprehensive.py` | Wikidata relationship import (uses registry) |
| `scripts/migrations/migrate_pid_edges_to_readable_types.py` | Rename PID edges (P31→INSTANCE_OF, etc.) for Bloom display |

---

## Credentials

- **Neo4j:** `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` in `.env`
- **Config loader:** `scripts/config_loader.py` loads `.env` via `dotenv`; scripts import from `config_loader`.

---

## Run Commands

```bash
# Edge label enrichment (run both)
python scripts/tools/canonicalize_edges.py
python scripts/maintenance/enrich_edge_labels.py

# Graph census
python -m scripts.tools.graph_census -o output/census.md

# Export JSX data
python -m scripts.tools.export_jsx_data -o output/jsx_architecture_data.json

# List PID-typed relationships (Neo4j Browser)
# Run: Cypher/list_pid_relationships.cypher
```
