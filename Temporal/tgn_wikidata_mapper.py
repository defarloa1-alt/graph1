"""
TGN-Wikidata Mapper
===================
Build and maintain mappings between Getty TGN IDs and Wikidata QIDs.

Usage:
    python Temporal/tgn_wikidata_mapper.py --build-cache
    python Temporal/tgn_wikidata_mapper.py --enrich-neo4j
    python Temporal/tgn_wikidata_mapper.py --lookup 7000874

Author: Chrystallum Project
Date: 2026-02-17
"""

import requests
import pandas as pd
import argparse
import time
from typing import Dict, List, Optional
from pathlib import Path
import json


class TGNWikidataMapper:
    """
    Maps Getty TGN IDs to Wikidata QIDs using SPARQL queries.
    Caches results locally for fast lookups.
    """

    WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
    USER_AGENT = "Chrystallum/1.0 (Historical Knowledge Graph; contact@example.com)"

    def __init__(self):
        """Initialize mapper and ensure data directory exists."""
        self.base_dir = Path(__file__).resolve().parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.data_dir / "tgn_wikidata_mapping.csv"
        self.stats_file = self.data_dir / "tgn_wikidata_mapping_stats.json"

    def build_complete_mapping(self, batch_size: int = 1000) -> pd.DataFrame:
        """
        Query Wikidata for all TGN→QID mappings.

        Wikidata Property P1667 = Getty TGN ID

        Args:
            batch_size: Number of results per SPARQL query (max 10000)

        Returns:
            DataFrame with columns: tgn_id, qid, label, latitude, longitude
        """
        print("=" * 60)
        print("Building TGN→Wikidata QID Mapping Cache")
        print("=" * 60)

        all_data = []
        offset = 0
        # Resume from existing cache if present
        if Path(self.CACHE_FILE).exists():
            print(f"Resuming from existing cache: {self.CACHE_FILE}")
            df_existing = pd.read_csv(self.CACHE_FILE)
            all_data = df_existing.to_dict('records')
            offset = len(df_existing)

        while True:
            print(f"\nFetching batch starting at offset {offset}...")

            query = f"""
            SELECT ?tgn ?item ?itemLabel ?lat ?long WHERE {{
                ?item wdt:P1667 ?tgn .

                # Get coordinates if available (Wikidata P625)
                OPTIONAL {{ 
                    ?item p:P625 ?coordinate .
                    ?coordinate psv:P625 ?coordValue .
                    ?coordValue wikibase:geoLatitude ?lat .
                    ?coordValue wikibase:geoLongitude ?long .
                }}

                SERVICE wikibase:label {{ 
                    bd:serviceParam wikibase:language "en,la,it,el,ar". 
                }}
            }}
            LIMIT {batch_size}
            OFFSET {offset}
            """

            try:
                response = requests.get(
                    self.WIKIDATA_SPARQL,
                    params={'query': query, 'format': 'json'},
                    headers={'User-Agent': self.USER_AGENT},
                    timeout=60
                )

                if response.status_code != 200:
                    print(f"  ✗ Error: HTTP {response.status_code}")
                    print(f"  Response: {response.text[:500]}")
                    break

                results = response.json()
                bindings = results.get('results', {}).get('bindings', [])

                if not bindings:
                    print(f"  ✓ No more results. Completed.")
                    break

                # Parse batch
                for binding in bindings:
                    all_data.append({
                        'tgn_id': binding['tgn']['value'],
                        'qid': binding['item']['value'].split('/')[-1],
                        'label': binding.get('itemLabel', {}).get('value', 'Unknown'),
                        'latitude': float(binding['lat']['value']) if 'lat' in binding else None,
                        'longitude': float(binding['long']['value']) if 'long' in binding else None
                    })

                print(f"  ✓ Retrieved {len(bindings)} mappings (total: {len(all_data)})")

                # If we got fewer results than batch_size, we're done
                if len(bindings) < batch_size:
                    print(f"  ✓ Completed (final batch with {len(bindings)} results)")
                    break

                offset += batch_size

                # Rate limiting - be nice to Wikidata
                time.sleep(8)

            except requests.Timeout:
                print(f"  ✗ Timeout at offset {offset}, retrying after 30s...")
                time.sleep(30)
                continue
            except Exception as e:
                print(f"  ✗ Error: {e}")
                print("  Saving progress so far...")
                # Save partial progress
                df = pd.DataFrame(all_data)
                df.to_csv(self.CACHE_FILE, index=False)
                break

        # Create DataFrame
        df = pd.DataFrame(all_data)

        # Remove duplicates (keep first occurrence)
        df = df.drop_duplicates(subset=['tgn_id'], keep='first')

        # Save to CSV
        df.to_csv(self.cache_file, index=False)

        # Save statistics
        stats = {
            'total_mappings': len(df),
            'with_coordinates': df['latitude'].notna().sum(),
            'without_coordinates': df['latitude'].isna().sum(),
            'last_updated': pd.Timestamp.now().isoformat(),
            'unique_qids': df['qid'].nunique(),
            'unique_tgns': df['tgn_id'].nunique()
        }

        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print("\n" + "=" * 60)
        print(f"✓ SUCCESS: Cached {len(df):,} TGN→QID mappings")
        print(f"  - File: {self.cache_file}")
        print(f"  - With coordinates: {stats['with_coordinates']:,}")
        print(f"  - Without coordinates: {stats['without_coordinates']:,}")
        print("=" * 60)

        return df

    def lookup_qid(self, tgn_id: str) -> Optional[Dict]:
        """
        Fast lookup from cached file.

        Args:
            tgn_id: Getty TGN ID (e.g., "7000874")

        Returns:
            Dict with qid, label, latitude, longitude or None if not found
        """
        if not self.cache_file.exists():
            print(f"✗ Cache file not found: {self.cache_file}")
            print("  Run with --build-cache first")
            return None

        df = pd.read_csv(self.cache_file)
        result = df[df['tgn_id'] == tgn_id]

        if result.empty:
            return None

        row = result.iloc[0]
        return {
            'tgn_id': row['tgn_id'],
            'qid': row['qid'],
            'label': row['label'],
            'latitude': row['latitude'] if pd.notna(row['latitude']) else None,
            'longitude': row['longitude'] if pd.notna(row['longitude']) else None
        }

    def lookup_tgn(self, qid: str) -> Optional[Dict]:
        """
        Reverse lookup: QID → TGN ID.

        Args:
            qid: Wikidata QID (e.g., "Q220")

        Returns:
            Dict with tgn_id, label, coordinates or None
        """
        if not self.cache_file.exists():
            print(f"✗ Cache file not found: {self.cache_file}")
            return None

        df = pd.read_csv(self.cache_file)
        result = df[df['qid'] == qid]

        if result.empty:
            return None

        row = result.iloc[0]
        return {
            'tgn_id': row['tgn_id'],
            'qid': row['qid'],
            'label': row['label'],
            'latitude': row['latitude'] if pd.notna(row['latitude']) else None,
            'longitude': row['longitude'] if pd.notna(row['longitude']) else None
        }

    def batch_lookup(self, tgn_ids: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Lookup multiple TGN IDs at once.

        Args:
            tgn_ids: List of TGN IDs

        Returns:
            Dict mapping tgn_id → result dict (or None if not found)
        """
        if not self.cache_file.exists():
            print(f"✗ Cache file not found: {self.cache_file}")
            return {}

        df = pd.read_csv(self.cache_file)
        results = {}

        for tgn_id in tgn_ids:
            result = df[df['tgn_id'] == tgn_id]

            if result.empty:
                results[tgn_id] = None
            else:
                row = result.iloc[0]
                results[tgn_id] = {
                    'tgn_id': row['tgn_id'],
                    'qid': row['qid'],
                    'label': row['label'],
                    'latitude': row['latitude'] if pd.notna(row['latitude']) else None,
                    'longitude': row['longitude'] if pd.notna(row['longitude']) else None
                }

        return results

    def enrich_neo4j_places(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """
        Add Wikidata QIDs to existing Place nodes in Neo4j.

        Args:
            neo4j_uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
        """
        try:
            from neo4j import GraphDatabase
        except ImportError:
            print("✗ neo4j package not installed. Run: pip install neo4j")
            return

        if not self.cache_file.exists():
            print(f"✗ Cache file not found: {self.cache_file}")
            print("  Run with --build-cache first")
            return

        print("=" * 60)
        print("Enriching Neo4j Place Nodes with Wikidata QIDs")
        print("=" * 60)

        df = pd.read_csv(self.cache_file)

        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

        enriched_count = 0
        not_found_count = 0

        with driver.session() as session:
            for _, row in df.iterrows():
                # Check if Place exists
                result = session.run(
                    "MATCH (p:Place {getty_tgn: $tgn_id}) RETURN count(p) as count",
                    tgn_id=row['tgn_id']
                )

                count = result.single()['count']

                if count > 0:
                    # Enrich with QID
                    session.run("""
                        MATCH (p:Place {getty_tgn: $tgn_id})
                        SET p.wikidata_qid = $qid,
                            p.wikidata_label = $label,
                            p.wikidata_enriched = datetime()
                    """, 
                    tgn_id=row['tgn_id'],
                    qid=row['qid'],
                    label=row['label'])

                    enriched_count += 1

                    if enriched_count % 100 == 0:
                        print(f"  ✓ Enriched {enriched_count} places...")
                else:
                    not_found_count += 1

        driver.close()

        print("\n" + "=" * 60)
        print(f"✓ SUCCESS: Enriched {enriched_count} Place nodes")
        print(f"  - Not found in Neo4j: {not_found_count}")
        print("=" * 60)

    def show_stats(self):
        """Display statistics about cached mappings."""
        if not self.stats_file.exists():
            print("✗ No statistics file found. Run --build-cache first.")
            return

        with open(self.stats_file, 'r') as f:
            stats = json.load(f)

        print("\n" + "=" * 60)
        print("TGN→Wikidata Mapping Statistics")
        print("=" * 60)
        print(f"Total mappings:        {stats['total_mappings']:,}")
        print(f"With coordinates:      {stats['with_coordinates']:,}")
        print(f"Without coordinates:   {stats['without_coordinates']:,}")
        print(f"Unique QIDs:           {stats['unique_qids']:,}")
        print(f"Unique TGN IDs:        {stats['unique_tgns']:,}")
        print(f"Last updated:          {stats['last_updated']}")
        print("=" * 60)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Build and maintain TGN→Wikidata QID mappings"
    )

    parser.add_argument(
        '--build-cache',
        action='store_true',
        help='Build complete TGN→QID mapping cache from Wikidata'
    )

    parser.add_argument(
        '--lookup',
        type=str,
        metavar='TGN_ID',
        help='Lookup QID for a TGN ID (e.g., 7000874)'
    )

    parser.add_argument(
        '--reverse-lookup',
        type=str,
        metavar='QID',
        help='Reverse lookup: find TGN ID for a Wikidata QID (e.g., Q220)'
    )

    parser.add_argument(
        '--enrich-neo4j',
        action='store_true',
        help='Add QIDs to existing Place nodes in Neo4j'
    )

    parser.add_argument(
        '--neo4j-uri',
        type=str,
        default='bolt://localhost:7687',
        help='Neo4j connection URI (default: bolt://localhost:7687)'
    )

    parser.add_argument(
        '--neo4j-user',
        type=str,
        default='neo4j',
        help='Neo4j username (default: neo4j)'
    )

    parser.add_argument(
        '--neo4j-password',
        type=str,
        default='password',
        help='Neo4j password (default: password)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show cache statistics'
    )

    args = parser.parse_args()

    mapper = TGNWikidataMapper()

    if args.build_cache:
        mapper.build_complete_mapping()

    elif args.lookup:
        result = mapper.lookup_qid(args.lookup)
        if result:
            print(f"\nTGN {args.lookup} → Wikidata {result['qid']}")
            print(f"  Label: {result['label']}")
            if result['latitude'] and result['longitude']:
                print(f"  Coordinates: {result['latitude']}, {result['longitude']}")
        else:
            print(f"\n✗ No Wikidata QID found for TGN {args.lookup}")

    elif args.reverse_lookup:
        result = mapper.lookup_tgn(args.reverse_lookup)
        if result:
            print(f"\nWikidata {args.reverse_lookup} → TGN {result['tgn_id']}")
            print(f"  Label: {result['label']}")
            if result['latitude'] and result['longitude']:
                print(f"  Coordinates: {result['latitude']}, {result['longitude']}")
        else:
            print(f"\n✗ No TGN ID found for Wikidata {args.reverse_lookup}")

    elif args.enrich_neo4j:
        mapper.enrich_neo4j_places(
            args.neo4j_uri,
            args.neo4j_user,
            args.neo4j_password
        )

    elif args.stats:
        mapper.show_stats()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
