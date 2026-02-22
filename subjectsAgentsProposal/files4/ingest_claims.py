#!/usr/bin/env python3
"""
Ingest Roman Republic Smoke Test Claims into Neo4j
Creates SubjectConcept, Facet, Claim, and Authority nodes with relationships
"""

import json
import sys
import uuid
from datetime import datetime
from neo4j import GraphDatabase

class ClaimIngester:
    """
    Handles ingestion of claims into Neo4j graph database
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize Neo4j connection
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        """
        Close Neo4j connection
        """
        self.driver.close()
    
    def ingest_claims(self, claims_json: dict):
        """
        Main ingestion workflow
        """
        with self.driver.session() as session:
            # 1. Create/update SubjectConcept
            subject_id = self._ingest_subject(session, claims_json['subject'])
            print(f"✅ Created SubjectConcept: {subject_id}")
            
            # 2. Create Facet nodes
            self._create_facets(session, claims_json['claims'])
            print(f"✅ Created {len(set(c['facet'] for c in claims_json['claims']))} Facet nodes")
            
            # 3. Ingest each claim
            claim_count = 0
            for claim in claims_json['claims']:
                self._ingest_claim(session, subject_id, claim, claims_json['metadata'])
                claim_count += 1
            
            print(f"✅ Ingested {claim_count} claims")
            
            # 4. Create facet relationships
            self._create_facet_relationships(session)
            print(f"✅ Created inter-facet relationships")
    
    def _ingest_subject(self, session, subject: dict) -> str:
        """
        Create or update SubjectConcept node
        """
        session.run("""
            MERGE (s:SubjectConcept {subject_id: $subject_id})
            SET s.label = $label,
                s.start_year = $start_year,
                s.end_year = $end_year,
                s.period_label = $period_label,
                s.last_updated = datetime()
        """, 
            subject_id=subject['subject_id'],
            label=subject['label'],
            start_year=subject['temporal']['start_year'],
            end_year=subject['temporal']['end_year'],
            period_label=subject['temporal']['period_label']
        )
        return subject['subject_id']
    
    def _create_facets(self, session, claims: list):
        """
        Create Facet nodes for all unique facets
        """
        facets = set(c['facet'] for c in claims)
        for facet in facets:
            session.run("""
                MERGE (f:Facet {name: $facet_name})
                SET f.last_updated = datetime()
            """, facet_name=facet)
    
    def _ingest_claim(self, session, subject_id: str, claim: dict, metadata: dict):
        """
        Create Claim node and all relationships
        """
        claim_id = f"claim_{uuid.uuid4().hex[:12]}"
        
        # Get facet (support both old 'facet' and new 'primary_facet')
        primary_facet = claim.get('primary_facet', claim.get('facet'))
        if not primary_facet:
            print(f"⚠️  Skipping claim without facet: {claim.get('claim_text', '')[:50]}...")
            return
        
        # Create Claim node
        session.run("""
            MATCH (s:SubjectConcept {subject_id: $subject_id})
            MATCH (f:Facet {name: $facet_name})
            CREATE (c:Claim {
                claim_id: $claim_id,
                text: $claim_text,
                confidence: $confidence,
                start_year: $start_year,
                end_year: $end_year,
                period: $period,
                source_type: $source_type,
                source_text: $source_text,
                generated_by: $generated_by,
                agent_version: $agent_version,
                timestamp: datetime()
            })
            CREATE (s)-[:HAS_CLAIM]->(c)
            CREATE (c)-[:ABOUT_FACET]->(f)
        """,
            subject_id=subject_id,
            facet_name=primary_facet,
            claim_id=claim_id,
            claim_text=claim['claim_text'],
            confidence=claim['confidence'],
            start_year=claim['temporal']['start_year'],
            end_year=claim['temporal']['end_year'],
            period=claim['temporal'].get('period', ''),
            source_type=claim['evidence']['source_type'],
            source_text=claim['evidence']['source_text'],
            generated_by=metadata['generated_by'],
            agent_version=metadata.get('agent_version', 'unknown')
        )
        
        # Create Authority node (if present)
        if 'authority' in claim['evidence']:
            self._create_authority(session, claim_id, claim['evidence']['authority'])
        
        # Create related facet relationships
        if 'related_facets' in claim:
            self._create_related_facets(session, claim_id, claim['related_facets'])
    
    def _create_authority(self, session, claim_id: str, authority: dict):
        """
        Create Authority node and link to claim
        """
        auth_type = authority['type']
        auth_id = authority.get('id') or authority.get('qid') or authority.get('code', 'unknown')
        
        session.run("""
            MATCH (c:Claim {claim_id: $claim_id})
            MERGE (a:Authority {
                type: $auth_type,
                auth_id: $auth_id
            })
            SET a.label = $auth_label,
                a.last_updated = datetime()
            MERGE (c)-[:CITES_AUTHORITY]->(a)
        """,
            claim_id=claim_id,
            auth_type=auth_type,
            auth_id=auth_id,
            auth_label=authority['label']
        )
    
    def _create_related_facets(self, session, claim_id: str, related_facets: list):
        """
        Create relationships to related facets
        """
        for facet_name in related_facets:
            session.run("""
                MATCH (c:Claim {claim_id: $claim_id})
                MATCH (f:Facet {name: $facet_name})
                MERGE (c)-[:RELATED_TO_FACET]->(f)
            """,
                claim_id=claim_id,
                facet_name=facet_name
            )
    
    def _create_facet_relationships(self, session):
        """
        Create relationships between facets based on co-occurrence
        """
        session.run("""
            MATCH (c:Claim)-[:ABOUT_FACET]->(f1:Facet)
            MATCH (c)-[:RELATED_TO_FACET]->(f2:Facet)
            WHERE f1 <> f2
            MERGE (f1)-[r:RELATED_FACET]-(f2)
            ON CREATE SET r.count = 1
            ON MATCH SET r.count = r.count + 1
        """)
    
    def get_stats(self):
        """
        Get ingestion statistics
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:SubjectConcept)
                OPTIONAL MATCH (s)-[:HAS_CLAIM]->(c:Claim)
                OPTIONAL MATCH (c)-[:ABOUT_FACET]->(f:Facet)
                OPTIONAL MATCH (c)-[:CITES_AUTHORITY]->(a:Authority)
                RETURN 
                    s.label as subject,
                    COUNT(DISTINCT c) as claim_count,
                    COUNT(DISTINCT f) as facet_count,
                    COUNT(DISTINCT a) as authority_count
            """)
            return result.single()


def print_neo4j_stats(stats):
    """
    Print ingestion statistics
    """
    print("\n" + "="*70)
    print("NEO4J INGESTION SUMMARY")
    print("="*70)
    print(f"\n📊 DATABASE STATISTICS:")
    print(f"  Subject: {stats['subject']}")
    print(f"  Claims: {stats['claim_count']}")
    print(f"  Facets: {stats['facet_count']}")
    print(f"  Authorities: {stats['authority_count']}")
    print("\n" + "="*70 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_claims.py <claims_json_file> [neo4j_uri] [username] [password]")
        print("\nDefaults:")
        print("  neo4j_uri: bolt://localhost:7687")
        print("  username: neo4j")
        print("  password: (will prompt)")
        print("\nExample:")
        print("  python ingest_claims.py roman_republic_smoke_test.json")
        sys.exit(1)
    
    filepath = sys.argv[1]
    neo4j_uri = sys.argv[2] if len(sys.argv) > 2 else "bolt://localhost:7687"
    username = sys.argv[3] if len(sys.argv) > 3 else "neo4j"
    password = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Prompt for password if not provided
    if not password:
        import getpass
        password = getpass.getpass("Neo4j password: ")
    
    # Load claims
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            claims_json = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON: {e}")
        sys.exit(1)
    
    # Ingest
    print(f"\n🔄 Connecting to Neo4j at {neo4j_uri}...")
    ingester = ClaimIngester(neo4j_uri, username, password)
    
    try:
        print(f"🔄 Ingesting claims from {filepath}...")
        ingester.ingest_claims(claims_json)
        
        # Get and print stats
        stats = ingester.get_stats()
        print_neo4j_stats(stats)
        
        print("✅ Ingestion complete!\n")
        
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        ingester.close()


if __name__ == "__main__":
    main()
