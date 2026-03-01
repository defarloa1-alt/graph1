// ============================================================================
// WIRE BIBLIOGRAPHY BRANCH
// ============================================================================
// If BibliographySource nodes exist, create BibliographyRegistry and link
// Chrystallum -[:HAS_BIBLIOGRAPHY]-> registry -[:CONTAINS]-> each source.
// Safe to run multiple times (MERGE).
// ============================================================================

MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MERGE (br:BibliographyRegistry {id: 'BIBLIO_REGISTRY'})
ON CREATE SET br.label = 'Bibliography Registry', br.system = true
MERGE (c)-[:HAS_BIBLIOGRAPHY]->(br);

MATCH (b:BibliographySource)
MATCH (br:BibliographyRegistry {id: 'BIBLIO_REGISTRY'})
MERGE (br)-[:CONTAINS]->(b);
