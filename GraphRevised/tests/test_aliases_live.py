"""addAlias (46 §4.5): suggested by reasoning, guarded, decided by the curator (live, rolled back)."""

import os
import unittest

from GraphRevised.operations import RefusedWrite, load_operations, run_write
from GraphRevised.proposals.aliases import conventional_forms, decide, parts_from_heading, propose, suggest
from GraphRevised.proposals.store import ReviewError

COMMANDER, HEIR, OTHER = "chr:entity:test-alias-commander", "chr:entity:test-alias-heir", "chr:entity:test-alias-other"
QUESTION, PASSAGE = "chr:entity:test-alias-question", "chr:observation:test-alias-passage"
AT = "2026-11-19T00:00:00Z"


class OfflineAliasTests(unittest.TestCase):
    def test_a_heading_gives_the_name_parts(self):
        self.assertEqual(parts_from_heading("SCARPUS, L. PINA'RIUS"),
                         {"praenomen": "Lucius", "nomen": "Pinarius", "cognomen": "Scarpus", "agnomen": None})
        with self.assertRaises(ValueError):
            parts_from_heading("Scarpus")

    def test_the_conventional_forms(self):
        forms = [f for f, _ in conventional_forms({"praenomen": "Lucius", "nomen": "Pinarius", "cognomen": "Scarpus"})]
        self.assertEqual(forms, ["L. Pinarius Scarpus", "Pinarius Scarpus", "Scarpus", "Lucius Pinarius"])


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "needs the local Neo4j")
class AliasLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase
        cls.operations = load_operations()
        cls.driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                          auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                          notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()
        for id_, kind, label, short in ((COMMANDER, "Person", "Lucius Testius Scarpo", "Testius Scarpo"),
                                        (HEIR, "Person", "Lucius Testius", None),
                                        (OTHER, "Person", "Scarpo", None),
                                        (QUESTION, "Question", "Is the heir the commander?", None)):
            run_write(self.tx, self.operations, "upsert_entity", {"id": id_, "kind": kind, "label": label,
                                                                  "description": None, "status": "proposed", "shortLabel": short})
        self.tx.run("""MATCH (c:Entity {id: $c}), (h:Entity {id: $h}), (q:Entity {id: $q})
                       CREATE (o:SourceObservation {id: $o, label: 'test passage', status: 'observed', sourceSystem: 'test',
                               retrievedAt: $at, contentHash: 'x', passageText: 'and the general, L. Testius Scarpo, refused him'})
                       CREATE (a1:Assertion {id: 'chr:assertion:test-alias-1', predicate: 'about', label: 'q about c', status: 'proposed',
                               category: 'interpretive', assertedBy: 'test'})-[:ASSERTION_SUBJECT]->(q)
                       CREATE (a1)-[:ASSERTION_OBJECT]->(c)
                       CREATE (a1)-[:SUPPORTED_BY]->(o)
                       CREATE (a2:Assertion {id: 'chr:assertion:test-alias-2', predicate: 'about', label: 'q about h', status: 'proposed',
                               category: 'interpretive', assertedBy: 'test'})-[:ASSERTION_SUBJECT]->(q)
                       CREATE (a2)-[:ASSERTION_OBJECT]->(h)""",
                    c=COMMANDER, h=HEIR, q=QUESTION, o=PASSAGE, at=AT)
        self.tx.run("MATCH (e:Entity {id: $id}) SET e.praenomen = 'Lucius', e.nomen = 'Testius', e.cognomen = 'Scarpo'",
                    id=COMMANDER)

    def tearDown(self):
        self.tx.rollback()

    def suggestions(self):
        return {item["alias"]: item for item in suggest(self.tx, COMMANDER)}

    def test_forms_are_attested_shared_or_refused(self):
        items = self.suggestions()
        self.assertNotIn("Testius Scarpo", items)  # already the short label
        self.assertEqual(items["L. Testius Scarpo"]["kind"], "attested")
        self.assertEqual(items["L. Testius Scarpo"]["evidence"][0], PASSAGE)
        self.assertEqual(items["Scarpo"]["kind"], "attested")  # inside "L. Testius Scarpo, refused"
        self.assertEqual(items["Scarpo"]["sharedWith"], [OTHER])  # shown with its bearer, not refused
        self.assertNotIn("refused", items["Scarpo"])
        self.assertIn("open Question", items["Lucius Testius"]["refused"])  # the heir's name
        with self.assertRaises(ReviewError):
            propose(self.tx, self.operations, "test", COMMANDER, items["Lucius Testius"], proposed_by="test", at=AT)

    def test_only_the_curator_adds_an_alias(self):
        item = self.suggestions()["L. Testius Scarpo"]
        proposal = propose(self.tx, self.operations, "test", COMMANDER, item, proposed_by="test", at=AT)
        self.assertEqual((proposal["status"], proposal["aliasKind"]), ("submitted", "attested"))
        names = lambda: self.tx.run("MATCH (e:Entity {id: $id}) RETURN e.alternativeNames AS n", id=COMMANDER).single()["n"]  # noqa: E731
        self.assertIsNone(names())  # proposed, not yet an alias
        decided = decide(self.tx, self.operations, proposal["id"], "accepted", decided_by="TD", decision_basis="a test",
                         decided_at=AT)
        self.assertEqual(decided["entity"]["alternativeNames"], ["L. Testius Scarpo"])
        self.assertNotIn("L. Testius Scarpo", self.suggestions())  # now known
        with self.assertRaises(RefusedWrite):  # the Entity bears it now
            propose(self.tx, self.operations, "test", COMMANDER, item, proposed_by="test", at=AT)

    def test_a_rejection_needs_a_reason(self):
        proposal = propose(self.tx, self.operations, "test", COMMANDER, self.suggestions()["Scarpo"], proposed_by="test", at=AT)
        with self.assertRaises(ReviewError):
            decide(self.tx, self.operations, proposal["id"], "rejected", decided_by="TD", decision_basis="x", decided_at=AT)
        decided = decide(self.tx, self.operations, proposal["id"], "rejected", decided_by="TD", decision_basis="ambiguous",
                         decided_at=AT, reason="underspecified")
        self.assertEqual(decided["proposal"]["status"], "rejected")
        self.assertIsNone(decided["entity"].get("alternativeNames"))


if __name__ == "__main__":
    unittest.main()
