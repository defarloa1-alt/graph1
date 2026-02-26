#!/usr/bin/env python3
"""
SCA Salience: Cold-Start Top Doors

Ranks SubjectConcepts as entry points for progressive disclosure.
Implements base_score + path_coherence (context_affinity=0 for cold start).

Read-back principle: The graph is the source of truth. Before scoring, reads
entity_count and harvest_status from Neo4j. Falls back to JSON when Neo4j
unavailable.

Usage:
    python scripts/backbone/subject/sca_salience_doors.py
    python scripts/backbone/subject/sca_salience_doors.py --root Q17167 --doors 5 --output output/analysis/sca_top_doors.json
    python scripts/backbone/subject/sca_salience_doors.py --no-neo4j   # Force JSON fallback
"""
import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None


CONFIDENCE_WEIGHTS = {
    "root": 1.00,
    "curated": 0.90,
    "llm:1.00": 0.80,
    "llm:0.95": 0.75,
    "llm:0.90": 0.70,
    "llm:0.85": 0.65,
    "llm:0.75": 0.55,
}


def load_anchors(path: Path) -> dict[str, dict]:
    """Load anchors as qid -> {label, confidence, primary_facet}."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    items = raw.get("anchors", raw) if isinstance(raw, dict) else raw
    return {
        a["qid"]: {
            "label": a.get("label", a.get("qid", "")),
            "confidence": a.get("confidence", a.get("source", "unknown")),
            "primary_facet": a.get("primary_facet", ""),
        }
        for a in items
        if a.get("qid")
    }


def load_hierarchy(path: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Return (child->parents, parent->children) and compute depth from root."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    edges = data.get("broader_than", data.get("edges", []))
    parents: dict[str, list[str]] = defaultdict(list)
    children: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        c = e.get("child_qid") or e.get("child")
        p = e.get("parent_qid") or e.get("parent")
        if c and p:
            parents[c].append(p)
            children[p].append(c)
    return dict(parents), dict(children)


def compute_depth(root_qid: str, parents: dict, children: dict) -> dict[str, int]:
    """BFS from root to assign depth. Root=0, direct children=1, etc."""
    depth = {root_qid: 0}
    queue = [root_qid]
    while queue:
        n = queue.pop(0)
        d = depth[n]
        for c in children.get(n, []):
            if c not in depth:
                depth[c] = d + 1
                queue.append(c)
    return depth


def load_entity_counts(edges_path: Path) -> dict[str, int]:
    """Count entities per subject_qid from member_of_edges.json."""
    with open(edges_path, encoding="utf-8") as f:
        edges = json.load(f)
    counts: dict[str, int] = defaultdict(int)
    for e in edges:
        qid = e.get("subject_qid") or e.get("anchor_qid")
        if qid:
            counts[qid] += 1
    return dict(counts)


def load_entity_counts_scoped(edges_path: Path) -> dict[str, int]:
    """Count only scoped entities (exclude unscoped). Use for noise-heavy clusters like Q7188."""
    with open(edges_path, encoding="utf-8") as f:
        edges = json.load(f)
    counts: dict[str, int] = defaultdict(int)
    for e in edges:
        status = e.get("scoping_status", "")
        if status == "unscoped":
            continue
        qid = e.get("subject_qid") or e.get("anchor_qid")
        if qid:
            counts[qid] += 1
    return dict(counts)


def load_harvest_status(progress_path: Path) -> set[str]:
    """Return set of QIDs with confirmed harvest."""
    if not progress_path.exists():
        return set()
    with open(progress_path, encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("completed", []))


def enrich_from_neo4j(
    uri: str,
    user: str,
    password: str,
    use_scoped_counts: bool = False,
) -> tuple[dict[str, int], set[str]] | None:
    """
    Read entity_count and harvest_status from Neo4j. Graph is source of truth.
    Returns (entity_counts, harvest_confirmed) or None if Neo4j unavailable.
    De facto confirmation: entity_count > 0 from MEMBER_OF edges counts as confirmed.
    use_scoped_counts: exclude unscoped entities (temporal_scoped, domain_scoped, or legacy only).
    """
    if not GraphDatabase or not uri or not password:
        return None
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            if use_scoped_counts:
                query = """
                MATCH (sc:SubjectConcept)
                OPTIONAL MATCH (e:Entity)-[r:MEMBER_OF]->(sc)
                WITH sc, e, r
                WHERE r IS NULL OR r.scoping_status IS NULL OR r.scoping_status <> 'unscoped'
                WITH sc, count(e) AS entity_count
                RETURN sc.qid AS qid,
                       coalesce(sc.harvest_status, '') AS harvest_status,
                       entity_count
                """
            else:
                query = """
                MATCH (sc:SubjectConcept)
                OPTIONAL MATCH (e:Entity)-[:MEMBER_OF]->(sc)
                WITH sc, count(e) AS entity_count
                RETURN sc.qid AS qid,
                       coalesce(sc.harvest_status, '') AS harvest_status,
                       entity_count
                """
            result = session.run(query)
            entity_counts: dict[str, int] = {}
            harvest_confirmed: set[str] = set()
            for record in result:
                qid = record.get("qid")
                if not qid:
                    continue
                ec = record.get("entity_count", 0) or 0
                entity_counts[qid] = ec
                status = (record.get("harvest_status") or "").strip().lower()
                if status == "confirmed" or ec > 0:
                    harvest_confirmed.add(qid)
        driver.close()
        return entity_counts, harvest_confirmed
    except Exception:
        return None


def base_score(
    sc_qid: str,
    entity_count: int,
    confidence: str,
    harvest_confirmed: bool,
    depth: int,
) -> float:
    """Base salience score (0–1 range)."""
    score = 0.0
    # Entity density (cap at 100)
    score += min(entity_count / 100, 1.0) * 0.35
    # Confidence
    conf_val = CONFIDENCE_WEIGHTS.get(confidence, 0.5)
    score += conf_val * 0.25
    # Harvest confirmation
    score += 0.20 if harvest_confirmed else 0.0
    # Depth penalty
    depth_penalty = min(max(0, depth - 1) * 0.08, 0.25)
    score -= depth_penalty
    return max(0, score)


def load_narrative_paths(path: Path | None) -> list[list[str]]:
    """Load curated narrative paths. Returns list of [qid, qid, ...] sequences."""
    if not path or not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        paths = data.get("paths", [])
        return [p["path"] for p in paths if isinstance(p.get("path"), list) and p["path"]]
    except (json.JSONDecodeError, KeyError):
        return []


def path_coherence(
    sc_qid: str,
    children: dict[str, list[str]],
    entity_counts: dict[str, int],
    harvest_confirmed: set[str],
    narrative_paths: list[list[str]] | None = None,
    min_entities: int = 5,
) -> float:
    """Score how many viable onward paths exist behind this door."""
    child_qids = children.get(sc_qid, [])
    viable = [
        c for c in child_qids
        if entity_counts.get(c, 0) >= min_entities and c in harvest_confirmed
    ]
    coherence = min(len(viable) / 5, 1.0) * 0.5
    # Cross-facet: nodes with multiple parents (simplified: just count children)
    coherence += min(len(child_qids) / 5, 1.0) * 0.5
    structural = coherence * 0.25

    # Narrative boost: doors that start curated paths get higher coherence
    narrative_boost = 0.0
    if narrative_paths:
        paths_starting_here = sum(1 for p in narrative_paths if p and p[0] == sc_qid)
        narrative_boost = 0.05 * min(paths_starting_here, 3)  # up to 0.15

    return structural + narrative_boost


def select_doors(
    candidates: list[tuple[str, float]],
    anchors: dict[str, dict],
    n: int,
) -> list[dict]:
    """Select top n with facet diversity."""
    selected: list[dict] = []
    used_facets: set[str] = set()
    for sc_qid, score in candidates:
        facet = (anchors.get(sc_qid) or {}).get("primary_facet", "")
        if facet not in used_facets or len(selected) < n:
            selected.append({
                "qid": sc_qid,
                "label": (anchors.get(sc_qid) or {}).get("label", sc_qid),
                "primary_facet": facet,
                "score": round(score, 4),
            })
            if facet:
                used_facets.add(facet)
        if len(selected) == n:
            break
    return selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="Q17167", help="Root SubjectConcept QID")
    parser.add_argument("--doors", type=int, default=3, help="Number of top doors")
    parser.add_argument(
        "--anchors",
        default="output/subject_concepts/subject_concept_anchors_qid_canonical.json",
        help="Anchors JSON",
    )
    parser.add_argument(
        "--hierarchy",
        default="output/subject_concepts/subject_concept_hierarchy.json",
        help="Hierarchy JSON",
    )
    parser.add_argument(
        "--edges",
        default="output/cluster_assignment/member_of_edges.json",
        help="member_of_edges.json",
    )
    parser.add_argument(
        "--harvest-progress",
        default="output/backlinks/harvest_progress.json",
        help="harvest_progress.json for confirmed status",
    )
    parser.add_argument(
        "--output",
        default="output/analysis/sca_top_doors.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--no-neo4j",
        action="store_true",
        help="Skip Neo4j read-back; use JSON only (pipeline artifacts)",
    )
    parser.add_argument(
        "--narrative-paths",
        default="output/subject_concepts/narrative_paths.json",
        help="Curated narrative paths JSON (boosts doors that start paths)",
    )
    parser.add_argument(
        "--min-entities",
        type=int,
        default=10,
        help="Minimum entity count to offer as door (default 10; under this = structurally present but not navigable)",
    )
    parser.add_argument(
        "--use-scoped-counts",
        action="store_true",
        help="Count only scoped entities (exclude unscoped); use for noise-heavy clusters like Q7188",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    anchors_path = root / args.anchors
    hierarchy_path = root / args.hierarchy
    edges_path = root / args.edges
    progress_path = root / args.harvest_progress
    narrative_paths_path = root / args.narrative_paths

    # Load .env for Neo4j config
    try:
        from dotenv import load_dotenv
        load_dotenv(root / ".env")
    except ImportError:
        pass

    anchors = load_anchors(anchors_path)
    parents, children = load_hierarchy(hierarchy_path)
    depth_map = compute_depth(args.root, parents, children)

    # Read-back: Neo4j is source of truth when available
    entity_counts: dict[str, int] = {}
    harvest_confirmed: set[str] = set()
    data_source = "json"

    if not args.no_neo4j and GraphDatabase:
        uri = os.getenv("NEO4J_URI", "")
        user = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        neo4j_data = enrich_from_neo4j(uri, user, password, use_scoped_counts=args.use_scoped_counts)
        if neo4j_data:
            entity_counts, harvest_confirmed = neo4j_data
            data_source = "neo4j"

    if data_source == "json":
        loader = load_entity_counts_scoped if args.use_scoped_counts else load_entity_counts
        entity_counts = loader(edges_path) if edges_path.exists() else {}
        harvest_confirmed = load_harvest_status(progress_path)

    narrative_paths = load_narrative_paths(narrative_paths_path)

    # Candidates: direct children of root (depth 1)
    candidate_qids = children.get(args.root, [])
    if not candidate_qids:
        # Root might have no children in hierarchy; use all depth-1 from anchors
        candidate_qids = [q for q, d in depth_map.items() if d == 1 and q != args.root]

    # Filter: under min_entities = structurally present but not yet navigable
    candidate_qids = [q for q in candidate_qids if entity_counts.get(q, 0) >= args.min_entities]

    scored: list[tuple[str, float]] = []
    for qid in candidate_qids:
        ec = entity_counts.get(qid, 0)
        conf = (anchors.get(qid) or {}).get("confidence", "unknown")
        confirmed = qid in harvest_confirmed
        d = depth_map.get(qid, 1)
        bs = base_score(qid, ec, conf, confirmed, d)
        pc = path_coherence(qid, children, entity_counts, harvest_confirmed, narrative_paths)
        total = bs + pc
        scored.append((qid, total))

    scored.sort(key=lambda x: -x[1])
    doors = select_doors(scored[: max(args.doors * 2, 6)], anchors, args.doors)

    report = {
        "root_qid": args.root,
        "n_doors": args.doors,
        "doors": doors,
        "candidates_scored": len(scored),
        "min_entities_threshold": args.min_entities,
        "use_scoped_counts": args.use_scoped_counts,
        "entity_counts_available": bool(entity_counts),
        "data_source": data_source,
        "narrative_paths_loaded": len(narrative_paths),
    }

    out_path = root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=" * 60)
    print("SCA SALIENCE: COLD-START TOP DOORS")
    print("=" * 60)
    print(f"Root: {args.root}  |  Top {args.doors} doors  |  Data: {data_source}")
    print("-" * 60)
    for i, d in enumerate(doors, 1):
        print(f"  {i}. {d['qid']}  score={d['score']:.3f}  [{d['primary_facet']}]")
        print(f"     {d['label'][:55]}")
    print("-" * 60)
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
