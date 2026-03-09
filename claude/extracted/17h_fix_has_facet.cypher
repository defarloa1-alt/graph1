// ============================================================
// Script 17h — Fix HAS_FACET misassignments
// ============================================================
// Two problems:
//   1. ~30 ecology disciplines have GEOGRAPHIC (wrong — they are ENVIRONMENTAL)
//      Fix: delete GEOGRAPHIC from any discipline whose label ends in 'ecology'
//      or matches other clearly non-geographic labels
//   2. BIOGRAPHIC facet has 0 disciplines — prosopography and history of Rome
//      are the primary anchors for biographic entity work
// ============================================================

// ── 1a. Remove GEOGRAPHIC from ecology disciplines ────────────────────────────
MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet {key:'GEOGRAPHIC'})
WHERE toLower(d.label) ENDS WITH 'ecology'
DELETE r
RETURN count(*) AS geographic_removed_from_ecology;

// ── 1b. Remove GEOGRAPHIC from other misassigned disciplines ──────────────────
// These have spatial keywords but are not geographic disciplines:
// - area studies       → SOCIAL/CULTURAL
// - dialectology       → LINGUISTIC
// - South Asian languages → LINGUISTIC
// - real estate economics → ECONOMIC
// - urban economics    → ECONOMIC
// - street design      → TECHNOLOGICAL
// - ocean circulation  → SCIENTIFIC (physical oceanography)
// - religion and geography → RELIGIOUS
MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet {key:'GEOGRAPHIC'})
WHERE d.label IN [
  'area studies', 'dialectology', 'South Asian languages',
  'real estate economics', 'urban economics', 'street design',
  'ocean circulation', 'religion and geography'
]
DELETE r
RETURN count(*) AS geographic_removed_other;

// ── 2. Add BIOGRAPHIC to prosopography ────────────────────────────────────────
MATCH (d:Discipline {qid:'Q783287'})
MATCH (f:Facet {key:'BIOGRAPHIC'})
MERGE (d)-[:HAS_FACET]->(f)
RETURN d.label AS discipline, f.key AS facet;

// ── 3. Add BIOGRAPHIC to history of Rome ──────────────────────────────────────
// Roman history is fundamentally prosopographic — persons ARE the record
MATCH (d:Discipline {qid:'Q646206'})
MATCH (f:Facet {key:'BIOGRAPHIC'})
MERGE (d)-[:HAS_FACET]->(f)
RETURN d.label AS discipline, f.key AS facet;

// ── 4. Verify final GEOGRAPHIC + BIOGRAPHIC counts ────────────────────────────
MATCH (d:Discipline)-[:HAS_FACET]->(f:Facet)
WHERE f.key IN ['GEOGRAPHIC','BIOGRAPHIC','ENVIRONMENTAL']
RETURN f.key AS facet, count(d) AS disciplines
ORDER BY facet;
