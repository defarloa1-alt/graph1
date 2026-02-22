# Agent UI Setup Guide

**Date:** February 15, 2026  
**Status:** Ready to deploy

---

## Overview

Two UI options built on top of your facet agent framework:

1. **Gradio** - Function-to-UI wrapper (recommended)
2. **Streamlit** - Script-style app with more layout control

Both provide:
- ✅ Text input for natural language queries
- ✅ Button to execute queries
- ✅ Formatted text output
- ✅ Two modes: Single Facet and Auto-Route
- ✅ Configuration validation and error handling
- ✅ Examples and help documentation

---

## Quick Start

### Option 1: Gradio (Recommended)

**Why Gradio:**
- Simpler code (directly wraps agent functions)
- Better for demo/testing
- Cleaner interface for callable functions
- Auto-generates API endpoints

**Install:**
```bash
pip install gradio
```

**Launch:**
```bash
cd C:\Projects\Graph1
python scripts\ui\agent_gradio_app.py
```

**Access:**
- Opens automatically: http://localhost:7860
- Or manually open browser to that URL

**Interface:**
- **Tab 1: Single Facet** - Query specific domain (Military, Political, etc.)
- **Tab 2: Auto-Route** - AI detects relevant facets automatically
- **Tab 3: Help** - Documentation and examples
- **Accordion: Configuration** - Shows setup status

### Option 2: Streamlit

**Why Streamlit:**
- More layout control
- Better for multi-page apps
- Built-in sidebar
- Rich markdown support

**Install:**
```bash
pip install streamlit
```

**Launch:**
```bash
cd C:\Projects\Graph1
streamlit run scripts\ui\agent_streamlit_app.py
```

**Access:**
- Opens automatically: http://localhost:8501
- Or manually open browser to that URL

**Interface:**
- **Sidebar:** Configuration, help, facet list
- **Main:** Mode selector (Single Facet vs Auto-Route)
- **Results:** Expandable sections per facet

---

## Prerequisites

Both UIs require:
- ✅ Python 3.8+
- ✅ Virtual environment activated
- ✅ Configuration complete (API keys set)
- ✅ Neo4j running

**Configuration Check:**
```bash
python scripts\config_loader.py
```

Expected output:
```
Configuration Status:
  OPENAI_API_KEY: ✓ Set
  PERPLEXITY_API_KEY: ✓ Set (optional for UI)
  NEO4J_PASSWORD: ✓ Set

Validation Tests:
✓ Agent configuration valid
```

If not configured, run:
```bash
# Windows
setup_config.bat

# Linux/Mac
./setup_config.sh
```

---

## Installation Steps

### 1. Install UI Framework

**Gradio:**
```bash
pip install gradio
```

**Streamlit:**
```bash
pip install streamlit
```

**Both:**
```bash
pip install gradio streamlit
```

### 2. Verify Installation

**Gradio:**
```bash
python -c "import gradio; print(gradio.__version__)"
# Expected: 4.x.x or higher
```

**Streamlit:**
```bash
python -c "import streamlit; print(streamlit.__version__)"
# Expected: 1.x.x or higher
```

### 3. Test Launch

**Gradio:**
```bash
python scripts\ui\agent_gradio_app.py
```

**Streamlit:**
```bash
streamlit run scripts\ui\agent_streamlit_app.py
```

---

## Usage

### Single Facet Mode

**When to use:**
- You know the specific domain (military, political, etc.)
- Focused, domain-specific questions
- Faster results (1 agent only)

**Example workflow:**
1. Select facet: "Military"
2. Type query: "What battles occurred in 1066?"
3. Click "Query Facet"
4. View results (formatted Cypher output)

**Gradio:**
- Tab 1: "Single Facet"
- Dropdown to select facet
- Text area for query
- Button to execute

**Streamlit:**
- Radio button: "Single Facet"
- Dropdown to select facet
- Text area for query
- Button to execute

### Auto-Route Mode

**When to use:**
- Complex questions spanning multiple domains
- Not sure which facet to use
- Want comprehensive results
- Exploratory research

**Example workflow:**
1. Type query: "What happened during the Norman Conquest?"
2. Adjust max facets (default: 3)
3. Click "Auto-Route Query"
4. AI detects relevant facets (e.g., Military, Political, Social)
5. View combined results

**Gradio:**
- Tab 2: "Auto-Route"
- Text area for query
- Slider for max facets
- Button to execute
- Results from all facets combined

**Streamlit:**
- Radio button: "Auto-Route"
- Text area for query
- Slider for max facets
- Button to execute
- Expandable sections per facet

---

## Example Queries

### Military Facet
```
What battles occurred in 1066?
Show me all castles built by William the Conqueror
List military campaigns in the Hundred Years War
```

### Political Facet
```
Who was king of England in 1215?
What treaties were signed during the reign of Edward I?
Show me all monarchs of France in the 14th century
```

### Religious Facet
```
Find all Benedictine monasteries founded before 1100
What bishops served in Canterbury?
Show me all churches built in the 13th century
```

### Intellectual Facet
```
Show me manuscripts from Oxford in the 13th century
What scholars taught at Paris University?
List all universities founded in medieval Europe
```

### Auto-Route Examples
```
What happened during the Norman Conquest?
Tell me about medieval monasteries in England
What technological advances occurred in the 13th century?
Show me cultural developments in Renaissance Italy
```

---

## Configuration Validation

Both UIs validate configuration on startup.

**If configuration incomplete:**

**Gradio:**
- Shows red accordion "Configuration Status" (expanded)
- Displays error message with setup instructions
- UI still accessible for reading help
- Queries disabled until configured

**Streamlit:**
- Sidebar shows "❌ Configuration Error"
- Expandable error details with instructions
- Warning message in main area
- Must click "Initialize Agents" after fixing

**Common configuration errors:**

1. **OPENAI_API_KEY missing:**
   ```
   Solution: Add to config.py or set environment variable
   export OPENAI_API_KEY="sk-..."
   ```

2. **NEO4J_PASSWORD missing:**
   ```
   Solution: Add to config.py or set environment variable
   export NEO4J_PASSWORD="your-password"
   ```

3. **Neo4j connection failed:**
   ```
   Solution: Verify Neo4j is running
   neo4j status
   ```

---

## Technical Details

### Gradio Implementation

**File:** `scripts/ui/agent_gradio_app.py` (450 lines)

**Key features:**
- `gr.Blocks()` layout with tabs
- `gr.Examples()` for quick testing
- `gr.Accordion()` for configuration status
- Error handling with helpful messages
- Auto-opens browser on launch

**Function signatures:**
```python
def query_single_facet(user_query: str, facet_key: str) -> str:
    """Query specific facet agent"""

def query_auto_route(user_query: str, max_facets: int) -> str:
    """Auto-route to relevant facets"""
```

**Launch options:**
```python
demo.launch(
    server_name="127.0.0.1",  # localhost only
    server_port=7860,
    share=False,  # no public URL
    inbrowser=True,  # auto-open browser
)
```

### Streamlit Implementation

**File:** `scripts/ui/agent_streamlit_app.py` (380 lines)

**Key features:**
- `st.session_state` for agent persistence
- `st.sidebar` for configuration
- `st.expander()` for collapsible results
- `st.spinner()` for loading states
- Manual initialization button

**Session state:**
```python
st.session_state.factory = FacetAgentFactory()
st.session_state.router = MultiAgentRouter(factory)
st.session_state.initialized = True
```

**Layout:**
```python
st.set_page_config(
    page_title="Chrystallum Agent UI",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

---

## Port Configuration

**Defaults:**
- Gradio: http://localhost:7860
- Streamlit: http://localhost:8501

**Change ports:**

**Gradio:**
Edit `agent_gradio_app.py`:
```python
demo.launch(server_port=8080)  # Custom port
```

**Streamlit:**
```bash
streamlit run scripts\ui\agent_streamlit_app.py --server.port 8080
```

---

## Security

**Both UIs:**
- ✅ Localhost only (no public access by default)
- ✅ Configuration validation before queries
- ✅ API keys not displayed in UI
- ✅ Error messages sanitized

**For production deployment:**
1. Enable authentication (Gradio: `auth=`, Streamlit: custom)
2. Use HTTPS reverse proxy (nginx, caddy)
3. Set `share=False` (Gradio) to prevent public URLs
4. Firewall rules for port access
5. Rate limiting for API calls

---

## Troubleshooting

### "Agents not initialized"

**Gradio:**
- Check "Configuration Status" accordion
- Follow setup instructions
- Restart app after fixing

**Streamlit:**
- Check sidebar for error details
- Fix configuration
- Click "Initialize Agents" button

### "Cypher query failed"

**Cause:** Generated Cypher syntax error or missing data

**Solutions:**
- Try rephrasing question
- Be more specific (names, dates, places)
- Try different facet in Single Facet mode
- Check Neo4j has relevant data

### Port already in use

**Gradio:**
```
Error: Port 7860 already in use
```

**Solution:**
```bash
# Find process using port
netstat -ano | findstr :7860

# Kill process (Windows)
taskkill /PID <pid> /F

# Or change port in code
```

**Streamlit:**
```
Error: Port 8501 already in use
```

**Solution:**
```bash
streamlit run scripts\ui\agent_streamlit_app.py --server.port 8080
```

### Import errors

**Error:**
```
ModuleNotFoundError: No module named 'gradio'
```

**Solution:**
```bash
pip install gradio streamlit
```

**Error:**
```
ModuleNotFoundError: No module named 'config_loader'
```

**Solution:**
Ensure you're running from project root:
```bash
cd C:\Projects\Graph1
python scripts\ui\agent_gradio_app.py
```

---

## Performance

### Query Times

**Single Facet:**
- Cypher generation: 1-2 seconds (OpenAI API)
- Neo4j query: 0.1-1 second (depends on complexity)
- Total: 1-3 seconds

**Auto-Route:**
- Facet detection: 1-2 seconds (OpenAI API)
- Per-facet query: 1-3 seconds each
- 3 facets: 4-10 seconds total

### Costs

**OpenAI API (gpt-3.5-turbo):**
- Single query: ~$0.002
- 100 queries: ~$0.20

**No cost for:**
- UI rendering
- Neo4j queries
- Result formatting

### Optimization

**For faster queries:**
- Use Single Facet mode (1 agent vs multiple)
- Reduce max facets in Auto-Route (3 → 1)
- Cache common queries (future feature)

**For lower costs:**
- Use Single Facet when possible
- Batch related questions
- Use gpt-3.5-turbo instead of gpt-4 (already default)

---

## Comparison: Gradio vs Streamlit

| Feature | Gradio | Streamlit |
|---------|--------|-----------|
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Layout Control** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Function Wrapping** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Examples UI** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Multi-page Apps** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Documentation** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Loading States** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Best For** | Demos, testing | Production apps |

**Recommendation:**
- **Gradio** for this use case: agent is already a callable function
- **Streamlit** if you expand to multi-page app later

---

## Next Steps

### 1. Choose UI Framework

**For quick demo/testing:**
```bash
pip install gradio
python scripts\ui\agent_gradio_app.py
```

**For production app:**
```bash
pip install streamlit
streamlit run scripts\ui\agent_streamlit_app.py
```

### 2. Test Configuration

**Verify agents initialize:**
- Gradio: Check green "Configuration Status"
- Streamlit: Click "Initialize Agents" in sidebar

### 3. Run Test Queries

**Single Facet:**
```
Facet: Military
Query: What battles occurred in 1066?
```

**Auto-Route:**
```
Query: What happened during the Norman Conquest?
```

### 4. Customize (Optional)

**Add facet-specific examples:**
Edit example lists in UI files

**Change theme:**
- Gradio: `theme=gr.themes.Soft()`
- Streamlit: `theme` in `.streamlit/config.toml`

**Add authentication:**
- Gradio: `demo.launch(auth=("user", "pass"))`
- Streamlit: Custom middleware

### 5. Deploy (Future)

**Local network:**
- Gradio: `server_name="0.0.0.0"`
- Streamlit: `--server.address 0.0.0.0`

**Production:**
- Containerize (Docker)
- Reverse proxy (nginx)
- HTTPS certificate
- Authentication layer
- Rate limiting

---

## Documentation

- 📖 [README.md](../../README.md) - Project overview
- 📖 [SETUP_GUIDE.md](SETUP_GUIDE.md) - Configuration
- 📖 [FACET_AGENT_README.md](../../scripts/agents/FACET_AGENT_README.md) - Agent architecture
- 📖 [Gradio Docs](https://www.gradio.app/docs)
- 📖 [Streamlit Docs](https://docs.streamlit.io)

---

**Status:** ✅ UI ready to launch  
**Recommendation:** Start with Gradio  
**Next:** `pip install gradio` → `python scripts\ui\agent_gradio_app.py`
