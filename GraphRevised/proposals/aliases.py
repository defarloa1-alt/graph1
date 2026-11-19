"""Aliases for a person, suggested by reasoning and decided by the curator (46 §4.5, 2026-11-19).

    python -m GraphRevised.proposals.aliases suggest <entity-id> [--apply]
    python -m GraphRevised.proposals.aliases list [--status submitted]
    python -m GraphRevised.proposals.aliases accept|reject <proposal-id> --by <name> --basis "<reason>" [--reason <code>]

The one label stays; the other names a person is found by are proposed as `addAlias` Proposals,
each with its reason, and only the curator accepts one (it then joins `alternativeNames`, which
name search reads). The suggester reasons in three steps:

1. **Forms by convention** from the Person's name parts (praenomen, nomen, cognomen, agnomen):
   the abbreviated praenomen with the rest ("L. Pinarius Scarpus"), nomen and cognomen ("Pinarius
   Scarpus"), the cognomen alone ("Scarpus"), praenomen and nomen ("Lucius Pinarius").
2. **Attestation**: each form is looked for in the passages we hold about the person (the evidence
   of claims naming them, and their mentions). Found, the alias is `attested` and quotes the
   passage; otherwise it is `convention`.
3. **Guards**: a form another entity already bears (label, short label, alias) is proposed with
   that entity named in `sharedWith`, never silently; and a form borne by an entity that shares an
   open Question with this one (both `about` it) is not proposed at all, since an alias must never
   settle an identity Question.

The name parts come from the Person, or, when it has none, from a source's entry heading in
Roman order ("Scarpus, L. Pinarius" is cognomen, praenomen, nomen), passed with --heading.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any

from GraphRevised.operations import run_write

from .store import REASON_CODES, ReviewError

# The standard abbreviations of the Roman praenomina.
PRAENOMINA = {
    "Aulus": "A.", "Appius": "Ap.", "Gaius": "C.", "Gnaeus": "Cn.", "Decimus": "D.", "Lucius": "L.",
    "Marcus": "M.", "Manius": "M'.", "Numerius": "N.", "Publius": "P.", "Quintus": "Q.", "Servius": "Ser.",
    "Sextus": "Sex.", "Spurius": "Sp.", "Titus": "T.", "Tiberius": "Ti.",
}
ABBREVIATIONS = {abbreviation: name for name, abbreviation in PRAENOMINA.items()}

PERSON = """
MATCH (e:Entity:Person {id: $id})
RETURN e.label AS label, e.shortLabel AS shortLabel, coalesce(e.alternativeNames, []) AS aliases,
       e.praenomen AS praenomen, e.nomen AS nomen, e.cognomen AS cognomen, e.agnomen AS agnomen
"""
PASSAGES = """
MATCH (e:Entity {id: $id})
CALL (e) {
  MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(e) WHERE a.status IN ['proposed', 'accepted']
  MATCH (a)-[:SUPPORTED_BY]->(o:SourceObservation) RETURN o
  UNION
  MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(e) WHERE a.status IN ['proposed', 'accepted']
  MATCH (p:Proposal)-[:PROPOSES]->(a) MATCH (p)-[:PROPOSES_EVIDENCE]->(o:SourceObservation)
  RETURN o
  UNION
  MATCH (n:Annotation)-[:CONCERNS]->(e) MATCH (n)-[:ANNOTATES]->(o:SourceObservation) RETURN o
}
RETURN DISTINCT o.id AS id, o.passageText AS text ORDER BY id
"""
BEARERS = """
MATCH (other:Entity) WHERE other.id <> $id AND NOT other.status IN ['deprecated', 'rejected']
  AND any(n IN [other.label, other.shortLabel] + coalesce(other.alternativeNames, []) WHERE toLower(n) = toLower($alias))
RETURN other.id AS id, other.label AS label,
       EXISTS {
         MATCH (q:Entity:Question)<-[:ASSERTION_SUBJECT]-(a1:Assertion {predicate: 'about'})-[:ASSERTION_OBJECT]->(:Entity {id: $id})
         WHERE a1.status IN ['proposed', 'accepted']
         MATCH (q)<-[:ASSERTION_SUBJECT]-(a2:Assertion {predicate: 'about'})-[:ASSERTION_OBJECT]->(other)
         WHERE a2.status IN ['proposed', 'accepted']
       } AS sharesQuestion
ORDER BY id
"""


def parts_from_heading(heading: str) -> dict[str, str | None]:
    """'Scarpus, L. Pinarius' (a dictionary heading: cognomen, then praenomen and nomen) to name parts."""
    cognomen, _, rest = (piece.strip() for piece in heading.replace("'", "").partition(","))
    words = rest.split()
    praenomen = ABBREVIATIONS.get(words[0]) if words else None
    if praenomen is None or len(words) < 2:
        raise ValueError(f"not a heading of the form 'Cognomen, P. Nomen': {heading!r}")
    title = lambda w: w[:1].upper() + w[1:].lower()  # noqa: E731  ("PINARIUS" in a capitalized heading)
    return {"praenomen": praenomen, "nomen": title(words[1]), "cognomen": title(cognomen), "agnomen": None}


def conventional_forms(parts: dict[str, str | None]) -> list[tuple[str, str]]:
    """(form, the convention it follows), most specific first."""
    p, n, c, a = (parts.get(k) for k in ("praenomen", "nomen", "cognomen", "agnomen"))
    forms = []
    if p and n:
        tail = " ".join(x for x in (n, c, a) if x)
        if p in PRAENOMINA:
            forms.append((f"{PRAENOMINA[p]} {tail}", "the praenomen abbreviated, as inscriptions, coins and "
                                                   "modern reference works write it"))
    if n and c:
        forms.append((f"{n} {c}", "nomen and cognomen, the form ancient historians use"))
    if c:
        forms.append((c, "the cognomen alone, as a narrative names a man once introduced"))
    if p and n:
        forms.append((f"{p} {n}", "praenomen and nomen"))
    if a:
        forms.append((a, "the agnomen alone"))
    return forms


def _attestation(form: str, passages: list[dict[str, Any]]) -> tuple[str, str] | None:
    pattern = re.compile(rf"(?<!\w){re.escape(form)}(?!\w)", re.I)
    for passage in passages:
        text = passage["text"] or ""
        match = pattern.search(text)
        if match:
            start, end = max(0, match.start() - 40), min(len(text), match.end() + 40)
            return passage["id"], text[start:end].strip()
    return None


def suggest(tx: Any, entity_id: str, heading: str | None = None) -> list[dict[str, Any]]:
    """The aliases worth proposing for a Person, each with its kind, reason, evidence and guards."""
    person = tx.run(PERSON, id=entity_id).single()
    if person is None:
        raise ReviewError(f"{entity_id} is not a Person")
    parts = dict(person)
    if heading:
        parts.update(parts_from_heading(heading))
    known = {name.lower() for name in [person["label"], person["shortLabel"], *person["aliases"]] if name}
    passages = tx.run(PASSAGES, id=entity_id).data()
    out = []
    forms = conventional_forms(parts)
    # Coins and inscriptions write capitals with V for U (SCARPVS): a distinct form, proposed only when attested.
    epigraphic = [(f.upper().replace("U", "V"), "the form coins and inscriptions write, in capitals with V for U")
                  for f, _ in forms if f.upper().replace("U", "V") != f.upper()]
    for form, convention in forms + epigraphic:
        if (form, convention) in epigraphic and _attestation(form, passages) is None:
            continue
        if form.lower() in known:
            continue
        bearers = tx.run(BEARERS, id=entity_id, alias=form).data()
        blocking = [b for b in bearers if b["sharesQuestion"]]
        found = _attestation(form, passages)
        item = {"alias": form, "convention": convention, "sharedWith": [b["id"] for b in bearers],
                "kind": "attested" if found else "convention", "evidence": found}
        if blocking:
            item["refused"] = (f"{', '.join(b['label'] for b in blocking)} also bears this name and shares an open "
                               f"Question with this person: an alias must not settle it")
        out.append(item)
    return out


def propose(tx: Any, operations: dict[str, str], registry_version: str, entity_id: str, item: dict[str, Any], *,
            proposed_by: str, at: str) -> dict[str, Any]:
    """Store one suggestion as an `addAlias` Proposal (refused suggestions are never stored)."""
    if item.get("refused"):
        raise ReviewError(item["refused"])
    reason = f"By convention: {item['convention']}."
    if item["evidence"]:
        reason += f" Attested in a passage we hold: \"{item['evidence'][1]}\"."
    if item["sharedWith"]:
        reason += f" Also borne by: {', '.join(item['sharedWith'])}."
    digest = hashlib.sha256(f"{entity_id}|{item['alias']}".encode("utf-8")).hexdigest()[:12]
    return run_write(tx, operations, "upsert_alias_proposal", {
        "id": f"chr:proposal:alias:{entity_id.split(':', 2)[2]}:{digest}", "entityId": entity_id,
        "alias": item["alias"], "aliasKind": item["kind"], "sharedWith": item["sharedWith"],
        "label": f"Proposal to add alias: {item['alias']}", "shortLabel": f"+alias: {item['alias']}",
        "rationale": reason, "createdBy": proposed_by, "createdAt": at,
        "draftSchemaVersion": "alias-1", "predicateRegistryVersion": registry_version,
        "observationId": item["evidence"][0] if item["evidence"] else None,
        "quotation": item["evidence"][1] if item["evidence"] else None,
    })[0]["proposal"]


def decide(tx: Any, operations: dict[str, str], proposal_id: str, status: str, *, decided_by: str,
           decision_basis: str, decided_at: str, reason: str | None = None) -> dict[str, Any]:
    """Accept (the alias joins alternativeNames) or reject (with a reason code) an alias Proposal."""
    if status == "rejected" and reason not in REASON_CODES:
        raise ReviewError(f"reason must be one of {list(REASON_CODES)}, not {reason!r}")
    rows = tx.run(operations["decide_alias_proposal"], {
        "proposalId": proposal_id, "status": status, "decidedAt": decided_at, "decidedBy": decided_by,
        "decisionBasis": decision_basis, "reason": reason}).data()
    if not rows:
        raise ReviewError(f"{proposal_id} is not an open alias proposal")
    return rows[0]


def list_alias_proposals(tx: Any, status: str | None = "submitted") -> list[dict[str, Any]]:
    return tx.run("""
        MATCH (p:Proposal {operation: 'addAlias'})-[:PROPOSES_ALIAS]->(e:Entity)
        WHERE $status IS NULL OR p.status = $status
        OPTIONAL MATCH (p)-[ev:PROPOSES_EVIDENCE]->(o:SourceObservation)
        RETURN p.id AS id, p.status AS status, e.label AS entity, p.alias AS alias, p.aliasKind AS kind,
               p.sharedWith AS sharedWith, p.rationale AS rationale, o.label AS evidence, ev.quotation AS quotation
        ORDER BY entity, alias""", status=status).data()


def main(argv: list[str] | None = None) -> int:
    from neo4j import GraphDatabase

    from GraphRevised.operations import load_operations

    from .registry import load_registry

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    s = commands.add_parser("suggest")
    s.add_argument("entity_id")
    s.add_argument("--heading", help="a source's entry heading, when the Person has no name parts")
    s.add_argument("--by", default="alias suggester (rule, 46 §4.5)")
    s.add_argument("--apply", action="store_true")
    ls = commands.add_parser("list")
    ls.add_argument("--status", default="submitted")
    for name in ("accept", "reject"):
        d = commands.add_parser(name)
        d.add_argument("proposal_id")
        d.add_argument("--by", required=True)
        d.add_argument("--basis", required=True)
        if name == "reject":
            d.add_argument("--reason", required=True, choices=REASON_CODES)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                operations = load_operations()
                if args.command == "suggest":
                    items = suggest(tx, args.entity_id, args.heading)
                    for item in items:
                        if not item.get("refused"):
                            item["proposal"] = propose(tx, operations, load_registry().version, args.entity_id, item,
                                                       proposed_by=args.by, at=at)["id"]
                    report: Any = items
                    commit = args.apply
                elif args.command == "list":
                    report, commit = list_alias_proposals(tx, args.status or None), False
                else:
                    report = decide(tx, operations, args.proposal_id,
                                    "accepted" if args.command == "accept" else "rejected", decided_by=args.by,
                                    decision_basis=args.basis, decided_at=at, reason=getattr(args, "reason", None))
                    report, commit = {"proposal": report["proposal"]["id"], "status": report["proposal"]["status"],
                                      "alternativeNames": report["entity"].get("alternativeNames")}, True
                tx.commit() if commit else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    if args.command == "suggest":
        print("applied" if args.apply else "dry run, rolled back")
    print(json.dumps(report, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
