#!/usr/bin/env python3
"""
SCA Complete Domain Builder - Gradio UI

Real-time progress display with throttling for:
1. 5-hop hierarchical exploration
2. Lateral entity discovery
3. Authority checking
4. Entity type classification
5. Complete domain summary

Shows processing lines as they happen
Throttles Wikidata requests to avoid rate limits
"""

import sys
from pathlib import Path
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
from scripts.agents.sca_generic_traversal import GenericGraphTraversal


def build_domain_with_progress(seed_qid: str, throttle_seconds: float = 1.0, max_entities: int = 5000):
    """
    Build complete domain with progress updates using GENERIC TRAVERSAL
    
    Args:
        seed_qid: Starting QID
        throttle_seconds: Delay between requests
        max_entities: Maximum entities to fetch
    
    Yields:
        Progress updates (for Gradio streaming)
    """
    
    if not seed_qid or not seed_qid.strip():
        yield "Please enter a QID\n"
        return
    
    seed_qid = seed_qid.strip().upper()
    if not seed_qid.startswith('Q'):
        seed_qid = f'Q{seed_qid}'
    
    yield f"{'='*80}\n"
    yield f"GENERIC GRAPH TRAVERSAL - SCA\n"
    yield f"{'='*80}\n\n"
    yield f"Seed QID: {seed_qid}\n"
    yield f"Max entities: {max_entities}\n"
    yield f"Max depth: 3 hops\n"
    yield f"Throttle: {throttle_seconds}s\n"
    yield f"Started: {datetime.now().strftime('%H:%M:%S')}\n\n"
    yield f"This will explore ALL relationships from the seed.\n"
    yield f"Expected runtime: {max_entities * throttle_seconds / 3600:.1f} hours\n\n"
    
    # Trackers
    total_entities = 0
    total_fetches = 0
    
    fetcher = WikidataEnhancedFetcher()
    
    # ========================================================================
    # PHASE 1: FETCH SEED ENTITY
    # ========================================================================
    
    yield f"\n{'#'*80}\n"
    yield f"PHASE 1: FETCHING SEED ENTITY\n"
    yield f"{'#'*80}\n\n"
    
    try:
        yield f"Fetching {seed_qid}...\n"
        seed_data = fetcher.fetch_entity_with_labels(seed_qid)
        total_fetches += 1
        total_entities += 1
        
        seed_label = seed_data.get('labels', {}).get('en', seed_qid)
        props_count = seed_data.get('statistics', {}).get('total_properties', 0)
        
        yield f"✅ SUCCESS: {seed_label}\n"
        yield f"   Properties: {props_count}\n"
        yield f"   Labels resolved: {len(fetcher.label_cache)}\n\n"
        
        time.sleep(throttle_seconds)
        
    except Exception as e:
        yield f"❌ FAILED: {e}\n"
        return
    
    # ========================================================================
    # PHASE 2: EXTRACT KEY RELATIONSHIPS
    # ========================================================================
    
    yield f"\n{'#'*80}\n"
    yield f"PHASE 2: EXTRACTING KEY RELATIONSHIPS\n"
    yield f"{'#'*80}\n\n"
    
    claims = seed_data.get('claims_with_labels', {})
    
    # Parents (P31, P279, P361)
    parents = []
    for prop in ['P31', 'P279', 'P361']:
        if prop in claims:
            for stmt in claims[prop].get('statements', []):
                val = stmt.get('value')
                val_label = stmt.get('value_label', val)
                if val and val.startswith('Q'):
                    parents.append({'qid': val, 'label': val_label, 'via': prop})
    
    yield f"**Parents found:** {len(parents)}\n"
    for p in parents[:5]:
        yield f"  - {p['qid']} ({p['label']}) via {p['via']}\n"
    if len(parents) > 5:
        yield f"  ... and {len(parents)-5} more\n"
    yield f"\n"
    
    # Children (P527)
    children = []
    if 'P527' in claims:
        for stmt in claims['P527'].get('statements', []):
            val = stmt.get('value')
            val_label = stmt.get('value_label', val)
            if val and val.startswith('Q'):
                children.append({'qid': val, 'label': val_label})
    
    yield f"**Children found:** {len(children)}\n"
    for c in children:
        yield f"  - {c['qid']} ({c['label']})\n"
    yield f"\n"
    
    # Lateral (P36, P793, P194, P38)
    lateral = []
    for prop, label in [('P36', 'capital'), ('P793', 'events'), 
                        ('P194', 'organizations'), ('P38', 'currency')]:
        if prop in claims:
            for stmt in claims[prop].get('statements', []):
                val = stmt.get('value')
                val_label = stmt.get('value_label', val)
                if val and val.startswith('Q'):
                    lateral.append({'qid': val, 'label': val_label, 'type': label})
    
    yield f"**Lateral entities found:** {len(lateral)}\n"
    for l in lateral[:10]:
        yield f"  - {l['qid']} ({l['label']}) [{l['type']}]\n"
    if len(lateral) > 10:
        yield f"  ... and {len(lateral)-10} more\n"
    yield f"\n"
    
    # ========================================================================
    # PHASE 3: FETCH PARENTS (Sample - first 5)
    # ========================================================================
    
    yield f"\n{'#'*80}\n"
    yield f"PHASE 3: EXPLORING PARENTS (First 5)\n"
    yield f"{'#'*80}\n\n"
    
    parent_data = []
    for i, parent in enumerate(parents[:5]):
        qid = parent['qid']
        
        yield f"[{i+1}/5] Fetching {qid} ({parent['label']})...\n"
        
        try:
            p_data = fetcher.fetch_entity_with_labels(qid)
            total_fetches += 1
            total_entities += 1
            
            props = p_data.get('statistics', {}).get('total_properties', 0)
            yield f"   ✅ {props} properties\n"
            
            parent_data.append(p_data)
            
            time.sleep(throttle_seconds)
            
        except Exception as e:
            yield f"   ❌ Failed: {e}\n"
        
        yield f"\n"
    
    # ========================================================================
    # PHASE 4: FETCH LATERAL ENTITIES
    # ========================================================================
    
    yield f"\n{'#'*80}\n"
    yield f"PHASE 4: EXPLORING LATERAL ENTITIES (All)\n"
    yield f"{'#'*80}\n\n"
    
    lateral_data = []
    authorities_found = []
    
    for i, lat in enumerate(lateral):
        qid = lat['qid']
        
        yield f"[{i+1}/{len(lateral)}] {qid} ({lat['label']}) [{lat['type']}]...\n"
        
        try:
            l_data = fetcher.fetch_entity_with_labels(qid)
            total_fetches += 1
            total_entities += 1
            
            # Check for authorities
            l_claims = l_data.get('claims_with_labels', {})
            auths = []
            
            if 'P244' in l_claims:
                lcsh_val = l_claims['P244']['statements'][0].get('value')
                auths.append(f"LCSH:{lcsh_val}")
            if 'P1584' in l_claims:
                pleiades_val = l_claims['P1584']['statements'][0].get('value')
                auths.append(f"Pleiades:{pleiades_val}")
                authorities_found.append(qid)
            if 'P2163' in l_claims:
                fast_val = l_claims['P2163']['statements'][0].get('value')
                auths.append(f"FAST:{fast_val}")
            if 'P1667' in l_claims:
                tgn_val = l_claims['P1667']['statements'][0].get('value')
                auths.append(f"TGN:{tgn_val}")
            
            if auths:
                yield f"   ✅ Authorities: {', '.join(auths)}\n"
                authorities_found.append(qid)
            else:
                yield f"   ⚠️  No authorities\n"
            
            lateral_data.append(l_data)
            
            time.sleep(throttle_seconds)
            
        except Exception as e:
            yield f"   ❌ Failed: {e}\n"
        
        yield f"\n"
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    yield f"\n{'='*80}\n"
    yield f"COMPLETE DOMAIN SUMMARY\n"
    yield f"{'='*80}\n\n"
    
    yield f"**Seed:** {seed_qid} ({seed_label})\n"
    yield f"**Total entities explored:** {total_entities}\n"
    yield f"**Total API calls:** {total_fetches}\n"
    yield f"**Entities with authorities:** {len(authorities_found)}\n\n"
    
    yield f"**Breakdown:**\n"
    yield f"  - Seed: 1\n"
    yield f"  - Parents sampled: {len(parent_data)}\n"
    yield f"  - Lateral entities: {len(lateral_data)}\n"
    yield f"  - With authorities: {len(authorities_found)}\n\n"
    
    if authorities_found:
        yield f"**Entities with Authority IDs:**\n"
        for qid in authorities_found:
            entity = next((l for l in lateral if l['qid'] == qid), None)
            if entity:
                yield f"  - {qid} ({entity['label']})\n"
    
    yield f"\n**Completed:** {datetime.now().strftime('%H:%M:%S')}\n"
    yield f"\n✅ Domain building complete! Check output/sca_complete/ for full data.\n"


def create_ui():
    """Create Gradio UI"""
    
    with gr.Blocks(title="SCA Complete Domain Builder") as demo:
        gr.Markdown("""
        # 🤖 SCA Complete Domain Builder
        
        Build a complete domain from a seed QID using SCA methodology:
        - Hierarchical exploration (parents, children)
        - Lateral exploration (places, events, organizations)
        - Authority checking (LCSH, FAST, Pleiades, TGN)
        - Entity type classification
        - Real-time progress display
        
        **Note:** This can take several minutes depending on throttle setting.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                qid_input = gr.Textbox(
                    label="Seed QID",
                    placeholder="Q17167",
                    value="Q17167",
                    info="Enter a QID to build complete domain"
                )
                
                throttle_input = gr.Slider(
                    minimum=0.5,
                    maximum=5.0,
                    value=1.0,
                    step=0.5,
                    label="Throttle (seconds between requests)",
                    info="Higher = slower but safer (avoids rate limits)"
                )
                
                build_btn = gr.Button(
                    "🚀 Build Complete Domain",
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("""
                ### 💡 Recommended QIDs
                
                - **Q17167** - Roman Republic (our example)
                - **Q11772** - Ancient Greece
                - **Q12554** - Middle Ages
                - **Q361** - World War I
                - **Q7209** - Han dynasty
                
                ### ⚙️ Throttle Guide
                
                - **0.5s** - Fast, may hit rate limits
                - **1.0s** - Balanced (recommended)
                - **2.0s** - Safe, slower
                - **5.0s** - Very safe, very slow
                """)
        
        with gr.Column(scale=2):
            gr.Markdown("## 📊 Live Progress")
            
            progress_output = gr.Textbox(
                label="Processing Log",
                lines=30,
                max_lines=50,
                interactive=False
            )
        
        # Event handler
        build_btn.click(
            fn=build_domain_with_progress,
            inputs=[qid_input, throttle_input],
            outputs=[progress_output]
        )
    
    return demo


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )
