#!/usr/bin/env python3
"""Schema Specialist — Neo-grounded LLM proposes pack schema (no Neo writes).

Usage (repo root):
  python -m chrystal_2.agents.schema_specialist propose --qid Q17167 --domain-id roman_republic
  python -m chrystal_2.agents.schema_specialist propose --qid Q17167 --domain-id roman_republic --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

AGENT_DIR = Path(__file__).resolve().parent
PRINCIPLES_PATH = AGENT_DIR / "PRINCIPLES.md"
PACKS_DIR = ROOT / "JSON" / "wikidata" / "packs"

DECISIONS = frozenset(
    {
        "subject_domain_property",
        "first_class_node",
        "first_class_relationship",
        "identity_tether",
        "ignore",
        "defer",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _anthropic_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY") or ""
    if key:
        return key.strip().strip("\"'")
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("ANTHROPIC_API_KEY not set in environment or .env")


def load_principles() -> str:
    return PRINCIPLES_PATH.read_text(encoding="utf-8")


def load_pack(qid: str, pack_path: Path | None = None) -> dict[str, Any]:
    path = pack_path or (PACKS_DIR / f"{qid}_pack_library.json")
    if not path.exists():
        raise SystemExit(
            f"Missing pack library: {path}\n"
            f"Run: python chrystal_2/harvest/build_pack_library.py --qid {qid}"
        )
    pack = json.loads(path.read_text(encoding="utf-8"))
    meta = pack.get("_meta") or {}
    if not meta.get("labeled"):
        raise SystemExit(f"Pack library not labeled: {path}")
    return pack


def claims_index(pack: dict[str, Any]) -> list[dict[str, Any]]:
    """Token-safe index: one row per PID with samples (not full claim trees)."""
    stmts = pack.get("statements") or {}
    claims = stmts.get("claims") or {}
    labels = stmts.get("property_labels") or {}
    rows: list[dict[str, Any]] = []
    for pid in sorted(claims.keys(), key=lambda x: (len(x), x)):
        entries = claims[pid]
        mains = [(e.get("mainsnak") or {}) for e in entries]
        datatype = next((m.get("datatype") for m in mains if m.get("datatype")), None)
        prop_label = labels.get(pid) or next(
            (m.get("property_label") for m in mains if m.get("property_label")), pid
        )
        samples: list[dict[str, Any]] = []
        for m in mains[:3]:
            samples.append(
                {
                    "value": m.get("value"),
                    "value_label": m.get("value_label"),
                    "datatype": m.get("datatype"),
                }
            )
        rows.append(
            {
                "pid": pid,
                "property_label": prop_label,
                "datatype": datatype,
                "statement_count": len(entries),
                "samples": samples,
            }
        )
    return rows


def load_neo_context(domain_id: str) -> dict[str, Any]:
    if "7fe339d2" not in (NEO4J_URI or ""):
        raise SystemExit(
            f"Refusing: NEO4J_URI is not chrystal_2 (7fe339d2): {NEO4J_URI}"
        )
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            node_types = [
                dict(r)
                for r in session.run(
                    """
                    MATCH (n:SYS_NodeType)
                    RETURN n.name AS name, n.domain AS domain, n.description AS description
                    ORDER BY n.name
                    """
                )
            ]
            rel_types = [
                dict(r)
                for r in session.run(
                    """
                    MATCH (r:SYS_RelationshipType)
                    RETURN coalesce(r.rel_type, r.name) AS relationship_type,
                           r.category AS category,
                           r.description AS description,
                           r.lifecycle_status AS lifecycle_status
                    ORDER BY coalesce(r.rel_type, r.name)
                    """
                )
            ]
            facets = [
                dict(r)
                for r in session.run(
                    """
                    MATCH (f:Facet)
                    RETURN f.key AS key, f.label AS label
                    ORDER BY f.key
                    """
                )
            ]
            federations = [
                dict(r)
                for r in session.run(
                    """
                    MATCH (fs:SYS_FederationSource)
                    RETURN fs.source_id AS source_id, fs.label AS label,
                           fs.scope AS scope, fs.status AS status,
                           fs.tool_names AS tool_names
                    ORDER BY fs.source_id
                    """
                )
            ]
            sd = session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                OPTIONAL MATCH (sd)-[:CONTAINS]->(s:SFASlot)
                RETURN sd.domain_id AS domain_id, sd.seed_qid AS seed_qid,
                       sd.label AS label, sd.kind AS kind,
                       sd.start_year AS start_year, sd.end_year AS end_year,
                       sd.status AS status, sd.reference_json AS reference_json,
                       count(s) AS sfa_slots
                """,
                domain_id=domain_id,
            ).single()
            subject_domain = dict(sd) if sd else None
    finally:
        driver.close()

    return {
        "instance": "chrystal_2",
        "node_types": node_types,
        "relationship_types": rel_types,
        "facets": facets,
        "federations": federations,
        "subject_domain": subject_domain,
    }


def build_user_payload(
    pack: dict[str, Any],
    neo: dict[str, Any],
    domain_id: str,
) -> dict[str, Any]:
    return {
        "task": (
            "Propose a schema for every seed PID in claims_index. "
            "Use only registry node_types and relationship_types. "
            "Return JSON only."
        ),
        "domain_id": domain_id,
        "seed": pack.get("seed"),
        "counts": pack.get("counts"),
        "external_ids_sample": (pack.get("external_ids") or [])[:40],
        "forward_links_sample": (pack.get("forward_links") or [])[:40],
        "backlinks_summary": {
            "accepted_count": (pack.get("counts") or {}).get("backlinks_accepted"),
            "note": "Neighbor cards only; do not expand into full statements this pass.",
            "sample": (pack.get("backlinks") or [])[:15],
        },
        "neo_registry": {
            "node_types": neo["node_types"],
            "relationship_types": [
                {
                    "relationship_type": r.get("relationship_type"),
                    "category": r.get("category"),
                    "lifecycle_status": r.get("lifecycle_status"),
                    "description": (r.get("description") or "")[:200],
                }
                for r in neo["relationship_types"]
            ],
            "facets": neo["facets"],
            "federations": neo["federations"],
            "subject_domain": neo["subject_domain"],
        },
        "claims_index": claims_index(pack),
        "required_output_schema": {
            "_meta": {
                "mode": "schema_specialist_llm",
                "grounding": ["neo_registry", "pack_library", "principles"],
                "writes_neo": False,
                "seed_qid": "...",
                "domain_id": domain_id,
                "generated_at": "ISO-8601",
            },
            "seed": {"qid": "...", "label": "...", "description": "..."},
            "decision_counts": {"subject_domain_property": 0},
            "sfa_shells": {
                "action": "ensure_inert_slots",
                "count": 18,
                "note": "One inert SFASlot per Facet; Domain lifecycle owns activation",
            },
            "proposals": [
                {
                    "pid": "P571",
                    "property_label": "...",
                    "datatype": "time",
                    "decision": "subject_domain_property",
                    "rationale": "one short sentence",
                    "property": "start_year",
                    "node_label": None,
                    "relationship_type": None,
                    "federation": None,
                }
            ],
        },
    }


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def validate_proposal(proposal: dict[str, Any], claims: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    props = proposal.get("proposals")
    if not isinstance(props, list) or not props:
        return ["proposals must be a non-empty list"]
    by_pid = {c["pid"] for c in claims}
    seen: set[str] = set()
    for i, row in enumerate(props):
        if not isinstance(row, dict):
            errors.append(f"proposals[{i}] not an object")
            continue
        pid = row.get("pid")
        if pid not in by_pid:
            errors.append(f"unknown pid in proposal: {pid}")
        if pid in seen:
            errors.append(f"duplicate pid: {pid}")
        seen.add(pid)
        dec = row.get("decision")
        if dec not in DECISIONS:
            errors.append(f"{pid}: invalid decision {dec!r}")
        if not row.get("rationale"):
            errors.append(f"{pid}: missing rationale")
    missing = sorted(by_pid - seen)
    if missing:
        errors.append(f"missing proposals for {len(missing)} PIDs: {missing[:12]}...")
    return errors


def call_llm(system: str, user_payload: dict[str, Any], model: str) -> dict[str, Any]:
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit("pip install anthropic") from exc

    client = anthropic.Anthropic(api_key=_anthropic_key())
    user_text = (
        "Design the schema proposal for this pack.\n\n"
        + json.dumps(user_payload, ensure_ascii=False, indent=2)
    )
    msg = client.messages.create(
        model=model,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": user_text}],
    )
    parts = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    raw = "\n".join(parts)
    try:
        return _extract_json(raw)
    except json.JSONDecodeError as exc:
        debug = PACKS_DIR / "_last_schema_specialist_raw.txt"
        debug.write_text(raw, encoding="utf-8")
        raise SystemExit(
            f"LLM did not return valid JSON ({exc}). Raw saved to {debug}"
        ) from exc


def propose(
    qid: str,
    domain_id: str,
    *,
    pack_path: Path | None = None,
    output: Path | None = None,
    model: str = "claude-sonnet-4-5",
    dry_run: bool = False,
) -> Path | None:
    pack = load_pack(qid, pack_path)
    neo = load_neo_context(domain_id)
    payload = build_user_payload(pack, neo, domain_id)
    index = payload["claims_index"]

    out_path = output or (PACKS_DIR / f"{qid}_schema_proposal.json")
    if dry_run:
        preview = {
            "_meta": {
                "mode": "dry_run",
                "claims": len(index),
                "node_types": len(neo["node_types"]),
                "relationship_types": len(neo["relationship_types"]),
                "subject_domain": neo["subject_domain"],
            },
            "payload_bytes": len(json.dumps(payload)),
        }
        print(json.dumps(preview, indent=2))
        return None

    system = load_principles()
    proposal = call_llm(system, payload, model)

    # Stamp authority meta (do not trust model for these)
    meta = proposal.setdefault("_meta", {})
    meta["mode"] = "schema_specialist_llm"
    meta["grounding"] = ["neo_registry", "pack_library", "principles"]
    meta["writes_neo"] = False
    meta["seed_qid"] = qid
    meta["domain_id"] = domain_id
    meta["generated_at"] = _now()
    meta["model"] = model
    meta["principles"] = str(PRINCIPLES_PATH.relative_to(ROOT)).replace("\\", "/")
    meta["pack_library"] = str(
        (pack_path or (PACKS_DIR / f"{qid}_pack_library.json")).relative_to(ROOT)
    ).replace("\\", "/")
    proposal["seed"] = pack.get("seed")

    # decision_counts
    counts: dict[str, int] = {}
    for row in proposal.get("proposals") or []:
        if isinstance(row, dict):
            d = row.get("decision") or "unknown"
            counts[d] = counts.get(d, 0) + 1
    proposal["decision_counts"] = counts

    errors = validate_proposal(proposal, index)
    if errors:
        bad = PACKS_DIR / f"{qid}_schema_proposal.INVALID.json"
        bad.write_text(
            json.dumps(proposal, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("Validation errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(f"Proposal invalid; wrote {bad}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(proposal, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out_path.relative_to(ROOT)}".replace("\\", "/"))
    print("decision_counts:", counts)
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chrystal 2 Schema Specialist")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("propose", help="LLM schema proposal from pack library + Neo")
    p.add_argument("--qid", required=True)
    p.add_argument("--domain-id", required=True)
    p.add_argument("--pack", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--model", default="claude-sonnet-4-5")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Load Neo + pack index only; no LLM call",
    )

    args = parser.parse_args(argv)
    if args.cmd == "propose":
        propose(
            args.qid.strip().upper(),
            args.domain_id.strip(),
            pack_path=args.pack,
            output=args.output,
            model=args.model,
            dry_run=args.dry_run,
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
