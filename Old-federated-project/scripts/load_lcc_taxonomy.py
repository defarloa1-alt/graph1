#!/usr/bin/env python3
"""
LCC Taxonomy ETL Script
======================

Extract, Transform, and Load LCC taxonomy data from parsed files into PostgreSQL.
Implements idempotent loading with upsert logic and data validation.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
import logging

# Database imports (will be installed via requirements.txt)
_DATABASE_AVAILABLE = False
if TYPE_CHECKING:
    from lcc_database_schema import LCCDatabaseManager, SubjectNode, SubjectEdge, SubjectTaxonomyMetadata
    from sqlalchemy.orm import Session

try:
    from lcc_database_schema import LCCDatabaseManager, SubjectNode, SubjectEdge, SubjectTaxonomyMetadata
    from sqlalchemy.orm import Session
    from sqlalchemy import and_, or_
    _DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Database dependencies not available: {e}")
    print("HINT: Run: pip install -r requirements.txt")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LCCETLProcessor:
    """
    ETL processor for LCC taxonomy data.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize ETL processor.
        
        Args:
            database_url: PostgreSQL connection string
        """
        self.db_manager = LCCDatabaseManager(database_url)
        self.processed_nodes = {}
        self.processed_edges = {}
        self.stats = {
            'nodes_processed': 0,
            'nodes_inserted': 0,
            'nodes_updated': 0,
            'edges_processed': 0,
            'edges_inserted': 0,
            'validation_errors': 0
        }
    
    def validate_class_code(self, class_code: str) -> bool:
        """
        Validate LCC class code format.
        
        Args:
            class_code: The class code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not class_code or not isinstance(class_code, str):
            return False
        
        # Valid patterns:
        # - Single letter: A, B, C
        # - Letter + number: A1, B23
        # - Letter + range: A1-100, B23-45
        # - Letter + decimal: A1.5, B23.456
        # - Complex: QA76.9.A25
        
        patterns = [
            r'^[A-Z]+$',                          # Single letter(s)
            r'^[A-Z]+[0-9]+$',                    # Letter + number
            r'^[A-Z]+[0-9]+-[0-9]+$',             # Letter + range
            r'^[A-Z]+[0-9]+\.[0-9]+$',            # Letter + decimal
            r'^[A-Z]+[0-9]+\.[0-9]+\.[A-Z][0-9]*$'  # Complex decimal
        ]
        
        return any(re.match(pattern, class_code.strip()) for pattern in patterns)
    
    def extract_numeric_range(self, class_code: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Extract numeric range from class code for sorting and hierarchy.
        
        Args:
            class_code: LCC class code
            
        Returns:
            Tuple of (start, end) numeric values
        """
        try:
            # Handle range format: A100-200
            if '-' in class_code:
                parts = class_code.split('-')
                if len(parts) == 2:
                    start_match = re.search(r'(\d+(?:\.\d+)?)$', parts[0])
                    end_match = re.search(r'^(\d+(?:\.\d+)?)', parts[1])
                    
                    if start_match and end_match:
                        return float(start_match.group(1)), float(end_match.group(1))
            
            # Handle decimal format: A123.45
            elif '.' in class_code:
                match = re.search(r'(\d+\.\d+)', class_code)
                if match:
                    value = float(match.group(1))
                    return value, value
            
            # Handle simple number: A123
            else:
                match = re.search(r'(\d+)', class_code)
                if match:
                    value = float(match.group(1))
                    return value, value
        
        except (ValueError, AttributeError):
            pass
        
        return None, None
    
    def determine_hierarchy_level(self, class_code: str, parent_code: str) -> int:
        """
        Determine hierarchy level based on class code structure and parent.
        
        Args:
            class_code: The class code to analyze
            parent_code: The parent class code
            
        Returns:
            Hierarchy level (0 = top level)
        """
        if not parent_code:
            return 0
        
        # Count the depth based on structure
        if '.' in class_code:
            # Decimal notation increases level
            return class_code.count('.') + 1
        
        # Range notation typically at level 1
        if '-' in class_code:
            return 1
        
        # Default based on length and complexity
        if len(class_code) <= 2:
            return 0
        elif len(class_code) <= 5:
            return 1
        else:
            return 2
    
    def normalize_parent_code(self, class_code: str) -> str:
        """
        Normalize and determine parent code from class code structure.
        
        Args:
            class_code: The class code to find parent for
            
        Returns:
            Parent class code or empty string
        """
        if not class_code:
            return ""
        
        # For decimal notation: QA76.9.A25 -> QA76.9
        if '.' in class_code:
            parts = class_code.split('.')
            if len(parts) > 1:
                return '.'.join(parts[:-1])
        
        # For range notation: A100-200 -> A
        if '-' in class_code:
            match = re.match(r'^([A-Z]+)', class_code)
            return match.group(1) if match else ""
        
        # For simple codes: A123 -> A (if A123 has more than just letter)
        match = re.match(r'^([A-Z]+)', class_code)
        if match:
            letter_part = match.group(1)
            if len(class_code) > len(letter_part):
                return letter_part
        
        return ""
    
    def transform_node_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw parsed data into normalized node format.
        
        Args:
            raw_data: Raw data from file parser
            
        Returns:
            Normalized node data
        """
        class_code = raw_data.get('class_code', '').strip()
        label = raw_data.get('label', '').strip()
        
        # Validate required fields
        if not self.validate_class_code(class_code):
            raise ValueError(f"Invalid class code: {class_code}")
        
        if not label:
            raise ValueError(f"Missing label for class code: {class_code}")
        
        # Normalize parent code
        parent_code = raw_data.get('parent_code', '').strip()
        if not parent_code:
            parent_code = self.normalize_parent_code(class_code)
        
        # Extract numeric range
        range_start, range_end = self.extract_numeric_range(class_code)
        
        # Determine hierarchy level
        level = raw_data.get('level', 0)
        if level == 0:  # Recalculate if not provided
            level = self.determine_hierarchy_level(class_code, parent_code)
        
        # Create normalized node data
        node_data = {
            'class_code': class_code,
            'label': label,
            'parent_code': parent_code if parent_code else None,
            'description': label,  # Use label as description for now
            'range_start': range_start,
            'range_end': range_end,
            'hierarchy_level': level,
            'source_file': raw_data.get('source_file', ''),
            'extra': {
                'raw_data': raw_data,
                'import_timestamp': datetime.now().isoformat()
            }
        }
        
        return node_data
    
    def load_consolidated_data(self, data_file: str = "consolidated_lcc_data.json") -> List[Dict[str, Any]]:
        """
        Load and validate consolidated LCC data from JSON file.
        
        Args:
            data_file: Path to consolidated JSON data file
            
        Returns:
            List of validated node data
        """
        file_path = Path(data_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Consolidated data file not found: {data_file}")
        
        logger.info(f"Loading consolidated data from: {data_file}")
        
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
        
        logger.info(f"Loaded {len(raw_data)} raw entries")
        
        # Transform and validate data
        validated_nodes = []
        errors = []
        
        for i, raw_entry in enumerate(raw_data):
            try:
                normalized = self.transform_node_data(raw_entry)
                validated_nodes.append(normalized)
            except Exception as e:
                error_msg = f"Entry {i}: {e}"
                errors.append(error_msg)
                logger.warning(error_msg)
                self.stats['validation_errors'] += 1
        
        logger.info(f"Validated {len(validated_nodes)} entries, {len(errors)} errors")
        
        if errors:
            logger.warning(f"Validation errors encountered:")
            for error in errors[:10]:  # Show first 10 errors
                logger.warning(f"  {error}")
        
        return validated_nodes
    
    def upsert_node(self, session, node_data: Dict[str, Any]) -> Tuple[Any, bool]:
        """
        Insert or update a subject node.
        
        Args:
            session: Database session
            node_data: Normalized node data
            
        Returns:
            Tuple of (node, was_created)
        """
        class_code = node_data['class_code']
        
        # Check if node exists
        existing_node = session.query(SubjectNode).filter(
            SubjectNode.class_code == class_code
        ).first()
        
        if existing_node:
            # Update existing node
            for key, value in node_data.items():
                if hasattr(existing_node, key):
                    setattr(existing_node, key, value)
            
            self.stats['nodes_updated'] += 1
            return existing_node, False
        else:
            # Create new node
            new_node = SubjectNode(**node_data)
            session.add(new_node)
            
            self.stats['nodes_inserted'] += 1
            return new_node, True
    
    def create_hierarchy_edges(self, session, nodes: List[Dict[str, Any]]):
        """
        Create hierarchy edges between parent and child nodes.
        
        Args:
            session: Database session
            nodes: List of node data
        """
        logger.info("Creating hierarchy edges...")
        
        # Group nodes by parent
        children_by_parent = {}
        for node in nodes:
            parent_code = node.get('parent_code')
            if parent_code:
                if parent_code not in children_by_parent:
                    children_by_parent[parent_code] = []
                children_by_parent[parent_code].append(node['class_code'])
        
        # Create edges
        for parent_code, child_codes in children_by_parent.items():
            # Verify parent exists
            parent_exists = session.query(SubjectNode).filter(
                SubjectNode.class_code == parent_code
            ).first()
            
            if not parent_exists:
                logger.warning(f"Parent node not found: {parent_code}")
                continue
            
            for child_code in child_codes:
                # Check if edge already exists
                existing_edge = session.query(SubjectEdge).filter(
                    and_(
                        SubjectEdge.parent_code == parent_code,
                        SubjectEdge.child_code == child_code,
                        SubjectEdge.relationship == 'broader'
                    )
                ).first()
                
                if not existing_edge:
                    edge = SubjectEdge(
                        parent_code=parent_code,
                        child_code=child_code,
                        relationship='broader',
                        source='lcc_etl',
                        extra={'created_by': 'etl_processor'}
                    )
                    session.add(edge)
                    self.stats['edges_inserted'] += 1
                
                self.stats['edges_processed'] += 1
    
    def create_taxonomy_metadata(self, session, version: str, config: Dict[str, Any]):
        """
        Create taxonomy metadata record.
        
        Args:
            session: Database session
            version: Import version identifier
            config: Import configuration and statistics
        """
        # Check if version already exists
        existing = session.query(SubjectTaxonomyMetadata).filter(
            SubjectTaxonomyMetadata.version == version
        ).first()
        
        if existing:
            # Update existing
            existing.import_config = config
            existing.total_nodes = self.stats['nodes_inserted'] + self.stats['nodes_updated']
            existing.total_edges = self.stats['edges_inserted']
            existing.import_status = 'active'
        else:
            # Create new
            metadata = SubjectTaxonomyMetadata(
                version=version,
                source_description=f"LCC taxonomy import from consolidated data",
                total_nodes=self.stats['nodes_inserted'] + self.stats['nodes_updated'],
                total_edges=self.stats['edges_inserted'],
                import_config=config,
                import_status='active'
            )
            session.add(metadata)
    
    def run_etl(self, data_file: str = "consolidated_lcc_data.json", 
                version: Optional[str] = None, 
                batch_size: int = 1000) -> Dict[str, Any]:
        """
        Run the complete ETL process.
        
        Args:
            data_file: Path to consolidated data file
            version: Import version (defaults to timestamp)
            batch_size: Number of records to process in each batch
            
        Returns:
            ETL results and statistics
        """
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"🚀 Starting LCC ETL process (version: {version})")
        start_time = datetime.now()
        
        try:
            # Load and validate data
            validated_nodes = self.load_consolidated_data(data_file)
            
            # Process in batches
            with self.db_manager.get_session() as session:
                logger.info(f"📥 Processing {len(validated_nodes)} nodes in batches of {batch_size}")
                
                for i in range(0, len(validated_nodes), batch_size):
                    batch = validated_nodes[i:i+batch_size]
                    
                    logger.info(f"Processing batch {i//batch_size + 1}/{(len(validated_nodes)-1)//batch_size + 1}")
                    
                    # Upsert nodes
                    for node_data in batch:
                        try:
                            self.upsert_node(session, node_data)
                            self.stats['nodes_processed'] += 1
                        except Exception as e:
                            logger.error(f"Error processing node {node_data.get('class_code')}: {e}")
                    
                    # Commit batch
                    session.commit()
                
                # Create hierarchy edges
                self.create_hierarchy_edges(session, validated_nodes)
                session.commit()
                
                # Create metadata
                config = {
                    'data_file': data_file,
                    'batch_size': batch_size,
                    'etl_stats': self.stats,
                    'processing_time_seconds': (datetime.now() - start_time).total_seconds()
                }
                self.create_taxonomy_metadata(session, version, config)
                session.commit()
            
            # Final statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results = {
                'version': version,
                'status': 'success',
                'duration_seconds': duration,
                'statistics': self.stats,
                'database_stats': self.db_manager.get_statistics()
            }
            
            logger.info(f"✅ ETL completed successfully in {duration:.2f} seconds")
            logger.info(f"📊 Final statistics: {self.stats}")
            
            return results
        
        except Exception as e:
            logger.error(f"❌ ETL failed: {e}")
            raise

def main():
    """
    Main ETL execution function.
    """
    print("📚 LCC Taxonomy ETL Processor")
    print("=" * 50)
    
    try:
        # Initialize ETL processor
        etl = LCCETLProcessor()
        
        # Ensure database schema exists
        etl.db_manager.create_tables()
        
        # Run ETL process
        results = etl.run_etl()
        
        print("\n🎉 ETL Process Completed Successfully!")
        print(f"📊 Results:")
        for key, value in results.items():
            if key != 'database_stats':
                print(f"  {key}: {value}")
        
        print(f"\n📈 Database Statistics:")
        for key, value in results['database_stats'].items():
            print(f"  {key}: {value}")
        
        return results
        
    except Exception as e:
        print(f"❌ ETL process failed: {e}")
        print("💡 Make sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database connection is configured")
        print("  3. consolidated_lcc_data.json exists")
        return None

if __name__ == "__main__":
    results = main()