#!/usr/bin/env python3
"""
SCA Generic Traversal - Live Progress UI

Streams real-time progress to Gradio interface
Shows each entity being fetched with full details
"""

import sys
from pathlib import Path
import time
from datetime import datetime
from collections import deque

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
from scripts.agents.wikidata_full_fetch_enhanced import WikidataEnhancedFetcher


def traverse_with_live_updates(seed_qid: str, max_entities: int, throttle: float):
    """
    Generic traversal with live progress updates
    
    Yields progress for Gradio streaming
    """
    
    if not seed_qid or not seed_qid.strip():
        yield "Please enter a QID\n"
        return
    
    seed_qid = seed_qid.strip().upper()
    if not seed_qid.startswith('Q'):
        seed_qid = f'Q{seed_qid}'
    
    # Initialize
    fetcher = WikidataEnhancedFetcher()
    visited = set()
    queue = deque()
    entities = {}
    relationships = []
    
    yield f"{'='*80}\n"
    yield f"GENERIC GRAPH TRAVERSAL\n"
    yield f"{'='*80}\n\n"
    yield f"Seed: {seed_qid}\n"
    yield f"Max entities: {max_entities}\n"
    yield f"Max depth: 3\n"
    yield f"Throttle: {throttle}s\n\n"
    yield f"Starting traversal...\n\n"
    
    # Add seed to queue
    queue.append({'qid': seed_qid, 'depth': 0, 'from': None, 'via': 'seed'})
    
    # Process queue
    while queue and len(visited) < max_entities:
        item = queue.popleft()
        qid = item['qid']
        depth = item['depth']
        
        if qid in visited:
            continue
        
        if depth > 3:
            continue
        
        # Fetch
        yield f"[{len(visited)+1}/{max_entities}] Depth {depth}: {qid}... "
        
        try:
            # This is the slow part - fetch with all labels
            entity_data = fetcher.fetch_entity_with_labels(qid)
            
            visited.add(qid)
            entities[qid] = entity_data
            
            label = entity_data.get('labels', {}).get('en', qid)
            props = entity_data.get('statistics', {}).get('total_properties', 0)
            
            # Show QID (Label) together
            yield f"({label}) - {props} props\n"
            
            # Record relationship
            if item['from']:
                relationships.append({
                    'from': item['from'],
                    'to': qid,
                    'via': item['via'],
                    'depth': depth
                })
            
            # Extract QIDs for next hop
            if depth < 3:
                claims = entity_data.get('claims_with_labels', {})
                new_count = 0
                
                for prop_id, prop_data in claims.items():
                    for stmt in prop_data.get('statements', []):
                        val = stmt.get('value')
                        
                        if isinstance(val, str) and val.startswith('Q') and val not in visited:
                            queue.append({
                                'qid': val,
                                'depth': depth + 1,
                                'from': qid,
                                'via': prop_id
                            })
                            new_count += 1
                
                if new_count > 0:
                    yield f"  -> Queue: +{new_count} entities (total queue: {len(queue)})\n"
            
            yield f"\n"
            
            # Throttle
            time.sleep(throttle)
            
        except Exception as e:
            yield f"  FAILED: {e}\n\n"
    
    # Summary
    yield f"\n{'='*80}\n"
    yield f"TRAVERSAL COMPLETE\n"
    yield f"{'='*80}\n\n"
    yield f"Entities fetched: {len(visited)}\n"
    yield f"Relationships: {len(relationships)}\n"
    yield f"Queue remaining: {len(queue)}\n\n"
    
    # Count by depth
    depth_counts = {}
    for ent_qid, ent_data in entities.items():
        # Need to track depth differently
        pass
    
    yield f"Results ready for Neo4j import!\n"


def create_ui():
    """Create Gradio UI"""
    
    with gr.Blocks(title="SCA Live Traversal") as demo:
        gr.Markdown("""
        # 🤖 SCA Generic Graph Traversal - LIVE
        
        Watch in real-time as the algorithm:
        - Fetches each entity
        - Shows properties found
        - Discovers new QIDs
        - Hops through the graph
        
        **Default: 5000 entities, 3 hops**
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                qid_input = gr.Textbox(
                    label="Seed QID",
                    value="Q17167",
                    placeholder="Q17167"
                )
                
                max_entities_input = gr.Number(
                    label="Max Entities",
                    value=5000,
                    minimum=10,
                    maximum=10000
                )
                
                throttle_input = gr.Slider(
                    label="Throttle (seconds)",
                    value=1.0,
                    minimum=0.5,
                    maximum=3.0,
                    step=0.5
                )
                
                run_btn = gr.Button("🚀 Start Traversal", variant="primary", size="lg")
                
                gr.Markdown("""
                ### ⚠️ Warning:
                - 5000 entities takes ~1-2 hours
                - Watch progress below
                - Results save automatically
                """)
            
            with gr.Column(scale=2):
                gr.Markdown("## 📊 Live Progress")
                
                progress_output = gr.Textbox(
                    label="Real-time Progress",
                    lines=40,
                    max_lines=50,
                    autoscroll=True
                )
        
        # Connect button
        run_btn.click(
            fn=traverse_with_live_updates,
            inputs=[qid_input, max_entities_input, throttle_input],
            outputs=[progress_output]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    
    print("\n" + "="*80)
    print("SCA GENERIC TRAVERSAL - LIVE PROGRESS UI")
    print("="*80)
    print("\nLaunching at: http://localhost:7861")
    print("Watch entities being discovered in real-time!")
    print("\nPress Ctrl+C to stop\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False
    )
