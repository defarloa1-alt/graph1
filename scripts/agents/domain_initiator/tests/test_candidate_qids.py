#!/usr/bin/env python3
"""Unit tests for candidate QID validation."""

import unittest

from scripts.agents.domain_initiator.candidate_qids import (
    BLOCKED_CANDIDATE_QIDS,
    CandidateEntity,
    SanitizeResult,
    label_plausible_for_scope,
    sanitize_candidate_qids,
    validate_candidate_qid,
)


class CandidateQidValidationTests(unittest.TestCase):
    def test_blocked_qids_rejected(self) -> None:
        for qid in ("Q2280988", "Q160534", "Q189822"):
            ok, reason = validate_candidate_qid(
                qid,
                CandidateEntity(qid=qid, label="anything"),
                scope_label="Constitutional Institutions",
            )
            self.assertFalse(ok)
            self.assertEqual(reason, "blocked_qid")

    def test_missing_entity_rejected(self) -> None:
        ok, reason = validate_candidate_qid(
            "Q202182",
            CandidateEntity(qid="Q202182", missing=True),
            scope_label="Constitutional Institutions",
        )
        self.assertFalse(ok)
        self.assertEqual(reason, "missing_entity")

    def test_film_instance_rejected(self) -> None:
        ok, reason = validate_candidate_qid(
            "Q999999",
            CandidateEntity(
                qid="Q999999",
                label="Some Film",
                instance_of=["Q11424"],
            ),
            scope_label="Constitutional Institutions",
        )
        self.assertFalse(ok)
        self.assertTrue(reason.startswith("blocked_instance_type"))

    def test_roman_concept_accepted(self) -> None:
        ok, reason = validate_candidate_qid(
            "Q666680",
            CandidateEntity(
                qid="Q666680",
                label="aristocratic republic",
                description="republic ruled by the noble class",
                instance_of=["Q1307214"],
            ),
            scope_label="Constitutional Institutions & Mixed Government",
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "ok")

    def test_kerouac_fails_scope_even_if_not_blocked(self) -> None:
        ok, _ = validate_candidate_qid(
            "Q999001",
            CandidateEntity(qid="Q999001", label="Jack Kerouac", instance_of=["Q5"]),
            scope_label="Constitutional Institutions",
            source_facet="political",
        )
        self.assertFalse(ok)

    def test_polish_priest_fails_roman_catholic_false_positive(self) -> None:
        ok, reason = validate_candidate_qid(
            "Q183238",
            CandidateEntity(
                qid="Q183238",
                label="Andrzej Suski",
                description="Polish Roman-Catholic priest",
                instance_of=["Q5"],
            ),
            scope_label="Popular Assemblies",
            source_facet="political",
        )
        self.assertFalse(ok)
        self.assertIn(reason, ("human_off_topic", "label_off_scope"))

        ok, _ = validate_candidate_qid(
            "Q999001",
            CandidateEntity(qid="Q999001", label="Jack Kerouac", instance_of=["Q5"]),
            scope_label="Constitutional Institutions",
            source_facet="political",
        )
        self.assertFalse(ok)

    def test_sanitize_strips_junk_and_merges_curated(self) -> None:
        entities = {
            "Q2280988": CandidateEntity(qid="Q2280988", label="Blinker en het Bagbag-juweel", instance_of=["Q11424"]),
            "Q666680": CandidateEntity(
                qid="Q666680",
                label="aristocratic republic",
                description="republic ruled by the noble class",
            ),
            "Q2576746": CandidateEntity(
                qid="Q2576746",
                label="Constitution of the Roman Republic",
                description="norms and laws of the Roman Republic",
            ),
            "Q361916": CandidateEntity(
                qid="Q361916",
                label="mixed government",
                description="form of government combining democracy, aristocracy and monarchy",
            ),
            "Q499146": CandidateEntity(
                qid="Q499146",
                label="imperium",
                description="supreme executive power in the Roman state",
            ),
            "Q1887031": CandidateEntity(
                qid="Q1887031",
                label="Mos maiorum",
                description="customs and traditions of ancient Rome",
            ),
            "Q202182": CandidateEntity(qid="Q202182", missing=True),
            "Q160534": CandidateEntity(qid="Q160534", label="Jack Kerouac", instance_of=["Q5"]),
        }
        result = sanitize_candidate_qids(
            ["Q2280988", "Q666680", "Q202182", "Q160534"],
            scope_key="constitutional_institutions",
            scope_label="Constitutional Institutions & Mixed Government",
            source_facet="political",
            entities=entities,
            merge_curated=True,
        )
        self.assertIn("Q666680", result.valid)
        self.assertIn("Q2576746", result.valid)
        self.assertNotIn("Q2280988", result.valid)
        self.assertNotIn("Q160534", result.valid)
        self.assertEqual(len(result.rejected), 3)

    def test_seed_qid_always_allowed(self) -> None:
        self.assertTrue(
            label_plausible_for_scope("Q17167", "Roman Republic", "Any Scope", seed_qid="Q17167")
        )


if __name__ == "__main__":
    unittest.main()
