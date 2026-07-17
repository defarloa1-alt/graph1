#!/usr/bin/env python3
"""
Live Roman Republic (Q17167) graph context for LLM agents.

Every agent that proposes structure or interprets the domain should call
get_republic_graph_context_prompt_block() and inject the result into the
system prompt (or first user message) before reasoning.

Falls back to output/baseline/Q17167_facet_hierarchy_baseline.json when Neo4j
is unavailable.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

DEFAULT_SEED_QID = "Q17167"
DEFAULT_DOMAIN_ID = "domain_roman_republic"
BASELINE_PATH = ROOT / "output" / "baseline" / "Q17167_facet_hierarchy_baseline.json"
CLAIMS_ARTIFACT = ROOT / "JSON" / "wikidata" / "integrated" / "Q17167_validated_claims_v2.json"

THRESHOLD_NAMES = (
    "level2_child_overload",
    "crosslink_thresh",
    "claim_promotion_confidence",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_baseline() -> dict[str, Any] | None:
    if not BASELINE_PATH.exists():
        return None
    with open(BASELINE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _pending_tracks() -> list[str]:
    pending: list[str] = []
    if CLAIMS_ARTIFACT.exists():
        pending.append(
            "Factual Wikidata claims (JSON/wikidata/integrated/Q17167_validated_claims_v2.json) — not yet written to graph"
        )
    return pending


def fetch_republic_graph_context(
    session: Any,
    *,
    seed_qid: str = DEFAULT_SEED_QID,
    domain_id: str = DEFAULT_DOMAIN_ID,
    include_decompositions: bool = True,
) -> dict[str, Any]:
    """Load structured graph context from Neo4j."""
    seed_qid = seed_qid.strip().upper()
    domain = session.run(
        """
        MATCH (sd:SubjectDomain)
        WHERE sd.seed_qid = $seed_qid OR sd.domain_id = $domain_id
        RETURN sd.domain_id AS domain_id, sd.label AS label, sd.seed_qid AS seed_qid,
               elementId(sd) AS eid
        LIMIT 1
        """,
        seed_qid=seed_qid,
        domain_id=domain_id,
    ).single()

    if not domain:
        return {"seed_qid": seed_qid, "found": False, "captured_at": _utc_now_iso()}

    period = session.run(
        """
        MATCH (p:Period {qid: $seed_qid})
        RETURN p.qid AS qid, p.label AS label, elementId(p) AS eid
        LIMIT 1
        """,
        seed_qid=seed_qid,
    ).single()

    umbrellas = [
        dict(r)
        for r in session.run(
            """
            MATCH (sd:SubjectDomain {seed_qid: $seed_qid})
                  -[:HAS_SUBJECT_CONCEPT]->(u:SubjectConcept)
            WHERE u.source = 'di_facet_umbrella' OR 'FacetUmbrella' IN labels(u)
            OPTIONAL MATCH (u)<-[:PART_OF]-(sc:SubjectConcept {source: 'di_proposal'})
            RETURN u.subject_id AS subject_id, u.label AS label,
                   u.source_facet AS facet, count(sc) AS decompositions
            ORDER BY facet
            """,
            seed_qid=seed_qid,
        )
    ]

    decompositions: list[dict[str, Any]] = []
    if include_decompositions:
        decompositions = [
            dict(r)
            for r in session.run(
                """
                MATCH (sd:SubjectDomain {seed_qid: $seed_qid})
                      -[:HAS_SUBJECT_CONCEPT]->(u:SubjectConcept)
                WHERE u.source = 'di_facet_umbrella' OR 'FacetUmbrella' IN labels(u)
                MATCH (u)<-[:PART_OF]-(sc:SubjectConcept {source: 'di_proposal'})
                RETURN u.source_facet AS facet, u.subject_id AS umbrella_id,
                       sc.subject_id AS subject_id, sc.label AS label
                ORDER BY facet, sc.label
                """,
                seed_qid=seed_qid,
            )
        ]

    di_stats = session.run(
        """
        MATCH (sc:SubjectConcept {source: 'di_proposal', seed_qid: $seed_qid})
        OPTIONAL MATCH (sc)-[:PART_OF]->(u:SubjectConcept)
        WHERE u.source = 'di_facet_umbrella' OR 'FacetUmbrella' IN labels(u)
        RETURN count(sc) AS total,
               count(u) AS part_of_umbrella
        """,
        seed_qid=seed_qid,
    ).single()

    training_runs = session.run(
        """
        MATCH (tr:SFA_TrainingRun {seed_qid: $seed_qid})
        RETURN count(tr) AS count
        """,
        seed_qid=seed_qid,
    ).single()["count"]

    uses_type = [
        dict(r)
        for r in session.run(
            """
            MATCH (sd:SubjectDomain {seed_qid: $seed_qid})-[:USES_TYPE]->(wt:WikidataType)
            RETURN wt.qid AS qid, wt.label AS label
            ORDER BY wt.label
            """,
            seed_qid=seed_qid,
        )
    ]

    thresholds = [
        dict(r)
        for r in session.run(
            """
            MATCH (t:SYS_Threshold)
            WHERE t.name IN $names
            RETURN t.name AS name, t.value AS value, t.unit AS unit
            ORDER BY t.name
            """,
            names=list(THRESHOLD_NAMES),
        )
    ]

    return {
        "seed_qid": seed_qid,
        "found": True,
        "source": "neo4j",
        "captured_at": _utc_now_iso(),
        "subject_domain": dict(domain),
        "period": dict(period) if period else None,
        "facet_umbrellas": umbrellas,
        "decompositions": decompositions,
        "di_proposals": {
            "total": di_stats["total"] if di_stats else 0,
            "part_of_umbrella": di_stats["part_of_umbrella"] if di_stats else 0,
        },
        "sfa_training_runs": training_runs,
        "uses_type": uses_type,
        "thresholds": thresholds,
        "pending_tracks": _pending_tracks(),
        "navigation": {
            "topic_hub": "SubjectDomain (Roman Republic · Subject Domain)",
            "temporal_anchor": "Period Q17167 — do not expand for subject tree",
            "hierarchy": "SubjectDomain -[:HAS_SUBJECT_CONCEPT]-> FacetUmbrella <-[:PART_OF]- di_proposal",
        },
    }


def _decompositions_from_enriched() -> list[dict[str, Any]]:
    path = ROOT / "output" / "di_proposals" / "Q17167_proposals_enriched.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    rows: list[dict[str, Any]] = []
    for proposal in doc.get("proposals", []):
        if proposal.get("status") != "approved":
            continue
        facet = (proposal.get("source_facet") or "").lower()
        subject_id = proposal.get("subject_id")
        if not facet or not subject_id:
            continue
        rows.append(
            {
                "facet": facet,
                "umbrella_id": f"sc_q17167_facet_{facet}",
                "subject_id": subject_id,
                "label": proposal.get("label", ""),
            }
        )
    return rows


def _baseline_to_context(baseline: dict[str, Any]) -> dict[str, Any]:
    decompositions = _decompositions_from_enriched()
    return {
        "seed_qid": baseline.get("subject_domain", {}).get("seed_qid", DEFAULT_SEED_QID),
        "found": True,
        "source": "baseline_json",
        "captured_at": baseline.get("captured", _utc_now_iso()),
        "subject_domain": baseline.get("subject_domain"),
        "period": baseline.get("period"),
        "facet_umbrellas": baseline.get("facet_umbrellas", []),
        "decompositions": decompositions,
        "di_proposals": baseline.get("di_proposals", {}),
        "sfa_training_runs": len(baseline.get("sfa_training", [])),
        "uses_type": baseline.get("uses_type", []),
        "thresholds": [],
        "pending_tracks": _pending_tracks(),
        "navigation": {
            "topic_hub": "SubjectDomain (Roman Republic · Subject Domain)",
            "temporal_anchor": "Period Q17167 — do not expand for subject tree",
            "hierarchy": "SubjectDomain -[:HAS_SUBJECT_CONCEPT]-> FacetUmbrella <-[:PART_OF]- di_proposal",
        },
    }


def load_republic_graph_context(
    seed_qid: str = DEFAULT_SEED_QID,
    *,
    driver: Any | None = None,
    include_decompositions: bool = True,
) -> dict[str, Any]:
    """Load context from Neo4j, falling back to baseline JSON."""
    seed_qid = seed_qid.strip().upper()
    ctx: dict[str, Any] | None = None

    try:
        from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME
        from neo4j import GraphDatabase

        db = NEO4J_DATABASE or "neo4j"
        owns_driver = driver is None
        active_driver = driver
        if owns_driver:
            active_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        try:
            with active_driver.session(database=db) as session:
                ctx = fetch_republic_graph_context(
                    session,
                    seed_qid=seed_qid,
                    include_decompositions=include_decompositions,
                )
        finally:
            if owns_driver and active_driver is not None:
                active_driver.close()
    except Exception as exc:
        baseline = _load_baseline()
        if baseline:
            result = _baseline_to_context(baseline)
            result["fallback_reason"] = str(exc)
            return result
        return {
            "seed_qid": seed_qid,
            "found": False,
            "source": "error",
            "error": str(exc),
            "captured_at": _utc_now_iso(),
        }

    if ctx and ctx.get("found"):
        return ctx

    baseline = _load_baseline()
    if baseline:
        return _baseline_to_context(baseline)

    return ctx or {
        "seed_qid": seed_qid,
        "found": False,
        "source": "missing",
        "captured_at": _utc_now_iso(),
    }


def format_republic_graph_context_markdown(ctx: dict[str, Any]) -> str:
    """Compact markdown block for LLM system prompts (~1–3k tokens)."""
    if not ctx.get("found"):
        return (
            "## Roman Republic graph context\n"
            f"No SubjectDomain found for {ctx.get('seed_qid', DEFAULT_SEED_QID)}. "
            "Use query_graph before proposing structure.\n"
        )

    sd = ctx.get("subject_domain") or {}
    period = ctx.get("period") or {}
    lines = [
        "## Roman Republic graph context (authoritative — read before proposing)",
        "",
        f"Captured: {ctx.get('captured_at', '?')} via {ctx.get('source', '?')}",
        "",
        "**Topic hub:** "
        f"SubjectDomain `{sd.get('domain_id', DEFAULT_DOMAIN_ID)}` — "
        f"{sd.get('label', 'Roman Republic · Subject Domain')}",
        "**Temporal anchor only:** "
        f"Period `{period.get('qid', 'Q17167')}` ({period.get('label', 'Roman Republic')}) — "
        "41k+ IN_PERIOD edges; not the subject decomposition tree.",
        "",
        "**Hierarchy:** "
        + (ctx.get("navigation") or {}).get(
            "hierarchy",
            "SubjectDomain → FacetUmbrella ← PART_OF di_proposal",
        ),
        "",
        "### Facet umbrellas",
        "| Facet | Umbrella ID | Label | Decomps |",
        "|-------|-------------|-------|---------|",
    ]

    for u in ctx.get("facet_umbrellas") or []:
        lines.append(
            f"| {u.get('facet', '?')} | `{u.get('subject_id', '?')}` | "
            f"{u.get('label', '?')} | {u.get('decompositions', 0)} |"
        )

    di = ctx.get("di_proposals") or {}
    lines.extend(
        [
            "",
            f"**DI proposals in graph:** {di.get('total', 0)} total, "
            f"{di.get('part_of_umbrella', 0)} under facet umbrellas",
            f"**SFA training runs:** {ctx.get('sfa_training_runs', 0)}",
        ]
    )

    if ctx.get("uses_type"):
        types_str = ", ".join(
            f"{t.get('label', '?')} ({t.get('qid', '?')})" for t in ctx["uses_type"]
        )
        lines.append(f"**Seed P31 types:** {types_str}")

    if ctx.get("thresholds"):
        lines.append("")
        lines.append("### Key thresholds (SYS_Threshold)")
        for t in ctx["thresholds"]:
            unit = f" {t['unit']}" if t.get("unit") else ""
            lines.append(f"- `{t.get('name')}` = {t.get('value')}{unit}")

    decomps = ctx.get("decompositions") or []
    if decomps:
        lines.append("")
        lines.append("### Existing decomposition SubjectConcepts (do not duplicate)")
        by_facet: dict[str, list[dict[str, Any]]] = {}
        for row in decomps:
            by_facet.setdefault(str(row.get("facet", "?")), []).append(row)
        for facet in sorted(by_facet):
            lines.append(f"**{facet}**")
            for row in by_facet[facet]:
                lines.append(f"- `{row.get('subject_id')}` — {row.get('label', '?')}")

    pending = ctx.get("pending_tracks") or []
    if pending:
        lines.append("")
        lines.append("### Not yet in graph")
        for item in pending:
            lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "### Agent rules",
            "- Propose only against this scaffold; use `query_graph` to verify before adding nodes.",
            "- New decompositions must `PART_OF` a facet umbrella — never attach directly to SubjectDomain.",
            "- Do not confuse SubjectDomain with Period Q17167 when navigating.",
            "- All relationship predicates must come from `relationship_types_registry_master.csv` / `SYS_RelationshipType`.",
            "- Align entities and predicates to CIDOC-CRM / CRMinf (see appended governance blocks).",
            "- Run `python -m scripts.tools.validate_sys_registry` when registry alignment is uncertain.",
        ]
    )
    return "\n".join(lines)


def get_republic_graph_context_prompt_block(
    seed_qid: str = DEFAULT_SEED_QID,
    *,
    driver: Any | None = None,
    include_decompositions: bool = True,
) -> str:
    """Primary entry point for agents: markdown context block for system prompts."""
    ctx = load_republic_graph_context(
        seed_qid,
        driver=driver,
        include_decompositions=include_decompositions,
    )
    return format_republic_graph_context_markdown(ctx)


def append_republic_graph_context(
    system_prompt: str,
    seed_qid: str,
    *,
    driver: Any | None = None,
    facet: str | None = None,
) -> str:
    """Append graph context + relationship registry + CIDOC alignment to system prompt."""
    block = get_republic_graph_context_prompt_block(seed_qid, driver=driver)
    if block.strip() in system_prompt:
        out = system_prompt
    else:
        out = f"{system_prompt.rstrip()}\n\n{block}"
    try:
        from scripts.tools.sys_registry import append_relationship_registry_context

        out = append_relationship_registry_context(out, facet=facet)
    except ImportError:
        pass
    try:
        from scripts.tools.cidoc_context import append_cidoc_context

        out = append_cidoc_context(out, facet=facet)
    except ImportError:
        pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Print Roman Republic graph context for LLM agents")
    ap.add_argument("--seed", default=DEFAULT_SEED_QID)
    ap.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    ap.add_argument("--write", action="store_true", help="Write markdown to output/context/")
    ap.add_argument("--no-decompositions", action="store_true")
    args = ap.parse_args()

    ctx = load_republic_graph_context(
        args.seed,
        include_decompositions=not args.no_decompositions,
    )
    if args.json:
        print(json.dumps(ctx, indent=2, ensure_ascii=False))
    else:
        md = format_republic_graph_context_markdown(ctx)
        print(md)
        if args.write:
            out = ROOT / "output" / "context" / f"{args.seed.upper()}_republic_graph_context.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(md + "\n", encoding="utf-8")
            print(f"\nWrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
