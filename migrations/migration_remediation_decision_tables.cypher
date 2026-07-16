// Migration: Architecture remediation (r1–r5)
// r1: Remove duplicate SYS_DecisionTable D20/D21
// r2: Ensure HAS_ROW for all SYS_DecisionRow
// r5: Add agent_type (SYS_AgentType), rule_id (SYS_ValidationRule)
// Run after: 17_discipline_scoring_and_kernel_patch.cypher, sys_gaps_migration.cypher

// D20 duplicates
MATCH (dt:SYS_DecisionTable {table_id: 'D20_SCORE_discipline_authority'})
WITH collect(dt) AS nodes
WHERE size(nodes) > 1
UNWIND range(1, size(nodes) - 1) AS i
DETACH DELETE nodes[i];

// D21 duplicates
MATCH (dt:SYS_DecisionTable {table_id: 'D21_SCORE_weighted_link_signals'})
WITH collect(dt) AS nodes
WHERE size(nodes) > 1
UNWIND range(1, size(nodes) - 1) AS i
DETACH DELETE nodes[i];

// ---------------------------------------------------------------------------
// R2: Ensure all SYS_DecisionRow have HAS_ROW from their table
// ---------------------------------------------------------------------------
MATCH (r:SYS_DecisionRow)
WHERE r.table_id IS NOT NULL
MATCH (dt:SYS_DecisionTable {table_id: r.table_id})
MERGE (dt)-[:HAS_ROW]->(r);

// ---------------------------------------------------------------------------
// R5: Add agent_type to SYS_AgentType, rule_id to SYS_ValidationRule
// ---------------------------------------------------------------------------
MATCH (at:SYS_AgentType)
WHERE at.agent_type IS NULL AND at.name IS NOT NULL
SET at.agent_type = at.name;

MATCH (at:SYS_AgentType)
WHERE at.agent_type IS NULL AND at.agent_type_id IS NOT NULL
SET at.agent_type = at.agent_type_id;

MATCH (vr:SYS_ValidationRule)
WHERE vr.rule_id IS NULL AND vr.name IS NOT NULL
SET vr.rule_id = vr.name;

// Verification (uncomment to run):
// MATCH (dt:SYS_DecisionTable) WHERE dt.table_id IN ['D20_SCORE_discipline_authority', 'D21_SCORE_weighted_link_signals']
// RETURN dt.table_id, count(*) AS cnt
// Expected: 1 row per table_id
//
// MATCH (dt:SYS_DecisionTable)-[:HAS_ROW]->(r:SYS_DecisionRow) RETURN dt.table_id, count(r) AS rows
//
// MATCH (at:SYS_AgentType) RETURN at.name, at.agent_type
// MATCH (vr:SYS_ValidationRule) RETURN vr.name, vr.rule_id
