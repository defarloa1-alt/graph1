"""Registry v7 (25-LIVES-AND-PLAYGROUND.md section 6): opposition, Work forms and imaginative
claims, and attestation in words. Offline, except the live class, which is rolled back."""

import os
import unittest

from GraphRevised.export.confidence import claim_lines, confidence, family_key
from GraphRevised.operations import RefusedWrite, load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation, Quotation, TimeQualifier
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.tests.test_proposals_offline import (
    AGRIPPA, COMMAND_PASSAGE, FLEET, QUOTE, WORK, FakeReader, command, entity,
)
from GraphRevised import localdb

RIVAL = entity("chr:entity:test-rival", "Person")
WAR = entity("chr:entity:test-war", "Event")
PLAY = {**entity("chr:entity:test-play", "Work"), "form": "play"}
PLAY_PASSAGE = {**COMMAND_PASSAGE, "id": "chr:observation:test:play", "workId": PLAY["id"], "workForm": "play"}
FEUD_PASSAGE = {
    "id": "chr:observation:test:feud", "observationKind": "passage", "status": "observed", "sourceSystem": "Test",
    "workId": WORK["id"], "editorialNotes": [],
    "passageText": "In the year 43 B.C. Agrippa and his rival were enemies, and the war began.",
}


def opposition(**extra):
    return ProposalDraft(**{
        "predicate": "opposed", "subject_id": RIVAL["id"], "object_id": AGRIPPA["id"],
        "observation_ids": (FEUD_PASSAGE["id"],),
        "quotations": (Quotation(observation_id=FEUD_PASSAGE["id"], text="Agrippa and his rival were enemies"),),
        "rationale": "offline v7 test", "proposed_by": "test", **extra,
    })


class OppositionTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.reader = FakeReader([AGRIPPA, RIVAL, WAR, WORK], [FEUD_PASSAGE])

    def test_opposed_is_symmetric_dated_and_has_no_wikidata_mapping(self):
        definition = self.registry.get("opposed")
        self.assertTrue(definition.symmetric)
        self.assertEqual((definition.qualifiers.time, definition.qualifiers.context), ("required", "optional"))
        self.assertEqual(definition.wikidata, ())  # P7047 is for fictive characters only
        self.assertEqual(definition.category, "factual")

    def test_either_order_gives_one_claim_and_an_undated_one_is_noted(self):
        one = validate(opposition(), self.reader, self.registry)
        other = validate(opposition(subject_id=AGRIPPA["id"], object_id=RIVAL["id"]), self.reader, self.registry)
        self.assertEqual(one.outcome, Outcome.VALID, one.reasons)
        self.assertEqual(one.assertion_id, other.assertion_id)
        self.assertTrue(any(note.startswith("undated") for note in one.notes))

    def test_a_dated_opposition_during_a_war(self):
        dated = opposition(
            time=TimeQualifier(source_expression="In the year 43 B.C.", edtf="-0042", calendar="julian",
                               normalization_basis="source"),
            context_id=WAR["id"], context_basis="quotation",
            qualifier_quotations=(
                QualifierQuotation(observation_id=FEUD_PASSAGE["id"], supports="time", text="In the year 43 B.C."),
                QualifierQuotation(observation_id=FEUD_PASSAGE["id"], supports="context", text="the war began")))
        result = validate(dated, self.reader, self.registry)
        self.assertEqual(result.outcome, Outcome.VALID, result.reasons)
        self.assertEqual(result.notes, ())


class ImaginativeTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.reader = FakeReader([AGRIPPA, FLEET, WORK, PLAY], [COMMAND_PASSAGE, PLAY_PASSAGE])

    def in_play(self, **extra):
        return command(observation_ids=(PLAY_PASSAGE["id"],),
                       quotations=(Quotation(observation_id=PLAY_PASSAGE["id"], text=QUOTE.text),), **extra)

    def test_creative_forms_are_work_forms(self):
        self.assertTrue(self.registry.creative_forms)
        self.assertLessEqual(self.registry.creative_forms, self.registry.work_forms)
        self.assertNotIn("biography", self.registry.creative_forms)

    def test_a_claim_attributed_to_a_creative_work_is_imaginative(self):
        result = validate(self.in_play(mode="attributed", attributed_to=PLAY["id"]), self.reader, self.registry)
        self.assertEqual(result.outcome, Outcome.VALID, result.reasons)
        self.assertEqual(result.category, "imaginative")

    def test_nonfiction_keeps_the_predicate_category(self):
        result = validate(command(mode="attributed", attributed_to=WORK["id"]), self.reader, self.registry)
        self.assertEqual(result.category, "factual")

    def test_fiction_never_supports_an_asserted_claim(self):
        result = validate(self.in_play(), self.reader, self.registry)
        self.assertEqual(result.outcome, Outcome.INVALID)
        self.assertTrue(any("creative Work" in reason for reason in result.reasons))


def member(status="proposed", category="factual", authors=(), lines=None, **extra):
    """Authors default to ancient witnesses, one line each."""
    lines = [("witness", a, a.title()) for a in sorted(authors)] if lines is None else lines
    return {"status": status, "category": category, "authors": set(authors), "lines": lines, **extra}


class LinesOfEvidenceTests(unittest.TestCase):
    """42-CORROBORATION-AND-CLAIM-KINDS.md: count independent lines, not authors."""
    STANDING = {"w:plut": "primary", "w:plut2": "primary", "w:dio": "primary",
                "w:weigall": "secondary", "w:hale": "secondary", "w:wiki": "tertiary"}
    IDENTITY = {"w:plut": "plutarch", "w:plut2": "plutarch"}
    NAME = {"w:plut": "Plutarch", "w:plut2": "Plutarch", "w:dio": "Dio", "w:weigall": "Weigall",
            "w:hale": "Hale", "w:wiki": "Wikipedia", "Wikidata": "Wikidata"}

    def fact(self, keys, basis=None, rests=()):
        return member(lines=claim_lines(keys, basis, rests, self.STANDING, self.IDENTITY, self.NAME))

    def judge(self, *members):
        return confidence(members[0], list(members))

    def test_a_modern_retelling_is_not_a_second_source(self):
        self.assertEqual(self.judge(self.fact(["w:plut"]), self.fact(["w:weigall"], "reports", ["w:plut"])),
                         "attested (1 ancient source); retold by Weigall")

    def test_untraced_modern_and_reference_works_are_named_not_counted(self):
        self.assertEqual(self.judge(self.fact(["w:plut"]), self.fact(["w:hale"]), self.fact(["w:wiki"])),
                         "attested (1 ancient source); also in Hale, Wikipedia")
        self.assertEqual(self.judge(self.fact(["w:hale"]), self.fact(["w:weigall"])),
                         "modern sources only (2 works, not traced)")
        self.assertEqual(self.judge(self.fact(["Wikidata"]), self.fact(["w:wiki"])),
                         "reference only (Wikidata, Wikipedia)")

    def test_two_ancient_lines_and_one_author_twice(self):
        self.assertEqual(self.judge(self.fact(["w:plut"]), self.fact(["w:dio"])), "well attested (2 ancient sources)")
        self.assertEqual(self.judge(self.fact(["w:plut"]), self.fact(["w:plut2"])), "attested (1 ancient source)")

    def test_a_report_resting_on_an_ancient_source_adds_its_line(self):
        self.assertEqual(self.judge(self.fact(["w:dio"]), self.fact(["w:weigall"], "reports", ["w:plut"])),
                         "well attested (2 ancient sources); retold by Weigall")

    def test_a_reconstruction(self):
        self.assertEqual(self.judge(self.fact(["w:hale"], "reconstructs"), self.fact(["w:wiki"])),
                         "a modern reconstruction (Hale); also in Wikipedia")
        self.assertEqual(self.judge(self.fact(["w:dio"]), self.fact(["w:hale"], "reconstructs")),
                         "attested (1 ancient source); reconstructed by Hale")

    def test_a_reference_work_that_cites_its_source_joins_that_line(self):
        self.assertEqual(self.judge(self.fact(["w:wiki"], "reports", ["w:dio"])),
                         "attested (1 ancient source); retold by Wikipedia")
        self.assertEqual(self.judge(self.fact(["w:wiki"], "reports", [])), "reference only (Wikipedia)")

    def test_an_unclassified_work_counts_as_reference(self):
        self.assertEqual(claim_lines(["w:new"], None, [], {}, {}, {}), [("reference", "w:new", "w:new")])


class ConfidenceTests(unittest.TestCase):
    def test_a_family_shares_its_base_id(self):
        base = "chr:assertion:cleopatra:participated-in:battle-of-actium"
        self.assertEqual(family_key(base + ":q0123456789"), base)
        self.assertEqual(family_key(base), base)

    def test_a_lone_claim_without_evidence_is_carried_by_its_family(self):
        lone = member()
        family = [lone, member(authors={"plutarch"}), member(authors={"dio"}), member(authors={"plutarch"})]
        self.assertEqual(confidence(lone, [lone]), "no evidence yet")
        self.assertEqual(confidence(lone, family), "well attested (2 ancient sources)")

    def test_one_author_and_rejected_members(self):
        claim = member(authors={"weigall"})
        self.assertEqual(confidence(claim, [claim, member(status="rejected", authors={"hale"})]), "attested (1 ancient source)")

    def test_readings_and_imagination_are_kinds_not_low_scores(self):
        reading = member(category="interpretive", authors={"hale"})
        self.assertEqual(confidence(reading, [reading]), "one author's reading")
        both = [reading, member(category="interpretive", authors={"weigall"})]
        self.assertEqual(confidence(reading, both), "a reading shared by 2 authors")
        imagined = member(category="imaginative", authors={"shakespeare"})
        self.assertEqual(confidence(imagined, [imagined, member(authors={"plutarch"})]), "imagined")

    def test_fiction_does_not_attest_a_fact(self):
        fact = member(authors={"plutarch"})
        self.assertEqual(confidence(fact, [fact, member(category="imaginative", authors={"shakespeare"})]),
                         "attested (1 ancient source)")

    def test_disputes_compare_values_not_wording(self):
        a = member(authors={"dio"}, start=100, end=100, once=True)
        b = member(authors={"hale"}, start=100, end=100)
        c = member(authors={"weigall"}, start=500, end=500)
        self.assertEqual(confidence(a, [a, b]), "well attested (2 ancient sources)")
        self.assertEqual(confidence(a, [a, b, c]), "disputed (3 authors)")
        self.assertEqual(confidence(a, [a, member(authors={"x"}, context="chr:entity:a"),
                                        member(authors={"y"}, context="chr:entity:b")]), "disputed (3 authors)")

    def test_a_fact_that_recurs_is_not_disputed_by_its_occasions(self):
        consul = member(authors={"wikidata"}, start=100, end=100)
        again = member(authors={"wikidata"}, start=500, end=500, context="chr:entity:b")
        self.assertEqual(confidence(consul, [consul, again]), "attested (1 ancient source)")
        self.assertEqual(confidence({**consul, "once": True}, [consul, again]), "disputed (1 author)")


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class WorkFormLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.operations, cls.registry = load_operations(), load_registry()
        cls.driver = GraphDatabase.driver(
            localdb.uri(),
            auth=localdb.auth(),
            notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=localdb.database())

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()
        self.tx.run("CREATE (:Entity:Work {id: 'chr:entity:test-v7-play', kind: 'Work', label: 'Test play', status: 'provisional'})")

    def tearDown(self):
        self.tx.rollback()

    def set_form(self, form):
        return run_write(self.tx, self.operations, "set_work_form", {
            "workId": "chr:entity:test-v7-play", "form": form, "allowedForms": sorted(self.registry.work_forms)})

    def test_a_form_must_be_known_and_is_fixed_once_claims_rest_on_it(self):
        with self.assertRaises(RefusedWrite):
            self.set_form("rumour")
        self.set_form("history")
        self.set_form("play")  # nothing attributed yet: may change
        self.tx.run("MATCH (w:Entity {id: 'chr:entity:test-v7-play'}) "
                    "CREATE (:Assertion {id: 'chr:assertion:test-v7'})-[:ATTRIBUTED_TO]->(w)")
        self.set_form("play")  # a retry
        with self.assertRaises(RefusedWrite):
            self.set_form("history")


if __name__ == "__main__":
    unittest.main()
