// D-031: Add facet_key to forbidden-facet SYS_Policy nodes
// Run BEFORE refactoring sca_agent.py and subject_concept_facet_agents.py
// Step 1 in D-031 build order

// Add facet_key to existing policies
MATCH (p:SYS_Policy {name: 'NoTemporalFacet'})
SET p.facet_key = 'TEMPORAL';

MATCH (p:SYS_Policy {name: 'NoClassificationFacet'})
SET p.facet_key = 'CLASSIFICATION';

// Create NoPatronageFacet and NoGenealogicalFacet if missing, then set facet_key
MERGE (p:SYS_Policy {name: 'NoPatronageFacet'})
SET p.description = 'PATRONAGE is NOT a facet — use social/diplomatic facets',
    p.facet_key = 'PATRONAGE',
    p.decision_table = 'D8_DETERMINE_SFA_facet_assignment',
    p.active = true,
    p.system = true;

MERGE (p:SYS_Policy {name: 'NoGenealogicalFacet'})
SET p.description = 'GENEALOGICAL is NOT a facet — use social/biographic facets',
    p.facet_key = 'GENEALOGICAL',
    p.decision_table = 'D8_DETERMINE_SFA_facet_assignment',
    p.active = true,
    p.system = true;
