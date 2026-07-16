#!/usr/bin/env python3
"""Resolve Wikidata QID labels — never emit bare QIDs as display labels."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

import requests

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1LabelResolver/1.0 (local tooling)"
QID_RE = re.compile(r"^Q\d+$", re.IGNORECASE)

DEFAULT_LABEL_CACHE = Path("JSON/wikidata/derived/label_cache.json")


def is_bare_qid_label(label: Optional[str], qid: str) -> bool:
    """True when label is missing or is just the QID (unintelligible for humans)."""
    if not label or not str(label).strip():
        return True
    clean = str(label).strip()
    q = (qid or "").strip().upper()
    if clean.upper() == q:
        return True
    if QID_RE.fullmatch(clean):
        return True
    return False


def load_label_cache(path: Path = DEFAULT_LABEL_CACHE) -> Dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "labels" in data:
        return {k.upper(): v for k, v in (data.get("labels") or {}).items() if v}
    if isinstance(data, dict):
        return {k.upper(): v for k, v in data.items() if isinstance(v, str) and v}
    return {}


def save_label_cache(cache: Dict[str, str], path: Path = DEFAULT_LABEL_CACHE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "label_count": len(cache),
        "labels": dict(sorted(cache.items())),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def labels_from_seed_index(seed_index: Optional[Dict[str, Any]]) -> Dict[str, str]:
    if not seed_index:
        return {}
    raw = seed_index.get("labels") or {}
    out: Dict[str, str] = {}
    for qid, label in raw.items():
        q = (qid or "").upper()
        if QID_RE.fullmatch(q) and isinstance(label, str) and not is_bare_qid_label(label, q):
            out[q] = label.strip()
    return out


def labels_from_statement_payloads(directory: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not directory.exists():
        return out
    for path in directory.glob("Q*_statements_full.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        qid = (payload.get("qid") or "").upper()
        label = payload.get("label")
        if QID_RE.fullmatch(qid) and isinstance(label, str) and not is_bare_qid_label(label, qid):
            out[qid] = label.strip()
    return out


def _chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _pick_label(entity: Dict[str, Any]) -> str:
    labels = entity.get("labels") or {}
    for lang in ("en", "la", "it", "fr", "de", "es"):
        row = labels.get(lang)
        if isinstance(row, dict) and row.get("value"):
            return str(row["value"]).strip()
    for row in labels.values():
        if isinstance(row, dict) and row.get("value"):
            return str(row["value"]).strip()
    descriptions = entity.get("descriptions") or {}
    for lang in ("en", "la", "it", "fr", "de", "es"):
        row = descriptions.get(lang)
        if isinstance(row, dict) and row.get("value"):
            return str(row["value"]).strip()[:120]
    for row in descriptions.values():
        if isinstance(row, dict) and row.get("value"):
            return str(row["value"]).strip()[:120]
    return ""


def fetch_labels_batch(
    qids: List[str],
    *,
    batch_size: int = 20,
    pause_s: float = 1.0,
    max_retries: int = 5,
) -> Dict[str, str]:
    headers = {"User-Agent": USER_AGENT}
    out: Dict[str, str] = {}
    unique = sorted({q.upper() for q in qids if QID_RE.fullmatch((q or "").upper())})
    for batch in _chunks(unique, max(1, batch_size)):
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": "|".join(batch),
            "languages": "en|la|it|fr|de|es",
            "props": "labels|descriptions",
        }
        for attempt in range(max_retries):
            resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=60)
            if resp.status_code == 429:
                time.sleep(3.0 * (attempt + 1))
                continue
            resp.raise_for_status()
            payload = resp.json()
            for qid, entity in (payload.get("entities") or {}).items():
                if not QID_RE.fullmatch(qid):
                    continue
                label = _pick_label(entity or {})
                if not is_bare_qid_label(label, qid):
                    out[qid] = label
            break
        time.sleep(pause_s)
    return out


def resolve_labels(
    qids: Iterable[str],
    *,
    seed_index: Optional[Dict[str, Any]] = None,
    statement_dirs: Optional[List[Path]] = None,
    cache_path: Path = DEFAULT_LABEL_CACHE,
    fetch_missing: bool = True,
) -> Dict[str, str]:
    """Merge cached, index, and statement labels; fetch any still missing."""
    cache = load_label_cache(cache_path)
    resolved: Dict[str, str] = dict(cache)

    for src in (labels_from_seed_index(seed_index),):
        resolved.update(src)

    for directory in statement_dirs or []:
        resolved.update(labels_from_statement_payloads(directory))

    needed = sorted({q.upper() for q in qids if QID_RE.fullmatch((q or "").upper())})
    missing = [q for q in needed if is_bare_qid_label(resolved.get(q), q)]

    if fetch_missing and missing:
        fetched = fetch_labels_batch(missing)
        resolved.update(fetched)
        cache.update({k: v for k, v in resolved.items() if not is_bare_qid_label(v, k)})
        save_label_cache(cache, cache_path)

    return resolved


def apply_labels_to_proposal(
    proposal: Dict[str, Any],
    labels: Dict[str, str],
) -> Dict[str, int]:
    """Patch nodes, claims, and timeline with resolved labels. Returns stats."""
    stats = {"patched": 0, "still_bare": 0}

    def _label_for(qid: str, current: str = "") -> str:
        q = (qid or "").upper()
        candidate = labels.get(q) or current or ""
        if not is_bare_qid_label(candidate, q):
            return candidate.strip()
        stats["still_bare"] += 1
        return candidate

    seed_qid = (proposal.get("seed") or {}).get("qid", "")
    seed_label = (proposal.get("seed") or {}).get("label", "")

    for node in proposal.get("nodes") or []:
        qid = node.get("qid", "")
        new_label = _label_for(qid, node.get("label", ""))
        if new_label != node.get("label"):
            node["label"] = new_label
            stats["patched"] += 1

    for key in ("relationship_claim_proposals", "attribute_claim_proposals"):
        for row in proposal.get(key) or []:
            for side in ("subject", "object"):
                qid_key = f"{side}_qid"
                label_key = f"{side}_label"
                qid = row.get(qid_key)
                if not qid:
                    continue
                new_label = _label_for(qid, row.get(label_key, ""))
                if new_label != row.get(label_key):
                    row[label_key] = new_label
                    stats["patched"] += 1

    for row in proposal.get("timeline_entries") or []:
        for qid_key, label_key in (
            ("subject_qid", "subject_label"),
            ("related_object_qid", "related_object_label"),
        ):
            qid = row.get(qid_key)
            if not qid:
                continue
            new_label = _label_for(qid, row.get(label_key, ""))
            if new_label != row.get(label_key):
                row[label_key] = new_label
                stats["patched"] += 1

    if seed_qid and not is_bare_qid_label(seed_label, seed_qid):
        labels.setdefault(seed_qid.upper(), seed_label)

    return stats
