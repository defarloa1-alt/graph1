"""
Methodical both-sides Cannae roster research (atomic Q-P-Q).

1. Query Wikidata for people linked to Battle of Cannae (Q179591) via P607 / reverse P710
2. Compare to graph Persons + existing military pilot Claims
3. For new QIDs: create Person stubs (approved path) + held FOUGHT_IN Claims
4. Emit research report; optional Anthropic pass for gap notes (slow/methodical)

Usage:
  python -m scripts.agents.military.cannae_roster_research --dry-run
  python -m scripts.agents.military.cannae_roster_research --write
  python -m scripts.agents.military.cannae_roster_research --write --llm-gaps
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import (  # noqa: E402
    NEO4J_DATABASE,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)
from scripts.tools.claim_ingestion_pipeline import ClaimIngestionPipeline  # noqa: E402
from scripts.tools.entity_cipher import generate_entity_cipher  # noqa: E402
from scripts.agents.military.igar import MILITARY_BATTLE_METHOD_PROMPT  # noqa: E402
from scripts.agents.military.registry_predicates import (  # noqa: E402
    assert_military_predicate,
)

load_dotenv()

CANNAE_QID = "Q179591"
CANNAE_ENTITY_ID = "evt_Q179591"
SCOPE_SUBJECT_ID = "sc_q17167_military_wars_campaigns"
SOURCE_AGENT = "SFA_sc_q17167_military_wars_campaigns_MILITARY"
DOMAIN_ID = "roman_republic"
FACET = "military"
PRED_PID = "P607"
USER_AGENT = "ChrystallumGraph1/1.0 (historical KG; Cannae roster research)"

# Seed known sides when Wikidata occupation/affiliation is thin
KNOWN_SIDE: dict[str, str] = {
    "Q36456": "carthaginian",  # Hannibal
    "Q463438": "carthaginian",  # Maharbal (correct WD item)
    "Q311702": "carthaginian",  # Hasdrubal Barca
    "Q6744857": "carthaginian",  # Hasdrubal (disambiguation risk — TBD)
    "Q315274": "roman",
    "Q432244": "roman",
    "Q554632": "roman",
    "Q857028": "roman",
    "Q580979": "roman",  # M. Minucius Rufus
}

# Wrong QID previously used as Maharbal in pilot (WD label = KRR Minigun)
BAD_MAHARBAL_QID = "Q249163"
TRUE_MAHARBAL_QID = "Q463438"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_json(url: str, *, timeout: int = 45) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def sparql(query: str, *, timeout: int = 90, retries: int = 3) -> list[dict[str, Any]]:
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode(
        {"query": query, "format": "json"}
    )
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            data = _http_json(url, timeout=timeout)
            return data.get("results", {}).get("bindings", [])
        except Exception as exc:  # noqa: BLE001 — network flake; retry
            last_err = exc
            print(f"  [warn] SPARQL attempt {attempt}/{retries} failed: {exc}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"SPARQL failed after {retries} attempts: {last_err}")


def fetch_entity_meta(qids: list[str]) -> dict[str, dict[str, Any]]:
    """labels + whether instance-of human (Q5)."""
    if not qids:
        return {}
    meta: dict[str, dict[str, Any]] = {}
    for i in range(0, len(qids), 40):
        chunk = qids[i : i + 40]
        url = (
            "https://www.wikidata.org/w/api.php?"
            + urllib.parse.urlencode(
                {
                    "action": "wbgetentities",
                    "ids": "|".join(chunk),
                    "props": "labels|claims",
                    "languages": "en",
                    "format": "json",
                }
            )
        )
        data = _http_json(url, timeout=45)
        for qid, ent in (data.get("entities") or {}).items():
            lab = ((ent.get("labels") or {}).get("en") or {}).get("value") or qid
            is_human = False
            for c in (ent.get("claims") or {}).get("P31", []):
                try:
                    if c["mainsnak"]["datavalue"]["value"]["id"] == "Q5":
                        is_human = True
                        break
                except (KeyError, TypeError):
                    continue
            meta[qid] = {"label": lab, "is_human": is_human}
        time.sleep(0.2)
    return meta


def fetch_cannae_p710() -> list[str]:
    """Participants listed on the Cannae item (P710)."""
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{CANNAE_QID}.json"
    try:
        data = _http_json(url, timeout=45)
    except Exception as exc:  # noqa: BLE001
        print(f"  [warn] EntityData P710 fetch failed: {exc}")
        return []
    claims = data["entities"][CANNAE_QID]["claims"].get("P710", [])
    qids: list[str] = []
    for c in claims:
        try:
            qids.append(c["mainsnak"]["datavalue"]["value"]["id"])
        except (KeyError, TypeError):
            continue
    return qids


def fetch_wikidata_roster() -> list[dict[str, Any]]:
    """
    People linked to Cannae:
      - Cannae P710 Person (entity API — reliable)
      - Person P607 Cannae (SPARQL — may flake; retry)
    """
    by_qid: dict[str, dict[str, Any]] = {}

    print("  fetching Cannae P710 via EntityData...")
    for qid in fetch_cannae_p710():
        by_qid[qid] = {"qid": qid, "label": qid, "via": "P710"}

    print("  fetching Person P607 Cannae via SPARQL...")
    query = f"""
    SELECT ?person WHERE {{
      ?person wdt:P607 wd:{CANNAE_QID} .
      ?person wdt:P31 wd:Q5 .
    }}
    LIMIT 80
    """
    try:
        for b in sparql(query, timeout=90, retries=3):
            uri = b["person"]["value"]
            qid = uri.rsplit("/", 1)[-1]
            # P607 preferred over P710 when both present
            by_qid[qid] = {"qid": qid, "label": qid, "via": "P607"}
    except Exception as exc:  # noqa: BLE001
        print(f"  [warn] P607 SPARQL unavailable ({exc}); using P710 + seed only")

    # Always include curated both-sides human seeds
    for qid, side in KNOWN_SIDE.items():
        if qid not in by_qid:
            by_qid[qid] = {"qid": qid, "label": qid, "via": "P607", "side_hint": side}

    # Drop the known bad Maharbal QID if present
    by_qid.pop(BAD_MAHARBAL_QID, None)

    meta = fetch_entity_meta(list(by_qid.keys()))
    out: list[dict[str, Any]] = []
    for qid, row in sorted(
        by_qid.items(), key=lambda kv: meta.get(kv[0], {}).get("label", kv[0])
    ):
        info = meta.get(qid) or {"label": qid, "is_human": False}
        if not info["is_human"]:
            print(f"  [skip non-human] {qid} {info['label']}")
            continue
        row = dict(row)
        row["label"] = info["label"]
        out.append(row)
    return out


def existing_pilot_subjects(session: Any) -> set[str]:
    rows = session.run(
        """
        MATCH (c:Claim)
        WHERE c.source_agent = $agent
        RETURN collect(DISTINCT c.subject_qid) AS qids
        """,
        agent=SOURCE_AGENT,
    ).single()
    return set(rows["qids"] or []) if rows else set()


def ensure_person(session: Any, qid: str, label: str) -> dict[str, Any]:
    entity_id = f"person_{qid.lower()}"
    entity_cipher = generate_entity_cipher("PERSON", qid=qid, namespace="wd")
    row = session.run(
        """
        MERGE (p:Person {qid: $qid})
        ON CREATE SET
            p:Entity,
            p.label = $label,
            p.entity_type = 'Person',
            p.entity_id = $entity_id,
            p.entity_cipher = $entity_cipher,
            p.stub = true,
            p.created_by = 'cannae_roster_research',
            p.created_at = datetime()
        ON MATCH SET
            p:Entity,
            p.label = coalesce(p.label, $label),
            p.entity_id = coalesce(p.entity_id, $entity_id),
            p.entity_cipher = coalesce(p.entity_cipher, $entity_cipher)
        RETURN p.qid AS qid, p.label AS label, p.entity_id AS entity_id
        """,
        qid=qid,
        label=label,
        entity_id=entity_id,
        entity_cipher=entity_cipher,
    ).single()
    return dict(row)


def route_claim(session: Any, claim_id: str) -> None:
    session.run(
        """
        MATCH (c:Claim {claim_id: $claim_id})
        MATCH (sc:SubjectConcept {subject_id: $subject_id})
        MERGE (c)-[r:IN_SCOPE]->(sc)
        SET r.routed_at = datetime(),
            r.routing_method = 'cannae_roster_research',
            r.domain_id = $domain_id,
            c.routed_subject_id = $subject_id,
            c.routed_subject_label = sc.label,
            c.domain_id = $domain_id
        """,
        claim_id=claim_id,
        subject_id=SCOPE_SUBJECT_ID,
        domain_id=DOMAIN_ID,
    )


def guess_side(qid: str, label: str) -> str:
    if qid in KNOWN_SIDE:
        return KNOWN_SIDE[qid]
    # Conservative default — research needed
    return "unknown"


def llm_gap_notes(roster: list[dict[str, Any]], missing: list[dict[str, Any]]) -> str:
    """Optional slow Anthropic pass for research notes. Never invents QIDs."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "LLM gaps skipped: ANTHROPIC_API_KEY not set"
    try:
        import anthropic
    except ImportError:
        return "LLM gaps skipped: anthropic package not installed"

    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""{MILITARY_BATTLE_METHOD_PROMPT}

Task: Battle of Cannae (Q179591) both-sides roster gap analysis.
Be slow and methodical. Do NOT invent QIDs. Do NOT invent IGAR.
Focus on: who is missing, which side, which predicate may be TBD, what primary source to check.

Wikidata roster QIDs already found:
{json.dumps(roster, indent=2)}

Not yet claimed in Chrystallum military pilot:
{json.dumps(missing, indent=2)}

Return concise markdown bullets only.
"""
    print("[llm] requesting methodical gap notes (this may take a minute)...")
    response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts).strip() or "(empty LLM response)"


def reject_bad_maharbal_claim(session: Any) -> None:
    """Reject pilot claim that used wrong Maharbal QID."""
    session.run(
        """
        MATCH (c:Claim)
        WHERE c.source_agent = $agent AND c.subject_qid = $bad
        SET c.status = 'rejected',
            c.predicate_status = 'tbd',
            c.review_notes = coalesce(c.review_notes, '') +
              ' | REJECTED: Q249163 is not Maharbal on Wikidata (label KRR Minigun); '
              + 'use Q463438 instead',
            c.reviewed_at = datetime(),
            c.reviewed_by = 'cannae_roster_research'
        """,
        agent=SOURCE_AGENT,
        bad=BAD_MAHARBAL_QID,
    )
    print(
        f"  [fix] rejected bad Maharbal claim subject={BAD_MAHARBAL_QID}; "
        f"true QID={TRUE_MAHARBAL_QID}"
    )


def run(*, write: bool, llm_gaps: bool) -> int:
    print(MILITARY_BATTLE_METHOD_PROMPT)
    print()
    print("[1/4] Fetching Wikidata Cannae participants...")
    roster = fetch_wikidata_roster()
    print(f"  Wikidata people: {len(roster)}")
    for r in roster:
        print(f"    {r['qid']}  {r['label']:<40} via {r['via']}")

    driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    database = NEO4J_DATABASE or "neo4j"
    pipeline = ClaimIngestionPipeline(driver, database=database)
    created: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    try:
        with driver.session(database=database) as session:
            if write:
                reject_bad_maharbal_claim(session)
            session.run(
                """
                MATCH (e:Event {qid: $qid})
                SET e.entity_id = coalesce(e.entity_id, $eid)
                """,
                qid=CANNAE_QID,
                eid=CANNAE_ENTITY_ID,
            )
            already = existing_pilot_subjects(session)
            print(f"\n[2/4] Existing pilot subjects: {len(already)}")

            missing = [r for r in roster if r["qid"] not in already]
            print(f"[3/4] Missing from pilot Claims: {len(missing)}")

            rel = assert_military_predicate("FOUGHT_IN", require_implemented=True)
            for person in missing:
                side = guess_side(person["qid"], person["label"])
                wd = ClaimIngestionPipeline.format_wd_statement(
                    person["qid"], PRED_PID, CANNAE_QID
                )
                pred_status = "confirmed" if person["via"] == "P607" else "tbd"
                research_notes = ""
                if pred_status == "tbd":
                    research_notes = (
                        f"Linked via Cannae {person['via']} on Wikidata; "
                        "confirm FOUGHT_IN vs finer military predicate before Validate."
                    )
                if side == "unknown":
                    research_notes = (
                        (research_notes + " ") if research_notes else ""
                    ) + "Side unknown — classify roman/carthaginian before Validate."
                    pred_status = "tbd"

                item = {
                    "qid": person["qid"],
                    "label": person["label"],
                    "side": side,
                    "via": person["via"],
                    "wd_statement": wd,
                    "predicate_status": pred_status,
                    "research_notes": research_notes.strip(),
                }
                print(
                    f"  + {wd}  {person['label']}  side={side}  "
                    f"status={pred_status}"
                )
                if not write:
                    skipped.append({**item, "status": "dry_run"})
                    continue

                person_node = ensure_person(session, person["qid"], person["label"])
                time.sleep(0.05)
                outcome = pipeline.ingest_claim(
                    entity_id=person_node["entity_id"],
                    relationship_type=rel,
                    target_id=CANNAE_ENTITY_ID,
                    confidence=0.7 if pred_status == "tbd" else 0.85,
                    label=f"{person['label']} fought in Battle of Cannae",
                    description=(
                        f"Atomic participation ({wd}) from Wikidata roster research. "
                        f"via={person['via']}; side={side}. "
                        "IGAR not attached."
                    ),
                    subject_qid=person["qid"],
                    retrieval_source="cannae_roster_research",
                    reasoning_notes="Wikidata P607/P710 roster expansion",
                    facet=FACET,
                    claim_signature={
                        "qid": person["qid"],
                        "pvalues": [PRED_PID],
                        "values": {PRED_PID: CANNAE_QID},
                        "rel": rel,
                        "pilot": "military_training_igar_both_sides_2026_07_16",
                        "side": side,
                    },
                    claim_type="relational",
                    source_agent=SOURCE_AGENT,
                    authority_source="wikidata",
                    authority_ids={
                        "person_qid": person["qid"],
                        "candidate_qid": CANNAE_QID,
                        "pred_pid": PRED_PID,
                        "domain_id": DOMAIN_ID,
                        "side": side,
                        "claim_layer": "atomic_participation",
                        "wikidata_via": person["via"],
                    },
                    pred_pid=PRED_PID,
                    strict_registry=True,
                    igar=None,
                    predicate_status=pred_status,
                    research_notes=research_notes,
                    initial_status="held",
                    require_igar=False,
                )
                claim_id = outcome.get("claim_id")
                if claim_id and outcome.get("status") != "error":
                    route_claim(session, claim_id)
                    session.run(
                        """
                        MATCH (c:Claim {claim_id: $cid})
                        SET c.status = 'held',
                            c.claim_layer = 'atomic_participation',
                            c.wd_statement = coalesce(c.wd_statement, $wd)
                        """,
                        cid=claim_id,
                        wd=wd,
                    )
                created.append({**item, **outcome})
                print(f"    -> {outcome.get('status')} {claim_id} {outcome.get('error')}")

        llm_notes = ""
        if llm_gaps:
            print("\n[4/4] LLM gap notes...")
            llm_notes = llm_gap_notes(roster, missing)
        else:
            print("\n[4/4] LLM gap notes skipped (pass --llm-gaps to enable)")

        out = {
            "ran_at": _utc_now(),
            "mode": "write" if write else "dry_run",
            "cannae_qid": CANNAE_QID,
            "wikidata_roster": roster,
            "created_or_dry": created or skipped,
            "llm_gap_notes": llm_notes,
        }
        out_path = ROOT / "output" / "cannae_roster_research.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
        print(f"\nWrote {out_path}")
        if llm_notes:
            notes_path = ROOT / "output" / "cannae_roster_llm_gaps.md"
            notes_path.write_text(llm_notes, encoding="utf-8")
            print(f"Wrote {notes_path}")
        print("[OK]")
        return 0
    finally:
        driver.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Cannae both-sides roster research")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument(
        "--llm-gaps",
        action="store_true",
        help="Ask Anthropic for slow methodical gap notes (no graph writes from LLM)",
    )
    args = ap.parse_args()
    if not args.dry_run and not args.write:
        ap.error("Specify --dry-run or --write")
    return run(write=args.write, llm_gaps=args.llm_gaps)


if __name__ == "__main__":
    raise SystemExit(main())
