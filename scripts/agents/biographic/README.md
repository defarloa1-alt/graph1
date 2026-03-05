# Biographic Subject Agent

Harvests biographical context for Person nodes with Wikidata QIDs. This agent *is* the harvest — forward properties, backlinks, and spouse qualifiers.

## What it does

1. **Forward properties** — P569/570 (birth/death), P19/20/119 (places), P509 (cause of death), external IDs (VIAF, GND, LCNAF, OCD, etc.), events (P607, P793, P1344, P166)
2. **Backlinks** — items that reference the person (undeclared children, subordinates, founded orgs, etc.)
3. **Spouse qualifiers** — enriches SPOUSE_OF edges with start_year, end_year, series_ordinal, end_reason, place_of_marriage

## Usage

```bash
# From project root
python -m scripts.agents.biographic --dprr 1976
python -m scripts.agents.biographic --all
python -m scripts.agents.biographic --all --dry
```

## Package structure

```
scripts/agents/biographic/
├── __init__.py       # Exports BiographicAgent, harvest_person, load_decision_model
├── agent.py          # Core harvest logic
├── decision_loader.py # Loads SYS_Policy / SYS_WikidataProperty from graph
├── cli.py            # argparse + main
├── __main__.py       # python -m entry point
└── README.md
```

## Decision model (optional)

Run the migration to seed graph-resident decision tables:

```bash
python scripts/neo4j/run_cypher_file.py scripts/migrations/migration_bio_decision_model.cypher
```

When present, the agent uses:
- **BacklinkRouting** — routes backlinks by (pred_pid, item_type_class) to sfa_queue
- **PlaceResolution** — governs stub vs resolved place handling
- **SnapIdAuthority** — derives snap_id from federation source IDs

Without the migration, the agent falls back to hardcoded `BACKLINK_PREDICATE_MAP`.

## Programmatic use

```python
from scripts.agents.biographic import BiographicAgent, harvest_person

# Option 1: Function
with driver.session() as session:
    harvest_person("Q125414", "1976", session)

# Option 2: Agent class
agent = BiographicAgent()
agent.harvest("Q125414", "1976")
agent.close()
```
