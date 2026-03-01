#!/usr/bin/env python3
"""
SCA Federation Positioning Step — Layer 1 (Deterministic)

Implements position_in_federated_schemas() for SCAAgent.
Proof of concept scoped to Q17167 (Roman Republic).

Adds to sca_agent.py:
  - _ensure_hops_policy()
  - _fetch_wikidata_classification_properties()
  - _resolve_classification_anchors()
  - _write_classification_anchors()
  - _write_positioned_as_edges()
  - _write_provides_anchor_edges()
  - position_in_federated_schemas()
  - positioning_report()

Usage (standalone dry-run, no Neo4j write):
  python sca_federation_positioning.py --dry-run

Usage (write to graph):
  python sca_federation_positioning.py --write \\
    --neo4j-uri neo4j+s://YOUR_URI \\
    --neo4j-password YOUR_PASSWORD

Spec: docs/architecture/SCA_FEDERATION_POSITIONING_SPEC_v2.md
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

# ── Constants ──────────────────────────────────────────────────────────────────

SPARQL_URL  = "https://query.wikidata.org/sparql"
USER_AGENT  = "Chrystallum/1.0 (research project)"
SPARQL_TIMEOUT_S = 30

# Wikidata properties harvested for Layer 1 positioning
POSITIONING_PROPERTIES = {
    "P31":   "INSTANCE_OF_CLASS",      # instance of
    "P279":  "CLASSIFICATION_PARENT",  # subclass of
    "P361":  "COMPOSITIONAL_PARENT",   # part of
    "P122":  "TYPE_ANCHOR",            # basic form of government
    "P527":  "COMPOSITIONAL_CHILD",    # has part
    "P460":  "SAME_AS_CANDIDATE",      # said to be same as
    "P1269": "ASSOCIATIVE",            # facet of
}

# Classification properties harvested from each target node
CLASSIFICATION_PROPS = {
    "P1036": "dewey",    # Dewey Decimal Classification
    "P1149": "lcc",      # Library of Congress Classification
    "P244":  "lcsh_id",  # Library of Congress authority ID
    "P2163": "fast_id",  # FAST subject heading ID
    "P227":  "gnd_id",   # GND ID (German authority, useful for crosscheck)
}

# Anchor type vocabulary (Chrystallum-internal)
# Maps Wikidata QIDs to anchor_type labels
# Populated from known parent QIDs of Q17167
ANCHOR_TYPE_MAP = {
    "Q1307214": "FormOfGovernment",
    "Q11514315": "HistoricalPeriod",
    "Q3024240":  "HistoricalCountry",
    "Q48349":    "Empire",
    "Q666680":   "FormOfGovernmentType",   # aristocratic republic
    "Q7270":     "FormOfGovernmentType",   # republic
    "Q1747689":  "CivilisationContext",    # Ancient Rome
    "Q28108":    "PoliticalSystem",        # political system
    "Q2277":     "HistoricalPeriod",       # Roman Empire (successor)
}

# Hops semantics (mirrors SYS_Policy node FederationPositioningHopsSemantics)
HOPS_POLICY = {
    "name": "FederationPositioningHopsSemantics",
    "definition": {
        0: "self — the domain root QID itself",
        1: "direct parent — immediate P31/P279/P361/P122 target",
        2: "grandparent — parent of a direct parent",
        "n": "nth ancestor in the traversal chain (shortest path)",
    },
    "rule": "shortest path from domain root to anchor through traversed properties",
}

# Domain root for this proof of concept
DOMAIN_ROOT_QID = "Q17167"
DOMAIN_ROOT_LABEL = "Roman Republic"

# Federation name for Layer 1 (Wikidata only)
FEDERATION_WIKIDATA = "wikidata"


# ── SPARQL helpers ─────────────────────────────────────────────────────────────

def _sparql_get(query: str, retries: int = 3) -> List[Dict]:
    """Execute SPARQL query against Wikidata, return bindings."""
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
        except requests.exceptions.HTTPError as e:
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


def _qid_from_uri(uri: str) -> str:
    return uri.split("/")[-1]


# ── Step 1: Fetch Wikidata classification properties for seed QID ──────────────

def fetch_wikidata_classification_properties(seed_qid: str) -> List[Dict]:
    """
    Fetch all Layer 1 positioning properties from Wikidata for seed_qid.
    Returns list of {property, rel_type, target_qid, target_label,
                     target_dewey, target_lcc, target_lcsh_id, target_fast_id,
                     target_gnd_id, target_description}
    """
    prop_list = " ".join(f"wdt:{p}" for p in POSITIONING_PROPERTIES)

    # Build OPTIONAL blocks for classification props on each target
    optional_blocks = "\n".join(
        f"  OPTIONAL {{ ?target wdt:{p} ?{name}. }}"
        for p, name in CLASSIFICATION_PROPS.items()
    )

    query = f"""
SELECT DISTINCT ?prop ?target ?targetLabel ?dewey ?lcc ?lcsh_id ?fast_id ?gnd_id
WHERE {{
  VALUES ?prop {{ {prop_list} }}
  wd:{seed_qid} ?prop ?target .
  FILTER(STRSTARTS(STR(?target), "http://www.wikidata.org/entity/Q"))
{optional_blocks}
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en".
    ?target rdfs:label ?targetLabel.
  }}
}}
"""
    print(f"  Fetching classification properties for {seed_qid} from Wikidata...")
    rows = _sparql_get(query)
    time.sleep(0.5)

    results = []
    seen = set()
    for row in rows:
        prop_uri   = row.get("prop",   {}).get("value", "")
        target_uri = row.get("target", {}).get("value", "")
        prop_id    = prop_uri.split("/")[-1].replace("direct/", "")
        target_qid = _qid_from_uri(target_uri)

        key = (prop_id, target_qid)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "property":     prop_id,
            "rel_type":     POSITIONING_PROPERTIES.get(prop_id, "ASSOCIATIVE"),
            "target_qid":   target_qid,
            "target_label": row.get("targetLabel", {}).get("value", ""),
            "dewey":        row.get("dewey",   {}).get("value", None),
            "lcc":          row.get("lcc",     {}).get("value", None),
            "lcsh_id":      row.get("lcsh_id", {}).get("value", None),
            "fast_id":      row.get("fast_id", {}).get("value", None),
            "gnd_id":       row.get("gnd_id",  {}).get("value", None),
        })

    print(f"  Found {len(results)} positioning relationships")
    return results


# ── Step 2: Fetch seed QID's own classification properties (hops=0) ───────────

def fetch_self_classification(seed_qid: str) -> Dict:
    """
    Fetch classification anchors on the seed QID itself (hops=0).
    Returns dict of {dewey, lcc, lcsh_id, fast_id, gnd_id, label}
    """
    optional_blocks = "\n".join(
        f"  OPTIONAL {{ wd:{seed_qid} wdt:{p} ?{name}. }}"
        for p, name in CLASSIFICATION_PROPS.items()
    )

    query = f"""
SELECT ?label ?dewey ?lcc ?lcsh_id ?fast_id ?gnd_id
WHERE {{
{optional_blocks}
  OPTIONAL {{
    wd:{seed_qid} rdfs:label ?label.
    FILTER(LANG(?label) = "en")
  }}
}}
LIMIT 1
"""
    print(f"  Fetching self-classification for {seed_qid}...")
    rows = _sparql_get(query)
    time.sleep(0.3)

    if not rows:
        return {}

    row = rows[0]
    return {
        "label":   row.get("label",   {}).get("value", DOMAIN_ROOT_LABEL),
        "dewey":   row.get("dewey",   {}).get("value", None),
        "lcc":     row.get("lcc",     {}).get("value", None),
        "lcsh_id": row.get("lcsh_id", {}).get("value", None),
        "fast_id": row.get("fast_id", {}).get("value", None),
        "gnd_id":  row.get("gnd_id",  {}).get("value", None),
    }


# ── Step 3: Build position map ─────────────────────────────────────────────────

def build_position_map(
    seed_qid: str,
    self_classification: Dict,
    parent_properties: List[Dict],
) -> Dict:
    """
    Combine self-classification (hops=0) and parent properties (hops=1)
    into a unified position map keyed by target_qid.

    Returns:
      {
        "Q17167": { hops:0, rel_type:"SELF", ... classification anchors ... },
        "Q1307214": { hops:1, rel_type:"INSTANCE_OF_CLASS", ... },
        ...
      }
    """
    position_map = {}

    # Self (hops=0)
    position_map[seed_qid] = {
        "qid":        seed_qid,
        "label":      self_classification.get("label", DOMAIN_ROOT_LABEL),
        "hops":       0,
        "property":   "SELF",
        "rel_type":   "SELF",
        "anchor_type": "DomainRoot",
        "federation": FEDERATION_WIKIDATA,
        "dewey":      self_classification.get("dewey"),
        "lcc":        self_classification.get("lcc"),
        "lcsh_id":    self_classification.get("lcsh_id"),
        "fast_id":    self_classification.get("fast_id"),
        "gnd_id":     self_classification.get("gnd_id"),
        "confidence": "HIGH",
    }

    # Direct parents (hops=1)
    for row in parent_properties:
        qid = row["target_qid"]
        if qid == seed_qid:
            continue

        # A QID can appear via multiple properties — keep all edges
        # but record shortest path (first seen = hops:1 for direct)
        entry = {
            "qid":        qid,
            "label":      row["target_label"],
            "hops":       1,
            "property":   row["property"],
            "rel_type":   row["rel_type"],
            "anchor_type": ANCHOR_TYPE_MAP.get(qid, "ClassificationAnchor"),
            "federation": FEDERATION_WIKIDATA,
            "dewey":      row.get("dewey"),
            "lcc":        row.get("lcc"),
            "lcsh_id":    row.get("lcsh_id"),
            "fast_id":    row.get("fast_id"),
            "gnd_id":     row.get("gnd_id"),
            "confidence": "HIGH",
        }

        # If QID seen before via different property, append as additional edge
        existing_key = qid
        if existing_key in position_map and position_map[existing_key]["hops"] == 1:
            # Store as list if multiple edges to same target
            if not isinstance(position_map.get(f"{qid}_edges"), list):
                position_map[f"{qid}_edges"] = [position_map[existing_key]]
            position_map[f"{qid}_edges"].append(entry)
        else:
            position_map[existing_key] = entry

    return position_map


# ── Step 4: Neo4j writes ───────────────────────────────────────────────────────

ENSURE_POLICY_QUERY = """
MERGE (p:SYS_Policy {name: $name})
SET p.definition     = $definition,
    p.rule           = $rule,
    p.last_updated   = $updated_at,
    p.updated_by     = 'sca_federation_positioning'
RETURN p.name AS name
"""

ENSURE_ANCHOR_QUERY = """
MERGE (a:ClassificationAnchor {qid: $qid})
SET a.label        = $label,
    a.anchor_type  = $anchor_type,
    a.federation   = $federation,
    a.dewey        = CASE WHEN $dewey   IS NOT NULL THEN $dewey   ELSE a.dewey   END,
    a.lcc          = CASE WHEN $lcc     IS NOT NULL THEN $lcc     ELSE a.lcc     END,
    a.lcsh_id      = CASE WHEN $lcsh_id IS NOT NULL THEN $lcsh_id ELSE a.lcsh_id END,
    a.fast_id      = CASE WHEN $fast_id IS NOT NULL THEN $fast_id ELSE a.fast_id END,
    a.gnd_id       = CASE WHEN $gnd_id  IS NOT NULL THEN $gnd_id  ELSE a.gnd_id  END,
    a.last_updated = $updated_at
RETURN a.qid AS qid
"""

POSITIONED_AS_QUERY = """
MATCH (sc:SubjectConcept {qid: $sc_qid})
MATCH (anchor:ClassificationAnchor {qid: $anchor_qid})
MERGE (sc)-[r:POSITIONED_AS {
  federation:   $federation,
  property:     $property,
  hops:         $hops
}]->(anchor)
SET r.rel_type     = $rel_type,
    r.anchor_type  = $anchor_type,
    r.confidence   = $confidence,
    r.policy_ref   = $policy_ref,
    r.positioned_at = $positioned_at
RETURN r.federation AS federation, r.hops AS hops
"""

PROVIDES_ANCHOR_QUERY = """
MATCH (fed:SYS_FederationSource {name: $fed_name})
MATCH (anchor:ClassificationAnchor {qid: $anchor_qid})
MERGE (fed)-[r:PROVIDES_ANCHOR]->(anchor)
SET r.confirmed_at = $confirmed_at
RETURN fed.name AS fed_name, anchor.qid AS anchor_qid
"""

ENTITY_AS_ANCHOR_QUERY = """
// Where target already exists as Entity, write POSITIONED_AS directly to Entity
MATCH (sc:SubjectConcept {qid: $sc_qid})
MATCH (target:Entity {qid: $anchor_qid})
MERGE (sc)-[r:POSITIONED_AS {
  federation:   $federation,
  property:     $property,
  hops:         $hops
}]->(target)
SET r.rel_type      = $rel_type,
    r.anchor_type   = $anchor_type,
    r.confidence    = $confidence,
    r.policy_ref    = $policy_ref,
    r.positioned_at = $positioned_at
RETURN r.federation AS federation, r.hops AS hops
"""

CHECK_ENTITY_EXISTS_QUERY = """
MATCH (e:Entity {qid: $qid}) RETURN e.qid AS qid LIMIT 1
"""


def write_position_map(
    driver,
    seed_qid: str,
    position_map: Dict,
    dry_run: bool = True,
) -> Dict:
    """
    Write position map to Neo4j:
    1. Ensure SYS_Policy node for hops semantics
    2. For each position entry:
       a. If target already exists as Entity → write POSITIONED_AS to Entity
       b. If not → create/merge ClassificationAnchor node, write POSITIONED_AS to it
    3. Write PROVIDES_ANCHOR from Wikidata SYS_FederationSource to each anchor

    Returns write summary.
    """
    now = datetime.now(timezone.utc).isoformat()
    policy_ref = HOPS_POLICY["name"]

    summary = {
        "policy_ensured": False,
        "anchors_created": 0,
        "positioned_as_to_entity": 0,
        "positioned_as_to_anchor": 0,
        "provides_anchor": 0,
        "errors": [],
    }

    if dry_run:
        print("\n  [DRY RUN] — no writes performed")
        _print_dry_run_plan(seed_qid, position_map, policy_ref)
        return summary

    with driver.session() as session:

        # ── 1. Ensure SYS_Policy ──────────────────────────────────────────────
        print("\n  Writing SYS_Policy node...")
        try:
            session.run(
                ENSURE_POLICY_QUERY,
                name=policy_ref,
                definition=json.dumps(HOPS_POLICY["definition"]),
                rule=HOPS_POLICY["rule"],
                updated_at=now,
            )
            summary["policy_ensured"] = True
            print(f"  ✓ SYS_Policy: {policy_ref}")
        except Exception as e:
            summary["errors"].append(f"Policy write failed: {e}")
            print(f"  ✗ Policy write failed: {e}")

        # ── 2. Write each position entry ──────────────────────────────────────
        print("\n  Writing ClassificationAnchor nodes and POSITIONED_AS edges...")

        for qid, entry in position_map.items():
            # Skip multi-edge tracking keys
            if qid.endswith("_edges"):
                continue
            if entry.get("rel_type") == "SELF":
                # Hops=0: write self-classification anchors to SubjectConcept directly
                # (properties, not edges — SubjectConcept already is the node)
                # Just write the POSITIONED_AS self-edge for completeness
                pass

            target_qid  = entry["qid"]
            rel_type    = entry["rel_type"]
            hops        = entry["hops"]
            anchor_type = entry["anchor_type"]
            property_id = entry["property"]

            try:
                # Check if target exists as Entity
                result = session.run(CHECK_ENTITY_EXISTS_QUERY, qid=target_qid)
                entity_exists = result.single() is not None

                if entity_exists and hops > 0:
                    # Write POSITIONED_AS directly to existing Entity node
                    session.run(
                        ENTITY_AS_ANCHOR_QUERY,
                        sc_qid=seed_qid,
                        anchor_qid=target_qid,
                        federation=FEDERATION_WIKIDATA,
                        property=property_id,
                        hops=hops,
                        rel_type=rel_type,
                        anchor_type=anchor_type,
                        confidence=entry["confidence"],
                        policy_ref=policy_ref,
                        positioned_at=now,
                    )
                    summary["positioned_as_to_entity"] += 1
                    print(f"  ✓ POSITIONED_AS → Entity {target_qid} ({entry['label']}) hops={hops} via {property_id}")

                else:
                    # Create/merge ClassificationAnchor node
                    session.run(
                        ENSURE_ANCHOR_QUERY,
                        qid=target_qid,
                        label=entry.get("label", ""),
                        anchor_type=anchor_type,
                        federation=FEDERATION_WIKIDATA,
                        dewey=entry.get("dewey"),
                        lcc=entry.get("lcc"),
                        lcsh_id=entry.get("lcsh_id"),
                        fast_id=entry.get("fast_id"),
                        gnd_id=entry.get("gnd_id"),
                        updated_at=now,
                    )
                    summary["anchors_created"] += 1

                    if hops > 0:
                        # Write POSITIONED_AS to ClassificationAnchor
                        session.run(
                            POSITIONED_AS_QUERY,
                            sc_qid=seed_qid,
                            anchor_qid=target_qid,
                            federation=FEDERATION_WIKIDATA,
                            property=property_id,
                            hops=hops,
                            rel_type=rel_type,
                            anchor_type=anchor_type,
                            confidence=entry["confidence"],
                            policy_ref=policy_ref,
                            positioned_at=now,
                        )
                        summary["positioned_as_to_anchor"] += 1
                        print(f"  ✓ ClassificationAnchor + POSITIONED_AS → {target_qid} ({entry['label']}) hops={hops} via {property_id}")

            except Exception as e:
                msg = f"Write failed for {target_qid}: {e}"
                summary["errors"].append(msg)
                print(f"  ✗ {msg}")

        # ── 3. Wire PROVIDES_ANCHOR from Wikidata FederationSource ────────────
        print("\n  Writing PROVIDES_ANCHOR edges from Wikidata FederationSource...")
        written_anchors = set()
        for qid, entry in position_map.items():
            if qid.endswith("_edges") or entry.get("rel_type") == "SELF":
                continue
            target_qid = entry["qid"]
            if target_qid in written_anchors:
                continue
            try:
                session.run(
                    PROVIDES_ANCHOR_QUERY,
                    fed_name="Wikidata",
                    anchor_qid=target_qid,
                    confirmed_at=now,
                )
                written_anchors.add(target_qid)
                summary["provides_anchor"] += 1
            except Exception as e:
                summary["errors"].append(f"PROVIDES_ANCHOR failed for {target_qid}: {e}")

        print(f"  ✓ PROVIDES_ANCHOR edges: {summary['provides_anchor']}")

    return summary


# ── Dry run display ────────────────────────────────────────────────────────────

def _print_dry_run_plan(seed_qid: str, position_map: Dict, policy_ref: str):
    print(f"\n  {'─'*70}")
    print(f"  DRY RUN PLAN — {seed_qid} ({DOMAIN_ROOT_LABEL})")
    print(f"  {'─'*70}")
    print(f"  SYS_Policy: {policy_ref}")
    print()

    for qid, entry in position_map.items():
        if qid.endswith("_edges"):
            continue
        hops       = entry.get("hops", "?")
        rel_type   = entry.get("rel_type", "?")
        label      = entry.get("label", "?")
        property_id = entry.get("property", "?")
        anchors = []
        if entry.get("dewey"):   anchors.append(f"Dewey={entry['dewey']}")
        if entry.get("lcc"):     anchors.append(f"LCC={entry['lcc']}")
        if entry.get("lcsh_id"): anchors.append(f"LCSH={entry['lcsh_id']}")
        if entry.get("fast_id"): anchors.append(f"FAST={entry['fast_id']}")
        anchor_str = " | ".join(anchors) if anchors else "no classification anchors"

        print(f"  hops={hops} [{rel_type}] → {qid} ({label})")
        print(f"    via: {property_id}  |  {anchor_str}")
        print()


# ── Positioning report ─────────────────────────────────────────────────────────

def generate_positioning_report(
    seed_qid: str,
    position_map: Dict,
    write_summary: Dict,
    dry_run: bool,
) -> Dict:
    """Generate JSON report of positioning results."""

    rows = []
    for qid, entry in position_map.items():
        if qid.endswith("_edges"):
            continue
        rows.append({
            "qid":        entry["qid"],
            "label":      entry.get("label", ""),
            "hops":       entry.get("hops"),
            "property":   entry.get("property"),
            "rel_type":   entry.get("rel_type"),
            "anchor_type": entry.get("anchor_type"),
            "dewey":      entry.get("dewey"),
            "lcc":        entry.get("lcc"),
            "lcsh_id":    entry.get("lcsh_id"),
            "fast_id":    entry.get("fast_id"),
            "has_anchors": any([
                entry.get("dewey"),
                entry.get("lcc"),
                entry.get("lcsh_id"),
                entry.get("fast_id"),
            ]),
        })

    # Summary of which systems RR is now addressable from
    addressable_from = {}
    for row in rows:
        if row["dewey"]:
            addressable_from.setdefault("dewey", []).append(
                {"qid": row["qid"], "label": row["label"], "value": row["dewey"], "hops": row["hops"]}
            )
        if row["lcc"]:
            addressable_from.setdefault("lcc", []).append(
                {"qid": row["qid"], "label": row["label"], "value": row["lcc"], "hops": row["hops"]}
            )
        if row["lcsh_id"]:
            addressable_from.setdefault("lcsh", []).append(
                {"qid": row["qid"], "label": row["label"], "value": row["lcsh_id"], "hops": row["hops"]}
            )
        if row["fast_id"]:
            addressable_from.setdefault("fast", []).append(
                {"qid": row["qid"], "label": row["label"], "value": row["fast_id"], "hops": row["hops"]}
            )

    return {
        "run_at":          datetime.now(timezone.utc).isoformat(),
        "seed_qid":        seed_qid,
        "seed_label":      DOMAIN_ROOT_LABEL,
        "dry_run":         dry_run,
        "layer":           1,
        "federation":      FEDERATION_WIKIDATA,
        "total_positions": len(rows),
        "addressable_from": addressable_from,
        "write_summary":   write_summary,
        "positions":       rows,
    }


def print_positioning_report(report: Dict):
    """Print human-readable positioning report to stdout."""
    print("\n" + "=" * 70)
    print(f"POSITIONING REPORT — {report['seed_qid']} ({report['seed_label']})")
    print("=" * 70)
    print(f"Run at:    {report['run_at']}")
    print(f"Mode:      {'DRY RUN' if report['dry_run'] else 'WRITE'}")
    print(f"Layer:     {report['layer']} (deterministic Wikidata)")
    print(f"Positions: {report['total_positions']}")
    print()

    af = report["addressable_from"]
    print("Addressable from:")
    for system in ["lcsh", "dewey", "lcc", "fast"]:
        entries = af.get(system, [])
        if entries:
            print(f"  {system.upper()}:")
            for e in entries:
                print(f"    {e['value']} — {e['label']} ({e['qid']}) hops={e['hops']}")
        else:
            print(f"  {system.upper()}: none found")

    print()
    ws = report["write_summary"]
    if not report["dry_run"]:
        print("Write summary:")
        print(f"  Policy ensured:            {ws['policy_ensured']}")
        print(f"  POSITIONED_AS → Entity:    {ws['positioned_as_to_entity']}")
        print(f"  POSITIONED_AS → Anchor:    {ws['positioned_as_to_anchor']}")
        print(f"  PROVIDES_ANCHOR edges:     {ws['provides_anchor']}")
        if ws["errors"]:
            print(f"  Errors ({len(ws['errors'])}):")
            for e in ws["errors"]:
                print(f"    - {e}")


# ── Main entry point ───────────────────────────────────────────────────────────

def position_in_federated_schemas(
    seed_qid: str = DOMAIN_ROOT_QID,
    dry_run: bool = True,
    neo4j_uri: Optional[str] = None,
    neo4j_user: str = "neo4j",
    neo4j_password: Optional[str] = None,
    report_path: Optional[str] = None,
) -> Dict:
    """
    Main entry point for federation positioning step.
    Layer 1 only — deterministic Wikidata traversal.

    Args:
        seed_qid:       Domain root QID (default Q17167)
        dry_run:        If True, resolve from Wikidata but do not write to Neo4j
        neo4j_uri:      Neo4j URI (required if dry_run=False)
        neo4j_user:     Neo4j username
        neo4j_password: Neo4j password (required if dry_run=False)
        report_path:    Path to write JSON report (optional)

    Returns:
        Positioning report dict
    """
    print("=" * 70)
    print("SCA FEDERATION POSITIONING STEP — Layer 1 (Deterministic)")
    print(f"Seed QID: {seed_qid} ({DOMAIN_ROOT_LABEL})")
    print("=" * 70)
    print()

    # ── Step 1: Fetch self-classification (hops=0) ────────────────────────────
    print("Step 1: Fetching self-classification properties...")
    self_classification = fetch_self_classification(seed_qid)
    print(f"  LCSH: {self_classification.get('lcsh_id', 'not found')}")
    print(f"  FAST: {self_classification.get('fast_id', 'not found')}")
    print(f"  Dewey: {self_classification.get('dewey', 'not found')}")
    print(f"  LCC: {self_classification.get('lcc', 'not found')}")
    print()

    # ── Step 2: Fetch direct parent properties (hops=1) ───────────────────────
    print("Step 2: Fetching classification properties from direct parents...")
    parent_properties = fetch_wikidata_classification_properties(seed_qid)
    print()

    # ── Step 3: Build position map ────────────────────────────────────────────
    print("Step 3: Building position map...")
    position_map = build_position_map(seed_qid, self_classification, parent_properties)
    print(f"  Position map: {len([k for k in position_map if not k.endswith('_edges')])} entries")
    print()

    # ── Step 4: Write to Neo4j (or dry run) ───────────────────────────────────
    write_summary = {
        "policy_ensured": False,
        "anchors_created": 0,
        "positioned_as_to_entity": 0,
        "positioned_as_to_anchor": 0,
        "provides_anchor": 0,
        "errors": [],
    }

    if not dry_run:
        if not neo4j_uri or not neo4j_password:
            print("Error: --write requires --neo4j-uri and --neo4j-password", file=sys.stderr)
            sys.exit(1)
        print("Step 4: Writing to Neo4j...")
        try:
            from neo4j import GraphDatabase
        except ImportError:
            print("Error: neo4j driver not installed. Run: pip install neo4j", file=sys.stderr)
            sys.exit(1)
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        try:
            write_summary = write_position_map(driver, seed_qid, position_map, dry_run=False)
        finally:
            driver.close()
    else:
        print("Step 4: Dry run — showing write plan...")
        write_summary = write_position_map(None, seed_qid, position_map, dry_run=True)

    print()

    # ── Step 5: Report ────────────────────────────────────────────────────────
    report = generate_positioning_report(seed_qid, position_map, write_summary, dry_run)
    print_positioning_report(report)

    if report_path:
        import pathlib
        pathlib.Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(report_path).write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\nReport written: {report_path}")

    return report


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SCA Federation Positioning Step — Layer 1 proof of concept on Q17167."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true",
                      help="Resolve from Wikidata, show plan, no graph writes.")
    mode.add_argument("--write",   action="store_true",
                      help="Resolve from Wikidata and write to Neo4j.")

    parser.add_argument("--qid", default=DOMAIN_ROOT_QID,
                        help=f"Seed QID (default: {DOMAIN_ROOT_QID})")
    parser.add_argument("--neo4j-uri",      default=None)
    parser.add_argument("--neo4j-user",     default="neo4j")
    parser.add_argument("--neo4j-password", default=None)
    parser.add_argument("--report",         default="output/subject_concepts/federation_positioning_report.json",
                        help="Path to write JSON report.")

    args = parser.parse_args()

    # Try .env fallback
    neo4j_uri  = args.neo4j_uri
    neo4j_pw   = args.neo4j_password
    if not neo4j_uri or not neo4j_pw:
        try:
            from config_loader import NEO4J_URI, NEO4J_PASSWORD
            neo4j_uri = neo4j_uri or NEO4J_URI
            neo4j_pw  = neo4j_pw  or NEO4J_PASSWORD
        except ImportError:
            pass
        try:
            from dotenv import load_dotenv; import os
            load_dotenv()
            neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI")
            neo4j_pw  = neo4j_pw  or os.getenv("NEO4J_PASSWORD")
        except ImportError:
            pass

    position_in_federated_schemas(
        seed_qid=args.qid,
        dry_run=args.dry_run,
        neo4j_uri=neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=neo4j_pw,
        report_path=args.report,
    )


if __name__ == "__main__":
    main()
