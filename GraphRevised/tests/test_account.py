"""Chrystallum's account, traced statement by statement (29 §4b): its shape, and its check against the graph."""

import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from GraphRevised.narrative.account import Account, AccountSection, Citation, NameLink, Statement, check

OBS = "chr:observation:test:work-a:1.2:abc123"
OBS_B = "chr:observation:test:work-b:4.1:def456"
PHASE = "chr:entity:phase:battle-of-test:engagement"
CLAIM = "chr:assertion:general-a:participated-in:battle-of-test:q0123456789"
PASSAGE = "At dawn the general led the left wing out against the enemy fleet."
PASSAGE_B = "The general, as others say, waited until the wind rose before he moved."


def source(sid, observation=OBS, quotation="the general led the left wing out", **extra):
    return Statement(statement_id=sid, kind="source", text="The general led the left wing out at dawn.",
                     citations=[Citation(observation_id=observation, locator="A 1.2", quotation=quotation)], **extra)


def account(*statements, **extra):
    statements = statements or (source("s1"),)
    return Account(**({"account_id": "chr:account:battle-of-test", "version": 1,
                       "inquiry_id": "chr:inquiry:battle-of-test", "focus_ids": ["chr:entity:battle-of-test"],
                       "title": "The Battle of Test", "written_by": "a model",
                       "sections": [AccountSection(section_id="engagement", title="The lines engage",
                                                   phase_ids=[PHASE], statements=list(statements))]} | extra))


class FakeReader:
    def __init__(self, claims=None, entities=None):
        self.claims = claims if claims is not None else {CLAIM: "proposed"}
        self.present = entities if entities is not None else {PHASE, "chr:entity:battle-of-test", "chr:entity:general-a"}

    def observations(self, ids):
        texts = {OBS: {"passageText": PASSAGE, "editorialNotes": ["Sept. 2, the date in the modern notes"],
                       "passageHash": "h1"},
                 OBS_B: {"passageText": PASSAGE_B, "editorialNotes": [], "passageHash": "h2"}}
        return {i: texts[i] | {"id": i} for i in ids if i in texts}

    def claim_statuses(self, ids):
        return {i: self.claims[i] for i in ids if i in self.claims}

    def entities(self, ids):
        return {i for i in ids if i in self.present}


class ShapeTests(unittest.TestCase):
    def test_each_kind_carries_its_own_evidence(self):
        with self.assertRaises(ValidationError):
            Statement(statement_id="s1", kind="source", text="Said without a passage.")
        with self.assertRaises(ValidationError):
            Statement(statement_id="s2", kind="synthesis", text="Our reading of it.")
        with self.assertRaises(ValidationError):
            Statement(statement_id="s2", kind="synthesis", text="Our reading of it.", rests_on=["s1"],
                      citations=source("x").citations)
        with self.assertRaises(ValidationError):
            Statement(statement_id="s3", kind="signpost", text="Not yet read: the fleet's losses.",
                      claim_ids=[CLAIM])
        with self.assertRaises(ValidationError):
            source("s1", rests_on=["s0"])

    def test_a_synthesis_rests_on_earlier_statements_that_hold_evidence(self):
        ours = Statement(statement_id="s2", kind="synthesis", text="The two accounts differ on why.",
                         rests_on=["s1"])
        later = Statement(statement_id="s0", kind="synthesis", text="Our reading, too early.", rests_on=["s1"])
        signpost = Statement(statement_id="s3", kind="signpost", text="Not yet read: the losses.")
        account(source("s1"), ours)
        with self.assertRaises(ValidationError):
            account(later, source("s1"))
        with self.assertRaises(ValidationError):
            account(source("s1"), signpost, Statement(statement_id="s4", kind="synthesis", text="From nothing.",
                                                      rests_on=["s3"]))
        with self.assertRaises(ValidationError):
            account(source("s1"), source("s1"))

    def test_links_name_words_in_the_statement(self):
        with self.assertRaises(ValidationError):
            source("s1", links=[NameLink(text="the admiral", entity_id="chr:entity:general-a")])
        source("s1", links=[NameLink(text="The general", entity_id="chr:entity:general-a")])

    def test_the_trace_follows_a_synthesis_to_its_passages(self):
        ours = Statement(statement_id="s3", kind="synthesis", text="The sources disagree on the timing.",
                         rests_on=["s1", "s2"])
        traced = account(source("s1", claim_ids=[CLAIM]),
                         source("s2", observation=OBS_B, quotation="waited until the wind rose"), ours).trace()
        self.assertEqual([(t["statement"], t["kind"], t["phases"]) for t in traced],
                         [("s1", "source", [PHASE]), ("s2", "source", [PHASE]), ("s3", "synthesis", [PHASE])])
        self.assertEqual(traced[0]["claims"], [CLAIM])
        self.assertEqual(traced[2]["passages"], sorted([OBS, OBS_B]))

    def test_versions_are_kept(self):
        first = account()
        second = first.revise(first.sections, written_by="the curator")
        self.assertEqual((second.version, second.previous_version, second.status), (2, 1, "draft"))
        with tempfile.TemporaryDirectory() as directory:
            paths = {first.save(Path(directory)), second.save(Path(directory))}
            self.assertEqual({Account.load(p).version for p in paths}, {1, 2})
        with self.assertRaises(ValidationError):
            account(version=2)
        with self.assertRaises(ValidationError):
            account(voice="Plutarch")


class CheckTests(unittest.TestCase):
    def test_a_sound_account_has_no_problems(self):
        self.assertEqual(check(account(source("s1", claim_ids=[CLAIM])), FakeReader()), [])

    def test_quotations_are_verbatim_and_not_editorial_notes(self):
        problems = check(account(source("s1", quotation="the general led the right wing out"),
                                 source("s2", quotation="Sept. 2, the date in the modern notes"),
                                 source("s3", observation="chr:observation:test:missing:1:0")), FakeReader())
        self.assertEqual(len(problems), 3)
        self.assertIn("not in A 1.2", problems[0])
        self.assertIn("editorial note", problems[1])
        self.assertIn("not a preserved observation", problems[2])

    def test_a_changed_passage_makes_the_account_stale(self):
        stale = Statement(statement_id="s1", kind="source", text="The general led the left wing out.",
                          citations=[Citation(observation_id=OBS, locator="A 1.2",
                                              quotation="the general led the left wing out", passage_hash="old")])
        self.assertIn("has changed", check(account(stale), FakeReader())[0])

    def test_claims_phases_and_links_must_be_live(self):
        reader = FakeReader(claims={CLAIM: "rejected"}, entities={"chr:entity:battle-of-test"})
        problems = check(account(source("s1", claim_ids=[CLAIM],
                                        links=[NameLink(text="The general", entity_id="chr:entity:general-a")])),
                         reader)
        self.assertEqual(len(problems), 3)
        self.assertTrue(any("is rejected" in p for p in problems))
        self.assertTrue(any("no phase" in p for p in problems))
        self.assertTrue(any("links to no Entity" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
