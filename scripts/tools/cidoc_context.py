"""
CIDOC-CRM / CRMinf context for LLM agent prompts.

Sources:
  - CIDOC/cidoc_wikidata_mapping_validated.csv (entity + property crosswalk)
  - Relationships/relationship_types_registry_master.csv (cidoc_crm_code per rel type)
  - Neo4j SYS_RelationshipType.cidoc_crm_code (after sync)

Chrystallum uses CIDOC as an alignment layer — not as the native graph schema.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CROSSWALK_CSV = ROOT / "CIDOC" / "cidoc_wikidata_mapping_validated.csv"
REGISTRY_CSV = ROOT / "Relationships" / "relationship_types_registry_master.csv"

# Core Chrystallum node → CIDOC class (from crosswalk chrystallum_fallback)
CHRYSTALLUM_ENTITY_MAP: tuple[tuple[str, str, str], ...] = (
    ("Person", "E21_Person", "Q5"),
    ("Event", "E5_Event", "Q1656682"),
    ("Place", "E53_Place", "Q82794"),
    ("Period", "E4_Period", "Q11514315"),
    ("Claim", "I2_Belief / E13_Attribute_Assignment", "Chrystallum-native"),
    ("CorpusWork", "E31_Document / I10_Provenance_Statement", "Q49848"),
    ("SubjectConcept", "E28_Conceptual_Object / E55_Type", "Q151885"),
)

FACET_CIDOC_CATEGORIES: dict[str, tuple[str, ...]] = {
    "biographic": ("Familial", "Position", "Participation", "Documentary", "Observation"),
    "military": ("Military", "Participation", "Geographic", "Causality"),
    "political": ("Political", "Diplomatic", "Position", "Causality"),
    "geographic": ("Geographic", "Spatial"),
    "religious": ("Religious", "Position"),
    "intellectual": ("Documentary", "Authorship", "Attribution"),
    "archaeological": ("Geographic", "Application", "Authorship"),
}


@lru_cache(maxsize=1)
def load_crosswalk() -> dict[str, Any]:
    by_qid: dict[str, dict[str, str]] = {}
    by_property: dict[str, dict[str, str]] = {}
    crminf: dict[str, dict[str, str]] = {}

    if not CROSSWALK_CSV.exists():
        return {"by_qid": by_qid, "by_property": by_property, "crminf": crminf}

    with open(CROSSWALK_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cidoc = (row.get("cidoc_class") or "").strip()
            if not cidoc:
                continue
            qid = (row.get("wikidata_qid") or "").strip()
            prop = (row.get("wikidata_property") or "").strip()
            entry = {
                "cidoc_class": cidoc,
                "confidence": (row.get("confidence") or "").strip(),
                "fallback": (row.get("chrystallum_fallback") or "").strip(),
                "mapping_type": (row.get("mapping_type") or "").strip(),
            }
            if qid:
                by_qid[qid] = entry
            if prop:
                for pid in prop.replace("+", "|").split("|"):
                    pid = pid.strip()
                    if pid:
                        by_property[pid] = entry
            if cidoc.startswith(("I", "J")) or "Belief" in cidoc or "Inference" in cidoc:
                crminf[cidoc] = entry
    return {"by_qid": by_qid, "by_property": by_property, "crminf": crminf}


@lru_cache(maxsize=1)
def load_relationship_cidoc_map() -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    if not REGISTRY_CSV.exists():
        return mapping
    with open(REGISTRY_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rel = (row.get("relationship_type") or "").strip().upper()
            code = (row.get("cidoc_crm_code") or "").strip()
            if not rel or not code:
                continue
            mapping[rel] = {
                "cidoc_crm_code": code,
                "cidoc_crm_kind": (row.get("cidoc_crm_kind") or "").strip(),
                "crminf_applicable": (row.get("crminf_applicable") or "").strip().lower(),
                "wikidata_property": (row.get("wikidata_property") or "").strip(),
                "lifecycle_status": (row.get("lifecycle_status") or "").strip(),
            }
    return mapping


def cidoc_for_relationship(rel_type: str) -> dict[str, str] | None:
    return load_relationship_cidoc_map().get((rel_type or "").strip().upper())


def cidoc_for_qid(qid: str) -> dict[str, str] | None:
    return load_crosswalk()["by_qid"].get((qid or "").strip().upper())


def cidoc_for_wikidata_property(pid: str) -> dict[str, str] | None:
    return load_crosswalk()["by_property"].get((pid or "").strip().upper())


def cidoc_agent_prompt_block(*, facet: str | None = None, rel_limit: int = 18) -> str:
    """Compact CIDOC-CRM / CRMinf block for system prompts."""
    crosswalk = load_crosswalk()
    rel_map = load_relationship_cidoc_map()

    lines = [
        "### CIDOC-CRM / CRMinf alignment (mandatory for predicates & entities)",
        "Chrystallum aligns to **CIDOC-CRM 7.1** + **CRMinf** for interoperability — not as native storage.",
        "When typing entities or relationships, consult:",
        "- `CIDOC/cidoc_wikidata_mapping_validated.csv`",
        "- `SYS_RelationshipType.cidoc_crm_code` / `cidoc_crm_kind` on the graph",
        "",
        "**Chrystallum node → CIDOC class:**",
    ]
    for label, cidoc, qid in CHRYSTALLUM_ENTITY_MAP:
        lines.append(f"- `{label}` → {cidoc}" + (f" (Wikidata {qid})" if qid.startswith("Q") else f" ({qid})"))

    lines.extend(
        [
            "",
            "**CRMinf claim epistemics:**",
            "- `CorpusWork` / passage = evidence (I10_Provenance_Statement, P1343)",
            "- `Claim` = I2_Belief / E13_Attribute_Assignment — confidence on Claim, not on canonical edge",
            "- Human validation = I7_Belief_Adoption; promotion to canonical edge = adopted belief",
            "- Multi-agent debate / Fischer lint = I5_Inference_Making",
            "",
            "**Wikidata property → CIDOC (common):**",
        ]
    )
    key_pids = ("P31", "P39", "P22", "P25", "P40", "P26", "P710", "P607", "P276", "P571", "P570", "P1343")
    for pid in key_pids:
        hit = crosswalk["by_property"].get(pid)
        if hit:
            lines.append(f"- `{pid}` → {hit['cidoc_class']} ({hit.get('confidence', '?')})")

    categories = FACET_CIDOC_CATEGORIES.get((facet or "").lower()) if facet else None
    rel_samples: list[tuple[str, dict[str, str]]] = []
    if REGISTRY_CSV.exists():
        with open(REGISTRY_CSV, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                cat = (row.get("category") or "").strip()
                rel = (row.get("relationship_type") or "").strip().upper()
                code = (row.get("cidoc_crm_code") or "").strip()
                if not rel or not code:
                    continue
                if categories and cat not in categories:
                    continue
                if (row.get("lifecycle_status") or "") != "implemented":
                    continue
                rel_samples.append(
                    (
                        rel,
                        {
                            "cidoc_crm_code": code,
                            "wikidata_property": (row.get("wikidata_property") or "").strip(),
                        },
                    )
                )

    if rel_samples:
        lines.append("")
        facet_label = f" ({facet} facet)" if facet else ""
        lines.append(f"**Relationship → CIDOC property{facet_label} (implemented sample):**")
        for rel, meta in rel_samples[:rel_limit]:
            pid = meta.get("wikidata_property") or ""
            pid_note = f", {pid}" if pid else ""
            lines.append(f"- `{rel}` → {meta['cidoc_crm_code']}{pid_note}")

    crminf_rows = list(crosswalk["crminf"].items())[:6]
    if crminf_rows:
        lines.append("")
        lines.append("**CRMinf classes (no direct Wikidata item — use Claim layer):**")
        for cls, meta in crminf_rows:
            fb = meta.get("fallback") or ""
            lines.append(f"- `{cls}` → {fb[:90]}")

    lines.extend(
        [
            "",
            "**Agent rules:**",
            "- Prefer relationship types with `cidoc_crm_code` in SYS_RelationshipType.",
            "- If Wikidata PID maps to a CIDOC property, use the registry relationship type — do not invent a parallel predicate.",
            "- Entity typing: E21 for persons, E5 for events, E53 for places unless crosswalk says otherwise.",
            "- Absence of CIDOC mapping → document in Claim.notes; do not force a wrong CRM class.",
        ]
    )
    return "\n".join(lines)


def append_cidoc_context(system_prompt: str, **kwargs: Any) -> str:
    block = cidoc_agent_prompt_block(**kwargs)
    if block.strip() in system_prompt:
        return system_prompt
    return f"{system_prompt.rstrip()}\n\n{block}"


def append_agent_governance_context(
    system_prompt: str,
    seed_qid: str = "Q17167",
    *,
    driver: Any | None = None,
    facet: str | None = None,
    include_graph: bool = True,
) -> str:
    """Chain: republic graph context + relationship registry + CIDOC (single injection)."""
    if include_graph:
        from scripts.agents.republic_graph_context import append_republic_graph_context

        return append_republic_graph_context(system_prompt, seed_qid, driver=driver, facet=facet)
    from scripts.tools.sys_registry import append_relationship_registry_context

    out = append_relationship_registry_context(system_prompt, facet=facet)
    return append_cidoc_context(out, facet=facet)
