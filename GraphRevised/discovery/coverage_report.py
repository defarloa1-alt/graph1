"""How far an event is from "done" (41-ENDGAME-PLAN.md §4): one line per checklist item.

    python -m GraphRevised.discovery.coverage_report GraphRevised/inquiries/<event>.json [--save]

Read-only, no model calls. For the inquiry's event it reports each item of the
"done" checklist as met, not met, or not built yet, with the counts behind it:

1. who, what, where, when: an accepted claim for each (participatedIn,
   partOf, occurredAt, occurred); "nothing attested" cannot be recorded yet.
2. every core source read through: each assigned passage (the passage
   finder's selection, else the inquiry's chapters) read by the general reader
   and by each lens specialist, as the run logs show. A dry run (not submitted)
   is shown but does not count.
3. every lens question marked: the latest lens analysis of the event, its
   marks (well attested, thin, contested, absent), and any question unmarked.
4. the phase spine reviewed: open phase placements (our own voice).
5. why recorded as voices: live interpretive claims on the event, by voice,
   and its passages of note.
6. consistency checks: not built yet (41 §3.4).
7. corroboration independent (D-148): the event's facts by attestation, and
   how many still rest on untraced modern or reference works.

--save also writes the result as JSON to runs/coverage-<event>-<time>.json.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.discovery.event_phases import PROPOSER_ID as PHASE_PROPOSER
from GraphRevised.discovery.passage_finder import load_finds

GRAPH_REVISED = Path(__file__).resolve().parents[1]
RUNS = GRAPH_REVISED / "runs"
LENSES = GRAPH_REVISED / "curation" / "lenses.json"
LIVE = ["accepted", "proposed"]
OPEN = ["submitted", "validating", "deferred"]
MARKS = {"well attested": "answered", "thin": "thin", "contested": "contested", "absent": "open"}

BASICS = {  # checklist item 1: question -> (predicate, the event's side of the claim)
    "who": ("participatedIn", "object"),
    "what": ("partOf", "subject"),
    "where": ("occurredAt", "subject"),
    "when": ("occurred", "subject"),
}

BASIC = """
MATCH (a:Assertion {predicate: $predicate})-[:%s]->(:Entity {id: $event})
WHERE a.status IN $live
RETURN a.status AS status, a.timeEdtf IS NOT NULL AS dated, count(*) AS n
"""

PLACEMENTS = """
MATCH (p:Proposal {createdBy: $proposer})-[:PROPOSES]->(a:Assertion {predicate: "partOf"})-[:ASSERTION_OBJECT]->(phase:Entity)
MATCH (phase)<-[:ASSERTION_SUBJECT]-(link:Assertion {predicate: "partOf"})-[:ASSERTION_OBJECT]->(:Entity {id: $event})
WHERE link.status IN $live
RETURN p.status AS status, count(DISTINCT p) AS n
"""

WHY = """
MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(:Entity {id: $event})
WHERE a.status IN $live AND a.category = "interpretive"
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity)
RETURN a.predicate AS predicate, a.status AS status, coalesce(w.label, "our own") AS voice
"""

NOTES = """
MATCH (n:Annotation {kind: "passage-of-note"})-[:CONCERNS]->(:Entity {id: $event})
RETURN n.status AS status, count(*) AS n
"""

PARTS = """
MATCH (part:Entity)<-[:ASSERTION_SUBJECT]-(a:Assertion {predicate: "partOf"})-[:ASSERTION_OBJECT]->(:Entity {id: $event})
WHERE a.status IN $live
OPTIONAL MATCH (sub:Entity)<-[:ASSERTION_SUBJECT]-(b:Assertion {predicate: "partOf"})-[:ASSERTION_OBJECT]->(part)
WHERE b.status IN $live
RETURN collect(DISTINCT part.id) + collect(DISTINCT sub.id) AS ids
"""


def basics(tx, event: str) -> dict[str, Any]:
    found = {}
    for question, (predicate, side) in BASICS.items():
        rel = "ASSERTION_OBJECT" if side == "object" else "ASSERTION_SUBJECT"
        rows = tx.run(BASIC % rel, predicate=predicate, event=event, live=LIVE).data()
        counts = Counter()
        for r in rows:
            counts[r["status"]] += r["n"]
            if r["dated"]:
                counts[r["status"] + " dated"] += r["n"]
        accepted = counts["accepted"] if predicate != "occurred" else counts["accepted dated"]
        found[question] = {"predicate": predicate, "accepted": counts["accepted"], "proposed": counts["proposed"],
                           **({"acceptedDated": counts["accepted dated"]} if predicate == "occurred" else {}),
                           "met": accepted > 0}
    return found


def _runs(inquiry: dict[str, Any]) -> list[tuple[dict[str, Any], list[str]]]:
    """Each reader run log for this inquiry or its event: (header, refs read)."""
    found = []
    for path in sorted(RUNS.glob("*reader*.jsonl")):
        lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            continue
        head = lines[0]
        if head.get("inquiry") != inquiry["id"] and head.get("narrativeEventId") != inquiry["narrativeEventId"]:
            continue
        found.append((head | {"file": path.name}, [line["ref"] for line in lines[1:] if "ref" in line]))
    return found


def assigned(inquiry: dict[str, Any], source: dict[str, Any]) -> tuple[list[str], str]:
    finds = load_finds(inquiry["id"], source["workId"])
    if finds:
        return list(finds["selected"]), "passage finder"
    from GraphRevised.adapters.sources import open_source
    return open_source(source, GRAPH_REVISED).refs(source.get("chapters")), "inquiry chapters"


def reading(inquiry: dict[str, Any], lenses: list[str]) -> dict[str, Any]:
    runs = _runs(inquiry)
    sources = []
    for source in inquiry["sources"]:
        refs, chosen_by = assigned(inquiry, source)
        row = {"workId": source["workId"], "voice": source.get("voice"), "assigned": len(refs), "by": chosen_by,
               "readers": {}}
        for reader in ["general", *lenses]:
            stored, dry = set(), set()
            for head, read in runs:
                if head.get("workId") != source["workId"] or ((head.get("lens") or {}).get("id") or "general") != reader:
                    continue
                (dry if head.get("submit") is False else stored).update(read)
            row["readers"][reader] = {"read": len(set(refs) & stored), "dryOnly": len((set(refs) & dry) - stored)}
        row["met"] = all(r["read"] == len(refs) for r in row["readers"].values()) and bool(refs)
        sources.append(row)
    return {"sources": sources, "met": all(s["met"] for s in sources)}


def lens_questions(event: str) -> dict[str, Any]:
    lenses = json.loads(LENSES.read_text(encoding="utf-8"))["lenses"]
    analyses = []
    for path in sorted(RUNS.glob("lens-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if (data.get("entity") or {}).get("id") == event:
            analyses.append((data.get("createdAt", ""), path.name, data))
    if not analyses:
        return {"analysis": None, "lenses": {}, "met": False}
    created, name, data = max(analyses)
    readings = dict(data.get("readings", {}))
    if data.get("general"):
        readings["general"] = data["general"]
    out = {}
    for lens in lenses:
        questions = lens.get("questions", [])
        marks = {}
        for f in readings.get(lens["id"], {}).get("findings", []):
            # The analysis may restate a question in shorter words: match it to the closest one.
            match = difflib.get_close_matches(f["question"], questions, n=1, cutoff=0.6)
            if match:
                marks.setdefault(match[0], MARKS.get(f.get("strength"), f.get("strength")))
        counts = Counter(marks.get(q, "unmarked") for q in questions)
        out[lens["id"]] = {"questions": len(lens.get("questions", [])), **counts,
                           "gaps": len(readings.get(lens["id"], {}).get("gaps", []))}
    return {"analysis": name, "createdAt": created, "lenses": out,
            "met": not any(v.get("unmarked") for v in out.values())}


def phases(tx, event: str) -> dict[str, Any]:
    counts = {r["status"]: r["n"] for r in tx.run(PLACEMENTS, proposer=PHASE_PROPOSER, event=event, live=LIVE)}
    open_ = sum(n for s, n in counts.items() if s in OPEN)
    return {**counts, "open": open_, "met": open_ == 0 and bool(counts)}


def why(tx, event: str) -> dict[str, Any]:
    rows = tx.run(WHY, event=event, live=LIVE).data()
    notes = {r["status"]: r["n"] for r in tx.run(NOTES, event=event)}
    accepted = [r for r in rows if r["status"] == "accepted"]
    return {"claims": Counter(f"{r['predicate']} {r['status']}" for r in rows),
            "voices": sorted({r["voice"] for r in rows}), "passagesOfNote": notes,
            "met": bool(accepted) and len({r["voice"] for r in rows}) >= 2}


def corroboration(tx, event: str) -> dict[str, Any]:
    from GraphRevised.export.cytoscape import projection
    ids = {event, *tx.run(PARTS, event=event, live=LIVE).single()["ids"]}
    elements = projection(tx)["elements"]
    facts = [e["data"] for e in elements["edges"] if e["data"]["source"] in ids or e["data"]["target"] in ids]
    facts += [f for n in elements["nodes"] if n["data"]["id"] in ids for f in n["data"]["facts"]]
    kinds = Counter(re.sub(r" \(.*", "", f["attestation"].split(";")[0]) for f in facts)
    untraced = kinds["modern sources only"] + kinds["reference only"]
    return {"facts": len(facts), "byAttestation": dict(kinds.most_common()), "untraced": untraced,
            "met": True, "note": "met by construction (D-148): a retelling never counts as a second source"}


def report(tx, inquiry: dict[str, Any]) -> dict[str, Any]:
    event = inquiry["narrativeEventId"]
    lenses = [lens["id"] for lens in json.loads(LENSES.read_text(encoding="utf-8"))["lenses"] if lens["id"] != "general"]
    label = tx.run("MATCH (e:Entity {id: $id}) RETURN e.label AS l", id=event).single()["l"]
    return {"event": {"id": event, "label": label}, "inquiry": inquiry["id"],
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "1 who what where when": basics(tx, event), "2 sources read": reading(inquiry, lenses),
            "3 lens questions": lens_questions(event), "4 phase spine": phases(tx, event),
            "5 why as voices": why(tx, event),
            "6 consistency": {"met": None, "note": "checks not built yet (41 §3.4)"},
            "7 corroboration": corroboration(tx, event)}


def _mark(met: bool | None) -> str:
    return "not built" if met is None else ("met" if met else "NOT MET")


def text(r: dict[str, Any]) -> str:
    out = [f"Coverage of {r['event']['label']} against \"done\" (41 §4), {r['at'][:10]}", ""]
    b = r["1 who what where when"]
    out.append(f"1. who, what, where, when: {_mark(all(v['met'] for v in b.values()))}")
    for q, v in b.items():
        extra = f", {v['acceptedDated']} accepted with a date" if "acceptedDated" in v else ""
        out.append(f"   {q} ({v['predicate']}): {v['accepted']} accepted{extra}, {v['proposed']} proposed — {_mark(v['met'])}")
    s = r["2 sources read"]
    out.append(f"2. every core source read through: {_mark(s['met'])}")
    for src in s["sources"]:
        readers = ", ".join(f"{k} {v['read']}/{src['assigned']}" + (f" (+{v['dryOnly']} dry run)" if v["dryOnly"] else "")
                            for k, v in src["readers"].items())
        out.append(f"   {src['voice'] or src['workId']} ({src['assigned']} passages, {src['by']}): {readers}")
    q = r["3 lens questions"]
    out.append(f"3. every lens question marked: {_mark(q['met'])}"
               + (f" (analysis {q['analysis']}, {q['createdAt'][:10]})" if q["analysis"] else " (no lens analysis)"))
    for lens, v in q["lenses"].items():
        marks = ", ".join(f"{v[k]} {k}" for k in ("answered", "thin", "contested", "open", "unmarked") if v.get(k))
        out.append(f"   {lens}: {v['questions']} questions — {marks}; {v['gaps']} gaps named")
    p = r["4 phase spine"]
    out.append(f"4. phase spine reviewed: {_mark(p['met'])} — {p['open']} placements open, "
               f"{p.get('accepted', 0)} accepted, {p.get('rejected', 0)} rejected")
    w = r["5 why as voices"]
    claims = ", ".join(f"{n} {k}" for k, n in sorted(w["claims"].items())) or "none"
    notes = ", ".join(f"{n} {k}" for k, n in w["passagesOfNote"].items()) or "none"
    out.append(f"5. why recorded as voices: {_mark(w['met'])} — interpretive claims: {claims}; "
               f"voices: {', '.join(w['voices']) or 'none'}; passages of note: {notes}")
    out.append(f"6. consistency checks: {_mark(None)} — {r['6 consistency']['note']}")
    c = r["7 corroboration"]
    kinds = ", ".join(f"{n} {k}" for k, n in c["byAttestation"].items())
    out.append(f"7. corroboration independent: {_mark(c['met'])} — {c['facts']} facts on the event and its parts: "
               f"{kinds}. {c['untraced']} rest only on untraced modern or reference works.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path)
    parser.add_argument("--save", action="store_true", help="also write the result to runs/ as JSON")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    inquiry = json.loads(args.inquiry.read_text(encoding="utf-8"))
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            result = session.execute_read(lambda tx: report(tx, inquiry))
    finally:
        driver.close()
    print(text(result))
    if args.save:
        slug = result["event"]["id"].rsplit(":", 1)[-1]
        path = RUNS / f"coverage-{slug}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=dict), encoding="utf-8")
        print(f"\nsaved {path.relative_to(GRAPH_REVISED.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
