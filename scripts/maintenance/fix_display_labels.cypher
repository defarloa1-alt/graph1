// ============================================================================
// FIX DISPLAY LABELS — Tribe, SYS_PropertyMapping, Cognomen
// ============================================================================
// 1. Tribe: set label = label_latin (full name) so UI shows "Clustumina" not "Clu."
// 2. SYS_PropertyMapping: set label = property_label so UI shows "instance of" not description
// 3. Cognomen: strip trailing ? from cognomen_id/label_latin (uncertain cognomens)
// Run: python scripts/neo4j/run_cypher_file.py scripts/maintenance/fix_display_labels.cypher
// ============================================================================

// 1. Tribe — use full name for display
MATCH (t:Tribe)
WHERE t.label_latin IS NOT NULL
SET t.label = t.label_latin;

// 1b. Cognomen — ensure label for display (label_latin or cognomen_id)
MATCH (c:Cognomen)
SET c.label = coalesce(c.label_latin, c.cognomen_id);

// 2. PropertyMapping / SYS_PropertyMapping — use property_label for display
MATCH (pm)
WHERE (pm:PropertyMapping OR pm:SYS_PropertyMapping) AND pm.property_label IS NOT NULL
SET pm.label = pm.property_label;

// 3. Cognomen — strip trailing ? from uncertain cognomens (one-time migration)
// 3a: Migrate relationships to new nodes with stripped cognomen_id
MATCH (p:Person)-[r:HAS_COGNOMEN]->(c:Cognomen)
WHERE c.cognomen_id ENDS WITH '?'
WITH c, r, trim(replace(c.cognomen_id, '?', '')) AS clean_id, p
WHERE clean_id <> ''
MERGE (c2:Cognomen {cognomen_id: clean_id})
SET c2.label_latin = coalesce(trim(replace(c.label_latin, '?', '')), clean_id),
    c2.label = coalesce(trim(replace(c.label_latin, '?', '')), clean_id)
MERGE (p)-[:HAS_COGNOMEN]->(c2)
DELETE r;

// 3b: Delete orphaned Cognomen nodes (had ? in id)
MATCH (c:Cognomen)
WHERE c.cognomen_id ENDS WITH '?' AND NOT ()-[:HAS_COGNOMEN]->(c)
DETACH DELETE c;
