# Project Artifact Registry Decisions

- Date: `2026-02-18`
- Source overrides: `JSON/registry/project_artifact_registry_overrides.json`
- Generated queue: `CSV/registry/project_artifact_registry_review_queue.csv`
- Remaining review items: `0`

## Resolved Override Rules

- None

## Resolved Path Overrides

- `Facets/Scripts/period_facet_tagger.py` -> fields={"status": "deprecated", "canonicality": "compatible_wrapper", "mutation_scope": "read_only", "gates": "none"}
  Note: Deprecated wrapper retained for compatibility; canonical implementation is scripts/backbone/temporal/period_facet_tagger.py.
- `scripts/analyze_label_overlap.py` -> fields={"owner_role": "Platform", "mutation_scope": "read_only", "gates": "none"}
  Note: Local analysis helper; no canonical graph mutation path.
- `scripts/config_loader.py` -> fields={"owner_role": "Platform", "mutation_scope": "read_only", "gates": "none"}
  Note: Configuration utility module for scripts/agents; not a mutation pipeline.
- `scripts/enrich_tsv_with_lcsh.py` -> fields={"owner_role": "Platform", "mutation_scope": "read_only", "gates": "none"}
  Note: Tabular enrichment utility for local preprocessing.
- `scripts/generate_periods_cypher.py` -> fields={"owner_role": "Platform", "mutation_scope": "read_only", "gates": "none"}
  Note: Cypher generation utility; executes outside canonical runtime pipeline.
- `scripts/phase_2_5_discovery_runner.py` -> fields={"owner_role": "SCA", "mutation_scope": "read_only", "gates": "none"}
  Note: Agent orchestration runner for discovery stage.
- `scripts/processing/temporal_bridge_discovery.py` -> fields={"owner_role": "SFA", "mutation_scope": "read_only", "gates": "none"}
  Note: Temporal bridge analysis logic used for reasoning support, not direct canonical writes.
- `scripts/report_lcsh_coverage.py` -> fields={"owner_role": "Platform", "mutation_scope": "read_only", "gates": "none"}
  Note: Coverage report utility over TSV artifacts.

## Remaining Review Items

- Queue is clear.
