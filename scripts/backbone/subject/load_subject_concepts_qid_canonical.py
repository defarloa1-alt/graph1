#!/usr/bin/env python3
"""
Load SubjectConcepts in QID-canonical format to Neo4j.

Canonical model:
  - SubjectConcept identity = qid (no slug)
  - DOMAIN_OF edge to KnowledgeDomain (scoping, not embedded in string)
  - BROADER_THAN edges for hierarchy (broader -> narrower)

Input:
  - output/subject_concepts/subject_concept_anchors_qid_canonical.json
  - output/subject_concepts/subject_concept_hierarchy.json
  - output/backlinks/*_report.json (optional) — sets harvest_status from backlink_rows

Usage:
    python scripts/backbone/subject/load_subject_concepts_qid_canonical.py
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:
    print("Error: pip install neo4j", file=sys.stderr)
    sys.exit(1)

# Config: load from .env at runtime (not module load) so dotenv is applied first
def _get_neo4j_config():
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parents[3] / ".env")
    except ImportError:
        pass
    return {
        "uri": os.getenv("NEO4J_URI", "neo4j+s://f7b612a3.databases.neo4j.io"),
        "user": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", ""),
        "database": os.getenv("NEO4J_DATABASE", "neo4j"),
    }


def load_anchors(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_hierarchy(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("broader_than", [])


def escape_cypher(s: str) -> str:
    """Escape single quotes for Cypher string literals."""
    return (s or "").replace("\\", "\\\\").replace("'", "\\'")


def load_harvest_status(harvest_dir: Path) -> dict[str, str]:
    """
    Read harvest reports, return {qid: "confirmed"|"unconfirmed"}.
    backlink_rows == 0 -> unconfirmed (no Wikidata corroboration yet).
    """
    status: dict[str, str] = {}
    for report_path in harvest_dir.glob("*_report.json"):
        try:
            with open(report_path, encoding="utf-8") as f:
                data = json.load(f)
            seed_qid = data.get("seed_qid")
            if not seed_qid:
                continue
            backlink_rows = data.get("counts", {}).get("backlink_rows", -1)
            status[seed_qid] = "confirmed" if backlink_rows > 0 else "unconfirmed"
        except (json.JSONDecodeError, KeyError):
            continue
    return status


def main():
    parser = argparse.ArgumentParser(description="Load QID-canonical SubjectConcepts to Neo4j")
    parser.add_argument(
        "--anchors",
        default="output/subject_concepts/subject_concept_anchors_qid_canonical.json",
        help="Path to canonical anchors JSON",
    )
    parser.add_argument(
        "--hierarchy",
        default="output/subject_concepts/subject_concept_hierarchy.json",
        help="Path to hierarchy JSON",
    )
    parser.add_argument(
        "--harvest-dir",
        default="output/backlinks",
        help="Harvest reports dir for harvest_status (backlink_rows==0 -> unconfirmed)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print summary only, no write")
    parser.add_argument(
        "--cypher",
        metavar="FILE",
        nargs="?",
        const="output/neo4j/load_subject_concepts_qid_canonical.cypher",
        help="Write Cypher to file (no Neo4j connection). Run in Neo4j Browser when reachable.",
    )
    parser.add_argument("--neo4j-password", default=None, help="Neo4j password (or NEO4J_PASSWORD env)")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    anchors_path = project_root / args.anchors
    hierarchy_path = project_root / args.hierarchy
    harvest_dir = project_root / args.harvest_dir

    if not anchors_path.exists():
        print(f"Error: {anchors_path} not found", file=sys.stderr)
        sys.exit(1)
    if not hierarchy_path.exists():
        print(f"Error: {hierarchy_path} not found", file=sys.stderr)
        sys.exit(1)

    anchors = load_anchors(anchors_path)
    hierarchy = load_hierarchy(hierarchy_path)
    harvest_status = load_harvest_status(harvest_dir) if harvest_dir.exists() else {}

    cfg = _get_neo4j_config()
    password = args.neo4j_password or cfg["password"]
    if not args.dry_run and not args.cypher and not password:
        import getpass
        password = getpass.getpass("Neo4j password: ")

    print("=" * 70)
    print("LOAD SUBJECTCONCEPTS (QID-CANONICAL)")
    print("=" * 70)
    print(f"Anchors:   {len(anchors)} SubjectConcepts")
    print(f"Hierarchy: {len(hierarchy)} BROADER_THAN edges")
    unconfirmed = sum(1 for a in anchors if harvest_status.get(a["qid"]) == "unconfirmed")
    print(f"Harvest:   {len(harvest_status)} reports, {unconfirmed} unconfirmed (backlink_rows=0)")
    print()

    if args.dry_run:
        print("[DRY RUN] Would create:")
        for a in anchors[:5]:
            print(f"  SubjectConcept {{qid: {a['qid']}, label: {a['label'][:40]}...}}")
        print(f"  ... and {len(anchors) - 5} more")
        print(f"  KnowledgeDomain {{qid: Q17167}}")
        print(f"  {len(hierarchy)} BROADER_THAN edges")
        return

    # --cypher: write to file, no Neo4j connection (use when DNS/network unreachable)
    if args.cypher:
        out_path = project_root / args.cypher
        out_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "// QID-canonical SubjectConcepts - run after migrate_subject_concepts_to_qid_canonical.cypher\n",
            "// Generated by load_subject_concepts_qid_canonical.py --cypher\n\n",
            "MERGE (kd:KnowledgeDomain {qid: 'Q17167'})\nSET kd.label = 'Roman Republic';\n\n",
        ]
        for a in anchors:
            qid, label, facet, conf = a["qid"], a.get("label", ""), a.get("primary_facet", ""), a.get("confidence", "")
            status = harvest_status.get(qid, "unknown")
            lines.append(f"MERGE (sc:SubjectConcept {{qid: '{qid}'}})\n")
            lines.append(f"SET sc.subject_id = '{qid}', sc.label = '{escape_cypher(label)}', sc.primary_facet = '{escape_cypher(facet)}', ")
            lines.append(f"sc.confidence = '{escape_cypher(conf)}', sc.source = 'wikidata', sc.harvest_status = '{status}';\n\n")
        for a in anchors:
            lines.append(f"MATCH (sc:SubjectConcept {{qid: '{a['qid']}'}})\n")
            lines.append(f"MATCH (kd:KnowledgeDomain {{qid: '{a.get('domain_qid', 'Q17167')}'}})\n")
            lines.append("MERGE (sc)-[:DOMAIN_OF]->(kd);\n\n")
        for h in hierarchy:
            lines.append(f"MATCH (broader:SubjectConcept {{qid: '{h['parent_qid']}'}})\n")
            lines.append(f"MATCH (narrower:SubjectConcept {{qid: '{h['child_qid']}'}})\n")
            lines.append("MERGE (broader)-[:BROADER_THAN]->(narrower);\n\n")
        out_path.write_text("".join(lines), encoding="utf-8")
        print(f"  Cypher written: {out_path}")
        print("  Run in Neo4j Browser when connectivity is available.")
        return

    driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["user"], password))

    try:
        with driver.session(database=cfg["database"]) as session:
            # 1. Ensure KnowledgeDomain exists (root Q17167)
            session.run("""
                MERGE (kd:KnowledgeDomain {qid: 'Q17167'})
                SET kd.label = 'Roman Republic'
            """)
            print("  [1/4] KnowledgeDomain Q17167 ensured")

            # 2. Create SubjectConcept nodes (qid as identity)
            for a in anchors:
                qid = a["qid"]
                status = harvest_status.get(qid, "unknown")  # confirmed|unconfirmed|unknown
                session.run("""
                    MERGE (sc:SubjectConcept {qid: $qid})
                    SET sc.subject_id = $qid,
                        sc.label = $label,
                        sc.primary_facet = $primary_facet,
                        sc.confidence = $confidence,
                        sc.source = 'wikidata',
                        sc.harvest_status = $harvest_status
                """, qid=qid, label=a.get("label", ""),
                     primary_facet=a.get("primary_facet", ""),
                     confidence=a.get("confidence", ""),
                     harvest_status=status)

            print(f"  [2/4] {len(anchors)} SubjectConcept nodes created/updated")

            # 3. DOMAIN_OF edges
            for a in anchors:
                session.run("""
                    MATCH (sc:SubjectConcept {qid: $qid})
                    MATCH (kd:KnowledgeDomain {qid: $domain_qid})
                    MERGE (sc)-[:DOMAIN_OF]->(kd)
                """, qid=a["qid"], domain_qid=a.get("domain_qid", "Q17167"))

            print(f"  [3/4] DOMAIN_OF edges created")

            # 4. BROADER_THAN edges (parent is broader, child is narrower)
            for h in hierarchy:
                session.run("""
                    MATCH (broader:SubjectConcept {qid: $parent_qid})
                    MATCH (narrower:SubjectConcept {qid: $child_qid})
                    MERGE (broader)-[:BROADER_THAN]->(narrower)
                """, parent_qid=h["parent_qid"], child_qid=h["child_qid"])

            print(f"  [4/4] {len(hierarchy)} BROADER_THAN edges created")

            # Verify
            result = session.run("MATCH (sc:SubjectConcept) RETURN count(sc) AS n")
            n = result.single()["n"]
            result = session.run("MATCH ()-[r:BROADER_THAN]->() RETURN count(r) AS n")
            bt = result.single()["n"]
            result = session.run("MATCH ()-[r:DOMAIN_OF]->() RETURN count(r) AS n")
            do = result.single()["n"]

        print()
        print("VERIFICATION")
        print(f"  SubjectConcepts: {n}")
        print(f"  BROADER_THAN:   {bt}")
        print(f"  DOMAIN_OF:      {do}")
        print("=" * 70)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
