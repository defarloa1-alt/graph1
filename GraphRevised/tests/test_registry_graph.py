"""The registry in the graph (D-159) and the graph type's fact-layer pins (D-158), without Neo4j."""

import importlib
import unittest

from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.registry_graph import kind_id, plan, predicate_id

graph_type = importlib.import_module("GraphRevised.migrations.018_graph_type")


class RegistryGraphPlanTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_registry()
        self.data = plan(self.registry)
        self.predicates = {p["properties"]["name"]: p for p in self.data["predicates"]}

    def test_every_predicate_and_kind_is_drawn(self):
        self.assertEqual(set(self.predicates), set(self.registry.predicates))
        self.assertEqual([k["name"] for k in self.data["kinds"]], list(self.registry.entity_kinds))
        self.assertEqual(self.data["registry"]["version"], self.registry.version)

    def test_links_follow_the_registry_kinds(self):
        links = {(l["type"], l["kind"]) for l in self.predicates["participatedIn"]["links"]}
        self.assertEqual({k for t, k in links if t == "SUBJECT_KIND"},
                         {kind_id("Group"), kind_id("Person"), kind_id("Polity")})
        self.assertEqual({k for t, k in links if t == "OBJECT_KIND"}, {kind_id("Event")})
        self.assertEqual({k for t, k in links if t == "ROLE_KIND"}, {kind_id("Office"), kind_id("Type")})
        self.assertFalse({t for t, _ in links} & {"CONTEXT_KIND"}, "participatedIn takes no context")

    def test_every_link_reaches_a_drawn_kind(self):
        kinds = {k["id"] for k in self.data["kinds"]}
        for predicate in self.data["predicates"]:
            for link in predicate["links"]:
                self.assertIn(link["kind"], kinds, predicate["properties"]["name"])

    def test_unary_predicates_have_no_object_kind(self):
        born = self.predicates["born"]
        self.assertTrue(born["properties"]["unary"])
        self.assertNotIn("OBJECT_KIND", {l["type"] for l in born["links"]})

    def test_properties_carry_ids_and_fact_layer_type(self):
        props = self.predicates["followedBy"]["properties"]
        self.assertEqual(props["id"], predicate_id("followedBy"))
        self.assertEqual(props["factLayerType"], "SUCCEEDED_BY")
        self.assertEqual(self.predicates["partOf"]["properties"]["kindPairs"],
                         ["Event -> Event", "Group -> Group", "Type -> Type", "Work -> Work"])


class FactLayerPinTests(unittest.TestCase):
    def setUp(self):
        self.pinned, self.unpinned = graph_type.fact_layer(load_registry())
        self.pins = {rel: (source, target) for rel, source, target, _ in self.pinned}

    def test_single_pair_predicates_are_pinned(self):
        self.assertEqual(self.pins["BORN_AT"], ("Person", "Place"))
        self.assertEqual(self.pins["HOLDS"], ("Work", "Position"))
        self.assertEqual(self.pins["SUCCEEDED_BY"], ("Period", "Period"))

    def test_dated_unary_facts_pin_to_year(self):
        self.assertEqual(self.pins["BORN"], ("Person", "Year"))
        self.assertIn("OCCURRED", self.unpinned, "occurred has three subject kinds")

    def test_several_kinds_at_an_end_stay_unpinned(self):
        for rel in ("PARTICIPATED_IN", "PART_OF", "OPPOSED", "ABOUT", "DESCRIBED_BY"):
            self.assertIn(rel, self.unpinned)
            self.assertNotIn(rel, self.pins)

    def test_every_predicate_is_covered_once(self):
        self.assertEqual(len(self.pins) + len(self.unpinned), len(load_registry().predicates))
        self.assertFalse(set(self.pins) & set(self.unpinned))

    def test_fact_types_never_reuse_an_infrastructure_type(self):
        infrastructure = {rel for rel, *_ in graph_type.RELATIONSHIPS if rel not in self.pins}
        self.assertFalse(infrastructure & (set(self.pins) | set(self.unpinned)))

    def test_statement_names_each_pin(self):
        statement = graph_type.graph_type()
        self.assertIn("(:Person)-[:BORN_AT =>", statement)
        self.assertIn("CONSTRAINT participated_in_derived_exists", statement)


class GraphTypeKindTests(unittest.TestCase):
    def test_subtypes_are_the_registry_kinds(self):
        """018 lists the Entity subtypes by hand; they must be the registry's kinds (47 §5.3)."""
        self.assertEqual(sorted(graph_type.SUBTYPES), sorted(load_registry().entity_kinds))
        self.assertEqual(len(graph_type.SUBTYPES), len(set(graph_type.SUBTYPES)))


if __name__ == "__main__":
    unittest.main()
