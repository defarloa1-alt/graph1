#!/usr/bin/env python3
"""Tests for anchor_to_property_allowlist in harvester."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.tools.wikidata_backlink_harvest import (
    _load_anchor_to_property_allowlist,
    _normalize_qid,
)


def test_load_anchor_allowlist():
    """Q182547 -> P31, Q337547 -> P140, P101, P361 from schema."""
    schema = ROOT / "JSON" / "chrystallum_schema.json"
    allowlist = _load_anchor_to_property_allowlist(schema)
    assert "Q182547" in allowlist
    assert allowlist["Q182547"] == ["P31"]
    assert "Q337547" in allowlist
    assert set(allowlist["Q337547"]) == {"P140", "P101", "P361"}


def test_unknown_anchor_returns_empty():
    """Anchor not in schema returns no override."""
    schema = ROOT / "JSON" / "chrystallum_schema.json"
    allowlist = _load_anchor_to_property_allowlist(schema)
    assert "Q99999" not in allowlist
