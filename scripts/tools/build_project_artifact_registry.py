"""Build an agent-facing project artifact registry.

Outputs:
- CSV/registry/project_artifact_registry.csv
- JSON/registry/project_artifact_registry.json
- md/Core/AGENT_ARTIFACT_ROUTING_GUIDE.md
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
TODAY = date.today().isoformat()

SCAN_ROOTS = [
    "scripts",
    "Neo4j/schema",
    "sysml",
    "CSV",
    "md/Architecture",
    "md/Agents",
    "md/Core",
    "JSON/policy",
    "JSON/kbpedia",
    "Relationships",
    "Facets",
    "Key Files",
]

INCLUDE_SUFFIXES = {
    ".py",
    ".ps1",
    ".sh",
    ".bat",
    ".cypher",
    ".json",
    ".md",
    ".csv",
    ".mmd",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
}

EXCLUDE_PREFIXES = (
    "Archive/",
    "Old-federated-project/",
    ".git/",
    "subjectsAgentsProposal/",
)

EXCLUDE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDE_SUFFIXES = {".gif", ".zip", ".gz", ".pdf", ".mp4"}

KNOWN_WRAPPERS = {
    "Python/migrate_temporal_hierarchy_levels.py",
    "subjectsAgentsProposal/files3/ingest_claims.py",
    "subjectsAgentsProposal/files3/validate_claims.py",
}


def to_posix(path: Path) -> str:
    return path.as_posix()


def should_skip(rel_path: str, path: Path) -> bool:
    if any(rel_path.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return True
    if any(part in EXCLUDE_DIR_NAMES for part in path.parts):
        return True
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    if path.name.startswith("."):
        return True
    if rel_path.startswith("CSV/"):
        low = rel_path.lower()
        if "/experiments/" in low:
            return True
        name = path.name.lower()
        csv_tokens = ("crosswalk", "canonical", "registry", "mapping", "master", "seed")
        if path.suffix.lower() == ".csv" and not any(token in name for token in csv_tokens):
            return True
    return False


def classify_artifact_type(rel_path: str, path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name.lower()

    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
        if rel_path.startswith("sysml/"):
            if "sequence" in name:
                return "sysml_sequence"
            return "sysml_bdd"
        return "diagram"

    if rel_path.startswith("Neo4j/schema/"):
        if name.startswith("run_") and suffix in {".py", ".ps1"}:
            return "pipeline_runner"
        if suffix == ".cypher":
            return "schema_cypher"
        if suffix == ".py":
            return "script"
        if suffix == ".md":
            return "architecture_doc"
        if suffix in {".csv", ".json"}:
            return "registry"
    if rel_path.startswith("sysml/"):
        if suffix == ".json":
            return "sysml_contract"
        if "sequence" in name or suffix == ".mmd":
            return "sysml_sequence"
        return "sysml_bdd"
    if rel_path.startswith("JSON/policy/"):
        return "policy"
    if rel_path.startswith("md/Architecture/"):
        if path.name.startswith("ADR-"):
            return "adr"
        return "architecture_doc"
    if rel_path.startswith("md/Agents/"):
        return "prompt_or_agent_spec"
    if rel_path.startswith("scripts/"):
        return "script"
    if rel_path.startswith("CSV/"):
        return "registry"
    if rel_path.startswith("JSON/kbpedia/"):
        return "registry"
    if rel_path.startswith("Relationships/") or rel_path.startswith("Facets/"):
        if suffix == ".py":
            return "script"
        if suffix in {".csv", ".json"}:
            return "registry"
        return "architecture_doc"
    if rel_path.startswith("md/Core/"):
        return "architecture_doc"
    if rel_path.startswith("Key Files/"):
        return "architecture_doc"
    if suffix == ".cypher":
        return "schema_cypher"
    return "artifact"


def classify_status(rel_path: str, path: Path) -> str:
    low = rel_path.lower()
    if low.startswith("archive/") or low.startswith("old-federated-project/"):
        return "archived"
    if any(token in low for token in ("draft", "todo", "proposal", "backlog")):
        return "draft"
    if ".backup" in low or ".recovered" in low:
        return "deprecated"
    return "active"


def classify_canonicality(rel_path: str, artifact_type: str) -> str:
    if rel_path in KNOWN_WRAPPERS:
        return "compatible_wrapper"
    if rel_path.startswith("Archive/") or rel_path.startswith("Old-federated-project/"):
        return "legacy_reference"
    if rel_path == "Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md":
        return "canonical"
    if rel_path == "md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md":
        return "canonical"
    if artifact_type in {"pipeline_runner", "schema_cypher", "policy"}:
        return "canonical"
    if rel_path.startswith(("scripts/", "sysml/", "md/Architecture/ADR-", "md/Agents/", "md/Core/")):
        return "canonical"
    if rel_path.startswith(("Relationships/", "Facets/", "CSV/", "JSON/kbpedia/")):
        return "canonical"
    return "legacy_reference"


def classify_owner_role(rel_path: str, artifact_type: str) -> str:
    if artifact_type in {"pipeline_runner", "schema_cypher", "policy"}:
        return "Pi"
    if rel_path.startswith("scripts/agents/") or rel_path.startswith("md/Agents/"):
        return "SCA"
    if rel_path.startswith("scripts/backbone/") or rel_path.startswith("scripts/tools/"):
        return "SFA"
    return "Platform"


def used_by_roles(owner_role: str, artifact_type: str) -> str:
    if owner_role == "Pi":
        return "Pi;SCA;SFA"
    if owner_role == "SCA":
        return "SCA;Pi"
    if owner_role == "SFA":
        return "SFA;Pi"
    if artifact_type.startswith("sysml_"):
        return "SCA;SFA;Pi;Platform"
    return "SCA;SFA;Pi"


def derive_task_tags(rel_path: str) -> str:
    low = rel_path.lower()
    tags: List[str] = []
    rules = [
        ("federat", "federation"),
        ("wikidata", "federation"),
        ("claim", "claims"),
        ("policy", "policy"),
        ("temporal", "temporal"),
        ("period", "temporal"),
        ("year", "temporal"),
        ("geo", "geographic"),
        ("place", "geographic"),
        ("pleiades", "geographic"),
        ("geonames", "geographic"),
        ("tgn", "geographic"),
        ("schema", "schema"),
        ("constraint", "schema"),
        ("index", "schema"),
        ("agent", "agent_routing"),
        ("facet", "agent_routing"),
        ("relationship", "relationships"),
        ("kbpedia", "kbpedia"),
        ("kko", "kbpedia"),
        ("sysml", "sysml"),
    ]
    for needle, tag in rules:
        if needle in low and tag not in tags:
            tags.append(tag)
    if not tags:
        tags.append("general")
    return ";".join(tags)


def infer_mutation_scope(rel_path: str, artifact_type: str) -> str:
    low = rel_path.lower()
    if artifact_type in {
        "architecture_doc",
        "adr",
        "registry",
        "diagram",
        "policy",
        "sysml_bdd",
        "sysml_sequence",
        "sysml_contract",
        "prompt_or_agent_spec",
    }:
        return "read_only"
    if any(token in low for token in ("proposal", "backlog", "todo")):
        return "proposal_only"
    write_tokens = (
        "ingest",
        "import",
        "load",
        "migrate",
        "seed",
        "pipeline",
        "create_",
        "update",
        "link_",
        "sync_",
        "run_",
    )
    if artifact_type in {"pipeline_runner", "schema_cypher"} or any(token in low for token in write_tokens):
        return "canonical_write"
    return "read_only"


def infer_gates(mutation_scope: str) -> str:
    if mutation_scope == "read_only":
        return "none"
    if mutation_scope == "proposal_only":
        return "U->Pi->Commit (proposal gate)"
    return "dispatcher_gate|policy_gate|U->Pi->Commit"


def infer_when_to_use(artifact_type: str, rel_path: str) -> str:
    if artifact_type == "pipeline_runner":
        return "Use when executing end-to-end seeded pipeline runs."
    if artifact_type == "schema_cypher":
        return "Use for schema bootstrap, migration, or deterministic graph checks."
    if artifact_type == "policy":
        return "Use for deterministic ordered decision-table evaluation."
    if artifact_type.startswith("sysml_"):
        return "Use when validating orchestration contracts and flow semantics."
    if artifact_type == "adr":
        return "Use when a boundary or invariant decision is needed."
    if rel_path.startswith("scripts/tools/"):
        return "Use for focused tooling in extraction, federation, or proposal generation."
    if rel_path.startswith("scripts/backbone/"):
        return "Use for backbone ingestion/enrichment workflows."
    if rel_path.startswith("scripts/agents/"):
        return "Use for runtime agent orchestration and execution tests."
    if rel_path.startswith("md/"):
        return "Use for architecture and operational guidance."
    return "Use as supporting project artifact."


def infer_inputs_outputs(artifact_type: str, rel_path: str) -> Tuple[str, str]:
    if artifact_type == "pipeline_runner":
        return ("CLI args + env + JSON/CSV inputs", "Neo4j writes + JSON/MD run artifacts")
    if artifact_type == "schema_cypher":
        return ("Neo4j graph state", "Schema objects and deterministic query results")
    if artifact_type == "policy":
        return ("Policy JSON payload", "Rule outcomes and gate flags")
    if artifact_type == "registry":
        return ("Curated tabular/json rows", "Lookup keys for routing/alignment")
    if artifact_type.startswith("sysml_"):
        return ("Contract/flow definitions", "Machine-checkable interface expectations")
    if rel_path.endswith(".py"):
        return ("CLI args + files + env", "Generated artifacts and/or graph mutations")
    if rel_path.endswith(".md"):
        return ("N/A", "Human-readable guidance")
    if rel_path.endswith(".json"):
        return ("N/A", "Structured artifact payload")
    if rel_path.endswith(".csv"):
        return ("N/A", "Tabular registry/crosswalk data")
    return ("N/A", "N/A")


def infer_example_invocation(rel_path: str, path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return f"python {rel_path}"
    if suffix == ".ps1":
        return f"powershell -File {rel_path}"
    if suffix == ".sh":
        return f"bash {rel_path}"
    if suffix == ".bat":
        return rel_path
    if suffix == ".cypher":
        return f"cypher-shell -u neo4j -p <password> < {rel_path}"
    return f"open {rel_path}"


def infer_validation_command(rel_path: str, path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return f"python {rel_path} --help"
    if suffix == ".ps1":
        return f"powershell -File {rel_path} -?"
    if suffix == ".cypher":
        return f"cypher-shell -u neo4j -p <password> < {rel_path}"
    if suffix == ".json":
        return f"python -m json.tool {rel_path}"
    if suffix == ".csv":
        return "manual_review"
    return "manual_review"


def infer_source_of_truth(rel_path: str) -> str:
    low = rel_path.lower()
    if "kbpedia" in low or "kko" in low:
        return "md/Architecture/ADR-003-KBpedia-Role-and-Boundaries.md"
    if "claim_confidence" in low or "policy" in low:
        return "md/Architecture/ADR-006-Claim-Confidence-Decision-Model.md"
    if rel_path.startswith("sysml/"):
        return "md/Architecture/2-17-26-CHRYSTALLUM_v0_AGENT_BOOTSTRAP_SPEC.md"
    if rel_path.startswith(("Neo4j/schema/", "scripts/", "Relationships/", "Facets/")):
        return "md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md"
    return "Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md"


def artifact_id_from_path(rel_path: str) -> str:
    base = rel_path.replace("\\", "/").lower()
    for ch in ["/", ".", " ", ":", "(", ")", "[", "]", ","]:
        base = base.replace(ch, "_")
    while "__" in base:
        base = base.replace("__", "_")
    return base.strip("_")


def collect_files() -> Iterable[Tuple[str, Path]]:
    for root_name in SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            rel_path = to_posix(path.relative_to(REPO_ROOT))
            if should_skip(rel_path, path):
                continue
            if path.suffix.lower() not in INCLUDE_SUFFIXES:
                continue
            yield rel_path, path


def build_records() -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    for rel_path, path in collect_files():
        artifact_type = classify_artifact_type(rel_path, path)
        status = classify_status(rel_path, path)
        canonicality = classify_canonicality(rel_path, artifact_type)
        owner_role = classify_owner_role(rel_path, artifact_type)
        scope = infer_mutation_scope(rel_path, artifact_type)
        inputs, outputs = infer_inputs_outputs(artifact_type, rel_path)
        record = {
            "artifact_id": artifact_id_from_path(rel_path),
            "artifact_type": artifact_type,
            "path": rel_path,
            "status": status,
            "canonicality": canonicality,
            "owner_role": owner_role,
            "used_by_agent_roles": used_by_roles(owner_role, artifact_type),
            "task_tags": derive_task_tags(rel_path),
            "when_to_use": infer_when_to_use(artifact_type, rel_path),
            "inputs": inputs,
            "outputs": outputs,
            "mutation_scope": scope,
            "gates": infer_gates(scope),
            "dependencies": "md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md",
            "example_invocation_or_query": infer_example_invocation(rel_path, path),
            "validation_command": infer_validation_command(rel_path, path),
            "source_of_truth_ref": infer_source_of_truth(rel_path),
            "last_validated_at": TODAY,
        }
        records.append(record)
    return sorted(records, key=lambda row: row["path"])


def write_csv(records: List[Dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(records[0].keys()) if records else []
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)


def write_json(records: List[Dict[str, str]], out_path: Path) -> Dict[str, object]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    by_type = Counter(r["artifact_type"] for r in records)
    by_role = Counter(r["owner_role"] for r in records)
    payload: Dict[str, object] = {
        "registry_id": "chrystallum_project_artifact_registry",
        "version": f"{TODAY}-v1",
        "status": "draft_non_normative",
        "generated_at": TODAY,
        "totals": {
            "artifacts": len(records),
            "by_type": dict(sorted(by_type.items())),
            "by_owner_role": dict(sorted(by_role.items())),
        },
        "artifacts": records,
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def build_routing_sections(records: List[Dict[str, str]]) -> Tuple[Dict[str, List[Dict[str, str]]], Dict[str, List[Dict[str, str]]]]:
    task_index: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    role_index: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in records:
        tags = [tag for tag in row["task_tags"].split(";") if tag]
        for tag in tags:
            task_index[tag].append(row)
        role_index[row["owner_role"]].append(row)
    return task_index, role_index


def pick_key_rows(rows: List[Dict[str, str]], limit: int = 8) -> List[Dict[str, str]]:
    ranked = sorted(
        rows,
        key=lambda r: (
            0 if r["artifact_type"] in {"pipeline_runner", "policy", "schema_cypher"} else 1,
            0 if r["canonicality"] == "canonical" else 1,
            r["path"],
        ),
    )
    return ranked[:limit]


def write_guide(records: List[Dict[str, str]], out_path: Path) -> None:
    task_index, role_index = build_routing_sections(records)
    lines: List[str] = []
    lines.append("# Agent Artifact Routing Guide")
    lines.append("")
    lines.append("Status: generated first-pass routing index from active canonical folders.")
    lines.append("")
    lines.append(f"- Generated: `{TODAY}`")
    lines.append(f"- Total artifacts indexed: `{len(records)}`")
    lines.append("- Source registry: `CSV/registry/project_artifact_registry.csv`")
    lines.append("- Review queue: `CSV/registry/project_artifact_registry_review_queue.csv`")
    lines.append("- Rebuild command: `python scripts/tools/build_project_artifact_registry.py`")
    lines.append("")
    lines.append("## Priority Entry Points")
    lines.append("")
    key_entries = [
        "Neo4j/schema/run_qid_pipeline.py",
        "scripts/tools/wikidata_backlink_harvest.py",
        "scripts/tools/claim_confidence_policy_engine.py",
        "scripts/tools/policy_subgraph_loader.py",
        "scripts/tools/kko_mapping_proposal_loader.py",
        "md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md",
        "Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md",
    ]
    for path in key_entries:
        lines.append(f"- `{path}`")
    lines.append("")
    lines.append("## Routing by Task Tag")
    lines.append("")
    for tag in sorted(task_index.keys()):
        lines.append(f"### `{tag}`")
        for row in pick_key_rows(task_index[tag], limit=6):
            lines.append(
                f"- `{row['path']}` | type=`{row['artifact_type']}` | scope=`{row['mutation_scope']}` | gates=`{row['gates']}`"
            )
        lines.append("")
    lines.append("## Routing by Owner Role")
    lines.append("")
    for role in sorted(role_index.keys()):
        lines.append(f"### `{role}`")
        for row in pick_key_rows(role_index[role], limit=6):
            lines.append(
                f"- `{row['path']}` | type=`{row['artifact_type']}` | tags=`{row['task_tags']}`"
            )
        lines.append("")
    lines.append("## Guardrails")
    lines.append("")
    lines.append("- Canonical write paths must follow `U -> Pi -> Commit`.")
    lines.append("- Proposal-only artifacts do not mutate canonical graph directly.")
    lines.append("- Use `md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md` for executable crosswalk anchors.")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def review_reasons(row: Dict[str, str]) -> List[str]:
    reasons: List[str] = []
    low = row["path"].lower()
    if row["status"] == "draft" and row["canonicality"] == "canonical":
        reasons.append("draft_in_canonical_path")
    if row["artifact_type"] in {"script", "pipeline_runner", "schema_cypher"} and row["owner_role"] == "Platform":
        reasons.append("executable_owned_by_platform")
    if row["artifact_type"] == "script" and row["mutation_scope"] == "read_only":
        write_tokens = ("ingest", "import", "load", "migrate", "seed", "create_", "update", "link_", "sync_")
        if any(token in low for token in write_tokens):
            reasons.append("scope_may_be_underclassified")
    if row["path"].startswith("Facets/Scripts/"):
        reasons.append("legacy_script_path_needs_canonical_confirmation")
    return reasons


def write_review_queue(records: List[Dict[str, str]], out_path: Path) -> int:
    queue_rows: List[Dict[str, str]] = []
    for row in records:
        reasons = review_reasons(row)
        if not reasons:
            continue
        queue_rows.append(
            {
                "path": row["path"],
                "artifact_type": row["artifact_type"],
                "owner_role": row["owner_role"],
                "mutation_scope": row["mutation_scope"],
                "status": row["status"],
                "reasons": ";".join(reasons),
                "recommended_action": "review_and_override_if_needed",
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "path",
                "artifact_type",
                "owner_role",
                "mutation_scope",
                "status",
                "reasons",
                "recommended_action",
            ],
        )
        writer.writeheader()
        writer.writerows(sorted(queue_rows, key=lambda r: r["path"]))
    return len(queue_rows)


def main() -> None:
    records = build_records()
    if not records:
        raise RuntimeError("No artifacts were indexed. Check scan roots and filters.")
    csv_path = REPO_ROOT / "CSV/registry/project_artifact_registry.csv"
    json_path = REPO_ROOT / "JSON/registry/project_artifact_registry.json"
    guide_path = REPO_ROOT / "md/Core/AGENT_ARTIFACT_ROUTING_GUIDE.md"
    review_path = REPO_ROOT / "CSV/registry/project_artifact_registry_review_queue.csv"
    write_csv(records, csv_path)
    payload = write_json(records, json_path)
    write_guide(records, guide_path)
    review_count = write_review_queue(records, review_path)
    print(f"indexed={len(records)}")
    print(f"csv={csv_path.as_posix()}")
    print(f"json={json_path.as_posix()}")
    print(f"guide={guide_path.as_posix()}")
    print(f"review_queue={review_path.as_posix()}")
    print(f"review_items={review_count}")
    print(f"by_type={payload['totals']['by_type']}")


if __name__ == "__main__":
    main()
