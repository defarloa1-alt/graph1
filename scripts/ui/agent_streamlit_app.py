#!/usr/bin/env python3
"""
Chrystallum Agent UI - Streamlit Interface
Purpose: Alternative web UI using Streamlit
Date: February 15, 2026

Launch:
  pip install streamlit
  streamlit run scripts/ui/agent_streamlit_app.py

Then open: http://localhost:8501
"""

import os
import sys
import streamlit as st
import json
from typing import List

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from config_loader import validate_agent_config, print_config_status
from facet_agent_framework import FacetAgentFactory, MultiAgentRouter


# Page configuration
st.set_page_config(
    page_title="Chrystallum Agent UI",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Session state initialization
if 'factory' not in st.session_state:
    st.session_state.factory = None
if 'router' not in st.session_state:
    st.session_state.router = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'init_error' not in st.session_state:
    st.session_state.init_error = None


def initialize_agents():
    """Initialize agent system"""
    try:
        # Validate configuration
        validate_agent_config(require_openai=True, require_neo4j=True)
        
        # Initialize factory and router
        st.session_state.factory = FacetAgentFactory()
        st.session_state.router = MultiAgentRouter(st.session_state.factory)
        st.session_state.initialized = True
        st.session_state.init_error = None
        
        return True
        
    except Exception as e:
        st.session_state.initialized = False
        st.session_state.init_error = str(e)
        return False


def get_available_facets() -> List[str]:
    """Get list of available facet keys and labels"""
    facets_file = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        '..', 
        'Prompts',
        'facet_agent_system_prompts.json'
    )
    
    try:
        with open(facets_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [(f['key'], f['label']) for f in data['facets']]
    except Exception:
        # Fallback list
        return [
            ('military', 'Military'),
            ('political', 'Political'),
            ('economic', 'Economic'),
            ('religious', 'Religious'),
            ('social', 'Social'),
            ('cultural', 'Cultural'),
            ('artistic', 'Artistic'),
            ('intellectual', 'Intellectual'),
            ('linguistic', 'Linguistic'),
            ('geographic', 'Geographic'),
            ('environmental', 'Environmental'),
            ('technological', 'Technological'),
            ('demographic', 'Demographic'),
            ('diplomatic', 'Diplomatic'),
            ('scientific', 'Scientific'),
            ('archaeological', 'Archaeological'),
            ('communication', 'Communication'),
        ]


# Header
st.title("🔮 Chrystallum Knowledge Graph Agent")
st.markdown("""
Query historical data using natural language. The system generates Cypher queries 
and retrieves results from Neo4j.
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Initialize agents button
    if st.button("🔄 Initialize Agents", type="primary"):
        with st.spinner("Initializing agents..."):
            initialize_agents()
    
    # Show initialization status
    if st.session_state.initialized:
        st.success("✅ Agents initialized!")
    elif st.session_state.init_error:
        st.error("❌ Configuration Error")
        with st.expander("Show Error Details"):
            st.code(st.session_state.init_error)
            st.markdown("""
            **Setup Instructions:**
            1. Copy `config.py.example` to `config.py`
            2. Add your API keys:
               - OPENAI_API_KEY
               - NEO4J_PASSWORD
            3. Or set environment variables
            4. Click "Initialize Agents" again
            
            **Quick Setup:**
            ```bash
            # Windows
            setup_config.bat
            
            # Linux/Mac
            ./setup_config.sh
            ```
            
            📖 See [SETUP_GUIDE.md](../../md/Guides/SETUP_GUIDE.md)
            """)
    else:
        st.info("👆 Click 'Initialize Agents' to start")
    
    st.divider()
    
    # Help section
    st.header("📖 Help")
    with st.expander("Quick Start"):
        st.markdown("""
        **Single Facet Mode:**
        1. Select a facet domain
        2. Type your question
        3. Click "Query"
        
        **Auto-Route Mode:**
        1. Type your question
        2. System detects relevant facets
        3. Queries multiple agents
        
        **Examples:**
        - "What battles occurred in 1066?"
        - "Show me all monasteries founded before 1100"
        - "What manuscripts were created in Oxford?"
        """)
    
    with st.expander("Available Facets"):
        facets = get_available_facets()
        for key, label in facets:
            st.markdown(f"- **{label}** (`{key}`)")
    
    with st.expander("Documentation"):
        st.markdown("""
        - [README.md](../../README.md)
        - [SETUP_GUIDE.md](../../md/Guides/SETUP_GUIDE.md)
        - [FACET_AGENT_README.md](../../scripts/agents/FACET_AGENT_README.md)
        """)


# Main content area
if not st.session_state.initialized:
    st.warning("⚠️ Agents not initialized. Use the sidebar to configure and initialize.")
    st.stop()


# Mode selection
mode = st.radio(
    "Select Mode:",
    ["🎯 Single Facet", "🔍 Auto-Route"],
    horizontal=True
)

st.divider()


# Mode 1: Single Facet Query
if mode == "🎯 Single Facet":
    st.subheader("Single Facet Query")
    st.markdown("Query a specific domain expert agent.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Facet selector
        facets = get_available_facets()
        facet_labels = {label: key for key, label in facets}
        
        selected_label = st.selectbox(
            "Select Facet:",
            options=list(facet_labels.keys()),
            index=0
        )
        selected_key = facet_labels[selected_label]
        
        # Query input
        user_query = st.text_area(
            "Your Question:",
            placeholder="Example: What military campaigns occurred in 1066?",
            height=100
        )
        
        # Query button
        query_btn = st.button("🔍 Query Facet", type="primary")
    
    with col2:
        st.markdown("**Example Queries:**")
        examples = {
            'military': "What battles occurred in 1066?",
            'political': "Who was king of England in 1066?",
            'religious': "Find all monasteries founded before 1100",
            'intellectual': "Show me manuscripts from Oxford",
        }
        
        if selected_key in examples:
            st.info(f"💡 Try: {examples[selected_key]}")
    
    # Execute query
    if query_btn and user_query:
        with st.spinner(f"Querying {selected_label} agent..."):
            try:
                agent = st.session_state.factory.get_agent(selected_key)
                results = agent.query(user_query)
                
                st.success("✅ Query complete!")
                st.divider()
                st.markdown("### Results")
                st.text(results)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try rephrasing your question or selecting a different facet.")


# Mode 2: Auto-Route Query
elif mode == "🔍 Auto-Route":
    st.subheader("Auto-Route Query")
    st.markdown("Let AI automatically detect which facets are relevant.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Query input
        user_query = st.text_area(
            "Your Question:",
            placeholder="Example: What happened during the Norman Conquest?",
            height=100
        )
        
        # Max facets slider
        max_facets = st.slider(
            "Max Facets to Query:",
            min_value=1,
            max_value=5,
            value=3,
            help="More facets = more comprehensive but slower"
        )
        
        # Query button
        query_btn = st.button("🔍 Auto-Route Query", type="primary")
    
    with col2:
        st.markdown("**Example Queries:**")
        st.info("💡 What happened during the Norman Conquest?")
        st.info("💡 Tell me about medieval monasteries in England")
        st.info("💡 What technological advances in the 13th century?")
    
    # Execute query
    if query_btn and user_query:
        with st.spinner("Detecting relevant facets..."):
            try:
                # Route query
                facets = st.session_state.router.route_query(user_query, max_facets=max_facets)
                
                if not facets:
                    st.error("❌ No relevant facets detected. Try a more specific question.")
                else:
                    st.success(f"✅ Detected {len(facets)} relevant facet(s): {', '.join(facets)}")
                    
                    st.divider()
                    st.markdown("### Results")
                    
                    # Query each facet
                    for facet_key in facets:
                        agent = st.session_state.factory.get_agent(facet_key)
                        
                        with st.expander(f"**{agent.facet_label} Facet**", expanded=True):
                            with st.spinner(f"Querying {agent.facet_label}..."):
                                results = agent.query(user_query)
                                st.text(results)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
<b>Chrystallum Knowledge Graph</b> | Phase 2.5 Multi-Agent Framework | February 2026
</div>
""", unsafe_allow_html=True)
