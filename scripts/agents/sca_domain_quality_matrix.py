#!/usr/bin/env python3
"""
SCA Domain Quality Matrix Builder

Given a Wikidata QID representing a domain (e.g., Q17167 = Roman Republic),
walk the ontological neighbourhood:

  1. Fetch P31 (instance of) targets → class anchors
  2. For each class anchor, follow P279 (subclass of) chains upward
  3. For each class anchor, follow P527 (has parts) chains downward
  4. At each level, harvest backlinks and score quality from Chrystallum perspective

Output: a quality matrix (CSV + JSON) showing for each node:
  - depth, traversal path, backlink counts, quality signals,
    authority coverage (LCSH, LCC, Dewey, FAST), entity-type distribution

Usage:
  # Dry run (no Neo4j, just Wikidata SPARQL)
  python scripts/agents/sca_domain_quality_matrix.py --qid Q17167

  # With depth/budget controls
  python scripts/agents/sca_domain_quality_matrix.py --qid Q17167 \\
      --max-depth 3 --max-backlinks 50 --output-dir output/domain_matrix

  # Write matrix to Neo4j as DomainQualityProbe nodes
  python scripts/agents/sca_domain_quality_matrix.py --qid Q17167 --write \\
      --neo4j-uri neo4j+s://YOUR_URI --neo4j-password YOUR_PASSWORD
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import requests


# ── Constants ─────────────────────────────────────────────────────────────────

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "Chrystallum/1.0 (research project)"
SPARQL_TIMEOUT_S = 30

# Traversal properties — the ontological skeleton
TRAVERSAL_PROPERTIES = {
    "P31":  {"label": "instance of",  "direction": "up",   "phase": "anchor"},
    "P279": {"label": "subclass of",  "direction": "up",   "phase": "chain"},
    "P527": {"label": "has parts",    "direction": "down", "phase": "chain"},
    "P361": {"label": "part of",      "direction": "up",   "phase": "chain"},
}

# Authority properties checked on each visited node
AUTHORITY_PROPERTIES = {
    "P244":  "lcsh_id",
    "P1036": "dewey",
    "P1149": "lcc",
    "P2163": "fast_id",
    "P227":  "gnd_id",
}

# Backlink quality signals — properties that indicate domain-relevant inbound links
BACKLINK_SIGNAL_PROPERTIES = [
    "P31",   # instance of  (entities typed as this concept)
    "P279",  # subclass of  (children)
    "P361",  # part of      (components claiming membership)
    "P527",  # has part      (containers)
    "P710",  # participant   (events referencing this)
    "P17",   # country       (geo-political)
    "P131",  # located in    (spatial)
    "P921",  # main subject  (scholarly works about)
]

# Known Wikimedia administrative noise — skip these
P31_DENYLIST = frozenset([
    "Q4167836",   # Wikimedia category
    "Q11266439",  # Wikimedia template
    "Q4167410",   # Wikimedia disambiguation page
    "Q13406463",  # Wikimedia list article
])


# ── SPARQL helpers ────────────────────────────────────────────────────────────

def _sparql_get(query: str, retries: int = 3) -> List[Dict]:
    """Execute SPARQL query against Wikidata with retry/rate-limit handling."""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": USER_AGENT,
    }
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(
                SPARQL_URL,
                params={"query": query},
                headers=headers,
                timeout=SPARQL_TIMEOUT_S,
            )
            resp.raise_for_status()
            return resp.json().get("results", {}).get("bindings", [])
        except requests.exceptions.HTTPError:
            if resp.status_code == 429:
                wait = 5 * attempt
                print(f"  [rate-limit] waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
        except requests.exceptions.RequestException as e:
            if attempt < retries:
                print(f"  [warn] SPARQL attempt {attempt} failed: {e}. Retrying...")
                time.sleep(3)
            else:
                raise
    return []


def _qid(uri: str) -> str:
    """Extract QID from Wikidata URI."""
    return uri.split("/")[-1]


# ── Phase 1: Seed resolution ─────────────────────────────────────────────────

def resolve_seed(qid: str) -> Dict:
    """Fetch label, description, and P31 targets for the seed QID."""
    auth_optionals = "\n".join(
        f"  OPTIONAL {{ wd:{qid} wdt:{pid} ?{name}. }}"
        for pid, name in AUTHORITY_PROPERTIES.items()
    )
    query = f"""
SELECT ?label ?description ?instanceOf ?instanceOfLabel
       ?lcsh_id ?dewey ?lcc ?fast_id ?gnd_id
WHERE {{
  wd:{qid} rdfs:label ?label . FILTER(LANG(?label) = "en")
  OPTIONAL {{ wd:{qid} schema:description ?description .
              FILTER(LANG(?description) = "en") }}
  OPTIONAL {{ wd:{qid} wdt:P31 ?instanceOf .
              SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "en".
                ?instanceOf rdfs:label ?instanceOfLabel.
              }}
           }}
{auth_optionals}
}}
"""
    rows = _sparql_get(query)
    if not rows:
        print(f"  [error] No data for {qid}")
        return {"qid": qid, "label": qid, "p31_targets": []}

    label = rows[0].get("label", {}).get("value", qid)
    description = rows[0].get("description", {}).get("value", "")

    # Collect P31 targets (deduplicated)
    p31_targets = {}
    for row in rows:
        io = row.get("instanceOf", {}).get("value")
        if io:
            tqid = _qid(io)
            if tqid not in p31_targets:
                p31_targets[tqid] = row.get("instanceOfLabel", {}).get("value", tqid)

    # Authority IDs from first row
    authorities = {}
    for name in AUTHORITY_PROPERTIES.values():
        val = rows[0].get(name, {}).get("value")
        if val:
            authorities[name] = val

    return {
        "qid": qid,
        "label": label,
        "description": description,
        "p31_targets": [{"qid": q, "label": l} for q, l in p31_targets.items()],
        "authorities": authorities,
    }


# ── Phase 2: Chain walker (P279 up, P527 down) ──────────────────────────────

def walk_chains(
    start_qid: str,
    start_label: str,
    max_depth: int = 3,
) -> List[Dict]:
    """
    BFS walk from a class anchor following P279 (up) and P527 (down).
    Returns list of visited nodes with depth and traversal path.
    """
    visited: Set[str] = set()
    queue: deque = deque()
    results: List[Dict] = []

    # Seed the queue with the starting node
    queue.append({
        "qid": start_qid,
        "label": start_label,
        "depth": 0,
        "path": [start_qid],
        "via_property": "P31",  # how we got here from domain root
    })

    while queue:
        node = queue.popleft()
        nqid = node["qid"]

        if nqid in visited:
            continue
        visited.add(nqid)

        # Fetch this node's upward (P279) and downward (P527) neighbours + authorities
        neighbours = _fetch_neighbours(nqid)
        node["authorities"] = neighbours.get("authorities", {})
        node["p279_targets"] = neighbours.get("P279", [])
        node["p527_targets"] = neighbours.get("P527", [])
        node["p361_targets"] = neighbours.get("P361", [])
        results.append(node)

        if node["depth"] >= max_depth:
            continue

        # Queue neighbours
        for prop_id in ("P279", "P527", "P361"):
            for target in neighbours.get(prop_id, []):
                if target["qid"] not in visited:
                    queue.append({
                        "qid": target["qid"],
                        "label": target["label"],
                        "depth": node["depth"] + 1,
                        "path": node["path"] + [target["qid"]],
                        "via_property": prop_id,
                    })

    return results


def _fetch_neighbours(qid: str) -> Dict:
    """Fetch P279, P527, P361 targets and authority IDs for a single QID."""
    auth_optionals = "\n".join(
        f"  OPTIONAL {{ wd:{qid} wdt:{pid} ?{name}. }}"
        for pid, name in AUTHORITY_PROPERTIES.items()
    )

    query = f"""
SELECT ?prop ?target ?targetLabel
       ?lcsh_id ?dewey ?lcc ?fast_id ?gnd_id
WHERE {{
  VALUES ?prop {{ wdt:P279 wdt:P527 wdt:P361 }}
  wd:{qid} ?prop ?target .
  FILTER(STRSTARTS(STR(?target), "http://www.wikidata.org/entity/Q"))
{auth_optionals}
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en".
    ?target rdfs:label ?targetLabel.
  }}
}}
"""
    rows = _sparql_get(query)
    time.sleep(0.5)  # be polite

    result: Dict[str, Any] = {"P279": [], "P527": [], "P361": [], "authorities": {}}

    # Parse authority IDs from first row
    if rows:
        for name in AUTHORITY_PROPERTIES.values():
            val = rows[0].get(name, {}).get("value")
            if val:
                result["authorities"][name] = val

    seen: Set[Tuple[str, str]] = set()
    for row in rows:
        prop_uri = row.get("prop", {}).get("value", "")
        target_uri = row.get("target", {}).get("value", "")
        if not target_uri:
            continue

        pid = prop_uri.split("/")[-1].replace("direct/", "")
        tqid = _qid(target_uri)
        key = (pid, tqid)
        if key in seen:
            continue
        seen.add(key)

        if pid in result:
            result[pid].append({
                "qid": tqid,
                "label": row.get("targetLabel", {}).get("value", tqid),
            })

    return result


# ── Phase 3: Backlink quality probe ──────────────────────────────────────────

def probe_backlinks(
    qid: str,
    max_backlinks: int = 50,
) -> Dict:
    """
    For a visited node, probe inbound links across BACKLINK_SIGNAL_PROPERTIES.
    Returns counts and entity-type distribution of backlinkers.
    """
    prop_values = " ".join(f"wdt:{p}" for p in BACKLINK_SIGNAL_PROPERTIES)

    query = f"""
SELECT ?prop ?source ?sourceLabel ?sourceType ?sourceTypeLabel
WHERE {{
  VALUES ?prop {{ {prop_values} }}
  ?source ?prop wd:{qid} .
  OPTIONAL {{ ?source wdt:P31 ?sourceType . }}
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en".
    ?source rdfs:label ?sourceLabel.
    ?sourceType rdfs:label ?sourceTypeLabel.
  }}
}}
LIMIT {max_backlinks}
"""
    rows = _sparql_get(query)
    time.sleep(0.5)

    by_property: Dict[str, int] = Counter()
    entity_types: Dict[str, int] = Counter()
    sources_seen: Set[str] = set()
    noise_count = 0

    for row in rows:
        prop_uri = row.get("prop", {}).get("value", "")
        source_uri = row.get("source", {}).get("value", "")
        source_type_uri = row.get("sourceType", {}).get("value", "")

        pid = prop_uri.split("/")[-1].replace("direct/", "")
        source_qid = _qid(source_uri)
        type_qid = _qid(source_type_uri) if source_type_uri else None

        # Filter Wikimedia noise
        if type_qid and type_qid in P31_DENYLIST:
            noise_count += 1
            continue

        by_property[pid] += 1
        sources_seen.add(source_qid)

        if type_qid:
            type_label = row.get("sourceTypeLabel", {}).get("value", type_qid)
            entity_types[f"{type_qid}:{type_label}"] += 1

    return {
        "total_backlinks": len(sources_seen),
        "noise_filtered": noise_count,
        "by_property": dict(by_property),
        "entity_type_distribution": dict(entity_types.most_common(20)),
        "hit_limit": len(rows) >= max_backlinks,
    }


# ── Phase 4: Quality scoring ─────────────────────────────────────────────────

def score_node(node: Dict, backlinks: Dict) -> Dict:
    """
    Score a node from Chrystallum system perspective.

    Dimensions:
      authority_coverage: how many of 5 authority IDs are present (0.0–1.0)
      backlink_density:   normalised backlink count (capped at 1.0)
      type_diversity:     Shannon-like diversity of entity types (0.0–1.0)
      property_spread:    fraction of signal properties with ≥1 backlink
      composite:          weighted combination
    """
    # Authority coverage (0–1)
    auth_count = len(node.get("authorities", {}))
    authority_coverage = auth_count / len(AUTHORITY_PROPERTIES)

    # Backlink density (normalised, cap at 100)
    total_bl = backlinks.get("total_backlinks", 0)
    backlink_density = min(total_bl / 100.0, 1.0)

    # Type diversity (unique types / total backlinks, capped)
    type_dist = backlinks.get("entity_type_distribution", {})
    n_types = len(type_dist)
    type_diversity = min(n_types / 10.0, 1.0) if total_bl > 0 else 0.0

    # Property spread
    by_prop = backlinks.get("by_property", {})
    property_spread = len(by_prop) / len(BACKLINK_SIGNAL_PROPERTIES) if BACKLINK_SIGNAL_PROPERTIES else 0.0

    # Composite (weighted)
    composite = (
        0.25 * authority_coverage
        + 0.30 * backlink_density
        + 0.20 * type_diversity
        + 0.25 * property_spread
    )

    return {
        "authority_coverage": round(authority_coverage, 3),
        "backlink_density": round(backlink_density, 3),
        "type_diversity": round(type_diversity, 3),
        "property_spread": round(property_spread, 3),
        "composite": round(composite, 3),
    }


# ── Orchestrator ──────────────────────────────────────────────────────────────

def build_domain_quality_matrix(
    domain_qid: str,
    max_depth: int = 3,
    max_backlinks: int = 50,
    output_dir: Optional[str] = None,
) -> Dict:
    """
    Full pipeline: seed → anchor classes → chain walk → backlink probe → score.
    Returns the complete matrix as a dict and writes CSV + JSON.
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print("=" * 80)
    print(f"DOMAIN QUALITY MATRIX — {domain_qid}")
    print(f"  max_depth={max_depth}  max_backlinks={max_backlinks}")
    print("=" * 80)

    # ── Step 1: Resolve seed ──
    print(f"\n[1/4] Resolving seed {domain_qid}...")
    seed = resolve_seed(domain_qid)
    print(f"  Label: {seed['label']}")
    print(f"  P31 anchors: {len(seed['p31_targets'])}")
    for t in seed["p31_targets"]:
        print(f"    → {t['qid']} ({t['label']})")

    # ── Step 2: Walk chains from each P31 anchor ──
    print(f"\n[2/4] Walking ontological chains (depth {max_depth})...")
    all_chain_nodes: List[Dict] = []

    # Include the seed itself as depth -1
    seed_node = {
        "qid": domain_qid,
        "label": seed["label"],
        "depth": -1,
        "path": [domain_qid],
        "via_property": "SEED",
        "authorities": seed.get("authorities", {}),
        "anchor_source": "SELF",
    }
    all_chain_nodes.append(seed_node)

    visited_globally: Set[str] = {domain_qid}
    for anchor in seed["p31_targets"]:
        print(f"\n  Chain from anchor: {anchor['qid']} ({anchor['label']})")
        chain_nodes = walk_chains(anchor["qid"], anchor["label"], max_depth)
        for cn in chain_nodes:
            cn["anchor_source"] = anchor["qid"]
            if cn["qid"] not in visited_globally:
                visited_globally.add(cn["qid"])
                all_chain_nodes.append(cn)

    print(f"\n  Total unique nodes in chains: {len(all_chain_nodes)}")

    # ── Step 3: Probe backlinks at each node ──
    print(f"\n[3/4] Probing backlinks at each node...")
    matrix_rows: List[Dict] = []

    for i, node in enumerate(all_chain_nodes):
        print(f"  [{i+1}/{len(all_chain_nodes)}] {node['qid']} ({node['label']})  depth={node['depth']}")
        bl = probe_backlinks(node["qid"], max_backlinks)
        scores = score_node(node, bl)

        row = {
            "qid": node["qid"],
            "label": node["label"],
            "depth": node["depth"],
            "via_property": node.get("via_property", ""),
            "anchor_source": node.get("anchor_source", ""),
            "path": " → ".join(node.get("path", [])),
            # Authority coverage
            "has_lcsh": "lcsh_id" in node.get("authorities", {}),
            "has_lcc": "lcc" in node.get("authorities", {}),
            "has_dewey": "dewey" in node.get("authorities", {}),
            "has_fast": "fast_id" in node.get("authorities", {}),
            "has_gnd": "gnd_id" in node.get("authorities", {}),
            # Backlink signals
            "backlink_total": bl["total_backlinks"],
            "backlink_noise_filtered": bl["noise_filtered"],
            "backlink_hit_limit": bl["hit_limit"],
            "backlink_by_property": bl["by_property"],
            "entity_type_distribution": bl["entity_type_distribution"],
            # Quality scores
            **scores,
        }
        matrix_rows.append(row)

    # ── Step 4: Sort by composite score and emit ──
    matrix_rows.sort(key=lambda r: r["composite"], reverse=True)

    print(f"\n[4/4] Quality matrix complete — {len(matrix_rows)} nodes scored")

    # Summary
    print("\n" + "=" * 80)
    print("QUALITY MATRIX SUMMARY")
    print("=" * 80)
    print(f"{'QID':<12} {'Label':<35} {'Depth':>5} {'BL':>5} {'Auth':>5} {'Composite':>9}")
    print("-" * 80)
    for row in matrix_rows[:30]:
        print(
            f"{row['qid']:<12} {row['label'][:34]:<35} "
            f"{row['depth']:>5} {row['backlink_total']:>5} "
            f"{row['authority_coverage']:>5.2f} {row['composite']:>9.3f}"
        )
    if len(matrix_rows) > 30:
        print(f"  ... and {len(matrix_rows) - 30} more rows")

    # ── Output ──
    out_dir = Path(output_dir or f"output/domain_matrix/{domain_qid}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # JSON (full detail)
    json_path = out_dir / f"quality_matrix_{domain_qid}_{ts}.json"
    report = {
        "domain_qid": domain_qid,
        "domain_label": seed["label"],
        "generated_at": ts,
        "parameters": {
            "max_depth": max_depth,
            "max_backlinks": max_backlinks,
        },
        "seed": seed,
        "matrix": matrix_rows,
        "summary": {
            "total_nodes": len(matrix_rows),
            "avg_composite": round(sum(r["composite"] for r in matrix_rows) / len(matrix_rows), 3) if matrix_rows else 0,
            "nodes_with_lcsh": sum(1 for r in matrix_rows if r["has_lcsh"]),
            "nodes_with_backlinks": sum(1 for r in matrix_rows if r["backlink_total"] > 0),
        },
    }
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n  JSON → {json_path}")

    # CSV (flat, analysis-ready)
    csv_path = out_dir / f"quality_matrix_{domain_qid}_{ts}.csv"
    csv_fields = [
        "qid", "label", "depth", "via_property", "anchor_source", "path",
        "has_lcsh", "has_lcc", "has_dewey", "has_fast", "has_gnd",
        "backlink_total", "backlink_noise_filtered", "backlink_hit_limit",
        "authority_coverage", "backlink_density", "type_diversity",
        "property_spread", "composite",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(matrix_rows)
    print(f"  CSV  → {csv_path}")

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build domain quality matrix from a Wikidata QID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--qid", required=True, help="Wikidata QID for domain root (e.g., Q17167)")
    parser.add_argument("--max-depth", type=int, default=3, help="Max traversal depth (default 3)")
    parser.add_argument("--max-backlinks", type=int, default=50, help="Max backlinks to probe per node (default 50)")
    parser.add_argument("--output-dir", help="Output directory (default: output/domain_matrix/<QID>)")
    parser.add_argument("--write", action="store_true", help="Write results to Neo4j")
    parser.add_argument("--neo4j-uri", help="Neo4j URI")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j user")
    parser.add_argument("--neo4j-password", help="Neo4j password")

    args = parser.parse_args()

    # Normalise QID
    qid = args.qid.upper()
    if not qid.startswith("Q"):
        qid = f"Q{qid}"

    report = build_domain_quality_matrix(
        domain_qid=qid,
        max_depth=args.max_depth,
        max_backlinks=args.max_backlinks,
        output_dir=args.output_dir,
    )

    if args.write:
        if not args.neo4j_uri or not args.neo4j_password:
            print("\n[error] --neo4j-uri and --neo4j-password required with --write")
            sys.exit(1)
        _write_to_neo4j(report, args.neo4j_uri, args.neo4j_user, args.neo4j_password)


def _write_to_neo4j(report: Dict, uri: str, user: str, password: str):
    """Write quality matrix as DomainQualityProbe nodes linked to SubjectConcept."""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("[error] neo4j driver not installed. pip install neo4j")
        sys.exit(1)

    driver = GraphDatabase.driver(uri, auth=(user, password))
    domain_qid = report["domain_qid"]

    with driver.session() as session:
        for row in report["matrix"]:
            session.run(
                """
                MERGE (p:DomainQualityProbe {qid: $qid, domain_qid: $domain_qid})
                SET p.label = $label,
                    p.depth = $depth,
                    p.via_property = $via_property,
                    p.anchor_source = $anchor_source,
                    p.authority_coverage = $authority_coverage,
                    p.backlink_density = $backlink_density,
                    p.type_diversity = $type_diversity,
                    p.property_spread = $property_spread,
                    p.composite = $composite,
                    p.backlink_total = $backlink_total,
                    p.has_lcsh = $has_lcsh,
                    p.has_lcc = $has_lcc,
                    p.has_dewey = $has_dewey,
                    p.updated_at = datetime()
                WITH p
                MATCH (sc:SubjectConcept {wikidata_qid: $domain_qid})
                MERGE (sc)-[:HAS_QUALITY_PROBE]->(p)
                """,
                qid=row["qid"],
                domain_qid=domain_qid,
                label=row["label"],
                depth=row["depth"],
                via_property=row["via_property"],
                anchor_source=row["anchor_source"],
                authority_coverage=row["authority_coverage"],
                backlink_density=row["backlink_density"],
                type_diversity=row["type_diversity"],
                property_spread=row["property_spread"],
                composite=row["composite"],
                backlink_total=row["backlink_total"],
                has_lcsh=row["has_lcsh"],
                has_lcc=row["has_lcc"],
                has_dewey=row["has_dewey"],
            )

    driver.close()
    print(f"\n  Wrote {len(report['matrix'])} DomainQualityProbe nodes to Neo4j")


if __name__ == "__main__":
    main()
