"""Storyboard an event's timeline: which presentation for which stretch (26a §5a, shape 10; D-179).

    python -m GraphRevised.narrative.storyboard <inquiry file | event id> [--persona browser] [--model ...]
        [--profiles-only]
    python -m GraphRevised.narrative.storyboard --items <storyboard.json> [--inquiry <inquiry file>]

The first form is the STORYBOARD worker. Code computes an evidence profile for each of the event's phases
(curation/phases.json) from the graph: depicted events, sources, people and groups, located places and the
greatest distance between them, years, open Questions; and, where a scene spec of the event exists, its
steps, movements, units, alternatives, disputes, corrections and statements by basis. The model reads the
catalogue (curation/presentations.json) and the profiles and proposes segments: which phases, which kind,
why, the transition, and the gaps. The code check (check()) holds each segment to its kind's conditions;
problems go back to the model once. The result is written to storyboards/<event>.storyboard.json, every
segment "proposed", for the curator to approve or veto. It chooses forms only: it writes nothing to the
graph, and owns no facts, Questions, predicates or sources.

The second form turns the segments the curator approved, and their gaps, into items for the
orchestrator's extend subcommand (a GENERATE item per segment, once GENERATE is a PlanAction; a REGISTER
or SOURCE_PLAN item per source-task gap). It prints the JSON list; nothing is called.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import typing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from GraphRevised.proposals.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "curation" / "presentations.json"
PHASES = ROOT / "curation" / "phases.json"
SOURCES = ROOT / "curation" / "sources.json"
SCENES = ROOT / "scenes"
OUT = ROOT / "storyboards"
MODEL = "claude-opus-5-5"
GRAINS = ["hours", "days", "months", "years", "decades", "centuries"]


# --- The profile: computed, never written by the model ---------------------------------------------

def km(a: list[float], b: list[float]) -> float:
    (x1, y1), (x2, y2) = a, b
    p1, p2 = math.radians(y1), math.radians(y2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(x2 - x1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(min(1.0, h)))


def extent(points: list[list[float]]) -> int:
    return round(max((km(a, b) for a in points for b in points), default=0))


def graph_profiles(tx: Any, event_id: str, phase_ids: dict[str, str]) -> dict[str, dict[str, Any]]:
    """Per phase, what the graph holds: its members (partOf the phase) and what they reach."""
    rows = tx.run(
        """
        UNWIND $phases AS ph
        MATCH (p:Entity {id: ph.id})
        OPTIONAL MATCH (m:Entity)-[:PART_OF]->(p)
        WITH ph, p, collect(DISTINCT m) AS ms
        CALL (ms) {
          UNWIND (CASE WHEN size(ms) = 0 THEN [null] ELSE ms END) AS m
          OPTIONAL MATCH (a:Annotation)-[:CONCERNS]->(m)
          OPTIONAL MATCH (a)-[:ANNOTATES]->(:SourceObservation)-[:IN_WORK]->(w:Entity)
            WHERE NOT coalesce(w.form, '') IN $creative  // an imaginative work is counted as reception, not as a source
          OPTIONAL MATCH (x:Person)-[:PARTICIPATED_IN]->(m)
          OPTIONAL MATCH (g:Group)-[:PARTICIPATED_IN]->(m)
          OPTIONAL MATCH (m)-[:OCCURRED_AT]->(pl:Place)
          OPTIONAL MATCH (pl)-[:AT_LOCATION]->(l:Location)
          OPTIONAL MATCH (m)-[:IN_YEAR]->(y)
          RETURN count(DISTINCT w) AS sources, count(DISTINCT x) AS persons, count(DISTINCT g) AS groups,
                 collect(DISTINCT CASE WHEN l IS NULL THEN null ELSE {label: pl.label, lonLat: [l.location.x, l.location.y]} END) AS places,
                 collect(DISTINCT pl.label) AS placesNamed, collect(DISTINCT y.id) AS years
        }
        OPTIONAL MATCH (q:Question)-[:ABOUT]->(t:Entity) WHERE t = p OR t IN ms
        RETURN ph.key AS key, size(ms) AS members, sources, persons, groups, places, placesNamed, years,
               count(DISTINCT q) AS questions
        """,
        phases=[{"key": k, "id": v} for k, v in phase_ids.items()], creative=sorted(load_registry().creative_forms),
    ).data()
    out = {}
    for r in rows:
        located = [p for p in r["places"] if p and None not in p["lonLat"]]  # a Location with no point is not located
        out[r["key"]] = {"members": r["members"], "events": r["members"], "sources": r["sources"], "persons": r["persons"],
                         "groups": r["groups"], "placesNamed": len([p for p in r["placesNamed"] if p]),
                         "locatedPlaces": sorted({p["label"] for p in located}),
                         "_points": [p["lonLat"] for p in located], "years": sorted(y for y in r["years"] if y),
                         "questions": r["questions"]}
    memory = tx.run(
        """
        MATCH (s:Assertion)-[:ASSERTION_OBJECT]->(:Entity {id: $event})
        WHERE s.predicate IN ['commemorates', 'depicts']
        RETURN s.predicate AS p, count(*) AS n
        """, event=event_id).data()
    out["_memory"] = {r["p"]: r["n"] for r in memory}
    return out


def scene_profiles(event_id: str) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], str | None]:
    """Per phase, what a scene spec of the event holds (steps carry their phase); steps with no phase
    are returned apart, as a stretch beyond the event's phases."""
    for path in sorted(SCENES.glob("*.proposed.json")):
        scene = json.loads(path.read_text(encoding="utf-8"))
        if scene.get("subject", {}).get("id") != event_id or scene.get("type") not in ("movement", "flyby"):
            continue
        places = {p["label"]: p["lonLat"] for p in scene.get("places", {}).values()}
        by: dict[str, dict[str, Any]] = {}
        loose: list[dict[str, Any]] = []
        for st in scene["steps"]:
            pts = []
            for leg in st.get("legs") or []:
                pts += [p["lonLat"] for p in [leg["from"], *(leg.get("via") or []), leg["to"]]]
            for pl in st.get("placements") or []:
                pts += pl["line"]
            for label in st.get("places") or []:
                if label in places:
                    pts.append(places[label])
            text = " ".join(x["text"] for x in st["statements"])
            pts += [ll for label, ll in places.items() if label in text]
            basis: dict[str, int] = {}
            for x in st["statements"]:
                basis[x["basis"]] = basis.get(x["basis"], 0) + 1
            row = {"step": st["order"], "view": st.get("view"), "grain": "hours" if st.get("view") == "battle" else "months",
                   "movements": len(st.get("legs") or []),
                   "units": len({pl["unit"]["label"] for pl in st.get("placements") or []}),
                   "alternatives": [k for k in ("ordersOfBattle", "routes") if st.get(k)],
                   "disputes": 1 if st.get("disputed") else 0, "corrections": len(st.get("corrected") or []),
                   "statements": basis, "_points": pts}
            (by.setdefault(st["phase"], {"rows": []})["rows"].append(row) if st.get("phase") else loose.append(row))
        return by, loose, path.name
    return {}, [], None


def merge_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"sceneSteps": sorted(r["step"] for r in rows), "movements": 0, "units": 0, "alternatives": [],
                           "disputes": 0, "corrections": 0, "statements": {}, "_points": []}
    for r in rows:
        for k in ("movements", "disputes", "corrections"):
            out[k] += r[k]
        out["units"] = max(out["units"], r["units"])
        out["alternatives"] += r["alternatives"]
        out["_points"] += r["_points"]
        for b, n in r["statements"].items():
            out["statements"][b] = out["statements"].get(b, 0) + n
    grains = [r["grain"] for r in rows]
    out["grain"] = min(grains, key=GRAINS.index) if grains else None
    out["grainFrom"] = "scene view" if grains else None
    return out


def profiles(event_id: str, session: Any) -> dict[str, Any]:
    spine = json.loads(PHASES.read_text(encoding="utf-8"))["events"].get(event_id)
    if not spine:
        raise SystemExit(f"no phases decided for {event_id}: the curator decides them first (curation/phases.json)")
    slug = event_id.split(":", 2)[2]
    ids = {p["key"]: f"chr:entity:phase:{slug}:{p['key']}" for p in spine["phases"]}
    graph = session.execute_read(lambda tx: graph_profiles(tx, event_id, ids))
    by_scene, loose, scene_file = scene_profiles(event_id)
    stretches = []
    for p in spine["phases"]:
        g = graph.get(p["key"], {})
        s = merge_rows(by_scene.get(p["key"], {}).get("rows", []))
        # the extent is what the scene draws where a scene covers the phase; else what the graph's places span
        points = s["_points"] if s["_points"] else g.get("_points", [])
        years = g.get("years", [])
        grain = s["grain"] or ("years" if len(years) > 1 else None)
        stretches.append({"key": p["key"], "label": p["label"], "scope": p["scope"],
                          **{k: v for k, v in g.items() if not k.startswith("_")},
                          **{k: v for k, v in s.items() if not k.startswith("_") and k != "grain"},
                          "grain": grain, "grainFrom": s["grainFrom"] or ("years in the graph" if grain else None),
                          "extentKm": extent(points), "extentFrom": "scene" if s["_points"] else "graph places",
                          "extentGraphKm": extent(g.get("_points", [])), "pointsLocated": len(points)})
    if loose:
        s = merge_rows(loose)
        stretches.append({"key": "beyond", "label": "Beyond the event's phases (scene steps with no phase)",
                          "scope": "what the scene shows after or around the event", "members": 0,
                          **{k: v for k, v in s.items() if not k.startswith("_")}, "extentKm": extent(s["_points"]),
                          "pointsLocated": len(s["_points"])})
    return {"event": event_id, "scene": scene_file, "stretches": stretches,
            "memory": {"commemorations": graph["_memory"].get("commemorates", 0),
                       "depictions": graph["_memory"].get("depicts", 0)}}


# --- The proposal: the model's -----------------------------------------------------------------------

class Gap(BaseModel):
    what: str
    becomes: Literal["question", "source-task", "none"]
    note: str
    source: str | None = Field(description="for a source-task: a source id from the registry list, else null")


class Segment(BaseModel):
    stretches: list[str] = Field(description="consecutive stretch keys, in order")
    title: str
    kind: str = Field(description="a kind id from the catalogue (not an overlay)")
    with_kinds: list[str] = Field(description="kinds shown with it, e.g. order-of-battle, disagreement")
    why: list[str] = Field(description="each reason a profile value against the kind's condition")
    transition: Literal["open", "zoom-in", "zoom-out", "cut", "pan"]
    gaps: list[Gap]


class Proposal(BaseModel):
    segments: list[Segment]
    overlays: list[str] = Field(description="overlay kinds (e.g. narration) and the segment titles they cover")


SYSTEM = """You are the storyboard specialist of Chrystallum, a history graph with strict provenance.
You choose how each stretch of an event's timeline is presented; you never add a fact. You receive the
catalogue of presentation kinds (what each answers, what it needs, what it must never imply, whether it is
built) and a profile of each stretch, computed from the graph and from any scene spec. Propose segments:
- cover every stretch exactly once, in order; a segment may join consecutive stretches that share a view;
- choose a kind whose `needs` the joined profile meets; never choose an overlay as a segment's kind;
- give reasons as profile values against the kind's conditions ("extent 12 km and a grain of hours");
- follow the grain rules for the view, and say the transition from the last segment;
- where a stretch qualifies for nothing richer than a timeline, say so, and name in `gaps` what would let
  it qualify (located places, movements, commemorating objects...): a gap becomes a Question, a
  source-task (give a source id from the registry list when one fits), or none;
- a kind that is not built may still be proposed; say it is not built in a reason.
Write plainly. Return JSON only."""


def ask(client: Any, model: str, catalogue: dict, prof: dict, registry: list[dict], persona: str,
        repair: list[str] | None = None, earlier: str | None = None) -> tuple[Proposal | None, dict]:
    user = (f"Persona: {persona}.\n\nCATALOGUE:\n{json.dumps(catalogue, ensure_ascii=False)}\n\n"
            f"PROFILES:\n{json.dumps(prof, ensure_ascii=False)}\n\nREGISTRY (sources by id and status):\n"
            f"{json.dumps(registry, ensure_ascii=False)}")
    messages = [{"role": "user", "content": user}]
    if repair:
        messages += [{"role": "assistant", "content": earlier or ""},
                     {"role": "user", "content": "The check found these problems. Return the whole proposal again, "
                                                 "fixed, changing only what they require:\n- " + "\n- ".join(repair)}]
    r = client.beta.messages.parse(model=model, max_tokens=12000, system=SYSTEM, messages=messages,
                                   output_format=Proposal, betas=["server-side-fallback-2026-07-01"],
                                   extra_body={"fallbacks": "default"})
    meta = {"model": r.model, "stopReason": r.stop_reason, "inputTokens": r.usage.input_tokens,
            "outputTokens": r.usage.output_tokens}
    return (None if r.stop_reason in ("refusal", "max_tokens") else r.parsed_output), meta


# --- The check: code holds each choice to its kind's conditions --------------------------------------

def joined(prof: dict, keys: list[str]) -> dict[str, Any]:
    rows = [s for s in prof["stretches"] if s["key"] in keys]
    j: dict[str, Any] = {"members": 0, "sources": 0, "persons": 0, "groups": 0, "movements": 0, "units": 0,
                         "questions": 0, "disputes": 0, "corrections": 0, "alternatives": 0, "phases": len(rows),
                         "locatedPlaces": set(), "statements": 0, "sceneSteps": 0}
    grains = []
    for r in rows:
        for k in ("members", "sources", "persons", "groups", "movements", "questions", "disputes", "corrections"):
            j[k] += r.get(k, 0) or 0
        j["units"] = max(j["units"], r.get("units", 0) or 0)
        j["alternatives"] += len(r.get("alternatives", []))
        j["locatedPlaces"] |= set(r.get("locatedPlaces", []))
        j["statements"] += sum((r.get("statements") or {}).values())
        j["sceneSteps"] += len(r.get("sceneSteps", []))
        if r.get("grain"):
            grains.append(r["grain"])
    j["locatedPlaces"] = len(j["locatedPlaces"]) or sum(1 for r in rows if r.get("pointsLocated", 0) >= 2) * 2
    j["extentKm"] = max((r.get("extentKm", 0) for r in rows), default=0)
    j["grain"] = min(grains, key=GRAINS.index) if grains else None
    j["phases"] = max(j["phases"], j["sceneSteps"])  # a stretch told in several scene steps has that many phases
    j["events"] = j["members"]
    j["entities"] = 1
    j["disputes"] += j["questions"]
    j["checkedScene"] = j["sceneSteps"] > 0
    j["commemorations"], j["depictions"] = prof["memory"]["commemorations"], prof["memory"]["depictions"]
    j["pictures"] = 0  # not profiled yet: the gallery is read by the explorer, not here
    return j


def meets(cond: str, value: Any) -> bool | None:
    """'>=2', '<50', a word, True; None when the value is unknown."""
    if value is None:
        return None
    if cond is True:
        return bool(value)
    if isinstance(cond, str) and cond[:2] in (">=", "<="):
        return value >= float(cond[2:]) if cond[:2] == ">=" else value <= float(cond[2:])
    if isinstance(cond, str) and cond[:1] in (">", "<"):
        return value > float(cond[1:]) if cond[0] == ">" else value < float(cond[1:])
    return value == cond


def needs_met(needs: dict[str, Any], j: dict[str, Any]) -> tuple[list[str], list[str]]:
    failed, unknown = [], []
    for field, cond in needs.items():
        if field == "any":
            ok = []
            for c in cond:
                name, op = next(((c[:i], c[i:]) for i in range(len(c)) if c[i] in "<>="), (c, True))
                ok.append(meets(op, j.get(name)))
            if not any(ok):
                failed.append(f"any of {cond}")
            continue
        r = meets(cond, j.get(field))
        if r is None:
            unknown.append(f"{field} {cond} (not in the profile)")
        elif not r:
            failed.append(f"{field} {cond}, but the profile gives {j.get(field)}")
    return failed, unknown


def check(proposal: dict, prof: dict, catalogue: dict) -> dict[str, list[str]]:
    kinds = {k["id"]: k for k in catalogue["kinds"]}
    order = [s["key"] for s in prof["stretches"]]
    problems, warnings, seen = [], [], []
    last_extent = None
    for n, seg in enumerate(proposal["segments"], 1):
        keys = seg["stretches"]
        if not keys or any(k not in order for k in keys):
            problems.append(f"segment {n}: unknown stretches {keys}")
            continue
        idx = [order.index(k) for k in keys]
        if idx != list(range(idx[0], idx[0] + len(idx))):
            problems.append(f"segment {n}: stretches {keys} are not consecutive")
        seen += keys
        kind = kinds.get(seg["kind"])
        if not kind:
            problems.append(f"segment {n}: kind {seg['kind']} is not in the catalogue")
            continue
        if kind.get("overlay"):
            problems.append(f"segment {n}: {seg['kind']} is an overlay, not a segment's kind")
        for w in seg.get("with_kinds", []):
            if w not in kinds:
                problems.append(f"segment {n}: kind {w} shown with it is not in the catalogue")
        j = joined(prof, keys)
        failed, unknown = needs_met(kind["needs"], j)
        for f in failed:
            problems.append(f"segment {n} ({seg['kind']}): needs {f}")
        for u in unknown:
            warnings.append(f"segment {n} ({seg['kind']}): cannot check {u}")
        for w in seg.get("with_kinds", []):
            if w in kinds:
                f2, _ = needs_met(kinds[w]["needs"], j)
                for f in f2:
                    problems.append(f"segment {n}: {w} shown with it needs {f}")
        if not kind.get("built"):
            warnings.append(f"segment {n}: {seg['kind']} is not built; it can be approved but not generated yet")
        if not seg["why"]:
            problems.append(f"segment {n}: no reasons")
        elif not any(ch.isdigit() for ch in " ".join(seg["why"])):
            warnings.append(f"segment {n}: its reasons cite no profile value")
        for g in seg.get("gaps", []):
            if g["becomes"] == "source-task" and not g.get("source"):
                warnings.append(f"segment {n}: source-task gap '{g['what']}' names no registry source; it becomes a Question")
        ext = j["extentKm"] or None
        if ext and last_extent:
            if seg["transition"] == "zoom-in" and ext >= last_extent:
                warnings.append(f"segment {n}: zoom-in, but its extent {ext} km is not smaller than {last_extent} km")
            if seg["transition"] == "zoom-out" and ext <= last_extent:
                warnings.append(f"segment {n}: zoom-out, but its extent {ext} km is not larger than {last_extent} km")
        last_extent = ext or last_extent
    missing = [k for k in order if k not in seen]
    doubled = sorted({k for k in seen if seen.count(k) > 1})
    if missing:
        problems.append(f"stretches not covered: {missing}")
    if doubled:
        problems.append(f"stretches in more than one segment: {doubled}")
    if seen and [k for k in order if k in seen] != list(dict.fromkeys(seen)):
        problems.append("segments are not in the timeline's order")
    return {"problems": problems, "warnings": warnings}


# --- Items for the orchestrator's extend ------------------------------------------------------------

GENERATE_BUILT = {"scene-movement"}  # what scenes/build_scene.py draws
GENERATE_KIND = {"movement-scene": "scene-movement", "battle-scene": "scene-battle", "flyby": "scene-flyby",
                 "memory-reception": "memory-reception"}


def plan_items(sb: dict, path: Path, inquiry: str | None) -> tuple[list[dict], list[str]]:
    from GraphRevised.orchestration.contracts import PlanAction

    actions = set(typing.get_args(PlanAction))
    registry = {s["id"]: s for s in json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]}
    items, held = [], []
    for seg in sb["segments"]:
        if seg.get("status") != "approved":
            continue
        origin = {"storyboard": sb["id"], "segment": seg["order"]}
        if seg["kind"] in GENERATE_KIND:
            if "GENERATE" not in actions:
                held.append(f"segment {seg['order']} ({seg['kind']}): waits for GENERATE")
            elif GENERATE_KIND[seg["kind"]] not in GENERATE_BUILT:
                held.append(f"segment {seg['order']} ({seg['kind']}): no worker draws {GENERATE_KIND[seg['kind']]} yet")
            else:
                items.append({"action": "GENERATE", "target": sb["subject"]["id"], "rationale": "; ".join(seg["why"]),
                              "expected_outputs": [f"a {seg['kind']} spec in scenes/, with its narration input"], "budget_usd": 1.5, "lens": None,
                              "call": {"worker": "GraphRevised.scenes.build_scene",
                                       "arguments": ["--kind", GENERATE_KIND[seg["kind"]], "--storyboard", str(path),
                                                     "--segment", str(seg["order"])]},
                              "origin": origin})
        for g_n, gap in enumerate(seg.get("gaps", [])):
            if gap["becomes"] != "source-task" or gap.get("source") not in registry:
                continue
            src = registry[gap["source"]]
            o = origin | {"gap": g_n}
            if src["status"] == "candidate":
                items.append({"action": "REGISTER", "target": src["id"], "rationale": f"{gap['what']}: {gap['note']}",
                              "expected_outputs": ["the source's rights quoted in the registry", "its status"],
                              "budget_usd": 0, "lens": None, "origin": o,
                              "call": {"worker": "manual", "instructions":
                                       f"Read the rights for {src['label']} at its own site ({src.get('homepage', '')}). "
                                       f"Quote them in curation/sources.json under {src['id']}, with the page and the date; "
                                       "set its rights class and nonCommercial; register it if they allow."}})
            elif inquiry:
                items.append({"action": "SOURCE_PLAN", "target": src["id"], "rationale": f"{gap['what']}: {gap['note']}",
                              "expected_outputs": ["a source plan in plans/"], "budget_usd": 1.0, "lens": None,
                              "origin": o, "call": {"worker": "GraphRevised.discovery.event_source_plan",
                                                    "arguments": [inquiry]}})
            else:
                held.append(f"segment {seg['order']} gap {g_n}: {src['id']} is registered; give --inquiry to plan it")
    return items, held


# --- Running it -------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", nargs="?", help="an inquiry file, or an event id")
    parser.add_argument("--persona", default="browser", choices=["browser", "student", "scholar"])
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--profiles-only", action="store_true", help="print the profiles; call no model")
    parser.add_argument("--items", type=Path, help="a storyboard: print extend items for its approved segments")
    parser.add_argument("--inquiry", help="with --items: the inquiry file, for SOURCE_PLAN items")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    if args.items:
        sb = json.loads(args.items.read_text(encoding="utf-8"))
        items, held = plan_items(sb, args.items, args.inquiry)
        print(json.dumps(items, indent=1, ensure_ascii=False))
        for h in held:
            print("held:", h, file=sys.stderr)
        return 0
    if not args.target:
        parser.error("give an inquiry file or an event id")
    event_id = args.target if args.target.startswith("chr:entity:") else \
        json.loads(Path(args.target).read_text(encoding="utf-8"))["narrativeEventId"]

    from neo4j import GraphDatabase
    from GraphRevised import localdb
    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            prof = profiles(event_id, session)
            label = session.run("MATCH (e:Entity {id: $id}) RETURN e.label AS l", id=event_id).single()["l"]
    finally:
        driver.close()
    if args.profiles_only:
        print(json.dumps(prof, indent=1, ensure_ascii=False))
        return 0

    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    registry = [{"id": s["id"], "label": s["label"], "status": s["status"],
                 "gives": (s.get("coverage") or {}).get("evidence", [])}
                for s in json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]]
    from GraphRevised.proposals.passage_reader import anthropic_client
    client = anthropic_client(run=f"storyboard:{event_id}")
    parsed, meta = ask(client, args.model, catalogue, prof, registry, args.persona)
    metas = [meta]
    if parsed is None:
        print(f"no storyboard: {meta['stopReason']}")
        return 1
    result = check(parsed.model_dump(), prof, catalogue)
    if result["problems"]:
        again, meta = ask(client, args.model, catalogue, prof, registry, args.persona,
                          repair=result["problems"], earlier=parsed.model_dump_json())
        metas.append(meta)
        if again is not None:
            parsed, result = again, check(again.model_dump(), prof, catalogue)
    slug = event_id.split(":", 2)[2]
    sb = {
        "id": f"chr:storyboard:{slug}", "subject": {"id": event_id, "label": label}, "persona": args.persona,
        "catalogueVersion": catalogue["version"], "scene": prof["scene"],
        "proposedBy": f"narrative/storyboard.py with {metas[-1]['model']}",
        "proposedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "calls": metas,
        "profiles": prof["stretches"], "memory": prof["memory"],
        "segments": [{"order": n, "status": "proposed", **{("with" if k == "with_kinds" else k): v for k, v in s.items()}}
                     for n, s in enumerate(parsed.model_dump()["segments"], 1)],
        "overlays": parsed.overlays,
        "check": {**result, "checkedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")},
    }
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{slug}.storyboard{'.rejected' if result['problems'] else ''}.json"
    out.write_text(json.dumps(sb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out}: {len(sb['segments'])} segments, {len(result['problems'])} problems, {len(result['warnings'])} warnings")
    for p in result["problems"] + result["warnings"]:
        print("  ", p)
    return 1 if result["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
