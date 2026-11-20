"""The lens analysts: any object read through each specialist lens, then through the general lens.

    python -m GraphRevised.discovery.lens_analyst chr:entity:<id> [--polity roman-republic]
        [--lens military --lens political ...] [--model claude-opus-5-5] [--context-only]

A lens is a way of reading, never stored (D-039, D-063). Each specialist lens agent is grounded per
polity (curation/lens-grounding/<polity>.json) and briefed by its lens (curation/lenses.json). It reads
what the graph already holds about the object (its claims and their neighbours' claims, with status
and voices, and for an event its phases and the moments placed in them) and the sources held for it,
then returns:

    findings          its questions answered from the claims given, each citing them by ref
    gaps              what the claims cannot answer, with where to look: an unread passage of a held
                      source, a source not held, or a relationship or entity missing
    predicate needs   relationships the registry lacks for this lens (granular and time-boxed)
    note              a short lens note, ours

The general lens then reads the object and all the specialists' readings, and adds the interactions
between dimensions and the gaps it judges duplicates.

The rest is deterministic: a cited ref that was not given is reported as invented; a gap in a held
source at a locator the readers already observed is marked already read; a predicate need already in
the registry is marked existing; gaps that point at the same passage, or the same relationship
between the same entities, are listed as overlaps across lenses. Nothing is written to the graph:
gaps and needs are run state (31 §3.1) for the source plan and the curator. The run file goes to
GraphRevised/runs/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from neo4j import GraphDatabase
from pydantic import BaseModel

from GraphRevised.proposals.passage_reader import anthropic_client
from GraphRevised.proposals.prompt_version import prompt_version
from GraphRevised.proposals.registry import load_registry
from GraphRevised import localdb

GRAPH_REVISED = Path(__file__).resolve().parents[1]
LENSES_PATH = GRAPH_REVISED / "curation" / "lenses.json"
GROUNDING_DIRECTORY = GRAPH_REVISED / "curation" / "lens-grounding"
INQUIRIES_DIRECTORY = GRAPH_REVISED / "inquiries"
BRIEFS_DIRECTORY = GRAPH_REVISED / "briefs"
RUNS_DIRECTORY = GRAPH_REVISED / "runs"
DEFAULT_MODEL = "claude-opus-5-5"
GENERAL = "general"
MOMENTS_PER_PHASE = 40

SPECIALIST_PROMPT = """\
You are a specialist lens agent for a historical knowledge graph. You read one object through one \
lens only, grounded in the lens's native terms, core sources, and rules for one polity. You are given \
the object, every claim the graph holds about it and its neighbours (each with a ref such as c12, \
its status, and its voices), and the sources held for it (each with a ref such as w3 and the \
locators its readers have already read).

Do four things:
1. Findings: answer the lens's questions that the claims given can answer. Cite the claims by ref. \
Use only the claims given, not your own knowledge; where the claims are thin or the voices disagree, \
say so in the strength.
2. Gaps: for each question the claims cannot answer, or answer only thinly, say why it matters to \
this lens and where to look. Prefer an unread passage of a held source (give its ref and the \
locator as the source numbers it); else a source not held (title and author, and a locator if you \
know one); else say which relationship or entity is missing. Name the registry predicate the answer \
would need, or a new one. Do not repeat a gap the readers have already covered: a locator listed as \
read has been read.
3. Predicate needs: relationships this lens needs that the registry lacks. Each must be granular \
(one kind of act or tie, not a category) and time-boxed (true at a time, with dates), with the kinds \
it joins and one example from this object.
4. Note: three to six sentences, the lens's reading of the object, marked as ours, resting on the \
findings.

Your knowledge of the period may direct where to look; it is never evidence. Stay within your lens: \
leave other dimensions to their own lenses.
"""

GENERAL_PROMPT = """\
You are the general lens for a historical knowledge graph: you read one object across every \
dimension at once. You are given the object, the claims the graph holds (refs c1...), the sources \
held (refs w1...), and the readings of the specialist lenses, each with its findings, gaps (refs such \
as military:g2), predicate needs, and note.

Do five things:
1. Findings: answer the general lens's questions from the claims, citing them by ref.
2. Interactions: where the dimensions act on each other in this object (a military means to a \
political end, an economic cause of a social change). Name the lenses involved, state the \
interaction, and cite the claims or the specialists' findings it rests on.
3. Duplicates: specialist gaps that ask the same question or point at the same passage; give their \
refs in groups.
4. Gaps: what no specialist lens covers, in the same form as theirs.
5. Note: three to six sentences, the object's significance across dimensions, marked as ours.

Use only the claims and readings given as evidence; your own knowledge may direct where to look.
"""


Strength = Literal["well attested", "thin", "contested", "absent"]
GapKind = Literal["unread passage", "source not held", "relationship missing", "entity missing"]


class Finding(BaseModel):
    question: str
    answer: str
    claims: list[str]
    strength: Strength


class Gap(BaseModel):
    question: str
    why: str
    kind: GapKind
    work_ref: str | None
    source: str | None
    locator: str | None
    predicate: str | None
    entities: list[str]


class PredicateNeed(BaseModel):
    name: str
    definition: str
    subject_kinds: list[str]
    object_kinds: list[str]
    example: str


class SpecialistOutput(BaseModel):
    findings: list[Finding]
    gaps: list[Gap]
    predicate_needs: list[PredicateNeed]
    note: str


class Interaction(BaseModel):
    lenses: list[str]
    statement: str
    rests_on: list[str]


class GeneralOutput(BaseModel):
    findings: list[Finding]
    interactions: list[Interaction]
    duplicates: list[list[str]]
    gaps: list[Gap]
    predicate_needs: list[PredicateNeed]
    note: str


def load_lenses(path: Path = LENSES_PATH) -> dict[str, dict[str, Any]]:
    return {lens["id"]: lens for lens in json.loads(path.read_text(encoding="utf-8"))["lenses"]}


def load_grounding(polity: str, directory: Path = GROUNDING_DIRECTORY) -> dict[str, Any]:
    path = directory / f"{polity}.json"
    if not path.exists():
        raise SystemExit(f"no grounding for {polity}: {path.name} is drafted by the agent and reviewed first")
    return json.loads(path.read_text(encoding="utf-8"))


CLAIMS_QUERY = """
MATCH (e:Entity {id: $id})
OPTIONAL MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(e)
WHERE NOT a.status IN ['rejected', 'superseded']
WITH e, collect(DISTINCT a) AS direct
OPTIONAL MATCH (e)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(d:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(n:Entity)
WHERE n <> e AND NOT d.status IN ['rejected', 'superseded']
WITH direct, collect(DISTINCT n) AS neighbours
OPTIONAL MATCH (s:Entity)<-[:ASSERTION_SUBJECT]-(b:Assertion)-[:ASSERTION_OBJECT]->(o:Entity)
WHERE s IN neighbours AND o IN neighbours AND NOT b.status IN ['rejected', 'superseded']
      AND NOT b.predicate IN ['partOf', 'describedBy']
WITH direct, collect(DISTINCT b) AS ring
UNWIND direct + ring AS a
MATCH (a)-[:ASSERTION_SUBJECT]->(s:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(o:Entity)
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_CONTEXT]->(c:Entity)
RETURN DISTINCT a.id AS id, a.predicate AS predicate, a.status AS status, a.category AS category,
       properties(a) AS props, s.id AS subjectId, coalesce(s.shortLabel, s.label) AS subject,
       head([label IN labels(s) WHERE label <> 'Entity']) AS subjectKind,
       o.id AS objectId, coalesce(o.shortLabel, o.label) AS object,
       head([label IN labels(o) WHERE label <> 'Entity']) AS objectKind,
       collect(DISTINCT coalesce(w.shortLabel, w.label)) AS voices, collect(DISTINCT c.label) AS context
ORDER BY predicate, subject, object, id
"""

MOMENTS_QUERY = """
MATCH (ph:Entity)<-[:ASSERTION_SUBJECT]-(p:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(:Entity {id: $id})
WHERE ph.id STARTS WITH 'chr:entity:phase:' AND NOT p.status IN ['rejected', 'superseded']
OPTIONAL MATCH (m:Entity)<-[:ASSERTION_SUBJECT]-(q:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph)
WHERE NOT q.status IN ['rejected', 'superseded']
RETURN ph.id AS id, coalesce(ph.shortLabel, ph.label) AS phase, ph.description AS description,
       collect(coalesce(m.shortLabel, m.label)) AS moments
ORDER BY id
"""

READ_QUERY = """
MATCH (o:SourceObservation)-[:IN_WORK]->(w:Entity) WHERE w.id IN $works
RETURN w.id AS work, collect(o.shortLabel) AS read
"""


def _time(props: dict[str, Any]) -> str | None:
    for key in ("timeEdtf", "timeStartEdtf", "timeStart", "time"):
        if props.get(key):
            end = props.get("timeEndEdtf") or props.get("timeEnd")
            return f"{props[key]}/{end}" if end and end != props[key] else str(props[key])
    return None


def claim_line(ref: str, c: dict[str, Any]) -> str:
    props = c["props"] or {}
    parts = [f"[{ref}] {c['subject']} ({c['subjectKind']}) {c['predicate']}"
             + (f" {c['object']} ({c['objectKind']})" if c["object"] else "")]
    when = _time(props)
    if when:
        parts.append(f"time {when}")
    if props.get("role") or props.get("roleLabel"):
        parts.append(f"role {props.get('roleLabel') or props.get('role')}")
    if props.get("quantity") is not None:
        parts.append(f"quantity {props['quantity']}")
    if c["context"]:
        parts.append("context " + ", ".join(c["context"]))
    parts.append(f"{c['status']}, {c['category'] or 'factual'}")
    parts.append("voices: " + (", ".join(c["voices"]) if c["voices"] else "ours (asserted)"))
    return " | ".join(parts)


def locator_of(short_label: str) -> str:
    """The locator a reader's observation names: the last token of its short label (Author Work 65.3 -> 65.3)."""
    return short_label.rsplit(" ", 1)[-1] if short_label else ""


def held_works(entity_id: str, directory: Path = INQUIRIES_DIRECTORY) -> list[str]:
    """The Works held for the object: the sources of the inquiries whose event it is."""
    works: dict[str, None] = {}
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("narrativeEventId") == entity_id:
            for source in data.get("sources") or [data.get("source") or {}]:
                if source.get("workId"):
                    works[source["workId"]] = None
    return list(works)


def brief_notes(work_id: str, directory: Path = BRIEFS_DIRECTORY) -> str | None:
    path = directory / f"{work_id.rsplit(':', 1)[-1]}.json"
    return json.loads(path.read_text(encoding="utf-8")).get("notes") if path.exists() else None


def gather(session: Any, entity_id: str) -> dict[str, Any]:
    entity = session.run(
        "MATCH (e:Entity {id: $id}) "
        "RETURN e {.id, kind: head([label IN labels(e) WHERE label <> 'Entity']), .label, .description} AS e",
                         id=entity_id).single()
    if entity is None:
        raise SystemExit(f"no entity {entity_id}")
    claims = session.run(CLAIMS_QUERY, id=entity_id).data()
    phases = session.run(MOMENTS_QUERY, id=entity_id).data()
    work_ids = held_works(entity_id)
    labels = {r["id"]: r["label"] for r in session.run(
        "MATCH (w:Entity) WHERE w.id IN $ids RETURN w.id AS id, w.label AS label", ids=work_ids).data()}
    read = {r["work"]: sorted({locator_of(s) for s in r["read"] if s}) for r in
            session.run(READ_QUERY, works=work_ids).data()}
    works = [{"id": w, "label": labels.get(w, w), "notes": brief_notes(w), "read": read.get(w, [])} for w in work_ids]
    return {"entity": entity["e"], "claims": claims, "phases": phases, "works": works}


def context_text(ctx: dict[str, Any]) -> tuple[str, dict[str, str], dict[str, str]]:
    """The packet every lens reads, with refs: c<n> for claims, w<n> for held Works."""
    claim_refs = {f"c{i + 1}": c["id"] for i, c in enumerate(ctx["claims"])}
    work_refs = {f"w{i + 1}": w["id"] for i, w in enumerate(ctx["works"])}
    e = ctx["entity"]
    lines = [f"Object: {e['label']} ({e['kind']}) {e['id']}", f"Description: {e.get('description') or 'none'}", "",
             f"Claims ({len(ctx['claims'])}):"]
    lines += [claim_line(ref, c) for ref, c in zip(claim_refs, ctx["claims"])]
    if ctx["phases"]:
        lines += ["", "Phases, with the moments the sources depict in each (our placement, proposed):"]
        for p in ctx["phases"]:
            shown = p["moments"][:MOMENTS_PER_PHASE]
            more = len(p["moments"]) - len(shown)
            lines.append(f"- {p['phase']}: {p['description'] or ''}")
            lines += [f"    · {m}" for m in shown] + ([f"    · … {more} more"] if more > 0 else [])
    lines += ["", "Sources held:"]
    for ref, w in zip(work_refs, ctx["works"]):
        lines.append(f"[{ref}] {w['label']}")
        if w["notes"]:
            lines.append(f"    brief: {w['notes']}")
        lines.append("    read: " + (", ".join(w["read"]) if w["read"] else "nothing yet"))
    return "\n".join(lines), claim_refs, work_refs


def lens_text(lens: dict[str, Any], grounding: dict[str, Any], registry_ids: list[str]) -> str:
    g = grounding["lenses"].get(lens["id"], {})
    lines = [f"Lens: {lens['label']}. {lens['purpose']}", f"In scope: {lens['relevance']}", "Questions:"]
    lines += [f"- {q}" for q in lens["questions"]]
    lines += ["", f"Grounding for {grounding['polity']}:", "Native terms:"]
    lines += [f"- {term}: {gloss}" for term, gloss in g.get("nativeTerms", [])]
    lines.append("Core sources:")
    lines += [f"- {s['author']}, {s['title']}" + (f" ({s['year']})" if s.get("year") else "")
              + f" [{s['type']}{', held' if s.get('held') else ''}]: {s['why']}" for s in g.get("coreSources", [])]
    lines.append("Rules:")
    lines += [f"- {r}" for r in g.get("rules", [])]
    lines += ["", "Registry predicates: " + ", ".join(registry_ids),
              "Predicates this lens highlights: " + (", ".join(lens["predicates"]) or "none yet")]
    return "\n".join(lines)


def _call(client, model: str, system: str, user: str, output_format) -> tuple[Any, dict]:
    response = client.beta.messages.parse(model=model, max_tokens=16000, system=system,
                                          messages=[{"role": "user", "content": user}], output_format=output_format)
    meta = {"model": response.model, "stopReason": response.stop_reason,
            "inputTokens": response.usage.input_tokens, "outputTokens": response.usage.output_tokens}
    return (None if response.stop_reason == "refusal" else response.parsed_output), meta


def specialist_packet(lens_block: str, context: str) -> str:
    return f"{lens_block}\n\n---\n\n{context}"


def general_packet(lens_block: str, context: str, readings: dict[str, dict[str, Any]]) -> str:
    parts = [lens_block, "---", context, "---", "Specialist readings:"]
    for lens_id, r in readings.items():
        parts.append(f"\n## {lens_id}\nNote: {r['note']}\nFindings:")
        parts += [f"- {f['question']} -> {f['answer']} [{', '.join(f['claims'])}] ({f['strength']})" for f in r["findings"]]
        parts.append("Gaps:")
        parts += [f"- [{g['ref']}] {g['question']} ({g['kind']}; {g.get('work') or g.get('source') or ''} "
                  f"{g.get('locator') or ''}; predicate {g.get('predicate') or 'none'})" for g in r["gaps"]]
        parts.append("Predicate needs: " + ", ".join(p["name"] for p in r["predicate_needs"]))
    return "\n".join(parts)


def check(lens_id: str, output: SpecialistOutput | GeneralOutput, claim_refs: dict[str, str], work_refs: dict[str, str],
          works: list[dict[str, Any]], registry_ids: set[str], gap_refs: set[str] = frozenset()) -> dict[str, Any]:
    """The deterministic checks on one lens's reading: refs resolved, invented refs reported, gaps in passages
    already read marked, predicate needs already in the registry marked."""
    read = {w["id"]: set(w["read"]) for w in works}
    invented: list[str] = []

    def resolve(refs: list[str]) -> list[str]:
        out = []
        for ref in refs:
            ref = ref.strip().strip("[]")
            if ref in claim_refs:
                out.append(claim_refs[ref])
            elif ref not in gap_refs and not re.fullmatch(r"\w+:f\d+", ref):
                invented.append(ref)
        return out

    findings = [f.model_dump() | {"claims": resolve(f.claims)} for f in output.findings]
    gaps = []
    for i, g in enumerate(output.gaps):
        gap = g.model_dump() | {"ref": f"{lens_id}:g{i + 1}"}
        work = work_refs.get((g.work_ref or "").strip().strip("[]"))
        gap["work"] = work
        if g.work_ref and not work:
            invented.append(g.work_ref)
        gap["alreadyRead"] = bool(work and g.locator and g.locator.strip() in read.get(work, set()))
        gap["predicateExists"] = bool(g.predicate and g.predicate in registry_ids)
        gaps.append(gap)
    needs = [p.model_dump() | {"exists": p.name in registry_ids} for p in output.predicate_needs]
    reading = {"lens": lens_id, "note": output.note, "findings": findings, "gaps": gaps, "predicate_needs": needs,
               "invented": invented}
    if isinstance(output, GeneralOutput):
        reading["interactions"] = [i.model_dump() | {"rests_on": resolve(i.rests_on) or i.rests_on}
                                   for i in output.interactions]
        reading["duplicates"] = output.duplicates
    return reading


def _norm(text: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def overlaps(readings: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Gaps of different lenses that point at the same passage, or at the same predicate between the same entities."""
    keys: dict[tuple, list[str]] = {}
    for r in readings.values():
        for g in r["gaps"]:
            if g["work"] and g["locator"]:
                keys.setdefault(("passage", g["work"], g["locator"].strip()), []).append(g["ref"])
            if g["predicate"] and g["entities"]:
                keys.setdefault(("relationship", g["predicate"], frozenset(_norm(e) for e in g["entities"])), []).append(g["ref"])
    out = []
    for key, refs in keys.items():
        if len({r.split(":")[0] for r in refs}) > 1:
            out.append({"by": key[0], "key": [k if not isinstance(k, frozenset) else sorted(k) for k in key[1:]],
                        "gaps": refs})
    return out


def summary(reading: dict[str, Any]) -> dict[str, int]:
    gaps = reading["gaps"]
    return {"findings": len(reading["findings"]), "gaps": len(gaps),
            "unreadPassages": sum(1 for g in gaps if g["kind"] == "unread passage" and not g["alreadyRead"]),
            "alreadyRead": sum(1 for g in gaps if g["alreadyRead"]),
            "sourcesNotHeld": sum(1 for g in gaps if g["kind"] == "source not held"),
            "relationshipOrEntityMissing": sum(1 for g in gaps if g["kind"] in ("relationship missing", "entity missing")),
            "newPredicates": sum(1 for p in reading["predicate_needs"] if not p["exists"]),
            "invented": len(reading["invented"])}


PROMPT_VERSION = prompt_version("lens-analyst-v1", SPECIALIST_PROMPT + GENERAL_PROMPT, claim_line, context_text,
                                lens_text, specialist_packet, general_packet)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entity")
    parser.add_argument("--polity", default="roman-republic")
    parser.add_argument("--lens", action="append", help="specialist lenses to run (default: all); general runs last")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--context-only", action="store_true", help="print the packet and stop, without calling a model")
    args = parser.parse_args(argv)

    lenses, grounding, registry = load_lenses(), load_grounding(args.polity), load_registry()
    registry_ids = sorted(registry.predicates)
    # A catalogued lens (lenses.json) has no grounding yet: it is not read until one is drafted and reviewed.
    specialists = args.lens or [k for k, v in lenses.items() if k != GENERAL and v.get("status") != "catalogued"]
    unknown = [k for k in specialists if k not in lenses or k == GENERAL]
    if unknown:
        raise SystemExit(f"not specialist lenses: {unknown}")

    driver = GraphDatabase.driver(
        localdb.uri(),
        auth=localdb.auth(),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=localdb.database()) as session:
            ctx = gather(session, args.entity)
    finally:
        driver.close()
    context, claim_refs, work_refs = context_text(ctx)
    if args.context_only:
        print(context)
        print(f"\n{len(ctx['claims'])} claims, {len(ctx['phases'])} phases, {len(ctx['works'])} works, "
              f"{len(context)} characters")
        return 0

    client = anthropic_client()
    calls, readings = [], {}
    for lens_id in specialists:
        block = lens_text(lenses[lens_id], grounding, registry_ids)
        output, meta = _call(client, args.model, SPECIALIST_PROMPT, specialist_packet(block, context), SpecialistOutput)
        calls.append(meta | {"lens": lens_id})
        if output is None:
            print(f"{lens_id}: no reading ({meta['stopReason']})")
            continue
        readings[lens_id] = check(lens_id, output, claim_refs, work_refs, ctx["works"], set(registry_ids))
        print(f"{lens_id}: {summary(readings[lens_id])}")

    gap_refs = {g["ref"] for r in readings.values() for g in r["gaps"]}
    block = lens_text(lenses[GENERAL], grounding, registry_ids)
    output, meta = _call(client, args.model, GENERAL_PROMPT, general_packet(block, context, readings), GeneralOutput)
    calls.append(meta | {"lens": GENERAL})
    general = check(GENERAL, output, claim_refs, work_refs, ctx["works"], set(registry_ids), gap_refs) if output else None
    if general:
        print(f"general: {summary(general)}; interactions {len(general['interactions'])}, "
              f"duplicate groups {len(general['duplicates'])}")

    usage = {k: sum(c.get(k, 0) for c in calls) for k in ("inputTokens", "outputTokens")}
    run = {
        "entity": ctx["entity"], "polity": args.polity, "createdAt": datetime.now(timezone.utc).isoformat(),
        "promptVersion": PROMPT_VERSION, "model": args.model, "lensesVersion": json.loads(LENSES_PATH.read_text(encoding="utf-8"))["version"],
        "groundingVersion": grounding["version"], "usage": usage, "calls": calls,
        "context": {"claims": len(ctx["claims"]), "phases": len(ctx["phases"]),
                    "works": [{"ref": r, "id": w} for r, w in work_refs.items()]},
        "summary": {k: summary(v) for k, v in readings.items()} | ({GENERAL: summary(general)} if general else {}),
        "overlaps": overlaps(readings), "readings": readings, "general": general,
    }
    RUNS_DIRECTORY.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RUNS_DIRECTORY / f"lens-{args.entity.rsplit(':', 1)[-1]}-{stamp}.json"
    path.write_bytes((json.dumps(run, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(f"overlaps across lenses: {len(run['overlaps'])}; {usage['inputTokens']} in, {usage['outputTokens']} out "
          f"-> {path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
