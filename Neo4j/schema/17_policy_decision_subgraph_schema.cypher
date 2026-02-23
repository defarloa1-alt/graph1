// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: POLICY DECISION SUBGRAPH
// ============================================================================
// File: 17_policy_decision_subgraph_schema.cypher
// Purpose:
// - Read-only policy-subgraph support for ordered decision-table governance
// - Hash-pinned policy versions for deterministic Pi evaluation traceability
// Created: 2026-02-18
// Status: Draft / additive
// ============================================================================

// ---------------------------------------------------------------------------
// UNIQUENESS CONSTRAINTS
// ---------------------------------------------------------------------------

CREATE CONSTRAINT policy_version_hash_unique IF NOT EXISTS
FOR (pv:PolicyVersion) REQUIRE pv.policy_hash IS UNIQUE;

CREATE CONSTRAINT decision_table_id_unique IF NOT EXISTS
FOR (dt:DecisionTable) REQUIRE dt.table_id IS UNIQUE;

CREATE CONSTRAINT decision_rule_id_unique IF NOT EXISTS
FOR (dr:DecisionRule) REQUIRE dr.rule_id IS UNIQUE;

CREATE CONSTRAINT decision_condition_id_unique IF NOT EXISTS
FOR (dc:DecisionCondition) REQUIRE dc.condition_id IS UNIQUE;

CREATE CONSTRAINT decision_outcome_id_unique IF NOT EXISTS
FOR (do:DecisionOutcome) REQUIRE do.outcome_id IS UNIQUE;

// ---------------------------------------------------------------------------
// REQUIRED PROPERTIES
// ---------------------------------------------------------------------------

CREATE CONSTRAINT policy_version_has_policy_id IF NOT EXISTS
FOR (pv:PolicyVersion) REQUIRE pv.policy_id IS NOT NULL;

CREATE CONSTRAINT policy_version_has_mode IF NOT EXISTS
FOR (pv:PolicyVersion) REQUIRE pv.evaluation_mode IS NOT NULL;

CREATE CONSTRAINT decision_table_has_policy_hash IF NOT EXISTS
FOR (dt:DecisionTable) REQUIRE dt.policy_hash IS NOT NULL;

CREATE CONSTRAINT decision_rule_has_row_id IF NOT EXISTS
FOR (dr:DecisionRule) REQUIRE dr.row_id IS NOT NULL;

CREATE CONSTRAINT decision_rule_has_order IF NOT EXISTS
FOR (dr:DecisionRule) REQUIRE dr.rule_order IS NOT NULL;

CREATE CONSTRAINT decision_condition_has_field IF NOT EXISTS
FOR (dc:DecisionCondition) REQUIRE dc.field IS NOT NULL;

CREATE CONSTRAINT decision_condition_has_operator IF NOT EXISTS
FOR (dc:DecisionCondition) REQUIRE dc.operator IS NOT NULL;

CREATE CONSTRAINT decision_outcome_has_field IF NOT EXISTS
FOR (do:DecisionOutcome) REQUIRE do.field IS NOT NULL;

// ---------------------------------------------------------------------------
// INDEXES
// ---------------------------------------------------------------------------

CREATE INDEX policy_version_id_index IF NOT EXISTS
FOR (pv:PolicyVersion) ON (pv.policy_id);

CREATE INDEX decision_table_policy_hash_index IF NOT EXISTS
FOR (dt:DecisionTable) ON (dt.policy_hash);

CREATE INDEX decision_table_key_index IF NOT EXISTS
FOR (dt:DecisionTable) ON (dt.table_key);

CREATE INDEX decision_rule_lookup_index IF NOT EXISTS
FOR (dr:DecisionRule) ON (dr.policy_hash, dr.table_key, dr.rule_order);

CREATE INDEX decision_condition_field_index IF NOT EXISTS
FOR (dc:DecisionCondition) ON (dc.field, dc.operator);

CREATE INDEX decision_outcome_field_index IF NOT EXISTS
FOR (do:DecisionOutcome) ON (do.field);

// ---------------------------------------------------------------------------
// NOTES
// ---------------------------------------------------------------------------
// 1) Loader should treat policy subgraph as append-safe by policy_hash.
// 2) Pi runtime should pin to explicit policy_hash, not "latest".
// 3) Mutations to active policy versions must go through governance workflow.
