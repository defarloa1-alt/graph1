#!/usr/bin/env python3
"""
Wire ROUTES_TO relationships between Discipline and SYS_FederationSource nodes
based on scope relevance (not external IDs).

Strategy:
- Universal federations: all disciplines
- Domain federations: seed disciplines + all SUBCLASS_OF descendants
- Relationship carries: scope_basis (why this link exists)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

# ── Universal federations: every discipline routes to these ──────────────
UNIVERSAL = [
    "wikidata",       # everything has a QID
    "lcsh_fast_lcc",  # library classification backbone
    "open_alex",      # scholarly literature for any discipline
    "open_library",   # books for any discipline
]

# ── Domain federations: seed labels + propagation ────────────────────────
# Each entry: federation_source_id -> {
#   "seeds": list of discipline labels that are direct matches,
#   "patterns": list of substrings to match in discipline labels,
#   "basis": why this routing exists
# }
DOMAIN_FEDERATIONS = {
    "dprr": {
        "seeds": [
            "history of Rome", "history of Italy", "history of Europe",
            "legal history", "military history", "political science",
            "classical philology", "study of history", "historiography",
            "numismatics", "etruscology",
        ],
        "patterns": ["roman", "latin", "prosop"],
        "basis": "Roman Republic prosopography; persons, offices, political careers",
    },
    "pleiades": {
        "seeds": [
            "archaeology", "historical geography",
            "history of Rome", "history of Greece", "history of Europe",
            "classical philology", "etruscology",
            "numismatics", "medieval studies",
        ],
        "patterns": ["ancient", "classic", "roman", "greek", "latin", "archae", "epigrap"],
        "basis": "Ancient places gazetteer; geographic data for classical world",
    },
    "trismegistos": {
        "seeds": [
            "Egyptology", "archaeology", "classical philology",
            "palaeography", "linguistics", "philology",
            "history of Rome", "history of Greece",
        ],
        "patterns": ["papyr", "epigrap", "ancient", "egypt"],
        "basis": "Papyrological/epigraphic texts; ancient document metadata",
    },
    "lgpn": {
        "seeds": [
            "history of Greece", "classical philology",
            "archaeology", "etruscology",
        ],
        "patterns": ["greek", "prosop", "onomast"],
        "basis": "Greek personal names; prosopographic data for Greek world",
    },
    "edh": {
        "seeds": [
            "history of Rome", "classical philology",
            "archaeology", "etruscology",
        ],
        "patterns": ["epigrap", "latin", "roman", "inscript"],
        "basis": "Latin inscriptions; epigraphic texts and metadata",
    },
    "periodo": {
        "seeds": [
            "study of history", "historiography", "archaeology",
            "history of Europe", "history of Rome", "history of Greece",
            "history of France", "history of Spain", "history of Portugal",
            "history of Italy", "history of Germany", "history of Poland",
            "medieval studies", "Egyptology", "art history",
            "world history", "church history", "military history",
            "diplomatic history", "ethnohistory", "legal history",
            "women's history", "history of religions",
            "history of science", "history of medicine",
            "history of astronomy", "history of ideas",
            "history of international relations",
            "natural history", "palaeography", "numismatics",
            "auxiliary science of history",
        ],
        "patterns": ["histor", "archae", "paleont", "medieva"],
        "basis": "Historical period definitions; temporal authority for any historical discipline",
    },
    "perseus_digital_library": {
        "seeds": [
            "classical philology", "history of Rome", "history of Greece",
            "philology", "archaeology",
        ],
        "patterns": ["classic", "greek", "latin", "roman", "ancient"],
        "basis": "Classical texts corpus; Greek/Latin primary sources",
    },
    "chrr": {
        "seeds": ["numismatics", "history of Rome", "etruscology"],
        "patterns": ["roman", "numism", "coin"],
        "basis": "Coinage of the Roman Republic; numismatic evidence",
    },
    "crro": {
        "seeds": ["numismatics", "history of Rome", "etruscology"],
        "patterns": ["roman", "numism", "coin"],
        "basis": "Coinage of the Roman Republic Online; numismatic data",
    },
    "ocd": {
        "seeds": [
            "classical philology", "history of Rome", "history of Greece",
            "archaeology", "philology", "etruscology",
            "numismatics", "art history", "military history",
        ],
        "patterns": ["classic", "ancient", "greek", "roman", "latin"],
        "basis": "Oxford Classical Dictionary; encyclopedic reference for classical world",
    },
    "getty_aat": {
        "seeds": [
            "art", "art history", "architecture", "archaeology",
            "museology", "design", "heraldry",
        ],
        "patterns": ["art", "visual", "decorat", "material culture", "aesthet", "archit"],
        "basis": "Art & Architecture Thesaurus; material culture and visual arts vocabulary",
    },
    "viaf": {
        "seeds": [
            "study of history", "philology", "classical philology",
            "linguistics", "art history",
        ],
        "patterns": [],
        "basis": "Virtual International Authority File; person/org authority across libraries",
    },
    "open_syllabus": {
        "seeds": [],
        "patterns": ["education", "pedagog", "teaching", "curricul"],
        "basis": "Teaching/syllabus data; what gets taught in universities",
    },
}


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 0. Load all disciplines
        result = session.run("MATCH (d:Discipline) RETURN d.qid as qid, d.label as label")
        all_discs = {r["qid"]: r["label"] for r in result}
        print(f"Total disciplines: {len(all_discs)}")

        # Build label -> qid lookup (lowercase)
        label_to_qid = {}
        for qid, label in all_discs.items():
            if label:
                label_to_qid[label.lower()] = qid

        # Load SUBCLASS_OF tree for descendant propagation
        result = session.run(
            "MATCH (child:Discipline)-[:SUBCLASS_OF]->(parent:Discipline) "
            "RETURN child.qid as child, parent.qid as parent"
        )
        children_of = {}  # parent_qid -> [child_qids]
        for r in result:
            children_of.setdefault(r["parent"], []).append(r["child"])

        def get_descendants(qid, visited=None):
            """Get all descendants of a discipline via SUBCLASS_OF."""
            if visited is None:
                visited = set()
            if qid in visited:
                return set()
            visited.add(qid)
            desc = set()
            for child in children_of.get(qid, []):
                desc.add(child)
                desc |= get_descendants(child, visited)
            return desc

        # 1. Universal federations
        for source_id in UNIVERSAL:
            result = session.run("""
                MATCH (d:Discipline)
                MATCH (f:SYS_FederationSource {source_id: $source_id})
                MERGE (d)-[r:ROUTES_TO]->(f)
                SET r.scope_basis = 'universal'
                RETURN count(r) as cnt
            """, source_id=source_id)
            cnt = result.single()["cnt"]
            print(f"  ROUTES_TO {source_id}: {cnt} (universal)")

        # 2. Domain federations: seeds + pattern matches + descendants
        for source_id, config in DOMAIN_FEDERATIONS.items():
            seed_qids = set()

            # Direct seed labels
            for seed_label in config["seeds"]:
                qid = label_to_qid.get(seed_label.lower())
                if qid:
                    seed_qids.add(qid)

            # Pattern matches
            for qid, label in all_discs.items():
                if not label:
                    continue
                lower = label.lower()
                for pattern in config["patterns"]:
                    if pattern.lower() in lower:
                        seed_qids.add(qid)
                        break

            # Propagate to descendants
            all_qids = set(seed_qids)
            for sq in seed_qids:
                all_qids |= get_descendants(sq)

            # Write relationships
            if all_qids:
                result = session.run("""
                    UNWIND $qids AS qid
                    MATCH (d:Discipline {qid: qid})
                    MATCH (f:SYS_FederationSource {source_id: $source_id})
                    MERGE (d)-[r:ROUTES_TO]->(f)
                    SET r.scope_basis = $basis
                    RETURN count(r) as cnt
                """, qids=list(all_qids), source_id=source_id, basis=config["basis"])
                cnt = result.single()["cnt"]
            else:
                cnt = 0

            print(f"  ROUTES_TO {source_id}: {cnt} ({len(seed_qids)} seeds + {cnt - len(seed_qids)} descendants)")

        # 3. Summary
        print("\n── Final ROUTES_TO summary ──")
        result = session.run("""
            MATCH (:Discipline)-[r:ROUTES_TO]->(f:SYS_FederationSource)
            RETURN f.source_id as source, count(r) as cnt
            ORDER BY cnt DESC
        """)
        for record in result:
            print(f"  {record['source']:30s} {record['cnt']}")

        result = session.run(
            "MATCH (:Discipline)-[r:ROUTES_TO]->(:SYS_FederationSource) RETURN count(r) as total"
        )
        print(f"\nTotal: {result.single()['total']} ROUTES_TO relationships")

        # How many disciplines route to at least one domain federation?
        result = session.run("""
            MATCH (d:Discipline)-[:ROUTES_TO]->(f:SYS_FederationSource)
            WHERE f.source_id NOT IN ['wikidata', 'lcsh_fast_lcc', 'open_alex', 'open_library']
            RETURN count(DISTINCT d) as cnt
        """)
        print(f"Disciplines with domain-specific routing: {result.single()['cnt']}/675")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
