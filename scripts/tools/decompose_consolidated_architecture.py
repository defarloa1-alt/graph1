#!/usr/bin/env python3
"""
Decompose Consolidated Architecture Document

Extracts sections from the large consolidated architecture file into modular files.
"""

import sys
from pathlib import Path

# Section boundaries (line numbers from grep analysis)
SECTIONS = {
    "ARCHITECTURE_CORE.md": {
        "start": 1,
        "end": 595,
        "description": "Sections 1-2: Executive Summary & System Overview"
    },
    "ARCHITECTURE_ONTOLOGY.md": {
        "start": 596,
        "end": 5204,
        "description": "Sections 3-7: Entity, Subject, Agent, Claims, Relationship Layers"
    },
    "ARCHITECTURE_IMPLEMENTATION.md": {
        "start": 5205,
        "end": 6959,
        "description": "Sections 8-9: Technology Stack & Workflows"
    },
    "ARCHITECTURE_GOVERNANCE.md": {
        "start": 6960,
        "end": 7577,
        "description": "Sections 10-12: QA, Governance, Future Directions"
    },
    "APPENDICES_START": {
        "start": 7578,
        "end": 15910,
        "description": "Part V: All Appendices (to be further subdivided)"
    }
}

def extract_section(input_file: Path, output_file: Path, start_line: int, end_line: int):
    """Extract lines from input file and write to output file."""
    print(f"Extracting lines {start_line}-{end_line} to {output_file.name}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract section (convert to 0-indexed)
    section_lines = lines[start_line-1:end_line]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(section_lines)
    
    print(f"  [OK] Wrote {len(section_lines)} lines to {output_file}")
    return len(section_lines)

def add_header(output_file: Path, section_name: str, description: str):
    """Add decomposition header to extracted file."""
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    header = f"""# {section_name.replace('.md', '').replace('_', ' ').title()}

**Version:** 3.2 Decomposed  
**Date:** February 19, 2026  
**Status:** Extracted from Consolidated  
**Source:** `2-12-26 Chrystallum Architecture - CONSOLIDATED.md` ({description})

---

## Navigation

**Architecture Documents:**
- [ARCHITECTURE_CORE.md](../ARCHITECTURE_CORE.md) - Executive summary & overview
- [ARCHITECTURE_ONTOLOGY.md](../ARCHITECTURE_ONTOLOGY.md) - Core ontology layers
- [ARCHITECTURE_IMPLEMENTATION.md](../ARCHITECTURE_IMPLEMENTATION.md) - Technology & workflows  
- [ARCHITECTURE_GOVERNANCE.md](../ARCHITECTURE_GOVERNANCE.md) - QA & governance
- [Appendices/](../Appendices/) - Detailed appendices

**Quick Links:**
- [README.md](../../README.md) - Project overview
- [ARCHITECTURE_IMPLEMENTATION_INDEX.md](../ARCHITECTURE_IMPLEMENTATION_INDEX.md) - Section to code mapping

---

"""
    
    # Insert header after any existing title
    if content.startswith('#'):
        # Find end of existing title
        first_newline = content.find('\n')
        if first_newline > 0:
            # Find next section
            next_section = content.find('\n#', first_newline + 1)
            if next_section > 0:
                new_content = content[:next_section] + '\n' + header + content[next_section:]
            else:
                new_content = content + '\n' + header
        else:
            new_content = header + content
    else:
        new_content = header + content
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    """Main extraction workflow."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    input_file = project_root / "Key Files" / "2-12-26 Chrystallum Architecture - CONSOLIDATED.md"
    output_dir = project_root / "Key Files"
    
    if not input_file.exists():
        print(f"❌ ERROR: Could not find {input_file}")
        sys.exit(1)
    
    print(f"Reading from: {input_file}")
    print(f"Writing to: {output_dir}")
    print()
    
    total_lines = 0
    
    # Extract each section (except appendices and core which is already created)
    for section_name, info in SECTIONS.items():
        if section_name in ["ARCHITECTURE_CORE.md", "APPENDICES_START"]:
            continue  # Skip core (already created) and appendices (separate process)
        
        output_file = output_dir / section_name
        lines_extracted = extract_section(
            input_file,
            output_file,
            info["start"],
            info["end"]
        )
        total_lines += lines_extracted
        print()
    
    print(f"Extraction complete!")
    print(f"   Total lines extracted: {total_lines:,}")
    print()
    print("Next steps:")
    print("1. Review extracted files for quality")
    print("2. Extract appendices into clustered folders")
    print("3. Update cross-references between files")
    print("4. Archive consolidated file")

if __name__ == "__main__":
    main()

