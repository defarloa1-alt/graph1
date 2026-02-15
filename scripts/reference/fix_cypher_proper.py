#!/usr/bin/env python3
"""
Properly restructure Cypher with correct WITH clauses.
Only pass variables that have been created.
"""
import re

def fix_cypher_proper(input_file, output_file):
    """Fix Cypher statements with proper WITH clauses."""
    
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
            fixed_lines.append(statements[0] + ';\n')
        else:
            # Track which variables exist
            available_vars = set()
            combined = []
            
            for i, stmt in enumerate(statements):
                if i > 0:
                    # Add WITH clause with variables available BEFORE this statement
                    # Don't include variables that are created in the current statement
                    vars_to_use = available_vars.copy()
                    
                    # Check what variables are created in this statement
                    merge_matches = re.findall(r'MERGE\s+\((\w+):', stmt)
                    create_matches = re.findall(r'CREATE\s+\((\w+):', stmt)
                    vars_created = set(merge_matches + create_matches)
                    
                    # Remove variables that are being created
                    vars_to_use = vars_to_use - vars_created
                    
                    if vars_to_use:
                        combined.append(' WITH ' + ', '.join(sorted(vars_to_use)))
                    else:
                        combined.append(' WITH p')  # Always have p after first statement
                
                combined.append(stmt)
                
                # Update available variables AFTER this statement executes
                merge_matches = re.findall(r'MERGE\s+\((\w+):', stmt)
                create_matches = re.findall(r'CREATE\s+\((\w+):', stmt)
                
                for var in merge_matches + create_matches:
                    available_vars.add(var)
                
                # p is always available after first statement
                if i == 0:
                    available_vars.add('p')
            
            fixed_lines.append(' '.join(combined) + ';\n')
        
        fixed_lines.append('\n')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed file written to {output_file}")

if __name__ == "__main__":
    fix_cypher_proper("Subjects/periods_import.cypher", "Subjects/periods_import.cypher")

