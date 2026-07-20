# Acceptance — Domain timeline + sidebar (v1)

**Pack:** `roman_republic` / Q17167  
**Readonly check:** `python chrystal_2/agents/domain/acceptance_view.py --domain-id roman_republic`

## Future UI

| Surface | Expectation |
|---------|-------------|
| Chart X | Years |
| Chart Y | Horizontal bars: **Kingdom → Republic → Empire** |
| Republic | Decomposed into Early / Middle / Late (`HAS_PART`) |
| Sidebar | Biblio tether, capital Rome, replaces Kingdom, followed by Empire, part of Ancient Rome |

## Graph contract

```
(:SubjectDomain)-[:STARTS_IN_YEAR|ENDS_IN_YEAR]->(:Year)          # pack bounds
(:SubjectDomain)-[:HAS_PART]->(:Period)                           # E/M/L
(:SubjectDomain)-[:REPLACES]->(:Period {qid:Q201038})             # Kingdom
(:SubjectDomain)-[:FOLLOWED_BY]->(:Period {qid:Q2277})            # Empire
(:SubjectDomain)-[:PART_OF]->(:Period {qid:Q1747689})             # Ancient Rome
(:SubjectDomain)-[:CAPITAL]->(:Place {qid:Q220})
(:SubjectDomain)-[:HAS_LCSH_AUTHORITY]->(:LCSH_Heading)
(:Period)-[:STARTS_IN_YEAR|ENDS_IN_YEAR]->(:Year)                 # drawable shells
```

Years on neighbor shells come from `stamp_period_years.py` (PeriodO promote or WD inception/end). Soft overlaps (e.g. Middle PeriodO 265–30 vs Late) are allowed.

## Pass criteria

`acceptance_view.py` exits 0 when `checks.pass` is true: primary lanes drawable, E/M/L drawable, sidebar has biblio + capital + replaces Kingdom + followed by Empire + part of Ancient Rome.
