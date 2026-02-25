// Schema node actions — run BEFORE D-029 relabeling script
// Per architect ruling. Schema nodes have separate migration path to SYS_PropertyDefinition.

// ---------------------------------------------------------------------------
// 1. Delete — Schema 3 (Period, D-012 stale), Schema 9 (empty), Schema 5 & 6 (duplicates)
// ---------------------------------------------------------------------------
MATCH (n:Schema)
WHERE n.required_props = ['period_id', 'start_year', 'end_year']
  AND n.uses_federations = ['PeriodO', 'Wikidata']
DETACH DELETE n;

// Schema 9: completely empty — only uses_federations: []
MATCH (n:Schema)
WHERE n.uses_federations = []
  AND (n.required_props IS NULL OR size(n.required_props) = 0)
DETACH DELETE n;

// 1b. Schema 5/6: delete both duplicate Wikidata-only stubs (confirmed indistinguishable)
MATCH (n:Schema)
WHERE 'Wikidata' IN n.uses_federations AND size(n.uses_federations) = 1
  AND (n.required_props IS NULL OR size(n.required_props) = 0)
DETACH DELETE n;

// ---------------------------------------------------------------------------
// 2. Update — Schema 8: WorldCat → LC_SRU (WorldCat backlogged per D-025)
// ---------------------------------------------------------------------------
MATCH (n:Schema)
WHERE n.uses_federations = ['WorldCat', 'Wikidata']
SET n.uses_federations = ['LC_SRU', 'Wikidata'];

// ---------------------------------------------------------------------------
// 3. Flag — Schema 4 (Human): incomplete, required_props missing
// ---------------------------------------------------------------------------
MATCH (n:Schema)
WHERE n.uses_federations = ['Wikidata', 'VIAF']
SET n.status = 'incomplete — required_props missing',
    n.system = true;

// ---------------------------------------------------------------------------
// 4. Add system: true to remaining Schema nodes (1, 2, 7, 8, and one of 5/6)
// Schema nodes are NOT relabeled in D-029 — they migrate to SYS_PropertyDefinition
// in SchemaRegistry build, not D-029.
// ---------------------------------------------------------------------------
MATCH (n:Schema)
SET n.system = true;
