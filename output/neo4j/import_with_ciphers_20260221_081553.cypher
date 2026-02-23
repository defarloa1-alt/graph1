// Neo4j Import - SCA Entities with Ciphers
// Generated: 2026-02-21T08:15:53.658724
// Total entities: 50

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
  property_summary: '{\'P31\': [\'Q11514315\', \'Q1307214\', \'Q48349\', \'Q3024240\'], \'P910\': [\'Q6944405\'], \'P140\': [\'Q337547\'], \'P194\': [\'Q130614\', \'Q1114821\'], \'P38\': [\'Q952064\'], \'P2348\': [\'Q486761\'], \'P1792\': [\'Q13285410\'], \'P527\': [\'Q2839628\', \'Q6106068\', \'Q2815472\'], \'P1366\': [\'Q2277\', \'Q206414\'], \'P155\': [\'Q201038\'], \'P36\': [\'Q220\'], \'P2936\': [\'Q397\', \'Q35497\'], \'P30\': [\'Q46\', \'Q48\', \'Q15\'], \'P3075\': [\'Q337547\'], \'P122\': [\'Q666680\'], \'P1365\': [\'Q201038\'], \'P361\': [\'Q1747689\'], \'P1889\': [\'Q346629\'], \'P5008\': [\'Q6173448\'], \'P793\': [\'Q124988\', \'Q3778726\', \'Q75813\', \'Q202161\', \'Q596373\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P279\': [\'Q6428674\'], \'P2354\': [\'Q17004260\'], \'P1687\': [\'P2408\', \'P2348\'], \'P8952\': [\'P571\', \'P1365\', \'P576\', \'P1366\'], \'P1963\': [\'P580\', \'P156\', \'P582\', \'P155\'], \'P1889\': [\'Q816829\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P279\': [\'Q183039\', \'Q2752458\', \'Q28108\'], \'P910\': [\'Q54069\'], \'P1687\': [\'P122\'], \'P1889\': [\'Q183039\', \'Q5589178\', \'Q19944802\', \'Q28108\', \'Q20076236\'], \'P527\': [\'Q759524\', \'Q191600\', \'Q31728\'], \'P1424\': [\'Q6526407\', \'Q25728256\', \'Q15838730\'], \'P8225\': [\'Q7188\'], \'P31\': [\'Q19478619\'], \'P13044\': [\'Q7188\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q6135095\'], \'P1343\': [\'Q20743760\', \'Q2041543\', \'Q867541\', \'Q101314624\', \'Q20078554\'], \'P2354\': [\'Q1151047\'], \'P1889\': [\'Q499146\', \'Q978370\', \'Q356252\'], \'P1424\': [\'Q7477250\'], \'P5008\': [\'Q6173448\'], \'P279\': [\'Q1250464\', \'Q3624078\'], \'P31\': [\'Q7269\'], \'P35\': [\'Q39018\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P279\': [\'Q19953632\', \'Q96196009\', \'Q19832712\', \'Q6256\'], \'P910\': [\'Q7238252\'], \'P1687\': [\'P17\'], \'P1424\': [\'Q6036853\'], \'P1889\': [\'Q3591867\'], \'P8952\': [\'P582\', \'P580\'], \'P1963\': [\'P571\', \'P1365\', \'P576\', \'P1366\', \'P36\'], \'P2354\': [\'Q62630\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q4167836\'], \'P301\': [\'Q17167\'], \'P4224\': [\'Q5\'], \'P155\': [\'Q8678306\'], \'P156\': [\'Q1456601\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q8251375\'], \'P1343\': [\'Q602358\', \'Q30059240\', \'Q867541\'], \'P31\': [\'Q108704490\'], \'P1889\': [\'Q107013262\', \'Q107013169\'], \'P1424\': [\'Q5626901\'], \'P361\': [\'Q122173\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q11204\', \'Q123432\', \'Q2570643\'], \'P159\': [\'Q1144514\', \'Q5194731\', \'Q1144512\'], \'P17\': [\'Q1747689\'], \'P527\': [\'Q20056508\'], \'P1343\': [\'Q30059240\', \'Q602358\'], \'P910\': [\'Q32899669\'], \'P2348\': [\'Q486761\'], \'P1889\': [\'Q343948\', \'Q1466018\'], \'P2670\': [\'Q20056508\'], \'P828\': [\'Q1225322\'], \'P5008\': [\'Q6173448\'], \'P279\': [\'Q2915100\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q17197366\'], \'P279\': [\'Q11204\'], \'P1343\': [\'Q3181656\', \'Q1138524\', \'Q867541\'], \'P17\': [\'Q1747689\'], \'P2348\': [\'Q17167\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q8386687\'], \'P31\': [\'Q17524420\'], \'P1269\': [\'Q1747689\'], \'P1343\': [\'Q602358\', \'Q1138524\', \'Q30059240\', \'Q19219752\'], \'P527\': [\'Q662137\', \'Q638048\'], \'P279\': [\'Q8142\', \'Q28783456\'], \'P2579\': [\'Q3879434\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P527\': [\'Q14618893\', \'Q17167\', \'Q428995\', \'Q11772\', \'Q181264\'], \'P910\': [\'Q8381710\'], \'P156\': [\'Q217050\'], \'P1269\': [\'Q937284\'], \'P31\': [\'Q11514315\', \'Q1292119\'], \'P1889\': [\'Q41493\'], \'P279\': [\'Q41493\'], \'P155\': [\'Q98270938\'], \'P2579\': [\'Q112939719\', \'Q495527\'], \'P5008\': [\'Q6173448\'], \'P361\': [\'Q41493\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q4167836\'], \'P971\': [\'Q19660746\', \'Q17167\', \'Q5\'], \'P4224\': [\'Q5\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q11514315\'], \'P361\': [\'Q17167\'], \'P155\': [\'Q201038\', \'Q16931679\', \'Q119137625\'], \'P156\': [\'Q6106068\'], \'P17\': [\'Q17167\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q11514315\'], \'P361\': [\'Q17167\'], \'P155\': [\'Q2839628\'], \'P156\': [\'Q2815472\'], \'P17\': [\'Q17167\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q11514315\'], \'P361\': [\'Q17167\'], \'P155\': [\'Q6106068\'], \'P156\': [\'Q787204\'], \'P17\': [\'Q17167\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P36\': [\'Q220\', \'Q16869\', \'Q13364\', \'Q490\', \'Q18287233\'], \'P37\': [\'Q397\', \'Q35497\'], \'P122\': [\'Q173424\', \'Q7269\', \'Q174450\', \'Q83204\', \'Q184558\'], \'P38\': [\'Q208041\', \'Q187776\', \'Q952064\', \'Q476078\', \'Q376895\'], \'P910\': [\'Q1456601\'], \'P140\': [\'Q337547\', \'Q7603670\'], \'P194\': [\'Q3510883\'], \'P31\': [\'Q48349\', \'Q11514315\', \'Q3024240\'], \'P2184\': [\'Q2671119\'], \'P1906\': [\'Q842606\'], \'P2959\': [\'Q21201536\'], \'P530\': [\'Q7209\', \'Q62646\', \'Q302980\'], \'P1792\': [\'Q8678282\'], \'P1464\': [\'Q32642796\'], \'P1465\': [\'Q42859641\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P47\': [\'Q1986139\'], \'P150\': [\'Q692775\', \'Q3626028\', \'Q1156891\', \'Q747040\', \'Q186513\'], \'P237\': [\'Q264655\', \'Q163323\'], \'P3075\': [\'Q337547\', \'Q5043\', \'Q29536\', \'Q83922\'], \'P1151\': [\'Q42353313\'], \'P1366\': [\'Q42834\', \'Q12544\'], \'P1365\': [\'Q17167\'], \'P1343\': [\'Q19180675\', \'Q3181656\', \'Q1154753\', \'Q16082057\', \'Q602358\'], \'P7867\': [\'Q8607609\'], \'P1889\': [\'Q178897\'], \'P30\': [\'Q46\', \'Q15\', \'Q48\', \'Q27527\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P1343\': [\'Q602358\', \'Q4532138\', \'Q124737636\'], \'P31\': [\'Q1307214\', \'Q11514315\'], \'P2596\': [\'Q1747689\'], \'P17\': [\'Q2277\'], \'P361\': [\'Q14618893\', \'Q105747718\'], \'P156\': [\'Q238399\'], \'P1889\': [\'Q787204\'], \'P1365\': [\'Q17167\'], \'P155\': [\'Q17167\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q8678306\'], \'P31\': [\'Q11514315\', \'Q3024240\'], \'P156\': [\'Q17167\'], \'P155\': [\'Q2566630\'], \'P361\': [\'Q41493\'], \'P279\': [\'Q830852\'], \'P276\': [\'Q1048669\'], \'P1889\': [\'Q326197\'], \'P527\': [\'Q3921629\', \'Q119137625\'], \'P122\': [\'Q584683\'], \'P140\': [\'Q337547\'], \'P194\': [\'Q287980\', \'Q3510884\'], \'P37\': [\'Q397\'], \'P36\': [\'Q220\', \'Q18287233\'], \'P2936\': [\'Q397\', \'Q12289\'], \'P1906\': [\'Q55375123\'], \'P30\': [\'Q5401\', \'Q46\'], \'P1365\': [\'Q5171759\'], \'P1366\': [\'Q17167\'], \'P5008\': [\'Q6173448\'], \'P3075\': [\'Q337547\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P1151\': [\'Q11381903\'], \'P5125\': [\'Q48740750\'], \'P1792\': [\'Q10142763\'], \'P1313\': [\'Q23936560\'], \'P417\': [\'Q33923\', \'Q9200\'], \'P2959\': [\'Q22665612\'], \'P1376\': [\'Q18288160\', \'Q38\', \'Q1282\', \'Q15119\', \'Q170174\'], \'P194\': [\'Q48617968\'], \'P131\': [\'Q15119\', \'Q170174\', \'Q1558632\', \'Q1747689\', \'Q17167\'], \'P2596\': [\'Q1200427\', \'Q103122\', \'Q3678788\', \'Q22907236\'], \'P206\': [\'Q13712\', \'Q546600\', \'Q38882\'], \'P17\': [\'Q38\', \'Q170174\', \'Q3755547\', \'Q583038\', \'Q12544\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P190\': [\'Q90\', \'Q31487\', \'Q34647\', \'Q43196\', \'Q132830\'], \'P910\': [\'Q8682052\'], \'P1791\': [\'Q7977790\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q7142639\'], \'P4132\': [\'Q539808\', \'Q318917\', \'Q661936\', \'Q48612\', \'Q178435\'], \'P1018\': [\'Q48509\'], \'P5109\': [\'Q1775415\', \'Q499327\', \'Q1775461\'], \'P2959\': [\'Q12715487\'], \'P2579\': [\'Q1806979\', \'Q841090\', \'Q108000026\'], \'P31\': [\'Q45762\', \'Q436240\', \'Q34770\', \'Q839470\'], \'P5206\': [\'Q3921589\', \'Q3953978\', \'Q4009868\', \'Q19819479\'], \'P282\': [\'Q8229\', \'Q41670\'], \'P3103\': [\'Q623742\', \'Q192613\', \'Q12547192\', \'Q501405\', \'Q1234617\'], \'P279\': [\'Q33478\', \'Q85380120\'], \'P2989\': [\'Q131105\', \'Q185077\', \'Q146078\', \'Q146233\', \'Q145599\'], \'P5008\': [\'Q5460604\', \'Q6173448\'], \'P1343\': [\'Q19180675\', \'Q602358\', \'Q106727050\', \'Q20078554\', \'Q867541\'], \'P3823\': [\'Q61954942\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P282\': [\'Q8216\', \'Q190102\'], \'P31\': [\'Q34770\', \'Q2315359\'], \'P279\': [\'Q2042538\'], \'P910\': [\'Q8250729\'], \'P527\': [\'Q11732220\', \'Q11871956\', \'Q107358\', \'Q78612105\'], \'P1365\': [\'Q668366\'], \'P1366\': [\'Q36387\'], \'P3103\': [\'Q623742\', \'Q216497\', \'Q192613\'], \'P2579\': [\'Q16267481\', \'Q841090\', \'Q495527\'], \'P3161\': [\'Q682111\', \'Q473746\', \'Q22716\', \'Q527205\'], \'P2341\': [\'Q11772\', \'Q155552\'], \'P4132\': [\'Q651641\', \'Q178435\', \'Q318917\'], \'P1343\': [\'Q602358\', \'Q19180675\', \'Q19219752\', \'Q867541\'], \'P156\': [\'Q36510\', \'Q220607\', \'Q107358\'], \'P5109\': [\'Q499327\', \'Q1775415\', \'Q1775461\'], \'P1889\': [\'Q107358\'], \'P3823\': [\'Q61954942\'], \'P7084\': [\'Q84971021\'], \'P155\': [\'Q668366\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P1151\': [\'Q4997598\'], \'P5125\': [\'Q7112259\'], \'P2633\': [\'Q119716\'], \'P2959\': [\'Q20820598\'], \'P1424\': [\'Q6984392\', \'Q17588291\', \'Q6328695\', \'Q10902188\'], \'P421\': [\'Q5412093\', \'Q5412099\', \'Q16894228\', \'Q2356448\', \'Q5412117\'], \'P2184\': [\'Q7787\'], \'P910\': [\'Q4587662\'], \'P1791\': [\'Q18915272\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P1151\': [\'Q8252068\'], \'P1740\': [\'Q7140349\'], \'P910\': [\'Q5610083\'], \'P5125\': [\'Q7112190\'], \'P1791\': [\'Q23657023\'], \'P2633\': [\'Q2001617\'], \'P706\': [\'Q186198\'], \'P527\': [\'Q27231\', \'Q11708\', \'Q27275\', \'Q771405\', \'Q7204\'], \'P1465\': [\'Q7071117\'], \'P2959\': [\'Q22828169\', \'Q137645156\'], \'P361\': [\'Q2\', \'Q5401\', \'Q27527\', \'Q2035462\', \'Q125965270\'], \'P47\': [\'Q46\', \'Q15\'], \'P31\': [\'Q5107\', \'Q2418896\', \'Q82794\'], \'P1464\': [\'Q8042599\'], \'P421\': [\'Q3297477\', \'Q3522509\', \'Q3543509\', \'Q385504\', \'Q4127120\'], \'P2184\': [\'Q627531\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P1151\': [\'Q7486129\'], \'P1740\': [\'Q7140863\'], \'P910\': [\'Q5460710\', \'Q32816044\'], \'P5125\': [\'Q7112174\'], \'P2633\': [\'Q781650\'], \'P1830\': [\'Q1666473\'], \'P706\': [\'Q39061\', \'Q41228\'], \'P1464\': [\'Q8044365\'], \'P1465\': [\'Q9682611\'], \'P2959\': [\'Q22828260\'], \'P361\': [\'Q2035462\', \'Q2\', \'Q27527\', \'Q125965270\'], \'P47\': [\'Q5401\', \'Q48\'], \'P31\': [\'Q5107\', \'Q2221906\', \'Q82794\'], \'P610\': [\'Q1394606\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P279\': [\'Q7270\', \'Q123432\'], \'P31\': [\'Q1307214\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P527\': [\'Q201038\', \'Q17167\', \'Q2277\', \'Q12544\'], \'P832\': [\'Q207213\'], \'P910\': [\'Q7098243\'], \'P1151\': [\'Q10631465\'], \'P2184\': [\'Q830852\'], \'P1792\': [\'Q5652564\'], \'P2348\': [\'Q486761\'], \'P47\': [\'Q83311\', \'Q807748\', \'Q2528503\'], \'P5125\': [\'Q1216140\'], \'P706\': [\'Q72499\'], \'P6104\': [\'Q6337458\'], \'P2579\': [\'Q435608\'], \'P36\': [\'Q18287233\'], \'P30\': [\'Q46\', \'Q15\', \'Q48\', \'Q27527\'], \'P1343\': [\'Q4532138\', \'Q19219752\', \'Q135617903\'], \'P8744\': [\'Q15265460\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q4167410\'], \'P1889\': [\'Q17167\', \'Q175881\', \'Q1072140\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q14204246\', \'Q51539995\'], \'P527\': [\'Q6173639\', \'Q12153864\', \'Q6173773\', \'Q12154424\', \'Q12154377\'], \'P361\': [\'Q43375360\'], \'P144\': [\'Q43375360\'], \'P910\': [\'Q8925636\'], \'P360\': [\'Q116974583\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P527\': [\'Q6286\', \'Q6271\', \'Q6334\'], \'P910\': [\'Q7155263\'], \'P1343\': [\'Q2657718\', \'Q30059240\', \'Q602358\', \'Q19180675\', \'Q2041543\'], \'P710\': [\'Q17167\', \'Q2429397\'], \'P31\': [\'Q104212151\', \'Q198\'], \'P5008\': [\'Q6173448\'], \'P1424\': [\'Q6418868\'], \'P276\': [\'Q17167\', \'Q2429397\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q24195900\'], \'P31\': [\'Q8465\'], \'P361\': [\'Q3395322\'], \'P276\': [\'Q186513\'], \'P138\': [\'Q296238\'], \'P17\': [\'Q17167\'], \'P710\': [\'Q271108\', \'Q309155\', \'Q190992\', \'Q5011445\', \'Q1741306\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P527\': [\'Q75626\', \'Q75665\', \'Q76118\', \'Q552373\'], \'P910\': [\'Q8592033\'], \'P31\': [\'Q104212151\'], \'P1343\': [\'Q4114391\', \'Q602358\'], \'P276\': [\'Q83958\'], \'P710\': [\'Q1747689\'], \'P5008\': [\'Q6173448\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q198\'], \'P910\': [\'Q6255896\'], \'P793\': [\'Q1628304\', \'Q1274566\', \'Q2984753\', \'Q635028\', \'Q1267513\'], \'P276\': [\'Q38060\'], \'P1343\': [\'Q4114391\', \'Q106199\', \'Q20078554\'], \'P710\': [\'Q1747689\', \'Q273854\', \'Q22633\', \'Q849967\', \'Q1255605\'], \'P5008\': [\'Q6173448\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q8808774\'], \'P31\': [\'Q104212151\', \'Q198\'], \'P710\': [\'Q1747689\', \'Q1265446\', \'Q1165749\', \'Q941821\', \'Q2479252\'], \'P276\': [\'Q913582\'], \'P460\': [\'Q19716429\'], \'P2348\': [\'Q2839628\'], \'P527\': [\'Q129059100\', \'Q5742664\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q8465\'], \'P1343\': [\'Q4114391\', \'Q4114391\', \'Q4114391\', \'Q19180675\', \'Q123560817\'], \'P527\': [\'Q516760\', \'Q849653\', \'Q203681\', \'Q28531438\', \'Q525325\'], \'P910\': [\'Q9811318\'], \'P276\': [\'Q186513\', \'Q23522\', \'Q15\', \'Q32047\', \'Q202311\'], \'P361\': [\'Q1747183\'], \'P7867\': [\'Q84061055\'], \'P828\': [\'Q25238182\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q198\'], \'P1343\': [\'Q30059240\', \'Q19180675\', \'Q602358\', \'Q3181656\', \'Q124737616\'], \'P710\': [\'Q1747689\', \'Q1265446\', \'Q941821\', \'Q2341546\', \'Q1165749\'], \'P276\': [\'Q38\'], \'P910\': [\'Q32380558\'], \'P17\': [\'Q38\'], \'P527\': [\'Q85745805\', \'Q85745822\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P279\': [\'Q186081\'], \'P460\': [\'Q17522177\'], \'P910\': [\'Q7779952\'], \'P2579\': [\'Q1066186\', \'Q1069\', \'Q420\'], \'P1269\': [\'Q1190554\'], \'P1687\': [\'P2348\'], \'P1343\': [\'Q63284758\', \'Q19219752\'], \'P1889\': [\'Q30287\', \'Q630830\', \'Q4375074\', \'Q61068956\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q13406463\'], \'P360\': [\'Q11514315\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P361\': [\'Q1066186\'], \'P1343\': [\'Q3181656\', \'Q4532138\', \'Q61070632\'], \'P279\': [\'Q13582682\', \'Q97359583\'], \'P1889\': [\'Q11514315\'], \'P31\': [\'Q1047113\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q9763182\'], \'P279\': [\'Q28108\'], \'P1889\': [\'Q1307214\', \'Q19944802\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P5008\': [\'Q68235346\'], \'P31\': [\'Q2712963\', \'Q5962346\'], \'P279\': [\'Q96247293\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q7238098\', \'Q9858415\'], \'P279\': [\'Q1639378\'], \'P1269\': [\'Q7163\'], \'P527\': [\'Q1307214\', \'Q273005\', \'Q211606\', \'Q5193417\', \'Q2478386\'], \'P1889\': [\'Q1307214\'], \'P1382\': [\'Q20076236\'], \'P2579\': [\'Q745692\', \'Q32492\'], \'P31\': [\'Q96116695\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q4167836\'], \'P301\': [\'Q1307214\'], \'P4329\': [\'Q6526407\', \'Q15838730\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P361\': [\'Q36442\'], \'P279\': [\'Q28108\', \'Q183039\'], \'P910\': [\'Q7957175\'], \'P1889\': [\'Q1307214\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q9098906\'], \'P279\': [\'Q183039\', \'Q759524\', \'Q7225121\'], \'P1889\': [\'Q1307214\', \'Q183039\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P1269\': [\'Q1331392\'], \'P1382\': [\'Q28108\'], \'P31\': [\'Q5962346\'], \'P279\': [\'Q28108\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q8704186\'], \'P1269\': [\'Q43229\'], \'P279\': [\'Q6671777\', \'Q211606\'], \'P2579\': [\'Q2029930\'], \'P31\': [\'Q111972893\'], \'P1889\': [\'Q130751825\'], \'P13044\': [\'Q43229\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P910\': [\'Q5726315\'], \'P361\': [\'Q7275\', \'Q1200977\'], \'P1343\': [\'Q2041543\', \'Q3181656\', \'Q1029706\'], \'P279\': [\'Q11771944\'], \'P527\': [\'Q294414\', \'Q3754526\', \'Q699386\', \'Q12056862\', \'Q1519782\'], \'P31\': [\'Q11862829\'], \'P2579\': [\'Q2736989\', \'Q125461740\'], \'P5008\': [\'Q6173448\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q11753321\'], \'P1423\': [\'Q1307214\'], \'P9926\': [\'Q54069\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P31\': [\'Q11266439\'], \'P1423\': [\'Q1307214\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
  property_summary: '{\'P301\': [\'Q48349\'], \'P31\': [\'Q4167836\'], \'P1753\': [\'Q1151047\'], \'P4329\': [\'Q7477250\']}',
  status: 'candidate',
  proposed_by: 'sca_traversal',
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
