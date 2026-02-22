#!/usr/bin/env python3
"""
Convert Taxonomy JSON to Mermaid Diagram

Creates a Mermaid flowchart showing:
- Root entity as hub
- 5-hop hierarchies (up and down)
- All relationships with labels
- Color-coded by hop distance
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TaxonomyMermaidGenerator:
    """Generate Mermaid diagram from taxonomy JSON"""
    
    def __init__(self, json_filepath: str):
        self.json_path = Path(json_filepath)
        self.data = None
        self.entities = {}
        self.mermaid_lines = []
        
    def load_json(self):
        """Load taxonomy JSON"""
        
        print(f"Loading: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.entities = self.data.get('entities', {})
        print(f"  Loaded {len(self.entities)} entities")
        
    def generate_mermaid(self):
        """Generate Mermaid diagram"""
        
        print(f"Generating Mermaid diagram...")
        
        # Start Mermaid graph
        self.mermaid_lines.append("graph TB")
        self.mermaid_lines.append("")
        self.mermaid_lines.append("%% Root Entity")
        
        root_qid = self.data.get('root_qid')
        root_label = self.data.get('root_label', root_qid)
        
        # Define root node (larger, highlighted)
        self.mermaid_lines.append(f"{root_qid}[\"{root_label}<br/>{root_qid}\"]")
        self.mermaid_lines.append(f"style {root_qid} fill:#ff6b6b,stroke:#c92a2a,stroke-width:4px,color:#fff")
        self.mermaid_lines.append("")
        
        # Add all entity definitions
        self.mermaid_lines.append("%% Entity Definitions")
        for qid, entity in self.entities.items():
            if qid != root_qid:
                label = entity.get('label', qid)
                # Clean label for Mermaid (escape quotes, limit length)
                clean_label = label.replace('"', "'")[:30]
                self.mermaid_lines.append(f"{qid}[\"{clean_label}<br/>{qid}\"]")
        
        self.mermaid_lines.append("")
        
        # Add upward relationships
        self.mermaid_lines.append("%% Upward Relationships (Parents)")
        upward_rels = self.data.get('relationships', {}).get('upward', [])
        
        for rel in upward_rels:
            from_qid = rel['from_qid']
            to_qid = rel['to_qid']
            prop_label = rel['property_label']
            hop = rel.get('hop', 0)
            
            # Create edge with label
            self.mermaid_lines.append(f"{from_qid} -->|{prop_label}| {to_qid}")
        
        self.mermaid_lines.append("")
        
        # Add downward relationships
        self.mermaid_lines.append("%% Downward Relationships (Children)")
        downward_rels = self.data.get('relationships', {}).get('downward', [])
        
        for rel in downward_rels:
            from_qid = rel['from_qid']
            to_qid = rel['to_qid']
            prop_label = rel['property_label']
            
            self.mermaid_lines.append(f"{from_qid} -.->|{prop_label}| {to_qid}")
        
        self.mermaid_lines.append("")
        
        # Add succession relationships
        self.mermaid_lines.append("%% Succession (Timeline)")
        succession_rels = self.data.get('relationships', {}).get('succession', [])
        
        for rel in succession_rels:
            from_qid = rel['from_qid']
            to_qid = rel['to_qid']
            prop_label = rel['property_label']
            
            self.mermaid_lines.append(f"{from_qid} ==>|{prop_label}| {to_qid}")
        
        self.mermaid_lines.append("")
        
        # Add styling by entity type
        self.mermaid_lines.append("%% Styling")
        self._add_styling(root_qid)
        
    def _add_styling(self, root_qid: str):
        """Add color styling based on entity characteristics"""
        
        # Group entities by type
        concrete_historical = []
        abstract_concepts = []
        academic = []
        temporal = []
        
        for qid, entity in self.entities.items():
            if qid == root_qid:
                continue
            
            label = entity.get('label', '').lower()
            props = entity.get('statistics', {}).get('total_properties', 0)
            
            # Categorize
            if any(term in label for term in ['republic', 'empire', 'kingdom', 'rome']):
                concrete_historical.append(qid)
            elif any(term in label for term in ['field', 'science', 'study', 'knowledge', 'discipline']):
                academic.append(qid)
            elif any(term in label for term in ['period', 'era', 'time', 'temporal']):
                temporal.append(qid)
            elif props > 30:
                abstract_concepts.append(qid)
        
        # Apply styles
        if concrete_historical:
            qid_list = ','.join(concrete_historical)
            self.mermaid_lines.append(f"classDef historical fill:#4dabf7,stroke:#1971c2,stroke-width:2px")
            self.mermaid_lines.append(f"class {qid_list} historical")
        
        if academic:
            qid_list = ','.join(academic)
            self.mermaid_lines.append(f"classDef academic fill:#51cf66,stroke:#2f9e44,stroke-width:2px")
            self.mermaid_lines.append(f"class {qid_list} academic")
        
        if temporal:
            qid_list = ','.join(temporal)
            self.mermaid_lines.append(f"classDef temporal fill:#ffd43b,stroke:#fab005,stroke-width:2px")
            self.mermaid_lines.append(f"class {qid_list} temporal")
        
        if abstract_concepts:
            qid_list = ','.join(abstract_concepts[:50])  # Limit to avoid too long
            self.mermaid_lines.append(f"classDef abstract fill:#cc5de8,stroke:#9c36b5,stroke-width:2px")
            self.mermaid_lines.append(f"class {qid_list} abstract")
    
    def save_mermaid(self, output_filename: str = None):
        """Save Mermaid diagram to file"""
        
        if not output_filename:
            root_qid = self.data.get('root_qid', 'unknown')
            output_filename = f"output/mermaid/{root_qid}_5hop_taxonomy.mmd"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.mermaid_lines))
        
        print(f"\nMermaid saved: {output_path}")
        print(f"  Lines: {len(self.mermaid_lines)}")
        print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")
        
        return str(output_path)
    
    def save_markdown_with_mermaid(self, output_filename: str = None):
        """Save as Markdown with embedded Mermaid"""
        
        if not output_filename:
            root_qid = self.data.get('root_qid', 'unknown')
            output_filename = f"output/mermaid/{root_qid}_5hop_taxonomy.md"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        root_qid = self.data.get('root_qid')
        root_label = self.data.get('root_label')
        stats = self.data.get('statistics', {})
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 5-Hop Taxonomy: {root_label} ({root_qid})\n\n")
            f.write(f"**Generated:** {self.data.get('timestamp', 'N/A')}\n\n")
            f.write(f"**Statistics:**\n")
            f.write(f"- Entities: {stats.get('total_entities_fetched', 0)}\n")
            f.write(f"- Relationships: {stats.get('total_relationships', 0)}\n")
            f.write(f"- Upward: {stats.get('upward_relationships', 0)}\n")
            f.write(f"- Downward: {stats.get('downward_relationships', 0)}\n")
            f.write(f"- Succession: {stats.get('succession_relationships', 0)}\n\n")
            f.write(f"---\n\n")
            f.write(f"## Taxonomy Diagram\n\n")
            f.write(f"```mermaid\n")
            f.write('\n'.join(self.mermaid_lines))
            f.write(f"\n```\n\n")
            f.write(f"---\n\n")
            f.write(f"## Legend\n\n")
            f.write(f"- **Red (Root):** {root_label} - Starting entity\n")
            f.write(f"- **Blue (Historical):** Concrete historical entities\n")
            f.write(f"- **Green (Academic):** Field of study, academic concepts\n")
            f.write(f"- **Yellow (Temporal):** Time-related concepts\n")
            f.write(f"- **Purple (Abstract):** Abstract concepts and classifications\n\n")
            f.write(f"**Relationship Types:**\n")
            f.write(f"- Solid arrow `-->` : Upward (parent, instance of, part of)\n")
            f.write(f"- Dotted arrow `-.->` : Downward (has parts, contains)\n")
            f.write(f"- Thick arrow `==>` : Succession (follows, followed by)\n")
        
        print(f"\nMarkdown saved: {output_path}")
        
        return str(output_path)
    
    def run_full_generation(self):
        """Run complete generation pipeline"""
        
        print(f"\n{'='*80}")
        print(f"TAXONOMY TO MERMAID GENERATOR")
        print(f"{'='*80}\n")
        
        # Load JSON
        self.load_json()
        
        # Generate Mermaid
        self.generate_mermaid()
        
        # Save files
        mermaid_path = self.save_mermaid()
        markdown_path = self.save_markdown_with_mermaid()
        
        print(f"\n{'='*80}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*80}\n")
        print(f"Mermaid file: {mermaid_path}")
        print(f"Markdown file: {markdown_path}")
        print(f"\nOpen the .md file in a Mermaid-compatible viewer!")
        
        return markdown_path


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # Use 5-hop file
        json_file = "output/taxonomy_recursive/Q17167_recursive_20260220_135756.json"
    
    generator = TaxonomyMermaidGenerator(json_file)
    markdown_path = generator.run_full_generation()
    
    print(f"\nDone! Mermaid diagram ready")


if __name__ == "__main__":
    main()
