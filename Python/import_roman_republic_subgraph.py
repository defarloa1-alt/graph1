#!/usr/bin/env python3
"""
Import Roman Republic subgraph to Neo4j
Demonstrates backbone integration with LCC routing
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Chrystallum"

def import_subgraph(driver):
    """Import Roman Republic subgraph"""
    
    with driver.session() as session:
        
        print("\n[STEP 1] Creating Period node...")
        session.run("""
            MERGE (p:Period {qid: "Q17167"})
            SET p.type_qid = "Q186081",
                p.cidoc_class = "E4_Period",
                p.label = "Roman Republic",
                p.start_year = -509,
                p.end_year = -27,
                p.earliest_start = "-0509",
                p.latest_start = "-0509",
                p.earliest_end = "-0027",
                p.latest_end = "-0027",
                p.start_date_min = "-0509",
                p.start_date_max = "-0509",
                p.end_date_min = "-0027",
                p.end_date_max = "-0027",
                p.unique_id = "period:Q17167"
        """)
        print("  ✅ Roman Republic period created")
        
        print("\n[STEP 2] Creating Event nodes...")
        
        # Republic Established
        session.run("""
            MERGE (e:Event {qid: "Q23402"})
            SET e.type_qid = "Q13418847",
                e.cidoc_class = "E5_Event",
                e.label = "Establishment of the Roman Republic",
                e.date_iso8601 = "-0509",
                e.start_date = "-0509",
                e.end_date = "-0509",
                e.start_date_min = "-0509",
                e.start_date_max = "-0509",
                e.end_date_min = "-0509",
                e.end_date_max = "-0509",
                e.granularity = "atomic",
                e.goal_type = "POL",
                e.trigger_type = "REVOLT",
                e.action_type = "POL_ACT",
                e.result_type = "POL_TRANS",
                e.unique_id = "event:Q23402"
        """)
        
        # Punic Wars
        session.run("""
            MERGE (e:Event {qid: "Q47084"})
            SET e.type_qid = "Q198",
                e.cidoc_class = "E5_Event",
                e.label = "Punic Wars",
                e.start_year = -264,
                e.end_year = -146,
                e.start_date = "-0264",
                e.end_date = "-0146",
                e.start_date_min = "-0264",
                e.start_date_max = "-0264",
                e.end_date_min = "-0146",
                e.end_date_max = "-0146",
                e.granularity = "composite",
                e.goal_type = "MIL",
                e.action_type = "MIL_ACT",
                e.result_type = "TERR_EXP",
                e.unique_id = "event:Q47084"
        """)
        
        # Gracchi Reforms
        session.run("""
            MERGE (e:Event {qid: "Q912145"})
            SET e.type_qid = "Q4502166",
                e.cidoc_class = "E7_Activity",
                e.label = "Gracchi Reforms",
                e.start_year = -133,
                e.end_year = -121,
                e.start_date = "-0133",
                e.end_date = "-0121",
                e.start_date_min = "-0133",
                e.start_date_max = "-0133",
                e.end_date_min = "-0121",
                e.end_date_max = "-0121",
                e.granularity = "composite",
                e.goal_type = "POL",
                e.trigger_type = "SOC_STRAIN",
                e.action_type = "POL_ACT",
                e.result_type = "POL_TRANS",
                e.unique_id = "event:Q912145"
        """)
        
        # Crossing of Rubicon
        session.run("""
            MERGE (e:Event {qid: "Q161954"})
            SET e.type_qid = "Q1190554",
                e.cidoc_class = "E5_Event",
                e.label = "Crossing of the Rubicon",
                e.date_iso8601 = "-0049-01-10",
                e.start_date = "-0049-01-10",
                e.end_date = "-0049-01-10",
                e.start_date_min = "-0049-01-10",
                e.start_date_max = "-0049-01-10",
                e.end_date_min = "-0049-01-10",
                e.end_date_max = "-0049-01-10",
                e.granularity = "atomic",
                e.goal_type = "POL",
                e.trigger_type = "OPPORT",
                e.action_type = "MIL_ACT",
                e.result_type = "POL_TRANS",
                e.unique_id = "event:Q161954"
        """)
        
        # Caesar Assassination
        session.run("""
            MERGE (e:Event {qid: "Q106398"})
            SET e.type_qid = "Q132821",
                e.cidoc_class = "E5_Event",
                e.label = "Assassination of Julius Caesar",
                e.date_iso8601 = "-0044-03-15",
                e.start_date = "-0044-03-15",
                e.end_date = "-0044-03-15",
                e.start_date_min = "-0044-03-15",
                e.start_date_max = "-0044-03-15",
                e.end_date_min = "-0044-03-15",
                e.end_date_max = "-0044-03-15",
                e.granularity = "atomic",
                e.goal_type = "POL",
                e.trigger_type = "THREAT",
                e.action_type = "POL_ACT",
                e.result_type = "POL_TRANS",
                e.unique_id = "event:Q106398"
        """)
        
        # Empire Established
        session.run("""
            MERGE (e:Event {qid: "Q23401"})
            SET e.type_qid = "Q13418847",
                e.cidoc_class = "E5_Event",
                e.label = "Establishment of the Roman Empire",
                e.date_iso8601 = "-0027",
                e.start_date = "-0027",
                e.end_date = "-0027",
                e.start_date_min = "-0027",
                e.start_date_max = "-0027",
                e.end_date_min = "-0027",
                e.end_date_max = "-0027",
                e.granularity = "atomic",
                e.goal_type = "POL",
                e.action_type = "POL_ACT",
                e.result_type = "POL_TRANS",
                e.unique_id = "event:Q23401"
        """)
        
        print("  ✅ 6 events created")
        
        print("\n[STEP 3] Creating Person nodes...")
        
        persons = [
            ("Q188117", "Q5", "E21_Person", "Lucius Tarquinius Superbus", "-0542", "-0495"),
            ("Q189411", "Q5", "E21_Person", "Tiberius Gracchus", "-0163", "-0133-06-10"),
            ("Q296646", "Q5", "E21_Person", "Gaius Gracchus", "-0154", "-0121"),
            ("Q159419", "Q5", "E21_Person", "Gaius Marius", "-0157", "-0086-01-13"),
            ("Q46654", "Q5", "E21_Person", "Lucius Cornelius Sulla", "-0138", "-0078"),
            ("Q297162", "Q5", "E21_Person", "Pompey", "-0106-09-29", "-0048-09-28"),
            ("Q1048", "Q5", "E21_Person", "Julius Caesar", "-0100-07-12", "-0044-03-15"),
            ("Q1405", "Q5", "E21_Person", "Augustus", "-0063-09-23", "0014-08-19"),
            ("Q193616", "Q5", "E21_Person", "Marcus Junius Brutus", "-0085", "-0042-10-23"),
        ]
        
        for qid, type_qid, cidoc, label, birth, death in persons:
            session.run("""
                MERGE (p:Person {qid: $qid})
                SET p.type_qid = $type_qid,
                    p.cidoc_class = $cidoc,
                    p.label = $label,
                    p.birth_date = $birth,
                    p.death_date = $death,
                    p.birth_date_min = $birth,
                    p.birth_date_max = $birth,
                    p.death_date_min = $death,
                    p.death_date_max = $death,
                    p.unique_id = 'person:' + $qid
            """, qid=qid, type_qid=type_qid, cidoc=cidoc, label=label, birth=birth, death=death)
        
        print(f"  ✅ {len(persons)} persons created")
        
        print("\n[STEP 4] Creating Place nodes...")
        
        places = [
            ("Q220", "Q515", "Rome", 41.9028, 12.4964, "very_high", "city"),
            ("Q6343", "Q515", "Carthage", 36.8531, 10.3231, "very_high", "ancient_city"),
            ("Q14378", "Q4022", "Rubicon River", 44.0667, 12.25, "very_high", "river"),
            ("Q4918", "Q165", "Mediterranean Sea", None, None, "very_high", "sea"),
        ]
        
        for qid, type_qid, label, lat, lon, stability, feature_type in places:
            if lat and lon:
                session.run("""
                    MERGE (p:Place {qid: $qid})
                    SET p.type_qid = $type_qid,
                        p.cidoc_class = "E53_Place",
                        p.label = $label,
                        p.coordinates = [$lat, $lon],
                        p.stability = $stability,
                        p.feature_type = $feature_type,
                        p.unique_id = 'place:' + $qid
                """, qid=qid, type_qid=type_qid, label=label, lat=lat, lon=lon, stability=stability, feature_type=feature_type)
            else:
                session.run("""
                    MERGE (p:Place {qid: $qid})
                    SET p.type_qid = $type_qid,
                        p.cidoc_class = "E53_Place",
                        p.label = $label,
                        p.stability = $stability,
                        p.feature_type = $feature_type,
                        p.unique_id = 'place:' + $qid
                """, qid=qid, type_qid=type_qid, label=label, stability=stability, feature_type=feature_type)
        
        print(f"  ✅ {len(places)} places created")
        
        print("\n[STEP 5] Creating Organization nodes...")
        
        session.run("""
            MERGE (o:Organization {qid: "Q842606"})
            SET o.type_qid = "Q7210356",
                o.cidoc_class = "E74_Group",
                o.label = "Roman Senate",
                o.inception = "-0509",
                o.unique_id = "org:Q842606"
        """)
        
        session.run("""
            MERGE (o:Organization {qid: "Q193439"})
            SET o.type_qid = "Q294414",
                o.cidoc_class = "E74_Group",
                o.label = "Tribune of the Plebs",
                o.inception = "-0494",
                o.unique_id = "org:Q193439"
        """)
        
        print("  ✅ 2 organizations created")
        
        print("\n[STEP 6] Linking to temporal backbone (Year nodes)...")
        
        # Link events to years
        year_links = [
            ("Q23402", -509),
            ("Q161954", -49),
            ("Q106398", -44),
            ("Q23401", -27),
        ]
        
        for event_qid, year_value in year_links:
            session.run("""
                MATCH (e:Event {qid: $event_qid})
                MATCH (y:Year {year_value: $year_value})
                MERGE (e)-[:POINT_IN_TIME]->(y)
            """, event_qid=event_qid, year_value=year_value)
        
        print(f"  ✅ {len(year_links)} event→year links created")
        
        print("\n[STEP 7] Linking events to period...")
        
        event_qids = ["Q23402", "Q47084", "Q912145", "Q161954", "Q106398"]
        for event_qid in event_qids:
            session.run("""
                MATCH (e:Event {qid: $event_qid})
                MATCH (p:Period {qid: "Q17167"})
                MERGE (e)-[:DURING]->(p)
            """, event_qid=event_qid)
        
        print(f"  ✅ {len(event_qids)} event→period links created")
        
        print("\n[STEP 8] Creating event sequence (FOLLOWED_BY)...")
        
        sequence = [
            ("Q23402", "Q47084"),
            ("Q47084", "Q912145"),
            ("Q912145", "Q161954"),
            ("Q161954", "Q106398"),
            ("Q106398", "Q23401"),
        ]
        
        for from_qid, to_qid in sequence:
            session.run("""
                MATCH (e1:Event {qid: $from_qid})
                MATCH (e2:Event {qid: $to_qid})
                MERGE (e1)-[:FOLLOWED_BY]->(e2)
            """, from_qid=from_qid, to_qid=to_qid)
        
        print(f"  ✅ {len(sequence)} sequential relationships created")
        
        print("\n[STEP 9] Creating political relationships...")
        
        # Tarquinius overthrown
        session.run("""
            MATCH (p:Person {qid: "Q188117"})
            MATCH (e:Event {qid: "Q23402"})
            MERGE (p)-[:OVERTHROWN_BY]->(e)
        """)
        
        # Senate governed Rome
        session.run("""
            MATCH (o:Organization {qid: "Q842606"})
            MATCH (pl:Place {qid: "Q220"})
            MERGE (o)-[:GOVERNED {start: -509, end: -27}]->(pl)
        """)
        
        # Gracchi initiated reforms
        session.run("""
            MATCH (p1:Person {qid: "Q189411"})
            MATCH (p2:Person {qid: "Q296646"})
            MATCH (e:Event {qid: "Q912145"})
            MERGE (p1)-[:INITIATED]->(e)
            MERGE (p2)-[:INITIATED]->(e)
        """)
        
        # Marius opposed Sulla
        session.run("""
            MATCH (p1:Person {qid: "Q159419"})
            MATCH (p2:Person {qid: "Q46654"})
            MERGE (p1)-[:OPPOSED_BY]->(p2)
        """)
        
        # Pompey allied with Caesar (First Triumvirate)
        session.run("""
            MATCH (p1:Person {qid: "Q297162"})
            MATCH (p2:Person {qid: "Q1048"})
            MERGE (p1)-[:ALLIED_WITH {start: -60, end: -53, alliance: "First Triumvirate"}]->(p2)
        """)
        
        # Pompey opposed Caesar (Civil War)
        session.run("""
            MATCH (p1:Person {qid: "Q297162"})
            MATCH (p2:Person {qid: "Q1048"})
            MERGE (p1)-[:OPPOSED_BY {start: -49}]->(p2)
        """)
        
        # Caesar crossed Rubicon
        session.run("""
            MATCH (p:Person {qid: "Q1048"})
            MATCH (pl:Place {qid: "Q14378"})
            MERGE (p)-[:CROSSED {date: "-0049-01-10"}]->(pl)
        """)
        
        # Caesar participated in crossing
        session.run("""
            MATCH (p:Person {qid: "Q1048"})
            MATCH (e:Event {qid: "Q161954"})
            MERGE (p)-[:PARTICIPATED_IN {role: "leader"}]->(e)
        """)
        
        # Brutus assassinated Caesar
        session.run("""
            MATCH (p1:Person {qid: "Q193616"})
            MATCH (p2:Person {qid: "Q1048"})
            MERGE (p1)-[:ASSASSINATED {date: "-0044-03-15"}]->(p2)
        """)
        
        # Caesar victim of assassination
        session.run("""
            MATCH (p:Person {qid: "Q1048"})
            MATCH (e:Event {qid: "Q106398"})
            MERGE (p)-[:PARTICIPATED_IN {role: "victim"}]->(e)
        """)
        
        # Augustus established Empire
        session.run("""
            MATCH (p:Person {qid: "Q1405"})
            MATCH (e:Event {qid: "Q23401"})
            MERGE (p)-[:ESTABLISHED]->(e)
        """)
        
        # Republic ended by Empire
        session.run("""
            MATCH (p:Period {qid: "Q17167"})
            MATCH (e:Event {qid: "Q23401"})
            MERGE (p)-[:ENDED_BY]->(e)
        """)
        
        print("  ✅ 12 political relationships created")
        
        print("\n[STEP 10] Creating geographic relationships...")
        
        # Events in places
        geo_links = [
            ("Q23402", "Q220"),  # Republic established in Rome
            ("Q161954", "Q14378"),  # Crossing at Rubicon
            ("Q106398", "Q220"),  # Assassination in Rome
        ]
        
        for event_qid, place_qid in geo_links:
            session.run("""
                MATCH (e:Event {qid: $event_qid})
                MATCH (p:Place {qid: $place_qid})
                MERGE (e)-[:LOCATED_IN]->(p)
            """, event_qid=event_qid, place_qid=place_qid)
        
        # Rome/Carthage participated in Punic Wars
        session.run("""
            MATCH (pl:Place {qid: "Q220"})
            MATCH (e:Event {qid: "Q47084"})
            MERGE (pl)-[:PARTICIPATED_IN {role: "belligerent"}]->(e)
        """)
        
        session.run("""
            MATCH (pl:Place {qid: "Q6343"})
            MATCH (e:Event {qid: "Q47084"})
            MERGE (pl)-[:PARTICIPATED_IN {role: "belligerent"}]->(e)
        """)
        
        print(f"  ✅ {len(geo_links) + 2} geographic relationships created")
        
        print("\n[STEP 11] ⭐ LINKING TO SUBJECT BACKBONE (LCC ROUTING) ⭐...")
        
        # Link to existing subjects (Caesar and Augustus already in DB)
        session.run("""
            MATCH (p:Person {qid: "Q1048"})
            MATCH (s:Subject {lcsh_id: "n79021400"})
            MERGE (p)-[:SUBJECT_OF]->(s)
        """)
        print("  ✅ Julius Caesar → Subject (n79021400, LCC: DG261-267)")
        
        session.run("""
            MATCH (p:Person {qid: "Q1405"})
            MATCH (s:Subject {lcsh_id: "n79033006"})
            MERGE (p)-[:SUBJECT_OF]->(s)
        """)
        print("  ✅ Augustus → Subject (n79033006, LCC: DG279)")
        
        # Create placeholder subjects for others (would be fetched from Wikidata in production)
        subjects_to_create = [
            ("sh85115114", "Rome--History--Republic, 265-30 B.C.", "DG235-254", None, None),
            ("sh85109110", "Punic Wars", "DG241-249.4", None, None),
            ("sh2003003122", "Rubicon River, Crossing of the, 49 B.C.", "DG260", None, None),
            ("sh85042928", "Assassination of Julius Caesar, 44 B.C.", "DG267", None, None),
        ]
        
        for lcsh_id, label, lcc_code, dewey, fast in subjects_to_create:
            session.run("""
                MERGE (s:Subject {lcsh_id: $lcsh_id})
                SET s.label = $label,
                    s.lcc_code = $lcc_code,
                    s.dewey_decimal = $dewey,
                    s.fast_id = $fast,
                    s.unique_id = 'lcsh:' + $lcsh_id,
                    s.source = 'manual_placeholder'
            """, lcsh_id=lcsh_id, label=label, lcc_code=lcc_code, dewey=dewey, fast=fast)
        
        print(f"  ✅ Created {len(subjects_to_create)} placeholder subjects")
        
        # Link entities to subjects
        session.run("""
            MATCH (p:Period {qid: "Q17167"})
            MATCH (s:Subject {lcsh_id: "sh85115114"})
            MERGE (p)-[:SUBJECT_OF]->(s)
        """)
        print("  ✅ Roman Republic → Subject (sh85115114, LCC: DG235-254)")
        
        session.run("""
            MATCH (e:Event {qid: "Q47084"})
            MATCH (s:Subject {lcsh_id: "sh85109110"})
            MERGE (e)-[:SUBJECT_OF]->(s)
        """)
        print("  ✅ Punic Wars → Subject (sh85109110, LCC: DG241-249.4)")
        
        session.run("""
            MATCH (e:Event {qid: "Q161954"})
            MATCH (s:Subject {lcsh_id: "sh2003003122"})
            MERGE (e)-[:SUBJECT_OF]->(s)
        """)
        print("  ✅ Crossing of Rubicon → Subject (sh2003003122, LCC: DG260)")
        
        session.run("""
            MATCH (e:Event {qid: "Q106398"})
            MATCH (s:Subject {lcsh_id: "sh85042928"})
            MERGE (e)-[:SUBJECT_OF]->(s)
        """)
        print("  ✅ Caesar Assassination → Subject (sh85042928, LCC: DG267)")

def verify_import(driver):
    """Verify the subgraph was imported correctly"""
    
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    with driver.session() as session:
        # Count nodes by type
        result = session.run("""
            MATCH (n)
            WHERE n.qid IS NOT NULL OR n.year_value IS NOT NULL OR n.lcsh_id IS NOT NULL
            RETURN labels(n)[0] as label, count(n) as count
            ORDER BY label
        """)
        
        print("\n[NODE COUNTS]")
        for r in result:
            print(f"  {r['label']}: {r['count']}")
        
        # Count relationships
        result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) as rel_type, count(r) as count
            ORDER BY count DESC
            LIMIT 10
        """)
        
        print("\n[TOP RELATIONSHIP TYPES]")
        for r in result:
            print(f"  {r['rel_type']}: {r['count']}")
        
        # Show LCC routing
        result = session.run("""
            MATCH (s:Subject)
            WHERE s.lcc_code IS NOT NULL AND s.lcc_code STARTS WITH 'DG'
            RETURN s.lcsh_id, s.label, s.lcc_code
            ORDER BY s.lcc_code
        """)
        
        print("\n[LCC ROUTING - Roman History Subjects]")
        for r in result:
            print(f"  {r['s.lcc_code']:<15} {r['s.lcsh_id']:<20} {r['s.label']}")

def main():
    print("="*80)
    print("IMPORT ROMAN REPUBLIC SUBGRAPH")
    print("Demonstrating LCC-based backbone integration")
    print("="*80)
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        import_subgraph(driver)
        verify_import(driver)
        
        print("\n" + "="*80)
        print("✅ IMPORT COMPLETE!")
        print("="*80)
        print("\nRun these Cypher queries to explore:")
        print("1. MATCH (e:Event)-[:SUBJECT_OF]->(s:Subject) RETURN e.label, s.lcc_code")
        print("2. MATCH (p:Person {qid: 'Q1048'})-[r]->() RETURN type(r), r")
        print("3. MATCH path=(e1:Event)-[:FOLLOWED_BY*]->(e2:Event) RETURN path LIMIT 1")
        print()
        
    finally:
        driver.close()

if __name__ == "__main__":
    main()

