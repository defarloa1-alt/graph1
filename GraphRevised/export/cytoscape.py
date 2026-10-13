"""Export the exploration view for Cytoscape: entities as nodes, claims as edges.

    python -m GraphRevised.export.cytoscape [--audit] [--out GraphRevised/exports/graph]

Writes <out>.cyjs (Cytoscape JSON: import in Cytoscape desktop with File >
Import > Network from File, or pass `elements` to Cytoscape.js) and
<out>.html (a self-contained Cytoscape.js page to open in a browser).

Read-only. Everything found is shown at once (25-LIVES-AND-PLAYGROUND.md
decision 2): accepted and proposed claims, every entity (proposed ones too,
and those no claim touches yet), each labelled with its status and source.
An attributed claim reads "proposed · according to <Work>"; an asserted claim
names the Works its evidence comes from, "proposed · from <Work>", counting
evidence still pending on open Proposals (a source system such as Wikidata
where the evidence has no Work; "no evidence" when none is left open). Each entity carries the passages of
note and mentions that concern it. Rejected and superseded claims, deprecated
entities, and dismissed notes appear only with --audit.

Following 06-GRAPH-NAVIGATION.md, a claim is one edge carrying its predicate,
status, mode, sources, and qualifiers; Proposals, source observations, and
Years are left out. A unary claim (such as `occurred`) has no object and is
listed on its subject node. Annotations are included whatever their
visibility, so the output (git-ignored) is the curator's own view. This is a
smoke view, not the explorer (20-EXPLORER-UI.md).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.proposals.temporal import display_edtf

GRAPH_REVISED = Path(__file__).resolve().parents[1]

VISIBLE = ["accepted", "proposed"]
AUDIT = VISIBLE + ["rejected", "superseded"]
OPEN_PROPOSALS = ["submitted", "validating", "deferred"]

ENTITY = "{.id, .label, .shortLabel, .kind, .status, .description}"

ENTITIES = f"""
MATCH (e:Entity) WHERE $audit OR e.status <> "deprecated"
RETURN e {ENTITY} AS entity,
       COLLECT {{
         MATCH (n:Annotation)-[:CONCERNS]->(e) WHERE $audit OR n.status <> "dismissed"
         OPTIONAL MATCH (n)-[:ANNOTATES]->(o:SourceObservation)
         RETURN n {{.id, .kind, .noteType, .note, .status, source: o.shortLabel}} ORDER BY o.shortLabel, n.id
       }} AS notes
"""

CLAIMS = f"""
MATCH (a:Assertion) WHERE a.status IN $statuses
MATCH (a)-[:ASSERTION_SUBJECT]->(s:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(o:Entity)
RETURN a {{.id, .label, .shortLabel, .predicate, .status, .mode, .category, .timeEdtf, .timeSourceExpression}} AS claim,
       s {ENTITY} AS subject, o {ENTITY} AS object,
       COLLECT {{ MATCH (a)-[:ASSERTION_CONTEXT]->(c:Entity) RETURN c.label }}[0] AS context,
       COLLECT {{ MATCH (a)-[:ASSERTION_ROLE]->(r:Entity) RETURN r.label }}[0] AS role,
       COLLECT {{ MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity) RETURN w.label }}[0] AS work,
       COLLECT {{ MATCH (a)-[:SUPPORTED_BY]->(ev:SourceObservation) RETURN DISTINCT ev.id }} AS evidence,
       COLLECT {{ MATCH (p:Proposal)-[:PROPOSES]->(a) WHERE p.status IN $open
                 MATCH (p)-[:PROPOSES_EVIDENCE]->(ev:SourceObservation) RETURN DISTINCT ev.id }} AS pendingEvidence,
       COLLECT {{ MATCH (a)-[:SUPPORTED_BY]->(ev:SourceObservation)
                 OPTIONAL MATCH (ev)-[:IN_WORK]->(w:Entity) RETURN coalesce(w.label, ev.sourceSystem) AS source
                 UNION
                 MATCH (p:Proposal)-[:PROPOSES]->(a) WHERE p.status IN $open
                 MATCH (p)-[:PROPOSES_EVIDENCE]->(ev:SourceObservation)
                 OPTIONAL MATCH (ev)-[:IN_WORK]->(w:Entity) RETURN coalesce(w.label, ev.sourceSystem) AS source
               }} AS sources
"""

STYLE = [
    {"selector": "node", "style": {"label": "data(label)", "font-size": 9, "text-wrap": "wrap",
                                   "text-max-width": 110, "background-color": "#8a8f98", "width": 22, "height": 22}},
    {"selector": "node[kind = 'Person']", "style": {"background-color": "#4f7bd9"}},
    {"selector": "node[kind = 'Group']", "style": {"background-color": "#2fa37a", "shape": "round-rectangle"}},
    {"selector": "node[kind = 'Event']", "style": {"background-color": "#d9822b", "shape": "diamond", "width": 30, "height": 30}},
    {"selector": "node[kind = 'Place']", "style": {"background-color": "#a35fc2", "shape": "triangle"}},
    {"selector": "node[kind = 'Work']", "style": {"background-color": "#b8a13a", "shape": "rectangle"}},
    {"selector": "node[kind = 'Period']", "style": {"background-color": "#3a9fb8", "shape": "barrel", "width": 34}},
    {"selector": "node[kind = 'Concept']", "style": {"background-color": "#c2607f", "shape": "hexagon"}},
    {"selector": "node[status = 'proposed']", "style": {"background-opacity": 0.35, "border-width": 2,
                                                         "border-style": "dashed", "border-color": "#777"}},
    {"selector": "node[status = 'deprecated']", "style": {"opacity": 0.35}},
    {"selector": "edge", "style": {"label": "data(label)", "font-size": 7, "curve-style": "bezier",
                                   "target-arrow-shape": "triangle", "width": 1.5, "line-color": "#666",
                                   "target-arrow-color": "#666", "text-rotation": "autorotate"}},
    {"selector": "edge[status = 'proposed']", "style": {"line-style": "dashed", "line-color": "#b0b0b0",
                                                         "target-arrow-color": "#b0b0b0", "color": "#888"}},
    {"selector": "edge[status = 'rejected']", "style": {"line-style": "dotted", "line-color": "#c0392b",
                                                         "target-arrow-color": "#c0392b", "opacity": 0.6}},
    {"selector": "edge[status = 'superseded']", "style": {"line-style": "dotted", "opacity": 0.45}},
    {"selector": "edge[mode = 'attributed']", "style": {"source-arrow-shape": "circle", "source-arrow-fill": "hollow"}},
]


def status_line(status: str, mode: str, work: str | None, sources: list[str]) -> str:
    """'proposed · according to <Work>' for an attribution; 'proposed · from <Work>, <Work>' for evidence."""
    if mode == "attributed" and work:
        return f"{status} · according to {work}"
    return f"{status} · from {', '.join(sources)}" if sources else f"{status} · no evidence"


def note_line(note: dict[str, Any]) -> str:
    kind = note.get("noteType") if note.get("kind") == "passage-of-note" else note.get("kind")
    where = ", ".join(part for part in (note.get("source"), note.get("status")) if part)
    return f"{kind}: {note.get('note')} ({where})"


def projection(tx: Any, audit: bool = False) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    def node(entity: dict[str, Any], notes: list[dict[str, Any]] = ()) -> None:
        nodes.setdefault(entity["id"], {"data": {
            "id": entity["id"], "label": entity.get("shortLabel") or entity["label"], "fullLabel": entity["label"],
            "kind": entity["kind"], "status": entity.get("status"), "description": entity.get("description"),
            "notes": [note_line(n) for n in notes], "unaryClaims": [],
        }})

    for row in tx.run(ENTITIES, audit=audit):
        node(row["entity"], row["notes"])
    for row in tx.run(CLAIMS, statuses=AUDIT if audit else VISIBLE, open=OPEN_PROPOSALS):
        claim, subject, obj = row["claim"], row["subject"], row["object"]
        node(subject)  # an endpoint hidden from the entity list (deprecated) still anchors its claim
        mode = claim.get("mode") or "asserted"
        sources = sorted(row["sources"])
        time = (display_edtf(claim["timeEdtf"]) if claim.get("timeEdtf") else claim.get("timeSourceExpression"))
        data = {
            "predicate": claim["predicate"], "status": claim["status"], "mode": mode,
            "category": claim.get("category"), "attributedTo": row["work"], "sources": sources,
            "statusLine": status_line(claim["status"], mode, row["work"], sources),
            "role": row["role"], "context": row["context"], "time": time,
            "evidence": len(row["evidence"]), "pendingEvidence": len(row["pendingEvidence"]),
            "fullLabel": claim["label"],
        }
        if obj is None:
            nodes[subject["id"]]["data"]["unaryClaims"].append(f"{claim['label']} — {data['statusLine']}")
            continue
        node(obj)
        edges.append({"data": {"id": claim["id"], "source": subject["id"], "target": obj["id"],
                               "label": claim["predicate"], **data}})
    return {"elements": {"nodes": list(nodes.values()), "edges": edges}}


HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Graph Smoke View</title>
<style>
  :root {{ --bg: #fbfbfa; --fg: #1d1d1f; --muted: #6b6b70; --panel: #ffffff; --line: #e3e3e0; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg: #17181a; --fg: #ececec; --muted: #9a9aa0; --panel: #222326; --line: #333; }} }}
  html, body {{ margin: 0; height: 100%; background: var(--bg); color: var(--fg); font: 13px/1.4 system-ui, sans-serif; }}
  #cy {{ position: absolute; inset: 0 320px 0 0; }}
  #card {{ position: absolute; top: 0; right: 0; bottom: 0; width: 320px; box-sizing: border-box; padding: 16px;
          overflow: auto; background: var(--panel); border-left: 1px solid var(--line); }}
  #card h2 {{ font-size: 15px; margin: 0 0 8px; }} #card dt {{ color: var(--muted); margin-top: 8px; }} #card dd {{ margin: 0; }}
  #card ul {{ margin: 0; padding-left: 18px; }} #card li {{ margin-bottom: 4px; }}
  @media (max-width: 700px) {{ #cy {{ inset: 0 0 45% 0; }} #card {{ top: 55%; width: 100%; border-left: 0; border-top: 1px solid var(--line); }} }}
</style></head>
<body><div id="cy"></div><aside id="card"><h2>Click a node or claim</h2>
<p>Solid: accepted. Dashed: proposed. Hollow circle at the start: "according to" a source.
Faded with a dashed border: a proposed entity. Nothing here is hidden for being unreviewed.</p></aside>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js"></script>
<script>
const graph = {graph};
const cy = cytoscape({{ container: document.getElementById("cy"), elements: graph.elements, style: {style},
                        layout: {{ name: "cose", animate: false, nodeRepulsion: 9000, idealEdgeLength: 120 }} }});
const card = document.getElementById("card");
const esc = s => String(s ?? "").replace(/[&<>]/g, c => ({{"&": "&amp;", "<": "&lt;", ">": "&gt;"}}[c]));
function show(title, fields) {{
  card.innerHTML = `<h2>${{esc(title)}}</h2><dl>` + fields.filter(([, v]) => v !== null && v !== undefined && v !== "" &&
    !(Array.isArray(v) && !v.length)).map(([k, v]) => `<dt>${{esc(k)}}</dt><dd>${{Array.isArray(v) ?
    "<ul>" + v.map(item => `<li>${{esc(item)}}</li>`).join("") + "</ul>" : esc(v)}}</dd>`).join("") + "</dl>";
}}
cy.on("tap", "node", e => {{ const d = e.target.data(); show(d.fullLabel, [["kind", d.kind], ["status", d.status],
  ["description", d.description], ["unary claims", d.unaryClaims], ["passages of note and mentions", d.notes],
  ["id", d.id]]); }});
cy.on("tap", "edge", e => {{ const d = e.target.data(); show(d.fullLabel, [["status", d.statusLine],
  ["predicate", d.predicate], ["mode", d.mode], ["category", d.category], ["role", d.role], ["during", d.context],
  ["time", d.time], ["evidence", d.evidence], ["pending evidence", d.pendingEvidence], ["claim id", d.id]]); }});
</script></body></html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audit", action="store_true",
                        help="also show rejected and superseded claims, deprecated entities, and dismissed notes")
    parser.add_argument("--out", type=Path, default=GRAPH_REVISED / "exports" / "graph")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            graph = session.execute_read(projection, args.audit)
    finally:
        driver.close()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cyjs = {"format_version": "1.0", "generated_by": "GraphRevised.export.cytoscape", "data": {"name": args.out.stem},
            **graph}
    args.out.with_suffix(".cyjs").write_text(json.dumps(cyjs, ensure_ascii=False, indent=1), encoding="utf-8")
    page = HTML.format(graph=json.dumps(graph, ensure_ascii=False).replace("</", "<\\/"), style=json.dumps(STYLE))
    args.out.with_suffix(".html").write_text(page, encoding="utf-8")
    elements = graph["elements"]
    print(f"{len(elements['nodes'])} nodes, {len(elements['edges'])} claim edges")
    print(f"{args.out.with_suffix('.cyjs')}\n{args.out.with_suffix('.html')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
