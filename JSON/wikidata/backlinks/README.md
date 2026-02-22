# Wikidata Backlink Harvest Reports

This folder stores backlink harvest run reports produced by:
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/wikidata_backlink_profile.py`

Recommended file naming:
- `Qxxxx_backlink_harvest_report.json`
- `Qxxxx_backlink_profile_<section>_summary.json`
- `Qxxxx_backlink_profile_<section>_by_entity.csv`
- `Qxxxx_backlink_profile_<section>_pair_counts.csv`

Example:
```bash
python scripts/tools/wikidata_backlink_harvest.py --seed-qid Q1048
python scripts/tools/wikidata_backlink_harvest.py --seed-qid Q1048 --mode discovery
python scripts/tools/wikidata_backlink_profile.py --input-report JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json --source-section accepted
```

Mode behavior:
- `production` (default): constrained budgets and class allowlist gate enabled.
- `discovery`: expanded budgets, schema properties unioned into property surface, class allowlist gate disabled by default.

Mode default budgets:
- `production`: `sparql_limit=500`, `max_sources_per_seed=200`, `max_new_nodes_per_seed=100`
- `discovery`: `sparql_limit=2000`, `max_sources_per_seed=1000`, `max_new_nodes_per_seed=500`

Report contents include:
- candidate and accepted/rejected source counts
- rejection reasons (`no_p31`, `class_not_allowed`, budget caps)
- class-resolution gate (`P31` + `P279`)
- datatype/value-type gate summary over accepted source nodes
- policy status (`pass` or `blocked_by_policy`)
- dispatcher routing counts (`route_counts`) and quarantine reasons
- frontier eligibility metrics (`frontier_eligible`, `frontier_excluded`)

Profile outputs include:
- summary policy status for selected candidates
- per-entity qualifier/reference and unsupported-pair rates
- aggregate datatype/value_type pair counts
