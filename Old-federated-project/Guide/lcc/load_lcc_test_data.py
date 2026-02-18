"""
Simple LCC Data Loader
======================

Loads LCC data from consolidated_lcc_data.json into the database for testing.
"""

import json
from enhanced_taxonomy_manager import EnhancedTaxonomyManager
from lcc_database_schema import SubjectNode

def load_lcc_data():
    """Load LCC data into the database."""
    print("Loading LCC data for testing...")
    
    # Initialize database
    db = EnhancedTaxonomyManager()
    db.create_tables()
    
    # Load consolidated data
    with open('consolidated_lcc_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data)} LCC entries")
    
    # Load subset for testing
    session = db.get_session()
    loaded_count = 0
    
    for item in data[:50]:  # Load first 50 for testing
        try:
            node = SubjectNode(
                class_code=item['class_code'],
                label=item['label'],
                parent_code=item.get('parent_code'),
                hierarchy_level=item.get('level', 0),
                source_file=item.get('source_file', 'consolidated')
            )
            session.add(node)
            loaded_count += 1
        except Exception as e:
            print(f"Error loading {item['class_code']}: {e}")
    
    session.commit()
    session.close()
    
    print(f"Loaded {loaded_count} LCC entries for testing")

if __name__ == "__main__":
    load_lcc_data()