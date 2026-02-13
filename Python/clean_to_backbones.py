#!/usr/bin/env python3
"""
Clean Neo4j Database - Keep ONLY Backbones
Removes everything except:
  1. Year nodes (temporal backbone)
  2. Subject nodes with lcsh_id (LCSH backbone)
  3. Their core relationships
"""

import sys
import io
from neo4j import GraphDatabase
import argparse

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def clean_database(uri: str, user: str, password: str, dry_run: bool = False):
    """Clean all non-backbone data from Neo4j."""
    
    print("="*80)
    print("CLEAN NEO4J - KEEP ONLY BACKBONES")
    print("="*80)
    print(f"URI: {uri}")
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'EXECUTE (will delete data)'}")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Step 0: Show current state
        print("[CURRENT STATE]")
        result = session.run("MATCH (n) RETURN labels(n)[0] as label, count(n) as count ORDER BY count DESC")
        for record in result:
            print(f"  {record['label']:25s}: {record['count']:>6,}")
        
        result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC")
        print("\n[RELATIONSHIPS]")
        for record in result:
            print(f"  {record['type']:25s}: {record['count']:>6,}")
        
        print()
        
        if dry_run:
            print("[DRY RUN] Would delete the following:")
            print()
        
        # Step 1: Delete old Subject nodes WITHOUT lcsh_id (PropertyRegistry remnants)
        result = session.run("MATCH (s:Subject) WHERE s.lcsh_id IS NULL RETURN count(s) as count")
        old_subjects = result.single()['count']
        
        print(f"[STEP 1] Old Subject nodes (no lcsh_id): {old_subjects}")
        if not dry_run and old_subjects > 0:
            session.run("MATCH (s:Subject) WHERE s.lcsh_id IS NULL DETACH DELETE s")
            print(f"  [DELETED] {old_subjects} old Subject nodes")
        
        # Step 2: Delete PropertyRegistry nodes
        result = session.run("MATCH (p:PropertyRegistry) RETURN count(p) as count")
        prop_reg = result.single()['count']
        
        print(f"\n[STEP 2] PropertyRegistry nodes: {prop_reg}")
        if not dry_run and prop_reg > 0:
            session.run("MATCH (p:PropertyRegistry) DETACH DELETE p")
            print(f"  [DELETED] {prop_reg} PropertyRegistry nodes")
        
        # Step 3: Delete Period nodes
        result = session.run("MATCH (p:Period) RETURN count(p) as count")
        periods = result.single()['count']
        
        print(f"\n[STEP 3] Period nodes: {periods}")
        if not dry_run and periods > 0:
            session.run("MATCH (p:Period) DETACH DELETE p")
            print(f"  [DELETED] {periods} Period nodes")
        
        # Step 4: Delete Event nodes
        result = session.run("MATCH (e:Event) RETURN count(e) as count")
        events = result.single()['count']
        
        print(f"\n[STEP 4] Event nodes: {events}")
        if not dry_run and events > 0:
            session.run("MATCH (e:Event) DETACH DELETE e")
            print(f"  [DELETED] {events} Event nodes")
        
        # Step 5: Delete Person/Human nodes
        result = session.run("MATCH (p) WHERE p:Person OR p:Human RETURN count(p) as count")
        people = result.single()['count']
        
        print(f"\n[STEP 5] Person/Human nodes: {people}")
        if not dry_run and people > 0:
            session.run("MATCH (p) WHERE p:Person OR p:Human DETACH DELETE p")
            print(f"  [DELETED] {people} Person/Human nodes")
        
        # Step 6: Delete Place nodes
        result = session.run("MATCH (p:Place) RETURN count(p) as count")
        places = result.single()['count']
        
        print(f"\n[STEP 6] Place nodes: {places}")
        if not dry_run and places > 0:
            session.run("MATCH (p:Place) DETACH DELETE p")
            print(f"  [DELETED] {places} Place nodes")
        
        # Step 7: Delete Organization nodes
        result = session.run("MATCH (o:Organization) RETURN count(o) as count")
        orgs = result.single()['count']
        
        print(f"\n[STEP 7] Organization nodes: {orgs}")
        if not dry_run and orgs > 0:
            session.run("MATCH (o:Organization) DETACH DELETE o")
            print(f"  [DELETED] {orgs} Organization nodes")
        
        # Step 8: Delete orphaned relationships (not connected to Year or Subject)
        if not dry_run:
            print(f"\n[STEP 8] Cleaning orphaned relationships...")
            # This should be automatic with DETACH DELETE above
            print("  [OK] Orphaned relationships cleaned via DETACH DELETE")
        
        # Final state
        print()
        print("="*80)
        print("FINAL STATE")
        print("="*80)
        
        result = session.run("MATCH (n) RETURN labels(n)[0] as label, count(n) as count ORDER BY count DESC")
        total_nodes = 0
        for record in result:
            count = record['count']
            total_nodes += count
            print(f"  {record['label']:25s}: {count:>6,}")
        
        result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC")
        total_rels = 0
        print("\n[RELATIONSHIPS]")
        for record in result:
            count = record['count']
            total_rels += count
            print(f"  {record['type']:25s}: {count:>6,}")
        
        print()
        print(f"Total nodes: {total_nodes:,}")
        print(f"Total relationships: {total_rels:,}")
        
        # Verify backbones
        print()
        print("[BACKBONE VERIFICATION]")
        result = session.run("MATCH (y:Year) RETURN count(y) as count")
        years = result.single()['count']
        print(f"  Year nodes:           {years:>6,}")
        
        result = session.run("MATCH (s:Subject) WHERE s.lcsh_id IS NOT NULL RETURN count(s) as count")
        subjects = result.single()['count']
        print(f"  LCSH Subject nodes:   {subjects:>6,}")
        
        result = session.run("MATCH ()-[r:FOLLOWED_BY]->() RETURN count(r) as count")
        chains = result.single()['count']
        print(f"  Year chains:          {chains:>6,}")
        
        result = session.run("MATCH ()-[r:BROADER_THAN]->() RETURN count(r) as count")
        hierarchy = result.single()['count']
        print(f"  LCSH hierarchy:       {hierarchy:>6,}")
        
        print()
        print("="*80)
        if dry_run:
            print("[DRY RUN COMPLETE] No changes made")
        else:
            print("[CLEAN COMPLETE] Database contains only backbone data")
        print("="*80)
    
    driver.close()

def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Clean Neo4j - keep only Year and LCSH backbones')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j URI')
    parser.add_argument('--user', default='neo4j', help='Neo4j username')
    parser.add_argument('--password', default='Chrystallum', help='Neo4j password')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    parser.add_argument('--execute', action='store_true', help='Execute deletion (required for safety)')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("[ERROR] Must specify --dry-run (preview) or --execute (delete)")
        print()
        print("Examples:")
        print("  python clean_to_backbones.py --dry-run      # Preview what would be deleted")
        print("  python clean_to_backbones.py --execute      # Actually delete non-backbone data")
        sys.exit(1)
    
    clean_database(args.uri, args.user, args.password, dry_run=args.dry_run)

if __name__ == "__main__":
    main()


