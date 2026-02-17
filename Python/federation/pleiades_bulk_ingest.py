#!/usr/bin/env python3
"""
Pleiades Bulk Ingest for Roman Republic Test Case

Downloads and ingests ancient Mediterranean places from Pleiades gazetteer,
filtered to Roman Republic period (-509 to -27 BCE) for map-ready visualization.

Source: https://pleiades.stoa.org/
Bulk Data: https://atlantides.org/downloads/pleiades/dumps/

Author: Chrystallum Project
Date: 2026-02-16
"""

import gzip
import hashlib
import json
import logging
import os
import re
import requests
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import pandas as pd
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
PLEIADES_DUMPS_URL = "https://atlantides.org/downloads/pleiades/dumps/"
PLEIADES_CSV_FILENAME = "pleiades-places-latest.csv.gz"
PLEIADES_JSON_API = "https://pleiades.stoa.org/places/{pleiades_id}/json"

# Roman Republic temporal boundaries
ROMAN_REPUBLIC_START = -509
ROMAN_REPUBLIC_END = -27

# Geographic bounding box (Mediterranean focus)
BBOX_LAT_MIN, BBOX_LAT_MAX = 30.0, 46.0
BBOX_LON_MIN, BBOX_LON_MAX = -12.0, 36.0

# Output paths
OUTPUT_DIR = Path("Geographic")
CACHE_DIR = OUTPUT_DIR / "cache"
OUTPUT_JSON = OUTPUT_DIR / "pleiades_roman_republic_places.json"
OUTPUT_CYPHER = OUTPUT_DIR / "pleiades_roman_republic_import.cypher"


class PleiadesIngester:
    """Bulk ingester for Pleiades ancient places data."""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """Initialize with Neo4j connection details."""
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = None
        
        # Ensure output directories exist
        OUTPUT_DIR.mkdir(exist_ok=True)
        CACHE_DIR.mkdir(exist_ok=True)
    
    def connect_neo4j(self):
        """Connect to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                assert result.single()["test"] == 1
            logger.info(f"Connected to Neo4j at {self.neo4j_uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close_neo4j(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")
    
    def download_pleiades_dump(self, force_download: bool = False) -> Path:
        """Download Pleiades CSV dump if not cached."""
        cache_file = CACHE_DIR / PLEIADES_CSV_FILENAME
        
        if cache_file.exists() and not force_download:
            logger.info(f"Using cached Pleiades dump: {cache_file}")
            return cache_file
        
        url = urljoin(PLEIADES_DUMPS_URL, PLEIADES_CSV_FILENAME)
        logger.info(f"Downloading Pleiades dump from {url}")
        
        try:
            response = requests.get(url, stream=True, timeout=120)
            response.raise_for_status()
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            with open(cache_file, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        progress = (downloaded / total_size) * 100
                        print(f"\rDownload progress: {progress:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            logger.info(f"Downloaded Pleiades dump to {cache_file}")
            return cache_file
            
        except Exception as e:
            logger.error(f"Failed to download Pleiades dump: {e}")
            raise
    
    def parse_pleiades_csv(self, csv_path: Path) -> pd.DataFrame:
        """Parse Pleiades CSV dump into DataFrame."""
        logger.info(f"Parsing Pleiades CSV: {csv_path}")
        
        try:
            # Read gzipped CSV
            with gzip.open(csv_path, 'rt', encoding='utf-8') as f:
                df = pd.read_csv(f)
            
            logger.info(f"Loaded {len(df)} places from Pleiades dump")
            return df
            
        except Exception as e:
            logger.error(f"Failed to parse Pleiades CSV: {e}")
            raise
    
    def filter_roman_republic_places(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter places to Roman Republic period and Mediterranean region."""
        logger.info("Filtering to Roman Republic places...")
        
        original_count = len(df)
        
        # Parse temporal attestations (minDate, maxDate columns)
        df = df[df['minDate'].notna() & df['maxDate'].notna()].copy()
        df['minDate'] = pd.to_numeric(df['minDate'], errors='coerce')
        df['maxDate'] = pd.to_numeric(df['maxDate'], errors='coerce')
        
        # Temporal filter: overlaps with Roman Republic
        df = df[
            (df['minDate'] <= ROMAN_REPUBLIC_END) & 
            (df['maxDate'] >= ROMAN_REPUBLIC_START)
        ].copy()
        
        # Geographic filter: Mediterranean bounding box (if coordinates available)
        if 'reprLat' in df.columns and 'reprLong' in df.columns:
            df = df[df['reprLat'].notna() & df['reprLong'].notna()].copy()
            df = df[
                (df['reprLat'] >= BBOX_LAT_MIN) & (df['reprLat'] <= BBOX_LAT_MAX) &
                (df['reprLong'] >= BBOX_LON_MIN) & (df['reprLong'] <= BBOX_LON_MAX)
            ].copy()
        
        filtered_count = len(df)
        logger.info(f"Filtered {original_count} → {filtered_count} Roman Republic places")
        
        return df
    
    def transform_to_map_ready(self, df: pd.DataFrame) -> List[Dict]:
        """Transform Pleiades data to map-ready JSON format."""
        logger.info("Transforming to map-ready format...")
        
        places = []
        
        for idx, row in df.iterrows():
            place = {
                "pleiades_id": str(row.get('id', '')),
                "label": row.get('title', 'Unknown'),
                "description": row.get('description', ''),
                "place_type": self._normalize_place_type(row.get('featureTypes', '')),
                "coordinates": {
                    "lat": float(row.get('reprLat', 0)),
                    "lon": float(row.get('reprLong', 0)),
                    "wkt": f"POINT({row.get('reprLong', 0)} {row.get('reprLat', 0)})",
                    "precision_meters": 5000  # Default uncertainty
                },
                "temporal_attestation": {
                    "earliest": int(row.get('minDate', 0)),
                    "latest": int(row.get('maxDate', 0)),
                    "overlaps_roman_republic": True
                },
                "uri": f"https://pleiades.stoa.org/places/{row.get('id', '')}",
                "modern_location": row.get('modernLocation', ''),
                "map_display_priority": self._calculate_display_priority(row)
            }
            
            places.append(place)
        
        logger.info(f"Transformed {len(places)} places to map-ready format")
        return places
    
    def _normalize_place_type(self, feature_types: str) -> str:
        """Normalize Pleiades feature types to canonical types."""
        if not feature_types or pd.isna(feature_types):
            return "unknown"
        
        feature_types = str(feature_types).lower()
        
        # Priority mapping (first match wins)
        if 'settlement' in feature_types or 'urban' in feature_types:
            return "settlement"
        elif 'fort' in feature_types or 'military' in feature_types:
            return "military"
        elif 'river' in feature_types or 'stream' in feature_types:
            return "river"
        elif 'temple' in feature_types or 'sanctuary' in feature_types:
            return "religious"
        elif 'mountain' in feature_types or 'hill' in feature_types:
            return "topographic"
        elif 'region' in feature_types or 'province' in feature_types:
            return "region"
        else:
            return "other"
    
    def _calculate_display_priority(self, row: pd.Series) -> int:
        """Calculate map display priority (1=always show, 3=zoom required)."""
        # Priority 1: Major cities, capitals, battle sites
        title = str(row.get('title', '')).lower()
        
        high_priority_keywords = [
            'roma', 'rome', 'carthage', 'alexandria', 'athens',
            'cannae', 'zama', 'pharsalus', 'alesia', 'rubicon'
        ]
        
        if any(keyword in title for keyword in high_priority_keywords):
            return 1
        
        # Priority 2: Notable settlements, regions
        place_type = self._normalize_place_type(row.get('featureTypes', ''))
        if place_type in ['settlement', 'region']:
            return 2
        
        # Priority 3: Everything else
        return 3
    
    def save_to_json(self, places: List[Dict], output_path: Path):
        """Save places to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(places, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(places)} places to {output_path}")
    
    def generate_cypher_import(self, places: List[Dict], output_path: Path):
        """Generate Cypher script for Neo4j import."""
        cypher_statements = [
            "// Pleiades Roman Republic Places Import",
            "// Generated: " + datetime.now().isoformat(),
            "",
            "// Create spatial index for coordinate queries",
            "CREATE INDEX place_coordinates IF NOT EXISTS FOR (p:Place) ON (p.coordinates_wkt);",
            "",
            "// Create constraint for unique Pleiades IDs",
            "CREATE CONSTRAINT place_pleiades_id IF NOT EXISTS FOR (p:Place) REQUIRE p.pleiades_id IS UNIQUE;",
            ""
        ]
        
        for place in places:
            stmt = f"""
// {place['label']} (Pleiades {place['pleiades_id']})
MERGE (p:Place {{pleiades_id: "{place['pleiades_id']}"}})
SET p.label = "{place['label'].replace('"', '\\"')}",
    p.place_type = "{place['place_type']}",
    p.valid_from = {place['temporal_attestation']['earliest']},
    p.valid_to = {place['temporal_attestation']['latest']},
    p.coordinates_wkt = "{place['coordinates']['wkt']}",
    p.lat = {place['coordinates']['lat']},
    p.lon = {place['coordinates']['lon']},
    p.precision_meters = {place['coordinates']['precision_meters']},
    p.map_display_priority = {place['map_display_priority']},
    p.pleiades_uri = "{place['uri']}"

MERGE (auth:AuthorityRecord {{source: "Pleiades", record_id: "{place['pleiades_id']}"}})
SET auth.record_type = "place"

MERGE (p)-[r:ALIGNED_WITH_PLEIADES]->(auth)
SET r.confidence = 0.98,
    r.temporal_attestation = "[{place['temporal_attestation']['earliest']}, {place['temporal_attestation']['latest']}]";
"""
            cypher_statements.append(stmt)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cypher_statements))
        
        logger.info(f"Generated Cypher import script: {output_path}")
    
    def ingest_to_neo4j(self, places: List[Dict]):
        """Ingest places directly to Neo4j."""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect_neo4j() first.")
        
        logger.info(f"Ingesting {len(places)} places to Neo4j...")
        
        with self.driver.session() as session:
            # Create indexes and constraints
            session.run("CREATE INDEX place_coordinates IF NOT EXISTS FOR (p:Place) ON (p.coordinates_wkt)")
            session.run("CREATE CONSTRAINT place_pleiades_id IF NOT EXISTS FOR (p:Place) REQUIRE p.pleiades_id IS UNIQUE")
            
            # Ingest places
            ingested = 0
            for place in places:
                try:
                    session.run("""
                        MERGE (p:Place {pleiades_id: $pleiades_id})
                        SET p.label = $label,
                            p.place_type = $place_type,
                            p.valid_from = $valid_from,
                            p.valid_to = $valid_to,
                            p.coordinates_wkt = $coordinates_wkt,
                            p.lat = $lat,
                            p.lon = $lon,
                            p.precision_meters = $precision_meters,
                            p.map_display_priority = $map_display_priority,
                            p.pleiades_uri = $uri
                        
                        MERGE (auth:AuthorityRecord {source: "Pleiades", record_id: $pleiades_id})
                        SET auth.record_type = "place"
                        
                        MERGE (p)-[r:ALIGNED_WITH_PLEIADES]->(auth)
                        SET r.confidence = 0.98,
                            r.temporal_attestation = $temporal_attestation
                    """, {
                        "pleiades_id": place["pleiades_id"],
                        "label": place["label"],
                        "place_type": place["place_type"],
                        "valid_from": place["temporal_attestation"]["earliest"],
                        "valid_to": place["temporal_attestation"]["latest"],
                        "coordinates_wkt": place["coordinates"]["wkt"],
                        "lat": place["coordinates"]["lat"],
                        "lon": place["coordinates"]["lon"],
                        "precision_meters": place["coordinates"]["precision_meters"],
                        "map_display_priority": place["map_display_priority"],
                        "uri": place["uri"],
                        "temporal_attestation": f"[{place['temporal_attestation']['earliest']}, {place['temporal_attestation']['latest']}]"
                    })
                    
                    ingested += 1
                    if ingested % 50 == 0:
                        logger.info(f"Ingested {ingested}/{len(places)} places...")
                
                except Exception as e:
                    logger.warning(f"Failed to ingest {place['label']}: {e}")
        
        logger.info(f"Successfully ingested {ingested} places to Neo4j")
    
    def export_geojson(self, places: List[Dict], output_path: Path):
        """Export places to GeoJSON for web mapping."""
        features = []
        
        for place in places:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [place["coordinates"]["lon"], place["coordinates"]["lat"]]
                },
                "properties": {
                    "name": place["label"],
                    "pleiades_id": place["pleiades_id"],
                    "place_type": place["place_type"],
                    "valid_from": place["temporal_attestation"]["earliest"],
                    "valid_to": place["temporal_attestation"]["latest"],
                    "display_priority": place["map_display_priority"],
                    "uri": place["uri"]
                }
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2)
        
        logger.info(f"Exported GeoJSON to {output_path}")
    
    def run_pipeline(self, ingest_to_db: bool = True):
        """Execute full ingestion pipeline."""
        logger.info("=" * 80)
        logger.info("PLEIADES BULK INGEST - ROMAN REPUBLIC TEST CASE")
        logger.info("=" * 80)
        
        # Step 1: Download Pleiades dump
        csv_path = self.download_pleiades_dump()
        
        # Step 2: Parse CSV
        df = self.parse_pleiades_csv(csv_path)
        
        # Step 3: Filter to Roman Republic
        df_filtered = self.filter_roman_republic_places(df)
        
        # Step 4: Transform to map-ready format
        places = self.transform_to_map_ready(df_filtered)
        
        # Step 5: Save to JSON
        self.save_to_json(places, OUTPUT_JSON)
        
        # Step 6: Generate Cypher import script
        self.generate_cypher_import(places, OUTPUT_CYPHER)
        
        # Step 7: Export GeoJSON for web mapping
        geojson_path = OUTPUT_DIR / "pleiades_roman_republic_places.geojson"
        self.export_geojson(places, geojson_path)
        
        # Step 8: Ingest to Neo4j (optional)
        if ingest_to_db:
            self.connect_neo4j()
            self.ingest_to_neo4j(places)
            self.close_neo4j()
        
        logger.info("=" * 80)
        logger.info("INGESTION COMPLETE")
        logger.info(f"Total places: {len(places)}")
        logger.info(f"JSON output: {OUTPUT_JSON}")
        logger.info(f"Cypher script: {OUTPUT_CYPHER}")
        logger.info(f"GeoJSON output: {geojson_path}")
        logger.info("=" * 80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pleiades bulk ingest for Roman Republic")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", required=True, help="Neo4j password")
    parser.add_argument("--no-ingest", action="store_true", help="Skip Neo4j ingest (generate files only)")
    
    args = parser.parse_args()
    
    ingester = PleiadesIngester(
        neo4j_uri=args.neo4j_uri,
        neo4j_user=args.neo4j_user,
        neo4j_password=args.neo4j_password
    )
    
    ingester.run_pipeline(ingest_to_db=not args.no_ingest)


if __name__ == "__main__":
    main()
