# Kanban Context — Operational Sequence & Metrics

**Last Updated:** 2026-02-27  
**PM:** AI PM Agent  
**Current Focus:** Phase 0c — build_adjacency_matrix.py

Tasks are managed in the LachyFS Kanban Markdown extension. Run **"Open Kanban Board"** from the command palette (`Ctrl+Shift+P`).

---

## Phase 0 — Federation Survey Pipeline (2026-02-27)

**Context:** Discarding 61 LLM-generated SubjectConcepts. Domain pack emerges from federation landscape surveys. SubjectConcepts derived from evidence, not pre-defined.

**Phase 0a DONE:** All six surveys run (LCSH, Pleiades, PeriodO, DPRR, WorldCat, LCC). Output in `output/nodes/*.json`. Enriched with semantic_facet. Loaded to Neo4j via load_lcsh_survey, load_federation_survey, load_lcc_nodes.

**Phase 0b DONE:** align_federations.py — 34k nodes, 1k aligned, ~7k edges. Output: output/aligned/roman_republic_aligned.json

**Phase 0c IN PROGRESS:** build_adjacency_matrix.py — adjacency matrix from aligned nodes.

**Pipeline sequence:**
```
survey_lcsh → survey_pleiades → survey_periodo → survey_dprr →
survey_worldcat → survey_lcc → align_federations → build_adjacency_matrix →
apply_rules → synthesis
```

**Key constraint:** Every survey must import `federation_node_schema` and emit `FederationSurvey` JSON.

---

## Prior Phases (Reference)

### Phase A — Close current gaps (no new federations)
1. Trismegistos crosswalk — run existing script, close enrichment gap
2. VIAF — name authority on DPRR persons via P214
3. Noise audit — remaining unscoped clusters beyond Q1764124/Q271108

### Phase B — Foundation federations (activate what's dormant)
4. Pleiades Phase 2 — coordinates, period names, LOCATED_IN on 41,884 Place nodes
5. LGPN forward SPARQL — prosopographic coverage for non-Roman persons
6. Getty AAT — SubjectConcept taxonomy enrichment, prerequisite for SFA quality

### Phase C — Enrichment federations (deepen what's connected)
7. Trismegistos Phase 2 — attestations, primary source claims, non-elite persons
8. EDH — Latin inscriptions as primary source evidence
9. OCD — taxonomy enrichment, SFA grounding corpus

### Phase D — Specialized evidence (SFA-specific)
10. Mercury (CHRR + CRRO) — numismatic evidence chain (geographic foundation exists)
11. Syme index extraction — prosopographic salience weights
12. Further epigraphic sources as needed

**Parallel track (no graph touches):** File restructure + DEV_GUIDE.md, SFA constitution documents, SysML model

---

## Metrics

**Post-DPRR Baseline (2026-02-25):**
- **MEMBER_OF:** 9,144 edges | **Unique entities:** 6,990
- **Scoped:** 91.2% | **Unscoped:** 8.8%
- **Q899409:** 5,363 entities, 0.0% unscoped
- **DPRR:** 2,960 Group A | 1,916 Group C | 9,807 posts | 1,992 status

---

## Notes

**Mercury deprioritization:** See DECISIONS.md D-021. Mercury's evidence chain (person → coin → findspot → place) requires Pleiades Phase 2. Running Mercury before Pleiades Phase 2 builds the middle of a bridge. Coins are important for numismatic/economic SFAs later — not foundational infrastructure.

**Discipline:** Update KANBAN (via extension) + REQUIREMENTS.md in same commit when touching both.

---

## D-035 Status (2026-02-26)

**Not started / stalled.** D12/D13 thresholds exist in graph (SYS_Threshold) but no script reads them. entity_count not populated on SubjectConcept; MCP get_subject_concepts returns null. Blocked until architect specifies which scripts consume D12/D13. entity_count write is unblocked (add to cluster_assignment post-pass).
