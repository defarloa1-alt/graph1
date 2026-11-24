"""The front door (31 §5 step 3, D-174): resolve, anchor, read coverage, orient, plan; run nothing.

Offline tests cover the command, the recipe conditions and the plan; live tests (rolled back,
synthetic entities) cover identity, the Subject, the draft inquiry, and saving."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from GraphRevised.orchestration.contracts import IdentityCandidate, InquiryRunState, RunStatus
from GraphRevised.orchestration.front_door import (
    RECIPES, conditions, find_inquiry, load_json, parse_command, plan_items,
)
from GraphRevised import localdb

ESTIMATES = {"perPassageReadUSD": 0.01, "minSources": 3}
FOCUS = IdentityCandidate(label="Battle of Test", kind="Event", qid="Q1", local_entity_id="chr:entity:t", why="test")
SOURCES = [{"workId": "chr:entity:w1", "voice": "One", "type": "perseus-tei"},
           {"workId": "chr:entity:w2", "voice": "Two", "type": "wikipedia-html"}]


def report(general=(10, 10), military=(0, 10), finder=("passage finder", "inquiry chapters"), lens_met=False, open_=0):
    rows = []
    for (g, total), (m, _), by, source in zip((general, general), (military, military), finder, SOURCES):
        rows.append({"workId": source["workId"], "voice": source["voice"], "assigned": total, "by": by,
                     "readers": {"general": {"read": g, "dryOnly": 0}, "military": {"read": m, "dryOnly": 0}}})
    return {"2 sources read": {"sources": rows, "met": False},
            "3 lens questions": {"met": lens_met}, "4 phase spine": {"met": False, "open": open_}}


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.recipe = load_json(RECIPES)["recipes"]["Event"]
        self.values = {"qid": "Q1", "focus": "chr:entity:t", "inquiry": "GraphRevised/inquiries/t.json", "label": "Battle of Test"}

    def test_the_command_names_its_thing(self):
        self.assertEqual(parse_command('graph "Battle of Test"'), "Battle of Test")
        self.assertEqual(parse_command("Graph  Battle of Test "), "Battle of Test")
        self.assertEqual(parse_command("“Battle of Test”"), "Battle of Test")

    def test_conditions_are_read_from_the_inquiry_and_coverage(self):
        held = conditions(FOCUS, {"sources": SOURCES}, report(), ESTIMATES)
        self.assertFalse(held["noLocalEntity"])
        self.assertFalse(held["noWikipediaSource"])
        self.assertTrue(held["fewSources"])
        self.assertEqual([s["workId"] for s in held["sourceWithoutFinder"]], ["chr:entity:w2"])
        self.assertEqual(held["sourceUnread"], [])
        self.assertEqual([(s["workId"], s["passages"]) for s in held["sourceUnreadByLens"]["military"]],
                         [("chr:entity:w1", 10), ("chr:entity:w2", 10)])
        self.assertTrue(held["lensQuestionsOpen"])
        self.assertTrue(held["noPhases"])
        self.assertFalse(conditions(FOCUS, {"sources": SOURCES}, report(open_=3), ESTIMATES)["noPhases"])

    def test_lenses_are_planned_in_the_catalogue_order_whichever_source_lacks_them(self):
        rows = report()
        rows["2 sources read"]["sources"][0]["readers"] = {"general": {"read": 10, "dryOnly": 0},
                                                           "military": {"read": 10, "dryOnly": 0},
                                                           "political": {"read": 0, "dryOnly": 0}}
        rows["2 sources read"]["sources"][1]["readers"]["political"] = {"read": 0, "dryOnly": 0}
        held = conditions(FOCUS, {"sources": SOURCES}, rows, ESTIMATES)
        self.assertEqual(list(held["sourceUnreadByLens"]), ["military", "political"])

    def test_the_plan_follows_the_recipe_within_the_budget(self):
        held = conditions(FOCUS, {"sources": SOURCES * 2}, report(), ESTIMATES)
        items, questions, calls = plan_items(self.recipe, held, ESTIMATES, self.values, budget=10)
        actions = [(i.action, i.lens, i.target) for i in items]
        self.assertEqual(actions[0][0], "FIND")
        self.assertIn(("READ", "military", "chr:entity:w1"), actions)
        read = next(i for i in items if i.action == "READ" and i.target == "chr:entity:w2")
        find = next(i for i in items if i.action == "FIND" and i.target == "chr:entity:w2")
        self.assertIn(find.item_id, read.depends_on)  # a reading waits for its own source's finder
        self.assertEqual(read.budget_usd, 0.1)  # 10 passages at $0.01, no start cost in these estimates
        self.assertEqual(calls[read.item_id]["arguments"],
                         ["GraphRevised/inquiries/t.json", "--source", "chr:entity:w2", "--found", "--unread", "--lens", "military",
                          "--submit"])
        self.assertTrue(any(q.startswith("RECONCILE is not built") for q in questions))
        self.assertFalse(any(i.action in ("RECONCILE", "CRITIQUE", "ACCOUNT") for i in items))

    def test_a_tight_budget_keeps_a_prefix_and_says_what_it_left_out(self):
        held = conditions(FOCUS, {"sources": SOURCES}, report(), ESTIMATES)
        estimates = ESTIMATES | {"minSources": 2}  # enough sources: no source plan
        held = conditions(FOCUS, {"sources": SOURCES}, report(), estimates)
        items, questions, _ = plan_items(self.recipe, held, estimates, self.values, budget=0.35)
        self.assertEqual([i.action for i in items], ["FIND"])
        left = next(q for q in questions if q.startswith("Left out for the budget"))
        self.assertIn("READ military One ($0.10)", left)  # it would fit, but the plan stays in recipe order

    def test_every_registry_source_is_listed_with_what_it_gives_and_its_rights(self):
        from GraphRevised.orchestration.front_door import REGISTRY, registry_federations

        registry = load_json(REGISTRY)
        listed = registry_federations(registry)
        self.assertEqual(len(listed), len(registry["sources"]))
        self.assertTrue(all(f.gives and f.status for f in listed))
        unverified = [f for f in listed if f.rights_class is None and f.status != "candidate"]
        self.assertTrue(all("not yet read at the source" in f.why for f in unverified))

    def test_candidates_are_ranked_by_the_questions_and_the_lenses_missing(self):
        from GraphRevised.orchestration.front_door import rank_candidates

        registry = {"sources": [
            {"id": "coins", "label": "Coins", "status": "candidate", "terms": ["coin"], "lenses": ["economic"], "rights": {}},
            {"id": "roads", "label": "Roads", "status": "candidate", "terms": ["route"], "lenses": ["military"], "rights": {}},
            {"id": "poems", "label": "Poems", "status": "candidate", "terms": ["verse"], "lenses": ["artistic"], "rights": {}},
            {"id": "inuse", "label": "In use", "status": "read", "terms": [], "lenses": [], "rights": {"unverified": "403"}},
            {"id": "fine", "label": "Fine", "status": "read", "terms": ["coin"], "lenses": ["economic"], "rights": {"class": "A"}}]}
        ranked = rank_candidates(registry, ["Do the legionary coin issues show his forces?"], ["military"])
        self.assertEqual([r["systemId"] for r in ranked], ["coins", "roads"])  # not poems, nor a source already read
        self.assertIn("bears on the Question", ranked[0]["why"])
        self.assertIn("military lens", ranked[1]["why"])

    def test_a_ranked_candidate_becomes_a_free_register_item_done_by_hand(self):
        held = conditions(FOCUS, {"sources": SOURCES * 2}, report(), ESTIMATES)
        held["candidateSources"] = [{"systemId": "coins", "label": "Coins", "homepage": "https://example.org/",
                                     "why": "bears on a Question", "score": 3, "passages": 0}]
        items, _, calls = plan_items(self.recipe, held, ESTIMATES, self.values, budget=10)
        register = next(i for i in items if i.action == "REGISTER")
        self.assertEqual((register.target, register.budget_usd), ("coins", 0))
        self.assertEqual(calls[register.item_id]["worker"], "manual")
        self.assertIn("https://example.org/", calls[register.item_id]["instructions"])

    def test_the_inquiry_is_found_by_its_focus(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a.json").write_text(json.dumps({"id": "chr:inquiry:a", "narrativeEventId": "chr:entity:x"}))
            Path(directory, "b.json").write_text(json.dumps({"id": "chr:inquiry:b", "focusIds": ["chr:entity:y"],
                                                             "narrativeEventId": "chr:entity:x"}))
            self.assertEqual(find_inquiry("chr:entity:x", Path(directory)).name, "a.json")
            self.assertEqual(find_inquiry("chr:entity:y", Path(directory)).name, "b.json")
            self.assertIsNone(find_inquiry("chr:entity:z", Path(directory)))


TWIN = ("chr:entity:test-front-door-twin-a", "chr:entity:test-front-door-twin-b")
LONE = "chr:entity:test-front-door-lone"
SUBJECT = "chr:subject:test-front-door-lone"


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class LiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        from GraphRevised.operations import load_operations

        cls.operations = load_operations()
        cls.driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
        cls.session = cls.driver.session(database=localdb.database())

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        from GraphRevised.operations import run_write

        self.tx = self.session.begin_transaction()
        self.addCleanup(self.tx.rollback)
        for entity_id, label in ((TWIN[0], "Zyxwv Qrstu Skirmish"), (TWIN[1], "Zyxwv Qrstu Skirmish"),
                                 (LONE, "Vwxyz Plover Engagement")):
            run_write(self.tx, self.operations, "upsert_entity", {
                "id": entity_id, "kind": "Event", "label": label, "description": f"test {entity_id[-6:]}",
                "status": "proposed", "shortLabel": None})
        self.tx.run("MATCH (e:Entity {id: $id}) CREATE (:Subject {id: $s, label: 'History of a test engagement', "
                    "status: 'provisional'})-[:HAS_SUBJECT_FOCUS]->(e)", id=LONE, s=SUBJECT)
        self.dirs = tempfile.TemporaryDirectory()
        self.addCleanup(self.dirs.cleanup)
        self.root = Path(self.dirs.name)

    def run_door(self, command, **extra):
        from GraphRevised.orchestration.front_door import front_door

        return front_door(self.tx, command, search=None, inquiries=self.root / "inquiries",
                          dossiers=self.root / "dossiers", run_id="front-door-test", **extra)

    def test_two_entities_with_the_same_words_are_a_question_for_the_curator(self):
        result = self.run_door('graph "Zyxwv Qrstu Skirmish"')
        state = result["state"]
        self.assertIsNone(state.plan)
        self.assertEqual(state.status, RunStatus.AWAITING_USER)
        self.assertEqual(state.open_interrupts()[0].reason, "identity")
        self.assertEqual(len(state.open_interrupts()[0].options), 2)
        chosen = self.run_door('graph "Zyxwv Qrstu Skirmish"', focus_key=TWIN[1])
        self.assertEqual(chosen["focus"].chosen.local_entity_id, TWIN[1])
        self.assertEqual(chosen["focus"].decided_by, "curator")

    def test_one_match_is_planned_against_its_subject_with_a_draft_inquiry(self):
        from GraphRevised.orchestration.front_door import save

        result = self.run_door("Vwxyz Plover Engagement")
        state = result["state"]
        self.assertEqual(state.plan.focus.chosen.local_entity_id, LONE)
        self.assertEqual(state.plan.subject.subject_id, SUBJECT)
        self.assertTrue(state.plan.subject.provisional)
        self.assertEqual(state.inquiry_id, "chr:inquiry:vwxyz-plover-engagement")
        self.assertEqual(result["draftInquiry"]["data"]["narrativeEventId"], LONE)
        self.assertEqual([i.action for i in state.plan.items], ["SOURCE_PLAN", "BUILD_INQUIRY"])  # no QID: no contact
        self.assertTrue(all(i.decision.status == "awaiting" for i in state.plan.items))
        self.assertIsNone(state.next_item())  # guided: nothing runs before the curator decides
        written = save(result, runs=self.root / "runs", dossiers=self.root / "dossiers", root=self.root)
        self.assertEqual(len(written), 4)
        self.assertEqual(InquiryRunState.load(self.root / "runs" / "front-door-test.json").plan.inquiry_id,
                         state.inquiry_id)
        with self.assertRaises(FileExistsError):
            save(result, runs=self.root / "runs", dossiers=self.root / "dossiers", root=self.root)
        again = self.run_door("Vwxyz Plover Engagement")
        self.assertEqual(again["dossier"].version, 2)  # a later orientation revises the dossier

    def test_nothing_is_written_to_the_graph(self):
        before = self.tx.run("MATCH (n) RETURN count(n) AS n").single()["n"]
        self.run_door("Vwxyz Plover Engagement")
        self.assertEqual(self.tx.run("MATCH (n) RETURN count(n) AS n").single()["n"], before)


if __name__ == "__main__":
    unittest.main()
