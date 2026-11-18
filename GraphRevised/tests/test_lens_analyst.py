"""The lens analysts' deterministic parts, without a model call or the graph."""

import unittest

from GraphRevised.discovery.lens_analyst import (
    Finding, Gap, PredicateNeed, SpecialistOutput, check, load_grounding, load_lenses, locator_of, overlaps,
)

CLAIMS = {"c1": "chr:assertion:one", "c2": "chr:assertion:two"}
WORKS_REFS = {"w1": "chr:entity:plutarch"}
WORKS = [{"id": "chr:entity:plutarch", "read": ["63.1", "64.2"]}]
REGISTRY = {"commanded", "participatedIn"}


def gap(question, work_ref=None, locator=None, predicate=None, entities=(), kind="unread passage"):
    return Gap(question=question, why="test", kind=kind, work_ref=work_ref, source=None, locator=locator,
               predicate=predicate, entities=list(entities))


def output(*gaps, claims=("c1",), needs=()):
    return SpecialistOutput(
        findings=[Finding(question="q", answer="a", claims=list(claims), strength="thin")],
        gaps=list(gaps), predicate_needs=list(needs), note="ours")


class LensTests(unittest.TestCase):
    def test_refs_resolve_and_invented_refs_are_reported(self):
        reading = check("military", output(gap("g", work_ref="w9"), claims=("c1", "[c2]", "c7")),
                        CLAIMS, WORKS_REFS, WORKS, REGISTRY)
        self.assertEqual(reading["findings"][0]["claims"], ["chr:assertion:one", "chr:assertion:two"])
        self.assertEqual(sorted(reading["invented"]), ["c7", "w9"])

    def test_a_gap_at_a_locator_already_read_is_marked(self):
        reading = check("military", output(gap("read", "w1", "63.1"), gap("unread", "w1", "70.1")),
                        CLAIMS, WORKS_REFS, WORKS, REGISTRY)
        self.assertEqual([g["alreadyRead"] for g in reading["gaps"]], [True, False])
        self.assertEqual([g["ref"] for g in reading["gaps"]], ["military:g1", "military:g2"])

    def test_predicate_needs_already_in_the_registry_are_marked(self):
        need = PredicateNeed(name="commanded", definition="d", subject_kinds=["Person"], object_kinds=["Group"],
                             example="e")
        new = need.model_copy(update={"name": "financedBy"})
        reading = check("economic", output(needs=(need, new)), CLAIMS, WORKS_REFS, WORKS, REGISTRY)
        self.assertEqual([n["exists"] for n in reading["predicate_needs"]], [True, False])

    def test_overlaps_are_across_lenses_only(self):
        military = check("military", output(gap("a", "w1", "70.1"), gap("b", predicate="opposed",
                                                                        entities=("Antony", "Octavian"))),
                         CLAIMS, WORKS_REFS, WORKS, REGISTRY)
        political = check("political", output(gap("c", "w1", "70.1"), gap("d", predicate="opposed",
                                                                          entities=("octavian", "Antony"))),
                          CLAIMS, WORKS_REFS, WORKS, REGISTRY)
        same_lens = check("social", output(gap("e", "w1", "71.1"), gap("f", "w1", "71.1")),
                          CLAIMS, WORKS_REFS, WORKS, REGISTRY)
        found = overlaps({"military": military, "political": political, "social": same_lens})
        self.assertEqual(sorted(o["by"] for o in found), ["passage", "relationship"])
        self.assertTrue(all(len({g.split(":")[0] for g in o["gaps"]}) == 2 for o in found))

    def test_locator_is_the_last_token(self):
        self.assertEqual(locator_of("Plutarch Antony 65.3"), "65.3")
        self.assertEqual(locator_of(""), "")

    def test_every_lens_has_grounding_for_the_roman_republic(self):
        lenses, grounding = load_lenses(), load_grounding("roman-republic")
        self.assertIn("general", lenses)
        read = {k for k, v in lenses.items() if v.get("status") != "catalogued"}
        self.assertEqual(read, set(grounding["lenses"]))  # a catalogued lens is grounded before it reads
        for lens in lenses.values():
            self.assertTrue(lens["questions"], lens["id"])

    def test_the_lens_catalogue_holds_the_eighteen_facets(self):
        lenses = load_lenses()
        self.assertEqual(len(set(lenses) - {"general"}), 18)
        self.assertIn("geographic", lenses)


if __name__ == "__main__":
    unittest.main()
