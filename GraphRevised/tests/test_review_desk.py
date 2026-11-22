"""The review desk's reads and decisions (live, rolled back; synthetic fixtures)."""

import os
import unittest

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import ReviewError, submit
from GraphRevised.review_desk.app import claims, decide, detail, entity, find, parts, render_detail, render_entity, table
from GraphRevised import localdb

BATTLE = ("chr:entity:test-desk-battle", "Event", "Test desk battle")
MOMENT = ("chr:entity:test-desk-moment", "Event", "Test desk moment")
LEADER = ("chr:entity:test-desk-leader", "Person", "Test desk leader")
PASSAGE = "chr:observation:test:desk-passage"
TEXT = "In the test desk moment of the battle the leader held the right wing."


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class ReviewDeskLiveTests(unittest.TestCase):
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
        self.addCleanup(self.tx.rollback)
        for entity_id, kind, label in (BATTLE, MOMENT, LEADER):
            run_write(self.tx, self.operations, "upsert_entity", {
                "id": entity_id, "kind": kind, "label": label, "description": None,
                "status": "provisional", "shortLabel": None})
        run_write(self.tx, self.operations, "upsert_passage_observation", {
            "id": PASSAGE, "label": "Test desk passage", "shortLabel": "Desk 1", "sourceSystem": "Test",
            "locator": "test:desk:1", "passageText": TEXT, "passageHash": "test", "editorialNotes": [],
            "language": "en", "workTitle": "Test", "author": "Test", "translator": None, "editionCitation": "Test",
            "rights": "test", "sourceUri": "test", "sourceRevision": "test", "retrievedAt": "2026-11-13T00:00:00Z",
            "contentHash": "test", "rawPayloadUri": None, "status": "observed"})
        self.part = self.propose("partOf", MOMENT[0], BATTLE[0], "test desk moment of the battle")
        self.took_part = self.propose("participatedIn", LEADER[0], MOMENT[0], "the leader held the right wing")

    def propose(self, predicate, subject, obj, quote):
        draft = ProposalDraft(predicate=predicate, subject_id=subject, object_id=obj, observation_ids=(PASSAGE,),
                              quotations=(Quotation(observation_id=PASSAGE, text=quote),),
                              rationale="a synthetic review desk claim", proposed_by="test-desk")
        return submit(self.tx, draft, self.registry, self.operations).validation

    def test_reads_an_entity_its_claims_and_its_parts(self):
        self.assertIn(MOMENT[0], [row["id"] for row in find(self.tx, "test desk moment")])
        rows = claims(self.tx, MOMENT[0])
        self.assertEqual({(r["predicate"], r["otherId"], r["outgoing"]) for r in rows},
                         {("partOf", BATTLE[0], True), ("participatedIn", LEADER[0], False)})
        self.assertTrue(all(len(r["open"]) == 1 for r in rows))
        self.assertEqual(len(table(rows)), 2)
        self.assertIn("2 live claims · 2 open proposals", render_entity(entity(self.tx, MOMENT[0]), rows))
        self.assertEqual([(p["id"], p["open"]) for p in parts(self.tx, BATTLE[0])], [(MOMENT[0], 2)])
        shown = render_detail(detail(self.tx, self.took_part.assertion_id))
        self.assertIn("“the leader held the right wing”", shown)
        self.assertIn(self.took_part.proposal_id, shown)

    def test_accept_then_reject_rebuild_the_fact_layer(self):
        _, counts = decide(self.tx, self.part.proposal_id, "accept", by="test-curator", basis="test")
        self.assertGreater(counts["factEdges"], 0)
        edge = self.tx.run("MATCH (:Entity {id: $s})-[r:PART_OF {derived: 'fact-layer'}]->(:Entity {id: $o}) "
                           "RETURN r.status AS status", s=MOMENT[0], o=BATTLE[0]).single()
        self.assertEqual(edge["status"], "accepted")

        decide(self.tx, self.took_part.proposal_id, "reject", by="test-curator", basis="test",
               reason="unsupported", reject_claim=True)
        gone = self.tx.run("MATCH (:Entity {id: $s})-[r:PARTICIPATED_IN {derived: 'fact-layer'}]->() RETURN count(r) AS n",
                           s=LEADER[0]).single()["n"]
        self.assertEqual(gone, 0)
        self.assertEqual(parts(self.tx, BATTLE[0])[0]["open"], 0)

    def test_a_decision_needs_who_and_why(self):
        with self.assertRaises(ReviewError):
            decide(self.tx, self.part.proposal_id, "accept", by="", basis="test")
        with self.assertRaises(ReviewError):
            decide(self.tx, self.part.proposal_id, "reject", by="test-curator", basis="test", reason="nope")


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class FootnoteCheckTabTests(unittest.TestCase):
    """The Footnote checks tab reads a stored check and decides it as the command line does."""

    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.operations = load_operations()
        cls.driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=localdb.database())

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        from GraphRevised.proposals.rests_on_check import (HARVEST, ClaimCheck, PassageVerdict, checked, proposal_for,
                                                           store)
        from GraphRevised.proposals import rests_on_check

        self.tx = self.session.begin_transaction()
        self.addCleanup(self.tx.rollback)
        claim, p1, p2 = "chr:assertion:test-desk-check", "chr:observation:test-desk-check-1", "chr:observation:test-desk-check-2"
        self.claim, self.p1, self.p2 = claim, p1, p2
        for id_, label in (("chr:entity:test-desk-check-work", "Test Life"), ("chr:entity:test-desk-check-wiki", "Test wiki")):
            run_write(self.tx, self.operations, "upsert_entity", {"id": id_, "kind": "Work", "label": label,
                                                                  "description": None, "status": "proposed",
                                                                  "shortLabel": None})
        self.tx.run("""MATCH (w:Entity {id: 'chr:entity:test-desk-check-work'}), (s:Entity {id: 'chr:entity:test-desk-check-wiki'})
                       CREATE (a:Assertion {id: $claim, predicate: 'commanded', label: 'Test desk check claim',
                               status: 'proposed', category: 'factual', assertedBy: 'test'})-[:ATTRIBUTED_TO]->(s)
                       WITH a, w
                       UNWIND [[$p1, 'Desk 65.2', 'Then Caesar posted Agrippa on the left.'],
                               [$p2, 'Desk 65.3', 'The ships were heavy and slow.']] AS p
                       CREATE (o:SourceObservation {id: p[0], label: p[1], shortLabel: p[1], status: 'observed',
                               sourceSystem: 'test', retrievedAt: '2026-11-21T00:00:00Z', contentHash: 'x',
                               passageText: p[2]})-[:IN_WORK]->(w)
                       CREATE (a)-[:RESTS_ON {status: 'accepted', createdBy: $by, createdAt: '2026-11-21T00:00:00Z',
                               citation: 'Desk 65', quotation: 'Agrippa, commanding the left wing'}]->(o)""",
                    claim=claim, p1=p1, p2=p2, by=HARVEST)
        row = rests_on_check.claims(self.tx, claim)[0]
        out = ClaimCheck(passages=[PassageVerdict(passage="P1", verdict="states", words="Caesar posted Agrippa on the left",
                                                  reason="It says so."),
                                   PassageVerdict(passage="P2", verdict="absent", reason="It is about ships.")],
                         together="states", reason="P1 states it; P2 is about the ships.")
        rows, _ = checked(out, row)
        self.proposal_id = store(self.tx, self.operations, proposal_for(
            row, rows, out, model_id="m", at="2026-11-21T00:00:00Z", registry_version="v20"))["id"]

    def link_status(self, observation):
        return self.tx.run("MATCH (:Assertion {id: $c})-[l:RESTS_ON]->(:SourceObservation {id: $o}) RETURN l.status AS s",
                           c=self.claim, o=observation).single()["s"]

    def test_lists_and_shows_a_check_by_verdict(self):
        from GraphRevised.review_desk.app import check_detail, check_table, checks, render_check

        listed = [r for r in checks(self.tx) if r["id"] == self.proposal_id]
        self.assertEqual([(r["states"], r["partly"], r["absent"]) for r in listed], [(1, 0, 1)])
        self.assertEqual(check_table(listed)[0][1:], ["Test desk check claim", 1, 0, 1, "submitted"])
        shown = render_check(check_detail(self.tx, self.proposal_id))
        self.assertLess(shown.index("**States the claim** (1)"), shown.index("**Does not say it** (1)"))
        self.assertIn("“Caesar posted Agrippa on the left”", shown)
        self.assertIn("> Taken together, the cited passages: states. Desk 65.2 states it; Desk 65.3 is about the ships.\n", shown)
        self.assertIn("1 link(s) rejected (kept as history)", shown)
        self.assertIn("footnote cites **Desk 65**", shown)

    def test_accept_applies_the_verdicts_and_reject_needs_a_reason(self):
        from GraphRevised.review_desk.app import check_detail, decide_check, render_check

        with self.assertRaises(ReviewError):
            decide_check(self.tx, self.proposal_id, "accept", by="", basis="test")
        with self.assertRaises(ReviewError):
            decide_check(self.tx, self.proposal_id, "reject", by="test-curator", basis="test", reason="nope")
        row = decide_check(self.tx, self.proposal_id, "accept", by="test-curator", basis="test")
        self.assertEqual((row["status"], row["applied"]), ("accepted", 1))
        self.assertEqual((self.link_status(self.p1), self.link_status(self.p2)), ("accepted", "rejected"))
        self.assertIn("**Decided:** accepted by test-curator", render_check(check_detail(self.tx, self.proposal_id)))

    def test_reject_leaves_every_link(self):
        from GraphRevised.review_desk.app import decide_check

        row = decide_check(self.tx, self.proposal_id, "reject", by="test-curator", basis="test", reason="false")
        self.assertEqual((row["status"], row["applied"]), ("rejected", 0))
        self.assertEqual((self.link_status(self.p1), self.link_status(self.p2)), ("accepted", "accepted"))


if __name__ == "__main__":
    unittest.main()
