// Chrystallum Data Validation Queries
// Generated: 2026-02-16T16:43:57.891922

// ========================================================================
// Check for duplicate claims (same cipher)
// ========================================================================
MATCH (c:Claim) WITH c.cipher AS cipher, COUNT(*) AS count
WHERE count > 1
RETURN cipher, count
ORDER BY count DESC;

// ========================================================================
// Check for duplicate claim IDs
// ========================================================================
MATCH (c:Claim) WITH c.claim_id AS claim_id, COUNT(*) AS count
WHERE count > 1
RETURN claim_id, count;

// ========================================================================
// Check for invalid facet keys
// ========================================================================
// Valid facet keys: 'archaeological', 'artistic', 'biographic', 'communication', 'cultural', 'demographic', 'diplomatic', 'economic', 'environmental', 'geographic', 'intellectual', 'linguistic', 'military', 'political', 'religious', 'scientific', 'social', 'technological'
MATCH (fa:FacetAssessment) WHERE NOT fa.facet IN ['archaeological', 'artistic', 'biographic', 'communication', 'cultural', 'demographic', 'diplomatic', 'economic', 'environmental', 'geographic', 'intellectual', 'linguistic', 'military', 'political', 'religious', 'scientific', 'social', 'technological']
RETURN fa.assessment_id, fa.facet
LIMIT 20;

// ========================================================================
// Check for missing facet assessments
// ========================================================================
MATCH (c:Claim) WHERE NOT (c)-[:HAS_ANALYSIS_RUN]->(:AnalysisRun)
RETURN c.claim_id, c.cipher
LIMIT 20;

// ========================================================================
// Check for invalid edge IDs (duplicates)
// ========================================================================
MATCH ()-[e:EDGE]->() WITH e.edge_id AS edge_id, COUNT(*) AS count
WHERE count > 1
RETURN edge_id, count;

// ========================================================================
// Summary statistics
// ========================================================================
MATCH (c:Claim) RETURN COUNT(c) AS total_claims;
MATCH (fa:FacetAssessment) RETURN COUNT(fa) AS total_assessments;
MATCH ()-[e:EDGE]->() RETURN COUNT(e) AS total_edges;