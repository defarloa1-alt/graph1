#!/usr/bin/env python3
"""
SFA Learning Bootstrap — Load inputs for SFA learning phase (no LLM).

Loads SYS_, Classification anchors (POSITIONED_AS), Discipline subgraph,
entity ontology slice (orgs, institutions — not individual persons), and
authority IDs (LCC/LCSH/FAST). Prints a summary for validation.

Usage:
    python scripts/agents/sfa_learning_bootstrap.py --dry-run
    python scripts/agents/sfa_learning_bootstrap.py --dry-run --seed Q17167
    python scripts/agents/sfa_learning_bootstrap.py --dry-run --json-out output/sfa_bootstrap_summary.json

Exit: 0 if all inputs present, 1 if any critical input missing.
"""

import argparse
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

try:
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = None

# Known ontology QIDs (institutions, not individual persons)
ONTOLOGY_SAMPLE_QIDS = [
    "Q130614",   # Roman Senate
    "Q842606",   # Senate (generic)
    "Q1114821",  # Citizens' assembly
    "Q17167",    # Roman Republic
    "Q1747689",  # Ancient Rome
    "Q220",      # Rome (city)
]


def load_sys(session) -> dict:
    """Load SYS_Policy nodes."""
    r = session.run("MATCH (p:SYS_Policy) RETURN p.name AS name, p.active AS active ORDER BY p.name")
    rows = list(r)
    return {
        "count": len(rows),
        "policies": [{"name": row["name"], "active": row.get("active")} for row in rows],
    }


def load_positioned_as(session, seed_qid: str) -> dict:
    """Load POSITIONED_AS chain for seed (SubjectConcept or Entity)."""
    r = session.run("""
        MATCH (sc)-[r:POSITIONED_AS]->(target)
        WHERE sc.qid = $seed
        RETURN target.qid AS target_qid, target.label AS target_label,
               r.rel_type AS rel_type, r.hops AS hops
        ORDER BY r.hops, target_qid
    """, seed=seed_qid)
    rows = list(r)
    return {
        "count": len(rows),
        "targets": [{"qid": row["target_qid"], "label": row["target_label"], "rel_type": row["rel_type"], "hops": row["hops"]} for row in rows],
    }


def load_discipline_subgraph(session) -> dict:
    """Load Discipline nodes and hierarchy edges."""
    r = session.run("MATCH (d:Discipline) RETURN count(d) AS n")
    n_disc = r.single()["n"]
    r = session.run("""
        MATCH (d:Discipline)-[r]->()
        RETURN type(r) AS rel_type, count(r) AS n
    """)
    edges = {row["rel_type"]: row["n"] for row in r}
    # Sample disciplines
    r = session.run("""
        MATCH (d:Discipline)
        RETURN d.qid AS qid, d.label AS label
        ORDER BY d.label
        LIMIT 15
    """)
    sample = [{"qid": row["qid"], "label": row["label"]} for row in r]
    return {
        "discipline_count": n_disc,
        "hierarchy_edges": edges,
        "sample": sample,
    }


def load_entity_ontology_slice(session, seed_qid: str) -> dict:
    """Load entity ontology slice: orgs, institutions, places, events — not individual persons."""
    # Count by entity_type (if present)
    r = session.run("""
        MATCH (e:Entity)
        RETURN coalesce(e.entity_type, 'unknown') AS et, count(e) AS n
        ORDER BY n DESC
    """)
    by_type = {row["et"]: row["n"] for row in r}
    # Ontology sample: known QIDs first, then org/place/event (no dprr_uri = not individual senator)
    r = session.run("""
        MATCH (e:Entity)
        WHERE e.qid IN $qids
           OR (e.entity_type IN ['Organization', 'Event', 'Place', 'Institution', 'ORGANIZATION', 'PLACE', 'EVENT'] AND e.dprr_uri IS NULL)
        RETURN e.qid AS qid, e.label AS label, e.entity_type AS entity_type
        ORDER BY CASE WHEN e.qid IN $qids THEN 0 ELSE 1 END, e.entity_type, e.label
        LIMIT 30
    """, qids=ONTOLOGY_SAMPLE_QIDS)
    sample = [{"qid": row["qid"], "label": row["label"], "entity_type": row["entity_type"]} for row in r]
    total_entities = sum(by_type.values())
    return {
        "total_entities": total_entities,
        "by_type": by_type,
        "ontology_sample_count": len(sample),
        "ontology_sample": sample,
    }


def load_authority_anchors(session, seed_qid: str) -> dict:
    """Load authority IDs (LCC, LCSH, FAST, Dewey) from Discipline tree, ClassificationAnchor, POSITIONED_AS targets."""
    # Discipline nodes — the main tree of authority anchors (fast_id, lcc, lcsh_id, ddc)
    r = session.run("""
        MATCH (d:Discipline)
        WHERE d.fast_id IS NOT NULL OR d.lcc IS NOT NULL OR d.lcsh_id IS NOT NULL OR d.ddc IS NOT NULL
        RETURN d.qid AS qid, d.label AS label, d.ddc AS dewey, d.lcc AS lcc, d.lcsh_id AS lcsh_id, d.fast_id AS fast_id
        LIMIT 20
    """)
    disciplines = [dict(row) for row in r]
    # Count total Discipline nodes with any authority
    r = session.run("""
        MATCH (d:Discipline)
        WHERE d.fast_id IS NOT NULL OR d.lcc IS NOT NULL OR d.lcsh_id IS NOT NULL OR d.ddc IS NOT NULL OR d.gnd_id IS NOT NULL OR d.aat_id IS NOT NULL
        RETURN count(d) AS n
    """)
    discipline_count = r.single()["n"]
    # ClassificationAnchor nodes (if label exists in schema)
    r = session.run("""
        MATCH (a:ClassificationAnchor)
        WHERE a.dewey IS NOT NULL OR a.lcc IS NOT NULL OR a.lcsh_id IS NOT NULL OR a.fast_id IS NOT NULL
        RETURN a.qid AS qid, a.label AS label, a.dewey AS dewey, a.lcc AS lcc, a.lcsh_id AS lcsh_id, a.fast_id AS fast_id
        LIMIT 20
    """)
    anchors = [dict(row) for row in r]
    # POSITIONED_AS targets with authority props (Entity may have lcc etc.)
    r = session.run("""
        MATCH (sc)-[:POSITIONED_AS]->(target)
        WHERE sc.qid = $seed
        AND (target.dewey IS NOT NULL OR target.lcc IS NOT NULL OR target.lcsh_id IS NOT NULL OR target.fast_id IS NOT NULL OR target.ddc IS NOT NULL)
        RETURN target.qid AS qid, target.label AS label,
               coalesce(target.dewey, target.ddc) AS dewey, target.lcc AS lcc, target.lcsh_id AS lcsh_id, target.fast_id AS fast_id
    """, seed=seed_qid)
    positioned = [dict(row) for row in r]
    return {
        "discipline_with_authority": discipline_count,
        "discipline_sample": disciplines[:5],
        "classification_anchors_with_authority": len(anchors),
        "positioned_targets_with_authority": len(positioned),
        "anchor_sample": anchors[:5],
        "positioned_sample": positioned[:5],
    }


def run_bootstrap(seed_qid: str = "Q17167", json_out: Path | None = None) -> dict:
    """Run bootstrap: load all inputs and return summary."""
    if not GraphDatabase:
        return {"error": "neo4j package not installed", "ready": False}
    if not NEO4J_PASSWORD:
        return {"error": "NEO4J_PASSWORD not set", "ready": False}

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    summary = {
        "seed_qid": seed_qid,
        "inputs": {},
        "ready": True,
        "warnings": [],
    }

    try:
        with driver.session() as session:
            # 1. SYS_
            sys_data = load_sys(session)
            summary["inputs"]["sys"] = sys_data
            if sys_data["count"] == 0:
                summary["warnings"].append("No SYS_Policy nodes found — SFA should load policies at session init")

            # 2. Classification anchors (POSITIONED_AS)
            pos_data = load_positioned_as(session, seed_qid)
            summary["inputs"]["positioned_as"] = pos_data
            if pos_data["count"] == 0:
                summary["warnings"].append(f"No POSITIONED_AS edges for {seed_qid} — run sca_federation_positioning_write")

            # 3. Discipline subgraph
            disc_data = load_discipline_subgraph(session)
            summary["inputs"]["discipline"] = disc_data
            if disc_data["discipline_count"] == 0:
                summary["warnings"].append("No Discipline nodes — run load_discipline_taxonomy")

            # 4. Entity ontology slice
            ent_data = load_entity_ontology_slice(session, seed_qid)
            summary["inputs"]["entity_ontology"] = ent_data
            if ent_data["total_entities"] == 0:
                summary["warnings"].append("No Entity nodes — entity harvest not run")
            elif ent_data["ontology_sample_count"] == 0:
                summary["warnings"].append("No ontology entities (org/event/place) found — check entity_type")

            # 5. Authority anchors (Discipline tree, ClassificationAnchor, POSITIONED_AS targets)
            auth_data = load_authority_anchors(session, seed_qid)
            summary["inputs"]["authority_anchors"] = auth_data
            has_authority = (
                auth_data.get("discipline_with_authority", 0) > 0
                or auth_data.get("classification_anchors_with_authority", 0) > 0
                or auth_data.get("positioned_targets_with_authority", 0) > 0
            )
            if not has_authority:
                summary["warnings"].append("No authority IDs (LCC/LCSH/FAST/Dewey) — run load_discipline_taxonomy or establish OpenAlex/OpenSyllabus/LCC links")

            # Overall readiness
            critical_missing = (
                sys_data["count"] == 0 or
                pos_data["count"] == 0 or
                disc_data["discipline_count"] == 0
            )
            if critical_missing:
                summary["ready"] = False
    finally:
        driver.close()

    if json_out:
        json_out = Path(json_out)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"  Wrote: {json_out}")

    return summary


def print_summary(summary: dict) -> None:
    """Print human-readable summary."""
    if "error" in summary:
        print(f"ERROR: {summary['error']}")
        return

    print("\n" + "=" * 60)
    print("SFA Learning Bootstrap — Dry Run")
    print("=" * 60)
    print(f"Seed: {summary['seed_qid']}")
    print()

    inp = summary.get("inputs", {})
    if "sys" in inp:
        s = inp["sys"]
        print(f"1. SYS_Policy:        {s['count']} policies")
        for p in s.get("policies", [])[:5]:
            print(f"   - {p['name']} (active={p.get('active')})")
        if s["count"] > 5:
            print(f"   ... and {s['count'] - 5} more")
        print()

    if "positioned_as" in inp:
        p = inp["positioned_as"]
        print(f"2. POSITIONED_AS:    {p['count']} targets")
        for t in p.get("targets", [])[:5]:
            print(f"   - {t['qid']} {t['label']} (hops={t.get('hops')}, {t.get('rel_type')})")
        if p["count"] > 5:
            print(f"   ... and {p['count'] - 5} more")
        print()

    if "discipline" in inp:
        d = inp["discipline"]
        print(f"3. Discipline:       {d['discipline_count']} nodes, edges: {d.get('hierarchy_edges', {})}")
        for s in d.get("sample", [])[:5]:
            print(f"   - {s['qid']} {s['label']}")
        if d["discipline_count"] > 5:
            print(f"   ... and {d['discipline_count'] - 5} more")
        print()

    if "entity_ontology" in inp:
        e = inp["entity_ontology"]
        print(f"4. Entity ontology:  {e['total_entities']} total, {e['ontology_sample_count']} in slice")
        print(f"   By type: {e.get('by_type', {})}")
        for s in e.get("ontology_sample", [])[:5]:
            print(f"   - {s['qid']} {s['label']} ({s.get('entity_type')})")
        if e.get("ontology_sample_count", 0) > 5:
            print(f"   ... and {e['ontology_sample_count'] - 5} more")
        print()

    if "authority_anchors" in inp:
        a = inp["authority_anchors"]
        print(f"5. Authority anchors: {a.get('discipline_with_authority', 0)} Discipline (LCC/LCSH/FAST/Dewey), "
              f"{a.get('classification_anchors_with_authority', 0)} ClassificationAnchor, "
              f"{a.get('positioned_targets_with_authority', 0)} positioned targets")
        for s in a.get("discipline_sample", [])[:3]:
            ids = [k for k in ["lcc", "lcsh_id", "fast_id", "dewey"] if s.get(k)]
            print(f"   - {s.get('qid')} {s.get('label', '')[:40]}: {', '.join(ids)}")
        print()

    if summary.get("warnings"):
        print("WARNINGS:")
        for w in summary["warnings"]:
            print(f"  - {w}")
        print()

    ready = summary.get("ready", False)
    print("=" * 60)
    print(f"Ready for SFA learning: {'YES' if ready else 'NO'}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="SFA Learning Bootstrap — load inputs for learning phase (dry-run, no LLM)"
    )
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Run bootstrap only, print summary (default)")
    parser.add_argument("--seed", default="Q17167",
                        help="Seed QID (default: Q17167 Roman Republic)")
    parser.add_argument("--json-out", type=str, default=None,
                        help="Write summary JSON to path")
    args = parser.parse_args()

    if not args.dry_run:
        print("Note: Only --dry-run is implemented. Full learning pass not yet wired.")
        args.dry_run = True

    summary = run_bootstrap(seed_qid=args.seed, json_out=Path(args.json_out) if args.json_out else None)
    print_summary(summary)

    sys.exit(0 if summary.get("ready", False) else 1)


if __name__ == "__main__":
    main()
