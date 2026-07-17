"""
Node Type Cleanup Investigation Script
Date: July 16, 2026
Purpose: Investigate and clean up Neo4j node types based on audit findings

Tasks:
1. Verify empty node types (exclude Material and Object)
2. Investigate ProposedEdge nodes
3. Consolidate duplicate node types (PERSON→Person, EVENT→Event)
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from typing import List, Dict, Any
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Neo4j connection
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USERNAME', os.getenv('NEO4J_USER'))  # Support both names
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

class NodeTypeCleanup:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_empty_node_types(self, exclude: List[str] = None) -> List[str]:
        """Get all node types with 0 nodes, excluding specified types."""
        if exclude is None:
            exclude = ['Material', 'Object']
        
        query = """
        CALL db.labels() YIELD label
        CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) as cnt', {})
        YIELD value
        WITH label, value.cnt as nodeCount
        WHERE nodeCount = 0 AND NOT label IN $exclude
        RETURN label as emptyType
        ORDER BY label
        """
        
        with self.driver.session() as session:
            result = session.run(query, exclude=exclude)
            return [record['emptyType'] for record in result]
    
    def investigate_proposed_edge(self) -> Dict[str, Any]:
        """Deep investigation of ProposedEdge nodes."""
        investigations = {}
        
        with self.driver.session() as session:
            # Basic count
            result = session.run("MATCH (pe:ProposedEdge) RETURN count(pe) as count")
            investigations['total_count'] = result.single()['count']
            
            # Compare to Claim count
            result = session.run("MATCH (c:Claim) RETURN count(c) as count")
            investigations['claim_count'] = result.single()['count']
            investigations['counts_match'] = (
                investigations['total_count'] == investigations['claim_count']
            )
            
            # Check for orphaned nodes
            result = session.run("""
                MATCH (pe:ProposedEdge)
                WHERE NOT (pe)-[]-()
                RETURN count(pe) as orphaned
            """)
            investigations['orphaned_count'] = result.single()['orphaned']
            
            # Sample properties
            result = session.run("""
                MATCH (pe:ProposedEdge)
                WITH pe LIMIT 5
                RETURN collect({
                    id: pe.id,
                    labels: labels(pe),
                    properties: keys(pe)
                }) as samples
            """)
            investigations['samples'] = result.single()['samples']
            
            # Relationship patterns
            result = session.run("""
                MATCH (pe:ProposedEdge)
                OPTIONAL MATCH (pe)-[r_out]->()
                OPTIONAL MATCH (pe)<-[r_in]-()
                WITH pe, 
                     collect(DISTINCT type(r_out)) as outTypes,
                     collect(DISTINCT type(r_in)) as inTypes
                RETURN 
                    count(pe) as total,
                    collect(DISTINCT outTypes)[0..5] as sampleOutgoing,
                    collect(DISTINCT inTypes)[0..5] as sampleIncoming
            """)
            record = result.single()
            investigations['relationship_patterns'] = {
                'sample_outgoing': record['sampleOutgoing'],
                'sample_incoming': record['sampleIncoming']
            }
            
            # Check for overlapping IDs with Claims
            result = session.run("""
                MATCH (c:Claim)
                WITH collect(c.id) as claimIds
                MATCH (pe:ProposedEdge)
                WHERE pe.id IN claimIds
                RETURN count(pe) as overlapping
            """)
            investigations['overlapping_claim_ids'] = result.single()['overlapping']
            
            # Check timestamps
            result = session.run("""
                MATCH (pe:ProposedEdge)
                WHERE pe.created_at IS NOT NULL
                RETURN 
                    min(pe.created_at) as earliest,
                    max(pe.created_at) as latest,
                    count(DISTINCT pe.created_at) as unique_timestamps
            """)
            timestamp_record = result.single()
            if timestamp_record and timestamp_record['earliest']:
                investigations['timestamps'] = {
                    'earliest': timestamp_record['earliest'],
                    'latest': timestamp_record['latest'],
                    'unique_count': timestamp_record['unique_timestamps']
                }
            else:
                investigations['timestamps'] = None
        
        return investigations
    
    def investigate_duplicates(self) -> Dict[str, Any]:
        """Investigate PERSON/Person and EVENT/Event duplicates."""
        duplicates = {}
        
        with self.driver.session() as session:
            # PERSON investigation - get basic info
            result = session.run("""
                MATCH (p:PERSON)
                RETURN count(p) as count
            """)
            person_count = result.single()['count']
            
            # Get detailed info for each PERSON node
            result = session.run("""
                MATCH (p:PERSON)
                OPTIONAL MATCH (p)-[r_out]->()
                OPTIONAL MATCH (p)<-[r_in]-()
                WITH p, count(DISTINCT r_out) as out_rels, count(DISTINCT r_in) as in_rels
                RETURN collect({
                    id: p.id,
                    labels: labels(p),
                    properties: keys(p),
                    out_rels: out_rels,
                    in_rels: in_rels
                }) as nodes
            """)
            record = result.single()
            duplicates['PERSON'] = {
                'count': person_count,
                'nodes': record['nodes'] if record else []
            }
            
            # Person count
            result = session.run("MATCH (p:Person) RETURN count(p) as count")
            duplicates['Person'] = {'count': result.single()['count']}
            
            # Check for nodes with both labels
            result = session.run("""
                MATCH (p:PERSON)
                WHERE p:Person
                RETURN count(p) as both_labels
            """)
            duplicates['PERSON_with_both_labels'] = result.single()['both_labels']
            
            # EVENT investigation - get basic info
            result = session.run("""
                MATCH (e:EVENT)
                RETURN count(e) as count
            """)
            event_count = result.single()['count']
            
            # Get detailed info for each EVENT node
            result = session.run("""
                MATCH (e:EVENT)
                OPTIONAL MATCH (e)-[r_out]->()
                OPTIONAL MATCH (e)<-[r_in]-()
                WITH e, count(DISTINCT r_out) as out_rels, count(DISTINCT r_in) as in_rels
                RETURN collect({
                    id: e.id,
                    labels: labels(e),
                    properties: keys(e),
                    out_rels: out_rels,
                    in_rels: in_rels
                }) as nodes
            """)
            record = result.single()
            duplicates['EVENT'] = {
                'count': event_count,
                'nodes': record['nodes'] if record else []
            }
            
            # Event count
            result = session.run("MATCH (e:Event) RETURN count(e) as count")
            duplicates['Event'] = {'count': result.single()['count']}
            
            # Check for nodes with both labels
            result = session.run("""
                MATCH (e:EVENT)
                WHERE e:Event
                RETURN count(e) as both_labels
            """)
            duplicates['EVENT_with_both_labels'] = result.single()['both_labels']
        
        return duplicates
    
    def consolidate_person_dry_run(self) -> List[Dict[str, Any]]:
        """Dry run for PERSON → Person consolidation."""
        query = """
        MATCH (p:PERSON)
        OPTIONAL MATCH (p)-[r_out]->()
        OPTIONAL MATCH (p)<-[r_in]-()
        RETURN 
            p.id as node_id,
            labels(p) as current_labels,
            keys(p) as properties,
            count(DISTINCT r_out) as outgoing_rels,
            count(DISTINCT r_in) as incoming_rels
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]
    
    def consolidate_person_execute(self) -> int:
        """Execute PERSON → Person consolidation."""
        query = """
        MATCH (p:PERSON)
        SET p:Person
        REMOVE p:PERSON
        RETURN count(p) as consolidated
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return result.single()['consolidated']
    
    def consolidate_event_dry_run(self) -> List[Dict[str, Any]]:
        """Dry run for EVENT → Event consolidation."""
        query = """
        MATCH (e:EVENT)
        OPTIONAL MATCH (e)-[r_out]->()
        OPTIONAL MATCH (e)<-[r_in]-()
        RETURN 
            e.id as node_id,
            labels(e) as current_labels,
            keys(e) as properties,
            count(DISTINCT r_out) as outgoing_rels,
            count(DISTINCT r_in) as incoming_rels
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]
    
    def consolidate_event_execute(self) -> int:
        """Execute EVENT → Event consolidation."""
        query = """
        MATCH (e:EVENT)
        SET e:Event
        REMOVE e:EVENT
        RETURN count(e) as consolidated
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return result.single()['consolidated']
    
    def verify_consolidation(self) -> Dict[str, Any]:
        """Verify consolidation results."""
        verification = {}
        
        with self.driver.session() as session:
            # Check for remaining PERSON nodes
            result = session.run("MATCH (p:PERSON) RETURN count(p) as count")
            verification['remaining_PERSON'] = result.single()['count']
            
            # Check for remaining EVENT nodes
            result = session.run("MATCH (e:EVENT) RETURN count(e) as count")
            verification['remaining_EVENT'] = result.single()['count']
            
            # Total Person count
            result = session.run("MATCH (p:Person) RETURN count(p) as count")
            verification['total_Person'] = result.single()['count']
            
            # Total Event count
            result = session.run("MATCH (e:Event) RETURN count(e) as count")
            verification['total_Event'] = result.single()['count']
        
        return verification


def generate_report(cleanup: NodeTypeCleanup) -> Dict[str, Any]:
    """Generate comprehensive investigation report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'investigations': {}
    }
    
    print("\n" + "="*70)
    print("NODE TYPE CLEANUP INVESTIGATION REPORT")
    print("="*70)
    
    # 1. Empty node types
    print("\n1. EMPTY NODE TYPES (excluding Material and Object)")
    print("-" * 70)
    empty_types = cleanup.get_empty_node_types()
    report['investigations']['empty_types'] = {
        'count': len(empty_types),
        'types': empty_types
    }
    print(f"Found {len(empty_types)} empty node types:")
    for i, node_type in enumerate(empty_types, 1):
        print(f"  {i:2d}. {node_type}")
    
    # 2. ProposedEdge investigation
    print("\n2. PROPOSED EDGE INVESTIGATION")
    print("-" * 70)
    proposed_edge = cleanup.investigate_proposed_edge()
    report['investigations']['proposed_edge'] = proposed_edge
    
    print(f"Total ProposedEdge nodes: {proposed_edge['total_count']}")
    print(f"Total Claim nodes: {proposed_edge['claim_count']}")
    print(f"Counts match: {proposed_edge['counts_match']}")
    print(f"Orphaned ProposedEdge nodes: {proposed_edge['orphaned_count']}")
    print(f"Overlapping IDs with Claims: {proposed_edge['overlapping_claim_ids']}")
    
    if proposed_edge.get('timestamps'):
        print(f"\nTimestamp range:")
        print(f"  Earliest: {proposed_edge['timestamps']['earliest']}")
        print(f"  Latest: {proposed_edge['timestamps']['latest']}")
    
    print(f"\nSample ProposedEdge nodes:")
    for i, sample in enumerate(proposed_edge['samples'][:3], 1):
        print(f"  {i}. ID: {sample.get('id', 'N/A')}")
        print(f"     Labels: {sample.get('labels', [])}")
        print(f"     Properties: {sample.get('properties', [])}")
    
    # 3. Duplicates investigation
    print("\n3. DUPLICATE NODE TYPE INVESTIGATION")
    print("-" * 70)
    duplicates = cleanup.investigate_duplicates()
    report['investigations']['duplicates'] = duplicates
    
    print(f"PERSON (uppercase): {duplicates['PERSON']['count']} nodes")
    print(f"Person (propercase): {duplicates['Person']['count']} nodes")
    print(f"Nodes with both labels: {duplicates['PERSON_with_both_labels']}")
    
    if duplicates['PERSON']['count'] > 0:
        print("\nPERSON nodes details:")
        for node in duplicates['PERSON']['nodes']:
            print(f"  - ID: {node.get('id', 'N/A')}")
            print(f"    Labels: {node.get('labels', [])}")
            print(f"    Properties: {node.get('properties', [])}")
            print(f"    Relationships: {node.get('out_rels', 0)} out, {node.get('in_rels', 0)} in")
    
    print(f"\nEVENT (uppercase): {duplicates['EVENT']['count']} nodes")
    print(f"Event (propercase): {duplicates['Event']['count']} nodes")
    print(f"Nodes with both labels: {duplicates['EVENT_with_both_labels']}")
    
    if duplicates['EVENT']['count'] > 0:
        print("\nEVENT nodes details:")
        for node in duplicates['EVENT']['nodes']:
            print(f"  - ID: {node.get('id', 'N/A')}")
            print(f"    Labels: {node.get('labels', [])}")
            print(f"    Properties: {node.get('properties', [])}")
            print(f"    Relationships: {node.get('out_rels', 0)} out, {node.get('in_rels', 0)} in")
    
    print("\n" + "="*70)
    print("END OF INVESTIGATION REPORT")
    print("="*70 + "\n")
    
    return report


def main():
    """Main execution function."""
    print("Connecting to Neo4j...")
    cleanup = NodeTypeCleanup(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Generate investigation report
        report = generate_report(cleanup)
        
        # Save report to file
        report_file = 'node_cleanup_investigation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nFull report saved to: {report_file}")
        
        # Generate recommendations
        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70)
        
        # ProposedEdge recommendation
        pe_count = report['investigations']['proposed_edge']['total_count']
        pe_orphaned = report['investigations']['proposed_edge']['orphaned_count']
        pe_overlap = report['investigations']['proposed_edge']['overlapping_claim_ids']
        
        print("\n1. ProposedEdge Status:")
        if pe_count == report['investigations']['proposed_edge']['claim_count']:
            print("   WARNING: ProposedEdge count matches Claim count exactly")
            print("   -> Likely legacy claim architecture")
            if pe_orphaned == pe_count:
                print("   -> All ProposedEdge nodes are orphaned")
                print("   RECOMMENDATION: Safe to delete if confirmed obsolete")
            else:
                print(f"   -> {pe_count - pe_orphaned} ProposedEdge nodes have relationships")
                print("   WARNING: RECOMMENDATION: Investigate relationships before deletion")
        
        if pe_overlap > 0:
            print(f"   WARNING: {pe_overlap} ProposedEdge nodes share IDs with Claims")
            print("   -> May indicate duplicate data")
        
        # Consolidation recommendations
        person_count = report['investigations']['duplicates']['PERSON']['count']
        event_count = report['investigations']['duplicates']['EVENT']['count']
        
        print(f"\n2. PERSON Consolidation:")
        if person_count > 0:
            print(f"   READY: Consolidate {person_count} PERSON nodes -> Person")
            print("   -> Run: python node_cleanup.py --consolidate-person")
        else:
            print("   COMPLETE: No PERSON nodes to consolidate")
        
        print(f"\n3. EVENT Consolidation:")
        if event_count > 0:
            print(f"   READY: Consolidate {event_count} EVENT nodes -> Event")
            print("   -> Run: python node_cleanup.py --consolidate-event")
        else:
            print("   COMPLETE: No EVENT nodes to consolidate")
        
        # Empty types recommendation
        empty_count = report['investigations']['empty_types']['count']
        print(f"\n4. Empty Node Types:")
        print(f"   Found {empty_count} empty node types (excluding Material, Object)")
        print("   SAFE: Safe to remove from schema")
        print("   -> Note: Neo4j doesn't support programmatic label deletion")
        print("   -> Labels will automatically disappear when no nodes use them")
        
    finally:
        cleanup.close()
        print("\nConnection closed.")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        cleanup = NodeTypeCleanup(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        try:
            if sys.argv[1] == '--consolidate-person':
                print("PERSON -> Person Consolidation")
                print("="*70)
                print("\nDry run results:")
                dry_run = cleanup.consolidate_person_dry_run()
                for node in dry_run:
                    print(f"  Node: {node['node_id']}")
                    print(f"    Current labels: {node['current_labels']}")
                    print(f"    Relationships: {node['outgoing_rels']} out, {node['incoming_rels']} in")
                
                confirm = input("\nProceed with consolidation? (yes/no): ")
                if confirm.lower() == 'yes':
                    count = cleanup.consolidate_person_execute()
                    print(f"\nSUCCESS: Consolidated {count} nodes")
                    
                    # Verify
                    verification = cleanup.verify_consolidation()
                    print(f"\nVerification:")
                    print(f"  Remaining PERSON: {verification['remaining_PERSON']}")
                    print(f"  Total Person: {verification['total_Person']}")
                else:
                    print("Consolidation cancelled")
            
            elif sys.argv[1] == '--consolidate-event':
                print("EVENT -> Event Consolidation")
                print("="*70)
                print("\nDry run results:")
                dry_run = cleanup.consolidate_event_dry_run()
                for node in dry_run:
                    print(f"  Node: {node['node_id']}")
                    print(f"    Current labels: {node['current_labels']}")
                    print(f"    Relationships: {node['outgoing_rels']} out, {node['incoming_rels']} in")
                
                confirm = input("\nProceed with consolidation? (yes/no): ")
                if confirm.lower() == 'yes':
                    count = cleanup.consolidate_event_execute()
                    print(f"\nSUCCESS: Consolidated {count} nodes")
                    
                    # Verify
                    verification = cleanup.verify_consolidation()
                    print(f"\nVerification:")
                    print(f"  Remaining EVENT: {verification['remaining_EVENT']}")
                    print(f"  Total Event: {verification['total_Event']}")
                else:
                    print("Consolidation cancelled")
            
            else:
                print(f"Unknown command: {sys.argv[1]}")
                print("\nUsage:")
                print("  python node_cleanup.py                    # Run investigation")
                print("  python node_cleanup.py --consolidate-person  # Consolidate PERSON")
                print("  python node_cleanup.py --consolidate-event   # Consolidate EVENT")
        
        finally:
            cleanup.close()
    else:
        main()
