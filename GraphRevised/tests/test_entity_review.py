"""Entity review: rule leads, the checks on the model's findings, and the commands they carry. Offline."""

import unittest

from GraphRevised.discovery.entity_review import Finding, Review, check, flags

ROW = {"id": "chr:entity:consul", "label": "consul", "kind": "Office", "status": "proposed", "claimCount": 0,
       "claims": [], "mentions": [{"id": "chr:annotation:m1", "note": "Linked in Wikipedia as 'consuls'"}],
       "wikidata": {"qid": "Q4489757", "ruleKind": "Office"},
       "nearby": [{"id": "chr:entity:roman-consul", "label": "Roman consul", "kind": "Office", "claimCount": 4,
                   "qid": "Q40779"}]}
ROW["flags"] = flags(ROW, ROW["nearby"])


def finding(**fields):
    base = dict(entity_id=ROW["id"], verdict="wrong-identity", target_entity_id="chr:entity:roman-consul",
                suggested_kind="", rationale="The generic consul; the Roman office is meant.",
                evidence_ids=["chr:annotation:m1"])
    return Finding(**(base | fields))


class EntityReviewTests(unittest.TestCase):
    def test_rule_leads(self):
        self.assertEqual(ROW["flags"], ["no claim uses it, while a similarly named entity is used"])
        misfiled = ROW | {"kind": "Type", "wikidata": {"qid": "Q1", "ruleKind": "Office"}}
        self.assertIn("the harvest rules give Wikidata's classes the kind Office, not Type", flags(misfiled, []))
        shared = [{"id": "chr:entity:other", "qid": "Q4489757", "claimCount": 0}]
        self.assertIn("another entity holds the same Wikidata identity: chr:entity:other", flags(ROW, shared))

    def test_a_wrong_identity_carries_the_command_to_retire_it(self):
        (item,) = check([ROW], Review(findings=[finding()]))
        self.assertEqual(item["problems"], [])
        self.assertTrue(item["commands"][0].startswith("python -m GraphRevised.proposals.review entity-reject chr:entity:consul"))
        self.assertIn("The entity meant is chr:entity:roman-consul.", item["commands"][0])

    def test_a_wrong_kind_settles_open_claims_first(self):
        row = ROW | {"claimCount": 1}
        (item,) = check([row], Review(findings=[finding(verdict="wrong-kind", target_entity_id="", suggested_kind="Type")]))
        self.assertTrue(item["commands"][0].startswith("# first: settle the 1 open claim"))
        self.assertIn("entity-kind chr:entity:consul --from Office --to Type", item["commands"][1])

    def test_findings_outside_the_packet_carry_problems_and_no_commands(self):
        for bad, problem in ((finding(target_entity_id="chr:entity:elsewhere"), "target is not among the nearby entities"),
                             (finding(evidence_ids=["chr:assertion:invented"]), "cites ids not in the packet"),
                             (finding(verdict="wrong-kind", suggested_kind="Rank"), "unknown kind 'Rank'"),
                             (finding(verdict="duplicate", target_entity_id=""), "duplicate without the entity to keep")):
            with self.subTest(problem=problem):
                (item,) = check([ROW], Review(findings=[bad]))
                self.assertIn(problem, item["problems"])
                self.assertEqual(item["commands"], [])

    def test_every_entity_is_judged_once(self):
        with self.assertRaises(ValueError):
            check([ROW], Review(findings=[]))
        with self.assertRaises(ValueError):
            check([ROW], Review(findings=[finding(), finding()]))


if __name__ == "__main__":
    unittest.main()
