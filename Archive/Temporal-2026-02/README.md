# Temporal, February 2026 (archived 2026-11-13)

Period work from the Aura era, superseded by
[GraphRevised/24-PERIODS-AND-TRANSFORMATION.md](../../GraphRevised/24-PERIODS-AND-TRANSFORMATION.md).

That design stored a period's dates, confidence, and authority tier on the
node, and stored membership (`OCCURRED_DURING`). The current design keeps each
source's definition as an attributed claim and computes membership. The
PeriodO copies are older than `GraphRevised/cache/periodo-dataset.json`. The
`wikidata_period_sca_*` files belong to the retired SCA. The other CSVs are
one-off analyses that nothing reads.

Kept in `Temporal/`: `PERIOD_CLASSIFICATION_PLAN.md` (its tiers became 24 §10.1),
`wikitime.json` (Wikidata periods with "part of", candidates for `subperiodOf`),
and the TGN-to-Wikidata mapping in `Temporal/Data/`.
