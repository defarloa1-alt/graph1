"""Hand the exploration view to Cytoscape Desktop.

    python GraphRevised/explorer/cytoscape_desktop.py            # write exports/graph-desktop.cyjs and .graphml
    python GraphRevised/explorer/cytoscape_desktop.py --push     # also load it into a running Cytoscape

Reads exports/graph.cyjs (written by `python -m GraphRevised.export.cytoscape`,
which reads Neo4j). Cytoscape Desktop's table columns hold numbers, text, and
lists of text, not nested objects, so each fact's voices (a list of objects)
are dropped here; their text versions (voiceLines, reviewLines) stay. Nothing
is written to Neo4j. Instructions: explorer/CYTOSCAPE-DESKTOP.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exports" / "graph.cyjs"
TARGET = ROOT / "exports" / "graph-desktop.cyjs"
GRAPHML = ROOT / "exports" / "graph-desktop.graphml"

STYLE = "Chrystallum"
SHAPES = {"Person": "ELLIPSE", "Event": "DIAMOND", "Place": "TRIANGLE", "Group": "ROUND_RECTANGLE",
          "Office": "HEXAGON", "Work": "RECTANGLE", "Concept": "OCTAGON", "Period": "PARALLELOGRAM",
          "Polity": "PARALLELOGRAM", "Type": "VEE",
          "Question": "STAR", "Position": "ROUND_DIAMOND"}


def flat(data: dict) -> dict:
    """Keep what Cytoscape Desktop's JSON reader accepts: scalars only.

    It refuses list values ("invalid type: class java.util.ArrayList"), so a
    list of text (voiceLines, notes, times) becomes one text, an item per line.
    Lists of objects (the voices themselves) are dropped.
    """
    out = {}
    for key, value in data.items():
        if value is None or isinstance(value, (str, int, float, bool)):
            out[key] = value
        elif isinstance(value, list) and all(isinstance(v, (str, int, float, bool)) for v in value):
            out[key] = "\n".join(map(str, value))
    return out


def write_flat() -> Path:
    export = json.loads(SOURCE.read_text(encoding="utf-8"))
    elements = export["elements"]
    desktop = {
        "format_version": "1.0",
        "generated_by": "GraphRevised.explorer.cytoscape_desktop",
        "data": {"name": "Chrystallum"},
        "elements": {
            "nodes": [{"data": {**flat(n["data"]), "name": n["data"].get("label")}} for n in elements["nodes"]],
            "edges": [{"data": {**flat(e["data"]), "name": e["data"].get("sentence"), "interaction": e["data"].get("label")}}
                      for e in elements["edges"]],
        },
    }
    TARGET.write_text(json.dumps(desktop, ensure_ascii=False, indent=1), encoding="utf-8")
    write_graphml(desktop)
    print(f"{len(elements['nodes'])} nodes, {len(elements['edges'])} fact edges -> {TARGET}")
    print(f"  and {GRAPHML}")
    return TARGET


def write_graphml(desktop: dict) -> None:
    """The same network as GraphML, which every Cytoscape version imports; lists become text, one item per line."""
    import networkx as nx

    def cell(value):
        return "\n".join(map(str, value)) if isinstance(value, list) else value

    graph = nx.MultiDiGraph()
    for n in desktop["elements"]["nodes"]:
        d = n["data"]
        graph.add_node(d["id"], **{k: cell(v) for k, v in d.items() if k != "id" and v is not None})
    for e in desktop["elements"]["edges"]:
        d = e["data"]
        graph.add_edge(d["source"], d["target"], key=d["id"],
                       **{k: cell(v) for k, v in d.items() if k not in ("source", "target") and v is not None})
    nx.write_graphml(graph, GRAPHML)


def push(path: Path) -> None:
    """Load the flat file into a running Cytoscape Desktop and style it (needs py4cytoscape)."""
    import py4cytoscape as p4c

    p4c.cytoscape_ping()
    p4c.import_network_from_file(str(GRAPHML))  # GraphML: the reader every Cytoscape version accepts
    defaults = {
        "NETWORK_BACKGROUND_PAINT": "#FFFFFF",
        "NODE_FILL_COLOR": "#E7E9EC", "NODE_BORDER_PAINT": "#4D545B", "NODE_BORDER_WIDTH": 1.5,
        "NODE_WIDTH": 28, "NODE_HEIGHT": 28, "NODE_LABEL_FONT_SIZE": 10, "NODE_LABEL_POSITION": "S,N,c,0.00,3.00",
        "EDGE_STROKE_UNSELECTED_PAINT": "#868D94", "EDGE_WIDTH": 1.3, "EDGE_TARGET_ARROW_SHAPE": "DELTA",
        "EDGE_LABEL_FONT_SIZE": 8, "EDGE_LABEL_COLOR": "#4D545B",
    }
    mappings = [
        p4c.map_visual_property("NODE_LABEL", "label", "p"),
        p4c.map_visual_property("NODE_SHAPE", "kind", "d", list(SHAPES), list(SHAPES.values())),
        p4c.map_visual_property("NODE_BORDER_STROKE", "status", "d", ["proposed"], ["EQUAL_DASH"]),
        p4c.map_visual_property("EDGE_LABEL", "label", "p"),
        p4c.map_visual_property("EDGE_LINE_TYPE", "status", "d", ["proposed"], ["EQUAL_DASH"]),
        p4c.map_visual_property("EDGE_SOURCE_ARROW_SHAPE", "mode", "d", ["attributed"], ["OPEN_CIRCLE"]),
    ]
    if STYLE in p4c.get_visual_style_names():
        p4c.delete_visual_style(STYLE)
    p4c.create_visual_style(STYLE, defaults=defaults, mappings=mappings)
    p4c.set_visual_style(STYLE)
    p4c.layout_network("force-directed")
    p4c.fit_content()
    print(f"Loaded into Cytoscape with the {STYLE} style.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--push", action="store_true", help="load into a running Cytoscape Desktop (needs py4cytoscape)")
    args = parser.parse_args(argv)
    path = write_flat()
    if args.push:
        push(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
