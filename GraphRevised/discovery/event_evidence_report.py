"""Read-only report of an event inquiry's depictions, evidence and chronology.

    python -m GraphRevised.discovery.event_evidence_report inquiries/<inquiry>.json --output report.json

An inquiry may list ``leadStopwords``: words too common in its sources (the main
actors, the place) to count as shared terms between two depicted events.

The candidate pairs are lexical leads for human review, never identity claims.
The report includes proposed and rejected data with their statuses; it does not
infer dates, chronology, or relationships from source order or phase placement.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

from neo4j import GraphDatabase

from GraphRevised.proposals.entities import depicted_event_id
from GraphRevised.discovery.source_text import include_source_text
from GraphRevised.subject_backbone import local_config

STOPWORDS = frozenset({
    "after", "battle", "before", "during", "fleet", "from", "into", "roman", "ships",
    "their", "they", "with",
})

EVENTS_QUERY = """
MATCH (event:Entity:Event)
WHERE any(prefix IN $prefixes WHERE event.id STARTS WITH prefix)
RETURN event.id AS id, event.label AS label, event.shortLabel AS shortLabel, event.status AS status
ORDER BY id
"""

MENTIONS_QUERY = """
MATCH (event:Entity:Event)<-[:CONCERNS]-(annotation:Annotation {kind: 'entity-mention'})
      -[:ANNOTATES]->(observation:SourceObservation)-[:IN_WORK]->(work:Entity:Work)
WHERE event.id IN $ids
RETURN DISTINCT event.id AS eventId, annotation.id AS annotationId, annotation.status AS annotationStatus,
       observation.id AS observationId, observation.label AS passage, observation.locator AS locator,
       observation.status AS observationStatus, work.id AS workId, work.label AS work,
       observation.passageText AS passageText, observation.editionCitation AS editionCitation,
       observation.rights AS rights, observation.sourceSystem AS sourceSystem
ORDER BY eventId, workId, observationId, annotationId
"""

ASSERTIONS_QUERY = """
MATCH (assertion:Assertion)-[:ASSERTION_SUBJECT]->(subject:Entity)
WHERE assertion.predicate IN $predicates
OPTIONAL MATCH (assertion)-[:ASSERTION_OBJECT]->(object:Entity)
WITH assertion, subject, object
WHERE subject.id IN $ids OR object.id IN $ids
OPTIONAL MATCH (assertion)-[:ATTRIBUTED_TO]->(work:Entity:Work)
OPTIONAL MATCH (assertion)-[:ASSERTION_CONTEXT]->(context:Entity)
RETURN assertion.id AS id, assertion.predicate AS predicate, assertion.status AS status,
       assertion.mode AS mode, assertion.label AS label,
       subject.id AS subjectId, subject.label AS subjectLabel,
       object.id AS objectId, object.label AS objectLabel,
       work.id AS workId, work.label AS work, context.id AS contextId,
       assertion.timeSourceExpression AS timeExpression, assertion.timeEdtf AS timeEdtf,
       assertion.timeRelativeOffset AS relativeOffset, assertion.timePrecision AS timePrecision,
       assertion.startEarliestJdn AS startEarliestJdn, assertion.startLatestJdn AS startLatestJdn,
       assertion.endEarliestJdn AS endEarliestJdn, assertion.endLatestJdn AS endLatestJdn
ORDER BY id
"""

EVIDENCE_QUERY = """
MATCH (assertion:Assertion) WHERE assertion.id IN $ids
CALL (assertion) {
  MATCH (assertion)-[link:SUPPORTED_BY]->(observation:SourceObservation)
  RETURN observation, 'supported' AS evidenceState, null AS proposalId, null AS proposalStatus, link.quotation AS quotation
  UNION ALL
  MATCH (proposal:Proposal)-[:PROPOSES]->(assertion)
        MATCH (proposal)-[link:PROPOSES_EVIDENCE]->(observation:SourceObservation)
  RETURN observation, 'proposal' AS evidenceState, proposal.id AS proposalId, proposal.status AS proposalStatus, link.quotation AS quotation
}
OPTIONAL MATCH (observation)-[:IN_WORK]->(work:Entity:Work)
RETURN DISTINCT assertion.id AS assertionId, observation.id AS observationId, observation.label AS passage,
       observation.locator AS locator, observation.status AS observationStatus, work.id AS workId,
       work.label AS work, evidenceState, proposalId, proposalStatus, quotation,
       observation.passageText AS passageText, observation.editionCitation AS editionCitation,
       observation.rights AS rights, observation.sourceSystem AS sourceSystem
ORDER BY assertionId, evidenceState, observationId
"""


def lexical_tokens(label: str, stopwords: frozenset[str] = frozenset()) -> set[str]:
    words = re.findall(r"[a-z0-9]+", label.lower())
    return {word for word in words if len(word) >= 4 and word not in STOPWORDS and word not in stopwords}


def candidates(events: list[dict], limit: int = 30,
               stopwords: frozenset[str] = frozenset()) -> tuple[list[dict], int]:
    """Produce bounded, explainable lexical leads; not identity determinations."""
    pairs = []
    usable = [e for e in events if e["status"] not in {"deprecated", "rejected"} and e.get("sourceWorkId")]
    for i, left in enumerate(usable):
        a = lexical_tokens(left.get("shortLabel") or left.get("label") or "", stopwords)
        for right in usable[i + 1:]:
            if left["sourceWorkId"] == right["sourceWorkId"]:
                continue
            b = lexical_tokens(right.get("shortLabel") or right.get("label") or "", stopwords)
            overlap = a & b
            if len(overlap) < 2:
                continue
            score = 2 * len(overlap) / (len(a) + len(b))
            if score < 0.6:
                continue
            pairs.append({
                "leftId": left["id"], "leftLabel": left["label"], "leftWorkId": left["sourceWorkId"],
                "rightId": right["id"], "rightLabel": right["label"], "rightWorkId": right["sourceWorkId"],
                "sharedTerms": sorted(overlap), "lexicalScore": round(score, 3),
                "reviewStatus": "unreviewed",
            })
    pairs.sort(key=lambda pair: (-pair["lexicalScore"], pair["leftId"], pair["rightId"]))
    return pairs[:limit], len(pairs)


def build_report(tx, inquiry: dict, candidate_limit: int = 30) -> dict:
    sources = inquiry["sources"]
    prefixes = {depicted_event_id(source["workId"], "x")[:-1]: source["workId"] for source in sources}
    if len(prefixes) != len(sources):
        raise ValueError("Inquiry contains duplicate source work IDs.")
    events = tx.run(EVENTS_QUERY, prefixes=list(prefixes)).data()
    ids = [event["id"] for event in events]
    for event in events:
        matched = [work for prefix, work in prefixes.items() if event["id"].startswith(prefix)]
        if len(matched) != 1:
            raise ValueError(f"Depicted event has ambiguous source prefix: {event['id']}")
        event["sourceWorkId"] = matched[0]
        event["mentions"] = []

    event_by_id = {event["id"]: event for event in events}
    for mention in tx.run(MENTIONS_QUERY, ids=ids).data():
        event_by_id[mention["eventId"]]["mentions"].append(include_source_text(mention))

    focus = inquiry["narrativeEventId"]
    phase_prefix = f"chr:entity:phase:{focus.split(':', 2)[2]}:"
    phases = tx.run(
        "MATCH (e:Entity:Event) WHERE e.id STARTS WITH $prefix "
        "RETURN e.id AS id, e.label AS label, e.status AS status ORDER BY id",
        prefix=phase_prefix,
    ).data()
    scoped_ids = ids + [focus] + [phase["id"] for phase in phases]
    predicates = ["partOf", "occurred", "happenedBefore", "triggeredBy", "resultedIn", "depictsSameAs"]
    assertions = tx.run(ASSERTIONS_QUERY, predicates=predicates, ids=scoped_ids).data()
    by_id = {}
    for assertion in assertions:
        if assertion["id"] in by_id:
            raise ValueError(f"Assertion has multiple endpoint, context, or attribution rows: {assertion['id']}")
        assertion["evidence"] = []
        by_id[assertion["id"]] = assertion
    for item in tx.run(EVIDENCE_QUERY, ids=list(by_id)).data():
        by_id[item["assertionId"]]["evidence"].append(include_source_text(item))

    stopwords = frozenset(word.lower() for word in inquiry.get("leadStopwords", []))
    leads, total = candidates(events, candidate_limit, stopwords)
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "inquiryId": inquiry["id"],
        "focusId": focus,
        "scope": "Depicted event IDs for inquiry source works, not proof that each belongs to the battle.",
        "limitations": [
            "All statuses are shown; proposed and rejected assertions are not accepted facts.",
            "Proposal evidence is labeled separately from support; check each proposal status.",
            "Passage mentions are annotations, not proof of event identity or chronology.",
            "Candidate pairs are lexical leads only and can be wrong; review passages and context.",
            "Phase order, derived dates, and causal or temporal inferences are not generated.",
        ],
        "summary": {
            "events": len(events),
            "eventsByStatus": dict(sorted(Counter(str(event["status"]) for event in events).items())),
            "eventsWithoutMentions": sum(not event["mentions"] for event in events),
            "phases": len(phases),
            "assertionsByPredicateAndStatus": [
                {"predicate": predicate, "status": status, "count": count}
                for (predicate, status), count in sorted(
                    Counter((str(a["predicate"]), str(a["status"])) for a in assertions).items()
                )
            ],
            "candidatePairsReturned": len(leads),
            "candidatePairsMatchingHeuristic": total,
        },
        "sources": [{"workId": s["workId"], "voice": s.get("voice")} for s in sources],
        "events": events,
        "phases": phases,
        "assertions": assertions,
        "alignmentCandidates": leads,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inquiry", type=Path, help="Existing event inquiry JSON")
    parser.add_argument("--output", type=Path, required=True, help="New JSON report path; existing files are not overwritten")
    parser.add_argument("--candidate-limit", type=int, default=30)
    args = parser.parse_args(argv)
    if args.candidate_limit < 0:
        parser.error("--candidate-limit must be non-negative")
    try:
        inquiry = json.loads(args.inquiry.read_text(encoding="utf-8"))
        config = local_config()
        with GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"])) as driver:
            with driver.session(database=config["database"], default_access_mode="READ") as session:
                report = session.execute_read(build_report, inquiry, args.candidate_limit)
        with args.output.open("x", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print(f"Report written to {args.output}")
        print(json.dumps(report["summary"], indent=2))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"Report failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
