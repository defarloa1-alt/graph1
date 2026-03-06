"""
Facet Console - harvest plan CLI

Usage:
    python -m scripts.agents.facet_console.harvest_plan_cli --facet Biographic --max 5
"""

import argparse
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from neo4j import GraphDatabase

# Suppress Neo4j property warnings (e.g. facets, primary_for not in graph)
try:
    from neo4j import NotificationMinimumSeverity, NotificationDisabledClassification
    _DRIVER_CONFIG = {
        "warn_notification_severity": NotificationMinimumSeverity.OFF,
        "notifications_disabled_classifications": [NotificationDisabledClassification.UNRECOGNIZED],
    }
except ImportError:
    try:
        from neo4j import NotificationMinimumSeverity
        _DRIVER_CONFIG = {"warn_notification_severity": NotificationMinimumSeverity.OFF}
    except ImportError:
        _DRIVER_CONFIG = {}

from scripts.agents.facet_console.discipline_registry import get_facet_disciplines
from scripts.agents.facet_console.harvest_job import create_harvest_job, REPOS_TEMPLATES


def main():
    parser = argparse.ArgumentParser(description="Generate harvest plan for a facet")
    parser.add_argument("--facet", default="Biographic", help="Facet label")
    parser.add_argument("--max", type=int, default=5, help="Max disciplines")
    parser.add_argument("--write", action="store_true", help="Write harvest jobs to output/")
    args = parser.parse_args()

    try:
        from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
        uri, user, password = NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    except ImportError:
        uri, user, password = "bolt://localhost:7687", "neo4j", ""

    if not password:
        print("NEO4J_PASSWORD required. Set in .env or config.", file=sys.stderr)
        sys.exit(1)
    driver = GraphDatabase.driver(uri, auth=(user, password), **_DRIVER_CONFIG)
    with driver.session() as session:
        disciplines = get_facet_disciplines(
            args.facet,
            session=session,
            prioritize_primary=True,
            max_disciplines=args.max,
        )

    driver.close()

    print(f"Facet: {args.facet}")
    print(f"Disciplines: {len(disciplines)}")
    for d in disciplines:
        role = "primary" if args.facet in (d.get("primary_for") or []) else "secondary"
        needs = "needs_harvest" if d.get("needs_harvest") else "in_graph"
        print(f"  {d['qid']} {d['label']} ({role}, {needs})")
        if args.write and d.get("repos"):
            for repo in d["repos"][:2]:
                if repo in REPOS_TEMPLATES:
                    job = create_harvest_job(
                        d["qid"], d["label"], args.facet, repo, d
                    )
                    if job:
                        print(f"    -> {repo}: {job['url'][:60]}...")

    if args.write:
        print(f"\nJobs written to output/facet_harvest_jobs/{args.facet.replace(' ', '_')}/")


if __name__ == "__main__":
    main()
