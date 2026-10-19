"""Build the greyscale explorer wireframe from the Cytoscape export.

Reads exports/graph.cyjs (git-ignored data), trims it to what the wireframe
draws, and writes exports/wireframe.html (also git-ignored). The template and
this script are the only tracked parts.

    python GraphRevised/explorer/wireframes/build.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPORT = ROOT / "exports" / "graph.cyjs"
TEMPLATE = Path(__file__).with_name("template.html")
OUTPUT = ROOT / "exports" / "wireframe.html"
IMAGES = ROOT / "explorer" / "images"

YEAR = re.compile(r"(\d{1,4})\s*(BCE|CE)")


def years(texts: list[str]) -> list[int]:
    """Signed years (BCE negative) named in a fact's time words."""
    found = []
    for text in texts:
        for number, era in YEAR.findall(text):
            found.append(-int(number) if era == "BCE" else int(number))
    return found


def trim_voice(voice: dict) -> dict:
    return {
        "accordingTo": voice.get("accordingTo"),
        "status": voice.get("status"),
        "mode": voice.get("mode"),
        "time": voice.get("time"),
        "role": voice.get("role"),
        "context": voice.get("context"),
        "quotes": [
            {k: q.get(k) for k in ("source", "locator", "url", "quotation", "pending")}
            for q in voice.get("quotes", [])
        ],
        "review": [
            {k: r.get(k) for k in ("operation", "status", "decidedBy", "decidedAt")}
            for r in voice.get("review", [])
        ],
    }


def trim_fact(fact: dict) -> dict:
    out = {
        k: fact.get(k)
        for k in ("id", "source", "target", "label", "sentence", "predicate",
                  "category", "status", "mode", "attestation", "times")
    }
    out["voices"] = [trim_voice(v) for v in fact.get("voices", [])]
    span = years(fact.get("times") or [])
    out["years"] = [min(span), max(span)] if span else None
    return out


def load_images() -> dict:
    """Images for entities, from explorer/images/images.json (git-ignored data).

    Each entry: {"entity": "chr:entity:mark-antony", "file": "antony.jpg",
    "depicts": "...", "author": "...", "licence": "...", "source": "..."}.
    Images are shrunk and embedded, since the published page cannot load files
    from other sites. Without a manifest, the page draws mock portraits.
    """
    manifest = IMAGES / "images.json"
    if not manifest.exists():
        return {}
    import base64
    import io

    from PIL import Image

    out = {}
    for entry in json.loads(manifest.read_text(encoding="utf-8")):
        image = Image.open(IMAGES / entry["file"]).convert("RGB")
        image.thumbnail((192, 192))
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=82)
        credit = " · ".join(x for x in (entry.get("depicts"), entry.get("author"),
                                         entry.get("licence"), entry.get("source")) if x)
        out[entry["entity"]] = {
            "src": "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode(),
            "credit": credit or "No credit recorded",
            # what the picture is (adapters/commons_images.py); only images of the time or of the
            # place today stand for an entity on the canvas, a later imagining only on its card
            "class": entry.get("class"),
            "canvas": entry.get("canvas", True),
        }
    return out


def load_phases() -> dict:
    """Each event's phase keys in the curator's order (curation/phases.json, D-091)."""
    path = ROOT / "curation" / "phases.json"
    if not path.exists():
        return {}
    events = json.loads(path.read_text(encoding="utf-8")).get("events", {})
    return {event: [phase["key"] for phase in spec.get("phases", [])] for event, spec in events.items()}


def build() -> Path:
    export = json.loads(EXPORT.read_text(encoding="utf-8"))
    nodes = []
    for element in export["elements"]["nodes"]:
        n = element["data"]
        nodes.append({
            "id": n["id"],
            "label": n.get("label"),
            "fullLabel": n.get("fullLabel") or n.get("label"),
            "kind": n.get("kind"),
            "status": n.get("status"),
            "description": n.get("description"),
            "notes": n.get("notes") or [],
            "facts": [trim_fact(f) for f in n.get("facts") or []],
            "authority": n.get("authorityLines") or [],
        })
    edges = [trim_fact(e["data"]) for e in export["elements"]["edges"]]
    data = {"generatedBy": export.get("generated_by"), "nodes": nodes, "edges": edges,
            "images": load_images(), "phases": load_phases()}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8").replace("__GRAPH_DATA__", payload)
    OUTPUT.write_text(page, encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path} ({path.stat().st_size // 1024} KB)")
