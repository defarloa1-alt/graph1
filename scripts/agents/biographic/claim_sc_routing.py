"""Route biographic claims to DI SubjectConcept scope (ADR-021).

Deterministic rules map harvest claims to decomposed biographic SCs under Q17167.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROPOSALS = ROOT / "output" / "di_proposals" / "Q17167_proposals_enriched.json"

# scope_key -> subject_id (biographic di_proposal SCs)
BIO_SCOPE_IDS: dict[str, str] = {
    "senatorial_elite_careers": "sc_q17167_senatorial_elite_careers",
    "populist_political_figures": "sc_q17167_populist_political_figures",
    "military_commanders": "sc_q17167_military_commanders",
    "late_republic_leaders": "sc_q17167_late_republic_leaders",
    "women_and_non_elite": "sc_q17167_women_and_non_elite",
    "onomastics_nomenclature": "sc_q17167_onomastics_nomenclature",
    "ancient_biographical_sources": "sc_q17167_ancient_biographical_sources",
}

MILITARY_EDGE_TYPES = frozenset(
    {
        "PARTICIPATED_IN",
        "RAISED_LEGION",
        "ORGANIZED",
        "COMMISSIONED",
        "HEADED",
    }
)

FAMILIAL_EDGE_TYPES = frozenset(
    {
        "CHILD_OF",
        "PARENT_OF",
        "SPOUSE_OF",
        "SIBLING_OF",
        "HALF_SIBLING_OF",
        "FATHER_OF",
        "MOTHER_OF",
    }
)

OFFICE_EDGE_TYPES = frozenset({"POSITION_HELD", "HAD_ROLE", "CHAIRED"})

# From DI candidate resolution — late Republic power figures
LATE_REPUBLIC_PERSON_QIDS = frozenset(
    {
        "Q1420",  # Caesar
        "Q1444",  # Pompey
        "Q1346",  # Marius
        "Q1493",  # Sulla
        "Q82817",  # Cicero
        "Q51673",  # Crassus
        "Q5165",  # Mark Antony
    }
)

POPULIST_PERSON_QIDS = frozenset(
    {
        "Q183060",  # Tiberius Gracchus
        "Q182804",  # Gaius Gracchus
        "Q314240",  # Clodius Pulcher
    }
)

WOMEN_SCOPE_QIDS = frozenset(
    {
        "Q233401",  # Cornelia (mother of Gracchi)
    }
)

ONOMASTICS_PRED_PIDS = frozenset({"P138", "P1448", "P2561"})


@dataclass(frozen=True)
class RoutingResult:
    scope_key: str
    subject_id: str
    label: str
    score: float
    method: str
    reason: str


def load_biographic_scopes(proposals_path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load biographic di_proposal SC metadata keyed by scope_key."""
    path = proposals_path or DEFAULT_PROPOSALS
    if not path.exists():
        return {
            key: {"subject_id": sid, "label": key.replace("_", " ").title(), "scope_key": key}
            for key, sid in BIO_SCOPE_IDS.items()
        }

    with open(path, encoding="utf-8") as f:
        doc = json.load(f)

    scopes: dict[str, dict[str, Any]] = {}
    for proposal in doc.get("proposals", []):
        if proposal.get("source_facet") != "biographic":
            continue
        scope_key = proposal.get("scope_key") or ""
        if not scope_key:
            continue
        scopes[scope_key] = {
            "scope_key": scope_key,
            "subject_id": proposal.get("subject_id") or BIO_SCOPE_IDS.get(scope_key, ""),
            "label": proposal.get("display_label") or proposal.get("label") or scope_key,
            "description": proposal.get("description") or "",
        }
    for key, sid in BIO_SCOPE_IDS.items():
        scopes.setdefault(
            key,
            {"scope_key": key, "subject_id": sid, "label": key.replace("_", " ").title()},
        )
    return scopes


def _result(
    scopes: dict[str, dict[str, Any]],
    scope_key: str,
    *,
    score: float,
    method: str,
    reason: str,
) -> RoutingResult:
    meta = scopes[scope_key]
    return RoutingResult(
        scope_key=scope_key,
        subject_id=meta["subject_id"],
        label=meta["label"],
        score=score,
        method=method,
        reason=reason,
    )


def route_biographic_claim(
    *,
    person_qid: str | None,
    candidate_qid: str | None,
    relationship_type: str | None,
    pred_pid: str | None,
    candidate_label: str | None = None,
    scopes: dict[str, dict[str, Any]] | None = None,
) -> RoutingResult:
    """Pick the best biographic SubjectConcept scope for a harvest claim."""
    scopes = scopes or load_biographic_scopes()
    rel = (relationship_type or "").upper()
    pid = (pred_pid or "").upper()
    person = (person_qid or "").upper()
    candidate = (candidate_qid or "").upper()
    cand_label = (candidate_label or "").lower()

    if pid in ONOMASTICS_PRED_PIDS or "named after" in cand_label:
        return _result(
            scopes,
            "onomastics_nomenclature",
            score=0.92,
            method="predicate",
            reason=f"Onomastic predicate {pid or 'label'}",
        )

    if person in WOMEN_SCOPE_QIDS or candidate in WOMEN_SCOPE_QIDS:
        return _result(
            scopes,
            "women_and_non_elite",
            score=0.88,
            method="person_set",
            reason="Known women / non-elite figure in DI resolution",
        )

    if rel in MILITARY_EDGE_TYPES:
        if person in LATE_REPUBLIC_PERSON_QIDS:
            return _result(
                scopes,
                "late_republic_leaders",
                score=0.85,
                method="person_set+edge",
                reason=f"Military edge {rel} on late-Republic figure {person}",
            )
        return _result(
            scopes,
            "military_commanders",
            score=0.9,
            method="edge",
            reason=f"Military/agent edge {rel}",
        )

    if person in POPULIST_PERSON_QIDS:
        return _result(
            scopes,
            "populist_political_figures",
            score=0.9,
            method="person_set",
            reason=f"Populist figure {person}",
        )

    if person in LATE_REPUBLIC_PERSON_QIDS and rel in OFFICE_EDGE_TYPES | FAMILIAL_EDGE_TYPES:
        return _result(
            scopes,
            "late_republic_leaders",
            score=0.88,
            method="person_set",
            reason=f"Late-Republic figure {person} with {rel}",
        )

    if rel in OFFICE_EDGE_TYPES:
        return _result(
            scopes,
            "senatorial_elite_careers",
            score=0.82,
            method="edge",
            reason=f"Magistracy / office edge {rel}",
        )

    if rel in FAMILIAL_EDGE_TYPES:
        return _result(
            scopes,
            "senatorial_elite_careers",
            score=0.75,
            method="edge",
            reason=f"Familial edge {rel} (default elite prosopography scope)",
        )

    if rel in {"FOUNDED", "COMMISSIONED"}:
        return _result(
            scopes,
            "senatorial_elite_careers",
            score=0.7,
            method="edge",
            reason=f"Institutional edge {rel}",
        )

    return _result(
        scopes,
        "senatorial_elite_careers",
        score=0.55,
        method="fallback",
        reason=f"No specific rule matched for {rel or 'unknown'} — default elite careers scope",
    )
