#!/usr/bin/env python3
"""Validate Place schema: node counts, relationships, integrity checks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD or ""))

def run(session, query):
    r = session.run(query)
    return [dict(rec) for rec in r]

with driver.session() as s:
    print("=" * 60)
    print("PLACE SCHEMA VALIDATION")
    print("=" * 60)

    # 1. Node counts (separate queries to avoid empty MATCH breaking chain)
    total = run(s, "MATCH (p:Place) RETURN count(p) AS c")[0]["c"]
    by_pleiades = run(s, "MATCH (p:Place) WHERE p.pleiades_id IS NOT NULL RETURN count(p) AS c")[0]["c"]
    by_qid = run(s, "MATCH (p:Place) WHERE p.qid IS NOT NULL RETURN count(p) AS c")[0]["c"]
    by_geonames = run(s, "MATCH (p:Place) WHERE p.geonames_id IS NOT NULL RETURN count(p) AS c")[0]["c"]
    place_names = run(s, "MATCH (n:PlaceName) RETURN count(n) AS c")[0]["c"]
    locations = run(s, "MATCH (l:Location) RETURN count(l) AS c")[0]["c"]
    place_types = run(s, "MATCH (pt:PlaceType) RETURN count(pt) AS c")[0]["c"]
    pleiades_place = run(s, "MATCH (pp:Pleiades_Place) RETURN count(pp) AS c")[0]["c"]
    r = [{"total": total, "by_pleiades": by_pleiades, "by_qid": by_qid, "by_geonames": by_geonames,
          "place_names": place_names, "locations": locations, "place_types": place_types, "pleiades_place": pleiades_place}]
    if r:
        row = r[0]
        print("\n1. NODE COUNTS")
        print("-" * 40)
        print(f"  Place total:           {row['total']}")
        print(f"  Place (pleiades_id):    {row['by_pleiades']}")
        print(f"  Place (qid):            {row['by_qid']}")
        print(f"  Place (geonames_id):    {row['by_geonames']}")
        print(f"  PlaceName:              {row['place_names']}")
        print(f"  Location:               {row['locations']}")
        print(f"  PlaceType:              {row['place_types']}")
        print(f"  Pleiades_Place:         {row['pleiades_place']}")

    # 2. Relationship counts (separate queries; some rel types may not exist)
    def rel_count(rel_type):
        try:
            return run(s, f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS c")[0]["c"]
        except Exception:
            return 0
    has_name = rel_count("HAS_NAME")
    has_location = rel_count("HAS_LOCATION")
    instance_of_type = rel_count("INSTANCE_OF_PLACE_TYPE")
    located_in = rel_count("LOCATED_IN")
    aligned_geo = rel_count("ALIGNED_WITH_GEO_BACKBONE")
    print("\n2. RELATIONSHIP COUNTS")
    print("-" * 40)
    print(f"  Place -[:HAS_NAME]-> PlaceName:        {has_name}")
    print(f"  Place -[:HAS_LOCATION]-> Location:     {has_location}")
    print(f"  Place -[:INSTANCE_OF_PLACE_TYPE]->:   {instance_of_type}")
    print(f"  Place -[:LOCATED_IN]-> Place:          {located_in}")
    print(f"  Pleiades_Place -[:ALIGNED_WITH_GEO_BACKBONE]->: {aligned_geo}")

    # 3. Place without any ID
    r = run(s, """
        MATCH (p:Place)
        WHERE p.pleiades_id IS NULL AND p.qid IS NULL AND p.geonames_id IS NULL
        RETURN count(p) AS orphan
    """)
    orphan = r[0]["orphan"] if r else 0
    print("\n3. INTEGRITY")
    print("-" * 40)
    print(f"  Place without pleiades_id/qid/geonames_id: {orphan}")

    # 4. LOCATED_IN source breakdown
    r = run(s, """
        MATCH (c:Place)-[r:LOCATED_IN]->(p:Place)
        WHERE c.pleiades_id IS NOT NULL
        RETURN r.source AS src, count(r) AS cnt
        ORDER BY cnt DESC
    """)
    print("\n4. LOCATED_IN SOURCE (Pleiades Place -> parent)")
    print("-" * 40)
    for row in r:
        print(f"  {row['src'] or '(null)'}: {row['cnt']}")

    # 5. Sample Place (Rome 423025)
    r = run(s, """
        MATCH (p:Place {pleiades_id: '423025'})
        OPTIONAL MATCH (p)-[:HAS_NAME]->(n:PlaceName)
        OPTIONAL MATCH (p)-[:HAS_LOCATION]->(l:Location)
        OPTIONAL MATCH (p)-[:INSTANCE_OF_PLACE_TYPE]->(pt:PlaceType)
        OPTIONAL MATCH (p)-[:LOCATED_IN*1..3]->(anc:Place)
        RETURN p.label AS label, p.place_type AS place_type,
               collect(DISTINCT n.name_attested)[0..5] AS sample_names,
               count(DISTINCT l) AS loc_count,
               collect(DISTINCT pt.type_id)[0..3] AS types,
               [a IN collect(DISTINCT anc) | a.label + ' (' + coalesce(a.pleiades_id, a.qid, a.geonames_id, '') + ')'] AS hierarchy
    """)
    if r:
        row = r[0]
        print("\n5. SAMPLE: Rome (pleiades_id 423025)")
        print("-" * 40)
        print(f"  Label: {row['label']}, PlaceType: {row['place_type']}")
        print(f"  Names: {row['sample_names']}")
        print(f"  Locations: {row['loc_count']}, Types: {row['types']}")
        print(f"  Hierarchy: {row['hierarchy']}")

    # 6. Orphans
    r = run(s, "MATCH (n:PlaceName) WHERE NOT (n)<-[:HAS_NAME]-(:Place) RETURN count(n) AS c")
    orphan_n = r[0]["c"] if r else 0
    r = run(s, "MATCH (l:Location) WHERE NOT (l)<-[:HAS_LOCATION]-(:Place) RETURN count(l) AS c")
    orphan_l = r[0]["c"] if r else 0
    print("\n6. ORPHANS")
    print("-" * 40)
    print(f"  PlaceName without Place: {orphan_n}")
    print(f"  Location without Place: {orphan_l}")

driver.close()
print("\n" + "=" * 60)
