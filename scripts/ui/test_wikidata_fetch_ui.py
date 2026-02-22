#!/usr/bin/env python3
"""
Gradio UI for Testing Wikidata Full Fetch

Simple interface to:
1. Enter a QID
2. Fetch ALL data from Wikidata
3. Display summary
4. Save to JSON
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import gradio as gr
import json
from scripts.agents.wikidata_full_fetch import WikidataFullFetcher


def fetch_and_display(qid: str):
    """
    Fetch Wikidata entity and return formatted display
    
    Args:
        qid: Wikidata QID (e.g., Q17167)
    
    Returns:
        Tuple of (summary_text, json_data, json_filepath)
    """
    if not qid or not qid.strip():
        return "❌ Please enter a QID", "", ""
    
    fetcher = WikidataFullFetcher()
    
    try:
        # Fetch data
        data = fetcher.fetch_entity_full(qid.strip())
        
        # Build summary text
        summary = build_summary_text(data)
        
        # Convert to pretty JSON
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Save to file
        filepath = fetcher.save_to_json(data)
        
        return summary, json_str, filepath
        
    except Exception as e:
        error_msg = f"❌ ERROR fetching {qid}:\n\n{str(e)}"
        return error_msg, "", ""


def build_summary_text(data: dict) -> str:
    """Build formatted summary text for display"""
    
    stats = data['statistics']
    qid = data['qid']
    
    summary = f"""
# ✅ SUCCESSFULLY FETCHED: {qid}

---

## 📊 Statistics

- **Labels:** {stats['total_labels']} languages
- **Descriptions:** {stats['total_descriptions']} languages
- **Aliases:** {stats['total_aliases']} total
- **Properties:** {stats['total_properties']} unique
- **Total Statements:** {stats['total_statements']}
- **External IDs:** {stats['total_external_ids']} types
- **Sitelinks:** {stats['total_sitelinks']} Wikipedia articles

---

## 🏷️ Main Label (English)

**{data['labels'].get('en', 'N/A')}**

---

## 📝 Description (English)

{data['descriptions'].get('en', 'N/A')}

---

## 🔤 Aliases (English)

"""
    
    # Add aliases
    if data['aliases'].get('en'):
        for alias in data['aliases']['en'][:10]:
            summary += f"- {alias}\n"
    else:
        summary += "None\n"
    
    summary += "\n---\n\n## 🔗 External Identifiers\n\n"
    
    # Add external IDs
    if data['external_identifiers']:
        for prop_id, values in list(data['external_identifiers'].items())[:15]:
            values_str = ', '.join(str(v) for v in values[:3])
            if len(values) > 3:
                values_str += f" ... (+{len(values)-3} more)"
            summary += f"- **{prop_id}:** {values_str}\n"
    else:
        summary += "None\n"
    
    summary += "\n---\n\n## 🌐 Wikipedia Articles (Top 10)\n\n"
    
    # Add sitelinks
    if data['sitelinks']:
        for site, link_data in list(data['sitelinks'].items())[:10]:
            summary += f"- **{site}:** {link_data['title']}\n"
    else:
        summary += "None\n"
    
    summary += "\n---\n\n## 📦 Top Properties (First 20)\n\n"
    
    # Add top properties
    prop_count = 0
    for prop_id, statements in list(data['claims'].items())[:20]:
        count = len(statements)
        summary += f"- **{prop_id}:** {count} statement(s)\n"
        prop_count += 1
    
    if len(data['claims']) > 20:
        remaining = len(data['claims']) - 20
        summary += f"\n*...and {remaining} more properties*\n"
    
    summary += "\n---\n\n"
    summary += f"**Fetch completed at:** {data['fetch_timestamp']}\n"
    
    return summary


def create_ui():
    """Create Gradio UI"""
    
    with gr.Blocks(title="Wikidata Full Fetch Tester") as demo:
        gr.Markdown("""
        # 🌐 Wikidata Full Entity Fetch - Test Interface
        
        Enter a Wikidata QID to fetch **ALL** data including:
        - Labels (all languages)
        - Descriptions (all languages)
        - Aliases (all languages)
        - All properties and statements
        - External identifiers (VIAF, LCNAF, GND, etc.)
        - Wikipedia sitelinks (all languages)
        
        ---
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                qid_input = gr.Textbox(
                    label="Wikidata QID",
                    placeholder="Q17167",
                    value="Q17167",
                    info="Enter a QID (e.g., Q17167 for Roman Republic)"
                )
                
                fetch_btn = gr.Button("🚀 Fetch Complete Data", variant="primary", size="lg")
                
                gr.Markdown("""
                ### 💡 Example QIDs
                
                - **Q17167** - Roman Republic
                - **Q1048** - Julius Caesar
                - **Q1747689** - Ancient Rome
                - **Q11768** - Ancient Greece
                - **Q842606** - Second Punic War
                - **Q5916** - Hannibal
                """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📊 Summary")
                summary_output = gr.Markdown(label="Summary")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 💾 Saved File")
                filepath_output = gr.Textbox(
                    label="JSON File Path",
                    interactive=False
                )
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📄 Complete JSON Data (Click to expand)")
                json_output = gr.Code(
                    label="Full JSON",
                    language="json",
                    lines=20
                )
        
        # Event handler
        fetch_btn.click(
            fn=fetch_and_display,
            inputs=[qid_input],
            outputs=[summary_output, json_output, filepath_output]
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
