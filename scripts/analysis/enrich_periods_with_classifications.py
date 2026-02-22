#!/usr/bin/env python3
"""
Enrich Historical Periods with Classifications

For each of the 89 historical periods, fetch:
- P31 (instance of) with values and labels
- P279 (subclass of) with values and labels
- P361 (part of) with values and labels

Shows how each period breaks down further.
"""

import sys
from pathlib import Path
import json
import requests
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class PeriodClassificationEnricher:
    """Enrich periods with classification properties"""
    
    def __init__(self):
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        
    def enrich_periods(self, periods: list) -> list:
        """
        Enrich all periods with P31, P279, P361
        
        Args:
            periods: List of period dicts with qid and label
        
        Returns:
            Enriched list with classifications
        """
        
        print(f"\n{'='*80}")
        print(f"ENRICHING {len(periods)} PERIODS WITH CLASSIFICATIONS")
        print(f"{'='*80}\n")
        
        enriched = []
        
        for i, period in enumerate(periods):
            qid = period['qid']
            label = period['label']
            
            print(f"[{i+1}/{len(periods)}] {qid} ({label})...", end=" ")
            
            try:
                classifications = self._fetch_classifications(qid)
                
                enriched_period = {
                    **period,
                    'P31_instance_of': classifications['P31'],
                    'P279_subclass_of': classifications['P279'],
                    'P361_part_of': classifications['P361']
                }
                
                enriched.append(enriched_period)
                
                # Show counts
                counts = f"P31:{len(classifications['P31'])} P279:{len(classifications['P279'])} P361:{len(classifications['P361'])}"
                print(f"OK - {counts}")
                
            except Exception as e:
                print(f"FAILED - {e}")
                enriched.append({
                    **period,
                    'P31_instance_of': [],
                    'P279_subclass_of': [],
                    'P361_part_of': [],
                    'error': str(e)
                })
        
        return enriched
    
    def _fetch_classifications(self, qid: str) -> dict:
        """Fetch P31, P279, P361 for a QID"""
        
        # Fetch entity data
        url = self.entity_url.format(qid=qid)
        
        response = requests.get(url, headers={
            'User-Agent': 'Chrystallum/1.0 (research project)'
        })
        response.raise_for_status()
        
        data = response.json()
        entity = data.get('entities', {}).get(qid, {})
        claims = entity.get('claims', {})
        
        # Collect QIDs from claims
        all_qids = set()
        
        p31_values = []
        for claim in claims.get('P31', []):
            value_qid = claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
            if value_qid:
                p31_values.append(value_qid)
                all_qids.add(value_qid)
        
        p279_values = []
        for claim in claims.get('P279', []):
            value_qid = claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
            if value_qid:
                p279_values.append(value_qid)
                all_qids.add(value_qid)
        
        p361_values = []
        for claim in claims.get('P361', []):
            value_qid = claim.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id')
            if value_qid:
                p361_values.append(value_qid)
                all_qids.add(value_qid)
        
        # Fetch labels for all QIDs
        labels = self._fetch_labels(list(all_qids))
        
        # Build result with labels
        classifications = {
            'P31': [{'qid': q, 'label': labels.get(q, q)} for q in p31_values],
            'P279': [{'qid': q, 'label': labels.get(q, q)} for q in p279_values],
            'P361': [{'qid': q, 'label': labels.get(q, q)} for q in p361_values]
        }
        
        return classifications
    
    def _fetch_labels(self, qids: list) -> dict:
        """Fetch labels for QIDs"""
        
        if not qids:
            return {}
        
        # Batch in groups of 50
        all_labels = {}
        
        for i in range(0, len(qids), 50):
            batch = qids[i:i+50]
            
            params = {
                'action': 'wbgetentities',
                'ids': '|'.join(batch),
                'props': 'labels',
                'languages': 'en',
                'format': 'json'
            }
            
            response = requests.get(self.api_url, params=params, headers={
                'User-Agent': 'Chrystallum/1.0 (research project)'
            })
            response.raise_for_status()
            
            data = response.json()
            
            for entity_id, entity in data.get('entities', {}).items():
                label = entity.get('labels', {}).get('en', {}).get('value', entity_id)
                all_labels[entity_id] = label
        
        return all_labels
    
    def save_enriched(self, enriched: list, output_filename: str = None):
        """Save enriched data"""
        
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"output/analysis/periods_enriched_{timestamp}.json"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enriched, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved: {output_path}")
        
        return str(output_path)
    
    def generate_enriched_chart(self, enriched: list, output_filename: str = None):
        """Generate markdown chart with classifications"""
        
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"output/analysis/periods_enriched_chart_{timestamp}.md"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = []
        lines.append("# 89 Historical Periods - Enriched with Classifications\n")
        lines.append("**Properties:** P31 (instance of), P279 (subclass of), P361 (part of)\n")
        lines.append("---\n\n")
        
        for i, period in enumerate(enriched, 1):
            qid = period['qid']
            label = period['label']
            
            lines.append(f"## {i}. {qid} - {label}\n\n")
            
            # P31 instance of
            p31_list = period.get('P31_instance_of', [])
            if p31_list:
                lines.append("**P31 (instance of):**\n")
                for item in p31_list:
                    lines.append(f"- {item['qid']} ({item['label']})\n")
                lines.append("\n")
            else:
                lines.append("**P31 (instance of):** None\n\n")
            
            # P279 subclass of
            p279_list = period.get('P279_subclass_of', [])
            if p279_list:
                lines.append("**P279 (subclass of):**\n")
                for item in p279_list:
                    lines.append(f"- {item['qid']} ({item['label']})\n")
                lines.append("\n")
            else:
                lines.append("**P279 (subclass of):** None\n\n")
            
            # P361 part of
            p361_list = period.get('P361_part_of', [])
            if p361_list:
                lines.append("**P361 (part of):**\n")
                for item in p361_list:
                    lines.append(f"- {item['qid']} ({item['label']})\n")
                lines.append("\n")
            else:
                lines.append("**P361 (part of):** None\n\n")
            
            lines.append("---\n\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(lines))
        
        print(f"Chart saved: {output_path}")
        
        return str(output_path)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    # Load the triaged periods
    if len(sys.argv) > 1:
        triage_file = sys.argv[1]
    else:
        triage_file = "output/backlinks/backlinks_triage_20260220_173458.json"
    
    print(f"Loading triaged periods from: {triage_file}")
    
    with open(triage_file, 'r', encoding='utf-8') as f:
        triage_data = json.load(f)
    
    periods = triage_data.get('periods', [])
    
    print(f"  Found {len(periods)} periods to enrich")
    
    # Enrich
    enricher = PeriodClassificationEnricher()
    enriched = enricher.enrich_periods(periods)
    
    # Save JSON
    json_path = enricher.save_enriched(enriched)
    
    # Generate chart
    chart_path = enricher.generate_enriched_chart(enriched)
    
    print(f"\n{'='*80}")
    print(f"ENRICHMENT COMPLETE")
    print(f"{'='*80}\n")
    print(f"JSON: {json_path}")
    print(f"Chart: {chart_path}")


if __name__ == "__main__":
    main()
