# Domain pipeline — one path (Chrystal 2)

**Locked intent:** stop growing parallel enrich CLIs. One Domain path after Schema.

```
harvest pack library
  → land SubjectDomain shell (+ Years)
  → Schema Specialist propose (structure only)
  → Domain schema apply (--review-write)     # existing
  → Domain bootstrap propose (LLM)          # biblio + PeriodO + thin geo
       grounding: proposal + Neo + FederationCards + local seeds
       tools: loc / OCLC / PeriodO / Pleiades resolve (results injected)
  → one review (LLM drops)
  → one write (registry-gated)
```

## Rules

1. **Federations are tools + cards**, not ad-hoc Python PID/QID maps.
2. **No new `apply_*_enrich.py` with curated maps.** Prefer propose JSON + review.
3. **Multi-aboutness** — multiple LCSH/FAST/LCC/PeriodO variants OK; soft ≠ trash.
4. **Pack Years stay on SubjectDomain** — PeriodO cites / enriches, does not replace bounds.
5. **Legacy scripts** (`place_domain.py`, `apply_periodo_enrich.py`, `stamp_place_geo.py`, …)
   are transitional; new packs use `pipeline.py bootstrap`.
6. **Reuse** `--reuse-plan` to re-review/re-apply without another propose LLM call.
7. **Thin geo** — bootstrap may `stamp_place_pleiades` on Domain-linked Places only;
   schema apply still owns CAPITAL / Place minting.

## Modules

| File | Role |
|------|------|
| `agents/domain/propose_bootstrap.py` | LLM propose → `*_domain_bootstrap_plan.json` |
| `agents/domain/review_bootstrap_plan.py` | LLM drop_indices |
| `agents/domain/apply_bootstrap_plan.py` | Registry-gated write |
| `agents/domain/pipeline.py` | One CLI |

## CLI

```powershell
# After schema apply exists for the pack:
python chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --dry-run
python chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --review-only
python chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --review-write
# Re-apply an existing plan (no propose):
python chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --dry-run --reuse-plan
```

Plan artifact: `JSON/wikidata/packs/{qid}_domain_bootstrap_plan.json`

For already-placed packs (e.g. `roman_republic`), expect mostly `noop` actions.

## Acceptance (what “done” means for a Domain)

UI sketch: years on X; Kingdom / Republic / Empire bars on Y; Republic → Early/Middle/Late; sidebar shows biblio, capital, replaces Kingdom, followed by Empire, part of Ancient Rome.

```powershell
python chrystal_2/agents/domain/stamp_period_years.py --domain-id roman_republic --write
python chrystal_2/agents/domain/acceptance_view.py --domain-id roman_republic
```

See `DOMAIN_ACCEPTANCE_TIMELINE.md`.
