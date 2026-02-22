#!/usr/bin/env python3
"""
Convert Taxonomy JSON to CSV

Creates a wide-format CSV where:
- Each row = one QID (entity)
- Each column = one property
- Values include labels (not just QIDs)

Output: initial-qid-subject-analysis.csv
"""

import sys
from pathlib import Path
import json
import csv
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TaxonomyToCSV:
    """Convert taxonomy JSON to wide-format CSV"""
    
    def __init__(self, json_filepath: str):
        """
        Initialize converter
        
        Args:
            json_filepath: Path to taxonomy JSON file
        """
        self.json_path = Path(json_filepath)
        self.data = None
        self.all_properties = set()
        self.entity_data = {}
        
    def load_json(self):
        """Load taxonomy JSON"""
        
        print(f"\n{'='*80}")
        print(f"LOADING TAXONOMY DATA")
        print(f"{'='*80}\n")
        
        print(f"Reading: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        entities = self.data.get('entities', {})
        print(f"  Loaded {len(entities)} entities")
        
        return self.data
    
    def extract_entity_properties(self):
        """Extract all properties for all entities"""
        
        print(f"\n{'='*80}")
        print(f"EXTRACTING PROPERTIES")
        print(f"{'='*80}\n")
        
        entities = self.data.get('entities', {})
        
        for qid, entity in entities.items():
            # Initialize entity row
            self.entity_data[qid] = {
                'qid': qid,
                'label': entity.get('label', qid),
                'description': entity.get('description', ''),
                'total_properties': entity.get('statistics', {}).get('total_properties', 0)
            }
            
            # Extract all claims
            claims = entity.get('claims_with_labels', {})
            
            for prop_id, prop_data in claims.items():
                prop_label = prop_data.get('property_label', prop_id)
                
                # Track unique property
                self.all_properties.add((prop_id, prop_label))
                
                # Get all values for this property
                statements = prop_data.get('statements', [])
                
                values = []
                for stmt in statements:
                    value = stmt.get('value')
                    value_label = stmt.get('value_label')
                    
                    # Format value with label if available
                    if value_label and value_label != value:
                        values.append(f"{value} ({value_label})")
                    else:
                        values.append(str(value))
                
                # Join multiple values with " | "
                combined_value = " | ".join(values) if values else ""
                
                # Store in entity data
                column_name = f"{prop_id}_{prop_label}"
                self.entity_data[qid][column_name] = combined_value
        
        print(f"Extracted properties from {len(self.entity_data)} entities")
        print(f"Found {len(self.all_properties)} unique properties")
        
        # Show sample properties
        print(f"\nSample properties (first 10):")
        for i, (prop_id, prop_label) in enumerate(sorted(self.all_properties)[:10]):
            print(f"  {prop_id} - {prop_label}")
        
        print(f"  ... and {len(self.all_properties) - 10} more")
    
    def create_csv(self, output_filename: str = None):
        """Create wide-format CSV"""
        
        if not output_filename:
            root_qid = self.data.get('root_qid', 'unknown')
            output_filename = f"output/csv/{root_qid}_initial-qid-subject-analysis.csv"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*80}")
        print(f"CREATING CSV")
        print(f"{'='*80}\n")
        
        print(f"Output: {output_path}")
        
        # Sort properties for consistent column order
        sorted_properties = sorted(self.all_properties)
        
        # Define columns
        columns = ['qid', 'label', 'description', 'total_properties']
        
        # Add property columns
        for prop_id, prop_label in sorted_properties:
            columns.append(f"{prop_id}_{prop_label}")
        
        print(f"  Columns: {len(columns)}")
        print(f"  Rows: {len(self.entity_data)}")
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
            
            # Write header
            writer.writeheader()
            
            # Write entity rows
            for qid in sorted(self.entity_data.keys()):
                row = self.entity_data[qid]
                writer.writerow(row)
        
        print(f"\n  SUCCESS! CSV created")
        print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
        
        return str(output_path)
    
    def print_preview(self, num_rows: int = 5, num_cols: int = 10):
        """Print a preview of the CSV data"""
        
        print(f"\n{'='*80}")
        print(f"CSV PREVIEW (First {num_rows} rows, first {num_cols} properties)")
        print(f"{'='*80}\n")
        
        # Get first N entities
        entities = list(sorted(self.entity_data.keys()))[:num_rows]
        
        # Get first N properties
        properties = sorted(self.all_properties)[:num_cols]
        
        # Print header
        print(f"{'QID':<15} {'Label':<30} | Properties...")
        print(f"{'-'*80}")
        
        # Print rows
        for qid in entities:
            entity = self.entity_data[qid]
            label = entity['label'][:28] if len(entity['label']) > 28 else entity['label']
            
            print(f"{qid:<15} {label:<30}")
            
            # Show first few property values
            for i, (prop_id, prop_label) in enumerate(properties[:3]):
                col_name = f"{prop_id}_{prop_label}"
                value = entity.get(col_name, '')
                if value:
                    display_val = value[:60] if len(value) > 60 else value
                    print(f"  {prop_id} ({prop_label}): {display_val}")
            
            print()
        
        print(f"{'-'*80}")
        print(f"... {len(self.entity_data) - num_rows} more rows")
        print(f"... {len(self.all_properties) - num_cols} more property columns")
        print()
    
    def generate_csv_summary(self):
        """Generate summary statistics about the CSV"""
        
        print(f"\n{'='*80}")
        print(f"CSV SUMMARY")
        print(f"{'='*80}\n")
        
        # Count non-empty cells per property
        property_usage = defaultdict(int)
        
        for qid, entity in self.entity_data.items():
            for prop_id, prop_label in self.all_properties:
                col_name = f"{prop_id}_{prop_label}"
                if entity.get(col_name):
                    property_usage[(prop_id, prop_label)] += 1
        
        # Sort by usage
        sorted_usage = sorted(property_usage.items(), key=lambda x: x[1], reverse=True)
        
        print(f"TOP 20 MOST COMMON PROPERTIES (across all entities):\n")
        print(f"{'Property':<15} {'Label':<40} {'Used By':<10}")
        print(f"{'-'*80}")
        
        for (prop_id, prop_label), count in sorted_usage[:20]:
            # Clean label for console output
            clean_label = prop_label.encode('ascii', 'replace').decode('ascii')[:38]
            print(f"{prop_id:<15} {clean_label:<40} {count}/{len(self.entity_data)}")
        
        print(f"\n... and {len(sorted_usage) - 20} more properties")
        
        # Sparsity analysis
        total_cells = len(self.entity_data) * len(self.all_properties)
        filled_cells = sum(property_usage.values())
        sparsity = (1 - filled_cells / total_cells) * 100
        
        print(f"\nSPARSITY ANALYSIS:")
        print(f"  Total possible cells: {total_cells:,}")
        print(f"  Filled cells: {filled_cells:,}")
        print(f"  Empty cells: {total_cells - filled_cells:,}")
        print(f"  Sparsity: {sparsity:.1f}%")
        print(f"  (This is normal - not all entities have all properties)")
        
    def run_full_conversion(self, output_filename: str = None):
        """Run complete conversion pipeline"""
        
        print(f"\n{'='*80}")
        print(f"TAXONOMY TO CSV CONVERTER")
        print(f"{'='*80}")
        
        # Load JSON
        self.load_json()
        
        # Extract properties
        self.extract_entity_properties()
        
        # Generate summary
        self.generate_csv_summary()
        
        # Preview
        self.print_preview()
        
        # Create CSV
        csv_path = self.create_csv(output_filename)
        
        print(f"\n{'='*80}")
        print(f"CONVERSION COMPLETE")
        print(f"{'='*80}\n")
        print(f"CSV file: {csv_path}")
        print(f"Entities: {len(self.entity_data)}")
        print(f"Properties: {len(self.all_properties)}")
        print(f"\nOpen in Excel/Google Sheets for analysis!")
        
        return csv_path


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # Use latest 5-hop file
        json_file = "output/taxonomy_recursive/Q17167_recursive_20260220_135756.json"
    
    converter = TaxonomyToCSV(json_file)
    csv_path = converter.run_full_conversion()
    
    print(f"\n✓ Done! CSV ready for analysis")
    print(f"  File: {csv_path}")


if __name__ == "__main__":
    main()
