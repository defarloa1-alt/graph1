# Scaffold Constraints and Indexes (Cypher DDL)
// NOTE:
// - This file uses Neo4j Cypher DDL despite the .sql extension.
// - Scope is scaffold-layer labels only.
// - Canonical labels/constraints remain in Neo4j/schema/*.cypher.

// ===============================
// ScaffoldNode constraints
// ===============================

// Single scaffold node per (analysis_run_id, qid)
CREATE CONSTRAINT scaffoldnode_run_qid_unique IF NOT EXISTS
FOR (n:ScaffoldNode)
REQUIRE (n.analysis_run_id, n.qid) IS UNIQUE;

CREATE CONSTRAINT scaffoldnode_analysis_run_id_exists IF NOT EXISTS
FOR (n:ScaffoldNode)
REQUIRE n.analysis_run_id IS NOT NULL;

CREATE CONSTRAINT scaffoldnode_qid_exists IF NOT EXISTS
FOR (n:ScaffoldNode)
REQUIRE n.qid IS NOT NULL;

// ===============================
// ScaffoldEdge constraints
// ===============================

CREATE CONSTRAINT scaffoldedge_id_unique IF NOT EXISTS
FOR (e:ScaffoldEdge)
REQUIRE e.edge_id IS UNIQUE;

CREATE CONSTRAINT scaffoldedge_id_exists IF NOT EXISTS
FOR (e:ScaffoldEdge)
REQUIRE e.edge_id IS NOT NULL;

CREATE CONSTRAINT scaffoldedge_analysis_run_id_exists IF NOT EXISTS
FOR (e:ScaffoldEdge)
REQUIRE e.analysis_run_id IS NOT NULL;

CREATE CONSTRAINT scaffoldedge_relationship_type_exists IF NOT EXISTS
FOR (e:ScaffoldEdge)
REQUIRE e.relationship_type IS NOT NULL;

// ===============================
// Scaffold indexes
// ===============================

CREATE INDEX scaffoldnode_run_idx IF NOT EXISTS
FOR (n:ScaffoldNode)
ON (n.analysis_run_id);

CREATE INDEX scaffoldnode_qid_idx IF NOT EXISTS
FOR (n:ScaffoldNode)
ON (n.qid);

CREATE INDEX scaffoldedge_run_idx IF NOT EXISTS
FOR (e:ScaffoldEdge)
ON (e.analysis_run_id);

CREATE INDEX scaffoldedge_relationship_type_idx IF NOT EXISTS
FOR (e:ScaffoldEdge)
ON (e.relationship_type);

CREATE INDEX scaffoldedge_wd_property_idx IF NOT EXISTS
FOR (e:ScaffoldEdge)
ON (e.wd_property);

// ===============================
// Connectivity convention
// ===============================
// (edge:ScaffoldEdge)-[:FROM]->(source:ScaffoldNode)
// (edge:ScaffoldEdge)-[:TO]->(target:ScaffoldNode)

// ===============================
// AnalysisRun note
// ===============================
// Reuse canonical AnalysisRun constraints/indexes from Neo4j/schema/*.cypher.
// Avoid redefining them here to prevent duplicate ownership of canonical schema.
