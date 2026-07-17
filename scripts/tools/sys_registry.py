"""
SYS registry validation — CSV master + Neo4j SYS_* cross-check (ADR / epistemic model).

Canonical source: Relationships/relationship_types_registry_master.csv
Graph mirror: SYS_RelationshipType nodes (may lag CSV; lifecycle_status often absent on graph)
Operational routing: SYS_Policy BacklinkRouting decision_table edge_type values
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_CSV = ROOT / "Relationships" / "relationship_types_registry_master.csv"
DEFAULT_FACET_JSON = ROOT / "Facets" / "facet_registry_master.json"

# Biographic / harvest edge types commonly emitted before CSV catch-up
BIOGRAPHIC_EDGE_ALLOWLIST = frozenset(
    {
        "RAISED_LEGION",
        "HEADED",
        "ORGANIZED",
        "COMMISSIONED",
        "FOUNDED",
        "PARTICIPATED_IN",
        "POSITION_HELD",
        "HAD_ROLE",
        "CHAIRED",
        "CHILD_OF",
        "PARENT_OF",
        "SPOUSE_OF",
        "SIBLING_OF",
        "HALF_SIBLING_OF",
        "FATHER_OF",
        "MOTHER_OF",
        "RELATED_TO",
        "APPOINTED_BY",
        "INFLUENCED",
        "NAMESAKE_OF",
    }
)


@dataclass(frozen=True)
class RelationshipRegistryEntry:
    relationship_type: str
    category: str
    description: str
    lifecycle_status: str
    wikidata_property: str | None
    directionality: str
    status: str

    @property
    def claim_allowed(self) -> bool:
        return self.lifecycle_status in {"implemented", "candidate"}


@dataclass
class RelationshipValidation:
    relationship_type: str
    normalized: str
    valid: bool
    lifecycle_status: str | None
    in_csv: bool
    in_graph: bool
    in_backlink_routing: bool
    wikidata_property: str | None
    message: str
    registry_status: str  # implemented | candidate | routing_only | unregistered

    def to_claim_properties(self) -> dict[str, Any]:
        return {
            "registry_status": self.registry_status,
            "registry_validated": self.valid,
        }


@dataclass
class SysRegistryAudit:
    csv_implemented: int = 0
    csv_candidate: int = 0
    csv_total: int = 0
    graph_rel_types: int = 0
    graph_with_rel_type_prop: int = 0
    csv_impl_missing_in_graph: list[str] = field(default_factory=list)
    graph_not_in_csv: list[str] = field(default_factory=list)
    backlink_edge_types: list[str] = field(default_factory=list)
    backlink_not_in_csv: list[str] = field(default_factory=list)
    backlink_not_implemented: list[str] = field(default_factory=list)
    sys_label_counts: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=1)
def load_relationship_registry(csv_path: str | None = None) -> dict[str, RelationshipRegistryEntry]:
    path = Path(csv_path) if csv_path else DEFAULT_REGISTRY_CSV
    entries: dict[str, RelationshipRegistryEntry] = {}
    for row in _read_csv(path):
        rel = (row.get("relationship_type") or "").strip().upper()
        if not rel:
            continue
        entries[rel] = RelationshipRegistryEntry(
            relationship_type=rel,
            category=(row.get("category") or "").strip(),
            description=(row.get("description") or "").strip(),
            lifecycle_status=(row.get("lifecycle_status") or "candidate").strip().lower(),
            wikidata_property=(row.get("wikidata_property") or "").strip().upper() or None,
            directionality=(row.get("directionality") or "").strip(),
            status=(row.get("status") or "").strip(),
        )
    return entries


@lru_cache(maxsize=1)
def pid_to_relationship_type(csv_path: str | None = None) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for rel, entry in load_relationship_registry(csv_path).items():
        if entry.wikidata_property and entry.lifecycle_status == "implemented":
            mapping[entry.wikidata_property] = rel
    return mapping


def normalize_relationship_type(rel_type: str) -> str:
    return (rel_type or "").strip().upper()


def validate_relationship_type(
    rel_type: str,
    *,
    pred_pid: str | None = None,
    csv_path: str | None = None,
    graph_rel_types: set[str] | None = None,
    backlink_edge_types: set[str] | None = None,
    strict: bool = False,
) -> RelationshipValidation:
    """Validate a proposed relationship type against CSV (+ optional graph / BacklinkRouting)."""
    normalized = normalize_relationship_type(rel_type)
    registry = load_relationship_registry(csv_path)
    entry = registry.get(normalized)

    in_csv = entry is not None
    lifecycle = entry.lifecycle_status if entry else None
    in_graph = bool(graph_rel_types and normalized in graph_rel_types)
    in_backlink = bool(backlink_edge_types and normalized in backlink_edge_types)

    if in_csv and entry and entry.claim_allowed:
        valid = True
        reg_status = entry.lifecycle_status
        msg = f"Registered ({entry.lifecycle_status}): {entry.category} — {entry.description[:120]}"
    elif in_backlink or normalized in BIOGRAPHIC_EDGE_ALLOWLIST:
        valid = not strict
        reg_status = "routing_only"
        msg = (
            f"{normalized} used in BacklinkRouting/harvest but missing or not implemented in CSV — "
            "add to relationship_types_registry_master.csv"
        )
    else:
        valid = False
        reg_status = "unregistered"
        msg = f"{normalized} not in relationship_types_registry_master.csv"

    if pred_pid and not entry:
        pid_norm = pred_pid.strip().upper()
        mapped = pid_to_relationship_type(csv_path).get(pid_norm)
        if mapped and mapped != normalized:
            msg += f"; PID {pid_norm} maps to {mapped} in CSV"

    return RelationshipValidation(
        relationship_type=rel_type,
        normalized=normalized,
        valid=valid,
        lifecycle_status=lifecycle,
        in_csv=in_csv,
        in_graph=in_graph,
        in_backlink_routing=in_backlink,
        wikidata_property=entry.wikidata_property if entry else None,
        message=msg,
        registry_status=reg_status,
    )


def fetch_graph_relationship_types(session: Any) -> set[str]:
    rows = session.run(
        """
        MATCH (n:SYS_RelationshipType)
        RETURN coalesce(n.rel_type, n.name) AS rt
        """
    )
    out: set[str] = set()
    for row in rows:
        rt = normalize_relationship_type(row["rt"] or "")
        if rt:
            out.add(rt)
    return out


def fetch_backlink_edge_types(session: Any) -> set[str]:
    row = session.run(
        "MATCH (p:SYS_Policy {name: 'BacklinkRouting'}) RETURN p.decision_table AS dt"
    ).single()
    if not row or not row["dt"]:
        return set()
    try:
        table = json.loads(row["dt"])
    except json.JSONDecodeError:
        return set()
    return {
        normalize_relationship_type(r.get("edge_type") or "")
        for r in table
        if r.get("edge_type")
    }


def fetch_sys_label_counts(session: Any) -> dict[str, int]:
    rows = session.run(
        """
        MATCH (n) WHERE any(l IN labels(n) WHERE l STARTS WITH 'SYS_')
        UNWIND labels(n) AS lab
        WITH lab WHERE lab STARTS WITH 'SYS_'
        RETURN lab, count(*) AS c ORDER BY c DESC
        """
    )
    return {row["lab"]: row["c"] for row in rows}


def audit_sys_registry(session: Any, *, csv_path: str | None = None) -> SysRegistryAudit:
    """Cross-validate CSV master vs Neo4j SYS_RelationshipType and BacklinkRouting."""
    registry = load_relationship_registry(csv_path)
    audit = SysRegistryAudit()
    audit.csv_total = len(registry)
    audit.csv_implemented = sum(1 for e in registry.values() if e.lifecycle_status == "implemented")
    audit.csv_candidate = sum(1 for e in registry.values() if e.lifecycle_status == "candidate")

    graph_types = fetch_graph_relationship_types(session)
    audit.graph_rel_types = len(graph_types)
    audit.graph_with_rel_type_prop = len(graph_types)

    csv_impl = {k for k, v in registry.items() if v.lifecycle_status == "implemented"}
    audit.csv_impl_missing_in_graph = sorted(csv_impl - graph_types)[:50]
    audit.graph_not_in_csv = sorted(graph_types - set(registry.keys()))[:50]

    backlink = fetch_backlink_edge_types(session)
    audit.backlink_edge_types = sorted(backlink)
    audit.backlink_not_in_csv = sorted(backlink - set(registry.keys()))
    audit.backlink_not_implemented = sorted(
        rt for rt in backlink
        if rt in registry and registry[rt].lifecycle_status != "implemented"
    )

    audit.sys_label_counts = fetch_sys_label_counts(session)

    if audit.csv_impl_missing_in_graph:
        audit.warnings.append(
            f"{len(audit.csv_impl_missing_in_graph)}+ implemented CSV types absent from SYS_RelationshipType"
        )
    if audit.backlink_not_in_csv:
        audit.warnings.append(
            f"BacklinkRouting edge types not in CSV: {', '.join(audit.backlink_not_in_csv)}"
        )
    if audit.backlink_not_implemented:
        audit.notes.append(
            "BacklinkRouting uses candidate lifecycle types (Hold recommended at review): "
            + ", ".join(audit.backlink_not_implemented)
        )
    return audit


def relationship_registry_prompt_block(
    *,
    facet: str | None = None,
    categories: tuple[str, ...] | None = None,
    limit: int = 35,
    csv_path: str | None = None,
) -> str:
    """Compact markdown block for LLM system prompts."""
    registry = load_relationship_registry(csv_path)
    lines = [
        "### Relationship type registry (mandatory)",
        "Before proposing any predicate, use a type from "
        "`Relationships/relationship_types_registry_master.csv` / `SYS_RelationshipType`.",
        "Prefer `lifecycle_status=implemented`. Do not invent new relationship types.",
        "",
    ]

    filt = registry.values()
    if categories:
        catset = {c.lower() for c in categories}
        filt = [e for e in filt if e.category.lower() in catset]
    elif facet == "biographic":
        catset = {"familial", "position", "participation", "relations", "authorship", "causality"}
        filt = [e for e in registry.values() if e.category.lower() in catset or e.lifecycle_status == "implemented"]

    impl = sorted(
        [e for e in filt if e.lifecycle_status == "implemented"],
        key=lambda e: e.relationship_type,
    )[:limit]

    lines.append("**Implemented types (sample):**")
    for e in impl:
        pid = f" ({e.wikidata_property})" if e.wikidata_property else ""
        lines.append(f"- `{e.relationship_type}`{pid} — {e.description[:90]}")

    lines.extend(
        [
            "",
            "**Agent rules:**",
            "- Query `MATCH (rt:SYS_RelationshipType) WHERE rt.rel_type = $t RETURN rt` to verify before writing.",
            "- Backlink harvest edge types come from `SYS_Policy` BacklinkRouting — must align with CSV.",
            "- Unregistered types → Hold claim; add CSV row with `lifecycle_status=candidate` before promotion.",
        ]
    )
    return "\n".join(lines)


def append_relationship_registry_context(system_prompt: str, **kwargs: Any) -> str:
    block = relationship_registry_prompt_block(**kwargs)
    if block.strip() in system_prompt:
        return system_prompt
    return f"{system_prompt.rstrip()}\n\n{block}"
