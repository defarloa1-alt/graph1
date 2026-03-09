"""
write_subject_concepts.py

Reads Q17167_subject_schema.json and writes 20 SubjectConcept nodes to Neo4j.
Each node is wired to:
  - Facet nodes via HAS_PRIMARY_FACET / HAS_SECONDARY_FACET
  - Seed domain via MEMBER_OF (Q17167)

Idempotent (MERGE on concept_cipher).
"""

import json
from pathlib import Path
from neo4j import GraphDatabase
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "output/subject_schema/Q17167_subject_schema.json"

MERGE_CONCEPT = """
MERGE (sc:SubjectConcept {subject_id: $subject_id})
SET sc.concept_cipher   = $cipher,
    sc.label            = $label,
    sc.wikidata_qid     = $qid,
    sc.lcsh_id          = $lcsh_id,
    sc.lcsh_id_status   = $lcsh_id_status,
    sc.lcsh_heading     = $lcsh_heading,
    sc.lcsh_resolved    = $lcsh_resolved,
    sc.lcc_primary      = $lcc_primary,
    sc.lcc_codes        = $lcc_codes,
    sc.scope_note       = $scope_note,
    sc.seed_qid         = $seed_qid,
    sc.source           = 'domain_initiator',
    sc.updated          = datetime()
WITH sc

// Primary facet
MATCH (fp:Facet {label: $primary_facet})
MERGE (sc)-[:HAS_PRIMARY_FACET]->(fp)

// Secondary facets
WITH sc
UNWIND $secondary_facets AS sec
MATCH (fs:Facet {label: sec})
MERGE (sc)-[:HAS_SECONDARY_FACET]->(fs)
"""

WIRE_SEED = """
MATCH (sc:SubjectConcept {seed_qid: $seed_qid})
MATCH (seed:SubjectConcept {wikidata_qid: $seed_qid})
WHERE sc <> seed
MERGE (sc)-[:MEMBER_OF]->(seed)
"""

def main():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    seed_qid = schema["seed_qid"]
    concepts = schema["subject_concepts"]

    print(f"Writing {len(concepts)} SubjectConcepts for {seed_qid}")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    written = 0

    with driver.session() as session:
        for sc in concepts:
            cipher = sc.get("concept_cipher")
            if not cipher:
                print(f"  SKIP {sc['label']} — no cipher")
                continue

            qid = sc.get("wikidata_qid", "")
            subject_id = f"subj_{qid.lower()}" if qid and qid != "NEEDS_LOOKUP" else f"subj_{cipher[:12]}"

            params = {
                "cipher":           cipher,
                "subject_id":       subject_id,
                "label":            sc["label"],
                "qid":              sc.get("wikidata_qid", ""),
                "lcsh_id":          sc.get("lcsh_id", ""),
                "lcsh_id_status":   sc.get("lcsh_id_status", ""),
                "lcsh_heading":     sc.get("lcsh_heading", ""),
                "lcsh_resolved":    sc.get("lcsh_id_resolved_label", ""),
                "lcc_primary":      sc.get("lcc_primary", ""),
                "lcc_codes":        sc.get("lcc_codes", []),
                "scope_note":       sc.get("scope_note", ""),
                "seed_qid":         seed_qid,
                "primary_facet":    sc["facets"]["primary"],
                "secondary_facets": sc["facets"].get("secondary", []),
            }

            result = session.run(MERGE_CONCEPT, params)
            result.consume()
            written += 1
            pf = sc["facets"]["primary"]
            sf = sc["facets"].get("secondary", [])
            print(f"  {written:2}. {sc['label']:<48} {pf} + {sf}")

    # Verify
    with driver.session() as session:
        count = session.run(
            "MATCH (sc:SubjectConcept {seed_qid: $qid}) RETURN count(sc) AS c",
            {"qid": seed_qid}
        ).single()["c"]
        edges = session.run(
            "MATCH (sc:SubjectConcept {seed_qid: $qid})-[e]->(f:Facet) RETURN count(e) AS c",
            {"qid": seed_qid}
        ).single()["c"]
        print(f"\nGraph: {count} SubjectConcept nodes for {seed_qid}, {edges} facet edges")

    driver.close()


if __name__ == "__main__":
    main()
