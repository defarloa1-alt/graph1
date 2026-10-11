"""Live Phase 5 replay tests. Every test is rolled back; the database never changes."""

import os
import unittest
from pathlib import Path

from GraphRevised.adapters.wikidata_statements import statement_observation
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft
from GraphRevised.proposals.store import Neo4jReader, ReviewError, accept, list_proposals, reject, submit
from GraphRevised.proposals.validator import Outcome
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation

PAYLOAD = Path(__file__).resolve().parents[1] / "phase-2-source" / "wikidata-Q160387-r2555342002.json"
ACTIUM = "chr:entity:battle-of-actium"
AGRIPPA_OBSERVATION = "chr:observation:wikidata:Q160387:P710:32bdfa2f:r2555342002"
OCTAVIAN = "chr:entity:augustus"
OCTAVIAN_STATEMENT = "Q160387$d9469717-433b-c369-9fc7-3d7d5bf2b969"
DECISION = {"decided_by": "test-curator", "decision_basis": "test", "decided_at": "2026-10-11T00:00:00Z"}

COUNTS = "CALL () { MATCH (n) RETURN count(n) AS nodes } CALL () { MATCH ()-[r]->() RETURN count(r) AS rels } RETURN nodes, rels"


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class ProposalWorkflowLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.operations = load_operations()
        cls.registry = load_registry()
        cls.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        )
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()
        self.reader = Neo4jReader(self.tx)

    def tearDown(self):
        self.tx.rollback()

    def counts(self):
        return self.tx.run(COUNTS).single().data()

    def add_octavian(self):
        """Reviewed identity setup a curator would do before proposals can name Octavian."""
        run_write(self.tx, self.operations, "upsert_entity", {
            "id": OCTAVIAN, "kind": "Person", "label": "Augustus", "description": None,
            "status": "provisional", "shortLabel": "Octavian",
        })
        run_write(self.tx, self.operations, "upsert_authority", {
            "entityId": OCTAVIAN, "id": "chr:authority:wikidata:Q1405", "system": "Wikidata",
            "identifier": "Q1405", "label": "Wikidata record: Augustus (Q1405)", "shortLabel": "Wikidata: Augustus",
            "description": None, "retrievedAt": None, "role": "entity_identity",
            "relation": "closeMatch", "linkStatus": "accepted",
        })
        params = statement_observation(
            PAYLOAD, OCTAVIAN_STATEMENT,
            label="Wikidata observation: Augustus participated in Battle of Actium",
            short_label="Wikidata: Octavian -> Actium",
        )
        run_write(self.tx, self.operations, "upsert_observation", params)
        return params["id"]

    def octavian_draft(self):
        observation = self.reader.observation(self.add_octavian())
        result = drafts_from_observation(observation, self.reader, self.registry)
        self.assertEqual(result.unresolved, ())
        self.assertEqual(len(result.drafts), 1)
        return result.drafts[0]

    def test_replaying_actium_observation_is_an_already_supported_duplicate(self):
        before = self.counts()
        observation = self.reader.observation(AGRIPPA_OBSERVATION)
        result = drafts_from_observation(observation, self.reader, self.registry)
        submission = submit(self.tx, result.drafts[0], self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.DUPLICATE)
        self.assertTrue(submission.validation.already_supported)
        self.assertFalse(submission.stored)
        self.assertEqual(self.counts(), before)

    def test_unlinked_participants_are_reported_not_created(self):
        before = self.counts()
        params = statement_observation(
            PAYLOAD, OCTAVIAN_STATEMENT, label="x", short_label="x",
        )
        result = drafts_from_observation(params, self.reader, self.registry)
        self.assertEqual(result.drafts, ())
        self.assertEqual(result.unresolved, ("Q1405 has no local Entity",))
        self.assertEqual(self.counts(), before)

    def test_octavian_proposal_full_workflow(self):
        draft = self.octavian_draft()
        submission = submit(self.tx, draft, self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.VALID)
        self.assertTrue(submission.stored)
        proposal_id = submission.validation.proposal_id

        stored = self.tx.run(
            "MATCH (p:Proposal {id: $id})-[:PROPOSES]->(a:Assertion) RETURN p, a", id=proposal_id
        ).single()
        self.assertEqual(stored["p"]["status"], "submitted")
        self.assertEqual(stored["p"]["predicateRegistryVersion"], "predicates-v1")
        self.assertEqual(stored["a"]["status"], "proposed")
        self.assertEqual(stored["a"]["label"], "Augustus participated in Battle of Actium")
        self.assertIn(proposal_id, [row["id"] for row in list_proposals(self.tx, "submitted")])

        before_retry = self.counts()
        retry = submit(self.tx, draft, self.registry, self.operations)
        self.assertEqual(retry.validation.outcome, Outcome.DUPLICATE)
        self.assertEqual(self.counts(), before_retry)

        decided = accept(self.tx, proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        self.assertEqual(decided["proposal"]["status"], "accepted")
        self.assertEqual(decided["assertion"]["status"], "accepted")
        context = self.tx.run(
            self.operations["get_temporal_context"], assertionId=submission.validation.assertion_id
        ).single()
        self.assertEqual(context["temporalContext"], "Battle of Actium, 31 BCE")

        with self.assertRaises(ReviewError):
            accept(self.tx, proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        with self.assertRaises(ReviewError):
            reject(self.tx, proposal_id, operations=self.operations, **DECISION)

    def test_rejection_marks_assertion_rejected(self):
        submission = submit(self.tx, self.octavian_draft(), self.registry, self.operations)
        decided = reject(self.tx, submission.validation.proposal_id, operations=self.operations, **DECISION)
        self.assertEqual(decided["proposal"]["status"], "rejected")
        self.assertEqual(decided["assertion"]["status"], "rejected")

    def test_invented_evidence_is_refused_and_nothing_is_stored(self):
        self.add_octavian()
        before = self.counts()
        invented = ProposalDraft(
            predicate="participatedIn",
            subject_id=OCTAVIAN,
            object_id=ACTIUM,
            observation_ids=(AGRIPPA_OBSERVATION,),
            rationale="cites Agrippa's statement as if it were Octavian's",
            proposed_by="test",
        )
        submission = submit(self.tx, invented, self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.INVALID)
        self.assertFalse(submission.stored)
        self.assertEqual(self.counts(), before)


if __name__ == "__main__":
    unittest.main()
