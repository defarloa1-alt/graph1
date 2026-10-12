"""Live Phase 5 workflow tests. Every test is rolled back; the database never changes.

The workflow tests build synthetic fixtures (test entities, made-up QIDs, a
test passage) inside their transaction, so they do not depend on what the
live graph currently contains. Only the Actium replay uses real data.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.passage_reader import load_inquiry
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import (
    Neo4jReader, ReviewError, accept, list_proposals, reject, reopen, submit, supersede,
)
from GraphRevised.proposals.validator import Outcome
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation

AGRIPPA_OBSERVATION = "chr:observation:wikidata:Q160387:P710:32bdfa2f:r2555342002"

BATTLE = ("chr:entity:test-battle", "Event", "Test battle", "Q999990001")
LEADER = ("chr:entity:test-leader", "Person", "Test leader", "Q999990002")
ADMIRAL = ("chr:entity:test-admiral", "Person", "Test admiral", "Q999990003")
UNLINKED_QID = "Q999990009"
PASSAGE_ID = "chr:observation:test:passage"
PASSAGE_TEXT = (
    "On the fifth day they came to an engagement. The leader had the right wing, "
    "and the admiral was extending the left wing to encircle the enemy."
)
DECISION = {"decided_by": "test-curator", "decision_basis": "test", "decided_at": "2026-10-11T00:00:00Z"}
REJECTION = {**DECISION, "reason": "unsupported"}

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
            notifications_min_severity="OFF",
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

    # -- fixtures -------------------------------------------------------------

    def counts(self):
        return self.tx.run(COUNTS).single().data()

    def write(self, operation, params):
        return run_write(self.tx, self.operations, operation, params)

    def add_entity(self, entity):
        entity_id, kind, label, qid = entity
        self.write("upsert_entity", {
            "id": entity_id, "kind": kind, "label": label, "description": None,
            "status": "provisional", "shortLabel": None,
        })
        self.write("upsert_authority", {
            "entityId": entity_id, "id": f"chr:authority:wikidata:{qid}", "system": "Wikidata",
            "identifier": qid, "label": f"Wikidata record: {label} ({qid})", "shortLabel": None,
            "description": None, "retrievedAt": None, "sourceUri": None, "sourceRevision": None,
            "contentHash": None, "rawPayloadUri": None, "role": "entity_identity",
            "relation": "closeMatch", "linkStatus": "accepted",
        })

    def statement(self, participant_qid, *, persist=True):
        """A synthetic Wikidata P710 statement: the test battle has this participant."""
        params = {
            "id": f"chr:observation:test:p710:{participant_qid}",
            "label": f"Test observation: {participant_qid} participated", "shortLabel": None,
            "sourceSystem": "Wikidata", "sourceEntityId": BATTLE[3], "predicateExternalId": "P710",
            "objectExternalId": participant_qid, "externalStatementId": f"{BATTLE[3]}$test-{participant_qid}",
            "qualifierPropertyIds": [], "sourceRevision": 1, "retrievedAt": "2026-10-11T00:00:00Z",
            "contentHash": "test", "rawPayloadUri": None, "status": "observed",
        }
        if persist:
            self.write("upsert_observation", params)
        return params

    def add_passage(self):
        self.write("upsert_passage_observation", {
            "id": PASSAGE_ID, "label": "Test passage", "shortLabel": None, "sourceSystem": "Test",
            "locator": "test:1", "passageText": PASSAGE_TEXT, "passageHash": "test",
            "editorialNotes": ["Sept. 2"], "language": "en", "workTitle": "Test", "author": "Test",
            "translator": None, "editionCitation": "Test", "rights": "test", "sourceUri": "test",
            "sourceRevision": "test", "retrievedAt": "2026-10-11T00:00:00Z", "contentHash": "test",
            "rawPayloadUri": None, "status": "observed",
        })

    def battle_with_leader(self):
        self.add_entity(BATTLE)
        self.add_entity(LEADER)
        self.write("link_year", {"entityId": BATTLE[0], "year": -31})
        observation = self.reader.observation(self.statement(LEADER[3])["id"])
        result = drafts_from_observation(observation, self.reader, self.registry)
        self.assertEqual(result.unresolved, ())
        self.assertEqual(len(result.drafts), 1)
        return result.drafts[0]

    def accepted_leader_claim(self):
        submission = submit(self.tx, self.battle_with_leader(), self.registry, self.operations)
        accept(self.tx, submission.validation.proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        return submission.validation.assertion_id

    def passage_draft(self, entity, quote):
        return ProposalDraft(
            predicate="participatedIn",
            subject_id=entity[0],
            object_id=BATTLE[0],
            observation_ids=(PASSAGE_ID,),
            quotations=(Quotation(observation_id=PASSAGE_ID, text=quote),),
            rationale="The test passage places this person in the battle line.",
            proposed_by="test",
        )

    def support_count(self, assertion_id):
        return len(self.reader.assertion(assertion_id)["observationIds"])

    # -- real-data replay ----------------------------------------------------

    def test_replaying_actium_observation_is_an_already_supported_duplicate(self):
        before = self.counts()
        observation = self.reader.observation(AGRIPPA_OBSERVATION)
        result = drafts_from_observation(observation, self.reader, self.registry)
        submission = submit(self.tx, result.drafts[0], self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.DUPLICATE)
        self.assertTrue(submission.validation.already_supported)
        self.assertFalse(submission.stored)
        self.assertEqual(self.counts(), before)

    # -- structured evidence -------------------------------------------------

    def test_unlinked_participants_are_reported_not_created(self):
        self.add_entity(BATTLE)
        before = self.counts()
        result = drafts_from_observation(self.statement(UNLINKED_QID, persist=False), self.reader, self.registry)
        self.assertEqual(result.drafts, ())
        self.assertEqual(result.unresolved, (f"{UNLINKED_QID} has no local Entity",))
        self.assertEqual(self.counts(), before)

    def test_full_workflow(self):
        draft = self.battle_with_leader()
        submission = submit(self.tx, draft, self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.VALID)
        self.assertTrue(submission.stored)
        proposal_id = submission.validation.proposal_id

        stored = self.tx.run(
            "MATCH (p:Proposal {id: $id})-[:PROPOSES]->(a:Assertion) RETURN p, a", id=proposal_id
        ).single()
        self.assertEqual(stored["p"]["status"], "submitted")
        self.assertEqual(stored["p"]["predicateRegistryVersion"], "predicates-v3")
        self.assertEqual(stored["a"]["status"], "proposed")
        self.assertEqual(stored["a"]["label"], "Test leader participated in Test battle")
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
        self.assertEqual(context["temporalContext"], "Test battle, 31 BCE")

        with self.assertRaises(ReviewError):
            accept(self.tx, proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        with self.assertRaises(ReviewError):
            reject(self.tx, proposal_id, operations=self.operations, **REJECTION)

    def test_new_claim_evidence_waits_for_acceptance(self):
        submission = submit(self.tx, self.battle_with_leader(), self.registry, self.operations)
        assertion_id = submission.validation.assertion_id
        self.assertEqual(self.support_count(assertion_id), 0)
        accept(self.tx, submission.validation.proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        self.assertEqual(self.support_count(assertion_id), 1)

    def test_rejecting_evidence_leaves_the_claim_open(self):
        submission = submit(self.tx, self.battle_with_leader(), self.registry, self.operations)
        decided = reject(self.tx, submission.validation.proposal_id, operations=self.operations, **REJECTION)
        self.assertEqual(decided["proposal"]["status"], "rejected")
        self.assertEqual(decided["assertion"]["status"], "proposed")
        self.assertEqual(self.support_count(submission.validation.assertion_id), 0)

    def test_rejecting_the_claim(self):
        submission = submit(self.tx, self.battle_with_leader(), self.registry, self.operations)
        decided = reject(self.tx, submission.validation.proposal_id, operations=self.operations,
                         reject_claim=True, **REJECTION)
        self.assertEqual(decided["assertion"]["status"], "rejected")
        self.assertTrue(decided["proposal"]["rejectedClaim"])

    def test_accepted_claim_cannot_be_rejected_through_a_proposal(self):
        assertion_id = self.accepted_leader_claim()
        self.add_passage()
        submission = submit(self.tx, self.passage_draft(LEADER, "The leader had the right wing"), self.registry, self.operations)
        with self.assertRaises(ReviewError):
            reject(self.tx, submission.validation.proposal_id, operations=self.operations, reject_claim=True, **REJECTION)
        self.assertEqual(self.reader.assertion(assertion_id)["status"], "accepted")

    def test_better_evidence_accepts_an_open_claim(self):
        """Weak evidence rejected, stronger evidence accepted: the claim survives."""
        weak = submit(self.tx, self.battle_with_leader(), self.registry, self.operations)
        assertion_id = weak.validation.assertion_id
        reject(self.tx, weak.validation.proposal_id, operations=self.operations, **REJECTION)
        self.add_passage()
        strong = submit(self.tx, self.passage_draft(LEADER, "The leader had the right wing"), self.registry, self.operations)
        self.assertEqual(strong.validation.outcome, Outcome.ADDS_EVIDENCE)
        decided = accept(self.tx, strong.validation.proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        self.assertEqual(decided["assertion"]["status"], "accepted")
        self.assertEqual(self.reader.assertion(assertion_id)["observationIds"], [PASSAGE_ID])

    def test_rejected_claim_can_be_reopened_and_then_supported(self):
        submission = submit(self.tx, self.battle_with_leader(), self.registry, self.operations)
        assertion_id = submission.validation.assertion_id
        reject(self.tx, submission.validation.proposal_id, operations=self.operations, reject_claim=True, **REJECTION)
        self.add_passage()
        draft = self.passage_draft(LEADER, "The leader had the right wing")
        self.assertEqual(submit(self.tx, draft, self.registry, self.operations).validation.outcome, Outcome.DUPLICATE)

        reopened = reopen(self.tx, assertion_id, operations=self.operations, **DECISION)
        self.assertEqual(reopened["assertion"]["status"], "proposed")
        self.assertEqual(reopened["assertion"]["reopenedBy"], "test-curator")
        with self.assertRaises(ReviewError):
            reopen(self.tx, assertion_id, operations=self.operations, **DECISION)

        evidence = submit(self.tx, draft, self.registry, self.operations)
        self.assertEqual(evidence.validation.outcome, Outcome.ADDS_EVIDENCE)
        decided = accept(self.tx, evidence.validation.proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        self.assertEqual(decided["assertion"]["status"], "accepted")

    def test_invented_evidence_is_refused_and_nothing_is_stored(self):
        self.battle_with_leader()
        self.add_entity(ADMIRAL)
        before = self.counts()
        invented = ProposalDraft(
            predicate="participatedIn",
            subject_id=ADMIRAL[0],
            object_id=BATTLE[0],
            observation_ids=(f"chr:observation:test:p710:{LEADER[3]}",),
            rationale="cites the leader's statement as if it were the admiral's",
            proposed_by="test",
        )
        submission = submit(self.tx, invented, self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.INVALID)
        self.assertFalse(submission.stored)
        self.assertEqual(self.counts(), before)

    # -- passage evidence ----------------------------------------------------

    def test_passage_evidence_for_accepted_assertion_waits_for_acceptance(self):
        assertion_id = self.accepted_leader_claim()
        self.add_passage()
        draft = self.passage_draft(LEADER, "The leader had the right wing")
        support_before = self.support_count(assertion_id)

        submission = submit(self.tx, draft, self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.ADDS_EVIDENCE)
        self.assertTrue(submission.stored)
        self.assertEqual(self.support_count(assertion_id), support_before)

        before_retry = self.counts()
        self.assertFalse(submit(self.tx, draft, self.registry, self.operations).stored)
        self.assertEqual(self.counts(), before_retry)

        accepted_at = self.tx.run("MATCH (a:Assertion {id: $id}) RETURN a.acceptedAt AS t", id=assertion_id).single()["t"]
        proposal_id = submission.validation.proposal_id
        decided = accept(self.tx, proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        self.assertEqual(decided["proposal"]["status"], "accepted")
        self.assertEqual(decided["assertion"]["status"], "accepted")
        self.assertEqual(decided["assertion"]["acceptedAt"], accepted_at)
        self.assertEqual(self.support_count(assertion_id), support_before + 1)
        support = self.tx.run(
            "MATCH (:Assertion {id: $id})-[s:SUPPORTED_BY]->(:SourceObservation {id: $passage}) "
            "RETURN s.quotation AS quotation, s.addedByProposal AS proposal",
            id=assertion_id, passage=PASSAGE_ID,
        ).single()
        self.assertEqual(support["quotation"], "The leader had the right wing")
        self.assertEqual(support["proposal"], proposal_id)
        self.assertEqual(submit(self.tx, draft, self.registry, self.operations).validation.outcome, Outcome.DUPLICATE)

    def test_rejected_evidence_leaves_assertion_untouched(self):
        assertion_id = self.accepted_leader_claim()
        self.add_passage()
        support_before = self.support_count(assertion_id)
        submission = submit(self.tx, self.passage_draft(LEADER, "The leader had the right wing"), self.registry, self.operations)
        decided = reject(self.tx, submission.validation.proposal_id, operations=self.operations, **REJECTION)
        self.assertEqual(decided["proposal"]["status"], "rejected")
        self.assertEqual(decided["assertion"]["status"], "accepted")
        self.assertEqual(self.support_count(assertion_id), support_before)

    def test_passage_can_support_a_new_assertion(self):
        self.add_entity(BATTLE)
        self.add_entity(ADMIRAL)
        self.add_passage()
        draft = self.passage_draft(ADMIRAL, "the admiral was extending the left wing to encircle the enemy")
        submission = submit(self.tx, draft, self.registry, self.operations)
        self.assertEqual(submission.validation.outcome, Outcome.VALID)
        decided = accept(self.tx, submission.validation.proposal_id, registry=self.registry, operations=self.operations, **DECISION)
        self.assertEqual(decided["assertion"]["status"], "accepted")

    def test_paraphrased_passage_evidence_is_refused(self):
        self.add_entity(BATTLE)
        self.add_entity(ADMIRAL)
        self.add_passage()
        before = self.counts()
        draft = self.passage_draft(ADMIRAL, "the admiral led the left wing of the fleet")
        self.assertEqual(submit(self.tx, draft, self.registry, self.operations).validation.outcome, Outcome.INVALID)
        self.assertEqual(self.counts(), before)

    # -- reason codes and supersession ---------------------------------------

    def test_rejection_needs_a_known_reason(self):
        submission = submit(self.tx, self.battle_with_leader(), self.registry, self.operations)
        with self.assertRaises(ReviewError):
            reject(self.tx, submission.validation.proposal_id, operations=self.operations, **DECISION, reason="weak")
        decided = reject(self.tx, submission.validation.proposal_id, operations=self.operations,
                         **DECISION, reason="underspecified")
        self.assertEqual(decided["proposal"]["decisionReason"], "underspecified")

    def proposed_admiral_claim(self):
        """A proposed claim whose only Proposal is still open."""
        self.add_passage()
        if self.reader.entity(ADMIRAL[0]) is None:
            self.add_entity(ADMIRAL)
        draft = self.passage_draft(ADMIRAL, "the admiral was extending the left wing to encircle the enemy")
        submission = submit(self.tx, draft, self.registry, self.operations)
        return submission.validation.assertion_id, submission.validation.proposal_id

    def test_superseding_an_accepted_claim_links_its_replacements(self):
        old = self.accepted_leader_claim()
        new, _ = self.proposed_admiral_claim()
        result = supersede(self.tx, old, [new], reason="underspecified", operations=self.operations, **DECISION)
        self.assertEqual(result["assertion"]["status"], "superseded")
        self.assertEqual(result["assertion"]["supersededFrom"], "accepted")
        self.assertEqual(result["assertion"]["supersedeReason"], "underspecified")
        self.assertEqual(result["replacementIds"], [new])
        links = self.tx.run(
            "MATCH (:Assertion {id: $old})-[:SUPERSEDED_BY]->(n:Assertion) RETURN collect(n.id) AS ids", old=old
        ).single()["ids"]
        self.assertEqual(links, [new])

        before = self.counts()
        retry = supersede(self.tx, old, [new], reason="underspecified", operations=self.operations,
                          **(DECISION | {"decided_at": "2099-01-01T00:00:00Z"}))
        self.assertEqual(retry["assertion"]["supersededAt"], DECISION["decided_at"])
        self.assertEqual(self.counts(), before)
        with self.assertRaises(ReviewError):
            supersede(self.tx, old, [new, "chr:assertion:test:missing"], reason="underspecified",
                      operations=self.operations, **DECISION)

        self.add_passage()
        evidence = submit(self.tx, self.passage_draft(LEADER, "The leader had the right wing"), self.registry, self.operations)
        self.assertEqual(evidence.validation.outcome, Outcome.DUPLICATE)
        self.assertFalse(evidence.stored)

    def test_superseding_a_proposed_claim_requires_its_proposals_decided(self):
        replacement = self.accepted_leader_claim()
        old, proposal = self.proposed_admiral_claim()
        with self.assertRaises(ReviewError):
            supersede(self.tx, old, [replacement], reason="superseded-by-model", operations=self.operations, **DECISION)
        reject(self.tx, proposal, operations=self.operations, **DECISION, reason="superseded-by-model")
        result = supersede(self.tx, old, [replacement], reason="superseded-by-model", operations=self.operations, **DECISION)
        self.assertEqual(result["assertion"]["status"], "superseded")
        self.assertEqual(result["assertion"]["supersededFrom"], "proposed")

    def test_invalid_supersessions_are_refused(self):
        accepted = self.accepted_leader_claim()
        old, proposal = self.proposed_admiral_claim()
        reject(self.tx, proposal, operations=self.operations, **REJECTION, reject_claim=True)
        before = self.counts()
        refused = [
            (old, [accepted], "underspecified"),  # a rejected claim
            (accepted, [accepted], "underspecified"),  # replaced by itself
            (accepted, ["chr:assertion:test:missing"], "underspecified"),  # unknown replacement
            (accepted, [old], "underspecified"),  # a rejected replacement
            (accepted, [], "underspecified"),  # no replacement
            (accepted, [accepted], "because"),  # unknown reason
        ]
        for assertion_id, replacements, reason in refused:
            with self.subTest(assertion=assertion_id, replacements=replacements, reason=reason):
                with self.assertRaises(ReviewError):
                    supersede(self.tx, assertion_id, replacements, reason=reason, operations=self.operations, **DECISION)
        self.assertEqual(self.counts(), before)

    # -- inquiry scope -------------------------------------------------------

    def test_inquiry_scope_is_focus_linked_and_declared_entities_only(self):
        self.accepted_leader_claim()
        self.add_entity(ADMIRAL)
        bystander = ("chr:entity:test-bystander", "Person", "Test bystander", "Q999990004")
        self.add_entity(bystander)
        self.write("upsert_subject", {"id": "chr:subject:test-battle", "label": "History of the test battle",
                                      "status": "provisional", "shortLabel": None})
        self.write("link_subject_focus", {"subjectId": "chr:subject:test-battle", "entityId": BATTLE[0]})
        inquiry = {
            "id": "chr:inquiry:test", "version": 1, "label": "Test inquiry",
            "subjectId": "chr:subject:test-battle",
            "source": {"edition": "phase-5-source/none.xml", "chapters": "1-2"},
            "candidateEntityIds": [ADMIRAL[0]], "guidance": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inquiry.json"
            path.write_text(json.dumps(inquiry), encoding="utf-8")
            scope = {entity["id"] for entity in load_inquiry(path, self.tx).scope}
        self.assertEqual(scope, {BATTLE[0], LEADER[0], ADMIRAL[0]})

    def test_inquiry_with_unknown_declared_entity_is_refused(self):
        self.add_entity(BATTLE)
        self.write("upsert_subject", {"id": "chr:subject:test-battle", "label": "History of the test battle",
                                      "status": "provisional", "shortLabel": None})
        self.write("link_subject_focus", {"subjectId": "chr:subject:test-battle", "entityId": BATTLE[0]})
        inquiry = {
            "id": "chr:inquiry:test", "version": 1, "label": "Test inquiry", "subjectId": "chr:subject:test-battle",
            "source": {"edition": "none", "chapters": "1-2"}, "candidateEntityIds": ["chr:entity:nobody"], "guidance": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inquiry.json"
            path.write_text(json.dumps(inquiry), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_inquiry(path, self.tx)

if __name__ == "__main__":
    unittest.main()
