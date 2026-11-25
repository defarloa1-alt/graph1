"""Draft a scene for one storyboard segment from the passages the graph holds (26a §3, shape 7; D-179).

    python -m GraphRevised.scenes.build_scene --storyboard <storyboard.json> --segment <n> [--kind scene-movement]
        [--model claude-opus-5-5] [--evidence-only]

The GENERATE worker for scenes. Code gathers the evidence: the segment's phases, the events placed in
them (partOf), the passages that depict those events (their stored text, locator and Work), the located
places those passages name (with their gazetteer points), and the people and groups who took part. The
model drafts the steps: statements, each sourced by verbatim quotations from those passages or marked as
an inference, and legs between listed places. The code check holds the draft to the rules:
- every quotation is word for word in its passage;
- every sourced statement has a quotation, and every number it states is in its quotations;
- a leg runs only between listed places, for a listed unit;
- a sourced leg's statement quotes a passage naming both its ends;
- every step is in one of the segment's phases.
Problems go back to the model once. A scene that passes is written as
scenes/<event>-seg<n>.proposed.json, with its narration input beside it, status proposed; one that does
not is written as .rejected.json. Nothing goes into the graph: a scene is a plan the renderers draw.

Built for kind scene-movement. A battle scene needs drawn ship lines, a Generalized Abstraction the
curator draws (D-172); that kind, flyby and memory-reception are not built here yet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from GraphRevised.proposals.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
SCENES = ROOT / "scenes"
MODEL = "claude-opus-5-5"
BUILT = {"scene-movement"}
MAX_CHARS = 90000  # passage text sent to the model; the most-cited passages first

NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
                "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand",
                "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"}


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


# --- Evidence: gathered by code ---------------------------------------------------------------------

def gather(session: Any, event_id: str, phase_keys: list[str]) -> dict[str, Any]:
    slug = event_id.split(":", 2)[2]
    phase_ids = [f"chr:entity:phase:{slug}:{k}" for k in phase_keys]
    rows = session.run(
        """
        UNWIND $phases AS pid
        MATCH (m:Entity)-[:PART_OF]->(:Entity {id: pid})
        MATCH (a:Annotation)-[:CONCERNS]->(m)
        MATCH (a)-[:ANNOTATES]->(o:SourceObservation)-[:IN_WORK]->(w:Entity)
        WHERE o.passageText IS NOT NULL AND NOT coalesce(w.form, '') IN $creative  // imaginative works are never evidence
        RETURN o.id AS obs, o.shortLabel AS loc, o.locator AS url, o.passageText AS text, w.id AS workId,
               w.label AS work, w.form AS form, collect(DISTINCT {event: m.id, label: m.label, phase: split(pid, ':')[-1]}) AS events
        """, phases=phase_ids, creative=sorted(load_registry().creative_forms)).data()
    rows.sort(key=lambda r: (-len(r["events"]), r["work"], r["loc"] or ""))
    passages, used = [], 0
    for r in rows:
        if used + len(r["text"]) > MAX_CHARS:
            continue
        used += len(r["text"])
        passages.append(r)
    obs = [p["obs"] for p in passages]
    places = session.run(
        """
        MATCH (a:Annotation)-[:ANNOTATES]->(o:SourceObservation) WHERE o.id IN $obs
        MATCH (a)-[:CONCERNS]->(pl:Place)-[:AT_LOCATION]->(l:Location)
        WHERE l.location IS NOT NULL
        RETURN pl.id AS id, pl.label AS label, pl.status AS status, l.location.x AS lon, l.location.y AS lat,
               l.system AS system, l.identifier AS identifier, l.names AS names, count(DISTINCT o) AS passages
        """, obs=obs).data()
    units = session.run(
        """
        UNWIND $phases AS pid
        MATCH (m:Entity)-[:PART_OF]->(:Entity {id: pid})
        MATCH (x:Entity)-[:PARTICIPATED_IN]->(m) WHERE x:Person OR x:Group
        RETURN x.id AS id, x.label AS label, labels(x)[1] AS kind, count(DISTINCT m) AS events
        ORDER BY events DESC LIMIT 40
        """, phases=phase_ids).data()
    label = session.run("MATCH (e:Entity {id: $id}) RETURN e.label AS l", id=event_id).single()["l"]
    out_places = {}
    for p in places:
        names = [n if isinstance(n, str) else (n or {}).get("name") for n in (p["names"] or [])]
        out_places[p["id"]] = {"id": p["id"], "label": p["label"], "status": p["status"], "lonLat": [p["lon"], p["lat"]],
                               "gazetteer": f"{p['system']} {p['identifier']}",
                               "names": sorted({n for n in names if n} | {p["label"]})[:12], "passages": p["passages"]}
    return {"event": event_id, "label": label, "phases": phase_keys, "passages": passages,
            "places": out_places, "units": {u["id"]: u for u in units}}


# --- The draft: the model's ---------------------------------------------------------------------------

class Quote(BaseModel):
    passage: str = Field(description="the passage's locator label, exactly as given (e.g. 'Work 50.13.5')")
    quotation: str = Field(description="words copied exactly from that passage")


class Statement(BaseModel):
    text: str
    basis: Literal["sourced", "inferred"]
    quotes: list[Quote] = Field(description="for sourced: the passages that say it; for inferred: the points it joins")
    note: str | None = Field(description="for inferred: what is inferred and from what; else optional")


class Leg(BaseModel):
    unit: str = Field(description="a unit id from the UNITS list")
    side: str | None = Field(description="the side the unit fought on, if the passages make it plain; else null")
    from_place: str = Field(description="a place id from the PLACES list")
    to_place: str = Field(description="a place id from the PLACES list")
    via: list[str] = Field(description="place ids passed through, from the PLACES list")
    basis: Literal["sourced", "inferred"]
    statement: int = Field(description="the 1-based number of the statement in this step that this leg draws")


class Alternative(BaseModel):
    according_to: str = Field(description="the Work")
    words: str = Field(description="what this source says, in our words")
    quotes: list[Quote]


class Disagreement(BaseModel):
    about: Literal["route", "command", "other"]
    note: str
    alternatives: list[Alternative]


class Step(BaseModel):
    phase: str
    title: str
    time_words: str = Field(description="when, in the sources' terms; a date only if a passage gives it")
    statements: list[Statement]
    legs: list[Leg]
    disagreements: list[Disagreement]


class Draft(BaseModel):
    steps: list[Step]
    place_names: dict[str, str] = Field(description="place id -> the name the passages use, when it differs from the label")


SYSTEM = """You draft a movement scene for Chrystallum, a history graph with strict provenance. A scene is a
sequence of steps on a campaign map: who went where, in what order, and what the sources say about it.
You may use only the PASSAGES given. Rules:
- Each statement is one short plain sentence. Sourced: one or more quotations copied word for word from
  the named passages (a phrase is enough), and nothing in the sentence that the quotations do not say: no
  number, date, name or motive beyond them. Inferred: joined up from sourced points ("he probably marched
  south"), with a note saying what is inferred from what. Prefer sourced.
- Legs: a unit moving from one listed place to another, drawing one statement of the step. A sourced leg's
  statement must quote passages that name both its ends; otherwise the leg is inferred. Never invent a
  route: a leg is a line between named places, and the map says so.
- Steps follow the phases in their given order; each step belongs to one phase. Use the sources' own
  names for people and places in the text; use place_names to record a place's name in the passages.
- Where two sources disagree (a route, who commanded what), give both as a disagreement, never choose.
- Prefer the ancient witnesses. A modern work or an encyclopedia may be quoted where no ancient passage
  says it, and then the statement names whose account it is ("in <author>'s account").
- Leave out what the passages do not support. Fewer, well-sourced steps are better than many.
Return JSON only."""


def ask(client: Any, model: str, ev: dict[str, Any], repair: list[str] | None = None, earlier: str | None = None):
    passages = [{"passage": p["loc"], "work": p["work"], "text": p["text"],
                 "depicts": [e["label"] for e in p["events"]], "phases": sorted({e["phase"] for e in p["events"]})}
                for p in ev["passages"]]
    places = [{k: p[k] for k in ("id", "label", "names")} for p in ev["places"].values()]
    units = [{"id": u["id"], "label": u["label"], "kind": u["kind"]} for u in ev["units"].values()]
    user = (f"EVENT: {ev['label']}\nPHASES, in order: {ev['phases']}\n\nPLACES (located):\n{json.dumps(places, ensure_ascii=False)}\n\n"
            f"UNITS:\n{json.dumps(units, ensure_ascii=False)}\n\nPASSAGES:\n{json.dumps(passages, ensure_ascii=False)}")
    messages = [{"role": "user", "content": user}]
    if repair:
        messages += [{"role": "assistant", "content": earlier or ""},
                     {"role": "user", "content": "The check found these problems. Return the whole draft again, fixed, "
                                                 "changing only what they require:\n- " + "\n- ".join(repair)}]
    r = client.beta.messages.parse(model=model, max_tokens=16000, system=SYSTEM, messages=messages, output_format=Draft,
                                   betas=["server-side-fallback-2026-07-01"], extra_body={"fallbacks": "default"})
    meta = {"model": r.model, "stopReason": r.stop_reason, "inputTokens": r.usage.input_tokens,
            "outputTokens": r.usage.output_tokens}
    return (None if r.stop_reason in ("refusal", "max_tokens") else r.parsed_output), meta


# --- The check: code --------------------------------------------------------------------------------

def numbers(text: str) -> set[str]:
    t = norm(text)
    return set(re.findall(r"\d+(?:[.,]\d+)?", t)) | {w for w in re.findall(r"[a-z]+", t) if w in NUMBER_WORDS}


def check(draft: dict[str, Any], ev: dict[str, Any]) -> dict[str, list[str]]:
    by_loc = {p["loc"]: p for p in ev["passages"]}
    problems, warnings = [], []
    order = ev["phases"]
    last_phase = 0
    if not draft["steps"]:
        problems.append("no steps")
    for s_n, st in enumerate(draft["steps"], 1):
        where = f"step {s_n}"
        if st["phase"] not in order:
            problems.append(f"{where}: phase {st['phase']} is not one of the segment's {order}")
        elif order.index(st["phase"]) < last_phase:
            problems.append(f"{where}: phase {st['phase']} comes before the previous step's; keep the phases' order")
        else:
            last_phase = order.index(st["phase"])
        for x_n, x in enumerate(st["statements"], 1):
            w = f"{where}.{x_n}"
            quoted = ""
            for q in x["quotes"]:
                p = by_loc.get(q["passage"])
                if not p:
                    problems.append(f"{w}: passage {q['passage']!r} is not one of those given")
                    continue
                if norm(q["quotation"]) not in norm(p["text"]):
                    problems.append(f"{w}: not word for word in {q['passage']}: {q['quotation']!r}")
                quoted += " " + q["quotation"]
            if x["basis"] == "sourced" and not x["quotes"]:
                problems.append(f"{w}: sourced, but no quotation")
            if x["basis"] == "sourced":
                extra = numbers(x["text"]) - numbers(quoted)
                if extra:
                    problems.append(f"{w}: states {sorted(extra)}, which its quotations do not")
            if x["basis"] == "inferred" and not x.get("note"):
                problems.append(f"{w}: inferred, but no note says what from")
        for l_n, leg in enumerate(st["legs"], 1):
            w = f"{where} leg {l_n}"
            if leg["unit"] not in ev["units"]:
                problems.append(f"{w}: unit {leg['unit']} is not in the UNITS list")
            ends = [leg["from_place"], *leg["via"], leg["to_place"]]
            bad = [p for p in ends if p not in ev["places"]]
            if bad:
                problems.append(f"{w}: places {bad} are not in the PLACES list")
            if not 1 <= leg["statement"] <= len(st["statements"]):
                problems.append(f"{w}: statement {leg['statement']} is not a statement of the step")
                continue
            if leg["basis"] == "sourced" and not bad:
                x = st["statements"][leg["statement"] - 1]
                quoted = norm(" ".join(by_loc[q["passage"]]["text"] for q in x["quotes"] if q["passage"] in by_loc))
                for end in (leg["from_place"], leg["to_place"]):
                    names = ev["places"][end]["names"] + ([draft["place_names"][end]] if end in draft.get("place_names", {}) else [])
                    if not any(norm(n) in quoted for n in names if n):
                        problems.append(f"{w}: sourced, but no passage quoted by statement {leg['statement']} names "
                                        f"{ev['places'][end]['label']}; mark the leg inferred or quote a passage that names it")
        for d in st["disagreements"]:
            if len(d["alternatives"]) < 2:
                problems.append(f"{where}: a disagreement needs two versions")
            for a in d["alternatives"]:
                for q in a["quotes"]:
                    p = by_loc.get(q["passage"])
                    if not p or norm(q["quotation"]) not in norm(p["text"]):
                        problems.append(f"{where}: disagreement quotation not word for word: {q['quotation']!r}")
    for pid, name in (draft.get("place_names") or {}).items():
        if pid in ev["places"] and not any(norm(name) in norm(p["text"]) for p in ev["passages"]):
            warnings.append(f"place name {name!r} for {ev['places'][pid]['label']} is in no passage given")
    return {"problems": problems, "warnings": warnings}


# --- Assembly: shape 7 -----------------------------------------------------------------------------

def basemap_for(points: list[list[float]]) -> str | None:
    """A held animation page whose embedded basemap's overview contains every point."""
    for page in sorted((ROOT / "docs").rglob("*.html")):
        m = re.search(r"const GEO=(\{.*?\});", page.read_text(encoding="utf-8", errors="ignore"), re.S)
        if not m:
            continue
        geo = json.loads(m.group(1))
        p, (bx, by, bw, bh) = geo["po"], geo["ovbox"]
        merc = lambda la: math.log(math.tan(math.pi / 4 + la * math.pi / 360))
        inside = all(bx <= p["ox"] + (lon - p["lon0"]) * math.pi / 180 * p["k"] <= bx + bw
                     and by <= p["oy"] + (p["mlat1"] - merc(lat)) * p["k"] <= by + bh for lon, lat in points)
        if inside:
            return page.relative_to(ROOT).as_posix()
    return None


def assemble(draft: dict[str, Any], ev: dict[str, Any], storyboard: dict[str, Any], segment: dict[str, Any],
             model: str, metas: list[dict]) -> dict[str, Any]:
    by_loc = {p["loc"]: p for p in ev["passages"]}
    names = dict(draft.get("place_names") or {})
    # a place is called what the scene's quoted passages call it most often, among its gazetteer names and its
    # held label (the ancient name where the sources use it); the model's choice stands where it gave one
    quoted = norm(" ".join(by_loc[q["passage"]]["text"] for st in draft["steps"] for x in st["statements"]
                           for q in x["quotes"] if q["passage"] in by_loc))
    for pid, p in ev["places"].items():
        if pid in names:
            continue
        counts = {n: len(re.findall(rf"\b{re.escape(norm(n))}\b", quoted)) for n in {*p["names"], p["label"]} if n and len(n) > 3}
        best = max(counts, key=lambda n: (counts[n], n == p["label"]), default=None)
        if best and counts[best] and best != p["label"]:
            names[pid] = best
    used = {pid for st in draft["steps"] for leg in st["legs"] for pid in [leg["from_place"], *leg["via"], leg["to_place"]]}
    mentioned = {pid for pid, p in ev["places"].items()
                 for st in draft["steps"] for x in st["statements"] if any(norm(n) in norm(x["text"]) for n in p["names"] + [names.get(pid, "")] if n)}
    places = {}
    for pid in sorted(used | mentioned):
        p = ev["places"][pid]
        label = names.get(pid) or p["label"]
        places[label] = {"label": label, "lonLat": p["lonLat"], "lonLatFrom": f"the gazetteer ({p['gazetteer']})",
                         "entity": pid, "status": p["status"], **({"heldAs": p["label"]} if label != p["label"] else {})}
    label_of = {pid: (names.get(pid) or ev["places"][pid]["label"]) for pid in ev["places"]}

    def voice(q):
        p = by_loc[q["passage"]]
        return {"accordingTo": p["work"], "work": p["workId"], "observation": p["obs"], "locator": p["loc"],
                "url": p.get("url"), "quotation": q["quotation"]}

    slug = ev["event"].split(":", 2)[2]
    scene_id = f"chr:scene:{slug}-seg{segment['order']}"
    by = f"the scene builder (scenes/build_scene.py with {metas[-1]['model']})"
    steps = []
    for n, st in enumerate(draft["steps"], 1):
        statements = []
        for x in st["statements"]:
            s = {"text": x["text"], "basis": x["basis"], "voices": [voice(q) for q in x["quotes"] if q["passage"] in by_loc]}
            if x["basis"] == "inferred":
                s["by"] = by
            if x.get("note"):
                s["note"] = x["note"]
            statements.append(s)
        legs = []
        for leg in st["legs"]:
            u = ev["units"][leg["unit"]]
            out = {"unit": {"entity": u["id"], "label": u["label"], **({"side": leg["side"]} if leg.get("side") else {})},
                   "from": places[label_of[leg["from_place"]]], "to": places[label_of[leg["to_place"]]],
                   "basis": leg["basis"], "statement": leg["statement"]}
            if leg["via"]:
                out["via"] = [places[label_of[v]] for v in leg["via"]]
            if leg["basis"] == "sourced":
                out["note"] = "Drawn as a line between the named places; the passages give the places, not the route."
            legs.append(out)
        step = {"order": n, "phase": st["phase"], "timeWords": st["time_words"], "view": "overview", "title": st["title"],
                "statements": statements, "legs": legs}
        for d in st["disagreements"]:
            key = {"route": "routes", "command": "ordersOfBattle"}.get(d["about"], "routes")
            if key in step:  # a second disagreement of the same kind in one step: kept as its own entry
                key = f"{key}{sum(k.startswith(key) for k in step)}"
            title = {"route": "Two routes", "command": "Two accounts of who commanded"}.get(d["about"], "Two versions")
            step[key] = {"title": title, "note": d["note"], "alternatives": [
                {"accordingTo": a["according_to"], "words": a["words"],
                 "voices": [voice(q) for q in a["quotes"] if q["passage"] in by_loc]} for a in d["alternatives"]]}
        steps.append(step)
    points = [p["lonLat"] for p in places.values()]
    scene = {
        "id": scene_id, "type": "movement", "title": f"{segment['title']} (generated)",
        "subject": {"id": ev["event"], "label": ev["label"], "kind": "Event"},
        "scope": f"storyboard segment {segment['order']}: {', '.join(ev['phases'])}",
        "sequenceBy": "order", "status": "proposed", "proposedBy": by,
        "proposedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "derivedFrom": {"storyboard": storyboard["id"], "segment": segment["order"],
                        "file": basemap_for(points) if points else None,
                        "builtBy": "scenes/build_scene.py: evidence gathered from the graph, steps drafted by the model, "
                                   "every quotation checked word for word against the stored passage",
                        "passagesGiven": len(ev["passages"])},
        "bases": {"sourced": "a stored passage says it; the quotation is verbatim",
                  "inferred": "joined up from sourced points; 'by' says whose inference"},
        "layers": ["terrain", "places", "unitPaths", "labels"],
        "terrain": {"source": "modern", "note": "the basemap of the held page named in derivedFrom.file, with its licences"},
        "places": places, "steps": steps,
        "footnote": "Generated from the passages the graph holds; places from the gazetteer. Lines between places are "
                    "drawn: no passage gives a route.",
    }
    for st in steps:
        st["id"] = f"{scene_id}#{st['order']}"
        for n, x in enumerate(st["statements"], 1):
            x["id"] = f"{scene_id}#{st['order']}.{n}"
    scene["contentHash"] = hashlib.sha256(json.dumps(scene, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return scene


def narration_input(scene: dict[str, Any]) -> dict[str, Any]:
    """What a narrator reads (scenes/NARRATION.md §2): the scene without the map's coordinates."""
    trim = lambda x: {**x, "voices": [{k: v[k] for k in ("accordingTo", "locator", "quotation")} for v in x.get("voices", [])]}
    steps = []
    for st in scene["steps"]:
        out = {k: st[k] for k in ("id", "order", "title", "timeWords", "view", "phase") if st.get(k) is not None}
        out["statements"] = [trim(x) for x in st["statements"]]
        for key in ("ordersOfBattle", "routes"):
            if key in st:
                out[key] = {**st[key], "alternatives": [trim(a) for a in st[key]["alternatives"]]}
        steps.append(out)
    return {"about": "Input for narration: see scenes/NARRATION.md. Key every line to statement ids; record contentHash.",
            **{k: scene[k] for k in ("id", "contentHash", "scope", "status", "bases")}, "subject": scene["subject"]["label"],
            "steps": steps}


# --- Running it -------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--storyboard", type=Path, required=True)
    parser.add_argument("--segment", type=int, required=True)
    parser.add_argument("--kind", default="scene-movement")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--evidence-only", action="store_true", help="print what would be sent; call no model")
    parser.add_argument("--from-draft", type=Path, help="check and assemble a saved draft (<stem>.draft.json) again; call no model")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if args.kind not in BUILT:
        print(f"{args.kind} is not built yet: this worker drafts {sorted(BUILT)}")
        return 2
    storyboard = json.loads(args.storyboard.read_text(encoding="utf-8"))
    segment = next((s for s in storyboard["segments"] if s["order"] == args.segment), None)
    if segment is None:
        raise SystemExit(f"no segment {args.segment} in {args.storyboard.name}")
    phases = [k for k in segment["stretches"] if k != "beyond"]
    if not phases:
        raise SystemExit("this segment has no phases of the event: nothing in the graph to draw it from")

    from neo4j import GraphDatabase
    from GraphRevised import localdb
    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            ev = gather(session, storyboard["subject"]["id"], phases)
    finally:
        driver.close()
    size = sum(len(p["text"]) for p in ev["passages"])
    print(f"evidence: {len(ev['passages'])} passages ({size} characters), {len(ev['places'])} located places, "
          f"{len(ev['units'])} units, phases {phases}")
    if args.evidence_only:
        for p in ev["passages"][:12]:
            print(f"  {p['loc']}: {len(p['events'])} events")
        print("  places:", ", ".join(p["label"] for p in ev["places"].values()))
        return 0

    slug = ev["event"].split(":", 2)[2]
    stem = f"{slug}-seg{args.segment}"
    if args.from_draft:
        saved = json.loads(args.from_draft.read_text(encoding="utf-8"))
        draft, metas = Draft.model_validate(saved["draft"]), saved["calls"]
        result = check(draft.model_dump(), ev)
    else:
        from GraphRevised.proposals.passage_reader import anthropic_client
        client = anthropic_client(run=f"scene:{storyboard['id']}#{args.segment}")
        draft, meta = ask(client, args.model, ev)
        metas = [meta]
        if draft is None:
            print(f"no draft: {meta['stopReason']}")
            return 1
        result = check(draft.model_dump(), ev)
    if result["problems"] and not args.from_draft:
        again, meta = ask(client, args.model, ev, repair=result["problems"], earlier=draft.model_dump_json())
        metas.append(meta)
        if again is not None:
            draft, result = again, check(again.model_dump(), ev)
    # the model's draft is kept, so a fix to the code can be re-applied without asking again (--from-draft)
    (SCENES / f"{stem}.draft.json").write_text(json.dumps({"draft": draft.model_dump(), "calls": metas}, indent=1,
                                                          ensure_ascii=False), encoding="utf-8")
    if result["problems"]:
        out = SCENES / f"{stem}.rejected.json"
        out.write_text(json.dumps({"draft": draft.model_dump(), "check": result, "calls": metas}, indent=1,
                                  ensure_ascii=False), encoding="utf-8")
        print(f"wrote {out}: {len(result['problems'])} problems")
        for p in result["problems"][:20]:
            print("  problem:", p)
        return 1
    scene = assemble(draft.model_dump(), ev, storyboard, segment, args.model, metas)
    scene["check"] = {**result, "calls": metas, "checkedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    out = SCENES / f"{stem}.proposed.json"
    out.write_text(json.dumps(scene, indent=1, ensure_ascii=False), encoding="utf-8")
    (SCENES / f"{stem}.narration-input.json").write_text(json.dumps(narration_input(scene), indent=1, ensure_ascii=False),
                                                          encoding="utf-8")
    counts: dict[str, int] = {}
    for st in scene["steps"]:
        for x in st["statements"]:
            counts[x["basis"]] = counts.get(x["basis"], 0) + 1
    print(f"wrote {out}: {len(scene['steps'])} steps, {counts}, {sum(len(s['legs']) for s in scene['steps'])} legs, "
          f"basemap {scene['derivedFrom']['file']}; {len(result['warnings'])} warnings")
    for w in result["warnings"]:
        print("  warning:", w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
