// ============================================================
// Script 18c — Add facets to 7 geo_bootstrap SubjectConcepts
// ============================================================
// The geo_bootstrap SCs were created with no HAS_FACET edges.
// This script adds primary + secondary facets grounded in each
// SC's thematic scope. GEOGRAPHIC is primary for most but
// GEO_POLITICAL_ENTITIES is POLITICAL-primary.
//
// Facet design rationale per SC:
//   GEO_ADMIN_DIVISIONS    GEOGRAPHIC(0.80) + POLITICAL(0.70) + SOCIAL(0.40)
//   GEO_GENERAL            GEOGRAPHIC(0.90) only — no distinguishing dimension
//   GEO_HIST_PLACES        GEOGRAPHIC(0.70) + ARCHAEOLOGICAL(0.80) [arch > geo]
//   GEO_HYDROGRAPHY        GEOGRAPHIC(0.90) + ENVIRONMENTAL(0.50)
//   GEO_PHYS_FEATURES      GEOGRAPHIC(0.90) + ENVIRONMENTAL(0.60)
//   GEO_SETTLEMENTS        GEOGRAPHIC(0.70) + SOCIAL(0.60) + ARCHAEOLOGICAL(0.50)
//   GEO_POLITICAL_ENTITIES POLITICAL(0.80) + GEOGRAPHIC(0.70) + MILITARY(0.50)
// ============================================================

// ── 1. GEO_ADMIN_DIVISIONS: Administrative & Political Divisions ──────────────
MATCH (sc:SubjectConcept {subject_id: 'GEO_ADMIN_DIVISIONS'})
MATCH (f1:Facet {key: 'GEOGRAPHIC'})   MERGE (sc)-[:HAS_FACET {weight: 0.80, is_primary: true}]->(f1)
WITH sc
MATCH (f2:Facet {key: 'POLITICAL'})    MERGE (sc)-[:HAS_FACET {weight: 0.70, is_primary: false}]->(f2)
WITH sc
MATCH (f3:Facet {key: 'SOCIAL'})       MERGE (sc)-[:HAS_FACET {weight: 0.40, is_primary: false}]->(f3)
RETURN sc.label AS sc, count(*) AS facets_added;

// ── 2. GEO_GENERAL: General Geographic Places ────────────────────────────────
MATCH (sc:SubjectConcept {subject_id: 'GEO_GENERAL'})
MATCH (f1:Facet {key: 'GEOGRAPHIC'})   MERGE (sc)-[:HAS_FACET {weight: 0.90, is_primary: true}]->(f1)
RETURN sc.label AS sc, count(*) AS facets_added;

// ── 3. GEO_HIST_PLACES: Historical Places & Archaeological Sites ──────────────
// ARCHAEOLOGICAL weight > GEOGRAPHIC — the defining dimension is excavatability
MATCH (sc:SubjectConcept {subject_id: 'GEO_HIST_PLACES'})
MATCH (f1:Facet {key: 'ARCHAEOLOGICAL'}) MERGE (sc)-[:HAS_FACET {weight: 0.80, is_primary: true}]->(f1)
WITH sc
MATCH (f2:Facet {key: 'GEOGRAPHIC'})     MERGE (sc)-[:HAS_FACET {weight: 0.70, is_primary: false}]->(f2)
RETURN sc.label AS sc, count(*) AS facets_added;

// ── 4. GEO_HYDROGRAPHY: Hydrography & Water Bodies ───────────────────────────
MATCH (sc:SubjectConcept {subject_id: 'GEO_HYDROGRAPHY'})
MATCH (f1:Facet {key: 'GEOGRAPHIC'})     MERGE (sc)-[:HAS_FACET {weight: 0.90, is_primary: true}]->(f1)
WITH sc
MATCH (f2:Facet {key: 'ENVIRONMENTAL'})  MERGE (sc)-[:HAS_FACET {weight: 0.50, is_primary: false}]->(f2)
RETURN sc.label AS sc, count(*) AS facets_added;

// ── 5. GEO_PHYS_FEATURES: Physical Geography & Landforms ─────────────────────
MATCH (sc:SubjectConcept {subject_id: 'GEO_PHYS_FEATURES'})
MATCH (f1:Facet {key: 'GEOGRAPHIC'})     MERGE (sc)-[:HAS_FACET {weight: 0.90, is_primary: true}]->(f1)
WITH sc
MATCH (f2:Facet {key: 'ENVIRONMENTAL'})  MERGE (sc)-[:HAS_FACET {weight: 0.60, is_primary: false}]->(f2)
RETURN sc.label AS sc, count(*) AS facets_added;

// ── 6. GEO_SETTLEMENTS: Settlements & Urban Places ───────────────────────────
MATCH (sc:SubjectConcept {subject_id: 'GEO_SETTLEMENTS'})
MATCH (f1:Facet {key: 'GEOGRAPHIC'})     MERGE (sc)-[:HAS_FACET {weight: 0.70, is_primary: true}]->(f1)
WITH sc
MATCH (f2:Facet {key: 'SOCIAL'})         MERGE (sc)-[:HAS_FACET {weight: 0.60, is_primary: false}]->(f2)
WITH sc
MATCH (f3:Facet {key: 'ARCHAEOLOGICAL'}) MERGE (sc)-[:HAS_FACET {weight: 0.50, is_primary: false}]->(f3)
RETURN sc.label AS sc, count(*) AS facets_added;

// ── 7. GEO_POLITICAL_ENTITIES: States, Empires & Political Entities ───────────
// POLITICAL is primary — this SC is about political organization, not location
MATCH (sc:SubjectConcept {subject_id: 'GEO_POLITICAL_ENTITIES'})
MATCH (f1:Facet {key: 'POLITICAL'})      MERGE (sc)-[:HAS_FACET {weight: 0.80, is_primary: true}]->(f1)
WITH sc
MATCH (f2:Facet {key: 'GEOGRAPHIC'})     MERGE (sc)-[:HAS_FACET {weight: 0.70, is_primary: false}]->(f2)
WITH sc
MATCH (f3:Facet {key: 'MILITARY'})       MERGE (sc)-[:HAS_FACET {weight: 0.50, is_primary: false}]->(f3)
RETURN sc.label AS sc, count(*) AS facets_added;

// ── 8. GEO_GENERAL patch — add CULTURAL secondary to meet CCS ≥2 rule ─────────
// "General Geographic Places" needs a second facet. Any named place has cultural
// context (settlement patterns, territorial identity, cultural landscape).
MATCH (sc:SubjectConcept {subject_id: 'GEO_GENERAL'})
MATCH (f2:Facet {key: 'CULTURAL'})     MERGE (sc)-[:HAS_FACET {weight: 0.40, is_primary: false}]->(f2)
RETURN sc.label AS sc, count(*) AS facets_added;

// ── 9. Verify — all 7 SCs now have ≥2 HAS_FACET edges ────────────────────────
MATCH (sc:SubjectConcept) WHERE sc.source = 'geo_bootstrap'
MATCH (sc)-[r:HAS_FACET]->(f:Facet)
RETURN sc.label AS label
     , collect(f.key + '(' + toString(r.weight) + ')') AS facets
     , count(f) AS facet_count
ORDER BY sc.label;
