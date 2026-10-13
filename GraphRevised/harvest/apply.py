"""First-contact harvest, increment 2: write what the report shows (25-LIVES-AND-PLAYGROUND.md sections 10-11).

    python -m GraphRevised.harvest.apply <QID> [--apply]

Without --apply, everything runs in one transaction that is rolled back, and
the outcome is reported. With --apply the transaction commits. Steps:

1. The focus must already be a local Entity with an accepted Wikidata
   identity: choosing whom to harvest is the curator's (or the agent's) call.
2. Its preserved Wikidata record is classed (wikidata_harvest.classify).
3. Each target of a mapped relationship is met once: its record is preserved
   (first contact) and its kind read from its "instance of" classes by the
   rules' kind table. A target with a known kind becomes a proposed Entity
   with its Wikidata identity (an Entity already holding that QID is reused);
   one whose classes the table does not cover waits for the agent's judgement.
4. Each mapped statement and each dated one (born, died) becomes a statement
   observation, with its time and other qualifiers recorded, and is proposed
   through the deterministic proposer and the validator: proposed claims
   "according to Wikidata", never accepted.
5. The focus's identifiers in federations we use become AuthorityRecords
   (role crosswalk); the rest stay readable in the preserved record.

Unmapped relationships (gens, partners, relatives, allegiance...) are
reported and wait for predicates. Nothing here accepts anything.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_statements import statement_observation
from GraphRevised.harvest.wikidata_harvest import Labels, Statement, classify, load_rules
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import PredicateRegistry, load_registry
from GraphRevised.proposals.store import Neo4jReader, submit
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.slices.add_entity import persist_identity, preserved_identity_payload

TIME_FIELDS = ("statementTimeEdtf", "statementTimeCalendar", "statementTimeMode", "statementTimeDisplay",
               "statementQualifiers")


class HarvestError(RuntimeError):
    """The harvest cannot start (no local focus with an accepted identity)."""


def kind_of(entity: dict[str, Any], rules: dict[str, Any]) -> str | None:
    """The kind an entity's "instance of" classes give by the rules' table, or None for the agent."""
    classes = {c["mainsnak"].get("datavalue", {}).get("value", {}).get("id")
               for c in entity.get("claims", {}).get("P31", []) if c.get("rank") != "deprecated"}
    for kind in rules["kindPriority"]:
        if classes & set(rules["kinds"].get(kind, [])):
            return kind
    return None


def _slug(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or "unnamed"


def surface(tx: Any, operations: dict[str, str], qid: str, rules: dict[str, Any]) -> dict[str, Any]:
    """Meet a target once: reuse the local Entity holding its QID, or propose one if its kind is known."""
    local = Neo4jReader(tx).entity_ids_for_wikidata(qid)
    if len(local) == 1:
        return {"qid": qid, "entityId": local[0], "state": "in the graph"}
    if len(local) > 1:
        return {"qid": qid, "entityId": None, "state": f"{len(local)} local Entities hold this QID: curator"}
    path, metadata = preserved_identity_payload(qid)
    entity = json.loads(path.read_bytes())["entities"][qid]
    kind = kind_of(entity, rules)
    if kind is None:
        return {"qid": qid, "entityId": None, "state": "kind unknown: waits for the agent", "label": metadata["entityLabel"]}
    entity_id = f"chr:entity:{_slug(metadata['entityLabel'])}"
    taken = tx.run("MATCH (e:Entity {id: $id}) RETURN count(e) AS n", id=entity_id).single()["n"]
    if taken:
        entity_id = f"{entity_id}-{qid.lower()}"
    persist_identity(tx, operations, entity_id=entity_id, kind=kind, payload_path=path, metadata=metadata,
                     status="proposed")
    return {"qid": qid, "entityId": entity_id, "state": f"proposed {kind}", "label": metadata["entityLabel"]}


def propose_statement(tx: Any, operations: dict[str, str], registry: PredicateRegistry, path, statement: Statement,
                      focus_label: str, labels: Labels) -> list[tuple[str, str, tuple[str, ...]]]:
    """Record one Wikidata statement as an observation and propose what it states."""
    target = labels.label(statement.value) if isinstance(statement.value, str) else "a date"
    observation = statement_observation(
        path, statement.statement_id,
        label=f"Wikidata observation: {focus_label} {labels.label(statement.pid)} {target}",
        short_label=f"Wikidata: {focus_label} {labels.label(statement.pid)} -> {target}")
    run_write(tx, operations, "upsert_observation", observation)
    run_write(tx, operations, "record_statement_time", {"id": observation["id"]} | {k: observation[k] for k in TIME_FIELDS})
    reader = Neo4jReader(tx)
    proposed = drafts_from_observation(reader.observation(observation["id"]), reader, registry)
    results = []
    for draft in proposed.drafts:
        validation = submit(tx, draft, registry, operations).validation
        results.append((validation.outcome.value, draft.predicate, validation.reasons))
    if proposed.unresolved:
        results.append(("unresolved", statement.pid, proposed.unresolved))
    return results


def harvest(tx: Any, qid: str, operations: dict[str, str], registry: PredicateRegistry,
            rules: dict[str, Any]) -> dict[str, Any]:
    reader = Neo4jReader(tx)
    focus_ids = reader.entity_ids_for_wikidata(qid)
    if len(focus_ids) != 1:
        raise HarvestError(f"{qid} needs exactly one local Entity with an accepted identity, not {len(focus_ids)}")
    focus = reader.entity(focus_ids[0])
    path, metadata = preserved_identity_payload(qid)
    entity = json.loads(path.read_bytes())["entities"][qid]
    statements, deprecated = classify(entity, rules, registry)
    labels = Labels()
    labels.resolve({s.pid for s in statements} | {s.value for s in statements if isinstance(s.value, str)
                                                    and s.value[:1] == "Q" and s.datatype.startswith("wikibase")})

    mapped = [s for s in statements if s.kind == "relationship" and s.predicates]
    dated = [s for s in statements if s.kind == "dated" and registry.for_wikidata(s.pid)]
    surfaced = {qid_: surface(tx, operations, qid_, rules) for qid_ in sorted({s.value for s in mapped})}
    claims: list[tuple[str, str, tuple[str, ...]]] = []
    for statement in mapped + dated:
        if statement.problems:
            claims.append(("skipped", statement.pid, tuple(statement.problems)))
            continue
        claims.extend(propose_statement(tx, operations, registry, path, statement, focus["label"], labels))

    crosswalk = []
    for statement in statements:
        system = rules["federations"].get(statement.pid)
        if statement.kind != "identifier" or system is None or not isinstance(statement.value, str):
            continue
        run_write(tx, operations, "upsert_authority", {
            "entityId": focus["id"], "id": f"chr:authority:{_slug(system)}:{_slug(statement.value)}",
            "system": system, "identifier": statement.value,
            "label": f"{focus['label']} in {system} ({system} {statement.value})",
            "shortLabel": f"{system}: {focus['label']}", "description": None,
            "retrievedAt": metadata["retrievedAt"], "sourceUri": metadata["sourceUri"],
            "sourceRevision": metadata["revision"], "contentHash": metadata["contentHash"],
            "rawPayloadUri": path.resolve().relative_to(path.resolve().parents[2]).as_posix(),
            "role": "crosswalk", "relation": "closeMatch", "linkStatus": "accepted",
        })
        crosswalk.append(f"{system} {statement.value}")

    unmapped = [s for s in statements if s.kind == "relationship" and not s.predicates]
    return {
        "focus": f"{focus['label']} ({qid})",
        "statements": len(statements), "deprecated": deprecated,
        "surfaced": surfaced,
        "claims": claims,
        "crosswalk": crosswalk,
        "unmapped": [f"{labels.label(s.pid)} ({s.pid}) -> {labels.show(s.value) if isinstance(s.value, str) else s.value}"
                     for s in unmapped],
    }


def summary(result: dict[str, Any]) -> str:
    states = Counter(item["state"].split(":")[0] for item in result["surfaced"].values())
    outcomes = Counter(outcome for outcome, _, _ in result["claims"])
    lines = [f"Harvest of {result['focus']}: {result['statements']} statements ({result['deprecated']} deprecated left out)",
             "Surfaced entities: " + ", ".join(f"{n} {s}" for s, n in states.most_common()),
             "Claims: " + ", ".join(f"{n} {o}" for o, n in outcomes.most_common()),
             f"Crosswalk: {len(result['crosswalk'])} ({', '.join(result['crosswalk'])})",
             f"Unmapped relationships waiting for predicates: {len(result['unmapped'])}"]
    waiting = [f"  {item.get('label', item['qid'])} ({item['qid']}): {item['state']}"
               for item in result["surfaced"].values() if item["entityId"] is None]
    if waiting:
        lines += ["Waiting:"] + waiting
    refused = [f"  {o} {p}: {'; '.join(r)}" for o, p, r in result["claims"] if o not in ("valid", "adds_evidence", "duplicate")]
    if refused:
        lines += ["Not stored:"] + refused
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("qid")
    parser.add_argument("--apply", action="store_true", help="commit; without it the transaction is rolled back")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                result = harvest(tx, args.qid, load_operations(), load_registry(), load_rules())
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("APPLIED. " if args.apply else "DRY RUN (rolled back). ") + summary(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
