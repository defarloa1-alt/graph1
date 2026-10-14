"""Capture from reading: highlight parsers (offline) and the capture path (live, rolled back)."""

import os
import unittest

from GraphRevised.capture.core import CaptureError, annotation_label, capture
from GraphRevised.capture.highlights import match_book, parse_kindle, parse_readwise
from GraphRevised.operations import RefusedWrite, load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit
from GraphRevised.proposals.validator import Outcome

KINDLE = """\ufeffA History of Test Wars: The Long Struggle (Ann Author)
- Your Highlight on page 12 | Location 180-183 | Added on Monday, 3 March 2025 10:00:00

It was a struggle over where the centre of gravity would lie.
==========
A History of Test Wars: The Long Struggle (Ann Author)
- Your Note on page 12 | Location 182 | Added on Monday, 3 March 2025 10:01:00

East or West: the hinge of the period.
==========
A History of Test Wars: The Long Struggle (Ann Author)
- Your Bookmark on page 14 | Location 200 | Added on Monday, 3 March 2025 10:02:00


==========
Another Book (Someone Else)
- Your Highlight at location 55-56 | Added on Tuesday, 4 March 2025 09:00:00

A line from another book.
==========
"""

READWISE = '''Highlight,Book Title,Book Author,Amazon Book ID,Note,Color,Tags,Location Type,Location,Highlighted at,Document tags
"Two ways of war, conventional and unconventional.",A History of Test Wars,Ann Author,B0TEST,Strategy as choice,yellow,,location,412,2025-03-05 10:00:00+00:00,
"A page highlight.",A History of Test Wars,Ann Author,B0TEST,,yellow,,page,37,2025-03-05 10:05:00+00:00,
'''

BOOKS = [{"title": "A History of Test Wars", "author": "Ann Author", "workId": "chr:entity:test-history",
          "edition": "Test Press, 2022, Kindle edition"}]


class AnnotationLabelTests(unittest.TestCase):
    def test_a_label_says_what_and_where_never_the_note(self):
        self.assertEqual(annotation_label(None, kind="entity-mention", note_type="detail", mentioned="Empire",
                                          mentioned_kind="Period", source="PeriodO"),
                         "Mention of “Empire” (Period) · PeriodO")
        self.assertEqual(annotation_label(None, kind="passage-of-note", note_type="anecdote"), "Anecdote")
        self.assertEqual(annotation_label(None, kind="curator-note", note_type=None), "Curator note")


class HighlightParserTests(unittest.TestCase):
    def test_kindle_highlights_with_their_notes(self):
        highlights = parse_kindle(KINDLE)
        self.assertEqual(len(highlights), 2)  # the bookmark and the note are not highlights
        first = highlights[0]
        self.assertEqual((first.title, first.author), ("A History of Test Wars: The Long Struggle", "Ann Author"))
        self.assertEqual(first.locator, ("p. 12", "page"))
        self.assertEqual(first.note, "East or West: the hinge of the period.")
        self.assertEqual(highlights[1].locator, ("loc. 55-56", "kindle-location"))

    def test_readwise_rows(self):
        highlights = parse_readwise(READWISE)
        self.assertEqual([h.locator for h in highlights], [("loc. 412", "kindle-location"), ("p. 37", "page")])
        self.assertEqual(highlights[0].note, "Strategy as choice")

    def test_books_are_matched_only_through_the_mapping(self):
        kindle = parse_kindle(KINDLE)
        self.assertEqual(match_book(kindle[0], BOOKS)["workId"], "chr:entity:test-history")
        self.assertIsNone(match_book(kindle[1], BOOKS))


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class CaptureLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.operations, cls.registry = load_operations(), load_registry()
        cls.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
            notifications_min_severity="OFF",
        )
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()
        for entity_id, kind, label in (("chr:entity:test-history", "Work", "Author, A History of Test Wars"),
                                       ("chr:entity:test-battle", "Event", "Test battle"),
                                       ("chr:entity:test-concept", "Concept", "conventional versus unconventional war")):
            run_write(self.tx, self.operations, "upsert_entity", {"id": entity_id, "kind": kind, "label": label,
                                                                  "description": None, "status": "provisional",
                                                                  "shortLabel": None})

    def tearDown(self):
        self.tx.rollback()

    ITEM = {"workId": "chr:entity:test-history", "locator": "p. 12", "locatorType": "page",
            "quote": "The battle represented two ways of war, conventional and unconventional.",
            "note": "Strategy as an eternal choice", "noteType": "interpretation",
            "concerns": ["chr:entity:test-battle"], "edition": "Test Press, 2022"}

    def test_a_capture_keeps_quotation_and_note_apart(self):
        result = capture(self.tx, self.operations, self.ITEM)
        row = self.tx.run(
            """MATCH (o:SourceObservation {id: $o})-[:IN_WORK]->(w:Entity)
               MATCH (a:Annotation {id: $a})-[link:ANNOTATES]->(o)
               MATCH (a)-[:CONCERNS]->(e:Entity)
               RETURN o.observationKind AS kind, o.visibility AS ov, w.id AS work, a.note AS note,
                      a.noteType AS type, a.visibility AS av, a.status AS status, link.quotation AS quotation,
                      a.label AS label, o.shortLabel AS place,
                      collect(e.id) AS concerns""",
            o=result["observationId"], a=result["annotationId"]).single()
        self.assertEqual((row["kind"], row["work"]), ("transcription", "chr:entity:test-history"))
        self.assertEqual((row["ov"], row["av"], row["status"]), ("private", "private", "flagged"))
        self.assertEqual((row["note"], row["type"]), ("Strategy as an eternal choice", "interpretation"))
        self.assertEqual(row["concerns"], ["chr:entity:test-battle"])
        self.assertEqual(row["label"], f"Interpretation · {row['place']}")  # what and where; the note says what
        self.assertEqual(capture(self.tx, self.operations, self.ITEM), result)  # a retry writes nothing new

    def test_a_capture_is_evidence_for_an_attributed_interpretation(self):
        result = capture(self.tx, self.operations, self.ITEM)
        draft = ProposalDraft(
            predicate="exemplifies", subject_id="chr:entity:test-battle", object_id="chr:entity:test-concept",
            observation_ids=(result["observationId"],),
            quotations=(Quotation(observation_id=result["observationId"],
                                  text="two ways of war, conventional and unconventional"),),
            mode="attributed", attributed_to="chr:entity:test-history",
            rationale="The author reads the battle as a contest of two ways of war.", proposed_by="curator",
        )
        submission = submit(self.tx, draft, self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.VALID, submission.validation.reasons)
        category = self.tx.run("MATCH (a:Assertion {id: $id}) RETURN a.category AS c",
                               id=submission.validation.assertion_id).single()["c"]
        self.assertEqual(category, "interpretive")

    def test_refusals(self):
        with self.assertRaises(CaptureError):
            capture(self.tx, self.operations, self.ITEM | {"workId": "chr:entity:test-battle"})  # not a Work
        with self.assertRaises(CaptureError):
            capture(self.tx, self.operations, self.ITEM | {"quote": "x" * 2000})
        result = capture(self.tx, self.operations, self.ITEM)
        with self.assertRaises(RefusedWrite):  # a retry naming other entities
            run_write(self.tx, self.operations, "upsert_annotation", {
                "id": result["annotationId"], "label": None, "kind": "passage-of-note", "noteType": "interpretation",
                "note": "x", "author": "curator", "visibility": "private", "createdAt": "2026-10-12T00:00:00Z",
                "observationId": result["observationId"], "quotation": "x", "concerns": ["chr:entity:test-concept"]})

    def test_annotations_can_be_endorsed_and_deleted(self):
        result = capture(self.tx, self.operations, self.ITEM)
        endorsed = run_write(self.tx, self.operations, "set_annotation_status", {
            "id": result["annotationId"], "status": "endorsed", "decidedBy": "curator",
            "decidedAt": "2026-10-12T00:00:00Z"})[0]["annotation"]
        self.assertEqual(endorsed["status"], "endorsed")
        run_write(self.tx, self.operations, "delete_annotation", {"id": result["annotationId"]})
        remaining = self.tx.run("MATCH (o:SourceObservation {id: $id}) RETURN count(o) AS n",
                                id=result["observationId"]).single()["n"]
        self.assertEqual(remaining, 1)  # the passage stays


if __name__ == "__main__":
    unittest.main()
