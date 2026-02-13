# statement data types

This note has been formalized into:

- `md/Architecture/Wikidata_Statement_Datatype_Ingestion_Spec.md`

Current profiling artifacts (Q1048 sample set):

- Full statements: `JSON/wikidata/statements/Q1048_statements_full.json`
- 100-row flattened sample: `JSON/wikidata/statements/Q1048_statements_sample_100.csv`
- Datatype profile summary: `JSON/wikidata/statements/Q1048_statement_datatype_profile_summary.json`
- Datatype profile by property: `JSON/wikidata/statements/Q1048_statement_datatype_profile_by_property.csv`
- Datatype/value-type pairs: `JSON/wikidata/statements/Q1048_statement_datatype_profile_datatype_pairs.csv`

Scripts:

- Full statement fetch: `scripts/tools/wikidata_fetch_all_statements.py`
- Statement sampling: `scripts/tools/wikidata_sample_statement_records.py`
- Datatype profiling: `scripts/tools/wikidata_statement_datatype_profile.py`
