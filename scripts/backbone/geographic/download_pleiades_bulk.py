"""
Download and Process Pleiades Bulk Data
========================================

Downloads the latest Pleiades gazetteer bulk exports (places, locations, names)
and prepares them for Neo4j import.

Pleiades Data Structure:
- pleiades-places-latest.csv.gz (6.3MB) - Core place entities
- pleiades-locations-latest.csv.gz (35MB) - Coordinate data
- pleiades-names-latest.csv.gz (3.4MB) - Historical name variants

Output:
- Geographic/pleiades_places.csv - Normalized places for Neo4j
- Geographic/pleiades_coordinates.csv - Location data
- Geographic/pleiades_names.csv - Name variants

Usage:
    python scripts/backbone/geographic/download_pleiades_bulk.py
    python scripts/backbone/geographic/download_pleiades_bulk.py --skip-download
"""

import csv
import gzip
import os
import sys
from pathlib import Path
from urllib.request import urlretrieve
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
GEOGRAPHIC_DIR = PROJECT_ROOT / "Geographic"
TEMP_DIR = GEOGRAPHIC_DIR / "temp"

# Pleiades URLs
BASE_URL = "https://atlantides.org/downloads/pleiades/dumps/"
FILES = {
    "places": "pleiades-places-latest.csv.gz",
    "locations": "pleiades-locations-latest.csv.gz",
    "names": "pleiades-names-latest.csv.gz"
}

def download_file(url: str, output_path: Path) -> bool:
    """Download a file with progress reporting."""
    try:
        logger.info(f"Downloading {url}...")
        
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = (downloaded / total_size) * 100 if total_size > 0 else 0
            if block_num % 100 == 0:  # Report every ~100 blocks
                logger.info(f"  Progress: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB)")
        
        urlretrieve(url, output_path, reporthook=report_progress)
        logger.info(f"✓ Downloaded to {output_path}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to download {url}: {e}")
        return False

def extract_gzip(input_path: Path, output_path: Path) -> bool:
    """Extract gzip file."""
    try:
        logger.info(f"Extracting {input_path.name}...")
        with gzip.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
        logger.info(f"✓ Extracted to {output_path}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to extract {input_path}: {e}")
        return False

def process_places(input_csv: Path, output_csv: Path) -> dict:
    """
    Process pleiades-places-latest.csv into Neo4j-ready format.
    
    Expected columns: id, title, description, placeTypes, bbox, reprLat, reprLong, ...
    
    Output format:
    pleiades_id, label, description, place_type, bbox, lat, long, min_date, max_date, uri
    """
    logger.info(f"Processing places from {input_csv}...")
    
    stats = {"total": 0, "ancient": 0, "with_coords": 0, "errors": 0}
    
    try:
        with open(input_csv, 'r', encoding='utf-8') as f_in:
            with open(output_csv, 'w', encoding='utf-8', newline='') as f_out:
                reader = csv.DictReader(f_in)
                writer = csv.writer(f_out)
                
                # Write header
                writer.writerow([
                    'pleiades_id', 'label', 'description', 'place_type', 
                    'bbox', 'lat', 'long', 'min_date', 'max_date', 
                    'uri', 'created', 'modified'
                ])
                
                for row in reader:
                    stats["total"] += 1
                    
                    try:
                        pleiades_id = row.get('id', '').strip()
                        title = row.get('title', '').strip()
                        description = row.get('description', '').strip()
                        place_types = row.get('placeTypes', '').strip()
                        bbox = row.get('bbox', '').strip()
                        lat = row.get('reprLat', '').strip()
                        long = row.get('reprLong', '').strip()
                        min_date = row.get('minDate', '').strip()
                        max_date = row.get('maxDate', '').strip()
                        created = row.get('created', '').strip()
                        modified = row.get('modified', '').strip()
                        
                        # Build URI
                        uri = f"https://pleiades.stoa.org/places/{pleiades_id}"
                        
                        # Track stats
                        if min_date or max_date:
                            stats["ancient"] += 1
                        if lat and long:
                            stats["with_coords"] += 1
                        
                        writer.writerow([
                            pleiades_id, title, description, place_types,
                            bbox, lat, long, min_date, max_date,
                            uri, created, modified
                        ])
                        
                    except Exception as e:
                        stats["errors"] += 1
                        logger.warning(f"Error processing row {stats['total']}: {e}")
        
        logger.info(f"✓ Processed {stats['total']} places:")
        logger.info(f"  - {stats['ancient']} with temporal bounds")
        logger.info(f"  - {stats['with_coords']} with coordinates")
        logger.info(f"  - {stats['errors']} errors")
        
        return stats
        
    except Exception as e:
        logger.error(f"✗ Failed to process places: {e}")
        return stats

def process_names(input_csv: Path, output_csv: Path) -> dict:
    """
    Process pleiades-names-latest.csv into Neo4j-ready format.
    
    Expected columns: id, nameAttested, nameLanguage, nameType, pid (place ID), ...
    
    Output format:
    name_id, pleiades_id, name_attested, language, name_type, romanized, created, modified
    """
    logger.info(f"Processing names from {input_csv}...")
    
    stats = {"total": 0, "attested": 0, "errors": 0}
    
    try:
        with open(input_csv, 'r', encoding='utf-8') as f_in:
            with open(output_csv, 'w', encoding='utf-8', newline='') as f_out:
                reader = csv.DictReader(f_in)
                writer = csv.writer(f_out)
                
                # Write header
                writer.writerow([
                    'name_id', 'pleiades_id', 'name_attested', 'language', 
                    'name_type', 'romanized', 'created', 'modified'
                ])
                
                for row in reader:
                    stats["total"] += 1
                    
                    try:
                        name_id = row.get('id', '').strip()
                        pleiades_id = row.get('pid', '').strip()
                        
                        # Strip /places/ prefix if present
                        if pleiades_id.startswith('/places/'):
                            pleiades_id = pleiades_id.replace('/places/', '')
                        
                        name_attested = row.get('nameAttested', '').strip()
                        language = row.get('nameLanguage', '').strip()
                        name_type = row.get('nameType', '').strip()
                        romanized = row.get('nameTransliterated', '').strip()
                        created = row.get('created', '').strip()
                        modified = row.get('modified', '').strip()
                        
                        if name_attested:
                            stats["attested"] += 1
                        
                        writer.writerow([
                            name_id, pleiades_id, name_attested, language,
                            name_type, romanized, created, modified
                        ])
                        
                    except Exception as e:
                        stats["errors"] += 1
                        logger.warning(f"Error processing name row {stats['total']}: {e}")
        
        logger.info(f"✓ Processed {stats['total']} names:")
        logger.info(f"  - {stats['attested']} with attested forms")
        logger.info(f"  - {stats['errors']} errors")
        
        return stats
        
    except Exception as e:
        logger.error(f"✗ Failed to process names: {e}")
        return stats

def process_locations(input_csv: Path, output_csv: Path) -> dict:
    """
    Process pleiades-locations-latest.csv into Neo4j-ready format.
    
    Expected columns: id, pid (place ID), title, locationTypeURI, lat, long, ...
    
    Output format:
    location_id, pleiades_id, title, location_type, lat, long, precision, created, modified
    """
    logger.info(f"Processing locations from {input_csv}...")
    
    stats = {"total": 0, "with_coords": 0, "errors": 0}
    
    try:
        with open(input_csv, 'r', encoding='utf-8') as f_in:
            with open(output_csv, 'w', encoding='utf-8', newline='') as f_out:
                reader = csv.DictReader(f_in)
                writer = csv.writer(f_out)
                
                # Write header
                writer.writerow([
                    'location_id', 'pleiades_id', 'title', 'location_type',
                    'lat', 'long', 'precision', 'created', 'modified'
                ])
                
                for row in reader:
                    stats["total"] += 1
                    
                    try:
                        location_id = row.get('id', '').strip()
                        pleiades_id = row.get('pid', '').strip()
                        title = row.get('title', '').strip()
                        location_type = row.get('locationType', '').strip()
                        lat = row.get('reprLat', '').strip()
                        long = row.get('reprLong', '').strip()
                        precision = row.get('locationPrecision', '').strip()
                        created = row.get('created', '').strip()
                        modified = row.get('modified', '').strip()
                        
                        if lat and long:
                            stats["with_coords"] += 1
                        
                        writer.writerow([
                            location_id, pleiades_id, title, location_type,
                            lat, long, precision, created, modified
                        ])
                        
                    except Exception as e:
                        stats["errors"] += 1
                        logger.warning(f"Error processing location row {stats['total']}: {e}")
        
        logger.info(f"✓ Processed {stats['total']} locations:")
        logger.info(f"  - {stats['with_coords']} with coordinates")
        logger.info(f"  - {stats['errors']} errors")
        
        return stats
        
    except Exception as e:
        logger.error(f"✗ Failed to process locations: {e}")
        return stats

def main(skip_download: bool = False):
    """Main execution flow."""
    logger.info("=" * 60)
    logger.info("Pleiades Bulk Data Download & Processing")
    logger.info("=" * 60)
    
    # Create directories
    GEOGRAPHIC_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    
    # Step 1: Download files (if not skipped)
    if not skip_download:
        logger.info("\n[1/4] Downloading Pleiades bulk data...")
        for key, filename in FILES.items():
            url = BASE_URL + filename
            output_path = TEMP_DIR / filename
            
            if output_path.exists():
                logger.info(f"  Skipping {filename} (already exists)")
            else:
                if not download_file(url, output_path):
                    logger.error(f"Failed to download {filename}, aborting.")
                    return False
    else:
        logger.info("\n[1/4] Skipping download (using existing files)...")
    
    # Step 2: Extract gzip files
    logger.info("\n[2/4] Extracting gzip files...")
    for key, filename in FILES.items():
        gz_path = TEMP_DIR / filename
        csv_path = TEMP_DIR / filename.replace('.gz', '')
        
        if not gz_path.exists():
            logger.error(f"Missing file: {gz_path}")
            return False
        
        if csv_path.exists():
            logger.info(f"  Skipping extraction of {filename} (already extracted)")
        else:
            if not extract_gzip(gz_path, csv_path):
                logger.error(f"Failed to extract {filename}, aborting.")
                return False
    
    # Step 3: Process CSV files
    logger.info("\n[3/4] Processing CSV files for Neo4j import...")
    
    # Process places
    places_stats = process_places(
        TEMP_DIR / "pleiades-places-latest.csv",
        GEOGRAPHIC_DIR / "pleiades_places.csv"
    )
    
    # Process names
    names_stats = process_names(
        TEMP_DIR / "pleiades-names-latest.csv",
        GEOGRAPHIC_DIR / "pleiades_names.csv"
    )
    
    # Process locations
    locations_stats = process_locations(
        TEMP_DIR / "pleiades-locations-latest.csv",
        GEOGRAPHIC_DIR / "pleiades_coordinates.csv"
    )
    
    # Step 4: Summary
    logger.info("\n[4/4] Summary:")
    logger.info("=" * 60)
    logger.info(f"✓ Places: {places_stats['total']} processed")
    logger.info(f"✓ Names: {names_stats['total']} processed")
    logger.info(f"✓ Locations: {locations_stats['total']} processed")
    logger.info("\nOutput files created:")
    logger.info(f"  - {GEOGRAPHIC_DIR / 'pleiades_places.csv'}")
    logger.info(f"  - {GEOGRAPHIC_DIR / 'pleiades_names.csv'}")
    logger.info(f"  - {GEOGRAPHIC_DIR / 'pleiades_coordinates.csv'}")
    logger.info("\nNext steps:")
    logger.info("  1. Review CSV files in Geographic/ folder")
    logger.info("  2. Run: python scripts/backbone/geographic/import_pleiades_to_neo4j.py")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    skip_download = "--skip-download" in sys.argv
    success = main(skip_download=skip_download)
    sys.exit(0 if success else 1)
