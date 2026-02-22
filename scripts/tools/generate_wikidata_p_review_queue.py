#!/usr/bin/env python3
"""Generate a review queue of Wikidata P-value suggestions for unmapped relationships.

Input:
  Relationships/relationship_types_registry_master.csv
  Relationships/relationship_types_seed.cypher

Output:
  Relationships/wikidata_p_mapping_review_queue_YYYY-MM-DD.csv
"""

from __future__ import annotations

import csv
import datetime as dt
import re
from pathlib import Path


SEED_PATTERN = re.compile(
    r'^\s*\{key:"(?P<key>[A-Z0-9_]+)".*?'
    r'wikidata_pid:(?P<pid>null|"[^"]*").*?'
    r'wikidata_label:(?P<label>null|"[^"]*").*?'
    r'inverse_of:(?P<inverse>null|"[^"]*")',
    flags=re.ASCII,
)


def _strip_token(token: str) -> str:
    token = token.strip()
    if token == "null":
        return ""
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    return token


def load_seed(seed_path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for line in seed_path.read_text(encoding="utf-8").splitlines():
        m = SEED_PATTERN.match(line)
        if not m:
            continue
        key = m.group("key")
        out[key] = {
            "pid": _strip_token(m.group("pid")),
            "label": _strip_token(m.group("label")),
            "inverse": _strip_token(m.group("inverse")),
        }
    return out


def mapped_pid(master_rows: list[dict[str, str]]) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for r in master_rows:
        rel = (r.get("relationship_type") or "").strip()
        pid = (r.get("wikidata_property") or "").strip()
        label = (r.get("wikidata_label") or "").strip()
        if rel and pid:
            out[rel] = (pid, label)
    return out


def counterpart_keys(rel: str) -> list[str]:
    cands: list[str] = []
    if rel.endswith("_BY"):
        cands.append(rel[:-3])
    if rel.endswith("_TO"):
        cands.append(rel[:-3])
    if rel.endswith("_FROM"):
        cands.append(rel[:-5])
    if rel.startswith("HAS_"):
        cands.append(rel[4:] + "_OF")
        cands.append(rel[4:])
    if rel.endswith("_OF"):
        cands.append("HAS_" + rel[:-3])
    # common explicit pair
    if rel == "OFFICE_HELD_BY":
        cands.append("POSITION_HELD")
        cands.append("APPOINTED_TO")
    return cands


def build_queue(
    master_rows: list[dict[str, str]],
    seed: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    mapped = mapped_pid(master_rows)
    queue: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    manual_pairs = {
        "HAS_MEMBER": ("P463", "member of", "high", "manual_pair"),
        "OFFICE_HELD_BY": ("P39", "position held", "high", "manual_pair"),
        "RENAMED_TO": ("P1448", "official name", "medium", "manual_pair"),
    }

    for r in master_rows:
        rel = (r.get("relationship_type") or "").strip()
        if not rel:
            continue
        if (r.get("wikidata_property") or "").strip():
            continue

        category = (r.get("category") or "").strip()
        desc = (r.get("description") or "").strip()

        suggestions: list[tuple[str, str, str, str, str]] = []

        # 1) direct seed mapping (highest confidence)
        sd = seed.get(rel)
        if sd and sd["pid"]:
            suggestions.append(
                (
                    sd["pid"],
                    sd["label"] or "",
                    "high",
                    "seed_direct",
                    f"Seed provides explicit mapping for {rel}",
                )
            )

        # 2) inverse from seed (high/medium)
        if sd and sd["inverse"]:
            inv = sd["inverse"]
            if inv in mapped:
                pid, label = mapped[inv]
                suggestions.append(
                    (
                        pid,
                        label,
                        "medium",
                        "seed_inverse_master",
                        f"Seed inverse_of={inv} and {inv} already mapped",
                    )
                )
            elif inv in seed and seed[inv]["pid"]:
                suggestions.append(
                    (
                        seed[inv]["pid"],
                        seed[inv]["label"] or "",
                        "medium",
                        "seed_inverse_seed",
                        f"Seed inverse_of={inv} has mapped pid in seed",
                    )
                )

        # 3) manual safe pair map
        if rel in manual_pairs:
            pid, label, conf, method = manual_pairs[rel]
            suggestions.append(
                (pid, label, conf, method, f"Manual canonical pair rule for {rel}")
            )

        # 4) lightweight counterpart heuristic
        for ck in counterpart_keys(rel):
            if ck in mapped:
                pid, label = mapped[ck]
                suggestions.append(
                    (
                        pid,
                        label,
                        "low",
                        "name_counterpart",
                        f"Counterpart {ck} already mapped",
                    )
                )

        # de-duplicate by pid
        dedup: dict[str, tuple[str, str, str, str]] = {}
        for pid, label, conf, method, rationale in suggestions:
            if not pid:
                continue
            rank = {"high": 3, "medium": 2, "low": 1}.get(conf, 0)
            prev = dedup.get(pid)
            if prev is None:
                dedup[pid] = (label, conf, method, rationale)
            else:
                prev_rank = {"high": 3, "medium": 2, "low": 1}.get(prev[1], 0)
                if rank > prev_rank:
                    dedup[pid] = (label, conf, method, rationale)

        for pid, (label, conf, method, rationale) in dedup.items():
            key = (rel, pid)
            if key in seen:
                continue
            seen.add(key)
            queue.append(
                {
                    "relationship_type": rel,
                    "category": category,
                    "description": desc,
                    "current_wikidata_property": "",
                    "suggested_wikidata_property": pid,
                    "suggested_wikidata_label": label,
                    "confidence": conf,
                    "method": method,
                    "rationale": rationale,
                    "review_status": "pending_review",
                }
            )

    # sort: high first, then medium, then low, then key
    conf_rank = {"high": 0, "medium": 1, "low": 2}
    queue.sort(
        key=lambda x: (
            conf_rank.get(x["confidence"], 3),
            x["relationship_type"],
            x["suggested_wikidata_property"],
        )
    )
    return queue


def main() -> None:
    root = Path(r"c:\Projects\Graph1")
    master = root / "Relationships" / "relationship_types_registry_master.csv"
    seed = root / "Relationships" / "relationship_types_seed.cypher"
    out = (
        root
        / "Relationships"
        / f"wikidata_p_mapping_review_queue_{dt.date.today().isoformat()}.csv"
    )

    rows = list(csv.DictReader(master.open(encoding="utf-8", newline="")))
    seed_map = load_seed(seed)
    queue = build_queue(rows, seed_map)

    with out.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "relationship_type",
            "category",
            "description",
            "current_wikidata_property",
            "suggested_wikidata_property",
            "suggested_wikidata_label",
            "confidence",
            "method",
            "rationale",
            "review_status",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(queue)

    print(f"master_rows={len(rows)}")
    print(f"seed_keys={len(seed_map)}")
    print(f"queue_rows={len(queue)}")
    high = sum(1 for r in queue if r["confidence"] == "high")
    med = sum(1 for r in queue if r["confidence"] == "medium")
    low = sum(1 for r in queue if r["confidence"] == "low")
    print(f"high={high}")
    print(f"medium={med}")
    print(f"low={low}")
    print(f"output={out}")


if __name__ == "__main__":
    main()
