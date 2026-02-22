# 2-18-26 Old Federated Project Harvest

Status: completed initial triage and selective extraction from `Old-federated-project` at commit `e7f56d61c1b5b791c27d2e63698bc5181cab184c`.

## Scope
- Reviewed deleted legacy folder content directly from Git history (no full restore to working tree).
- Prioritized artifacts useful to current Graph1 architecture:
- LCSH relationship extraction
- LCC code normalization and hierarchy helpers
- Deferred heavy PostgreSQL-only stacks and duplicated architecture prose.

## Extracted Artifacts
1. `scripts/tools/extract_lcsh_relationships.py`
- Source: `Old-federated-project/scripts/extract_lcsh_relationships.py`
- Why extracted: practical, small, directly useful for deriving `skos:broader` / `skos:narrower` graph edges from LCSH JSON-LD/NDJSON dumps.
- Notes: generalized parser to support both JSON and NDJSON variants.

2. `scripts/tools/lcc_code_utils.py`
- Source logic: `Old-federated-project/scripts/load_lcc_taxonomy.py` (LCC validation, parent inference, numeric range extraction).
- Why extracted: reusable normalization functions for LCC parsing and future crosswalk/routing checks without importing the legacy ETL stack.

3. `Facets/lcc_fast_seed_mappings_legacy.json`
- Source logic: `Old-federated-project/Guide/lcc/analyze_unmapped_codes.py` (`generate_expanded_mappings()`).
- Why extracted: preserves a large set of legacy LCC-to-FAST seed associations for review/crosswalk bootstrapping.
- Scope: 131 LCC code groups and 131 seed links.
- Caution: treat as `seed/provisional` until validated against authoritative FAST endpoints.

4. `scripts/tools/lcc_fast_seed_summary.py`
- Why extracted: quick diagnostic utility for the seed mapping file (counts by class letter, facet type, confidence).

## Deferred (Not Extracted)
1. `Old-federated-project/Guide/lcc/lcc_database_schema.py`
2. `Old-federated-project/Guide/lcc/fast_database_schema.py`
3. `Old-federated-project/Guide/lcc/enhanced_taxonomy_manager.py`
4. `Old-federated-project/Guide/lcc/lcc_fast_crosswalk_builder.py`
5. `Old-federated-project/scripts/load_lcc_taxonomy.py`

Reason deferred:
- Built around a separate PostgreSQL schema/toolchain not aligned to current Neo4j-first implementation path.
- Requires broader migration design before safe integration.

## Second-Pass Review Notes
Additional files reviewed in second pass:
1. `Old-federated-project/Guide/lcc/analyze_unmapped_codes.py`
2. `Old-federated-project/Guide/lcc/apply_mapping_expansion.py`
3. `Old-federated-project/Guide/lcc/lcc_source_explorer.py`
4. `Old-federated-project/Guide/lcc/enhanced_subject_taxonomy_bundle.py`
5. `Old-federated-project/core/component_ontology.py`
6. `Old-federated-project/core/domain_absorption.py`
7. `Old-federated-project/src/models/project_models.py`

Outcome:
1. Harvested only crosswalk seed data and lightweight summary tooling.
2. Deferred framework-level files that would introduce parallel architecture stacks.
3. Completed separate conceptual markdown harvest:
   `md/Architecture/2-18-26-Old-Federated-Project-Conceptual-Artifacts.md`

## Quick Use
1. Build a CSV of LCSH labels and hierarchy links:
```powershell
python scripts/tools/extract_lcsh_relationships.py `
  --input <path-to-lcsh-jsonld-or-ndjson> `
  --output <path-to-output.csv>
```
2. Reuse LCC helpers in scripts:
```python
from scripts.tools.lcc_code_utils import (
    is_valid_lcc_class_code,
    extract_numeric_range,
    infer_parent_code,
    infer_hierarchy_level,
)
```
3. Summarize legacy seed mappings:
```powershell
python scripts/tools/lcc_fast_seed_summary.py
```

## Next Pass (Optional)
1. Port only crosswalk heuristics from `lcc_fast_crosswalk_builder.py` into a Neo4j-compatible adapter interface.
2. Add small tests for `lcc_code_utils.py` regex/range behavior against real LCC samples.
3. Integrate conceptual docs into implementation planning:
   - `md/Architecture/Presentation_Orchestration_PLAO_ESB_v1.md`
   - `md/Architecture/Scenario_Generation_QA_Gates_v1.md`
   - `md/Architecture/ADR-002-Policy-Gate-and-Update-Operator-Separation.md`
