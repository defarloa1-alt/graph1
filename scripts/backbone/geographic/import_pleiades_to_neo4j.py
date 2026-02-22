"""
Import Pleiades Data to Neo4j
==============================

Imports processed Pleiades CSV data into Neo4j as :Place nodes with relationships.

Schema Created:
- (:Place {pleiades_id, label, description, ...})
- (:PlaceName {name_id, name_attested, language, ...})
- (:Location {location_id, lat, long, precision, ...})
- (Place)-[:HAS_NAME]->(PlaceName)
- (Place)-[:HAS_LOCATION]->(Location)

Prerequisites:
    python scripts/backbone/geographic/download_pleiades_bulk.py

Usage:
    python scripts/backbone/geographic/import_pleiades_to_neo4j.py
    python scripts/backbone/geographic/import_pleiades_to_neo4j.py --limit 1000
"""

import argparse
import sys
from pathlib import Path
import logging
from neo4j import GraphDatabase

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
GEOGRAPHIC_DIR = PROJECT_ROOT / "Geographic"
PLACES_CSV = GEOGRAPHIC_DIR / "pleiades_places.csv"
NAMES_CSV = GEOGRAPHIC_DIR / "pleiades_names.csv"
LOCATIONS_CSV = GEOGRAPHIC_DIR / "pleiades_coordinates.csv"

class PleiadesImporter:
    """Import Pleiades data to Neo4j."""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
    
    def close(self):
        self.driver.close()
    
    def create_constraints(self):
        """Create uniqueness constraints and indexes."""
        logger.info("Creating constraints and indexes...")
        
        queries = [
            # Uniqueness constraints
            "CREATE CONSTRAINT place_pleiades_id IF NOT EXISTS FOR (p:Place) REQUIRE p.pleiades_id IS UNIQUE",
            "CREATE CONSTRAINT placename_name_id IF NOT EXISTS FOR (n:PlaceName) REQUIRE n.name_id IS UNIQUE",
            "CREATE CONSTRAINT location_location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",
            
            # Performance indexes
            "CREATE INDEX place_label IF NOT EXISTS FOR (p:Place) ON (p.label)",
            "CREATE INDEX place_type IF NOT EXISTS FOR (p:Place) ON (p.place_type)",
            "CREATE INDEX placename_attested IF NOT EXISTS FOR (n:PlaceName) ON (n.name_attested)",
            "CREATE INDEX placename_language IF NOT EXISTS FOR (n:PlaceName) ON (n.language)",
            "CREATE INDEX location_coords IF NOT EXISTS FOR (l:Location) ON (l.lat, l.long)",
        ]
        
        with self.driver.session(database=self.database) as session:
            for query in queries:
                try:
                    session.run(query)
                    logger.info(f"  ✓ {query[:50]}...")
                except Exception as e:
                    logger.warning(f"  ⚠ {query[:50]}... already exists or failed: {e}")
    
    def import_places(self, limit: int = None):
        """Import Place nodes from CSV."""
        logger.info(f"Importing places from {PLACES_CSV}...")
        
        if not PLACES_CSV.exists():
            logger.error(f"File not found: {PLACES_CSV}")
            return 0
        
        import csv
        count = 0
        batch_size = 1000
        batch = []
        
        query = """
        UNWIND $batch AS row
        MERGE (p:Place {pleiades_id: row.pleiades_id})
        SET p.label = row.label,
            p.label_clean = row.label_clean,
            p.description = row.description,
            p.place_type = row.place_type,
            p.bbox = row.bbox,
            p.lat = row.lat,
            p.long = row.long,
            p.min_date = row.min_date,
            p.max_date = row.max_date,
            p.uri = row.uri,
            p.authority = 'Pleiades',
            p.confidence = 0.90,
            p.entity_type = 'place',
            p.wikidata_qid = coalesce(row.wikidata_qid, p.wikidata_qid)
        """
        
        with open(PLACES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with self.driver.session(database=self.database) as session:
                for row in reader:
                    if not row.get('pleiades_id'):
                        continue
                    # Convert numeric fields
                    import re
                    qid_candidate = row.get('wikidata_qid') or row.get('qid')
                    if qid_candidate and re.match(r'^Q\\d+$', qid_candidate):
                        wikidata_qid = qid_candidate
                    else:
                        wikidata_qid = None
                    place_data = {
                        'pleiades_id': row['pleiades_id'],
                        'label': row['label'],
                        'label_clean': row.get('label_clean') or None,
                        'description': row['description'],
                        'place_type': row['place_type'],
                        'bbox': row['bbox'],
                        'lat': float(row['lat']) if row['lat'] else None,
                        'long': float(row['long']) if row['long'] else None,
                        'min_date': int(row['min_date']) if row['min_date'] else None,
                        'max_date': int(row['max_date']) if row['max_date'] else None,
                        'uri': row['uri'],
                        'wikidata_qid': wikidata_qid
                    }
                    
                    batch.append(place_data)
                    count += 1
                    
                    if len(batch) >= batch_size:
                        session.run(query, batch=batch)
                        logger.info(f"  Imported {count} places...")
                        batch = []
                    
                    if limit and count >= limit:
                        break
                
                # Import remaining batch
                if batch:
                    session.run(query, batch=batch)
        
        logger.info(f"  ✓ Imported {count} places")
        return count
    
    def import_names(self, limit: int = None):
        """Import PlaceName nodes and relationships."""
        logger.info(f"Importing names from {NAMES_CSV}...")
        
        if not NAMES_CSV.exists():
            logger.error(f"File not found: {NAMES_CSV}")
            return 0
        
        import csv
        count = 0
        batch_size = 1000
        batch = []
        
        query = """
        UNWIND $batch AS row
        MATCH (p:Place {pleiades_id: row.pleiades_id})
        MERGE (n:PlaceName {name_id: row.name_id})
        SET n.name_attested = row.name_attested,
            n.label = row.name_attested,
            n.language = row.language,
            n.name_type = row.name_type,
            n.romanized = row.romanized
        MERGE (p)-[:HAS_NAME]->(n)
        """
        
        with open(NAMES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with self.driver.session(database=self.database) as session:
                for row in reader:
                    name_data = {
                        'pleiades_id': row['pleiades_id'],
                        'name_id': row['name_id'],
                        'name_attested': row['name_attested'],
                        'language': row['language'],
                        'name_type': row['name_type'],
                        'romanized': row['romanized']
                    }
                    
                    batch.append(name_data)
                    count += 1
                    
                    if len(batch) >= batch_size:
                        session.run(query, batch=batch)
                        logger.info(f"  Imported {count} names...")
                        batch = []
                    
                    if limit and count >= limit:
                        break
                
                # Import remaining batch
                if batch:
                    session.run(query, batch=batch)
        
        logger.info(f"  ✓ Imported {count} names")
        return count
    
    def import_locations(self, limit: int = None):
        """Import Location nodes and relationships."""
        logger.info(f"Importing locations from {LOCATIONS_CSV}...")
        
        if not LOCATIONS_CSV.exists():
            logger.error(f"File not found: {LOCATIONS_CSV}")
            return 0
        
        import csv
        count = 0
        batch_size = 1000
        batch = []
        
        query = """
        UNWIND $batch AS row
        MATCH (p:Place {pleiades_id: row.pleiades_id})
        MERGE (l:Location {location_id: row.location_id})
        SET l.title = row.title,
            l.location_type = row.location_type,
            l.lat = row.lat,
            l.long = row.long,
            l.precision = row.precision
        MERGE (p)-[:HAS_LOCATION]->(l)
        """
        
        with open(LOCATIONS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            with self.driver.session(database=self.database) as session:
                for row in reader:
                    # Skip rows without coordinates
                    if not row['lat'] or not row['long']:
                        continue
                        
                    location_data = {
                        'pleiades_id': row['pleiades_id'],
                        'location_id': row['location_id'],
                        'title': row['title'],
                        'location_type': row['location_type'],
                        'lat': float(row['lat']),
                        'long': float(row['long']),
                        'precision': row['precision']
                    }
                    
                    batch.append(location_data)
                    count += 1
                    
                    if len(batch) >= batch_size:
                        session.run(query, batch=batch)
                        logger.info(f"  Imported {count} locations...")
                        batch = []
                    
                    if limit and count >= limit:
                        break
                
                # Import remaining batch
                if batch:
                    session.run(query, batch=batch)
        
        logger.info(f"  ✓ Imported {count} locations")
        return count
    
    def verify_import(self):
        """Verify import statistics."""
        logger.info("\nVerifying import...")
        
        queries = {
            "Places": "MATCH (p:Place) RETURN count(p) as count",
            "Names": "MATCH (n:PlaceName) RETURN count(n) as count",
            "Locations": "MATCH (l:Location) RETURN count(l) as count",
            "HAS_NAME relationships": "MATCH ()-[r:HAS_NAME]->() RETURN count(r) as count",
            "HAS_LOCATION relationships": "MATCH ()-[r:HAS_LOCATION]->() RETURN count(r) as count",
            "Places with coordinates": "MATCH (p:Place) WHERE p.lat IS NOT NULL RETURN count(p) as count",
            "Places with temporal bounds": "MATCH (p:Place) WHERE p.min_date IS NOT NULL RETURN count(p) as count",
        }
        
        with self.driver.session(database=self.database) as session:
            logger.info("\nImport Statistics:")
            logger.info("=" * 60)
            for label, query in queries.items():
                result = session.run(query)
                count = result.single()["count"]
                logger.info(f"  {label}: {count:,}")
            logger.info("=" * 60)
    
    def sample_places(self, limit: int = 5):
        """Display sample places."""
        logger.info(f"\nSample Places (first {limit}):")
        logger.info("=" * 60)
        
        query = f"""
        MATCH (p:Place)
        WHERE p.lat IS NOT NULL
        RETURN p.pleiades_id, p.label, p.place_type, p.lat, p.long, p.min_date, p.max_date
        LIMIT {limit}
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            for record in result:
                logger.info(f"  {record['p.pleiades_id']}: {record['p.label']}")
                logger.info(f"    Type: {record['p.place_type']}")
                logger.info(f"    Coords: ({record['p.lat']}, {record['p.long']})")
                logger.info(f"    Dates: {record['p.min_date']} to {record['p.max_date']}")
                logger.info("")

def main(
    *,
    uri: str = NEO4J_URI,
    user: str = NEO4J_USERNAME,
    password: str = NEO4J_PASSWORD,
    database: str = "neo4j",
    limit: int = None,
):
    """Main execution flow."""
    logger.info("=" * 60)
    logger.info("Pleiades to Neo4j Import")
    logger.info("=" * 60)
    logger.info(f"Target Neo4j: {uri} | database={database}")
    
    # Check CSV files exist
    if not PLACES_CSV.exists():
        logger.error(f"Missing file: {PLACES_CSV}")
        logger.error("Run: python scripts/backbone/geographic/download_pleiades_bulk.py")
        return False
    
    importer = PleiadesImporter(uri, user, password, database)
    
    try:
        # Step 1: Create schema
        logger.info("\n[1/5] Creating schema...")
        importer.create_constraints()
        
        # Step 2: Import places
        logger.info("\n[2/5] Importing places...")
        places_count = importer.import_places(limit=limit)
        
        # Step 3: Import names
        logger.info("\n[3/5] Importing names...")
        names_count = importer.import_names(limit=limit)
        
        # Step 4: Import locations
        logger.info("\n[4/5] Importing locations...")
        locations_count = importer.import_locations(limit=limit)
        
        # Step 5: Verify
        logger.info("\n[5/5] Verification...")
        importer.verify_import()
        importer.sample_places()
        
        logger.info("\n✓ Import complete!")
        logger.info("\nNext steps:")
        logger.info("  1. Query places: MATCH (p:Place) WHERE p.label CONTAINS 'Rome' RETURN p LIMIT 5")
        logger.info("  2. Find names: MATCH (p:Place)-[:HAS_NAME]->(n) WHERE n.language = 'la' RETURN p, n LIMIT 10")
        logger.info("  3. Geographic search: MATCH (p:Place) WHERE p.lat > 40 AND p.lat < 45 RETURN p")
        
        return True
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        importer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Pleiades CSV extracts into Neo4j.")
    parser.add_argument("--uri", default=NEO4J_URI, help="Neo4j URI")
    parser.add_argument("--user", default=NEO4J_USERNAME, help="Neo4j username")
    parser.add_argument("--password", default=NEO4J_PASSWORD, help="Neo4j password")
    parser.add_argument("--database", default="neo4j", help="Neo4j database name")
    parser.add_argument("--limit", type=int, default=None, help="Optional row limit per source CSV")
    args = parser.parse_args()

    if args.limit is not None:
        logger.info(f"Limiting import to {args.limit} records per file")

    success = main(
        uri=args.uri,
        user=args.user,
        password=args.password,
        database=args.database,
        limit=args.limit,
    )
    sys.exit(0 if success else 1)
