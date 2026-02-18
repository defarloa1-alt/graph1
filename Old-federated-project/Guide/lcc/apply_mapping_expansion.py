"""
Crosswalk Expansion Implementation
==================================

Apply comprehensive LCC-FAST mappings to close coverage gaps.
"""

import sqlite3
import json
from datetime import datetime

def apply_expanded_mappings():
    """Apply the comprehensive mapping expansion to the database."""
    
    print("=== Applying Expanded LCC-FAST Mappings ===\n")
    
    # Load the expanded mappings
    with open('expanded_mappings.json', 'r') as f:
        mappings_data = json.load(f)
    
    conn = sqlite3.connect('taxonomy.db')
    cursor = conn.cursor()
    
    total_added = 0
    total_attempted = 0
    mapping_results = {
        "success": [],
        "errors": [],
        "skipped": []
    }
    
    for lcc_code, mappings in mappings_data.items():
        for mapping in mappings:
            total_attempted += 1
            
            try:
                # Check if mapping already exists
                cursor.execute(
                    "SELECT COUNT(*) FROM lcc_fast_crosswalk WHERE lcc_class_code = ? AND fast_id = ?",
                    (lcc_code, mapping['fast_id'])
                )
                
                if cursor.fetchone()[0] > 0:
                    mapping_results["skipped"].append({
                        "lcc_code": lcc_code,
                        "fast_id": mapping['fast_id'],
                        "reason": "Mapping already exists"
                    })
                    continue
                
                # Determine mapping type and confidence level
                mapping_type = "direct" if mapping['confidence'] == "high" else "approximate"
                confidence_level = {
                    "high": 95,
                    "medium": 85, 
                    "low": 75,
                    "needs_review": 65
                }.get(mapping['confidence'], 75)
                
                # Insert new mapping
                cursor.execute("""
                    INSERT INTO lcc_fast_crosswalk 
                    (lcc_class_code, fast_id, mapping_type, confidence_level, 
                     scope_notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    lcc_code,
                    mapping['fast_id'], 
                    mapping_type,
                    confidence_level,
                    mapping['mapping_rationale'],
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                total_added += 1
                mapping_results["success"].append({
                    "lcc_code": lcc_code,
                    "fast_id": mapping['fast_id'],
                    "heading": mapping['heading'],
                    "confidence": confidence_level
                })
                
                print(f"SUCCESS: {lcc_code} -> {mapping['fast_id']} ({mapping['heading']}) [{confidence_level}%]")
                
            except Exception as e:
                mapping_results["errors"].append({
                    "lcc_code": lcc_code,
                    "fast_id": mapping['fast_id'],
                    "error": str(e)
                })
                print(f"ERROR mapping {lcc_code} -> {mapping['fast_id']}: {e}")
    
    conn.commit()
    
    # Generate summary report
    print(f"\n=== Expansion Summary ===")
    print(f"Total mappings attempted: {total_attempted}")
    print(f"Successfully added: {total_added}")
    print(f"Skipped (already exist): {len(mapping_results['skipped'])}")
    print(f"Errors: {len(mapping_results['errors'])}")
    
    # Check new coverage
    cursor.execute("SELECT COUNT(DISTINCT lcc_class_code) FROM lcc_fast_crosswalk")
    mapped_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM subject_nodes")
    total_count = cursor.fetchone()[0]
    
    coverage_rate = (mapped_count / total_count) * 100
    print(f"New coverage rate: {coverage_rate:.1f}% ({mapped_count}/{total_count})")
    
    # Save results for review
    with open('mapping_expansion_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_attempted": total_attempted,
            "total_added": total_added,
            "coverage_rate": coverage_rate,
            "results": mapping_results
        }, f, indent=2)
    
    conn.close()
    print(f"\nResults saved to mapping_expansion_results.json")

if __name__ == '__main__':
    apply_expanded_mappings()
