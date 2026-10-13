"""Registry v9 (docs/Response - Roman Republican Institutions and Military Hierarchies.md): kinds Type
and Polity, the structure predicates, the quantity qualifier, context and role kinds per predicate,
and Wikidata "part of" chosen by kind. Offline, except the live class, which is rolled back."""

import os
import unittest

from pydantic import ValidationError

from GraphRevised.export.confidence import disputed
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import assertion_id, load_registry, qualifier_signature
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation, QuantityQualifier, Quotation, TimeQualifier
from GraphRevised.proposals.store import _draft_from_stored
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.tests.test_proposals_offline import FakeReader, entity, observation

MANIPLE = entity("chr:entity:test-maniple", "Type")
LEGION = entity("chr:entity:test-polybian-legion", "Type")
FLEET = entity("chr:entity:test-fleet", "Group")
WING = entity("chr:entity:test-wing", "Group")
BATTLE = entity("chr:entity:test-battle", "Event")
CONSUL = entity("chr:entity:test-consul", "Office")
IMPERIUM = entity("chr:entity:test-imperium", "Type")
SICILY = entity("chr:entity:test-sicily", "Place")
COMMANDER = entity("chr:entity:test-commander", "Person", "Q900001")
COLLEGE = entity("chr:entity:test-college", "Group", "Q900002")
TRIUMVIRATE_CLASS = entity("chr:entity:test-triumvirate", "Concept", "Q900003")
ERA = entity("chr:entity:test-era", "Period", "Q900004")
LATE_ERA = entity("chr:entity:test-late-era", "Period", "Q900005")
REPUBLIC = entity("chr:entity:test-republic", "Polity")
WORK = entity("chr:entity:test-polybius", "Work")

PASSAGE = {
    "id": "chr:observation:test:polybius", "observationKind": "passage", "status": "observed",
    "sourceSystem": "Test", "workId": WORK["id"], "editorialNotes": [],
    "passageText": "They divide each legion into thirty maniples, and the consul in Sicily held command.",
}


def structure(predicate, subject, obj, quote, **extra):
    return ProposalDraft(**{
        "predicate": predicate, "subject_id": subject["id"], "object_id": obj["id"],
        "observation_ids": (PASSAGE["id"],),
        "quotations": (Quotation(observation_id=PASSAGE["id"], text=quote),),
        "rationale": "offline v9 test", "proposed_by": "test", **extra,
    })


def thirty(**extra):
    return structure("partOf", MANIPLE, LEGION, "They divide each legion into thirty maniples", **{
        "quantity": QuantityQualifier(source_expression="thirty maniples", minimum=30, maximum=30),
        "qualifier_quotations": (QualifierQuotation(observation_id=PASSAGE["id"], supports="quantity",
                                                    text="thirty maniples"),), **extra})


class RegistryV9Tests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()

    def test_kinds_and_predicates(self):
        self.assertTrue({"Type", "Polity"} <= set(self.registry.entity_kinds))
        for predicate in ("instanceOf", "precedes", "electedBy", "exercisedPower", "heldPower", "servedUnder", "memberOf"):
            self.assertIsNotNone(self.registry.get(predicate), predicate)
        self.assertEqual({m.pid for m in self.registry.get("memberOf").wikidata}, {"P463", "P361"})
        self.assertEqual(self.registry.get("heldPower").context_kinds, frozenset({"Event", "Group", "Place"}))
        self.assertEqual(self.registry.role_kinds(self.registry.get("heldPower")), frozenset({"Office"}))
        self.assertIn("Polity", self.registry.get("alliedWith").subject_kinds)

    def test_part_of_pairs_its_kinds(self):
        part_of = self.registry.get("partOf")
        self.assertTrue(part_of.allows_kinds("Group", "Group"))
        self.assertTrue(part_of.allows_kinds("Type", "Type"))
        self.assertFalse(part_of.allows_kinds("Event", "Group"))
        self.assertFalse(part_of.allows_kinds("Person", "Group"))


class QuantityTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.reader = FakeReader([MANIPLE, LEGION, FLEET, WING, BATTLE, COMMANDER, COLLEGE, WORK], [PASSAGE])

    def test_a_composition_with_its_quantity(self):
        result = validate(thirty(), self.reader, self.registry)
        self.assertEqual(result.outcome, Outcome.VALID, result.reasons)
        self.assertEqual(qualifier_signature(result.draft)["quantity"], {"minimum": 30, "maximum": 30})

    def test_the_figure_is_identity_the_wording_is_not(self):
        same = thirty(quantity=QuantityQualifier(source_expression="maniples", minimum=30, maximum=30))
        other = thirty(quantity=QuantityQualifier(source_expression="thirty maniples", minimum=10, maximum=10))
        ids = [assertion_id("partOf", MANIPLE["id"], LEGION["id"], qualifier_signature(d)) for d in (thirty(), same, other)]
        self.assertEqual(ids[0], ids[1])
        self.assertNotEqual(ids[0], ids[2])

    def test_a_quantity_from_a_passage_needs_its_quotation(self):
        result = validate(thirty(qualifier_quotations=()), self.reader, self.registry)
        self.assertEqual(result.outcome, Outcome.INVALID)
        self.assertIn("a quantity drawn from a passage needs a quantity quotation", result.reasons)

    def test_only_predicates_that_count_take_a_quantity(self):
        draft = structure("memberOf", COMMANDER, COLLEGE, "the consul in Sicily held command",
                          quantity=QuantityQualifier(source_expression="thirty", typical=30))
        result = validate(draft, self.reader, self.registry)
        self.assertIn("memberOf takes no quantity", result.reasons)

    def test_an_event_is_never_part_of_a_force(self):
        result = validate(structure("partOf", BATTLE, FLEET, "the consul in Sicily held command"), self.reader, self.registry)
        self.assertEqual(result.outcome, Outcome.INVALID)
        self.assertTrue(any("not Event to Group" in reason for reason in result.reasons), result.reasons)

    def test_a_quantity_is_consistent(self):
        with self.assertRaises(ValidationError):
            QuantityQualifier(source_expression="x")
        with self.assertRaises(ValidationError):
            QuantityQualifier(source_expression="x", minimum=40, maximum=30)
        with self.assertRaises(ValidationError):
            QuantityQualifier(source_expression="x", minimum=10, maximum=20, typical=30)
        self.assertEqual(QuantityQualifier(source_expression="x", minimum=10, maximum=20, typical=12).display(),
                         "10–20, usually 12")
        self.assertEqual(QuantityQualifier(source_expression="x", typical=2).display(), "2")


class PowerTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.reader = FakeReader([COMMANDER, IMPERIUM, CONSUL, SICILY, BATTLE, WORK], [PASSAGE])

    def held(self, **extra):
        return structure("heldPower", COMMANDER, IMPERIUM, "the consul in Sicily held command", **extra)

    def test_a_power_held_through_an_office_for_a_provincia(self):
        draft = self.held(role_id=CONSUL["id"], context_id=SICILY["id"], context_basis="quotation",
                          qualifier_quotations=(
                              QualifierQuotation(observation_id=PASSAGE["id"], supports="role", text="the consul"),
                              QualifierQuotation(observation_id=PASSAGE["id"], supports="context", text="in Sicily")))
        result = validate(draft, self.reader, self.registry)
        self.assertEqual(result.outcome, Outcome.VALID, result.reasons)
        self.assertIn("undated: heldPower expects a time", result.notes)

    def test_context_and_role_kinds_are_the_predicates(self):
        wrong = self.held(role_id=IMPERIUM["id"], context_id=COMMANDER["id"], context_basis="inquiry",
                          inquiry_id="test")
        reasons = validate(wrong, self.reader, self.registry).reasons
        self.assertIn("context must be an Entity of kind Event or Group or Place, not Person", reasons)
        self.assertIn("role must be an Entity of kind Office, not Type", reasons)


class PartOfByKindTests(unittest.TestCase):
    """Wikidata P361 "part of" evidences whichever predicate fits its endpoints' kinds."""

    def setUp(self):
        self.registry = load_registry()
        self.reader = FakeReader([COMMANDER, COLLEGE, TRIUMVIRATE_CLASS, ERA, LATE_ERA])

    def drafts(self, source, value):
        return drafts_from_observation(observation("chr:observation:p361", source, "P361", value), self.reader, self.registry)

    def test_a_person_part_of_a_body_is_a_member(self):
        result = self.drafts("Q900001", "Q900002")
        self.assertEqual([d.predicate for d in result.drafts], ["memberOf"])

    def test_a_period_part_of_a_period_is_a_subperiod(self):
        self.assertEqual([d.predicate for d in self.drafts("Q900005", "Q900004").drafts], ["subperiodOf"])

    def test_a_person_part_of_a_class_fits_nothing(self):
        result = self.drafts("Q900001", "Q900003")
        self.assertEqual(result.drafts, ())
        self.assertTrue(result.unresolved and "fits no registered predicate" in result.unresolved[0], result.unresolved)


class QuantityDisputeTests(unittest.TestCase):
    def test_different_figures_for_one_time_are_disputed(self):
        thirty_maniples = {"quantity": "minimum=30;maximum=30", "start": 100, "end": 200}
        ten = {"quantity": "minimum=10;maximum=10", "start": 150, "end": 250}
        also_thirty = {"quantity": "minimum=30;maximum=30", "start": 120, "end": 180}
        undated = {"quantity": "minimum=10;maximum=10"}
        self.assertTrue(disputed([thirty_maniples, ten]))
        self.assertFalse(disputed([thirty_maniples, also_thirty]))
        self.assertTrue(disputed([thirty_maniples, undated]))
        # Figures for times apart are not a quantity dispute; whether the times themselves are a
        # dispute is the time rule's (non-overlapping bounds), which does not yet know repeatable facts.


class StoredDraftTests(unittest.TestCase):
    def test_a_window_and_a_quantity_survive_the_round_trip(self):
        stored = {"predicate": "spouseOf", "subjectId": "chr:entity:a", "objectId": "chr:entity:b",
                  "timeSourceExpression": "68 BCE – 50 BCE (Wikidata)", "timeEdtf": "-0067/-0049",
                  "timeCalendar": "julian", "timeNormalizationBasis": "source", "timeMode": "within",
                  "quantitySourceExpression": "thirty", "quantityMinimum": 30, "quantityMaximum": 30}
        draft = _draft_from_stored(stored, [{"observationId": "chr:observation:x", "quotation": None}],
                                   rationale="round trip test", proposed_by="test")
        self.assertEqual(draft.time.mode, "within")
        self.assertEqual(draft.quantity.signature(), {"minimum": 30, "maximum": 30})


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class LiveV9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.operations, cls.registry = load_operations(), load_registry()
        cls.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
            notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()

    def tearDown(self):
        self.tx.rollback()

    def write(self, operation, params):
        return run_write(self.tx, self.operations, operation, params)

    def add(self, *entities):
        for item in entities:
            self.write("upsert_entity", {"id": item["id"], "kind": item["kind"], "label": item["label"],
                                         "description": None, "status": "provisional", "shortLabel": None})

    def passage(self, text):
        self.add(WORK)
        self.write("upsert_passage_observation", {
            "id": PASSAGE["id"], "label": "Test passage", "shortLabel": None, "sourceSystem": "Test",
            "locator": "test:6", "passageText": text, "passageHash": "test", "editorialNotes": [],
            "language": "en", "workTitle": "Test", "author": "Test", "translator": None,
            "editionCitation": "Test", "rights": "test", "sourceUri": "test", "sourceRevision": "test",
            "retrievedAt": "2026-10-13T00:00:00Z", "contentHash": "test", "rawPayloadUri": None, "status": "observed"})
        self.write("link_observation_work", {"observationId": PASSAGE["id"], "workId": WORK["id"]})

    def accept(self, proposal):
        from GraphRevised.proposals.store import accept

        return accept(self.tx, proposal, decided_by="test", decision_basis="v9 live test",
                      decided_at="2026-10-13T00:00:00Z", registry=self.registry, operations=self.operations)

    def test_a_quantified_composition_is_stored_and_accepted(self):
        from GraphRevised.proposals.store import submit

        self.add(MANIPLE, LEGION)
        self.passage(PASSAGE["passageText"])
        submission = submit(self.tx, thirty(), self.registry, self.operations)
        self.assertTrue(submission.stored, submission.validation.reasons)
        stored = self.tx.run("MATCH (a:Assertion {id: $id}) RETURN properties(a) AS a",
                             id=submission.validation.assertion_id).single()["a"]
        self.assertEqual((stored["quantityMinimum"], stored["quantityMaximum"], stored["quantitySourceExpression"]),
                         (30, 30, "thirty maniples"))
        self.assertIn("(quantity 30)", stored["label"])
        self.assertEqual(self.accept(submission.validation.proposal_id)["assertion"]["status"], "accepted")

    def test_a_claim_dated_within_a_window_can_be_accepted(self):
        from GraphRevised.proposals.store import submit

        self.add(COMMANDER, COLLEGE)
        text = "Sometime between 68 and 50 BC the commander joined the college of priests."
        self.passage(text)
        draft = ProposalDraft(
            predicate="memberOf", subject_id=COMMANDER["id"], object_id=COLLEGE["id"],
            observation_ids=(PASSAGE["id"],),
            quotations=(Quotation(observation_id=PASSAGE["id"], text="the commander joined the college of priests"),),
            time=TimeQualifier(source_expression="between 68 and 50 BC", edtf="-0067/-0049", calendar="julian",
                               normalization_basis="source", mode="within"),
            qualifier_quotations=(QualifierQuotation(observation_id=PASSAGE["id"], supports="time",
                                                     text="Sometime between 68 and 50 BC"),),
            rationale="live window test", proposed_by="test")
        submission = submit(self.tx, draft, self.registry, self.operations)
        self.assertTrue(submission.stored, submission.validation.reasons)
        self.assertEqual(self.accept(submission.validation.proposal_id)["assertion"]["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
