// ============================================================
// Place Node Hygiene Backfill
// ============================================================
// Fixes missing place_id, entity_type, authority, confidence
// on GeoNames backbone, Wikidata backbone, and stub Place nodes.
//
// Safe to re-run (all SET operations are idempotent).
// Run each block separately in Neo4j Browser or cypher-shell.
// ============================================================


// ----- 1. GeoNames backbone: 1,743 nodes -----
// Missing: place_id, entity_type, confidence
// Note: label is currently set to geonames_id (numeric string)

MATCH (p:Place)
WHERE p.node_type = 'geonames_place_backbone'
  AND p.place_id IS NULL
SET p.place_id = 'plc_gn_' + p.geonames_id,
    p.entity_type = 'place',
    p.confidence = 0.85
RETURN count(p) AS geonames_backfilled;


// ----- 2. Wikidata backbone: 331 nodes -----
// Missing: place_id, entity_type, authority, confidence

MATCH (p:Place)
WHERE p.node_type = 'wikidata_place_backbone'
  AND p.place_id IS NULL
SET p.place_id = 'plc_wd_' + p.qid,
    p.entity_type = 'place',
    p.authority = 'Wikidata',
    p.confidence = 0.85
RETURN count(p) AS wikidata_backfilled;


// ----- 3. Pleiades nodes missing place_id (no federation): ~235 nodes -----
// These have pleiades_id and authority but were created before
// the place_id convention was established.

MATCH (p:Place)
WHERE p.pleiades_id IS NOT NULL
  AND p.place_id IS NULL
SET p.place_id = 'plc_pl_' + p.pleiades_id
RETURN count(p) AS pleiades_backfilled;


// ----- 4. Resolved stubs (qid only, no pleiades_id): ~126 nodes -----
// Missing: place_id, authority, confidence
// These have qid + entity_type but no authority

MATCH (p:Place)
WHERE p.qid IS NOT NULL
  AND p.pleiades_id IS NULL
  AND p.node_type IS NULL
  AND p.authority IS NULL
SET p.place_id = coalesce(p.place_id, 'plc_wd_' + p.qid),
    p.authority = 'Wikidata',
    p.confidence = coalesce(p.confidence, 0.80)
RETURN count(p) AS stubs_backfilled;


// ----- 5. Verify: no Place nodes remain without place_id -----

MATCH (p:Place)
WHERE p.place_id IS NULL
RETURN count(p) AS remaining_without_place_id;


// ----- 6. Verify: no Place nodes remain without authority -----

MATCH (p:Place)
WHERE p.authority IS NULL
RETURN count(p) AS remaining_without_authority;


// ----- 7. Verify: no Place nodes remain without entity_type -----

MATCH (p:Place)
WHERE p.entity_type IS NULL
RETURN count(p) AS remaining_without_entity_type;
