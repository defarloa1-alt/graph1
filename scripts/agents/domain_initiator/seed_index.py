"""Load Seed Knowledge Index artifacts for DI validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_DERIVED_DIR = Path("JSON/wikidata/derived")


def seed_index_path(qid: str, derived_dir: Path | None = None) -> Path:
    return (derived_dir or DEFAULT_DERIVED_DIR) / f"{qid.upper()}_seed_index.json"


def load_seed_index(qid: str, derived_dir: Path | None = None) -> dict[str, Any] | None:
    path = seed_index_path(qid, derived_dir)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def allowed_qid_set(index: dict[str, Any] | None) -> frozenset[str]:
    if not index:
        return frozenset()
    allowed = index.get("allowed_candidate_qids") or {}
    union = allowed.get("union") or []
    seed = (allowed.get("seed_qid") or index.get("seed", {}).get("qid") or "").upper()
    qids = {q.upper() for q in union if q}
    if seed:
        qids.add(seed)
    return frozenset(qids)


def is_seed_connected(qid: str, index: dict[str, Any] | None) -> bool:
    if not index:
        return False
    return qid.upper() in allowed_qid_set(index)


def label_from_index(index: dict[str, Any] | None, qid: str) -> str | None:
    if not index:
        return None
    labels = index.get("labels") or {}
    return labels.get(qid.upper())
