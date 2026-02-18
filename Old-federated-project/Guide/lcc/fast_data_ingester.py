"""
FAST Data Ingestion Pipeline
===========================

Downloads and processes FAST (Faceted Application of Subject Terminology) data
from OCLC's official data repository. Handles RDF N-Triples format for structured ingestion.
"""

import os
import json
import requests
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import re

# RDF parsing
try:
    import rdflib
    from rdflib import Graph, Namespace, URIRef, Literal
    RDF_AVAILABLE = True
except ImportError:
    print("Warning: rdflib not available. Install with: pip install rdflib")
    RDF_AVAILABLE = False

from enhanced_taxonomy_manager import EnhancedTaxonomyManager
from fast_database_schema import FASTSubject, FASTEdge, FASTFacetType

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FASTDataIngester:
    """
    Handles downloading and ingesting FAST data from OCLC.
    """
    
    # OCLC FAST download URLs (as of October 2024)
    FAST_BASE_URL = "https://www.oclc.org/research/areas/data-science/fast/download"
    
    # RDF N-Triples download URLs by facet
    FAST_RDF_URLS = {
        'topical': 'https://www.oclc.org/content/dam/research/activities/fast/FASTTopical.zip',
        'geographic': 'https://www.oclc.org/content/dam/research/activities/fast/FASTGeographic.zip',
        'form_genre': 'https://www.oclc.org/content/dam/research/activities/fast/FASTFormGenre.zip',
        'personal_name': 'https://www.oclc.org/content/dam/research/activities/fast/FASTPersonal.zip',
        'corporate_name': 'https://www.oclc.org/content/dam/research/activities/fast/FASTCorporate.zip',
        'event': 'https://www.oclc.org/content/dam/research/activities/fast/FASTEvent.zip',
        'chronological': 'https://www.oclc.org/content/dam/research/activities/fast/FASTChronological.zip',
        'title_work': 'https://www.oclc.org/content/dam/research/activities/fast/FASTUniformTitles.zip',
        'meeting': 'https://www.oclc.org/content/dam/research/activities/fast/FASTMeeting.zip'
    }
    
    # FAST namespace definitions
    FAST_NS = Namespace("http://id.worldcat.org/fast/")
    SKOS_NS = Namespace("http://www.w3.org/2004/02/skos/core#")
    RDF_NS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    
    def __init__(self, data_dir: str = "data/fast", database_manager: Optional[EnhancedTaxonomyManager] = None):
        """
        Initialize FAST data ingester.
        
        Args:
            data_dir: Directory to store downloaded FAST data
            database_manager: Database manager for storing processed data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_manager = database_manager or EnhancedTaxonomyManager()
        
        # Processing statistics
        self.stats = {
            'downloaded_facets': [],
            'processed_subjects': 0,
            'processed_edges': 0,
            'errors': [],
            'facet_counts': {}
        }
    
    def download_fast_data(self, facets: Optional[List[str]] = None, force_download: bool = False) -> Dict[str, str]:
        """
        Download FAST data files from OCLC.
        
        Args:
            facets: List of facets to download. If None, downloads priority facets.
            force_download: Whether to re-download existing files
            
        Returns:
            Dictionary mapping facet names to downloaded file paths
        """
        if facets is None:
            # Priority facets for initial implementation
            facets = ['topical', 'geographic', 'form_genre']
        
        downloaded_files = {}
        
        for facet in facets:
            if facet not in self.FAST_RDF_URLS:
                logger.warning(f"Unknown facet: {facet}")
                continue
            
            logger.info(f"Downloading FAST {facet} data...")
            
            # Download destination
            zip_path = self.data_dir / f"fast_{facet}.zip"
            extract_dir = self.data_dir / f"fast_{facet}"
            
            # Skip if already downloaded and not forcing
            if zip_path.exists() and not force_download:
                logger.info(f"Using existing download: {zip_path}")
                downloaded_files[facet] = str(extract_dir)
                continue
            
            try:
                # Download the ZIP file
                response = requests.get(self.FAST_RDF_URLS[facet], stream=True)
                response.raise_for_status()
                
                # Save ZIP file
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract ZIP file
                extract_dir.mkdir(exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                downloaded_files[facet] = str(extract_dir)
                self.stats['downloaded_facets'].append(facet)
                
                logger.info(f"Successfully downloaded and extracted {facet} data")
                
            except Exception as e:
                error_msg = f"Failed to download {facet}: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
        
        return downloaded_files
    
    def parse_rdf_file(self, file_path: Path, facet_type: FASTFacetType) -> List[Dict[str, Any]]:
        """
        Parse a FAST RDF N-Triples file to extract subject data.
        
        Args:
            file_path: Path to the RDF file
            facet_type: Type of FAST facet
            
        Returns:
            List of parsed FAST subject dictionaries
        """
        if not RDF_AVAILABLE:
            raise ImportError("rdflib is required for RDF parsing. Install with: pip install rdflib")
        
        subjects = []
        
        try:
            # Load RDF graph
            graph = Graph()
            graph.parse(str(file_path), format='nt')  # N-Triples format
            
            logger.info(f"Parsing RDF file: {file_path.name} ({len(graph)} triples)")
            
            # Extract subjects from the graph
            for subject_uri in graph.subjects(predicate=self.RDF_NS.type, object=self.SKOS_NS.Concept):
                subject_data = self._extract_subject_data(graph, subject_uri, facet_type)
                if subject_data:
                    subjects.append(subject_data)
            
            logger.info(f"Extracted {len(subjects)} subjects from {file_path.name}")
            
        except Exception as e:
            error_msg = f"Failed to parse RDF file {file_path}: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
        
        return subjects
    
    def _extract_subject_data(self, graph: Graph, subject_uri: URIRef, facet_type: FASTFacetType) -> Optional[Dict[str, Any]]:
        """
        Extract data for a single FAST subject from RDF graph.
        
        Args:
            graph: RDF graph
            subject_uri: URI of the subject
            facet_type: FAST facet type
            
        Returns:
            Dictionary with subject data or None if extraction fails
        """
        try:
            # Extract FAST ID from URI (e.g., http://id.worldcat.org/fast/1234567)
            fast_id_match = re.search(r'/fast/(\d+)', str(subject_uri))
            if not fast_id_match:
                return None
            
            fast_id = f"fst{fast_id_match.group(1).zfill(8)}"
            
            # Extract preferred label
            pref_label = None
            for label in graph.objects(subject_uri, self.SKOS_NS.prefLabel):
                pref_label = str(label)
                break
            
            if not pref_label:
                return None
            
            # Extract alternative labels
            alt_labels = []
            for alt_label in graph.objects(subject_uri, self.SKOS_NS.altLabel):
                alt_labels.append(str(alt_label))
            
            # Extract scope notes
            scope_notes = []
            for scope_note in graph.objects(subject_uri, self.SKOS_NS.scopeNote):
                scope_notes.append(str(scope_note))
            
            # Extract broader/narrower relationships
            broader_terms = []
            for broader in graph.objects(subject_uri, self.SKOS_NS.broader):
                broader_id_match = re.search(r'/fast/(\d+)', str(broader))
                if broader_id_match:
                    broader_terms.append(f"fst{broader_id_match.group(1).zfill(8)}")
            
            narrower_terms = []
            for narrower in graph.objects(subject_uri, self.SKOS_NS.narrower):
                narrower_id_match = re.search(r'/fast/(\d+)', str(narrower))
                if narrower_id_match:
                    narrower_terms.append(f"fst{narrower_id_match.group(1).zfill(8)}")
            
            # Extract related terms
            related_terms = []
            for related in graph.objects(subject_uri, self.SKOS_NS.related):
                related_id_match = re.search(r'/fast/(\d+)', str(related))
                if related_id_match:
                    related_terms.append(f"fst{related_id_match.group(1).zfill(8)}")
            
            subject_data = {
                'fast_id': fast_id,
                'heading': pref_label,
                'facet_type': facet_type,
                'variant_forms': alt_labels,
                'scope_note': '; '.join(scope_notes) if scope_notes else None,
                'related_terms': related_terms,
                'broader_terms': broader_terms,
                'narrower_terms': narrower_terms,
                'authority_source': 'fast',
                'confidence_score': 100,
                'extra': {
                    'uri': str(subject_uri),
                    'extracted_at': datetime.now().isoformat()
                }
            }
            
            return subject_data
            
        except Exception as e:
            logger.warning(f"Failed to extract data for subject {subject_uri}: {str(e)}")
            return None
    
    def process_facet_data(self, facet_dir: Path, facet_type: FASTFacetType) -> List[Dict[str, Any]]:
        """
        Process all RDF files in a facet directory.
        
        Args:
            facet_dir: Directory containing extracted FAST data
            facet_type: FAST facet type
            
        Returns:
            List of processed FAST subjects
        """
        all_subjects = []
        
        # Find RDF files (usually .nt or .rdf)
        rdf_files = list(facet_dir.glob("*.nt")) + list(facet_dir.glob("*.rdf"))
        
        if not rdf_files:
            logger.warning(f"No RDF files found in {facet_dir}")
            return all_subjects
        
        for rdf_file in rdf_files:
            logger.info(f"Processing RDF file: {rdf_file.name}")
            subjects = self.parse_rdf_file(rdf_file, facet_type)
            all_subjects.extend(subjects)
        
        self.stats['facet_counts'][facet_type.value] = len(all_subjects)
        return all_subjects
    
    def ingest_to_database(self, subjects: List[Dict[str, Any]]) -> int:
        """
        Ingest FAST subjects into the database.
        
        Args:
            subjects: List of FAST subject dictionaries
            
        Returns:
            Number of subjects successfully ingested
        """
        ingested_count = 0
        
        with self.db_manager.get_session() as session:
            for subject_data in subjects:
                try:
                    # Create FAST subject
                    fast_subject = self.db_manager.create_fast_subject(
                        fast_id=subject_data['fast_id'],
                        heading=subject_data['heading'],
                        facet_type=subject_data['facet_type'],
                        variant_forms=subject_data.get('variant_forms', []),
                        scope_note=subject_data.get('scope_note'),
                        related_terms=subject_data.get('related_terms', []),
                        authority_source=subject_data.get('authority_source', 'fast'),
                        confidence_score=subject_data.get('confidence_score', 100),
                        extra=subject_data.get('extra', {})
                    )
                    
                    ingested_count += 1
                    
                    if ingested_count % 1000 == 0:
                        logger.info(f"Ingested {ingested_count} FAST subjects...")
                
                except Exception as e:
                    error_msg = f"Failed to ingest subject {subject_data.get('fast_id', 'unknown')}: {str(e)}"
                    logger.warning(error_msg)
                    self.stats['errors'].append(error_msg)
        
        self.stats['processed_subjects'] += ingested_count
        return ingested_count
    
    def create_fast_edges(self, subjects: List[Dict[str, Any]]) -> int:
        """
        Create edges between FAST subjects based on hierarchical relationships.
        
        Args:
            subjects: List of FAST subject dictionaries with relationship data
            
        Returns:
            Number of edges created
        """
        edges_created = 0
        
        with self.db_manager.get_session() as session:
            for subject_data in subjects:
                fast_id = subject_data['fast_id']
                
                # Create broader/narrower relationships
                for broader_id in subject_data.get('broader_terms', []):
                    try:
                        edge = FASTEdge(
                            source_fast_id=fast_id,
                            target_fast_id=broader_id,
                            relationship_type='broader',
                            strength=90,
                            source='fast_rdf'
                        )
                        session.add(edge)
                        edges_created += 1
                    except Exception as e:
                        logger.warning(f"Failed to create broader edge {fast_id} -> {broader_id}: {e}")
                
                for narrower_id in subject_data.get('narrower_terms', []):
                    try:
                        edge = FASTEdge(
                            source_fast_id=fast_id,
                            target_fast_id=narrower_id,
                            relationship_type='narrower',
                            strength=90,
                            source='fast_rdf'
                        )
                        session.add(edge)
                        edges_created += 1
                    except Exception as e:
                        logger.warning(f"Failed to create narrower edge {fast_id} -> {narrower_id}: {e}")
                
                # Create related term relationships
                for related_id in subject_data.get('related_terms', []):
                    try:
                        edge = FASTEdge(
                            source_fast_id=fast_id,
                            target_fast_id=related_id,
                            relationship_type='related',
                            strength=70,
                            source='fast_rdf'
                        )
                        session.add(edge)
                        edges_created += 1
                    except Exception as e:
                        logger.warning(f"Failed to create related edge {fast_id} -> {related_id}: {e}")
            
            session.commit()
        
        self.stats['processed_edges'] += edges_created
        return edges_created
    
    def run_full_ingestion(self, facets: Optional[List[str]] = None, force_download: bool = False) -> Dict[str, Any]:
        """
        Run complete FAST data ingestion pipeline.
        
        Args:
            facets: List of facets to process
            force_download: Whether to re-download existing files
            
        Returns:
            Ingestion statistics and results
        """
        logger.info("Starting FAST data ingestion pipeline...")
        start_time = datetime.now()
        
        # Reset statistics
        self.stats = {
            'downloaded_facets': [],
            'processed_subjects': 0,
            'processed_edges': 0,
            'errors': [],
            'facet_counts': {}
        }
        
        try:
            # Step 1: Download data
            downloaded_files = self.download_fast_data(facets, force_download)
            
            if not downloaded_files:
                logger.error("No FAST data files downloaded")
                return self.stats
            
            # Step 2: Create database tables
            self.db_manager.create_tables()
            
            # Step 3: Process each facet
            all_subjects = []
            
            for facet_name, facet_dir in downloaded_files.items():
                logger.info(f"Processing {facet_name} facet...")
                
                # Map facet name to enum
                facet_type_mapping = {
                    'topical': FASTFacetType.TOPICAL,
                    'geographic': FASTFacetType.GEOGRAPHIC,
                    'form_genre': FASTFacetType.FORM_GENRE,
                    'personal_name': FASTFacetType.PERSONAL_NAME,
                    'corporate_name': FASTFacetType.CORPORATE_NAME,
                    'event': FASTFacetType.EVENT,
                    'chronological': FASTFacetType.CHRONOLOGICAL,
                    'title_work': FASTFacetType.TITLE_WORK
                }
                
                facet_type = facet_type_mapping.get(facet_name)
                if not facet_type:
                    logger.warning(f"Unknown facet type: {facet_name}")
                    continue
                
                # Process facet data
                subjects = self.process_facet_data(Path(facet_dir), facet_type)
                all_subjects.extend(subjects)
                
                # Ingest to database
                if subjects:
                    ingested = self.ingest_to_database(subjects)
                    logger.info(f"Ingested {ingested} subjects for {facet_name} facet")
            
            # Step 4: Create edges
            if all_subjects:
                edges_created = self.create_fast_edges(all_subjects)
                logger.info(f"Created {edges_created} FAST relationship edges")
            
            # Final statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.stats.update({
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'total_subjects': len(all_subjects),
                'success': True
            })
            
            logger.info(f"FAST ingestion completed in {duration:.2f} seconds")
            logger.info(f"Processed {self.stats['processed_subjects']} subjects and {self.stats['processed_edges']} edges")
            
        except Exception as e:
            error_msg = f"FAST ingestion failed: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            self.stats['success'] = False
        
        return self.stats

def main():
    """Main function for running FAST data ingestion."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest FAST data into taxonomy database')
    parser.add_argument('--facets', nargs='+', 
                       choices=['topical', 'geographic', 'form_genre', 'personal_name', 
                               'corporate_name', 'event', 'chronological', 'title_work'],
                       default=['topical', 'geographic', 'form_genre'],
                       help='FAST facets to process')
    parser.add_argument('--force-download', action='store_true',
                       help='Force re-download of existing files')
    parser.add_argument('--data-dir', default='data/fast',
                       help='Directory for FAST data files')
    
    args = parser.parse_args()
    
    # Initialize ingester
    ingester = FASTDataIngester(data_dir=args.data_dir)
    
    # Run ingestion
    results = ingester.run_full_ingestion(
        facets=args.facets,
        force_download=args.force_download
    )
    
    # Print results
    print("\nFAST Data Ingestion Results:")
    print("=" * 50)
    print(f"Success: {results.get('success', False)}")
    print(f"Processed Subjects: {results.get('processed_subjects', 0)}")
    print(f"Processed Edges: {results.get('processed_edges', 0)}")
    print(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
    
    if results.get('facet_counts'):
        print("\nFacet Counts:")
        for facet, count in results['facet_counts'].items():
            print(f"  {facet}: {count}")
    
    if results.get('errors'):
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  • {error}")

if __name__ == "__main__":
    main()