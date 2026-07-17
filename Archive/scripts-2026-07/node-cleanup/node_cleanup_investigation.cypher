// ===================================================================
// NODE TYPE CLEANUP INVESTIGATION
// Date: July 16, 2026
// Purpose: Investigate node types before cleanup
// ===================================================================

// ===================================================================
// PART 1: VERIFY EMPTY NODE TYPES (46 types identified)
// ===================================================================

// List all node types that have 0 nodes
// This generates a verification report
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) as cnt', {})
YIELD value
WITH label, value.cnt as nodeCount
WHERE nodeCount = 0
RETURN label as EmptyNodeType
ORDER BY label;

// Count empty node types
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) as cnt', {})
YIELD value
WITH label, value.cnt as nodeCount
WHERE nodeCount = 0
RETURN count(label) as TotalEmptyTypes;


// ===================================================================
// PART 2: PROPOSED EDGE DEEP INVESTIGATION
// ===================================================================

// Basic stats on ProposedEdge
MATCH (pe:ProposedEdge)
RETURN 
    count(pe) as TotalProposedEdge,
    count(DISTINCT labels(pe)) as LabelCombinations;

// Check ProposedEdge properties
MATCH (pe:ProposedEdge)
WITH pe LIMIT 10
RETURN pe, labels(pe), keys(pe);

// Check ProposedEdge relationships (incoming and outgoing)
MATCH (pe:ProposedEdge)
WITH pe LIMIT 1
OPTIONAL MATCH (pe)-[r]->()
WITH pe, collect(DISTINCT type(r)) as outgoingTypes
OPTIONAL MATCH (pe)<-[r2]-()
RETURN 
    labels(pe) as labels,
    keys(pe) as properties,
    outgoingTypes as outgoingRelTypes,
    collect(DISTINCT type(r2)) as incomingRelTypes;

// Count relationship patterns for ALL ProposedEdge nodes
MATCH (pe:ProposedEdge)
OPTIONAL MATCH (pe)-[r_out]->()
OPTIONAL MATCH (pe)<-[r_in]-()
WITH pe, 
     collect(DISTINCT type(r_out)) as outTypes,
     collect(DISTINCT type(r_in)) as inTypes
RETURN 
    count(pe) as nodeCount,
    outTypes,
    inTypes,
    count(DISTINCT outTypes + inTypes) as uniqueRelPatterns;

// Find ProposedEdge nodes that are orphaned (no relationships)
MATCH (pe:ProposedEdge)
WHERE NOT (pe)-[]-()
RETURN count(pe) as OrphanedProposedEdge;

// Compare ProposedEdge to Claim nodes
MATCH (c:Claim)
WITH count(c) as claimCount
MATCH (pe:ProposedEdge)
WITH claimCount, count(pe) as proposedEdgeCount
RETURN 
    claimCount,
    proposedEdgeCount,
    claimCount = proposedEdgeCount as CountsMatch;

// Check if ProposedEdge has any overlapping IDs with Claims
MATCH (c:Claim)
WITH collect(c.id) as claimIds
MATCH (pe:ProposedEdge)
WHERE pe.id IN claimIds
RETURN count(pe) as OverlappingIds;

// Sample ProposedEdge properties vs Claim properties
MATCH (pe:ProposedEdge)
WITH pe LIMIT 5
WITH collect({
    type: 'ProposedEdge',
    id: pe.id,
    properties: keys(pe)
}) as proposedSamples
MATCH (c:Claim)
WITH proposedSamples, c LIMIT 5
RETURN 
    proposedSamples,
    collect({
        type: 'Claim',
        id: c.id,
        properties: keys(c)
    }) as claimSamples;

// Check creation timestamps on ProposedEdge
MATCH (pe:ProposedEdge)
RETURN 
    min(pe.created_at) as earliest,
    max(pe.created_at) as latest,
    count(DISTINCT pe.created_at) as uniqueTimestamps
WHERE pe.created_at IS NOT NULL;


// ===================================================================
// PART 3: DUPLICATE NODE TYPE ANALYSIS
// ===================================================================

// PERSON vs Person investigation
MATCH (p:PERSON)
RETURN 
    'PERSON (uppercase)' as NodeType,
    count(p) as Count,
    collect(p.id) as Ids,
    collect(keys(p)) as PropertySets LIMIT 1;

MATCH (p:Person)
RETURN 
    'Person (propercase)' as NodeType,
    count(p) as Count;

// Sample PERSON nodes to understand what they are
MATCH (p:PERSON)
OPTIONAL MATCH (p)-[r]->(target)
RETURN 
    p,
    labels(p) as labels,
    keys(p) as properties,
    collect({rel: type(r), target: labels(target)}) as relationships;

// EVENT vs Event investigation
MATCH (e:EVENT)
RETURN 
    'EVENT (uppercase)' as NodeType,
    count(e) as Count,
    collect(e.id) as Ids,
    collect(keys(e)) as PropertySets LIMIT 1;

MATCH (e:Event)
RETURN 
    'Event (propercase)' as NodeType,
    count(e) as Count;

// Sample EVENT nodes to understand what they are
MATCH (e:EVENT)
OPTIONAL MATCH (e)-[r]->(target)
RETURN 
    e,
    labels(e) as labels,
    keys(e) as properties,
    collect({rel: type(r), target: labels(target)}) as relationships;


// ===================================================================
// PART 4: CHECK FOR MULTI-LABELED NODES
// ===================================================================

// Check if any PERSON nodes have both PERSON and Person labels
MATCH (p:PERSON)
WHERE p:Person
RETURN count(p) as NodesWithBothLabels;

// Check if any EVENT nodes have both EVENT and Event labels
MATCH (e:EVENT)
WHERE e:Event
RETURN count(e) as NodesWithBothLabels;


// ===================================================================
// PART 5: MATERIAL AND OBJECT VERIFICATION
// ===================================================================

// Verify Material is empty (user wants to keep)
MATCH (m:Material)
RETURN count(m) as MaterialCount;

// Verify Object is empty (user wants to keep)
MATCH (o:Object)
RETURN count(o) as ObjectCount;


// ===================================================================
// SUMMARY REPORT QUERY
// ===================================================================

// Generate complete investigation summary
WITH [
    {category: 'Empty Types', query: 'CALL db.labels() YIELD label CALL apoc.cypher.run(\'MATCH (n:`\' + label + \'`) RETURN count(n) as cnt\', {}) YIELD value WITH label, value.cnt as nodeCount WHERE nodeCount = 0 RETURN count(label)'},
    {category: 'ProposedEdge Count', query: 'MATCH (pe:ProposedEdge) RETURN count(pe)'},
    {category: 'Claim Count', query: 'MATCH (c:Claim) RETURN count(c)'},
    {category: 'PERSON Count', query: 'MATCH (p:PERSON) RETURN count(p)'},
    {category: 'Person Count', query: 'MATCH (p:Person) RETURN count(p)'},
    {category: 'EVENT Count', query: 'MATCH (e:EVENT) RETURN count(e)'},
    {category: 'Event Count', query: 'MATCH (e:Event) RETURN count(e)'}
] as checks
RETURN checks;
