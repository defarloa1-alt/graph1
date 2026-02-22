"""
Hierarchy Query Engine for Chrystallum

Implements semantic query patterns using P31/P279/P361/P101/P2578/P921/P1269 relationships:
  - P31: instance-of (individual → class)
  - P279: subclass-of (class → superclass) [TRANSITIVE]
  - P361: part-of (component → whole) [TRANSITIVE]
  - P101: field-of-work (person/org → discipline)
  - P2578: studies (discipline → object of study)
  - P921: main-subject (work → topic)
  - P1269: facet-of (aspect → broader concept)

Use Cases:
  1. Semantic query expansion: "Find all battles in Punic Wars"
  2. Expert discovery: "Who specializes in military history?"
  3. Source discovery: "What works are about Roman politics?"
  4. Contradiction detection: Cross-hierarchy inconsistencies
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
from neo4j import Session, Query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HierarchyRelationType(Enum):
    """Supported hierarchy relationship types"""
    INSTANCE_OF = "INSTANCE_OF"  # P31
    SUBCLASS_OF = "SUBCLASS_OF"  # P279 [transitive]
    PART_OF = "PART_OF"  # P361 [transitive]
    FIELD_OF_WORK = "FIELD_OF_WORK"  # P101
    STUDIES = "STUDIES"  # P2578
    MAIN_SUBJECT = "MAIN_SUBJECT"  # P921
    FACET_OF = "FACET_OF"  # P1269


@dataclass
class HierarchyNode:
    """Node in hierarchy with metadata"""
    qid: str
    label: str
    node_type: str  # "Entity", "SubjectConcept", "Work", "Person", "Organization"
    properties: Dict = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class HierarchyPath:
    """Path through hierarchy for reasoning"""
    nodes: List[HierarchyNode]
    edges: List[HierarchyRelationType]
    transitive_inference: bool = False

    def __str__(self) -> str:
        """Readable path representation"""
        parts = [self.nodes[0].label]
        for edge, node in zip(self.edges, self.nodes[1:]):
            parts.append(f" -{edge.value}-> {node.label}")
        return "".join(parts)


class HierarchyQueryEngine:
    """
    Query engine for semantic hierarchy traversal and reasoning
    """

    def __init__(self, session: Session):
        self.session = session

    # ============================================================================
    # USE CASE 1: SEMANTIC QUERY EXPANSION
    # ============================================================================

    def find_instances_of_class(
        self,
        class_qid: str,
        include_subclasses: bool = True,
        max_depth: int = 5,
    ) -> List[HierarchyNode]:
        """
        Find all instances of a class, optionally including subclasses.

        Pattern:
          (specific)-[:INSTANCE_OF]->(class) OR
          (specific)-[:INSTANCE_OF]->(subclass)-[:SUBCLASS_OF*]->(class)

        Example:
          find_instances_of_class("Q178561")  # battle
          → [Battle of Cannae, Battle of Trebia, Battle of Zama, ...]

        Args:
            class_qid: Wikidata QID of class (e.g., "Q178561" for battle)
            include_subclasses: If True, includes instances of all subclasses
            max_depth: Maximum subclass hierarchy depth

        Returns:
            List of instances with QID and label
        """

        if include_subclasses:
            query = """
            MATCH (instance)-[:INSTANCE_OF]->(intermediate)-[:SUBCLASS_OF*0..{depth}]->(class:SubjectConcept {{qid: $class_qid}})
            RETURN DISTINCT instance.qid as qid, instance.label as label, instance.node_type as type
            ORDER BY instance.label
            """.format(depth=max_depth)
        else:
            query = """
            MATCH (instance)-[:INSTANCE_OF]->(class:SubjectConcept {{qid: $class_qid}})
            RETURN instance.qid as qid, instance.label as label, instance.node_type as type
            ORDER BY instance.label
            """

        try:
            result = self.session.run(query, class_qid=class_qid)
            return [
                HierarchyNode(
                    qid=record["qid"],
                    label=record["label"],
                    node_type=record["type"],
                )
                for record in result
            ]
        except Exception as e:
            logger.error(f"Error finding instances of {class_qid}: {e}")
            return []

    def find_superclasses(
        self,
        entity_qid: str,
        max_depth: int = 5,
    ) -> List[HierarchyPath]:
        """
        Find all superclasses of an entity via P31 and P279.

        Pattern:
          (entity)-[:INSTANCE_OF]->(class)
          (class)-[:SUBCLASS_OF*]->(superclass)

        Example:
          find_superclasses("Q13377")  # Battle of Cannae
          → [battle, military conflict, event, entity]

        Args:
            entity_qid: QID of entity to classify
            max_depth: Maximum traversal depth

        Returns:
            List of paths from entity to all superclasses
        """

        query = """
        MATCH path = (entity:Event {{qid: $entity_qid}})
              -[:INSTANCE_OF]->(class:SubjectConcept)
              -[:SUBCLASS_OF*0..{depth}]->(superclass:SubjectConcept)
        WITH path, nodes(path) as node_list
        RETURN [n in node_list | {{qid: n.qid, label: n.label, type: n.node_type}}] as path_nodes,
               [e in relationships(path) | type(e)] as edge_types
        ORDER BY length(relationships(path))
        """.format(depth=max_depth)

        try:
            result = self.session.run(query, entity_qid=entity_qid)
            paths = []
            for record in result:
                nodes = [
                    HierarchyNode(
                        qid=n["qid"],
                        label=n["label"],
                        node_type=n["type"],
                    )
                    for n in record["path_nodes"]
                ]
                edges = [
                    HierarchyRelationType[edge.replace("-", "_").upper()]
                    for edge in record["edge_types"]
                ]
                paths.append(
                    HierarchyPath(
                        nodes=nodes,
                        edges=edges,
                        transitive_inference=len(edges) > 1,
                    )
                )
            return paths
        except Exception as e:
            logger.error(f"Error finding superclasses of {entity_qid}: {e}")
            return []

    def find_components(
        self,
        whole_qid: str,
        max_depth: int = 3,
    ) -> List[HierarchyNode]:
        """
        Find all components of a whole via P361 (part-of).

        Pattern:
          (component)-[:PART_OF*1..depth]->(whole)

        Example:
          find_components("Q185736")  # Second Punic War
          → [Battle of Cannae, Battle of Trebia, ...]

        Args:
            whole_qid: QID of the whole entity
            max_depth: Maximum part-of traversal depth

        Returns:
            List of components
        """

        query = """
        MATCH (component)-[:PART_OF*1..{depth}]->(whole {{qid: $whole_qid}})
        RETURN DISTINCT component.qid as qid, component.label as label, 
                        component.node_type as type
        ORDER BY component.label
        """.format(depth=max_depth)

        try:
            result = self.session.run(query, whole_qid=whole_qid)
            return [
                HierarchyNode(
                    qid=record["qid"],
                    label=record["label"],
                    node_type=record["type"],
                )
                for record in result
            ]
        except Exception as e:
            logger.error(f"Error finding components of {whole_qid}: {e}")
            return []

    # ============================================================================
    # USE CASE 2: EXPERT DISCOVERY (P101)
    # ============================================================================

    def find_experts_in_field(
        self,
        discipline_qid: str,
        min_confidence: float = 0.7,
    ) -> List[Tuple[HierarchyNode, float]]:
        """
        Find people/organizations who specialize in a discipline via P101.

        Pattern:
          (person|org)-[:FIELD_OF_WORK]->(discipline)

        Example:
          find_experts_in_field("Q188507")  # military history
          → [(Polybius, 0.95), (Livy, 0.90), ...]

        Args:
            discipline_qid: QID of academic discipline
            min_confidence: Minimum confidence score

        Returns:
            List of (expert, confidence) tuples
        """

        query = """
        MATCH (expert)-[r:FIELD_OF_WORK]->(discipline:SubjectConcept {{qid: $discipline_qid}})
        WHERE r.confidence >= $min_confidence OR r.confidence IS NULL
        RETURN expert.qid as qid, expert.label as label, expert.node_type as type,
               COALESCE(r.confidence, 0.95) as confidence
        ORDER BY confidence DESC
        """

        try:
            result = self.session.run(
                query,
                discipline_qid=discipline_qid,
                min_confidence=min_confidence,
            )
            return [
                (
                    HierarchyNode(
                        qid=record["qid"],
                        label=record["label"],
                        node_type=record["type"],
                        confidence=record["confidence"],
                    ),
                    record["confidence"],
                )
                for record in result
            ]
        except Exception as e:
            logger.error(f"Error finding experts in {discipline_qid}: {e}")
            return []

    def find_disciplines_for_expert(
        self,
        person_qid: str,
    ) -> List[HierarchyNode]:
        """
        Find all disciplines a person specializes in via P101.

        Pattern:
          (person)-[:FIELD_OF_WORK]->(discipline)

        Example:
          find_disciplines_for_expert("Q7345")  # Polybius
          → [military history, ancient history, ...]

        Args:
            person_qid: QID of person

        Returns:
            List of disciplines
        """

        query = """
        MATCH (person:Person {{qid: $person_qid}})-[:FIELD_OF_WORK]->(discipline:SubjectConcept)
        RETURN discipline.qid as qid, discipline.label as label, discipline.node_type as type
        ORDER BY discipline.label
        """

        try:
            result = self.session.run(query, person_qid=person_qid)
            return [
                HierarchyNode(
                    qid=record["qid"],
                    label=record["label"],
                    node_type=record["type"],
                )
                for record in result
            ]
        except Exception as e:
            logger.error(f"Error finding disciplines for expert {person_qid}: {e}")
            return []

    # ============================================================================
    # USE CASE 3: SOURCE DISCOVERY (P921)
    # ============================================================================

    def find_works_about_topic(
        self,
        topic_qid: str,
        work_type: Optional[str] = None,
    ) -> List[HierarchyNode]:
        """
        Find works (books, articles) about a topic via P921.

        Pattern:
          (work)-[:MAIN_SUBJECT]->(topic)

        Example:
          find_works_about_topic("Q7163")  # politics
          → ["De re publica", "Politics (Aristotle)", ...]

        Args:
            topic_qid: QID of topic
            work_type: Optional filter (e.g., "book", "article")

        Returns:
            List of works
        """

        if work_type:
            query = """
            MATCH (work:Work {{type: $work_type}})-[:MAIN_SUBJECT]->(topic {{qid: $topic_qid}})
            RETURN DISTINCT work.qid as qid, work.label as label, work.node_type as type
            ORDER BY work.label
            """
        else:
            query = """
            MATCH (work:Work)-[:MAIN_SUBJECT]->(topic {{qid: $topic_qid}})
            RETURN DISTINCT work.qid as qid, work.label as label, work.node_type as type
            ORDER BY work.label
            """

        try:
            result = self.session.run(
                query,
                topic_qid=topic_qid,
                work_type=work_type,
            )
            return [
                HierarchyNode(
                    qid=record["qid"],
                    label=record["label"],
                    node_type=record["type"],
                )
                for record in result
            ]
        except Exception as e:
            logger.error(f"Error finding works about {topic_qid}: {e}")
            return []

    def find_works_by_expert(
        self,
        person_qid: str,
    ) -> List[Tuple[HierarchyNode, List[str]]]:
        """
        Find works by a person and their main subjects.

        Pattern:
          (person)-[:AUTHOR_OF]->(work)-[:MAIN_SUBJECT]->(topic)

        Example:
          find_works_by_expert("Q7345")  # Polybius
          → [("Histories", ["military", "politics", ...])]

        Args:
            person_qid: QID of author

        Returns:
            List of (work, topics) tuples
        """

        query = """
        MATCH (person:Person {{qid: $person_qid}})-[:AUTHOR_OF]->(work:Work)
        OPTIONAL MATCH (work)-[:MAIN_SUBJECT]->(topic)
        RETURN DISTINCT work.qid as qid, work.label as label,
               collect(DISTINCT topic.label) as topics
        ORDER BY work.label
        """

        try:
            result = self.session.run(query, person_qid=person_qid)
            return [
                (
                    HierarchyNode(
                        qid=record["qid"],
                        label=record["label"],
                        node_type="Work",
                    ),
                    record["topics"],
                )
                for record in result
            ]
        except Exception as e:
            logger.error(f"Error finding works by expert {person_qid}: {e}")
            return []

    # ============================================================================
    # USE CASE 4: CONTRADICTION DETECTION
    # ============================================================================

    def find_cross_hierarchy_contradictions(
        self,
        entity_qid: str,
    ) -> List[Dict]:
        """
        Find contradictory claims about an entity at different hierarchy levels.

        Pattern:
          (specific_claim)-[:SUBJECT]->(specific_entity)
          (specific_entity)-[:INSTANCE_OF*]->(general_entity)
          (general_claim)-[:SUBJECT]->(general_entity)
          Where specific_claim and general_claim have opposite meanings

        Example:
          (claim: "Battle of Cannae was Roman victory")
          vs.
          (claim about Second Punic War: "Rome suffered defeats")

        Args:
            entity_qid: QID of entity to check

        Returns:
            List of contradictions: {specific_claim, general_claim, contradiction_type}
        """

        query = """
        MATCH (specific_claim:Claim)-[:SUBJECT]->(specific_entity {{qid: $entity_qid}})
        MATCH (specific_entity)-[:INSTANCE_OF|PART_OF*1..3]->(general_entity)
        MATCH (general_claim:Claim)-[:SUBJECT]->(general_entity)
        WHERE specific_claim.id <> general_claim.id
          AND (
            (specific_claim.label CONTAINS 'victory' AND general_claim.label CONTAINS 'defeat')
            OR (specific_claim.label CONTAINS 'ally' AND general_claim.label CONTAINS 'enemy')
            OR (specific_claim.label CONTAINS 'success' AND general_claim.label CONTAINS 'failure')
          )
        RETURN {{
            contradiction_type: 'hierarchical',
            specific_claim_id: specific_claim.id,
            specific_claim_label: specific_claim.label,
            specific_confidence: specific_claim.confidence,
            general_claim_id: general_claim.id,
            general_claim_label: general_claim.label,
            general_confidence: general_claim.confidence,
            entity_hierarchy_distance: length(relationships)
        }} as contradiction
        """

        try:
            result = self.session.run(query, entity_qid=entity_qid)
            return [record["contradiction"] for record in result]
        except Exception as e:
            logger.error(f"Error finding contradictions for {entity_qid}: {e}")
            return []

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def find_all_facets_of_concept(
        self,
        concept_qid: str,
    ) -> List[HierarchyNode]:
        """
        Find all aspects/facets of a concept via P1269.

        Pattern:
          (facet)-[:FACET_OF*1..]->(concept)

        Example:
          find_all_facets_of_concept("Q8134")  # economics
          → [microeconomics, macroeconomics, econometrics, ...]

        Args:
            concept_qid: QID of broader concept

        Returns:
            List of facets
        """

        query = """
        MATCH (facet)-[:FACET_OF*1..5]->(concept:SubjectConcept {{qid: $concept_qid}})
        RETURN DISTINCT facet.qid as qid, facet.label as label, facet.node_type as type
        ORDER BY facet.label
        """

        try:
            result = self.session.run(query, concept_qid=concept_qid)
            return [
                HierarchyNode(
                    qid=record["qid"],
                    label=record["label"],
                    node_type=record["type"],
                )
                for record in result
            ]
        except Exception as e:
            logger.error(f"Error finding facets of {concept_qid}: {e}")
            return []

    def find_what_discipline_studies(
        self,
        discipline_qid: str,
    ) -> List[HierarchyNode]:
        """
        Find what an academic discipline studies via P2578.

        Pattern:
          (discipline)-[:STUDIES]->(object_of_study)

        Example:
          find_what_discipline_studies("Q188507")  # military history
          → [warfare, military, conflict, ...]

        Args:
            discipline_qid: QID of academic discipline

        Returns:
            List of objects studied
        """

        query = """
        MATCH (discipline:SubjectConcept {{qid: $discipline_qid}})-[:STUDIES]->(studied_object)
        RETURN studied_object.qid as qid, studied_object.label as label, 
               studied_object.node_type as type
        ORDER BY studied_object.label
        """

        try:
            result = self.session.run(query, discipline_qid=discipline_qid)
            return [
                HierarchyNode(
                    qid=record["qid"],
                    label=record["label"],
                    node_type=record["type"],
                )
                for record in result
            ]
        except Exception as e:
            logger.error(f"Error finding what {discipline_qid} studies: {e}")
            return []

    def infer_facets_from_hierarchy(
        self,
        entity_qid: str,
        facet_mapping: Dict[str, List[str]],
    ) -> List[str]:
        """
        Infer facets for an entity based on its P31/P279 hierarchy.

        Algorithm:
          1. Get all superclasses via instance-of + subclass-of
          2. Map each superclass to facets using provided mapping
          3. Deduplicate and return

        Example:
          infer_facets_from_hierarchy("Q13377", FACET_MAPPING)
          # Battle of Cannae → battle → military conflict
          # → ["military", "temporal", "geographic"]

        Args:
            entity_qid: QID of entity
            facet_mapping: Dict from QID/label to list of facets

        Returns:
            List of inferred facets
        """

        superclasses = self.find_superclasses(entity_qid)
        facets = set()

        for path in superclasses:
            for node in path.nodes:
                # Check by QID first, then label
                if node.qid in facet_mapping:
                    facets.update(facet_mapping[node.qid])
                elif node.label in facet_mapping:
                    facets.update(facet_mapping[node.label])

        return sorted(list(facets))

    # ============================================================================
    # BATCH OPERATIONS
    # ============================================================================

    def batch_find_instances(
        self,
        class_qids: List[str],
    ) -> Dict[str, List[HierarchyNode]]:
        """
        Find instances for multiple classes.

        Args:
            class_qids: List of QIDs

        Returns:
            Dict mapping QID to list of instances
        """

        return {qid: self.find_instances_of_class(qid) for qid in class_qids}

    def batch_find_experts(
        self,
        discipline_qids: List[str],
    ) -> Dict[str, List[Tuple[HierarchyNode, float]]]:
        """
        Find experts for multiple disciplines.

        Args:
            discipline_qids: List of discipline QIDs

        Returns:
            Dict mapping QID to list of (expert, confidence) tuples
        """

        return {qid: self.find_experts_in_field(qid) for qid in discipline_qids}


if __name__ == "__main__":
    # Example usage (requires Neo4j running)
    from neo4j import GraphDatabase

    URI = "bolt://localhost:7687"
    AUTH = ("neo4j", "password")

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            engine = HierarchyQueryEngine(session)

            # Use Case 1: Find instances
            print("=== USE CASE 1: Find instances of 'battle' ===")
            battles = engine.find_instances_of_class("Q178561")
            for battle in battles[:5]:
                print(f"  - {battle.label} ({battle.qid})")

            # Use Case 2: Find experts
            print("\n=== USE CASE 2: Find experts in military history ===")
            experts = engine.find_experts_in_field("Q188507")
            for expert, conf in experts[:5]:
                print(f"  - {expert.label} ({expert.qid}): {conf:.2f}")

            # Use Case 3: Find works
            print("\n=== USE CASE 3: Find works about Roman politics ===")
            works = engine.find_works_about_topic("Q7163")
            for work in works[:5]:
                print(f"  - {work.label} ({work.qid})")

            # Use Case 4: Find contradictions
            print("\n=== USE CASE 4: Find contradictions ===")
            contradictions = engine.find_cross_hierarchy_contradictions("Q13377")
            for contradiction in contradictions[:3]:
                print(f"  - {contradiction}")
