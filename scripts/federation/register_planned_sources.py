#!/usr/bin/env python3
"""
Register planned federation sources: Open Syllabus, Open Library, OpenAlex, Perseus.
Based on SFA_INDEX_READER_Spec_v1 (Table 13) and D-039 architectural decision.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

SOURCES = [
    {
        "source_id": "open_syllabus",
        "label": "Open Syllabus",
        "status": "planned",
        "phase": "D",
        "endpoint": "https://api.opensyllabus.org/",
        "access": "data_agreement_required",
        "scoping_weight": 0.0,
        "description": (
            "Teaching importance scores and co-assignment networks across 15.7M syllabi. "
            "Provides teaching_score and TAUGHT_WITH relationships for Work nodes. "
            "Requires data access agreement application."
        ),
        "data_types": "title, author, ISBN, teaching_score, co_assignments",
        "use_in_chrystallum": "Work node enrichment step 1 in SFA_INDEX_READER bibliographic bootstrap",
        "added_date": "2026-03-01",
    },
    {
        "source_id": "open_library",
        "label": "Open Library",
        "status": "planned",
        "phase": "D",
        "endpoint": "https://openlibrary.org/api/books",
        "access": "free_no_key",
        "scoping_weight": 0.0,
        "description": (
            "ISBN to OCLC/LCCN/subjects bridge via Internet Archive. "
            "Links Work nodes to existing LCSH/FAST federation. "
            "Full-text availability flag via Internet Archive."
        ),
        "data_types": "ISBN, OCLC, LCCN, subjects, full_text_flag",
        "use_in_chrystallum": "Work node enrichment step 2 in SFA_INDEX_READER bibliographic bootstrap",
        "added_date": "2026-03-01",
    },
    {
        "source_id": "open_alex",
        "label": "OpenAlex",
        "status": "planned",
        "phase": "D",
        "endpoint": "https://api.openalex.org/works",
        "access": "free_no_key",
        "scoping_weight": 0.0,
        "description": (
            "Secondary scholarship index with 240M+ works. "
            "Open access detection, citation graphs, topic classification. "
            "Free API with concept/topic filters for Roman Republic secondary scholarship. "
            "OA URL enables agent-accessible full text."
        ),
        "data_types": "DOI, open_access, oa_url, cited_by_count, topics, referenced_works",
        "use_in_chrystallum": (
            "Work node enrichment step 3; "
            "secondary scholarship harvest by concept filter (Roman Republic, Classical Antiquity)"
        ),
        "added_date": "2026-03-01",
    },
    {
        "source_id": "perseus_digital_library",
        "label": "Perseus Digital Library",
        "status": "planned",
        "phase": "D",
        "endpoint": "https://catalog.perseus.org/",
        "access": "free_public",
        "scoping_weight": 0.0,
        "description": (
            "Canonical classical text identifiers via CTS URNs. "
            "~950 authors, 3200+ works. Passage-level addressing for primary source citations. "
            "Latin and Greek primary texts with stable URIs."
        ),
        "data_types": "CTS_URN, author, title, language, passage_text",
        "use_in_chrystallum": (
            "Primary source Work nodes; "
            "passage-level provenance for claim chains (e.g. Polybius 3.50.1)"
        ),
        "added_date": "2026-03-01",
    },
]

CYPHER = """
MERGE (fs:SYS_FederationSource {source_id: $source_id})
SET fs.label              = $label,
    fs.status             = $status,
    fs.phase              = $phase,
    fs.endpoint           = $endpoint,
    fs.access             = $access,
    fs.scoping_weight     = $scoping_weight,
    fs.description        = $description,
    fs.data_types         = $data_types,
    fs.use_in_chrystallum = $use_in_chrystallum,
    fs.added_date         = $added_date
RETURN fs.label AS label, fs.status AS status
"""

RELATIONSHIP_TYPES = [
    # From SFA_INDEX_READER_Spec_v1 Table 7 — not yet in SYS_RelationshipType
    {"rel_type": "ALLIED_WITH",        "domain": "Entity",  "range": "Entity",  "facet": "POLITICAL",                 "source": "index_reader_spec"},
    {"rel_type": "SUPPORTER_OF",       "domain": "Entity",  "range": "Entity",  "facet": "POLITICAL",                 "source": "index_reader_spec"},
    {"rel_type": "DECLARED_HOSTIS",    "domain": "Entity",  "range": "Entity",  "facet": "POLITICAL",                 "source": "index_reader_spec"},
    {"rel_type": "PROSCRIBED",         "domain": "Entity",  "range": "Entity",  "facet": "POLITICAL",                 "source": "index_reader_spec"},
    {"rel_type": "SERVED_UNDER",       "domain": "Entity",  "range": "Entity",  "facet": "POLITICAL",                 "source": "index_reader_spec"},
    {"rel_type": "DESCENDANT_OF",      "domain": "Entity",  "range": "Entity",  "facet": "BIOGRAPHIC",                "source": "index_reader_spec"},
    {"rel_type": "MARRIED_INTO",       "domain": "Entity",  "range": "Entity",  "facet": "SOCIAL",                    "source": "index_reader_spec"},
    {"rel_type": "HAS_LINEAGE",        "domain": "Entity",  "range": "Entity",  "facet": "BIOGRAPHIC",                "source": "index_reader_spec"},
    {"rel_type": "HELD_PRIESTHOOD",    "domain": "Entity",  "range": "Position","facet": "RELIGIOUS",                 "source": "index_reader_spec"},
    {"rel_type": "SUBJECT_OF_WORK",    "domain": "Entity",  "range": "Work",    "facet": "ARTISTIC",                  "source": "index_reader_spec"},
    {"rel_type": "INVOLVED_IN_EVENT",  "domain": "Entity",  "range": "Event",   "facet": "POLITICAL",                 "source": "index_reader_spec"},
    {"rel_type": "TAUGHT_WITH",        "domain": "Work",    "range": "Work",    "facet": "INTELLECTUAL",              "source": "open_syllabus_coassignment"},
    {"rel_type": "CITES",              "domain": "Work",    "range": "Work",    "facet": "INTELLECTUAL",              "source": "openalex_citation_graph"},
    {"rel_type": "AUTHORED_BY",        "domain": "Work",    "range": "Entity",  "facet": "INTELLECTUAL",              "source": "works_layer"},
    {"rel_type": "EVIDENCED_IN",       "domain": "Claim",   "range": "Work",    "facet": None,                        "source": "claim_provenance"},
]

REL_CYPHER = """
MERGE (rt:SYS_RelationshipType {rel_type: $rel_type})
SET rt.domain  = $domain,
    rt.range   = $range,
    rt.facet   = $facet,
    rt.source  = $source,
    rt.added_date = '2026-03-01'
RETURN rt.rel_type AS rel_type
"""

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        print("=== Registering planned federation sources ===")
        for src in SOURCES:
            result = session.run(CYPHER, **src)
            rec = result.single()
            print(f"  {rec['label']} [{rec['status']}]")

        total = session.run(
            "MATCH (fs:SYS_FederationSource) RETURN count(fs) AS c"
        ).single()["c"]
        print(f"  Total SYS_FederationSource: {total}")

        print()
        print("=== Adding Index Reader relationship types to SYS_RelationshipType ===")
        for rt in RELATIONSHIP_TYPES:
            result = session.run(REL_CYPHER, **rt)
            rec = result.single()
            print(f"  {rec['rel_type']}")

        total_rt = session.run(
            "MATCH (rt:SYS_RelationshipType) RETURN count(rt) AS c"
        ).single()["c"]
        print(f"  Total SYS_RelationshipType: {total_rt}")

        print()
        print("=== Registering SFA_INDEX_READER agent ===")
        session.run("""
            MERGE (a:Agent {agent_id: 'SFA_INDEX_READER'})
            SET a.agent_type          = 'BIBLIOGRAPHIC_SPECIALIST',
                a.authority_tier      = 'Agent-Discovered',
                a.confidence_ceiling  = 0.82,
                a.input_modality      = 'image_or_ocr_text',
                a.output_types        = 'ScaffoldNode, ScaffoldEdge, Claim',
                a.facet_scope         = 'ALL',
                a.governing_policies  = 'ApprovalRequired, NoTemporalFacet',
                a.spec_version        = '1.0',
                a.spec_date           = '2026-03-01',
                a.status              = 'spec_only'
        """)
        print("  SFA_INDEX_READER agent node created")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
