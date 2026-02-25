# Round 3 — D10 Claim Promotion + D8 SFA Confidence Refactor

**Task file for Cloud Agent.** Read `AGENTS.md` and `DECISIONS.md` before starting. Do exactly what this task specifies. Modify only the files listed below.

---

## Task reference

- **DECISIONS.md:** D-032 (D6 threshold refactor), D-031 (MCP/FORBIDDEN_FACETS)
- **DMN tables:** `sysml/DMN_DECISION_TABLES.md` — D10, D8
- **Block catalog:** `sysml/BLOCK_CATALOG_RECONCILED.md` — ClaimLifecycleService, SFAEngine

---

## What to do

### 1. D10 — claim_ingestion_pipeline.py

Refactor `claim_ingestion_pipeline.py` to read from graph instead of hardcoding:

- `claim_promotion_confidence` (0.90) → SYS_Threshold node `claim_promotion_confidence`
- `claim_promotion_posterior` (0.90) → SYS_Threshold node `claim_promotion_posterior`
- `ApprovalRequired` gate → SYS_Policy node `ApprovalRequired`

**Current locations:** ~lines 633–634 (promotion gates). Use `config_loader` for Neo4j credentials. Query SYS_Threshold and SYS_Policy by name; do not hardcode values.

**Acceptance test:** `grep -n "0\.90" scripts/tools/claim_ingestion_pipeline.py` returns no matches for these thresholds.

### 2. D8 — subject_concept_facet_agents.py (and sca_agent.py if needed)

Refactor `subject_concept_facet_agents.py` to read `sfa_proposal_confidence_default` from SYS_Threshold. FORBIDDEN_FACETS already reads from graph (D-031).

**Current location:** ~lines 261, 289 (proposal confidence default 0.8). Use direct Neo4j or MCP `get_threshold("sfa_proposal_confidence_default")`.

**If `sca_agent.py`** has a hardcoded proposal confidence or bootstrap assertion, refactor it too. Check `_validate_bootstrap` and any confidence defaults.

**Acceptance test:** `grep -n "0\.8\|0\.75" scripts/agents/subject_concept_facet_agents.py scripts/agents/sca_agent.py` returns no matches for these confidence defaults (or they are only in comments/fallback).

---

## Files to modify (only these)

- `scripts/tools/claim_ingestion_pipeline.py`
- `scripts/agents/subject_concept_facet_agents.py`
- `scripts/agents/sca_agent.py` (only if it has hardcoded confidence values)

---

## Do not

- Create new files.
- Add Docker, Node.js, or new dependencies.
- Modify block catalog or DMN tables (they are already correct for D10/D8).
- Refactor code outside the scope of these two refactors.
