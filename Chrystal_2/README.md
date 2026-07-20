# Chrystal 2 (`7fe339d2`) — documentation & code root

Prototype Aura instance for the thinned architecture.

**Canonical production graph remains** `ac63a8e5`. Do not migrate peer SCs / Claims here until the bootstrap story sticks.

**Hunt map:** [`INDEX.md`](INDEX.md) · **status:** [`bootstrap/STATUS.md`](bootstrap/STATUS.md)

> All Chrystal_2 design docs, agents, federation cards, and C2 Cypher belong **in this folder**.  
> Shared dumps (WD packs, Pleiades, PeriodO CSV) stay at repo root — listed in INDEX “External”.

## Folders

| Path | Purpose |
|------|---------|
| `architecture/` | Terminology, Domain pipeline/geo/events, Librarianship, federation contract |
| `agents/` | Domain, Schema Specialist, Librarian |
| `bootstrap/` | Load order + seed / land scripts + STATUS |
| `harvest/` | Pack library builder + contract |
| `federations/` | FederationCard JSON + thin `crosswalks/` seeds |
| `cypher/` | C2-only Cypher (keep out of old repo trees) |
| `ui/` | Agent terminal / Gradio spikes |
| `csv/` | Inventory of which existing CSVs matter |
| `env/` | Credentials / instance switching |
| `archive/` | Superseded C2 material |

## Current status (RR vignette)

- Foundation: Years, Facets, SchemaRegistry, AgentTypes, thin RelTypes, 6 federation cards (incl. PeriodO + Pleiades)
- Pack `roman_republic`: schema apply, biblio, PeriodO, capital geo; timeline acceptance **pass**
- Domain bootstrap: `pipeline.py bootstrap` (biblio + PeriodO + geo) — RR smoke = mostly `noop`
- Domain events: **ownership + 3-slot locked** (Domain shortlist/dates; Bio=participation; any SFA may deepen) — `architecture/DOMAIN_EVENTS.md`
- Claims deferred

## Locked path

```
pack library → SubjectDomain shell → Schema Specialist → schema apply
  → Domain bootstrap (biblio + PeriodO + thin geo)
  → acceptance_view
```

```powershell
# From repo root (folder may appear as Chrystal_2 or chrystal_2 on Windows)
python Chrystal_2/agents/domain/pipeline.py bootstrap --qid Q17167 --domain-id roman_republic --dry-run
python Chrystal_2/agents/domain/acceptance_view.py --domain-id roman_republic
python Chrystal_2/ui/agent_terminal.py
# http://127.0.0.1:7860
```

Legacy CLIs (`place_domain.py`, `apply_periodo_enrich.py`, `stamp_place_geo.py`) remain for replay; prefer bootstrap for new packs.
