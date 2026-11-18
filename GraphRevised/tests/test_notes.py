"""The curator's Obsidian notes: read, checked, and the id written back (capture/notes.py), without the graph."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from GraphRevised.capture import notes as notes_module
from GraphRevised.capture.notes import NoteError, check, notes_in, read_note, write_back_id

BOOK = """---
chrystallum: note
id:
noteType: excerpt
status: draft
visibility: private
isbn: "978-0-306-40615-7"
page: 5
chapter: Prologue
work: chr:entity:a-book
quotationStatus: private-copy
concerns:
  - chr:entity:a-battle
related:
  - "[[Other]]"
tags:
---

> [!quote]
> The first line of the passage,
> and its second line.
"""

IMAGE = """---
chrystallum: image
id:
image: "[[picture.png]]"
depicts: "A reconstruction of a monument"
rights: copyright
visibility: private
concerns:
  - chr:entity:a-battle
---

![[picture.png]]

What I think of it.
"""


class FakeReader:
    def entities(self, ids):
        return {i: i for i in ids if i in {"chr:entity:a-battle", "chr:entity:a-book"}}

    def work(self, work_id):
        return "A Book" if work_id == "chr:entity:a-book" else None

    def work_for_lccn(self, lccn):
        return ["chr:entity:a-book"] if lccn == "2099000001" else []


class Neo4jNoteReaderTests(unittest.TestCase):
    class Transaction:
        def __init__(self, label):
            self.label = label
            self.query = None

        def run(self, query, **_):
            self.query = query
            return self

        def single(self):
            return {"label": self.label} if self.label else None

    def test_work_lookup_uses_the_subtype_label(self):
        tx = self.Transaction("A Book")
        self.assertEqual(notes_module.Neo4jNoteReader(tx).work("chr:entity:a-book"), "A Book")
        self.assertIn("MATCH (w:Entity:Work {id: $id})", tx.query)

    def test_non_work_is_not_returned_as_a_work(self):
        tx = self.Transaction(None)
        self.assertIsNone(notes_module.Neo4jNoteReader(tx).work("chr:entity:a-battle"))
        self.assertIn("MATCH (w:Entity:Work {id: $id})", tx.query)


class NoteTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.folder = Path(self.directory.name)
        (self.folder / "images").mkdir()
        (self.folder / "images" / "picture.png").write_bytes(b"not really a png")
        (self.folder / "_templates").mkdir()
        (self.folder / "_templates" / "note.md").write_text(BOOK, encoding="utf-8")
        (self.folder / "Other.md").write_text(IMAGE, encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def write(self, name, text):
        path = self.folder / f"{name}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def problems(self, text, name="Note"):
        return check(read_note(self.write(name, text)), FakeReader(), set(notes_in(self.folder)) | {name}, self.folder)

    def test_a_sound_book_note_and_image_note(self):
        note = read_note(self.write("Note", BOOK))
        self.assertEqual(note.quote, "The first line of the passage, and its second line.")
        self.assertEqual(note.locator(), "Prologue, p. 5")
        self.assertEqual(self.problems(BOOK), [])
        self.assertEqual(self.problems(IMAGE, "Image"), [])
        self.assertEqual(read_note(self.folder / "Other.md").text, "What I think of it.")

    def test_the_books_footnote_is_kept_apart_from_the_curators_text(self):
        text = BOOK.replace("> and its second line.", "> and its second line.[^34] A third sentence.") + (
            "\n[^34]: Dio 50.12.7; Plut. Ant. 63.3;\n    Kromayer 1899, 21.\n\nWhat I think of it.\n")
        note = read_note(self.write("Note", text))
        self.assertEqual(note.quote, "The first line of the passage, and its second line. A third sentence.")
        self.assertEqual(note.text, "What I think of it.")
        [footnote] = note.footnotes
        self.assertEqual((footnote.mark, footnote.text), ("34", "Dio 50.12.7; Plut. Ant. 63.3; Kromayer 1899, 21."))
        self.assertEqual(footnote.sentence, "The first line of the passage, and its second line.")
        self.assertIn('"mark": "34"', footnote.stored())
        self.assertEqual(self.problems(text), [])

    def test_a_footnote_and_its_mark_must_match(self):
        no_note = BOOK.replace("second line.", "second line.[^2]")
        self.assertIn("footnote mark [^2] in the quote has no footnote written below it", self.problems(no_note))
        no_mark = BOOK + "\n[^3]: Dio 50.1.\n"
        self.assertIn("footnote [^3] has no mark in the quote: put [^3] where the book has it", self.problems(no_mark))

    def test_suggestions_rank_a_whole_label_first_and_skip_common_words(self):
        from GraphRevised.capture.notes import significant_words, suggest_concerns
        text = BOOK.replace("The first line of the passage,", "The Actium promontory was sandy; Antony's army").replace(
            "and its second line.", "camped there.")
        note = read_note(self.write("Note", text))
        self.assertNotIn("there", significant_words(note.quote))
        self.assertIn("antony", significant_words(note.quote))
        rows = [{"id": "a", "label": "Battle of Actium", "kind": "Event", "status": "resolved"},
                {"id": "b", "label": "Actium promontory", "kind": "Place", "status": "provisional"},
                {"id": "c", "label": "Antony's land army at Actium", "kind": "Group", "status": "provisional"},
                {"id": "d", "label": "Ionian Sea", "kind": "Place", "status": "proposed"}]
        ranked = suggest_concerns(note, rows)
        self.assertEqual([r["id"] for r in ranked], ["b", "a", "c"])
        self.assertTrue(ranked[0]["whole"])
        self.assertEqual(ranked[2]["matched"], ["antony", "army", "actium"])

    def test_templates_are_skipped(self):
        self.assertNotIn("note", notes_in(self.folder))
        self.assertIn("Other", notes_in(self.folder))

    def test_frontmatter_that_is_not_there_or_does_not_parse(self):
        with self.assertRaises(NoteError):
            read_note(self.write("Plain", "chrystallum: note\nid:\n"))
        with self.assertRaises(NoteError):
            read_note(self.write("Tabs", "---\nconcerns:\n\t- chr:entity:a-battle\n---\n"))

    def test_the_mistakes_met_in_practice(self):
        found = "\n".join(self.problems(BOOK
            .replace("chapter: Prologue", "Chapter: Prologue")
            .replace("chr:entity:a-battle", "chr:entity:a-Battle")
            .replace('"978-0-306-40615-7"', "'\"978-0-306-40615-8\"'")
            .replace("[[Other]]", "[[Renamed]]")
            .replace("its second line.", "its second line.\n\nYour own thoughts, if any.")))
        for expected in ("['Chapter']", "a-Battle is not in the graph (ids are lowercase)", "fails its check digit",
                         "quote marks", "[[Renamed]] is no note", "placeholder"):
            self.assertIn(expected, found)

    def test_a_note_says_what_it_is_and_has_what_it_needs(self):
        self.assertIn("no quote block", "\n".join(self.problems(BOOK.split("> [!quote]")[0])))
        self.assertIn("no text of the curator's", "\n".join(self.problems(BOOK.replace("excerpt", "interpretation"))))
        self.assertIn("is not in the folder", "\n".join(self.problems(IMAGE.replace("picture.png", "missing.png"), "Image")))
        self.assertIn("depicts is empty", "\n".join(self.problems(IMAGE.replace('"A reconstruction of a monument"', '""'), "Image")))

    def test_the_book_found_by_its_isbn(self):
        without_work = BOOK.replace("work: chr:entity:a-book\n", "")
        with mock.patch.object(notes_module, "lccn_for_isbn", return_value=["2099000001"]):
            self.assertEqual(self.problems(without_work), [])
        with mock.patch.object(notes_module, "lccn_for_isbn", return_value=[]):
            self.assertIn("no preserved LC record", "\n".join(self.problems(without_work)))

    def test_only_the_empty_id_line_changes(self):
        path = self.write("Note", BOOK)
        write_back_id(path, "chr:annotation:0123456789abcdef")
        after = path.read_text(encoding="utf-8")
        self.assertEqual(after, BOOK.replace("id:\n", "id: chr:annotation:0123456789abcdef\n", 1))
        write_back_id(path, "chr:annotation:ffffffffffffffff")  # an id already written is never replaced
        self.assertEqual(path.read_text(encoding="utf-8"), after)


if __name__ == "__main__":
    unittest.main()
