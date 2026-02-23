// Neo4j Import - SCA Entities with Ciphers
// Generated: 2026-02-21T07:31:10.618973
// Total entities: 300

// ============ INDEXES ============

// Tier 1: Entity cipher indexes
CREATE INDEX entity_cipher_idx IF NOT EXISTS FOR (n:Entity) ON (n.entity_cipher);
CREATE INDEX entity_qid_idx IF NOT EXISTS FOR (n:Entity) ON (n.qid);
CREATE INDEX entity_type_idx IF NOT EXISTS FOR (n:Entity) ON (n.entity_type, n.entity_cipher);

// Tier 2: Faceted cipher indexes
CREATE INDEX faceted_cipher_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.faceted_cipher);
CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.entity_cipher, n.facet_id);

// ============ ENTITIES ============


// Entity 1: Q17167 (Roman Republic)
CREATE (:Entity {
  entity_id: 'subjectconcept_q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  label: 'Roman Republic',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 61,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 2: Q11514315 (historical period)
CREATE (:Entity {
  entity_id: 'concept_q11514315',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  label: 'historical period',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 20,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 3: Q1307214 (form of government)
CREATE (:Entity {
  entity_id: 'concept_q1307214',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  label: 'form of government',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 30,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 4: Q48349 (empire)
CREATE (:Entity {
  entity_id: 'concept_q48349',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  label: 'empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 55,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 5: Q3024240 (historical country)
CREATE (:Entity {
  entity_id: 'concept_q3024240',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  label: 'historical country',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 16,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 6: Q6944405 (Category:Roman Republic)
CREATE (:Entity {
  entity_id: 'concept_q6944405',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  label: 'Category:Roman Republic',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 7: Q337547 (ancient Roman religion)
CREATE (:Entity {
  entity_id: 'concept_q337547',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  label: 'ancient Roman religion',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 31,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 8: Q130614 (Roman Senate)
CREATE (:Entity {
  entity_id: 'concept_q130614',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  label: 'Roman Senate',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 27,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 9: Q1114821 (citizens\' assemblies of the Roman Republic)
CREATE (:Entity {
  entity_id: 'organization_q1114821',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  label: 'citizens\' assemblies of the Roman Republic',
  entity_type: 'ORGANIZATION',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 10,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 10: Q952064 (Roman currency)
CREATE (:Entity {
  entity_id: 'concept_q952064',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  label: 'Roman currency',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 26,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 11: Q486761 (classical antiquity)
CREATE (:Entity {
  entity_id: 'subjectconcept_q486761',
  entity_cipher: 'ent_sub_Q486761',
  qid: 'Q486761',
  label: 'classical antiquity',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 68,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 12: Q13285410 (Category:People from the Roman Republic)
CREATE (:Entity {
  entity_id: 'concept_q13285410',
  entity_cipher: 'ent_con_Q13285410',
  qid: 'Q13285410',
  label: 'Category:People from the Roman Republic',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 13: Q2839628 (Early Roman Republic)
CREATE (:Entity {
  entity_id: 'subjectconcept_q2839628',
  entity_cipher: 'ent_sub_Q2839628',
  qid: 'Q2839628',
  label: 'Early Roman Republic',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 14: Q6106068 (Middle Roman Republic)
CREATE (:Entity {
  entity_id: 'subjectconcept_q6106068',
  entity_cipher: 'ent_sub_Q6106068',
  qid: 'Q6106068',
  label: 'Middle Roman Republic',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 15: Q2815472 (Late Roman Republic)
CREATE (:Entity {
  entity_id: 'subjectconcept_q2815472',
  entity_cipher: 'ent_sub_Q2815472',
  qid: 'Q2815472',
  label: 'Late Roman Republic',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 10,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 16: Q2277 (Roman Empire)
CREATE (:Entity {
  entity_id: 'subjectconcept_q2277',
  entity_cipher: 'ent_sub_Q2277',
  qid: 'Q2277',
  label: 'Roman Empire',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 102,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 17: Q206414 (Principate)
CREATE (:Entity {
  entity_id: 'subjectconcept_q206414',
  entity_cipher: 'ent_sub_Q206414',
  qid: 'Q206414',
  label: 'Principate',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 24,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 18: Q201038 (Roman Kingdom)
CREATE (:Entity {
  entity_id: 'subjectconcept_q201038',
  entity_cipher: 'ent_sub_Q201038',
  qid: 'Q201038',
  label: 'Roman Kingdom',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 38,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 19: Q220 (Rome)
CREATE (:Entity {
  entity_id: 'place_q220',
  entity_cipher: 'ent_plc_Q220',
  qid: 'Q220',
  label: 'Rome',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 5,
  properties_count: 262,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 20: Q397 (Latin)
CREATE (:Entity {
  entity_id: 'concept_q397',
  entity_cipher: 'ent_con_Q397',
  qid: 'Q397',
  label: 'Latin',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 132,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 21: Q35497 (Ancient Greek)
CREATE (:Entity {
  entity_id: 'concept_q35497',
  entity_cipher: 'ent_con_Q35497',
  qid: 'Q35497',
  label: 'Ancient Greek',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 70,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 22: Q46 (Europe)
CREATE (:Entity {
  entity_id: 'concept_q46',
  entity_cipher: 'ent_con_Q46',
  qid: 'Q46',
  label: 'Europe',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 228,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 23: Q48 (Asia)
CREATE (:Entity {
  entity_id: 'concept_q48',
  entity_cipher: 'ent_con_Q48',
  qid: 'Q48',
  label: 'Asia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 5,
  properties_count: 213,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 24: Q15 (Africa)
CREATE (:Entity {
  entity_id: 'concept_q15',
  entity_cipher: 'ent_con_Q15',
  qid: 'Q15',
  label: 'Africa',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 254,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 25: Q666680 (aristocratic republic)
CREATE (:Entity {
  entity_id: 'concept_q666680',
  entity_cipher: 'ent_con_Q666680',
  qid: 'Q666680',
  label: 'aristocratic republic',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 26: Q1747689 (Ancient Rome)
CREATE (:Entity {
  entity_id: 'concept_q1747689',
  entity_cipher: 'ent_con_Q1747689',
  qid: 'Q1747689',
  label: 'Ancient Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 114,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 27: Q346629 (Roman Republic)
CREATE (:Entity {
  entity_id: 'concept_q346629',
  entity_cipher: 'ent_con_Q346629',
  qid: 'Q346629',
  label: 'Roman Republic',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 28: Q6173448 (Wikipedia:Vital articles/Level/4)
CREATE (:Entity {
  entity_id: 'concept_q6173448',
  entity_cipher: 'ent_con_Q6173448',
  qid: 'Q6173448',
  label: 'Wikipedia:Vital articles/Level/4',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 7,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 29: Q124988 (Punic Wars)
CREATE (:Entity {
  entity_id: 'event_q124988',
  entity_cipher: 'ent_evt_Q124988',
  qid: 'Q124988',
  label: 'Punic Wars',
  entity_type: 'EVENT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 44,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 30: Q3778726 (Sertorian War)
CREATE (:Entity {
  entity_id: 'event_q3778726',
  entity_cipher: 'ent_evt_Q3778726',
  qid: 'Q3778726',
  label: 'Sertorian War',
  entity_type: 'EVENT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 12,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 31: Q75813 (Macedonian Wars)
CREATE (:Entity {
  entity_id: 'event_q75813',
  entity_cipher: 'ent_evt_Q75813',
  qid: 'Q75813',
  label: 'Macedonian Wars',
  entity_type: 'EVENT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 16,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 32: Q202161 (Gallic War)
CREATE (:Entity {
  entity_id: 'event_q202161',
  entity_cipher: 'ent_evt_Q202161',
  qid: 'Q202161',
  label: 'Gallic War',
  entity_type: 'EVENT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 36,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 33: Q596373 (Pyrrhic War)
CREATE (:Entity {
  entity_id: 'event_q596373',
  entity_cipher: 'ent_evt_Q596373',
  qid: 'Q596373',
  label: 'Pyrrhic War',
  entity_type: 'EVENT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 34: Q1238338 (Caesar\'s Civil War)
CREATE (:Entity {
  entity_id: 'event_q1238338',
  entity_cipher: 'ent_evt_Q1238338',
  qid: 'Q1238338',
  label: 'Caesar\'s Civil War',
  entity_type: 'EVENT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 35: Q677316 (Social War of 91-87 BCE)
CREATE (:Entity {
  entity_id: 'event_q677316',
  entity_cipher: 'ent_evt_Q677316',
  qid: 'Q677316',
  label: 'Social War of 91-87 BCE',
  entity_type: 'EVENT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 31,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 36: Q6428674 (era)
CREATE (:Entity {
  entity_id: 'concept_q6428674',
  entity_cipher: 'ent_con_Q6428674',
  qid: 'Q6428674',
  label: 'era',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 26,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 37: Q17004260 (list of time periods)
CREATE (:Entity {
  entity_id: 'concept_q17004260',
  entity_cipher: 'ent_con_Q17004260',
  qid: 'Q17004260',
  label: 'list of time periods',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 38: Q816829 (periodization)
CREATE (:Entity {
  entity_id: 'concept_q816829',
  entity_cipher: 'ent_con_Q816829',
  qid: 'Q816829',
  label: 'periodization',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 30,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 39: Q183039 (form of state)
CREATE (:Entity {
  entity_id: 'concept_q183039',
  entity_cipher: 'ent_con_Q183039',
  qid: 'Q183039',
  label: 'form of state',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 12,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 40: Q2752458 (administrative type)
CREATE (:Entity {
  entity_id: 'concept_q2752458',
  entity_cipher: 'ent_con_Q2752458',
  qid: 'Q2752458',
  label: 'administrative type',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 5,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 41: Q28108 (political system)
CREATE (:Entity {
  entity_id: 'concept_q28108',
  entity_cipher: 'ent_con_Q28108',
  qid: 'Q28108',
  label: 'political system',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 39,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 42: Q54069 (Category:Forms of government)
CREATE (:Entity {
  entity_id: 'concept_q54069',
  entity_cipher: 'ent_con_Q54069',
  qid: 'Q54069',
  label: 'Category:Forms of government',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 43: Q5589178 (regime)
CREATE (:Entity {
  entity_id: 'concept_q5589178',
  entity_cipher: 'ent_con_Q5589178',
  qid: 'Q5589178',
  label: 'regime',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 12,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 44: Q19944802 (government structure)
CREATE (:Entity {
  entity_id: 'concept_q19944802',
  entity_cipher: 'ent_con_Q19944802',
  qid: 'Q19944802',
  label: 'government structure',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 45: Q20076236 (state system)
CREATE (:Entity {
  entity_id: 'concept_q20076236',
  entity_cipher: 'ent_con_Q20076236',
  qid: 'Q20076236',
  label: 'state system',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 46: Q759524 (organizational structure)
CREATE (:Entity {
  entity_id: 'concept_q759524',
  entity_cipher: 'ent_con_Q759524',
  qid: 'Q759524',
  label: 'organizational structure',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 24,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 47: Q31728 (public administration)
CREATE (:Entity {
  entity_id: 'concept_q31728',
  entity_cipher: 'ent_con_Q31728',
  qid: 'Q31728',
  label: 'public administration',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 60,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 48: Q6526407 (Template:Basic forms of government)
CREATE (:Entity {
  entity_id: 'concept_q6526407',
  entity_cipher: 'ent_con_Q6526407',
  qid: 'Q6526407',
  label: 'Template:Basic forms of government',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 49: Q25728256 (Template:Forms of government footer)
CREATE (:Entity {
  entity_id: 'concept_q25728256',
  entity_cipher: 'ent_con_Q25728256',
  qid: 'Q25728256',
  label: 'Template:Forms of government footer',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 50: Q6135095 (Category:Empires)
CREATE (:Entity {
  entity_id: 'concept_q6135095',
  entity_cipher: 'ent_con_Q6135095',
  qid: 'Q6135095',
  label: 'Category:Empires',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 5,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 51: Q2041543 (Otto\'s encyclopedia)
CREATE (:Entity {
  entity_id: 'concept_q2041543',
  entity_cipher: 'ent_con_Q2041543',
  qid: 'Q2041543',
  label: 'Otto\'s encyclopedia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 52: Q20078554 (Great Soviet Encyclopedia (1926–1947))
CREATE (:Entity {
  entity_id: 'concept_q20078554',
  entity_cipher: 'ent_con_Q20078554',
  qid: 'Q20078554',
  label: 'Great Soviet Encyclopedia (1926–1947)',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 15,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 53: Q20096917 (Encyclopædia Britannica Ninth Edition)
CREATE (:Entity {
  entity_id: 'concept_q20096917',
  entity_cipher: 'ent_con_Q20096917',
  qid: 'Q20096917',
  label: 'Encyclopædia Britannica Ninth Edition',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 10,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 54: Q602358 (Brockhaus and Efron Encyclopedic Dictionary)
CREATE (:Entity {
  entity_id: 'concept_q602358',
  entity_cipher: 'ent_con_Q602358',
  qid: 'Q602358',
  label: 'Brockhaus and Efron Encyclopedic Dictionary',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 27,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 55: Q19180675 (Small Brockhaus and Efron Encyclopedic Dictionary)
CREATE (:Entity {
  entity_id: 'concept_q19180675',
  entity_cipher: 'ent_con_Q19180675',
  qid: 'Q19180675',
  label: 'Small Brockhaus and Efron Encyclopedic Dictionary',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 11,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 56: Q4532138 (Granat Encyclopedic Dictionary)
CREATE (:Entity {
  entity_id: 'concept_q4532138',
  entity_cipher: 'ent_con_Q4532138',
  qid: 'Q4532138',
  label: 'Granat Encyclopedic Dictionary',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 18,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 57: Q356252 (Imperia)
CREATE (:Entity {
  entity_id: 'concept_q356252',
  entity_cipher: 'ent_con_Q356252',
  qid: 'Q356252',
  label: 'Imperia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 1,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 58: Q3624078 (sovereign state)
CREATE (:Entity {
  entity_id: 'concept_q3624078',
  entity_cipher: 'ent_con_Q3624078',
  qid: 'Q3624078',
  label: 'sovereign state',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 24,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 59: Q7269 (monarchy)
CREATE (:Entity {
  entity_id: 'concept_q7269',
  entity_cipher: 'ent_con_Q7269',
  qid: 'Q7269',
  label: 'monarchy',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 76,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 60: Q96196009 (former or current state)
CREATE (:Entity {
  entity_id: 'concept_q96196009',
  entity_cipher: 'ent_con_Q96196009',
  qid: 'Q96196009',
  label: 'former or current state',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 61: Q19832712 (historical administrative division)
CREATE (:Entity {
  entity_id: 'concept_q19832712',
  entity_cipher: 'ent_con_Q19832712',
  qid: 'Q19832712',
  label: 'historical administrative division',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 62: Q6256 (country)
CREATE (:Entity {
  entity_id: 'concept_q6256',
  entity_cipher: 'ent_con_Q6256',
  qid: 'Q6256',
  label: 'country',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 68,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 63: Q7238252 (Category:Former countries)
CREATE (:Entity {
  entity_id: 'concept_q7238252',
  entity_cipher: 'ent_con_Q7238252',
  qid: 'Q7238252',
  label: 'Category:Former countries',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 64: Q6036853 (Template:Infobox former country)
CREATE (:Entity {
  entity_id: 'concept_q6036853',
  entity_cipher: 'ent_con_Q6036853',
  qid: 'Q6036853',
  label: 'Template:Infobox former country',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 65: Q3591867 (proposed country)
CREATE (:Entity {
  entity_id: 'concept_q3591867',
  entity_cipher: 'ent_con_Q3591867',
  qid: 'Q3591867',
  label: 'proposed country',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 66: Q62630 (list of former sovereign states)
CREATE (:Entity {
  entity_id: 'concept_q62630',
  entity_cipher: 'ent_con_Q62630',
  qid: 'Q62630',
  label: 'list of former sovereign states',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 67: Q4167836 (Wikimedia category)
CREATE (:Entity {
  entity_id: 'concept_q4167836',
  entity_cipher: 'ent_con_Q4167836',
  qid: 'Q4167836',
  label: 'Wikimedia category',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 12,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 68: Q5 (human)
CREATE (:Entity {
  entity_id: 'concept_q5',
  entity_cipher: 'ent_con_Q5',
  qid: 'Q5',
  label: 'human',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 111,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 69: Q8678306 (Category:Roman Kingdom)
CREATE (:Entity {
  entity_id: 'concept_q8678306',
  entity_cipher: 'ent_con_Q8678306',
  qid: 'Q8678306',
  label: 'Category:Roman Kingdom',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 70: Q8251375 (Category:Ancient Roman religion)
CREATE (:Entity {
  entity_id: 'concept_q8251375',
  entity_cipher: 'ent_con_Q8251375',
  qid: 'Q8251375',
  label: 'Category:Ancient Roman religion',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 71: Q30059240 (Russian translation of Lübker\'s Antiquity Lexicon)
CREATE (:Entity {
  entity_id: 'concept_q30059240',
  entity_cipher: 'ent_con_Q30059240',
  qid: 'Q30059240',
  label: 'Russian translation of Lübker\'s Antiquity Lexicon',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 15,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 72: Q107013262 (religious policies of the Roman Empire)
CREATE (:Entity {
  entity_id: 'concept_q107013262',
  entity_cipher: 'ent_con_Q107013262',
  qid: 'Q107013262',
  label: 'religious policies of the Roman Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 73: Q107013169 (religion in ancient Rome)
CREATE (:Entity {
  entity_id: 'concept_q107013169',
  entity_cipher: 'ent_con_Q107013169',
  qid: 'Q107013169',
  label: 'religion in ancient Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 74: Q5626901 (Template:Roman religion)
CREATE (:Entity {
  entity_id: 'concept_q5626901',
  entity_cipher: 'ent_con_Q5626901',
  qid: 'Q5626901',
  label: 'Template:Roman religion',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 75: Q11204 (legislature)
CREATE (:Entity {
  entity_id: 'concept_q11204',
  entity_cipher: 'ent_con_Q11204',
  qid: 'Q11204',
  label: 'legislature',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 47,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 76: Q1144514 (Curia Julia)
CREATE (:Entity {
  entity_id: 'concept_q1144514',
  entity_cipher: 'ent_con_Q1144514',
  qid: 'Q1144514',
  label: 'Curia Julia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 77: Q32899669 (Category:Roman Senate)
CREATE (:Entity {
  entity_id: 'concept_q32899669',
  entity_cipher: 'ent_con_Q32899669',
  qid: 'Q32899669',
  label: 'Category:Roman Senate',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 78: Q1225322 (ordo senatorius)
CREATE (:Entity {
  entity_id: 'concept_q1225322',
  entity_cipher: 'ent_con_Q1225322',
  qid: 'Q1225322',
  label: 'ordo senatorius',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 79: Q2915100 (political institutions of ancient Rome)
CREATE (:Entity {
  entity_id: 'concept_q2915100',
  entity_cipher: 'ent_con_Q2915100',
  qid: 'Q2915100',
  label: 'political institutions of ancient Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 80: Q17197366 (type of organization)
CREATE (:Entity {
  entity_id: 'concept_q17197366',
  entity_cipher: 'ent_con_Q17197366',
  qid: 'Q17197366',
  label: 'type of organization',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 81: Q3181656 (The Nuttall Encyclopædia)
CREATE (:Entity {
  entity_id: 'concept_q3181656',
  entity_cipher: 'ent_con_Q3181656',
  qid: 'Q3181656',
  label: 'The Nuttall Encyclopædia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 12,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 82: Q1138524 (Pauly–Wissowa)
CREATE (:Entity {
  entity_id: 'concept_q1138524',
  entity_cipher: 'ent_con_Q1138524',
  qid: 'Q1138524',
  label: 'Pauly–Wissowa',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 28,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 83: Q867541 (Encyclopædia Britannica 11th edition)
CREATE (:Entity {
  entity_id: 'concept_q867541',
  entity_cipher: 'ent_con_Q867541',
  qid: 'Q867541',
  label: 'Encyclopædia Britannica 11th edition',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 44,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 84: Q8386687 (Category:Coins of ancient Rome)
CREATE (:Entity {
  entity_id: 'concept_q8386687',
  entity_cipher: 'ent_con_Q8386687',
  qid: 'Q8386687',
  label: 'Category:Coins of ancient Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 85: Q17524420 (aspect of history)
CREATE (:Entity {
  entity_id: 'concept_q17524420',
  entity_cipher: 'ent_con_Q17524420',
  qid: 'Q17524420',
  label: 'aspect of history',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 86: Q19219752 (Meyers Konversations-Lexikon, 4th edition (1885–1890))
CREATE (:Entity {
  entity_id: 'concept_q19219752',
  entity_cipher: 'ent_con_Q19219752',
  qid: 'Q19219752',
  label: 'Meyers Konversations-Lexikon, 4th edition (1885–1890)',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 87: Q662137 (Roman Republican currency)
CREATE (:Entity {
  entity_id: 'concept_q662137',
  entity_cipher: 'ent_con_Q662137',
  qid: 'Q662137',
  label: 'Roman Republican currency',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 7,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 88: Q638048 (Roman Imperial coinage)
CREATE (:Entity {
  entity_id: 'concept_q638048',
  entity_cipher: 'ent_con_Q638048',
  qid: 'Q638048',
  label: 'Roman Imperial coinage',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 7,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 89: Q8142 (currency)
CREATE (:Entity {
  entity_id: 'concept_q8142',
  entity_cipher: 'ent_con_Q8142',
  qid: 'Q8142',
  label: 'currency',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 75,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 90: Q28783456 (obsolete currency)
CREATE (:Entity {
  entity_id: 'concept_q28783456',
  entity_cipher: 'ent_con_Q28783456',
  qid: 'Q28783456',
  label: 'obsolete currency',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 91: Q3879434 (Roman numismatics)
CREATE (:Entity {
  entity_id: 'concept_q3879434',
  entity_cipher: 'ent_con_Q3879434',
  qid: 'Q3879434',
  label: 'Roman numismatics',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 92: Q14618893 (Classical Roman Empire)
CREATE (:Entity {
  entity_id: 'subjectconcept_q14618893',
  entity_cipher: 'ent_sub_Q14618893',
  qid: 'Q14618893',
  label: 'Classical Roman Empire',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 9,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 93: Q11772 (Ancient Greece)
CREATE (:Entity {
  entity_id: 'concept_q11772',
  entity_cipher: 'ent_con_Q11772',
  qid: 'Q11772',
  label: 'Ancient Greece',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 71,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 94: Q181264 (Mycenaean Greece)
CREATE (:Entity {
  entity_id: 'concept_q181264',
  entity_cipher: 'ent_con_Q181264',
  qid: 'Q181264',
  label: 'Mycenaean Greece',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 49,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 95: Q134178 (Minoan civilization)
CREATE (:Entity {
  entity_id: 'concept_q134178',
  entity_cipher: 'ent_con_Q134178',
  qid: 'Q134178',
  label: 'Minoan civilization',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 56,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 96: Q17161 (Etruscans)
CREATE (:Entity {
  entity_id: 'concept_q17161',
  entity_cipher: 'ent_con_Q17161',
  qid: 'Q17161',
  label: 'Etruscans',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 64,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 97: Q245813 (Bronze age Cyprus)
CREATE (:Entity {
  entity_id: 'concept_q245813',
  entity_cipher: 'ent_con_Q245813',
  qid: 'Q245813',
  label: 'Bronze age Cyprus',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 98: Q12544 (Byzantine Empire)
CREATE (:Entity {
  entity_id: 'concept_q12544',
  entity_cipher: 'ent_con_Q12544',
  qid: 'Q12544',
  label: 'Byzantine Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 5,
  properties_count: 144,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 99: Q3617880 (Italic peoples)
CREATE (:Entity {
  entity_id: 'concept_q3617880',
  entity_cipher: 'ent_con_Q3617880',
  qid: 'Q3617880',
  label: 'Italic peoples',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 16,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 100: Q1778719 (Lydians)
CREATE (:Entity {
  entity_id: 'concept_q1778719',
  entity_cipher: 'ent_con_Q1778719',
  qid: 'Q1778719',
  label: 'Lydians',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 101: Q83958 (Macedonia)
CREATE (:Entity {
  entity_id: 'concept_q83958',
  entity_cipher: 'ent_con_Q83958',
  qid: 'Q83958',
  label: 'Macedonia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 52,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 102: Q131802 (Scythians)
CREATE (:Entity {
  entity_id: 'concept_q131802',
  entity_cipher: 'ent_con_Q131802',
  qid: 'Q131802',
  label: 'Scythians',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 48,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 103: Q6111354 (Classical Rome)
CREATE (:Entity {
  entity_id: 'concept_q6111354',
  entity_cipher: 'ent_con_Q6111354',
  qid: 'Q6111354',
  label: 'Classical Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 104: Q8381710 (Category:Classical antiquity)
CREATE (:Entity {
  entity_id: 'concept_q8381710',
  entity_cipher: 'ent_con_Q8381710',
  qid: 'Q8381710',
  label: 'Category:Classical antiquity',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 105: Q217050 (late antiquity)
CREATE (:Entity {
  entity_id: 'concept_q217050',
  entity_cipher: 'ent_con_Q217050',
  qid: 'Q217050',
  label: 'late antiquity',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 38,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 106: Q937284 (Greco-Roman world)
CREATE (:Entity {
  entity_id: 'concept_q937284',
  entity_cipher: 'ent_con_Q937284',
  qid: 'Q937284',
  label: 'Greco-Roman world',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 15,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 107: Q1292119 (style)
CREATE (:Entity {
  entity_id: 'concept_q1292119',
  entity_cipher: 'ent_con_Q1292119',
  qid: 'Q1292119',
  label: 'style',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 21,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 108: Q41493 (ancient history)
CREATE (:Entity {
  entity_id: 'concept_q41493',
  entity_cipher: 'ent_con_Q41493',
  qid: 'Q41493',
  label: 'ancient history',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 77,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 109: Q98270938 (Early antiquity)
CREATE (:Entity {
  entity_id: 'concept_q98270938',
  entity_cipher: 'ent_con_Q98270938',
  qid: 'Q98270938',
  label: 'Early antiquity',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 110: Q112939719 (Classical Greek and Roman history)
CREATE (:Entity {
  entity_id: 'concept_q112939719',
  entity_cipher: 'ent_con_Q112939719',
  qid: 'Q112939719',
  label: 'Classical Greek and Roman history',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 9,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 111: Q495527 (classical philology)
CREATE (:Entity {
  entity_id: 'concept_q495527',
  entity_cipher: 'ent_con_Q495527',
  qid: 'Q495527',
  label: 'classical philology',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 37,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 112: Q3351707 (Pax Leksikon)
CREATE (:Entity {
  entity_id: 'concept_q3351707',
  entity_cipher: 'ent_con_Q3351707',
  qid: 'Q3351707',
  label: 'Pax Leksikon',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 113: Q19660746 (person related to this place)
CREATE (:Entity {
  entity_id: 'concept_q19660746',
  entity_cipher: 'ent_con_Q19660746',
  qid: 'Q19660746',
  label: 'person related to this place',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 114: Q16931679 (Overthrow of the Roman monarchy)
CREATE (:Entity {
  entity_id: 'concept_q16931679',
  entity_cipher: 'ent_con_Q16931679',
  qid: 'Q16931679',
  label: 'Overthrow of the Roman monarchy',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 9,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 115: Q119137625 (Second Roman Kingdom)
CREATE (:Entity {
  entity_id: 'subjectconcept_q119137625',
  entity_cipher: 'ent_sub_Q119137625',
  qid: 'Q119137625',
  label: 'Second Roman Kingdom',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 9,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 116: Q16869 (Constantinople)
CREATE (:Entity {
  entity_id: 'place_q16869',
  entity_cipher: 'ent_plc_Q16869',
  qid: 'Q16869',
  label: 'Constantinople',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 78,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 117: Q13364 (Ravenna)
CREATE (:Entity {
  entity_id: 'place_q13364',
  entity_cipher: 'ent_plc_Q13364',
  qid: 'Q13364',
  label: 'Ravenna',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 5,
  properties_count: 138,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 118: Q18287233 (Roma)
CREATE (:Entity {
  entity_id: 'place_q18287233',
  entity_cipher: 'ent_plc_Q18287233',
  qid: 'Q18287233',
  label: 'Roma',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 36,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 119: Q173424 (autocracy)
CREATE (:Entity {
  entity_id: 'concept_q173424',
  entity_cipher: 'ent_con_Q173424',
  qid: 'Q173424',
  label: 'autocracy',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 36,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 120: Q174450 (Roman Tetrarchy)
CREATE (:Entity {
  entity_id: 'subjectconcept_q174450',
  entity_cipher: 'ent_sub_Q174450',
  qid: 'Q174450',
  label: 'Roman Tetrarchy',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 23,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 121: Q208041 (sestertius)
CREATE (:Entity {
  entity_id: 'concept_q208041',
  entity_cipher: 'ent_con_Q208041',
  qid: 'Q208041',
  label: 'sestertius',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 36,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 122: Q187776 (denarius)
CREATE (:Entity {
  entity_id: 'concept_q187776',
  entity_cipher: 'ent_con_Q187776',
  qid: 'Q187776',
  label: 'denarius',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 39,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 123: Q476078 (aureus)
CREATE (:Entity {
  entity_id: 'concept_q476078',
  entity_cipher: 'ent_con_Q476078',
  qid: 'Q476078',
  label: 'aureus',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 28,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 124: Q376895 (as)
CREATE (:Entity {
  entity_id: 'concept_q376895',
  entity_cipher: 'ent_con_Q376895',
  qid: 'Q376895',
  label: 'as',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 29,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 125: Q7603670 (state church of the Roman Empire)
CREATE (:Entity {
  entity_id: 'concept_q7603670',
  entity_cipher: 'ent_con_Q7603670',
  qid: 'Q7603670',
  label: 'state church of the Roman Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 126: Q2671119 (history of the Roman Empire)
CREATE (:Entity {
  entity_id: 'concept_q2671119',
  entity_cipher: 'ent_con_Q2671119',
  qid: 'Q2671119',
  label: 'history of the Roman Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 13,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 127: Q842606 (Roman emperor)
CREATE (:Entity {
  entity_id: 'concept_q842606',
  entity_cipher: 'ent_con_Q842606',
  qid: 'Q842606',
  label: 'Roman emperor',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 30,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 128: Q21201536 (Q21201536)
CREATE (:Entity {
  entity_id: 'concept_q21201536',
  entity_cipher: 'ent_con_Q21201536',
  qid: 'Q21201536',
  label: 'Q21201536',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 129: Q7209 (Han dynasty)
CREATE (:Entity {
  entity_id: 'subjectconcept_q7209',
  entity_cipher: 'ent_sub_Q7209',
  qid: 'Q7209',
  label: 'Han dynasty',
  entity_type: 'SUBJECTCONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 55,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 130: Q62646 (Germania)
CREATE (:Entity {
  entity_id: 'concept_q62646',
  entity_cipher: 'ent_con_Q62646',
  qid: 'Q62646',
  label: 'Germania',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 25,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 131: Q302980 (Hibernia)
CREATE (:Entity {
  entity_id: 'concept_q302980',
  entity_cipher: 'ent_con_Q302980',
  qid: 'Q302980',
  label: 'Hibernia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 11,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 132: Q32642796 (Q32642796)
CREATE (:Entity {
  entity_id: 'concept_q32642796',
  entity_cipher: 'ent_con_Q32642796',
  qid: 'Q32642796',
  label: 'Q32642796',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 133: Q42859641 (Q42859641)
CREATE (:Entity {
  entity_id: 'concept_q42859641',
  entity_cipher: 'ent_con_Q42859641',
  qid: 'Q42859641',
  label: 'Q42859641',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 134: Q5460604 (Wikipedia:List of articles all languages should have)
CREATE (:Entity {
  entity_id: 'concept_q5460604',
  entity_cipher: 'ent_con_Q5460604',
  qid: 'Q5460604',
  label: 'Wikipedia:List of articles all languages should have',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 135: Q1986139 (Parthian Empire)
CREATE (:Entity {
  entity_id: 'concept_q1986139',
  entity_cipher: 'ent_con_Q1986139',
  qid: 'Q1986139',
  label: 'Parthian Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 50,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 136: Q3626028 (Dacia Mediterranea)
CREATE (:Entity {
  entity_id: 'concept_q3626028',
  entity_cipher: 'ent_con_Q3626028',
  qid: 'Q3626028',
  label: 'Dacia Mediterranea',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 137: Q747040 (Hispania Ulterior)
CREATE (:Entity {
  entity_id: 'concept_q747040',
  entity_cipher: 'ent_con_Q747040',
  qid: 'Q747040',
  label: 'Hispania Ulterior',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 20,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 138: Q1126678 (Hispania Citerior)
CREATE (:Entity {
  entity_id: 'concept_q1126678',
  entity_cipher: 'ent_con_Q1126678',
  qid: 'Q1126678',
  label: 'Hispania Citerior',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 24,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 139: Q170062 (Pannonia)
CREATE (:Entity {
  entity_id: 'concept_q170062',
  entity_cipher: 'ent_con_Q170062',
  qid: 'Q170062',
  label: 'Pannonia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 47,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 140: Q765845 (Mesopotamia)
CREATE (:Entity {
  entity_id: 'concept_q765845',
  entity_cipher: 'ent_con_Q765845',
  qid: 'Q765845',
  label: 'Mesopotamia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 141: Q202311 (Roman Egypt)
CREATE (:Entity {
  entity_id: 'concept_q202311',
  entity_cipher: 'ent_con_Q202311',
  qid: 'Q202311',
  label: 'Roman Egypt',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 30,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 142: Q623322 (Alpes Cottiae)
CREATE (:Entity {
  entity_id: 'concept_q623322',
  entity_cipher: 'ent_con_Q623322',
  qid: 'Q623322',
  label: 'Alpes Cottiae',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 14,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 143: Q360922 (Alpes Graiae)
CREATE (:Entity {
  entity_id: 'concept_q360922',
  entity_cipher: 'ent_con_Q360922',
  qid: 'Q360922',
  label: 'Alpes Graiae',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 7,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 144: Q309270 (Alpes Maritimae)
CREATE (:Entity {
  entity_id: 'concept_q309270',
  entity_cipher: 'ent_con_Q309270',
  qid: 'Q309270',
  label: 'Alpes Maritimae',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 18,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 145: Q221353 (Arabia Petraea)
CREATE (:Entity {
  entity_id: 'concept_q221353',
  entity_cipher: 'ent_con_Q221353',
  qid: 'Q221353',
  label: 'Arabia Petraea',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 27,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 146: Q1254480 (Roman Armenia)
CREATE (:Entity {
  entity_id: 'concept_q1254480',
  entity_cipher: 'ent_con_Q1254480',
  qid: 'Q1254480',
  label: 'Roman Armenia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 147: Q685537 (Britannia Inferior)
CREATE (:Entity {
  entity_id: 'concept_q685537',
  entity_cipher: 'ent_con_Q685537',
  qid: 'Q685537',
  label: 'Britannia Inferior',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 11,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 148: Q918059 (Britannia Superior)
CREATE (:Entity {
  entity_id: 'concept_q918059',
  entity_cipher: 'ent_con_Q918059',
  qid: 'Q918059',
  label: 'Britannia Superior',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 10,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 149: Q33490 (Cappadocia)
CREATE (:Entity {
  entity_id: 'concept_q33490',
  entity_cipher: 'ent_con_Q33490',
  qid: 'Q33490',
  label: 'Cappadocia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 150: Q4819648 (Cilicia)
CREATE (:Entity {
  entity_id: 'concept_q4819648',
  entity_cipher: 'ent_con_Q4819648',
  qid: 'Q4819648',
  label: 'Cilicia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 151: Q971609 (Dacia)
CREATE (:Entity {
  entity_id: 'concept_q971609',
  entity_cipher: 'ent_con_Q971609',
  qid: 'Q971609',
  label: 'Dacia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 32,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 152: Q12277185 (Dacia Superior)
CREATE (:Entity {
  entity_id: 'concept_q12277185',
  entity_cipher: 'ent_con_Q12277185',
  qid: 'Q12277185',
  label: 'Dacia Superior',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 153: Q12270914 (Tres Daciae)
CREATE (:Entity {
  entity_id: 'concept_q12270914',
  entity_cipher: 'ent_con_Q12270914',
  qid: 'Q12270914',
  label: 'Tres Daciae',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 154: Q1820754 (Epirus)
CREATE (:Entity {
  entity_id: 'concept_q1820754',
  entity_cipher: 'ent_con_Q1820754',
  qid: 'Q1820754',
  label: 'Epirus',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 155: Q1249412 (Galatia)
CREATE (:Entity {
  entity_id: 'concept_q1249412',
  entity_cipher: 'ent_con_Q1249412',
  qid: 'Q1249412',
  label: 'Galatia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 156: Q715376 (Gallia Aquitania)
CREATE (:Entity {
  entity_id: 'concept_q715376',
  entity_cipher: 'ent_con_Q715376',
  qid: 'Q715376',
  label: 'Gallia Aquitania',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 157: Q206443 (Gallia Belgica)
CREATE (:Entity {
  entity_id: 'concept_q206443',
  entity_cipher: 'ent_con_Q206443',
  qid: 'Q206443',
  label: 'Gallia Belgica',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 34,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 158: Q10971 (Gallia Lugdunensis)
CREATE (:Entity {
  entity_id: 'concept_q10971',
  entity_cipher: 'ent_con_Q10971',
  qid: 'Q10971',
  label: 'Gallia Lugdunensis',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 26,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 159: Q152136 (Germania Inferior)
CREATE (:Entity {
  entity_id: 'concept_q152136',
  entity_cipher: 'ent_con_Q152136',
  qid: 'Q152136',
  label: 'Germania Inferior',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 29,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 160: Q219415 (Hispania Baetica)
CREATE (:Entity {
  entity_id: 'concept_q219415',
  entity_cipher: 'ent_con_Q219415',
  qid: 'Q219415',
  label: 'Hispania Baetica',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 31,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 161: Q1330965 (Dalmatia)
CREATE (:Entity {
  entity_id: 'concept_q1330965',
  entity_cipher: 'ent_con_Q1330965',
  qid: 'Q1330965',
  label: 'Dalmatia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 20,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 162: Q734505 (Mauretania Caesariensis)
CREATE (:Entity {
  entity_id: 'concept_q734505',
  entity_cipher: 'ent_con_Q734505',
  qid: 'Q734505',
  label: 'Mauretania Caesariensis',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 25,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 163: Q18236771 (Moesia)
CREATE (:Entity {
  entity_id: 'concept_q18236771',
  entity_cipher: 'ent_con_Q18236771',
  qid: 'Q18236771',
  label: 'Moesia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 5,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 164: Q3878417 (Noricum)
CREATE (:Entity {
  entity_id: 'concept_q3878417',
  entity_cipher: 'ent_con_Q3878417',
  qid: 'Q3878417',
  label: 'Noricum',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 16,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 165: Q1247297 (Lower Pannonia)
CREATE (:Entity {
  entity_id: 'concept_q1247297',
  entity_cipher: 'ent_con_Q1247297',
  qid: 'Q1247297',
  label: 'Lower Pannonia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 13,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 166: Q642188 (Upper Pannonia)
CREATE (:Entity {
  entity_id: 'concept_q642188',
  entity_cipher: 'ent_con_Q642188',
  qid: 'Q642188',
  label: 'Upper Pannonia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 12,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 167: Q156789 (Raetia)
CREATE (:Entity {
  entity_id: 'concept_q156789',
  entity_cipher: 'ent_con_Q156789',
  qid: 'Q156789',
  label: 'Raetia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 45,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 168: Q281345 (Corsica and Sardinia)
CREATE (:Entity {
  entity_id: 'concept_q281345',
  entity_cipher: 'ent_con_Q281345',
  qid: 'Q281345',
  label: 'Corsica and Sardinia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 20,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 169: Q691321 (Sicilia)
CREATE (:Entity {
  entity_id: 'concept_q691321',
  entity_cipher: 'ent_con_Q691321',
  qid: 'Q691321',
  label: 'Sicilia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 170: Q207118 (Roman Syria)
CREATE (:Entity {
  entity_id: 'concept_q207118',
  entity_cipher: 'ent_con_Q207118',
  qid: 'Q207118',
  label: 'Roman Syria',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 27,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 171: Q27150039 (Coele-Syria)
CREATE (:Entity {
  entity_id: 'concept_q27150039',
  entity_cipher: 'ent_con_Q27150039',
  qid: 'Q27150039',
  label: 'Coele-Syria',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 11,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 172: Q635058 (Thracia)
CREATE (:Entity {
  entity_id: 'concept_q635058',
  entity_cipher: 'ent_con_Q635058',
  qid: 'Q635058',
  label: 'Thracia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 173: Q913582 (Roman Italy)
CREATE (:Entity {
  entity_id: 'concept_q913582',
  entity_cipher: 'ent_con_Q913582',
  qid: 'Q913582',
  label: 'Roman Italy',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 20,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 174: Q181238 (Africa)
CREATE (:Entity {
  entity_id: 'concept_q181238',
  entity_cipher: 'ent_con_Q181238',
  qid: 'Q181238',
  label: 'Africa',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 41,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 175: Q210718 (Asia)
CREATE (:Entity {
  entity_id: 'concept_q210718',
  entity_cipher: 'ent_con_Q210718',
  qid: 'Q210718',
  label: 'Asia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 35,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 176: Q185103 (Roman Britain)
CREATE (:Entity {
  entity_id: 'concept_q185103',
  entity_cipher: 'ent_con_Q185103',
  qid: 'Q185103',
  label: 'Roman Britain',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 49,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 177: Q913382 (Bithynia et Pontus)
CREATE (:Entity {
  entity_id: 'concept_q913382',
  entity_cipher: 'ent_con_Q913382',
  qid: 'Q913382',
  label: 'Bithynia et Pontus',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 21,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 178: Q2967757 (Cyprus)
CREATE (:Entity {
  entity_id: 'concept_q2967757',
  entity_cipher: 'ent_con_Q2967757',
  qid: 'Q2967757',
  label: 'Cyprus',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 18,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 179: Q26897 (Gallia Narbonensis)
CREATE (:Entity {
  entity_id: 'concept_q26897',
  entity_cipher: 'ent_con_Q26897',
  qid: 'Q26897',
  label: 'Gallia Narbonensis',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 40,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 180: Q40169 (Assyria)
CREATE (:Entity {
  entity_id: 'concept_q40169',
  entity_cipher: 'ent_con_Q40169',
  qid: 'Q40169',
  label: 'Assyria',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 181: Q11939617 (Osroene)
CREATE (:Entity {
  entity_id: 'concept_q11939617',
  entity_cipher: 'ent_con_Q11939617',
  qid: 'Q11939617',
  label: 'Osroene',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 13,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 182: Q1669578 (Syria Palaestina)
CREATE (:Entity {
  entity_id: 'concept_q1669578',
  entity_cipher: 'ent_con_Q1669578',
  qid: 'Q1669578',
  label: 'Syria Palaestina',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 25,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 183: Q264655 (vexillum)
CREATE (:Entity {
  entity_id: 'concept_q264655',
  entity_cipher: 'ent_con_Q264655',
  qid: 'Q264655',
  label: 'vexillum',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 184: Q163323 (Roman legion)
CREATE (:Entity {
  entity_id: 'concept_q163323',
  entity_cipher: 'ent_con_Q163323',
  qid: 'Q163323',
  label: 'Roman legion',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 29,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 185: Q5043 (Christianity)
CREATE (:Entity {
  entity_id: 'concept_q5043',
  entity_cipher: 'ent_con_Q5043',
  qid: 'Q5043',
  label: 'Christianity',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 165,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 186: Q29536 (paganism)
CREATE (:Entity {
  entity_id: 'concept_q29536',
  entity_cipher: 'ent_con_Q29536',
  qid: 'Q29536',
  label: 'paganism',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 56,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 187: Q83922 (Arianism)
CREATE (:Entity {
  entity_id: 'concept_q83922',
  entity_cipher: 'ent_con_Q83922',
  qid: 'Q83922',
  label: 'Arianism',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 59,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 188: Q42353313 (Portal:Roman Empire)
CREATE (:Entity {
  entity_id: 'concept_q42353313',
  entity_cipher: 'ent_con_Q42353313',
  qid: 'Q42353313',
  label: 'Portal:Roman Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 189: Q1154753 (Book of Jin)
CREATE (:Entity {
  entity_id: 'concept_q1154753',
  entity_cipher: 'ent_con_Q1154753',
  qid: 'Q1154753',
  label: 'Book of Jin',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 16,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 190: Q16082057 (The New Student\'s Reference Work)
CREATE (:Entity {
  entity_id: 'concept_q16082057',
  entity_cipher: 'ent_con_Q16082057',
  qid: 'Q16082057',
  label: 'The New Student\'s Reference Work',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 11,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 191: Q8607609 (Category:Maps of the Roman Empire)
CREATE (:Entity {
  entity_id: 'concept_q8607609',
  entity_cipher: 'ent_con_Q8607609',
  qid: 'Q8607609',
  label: 'Category:Maps of the Roman Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 192: Q178897 (Latin Empire)
CREATE (:Entity {
  entity_id: 'concept_q178897',
  entity_cipher: 'ent_con_Q178897',
  qid: 'Q178897',
  label: 'Latin Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 37,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 193: Q3718695 (economy of the Roman Empire)
CREATE (:Entity {
  entity_id: 'concept_q3718695',
  entity_cipher: 'ent_con_Q3718695',
  qid: 'Q3718695',
  label: 'economy of the Roman Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 194: Q3974187 (military history of ancient Rome)
CREATE (:Entity {
  entity_id: 'concept_q3974187',
  entity_cipher: 'ent_con_Q3974187',
  qid: 'Q3974187',
  label: 'military history of ancient Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 8,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 195: Q16186 (Province of Imperia)
CREATE (:Entity {
  entity_id: 'concept_q16186',
  entity_cipher: 'ent_con_Q16186',
  qid: 'Q16186',
  label: 'Province of Imperia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 63,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 196: Q124737636 (Armenian Soviet Encyclopedia, vol. 9)
CREATE (:Entity {
  entity_id: 'concept_q124737636',
  entity_cipher: 'ent_con_Q124737636',
  qid: 'Q124737636',
  label: 'Armenian Soviet Encyclopedia, vol. 9',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 5,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 197: Q238399 (Dominate)
CREATE (:Entity {
  entity_id: 'concept_q238399',
  entity_cipher: 'ent_con_Q238399',
  qid: 'Q238399',
  label: 'Dominate',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 198: Q787204 (High Roman Empire)
CREATE (:Entity {
  entity_id: 'concept_q787204',
  entity_cipher: 'ent_con_Q787204',
  qid: 'Q787204',
  label: 'High Roman Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 14,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 199: Q2566630 (Roman Iron Age)
CREATE (:Entity {
  entity_id: 'concept_q2566630',
  entity_cipher: 'ent_con_Q2566630',
  qid: 'Q2566630',
  label: 'Roman Iron Age',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 9,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 200: Q830852 (history of ancient Rome)
CREATE (:Entity {
  entity_id: 'concept_q830852',
  entity_cipher: 'ent_con_Q830852',
  qid: 'Q830852',
  label: 'history of ancient Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 12,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 201: Q1048669 (Latium)
CREATE (:Entity {
  entity_id: 'concept_q1048669',
  entity_cipher: 'ent_con_Q1048669',
  qid: 'Q1048669',
  label: 'Latium',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 21,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 202: Q326197 (list of kings of Rome)
CREATE (:Entity {
  entity_id: 'concept_q326197',
  entity_cipher: 'ent_con_Q326197',
  qid: 'Q326197',
  label: 'list of kings of Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 6,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 203: Q3921629 (First Roman Kingdom)
CREATE (:Entity {
  entity_id: 'concept_q3921629',
  entity_cipher: 'ent_con_Q3921629',
  qid: 'Q3921629',
  label: 'First Roman Kingdom',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 9,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 204: Q584683 (elective monarchy)
CREATE (:Entity {
  entity_id: 'concept_q584683',
  entity_cipher: 'ent_con_Q584683',
  qid: 'Q584683',
  label: 'elective monarchy',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 9,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 205: Q55375123 (King of Rome)
CREATE (:Entity {
  entity_id: 'concept_q55375123',
  entity_cipher: 'ent_con_Q55375123',
  qid: 'Q55375123',
  label: 'King of Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 14,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 206: Q5171759 (Corniculum)
CREATE (:Entity {
  entity_id: 'concept_q5171759',
  entity_cipher: 'ent_con_Q5171759',
  qid: 'Q5171759',
  label: 'Corniculum',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 14,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 207: Q11381903 (Portal:Rome)
CREATE (:Entity {
  entity_id: 'concept_q11381903',
  entity_cipher: 'ent_con_Q11381903',
  qid: 'Q11381903',
  label: 'Portal:Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 208: Q48740750 (outline of Rome)
CREATE (:Entity {
  entity_id: 'concept_q48740750',
  entity_cipher: 'ent_con_Q48740750',
  qid: 'Q48740750',
  label: 'outline of Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 209: Q10142763 (Category:People from Rome)
CREATE (:Entity {
  entity_id: 'concept_q10142763',
  entity_cipher: 'ent_con_Q10142763',
  qid: 'Q10142763',
  label: 'Category:People from Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 210: Q23936560 (mayor of Rome)
CREATE (:Entity {
  entity_id: 'concept_q23936560',
  entity_cipher: 'ent_con_Q23936560',
  qid: 'Q23936560',
  label: 'mayor of Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 17,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 211: Q33923 (Saint Peter)
CREATE (:Entity {
  entity_id: 'concept_q33923',
  entity_cipher: 'ent_con_Q33923',
  qid: 'Q33923',
  label: 'Saint Peter',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 168,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 212: Q9200 (Paul the Apostle)
CREATE (:Entity {
  entity_id: 'concept_q9200',
  entity_cipher: 'ent_con_Q9200',
  qid: 'Q9200',
  label: 'Paul the Apostle',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 213,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 213: Q22665612 (Q22665612)
CREATE (:Entity {
  entity_id: 'concept_q22665612',
  entity_cipher: 'ent_con_Q22665612',
  qid: 'Q22665612',
  label: 'Q22665612',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 214: Q18288160 (Metropolitan City of Rome)
CREATE (:Entity {
  entity_id: 'place_q18288160',
  entity_cipher: 'ent_plc_Q18288160',
  qid: 'Q18288160',
  label: 'Metropolitan City of Rome',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 48,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 215: Q38 (Italy)
CREATE (:Entity {
  entity_id: 'concept_q38',
  entity_cipher: 'ent_con_Q38',
  qid: 'Q38',
  label: 'Italy',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 369,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 216: Q1282 (Lazio)
CREATE (:Entity {
  entity_id: 'concept_q1282',
  entity_cipher: 'ent_con_Q1282',
  qid: 'Q1282',
  label: 'Lazio',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 107,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 217: Q170174 (Papal States)
CREATE (:Entity {
  entity_id: 'concept_q170174',
  entity_cipher: 'ent_con_Q170174',
  qid: 'Q170174',
  label: 'Papal States',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 81,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 218: Q3528124 (Tibre)
CREATE (:Entity {
  entity_id: 'concept_q3528124',
  entity_cipher: 'ent_con_Q3528124',
  qid: 'Q3528124',
  label: 'Tibre',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 10,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 219: Q172579 (Kingdom of Italy)
CREATE (:Entity {
  entity_id: 'concept_q172579',
  entity_cipher: 'ent_con_Q172579',
  qid: 'Q172579',
  label: 'Kingdom of Italy',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 59,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 220: Q3940419 (Roma Capitale)
CREATE (:Entity {
  entity_id: 'concept_q3940419',
  entity_cipher: 'ent_con_Q3940419',
  qid: 'Q3940419',
  label: 'Roma Capitale',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 25,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 221: Q1072140 (Roman Republic)
CREATE (:Entity {
  entity_id: 'concept_q1072140',
  entity_cipher: 'ent_con_Q1072140',
  qid: 'Q1072140',
  label: 'Roman Republic',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 46,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 222: Q134317926 (Italian State)
CREATE (:Entity {
  entity_id: 'concept_q134317926',
  entity_cipher: 'ent_con_Q134317926',
  qid: 'Q134317926',
  label: 'Italian State',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 7,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 223: Q15119 (Province of Rome)
CREATE (:Entity {
  entity_id: 'concept_q15119',
  entity_cipher: 'ent_con_Q15119',
  qid: 'Q15119',
  label: 'Province of Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 72,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 224: Q42834 (Western Roman Empire)
CREATE (:Entity {
  entity_id: 'concept_q42834',
  entity_cipher: 'ent_con_Q42834',
  qid: 'Q42834',
  label: 'Western Roman Empire',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 60,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 225: Q3677829 (circle of Rome)
CREATE (:Entity {
  entity_id: 'concept_q3677829',
  entity_cipher: 'ent_con_Q3677829',
  qid: 'Q3677829',
  label: 'circle of Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 7,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 226: Q1200427 (culture of ancient Rome)
CREATE (:Entity {
  entity_id: 'concept_q1200427',
  entity_cipher: 'ent_con_Q1200427',
  qid: 'Q1200427',
  label: 'culture of ancient Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 14,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 227: Q3678788 (Byzantine civilization)
CREATE (:Entity {
  entity_id: 'concept_q3678788',
  entity_cipher: 'ent_con_Q3678788',
  qid: 'Q3678788',
  label: 'Byzantine civilization',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 228: Q13712 (Tiber)
CREATE (:Entity {
  entity_id: 'concept_q13712',
  entity_cipher: 'ent_con_Q13712',
  qid: 'Q13712',
  label: 'Tiber',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 69,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 229: Q38882 (Tyrrhenian Sea)
CREATE (:Entity {
  entity_id: 'concept_q38882',
  entity_cipher: 'ent_con_Q38882',
  qid: 'Q38882',
  label: 'Tyrrhenian Sea',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 5,
  properties_count: 61,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 230: Q583038 (Ostrogothic Kingdom)
CREATE (:Entity {
  entity_id: 'concept_q583038',
  entity_cipher: 'ent_con_Q583038',
  qid: 'Q583038',
  label: 'Ostrogothic Kingdom',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 25,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 231: Q237 (Vatican City)
CREATE (:Entity {
  entity_id: 'place_q237',
  entity_cipher: 'ent_plc_Q237',
  qid: 'Q237',
  label: 'Vatican City',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 255,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 232: Q90 (Paris)
CREATE (:Entity {
  entity_id: 'concept_q90',
  entity_cipher: 'ent_con_Q90',
  qid: 'Q90',
  label: 'Paris',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 317,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 233: Q31487 (Kraków)
CREATE (:Entity {
  entity_id: 'place_q31487',
  entity_cipher: 'ent_plc_Q31487',
  qid: 'Q31487',
  label: 'Kraków',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 170,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 234: Q43196 (Cincinnati)
CREATE (:Entity {
  entity_id: 'place_q43196',
  entity_cipher: 'ent_plc_Q43196',
  qid: 'Q43196',
  label: 'Cincinnati',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 129,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 235: Q132830 (Douala)
CREATE (:Entity {
  entity_id: 'place_q132830',
  entity_cipher: 'ent_plc_Q132830',
  qid: 'Q132830',
  label: 'Douala',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 70,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 236: Q484799 (Marbella)
CREATE (:Entity {
  entity_id: 'concept_q484799',
  entity_cipher: 'ent_con_Q484799',
  qid: 'Q484799',
  label: 'Marbella',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 77,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 237: Q1819965 (Achacachi Municipality)
CREATE (:Entity {
  entity_id: 'concept_q1819965',
  entity_cipher: 'ent_con_Q1819965',
  qid: 'Q1819965',
  label: 'Achacachi Municipality',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 16,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 238: Q1490 (Tokyo)
CREATE (:Entity {
  entity_id: 'concept_q1490',
  entity_cipher: 'ent_con_Q1490',
  qid: 'Q1490',
  label: 'Tokyo',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 223,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 239: Q8717 (Seville)
CREATE (:Entity {
  entity_id: 'concept_q8717',
  entity_cipher: 'ent_con_Q8717',
  qid: 'Q8717',
  label: 'Seville',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 146,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 240: Q13437 (Benevento)
CREATE (:Entity {
  entity_id: 'concept_q13437',
  entity_cipher: 'ent_con_Q13437',
  qid: 'Q13437',
  label: 'Benevento',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 105,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 241: Q8684 (Seoul)
CREATE (:Entity {
  entity_id: 'place_q8684',
  entity_cipher: 'ent_plc_Q8684',
  qid: 'Q8684',
  label: 'Seoul',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 205,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 242: Q3689056 (Contrada della Lupa)
CREATE (:Entity {
  entity_id: 'concept_q3689056',
  entity_cipher: 'ent_con_Q3689056',
  qid: 'Q3689056',
  label: 'Contrada della Lupa',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 243: Q459 (Plovdiv)
CREATE (:Entity {
  entity_id: 'place_q459',
  entity_cipher: 'ent_plc_Q459',
  qid: 'Q459',
  label: 'Plovdiv',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 112,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 244: Q61 (Washington, D.C.)
CREATE (:Entity {
  entity_id: 'place_q61',
  entity_cipher: 'ent_plc_Q61',
  qid: 'Q61',
  label: 'Washington, D.C.',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 253,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 245: Q2844 (Brasília)
CREATE (:Entity {
  entity_id: 'place_q2844',
  entity_cipher: 'ent_plc_Q2844',
  qid: 'Q2844',
  label: 'Brasília',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 133,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 246: Q956 (Beijing)
CREATE (:Entity {
  entity_id: 'place_q956',
  entity_cipher: 'ent_plc_Q956',
  qid: 'Q956',
  label: 'Beijing',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 189,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 247: Q1489 (Mexico City)
CREATE (:Entity {
  entity_id: 'place_q1489',
  entity_cipher: 'ent_plc_Q1489',
  qid: 'Q1489',
  label: 'Mexico City',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 198,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 248: Q19689 (Tirana)
CREATE (:Entity {
  entity_id: 'place_q19689',
  entity_cipher: 'ent_plc_Q19689',
  qid: 'Q19689',
  label: 'Tirana',
  entity_type: 'PLACE',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 121,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 249: Q8682052 (Category:Rome)
CREATE (:Entity {
  entity_id: 'concept_q8682052',
  entity_cipher: 'ent_con_Q8682052',
  qid: 'Q8682052',
  label: 'Category:Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 4,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 250: Q7977790 (Category:Burials in Rome by place)
CREATE (:Entity {
  entity_id: 'concept_q7977790',
  entity_cipher: 'ent_con_Q7977790',
  qid: 'Q7977790',
  label: 'Category:Burials in Rome by place',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 3,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 251: Q463130 (Gianni Alemanno)
CREATE (:Entity {
  entity_id: 'person_q463130',
  entity_cipher: 'ent_per_Q463130',
  qid: 'Q463130',
  label: 'Gianni Alemanno',
  entity_type: 'PERSON',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 47,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 252: Q535345 (Francesco Rutelli)
CREATE (:Entity {
  entity_id: 'person_q535345',
  entity_cipher: 'ent_per_Q535345',
  qid: 'Q535345',
  label: 'Francesco Rutelli',
  entity_type: 'PERSON',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 60,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 253: Q319547 (Walter Veltroni)
CREATE (:Entity {
  entity_id: 'person_q319547',
  entity_cipher: 'ent_per_Q319547',
  qid: 'Q319547',
  label: 'Walter Veltroni',
  entity_type: 'PERSON',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 96,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 254: Q1394623 (Franco Carraro)
CREATE (:Entity {
  entity_id: 'person_q1394623',
  entity_cipher: 'ent_per_Q1394623',
  qid: 'Q1394623',
  label: 'Franco Carraro',
  entity_type: 'PERSON',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 37,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 255: Q948169 (Roberto Gualtieri)
CREATE (:Entity {
  entity_id: 'person_q948169',
  entity_cipher: 'ent_per_Q948169',
  qid: 'Q948169',
  label: 'Roberto Gualtieri',
  entity_type: 'PERSON',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 58,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 256: Q6469667 (Category:Films shot in Rome)
CREATE (:Entity {
  entity_id: 'concept_q6469667',
  entity_cipher: 'ent_con_Q6469667',
  qid: 'Q6469667',
  label: 'Category:Films shot in Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 5,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 257: Q642958 (Stadio Nazionale)
CREATE (:Entity {
  entity_id: 'concept_q642958',
  entity_cipher: 'ent_con_Q642958',
  qid: 'Q642958',
  label: 'Stadio Nazionale',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 23,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 258: Q737333 (Cornelia)
CREATE (:Entity {
  entity_id: 'concept_q737333',
  entity_cipher: 'ent_con_Q737333',
  qid: 'Q737333',
  label: 'Cornelia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 25,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 259: Q1189119 (Foro Italico swimming complex)
CREATE (:Entity {
  entity_id: 'concept_q1189119',
  entity_cipher: 'ent_con_Q1189119',
  qid: 'Q1189119',
  label: 'Foro Italico swimming complex',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 15,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 260: Q42949340 (Cod. Pal. germ. 313)
CREATE (:Entity {
  entity_id: 'concept_q42949340',
  entity_cipher: 'ent_con_Q42949340',
  qid: 'Q42949340',
  label: 'Cod. Pal. germ. 313',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 17,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 261: Q241693 (Anguillara Sabazia)
CREATE (:Entity {
  entity_id: 'concept_q241693',
  entity_cipher: 'ent_con_Q241693',
  qid: 'Q241693',
  label: 'Anguillara Sabazia',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 61,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 262: Q241733 (Ardea)
CREATE (:Entity {
  entity_id: 'concept_q241733',
  entity_cipher: 'ent_con_Q241733',
  qid: 'Q241733',
  label: 'Ardea',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 60,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 263: Q242105 (Castel Gandolfo)
CREATE (:Entity {
  entity_id: 'concept_q242105',
  entity_cipher: 'ent_con_Q242105',
  qid: 'Q242105',
  label: 'Castel Gandolfo',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 80,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 264: Q242513 (Ciampino)
CREATE (:Entity {
  entity_id: 'concept_q242513',
  entity_cipher: 'ent_con_Q242513',
  qid: 'Q242513',
  label: 'Ciampino',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 50,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 265: Q242558 (Colonna)
CREATE (:Entity {
  entity_id: 'concept_q242558',
  entity_cipher: 'ent_con_Q242558',
  qid: 'Q242558',
  label: 'Colonna',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 40,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 266: Q19326 (Fiumicino)
CREATE (:Entity {
  entity_id: 'concept_q19326',
  entity_cipher: 'ent_con_Q19326',
  qid: 'Q19326',
  label: 'Fiumicino',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 59,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 267: Q242637 (Fonte Nuova)
CREATE (:Entity {
  entity_id: 'concept_q242637',
  entity_cipher: 'ent_con_Q242637',
  qid: 'Q242637',
  label: 'Fonte Nuova',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 41,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 268: Q242645 (Formello)
CREATE (:Entity {
  entity_id: 'concept_q242645',
  entity_cipher: 'ent_con_Q242645',
  qid: 'Q242645',
  label: 'Formello',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 48,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 269: Q242703 (Grottaferrata)
CREATE (:Entity {
  entity_id: 'concept_q242703',
  entity_cipher: 'ent_con_Q242703',
  qid: 'Q242703',
  label: 'Grottaferrata',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 72,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 270: Q242965 (Monte Porzio Catone)
CREATE (:Entity {
  entity_id: 'concept_q242965',
  entity_cipher: 'ent_con_Q242965',
  qid: 'Q242965',
  label: 'Monte Porzio Catone',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 54,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 271: Q242998 (Monterotondo)
CREATE (:Entity {
  entity_id: 'concept_q242998',
  entity_cipher: 'ent_con_Q242998',
  qid: 'Q242998',
  label: 'Monterotondo',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 53,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 272: Q243311 (Sacrofano)
CREATE (:Entity {
  entity_id: 'concept_q243311',
  entity_cipher: 'ent_con_Q243311',
  qid: 'Q243311',
  label: 'Sacrofano',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 40,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 273: Q243497 (Trevignano Romano)
CREATE (:Entity {
  entity_id: 'concept_q243497',
  entity_cipher: 'ent_con_Q243497',
  qid: 'Q243497',
  label: 'Trevignano Romano',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 51,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 274: Q191115 (Albano Laziale)
CREATE (:Entity {
  entity_id: 'concept_q191115',
  entity_cipher: 'ent_con_Q191115',
  qid: 'Q191115',
  label: 'Albano Laziale',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 72,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 275: Q241911 (Campagnano di Roma)
CREATE (:Entity {
  entity_id: 'concept_q241911',
  entity_cipher: 'ent_con_Q241911',
  qid: 'Q241911',
  label: 'Campagnano di Roma',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 4,
  properties_count: 47,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 276: Q242120 (Castel San Pietro Romano)
CREATE (:Entity {
  entity_id: 'concept_q242120',
  entity_cipher: 'ent_con_Q242120',
  qid: 'Q242120',
  label: 'Castel San Pietro Romano',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 44,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 277: Q190963 (Frascati)
CREATE (:Entity {
  entity_id: 'concept_q190963',
  entity_cipher: 'ent_con_Q190963',
  qid: 'Q190963',
  label: 'Frascati',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 81,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 278: Q242661 (Gallicano nel Lazio)
CREATE (:Entity {
  entity_id: 'concept_q242661',
  entity_cipher: 'ent_con_Q242661',
  qid: 'Q242661',
  label: 'Gallicano nel Lazio',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 41,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 279: Q242926 (Marino)
CREATE (:Entity {
  entity_id: 'concept_q242926',
  entity_cipher: 'ent_con_Q242926',
  qid: 'Q242926',
  label: 'Marino',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 66,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 280: Q243133 (Palestrina)
CREATE (:Entity {
  entity_id: 'concept_q243133',
  entity_cipher: 'ent_con_Q243133',
  qid: 'Q243133',
  label: 'Palestrina',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 5,
  properties_count: 76,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 281: Q243188 (Riano)
CREATE (:Entity {
  entity_id: 'concept_q243188',
  entity_cipher: 'ent_con_Q243188',
  qid: 'Q243188',
  label: 'Riano',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 37,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 282: Q242710 (Guidonia Montecelio)
CREATE (:Entity {
  entity_id: 'concept_q242710',
  entity_cipher: 'ent_con_Q242710',
  qid: 'Q242710',
  label: 'Guidonia Montecelio',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 61,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 283: Q8070169 (Category:Births in Rome)
CREATE (:Entity {
  entity_id: 'concept_q8070169',
  entity_cipher: 'ent_con_Q8070169',
  qid: 'Q8070169',
  label: 'Category:Births in Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 5,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 284: Q1242632 (Remus)
CREATE (:Entity {
  entity_id: 'person_q1242632',
  entity_cipher: 'ent_per_Q1242632',
  qid: 'Q1242632',
  label: 'Remus',
  entity_type: 'PERSON',
  namespace: 'wd',
  federation_score: 3,
  properties_count: 58,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 285: Q16494134 (Municipio II)
CREATE (:Entity {
  entity_id: 'concept_q16494134',
  entity_cipher: 'ent_con_Q16494134',
  qid: 'Q16494134',
  label: 'Municipio II',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 21,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 286: Q16003470 (Municipio III)
CREATE (:Entity {
  entity_id: 'concept_q16003470',
  entity_cipher: 'ent_con_Q16003470',
  qid: 'Q16003470',
  label: 'Municipio III',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 287: Q16481953 (Municipio V)
CREATE (:Entity {
  entity_id: 'concept_q16481953',
  entity_cipher: 'ent_con_Q16481953',
  qid: 'Q16481953',
  label: 'Municipio V',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 288: Q16481966 (Municipio VII)
CREATE (:Entity {
  entity_id: 'concept_q16481966',
  entity_cipher: 'ent_con_Q16481966',
  qid: 'Q16481966',
  label: 'Municipio VII',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 21,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 289: Q16495467 (Municipio VIII)
CREATE (:Entity {
  entity_id: 'concept_q16495467',
  entity_cipher: 'ent_con_Q16495467',
  qid: 'Q16495467',
  label: 'Municipio VIII',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 23,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 290: Q16481977 (Municipio X)
CREATE (:Entity {
  entity_id: 'concept_q16481977',
  entity_cipher: 'ent_con_Q16481977',
  qid: 'Q16481977',
  label: 'Municipio X',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 291: Q16481992 (Municipio XII)
CREATE (:Entity {
  entity_id: 'concept_q16481992',
  entity_cipher: 'ent_con_Q16481992',
  qid: 'Q16481992',
  label: 'Municipio XII',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 20,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 292: Q16482002 (Municipio XIV)
CREATE (:Entity {
  entity_id: 'concept_q16482002',
  entity_cipher: 'ent_con_Q16482002',
  qid: 'Q16482002',
  label: 'Municipio XIV',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 22,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 293: Q4173137 (Jewish Encyclopedia of Brockhaus and Efron)
CREATE (:Entity {
  entity_id: 'concept_q4173137',
  entity_cipher: 'ent_con_Q4173137',
  qid: 'Q4173137',
  label: 'Jewish Encyclopedia of Brockhaus and Efron',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 16,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 294: Q20961706 (Infernal Dictionary, 6th ed.)
CREATE (:Entity {
  entity_id: 'concept_q20961706',
  entity_cipher: 'ent_con_Q20961706',
  qid: 'Q20961706',
  label: 'Infernal Dictionary, 6th ed.',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 14,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 295: Q111600428 (Q111600428)
CREATE (:Entity {
  entity_id: 'concept_q111600428',
  entity_cipher: 'ent_con_Q111600428',
  qid: 'Q111600428',
  label: 'Q111600428',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 9,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 296: Q126374795 (Meyer’s Universum, Erster Band)
CREATE (:Entity {
  entity_id: 'concept_q126374795',
  entity_cipher: 'ent_con_Q126374795',
  qid: 'Q126374795',
  label: 'Meyer’s Universum, Erster Band',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 297: Q137757464 (Meyer’s Universum, Zwanzigster Band)
CREATE (:Entity {
  entity_id: 'concept_q137757464',
  entity_cipher: 'ent_con_Q137757464',
  qid: 'Q137757464',
  label: 'Meyer’s Universum, Zwanzigster Band',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 19,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 298: Q6701024 (Category:Geography of Ancient Rome)
CREATE (:Entity {
  entity_id: 'concept_q6701024',
  entity_cipher: 'ent_con_Q6701024',
  qid: 'Q6701024',
  label: 'Category:Geography of Ancient Rome',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 2,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 299: Q652 (Italian)
CREATE (:Entity {
  entity_id: 'concept_q652',
  entity_cipher: 'ent_con_Q652',
  qid: 'Q652',
  label: 'Italian',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 2,
  properties_count: 127,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// Entity 300: Q6655 (UTC+01:00)
CREATE (:Entity {
  entity_id: 'concept_q6655',
  entity_cipher: 'ent_con_Q6655',
  qid: 'Q6655',
  label: 'UTC+01:00',
  entity_type: 'CONCEPT',
  namespace: 'wd',
  federation_score: 1,
  properties_count: 7,
  discovered_from: 'sca_traversal',
  imported_at: datetime()
})


// ============ FACETED ENTITIES (Sample - First 10) ============


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q17167_Q17167',
  entity_cipher: 'ent_sub_Q17167',
  qid: 'Q17167',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q11514315_Q17167',
  entity_cipher: 'ent_con_Q11514315',
  qid: 'Q11514315',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q1307214_Q17167',
  entity_cipher: 'ent_con_Q1307214',
  qid: 'Q1307214',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q48349_Q17167',
  entity_cipher: 'ent_con_Q48349',
  qid: 'Q48349',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q3024240_Q17167',
  entity_cipher: 'ent_con_Q3024240',
  qid: 'Q3024240',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q6944405_Q17167',
  entity_cipher: 'ent_con_Q6944405',
  qid: 'Q6944405',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q337547_Q17167',
  entity_cipher: 'ent_con_Q337547',
  qid: 'Q337547',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q130614_Q17167',
  entity_cipher: 'ent_con_Q130614',
  qid: 'Q130614',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q1114821_Q17167',
  entity_cipher: 'ent_org_Q1114821',
  qid: 'Q1114821',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_arc_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'ARCHAEOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_art_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'ARTISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_bio_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'BIOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_com_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'COMMUNICATION',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_cul_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'CULTURAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dem_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'DEMOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_dip_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'DIPLOMATIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_eco_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'ECONOMIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_env_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'ENVIRONMENTAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_geo_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'GEOGRAPHIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_int_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'INTELLECTUAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_lin_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'LINGUISTIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_mil_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'MILITARY',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_pol_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'POLITICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_rel_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'RELIGIOUS',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_sci_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'SCIENTIFIC',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_soc_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'SOCIAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})


CREATE (:FacetedEntity {
  faceted_cipher: 'fent_tec_Q952064_Q17167',
  entity_cipher: 'ent_con_Q952064',
  qid: 'Q952064',
  facet_id: 'TECHNOLOGICAL',
  subjectconcept_id: 'Q17167',
  created_at: datetime()
})
