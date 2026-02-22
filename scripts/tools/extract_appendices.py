#!/usr/bin/env python3
"""
Extract Appendices from Consolidated Architecture Document

Organizes 26 appendices into 6 thematic clusters.
"""

import re
from pathlib import Path

# Appendix clustering strategy (from decomposition plan)
APPENDIX_CLUSTERS = {
    "01_Domain_Ontology": {
        "appendices": ["A", "B", "C", "D"],
        "names": {
            "A": "Canonical_Relationship_Types.md",
            "B": "Action_Structure_Vocabularies.md",
            "C": "Entity_Type_Taxonomies.md",
            "D": "Subject_Facet_Classification.md"
        }
    },
    "02_Authority_Integration": {
        "appendices": ["E", "F", "K"],
        "names": {
            "E": "Temporal_Authority_Alignment.md",
            "F": "Geographic_Authority_Integration.md",
            "K": "Wikidata_Integration_Patterns.md"
        }
    },
    "03_Standards_Alignment": {
        "appendices": ["L", "P", "R", "S"],
        "names": {
            "L": "CIDOC_CRM_Integration_Guide.md",
            "P": "Semantic_Enrichment_Ontology_Alignment.md",
            "R": "Federation_Strategy_Multi_Authority.md",
            "S": "BabelNet_Lexical_Authority.md"
        }
    },
    "04_Implementation_Patterns": {
        "appendices": ["G", "J", "O", "T"],
        "names": {
            "G": "Legacy_Implementation_Patterns.md",
            "J": "Implementation_Examples.md",
            "O": "Facet_Training_Resources_Registry.md",
            "T": "Subject_Facet_Agent_Workflow.md"
        }
    },
    "05_Architecture_Decisions": {
        "appendices": ["H", "U", "V", "W", "X", "Y"],
        "names": {
            "H": "Architectural_Decision_Records_Overview.md",
            "U": "ADR_001_Claim_Identity_Ciphers.md",
            "V": "ADR_002_Function_Driven_Relationships.md",
            "W": "ADR_004_Canonical_18_Facet_System.md",
            "X": "ADR_005_Federated_Claims_Signing.md",
            "Y": "ADR_006_Bootstrap_Scaffold_Contract.md"
        }
    },
    "06_Advanced_Topics": {
        "appendices": ["I", "M", "N", "Q"],
        "names": {
            "I": "Mathematical_Formalization.md",
            "M": "Identifier_Safety_Reference.md",
            "N": "Property_Extensions_Advanced_Attributes.md",
            "Q": "Operational_Modes_Agent_Orchestration.md"
        }
    }
}

def find_appendix_boundaries(file_path: Path) -> dict:
    """Find start line for each appendix."""
    print("Scanning for appendix boundaries...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    boundaries = {}
    appendix_pattern = re.compile(r'^#+ \*\*Appendix ([A-Z])(\.?\d*):')
    
    for i, line in enumerate(lines, 1):
        match = appendix_pattern.match(line)
        if match:
            appendix_letter = match.group(1)
            boundaries[appendix_letter] = i
            print(f"  Found Appendix {appendix_letter} at line {i}")
    
    # Add end marker
    boundaries['END'] = len(lines)
    
    return boundaries

def extract_appendix(input_file: Path, output_folder: Path, appendix_letter: str, 
                    output_filename: str, start_line: int, end_line: int):
    """Extract one appendix to a file."""
    output_path = output_folder / output_filename
    
    print(f"Extracting Appendix {appendix_letter}: lines {start_line}-{end_line} to {output_path.name}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract section
    section_lines = lines[start_line-1:end_line-1]
    
    # Add navigation header
    header = f"""# Appendix {appendix_letter}: {output_filename.replace('_', ' ').replace('.md', '')}

**Version:** 3.2 Decomposed  
**Date:** February 19, 2026  
**Source:** Extracted from Consolidated Architecture Document

---

## Navigation

**Main Architecture:**
- [ARCHITECTURE_CORE.md](../../ARCHITECTURE_CORE.md)
- [ARCHITECTURE_ONTOLOGY.md](../../ARCHITECTURE_ONTOLOGY.md)
- [ARCHITECTURE_IMPLEMENTATION.md](../../ARCHITECTURE_IMPLEMENTATION.md)
- [ARCHITECTURE_GOVERNANCE.md](../../ARCHITECTURE_GOVERNANCE.md)

**Appendices Index:** [README.md](../README.md)

---

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        f.writelines(section_lines)
    
    print(f"  [OK] Wrote {len(section_lines)} lines")
    return len(section_lines)

def main():
    """Main extraction workflow."""
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / "Key Files" / "2-12-26 Chrystallum Architecture - CONSOLIDATED.md"
    appendices_base = project_root / "Key Files" / "Appendices"
    
    if not input_file.exists():
        print(f"ERROR: Could not find {input_file}")
        return
    
    # Find all appendix boundaries
    boundaries = find_appendix_boundaries(input_file)
    print(f"\nFound {len(boundaries)-1} appendices\n")
    
    total_lines = 0
    extracted_count = 0
    
    # Extract each appendix into appropriate cluster folder
    for cluster_name, cluster_info in APPENDIX_CLUSTERS.items():
        cluster_folder = appendices_base / cluster_name
        cluster_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\n=== Cluster: {cluster_name} ===")
        
        for appendix_letter in cluster_info["appendices"]:
            if appendix_letter not in boundaries:
                print(f"  [WARN] Appendix {appendix_letter} not found in file")
                continue
            
            # Find end line (next appendix or document end)
            appendix_letters = sorted(boundaries.keys())
            current_idx = appendix_letters.index(appendix_letter)
            if current_idx < len(appendix_letters) - 1:
                next_letter = appendix_letters[current_idx + 1]
                end_line = boundaries[next_letter]
            else:
                end_line = boundaries['END']
            
            start_line = boundaries[appendix_letter]
            output_filename = cluster_info["names"][appendix_letter]
            
            lines_extracted = extract_appendix(
                input_file,
                cluster_folder,
                appendix_letter,
                output_filename,
                start_line,
                end_line
            )
            
            total_lines += lines_extracted
            extracted_count += 1
    
    print(f"\n{'='*60}")
    print(f"Extraction complete!")
    print(f"  Appendices extracted: {extracted_count}")
    print(f"  Total lines: {total_lines:,}")
    print(f"  Output: {appendices_base}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()


