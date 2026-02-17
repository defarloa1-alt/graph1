#!/usr/bin/env python3
"""
Fix UTF-8 encoding artifacts in Markdown files.
Replaces mojibake arrow (â†') with proper Unicode arrow (→).
"""

import os
from pathlib import Path

# The malformed sequence
ARTIFACT = "â†'"  # This is how mojib ake renders in UTF-8
CORRECT = "→"  # Proper Unicode arrow (U+2192)

def fix_file(filepath):
    """Fix encoding artifacts in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if ARTIFACT in content:
            count = content.count(ARTIFACT)
            new_content = content.replace(ARTIFACT, CORRECT)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return count
        return 0
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return 0

def main():
    """Scan and fix all Markdown files."""
    root = Path('.')
    markdown_files = list(root.rglob('*.md'))
    
    print("Scanning for encoding artifacts (â†' → →)...")
    print()
    
    files_fixed = 0
    total_replacements = 0
    
    for filepath in markdown_files:
        # Skip .git and node_modules
        if '.git' in filepath.parts or 'node_modules' in filepath.parts:
            continue
        
        count = fix_file(filepath)
        if count > 0:
            print(f"Fixed {count} instances in: {filepath}")
            files_fixed += 1
            total_replacements += count
    
    print()
    print("=" * 40)
    print(f"Files fixed: {files_fixed}")
    print(f"Total replacements: {total_replacements}")
    print("=" * 40)

if __name__ == '__main__':
    main()
