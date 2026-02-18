# Presentation Layer Agent Orchestrator & ESB Architecture

## Executive Summary

The **Presentation Layer Agent Orchestrator (PLAO)** extends Chrystallum's SDLC automation with an intelligent front-end layer that dynamically determines the optimal way to present information to users. It coordinates specialized sub-agents that integrate with external systems (terrain generation, 3D models, simulations) via an **Agent ESB (Enterprise Service Bus)** to deliver rich, context-appropriate content.

**Key Innovation:** Instead of fixed UI templates, the PLAO analyzes user context, role, query intent, and available data sources to orchestrate the best presentation strategy using sub-agents as intelligent adapters to external services.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│         USER (Browser/Application)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│    PRESENTATION LAYER AGENT ORCHESTRATOR (PLAO)            │
│  • Analyzes user context (role, query, viewport)           │
│  • Decides optimal presentation strategy                    │
│  • Orchestrates sub-agents via ESB                         │
│  • Composes final response (HTML, 3D, charts, etc.)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              AGENT ESB (Enterprise Service Bus)             │
│  • Routes requests to appropriate sub-agents                │
│  • Handles protocol translation (REST, gRPC, GraphQL)       │
│  • Manages authentication & rate limiting                   │
│  • Caches responses for performance                         │
│  • Monitors health & circuit breaking                       │
└──────┬──────┬──────┬──────┬──────┬──────┬──────────────────┘
       │      │      │      │      │      │
       ↓      ↓      ↓      ↓      ↓      ↓
┌──────┴┐ ┌──┴───┐ ┌┴────┐ ┌┴────┐ ┌┴────┐ ┌┴──────┐
│Terrain│ │3D Obj│ │Chart│ │Video│ │SysML│ │Code   │
│Agent  │ │Agent │ │Agent│ │Agent│ │Agent│ │Gen    │
└───┬───┘ └──┬───┘ └┬────┘ └┬────┘ └┬────┘ └┬──────┘
    │        │      │       │       │       │
    ↓        ↓      ↓       ↓       ↓       ↓
[External APIs: TerrainAPI, Blender, D3.js, FFmpeg, SysML Tools, GitHub]
```

---

## Presentation Layer Agent Orchestrator (PLAO)

### Core Responsibilities

1. **Context Analysis** - Understand user's current state
2. **Intent Recognition** - What is user trying to accomplish?
3. **Strategy Selection** - Best way to present information
4. **Sub-Agent Orchestration** - Coordinate specialized agents
5. **Response Composition** - Assemble final rich content
6. **Performance Optimization** - Cache, lazy load, prioritize

### Decision Flow

```python
class PresentationLayerOrchestrator:
    """
    Orchestrates optimal presentation strategy based on user context
    """
    
    def orchestrate_response(self, user_query: str, context: UserContext) -> Response:
        """
        Main orchestration logic
        
        Input: User query + context (role, viewport, history, preferences)
        Output: Composed response (HTML, 3D, charts, etc.)
        """
        # Step 1: Analyze context
        role = context.role  # Executive, Manager, Architect, Developer, etc.
        viewport = context.viewport  # Desktop, mobile, VR headset
        intent = self.recognize_intent(user_query)
        
        # Step 2: Query knowledge graph for data
        graph_data = self.query_neo4j(user_query, role)
        
        # Step 3: Determine presentation strategy
        strategy = self.select_strategy(
            intent=intent,
            data_type=graph_data.type,
            role=role,
            viewport=viewport
        )
        
        # Step 4: Orchestrate sub-agents via ESB
        sub_responses = []
        for task in strategy.tasks:
            response = self.esb.route(
                agent_type=task.agent,
                request=task.request,
                timeout=task.timeout
            )
            sub_responses.append(response)
        
        # Step 5: Compose final response
        final_response = self.compose(
            strategy=strategy,
            graph_data=graph_data,
            sub_responses=sub_responses
        )
        
        return final_response
```

### Context Analysis

**User Context Includes:**
```python
@dataclass
class UserContext:
    # Identity
    user_id: str
    role: str  # Executive, Manager, Architect, Developer, QA, etc.
    permissions: List[str]
    
    # Device/Viewport
    viewport: str  # desktop, mobile, tablet, vr_headset
    screen_size: Tuple[int, int]
    device_capabilities: Dict[str, bool]  # webgl, webgpu, canvas
    
    # Session
    current_graph_view: str  # Which part of graph they're viewing
    recent_queries: List[str]
    interaction_history: List[Interaction]
    
    # Preferences
    preferred_visualization: str  # 2d_graph, 3d_graph, table, timeline
    theme: str  # library, solar_system, blueprint, museum
    accessibility: Dict[str, Any]  # screen_reader, high_contrast, etc.
    
    # Performance
    network_speed: str  # fast, medium, slow
    device_performance: str  # high, medium, low
```

### Intent Recognition

**The PLAO classifies user intent into categories:**

```python
class Intent(Enum):
    # Navigation
    EXPLORE_GRAPH = "explore_graph"  # "Show me Caesar's connections"
    TRACE_REQUIREMENT = "trace_requirement"  # "Where is REQ-001 implemented?"
    FIND_PATH = "find_path"  # "How is Caesar related to Pompey?"
    
    # Analysis
    COMPARE_OPTIONS = "compare_options"  # "Lambda vs ECS for auth service"
    ANALYZE_IMPACT = "analyze_impact"  # "What breaks if I change this?"
    ASSESS_QUALITY = "assess_quality"  # "Test coverage for password reset"
    
    # Visualization
    VIEW_ARCHITECTURE = "view_architecture"  # "Show me system architecture"
    VIEW_TIMELINE = "view_timeline"  # "Timeline of Caesar's life"
    VIEW_TERRAIN = "view_terrain"  # "3D terrain of Rubicon crossing"
    VIEW_3D_MODEL = "view_3d_model"  # "Show me 3D model of Roman fort"
    
    # Creation
    CREATE_REQUIREMENT = "create_requirement"
    CREATE_ARCHITECTURE = "create_architecture"
    CREATE_TEST_CASE = "create_test_case"
    
    # Collaboration
    START_DEBATE = "start_debate"
    REVIEW_DECISION = "review_decision"
    APPROVE_MERGE = "approve_merge"

def recognize_intent(self, query: str) -> Intent:
    """
    Use LLM to classify user intent
    
    Prompt: "User query: '{query}'. Intent: ..."
    Returns: Intent enum + confidence score
    """
    prompt = f"""
    User query: "{query}"
    User role: {self.context.role}
    Current view: {self.context.current_graph_view}
    
    Classify intent (choose one):
    - explore_graph: Navigate/browse connections
    - trace_requirement: Follow requirement to code
    - view_architecture: See system structure
    - view_terrain: Geographic/spatial visualization
    - view_3d_model: 3D object rendering
    - compare_options: Side-by-side comparison
    - analyze_impact: Dependency analysis
    - create_*: User wants to add something
    - start_debate: Initiate discussion
    
    Intent:
    """
    
    response = self.llm.generate(prompt)
    return Intent(response.intent), response.confidence
```

---

## Strategy Selection

**Based on intent, data type, role, and viewport, PLAO selects presentation strategy:**

### Example Strategies

#### Strategy 1: Architect Views System Architecture

**Context:**
- Role: Architect
- Intent: VIEW_ARCHITECTURE
- Query: "Show me password reset system architecture"
- Viewport: Desktop (1920x1080)

**Selected Strategy:**
```python
{
    "strategy_id": "architecture_detailed_view",
    "layout": "three_zone",  # Sidebar + Graph + Inspector
    "primary_visualization": "block_definition_diagram",
    "tasks": [
        {
            "agent": "SysMLAgent",
            "request": {
                "operation": "render_block_diagram",
                "node_id": "ARCH-002",
                "detail_level": "full",  # Show internals
                "format": "svg"
            },
            "timeout": 5000  # 5 seconds
        },
        {
            "agent": "CodeGenAgent",
            "request": {
                "operation": "get_implementation_status",
                "block_ids": ["API_Gateway", "Auth_Service", "Email_Service"],
                "include_tests": true
            },
            "timeout": 3000
        }
    ],
    "composition": {
        "main_panel": "sysml_block_diagram",  # SVG from SysMLAgent
        "sidebar": "architecture_tree",  # Hierarchical view
        "inspector": "block_details + code_links"  # From CodeGenAgent
    }
}
```

#### Strategy 2: Executive Views OKR Progress

**Context:**
- Role: Executive
- Intent: ANALYZE_IMPACT
- Query: "Q1 security goals progress"
- Viewport: Mobile (375x812)

**Selected Strategy:**
```python
{
    "strategy_id": "executive_dashboard_mobile",
    "layout": "single_column",  # Mobile-optimized
    "primary_visualization": "progress_chart",
    "tasks": [
        {
            "agent": "ChartAgent",
            "request": {
                "operation": "render_okr_progress",
                "goal_id": "GOAL-Q1-2025-SECURITY",
                "chart_type": "donut",  # Compact for mobile
                "include_kpis": true
            },
            "timeout": 2000
        },
        {
            "agent": "GraphAgent",
            "request": {
                "operation": "trace_goal_to_code",
                "goal_id": "GOAL-Q1-2025-SECURITY",
                "depth": 3,  # Goal → Req → Arch → Code
                "status_only": true  # Just completion %
            },
            "timeout": 3000
        }
    ],
    "composition": {
        "main_panel": "donut_chart + summary_card",
        "scroll_down": "feature_list_with_status",
        "no_sidebar": true  # Mobile: full width
    }
}
```

#### Strategy 3: Historian Views Battle of Pharsalus (3D Terrain)

**Context:**
- Role: Researcher (historian)
- Intent: VIEW_TERRAIN
- Query: "Show me terrain of Battle of Pharsalus"
- Viewport: Desktop + WebGL support

**Selected Strategy:**
```python
{
    "strategy_id": "historical_terrain_3d",
    "layout": "immersive_canvas",  # Full-screen 3D
    "primary_visualization": "3d_terrain",
    "tasks": [
        {
            "agent": "TerrainAgent",
            "request": {
                "operation": "generate_terrain",
                "location": {
                    "lat": 39.2833,
                    "lon": 22.5667,
                    "bbox": [39.2, 39.4, 22.4, 22.7]  # ~20km area
                },
                "historical_period": "-48 BCE",
                "elevation_source": "dem_srtm",  # Shuttle Radar Topography Mission
                "texture": "satellite_historical_approximation",
                "format": "gltf",  # 3D model format
                "lod_levels": 3  # Level of detail
            },
            "timeout": 10000  # 10 seconds (terrain generation expensive)
        },
        {
            "agent": "3DObjectAgent",
            "request": {
                "operation": "place_objects",
                "objects": [
                    {"type": "roman_camp", "position": [39.29, 22.55, 0]},
                    {"type": "battle_lines", "positions": [...]}
                ],
                "scale": "historical_accurate"
            },
            "timeout": 5000
        },
        {
            "agent": "GraphAgent",
            "request": {
                "operation": "get_battle_context",
                "event_id": "Q48321",  # Wikidata QID for Battle of Pharsalus
                "include_sources": true
            },
            "timeout": 2000
        }
    ],
    "composition": {
        "main_panel": "webgl_3d_viewer",  # Three.js renderer
        "overlay": "battle_info_card",  # Floating info
        "controls": "orbit_camera + timeline_slider"
    }
}
```

#### Strategy 4: Developer Views Code Implementation

**Context:**
- Role: Developer
- Intent: TRACE_REQUIREMENT
- Query: "Show me code implementing password reset"
- Viewport: Desktop (VS Code embedded)

**Selected Strategy:**
```python
{
    "strategy_id": "code_traceability_view",
    "layout": "split_vertical",  # Graph left, code right
    "primary_visualization": "code_with_graph",
    "tasks": [
        {
            "agent": "GraphAgent",
            "request": {
                "operation": "trace_requirement_to_code",
                "requirement_id": "REQ-001",
                "show_path": true  # REQ → ARCH → CODE
            },
            "timeout": 2000
        },
        {
            "agent": "CodeGenAgent",
            "request": {
                "operation": "fetch_code",
                "file_path": "auth/password_reset.py",
                "annotate": true,  # Add inline comments linking to requirements
                "highlight_lines": [15, 16, 17, 30, 31]  # Lines implementing AC1, AC2
            },
            "timeout": 3000
        },
        {
            "agent": "GitAgent",
            "request": {
                "operation": "get_commit_history",
                "file_path": "auth/password_reset.py",
                "limit": 10
            },
            "timeout": 2000
        }
    ],
    "composition": {
        "left_panel": "graph_with_trace_highlighted",
        "right_panel": "code_editor_readonly",
        "bottom_panel": "commit_history + test_results"
    }
}
```

---

## Agent ESB (Enterprise Service Bus)

### Core Functions

The Agent ESB is the **routing and orchestration layer** between PLAO and specialized sub-agents.

```python
class AgentESB:
    """
    Enterprise Service Bus for agent-to-agent communication
    
    Handles:
    - Routing: Directs requests to correct sub-agent
    - Protocol translation: REST, gRPC, GraphQL, WebSocket
    - Authentication: API keys, OAuth, JWT
    - Rate limiting: Prevent abuse of external services
    - Caching: Cache expensive operations (terrain generation)
    - Circuit breaking: Fail gracefully if service down
    - Monitoring: Track latency, errors, throughput
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentAdapter] = {}
        self.cache = LRUCache(maxsize=1000)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        
    def register_agent(self, agent_type: str, adapter: AgentAdapter):
        """Register a sub-agent with the ESB"""
        self.agents[agent_type] = adapter
        self.circuit_breakers[agent_type] = CircuitBreaker(
            failure_threshold=5,
            timeout=30
        )
        self.rate_limiters[agent_type] = RateLimiter(
            requests_per_minute=60  # Configurable per agent
        )
    
    def route(self, agent_type: str, request: Dict, timeout: int) -> Response:
        """
        Route request to appropriate sub-agent
        
        Steps:
        1. Check cache
        2. Check circuit breaker (is agent healthy?)
        3. Check rate limiter
        4. Call agent adapter
        5. Cache response
        6. Return result
        """
        # Step 1: Check cache
        cache_key = self._generate_cache_key(agent_type, request)
        if cached := self.cache.get(cache_key):
            logger.info(f"Cache hit for {agent_type}: {cache_key}")
            return cached
        
        # Step 2: Circuit breaker check
        circuit_breaker = self.circuit_breakers[agent_type]
        if circuit_breaker.is_open():
            logger.warning(f"Circuit breaker OPEN for {agent_type}, returning fallback")
            return self._fallback_response(agent_type, request)
        
        # Step 3: Rate limit check
        rate_limiter = self.rate_limiters[agent_type]
        if not rate_limiter.allow():
            logger.warning(f"Rate limit exceeded for {agent_type}")
            return Response(status="rate_limited", retry_after=rate_limiter.retry_after())
        
        # Step 4: Call agent
        try:
            agent = self.agents[agent_type]
            response = agent.execute(request, timeout=timeout)
            
            # Success: reset circuit breaker
            circuit_breaker.record_success()
            
            # Step 5: Cache response
            self.cache.set(cache_key, response, ttl=request.get("cache_ttl", 300))
            
            return response
            
        except TimeoutError:
            circuit_breaker.record_failure()
            return Response(status="timeout", message=f"{agent_type} timed out")
            
        except Exception as e:
            circuit_breaker.record_failure()
            logger.error(f"Error calling {agent_type}: {e}")
            return Response(status="error", message=str(e))
    
    def _generate_cache_key(self, agent_type: str, request: Dict) -> str:
        """Generate cache key from agent type + request params"""
        request_str = json.dumps(request, sort_keys=True)
        return f"{agent_type}:{hashlib.md5(request_str.encode()).hexdigest()}"
    
    def _fallback_response(self, agent_type: str, request: Dict) -> Response:
        """Return cached or degraded response when agent unavailable"""
        # Try stale cache
        cache_key = self._generate_cache_key(agent_type, request)
        if stale := self.cache.get_stale(cache_key):
            return Response(status="stale_cache", data=stale.data)
        
        # Return minimal fallback
        return Response(
            status="service_unavailable",
            message=f"{agent_type} temporarily unavailable"
        )
```

### Agent Adapter Pattern

**Each sub-agent has an adapter that translates ESB requests to external API calls:**

```python
class AgentAdapter(ABC):
    """Base class for all agent adapters"""
    
    @abstractmethod
    def execute(self, request: Dict, timeout: int) -> Response:
        """Execute agent-specific operation"""
        pass

class TerrainAgentAdapter(AgentAdapter):
    """
    Adapter for terrain generation service
    
    External API: TerrainAPI (hypothetical terrain generation service)
    Protocol: REST over HTTPS
    Auth: API key
    """
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    def execute(self, request: Dict, timeout: int) -> Response:
        """
        Generate 3D terrain model
        
        Request:
        {
            "operation": "generate_terrain",
            "location": {"lat": 39.28, "lon": 22.56, "bbox": [...]},
            "elevation_source": "dem_srtm",
            "format": "gltf"
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "gltf_url": "https://cdn.terrain.api/models/abc123.gltf",
                "metadata": {...}
            }
        }
        """
        if request["operation"] != "generate_terrain":
            return Response(status="error", message="Unknown operation")
        
        # Call external TerrainAPI
        api_response = self.client.post(
            f"{self.base_url}/generate",
            json={
                "bbox": request["location"]["bbox"],
                "elevation_source": request["elevation_source"],
                "output_format": request["format"],
                "lod": request.get("lod_levels", 2)
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=timeout / 1000  # Convert ms to seconds
        )
        
        if api_response.status_code == 200:
            data = api_response.json()
            return Response(
                status="success",
                data={
                    "gltf_url": data["model_url"],
                    "metadata": {
                        "vertices": data["vertex_count"],
                        "triangles": data["triangle_count"],
                        "size_mb": data["file_size_mb"]
                    }
                }
            )
        else:
            return Response(
                status="error",
                message=f"TerrainAPI error: {api_response.status_code}"
            )

class ThreeDObjectAgentAdapter(AgentAdapter):
    """
    Adapter for 3D object placement and rendering
    
    External API: Blender Python API (local) or 3D model service
    """
    
    def execute(self, request: Dict, timeout: int) -> Response:
        """
        Place 3D objects on terrain
        
        Request:
        {
            "operation": "place_objects",
            "objects": [
                {"type": "roman_camp", "position": [39.29, 22.55, 0]},
                {"type": "battle_lines", "positions": [...]}
            ],
            "scale": "historical_accurate"
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "scene_url": "https://cdn.models.api/scenes/xyz789.gltf",
                "objects": [
                    {"id": "camp_001", "model_url": "..."},
                    {"id": "lines_002", "model_url": "..."}
                ]
            }
        }
        """
        # Implementation would call Blender Python API or 3D service
        # For now, stub response
        return Response(
            status="success",
            data={
                "scene_url": f"https://models.api/scenes/{uuid.uuid4()}.gltf",
                "objects": [
                    {
                        "id": f"obj_{i}",
                        "type": obj["type"],
                        "position": obj["position"]
                    }
                    for i, obj in enumerate(request["objects"])
                ]
            }
        )

class SysMLAgentAdapter(AgentAdapter):
    """
    Adapter for SysML diagram rendering
    
    External Tool: SysML tools (Cameo, MagicDraw) or custom renderer
    """
    
    def execute(self, request: Dict, timeout: int) -> Response:
        """
        Render SysML diagram from graph node
        
        Request:
        {
            "operation": "render_block_diagram",
            "node_id": "ARCH-002",
            "detail_level": "full",
            "format": "svg"
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "svg": "<svg>...</svg>",
                "interactive_elements": [...]
            }
        }
        """
        # Query Neo4j for SysML node
        node = self._query_neo4j(request["node_id"])
        
        # Generate SVG diagram
        svg = self._render_block_diagram(
            node=node,
            detail_level=request["detail_level"]
        )
        
        return Response(
            status="success",
            data={
                "svg": svg,
                "interactive_elements": self._extract_clickable_blocks(node)
            }
        )
    
    def _query_neo4j(self, node_id: str):
        """Fetch SysML node from Neo4j"""
        # Implementation
        pass
    
    def _render_block_diagram(self, node, detail_level: str) -> str:
        """Generate SVG for block definition diagram"""
        # Use graphviz or custom renderer
        # Return SVG string
        pass

class ChartAgentAdapter(AgentAdapter):
    """
    Adapter for chart generation (D3.js, Chart.js, Plotly)
    """
    
    def execute(self, request: Dict, timeout: int) -> Response:
        """
        Generate chart from data
        
        Request:
        {
            "operation": "render_okr_progress",
            "goal_id": "GOAL-Q1-2025-SECURITY",
            "chart_type": "donut",
            "include_kpis": true
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "chart_config": {...},  # D3.js/Chart.js config
                "chart_image_url": "...",  # Pre-rendered PNG (optional)
                "data": [...]  # Raw data if client wants to render
            }
        }
        """
        # Query graph for OKR data
        okr_data = self._query_okr_progress(request["goal_id"])
        
        # Generate chart config
        chart_config = {
            "type": "doughnut",
            "data": {
                "labels": [req["name"] for req in okr_data["requirements"]],
                "datasets": [{
                    "data": [req["completion"] for req in okr_data["requirements"]],
                    "backgroundColor": ["#4CAF50", "#FFC107", "#F44336"]
                }]
            },
            "options": {
                "responsive": true,
                "plugins": {
                    "legend": {"position": "bottom"}
                }
            }
        }
        
        return Response(
            status="success",
            data={
                "chart_config": chart_config,
                "summary": {
                    "total_features": len(okr_data["requirements"]),
                    "completed": sum(1 for r in okr_data["requirements"] if r["completion"] == 100),
                    "in_progress": sum(1 for r in okr_data["requirements"] if 0 < r["completion"] < 100)
                }
            }
        )
```

---

## Response Composition

**Once PLAO receives responses from all sub-agents, it composes the final output:**

```python
def compose(self, strategy: Strategy, graph_data: GraphData, sub_responses: List[Response]) -> FinalResponse:
    """
    Compose final rich response from sub-agent outputs
    
    Strategy defines layout, sub_responses contain content
    """
    if strategy.layout == "three_zone":
        return self._compose_three_zone(strategy, graph_data, sub_responses)
    
    elif strategy.layout == "immersive_canvas":
        return self._compose_3d_immersive(strategy, graph_data, sub_responses)
    
    elif strategy.layout == "split_vertical":
        return self._compose_split_view(strategy, graph_data, sub_responses)
    
    else:
        return self._compose_default(strategy, graph_data, sub_responses)

def _compose_3d_immersive(self, strategy, graph_data, sub_responses) -> FinalResponse:
    """
    Compose 3D immersive view (e.g., Battle of Pharsalus terrain)
    
    Layout:
    - Full-screen WebGL canvas
    - Floating info overlay (top-right)
    - Timeline slider (bottom)
    - Graph minimap (bottom-left)
    """
    terrain_response = sub_responses[0]  # TerrainAgent
    objects_response = sub_responses[1]  # 3DObjectAgent
    context_response = sub_responses[2]  # GraphAgent
    
    return FinalResponse(
        content_type="application/json",
        data={
            "layout": "immersive_3d",
            "main_panel": {
                "type": "webgl_viewer",
                "terrain_model_url": terrain_response.data["gltf_url"],
                "objects": objects_response.data["objects"],
                "camera": {
                    "type": "orbit",
                    "initial_position": [39.29, 22.55, 500],  # 500m above
                    "target": [39.29, 22.55, 0]
                },
                "lighting": {
                    "type": "directional",
                    "direction": [1, -1, 0.5],  # Sun angle for -48 BCE
                    "intensity": 0.8
                }
            },
            "overlay": {
                "type": "info_card",
                "position": "top_right",
                "content": {
                    "title": "Battle of Pharsalus (48 BCE)",
                    "summary": context_response.data["summary"],
                    "sources": context_response.data["sources"],
                    "related_nodes": context_response.data["related"]
                }
            },
            "timeline": {
                "type": "slider",
                "position": "bottom_center",
                "range": [-48, -47],  # Years BCE
                "current": -48,
                "events": context_response.data["timeline_events"]
            },
            "minimap": {
                "type": "graph_overview",
                "position": "bottom_left",
                "current_node": graph_data.node_id,
                "visible_radius": 2  # Show 2-hop neighbors
            }
        }
    )
```

---

## Integration with Neo4j Knowledge Graph

**The PLAO and sub-agents query the underlying Neo4j graph for:**

1. **Node metadata** (SysML models, requirements, code files)
2. **Relationships** (satisfies, implements, verifies)
3. **Provenance** (who created, when, why)
4. **Context** (related nodes, debate history)

**Example Cypher query from TerrainAgent:**

```cypher
// Get all historical locations related to a battle
MATCH (event:SysMLNode {sysml_id: "Q48321"})  // Battle of Pharsalus
-[:OCCURRED_AT]->
(location:Location)

RETURN location.name, location.lat, location.lon, location.qid
```

**Example Cypher query from ChartAgent:**

```cypher
// Get OKR progress data
MATCH path = (goal:SysMLNode {sysml_id: "GOAL-Q1-2025-SECURITY"})
-[:DERIVES*]->
(req:SysMLNode {sysml_type: "<<requirement>>"})
-[:SATISFIES]->
(arch:SysMLNode {sysml_type: "<<block>>"})
-[:VERIFIED_BY]->
(test:SysMLNode {sysml_type: "<<testCase>>"})

WITH req, test
RETURN 
  req.sysml_id as RequirementID,
  req.name as Feature,
  count(test) as TotalTests,
  count(CASE WHEN test.status = "PASSED" THEN 1 END) as PassedTests,
  (count(CASE WHEN test.status = "PASSED" THEN 1 END) * 100.0 / count(test)) as Completion
ORDER BY Completion ASC
```

---

## Performance Optimization

### Caching Strategy

**Three-tier cache:**

1. **L1: In-memory (LRU)** - Fast, small (1000 entries), 5-minute TTL
   - User context, recent queries, frequently accessed nodes

2. **L2: Redis** - Medium speed, larger (100K entries), 1-hour TTL
   - Rendered charts, SysML diagrams, graph query results

3. **L3: CDN (CloudFront/Cloudflare)** - Global edge cache, 24-hour TTL
   - Static assets (terrain models, 3D objects, videos)

```python
class CacheManager:
    def __init__(self):
        self.l1_cache = LRUCache(maxsize=1000)
        self.l2_cache = redis.Redis(host='localhost', port=6379)
        self.cdn_prefix = "https://cdn.chrystallum.com"
    
    def get(self, key: str) -> Optional[Any]:
        # Try L1
        if value := self.l1_cache.get(key):
            return value
        
        # Try L2
        if value := self.l2_cache.get(key):
            self.l1_cache.set(key, value)  # Promote to L1
            return value
        
        # Miss
        return None
    
    def set(self, key: str, value: Any, ttl: int):
        # Set in L1
        self.l1_cache.set(key, value, ttl=min(ttl, 300))
        
        # Set in L2
        self.l2_cache.setex(key, ttl, pickle.dumps(value))
        
        # If large static asset, upload to CDN
        if isinstance(value, LargeAsset):
            cdn_url = self._upload_to_cdn(value)
            return cdn_url
```

### Lazy Loading

**For expensive operations (terrain generation), use progressive loading:**

```javascript
// Frontend: Request low-res terrain first, then upgrade
async function loadTerrain(bbox) {
    // Step 1: Load low-res preview (fast, <1s)
    const preview = await fetch('/api/terrain/preview', {
        method: 'POST',
        body: JSON.stringify({ bbox, lod: 0 })  // Level of detail: 0
    });
    renderTerrain(await preview.json());
    
    // Step 2: Load high-res model (slower, 5-10s)
    const fullModel = await fetch('/api/terrain/full', {
        method: 'POST',
        body: JSON.stringify({ bbox, lod: 3 })
    });
    renderTerrain(await fullModel.json());
}
```

---

## Example: Complete Flow

**User query:** "Show me Battle of Pharsalus terrain with troop positions"

### 1. PLAO Receives Request

```python
user_context = UserContext(
    user_id="historian_001",
    role="Researcher",
    viewport="desktop",
    screen_size=(1920, 1080),
    device_capabilities={"webgl": True, "webgpu": False}
)

query = "Show me Battle of Pharsalus terrain with troop positions"

response = plao.orchestrate_response(query, user_context)
```

### 2. Intent Recognition

```python
intent = plao.recognize_intent(query)
# Returns: Intent.VIEW_TERRAIN (confidence: 0.95)
```

### 3. Strategy Selection

```python
strategy = plao.select_strategy(
    intent=Intent.VIEW_TERRAIN,
    data_type="historical_event",
    role="Researcher",
    viewport="desktop"
)
# Returns: "historical_terrain_3d" strategy
```

### 4. ESB Orchestration

```python
# Task 1: Generate terrain
terrain_response = esb.route(
    agent_type="TerrainAgent",
    request={
        "operation": "generate_terrain",
        "location": {"lat": 39.28, "lon": 22.56, "bbox": [39.2, 39.4, 22.4, 22.7]},
        "historical_period": "-48 BCE",
        "format": "gltf"
    },
    timeout=10000
)
# Returns: {"gltf_url": "https://cdn.../terrain_pharsalus.gltf"}

# Task 2: Place troop positions
objects_response = esb.route(
    agent_type="3DObjectAgent",
    request={
        "operation": "place_objects",
        "objects": [
            {"type": "roman_legion", "position": [39.29, 22.55, 0], "count": 22000},
            {"type": "pompey_forces", "position": [39.30, 22.57, 0], "count": 45000}
        ]
    },
    timeout=5000
)
# Returns: {"scene_url": "https://cdn.../battle_scene.gltf"}

# Task 3: Get historical context
context_response = esb.route(
    agent_type="GraphAgent",
    request={
        "operation": "get_battle_context",
        "event_id": "Q48321",  # Wikidata QID
        "include_sources": True
    },
    timeout=2000
)
# Returns: {"summary": "...", "sources": [...], "timeline_events": [...]}
```

### 5. Response Composition

```python
final_response = plao.compose(
    strategy=strategy,
    graph_data=graph_data,
    sub_responses=[terrain_response, objects_response, context_response]
)
# Returns: FinalResponse with WebGL viewer config + overlay data
```

### 6. Frontend Rendering

```javascript
// React component receives final_response
function BattleViewer({ response }) {
    const { main_panel, overlay, timeline } = response.data;
    
    return (
        <div className="immersive-3d">
            <WebGLViewer
                terrainUrl={main_panel.terrain_model_url}
                objects={main_panel.objects}
                camera={main_panel.camera}
                lighting={main_panel.lighting}
            />
            
            <InfoOverlay
                position={overlay.position}
                content={overlay.content}
            />
            
            <TimelineSlider
                range={timeline.range}
                events={timeline.events}
                onChange={handleTimelineChange}
            />
        </div>
    );
}
```

---

## Summary: PLAO + Agent ESB Benefits

| Aspect | Without PLAO/ESB | With PLAO/ESB |
|--------|-----------------|---------------|
| **Presentation** | Fixed UI templates | Dynamic, context-aware strategies |
| **External systems** | Hard-coded API calls | Pluggable agent adapters |
| **Performance** | No caching, slow | Multi-tier cache, lazy loading |
| **Reliability** | Single point of failure | Circuit breakers, fallbacks |
| **Scalability** | Monolithic | Microservices-ready |
| **Rich content** | Limited to charts/tables | 3D terrain, video, simulations |
| **Multi-role** | One-size-fits-all | Role-optimized views |

---

## Integration with Existing Architecture

**PLAO sits on top of the SysML multi-role architecture:**

```
┌─────────────────────────────────────┐
│  USER (Executive, Architect, etc.)  │
└──────────────┬──────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│  PRESENTATION LAYER ORCHESTRATOR     │  ← NEW LAYER
│  • Analyzes context & intent         │
│  • Selects strategy                  │
│  • Orchestrates sub-agents via ESB   │
└──────────────┬───────────────────────┘
               │
               ↓
┌──────────────────────────────────────┐
│  AGENT ESB                           │  ← NEW LAYER
│  • Routes to sub-agents              │
│  • Handles external APIs             │
│  • Caching, circuit breaking         │
└──────────────┬───────────────────────┘
               │
        ┌──────┴──────┬──────┬──────┬──────┐
        ↓             ↓      ↓      ↓      ↓
    Terrain      3D Obj  Chart  SysML  Code
     Agent       Agent   Agent  Agent  Agent
        │             │      │      │      │
        ↓             ↓      ↓      ↓      ↓
    External APIs  (Blender, D3, Tools, GitHub)
```

**Data flow:**
1. User query → PLAO
2. PLAO queries Neo4j (existing SysML knowledge graph)
3. PLAO orchestrates sub-agents via ESB
4. Sub-agents call external APIs
5. PLAO composes rich response
6. User receives context-optimized presentation

---

## Next Steps

1. **Implement PLAO core** (context analysis, intent recognition, strategy selection)
2. **Build Agent ESB** (routing, caching, circuit breaking)
3. **Create agent adapters** (TerrainAgent, 3DObjectAgent, ChartAgent, SysMLAgent)
4. **Integrate with Neo4j** (Cypher queries from agents)
5. **Frontend WebGL viewer** (Three.js for 3D terrain/objects)
6. **Performance testing** (cache hit rates, latency, throughput)
7. **Documentation** (API specs for each agent adapter)

**This completes the architecture:** SysML knowledge graph + Multi-role agents + Presentation orchestrator + Agent ESB = Full-stack SDLC automation with rich, context-aware UX.

Would you like me to design the Python implementation for PLAO or the agent adapter interfaces?