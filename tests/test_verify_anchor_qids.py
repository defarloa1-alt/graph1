#!/usr/bin/env python3
"""
Tests for verify_anchor_qids: _labels_compatible heuristic.
Uses unit tests only (no Wikidata API calls).
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Import from scripts - add project root to path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.analysis.verify_anchor_qids import _labels_compatible, run_verification


class TestLabelsCompatible:
    """Test the label compatibility heuristic."""

    def test_exact_match(self):
        assert _labels_compatible("Roman Republic", "Roman Republic") is True

    def test_case_insensitive(self):
        assert _labels_compatible("roman republic", "Roman Republic") is True

    def test_shared_significant_word(self):
        assert _labels_compatible("Republican ideals", "Mos maiorum") is False
        assert _labels_compatible("Roman Senate", "Roman Republic") is True  # Roman
        assert _labels_compatible("Government", "government") is True

    def test_substring(self):
        assert _labels_compatible("Late Roman Republic", "Roman Republic") is True
        assert _labels_compatible("Roman", "Roman Republic") is True

    def test_mismatch(self):
        assert _labels_compatible("Late Republic", "Plauen") is False
        assert _labels_compatible("Government", "Education") is False
        assert _labels_compatible("Public ritual", "Robert E. Howard") is False

    def test_short_words_ignored(self):
        # "way" and "of" are short; "mos" might match if in both
        assert _labels_compatible("mos maiorum", "Mos maiorum") is True


class TestRunVerification:
    """Test run_verification with mocked/fixture data."""

    def test_empty_anchors(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([], f)
            path = Path(f.name)
        try:
            mismatches = run_verification(path, verbose=False)
            assert mismatches == []
        finally:
            path.unlink()

    def test_anchors_list_format_mocked(self):
        """Run verification with mocked Wikidata - no API calls."""
        anchors = [
            {"qid": "Q17167", "label": "Roman Republic"},
            {"qid": "Q5", "label": "human"},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(anchors, f)
            path = Path(f.name)
        try:
            with patch(
                "scripts.analysis.verify_anchor_qids.fetch_wikidata_label",
                side_effect=lambda qid: {"Q17167": "Roman Republic", "Q5": "human"}.get(qid),
            ) as _:
                mismatches = run_verification(path, verbose=False)
            assert isinstance(mismatches, list)
            assert len(mismatches) == 0  # labels match
        finally:
            path.unlink()

    def test_anchors_list_format_mismatch_mocked(self):
        """Run verification with mocked mismatch - Q3952=Plauen."""
        anchors = [{"qid": "Q3952", "label": "Late Republic"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(anchors, f)
            path = Path(f.name)
        try:
            with patch(
                "scripts.analysis.verify_anchor_qids.fetch_wikidata_label",
                return_value="Plauen",  # actual Wikidata label for Q3952
            ) as _:
                mismatches = run_verification(path, verbose=False)
            assert len(mismatches) == 1
            assert mismatches[0]["qid"] == "Q3952"
            assert mismatches[0]["wd"] == "Plauen"
        finally:
            path.unlink()

    def test_anchors_wrapped_format(self):
        anchors = [{"qid": "Q17167", "label": "Roman Republic"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"anchors": anchors}, f)
            path = Path(f.name)
        try:
            with patch(
                "scripts.analysis.verify_anchor_qids.fetch_wikidata_label",
                return_value="Roman Republic",
            ) as _:
                mismatches = run_verification(path, verbose=False)
            assert isinstance(mismatches, list)
        finally:
            path.unlink()
