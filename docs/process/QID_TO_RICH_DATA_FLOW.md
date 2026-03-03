# QID → Rich Data Flow

**Purpose:** Single QID input yields discipline placement, bibliography, online texts, and SFA categorizations. **Goal:** Consolidate all of this into a proposed schema (e.g. via independent LLM).

**Status:** Implemented (2026-03-02)

---

## Pipeline

| Step | Script | Input | Output | Requires |
|------|--------|-------|--------|----------|
| 1 | `export_federated_roman_republic.py` | Neo4j graph | `output/reports/federated_roman_republic_*.json` | Neo4j |
| 2 | `sfa_scope_federated_view.py` | Federated JSON | `output/sfa_scoped/{FACET}_{SEED}_*.json` | ANTHROPIC_API_KEY |
| 3 | `sfa_enrich_scoped_with_bibliography.py` | Scoped JSON | `*_bibliography.json` | WorldCat, OpenAlex, Open Syllabus, optional LCSH/Dewey/LCC |

---

## What the User Sees

1. **Academic discipline placement** — Dewey, LCC, LCSH with explanations
2. **Bibliographic landscape** — WorldCat, Open Syllabus, OpenAlex
3. **Online texts** — Internet Archive (`ia_url`), LOC TOC (`toc_url`)
4. **SFA categorizations** — Scoped disciplines, LCC, LCSH, entities for schema design

---

## UI

**Gradio:** `scripts/ui/sfa_qid_explorer.py`

```bash
python scripts/ui/sfa_qid_explorer.py
# Open http://localhost:7861
```

**Launch:** `scripts/launchers/launch_sfa_qid_explorer.bat`

- Input: QID (default Q17167), Facet (default POLITICAL)
- Tabs: Overview, Disciplines, LCC, LCSH, Bibliography, Online Texts
- **CSV export** — Comprehensive: all tabs, all resources (META, SCHEMA_NODES, BIBLIOGRAPHY, ONLINE_TEXTS)
- **JSON export (LLM-ready)** — Consolidated structure for schema proposal: meta, schema_nodes, bibliography, online_texts, prompt_hint

---

## Self-Describing System

When `SYS_ProcessRegistry` is populated, add:

```cypher
CREATE (p:SYS_Process {
  name: "QID_TO_RICH_DATA",
  description: "QID input → discipline placement, bibliography, online texts, SFA scope",
  pipeline: ["export_federated", "sfa_scope", "sfa_enrich"],
  ui_entry: "scripts/ui/sfa_qid_explorer.py",
  port: 7861
})
```
