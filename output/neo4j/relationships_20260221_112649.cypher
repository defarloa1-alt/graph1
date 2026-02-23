// Entity Relationship Import - REQ-FUNC-010
// Generated: 2026-02-21T11:26:49.194224
// Entities: 300


// Q17167 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --INSTANCE_OF--> Q1307214
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --INSTANCE_OF--> Q48349
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q48349'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_OFFICIAL_RELIGION--> Q337547
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q337547'})
MERGE (from)-[r:HAS_OFFICIAL_RELIGION]->(to)
ON CREATE SET
  r.wikidata_pid = 'P140',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_LEGISLATIVE_BODY--> Q130614
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q130614'})
MERGE (from)-[r:HAS_LEGISLATIVE_BODY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P194',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_LEGISLATIVE_BODY--> Q1114821
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q1114821'})
MERGE (from)-[r:HAS_LEGISLATIVE_BODY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P194',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_CURRENCY--> Q952064
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:HAS_CURRENCY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P38',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_PARTS--> Q2839628
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q2839628'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_PARTS--> Q6106068
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q6106068'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_PARTS--> Q2815472
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q2815472'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --REPLACED_BY--> Q2277
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --REPLACED_BY--> Q206414
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q206414'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --FOLLOWS--> Q201038
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --ON_CONTINENT--> Q15
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --REPLACES--> Q201038
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --PART_OF--> Q1747689
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_SIGNIFICANT_EVENT--> Q124988
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q124988'})
MERGE (from)-[r:HAS_SIGNIFICANT_EVENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P793',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_SIGNIFICANT_EVENT--> Q3778726
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q3778726'})
MERGE (from)-[r:HAS_SIGNIFICANT_EVENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P793',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_SIGNIFICANT_EVENT--> Q75813
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q75813'})
MERGE (from)-[r:HAS_SIGNIFICANT_EVENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P793',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_SIGNIFICANT_EVENT--> Q202161
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q202161'})
MERGE (from)-[r:HAS_SIGNIFICANT_EVENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P793',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_SIGNIFICANT_EVENT--> Q596373
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q596373'})
MERGE (from)-[r:HAS_SIGNIFICANT_EVENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P793',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_SIGNIFICANT_EVENT--> Q1238338
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q1238338'})
MERGE (from)-[r:HAS_SIGNIFICANT_EVENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P793',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_SIGNIFICANT_EVENT--> Q677316
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q677316'})
MERGE (from)-[r:HAS_SIGNIFICANT_EVENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P793',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --FOLLOWED_BY--> Q2277
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q17167 --FOLLOWED_BY--> Q206414
MATCH (from:Entity {qid: 'Q17167'})
MATCH (to:Entity {qid: 'Q206414'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q11514315 --SUBCLASS_OF--> Q6428674
MATCH (from:Entity {qid: 'Q11514315'})
MATCH (to:Entity {qid: 'Q6428674'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1307214 --SUBCLASS_OF--> Q183039
MATCH (from:Entity {qid: 'Q1307214'})
MATCH (to:Entity {qid: 'Q183039'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1307214 --SUBCLASS_OF--> Q2752458
MATCH (from:Entity {qid: 'Q1307214'})
MATCH (to:Entity {qid: 'Q2752458'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1307214 --SUBCLASS_OF--> Q28108
MATCH (from:Entity {qid: 'Q1307214'})
MATCH (to:Entity {qid: 'Q28108'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1307214 --HAS_PARTS--> Q759524
MATCH (from:Entity {qid: 'Q1307214'})
MATCH (to:Entity {qid: 'Q759524'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1307214 --HAS_PARTS--> Q31728
MATCH (from:Entity {qid: 'Q1307214'})
MATCH (to:Entity {qid: 'Q31728'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q48349 --SUBCLASS_OF--> Q3624078
MATCH (from:Entity {qid: 'Q48349'})
MATCH (to:Entity {qid: 'Q3624078'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q48349 --INSTANCE_OF--> Q7269
MATCH (from:Entity {qid: 'Q48349'})
MATCH (to:Entity {qid: 'Q7269'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3024240 --SUBCLASS_OF--> Q96196009
MATCH (from:Entity {qid: 'Q3024240'})
MATCH (to:Entity {qid: 'Q96196009'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3024240 --SUBCLASS_OF--> Q19832712
MATCH (from:Entity {qid: 'Q3024240'})
MATCH (to:Entity {qid: 'Q19832712'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3024240 --SUBCLASS_OF--> Q6256
MATCH (from:Entity {qid: 'Q3024240'})
MATCH (to:Entity {qid: 'Q6256'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6944405 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q6944405'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6944405 --FOLLOWS--> Q8678306
MATCH (from:Entity {qid: 'Q6944405'})
MATCH (to:Entity {qid: 'Q8678306'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q130614 --INSTANCE_OF--> Q11204
MATCH (from:Entity {qid: 'Q130614'})
MATCH (to:Entity {qid: 'Q11204'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q130614 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q130614'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q130614 --SUBCLASS_OF--> Q2915100
MATCH (from:Entity {qid: 'Q130614'})
MATCH (to:Entity {qid: 'Q2915100'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1114821 --INSTANCE_OF--> Q17197366
MATCH (from:Entity {qid: 'Q1114821'})
MATCH (to:Entity {qid: 'Q17197366'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1114821 --SUBCLASS_OF--> Q11204
MATCH (from:Entity {qid: 'Q1114821'})
MATCH (to:Entity {qid: 'Q11204'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1114821 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q1114821'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q952064 --INSTANCE_OF--> Q17524420
MATCH (from:Entity {qid: 'Q952064'})
MATCH (to:Entity {qid: 'Q17524420'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q952064 --HAS_PARTS--> Q662137
MATCH (from:Entity {qid: 'Q952064'})
MATCH (to:Entity {qid: 'Q662137'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q952064 --HAS_PARTS--> Q638048
MATCH (from:Entity {qid: 'Q952064'})
MATCH (to:Entity {qid: 'Q638048'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q952064 --SUBCLASS_OF--> Q8142
MATCH (from:Entity {qid: 'Q952064'})
MATCH (to:Entity {qid: 'Q8142'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q952064 --SUBCLASS_OF--> Q28783456
MATCH (from:Entity {qid: 'Q952064'})
MATCH (to:Entity {qid: 'Q28783456'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q14618893
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q14618893'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q17167
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q11772
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q11772'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q181264
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q181264'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q134178
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q134178'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q17161
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q17161'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q245813
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q245813'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q12544
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q3617880
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q3617880'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q1778719
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q1778719'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q83958
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q83958'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q131802
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q131802'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --HAS_PARTS--> Q6111354
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q6111354'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --FOLLOWED_BY--> Q217050
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q217050'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --INSTANCE_OF--> Q1292119
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q1292119'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --SUBCLASS_OF--> Q41493
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q41493'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --FOLLOWS--> Q98270938
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q98270938'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --PART_OF--> Q41493
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q41493'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --LOCATED_IN--> Q11772
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q11772'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q486761 --LOCATED_IN--> Q1747689
MATCH (from:Entity {qid: 'Q486761'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13285410 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q13285410'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2839628 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q2839628'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2839628 --PART_OF--> Q17167
MATCH (from:Entity {qid: 'Q2839628'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2839628 --FOLLOWS--> Q201038
MATCH (from:Entity {qid: 'Q2839628'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2839628 --FOLLOWS--> Q16931679
MATCH (from:Entity {qid: 'Q2839628'})
MATCH (to:Entity {qid: 'Q16931679'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2839628 --FOLLOWS--> Q119137625
MATCH (from:Entity {qid: 'Q2839628'})
MATCH (to:Entity {qid: 'Q119137625'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2839628 --FOLLOWED_BY--> Q6106068
MATCH (from:Entity {qid: 'Q2839628'})
MATCH (to:Entity {qid: 'Q6106068'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2839628 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q2839628'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6106068 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q6106068'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6106068 --PART_OF--> Q17167
MATCH (from:Entity {qid: 'Q6106068'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6106068 --FOLLOWS--> Q2839628
MATCH (from:Entity {qid: 'Q6106068'})
MATCH (to:Entity {qid: 'Q2839628'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6106068 --FOLLOWED_BY--> Q2815472
MATCH (from:Entity {qid: 'Q6106068'})
MATCH (to:Entity {qid: 'Q2815472'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6106068 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q6106068'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2815472 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q2815472'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2815472 --PART_OF--> Q17167
MATCH (from:Entity {qid: 'Q2815472'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2815472 --FOLLOWS--> Q6106068
MATCH (from:Entity {qid: 'Q2815472'})
MATCH (to:Entity {qid: 'Q6106068'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2815472 --FOLLOWED_BY--> Q787204
MATCH (from:Entity {qid: 'Q2815472'})
MATCH (to:Entity {qid: 'Q787204'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2815472 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q2815472'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CAPITAL--> Q16869
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q16869'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CAPITAL--> Q13364
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q13364'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CAPITAL--> Q18287233
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q18287233'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_OFFICIAL_LANGUAGE--> Q35497
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q35497'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CURRENCY--> Q208041
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q208041'})
MERGE (from)-[r:HAS_CURRENCY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P38',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CURRENCY--> Q187776
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q187776'})
MERGE (from)-[r:HAS_CURRENCY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P38',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CURRENCY--> Q952064
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:HAS_CURRENCY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P38',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CURRENCY--> Q476078
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q476078'})
MERGE (from)-[r:HAS_CURRENCY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P38',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_CURRENCY--> Q376895
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q376895'})
MERGE (from)-[r:HAS_CURRENCY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P38',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_OFFICIAL_RELIGION--> Q337547
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q337547'})
MERGE (from)-[r:HAS_OFFICIAL_RELIGION]->(to)
ON CREATE SET
  r.wikidata_pid = 'P140',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_OFFICIAL_RELIGION--> Q7603670
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q7603670'})
MERGE (from)-[r:HAS_OFFICIAL_RELIGION]->(to)
ON CREATE SET
  r.wikidata_pid = 'P140',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --INSTANCE_OF--> Q48349
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q48349'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --SHARES_BORDER_WITH--> Q1986139
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1986139'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q3626028
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q3626028'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q747040
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q747040'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q1126678
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1126678'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q170062
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q170062'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q765845
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q765845'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q202311
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q202311'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q623322
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q623322'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q360922
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q360922'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q309270
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q309270'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q221353
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q221353'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q1254480
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1254480'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q685537
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q685537'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q918059
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q918059'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q33490
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q33490'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q4819648
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q4819648'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q971609
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q971609'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q12277185
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q12277185'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q12270914
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q12270914'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q1820754
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1820754'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q1249412
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1249412'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q715376
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q715376'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q206443
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q206443'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q10971
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q10971'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q152136
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q152136'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q219415
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q219415'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q1330965
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1330965'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q734505
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q734505'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q18236771
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q18236771'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q3878417
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q3878417'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q1247297
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1247297'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q642188
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q642188'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q156789
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q156789'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q281345
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q281345'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q691321
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q691321'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q207118
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q207118'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q27150039
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q27150039'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q635058
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q635058'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q913582
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q913582'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q181238
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q181238'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q210718
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q210718'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q185103
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q185103'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q913382
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q913382'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q2967757
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q2967757'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q26897
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q26897'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q40169
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q40169'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q11939617
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q11939617'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --CONTAINS--> Q1669578
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1669578'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --REPLACED_BY--> Q42834
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q42834'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --REPLACED_BY--> Q12544
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --REPLACES--> Q17167
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --ON_CONTINENT--> Q15
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --HAS_PARTS--> Q787204
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q787204'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --PART_OF--> Q1747689
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2277 --FOLLOWS--> Q17167
MATCH (from:Entity {qid: 'Q2277'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206414 --INSTANCE_OF--> Q1307214
MATCH (from:Entity {qid: 'Q206414'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206414 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q206414'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206414 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q206414'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206414 --PART_OF--> Q14618893
MATCH (from:Entity {qid: 'Q206414'})
MATCH (to:Entity {qid: 'Q14618893'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206414 --FOLLOWED_BY--> Q238399
MATCH (from:Entity {qid: 'Q206414'})
MATCH (to:Entity {qid: 'Q238399'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206414 --REPLACES--> Q17167
MATCH (from:Entity {qid: 'Q206414'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206414 --FOLLOWS--> Q17167
MATCH (from:Entity {qid: 'Q206414'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --FOLLOWED_BY--> Q17167
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --FOLLOWS--> Q2566630
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q2566630'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --PART_OF--> Q41493
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q41493'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --SUBCLASS_OF--> Q830852
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q830852'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --LOCATED_IN--> Q1048669
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q1048669'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --HAS_PARTS--> Q3921629
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q3921629'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --HAS_PARTS--> Q119137625
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q119137625'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --HAS_OFFICIAL_RELIGION--> Q337547
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q337547'})
MERGE (from)-[r:HAS_OFFICIAL_RELIGION]->(to)
ON CREATE SET
  r.wikidata_pid = 'P140',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --HAS_CAPITAL--> Q18287233
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q18287233'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --REPLACES--> Q5171759
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q5171759'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q201038 --REPLACED_BY--> Q17167
MATCH (from:Entity {qid: 'Q201038'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q170174
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q583038
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q583038'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q12544
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q172579
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q172579'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q201038
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q42834
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q42834'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --LOCATED_IN_COUNTRY--> Q237
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q237'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q241693
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q241693'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q241733
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q241733'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242105
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242105'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242513
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242513'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242558
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242558'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q19326
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q19326'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242637
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242637'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242645
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242645'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242703
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242703'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242965
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242965'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242998
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242998'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q243311
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q243311'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q243497
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q243497'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q191115
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q191115'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q241911
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q241911'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242120
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242120'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q190963
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q190963'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242661
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242661'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242926
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242926'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q243133
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q243133'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q243188
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q243188'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --SHARES_BORDER_WITH--> Q242710
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q242710'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --CONTAINS--> Q16494134
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q16494134'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --CONTAINS--> Q16003470
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q16003470'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --CONTAINS--> Q16481953
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q16481953'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --CONTAINS--> Q16481966
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q16481966'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --CONTAINS--> Q16495467
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q16495467'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --CONTAINS--> Q16481977
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q16481977'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --CONTAINS--> Q16481992
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q16481992'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --CONTAINS--> Q16482002
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q16482002'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q220 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q220'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q397 --LOCATED_IN_COUNTRY--> Q237
MATCH (from:Entity {qid: 'Q397'})
MATCH (to:Entity {qid: 'Q237'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q46 --SHARES_BORDER_WITH--> Q48
MATCH (from:Entity {qid: 'Q46'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q48 --SHARES_BORDER_WITH--> Q46
MATCH (from:Entity {qid: 'Q48'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q48 --SHARES_BORDER_WITH--> Q15
MATCH (from:Entity {qid: 'Q48'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15 --SHARES_BORDER_WITH--> Q48
MATCH (from:Entity {qid: 'Q15'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q666680 --INSTANCE_OF--> Q1307214
MATCH (from:Entity {qid: 'Q666680'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --HAS_PARTS--> Q201038
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --HAS_PARTS--> Q17167
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --HAS_PARTS--> Q2277
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --HAS_PARTS--> Q12544
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --HAS_CAPITAL--> Q18287233
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q18287233'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --ON_CONTINENT--> Q15
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --FOLLOWED_BY--> Q12544
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1747689 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q1747689'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q124988 --LOCATED_IN--> Q17167
MATCH (from:Entity {qid: 'Q124988'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3778726 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q3778726'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q75813 --LOCATED_IN--> Q83958
MATCH (from:Entity {qid: 'Q75813'})
MATCH (to:Entity {qid: 'Q83958'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q596373 --LOCATED_IN--> Q913582
MATCH (from:Entity {qid: 'Q596373'})
MATCH (to:Entity {qid: 'Q913582'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1238338 --LOCATED_IN--> Q15
MATCH (from:Entity {qid: 'Q1238338'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1238338 --LOCATED_IN--> Q202311
MATCH (from:Entity {qid: 'Q1238338'})
MATCH (to:Entity {qid: 'Q202311'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q677316 --LOCATED_IN--> Q38
MATCH (from:Entity {qid: 'Q677316'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q677316 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q677316'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q183039 --SUBCLASS_OF--> Q28108
MATCH (from:Entity {qid: 'Q183039'})
MATCH (to:Entity {qid: 'Q28108'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q28108 --HAS_PARTS--> Q1307214
MATCH (from:Entity {qid: 'Q28108'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q54069 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q54069'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q5589178 --SUBCLASS_OF--> Q28108
MATCH (from:Entity {qid: 'Q5589178'})
MATCH (to:Entity {qid: 'Q28108'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q5589178 --SUBCLASS_OF--> Q183039
MATCH (from:Entity {qid: 'Q5589178'})
MATCH (to:Entity {qid: 'Q183039'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q19944802 --SUBCLASS_OF--> Q183039
MATCH (from:Entity {qid: 'Q19944802'})
MATCH (to:Entity {qid: 'Q183039'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q19944802 --SUBCLASS_OF--> Q759524
MATCH (from:Entity {qid: 'Q19944802'})
MATCH (to:Entity {qid: 'Q759524'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q20076236 --SUBCLASS_OF--> Q28108
MATCH (from:Entity {qid: 'Q20076236'})
MATCH (to:Entity {qid: 'Q28108'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6135095 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q6135095'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3624078 --SUBCLASS_OF--> Q6256
MATCH (from:Entity {qid: 'Q3624078'})
MATCH (to:Entity {qid: 'Q6256'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q7269 --INSTANCE_OF--> Q1307214
MATCH (from:Entity {qid: 'Q7269'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q7238252 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q7238252'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3591867 --SUBCLASS_OF--> Q6256
MATCH (from:Entity {qid: 'Q3591867'})
MATCH (to:Entity {qid: 'Q6256'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8678306 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q8678306'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8678306 --FOLLOWED_BY--> Q6944405
MATCH (from:Entity {qid: 'Q8678306'})
MATCH (to:Entity {qid: 'Q6944405'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8251375 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q8251375'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q107013262 --INSTANCE_OF--> Q17524420
MATCH (from:Entity {qid: 'Q107013262'})
MATCH (to:Entity {qid: 'Q17524420'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q107013262 --PART_OF--> Q107013169
MATCH (from:Entity {qid: 'Q107013262'})
MATCH (to:Entity {qid: 'Q107013169'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q107013262 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q107013262'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q107013169 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q107013169'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q107013169 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q107013169'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q107013169 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q107013169'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q107013169 --PART_OF--> Q1200427
MATCH (from:Entity {qid: 'Q107013169'})
MATCH (to:Entity {qid: 'Q1200427'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1144514 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q1144514'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q32899669 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q32899669'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8386687 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q8386687'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q662137 --PART_OF--> Q952064
MATCH (from:Entity {qid: 'Q662137'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q662137 --INSTANCE_OF--> Q17524420
MATCH (from:Entity {qid: 'Q662137'})
MATCH (to:Entity {qid: 'Q17524420'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q662137 --FOLLOWED_BY--> Q638048
MATCH (from:Entity {qid: 'Q662137'})
MATCH (to:Entity {qid: 'Q638048'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q638048 --PART_OF--> Q952064
MATCH (from:Entity {qid: 'Q638048'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q638048 --INSTANCE_OF--> Q17524420
MATCH (from:Entity {qid: 'Q638048'})
MATCH (to:Entity {qid: 'Q17524420'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q638048 --FOLLOWS--> Q662137
MATCH (from:Entity {qid: 'Q638048'})
MATCH (to:Entity {qid: 'Q662137'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q28783456 --SUBCLASS_OF--> Q8142
MATCH (from:Entity {qid: 'Q28783456'})
MATCH (to:Entity {qid: 'Q8142'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q14618893 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q14618893'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q14618893 --PART_OF--> Q2671119
MATCH (from:Entity {qid: 'Q14618893'})
MATCH (to:Entity {qid: 'Q2671119'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q14618893 --INSTANCE_OF--> Q17524420
MATCH (from:Entity {qid: 'Q14618893'})
MATCH (to:Entity {qid: 'Q17524420'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q14618893 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q14618893'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q14618893 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q14618893'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q14618893 --SUBCLASS_OF--> Q2277
MATCH (from:Entity {qid: 'Q14618893'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q11772 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q11772'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q11772 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q11772'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q11772 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q11772'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q11772 --ON_CONTINENT--> Q15
MATCH (from:Entity {qid: 'Q11772'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q181264 --INSTANCE_OF--> Q1292119
MATCH (from:Entity {qid: 'Q181264'})
MATCH (to:Entity {qid: 'Q1292119'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q181264 --REPLACES--> Q134178
MATCH (from:Entity {qid: 'Q181264'})
MATCH (to:Entity {qid: 'Q134178'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q134178 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q134178'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q134178 --INSTANCE_OF--> Q1292119
MATCH (from:Entity {qid: 'Q134178'})
MATCH (to:Entity {qid: 'Q1292119'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q134178 --REPLACED_BY--> Q181264
MATCH (from:Entity {qid: 'Q134178'})
MATCH (to:Entity {qid: 'Q181264'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q245813 --PART_OF--> Q11772
MATCH (from:Entity {qid: 'Q245813'})
MATCH (to:Entity {qid: 'Q11772'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --INSTANCE_OF--> Q48349
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q48349'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --HAS_CAPITAL--> Q16869
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q16869'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --ON_CONTINENT--> Q15
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --REPLACES--> Q2277
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --REPLACES--> Q42834
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q42834'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --REPLACES--> Q178897
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q178897'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --REPLACED_BY--> Q178897
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q178897'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --SHARES_BORDER_WITH--> Q42834
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q42834'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --PART_OF--> Q2277
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --FOLLOWS--> Q1747689
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12544 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q12544'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q83958 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q83958'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q83958 --HAS_OFFICIAL_LANGUAGE--> Q35497
MATCH (from:Entity {qid: 'Q83958'})
MATCH (to:Entity {qid: 'Q35497'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q83958 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q83958'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q83958 --LOCATED_IN_COUNTRY--> Q83958
MATCH (from:Entity {qid: 'Q83958'})
MATCH (to:Entity {qid: 'Q83958'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6111354 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q6111354'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6111354 --PART_OF--> Q486761
MATCH (from:Entity {qid: 'Q6111354'})
MATCH (to:Entity {qid: 'Q486761'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6111354 --SUBCLASS_OF--> Q1747689
MATCH (from:Entity {qid: 'Q6111354'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8381710 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q8381710'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q217050 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q217050'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q217050 --FOLLOWS--> Q486761
MATCH (from:Entity {qid: 'Q217050'})
MATCH (to:Entity {qid: 'Q486761'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q217050 --SUBCLASS_OF--> Q41493
MATCH (from:Entity {qid: 'Q217050'})
MATCH (to:Entity {qid: 'Q41493'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q41493 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q41493'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q41493 --HAS_PARTS--> Q486761
MATCH (from:Entity {qid: 'Q41493'})
MATCH (to:Entity {qid: 'Q486761'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q41493 --HAS_PARTS--> Q217050
MATCH (from:Entity {qid: 'Q41493'})
MATCH (to:Entity {qid: 'Q217050'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q98270938 --PART_OF--> Q41493
MATCH (from:Entity {qid: 'Q98270938'})
MATCH (to:Entity {qid: 'Q41493'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q98270938 --FOLLOWED_BY--> Q486761
MATCH (from:Entity {qid: 'Q98270938'})
MATCH (to:Entity {qid: 'Q486761'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q112939719 --HAS_PARTS--> Q830852
MATCH (from:Entity {qid: 'Q112939719'})
MATCH (to:Entity {qid: 'Q830852'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16931679 --LOCATED_IN--> Q1747689
MATCH (from:Entity {qid: 'Q16931679'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16931679 --LOCATED_IN_COUNTRY--> Q201038
MATCH (from:Entity {qid: 'Q16931679'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16931679 --FOLLOWS--> Q119137625
MATCH (from:Entity {qid: 'Q16931679'})
MATCH (to:Entity {qid: 'Q119137625'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16931679 --FOLLOWED_BY--> Q2839628
MATCH (from:Entity {qid: 'Q16931679'})
MATCH (to:Entity {qid: 'Q2839628'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q119137625 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q119137625'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q119137625 --FOLLOWS--> Q3921629
MATCH (from:Entity {qid: 'Q119137625'})
MATCH (to:Entity {qid: 'Q3921629'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q119137625 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q119137625'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q119137625 --FOLLOWED_BY--> Q16931679
MATCH (from:Entity {qid: 'Q119137625'})
MATCH (to:Entity {qid: 'Q16931679'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q119137625 --FOLLOWED_BY--> Q2839628
MATCH (from:Entity {qid: 'Q119137625'})
MATCH (to:Entity {qid: 'Q2839628'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q119137625 --SUBCLASS_OF--> Q201038
MATCH (from:Entity {qid: 'Q119137625'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q119137625 --PART_OF--> Q201038
MATCH (from:Entity {qid: 'Q119137625'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16869 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q16869'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16869 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q16869'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16869 --LOCATED_IN_COUNTRY--> Q12544
MATCH (from:Entity {qid: 'Q16869'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16869 --LOCATED_IN_COUNTRY--> Q178897
MATCH (from:Entity {qid: 'Q16869'})
MATCH (to:Entity {qid: 'Q178897'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16869 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q16869'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13364 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q13364'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13364 --LOCATED_IN_COUNTRY--> Q170174
MATCH (from:Entity {qid: 'Q13364'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13364 --LOCATED_IN_COUNTRY--> Q170174
MATCH (from:Entity {qid: 'Q13364'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13364 --LOCATED_IN_COUNTRY--> Q170174
MATCH (from:Entity {qid: 'Q13364'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13364 --LOCATED_IN_COUNTRY--> Q170174
MATCH (from:Entity {qid: 'Q13364'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13364 --LOCATED_IN_COUNTRY--> Q172579
MATCH (from:Entity {qid: 'Q13364'})
MATCH (to:Entity {qid: 'Q172579'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13364 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q13364'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q18287233 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q18287233'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q173424 --INSTANCE_OF--> Q1307214
MATCH (from:Entity {qid: 'Q173424'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q173424 --INSTANCE_OF--> Q183039
MATCH (from:Entity {qid: 'Q173424'})
MATCH (to:Entity {qid: 'Q183039'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q173424 --SUBCLASS_OF--> Q28108
MATCH (from:Entity {qid: 'Q173424'})
MATCH (to:Entity {qid: 'Q28108'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q173424 --SUBCLASS_OF--> Q20076236
MATCH (from:Entity {qid: 'Q173424'})
MATCH (to:Entity {qid: 'Q20076236'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q173424 --HAS_PARTS--> Q7269
MATCH (from:Entity {qid: 'Q173424'})
MATCH (to:Entity {qid: 'Q7269'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q174450 --INSTANCE_OF--> Q1307214
MATCH (from:Entity {qid: 'Q174450'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q174450 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q174450'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q208041 --SUBCLASS_OF--> Q952064
MATCH (from:Entity {qid: 'Q208041'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q208041 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q208041'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q187776 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q187776'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q187776 --INSTANCE_OF--> Q8142
MATCH (from:Entity {qid: 'Q187776'})
MATCH (to:Entity {qid: 'Q8142'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q187776 --PART_OF--> Q952064
MATCH (from:Entity {qid: 'Q187776'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q476078 --INSTANCE_OF--> Q8142
MATCH (from:Entity {qid: 'Q476078'})
MATCH (to:Entity {qid: 'Q8142'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q476078 --SUBCLASS_OF--> Q952064
MATCH (from:Entity {qid: 'Q476078'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q476078 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q476078'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q376895 --INSTANCE_OF--> Q8142
MATCH (from:Entity {qid: 'Q376895'})
MATCH (to:Entity {qid: 'Q8142'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q376895 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q376895'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q376895 --PART_OF--> Q952064
MATCH (from:Entity {qid: 'Q376895'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q7603670 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q7603670'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2671119 --HAS_PARTS--> Q787204
MATCH (from:Entity {qid: 'Q2671119'})
MATCH (to:Entity {qid: 'Q787204'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2671119 --HAS_PARTS--> Q206414
MATCH (from:Entity {qid: 'Q2671119'})
MATCH (to:Entity {qid: 'Q206414'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2671119 --HAS_PARTS--> Q14618893
MATCH (from:Entity {qid: 'Q2671119'})
MATCH (to:Entity {qid: 'Q14618893'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2671119 --HAS_PARTS--> Q238399
MATCH (from:Entity {qid: 'Q2671119'})
MATCH (to:Entity {qid: 'Q238399'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2671119 --HAS_PARTS--> Q174450
MATCH (from:Entity {qid: 'Q2671119'})
MATCH (to:Entity {qid: 'Q174450'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q842606 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q842606'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q7209 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q7209'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q7209 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q7209'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q7209 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q7209'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q32642796 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q32642796'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42859641 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q42859641'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1986139 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q1986139'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1986139 --INSTANCE_OF--> Q48349
MATCH (from:Entity {qid: 'Q1986139'})
MATCH (to:Entity {qid: 'Q48349'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1986139 --INSTANCE_OF--> Q816829
MATCH (from:Entity {qid: 'Q1986139'})
MATCH (to:Entity {qid: 'Q816829'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1986139 --SHARES_BORDER_WITH--> Q2277
MATCH (from:Entity {qid: 'Q1986139'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1986139 --LOCATED_IN_COUNTRY--> Q1986139
MATCH (from:Entity {qid: 'Q1986139'})
MATCH (to:Entity {qid: 'Q1986139'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1986139 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q1986139'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1986139 --REPLACED_BY--> Q765845
MATCH (from:Entity {qid: 'Q1986139'})
MATCH (to:Entity {qid: 'Q765845'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3626028 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q3626028'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q747040 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q747040'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q747040 --SHARES_BORDER_WITH--> Q1126678
MATCH (from:Entity {qid: 'Q747040'})
MATCH (to:Entity {qid: 'Q1126678'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q747040 --REPLACED_BY--> Q219415
MATCH (from:Entity {qid: 'Q747040'})
MATCH (to:Entity {qid: 'Q219415'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1126678 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q1126678'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1126678 --SHARES_BORDER_WITH--> Q747040
MATCH (from:Entity {qid: 'Q1126678'})
MATCH (to:Entity {qid: 'Q747040'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1126678 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q1126678'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170062 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q170062'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170062 --REPLACED_BY--> Q642188
MATCH (from:Entity {qid: 'Q170062'})
MATCH (to:Entity {qid: 'Q642188'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q765845 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q765845'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q765845 --LOCATED_IN_COUNTRY--> Q12544
MATCH (from:Entity {qid: 'Q765845'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q765845 --REPLACES--> Q1986139
MATCH (from:Entity {qid: 'Q765845'})
MATCH (to:Entity {qid: 'Q1986139'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q202311 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q202311'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q202311 --LOCATED_IN_COUNTRY--> Q12544
MATCH (from:Entity {qid: 'Q202311'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q202311 --SHARES_BORDER_WITH--> Q221353
MATCH (from:Entity {qid: 'Q202311'})
MATCH (to:Entity {qid: 'Q221353'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q202311 --ON_CONTINENT--> Q15
MATCH (from:Entity {qid: 'Q202311'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q623322 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q623322'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q309270 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q309270'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q221353 --SHARES_BORDER_WITH--> Q1669578
MATCH (from:Entity {qid: 'Q221353'})
MATCH (to:Entity {qid: 'Q1669578'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q221353 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q221353'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1254480 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q1254480'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q685537 --PART_OF--> Q185103
MATCH (from:Entity {qid: 'Q685537'})
MATCH (to:Entity {qid: 'Q185103'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q685537 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q685537'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q918059 --PART_OF--> Q185103
MATCH (from:Entity {qid: 'Q918059'})
MATCH (to:Entity {qid: 'Q185103'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q918059 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q918059'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q33490 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q33490'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q4819648 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q4819648'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q971609 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q971609'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q971609 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q971609'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q971609 --HAS_PARTS--> Q12277185
MATCH (from:Entity {qid: 'Q971609'})
MATCH (to:Entity {qid: 'Q12277185'})
MERGE (from)-[r:HAS_PARTS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P527',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12277185 --PART_OF--> Q971609
MATCH (from:Entity {qid: 'Q12277185'})
MATCH (to:Entity {qid: 'Q971609'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12277185 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q12277185'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12270914 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q12270914'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q12270914 --REPLACES--> Q12277185
MATCH (from:Entity {qid: 'Q12270914'})
MATCH (to:Entity {qid: 'Q12277185'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1249412 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q1249412'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q715376 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q715376'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q715376 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q715376'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206443 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q206443'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206443 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q206443'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206443 --LOCATED_IN_COUNTRY--> Q42834
MATCH (from:Entity {qid: 'Q206443'})
MATCH (to:Entity {qid: 'Q42834'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q206443 --PART_OF--> Q2277
MATCH (from:Entity {qid: 'Q206443'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q10971 --LOCATED_IN_COUNTRY--> Q42834
MATCH (from:Entity {qid: 'Q10971'})
MATCH (to:Entity {qid: 'Q42834'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q10971 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q10971'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q152136 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q152136'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q152136 --PART_OF--> Q2277
MATCH (from:Entity {qid: 'Q152136'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q219415 --PART_OF--> Q1747689
MATCH (from:Entity {qid: 'Q219415'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q219415 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q219415'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1330965 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q1330965'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q734505 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q734505'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q734505 --ON_CONTINENT--> Q15
MATCH (from:Entity {qid: 'Q734505'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q18236771 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q18236771'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3878417 --PART_OF--> Q2277
MATCH (from:Entity {qid: 'Q3878417'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3878417 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q3878417'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1247297 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q1247297'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1247297 --REPLACES--> Q170062
MATCH (from:Entity {qid: 'Q1247297'})
MATCH (to:Entity {qid: 'Q170062'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q642188 --REPLACES--> Q170062
MATCH (from:Entity {qid: 'Q642188'})
MATCH (to:Entity {qid: 'Q170062'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q642188 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q642188'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q156789 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q156789'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q156789 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q156789'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q281345 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q281345'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q691321 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q691321'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q207118 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q207118'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q207118 --REPLACED_BY--> Q27150039
MATCH (from:Entity {qid: 'Q207118'})
MATCH (to:Entity {qid: 'Q27150039'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q27150039 --REPLACES--> Q207118
MATCH (from:Entity {qid: 'Q27150039'})
MATCH (to:Entity {qid: 'Q207118'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q27150039 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q27150039'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q635058 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q635058'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q913582 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q913582'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q913582 --HAS_CAPITAL--> Q18287233
MATCH (from:Entity {qid: 'Q913582'})
MATCH (to:Entity {qid: 'Q18287233'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q913582 --HAS_CAPITAL--> Q13364
MATCH (from:Entity {qid: 'Q913582'})
MATCH (to:Entity {qid: 'Q13364'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q181238 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q181238'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q210718 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q210718'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q210718 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q210718'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q210718 --LOCATED_IN_COUNTRY--> Q12544
MATCH (from:Entity {qid: 'Q210718'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q185103 --PART_OF--> Q2277
MATCH (from:Entity {qid: 'Q185103'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q185103 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q185103'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q913382 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q913382'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2967757 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q2967757'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2967757 --LOCATED_IN_COUNTRY--> Q12544
MATCH (from:Entity {qid: 'Q2967757'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q26897 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q26897'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q26897 --SHARES_BORDER_WITH--> Q715376
MATCH (from:Entity {qid: 'Q26897'})
MATCH (to:Entity {qid: 'Q715376'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q26897 --SHARES_BORDER_WITH--> Q10971
MATCH (from:Entity {qid: 'Q26897'})
MATCH (to:Entity {qid: 'Q10971'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q26897 --PART_OF--> Q2277
MATCH (from:Entity {qid: 'Q26897'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q40169 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q40169'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q40169 --REPLACES--> Q1986139
MATCH (from:Entity {qid: 'Q40169'})
MATCH (to:Entity {qid: 'Q1986139'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q40169 --REPLACED_BY--> Q1986139
MATCH (from:Entity {qid: 'Q40169'})
MATCH (to:Entity {qid: 'Q1986139'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q11939617 --LOCATED_IN_COUNTRY--> Q12544
MATCH (from:Entity {qid: 'Q11939617'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q11939617 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q11939617'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1669578 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q1669578'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1669578 --SHARES_BORDER_WITH--> Q221353
MATCH (from:Entity {qid: 'Q1669578'})
MATCH (to:Entity {qid: 'Q221353'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1669578 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q1669578'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q163323 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q163323'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q83922 --HAS_OFFICIAL_RELIGION--> Q5043
MATCH (from:Entity {qid: 'Q83922'})
MATCH (to:Entity {qid: 'Q5043'})
MERGE (from)-[r:HAS_OFFICIAL_RELIGION]->(to)
ON CREATE SET
  r.wikidata_pid = 'P140',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8607609 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q8607609'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q178897 --HAS_CAPITAL--> Q16869
MATCH (from:Entity {qid: 'Q178897'})
MATCH (to:Entity {qid: 'Q16869'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q178897 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q178897'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q178897 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q178897'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q178897 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q178897'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q178897 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q178897'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3718695 --LOCATED_IN--> Q2277
MATCH (from:Entity {qid: 'Q3718695'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3718695 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q3718695'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3974187 --INSTANCE_OF--> Q17524420
MATCH (from:Entity {qid: 'Q3974187'})
MATCH (to:Entity {qid: 'Q17524420'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3974187 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q3974187'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3974187 --LOCATED_IN--> Q46
MATCH (from:Entity {qid: 'Q3974187'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3974187 --LOCATED_IN--> Q15
MATCH (from:Entity {qid: 'Q3974187'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3974187 --LOCATED_IN--> Q48
MATCH (from:Entity {qid: 'Q3974187'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16186 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16186'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q238399 --INSTANCE_OF--> Q1307214
MATCH (from:Entity {qid: 'Q238399'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q238399 --INSTANCE_OF--> Q183039
MATCH (from:Entity {qid: 'Q238399'})
MATCH (to:Entity {qid: 'Q183039'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q238399 --INSTANCE_OF--> Q20076236
MATCH (from:Entity {qid: 'Q238399'})
MATCH (to:Entity {qid: 'Q20076236'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q238399 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q238399'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q238399 --FOLLOWS--> Q206414
MATCH (from:Entity {qid: 'Q238399'})
MATCH (to:Entity {qid: 'Q206414'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q238399 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q238399'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q787204 --PART_OF--> Q2277
MATCH (from:Entity {qid: 'Q787204'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q787204 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q787204'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q787204 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q787204'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q787204 --FOLLOWS--> Q2815472
MATCH (from:Entity {qid: 'Q787204'})
MATCH (to:Entity {qid: 'Q2815472'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q2566630 --FOLLOWED_BY--> Q201038
MATCH (from:Entity {qid: 'Q2566630'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q830852 --PART_OF--> Q41493
MATCH (from:Entity {qid: 'Q830852'})
MATCH (to:Entity {qid: 'Q41493'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q830852 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q830852'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1048669 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q1048669'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1048669 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q1048669'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3921629 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q3921629'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3921629 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q3921629'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3921629 --PART_OF--> Q201038
MATCH (from:Entity {qid: 'Q3921629'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3921629 --FOLLOWED_BY--> Q119137625
MATCH (from:Entity {qid: 'Q3921629'})
MATCH (to:Entity {qid: 'Q119137625'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3921629 --SUBCLASS_OF--> Q201038
MATCH (from:Entity {qid: 'Q3921629'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q584683 --SUBCLASS_OF--> Q7269
MATCH (from:Entity {qid: 'Q584683'})
MATCH (to:Entity {qid: 'Q7269'})
MERGE (from)-[r:SUBCLASS_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P279',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q584683 --INSTANCE_OF--> Q1307214
MATCH (from:Entity {qid: 'Q584683'})
MATCH (to:Entity {qid: 'Q1307214'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q55375123 --LOCATED_IN_COUNTRY--> Q201038
MATCH (from:Entity {qid: 'Q55375123'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q5171759 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q5171759'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q5171759 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q5171759'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q5171759 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q5171759'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q5171759 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q5171759'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q5171759 --REPLACED_BY--> Q201038
MATCH (from:Entity {qid: 'Q5171759'})
MATCH (to:Entity {qid: 'Q201038'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q48740750 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q48740750'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q10142763 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q10142763'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q23936560 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q23936560'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q23936560 --LOCATED_IN_COUNTRY--> Q172579
MATCH (from:Entity {qid: 'Q23936560'})
MATCH (to:Entity {qid: 'Q172579'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q33923 --INSTANCE_OF--> Q5
MATCH (from:Entity {qid: 'Q33923'})
MATCH (to:Entity {qid: 'Q5'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q9200 --HAS_OFFICIAL_RELIGION--> Q5043
MATCH (from:Entity {qid: 'Q9200'})
MATCH (to:Entity {qid: 'Q5043'})
MERGE (from)-[r:HAS_OFFICIAL_RELIGION]->(to)
ON CREATE SET
  r.wikidata_pid = 'P140',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q9200 --INSTANCE_OF--> Q5
MATCH (from:Entity {qid: 'Q9200'})
MATCH (to:Entity {qid: 'Q5'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q18288160 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q18288160'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q18288160 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q18288160'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q18288160 --REPLACES--> Q15119
MATCH (from:Entity {qid: 'Q18288160'})
MATCH (to:Entity {qid: 'Q15119'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --ON_CONTINENT--> Q15
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q15'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --REPLACES--> Q172579
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q172579'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --FOLLOWS--> Q172579
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q172579'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --PART_OF--> Q46
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --SHARES_BORDER_WITH--> Q237
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q237'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --CONTAINS--> Q1282
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q1282'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --INSTANCE_OF--> Q6256
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q6256'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --INSTANCE_OF--> Q3624078
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q3624078'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q38'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1282 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q1282'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1282 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q1282'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1282 --CONTAINS--> Q15119
MATCH (from:Entity {qid: 'Q1282'})
MATCH (to:Entity {qid: 'Q15119'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1282 --CONTAINS--> Q18288160
MATCH (from:Entity {qid: 'Q1282'})
MATCH (to:Entity {qid: 'Q18288160'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --INSTANCE_OF--> Q3624078
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q3624078'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --FOLLOWED_BY--> Q172579
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q172579'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --LOCATED_IN_COUNTRY--> Q170174
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --REPLACED_BY--> Q237
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q237'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --REPLACED_BY--> Q1072140
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q1072140'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q170174 --REPLACES--> Q1072140
MATCH (from:Entity {qid: 'Q170174'})
MATCH (to:Entity {qid: 'Q1072140'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3528124 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q3528124'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q172579 --FOLLOWS--> Q170174
MATCH (from:Entity {qid: 'Q172579'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:FOLLOWS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P155',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q172579 --FOLLOWED_BY--> Q38
MATCH (from:Entity {qid: 'Q172579'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:FOLLOWED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P156',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q172579 --INSTANCE_OF--> Q3624078
MATCH (from:Entity {qid: 'Q172579'})
MATCH (to:Entity {qid: 'Q3624078'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q172579 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q172579'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q172579 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q172579'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q172579 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q172579'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q172579 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q172579'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q172579 --REPLACED_BY--> Q38
MATCH (from:Entity {qid: 'Q172579'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3940419 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q3940419'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1072140 --REPLACES--> Q170174
MATCH (from:Entity {qid: 'Q1072140'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1072140 --REPLACED_BY--> Q170174
MATCH (from:Entity {qid: 'Q1072140'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1072140 --LOCATED_IN_COUNTRY--> Q1072140
MATCH (from:Entity {qid: 'Q1072140'})
MATCH (to:Entity {qid: 'Q1072140'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1072140 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q1072140'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1072140 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q1072140'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1072140 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q1072140'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q134317926 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q134317926'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q134317926 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q134317926'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q191115
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q191115'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q241693
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q241693'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q241733
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q241733'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q241911
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q241911'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242105
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242105'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242120
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242120'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242513
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242513'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242558
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242558'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q19326
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q19326'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242637
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242637'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242645
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242645'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q190963
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q190963'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242661
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242661'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242703
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242703'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242710
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242710'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242926
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242926'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242965
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242965'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q242998
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q242998'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q243133
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q243133'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q243188
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q243188'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q220
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q243311
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q243311'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --CONTAINS--> Q243497
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q243497'})
MERGE (from)-[r:CONTAINS]->(to)
ON CREATE SET
  r.wikidata_pid = 'P150',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --REPLACED_BY--> Q18288160
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q18288160'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q15119 --PART_OF--> Q1282
MATCH (from:Entity {qid: 'Q15119'})
MATCH (to:Entity {qid: 'Q1282'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --INSTANCE_OF--> Q48349
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q48349'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --HAS_OFFICIAL_RELIGION--> Q5043
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q5043'})
MERGE (from)-[r:HAS_OFFICIAL_RELIGION]->(to)
ON CREATE SET
  r.wikidata_pid = 'P140',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --HAS_CAPITAL--> Q13364
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q13364'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --HAS_CURRENCY--> Q952064
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q952064'})
MERGE (from)-[r:HAS_CURRENCY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P38',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --REPLACED_BY--> Q12544
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:REPLACED_BY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1366',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --REPLACES--> Q2277
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --SHARES_BORDER_WITH--> Q12544
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q12544'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q42834 --PART_OF--> Q2277
MATCH (from:Entity {qid: 'Q42834'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:PART_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P361',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3677829 --LOCATED_IN_COUNTRY--> Q172579
MATCH (from:Entity {qid: 'Q3677829'})
MATCH (to:Entity {qid: 'Q172579'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3677829 --HAS_CAPITAL--> Q220
MATCH (from:Entity {qid: 'Q3677829'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1200427 --INSTANCE_OF--> Q11514315
MATCH (from:Entity {qid: 'Q1200427'})
MATCH (to:Entity {qid: 'Q11514315'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1200427 --INSTANCE_OF--> Q1292119
MATCH (from:Entity {qid: 'Q1200427'})
MATCH (to:Entity {qid: 'Q1292119'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1200427 --LOCATED_IN_COUNTRY--> Q1747689
MATCH (from:Entity {qid: 'Q1200427'})
MATCH (to:Entity {qid: 'Q1747689'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13712 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q13712'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13712 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q13712'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q38882 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q38882'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q583038 --HAS_OFFICIAL_RELIGION--> Q83922
MATCH (from:Entity {qid: 'Q583038'})
MATCH (to:Entity {qid: 'Q83922'})
MERGE (from)-[r:HAS_OFFICIAL_RELIGION]->(to)
ON CREATE SET
  r.wikidata_pid = 'P140',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q583038 --HAS_CAPITAL--> Q13364
MATCH (from:Entity {qid: 'Q583038'})
MATCH (to:Entity {qid: 'Q13364'})
MERGE (from)-[r:HAS_CAPITAL]->(to)
ON CREATE SET
  r.wikidata_pid = 'P36',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q583038 --INSTANCE_OF--> Q3024240
MATCH (from:Entity {qid: 'Q583038'})
MATCH (to:Entity {qid: 'Q3024240'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q583038 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q583038'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q583038 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q583038'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q237 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q237'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q237 --SHARES_BORDER_WITH--> Q38
MATCH (from:Entity {qid: 'Q237'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q237 --INSTANCE_OF--> Q3624078
MATCH (from:Entity {qid: 'Q237'})
MATCH (to:Entity {qid: 'Q3624078'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q237 --INSTANCE_OF--> Q6256
MATCH (from:Entity {qid: 'Q237'})
MATCH (to:Entity {qid: 'Q6256'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q237 --REPLACES--> Q170174
MATCH (from:Entity {qid: 'Q237'})
MATCH (to:Entity {qid: 'Q170174'})
MERGE (from)-[r:REPLACES]->(to)
ON CREATE SET
  r.wikidata_pid = 'P1365',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q237 --LOCATED_IN_COUNTRY--> Q237
MATCH (from:Entity {qid: 'Q237'})
MATCH (to:Entity {qid: 'Q237'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q237 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q237'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q237 --HAS_OFFICIAL_LANGUAGE--> Q397
MATCH (from:Entity {qid: 'Q237'})
MATCH (to:Entity {qid: 'Q397'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q90 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q90'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q31487 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q31487'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q484799 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q484799'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1490 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q1490'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8717 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q8717'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q13437 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q13437'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8684 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q8684'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q3689056 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q3689056'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q459 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q459'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q956 --ON_CONTINENT--> Q48
MATCH (from:Entity {qid: 'Q956'})
MATCH (to:Entity {qid: 'Q48'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8682052 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q8682052'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q7977790 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q7977790'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q463130 --INSTANCE_OF--> Q5
MATCH (from:Entity {qid: 'Q463130'})
MATCH (to:Entity {qid: 'Q5'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q535345 --INSTANCE_OF--> Q5
MATCH (from:Entity {qid: 'Q535345'})
MATCH (to:Entity {qid: 'Q5'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q319547 --INSTANCE_OF--> Q5
MATCH (from:Entity {qid: 'Q319547'})
MATCH (to:Entity {qid: 'Q5'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1394623 --INSTANCE_OF--> Q5
MATCH (from:Entity {qid: 'Q1394623'})
MATCH (to:Entity {qid: 'Q5'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q948169 --INSTANCE_OF--> Q5
MATCH (from:Entity {qid: 'Q948169'})
MATCH (to:Entity {qid: 'Q5'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6469667 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q6469667'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q642958 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q642958'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q642958 --LOCATED_IN--> Q220
MATCH (from:Entity {qid: 'Q642958'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q737333 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q737333'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q737333 --ON_CONTINENT--> Q46
MATCH (from:Entity {qid: 'Q737333'})
MATCH (to:Entity {qid: 'Q46'})
MERGE (from)-[r:ON_CONTINENT]->(to)
ON CREATE SET
  r.wikidata_pid = 'P30',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1189119 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q1189119'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q1189119 --LOCATED_IN--> Q220
MATCH (from:Entity {qid: 'Q1189119'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:LOCATED_IN]->(to)
ON CREATE SET
  r.wikidata_pid = 'P276',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241693 --SHARES_BORDER_WITH--> Q241911
MATCH (from:Entity {qid: 'Q241693'})
MATCH (to:Entity {qid: 'Q241911'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241693 --SHARES_BORDER_WITH--> Q19326
MATCH (from:Entity {qid: 'Q241693'})
MATCH (to:Entity {qid: 'Q19326'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241693 --SHARES_BORDER_WITH--> Q243497
MATCH (from:Entity {qid: 'Q241693'})
MATCH (to:Entity {qid: 'Q243497'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241693 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q241693'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241693 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q241693'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241693 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q241693'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241733 --SHARES_BORDER_WITH--> Q191115
MATCH (from:Entity {qid: 'Q241733'})
MATCH (to:Entity {qid: 'Q191115'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241733 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q241733'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241733 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q241733'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242105 --SHARES_BORDER_WITH--> Q191115
MATCH (from:Entity {qid: 'Q242105'})
MATCH (to:Entity {qid: 'Q191115'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242105 --SHARES_BORDER_WITH--> Q242703
MATCH (from:Entity {qid: 'Q242105'})
MATCH (to:Entity {qid: 'Q242703'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242105 --SHARES_BORDER_WITH--> Q242926
MATCH (from:Entity {qid: 'Q242105'})
MATCH (to:Entity {qid: 'Q242926'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242105 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242105'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242105 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242105'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242105 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q242105'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242513 --SHARES_BORDER_WITH--> Q242703
MATCH (from:Entity {qid: 'Q242513'})
MATCH (to:Entity {qid: 'Q242703'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242513 --SHARES_BORDER_WITH--> Q242926
MATCH (from:Entity {qid: 'Q242513'})
MATCH (to:Entity {qid: 'Q242926'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242513 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242513'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242513 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242513'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242558 --SHARES_BORDER_WITH--> Q242965
MATCH (from:Entity {qid: 'Q242558'})
MATCH (to:Entity {qid: 'Q242965'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242558 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242558'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242558 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242558'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q19326 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q19326'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q19326 --SHARES_BORDER_WITH--> Q241693
MATCH (from:Entity {qid: 'Q19326'})
MATCH (to:Entity {qid: 'Q241693'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q19326 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q19326'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242637 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242637'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242637 --SHARES_BORDER_WITH--> Q242710
MATCH (from:Entity {qid: 'Q242637'})
MATCH (to:Entity {qid: 'Q242710'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242637 --SHARES_BORDER_WITH--> Q242998
MATCH (from:Entity {qid: 'Q242637'})
MATCH (to:Entity {qid: 'Q242998'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242637 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242637'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242645 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242645'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242645 --SHARES_BORDER_WITH--> Q241911
MATCH (from:Entity {qid: 'Q242645'})
MATCH (to:Entity {qid: 'Q241911'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242645 --SHARES_BORDER_WITH--> Q243311
MATCH (from:Entity {qid: 'Q242645'})
MATCH (to:Entity {qid: 'Q243311'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242645 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242645'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242703 --SHARES_BORDER_WITH--> Q242513
MATCH (from:Entity {qid: 'Q242703'})
MATCH (to:Entity {qid: 'Q242513'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242703 --SHARES_BORDER_WITH--> Q190963
MATCH (from:Entity {qid: 'Q242703'})
MATCH (to:Entity {qid: 'Q190963'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242703 --SHARES_BORDER_WITH--> Q242965
MATCH (from:Entity {qid: 'Q242703'})
MATCH (to:Entity {qid: 'Q242965'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242703 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242703'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242703 --SHARES_BORDER_WITH--> Q242105
MATCH (from:Entity {qid: 'Q242703'})
MATCH (to:Entity {qid: 'Q242105'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242703 --SHARES_BORDER_WITH--> Q242926
MATCH (from:Entity {qid: 'Q242703'})
MATCH (to:Entity {qid: 'Q242926'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242703 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242703'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242965 --SHARES_BORDER_WITH--> Q190963
MATCH (from:Entity {qid: 'Q242965'})
MATCH (to:Entity {qid: 'Q190963'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242965 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242965'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242965 --SHARES_BORDER_WITH--> Q242703
MATCH (from:Entity {qid: 'Q242965'})
MATCH (to:Entity {qid: 'Q242703'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242965 --SHARES_BORDER_WITH--> Q242558
MATCH (from:Entity {qid: 'Q242965'})
MATCH (to:Entity {qid: 'Q242558'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242965 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242965'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242998 --SHARES_BORDER_WITH--> Q242637
MATCH (from:Entity {qid: 'Q242998'})
MATCH (to:Entity {qid: 'Q242637'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242998 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242998'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242998 --SHARES_BORDER_WITH--> Q243188
MATCH (from:Entity {qid: 'Q242998'})
MATCH (to:Entity {qid: 'Q243188'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242998 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242998'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243311 --SHARES_BORDER_WITH--> Q241911
MATCH (from:Entity {qid: 'Q243311'})
MATCH (to:Entity {qid: 'Q241911'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243311 --SHARES_BORDER_WITH--> Q242645
MATCH (from:Entity {qid: 'Q243311'})
MATCH (to:Entity {qid: 'Q242645'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243311 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q243311'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243311 --SHARES_BORDER_WITH--> Q243188
MATCH (from:Entity {qid: 'Q243311'})
MATCH (to:Entity {qid: 'Q243188'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243311 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q243311'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243497 --SHARES_BORDER_WITH--> Q241911
MATCH (from:Entity {qid: 'Q243497'})
MATCH (to:Entity {qid: 'Q241911'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243497 --SHARES_BORDER_WITH--> Q241693
MATCH (from:Entity {qid: 'Q243497'})
MATCH (to:Entity {qid: 'Q241693'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243497 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q243497'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243497 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q243497'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q191115 --SHARES_BORDER_WITH--> Q241733
MATCH (from:Entity {qid: 'Q191115'})
MATCH (to:Entity {qid: 'Q241733'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q191115 --SHARES_BORDER_WITH--> Q242105
MATCH (from:Entity {qid: 'Q191115'})
MATCH (to:Entity {qid: 'Q242105'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q191115 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q191115'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q191115 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q191115'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q191115 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q191115'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241911 --SHARES_BORDER_WITH--> Q241693
MATCH (from:Entity {qid: 'Q241911'})
MATCH (to:Entity {qid: 'Q241693'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241911 --SHARES_BORDER_WITH--> Q242645
MATCH (from:Entity {qid: 'Q241911'})
MATCH (to:Entity {qid: 'Q242645'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241911 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q241911'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241911 --SHARES_BORDER_WITH--> Q243311
MATCH (from:Entity {qid: 'Q241911'})
MATCH (to:Entity {qid: 'Q243311'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241911 --SHARES_BORDER_WITH--> Q243497
MATCH (from:Entity {qid: 'Q241911'})
MATCH (to:Entity {qid: 'Q243497'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q241911 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q241911'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242120 --SHARES_BORDER_WITH--> Q243133
MATCH (from:Entity {qid: 'Q242120'})
MATCH (to:Entity {qid: 'Q243133'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242120 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242120'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242120 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242120'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q190963 --SHARES_BORDER_WITH--> Q242965
MATCH (from:Entity {qid: 'Q190963'})
MATCH (to:Entity {qid: 'Q242965'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q190963 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q190963'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q190963 --SHARES_BORDER_WITH--> Q242703
MATCH (from:Entity {qid: 'Q190963'})
MATCH (to:Entity {qid: 'Q242703'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q190963 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q190963'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242661 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242661'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242661 --SHARES_BORDER_WITH--> Q243133
MATCH (from:Entity {qid: 'Q242661'})
MATCH (to:Entity {qid: 'Q243133'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242661 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242661'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242926 --SHARES_BORDER_WITH--> Q242105
MATCH (from:Entity {qid: 'Q242926'})
MATCH (to:Entity {qid: 'Q242105'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242926 --SHARES_BORDER_WITH--> Q242703
MATCH (from:Entity {qid: 'Q242926'})
MATCH (to:Entity {qid: 'Q242703'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242926 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242926'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242926 --SHARES_BORDER_WITH--> Q242513
MATCH (from:Entity {qid: 'Q242926'})
MATCH (to:Entity {qid: 'Q242513'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242926 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242926'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243133 --SHARES_BORDER_WITH--> Q242120
MATCH (from:Entity {qid: 'Q243133'})
MATCH (to:Entity {qid: 'Q242120'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243133 --SHARES_BORDER_WITH--> Q242661
MATCH (from:Entity {qid: 'Q243133'})
MATCH (to:Entity {qid: 'Q242661'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243133 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q243133'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243133 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q243133'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243133 --LOCATED_IN_COUNTRY--> Q172579
MATCH (from:Entity {qid: 'Q243133'})
MATCH (to:Entity {qid: 'Q172579'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243133 --LOCATED_IN_COUNTRY--> Q2277
MATCH (from:Entity {qid: 'Q243133'})
MATCH (to:Entity {qid: 'Q2277'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243133 --LOCATED_IN_COUNTRY--> Q17167
MATCH (from:Entity {qid: 'Q243133'})
MATCH (to:Entity {qid: 'Q17167'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243188 --SHARES_BORDER_WITH--> Q242998
MATCH (from:Entity {qid: 'Q243188'})
MATCH (to:Entity {qid: 'Q242998'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243188 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q243188'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243188 --SHARES_BORDER_WITH--> Q243311
MATCH (from:Entity {qid: 'Q243188'})
MATCH (to:Entity {qid: 'Q243311'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q243188 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q243188'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242710 --SHARES_BORDER_WITH--> Q220
MATCH (from:Entity {qid: 'Q242710'})
MATCH (to:Entity {qid: 'Q220'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242710 --SHARES_BORDER_WITH--> Q242637
MATCH (from:Entity {qid: 'Q242710'})
MATCH (to:Entity {qid: 'Q242637'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242710 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q242710'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q242710 --HAS_OFFICIAL_LANGUAGE--> Q652
MATCH (from:Entity {qid: 'Q242710'})
MATCH (to:Entity {qid: 'Q652'})
MERGE (from)-[r:HAS_OFFICIAL_LANGUAGE]->(to)
ON CREATE SET
  r.wikidata_pid = 'P37',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q8070169 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q8070169'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16494134 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16494134'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16494134 --SHARES_BORDER_WITH--> Q16003470
MATCH (from:Entity {qid: 'Q16494134'})
MATCH (to:Entity {qid: 'Q16003470'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16494134 --SHARES_BORDER_WITH--> Q16481953
MATCH (from:Entity {qid: 'Q16494134'})
MATCH (to:Entity {qid: 'Q16481953'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16003470 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16003470'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16003470 --SHARES_BORDER_WITH--> Q16494134
MATCH (from:Entity {qid: 'Q16003470'})
MATCH (to:Entity {qid: 'Q16494134'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16481953 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16481953'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16481953 --SHARES_BORDER_WITH--> Q16494134
MATCH (from:Entity {qid: 'Q16481953'})
MATCH (to:Entity {qid: 'Q16494134'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16481953 --SHARES_BORDER_WITH--> Q16481966
MATCH (from:Entity {qid: 'Q16481953'})
MATCH (to:Entity {qid: 'Q16481966'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16481966 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16481966'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16481966 --SHARES_BORDER_WITH--> Q16481953
MATCH (from:Entity {qid: 'Q16481966'})
MATCH (to:Entity {qid: 'Q16481953'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16481966 --SHARES_BORDER_WITH--> Q16495467
MATCH (from:Entity {qid: 'Q16481966'})
MATCH (to:Entity {qid: 'Q16495467'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16495467 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16495467'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16495467 --SHARES_BORDER_WITH--> Q16481966
MATCH (from:Entity {qid: 'Q16495467'})
MATCH (to:Entity {qid: 'Q16481966'})
MERGE (from)-[r:SHARES_BORDER_WITH]->(to)
ON CREATE SET
  r.wikidata_pid = 'P47',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16481977 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16481977'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16481992 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16481992'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q16482002 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q16482002'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q6701024 --INSTANCE_OF--> Q4167836
MATCH (from:Entity {qid: 'Q6701024'})
MATCH (to:Entity {qid: 'Q4167836'})
MERGE (from)-[r:INSTANCE_OF]->(to)
ON CREATE SET
  r.wikidata_pid = 'P31',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q652 --LOCATED_IN_COUNTRY--> Q38
MATCH (from:Entity {qid: 'Q652'})
MATCH (to:Entity {qid: 'Q38'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';


// Q652 --LOCATED_IN_COUNTRY--> Q237
MATCH (from:Entity {qid: 'Q652'})
MATCH (to:Entity {qid: 'Q237'})
MERGE (from)-[r:LOCATED_IN_COUNTRY]->(to)
ON CREATE SET
  r.wikidata_pid = 'P17',
  r.created_at = datetime(),
  r.source = 'wikidata';
