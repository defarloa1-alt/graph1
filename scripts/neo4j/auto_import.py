#!/usr/bin/env python3
"""
Auto Import to Neo4j - Handles Large Cypher Files

Automatically executes Cypher in batches:
- Reads large Cypher files
- Splits into batches
- Executes with progress
- Handles millions of records
"""

import sys
from pathlib import Path
from neo4j import GraphDatabase
import time

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    sys.path.insert(0, str(project_root))
    from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
    NEO4J_USERNAME = NEO4J_USER  # Alias
except ImportError as e:
    print(f"Error importing config: {e}")
    print("Make sure config.py exists in the project root")
    sys.exit(1)


class AutoImporter:
    """Automatically import Cypher files to Neo4j"""
    
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def execute_cypher_file(self, filepath: str, batch_size: int = 100):
        """
        Execute a Cypher file in batches
        
        Args:
            filepath: Path to .cypher file
            batch_size: Statements per batch
        """
        
        print(f"\n{'='*80}")
        print(f"AUTO IMPORT TO NEO4J")
        print(f"{'='*80}\n")
        
        # Read file
        print(f"Reading: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into statements
        statements = self._split_cypher(content)
        
        total_statements = len(statements)
        print(f"  Total statements: {total_statements}")
        print(f"  Batch size: {batch_size}\n")
        
        # Execute in batches
        executed = 0
        failed = 0
        
        with self.driver.session() as session:
            for i in range(0, total_statements, batch_size):
                batch = statements[i:i+batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_statements + batch_size - 1) // batch_size
                
                print(f"[Batch {batch_num}/{total_batches}] Executing {len(batch)} statements...", end=" ", flush=True)
                
                try:
                    for stmt in batch:
                        if stmt.strip():
                            session.run(stmt)
                    
                    executed += len(batch)
                    print(f"OK ({executed}/{total_statements})")
                    
                except Exception as e:
                    failed += len(batch)
                    print(f"FAILED: {e}")
                
                # Small delay between batches
                time.sleep(0.1)
        
        print(f"\n{'='*80}")
        print(f"IMPORT COMPLETE")
        print(f"{'='*80}\n")
        print(f"Executed: {executed}")
        print(f"Failed: {failed}")
        print(f"Total: {total_statements}\n")
    
    def _split_cypher(self, content: str) -> list:
        """Split Cypher content into individual statements"""
        
        # Remove comments
        lines = []
        for line in content.split('\n'):
            if not line.strip().startswith('//'):
                lines.append(line)
        
        content_no_comments = '\n'.join(lines)
        
        # Split on semicolons
        statements = content_no_comments.split(';')
        
        # Clean up and filter
        cleaned = []
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and len(stmt) > 5:  # Skip empty or tiny statements
                # Add semicolon back
                cleaned.append(stmt + ';')
        
        return cleaned
    
    def close(self):
        """Close driver"""
        self.driver.close()


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python auto_import.py <cypher_file> [batch_size] [uri] [user] [password]")
        print("Example: python auto_import.py output/neo4j/import.cypher 100")
        print("         python auto_import.py output/neo4j/import.cypher 100 neo4j+s://xxx user pass")
        sys.exit(1)
    
    filepath = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    # Use command-line args or fallback to config
    if len(sys.argv) > 5:
        uri = sys.argv[3]
        username = sys.argv[4]
        password = sys.argv[5]
    else:
        uri = NEO4J_URI
        username = NEO4J_USER
        password = NEO4J_PASSWORD
    
    print(f"Connecting to Neo4j...")
    print(f"  URI: {uri}")
    
    importer = AutoImporter(uri, username, password)
    
    try:
        importer.execute_cypher_file(filepath, batch_size)
    finally:
        importer.close()
    
    print("Done!")


if __name__ == "__main__":
    main()
