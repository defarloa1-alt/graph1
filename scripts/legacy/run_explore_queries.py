#!/usr/bin/env python3
"""
Execute Exploration Queries from explore_imported_entities.cypher

This script connects to Neo4j and runs the queries interactively,
displaying results in the terminal.
"""

from neo4j import GraphDatabase
import sys
from pathlib import Path

# Neo4j connection (from your successful import)
NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"


def parse_cypher_file(filepath):
    """Parse Cypher file into individual queries"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by queries (each ends with semicolon)
    queries = []
    current_query = []
    current_comment = []
    
    for line in content.split('\n'):
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
        
        # Collect comments
        if stripped.startswith('//'):
            current_comment.append(stripped)
            continue
        
        # Add line to current query
        current_query.append(line)
        
        # If line ends with semicolon, query is complete
        if stripped.endswith(';'):
            query_text = '\n'.join(current_query)
            comment_text = '\n'.join(current_comment) if current_comment else None
            
            # Only add non-empty queries
            if query_text.strip() not in [';', '']:
                queries.append({
                    'comment': comment_text,
                    'query': query_text
                })
            
            current_query = []
            current_comment = []
    
    return queries


def execute_query(driver, query_text, description=None):
    """Execute a single Cypher query and display results"""
    try:
        with driver.session() as session:
            result = session.run(query_text)
            
            # Get records
            records = list(result)
            
            if description:
                print(f"\n{'='*80}")
                print(description)
                print('='*80)
            
            if not records:
                print("  No results returned")
                return
            
            # Display results
            print(f"  Rows: {len(records)}\n")
            
            # Get column names
            if records:
                keys = records[0].keys()
                
                # Display as table
                for i, record in enumerate(records[:20], 1):  # Limit to first 20
                    print(f"  Row {i}:")
                    for key in keys:
                        value = record[key]
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        print(f"    {key}: {value}")
                    print()
                
                if len(records) > 20:
                    print(f"  ... and {len(records) - 20} more rows")
            
    except Exception as e:
        print(f"\n  ❌ ERROR: {e}")


def main():
    print("\n" + "="*80)
    print("NEO4J EXPLORATION QUERIES")
    print("="*80)
    print(f"\nConnecting to: {NEO4J_URI}")
    
    # Parse queries
    cypher_file = Path("explore_imported_entities.cypher")
    if not cypher_file.exists():
        print(f"ERROR: File not found: {cypher_file}")
        sys.exit(1)
    
    queries = parse_cypher_file(cypher_file)
    print(f"Found {len(queries)} queries\n")
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        # Test connection
        driver.verify_connectivity()
        print("✅ Connected successfully!\n")
        
        # Ask which queries to run
        print("Options:")
        print("  1. Run all queries sequentially")
        print("  2. Run specific query by number")
        print("  3. Interactive mode (y/n for each query)")
        print()
        
        choice = input("Select option (1/2/3): ").strip()
        
        if choice == '1':
            # Run all
            for i, q in enumerate(queries, 1):
                print(f"\n[Query {i}/{len(queries)}]")
                execute_query(driver, q['query'], q['comment'])
                input("\nPress Enter to continue...")
        
        elif choice == '2':
            # Run specific
            # Show query list
            print("\nAvailable queries:")
            for i, q in enumerate(queries, 1):
                comment = q['comment'] or "No description"
                # Get first line of comment
                first_line = comment.split('\n')[0].replace('//', '').strip()
                print(f"  {i}. {first_line}")
            
            query_num = int(input("\nEnter query number: "))
            if 1 <= query_num <= len(queries):
                q = queries[query_num - 1]
                execute_query(driver, q['query'], q['comment'])
            else:
                print("Invalid query number")
        
        elif choice == '3':
            # Interactive
            for i, q in enumerate(queries, 1):
                print(f"\n[Query {i}/{len(queries)}]")
                if q['comment']:
                    print(q['comment'])
                print("\nQuery:")
                print(q['query'][:200] + ("..." if len(q['query']) > 200 else ""))
                
                run = input("\nRun this query? (y/n/q to quit): ").strip().lower()
                if run == 'q':
                    break
                elif run == 'y':
                    execute_query(driver, q['query'], q['comment'])
                    input("\nPress Enter to continue...")
        
        else:
            print("Invalid option")
    
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
    
    finally:
        driver.close()
        print("\n✅ Disconnected")


if __name__ == "__main__":
    main()
