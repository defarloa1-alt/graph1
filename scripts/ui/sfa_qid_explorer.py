#!/usr/bin/env python3
"""
SFA QID Explorer — Simple Gradio UI for QID → Rich Data.

Input a Wikidata QID (e.g. Q17167 Roman Republic) and facet to see:
- Academic discipline placement (Dewey, LCC, LCSH)
- Bibliography (WorldCat, Open Syllabus, OpenAlex)
- Online texts (Internet Archive, TOC links)
- SFA categorizations for schema design

Uses pre-built output from:
  1. export_federated_roman_republic.py (Neo4j)
  2. sfa_scope_federated_view.py
  3. sfa_enrich_scoped_with_bibliography.py

Launch:
  pip install gradio
  python scripts/ui/sfa_qid_explorer.py

Then open: http://localhost:7861
"""

import csv
import io
import json
import os
import sys
import tempfile
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))

try:
    import gradio as gr
except ImportError:
    print("Install gradio: pip install gradio")
    sys.exit(1)

SFA_SCOPED_DIR = _root / "output" / "sfa_scoped"
REPORTS_DIR = _root / "output" / "reports"
WORLDCAT_PATH = _root / "output" / "nodes" / "worldcat_roman_republic.json"


def _find_latest_scoped(facet: str, seed_qid: str) -> Path | None:
    """Find latest scoped file, prefer _bibliography.json."""
    dir_path = SFA_SCOPED_DIR.resolve()
    if not dir_path.exists():
        return None
    pattern = f"{facet}_{seed_qid}_*.json"
    files = sorted(dir_path.glob(pattern))
    if not files:
        return None
    # Prefer bibliography-enriched (exclude _bibliography_bibliography chains)
    bib = [f for f in files if "_bibliography.json" in f.name and "_bibliography_bibliography" not in f.name]
    return Path(bib[-1]) if bib else Path(files[-1])


def load_scoped_data(facet: str, seed_qid: str, file_path: str | None = None) -> tuple[dict | None, str]:
    """Load scoped JSON. Returns (data, status_message). file_path overrides auto-find."""
    path = None
    if file_path and file_path.strip():
        p = Path(file_path.strip())
        if p.exists():
            path = p
    if not path:
        path = _find_latest_scoped(facet, seed_qid)
    if not path or not path.exists():
        search_dir = SFA_SCOPED_DIR.resolve()
        return None, (
            f"No scoped data for {facet} / {seed_qid}.\n\n"
            f"Search path: {search_dir}\n"
            f"Pattern: {facet}_{seed_qid}_*.json\n\n"
            f"Run:\n  1. export_federated_roman_republic.py\n"
            f"  2. sfa_scope_federated_view.py --facet {facet}\n"
            f"  3. sfa_enrich_scoped_with_bibliography.py\n\n"
            f"Or paste a file path above."
        )
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data, f"Loaded: {path.name}"
    except Exception as e:
        return None, f"Error: {e}"


def _format_md_section(title: str, items: list, fmt_fn) -> str:
    lines = [f"## {title}\n"]
    for i, item in enumerate(items[:20], 1):
        lines.append(f"### {i}. {fmt_fn(item)}")
    if len(items) > 20:
        lines.append(f"\n*... and {len(items) - 20} more*")
    return "\n".join(lines)


def _build_overview(data: dict) -> str:
    out = data.get("output", data)
    facet = out.get("facet", "")
    seed = out.get("seed_qid", "")
    lines = [
        f"# QID → Rich Data: {seed} ({facet})",
        "",
        "## Summary",
        f"- **Facet:** {facet}",
        f"- **Seed QID:** {seed}",
        f"- **Scoped disciplines:** {len(out.get('scoped_disciplines', []))}",
        f"- **Scoped LCC:** {len(out.get('scoped_lcc', []))}",
        f"- **Scoped LCSH:** {len(out.get('scoped_lcsh', []))}",
        f"- **Scoped entities:** {len(out.get('scoped_entities', []))}",
        "",
        "## SFA Rationale",
        out.get("sfa_rationale", "") or "(none)",
    ]
    return "\n".join(lines)


def _build_disciplines_md(data: dict) -> str:
    items = data.get("output", {}).get("scoped_disciplines", [])
    def fmt(d):
        ids = [f"Dewey={d.get('dewey')}", f"LCC={d.get('lcc')}", f"LCSH={d.get('lcsh_id')}"]
        ids = [x for x in ids if x and "=None" not in x]
        return f"**{d.get('label', '')}** — {', '.join(ids)}\n\n{d.get('rationale', '')[:200]}..."
    return _format_md_section("Scoped Disciplines", items, fmt)


def _build_lcc_md(data: dict) -> str:
    items = data.get("output", {}).get("scoped_lcc", [])
    def fmt(d):
        return f"**{d.get('code', '')}** — {d.get('label', '')}\n\n{d.get('rationale', '')[:200]}..."
    return _format_md_section("Scoped LCC", items, fmt)


def _build_lcsh_md(data: dict) -> str:
    items = data.get("output", {}).get("scoped_lcsh", [])
    def fmt(d):
        res = d.get("lcsh_resolved") or {}
        label = res.get("label") or d.get("label", "")
        bt = res.get("broader", [])
        nt = res.get("narrower", [])
        extra = f"  BT: {[x['id'] for x in bt]}" if bt else ""
        extra += f"  NT: {[x['id'] for x in nt]}" if nt else ""
        return f"**{d.get('lcsh_id', '')}** — {label}\n{extra}\n\n{d.get('rationale', '')[:150]}..."
    return _format_md_section("Scoped LCSH", items, fmt)


def _build_bibliography_md(data: dict) -> str:
    out = data.get("output", {})
    all_bib = []
    for section in ("scoped_disciplines", "scoped_lcc", "scoped_lcsh"):
        for item in out.get(section, []):
            for b in item.get("bibliography", [])[:5]:
                b["_section"] = item.get("label", item.get("code", ""))[:40]
                all_bib.append(b)
    seen = set()
    unique = []
    for b in all_bib:
        k = (b.get("title") or "").lower()[:60]
        if k and k not in seen:
            seen.add(k)
            unique.append(b)
    lines = ["## Bibliography (sample)\n"]
    for i, b in enumerate(unique[:30], 1):
        title = b.get("title", "")
        authors = b.get("authors", "")
        uri = b.get("uri", "")
        ia = b.get("ia_url", "")
        toc = b.get("toc_url", "")
        src = b.get("source", "")
        section = b.get("_section", "")
        links = []
        if uri:
            links.append(f"[Open Library]({uri})")
        if ia:
            links.append(f"[Internet Archive]({ia})")
        if toc:
            links.append(f"[TOC]({toc})")
        lines.append(f"### {i}. {title}")
        if authors:
            lines.append(f"*{authors}*")
        lines.append(f"  Section: {section} | Source: {src}")
        if links:
            lines.append("  " + " | ".join(links))
        lines.append("")
    return "\n".join(lines)


def _build_schema_nodes_md(data: dict) -> str:
    """All nodes the SFA considers when defining its schema — disciplines, LCC, LCSH, entities."""
    out = data.get("output", {})
    lines = [
        "# Schema Nodes — SFA Input",
        "",
        "These are the nodes the SFA will consider when it starts to define its schema.",
        "",
        "---",
        "",
    ]
    n = 0
    # Disciplines
    for d in out.get("scoped_disciplines", []):
        n += 1
        ids = [x for x in [f"QID={d.get('qid')}", f"Dewey={d.get('dewey')}", f"LCC={d.get('lcc')}", f"LCSH={d.get('lcsh_id')}"] if x and "=None" not in x]
        lines.append(f"**{n}. [DISCIPLINE]** {d.get('label', '')}")
        lines.append(f"   {', '.join(ids)}")
        lines.append(f"   *{d.get('rationale', '')[:180]}...*")
        lines.append("")
    # LCC
    for d in out.get("scoped_lcc", []):
        n += 1
        lines.append(f"**{n}. [LCC]** {d.get('code', '')} — {d.get('label', '')}")
        lines.append(f"   *{d.get('rationale', '')[:180]}...*")
        lines.append("")
    # LCSH
    for d in out.get("scoped_lcsh", []):
        n += 1
        res = d.get("lcsh_resolved") or {}
        label = res.get("label") or d.get("label", "")
        lines.append(f"**{n}. [LCSH]** {d.get('lcsh_id', '')} — {label}")
        lines.append(f"   *{d.get('rationale', '')[:180]}...*")
        lines.append("")
    # Entities
    for d in out.get("scoped_entities", []):
        n += 1
        lines.append(f"**{n}. [ENTITY]** {d.get('qid', '')} — {d.get('label', '')} ({d.get('entity_type', '')})")
        lines.append(f"   *{d.get('rationale', '')[:180]}...*")
        lines.append("")
    lines.append(f"---\n**Total: {n} schema nodes**")
    return "\n".join(lines)


def _build_online_texts_md(data: dict) -> str:
    out = data.get("output", {})
    with_ia = []
    for section in ("scoped_disciplines", "scoped_lcc", "scoped_lcsh"):
        for item in out.get(section, []):
            for b in item.get("bibliography", []):
                if b.get("ia_url"):
                    with_ia.append(b)
    seen = set()
    unique = []
    for b in with_ia:
        k = b.get("ia_url", "")
        if k and k not in seen:
            seen.add(k)
            unique.append(b)
    lines = ["## Works with Internet Archive full text\n"]
    for i, b in enumerate(unique[:25], 1):
        lines.append(f"{i}. [{b.get('title', '')}]({b.get('ia_url')}) — {b.get('authors', '')}")
    return "\n".join(lines)


def to_csv(data: dict) -> str:
    """Comprehensive CSV: all tabs, all resources. LLM-ready for schema consolidation."""
    out = data.get("output", {})
    buf = io.StringIO()
    w = csv.writer(buf)

    # --- META (Overview) ---
    w.writerow(["#META", "facet", out.get("facet", "")])
    w.writerow(["#META", "seed_qid", out.get("seed_qid", "")])
    w.writerow(["#META", "disciplines_count", len(out.get("scoped_disciplines", []))])
    w.writerow(["#META", "lcc_count", len(out.get("scoped_lcc", []))])
    w.writerow(["#META", "lcsh_count", len(out.get("scoped_lcsh", []))])
    w.writerow(["#META", "entities_count", len(out.get("scoped_entities", []))])
    w.writerow([])

    # --- SCHEMA NODES (Disciplines, LCC, LCSH, Entities) ---
    w.writerow(["#SCHEMA_NODES", "TYPE", "QID", "LABEL", "DEWEY", "LCC", "LCSH_ID", "BROADER", "NARROWER", "RATIONALE"])
    for d in out.get("scoped_disciplines", []):
        w.writerow(["discipline", d.get("qid"), d.get("label"), d.get("dewey"), d.get("lcc"), d.get("lcsh_id"), "", "", (d.get("rationale") or "")[:300]])
    for d in out.get("scoped_lcc", []):
        w.writerow(["lcc", "", d.get("label"), "", d.get("code"), "", "", "", (d.get("rationale") or "")[:300]])
    for d in out.get("scoped_lcsh", []):
        res = d.get("lcsh_resolved") or {}
        label = res.get("label") or d.get("label", "")
        bt = "; ".join(x.get("id", "") for x in res.get("broader", []))
        nt = "; ".join(x.get("id", "") for x in res.get("narrower", []))
        w.writerow(["lcsh", "", label, "", "", d.get("lcsh_id"), bt, nt, (d.get("rationale") or "")[:300]])
    for d in out.get("scoped_entities", []):
        w.writerow(["entity", d.get("qid"), d.get("label"), "", "", "", "", "", (d.get("rationale") or "")[:300]])
    w.writerow([])

    # --- BIBLIOGRAPHY (all entries from all sections, full columns) ---
    bib_cols = ["#BIBLIOGRAPHY", "SECTION", "TITLE", "AUTHORS", "SOURCE", "URI", "IA_URL", "TOC_URL", "OA_URL",
                "GALAXY_SEARCH_URL", "PUBLISHER", "YEAR", "MATCH_COUNT", "FIELD", "OPENALEX_ID", "DOI"]
    w.writerow(bib_cols)
    for section_key, section_label in [
        ("scoped_disciplines", "label"),
        ("scoped_lcc", "code"),
        ("scoped_lcsh", "lcsh_id"),
        ("scoped_entities", "label"),
    ]:
        for item in out.get(section_key, []):
            sec_val = item.get(section_label, item.get("label", item.get("code", "")))[:50]
            for b in item.get("bibliography", []):
                w.writerow([
                    "",
                    sec_val,
                    b.get("title", ""),
                    b.get("authors", ""),
                    b.get("source", ""),
                    b.get("uri", ""),
                    b.get("ia_url", ""),
                    b.get("toc_url", ""),
                    b.get("oa_url", ""),
                    b.get("galaxy_search_url", ""),
                    b.get("publisher", ""),
                    str(b.get("year", "")),
                    str(b.get("match_count", "")),
                    b.get("field", ""),
                    b.get("openalex_id", ""),
                    b.get("doi", ""),
                ])
    w.writerow([])

    # --- ONLINE TEXTS (works with Internet Archive full text) ---
    w.writerow(["#ONLINE_TEXTS", "SECTION", "TITLE", "AUTHORS", "IA_URL", "TOC_URL", "PUBLISHER", "YEAR"])
    seen_ia = set()
    for section_key, section_label in [
        ("scoped_disciplines", "label"),
        ("scoped_lcc", "code"),
        ("scoped_lcsh", "lcsh_id"),
        ("scoped_entities", "label"),
    ]:
        for item in out.get(section_key, []):
            sec_val = item.get(section_label, item.get("label", item.get("code", "")))[:50]
            for b in item.get("bibliography", []):
                ia = b.get("ia_url", "")
                if ia and ia not in seen_ia:
                    seen_ia.add(ia)
                    w.writerow([
                        sec_val,
                        b.get("title", ""),
                        b.get("authors", ""),
                        ia,
                        b.get("toc_url", ""),
                        b.get("publisher", ""),
                        str(b.get("year", "")),
                    ])
    return buf.getvalue()


def to_json_llm(data: dict) -> dict:
    """Consolidated structure for LLM schema proposal. All tabs, all resources."""
    out = data.get("output", {})
    schema_nodes = []
    for d in out.get("scoped_disciplines", []):
        schema_nodes.append({"type": "discipline", "qid": d.get("qid"), "label": d.get("label"),
                             "dewey": d.get("dewey"), "lcc": d.get("lcc"), "lcsh_id": d.get("lcsh_id"),
                             "rationale": d.get("rationale")})
    for d in out.get("scoped_lcc", []):
        schema_nodes.append({"type": "lcc", "code": d.get("code"), "label": d.get("label"),
                             "rationale": d.get("rationale")})
    for d in out.get("scoped_lcsh", []):
        res = d.get("lcsh_resolved") or {}
        schema_nodes.append({"type": "lcsh", "lcsh_id": d.get("lcsh_id"),
                             "label": res.get("label") or d.get("label"),
                             "broader": [x.get("id") for x in res.get("broader", [])],
                             "narrower": [x.get("id") for x in res.get("narrower", [])],
                             "rationale": d.get("rationale")})
    for d in out.get("scoped_entities", []):
        schema_nodes.append({"type": "entity", "qid": d.get("qid"), "label": d.get("label"),
                             "entity_type": d.get("entity_type"), "rationale": d.get("rationale")})

    bibliography = []
    for section_key, section_label in [
        ("scoped_disciplines", "label"), ("scoped_lcc", "code"),
        ("scoped_lcsh", "lcsh_id"), ("scoped_entities", "label"),
    ]:
        for item in out.get(section_key, []):
            sec = item.get(section_label, item.get("label", item.get("code", "")))
            for b in item.get("bibliography", []):
                bibliography.append({
                    "section": sec,
                    "title": b.get("title"), "authors": b.get("authors"),
                    "source": b.get("source"), "uri": b.get("uri"),
                    "ia_url": b.get("ia_url"), "toc_url": b.get("toc_url"), "oa_url": b.get("oa_url"),
                    "galaxy_search_url": b.get("galaxy_search_url"),
                    "publisher": b.get("publisher"), "year": b.get("year"),
                    "match_count": b.get("match_count"), "field": b.get("field"),
                    "openalex_id": b.get("openalex_id"), "doi": b.get("doi"),
                })

    online_texts = []
    seen_ia = set()
    for section_key, section_label in [
        ("scoped_disciplines", "label"), ("scoped_lcc", "code"),
        ("scoped_lcsh", "lcsh_id"), ("scoped_entities", "label"),
    ]:
        for item in out.get(section_key, []):
            sec = item.get(section_label, item.get("label", item.get("code", "")))
            for b in item.get("bibliography", []):
                ia = b.get("ia_url")
                if ia and ia not in seen_ia:
                    seen_ia.add(ia)
                    online_texts.append({
                        "section": sec, "title": b.get("title"), "authors": b.get("authors"),
                        "ia_url": ia, "toc_url": b.get("toc_url"),
                        "publisher": b.get("publisher"), "year": b.get("year"),
                    })

    return {
        "meta": {"facet": out.get("facet"), "seed_qid": out.get("seed_qid"),
                 "sfa_rationale": out.get("sfa_rationale"),
                 "counts": {"disciplines": len(out.get("scoped_disciplines", [])),
                           "lcc": len(out.get("scoped_lcc", [])),
                           "lcsh": len(out.get("scoped_lcsh", [])),
                           "entities": len(out.get("scoped_entities", [])),
                           "bibliography": len(bibliography), "online_texts": len(online_texts)}},
        "schema_nodes": schema_nodes,
        "bibliography": bibliography,
        "online_texts": online_texts,
        "prompt_hint": "Use this data to propose a consolidated schema for the SFA. These are pure subjects (disciplines, LCC, LCSH, entities). SubjectConcept layer comes later. Consider bibliography as evidence. Output suitable for D9 constitution layer population.",
    }


def run_explorer(facet: str, seed_qid: str, file_path: str | None = None) -> tuple[str, str, str, str, str, str, str, str, str]:
    """Load data and return (overview, schema_nodes, disciplines, lcc, lcsh, bibliography, online, csv, json)."""
    data, status = load_scoped_data(facet, seed_qid, file_path)
    if not data:
        return status, "", "", "", "", "", "", "", ""
    overview = _build_overview(data)
    schema_nodes = _build_schema_nodes_md(data)
    disciplines = _build_disciplines_md(data)
    lcc = _build_lcc_md(data)
    lcsh = _build_lcsh_md(data)
    bibliography = _build_bibliography_md(data)
    online = _build_online_texts_md(data)
    csv_str = to_csv(data)
    json_str = json.dumps(to_json_llm(data), indent=2, ensure_ascii=False)
    return overview, schema_nodes, disciplines, lcc, lcsh, bibliography, online, csv_str, json_str


def main():
    with gr.Blocks(title="SFA QID Explorer") as demo:
        gr.Markdown("""
        # SFA QID Explorer

        **Input a Wikidata QID** to see where it sits in academic disciplines and bibliographic worlds,
        what texts are available online, and related books. SFA categorizations inform schema design.

        Uses pre-built data from `output/sfa_scoped/`. Run the pipeline first if needed.
        """)

        with gr.Row():
            qid_input = gr.Textbox(label="Seed QID", value="Q17167", placeholder="Q17167")
            facet_input = gr.Dropdown(
                label="Facet",
                choices=["POLITICAL", "MILITARY", "LEGAL", "SOCIAL", "ECONOMIC", "RELIGIOUS", "CULTURAL", "GEOGRAPHIC"],
                value="POLITICAL",
            )
            load_btn = gr.Button("Load", variant="primary")
        default_path = str((_root / "output" / "sfa_scoped" / "POLITICAL_Q17167_20260302_170241_bibliography.json").resolve())
        file_path_input = gr.Textbox(
            label="Or paste file path (overrides auto-find)",
            placeholder=default_path,
            value=default_path if (SFA_SCOPED_DIR / "POLITICAL_Q17167_20260302_170241_bibliography.json").exists() else "",
            lines=1,
        )

        status_box = gr.Textbox(label="Status", value="Enter QID and facet, then click Load.", interactive=False)

        with gr.Accordion("Schema Nodes — all nodes the SFA considers when defining its schema", open=True):
            schema_nodes_out = gr.Markdown(value="Click **Load** to populate.")

        with gr.Tabs():
            with gr.Tab("Overview"):
                overview_out = gr.Markdown()
            with gr.Tab("Disciplines"):
                disciplines_out = gr.Markdown()
            with gr.Tab("LCC"):
                lcc_out = gr.Markdown()
            with gr.Tab("LCSH"):
                lcsh_out = gr.Markdown()
            with gr.Tab("Bibliography"):
                bibliography_out = gr.Markdown()
            with gr.Tab("Online Texts"):
                online_out = gr.Markdown()

        csv_out = gr.Textbox(label="CSV Export (comprehensive: all tabs, all resources)", lines=10, interactive=False)
        with gr.Row():
            csv_download = gr.DownloadButton(label="Download CSV")
            json_download = gr.DownloadButton(label="Download JSON (LLM-ready)")

        def on_load(facet, qid, fp):
            o, sn, d, l, lc, b, on, c, j = run_explorer(facet, qid.strip(), fp or None)
            csv_path = json_path = None
            csv_preview = ""
            if c:
                p = _root / "output" / "sfa_scoped" / "sfa_export.csv"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(c, encoding="utf-8")
                csv_path = str(p)
                csv_preview = c[:3000] + "..." if len(c) > 3000 else c
            if j:
                pj = _root / "output" / "sfa_scoped" / "sfa_export_llm.json"
                pj.parent.mkdir(parents=True, exist_ok=True)
                pj.write_text(j, encoding="utf-8")
                json_path = str(pj)
            return (
                o,
                csv_preview,
                csv_path,
                json_path,
                o, sn, d, l, lc, b, on,
            )

        load_btn.click(
            fn=on_load,
            inputs=[facet_input, qid_input, file_path_input],
            outputs=[status_box, csv_out, csv_download, json_download, overview_out, schema_nodes_out, disciplines_out, lcc_out, lcsh_out, bibliography_out, online_out],
        )

        gr.Markdown("""
        ---
        **Pipeline:** `export_federated_roman_republic.py` → `sfa_scope_federated_view.py` → `sfa_enrich_scoped_with_bibliography.py`
        """)

    demo.launch(
        server_name="0.0.0.0",  # Bind all interfaces; use http://127.0.0.1:7862 or http://localhost:7862
        server_port=7862,
        share=False,
        theme=gr.themes.Soft(),
        inbrowser=True,  # Auto-open browser after server is ready
    )


if __name__ == "__main__":
    main()
