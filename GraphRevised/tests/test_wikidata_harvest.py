"""First-contact harvest, increment 1: Wikidata dates by precision, statement classes, Year tethers. Offline."""

import json
import os
import unittest
from pathlib import Path

from GraphRevised.harvest.wikidata_harvest import classify, load_rules, tether
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.temporal import TimeValueError, wikidata_time
from GraphRevised.proposals.validator import validate

JULIAN = "http://www.wikidata.org/entity/Q1985786"
PAYLOAD = Path(__file__).resolve().parents[1] / "phase-5-source" / "wikidata-Q51673-r2553883228.json"


def time(value, precision):
    return {"time": value, "precision": precision, "calendarmodel": JULIAN}


class WikidataTimeTests(unittest.TestCase):
    def test_bce_years_are_historical_and_become_astronomical(self):
        self.assertEqual(wikidata_time(time("-0083-00-00T00:00:00Z", 9)), ("-0082", "julian"))
        self.assertEqual(wikidata_time(time("-0083-01-14T00:00:00Z", 11)), ("-0082-01-14", "julian"))
        self.assertEqual(wikidata_time(time("+0014-08-00T00:00:00Z", 10)), ("0014-08", "julian"))

    def test_decades_and_centuries_become_the_years_they_cover(self):
        self.assertEqual(wikidata_time(time("-0050-00-00T00:00:00Z", 8)), ("-0058/-0049", "julian"))  # 59-50 BCE
        self.assertEqual(wikidata_time(time("-0044-00-00T00:00:00Z", 8)), ("-0048/-0039", "julian"))  # not -50..-41
        self.assertEqual(wikidata_time(time("-0083-00-00T00:00:00Z", 7)), ("-0099/0000", "julian"))   # 100-1 BCE
        self.assertEqual(wikidata_time(time("+0014-00-00T00:00:00Z", 7)), ("0001/0100", "julian"))

    def test_a_date_known_to_its_century_is_sometime_within_it(self):
        from GraphRevised.adapters.wikidata_statements import assemble_time

        century = assemble_time({"point": time("-0083-00-00T00:00:00Z", 7)})
        self.assertEqual((century["edtf"], century["mode"]), ("-0099/0000", "within"))
        self.assertEqual(tether(century["edtf"], century["calendar"], century["mode"]),
                         {"how": "within", "years": [-100, -1]})  # two Year links, not a hundred
        self.assertEqual(assemble_time({"point": time("-0083-00-00T00:00:00Z", 9)})["mode"], "during")

    def test_coarse_or_impossible_values_are_refused(self):
        with self.assertRaises(TimeValueError):
            wikidata_time(time("-0500-00-00T00:00:00Z", 6))
        with self.assertRaises(TimeValueError):
            wikidata_time(time("+0000-00-00T00:00:00Z", 9))
        with self.assertRaises(TimeValueError):
            wikidata_time({"time": "-0083-00-00T00:00:00Z", "precision": 9, "calendarmodel": "Q0"})


class TetherTests(unittest.TestCase):
    def test_a_point_or_span_is_during_and_a_window_is_within(self):
        self.assertEqual(tether("-0039/-0031", "julian", "during"), {"how": "during", "years": [-40, -32], "count": 9})
        self.assertEqual(tether("-0067/-0049", "julian", "within"), {"how": "within", "years": [-68, -50]})

    def test_long_spans_tether_by_their_ends_and_outside_dates_are_flagged(self):
        self.assertEqual(tether("-0508/-0026", "julian", "during")["how"], "start and end")
        self.assertEqual(tether("-2999", "julian", "during"), {"how": "outside the backbone", "years": [-3000]})
        self.assertEqual(tether("-0063/..", "julian", "during"), {"how": "start only", "years": [-64]})


class ClassifyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        entity = json.loads(PAYLOAD.read_bytes())["entities"]["Q51673"]
        cls.statements, cls.deprecated = classify(entity, load_rules(), load_registry())

    def pick(self, pid):
        return [s for s in self.statements if s.pid == pid]

    def test_every_statement_has_a_kind_and_deprecated_ones_are_left_out(self):
        kinds = {s.kind for s in self.statements}
        self.assertLessEqual(kinds, {"identifier", "attribute", "dated", "relationship", "housekeeping"})
        self.assertGreater(self.deprecated, 0)
        self.assertTrue(all(s.rank != "deprecated" for s in self.statements))

    def test_dates_are_dated_claims_not_attributes(self):
        born = self.pick("P569")
        self.assertTrue(born and all(s.kind == "dated" and s.event == "born" for s in born))
        self.assertIn("preferred", {s.rank for s in born})

    def test_classifying_items_are_attributes_and_identifiers_are_crosswalk(self):
        self.assertEqual({s.kind for s in self.pick("P21")}, {"attribute"})
        self.assertEqual({s.kind for s in self.pick("P6863")}, {"identifier"})
        self.assertEqual({s.kind for s in self.pick("P373")}, {"housekeeping"})

    def test_relationships_carry_mapped_qualifiers(self):
        spouses = self.pick("P26")
        self.assertTrue(all(s.kind == "relationship" and s.predicates == [("spouseOf", "forward")] for s in spouses))
        windows = [s for s in spouses if s.time and s.time["mode"] == "within"]
        self.assertTrue(windows, "an earliest/latest pair is an uncertain window")
        self.assertTrue(any("P1545" in s.carried and "P1534" in s.carried for s in spouses))
        offices = [s for s in self.pick("P39") if s.carried.get("P1706")]
        self.assertTrue(offices, "a colleague (together with) is carried")


if __name__ == "__main__":
    unittest.main()


class StatementClaimTests(unittest.TestCase):
    """Wikidata statements with dates and qualifiers become valid claims, compared rather than deferred."""

    @classmethod
    def setUpClass(cls):
        from GraphRevised.adapters.wikidata_statements import statement_observation
        from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
        from GraphRevised.tests.test_proposals_offline import FakeReader, entity

        cls.registry = load_registry()
        cls.drafts_from_observation = staticmethod(drafts_from_observation)
        claims = json.loads(PAYLOAD.read_bytes())["entities"]["Q51673"]["claims"]
        cls.antony = entity("chr:entity:test-antony", "Person", "Q51673")
        cls.octavia = entity("chr:entity:test-octavia", "Person", "Q229483")
        cls.fadia = entity("chr:entity:test-fadia", "Person", "Q11923347")

        def observe(pid, pick):
            statement = next(c for c in claims[pid] if pick(c))
            return statement_observation(PAYLOAD, statement["id"], label="test", short_label="test",
                                         retrieved_at="2026-10-13T00:00:00Z")

        cls.born = observe("P569", lambda c: c.get("rank") == "preferred")
        cls.married = observe("P26", lambda c: c["mainsnak"]["datavalue"]["value"]["id"] == "Q229483")
        cls.window = observe("P26", lambda c: c["mainsnak"]["datavalue"]["value"]["id"] == "Q11923347")
        cls.reader = FakeReader([cls.antony, cls.octavia, cls.fadia], [cls.born, cls.married, cls.window])

    def proposed(self, observation):
        result = self.drafts_from_observation(observation, self.reader, self.registry)
        self.assertEqual(len(result.drafts), 1, result.unresolved)
        return result.drafts[0]

    def test_a_birth_date_is_a_dated_claim(self):
        self.assertIsNone(self.born["objectExternalId"])
        draft = self.proposed(self.born)
        self.assertEqual((draft.predicate, draft.object_id, draft.time.edtf), ("born", None, "-0082"))
        result = validate(draft, self.reader, self.registry)
        self.assertEqual(result.outcome.value, "valid", result.reasons)

    def test_a_marriage_carries_its_span_and_qualifiers(self):
        self.assertEqual(json.loads(self.married["statementQualifiers"])["P1534"], ["Q93190"])  # ended by divorce
        draft = self.proposed(self.married)
        self.assertEqual((draft.predicate, draft.time.edtf, draft.time.mode), ("spouseOf", "-0039/-0031", "during"))
        self.assertEqual(validate(draft, self.reader, self.registry).outcome.value, "valid")

    def test_an_uncertain_window_is_a_within_claim(self):
        draft = self.proposed(self.window)
        self.assertEqual((draft.time.edtf, draft.time.mode), ("-0067/-0049", "within"))
        self.assertEqual(validate(draft, self.reader, self.registry).outcome.value, "valid")

    def test_a_time_the_statement_does_not_state_is_refused(self):
        draft = self.proposed(self.married)
        wrong = draft.model_copy(update={"time": draft.time.model_copy(update={"edtf": "-0040/-0031"})})
        result = validate(wrong, self.reader, self.registry)
        self.assertEqual(result.outcome.value, "invalid")
        self.assertTrue(any("not the time" in reason for reason in result.reasons))


class KindTests(unittest.TestCase):
    def test_kinds_come_from_instance_of_and_unknown_classes_wait(self):
        from GraphRevised.harvest.apply import kind_of

        def entity(*classes, deprecated=()):
            claims = [{"mainsnak": {"datavalue": {"value": {"id": c}}}, "rank": "normal"} for c in classes]
            claims += [{"mainsnak": {"datavalue": {"value": {"id": c}}}, "rank": "deprecated"} for c in deprecated]
            return {"claims": {"P31": claims}}

        rules = load_rules()
        self.assertEqual(kind_of(entity("Q5"), rules), "Person")
        self.assertEqual(kind_of(entity("Q1200957", "Q515"), rules), "Place")  # tourist destination and city
        self.assertEqual(kind_of(entity("Q4164871", "Q5"), rules), "Person")   # priority, not order
        self.assertIsNone(kind_of(entity("Q1307214"), rules))                  # form of government: the agent's call
        self.assertIsNone(kind_of(entity(deprecated=("Q5",)), rules))
        self.assertTrue(set(rules["kinds"]) <= set(rules["kindPriority"]))


class FederationSystemTests(unittest.TestCase):
    def test_a_federation_may_name_its_system_by_prefix(self):
        from GraphRevised.harvest.apply import federation_system

        rules = {"federations": {"P1": "Plain", "P2": {"byPrefix": {"s": "Short", "sh": "Long"}, "default": "Other"}}}
        self.assertEqual(federation_system(rules, "P1", "anything"), "Plain")
        self.assertEqual(federation_system(rules, "P2", "sh123"), "Long")  # the longest prefix wins
        self.assertEqual(federation_system(rules, "P2", "s123"), "Short")
        self.assertEqual(federation_system(rules, "P2", "x123"), "Other")
        self.assertIsNone(federation_system(rules, "P3", "x123"))

    def test_one_identifier_property_holding_two_files_is_split_by_prefix(self):
        from GraphRevised.harvest.apply import federation_system

        rules = load_rules()
        self.assertIsInstance(rules["federations"]["P244"], dict)
        systems = {federation_system(rules, "P244", value) for value in ("sh85000001", "n80000001", "nr2000000001")}
        self.assertEqual(len(systems), 2, "subject headings and names are different systems")


AUTHORITY_FIXTURES = """
CREATE (e:Entity {id: "chr:entity:test-auth-event", kind: "Event", label: "Test event", status: "provisional"})
CREATE (s:Subject {id: "chr:subject:test-auth", label: "Test subject", status: "provisional"})
CREATE (heading:AuthorityRecord {id: "chr:authority:test-headings:x1", system: "Test headings", identifier: "x1",
                                 label: "Heading words (x1)"})
CREATE (s)-[:HAS_AUTHORITY_RECORD {role: "subject_access", relation: "closeMatch", status: "accepted"}]->(heading)
CREATE (dup:AuthorityRecord {id: "chr:authority:test-library:x1", system: "Test library", identifier: "x1",
                             label: "Test event in Test library (x1)"})
CREATE (e)-[:HAS_AUTHORITY_RECORD {role: "crosswalk", relation: "closeMatch", status: "accepted"}]->(dup)
CREATE (name:AuthorityRecord {id: "chr:authority:test-library:y1", system: "Test library", identifier: "y1",
                              label: "Test event in Test library (y1)"})
CREATE (e)-[:HAS_AUTHORITY_RECORD {role: "crosswalk", relation: "closeMatch", status: "accepted"}]->(name)
"""
EVENT = "chr:entity:test-auth-event"
HEADING, DUPLICATE, NAME = "chr:authority:test-headings:x1", "chr:authority:test-library:x1", "chr:authority:test-library:y1"


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "NEO4J_PASSWORD not set")
class AuthorityOperationTests(unittest.TestCase):
    """Linking without relabelling, renaming a system, retiring a duplicate. Rolled back; synthetic fixtures."""

    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        from GraphRevised.operations import load_operations

        cls.operations = load_operations()
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
        self.tx.run(AUTHORITY_FIXTURES)

    def tearDown(self):
        self.tx.rollback()

    def op(self, name, params):
        return self.tx.run(self.operations[name], params).data()

    def record(self, record_id):
        return self.tx.run(
            "MATCH (a:AuthorityRecord {id: $id}) "
            "RETURN a.label AS label, a.system AS system, a.formerId AS formerId, a.mergedIds AS mergedIds, "
            "COUNT { (a)<-[:HAS_AUTHORITY_RECORD]-() } AS links", id=record_id).single()

    def test_linking_an_existing_record_keeps_its_words_and_records_the_statement(self):
        link = {"entityId": EVENT, "system": "Test headings", "identifier": "x1", "role": "crosswalk",
                "relation": "closeMatch", "linkStatus": "accepted", "statementRank": "preferred",
                "statementReferences": 2}
        self.assertTrue(self.op("link_authority", link))
        row = self.tx.run("MATCH (:Entity {id: $event})-[l:HAS_AUTHORITY_RECORD]->(:AuthorityRecord {id: $heading}) "
                          "RETURN l.role AS role, l.statementRank AS rank, l.statementReferences AS refs",
                          event=EVENT, heading=HEADING).single()
        self.assertEqual((row["role"], row["rank"], row["refs"]), ("crosswalk", "preferred", 2))
        self.assertEqual(self.record(HEADING)["label"], "Heading words (x1)")
        self.assertEqual(self.op("link_authority", {**link, "identifier": "missing"}), [], "never creates a record")

    def test_a_duplicate_is_retired_into_the_record_that_stays(self):
        rows = self.op("merge_authority_into", {"id": DUPLICATE, "targetId": HEADING})
        self.assertEqual(rows[0]["moved"], 1)
        row = self.record(HEADING)
        self.assertEqual((row["label"], row["mergedIds"], row["links"]), ("Heading words (x1)", [DUPLICATE], 2))
        self.assertIsNone(self.record(DUPLICATE))

    def test_a_record_with_another_identifier_or_other_relationships_is_not_retired(self):
        self.assertEqual(self.op("merge_authority_into", {"id": NAME, "targetId": HEADING}), [])
        self.tx.run("MATCH (a {id: $id}) CREATE (:Assertion {id: 'chr:assertion:test-auth'})-[:ASSERTION_OBJECT]->(a)",
                    id=DUPLICATE)
        self.assertEqual(self.op("merge_authority_into", {"id": DUPLICATE, "targetId": HEADING}), [])

    def test_renaming_a_system_keeps_the_former_id_and_refuses_a_clash(self):
        rename = {"id": NAME, "newId": "chr:authority:test-names:y1", "system": "Test names",
                  "label": "Test event in Test names (Test names y1)", "shortLabel": "Test names: Test event"}
        self.assertTrue(self.op("rename_authority_system", rename))
        row = self.record("chr:authority:test-names:y1")
        self.assertEqual((row["system"], row["formerId"], row["links"]), ("Test names", NAME, 1))
        clash = {**rename, "id": DUPLICATE, "newId": "chr:authority:test-headings:x1b", "system": "Test headings"}
        self.assertEqual(self.op("rename_authority_system", clash), [], "x1 already has a Test headings record")
