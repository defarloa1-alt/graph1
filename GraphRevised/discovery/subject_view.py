"""Read-only, evidence-aware assertion view for an event Subject.

Run it through ``python -m GraphRevised.discovery.event_subject_view``.

Only direct focus references and one- or two-hop event partOf placements are
included. The two-hop case requires a phase of the focus event as the
intermediate event.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from GraphRevised.discovery.event_evidence_report import build_report
from GraphRevised.discovery.source_text import include_source_text
from GraphRevised.proposals.entities import depicted_event_id


def phase_prefix(focus_id: str) -> str:
    """The id prefix of a focus event's phases (chr:entity:phase:<focus>:)."""
    return f"chr:entity:phase:{focus_id.split(':', 2)[2]}:"


FOCUS_QUERY = """
MATCH (subject:Subject {id: $subjectId})-[:HAS_SUBJECT_FOCUS]->(focus:Entity:Event {id: $focusId})
RETURN subject {.id, .label, .status} AS subject, focus {.id, .label, .status} AS focus
"""

HIERARCHY_QUERY = """
MATCH (subject:Subject {id: $subjectId})
MATCH path = (subject)-[:NARROWER_THAN*1..8]->(parent:Subject)
WHERE all(n IN nodes(path) WHERE single(m IN nodes(path) WHERE m = n))
RETURN [n IN nodes(path) | n {.id, .label, .status}] AS subjects
ORDER BY parent.id, length(path)
"""

PLACEMENTS_QUERY = """
MATCH (child:Entity:Event)<-[:ASSERTION_SUBJECT]-(a:Assertion {predicate: 'partOf'})
      -[:ASSERTION_OBJECT]->(parent:Entity:Event)
WHERE a.status IN ['proposed', 'accepted']
  AND (parent.id = $focusId OR parent.id STARTS WITH $phasePrefix)
  AND child.id <> parent.id
RETURN child {.id, .label, .status} AS child, parent {.id, .label, .status} AS parent,
       a {.id, .label, .status, .predicate, .mode} AS assertion
ORDER BY parent.id, child.id, a.id
"""

ASSERTIONS_QUERY = """
MATCH (a:Assertion)-[role:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]->(e:Entity)
WHERE e.id IN $eventIds AND a.status IN ['proposed', 'accepted']
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(work:Entity:Work)
RETURN a {.id, .label, .status, .predicate, .mode, .category} AS assertion,
       e.id AS eventId, type(role) AS role, work.id AS workId, work.label AS workLabel
ORDER BY a.id, e.id, role
"""

TOPICAL_QUERY = """
MATCH (event:Entity:Event)-[placement:IN_SUBJECT]->(section:Subject)
      -[:NARROWER_THAN]->(subject:Subject {id: $subjectId})
WHERE section.id = $sectionId AND placement.status IN ['proposed', 'accepted']
OPTIONAL MATCH (source:Assertion {id: placement.sourceAssertionId})
RETURN event {.id, .label, .status} AS event, section {.id, .label, .status} AS section,
       properties(placement) AS placement,
       source {.id, .label, .status, .predicate, .mode} AS sourceAssertion
ORDER BY event.id
"""

EVIDENCE_QUERY = """
MATCH (a:Assertion) WHERE a.id IN $assertionIds
CALL (a) {
  MATCH (a)-[link:SUPPORTED_BY]->(o:SourceObservation)
  RETURN o, 'supported' AS evidenceState, null AS proposalId,
         null AS proposalStatus, null AS rationale, link.quotation AS quotation
  UNION ALL
  MATCH (p:Proposal)-[:PROPOSES]->(a)
        MATCH (p)-[link:PROPOSES_EVIDENCE]->(o:SourceObservation)
  RETURN o, 'proposal' AS evidenceState, p.id AS proposalId,
         p.status AS proposalStatus, p.rationale AS rationale, link.quotation AS quotation
}
OPTIONAL MATCH (o)-[:IN_WORK]->(work:Entity:Work)
RETURN DISTINCT a.id AS assertionId, o.id AS observationId, o.locator AS locator,
       o.label AS passage, o.status AS observationStatus, work.id AS workId,
       work.label AS workLabel, evidenceState, proposalId, proposalStatus, rationale, quotation,
       o.passageText AS passageText, o.editionCitation AS editionCitation,
       o.rights AS rights, o.sourceSystem AS sourceSystem
ORDER BY assertionId, evidenceState, proposalId, observationId
"""

TIMELINE_WORKS_QUERY = """
MATCH (event:Entity:Event)<-[:CONCERNS]-(:Annotation {kind: 'entity-mention'})
      -[:ANNOTATES]->(:SourceObservation)-[:IN_WORK]->(work:Entity:Work)
WHERE event.id IN $ids
RETURN DISTINCT event.id AS eventId, work.id AS workId, work.label AS workLabel
ORDER BY workId, eventId
"""


def build_view(tx, *, subject_id: str, focus_id: str, section_id: str | None = None) -> dict:
    phases = phase_prefix(focus_id)
    focus_rows = tx.run(FOCUS_QUERY, subjectId=subject_id, focusId=focus_id).data()
    if len(focus_rows) != 1:
        raise ValueError(f"Expected exactly one Subject-to-focus link for {subject_id} and {focus_id}.")
    subject, focus = focus_rows[0]["subject"], focus_rows[0]["focus"]
    hierarchy = tx.run(HIERARCHY_QUERY, subjectId=subject_id).data()
    placements = tx.run(PLACEMENTS_QUERY, focusId=focus_id, phasePrefix=phases).data()

    routes = defaultdict(list)
    routes[focus_id].append({"kind": "focus", "events": [focus], "placements": []})
    for row in placements:
        if row["parent"]["id"] == focus_id and row["child"]["id"] != focus_id:
            routes[row["child"]["id"]].append({
                "kind": "partOf", "events": [row["child"], focus], "placements": [row["assertion"]],
            })
    for row in placements:
        parent_id, child_id = row["parent"]["id"], row["child"]["id"]
        if not parent_id.startswith(phases) or child_id == focus_id:
            continue
        for parent_route in routes.get(parent_id, []):
            if len(parent_route["placements"]) != 1:
                continue
            routes[child_id].append({
                "kind": "partOf", "events": [row["child"]] + parent_route["events"],
                "placements": [row["assertion"]] + parent_route["placements"],
            })

    topical = tx.run(TOPICAL_QUERY, subjectId=subject_id, sectionId=section_id).data() if section_id else []
    for row in topical:
        routes[row["event"]["id"]].append({
            "kind": "subjectPlacement", "events": [row["event"]], "placements": [],
            "section": row["section"], "topicalPlacement": row["placement"],
            "sourceAssertion": row["sourceAssertion"],
        })

    rows = tx.run(ASSERTIONS_QUERY, eventIds=sorted(routes)).data()
    claims = {}
    for row in rows:
        assertion = row["assertion"]
        claim = claims.setdefault(assertion["id"], {
            **assertion, "mode": assertion["mode"] or "asserted",
            "workId": row["workId"], "workLabel": row["workLabel"], "routes": [], "evidence": [],
        })
        for route in routes[row["eventId"]]:
            claim["routes"].append({"assertionRole": row["role"], **route})

    evidence_ids = set(claims)
    for paths in routes.values():
        for route in paths:
            evidence_ids.update(placement["id"] for placement in route["placements"])
            if route.get("sourceAssertion"):
                evidence_ids.add(route["sourceAssertion"]["id"])
    evidence = defaultdict(list)
    for item in tx.run(EVIDENCE_QUERY, assertionIds=sorted(evidence_ids)).data():
        assertion_id = item["assertionId"]
        evidence[assertion_id].append(include_source_text(item))
    for claim in claims.values():
        claim["evidence"] = evidence[claim["id"]]
        for route in claim["routes"]:
            for placement in route["placements"]:
                placement["evidence"] = evidence[placement["id"]]
            if route.get("sourceAssertion"):
                route["sourceAssertion"]["evidence"] = evidence[route["sourceAssertion"]["id"]]

    return {
        "subject": subject,
        "focus": focus,
        "broaderSubjectPaths": [row["subjects"] for row in hierarchy],
        "limitations": [
            "Routes are relevance paths, not assertions that every connected event is historically part of the focus event.",
            "Only proposed and accepted claims and placement assertions are included; their statuses are not promoted.",
            "Two-hop event placement paths use a focus-event phase; other event paths are not included.",
            "Only explicit IN_SUBJECT placements in the selected child Subject are included." if section_id
            else "No topical child Subject was selected; IN_SUBJECT placements are not included.",
            "Subject hierarchy paths reflect stored links, not independently verified authority headings.",
            "No membership is propagated through people, places, source identity matches, or narration order.",
        ],
        "summary": {
            "eventsReached": len(routes),
            "assertions": len(claims),
            "assertionsByStatus": dict(sorted(Counter(str(a["status"]) for a in claims.values()).items())),
            "broaderPaths": len(hierarchy),
        },
        "assertions": sorted(claims.values(), key=lambda claim: claim["id"]),
    }


def add_source_timeline(view: dict, report: dict) -> None:
    """Include source-attributed chronology for events already reached by the Subject view."""
    scoped = {
        event["id"]
        for assertion in view["assertions"]
        for route in assertion["routes"]
        for event in route["events"]
    }
    events = [event for event in report["events"] if event["id"] in scoped
              and event["status"] not in {"rejected", "deprecated"}]
    ids = {event["id"] for event in events}
    assertions = [
        assertion for assertion in report["assertions"]
        if assertion["status"] in {"accepted", "proposed"}
        and (
            (assertion["predicate"] == "occurred" and assertion["subjectId"] in ids
             and assertion["mode"] == "attributed")
            or (assertion["predicate"] == "happenedBefore"
                and assertion["subjectId"] in ids and assertion["objectId"] in ids
                and assertion["mode"] == "attributed")
            or (assertion["predicate"] == "depictsSameAs"
                and assertion["subjectId"] in ids and assertion["objectId"] in ids)
        )
    ]
    view["sourceTimeline"] = {
        "sources": report["sources"],
        "events": events,
        "assertions": assertions,
    }


def deduplicate_source_passages(view: dict) -> None:
    passages = {}

    def collect(items):
        for item in items:
            text = item.pop("passageText", None)
            if text:
                observation_id = item["observationId"]
                if observation_id in passages and passages[observation_id] != text:
                    raise ValueError(f"Conflicting source text for observation {observation_id}")
                passages[observation_id] = text

    for assertion in view["assertions"]:
        collect(assertion["evidence"])
        for route in assertion["routes"]:
            for placement in route["placements"]:
                collect(placement["evidence"])
            if route.get("sourceAssertion"):
                collect(route["sourceAssertion"]["evidence"])
    for event in view["sourceTimeline"]["events"]:
        collect(event["mentions"])
    for assertion in view["sourceTimeline"]["assertions"]:
        collect(assertion["evidence"])
    view["sourcePassages"] = passages


def build_with_source_timeline(tx, inquiry: dict, *, subject_id: str | None = None,
                               focus_id: str | None = None, section_id: str | None = None) -> dict:
    """The Subject view plus the source timeline; ids default to the inquiry's own."""
    view = build_view(tx, subject_id=subject_id or inquiry["subjectId"],
                      focus_id=focus_id or inquiry["narrativeEventId"], section_id=section_id)
    scoped = {
        event["id"] for assertion in view["assertions"]
        for route in assertion["routes"] for event in route["events"]
        if event["id"].startswith("chr:entity:depicted:")
    }
    known = {source["workId"] for source in inquiry["sources"]}
    additional = {}
    for row in tx.run(TIMELINE_WORKS_QUERY, ids=sorted(scoped)).data():
        if row["eventId"].startswith(depicted_event_id(row["workId"], "x")[:-1]):
            if row["workId"] not in known:
                additional[row["workId"]] = {"workId": row["workId"], "voice": row["workLabel"]}
    expanded = {**inquiry, "sources": inquiry["sources"] + list(additional.values())}
    add_source_timeline(view, build_report(tx, expanded, candidate_limit=0))
    deduplicate_source_passages(view)
    return view

