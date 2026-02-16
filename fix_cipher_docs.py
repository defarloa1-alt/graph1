#!/usr/bin/env python3
"""Fix misleading cipher documentation in architecture"""

import re

file_path = "Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the misleading comment
for i, line in enumerate(lines):
    if 'Computed with confidence=0.85' in line:
        lines[i] = line.replace(
            '// Computed with confidence=0.85',
            '// Content-only cipher (NOT computed with confidence)'
        )
        print(f"✓ Fixed line {i+1}: removed 'Computed with confidence' comment")
    
    # Also fix the misleading "Different confidence → different cipher!"
    if 'Different confidence' in line and 'different cipher' in line:
        lines[i] = '// SAME CIPHER if confidence only changes; DIFFERENT cipher only if content changes\n'
        print(f"✓ Fixed line {i+1}: clarified cipher stability")

# Insert clarification after the versioning example
for i, line in enumerate(lines):
    if line.strip().startswith('**Benefits:**') and i > 3500 and i <3550:
        # Check if this is the claim versioning section (look backwards for context)
        context = ''.join(lines[max(0,i-20):i])
        if 'Query claim evolution' in context:
            # Insert clarification BEFORE the Benefits section
            clarification = """
**Key Point (ADR-001 Alignment):**
- **Same content + updated confidence → SAME cipher** (cipher depends only on content, not provenance)
- **Different content → DIFFERENT cipher** (captures semantic change, e.g., refined temporal data)
- Provenance changes (confidence updates, new reviews) do NOT change the cipher
- See **Appendix U (ADR-001)** for complete cipher specification

"""
            lines.insert(i, clarification)
            print(f"✓ Inserted ADR-001 alignment note at line {i+1}")
            break

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ Fixed misled cipher versioning documentation")
print("✅ Added ADR-001 alignment clarification")
