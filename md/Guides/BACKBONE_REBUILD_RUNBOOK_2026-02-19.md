# Backbone Rebuild Runbook (2026-02-19)

Purpose: deterministic re-seed after Neo4j DB corruption/quarantine.

## 1) Choose Target DB

Use `chrystallum` as the active rebuild target until default `neo4j` is healthy.

Check:

```cypher
SHOW DATABASES YIELD name, currentStatus, statusMessage, default
RETURN name, currentStatus, statusMessage, default
ORDER BY name;
```

## 2) Temporal Backbone (Years)

```powershell
python scripts/backbone/temporal/genYearsToNeo.py `
  --uri bolt://127.0.0.1:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database chrystallum `
  --start -2000 `
  --end 2025
```

## 3) Geo Backbone (Pleiades Places)

```powershell
python scripts/backbone/geographic/import_pleiades_to_neo4j.py `
  --uri bolt://127.0.0.1:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database chrystallum
```

Optional smoke sample:

```powershell
python scripts/backbone/geographic/import_pleiades_to_neo4j.py `
  --uri bolt://127.0.0.1:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database chrystallum `
  --limit 1000
```

## 4) Geo Type Policy/Core Mapping

```powershell
python scripts/backbone/geographic/build_place_type_hierarchy.py `
  --no-wikidata `
  --load-neo4j `
  --neo4j-mode core `
  --force-http `
  --uri bolt://127.0.0.1:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database chrystallum
```

## 5) Period Backbone (Filtered PeriodO Import)

```powershell
python scripts/backbone/temporal/import_enriched_periods.py `
  --uri bolt://127.0.0.1:7687 `
  --user neo4j `
  --password $env:NEO4J_PASSWORD `
  --database chrystallum
```

## 6) Federation Crosswalk Build (CSV Layer)

```powershell
python scripts/backbone/geographic/build_pleiades_geonames_crosswalk.py
python scripts/backbone/geographic/build_geonames_wikidata_bridge.py
```

## 7) Verification Queries

```cypher
MATCH (n) RETURN count(n) AS nodes;
MATCH ()-[r]->() RETURN count(r) AS rels;
RETURN
  count { MATCH (:Year) } AS years,
  count { MATCH (:Place) } AS places,
  count { MATCH (:Period) } AS periods,
  count { MATCH (:PlaceType) } AS place_types,
  count { MATCH (:PlaceTypeTokenMap) } AS place_type_maps;
```

## Notes

1. If `neo4j` default DB stays quarantined, continue seeding `chrystallum`.
2. Once `neo4j` is healthy, rerun the same sequence with `--database neo4j`.
3. Keep federation scoring policy work separate from base backbone rebuild.
