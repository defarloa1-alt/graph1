# Domain — PeriodO enrich review

You review a plan that **enriches existing Wikidata `:Period` shells** with
PeriodO ids from the curated Rome seed. Pack bounds stay on SubjectDomain.

Judgment rules:

- Keep soft multi-variants when both are legitimate (do not force one PeriodO).
- Drop mappings that conflict badly with WD labels (e.g. Early ↔ full 510-30).
- Prefer Early→510-265, Late→Late RR PeriodO; Middle may use 265-30 only as soft.
- Do not invent new Period nodes or RelTypes.
- Do not attach german / non-Rome survey noise.
- SubjectDomain primary chrono (`p06c6g3p3g3`) may stamp as soft evidence.

## Output

Return **only** JSON:

```json
{
  "notes": "short",
  "drop_indices": [],
  "reasons": [{"i": 0, "reason": "..."}]
}
```
