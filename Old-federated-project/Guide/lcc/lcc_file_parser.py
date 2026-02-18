#!/usr/bin/env python3
"""
LCC File Parser and Structure Analyzer
======================================

Parse LCC source files and extract structured data for taxonomy implementation.
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

class LCCFileParser:
    """Parser for LCC Excel and CSV files"""
    
    def __init__(self, source_dir: str = r"c:\Projects\Subjects\source"):
        self.source_dir = Path(source_dir)
        self.parsed_data = {}
        
    def parse_csv_outline(self, content: str) -> List[Dict[str, Any]]:
        """Parse the complex outline format in CSV files"""
        
        entries = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract class code and description using regex
            # Pattern: class_code followed by description
            match = re.match(r'^([A-Z]+[0-9.-]*)\s+(.+)$', line)
            if match:
                class_code, description = match.groups()
                
                # Determine hierarchy level by indentation or pattern
                level = self._determine_hierarchy_level(line, class_code)
                
                entries.append({
                    'class_code': class_code.strip(),
                    'label': description.strip(),
                    'level': level,
                    'raw_line': line
                })
        
        return entries
    
    def _determine_hierarchy_level(self, line: str, class_code: str) -> int:
        """Determine hierarchy level based on class code pattern"""
        
        # Level 0: Single letters (A, B, C, etc.)
        if re.match(r'^[A-Z]$', class_code):
            return 0
        
        # Level 1: Letter + number (A1, B1, etc.)
        if re.match(r'^[A-Z][0-9]+$', class_code):
            return 1
            
        # Level 2: Letter + number range (A1-100, etc.)
        if re.match(r'^[A-Z][0-9]+-[0-9]+$', class_code):
            return 1
            
        # Level 3: More specific codes
        if '.' in class_code:
            return 2
            
        # Default to level 1
        return 1
    
    def parse_excel_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse Excel LCC file"""
        
        try:
            # Try different sheet names and structures
            df = pd.read_excel(file_path)
            
            entries = []
            
            # Check for common column patterns
            columns = [col.lower() for col in df.columns]
            
            for idx, row in df.iterrows():
                # Extract data based on available columns
                entry = {
                    'file_source': file_path.name,
                    'row_index': idx
                }
                
                # Try to extract class code and label from first few columns
                for i, cell in enumerate(row[:3]):
                    if pd.notna(cell) and isinstance(cell, str):
                        # Look for class code pattern
                        if re.match(r'^[A-Z]+[0-9.-]*$', str(cell).strip()):
                            entry['class_code'] = str(cell).strip()
                        else:
                            if 'label' not in entry:
                                entry['label'] = str(cell).strip()
                
                if 'class_code' in entry:
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            print(f"Error parsing {file_path.name}: {e}")
            return []
    
    def parse_csv_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse CSV LCC file"""
        
        try:
            df = pd.read_csv(file_path)
            
            entries = []
            
            # Check if this is an outline format (single column with complex data)
            if len(df.columns) <= 3 and len(df) < 20:
                # This looks like an outline format
                for idx, row in df.iterrows():
                    first_col = row.iloc[0]
                    if pd.notna(first_col) and isinstance(first_col, str):
                        outline_entries = self.parse_csv_outline(first_col)
                        for entry in outline_entries:
                            entry['file_source'] = file_path.name
                            entry['row_index'] = idx
                            entries.extend([entry])
            else:
                # Regular tabular format
                for idx, row in df.iterrows():
                    entry = {
                        'file_source': file_path.name,
                        'row_index': idx
                    }
                    
                    # Extract data from columns
                    for col, value in row.items():
                        if pd.notna(value):
                            entry[col] = str(value).strip()
                    
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            print(f"Error parsing {file_path.name}: {e}")
            return []
    
    def parse_all_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """Parse all LCC files in the source directory"""
        
        results = {}
        
        # Get all Excel and CSV files
        xlsx_files = list(self.source_dir.glob("*.xlsx"))
        csv_files = list(self.source_dir.glob("*.csv"))
        
        print(f"Found {len(xlsx_files)} Excel files and {len(csv_files)} CSV files")
        
        # Parse Excel files
        for file_path in xlsx_files:
            print(f"Parsing Excel: {file_path.name}")
            try:
                entries = self.parse_excel_file(file_path)
                results[file_path.name] = entries
                print(f"  Extracted {len(entries)} entries")
            except Exception as e:
                print(f"  Error: {e}")
                results[file_path.name] = []
        
        # Parse CSV files  
        for file_path in csv_files:
            print(f"Parsing CSV: {file_path.name}")
            try:
                entries = self.parse_csv_file(file_path)
                results[file_path.name] = entries
                print(f"  Extracted {len(entries)} entries")
            except Exception as e:
                print(f"  Error: {e}")
                results[file_path.name] = []
        
        self.parsed_data = results
        return results
    
    def consolidate_data(self) -> List[Dict[str, Any]]:
        """Consolidate all parsed data into a unified structure"""
        
        consolidated = []
        
        for file_name, entries in self.parsed_data.items():
            for entry in entries:
                # Standardize the entry
                standardized = {
                    'class_code': entry.get('class_code', ''),
                    'label': entry.get('label', ''),
                    'parent_code': self._extract_parent_code(entry.get('class_code', '')),
                    'level': entry.get('level', 0),
                    'source_file': file_name,
                    'raw_data': entry
                }
                
                # Only include entries with class codes
                if standardized['class_code']:
                    consolidated.append(standardized)
        
        return consolidated
    
    def _extract_parent_code(self, class_code: str) -> str:
        """Extract parent class code from a given class code"""
        
        if not class_code:
            return ""
        
        # For codes like "QA76.9.A25", parent would be "QA76.9"
        # For codes like "QA76-77", parent would be "QA"
        # For codes like "Q", parent would be ""
        
        if '.' in class_code:
            parts = class_code.split('.')
            if len(parts) > 1:
                return '.'.join(parts[:-1])
        
        if '-' in class_code:
            parts = class_code.split('-')
            return re.match(r'^[A-Z]+', parts[0]).group()
        
        # For single letter or letter+number, parent is just the letter
        match = re.match(r'^([A-Z]+)', class_code)
        if match and len(match.group(1)) < len(class_code):
            return match.group(1)
        
        return ""

def main():
    """Main function to demonstrate LCC parsing"""
    
    print("🔍 LCC File Parser Analysis")
    print("=" * 50)
    
    parser = LCCFileParser()
    
    # Parse all files
    results = parser.parse_all_files()
    
    # Consolidate data
    consolidated = parser.consolidate_data()
    
    print(f"\n📊 Consolidation Results:")
    print(f"  Total entries: {len(consolidated)}")
    
    # Show sample entries
    if consolidated:
        print(f"\n📋 Sample entries:")
        for i, entry in enumerate(consolidated[:5]):
            print(f"  {i+1}. {entry['class_code']} - {entry['label'][:50]}...")
    
    # Save consolidated data
    output_file = "consolidated_lcc_data.json"
    with open(output_file, 'w') as f:
        json.dump(consolidated, f, indent=2)
    
    print(f"\n💾 Consolidated data saved to: {output_file}")
    
    # Generate summary statistics
    stats = {
        'total_files_processed': len(results),
        'total_entries_extracted': len(consolidated),
        'files_with_data': len([f for f, entries in results.items() if entries]),
        'unique_class_codes': len(set(entry['class_code'] for entry in consolidated)),
        'class_code_patterns': {},
        'hierarchy_levels': {}
    }
    
    # Analyze class code patterns
    for entry in consolidated:
        code = entry['class_code']
        level = entry['level']
        
        # Pattern analysis
        if re.match(r'^[A-Z]$', code):
            pattern = 'single_letter'
        elif re.match(r'^[A-Z][0-9]+$', code):
            pattern = 'letter_number'
        elif re.match(r'^[A-Z][0-9]+-[0-9]+$', code):
            pattern = 'range'
        elif '.' in code:
            pattern = 'decimal'
        else:
            pattern = 'other'
        
        stats['class_code_patterns'][pattern] = stats['class_code_patterns'].get(pattern, 0) + 1
        stats['hierarchy_levels'][str(level)] = stats['hierarchy_levels'].get(str(level), 0) + 1
    
    print(f"\n📈 Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return consolidated, stats

if __name__ == "__main__":
    consolidated_data, statistics = main()