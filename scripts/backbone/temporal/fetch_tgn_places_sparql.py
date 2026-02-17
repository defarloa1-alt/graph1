#!/usr/bin/env python3
"""
Fetch Getty TGN places via SPARQL and import to Neo4j.
Recommended for region normalization in period modeling.
"""
import requests
from typing import List, Dict
from neo4j import GraphDatabase

# --- CONFIG ---
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "Chrystallum"

SPARQL_ENDPOINT = "https://vocab.getty.edu/sparql.json"

# --- SPARQL QUERY ---
MEDITERRANEAN_TGN_ID = "7006667"  # Mediterranean Basin

SPARQL_QUERY = f"""
PREFIX gvp: <http://vocab.getty.edu/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX wgs84: <http://www.w3.org/2003/01/geo/wgs84_pos#>

SELECT ?place ?name ?lat ?long ?parent
WHERE {{
    ?place gvp:broaderExtended <http://vocab.getty.edu/tgn/{MEDITERRANEAN_TGN_ID}> .
    ?place skos:prefLabel ?name .
    FILTER(lang(?name) = "en")
    OPTIONAL {{ ?place wgs84:lat ?lat }}
    OPTIONAL {{ ?place wgs84:long ?long }}
    OPTIONAL {{ ?place gvp:broaderPreferred ?parent }}
}}
LIMIT 5000
"""

def fetch_places() -> List[Dict]:
    """Fetch places in the Mediterranean region from Getty TGN via SPARQL."""
    response = requests.post(
        SPARQL_ENDPOINT,
        data={"query": SPARQL_QUERY},
        headers={"Accept": "application/sparql-results+json"}
    )
    response.raise_for_status()
    data = response.json()
    results = []
    for row in data["results"]["bindings"]:
        tgn_id = row["place"]["value"].split("/")[-1]
        name = row["name"]["value"]
        lat = float(row["lat"]["value"]) if "lat" in row else None
        long = float(row["long"]["value"]) if "long" in row else None
        parent = row["parent"]["value"].split("/")[-1] if "parent" in row else None
        results.append({
            "tgn_id": tgn_id,
            "label": name,
            "latitude": lat,
            "longitude": long,
            "parent_tgn": parent
        })
    return results

def import_to_neo4j(places: List[Dict]):
    """Import fetched places into Neo4j as Place nodes."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    with driver.session() as session:
        for place in places:
            session.run("""
                MERGE (p:Place {getty_tgn: $tgn_id})
                SET p.qid = $qid,
                    p.label = $label,
                    p.latitude = $latitude,
                    p.longitude = $longitude,
                    p.source = 'Getty TGN',
                    p.entity_type = 'place'
            """,
            tgn_id=place["tgn_id"],
            qid=f"tgn:{place['tgn_id']}",
            label=place["label"],
            latitude=place["latitude"],
            longitude=place["longitude"])
            if place["parent_tgn"]:
                session.run("""
                    MATCH (child:Place {getty_tgn: $child_id})
                    MERGE (parent:Place {getty_tgn: $parent_id})
                    ON CREATE SET
                        parent.qid = $parent_qid,
                        parent.entity_type = 'place',
                        parent.source = 'Getty TGN'
                    MERGE (child)-[:PART_OF]->(parent)
                """,
                child_id=place["tgn_id"],
                parent_id=place["parent_tgn"],
                parent_qid=f"tgn:{place['parent_tgn']}")
    driver.close()

def main():
    print("Fetching Getty TGN places via SPARQL...")
    places = fetch_places()
    print(f"Fetched {len(places)} places.")
    print("Importing to Neo4j...")
    import_to_neo4j(places)
    print("Done.")

if __name__ == "__main__":
    main()
