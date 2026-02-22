# Prompts Directory

This directory contains LLM prompts and instruction templates used by agents.

## Structure

- **`system/`** - Ready-to-use system prompts (.txt files)
- **`guides/`** - Extraction instruction guides (.md files)  
- **`templates/`** - Python code to load/combine prompts

## Usage

### Python

```python
from prompts.templates.load_prompts import (
    load_system_prompt,
    load_extraction_guide,
    build_agent_prompt,
    get_extraction_agent_prompt
)

# Load individual prompt
prompt = load_system_prompt("extraction_agent")

# Load extraction guide
guide = load_extraction_guide("temporal_extraction")

# Build complete prompt
full_prompt = build_agent_prompt(
    "extraction_agent",
    extraction_guides=["temporal_extraction", "geographic_extraction"]
)

# Or use convenience function
prompt = get_extraction_agent_prompt()
```

### LangChain Integration

```python
from langchain.prompts import ChatPromptTemplate
from prompts.templates.load_prompts import get_extraction_agent_prompt

system_prompt = get_extraction_agent_prompt()

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{text}")
])
```

### Using config.paths

```python
from config.paths import Paths

# Get prompt paths
prompt_path = Paths.system_prompt("extraction_agent")
guide_path = Paths.extraction_guide("temporal_extraction")

# Read files
prompt_text = prompt_path.read_text()
guide_text = guide_path.read_text()
```

## Files

### System Prompts
- `system/extraction_agent.txt` - Main entity/relationship extraction prompt
- `system/person_research_agent.txt` - Person research prompt

### Extraction Guides
- `guides/temporal_extraction.md` - Temporal data extraction rules
- `guides/geographic_extraction.md` - Geographic data extraction rules

## Migration Status

During migration, prompts may exist in both old and new locations.
The `load_prompts.py` module handles backward compatibility automatically.

**Legacy Locations (still supported):**
- `Prompts/extraction_agent.txt` → `Prompts/extraction_agent.txt`
- `Person PROMPT.txt` → `prompts/system/person_research_agent.txt`
- `temporal/docs/Temporal_Data_Extraction_Guide.md` → `prompts/guides/temporal_extraction.md`
- `temporal/Geo/docs/Geographic_Data_Extraction_Guide.md` → `prompts/guides/geographic_extraction.md`

## Related Documentation

- `config/paths.py` - Path configuration with prompt helpers
- `config/README.md` - Path configuration usage
- `MIGRATION_PATH_CONFIG.md` - Migration strategy


