"""Library subject headings: labels come from the authority's record, codes are never shown alone."""

import os
import unittest

from GraphRevised.adapters.library_headings import (
    SOURCE_DIRECTORY, HeadingError, display, fast_label, lcsh_label, preserved_heading,
)
from GraphRevised.operations import RefusedWrite, load_operations, run_write

LCSH_PAYLOAD = SOURCE_DIRECTORY / "lcsh-sh85000736.json"
FAST_PAYLOAD = SOURCE_DIRECTORY / "fast-796265.rdf.xml"


class HeadingTests(unittest.TestCase):
    def test_labels_are_read_from_the_preserved_records(self):
        self.assertEqual(lcsh_label(LCSH_PAYLOAD.read_bytes(), "sh85000736"), "Actium, Battle of, 31 B.C.")
        self.assertEqual(fast_label(FAST_PAYLOAD.read_bytes(), "796265"), "Battle of Actium (31 B.C.)")

    def test_a_record_without_the_heading_has_no_label(self):
        with self.assertRaises(HeadingError):
            lcsh_label(LCSH_PAYLOAD.read_bytes(), "sh00000001")
        with self.assertRaises(HeadingError):
            fast_label(FAST_PAYLOAD.read_bytes(), "fst00796265")  # the deprecated form is not the record

    def test_preserved_records_are_reused_and_malformed_codes_refused(self):
        path, metadata = preserved_heading("FAST", "796265")  # no network: the record is preserved
        self.assertEqual(path, FAST_PAYLOAD)
        self.assertIn("ODC-By", metadata["license"])
        for system, identifier in (("FAST", "fst00796265"), ("LCSH", "85000736"), ("LCC", "DG268")):
            with self.assertRaises(HeadingError):
                preserved_heading(system, identifier)

    def test_a_code_is_shown_after_its_words(self):
        self.assertEqual(display("FAST", "796265", "Battle of Actium (31 B.C.)"),
                         "Battle of Actium (31 B.C.) (FAST 796265)")


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class SubjectAuthorityLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.operations = load_operations()
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
        self.tx.run("CREATE (:Subject {id: 'chr:subject:test-heading', label: 'Test subject', status: 'provisional'})")

    def tearDown(self):
        self.tx.rollback()

    def attach(self, **overrides):
        params = {"subjectId": "chr:subject:test-heading", "id": "chr:authority:lcsh:sh0000000001",
                  "system": "LCSH", "identifier": "sh0000000001", "label": "LCSH heading: Test (LCSH sh0000000001)",
                  "shortLabel": "Test (LCSH sh0000000001)", "description": None, "retrievedAt": None,
                  "sourceUri": None, "contentHash": None, "rawPayloadUri": None, "license": None,
                  "role": "subject_access", "relation": "closeMatch", "linkStatus": "accepted", **overrides}
        return run_write(self.tx, self.operations, "upsert_subject_authority", params)

    def test_a_heading_attaches_once_and_needs_its_label(self):
        self.attach()
        self.attach()  # a retry
        links = self.tx.run("MATCH (:Subject {id: 'chr:subject:test-heading'})-[l:HAS_AUTHORITY_RECORD]->(r) "
                            "RETURN l.role AS role, r.shortLabel AS shown").data()
        self.assertEqual(links, [{"role": "subject_access", "shown": "Test (LCSH sh0000000001)"}])
        with self.assertRaises(RefusedWrite):
            self.attach(id="chr:authority:lcsh:other")  # the same heading under another local ID
        with self.assertRaises(RefusedWrite):
            self.attach(identifier="sh0000000002", id="chr:authority:lcsh:sh0000000002", label=None)
        with self.assertRaises(RefusedWrite):
            self.attach(subjectId="chr:subject:missing")


if __name__ == "__main__":
    unittest.main()
