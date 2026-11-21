"""The rests-on check (D-169): a model's verdicts, verified in code, stored as a Proposal (live, rolled back)."""

import os
import unittest

from GraphRevised.operations import RefusedWrite, load_operations, run_write
from GraphRevised.proposals.rests_on_check import (HARVEST, RULE_BY, ClaimCheck, PassageVerdict, check_request,
                                                   checked, claims, decide, proposal_for, store)
from GraphRevised.proposals.store import ReviewError
from GraphRevised import localdb

CLAIM, WORK, SOURCE = "chr:assertion:test-check-claim", "chr:entity:test-check-work", "chr:entity:test-check-wiki"
P1, P2 = "chr:observation:test-check-65.2", "chr:observation:test-check-65.3"
TEXT1 = "Then Caesar posted Agrippa on the left, and himself took the right."
TEXT2 = "Antony's ships were heavy and slow, built more for show than for battle."
AT = "2026-11-21T00:00:00Z"


def claim_row():
    return {"claim": CLAIM, "label": "According to the test wiki: Agrippa commanded the left wing",
            "links": [{"id": P1, "ref": "Test 65.2", "text": TEXT1, "work": "Test Life", "citation": "Test 65",
                       "quotation": "Agrippa, commanding the left wing", "checked": False},
                      {"id": P2, "ref": "Test 65.3", "text": TEXT2, "work": "Test Life", "citation": "Test 65",
                       "quotation": "Agrippa, commanding the left wing", "checked": False}]}


def output(v1="states", w1="Caesar posted Agrippa on the left", v2="absent", w2=""):
    return ClaimCheck(passages=[PassageVerdict(passage="P1", verdict=v1, words=w1, reason="It says so."),
                                PassageVerdict(passage="P2", verdict=v2, words=w2, reason="It is about ships.")],
                      together="states", reason="65.2 states it; 65.3 is about the ships.")


class OfflineCheckTests(unittest.TestCase):
    def test_the_request_tags_every_passage_and_names_the_citation(self):
        request = check_request("claude-sonnet-5-5", claim_row())
        user = request["messages"][0]["content"]
        self.assertIn("[P1] Test 65.2", user)
        self.assertIn("[P2] Test 65.3", user)
        self.assertIn("Its footnote cites: Test 65", user)
        self.assertIs(request["output_format"], ClaimCheck)

    def test_words_are_verified_verbatim(self):
        rows, problems = checked(output(), claim_row())
        self.assertEqual(problems, [])
        self.assertTrue(rows[0]["verified"])
        self.assertIsNone(rows[1]["words"])
        rows, _ = checked(output(w1="Caesar put Agrippa on the left"), claim_row())
        self.assertFalse(rows[0]["verified"], "paraphrased words are not verified")
        rows, _ = checked(output(w1="Caesar posted ... the left"), claim_row())
        self.assertFalse(rows[0]["verified"], "an ellipsis is never verified")

    def test_a_skipped_or_doubled_passage_is_a_problem(self):
        skipped = ClaimCheck(passages=[PassageVerdict(passage="P1", verdict="states", words="Caesar posted Agrippa",
                                                      reason="r")], together="states", reason="r")
        self.assertEqual(checked(skipped, claim_row())[1], ["P2 not judged"])
        unknown = ClaimCheck(passages=output().passages + [PassageVerdict(passage="P9", verdict="absent", reason="r")],
                             together="states", reason="r")
        self.assertIn("unknown passage tag 'P9'", checked(unknown, claim_row())[1])

    def test_only_a_fully_confirmed_check_is_accepted_by_rule(self):
        rows, _ = checked(output(), claim_row())
        mixed = proposal_for(claim_row(), rows, output(), model_id="m", at=AT, registry_version="v20")
        self.assertEqual(mixed["status"], "submitted")
        self.assertIsNone(mixed["decidedBy"])
        both = output(v2="states", w2="Antony's ships were heavy")
        rows, _ = checked(both, claim_row())
        confirmed = proposal_for(claim_row(), rows, both, model_id="m", at=AT, registry_version="v20")
        self.assertEqual((confirmed["status"], confirmed["decidedBy"], confirmed["verdict"]),
                         ("accepted", RULE_BY, "confirmed"))
        unverified = output(v2="states", w2="ships that were slow")
        rows, _ = checked(unverified, claim_row())
        self.assertEqual(proposal_for(claim_row(), rows, unverified, model_id="m", at=AT,
                                      registry_version="v20")["status"], "submitted")


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "needs the local Neo4j")
class CheckLiveTests(unittest.TestCase):
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
        self.tx = self.session.begin_transaction()
        for id_, label in ((WORK, "Test Life"), (SOURCE, "Test wiki")):
            run_write(self.tx, self.operations, "upsert_entity", {"id": id_, "kind": "Work", "label": label,
                                                                  "description": None, "status": "proposed",
                                                                  "shortLabel": None})
        self.tx.run("""MATCH (w:Entity {id: $work}), (s:Entity {id: $source})
                       CREATE (a:Assertion {id: $claim, predicate: 'commanded', label: 'test claim', status: 'proposed',
                               category: 'factual', assertedBy: 'test'})-[:ATTRIBUTED_TO]->(s)
                       WITH a, w
                       UNWIND [[$p1, 'Test 65.2', $t1], [$p2, 'Test 65.3', $t2]] AS p
                       CREATE (o:SourceObservation {id: p[0], label: p[1], shortLabel: p[1], status: 'observed',
                               sourceSystem: 'test', retrievedAt: $at, contentHash: 'x', passageText: p[2]})-[:IN_WORK]->(w)
                       CREATE (a)-[:RESTS_ON {status: 'accepted', createdBy: $by, createdAt: $at, citation: 'Test 65',
                               quotation: 'Agrippa, commanding the left wing'}]->(o)""",
                    work=WORK, source=SOURCE, claim=CLAIM, p1=P1, p2=P2, t1=TEXT1, t2=TEXT2, at=AT, by=HARVEST)

    def tearDown(self):
        self.tx.rollback()

    def proposal(self, out, recheck=False):
        row = claims(self.tx, CLAIM, recheck=recheck)[0]
        rows, problems = checked(out, row)
        self.assertEqual(problems, [])
        return proposal_for(row, rows, out, model_id="m", at=AT, registry_version="v20")

    def links(self):
        return {r["o"]: r for r in self.tx.run(
            "MATCH (:Assertion {id: $c})-[l:RESTS_ON]->(o) RETURN o.id AS o, l.status AS status, l.check AS check, "
            "l.support AS support, l.checkProposal AS proposal", c=CLAIM).data()}

    def test_claims_reads_the_links_in_order_and_skips_checked_ones(self):
        row = claims(self.tx, CLAIM)[0]
        self.assertEqual([l["id"] for l in row["links"]], [P1, P2])
        store(self.tx, self.operations, self.proposal(output()))
        self.assertEqual(claims(self.tx, CLAIM), [])

    def test_a_mixed_check_waits_then_accepting_it_rejects_the_absent_link(self):
        proposal = self.proposal(output())
        stored = store(self.tx, self.operations, proposal)
        self.assertEqual((stored["status"], stored["passages"]), ("submitted", 2))
        links = self.links()
        self.assertEqual((links[P1]["check"], links[P2]["check"]), ("states", "absent"))
        self.assertEqual(links[P2]["status"], "accepted", "nothing changes before the curator decides")
        decided = decide(self.tx, self.operations, proposal["id"], "accepted", decided_by="test curator",
                         decision_basis="test", decided_at=AT)
        self.assertEqual(decided["applied"], 1)
        links = self.links()
        self.assertEqual((links[P1]["status"], links[P2]["status"]), ("accepted", "rejected"))
        again = decide(self.tx, self.operations, proposal["id"], "accepted", decided_by="test curator",
                       decision_basis="test", decided_at=AT)
        self.assertEqual(again["applied"], 0, "a retry is a no-op")

    def test_rejecting_a_check_leaves_the_links_and_partial_is_marked_on_accept(self):
        proposal = self.proposal(output(v2="partly", w2="Antony's ships were heavy"))
        store(self.tx, self.operations, proposal)
        with self.assertRaises(ReviewError):
            decide(self.tx, self.operations, proposal["id"], "rejected", decided_by="t", decision_basis="t",
                   decided_at=AT, reason="not-a-code")
        decide(self.tx, self.operations, proposal["id"], "accepted", decided_by="t", decision_basis="t", decided_at=AT)
        self.assertEqual(self.links()[P2]["support"], "partial")
        self.assertEqual(self.links()[P2]["status"], "accepted")

    def test_a_confirmed_check_is_accepted_and_cannot_be_decided_again(self):
        both = output(v2="states", w2="Antony's ships were heavy")
        proposal = self.proposal(both)
        self.assertEqual(store(self.tx, self.operations, proposal)["status"], "accepted")
        with self.assertRaises(ReviewError):
            decide(self.tx, self.operations, proposal["id"], "rejected", decided_by="t", decision_basis="t",
                   decided_at=AT, reason="false")

    def test_a_check_with_a_newer_prompt_supersedes_the_open_one(self):
        old = {**self.proposal(output()), "id": "chr:proposal:check:test-old", "promptVersion": "rests-on-check-v0-old"}
        store(self.tx, self.operations, old)
        self.assertEqual(claims(self.tx, CLAIM), [], "checked once")
        self.assertEqual(len(claims(self.tx, CLAIM, recheck=True)), 1, "an open check from another prompt is redone")
        new = self.proposal(output(v2="partly", w2="Antony's ships were heavy"), recheck=True)
        store(self.tx, self.operations, new)
        status = self.tx.run("MATCH (p:Proposal {id: $id}) RETURN p.status AS s, p.decisionReason AS r",
                             id=old["id"]).single()
        self.assertEqual((status["s"], status["r"]), ("rejected", "superseded-by-model"))
        self.assertEqual((self.links()[P2]["check"], self.links()[P2]["proposal"]), ("partly", new["id"]))
        self.assertEqual(claims(self.tx, CLAIM, recheck=True), [], "the current prompt's check is not redone")

    def test_a_passage_the_claim_does_not_rest_on_is_refused(self):
        proposal = self.proposal(output())
        proposal["checks"][1]["observationId"] = "chr:observation:not-linked"
        with self.assertRaises(RefusedWrite):
            store(self.tx, self.operations, proposal)


if __name__ == "__main__":
    unittest.main()
