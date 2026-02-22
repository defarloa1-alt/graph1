# Quick Reference: Launch Your Agent UI

**Date:** February 15, 2026

---

## TL;DR - Get UI Running in 30 Seconds

### Windows:
```cmd
cd C:\Projects\Graph1
launch_gradio_ui.bat
```

### Linux/Mac:
```bash
cd /path/to/Graph1
chmod +x launch_gradio_ui.sh
./launch_gradio_ui.sh
```

**Opens:** http://localhost:7860

---

## Two Options Built For You

### Option 1: Gradio ⭐ (Recommended)
- **Why:** Simpler, better for demos, perfect for your agent interface
- **Launch:** `launch_gradio_ui.bat` (Windows) or `./launch_gradio_ui.sh` (Linux)
- **Port:** http://localhost:7860
- **File:** `scripts/ui/agent_gradio_app.py`

### Option 2: Streamlit
- **Why:** More layout control, better for complex apps
- **Launch:** `launch_streamlit_ui.bat` (Windows) or `./launch_streamlit_ui.sh` (Linux)
- **Port:** http://localhost:8501
- **File:** `scripts/ui/agent_streamlit_app.py`

---

## What You Get

### Both UIs Provide:
- ✅ **Single Facet Mode:** Query 1 of 17 domain experts
- ✅ **Auto-Route Mode:** AI picks relevant facets for you
- ✅ **Configuration Validation:** Shows setup status
- ✅ **Built-in Examples:** Quick test queries
- ✅ **Help Documentation:** In-app guides
- ✅ **Error Handling:** Helpful messages

---

## Example Queries to Try

### Single Facet Mode
Select facet → Type query → Click button

**Military:**
```
What battles occurred in 1066?
```

**Religious:**
```
Find all monasteries founded before 1100
```

**Political:**
```
Who was king of England in 1215?
```

### Auto-Route Mode
Type query → AI detects relevant facets → Queries all

**Complex Query:**
```
What happened during the Norman Conquest?
```
*(Detects: Military, Political, Social facets)*

---

## Prerequisites

Must be configured before launching UI:

1. **API Keys Set:**
   - `OPENAI_API_KEY` ✓
   - `NEO4J_PASSWORD` ✓

2. **Neo4j Running:**
   ```bash
   neo4j status  # Should show "running"
   ```

3. **Configuration Valid:**
   ```bash
   python scripts\config_loader.py  # All checks should pass
   ```

**If not configured:**
```bash
# Windows
setup_config.bat

# Linux/Mac
./setup_config.sh
```

---

## Files Created Today

### Web Applications
- `scripts/ui/agent_gradio_app.py` (450 lines)
- `scripts/ui/agent_streamlit_app.py` (380 lines)

### Launch Scripts
- `launch_gradio_ui.bat` / `.sh` (Windows/Linux)
- `launch_streamlit_ui.bat` / `.sh` (Windows/Linux)

### Documentation
- `md/Guides/UI_SETUP_GUIDE.md` (comprehensive, 800 lines)
- `md/Reports/UI_IMPLEMENTATION_SUMMARY.md` (architecture review)
- `QUICK_REFERENCE_UI.md` (this file)

### Updated
- `requirements.txt` (added gradio, streamlit)
- `README.md` (added UI sections)

---

## Installation (If Needed)

Both UIs auto-install on first launch, but you can also:

```bash
# Install both
pip install gradio streamlit

# Or just one
pip install gradio       # Recommended
pip install streamlit
```

---

## Troubleshooting

### "Agents not initialized"
**Cause:** Configuration incomplete

**Fix:**
1. Click Configuration Status (Gradio) or sidebar (Streamlit)
2. Follow setup instructions shown
3. Run `setup_config.bat` or see `md/Guides/SETUP_GUIDE.md`
4. Restart UI

### "Port already in use"
**Gradio (7860):**
```bash
# Windows
netstat -ano | findstr :7860
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:7860 | xargs kill
```

**Streamlit (8501):**
Change port: `streamlit run app.py --server.port 8080`

### "Cypher query failed"
**Try:**
- Rephrase question more specifically
- Try a different facet
- Check if data exists in graph for that query

---

## Performance

**Query Times:**
- Single Facet: 1-3 seconds
- Auto-Route (3 facets): 4-11 seconds

**Costs:**
- Single query: ~$0.002 (OpenAI)
- 100 queries: ~$0.20

---

## Documentation

**Full guides:**
- [UI_SETUP_GUIDE.md](../Guides/UI_SETUP_GUIDE.md) - Complete setup (10 min read)
- [UI_IMPLEMENTATION_SUMMARY.md](../Reports/UI_IMPLEMENTATION_SUMMARY.md) - Architecture deep-dive (15 min)
- [README.md](../../README.md) - Project overview with UI quick start
- [SETUP_GUIDE.md](../Guides/SETUP_GUIDE.md) - Configuration prerequisite

**In 3 words:**
1. UI_SETUP_GUIDE.md = How to use
2. UI_IMPLEMENTATION_SUMMARY.md = How it works
3. This file = Get started NOW

---

## Command Cheat Sheet

### Gradio
```bash
# Launch (Windows)
launch_gradio_ui.bat

# Launch (Linux/Mac)
chmod +x launch_gradio_ui.sh
./launch_gradio_ui.sh

# Manual launch
python scripts/ui/agent_gradio_app.py

# Install only
pip install gradio
```

### Streamlit
```bash
# Launch (Windows)
launch_streamlit_ui.bat

# Launch (Linux/Mac)
./launch_streamlit_ui.sh

# Manual launch
streamlit run scripts/ui/agent_streamlit_app.py

# Install only
pip install streamlit
```

### Configuration
```bash
# Validate config
python scripts/config_loader.py

# Quick setup
setup_config.bat        # Windows
./setup_config.sh       # Linux/Mac

# Check Neo4j
neo4j status
```

---

## What's Different: Gradio vs Streamlit

| Feature | Gradio | Streamlit |
|---------|--------|-----------|
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Examples UI** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Layout** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Best For** | Demos, functions | Complex apps |

**Recommendation:** Start with Gradio for your use case.

---

## Architecture at a Glance

```
User Browser
    ↓ http://localhost:7860
Gradio/Streamlit UI
    ↓ call: agent.query(text)
FacetAgent (1 of 17)
    ↓ OpenAI API
Cypher Query Generated
    ↓ Neo4j
Database Query
    ↓ format
Results
    ↓ display
User Browser
```

**Total time:** 1-3 seconds per query

---

## Your Next Steps

### Right Now (2 minutes)
1. Open terminal in `C:\Projects\Graph1`
2. Run `launch_gradio_ui.bat` (Windows) or `./launch_gradio_ui.sh` (Linux)
3. Browser opens to http://localhost:7860
4. Click "Single Facet" tab
5. Select "Military" facet
6. Type: "What battles occurred in 1066?"
7. Click "Query Facet"
8. See results!

### Next 10 minutes
- Try Auto-Route mode
- Test different facets
- Read the Help tab
- Show to team

### This Week
- Read `md/Guides/UI_SETUP_GUIDE.md` for advanced features
- Customize examples
- Deploy to team network (optional)

---

## Support

**Configuration issues:**
See [SETUP_GUIDE.md](../Guides/SETUP_GUIDE.md)

**UI usage questions:**
See [UI_SETUP_GUIDE.md](../Guides/UI_SETUP_GUIDE.md)

**Agent architecture:**
See [FACET_AGENT_README.md](../../scripts/agents/FACET_AGENT_README.md)

**Quick config check:**
```bash
python scripts/config_loader.py
```

---

**Status:** ✅ Ready to launch  
**Recommended:** Gradio (`launch_gradio_ui.bat`)  
**Time to first query:** < 30 seconds  
**Enjoy!** 🚀
