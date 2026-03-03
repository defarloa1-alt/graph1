// ADR-007 Section 3: Person Noise Nodes — Cypher Queries
// 25 nodes in person_ namespace that fail the veto gate (P31 ≠ human when dprr_id IS NULL)

// ─────────────────────────────────────────────────────────────────────────────
// 1. IDENTIFY: All person_ namespace nodes with dprr_id IS NULL
// ─────────────────────────────────────────────────────────────────────────────

MATCH (n:Entity)
WHERE (n.entity_id STARTS WITH 'person_' OR (n.entity_cipher STARTS WITH 'ent_per_' AND n.entity_type = 'PERSON'))
  AND n.dprr_id IS NULL
RETURN n.entity_id, n.entity_cipher, n.qid, n.label, n.entity_type
ORDER BY n.label;

// ─────────────────────────────────────────────────────────────────────────────
// 2. VETO FAILURES: Those with P31 → non-human, or no P31 at all
// ─────────────────────────────────────────────────────────────────────────────

MATCH (n:Entity)
WHERE (n.entity_id STARTS WITH 'person_' OR (n.entity_cipher STARTS WITH 'ent_per_' AND n.entity_type = 'PERSON'))
  AND n.dprr_id IS NULL
OPTIONAL MATCH (n)-[r]->(p31:Entity)
WHERE type(r) IN ['P31', 'WIKIDATA_P31']
WITH n,
     collect(DISTINCT CASE WHEN p31 IS NOT NULL THEN {qid: p31.qid, label: p31.label} END) AS raw_targets
WITH n, [t IN raw_targets WHERE t IS NOT NULL AND (t.qid IS NOT NULL OR t.label IS NOT NULL)] AS p31_targets
WITH n, p31_targets,
     size(p31_targets) > 0 AND any(t IN p31_targets WHERE (t.qid = 'Q5' OR toLower(coalesce(t.label, '')) = 'human')) AS has_human_p31
WHERE (size(p31_targets) = 0) OR (NOT has_human_p31)
RETURN n.entity_id, n.entity_cipher, n.qid, n.label, p31_targets
ORDER BY n.label;

// ─────────────────────────────────────────────────────────────────────────────
// 3. REMEDIATION: Non-persons — reclassify entity_type and entity_id
//    Run per-node after manual classification. Example for a place:
// ─────────────────────────────────────────────────────────────────────────────

// Example: Reclassify "Mediterranean Region" (PLACE)
// MATCH (n:Entity {entity_id: 'person_q...'})
// SET n.entity_type = 'PLACE',
//     n.entity_id = 'plc_q...',
//     n.entity_cipher = 'ent_plc_Q...',
//     n.dq_flag = 'DQ_WRONG_ENTITY_TYPE';

// ─────────────────────────────────────────────────────────────────────────────
// 4. REMEDIATION: Mythological — add :MythologicalPerson
//    Romulus, Remus, Europa
// ─────────────────────────────────────────────────────────────────────────────

// MATCH (n:Entity)
// WHERE n.label IN ['Romulus', 'Remus', 'Europa']
//   AND n.entity_id STARTS WITH 'person_'
//   AND n.dprr_id IS NULL
// SET n:Person:MythologicalPerson,
//     n.mythological = true,
//     n.dq_flag = 'DQ_UNRESOLVED_PERSONHOOD';

// ─────────────────────────────────────────────────────────────────────────────
// 5. BIBLICAL: Queue for P31 re-fetch (no graph change until P31 confirmed)
//    Andrew the Apostle, Silas, Damaris, Aristarchus, etc.
//    Use adr007_section3_person_noise_cleanup.py --apply to write queue file
// ─────────────────────────────────────────────────────────────────────────────
