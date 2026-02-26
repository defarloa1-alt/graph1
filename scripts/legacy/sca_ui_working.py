#!/usr/bin/env python3
"""
SCA Traversal - WORKING Gradio UI with Live Streaming

FIXED: Proper streaming with accumulated text and labels on same line
"""

import sys
from pathlib import Path
import time
from datetime import datetime
from collections import deque

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import gradio as gr
from scripts.agents.wikidata_full_fetch_enhanced import WikidataEnhancedFetcher


def run_traversal_streaming(seed_qid: str, max_entities: int, throttle: float):
    """
    Run traversal with proper Gradio streaming
    
    Key: Yield ACCUMULATED text each time for Gradio to update
    """
    
    output_text = ""  # Accumulated output
    
    if not seed_qid or not seed_qid.strip():
        yield "Please enter a QID\n"
        return
    
    seed_qid = seed_qid.strip().upper()
    if not seed_qid.startswith('Q'):
        seed_qid = f'Q{seed_qid}'
    
    # Header
    output_text += "="*80 + "\n"
    output_text += "SCA GENERIC TRAVERSAL - LIVE\n"
    output_text += "="*80 + "\n\n"
    output_text += f"Seed: {seed_qid}\n"
    output_text += f"Max: {max_entities} entities\n"
    output_text += f"Throttle: {throttle}s\n\n"
    yield output_text
    
    # Initialize
    fetcher = WikidataEnhancedFetcher()
    visited = set()
    queue = deque([{'qid': seed_qid, 'depth': 0, 'from': None, 'via': 'seed'}])
    
    # Process
    while queue and len(visited) < max_entities:
        item = queue.popleft()
        qid = item['qid']
        depth = item['depth']
        
        if qid in visited or depth > 3:
            continue
        
        try:
            # Show what we're fetching
            output_text += f"[{len(visited)+1}/{max_entities}] Depth {depth}: {qid}... "
            yield output_text
            
            # Fetch
            entity_data = fetcher.fetch_entity_with_labels(qid)
            visited.add(qid)
            
            label = entity_data.get('labels', {}).get('en', qid)
            props = entity_data.get('statistics', {}).get('total_properties', 0)
            
            # Add label on SAME line
            output_text += f"({label}) - {props} props\n"
            yield output_text
            
            # Extract new QIDs
            if depth < 3:
                claims = entity_data.get('claims_with_labels', {})
                new_count = 0
                
                for prop_data in claims.values():
                    for stmt in prop_data.get('statements', []):
                        val = stmt.get('value')
                        if isinstance(val, str) and val.startswith('Q') and val not in visited:
                            queue.append({'qid': val, 'depth': depth+1, 'from': qid, 'via': 'prop'})
                            new_count += 1
                
                if new_count > 0:
                    output_text += f"  -> +{new_count} QIDs to queue (total: {len(queue)})\n"
                    yield output_text
            
            time.sleep(throttle)
            
        except Exception as e:
            output_text += f"FAILED: {e}\n"
            yield output_text
    
    # Summary
    output_text += "\n" + "="*80 + "\n"
    output_text += "COMPLETE\n"
    output_text += "="*80 + "\n"
    output_text += f"Fetched: {len(visited)} entities\n"
    output_text += f"Queue remaining: {len(queue)}\n"
    yield output_text


def create_ui():
    """Create Gradio UI"""
    
    with gr.Blocks(title="SCA Live Traversal") as demo:
        gr.Markdown("# SCA Generic Traversal - LIVE with Labels")
        
        with gr.Row():
            qid = gr.Textbox(label="Seed QID", value="Q17167")
            max_ent = gr.Number(label="Max Entities", value=5000)
            throttle = gr.Slider(label="Throttle (s)", value=1.0, minimum=0.5, maximum=3.0)
        
        btn = gr.Button("START TRAVERSAL", variant="primary", size="lg")
        
        output = gr.Textbox(label="Live Progress - QID (Label) Format", lines=35, max_lines=50)
        
        btn.click(
            fn=run_traversal_streaming,
            inputs=[qid, max_ent, throttle],
            outputs=output
        )
    
    return demo


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SCA TRAVERSAL UI - FIXED")
    print("="*80)
    print("\nURL: http://localhost:7862")
    print("Format: [#] Depth: QID... (LABEL) - props")
    print("\nPress Ctrl+C to stop\n")
    
    demo = create_ui()
    demo.launch(server_name="127.0.0.1", server_port=7862, share=False)
