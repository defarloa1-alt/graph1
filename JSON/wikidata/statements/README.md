# Wikidata Statement Payloads

Full statement exports from Wikidata entity pages.

## Primary seed: Q17167 (Roman Republic)

Operational artifacts for the Roman Republic ontology work:

- `Q17167_statements_full.json` — 80 direct claims on the seed
- `Q17167_statement_datatype_profile_*` — datatype analytics

## Pilot: Q1048 (Julius Caesar)

Q1048 files are a **datatype profiling pilot** (451 statements) used to design
`md/Architecture/Wikidata_Statement_Datatype_Ingestion_Spec.md`. They are not
used for Roman Republic DI validation.

Prefer the shorter profile filenames (`Q1048_statement_datatype_profile_*`).

## Producers

- `scripts/tools/wikidata_fetch_all_statements.py`
- `scripts/tools/wikidata_sample_statement_records.py`
- `scripts/tools/wikidata_statement_datatype_profile.py`

## Derived index (runtime)

Build the consumable seed index from statements + backlinks:

```bash
python scripts/tools/wikidata_build_seed_index.py --qid Q17167 --fetch-labels
```

Output: `JSON/wikidata/derived/Q17167_seed_index.json`

See `JSON/wikidata/derived/README.md`.

## Example fetch

```bash
python scripts/tools/wikidata_fetch_all_statements.py --qid Q17167 --output JSON/wikidata/statements/Q17167_statements_full.json
python scripts/tools/wikidata_statement_datatype_profile.py --input JSON/wikidata/statements/Q17167_statements_full.json
```
