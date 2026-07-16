#!/usr/bin/env python3
"""Tests for seed knowledge index loading and validation."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.agents.domain_initiator.candidate_qids import (
    CandidateEntity,
    validate_candidate_qid,
)
from scripts.agents.domain_initiator.seed_index import allowed_qid_set, load_seed_index


class SeedIndexTests(unittest.TestCase):
    def test_allowed_qid_set(self) -> None:
        index = {
            "seed": {"qid": "Q17167"},
            "allowed_candidate_qids": {
                "seed_qid": "Q17167",
                "union": ["Q17167", "Q666680", "Q124988"],
            },
        }
        allowed = allowed_qid_set(index)
        self.assertIn("Q17167", allowed)
        self.assertIn("Q666680", allowed)
        self.assertNotIn("Q2280988", allowed)

    def test_not_seed_connected_rejected(self) -> None:
        index = {
            "allowed_candidate_qids": {"union": ["Q17167", "Q666680"]},
        }
        ok, reason = validate_candidate_qid(
            "Q2280988",
            CandidateEntity(
                qid="Q2280988",
                label="Blinker en het Bagbag-juweel",
                instance_of=["Q11424"],
            ),
            scope_label="Constitutional Institutions",
            seed_qid="Q17167",
            source_facet="political",
            seed_index=index,
        )
        self.assertFalse(ok)
        self.assertIn(reason, ("blocked_qid", "blocked_instance_type:Q11424", "not_seed_connected"))

    def test_seed_index_accepts_connected_qid(self) -> None:
        index = {
            "allowed_candidate_qids": {"union": ["Q17167", "Q124988"]},
        }
        ok, reason = validate_candidate_qid(
            "Q124988",
            CandidateEntity(qid="Q124988", label="Battle of Cannae"),
            scope_label="Wars",
            seed_qid="Q17167",
            source_facet="military",
            seed_index=index,
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "seed_index")

    def test_load_seed_index_roundtrip(self) -> None:
        payload = {
            "seed": {"qid": "Q17167", "label": "Roman Republic"},
            "allowed_candidate_qids": {"union": ["Q17167"]},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Q17167_seed_index.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            loaded = load_seed_index("Q17167", derived_dir=Path(tmp))
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded["seed"]["label"], "Roman Republic")


if __name__ == "__main__":
    unittest.main()
