#!/usr/bin/env python3
"""
Convert Taxonomy JSON to Mermaid Diagram - FILTERED BY DENSITY

Keeps all 5 hops but filters based on property density:
- Include entities with many properties (>10)
- Include all direct parents and children of root
- Include academic/field of study entities
- This naturally reduces edges while keeping important structure
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TaxonomyMermaidFiltered:
    """Generate filtered Mermaid diagram based on entity density"""
    
    def __init__(self, json_filepath: str, min_properties: int = 10):
        self.json_path = Path(json_filepath)
        self.min_properties = min_properties
        self.data = None
        self.entities = {}
        self.filtered_entities = set()
        self.mermaid_lines = []
        
    def load_json(self):
        """Load taxonomy JSON"""
        
        print(f"\n{'='*80}")
        print(f"LOADING TAXONOMY DATA")
        print(f"{'='*80}\n")
        
        print(f"Reading: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.entities = self.data.get('entities', {})
        print(f"  Loaded {len(self.entities)} entities")
        
    def filter_by_density(self):
        """Filter entities by property density"""
        
        print(f"\n{'='*80}")
        print(f"FILTERING BY DENSITY")
        print(f"{'='*80}\n")
        
        print(f"Minimum properties: {self.min_properties}")
        
        root_qid = self.data.get('root_qid')
        
        # Always include root
        self.filtered_entities.add(root_qid)
        
        # Get direct parents and children (hop 1)
        upward_rels = self.data.get('relationships', {}).get('upward', [])
        downward_rels = self.data.get('relationships', {}).get('downward', [])
        succession_rels = self.data.get('relationships', {}).get('succession', [])
        
        # Always include hop 1 parents
        for rel in upward_rels:
            if rel['from_qid'] == root_qid and rel['hop'] == 1:
                self.filtered_entities.add(rel['to_qid'])
        
        # Always include all children
        for rel in downward_rels:
            self.filtered_entities.add(rel['from_qid'])
            self.filtered_entities.add(rel['to_qid'])
        
        # Always include succession
        for rel in succession_rels:
            self.filtered_entities.add(rel['from_qid'])
            self.filtered_entities.add(rel['to_qid'])
        
        print(f"  Always included (root + hop 1 + succession): {len(self.filtered_entities)}")
        
        # Add high-density entities
        for qid, entity in self.entities.items():
            props = entity.get('statistics', {}).get('total_properties', 0)
            label = entity.get('label', '').lower()
            
            # Include if:
            # 1. Has many properties
            if props >= self.min_properties:
                self.filtered_entities.add(qid)
            
            # 2. Is academic/field concept (even if few properties)
            elif any(term in label for term in [
                'field of study', 'academic', 'science', 'discipline',
                'knowledge', 'civilization', 'culture', 'society'
            ]):
                self.filtered_entities.add(qid)
        
        print(f"  Total filtered entities: {len(self.filtered_entities)}")
        print(f"  Removed: {len(self.entities) - len(self.filtered_entities)}")
        
        # Show what we're keeping
        print(f"\n  Keeping entities like:")
        for qid in list(self.filtered_entities)[:10]:
            entity = self.entities[qid]
            label = entity['label']
            props = entity.get('statistics', {}).get('total_properties', 0)
            print(f"    {qid} - {label} ({props} props)")
        print(f"    ... and {len(self.filtered_entities) - 10} more")
        
    def generate_mermaid(self):
        """Generate Mermaid diagram with filtered entities"""
        
        print(f"\n{'='*80}")
        print(f"GENERATING MERMAID DIAGRAM")
        print(f"{'='*80}\n")
        
        # Start Mermaid graph
        self.mermaid_lines.append("graph TB")
        self.mermaid_lines.append("")
        self.mermaid_lines.append("%% Root Entity")
        
        root_qid = self.data.get('root_qid')
        root_label = self.data.get('root_label', root_qid)
        
        # Define root node
        self.mermaid_lines.append(f'{root_qid}["{root_label}<br/>{root_qid}"]')
        self.mermaid_lines.append(f"style {root_qid} fill:#ff6b6b,stroke:#c92a2a,stroke-width:4px,color:#fff")
        self.mermaid_lines.append("")
        
        # Define filtered entities
        self.mermaid_lines.append("%% Entity Definitions")
        for qid in sorted(self.filtered_entities):
            if qid != root_qid and qid in self.entities:
                entity = self.entities[qid]
                label = entity.get('label', qid)
                props = entity.get('statistics', {}).get('total_properties', 0)
                
                # Clean label and add property count
                clean_label = label.replace('"', "'")[:25]
                self.mermaid_lines.append(f'{qid}["{clean_label}<br/>{qid}<br/>({props}p)"]')
        
        self.mermaid_lines.append("")
        
        # Filter relationships
        filtered_upward = []
        filtered_downward = []
        filtered_succession = []
        
        # Upward relationships (only if both entities are in filtered set)
        upward_rels = self.data.get('relationships', {}).get('upward', [])
        for rel in upward_rels:
            if rel['from_qid'] in self.filtered_entities and rel['to_qid'] in self.filtered_entities:
                filtered_upward.append(rel)
        
        # Downward relationships
        downward_rels = self.data.get('relationships', {}).get('downward', [])
        for rel in downward_rels:
            if rel['from_qid'] in self.filtered_entities and rel['to_qid'] in self.filtered_entities:
                filtered_downward.append(rel)
        
        # Succession relationships
        succession_rels = self.data.get('relationships', {}).get('succession', [])
        for rel in succession_rels:
            if rel['from_qid'] in self.filtered_entities and rel['to_qid'] in self.filtered_entities:
                filtered_succession.append(rel)
        
        total_edges = len(filtered_upward) + len(filtered_downward) + len(filtered_succession)
        
        print(f"  Filtered relationships:")
        print(f"    Upward: {len(filtered_upward)} (from {len(upward_rels)})")
        print(f"    Downward: {len(filtered_downward)} (from {len(downward_rels)})")
        print(f"    Succession: {len(filtered_succession)} (from {len(succession_rels)})")
        print(f"    TOTAL EDGES: {total_edges}")
        
        if total_edges > 500:
            print(f"\n  WARNING: Still {total_edges} edges (limit is 500)")
            print(f"  Further filtering needed...")
        
        # Add relationships
        self.mermaid_lines.append("%% Upward Relationships (Parents)")
        for rel in filtered_upward:
            from_qid = rel['from_qid']
            to_qid = rel['to_qid']
            prop_label = rel['property_label'][:20]  # Limit label length
            
            self.mermaid_lines.append(f"{from_qid} -->|{prop_label}| {to_qid}")
        
        self.mermaid_lines.append("")
        self.mermaid_lines.append("%% Downward Relationships (Children)")
        for rel in filtered_downward:
            from_qid = rel['from_qid']
            to_qid = rel['to_qid']
            prop_label = rel['property_label'][:20]
            
            self.mermaid_lines.append(f"{from_qid} -.->|{prop_label}| {to_qid}")
        
        self.mermaid_lines.append("")
        self.mermaid_lines.append("%% Succession (Timeline)")
        for rel in filtered_succession:
            from_qid = rel['from_qid']
            to_qid = rel['to_qid']
            prop_label = rel['property_label'][:20]
            
            self.mermaid_lines.append(f"{from_qid} ==>|{prop_label}| {to_qid}")
        
        self.mermaid_lines.append("")
        
        # Add styling
        self.mermaid_lines.append("%% Styling by Category")
        self._add_styling(root_qid)
        
        return total_edges
    
    def _add_styling(self, root_qid: str):
        """Add color styling"""
        
        concrete = []
        academic = []
        temporal = []
        cultural = []
        political = []
        
        for qid in self.filtered_entities:
            if qid == root_qid or qid not in self.entities:
                continue
            
            entity = self.entities[qid]
            label = entity.get('label', '').lower()
            
            if any(term in label for term in ['republic', 'empire', 'kingdom', 'rome']):
                concrete.append(qid)
            elif any(term in label for term in ['field', 'science', 'knowledge', 'academic', 'study']):
                academic.append(qid)
            elif any(term in label for term in ['period', 'era', 'time', 'interval']):
                temporal.append(qid)
            elif any(term in label for term in ['culture', 'civilization', 'society']):
                cultural.append(qid)
            elif any(term in label for term in ['government', 'political', 'state', 'country']):
                political.append(qid)
        
        if concrete:
            self.mermaid_lines.append(f"classDef historical fill:#4dabf7,stroke:#1971c2,stroke-width:2px")
            self.mermaid_lines.append(f"class {','.join(concrete)} historical")
        
        if academic:
            self.mermaid_lines.append(f"classDef academic fill:#51cf66,stroke:#2f9e44,stroke-width:2px")
            self.mermaid_lines.append(f"class {','.join(academic)} academic")
        
        if temporal:
            self.mermaid_lines.append(f"classDef temporal fill:#ffd43b,stroke:#fab005,stroke-width:2px")
            self.mermaid_lines.append(f"class {','.join(temporal)} temporal")
        
        if cultural:
            self.mermaid_lines.append(f"classDef cultural fill:#da77f2,stroke:#9c36b5,stroke-width:2px")
            self.mermaid_lines.append(f"class {','.join(cultural)} cultural")
        
        if political:
            self.mermaid_lines.append(f"classDef political fill:#ffa94d,stroke:#fd7e14,stroke-width:2px")
            self.mermaid_lines.append(f"class {','.join(political)} political")
    
    def save_mermaid(self, output_filename: str = None):
        """Save Mermaid to file"""
        
        if not output_filename:
            root_qid = self.data.get('root_qid', 'unknown')
            output_filename = f"output/mermaid/{root_qid}_filtered_taxonomy.mmd"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.mermaid_lines))
        
        print(f"\nMermaid saved: {output_path}")
        print(f"  Lines: {len(self.mermaid_lines)}")
        
        return str(output_path)
    
    def save_markdown(self, output_filename: str = None):
        """Save as Markdown with embedded Mermaid"""
        
        if not output_filename:
            root_qid = self.data.get('root_qid', 'unknown')
            output_filename = f"output/mermaid/{root_qid}_filtered_taxonomy.md"
        
        output_path = Path(output_filename)
        
        root_qid = self.data.get('root_qid')
        root_label = self.data.get('root_label')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 5-Hop Taxonomy (Filtered by Density): {root_label}\n\n")
            f.write(f"**Root:** {root_qid} ({root_label})\n")
            f.write(f"**Filter:** Entities with ≥{self.min_properties} properties\n")
            f.write(f"**Entities shown:** {len(self.filtered_entities)} (of {len(self.entities)} total)\n\n")
            f.write(f"---\n\n")
            f.write(f"## Taxonomy Diagram\n\n")
            f.write(f"```mermaid\n")
            f.write('\n'.join(self.mermaid_lines))
            f.write(f"\n```\n\n")
            f.write(f"---\n\n")
            f.write(f"## Legend\n\n")
            f.write(f"**Colors:**\n")
            f.write(f"- 🔴 **Red:** Root entity ({root_label})\n")
            f.write(f"- 🔵 **Blue:** Historical entities (republics, empires, kingdoms)\n")
            f.write(f"- 🟢 **Green:** Academic/knowledge entities (field of study, science)\n")
            f.write(f"- 🟡 **Yellow:** Temporal concepts (period, era, time)\n")
            f.write(f"- 🟣 **Purple:** Cultural concepts (civilization, culture, society)\n")
            f.write(f"- 🟠 **Orange:** Political concepts (government, state, country)\n\n")
            f.write(f"**Arrows:**\n")
            f.write(f"- Solid `-->` : Upward hierarchy (instance of, part of, subclass of)\n")
            f.write(f"- Dotted `-.->` : Downward hierarchy (has parts, contains)\n")
            f.write(f"- Thick `==>` : Succession timeline (follows, followed by)\n\n")
            f.write(f"**Node Labels:**\n")
            f.write(f"- Format: `Label` `QID` `(#p)` where # is property count\n")
            f.write(f"- Higher property count = more data-rich entity\n")
        
        print(f"Markdown saved: {output_path}")
        
        return str(output_path)
    
    def run_full_generation(self):
        """Run complete generation pipeline"""
        
        print(f"\n{'='*80}")
        print(f"FILTERED TAXONOMY TO MERMAID")
        print(f"{'='*80}")
        
        # Load JSON
        self.load_json()
        
        # Filter by density
        self.filter_by_density()
        
        # Generate Mermaid
        total_edges = self.generate_mermaid()
        
        # Save files
        mermaid_path = self.save_mermaid()
        markdown_path = self.save_markdown()
        
        print(f"\n{'='*80}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*80}\n")
        print(f"Entities: {len(self.filtered_entities)} (filtered from {len(self.entities)})")
        print(f"Edges: {total_edges}")
        print(f"Status: {'OK' if total_edges <= 500 else 'STILL TOO LARGE'}")
        print(f"\nFiles:")
        print(f"  {mermaid_path}")
        print(f"  {markdown_path}")
        
        return markdown_path


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "output/taxonomy_recursive/Q17167_recursive_20260220_135756.json"
    
    # Start with min_properties = 10
    min_props = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    generator = TaxonomyMermaidFiltered(json_file, min_properties=min_props)
    generator.run_full_generation()


if __name__ == "__main__":
    main()
