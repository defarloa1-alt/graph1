// Create Chrystallum Authority Federation Structure
// Based on Key Files and Architecture documentation

// ============================================================================
// STEP 1: Create Chrystallum root shell node
// ============================================================================
MERGE (chrys:Chrystallum:Root {
    id: 'CHRYSTALLUM_ROOT',
    label: 'Chrystallum',
    type: 'knowledge_graph_root',
    description: 'Root node of the Chrystallum federated knowledge graph'
});

// ============================================================================
// STEP 2: Create Federation category node
// ============================================================================
MERGE (fed_cat:Federation:Category {
    id: 'FEDERATION_CATEGORY',
    label: 'Authority Federations',
    type: 'federation_cluster',
    description: 'Federated authority systems and classification standards'
});

// ============================================================================
// STEP 3: Link Chrystallum to Federation category
// ============================================================================
MATCH (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (f:Federation:Category {id: 'FEDERATION_CATEGORY'})
MERGE (c)-[:HAS_FEDERATION_CLUSTER]->(f);

// ============================================================================
// STEP 4: Create individual authority federation nodes
// ============================================================================

// LCSH - Primary Backbone
MERGE (lcsh:Federation:AuthoritySystem {
    id: 'FED_LCSH',
    label: 'LCSH - Library of Congress Subject Headings',
    type: 'subject_classification',
    role: 'primary_backbone',
    coverage: '86% events',
    wikidata_property: 'P244',
    url: 'https://id.loc.gov/authorities/subjects.html'
});

// Dewey Decimal - Agent Routing
MERGE (dewey:Federation:AuthoritySystem {
    id: 'FED_DEWEY',
    label: 'Dewey Decimal Classification',
    type: 'hierarchical_classification',
    role: 'agent_routing',
    coverage: 'hierarchical organization',
    wikidata_property: 'P1036',
    url: 'https://www.oclc.org/en/dewey.html'
});

// LCC - Hierarchical Classification
MERGE (lcc:Federation:AuthoritySystem {
    id: 'FED_LCC',
    label: 'LCC - Library of Congress Classification',
    type: 'hierarchical_classification',
    role: 'supplementary',
    coverage: '100% history subjects',
    wikidata_property: 'P1149',
    url: 'https://www.loc.gov/aba/cataloging/classification/'
});

// FAST - Supplementary Property
MERGE (fast:Federation:AuthoritySystem {
    id: 'FED_FAST',
    label: 'FAST - Faceted Application of Subject Terminology',
    type: 'faceted_subject',
    role: 'supplementary',
    coverage: '14% events, good for entities',
    wikidata_property: 'P2163',
    url: 'https://fast.oclc.org/'
});

// Wikidata - Entity Authority
MERGE (wikidata:Federation:AuthoritySystem {
    id: 'FED_WIKIDATA',
    label: 'Wikidata',
    type: 'linked_open_data',
    role: 'entity_authority',
    coverage: 'universal entity IDs',
    wikidata_property: 'self',
    url: 'https://www.wikidata.org/'
});

// Getty AAT - Art & Architecture
MERGE (getty:Federation:AuthoritySystem {
    id: 'FED_GETTY_AAT',
    label: 'Getty AAT - Art & Architecture Thesaurus',
    type: 'domain_vocabulary',
    role: 'materials_activities',
    coverage: 'objects, materials, activities',
    wikidata_property: 'P1014',
    url: 'https://www.getty.edu/research/tools/vocabularies/aat/'
});

// Pleiades - Geographic Authority
MERGE (pleiades:Federation:AuthoritySystem {
    id: 'FED_PLEIADES',
    label: 'Pleiades Gazetteer',
    type: 'geographic_authority',
    role: 'ancient_places',
    coverage: 'ancient world geography',
    wikidata_property: 'P1584',
    url: 'https://pleiades.stoa.org/'
});

// VIAF - Name Authority
MERGE (viaf:Federation:AuthoritySystem {
    id: 'FED_VIAF',
    label: 'VIAF - Virtual International Authority File',
    type: 'name_authority',
    role: 'person_disambiguation',
    coverage: 'international name variants',
    wikidata_property: 'P214',
    url: 'http://viaf.org/'
});

// CIDOC-CRM - Cultural Heritage Ontology
MERGE (cidoc:Federation:AuthoritySystem {
    id: 'FED_CIDOC_CRM',
    label: 'CIDOC-CRM',
    type: 'ontology_standard',
    role: 'cultural_heritage',
    coverage: 'museum/heritage semantics',
    wikidata_property: 'aligned',
    url: 'https://www.cidoc-crm.org/'
});

// ============================================================================
// STEP 5: Create IS_COMPOSED_OF relationships
// ============================================================================

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (lcsh:Federation {id: 'FED_LCSH'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'primary_backbone',
    priority: 1
}]->(lcsh);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (dewey:Federation {id: 'FED_DEWEY'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'agent_routing',
    priority: 2
}]->(dewey);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (lcc:Federation {id: 'FED_LCC'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'classification',
    priority: 3
}]->(lcc);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (fast:Federation {id: 'FED_FAST'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'supplementary',
    priority: 4
}]->(fast);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (wikidata:Federation {id: 'FED_WIKIDATA'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'entity_authority',
    priority: 1
}]->(wikidata);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (getty:Federation {id: 'FED_GETTY_AAT'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'domain_vocabulary',
    priority: 5
}]->(getty);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (pleiades:Federation {id: 'FED_PLEIADES'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'geographic_authority',
    priority: 6
}]->(pleiades);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (viaf:Federation {id: 'FED_VIAF'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'name_authority',
    priority: 7
}]->(viaf);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (cidoc:Federation:AuthoritySystem {id: 'FED_CIDOC_CRM'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'ontology_standard',
    priority: 8
}]->(cidoc);

// ============================================================================
// Verification: View the structure
// ============================================================================

MATCH path = (c:Chrystallum)-[:HAS_FEDERATION_CLUSTER]->(cat:Federation:Category)-[:IS_COMPOSED_OF]->(fed:Federation:AuthoritySystem)
RETURN path;

// Table view
MATCH (c:Chrystallum)-[:HAS_FEDERATION_CLUSTER]->(cat:Federation:Category)-[:IS_COMPOSED_OF]->(fed:Federation:AuthoritySystem)
RETURN 
    c.label as Root,
    cat.label as Category,
    fed.label as Federation,
    fed.role as Role,
    fed.coverage as Coverage
ORDER BY fed.id;

