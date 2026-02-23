// ============================================================================
// EXPLORE IMPORTED ENTITIES - 300 Entities from SCA
// ============================================================================

// ============================================================================
// 1. OVERVIEW STATISTICS
// ============================================================================

// Total entities
MATCH (n:Entity)
RETURN count(n) as total_entities;

// Breakdown by entity type
MATCH (n:Entity)
RETURN n.entity_type as entity_type, count(n) as count
ORDER BY count DESC;

// Federation score distribution
MATCH (n:Entity)
RETURN n.federation_score as fed_score, count(n) as count
ORDER BY fed_score DESC;

// ============================================================================
// 2. SAMPLE ENTITIES (First 20)
// ============================================================================

// First 20 with all properties
MATCH (n:Entity)
RETURN n.qid as QID,
       n.label as Label,
       n.entity_type as Type,
       n.entity_cipher as Entity_Cipher,
       n.federation_score as Fed_Score,
       n.properties_count as Properties
ORDER BY n.entity_id
LIMIT 20;

// ============================================================================
// 3. ENTITIES BY TYPE
// ============================================================================

// SubjectConcepts
MATCH (n:Entity {entity_type: 'SUBJECTCONCEPT'})
RETURN n.qid as QID, n.label as Label, n.entity_cipher as Cipher, n.federation_score as Fed
ORDER BY n.federation_score DESC
LIMIT 10;

// Places
MATCH (n:Entity {entity_type: 'PLACE'})
RETURN n.qid as QID, n.label as Label, n.entity_cipher as Cipher, n.federation_score as Fed
ORDER BY n.federation_score DESC
LIMIT 10;

// Events
MATCH (n:Entity {entity_type: 'EVENT'})
RETURN n.qid as QID, n.label as Label, n.entity_cipher as Cipher, n.federation_score as Fed
ORDER BY n.federation_score DESC
LIMIT 10;

// Concepts (abstract)
MATCH (n:Entity {entity_type: 'CONCEPT'})
RETURN n.qid as QID, n.label as Label, n.entity_cipher as Cipher, n.federation_score as Fed
ORDER BY n.federation_score DESC
LIMIT 20;

// ============================================================================
// 4. HIGH FEDERATION SCORE ENTITIES
// ============================================================================

// Entities with Fed >= 3 (well-connected to authorities)
MATCH (n:Entity)
WHERE n.federation_score >= 3
RETURN n.qid as QID,
       n.label as Label,
       n.entity_type as Type,
       n.federation_score as Fed_Score,
       n.entity_cipher as Cipher
ORDER BY n.federation_score DESC, n.label;

// ============================================================================
// 5. THE SEED ENTITY
// ============================================================================

// Roman Republic (our starting point)
MATCH (n:Entity {qid: 'Q17167'})
RETURN n.qid as QID,
       n.label as Label,
       n.entity_type as Type,
       n.entity_cipher as Cipher,
       n.federation_score as Fed,
       n.properties_count as Properties;

// ============================================================================
// 6. CIPHER VERIFICATION
// ============================================================================

// Check cipher uniqueness
MATCH (n:Entity)
WHERE n.entity_cipher IS NOT NULL
WITH n.entity_cipher as cipher, count(n) as count
WHERE count > 1
RETURN cipher, count
ORDER BY count DESC;
// Should return 0 rows (all ciphers unique)

// Test cipher-based lookup (should be instant)
MATCH (n:Entity {entity_cipher: 'ent_sub_Q17167'})
RETURN n;

// ============================================================================
// 7. ENTITY LABEL PATTERNS
// ============================================================================

// Entities with "Rome" in label
MATCH (n:Entity)
WHERE n.label IS NOT NULL AND toLower(n.label) CONTAINS 'rome'
RETURN n.qid as QID, n.label as Label, n.entity_type as Type, n.federation_score as Fed
ORDER BY n.federation_score DESC;

// Entities with "Republic" in label
MATCH (n:Entity)
WHERE n.label IS NOT NULL AND toLower(n.label) CONTAINS 'republic'
RETURN n.qid as QID, n.label as Label, n.entity_type as Type, n.federation_score as Fed
ORDER BY n.federation_score DESC;

// ============================================================================
// 8. PROPERTY COUNT ANALYSIS
// ============================================================================

// Top 10 entities by property count
MATCH (n:Entity)
RETURN n.qid as QID, n.label as Label, n.properties_count as Properties, n.entity_type as Type
ORDER BY n.properties_count DESC
LIMIT 10;

// Bottom 10 (least properties)
MATCH (n:Entity)
RETURN n.qid as QID, n.label as Label, n.properties_count as Properties, n.entity_type as Type
ORDER BY n.properties_count ASC
LIMIT 10;

// ============================================================================
// 9. NAMESPACE DISTRIBUTION
// ============================================================================

// All should be "wd" (Wikidata) for now
MATCH (n:Entity)
RETURN n.namespace as namespace, count(n) as count;

// ============================================================================
// 10. DATA QUALITY CHECKS
// ============================================================================

// Check for entities with missing critical properties
MATCH (n:Entity)
WHERE n.entity_cipher IS NULL 
   OR n.qid IS NULL 
   OR n.label IS NULL
   OR n.entity_type IS NULL
RETURN n.qid as QID, 
       n.label as Label,
       n.entity_cipher IS NULL as missing_cipher,
       n.qid IS NULL as missing_qid,
       n.label IS NULL as missing_label,
       n.entity_type IS NULL as missing_type
LIMIT 20;

// ============================================================================
// 11. SAMPLE COMPLETE ENTITY
// ============================================================================

// Show complete properties of Roman Republic
MATCH (n:Entity {qid: 'Q17167'})
RETURN n;
