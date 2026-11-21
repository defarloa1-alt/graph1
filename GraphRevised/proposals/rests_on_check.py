"""Check the rests-on links that code made from Wikipedia footnotes (D-169, 47 §3.1).

    python -m GraphRevised.proposals.rests_on_check check [--claim <id>] [--max-links N] [--read [--apply]]
    python -m GraphRevised.proposals.rests_on_check list [--status submitted|accepted|rejected|all]
    python -m GraphRevised.proposals.rests_on_check decide <proposal id> accept|reject [--reason <code>] --by "<name>"

`harvest/wikipedia_footnotes.py` links a modern claim to every passage in the range its footnote
cites (a citation of chapters 65-66 links it to each section of 65 and 66 we hold). Where the footnote
sits, and how wide its range is, are guesses about what it supports, and these links count for
attestation (D-148). Here a model reads each claim beside all the passages it was linked to, one call
per claim, and judges each passage: it states the claim, states part of it, or does not say it. For
the first two it copies the passage's own words that carry it, and code checks those words verbatim.

Each claim's check is stored as a `checkRestsOn` Proposal (CHECKS_CLAIM, CHECKS_PASSAGE), signed with
the model and prompt version. When every link is confirmed in verified words, the check is accepted by
rule and the links keep their acceptance (D-169). Otherwise it waits for the curator: accepting it
applies the verdicts (a link whose passage does not state the claim is rejected and kept as history,
one that states part of it is marked partial) and rebuilds the fact layer; rejecting it leaves every
link as it was.

`check` is a dry run by default: it builds each request and prices its worst case; nothing is called.
`--read` calls the model (paid: needs CHRYSTALLUM_BUDGET and the curator's go-ahead; `--run-cap`
stops the run at that many dollars); without `--apply` the checks are validated and rolled back.
Claims already checked are skipped, so a run can be resumed. `--recheck` checks again a claim whose
open checks were all made with another prompt version; the new check supersedes them (rejected,
`superseded-by-model`, kept as history). Only live claims are checked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from GraphRevised import localdb
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.passage_reader import RUNS_DIRECTORY
from GraphRevised.proposals.prompt_version import prompt_version
from GraphRevised.proposals.store import REASON_CODES, ReviewError
from GraphRevised.spend_meter import ceiling

MODEL = "claude-sonnet-5-5"  # the curator's authorization for the first run (D-169)
CHECKER = "rests-on-checker"
HARVEST = "wikipedia-footnote-harvest-v1"
SCHEMA = "rests-on-check-1"
RULE_BY = "rule: D-169 rests-on check, every link confirmed"
RULE_BASIS = ("Accepted by rule (D-169): the check found each linked passage states the claim, in words "
              "verified in the passage; the links keep their acceptance by rule (D-145).")
MAX_TOKENS = 8000
CURATION = Path(__file__).resolve().parents[1] / "curation" / "rests-on-check.json"

SYSTEM_TEMPLATE = """You check links between a modern claim and the ancient passages its footnote cites.

The claim is a statement a modern work (here Wikipedia) makes; you are asked whether each ancient passage says the same thing. Judge the claim as stored. The modern work's own words are given only to show where the claim was drawn from: details they add beyond the stored claim (what someone did, a number, a wing, a motive) are not part of the claim. For "X participated in the battle", a passage that has X fighting in that battle states it, whatever else the modern words say about X. Code made each link from the footnote's locator alone, so a range such as "65-66" linked the claim to every section of it that we hold. Usually only one or two of them say it, and that is expected: say so plainly.

For each passage, judge only what that passage itself says, in this translation:
- states: the passage says what the claim says (the people, places or events, and the relation between them), though in its own words. A translation's names count: {naming}.
- partly: the passage says part of it, for example the person and the battle but not the role, or the relation but not one of the parties.
- absent: the passage does not say it.
Do not use what you know from other sources, or what another passage in the list says, to fill a gap in one passage.

For states and partly, copy the words that carry it: one continuous run of words from that passage, exactly as written there, with no ellipsis. For absent, leave words empty. Give each reason in one short sentence. Then say whether the cited passages, taken together, state the claim."""
# The template stays general; the example comes from curation (reusable code names no source).
SYSTEM = SYSTEM_TEMPLATE.replace("{naming}", json.loads(CURATION.read_text(encoding="utf-8"))["namingExample"])


class PassageVerdict(BaseModel):
    passage: str = Field(description="the passage's tag, exactly as given, such as P1")
    verdict: Literal["states", "partly", "absent"]
    words: str = Field(default="", description="for states and partly: one continuous run of words copied "
                                               "exactly from this passage; empty for absent")
    reason: str = Field(description="one short sentence")


class ClaimCheck(BaseModel):
    passages: list[PassageVerdict]
    together: Literal["states", "partly", "absent"] = Field(
        description="whether the cited passages, taken together, state the claim")
    reason: str = Field(description="one or two sentences on the citation as a whole")


# A claim is checked once. With --recheck, a claim whose checks are all still open and were made with
# another prompt version is checked again, and the newer check supersedes them.
LINKS = """
MATCH (a:Assertion)-[l:RESTS_ON]->(o:SourceObservation)-[:IN_WORK]->(w:Entity)
WHERE a.status IN ["accepted", "proposed"] AND l.createdBy = $by
  AND coalesce(l.status, "accepted") IN ["accepted", "proposed"]
  AND ($claim IS NULL OR a.id = $claim)
WITH a, collect({id: o.id, ref: coalesce(o.shortLabel, o.id), text: o.passageText, work: w.label,
                 citation: l.citation, quotation: l.quotation}) AS links
OPTIONAL MATCH (p:Proposal {operation: "checkRestsOn"})-[:CHECKS_CLAIM]->(a)
WITH a, links, collect(p {.status, .promptVersion}) AS prior
WHERE size(prior) = 0 OR ($recheck AND all(x IN prior WHERE x.status = "submitted" AND x.promptVersion <> $version))
RETURN a.id AS claim, a.label AS label, links
ORDER BY a.id
"""


def _order(ref: str) -> tuple:
    return tuple(int(n) if n.isdigit() else n for n in re.findall(r"\d+|\D+", ref))


def claims(tx: Any, claim: str | None = None, recheck: bool = False) -> list[dict[str, Any]]:
    rows = tx.run(LINKS, by=HARVEST, claim=claim, recheck=recheck, version=checker_prompt_version()).data()
    for row in rows:
        row["links"] = sorted(row["links"], key=lambda link: _order(link["ref"]))
    return rows


def check_request(model: str, claim: dict[str, Any]) -> dict[str, Any]:
    quotations = list(dict.fromkeys(l["quotation"] for l in claim["links"] if l["quotation"]))
    citations = list(dict.fromkeys(l["citation"] for l in claim["links"] if l["citation"]))
    passages = "\n\n".join(f"[P{n}] {link['ref']} ({link['work']})\n{link['text']}"
                           for n, link in enumerate(claim["links"], 1))
    user = (f"The claim, as stored (judge this): {claim['label']}\n"
            + "".join(f"The modern work's words it was drawn from (context only): \"{q}\"\n" for q in quotations)
            + f"Its footnote cites: {'; '.join(citations) or 'unknown'}\n\n"
            + f"The passages code linked it to:\n\n{passages}")
    return {"model": model, "max_tokens": MAX_TOKENS, "system": SYSTEM,
            "messages": [{"role": "user", "content": user}], "output_format": ClaimCheck}


def checker_prompt_version() -> str:
    return prompt_version("rests-on-check-v2", SYSTEM, check_request)


def _normal(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[–—]", "-", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def checked(output: ClaimCheck, claim: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Each link's verdict, with its words verified verbatim in that passage. Problems are returned,
    never repaired: a passage the model skipped or named twice makes the whole check unusable."""
    tags = {f"P{n}": link for n, link in enumerate(claim["links"], 1)}
    seen: dict[str, PassageVerdict] = {}
    problems = []
    for item in output.passages:
        if item.passage not in tags:
            problems.append(f"unknown passage tag {item.passage!r}")
        elif item.passage in seen:
            problems.append(f"{item.passage} judged twice")
        else:
            seen[item.passage] = item
    problems += [f"{tag} not judged" for tag in tags if tag not in seen]
    rows = []
    for tag, item in seen.items():
        link = tags[tag]
        words = item.words.strip() if item.verdict != "absent" else ""
        verified = bool(words) and "..." not in words and "…" not in words \
            and _normal(words) in _normal(link["text"] or "")
        rows.append({"observationId": link["id"], "ref": link["ref"], "verdict": item.verdict,
                     "words": words or None, "reason": item.reason.strip(), "verified": verified})
    return rows, problems


def proposal_for(claim: dict[str, Any], rows: list[dict[str, Any]], output: ClaimCheck, *, model_id: str,
                 at: str, registry_version: str) -> dict[str, Any]:
    confirmed = all(r["verdict"] == "states" and r["verified"] for r in rows)
    counts = {v: sum(r["verdict"] == v for r in rows) for v in ("states", "partly", "absent")}
    unverified = sum(r["verdict"] != "absent" and not r["verified"] for r in rows)
    verdict = "confirmed" if confirmed else (
        f"to review: {counts['states']} state it, {counts['partly']} in part, {counts['absent']} do not"
        + (f", {unverified} with words not found verbatim" if unverified else ""))
    lines = [f"{r['ref']}: {r['verdict']}" + (f" (\"{r['words']}\")" if r["words"] else "")
             + ("" if r["verified"] or r["verdict"] == "absent" else " [words not found verbatim]")
             + f". {r['reason']}" for r in rows]
    rationale = (f"Reasoning check (D-169) of the {len(rows)} rests-on links code made from the claim's footnote. "
                 f"Taken together, the cited passages: {output.together}. {output.reason.strip()} "
                 + " | ".join(lines))
    digest = hashlib.sha256("|".join(sorted(r["observationId"] for r in rows) + [checker_prompt_version()])
                            .encode("utf-8")).hexdigest()[:12]
    return {
        "id": f"chr:proposal:check:{claim['claim'].split(':', 2)[-1]}:{digest}", "assertionId": claim["claim"],
        "label": f"Check of rests-on links: {claim['label']}",
        "shortLabel": f"check: {len(rows)} passages, {'confirmed' if confirmed else 'to review'}",
        "status": "accepted" if confirmed else "submitted", "verdict": verdict, "createdBy": CHECKER,
        "createdAt": at, "rationale": rationale, "modelId": model_id, "promptVersion": checker_prompt_version(),
        "draftSchemaVersion": SCHEMA, "predicateRegistryVersion": registry_version,
        "decidedAt": at if confirmed else None, "decidedBy": RULE_BY if confirmed else None,
        "decisionBasis": RULE_BASIS if confirmed else None,
        "checks": [{k: r[k] for k in ("observationId", "verdict", "words", "reason", "verified")} for r in rows],
    }


def store(tx: Any, operations: dict[str, str], proposal: dict[str, Any]) -> dict[str, Any]:
    return run_write(tx, operations, "upsert_rests_on_check", proposal)[0]


def decide(tx: Any, operations: dict[str, str], proposal_id: str, status: str, *, decided_by: str,
           decision_basis: str, decided_at: str, reason: str | None = None) -> dict[str, Any]:
    """Accept (the verdicts apply to the links) or reject (with a reason code) an open check, then
    rebuild the fact layer, whose attestation reads the links."""
    from GraphRevised.export.fact_layer import rebuild

    if status == "rejected" and reason not in REASON_CODES:
        raise ReviewError(f"reason must be one of {list(REASON_CODES)}, not {reason!r}")
    rows = tx.run(operations["decide_rests_on_check"], {
        "proposalId": proposal_id, "status": status, "decidedAt": decided_at, "decidedBy": decided_by,
        "decisionBasis": decision_basis, "reason": reason}).data()
    if not rows:
        raise ReviewError(f"{proposal_id} is not an open rests-on check")
    rebuild(tx)
    return rows[0]


def list_checks(tx: Any, status: str | None = "submitted") -> list[dict[str, Any]]:
    return tx.run("""
        MATCH (p:Proposal {operation: 'checkRestsOn'})-[:CHECKS_CLAIM]->(a:Assertion)
        WHERE $status IS NULL OR p.status = $status
        RETURN p.id AS id, p.status AS status, p.checkVerdict AS verdict, a.label AS claim,
               p.rationale AS rationale, p.decidedBy AS decidedBy
        ORDER BY claim""", status=status).data()


def run_check(args: argparse.Namespace, session: Any, client: Any) -> int:
    from GraphRevised.proposals.registry import load_registry

    operations, registry = load_operations(), load_registry()
    work = session.execute_read(lambda tx: claims(tx, args.claim, args.recheck))
    picked, links = [], 0
    for claim in work:
        if args.max_links is not None and links + len(claim["links"]) > args.max_links:
            continue
        picked.append(claim)
        links += len(claim["links"])
    print(f"{len(work)} live claims with unchecked footnote links; this run: {len(picked)} claims, {links} links"
          f" (model {args.model}, prompt {checker_prompt_version()})")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = None
    if args.read:
        RUNS_DIRECTORY.mkdir(exist_ok=True)
        log = (RUNS_DIRECTORY / f"rests-on-check-{stamp}.jsonl").open("w", encoding="utf-8")
        log.write(json.dumps({"model": args.model, "promptVersion": checker_prompt_version(), "apply": args.apply,
                              "claims": len(picked), "links": links, "runCapUSD": str(args.run_cap)}) + "\n")
    worst, start = Decimal(0), (client.meter.spent if client else Decimal(0))
    try:
        for claim in picked:
            request = check_request(args.model, claim)
            top = ceiling(args.model, request)
            worst += top
            if not args.read:
                print(f"  {claim['claim']}: {len(claim['links'])} passages; worst case ${top:.4f}")
                continue
            if client.meter.spent - start + top > args.run_cap:
                print(f"stopped: the next call could take this run past its ${args.run_cap} cap")
                break
            response = client.messages.parse(**request)
            output = response.parsed_output
            record: dict[str, Any] = {"claim": claim["claim"], "model": response.model,
                                      "requestId": response._request_id, "stopReason": response.stop_reason}
            if output is None:
                record["error"] = "refusal or no parsed output"
                log.write(json.dumps(record) + "\n")
                print(f"  {claim['label']}\n    no output ({response.stop_reason}); not stored")
                continue
            rows, problems = checked(output, claim)
            record.update({"together": output.together, "reason": output.reason, "links": rows,
                           "problems": problems})
            print(f"  {claim['label']}\n    together: {output.together}. {output.reason}")
            for r in rows:
                mark = "" if r["verified"] or r["verdict"] == "absent" else "  [words not found verbatim]"
                print(f"    {r['ref']}: {r['verdict']}{mark}" + (f"  \"{r['words']}\"" if r["words"] else "")
                      + f"  ({r['reason']})")
            if problems:
                print(f"    not stored: {'; '.join(problems)}")
                log.write(json.dumps(record) + "\n")
                continue
            at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            proposal = proposal_for(claim, rows, output, model_id=response.model, at=at,
                                    registry_version=registry.version)
            tx = session.begin_transaction()
            try:
                stored = store(tx, operations, proposal)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
            record.update({"proposal": stored["id"], "status": stored["status"], "stored": args.apply})
            print(f"    {'stored' if args.apply else 'validated, rolled back'}: {stored['status']} ({proposal['verdict']})")
            log.write(json.dumps(record) + "\n")
    finally:
        if log is not None:
            log.close()
    if args.read:
        print(f"this run spent ${client.meter.spent - start:.4f}")
    else:
        print(f"worst case for these claims: ${worst:.4f} (dry run; nothing was spent)")
    return 0


def main(argv: list[str] | None = None) -> int:
    from neo4j import GraphDatabase

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    c = commands.add_parser("check")
    c.add_argument("--claim", help="only this claim's links")
    c.add_argument("--max-links", type=int, help="take claims, in order, while their links stay within N")
    c.add_argument("--model", default=MODEL)
    c.add_argument("--read", action="store_true", help="call the model (paid; needs CHRYSTALLUM_BUDGET)")
    c.add_argument("--apply", action="store_true", help="with --read: store the checks")
    c.add_argument("--recheck", action="store_true",
                   help="check again claims whose open checks used another prompt version (they are superseded)")
    c.add_argument("--run-cap", type=Decimal, default=Decimal("5"), help="stop this run at this many USD")
    l = commands.add_parser("list")
    l.add_argument("--status", default="submitted", choices=("submitted", "accepted", "rejected", "all"))
    d = commands.add_parser("decide")
    d.add_argument("proposal_id")
    d.add_argument("decision", choices=("accept", "reject"))
    d.add_argument("--reason", choices=REASON_CODES)
    d.add_argument("--basis", default="")
    d.add_argument("--by", required=True, help="the name the decision is signed with")
    args = parser.parse_args(argv)
    if args.command == "check" and args.apply and not args.read:
        parser.error("--apply needs --read")
    sys.stdout.reconfigure(encoding="utf-8")
    client = None
    if args.command == "check" and args.read:
        from GraphRevised.proposals.passage_reader import anthropic_client
        client = anthropic_client()  # refuses here when no budget is named
    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            if args.command == "check":
                return run_check(args, session, client)
            if args.command == "list":
                rows = session.execute_read(lambda tx: list_checks(tx, None if args.status == "all" else args.status))
                for row in rows:
                    print(f"{row['status']:<10} {row['id']}\n  {row['claim']}\n  {row['verdict']}\n  {row['rationale']}\n")
                print(f"{len(rows)} checks")
                return 0
            status = "accepted" if args.decision == "accept" else "rejected"
            at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            row = session.execute_write(lambda tx: decide(
                tx, load_operations(), args.proposal_id, status, decided_by=args.by, decided_at=at,
                decision_basis=args.basis or f"Curator's review of the check ({status}).", reason=args.reason))
            print(f"{row['id']}: {row['status']}; {row['applied']} links changed; fact layer rebuilt")
            return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
