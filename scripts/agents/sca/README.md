# SCA — Subject Classification Agent

Synthesizes domain landscapes from taxonomy harvest + lateral exploration.

## What it does

1. **Domain landscape narrative** — Where the subject sits academically
2. **Per-facet resource pointers** — What each SFA should start from (anchor QIDs, authority IDs)
3. **Taxonomy candidates** — Nodes worth promoting to future SubjectConcepts

## Usage

```bash
# From project root
python -m scripts.agents.sca landscape Q17167 \
  --taxonomy output/taxonomy_recursive/Q17167_recursive_20260220_135756.json \
  --lateral  output/lateral/Q17167_lateral_20260301_221807.json \
  --output   output/sca_landscape/
```

## Package structure

```
scripts/agents/sca/
├── __init__.py           # Exports synthesize
├── landscape_synthesis.py # Core LLM reasoning pass
├── cli.py                # argparse + main
├── __main__.py           # python -m entry point
└── README.md
```

## Requirements

- `ANTHROPIC_API_KEY` in `.env`
- `pip install anthropic`
- Neo4j (optional, for facets from graph; falls back to hardcoded list)

## Programmatic use

```python
from scripts.agents.sca import synthesize

result = synthesize(
    seed_qid="Q17167",
    taxonomy_path="output/taxonomy_recursive/Q17167_recursive_20260220_135756.json",
    lateral_path="output/lateral/Q17167_lateral_20260301_221807.json",
    output_dir="output/sca_landscape/",
)
```
