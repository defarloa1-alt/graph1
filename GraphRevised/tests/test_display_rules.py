"""The projection's display rules (export/display.py): folds and hints that mark, never remove."""

import unittest

from GraphRevised.export import display


def node(id, label, kind="Event", description=None, facts=()):
    return {"data": {"id": id, "label": label, "fullLabel": label, "kind": kind, "description": description,
                     "facts": list(facts)}}


def edge(source, target, predicate, category="factual", status="proposed"):
    return {"data": {"id": f"{source}>{predicate}>{target}#{category}", "source": source, "target": target,
                     "predicate": predicate, "category": category, "status": status}}


def run(nodes, edges, standing=None):
    elements = display.apply({"nodes": nodes, "edges": edges}, standing or {})
    return ({n["data"]["id"]: n["data"] for n in elements["nodes"]},
            {e["data"]["id"]: e["data"] for e in elements["edges"]})


class PartsThroughParts(unittest.TestCase):
    def setUp(self):
        self.nodes = [node("battle", "Battle"), node("phase", "Phase"), node("moment", "Moment"),
                      node("loose", "Loose moment")]

    def test_a_moment_in_a_phase_folds_its_line_to_the_battle(self):
        nodes, edges = run(self.nodes, [edge("moment", "battle", "partOf"), edge("moment", "phase", "partOf"),
                                        edge("phase", "battle", "partOf"), edge("loose", "battle", "partOf")])
        folded = edges["moment>partOf>battle#factual"]
        self.assertEqual((folded["fold"], folded["foldVia"]), ("via-part", "phase"))
        self.assertNotIn("fold", edges["moment>partOf>phase#factual"])
        self.assertNotIn("fold", edges["phase>partOf>battle#factual"])
        self.assertNotIn("fold", edges["loose>partOf>battle#factual"], "a moment in no phase keeps its line")
        self.assertEqual(nodes["battle"]["folded"], {"via-part": 1})

    def test_nothing_is_removed(self):
        _, edges = run(self.nodes, [edge("moment", "battle", "partOf"), edge("moment", "phase", "partOf"),
                                    edge("phase", "battle", "partOf")])
        self.assertEqual(len(edges), 3)

    def test_a_rejected_route_does_not_fold(self):
        _, edges = run(self.nodes, [edge("moment", "battle", "partOf"),
                                    edge("moment", "phase", "partOf", status="rejected"),
                                    edge("phase", "battle", "partOf")])
        self.assertNotIn("fold", edges["moment>partOf>battle#factual"])


class DistinctBesidePart(unittest.TestCase):
    def test_distinct_from_folds_when_the_pair_is_also_part_of(self):
        nodes = [node("battle", "Battle"), node("war", "War"), node("other", "Other battle")]
        _, edges = run(nodes, [edge("battle", "war", "partOf"), edge("war", "battle", "distinctFrom"),
                               edge("battle", "other", "distinctFrom")])
        self.assertEqual(edges["war>distinctFrom>battle#factual"]["fold"], "part-says-distinct")
        self.assertNotIn("fold", edges["battle>distinctFrom>other#factual"])


class ReferenceWorks(unittest.TestCase):
    def test_tertiary_works_fold_into_a_count_and_works_carry_their_standing(self):
        nodes = [node("alexandria", "Alexandria", "Place"), node("enc", "Encyclopedia", "Work"),
                 node("enc2", "Lexicon", "Work"), node("hale", "Hale, Famous Sea Fights", "Work")]
        data, edges = run(nodes, [edge("alexandria", "enc", "describedBy"), edge("alexandria", "enc2", "describedBy"),
                                  edge("alexandria", "hale", "describedBy")],
                          {"enc": "tertiary", "enc2": "tertiary", "hale": "secondary"})
        self.assertEqual(data["alexandria"]["referenceWorks"], 2)
        self.assertEqual(edges["alexandria>describedBy>enc#factual"]["fold"], "reference-work")
        self.assertNotIn("fold", edges["alexandria>describedBy>hale#factual"])
        self.assertEqual((data["hale"]["standing"], data["hale"]["standingWords"]), ("secondary", "modern"))
        self.assertEqual(data["enc"]["standingWords"], "reference")


class KindOfStatement(unittest.TestCase):
    def test_lines_are_counted_by_category_and_fiction_only_entities_are_marked(self):
        nodes = [node("battle", "Battle"), node("virgil-moment", "The fleets clash"), node("antony", "Antony", "Person")]
        data, _ = run(nodes, [edge("virgil-moment", "battle", "partOf", "imaginative"),
                              edge("antony", "battle", "participatedIn"),
                              edge("antony", "battle", "commanded", "imaginative")])
        self.assertTrue(data["virgil-moment"]["imaginedOnly"])
        self.assertFalse(data["antony"]["imaginedOnly"])
        self.assertEqual(data["battle"]["lines"], {"imaginative": 2, "factual": 1})


class NameHints(unittest.TestCase):
    def test_two_battles_of_one_name_are_told_apart_by_year(self):
        a = node("actium", "Battle of Actium", description="31 BCE decisive confrontation",
                 facts=[{"predicate": "occurred", "sentence": "Battle of Actium occurred", "times": ["2 September 31 BCE"]}])
        b = node("actium-435", "Battle of Actium", description="battle of 435 BC between Corinth and Corcyra")
        data, _ = run([a, b, node("lone", "Nicopolis", "Place")], [])
        self.assertEqual(data["actium"]["hint"], "2 September 31 BCE")
        self.assertEqual(data["actium-435"]["hint"], "435 BC")
        self.assertNotIn("hint", data["lone"])

    def test_different_kinds_are_told_apart_by_kind(self):
        data, _ = run([node("period", "Roman Empire", "Period"), node("state", "Roman Empire", "Polity")], [])
        self.assertEqual((data["period"]["hint"], data["state"]["hint"]), ("period", "state"))

    def test_people_fall_back_to_their_description_and_never_to_a_code(self):
        data, _ = run([node("fulvia", "Fulvia", "Person", "wife of Mark Antony; died 40 BC"),
                       node("fulvia-q1", "Fulvia", "Person", facts=[
                           {"predicate": "born", "sentence": "Fulvia was born", "times": ["100 BCE – 1 BCE"]},
                           {"predicate": "died", "sentence": "Fulvia died", "times": ["39 BCE"]}]),
                       node("fulvia-q2", "Fulvia", "Person")], [])
        self.assertEqual(data["fulvia"]["hint"], "wife of Mark Antony")
        self.assertEqual(data["fulvia-q1"]["hint"], "died 39 BCE", "a span is too vague; the verb says what the year is")
        self.assertEqual(data["fulvia-q2"]["hint"], "another person")


class SubjectAccess(unittest.TestCase):
    def test_a_moment_reaches_the_battle_heading_through_its_phase(self):
        battle = node("battle", "Battle of Actium")
        battle["data"]["authority"] = [{"system": "LCSH", "identifier": "sh85000736",
                                        "label": "Actium, Battle of, 31 B.C. (LCSH sh85000736)"},
                                       {"system": "Wikidata", "identifier": "Q1", "label": "Battle of Actium in Wikidata"}]
        nodes = [battle, node("phase", "The fleets deploy"), node("moment", "Agrippa restrains Caesar"),
                 node("verse", "The fleets clash")]
        data, _ = run(nodes, [edge("moment", "phase", "partOf"), edge("phase", "battle", "partOf"),
                              edge("verse", "battle", "partOf", "imaginative")])
        self.assertEqual(data["moment"]["subjectAccess"],
                         [{"heading": "Actium, Battle of, 31 B.C. (LCSH sh85000736)", "via": "battle",
                           "viaLabel": "Battle of Actium"}])
        self.assertEqual(data["phase"]["subjectAccess"][0]["via"], "battle")
        self.assertNotIn("subjectAccess", data["battle"], "its own heading is not inherited")
        self.assertNotIn("subjectAccess", data["verse"], "an imagined part inherits nothing")


class Descriptions(unittest.TestCase):
    def test_a_description_that_is_only_a_link_is_not_shown(self):
        data, _ = run([node("s", "Actium, Battle of", "Concept", "http://id.loc.gov/authorities/subjects/sh85000631"),
                       node("t", "Nicopolis", "Place", "city founded by Octavian, see https://example.org")], [])
        self.assertIsNone(data["s"]["description"])
        self.assertIsNotNone(data["t"]["description"])


if __name__ == "__main__":
    unittest.main()
