#!/usr/bin/env python3
"""
SCA Generic Traversal - Gradio UI

Simple UI that runs the generic graph traversal algorithm
Default: 5000 entities, 3 hops
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
import subprocess


def run_traversal(seed_qid: str, throttle: float = 1.0):
    """
    Run generic traversal via subprocess
    
    Returns:
        Status message
    """
    
    if not seed_qid or not seed_qid.strip():
        return "Please enter a QID"
    
    seed_qid = seed_qid.strip().upper()
    if not seed_qid.startswith('Q'):
        seed_qid = f'Q{seed_qid}'
    
    result = f"""
Starting Generic Graph Traversal...

Seed: {seed_qid}
Max entities: 5000
Max depth: 3 hops
Throttle: {throttle}s between requests

Estimated time: {5000 * throttle / 3600:.1f} hours

The traversal is running in the terminal.
Check the terminal window for live progress!

Output will be saved to:
  output/traversal/{seed_qid}_traversal_YYYYMMDD_HHMMSS.json

Once complete, you'll have thousands of entities with:
- All QIDs and labels
- All relationships
- Complete property data
- Ready for Neo4j import

Press the button again to start another traversal.
"""
    
    # Launch in subprocess
    cmd = [
        "python",
        "scripts/agents/sca_generic_traversal.py",
        seed_qid,
        "5",  # depth
        "5000",  # max entities
        str(throttle)
    ]
    
    subprocess.Popen(cmd, cwd=str(project_root))
    
    return result


def create_ui():
    """Create Gradio UI"""
    
    with gr.Blocks(title="SCA Generic Traversal") as demo:
        gr.Markdown("""
        # 🤖 SCA Generic Graph Traversal
        
        Explores EVERYTHING from a seed QID:
        - Follows ALL properties
        - Fetches ALL connected entities
        - Up to 5,000 entities by default
        - 3 hops deep
        
        **Note:** Check the terminal window for live progress!
        """)
        
        with gr.Row():
            with gr.Column():
                qid_input = gr.Textbox(
                    label="Seed QID",
                    placeholder="Q17167",
                    value="Q17167"
                )
                
                throttle_input = gr.Slider(
                    minimum=0.5,
                    maximum=3.0,
                    value=1.0,
                    step=0.5,
                    label="Throttle (seconds)"
                )
                
                run_btn = gr.Button("🚀 Start Traversal", variant="primary", size="lg")
                
                gr.Markdown("""
                ### Examples:
                - Q17167 - Roman Republic
                - Q11772 - Ancient Greece  
                - Q1747689 - Ancient Rome
                - Q12554 - Middle Ages
                
                ### Settings:
                - 5000 entities max
                - 3 hops deep
                - Progress in terminal
                """)
            
            with gr.Column():
                output = gr.Textbox(
                    label="Status",
                    lines=20,
                    interactive=False
                )
        
        run_btn.click(
            fn=run_traversal,
            inputs=[qid_input, throttle_input],
            outputs=[output]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    
    print("=" * 80)
    print("SCA GENERIC TRAVERSAL UI")
    print("=" * 80)
    print("\nLaunching Gradio at http://localhost:7860")
    print("Watch the TERMINAL for live progress when you press the button!")
    print("\nPress Ctrl+C to stop the server\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
