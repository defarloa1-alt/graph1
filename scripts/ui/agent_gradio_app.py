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
from facet_agent_framework import FacetAgentFactory, MultiAgentRouter, AgentOperationalMode, SubjectConceptAgent


# Global agent factory, router, and SCA
factory = None
router = None
sca = None  # SubjectConceptAgent for cross-domain orchestration
# Global log stream for UI updates
log_stream = []


def initialize_agents() -> Tuple[bool, str]:
    """Initialize agent system"""
    global factory, router, sca
    
    try:
        # Validate configuration
        print("\n🔧 Validating configuration...")
        print_config_status()
        validate_agent_config(require_openai=True, require_neo4j=True)
        
        # Initialize factory, router, and SCA
        print("\n🤖 Initializing agents...")
        factory = FacetAgentFactory()
        router = MultiAgentRouter(factory)
        sca = SubjectConceptAgent(factory=factory)  # Master coordinator
        
        return True, "✅ Agents initialized successfully (including SubjectConceptAgent)!"
        
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
4. For help: see md/Guides/SETUP_GUIDE.md

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
        'Prompts',
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


def ui_log_callback(message: str) -> None:
    """Callback function to capture log messages for UI streaming"""
    global log_stream
    log_stream.append(message)


def run_initialize_mode(facet_key: str, anchor_qid: str, depth: int) -> Tuple[str, str]:
    """
    Run Initialize mode for a facet agent
    
    Args:
        facet_key: Facet to initialize (e.g., 'military')
        anchor_qid: Wikidata QID to bootstrap from (e.g., 'Q17167')
        depth: Hierarchy depth (1-3)
        
    Returns:
        (status_message, log_output)
    """
    global log_stream
    log_stream = []  # Reset log
    
    if not factory:
        return "❌ Agents not initialized. Check configuration tab.", ""
    
    try:
        # Get agent
        agent = factory.get_agent(facet_key)
        
        # Run initialize mode
        result = agent.execute_initialize_mode(
            anchor_qid=anchor_qid,
            depth=depth,
            auto_submit_claims=False,  # Don't auto-submit in smoke test
            ui_callback=ui_log_callback
        )
        
        # Format results
        if result['status'] == 'INITIALIZED':
            status = f"""
✅ Initialize Mode Complete!

**Session:** {result['session_id']}
**Anchor:** {result.get('anchor_label', 'Unknown')} ({result['anchor_qid']})

**Results:**
- Nodes created: {result['nodes_created']}
- Relationships discovered: {result['relationships_discovered']}
- Claims generated: {result['claims_generated']}
- Claims submitted: {result['claims_submitted']}

**Quality Metrics:**
- Completeness score: {result['completeness_score']:.1%}
- CIDOC-CRM class: {result['cidoc_crm_class']}
- CIDOC confidence: {result['cidoc_crm_confidence']}

**Performance:**
- Duration: {result['duration_seconds']:.1f} seconds
- Log file: {result['log_file']}

🎯 Status: {result['status']}
"""
        else:
            status = f"""
❌ Initialize Mode Failed

**Status:** {result['status']}
**Error:** {result.get('error', result.get('reason', 'Unknown error'))}

**Log file:** {result.get('log_file', 'N/A')}
"""
        
        # Format log output
        log_output = "\n".join(log_stream) if log_stream else "No log output captured"
        
        return status, log_output
        
    except Exception as e:
        return f"❌ Error: {str(e)}", "\n".join(log_stream)


def run_subject_ontology_proposal(facet_key: str) -> Tuple[str, str]:
    """
    Propose subject ontology after Initialize mode
    
    Args:
        facet_key: Facet to propose ontology for (e.g., 'military')
        
    Returns:
        (status_message, log_output)
    """
    global log_stream
    log_stream = []  # Reset log
    
    if not factory:
        return "❌ Agents not initialized. Check configuration tab.", ""
    
    try:
        # Get agent
        agent = factory.get_agent(facet_key)
        
        # Run subject ontology proposal
        result = agent.propose_subject_ontology(ui_callback=ui_log_callback)
        
        # Format results
        if result['status'] == 'ONTOLOGY_PROPOSED':
            # Build ontology class details
            classes_detail = ""
            for cls in result.get('ontology_classes', []):
                classes_detail += f"\n- **{cls['class_name']}**"
                if cls.get('member_count'):
                    classes_detail += f" ({cls['member_count']} members)"
                if cls.get('characteristics'):
                    classes_detail += f"\n  Characteristics: {', '.join(cls['characteristics'][:3])}"
                if cls.get('examples'):
                    classes_detail += f"\n  Examples: {', '.join(cls['examples'])}"
            
            # Build relationships
            rels_detail = ""
            for rel in result.get('relationships', [])[:5]:
                rels_detail += f"\n- {rel['source']} → {rel['target']} ({rel['relationship_type']})"
            
            status = f"""
✅ Subject Ontology Proposed!

**Session:** {result['session_id']}
**Facet:** {result['facet']}

**Proposed Ontology Structure:**

**Classes:** {len(result['ontology_classes'])} classes
{classes_detail}

**Relationships:** {len(result['relationships'])} relationships
{rels_detail if result.get('relationships') else "No relationships identified"}

**Quality Metrics:**
- Hierarchy depth: {result['hierarchy_depth']}
- Strength score: {result['strength_score']:.2%}
- Clusters identified: {len(result['clusters'])}
- Claim templates: {len(result['claim_templates'])}
- Validation rules: {len(result['validation_rules'])}

**Reasoning:**
{result['reasoning']}

**Performance:**
- Duration: {result['duration_seconds']:.1f} seconds
- Log file: {result['log_file']}

🎯 Status: {result['status']}
📋 This ontology now guides Training mode claim generation
"""
        elif result['status'] == 'SKIPPED':
            status = f"""
⚠️ Subject Ontology Proposal Skipped

**Reason:** {result.get('reason', 'Unknown reason')}

📋 Initialize mode must run first to create nodes for ontology analysis.

**Run Workflow:**
1. Run Initialize mode (creates bootstrap nodes)
2. Run Subject Ontology Proposal (analyzes type hierarchies)
3. Run Training mode (uses proposed ontology for claims)
"""
        else:
            status = f"""
❌ Subject Ontology Proposal Failed

**Status:** {result['status']}
**Error:** {result.get('error', 'Unknown error')}

**Log file:** {result.get('log_file', 'N/A')}
"""
        
        # Format log output
        log_output = "\n".join(log_stream) if log_stream else "No log output captured"
        
        return status, log_output
        
    except Exception as e:
        return f"❌ Error: {str(e)}", "\n".join(log_stream)

def run_training_mode(
    facet_key: str,
    max_iterations: int,
    target_claims: int,
    min_confidence: float
) -> Tuple[str, str]:
    """
    Run Training mode for a facet agent
    
    Args:
        facet_key: Facet to train
        max_iterations: Max nodes to process
        target_claims: Target number of claims
        min_confidence: Minimum confidence threshold
        
    Returns:
        (status_message, log_output)
    """
    global log_stream
    log_stream = []  # Reset log
    
    if not factory:
        return "❌ Agents not initialized. Check configuration tab.", ""
    
    try:
        # Get agent
        agent = factory.get_agent(facet_key)
        
        # Run training mode
        result = agent.execute_training_mode(
            max_iterations=max_iterations,
            target_claims=target_claims,
            min_confidence=min_confidence,
            auto_submit_high_confidence=False,  # Don't auto-submit in smoke test
            ui_callback=ui_log_callback
        )
        
        # Format results
        if result['status'] == 'TRAINING_COMPLETE':
            status = f"""
✅ Training Mode Complete!

**Session:** {result['session_id']}

**Results:**
- Nodes processed: {result['nodes_processed']}
- Iterations: {result['iterations']}
- Claims proposed: {result['claims_proposed']}
- Claims submitted: {result['claims_submitted']}

**Quality Metrics:**
- Avg confidence: {result['avg_confidence']:.2%}
- Avg completeness: {result.get('avg_completeness', 0):.2%}

**Performance:**
- Duration: {result['duration_seconds']:.1f} seconds
- Claims per second: {result['claims_per_second']:.2f}
- Log file: {result['log_file']}

🎯 Status: {result['status']}
"""
        else:
            status = f"""
❌ Training Mode Failed

**Status:** {result['status']}
**Error:** {result.get('error', 'Unknown error')}

**Log file:** {result.get('log_file', 'N/A')}
"""
        
        # Format log output
        log_output = "\n".join(log_stream) if log_stream else "No log output captured"
        
        return status, log_output
        
    except Exception as e:
        return f"❌ Error: {str(e)}", "\n".join(log_stream)

def run_cross_domain_query(query: str, max_facets: int = 3) -> Tuple[str, str]:
    """
    Run cross-domain query using SubjectConceptAgent
    
    Args:
        query: Natural language query (e.g., "What is the relationship between a Roman senator and a mollusk?")
        max_facets: Maximum facets to query (1-5)
        
    Returns:
        (status_message, log_output)
    """
    global sca, log_stream
    
    # Reset log stream
    log_stream = []
    
    try:
        if not sca:
            return "❌ SubjectConceptAgent not initialized", ""
        
        # Execute cross-domain query
        result = sca.execute_cross_domain_query(
            query=query,
            auto_classify=True
        )
        
        # Format status message
        if result['status'] == 'SUCCESS':
            facets_queried = ', '.join(result['classification']['facets'])
            bridge_concepts = ', '.join([b['label'] for b in result['bridges']]) if result['bridges'] else 'None'
            
            status = f"""
✅ Cross-Domain Query Complete

**Query:** {query}

**Classification:**
- Facets: {facets_queried}
- Cross-domain: {'Yes' if result['classification']['cross_domain'] else 'No'}
- Reasoning: {result['classification']['reasoning']}

**Results:**
- Total nodes: {result['total_nodes']}
- Total claims: {result['total_claims']}
- Bridge claims generated: {result.get('bridge_claim_count', 0)}
- Bridge concepts: {bridge_concepts}

**Synthesized Answer:**
{result['synthesized_response']}

---

### Facet-Specific Results:

"""
            # Add each facet's results
            for facet_key, facet_result in result['facet_results'].items():
                if isinstance(facet_result, dict):
                    node_count = len(facet_result.get('nodes', []))
                    status += f"\n**{facet_key.capitalize()}:** {node_count} nodes found"
                else:
                    status += f"\n**{facet_key.capitalize()}:** Error - {str(facet_result)}"
            
        else:
            status = f"""
❌ Cross-Domain Query Failed

**Status:** {result['status']}
**Error:** {result.get('error', 'Unknown error')}
"""
        
        # Format log output (capture console output)
        log_output = f"""Cross-domain query executed.

Classification: {result.get('classification', {}).get('reasoning', 'N/A')}
Facets: {', '.join(result.get('classification', {}).get('facets', []))}
Total nodes: {result.get('total_nodes', 0)}
Bridge claims: {result.get('bridge_claim_count', 0)} (node/edge creation claims)
"""
        
        return status, log_output
        
    except Exception as e:
        return f"❌ Error: {str(e)}", f"Exception: {str(e)}"



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
        
        📖 See [SETUP_GUIDE.md](../../md/Guides/SETUP_GUIDE.md) for details
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
        
        # Tab 3: Agent Operations (STEP 5)
        with gr.Tab("⚙️ Agent Operations"):
            gr.Markdown("""
            ## Agent Operational Modes (Step 5 - Smoke Test)
            
            Test the agent operational workflows:
            - **Initialize Mode**: Bootstrap new domain from Wikidata
            - **Training Mode**: Extended iterative claim generation
            
            **Purpose:** Validate agent behavior with verbose logging for system validation.
            """)
            
            # Initialize Mode Section
            with gr.Accordion("🚀 Initialize Mode", open=True):
                gr.Markdown("""
                Bootstrap a new domain from a Wikidata anchor entity. Creates SubjectConcept 
                nodes, discovers hierarchy, and generates foundational claims.
                
                **Example anchors:**
                - Q17167 (Roman Republic)
                - Q28048 (Battle of Pharsalus)
                - Q1747689 (Ancient Rome)
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        init_facet_selector = gr.Dropdown(
                            choices=get_available_facets(),
                            value="military",
                            label="Select Facet",
                            interactive=True
                        )
                        
                        init_qid_input = gr.Textbox(
                            label="Wikidata QID (Anchor)",
                            placeholder="Q17167",
                            value="Q17167",
                            lines=1
                        )
                        
                        init_depth_slider = gr.Slider(
                            minimum=1,
                            maximum=3,
                            value=1,
                            step=1,
                            label="Hierarchy Depth",
                            info="1=fast, 2=moderate, 3=comprehensive"
                        )
                        
                        init_run_btn = gr.Button(
                            "🚀 Run Initialize Mode",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=2):
                        init_status_output = gr.Textbox(
                            label="Status",
                            lines=20,
                            interactive=False
                        )
                
                # Log output below
                init_log_output = gr.Textbox(
                    label="Verbose Log Output (Real-time)",
                    lines=15,
                    interactive=False,
                    max_lines=50
                )
                
                init_run_btn.click(
                    fn=run_initialize_mode,
                    inputs=[init_facet_selector, init_qid_input, init_depth_slider],
                    outputs=[init_status_output, init_log_output]
                )
            
            # Subject Ontology Proposal Section
            with gr.Accordion("📊 Subject Ontology Proposal", open=False):
                gr.Markdown("""
                Analyze hierarchical type properties (P31 instance_of, P279 subclass_of, P361 part_of)
                discovered during Initialize mode to propose a coherent subject ontology.
                
                This ontology structure guides Training mode claim generation and provides the 
                conceptual framework for the facet.
                
                **Workflow:**
                1. Run Initialize mode first (creates bootstrap nodes)
                2. Run Subject Ontology Proposal (analyzes type hierarchies)
                3. Run Training mode (generates claims using proposed ontology)
                
                **Output:** Proposed classes, relationships, claim templates, and validation rules
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        onto_facet_selector = gr.Dropdown(
                            choices=get_available_facets(),
                            value="military",
                            label="Select Facet",
                            interactive=True
                        )
                        
                        onto_run_btn = gr.Button(
                            "📊 Propose Subject Ontology",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=2):
                        onto_status_output = gr.Textbox(
                            label="Status",
                            lines=25,
                            interactive=False
                        )
                
                # Log output below
                onto_log_output = gr.Textbox(
                    label="Verbose Log Output (Real-time)",
                    lines=15,
                    interactive=False,
                    max_lines=50
                )
                
                onto_run_btn.click(
                    fn=run_subject_ontology_proposal,
                    inputs=[onto_facet_selector],
                    outputs=[onto_status_output, onto_log_output]
                )
            
            # Training Mode Section
            with gr.Accordion("🏋️ Training Mode", open=False):
                gr.Markdown("""
                Extended iterative claim generation. Processes existing SubjectConcept nodes,
                fetches Wikidata enrichment, validates quality, and proposes claims systematically.
                
                **Prerequisites:** At least a few nodes in the graph (use Initialize mode first).
                """)
                
                with gr.Row():
                    with gr.Column(scale=1):
                        train_facet_selector = gr.Dropdown(
                            choices=get_available_facets(),
                            value="military",
                            label="Select Facet",
                            interactive=True
                        )
                        
                        train_iterations_slider = gr.Slider(
                            minimum=5,
                            maximum=100,
                            value=20,
                            step=5,
                            label="Max Iterations",
                            info="Max nodes to process"
                        )
                        
                        train_target_slider = gr.Slider(
                            minimum=10,
                            maximum=500,
                            value=100,
                            step=10,
                            label="Target Claims",
                            info="Stop after this many claims"
                        )
                        
                        train_confidence_slider = gr.Slider(
                            minimum=0.5,
                            maximum=1.0,
                            value=0.80,
                            step=0.05,
                            label="Min Confidence",
                            info="Minimum confidence threshold"
                        )
                        
                        train_run_btn = gr.Button(
                            "🏋️ Run Training Mode",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=2):
                        train_status_output = gr.Textbox(
                            label="Status",
                            lines=20,
                            interactive=False
                        )
                
                # Log output below
                train_log_output = gr.Textbox(
                    label="Verbose Log Output (Real-time)",
                    lines=15,
                    interactive=False,
                    max_lines=50
                )
                
                train_run_btn.click(
                    fn=run_training_mode,
                    inputs=[
                        train_facet_selector,
                        train_iterations_slider,
                        train_target_slider,
                        train_confidence_slider
                    ],
                    outputs=[train_status_output, train_log_output]
                )
            
            # Smoke Test Guidance
            with gr.Accordion("📋 Smoke Test Checklist", open=False):
                gr.Markdown("""
                ## Step 5 Smoke Test Validation
                
                ### Initialize Mode Checklist:
                - [ ] Session ID generated correctly
                - [ ] Wikidata entity fetched successfully
                - [ ] Completeness validation runs (Step 3.5)
                - [ ] CIDOC-CRM alignment applied (Step 4)
                - [ ] Nodes created in Neo4j
                - [ ] Hierarchy discovered via P31/P279/P361
                - [ ] Claims generated with confidence scores
                - [ ] Log file created and readable
                - [ ] Verbose logging shows reasoning
                
                ### Subject Ontology Proposal Checklist:
                - [ ] Runs after Initialize mode (has initialized nodes)
                - [ ] Loads session context correctly
                - [ ] Extracts P31/P279/P361 type hierarchies
                - [ ] Identifies conceptual clusters via LLM
                - [ ] Proposes ontology classes and relationships
                - [ ] Generates claim templates for Training mode
                - [ ] Defines validation rules
                - [ ] Calculates strength score (0-1)
                - [ ] Returns structured ontology output
                - [ ] Log shows hierarchical analysis
                
                ### Training Mode Checklist:
                - [ ] Session context loaded (Step 2)
                - [ ] Uses proposed ontology to guide claim generation
                - [ ] Existing nodes iterated systematically
                - [ ] Wikidata enrichment per node
                - [ ] Completeness validation per node
                - [ ] CIDOC-CRM alignment per node
                - [ ] Claims generated from statements
                - [ ] CRMinf belief tracking on claims (Step 4)
                - [ ] Metrics calculated (claims/sec, avg confidence)
                - [ ] Log shows reasoning for each decision
                - [ ] Graceful error handling
                
                ### Log File Validation:
                - [ ] Timestamps on every line
                - [ ] Action categories labeled
                - [ ] Reasoning steps logged
                - [ ] Query executions tracked
                - [ ] Errors captured with context
                - [ ] Session summary at end
                
                ### Performance Validation:
                - [ ] Initialize completes in <60s (depth=1)
                - [ ] Subject Ontology Proposal completes in <30s
                - [ ] Training processes ≥5 nodes/minute
                - [ ] No memory leaks during extended training
                - [ ] Neo4j connection stable
                - [ ] Log file doesn't exceed 10MB
                """)
        
        # Tab 4: Cross-Domain Queries (SubjectConceptAgent)
        with gr.Tab("🌐 Cross-Domain"):
            gr.Markdown("""
            ## SubjectConceptAgent (SCA) - Master Coordinator
            
            The SCA orchestrates multiple facet agents to answer **cross-domain queries** that span multiple domains.
            
            **Example Query:**
            - "What is the relationship between a Roman senator and a mollusk?"
              - → Queries: political (senator), scientific (mollusk), cultural (purple dye)
              - → Bridge claims: NODE_CREATION for "Tyrian purple", EDGE_CREATION linking domains
              - → Answer: Senators wore purple togas dyed with murex snail extract
            
            **How it works:**
            1. LLM classifies which facets are needed (from canonical 17)
            2. SCA simulates SubjectFacetAgents (SFAs) for smoke test validation
            3. SFAs return simulated domain-specific results
            4. SCA generates bridge CLAIMS (node/edge creation) connecting domains
            5. LLM synthesizes a coherent answer
            
            **Note:** Currently using SIMULATED agents for smoke test. Production will spawn real agents.
            
            **Try these cross-domain queries:**
            - "How did environmental disasters affect military campaigns?"
            - "What was the economic impact of religious institutions?"
            - "How did intellectual movements influence political reforms?"
            
            **Canonical 17 Facets:**
            archaeological, artistic, cultural, demographic, diplomatic, economic, environmental,
            geographic, intellectual, linguistic, military, political, religious, scientific,
            social, technological, communication
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### Cross-Domain Query")
                    
                    cross_query_input = gr.Textbox(
                        label="Query",
                        placeholder="What is the relationship between a Roman senator and a mollusk?",
                        lines=3,
                        info="Ask a question that spans multiple domains"
                    )
                    
                    with gr.Row():
                        cross_max_facets = gr.Slider(
                            minimum=1,
                            maximum=5,
                            value=3,
                            step=1,
                            label="Max Facets",
                            info="Maximum number of domains to query"
                        )
                    
                    cross_run_btn = gr.Button("🌐 Run Cross-Domain Query", variant="primary", size="lg")
                    
                    gr.Markdown("""
                    **Note:** Cross-domain queries use GPT-4 for classification and synthesis, 
                    so they may take 30-60 seconds to complete.
                    """)
                
                with gr.Column(scale=3):
                    gr.Markdown("### Results")
                    
                    cross_status_output = gr.Textbox(
                        label="Status & Synthesized Answer",
                        lines=25,
                        interactive=False,
                        show_copy_button=True
                    )
                    
                    cross_log_output = gr.Textbox(
                        label="Query Log",
                        lines=10,
                        max_lines=30,
                        interactive=False,
                        show_copy_button=True
                    )
            
            # Connect button to handler
            cross_run_btn.click(
                fn=run_cross_domain_query,
                inputs=[cross_query_input, cross_max_facets],
                outputs=[cross_status_output, cross_log_output]
            )
            
            with gr.Accordion("🧪 Example Queries", open=False):
                gr.Markdown("""
                ### Single-Domain Queries (Use Single Facet tab instead):
                - "What battles did Julius Caesar fight?" → military only
                - "Who were the Roman emperors?" → political only
                - "What temples were built in Rome?" → religious only
                
                ### Cross-Domain Queries (Perfect for SCA):
                - "What is the relationship between a Roman senator and a mollusk?"
                  - Domains: political, scientific, cultural
                  - Bridge claims: CREATE node "Tyrian purple", CREATE edges to senator/mollusk/dye
                
                - "How did environmental disasters affect military campaigns?"
                  - Domains: environmental, military
                  - Bridge claims: CREATE edges linking disaster events to battle outcomes
                
                - "What was the economic impact of monastery construction?"
                  - Domains: economic, religious, technological
                  - Bridge: Labor, materials, trade networks
                
                - "How did philosophical movements influence political reforms?"
                  - Domains: intellectual, political
                  - Bridge: Ideas → policy changes
                
                - "What role did trade routes play in religious expansion?"
                  - Domains: economic, geographic, religious, communication
                  - Bridge: Merchants spreading beliefs along trade paths
                
                ### Why SCA is Needed:
                Traditional single-facet agents can't answer these queries because:
                1. Each agent only knows its domain
                2. No agent can traverse cross-domain relationships alone
                3. Bridge concepts often reside in **different facets**
                
                SCA solves this by:
                1. Identifying all relevant domains (from canonical 17 facets)
                2. Simulating each domain's expert agent (smoke test mode)
                3. GENERATING CLAIMS for conceptual bridges (node/edge creation)
                4. Synthesizing a unified answer
                
                **Bridge Claims = Data Creation:**
                - NODE_CREATION: Create shared concept node (e.g., "Tyrian purple")
                - EDGE_CREATION: Link concept to nodes in multiple facets
                - NODE_MODIFICATION: Add multi-facet tags to existing nodes
                """)
        
        # Tab 5: Help
        with gr.Tab("📖 Help"):
            gr.Markdown("""
            ##How to Use
            
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
            - Run `setup_config.bat` or see md/Guides/SETUP_GUIDE.md
            
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
            - 📖 [SETUP_GUIDE.md](../../md/Guides/SETUP_GUIDE.md) - Configuration help
            - 📖 [FACET_AGENT_README.md](../../scripts/agents/FACET_AGENT_README.md) - Agent architecture
            
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
