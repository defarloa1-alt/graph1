"""The source registry's shape (curation/sources.json), without the network."""

import inspect
import json
import unittest
from pathlib import Path

from GraphRevised.adapters import sources

REGISTRY = json.loads((Path(__file__).resolve().parents[1] / "curation" / "sources.json").read_text(encoding="utf-8"))


class SourceRegistryTests(unittest.TestCase):
    def test_ids_are_unique(self):
        ids = [s["id"] for s in REGISTRY["sources"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_statuses_and_classes_are_defined(self):
        for source in REGISTRY["sources"]:
            with self.subTest(source=source["id"]):
                self.assertIn(source["status"], REGISTRY["statuses"])
                for part in source["rights"]["class"].split("/"):
                    self.assertIn(part, REGISTRY["rightsClasses"])

    def test_checked_rights_are_quoted_with_where_and_when(self):
        for source in REGISTRY["sources"]:
            if source["status"] == "candidate":
                continue
            with self.subTest(source=source["id"]):
                rights = source["rights"]
                self.assertTrue(rights["statement"])
                self.assertTrue(rights["statementUri"].startswith("https://"))
                self.assertRegex(rights["checkedAt"], r"^\d{4}-\d{2}-\d{2}$")

    def test_a_source_read_has_an_adapter_the_interface_knows(self):
        known = inspect.getsource(sources.open_source)
        for source in REGISTRY["sources"]:
            with self.subTest(source=source["id"]):
                if source["status"] == "read":
                    self.assertIn(f'"{source["adapter"]["type"]}"', known)
                    self.assertTrue((Path(sources.__file__).parents[1] / source["adapter"]["module"]).exists())


if __name__ == "__main__":
    unittest.main()
