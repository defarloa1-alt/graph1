#!/usr/bin/env python3
"""
Restructure the Cypher file to use WITH clauses so variables stay in scope.
"""
import re

def add_with_clauses(input_file, output_file):
    """Add WITH clauses between statements to keep variables in scope."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            fixed_lines.append('\n')
            continue
        
        # Split by semicolons
        statements = [s.strip() for s in stripped.split(';') if s.strip()]
        
        if len(statements) == 1:
            # Single statement, just add it
            fixed_lines.append(statements[0] + ';\n')
        else:
            # Multiple statements - chain with WITH
            combined = []
            for i, stmt in enumerate(statements):
                if i == 0:
                    # First statement
                    combined.append(stmt)
                else:
                    # Subsequent statements - add WITH to pass variables
                    # Extract variable names from previous statement
                    # For simplicity, just use WITH p, end, start, f, geo, next, prev, parent
                    combined.append(' WITH p')
                    # Check what variables might be needed
                    if 'end:Year' in stmt or 'end)' in stmt:
                        combined[-1] += ', end'
                    if 'start:Year' in stmt or 'start)' in stmt:
                        combined[-1] += ', start'
                    if 'f:Facet' in stmt or 'f)' in stmt:
                        combined[-1] += ', f'
                    if 'geo:Place' in stmt or 'geo)' in stmt:
                        combined[-1] += ', geo'
                    if 'next:Period' in stmt or 'next)' in stmt:
                        combined[-1] += ', next'
                    if 'prev:Period' in stmt or 'prev)' in stmt:
                        combined[-1] += ', prev'
                    if 'parent:Period' in stmt or 'parent)' in stmt:
                        combined[-1] += ', parent'
                    combined.append(stmt)
            
            fixed_lines.append(' '.join(combined) + ';\n')
        
        fixed_lines.append('\n')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed file written to {output_file}")

if __name__ == "__main__":
    add_with_clauses("Subjects/periods_import.cypher", "Subjects/periods_import.cypher")

