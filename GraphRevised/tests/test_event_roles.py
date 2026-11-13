"""Roles on the participants of a depicted event (D-138, registry v13), offline."""

import unittest

from GraphRevised.proposals.passage_reader import ReaderParticipant, depicted_drafts, event_role_aliases, to_depicted
from GraphRevised.proposals.registry import REGISTRY_PATH, load_registry
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.tests.test_depicted_events import (
    BATTLE, INQUIRY, OBSERVATION, WORK, event, output,
)
from GraphRevised.tests.test_proposals_offline import FakeReader, entity

CAPTOR = "chr:entity:test-captor-role"
CONSUL = "chr:entity:test-consul"
FLEET = "chr:entity:test-fleet"
TEXT = "At the tenth hour the victors' fleet took three hundred ships as captors of the line."
PASSAGE = {"id": OBSERVATION, "passageText": TEXT}
SCOPE = {FLEET, CAPTOR, CONSUL, BATTLE}


def capture(role_id="", role_quotation=""):
    return event("e1", "The fleet takes the ships", "the victors' fleet took three hundred ships",
                 participants=[ReaderParticipant(entity_id=FLEET, quotation="the victors' fleet took",
                                                 role_id=role_id, role_quotation=role_quotation)])


def reader(role_kind):
    return FakeReader(
        [entity("chr:entity:depicted:test-chronicle:the-fleet-takes-the-ships", "Event"), entity(BATTLE, "Event"),
         entity(FLEET, "Group"), entity(CAPTOR, role_kind), entity(WORK, "Work")],
        [{**PASSAGE, "observationKind": "passage", "status": "observed", "sourceSystem": "Test", "workId": WORK,
          "editorialNotes": []}])


def participation(events):
    (draft,) = [d for d in depicted_drafts(events[0], OBSERVATION, "test-model", INQUIRY)
                if d.predicate == "participatedIn"]
    return draft


class EventRoleTests(unittest.TestCase):
    def test_a_role_shown_verbatim_reaches_the_claim(self):
        events, refused = to_depicted(output(capture(CAPTOR, "as captors of the line")), PASSAGE, INQUIRY, set(), SCOPE)
        self.assertEqual(refused, [])
        draft = participation(events)
        self.assertEqual(draft.role_id, CAPTOR)
        self.assertEqual([(q.supports, q.text) for q in draft.qualifier_quotations], [("role", "as captors of the line")])

    def test_a_role_not_shown_or_not_in_scope_is_dropped_and_the_participant_kept(self):
        for role_id, quotation, reason in ((CAPTOR, "as prize-takers of the line", "role quotation not verbatim"),
                                           ("chr:entity:elsewhere", "as captors of the line", "role not in inquiry scope")):
            with self.subTest(reason=reason):
                events, _ = to_depicted(output(capture(role_id, quotation)), PASSAGE, INQUIRY, set(), SCOPE)
                self.assertIsNone(participation(events).role_id)
                self.assertEqual(events[0]["dropped"][0]["reason"], reason)

    def test_no_role_is_a_plain_participation(self):
        events, _ = to_depicted(output(capture()), PASSAGE, INQUIRY, set(), SCOPE)
        draft = participation(events)
        self.assertIsNone(draft.role_id)
        self.assertEqual(draft.qualifier_quotations, ())

    def test_registry_v13_takes_a_type_as_a_role_and_v12_does_not(self):
        events, _ = to_depicted(output(capture(CAPTOR, "as captors of the line")), PASSAGE, INQUIRY, set(), SCOPE)
        draft = participation(events)
        v13, v12 = (load_registry(REGISTRY_PATH.with_name(f"predicates.{v}.json")) for v in ("v13", "v12"))
        self.assertEqual(v13.version, "predicates-v13")
        self.assertEqual(validate(draft, reader("Type"), v13).outcome, Outcome.VALID)
        self.assertEqual(validate(draft, reader("Office"), v13).outcome, Outcome.VALID)
        self.assertNotEqual(validate(draft, reader("Type"), v12).outcome, Outcome.VALID)
        self.assertNotEqual(validate(draft, reader("Person"), v13).outcome, Outcome.VALID)

    def test_v13_changes_only_participation_roles(self):
        v13, v12 = (load_registry(REGISTRY_PATH.with_name(f"predicates.{v}.json")) for v in ("v13", "v12"))
        self.assertEqual(set(v13.predicates), set(v12.predicates))
        changed = [p for p in v13.predicates if v13.predicates[p] != v12.predicates[p]]
        self.assertEqual(changed, ["participatedIn"])
        self.assertEqual(v13.role_kinds(v13.get("participatedIn")), frozenset({"Office", "Type"}))


class ObjectInvolvementTests(unittest.TestCase):
    """Registry v14: an Object takes part in an event only through a role (seized, dedicated, destroyed)."""

    def setUp(self):
        self.v14 = load_registry()
        self.ship = entity("chr:entity:test-flagship", "Object")

    def involvement(self, role_id):
        quotation = "as captors of the line" if role_id else ""
        events, _ = to_depicted(output(capture(role_id or "", quotation)), PASSAGE, INQUIRY, set(), SCOPE)
        draft = participation(events)
        return draft.model_copy(update={"predicate": "involvedIn", "subject_id": self.ship["id"]})

    def reader(self):
        base = reader("Type")
        return FakeReader(list(base.entities.values()) + [self.ship], list(base.observations.values()))

    def test_an_object_with_a_role_is_involved(self):
        self.assertEqual(self.v14.version, "predicates-v14")
        self.assertEqual(validate(self.involvement(CAPTOR), self.reader(), self.v14).outcome, Outcome.VALID)

    def test_an_object_without_a_role_is_noted_and_cannot_participate(self):
        # "required" means expected: the claim is kept with a note, as for any qualifier a source omits
        bare = validate(self.involvement(None), self.reader(), self.v14)
        self.assertEqual(bare.outcome, Outcome.VALID)
        self.assertIn("no role: involvedIn expects one", bare.notes)
        participating = self.involvement(CAPTOR).model_copy(update={"predicate": "participatedIn"})
        self.assertNotEqual(validate(participating, self.reader(), self.v14).outcome, Outcome.VALID)

    def test_v14_adds_only_involvement(self):
        v13 = load_registry(REGISTRY_PATH.with_name("predicates.v13.json"))
        self.assertEqual(set(self.v14.predicates) - set(v13.predicates), {"involvedIn"})
        self.assertTrue(all(self.v14.predicates[p] == v13.predicates[p] for p in v13.predicates))



SHIP = "chr:entity:test-flagship"
SEIZED = "chr:entity:test-seized-role"


def seizure(object_id=SHIP, role_id=SEIZED, role_quotation="took three hundred ships"):
    return capture(CAPTOR, "as captors of the line").model_copy(update={"objects": [
        ReaderParticipant(entity_id=object_id, quotation="three hundred ships as captors",
                          role_id=role_id, role_quotation=role_quotation)]})


class ReaderObjectTests(unittest.TestCase):
    """A named object in a depicted event becomes involvedIn with its role, never participatedIn."""

    def test_an_object_is_drafted_as_involved_with_its_role(self):
        events, refused = to_depicted(output(seizure()), PASSAGE, INQUIRY, set(), SCOPE | {SHIP, SEIZED})
        self.assertEqual(refused, [])
        drafts = depicted_drafts(events[0], OBSERVATION, "test-model", INQUIRY)
        (involved,) = [d for d in drafts if d.predicate == "involvedIn"]
        self.assertEqual((involved.subject_id, involved.object_id, involved.role_id), (SHIP, events[0]["id"], SEIZED))
        self.assertEqual([q.text for q in involved.qualifier_quotations], ["took three hundred ships"])
        self.assertNotIn(SHIP, [d.subject_id for d in drafts if d.predicate == "participatedIn"])

    def test_an_object_not_in_scope_is_dropped(self):
        events, _ = to_depicted(output(seizure()), PASSAGE, INQUIRY, set(), SCOPE)
        self.assertEqual(events[0]["objects"], [])
        self.assertEqual(events[0]["dropped"][0], {"object": SHIP, "reason": "not in inquiry scope"})

    def test_the_curated_roles_carry_their_aliases(self):
        aliases = event_role_aliases()
        self.assertEqual(len(aliases), 22)
        self.assertIn("prisoner", aliases["chr:entity:role-captive"])


if __name__ == "__main__":
    unittest.main()
