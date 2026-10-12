"""Related claims in the check, and local candidates before an entity is created."""

import os
import unittest

from GraphRevised.identity.local_candidates import candidates, similarity
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation
from GraphRevised.proposals.validator import classify_related

BASE = "chr:assertion:a:commanded:b"


class StubReader:
    def __init__(self, rows):
        self.rows = rows

    def related_assertions(self, base_id):
        return [row for row in self.rows if row["id"] == base_id or row["id"].startswith(base_id + ":q")]


def draft(**extra):
    return ProposalDraft(predicate="commanded", subject_id="chr:entity:a", object_id="chr:entity:b",
                         observation_ids=("chr:observation:x",), rationale="classification test", proposed_by="test",
                         **extra)


ROLE = {"role_id": "chr:entity:legatus", "qualifier_quotations": (
    QualifierQuotation(observation_id="chr:observation:x", supports="role", text="as legate"),)}


def row(suffix="", status="accepted", mode=None, context=None, role=None, time=None, work=None):
    return {"id": BASE + suffix, "status": status, "mode": mode, "attributedTo": work, "context": context,
            "role": role, "time": time}


class RelatedClaimTests(unittest.TestCase):
    def relations(self, proposal, rows, own):
        return {item["id"]: item["relation"] for item in classify_related(proposal, StubReader(rows), BASE, own)}

    def test_relations(self):
        rows = [
            row(),  # coarse, asserted
            row(":q1111111111", mode="attributed", work="w2"),  # same content, another source
            row(":q2222222222", role="chr:entity:consul"),  # another role
            row(":q3333333333", role="chr:entity:legatus", time="-0030"),  # finer than the draft
        ]
        attributed = draft(mode="attributed", attributed_to="chr:entity:w1")
        self.assertEqual(self.relations(attributed, rows, BASE + ":qown"), {
            BASE: "parallel", BASE + ":q1111111111": "parallel",
            BASE + ":q2222222222": "refined-by", BASE + ":q3333333333": "refined-by"})
        with_role = draft(**ROLE)
        self.assertEqual(self.relations(with_role, rows, BASE + ":qown"), {
            BASE: "refines", BASE + ":q1111111111": "refines",
            BASE + ":q2222222222": "conflicts", BASE + ":q3333333333": "refined-by"})

    def test_a_claim_is_not_related_to_itself_and_readers_may_lack_the_lookup(self):
        self.assertEqual(classify_related(draft(), StubReader([row()]), BASE, BASE), [])
        self.assertEqual(classify_related(draft(), object(), BASE, BASE), [])


class SimilarityTests(unittest.TestCase):
    def test_scores(self):
        self.assertEqual(similarity("Decisive battle", "decisive  battle"), 1.0)
        self.assertEqual(similarity("unconventional war", "conventional versus unconventional war"), 0.8)
        self.assertLess(similarity("Battle of Actium", "Battle of Philippi"), 0.5)
        self.assertEqual(similarity("", "x"), 0.0)


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class LiveTests(unittest.TestCase):
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

    def test_local_candidates_find_near_synonyms_of_the_same_kind(self):
        for entity_id, kind in (("chr:entity:test-concept-a", "Concept"), ("chr:entity:test-person-a", "Person")):
            run_write(self.tx, self.operations, "upsert_entity", {
                "id": entity_id, "kind": kind, "label": "Test fleet-in-being strategy", "description": None,
                "status": "provisional", "shortLabel": None})
        found = candidates(self.tx, "test fleet in being strategy", "Concept")
        self.assertEqual([item["id"] for item in found], ["chr:entity:test-concept-a"])
        self.assertEqual(candidates(self.tx, "test fleet in being strategy", "Concept",
                                    exclude="chr:entity:test-concept-a"), [])

    def test_related_claims_are_reported_by_the_live_reader(self):
        from GraphRevised.proposals.store import Neo4jReader

        rows = Neo4jReader(self.tx).related_assertions("chr:assertion:no-such:claim:here")
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
