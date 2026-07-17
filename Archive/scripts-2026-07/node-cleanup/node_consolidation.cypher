// ===================================================================
// NODE TYPE CONSOLIDATION SCRIPTS
// Date: July 16, 2026
// Purpose: Consolidate duplicate node types (PERSON→Person, EVENT→Event)
// IMPORTANT: Run investigation script first!
// ===================================================================

// ===================================================================
// DRY RUN MODE: PERSON → Person Consolidation
// ===================================================================

// Show what WILL be consolidated (preview)
MATCH (p:PERSON)
OPTIONAL MATCH (p)-[r_out]->(target)
OPTIONAL MATCH (source)<-[r_in]-(p)
RETURN 
    'DRY RUN: PERSON → Person' as Action,
    p.id as NodeId,
    labels(p) as CurrentLabels,
    keys(p) as Properties,
    count(DISTINCT r_out) as OutgoingRelCount,
    count(DISTINCT r_in) as IncomingRelCount,
    collect(DISTINCT type(r_out))[0..5] as SampleOutgoingRels,
    collect(DISTINCT type(r_in))[0..5] as SampleIncomingRels;

// Count what will be affected
MATCH (p:PERSON)
RETURN 
    'PERSON → Person Summary' as Action,
    count(p) as NodesToConsolidate,
    count(DISTINCT p.id) as UniqueIds;


// ===================================================================
// ACTUAL CONSOLIDATION: PERSON → Person
// ===================================================================
// UNCOMMENT BELOW TO EXECUTE (after reviewing dry run)

// MATCH (p:PERSON)
// SET p:Person
// REMOVE p:PERSON
// RETURN count(p) as NodesConsolidated;

// // Verify consolidation
// MATCH (p:PERSON)
// RETURN count(p) as RemainingPERSONNodes;


// ===================================================================
// DRY RUN MODE: EVENT → Event Consolidation
// ===================================================================

// Show what WILL be consolidated (preview)
MATCH (e:EVENT)
OPTIONAL MATCH (e)-[r_out]->(target)
OPTIONAL MATCH (source)<-[r_in]-(e)
RETURN 
    'DRY RUN: EVENT → Event' as Action,
    e.id as NodeId,
    labels(e) as CurrentLabels,
    keys(e) as Properties,
    count(DISTINCT r_out) as OutgoingRelCount,
    count(DISTINCT r_in) as IncomingRelCount,
    collect(DISTINCT type(r_out))[0..5] as SampleOutgoingRels,
    collect(DISTINCT type(r_in))[0..5] as SampleIncomingRels;

// Count what will be affected
MATCH (e:EVENT)
RETURN 
    'EVENT → Event Summary' as Action,
    count(e) as NodesToConsolidate,
    count(DISTINCT e.id) as UniqueIds;


// ===================================================================
// ACTUAL CONSOLIDATION: EVENT → Event
// ===================================================================
// UNCOMMENT BELOW TO EXECUTE (after reviewing dry run)

// MATCH (e:EVENT)
// SET e:Event
// REMOVE e:EVENT
// RETURN count(e) as NodesConsolidated;

// // Verify consolidation
// MATCH (e:EVENT)
// RETURN count(e) as RemainingEVENTNodes;


// ===================================================================
// POST-CONSOLIDATION VERIFICATION
// ===================================================================

// After consolidation, verify Person label
// MATCH (p:Person)
// RETURN count(p) as TotalPersonNodes;

// After consolidation, verify Event label
// MATCH (e:Event)
// RETURN count(e) as TotalEventNodes;

// Check for any remaining uppercase duplicates
// MATCH (n)
// WHERE 'PERSON' IN labels(n) OR 'EVENT' IN labels(n)
// RETURN labels(n) as RemainingUppercaseLabels, count(n) as Count;


// ===================================================================
// ROLLBACK SCRIPTS (if needed)
// ===================================================================

// If PERSON consolidation needs rollback (requires tracking which were consolidated)
// Note: This is approximate - true rollback would need transaction log or backup

// // Restore PERSON label to previously consolidated nodes
// // (Only works if you kept IDs)
// MATCH (p:Person)
// WHERE p.id IN ['id1', 'id2'] // Replace with actual IDs
// SET p:PERSON
// RETURN count(p) as NodesRolledBack;
