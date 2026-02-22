#!/usr/bin/env python3
"""
SCA Gradio UI - FIXED with Proper Streaming

Shows hierarchy, properties, external IDs - all with labels
Streams to Gradio properly
"""

import sys
from pathlib import Path
import time
from collections import deque
import requests

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import gradio as gr


def traverse_with_streaming(seed_qid: str, max_entities: int, throttle: float):
    """
    Traverse with streaming output - yields accumulated text
    
    Shows: QID (Label), Hierarchy, External IDs - ALL WITH LABELS
    """
    
    accumulated = ""  # Must accumulate for Gradio
    
    if not seed_qid:
        yield "Enter a QID"
        return
    
    seed_qid = seed_qid.strip().upper()
    if not seed_qid.startswith('Q'):
        seed_qid = f'Q{seed_qid}'
    
    # Initialize
    api_url = "https://www.wikidata.org/w/api.php"
    entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    
    visited = set()
    queue = deque([{'qid': seed_qid, 'depth': 0}])
    label_cache = {}
    
    accumulated += "="*80 + "\n"
    accumulated += "SCA ENHANCED TRAVERSAL\n"
    accumulated += "="*80 + "\n\n"
    yield accumulated
    
    # Helper functions
    def fetch_labels(qids):
        """Fetch labels for QIDs"""
        qid_list = [q for q in qids if q not in label_cache]
        for i in range(0, len(qid_list), 50):
            batch = qid_list[i:i+50]
            params = {'action': 'wbgetentities', 'ids': '|'.join(batch), 'props': 'labels', 'languages': 'en', 'format': 'json'}
            resp = requests.get(api_url, params=params, headers={'User-Agent': 'Chrystallum/1.0'})
            data = resp.json()
            for eid, edata in data.get('entities', {}).items():
                label_cache[eid] = edata.get('labels', {}).get('en', {}).get('value', eid)
    
    def get_entity_id(claim):
        """Extract entity ID from claim"""
        dv = claim.get('mainsnak', {}).get('datavalue', {})
        if dv.get('type') == 'wikibase-entityid':
            return dv.get('value', {}).get('id', '')
        return None
    
    # Process queue
    while queue and len(visited) < max_entities:
        item = queue.popleft()
        qid = item['qid']
        depth = item['depth']
        
        if qid in visited or depth > 3:
            continue
        
        try:
            # Fetch entity (silent)
            url = entity_url.format(qid=qid)
            resp = requests.get(url, headers={'User-Agent': 'Chrystallum/1.0'})
            resp.raise_for_status()
            
            entity_data = resp.json().get('entities', {}).get(qid, {})
            label = entity_data.get('labels', {}).get('en', {}).get('value', qid)
            claims = entity_data.get('claims', {})
            
            visited.add(qid)
            
            # Show entity
            accumulated += f"\n[{len(visited)}/{max_entities}] Depth {depth}: {qid} ({label})\n"
            accumulated += "-"*80 + "\n"
            yield accumulated
            
            # Collect QIDs for labeling
            all_qids = set()
            
            # Extract parents
            parents = []
            for prop in ['P31', 'P279', 'P361']:
                if prop in claims:
                    all_qids.add(prop)
                    for claim in claims[prop][:3]:
                        val = get_entity_id(claim)
                        if val:
                            parents.append((prop, val))
                            all_qids.add(val)
            
            # Extract children  
            children = []
            for prop in ['P527']:
                if prop in claims:
                    all_qids.add(prop)
                    for claim in claims[prop]:
                        val = get_entity_id(claim)
                        if val:
                            children.append((prop, val))
                            all_qids.add(val)
                            if val not in visited:
                                queue.append({'qid': val, 'depth': depth+1})
            
            # Fetch labels
            if all_qids:
                fetch_labels(all_qids)
            
            # Show parents with labels
            if parents:
                accumulated += "PARENTS:\n"
                for prop, val in parents:
                    prop_label = label_cache.get(prop, prop)
                    val_label = label_cache.get(val, val)
                    accumulated += f"  {prop} ({prop_label}): {val} ({val_label})\n"
                    if val not in visited:
                        queue.append({'qid': val, 'depth': depth+1})
                yield accumulated
            
            # Show children with labels
            if children:
                accumulated += "CHILDREN:\n"
                for prop, val in children:
                    prop_label = label_cache.get(prop, prop)
                    val_label = label_cache.get(val, val)
                    accumulated += f"  {prop} ({prop_label}): {val} ({val_label})\n"
                yield accumulated
            
            # Show external IDs
            ext_ids = {}
            if 'P244' in claims:
                ext_ids['LCSH'] = claims['P244'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            if 'P1584' in claims:
                ext_ids['Pleiades'] = claims['P1584'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            if 'P2163' in claims:
                ext_ids['FAST'] = claims['P2163'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            if 'P1667' in claims:
                ext_ids['TGN'] = claims['P1667'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            
            if ext_ids:
                accumulated += "EXTERNAL IDs:\n"
                for id_type, id_val in ext_ids.items():
                    accumulated += f"  {id_type}: {id_val}\n"
                yield accumulated
            
            accumulated += f"Properties: {len(claims)}, Queue: {len(queue)}\n"
            yield accumulated
            
            time.sleep(throttle)
            
        except Exception as e:
            accumulated += f"FAILED: {e}\n"
            yield accumulated
    
    accumulated += f"\n{'='*80}\n"
    accumulated += f"COMPLETE: {len(visited)} entities\n"
    yield accumulated


def create_ui():
    """Create UI"""
    
    with gr.Blocks(title="SCA Enhanced") as demo:
        gr.Markdown("# SCA Enhanced Traversal - Hierarchy + Properties + External IDs")
        
        with gr.Row():
            qid = gr.Textbox(label="Seed QID", value="Q17167")
            max_ent = gr.Number(label="Max Entities", value=5000)
            throttle = gr.Slider(label="Throttle", value=1.0, minimum=0.5, maximum=3.0)
        
        btn = gr.Button("START", variant="primary", size="lg")
        output = gr.Textbox(label="Progress - Shows QID (Label) + Hierarchy + External IDs", lines=40)
        
        btn.click(fn=traverse_with_streaming, inputs=[qid, max_ent, throttle], outputs=output)
    
    return demo


if __name__ == "__main__":
    print("="*80)
    print("SCA ENHANCED TRAVERSAL UI")
    print("="*80)
    print("\nShows: Hierarchy, Properties, External IDs")
    print("All with LABELS!\n")
    print("URL: http://localhost:7863\n")
    
    demo = create_ui()
    demo.launch(server_name="127.0.0.1", server_port=7863, share=False)
