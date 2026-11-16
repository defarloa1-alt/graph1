"""Preview or submit explicitly reviewed Meaning and memory Subject placements.

The manifest is supplied by the curator. Preview is offline; --apply writes only
to the configured local neo4j database and never modifies historical assertions.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from GraphRevised.pilots.actium_meaning_memory_pilot import CHILD_ID, PHASE_ID, SUBJECT_ID
from GraphRevised.subject_backbone import local_config, require_subject_constraint

LABEL = "Meaning and memory of the Battle of Actium"


def validate_manifest(value: object) -> dict:
    if not isinstance(value, dict):
        raise ValueError("Manifest must be an object.")
    if set(value) != {"curator", "placements"}:
        raise ValueError("Manifest requires only curator and placements.")
    if not isinstance(value["curator"], str) or not value["curator"].strip():
        raise ValueError("A curator name is required.")
    rows = value["placements"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one individually selected placement is required.")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"eventId", "sourceAssertionId", "reason"}:
            raise ValueError("Every placement requires only eventId, sourceAssertionId and reason.")
        if any(not isinstance(row[key], str) or not row[key].strip() for key in row):
            raise ValueError("Placement fields must be non-empty strings.")
        if not row["eventId"].startswith("chr:entity:depicted:") or not row["sourceAssertionId"].startswith("chr:assertion:"):
            raise ValueError("Placement must name a depicted event and an existing assertion.")
        if row["eventId"] in seen:
            raise ValueError(f"Duplicate event: {row['eventId']}")
        seen.add(row["eventId"])
    return value


def submit_placements(tx, manifest: dict, submitted_at: str) -> dict:
    """Create the pilot Subject and proposed placements in one transaction."""
    validate_manifest(manifest)
    parent = tx.run(
        "MATCH (s:Subject {id: $id}) RETURN s.id AS id", id=SUBJECT_ID
    ).data()
    if len(parent) != 1:
        raise ValueError("The Actium history Subject must exist uniquely.")

    existing = tx.run(
        "MATCH (s:Subject {id: $id}) RETURN s.label AS label, s.status AS status",
        id=CHILD_ID,
    ).data()
    if len(existing) > 1 or (existing and (
        existing[0]["label"] != LABEL or existing[0]["status"] not in {"candidate", "provisional", "validated"}
    )):
        raise ValueError("The pilot Subject conflicts with an existing Subject.")
    cycle = tx.run(
        "MATCH (parent:Subject {id: $parent}) "
        "OPTIONAL MATCH (child:Subject {id: $child}) "
        "RETURN EXISTS { MATCH (parent)-[:NARROWER_THAN*1..]->(child) } AS cycle",
        parent=SUBJECT_ID, child=CHILD_ID,
    ).single(strict=True)
    if cycle["cycle"]:
        raise ValueError("The Subject hierarchy would contain a cycle.")

    for row in manifest["placements"]:
        found = tx.run(
            """MATCH (event:Entity:Event {id: $eventId})
               MATCH (a:Assertion {id: $assertionId, predicate: 'partOf'})
                     -[:ASSERTION_SUBJECT]->(event)
               MATCH (a)-[:ASSERTION_OBJECT]->(:Entity:Event {id: $phaseId})
               WHERE a.status IN ['proposed', 'accepted'] AND (
                 EXISTS {
                   MATCH (p:Proposal)-[:PROPOSES]->(a)
                   MATCH (p)-[:PROPOSES_EVIDENCE]->(:SourceObservation {status: 'observed'})
                   WHERE p.status IN ['submitted', 'validating', 'deferred', 'accepted']
                 } OR EXISTS {
                   MATCH (a)-[:SUPPORTED_BY]->(:SourceObservation {status: 'observed'})
                 }
               )
               RETURN event.status AS eventStatus, a.status AS assertionStatus""",
            eventId=row["eventId"], assertionId=row["sourceAssertionId"], phaseId=PHASE_ID,
        ).data()
        if len(found) != 1 or found[0]["eventStatus"] in {"rejected", "deprecated"}:
            raise ValueError(f"Placement source is missing, inactive, or lacks evidence: {row['eventId']}")
        prior = tx.run(
            """MATCH (:Entity {id: $eventId})-[r:IN_SUBJECT]->(:Subject {id: $subjectId})
               RETURN properties(r) AS placement""",
            eventId=row["eventId"], subjectId=CHILD_ID,
        ).data()
        if len(prior) > 1:
            raise ValueError(f"Multiple existing placements: {row['eventId']}")
        if prior:
            p = prior[0]["placement"]
            if (p.get("status"), p.get("sourceAssertionId"), p.get("reason"), p.get("proposedBy")) != (
                "proposed", row["sourceAssertionId"], row["reason"], manifest["curator"]
            ):
                raise ValueError(f"Existing placement differs or was reviewed: {row['eventId']}")

    subject = tx.run(
        """MATCH (parent:Subject {id: $parent})
           MERGE (child:Subject {id: $child})
           ON CREATE SET child.label = $label, child.status = 'candidate'
           MERGE (child)-[r:NARROWER_THAN]->(parent)
           ON CREATE SET r.reason = $reason, r.approvedBy = $curator
           RETURN child.id AS id""",
        parent=SUBJECT_ID, child=CHILD_ID, label=LABEL, curator=manifest["curator"],
        reason="Curator-selected topic within the history of the Battle of Actium.",
    ).data()
    if len(subject) != 1:
        raise RuntimeError("Pilot Subject could not be created uniquely.")
    for row in manifest["placements"]:
        result = tx.run(
            """MATCH (event:Entity:Event {id: $eventId}), (subject:Subject {id: $subjectId})
               MERGE (event)-[r:IN_SUBJECT]->(subject)
               ON CREATE SET r.status = 'proposed', r.reason = $reason,
                 r.proposedBy = $curator, r.proposedAt = $submittedAt,
                 r.sourceAssertionId = $assertionId
               RETURN r.status AS status""",
            eventId=row["eventId"], subjectId=CHILD_ID, reason=row["reason"],
            curator=manifest["curator"], submittedAt=submitted_at, assertionId=row["sourceAssertionId"],
        ).data()
        if len(result) != 1 or result[0]["status"] != "proposed":
            raise RuntimeError(f"Placement could not be submitted: {row['eventId']}")
    return {"subjectId": CHILD_ID, "proposedPlacements": len(manifest["placements"])}


def decide_placement(tx, event_id: str, decision: str, curator: str, basis: str, decided_at: str) -> dict:
    """Decide one proposed topical placement; terminal decisions are not overwritten."""
    if decision not in {"accepted", "rejected"}:
        raise ValueError("Decision must be accepted or rejected.")
    if not event_id.startswith("chr:entity:depicted:") or not curator.strip() or not basis.strip():
        raise ValueError("A depicted event, curator and decision basis are required.")
    rows = tx.run(
        """MATCH (event:Entity:Event {id: $eventId})-[r:IN_SUBJECT]->(s:Subject {id: $subjectId})
           WHERE r.status = 'proposed' AND ($decision = 'rejected' OR (
             NOT event.status IN ['deprecated', 'rejected'] AND EXISTS {
               MATCH (a:Assertion {id: r.sourceAssertionId, predicate: 'partOf'})
                     -[:ASSERTION_SUBJECT]->(event)
               MATCH (a)-[:ASSERTION_OBJECT]->(:Entity:Event {id: $phaseId})
               WHERE a.status IN ['proposed', 'accepted'] AND (
                 EXISTS { MATCH (a)-[:SUPPORTED_BY]->(:SourceObservation {status: 'observed'}) }
                 OR EXISTS {
                   MATCH (p:Proposal)-[:PROPOSES]->(a)
                   MATCH (p)-[:PROPOSES_EVIDENCE]->(:SourceObservation {status: 'observed'})
                   WHERE p.status IN ['submitted', 'validating', 'deferred', 'accepted']
                 }
               )
             }
           ))
           SET r.status = $decision, r.decidedBy = $curator,
               r.decisionBasis = $basis, r.decidedAt = $decidedAt
           RETURN r.status AS status, r.sourceAssertionId AS sourceAssertionId""",
        eventId=event_id, subjectId=CHILD_ID, phaseId=PHASE_ID,
        decision=decision, curator=curator, basis=basis, decidedAt=decided_at,
    ).data()
    if len(rows) != 1:
        raise ValueError("Placement is absent, already decided, or cannot be accepted with its current source evidence.")
    return rows[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    submit = sub.add_parser("submit", help="Preview or submit individual curator-selected placements")
    submit.add_argument("manifest", type=Path)
    submit.add_argument("--apply", action="store_true", help="write the reviewed manifest to local Neo4j")
    decide = sub.add_parser("decide", help="Preview or decide one previously proposed placement")
    decide.add_argument("event_id")
    decide.add_argument("--decision", choices=("accepted", "rejected"), required=True)
    decide.add_argument("--by", required=True)
    decide.add_argument("--basis", required=True)
    decide.add_argument("--apply", action="store_true", help="write this decision to local Neo4j")
    args = parser.parse_args(argv)
    try:
        if args.action == "submit":
            manifest = validate_manifest(json.loads(args.manifest.read_text(encoding="utf-8")))
            print(f"Curator: {manifest['curator']}; individually selected placements: {len(manifest['placements'])}")
            for row in manifest["placements"]:
                print(f"  {row['eventId']} <- {row['sourceAssertionId']}: {row['reason']}")
        else:
            if not args.event_id.startswith("chr:entity:depicted:") or not args.by.strip() or not args.basis.strip():
                raise ValueError("A depicted event, curator and decision basis are required.")
            print(f"Decision: {args.decision}; event: {args.event_id}; by: {args.by}; basis: {args.basis}")
        if not args.apply:
            print("Offline preview only; no database connection or graph writes.")
            return 0
        from neo4j import GraphDatabase

        config = local_config()
        print(f"Target: {config['uri']}, database {config['database']}")
        now = datetime.now(timezone.utc).isoformat()
        with GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"])) as driver:
            with driver.session(database=config["database"]) as session:
                require_subject_constraint(session)
                if args.action == "submit":
                    result = session.execute_write(submit_placements, manifest, now)
                else:
                    result = session.execute_write(decide_placement, args.event_id, args.decision, args.by, args.basis, now)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Pilot operation refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
