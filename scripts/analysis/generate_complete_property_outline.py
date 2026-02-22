#!/usr/bin/env python3
"""
Generate Complete Property Outline

For each QID in the taxonomy, show:
- QID and label
- ALL properties with number, label, and values
- Hierarchical outline format
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class PropertyOutlineGenerator:
    """Generate complete property outline from taxonomy JSON"""
    
    def __init__(self, json_filepath: str):
        self.json_path = Path(json_filepath)
        self.data = None
        self.outline_lines = []
        
    def load_json(self):
        """Load taxonomy JSON"""
        
        print(f"Loading: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        entities = self.data.get('entities', {})
        print(f"  Loaded {len(entities)} entities\n")
        
        return entities
    
    def generate_outline(self):
        """Generate complete property outline"""
        
        print(f"Generating property outline...\n")
        
        entities = self.data.get('entities', {})
        root_qid = self.data.get('root_qid')
        
        # Sort entities: root first, then alphabetically
        sorted_qids = sorted(entities.keys())
        if root_qid in sorted_qids:
            sorted_qids.remove(root_qid)
            sorted_qids.insert(0, root_qid)
        
        # Generate outline for each entity
        for i, qid in enumerate(sorted_qids):
            entity = entities[qid]
            self._generate_entity_outline(qid, entity, is_root=(qid == root_qid))
            
            # Progress
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(sorted_qids)} entities")
        
        print(f"  Completed all {len(sorted_qids)} entities\n")
    
    def _generate_entity_outline(self, qid: str, entity: dict, is_root: bool = False):
        """Generate outline for a single entity"""
        
        label = entity.get('label', qid)
        description = entity.get('description', 'No description')
        stats = entity.get('statistics', {})
        total_props = stats.get('total_properties', 0)
        
        # Entity header
        marker = "*** ROOT ***" if is_root else ""
        self.outline_lines.append("=" * 80)
        self.outline_lines.append(f"{qid} - {label} {marker}")
        self.outline_lines.append("=" * 80)
        self.outline_lines.append(f"Description: {description}")
        self.outline_lines.append(f"Total Properties: {total_props}")
        self.outline_lines.append("")
        
        # Get all claims with labels
        claims = entity.get('claims_with_labels', {})
        
        if not claims:
            self.outline_lines.append("  (No properties)")
            self.outline_lines.append("")
            return
        
        # Sort properties alphabetically
        sorted_props = sorted(claims.items())
        
        # Generate outline for each property
        for prop_id, prop_data in sorted_props:
            prop_label = prop_data.get('property_label', prop_id)
            statements = prop_data.get('statements', [])
            
            # Property header
            self.outline_lines.append(f"{prop_id} ({prop_label})")
            self.outline_lines.append("-" * 80)
            
            if not statements:
                self.outline_lines.append("  (No values)")
                self.outline_lines.append("")
                continue
            
            # Show all values
            for j, stmt in enumerate(statements, 1):
                value = stmt.get('value')
                value_label = stmt.get('value_label', '')
                rank = stmt.get('rank', 'normal')
                
                # Format value with label
                if value_label and value_label != value:
                    value_display = f"{value} ({value_label})"
                else:
                    value_display = str(value)
                
                # Truncate if too long
                if len(value_display) > 100:
                    value_display = value_display[:97] + "..."
                
                self.outline_lines.append(f"  [{j}] {value_display}")
                
                if rank != 'normal':
                    self.outline_lines.append(f"      Rank: {rank}")
                
                # Show qualifiers if any
                qualifiers = stmt.get('qualifiers_with_labels', {})
                if qualifiers:
                    self.outline_lines.append(f"      Qualifiers:")
                    for qual_prop, qual_data in list(qualifiers.items())[:3]:  # Show first 3
                        qual_label = qual_data.get('property_label', qual_prop)
                        qual_values = qual_data.get('values', [])
                        
                        for qual_val in qual_values[:2]:  # Show first 2 values
                            val = qual_val.get('value')
                            val_label = qual_val.get('label', '')
                            
                            if val_label and val_label != val:
                                self.outline_lines.append(f"        - {qual_prop} ({qual_label}): {val} ({val_label})")
                            else:
                                self.outline_lines.append(f"        - {qual_prop} ({qual_label}): {val}")
            
            self.outline_lines.append("")
    
    def save_outline(self, output_filename: str = None):
        """Save outline to text file"""
        
        if not output_filename:
            root_qid = self.data.get('root_qid', 'unknown')
            output_filename = f"output/outlines/{root_qid}_complete_property_outline.txt"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.outline_lines))
        
        file_size = output_path.stat().st_size / 1024
        
        print(f"Outline saved: {output_path}")
        print(f"  Lines: {len(self.outline_lines):,}")
        print(f"  Size: {file_size:.1f} KB")
        
        return str(output_path)
    
    def run_full_generation(self):
        """Run complete generation pipeline"""
        
        print(f"\n{'='*80}")
        print(f"COMPLETE PROPERTY OUTLINE GENERATOR")
        print(f"{'='*80}\n")
        
        # Load JSON
        entities = self.load_json()
        
        # Generate outline
        self.generate_outline()
        
        # Save
        outline_path = self.save_outline()
        
        print(f"\n{'='*80}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*80}\n")
        print(f"File: {outline_path}")
        print(f"Entities: {len(entities)}")
        print(f"Lines: {len(self.outline_lines):,}")
        
        return outline_path


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "output/taxonomy_recursive/Q17167_recursive_20260220_135756.json"
    
    generator = PropertyOutlineGenerator(json_file)
    generator.run_full_generation()


if __name__ == "__main__":
    main()
