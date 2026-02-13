#!/usr/bin/env python3
"""Execute period classification: convert, keep, or delete periods"""

import csv
from neo4j import GraphDatabase

uri = 'bolt://127.0.0.1:7687'
username = 'neo4j'
password = 'Chrystallum'

driver = GraphDatabase.driver(uri, auth=(username, password))

print("=" * 70)
print("EXECUTING PERIOD CLASSIFICATION")
print("=" * 70)

# Read classification decisions
classifications = []
with open('Temporal/period_classification_decisions.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    classifications = list(reader)

print(f"\nLoaded {len(classifications)} classification decisions")

# Group by action
tier2_convert = [c for c in classifications if c['action'] == 'convert_to_event']
tier3_delete = [c for c in classifications if c['tier'] == '3' and c['action'] == 'delete']
tier4_delete = [c for c in classifications if c['tier'] == '4' and c['action'] == 'delete']

print(f"  Tier 2 (Convert to Event): {len(tier2_convert)}")
print(f"  Tier 3 (Delete institutional): {len(tier3_delete)}")
print(f"  Tier 4 (Delete problematic): {len(tier4_delete)}")

try:
    with driver.session() as session:
        # Tier 2: Convert to Event
        print("\n[TIER 2] Converting periods to events...")
        converted = 0
        errors = 0
        
        for entry in tier2_convert:
            qid = entry['qid']
            label = entry['current_label']
            
            try:
                # Get period properties
                result = session.run("""
                    MATCH (p:Period {qid: $qid})
                    RETURN p.label as label, p.start_year as start, p.end_year as end,
                           p.start_date_iso as start_iso, p.end_date_iso as end_iso,
                           p.description as description
                """, qid=qid)
                
                period = result.single()
                if not period:
                    print(f"  Not found: {qid} - {label}")
                    continue
                
                # Convert to Event
                session.run("""
                    MATCH (p:Period {qid: $qid})
                    SET p:Event
                    REMOVE p:Period
                    SET p.event_type = 'historical_episode',
                        p.granularity = 'composite',
                        p.cidoc_crm_class = 'E5_Event',
                        p.unique_id = 'EVENT_' + $qid,
                        p.converted_from = 'Period',
                        p.converted_date = datetime()
                """, qid=qid)
                
                converted += 1
                print(f"  ✓ Converted: {qid} - {label}")
                
            except Exception as e:
                errors += 1
                print(f"  ✗ Error: {qid} - {e}")
        
        print(f"\n  Converted: {converted}, Errors: {errors}")
        
        # Tier 3: Delete institutional
        print("\n[TIER 3] Deleting institutional periods...")
        deleted_tier3 = 0
        
        for entry in tier3_delete:
            qid = entry['qid']
            label = entry['current_label']
            
            try:
                result = session.run("""
                    MATCH (p:Period {qid: $qid})
                    DETACH DELETE p
                    RETURN count(p) as deleted
                """, qid=qid)
                
                if result.single()['deleted'] > 0:
                    deleted_tier3 += 1
                    print(f"  ✓ Deleted: {qid} - {label}")
                else:
                    print(f"  Not found: {qid} - {label}")
            except Exception as e:
                print(f"  ✗ Error: {qid} - {e}")
        
        print(f"\n  Deleted: {deleted_tier3}")
        
        # Tier 4: Delete problematic
        print("\n[TIER 4] Deleting problematic periods...")
        deleted_tier4 = 0
        
        for entry in tier4_delete:
            qid = entry['qid']
            label = entry['current_label']
            
            try:
                result = session.run("""
                    MATCH (p:Period {qid: $qid})
                    DETACH DELETE p
                    RETURN count(p) as deleted
                """, qid=qid)
                
                if result.single()['deleted'] > 0:
                    deleted_tier4 += 1
                    print(f"  ✓ Deleted: {qid} - {label}")
                else:
                    print(f"  Not found: {qid} - {label}")
            except Exception as e:
                print(f"  ✗ Error: {qid} - {e}")
        
        print(f"\n  Deleted: {deleted_tier4}")
        
        # Final counts
        print("\n[VERIFICATION] Final node counts...")
        result = session.run("MATCH (p:Period) RETURN count(p) as periods")
        periods = result.single()['periods']
        
        result = session.run("MATCH (e:Event) RETURN count(e) as events")
        events = result.single()['events']
        
        print(f"  Period nodes: {periods}")
        print(f"  Event nodes: {events}")
        
        print("\n" + "=" * 70)
        print("CLASSIFICATION COMPLETE")
        print("=" * 70)
        print(f"Summary:")
        print(f"  Converted to Events: {converted}")
        print(f"  Deleted (Tier 3): {deleted_tier3}")
        print(f"  Deleted (Tier 4): {deleted_tier4}")
        print(f"  Remaining Periods: {periods}")
        print(f"  Total Events: {events}")

finally:
    driver.close()

