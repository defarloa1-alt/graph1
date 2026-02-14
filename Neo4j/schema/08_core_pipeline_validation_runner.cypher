// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: CORE PIPELINE VALIDATION INVENTORY (PHASE 1)
// ============================================================================
// File: 08_core_pipeline_validation_runner.cypher
// Purpose: Browser-safe inventory for environments where SHOW cannot be chained
//          with WITH/CALL subqueries.
// Usage:
// 1) Run statement 1 and copy results.
// 2) Run statement 2 and copy results.
// 3) For automatic PASS/FAIL, run:
//    python Neo4j/schema/08_core_pipeline_validation_runner.py
// ============================================================================

SHOW CONSTRAINTS YIELD name, type, entityType, labelsOrTypes, properties
RETURN name, type, entityType, labelsOrTypes, properties
ORDER BY name;

SHOW INDEXES YIELD name, type, state, owningConstraint, entityType, labelsOrTypes, properties
WHERE type <> 'LOOKUP' AND (owningConstraint IS NULL OR owningConstraint = '')
RETURN name, type, state, owningConstraint, entityType, labelsOrTypes, properties
ORDER BY name;

