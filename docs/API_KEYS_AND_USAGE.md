# API Keys and Usage

**Purpose:** Where to get keys, how to set them, verification, code examples, script reference, rate limits, and troubleshooting.

---

## 1. Where to Get Keys

| Provider | URL | Key Format | Notes |
|----------|-----|------------|-------|
| **OpenAI** | https://platform.openai.com/api-keys | `sk-proj-...` or `sk-...` | Create key, copy immediately (shown once) |
| **Perplexity** | https://www.perplexity.ai/settings/api | `pplx-...` | Sign in, API section |

---

## 2. How to Set Keys

### Priority (first found wins)

1. **Environment variables**
2. **config.py** (project root)
3. **.env** (loaded by config_loader via python-dotenv)

### Option A: config.py

```bash
copy config.py.example config.py
# Edit config.py:
```

```python
OPENAI_API_KEY = "sk-proj-your-key-here"
PERPLEXITY_API_KEY = "pplx-your-key-here"
```

- **Location:** Project root (same folder as README.md)
- **Security:** `config.py` is in `.gitignore` — never committed

### Option B: .env

Create `.env` in project root:

```
OPENAI_API_KEY=sk-proj-your-key-here
PERPLEXITY_API_KEY=pplx-your-key-here
NEO4J_PASSWORD=your-password
```

- `config_loader.py` loads `.env` via `python-dotenv` when scripts run
- `.env` should be in `.gitignore`

### Option C: Environment variables

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-proj-your-key"
$env:PERPLEXITY_API_KEY = "pplx-your-key"
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-proj-your-key
set PERPLEXITY_API_KEY=pplx-your-key
```

**Linux / Mac:**
```bash
export OPENAI_API_KEY="sk-proj-your-key"
export PERPLEXITY_API_KEY="pplx-your-key"
```

### Perplexity aliases

`config_loader` accepts either:

- `PPLX_API_KEY` (official)
- `PERPLEXITY_API_KEY` (legacy)

Both work; `PPLX_API_KEY` takes precedence if both are set.

---

## 3. Verification

### Run config_loader

```bash
python scripts/config_loader.py
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

### Quick Python check

```python
from scripts.config_loader import OPENAI_API_KEY, PERPLEXITY_API_KEY, print_config_status
print_config_status()
```

---

## 4. Code Usage

### OpenAI via HTTP (requests)

```python
import os
import requests

key = os.getenv("OPENAI_API_KEY")  # or from config_loader
url = "https://api.openai.com/v1/chat/completions"
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"}
    ],
    "temperature": 0.1,
}
r = requests.post(url, json=payload, headers=headers, timeout=60)
content = r.json()["choices"][0]["message"]["content"]
```

### OpenAI via SDK (openai)

```python
from openai import OpenAI
from scripts.config_loader import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"}
    ],
    temperature=0.1,
)
content = response.choices[0].message.content
```

### Perplexity via HTTP (requests)

```python
import os
import requests

key = os.getenv("PERPLEXITY_API_KEY") or os.getenv("PPLX_API_KEY")
url = "https://api.perplexity.ai/chat/completions"
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
payload = {
    "model": "llama-3.1-sonar-large-128k-online",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"}
    ],
    "temperature": 0.1,
}
r = requests.post(url, json=payload, headers=headers, timeout=60)
content = r.json()["choices"][0]["message"]["content"]
```

### Prefer config_loader

```python
from scripts.config_loader import OPENAI_API_KEY, PERPLEXITY_API_KEY

# Uses env > config.py > .env
key = OPENAI_API_KEY
```

---

## 5. Script Reference

| Script | OpenAI | Perplexity | Notes |
|--------|--------|------------|-------|
| `scripts/agents/facet_agent_framework.py` | ✓ | | SDK |
| `scripts/agents/query_executor_agent_test.py` | ✓ | | SDK |
| `scripts/agents/sca_agent.py` | | ✓ | HTTP |
| `scripts/agents/subject_concept_facet_agents.py` | | ✓ | HTTP |
| `scripts/agents/subject_concept_workflow.py` | | ✓ | HTTP |
| `scripts/agents/book_discovery_agent.py` | | ✓ | HTTP |
| `scripts/backbone/subject/map_lcc_to_facets_llm.py` | ✓ | ✓ | HTTP, `--provider` |
| `scripts/backbone/subject/find_subject_concept_anchors.py` | | ✓ | HTTP, `--use-perplexity` |
| `scripts/backbone/temporal/enrich_periods_with_perplexity.py` | | ✓ | config |
| `scripts/legacy/llm_resolve_unknown_properties.py` | ✓ | | SDK |
| `scripts/ui/agent_gradio_app.py` | ✓ | | via agents |
| `scripts/ui/agent_streamlit_app.py` | ✓ | | via agents |

---

## 6. Rate Limits & Practices

### OpenAI

- **Docs:** https://platform.openai.com/docs/guides/rate-limits
- **Limits:** RPM, RPD, TPM, TPD (tier-based)
- **429:** Implement exponential backoff
- **Models:** `gpt-4o-mini` (cheap), `gpt-4o` (stronger)
- **Temperature:** 0.1–0.2 for structured output; 0.7+ for creative

### Perplexity

- **Docs:** https://docs.perplexity.ai/guides/rate-limits
- **Limits:** Tier-based (spend → higher limits)
- **Models:** `llama-3.1-sonar-large-128k-online`, `sonar-pro`
- **Temperature:** 0.1 for deterministic; 0.3–0.5 for varied

### Practices

- Use `temperature=0.1` for JSON, classification, mapping
- Batch requests when possible (e.g. LCC mapping: 35 classes per call)
- Cache LLM outputs when idempotent (e.g. LCC→facet mappings)
- Handle 429 with retry + backoff

---

## 7. Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `OPENAI_API_KEY not set` | Key not in env, config.py, or .env | Set in config.py or `$env:OPENAI_API_KEY = "sk-..."` |
| `PERPLEXITY_API_KEY not set` | Same | Set `PERPLEXITY_API_KEY` or `PPLX_API_KEY` |
| `401 Unauthorized` | Invalid or expired key | Regenerate key at provider dashboard |
| `429 Too Many Requests` | Rate limit | Wait, retry with backoff; check tier |
| `config.py not found` | No config | `copy config.py.example config.py` and edit |
| `ModuleNotFoundError: config` | Wrong cwd | Run from project root |
| `dotenv` not loading | Missing python-dotenv | `pip install python-dotenv` |

### Common fixes

**Keys not loading:**
```bash
# Verify config_loader sees them
python -c "from scripts.config_loader import OPENAI_API_KEY; print('OK' if OPENAI_API_KEY else 'Missing')"
```

**Perplexity 401:**
- Confirm key starts with `pplx-`
- Check https://www.perplexity.ai/settings/api for validity

---

## 8. Related Docs

| Doc | Purpose |
|-----|---------|
| `md/Guides/CONFIGURATION_COMPLETE.md` | Full configuration guide |
| `scripts/setup/setup_config.bat` | Windows setup |
| `scripts/setup/setup_config.sh` | Linux/Mac setup |
| `config.py.example` | Config template |
| `README.md` | Quick start, setup section |
| `docs/agents/SUBJECT_AGENT_NEO4J_PUSH_GUIDE.md` | Agent config patterns |
