#!/usr/bin/env python3
"""
Chrystallum Agent UI - Gradio Interface
Purpose: Simple web UI for facet agents
Date: February 15, 2026

Launch:
  pip install gradio
  python scripts/ui/agent_gradio_app.py

Then open: http://localhost:7860
"""

import os
import sys
import gradio as gr
import json
from typing import List, Tuple

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from config_loader import validate_agent_config, print_config_status
from facet_agent_framework import FacetAgentFactory, MultiAgentRouter


# Global agent factory and router
factory = None
router = None


def initialize_agents() -> Tuple[bool, str]:
    """Initialize agent system"""
    global factory, router
    
    try:
        # Validate configuration
        print("\n🔧 Validating configuration...")
        print_config_status()
        validate_agent_config(require_openai=True, require_neo4j=True)
        
        # Initialize factory and router
        print("\n🤖 Initializing agents...")
        factory = FacetAgentFactory()
        router = MultiAgentRouter(factory)
        
        return True, "✅ Agents initialized successfully!"
        
    except Exception as e:
        error_msg = f"""
❌ Configuration Error:

{str(e)}

📝 Setup Instructions:
1. Copy config.py.example to config.py
2. Add your API keys:
   - OPENAI_API_KEY
   - NEO4J_PASSWORD
3. Or set environment variables
4. For help: see SETUP_GUIDE.md

Quick setup: run setup_config.bat (Windows) or ./setup_config.sh (Linux)
"""
        return False, error_msg


def query_single_facet(user_query: str, facet_key: str) -> str:
    """
    Query a specific facet agent
    
    Args:
        user_query: Natural language question
        facet_key: Facet identifier (e.g., 'military', 'political')
        
    Returns:
        Formatted results
    """
    if not factory:
        return "❌ Agents not initialized. Check configuration tab."
    
    try:
        agent = factory.get_agent(facet_key)
        results = agent.query(user_query)
        return results
        
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nCypher query may have failed. Try rephrasing."


def query_auto_route(user_query: str, max_facets: int = 3) -> str:
    """
    Auto-route query to relevant facets
    
    Args:
        user_query: Natural language question
        max_facets: Maximum number of facets to query
        
    Returns:
        Combined results from all relevant facets
    """
    if not router:
        return "❌ Agents not initialized. Check configuration tab."
    
    try:
        # Detect relevant facets
        print(f"\n🔍 Auto-routing query: {user_query}")
        facets = router.route_query(user_query, max_facets=max_facets)
        
        if not facets:
            return "❌ No relevant facets detected. Try a more specific question."
        
        # Query each facet
        results = []
        for facet_key in facets:
            agent = factory.get_agent(facet_key)
            facet_results = agent.query(user_query)
            results.append(f"## {agent.facet_label} Facet\n\n{facet_results}\n")
        
        # Combine results
        header = f"🔍 Queried {len(facets)} facet(s): {', '.join(facets)}\n\n"
        return header + "\n---\n\n".join(results)
        
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_available_facets() -> List[str]:
    """Get list of available facet keys"""
    facets_file = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        '..', 
        'facet_agent_system_prompts.json'
    )
    
    try:
        with open(facets_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [facet['key'] for facet in data['facets']]
    except Exception:
        # Fallback list
        return [
            'military', 'political', 'economic', 'religious', 'social',
            'cultural', 'artistic', 'intellectual', 'linguistic', 'geographic',
            'environmental', 'technological', 'demographic', 'diplomatic',
            'scientific', 'archaeological', 'communication'
        ]


# Initialize on startup
init_success, init_message = initialize_agents()


# Build Gradio interface
with gr.Blocks(
    title="Chrystallum Agent UI",
    theme=gr.themes.Soft()
) as demo:
    
    gr.Markdown("""
    # 🔮 Chrystallum Knowledge Graph Agent
    
    Query historical data using natural language. The system will generate Cypher queries 
    and retrieve results from Neo4j.
    
    **Two modes:**
    - 🎯 **Single Facet:** Query a specific domain (military, political, etc.)
    - 🔍 **Auto-Route:** Let AI detect relevant facets automatically
    """)
    
    # Configuration status
    with gr.Accordion("⚙️ Configuration Status", open=not init_success):
        config_status = gr.Textbox(
            value=init_message,
            label="System Status",
            lines=10,
            interactive=False
        )
        
        gr.Markdown("""
        **Quick Setup:**
        ```bash
        # Windows
        setup_config.bat
        
        # Linux/Mac
        ./setup_config.sh
        ```
        
        **Manual Setup:**
        1. Copy `config.py.example` to `config.py`
        2. Add your API keys (OPENAI_API_KEY, NEO4J_PASSWORD)
        3. Restart this UI
        
        📖 See [SETUP_GUIDE.md](../../SETUP_GUIDE.md) for details
        """)
    
    # Main interface tabs
    with gr.Tabs():
        
        # Tab 1: Single Facet Query
        with gr.Tab("🎯 Single Facet"):
            gr.Markdown("""
            Query a specific domain expert agent. Each facet understands 
            specialized terminology and relationships.
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    facet_query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Example: What military campaigns occurred in 1066?",
                        lines=3
                    )
                    
                    facet_selector = gr.Dropdown(
                        choices=get_available_facets(),
                        value="military",
                        label="Select Facet",
                        interactive=True
                    )
                    
                    facet_query_btn = gr.Button(
                        "🔍 Query Facet", 
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=3):
                    facet_output = gr.Textbox(
                        label="Results",
                        lines=20,
                        interactive=False
                    )
            
            # Examples
            gr.Examples(
                examples=[
                    ["What battles occurred in 1066?", "military"],
                    ["Who was king of England in 1066?", "political"],
                    ["What churches were built in the 12th century?", "religious"],
                    ["Show me all monasteries founded before 1100", "religious"],
                    ["What manuscripts were created in medieval England?", "intellectual"],
                ],
                inputs=[facet_query_input, facet_selector],
            )
            
            facet_query_btn.click(
                fn=query_single_facet,
                inputs=[facet_query_input, facet_selector],
                outputs=facet_output
            )
        
        # Tab 2: Auto-Route Query
        with gr.Tab("🔍 Auto-Route"):
            gr.Markdown("""
            Let AI automatically detect which facets are relevant to your question.
            Queries up to 3 facets simultaneously for comprehensive results.
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    auto_query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Example: What happened during the Norman Conquest?",
                        lines=3
                    )
                    
                    max_facets_slider = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=3,
                        step=1,
                        label="Max Facets to Query",
                        info="More facets = more comprehensive but slower"
                    )
                    
                    auto_query_btn = gr.Button(
                        "🔍 Auto-Route Query", 
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=3):
                    auto_output = gr.Textbox(
                        label="Results",
                        lines=25,
                        interactive=False
                    )
            
            # Examples
            gr.Examples(
                examples=[
                    ["What happened during the Norman Conquest?"],
                    ["Tell me about medieval monasteries in England"],
                    ["What technological advances occurred in the 13th century?"],
                    ["Show me cultural developments in Renaissance Italy"],
                ],
                inputs=[auto_query_input],
            )
            
            auto_query_btn.click(
                fn=query_auto_route,
                inputs=[auto_query_input, max_facets_slider],
                outputs=auto_output
            )
        
        # Tab 3: Help
        with gr.Tab("📖 Help"):
            gr.Markdown("""
            ## How to Use
            
            ### Single Facet Mode
            1. Type your question in natural language
            2. Select the relevant facet domain
            3. Click "Query Facet"
            4. Results appear on the right
            
            **Available Facets:**
            - **Military:** Battles, campaigns, fortifications, armies
            - **Political:** Rulers, governments, treaties, succession
            - **Economic:** Trade, taxation, currency, markets
            - **Religious:** Churches, monasteries, clergy, theology
            - **Social:** Classes, family, gender, daily life
            - **Cultural:** Art, literature, music, customs
            - **Artistic:** Architecture, sculpture, painting
            - **Intellectual:** Philosophy, education, manuscripts
            - **Linguistic:** Languages, dialects, translation
            - **Geographic:** Places, regions, boundaries, features
            - **Environmental:** Climate, agriculture, disasters
            - **Technological:** Inventions, tools, engineering
            - **Demographic:** Population, migration, settlement
            - **Diplomatic:** Embassies, alliances, negotiations
            - **Scientific:** Discoveries, medicine, astronomy
            - **Archaeological:** Excavations, artifacts, sites
            - **Communication:** Writing, printing, roads, messengers
            
            ### Auto-Route Mode
            1. Type your question (can be broad or specific)
            2. Adjust max facets slider (default: 3)
            3. Click "Auto-Route Query"
            4. AI detects relevant facets and queries them all
            5. Combined results appear on right
            
            **When to use Auto-Route:**
            - Complex questions spanning multiple domains
            - Not sure which facet to use
            - Want comprehensive results
            - Exploratory research
            
            **When to use Single Facet:**
            - Focused domain-specific questions
            - You know the exact facet needed
            - Faster results (1 agent vs. multiple)
            - Testing specific agent behavior
            
            ## Example Queries
            
            **Military:**
            - "What battles occurred in 1066?"
            - "Show me all castles built by William the Conqueror"
            - "List military campaigns in the Hundred Years War"
            
            **Political:**
            - "Who was king of England in 1215?"
            - "What treaties were signed during the reign of Edward I?"
            
            **Religious:**
            - "Find all Benedictine monasteries founded before 1100"
            - "What bishops served in Canterbury?"
            
            **Intellectual:**
            - "Show me manuscripts from Oxford in the 13th century"
            - "What scholars taught at Paris University?"
            
            ## Technical Details
            
            - **Cypher Generation:** OpenAI GPT-3.5-turbo converts your question to Cypher
            - **Graph Query:** Cypher executes against Neo4j database
            - **Result Formatting:** Agent formats results for readability
            - **Cost:** ~$0.002 per query (OpenAI API)
            
            ## Troubleshooting
            
            **"Agents not initialized" error:**
            - Check Configuration Status tab
            - Ensure API keys are set (OPENAI_API_KEY, NEO4J_PASSWORD)
            - Run `setup_config.bat` or see SETUP_GUIDE.md
            
            **"Cypher query failed" error:**
            - Try rephrasing your question
            - Be more specific about entities (names, dates, places)
            - Check Single Facet mode if Auto-Route failed
            
            **Empty results:**
            - Data may not exist in graph for that query
            - Try broader search terms
            - Check date ranges (data currently: medieval-early modern)
            
            ## Documentation
            
            - 📖 [README.md](../../README.md) - Project overview
            - 📖 [SETUP_GUIDE.md](../../SETUP_GUIDE.md) - Configuration help
            - 📖 [FACET_AGENT_README.md](../../FACET_AGENT_README.md) - Agent architecture
            
            ## Support
            
            For issues or questions, check the documentation above or review 
            the Configuration Status tab for setup help.
            """)
    
    gr.Markdown("""
    ---
    **Chrystallum Knowledge Graph** | Phase 2.5 Multi-Agent Framework | February 2026
    """)


# Launch configuration
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔮 Chrystallum Agent UI")
    print("="*60)
    
    if init_success:
        print("✅ Agents initialized successfully!")
        print("\n📡 Launching Gradio interface...")
        print("   Open your browser to: http://localhost:7860")
    else:
        print("⚠️  Configuration incomplete - UI will show setup instructions")
        print("   You can still launch the UI to see configuration help")
    
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Launch Gradio app
    demo.launch(
        server_name="127.0.0.1",  # localhost only (secure)
        server_port=7860,
        share=False,  # Don't create public URL
        inbrowser=True,  # Auto-open browser
        show_error=True  # Show detailed errors
    )
