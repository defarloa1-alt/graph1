# PeriodO — Domain temporal federation (Chrystal 2)

**Owner:** Domain agent (at apply)  
**Card:** `federations/periodo.json`  
**Access:** local CSV/dump first; HTTP refresh only  

## Not pack bounds

Pack chronology stays on `:SubjectDomain` (`start_year` / `end_year` + Year edges).  
PeriodO **validates / enriches named Period nominations** — soft multi-variant OK.

## Rome seed (tiny — do not bulk-load survey CSV)

`federations/crosswalks/periodo_roman_republic_seed.csv`

| ID | Label | Soft |
|----|-------|------|
| `p06c6g3p3g3` | Republic, 510-30 B.C | no (primary chrono) |
| `p06c6g3hb99` | Republic, 265-30 B.C | yes |
| `p06c6g36mkq` | Republic, 510-265 B.C | yes |
| `p0jrrjbchh2` | Late Roman Republic | yes |

Rebuild: `python chrystal_2/agents/domain/curate_periodo_seed.py`

## Tools

```python
from periodo_tools import periodo_lookup_seed, periodo_resolve_id
periodo_lookup_seed(domain_id="roman_republic")
periodo_resolve_id("p06c6g3p3g3")
```

```powershell
python chrystal_2/agents/domain/apply_periodo_enrich.py --domain-id roman_republic --dry-run
python chrystal_2/agents/domain/apply_periodo_enrich.py --domain-id roman_republic --review-write
```

Enrich writes `periodo_id` / years onto existing WD `:Period` shells (Early/Middle/Late) and stamps primary `p06c6g3p3g3` on SubjectDomain. Neighbor shells (Kingdom, Empire, …) stay `wd_candidate` until mapped.

## Trap

`CSV/periodo_roman_republic*.csv` includes any period whose span overlaps −509…−27 — mostly non-Rome noise. Prefer the seed.
