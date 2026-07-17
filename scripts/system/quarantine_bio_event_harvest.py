"""
Quarantine prior biographic Event harvest contamination.

Policy (2026-07-16):
  - Biographic harvest must not author Event nodes or PARTICIPATED_IN.
  - Prior path fabricated Event.start_date from person birth/death years.
  - Treat that Event temporal data as untrusted; demote PARTICIPATED_IN edges.

Actions (--apply):
  1. Audit bio-sourced PARTICIPATED_IN + *-01-01 Event dates to JSON.
  2. Flag Events: date_untrusted=true, date_source=bio_person_proxy.
  3. DELETE PARTICIPATED_IN where source in wikidata_p607 / wikidata_p793_p1344.
  4. Fix Cannae Q179591.start_date from Wikidata P585 (-0216-08-02).
  5. Quarantine mislabeled Event Q36456 (Wikidata Hannibal, not Cannae).

Usage:
  python scripts/system/quarantine_bio_event_harvest.py --dry-run
  python scripts/system/quarantine_bio_event_harvest.py --apply
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
load_dotenv()

BIO_PARTICIPATION_SOURCES = ("wikidata_p607", "wikidata_p793_p1344")
CANNAE_QID = "Q179591"
CANNAE_WD_START = "-0216-08-02"  # Wikidata P585 (verified)
HANNUAL_AS_EVENT_QID = "Q36456"  # Wikidata person Hannibal, mislabeled Event


def connect():
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(
            os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER"),
            os.getenv("NEO4J_PASSWORD"),
        ),
    ), os.getenv("NEO4J_DATABASE") or "neo4j"


def fetch_wikidata_p585(qid: str) -> str | None:
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ChrystallumGraph1/1.0 (historical KG; local maintenance)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.load(resp)
    except Exception as exc:
        print(f"WARN Wikidata fetch failed for {qid}: {exc}")
        return None
    claims = data["entities"][qid]["claims"].get("P585", [])
    if not claims:
        return None
    time_val = claims[0]["mainsnak"]["datavalue"]["value"]["time"]
    # Wikidata: +0216-08-02T00:00:00Z or -0216-08-02T00:00:00Z
    # Graph convention for BCE: -0216-08-02
    if time_val.startswith("+"):
        return time_val[1:11]
    if time_val.startswith("-"):
        return time_val[:11]
    return time_val[:10]


def audit(session, out_path: Path) -> dict:
    edges = [
        dict(r)
        for r in session.run(
            """
            MATCH (p:Person)-[r:PARTICIPATED_IN]->(e:Event)
            WHERE r.source IN $sources
            RETURN p.qid AS person_qid, p.label AS person_label,
                   p.birth_year AS birth_year, p.death_year AS death_year,
                   e.qid AS event_qid, e.label AS event_label,
                   e.start_date AS event_start_date,
                   r.source AS source
            ORDER BY e.qid, p.qid
            """,
            sources=list(BIO_PARTICIPATION_SOURCES),
        )
    ]
    events = [
        dict(r)
        for r in session.run(
            """
            MATCH (e:Event)
            WHERE e.start_date ENDS WITH '-01-01'
               OR e.qid = $bad_qid
            OPTIONAL MATCH (e)<-[r:PARTICIPATED_IN]-()
            RETURN e.qid AS qid, e.label AS label, e.start_date AS start_date,
                   keys(e) AS keys, count(r) AS participation_count
            ORDER BY e.qid
            """,
            bad_qid=HANNUAL_AS_EVENT_QID,
        )
    ]
    payload = {
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "policy": "bio_event_harvest_quarantine_2026_07_16",
        "participation_edge_count": len(edges),
        "proxy_or_bad_event_count": len(events),
        "participation_edges": edges,
        "events": events,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def preview(session) -> None:
    for r in session.run(
        """
        MATCH ()-[r:PARTICIPATED_IN]->()
        WHERE r.source IN $sources
        RETURN r.source AS source, count(*) AS n
        ORDER BY n DESC
        """,
        sources=list(BIO_PARTICIPATION_SOURCES),
    ):
        print("PARTICIPATED_IN", dict(r))
    for r in session.run(
        """
        MATCH (e:Event)
        WHERE e.start_date ENDS WITH '-01-01'
        RETURN count(e) AS proxy_date_events
        """
    ):
        print("proxy_date_events", dict(r))
    for r in session.run(
        """
        MATCH (e:Event {qid: $qid})
        RETURN e.qid AS qid, e.label AS label, e.start_date AS start_date,
               e.date_untrusted AS date_untrusted
        """,
        qid=CANNAE_QID,
    ):
        print("cannae", dict(r))
    for r in session.run(
        """
        MATCH (n {qid: $qid})
        RETURN labels(n) AS labels, n.label AS label, n.start_date AS start_date
        """,
        qid=HANNUAL_AS_EVENT_QID,
    ):
        print("q36456", dict(r))


def apply(session, audit_path: Path) -> None:
    payload = audit(session, audit_path)
    print(f"Wrote audit: {audit_path} ({payload['participation_edge_count']} edges)")

    # 1) Flag proxy-date Events
    flagged = session.run(
        """
        MATCH (e:Event)
        WHERE e.start_date ENDS WITH '-01-01'
        SET e.date_untrusted = true,
            e.date_source = 'bio_person_proxy',
            e.quarantined_at = datetime(),
            e.quarantine_reason = 'bio_harvest_person_year_proxy_date'
        RETURN count(e) AS n
        """
    ).single()["n"]
    print(f"Flagged date_untrusted Events: {flagged}")

    # 2) Demote PARTICIPATED_IN (delete after audit)
    deleted = session.run(
        """
        MATCH ()-[r:PARTICIPATED_IN]->()
        WHERE r.source IN $sources
        DELETE r
        RETURN count(*) AS n
        """,
        sources=list(BIO_PARTICIPATION_SOURCES),
    ).single()["n"]
    print(f"Deleted PARTICIPATED_IN edges: {deleted}")

    # 3) Fix Cannae from Wikidata P585
    wd_date = fetch_wikidata_p585(CANNAE_QID) or CANNAE_WD_START
    if wd_date != CANNAE_WD_START:
        print(f"WARN: live Wikidata P585={wd_date}; using that value")
    fixed = session.run(
        """
        MATCH (e:Event {qid: $qid})
        SET e.start_date = $start_date,
            e.date_source = 'wikidata_p585',
            e.date_untrusted = false,
            e.quarantine_reason = null,
            e.date_corrected_at = datetime(),
            e.date_corrected_from = 'bio_person_proxy'
        RETURN e.qid AS qid, e.start_date AS start_date, e.date_source AS date_source
        """,
        qid=CANNAE_QID,
        start_date=wd_date,
    ).single()
    print("Cannae fixed:", dict(fixed) if fixed else None)

    # 4) Quarantine Event Q36456 (Hannibal mislabeled as Cannae)
    bad = session.run(
        """
        MATCH (e:Event {qid: $qid})
        SET e.quarantined = true,
            e.date_untrusted = true,
            e.quarantine_reason = 'qid_is_wikidata_hannibal_not_battle_of_cannae',
            e.quarantined_at = datetime(),
            e.label = coalesce(e.label, 'Q36456') + ' [QUARANTINE: not Cannae; WD=Hannibal]'
        RETURN e.qid AS qid, e.label AS label, e.start_date AS start_date
        """,
        qid=HANNUAL_AS_EVENT_QID,
    ).single()
    print("Q36456 quarantined:", dict(bad) if bad else "not found as Event")

    remaining = session.run(
        """
        MATCH ()-[r:PARTICIPATED_IN]->()
        WHERE r.source IN $sources
        RETURN count(r) AS n
        """,
        sources=list(BIO_PARTICIPATION_SOURCES),
    ).single()["n"]
    print(f"Remaining bio PARTICIPATED_IN: {remaining}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--audit-out",
        default=str(ROOT / "output" / "quarantine_bio_event_harvest.json"),
    )
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        parser.error("Specify --dry-run or --apply")

    driver, database = connect()
    audit_path = Path(args.audit_out)
    with driver.session(database=database) as session:
        preview(session)
        if args.dry_run:
            payload = audit(session, audit_path)
            print(
                f"[dry-run] audit written: {audit_path} "
                f"({payload['participation_edge_count']} edges, "
                f"{payload['proxy_or_bad_event_count']} events)"
            )
        else:
            apply(session, audit_path)
    driver.close()


if __name__ == "__main__":
    main()
