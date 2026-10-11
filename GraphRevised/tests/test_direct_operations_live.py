"""Live checks for the Phase 3 direct operations.

Every test runs inside a transaction that is rolled back, so the local
clean-start database is never changed. Requires NEO4J_PASSWORD; NEO4J_URI and
NEO4J_USERNAME default to the local clean-start instance.
"""

import os
import unittest
from pathlib import Path

OPERATIONS_PATH = Path(__file__).resolve().parents[1] / "13-PHASE-3-DIRECT-OPERATIONS.cypher"

ACTIUM = "chr:entity:battle-of-actium"
AGRIPPA = "chr:entity:marcus-vipsanius-agrippa"
SUBJECT = "chr:subject:history-of-battle-of-actium"
AUTHORITY = "chr:authority:wikidata:Q160387"
OBSERVATION = "chr:observation:wikidata:Q160387:P710:32bdfa2f:r2555342002"
ASSERTION = "chr:assertion:marcus-vipsanius-agrippa:participated-in:battle-of-actium"
PROPOSAL = "chr:proposal:accept-marcus-vipsanius-agrippa-participation-at-actium"

(
    GET_NODE,
    GET_SUBJECT,
    GET_NEIGHBORHOOD,
    GET_EVIDENCE,
    GET_TEMPORAL_CONTEXT,
    UPSERT_ENTITY,
    UPSERT_SUBJECT,
    LINK_SUBJECT_FOCUS,
    LINK_YEAR,
    UPSERT_AUTHORITY,
    UPSERT_OBSERVATION,
    UPSERT_ASSERTION,
    LINK_SUPPORT,
    UPSERT_PROPOSAL,
    DECIDE_PROPOSAL,
) = range(15)


def load_statements() -> list[str]:
    lines = [
        line
        for line in OPERATIONS_PATH.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("//")
    ]
    statements = [part.strip() for part in "\n".join(lines).split(";")]
    return [statement for statement in statements if statement]


SNAPSHOT_QUERY = """
CALL () {
  MATCH (node) WHERE NOT node:Year
  RETURN collect([labels(node), properties(node)]) AS nodes
}
CALL () {
  MATCH (start)-[relationship]->(end) WHERE NOT start:Year
  RETURN collect([
    coalesce(start.id, start.year), type(relationship),
    properties(relationship), coalesce(end.id, end.year)
  ]) AS relationships
}
CALL () { MATCH (node) RETURN count(node) AS nodeCount }
CALL () { MATCH ()-[relationship]->() RETURN count(relationship) AS relationshipCount }
RETURN nodes, relationships, nodeCount, relationshipCount
"""


def entity_params(**overrides):
    params = {
        "id": ACTIUM,
        "kind": "Event",
        "label": None,
        "description": None,
        "status": None,
        "shortLabel": None,
    }
    params.update(overrides)
    return params


def authority_params(**overrides):
    params = {
        "entityId": ACTIUM,
        "id": AUTHORITY,
        "system": "Wikidata",
        "identifier": "Q160387",
        "label": None,
        "shortLabel": None,
        "description": None,
        "retrievedAt": None,
        "role": "entity_identity",
        "relation": "closeMatch",
        "linkStatus": "accepted",
    }
    params.update(overrides)
    return params


def assertion_params(**overrides):
    params = {
        "id": ASSERTION,
        "label": None,
        "shortLabel": None,
        "predicate": "participatedIn",
        "assertedBy": "test",
        "subjectId": AGRIPPA,
        "objectId": ACTIUM,
    }
    params.update(overrides)
    return params


def proposal_params(**overrides):
    params = {
        "id": PROPOSAL,
        "assertionId": ASSERTION,
        "label": None,
        "shortLabel": None,
        "operation": "create",
        "createdBy": "test",
    }
    params.update(overrides)
    return params


def decision_params(proposal_id, status):
    return {
        "proposalId": proposal_id,
        "proposalStatus": status,
        "decidedAt": "2026-10-11T00:00:00Z",
        "decidedBy": "test",
        "decisionBasis": "test",
    }


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class DirectOperationsLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from neo4j import GraphDatabase

        cls.statements = load_statements()
        cls.driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        )
        cls.session = cls.driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.close()
        cls.driver.close()

    def setUp(self) -> None:
        self.tx = self.session.begin_transaction()
        self.before = self.snapshot()

    def tearDown(self) -> None:
        self.tx.rollback()

    def run_op(self, index, params):
        return self.tx.run(self.statements[index], params).data()

    def snapshot(self):
        return self.tx.run(SNAPSHOT_QUERY).single().data()

    def assertUnchanged(self) -> None:
        after = self.snapshot()
        self.assertEqual(after["nodeCount"], self.before["nodeCount"])
        self.assertEqual(after["relationshipCount"], self.before["relationshipCount"])
        self.assertCountEqual(after["nodes"], self.before["nodes"])
        self.assertCountEqual(after["relationships"], self.before["relationships"])

    def assertRefused(self, index, params) -> None:
        self.assertEqual(self.run_op(index, params), [])
        self.assertUnchanged()

    def test_artifact_has_fifteen_statements(self) -> None:
        self.assertEqual(len(self.statements), 15)

    def test_reads_return_actium_slice(self) -> None:
        self.assertEqual(self.run_op(GET_NODE, {"id": ACTIUM})[0]["nodeTypes"], ["Entity"])
        self.assertEqual(self.run_op(GET_SUBJECT, {"subjectId": SUBJECT})[0]["focus"]["id"], ACTIUM)
        neighborhood = self.run_op(GET_NEIGHBORHOOD, {"entityId": ACTIUM})
        self.assertEqual([row["predicate"] for row in neighborhood], ["participatedIn"])
        evidence = self.run_op(GET_EVIDENCE, {"assertionId": ASSERTION})[0]
        self.assertEqual([obs["id"] for obs in evidence["sourceObservations"]], [OBSERVATION])
        self.assertEqual([prop["id"] for prop in evidence["proposals"]], [PROPOSAL])
        context = self.run_op(GET_TEMPORAL_CONTEXT, {"assertionId": ASSERTION})[0]
        self.assertEqual(context["temporalContext"], "Battle of Actium, 31 BCE")

    def test_replaying_every_write_changes_nothing(self) -> None:
        writes = [
            (UPSERT_ENTITY, entity_params()),
            (UPSERT_ENTITY, entity_params(id=AGRIPPA, kind="Person")),
            (UPSERT_SUBJECT, {"id": SUBJECT, "label": None, "status": None, "shortLabel": None}),
            (LINK_SUBJECT_FOCUS, {"subjectId": SUBJECT, "entityId": ACTIUM}),
            (LINK_YEAR, {"entityId": ACTIUM, "year": -31}),
            (UPSERT_AUTHORITY, authority_params()),
            (
                UPSERT_OBSERVATION,
                {
                    "id": OBSERVATION,
                    "label": None,
                    "shortLabel": None,
                    "sourceSystem": "Wikidata",
                    "sourceEntityId": "Q160387",
                    "predicateExternalId": "P710",
                    "objectExternalId": "Q48174",
                    "externalStatementId": "Q160387$32bdfa2f-497d-fb83-169f-f9567f3152ec",
                    "sourceRevision": 2555342002,
                    "retrievedAt": "2026-10-11T11:25:54.938655+00:00",
                    "contentHash": "different-on-purpose",
                    "rawPayloadUri": None,
                    "status": None,
                },
            ),
            (UPSERT_ASSERTION, assertion_params()),
            (LINK_SUPPORT, {"assertionId": ASSERTION, "observationId": OBSERVATION}),
            (UPSERT_PROPOSAL, proposal_params()),
            (DECIDE_PROPOSAL, decision_params(PROPOSAL, "accepted")),
        ]
        for index, params in writes:
            with self.subTest(operation=index):
                self.assertEqual(len(self.run_op(index, params)), 1)
        self.assertUnchanged()

    def test_year_outside_backbone_is_refused(self) -> None:
        for year in (0, -2500, 3000):
            with self.subTest(year=year):
                self.assertRefused(LINK_YEAR, {"entityId": ACTIUM, "year": year})

    def test_entity_kind_cannot_change(self) -> None:
        self.assertRefused(UPSERT_ENTITY, entity_params(kind="Person"))

    def test_authority_with_conflicting_local_id_is_refused(self) -> None:
        self.assertRefused(UPSERT_AUTHORITY, authority_params(id="chr:authority:other"))

    def test_authority_for_missing_entity_creates_nothing(self) -> None:
        self.assertRefused(
            UPSERT_AUTHORITY,
            authority_params(entityId="chr:entity:missing", id="chr:authority:wikidata:Q1", identifier="Q1"),
        )

    def test_assertion_identity_cannot_change(self) -> None:
        self.assertRefused(UPSERT_ASSERTION, assertion_params(predicate="commanded"))
        self.assertRefused(UPSERT_ASSERTION, assertion_params(objectId=AGRIPPA))

    def test_assertion_with_missing_endpoint_creates_nothing(self) -> None:
        self.assertRefused(
            UPSERT_ASSERTION,
            assertion_params(id="chr:assertion:test:missing", subjectId="chr:entity:missing"),
        )

    def test_proposal_cannot_retarget(self) -> None:
        self.run_op(UPSERT_ENTITY, entity_params(id="chr:entity:test-octavian", kind="Person"))
        self.run_op(
            UPSERT_ASSERTION,
            assertion_params(id="chr:assertion:test:octavian", subjectId="chr:entity:test-octavian"),
        )
        self.before = self.snapshot()
        self.assertRefused(UPSERT_PROPOSAL, proposal_params(assertionId="chr:assertion:test:octavian"))

    def test_terminal_decision_cannot_be_reversed(self) -> None:
        self.assertRefused(DECIDE_PROPOSAL, decision_params(PROPOSAL, "rejected"))
        self.assertRefused(DECIDE_PROPOSAL, decision_params(PROPOSAL, "validating"))

    def test_unknown_status_is_refused(self) -> None:
        self.assertRefused(DECIDE_PROPOSAL, decision_params(PROPOSAL, "approved"))

    def test_new_proposal_lifecycle(self) -> None:
        assertion_id = "chr:assertion:test:octavian"
        proposal_id = "chr:proposal:test:octavian"
        self.run_op(UPSERT_ENTITY, entity_params(id="chr:entity:test-octavian", kind="Person"))
        created = self.run_op(
            UPSERT_ASSERTION,
            assertion_params(id=assertion_id, subjectId="chr:entity:test-octavian"),
        )
        self.assertEqual(created[0]["assertion"]["status"], "proposed")
        proposal = self.run_op(UPSERT_PROPOSAL, proposal_params(id=proposal_id, assertionId=assertion_id))
        self.assertEqual(proposal[0]["proposal"]["status"], "submitted")

        self.assertEqual(self.run_op(DECIDE_PROPOSAL, decision_params(proposal_id, "accepted")), [])
        self.assertEqual(len(self.run_op(DECIDE_PROPOSAL, decision_params(proposal_id, "validating"))), 1)
        accepted = self.run_op(DECIDE_PROPOSAL, decision_params(proposal_id, "accepted"))[0]
        self.assertEqual(accepted["proposal"]["status"], "accepted")
        self.assertEqual(accepted["assertion"]["status"], "accepted")
        self.assertEqual(accepted["assertion"]["acceptedAt"], "2026-10-11T00:00:00Z")

        retry = decision_params(proposal_id, "accepted") | {"decidedAt": "2099-01-01T00:00:00Z"}
        retried = self.run_op(DECIDE_PROPOSAL, retry)[0]
        self.assertEqual(retried["proposal"]["decidedAt"], "2026-10-11T00:00:00Z")

        second_id = "chr:proposal:test:octavian-second"
        self.run_op(UPSERT_PROPOSAL, proposal_params(id=second_id, assertionId=assertion_id))
        rejected = self.run_op(DECIDE_PROPOSAL, decision_params(second_id, "rejected"))[0]
        self.assertEqual(rejected["proposal"]["status"], "rejected")
        self.assertEqual(rejected["assertion"]["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
