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


NETWORKS = {"hub": "Hub", "order": ["Coins", "Open hub"],
            "systems": {"Hub": {"network": "Open hub", "link": "https://hub.test/{id}", "hosts": ["hub.test"]},
                        "Mint": {"network": "Coins", "link": "https://mint.test/{id}", "hosts": ["mint.test"]},
                        "Atlas": {"network": "Ancient places", "link": "https://atlas.test/{id}", "hosts": ["atlas.test"]},
                        "Folk": {"network": "People", "link": "https://folk.test/author/{id}",
                                 "linkByKind": {"Place": "https://folk.test/place/{id}"}, "hosts": ["folk.test"]}},
            "expected": {"Person": ["Folk"], "Place": ["Atlas"]}}


def authority(system, identifier, role="crosswalk", status="accepted", uri=None):
    return {"system": system, "identifier": identifier, "label": f"{system} record ({identifier})", "role": role,
            "status": status, "relation": "closeMatch", "others": 0, "sourceUri": uri}


class Elsewhere(unittest.TestCase):
    def run_rule(self, data):
        nodes = {data["id"]: data}
        display.elsewhere(nodes, NETWORKS)
        return data.get("elsewhere")

    def test_each_record_says_how_it_is_held_in_the_profile_order(self):
        data = {"id": "p", "kind": "Person", "authority": [
            authority("Hub", "H1", role="entity_identity", uri="https://hub.test/H1.json"),
            authority("Mint", "m1", uri="https://hub.test/H1.json"),
            authority("Mint", "m2", uri="https://mint.test/m2"),
            authority("Mint", "m3", status="proposed", uri="https://mint.test/m3")]}
        ew = self.run_rule(data)
        self.assertEqual([g["network"] for g in ew["networks"]], ["Coins", "Open hub", "People"])
        coins = {r["identifier"]: r for r in ew["networks"][0]["rows"]}
        self.assertEqual(coins["m1"]["words"], "per Hub")
        self.assertEqual(coins["m2"]["words"], "checked there")
        self.assertEqual(coins["m3"]["words"], "proposed")
        self.assertEqual(coins["m2"]["url"], "https://mint.test/m2")
        self.assertEqual(ew["networks"][1]["rows"][0]["words"], "its identity · close match")
        self.assertEqual(ew["networks"][2]["rows"], [{"system": "Folk", "missing": True, "words": "none held",
                                                     "why": "No record held here yet."}])
        self.assertEqual(ew["summary"], "4 records in 2 networks, 1 per Hub only.")

    def test_a_place_reads_its_gazetteer_and_its_kind_link(self):
        data = {"id": "x", "kind": "Place", "authority": [authority("Folk", "7", uri="https://folk.test/7")],
                "gazetteer": [{"system": "Atlas", "identifier": "42", "label": "Old town", "status": "accepted",
                               "basis": "Atlas 42 (crosswalk)"}]}
        rows = {r["system"]: r for g in self.run_rule(data)["networks"] for r in g["rows"]}
        self.assertEqual((rows["Atlas"]["label"], rows["Atlas"]["words"]), ("Old town (Atlas 42)", "its location"))
        self.assertEqual(rows["Folk"]["url"], "https://folk.test/place/7")
        self.assertNotIn("missing", rows["Atlas"], "a gazetteer record is held, not missing")

    def test_a_crosswalk_the_gazetteer_holds_is_its_location(self):
        data = {"id": "x", "kind": "Place", "authority": [authority("Atlas", "42", uri="https://hub.test/Q1.json")],
                "gazetteer": [{"system": "Atlas", "identifier": "42", "label": "Old town", "status": "accepted"}]}
        rows = [r for g in self.run_rule(data)["networks"] for r in g["rows"] if r["system"] == "Atlas"]
        self.assertEqual([(r["label"], r["words"]) for r in rows], [("Atlas record (42)", "its location")])


def voice(*sources):
    return {"accordingTo": sources[0], "quotes": [{"source": s} for s in sources[1:]]}


class EvidenceKinds(unittest.TestCase):
    def setUp(self):
        self.works = {"Coin series": {"form": "coinage"}, "Old history": {"standing": "primary"},
                      "New study": {"standing": "secondary"}, "A play": {"form": "play", "standing": "primary"}}

    def kinds(self, *voices):
        return display.evidence_of({"voices": list(voices)}, self.works, frozenset({"play", "poem"}))

    def test_two_kinds_agreeing_are_named(self):
        ev = self.kinds(voice("Old history"), voice("New study", "Coin series"))
        self.assertEqual([k["kind"] for k in ev["kinds"]], ["text", "coin"])
        self.assertEqual(ev["sentence"], "2 independent kinds of evidence: ancient text and coin.")
        self.assertEqual(ev["also"], ["1 modern study"])
        self.assertEqual(ev["missing"], ["inscription"])

    def test_any_creative_form_is_imagined_never_a_text(self):
        ev = self.kinds(voice("A play"))
        self.assertEqual(ev["kinds"], [])
        self.assertEqual(ev["also"], ["1 imaginative work"])
        self.assertEqual(ev["sentence"], "No ancient evidence held: only later writers say it.")


if __name__ == "__main__":
    unittest.main()
