// Neo4j Import - SCA Entities with Ciphers
// Generated: 2026-02-23T07:57:10.659984
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
MERGE (n:Entity {qid: 'Q17167'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q17167',
  n.entity_id = 'subjectconcept_q17167',
  n.label = 'Roman Republic',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 61,
  n.property_summary = '{\'P31\': [\'Q11514315\', \'Q1307214\', \'Q48349\', \'Q3024240\'], \'P910\': [\'Q6944405\'], \'P140\': [\'Q337547\'], \'P194\': [\'Q130614\', \'Q1114821\'], \'P38\': [\'Q952064\'], \'P2348\': [\'Q486761\'], \'P1792\': [\'Q13285410\'], \'P527\': [\'Q2839628\', \'Q6106068\', \'Q2815472\'], \'P1366\': [\'Q2277\', \'Q206414\'], \'P155\': [\'Q201038\'], \'P36\': [\'Q220\'], \'P2936\': [\'Q397\', \'Q35497\'], \'P30\': [\'Q46\', \'Q48\', \'Q15\'], \'P3075\': [\'Q337547\'], \'P122\': [\'Q666680\'], \'P1365\': [\'Q201038\'], \'P361\': [\'Q1747689\'], \'P1889\': [\'Q346629\'], \'P5008\': [\'Q6173448\'], \'P793\': [\'Q124988\', \'Q3778726\', \'Q75813\', \'Q202161\', \'Q596373\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 2: Q11514315 (historical period)
MERGE (n:Entity {qid: 'Q11514315'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q11514315',
  n.entity_id = 'concept_q11514315',
  n.label = 'historical period',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 20,
  n.property_summary = '{\'P279\': [\'Q6428674\'], \'P2354\': [\'Q17004260\'], \'P1687\': [\'P2408\', \'P2348\'], \'P8952\': [\'P571\', \'P1365\', \'P576\', \'P1366\'], \'P1963\': [\'P580\', \'P156\', \'P582\', \'P155\'], \'P1889\': [\'Q816829\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 3: Q1307214 (form of government)
MERGE (n:Entity {qid: 'Q1307214'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1307214',
  n.entity_id = 'concept_q1307214',
  n.label = 'form of government',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 30,
  n.property_summary = '{\'P279\': [\'Q183039\', \'Q2752458\', \'Q28108\'], \'P910\': [\'Q54069\'], \'P1687\': [\'P122\'], \'P1889\': [\'Q183039\', \'Q5589178\', \'Q19944802\', \'Q28108\', \'Q20076236\'], \'P527\': [\'Q759524\', \'Q191600\', \'Q31728\'], \'P1424\': [\'Q6526407\', \'Q25728256\', \'Q15838730\'], \'P8225\': [\'Q7188\'], \'P31\': [\'Q19478619\'], \'P13044\': [\'Q7188\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 4: Q48349 (empire)
MERGE (n:Entity {qid: 'Q48349'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q48349',
  n.entity_id = 'concept_q48349',
  n.label = 'empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 55,
  n.property_summary = '{\'P910\': [\'Q6135095\'], \'P1343\': [\'Q20743760\', \'Q2041543\', \'Q867541\', \'Q101314624\', \'Q20078554\'], \'P2354\': [\'Q1151047\'], \'P1889\': [\'Q499146\', \'Q978370\', \'Q356252\'], \'P1424\': [\'Q7477250\'], \'P5008\': [\'Q6173448\'], \'P279\': [\'Q1250464\', \'Q3624078\'], \'P31\': [\'Q7269\'], \'P35\': [\'Q39018\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 5: Q3024240 (historical country)
MERGE (n:Entity {qid: 'Q3024240'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3024240',
  n.entity_id = 'concept_q3024240',
  n.label = 'historical country',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 16,
  n.property_summary = '{\'P279\': [\'Q19953632\', \'Q96196009\', \'Q19832712\', \'Q6256\'], \'P910\': [\'Q7238252\'], \'P1687\': [\'P17\'], \'P1424\': [\'Q6036853\'], \'P1889\': [\'Q3591867\'], \'P8952\': [\'P582\', \'P580\'], \'P1963\': [\'P571\', \'P1365\', \'P576\', \'P1366\', \'P36\'], \'P2354\': [\'Q62630\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 6: Q6944405 (Category:Roman Republic)
MERGE (n:Entity {qid: 'Q6944405'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6944405',
  n.entity_id = 'concept_q6944405',
  n.label = 'Category:Roman Republic',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P301\': [\'Q17167\'], \'P4224\': [\'Q5\'], \'P155\': [\'Q8678306\'], \'P156\': [\'Q1456601\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 7: Q337547 (ancient Roman religion)
MERGE (n:Entity {qid: 'Q337547'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q337547',
  n.entity_id = 'concept_q337547',
  n.label = 'ancient Roman religion',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 31,
  n.property_summary = '{\'P910\': [\'Q8251375\'], \'P1343\': [\'Q602358\', \'Q30059240\', \'Q867541\'], \'P31\': [\'Q108704490\'], \'P1889\': [\'Q107013262\', \'Q107013169\'], \'P1424\': [\'Q5626901\'], \'P361\': [\'Q122173\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 8: Q130614 (Roman Senate)
MERGE (n:Entity {qid: 'Q130614'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q130614',
  n.entity_id = 'concept_q130614',
  n.label = 'Roman Senate',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 27,
  n.property_summary = '{\'P31\': [\'Q11204\', \'Q123432\', \'Q2570643\'], \'P159\': [\'Q1144514\', \'Q5194731\', \'Q1144512\'], \'P17\': [\'Q1747689\'], \'P527\': [\'Q20056508\'], \'P1343\': [\'Q30059240\', \'Q602358\'], \'P910\': [\'Q32899669\'], \'P2348\': [\'Q486761\'], \'P1889\': [\'Q343948\', \'Q1466018\'], \'P2670\': [\'Q20056508\'], \'P828\': [\'Q1225322\'], \'P5008\': [\'Q6173448\'], \'P279\': [\'Q2915100\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 9: Q1114821 (citizens\' assemblies of the Roman Republic)
MERGE (n:Entity {qid: 'Q1114821'})
ON CREATE SET
  n.entity_cipher = 'ent_org_Q1114821',
  n.entity_id = 'organization_q1114821',
  n.label = 'citizens\\\' assemblies of the Roman Republic',
  n.entity_type = 'ORGANIZATION',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 10,
  n.property_summary = '{\'P31\': [\'Q17197366\'], \'P279\': [\'Q11204\'], \'P1343\': [\'Q3181656\', \'Q1138524\', \'Q867541\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q17167\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 10: Q952064 (Roman currency)
MERGE (n:Entity {qid: 'Q952064'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q952064',
  n.entity_id = 'concept_q952064',
  n.label = 'Roman currency',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 26,
  n.property_summary = '{\'P910\': [\'Q8386687\'], \'P31\': [\'Q17524420\'], \'P1269\': [\'Q1747689\'], \'P1343\': [\'Q602358\', \'Q1138524\', \'Q30059240\', \'Q19219752\'], \'P527\': [\'Q662137\', \'Q638048\'], \'P279\': [\'Q8142\', \'Q28783456\'], \'P2579\': [\'Q3879434\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 11: Q486761 (classical antiquity)
MERGE (n:Entity {qid: 'Q486761'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q486761',
  n.entity_id = 'subjectconcept_q486761',
  n.label = 'classical antiquity',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 68,
  n.property_summary = '{\'P527\': [\'Q14618893\', \'Q17167\', \'Q428995\', \'Q11772\', \'Q181264\'], \'P910\': [\'Q8381710\'], \'P156\': [\'Q217050\'], \'P1269\': [\'Q937284\'], \'P31\': [\'Q11514315\', \'Q1292119\'], \'P1889\': [\'Q41493\'], \'P279\': [\'Q41493\'], \'P155\': [\'Q98270938\'], \'P2579\': [\'Q112939719\', \'Q495527\'], \'P5008\': [\'Q6173448\'], \'P361\': [\'Q41493\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 12: Q13285410 (Category:People from the Roman Republic)
MERGE (n:Entity {qid: 'Q13285410'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q13285410',
  n.entity_id = 'concept_q13285410',
  n.label = 'Category:People from the Roman Republic',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q19660746\', \'Q17167\', \'Q5\'], \'P4224\': [\'Q5\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 13: Q2839628 (Early Roman Republic)
MERGE (n:Entity {qid: 'Q2839628'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q2839628',
  n.entity_id = 'subjectconcept_q2839628',
  n.label = 'Early Roman Republic',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P31\': [\'Q11514315\'], \'P361\': [\'Q17167\'], \'P155\': [\'Q201038\', \'Q16931679\', \'Q119137625\'], \'P156\': [\'Q6106068\'], \'P17\': [\'Q17167\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 14: Q6106068 (Middle Roman Republic)
MERGE (n:Entity {qid: 'Q6106068'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q6106068',
  n.entity_id = 'subjectconcept_q6106068',
  n.label = 'Middle Roman Republic',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P31\': [\'Q11514315\'], \'P361\': [\'Q17167\'], \'P155\': [\'Q2839628\'], \'P156\': [\'Q2815472\'], \'P17\': [\'Q17167\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 15: Q2815472 (Late Roman Republic)
MERGE (n:Entity {qid: 'Q2815472'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q2815472',
  n.entity_id = 'subjectconcept_q2815472',
  n.label = 'Late Roman Republic',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 10,
  n.property_summary = '{\'P31\': [\'Q11514315\'], \'P361\': [\'Q17167\'], \'P155\': [\'Q6106068\'], \'P156\': [\'Q787204\'], \'P17\': [\'Q17167\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 16: Q2277 (Roman Empire)
MERGE (n:Entity {qid: 'Q2277'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q2277',
  n.entity_id = 'subjectconcept_q2277',
  n.label = 'Roman Empire',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 102,
  n.property_summary = '{\'P36\': [\'Q220\', \'Q16869\', \'Q13364\', \'Q490\', \'Q18287233\'], \'P37\': [\'Q397\', \'Q35497\'], \'P122\': [\'Q173424\', \'Q7269\', \'Q174450\', \'Q83204\', \'Q184558\'], \'P38\': [\'Q208041\', \'Q187776\', \'Q952064\', \'Q476078\', \'Q376895\'], \'P910\': [\'Q1456601\'], \'P140\': [\'Q337547\', \'Q7603670\'], \'P194\': [\'Q3510883\'], \'P31\': [\'Q48349\', \'Q11514315\', \'Q3024240\'], \'P2184\': [\'Q2671119\'], \'P1906\': [\'Q842606\'], \'P2959\': [\'Q21201536\'], \'P530\': [\'Q7209\', \'Q62646\', \'Q302980\'], \'P1792\': [\'Q8678282\'], \'P1464\': [\'Q32642796\'], \'P1465\': [\'Q42859641\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P47\': [\'Q1986139\'], \'P150\': [\'Q692775\', \'Q3626028\', \'Q1156891\', \'Q747040\', \'Q186513\'], \'P237\': [\'Q264655\', \'Q163323\'], \'P3075\': [\'Q337547\', \'Q5043\', \'Q29536\', \'Q83922\'], \'P1151\': [\'Q42353313\'], \'P1366\': [\'Q42834\', \'Q12544\'], \'P1365\': [\'Q17167\'], \'P1343\': [\'Q19180675\', \'Q3181656\', \'Q1154753\', \'Q16082057\', \'Q602358\'], \'P7867\': [\'Q8607609\'], \'P1889\': [\'Q178897\'], \'P30\': [\'Q46\', \'Q15\', \'Q48\', \'Q27527\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 17: Q206414 (Principate)
MERGE (n:Entity {qid: 'Q206414'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q206414',
  n.entity_id = 'subjectconcept_q206414',
  n.label = 'Principate',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 24,
  n.property_summary = '{\'P1343\': [\'Q602358\', \'Q4532138\', \'Q124737636\'], \'P31\': [\'Q1307214\', \'Q11514315\'], \'P2596\': [\'Q1747689\'], \'P17\': [\'Q2277\'], \'P361\': [\'Q14618893\', \'Q105747718\'], \'P156\': [\'Q238399\'], \'P1889\': [\'Q787204\'], \'P1365\': [\'Q17167\'], \'P155\': [\'Q17167\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 18: Q201038 (Roman Kingdom)
MERGE (n:Entity {qid: 'Q201038'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q201038',
  n.entity_id = 'subjectconcept_q201038',
  n.label = 'Roman Kingdom',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 38,
  n.property_summary = '{\'P910\': [\'Q8678306\'], \'P31\': [\'Q11514315\', \'Q3024240\'], \'P156\': [\'Q17167\'], \'P155\': [\'Q2566630\'], \'P361\': [\'Q41493\'], \'P279\': [\'Q830852\'], \'P276\': [\'Q1048669\'], \'P1889\': [\'Q326197\'], \'P527\': [\'Q3921629\', \'Q119137625\'], \'P122\': [\'Q584683\'], \'P140\': [\'Q337547\'], \'P194\': [\'Q287980\', \'Q3510884\'], \'P37\': [\'Q397\'], \'P36\': [\'Q220\', \'Q18287233\'], \'P2936\': [\'Q397\', \'Q12289\'], \'P1906\': [\'Q55375123\'], \'P30\': [\'Q5401\', \'Q46\'], \'P1365\': [\'Q5171759\'], \'P1366\': [\'Q17167\'], \'P5008\': [\'Q6173448\'], \'P3075\': [\'Q337547\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 19: Q220 (Rome)
MERGE (n:Entity {qid: 'Q220'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q220',
  n.entity_id = 'place_q220',
  n.label = 'Rome',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 5,
  n.properties_count = 262,
  n.property_summary = '{\'P1151\': [\'Q11381903\'], \'P5125\': [\'Q48740750\'], \'P1792\': [\'Q10142763\'], \'P1313\': [\'Q23936560\'], \'P417\': [\'Q33923\', \'Q9200\'], \'P2959\': [\'Q22665612\'], \'P1376\': [\'Q18288160\', \'Q38\', \'Q1282\', \'Q15119\', \'Q170174\'], \'P194\': [\'Q48617968\'], \'P131\': [\'Q15119\', \'Q170174\', \'Q1558632\', \'Q1747689\', \'Q17167\'], \'P2596\': [\'Q1200427\', \'Q103122\', \'Q3678788\', \'Q22907236\'], \'P206\': [\'Q13712\', \'Q546600\', \'Q38882\'], \'P17\': [\'Q38\', \'Q170174\', \'Q3755547\', \'Q583038\', \'Q12544\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P190\': [\'Q90\', \'Q31487\', \'Q34647\', \'Q43196\', \'Q132830\'], \'P910\': [\'Q8682052\'], \'P1791\': [\'Q7977790\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 20: Q397 (Latin)
MERGE (n:Entity {qid: 'Q397'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q397',
  n.entity_id = 'concept_q397',
  n.label = 'Latin',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 132,
  n.property_summary = '{\'P910\': [\'Q7142639\'], \'P4132\': [\'Q539808\', \'Q318917\', \'Q661936\', \'Q48612\', \'Q178435\'], \'P1018\': [\'Q48509\'], \'P5109\': [\'Q1775415\', \'Q499327\', \'Q1775461\'], \'P2959\': [\'Q12715487\'], \'P2579\': [\'Q1806979\', \'Q841090\', \'Q108000026\'], \'P31\': [\'Q45762\', \'Q436240\', \'Q34770\', \'Q839470\'], \'P5206\': [\'Q3921589\', \'Q3953978\', \'Q4009868\', \'Q19819479\'], \'P282\': [\'Q8229\', \'Q41670\'], \'P3103\': [\'Q623742\', \'Q192613\', \'Q12547192\', \'Q501405\', \'Q1234617\'], \'P279\': [\'Q33478\', \'Q85380120\'], \'P2989\': [\'Q131105\', \'Q185077\', \'Q146078\', \'Q146233\', \'Q145599\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P1343\': [\'Q19180675\', \'Q602358\', \'Q106727050\', \'Q20078554\', \'Q867541\'], \'P3823\': [\'Q61954942\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 21: Q35497 (Ancient Greek)
MERGE (n:Entity {qid: 'Q35497'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q35497',
  n.entity_id = 'concept_q35497',
  n.label = 'Ancient Greek',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 70,
  n.property_summary = '{\'P282\': [\'Q8216\', \'Q190102\'], \'P31\': [\'Q34770\', \'Q2315359\'], \'P279\': [\'Q2042538\'], \'P910\': [\'Q8250729\'], \'P527\': [\'Q11732220\', \'Q11871956\', \'Q107358\', \'Q78612105\'], \'P1365\': [\'Q668366\'], \'P1366\': [\'Q36387\'], \'P3103\': [\'Q623742\', \'Q216497\', \'Q192613\'], \'P2579\': [\'Q16267481\', \'Q841090\', \'Q495527\'], \'P3161\': [\'Q682111\', \'Q473746\', \'Q22716\', \'Q527205\'], \'P2341\': [\'Q11772\', \'Q155552\'], \'P4132\': [\'Q651641\', \'Q178435\', \'Q318917\'], \'P1343\': [\'Q602358\', \'Q19180675\', \'Q19219752\', \'Q867541\'], \'P156\': [\'Q36510\', \'Q220607\', \'Q107358\'], \'P5109\': [\'Q499327\', \'Q1775415\', \'Q1775461\'], \'P1889\': [\'Q107358\'], \'P3823\': [\'Q61954942\'], \'P7084\': [\'Q84971021\'], \'P155\': [\'Q668366\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 22: Q46 (Europe)
MERGE (n:Entity {qid: 'Q46'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q46',
  n.entity_id = 'concept_q46',
  n.label = 'Europe',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 228,
  n.property_summary = '{\'P1151\': [\'Q4997598\'], \'P5125\': [\'Q7112259\'], \'P2633\': [\'Q119716\'], \'P2959\': [\'Q20820598\'], \'P1424\': [\'Q6984392\', \'Q17588291\', \'Q6328695\', \'Q10902188\'], \'P421\': [\'Q5412093\', \'Q5412099\', \'Q16894228\', \'Q2356448\', \'Q5412117\'], \'P2184\': [\'Q7787\'], \'P910\': [\'Q4587662\'], \'P1791\': [\'Q18915272\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 23: Q48 (Asia)
MERGE (n:Entity {qid: 'Q48'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q48',
  n.entity_id = 'concept_q48',
  n.label = 'Asia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 5,
  n.properties_count = 213,
  n.property_summary = '{\'P1151\': [\'Q8252068\'], \'P1740\': [\'Q7140349\'], \'P910\': [\'Q5610083\'], \'P5125\': [\'Q7112190\'], \'P1791\': [\'Q23657023\'], \'P2633\': [\'Q2001617\'], \'P706\': [\'Q186198\'], \'P527\': [\'Q27231\', \'Q11708\', \'Q27275\', \'Q771405\', \'Q7204\'], \'P1465\': [\'Q7071117\'], \'P2959\': [\'Q22828169\', \'Q137645156\'], \'P361\': [\'Q2\', \'Q5401\', \'Q27527\', \'Q2035462\', \'Q125965270\'], \'P47\': [\'Q46\', \'Q15\'], \'P31\': [\'Q5107\', \'Q2418896\', \'Q82794\'], \'P1464\': [\'Q8042599\'], \'P421\': [\'Q3297477\', \'Q3522509\', \'Q3543509\', \'Q385504\', \'Q4127120\'], \'P2184\': [\'Q627531\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 24: Q15 (Africa)
MERGE (n:Entity {qid: 'Q15'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q15',
  n.entity_id = 'concept_q15',
  n.label = 'Africa',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 254,
  n.property_summary = '{\'P1151\': [\'Q7486129\'], \'P1740\': [\'Q7140863\'], \'P910\': [\'Q5460710\', \'Q32816044\'], \'P5125\': [\'Q7112174\'], \'P2633\': [\'Q781650\'], \'P1830\': [\'Q1666473\'], \'P706\': [\'Q39061\', \'Q41228\'], \'P1464\': [\'Q8044365\'], \'P1465\': [\'Q9682611\'], \'P2959\': [\'Q22828260\'], \'P361\': [\'Q2035462\', \'Q2\', \'Q27527\', \'Q125965270\'], \'P47\': [\'Q5401\', \'Q48\'], \'P31\': [\'Q5107\', \'Q2221906\', \'Q82794\'], \'P610\': [\'Q1394606\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 25: Q666680 (aristocratic republic)
MERGE (n:Entity {qid: 'Q666680'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q666680',
  n.entity_id = 'concept_q666680',
  n.label = 'aristocratic republic',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P279\': [\'Q7270\', \'Q123432\'], \'P31\': [\'Q1307214\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 26: Q1747689 (Ancient Rome)
MERGE (n:Entity {qid: 'Q1747689'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1747689',
  n.entity_id = 'concept_q1747689',
  n.label = 'Ancient Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 114,
  n.property_summary = '{\'P527\': [\'Q201038\', \'Q17167\', \'Q2277\', \'Q12544\'], \'P832\': [\'Q207213\'], \'P910\': [\'Q7098243\'], \'P1151\': [\'Q10631465\'], \'P2184\': [\'Q830852\'], \'P1792\': [\'Q5652564\'], \'P2348\': [\'Q486761\'], \'P47\': [\'Q83311\', \'Q807748\', \'Q2528503\'], \'P5125\': [\'Q1216140\'], \'P706\': [\'Q72499\'], \'P6104\': [\'Q6337458\'], \'P2579\': [\'Q435608\'], \'P36\': [\'Q18287233\'], \'P30\': [\'Q46\', \'Q15\', \'Q48\', \'Q27527\'], \'P1343\': [\'Q4532138\', \'Q19219752\', \'Q135617903\'], \'P8744\': [\'Q15265460\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 27: Q346629 (Roman Republic)
MERGE (n:Entity {qid: 'Q346629'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q346629',
  n.entity_id = 'concept_q346629',
  n.label = 'Roman Republic',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P31\': [\'Q4167410\'], \'P1889\': [\'Q17167\', \'Q175881\', \'Q1072140\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 28: Q6173448 (Wikipedia:Vital articles/Level/4)
MERGE (n:Entity {qid: 'Q6173448'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6173448',
  n.entity_id = 'concept_q6173448',
  n.label = 'Wikipedia:Vital articles/Level/4',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 7,
  n.property_summary = '{\'P31\': [\'Q14204246\', \'Q51539995\'], \'P527\': [\'Q6173639\', \'Q12153864\', \'Q6173773\', \'Q12154424\', \'Q12154377\'], \'P361\': [\'Q43375360\'], \'P144\': [\'Q43375360\'], \'P910\': [\'Q8925636\'], \'P360\': [\'Q116974583\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 29: Q124988 (Punic Wars)
MERGE (n:Entity {qid: 'Q124988'})
ON CREATE SET
  n.entity_cipher = 'ent_evt_Q124988',
  n.entity_id = 'event_q124988',
  n.label = 'Punic Wars',
  n.entity_type = 'EVENT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 44,
  n.property_summary = '{\'P527\': [\'Q6286\', \'Q6271\', \'Q6334\'], \'P910\': [\'Q7155263\'], \'P1343\': [\'Q2657718\', \'Q30059240\', \'Q602358\', \'Q19180675\', \'Q2041543\'], \'P710\': [\'Q17167\', \'Q2429397\'], \'P31\': [\'Q104212151\', \'Q198\'], \'P5008\': [\'Q6173448\'], \'P1424\': [\'Q6418868\'], \'P276\': [\'Q17167\', \'Q2429397\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 30: Q3778726 (Sertorian War)
MERGE (n:Entity {qid: 'Q3778726'})
ON CREATE SET
  n.entity_cipher = 'ent_evt_Q3778726',
  n.entity_id = 'event_q3778726',
  n.label = 'Sertorian War',
  n.entity_type = 'EVENT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 12,
  n.property_summary = '{\'P910\': [\'Q24195900\'], \'P31\': [\'Q8465\'], \'P361\': [\'Q3395322\'], \'P276\': [\'Q186513\'], \'P138\': [\'Q296238\'], \'P17\': [\'Q17167\'], \'P710\': [\'Q271108\', \'Q309155\', \'Q190992\', \'Q5011445\', \'Q1741306\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 31: Q75813 (Macedonian Wars)
MERGE (n:Entity {qid: 'Q75813'})
ON CREATE SET
  n.entity_cipher = 'ent_evt_Q75813',
  n.entity_id = 'event_q75813',
  n.label = 'Macedonian Wars',
  n.entity_type = 'EVENT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 16,
  n.property_summary = '{\'P527\': [\'Q75626\', \'Q75665\', \'Q76118\', \'Q552373\'], \'P910\': [\'Q8592033\'], \'P31\': [\'Q104212151\'], \'P1343\': [\'Q4114391\', \'Q602358\'], \'P276\': [\'Q83958\'], \'P710\': [\'Q1747689\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 32: Q202161 (Gallic War)
MERGE (n:Entity {qid: 'Q202161'})
ON CREATE SET
  n.entity_cipher = 'ent_evt_Q202161',
  n.entity_id = 'event_q202161',
  n.label = 'Gallic War',
  n.entity_type = 'EVENT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 36,
  n.property_summary = '{\'P31\': [\'Q198\'], \'P910\': [\'Q6255896\'], \'P793\': [\'Q1628304\', \'Q1274566\', \'Q2984753\', \'Q635028\', \'Q1267513\'], \'P276\': [\'Q38060\'], \'P1343\': [\'Q4114391\', \'Q106199\', \'Q20078554\'], \'P710\': [\'Q1747689\', \'Q273854\', \'Q22633\', \'Q849967\', \'Q1255605\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 33: Q596373 (Pyrrhic War)
MERGE (n:Entity {qid: 'Q596373'})
ON CREATE SET
  n.entity_cipher = 'ent_evt_Q596373',
  n.entity_id = 'event_q596373',
  n.label = 'Pyrrhic War',
  n.entity_type = 'EVENT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 19,
  n.property_summary = '{\'P910\': [\'Q8808774\'], \'P31\': [\'Q104212151\', \'Q198\'], \'P710\': [\'Q1747689\', \'Q1265446\', \'Q1165749\', \'Q941821\', \'Q2479252\'], \'P276\': [\'Q913582\'], \'P460\': [\'Q19716429\'], \'P2348\': [\'Q2839628\'], \'P527\': [\'Q129059100\', \'Q5742664\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 34: Q1238338 (Caesar\'s Civil War)
MERGE (n:Entity {qid: 'Q1238338'})
ON CREATE SET
  n.entity_cipher = 'ent_evt_Q1238338',
  n.entity_id = 'event_q1238338',
  n.label = 'Caesar\\\'s Civil War',
  n.entity_type = 'EVENT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 22,
  n.property_summary = '{\'P31\': [\'Q8465\'], \'P1343\': [\'Q4114391\', \'Q4114391\', \'Q4114391\', \'Q19180675\', \'Q123560817\'], \'P527\': [\'Q516760\', \'Q849653\', \'Q203681\', \'Q28531438\', \'Q525325\'], \'P910\': [\'Q9811318\'], \'P276\': [\'Q186513\', \'Q23522\', \'Q15\', \'Q32047\', \'Q202311\'], \'P361\': [\'Q1747183\'], \'P7867\': [\'Q84061055\'], \'P828\': [\'Q25238182\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 35: Q677316 (Social War of 91-87 BCE)
MERGE (n:Entity {qid: 'Q677316'})
ON CREATE SET
  n.entity_cipher = 'ent_evt_Q677316',
  n.entity_id = 'event_q677316',
  n.label = 'Social War of 91-87 BCE',
  n.entity_type = 'EVENT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 31,
  n.property_summary = '{\'P31\': [\'Q198\'], \'P1343\': [\'Q30059240\', \'Q19180675\', \'Q602358\', \'Q3181656\', \'Q124737616\'], \'P710\': [\'Q1747689\', \'Q1265446\', \'Q941821\', \'Q2341546\', \'Q1165749\'], \'P276\': [\'Q38\'], \'P910\': [\'Q32380558\'], \'P17\': [\'Q38\'], \'P527\': [\'Q85745805\', \'Q85745822\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 36: Q6428674 (era)
MERGE (n:Entity {qid: 'Q6428674'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6428674',
  n.entity_id = 'concept_q6428674',
  n.label = 'era',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 26,
  n.property_summary = '{\'P279\': [\'Q186081\'], \'P460\': [\'Q17522177\'], \'P910\': [\'Q7779952\'], \'P2579\': [\'Q1066186\', \'Q1069\', \'Q420\'], \'P1269\': [\'Q1190554\'], \'P1687\': [\'P2348\'], \'P1343\': [\'Q63284758\', \'Q19219752\'], \'P1889\': [\'Q30287\', \'Q630830\', \'Q4375074\', \'Q61068956\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 37: Q17004260 (list of time periods)
MERGE (n:Entity {qid: 'Q17004260'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q17004260',
  n.entity_id = 'concept_q17004260',
  n.label = 'list of time periods',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P31\': [\'Q13406463\'], \'P360\': [\'Q11514315\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 38: Q816829 (periodization)
MERGE (n:Entity {qid: 'Q816829'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q816829',
  n.entity_id = 'concept_q816829',
  n.label = 'periodization',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 30,
  n.property_summary = '{\'P361\': [\'Q1066186\'], \'P1343\': [\'Q3181656\', \'Q4532138\', \'Q61070632\'], \'P279\': [\'Q13582682\', \'Q97359583\'], \'P1889\': [\'Q11514315\'], \'P31\': [\'Q1047113\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 39: Q183039 (form of state)
MERGE (n:Entity {qid: 'Q183039'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q183039',
  n.entity_id = 'concept_q183039',
  n.label = 'form of state',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 12,
  n.property_summary = '{\'P910\': [\'Q9763182\'], \'P279\': [\'Q28108\'], \'P1889\': [\'Q1307214\', \'Q19944802\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 40: Q2752458 (administrative type)
MERGE (n:Entity {qid: 'Q2752458'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q2752458',
  n.entity_id = 'concept_q2752458',
  n.label = 'administrative type',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 5,
  n.property_summary = '{\'P5008\': [\'Q68235346\'], \'P31\': [\'Q2712963\', \'Q5962346\'], \'P279\': [\'Q96247293\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 41: Q28108 (political system)
MERGE (n:Entity {qid: 'Q28108'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q28108',
  n.entity_id = 'concept_q28108',
  n.label = 'political system',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 39,
  n.property_summary = '{\'P910\': [\'Q7238098\', \'Q9858415\'], \'P279\': [\'Q1639378\'], \'P1269\': [\'Q7163\'], \'P527\': [\'Q1307214\', \'Q273005\', \'Q211606\', \'Q5193417\', \'Q2478386\'], \'P1889\': [\'Q1307214\'], \'P1382\': [\'Q20076236\'], \'P2579\': [\'Q745692\', \'Q32492\'], \'P31\': [\'Q96116695\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 42: Q54069 (Category:Forms of government)
MERGE (n:Entity {qid: 'Q54069'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q54069',
  n.entity_id = 'concept_q54069',
  n.label = 'Category:Forms of government',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P301\': [\'Q1307214\'], \'P4329\': [\'Q6526407\', \'Q15838730\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 43: Q5589178 (regime)
MERGE (n:Entity {qid: 'Q5589178'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q5589178',
  n.entity_id = 'concept_q5589178',
  n.label = 'regime',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 12,
  n.property_summary = '{\'P361\': [\'Q36442\'], \'P279\': [\'Q28108\', \'Q183039\'], \'P910\': [\'Q7957175\'], \'P1889\': [\'Q1307214\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 44: Q19944802 (government structure)
MERGE (n:Entity {qid: 'Q19944802'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q19944802',
  n.entity_id = 'concept_q19944802',
  n.label = 'government structure',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P910\': [\'Q9098906\'], \'P279\': [\'Q183039\', \'Q759524\', \'Q7225121\'], \'P1889\': [\'Q1307214\', \'Q183039\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 45: Q20076236 (state system)
MERGE (n:Entity {qid: 'Q20076236'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q20076236',
  n.entity_id = 'concept_q20076236',
  n.label = 'state system',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P1269\': [\'Q1331392\'], \'P1382\': [\'Q28108\'], \'P31\': [\'Q5962346\'], \'P279\': [\'Q28108\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 46: Q759524 (organizational structure)
MERGE (n:Entity {qid: 'Q759524'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q759524',
  n.entity_id = 'concept_q759524',
  n.label = 'organizational structure',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 24,
  n.property_summary = '{\'P910\': [\'Q8704186\'], \'P1269\': [\'Q43229\'], \'P279\': [\'Q6671777\', \'Q211606\'], \'P2579\': [\'Q2029930\'], \'P31\': [\'Q111972893\'], \'P1889\': [\'Q130751825\'], \'P13044\': [\'Q43229\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 47: Q31728 (public administration)
MERGE (n:Entity {qid: 'Q31728'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q31728',
  n.entity_id = 'concept_q31728',
  n.label = 'public administration',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 60,
  n.property_summary = '{\'P910\': [\'Q5726315\'], \'P361\': [\'Q7275\', \'Q1200977\'], \'P1343\': [\'Q2041543\', \'Q3181656\', \'Q1029706\'], \'P279\': [\'Q11771944\'], \'P527\': [\'Q294414\', \'Q3754526\', \'Q699386\', \'Q12056862\', \'Q1519782\'], \'P31\': [\'Q11862829\'], \'P2579\': [\'Q2736989\', \'Q125461740\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 48: Q6526407 (Template:Basic forms of government)
MERGE (n:Entity {qid: 'Q6526407'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6526407',
  n.entity_id = 'concept_q6526407',
  n.label = 'Template:Basic forms of government',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q11753321\'], \'P1423\': [\'Q1307214\'], \'P9926\': [\'Q54069\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 49: Q25728256 (Template:Forms of government footer)
MERGE (n:Entity {qid: 'Q25728256'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q25728256',
  n.entity_id = 'concept_q25728256',
  n.label = 'Template:Forms of government footer',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P31\': [\'Q11266439\'], \'P1423\': [\'Q1307214\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 50: Q6135095 (Category:Empires)
MERGE (n:Entity {qid: 'Q6135095'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6135095',
  n.entity_id = 'concept_q6135095',
  n.label = 'Category:Empires',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 5,
  n.property_summary = '{\'P301\': [\'Q48349\'], \'P31\': [\'Q4167836\'], \'P1753\': [\'Q1151047\'], \'P4329\': [\'Q7477250\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 51: Q2041543 (Otto\'s encyclopedia)
MERGE (n:Entity {qid: 'Q2041543'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q2041543',
  n.entity_id = 'concept_q2041543',
  n.label = 'Otto\\\'s encyclopedia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 22,
  n.property_summary = '{\'P767\': [\'Q10282226\', \'Q10379548\', \'Q1040777\', \'Q10546686\', \'Q10710174\'], \'P407\': [\'Q9056\'], \'P31\': [\'Q3331189\'], \'P910\': [\'Q16956809\'], \'P527\': [\'Q23857524\', \'Q23857527\', \'Q23857636\', \'Q23870362\', \'Q23857530\'], \'P123\': [\'Q28840617\'], \'P50\': [\'Q1690980\'], \'P136\': [\'Q5292\'], \'P629\': [\'Q59393688\'], \'P291\': [\'Q1085\'], \'P495\': [\'Q28513\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 52: Q20078554 (Great Soviet Encyclopedia (1926–1947))
MERGE (n:Entity {qid: 'Q20078554'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q20078554',
  n.entity_id = 'concept_q20078554',
  n.label = 'Great Soviet Encyclopedia (1926–1947)',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 15,
  n.property_summary = '{\'P407\': [\'Q7737\'], \'P629\': [\'Q234535\'], \'P31\': [\'Q3331189\'], \'P291\': [\'Q649\'], \'P98\': [\'Q167997\'], \'P123\': [\'Q5061737\'], \'P527\': [\'Q43200213\', \'Q43200216\', \'Q43200221\', \'Q43200225\', \'Q43200228\'], \'P747\': [\'Q28841889\', \'Q28841897\'], \'P7937\': [\'Q5292\'], \'P1424\': [\'Q51844735\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 53: Q20096917 (Encyclopædia Britannica Ninth Edition)
MERGE (n:Entity {qid: 'Q20096917'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q20096917',
  n.entity_id = 'concept_q20096917',
  n.label = 'Encyclopædia Britannica Ninth Edition',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 10,
  n.property_summary = '{\'P31\': [\'Q3331189\'], \'P629\': [\'Q455\'], \'P6216\': [\'Q19652\'], \'P155\': [\'Q84237483\'], \'P156\': [\'Q84246840\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 54: Q602358 (Brockhaus and Efron Encyclopedic Dictionary)
MERGE (n:Entity {qid: 'Q602358'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q602358',
  n.entity_id = 'concept_q602358',
  n.label = 'Brockhaus and Efron Encyclopedic Dictionary',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 27,
  n.property_summary = '{\'P136\': [\'Q5292\', \'Q975413\'], \'P910\': [\'Q7071113\'], \'P123\': [\'Q19908137\'], \'P407\': [\'Q7737\'], \'P98\': [\'Q4065721\', \'Q1782723\', \'Q4361720\'], \'P291\': [\'Q656\'], \'P1424\': [\'Q14347088\'], \'P495\': [\'Q34266\', \'Q159\'], \'P144\': [\'Q4207256\', \'Q1138512\'], \'P6216\': [\'Q19652\', \'Q19652\'], \'P527\': [\'Q23892884\', \'Q23892888\', \'Q23892889\', \'Q23892890\', \'Q23892896\'], \'P31\': [\'Q3331189\'], \'P50\': [\'Q1690980\', \'Q4054981\', \'Q4056733\', \'Q24009771\', \'Q4057471\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 55: Q19180675 (Small Brockhaus and Efron Encyclopedic Dictionary)
MERGE (n:Entity {qid: 'Q19180675'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q19180675',
  n.entity_id = 'concept_q19180675',
  n.label = 'Small Brockhaus and Efron Encyclopedic Dictionary',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 11,
  n.property_summary = '{\'P31\': [\'Q47461344\'], \'P136\': [\'Q975413\'], \'P407\': [\'Q7737\'], \'P6216\': [\'Q19652\'], \'P747\': [\'Q24717970\'], \'P495\': [\'Q34266\'], \'P123\': [\'Q19908137\'], \'P910\': [\'Q117360567\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 56: Q4532138 (Granat Encyclopedic Dictionary)
MERGE (n:Entity {qid: 'Q4532138'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q4532138',
  n.entity_id = 'concept_q4532138',
  n.label = 'Granat Encyclopedic Dictionary',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 18,
  n.property_summary = '{\'P31\': [\'Q975413\', \'Q3331189\'], \'P136\': [\'Q975413\'], \'P495\': [\'Q34266\', \'Q15180\'], \'P123\': [\'Q4147766\'], \'P910\': [\'Q28870151\'], \'P407\': [\'Q7737\'], \'P6216\': [\'Q19652\'], \'P144\': [\'Q63284758\'], \'P629\': [\'Q63284758\'], \'P138\': [\'Q4147766\', \'Q4147768\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 57: Q356252 (Imperia)
MERGE (n:Entity {qid: 'Q356252'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q356252',
  n.entity_id = 'concept_q356252',
  n.label = 'Imperia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 1,
  n.property_summary = '{\'P31\': [\'Q4167410\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 58: Q3624078 (sovereign state)
MERGE (n:Entity {qid: 'Q3624078'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3624078',
  n.entity_id = 'concept_q3624078',
  n.label = 'sovereign state',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 24,
  n.property_summary = '{\'P279\': [\'Q7275\', \'Q6256\'], \'P460\': [\'Q3591847\', \'Q6726158\'], \'P461\': [\'Q1151405\'], \'P2354\': [\'Q11750\'], \'P910\': [\'Q7160365\'], \'P1889\': [\'Q2324272\', \'Q7275\'], \'P5008\': [\'Q6173448\'], \'P138\': [\'Q42008\', \'Q7275\'], \'P1687\': [\'P17\'], \'P1343\': [\'Q867541\'], \'P12861\': [\'E32\'], \'P527\': [\'Q7275\', \'Q2472587\'], \'P5869\': [\'Q142\', \'Q212\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 59: Q7269 (monarchy)
MERGE (n:Entity {qid: 'Q7269'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q7269',
  n.entity_id = 'concept_q7269',
  n.label = 'monarchy',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 76,
  n.property_summary = '{\'P910\': [\'Q54068\'], \'P31\': [\'Q1307214\'], \'P527\': [\'Q116\'], \'P279\': [\'Q22676587\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P2354\': [\'Q3446184\'], \'P1151\': [\'Q8209976\'], \'P1343\': [\'Q602358\', \'Q867541\', \'Q20078554\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 60: Q96196009 (former or current state)
MERGE (n:Entity {qid: 'Q96196009'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q96196009',
  n.entity_id = 'concept_q96196009',
  n.label = 'former or current state',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P279\': [\'Q1063239\'], \'P2238\': [\'Q461585\'], \'P31\': [\'Q15617994\'], \'P2738\': [\'Q23766486\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 61: Q19832712 (historical administrative division)
MERGE (n:Entity {qid: 'Q19832712'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q19832712',
  n.entity_id = 'concept_q19832712',
  n.label = 'historical administrative division',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P279\': [\'Q56061\', \'Q1620908\'], \'P460\': [\'Q19953632\'], \'P1889\': [\'Q28864185\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 62: Q6256 (country)
MERGE (n:Entity {qid: 'Q6256'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6256',
  n.entity_id = 'concept_q6256',
  n.label = 'country',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 68,
  n.property_summary = '{\'P1151\': [\'Q6988967\'], \'P460\': [\'Q7275\'], \'P279\': [\'Q4835091\', \'Q1048835\'], \'P910\': [\'Q4026570\', \'Q9699162\'], \'P1687\': [\'P17\', \'P495\', \'P27\', \'P1532\'], \'P1963\': [\'P17\', \'P30\', \'P150\', \'P35\', \'P36\'], \'P150\': [\'Q10864048\'], \'P2959\': [\'Q22828881\'], \'P1424\': [\'Q5621162\', \'Q5047\'], \'P1889\': [\'Q231002\', \'Q7275\', \'Q7188\'], \'P527\': [\'Q183366\'], \'P5869\': [\'Q183\'], \'P6186\': [\'Q5641433\'], \'P6104\': [\'Q8503406\'], \'P2670\': [\'Q1020994\'], \'P31\': [\'Q15617994\', \'Q24229398\'], \'P5008\': [\'Q6173448\'], \'P2737\': [\'Q23766486\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 63: Q7238252 (Category:Former countries)
MERGE (n:Entity {qid: 'Q7238252'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q7238252',
  n.entity_id = 'concept_q7238252',
  n.label = 'Category:Former countries',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P301\': [\'Q3024240\'], \'P31\': [\'Q4167836\'], \'P1753\': [\'Q62630\'], \'P971\': [\'Q29933798\', \'Q15893266\'], \'P1889\': [\'Q115743962\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 64: Q6036853 (Template:Infobox former country)
MERGE (n:Entity {qid: 'Q6036853'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6036853',
  n.entity_id = 'concept_q6036853',
  n.label = 'Template:Infobox former country',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P31\': [\'Q19887878\'], \'P2959\': [\'Q25721295\'], \'P1423\': [\'Q3024240\'], \'P279\': [\'Q5621162\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 65: Q3591867 (proposed country)
MERGE (n:Entity {qid: 'Q3591867'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3591867',
  n.entity_id = 'concept_q3591867',
  n.label = 'proposed country',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P910\': [\'Q8797905\'], \'P279\': [\'Q6256\', \'Q28864185\'], \'P1889\': [\'Q1145276\', \'Q3024240\', \'Q77172450\'], \'P828\': [\'Q112074700\', \'Q1464916\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 66: Q62630 (list of former sovereign states)
MERGE (n:Entity {qid: 'Q62630'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q62630',
  n.entity_id = 'concept_q62630',
  n.label = 'list of former sovereign states',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P360\': [\'Q3024240\'], \'P31\': [\'Q13406463\'], \'P1754\': [\'Q7238252\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 67: Q4167836 (Wikimedia category)
MERGE (n:Entity {qid: 'Q4167836'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q4167836',
  n.entity_id = 'concept_q4167836',
  n.label = 'Wikimedia category',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 12,
  n.property_summary = '{\'P279\': [\'Q12139612\', \'Q17442446\', \'Q118555179\'], \'P31\': [\'Q56005592\', \'Q4656150\'], \'P910\': [\'Q2944534\', \'Q10013748\'], \'P1889\': [\'Q224414\', \'Q4989342\', \'Q42104522\', \'Q64549097\', \'Q15647814\'], \'P6104\': [\'Q4391019\'], \'P5869\': [\'Q1458083\', \'Q6377645\'], \'P1424\': [\'Q24817459\', \'Q30511862\', \'Q6439308\', \'Q7639029\'], \'P361\': [\'Q118559258\'], \'P1963\': [\'P31\', \'P301\', \'P4329\', \'P971\', \'P4224\'], \'P1687\': [\'P910\', \'P301\', \'P4329\', \'P971\', \'P4224\'], \'P12861\': [\'E315\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 68: Q5 (human)
MERGE (n:Entity {qid: 'Q5'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q5',
  n.entity_id = 'concept_q5',
  n.label = 'human',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 111,
  n.property_summary = '{\'P527\': [\'Q23852\'], \'P1552\': [\'Q1071027\', \'Q185836\', \'Q48277\', \'Q238372\', \'Q1314553\'], \'P361\': [\'Q8425\', \'Q1156970\', \'Q42762\', \'Q16334295\'], \'P1424\': [\'Q6249834\', \'Q20829728\', \'Q17534637\'], \'P910\': [\'Q6697530\'], \'P1343\': [\'Q4173137\', \'Q4086271\', \'Q4532138\', \'Q302556\', \'Q602358\'], \'P1963\': [\'P21\', \'P569\', \'P570\', \'P735\', \'P734\'], \'P2579\': [\'Q23404\', \'Q720858\'], \'P2283\': [\'Q8205328\', \'Q39546\', \'Q315\'], \'P460\': [\'Q15978631\'], \'P4733\': [\'Q7390\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P1889\': [\'Q2472587\', \'Q95074\', \'Q215627\', \'Q114353657\', \'Q124542004\'], \'P5869\': [\'Q42\', \'Q7186\', \'Q762\', \'Q7226\', \'Q37151\'], \'P279\': [\'Q110551885\', \'Q215627\', \'Q26401003\', \'Q164509\', \'Q154954\'], \'P1542\': [\'Q16686448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 69: Q8678306 (Category:Roman Kingdom)
MERGE (n:Entity {qid: 'Q8678306'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8678306',
  n.entity_id = 'concept_q8678306',
  n.label = 'Category:Roman Kingdom',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P301\': [\'Q201038\'], \'P156\': [\'Q6944405\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 70: Q8251375 (Category:Ancient Roman religion)
MERGE (n:Entity {qid: 'Q8251375'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8251375',
  n.entity_id = 'concept_q8251375',
  n.label = 'Category:Ancient Roman religion',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P301\': [\'Q337547\'], \'P31\': [\'Q4167836\'], \'P971\': [\'Q9174\', \'Q1747689\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 71: Q30059240 (Russian translation of Lübker\'s Antiquity Lexicon)
MERGE (n:Entity {qid: 'Q30059240'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q30059240',
  n.entity_id = 'concept_q30059240',
  n.label = 'Russian translation of Lübker\\\'s Antiquity Lexicon',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 15,
  n.property_summary = '{\'P31\': [\'Q3331189\', \'Q2134855\'], \'P629\': [\'Q30067878\', \'Q4391526\'], \'P407\': [\'Q7737\'], \'P291\': [\'Q656\'], \'P123\': [\'Q24933120\'], \'P50\': [\'Q101490\'], \'P655\': [\'Q4106039\', \'Q1459210\', \'Q4135794\', \'Q60829448\', \'Q45319014\'], \'P98\': [\'Q694826\', \'Q4135787\', \'Q4249594\', \'Q1459210\', \'Q4319762\'], \'P747\': [\'Q30067970\'], \'P6216\': [\'Q19652\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 72: Q107013262 (religious policies of the Roman Empire)
MERGE (n:Entity {qid: 'Q107013262'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q107013262',
  n.entity_id = 'concept_q107013262',
  n.label = 'religious policies of the Roman Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P31\': [\'Q17524420\'], \'P279\': [\'Q107013288\'], \'P361\': [\'Q107013169\'], \'P1001\': [\'Q1747689\'], \'P17\': [\'Q1747689\'], \'P1889\': [\'Q107013169\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 73: Q107013169 (religion in ancient Rome)
MERGE (n:Entity {qid: 'Q107013169'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q107013169',
  n.entity_id = 'concept_q107013169',
  n.label = 'religion in ancient Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P1889\': [\'Q337547\', \'Q107013262\'], \'P1269\': [\'Q1747689\'], \'P17\': [\'Q1747689\', \'Q17167\', \'Q2277\'], \'P910\': [\'Q8648681\'], \'P31\': [\'Q66374263\'], \'P279\': [\'Q13198592\'], \'P361\': [\'Q1200427\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 74: Q5626901 (Template:Roman religion)
MERGE (n:Entity {qid: 'Q5626901'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q5626901',
  n.entity_id = 'concept_q5626901',
  n.label = 'Template:Roman religion',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P31\': [\'Q11753321\', \'Q11266439\'], \'P1423\': [\'Q337547\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 75: Q11204 (legislature)
MERGE (n:Entity {qid: 'Q11204'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q11204',
  n.entity_id = 'concept_q11204',
  n.label = 'legislature',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 47,
  n.property_summary = '{\'P910\': [\'Q5902757\'], \'P279\': [\'Q1752346\', \'Q2324993\', \'Q895526\'], \'P1269\': [\'Q79896\', \'Q7174\'], \'P1687\': [\'P194\'], \'P2283\': [\'Q3406566\'], \'P2670\': [\'Q4175034\'], \'P460\': [\'Q10553309\'], \'P361\': [\'Q7188\', \'Q2101636\'], \'P5008\': [\'Q6173448\'], \'P1343\': [\'Q20078554\', \'Q19219752\', \'Q1029706\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 76: Q1144514 (Curia Julia)
MERGE (n:Entity {qid: 'Q1144514'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1144514',
  n.entity_id = 'concept_q1144514',
  n.label = 'Curia Julia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 22,
  n.property_summary = '{\'P31\': [\'Q5194727\', \'Q839954\'], \'P17\': [\'Q38\'], \'P131\': [\'Q220\'], \'P276\': [\'Q180212\'], \'P910\': [\'Q55246515\'], \'P2596\': [\'Q1747689\'], \'P1398\': [\'Q1144512\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 77: Q32899669 (Category:Roman Senate)
MERGE (n:Entity {qid: 'Q32899669'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q32899669',
  n.entity_id = 'concept_q32899669',
  n.label = 'Category:Roman Senate',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P301\': [\'Q130614\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 78: Q1225322 (ordo senatorius)
MERGE (n:Entity {qid: 'Q1225322'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1225322',
  n.entity_id = 'concept_q1225322',
  n.label = 'ordo senatorius',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P31\': [\'Q1392538\'], \'P279\': [\'Q1001045\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 79: Q2915100 (political institutions of ancient Rome)
MERGE (n:Entity {qid: 'Q2915100'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q2915100',
  n.entity_id = 'concept_q2915100',
  n.label = 'political institutions of ancient Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 8,
  n.property_summary = '{\'P279\': [\'Q18810687\'], \'P1001\': [\'Q1747689\'], \'P910\': [\'Q7953957\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 80: Q17197366 (type of organization)
MERGE (n:Entity {qid: 'Q17197366'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q17197366',
  n.entity_id = 'concept_q17197366',
  n.label = 'type of organization',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P279\': [\'Q16889133\', \'Q96251598\'], \'P910\': [\'Q6448834\'], \'P31\': [\'Q24017414\', \'Q151885\'], \'P8225\': [\'Q43229\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 81: Q3181656 (The Nuttall Encyclopædia)
MERGE (n:Entity {qid: 'Q3181656'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3181656',
  n.entity_id = 'concept_q3181656',
  n.label = 'The Nuttall Encyclopædia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 12,
  n.property_summary = '{\'P31\': [\'Q7725634\'], \'P407\': [\'Q1860\'], \'P136\': [\'Q5292\'], \'P6216\': [\'Q19652\'], \'P495\': [\'Q145\'], \'P138\': [\'Q26997543\'], \'P7937\': [\'Q5292\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 82: Q1138524 (Pauly–Wissowa)
MERGE (n:Entity {qid: 'Q1138524'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1138524',
  n.entity_id = 'concept_q1138524',
  n.label = 'Pauly–Wissowa',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 28,
  n.property_summary = '{\'P31\': [\'Q47461344\', \'Q60534428\'], \'P98\': [\'Q66607\', \'Q73314\', \'Q1642032\', \'Q1700609\', \'Q1782516\'], \'P793\': [\'Q7318524\', \'Q7318524\'], \'P123\': [\'Q1661918\', \'Q20061749\'], \'P156\': [\'Q12899625\', \'Q262758\'], \'P527\': [\'Q18822586\', \'Q18822599\', \'Q18822594\'], \'P495\': [\'Q1206012\', \'Q713750\'], \'P155\': [\'Q30545150\'], \'P407\': [\'Q188\'], \'P910\': [\'Q48373401\'], \'P291\': [\'Q1022\'], \'P50\': [\'Q2818964\'], \'P7937\': [\'Q5292\'], \'P138\': [\'Q70497\', \'Q66607\'], \'P361\': [\'Q132460627\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 83: Q867541 (Encyclopædia Britannica 11th edition)
MERGE (n:Entity {qid: 'Q867541'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q867541',
  n.entity_id = 'concept_q867541',
  n.label = 'Encyclopædia Britannica 11th edition',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 44,
  n.property_summary = '{\'P407\': [\'Q1860\'], \'P31\': [\'Q3331189\'], \'P629\': [\'Q455\'], \'P291\': [\'Q60\', \'Q350\'], \'P910\': [\'Q15625009\'], \'P495\': [\'Q145\', \'Q174193\'], \'P6216\': [\'Q19652\'], \'P155\': [\'Q84246840\'], \'P156\': [\'Q15987490\'], \'P136\': [\'Q5292\'], \'P98\': [\'Q5607942\'], \'P123\': [\'Q912887\'], \'P1424\': [\'Q6519046\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 84: Q8386687 (Category:Coins of ancient Rome)
MERGE (n:Entity {qid: 'Q8386687'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8386687',
  n.entity_id = 'concept_q8386687',
  n.label = 'Category:Coins of ancient Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P301\': [\'Q952064\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 85: Q17524420 (aspect of history)
MERGE (n:Entity {qid: 'Q17524420'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q17524420',
  n.entity_id = 'concept_q17524420',
  n.label = 'aspect of history',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P279\': [\'Q21040055\', \'Q1047113\'], \'P1687\': [\'P2184\'], \'P1963\': [\'P1269\', \'P921\', \'P910\', \'P7153\', \'P2348\'], \'P2579\': [\'Q1066186\'], \'P361\': [\'Q309\'], \'P31\': [\'Q19478619\'], \'P8225\': [\'Q309\'], \'P1889\': [\'Q18340514\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 86: Q19219752 (Meyers Konversations-Lexikon, 4th edition (1885–1890))
MERGE (n:Entity {qid: 'Q19219752'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q19219752',
  n.entity_id = 'concept_q19219752',
  n.label = 'Meyers Konversations-Lexikon, 4th edition (1885–1890)',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q3331189\'], \'P407\': [\'Q188\', \'Q9056\'], \'P629\': [\'Q1138512\'], \'P291\': [\'Q2079\'], \'P495\': [\'Q1206012\'], \'P527\': [\'Q56547107\'], \'P123\': [\'Q314219\'], \'P6216\': [\'Q19652\'], \'P910\': [\'Q29044160\'], \'P50\': [\'Q1690980\'], \'P767\': [\'Q73219\', \'Q107315847\', \'Q78142\', \'Q98427\', \'Q5806821\'], \'P136\': [\'Q18168594\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 87: Q662137 (Roman Republican currency)
MERGE (n:Entity {qid: 'Q662137'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q662137',
  n.entity_id = 'concept_q662137',
  n.label = 'Roman Republican currency',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 7,
  n.property_summary = '{\'P361\': [\'Q952064\'], \'P1269\': [\'Q8142\', \'Q17167\'], \'P31\': [\'Q17524420\'], \'P156\': [\'Q638048\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 88: Q638048 (Roman Imperial coinage)
MERGE (n:Entity {qid: 'Q638048'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q638048',
  n.entity_id = 'concept_q638048',
  n.label = 'Roman Imperial coinage',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 7,
  n.property_summary = '{\'P910\': [\'Q9216807\'], \'P361\': [\'Q952064\'], \'P1269\': [\'Q8142\', \'Q2277\'], \'P31\': [\'Q17524420\'], \'P155\': [\'Q662137\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 89: Q8142 (currency)
MERGE (n:Entity {qid: 'Q8142'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8142',
  n.entity_id = 'concept_q8142',
  n.label = 'currency',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 75,
  n.property_summary = '{\'P279\': [\'Q11105360\', \'Q47574\', \'Q1368\', \'Q65240001\'], \'P910\': [\'Q6959409\', \'Q41724807\'], \'P1963\': [\'P498\', \'P562\', \'P17\', \'P489\', \'P9059\'], \'P1424\': [\'Q6453809\'], \'P1687\': [\'P38\'], \'P2354\': [\'Q858338\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P1889\': [\'Q15220494\', \'Q5194983\', \'Q6936966\', \'Q1368\', \'Q831772\'], \'P5869\': [\'Q4917\', \'Q4916\', \'Q80524\', \'Q131473\'], \'P2184\': [\'Q3137262\'], \'P1343\': [\'Q101314624\', \'Q20078554\', \'Q602358\', \'Q19180675\', \'Q19219752\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 90: Q28783456 (obsolete currency)
MERGE (n:Entity {qid: 'Q28783456'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q28783456',
  n.entity_id = 'concept_q28783456',
  n.label = 'obsolete currency',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P279\': [\'Q8142\', \'Q15893266\', \'Q28607529\'], \'P910\': [\'Q7712665\', \'Q7713802\'], \'P2354\': [\'Q2042322\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 91: Q3879434 (Roman numismatics)
MERGE (n:Entity {qid: 'Q3879434'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3879434',
  n.entity_id = 'concept_q3879434',
  n.label = 'Roman numismatics',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P2578\': [\'Q952064\'], \'P279\': [\'Q576052\'], \'P31\': [\'Q1047113\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 92: Q14618893 (Classical Roman Empire)
MERGE (n:Entity {qid: 'Q14618893'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q14618893',
  n.entity_id = 'subjectconcept_q14618893',
  n.label = 'Classical Roman Empire',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 9,
  n.property_summary = '{\'P17\': [\'Q1747689\'], \'P361\': [\'Q2671119\'], \'P31\': [\'Q17524420\', \'Q11514315\', \'Q3024240\'], \'P1269\': [\'Q2671119\'], \'P279\': [\'Q2277\', \'Q16147990\'], \'P1889\': [\'Q6111354\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 93: Q11772 (Ancient Greece)
MERGE (n:Entity {qid: 'Q11772'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q11772',
  n.entity_id = 'concept_q11772',
  n.label = 'Ancient Greece',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 71,
  n.property_summary = '{\'P31\': [\'Q1792644\', \'Q28171280\', \'Q1620908\', \'Q3502482\', \'Q11042\'], \'P910\': [\'Q7215882\'], \'P361\': [\'Q7794\'], \'P1151\': [\'Q10566332\'], \'P2184\': [\'Q7798\'], \'P30\': [\'Q46\', \'Q48\', \'Q15\'], \'P2959\': [\'Q22828833\'], \'P1792\': [\'Q6692116\'], \'P47\': [\'Q41741\', \'Q32047\', \'Q83311\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P5125\': [\'Q7112550\'], \'P2579\': [\'Q435608\', \'Q16267481\', \'Q841090\'], \'P1424\': [\'Q6054993\'], \'P8744\': [\'Q2736823\'], \'P1343\': [\'Q3181656\'], \'P2341\': [\'Q41\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 94: Q181264 (Mycenaean Greece)
MERGE (n:Entity {qid: 'Q181264'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q181264',
  n.entity_id = 'concept_q181264',
  n.label = 'Mycenaean Greece',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 49,
  n.property_summary = '{\'P31\': [\'Q465299\', \'Q11042\', \'Q1292119\', \'Q8432\'], \'P910\': [\'Q8655406\'], \'P61\': [\'Q57106\'], \'P2579\': [\'Q26425130\'], \'P2348\': [\'Q11761\'], \'P156\': [\'Q210443\'], \'P1382\': [\'Q134178\'], \'P1343\': [\'Q602358\', \'Q20078554\', \'Q1138524\'], \'P1365\': [\'Q134178\'], \'P607\': [\'Q112106967\'], \'P5008\': [\'Q6173448\'], \'P276\': [\'Q78967\', \'Q34374\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 95: Q134178 (Minoan civilization)
MERGE (n:Entity {qid: 'Q134178'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q134178',
  n.entity_id = 'concept_q134178',
  n.label = 'Minoan civilization',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 56,
  n.property_summary = '{\'P910\': [\'Q7213579\'], \'P31\': [\'Q465299\', \'Q2718886\', \'Q28171280\', \'Q11514315\', \'Q1292119\'], \'P361\': [\'Q11761\', \'Q1516494\'], \'P138\': [\'Q23168\'], \'P276\': [\'Q34374\'], \'P1382\': [\'Q181264\', \'Q318144\'], \'P2936\': [\'Q1669994\'], \'P1366\': [\'Q181264\'], \'P7867\': [\'Q84118110\'], \'P1343\': [\'Q20078554\', \'Q20078554\'], \'P607\': [\'Q112106967\'], \'P2341\': [\'Q34374\'], \'P1424\': [\'Q14695113\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 96: Q17161 (Etruscans)
MERGE (n:Entity {qid: 'Q17161'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q17161',
  n.entity_id = 'concept_q17161',
  n.label = 'Etruscans',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 64,
  n.property_summary = '{\'P910\': [\'Q7147389\'], \'P140\': [\'Q478186\'], \'P1343\': [\'Q678259\', \'Q19219752\', \'Q66386517\', \'Q1138524\'], \'P527\': [\'Q5404909\', \'Q3411955\', \'Q3411971\', \'Q3589333\', \'Q3411970\'], \'P31\': [\'Q8432\', \'Q4204501\'], \'P2348\': [\'Q486761\'], \'P103\': [\'Q35726\'], \'P2283\': [\'Q119094\'], \'P2341\': [\'Q38\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 97: Q245813 (Bronze age Cyprus)
MERGE (n:Entity {qid: 'Q245813'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q245813',
  n.entity_id = 'concept_q245813',
  n.label = 'Bronze age Cyprus',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q15401633\'], \'P361\': [\'Q11772\', \'Q446185\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 98: Q12544 (Byzantine Empire)
MERGE (n:Entity {qid: 'Q12544'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q12544',
  n.entity_id = 'concept_q12544',
  n.label = 'Byzantine Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 5,
  n.properties_count = 144,
  n.property_summary = '{\'P140\': [\'Q3333484\'], \'P910\': [\'Q5819039\'], \'P31\': [\'Q48349\', \'Q3024240\', \'Q11514315\', \'Q392160\', \'Q56061\'], \'P36\': [\'Q16869\'], \'P156\': [\'Q8575586\', \'Q12490507\', \'Q12560\', \'Q178913\', \'Q603771\'], \'P1343\': [\'Q302556\', \'Q3181656\', \'Q19180675\', \'Q4173137\', \'Q1146980\'], \'P37\': [\'Q1163234\', \'Q36387\'], \'P122\': [\'Q184558\', \'Q238399\'], \'P38\': [\'Q231455\', \'Q1018755\', \'Q6851831\', \'Q127441\', \'Q1090682\'], \'P1792\': [\'Q6993774\'], \'P1465\': [\'Q13993758\'], \'P1464\': [\'Q8049025\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P5125\': [\'Q7112751\'], \'P2579\': [\'Q648154\'], \'P30\': [\'Q46\', \'Q15\', \'Q48\'], \'P1344\': [\'Q698985\', \'Q29100\', \'Q2288144\', \'Q858108\', \'Q327150\'], \'P1365\': [\'Q2277\', \'Q42834\', \'Q178897\', \'Q24089696\'], \'P1366\': [\'Q603771\', \'Q12560\', \'Q1152508\', \'Q6753657\', \'Q178897\'], \'P1830\': [\'Q2302532\', \'Q2968035\', \'Q301376\'], \'P2936\': [\'Q397\', \'Q36387\', \'Q107358\'], \'P3075\': [\'Q3333484\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 99: Q3617880 (Italic peoples)
MERGE (n:Entity {qid: 'Q3617880'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3617880',
  n.entity_id = 'concept_q3617880',
  n.label = 'Italic peoples',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 16,
  n.property_summary = '{\'P31\': [\'Q55208590\', \'Q4204501\'], \'P1343\': [\'Q602358\', \'Q17378135\', \'Q4114391\', \'Q19180675\', \'Q4173137\'], \'P910\': [\'Q7052444\'], \'P276\': [\'Q145694\'], \'P279\': [\'Q394067\', \'Q475027\'], \'P2341\': [\'Q145694\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 100: Q1778719 (Lydians)
MERGE (n:Entity {qid: 'Q1778719'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1778719',
  n.entity_id = 'concept_q1778719',
  n.label = 'Lydians',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P910\': [\'Q8607519\'], \'P31\': [\'Q4204501\'], \'P279\': [\'Q290170\'], \'P2936\': [\'Q36095\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 101: Q83958 (Macedonia)
MERGE (n:Entity {qid: 'Q83958'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q83958',
  n.entity_id = 'concept_q83958',
  n.label = 'Macedonia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 52,
  n.property_summary = '{\'P31\': [\'Q1250464\', \'Q3024240\'], \'P910\': [\'Q7116772\'], \'P122\': [\'Q79751\', \'Q7269\'], \'P140\': [\'Q855270\'], \'P36\': [\'Q16963755\', \'Q213679\', \'Q404200\'], \'P194\': [\'Q1122426\'], \'P38\': [\'Q1083662\'], \'P1343\': [\'Q602358\', \'Q19180675\', \'Q4173137\', \'Q4086271\', \'Q30059240\'], \'P138\': [\'Q576065\'], \'P2184\': [\'Q29687924\'], \'P37\': [\'Q35974\', \'Q35497\'], \'P1464\': [\'Q31937455\'], \'P30\': [\'Q46\'], \'P17\': [\'Q83958\'], \'P2936\': [\'Q35974\', \'Q35497\'], \'P2238\': [\'Q866007\'], \'P47\': [\'Q41741\', \'Q32047\'], \'P1889\': [\'Q39702\', \'Q103251\'], \'P527\': [\'Q95982472\'], \'P3075\': [\'Q855270\'], \'P5008\': [\'Q6173448\'], \'P1344\': [\'Q233667\', \'Q16683515\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 102: Q131802 (Scythians)
MERGE (n:Entity {qid: 'Q131802'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q131802',
  n.entity_id = 'concept_q131802',
  n.label = 'Scythians',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 48,
  n.property_summary = '{\'P910\': [\'Q8723917\'], \'P31\': [\'Q4204501\'], \'P1343\': [\'Q2657718\', \'Q4086271\', \'Q19180675\', \'Q602358\', \'Q1138524\'], \'P1299\': [\'Q746583\', \'Q9184\'], \'P2670\': [\'Q1753235\'], \'P103\': [\'Q749834\'], \'P1412\': [\'Q749834\'], \'P276\': [\'Q845909\'], \'P361\': [\'Q1672477\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 103: Q6111354 (Classical Rome)
MERGE (n:Entity {qid: 'Q6111354'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6111354',
  n.entity_id = 'concept_q6111354',
  n.label = 'Classical Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P31\': [\'Q11514315\', \'Q11042\'], \'P361\': [\'Q486761\'], \'P1269\': [\'Q1747689\'], \'P1889\': [\'Q14618893\'], \'P279\': [\'Q1747689\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 104: Q8381710 (Category:Classical antiquity)
MERGE (n:Entity {qid: 'Q8381710'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8381710',
  n.entity_id = 'concept_q8381710',
  n.label = 'Category:Classical antiquity',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P301\': [\'Q486761\'], \'P31\': [\'Q4167836\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 105: Q217050 (late antiquity)
MERGE (n:Entity {qid: 'Q217050'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q217050',
  n.entity_id = 'concept_q217050',
  n.label = 'late antiquity',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 38,
  n.property_summary = '{\'P1151\': [\'Q10968580\'], \'P910\': [\'Q6236097\'], \'P31\': [\'Q11514315\', \'Q465299\', \'Q11042\'], \'P156\': [\'Q202763\'], \'P155\': [\'Q486761\'], \'P1382\': [\'Q202763\'], \'P5008\': [\'Q6173448\'], \'P279\': [\'Q41493\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 106: Q937284 (Greco-Roman world)
MERGE (n:Entity {qid: 'Q937284'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q937284',
  n.entity_id = 'concept_q937284',
  n.label = 'Greco-Roman world',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 15,
  n.property_summary = '{\'P910\': [\'Q7452497\'], \'P31\': [\'Q82794\'], \'P138\': [\'Q11772\', \'Q1747689\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 107: Q1292119 (style)
MERGE (n:Entity {qid: 'Q1292119'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1292119',
  n.entity_id = 'concept_q1292119',
  n.label = 'style',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 21,
  n.property_summary = '{\'P31\': [\'Q151885\', \'Q3533467\'], \'P361\': [\'Q11042\'], \'P527\': [\'Q1792644\', \'Q32880\'], \'P2579\': [\'Q35986\'], \'P1889\': [\'Q166557\', \'Q44928003\'], \'P910\': [\'Q7210517\'], \'P279\': [\'Q1207505\'], \'P1343\': [\'Q19219752\'], \'P1424\': [\'Q14400798\'], \'P1269\': [\'Q50637\', \'Q1143546\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 108: Q41493 (ancient history)
MERGE (n:Entity {qid: 'Q41493'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q41493',
  n.entity_id = 'concept_q41493',
  n.label = 'ancient history',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 77,
  n.property_summary = '{\'P910\': [\'Q6499653\'], \'P156\': [\'Q12554\', \'Q7234117\'], \'P1343\': [\'Q2041543\', \'Q66890318\', \'Q19219752\', \'Q867541\'], \'P1269\': [\'Q309\'], \'P31\': [\'Q186081\', \'Q1047113\', \'Q11514315\'], \'P5125\': [\'Q28453687\'], \'P1889\': [\'Q486761\', \'Q110227091\'], \'P279\': [\'Q309\', \'Q116697863\'], \'P527\': [\'Q486761\', \'Q269678\', \'Q11768\', \'Q217050\'], \'P1424\': [\'Q6678356\'], \'P155\': [\'Q11756\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 109: Q98270938 (Early antiquity)
MERGE (n:Entity {qid: 'Q98270938'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q98270938',
  n.entity_id = 'concept_q98270938',
  n.label = 'Early antiquity',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q15401633\'], \'P361\': [\'Q41493\'], \'P156\': [\'Q486761\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 110: Q112939719 (Classical Greek and Roman history)
MERGE (n:Entity {qid: 'Q112939719'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q112939719',
  n.entity_id = 'concept_q112939719',
  n.label = 'Classical Greek and Roman history',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 9,
  n.property_summary = '{\'P31\': [\'Q11862829\'], \'P279\': [\'Q309\'], \'P910\': [\'Q18343057\'], \'P1269\': [\'Q7787\'], \'P361\': [\'Q7787\'], \'P3095\': [\'Q20873384\'], \'P527\': [\'Q830852\', \'Q7798\'], \'P2578\': [\'Q486761\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 111: Q495527 (classical philology)
MERGE (n:Entity {qid: 'Q495527'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q495527',
  n.entity_id = 'concept_q495527',
  n.label = 'classical philology',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 37,
  n.property_summary = '{\'P279\': [\'Q40634\', \'Q841090\'], \'P910\': [\'Q7298503\'], \'P31\': [\'Q11862829\', \'Q4671286\', \'Q189533\'], \'P3095\': [\'Q16267607\'], \'P461\': [\'Q11790583\'], \'P1343\': [\'Q602358\', \'Q19180675\'], \'P361\': [\'Q841090\'], \'P527\': [\'Q757248\'], \'P1889\': [\'Q10913068\'], \'P1382\': [\'Q112800417\'], \'P2578\': [\'Q397\', \'Q35497\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 112: Q3351707 (Pax Leksikon)
MERGE (n:Entity {qid: 'Q3351707'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3351707',
  n.entity_id = 'concept_q3351707',
  n.label = 'Pax Leksikon',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P31\': [\'Q47461344\', \'Q18168594\'], \'P407\': [\'Q9043\'], \'P2670\': [\'Q1238720\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 113: Q19660746 (person related to this place)
MERGE (n:Entity {qid: 'Q19660746'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q19660746',
  n.entity_id = 'concept_q19660746',
  n.label = 'person related to this place',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P279\': [\'Q215627\', \'Q111604130\'], \'P31\': [\'Q19478619\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 114: Q16931679 (Overthrow of the Roman monarchy)
MERGE (n:Entity {qid: 'Q16931679'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16931679',
  n.entity_id = 'concept_q16931679',
  n.label = 'Overthrow of the Roman monarchy',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 9,
  n.property_summary = '{\'P31\': [\'Q10931\'], \'P276\': [\'Q1747689\'], \'P17\': [\'Q201038\'], \'P155\': [\'Q119137625\'], \'P156\': [\'Q2839628\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 115: Q119137625 (Second Roman Kingdom)
MERGE (n:Entity {qid: 'Q119137625'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q119137625',
  n.entity_id = 'subjectconcept_q119137625',
  n.label = 'Second Roman Kingdom',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 9,
  n.property_summary = '{\'P31\': [\'Q11514315\'], \'P155\': [\'Q3921629\'], \'P1382\': [\'Q108655256\'], \'P17\': [\'Q1747689\'], \'P156\': [\'Q16931679\', \'Q2839628\'], \'P279\': [\'Q201038\'], \'P361\': [\'Q201038\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 116: Q16869 (Constantinople)
MERGE (n:Entity {qid: 'Q16869'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q16869',
  n.entity_id = 'place_q16869',
  n.label = 'Constantinople',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 78,
  n.property_summary = '{\'P1376\': [\'Q12544\', \'Q178897\', \'Q2277\', \'Q12544\', \'Q12560\'], \'P31\': [\'Q515\', \'Q56061\', \'Q15661340\'], \'P138\': [\'Q8413\'], \'P30\': [\'Q46\', \'Q48\'], \'P156\': [\'Q406\'], \'P910\': [\'Q7494925\'], \'P17\': [\'Q12544\', \'Q178897\', \'Q1747689\', \'Q12560\', \'Q43\'], \'P1464\': [\'Q8073857\'], \'P155\': [\'Q23725\'], \'P1792\': [\'Q6805163\'], \'P1465\': [\'Q9218161\'], \'P460\': [\'Q2008228\'], \'P1343\': [\'Q4114391\', \'Q602358\', \'Q19180675\', \'Q4173137\', \'Q1138524\'], \'P1791\': [\'Q7978212\'], \'P793\': [\'Q160077\', \'Q700886\', \'Q16827799\', \'Q3485863\', \'Q61072733\'], \'P7867\': [\'Q84133403\'], \'P1365\': [\'Q23725\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 117: Q13364 (Ravenna)
MERGE (n:Entity {qid: 'Q13364'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q13364',
  n.entity_id = 'place_q13364',
  n.label = 'Ravenna',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 5,
  n.properties_count = 138,
  n.property_summary = '{\'P190\': [\'Q6829\', \'Q44238\', \'Q130272\', \'Q207639\', \'Q1722\'], \'P6\': [\'Q3738068\', \'Q24717798\'], \'P17\': [\'Q38\', \'Q170174\', \'Q4948\', \'Q170174\', \'Q4948\'], \'P131\': [\'Q16252\', \'Q694740\', \'Q1237690\', \'Q3270112\', \'Q3270112\'], \'P47\': [\'Q95090\', \'Q52957\', \'Q99934\', \'Q52975\', \'Q6662\'], \'P417\': [\'Q320199\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P910\': [\'Q8635352\'], \'P31\': [\'Q747074\', \'Q515\', \'Q1549591\'], \'P1464\': [\'Q8069548\'], \'P1465\': [\'Q9219621\'], \'P1740\': [\'Q10219757\'], \'P1792\': [\'Q7925225\'], \'P1376\': [\'Q16252\', \'Q3755547\', \'Q3270112\', \'Q3270110\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 118: Q18287233 (Roma)
MERGE (n:Entity {qid: 'Q18287233'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q18287233',
  n.entity_id = 'place_q18287233',
  n.label = 'Roma',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 36,
  n.property_summary = '{\'P31\': [\'Q839954\', \'Q15661340\', \'Q17362920\'], \'P17\': [\'Q38\'], \'P1889\': [\'Q18690178\', \'Q7361461\'], \'P910\': [\'Q8251497\'], \'P1465\': [\'Q110763718\'], \'P2596\': [\'Q1747689\'], \'P460\': [\'Q220\'], \'P1464\': [\'Q124988611\'], \'P1792\': [\'Q124988636\'], \'P527\': [\'Q134036721\'], \'P1376\': [\'Q201038\', \'Q17167\', \'Q2277\', \'Q1747689\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 119: Q173424 (autocracy)
MERGE (n:Entity {qid: 'Q173424'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q173424',
  n.entity_id = 'concept_q173424',
  n.label = 'autocracy',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 36,
  n.property_summary = '{\'P31\': [\'Q1307214\', \'Q183039\'], \'P279\': [\'Q28108\', \'Q20076236\'], \'P1343\': [\'Q20078554\', \'Q602358\', \'Q19180675\', \'Q19219752\', \'Q867541\'], \'P461\': [\'Q7174\'], \'P460\': [\'Q13165396\'], \'P910\': [\'Q9768904\'], \'P527\': [\'Q7269\', \'Q317\', \'Q2439061\'], \'P1552\': [\'Q1899269\', \'Q375159\', \'Q7281\', \'Q17099732\', \'Q177253\'], \'P1889\': [\'Q37739\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 120: Q174450 (Roman Tetrarchy)
MERGE (n:Entity {qid: 'Q174450'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q174450',
  n.entity_id = 'subjectconcept_q174450',
  n.label = 'Roman Tetrarchy',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 23,
  n.property_summary = '{\'P31\': [\'Q1307214\', \'Q6555883\', \'Q11514315\'], \'P1343\': [\'Q602358\', \'Q4532138\', \'Q4173137\'], \'P910\': [\'Q9521162\'], \'P279\': [\'Q56061\', \'Q1553864\'], \'P1365\': [\'Q129167\'], \'P1269\': [\'Q2671119\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 121: Q208041 (sestertius)
MERGE (n:Entity {qid: 'Q208041'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q208041',
  n.entity_id = 'concept_q208041',
  n.label = 'sestertius',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 36,
  n.property_summary = '{\'P31\': [\'Q918448\', \'Q113813711\'], \'P1343\': [\'Q602358\', \'Q19180675\', \'Q1138524\', \'Q30059240\', \'Q3181656\'], \'P910\': [\'Q55276293\'], \'P279\': [\'Q952064\'], \'P17\': [\'Q1747689\'], \'P186\': [\'Q1090\', \'Q34095\', \'Q39782\'], \'P138\': [\'Q114880931\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 122: Q187776 (denarius)
MERGE (n:Entity {qid: 'Q187776'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q187776',
  n.entity_id = 'concept_q187776',
  n.label = 'denarius',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 39,
  n.property_summary = '{\'P186\': [\'Q1090\'], \'P17\': [\'Q1747689\'], \'P910\': [\'Q9513003\'], \'P279\': [\'Q41207\'], \'P31\': [\'Q8142\', \'Q113813711\', \'Q918448\'], \'P138\': [\'Q23806\'], \'P489\': [\'Q4419555\'], \'P1343\': [\'Q4086271\', \'Q3181656\', \'Q19219752\', \'Q1138524\'], \'P1889\': [\'Q177875\'], \'P361\': [\'Q952064\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 123: Q476078 (aureus)
MERGE (n:Entity {qid: 'Q476078'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q476078',
  n.entity_id = 'concept_q476078',
  n.label = 'aureus',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 28,
  n.property_summary = '{\'P910\': [\'Q7609880\'], \'P31\': [\'Q8142\', \'Q7048891\', \'Q918448\'], \'P279\': [\'Q860641\', \'Q952064\'], \'P17\': [\'Q17167\'], \'P186\': [\'Q897\'], \'P1889\': [\'Q643507\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 124: Q376895 (as)
MERGE (n:Entity {qid: 'Q376895'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q376895',
  n.entity_id = 'concept_q376895',
  n.label = 'as',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 29,
  n.property_summary = '{\'P31\': [\'Q8142\', \'Q918448\'], \'P910\': [\'Q55299567\'], \'P1343\': [\'Q30059240\', \'Q602358\', \'Q602358\', \'Q4086271\', \'Q4086271\'], \'P17\': [\'Q1747689\'], \'P361\': [\'Q952064\'], \'P279\': [\'Q41207\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 125: Q7603670 (state church of the Roman Empire)
MERGE (n:Entity {qid: 'Q7603670'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q7603670',
  n.entity_id = 'concept_q7603670',
  n.label = 'state church of the Roman Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P31\': [\'Q2325038\'], \'P17\': [\'Q2277\'], \'P2348\': [\'Q2277\'], \'P279\': [\'Q13291346\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 126: Q2671119 (history of the Roman Empire)
MERGE (n:Entity {qid: 'Q2671119'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q2671119',
  n.entity_id = 'concept_q2671119',
  n.label = 'history of the Roman Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 13,
  n.property_summary = '{\'P910\': [\'Q8520196\'], \'P31\': [\'Q17544377\'], \'P1269\': [\'Q2277\'], \'P361\': [\'Q156312\'], \'P279\': [\'Q7787\'], \'P1382\': [\'Q830852\'], \'P527\': [\'Q75207\', \'Q787204\', \'Q206414\', \'Q14618893\', \'Q16147990\'], \'P1552\': [\'Q123753691\'], \'P1299\': [\'Q131613709\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 127: Q842606 (Roman emperor)
MERGE (n:Entity {qid: 'Q842606'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q842606',
  n.entity_id = 'concept_q842606',
  n.label = 'Roman emperor',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 30,
  n.property_summary = '{\'P279\': [\'Q39018\'], \'P910\': [\'Q6992597\'], \'P31\': [\'Q4164871\', \'Q355567\', \'Q114962596\'], \'P1001\': [\'Q1747689\'], \'P2354\': [\'Q125740\'], \'P1889\': [\'Q181765\'], \'P1366\': [\'Q18577504\', \'Q111841409\'], \'P1424\': [\'Q10801483\', \'Q22707299\'], \'P1299\': [\'Q126364388\'], \'P17\': [\'Q1747689\'], \'P6104\': [\'Q124005020\', \'Q26208713\', \'Q4913761\', \'Q11336485\', \'Q5492483\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 128: Q21201536 (Q21201536)
MERGE (n:Entity {qid: 'Q21201536'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q21201536',
  n.entity_id = 'concept_q21201536',
  n.label = 'Q21201536',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P2959\': [\'Q2277\'], \'P31\': [\'Q21286738\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 129: Q7209 (Han dynasty)
MERGE (n:Entity {qid: 'Q7209'})
ON CREATE SET
  n.entity_cipher = 'ent_sub_Q7209',
  n.entity_id = 'subjectconcept_q7209',
  n.label = 'Han dynasty',
  n.entity_type = 'SUBJECTCONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 55,
  n.property_summary = '{\'P31\': [\'Q12857432\', \'Q50068795\', \'Q11514315\', \'Q3024240\'], \'P910\': [\'Q7148757\'], \'P36\': [\'Q6501000\', \'Q6501000\', \'Q187136\', \'Q187136\', \'Q404529\'], \'P1343\': [\'Q2041543\', \'Q602358\', \'Q124737633\'], \'P530\': [\'Q2277\'], \'P527\': [\'Q1072949\', \'Q1147037\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P156\': [\'Q320930\', \'Q320925\', \'Q274488\'], \'P30\': [\'Q48\'], \'P122\': [\'Q7269\'], \'P361\': [\'Q11596055\', \'Q5326669\'], \'P2184\': [\'Q15709899\'], \'P17\': [\'Q12060881\'], \'P1365\': [\'Q7183\'], \'P138\': [\'Q1574130\'], \'P1889\': [\'Q1574130\', \'Q123576003\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 130: Q62646 (Germania)
MERGE (n:Entity {qid: 'Q62646'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q62646',
  n.entity_id = 'concept_q62646',
  n.label = 'Germania',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 25,
  n.property_summary = '{\'P31\': [\'Q1620908\'], \'P910\': [\'Q9223526\'], \'P530\': [\'Q2277\'], \'P1889\': [\'Q225018\'], \'P17\': [\'Q183\'], \'P2348\': [\'Q486761\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 131: Q302980 (Hibernia)
MERGE (n:Entity {qid: 'Q302980'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q302980',
  n.entity_id = 'concept_q302980',
  n.label = 'Hibernia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 11,
  n.property_summary = '{\'P31\': [\'Q134607850\'], \'P1343\': [\'Q20078554\', \'Q3181656\', \'Q867541\'], \'P1269\': [\'Q22890\', \'Q253854\'], \'P407\': [\'Q253854\'], \'P10476\': [\'Q22890\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 132: Q32642796 (Q32642796)
MERGE (n:Entity {qid: 'Q32642796'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q32642796',
  n.entity_id = 'concept_q32642796',
  n.label = 'Q32642796',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q1322263\', \'Q2277\'], \'P4224\': [\'Q5\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 133: Q42859641 (Q42859641)
MERGE (n:Entity {qid: 'Q42859641'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q42859641',
  n.entity_id = 'concept_q42859641',
  n.label = 'Q42859641',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q18658526\', \'Q2277\'], \'P4224\': [\'Q5\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 134: Q5460604 (Wikipedia:List of articles all languages should have)
MERGE (n:Entity {qid: 'Q5460604'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q5460604',
  n.entity_id = 'concept_q5460604',
  n.label = 'Wikipedia:List of articles all languages should have',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P31\': [\'Q14204246\', \'Q16695773\', \'Q51539995\'], \'P910\': [\'Q8181072\', \'Q9785911\'], \'P360\': [\'Q15138389\'], \'P460\': [\'Q43375360\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 135: Q1986139 (Parthian Empire)
MERGE (n:Entity {qid: 'Q1986139'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1986139',
  n.entity_id = 'concept_q1986139',
  n.label = 'Parthian Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 50,
  n.property_summary = '{\'P910\': [\'Q8964152\'], \'P38\': [\'Q25570\'], \'P140\': [\'Q9601\', \'Q797944\'], \'P31\': [\'Q3024240\', \'Q48349\', \'Q816829\'], \'P37\': [\'Q25953\', \'Q107358\', \'Q28602\', \'Q32063\', \'Q946997\'], \'P138\': [\'Q1645483\'], \'P2596\': [\'Q25763\'], \'P112\': [\'Q315913\'], \'P122\': [\'Q4482688\'], \'P1906\': [\'Q938153\'], \'P1365\': [\'Q93180\'], \'P263\': [\'Q192541\', \'Q696193\', \'Q854672\', \'Q4803191\', \'Q636188\'], \'P36\': [\'Q854672\', \'Q192541\', \'Q1136681\', \'Q1518300\'], \'P3075\': [\'Q9601\', \'Q219903\'], \'P47\': [\'Q2277\'], \'P17\': [\'Q1986139\'], \'P2936\': [\'Q25953\'], \'P7867\': [\'Q84079862\'], \'P1343\': [\'Q1768721\', \'Q272530\', \'Q430428\', \'Q1269357\', \'Q1285731\'], \'P30\': [\'Q48\'], \'P1366\': [\'Q765845\', \'Q83891\'], \'P1889\': [\'Q1255614\'], \'P5008\': [\'Q6173448\'], \'P1344\': [\'Q65081364\'], \'P1792\': [\'Q8757039\'], \'P6104\': [\'Q21830396\', \'Q21830386\', \'Q8486702\', \'Q11106565\', \'Q26208713\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 136: Q3626028 (Dacia Mediterranea)
MERGE (n:Entity {qid: 'Q3626028'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3626028',
  n.entity_id = 'concept_q3626028',
  n.label = 'Dacia Mediterranea',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 8,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P131\': [\'Q2348363\'], \'P17\': [\'Q1747689\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 137: Q747040 (Hispania Ulterior)
MERGE (n:Entity {qid: 'Q747040'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q747040',
  n.entity_id = 'concept_q747040',
  n.label = 'Hispania Ulterior',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 20,
  n.property_summary = '{\'P361\': [\'Q186513\'], \'P17\': [\'Q1747689\'], \'P31\': [\'Q182547\'], \'P910\': [\'Q20893376\'], \'P1001\': [\'Q1747689\'], \'P36\': [\'Q2997165\'], \'P47\': [\'Q1126678\'], \'P4777\': [\'Q4918\', \'Q97\'], \'P3179\': [\'Q29\', \'Q45\'], \'P1366\': [\'Q219415\', \'Q188650\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 138: Q1126678 (Hispania Citerior)
MERGE (n:Entity {qid: 'Q1126678'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1126678',
  n.entity_id = 'concept_q1126678',
  n.label = 'Hispania Citerior',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 24,
  n.property_summary = '{\'P361\': [\'Q186513\'], \'P17\': [\'Q1747689\'], \'P31\': [\'Q182547\'], \'P36\': [\'Q1501940\'], \'P1001\': [\'Q1747689\'], \'P910\': [\'Q49687186\'], \'P47\': [\'Q747040\'], \'P4777\': [\'Q4918\', \'Q2090594\', \'Q97\', \'Q12431\'], \'P3179\': [\'Q29\'], \'P30\': [\'Q46\'], \'P1366\': [\'Q216791\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 139: Q170062 (Pannonia)
MERGE (n:Entity {qid: 'Q170062'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q170062',
  n.entity_id = 'concept_q170062',
  n.label = 'Pannonia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 47,
  n.property_summary = '{\'P36\': [\'Q508815\'], \'P31\': [\'Q182547\'], \'P910\': [\'Q9614468\'], \'P1343\': [\'Q2041543\', \'Q30059240\', \'Q602358\', \'Q19180675\', \'Q4091878\'], \'P1464\': [\'Q32642794\'], \'P1792\': [\'Q32642799\'], \'P1465\': [\'Q55908357\'], \'P7867\': [\'Q84058797\'], \'P17\': [\'Q2277\'], \'P2348\': [\'Q2277\'], \'P1366\': [\'Q642188\'], \'P2388\': [\'Q133227104\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 140: Q765845 (Mesopotamia)
MERGE (n:Entity {qid: 'Q765845'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q765845',
  n.entity_id = 'concept_q765845',
  n.label = 'Mesopotamia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P1889\': [\'Q6821580\'], \'P17\': [\'Q1747689\', \'Q12544\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q1986139\'], \'P1366\': [\'Q12490507\'], \'P36\': [\'Q112437254\', \'Q555783\'], \'P2388\': [\'Q3909811\', \'Q3716740\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 141: Q202311 (Roman Egypt)
MERGE (n:Entity {qid: 'Q202311'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q202311',
  n.entity_id = 'concept_q202311',
  n.label = 'Roman Egypt',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 30,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q8678273\'], \'P17\': [\'Q1747689\', \'Q12544\'], \'P1464\': [\'Q32653303\'], \'P1792\': [\'Q8674355\'], \'P47\': [\'Q692775\', \'Q1003997\', \'Q221353\'], \'P36\': [\'Q87\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q2320005\'], \'P1366\': [\'Q20987778\'], \'P30\': [\'Q15\'], \'P1889\': [\'Q20099095\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 142: Q623322 (Alpes Cottiae)
MERGE (n:Entity {qid: 'Q623322'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q623322',
  n.entity_id = 'concept_q623322',
  n.label = 'Alpes Cottiae',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 14,
  n.property_summary = '{\'P17\': [\'Q142\', \'Q38\'], \'P31\': [\'Q182547\'], \'P1366\': [\'Q103333\'], \'P36\': [\'Q112309778\'], \'P910\': [\'Q135338416\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 143: Q360922 (Alpes Graiae)
MERGE (n:Entity {qid: 'Q360922'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q360922',
  n.entity_id = 'concept_q360922',
  n.label = 'Alpes Graiae',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 7,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P1889\': [\'Q660100\', \'Q1262\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 144: Q309270 (Alpes Maritimae)
MERGE (n:Entity {qid: 'Q309270'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q309270',
  n.entity_id = 'concept_q309270',
  n.label = 'Alpes Maritimae',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 18,
  n.property_summary = '{\'P17\': [\'Q1747689\'], \'P31\': [\'Q182547\'], \'P36\': [\'Q2944184\', \'Q86724902\'], \'P112\': [\'Q1413\'], \'P1366\': [\'Q3755547\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 145: Q221353 (Arabia Petraea)
MERGE (n:Entity {qid: 'Q221353'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q221353',
  n.entity_id = 'concept_q221353',
  n.label = 'Arabia Petraea',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 27,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q9412529\'], \'P36\': [\'Q5788\'], \'P131\': [\'Q1228622\'], \'P3842\': [\'Q810\'], \'P1365\': [\'Q11029653\'], \'P1366\': [\'Q4896786\'], \'P47\': [\'Q1669578\'], \'P17\': [\'Q1747689\'], \'P2388\': [\'Q132859652\', \'Q3716733\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 146: Q1254480 (Roman Armenia)
MERGE (n:Entity {qid: 'Q1254480'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1254480',
  n.entity_id = 'concept_q1254480',
  n.label = 'Roman Armenia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q32349241\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q208404\'], \'P1366\': [\'Q208404\'], \'P36\': [\'Q706215\'], \'P2388\': [\'Q3716734\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 147: Q685537 (Britannia Inferior)
MERGE (n:Entity {qid: 'Q685537'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q685537',
  n.entity_id = 'concept_q685537',
  n.label = 'Britannia Inferior',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 11,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P361\': [\'Q185103\'], \'P36\': [\'Q958954\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 148: Q918059 (Britannia Superior)
MERGE (n:Entity {qid: 'Q918059'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q918059',
  n.entity_id = 'concept_q918059',
  n.label = 'Britannia Superior',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 10,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P361\': [\'Q185103\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P36\': [\'Q84\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 149: Q33490 (Cappadocia)
MERGE (n:Entity {qid: 'Q33490'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q33490',
  n.entity_id = 'concept_q33490',
  n.label = 'Cappadocia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P17\': [\'Q1747689\'], \'P36\': [\'Q10439273\'], \'P1365\': [\'Q29654286\'], \'P1366\': [\'Q682167\'], \'P1343\': [\'Q30059240\'], \'P2388\': [\'Q132004691\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 150: Q4819648 (Cilicia)
MERGE (n:Entity {qid: 'Q4819648'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q4819648',
  n.entity_id = 'concept_q4819648',
  n.label = 'Cilicia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q9444138\'], \'P36\': [\'Q134287\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1366\': [\'Q1565700\'], \'P138\': [\'Q620864\'], \'P706\': [\'Q620864\'], \'P2388\': [\'Q132181358\', \'Q132862500\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 151: Q971609 (Dacia)
MERGE (n:Entity {qid: 'Q971609'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q971609',
  n.entity_id = 'concept_q971609',
  n.label = 'Dacia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 32,
  n.property_summary = '{\'P910\': [\'Q8678265\'], \'P31\': [\'Q182547\'], \'P36\': [\'Q2671791\'], \'P37\': [\'Q397\'], \'P1889\': [\'Q173082\'], \'P7867\': [\'Q84085989\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q173082\'], \'P1366\': [\'Q1223485\'], \'P527\': [\'Q12277185\', \'Q748818\', \'Q12277575\'], \'P1343\': [\'Q1138524\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 152: Q12277185 (Dacia Superior)
MERGE (n:Entity {qid: 'Q12277185'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q12277185',
  n.entity_id = 'concept_q12277185',
  n.label = 'Dacia Superior',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P361\': [\'Q971609\'], \'P17\': [\'Q2277\'], \'P36\': [\'Q174665\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 153: Q12270914 (Tres Daciae)
MERGE (n:Entity {qid: 'Q12270914'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q12270914',
  n.entity_id = 'concept_q12270914',
  n.label = 'Tres Daciae',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P17\': [\'Q2277\'], \'P1365\': [\'Q12277185\', \'Q748818\', \'Q12277575\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 154: Q1820754 (Epirus)
MERGE (n:Entity {qid: 'Q1820754'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1820754',
  n.entity_id = 'concept_q1820754',
  n.label = 'Epirus',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 8,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P36\': [\'Q943637\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 155: Q1249412 (Galatia)
MERGE (n:Entity {qid: 'Q1249412'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1249412',
  n.entity_id = 'concept_q1249412',
  n.label = 'Galatia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q17167\', \'Q2277\'], \'P1365\': [\'Q26847\'], \'P1366\': [\'Q1491574\'], \'P1343\': [\'Q3181656\'], \'P36\': [\'Q557644\'], \'P2388\': [\'Q132776783\'], \'P910\': [\'Q25211635\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 156: Q715376 (Gallia Aquitania)
MERGE (n:Entity {qid: 'Q715376'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q715376',
  n.entity_id = 'concept_q715376',
  n.label = 'Gallia Aquitania',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P17\': [\'Q1747689\'], \'P1343\': [\'Q20078554\', \'Q1138524\'], \'P910\': [\'Q30726806\'], \'P36\': [\'Q2928315\'], \'P30\': [\'Q46\'], \'P527\': [\'Q204802\', \'Q522421\', \'Q1552899\'], \'P2388\': [\'Q133103698\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 157: Q206443 (Gallia Belgica)
MERGE (n:Entity {qid: 'Q206443'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q206443',
  n.entity_id = 'concept_q206443',
  n.label = 'Gallia Belgica',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 34,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q9025750\'], \'P36\': [\'Q41876\', \'Q3138\'], \'P17\': [\'Q1747689\', \'Q273025\', \'Q1747689\', \'Q42834\'], \'P3842\': [\'Q18677983\', \'Q18677767\', \'Q2982948\'], \'P361\': [\'Q879466\', \'Q2277\'], \'P131\': [\'Q1228610\'], \'P1269\': [\'Q319602\'], \'P156\': [\'Q153553\'], \'P138\': [\'Q337104\'], \'P2388\': [\'Q133226163\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 158: Q10971 (Gallia Lugdunensis)
MERGE (n:Entity {qid: 'Q10971'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q10971',
  n.entity_id = 'concept_q10971',
  n.label = 'Gallia Lugdunensis',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 26,
  n.property_summary = '{\'P131\': [\'Q1228610\', \'Q42834\', \'Q2277\'], \'P31\': [\'Q182547\'], \'P17\': [\'Q42834\', \'Q13590051\', \'Q1747689\'], \'P910\': [\'Q30726808\'], \'P36\': [\'Q665\'], \'P2348\': [\'Q2277\'], \'P1366\': [\'Q146246\'], \'P138\': [\'Q665\'], \'P1343\': [\'Q121944343\', \'Q121944345\'], \'P1889\': [\'Q38060\'], \'P2388\': [\'Q133188186\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 159: Q152136 (Germania Inferior)
MERGE (n:Entity {qid: 'Q152136'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q152136',
  n.entity_id = 'concept_q152136',
  n.label = 'Germania Inferior',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 29,
  n.property_summary = '{\'P156\': [\'Q831791\'], \'P910\': [\'Q8490977\'], \'P31\': [\'Q182547\'], \'P36\': [\'Q23048\'], \'P17\': [\'Q1747689\'], \'P1343\': [\'Q2657718\'], \'P361\': [\'Q2277\'], \'P1366\': [\'Q146246\'], \'P2388\': [\'Q132174254\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 160: Q219415 (Hispania Baetica)
MERGE (n:Entity {qid: 'Q219415'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q219415',
  n.entity_id = 'concept_q219415',
  n.label = 'Hispania Baetica',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 31,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P361\': [\'Q186513\', \'Q1747689\'], \'P910\': [\'Q9428012\'], \'P17\': [\'Q1747689\'], \'P36\': [\'Q2997165\'], \'P1001\': [\'Q1747689\'], \'P47\': [\'Q188650\', \'Q216791\'], \'P1366\': [\'Q126936\'], \'P131\': [\'Q186513\'], \'P138\': [\'Q14309\'], \'P1343\': [\'Q30059240\'], \'P2388\': [\'Q133101031\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 161: Q1330965 (Dalmatia)
MERGE (n:Entity {qid: 'Q1330965'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1330965',
  n.entity_id = 'concept_q1330965',
  n.label = 'Dalmatia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 20,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q9449947\'], \'P1366\': [\'Q13563256\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q753824\'], \'P36\': [\'Q1258998\'], \'P1889\': [\'Q128031621\'], \'P2388\': [\'Q133462575\'], \'P1343\': [\'Q1138524\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 162: Q734505 (Mauretania Caesariensis)
MERGE (n:Entity {qid: 'Q734505'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q734505',
  n.entity_id = 'concept_q734505',
  n.label = 'Mauretania Caesariensis',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 25,
  n.property_summary = '{\'P17\': [\'Q1747689\'], \'P910\': [\'Q8612294\'], \'P31\': [\'Q182547\'], \'P36\': [\'Q1309531\'], \'P30\': [\'Q15\'], \'P1365\': [\'Q309272\'], \'P1366\': [\'Q8575586\'], \'P2388\': [\'Q3716755\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 163: Q18236771 (Moesia)
MERGE (n:Entity {qid: 'Q18236771'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q18236771',
  n.entity_id = 'concept_q18236771',
  n.label = 'Moesia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 5,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P17\': [\'Q2277\'], \'P2388\': [\'Q133103218\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 164: Q3878417 (Noricum)
MERGE (n:Entity {qid: 'Q3878417'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3878417',
  n.entity_id = 'concept_q3878417',
  n.label = 'Noricum',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 16,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P361\': [\'Q875638\', \'Q2277\'], \'P1889\': [\'Q131434\'], \'P17\': [\'Q1747689\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 165: Q1247297 (Lower Pannonia)
MERGE (n:Entity {qid: 'Q1247297'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1247297',
  n.entity_id = 'concept_q1247297',
  n.label = 'Lower Pannonia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 13,
  n.property_summary = '{\'P910\': [\'Q13337932\'], \'P31\': [\'Q182547\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q170062\'], \'P1366\': [\'Q2604816\'], \'P2388\': [\'Q132452957\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 166: Q642188 (Upper Pannonia)
MERGE (n:Entity {qid: 'Q642188'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q642188',
  n.entity_id = 'concept_q642188',
  n.label = 'Upper Pannonia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 12,
  n.property_summary = '{\'P910\': [\'Q28438530\'], \'P31\': [\'Q182547\'], \'P1365\': [\'Q170062\'], \'P1366\': [\'Q6645669\'], \'P17\': [\'Q2277\'], \'P2388\': [\'Q133227152\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 167: Q156789 (Raetia)
MERGE (n:Entity {qid: 'Q156789'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q156789',
  n.entity_id = 'concept_q156789',
  n.label = 'Raetia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 45,
  n.property_summary = '{\'P31\': [\'Q1620908\', \'Q182547\'], \'P30\': [\'Q46\'], \'P138\': [\'Q685035\'], \'P910\': [\'Q9683091\'], \'P1343\': [\'Q19180675\', \'Q602358\', \'Q30059240\', \'Q1138524\', \'Q867541\'], \'P36\': [\'Q2749\'], \'P47\': [\'Q17374397\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1366\': [\'Q103122\'], \'P2388\': [\'Q133104032\', \'Q133102293\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 168: Q281345 (Corsica and Sardinia)
MERGE (n:Entity {qid: 'Q281345'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q281345',
  n.entity_id = 'concept_q281345',
  n.label = 'Corsica and Sardinia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 20,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P36\': [\'Q1897\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q486761\'], \'P3179\': [\'Q38\', \'Q142\'], \'P1001\': [\'Q1747689\'], \'P4777\': [\'Q4918\'], \'P1365\': [\'Q2429397\'], \'P1366\': [\'Q10416611\'], \'P910\': [\'Q135341302\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 169: Q691321 (Sicilia)
MERGE (n:Entity {qid: 'Q691321'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q691321',
  n.entity_id = 'concept_q691321',
  n.label = 'Sicilia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 22,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P17\': [\'Q1747689\'], \'P36\': [\'Q13670\'], \'P3179\': [\'Q38\', \'Q233\'], \'P2348\': [\'Q486761\'], \'P910\': [\'Q10179595\'], \'P1001\': [\'Q1747689\'], \'P4777\': [\'Q4918\'], \'P1365\': [\'Q2429397\'], \'P1366\': [\'Q1895939\'], \'P30\': [\'Q5401\'], \'P2388\': [\'Q132753491\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 170: Q207118 (Roman Syria)
MERGE (n:Entity {qid: 'Q207118'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q207118',
  n.entity_id = 'concept_q207118',
  n.label = 'Roman Syria',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 27,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q7036787\'], \'P17\': [\'Q1747689\'], \'P1365\': [\'Q1123749\'], \'P1366\': [\'Q27150039\', \'Q11950672\'], \'P36\': [\'Q200441\'], \'P1464\': [\'Q32755207\'], \'P1792\': [\'Q32755211\'], \'P361\': [\'Q3832489\'], \'P1889\': [\'Q1669578\'], \'P2348\': [\'Q2277\'], \'P3842\': [\'Q822\', \'Q858\', \'Q43\'], \'P2388\': [\'Q133099489\', \'Q131996867\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 171: Q27150039 (Coele-Syria)
MERGE (n:Entity {qid: 'Q27150039'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q27150039',
  n.entity_id = 'concept_q27150039',
  n.label = 'Coele-Syria',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 11,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P2348\': [\'Q1747689\'], \'P1366\': [\'Q11950671\', \'Q11950673\'], \'P1365\': [\'Q207118\'], \'P36\': [\'Q200441\'], \'P17\': [\'Q2277\'], \'P2388\': [\'Q133099766\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 172: Q635058 (Thracia)
MERGE (n:Entity {qid: 'Q635058'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q635058',
  n.entity_id = 'concept_q635058',
  n.label = 'Thracia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 22,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P276\': [\'Q41741\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P155\': [\'Q870517\'], \'P1365\': [\'Q870517\'], \'P1366\': [\'Q1491574\'], \'P2388\': [\'Q132721849\'], \'P910\': [\'Q8678371\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 173: Q913582 (Roman Italy)
MERGE (n:Entity {qid: 'Q913582'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q913582',
  n.entity_id = 'concept_q913582',
  n.label = 'Roman Italy',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 20,
  n.property_summary = '{\'P31\': [\'Q1620908\'], \'P910\': [\'Q8486424\'], \'P2184\': [\'Q56544750\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1889\': [\'Q233567\', \'Q764112\', \'Q3804110\'], \'P150\': [\'Q549800\', \'Q3931879\', \'Q767422\', \'Q1247527\', \'Q510990\'], \'P36\': [\'Q18287233\', \'Q729978\', \'Q13364\'], \'P1343\': [\'Q19219752\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 174: Q181238 (Africa)
MERGE (n:Entity {qid: 'Q181238'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q181238',
  n.entity_id = 'concept_q181238',
  n.label = 'Africa',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 41,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q8875838\'], \'P1343\': [\'Q2041543\', \'Q20078554\', \'Q602358\', \'Q19211082\', \'Q867541\'], \'P36\': [\'Q1892445\'], \'P131\': [\'Q764112\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q2429397\'], \'P1366\': [\'Q10416611\'], \'P1889\': [\'Q383824\', \'Q111740735\', \'Q622855\'], \'P2388\': [\'Q132171657\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 175: Q210718 (Asia)
MERGE (n:Entity {qid: 'Q210718'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q210718',
  n.entity_id = 'concept_q210718',
  n.label = 'Asia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 35,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q27671960\'], \'P1343\': [\'Q1138524\', \'Q20078554\', \'Q19211082\', \'Q19180675\', \'Q4086271\'], \'P17\': [\'Q2277\', \'Q17167\', \'Q12544\'], \'P36\': [\'Q47611\'], \'P131\': [\'Q1223088\'], \'P1365\': [\'Q321029\'], \'P1366\': [\'Q488230\'], \'P2388\': [\'Q131994231\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 176: Q185103 (Roman Britain)
MERGE (n:Entity {qid: 'Q185103'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q185103',
  n.entity_id = 'concept_q185103',
  n.label = 'Roman Britain',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 49,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P36\': [\'Q84\', \'Q630604\'], \'P910\': [\'Q8674467\'], \'P156\': [\'Q954585\', \'Q956451\', \'Q2578706\'], \'P1464\': [\'Q32672434\'], \'P1792\': [\'Q32672440\'], \'P361\': [\'Q2277\'], \'P1889\': [\'Q12130\', \'Q327\', \'Q18415117\'], \'P527\': [\'Q1233334\', \'Q1510781\', \'Q1355961\'], \'P131\': [\'Q1232541\'], \'P7867\': [\'Q83977448\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q435405\'], \'P1366\': [\'Q977566\', \'Q769782\'], \'P138\': [\'Q102891\'], \'P1343\': [\'Q867541\', \'Q30059240\', \'Q20078554\'], \'P2388\': [\'Q131993884\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 177: Q913382 (Bithynia et Pontus)
MERGE (n:Entity {qid: 'Q913382'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q913382',
  n.entity_id = 'concept_q913382',
  n.label = 'Bithynia et Pontus',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 21,
  n.property_summary = '{\'P910\': [\'Q28400035\'], \'P31\': [\'Q182547\'], \'P36\': [\'Q209349\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q3762571\'], \'P1366\': [\'Q1003257\', \'Q25535434\'], \'P2388\': [\'Q132027314\', \'Q133224935\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 178: Q2967757 (Cyprus)
MERGE (n:Entity {qid: 'Q2967757'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q2967757',
  n.entity_id = 'concept_q2967757',
  n.label = 'Cyprus',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 18,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P36\': [\'Q180918\'], \'P910\': [\'Q28462449\'], \'P17\': [\'Q1747689\', \'Q12544\'], \'P706\': [\'Q644636\'], \'P1365\': [\'Q2320005\'], \'P1366\': [\'Q2333703\'], \'P2388\': [\'Q131994206\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 179: Q26897 (Gallia Narbonensis)
MERGE (n:Entity {qid: 'Q26897'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q26897',
  n.entity_id = 'concept_q26897',
  n.label = 'Gallia Narbonensis',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 40,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P910\': [\'Q26926253\'], \'P1889\': [\'Q1007736\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q486761\'], \'P36\': [\'Q11938382\'], \'P206\': [\'Q4918\'], \'P1001\': [\'Q1747689\'], \'P47\': [\'Q216791\', \'Q715376\', \'Q10971\'], \'P1366\': [\'Q89702616\', \'Q89702680\', \'Q3557971\'], \'P361\': [\'Q2277\'], \'P138\': [\'Q11938382\'], \'P1343\': [\'Q867541\'], \'P2388\': [\'Q132042563\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 180: Q40169 (Assyria)
MERGE (n:Entity {qid: 'Q40169'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q40169',
  n.entity_id = 'concept_q40169',
  n.label = 'Assyria',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P1343\': [\'Q602358\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q2277\'], \'P1365\': [\'Q1986139\'], \'P1366\': [\'Q1986139\'], \'P910\': [\'Q135341395\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 181: Q11939617 (Osroene)
MERGE (n:Entity {qid: 'Q11939617'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q11939617',
  n.entity_id = 'concept_q11939617',
  n.label = 'Osroene',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 13,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P36\': [\'Q1190403\', \'Q3500626\'], \'P17\': [\'Q12544\', \'Q1747689\'], \'P131\': [\'Q1228622\'], \'P1365\': [\'Q237234\'], \'P1366\': [\'Q12490507\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 182: Q1669578 (Syria Palaestina)
MERGE (n:Entity {qid: 'Q1669578'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1669578',
  n.entity_id = 'concept_q1669578',
  n.label = 'Syria Palaestina',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 25,
  n.property_summary = '{\'P31\': [\'Q182547\'], \'P36\': [\'Q319242\'], \'P1366\': [\'Q3274024\', \'Q7126539\'], \'P1365\': [\'Q1003997\'], \'P2348\': [\'Q15843470\'], \'P3842\': [\'Q801\'], \'P1889\': [\'Q13415123\', \'Q207118\'], \'P17\': [\'Q2277\'], \'P47\': [\'Q221353\'], \'P706\': [\'Q170526\'], \'P276\': [\'Q81483\'], \'P793\': [\'Q882925\'], \'P37\': [\'Q397\'], \'P2959\': [\'Q15838109\'], \'P2388\': [\'Q3716744\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 183: Q264655 (vexillum)
MERGE (n:Entity {qid: 'Q264655'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q264655',
  n.entity_id = 'concept_q264655',
  n.label = 'vexillum',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P31\': [\'Q2912707\'], \'P279\': [\'Q249566\', \'Q806880\'], \'P1343\': [\'Q867541\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 184: Q163323 (Roman legion)
MERGE (n:Entity {qid: 'Q163323'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q163323',
  n.entity_id = 'concept_q163323',
  n.label = 'Roman legion',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 29,
  n.property_summary = '{\'P279\': [\'Q93479232\', \'Q104185420\'], \'P17\': [\'Q1747689\'], \'P910\': [\'Q8678639\', \'Q6467614\'], \'P1343\': [\'Q4086271\', \'Q4114391\', \'Q19180675\', \'Q602358\', \'Q1138524\'], \'P2354\': [\'Q1334983\'], \'P361\': [\'Q1114493\'], \'P276\': [\'Q182547\'], \'P527\': [\'Q593875\', \'Q191306\', \'Q131831810\', \'Q17346959\'], \'P1889\': [\'Q224363\'], \'P31\': [\'Q176799\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 185: Q5043 (Christianity)
MERGE (n:Entity {qid: 'Q5043'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q5043',
  n.entity_id = 'concept_q5043',
  n.label = 'Christianity',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 165,
  n.property_summary = '{\'P1151\': [\'Q8586708\'], \'P910\': [\'Q1983866\', \'Q33096581\'], \'P3095\': [\'Q106039\'], \'P2959\': [\'Q22828226\'], \'P1424\': [\'Q5881848\', \'Q6923874\'], \'P740\': [\'Q1218\'], \'P5125\': [\'Q7112229\'], \'P31\': [\'Q6957341\'], \'P112\': [\'Q302\', \'Q345\', \'Q9200\', \'Q33923\'], \'P2184\': [\'Q235329\'], \'P279\': [\'Q47280\'], \'P138\': [\'Q642420\', \'Q302\', \'Q430776\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P1343\': [\'Q19538713\', \'Q19180675\', \'Q602358\', \'Q3181656\', \'Q867541\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 186: Q29536 (paganism)
MERGE (n:Entity {qid: 'Q29536'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q29536',
  n.entity_id = 'concept_q29536',
  n.label = 'paganism',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 56,
  n.property_summary = '{\'P910\': [\'Q8708871\'], \'P527\': [\'Q2060071\'], \'P279\': [\'Q9174\'], \'P1343\': [\'Q2041543\', \'Q63284758\', \'Q3181656\', \'Q4173137\', \'Q19180675\'], \'P460\': [\'Q12371796\'], \'P31\': [\'Q49447\', \'Q110401222\', \'Q49773\', \'Q16334295\'], \'P1151\': [\'Q28012055\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 187: Q83922 (Arianism)
MERGE (n:Entity {qid: 'Q83922'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q83922',
  n.entity_id = 'concept_q83922',
  n.label = 'Arianism',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 59,
  n.property_summary = '{\'P138\': [\'Q106026\'], \'P910\': [\'Q8262933\'], \'P31\': [\'Q2728698\'], \'P1343\': [\'Q602358\', \'Q3181656\', \'Q4173137\', \'Q19211082\', \'Q19180675\'], \'P461\': [\'Q37090\'], \'P1889\': [\'Q749576\', \'Q85743247\'], \'P279\': [\'Q160598\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 188: Q42353313 (Portal:Roman Empire)
MERGE (n:Entity {qid: 'Q42353313'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q42353313',
  n.entity_id = 'concept_q42353313',
  n.label = 'Portal:Roman Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P31\': [\'Q4663903\'], \'P1204\': [\'Q2277\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 189: Q1154753 (Book of Jin)
MERGE (n:Entity {qid: 'Q1154753'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1154753',
  n.entity_id = 'concept_q1154753',
  n.label = 'Book of Jin',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 16,
  n.property_summary = '{\'P31\': [\'Q7725634\', \'Q10916116\'], \'P50\': [\'Q736647\'], \'P407\': [\'Q2016252\'], \'P495\': [\'Q9683\'], \'P361\': [\'Q175077\'], \'P747\': [\'Q28348194\'], \'P1343\': [\'Q1768721\'], \'P136\': [\'Q1619411\', \'Q11080698\'], \'P921\': [\'Q7352\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 190: Q16082057 (The New Student\'s Reference Work)
MERGE (n:Entity {qid: 'Q16082057'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16082057',
  n.entity_id = 'concept_q16082057',
  n.label = 'The New Student\\\'s Reference Work',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 11,
  n.property_summary = '{\'P98\': [\'Q5071149\', \'Q5488544\'], \'P291\': [\'Q1297\'], \'P407\': [\'Q1860\'], \'P6216\': [\'Q19652\', \'Q19652\'], \'P31\': [\'Q13136\'], \'P7937\': [\'Q5292\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 191: Q8607609 (Category:Maps of the Roman Empire)
MERGE (n:Entity {qid: 'Q8607609'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8607609',
  n.entity_id = 'concept_q8607609',
  n.label = 'Category:Maps of the Roman Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q4006\', \'Q2277\'], \'P4224\': [\'Q4006\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 192: Q178897 (Latin Empire)
MERGE (n:Entity {qid: 'Q178897'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q178897',
  n.entity_id = 'concept_q178897',
  n.label = 'Latin Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 37,
  n.property_summary = '{\'P910\': [\'Q6432187\'], \'P36\': [\'Q16869\'], \'P140\': [\'Q9592\', \'Q3333484\'], \'P1343\': [\'Q3181656\', \'Q602358\', \'Q19180675\', \'Q20078554\', \'Q124737630\'], \'P31\': [\'Q190967\', \'Q3024240\'], \'P37\': [\'Q35222\', \'Q397\'], \'P122\': [\'Q7269\'], \'P2936\': [\'Q36387\'], \'P1889\': [\'Q2277\'], \'P30\': [\'Q46\', \'Q48\'], \'P5008\': [\'Q6173448\'], \'P3075\': [\'Q9592\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 193: Q3718695 (economy of the Roman Empire)
MERGE (n:Entity {qid: 'Q3718695'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3718695',
  n.entity_id = 'concept_q3718695',
  n.label = 'economy of the Roman Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P910\': [\'Q9147799\'], \'P31\': [\'Q100773131\'], \'P276\': [\'Q2277\'], \'P17\': [\'Q1747689\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 194: Q3974187 (military history of ancient Rome)
MERGE (n:Entity {qid: 'Q3974187'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3974187',
  n.entity_id = 'concept_q3974187',
  n.label = 'military history of ancient Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 8,
  n.property_summary = '{\'P910\': [\'Q9108030\'], \'P31\': [\'Q192781\', \'Q17524420\'], \'P1269\': [\'Q368460\', \'Q1747689\'], \'P17\': [\'Q1747689\'], \'P276\': [\'Q46\', \'Q15\', \'Q48\', \'Q27527\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 195: Q16186 (Province of Imperia)
MERGE (n:Entity {qid: 'Q16186'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16186',
  n.entity_id = 'concept_q16186',
  n.label = 'Province of Imperia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 63,
  n.property_summary = '{\'P31\': [\'Q15089\'], \'P17\': [\'Q38\'], \'P36\': [\'Q13318\'], \'P47\': [\'Q3139\', \'Q15091\', \'Q16274\'], \'P131\': [\'Q1256\'], \'P6\': [\'Q3840134\', \'Q1098169\'], \'P150\': [\'Q264583\', \'Q268067\', \'Q268098\', \'Q268113\', \'Q268137\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P910\': [\'Q8270714\'], \'P1792\': [\'Q9918644\'], \'P1464\': [\'Q9229315\'], \'P1465\': [\'Q15113312\'], \'P1343\': [\'Q602358\', \'Q19219752\'], \'P166\': [\'Q15042072\'], \'P2936\': [\'Q14185\'], \'P1313\': [\'Q75026026\'], \'P1424\': [\'Q10696663\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 196: Q124737636 (Armenian Soviet Encyclopedia, vol. 9)
MERGE (n:Entity {qid: 'Q124737636'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q124737636',
  n.entity_id = 'concept_q124737636',
  n.label = 'Armenian Soviet Encyclopedia, vol. 9',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 5,
  n.property_summary = '{\'P31\': [\'Q1238720\'], \'P361\': [\'Q2657718\'], \'P407\': [\'Q8785\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 197: Q238399 (Dominate)
MERGE (n:Entity {qid: 'Q238399'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q238399',
  n.entity_id = 'concept_q238399',
  n.label = 'Dominate',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 19,
  n.property_summary = '{\'P361\': [\'Q646206\'], \'P1343\': [\'Q2657718\'], \'P31\': [\'Q1307214\', \'Q183039\', \'Q20076236\', \'Q11514315\'], \'P2596\': [\'Q1747689\'], \'P155\': [\'Q206414\'], \'P17\': [\'Q2277\'], \'P279\': [\'Q16147990\'], \'P138\': [\'Q1283380\'], \'P1889\': [\'Q2886278\'], \'P1906\': [\'Q1283380\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 198: Q787204 (High Roman Empire)
MERGE (n:Entity {qid: 'Q787204'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q787204',
  n.entity_id = 'concept_q787204',
  n.label = 'High Roman Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 14,
  n.property_summary = '{\'P361\': [\'Q2277\'], \'P156\': [\'Q2886278\'], \'P31\': [\'Q11514315\', \'Q3024240\'], \'P155\': [\'Q2815472\'], \'P279\': [\'Q16147990\'], \'P1534\': [\'Q329838\'], \'P1889\': [\'Q206414\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 199: Q2566630 (Roman Iron Age)
MERGE (n:Entity {qid: 'Q2566630'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q2566630',
  n.entity_id = 'concept_q2566630',
  n.label = 'Roman Iron Age',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 9,
  n.property_summary = '{\'P279\': [\'Q11764\'], \'P156\': [\'Q201038\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 200: Q830852 (history of ancient Rome)
MERGE (n:Entity {qid: 'Q830852'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q830852',
  n.entity_id = 'concept_q830852',
  n.label = 'history of ancient Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 12,
  n.property_summary = '{\'P361\': [\'Q41493\'], \'P31\': [\'Q17544377\'], \'P17\': [\'Q1747689\'], \'P279\': [\'Q646206\'], \'P1269\': [\'Q1747689\'], \'P1382\': [\'Q2671119\'], \'P910\': [\'Q6957668\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 201: Q1048669 (Latium)
MERGE (n:Entity {qid: 'Q1048669'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1048669',
  n.entity_id = 'concept_q1048669',
  n.label = 'Latium',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 21,
  n.property_summary = '{\'P31\': [\'Q1620908\'], \'P17\': [\'Q1747689\', \'Q38\'], \'P1343\': [\'Q30059240\', \'Q19180675\', \'Q1138524\'], \'P910\': [\'Q135341464\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 202: Q326197 (list of kings of Rome)
MERGE (n:Entity {qid: 'Q326197'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q326197',
  n.entity_id = 'concept_q326197',
  n.label = 'list of kings of Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 6,
  n.property_summary = '{\'P31\': [\'Q13406463\'], \'P360\': [\'Q55375123\'], \'P2348\': [\'Q201038\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 203: Q3921629 (First Roman Kingdom)
MERGE (n:Entity {qid: 'Q3921629'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3921629',
  n.entity_id = 'concept_q3921629',
  n.label = 'First Roman Kingdom',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 9,
  n.property_summary = '{\'P31\': [\'Q11514315\'], \'P17\': [\'Q1747689\'], \'P155\': [\'Q1247524\'], \'P361\': [\'Q201038\'], \'P156\': [\'Q119137625\'], \'P279\': [\'Q201038\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 204: Q584683 (elective monarchy)
MERGE (n:Entity {qid: 'Q584683'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q584683',
  n.entity_id = 'concept_q584683',
  n.label = 'elective monarchy',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 9,
  n.property_summary = '{\'P279\': [\'Q7269\'], \'P31\': [\'Q1307214\'], \'P910\': [\'Q20679521\'], \'P2283\': [\'Q40231\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 205: Q55375123 (King of Rome)
MERGE (n:Entity {qid: 'Q55375123'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q55375123',
  n.entity_id = 'concept_q55375123',
  n.label = 'King of Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 14,
  n.property_summary = '{\'P31\': [\'Q114962596\'], \'P279\': [\'Q12097\', \'Q6949213\'], \'P17\': [\'Q201038\'], \'P1001\': [\'Q1747689\'], \'P2348\': [\'Q201038\'], \'P2354\': [\'Q326197\'], \'P1889\': [\'Q782985\'], \'P910\': [\'Q8574422\'], \'P1308\': [\'Q2186\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 206: Q5171759 (Corniculum)
MERGE (n:Entity {qid: 'Q5171759'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q5171759',
  n.entity_id = 'concept_q5171759',
  n.label = 'Corniculum',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 14,
  n.property_summary = '{\'P17\': [\'Q38\', \'Q1747689\'], \'P31\': [\'Q15661340\', \'Q3024240\', \'Q133442\'], \'P361\': [\'Q3678593\'], \'P30\': [\'Q46\'], \'P1366\': [\'Q201038\'], \'P1343\': [\'Q1138524\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 207: Q11381903 (Portal:Rome)
MERGE (n:Entity {qid: 'Q11381903'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q11381903',
  n.entity_id = 'concept_q11381903',
  n.label = 'Portal:Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q4663903\'], \'P1204\': [\'Q220\'], \'P910\': [\'Q8682105\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 208: Q48740750 (outline of Rome)
MERGE (n:Entity {qid: 'Q48740750'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q48740750',
  n.entity_id = 'concept_q48740750',
  n.label = 'outline of Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q26884324\'], \'P17\': [\'Q38\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 209: Q10142763 (Category:People from Rome)
MERGE (n:Entity {qid: 'Q10142763'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q10142763',
  n.entity_id = 'concept_q10142763',
  n.label = 'Category:People from Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q220\', \'Q19660746\', \'Q5\'], \'P4224\': [\'Q5\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 210: Q23936560 (mayor of Rome)
MERGE (n:Entity {qid: 'Q23936560'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q23936560',
  n.entity_id = 'concept_q23936560',
  n.label = 'mayor of Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 17,
  n.property_summary = '{\'P279\': [\'Q99022939\'], \'P31\': [\'Q294414\', \'Q4164871\'], \'P2354\': [\'Q2088005\'], \'P1001\': [\'Q220\', \'Q18288160\'], \'P17\': [\'Q38\', \'Q172579\'], \'P910\': [\'Q7861393\'], \'P1308\': [\'Q948169\', \'Q23766020\'], \'P361\': [\'Q48782474\'], \'P1424\': [\'Q20372647\'], \'P1365\': [\'Q16601501\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 211: Q33923 (Saint Peter)
MERGE (n:Entity {qid: 'Q33923'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q33923',
  n.entity_id = 'concept_q33923',
  n.label = 'Saint Peter',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 168,
  n.property_summary = '{\'P39\': [\'Q19546\', \'Q43412\', \'Q865026\'], \'P31\': [\'Q5\'], \'P411\': [\'Q123110154\'], \'P20\': [\'Q18287233\'], \'P19\': [\'Q501773\'], \'P106\': [\'Q831474\', \'Q331432\', \'Q611644\'], \'P140\': [\'Q262109\'], \'P910\': [\'Q8698478\'], \'P26\': [\'Q22340337\'], \'P1038\': [\'Q23581940\'], \'P509\': [\'Q3235597\'], \'P1196\': [\'Q8454\'], \'P2348\': [\'Q787204\'], \'P3373\': [\'Q43399\'], \'P551\': [\'Q1218\', \'Q200441\', \'Q220\', \'Q59174\'], \'P119\': [\'Q2119637\'], \'P1066\': [\'Q302\'], \'P841\': [\'Q2659\'], \'P937\': [\'Q220\'], \'P1343\': [\'Q929625\', \'Q602358\', \'Q4086271\', \'Q19180675\', \'Q2041543\'], \'P361\': [\'Q4155679\'], \'P1576\': [\'Q45996\'], \'P4185\': [\'Q2546006\', \'Q2216236\', \'Q1063103\', \'Q111843053\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 212: Q9200 (Paul the Apostle)
MERGE (n:Entity {qid: 'Q9200'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q9200',
  n.entity_id = 'concept_q9200',
  n.label = 'Paul the Apostle',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 213,
  n.property_summary = '{\'P21\': [\'Q6581097\'], \'P19\': [\'Q134287\'], \'P140\': [\'Q26403\', \'Q5043\'], \'P841\': [\'Q2659\', \'Q2688\', \'Q2325\', \'Q2279\', \'Q3027\'], \'P31\': [\'Q5\'], \'P910\': [\'Q7336863\'], \'P411\': [\'Q123110154\', \'Q43412\'], \'P20\': [\'Q220\'], \'P106\': [\'Q36180\', \'Q1234713\', \'Q219477\', \'Q4504549\', \'Q133485\'], \'P735\': [\'Q9302723\', \'Q4391614\'], \'P27\': [\'Q1747689\'], \'P39\': [\'Q43412\'], \'P1343\': [\'Q21065550\', \'Q602358\', \'Q19180675\', \'Q4086271\', \'Q929625\'], \'P2348\': [\'Q787204\'], \'P1412\': [\'Q35497\', \'Q9288\', \'Q107358\', \'Q397\'], \'P737\': [\'Q310584\', \'Q302\'], \'P509\': [\'Q204933\'], \'P793\': [\'Q901397\', \'Q6014567\'], \'P1576\': [\'Q45996\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 213: Q22665612 (Q22665612)
MERGE (n:Entity {qid: 'Q22665612'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q22665612',
  n.entity_id = 'concept_q22665612',
  n.label = 'Q22665612',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P31\': [\'Q21286738\'], \'P2959\': [\'Q220\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 214: Q18288160 (Metropolitan City of Rome)
MERGE (n:Entity {qid: 'Q18288160'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q18288160',
  n.entity_id = 'place_q18288160',
  n.label = 'Metropolitan City of Rome',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 48,
  n.property_summary = '{\'P31\': [\'Q15110\', \'Q15089\'], \'P17\': [\'Q38\'], \'P131\': [\'Q1282\'], \'P47\': [\'Q16318\', \'Q16267\', \'Q16189\', \'Q16181\', \'Q16196\'], \'P36\': [\'Q220\'], \'P910\': [\'Q20933370\'], \'P1365\': [\'Q15119\'], \'P1792\': [\'Q6457043\'], \'P1464\': [\'Q15223994\'], \'P1465\': [\'Q9221315\'], \'P463\': [\'Q1768108\'], \'P2936\': [\'Q652\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P1313\': [\'Q99293558\'], \'P194\': [\'Q130410342\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 215: Q38 (Italy)
MERGE (n:Entity {qid: 'Q38'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q38',
  n.entity_id = 'concept_q38',
  n.label = 'Italy',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 369,
  n.property_summary = '{\'P1151\': [\'Q10631821\'], \'P5125\': [\'Q7112307\'], \'P38\': [\'Q4916\', \'Q204992\'], \'P1792\': [\'Q3919890\'], \'P2852\': [\'Q1061257\', \'Q25648804\', \'Q25648805\', \'Q11185210\'], \'P2853\': [\'Q1378312\', \'Q1123613\', \'Q1520890\'], \'P2633\': [\'Q216989\'], \'P1313\': [\'Q796897\'], \'P417\': [\'Q676555\', \'Q229190\'], \'P2959\': [\'Q20820609\', \'Q30277415\'], \'P122\': [\'Q4198907\', \'Q179164\'], \'P832\': [\'Q196627\', \'Q132001\', \'Q209663\', \'Q2851732\', \'Q47499\'], \'P1552\': [\'Q3174312\'], \'P30\': [\'Q46\', \'Q15\'], \'P530\': [\'Q222\', \'Q228\', \'Q184\', \'Q31\', \'Q225\'], \'P1906\': [\'Q332711\'], \'P194\': [\'Q1117578\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 216: Q1282 (Lazio)
MERGE (n:Entity {qid: 'Q1282'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1282',
  n.entity_id = 'concept_q1282',
  n.label = 'Lazio',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 107,
  n.property_summary = '{\'P31\': [\'Q16110\'], \'P17\': [\'Q38\'], \'P36\': [\'Q220\'], \'P47\': [\'Q1273\', \'Q1280\', \'Q1279\', \'Q1284\', \'Q1443\'], \'P131\': [\'Q38\', \'Q172579\'], \'P150\': [\'Q16181\', \'Q16196\', \'Q16267\', \'Q15119\', \'Q16318\'], \'P6\': [\'Q1332769\'], \'P194\': [\'Q3687387\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P910\': [\'Q7215077\'], \'P1464\': [\'Q8060922\'], \'P1465\': [\'Q9221408\'], \'P190\': [\'Q5776\'], \'P1740\': [\'Q6468971\'], \'P1792\': [\'Q7234704\'], \'P2633\': [\'Q3760257\'], \'P417\': [\'Q33923\', \'Q9200\'], \'P1151\': [\'Q11042266\'], \'P361\': [\'Q1127320\'], \'P1313\': [\'Q16976470\'], \'P208\': [\'Q30888445\'], \'P1791\': [\'Q8328642\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 217: Q170174 (Papal States)
MERGE (n:Entity {qid: 'Q170174'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q170174',
  n.entity_id = 'concept_q170174',
  n.label = 'Papal States',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 81,
  n.property_summary = '{\'P36\': [\'Q220\'], \'P910\': [\'Q7098253\'], \'P122\': [\'Q584683\', \'Q4055127\'], \'P85\': [\'Q3774332\'], \'P38\': [\'Q1403484\', \'Q2274312\'], \'P140\': [\'Q9592\'], \'P31\': [\'Q3024240\', \'Q3624078\', \'Q10551526\', \'Q44405\', \'Q107230986\'], \'P156\': [\'Q172579\', \'Q1788988\'], \'P155\': [\'Q1788988\'], \'P1343\': [\'Q678259\', \'Q3181656\', \'Q602358\', \'Q19180675\', \'Q867541\'], \'P17\': [\'Q170174\'], \'P706\': [\'Q145694\'], \'P1366\': [\'Q237\', \'Q1788988\', \'Q1072140\'], \'P37\': [\'Q397\'], \'P1464\': [\'Q20804499\'], \'P30\': [\'Q46\'], \'P47\': [\'Q131964\', \'Q252580\', \'Q238\', \'Q180393\'], \'P1830\': [\'Q3437427\'], \'P2936\': [\'Q397\', \'Q1231625\', \'Q652\'], \'P3075\': [\'Q9592\'], \'P1365\': [\'Q1072140\', \'Q2393278\', \'Q2829270\', \'Q3968612\', \'Q106396892\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 218: Q3528124 (Tibre)
MERGE (n:Entity {qid: 'Q3528124'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3528124',
  n.entity_id = 'concept_q3528124',
  n.label = 'Tibre',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 10,
  n.property_summary = '{\'P17\': [\'Q175881\'], \'P31\': [\'Q6465\'], \'P36\': [\'Q220\'], \'P138\': [\'Q13712\'], \'P131\': [\'Q142\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 219: Q172579 (Kingdom of Italy)
MERGE (n:Entity {qid: 'Q172579'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q172579',
  n.entity_id = 'concept_q172579',
  n.label = 'Kingdom of Italy',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 59,
  n.property_summary = '{\'P122\': [\'Q41614\', \'Q3330103\', \'Q50686\', \'Q6229\', \'Q317\'], \'P35\': [\'Q168691\', \'Q153688\', \'Q150642\', \'Q187149\'], \'P155\': [\'Q165154\', \'Q180393\', \'Q209857\', \'Q170174\', \'Q131964\'], \'P156\': [\'Q38\'], \'P31\': [\'Q3624078\', \'Q3024240\', \'Q20181813\'], \'P1365\': [\'Q268970\', \'Q6006584\', \'Q548114\', \'Q180393\', \'Q2577303\'], \'P910\': [\'Q8574257\'], \'P36\': [\'Q495\', \'Q2044\', \'Q220\'], \'P237\': [\'Q199432\'], \'P163\': [\'Q42876\'], \'P38\': [\'Q204992\'], \'P37\': [\'Q652\'], \'P47\': [\'Q176495\', \'Q518101\', \'Q1277557\', \'Q28513\', \'Q131964\'], \'P30\': [\'Q46\'], \'P361\': [\'Q215669\', \'Q153867\'], \'P1366\': [\'Q38\'], \'P1344\': [\'Q65132216\', \'Q989115\', \'Q94916\'], \'P3075\': [\'Q1841\'], \'P2936\': [\'Q652\'], \'P463\': [\'Q38130\'], \'P793\': [\'Q3922436\'], \'P1889\': [\'Q1098499\'], \'P1464\': [\'Q111043177\'], \'P85\': [\'Q599517\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 220: Q3940419 (Roma Capitale)
MERGE (n:Entity {qid: 'Q3940419'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3940419',
  n.entity_id = 'concept_q3940419',
  n.label = 'Roma Capitale',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 25,
  n.property_summary = '{\'P131\': [\'Q18288160\', \'Q15119\'], \'P17\': [\'Q38\'], \'P31\': [\'Q3726248\', \'Q56061\'], \'P355\': [\'Q530087\', \'Q3631446\', \'Q3604235\', \'Q3940432\', \'Q30284569\'], \'P421\': [\'Q6655\', \'Q6723\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 221: Q1072140 (Roman Republic)
MERGE (n:Entity {qid: 'Q1072140'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1072140',
  n.entity_id = 'concept_q1072140',
  n.label = 'Roman Republic',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 46,
  n.property_summary = '{\'P85\': [\'Q187\'], \'P31\': [\'Q10711424\', \'Q10931\', \'Q99541706\', \'Q180684\'], \'P706\': [\'Q145694\'], \'P1365\': [\'Q170174\'], \'P1366\': [\'Q170174\'], \'P910\': [\'Q9246785\'], \'P17\': [\'Q1072140\'], \'P37\': [\'Q652\'], \'P38\': [\'Q1403484\'], \'P122\': [\'Q4198907\', \'Q2523556\'], \'P36\': [\'Q220\'], \'P30\': [\'Q46\'], \'P1889\': [\'Q346629\'], \'P237\': [\'Q199432\'], \'P163\': [\'Q42876\'], \'P828\': [\'Q137690829\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 222: Q134317926 (Italian State)
MERGE (n:Entity {qid: 'Q134317926'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q134317926',
  n.entity_id = 'concept_q134317926',
  n.label = 'Italian State',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 7,
  n.property_summary = '{\'P31\': [\'Q7275\'], \'P36\': [\'Q220\'], \'P1269\': [\'Q38\'], \'P17\': [\'Q38\'], \'P1001\': [\'Q38\'], \'P527\': [\'Q3773971\', \'Q1117578\', \'Q1135541\', \'Q349511\', \'Q1969510\'], \'P1830\': [\'Q55083048\', \'Q2219248\', \'Q134318865\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 223: Q15119 (Province of Rome)
MERGE (n:Entity {qid: 'Q15119'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q15119',
  n.entity_id = 'concept_q15119',
  n.label = 'Province of Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 72,
  n.property_summary = '{\'P17\': [\'Q38\'], \'P31\': [\'Q3924474\'], \'P36\': [\'Q220\'], \'P47\': [\'Q16318\', \'Q16267\', \'Q16189\', \'Q16181\', \'Q16196\'], \'P131\': [\'Q1282\'], \'P150\': [\'Q239180\', \'Q241659\', \'Q191115\', \'Q241680\', \'Q241693\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P910\': [\'Q8803633\'], \'P1740\': [\'Q10211870\'], \'P1366\': [\'Q18288160\'], \'P361\': [\'Q1282\'], \'P1792\': [\'Q6457043\'], \'P1464\': [\'Q15223994\'], \'P1465\': [\'Q9221315\'], \'P1343\': [\'Q602358\', \'Q4532138\', \'Q867541\', \'Q19219752\'], \'P2936\': [\'Q1057898\'], \'P1313\': [\'Q73777520\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 224: Q42834 (Western Roman Empire)
MERGE (n:Entity {qid: 'Q42834'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q42834',
  n.entity_id = 'concept_q42834',
  n.label = 'Western Roman Empire',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 60,
  n.property_summary = '{\'P31\': [\'Q48349\', \'Q3024240\', \'Q56061\'], \'P910\': [\'Q8913343\'], \'P140\': [\'Q5043\'], \'P36\': [\'Q729978\', \'Q115738657\', \'Q13364\'], \'P122\': [\'Q173424\', \'Q7269\', \'Q238399\'], \'P194\': [\'Q3510883\'], \'P38\': [\'Q952064\'], \'P1366\': [\'Q146246\', \'Q3755547\', \'Q3307686\', \'Q12544\', \'Q1048918\'], \'P1343\': [\'Q2041543\', \'Q3181656\'], \'P37\': [\'Q397\'], \'P30\': [\'Q46\'], \'P2936\': [\'Q397\'], \'P3075\': [\'Q5043\'], \'P1365\': [\'Q2277\'], \'P17\': [\'Q2277\'], \'P47\': [\'Q12544\'], \'P2388\': [\'Q111841409\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 225: Q3677829 (circle of Rome)
MERGE (n:Entity {qid: 'Q3677829'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3677829',
  n.entity_id = 'concept_q3677829',
  n.label = 'circle of Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 7,
  n.property_summary = '{\'P31\': [\'Q3677604\'], \'P17\': [\'Q172579\'], \'P131\': [\'Q15119\'], \'P36\': [\'Q220\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 226: Q1200427 (culture of ancient Rome)
MERGE (n:Entity {qid: 'Q1200427'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1200427',
  n.entity_id = 'concept_q1200427',
  n.label = 'culture of ancient Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 14,
  n.property_summary = '{\'P910\': [\'Q7151915\'], \'P31\': [\'Q19958368\', \'Q11514315\', \'Q1292119\', \'Q11042\'], \'P6379\': [\'Q239303\'], \'P1269\': [\'Q1747689\'], \'P279\': [\'Q13152690\'], \'P17\': [\'Q1747689\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 227: Q3678788 (Byzantine civilization)
MERGE (n:Entity {qid: 'Q3678788'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3678788',
  n.entity_id = 'concept_q3678788',
  n.label = 'Byzantine civilization',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P31\': [\'Q465299\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 228: Q13712 (Tiber)
MERGE (n:Entity {qid: 'Q13712'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q13712',
  n.entity_id = 'concept_q13712',
  n.label = 'Tiber',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 69,
  n.property_summary = '{\'P31\': [\'Q4022\'], \'P17\': [\'Q38\'], \'P30\': [\'Q46\'], \'P403\': [\'Q38882\'], \'P910\': [\'Q9140778\'], \'P1200\': [\'Q8956808\'], \'P469\': [\'Q2881830\'], \'P974\': [\'Q1071692\', \'Q932761\', \'Q546600\', \'Q1139578\', \'Q33473\'], \'P1343\': [\'Q30059240\', \'Q602358\', \'Q3181656\', \'Q867541\'], \'P205\': [\'Q38\'], \'P1889\': [\'Q17252\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 229: Q38882 (Tyrrhenian Sea)
MERGE (n:Entity {qid: 'Q38882'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q38882',
  n.entity_id = 'concept_q38882',
  n.label = 'Tyrrhenian Sea',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 5,
  n.properties_count = 61,
  n.property_summary = '{\'P31\': [\'Q165\'], \'P361\': [\'Q6008933\'], \'P910\': [\'Q9147404\'], \'P1343\': [\'Q602358\', \'Q19180675\', \'Q30059240\', \'Q35541239\', \'Q30059240\'], \'P205\': [\'Q142\', \'Q38\'], \'P4330\': [\'Q1462\', \'Q14112\', \'Q4951156\', \'Q212203\'], \'P4614\': [\'Q84427820\'], \'P1465\': [\'Q104404651\'], \'P17\': [\'Q38\'], \'P200\': [\'Q13712\', \'Q572191\', \'Q1223308\', \'Q691596\', \'Q1243685\'], \'P5008\': [\'Q6173448\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 230: Q583038 (Ostrogothic Kingdom)
MERGE (n:Entity {qid: 'Q583038'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q583038',
  n.entity_id = 'concept_q583038',
  n.label = 'Ostrogothic Kingdom',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 25,
  n.property_summary = '{\'P140\': [\'Q83922\'], \'P36\': [\'Q115738657\', \'Q6259\', \'Q13364\'], \'P31\': [\'Q3024240\', \'Q1371288\', \'Q3446291\'], \'P910\': [\'Q9061376\'], \'P122\': [\'Q7269\'], \'P37\': [\'Q397\', \'Q35722\'], \'P1365\': [\'Q3755547\'], \'P2936\': [\'Q397\', \'Q35722\'], \'P3075\': [\'Q83922\'], \'P1366\': [\'Q1152508\', \'Q848383\'], \'P30\': [\'Q46\'], \'P1343\': [\'Q602358\'], \'P2388\': [\'Q22953196\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 231: Q237 (Vatican City)
MERGE (n:Entity {qid: 'Q237'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q237',
  n.entity_id = 'place_q237',
  n.label = 'Vatican City',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 255,
  n.property_summary = '{\'P38\': [\'Q4916\', \'Q183354\'], \'P85\': [\'Q190226\'], \'P30\': [\'Q46\'], \'P78\': [\'Q42381\'], \'P138\': [\'Q1053000\'], \'P47\': [\'Q38\', \'Q458\'], \'P35\': [\'Q450675\', \'Q2494\', \'Q989\', \'Q37278\', \'Q23873\'], \'P31\': [\'Q3624078\', \'Q133442\', \'Q171441\', \'Q123480\', \'Q570116\'], \'P122\': [\'Q44405\', \'Q584683\', \'Q184558\', \'Q4055127\', \'Q41614\'], \'P163\': [\'Q79198\'], \'P194\': [\'Q7478146\'], \'P463\': [\'Q17495\', \'Q8475\', \'Q376150\'], \'P501\': [\'Q220\', \'Q38\'], \'P910\': [\'Q1411544\'], \'P421\': [\'Q25989\', \'Q6655\', \'Q109522221\'], \'P237\': [\'Q200198\'], \'P610\': [\'Q1053000\'], \'P1465\': [\'Q8365665\'], \'P1151\': [\'Q7240296\'], \'P1740\': [\'Q10208993\'], \'P1791\': [\'Q8328826\'], \'P1792\': [\'Q6993516\'], \'P1435\': [\'Q9259\', \'Q26086651\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 232: Q90 (Paris)
MERGE (n:Entity {qid: 'Q90'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q90',
  n.entity_id = 'concept_q90',
  n.label = 'Paris',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 317,
  n.property_summary = '{\'P1151\': [\'Q8253667\'], \'P1792\': [\'Q8964470\'], \'P1313\': [\'Q12371988\', \'Q1465786\'], \'P417\': [\'Q235863\'], \'P17\': [\'Q142\', \'Q70972\', \'Q146246\', \'Q2748708\', \'Q142\'], \'P1424\': [\'Q18220037\'], \'P1376\': [\'Q142\', \'Q13917\', \'Q70972\', \'Q71092\', \'Q106577\'], \'P868\': [\'Q21129738\'], \'P2184\': [\'Q845625\'], \'P206\': [\'Q1471\', \'Q810526\', \'Q860172\', \'Q1032646\'], \'P1456\': [\'Q1403319\', \'Q3252156\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P190\': [\'Q220\', \'Q1490\', \'Q34600\', \'Q64\', \'Q158119\'], \'P1365\': [\'Q270273\', \'Q124881945\'], \'P30\': [\'Q46\'], \'P237\': [\'Q1925366\'], \'P166\': [\'Q2727598\', \'Q2990283\', \'Q10855271\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 233: Q31487 (Kraków)
MERGE (n:Entity {qid: 'Q31487'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q31487',
  n.entity_id = 'place_q31487',
  n.label = 'Kraków',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 170,
  n.property_summary = '{\'P1151\': [\'Q13220232\'], \'P6\': [\'Q179502\', \'Q4759655\', \'Q11730701\', \'Q11749071\', \'Q3157086\'], \'P17\': [\'Q36\', \'Q156111\', \'Q207272\', \'Q688918\', \'Q501303\'], \'P31\': [\'Q925381\', \'Q1549591\', \'Q707813\', \'Q1200957\', \'Q129268952\'], \'P131\': [\'Q54159\', \'Q11825637\', \'Q9377184\', \'Q9377185\', \'Q6435962\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P910\': [\'Q6921577\'], \'P190\': [\'Q68965\', \'Q1794\', \'Q216\', \'Q1479\', \'Q1780\'], \'P1464\': [\'Q9887936\'], \'P1465\': [\'Q9911242\'], \'P1740\': [\'Q8458138\'], \'P1792\': [\'Q6582149\'], \'P1376\': [\'Q54159\', \'Q172107\', \'Q1164890\', \'Q1649871\', \'Q156111\'], \'P1343\': [\'Q19538713\', \'Q19180675\', \'Q602358\', \'Q4173137\', \'Q4114391\'], \'P206\': [\'Q548\'], \'P30\': [\'Q46\'], \'P1313\': [\'Q13647765\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 234: Q43196 (Cincinnati)
MERGE (n:Entity {qid: 'Q43196'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q43196',
  n.entity_id = 'place_q43196',
  n.label = 'Cincinnati',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 129,
  n.property_summary = '{\'P190\': [\'Q192225\', \'Q40898\', \'Q1726\', \'Q10086\', \'Q45798\'], \'P1151\': [\'Q11240582\'], \'P17\': [\'Q30\'], \'P131\': [\'Q152891\'], \'P163\': [\'Q5456721\'], \'P31\': [\'Q1549591\', \'Q1093829\', \'Q62049\', \'Q108569710\'], \'P910\': [\'Q8371907\'], \'P1464\': [\'Q8078460\'], \'P1465\': [\'Q9218063\'], \'P138\': [\'Q1632484\'], \'P1792\': [\'Q7115063\'], \'P1376\': [\'Q152891\'], \'P6\': [\'Q6227508\', \'Q43373558\'], \'P2184\': [\'Q12060208\', \'Q7805686\'], \'P206\': [\'Q4915\'], \'P1830\': [\'Q153824\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 235: Q132830 (Douala)
MERGE (n:Entity {qid: 'Q132830'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q132830',
  n.entity_id = 'place_q132830',
  n.label = 'Douala',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 70,
  n.property_summary = '{\'P1464\': [\'Q8053002\'], \'P190\': [\'Q1345\', \'Q209905\', \'Q220\', \'Q546\', \'Q3935\'], \'P131\': [\'Q769841\', \'Q845172\'], \'P17\': [\'Q1009\'], \'P31\': [\'Q2264924\', \'Q1549591\'], \'P910\': [\'Q8388734\'], \'P1465\': [\'Q18289577\'], \'P1792\': [\'Q7912863\'], \'P1376\': [\'Q668294\', \'Q845172\', \'Q769841\'], \'P421\': [\'Q6655\'], \'P206\': [\'Q1405842\'], \'P7867\': [\'Q84057252\'], \'P8989\': [\'Q104595679\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 236: Q484799 (Marbella)
MERGE (n:Entity {qid: 'Q484799'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q484799',
  n.entity_id = 'concept_q484799',
  n.label = 'Marbella',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 77,
  n.property_summary = '{\'P17\': [\'Q29\'], \'P31\': [\'Q2074737\'], \'P131\': [\'Q95028\'], \'P6\': [\'Q6173697\'], \'P190\': [\'Q53081\', \'Q25475\', \'Q202445\', \'Q3861\', \'Q374365\'], \'P910\': [\'Q8607934\'], \'P1464\': [\'Q15075680\'], \'P1465\': [\'Q9219021\'], \'P1792\': [\'Q7920012\'], \'P47\': [\'Q816672\', \'Q492748\', \'Q944160\', \'Q492744\', \'Q1630419\'], \'P206\': [\'Q4918\'], \'P1313\': [\'Q26698295\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P1376\': [\'Q2997038\'], \'P1889\': [\'Q57559439\'], \'P7867\': [\'Q84037697\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 237: Q1819965 (Achacachi Municipality)
MERGE (n:Entity {qid: 'Q1819965'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1819965',
  n.entity_id = 'concept_q1819965',
  n.label = 'Achacachi Municipality',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 16,
  n.property_summary = '{\'P31\': [\'Q1062710\'], \'P17\': [\'Q750\'], \'P131\': [\'Q951271\'], \'P190\': [\'Q220\'], \'P1889\': [\'Q1553175\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 238: Q1490 (Tokyo)
MERGE (n:Entity {qid: 'Q1490'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1490',
  n.entity_id = 'concept_q1490',
  n.label = 'Tokyo',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 223,
  n.property_summary = '{\'P31\': [\'Q124313007\', \'Q1025961\', \'Q1200957\', \'Q200250\', \'Q208511\'], \'P150\': [\'Q213464\', \'Q232624\', \'Q212713\', \'Q214051\', \'Q212704\'], \'P527\': [\'Q1323122\', \'Q7473516\', \'Q1074185\', \'Q308891\', \'Q1138596\'], \'P47\': [\'Q80011\', \'Q128186\', \'Q132720\', \'Q127513\'], \'P6\': [\'Q389617\', \'Q1280894\', \'Q38849\', \'Q3119116\', \'Q3482657\'], \'P421\': [\'Q909085\'], \'P17\': [\'Q17\'], \'P190\': [\'Q64\', \'Q60\', \'Q3224\', \'Q3630\', \'Q8684\'], \'P910\': [\'Q9542407\'], \'P1464\': [\'Q8075578\'], \'P1465\': [\'Q9220173\'], \'P1792\': [\'Q6748064\'], \'P1376\': [\'Q696251\', \'Q17\', \'Q188712\'], \'P131\': [\'Q17\', \'Q132480\'], \'P194\': [\'Q7813951\'], \'P208\': [\'Q1074185\'], \'P163\': [\'Q20900820\'], \'P1889\': [\'Q355898\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 239: Q8717 (Seville)
MERGE (n:Entity {qid: 'Q8717'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8717',
  n.entity_id = 'concept_q8717',
  n.label = 'Seville',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 146,
  n.property_summary = '{\'P17\': [\'Q29\', \'Q276951\'], \'P6\': [\'Q5949284\'], \'P131\': [\'Q95088\', \'Q1796239\', \'Q3849062\'], \'P163\': [\'Q83989\'], \'P237\': [\'Q2843986\'], \'P190\': [\'Q38380\', \'Q53081\', \'Q35004\', \'Q1492\', \'Q1486\'], \'P47\': [\'Q494781\', \'Q904151\', \'Q752127\', \'Q63092\', \'Q489205\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P910\': [\'Q8733566\'], \'P1464\': [\'Q8072109\'], \'P1465\': [\'Q14331347\'], \'P1740\': [\'Q10220313\'], \'P1792\': [\'Q7117921\'], \'P1376\': [\'Q5783\', \'Q1796239\', \'Q95088\', \'Q199688\', \'Q2655584\'], \'P2184\': [\'Q3136820\'], \'P1313\': [\'Q26274423\'], \'P1791\': [\'Q8328770\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 240: Q13437 (Benevento)
MERGE (n:Entity {qid: 'Q13437'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q13437',
  n.entity_id = 'concept_q13437',
  n.label = 'Benevento',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 105,
  n.property_summary = '{\'P1464\': [\'Q8045870\'], \'P17\': [\'Q38\'], \'P131\': [\'Q16134\'], \'P47\': [\'Q55849\', \'Q55889\', \'Q55908\', \'Q55935\', \'Q55946\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P910\': [\'Q6625548\'], \'P31\': [\'Q747074\'], \'P190\': [\'Q5776\', \'Q2634\', \'Q72712\', \'Q72425\', \'Q4656\'], \'P1465\': [\'Q9217664\'], \'P1792\': [\'Q8727689\'], \'P1343\': [\'Q678259\', \'Q20078554\', \'Q30059240\', \'Q602358\', \'Q19180675\'], \'P1376\': [\'Q16134\', \'Q1036791\'], \'P6\': [\'Q1394911\'], \'P206\': [\'Q857589\'], \'P166\': [\'Q48624858\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 241: Q8684 (Seoul)
MERGE (n:Entity {qid: 'Q8684'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q8684',
  n.entity_id = 'place_q8684',
  n.label = 'Seoul',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 205,
  n.property_summary = '{\'P910\': [\'Q6400933\'], \'P6\': [\'Q22803\', \'Q14342\', \'Q494239\', \'Q494239\', \'Q380681\'], \'P1792\': [\'Q6820565\'], \'P1313\': [\'Q488289\'], \'P1740\': [\'Q7925549\'], \'P1830\': [\'Q16171281\', \'Q17469\', \'Q17503\', \'Q75330\', \'Q100852\'], \'P17\': [\'Q884\', \'Q503585\'], \'P1376\': [\'Q884\', \'Q28179\', \'Q28278\', \'Q484104\', \'Q28233\'], \'P2184\': [\'Q494780\', \'Q7805915\'], \'P47\': [\'Q20937\', \'Q20934\'], \'P1464\': [\'Q9227354\'], \'P194\': [\'Q12601388\'], \'P421\': [\'Q7041\'], \'P190\': [\'Q62\', \'Q85\', \'Q3630\', \'Q987\', \'Q1867\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 242: Q3689056 (Contrada della Lupa)
MERGE (n:Entity {qid: 'Q3689056'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q3689056',
  n.entity_id = 'concept_q3689056',
  n.label = 'Contrada della Lupa',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 22,
  n.property_summary = '{\'P31\': [\'Q1231729\'], \'P17\': [\'Q38\'], \'P131\': [\'Q2751\'], \'P190\': [\'Q220\'], \'P138\': [\'Q408623\'], \'P417\': [\'Q152457\'], \'P361\': [\'Q62366962\'], \'P47\': [\'Q3877596\', \'Q3689047\', \'Q3689045\'], \'P2238\': [\'Q2028376\', \'Q55386956\'], \'P2522\': [\'Q940390\', \'Q940390\'], \'P1830\': [\'Q55386956\'], \'P6364\': [\'Q23444\', \'Q23445\', \'Q39338\'], \'P421\': [\'Q6655\', \'Q6723\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 243: Q459 (Plovdiv)
MERGE (n:Entity {qid: 'Q459'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q459',
  n.entity_id = 'place_q459',
  n.label = 'Plovdiv',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 112,
  n.property_summary = '{\'P190\': [\'Q2079\', \'Q374365\', \'Q40738\', \'Q192606\', \'Q5788\'], \'P131\': [\'Q4365146\'], \'P31\': [\'Q129676344\', \'Q15303838\', \'Q15344922\', \'Q89487741\'], \'P910\': [\'Q7345207\'], \'P1465\': [\'Q10023446\'], \'P1464\': [\'Q8068309\'], \'P1792\': [\'Q8745954\'], \'P1376\': [\'Q187874\', \'Q4365146\', \'Q1500386\', \'Q162565\'], \'P1343\': [\'Q2041543\', \'Q602358\', \'Q19180675\', \'Q4532138\', \'Q4173137\'], \'P206\': [\'Q204347\'], \'P421\': [\'Q6723\', \'Q6760\'], \'P6\': [\'Q12281254\', \'Q123582957\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 244: Q61 (Washington, D.C.)
MERGE (n:Entity {qid: 'Q61'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q61',
  n.entity_id = 'place_q61',
  n.label = 'Washington, D.C.',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 253,
  n.property_summary = '{\'P17\': [\'Q30\'], \'P47\': [\'Q107126\', \'Q88\', \'Q26807\', \'Q488659\', \'Q341915\'], \'P1151\': [\'Q11242630\'], \'P31\': [\'Q1093829\', \'Q1549591\', \'Q486972\', \'Q15840617\', \'Q114496982\'], \'P131\': [\'Q3551781\'], \'P138\': [\'Q23\', \'Q7322\'], \'P30\': [\'Q49\'], \'P190\': [\'Q240\', \'Q1861\', \'Q3718\', \'Q956\', \'Q1524\'], \'P163\': [\'Q906340\'], \'P910\': [\'Q8166193\'], \'P1464\': [\'Q8048367\'], \'P1465\': [\'Q8365674\'], \'P1740\': [\'Q7237299\'], \'P1791\': [\'Q7975332\'], \'P1792\': [\'Q8753221\'], \'P421\': [\'Q941023\', \'Q5390\', \'Q5762\', \'Q28146035\'], \'P1343\': [\'Q302556\', \'Q2041543\', \'Q602358\', \'Q4173137\', \'Q19180675\'], \'P1376\': [\'Q30\', \'Q3551781\'], \'P2184\': [\'Q685093\', \'Q22026116\'], \'P206\': [\'Q179444\', \'Q483607\', \'Q2352739\'], \'P2633\': [\'Q5535257\'], \'P3403\': [\'Q3551781\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 245: Q2844 (Brasília)
MERGE (n:Entity {qid: 'Q2844'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q2844',
  n.entity_id = 'place_q2844',
  n.label = 'Brasília',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 133,
  n.property_summary = '{\'P190\': [\'Q1486\', \'Q1963\', \'Q5826\', \'Q597\', \'Q727\'], \'P17\': [\'Q155\'], \'P31\': [\'Q1549591\', \'Q515\', \'Q15840617\', \'Q114496982\', \'Q257391\'], \'P910\': [\'Q7484924\'], \'P131\': [\'Q119158\'], \'P421\': [\'Q6513\'], \'P1464\': [\'Q9229004\'], \'P1465\': [\'Q9686029\'], \'P1740\': [\'Q13262406\'], \'P1792\': [\'Q7115378\'], \'P84\': [\'Q1497375\'], \'P1376\': [\'Q155\', \'Q210542\', \'Q119158\'], \'P206\': [\'Q3432578\', \'Q2627794\'], \'P138\': [\'Q155\'], \'P417\': [\'Q146183\', \'Q2469225\'], \'P463\': [\'Q4005967\', \'Q1139352\', \'Q734958\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 246: Q956 (Beijing)
MERGE (n:Entity {qid: 'Q956'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q956',
  n.entity_id = 'place_q956',
  n.label = 'Beijing',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 189,
  n.property_summary = '{\'P1151\': [\'Q11379090\'], \'P17\': [\'Q148\', \'Q13426199\', \'Q696242\', \'Q704714\', \'Q13426199\'], \'P47\': [\'Q21208\', \'Q11736\', \'Q58710\', \'Q58584\', \'Q58650\'], \'P6\': [\'Q28417331\'], \'P150\': [\'Q394681\', \'Q30138\', \'Q394701\', \'Q393831\', \'Q393475\'], \'P210\': [\'Q3370201\', \'Q19825407\'], \'P131\': [\'Q148\', \'Q7313\', \'Q8733\', \'Q9903\'], \'P190\': [\'Q64\', \'Q85\', \'Q23661\', \'Q1761\', \'Q19689\'], \'P208\': [\'Q10902215\'], \'P910\': [\'Q7132800\'], \'P421\': [\'Q6985\'], \'P1464\': [\'Q18057881\'], \'P1465\': [\'Q6482278\'], \'P1740\': [\'Q6548000\'], \'P1792\': [\'Q6483370\'], \'P1376\': [\'Q148\', \'Q12060881\', \'Q56271505\', \'Q175379\', \'Q13426199\'], \'P2633\': [\'Q5535122\'], \'P2959\': [\'Q22828410\'], \'P1313\': [\'Q17279086\'], \'P610\': [\'Q10870769\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 247: Q1489 (Mexico City)
MERGE (n:Entity {qid: 'Q1489'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q1489',
  n.entity_id = 'place_q1489',
  n.label = 'Mexico City',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 198,
  n.property_summary = '{\'P237\': [\'Q1947763\'], \'P190\': [\'Q1863\', \'Q1524\', \'Q159273\', \'Q956\', \'Q3820\'], \'P31\': [\'Q20528428\', \'Q1549591\', \'Q515\', \'Q200250\', \'Q51929311\'], \'P17\': [\'Q96\'], \'P421\': [\'Q5385\', \'Q2086913\'], \'P131\': [\'Q285658\', \'Q170603\', \'Q96\'], \'P910\': [\'Q6579509\'], \'P194\': [\'Q2867085\'], \'P1464\': [\'Q9224233\'], \'P1465\': [\'Q9218076\'], \'P1740\': [\'Q19363131\'], \'P1792\': [\'Q7234646\'], \'P1376\': [\'Q96\', \'Q170603\', \'Q285658\', \'Q1109279\', \'Q2608489\'], \'P6\': [\'Q5475632\', \'Q5771800\', \'Q28367149\', \'Q5125955\'], \'P1365\': [\'Q13695\'], \'P112\': [\'Q441300\'], \'P2184\': [\'Q2881158\', \'Q10940702\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 248: Q19689 (Tirana)
MERGE (n:Entity {qid: 'Q19689'})
ON CREATE SET
  n.entity_cipher = 'ent_plc_Q19689',
  n.entity_id = 'place_q19689',
  n.label = 'Tirana',
  n.entity_type = 'PLACE',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 121,
  n.property_summary = '{\'P31\': [\'Q515\', \'Q129676344\', \'Q5154045\', \'Q486972\', \'Q5119\'], \'P17\': [\'Q222\'], \'P237\': [\'Q3303528\'], \'P910\': [\'Q8963319\'], \'P131\': [\'Q13037436\'], \'P190\': [\'Q3640\', \'Q1524\', \'Q1492\', \'Q956\', \'Q240\'], \'P1464\': [\'Q10207274\'], \'P1465\': [\'Q9220165\'], \'P421\': [\'Q6655\'], \'P1792\': [\'Q7929843\'], \'P1376\': [\'Q229892\', \'Q13037436\', \'Q222\', \'Q187035\', \'Q1923781\'], \'P1343\': [\'Q867541\', \'Q124737664\', \'Q757187\'], \'P206\': [\'Q1274495\', \'Q3303567\'], \'P6\': [\'Q16354049\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 249: Q8682052 (Category:Rome)
MERGE (n:Entity {qid: 'Q8682052'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8682052',
  n.entity_id = 'concept_q8682052',
  n.label = 'Category:Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 4,
  n.property_summary = '{\'P301\': [\'Q220\'], \'P31\': [\'Q4167836\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 250: Q7977790 (Category:Burials in Rome by place)
MERGE (n:Entity {qid: 'Q7977790'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q7977790',
  n.entity_id = 'concept_q7977790',
  n.label = 'Category:Burials in Rome by place',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 3,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q12131650\', \'Q220\'], \'P4224\': [\'Q5\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 251: Q463130 (Gianni Alemanno)
MERGE (n:Entity {qid: 'Q463130'})
ON CREATE SET
  n.entity_cipher = 'ent_per_Q463130',
  n.entity_id = 'person_q463130',
  n.label = 'Gianni Alemanno',
  n.entity_type = 'PERSON',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 47,
  n.property_summary = '{\'P39\': [\'Q23936560\', \'Q18558478\', \'Q658082\', \'Q658082\', \'Q18558478\'], \'P102\': [\'Q47720\', \'Q662849\', \'Q1126102\', \'Q16987709\', \'Q1757843\'], \'P19\': [\'Q3519\'], \'P106\': [\'Q82955\', \'Q1930187\', \'Q81096\'], \'P27\': [\'Q38\'], \'P31\': [\'Q5\'], \'P735\': [\'Q1158906\'], \'P734\': [\'Q18502490\'], \'P1412\': [\'Q652\'], \'P937\': [\'Q220\'], \'P26\': [\'Q52418695\'], \'P641\': [\'Q36908\'], \'P21\': [\'Q6581097\'], \'P69\': [\'Q748085\'], \'P103\': [\'Q652\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 252: Q535345 (Francesco Rutelli)
MERGE (n:Entity {qid: 'Q535345'})
ON CREATE SET
  n.entity_cipher = 'ent_per_Q535345',
  n.entity_id = 'person_q535345',
  n.label = 'Francesco Rutelli',
  n.entity_type = 'PERSON',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 60,
  n.property_summary = '{\'P26\': [\'Q3634667\'], \'P27\': [\'Q38\'], \'P19\': [\'Q220\'], \'P102\': [\'Q2704736\', \'Q47729\', \'Q178216\', \'Q662502\', \'Q1185894\'], \'P31\': [\'Q5\'], \'P106\': [\'Q82955\', \'Q1930187\'], \'P735\': [\'Q2268455\'], \'P39\': [\'Q18558478\', \'Q13653224\', \'Q23936560\', \'Q4011164\', \'Q32137240\'], \'P1412\': [\'Q652\'], \'P937\': [\'Q6602\', \'Q239\', \'Q220\'], \'P1038\': [\'Q982524\'], \'P69\': [\'Q209344\'], \'P734\': [\'Q55087913\'], \'P21\': [\'Q6581097\'], \'P166\': [\'Q59637861\', \'Q17063180\', \'Q338751\', \'Q12201445\', \'Q28861961\'], \'P103\': [\'Q652\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 253: Q319547 (Walter Veltroni)
MERGE (n:Entity {qid: 'Q319547'})
ON CREATE SET
  n.entity_cipher = 'ent_per_Q319547',
  n.entity_id = 'person_q319547',
  n.label = 'Walter Veltroni',
  n.entity_type = 'PERSON',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 96,
  n.property_summary = '{\'P22\': [\'Q4015575\'], \'P27\': [\'Q38\'], \'P19\': [\'Q220\'], \'P166\': [\'Q10855195\', \'Q14539974\', \'Q96279182\'], \'P102\': [\'Q3740909\', \'Q461886\', \'Q1294923\', \'Q541679\', \'Q47729\'], \'P31\': [\'Q5\'], \'P39\': [\'Q23936560\', \'Q15309742\', \'Q18558478\', \'Q4011164\', \'Q55110543\'], \'P463\': [\'Q841424\', \'Q841424\'], \'P25\': [\'Q15310642\'], \'P106\': [\'Q82955\', \'Q36180\', \'Q1930187\', \'Q2526255\', \'Q4220892\'], \'P735\': [\'Q499249\'], \'P1412\': [\'Q652\', \'Q9063\'], \'P937\': [\'Q6602\', \'Q239\', \'Q220\'], \'P734\': [\'Q21510610\'], \'P910\': [\'Q55296736\'], \'P21\': [\'Q6581097\'], \'P1038\': [\'Q3678133\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 254: Q1394623 (Franco Carraro)
MERGE (n:Entity {qid: 'Q1394623'})
ON CREATE SET
  n.entity_cipher = 'ent_per_Q1394623',
  n.entity_id = 'person_q1394623',
  n.label = 'Franco Carraro',
  n.entity_type = 'PERSON',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 37,
  n.property_summary = '{\'P21\': [\'Q6581097\'], \'P102\': [\'Q590750\', \'Q47720\', \'Q14924303\'], \'P31\': [\'Q5\'], \'P19\': [\'Q617\'], \'P735\': [\'Q15303969\'], \'P27\': [\'Q38\'], \'P106\': [\'Q82955\'], \'P463\': [\'Q40970\'], \'P641\': [\'Q2736\'], \'P39\': [\'Q23936560\', \'Q55168089\', \'Q55168089\', \'Q55168089\', \'Q13653224\'], \'P166\': [\'Q14539974\', \'Q15279723\'], \'P1412\': [\'Q652\'], \'P734\': [\'Q37060339\'], \'P103\': [\'Q652\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 255: Q948169 (Roberto Gualtieri)
MERGE (n:Entity {qid: 'Q948169'})
ON CREATE SET
  n.entity_cipher = 'ent_per_Q948169',
  n.entity_id = 'person_q948169',
  n.label = 'Roberto Gualtieri',
  n.entity_type = 'PERSON',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 58,
  n.property_summary = '{\'P27\': [\'Q38\'], \'P19\': [\'Q220\'], \'P102\': [\'Q47729\'], \'P31\': [\'Q5\'], \'P39\': [\'Q27169\', \'Q27169\', \'Q27169\', \'Q28002382\', \'Q18558478\'], \'P735\': [\'Q15905580\'], \'P106\': [\'Q82955\', \'Q201788\', \'Q1622272\', \'Q1650915\'], \'P937\': [\'Q6602\', \'Q239\', \'Q220\'], \'P108\': [\'Q209344\', \'Q691851\'], \'P1412\': [\'Q652\'], \'P734\': [\'Q37043375\'], \'P69\': [\'Q209344\', \'Q691851\'], \'P1343\': [\'Q67311526\'], \'P21\': [\'Q6581097\'], \'P103\': [\'Q652\'], \'P1303\': [\'Q6607\'], \'P1344\': [\'Q114717236\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 256: Q6469667 (Category:Films shot in Rome)
MERGE (n:Entity {qid: 'Q6469667'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6469667',
  n.entity_id = 'concept_q6469667',
  n.label = 'Category:Films shot in Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 5,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q1045481\', \'Q220\'], \'P461\': [\'Q7141274\'], \'P4224\': [\'Q11424\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 257: Q642958 (Stadio Nazionale)
MERGE (n:Entity {qid: 'Q642958'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q642958',
  n.entity_id = 'concept_q642958',
  n.label = 'Stadio Nazionale',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 23,
  n.property_summary = '{\'P17\': [\'Q38\'], \'P31\': [\'Q74539696\'], \'P127\': [\'Q220\'], \'P131\': [\'Q220\'], \'P641\': [\'Q2736\'], \'P84\': [\'Q1382978\'], \'P765\': [\'Q207766\'], \'P466\': [\'Q113135\', \'Q2609\', \'Q2739\'], \'P793\': [\'Q1477177\'], \'P276\': [\'Q220\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 258: Q737333 (Cornelia)
MERGE (n:Entity {qid: 'Q737333'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q737333',
  n.entity_id = 'concept_q737333',
  n.label = 'Cornelia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 25,
  n.property_summary = '{\'P81\': [\'Q572544\'], \'P197\': [\'Q1232747\', \'Q648499\'], \'P17\': [\'Q38\'], \'P31\': [\'Q928830\', \'Q22808403\'], \'P131\': [\'Q220\'], \'P127\': [\'Q220\'], \'P912\': [\'Q657345\', \'Q813966\'], \'P137\': [\'Q530087\'], \'P5817\': [\'Q55654238\'], \'P16\': [\'Q237480\'], \'P30\': [\'Q46\'], \'P2846\': [\'Q24192068\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 259: Q1189119 (Foro Italico swimming complex)
MERGE (n:Entity {qid: 'Q1189119'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q1189119',
  n.entity_id = 'concept_q1189119',
  n.label = 'Foro Italico swimming complex',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 15,
  n.property_summary = '{\'P17\': [\'Q38\'], \'P31\': [\'Q200023\'], \'P641\': [\'Q31920\'], \'P127\': [\'Q21190087\'], \'P910\': [\'Q125658559\'], \'P527\': [\'Q135910546\', \'Q135910779\'], \'P131\': [\'Q220\'], \'P276\': [\'Q220\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 260: Q42949340 (Cod. Pal. germ. 313)
MERGE (n:Entity {qid: 'Q42949340'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q42949340',
  n.entity_id = 'concept_q42949340',
  n.label = 'Cod. Pal. germ. 313',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 17,
  n.property_summary = '{\'P195\': [\'Q684368\'], \'P921\': [\'Q1169342\'], \'P31\': [\'Q213924\'], \'P407\': [\'Q837985\'], \'P186\': [\'Q11472\'], \'P127\': [\'Q2966\', \'Q220\'], \'P361\': [\'Q1106116\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 261: Q241693 (Anguillara Sabazia)
MERGE (n:Entity {qid: 'Q241693'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q241693',
  n.entity_id = 'concept_q241693',
  n.label = 'Anguillara Sabazia',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 61,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\', \'Q136290577\'], \'P47\': [\'Q241791\', \'Q241911\', \'Q242505\', \'Q19326\', \'Q243497\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P190\': [\'Q1998560\'], \'P910\': [\'Q9015571\'], \'P36\': [\'Q30022234\'], \'P1464\': [\'Q9228445\'], \'P1792\': [\'Q96889159\'], \'P1465\': [\'Q9220570\'], \'P417\': [\'Q151967\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 262: Q241733 (Ardea)
MERGE (n:Entity {qid: 'Q241733'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q241733',
  n.entity_id = 'concept_q241733',
  n.label = 'Ardea',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 60,
  n.property_summary = '{\'P190\': [\'Q189901\', \'Q62010\'], \'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q191115\', \'Q128052\', \'Q243172\', \'Q241717\', \'Q241744\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P910\': [\'Q21529677\'], \'P1343\': [\'Q1138524\', \'Q30059240\', \'Q602358\', \'Q867541\'], \'P1464\': [\'Q22988398\'], \'P36\': [\'Q49281016\'], \'P1792\': [\'Q24073509\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 263: Q242105 (Castel Gandolfo)
MERGE (n:Entity {qid: 'Q242105'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242105',
  n.entity_id = 'concept_q242105',
  n.label = 'Castel Gandolfo',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 80,
  n.property_summary = '{\'P910\': [\'Q9093097\'], \'P131\': [\'Q15119\', \'Q18288160\'], \'P31\': [\'Q747074\'], \'P47\': [\'Q191115\', \'Q242703\', \'Q242926\', \'Q243228\', \'Q220\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P190\': [\'Q1002525\', \'Q338877\'], \'P1464\': [\'Q9223989\'], \'P1465\': [\'Q9217942\'], \'P36\': [\'Q30024117\'], \'P1792\': [\'Q25194128\'], \'P7867\': [\'Q84046921\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 264: Q242513 (Ciampino)
MERGE (n:Entity {qid: 'Q242513'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242513',
  n.entity_id = 'concept_q242513',
  n.label = 'Ciampino',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 50,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q242703\', \'Q242926\', \'Q220\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P910\': [\'Q9107831\'], \'P36\': [\'Q30024727\'], \'P417\': [\'Q408284\'], \'P9235\': [\'Q106435258\'], \'P1792\': [\'Q86320549\'], \'P1465\': [\'Q86320581\'], \'P1464\': [\'Q86320582\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 265: Q242558 (Colonna)
MERGE (n:Entity {qid: 'Q242558'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242558',
  n.entity_id = 'concept_q242558',
  n.label = 'Colonna',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 40,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q242965\', \'Q242954\', \'Q243346\', \'Q140255\', \'Q220\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P190\': [\'Q1064425\'], \'P1464\': [\'Q18756473\'], \'P910\': [\'Q9112650\'], \'P417\': [\'Q44269\'], \'P1889\': [\'Q1110986\'], \'P9235\': [\'Q106435258\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 266: Q19326 (Fiumicino)
MERGE (n:Entity {qid: 'Q19326'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q19326',
  n.entity_id = 'concept_q19326',
  n.label = 'Fiumicino',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 59,
  n.property_summary = '{\'P131\': [\'Q18288160\', \'Q15119\'], \'P47\': [\'Q242505\', \'Q220\', \'Q241693\', \'Q242784\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P31\': [\'Q747074\'], \'P910\': [\'Q9161263\'], \'P1792\': [\'Q25193746\'], \'P190\': [\'Q57818\'], \'P1365\': [\'Q12901128\'], \'P1465\': [\'Q32092427\'], \'P17\': [\'Q38\'], \'P9235\': [\'Q106435265\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 267: Q242637 (Fonte Nuova)
MERGE (n:Entity {qid: 'Q242637'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242637',
  n.entity_id = 'concept_q242637',
  n.label = 'Fonte Nuova',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 41,
  n.property_summary = '{\'P910\': [\'Q9161968\'], \'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q242942\', \'Q220\', \'Q242710\', \'Q242998\', \'Q243408\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P190\': [\'Q966657\'], \'P1465\': [\'Q18755262\'], \'P417\': [\'Q128267\'], \'P9235\': [\'Q106435258\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 268: Q242645 (Formello)
MERGE (n:Entity {qid: 'Q242645'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242645',
  n.entity_id = 'concept_q242645',
  n.label = 'Formello',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 48,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\', \'Q136290577\'], \'P47\': [\'Q220\', \'Q241911\', \'Q243311\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P1465\': [\'Q18755279\'], \'P910\': [\'Q21745556\'], \'P36\': [\'Q30025816\'], \'P417\': [\'Q17590\'], \'P9235\': [\'Q106435263\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 269: Q242703 (Grottaferrata)
MERGE (n:Entity {qid: 'Q242703'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242703',
  n.entity_id = 'concept_q242703',
  n.label = 'Grottaferrata',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 72,
  n.property_summary = '{\'P190\': [\'Q320308\', \'Q53840\', \'Q80663\', \'Q51871\', \'Q81453\'], \'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q242513\', \'Q190963\', \'Q242965\', \'Q242954\', \'Q220\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P1464\': [\'Q18757671\'], \'P1465\': [\'Q9218541\'], \'P910\': [\'Q9179066\'], \'P36\': [\'Q30026245\'], \'P1792\': [\'Q91213163\'], \'P417\': [\'Q171807\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 270: Q242965 (Monte Porzio Catone)
MERGE (n:Entity {qid: 'Q242965'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242965',
  n.entity_id = 'concept_q242965',
  n.label = 'Monte Porzio Catone',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 54,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\', \'Q136290579\'], \'P47\': [\'Q190963\', \'Q242954\', \'Q220\', \'Q242703\', \'Q243210\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P190\': [\'Q1016829\'], \'P1464\': [\'Q18754783\'], \'P1465\': [\'Q9219150\'], \'P910\': [\'Q9217163\'], \'P36\': [\'Q30027757\'], \'P1792\': [\'Q134542380\'], \'P417\': [\'Q2424767\'], \'P9235\': [\'Q106435258\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 271: Q242998 (Monterotondo)
MERGE (n:Entity {qid: 'Q242998'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242998',
  n.entity_id = 'concept_q242998',
  n.label = 'Monterotondo',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 53,
  n.property_summary = '{\'P131\': [\'Q18288160\', \'Q136290596\'], \'P47\': [\'Q242126\', \'Q242637\', \'Q242942\', \'Q242990\', \'Q243143\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P1464\': [\'Q9225932\'], \'P1465\': [\'Q9219167\'], \'P910\': [\'Q9217252\'], \'P1792\': [\'Q9237654\'], \'P36\': [\'Q30027937\'], \'P166\': [\'Q850170\'], \'P417\': [\'Q43675\'], \'P9235\': [\'Q106435258\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 272: Q243311 (Sacrofano)
MERGE (n:Entity {qid: 'Q243311'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q243311',
  n.entity_id = 'concept_q243311',
  n.label = 'Sacrofano',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 40,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\', \'Q136290578\'], \'P47\': [\'Q241911\', \'Q242126\', \'Q242645\', \'Q397182\', \'Q220\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P1464\': [\'Q18753319\'], \'P1465\': [\'Q18761390\'], \'P910\': [\'Q21755495\'], \'P36\': [\'Q30029675\'], \'P1792\': [\'Q105626899\'], \'P9235\': [\'Q106435263\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 273: Q243497 (Trevignano Romano)
MERGE (n:Entity {qid: 'Q243497'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q243497',
  n.entity_id = 'concept_q243497',
  n.label = 'Trevignano Romano',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 51,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\', \'Q136290577\'], \'P47\': [\'Q241791\', \'Q241911\', \'Q176150\', \'Q176155\', \'Q177741\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P1464\': [\'Q18752654\'], \'P1465\': [\'Q18761619\'], \'P910\': [\'Q21755566\'], \'P36\': [\'Q30031312\'], \'P417\': [\'Q316295\'], \'P9235\': [\'Q106435265\'], \'P10611\': [\'Q678967\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 274: Q191115 (Albano Laziale)
MERGE (n:Entity {qid: 'Q191115'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q191115',
  n.entity_id = 'concept_q191115',
  n.label = 'Albano Laziale',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 72,
  n.property_summary = '{\'P190\': [\'Q161919\', \'Q62868\', \'Q450625\', \'Q54520\'], \'P131\': [\'Q18288160\'], \'P47\': [\'Q241733\', \'Q241744\', \'Q242105\', \'Q243228\', \'Q220\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P910\': [\'Q8990203\'], \'P1792\': [\'Q9238192\'], \'P1464\': [\'Q9228340\'], \'P1465\': [\'Q9220513\'], \'P36\': [\'Q30022065\'], \'P1343\': [\'Q19180675\', \'Q602358\', \'Q30059240\', \'Q19047539\', \'Q16082057\'], \'P7867\': [\'Q84085730\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 275: Q241911 (Campagnano di Roma)
MERGE (n:Entity {qid: 'Q241911'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q241911',
  n.entity_id = 'concept_q241911',
  n.label = 'Campagnano di Roma',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 4,
  n.properties_count = 47,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q241693\', \'Q242645\', \'Q242870\', \'Q242935\', \'Q176155\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P910\': [\'Q9068833\'], \'P36\': [\'Q30023467\'], \'P417\': [\'Q40662\'], \'P9235\': [\'Q106435263\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 276: Q242120 (Castel San Pietro Romano)
MERGE (n:Entity {qid: 'Q242120'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242120',
  n.entity_id = 'concept_q242120',
  n.label = 'Castel San Pietro Romano',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 44,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\', \'Q136290595\'], \'P47\': [\'Q241990\', \'Q177726\', \'Q243133\', \'Q243168\', \'Q243220\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P36\': [\'Q30024139\'], \'P417\': [\'Q152457\'], \'P9235\': [\'Q106435258\'], \'P463\': [\'Q127107\'], \'P910\': [\'Q124068942\'], \'P1792\': [\'Q124068987\'], \'P1465\': [\'Q124069003\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 277: Q190963 (Frascati)
MERGE (n:Entity {qid: 'Q190963'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q190963',
  n.entity_id = 'concept_q190963',
  n.label = 'Frascati',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 81,
  n.property_summary = '{\'P190\': [\'Q153260\', \'Q189153\', \'Q12995\', \'Q1368496\'], \'P910\': [\'Q9164230\'], \'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q242965\', \'Q220\', \'Q242703\', \'Q242954\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P1465\': [\'Q9218403\'], \'P1464\': [\'Q9224749\'], \'P1792\': [\'Q13283048\'], \'P36\': [\'Q30025877\'], \'P1343\': [\'Q4532138\', \'Q867541\', \'Q5375740\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 278: Q242661 (Gallicano nel Lazio)
MERGE (n:Entity {qid: 'Q242661'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242661',
  n.entity_id = 'concept_q242661',
  n.label = 'Gallicano nel Lazio',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 41,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q220\', \'Q140255\', \'Q243133\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P1464\': [\'Q18757383\'], \'P1465\': [\'Q18758762\'], \'P910\': [\'Q21747092\'], \'P36\': [\'Q30025967\'], \'P1792\': [\'Q106298877\'], \'P417\': [\'Q43399\'], \'P9235\': [\'Q106435258\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 279: Q242926 (Marino)
MERGE (n:Entity {qid: 'Q242926'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242926',
  n.entity_id = 'concept_q242926',
  n.label = 'Marino',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 66,
  n.property_summary = '{\'P190\': [\'Q4071168\', \'Q72134\', \'Q172455\', \'Q23042\', \'Q51690\'], \'P131\': [\'Q15119\', \'Q18288160\', \'Q136290581\'], \'P47\': [\'Q243228\', \'Q242105\', \'Q242703\', \'Q220\', \'Q242513\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P1465\': [\'Q9219029\'], \'P1464\': [\'Q9225700\'], \'P1792\': [\'Q9237592\'], \'P910\': [\'Q9214715\'], \'P36\': [\'Q30027266\'], \'P150\': [\'Q15140797\', \'Q3215006\', \'Q3715940\', \'Q1882772\', \'Q2627825\'], \'P1366\': [\'Q3643232\'], \'P1365\': [\'Q3643232\'], \'P1830\': [\'Q3889880\', \'Q3967911\'], \'P7867\': [\'Q84068577\'], \'P8744\': [\'Q3718718\'], \'P417\': [\'Q185856\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 280: Q243133 (Palestrina)
MERGE (n:Entity {qid: 'Q243133'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q243133',
  n.entity_id = 'concept_q243133',
  n.label = 'Palestrina',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 5,
  n.properties_count = 76,
  n.property_summary = '{\'P910\': [\'Q9234676\'], \'P131\': [\'Q15119\', \'Q18288160\', \'Q136290595\'], \'P47\': [\'Q242120\', \'Q177726\', \'Q242661\', \'Q243220\', \'Q220\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\', \'Q172579\', \'Q2277\', \'Q17167\'], \'P31\': [\'Q747074\'], \'P190\': [\'Q262684\', \'Q114877\'], \'P1464\': [\'Q9226322\'], \'P1465\': [\'Q9219408\'], \'P1792\': [\'Q16515169\'], \'P1343\': [\'Q2041543\', \'Q3181656\', \'Q867541\', \'Q19077875\'], \'P36\': [\'Q30028551\'], \'P832\': [\'Q150139\'], \'P1365\': [\'Q2107419\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 281: Q243188 (Riano)
MERGE (n:Entity {qid: 'Q243188'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q243188',
  n.entity_id = 'concept_q243188',
  n.label = 'Riano',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 37,
  n.property_summary = '{\'P131\': [\'Q15119\', \'Q18288160\', \'Q136290578\'], \'P47\': [\'Q242126\', \'Q242998\', \'Q220\', \'Q243311\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q747074\'], \'P36\': [\'Q30029340\'], \'P417\': [\'Q48438\'], \'P9235\': [\'Q106435263\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 282: Q242710 (Guidonia Montecelio)
MERGE (n:Entity {qid: 'Q242710'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q242710',
  n.entity_id = 'concept_q242710',
  n.label = 'Guidonia Montecelio',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 61,
  n.property_summary = '{\'P190\': [\'Q966657\'], \'P131\': [\'Q15119\', \'Q18288160\'], \'P47\': [\'Q242917\', \'Q220\', \'Q243408\', \'Q242637\', \'Q243143\'], \'P417\': [\'Q3842717\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P17\': [\'Q38\'], \'P31\': [\'Q954172\'], \'P1464\': [\'Q9225004\'], \'P910\': [\'Q9184727\'], \'P36\': [\'Q30026322\'], \'P7867\': [\'Q84082271\'], \'P1792\': [\'Q94385255\'], \'P1465\': [\'Q94385260\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 283: Q8070169 (Category:Births in Rome)
MERGE (n:Entity {qid: 'Q8070169'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q8070169',
  n.entity_id = 'concept_q8070169',
  n.label = 'Category:Births in Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 5,
  n.property_summary = '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q1322263\', \'Q220\'], \'P461\': [\'Q9689571\'], \'P4224\': [\'Q5\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 284: Q1242632 (Remus)
MERGE (n:Entity {qid: 'Q1242632'})
ON CREATE SET
  n.entity_cipher = 'ent_per_Q1242632',
  n.entity_id = 'person_q1242632',
  n.label = 'Remus',
  n.entity_type = 'PERSON',
  n.namespace = 'wd',
  n.federation_score = 3,
  n.properties_count = 58,
  n.property_summary = '{\'P361\': [\'Q2197\'], \'P31\': [\'Q124710051\', \'Q124940323\'], \'P25\': [\'Q219936\'], \'P22\': [\'Q112\'], \'P21\': [\'Q6581097\'], \'P157\': [\'Q2186\'], \'P119\': [\'Q194103\'], \'P3373\': [\'Q2186\'], \'P1343\': [\'Q30059240\', \'Q1138524\', \'Q3181656\'], \'P27\': [\'Q1747689\'], \'P2348\': [\'Q201038\'], \'P19\': [\'Q335070\'], \'P20\': [\'Q220\'], \'P1196\': [\'Q149086\'], \'P1080\': [\'Q122173\'], \'P40\': [\'Q113027477\', \'Q113027497\', \'Q7450768\'], \'P1889\': [\'Q28540088\', \'Q3932444\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 285: Q16494134 (Municipio II)
MERGE (n:Entity {qid: 'Q16494134'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16494134',
  n.entity_id = 'concept_q16494134',
  n.label = 'Municipio II',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 21,
  n.property_summary = '{\'P910\': [\'Q9222016\'], \'P17\': [\'Q38\'], \'P31\': [\'Q525504\'], \'P131\': [\'Q3940419\'], \'P1365\': [\'Q1223319\', \'Q947222\'], \'P190\': [\'Q2542169\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P47\': [\'Q550592\', \'Q16003470\', \'Q16003516\', \'Q16481953\', \'Q16482005\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 286: Q16003470 (Municipio III)
MERGE (n:Entity {qid: 'Q16003470'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16003470',
  n.entity_id = 'concept_q16003470',
  n.label = 'Municipio III',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 22,
  n.property_summary = '{\'P910\': [\'Q9222017\'], \'P17\': [\'Q38\'], \'P31\': [\'Q525504\'], \'P131\': [\'Q3940419\'], \'P1365\': [\'Q1223251\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P47\': [\'Q16494134\', \'Q16003516\', \'Q16482005\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 287: Q16481953 (Municipio V)
MERGE (n:Entity {qid: 'Q16481953'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16481953',
  n.entity_id = 'concept_q16481953',
  n.label = 'Municipio V',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 22,
  n.property_summary = '{\'P910\': [\'Q9222020\'], \'P17\': [\'Q38\'], \'P31\': [\'Q525504\'], \'P131\': [\'Q3940419\'], \'P1365\': [\'Q545658\', \'Q654771\'], \'P6\': [\'Q95509135\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P47\': [\'Q550592\', \'Q16494134\', \'Q16003516\', \'Q16481961\', \'Q16481966\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 288: Q16481966 (Municipio VII)
MERGE (n:Entity {qid: 'Q16481966'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16481966',
  n.entity_id = 'concept_q16481966',
  n.label = 'Municipio VII',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 21,
  n.property_summary = '{\'P910\': [\'Q9222022\'], \'P17\': [\'Q38\'], \'P31\': [\'Q525504\'], \'P131\': [\'Q3940419\'], \'P1365\': [\'Q950023\', \'Q1135073\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P47\': [\'Q550592\', \'Q16481953\', \'Q16481961\', \'Q16495467\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 289: Q16495467 (Municipio VIII)
MERGE (n:Entity {qid: 'Q16495467'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16495467',
  n.entity_id = 'concept_q16495467',
  n.label = 'Municipio VIII',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 23,
  n.property_summary = '{\'P910\': [\'Q9222023\'], \'P17\': [\'Q38\'], \'P31\': [\'Q525504\'], \'P131\': [\'Q3940419\'], \'P1365\': [\'Q1163800\'], \'P190\': [\'Q126415\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P47\': [\'Q550592\', \'Q16481966\', \'Q16481947\', \'Q16481986\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 290: Q16481977 (Municipio X)
MERGE (n:Entity {qid: 'Q16481977'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16481977',
  n.entity_id = 'concept_q16481977',
  n.label = 'Municipio X',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 22,
  n.property_summary = '{\'P910\': [\'Q9222024\'], \'P17\': [\'Q38\'], \'P31\': [\'Q525504\'], \'P131\': [\'Q3940419\'], \'P1365\': [\'Q1231958\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P47\': [\'Q16481947\', \'Q16481986\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 291: Q16481992 (Municipio XII)
MERGE (n:Entity {qid: 'Q16481992'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16481992',
  n.entity_id = 'concept_q16481992',
  n.label = 'Municipio XII',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 20,
  n.property_summary = '{\'P910\': [\'Q9222026\'], \'P17\': [\'Q38\'], \'P31\': [\'Q525504\'], \'P131\': [\'Q3940419\'], \'P1365\': [\'Q682792\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P47\': [\'Q550592\', \'Q16481986\', \'Q16481997\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 292: Q16482002 (Municipio XIV)
MERGE (n:Entity {qid: 'Q16482002'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q16482002',
  n.entity_id = 'concept_q16482002',
  n.label = 'Municipio XIV',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 22,
  n.property_summary = '{\'P910\': [\'Q19936715\'], \'P17\': [\'Q38\'], \'P31\': [\'Q525504\'], \'P1365\': [\'Q1221519\'], \'P131\': [\'Q3940419\'], \'P421\': [\'Q6655\', \'Q6723\'], \'P47\': [\'Q550592\', \'Q16481997\', \'Q16482005\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 293: Q4173137 (Jewish Encyclopedia of Brockhaus and Efron)
MERGE (n:Entity {qid: 'Q4173137'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q4173137',
  n.entity_id = 'concept_q4173137',
  n.label = 'Jewish Encyclopedia of Brockhaus and Efron',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 16,
  n.property_summary = '{\'P31\': [\'Q56165908\'], \'P910\': [\'Q21096015\'], \'P527\': [\'Q21096032\', \'Q21096035\', \'Q21096039\', \'Q21096041\', \'Q21096042\'], \'P291\': [\'Q656\'], \'P407\': [\'Q7737\'], \'P921\': [\'Q9268\', \'Q961603\'], \'P50\': [\'Q1690980\'], \'P123\': [\'Q19908137\'], \'P7937\': [\'Q5292\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 294: Q20961706 (Infernal Dictionary, 6th ed.)
MERGE (n:Entity {qid: 'Q20961706'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q20961706',
  n.entity_id = 'concept_q20961706',
  n.label = 'Infernal Dictionary, 6th ed.',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 14,
  n.property_summary = '{\'P31\': [\'Q3331189\'], \'P629\': [\'Q1210353\'], \'P110\': [\'Q135113993\'], \'P872\': [\'Q3392522\'], \'P123\': [\'Q3392522\'], \'P407\': [\'Q150\'], \'P6216\': [\'Q19652\', \'Q19652\'], \'P50\': [\'Q2283832\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 295: Q111600428 (Q111600428)
MERGE (n:Entity {qid: 'Q111600428'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q111600428',
  n.entity_id = 'concept_q111600428',
  n.label = 'Q111600428',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 9,
  n.property_summary = '{\'P31\': [\'Q3331189\'], \'P50\': [\'Q155855\'], \'P629\': [\'Q12021884\'], \'P291\': [\'Q1085\'], \'P407\': [\'Q9056\'], \'P361\': [\'Q131691494\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 296: Q126374795 (Meyer’s Universum, Erster Band)
MERGE (n:Entity {qid: 'Q126374795'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q126374795',
  n.entity_id = 'concept_q126374795',
  n.label = 'Meyer’s Universum, Erster Band',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q732577\', \'Q4230425\'], \'P407\': [\'Q188\'], \'P50\': [\'Q76183\'], \'P291\': [\'Q504348\', \'Q60\'], \'P6216\': [\'Q19652\'], \'P527\': [\'Q126375420\', \'Q126382159\', \'Q126382821\', \'Q126391133\', \'Q126391147\'], \'P179\': [\'Q29418320\'], \'P156\': [\'Q126937278\'], \'P972\': [\'Q133465596\', \'Q61729277\'], \'P123\': [\'Q314219\'], \'P98\': [\'Q76183\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 297: Q137757464 (Meyer’s Universum, Zwanzigster Band)
MERGE (n:Entity {qid: 'Q137757464'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q137757464',
  n.entity_id = 'concept_q137757464',
  n.label = 'Meyer’s Universum, Zwanzigster Band',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 19,
  n.property_summary = '{\'P31\': [\'Q732577\', \'Q4230425\'], \'P179\': [\'Q29418320\'], \'P155\': [\'Q137654208\'], \'P50\': [\'Q120915\'], \'P98\': [\'Q96012\'], \'P123\': [\'Q314219\'], \'P291\': [\'Q504348\'], \'P407\': [\'Q188\'], \'P6216\': [\'Q19652\'], \'P527\': [\'Q137757459\', \'Q137757709\', \'Q137757729\', \'Q137757775\', \'Q137757780\'], \'P156\': [\'Q137863868\'], \'P972\': [\'Q61729277\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 298: Q6701024 (Category:Geography of Ancient Rome)
MERGE (n:Entity {qid: 'Q6701024'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6701024',
  n.entity_id = 'concept_q6701024',
  n.label = 'Category:Geography of Ancient Rome',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 2,
  n.property_summary = '{\'P31\': [\'Q4167836\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 299: Q652 (Italian)
MERGE (n:Entity {qid: 'Q652'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q652',
  n.entity_id = 'concept_q652',
  n.label = 'Italian',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 2,
  n.properties_count = 127,
  n.property_summary = '{\'P1151\': [\'Q47487400\'], \'P910\': [\'Q7237580\'], \'P1999\': [\'Q20672086\'], \'P4132\': [\'Q651641\', \'Q7888569\', \'Q74835210\', \'Q661936\'], \'P1018\': [\'Q338489\'], \'P5996\': [\'Q6840646\'], \'P5109\': [\'Q499327\', \'Q1775415\'], \'P2959\': [\'Q22828827\'], \'P2579\': [\'Q515601\'], \'P5110\': [\'Q51929218\', \'Q51929369\', \'Q52431955\', \'Q52431970\', \'Q51929290\'], \'P31\': [\'Q33742\', \'Q1288568\'], \'P3161\': [\'Q682111\', \'Q625581\', \'Q473746\', \'Q22716\', \'Q179230\'], \'P5206\': [\'Q3921587\', \'Q3953977\', \'Q3984890\'], \'P282\': [\'Q550383\', \'Q16987661\'], \'P3103\': [\'Q1101896\', \'Q12547192\', \'Q192613\', \'Q1240211\', \'Q442485\'], \'P2989\': [\'Q131105\'], \'P279\': [\'Q3356483\', \'Q85380120\'], \'P1343\': [\'Q602358\', \'Q19180675\', \'Q867541\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


// Entity 300: Q6655 (UTC+01:00)
MERGE (n:Entity {qid: 'Q6655'})
ON CREATE SET
  n.entity_cipher = 'ent_con_Q6655',
  n.entity_id = 'concept_q6655',
  n.label = 'UTC+01:00',
  n.entity_type = 'CONCEPT',
  n.namespace = 'wd',
  n.federation_score = 1,
  n.properties_count = 7,
  n.property_summary = '{\'P31\': [\'Q17272482\'], \'P460\': [\'Q25989\', \'Q1773995\', \'Q106763456\']}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()


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
