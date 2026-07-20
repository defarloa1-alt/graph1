# Schema Specialist agent — Chrystal 2

**Status:** Locked 2026-07-19  
**Neo role:** `SYS_AgentType` name `SCHEMA_SPECIALIST`

## Wikidata role

Wikidata is a **federation hub** (discovery + crosswalks), **not** a truth authority.
Pack library values are candidates. Domain **apply** validates and may enrich or
replace them from other federations / review — keeping a WD value is optional.

## Job

Read the **pack library** JSON and the **live Neo schema**. Propose how each seed WD property becomes:

- a **property on the SubjectDomain**, or  
- a **first-class node + relationship** (registry types only), or  
- an **identity/aboutness tether** (Librarian / FederationCards), or  
- **ignore / defer**

Does **not** invent `SYS_NodeType` / `SYS_RelationshipType` names. Does **not** write Neo until a human (or Validation) accepts the proposal.

## Grounding (required) — not fine-tuning

Off-the-shelf LLM alone is insufficient. Each run must receive:

| Input | Source |
|-------|--------|
| Pack library | `JSON/wikidata/packs/{qid}_pack_library.json` |
| Allowed node types | Neo `SYS_NodeType` (ship set) |
| Allowed relationship types | Neo `SYS_RelationshipType` (thin registry) |
| Principles | Short system brief (below) |
| Optional few-shots | Only **reviewed** prior decisions (not Python PID maps) |

Fine-tuning is out of scope until many reviewed pack proposals exist.

## Anti-patterns

| Forbidden | Why |
|-----------|-----|
| Hardcoded `PID_OVERRIDES` in Python | Frozen pseudo-training; bypasses Neo |
| Inventing relationship types | Must use registry or propose `candidate` + Hold |
| Expanding every backlink into full statements in one shot | Pack library already indexes neighbors; expand on demand |
| Treating encyclopedia/media PIDs as structure | Prefer ignore |
| Minting `:Period` for pack bounds | Dates live on SubjectDomain |
| Minting `:Period` from WD alone | **PeriodO** is the period authority; WD only nominates candidates — prefer `defer` until PeriodO-backed |

## Principles (system brief sketch)

1. SubjectDomain **is** the pack (`TERMINOLOGY.md`).  
2. Structure vs topics (`ONTOLOGY_PRINCIPLES.md`): type/hierarchy ≠ aboutness.  
3. Scalars / times / simple quantities → prefer SubjectDomain properties (+ Year edges when bounds).  
4. Item-valued PIDs → first-class only if a registry node type + rel type fit; else defer.  
5. External IDs → identity_tether **only if** a FederationCard exists for that authority; else defer. Encyclopedia IDs → ignore.  
6. Named Period edges may stay as WD structural nominations; PeriodO validates/enriches at apply.  
7. Never emit PID/QID without label (pack library already labeled).  
8. Output proposal JSON only; `writes_neo: false` until approved.

## Tools (thin)

| Tool | Returns |
|------|---------|
| `get_pack_library(qid)` | Pack library path/contents summary + claims index |
| `list_node_types()` | From Neo |
| `list_relationship_types()` | From Neo |
| `get_subject_domain(domain_id)` | Current shell props |
| `list_federations()` | Cards summary for identity decisions |

No raw Wikidata HTTP in this agent — harvest already produced the library.

## Output

`JSON/wikidata/packs/{qid}_schema_proposal.json` authored by the agent (same rough shape as the pack contract: per-PID `decision` + rationale).  
Mark `_meta.mode = "schema_specialist_llm"` and `_meta.grounding = ["neo_registry", "pack_library", "principles"]`.

## Archived (do not use)

`archive/2026-07-19_hardcoded_schema/` — old deterministic propose script + its Republic proposal JSON. Not authoritative.

## Implementation order

1. This brief ✓  
2. Agent CLI ✓ — `python -m chrystal_2.agents.schema_specialist propose --qid Q17167 --domain-id roman_republic`  
   Principles: `chrystal_2/agents/schema_specialist/PRINCIPLES.md`  
3. Human review  
4. Apply script (registry-gated writes)  
5. Librarian  
