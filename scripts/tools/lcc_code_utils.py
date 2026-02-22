from __future__ import annotations

import re
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
