"""
Academic Property Harvester for Chrystallum

Harvests Wikidata properties for academic disciplines and related entities:
  - P101: field-of-work (person/org → discipline)
  - P2578: studies (discipline → object of study)
  - P921: main-subject (work → topic)
  - P1269: facet-of (aspect → broader concept)

Uses SPARQL queries to extract relationships and formats for Neo4j loading.
"""

import json
import csv
import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wikidata SPARQL endpoint
WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# Domain-specific discipline mappings
DOMAIN_DISCIPLINE_MAPPINGS = {
    "Roman Republic": [
        ("Q188507", "military history"),
        ("Q36442", "political science"),
        ("Q192633", "ancient history"),
        ("Q213987", "classical philology"),
        ("Q87893", "Roman law"),
        ("Q39680", "numismatics"),
        ("Q50641", "epigraphy"),
        ("Q121955", "palaeography"),
    ],
    "Mediterranean History": [
        ("Q188507", "military history"),
        ("Q36442", "political science"),
        ("Q192633", "ancient history"),
        ("Q8134", "economics"),
        ("Q7163", "politics"),
        ("Q42365", "geography"),
    ],
}


@dataclass
class AcademicProperty:
    """Represents a harvested Wikidata property relationship"""

    source_qid: str
    source_label: str
    source_type: str  # "person", "discipline", "work", "concept"
    property_type: str  # "P101", "P2578", "P921", "P1269"
    target_qid: str
    target_label: str
    target_type: str
    confidence: float = 0.95
    source_url: str = ""


class AcademicPropertyHarvester:
    """
    Harvests academic properties from Wikidata using SPARQL
    """

    def __init__(self, output_dir: Path = Path("CSV")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.properties: List[AcademicProperty] = []

    def harvest_p101_field_of_work(
        self,
        discipline_qids: List[str],
    ) -> List[AcademicProperty]:
        """
        Harvest P101 (field of work): Person/Org → Discipline

        SPARQL Pattern:
          ?person wdt:P101 ?discipline
          WHERE ?discipline is one of discipline_qids

        Args:
            discipline_qids: List of discipline QIDs

        Returns:
            List of AcademicProperty objects
        """

        logger.info(f"Harvesting P101 (field of work) for {len(discipline_qids)} disciplines")

        properties = []
        qid_list = " ".join(f"wd:{qid}" for qid in discipline_qids)

        sparql_query = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?person ?personLabel ?discipline ?disciplineLabel
        WHERE {{
          ?person wdt:P101 ?discipline .
          ?discipline wdt:P31 wd:Q11862829 .  # instance of: academic discipline
          VALUES ?discipline {{ {qid_list} }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        LIMIT 10000
        """

        try:
            results = self._execute_sparql(sparql_query)
            for binding in results.get("results", {}).get("bindings", []):
                person_qid = binding.get("person", {}).get("value", "").split("/")[-1]
                person_label = binding.get("personLabel", {}).get("value", "")
                discipline_qid = binding.get("discipline", {}).get("value", "").split("/")[-1]
                discipline_label = binding.get("disciplineLabel", {}).get("value", "")

                if person_qid and discipline_qid:
                    prop = AcademicProperty(
                        source_qid=person_qid,
                        source_label=person_label,
                        source_type="person",
                        property_type="P101",
                        target_qid=discipline_qid,
                        target_label=discipline_label,
                        target_type="discipline",
                        confidence=0.95,
                    )
                    properties.append(prop)

            logger.info(f"  → Found {len(properties)} P101 relationships")
            self.properties.extend(properties)
            return properties

        except Exception as e:
            logger.error(f"Error harvesting P101: {e}")
            return []

    def harvest_p2578_studies(
        self,
        discipline_qids: List[str],
    ) -> List[AcademicProperty]:
        """
        Harvest P2578 (studies): Discipline → Object of Study

        SPARQL Pattern:
          ?discipline wdt:P2578 ?object
          WHERE ?discipline is one of discipline_qids

        Args:
            discipline_qids: List of discipline QIDs

        Returns:
            List of AcademicProperty objects
        """

        logger.info(f"Harvesting P2578 (studies) for {len(discipline_qids)} disciplines")

        properties = []
        qid_list = " ".join(f"wd:{qid}" for qid in discipline_qids)

        sparql_query = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?discipline ?disciplineLabel ?object ?objectLabel ?objectType
        WHERE {{
          VALUES ?discipline {{ {qid_list} }}
          ?discipline wdt:P2578 ?object .
          OPTIONAL {{ ?object wdt:P31 ?objectType . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        LIMIT 5000
        """

        try:
            results = self._execute_sparql(sparql_query)
            for binding in results.get("results", {}).get("bindings", []):
                discipline_qid = binding.get("discipline", {}).get("value", "").split("/")[-1]
                discipline_label = binding.get("disciplineLabel", {}).get("value", "")
                object_qid = binding.get("object", {}).get("value", "").split("/")[-1]
                object_label = binding.get("objectLabel", {}).get("value", "")

                if discipline_qid and object_qid:
                    prop = AcademicProperty(
                        source_qid=discipline_qid,
                        source_label=discipline_label,
                        source_type="discipline",
                        property_type="P2578",
                        target_qid=object_qid,
                        target_label=object_label,
                        target_type="concept",
                        confidence=0.95,
                    )
                    properties.append(prop)

            logger.info(f"  → Found {len(properties)} P2578 relationships")
            self.properties.extend(properties)
            return properties

        except Exception as e:
            logger.error(f"Error harvesting P2578: {e}")
            return []

    def harvest_p921_main_subject(
        self,
        topic_qids: List[str],
    ) -> List[AcademicProperty]:
        """
        Harvest P921 (main subject): Work → Topic

        SPARQL Pattern:
          ?work wdt:P921 ?topic
          WHERE ?topic is one of topic_qids

        Args:
            topic_qids: List of topic QIDs to find works about

        Returns:
            List of AcademicProperty objects
        """

        logger.info(f"Harvesting P921 (main subject) for {len(topic_qids)} topics")

        properties = []
        qid_list = " ".join(f"wd:{qid}" for qid in topic_qids)

        sparql_query = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?work ?workLabel ?workType ?topic ?topicLabel
        WHERE {{
          ?work wdt:P921 ?topic .
          VALUES ?topic {{ {qid_list} }}
          OPTIONAL {{ ?work wdt:P31 ?workType . }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        LIMIT 10000
        """

        try:
            results = self._execute_sparql(sparql_query)
            for binding in results.get("results", {}).get("bindings", []):
                work_qid = binding.get("work", {}).get("value", "").split("/")[-1]
                work_label = binding.get("workLabel", {}).get("value", "")
                topic_qid = binding.get("topic", {}).get("value", "").split("/")[-1]
                topic_label = binding.get("topicLabel", {}).get("value", "")

                if work_qid and topic_qid:
                    prop = AcademicProperty(
                        source_qid=work_qid,
                        source_label=work_label,
                        source_type="work",
                        property_type="P921",
                        target_qid=topic_qid,
                        target_label=topic_label,
                        target_type="concept",
                        confidence=0.95,
                    )
                    properties.append(prop)

            logger.info(f"  → Found {len(properties)} P921 relationships")
            self.properties.extend(properties)
            return properties

        except Exception as e:
            logger.error(f"Error harvesting P921: {e}")
            return []

    def harvest_p1269_facet_of(
        self,
        concept_qids: List[str],
    ) -> List[AcademicProperty]:
        """
        Harvest P1269 (facet of): Aspect → Broader Concept

        SPARQL Pattern:
          ?aspect wdt:P1269 ?broader_concept
          WHERE ?broader_concept is one of concept_qids

        Args:
            concept_qids: List of broader concept QIDs

        Returns:
            List of AcademicProperty objects
        """

        logger.info(f"Harvesting P1269 (facet of) for {len(concept_qids)} concepts")

        properties = []
        qid_list = " ".join(f"wd:{qid}" for qid in concept_qids)

        sparql_query = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?aspect ?aspectLabel ?broader ?broaderLabel
        WHERE {{
          ?aspect wdt:P1269 ?broader .
          VALUES ?broader {{ {qid_list} }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        LIMIT 5000
        """

        try:
            results = self._execute_sparql(sparql_query)
            for binding in results.get("results", {}).get("bindings", []):
                aspect_qid = binding.get("aspect", {}).get("value", "").split("/")[-1]
                aspect_label = binding.get("aspectLabel", {}).get("value", "")
                broader_qid = binding.get("broader", {}).get("value", "").split("/")[-1]
                broader_label = binding.get("broaderLabel", {}).get("value", "")

                if aspect_qid and broader_qid:
                    prop = AcademicProperty(
                        source_qid=aspect_qid,
                        source_label=aspect_label,
                        source_type="concept",
                        property_type="P1269",
                        target_qid=broader_qid,
                        target_label=broader_label,
                        target_type="concept",
                        confidence=0.95,
                    )
                    properties.append(prop)

            logger.info(f"  → Found {len(properties)} P1269 relationships")
            self.properties.extend(properties)
            return properties

        except Exception as e:
            logger.error(f"Error harvesting P1269: {e}")
            return []

    def harvest_domain(
        self,
        domain: str = "Roman Republic",
    ) -> Dict[str, List[AcademicProperty]]:
        """
        Harvest all academic properties for a domain.

        Args:
            domain: Domain name (e.g., "Roman Republic")

        Returns:
            Dict with keys: "P101", "P2578", "P921", "P1269"
        """

        logger.info(f"Starting harvest for domain: {domain}")

        disciplines = DOMAIN_DISCIPLINE_MAPPINGS.get(domain, [])
        if not disciplines:
            logger.error(f"Domain {domain} not found in mappings")
            return {}

        discipline_qids = [qid for qid, _ in disciplines]

        results = {
            "P101": self.harvest_p101_field_of_work(discipline_qids),
            "P2578": self.harvest_p2578_studies(discipline_qids),
            "P921": self.harvest_p921_main_subject(discipline_qids),
            "P1269": self.harvest_p1269_facet_of(discipline_qids),
        }

        logger.info(f"Harvest complete. Total properties: {len(self.properties)}")
        return results

    def save_to_csv(self, filename: str = "academic_properties.csv") -> Path:
        """
        Save harvested properties to CSV for Neo4j import.

        CSV format:
          source_qid, source_label, source_type, property_type, target_qid, target_label, target_type

        Args:
            filename: Output CSV filename

        Returns:
            Path to saved file
        """

        filepath = self.output_dir / filename
        logger.info(f"Saving {len(self.properties)} properties to {filepath}")

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "source_qid",
                        "source_label",
                        "source_type",
                        "property_type",
                        "target_qid",
                        "target_label",
                        "target_type",
                        "confidence",
                    ],
                )
                writer.writeheader()
                for prop in self.properties:
                    writer.writerow(asdict(prop))

            logger.info(f"Saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return None

    def save_to_json(self, filename: str = "academic_properties.json") -> Path:
        """
        Save harvested properties to JSON.

        Args:
            filename: Output JSON filename

        Returns:
            Path to saved file
        """

        filepath = self.output_dir / filename
        logger.info(f"Saving {len(self.properties)} properties to {filepath}")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    [asdict(prop) for prop in self.properties],
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            logger.info(f"Saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return None

    def save_cypher_import_script(
        self,
        filename: str = "import_academic_properties.cypher",
    ) -> Path:
        """
        Generate Cypher script to load properties into Neo4j.

        Args:
            filename: Output Cypher filename

        Returns:
            Path to saved file
        """

        filepath = self.output_dir / filename
        logger.info(f"Generating Cypher import script: {filepath}")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("// Auto-generated Cypher import script\n")
                f.write(f"// Generated: {datetime.now().isoformat()}\n")
                f.write("// Load academic properties from Wikidata\n\n")

                # Group by property type
                by_property = {}
                for prop in self.properties:
                    if prop.property_type not in by_property:
                        by_property[prop.property_type] = []
                    by_property[prop.property_type].append(prop)

                for property_type, props in by_property.items():
                    f.write(f"\n// ===== {property_type} ({len(props)} relationships) =====\n\n")

                    for prop in props:
                        # Map property types to Neo4j relationship names
                        rel_map = {
                            "P101": "FIELD_OF_WORK",
                            "P2578": "STUDIES",
                            "P921": "MAIN_SUBJECT",
                            "P1269": "FACET_OF",
                        }
                        rel_type = rel_map[property_type]

                        f.write(
                            f"// {prop.source_label} -{rel_type}-> {prop.target_label}\n"
                        )
                        f.write(
                            f"MATCH (source {{qid: '{prop.source_qid}'}}) "
                        )
                        f.write(
                            f"MATCH (target {{qid: '{prop.target_qid}'}}) "
                        )
                        f.write(
                            f"CREATE (source)-[:{rel_type} "
                            f"{{source: 'wikidata', property: '{property_type}', "
                            f"confidence: {prop.confidence}}}]->(target);\n"
                        )

            logger.info(f"Generated {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generating Cypher script: {e}")
            return None

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def _execute_sparql(self, query: str) -> Dict:
        """
        Execute SPARQL query against Wikidata endpoint.

        Args:
            query: SPARQL query string

        Returns:
            JSON response from Wikidata
        """

        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "Chrystallum/1.0",
        }

        try:
            response = requests.get(
                WIKIDATA_SPARQL_ENDPOINT,
                params={"query": query},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"SPARQL query failed: {e}")
            return {}

    def get_statistics(self) -> Dict:
        """Get statistics about harvested properties"""

        by_property = {}
        by_source_type = {}
        by_target_type = {}

        for prop in self.properties:
            by_property[prop.property_type] = by_property.get(prop.property_type, 0) + 1
            by_source_type[prop.source_type] = by_source_type.get(prop.source_type, 0) + 1
            by_target_type[prop.target_type] = by_target_type.get(prop.target_type, 0) + 1

        return {
            "total_properties": len(self.properties),
            "by_property_type": by_property,
            "by_source_type": by_source_type,
            "by_target_type": by_target_type,
        }


if __name__ == "__main__":
    import sys

    harvester = AcademicPropertyHarvester()

    # Harvest for Roman Republic
    print("Harvesting academic properties for Roman Republic...")
    harvester.harvest_domain("Roman Republic")

    # Print statistics
    stats = harvester.get_statistics()
    print("\nHarvest Statistics:")
    print(json.dumps(stats, indent=2))

    # Save outputs
    harvester.save_to_csv("academic_properties_roman_republic.csv")
    harvester.save_to_json("academic_properties_roman_republic.json")
    harvester.save_cypher_import_script("import_academic_properties_roman_republic.cypher")

    print("\nFiles saved to CSV/ directory")
