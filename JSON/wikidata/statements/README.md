# Wikidata Statement Payloads

This folder stores full statement exports from Wikidata entity pages.

Recommended file naming:
- `Qxxxx_statements_full.json`

Primary producer script:
- `scripts/tools/wikidata_fetch_all_statements.py`

Example:
```bash
python scripts/tools/wikidata_fetch_all_statements.py --qid Q1048 --summary-only --output JSON/wikidata/statements/Q1048_statements_full.json
```

Why keep these:
- Preserve raw claims, qualifiers, and references for auditability.
- Support datatype profiling (`time`, `wikibase-entityid`, `quantity`, etc.).
- Enable repeatable enrichment experiments without re-querying every time.
