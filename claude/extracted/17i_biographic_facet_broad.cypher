// ============================================================
// Script 17i — Broaden BIOGRAPHIC HAS_FACET
// ============================================================
// BIOGRAPHIC is cross-cutting: any discipline whose primary subject
// matter involves historical persons as actors, subjects, or evidence
// should carry it. Three passes:
//
//   A. All disciplines with POLITICAL facet — office-holders, rulers,
//      legislators, administrators are persons
//   B. All disciplines with MILITARY or DIPLOMATIC facet — commanders,
//      legates, diplomats are persons
//   C. Label-pattern disciplines: history-of-[X], historiography,
//      etruscology, numismatics, legal history, women's history,
//      classical philology, church history, auxiliary sciences of history
//
// Excluded: pure sciences, ecology, linguistics, economics, technology
// (persons are not the primary data unit there)
// ============================================================

// ── A. Add BIOGRAPHIC to all POLITICAL disciplines ────────────────────────────
MATCH (d:Discipline)-[:HAS_FACET]->(fp:Facet {key:'POLITICAL'})
MATCH (fb:Facet {key:'BIOGRAPHIC'})
MERGE (d)-[:HAS_FACET]->(fb)
RETURN count(d) AS added_via_political;

// ── B. Add BIOGRAPHIC to all MILITARY + DIPLOMATIC disciplines ────────────────
MATCH (d:Discipline)-[:HAS_FACET]->(fp:Facet)
WHERE fp.key IN ['MILITARY','DIPLOMATIC']
MATCH (fb:Facet {key:'BIOGRAPHIC'})
MERGE (d)-[:HAS_FACET]->(fb)
RETURN count(d) AS added_via_military_diplomatic;

// ── C. Label-pattern historical disciplines ───────────────────────────────────
MATCH (d:Discipline)
WHERE toLower(d.label) STARTS WITH 'history of'
   OR toLower(d.label) IN [
        'historiography', 'etruscology', 'numismatics',
        'legal history', 'women\'s history', 'classical philology',
        'church history', 'auxiliary science of history',
        'study of history', 'historical research',
        'art history', 'cultural history', 'social history',
        'economic history', 'intellectual history', 'ancient history',
        'medieval studies', 'classical studies', 'palaeography'
      ]
MATCH (fb:Facet {key:'BIOGRAPHIC'})
MERGE (d)-[:HAS_FACET]->(fb)
RETURN count(d) AS added_via_label_pattern;

// ── Verify ────────────────────────────────────────────────────────────────────
MATCH (d:Discipline)-[:HAS_FACET]->(f:Facet {key:'BIOGRAPHIC'})
RETURN count(d) AS total_biographic_disciplines;
