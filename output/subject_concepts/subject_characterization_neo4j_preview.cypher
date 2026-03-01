// ============================================================================
// SUBJECT CHARACTERIZATION → NEO4J PREVIEW
// ============================================================================
// Source: subject_characterization_results.json (Q17167 Roman Republic)
// Generated for preview before push. Run in Neo4j Browser to execute.
// ============================================================================
//
// STRUCTURE (what gets created):
//
//   (SubjectConcept {qid:'Q17167', label:'Roman Republic', wikipedia_url, material_type, summary, ...})
//        |
//        |--[:MAPS_TO_FACET {weight:1.0, reason:"..."}]--> (Facet {facet_id:'facet_political'})
//        |--[:MAPS_TO_FACET {weight:0.9, reason:"..."}]--> (Facet {facet_id:'facet_military'})
//        |--[:MAPS_TO_FACET {weight:0.9, reason:"..."}]--> (Facet {facet_id:'facet_social'})
//        |--[:MAPS_TO_FACET {weight:0.9, reason:"..."}]--> (Facet {facet_id:'facet_cultural'})
//        |--[:MAPS_TO_FACET {weight:0.9, reason:"..."}]--> (Facet {facet_id:'facet_geographic'})
//        |--[:MAPS_TO_FACET {weight:0.8, reason:"..."}]--> (Facet {facet_id:'facet_archaeological'})
//        |--[:MAPS_TO_FACET {weight:0.8, reason:"..."}]--> (Facet {facet_id:'facet_biographic'})
//        |--[:MAPS_TO_FACET {weight:0.8, reason:"..."}]--> (Facet {facet_id:'facet_diplomatic'})
//        |--[:MAPS_TO_FACET {weight:0.8, reason:"..."}]--> (Facet {facet_id:'facet_intellectual'})
//        |--[:MAPS_TO_FACET {weight:0.7, reason:"..."}]--> (Facet {facet_id:'facet_artistic'})
//        |--[:MAPS_TO_FACET {weight:0.7, reason:"..."}]--> (Facet {facet_id:'facet_communication'})
//        |--[:MAPS_TO_FACET {weight:0.7, reason:"..."}]--> (Facet {facet_id:'facet_economic'})
//        |--[:MAPS_TO_FACET {weight:0.7, reason:"..."}]--> (Facet {facet_id:'facet_religious'})
//        |--[:MAPS_TO_FACET {weight:0.7, reason:"..."}]--> (Facet {facet_id:'facet_technological'})
//        |--[:MAPS_TO_FACET {weight:0.6, reason:"..."}]--> (Facet {facet_id:'facet_demographic'})
//        |--[:MAPS_TO_FACET {weight:0.6, reason:"..."}]--> (Facet {facet_id:'facet_linguistic'})
//        |--[:MAPS_TO_FACET {weight:0.4, reason:"..."}]--> (Facet {facet_id:'facet_environmental'})
//        +--[:MAPS_TO_FACET {weight:0.3, reason:"..."}]--> (Facet {facet_id:'facet_scientific'})
//
// ============================================================================

// ----------------------------------------------------------------------------
// 1. MERGE SubjectConcept (create or update)
// ----------------------------------------------------------------------------
MERGE (sc:SubjectConcept {qid: 'Q17167'})
ON CREATE SET
  sc.subject_id = 'subj_roman_republic_q17167',
  sc.label = 'Roman Republic',
  sc.created_at = datetime(),
  sc.created_by = 'subject_characterization_agent'
ON MATCH SET
  sc.updated_at = datetime(),
  sc.updated_by = 'subject_characterization_agent'
SET
  sc.wikipedia_url = 'https://en.wikipedia.org/wiki/Roman_Republic',
  sc.material_type = 'secondary',
  sc.material_reason = 'The search results are scholarly syntheses and educational resources (Lumen Learning, Britannica, Wikipedia, academic articles) that interpret and explain the Roman Republic rather than presenting primary source documents or original texts.',
  sc.summary = 'The Roman Republic (509–27 BCE) was a complex political system combining democratic assemblies, aristocratic Senate, and elected magistracies that governed territorial expansion, military conquest, and cultural synthesis across the Mediterranean.',
  sc.lcsh_id = 'sh85115114',
  sc.wikidata_description = 'period of ancient Roman civilization (509 BC–27 BC)',
  sc.primary_facet = 'POLITICAL',
  sc.related_facets = ['MILITARY', 'SOCIAL', 'CULTURAL', 'GEOGRAPHIC', 'ARCHAEOLOGICAL', 'BIOGRAPHIC', 'DIPLOMATIC', 'INTELLECTUAL', 'ARTISTIC', 'COMMUNICATION', 'ECONOMIC', 'RELIGIOUS', 'TECHNOLOGICAL', 'DEMOGRAPHIC', 'LINGUISTIC', 'ENVIRONMENTAL', 'SCIENTIFIC']
RETURN sc;


// ----------------------------------------------------------------------------
// 2. REMOVE existing MAPS_TO_FACET edges (idempotent re-run)
// ----------------------------------------------------------------------------
MATCH (sc:SubjectConcept {qid: 'Q17167'})-[r:MAPS_TO_FACET]->()
DELETE r;


// ----------------------------------------------------------------------------
// 3. CREATE MAPS_TO_FACET edges (one per facet with weight + reason)
// ----------------------------------------------------------------------------
// Facet nodes: schema uses facet_id = 'facet_{lowercase}' (e.g. facet_political)
// We MERGE to create if missing; existing schema may have facet_political, facet_military, etc.

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_archaeological'})
ON CREATE SET f.label = 'Archaeological'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.8,
  reason: 'The Roman Republic generated extensive material culture—sites, excavations, artifacts, inscriptions, coins, pottery, and structural remains that form the primary evidence base for understanding the period.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_artistic'})
ON CREATE SET f.label = 'Artistic'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.7,
  reason: 'The Republic produced significant sculpture, architecture (temples, public buildings), literature (Cicero, Livy), and poetry that defined Roman aesthetic traditions and cultural identity.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_biographic'})
ON CREATE SET f.label = 'Biographic'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.8,
  reason: "The Republic's political system centered on individual magistrates, consuls, and senators; prosopography of elite families (patrician and plebeian) is essential to understanding republican governance and social structure.",
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_communication'})
ON CREATE SET f.label = 'Communication'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.7,
  reason: 'Oratory and rhetoric were central to republican politics; magistrates and senators used persuasion and messaging to influence assemblies and the public; senatorial decrees and legislative proposals required rhetorical skill.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_cultural'})
ON CREATE SET f.label = 'Cultural'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.9,
  reason: 'The Republic was fundamentally a cultural entity blending Latin, Etruscan, Sabine, Oscan, and Greek elements; republican ideology, civic identity, and values (virtus, pietas, dignitas) shaped Roman civilization.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_demographic'})
ON CREATE SET f.label = 'Demographic'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.6,
  reason: 'The Republic conducted censuses (comitia centuriata role); population growth, citizenship expansion (inclusion of peninsular Italians after Social War), and settlement patterns were integral to republican development.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_diplomatic'})
ON CREATE SET f.label = 'Diplomatic'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.8,
  reason: "Foreign policy was the Senate's primary focus; the Republic engaged in treaties, alliances, embassies, and negotiations with neighboring states and conquered territories.",
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_economic'})
ON CREATE SET f.label = 'Economic'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.7,
  reason: 'The Republic managed public treasury, regulated markets (curule aediles), controlled trade routes, and developed systems of taxation and provincial revenue; economic expansion accompanied territorial conquest.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_environmental'})
ON CREATE SET f.label = 'Environmental'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.4,
  reason: 'Agricultural production and natural resources supported the Republic\'s economy and military; environmental factors influenced settlement and expansion, though not a primary focus of republican institutions.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_geographic'})
ON CREATE SET f.label = 'Geographic'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.9,
  reason: "The Republic's defining characteristic was territorial expansion from the Italian peninsula to Mediterranean dominance; provinces, conquered territories, and geographic administration were central to republican governance.",
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_intellectual'})
ON CREATE SET f.label = 'Intellectual'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.8,
  reason: 'The Republic developed sophisticated legal systems (civil law administered by praetors), constitutional principles (checks and balances, separation of powers), historiography (Livy), and political philosophy that influenced later thought.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_linguistic'})
ON CREATE SET f.label = 'Linguistic'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.6,
  reason: 'Latin emerged as the dominant language of the Republic; written laws, senatorial decrees, and inscriptions preserved republican discourse; linguistic standardization accompanied political expansion.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_military'})
ON CREATE SET f.label = 'Military'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.9,
  reason: 'The Republic was fundamentally militaristic; the comitia centuriata (assembly of centuries/soldiers) declared war, magistrates commanded legions, praetors led provincial armies, and military power underpinned republican expansion and survival.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_political'})
ON CREATE SET f.label = 'Political'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 1.0,
  reason: 'The Roman Republic was defined by its political system: the Senate, magistracies (consuls, praetors, censors, quaestors, aediles), assemblies (comitia centuriata, comitia tributa, concilium plebis), checks and balances, and constitutional evolution through precedent.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_religious'})
ON CREATE SET f.label = 'Religious'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.7,
  reason: 'Roman religion permeated republican institutions; priests held political office, religious law was administered, temples served civic functions, and religious ritual legitimized political authority and military campaigns.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_scientific'})
ON CREATE SET f.label = 'Scientific'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.3,
  reason: 'While the Republic did not prioritize scientific advancement, engineering knowledge (aqueducts, roads, military siege equipment) applied mathematical and practical principles; medicine and astronomy had limited institutional roles.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_social'})
ON CREATE SET f.label = 'Social'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.9,
  reason: 'The Republic was structured by social hierarchy: patrician-plebeian conflict, class-based political access, patronage networks, slavery as economic foundation, kinship ties determining political power, and gradual plebeian integration into elite structures.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);

MATCH (sc:SubjectConcept {qid: 'Q17167'})
MERGE (f:Facet {facet_id: 'facet_technological'})
ON CREATE SET f.label = 'Technological'
MERGE (sc)-[:MAPS_TO_FACET {
  weight: 0.7,
  reason: 'The Republic developed infrastructure (Via Appia, aqueducts), military engineering (siege equipment, fortifications), construction techniques, and concrete technology that supported territorial administration and military campaigns.',
  source: 'subject_characterization_agent',
  created_at: datetime()
}]->(f);


// ----------------------------------------------------------------------------
// 4. VERIFY: Query what was created (uncomment to run)
// ----------------------------------------------------------------------------
// MATCH (sc:SubjectConcept {qid: 'Q17167'})-[r:MAPS_TO_FACET]->(f:Facet)
// RETURN sc.label, f.facet_id, r.weight, substring(r.reason, 0, 80) + '...' AS reason_preview
// ORDER BY r.weight DESC;
