#!/usr/bin/env python3
"""
SCA Domain Quality Matrix — backlink density and entity-type profile for a SubjectConcept QID.

Performs real backlink traversal:
- Depth 1: entities that link TO the target QID (via any allowlisted property)
- Depth 2+: for each backlink at depth N, entities that link TO that backlink (recursive)
- Uses single SPARQL query per target (VALUES ?prop) for efficient backlink discovery
- Optional LLM analysis for domain quality interpretation

Usage:
  python scripts/agents/sca_domain_quality_matrix.py --qid Q17167

  python scripts/agents/sca_domain_quality_matrix.py --qid Q17167 \\
      --max-depth 3 --max-backlinks 50

  python scripts/agents/sca_domain_quality_matrix.py --qid Q17167 --analyze

  python scripts/agents/sca_domain_quality_matrix.py --qid Q17167 --write \\
      --neo4j-uri neo4j+s://YOUR_URI --neo4j-password YOUR_PASSWORD

Requires: ANTHROPIC_API_KEY for --analyze
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))

SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Chrystallum/1.0 (SCA domain quality matrix)"
QID_RE = re.compile(r"^Q[1-9]\d*$")
PID_RE = re.compile(r"^P[1-9]\d*$")

# Broad property allowlist for backlink discovery (aligned with wikidata_backlink_harvest)
BACKLINK_PROPERTIES = [
    "P31", "P279", "P361", "P527", "P122", "P1269", "P460",
    "P710", "P1441", "P138", "P112", "P737", "P828",
    "P131", "P17", "P39", "P106", "P921", "P101", "P2578", "P2579",
]


def _wd_uri_to_id(uri: str) -> str:
    if not uri:
        return ""
    tail = uri.rsplit("/", 1)[-1].strip().upper()
    if QID_RE.fullmatch(tail) or PID_RE.fullmatch(tail):
        return tail
    return ""


def _sparql(query: str, timeout_s: int = 60) -> list[dict]:
    r = requests.get(
        SPARQL_URL,
        params={"query": query, "format": "json"},
        headers={"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT},
        timeout=timeout_s,
    )
    r.raise_for_status()
    bindings = r.json().get("results", {}).get("bindings", [])
    out = []
    for row in bindings:
        parsed = {k: v.get("value", "") for k, v in row.items()}
        out.append(parsed)
    return out


def _fetch_backlink_rows(target_qid: str, limit: int, timeout_s: int = 60) -> list[dict]:
    """Fetch all backlinks to target via allowlisted properties (single query)."""
    prop_values = " ".join(f"wdt:{p}" for p in BACKLINK_PROPERTIES)
    query = f"""
SELECT ?source ?sourceLabel ?prop ?p31 ?p31Label WHERE {{
  BIND(wd:{target_qid} AS ?target)
  VALUES ?prop {{ {prop_values} }}
  ?source ?prop ?target .
  OPTIONAL {{ ?source wdt:P31 ?p31 . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT {max(1, limit)}
"""
    return _sparql(query, timeout_s=timeout_s)


def _build_backlink_candidates(rows: list[dict]) -> dict[str, dict]:
    """Aggregate rows into per-source candidates with backlink_hits, properties, p31."""
    candidates: dict[str, dict] = {}
    for row in rows:
        source_qid = _wd_uri_to_id(row.get("source", ""))
        if not QID_RE.fullmatch(source_qid):
            continue
        prop_pid = _wd_uri_to_id(row.get("prop", ""))
        p31_qid = _wd_uri_to_id(row.get("p31", ""))
        source_label = (row.get("sourceLabel") or "").strip()
        p31_label = (row.get("p31Label") or "").strip()

        entry = candidates.setdefault(
            source_qid,
            {
                "qid": source_qid,
                "label": source_label,
                "properties": set(),
                "p31": set(),
                "p31_labels": {},
                "backlink_hits": 0,
            },
        )
        entry["backlink_hits"] += 1
        if source_label and not entry["label"]:
            entry["label"] = source_label
        if PID_RE.fullmatch(prop_pid):
            entry["properties"].add(prop_pid)
        if QID_RE.fullmatch(p31_qid):
            entry["p31"].add(p31_qid)
            if p31_label:
                entry["p31_labels"][p31_qid] = p31_label
    return candidates


def _get_backlinks_for_target(
    target_qid: str,
    limit: int,
    timeout_s: int = 60,
    sleep_ms: int = 300,
) -> list[dict]:
    """Get backlinks to target_qid (single query, all properties). Returns list of backlink dicts."""
    rows = _fetch_backlink_rows(target_qid, limit, timeout_s)
    time.sleep(sleep_ms / 1000.0)
    candidates = _build_backlink_candidates(rows)
    out = []
    for c in sorted(candidates.values(), key=lambda x: (-x["backlink_hits"], -len(x["properties"]), x["qid"])):
        out.append({
            "qid": c["qid"],
            "label": c["label"],
            "via_properties": sorted(c["properties"]),
            "backlink_hits": c["backlink_hits"],
            "p31": sorted(c["p31"]),
            "p31_labels": dict(c["p31_labels"]),
        })
    return out


def _get_p31_values(qids: list[str], timeout_s: int = 60) -> dict[str, list[str]]:
    """Batch fetch P31 (instance of) for QIDs. Returns {qid: [type_qids]}."""
    out: dict[str, list[str]] = defaultdict(list)
    for chunk in [qids[i : i + 50] for i in range(0, len(qids), 50)]:
        ids = " ".join(f"wd:{q}" for q in chunk)
        query = f"""
        SELECT ?item ?type WHERE {{
          VALUES ?item {{ {ids} }}
          ?item wdt:P31 ?type .
        }}
        """
        rows = _sparql(query, timeout_s)
        for r in rows:
            item = _wd_uri_to_id(r.get("item", ""))
            typ = _wd_uri_to_id(r.get("type", ""))
            if item and typ:
                out[item].append(typ)
        time.sleep(0.5)
    return dict(out)


def _get_labels(qids: list[str]) -> dict[str, str]:
    """Fetch labels for QIDs via API."""
    if not qids:
        return {}
    r = requests.get(
        WIKIDATA_API,
        params={
            "action": "wbgetentities",
            "ids": "|".join(qids[:50]),
            "props": "labels",
            "languages": "en",
            "format": "json",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json().get("entities", {})
    return {
        qid: (data.get(qid, {}).get("labels", {}).get("en", {}).get("value") or qid)
        for qid in qids[:50]
    }


def _traverse_backlinks(
    target_qid: str,
    max_depth: int,
    max_backlinks_per_level: int,
    sleep_ms: int = 300,
) -> tuple[list[dict], dict[str, list[dict]], dict[str, int]]:
    """
    Recursive backlink traversal. Returns (all_backlinks, by_depth, by_property).
    - Depth 1: backlinks to target
    - Depth 2: backlinks to each depth-1 backlink
    - Depth N: backlinks to each depth-(N-1) backlink
    """
    all_backlinks: list[dict] = []
    by_depth: dict[str, list[dict]] = defaultdict(list)
    by_property: dict[str, int] = defaultdict(int)
    seen_at_depth: dict[int, set[str]] = {1: set()}

    frontier = [(target_qid, 0, None)]  # (qid, depth, parent_qid)
    visited_targets: set[tuple[str, int]] = set()

    while frontier:
        current_qid, depth, parent_qid = frontier.pop(0)
        if (current_qid, depth) in visited_targets:
            continue
        visited_targets.add((current_qid, depth))

        next_depth = depth + 1
        if next_depth > max_depth:
            continue

        bl_list = _get_backlinks_for_target(
            current_qid,
            limit=max_backlinks_per_level,
            sleep_ms=sleep_ms,
        )

        for b in bl_list:
            b["depth"] = next_depth
            b["target_qid"] = current_qid
            b["parent_qid"] = parent_qid
            for p in b.get("via_properties", []):
                by_property[p] = by_property.get(p, 0) + 1

            key = f"depth_{next_depth}"
            by_depth[key].append(b)
            all_backlinks.append(b)

            if next_depth < max_depth:
                if next_depth not in seen_at_depth:
                    seen_at_depth[next_depth] = set()
                if b["qid"] not in seen_at_depth[next_depth]:
                    seen_at_depth[next_depth].add(b["qid"])
                    frontier.append((b["qid"], next_depth, current_qid))

    return all_backlinks, dict(by_depth), by_property


def build_quality_matrix(
    target_qid: str,
    max_backlinks: int = 50,
    max_depth: int = 1,
    sleep_ms: int = 300,
) -> dict:
    """
    Build domain quality matrix for target QID with real backlink traversal.
    - Depth 1: entities linking TO target (single SPARQL, all properties)
    - Depth 2+: for each backlink at depth N-1, entities linking TO that backlink
    Returns dict with backlinks by depth, by property, entity type distribution.
    """
    all_backlinks, by_depth, by_property = _traverse_backlinks(
        target_qid,
        max_depth=max_depth,
        max_backlinks_per_level=max_backlinks,
        sleep_ms=sleep_ms,
    )

    # Dedupe by qid (keep first occurrence)
    seen = set()
    unique = []
    for b in all_backlinks:
        q = b["qid"]
        if q not in seen:
            seen.add(q)
            unique.append(b)

    qids = [b["qid"] for b in unique]
    p31_map = _get_p31_values(qids)

    type_counts: dict[str, int] = defaultdict(int)
    for b in unique:
        for t in p31_map.get(b["qid"], []):
            type_counts[t] += 1

    # Ensure via_properties is a list for JSON
    for b in unique:
        if "via_properties" not in b:
            b["via_properties"] = []

    matrix = {
        "target_qid": target_qid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "max_backlinks": max_backlinks,
        "max_depth": max_depth,
        "summary": {
            "total_backlinks": len(unique),
            "total_traversal_edges": len(all_backlinks),
            "by_depth": {k: len(v) for k, v in by_depth.items()},
            "by_property": dict(by_property),
            "by_entity_type": dict(type_counts),
        },
        "backlinks": unique[:max_backlinks * 3],
        "by_depth": {k: v[:max_backlinks] for k, v in by_depth.items()},
        "p31_by_qid": dict(p31_map),
    }
    return matrix


def _get_anthropic_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and (_root / ".env").exists():
        for line in (_root / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"')
                break
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment or .env")
    return api_key


def analyze_with_llm(matrix: dict, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024) -> dict:
    """
    Use LLM to interpret the backlink quality matrix and suggest domain quality assessment.
    Returns {assessment, connectivity_score, positioning_suggestions, caveats}.
    """
    try:
        import anthropic
    except ImportError:
        return {"error": "anthropic package required for --analyze. pip install anthropic"}

    summary = matrix.get("summary", {})
    target = matrix.get("target_qid", "")
    by_prop = summary.get("by_property", {})
    by_type = summary.get("by_entity_type", {})
    by_depth = summary.get("by_depth", {})
    total = summary.get("total_backlinks", 0)
    total_edges = summary.get("total_traversal_edges", 0)

    system = """You are a knowledge graph analyst assessing Wikidata SubjectConcept domain quality.
Given backlink traversal data (entities that link TO the target, and optionally backlinks of those backlinks),
interpret the connectivity profile and suggest positioning. Be concise and actionable."""

    user = f"""Target QID: {target}
Backlink summary:
- Total unique backlinks: {total}
- Total traversal edges (including depth): {total_edges}
- By depth: {json.dumps(by_depth)}
- By property (P31=instance of, P279=subclass of, P361=part of, etc.): {json.dumps(by_prop)}
- Top entity types (P31): {json.dumps(dict(sorted(by_type.items(), key=lambda x: -x[1])[:15]))}

Assess:
1. Domain quality: Is this a well-connected hub or sparse? What does the property/type mix suggest?
2. Connectivity score (1-10) with brief justification
3. Positioning suggestions for SCA (Subject Concept Alignment): which facets or LCC/LCSH mappings might fit?
4. Caveats or data quality concerns

Respond with valid JSON only, no markdown:
{{"assessment": "2-3 sentence summary", "connectivity_score": 1-10, "positioning_suggestions": ["suggestion1", "..."], "caveats": ["caveat1", "..."]}}"""

    try:
        client = anthropic.Anthropic(api_key=_get_anthropic_key())
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = msg.content[0].text.strip()
        for prefix in ("```json", "```"):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"LLM response parse error: {e}"}
    except Exception as e:
        return {"error": str(e)}


def write_to_neo4j(
    matrix: dict,
    neo4j_uri: str,
    neo4j_password: str,
    neo4j_user: str = "neo4j",
    database: str = "neo4j",
) -> None:
    """Write quality matrix to Neo4j as DomainQualityRun node."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j required for --write", file=sys.stderr)
        sys.exit(1)

    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    target_qid = matrix["target_qid"]
    summary = matrix["summary"]

    with driver.session(database=database) as session:
        session.run(
            """
            MERGE (r:DomainQualityRun {target_qid: $target_qid})
            SET r.timestamp = $ts,
                r.total_backlinks = $total,
                r.by_property = $by_prop,
                r.by_entity_type = $by_type,
                r.updated_by = 'sca_domain_quality_matrix'
            """,
            target_qid=target_qid,
            ts=matrix["timestamp"],
            total=summary["total_backlinks"],
            by_prop=json.dumps(summary["by_property"]),
            by_type=json.dumps(summary["by_entity_type"]),
        )
        # Link to Entity or SubjectConcept if exists
        session.run(
            """
            MATCH (r:DomainQualityRun {target_qid: $target_qid})
            OPTIONAL MATCH (e:Entity {qid: $target_qid})
            WITH r, e WHERE e IS NOT NULL
            MERGE (e)-[:HAS_QUALITY_RUN]->(r)
            """,
            target_qid=target_qid,
        )
        session.run(
            """
            MATCH (r:DomainQualityRun {target_qid: $target_qid})
            OPTIONAL MATCH (s:SubjectConcept) WHERE s.qid = $target_qid
            WITH r, s WHERE s IS NOT NULL
            MERGE (s)-[:HAS_QUALITY_RUN]->(r)
            """,
            target_qid=target_qid,
        )
    driver.close()
    print(f"  Wrote DomainQualityRun for {target_qid} to Neo4j")


def main() -> int:
    ap = argparse.ArgumentParser(description="SCA Domain Quality Matrix for SubjectConcept QID")
    ap.add_argument("--qid", required=True, help="Target QID (e.g. Q17167)")
    ap.add_argument("--max-depth", type=int, default=1, help="Max traversal depth (default 1)")
    ap.add_argument("--max-backlinks", type=int, default=50, help="Max backlinks per level (default 50)")
    ap.add_argument("--analyze", action="store_true", help="Run LLM analysis on backlink profile (requires ANTHROPIC_API_KEY)")
    ap.add_argument("--write", action="store_true", help="Write to Neo4j")
    ap.add_argument("--neo4j-uri", default=None)
    ap.add_argument("--neo4j-password", default=None)
    ap.add_argument("--output", "-o", default=None, help="JSON output path")
    args = ap.parse_args()

    qid = args.qid.strip().upper()
    if not qid.startswith("Q") or not qid[1:].isdigit():
        print("Invalid QID", file=sys.stderr)
        return 1

    print(f"Building domain quality matrix for {qid}...")
    print(f"  max_depth={args.max_depth}, max_backlinks={args.max_backlinks}")
    matrix = build_quality_matrix(qid, max_backlinks=args.max_backlinks, max_depth=args.max_depth)

    summary = matrix["summary"]
    print(f"\nSummary:")
    print(f"  Total backlinks: {summary['total_backlinks']}")
    print(f"  Total traversal edges: {summary.get('total_traversal_edges', summary['total_backlinks'])}")
    if summary.get("by_depth"):
        print(f"  By depth: {summary['by_depth']}")
    print(f"  By property: {summary['by_property']}")
    print(f"  Top entity types: {dict(sorted(summary['by_entity_type'].items(), key=lambda x: -x[1])[:10])}")

    if args.analyze:
        print("\nRunning LLM analysis...")
        llm_result = analyze_with_llm(matrix)
        if "error" in llm_result:
            print(f"  LLM error: {llm_result['error']}", file=sys.stderr)
        else:
            print(f"\nLLM assessment:")
            print(f"  {llm_result.get('assessment', '')}")
            print(f"  Connectivity score: {llm_result.get('connectivity_score', 'N/A')}")
            print(f"  Positioning: {llm_result.get('positioning_suggestions', [])}")
            print(f"  Caveats: {llm_result.get('caveats', [])}")
            matrix["llm_analysis"] = llm_result

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
        print(f"\nWrote {out_path}")

    if args.write:
        neo4j_uri = args.neo4j_uri
        neo4j_pw = args.neo4j_password
        if not neo4j_uri or not neo4j_pw:
            try:
                from config_loader import NEO4J_URI, NEO4J_PASSWORD
                neo4j_uri = neo4j_uri or NEO4J_URI
                neo4j_pw = neo4j_pw or NEO4J_PASSWORD
            except ImportError:
                pass
            if not neo4j_uri or not neo4j_pw:
                try:
                    from dotenv import load_dotenv
                    import os
                    load_dotenv(_root / ".env")
                    neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI")
                    neo4j_pw = neo4j_pw or os.getenv("NEO4J_PASSWORD")
                except ImportError:
                    pass
        if not neo4j_uri or not neo4j_pw:
            print("--neo4j-uri and --neo4j-password required for --write (or set in .env)", file=sys.stderr)
            return 1
        write_to_neo4j(matrix, neo4j_uri, neo4j_pw)

    return 0


if __name__ == "__main__":
    sys.exit(main())
