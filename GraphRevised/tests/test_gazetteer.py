"""The gazetteer (27-GAZETTEER.md): Pleiades records, the GeoNames modern tree, the bridge
between them, and the batched operations. Offline, except the live class, which is rolled back."""

import io
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from GraphRevised.gazetteer.geonames import build_tree, haversine_km, nearest_populated
from GraphRevised.gazetteer.load import build_rows, geonames_id, pleiades_id
from GraphRevised.gazetteer.pleiades import name_lines, parse_place
from GraphRevised.operations import RefusedWrite, load_operations, run_write

RULES = json.loads((Path(__file__).resolve().parents[1] / "curation" / "gazetteer.json").read_text(encoding="utf-8"))


def line(gid, name, lat, lon, cls, code, cc, a1="", a2="", a3="", a4="", pop=0):
    return "\t".join([str(gid), name, name, "", str(lat), str(lon), cls, code, cc, "", a1, a2, a3, a4, str(pop),
                      "", "", "", ""]) + "\n"


# A small world: Europe, Italy, Lazio (ADM1), Rome province (ADM2), Rome commune (ADM3, its ADM2
# code given), an ADM3 whose ADM2 level is skipped, a duplicate ADM1, an ADM5 under the commune,
# a populated place, and a feature Pleiades names.
LINES = [
    line(6255148, "Europe", 48.7, 9.1, "L", "CONT", ""),
    line(3175395, "Italy", 42.8, 12.8, "A", "PCLI", "IT"),
    line(3174976, "Lazio", 41.9, 12.8, "A", "ADM1", "IT", "07"),
    line(9999001, "Lazio (old)", 41.9, 12.8, "A", "ADM1", "IT", "07"),
    line(3169069, "Rome", 41.9, 12.6, "A", "ADM2", "IT", "07", "RM"),
    line(6539761, "Roma", 41.89, 12.51, "A", "ADM3", "IT", "07", "RM", "058091"),
    line(9999002, "Skipped", 41.5, 13.0, "A", "ADM3", "IT", "07", "", "099999"),
    line(9999003, "Municipio I", 41.89, 12.49, "A", "ADM5", "IT", "07", "RM", "058091"),
    line(3169070, "Rome", 41.89193, 12.51133, "P", "PPLC", "IT", "07", "RM", "058091", pop=2318895),
    line(3183560, "Albano Laziale", 41.73, 12.66, "P", "PPL", "IT", "07", "RM", "058003"),
    line(9999004, "Lago Albano", 41.75, 12.66, "H", "LK", "IT", "07", "RM"),
]


def small_world(directory: Path) -> None:
    (directory / "countryInfo.txt").write_text(
        "#ISO\tISO3\tISO-Numeric\tfips\tCountry\tCapital\tArea\tPopulation\tContinent\ttld\tCurrencyCode\t"
        "CurrencyName\tPhone\tPostal\tRegex\tLanguages\tgeonameid\tneighbours\tEquivalentFipsCode\n"
        "IT\tITA\t380\tIT\tItaly\tRome\t301230\t60000000\tEU\t.it\tEUR\tEuro\t39\t#####\t^$\tit-IT\t3175395\t\t\n",
        encoding="utf-8")
    (directory / "admin1CodesASCII.txt").write_text("IT.07\tLatium\tLatium\t3174976\n", encoding="utf-8")
    (directory / "admin2Codes.txt").write_text("IT.07.RM\tRome\tRome\t3169069\n", encoding="utf-8")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("hierarchy.txt", "6539761\t9999003\tADM\n3169069\t6539761\tADM\n")
    (directory / "hierarchy.zip").write_bytes(buffer.getvalue())


PLEIADES = {
    "id": "423025", "title": "Roma", "placeTypes": ["settlement"], "reprPoint": [12.4862, 41.8919],
    "names": [{"romanized": "Roma", "attested": "Ῥώμη", "attestations": [{"timePeriod": "roman"},
                                                                       {"timePeriod": "late-antique"}]}],
    "connections": [
        {"connectionType": "part_of_regional", "connectsTo": "https://pleiades.stoa.org/places/607225751",
         "attestations": [{"timePeriod": "roman"}]},
        {"connectionType": "connection", "connectsTo": "https://pleiades.stoa.org/places/803793619", "attestations": []},
    ],
    "references": [{"accessURI": "http://www.geonames.org/3169070"},
                   {"accessURI": "https://www.wikidata.org/wiki/Q220"},
                   {"accessURI": "http://vocab.getty.edu/page/tgn/7000874"}],
}


class PleiadesTests(unittest.TestCase):
    def test_a_place_keeps_its_parents_names_and_identifiers(self):
        place = parse_place(PLEIADES)
        self.assertEqual((place["lat"], place["lon"]), (41.8919, 12.4862))
        self.assertEqual((place["geonames"], place["wikidata"], place["tgn"]), (["3169070"], ["Q220"], ["7000874"]))
        self.assertEqual(place["connections"][0], {"type": "part_of_regional", "target": "607225751",
                                                   "periods": ["roman"]})
        self.assertEqual(name_lines(place["names"]), (["Roma"], ["Roma (late-antique, roman)"]))

    def test_an_unlocated_place_has_no_point(self):
        place = parse_place({**PLEIADES, "reprPoint": None})
        self.assertIsNone(place["lat"])


class ModernTreeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        path = Path(self.directory.name)
        small_world(path)
        cells = {(41, 12), (41, 13)}
        self.tree = build_tree(path, RULES, {"3169070", "9999004"}, cells, lines=iter(LINES))

    def tearDown(self):
        self.directory.cleanup()

    def test_each_unit_takes_the_nearest_higher_level_its_codes_name(self):
        parents = self.tree.parents
        self.assertEqual(parents["3175395"], "6255148")  # Italy in Europe, from countryInfo
        self.assertEqual(parents["3174976"], "3175395")
        self.assertEqual(parents["6539761"], "3169069")
        self.assertEqual(parents["9999002"], "3174976")  # a skipped ADM2 does not break the chain
        self.assertEqual(parents["9999003"], "6539761")  # ADM5 from hierarchy.txt

    def test_the_listed_unit_wins_a_duplicate_code(self):
        self.assertIn("3174976", self.tree.units)
        self.assertNotIn("9999001", self.tree.units)
        self.assertEqual(self.tree.report["duplicateCodePaths"], 1)

    def test_populated_places_are_kept_only_for_the_bridge(self):
        self.assertNotIn("3183560", self.tree.units)
        found, km = nearest_populated(self.tree, 41.8919, 12.4862, 50)
        self.assertEqual(found.id, "3169070")
        self.assertLess(km, 3)
        self.assertEqual(self.tree.most_specific_unit(found), "6539761")
        self.assertIsNone(nearest_populated(self.tree, 45.0, 12.5, 50))

    def test_the_bridge(self):
        roma = parse_place(PLEIADES)
        alba = parse_place({**PLEIADES, "id": "1", "title": "Alba Longa", "reprPoint": [12.65, 41.75],
                            "references": [], "connections": []})
        far = parse_place({**PLEIADES, "id": "2", "title": "Far away", "reprPoint": [12.5, 45.0],
                           "references": [], "connections": []})
        rows = build_rows(RULES, [roma, alba, far], self.tree, {"geonames": "g", "pleiades": "p"})
        bridges = {b["ancient"]: b for b in rows["bridges"]}
        self.assertEqual(bridges[pleiades_id("423025")]["how"], "pleiades reference")
        self.assertEqual(bridges[pleiades_id("423025")]["modern"], geonames_id("3169070"))
        self.assertEqual((bridges[pleiades_id("1")]["how"], bridges[pleiades_id("1")]["viaLabel"]),
                         ("nearest place", "Albano Laziale"))
        self.assertEqual(rows["unbridged"][0]["pleiades"], "2")
        self.assertEqual(rows["report"]["ancientParentMissing"], 1)  # 607225751 is not in this small dump
        # the referenced populated place is loaded and placed in the modern tree
        modern = {(r["child"], r["parent"]) for r in rows["parents"] if r["tree"] == "modern"}
        self.assertIn((geonames_id("3169070"), geonames_id("6539761")), modern)

    def test_distance(self):
        self.assertAlmostEqual(haversine_km(41.9, 12.5, 40.85, 14.27), 188, delta=3)  # Rome to Naples


@unittest.skipUnless(os.environ.get("NEO4J_PASSWORD"), "needs NEO4J_PASSWORD")
class GazetteerOperationsLiveTests(unittest.TestCase):
    """The batched operations, in a transaction that is always rolled back."""

    @classmethod
    def setUpClass(cls):
        from neo4j import GraphDatabase

        cls.driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                          auth=("neo4j", os.environ["NEO4J_PASSWORD"]), notifications_min_severity="OFF")
        cls.operations = load_operations()

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

    def setUp(self):
        self.session = self.driver.session(database="neo4j")
        self.tx = self.session.begin_transaction()

    def tearDown(self):
        self.tx.rollback()
        self.session.close()

    def location(self, system, identifier, **extra):
        return {"id": f"chr:location:test-{system.lower()}:{identifier}", "label": identifier, "system": f"Test{system}",
                "identifier": identifier, "kind": "test", "lat": 41.9, "lon": 12.5, "population": None,
                "placeTypes": None, "names": None, "nameAttestations": None, "dataset": "test", **extra}

    def write(self, name, rows):
        return run_write(self.tx, self.operations, name, {"rows": rows})

    def test_locations_parents_and_bridge(self):
        city, region, other, ancient = (self.location("Modern", "city"), self.location("Modern", "region"),
                                        self.location("Modern", "other"), self.location("Ancient", "urbs"))
        self.write("upsert_locations", [city, region, other, ancient])
        self.write("upsert_locations", [city])  # a retry changes nothing
        self.write("link_location_parents", [{"child": city["id"], "parent": region["id"], "tree": "modern",
                                              "relation": "admin", "periods": None}])
        self.write("link_location_parents", [{"child": city["id"], "parent": other["id"], "tree": "modern",
                                              "relation": "admin", "periods": None}])
        parents = self.tx.run("MATCH (:Location {id: $id})-[:WITHIN {tree: 'modern'}]->(p) RETURN p.id AS id",
                              id=city["id"]).value("id")
        self.assertEqual(parents, [other["id"]])  # one modern parent: the new one replaces the old
        self.write("link_modern_locations", [{"ancient": ancient["id"], "modern": city["id"], "how": "nearest place",
                                              "distanceKm": 1.2, "viaId": "x", "viaLabel": "X"}])
        point = self.tx.run("MATCH (l:Location {id: $id}) RETURN l.location.latitude AS lat", id=city["id"]).single()
        self.assertAlmostEqual(point["lat"], 41.9)

    def test_refusals(self):
        city = self.location("Modern", "city")
        self.write("upsert_locations", [city])
        with self.assertRaises(RefusedWrite):  # an id cannot move to another identifier
            self.write("upsert_locations", [{**city, "identifier": "elsewhere"}])

    def test_a_missing_end_refuses_the_batch(self):
        city = self.location("Modern", "city")
        self.write("upsert_locations", [city])
        with self.assertRaises(RefusedWrite):
            self.write("link_location_parents", [{"child": city["id"], "parent": "chr:location:test:none",
                                                  "tree": "modern", "relation": "admin", "periods": None}])


if __name__ == "__main__":
    unittest.main()
