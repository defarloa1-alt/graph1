"""The scene builder's code check (scenes/build_scene.py, D-179): offline, on synthetic evidence."""

import unittest

from GraphRevised.scenes.build_scene import assemble, check, narration_input

EV = {
    "event": "chr:entity:test-war", "label": "Test War", "phases": ["march", "siege"],
    "passages": [
        {"loc": "Annals 1.1", "obs": "o1", "work": "Annals", "workId": "chr:entity:annals", "url": None,
         "text": "The general marched from Alba to Roma with three legions.", "events": []},
        {"loc": "Annals 1.2", "obs": "o2", "work": "Annals", "workId": "chr:entity:annals", "url": None,
         "text": "He laid siege to the city for many days.", "events": []},
    ],
    "places": {"p:alba": {"id": "p:alba", "label": "Alba Longa", "names": ["Alba", "Alba Longa"], "lonLat": [12.6, 41.7],
                          "gazetteer": "Pleiades 1", "status": "accepted"},
               "p:roma": {"id": "p:roma", "label": "Rome", "names": ["Roma", "Rome"], "lonLat": [12.5, 41.9],
                          "gazetteer": "Pleiades 2", "status": "accepted"},
               "p:veii": {"id": "p:veii", "label": "Veii", "names": ["Veii"], "lonLat": [12.4, 42.0],
                          "gazetteer": "Pleiades 3", "status": "proposed"}},
    "units": {"u:general": {"id": "u:general", "label": "The general", "kind": "Person"}},
}


def q(loc, words):
    return {"passage": loc, "quotation": words}


def stmt(text, basis="sourced", quotes=(), note=None):
    return {"text": text, "basis": basis, "quotes": list(quotes), "note": note}


def leg(frm, to, basis="sourced", statement=1):
    return {"unit": "u:general", "side": None, "from_place": frm, "to_place": to, "via": [], "basis": basis, "statement": statement}


def step(phase, statements, legs=(), disagreements=()):
    return {"phase": phase, "title": "t", "time_words": "spring", "statements": list(statements), "legs": list(legs),
            "disagreements": list(disagreements)}


GOOD = {"place_names": {"p:roma": "Roma"}, "steps": [
    step("march", [stmt("The general marches from Alba to Roma with three legions.",
                        quotes=[q("Annals 1.1", "marched from Alba to Roma with three legions")])],
         [leg("p:alba", "p:roma")]),
    step("siege", [stmt("He besieges the city.", quotes=[q("Annals 1.2", "He laid siege to the city")]),
                   stmt("He probably went on to Veii.", "inferred", note="no passage names Veii; joined from the siege")],
         [leg("p:roma", "p:veii", "inferred", 2)])]}


class SceneBuilderCheckTests(unittest.TestCase):
    def test_a_sourced_draft_passes(self):
        self.assertEqual(check(GOOD, EV)["problems"], [])

    def test_a_quotation_must_be_word_for_word(self):
        draft = {"place_names": {}, "steps": [step("march", [stmt("He marches.", quotes=[q("Annals 1.1", "marched swiftly from Alba")])])]}
        self.assertTrue(any("not word for word" in p for p in check(draft, EV)["problems"]))

    def test_a_number_must_be_in_the_quotations(self):
        draft = {"place_names": {}, "steps": [step("march", [stmt("He marches with four legions.", quotes=[q("Annals 1.1", "marched from Alba")])])]}
        self.assertTrue(any("['four']" in p for p in check(draft, EV)["problems"]))

    def test_a_sourced_leg_needs_a_passage_naming_both_ends(self):
        draft = {"place_names": {}, "steps": [step("siege", [stmt("He besieges the city.", quotes=[q("Annals 1.2", "He laid siege")])],
                                                   [leg("p:roma", "p:veii")])]}
        problems = " | ".join(check(draft, EV)["problems"])
        self.assertIn("names Rome", problems)
        self.assertIn("names Veii", problems)

    def test_legs_only_between_listed_places_and_phases_in_order(self):
        draft = {"place_names": {}, "steps": [
            step("siege", [stmt("He besieges the city.", quotes=[q("Annals 1.2", "He laid siege")])]),
            step("march", [stmt("He marches.", quotes=[q("Annals 1.1", "marched")])], [leg("p:alba", "p:nowhere", "inferred")])]}
        problems = " | ".join(check(draft, EV)["problems"])
        self.assertIn("not in the PLACES list", problems)
        self.assertIn("keep the phases' order", problems)

    def test_an_inference_says_what_from(self):
        draft = {"place_names": {}, "steps": [step("march", [stmt("He probably hurried.", "inferred")])]}
        self.assertTrue(any("no note" in p for p in check(draft, EV)["problems"]))

    def test_the_scene_is_shape_7_with_ids_names_of_the_time_and_a_narration_input(self):
        scene = assemble(GOOD, EV, {"id": "chr:storyboard:test-war"}, {"order": 1, "title": "The march"}, "m", [{"model": "m"}])
        self.assertEqual(scene["id"], "chr:scene:test-war-seg1")
        self.assertEqual(scene["steps"][0]["statements"][0]["id"], "chr:scene:test-war-seg1#1.1")
        self.assertIn("Roma", scene["places"])  # the passages' name, with the held label kept
        self.assertEqual(scene["places"]["Roma"]["heldAs"], "Rome")
        self.assertEqual(scene["steps"][1]["statements"][1]["by"], "the scene builder (scenes/build_scene.py with m)")
        self.assertEqual(scene["steps"][0]["statements"][0]["voices"][0]["observation"], "o1")
        self.assertIn("contentHash", scene)
        ni = narration_input(scene)
        self.assertNotIn("legs", ni["steps"][0])
        self.assertEqual(ni["steps"][0]["statements"][0]["voices"][0], {"accordingTo": "Annals", "locator": "Annals 1.1",
                                                                        "quotation": "marched from Alba to Roma with three legions"})


if __name__ == "__main__":
    unittest.main()
