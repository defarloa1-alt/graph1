# Bootstrap load order — Chrystal 2

Target: Aura `7fe339d2`. Ensure `.env` points here (`chrystal_2/env/ENV_CHECK.md`).

## Before any Wikidata harvest

1. **Temporal backbone (Years)**  
   Script defaults to localhost — pass Aura from `.env`:
   ```powershell
   python -c "from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE; import subprocess, sys; subprocess.check_call([sys.executable, 'scripts/backbone/temporal/genYearsToNeo.py', '--uri', NEO4J_URI, '--user', NEO4J_USERNAME, '--password', NEO4J_PASSWORD, '--database', NEO4J_DATABASE or 'neo4j', '--start', '-2000', '--end', '2025'])"
   ```
   Or manually: `--uri neo4j+s://7fe339d2.databases.neo4j.io --user neo4j --password … --start -2000 --end 2025`  
   Optional later: Decade/Century/Millennium via `scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py`.

2. **Thin SYS ship set** (see `architecture/SYS_CORE_SHIP_SET.md`)  
   - SchemaRegistry + NodeType/RelType from master CSV  
   - 18 Facets from `Facets/facet_registry_master.csv`  
   - AgentTypes (minimal): Domain, Schema specialist, Librarian, SFA, Validation  
     (no SCA agent — SubjectConcepts are nodes; Domain owns lifecycle)  
   - ~~ClaimStatus / RejectionReason~~ — deferred (stay foundational)
   - Minimal D-tables + universal Policies (non-claim)
   - FederationRegistry shell + global sources only (Wikidata, VIAF, OpenAlex, LCSH/FAST/LCC):
     ```powershell
     python chrystal_2/bootstrap/seed_federation_registry.py
     ```
     Cards: `chrystal_2/federations/*.json`. Domain-attached sources (DPRR, Pleiades, …) later.

3. **Domain landing (inert shell)** — after SYS ship:
   ```powershell
   python chrystal_2/bootstrap/land_domain_roman_republic.py
   ```
   See `architecture/DOMAIN_LANDING.md`. Then Librarian (FederationCards). No Claims yet.

## Explicitly not in this pass

- Republic Pleiades / DPRR / PeriodO CSVs  
- Peer SubjectConcepts / FacetUmbrellas from `ac63a8e5`  
- Full `SYS_RoutingRule` / Rome `FacetPolicy` dump  
- Discipline backbone  

## Smoke checks

```cypher
MATCH (y:Year) RETURN min(y.year) AS min_y, max(y.year) AS max_y, count(y) AS n
MATCH (f:Facet) RETURN count(f) AS facets
MATCH (n:SYS_RelationshipType) RETURN count(n) AS rel_types
MATCH (:SYS_FederationRegistry)-[:CONTAINS]->(fs:SYS_FederationSource)
RETURN fs.source_id, fs.scope, fs.model_path
```
