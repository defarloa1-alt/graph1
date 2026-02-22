#!/usr/bin/env python3
"""
Enrich Periods with Perplexity Analysis
- Analyze each period to determine primary facets
- Remove any events that shouldn't be periods
- Restructure edges with proper facet relationships
- Generate clean, properly structured Cypher import file
"""
import sys
import io
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("❌ ERROR: requests not installed")
    print("   Run: pip install requests")
    sys.exit(1)

# Add parent directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent.parent.parent))

# Facet mapping from schema
FACET_TYPES = {
    'PoliticalFacet': ['political', 'state', 'regime', 'dynasty', 'governance', 'government', 'republic', 'empire', 'kingdom'],
    'CulturalFacet': ['cultural', 'culture', 'era', 'identity', 'literature', 'arts', 'civilization'],
    'TechnologicalFacet': ['technological', 'technology', 'tool', 'production', 'industrial', 'revolution'],
    'ReligiousFacet': ['religious', 'religion', 'movement', 'doctrinal', 'theological'],
    'EconomicFacet': ['economic', 'economy', 'trade', 'financial', 'commerce'],
    'MilitaryFacet': ['military', 'warfare', 'conquest', 'war', 'battle', 'conflict'],
    'EnvironmentalFacet': ['environmental', 'climate', 'ecological'],
    'DemographicFacet': ['demographic', 'population', 'migration', 'urbanization'],
    'IntellectualFacet': ['intellectual', 'philosophical', 'scholarly', 'thought'],
    'ScientificFacet': ['scientific', 'science', 'paradigm', 'revolution'],
    'ArtisticFacet': ['artistic', 'art', 'architectural', 'aesthetic', 'style'],
    'SocialFacet': ['social', 'norms', 'class', 'society'],
    'LinguisticFacet': ['linguistic', 'language', 'script'],
    'ArchaeologicalFacet': ['archaeological', 'archaeology', 'material-culture', 'stratigraphy'],
    'DiplomaticFacet': ['diplomatic', 'alliance', 'treaty', 'international']
}

# Event keywords to filter out
EVENT_KEYWORDS = [
    'battle', 'war', 'revolution', 'uprising', 'rebellion', 'invasion', 
    'siege', 'treaty', 'agreement', 'conference', 'meeting', 'assembly',
    'coronation', 'assassination', 'death', 'birth', 'marriage'
]

def parse_periods_from_cypher(file_path) -> List[Dict]:
    """Parse periods from the Cypher import file."""
    with open(str(file_path), 'r', encoding='utf-8') as f:
        content = f.read()
    
    periods = []
    
    # Split by period blocks - look for MERGE (p:Period patterns
    # Since file may be all on one line, we need to handle that
    period_blocks = re.split(r'(?=MERGE \(p:Period)', content)
    
    for block in period_blocks:
        if not block.strip() or 'MERGE (p:Period' not in block:
            continue
        
        # Extract qid
        qid_match = re.search(r"qid: '([^']+)'", block)
        if not qid_match:
            continue
        qid = qid_match.group(1)
        
        # Extract label - handle escaped apostrophes
        label_match = re.search(r"SET p\.label = '((?:[^']|'')+)'", block)
        if not label_match:
            continue
        label = label_match.group(1).replace("''", "'")  # Unescape
        
        # Extract start_year
        start_year = None
        start_match = re.search(r"SET p\.start_year = (\d+)", block)
        if start_match:
            start_year = int(start_match.group(1))
        
        # Extract end_year
        end_year = None
        end_match = re.search(r"SET p\.end_year = (\d+)", block)
        if end_match:
            end_year = int(end_match.group(1))
        
        # Extract current facet label if present
        facet_label = None
        facet_match = re.search(r"MERGE \(f:Facet \{label: '([^']+)'\}\)", block)
        if facet_match:
            facet_label = facet_match.group(1)
        
        # Extract ALL locations (Place nodes) - a period can span multiple geographic areas
        location_qids = set()
        for location_match in re.finditer(r"MERGE \(geo:Place \{qid: '([^']+)'\}\)", block):
            location_qids.add(location_match.group(1))
        
        periods.append({
            'qid': qid,
            'label': label,
            'start_year': start_year,
            'end_year': end_year,
            'location_qids': location_qids,  # Now a set of all locations
            'current_facet': facet_label,
            'raw_content': block[:500]  # First 500 chars for debugging
        })
    
    return periods

def query_perplexity(period_label: str, qid: str, start_year: Optional[int] = None, end_year: Optional[int] = None) -> Dict:
    """
    Query Perplexity API to analyze a period and determine facets.
    
    Note: This requires Perplexity API key. If not available, falls back to rule-based classification.
    """
    # Check for API key
    api_key = None
    try:
        from config import PERPLEXITY_API_KEY
        api_key = PERPLEXITY_API_KEY
    except ImportError:
        pass
    
    if not api_key:
        # Fallback to rule-based classification
        result = classify_period_rule_based(period_label, start_year, end_year)
        result['method'] = 'rule-based'
        return result
    
    # Build query
    query = f"What type of historical period is '{period_label}'"
    if start_year and end_year:
        query += f" ({start_year} to {end_year})"
    elif start_year:
        query += f" (starting {start_year})"
    elif end_year:
        query += f" (ending {end_year})"
    
    query += "? What is the PRIMARY facet for this period? Choose ONE: Political, Cultural, Technological, Religious, Economic, Military, Archaeological, or other. Is this a period or an event?"
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a historical classification expert. Analyze periods and determine the PRIMARY facet (singular, not multiple). Return JSON with: is_period (boolean), primary_facet (string - ONE facet type), is_event (boolean), confidence (float)."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON from response
            try:
                # Extract JSON if wrapped in markdown
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    parsed['method'] = 'perplexity-api'
                    return parsed
            except:
                pass
            
            # Fallback: parse text response
            result = parse_perplexity_response(content, period_label)
            result['method'] = 'perplexity-api'
            return result
        else:
            print(f"⚠️  Perplexity API error: {response.status_code}")
            return classify_period_rule_based(period_label, start_year, end_year)
    
    except Exception as e:
        print(f"⚠️  Perplexity API error: {e}")
        return classify_period_rule_based(period_label, start_year, end_year)

def parse_perplexity_response(content: str, period_label: str) -> Dict:
    """Parse Perplexity text response into structured data."""
    result = {
        'is_period': True,
        'is_event': False,
        'primary_facets': [],
        'confidence': 0.7
    }
    
    content_lower = content.lower()
    
    # Check if it's an event
    if any(keyword in content_lower for keyword in ['event', 'battle', 'war', 'treaty', 'revolution']):
        if any(keyword in period_label.lower() for keyword in EVENT_KEYWORDS):
            result['is_event'] = True
            result['is_period'] = False
    
    # Extract facets
    for facet_type, keywords in FACET_TYPES.items():
        if any(keyword in content_lower for keyword in keywords):
            result['primary_facets'].append(facet_type)
    
    # If no facets found, use rule-based
    if not result['primary_facets']:
        rule_result = classify_period_rule_based(period_label, None, None)
        result['primary_facet'] = rule_result.get('primary_facet', 'CulturalFacet')
    else:
        # Use PRIMARY facet (first one)
        result['primary_facet'] = result['primary_facets'][0]
    
    # Remove list, keep only primary
    result.pop('primary_facets', None)
    
    return result

def classify_period_rule_based(period_label: str, start_year: Optional[int], end_year: Optional[int]) -> Dict:
    """Rule-based classification when Perplexity is unavailable."""
    label_lower = period_label.lower()
    
    # Check if it's an event
    is_event = any(keyword in label_lower for keyword in EVENT_KEYWORDS)
    
    # Determine facets
    facets = []
    for facet_type, keywords in FACET_TYPES.items():
        if any(keyword in label_lower for keyword in keywords):
            facets.append(facet_type)
    
    # Default to CulturalFacet if no specific facet found
    if not facets:
        facets = ['CulturalFacet']  # Most periods have cultural aspects
    
    # Return only PRIMARY facet (first one, most relevant)
    return {
        'is_period': not is_event,
        'is_event': is_event,
        'primary_facet': facets[0] if facets else 'CulturalFacet',  # PRIMARY facet only
        'confidence': 0.6
    }

def generate_cypher(periods: List[Dict], output_file):
    """Generate properly structured Cypher import file."""
    lines = []
    period_count = 0
    
    print(f"\n📝 Step 3: Generating enriched Cypher file...")
    print(f"   Processing {len(periods)} analyzed periods for Cypher generation...")
    
    for period in periods:
        # Requirement 1: Remove events
        if period.get('is_event', False):
            print(f"      ⚠️  FILTERED: Event detected - {period['label']}")
            continue
        
        # Requirement 2: Must have BOTH start_year AND end_year
        if not period.get('start_year') or not period.get('end_year'):
            missing = []
            if not period.get('start_year'):
                missing.append('start_year')
            if not period.get('end_year'):
                missing.append('end_year')
            print(f"      ⚠️  FILTERED: Missing dates ({', '.join(missing)}) - {period['label']}")
            continue
        
        # Requirement 3: Must have at least one location (Place node)
        location_qids = period.get('location_qids', set())
        if not location_qids or len(location_qids) == 0:
            print(f"      ⚠️  FILTERED: Missing location (Place node) - {period['label']}")
            continue
        
        # Requirement 4: End date must be >= 2000 BCE (end_year >= -2000)
        if period.get('end_year') and period['end_year'] < -2000:
            print(f"      ⚠️  FILTERED: End date before 2000 BCE (ends {period['end_year']}) - {period['label']}")
            continue
        
        # All validations passed
        period_count += 1
        primary_facet = period.get('primary_facet', 'Unknown')
        print(f"      ✅ INCLUDED [{period_count}]: {period['label']}")
        print(f"         Primary Facet: {primary_facet}")
        print(f"         Dates: {period.get('start_year')} to {period.get('end_year')}")
        print(f"         Locations: {len(period.get('location_qids', set()))} place(s)")
        
        # Start period block
        qid = period['qid']
        label = period['label'].replace("'", "''")  # Escape apostrophes
        
        block = [f"MERGE (p:Period {{qid: '{qid}'}})"]
        block.append(f"SET p.label = '{label}'")
        
        # Add years if available
        if period.get('start_year'):
            block.append(f"SET p.start_year = {period['start_year']}")
            block.append(f"MERGE (start:Year {{value: {period['start_year']}}})")
            block.append("MERGE (p)-[:STARTS_IN]->(start)")
        
        if period.get('end_year'):
            block.append(f"SET p.end_year = {period['end_year']}")
            block.append(f"MERGE (end:Year {{value: {period['end_year']}}})")
            block.append("MERGE (p)-[:ENDS_IN]->(end)")
        
        # Requirement 4: Add PRIMARY facet relationship (only one)
        facet_type = period.get('primary_facet', 'CulturalFacet')
        if not facet_type:
            facet_type = 'CulturalFacet'  # Fallback
        
        # Create facet node with proper structure
        facet_label = facet_type.replace('Facet', '').lower()
        # Use unique_id for facet nodes
        facet_unique_id = f"{facet_type.upper()}_{facet_label.upper().replace(' ', '_')}"
        block.append(f"MERGE (f:{facet_type}:Facet {{unique_id: '{facet_unique_id}'}})")
        block.append(f"SET f.label = '{facet_label}'")
        
        # Create PRIMARY facet relationship - use schema pattern: HAS_[FACET_TYPE]_FACET
        # e.g., HAS_POLITICAL_FACET, HAS_CULTURAL_FACET
        relationship = f"HAS_{facet_type.upper().replace('FACET', '')}_FACET"
        block.append(f"MERGE (p)-[:{relationship}]->(f)")
        
        # Requirement 5: Add ALL locations (Place nodes) - periods can span multiple geographic areas
        location_qids = period.get('location_qids', set())
        for i, location_qid in enumerate(sorted(location_qids)):
            var_name = f"geo{i}" if i > 0 else "geo"
            block.append(f"MERGE ({var_name}:Place {{qid: '{location_qid}'}})")
            block.append(f"MERGE (p)-[:LOCATED_IN]->({var_name})")
        
        # Join block with semicolons
        lines.append('; '.join(block) + ';')
        lines.append('')  # Blank line between periods
    
    # Write to file
    with open(str(output_file), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n✅ Generated {output_file}")
    print(f"   Total periods included: {period_count}")

def main():
    # Find project root (where Subjects folder is located)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent  # Go up to project root
    
    input_file = project_root / "Subjects" / "periods_import.cypher"
    output_file = project_root / "Subjects" / "periods_import_enriched.cypher"
    
    print("="*80)
    print("Enriching Periods with Perplexity Analysis")
    print("="*80)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    # Verify input file exists
    if not Path(input_file).exists():
        print(f"\n❌ ERROR: Input file not found: {input_file}")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Script location: {Path(__file__).resolve()}")
        sys.exit(1)
    
    print()
    
    # Parse periods
    print("📊 Step 1: Parsing periods from Cypher file...")
    periods = parse_periods_from_cypher(input_file)
    print(f"   Found {len(periods)} periods")
    print()
    
    # Analyze each period
    print("🤖 Step 2: Analyzing periods and determining facets...")
    print("   (Note: If Perplexity API key not found, using rule-based classification)")
    print("   For each period, showing:")
    print("      - Period details (label, dates, location)")
    print("      - Facet determination (primary facet, confidence)")
    print("      - Validation status (pass/fail reasons)")
    print()
    
    analyzed_periods = []
    for i, period in enumerate(periods, 1):
        print(f"\n   [{i}/{len(periods)}] Processing: {period['label']}")
        print(f"      QID: {period['qid'][-20:]}")
        if period.get('start_year') or period.get('end_year'):
            date_range = f"{period.get('start_year', '?')} to {period.get('end_year', '?')}"
            print(f"      Dates: {date_range}")
        if period.get('location_qids'):
            location_count = len(period['location_qids'])
            print(f"      Locations: {location_count} place(s)")
        
        method_str = "Perplexity API" if hasattr(query_perplexity, '__code__') else "Rule-based"
        print(f"      → Determining primary facet ({method_str})...", end=' ', flush=True)
        
        analysis = query_perplexity(
            period['label'],
            period['qid'],
            period.get('start_year'),
            period.get('end_year')
        )
        
        period.update(analysis)
        analyzed_periods.append(period)
        
        # Show facet determination result
        primary_facet = analysis.get('primary_facet', 'None')
        confidence = analysis.get('confidence', 0.0)
        method = analysis.get('method', 'unknown')
        print(f"✓")
        print(f"      Facet Determination ({method}):")
        print(f"         Primary Facet: {primary_facet}")
        print(f"         Confidence: {confidence:.2f}")
        print(f"         Is Period: {analysis.get('is_period', False)}")
        print(f"         Is Event: {analysis.get('is_event', False)}")
        
        # Show validation status
        validation_issues = []
        if analysis.get('is_event'):
            validation_issues.append("❌ EVENT (will skip)")
        if not period.get('start_year') or not period.get('end_year'):
            validation_issues.append("❌ MISSING DATES")
        if not period.get('location_qids'):
            validation_issues.append("❌ MISSING LOCATION")
        if period.get('end_year') and period['end_year'] < -2000:
            validation_issues.append(f"❌ TOO OLD (ends {period['end_year']} BCE)")
        
        if validation_issues:
            print(f"      Validation: {' | '.join(validation_issues)}")
        else:
            print(f"      Validation: ✅ PASSED - Will be included in output")
        
        # Rate limiting
        time.sleep(0.5)
    
    print()
    
    # Generate new Cypher file
    generate_cypher(analyzed_periods, output_file)
    
    # Summary
    print()
    print("="*80)
    print("Summary")
    print("="*80)
    events_count = sum(1 for p in analyzed_periods if p.get('is_event', False))
    missing_dates_count = sum(1 for p in analyzed_periods if not p.get('is_event', False) and (not p.get('start_year') or not p.get('end_year')))
    missing_location_count = sum(1 for p in analyzed_periods if not p.get('is_event', False) and p.get('start_year') and p.get('end_year') and not p.get('location_qids'))
    too_old_count = sum(1 for p in analyzed_periods if not p.get('is_event', False) and p.get('start_year') and p.get('end_year') and p.get('location_qids') and p.get('end_year') and p['end_year'] < -2000)
    valid_periods_count = sum(1 for p in analyzed_periods if not p.get('is_event', False) and p.get('start_year') and p.get('end_year') and p.get('location_qids') and (not p.get('end_year') or p['end_year'] >= -2000))
    
    print(f"Total analyzed: {len(analyzed_periods)}")
    print(f"✅ Valid periods (with dates + location, end >= 2000 BCE): {valid_periods_count}")
    print(f"❌ Events (filtered out): {events_count}")
    print(f"❌ Missing start/end dates: {missing_dates_count}")
    print(f"❌ Missing location: {missing_location_count}")
    print(f"❌ End date before 2000 BCE: {too_old_count}")
    print()
    print(f"✅ Enriched file ready: {output_file}")
    print("="*80)

if __name__ == "__main__":
    main()

