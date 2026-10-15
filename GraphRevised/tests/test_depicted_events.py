"""Depicted events (reader prompt v13, registry v10; 23-NARRATIVE-AND-NOTES.md section 2,
29-EVENT-CENTRED-INQUIRY.md): one source's actions within an event, checked span by span and
turned into attributed claims, with their order where the source gives it. Offline."""

import unittest
from dataclasses import replace

from GraphRevised.proposals.entities import depicted_event_id
from GraphRevised.proposals.passage_reader import (
    Inquiry, ReaderDepictedEvent, ReaderEventLink, ReaderOutput, ReaderParticipant, depicted_drafts, to_depicted,
)
from GraphRevised.proposals.registry import REGISTRY_PATH, load_registry
from GraphRevised.proposals.validator import Outcome, validate
from GraphRevised.tests.test_proposals_offline import FakeReader, entity

WORK = "chr:entity:test-chronicle"
BATTLE = "chr:entity:test-battle"
ADMIRAL = "chr:entity:test-admiral"
QUEEN = "chr:entity:test-queen"
CAPE = "chr:entity:test-cape"
OBSERVATION = "chr:observation:test:chronicle-9.1"
TEXT = ("At the sixth hour the queen hoisted her sails and fled through the line. When the admiral saw this, "
        "he left his flagship and followed her, and after this the fleet fought on near the cape until evening.")
PASSAGE = {"id": OBSERVATION, "passageText": TEXT}
INQUIRY = Inquiry(
    id="chr:inquiry:test-battle", version=1, label="The test battle", subject={"id": "chr:subject:test", "label": "Test"},
    focus=[], scope=[], guidance=[], source={"type": "perseus-tei", "edition": "none.xml"},
    work_id=WORK, narrative_event_id=BATTLE, calendar="julian", proposable_kinds=("Event",), voice="Chronicler",
)
SCOPE = {ADMIRAL, QUEEN, CAPE, BATTLE}


def event(key, label, quotation, **extra):
    fields = dict(key=key, label=label, existing_id="", quotation=quotation, within_narrative_event=True,
                  participants=[], place_id="", place_quotation="", time_expression="", time_quotation="",
                  relative_offset="", links=[])
    return ReaderDepictedEvent(**(fields | extra))


FLIGHT = event("e1", "The queen's flight", "the queen hoisted her sails and fled through the line",
               participants=[ReaderParticipant(entity_id=QUEEN, quotation="the queen hoisted her sails")],
               time_expression="At the sixth hour", time_quotation="At the sixth hour the queen", relative_offset="PT6H")
PURSUIT = event("e2", "The admiral follows the queen", "he left his flagship and followed her",
                participants=[ReaderParticipant(entity_id=ADMIRAL, quotation="When the admiral saw this")],
                links=[ReaderEventLink(relation="triggered_by", target="e1", quotation="When the admiral saw this")])
FIGHTING_ON = event("e3", "The fleet fights on", "the fleet fought on near the cape until evening",
                    place_id=CAPE, place_quotation="fought on near the cape",
                    links=[ReaderEventLink(relation="after", target="e2", quotation="and after this the fleet fought on")])


def output(*events):
    return ReaderOutput(claims=[], unresolved_mentions=[], notes=[], periods=[], depicted_events=list(events))


class DepictedEventTests(unittest.TestCase):
    def test_events_get_one_id_per_source_and_label(self):
        events, refused = to_depicted(output(FLIGHT, PURSUIT, FIGHTING_ON), PASSAGE, INQUIRY, set(), SCOPE)
        self.assertEqual(refused, [])
        self.assertEqual(events[0]["id"], "chr:entity:depicted:test-chronicle:the-queen-s-flight")
        self.assertEqual(events[0]["id"], depicted_event_id(WORK, "The queen's flight"))
        self.assertEqual(events[1]["links"], [{"relation": "triggered_by", "target": events[0]["id"],
                                               "quotation": "When the admiral saw this"}])

    def test_drafts_carry_the_order_the_source_gives(self):
        events, _ = to_depicted(output(FLIGHT, PURSUIT, FIGHTING_ON), PASSAGE, INQUIRY, set(), SCOPE)
        flight, pursuit, fighting = (depicted_drafts(e, OBSERVATION, "test-model", INQUIRY) for e in events)
        self.assertEqual([(d.predicate, d.subject_id, d.object_id) for d in flight], [
            ("partOf", events[0]["id"], BATTLE), ("participatedIn", QUEEN, events[0]["id"]),
            ("occurred", events[0]["id"], None)])
        occurred = flight[2]
        self.assertEqual((occurred.time.source_expression, occurred.time.relative_offset, occurred.context_id),
                         ("At the sixth hour", "PT6H", BATTLE))
        self.assertIn(("triggeredBy", events[1]["id"], events[0]["id"]),
                      [(d.predicate, d.subject_id, d.object_id) for d in pursuit])
        # "after" is stored the other way round: the earlier event happenedBefore the later one
        self.assertIn(("happenedBefore", events[1]["id"], events[2]["id"]),
                      [(d.predicate, d.subject_id, d.object_id) for d in fighting])
        self.assertIn(("occurredAt", events[2]["id"], CAPE), [(d.predicate, d.subject_id, d.object_id) for d in fighting])
        self.assertTrue(all(d.mode == "attributed" and d.attributed_to == WORK for d in flight + pursuit + fighting))

    def test_drafts_validate_against_registry_v10(self):
        registry = load_registry()
        events, _ = to_depicted(output(FLIGHT, PURSUIT, FIGHTING_ON), PASSAGE, INQUIRY, set(), SCOPE)
        entities = [entity(e["id"], "Event") for e in events] + [
            entity(BATTLE, "Event"), entity(ADMIRAL, "Person"), entity(QUEEN, "Person"), entity(CAPE, "Place"),
            entity(WORK, "Work")]
        reader = FakeReader(entities, [{**PASSAGE, "observationKind": "passage", "status": "observed",
                                        "sourceSystem": "Test", "workId": WORK, "editorialNotes": []}])
        for e in events:
            for draft in depicted_drafts(e, OBSERVATION, "test-model", INQUIRY):
                with self.subTest(predicate=draft.predicate, subject=draft.subject_id):
                    result = validate(draft, reader, registry)
                    self.assertEqual(result.outcome, Outcome.VALID, result.reasons)

    def test_parts_the_passage_does_not_show_are_dropped(self):
        loose = event("e1", "The queen's flight", "the queen hoisted her sails and fled through the line",
                      participants=[ReaderParticipant(entity_id="chr:entity:test-stranger", quotation="the queen hoisted her sails"),
                                    ReaderParticipant(entity_id=QUEEN, quotation="the queen raised a banner high")],
                      links=[ReaderEventLink(relation="after", target="e9", quotation="When the admiral saw this")])
        (checked,), refused = to_depicted(output(loose), PASSAGE, INQUIRY, set(), SCOPE)
        self.assertEqual(refused, [])
        self.assertEqual((checked["participants"], checked["links"]), ([], []))
        self.assertEqual(len(checked["dropped"]), 3)

    def test_refusals(self):
        cases = {
            "verbatim": event("e1", "Invented", "the queen sailed to the moon and back again"),
            "existing_id": event("e1", "", "the queen hoisted her sails", existing_id="chr:entity:depicted:other:x"),
            "label": event("e1", " ", "the queen hoisted her sails"),
            "offset": event("e1", "Before", "the queen hoisted her sails", within_narrative_event=False,
                            time_expression="At the sixth hour", time_quotation="At the sixth hour",
                            relative_offset="PT6H"),
        }
        for name, case in cases.items():
            with self.subTest(case=name):
                events, refused = to_depicted(output(case), PASSAGE, INQUIRY, set(), SCOPE)
                self.assertEqual((events, len(refused)), ([], 1))

    def test_an_event_continued_from_an_earlier_passage(self):
        known = depicted_event_id(WORK, "The queen's flight")
        later = event("e1", "", "he left his flagship and followed her", existing_id=known)
        (checked,), _ = to_depicted(output(later), PASSAGE, INQUIRY, {known}, SCOPE)
        self.assertEqual((checked["id"], checked["new"]), (known, False))

    def test_an_inquiry_without_event_proposals_refuses_them(self):
        events, refused = to_depicted(output(FLIGHT), PASSAGE, replace(INQUIRY, proposable_kinds=()), set(), SCOPE)
        self.assertEqual((events, len(refused)), ([], 1))

    def test_registry_v11_dates_participation(self):
        registry = load_registry()
        self.assertEqual(registry.version, "predicates-v11")
        self.assertEqual(registry.get("participatedIn").qualifiers.time, "optional")

    def test_registry_v10(self):
        registry = load_registry(REGISTRY_PATH.with_name("predicates.v10.json"))
        self.assertEqual(registry.version, "predicates-v10")
        before = registry.get("happenedBefore")
        self.assertTrue(before.allows_kinds("Event", "Event"))
        self.assertEqual(before.qualifiers.time, "none")
        self.assertEqual(registry.get("precedes").qualifiers.time, "required")  # the cursus keeps its dates
        self.assertEqual(registry.get("occurred").qualifiers.context, "optional")


if __name__ == "__main__":
    unittest.main()
