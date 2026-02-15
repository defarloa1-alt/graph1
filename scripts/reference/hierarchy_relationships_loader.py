"""
Hierarchy Relationships Loader for Chrystallum

Loads harvested academic properties (P101/P2578/P921/P1269) into Neo4j.
Handles CSV input and creates relationship nodes/edges.
"""

import csv
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from enum import Enum

from neo4j import Session, GraphDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropertyType(Enum):
    """Academic property types from Wikidata"""

    P101 = ("FIELD_OF_WORK", "person", "discipline")  # (rel_name, source_type, target_type)
    P2578 = ("STUDIES", "discipline", "concept")
    P921 = ("MAIN_SUBJECT", "work", "concept")
    P1269 = ("FACET_OF", "concept", "concept")


class HierarchyRelationshipsLoader:
    """
    Loader for Wikidata hierarchy relationships into Neo4j
    """

    def __init__(self, session: Session):
        self.session = session

    def load_csv(
        self,
        csv_file: Path,
        batch_size: int = 100,
    ) -> Tuple[int, int]:
        """
        Load relationships from CSV file.

        CSV format:
          source_qid, source_label, source_type, property_type, target_qid, target_label, target_type, confidence

        Args:
            csv_file: Path to CSV file
            batch_size: Number of relationships to load per batch

        Returns:
            (total_loaded, total_failed)
        """

        logger.info(f"Loading relationships from {csv_file}")

        total_loaded = 0
        total_failed = 0
        batch = []

        try:
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    batch.append(row)

                    if len(batch) >= batch_size:
                        loaded, failed = self._load_batch(batch)
                        total_loaded += loaded
                        total_failed += failed
                        batch = []

                # Load remaining batch
                if batch:
                    loaded, failed = self._load_batch(batch)
                    total_loaded += loaded
                    total_failed += failed

        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            return 0, 0

        logger.info(f"Load complete. Loaded: {total_loaded}, Failed: {total_failed}")
        return total_loaded, total_failed

    def _load_batch(
        self,
        batch: List[Dict],
    ) -> Tuple[int, int]:
        """
        Load a batch of relationships.

        Args:
            batch: List of relationship dicts

        Returns:
            (loaded, failed)
        """

        loaded = 0
        failed = 0

        # Group by property type
        by_property = {}
        for row in batch:
            prop_type = row.get("property_type")
            if prop_type not in by_property:
                by_property[prop_type] = []
            by_property[prop_type].append(row)

        # Load each property type
        for prop_type, rows in by_property.items():
            for row in rows:
                try:
                    if prop_type == "P101":
                        self._load_p101(row)
                    elif prop_type == "P2578":
                        self._load_p2578(row)
                    elif prop_type == "P921":
                        self._load_p921(row)
                    elif prop_type == "P1269":
                        self._load_p1269(row)

                    loaded += 1

                except Exception as e:
                    logger.error(f"Error loading relationship: {e}")
                    failed += 1

        return loaded, failed

    def _load_p101(self, row: Dict) -> None:
        """
        Load P101 (field of work) relationship.

        Pattern:
          (person)-[:FIELD_OF_WORK]->(discipline)
        """

        source_qid = row.get("source_qid")
        source_label = row.get("source_label")
        target_qid = row.get("target_qid")
        target_label = row.get("target_label")
        confidence = float(row.get("confidence", 0.95))

        query = """
        MERGE (person:Person {qid: $source_qid})
          ON CREATE SET person.label = $source_label
        MERGE (discipline:SubjectConcept {qid: $target_qid})
          ON CREATE SET discipline.label = $target_label, discipline.type = 'discipline'
        MERGE (person)-[r:FIELD_OF_WORK]->(discipline)
          SET r.source = 'wikidata', r.property = 'P101', r.confidence = $confidence
        """

        self.session.run(
            query,
            source_qid=source_qid,
            source_label=source_label,
            target_qid=target_qid,
            target_label=target_label,
            confidence=confidence,
        )

    def _load_p2578(self, row: Dict) -> None:
        """
        Load P2578 (studies) relationship.

        Pattern:
          (discipline)-[:STUDIES]->(object_of_study)
        """

        source_qid = row.get("source_qid")
        source_label = row.get("source_label")
        target_qid = row.get("target_qid")
        target_label = row.get("target_label")
        confidence = float(row.get("confidence", 0.95))

        query = """
        MERGE (discipline:SubjectConcept {qid: $source_qid})
          ON CREATE SET discipline.label = $source_label, discipline.type = 'discipline'
        MERGE (object:SubjectConcept {qid: $target_qid})
          ON CREATE SET object.label = $target_label
        MERGE (discipline)-[r:STUDIES]->(object)
          SET r.source = 'wikidata', r.property = 'P2578', r.confidence = $confidence
        """

        self.session.run(
            query,
            source_qid=source_qid,
            source_label=source_label,
            target_qid=target_qid,
            target_label=target_label,
            confidence=confidence,
        )

    def _load_p921(self, row: Dict) -> None:
        """
        Load P921 (main subject) relationship.

        Pattern:
          (work)-[:MAIN_SUBJECT]->(topic)
        """

        source_qid = row.get("source_qid")
        source_label = row.get("source_label")
        target_qid = row.get("target_qid")
        target_label = row.get("target_label")
        confidence = float(row.get("confidence", 0.95))

        query = """
        MERGE (work:Work {qid: $source_qid})
          ON CREATE SET work.label = $source_label
        MERGE (topic {qid: $target_qid})
          ON CREATE SET topic.label = $target_label
        MERGE (work)-[r:MAIN_SUBJECT]->(topic)
          SET r.source = 'wikidata', r.property = 'P921', r.confidence = $confidence
        """

        self.session.run(
            query,
            source_qid=source_qid,
            source_label=source_label,
            target_qid=target_qid,
            target_label=target_label,
            confidence=confidence,
        )

    def _load_p1269(self, row: Dict) -> None:
        """
        Load P1269 (facet of) relationship.

        Pattern:
          (facet)-[:FACET_OF]->(broader_concept)
        """

        source_qid = row.get("source_qid")
        source_label = row.get("source_label")
        target_qid = row.get("target_qid")
        target_label = row.get("target_label")
        confidence = float(row.get("confidence", 0.95))

        query = """
        MERGE (facet:SubjectConcept {qid: $source_qid})
          ON CREATE SET facet.label = $source_label
        MERGE (broader:SubjectConcept {qid: $target_qid})
          ON CREATE SET broader.label = $target_label
        MERGE (facet)-[r:FACET_OF]->(broader)
          SET r.source = 'wikidata', r.property = 'P1269', r.confidence = $confidence
        """

        self.session.run(
            query,
            source_qid=source_qid,
            source_label=source_label,
            target_qid=target_qid,
            target_label=target_label,
            confidence=confidence,
        )

    # ============================================================================
    # STATISTICS & VERIFICATION
    # ============================================================================

    def get_relationship_counts(self) -> Dict[str, int]:
        """
        Get count of each relationship type loaded.

        Returns:
            Dict with relationship type counts
        """

        query = """
        RETURN {
            field_of_work: size((()-[:FIELD_OF_WORK]->())),
            studies: size((()-[:STUDIES]->())),
            main_subject: size((()-[:MAIN_SUBJECT]->())),
            facet_of: size((()-[:FACET_OF]->()))
        } as counts
        """

        result = self.session.run(query)
        record = result.single()
        return record["counts"] if record else {}

    def verify_load(self) -> Dict:
        """
        Verify that relationships were loaded correctly.

        Returns:
            Dict with verification results
        """

        query = """
        RETURN {
            people_with_fields: COUNT(DISTINCT (p:Person)-[:FIELD_OF_WORK]->()),
            disciplines_studied_by: COUNT(DISTINCT (d:SubjectConcept)-[:STUDIES]->()),
            works_with_subjects: COUNT(DISTINCT (w:Work)-[:MAIN_SUBJECT]->()),
            facets: COUNT(DISTINCT (f)-[:FACET_OF]->())
        } as stats
        """

        result = self.session.run(query)
        record = result.single()
        return record["stats"] if record else {}


def load_academic_properties(
    csv_dir: Path = Path("CSV"),
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_auth: Tuple[str, str] = ("neo4j", "password"),
) -> Dict:
    """
    Load all academic properties from CSV files.

    Args:
        csv_dir: Directory containing CSV files
        neo4j_uri: Neo4j connection URI
        neo4j_auth: (username, password)

    Returns:
        Summary of loaded relationships
    """

    logger.info(f"Starting academic properties load from {csv_dir}")

    csv_dir = Path(csv_dir)
    csv_files = list(csv_dir.glob("academic_properties*.csv"))

    if not csv_files:
        logger.error(f"No CSV files found in {csv_dir}")
        return {}

    summary = {
        "files_processed": 0,
        "total_loaded": 0,
        "total_failed": 0,
        "relationship_counts": {},
    }

    try:
        with GraphDatabase.driver(neo4j_uri, auth=neo4j_auth) as driver:
            with driver.session() as session:
                loader = HierarchyRelationshipsLoader(session)

                for csv_file in csv_files:
                    logger.info(f"Loading {csv_file.name}")
                    loaded, failed = loader.load_csv(csv_file)
                    summary["files_processed"] += 1
                    summary["total_loaded"] += loaded
                    summary["total_failed"] += failed

                # Get final statistics
                summary["relationship_counts"] = loader.get_relationship_counts()
                summary["verification"] = loader.verify_load()

    except Exception as e:
        logger.error(f"Error loading relationships: {e}")

    logger.info(f"Load summary: {summary}")
    return summary


if __name__ == "__main__":
    # Example usage
    summary = load_academic_properties()
    print("\nLoad Summary:")
    import json

    print(json.dumps(summary, indent=2))
