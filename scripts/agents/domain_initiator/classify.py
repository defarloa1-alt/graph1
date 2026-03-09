#!/usr/bin/env python3
"""
Domain Initiator (DI) — Classify.

Consumes a DI harvest JSON and produces per-facet deltas for the SCA.

Three-tier routing:
  1. instance_of / subclass_of QIDs → facet via anchor registry + type hierarchy
  2. PIDs on each candidate → facet via SYS_PropertyMapping (queried from graph)
  3. External ID PIDs → federation source activation → facet

Output: per-facet delta bundles ready for SCA → SFA routing.

Rule: Never pass PID or QID without its label.

Usage:
  python scripts/agents/domain_initiator/classify.py --harvest output/di_harvest/Q17167_di_harvest.json
  python scripts/agents/domain_initiator/classify.py --harvest output/di_harvest/Q17167_di_harvest.json --output output/di_classify/
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

FACET_REGISTRY = ROOT / "Facets" / "facet_registry_master.json"

# ── Tier 1: Type QID → Facet routing ─────────────────────────────────────────
# Built from facet_registry_master.json anchors + domain-specific extensions.
# Extensions cover common Wikidata types the anchors miss but that clearly
# route to a facet. Each maps QID → list of (facet_key, role) tuples.

TYPE_EXTENSIONS: Dict[str, List[Tuple[str, str]]] = {
    # Economic
    "Q8142":       [("economic", "primary")],    # currency
    "Q918448":     [("economic", "primary")],    # denomination
    "Q952064":     [("economic", "primary")],    # Roman currency
    "Q41207":      [("economic", "primary")],    # coin
    "Q113813711":  [("economic", "primary")],    # coin type
    "Q860641":     [("economic", "primary")],    # gold coin
    "Q11650194":   [("economic", "primary")],    # bronze coin
    "Q7048891":    [("economic", "primary")],    # non-decimal currency
    "Q93288":      [("political", "primary"), ("social", "secondary"), ("economic", "secondary")],  # contract
    "Q2135465":    [("political", "primary"), ("social", "secondary")],   # legal term
    "Q2165988":    [("social", "primary"), ("economic", "secondary")],     # debt bondage
    # Military
    "Q178561":     [("military", "primary"), ("geographic", "secondary")],  # battle
    "Q176799":     [("military", "primary"), ("political", "secondary")],   # military unit
    "Q851436":     [("military", "primary"), ("political", "secondary")],   # bodyguard
    "Q971045":     [("military", "primary")],    # royal guard
    "Q11010841":   [("military", "primary")],    # imperial guard
    "Q104212151":  [("military", "primary")],    # series of wars
    # Geographic
    "Q182547":     [("geographic", "primary"), ("political", "secondary")],  # Roman province
    "Q6256":       [("geographic", "primary"), ("political", "secondary")],  # country
    "Q82794":      [("geographic", "primary")],    # geographic region
    "Q515":        [("geographic", "primary"), ("political", "secondary")],  # city
    "Q1549591":    [("geographic", "primary")],    # big city
    "Q3624078":    [("political", "primary"), ("geographic", "secondary")],  # sovereign state
    # Political / Social
    "Q820655":     [("political", "primary"), ("social", "secondary")],   # statute
    "Q2672648":    [("social", "primary"), ("political", "secondary")],    # social conflict
    "Q1471594":    [("social", "primary"), ("political", "secondary")],    # collective action
    "Q687031":     [("political", "primary"), ("social", "secondary")],    # secession
    "Q48349":      [("political", "primary"), ("military", "secondary")],  # empire
    "Q3024240":    [("political", "primary"), ("geographic", "secondary")],  # historical country
    "Q1307214":    [("political", "primary")],     # form of government
    "Q7188":       [("political", "primary")],     # government
    "Q666680":     [("political", "primary")],     # aristocratic republic (form of govt)
    # Religious
    "Q9174":       [("religious", "primary")],     # religion
    "Q1826286":    [("religious", "primary")],     # religious movement
    "Q2340164":    [("religious", "primary"), ("cultural", "secondary")],  # religion of ancient Rome
    "Q337547":     [("religious", "primary"), ("cultural", "secondary")],  # ancient Roman religion (specific QID)
    # Cultural / Artistic
    "Q19958368":   [("cultural", "primary")],    # culture of an area
    "Q1200427":    [("cultural", "primary")],    # culture of ancient Rome
    "Q7777573":    [("artistic", "primary"), ("cultural", "secondary"), ("communication", "secondary")],  # theatrical genre
    # Linguistic
    "Q315":        [("linguistic", "primary")],    # language
    "Q34770":      [("linguistic", "primary")],    # language family
    # Demographic
    "Q133311":     [("demographic", "primary"), ("social", "secondary"), ("geographic", "secondary")],  # tribe
    # Temporal (not a facet — flagged for filtering)
    "Q11514315":   [],  # historical period — temporal, not routed to facet
    "Q486761":     [],  # classical antiquity — temporal scope, not facet
    "Q3647172":    [("scientific", "secondary"), ("economic", "primary")],  # unit of mass
    # Wikipedia infrastructure (filter out)
    "Q4167836":    [],  # Wikimedia category — not domain content
    "Q56284429":   [],  # Wikimedia vital articles — not domain content
}

# ── Tier 3: External ID PID → federation source + facet ──────────────────────
EXTERNAL_ID_ROUTING: Dict[str, Dict[str, Any]] = {
    "P1584": {
        "federation_source": {"source_id": "pleiades", "label": "Pleiades"},
        "facets": [("geographic", "primary"), ("archaeological", "secondary")],
    },
    "P1566": {
        "federation_source": {"source_id": "geonames", "label": "GeoNames"},
        "facets": [("geographic", "primary")],
    },
    "P244": {
        "federation_source": {"source_id": "loc", "label": "Library of Congress"},
        "facets": [],  # backbone, not facet-specific
        "backbone": True,
    },
    "P2163": {
        "federation_source": {"source_id": "fast", "label": "FAST"},
        "facets": [],
        "backbone": True,
    },
    "P1036": {
        "federation_source": {"source_id": "dewey", "label": "Dewey Decimal"},
        "facets": [],
        "backbone": True,
    },
    "P214": {
        "federation_source": {"source_id": "viaf", "label": "VIAF"},
        "facets": [("biographic", "secondary"), ("intellectual", "secondary")],
    },
    "P227": {
        "federation_source": {"source_id": "gnd", "label": "GND"},
        "facets": [("intellectual", "secondary"), ("biographic", "secondary")],
    },
}


def load_facet_registry() -> Dict[str, Dict]:
    """Load facet registry and build QID → facet anchor map."""
    with open(FACET_REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)

    # anchor_qid → [(facet_key, "anchor")]
    anchor_map: Dict[str, List[Tuple[str, str]]] = {}
    facet_defs: Dict[str, Dict] = {}

    for facet in reg["facets"]:
        key = facet["key"]
        facet_defs[key] = {
            "label": facet["label"],
            "definition": facet["definition"],
        }
        for anchor in facet.get("anchors", []):
            qid = anchor["qid"]
            if qid not in anchor_map:
                anchor_map[qid] = []
            anchor_map[qid].append((key, "anchor"))

    return anchor_map, facet_defs


def load_property_mappings() -> Dict[str, Dict]:
    """Load curated PID→facet mappings (static).

    The bulk SYS_PropertyMapping nodes (500) were removed from the graph —
    they were a generic classification of ALL Wikidata PIDs, mostly irrelevant
    to the Roman Republic domain. This static map covers the PIDs that actually
    matter for domain initiator routing.
    """
    return _static_pid_map()


def _static_pid_map() -> Dict[str, Dict]:
    """Minimal PID→facet for offline use."""
    return {
        "P17":   {"label": "country",    "primary_facet": "geographic", "secondary_facets": []},
        "P131":  {"label": "located in the administrative territorial entity", "primary_facet": "geographic", "secondary_facets": []},
        "P276":  {"label": "location",   "primary_facet": "geographic", "secondary_facets": []},
        "P625":  {"label": "coordinate location", "primary_facet": "geographic", "secondary_facets": []},
        "P1584": {"label": "Pleiades ID","primary_facet": "geographic", "secondary_facets": ["archaeological"]},
        "P1566": {"label": "GeoNames ID","primary_facet": "geographic", "secondary_facets": []},
        "P39":   {"label": "position held", "primary_facet": "political", "secondary_facets": ["biographic", "social"]},
        "P279":  {"label": "subclass of","primary_facet": "intellectual","secondary_facets": []},
        "P361":  {"label": "part of",    "primary_facet": "intellectual","secondary_facets": []},
        "P1344": {"label": "participant in", "primary_facet": "military","secondary_facets": ["political"]},
        "P793":  {"label": "significant event", "primary_facet": "political", "secondary_facets": ["military"]},
    }


def classify_candidate(
    candidate: Dict,
    anchor_map: Dict[str, List[Tuple[str, str]]],
    pid_map: Dict[str, Dict],
) -> Dict[str, Any]:
    """
    Classify a single harvest candidate into facets.

    Returns the candidate dict enriched with:
      - facet_scores: {facet_key: {"score": float, "signals": [...]}}
      - primary_facet, secondary_facets
      - federation_activations: [{source_id, label, pid, pid_label}]
      - backbone_links: [{pid, label, value}]
      - is_temporal: True if the entity is a period subdivision (skip for SFA routing)
    """
    facet_signals: Dict[str, List[Dict]] = defaultdict(list)
    federation_activations: List[Dict] = []
    backbone_links: List[Dict] = []
    is_temporal = False

    qid = candidate["qid"]
    label = candidate["label"]

    # ── Tier 0: candidate's own QID → facet (for forward-linked named entities)
    # e.g. Q337547 (ancient Roman religion) IS a religion, not instance_of religion
    if qid in TYPE_EXTENSIONS:
        routes = TYPE_EXTENSIONS[qid]
        if not routes:
            is_temporal = True
        for facet_key, role in routes:
            facet_signals[facet_key].append({
                "tier": 1,
                "source": "self_qid",
                "qid": qid,
                "label": label,
                "role": role,
                "reason": f"entity {label} ({qid}) directly matched",
            })
    if qid in anchor_map:
        for facet_key, role in anchor_map[qid]:
            facet_signals[facet_key].append({
                "tier": 1,
                "source": "self_qid",
                "qid": qid,
                "label": label,
                "role": role,
                "reason": f"entity {label} ({qid}) is facet anchor",
            })

    # ── Tier 1: instance_of / subclass_of → facet ────────────────────────
    for source_field in ("instance_of", "subclass_of"):
        for ref in candidate.get(source_field, []):
            ref_qid = ref["qid"]
            ref_label = ref["label"]

            # Check type extensions first (domain-specific, more precise)
            if ref_qid in TYPE_EXTENSIONS:
                routes = TYPE_EXTENSIONS[ref_qid]
                if not routes:
                    # Empty list = temporal or non-facet entity
                    is_temporal = True
                for facet_key, role in routes:
                    facet_signals[facet_key].append({
                        "tier": 1,
                        "source": source_field,
                        "qid": ref_qid,
                        "label": ref_label,
                        "role": role,
                        "reason": f"{source_field} {ref_label} ({ref_qid})",
                    })

            # Check facet registry anchors
            if ref_qid in anchor_map:
                for facet_key, role in anchor_map[ref_qid]:
                    facet_signals[facet_key].append({
                        "tier": 1,
                        "source": source_field,
                        "qid": ref_qid,
                        "label": ref_label,
                        "role": role,
                        "reason": f"{source_field} anchor {ref_label} ({ref_qid})",
                    })

    # ── Tier 2: PIDs on geo_properties → facet ───────────────────────────
    for geo_prop in candidate.get("geo_properties", []):
        pid = geo_prop["pid"]
        pid_label = geo_prop["label"]
        if pid in pid_map:
            pm = pid_map[pid]
            pf = pm["primary_facet"]
            if pf:
                facet_signals[pf].append({
                    "tier": 2,
                    "source": "geo_property",
                    "pid": pid,
                    "label": pid_label,
                    "role": "primary",
                    "reason": f"property {pid_label} ({pid})",
                })
            for sf in pm.get("secondary_facets", []):
                facet_signals[sf].append({
                    "tier": 2,
                    "source": "geo_property",
                    "pid": pid,
                    "label": pid_label,
                    "role": "secondary",
                    "reason": f"property {pid_label} ({pid}) secondary",
                })

    # ── Tier 3: External IDs → federation + facet ────────────────────────
    for ext in candidate.get("external_ids", []):
        pid = ext["pid"]
        pid_label = ext["label"]
        value = ext.get("value", "")

        if pid in EXTERNAL_ID_ROUTING:
            route = EXTERNAL_ID_ROUTING[pid]
            fed = route["federation_source"]
            federation_activations.append({
                "source_id": fed["source_id"],
                "label": fed["label"],
                "pid": pid,
                "pid_label": pid_label,
                "value": value,
            })
            if route.get("backbone"):
                backbone_links.append({
                    "pid": pid,
                    "label": pid_label,
                    "value": value,
                })
            for facet_key, role in route.get("facets", []):
                facet_signals[facet_key].append({
                    "tier": 3,
                    "source": "external_id",
                    "pid": pid,
                    "label": pid_label,
                    "value": value,
                    "role": role,
                    "reason": f"federation {fed['label']} via {pid_label} ({pid})",
                })

    # ── Score facets ─────────────────────────────────────────────────────
    # Tier 1 signals (type match) weight 8, Tier 2 (property) weight 1, Tier 3 (federation) weight 2
    # Primary role doubles the signal weight.
    # Tier 2 is deduplicated by PID — P17 appearing 3x (3 countries) counts once,
    # not 3x. This prevents geo-heavy entities from drowning out type signals.
    TIER_WEIGHTS = {1: 8, 2: 1, 3: 2}
    ROLE_MULT = {"primary": 2.0, "secondary": 1.0, "anchor": 1.5}

    facet_scores: Dict[str, Dict] = {}
    for facet_key, signals in facet_signals.items():
        # Deduplicate Tier 2 by PID per facet
        seen_tier2_pids: Set[str] = set()
        score = 0.0
        for s in signals:
            if s["tier"] == 2:
                pid = s.get("pid", "")
                if pid in seen_tier2_pids:
                    continue
                seen_tier2_pids.add(pid)
            score += TIER_WEIGHTS.get(s["tier"], 1) * ROLE_MULT.get(s["role"], 1.0)
        facet_scores[facet_key] = {
            "score": score,
            "signal_count": len(signals),
            "signals": signals,
        }

    # Sort by score descending
    ranked = sorted(facet_scores.items(), key=lambda x: -x[1]["score"])
    primary_facet = ranked[0][0] if ranked else None
    secondary_facets = [k for k, v in ranked[1:] if v["score"] > 0]

    return {
        "qid": qid,
        "label": label,
        "primary_facet": primary_facet,
        "secondary_facets": secondary_facets,
        "facet_scores": facet_scores,
        "federation_activations": federation_activations,
        "backbone_links": backbone_links,
        "is_temporal": is_temporal,
    }


def resolve_most_granular_subject(
    harvest: Dict,
    classified: List[Dict],
) -> Dict[str, Any]:
    """
    From backbone links, identify the most granular LCSH subject for the domain.

    Strategy:
    - LCNAF sh-IDs are more specific than Dewey ranges
    - The seed's own LCSH is the domain tether
    - Backlink LCSH headings may be sub-domain tethers
    """
    backbone = harvest.get("subject_backbone_links", {})
    seed = harvest.get("seed", {})

    lcnaf = backbone.get("lcnaf", [])
    dewey = backbone.get("dewey", [])
    fast = backbone.get("fast", [])

    # Seed's own LCSH (if present) is the domain tether
    seed_lcsh = None
    sub_subjects: List[Dict] = []
    for entry in lcnaf:
        rec = {
            "qid": entry["qid"],
            "label": entry["label"],
            "lcnaf_id": entry["lcnaf_id"],
            "type": "lcnaf",
        }
        if entry["qid"] == seed.get("qid"):
            seed_lcsh = rec
        else:
            sub_subjects.append(rec)

    for entry in dewey:
        sub_subjects.append({
            "qid": entry["qid"],
            "label": entry["label"],
            "dewey_id": entry["dewey_id"],
            "type": "dewey",
        })

    for entry in fast:
        sub_subjects.append({
            "qid": entry["qid"],
            "label": entry["label"],
            "fast_id": entry["fast_id"],
            "type": "fast",
        })

    return {
        "domain_tether": seed_lcsh,
        "sub_subjects": sub_subjects,
        "backbone_summary": {
            "lcnaf_count": len(lcnaf),
            "dewey_count": len(dewey),
            "fast_count": len(fast),
        },
    }


def build_facet_deltas(
    classified: List[Dict],
    facet_defs: Dict[str, Dict],
    subject_resolution: Dict,
) -> List[Dict[str, Any]]:
    """
    Group classified candidates by facet → per-facet delta bundles for SCA.

    Each delta includes:
    - facet metadata (label, definition)
    - candidates assigned to this facet (primary or secondary)
    - federation sources activated across those candidates
    - relevant backbone links
    - evidence summary
    """
    # Group candidates by facet
    facet_candidates: Dict[str, List[Dict]] = defaultdict(list)
    facet_federations: Dict[str, Dict[str, Dict]] = defaultdict(dict)

    for c in classified:
        if c["is_temporal"]:
            continue  # skip period subdivisions

        primary = c["primary_facet"]
        if primary:
            facet_candidates[primary].append({
                "qid": c["qid"],
                "label": c["label"],
                "role": "primary",
                "score": c["facet_scores"].get(primary, {}).get("score", 0),
                "signals": c["facet_scores"].get(primary, {}).get("signals", []),
            })
        for sf in c["secondary_facets"]:
            facet_candidates[sf].append({
                "qid": c["qid"],
                "label": c["label"],
                "role": "secondary",
                "score": c["facet_scores"].get(sf, {}).get("score", 0),
                "signals": c["facet_scores"].get(sf, {}).get("signals", []),
            })

        # Aggregate federation activations by facet
        for fa in c["federation_activations"]:
            sid = fa["source_id"]
            for facet_key in [primary] + c["secondary_facets"]:
                if facet_key:
                    facet_federations[facet_key][sid] = {
                        "source_id": sid,
                        "label": fa["label"],
                        "pid": fa["pid"],
                        "pid_label": fa["pid_label"],
                    }

    # Build deltas
    deltas: List[Dict] = []
    for facet_key in sorted(facet_defs.keys()):
        candidates = facet_candidates.get(facet_key, [])
        if not candidates:
            continue

        fdef = facet_defs[facet_key]
        federations = list(facet_federations.get(facet_key, {}).values())

        # Sort candidates by score descending
        candidates.sort(key=lambda x: -x["score"])

        # Count by role
        primary_count = sum(1 for c in candidates if c["role"] == "primary")
        secondary_count = sum(1 for c in candidates if c["role"] == "secondary")

        # Evidence summary
        type_labels = set()
        for c in candidates:
            for s in c.get("signals", []):
                if s["tier"] == 1:
                    type_labels.add(s["label"])

        summary = (
            f"{len(candidates)} candidates ({primary_count} primary, {secondary_count} secondary)"
        )
        if type_labels:
            summary += f"; types: {', '.join(sorted(type_labels))}"
        if federations:
            summary += f"; federation: {', '.join(f['label'] for f in federations)}"

        deltas.append({
            "facet_key": facet_key,
            "facet_label": fdef["label"],
            "facet_definition": fdef["definition"],
            "candidate_count": len(candidates),
            "primary_count": primary_count,
            "secondary_count": secondary_count,
            "candidates": candidates,
            "federation_sources": federations,
            "evidence_summary": summary,
            "recommended_action": "SFA_EVALUATE",
        })

    return deltas


def main() -> int:
    parser = argparse.ArgumentParser(description="Domain Initiator — Classify")
    parser.add_argument(
        "--harvest",
        type=Path,
        default=ROOT / "output" / "di_harvest" / "Q17167_di_harvest.json",
        help="Path to DI harvest JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "di_classify",
        help="Output directory",
    )
    args = parser.parse_args()

    # Load harvest
    print(f"DI Classify — {args.harvest.name}")
    print("=" * 60)
    with open(args.harvest, encoding="utf-8") as f:
        harvest = json.load(f)

    seed = harvest["seed"]
    candidates = harvest["candidates"]
    print(f"  Seed: {seed['qid']} ({seed['label']})")
    print(f"  Candidates: {len(candidates)}")

    # Load routing tables
    print("\n[1] Loading routing tables...")
    anchor_map, facet_defs = load_facet_registry()
    print(f"  Facet registry: {len(facet_defs)} facets, {len(anchor_map)} anchor QIDs")
    pid_map = load_property_mappings()

    # Classify each candidate
    print(f"\n[2] Classifying {len(candidates)} candidates...")
    classified: List[Dict] = []
    temporal_count = 0
    unrouted_count = 0

    for c in candidates:
        result = classify_candidate(c, anchor_map, pid_map)
        classified.append(result)
        if result["is_temporal"]:
            temporal_count += 1
        elif not result["primary_facet"]:
            unrouted_count += 1

    routed = len(classified) - temporal_count - unrouted_count
    print(f"  Routed: {routed}, Temporal (skipped): {temporal_count}, Unrouted: {unrouted_count}")

    # Resolve most granular subject
    print("\n[3] Resolving subject backbone...")
    subject_resolution = resolve_most_granular_subject(harvest, classified)
    tether = subject_resolution["domain_tether"]
    if tether:
        print(f"  Domain tether: {tether['lcnaf_id']} ({tether['label']})")
    subs = subject_resolution["sub_subjects"]
    if subs:
        for s in subs:
            id_key = next((k for k in ("lcnaf_id", "dewey_id", "fast_id") if k in s), None)
            print(f"  Sub-subject: {s.get(id_key, '?')} ({s['label']})")

    # Build per-facet deltas
    print(f"\n[4] Building per-facet deltas...")
    deltas = build_facet_deltas(classified, facet_defs, subject_resolution)

    print(f"  {len(deltas)} facets activated:\n")
    for d in deltas:
        fed_str = ""
        if d["federation_sources"]:
            fed_str = f"  fed: {', '.join(f['label'] for f in d['federation_sources'])}"
        print(
            f"    {d['facet_label']:15} "
            f"{d['primary_count']:2}p + {d['secondary_count']:2}s = {d['candidate_count']:2} candidates"
            f"{fed_str}"
        )

    # Temporal entities (informational)
    temporal = [c for c in classified if c["is_temporal"]]
    if temporal:
        print(f"\n  Temporal (not routed to SFA):")
        for t in temporal:
            print(f"    {t['qid']:12} {t['label']}")

    # Unrouted entities
    unrouted = [c for c in classified if not c["primary_facet"] and not c["is_temporal"]]
    if unrouted:
        print(f"\n  Unrouted (needs manual classification):")
        for u in unrouted:
            print(f"    {u['qid']:12} {u['label']}")

    # Assemble output
    payload = {
        "seed": seed,
        "subject_resolution": subject_resolution,
        "facet_deltas": deltas,
        "temporal_entities": [
            {"qid": t["qid"], "label": t["label"]} for t in temporal
        ],
        "unrouted_entities": [
            {"qid": u["qid"], "label": u["label"]} for u in unrouted
        ],
        "classification_summary": {
            "total_candidates": len(candidates),
            "routed": routed,
            "temporal_skipped": temporal_count,
            "unrouted": unrouted_count,
            "facets_activated": len(deltas),
        },
        "recommended_next_steps": [
            {
                "action": "SCA_ROUTE",
                "reason": f"{len(deltas)} facet deltas ready for SFA routing",
                "hint": "SCA reads facet_deltas[], dispatches each to its SFA",
            },
        ],
        "_meta": {
            "rule": "Never pass PID or QID without label",
            "harvest_source": str(args.harvest),
            "routing_tiers": [
                "Tier 1: instance_of/subclass_of QID → facet anchor + type extensions",
                "Tier 2: property PIDs → SYS_PropertyMapping facet",
                "Tier 3: external ID PIDs → federation source → facet",
            ],
        },
    }

    args.output.mkdir(parents=True, exist_ok=True)
    seed_qid = seed["qid"]
    out_path = args.output / f"{seed_qid}_di_classify.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Wrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
