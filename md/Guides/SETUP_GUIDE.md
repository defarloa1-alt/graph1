# Chrystallum Setup Guide

**Quick Start:** Get your agents running in 5 minutes

---

## Prerequisites

- Python 3.8+
- Neo4j 5.0+ (local or cloud)
- Git

---

## Step 1: Clone & Install Dependencies

```bash
cd C:\Projects\Graph1
pip install -r requirements.txt
```

**Required packages:**
- `neo4j>=5.0.0` - Graph database driver
- `openai>=0.27.0` - OpenAI API client
- `requests>=2.28.0` - HTTP client (for Perplexity)

---

## Step 2: Configure API Keys

### Option A: Using config.py (Recommended)

```bash
# Copy example config
copy config.py.example config.py

# Edit config.py with your API keys
notepad config.py
```

**config.py:**
```python
# OpenAI API Key (required for agents)
OPENAI_API_KEY = "sk-proj-abc123..."  # Get from platform.openai.com

# Perplexity API Key (required for book discovery)
PERPLEXITY_API_KEY = "pplx-xyz789..."  # Get from perplexity.ai

# Neo4j Connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your-password"  # Your actual password
NEO4J_DATABASE = "neo4j"
```

### Option B: Using Environment Variables

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-proj-abc123..."
$env:PERPLEXITY_API_KEY = "pplx-xyz789..."
$env:NEO4J_PASSWORD = "your-password"

# Linux/Mac
export OPENAI_API_KEY="sk-proj-abc123..."
export PERPLEXITY_API_KEY="pplx-xyz789..."
export NEO4J_PASSWORD="your-password"
```

### Option C: Using .env file

```bash
# Copy example
copy .env.example .env

# Edit .env
notepad .env
```

Then load in PowerShell:
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
```

---

## Step 3: Get API Keys

### OpenAI API Key (Required)

1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy key (starts with `sk-proj-` or `sk-`)
5. Add to `config.py` or environment

**Cost:** ~$0.002 per query (gpt-3.5-turbo)

### Perplexity API Key (Required for Discovery)

1. Go to https://www.perplexity.ai/settings/api
2. Sign in or create account
3. Click "Generate API Key"
4. Copy key (starts with `pplx-`)
5. Add to `config.py` or environment

**Cost:** ~$0.005 per search query

### Neo4j Password (Required)

If using local Neo4j:
```bash
# Default password: neo4j (change on first login)
# Or your custom password
```

If using Neo4j Aura:
```bash
# Copy connection string and password from Aura console
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_PASSWORD=your-generated-password
```

---

## Step 4: Verify Configuration

```bash
cd C:\Projects\Graph1
python scripts\config_loader.py
```

**Expected output:**
```
Chrystallum Configuration Loader
============================================================
Configuration Status:
  Config file found: True
  OPENAI_API_KEY: ✓ Set
  PERPLEXITY_API_KEY: ✓ Set
  NEO4J_URI: bolt://localhost:7687
  NEO4J_USERNAME: neo4j
  NEO4J_PASSWORD: ✓ Set
  NEO4J_DATABASE: neo4j

Validation Tests:
✓ Agent configuration valid
✓ Discovery configuration valid
```

---

## Step 5: Test Neo4j Connection

```bash
python -c "
from neo4j import GraphDatabase
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
with driver.session() as session:
    result = session.run('RETURN 1 as test')
    print('✓ Neo4j connected:', result.single()['test'])
driver.close()
"
```

---

## Step 6: Test Agent Framework

```bash
cd C:\Projects\Graph1

# Test facet agent
python scripts\agents\facet_agent_framework.py

# Test book discovery
python scripts\agents\book_discovery_agent.py
```

---

## Common Issues

### Issue: "OPENAI_API_KEY is required but not set"

**Solution:**
1. Check `config.py` exists and has valid key
2. Or set environment variable
3. Verify with `python scripts\config_loader.py`

### Issue: "Neo4j connection refused"

**Solution:**
1. Check Neo4j is running: `neo4j status`
2. Verify URI: `bolt://localhost:7687` (local) or `neo4j+s://...` (Aura)
3. Test password is correct

### Issue: "Perplexity API rate limit"

**Solution:**
1. Check API quota at perplexity.ai/settings/api
2. Run discovery with fewer workers: `max_workers=1`
3. Add delays between requests

### Issue: "Module not found: config_loader"

**Solution:**
```bash
# Make sure you're in the right directory
cd C:\Projects\Graph1

# Verify file exists
dir scripts\config_loader.py

# Run with full path
python C:\Projects\Graph1\scripts\config_loader.py
```

---

## Next Steps

### Run Phase 2.5 Discovery (After Setup)

```bash
cd C:\Projects\Graph1
python scripts\phase_2_5_discovery_runner.py
```

This will:
1. Query library catalogs for books (17 facets)
2. Score by 7-indicator algorithm
3. Export rankings to `tmp/`
4. Generate summary report

**Expected runtime:** 30-60 minutes (parallel)  
**Expected cost:** ~$5-10 (Perplexity + OpenAI calls)

### Run Single Facet Agent

```python
from scripts.agents.facet_agent_framework import FacetAgentFactory

# Load system prompt from JSON
import json
with open('facet_agent_system_prompts.json') as f:
    prompts = json.load(f)

military_config = prompts['facets'][0]  # Military facet

agent = FacetAgentFactory.create_agent(
    facet_key=military_config['key'],
    facet_label=military_config['label'],
    system_prompt=military_config['system_prompt']
)

result = agent.query("Show me battles in 49 BCE")
print(result)

agent.close()
```

---

## Configuration Priority

Configuration is loaded in this order (first found wins):

1. **Environment variables** (highest priority)
2. **config.py** (local configuration file)
3. **Defaults** (hardcoded fallbacks)

This allows:
- Development: Use `config.py` (gitignored)
- Production: Use environment variables
- CI/CD: Use environment variables from secrets

---

## Security Notes

⚠️ **Never commit API keys to Git**

Files automatically ignored:
- `config.py` (in .gitignore)
- `.env` (in .gitignore)

Safe to commit:
- `config.py.example`
- `.env.example`

---

## Cost Estimates

### OpenAI (gpt-3.5-turbo)
- Query: ~$0.002 per query
- 100 queries: ~$0.20
- 1,000 queries: ~$2.00

### Perplexity (pplx-7b-chat)
- Search: ~$0.005 per search
- 50 books/facet × 17 facets = 850 searches
- Phase 2.5 Stage 1: ~$4-5

### Total Phase 2.5 Stage 1
- Book discovery (17 facets): ~$5-10
- Claim generation (Stages 3-4): ~$20-30
- **Total estimate: $25-40**

---

## Support

**Configuration issues:**
```bash
python scripts\config_loader.py
```

**Test Neo4j:**
```bash
python -c "from scripts.config_loader import *; print_config_status()"
```

**Validate all:**
```bash
python scripts\config_loader.py
```

---

**Last updated:** February 15, 2026  
**Setup time:** 5-10 minutes  
**Ready to run:** Phase 2.5 Discovery
