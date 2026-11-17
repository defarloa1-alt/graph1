"""Questions and Positions in the read side (44, D-153): a Position's history in words, never a
count of evidence; each holds or rejects link says whose account it is; the fact layer draws a
Question one hop from its event. The live test is rolled back and looks only at its fixtures."""

import os
import unittest

from GraphRevised.export.confidence import position_history, position_link_wording
from GraphRevised.export.cytoscape import projection
from GraphRevised.export.fact_layer import plan


def link(verb, holder, name, time=None, start=None, ancient=False, reporter=None, status="proposed"):
    return {"verb": verb, "holder": holder, "name": name, "time": time, "start": start, "ancient": ancient,
            "reporter": reporter, "status": status}


class PositionWordingTests(unittest.TestCase):
    def test_a_history_not_a_count(self):
        history = position_history([
            link("holds", "w:kromayer-1899", "Kromayer", "1899 CE", 2414000, reporter="Lange"),
            link("holds", "w:dio", "Cassius Dio", ancient=True, reporter="Lange"),
            link("holds", "w:gillies", "Gillies", "1807 CE", 2380000, reporter="Lange"),
            link("rejects", "w:tarn-1931", "Tarn", "1931 CE", 2426000, reporter="Lange"),
            link("holds", "w:gone", "Withdrawn", "1900 CE", 2415000, status="rejected"),
        ], [{"reception": "dominant", "time": "from 1899 CE", "according": "Lange", "status": "proposed"}])
        self.assertEqual(history, "held by Cassius Dio; Gillies (1807), Kromayer (1899); rejected by Tarn (1931); "
                                  "dominant from 1899 (according to Lange); as reported by Lange")
        self.assertNotIn("attested", history)

    def test_two_reporters_of_one_holder_name_it_once(self):
        history = position_history([link("holds", "w:k", "Kromayer", "1899 CE", 1, reporter="Lange"),
                                    link("holds", "w:k", "Kromayer", "1899 CE", 1, reporter="Tarn")])
        self.assertEqual(history, "held by Kromayer (1899); as reported by Lange, Tarn")

    def test_a_source_time_phrase_reads_inside_the_sentence(self):
        received = [{"reception": "dominant", "time": "Until the end of the nineteenth century",
                     "according": "D", "status": "proposed"},
                    {"reception": "contested", "time": "Augustan times", "according": None, "status": "proposed"}]
        self.assertEqual(position_history([], received),
                         "dominant until the end of the nineteenth century (according to D); contested Augustan times")

    def test_nothing_live_says_so(self):
        self.assertEqual(position_history([link("holds", "w", "X", status="superseded")]), "no holder recorded yet")

    def test_a_link_in_its_own_words_or_reported(self):
        own = {"status": "accepted", "work": "w:lange", "name": "Lange"}
        reported = {"status": "proposed", "work": "w:lange", "name": "Lange"}
        self.assertEqual(position_link_wording("w:lange", [own]), "in its own words")
        self.assertEqual(position_link_wording("w:kromayer", [reported]), "reported by Lange")
        self.assertEqual(position_link_wording("w:kromayer", [reported, {"status": "accepted", "work": "w:kromayer",
                                                                         "name": "Kromayer"}]),
                         "in its own words; also reported by Lange")

    def test_the_fact_layer_writes_a_position_history(self):
        view = {"elements": {"nodes": [{"data": {"id": "p", "label": "P", "fullLabel": "P", "facts": [],
                                                 "history": "held by Cassius Dio"}}], "edges": []}}
        summary = {row["id"]: row["properties"] for row in plan(view, [])["summary"]}
        self.assertEqual(summary["p"], {"history": "held by Cassius Dio"})


FIXTURES = """
CREATE (battle:Entity:Event {id: "chr:entity:test-h-battle", label: "Test battle", status: "provisional"})
CREATE (question:Entity:Question {id: "chr:entity:test-h-question", label: "What was the test commander's aim?",
                                  status: "proposed"})
CREATE (position:Entity:Position {id: "chr:entity:test-h-breakout", label: "He meant to break out",
                                  status: "proposed"})
CREATE (ancient:Entity:Work {id: "chr:entity:test-h-history", label: "Test historian, Test history",
                             shortLabel: "Test history", standing: "primary"})
CREATE (historian:Entity:Person {id: "chr:entity:test-h-historian", label: "Test historian"})
CREATE (study:Entity:Work {id: "chr:entity:test-h-study", label: "Test scholar, Test study",
                           shortLabel: "Test study", standing: "secondary"})
CREATE (review:Entity:Work {id: "chr:entity:test-h-review", label: "Test reviewer, Test reconsideration",
                            shortLabel: "Test reconsideration", standing: "secondary"})
CREATE (author:Assertion {id: "chr:assertion:test-h-author", predicate: "authorOf", status: "accepted",
                          category: "factual"})
CREATE (author)-[:ASSERTION_SUBJECT]->(historian), (author)-[:ASSERTION_OBJECT]->(ancient)
CREATE (about:Assertion {id: "chr:assertion:test-h-about", predicate: "about", status: "proposed",
                         mode: "attributed", category: "interpretive"})
CREATE (about)-[:ASSERTION_SUBJECT]->(question), (about)-[:ASSERTION_OBJECT]->(battle),
       (about)-[:ATTRIBUTED_TO]->(review)
CREATE (answers:Assertion {id: "chr:assertion:test-h-answers", predicate: "answers", status: "proposed",
                           mode: "attributed", category: "interpretive"})
CREATE (answers)-[:ASSERTION_SUBJECT]->(position), (answers)-[:ASSERTION_OBJECT]->(question),
       (answers)-[:ATTRIBUTED_TO]->(review)
CREATE (dio:Assertion {id: "chr:assertion:test-h-history:holds:test-h-breakout:q0000000001", predicate: "holds",
                       status: "proposed", mode: "attributed", category: "interpretive"})
CREATE (dio)-[:ASSERTION_SUBJECT]->(ancient), (dio)-[:ASSERTION_OBJECT]->(position), (dio)-[:ATTRIBUTED_TO]->(review)
CREATE (revived:Assertion {id: "chr:assertion:test-h-study:holds:test-h-breakout:q0000000002", predicate: "holds",
                           status: "proposed", mode: "attributed", category: "interpretive", stance: "adopts",
                           timeEdtf: "1899", timeSourceExpression: "1899", startEarliestJdn: 2414291})
CREATE (revived)-[:ASSERTION_SUBJECT]->(study), (revived)-[:ASSERTION_OBJECT]->(position),
       (revived)-[:ATTRIBUTED_TO]->(review)
CREATE (dominant:Assertion {id: "chr:assertion:test-h-breakout:had-reception:q0000000003", predicate: "hadReception",
                            status: "proposed", mode: "attributed", category: "interpretive", reception: "dominant",
                            timeEdtf: "1899/..", timeSourceExpression: "ever since"})
CREATE (dominant)-[:ASSERTION_SUBJECT]->(position), (dominant)-[:ATTRIBUTED_TO]->(review)
"""


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class PositionProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

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
        self.tx.run(FIXTURES)
        elements = projection(self.tx)["elements"]
        self.nodes = {n["data"]["id"]: n["data"] for n in elements["nodes"] if "test-h" in n["data"]["id"]}
        self.edges = {e["data"]["id"]: e["data"] for e in elements["edges"] if "test-h" in e["data"]["id"]}

    def tearDown(self):
        self.tx.rollback()

    def test_the_question_is_one_hop_from_its_event(self):
        about = self.edges["chr:assertion:test-h-about#interpretive"]
        self.assertEqual((about["source"], about["target"], about["predicate"]),
                         ("chr:entity:test-h-question", "chr:entity:test-h-battle", "about"))

    def test_the_position_carries_its_history_and_timeline(self):
        position = self.nodes["chr:entity:test-h-breakout"]
        self.assertEqual(position["history"], "held by Test historian; Test scholar (1899); dominant from 1899 "
                                              "(according to Test reviewer); as reported by Test reviewer")
        self.assertEqual([(t["name"], t["ancient"], t["stance"]) for t in position["timeline"]],
                         [("Test historian", True, None), ("Test scholar", False, "adopts")])

    def test_a_holds_link_says_who_reports_it(self):
        held = self.edges["chr:assertion:test-h-study:holds:test-h-breakout#interpretive"]
        self.assertEqual(held["attestation"], "reported by Test reviewer")  # named by author
        self.assertIn("stance: adopts", held["voiceLines"][0])


PAGE = ("The ancient writers, with one exception, say that the commander fought to win. Scholar B revived the "
        "exception's view in 1899, that he meant to break out by sea, and it has been the dominant view ever since. "
        "Scholar C rejected it in 1931.")


class HistoriographyConversionTests(unittest.TestCase):
    """A reading's historiography section becomes proposals attributed to the work read (44 §3)."""

    def plan(self, output, **extra):
        from GraphRevised.proposals.historiography import to_historiography
        return to_historiography(output, PAGE, work_id="chr:entity:test-review", locator="p. 608",
                                 scope_ids={"chr:entity:test-battle"},
                                 work_ids={"chr:entity:test-review", "chr:entity:test-history"},
                                 proposed_by="lens-specialist:test/test", model_id=None, prompt_version=None,
                                 inquiry_id=None, **extra)

    def output(self, **changes):
        from GraphRevised.proposals.historiography import HistoriographyOutput
        data = {
            "questions": [{"key": "q1", "question": "What did the commander intend?", "existing_id": "",
                           "about_ids": ["chr:entity:test-battle"],
                           "quotation": "say that the commander fought to win"}],
            "positions": [{"key": "p1", "label": "He meant to break out by sea", "existing_id": "",
                           "question": "q1", "quotation": "that he meant to break out by sea"}],
            "holdings": [
                {"position": "p1", "verb": "holds", "holder_id": "chr:entity:test-history", "holder_name": "",
                 "holder_year": "", "own": False, "quotation": "with one exception", "stance": "", "stance_quotation": "",
                 "time_source_expression": "", "time_quotation": "", "time_edtf": "", "rests_on": ["Hist. 5.12"]},
                {"position": "p1", "verb": "holds", "holder_id": "", "holder_name": "Scholar B", "holder_year": "1899",
                 "own": False, "quotation": "Scholar B revived the exception's view in 1899", "stance": "adopts",
                 "stance_quotation": "revived", "time_source_expression": "1899", "time_quotation": "in 1899",
                 "time_edtf": "1899", "rests_on": []}],
            "receptions": [{"position": "p1", "reception": "dominant",
                            "quotation": "it has been the dominant view ever since",
                            "time_source_expression": "ever since", "time_quotation": "ever since",
                            "time_edtf": ""}],
        } | changes
        return HistoriographyOutput.model_validate(data)

    def test_entities_and_drafts_attributed_to_the_work_read(self):
        plan = self.plan(self.output())
        self.assertEqual([(e["kind"], e["id"]) for e in plan.entities],
                         [("Question", "chr:entity:proposed-question-what-did-the-commander-intend"),
                          ("Position", "chr:entity:proposed-position-he-meant-to-break-out-by-sea")])
        self.assertEqual([d.predicate for d in plan.drafts], ["about", "answers", "holds", "hadReception"])
        self.assertTrue(all(d.mode == "attributed" and d.attributed_to == "chr:entity:test-review"
                            for d in plan.drafts))
        self.assertEqual(plan.refused, [])

    def test_a_named_holder_not_held_is_left_to_the_curator(self):
        plan = self.plan(self.output())
        self.assertEqual([(h["name"], h["year"]) for h in plan.unresolved_holders], [("Scholar B", "1899")])

    def test_each_draft_cites_a_short_transcription_holding_its_quotations(self):
        plan = self.plan(self.output())
        spans = {t["id"]: t["quote"] for t in plan.transcriptions}
        for d in plan.drafts:
            span = spans[d.observation_ids[0]]
            self.assertIn(span, PAGE)
            for q in d.qualifier_quotations:
                self.assertIn(q.text, span)
        received = plan.drafts[-1]
        self.assertEqual((received.reception, received.time.source_expression), ("dominant", "ever since"))

    def test_a_quotation_not_on_the_page_is_refused(self):
        bad = self.output(questions=[{"key": "q1", "question": "What did the commander intend?", "existing_id": "",
                                      "about_ids": ["chr:entity:test-battle"], "quotation": "words not on the page"}])
        plan = self.plan(bad)
        self.assertIn("quotation does not appear verbatim", plan.refused[0]["reason"])

    def test_an_existing_position_is_reused_never_restated(self):
        output = self.output(positions=[{"key": "p1", "label": "", "existing_id": "chr:entity:position-known",
                                         "question": "q1", "quotation": "that he meant to break out by sea"}])
        plan = self.plan(output, existing={"chr:entity:position-known"})
        self.assertEqual([e["kind"] for e in plan.entities], ["Question"])
        self.assertIn(("holds", "chr:entity:position-known"),
                      [(d.predicate, d.object_id) for d in plan.drafts])

    def test_the_general_reader_never_sees_the_historiography_predicates(self):
        from GraphRevised.proposals.passage_reader import predicate_guide
        from GraphRevised.proposals.registry import load_registry
        guide = predicate_guide(load_registry())
        for name in ("about", "answers", "holds", "rejects", "hadReception"):
            self.assertNotIn(f"- {name} (", guide)


class LicensedClaimTests(unittest.TestCase):
    def test_a_lens_claim_cites_the_span_of_the_page_holding_its_quotations(self):
        from GraphRevised.proposals.article_reader import licensed_claim_drafts
        from GraphRevised.proposals.historiography import HistoriographyPlan
        from GraphRevised.proposals.passage_reader import Inquiry, ReaderClaim
        inquiry = Inquiry(id="test", version=1, label="test", subject={"id": "s", "label": "S"}, focus=[],
                          scope=[], guidance=[], source={}, work_id="chr:entity:test-review",
                          narrative_event_id=None, calendar="julian")
        claim = dict(predicate="opposed", subject_id="chr:entity:a", object_id="chr:entity:b",
                     quotation="Scholar C rejected it", rationale="test rationale for a claim", relevance="test", ambiguities=[],
                     role_id="", role_quotation="", time_source_expression="1931", time_quotation="in 1931",
                     time_edtf="", context_id="", context_quotation="")
        plan = HistoriographyPlan()
        refused = licensed_claim_drafts([ReaderClaim(**claim), ReaderClaim(**claim | {"quotation": "not on it at all"})],
                                        PAGE, locator="p. 608", model_id="m", inquiry=inquiry, plan=plan)
        self.assertEqual(len(plan.drafts), 1)
        self.assertEqual(plan.transcriptions[0]["quote"], "Scholar C rejected it in 1931")
        self.assertEqual(plan.drafts[0].observation_ids, (plan.transcriptions[0]["id"],))
        self.assertIn("verbatim", refused[0]["reason"])


STORE_FIXTURES = """
CREATE (:Entity:Event {id: "chr:entity:test-battle", label: "Test battle", status: "provisional"})
CREATE (:Entity:Work {id: "chr:entity:test-review", label: "Test reviewer, Test reconsideration",
                      standing: "secondary", form: "history"})
CREATE (:Entity:Work {id: "chr:entity:test-history", label: "Test historian, Test history",
                      standing: "primary", form: "history"})
"""


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class StoreHistoriographyTests(unittest.TestCase):
    """Storing a page's historiography: everything proposed, the page itself never stored. Rolled back."""

    @classmethod
    def setUpClass(cls):
        PositionProjectionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.driver.close()

    def setUp(self):
        self.tx = self.session.begin_transaction()
        self.tx.run(STORE_FIXTURES)

    def tearDown(self):
        self.tx.rollback()

    def test_transcriptions_entities_and_proposals_are_stored(self):
        from GraphRevised.operations import load_operations
        from GraphRevised.proposals.historiography import store_historiography
        from GraphRevised.proposals.registry import load_registry
        conversion = HistoriographyConversionTests()
        plan = conversion.plan(conversion.output())
        result = store_historiography(self.tx, load_operations(), load_registry(), plan,
                                      work_label="Test reviewer, Test reconsideration", edition_citation="Test 2011",
                                      proposed_by="lens-specialist:test/test", at="2026-11-16T00:00:00+00:00")
        self.assertEqual([(e["kind"], e["created"]) for e in result["entities"]], [("Question", True), ("Position", True)])
        self.assertEqual([(d["predicate"], d["outcome"], d["stored"]) for d in result["drafts"]],
                         [("about", "valid", True), ("answers", "valid", True), ("holds", "valid", True),
                          ("hadReception", "valid", True)], result["drafts"])
        texts = self.tx.run("MATCH (o:SourceObservation)-[:IN_WORK]->(:Work {id: 'chr:entity:test-review'}) "
                            "RETURN o.passageText AS text, o.rights AS rights").data()
        self.assertTrue(texts and all(len(t["text"]) <= 600 and t["text"] in PAGE for t in texts))
        self.assertNotIn(PAGE, [t["text"] for t in texts])  # never the whole page
        claims = self.tx.run("MATCH (a:Assertion)-[:ATTRIBUTED_TO]->(:Work {id: 'chr:entity:test-review'}) "
                             "RETURN a.predicate AS p, a.status AS s, a.reception AS r").data()
        self.assertEqual({c["s"] for c in claims}, {"proposed"})
        self.assertIn("dominant", {c["r"] for c in claims})
        kinds = self.tx.run("MATCH (e:Entity) WHERE e.id IN $ids RETURN e.status AS s, labels(e) AS l",
                            ids=[e["id"] for e in result["entities"]]).data()
        self.assertEqual({r["s"] for r in kinds}, {"proposed"})


if __name__ == "__main__":
    unittest.main()
