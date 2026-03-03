#!/usr/bin/env python3
"""
Export Federated Roman Republic View — Actual results from Neo4j.

Queries the graph and writes a markdown report + JSON with:
  - Subject positioning (POSITIONED_AS chain)
  - Discipline tree with Dewey, LCC, LCSH, FAST
  - Entity ontology (institutions, places)
  - Stats

Usage:
  python scripts/agents/export_federated_roman_republic.py
  python scripts/agents/export_federated_roman_republic.py --out output/reports
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

try:
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = None

SEED_QID = "Q17167"


def run(session, query: str, **params):
    r = session.run(query, **params)
    return [dict(rec) for rec in r]


def export(seed_qid: str = SEED_QID, out_dir: Path | None = None) -> dict:
    out_dir = out_dir or _root / "output" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if not GraphDatabase or not NEO4J_PASSWORD:
        raise RuntimeError("Neo4j not configured. Set NEO4J_PASSWORD in .env")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    data = {"seed_qid": seed_qid, "exported_at": datetime.now(timezone.utc).isoformat(), "sections": {}}

    try:
        with driver.session() as session:
            # 1. POSITIONED_AS chain
            positioned = run(session, """
                MATCH (sc)-[r:POSITIONED_AS]->(target)
                WHERE sc.qid = $seed
                RETURN target.qid AS qid, target.label AS label,
                       r.rel_type AS rel_type, r.hops AS hops
                ORDER BY r.hops, target.qid
            """, seed=seed_qid)
            data["sections"]["positioned_as"] = positioned

            # 2. Disciplines with authority IDs (Roman Republic–relevant: history, politic, classic, roman)
            disciplines_all = run(session, """
                MATCH (d:Discipline)
                WHERE d.fast_id IS NOT NULL OR d.lcc IS NOT NULL OR d.lcsh_id IS NOT NULL OR d.ddc IS NOT NULL
                RETURN d.qid AS qid, d.label AS label,
                       d.ddc AS dewey, d.lcc AS lcc, d.lcsh_id AS lcsh_id, d.fast_id AS fast_id,
                       d.gnd_id AS gnd_id, d.aat_id AS aat_id
                ORDER BY d.label
                LIMIT 500
            """)
            # Filter for Roman Republic relevance
            keywords = ["roman", "rome", "politic", "history", "classic", "ancient", "republic", "law", "military"]
            relevant = [d for d in disciplines_all if any(k in (d.get("label") or "").lower() for k in keywords)]
            data["sections"]["disciplines_relevant"] = relevant[:80]
            data["sections"]["disciplines_sample"] = disciplines_all[:50]
            data["sections"]["discipline_total_with_auth"] = len(disciplines_all)

            # 3. Entity ontology
            ontology = run(session, """
                MATCH (e:Entity)
                WHERE e.qid IN $qids
                   OR (e.entity_type IN ['Organization', 'Event', 'Place', 'ORGANIZATION', 'PLACE', 'EVENT'] AND e.dprr_uri IS NULL)
                RETURN e.qid AS qid, e.label AS label, e.entity_type AS entity_type
                ORDER BY CASE WHEN e.qid IN $qids THEN 0 ELSE 1 END, e.label
                LIMIT 50
            """, qids=["Q130614", "Q842606", "Q1114821", "Q17167", "Q1747689", "Q220"])
            data["sections"]["entity_ontology"] = ontology

            # 4. LCC_Class if present
            try:
                lcc = run(session, """
                    MATCH (l:LCC_Class)
                    WHERE l.code IS NOT NULL
                    RETURN l.code AS code, l.label AS label
                    ORDER BY l.code
                    LIMIT 100
                """)
                data["sections"]["lcc_classes"] = lcc
            except Exception:
                data["sections"]["lcc_classes"] = []

            # 5. LCSH if present
            try:
                lcsh = run(session, """
                    MATCH (l:LCSH_Heading)
                    RETURN l.lcsh_id AS lcsh_id, l.label AS label
                    ORDER BY l.label
                    LIMIT 50
                """)
                data["sections"]["lcsh_headings"] = lcsh
            except Exception:
                data["sections"]["lcsh_headings"] = []

    finally:
        driver.close()

    # Write JSON
    json_path = out_dir / f"federated_roman_republic_{ts}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    data["_json_path"] = str(json_path)

    # Write Markdown
    md_path = out_dir / f"federated_roman_republic_{ts}.md"
    md = build_markdown(data)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    data["_md_path"] = str(md_path)

    print(f"Exported:")
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")
    return data


def build_markdown(data: dict) -> str:
    sections = data.get("sections", {})
    lines = [
        "# Federated Roman Republic View",
        "",
        f"**Seed:** {data['seed_qid']} | **Exported:** {data['exported_at']}",
        "",
        "---",
        "",
        "## 1. Subject Positioning (POSITIONED_AS)",
        "",
    ]
    for p in sections.get("positioned_as", []):
        lines.append(f"- **{p['qid']}** {p['label']} (hops={p.get('hops')}, {p.get('rel_type')})")
    lines.extend(["", "---", "", "## 2. Discipline Tree (Dewey, LCC, LCSH, FAST)", ""])
    lines.append(f"*Total with authority IDs: {sections.get('discipline_total_with_auth', 0)}*")
    lines.append("")
    lines.append("### Roman Republic–relevant disciplines")
    lines.append("")
    for d in sections.get("disciplines_relevant", [])[:40]:
        ids = []
        if d.get("dewey"): ids.append(f"Dewey={d['dewey']}")
        if d.get("lcc"): ids.append(f"LCC={d['lcc']}")
        if d.get("lcsh_id"): ids.append(f"LCSH={d['lcsh_id']}")
        if d.get("fast_id"): ids.append(f"FAST={d['fast_id']}")
        ids_str = " | ".join(ids) if ids else "—"
        lines.append(f"- **{d['qid']}** {d.get('label', '')[:50]}")
        lines.append(f"  {ids_str}")
    lines.extend(["", "### Sample (all disciplines)", ""])
    for d in sections.get("disciplines_sample", [])[:20]:
        ids = [f"{k}={v}" for k, v in [("Dewey", d.get("dewey")), ("LCC", d.get("lcc")), ("LCSH", d.get("lcsh_id")), ("FAST", d.get("fast_id"))] if v]
        lines.append(f"- {d['qid']} {d.get('label', '')[:45]}: {', '.join(ids)}")
    lines.extend(["", "---", "", "## 3. Entity Ontology (institutions, places)", ""])
    for e in sections.get("entity_ontology", [])[:30]:
        lines.append(f"- **{e['qid']}** {e.get('label', '')[:50]} ({e.get('entity_type', '')})")
    if sections.get("lcc_classes"):
        lines.extend(["", "---", "", "## 4. LCC Classes", ""])
        for l in sections["lcc_classes"][:30]:
            lines.append(f"- {l.get('code')} {l.get('label', '')[:50]}")
    if sections.get("lcsh_headings"):
        lines.extend(["", "---", "", "## 5. LCSH Headings", ""])
        for l in sections["lcsh_headings"][:30]:
            lines.append(f"- {l.get('lcsh_id')} {l.get('label', '')[:50]}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Export federated Roman Republic view from Neo4j")
    parser.add_argument("--seed", default=SEED_QID, help="Seed QID")
    parser.add_argument("--out", type=Path, default=None, help="Output directory")
    args = parser.parse_args()
    export(seed_qid=args.seed, out_dir=args.out)


if __name__ == "__main__":
    main()
