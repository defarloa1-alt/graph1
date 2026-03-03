# Person Harvest — Gradio UI Plan (Pinned)

**Created:** 2026-03-03  
**Trigger:** When person extract (Person Harvest Orchestrator) is ready to run end-to-end.

---

## Goal

Launch the Person Harvest flow in Gradio and get a **verbose response for every step**. Each step can take time (discovery, context packet, agent, executor); the UI should stream progress so the user sees what is happening.

---

## Current State

- **Orchestrator:** `scripts/person_harvest/orchestrator.py` — Discovery → context packet → agent → executor, one person at a time
- **Gradio app:** `scripts/ui/agent_gradio_app.py` — Facet agents, SCA, cross-domain; no Person Harvest tab yet
- **Person Harvest flow:** CLI only (`python -m scripts.person_harvest.orchestrator --limit 10`)

---

## Planned UI Changes

### 1. New Gradio tab: "Person Harvest"

- **Inputs:**
  - Limit (persons to harvest, default 10)
  - Seed QID (optional — single person)
  - From graph (checkbox — discover from graph vs Wikidata)
  - Dry run (checkbox)
- **Output:** Streaming text area that shows verbose progress for every step

### 2. Verbose step-by-step output

Stream (yield) progress for each phase:

| Phase | What to stream |
|-------|----------------|
| **Discovery** | "Discovering persons...", count found, DPRR blocked status |
| **Per person** | "Processing Q12345 (label)...", "  Building context packet...", "  Agent reasoning...", "  Executing plan..." |
| **Context packet** | "  dprr_raw: present/absent", "  wikidata_raw: N claims" |
| **Agent** | "  PersonHarvestPlan produced", "  identity_resolution: ...", "  attribute_claims: N" |
| **Executor** | "  Entity created/updated", "  FATHER_OF/MOTHER_OF written", "  BORN_IN_YEAR/DIED_IN_YEAR linked" |
| **Summary** | "Harvest complete: N created, N updated, N skipped" |

### 3. Implementation approach

- **Option A:** Wrap orchestrator in a generator that yields progress strings; Gradio `gr.ChatInterface` or `gr.Textbox` with `stream=True` / `every` callback
- **Option B:** Add `verbose=True` and a `progress_callback: Callable[[str], None]` to orchestrator; Gradio passes a callback that appends to the output
- **Option C:** Use `gr.Textbox` with a thread that runs the orchestrator and pushes updates via `gr.Textbox.update(value=accumulated)` in a loop

Reference: `scripts/legacy/sca_gradio_fixed.py` and `scripts/ui/sca_ui_live_progress.py` — "Must accumulate for Gradio" pattern for streaming.

### 4. Dependencies

- Orchestrator must be callable from UI (no `sys.exit`, return stats dict)
- Consider `--limit 1` for initial UI testing (single person, full verbose)
- DPRR blocked → context packet uses graph-local `dprr_raw` (no network); agent/executor still need Neo4j

---

## Checklist (when implementing)

- [ ] Add Person Harvest tab to `agent_gradio_app.py`
- [ ] Create `run_person_harvest(limit, seed_qid, from_graph, dry_run)` that yields progress
- [ ] Wire to streaming `gr.Textbox` or equivalent
- [ ] Test with `--limit 1 --dry-run` first
- [ ] Document launch: `launch_gradio_ui.bat` → Person Harvest tab

---

## Related

- `Person/OPEN_ITEMS_DETAILED.md` — Full 13-step executor, SYS_HarvestPlan writer
- `Person/3-3-26-plan.txt` — Phase 5/6 context packet, agent infrastructure
- `scripts/person_harvest/orchestrator.py` — Main loop
