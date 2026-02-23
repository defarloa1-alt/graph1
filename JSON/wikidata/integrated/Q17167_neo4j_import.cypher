// Neo4j Import for Q17167 - Roman Republic
// Generated: 2026-02-16T19:29:17.913451Z
// Claims: 166
// Unique assertions: 166

// Create seed entity
MERGE (seed:Entity:HistoricalPeriod {qid: 'Q17167'})
  SET seed.label = 'Roman Republic'
  SET seed.description = 'period of ancient Roman civilization (509 BC–27 BC)'

// Create claims (by AssertionCipher)
MERGE (c:Claim {cipher: '73f84285159dfe1b40fbbe5ea844617fb9591294487ce5b6fdead21c2979fe02'})
  SET c.content = 'Master of Arts in Ancient Greek and Roman Studies (Brandeis University) field of work Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P101'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.892805Z'
MERGE (subj:Entity {qid: 'Q106113087'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:FIELD_OF_STUDY]->(obj)
  SET r.confidence = 0.84
  SET r.source_id = 'wikidata:P101'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dc9861c2fb9e299838ca7eaf70447e9431dfc425c8fde52f507446d94d012dc5'})
  SET c.content = 'quadrans country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.892920Z'
MERGE (subj:Entity {qid: 'Q1249076'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.84
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5b4a725ba9bd65ac0565cc414feb218bc0dc0638a107f4390535961998e4c49f'})
  SET c.content = 'ancient drachma country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.892992Z'
MERGE (subj:Entity {qid: 'Q15078648'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.84
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dbd11b59581d71361bfd699d9f1cb9d24ed23257ac2ee3c4c9aaefddef6f7bda'})
  SET c.content = 'aureus country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893052Z'
MERGE (subj:Entity {qid: 'Q476078'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.84
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b5b65181f7021277f7bcb1603404d7687d6726e9a4086a41d82873b897927d68'})
  SET c.content = 'bes country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893104Z'
MERGE (subj:Entity {qid: 'Q829397'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.84
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'da2bbbded55f1e4200e19b979bc157647b1321a46b9c5a16392024d08c962b09'})
  SET c.content = 'Alyson Maureen Roy field of work Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P101'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893174Z'
MERGE (subj:Entity {qid: 'Q107468361'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:FIELD_OF_STUDY]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P101'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '530ee55bbd7cac7deea51f736e5f20ea9f8db00a41ba14e8f7694dae9accce3f'})
  SET c.content = 'Thibaud Lanfranchi field of work Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P101'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893231Z'
MERGE (subj:Entity {qid: 'Q113842043'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:FIELD_OF_STUDY]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P101'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f79edf420511b1239a3d2952c575096e4311695d05d125ef4740d797bdb1302e'})
  SET c.content = 'Marianne Coudry field of work Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P101'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893283Z'
MERGE (subj:Entity {qid: 'Q132795814'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:FIELD_OF_STUDY]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P101'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5e1482cc0e1925cf68ffe6be10b6acf998d3a98e71e2771613c376341f3d6867'})
  SET c.content = 'Michel Humm field of work Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P101'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893341Z'
MERGE (subj:Entity {qid: 'Q133737719'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:FIELD_OF_STUDY]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P101'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ecd29103ec70bf1bc91b4ef8090ca361fc5927f7f1a1fca6eb84507d64b62d7a'})
  SET c.content = 'Roman Kingdom replaced by Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P1366'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893391Z'
MERGE (subj:Entity {qid: 'Q201038'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:REPLACED_BY]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P1366'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bc2f33fe26191f3c6b983b6ca6e11337fd0227d9eae67d6129136ff1804fb9cf'})
  SET c.content = 'religion in ancient Rome country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893439Z'
MERGE (subj:Entity {qid: 'Q107013169'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c915339380db91e71117b61401cfdecb406f1bb703f2b40cf2d4c696b1a3005a'})
  SET c.content = 'triens country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893486Z'
MERGE (subj:Entity {qid: 'Q1249059'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fc97d6e53af25ab6b4b5b0699ddfcea385759253bb063ee7c889c0aca9e855b6'})
  SET c.content = 'Siege of Carthago Nova country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893537Z'
MERGE (subj:Entity {qid: 'Q137972719'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'daedcfc933cc734f45ad51d2232952839c31cd903301d0de64930210c15c0f8c'})
  SET c.content = 'nexum country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893584Z'
MERGE (subj:Entity {qid: 'Q1422780'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '486c8708f8b9d86aa988893d0e3389d7fdc4b35df3976658fc55f312c7dc0c48'})
  SET c.content = 'Constitutional reforms of Lucius Cornelius Sulla country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893636Z'
MERGE (subj:Entity {qid: 'Q1812526'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dd21fe28163389c72a09975d924011b709c7fefd821ae2c0927333f379c596ea'})
  SET c.content = 'Praetorian Guard country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893681Z'
MERGE (subj:Entity {qid: 'Q181733'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aa9ed99bd1e4f940143412d960048c459df4d45c0cc109898403eb2c59da1b88'})
  SET c.content = 'culture of the Roman Republic country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893731Z'
MERGE (subj:Entity {qid: 'Q1888820'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'af5a75da8f3fa3910f2b7276aa5cf833dbd10b359d54722e32e9659177f0af12'})
  SET c.content = 'Battle of Cartagena country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893777Z'
MERGE (subj:Entity {qid: 'Q20102510'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '57a4e056d7d9172708295535cdceaa5cc3b470a857d904b31850950c26cf2420'})
  SET c.content = 'Lex Mamilia de senatoribus country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893826Z'
MERGE (subj:Entity {qid: 'Q20108410'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5a1d1f5646bf7915f4fe789110f005b580239f1337251a3c253636045c5353f6'})
  SET c.content = 'Asia country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893870Z'
MERGE (subj:Entity {qid: 'Q210718'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '16d94b31f08e0786ed679383364ef6d5d2013ecfdd2c4a463b776acea7c211d2'})
  SET c.content = 'Battle of Nola country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893914Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '790bd7e9342e2263addfb608fd0fc973c869e6b778cc35a4b4968e43cbb40690'})
  SET c.content = 'litra country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.893958Z'
MERGE (subj:Entity {qid: 'Q3256634'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd2793ad76c2d7e626df47fd0078d49f320a96e05efebf93cde591601b229f374'})
  SET c.content = 'sextans country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894004Z'
MERGE (subj:Entity {qid: 'Q548953'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6817714d0034a2f3208a4a16ab2db4c18d9706aaceca8b8c7a2e0270fc4c1b74'})
  SET c.content = 'Battle of Apamea country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894054Z'
MERGE (subj:Entity {qid: 'Q9172749'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'faac0597b8a276e2ac26f572f5ae57677d865965065f50e6fdd8e24453f6c17b'})
  SET c.content = 'Gaius Marcius Censorinus place of birth Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894102Z'
MERGE (subj:Entity {qid: 'Q1223584'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0603c7ea1073983ce5d72535b719e48114aaba6b613126bd7f0ba929c28dcc7b'})
  SET c.content = 'Titus Quinctius Crispinus Sulpicianus place of birth Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894150Z'
MERGE (subj:Entity {qid: 'Q1227220'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0609ee7b2c1547d3e4525e2a027af0bd865fd2e116b3b0abbdd7fa333486f23c'})
  SET c.content = 'Ancient Rome has part(s) Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894199Z'
MERGE (subj:Entity {qid: 'Q1747689'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '833f574b1b68fe2881ea80034bb714c2b7eff87aebad23468af735d9914df4cc'})
  SET c.content = 'classical antiquity has part(s) Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894247Z'
MERGE (subj:Entity {qid: 'Q486761'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7c2ee0dd597810470e9f9137a0d4294f98e04aaed4ac4008fe1fd6e0761eff9b'})
  SET c.content = 'Battle of Ilipa participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894304Z'
MERGE (subj:Entity {qid: 'Q1055755'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b2eef9eab71e9e9cb941c31fa364a7ffa568a827ce29eea1a4b76be77abd287a'})
  SET c.content = 'Battle of Numistro participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894369Z'
MERGE (subj:Entity {qid: 'Q1184835'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '43e8b235e2fe9db7bd03123ff3b3c6a73162f4834f842c770ad423498e5f58bb'})
  SET c.content = 'Batlle of Emporion participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894426Z'
MERGE (subj:Entity {qid: 'Q11908712'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6a3058f636ee66f7cbc4b956f51ce881b54e6a85b308bfcc723f972d8e994863'})
  SET c.content = 'Battle of Rhode participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894477Z'
MERGE (subj:Entity {qid: 'Q11908765'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8f79b4d724225b3dadbf5a2fb830192713afced906cc88c2c32f873fe0b5b116'})
  SET c.content = 'Iberian revolt participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894527Z'
MERGE (subj:Entity {qid: 'Q11945466'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4a62e5321200e956b2bb8f90a6fa253eb4045d696d354b359841ed6c329371ff'})
  SET c.content = 'Lusitanian War participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894577Z'
MERGE (subj:Entity {qid: 'Q1202928'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a8d1f0583bd84e5b39c394e73ae4ee2b3e514ac68311b60768a83b8ffacc658b'})
  SET c.content = 'Latin War participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894624Z'
MERGE (subj:Entity {qid: 'Q12356285'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '45bd3b35e01f601f8e82c70d74138b7277108198d594c76511ca939b37d9a3ec'})
  SET c.content = 'Punic Wars participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894674Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '12bf7e0e88093387fd2a84d366639606dd0666bbe2130b9f64290b543662ad00'})
  SET c.content = 'Battle of the Axona participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894724Z'
MERGE (subj:Entity {qid: 'Q1260622'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '526bd576a8837f71932afb369a599ffc69bc8095167ca38ad8493cb530274d66'})
  SET c.content = 'Siege of Acerra participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894770Z'
MERGE (subj:Entity {qid: 'Q130534948'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fbf87f884b36b3753046e687e3de9ce64110ce6daf68586d9416c90e4abef467'})
  SET c.content = 'Hannibal\'s crossing of the Alps participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894823Z'
MERGE (subj:Entity {qid: 'Q1337302'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c2eb844bbb90c19460c3888f3da2a9380240fea49f7c53086a02e07455299d02'})
  SET c.content = 'Battle of Cissa participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894874Z'
MERGE (subj:Entity {qid: 'Q1500211'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a2b4f865ba18c71aa6c72cac288e9dc2aedd245daa1df854928f658034b33c02'})
  SET c.content = 'Numantine War participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894921Z'
MERGE (subj:Entity {qid: 'Q1503611'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7eba0303dcccc4ead05ac4c2807dcdf3e8adc94a86249bf631a4562db60a1a9b'})
  SET c.content = 'Battle of New Carthage participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.894969Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c6560e82943b668d52cf3a535e4d45a93f1205102ba0577321ac7b7520b6d186'})
  SET c.content = 'Battle of Orongis participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895020Z'
MERGE (subj:Entity {qid: 'Q18649467'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3e9fc36b787c88feb22c9d8ae802ab7296830e52e33edc780472ab580324d622'})
  SET c.content = 'Battle of Munda participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895069Z'
MERGE (subj:Entity {qid: 'Q18649505'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fd3257df2a62679592410f2f7ba751085fd3b5ab4867a1fc433d05ed091f557e'})
  SET c.content = 'Battle of the Nile participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895117Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2d65640131be29920dbb1aaa22f4e76191caf7e5d55791a9e7d4d9c67c2ab5e6'})
  SET c.content = 'Battle of Cartagena participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895164Z'
MERGE (subj:Entity {qid: 'Q20102510'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'df4b38a11618959b600c8c16377c40d45efa024796ebe0d6d61c2795347e9c2a'})
  SET c.content = 'Battle of Sapriportis participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895213Z'
MERGE (subj:Entity {qid: 'Q21234831'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b158cbeba5ae2b31f2fec27508060432d81ff0b984f594aee8a7ceb731439f7f'})
  SET c.content = 'Battle of Chalcedon participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895263Z'
MERGE (subj:Entity {qid: 'Q2331925'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e9c3b7492c92980f8f034b7a3b078bdb6cd1c341e041fa3b0185d5ef28d25162'})
  SET c.content = 'Battle of Nola participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895310Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '18ecf4eff108ede569f6619f4ba8839002d51a92d7a29d0871706a2b1b7209f0'})
  SET c.content = 'Ambiorix\'s revolt participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895361Z'
MERGE (subj:Entity {qid: 'Q2505574'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2e445f4c666951b07379672bafac0857adef67928e3807ec9b5e203fb474ade3'})
  SET c.content = 'Battle of Pydna participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895409Z'
MERGE (subj:Entity {qid: 'Q2617894'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7290cc5b4b74c3cd686203c3f108625bff365ca3f566b4ce58f1b0f05861004c'})
  SET c.content = 'Battle of Mount Algidus participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895457Z'
MERGE (subj:Entity {qid: 'Q2705449'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0409df08f4c49810fd181776b67d6ddb420ce22d341d328123ceb077f81a5aed'})
  SET c.content = 'Battle of the Lycus participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895510Z'
MERGE (subj:Entity {qid: 'Q2707112'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ffdd7582504cc9ce136f995d142ae15d10638035ed7548c682d76eea80d9b388'})
  SET c.content = 'Roman conquest of Hispania during the Second Punic War participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895566Z'
MERGE (subj:Entity {qid: 'Q28670084'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c30769da5d1cee1fede60656c02858dfa244392f57d87c49ecd93683a29a5168'})
  SET c.content = 'Octavian\'s military campaigns in Illyricum participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895621Z'
MERGE (subj:Entity {qid: 'Q2935356'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5adef9b817cabdfb69657e549ffd2bc43a73ca944f08f56262fc3a763539fd6f'})
  SET c.content = 'Siege of Numantia participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895667Z'
MERGE (subj:Entity {qid: 'Q815183'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5c68952d7e8a4971ec60d4fae21add178ae2ba31cae88bb89ea2f12b9e23aa0e'})
  SET c.content = 'Battle of Apamea participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895714Z'
MERGE (subj:Entity {qid: 'Q9172749'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '180724a25eb40cee5df088d300de314f72fe3e66ee27d0f8e10fa7327fbf4944'})
  SET c.content = 'stasis.hypotheses.org main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895767Z'
MERGE (subj:Entity {qid: 'Q122732170'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8ae64efa24f2602b90b1b52b1a31cdff598ad8562da0871a972dcdb2c1794f62'})
  SET c.content = 'Falling Sky: The Gallic Revolt Against Caesar main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895824Z'
MERGE (subj:Entity {qid: 'Q137219487'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8c056ffdb0f3bece38b4f7b29acd428d8c817afd562f7fd0a2ec9baed7bb32c1'})
  SET c.content = 'Imperium main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895870Z'
MERGE (subj:Entity {qid: 'Q1660324'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd295442e3ddd0ec7173eea23394656236e69217ab02b5e76c11719ecfa237c4a'})
  SET c.content = 'Dictator main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895918Z'
MERGE (subj:Entity {qid: 'Q21162234'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bd6ec1123538d2db5c51e94ed899adda5b814bd077e3cc14568e2ca39d659594'})
  SET c.content = 'half-stater country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.895966Z'
MERGE (subj:Entity {qid: 'Q106841885'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.74
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '017abb4c20896792675815c7dd1e24abb2dba1d9b6465fb8f2ca1bdcdaf6f7dd'})
  SET c.content = 'Roman Republic religion or worldview ancient Roman religion'
  SET c.source_id = 'wikidata:Q17167:P140'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896032Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q337547'})
MERGE (subj)-[r:CONVERTED_BY]->(obj)
  SET r.confidence = 0.73
  SET r.source_id = 'wikidata:P140'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '43aa41971b05ac81d3f5d179391cb55d6d517f52c1b440cfb1c38e4a286abc64'})
  SET c.content = 'didrachm country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896096Z'
MERGE (subj:Entity {qid: 'Q11320126'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '076237101e725af196d4862b34e8a7e0208c4d073faa300b397e3322342bce9e'})
  SET c.content = 'Battle of Petelia country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896143Z'
MERGE (subj:Entity {qid: 'Q11688220'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a48817d2470cb3285c7e4f0f46ab96b124f7c5495fe2639382d99672926b178a'})
  SET c.content = 'victoriatus country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896187Z'
MERGE (subj:Entity {qid: 'Q1228632'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4dcec2b464080c715fd33e20ec1d4249bb6ae33f3352d3cf37fe563346fbc818'})
  SET c.content = 'dodrans country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896236Z'
MERGE (subj:Entity {qid: 'Q1234467'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ee1f3316261ece3d877a886262c099a3f3e430ab5973cdd6ba3a7a78d98eea61'})
  SET c.content = 'Q124798662 country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896283Z'
MERGE (subj:Entity {qid: 'Q124798662'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '70569c69cb924ca88a7fed80ff5b22c416f21774b532a3c15b14f3fe7a7f1f57'})
  SET c.content = 'semis country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896326Z'
MERGE (subj:Entity {qid: 'Q1249093'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0d02ed45c85248326cbc9851b44363c623250223be6a4519d9ae6447fbb4c2f5'})
  SET c.content = 'denarius serratus country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896384Z'
MERGE (subj:Entity {qid: 'Q129571751'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2ce8ca3776f44a8cf09d88b55ab5f035459863af9e62cf9d6b4a17e2023ef58d'})
  SET c.content = 'double-litra country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896433Z'
MERGE (subj:Entity {qid: 'Q129571920'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2bcbb931b00d59aef850ab051329f27fa2c249445f5a142646a634b01e003110'})
  SET c.content = 'double victoriatus country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896481Z'
MERGE (subj:Entity {qid: 'Q129571942'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4a14d1c634369cbb9540e10319943d42f541f266cc65d4302e372b81d0e44ca1'})
  SET c.content = 'half victoriatus country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896525Z'
MERGE (subj:Entity {qid: 'Q129571969'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'de6fe6eb5dc84df49c9a86414a161f286483f3bc793eec7ff08a0f1b6ec10696'})
  SET c.content = 'half-litra country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896571Z'
MERGE (subj:Entity {qid: 'Q129571980'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bba14582648560a2ad2ab72700979772c0b14c023f930987bf7364dbfa889c00'})
  SET c.content = 'Battle of Geronium country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896619Z'
MERGE (subj:Entity {qid: 'Q1974201'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4ab556bb44b24fd595819191b3974993211821d9f38f436ab40552f7ebf004ba'})
  SET c.content = 'Suci country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896664Z'
MERGE (subj:Entity {qid: 'Q2022780'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5e2fd9ac0d78cd6eb6131d88f51373ca9404640055624eb604ba2782052519d3'})
  SET c.content = 'half aureus country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896711Z'
MERGE (subj:Entity {qid: 'Q2123159'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0c029c92db5919efdb0f6be8e572d8e1e20750c1faabe5dccdf0c8b5e28797d0'})
  SET c.content = 'quincussis country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896771Z'
MERGE (subj:Entity {qid: 'Q2123190'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '99fbe1d3137494deda9315f76eea5a9d25b1b69b0388a483c7df7abcc6f01736'})
  SET c.content = '122 BC eruption of Mount Etna country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896828Z'
MERGE (subj:Entity {qid: 'Q21328960'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9dea8443718faa54d6186f96122b09e29c19653ae30c581f52f651669f1704d6'})
  SET c.content = 'tressis country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896874Z'
MERGE (subj:Entity {qid: 'Q277376'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd861f26343a092a580ffce1d1891829f2e96abe28b506c3d51e0fa925ad8d09c'})
  SET c.content = 'Semuncia country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896918Z'
MERGE (subj:Entity {qid: 'Q663270'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0c4d028d88ff7b5eaa960f99fdd6f4a07905e17f8e872b6a7c3cf53d15e40236'})
  SET c.content = 'quartuncia country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.896967Z'
MERGE (subj:Entity {qid: 'Q671292'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd0f9ced08eb8a0ad3ec326ce0f3a3347827be96c98fe4fe77531551f175aad50'})
  SET c.content = 'Q134878258 place of birth Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.897016Z'
MERGE (subj:Entity {qid: 'Q134878258'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8c4cb21b34ebc9dc6d3e9a56394c8cd719020e187e6a7ccaac54716b1e5ea173'})
  SET c.content = 'Battle of Andagoste participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.897067Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '88bf62d0304a307040439e4a51d4d701d5d3b05854664b19819fb33d531d4a5f'})
  SET c.content = 'Battle of Halys participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.897299Z'
MERGE (subj:Entity {qid: 'Q17277303'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9a7bf5340ad3b3d39434211d4bbf9fd69ad1242b4ccf51b7969bf2bad06ebcb7'})
  SET c.content = 'Antony\'s Parthian War participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.897403Z'
MERGE (subj:Entity {qid: 'Q2334699'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e02ff5af608d8350c7d350793cbc468540210a304016cb126072b8542a6babc7'})
  SET c.content = 'Changes that accompany the political transition in the ancient Greek polis: from non-citizens to citizens main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.897961Z'
MERGE (subj:Entity {qid: 'Q120241324'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cb7edfbbe2b83b50cc7f23b17f7dfc5984ffa4c5ad9c0a7cbbed0aff04f25263'})
  SET c.content = 'Monarchische Herrschaft im Altertum main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898041Z'
MERGE (subj:Entity {qid: 'Q122746922'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4784c9dfee715b99f173394ec9b4d667eb1d1b4f88d006385b296fd7a855b0a2'})
  SET c.content = 'Carsten Hjort Lange: From Hannibal to Sulla: The Birth of Civil War in Republican Rome. Berlin: De Gruyter 2024 main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898121Z'
MERGE (subj:Entity {qid: 'Q122861593'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ee6e471a20b811a9874bc3a9191769d5c3d515400dd70d02dd696b6fc92a9639'})
  SET c.content = 'History program for Italian primary school main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898185Z'
MERGE (subj:Entity {qid: 'Q123116313'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aff70518163ea45f944fa1e8c176893f1bda539f0c4df412223d011ca04c1671'})
  SET c.content = 'History program for Italian junior high school main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898245Z'
MERGE (subj:Entity {qid: 'Q123157468'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b16e56db50c3611bd9801702b9007240c89af162c7f954344f64fce59587c953'})
  SET c.content = 'Battle near Osca country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898310Z'
MERGE (subj:Entity {qid: 'Q104834716'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '617d2aaf2a0059e0a7bf1efa0fecdef41bfa012d5b6e63d0f9eea3ff89aaebed'})
  SET c.content = 'Seleuceia in Cilicia country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898360Z'
MERGE (subj:Entity {qid: 'Q11948139'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd572b6d69d4df51c203b945ee4b629ad6ee054ec890db0293ff6ff4717be80fe'})
  SET c.content = 'Siege of Nola country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898414Z'
MERGE (subj:Entity {qid: 'Q137921341'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '02ea11ddd5dbdb0e300a18cb16d580b7f85a54b40a0f2dd23a5cafde72ba8f95'})
  SET c.content = 'Lex Iulia de civitate country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898464Z'
MERGE (subj:Entity {qid: 'Q15282014'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fbb3942615d58b80a6c8375ea864f2d065ad685d02d042fcd02f62d5ac224fe3'})
  SET c.content = 'First secessio plebis in 494 BC country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898520Z'
MERGE (subj:Entity {qid: 'Q15651483'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0c1bbc48cd2f65892369aee7e23b462ee3b3b26e58c34badb0ecbc7a53fb8b32'})
  SET c.content = 'Late Roman Republic country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898581Z'
MERGE (subj:Entity {qid: 'Q2815472'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f0c15c64f38cf3bee6e8d75853e2e9c9add1a2272bb53c338b0cee9662835c63'})
  SET c.content = 'Early Roman Republic country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898636Z'
MERGE (subj:Entity {qid: 'Q2839628'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ce7aa64efbd3a3a80d67edc83d5111d19f71c8a4217e7c280a502e637ac4103b'})
  SET c.content = 'Middle Roman Republic country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898684Z'
MERGE (subj:Entity {qid: 'Q6106068'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6621e66c6d95cbe14d11a8e5bad2edee059accc574c46aec84328dff3337dd71'})
  SET c.content = 'Late Roman Republic part of Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898735Z'
MERGE (subj:Entity {qid: 'Q2815472'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7c98e33aa7d88f5dc31be61c0a9caa874cbe211735a6536b37e77e1e9a8376ec'})
  SET c.content = 'Early Roman Republic part of Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898788Z'
MERGE (subj:Entity {qid: 'Q2839628'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c76a155305ed0d281dcdc9a153408fe6da02026ad59f51df4892b022144f3421'})
  SET c.content = 'Middle Roman Republic part of Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898837Z'
MERGE (subj:Entity {qid: 'Q6106068'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '43638ae596c1fce388f7419a05c1d1b7ec58a6347edfb81d39596e947e5df332'})
  SET c.content = 'Roman conquest of Gallaecia participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898895Z'
MERGE (subj:Entity {qid: 'Q107342906'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9030d9c49912d10d62b150a9cc07fa987a93c582718e473cbcd15d4657df3e8b'})
  SET c.content = 'Siege of Antioch participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898945Z'
MERGE (subj:Entity {qid: 'Q109377210'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '53bba9e7c1d2cfc21bffb11dd857bd9adb1357f312d3e039232dfc8354908553'})
  SET c.content = 'Siege of Bassania participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.898998Z'
MERGE (subj:Entity {qid: 'Q123310379'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bb07a166cd022c3262a3f1d88ea96ccb601ebee6586ef70c6d0d0e7ddf5b5352'})
  SET c.content = 'Battle of Placentia participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899046Z'
MERGE (subj:Entity {qid: 'Q124714225'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '538f939e27974f6f02991abb74d8cbef0a06c848da2dc83bbbdb22176a926796'})
  SET c.content = 'Conquest of Conistorgis participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899094Z'
MERGE (subj:Entity {qid: 'Q127606735'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3ac569a10bcddf02be628072e9581f93b2b3bd08a2a6ede9c73854b6d7ffd078'})
  SET c.content = 'The scene of the Apennine Peninsula in the Pyrrhic War participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899148Z'
MERGE (subj:Entity {qid: 'Q129059100'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e59259e01427ed5212762b695b9959f957525b179bd7cf2634b3080b1a1a4cc3'})
  SET c.content = 'Conquest of Oxthracae participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899195Z'
MERGE (subj:Entity {qid: 'Q130318424'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd1e47fe41d62f152e4eb7205606af2ce12237cd84ffa1d6ace7712e259a7ceac'})
  SET c.content = 'Siege of Ocile participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899246Z'
MERGE (subj:Entity {qid: 'Q130329121'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5c0e1360a60c23c648891a6b78f6117a4514a165a24f30dada6cdc3bbffb0fb7'})
  SET c.content = 'Siege of Pallantia participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899294Z'
MERGE (subj:Entity {qid: 'Q130329781'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7104cc645f9a3f00c7978ec4b9095f91954b974d4c76bf7f4fb28aee74f9f56a'})
  SET c.content = 'Siege of the Blastophoenicians participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899346Z'
MERGE (subj:Entity {qid: 'Q130329807'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ee0bc59a1a93ce81ca0891da81f23050a1df590a346b8a001c08fa073d3c787c'})
  SET c.content = 'Raid of Carpetania participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899394Z'
MERGE (subj:Entity {qid: 'Q130348963'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fccb99d193aafeb003b97559507da117b17082e5f7175283ebfc5bd049f4fbaa'})
  SET c.content = 'Battle of Delos participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899443Z'
MERGE (subj:Entity {qid: 'Q130857859'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e02ff208f0063d496af9ae6b67da8feebbd4763644d94041e2f8b0ab93952b51'})
  SET c.content = 'Battle of the Tagus participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899491Z'
MERGE (subj:Entity {qid: 'Q131686739'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '988a79425cb85dd549c3b1b086a79fbede41c5f19131ddb4c99aeba10e30f96a'})
  SET c.content = 'Siege of Aiginion participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899535Z'
MERGE (subj:Entity {qid: 'Q132452152'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c9f2f80ae167ec57a19cf34daad76fb7009c83ecf69d82b2dbaca157f230e4ad'})
  SET c.content = 'Battle of Uskana participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899595Z'
MERGE (subj:Entity {qid: 'Q133480177'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e63b68a1860d870f749df4cfe8af0bfe9b76a4e8068a5e8e51ccc901fbc46aef'})
  SET c.content = 'Roman invasion of Africa participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899648Z'
MERGE (subj:Entity {qid: 'Q134836736'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '562e355984e40aab577229a6a7c61e96dae0f99618cb971e11c2e67412965c55'})
  SET c.content = 'Demetrius\'s Winter offensive in Southern Illyria participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899702Z'
MERGE (subj:Entity {qid: 'Q136716728'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2f99675abfbc869b46d1f7fdd015f4492995a8676048fe250dcaaba088c87803'})
  SET c.content = 'Bellum Dardanicum participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.899752Z'
MERGE (subj:Entity {qid: 'Q137217360'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e303f40559a652ad62e877b47c9831ffc1c3d4f7fe695a00fd9ac2d17059cb36'})
  SET c.content = 'Roman–Dardanian wars participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.900742Z'
MERGE (subj:Entity {qid: 'Q137719648'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '13af61538d9adf870af6eb69f70e3e9ac9e7c168582e8025259c73d1ddb7bed1'})
  SET c.content = 'Siege of Nola participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.900836Z'
MERGE (subj:Entity {qid: 'Q137921341'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '151753b71034adc7000d37501e7b8ebeee2bbd72e5a4eec55d51bdf36f574167'})
  SET c.content = 'Pontic War participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.900897Z'
MERGE (subj:Entity {qid: 'Q18408280'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '67f95d2f6a25116ac080e085f091a6c0ab63c4c6c4b7a650598e3411b54d160e'})
  SET c.content = 'Battle of Campi Veteres participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.900950Z'
MERGE (subj:Entity {qid: 'Q18667552'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f9eaa0f938df0189f0230ae6b2f1597abb22560ff027fcc02b4383ce1451a18b'})
  SET c.content = 'Siege of Arpi participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901003Z'
MERGE (subj:Entity {qid: 'Q20008151'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '61fa3961e3debf80bac959fb920a1d8c4410b9ab19114d6db4b86592f198f2c2'})
  SET c.content = 'Parthian campaigns of Publius Ventidius participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901056Z'
MERGE (subj:Entity {qid: 'Q20008414'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7ed9112a7c8932df444a842989f90374bfdf6fa8a4e78ef02d5e47d40054c1b9'})
  SET c.content = 'Battle of Petilia participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901106Z'
MERGE (subj:Entity {qid: 'Q24045885'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1b1367b8b77dde6710e529bbcbaa9ca95c70237f70080b1a2ecc757d73fc5154'})
  SET c.content = 'Battle of Chaeronea participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901153Z'
MERGE (subj:Entity {qid: 'Q25414978'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd7921317920692ee743e6df30c6da1126ab6ed1673c3e72cafc71948892dce36'})
  SET c.content = 'Battle of the Douro participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901202Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7caa01d197dfd91a7b9489c6a2d64d7a4e24957ad68aa669ae1c5d64d5d6a013'})
  SET c.content = 'Battle of the Granicus participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901600Z'
MERGE (subj:Entity {qid: 'Q28665781'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '99cfebed175605bd3e541f646dceff7ab66008c6c2a323bcde03984401dafde0'})
  SET c.content = 'Hannibal\'s crossing of the Apennines participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901693Z'
MERGE (subj:Entity {qid: 'Q28668107'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '34972c713f299455e77a79619bc282f1cc8b6d07adb93720f02dbb8a7e5e4d19'})
  SET c.content = 'Battle of Zama participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901756Z'
MERGE (subj:Entity {qid: 'Q2890429'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '58f3c3a5b9589875e2fc772cdd4c1fccc47a0fed77604231dcae34aaf991a8ee'})
  SET c.content = 'Battle of the Point of Italy participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901812Z'
MERGE (subj:Entity {qid: 'Q2890613'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd25058ad2ba6f5a924a0dd3d56ff5334c83ba523a10c65c0d8a520c483882a76'})
  SET c.content = 'Cicero And The Fall Of The Roman Republic main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901868Z'
MERGE (subj:Entity {qid: 'Q110572348'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bca9671ef7d72d9c1d58c50bb6645998de72e2b0601d3ff52b2f44558fc869c3'})
  SET c.content = 'Extra: Dr. Emma Southon on murder in ancient Rome main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.901925Z'
MERGE (subj:Entity {qid: 'Q111666120'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'acbc1bff7152f55ccd10ce676757890f6c5636b969a64317c9ad53df5d5012d6'})
  SET c.content = 'Der Senat, der über Leichen ging main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902349Z'
MERGE (subj:Entity {qid: 'Q111666121'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9dd5841d7ede48e930734a76f2761d704cb08aeba1a4eb20e231e7a93c8ea790'})
  SET c.content = 'Civil War in Ancient Greece and Rome: Contexts of Disintegration and Reintegration, ed. Henning Börm, Marco Mattheis, Johannes Wienand. Stuttgart: Steiner 2016 main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902489Z'
MERGE (subj:Entity {qid: 'Q122746681'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2bbe3e9bc497275550b53636c301d790a0181653ad16dc91346a8af173f0ae2f'})
  SET c.content = 'Les històries romanes main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902557Z'
MERGE (subj:Entity {qid: 'Q123039428'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0a7253be6740df902090b35c3982e29c0563f5711b9df333e2f1cc2927e60b5f'})
  SET c.content = 'Livre de Tytus Livius de hystoire roumaine main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902618Z'
MERGE (subj:Entity {qid: 'Q123039445'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'eec668190443e3dccf2efd82cef4e259aff22fbb5ec58c45859401078ab55b41'})
  SET c.content = 'Imperatores victi main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902670Z'
MERGE (subj:Entity {qid: 'Q123245395'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '606f7ef9e106054a2f3fe19c4531785d8ae1c0d5e1f132eba5f306b0a28c39df'})
  SET c.content = 'Roman Republic replaces Roman Kingdom'
  SET c.source_id = 'wikidata:Q17167:P1365'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902734Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q201038'})
MERGE (subj)-[r:SUCCESSOR_OF]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P1365'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4e817df456d34da9000927dbc444bc300d2422e172a5345d26293147f3a0a0f9'})
  SET c.content = 'Roman Republic replaced by Principate'
  SET c.source_id = 'wikidata:Q17167:P1366'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902782Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q206414'})
MERGE (subj)-[r:REPLACED_BY]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P1366'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '25bb8d3cbb436b32680d5b207c654a108230637765037325ceea16f005d519be'})
  SET c.content = 'Roman Republic replaced by Roman Empire'
  SET c.source_id = 'wikidata:Q17167:P1366'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902827Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q2277'})
MERGE (subj)-[r:REPLACED_BY]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P1366'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f14d90b63aaeaad6408dd8d4add7ba1c4e139370affd2f76feb71de8804a05cb'})
  SET c.content = 'Roman Republic part of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902902Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b73e4035e8c67f12a1ca19184d965a019f7a991a544aa1c16277d7d2a857a4a1'})
  SET c.content = 'Roman Republic has part(s) Early Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.902956Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q2839628'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd16c92a433894779ca4b602faec1160128b4d1334e70845ce6e4d819470ab183'})
  SET c.content = 'Roman Republic has part(s) Late Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903003Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q2815472'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1988e50f77aa9e1ce103f8498bbbf78f5acf82fd0397c71f2ddd9d74e8d22dbe'})
  SET c.content = 'Roman Republic has part(s) Middle Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903048Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q6106068'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cf4ebc9c28c494e4fc14896e5009e241574b03c43a914a6859367ba2a1c94d7c'})
  SET c.content = 'Law of majestas applies to jurisdiction Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P1001'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903122Z'
MERGE (subj:Entity {qid: 'Q6503456'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:APPLIES_TO_JURISDICTION]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1001'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4982ed637734abb3bb39d674577a0d637823cca655bbcacb595a8bb07a7f934f'})
  SET c.content = 'Res Publica named after Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P138'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903172Z'
MERGE (subj:Entity {qid: 'Q130343589'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:NAMED_AFTER]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P138'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f0d1dc83fc51fc997b0cf3743290dd3c56be98bb4cd1fe869b4ca91e5593b768'})
  SET c.content = 'Q11905280 country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903219Z'
MERGE (subj:Entity {qid: 'Q11905280'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5b66253996b67936d43e08d5a8a05dd5c303007df75866fa5b2e000dd9f43c12'})
  SET c.content = 'Pompey\'s eastern settlement country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903267Z'
MERGE (subj:Entity {qid: 'Q122918768'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4e83da9fe81f77f06aa44e9747d5bc41cdbb10acb850e8d0394d6e24cdeb22f2'})
  SET c.content = 'March on Rome country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903314Z'
MERGE (subj:Entity {qid: 'Q125727661'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2ae1661d8075aa74a9d4302c2321ef6907da76c4454a83c90a70bdc314390218'})
  SET c.content = 'political violence in the late Roman Republic country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903364Z'
MERGE (subj:Entity {qid: 'Q12594116'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd6ad73d1facd523e6ab6ade919ac271e21232afa351692fac2886e8779383fc6'})
  SET c.content = '20-As country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903408Z'
MERGE (subj:Entity {qid: 'Q129571642'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '583f0d226fd4adcedc26b8d6083791ff5958c13a2f08317ec8359f8c742ebd67'})
  SET c.content = '40-As country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903451Z'
MERGE (subj:Entity {qid: 'Q129571668'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '667efa5149c09558c100902e2076853594abcb173666815b3b402c5c39675096'})
  SET c.content = '60-As country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903495Z'
MERGE (subj:Entity {qid: 'Q129571682'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c874b41fd805e19c5278eecf5d3d1afab2d342f465034f49e9220cdd9e5fbf21'})
  SET c.content = 'Law of majestas country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903542Z'
MERGE (subj:Entity {qid: 'Q6503456'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6e15e459ee3113a9213cf193e41b807667cfc2aeace5b7c2580e716cc0539a4c'})
  SET c.content = 'Siege of Mytistraton participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903593Z'
MERGE (subj:Entity {qid: 'Q16683525'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b6970c07403e8b466174dd2597d189347d0b0d84ea497624a588d53e06441513'})
  SET c.content = 'Ebro Treaty participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903642Z'
MERGE (subj:Entity {qid: 'Q188322'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:PARTICIPATED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd6b25cf2bfe4ede67d1bb78de7b6acdb729e8085ffb227026c7744a6a5b4525f'})
  SET c.content = 'Template:Country data Roman Republic main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903702Z'
MERGE (subj:Entity {qid: 'Q112998934'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b4eadc594c02340881e5f5a49ef4fb7d6f1a6e2c007e16fc8254f35fbba557ae'})
  SET c.content = 'Stefan Rebenich, Johannes Wienand: Monarchische Herrschaft im Altertum. Zugänge und Perspektiven, in: Monarchische Herrschaft im Altertum, ed. S. Rebenich in cooperation with J. Wienand, Berlin: De Gruyter 2017, 1-41 main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903782Z'
MERGE (subj:Entity {qid: 'Q122751016'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '04d685ffc666a9ff698709ddd0a5ce9defadf7be52c2b906cb4a7b7ba02090c4'})
  SET c.content = 'Internal War. Society: Social Order and Political Conflict in Antiquity main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903837Z'
MERGE (subj:Entity {qid: 'Q122764589'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '55571df034abbceb79b4fe23503e302f3ee180c1f825e8e40f0615dcb59b0425'})
  SET c.content = 'Johannes Wienand: Stasis. An Academic Blog on Ancient Civil War, in: Stasis – Avenues to Ancient Civil War, October 9, 2023, doi: 10.59350/377m7-vkt78 main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903920Z'
MERGE (subj:Entity {qid: 'Q122865066'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cf0087098fcd546ba004bb5691dc57223a4f8259300007c9e9d97646d040dfe8'})
  SET c.content = 'Carsten Hjort Lange: Civil War Seen Through the Lens of Ancient History, in: Stasis – Avenues to Ancient Civil War, October 10, 2023, doi: 10.59350/5b9hv-1xz57 main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.903995Z'
MERGE (subj:Entity {qid: 'Q123002123'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8b4fc11e16c216ae02aaa48d4732575fab31b5a9cb0163a4ce6d4d2e110b964a'})
  SET c.content = 'Romerrikets historie - republikkens vekst og fall main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.904067Z'
MERGE (subj:Entity {qid: 'Q127525629'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c0070c6164664933696465d617777e1291721b4a893985a2aab7339186dd17e9'})
  SET c.content = 'Geschichte Roms in seinem Übergange vor der republikanischen zur monarchischen Verfassung oder Pompeius, Caesar, Cicero und ihre Zeitgenossen main subject Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P921'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-02-16T19:29:17.904142Z'
MERGE (subj:Entity {qid: 'Q30557111'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:SUBJECT_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P921'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)
