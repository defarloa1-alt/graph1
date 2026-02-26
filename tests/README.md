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
