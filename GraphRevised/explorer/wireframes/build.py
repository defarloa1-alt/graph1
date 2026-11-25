"""Build the greyscale explorer wireframe from the Cytoscape export.

Reads exports/graph.cyjs (git-ignored data), trims it to what the wireframe
draws, and writes exports/wireframe.html (also git-ignored). The template and
this script are the only tracked parts.

    python GraphRevised/explorer/wireframes/build.py
"""

from __future__ import annotations

import hashlib
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
    out.update({k: fact[k] for k in ("fold", "foldVia", "evidence") if fact.get(k)})  # display rules (export/display.py)
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


def load_gallery() -> dict:
    """Pictures from the Wikipedia articles we hold (explorer/images/gallery.json, adapters/commons_images.py):
    entity id -> [{src, caption, depicts, credit, page}]. A picture is listed on the entity its caption
    links and on the article's own entity; shrunk and embedded like the entity images."""
    manifest = IMAGES / "gallery.json"
    if not manifest.exists():
        return {}
    import base64
    import io

    from PIL import Image

    out: dict = {}
    for entry in json.loads(manifest.read_text(encoding="utf-8")):
        image = Image.open(IMAGES / entry["file"]).convert("RGB")
        image.thumbnail((320, 240))
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=80)
        item = {
            "src": "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode(),
            "file": entry["commonsFile"], "caption": entry.get("caption") or "", "depicts": entry.get("depicts"),
            "class": entry.get("class"), "page": entry.get("page"),
            "credit": " · ".join(x for x in (entry.get("author"), entry.get("date"), entry.get("licence")) if x),
        }
        for key in dict.fromkeys((entry["entity"], entry.get("article"))):
            if key:
                out.setdefault(key, []).append(item)
    return out


def load_backdrops() -> dict:
    """Generated illustrations for poster backdrops (explorer/images/generated/*.json, each beside its
    picture): entity id -> {src, caption}. One replaced by a newer record ("supersedes") is skipped.
    Never a picture of the event: the caption says it is generated (D-172)."""
    folder = IMAGES / "generated"
    records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))] if folder.exists() else []
    replaced = {r.get("supersedes") for r in records}
    out = {}
    import base64
    import io

    from PIL import Image

    for r in records:
        if r["file"] in replaced or not (folder / r["file"]).exists():
            continue
        image = Image.open(folder / r["file"]).convert("RGB")
        image.thumbnail((1600, 1600))
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=78)
        model = r.get("model", "").split(" (")[0]
        out[r["for"]] = {
            "src": "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode(),
            "caption": f"Illustration, generated ({model}, {r.get('made')}): not a picture of the battle"
                       + ("; awaiting the curator's review" if r.get("review", "").startswith("awaiting") else ""),
        }
    return out


ENTITY_ID = re.compile(r"chr:entity:[\w.-]+")
LEFT_OUT = re.compile(r"READ (\w+) (.+?) \(\$([\d.]+)\)")


def load_reach() -> dict:
    """Where the system can look: the source registry (curation/sources.json, D-177), every source with
    what it gives, its status (read, registered, candidate), its rights class and its marks."""
    registry = json.loads((ROOT / "curation" / "sources.json").read_text(encoding="utf-8"))
    gives = {k: v for k, v in (registry.get("gives") or {}).items() if not k.startswith("_")}
    out = []
    for s in registry["sources"]:
        rights = s.get("rights") or {}
        out.append({"system_id": s["id"], "name": s["label"], "status": s["status"], "gives": s.get("gives") or [],
                    "rights_class": rights.get("class"), "unverified": bool(rights.get("unverified")),
                    "non_commercial": bool(s.get("nonCommercial")), "homepage": s.get("homepage"),
                    "lenses": s.get("lenses") or [], "about": (s.get("coverage") or {}).get("description", "")})
    return {"gives": gives, "sources": out}


def load_plans() -> dict:
    """The newest front-door run per focus (runs/front-door-*.json, D-174): entity id -> the run, trimmed
    for the Plan view. Each source row of the coverage matrix gets its state per lens: an item of the
    plan, left out for the budget, or read already."""
    runs = sorted((ROOT / "runs").glob("front-door-*.json"), key=lambda p: p.name)
    out = {}
    for path in runs:
        if path.name.endswith(".calls.json"):
            continue
        run = json.loads(path.read_text(encoding="utf-8"))
        o, plan = run.get("orientation") or {}, run.get("plan") or {}
        focus = (o.get("focus") or {}).get("chosen") or {}
        key = focus.get("local_entity_id")
        if not key or not plan:
            continue
        calls_path = path.with_name(path.stem + ".calls.json")
        calls = json.loads(calls_path.read_text(encoding="utf-8")).get("calls", {}) if calls_path.exists() else {}
        lenses = [l["name"].lower() for l in o.get("lenses", []) if l["name"].lower() != "general"]
        # the sources and their "not read by" gaps come in the same order (orchestration/front_door.py)
        source_gaps = [g for g in plan["coverage"]["gaps"] if g["kind"] == "source"]
        rows, by_short, by_entity = [], {}, {}
        for i, s in enumerate(o.get("sources", [])):
            m = ENTITY_ID.search(s.get("why") or "")
            gap = source_gaps[i]["description"] if i < len(source_gaps) else ""
            short, _, missing = gap.partition(": not read by ")
            row = {"work": s["work"], "entity": m.group(0) if m else None, "kind": s.get("kind"),
                   "short": short or s["work"].split(",")[0],
                   "cells": {l: ("unread" if l in missing.split(", ") else "read") for l in lenses}}
            rows.append(row)
            by_short[row["short"]] = row
            if row["entity"]:
                by_entity[row["entity"]] = row
        for item in plan.get("items", []):
            row = by_entity.get(item.get("target"))
            if row and item.get("lens") in row["cells"]:
                row["cells"][item["lens"]] = {"item": item["item_id"], "usd": item.get("budget_usd")}
        not_built, left_out, notes = [], [], []
        for q in plan.get("unresolved_questions", []):
            if q.startswith("Left out for the budget"):
                for lens, short, usd in LEFT_OUT.findall(q):
                    left_out.append({"lens": lens, "short": short, "usd": float(usd)})
                    row = by_short.get(short)
                    if row and row["cells"].get(lens) == "unread":
                        row["cells"][lens] = {"left": True, "usd": float(usd)}
            elif " is not built yet" in q:
                not_built.append(q)
            else:
                notes.append(q)
        # what the orchestrator did (D-175): each item's attempts, newest last; a retried failure is set aside
        results = {r["assignment_id"]: r for r in run.get("results") or []}
        set_aside = set(run.get("set_aside") or [])
        attempts: dict = {}
        for a in run.get("assignments") or []:
            r = results.get(a["assignment_id"])
            state = "set_aside" if a["assignment_id"] in set_aside else (r["status"] if r else "running")
            attempts.setdefault(a["item_id"], []).append({
                "state": state, "started": a.get("started_at"), "finished": r.get("finished_at") if r else None,
                "cost": r.get("cost_usd") if r else None, "proposals": len(r.get("proposal_ids") or []) if r else 0,
                "error": (r.get("error") or None) if r else None})
        # an item that has run ok has read its source through its lens since the plan was made: the matrix says so
        for row in rows:
            for lens, c in row["cells"].items():
                tries = attempts.get(c.get("item")) if isinstance(c, dict) else None
                if tries and tries[-1]["state"] == "ok":
                    row["cells"][lens] = "read"
        interrupts = [{k: i.get(k) for k in ("item_id", "reason", "question", "options", "answer", "answered_by")}
                      for i in run.get("interrupts") or []]
        earlier = out.get(key)  # the runs are read oldest first, so a run already held is an earlier plan
        out[key] = {
            "attempts": attempts, "interrupts": interrupts, "stoppedBecause": run.get("stopping_explanation"),
            "earlier": ([{"runId": earlier["runId"], "status": earlier["status"], "spent": earlier["spent"]}] + earlier.get("earlier", []))
                       if earlier else [],
            "runId": run["run_id"], "command": run.get("command"), "mode": run.get("mode"), "status": run.get("status"),
            "createdAt": run.get("created_at"), "planVersion": plan.get("version"), "dossierVersion": run.get("dossier_version"),
            "focus": o.get("focus"), "years": [o.get("earliest_year"), o.get("latest_year")], "places": o.get("places", []),
            "statements": o.get("statements", []), "controversies": o.get("controversies", []),
            "traps": o.get("identity_traps", []), "federations": o.get("federations", []),
            "lenses": lenses, "scope": plan.get("scope"),
            "federations": [f for f in o.get("federations", []) if f.get("system_id")], "subject": plan.get("subject"),
            "coverage": {k: plan["coverage"].get(k) for k in ("claims_by_status", "open_proposals", "read_at")}
                        | {"entities": len(plan["coverage"].get("reused_entity_ids", [])),
                           "otherGaps": [g for g in plan["coverage"]["gaps"] if g["kind"] != "source"]},
            "matrix": rows, "items": plan.get("items", []), "calls": calls, "leftOut": left_out,
            "notBuilt": not_built, "notes": notes, "stopping": plan.get("stopping_rules", []),
            "budget": plan.get("budget_usd"), "spent": run.get("spent_usd", 0), "scopeApproved": plan.get("scope_approved"),
        }
    return out


BASEMAPS: dict = {}


def load_scenes() -> dict:
    """Movement scenes (scenes/*.json, 26a shape 7), by subject. A scene derived from an animation page that
    embeds its own basemap (coastlines and hillshade, `const GEO={...}`) carries that basemap with it; its
    licences are in the scene's `terrain` note."""
    out = {}
    for path in sorted((ROOT / "scenes").glob("*.json")) if (ROOT / "scenes").exists() else []:
        scene = json.loads(path.read_text(encoding="utf-8"))
        if scene.get("type") not in ("movement", "flyby"):
            continue  # its narration input and its narrations sit beside it
        source = (scene.get("derivedFrom") or {}).get("file")
        page = ROOT / source if source else None
        if page and page.exists():
            if source not in BASEMAPS:
                m = re.search(r"const GEO=(\{.*?\});", page.read_text(encoding="utf-8"), re.S)
                if m:
                    BASEMAPS[source] = json.loads(m.group(1))
            if source in BASEMAPS:
                scene["basemap"] = source  # the page's basemap, held once in DATA.basemaps
        scene["file"] = path.relative_to(ROOT).as_posix()
        # its narrations (scenes/NARRATION.md), by persona; one written for another version of the scene is stale
        stem = path.name.split(".")[0]
        scene["narrations"] = {}
        for npath in sorted(path.parent.glob(f"{stem}.narration.*.json")):
            if npath.name.endswith(".rejected.json"):
                continue
            n = json.loads(npath.read_text(encoding="utf-8"))
            scene["narrations"][n.get("persona", "browser")] = {
                "stale": n.get("sceneContentHash") != scene.get("contentHash"), "madeBy": n.get("madeBy"),
                "madeAt": n.get("madeAt"), "warnings": len((n.get("check") or {}).get("warnings", [])),
                "steps": {s["stepId"]: s["lines"] for s in n.get("steps", [])}}
            # its voiced clips (narrative/voice_scene.py), used only if they voice this exact narration file
            apath = ROOT / "scenes" / "audio" / scene["id"].rsplit(":", 1)[-1] / n.get("persona", "browser") / "audio.json"
            if apath.exists():
                rec = json.loads(apath.read_text(encoding="utf-8"))
                if rec.get("narrationSha256") == hashlib.sha256(npath.read_bytes()).hexdigest():
                    scene["narrations"][n.get("persona", "browser")]["audio"] = {
                        "dir": "../" + apath.parent.relative_to(ROOT).as_posix() + "/",
                        "voice": rec.get("voiceName") or rec.get("voice"), "generator": rec.get("generator"),
                        "madeAt": rec.get("madeAt"), "seconds": rec.get("seconds"),
                        "clips": {c["id"]: {"file": c["file"], "seconds": c.get("seconds")} for c in rec["clips"]
                                  if (apath.parent / c["file"]).exists()}}
        out.setdefault(scene["subject"]["id"], []).append(scene)
    for scenes in out.values():
        scenes.sort(key=lambda sc: (bool((sc.get("derivedFrom") or {}).get("storyboard")), sc["file"]))
    return out


def load_storyboards() -> dict:
    """Each event's storyboard (storyboards/<event>.storyboard.json, 26a §5a, D-179), keyed by its subject; a
    rejected one is left out. Each gap's registry source gets its label and status, for the Storyboard view."""
    reg = {s["id"]: s for s in json.loads((ROOT / "curation" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    cat = json.loads((ROOT / "curation" / "presentations.json").read_text(encoding="utf-8"))
    out = {}
    for path in sorted((ROOT / "storyboards").glob("*.storyboard.json")):
        sb = json.loads(path.read_text(encoding="utf-8"))
        used = {g.get("source") for s in sb["segments"] for g in s.get("gaps", []) if g.get("source")}
        sb["sources"] = {i: {"label": reg[i]["label"], "status": reg[i]["status"]} for i in used if i in reg}
        sb["kinds"] = {k["id"]: {"answers": k["answers"], "built": k["built"], "never": k["never"]} for k in cat["kinds"]}
        sb["file"] = path.relative_to(ROOT).as_posix()
        sb.pop("calls", None)
        out[sb["subject"]["id"]] = sb
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
            # display rules from the projection (export/display.py); elsewhere is the card's Elsewhere block
            **{k: n[k] for k in ("hint", "standing", "standingWords", "referenceWorks", "imaginedOnly", "folded",
                                 "coordinates", "subjectAccess", "form", "elsewhere")
               if n.get(k)},
        })
    edges = [trim_fact(e["data"]) for e in export["elements"]["edges"]]
    data = {"generatedBy": export.get("generated_by"), "nodes": nodes, "edges": edges,
            "images": load_images(), "gallery": load_gallery(), "backdrops": load_backdrops(), "plans": load_plans(), "reach": load_reach(), "sceneSets": load_scenes(), "basemaps": BASEMAPS, "storyboards": load_storyboards(), "phases": load_phases()}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8").replace("__GRAPH_DATA__", payload)
    OUTPUT.write_text(page, encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path} ({path.stat().st_size // 1024} KB)")
