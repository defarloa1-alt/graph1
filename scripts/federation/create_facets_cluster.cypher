// Create Facets Subcluster Structure
// 18 Canonical Facets from ADR-004

// ============================================================================
// STEP 1: Create Facets category shell node
// ============================================================================
MERGE (facets_cat:Facets:Category {
    id: 'FACETS_CATEGORY',
    label: 'Canonical Facets',
    type: 'facet_cluster',
    description: '18 canonical analytical dimensions for entity classification',
    facet_count: 18,
    source_adr: 'ADR_004_Canonical_18_Facet_System'
});

// ============================================================================
// STEP 2: Link Chrystallum root to Facets category
// ============================================================================
MATCH (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (f:Facets:Category {id: 'FACETS_CATEGORY'})
MERGE (c)-[:HAS_FACET_CLUSTER {
    cluster_type: 'analytical_dimensions',
    description: '18-facet system for multi-dimensional classification'
}]->(f);

// ============================================================================
// STEP 3: Create 18 canonical facet nodes
// ============================================================================

// 1. ARCHAEOLOGICAL
MERGE (f1:ArchaeologicalFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_ARCHAEOLOGICAL',
    key: 'ARCHAEOLOGICAL',
    label: 'Archaeological',
    description: 'Material-culture periods, stratigraphy, typologies'
});

// 2. ARTISTIC
MERGE (f2:ArtisticFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_ARTISTIC',
    key: 'ARTISTIC',
    label: 'Artistic',
    description: 'Art movements, architectural styles, aesthetic regimes'
});

// 3. BIOGRAPHIC
MERGE (f3:BiographicFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_BIOGRAPHIC',
    key: 'BIOGRAPHIC',
    label: 'Biographic',
    description: 'Personal history, biography, life events, careers, genealogy'
});

// 4. CULTURAL
MERGE (f4:CulturalFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_CULTURAL',
    key: 'CULTURAL',
    label: 'Cultural',
    description: 'Cultural eras, shared practices, identity, literature, arts'
});

// 5. DEMOGRAPHIC
MERGE (f5:DemographicFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_DEMOGRAPHIC',
    key: 'DEMOGRAPHIC',
    label: 'Demographic',
    description: 'Population structure, migration, urbanization waves'
});

// 6. DIPLOMATIC
MERGE (f6:DiplomaticFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_DIPLOMATIC',
    key: 'DIPLOMATIC',
    label: 'Diplomatic',
    description: 'International systems, alliances, treaty regimes'
});

// 7. ECONOMIC
MERGE (f7:EconomicFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_ECONOMIC',
    key: 'ECONOMIC',
    label: 'Economic',
    description: 'Economic systems, trade regimes, financial structures'
});

// 8. ENVIRONMENTAL
MERGE (f8:EnvironmentalFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_ENVIRONMENTAL',
    key: 'ENVIRONMENTAL',
    label: 'Environmental',
    description: 'Climate regimes, ecological shifts, environmental phases'
});

// 9. GEOGRAPHIC
MERGE (f9:GeographicFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_GEOGRAPHIC',
    key: 'GEOGRAPHIC',
    label: 'Geographic',
    description: 'Spatial organization, territorial control, geographic regions'
});

// 10. INTELLECTUAL
MERGE (f10:IntellectualFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_INTELLECTUAL',
    key: 'INTELLECTUAL',
    label: 'Intellectual',
    description: 'Schools of thought, philosophical or scholarly movements'
});

// 11. LINGUISTIC
MERGE (f11:LinguisticFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_LINGUISTIC',
    key: 'LINGUISTIC',
    label: 'Linguistic',
    description: 'Language families, scripts, linguistic shifts'
});

// 12. MILITARY
MERGE (f12:MilitaryFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_MILITARY',
    key: 'MILITARY',
    label: 'Military',
    description: 'Warfare, conquests, military systems, strategic eras'
});

// 13. POLITICAL
MERGE (f13:PoliticalFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_POLITICAL',
    key: 'POLITICAL',
    label: 'Political',
    description: 'Periods defined by states, regimes, dynasties, governance'
});

// 14. RELIGIOUS
MERGE (f14:ReligiousFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_RELIGIOUS',
    key: 'RELIGIOUS',
    label: 'Religious',
    description: 'Religious movements, institutions, doctrinal eras'
});

// 15. SCIENTIFIC
MERGE (f15:ScientificFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_SCIENTIFIC',
    key: 'SCIENTIFIC',
    label: 'Scientific',
    description: 'Scientific paradigms, revolutions, epistemic frameworks'
});

// 16. SOCIAL
MERGE (f16:SocialFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_SOCIAL',
    key: 'SOCIAL',
    label: 'Social',
    description: 'Social norms, class structures, social movements'
});

// 17. TECHNOLOGICAL
MERGE (f17:TechnologicalFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_TECHNOLOGICAL',
    key: 'TECHNOLOGICAL',
    label: 'Technological',
    description: 'Tool regimes, production technologies, industrial phases'
});

// 18. COMMUNICATION
MERGE (f18:CommunicationFacet:Facet:CanonicalFacet {
    unique_id: 'FACET_COMMUNICATION',
    key: 'COMMUNICATION',
    label: 'Communication',
    description: 'Information exchange, media, communication technologies'
});

// ============================================================================
// STEP 4: Create IS_COMPOSED_OF relationships (Facets → 18 facet instances)
// ============================================================================

MATCH (cat:Facets:Category {id: 'FACETS_CATEGORY'})
MATCH (f:CanonicalFacet)
MERGE (cat)-[:IS_COMPOSED_OF {
    facet_system: 'canonical_18',
    enforcement: 'ADR_004'
}]->(f);

// ============================================================================
// Verification
// ============================================================================

MATCH path = (c:Chrystallum)-[:HAS_FACET_CLUSTER]->(cat:Facets:Category)-[:IS_COMPOSED_OF]->(f:CanonicalFacet)
RETURN path;

// Table view
MATCH (c:Chrystallum)-[:HAS_FACET_CLUSTER]->(cat:Facets:Category)-[:IS_COMPOSED_OF]->(f:CanonicalFacet)
RETURN 
    c.label as Root,
    cat.label as Category,
    f.key as FacetKey,
    f.label as Facet,
    f.description as Description
ORDER BY f.key;

