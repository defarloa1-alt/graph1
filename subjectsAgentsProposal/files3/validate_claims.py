#!/usr/bin/env python3
"""
Validate Roman Republic Smoke Test Claims
Checks structure, completeness, and data quality
"""

import json
import sys
from typing import List, Dict, Any

def validate_smoke_test(claims_json: Dict[str, Any]) -> List[str]:
    """
    Validate the 17 claims from the smoke test
    Returns list of issues (empty if all valid)
    """
    issues = []
    
    # 1. Check top-level structure
    required_top = ['subject', 'claims', 'metadata']
    for field in required_top:
        if field not in claims_json:
            issues.append(f"Missing top-level field: '{field}'")
            return issues  # Can't continue without these
    
    # 2. Check subject structure
    subject = claims_json['subject']
    required_subject = ['subject_id', 'label', 'temporal']
    for field in required_subject:
        if field not in subject:
            issues.append(f"Subject missing field: '{field}'")
    
    # 3. Check claim count (flexible range for natural distribution)
    claims = claims_json['claims']
    if len(claims) < 20:
        issues.append(f"⚠️ Only {len(claims)} claims (recommended: 25-30)")
    elif len(claims) > 40:
        issues.append(f"⚠️ Too many claims: {len(claims)} (recommended: 25-30)")
    
    # 4. Check facet coverage (some facets may have 0 claims - this is OK!)
    expected_facets = [
        "Military", "Political", "Social", "Economic", "Diplomatic",
        "Religious", "Legal", "Literary", "Cultural", "Technological",
        "Agricultural", "Artistic", "Philosophical", "Scientific",
        "Geographic", "Biographical", "Communication"
    ]
    
    found_primary = [c.get('primary_facet', c.get('facet', '')) for c in claims]
    covered_facets = set(found_primary) & set(expected_facets)
    
    if len(covered_facets) < 8:
        issues.append(f"⚠️ Only {len(covered_facets)} facets covered (low diversity)")
    
    # No longer checking for duplicates since multiple claims per facet is expected
    
    # 5. Check each claim structure
    for i, claim in enumerate(claims):
        claim_num = i + 1
        facet = claim.get('primary_facet', claim.get('facet', f'unknown_{claim_num}'))
        
        # Required fields
        required = ['claim_text', 'evidence', 'confidence', 'temporal']
        # primary_facet OR facet (backward compatible)
        if 'primary_facet' not in claim and 'facet' not in claim:
            issues.append(f"❌ Claim {claim_num}: Missing 'primary_facet' or 'facet'")
        
        for field in required:
            if field not in claim:
                issues.append(f"❌ Claim {claim_num} ({facet}): Missing '{field}'")
        
        # Claim text length
        if 'claim_text' in claim:
            text_len = len(claim['claim_text'])
            if text_len < 20:
                issues.append(f"⚠️ Claim {claim_num} ({facet}): Suspiciously short ({text_len} chars)")
            if text_len > 500:
                issues.append(f"⚠️ Claim {claim_num} ({facet}): Very long ({text_len} chars)")
        
        # Confidence range
        if 'confidence' in claim:
            conf = claim['confidence']
            if not isinstance(conf, (int, float)):
                issues.append(f"❌ Claim {claim_num} ({facet}): Confidence must be number, got {type(conf)}")
            elif not (0.0 <= conf <= 1.0):
                issues.append(f"❌ Claim {claim_num} ({facet}): Invalid confidence {conf} (must be 0.0-1.0)")
            elif conf < 0.5:
                issues.append(f"⚠️ Claim {claim_num} ({facet}): Low confidence ({conf})")
        
        # Evidence structure
        if 'evidence' in claim:
            ev = claim['evidence']
            if not isinstance(ev, dict):
                issues.append(f"❌ Claim {claim_num} ({facet}): Evidence must be object")
            else:
                if 'source_type' not in ev:
                    issues.append(f"❌ Claim {claim_num} ({facet}): Evidence missing 'source_type'")
                if 'source_text' not in ev:
                    issues.append(f"❌ Claim {claim_num} ({facet}): Evidence missing 'source_text'")
                
                # Check authority if present
                if 'authority' in ev:
                    auth = ev['authority']
                    if 'type' not in auth or 'label' not in auth:
                        issues.append(f"⚠️ Claim {claim_num} ({facet}): Incomplete authority")
        
        # Temporal structure
        if 'temporal' in claim:
            temp = claim['temporal']
            if not isinstance(temp, dict):
                issues.append(f"❌ Claim {claim_num} ({facet}): Temporal must be object")
            else:
                if 'start_year' not in temp:
                    issues.append(f"❌ Claim {claim_num} ({facet}): Temporal missing 'start_year'")
                if 'end_year' not in temp:
                    issues.append(f"❌ Claim {claim_num} ({facet}): Temporal missing 'end_year'")
                
                # Check date ranges are within Roman Republic
                start = temp.get('start_year', 0)
                end = temp.get('end_year', 0)
                
                if start < -509:
                    issues.append(f"⚠️ Claim {claim_num} ({facet}): Start year {start} before Republic founding (-509)")
                if end > -27:
                    issues.append(f"⚠️ Claim {claim_num} ({facet}): End year {end} after Republic end (-27)")
                if start > end:
                    issues.append(f"❌ Claim {claim_num} ({facet}): Start year {start} after end year {end}")
    
    # 6. Check for duplicate claim text
    claim_texts = [c.get('claim_text', '') for c in claims]
    unique_texts = set(claim_texts)
    if len(claim_texts) != len(unique_texts):
        issues.append("❌ Duplicate claim texts detected")
    
    # 7. Check metadata
    metadata = claims_json['metadata']
    if 'generated_by' not in metadata:
        issues.append("⚠️ Metadata missing 'generated_by'")
    if 'timestamp' not in metadata:
        issues.append("⚠️ Metadata missing 'timestamp'")
    
    return issues


def print_summary(claims_json: Dict[str, Any], issues: List[str]):
    """
    Print validation summary
    """
    print("\n" + "="*70)
    print("SMOKE TEST VALIDATION REPORT")
    print("="*70)
    
    # Basic stats
    print(f"\n📊 STATISTICS:")
    print(f"  Subject: {claims_json.get('subject', {}).get('label', 'Unknown')}")
    print(f"  Total claims: {len(claims_json.get('claims', []))}")
    print(f"  Expected: 17")
    
    # Facet distribution
    claims = claims_json.get('claims', [])
    facet_counts = {}
    for claim in claims:
        primary = claim.get('primary_facet', claim.get('facet', 'Unknown'))
        facet_counts[primary] = facet_counts.get(primary, 0) + 1
    
    print(f"\n📋 FACET DISTRIBUTION:")
    all_facets = [
        "Military", "Political", "Social", "Economic", "Diplomatic",
        "Religious", "Legal", "Literary", "Cultural", "Technological",
        "Agricultural", "Artistic", "Philosophical", "Scientific",
        "Geographic", "Biographical", "Communication"
    ]
    for facet in sorted(all_facets):
        count = facet_counts.get(facet, 0)
        if count == 0:
            print(f"  ⚪ {facet}: {count} claims")
        elif count <= 2:
            print(f"  🔵 {facet}: {count} claims")
        else:
            print(f"  🟢 {facet}: {count} claims")
    
    # Confidence distribution
    confidences = [c.get('confidence', 0) for c in claims]
    if confidences:
        avg_conf = sum(confidences) / len(confidences)
        min_conf = min(confidences)
        max_conf = max(confidences)
        print(f"\n📈 CONFIDENCE SCORES:")
        print(f"  Average: {avg_conf:.2f}")
        print(f"  Range: {min_conf:.2f} - {max_conf:.2f}")
    
    # Authority usage
    with_authority = sum(1 for c in claims if 'authority' in c.get('evidence', {}))
    print(f"\n📚 AUTHORITY CITATIONS:")
    print(f"  Claims with authorities: {with_authority}/{len(claims)}")
    
    # Issues
    print(f"\n🔍 VALIDATION ISSUES:")
    if not issues:
        print("  ✅ No issues found! All validations passed.")
    else:
        print(f"  Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"    {issue}")
    
    # Overall result
    print("\n" + "="*70)
    if not issues:
        print("🎉 RESULT: ✅ PASSED - Ready for ingestion!")
    else:
        critical = sum(1 for i in issues if '❌' in i)
        warnings = sum(1 for i in issues if '⚠️' in i)
        print(f"⚠️ RESULT: NEEDS REVIEW - {critical} critical, {warnings} warnings")
    print("="*70 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_claims.py <claims_json_file>")
        print("Example: python validate_claims.py roman_republic_smoke_test.json")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            claims_json = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON: {e}")
        sys.exit(1)
    
    # Run validation
    issues = validate_smoke_test(claims_json)
    
    # Print summary
    print_summary(claims_json, issues)
    
    # Exit code
    sys.exit(0 if not issues else 1)


if __name__ == "__main__":
    main()
