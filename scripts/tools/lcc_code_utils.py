from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Optional, Tuple


_LCC_PATTERNS = (
    r"^[A-Z]{1,3}$",
    r"^[A-Z]{1,3}\d+$",
    r"^[A-Z]{1,3}\d+-\d+$",
    r"^[A-Z]{1,3}\d+\.\d+$",
    r"^[A-Z]{1,3}\d+\.\d+\.[A-Z]\d*$",
)


def is_valid_lcc_class_code(class_code: str) -> bool:
    if not class_code or not isinstance(class_code, str):
        return False
    value = class_code.strip().upper()
    return any(re.match(pattern, value) for pattern in _LCC_PATTERNS)


def extract_numeric_range(class_code: str) -> Tuple[Optional[float], Optional[float]]:
    value = (class_code or "").strip().upper()
    if not value:
        return None, None

    try:
        # A100-200
        if "-" in value:
            left, right = value.split("-", 1)
            left_match = re.search(r"(\d+(?:\.\d+)?)$", left)
            right_match = re.search(r"^(\d+(?:\.\d+)?)", right)
            if left_match and right_match:
                return float(left_match.group(1)), float(right_match.group(1))

        # A123.45
        decimal_match = re.search(r"(\d+\.\d+)", value)
        if decimal_match:
            number = float(decimal_match.group(1))
            return number, number

        # A123
        integer_match = re.search(r"(\d+)", value)
        if integer_match:
            number = float(integer_match.group(1))
            return number, number
    except ValueError:
        return None, None

    return None, None


def infer_parent_code(class_code: str) -> Optional[str]:
    value = (class_code or "").strip().upper()
    if not value:
        return None

    # QA76.9.A25 -> QA76.9
    if "." in value:
        parts = value.split(".")
        if len(parts) > 1:
            return ".".join(parts[:-1])

    # A100-200 -> A
    if "-" in value:
        match = re.match(r"^([A-Z]+)", value)
        return match.group(1) if match else None

    # A123 -> A
    match = re.match(r"^([A-Z]+)", value)
    if match and len(value) > len(match.group(1)):
        return match.group(1)

    return None


def infer_hierarchy_level(class_code: str, parent_code: Optional[str] = None) -> int:
    value = (class_code or "").strip().upper()
    parent = (parent_code or "").strip().upper()
    if not value or not parent:
        return 0

    if "." in value:
        return value.count(".") + 1
    if "-" in value:
        return 1
    if len(value) <= 2:
        return 0
    if len(value) <= 5:
        return 1
    return 2


# Sub-range labels not present as exact rows in dg_schedule / lcc_roman_republic
LCC_LABEL_SUPPLEMENT: dict[str, str] = {
    "DG241-253": "Republic wars and conquest (Middle Republic campaigns)",
    "DG241-269": "Republic, 509-27 B.C.",
    "DG242-249.4": "Punic Wars period",
    "DG253.5-269": "Fall of the Republic / civil wars",
}


def load_lcc_label_index(root: Path | None = None) -> dict[str, str]:
    """Load code -> human label from Roman Republic LCC schedules."""
    root = root or Path(__file__).resolve().parents[2]
    index: dict[str, str] = dict(LCC_LABEL_SUPPLEMENT)
    sources = [
        root / "CSV" / "lcc_roman_republic.csv",
        root / "Subjects" / "LCC" / "dg_schedule.csv",
    ]
    for path in sources:
        if not path.exists():
            continue
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = (row.get("code") or row.get("id") or "").strip().upper()
                label = (row.get("label") or "").strip()
                if code and label:
                    index[code] = label
    return index


def _parse_dg_numeric(code: str) -> tuple[float | None, float | None]:
    """Parse DG241-253 or DG253.5-269 into numeric range."""
    value = code.strip().upper()
    m = re.match(r"^([A-Z]+)(\d+(?:\.\d+)?)(?:-(\d+(?:\.\d+)?))?$", value)
    if not m:
        return None, None
    start = float(m.group(2))
    end = float(m.group(3)) if m.group(3) else start
    return start, end


def _nearest_lcc_label(code: str, index: dict[str, str]) -> str | None:
    """Best-effort label when code is a sub-range not listed exactly."""
    start, end = _parse_dg_numeric(code)
    if start is None:
        return None
    best_label: str | None = None
    best_span = float("inf")
    for key, label in index.items():
        k_start, k_end = _parse_dg_numeric(key)
        if k_start is None:
            continue
        if k_start <= start and end <= k_end:
            span = k_end - k_start
            if span < best_span:
                best_span = span
                best_label = label
    return best_label


def label_lcc_code(code: str, index: dict[str, str]) -> dict[str, str]:
    """Return {code, label} for display; never bare code alone."""
    normalized = (code or "").strip().upper()
    if not normalized:
        return {"code": "", "label": ""}
    label = index.get(normalized) or _nearest_lcc_label(normalized, index)
    return {"code": normalized, "label": label or normalized}


def label_lcc_codes(codes: list[str], index: dict[str, str]) -> list[dict[str, str]]:
    seen: set[str] = set()
    labeled: list[dict[str, str]] = []
    for code in codes:
        entry = label_lcc_code(code, index)
        if entry["code"] and entry["code"] not in seen:
            seen.add(entry["code"])
            labeled.append(entry)
    return labeled
