# Chrystal 2 — index

**Folder:** `Chrystal_2/` (Windows may resolve `chrystal_2/` the same)  
**Instance:** Aura `7fe339d2`  
**Not this folder:** deprecated “Chrystal 2.0” (`0da8c4a3`) — see repo `docs/DEPRECATED_CHRYSTAL_2.0.md`

Start here → [`README.md`](README.md) · live checklist → [`bootstrap/STATUS.md`](bootstrap/STATUS.md)

---

## Tree (canonical — hunt here first)

| Path | Contents |
|------|----------|
| [`architecture/`](architecture/) | Locked designs, acceptance contracts, ownership |
| [`agents/`](agents/) | Domain, Schema Specialist, Librarian (+ principles) |
| [`bootstrap/`](bootstrap/) | Foundation seed scripts + STATUS + LOAD_ORDER |
| [`harvest/`](harvest/) | Pack library builder + contract |
| [`federations/`](federations/) | FederationCard JSON + [`crosswalks/`](federations/crosswalks/) seeds |
| [`cypher/`](cypher/) | **Chrystal_2-only** Cypher (scratch / verify / migrations). Keep out of root `claude/`, `migrations/` |
| [`ui/`](ui/) | Gradio / agent terminal spikes |
| [`csv/`](csv/) | Inventory of which *repo* CSVs matter (does not duplicate dumps) |
| [`env/`](env/) | Instance / credentials notes |
| [`archive/`](archive/) | Superseded C2 material |

### Architecture docs

| Doc | Topic |
|-----|--------|
| [`TERMINOLOGY.md`](architecture/TERMINOLOGY.md) | Locked terms |
| [`DOMAIN_PIPELINE.md`](architecture/DOMAIN_PIPELINE.md) | One Domain bootstrap path |
| [`DOMAIN_LANDING.md`](architecture/DOMAIN_LANDING.md) | SubjectDomain landing |
| [`DOMAIN_ACCEPTANCE_TIMELINE.md`](architecture/DOMAIN_ACCEPTANCE_TIMELINE.md) | Timeline + sidebar acceptance |
| [`DOMAIN_GEO.md`](architecture/DOMAIN_GEO.md) | Thin Domain geo / Pleiades |
| [`DOMAIN_EVENTS.md`](architecture/DOMAIN_EVENTS.md) | Pack Events: Domain owns shortlist/dates; Bio=participation; any SFA may deepen |
| [`PERIODO.md`](architecture/PERIODO.md) | PeriodO |
| [`LIBRARIAN.md`](architecture/LIBRARIAN.md) | Domain aboutness |
| [`SCHEMA_SPECIALIST.md`](architecture/SCHEMA_SPECIALIST.md) | Schema propose |
| [`FEDERATION_LLM_CONTRACT.md`](architecture/FEDERATION_LLM_CONTRACT.md) | Federation cards for LLMs |
| [`SYS_CORE_SHIP_SET.md`](architecture/SYS_CORE_SHIP_SET.md) | Foundation ship set |

### Agent entrypoints

| Agent | CLI |
|-------|-----|
| Schema Specialist | `python Chrystal_2/agents/schema_specialist/__main__.py propose …` |
| Domain schema apply | `python Chrystal_2/agents/domain/apply_schema.py …` |
| Domain bootstrap (biblio+PeriodO+geo) | `python Chrystal_2/agents/domain/pipeline.py bootstrap …` |
| Domain acceptance | `python Chrystal_2/agents/domain/acceptance_view.py …` |
| Librarian (legacy place) | `python Chrystal_2/agents/librarian/place_domain.py …` |

---

## Shared data **outside** this folder (intentional)

Do **not** clone dumps into `Chrystal_2/`. Cards + seeds point at them:

| External path | Role |
|---------------|------|
| `JSON/wikidata/packs/` | Pack library + schema proposals + bootstrap plans |
| `JSON/wikidata/statements/` | WD statement dumps |
| `Geographic/pleiades_*.csv` | Pleiades local dump |
| `Temporal/periodo-dataset.csv` | PeriodO dump |
| `CSV/` (selected) | PeriodO/Pleiades/LCC slices — see [`csv/CSV_INVENTORY.md`](csv/CSV_INVENTORY.md) |
| `.env` (repo root) | `NEO4J_*` must target `7fe339d2` |

C2-authored **tiny seeds** live under `federations/crosswalks/` (PeriodO Rome, Pleiades Rome, biblio candidates).

---

## Rule

New Chrystal_2 docs, Python agents, and Cypher → **under `Chrystal_2/`**.  
If something must live outside (shared dump), add a one-line pointer in this INDEX and in the relevant architecture doc — do not orphan it in root `docs/` or `scripts/agents/` for C2 work.
