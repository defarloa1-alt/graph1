# Chrystallum Knowledge Graph

**A federated historical knowledge graph with 17 specialized facet agents**

[![Neo4j 5.0+](https://img.shields.io/badge/Neo4j-5.0+-blue)](https://neo4j.com)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-orange)](https://openai.com)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)]()

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone & Install
```bash
git clone <repo-url>
cd Graph1
pip install -r requirements.txt
```

### 2. Configure API Keys

**Windows:**
```cmd
setup_config.bat
```

**Linux/Mac:**
```bash
chmod +x setup_config.sh
./setup_config.sh
```

Follow the prompts to add your API keys to `config.py`.

### 3. Verify Setup
```bash
python scripts/config_loader.py
```

### 4. Deploy Neo4j Schema (First Time Only)
```bash
python Neo4j/schema/run_cypher_file.py Neo4j/schema/01_schema_constraints_neo5_compatible.cypher
python Neo4j/schema/run_cypher_file.py Neo4j/schema/02_schema_indexes.cypher
```

**You're ready!** ✓

### 5. Launch Web UI (Optional)

**Gradio (Recommended):**
```bash
pip install gradio
launch_gradio_ui.bat        # Windows
./launch_gradio_ui.sh       # Linux/Mac
```
Opens: http://localhost:7860

**Streamlit:**
```bash
pip install streamlit
launch_streamlit_ui.bat     # Windows
./launch_streamlit_ui.sh    # Linux/Mac
```
Opens: http://localhost:8501

📖 See [UI_SETUP_GUIDE.md](md/Guides/UI_SETUP_GUIDE.md) for details

---

## 📚 What Is This?

Chrystallum is a **5.5-layer authority stack** for historical knowledge:

| Layer | Authority | Purpose | Status |
|-------|-----------|---------|--------|
| **1** | Library Science (LCSH/LCC/FAST) | Canonical gate | ✅ Ready |
| **2** | Federation (Wikidata/Wikipedia) | Linked data | ✅ Ready |
| **2.5** | Hierarchy (P31/P279/P361) | Semantic inference | ✅ Ready |
| **3** | Facets (17 domains) | Disciplinary knowledge | ✅ Ready |
| **4** | Subjects (SubjectConcepts) | Instance authority | ✅ Ready |
| **5** | Agents (Discovery & Claims) | Inference authority | ✅ Ready |

---

## 🎯 Core Features

### 17 Specialized Facet Agents
Each with domain expertise:
- **Military** - Warfare, battles, strategy
- **Political** - States, rulers, governance
- **Economic** - Trade, currency, systems
- **Religious** - Faith, institutions, clergy
- **Social** - Class, kinship, family
- **Cultural** - Identity, movements, symbols
- **Artistic** - Art, architecture, aesthetics
- **Intellectual** - Philosophy, ideas, schools
- **Linguistic** - Languages, scripts, writing
- **Geographic** - Regions, territories, zones
- **Environmental** - Climate, ecology, nature
- **Technological** - Innovation, tools
- **Demographic** - Population, migration
- **Diplomatic** - Treaties, alliances
- **Scientific** - Science, theories, paradigms
- **Archaeological** - Sites, artifacts, material
- **Communication** - Messaging, propaganda

### Multi-Agent Query System
```python
from scripts.agents.facet_agent_framework import FacetAgentFactory, MultiAgentRouter

# Create all 17 agents
agents = FacetAgentFactory.create_all_agents()

# Auto-route query to appropriate facets
router = MultiAgentRouter(agents)
results = router.execute_multi_facet(
    "What was the military and political response to Caesar's assassination?"
)
```

### Phase 2.5: Index Mining
Discover and rank books from library catalogs:
```bash
python scripts/phase_2_5_discovery_runner.py
```

**Output:** Ranked books by 7-indicator scoring algorithm
- English language
- Full text availability
- Index presence
- Publication year
- Academic authority
- Page count (300-600pp optimal)
- Historical closeness

---

## 📖 Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[2-12-26 Chrystallum Architecture - CONSOLIDATED.md](Key%20Files/2-12-26%20Chrystallum%20Architecture%20-%20CONSOLIDATED.md)** | **PRIMARY ARCHITECTURE SPEC (v3.2)** | **60 min** |
| [ARCHITECTURE_IMPLEMENTATION_INDEX.md](md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md) | Maps architecture → implementation files | 5 min |
| [AI_CONTEXT.md](AI_CONTEXT.md) | Project status & agent progress (Steps 1-4) | 15 min |
| [AGENT_SESSION_QUICK_REFERENCE.md](md/Reference/AGENT_SESSION_QUICK_REFERENCE.md) | 28 agent methods quick reference | 10 min |
| [SETUP_GUIDE.md](md/Guides/SETUP_GUIDE.md) | Complete setup instructions | 10 min |
| [UI_SETUP_GUIDE.md](md/Guides/UI_SETUP_GUIDE.md) | Web UI (Gradio/Streamlit) | 10 min |
| [FACET_AGENT_README.md](scripts/agents/FACET_AGENT_README.md) | Agent architecture & usage | 15 min |
| [INDEX_MINING_PHASE_2_5_LAUNCH.md](md/Reports/INDEX_MINING_PHASE_2_5_LAUNCH.md) | Phase 2.5 workflow | 10 min |
| [QUICK_START.md](md/Guides/QUICK_START.md) | Get running fast | 5 min |
| **Agent Implementation Steps** | | |
| ├─ [STEP_1_COMPLETE.md](STEP_1_COMPLETE.md) | Architecture understanding (8 methods) | 10 min |
| ├─ [STEP_2_COMPLETE.md](STEP_2_COMPLETE.md) | State introspection (8 methods) | 10 min |
| ├─ [STEP_3_COMPLETE.md](STEP_3_COMPLETE.md) | Federation discovery (6 methods) | 10 min |
| ├─ [PROPERTY_PATTERN_MINING_INTEGRATION.md](md/Architecture/PROPERTY_PATTERN_MINING_INTEGRATION.md) | Completeness validation (2 methods) | 5 min |
| └─ [STEP_4_COMPLETE.md](STEP_4_COMPLETE.md) | CIDOC-CRM/CRMinf ontology (4 methods) | 15 min |

---

## 🛠️ Usage Examples

### Single Facet Agent
```python
from scripts.agents.facet_agent_framework import FacetAgentFactory

agent = FacetAgentFactory.create_agent(
    facet_key="military",
    facet_label="Military",
    system_prompt=military_prompt
)

# Query Mode: Live Neo4j execution
result = agent.query("Show me battles in 49 BCE")

# Proposal Mode: Generate claim files
agent.propose_claim(
    entity_id="Q181098",
    relationship_type="OCCURRED_IN",
    target_id="Y-0216",
    confidence=0.95,
    label="Battle of Cannae in 216 BCE"
)

agent.close()
```

### Book Discovery (Phase 2.5)
```python
from scripts.agents.book_discovery_agent import BookDiscoveryAgent

agent = BookDiscoveryAgent()

books, export_file = agent.discover_and_rank(
    topic="Roman military history",
    context="Ancient Rome, 27 BCE - 476 CE",
    library="all",
    max_results=50
)

print(f"Top 3 books:")
for book in books[:3]:
    print(f"{book['title']} - Score: {book['quality_score']}")
```

### Web UI (Gradio/Streamlit)
Two UI options for interactive queries:

**Launch Gradio:**
```bash
pip install gradio
python scripts/ui/agent_gradio_app.py
# Opens: http://localhost:7860
```

**Launch Streamlit:**
```bash
pip install streamlit
streamlit run scripts/ui/agent_streamlit_app.py
# Opens: http://localhost:8501
```

**Features:**
- 🎯 Single Facet Mode: Query specific domain agent
- 🔍 Auto-Route Mode: AI detects relevant facets
- ⚙️ Configuration validation UI
- 📖 Built-in help and examples
- 🔒 Localhost only (secure by default)

📖 Full guide: [UI_SETUP_GUIDE.md](md/Guides/UI_SETUP_GUIDE.md)

---

## 🗂️ Project Structure

```
Graph1/
├── scripts/
│   ├── agents/
│   │   ├── facet_agent_framework.py       # Base FacetAgent + Router
│   │   ├── book_discovery_agent.py        # Perplexity book discovery
│   │   └── FACET_AGENT_README.md          # Agent documentation
│   ├── ui/
│   │   ├── agent_gradio_app.py            # Gradio web interface
│   │   └── agent_streamlit_app.py         # Streamlit web interface
│   ├── phase_2_5_discovery_runner.py      # Orchestrate 17-facet discovery
│   └── config_loader.py                    # Secure API key management
├── Prompts/facet_agent_system_prompts.json # 17 facet-specific prompts
├── Neo4j/schema/                            # Database schema + indexes
├── Facets/facet_registry_master.json       # Facet definitions
├── config.py.example                        # Configuration template
├── .env.example                             # Environment variable template
├── setup_config.bat                         # Windows setup script
├── setup_config.sh                          # Linux/Mac setup script
├── launch_gradio_ui.bat / .sh               # Launch Gradio UI
├── launch_streamlit_ui.bat / .sh            # Launch Streamlit UI
└── requirements.txt                         # Python dependencies
```

---

## 🔑 API Keys Required

| Service | Purpose | Cost | Get Key |
|---------|---------|------|---------|
| **OpenAI** | Agent queries | ~$0.002/query | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **Perplexity** | Book discovery | ~$0.005/search | [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) |
| **Neo4j** | Database | Free (local) | [neo4j.com](https://neo4j.com) |

**Phase 2.5 Cost Estimate:** $25-40 total for complete discovery workflow

---

## 🚦 Current Status

### ✅ Production Ready
- 17 facet agents with specialized expertise
- Multi-agent router for auto-routing queries
- Book discovery via Perplexity API
- 7-indicator scoring algorithm
- Neo4j schema (97 constraints, 150 indexes)
- Configuration management (secure API keys)
- Complete documentation

### 🔄 In Progress
- Phase 2.5 Stage 1: Book discovery (Feb 15-18)
- Stage 2: Index extraction (Feb 19-22)
- Stage 3: Claim generation (Mar 3-10)
- Stage 4: Validation + promotion (Mar 10-15)

### 📅 Timeline
- **Feb 15:** Multi-agent framework deployed ✓
- **Feb 18:** Top 50 books ranked (target)
- **Mar 15:** 1,500-2,500 claims promoted (target)

---

## 🤝 Contributing

See [ARCHITECTURE_IMPLEMENTATION_INDEX.md](md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md) for development guidelines.

**Key principles:**
- Facet agents are independent (no cross-domain interference)
- Claim proposals are file-based (audit trail required)
- Validation happens separately from proposal generation
- Authority tracking: QID primary + LCSH/FAST/LCC as properties

---

## 📊 Database Schema

**Node Types:**
- `SubjectConcept` - Thematic anchors (5+ bootstrap)
- `Human` - People
- `Event` - Historical events
- `Place` - Locations
- `Period` - Time periods
- `Claim` - Knowledge assertions with evidence
- `Year` - Calendar years (4,025 nodes: -2000 to 2025 CE)

**Key Relationships:**
- `CLASSIFIED_BY` - Entity → Subject
- `PARTICIPATED_IN` - Human → Event
- `OCCURRED_DURING` - Event → Period
- `STARTS_IN_YEAR` / `ENDS_IN_YEAR` - Temporal bounds
- `PART_OF` - Hierarchical organization
- `SUPPORTED_BY` - Evidence backing

---

## 🔒 Security

- API keys in `config.py` (gitignored)
- Or use environment variables
- Never commit credentials
- See [SETUP_GUIDE.md](md/Guides/SETUP_GUIDE.md) for best practices

---

## 📝 License

[Your License Here]

---

## 🆘 Support

**Configuration issues:**
```bash
python scripts/config_loader.py
```

**Test Neo4j connection:**
```bash
python -c "from neo4j import GraphDatabase; from scripts.config_loader import *; driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)); driver.verify_connectivity(); print('✓ Connected')"
```

**Validate schema:**
```bash
python -c "from scripts.config_loader import *; from neo4j import GraphDatabase; driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)); result = driver.execute_query('SHOW CONSTRAINTS'); print(f'Constraints: {len(result.records)}'); driver.close()"
```

---

**Built with:** Neo4j, Python, OpenAI, Perplexity  
**Last updated:** February 15, 2026  
**Status:** Production Ready for Phase 2.5
