// Neo4j Cleanup Script - Remove Duplicate Entities
// Created: 2026-02-21
// Purpose: Remove 50 duplicate entity nodes identified in QA testing
//
// CRITICAL: This script will DELETE 50 nodes from the database
// Strategy: Keep the EARLIEST import, delete the later duplicates
//
// Run this script AFTER backing up your database or confirming in test environment

// ============================================================================
// PART 1: Preview Duplicates (DRY RUN)
// ============================================================================
// Uncomment to see what will be deleted:
/*
MATCH (n:Entity)
WITH n.qid as qid, collect(n) as nodes
WHERE size(nodes) > 1
WITH qid, nodes, 
     [n in nodes | {id: n.entity_id, imported: n.imported_at, label: n.label}] as node_details,
     min([n in nodes | n.imported_at]) as keep_time
RETURN qid, size(nodes) as duplicate_count, node_details, keep_time
ORDER BY qid
*/

// ============================================================================
// PART 2: Remove Duplicates (EXECUTION)
// ============================================================================
// Strategy: For each QID with multiple nodes, keep the oldest, delete the rest

MATCH (n:Entity)
WITH n.qid as qid, collect(n) as nodes
WHERE size(nodes) > 1
WITH qid, nodes, min([n in nodes | n.imported_at]) as keep_time
UNWIND nodes as node
WITH node, keep_time
WHERE node.imported_at > keep_time  // Delete only newer duplicates
DETACH DELETE node;

// ============================================================================
// PART 3: Verification Query
// ============================================================================
// Run after cleanup to verify no duplicates remain

// Check total entities
MATCH (n:Entity)
RETURN count(n) as total_entities,
       count(DISTINCT n.qid) as unique_qids,
       count(DISTINCT n.entity_cipher) as unique_ciphers;
// Expected: All three counts should be 300

// Check for any remaining duplicates
MATCH (n:Entity)
WITH n.qid as qid, count(n) as node_count
WHERE node_count > 1
RETURN count(qid) as remaining_duplicates;
// Expected: 0

// ============================================================================
// PART 4: Add Uniqueness Constraints (RECOMMENDED)
// ============================================================================
// Prevents future duplicate imports

CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS
FOR (n:Entity) REQUIRE n.qid IS UNIQUE;

CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (n:Entity) REQUIRE n.entity_id IS UNIQUE;

CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS
FOR (n:Entity) REQUIRE n.entity_cipher IS UNIQUE;

// ============================================================================
// Expected Results After Cleanup:
// - Total Entity nodes: 300 (down from 350)
// - Unique QIDs: 300
// - Unique Ciphers: 300
// - Duplicate count: 0
// ============================================================================
