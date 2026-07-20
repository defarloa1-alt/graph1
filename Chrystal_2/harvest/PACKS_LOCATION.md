# Pack artifacts (external to Chrystal_2/)

Runtime pack JSON lives at repo:

`JSON/wikidata/packs/`

Examples: `{qid}_pack_library.json`, `{qid}_schema_proposal.json`, `{qid}_domain_bootstrap_plan.json`.

Chrystal_2 **code and contracts** for building / applying those packs live under:

- `Chrystal_2/harvest/`
- `Chrystal_2/agents/`
- `Chrystal_2/architecture/DOMAIN_PIPELINE.md`

Do not scatter new pack-pipeline docs into root `docs/` — put them under `Chrystal_2/architecture/` or `Chrystal_2/harvest/` and link from `Chrystal_2/INDEX.md`.
