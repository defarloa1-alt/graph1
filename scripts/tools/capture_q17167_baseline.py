#!/usr/bin/env python3
"""Capture Q17167 Roman Republic facet hierarchy baseline for docs."""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
with driver.session(database=NEO4J_DATABASE) as s:
    baseline = {
        "captured": date.today().isoformat(),
        "database": NEO4J_DATABASE,
        "uri_host": NEO4J_URI.split("@")[-1] if "@" in NEO4J_URI else NEO4J_URI,
        "subject_domain": dict(
            s.run(
                """
                MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
                RETURN sd.domain_id AS domain_id, sd.label AS label,
                       sd.seed_qid AS seed_qid, elementId(sd) AS eid
                """
            ).single()
        ),
        "period": dict(
            s.run(
                """
                MATCH (p:Period {qid: 'Q17167'})
                RETURN p.qid AS qid, p.label AS label, elementId(p) AS eid
                """
            ).single()
        ),
        "facet_umbrellas": [
            dict(r)
            for r in s.run(
                """
                MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
                      -[:HAS_SUBJECT_CONCEPT]->(u:FacetUmbrella)
                OPTIONAL MATCH (u)<-[:PART_OF]-(sc:SubjectConcept {source: 'di_proposal'})
                RETURN u.subject_id AS subject_id, u.label AS label,
                       u.source_facet AS facet, count(sc) AS decompositions
                ORDER BY facet
                """
            )
        ],
        "domain_edges": [
            dict(r)
            for r in s.run(
                """
                MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})-[r]->(n)
                RETURN type(r) AS rel, labels(n)[0] AS target,
                       coalesce(n.source, n.qid, n.code) AS key, count(*) AS cnt
                ORDER BY rel, key
                """
            )
        ],
        "domain_incoming_sc": s.run(
            """
            MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
                  <-[:SCOPED_TO|PART_OF|HAS_SUBJECT_CONCEPT]-(sc:SubjectConcept)
            RETURN count(sc) AS cnt
            """
        ).single()["cnt"],
        "di_proposals": {
            "total": s.run(
                "MATCH (sc:SubjectConcept {source: 'di_proposal', seed_qid: 'Q17167'}) RETURN count(sc) AS c"
            ).single()["c"],
            "part_of_umbrella": s.run(
                """
                MATCH (sc:SubjectConcept {source: 'di_proposal', seed_qid: 'Q17167'})
                      -[:PART_OF]->(:FacetUmbrella)
                RETURN count(sc) AS c
                """
            ).single()["c"],
            "scoped_to_domain": s.run(
                """
                MATCH (sc:SubjectConcept {source: 'di_proposal', seed_qid: 'Q17167'})
                      -[:SCOPED_TO]->(:SubjectDomain)
                RETURN count(sc) AS c
                """
            ).single()["c"],
        },
        "sfa_training": [
            dict(r)
            for r in s.run(
                """
                MATCH (tr:SFA_TrainingRun {seed_qid: 'Q17167'})
                OPTIONAL MATCH (tr)-[:RELEVANT_TO_SUBJECT]->(u:FacetUmbrella)
                RETURN tr.facet_key AS facet, tr.run_id AS run_id, u.subject_id AS umbrella
                ORDER BY facet, run_id
                """
            )
        ],
        "bootstrap_orphans": {
            "ccs_bootstrap": s.run(
                "MATCH (sc:SubjectConcept {source: 'ccs_bootstrap'}) RETURN count(sc) AS c"
            ).single()["c"],
            "on_domain": s.run(
                """
                MATCH (:SubjectDomain {domain_id: 'domain_roman_republic'})
                      -[:HAS_SUBJECT_CONCEPT]->(sc)
                WHERE sc.source <> 'di_facet_umbrella'
                RETURN count(sc) AS c
                """
            ).single()["c"],
        },
        "uses_type": [
            dict(r)
            for r in s.run(
                """
                MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
                      -[:USES_TYPE]->(wt:WikidataType)
                RETURN wt.qid AS qid, wt.label AS label
                """
            )
        ],
    }
driver.close()

out_path = ROOT / "output" / "baseline" / "Q17167_facet_hierarchy_baseline.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(baseline, f, indent=2, ensure_ascii=False)
print(json.dumps(baseline, indent=2, ensure_ascii=False))
print(f"\nWrote {out_path}")
