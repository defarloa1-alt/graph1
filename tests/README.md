# Pipeline Tests

Unit tests for the backlink harvest pipeline: verify_anchor_qids, SCA salience, and related components.

## Run

```powershell
cd c:\Projects\Graph1
python -m pytest tests/ -v
```

Run a specific test file:

```powershell
python -m pytest tests/test_verify_anchor_qids.py -v
python -m pytest tests/test_sca_salience.py -v
```

## Coverage

- **test_verify_anchor_qids.py** — `_labels_compatible` heuristic, `run_verification` with mocked Wikidata (no API calls)
- **test_sca_salience.py** — load_anchors, load_hierarchy, compute_depth, load_entity_counts, load_harvest_status, base_score, path_coherence, select_doors (no Neo4j)

## Dependencies

- pytest (in requirements.txt)

## Perplexity API (scripts using LLM)

Scripts like `enrich_survey_facets_llm.py` and `subject_characterization_agent.py` call the Perplexity API. Configure via `.env` or `config.py`:

| Env var | Notes |
|---------|-------|
| `PPLX_API_KEY` | Preferred (Perplexity's official name) |
| `PERPLEXITY_API_KEY` | Legacy alias |

Use `scripts.config_loader` so keys load from `.env` and `config.py`. Model: `sonar-pro` (avoid deprecated `llama-3.1-sonar-large-128k-online`).
