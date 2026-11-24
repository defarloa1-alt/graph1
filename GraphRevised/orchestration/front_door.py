"""The front door (31-ONE-COMMAND.md §3.1, §5 step 3): one command becomes a plan, and nothing runs.

    python -m GraphRevised.orchestration.front_door "graph <anything>" [--kind Event] [--mode guided]
        [--budget 10] [--owner curator] [--offline] [--save] [--json]

From the command it resolves the focus, anchors it to a Subject, reads what the graph already holds,
writes an orientation brief, and plans the inquiry's line items from the kind's recipe
(curation/recipes.json), trimmed to what coverage shows is missing. It writes nothing to the graph
and runs no worker: the orchestrator (31 §5 step 4) runs the approved items.

Code first (D-174). There is no model call here yet:

- identity is local first (the words of a local Entity's labels and aliases, identity/local_candidates),
  then Wikidata's search; one exact match resolves it, several make it ambiguous (an interrupt), and a
  single partial match is asked about, never assumed;
- the scope test of 08 is not built: a resolved focus of a kind with a recipe is in scope, and the
  brief says so;
- the brief is read from the graph, the inquiry file and the source registry: years, places, the
  Questions about the focus (its controversies), entities whose words overlap its own (identity
  traps), the inquiry's sources, the registry's readable systems, the lenses in use. Each statement
  names where it came from: reconnaissance, never evidence.

A focus that already has an inquiry file is planned against it (curator, 2026-11-24). A focus without
one gets a draft inquiry file in plans/, which the curator approves before it moves to inquiries/.

The default only shows the plan. --save writes the run file (runs/front-door-<focus>-<time>.json, an
InquiryRunState with plan version 1 and status awaiting_user), a dossier version (dossiers/), and the
draft inquiry file when there is one. Nothing is overwritten.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from GraphRevised.orchestration.contracts import (
    AuthorityMatch, Choice, CoverageMap, Gap, IdentityCandidate, Inquiry, InquiryPlan, InquiryRunState, Interrupt,
    OrientationBrief, OrientationDossier, OrientationStatement, PlanItem, RelationshipNeed, ResolvedFocus, RunMode,
    RunStatus, ScopeDecision, SourceCandidate, SubjectAnchor,
)

GRAPH_REVISED = Path(__file__).resolve().parents[1]
RECIPES = GRAPH_REVISED / "curation" / "recipes.json"
REGISTRY = GRAPH_REVISED / "curation" / "sources.json"
LENSES = GRAPH_REVISED / "curation" / "lenses.json"
INQUIRIES = GRAPH_REVISED / "inquiries"
PLANS = GRAPH_REVISED / "plans"
RUNS = GRAPH_REVISED / "runs"
DOSSIERS = GRAPH_REVISED / "dossiers"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
DECIDED_BY = "front-door (code, D-174)"
LIVE = ["accepted", "proposed"]
OPEN = ["submitted", "validating", "deferred"]
RELATIONS = {"exactMatch": "exact", "closeMatch": "close", "broadMatch": "broader", "narrowMatch": "narrower",
             "relatedMatch": "related"}
HEADING_SYSTEMS = ("LCSH", "FAST", "LCNAF")
STANDING = {"primary": "primary", "secondary": "modern", "tertiary": "reference"}

Search = Callable[[str], list[dict[str, Any]]]  # Wikidata search: [{"id", "label", "description", "kind"}]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slug(label: str) -> str:
    """The harvester's id rule (harvest/apply._slug), so a planned focus id is the one first contact makes."""
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or "unnamed"


def parse_command(command: str) -> str:
    """The thing named: `graph "X"`, `Graph X`, or just X."""
    text = re.sub(r"^\s*graph\s+", "", command.strip(), flags=re.IGNORECASE).strip()
    return text.strip("\"'“”‘’ ").strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# --- Identity ------------------------------------------------------------------------------------

def wikidata_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Wikidata's own search, each hit with its label, description, and the kind the harvest rules give
    its classes (None when the checked table does not decide it)."""
    from GraphRevised.adapters.wikidata_identity import polite_get
    from GraphRevised.harvest.apply import SUPERCLASSES, kind_of
    from GraphRevised.harvest.wikidata_harvest import load_rules

    hits = polite_get(WIKIDATA_API, params={"action": "wbsearchentities", "search": query, "language": "en",
                                            "limit": limit, "format": "json", "formatversion": 2}).json().get("search", [])
    if not hits:
        return []
    ids = "|".join(h["id"] for h in hits)
    entities = polite_get(WIKIDATA_API, params={"action": "wbgetentities", "ids": ids, "props": "claims",
                                                "format": "json", "formatversion": 2}).json().get("entities", {})
    rules = load_rules()
    return [{"id": h["id"], "label": h.get("label", h["id"]), "description": h.get("description"),
             "kind": kind_of(entities.get(h["id"], {}), rules, SUPERCLASSES),
             "source": f"{WIKIDATA_API}?action=wbsearchentities&search={query}"} for h in hits]


LOCAL_QIDS = """
UNWIND $ids AS id
MATCH (e:Entity {id: id})
OPTIONAL MATCH (e)-[l:HAS_AUTHORITY_RECORD {role: 'entity_identity'}]->(a:AuthorityRecord {system: 'Wikidata'})
WHERE l.status = 'accepted'
RETURN e.id AS id, e.description AS description, head(collect(a.identifier)) AS qid
"""

BY_QID = """
MATCH (e:Entity)-[l:HAS_AUTHORITY_RECORD {role: 'entity_identity'}]->(:AuthorityRecord {system: 'Wikidata', identifier: $qid})
WHERE l.status = 'accepted' AND coalesce(e.status, '') <> 'retired'
RETURN e.id AS id, e.label AS label, head([k IN labels(e) WHERE k <> 'Entity']) AS kind, e.description AS description
"""


def _local(tx, query: str, kind: str | None) -> list[dict[str, Any]]:
    from GraphRevised.identity.local_candidates import candidates

    rows = candidates(tx, query, kind, threshold=0.5, limit=8)
    extra = {r["id"]: r for r in tx.run(LOCAL_QIDS, ids=[r["id"] for r in rows]).data()}
    return [r | {"qid": extra.get(r["id"], {}).get("qid"), "description": extra.get(r["id"], {}).get("description")}
            for r in rows]


def _candidate(row: dict[str, Any], why: str) -> IdentityCandidate:
    return IdentityCandidate(label=row["label"], description=row.get("description"), kind=row["kind"],
                             qid=row.get("qid"), local_entity_id=row.get("localId", row.get("id") if row.get("local") else None),
                             why=why)


def resolve(tx, query: str, kind: str | None, search: Search | None) -> tuple[ResolvedFocus, list[OrientationStatement]]:
    """Local first, then Wikidata. One exact match resolves; several are ambiguous; a lone partial match
    is unresolved, to be asked about."""
    from GraphRevised.identity.local_candidates import similarity

    statements: list[OrientationStatement] = []
    local = [r | {"local": True} for r in _local(tx, query, kind)]
    exact = [r for r in local if r["score"] == 1.0]
    if len(exact) == 1:
        row = exact[0]
        why = f"the only local {row['kind']} whose words are the command's (matched “{row['matched']}”)"
        statements.append(OrientationStatement(text=f"The focus is the local {row['kind']} {row['label']}.",
                                               source=f"graph: {row['id']}"))
        return ResolvedFocus(status="resolved", chosen=_candidate(row, why), decided_by=DECIDED_BY), statements
    if len(exact) > 1:
        return ResolvedFocus(status="ambiguous", candidates=[_candidate(r, "a local entity with the same words")
                                                             for r in exact]), statements

    hits = []
    for hit in (search(query) if search else []):
        held = tx.run(BY_QID, qid=hit["id"]).data()
        if held:
            hit = hit | {"localId": held[0]["id"], "kind": held[0]["kind"], "local": True}
        hit_kind = hit.get("kind") or kind
        if kind and hit_kind != kind:
            continue
        if hit_kind is None:
            statements.append(OrientationStatement(
                text=f"Wikidata's “{hit['label']}” ({hit['id']}) was left out: the harvest rules do not give its kind.",
                source=hit["source"]))
            continue
        hits.append(hit | {"kind": hit_kind, "qid": hit["id"]})
    same = [h for h in hits if similarity(query, h["label"]) == 1.0]
    if len(same) == 1:
        hit = same[0]
        where = "held locally as " + hit["localId"] if hit.get("localId") else "not yet in the graph"
        statements.append(OrientationStatement(text=f"Wikidata's “{hit['label']}” ({hit['qid']}) is the focus, {where}.",
                                               source=hit["source"]))
        return ResolvedFocus(status="resolved", decided_by=DECIDED_BY, chosen=_candidate(
            hit, "the only Wikidata result whose words are the command's")), statements

    pool = [_candidate(r, f"a local entity sharing words with the command (matched “{r['matched']}”)") for r in local]
    seen = {c.local_entity_id for c in pool if c.local_entity_id} | {c.qid for c in pool if c.qid}
    pool += [_candidate(h, "a Wikidata result for the command") for h in hits
             if h.get("localId") not in seen and h["qid"] not in seen]
    if len(pool) >= 2:
        return ResolvedFocus(status="ambiguous", candidates=pool), statements
    return ResolvedFocus(status="unresolved", candidates=pool), statements


# --- The Subject ---------------------------------------------------------------------------------

SUBJECTS = """
MATCH (s:Subject)-[:HAS_SUBJECT_FOCUS]->(:Entity {id: $id})
OPTIONAL MATCH (s)-[l:HAS_AUTHORITY_RECORD]->(a:AuthorityRecord)
WHERE l.status = 'accepted'
RETURN s.id AS id, s.label AS label, s.status AS status,
       collect(CASE WHEN a IS NULL THEN NULL ELSE {system: a.system, identifier: a.identifier, label: a.label,
               relation: l.relation, checked: a.retrievedAt} END) AS matches
ORDER BY s.id
"""

HEADINGS = """
MATCH (:Entity {id: $id})-[l:HAS_AUTHORITY_RECORD]->(a:AuthorityRecord)
WHERE l.status = 'accepted' AND a.system IN $systems
RETURN a.system AS system, a.identifier AS identifier, a.label AS label, l.relation AS relation, a.retrievedAt AS checked
"""


def _match(row: dict[str, Any]) -> AuthorityMatch:
    kind = RELATIONS.get(row.get("relation") or "", "candidate")
    return AuthorityMatch(system=row["system"], identifier=row["identifier"], label=row["label"], match_type=kind,
                          checked_at=row.get("checked") if kind != "candidate" else None)


def anchor(tx, focus: IdentityCandidate) -> tuple[SubjectAnchor, list[OrientationStatement]]:
    """The Subject whose focus this is; else a proposed one, labelled as ours, with the focus's own
    library headings beside it (28 §6). Nothing is created here."""
    statements = []
    rows = tx.run(SUBJECTS, id=focus.local_entity_id).data() if focus.local_entity_id else []
    if rows:
        row = rows[0]
        matches = [_match(m) for m in row["matches"]]
        provisional = row["status"] != "accepted" or not any(m.match_type == "exact" for m in matches)
        statements.append(OrientationStatement(text=f"The Subject is “{row['label']}” ({row['status']}).",
                                               source=f"graph: {row['id']}"))
        if len(rows) > 1:
            statements.append(OrientationStatement(
                text="Other Subjects share this focus: " + "; ".join(f"“{r['label']}”" for r in rows[1:]),
                source="graph: " + ", ".join(r["id"] for r in rows[1:])))
        return SubjectAnchor(subject_id=row["id"], matches=matches, provisional=provisional), statements
    headings = tx.run(HEADINGS, id=focus.local_entity_id, systems=list(HEADING_SYSTEMS)).data() if focus.local_entity_id else []
    return SubjectAnchor(proposed_label=f"History of {focus.label}", matches=[_match(h) for h in headings],
                         provisional=True), statements


# --- Coverage ------------------------------------------------------------------------------------

CLAIMS = """
MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(:Entity {id: $id})
WITH DISTINCT a
OPTIONAL MATCH (p:Proposal)-[:PROPOSES]->(a)
RETURN a.status AS status, count(DISTINCT a) AS claims,
       count(DISTINCT CASE WHEN p.status IN $open THEN p END) AS open
"""

NEIGHBOURS = """
MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(:Entity {id: $id})
WHERE a.status IN $live
MATCH (a)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(other:Entity)
WHERE other.id <> $id
RETURN DISTINCT other.id AS id ORDER BY id
"""


def find_inquiry(focus_id: str | None, directory: Path = INQUIRIES) -> Path | None:
    """The inquiry file whose focus this is (its focusIds, else its narrative event)."""
    if not focus_id:
        return None
    for path in sorted(directory.glob("*.json")):
        data = load_json(path)
        if focus_id in (data.get("focusIds") or [data.get("narrativeEventId")]):
            return path
    return None


def coverage(tx, focus_id: str | None, inquiry: dict[str, Any] | None, kind: str) -> tuple[CoverageMap, dict[str, Any]]:
    """What the graph holds for the focus, and for an event with an inquiry the "done" checklist
    (discovery/coverage_report, 41 §4), whose unmet items are the gaps."""
    if not focus_id:
        return CoverageMap(gaps=[Gap(kind="entity", description="the focus is not in the graph",
                                     why="first contact makes it a proposed Entity")]), {}
    by_status, open_proposals = {}, 0
    for row in tx.run(CLAIMS, id=focus_id, open=OPEN).data():
        by_status[row["status"]] = row["claims"]
        open_proposals += row["open"]
    reused = [r["id"] for r in tx.run(NEIGHBOURS, id=focus_id, live=LIVE).data()]
    report: dict[str, Any] = {}
    gaps: list[Gap] = []
    if kind == "Event":
        from GraphRevised.discovery import coverage_report

        if inquiry:
            report = coverage_report.report(tx, inquiry)
        else:
            report = {"1 who what where when": coverage_report.basics(tx, focus_id)}
        gaps = _gaps(report)
    if not inquiry:
        gaps.append(Gap(kind="source", description="no inquiry reads sources for this focus",
                        why="a draft inquiry file is written for the curator to approve"))
    works = [s["workId"] for s in (inquiry or {}).get("sources", [])]
    return CoverageMap(reused_entity_ids=reused, claims_by_status=by_status, open_proposals=open_proposals,
                       works_read=works, gaps=gaps), report


def _gaps(report: dict[str, Any]) -> list[Gap]:
    gaps = []
    for question, row in report.get("1 who what where when", {}).items():
        if not row["met"]:
            gaps.append(Gap(kind="relationship", description=f"{question}: no accepted {row['predicate']} claim",
                            why="item 1 of the done checklist (41 §4)"))
    reading = report.get("2 sources read")
    if reading and not reading["met"]:
        for source in reading["sources"]:
            short = [k for k, v in source["readers"].items() if v["read"] < source["assigned"]]
            if short:
                gaps.append(Gap(kind="source", description=f"{source['voice'] or source['workId']}: not read by "
                                + ", ".join(short), why="item 2 of the done checklist (41 §4)"))
    lens = report.get("3 lens questions")
    if lens and not lens["met"]:
        gaps.append(Gap(kind="other", description="lens questions open, thin, or unmarked",
                        why="item 3 of the done checklist (41 §4)"))
    phases = report.get("4 phase spine")
    if phases and not phases["met"]:
        gaps.append(Gap(kind="phase", description=f"{phases['open']} phase placements open",
                        why="item 4 of the done checklist (41 §4)"))
    return gaps


# --- The orientation brief -----------------------------------------------------------------------

YEARS = """
MATCH (:Entity {id: $id})-[:OCCURRED|IN_YEAR|BEGAN|ENDED]->(y:Year)
RETURN min(y.year) AS earliest, max(y.year) AS latest
"""

PLACES = """
MATCH (a:Assertion {predicate: 'occurredAt'})-[:ASSERTION_SUBJECT]->(:Entity {id: $id})
WHERE a.status IN $live
MATCH (a)-[:ASSERTION_OBJECT]->(p:Entity)
RETURN p.id AS id, p.label AS label, min(a.status) AS status ORDER BY status, label
"""

DISTINCT = """
MATCH (:Entity {id: $id})<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(a:Assertion {predicate: 'distinctFrom', status: 'accepted'})
      -[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(other:Entity)
WHERE other.id <> $id
RETURN collect(DISTINCT other.id) AS ids
"""
NOT_TRAPS = {"Question", "Position"}  # their labels quote the focus's name; they are about it, not mistaken for it

QUESTIONS = """
MATCH (q:Question)<-[:ASSERTION_SUBJECT]-(a:Assertion {predicate: 'about'})-[:ASSERTION_OBJECT]->(:Entity {id: $id})
WHERE a.status IN $live
RETURN q.id AS id, q.label AS label, a.status AS status ORDER BY a.status, label
"""

WORKS = """
UNWIND $ids AS id
MATCH (w:Entity {id: id})
RETURN w.id AS id, w.label AS label, w.standing AS standing
"""


def orient(tx, focus: ResolvedFocus, kind: str, inquiry: dict[str, Any] | None, recipe: dict[str, Any],
           found: list[OrientationStatement]) -> OrientationBrief:
    from GraphRevised.identity.local_candidates import candidates

    chosen = focus.chosen
    statements = list(found)
    fid = chosen.local_entity_id
    earliest = latest = None
    places: list[str] = []
    controversies: list[str] = []
    traps: list[str] = []
    needs: list[RelationshipNeed] = []
    if fid:
        years = tx.run(YEARS, id=fid).single()
        earliest, latest = years["earliest"], years["latest"]
        if earliest is not None:
            statements.append(OrientationStatement(text=f"The graph dates it to {_year(earliest)}"
                                                   + (f" to {_year(latest)}" if latest != earliest else "") + ".",
                                                   source=f"graph: {fid} (Year links)"))
        for row in tx.run(PLACES, id=fid, live=LIVE).data():
            places.append(row["label"])
            statements.append(OrientationStatement(text=f"It took place at {row['label']} ({row['status']}).",
                                                   source=f"graph: {row['id']}"))
        for row in tx.run(QUESTIONS, id=fid, live=LIVE).data():
            controversies.append(f"{row['label']} ({row['status']} Question, {row['id']})")
        distinct = set(tx.run(DISTINCT, id=fid).single()["ids"])
        for row in candidates(tx, chosen.label, None, exclude=fid, threshold=0.5, limit=12):
            if row["kind"] in NOT_TRAPS or (row["kind"] == "Work" and row["score"] < 1.0) or len(traps) == 5:
                continue  # a Work is mistaken for the focus only when its title is the focus's name
            settled = "; already recorded as distinct (accepted distinctFrom)" if row["id"] in distinct else ""
            traps.append(f"{row['label']} ({row['kind']}, {row['id']}) shares words with the focus "
                         f"(matched “{row['matched']}”){settled}")
    sources =[SourceCandidate(work=row["label"], kind=STANDING.get(row["standing"] or "", "reference"),
                               why=f"already a source of the inquiry ({row['id']}, standing {row['standing'] or 'not set'})")
               for row in tx.run(WORKS, ids=[s["workId"] for s in (inquiry or {}).get("sources", [])]).data()]
    federations = [Choice(name=s["label"], why=f"the source registry reads it (status {s['status']}, {s['id']})")
                   for s in load_json(REGISTRY)["sources"] if s.get("status") == "read"]
    lenses = [Choice(name=lens["label"], why=f"a lens in use (curation/lenses.json: {lens['id']})")
              for lens in load_json(LENSES)["lenses"] if lens.get("status") != "catalogued"]
    if not fid:
        needs.append(RelationshipNeed(subject=chosen.label, why="the focus needs first contact before anything else"))
    return OrientationBrief(focus=focus, kind=kind, earliest_year=earliest, latest_year=latest, places=places,
                            relationship_needs=needs, federations=federations, sources=sources, lenses=lenses,
                            controversies=controversies, identity_traps=traps, statements=statements,
                            stopping_rule="; ".join(recipe["stoppingRules"]))


def _year(year: int) -> str:
    return f"{-year} BCE" if year < 0 else f"{year} CE"


# --- The plan ------------------------------------------------------------------------------------

def conditions(focus: IdentityCandidate, inquiry: dict[str, Any] | None, report: dict[str, Any],
               estimates: dict[str, Any]) -> dict[str, Any]:
    """Each recipe condition, read from the focus, the inquiry, and the coverage report. A per-source
    condition is the list of sources (with their passages) it holds for; per lens, a dict by lens."""
    sources = (inquiry or {}).get("sources", [])
    wikipedia = {s["adapter"]["type"] for s in load_json(REGISTRY)["sources"]
                 if s["id"] == "wikipedia" and s.get("adapter")}
    read = {r["workId"]: r for r in report.get("2 sources read", {}).get("sources", [])}
    lens = report.get("3 lens questions")
    phases = report.get("4 phase spine")
    by_lens: dict[str, list[dict[str, Any]]] = {}
    for source in sources:
        row = read.get(source["workId"])
        for name, counts in (row or {}).get("readers", {}).items():
            if name != "general" and counts["read"] < row["assigned"]:
                by_lens.setdefault(name, []).append(source | {"passages": row["assigned"] - counts["read"]})
    return {
        "always": True,
        "noLocalEntity": focus.local_entity_id is None,
        "noWikipediaSource": bool(focus.qid) and not any(s.get("type") in wikipedia for s in sources),
        "fewSources": len(sources) < estimates["minSources"],
        "sourceWithoutFinder": [s | {"passages": 0} for s in sources
                                if read.get(s["workId"], {}).get("by") != "passage finder"],
        "sourceUnread": [s | {"passages": read[s["workId"]]["assigned"] - read[s["workId"]]["readers"]["general"]["read"]}
                         for s in sources if s["workId"] in read
                         and read[s["workId"]]["readers"]["general"]["read"] < read[s["workId"]]["assigned"]],
        "sourceUnreadByLens": by_lens,
        "lensQuestionsOpen": bool(lens) and not lens["met"],
        "noPhases": bool(phases) and phases.get("open", 0) + phases.get("accepted", 0) + phases.get("rejected", 0) == 0,
    }


def _fill(arguments: list[str], values: dict[str, str]) -> list[str]:
    return [re.sub(r"\{(\w+)\}", lambda m: values.get(m.group(1), m.group(0)), a) for a in arguments]


def plan_items(recipe: dict[str, Any], held: dict[str, Any], estimates: dict[str, Any], values: dict[str, str],
               budget: float) -> tuple[list[PlanItem], list[str], dict[str, dict[str, Any]]]:
    """The recipe's steps whose conditions hold, in order, within the budget. Returns the items, the
    open questions (steps not built, items left out for the budget), and each item's worker call."""
    items: list[PlanItem] = []
    questions: list[str] = []
    calls: dict[str, dict[str, Any]] = {}
    planned: list[tuple[str, str, str | None]] = []  # (item id, action, workId)
    spent = 0.0
    left_out: list[str] = []
    for step in recipe["steps"]:
        held_value = held.get(step["when"])
        if not held_value:
            continue
        if step.get("worker") is None:
            questions.append(f"{step['action']} is not built yet: {step['rationale']}")
            continue
        if step.get("perLens"):
            units = [(lens, s) for lens, rows in held_value.items() for s in rows]
        elif step.get("perSource"):
            units = [(None, s) for s in held_value]
        else:
            units = [(None, None)]
        for lens, source in units:
            work = source["workId"] if source else None
            cost = (source["passages"] * estimates["perPassageReadUSD"]) if step.get("costPerPassage") else step["budgetUSD"]
            cost = round(cost, 2)
            name = " ".join(x for x in (step["action"], lens, source and (source.get("voice") or work)) if x)
            if left_out or spent + cost > budget + 1e-9:  # the plan is a prefix of the recipe's order
                left_out.append(f"{name} (${cost:.2f})")
                continue
            item_id = f"P{len(items) + 1:02d}"
            after = set(step.get("after", []))
            depends = [i for i, action, w in planned if action in after
                       and (action != "FIND" or w == work)]
            target = work or values.get("focus") or values["label"]
            rationale = step["rationale"] + (f" ({source['passages']} passages)" if source and source["passages"] else "")
            items.append(PlanItem(item_id=item_id, action=step["action"], target=target, rationale=rationale,
                                  expected_outputs=step["outputs"], budget_usd=cost, depends_on=depends, lens=lens))
            calls[item_id] = {"worker": step["worker"],
                              "arguments": _fill(step["arguments"], values | {"workId": work or "", "lens": lens or ""})}
            planned.append((item_id, step["action"], work))
            spent += cost
    if left_out:
        questions.append(f"Left out for the budget (${budget:.2f}): " + "; ".join(left_out))
    return items, questions, calls


# --- The whole front door ------------------------------------------------------------------------

def draft_inquiry(focus: IdentityCandidate, focus_id: str, subject: SubjectAnchor, brief: OrientationBrief) -> dict[str, Any]:
    """A draft inquiry file (29 §2) for a focus that has none; the curator approves it into inquiries/."""
    calendar = "julian" if brief.earliest_year is not None and brief.earliest_year < 1582 else None
    data = {"id": f"chr:inquiry:{slug(focus.label)}", "version": 1, "status": "draft", "draftedBy": DECIDED_BY,
            "label": f"{focus.label}, as its sources tell it", "kind": focus.kind,
            "question": f"What do the sources say about {focus.label}?", "subjectId": subject.subject_id,
            "focusIds": [focus_id], "sources": [], "candidateEntityIds": [], "guidance": [],
            "proposableKinds": [focus.kind]}
    if focus.kind == "Event":
        data["narrativeEventId"] = focus_id
    if calendar:
        data["calendar"] = calendar
    return data


CHOSEN = """
MATCH (e:Entity)
WHERE e.id = $key OR EXISTS {
  (e)-[l:HAS_AUTHORITY_RECORD {role: 'entity_identity'}]->(:AuthorityRecord {system: 'Wikidata', identifier: $key})
  WHERE l.status = 'accepted' }
OPTIONAL MATCH (e)-[l:HAS_AUTHORITY_RECORD {role: 'entity_identity'}]->(a:AuthorityRecord {system: 'Wikidata'})
WHERE l.status = 'accepted'
RETURN e.id AS id, e.label AS label, e.description AS description,
       head([k IN labels(e) WHERE k <> 'Entity']) AS kind, head(collect(a.identifier)) AS qid
"""


def chosen_by_curator(tx, focus: ResolvedFocus, key: str, by: str) -> ResolvedFocus:
    """The curator's answer to an identity question: a local Entity id or a Wikidata QID."""
    for c in focus.candidates + ([focus.chosen] if focus.chosen else []):
        if key in (c.local_entity_id, c.qid):
            return ResolvedFocus(status="resolved", chosen=c.model_copy(update={"why": f"chosen by {by}"}),
                                 candidates=focus.candidates, decided_by=by)
    rows = tx.run(CHOSEN, key=key).data()
    if len(rows) != 1:
        raise ValueError(f"{key} names {len(rows)} local entities; give one local Entity id or a held QID")
    row = rows[0] | {"local": True}
    return ResolvedFocus(status="resolved", chosen=_candidate(row, f"chosen by {by}"), candidates=focus.candidates,
                         decided_by=by)


def front_door(tx, command: str, *, kind: str | None = None, focus_key: str | None = None, mode: RunMode = RunMode.GUIDED, budget: float = 10.0,
               owner: str = "curator", search: Search | None = None, recipes_path: Path = RECIPES,
               inquiries: Path = INQUIRIES, dossiers: Path = DOSSIERS, run_id: str | None = None) -> dict[str, Any]:
    """Plan one command. Returns the run state and what --save would write; writes nothing."""
    recipes = load_json(recipes_path)
    query = parse_command(command)
    run_id = run_id or f"front-door-{slug(query)}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    focus, found = resolve(tx, query, kind, search)
    if focus_key:
        focus = chosen_by_curator(tx, focus, focus_key, owner)
        found.append(OrientationStatement(text=f"{owner} chose the focus: {_who(focus.chosen)}.",
                                          source=f"the command line (--focus {focus_key})"))
    out: dict[str, Any] = {"query": query, "draftInquiry": None, "dossier": None, "calls": {}}
    if focus.status != "resolved":
        options = [_who(c) + (f": {c.description}" if c.description else "") for c in focus.candidates]
        question = (f"Which one does “{query}” name?" if focus.status == "ambiguous" else
                    f"“{query}” matched {'only ' + options[0] if options else 'nothing'}: is that it, or what does it name?")
        state = InquiryRunState(run_id=run_id, command=command, mode=mode, owner=owner, status=RunStatus.AWAITING_USER,
                                interrupts=[Interrupt(interrupt_id=f"{run_id}:identity", reason="identity",
                                                      question=question, options=options)])
        return out | {"state": state, "focus": focus, "statements": found}
    chosen = focus.chosen
    focus_kind = chosen.kind
    recipe = recipes["recipes"].get(focus_kind)
    if recipe is None:
        state = InquiryRunState(run_id=run_id, command=command, mode=mode, owner=owner, status=RunStatus.AWAITING_USER,
                                interrupts=[Interrupt(interrupt_id=f"{run_id}:scope", reason="scope", question=(
                                    f"There is no recipe for a {focus_kind} yet (31 §3.3): write one, or reframe the command?"),
                                    options=[f"a {focus_kind} recipe in curation/recipes.json", "a reframed command"])])
        return out | {"state": state, "focus": focus, "statements": found}

    subject, said = anchor(tx, chosen)
    inquiry_path = find_inquiry(chosen.local_entity_id, inquiries)
    inquiry_data = load_json(inquiry_path) if inquiry_path else None
    cover, report = coverage(tx, chosen.local_entity_id, inquiry_data, focus_kind)
    brief = orient(tx, focus, focus_kind, inquiry_data, recipe, found + said)
    focus_id = chosen.local_entity_id or f"chr:entity:{slug(chosen.label)}"
    if inquiry_path:
        inquiry = Inquiry.from_reading_file(inquiry_path, kind=focus_kind, root=GRAPH_REVISED)
        inquiry_file = inquiry_path.relative_to(GRAPH_REVISED).as_posix()
    else:
        draft = draft_inquiry(chosen, focus_id, subject, brief)
        inquiry_file = f"plans/inquiry-draft-{slug(chosen.label)}.json"
        inquiry = Inquiry(inquiry_id=draft["id"], question=draft["question"], focus_ids=[focus_id], kind=focus_kind,
                          subject_id=subject.subject_id, reading_file=inquiry_file)
        out["draftInquiry"] = {"path": inquiry_file, "data": draft}

    held = conditions(chosen, inquiry_data, report, recipes["estimates"])
    values = {"qid": chosen.qid or "", "focus": focus_id, "inquiry": f"GraphRevised/{inquiry_file}", "label": chosen.label}
    items, questions, calls = plan_items(recipe, held, recipes["estimates"], values, budget)
    if held["fewSources"] and any(i.action == "BUILD_INQUIRY" for i in items):
        questions.append("Once the new sources are in the inquiry, run the front door again: finding, reading, "
                         "lenses and phases are planned from the sources the inquiry then holds (plan v2)")
    phases = report.get("4 phase spine")
    if phases and phases.get("open"):
        questions.append(f"{phases['open']} phase placements wait for the curator's review (not an agent item)")
    if not inquiry_path:
        questions.append(f"Approve the draft inquiry ({inquiry_file}) into inquiries/ before its items run")
    questions.append("The scope test (08) and the model's orientation (controversies, traps, lenses) are not built "
                     "yet (D-174): this brief is read from the graph, the inquiry, and the registries")
    scope = ScopeDecision(decision="IN_SCOPE", primary_intent="HISTORICAL_GRAPH_CONSTRUCTION",
                          explanation=f"the command names a {focus_kind} with a recipe; scope by code until the "
                                      "model's test (08) is built")
    plan = InquiryPlan(plan_id=run_id, inquiry_id=inquiry.inquiry_id, version=1, command=command, mode=mode,
                       scope=scope, focus=focus, subject=subject, coverage=cover, recipe=focus_kind,
                       lenses=brief.lenses, items=items, stopping_rules=recipe["stoppingRules"],
                       unresolved_questions=questions, budget_usd=budget)

    dossier_id = f"chr:dossier:{slug(chosen.label)}"
    versions = sorted(dossiers.glob(f"{slug(chosen.label)}.v*.json"),
                      key=lambda p: int(re.search(r"\.v(\d+)\.json$", p.name).group(1)))
    if versions:
        dossier = OrientationDossier.load(versions[-1]).revise(brief, run_id, inquiry.inquiry_id)
    else:
        dossier = OrientationDossier(dossier_id=dossier_id, version=1, focus_ids=[focus_id],
                                     subject_id=subject.subject_id, brief=brief, used_by_inquiries=[inquiry.inquiry_id],
                                     updated_by_run=run_id)
    out["dossier"] = dossier
    state = InquiryRunState(run_id=run_id, command=command, inquiry_id=inquiry.inquiry_id, dossier_id=dossier_id,
                            dossier_version=dossier.version, mode=mode, owner=owner, status=RunStatus.AWAITING_USER,
                            orientation=brief, plan=plan, plan_versions=[1])
    out["calls"] = calls
    return out | {"state": state, "focus": focus, "statements": brief.statements, "inquiry": inquiry, "report": report}


def save(result: dict[str, Any], runs: Path = RUNS, dossiers: Path = DOSSIERS, root: Path = GRAPH_REVISED) -> list[Path]:
    """The run file (with each item's worker call beside the state), the dossier version, the draft
    inquiry. Refuses to overwrite."""
    written = []
    state: InquiryRunState = result["state"]
    run_path = runs / f"{state.run_id}.json"
    targets = [run_path]
    dossier: OrientationDossier | None = result.get("dossier")
    if dossier:
        targets.append(dossiers / f"{dossier.dossier_id.split(':', 2)[2]}.v{dossier.version}.json")
    draft = result.get("draftInquiry")
    if draft:
        targets.append(root / draft["path"])
    existing = [p for p in targets if p.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite: {', '.join(str(p) for p in existing)}")
    state.save(run_path)
    calls = {"runId": state.run_id, "calls": result["calls"]}
    calls_path = runs / f"{state.run_id}.calls.json"
    calls_path.write_text(json.dumps(calls, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written += [run_path, calls_path]
    if dossier:
        written.append(dossier.save(dossiers))
    if draft:
        path = root / draft["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(draft["data"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    return written


# --- Showing it ----------------------------------------------------------------------------------

def _who(c: IdentityCandidate) -> str:
    codes = ", ".join(x for x in (f"Wikidata {c.qid}" if c.qid else None, c.local_entity_id) if x)
    return f"{c.label} ({c.kind}{', ' + codes if codes else ''})"


def text(result: dict[str, Any]) -> str:
    state: InquiryRunState = result["state"]
    focus: ResolvedFocus = result["focus"]
    lines = [f"Front door: {state.command}", ""]
    if state.plan is None:
        lines.append(f"Focus: {focus.status}.")
        for interrupt in state.open_interrupts():
            lines.append(f"Question for the curator ({interrupt.reason}): {interrupt.question}")
            lines += [f"  - {o}" for o in interrupt.options]
            if interrupt.reason == "identity":
                lines.append("Answer with --focus <local Entity id or QID>.")
        lines += [f"  · {s.text} [{s.source}]" for s in result.get("statements", [])]
        return "\n".join(lines)
    plan, brief = state.plan, state.orientation
    lines.append(f"Focus: {_who(focus.chosen)}, {focus.chosen.why}.")
    s = plan.subject
    lines.append(("Subject: " + (s.subject_id or f"proposed “{s.proposed_label}”")
                  + (" (provisional)" if s.provisional else "")
                  + "".join(f"\n  {m.match_type}: {m.label}" for m in s.matches)))
    draft = result.get("draftInquiry")
    lines.append(f"Inquiry: {plan.inquiry_id}" + (f" — a draft, {draft['path']}" if draft else
                                                  f" ({result['inquiry'].reading_file})"))
    c = plan.coverage
    claims = ", ".join(f"{n} {k}" for k, n in sorted(c.claims_by_status.items())) or "none"
    lines += ["", f"Coverage: claims {claims}; {c.open_proposals} open proposals; {len(c.reused_entity_ids)} entities "
              f"linked; {len(c.works_read)} works in the inquiry"]
    lines += [f"  gap ({g.kind}): {g.description}" for g in c.gaps]
    lines += ["", "Orientation (read from the graph and registries; reconnaissance, not evidence):"]
    lines += [f"  · {st.text} [{st.source}]" for st in brief.statements]
    if brief.controversies:
        lines.append(f"  Controversies: {len(brief.controversies)} Questions about the focus")
        lines += [f"    - {re.sub(r', chr:[^)]*', '', q)}" for q in brief.controversies[:8]]
        if len(brief.controversies) > 8:
            lines.append(f"    … and {len(brief.controversies) - 8} more")
    lines += [f"  Identity trap: {t}" for t in brief.identity_traps]
    lines.append("  Lenses: " + ", ".join(lens.name for lens in brief.lenses))
    lines += ["", f"Plan v{plan.version} ({plan.mode.value}, recipe {plan.recipe}, budget ${plan.budget_usd:.2f}, "
              f"items ${sum(i.budget_usd for i in plan.items):.2f}); nothing has run:"]
    for i in plan.items:
        after = f" after {', '.join(i.depends_on)}" if i.depends_on else ""
        call = result["calls"].get(i.item_id, {})
        lines.append(f"  {i.item_id} {i.action}{' ' + i.lens if i.lens else ''} — {i.target}  ${i.budget_usd:.2f}{after}")
        lines.append(f"      {i.rationale}")
        lines.append(f"      python -m {call.get('worker')} {' '.join(call.get('arguments', []))}")
    if not plan.items:
        lines.append("  (no items: coverage shows nothing the recipe's workers would add)")
    lines += ["", "Open questions:"] + [f"  - {q}" for q in plan.unresolved_questions]
    lines += ["", "Stopping rules: " + "; ".join(plan.stopping_rules)]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", help='the command, e.g. graph "Battle of X"')
    parser.add_argument("--kind", help="the focus's kind, when the command alone is ambiguous")
    parser.add_argument("--focus", help="answer an identity question: the local Entity id or QID the command names")
    parser.add_argument("--mode", choices=[m.value for m in RunMode], default=RunMode.GUIDED.value)
    parser.add_argument("--budget", type=float, default=10.0, help="the plan's model budget in USD (an estimate)")
    parser.add_argument("--owner", default="curator")
    parser.add_argument("--offline", action="store_true", help="no Wikidata search: the local graph only")
    parser.add_argument("--save", action="store_true", help="write the run file, the dossier, and any draft inquiry")
    parser.add_argument("--json", action="store_true", help="print the run state as JSON")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    from neo4j import GraphDatabase
    from GraphRevised import localdb

    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                result = front_door(tx, args.command, kind=args.kind, focus_key=args.focus, mode=RunMode(args.mode), budget=args.budget,
                                    owner=args.owner, search=None if args.offline else wikidata_search)
            finally:
                tx.rollback()  # the front door only reads
    finally:
        driver.close()
    print(result["state"].model_dump_json(indent=2) if args.json else text(result))
    if args.save:
        for path in save(result):
            print(f"wrote {path.relative_to(GRAPH_REVISED.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
