// ============================================================================
// GRAPH VISUALIZATION QUERIES - Neo4j Browser
// ============================================================================
// These return nodes and relationships for visual graph view
// Run in Neo4j Browser to see network diagrams
// ============================================================================


// ============================================================================
// 1. COMPLETE NETWORK (All 300 entities)
// ============================================================================

MATCH (n:Entity)
RETURN n
LIMIT 300;

// Note: This shows all entities but no relationships yet
// Will be a scatter of disconnected nodes


// ============================================================================
// 2. HIGH-VALUE ENTITIES (Fed >= 3)
// ============================================================================

MATCH (n:Entity)
WHERE n.federation_score >= 3
RETURN n;

// Shows 71 well-connected entities
// Color-coded by entity_type in Neo4j Browser


// ============================================================================
// 3. ENTITIES BY TYPE (Color-coded)
// ============================================================================

// All Places
MATCH (p:Entity {entity_type: 'PLACE'})
RETURN p;

// All SubjectConcepts
MATCH (s:Entity {entity_type: 'SUBJECTCONCEPT'})
RETURN s;

// All Events
MATCH (e:Entity {entity_type: 'EVENT'})
RETURN e;

// All People
MATCH (h:Entity {entity_type: 'PERSON'})
RETURN h;


// ============================================================================
// 4. SEED ENTITY AND ITS CONTEXT
// ============================================================================

// Roman Republic (seed) + nearby entities
MATCH (seed:Entity {qid: 'Q17167'})
OPTIONAL MATCH (other:Entity)
WHERE other.qid IN ['Q1747689', 'Q220', 'Q201038', 'Q2277', 'Q206414', 
                     'Q2839628', 'Q6106068', 'Q2815472']
RETURN seed, other;

// Shows Roman Republic + Ancient Rome + Rome + Kingdom/Empire + Early/Middle/Late


// ============================================================================
// 5. TOP 20 BY FEDERATION SCORE
// ============================================================================

MATCH (n:Entity)
WHERE n.federation_score >= 2
RETURN n
ORDER BY n.federation_score DESC, n.properties_count DESC
LIMIT 20;


// ============================================================================
// 6. GEOGRAPHIC NETWORK (Places + High-value entities)
// ============================================================================

MATCH (p:Entity {entity_type: 'PLACE'})
WHERE p.federation_score >= 2
RETURN p;

// Shows 16 places, those with Fed >= 2 are well-documented


// ============================================================================
// 7. HISTORICAL PERIODS (SubjectConcepts)
// ============================================================================

MATCH (s:Entity {entity_type: 'SUBJECTCONCEPT'})
RETURN s;

// Shows all 12 historical periods discovered


// ============================================================================
// 8. SAMPLE DIVERSE NETWORK
// ============================================================================

// Get variety of entity types
MATCH (place:Entity {entity_type: 'PLACE'})
WITH place LIMIT 5
MATCH (period:Entity {entity_type: 'SUBJECTCONCEPT'})
WITH place, period LIMIT 3
MATCH (event:Entity {entity_type: 'EVENT'})
WITH place, period, event LIMIT 2
MATCH (person:Entity {entity_type: 'PERSON'})
WITH place, period, event, person LIMIT 2
RETURN place, period, event, person;


// ============================================================================
// 9. FEDERATION SCORE SPECTRUM
// ============================================================================

// Sample from each federation score level
MATCH (fed5:Entity {federation_score: 5})
WITH fed5 LIMIT 3
MATCH (fed4:Entity {federation_score: 4})
WITH fed5, fed4 LIMIT 3
MATCH (fed3:Entity {federation_score: 3})
WITH fed5, fed4, fed3 LIMIT 3
MATCH (fed2:Entity {federation_score: 2})
WITH fed5, fed4, fed3, fed2 LIMIT 3
MATCH (fed1:Entity {federation_score: 1})
WITH fed5, fed4, fed3, fed2, fed1 LIMIT 3
RETURN fed5, fed4, fed3, fed2, fed1;

// Shows 15 entities across all federation levels


// ============================================================================
// 10. SEARCH BY NAME
// ============================================================================

// Find specific entities by name
MATCH (n:Entity)
WHERE n.label CONTAINS 'Rome'
   OR n.label CONTAINS 'Greek'
   OR n.label CONTAINS 'Republic'
RETURN n
LIMIT 30;


// ============================================================================
// TIPS FOR NEO4J BROWSER:
// ============================================================================

// After running a query:
// - Click nodes to see properties
// - Right-click for options
// - Use layout buttons to organize
// - Color nodes by entity_type (in settings)
// - Expand/collapse groups

// To customize display:
// 1. Run query
// 2. Click gear icon at bottom
// 3. Set caption to: {label}
// 4. Set color by: entity_type
// 5. Set size by: federation_score
