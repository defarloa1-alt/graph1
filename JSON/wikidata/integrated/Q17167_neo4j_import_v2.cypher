// Neo4j Import for Q17167 - Roman Republic
// Generated: 2026-07-14T22:30:23.189135Z
// Claims: 1027
// Unique assertions: 1007

// Create seed entity
MERGE (seed:Entity:HistoricalPeriod {qid: 'Q17167'})
  SET seed.label = 'Roman Republic'
  SET seed.description = 'period of ancient Roman civilization (509 BC–27 BC)'

// Create claims (by AssertionCipher)
MERGE (c:Claim {cipher: '940740c59b5c12d51595902b2fe3c0300ea3b969a4e203cbb6e912c4eca22c77'})
  SET c.content = 'Hannibal fought in Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.073586Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.84
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '520a4ef7b41de8276eb26651fb6c38e0824eba039a60f140de29b2bebc3f1402'})
  SET c.content = 'Hannibal —[AWARDED_TO]→ illustrious son'
  SET c.source_id = 'wikidata:Q17167:P166'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.073947Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q56035316'})
MERGE (subj)-[r:AWARDED_TO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P166'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a9bd0f9baae732dd4c1c95aef418a402c390c9b1cca31ccd85d02a8f7f65b097'})
  SET c.content = 'Rome is birthplace of Julius Caesar'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074008Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q220'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3c151effb2c85d8b123ba022240fcbdf3d52bf13b1bfead722fb6c7a48e2f4a0'})
  SET c.content = 'Regio V Picenum is birthplace of Pompey'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074051Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q510990'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1894ce37d78788fe085aff0c8d95647d58d9e705f283b0cad06ae201c961323f'})
  SET c.content = 'Sinop is birthplace of Mithridates VI of Pontus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074091Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q599416'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '24e5550a3bc240ccbb9da38103cdef11271d64c244e92267e4f0f888f3f71de3'})
  SET c.content = 'Carthage is birthplace of Mago'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074128Z'
MERGE (subj:Entity {qid: 'Q335604'})
MERGE (obj:Entity {qid: 'Q6343'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '83feab6f4a3cf17ac2e3e99e122c463c980ad18c23d50723567886e315b7b913'})
  SET c.content = 'Carthage is birthplace of Hannibal'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074164Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q6343'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5fd549379693384a77d60025a4f2bc1e72bf71ac3df8d009fbdf28482685582e'})
  SET c.content = 'Alexandria is birthplace of Cleopatra'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074199Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q87'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e4edc5329d509a79b05965f9f19cef6440d434f1610edb05293843a4ae1b4781'})
  SET c.content = 'Julius Caesar —[DEATH_PLACE_OF]→ Theatre of Pompey'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074237Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q944814'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1d0e409285afb4fc56a980f46d0746e5535486aeb374022c556016c52572e09b'})
  SET c.content = 'Pompey —[DEATH_PLACE_OF]→ Pelusium'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074272Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q1145715'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2b745c9acf9b566977b77e99d24d42e9f763239b1ee8f9ee6536610b16020c39'})
  SET c.content = 'Gaius Marius —[DEATH_PLACE_OF]→ Rome'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074306Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q220'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f2ab5c4e801827c0c4bc7f27aa850aae9ec2e62b19ca709caa4c5a2d12ed64a4'})
  SET c.content = 'Hasdrubal Barca —[DEATH_PLACE_OF]→ Metauro'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074345Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q653678'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '77470eb5a52daff87d23d763e969f7e7ecdb9073d8b5fb7adcf7abde032e0168'})
  SET c.content = 'Hannibal —[DEATH_PLACE_OF]→ Gebze'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074376Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q206116'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5ac4efcc5173c6ae9594d432370d1cdb110cfc455ae69c1822abaeb8df2d3550'})
  SET c.content = 'Hasdrubal Gisco —[DEATH_PLACE_OF]→ Carthage'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074407Z'
MERGE (subj:Entity {qid: 'Q452048'})
MERGE (obj:Entity {qid: 'Q6343'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fe88d423c4b44e8664ff5cb6d9ac7aca88902d4fd250b9332ab5568bae338d69'})
  SET c.content = 'Cleopatra —[DEATH_PLACE_OF]→ Alexandria'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074439Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q87'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4c25971a882fd666923e374711365965ebe623591c08beb824d50f04b2e5c4df'})
  SET c.content = 'Julius Caesar —[MARRIED_INTO]→ Pompeia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074471Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q234825'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3e87acbe343a46bb4c8cba1666d0af959c92cadea32965ee1fc8c73ff99f9a42'})
  SET c.content = 'Julius Caesar —[MARRIED_INTO]→ Cornelia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074501Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q235423'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7e298738316d006be4817459f323be4752a5488491c3790ad6b4d679559cb597'})
  SET c.content = 'Julius Caesar —[MARRIED_INTO]→ Calpurnia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074531Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q235627'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b52e8a5bf79ccd003812c831fd65b0f7be39cff903cd0a7651e9977417b5557e'})
  SET c.content = 'Pompey —[MARRIED_INTO]→ Aemilia Scaura'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074562Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q380857'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0d63599164a3ac3578bf46987afd23b641197c30557703557df1a39f121da136'})
  SET c.content = 'Pompey —[MARRIED_INTO]→ Mucia Tertia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074595Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q273616'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5adccae2afa9ebb3629da1a03229c95f776f025a7b9765d80c161b1416813c03'})
  SET c.content = 'Pompey —[MARRIED_INTO]→ Cornelia Metella'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074627Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q270384'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'eeb9d6eea7c068ebc552f50d1948bc1bef13e46ee0743cef7cbfb4810aebf278'})
  SET c.content = 'Pompey —[MARRIED_INTO]→ Julia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074656Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q235087'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6cd99d8df6531952d06cc93154a86840c43a9586b33af0a359d67739f22d1c1a'})
  SET c.content = 'Pompey —[MARRIED_INTO]→ Antistia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074686Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q518068'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a272e6f2066d181f93aeb68dd6f3275900f8b2c47f9aea6f6bc7a0424ee049f1'})
  SET c.content = 'Cato the Elder —[MARRIED_INTO]→ Licinia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074720Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q1281529'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a63074a8d091d136f3042840c40ad0af7766e613db7b44e4a5806504878edd7b'})
  SET c.content = 'Cato the Elder —[MARRIED_INTO]→ Salonia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074751Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q435959'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '03139b320857eb437af5d81ee073143a894e45e99b7d339a463988116e4e12b8'})
  SET c.content = 'Antipater the Idumaean —[MARRIED_INTO]→ Cypros'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074783Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q2583477'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '61a42dec932f8be830fcbc90bd75c2687c53da81ea399bcbfcddffde38c03a40'})
  SET c.content = 'Julius Caesar held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074818Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e6fc91b335e9697d60fafa3a980ccae61fbbeac3bccc2a757a5621e180c70d51'})
  SET c.content = 'Julius Caesar held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074850Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a51dfa30b4847a06ad1410344cc7171bd42f59b563b54fc9a7dc2d68056fd5c7'})
  SET c.content = 'Julius Caesar held office moneyer'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074880Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q1861571'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '57774e0d4c62fe9c64653e932b78306ffaac4fe9e26bc8d325350d9c7bbda813'})
  SET c.content = 'Gaius Memmius held office triumvir monetalis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074913Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q7844592'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7ec932ec0297d14f49df4c31bf51407e5663977751fd9ef36cf329388b04dad6'})
  SET c.content = 'Gaius Tarquitius Priscus held office Praefectus'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074945Z'
MERGE (subj:Entity {qid: 'Q11950924'})
MERGE (obj:Entity {qid: 'Q5183538'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '89490809527d17c122dc64b6894fe0b0f15df773a109d10d49527287ff90af72'})
  SET c.content = 'Gaius Tarquitius Priscus held office legatus'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.074976Z'
MERGE (subj:Entity {qid: 'Q11950924'})
MERGE (obj:Entity {qid: 'Q212624'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c787a86273529eae32d979ac921669c01896a05e02a98b2c60e748fe2eb9ca19'})
  SET c.content = 'Lucius Thorius Balbus held office triumvir monetalis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075039Z'
MERGE (subj:Entity {qid: 'Q1247730'})
MERGE (obj:Entity {qid: 'Q7844592'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '91d1510e87c742f8e693ffc50f4e112a0923135f8b1a032a25e49e1620f84528'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus held office tribune of the plebs'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075075Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q11704729'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '39aa70132bde22bd98a3caa5589c19ecd71d7ae67d99194625df31ca4687c991'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus held office consul suffectus'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075108Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q629712'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6b9c5db231b1e113a2be948798bc9dc9a7f7afabd2776fb845d19f1fbacca55e'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075140Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '97d069413e6343aae04df1553c50815a631a7f58769beafa9d7729d71de54918'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus held office decemvir legibus scribundis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075171Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q1969993'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5d5e5971d7c7d34d6cb20a8f33606142b810cc5457d7b19f3fe6271165e2613'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus held office Praefectus annonae'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075206Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q581899'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2d4b01b1850d552c82c53013c36e997f69e23404633895c0b2d7e7cc987e94bc'})
  SET c.content = 'Pompey held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075236Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e12f45126ba80d0f834d97ffad15ff2082bc4eed2252288f1a5772621a9bf945'})
  SET c.content = 'Pompey held office moneyer'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075265Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q1861571'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '62add6a768f2d0055b89525bdc79cdff0b670aae1c00eb995be92f9f5c4627f9'})
  SET c.content = 'Pompey held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075327Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ee84f61579d43ef7d7fb92fda37a314d00b28213d5bc39c65ca8e4ddeb2b8ef4'})
  SET c.content = 'Marcus Junius Silanus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075360Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '67db9155efbe58f9bfdbe167ae1bdff0c204b0fcd997b56392be0c07c55b00f6'})
  SET c.content = 'Marcus Junius Silanus held office Praefectus'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075391Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q5183538'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e461f0b0b2165486e642f48fa714ed6c3cc8116dd0da13ea937a733250240681'})
  SET c.content = 'Marcus Junius Silanus held office proconsul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075422Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q2912782'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '673bfa7aed77518afc76121d843c4ad06c88992b2b2b84f2613fff4963d19a3d'})
  SET c.content = 'Gaius Marius held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075452Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6d99c24f679b896c197a0cd3417ddecb7395096022888bfa840b7b04c7830054'})
  SET c.content = 'Gaius Marius held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075482Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1163e52aa6e73fc607227215022b7613bcbe2c3d2711ee5f0ee8a919f6fed528'})
  SET c.content = 'Gaius Marius held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075510Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a4eaa7bc07f894dfd768bd918445258158e2978c46f34da733f3cb878f4736a7'})
  SET c.content = 'Gaius Marius held office tribune of the plebs'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075542Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q11704729'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '33666d9baf2bf17eb3b9370a5db7917e20398527605d63c3e2926fc7d8e17fdb'})
  SET c.content = 'Cato the Elder held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075571Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd481309e81f18e08213c9d6465e884147187194236e8fb12aa3b6c26773ad45c'})
  SET c.content = 'Cato the Elder held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075599Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0be66842d08ecfe592dea5437d68e92d56c3dc7f97a5f69c6bcaac29f5445923'})
  SET c.content = 'Gaius Cassius Longinus held office moneyer'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075640Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q1861571'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c0d436f4ff6be66e9c3538b1d7e59f2c4ef0cd828a68ddf6c39cc6de0a177495'})
  SET c.content = 'Scipio Africanus held office proconsul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075675Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q2912782'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0fb235ef64fbd25ad15d09b9bd4d92a5c675d580af8acac2b2f32c41ad94cf05'})
  SET c.content = 'Scipio Africanus held office aedile'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075709Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q205757'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b55f646c7daeb29852b9b15ed5bcc2295f6ffa5038002abf8b2777a3525fe4bf'})
  SET c.content = 'Scipio Africanus held office Roman censor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075742Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q189851'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3cc09f898498ee3288a9087fc44f20f278e06f0e452f54da1a43cf7efde5b2d7'})
  SET c.content = 'Scipio Africanus held office legatus'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075775Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q212624'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'af5ad62f3c8d5198aec3846f211bff997d12624644732b6af9f2c82498310bed'})
  SET c.content = 'Scipio Africanus held office military tribune'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075811Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q849288'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ef4514a4429b3b1bc06014740f71a0d6253b76ddd88b52ca5efba0fc1fa5bcd8'})
  SET c.content = 'Scipio Africanus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075841Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5407bbb6f04dca16596f5e4360a1446d693223c880b3e82dc6fb7a3d255808ac'})
  SET c.content = 'Scipio Africanus held office salian priest'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075899Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q106211846'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '095806c8eda3ab3b4d7d5c2382bb9aad780ba28ff48bfae6888de1790e6ab9b4'})
  SET c.content = 'Lucullus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075960Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '445cdce9b7dfea197313d3579fa26e4a4dad5bca8dda20d9556b22876e293f91'})
  SET c.content = 'Lucullus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.075995Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7e27594c66237927caf16062e00f4c639c69e1d7eccfb5ce77daabc3275edd26'})
  SET c.content = 'Lucullus held office aedile'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076027Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q205757'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6539b5233afca9cbc3836d7983775b56d6586d446a995453a3daf8ff6fa68123'})
  SET c.content = 'Lucullus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076057Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '836f37fff807d5daa73fbf88762a047d8fa2a2eb60f1b08373105727e2ca10ef'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076089Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9164175dfe8fe7820beea14320dea8d7c02aa38d0df26221e734fc5714b6b15a'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076122Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '07e415bb5215f4acd55a8ee827a09c6abe1d1bdf08ed7f90dca7376b538f41e5'})
  SET c.content = 'Cincinnatus held office Roman dictator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076153Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q236885'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b5230a146a6940c9e2fbac0827dc4e4f86d8c3f40eafdec31438f6ce05ccfdc3'})
  SET c.content = 'Marcus Claudius Marcellus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076187Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '767473ef53ed3efc55dfcfc5fb40c3ffd29ca5b4c0429cc8851ffa3705e11c9d'})
  SET c.content = 'Marcus Claudius Marcellus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076219Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ad8c4c65705df39b2577b578c57a0111939d666ff53b7e3294947e831dabd36e'})
  SET c.content = 'Quintus Caecilius Metellus Pius held office triumvir monetalis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076251Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q7844592'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd7beea7ac42e8f051a56638b20e4a2b095415f90bb43c1e9c6386b3e7edc3906'})
  SET c.content = 'Quintus Caecilius Metellus Pius held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076285Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bdf88190119e0a1772f95e61e8497a3587b789237f31db65d5ad966247311262'})
  SET c.content = 'Quintus Caecilius Metellus Pius held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076318Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '80e75ac57b811d357040050ac6020eb9d809d77f0e0c7a201e3fbe483e59994d'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076350Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c1a078d5b0cf249a913e1c307c460f580f71e9080cd55e4bf3b54df8ffb5197e'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076381Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8bccfa8ce6bed089324ac484e4be1e306c843d45ee785a5702e9fe0604cb22e7'})
  SET c.content = 'Publius Cornelius Scipio held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076413Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ec4df574cde4c2ab1b47c5229613f877a71dc9c0d3e167218d356a73c8bfda5f'})
  SET c.content = 'Publius Cornelius Scipio held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076448Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '899fe48c096ee1145379c4aeeefc7ef664da7c27752bc7d464355b355cf71d01'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus held office triumvir monetalis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076481Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q7844592'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ea754f10617c2e7c7b257566d9cc5d3b3a698cd9c22dff7deeb0cacaba847cf6'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076513Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c03e4917014e8b69feaf432fbf212341a2add699a06792ce7ee9e841bc9577f8'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076547Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '362ac4f8b2c6efac034b1a3580197c435b8c013eed75c6d62f09ccf2aa354229'})
  SET c.content = 'Tiberius Sempronius Longus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076579Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5b79d905fea40bee86071b280dceacf578a9efc08520e7636c52e4891a23edb9'})
  SET c.content = 'Tiberius Sempronius Longus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076613Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aff029c74ae5796e0e88dc09ce93ff489d57a2a9bb8737a8ad33ebdd23278602'})
  SET c.content = 'Tiberius Sempronius Longus held office decemvir sacris faciundis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076644Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q127606216'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '126f94112aac0bf34314ec52c75aa867dac392eb6cfc6ea72fd94a80e1eca523'})
  SET c.content = 'Lucius Mummius Achaicus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076676Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f13e5d7c22811cd46e4247355c7ba9525eab76b844b1f26b13a5fb513d8d114f'})
  SET c.content = 'Lucius Mummius Achaicus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076708Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bd78ea7822540f718c32256d29acd5efe746ea2f0c90a7853506ea67f9491684'})
  SET c.content = 'Lucius Afranius held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076740Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1cfe5558e27b235c340759701b59b58fac1c74db0d188c88243fa72cfce98484'})
  SET c.content = 'Quintus Labienus held office triumvir monetalis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076771Z'
MERGE (subj:Entity {qid: 'Q551516'})
MERGE (obj:Entity {qid: 'Q7844592'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0c06b3be5ee4875ec8f8301bfb707d640ec9da3ef62c14a79c9f558b972e32a1'})
  SET c.content = 'Tiberius Sempronius Gracchus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076807Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aa918351e737608d62e8252a7f4ca08febc5cb5ee2301578d05255c62c977a4c'})
  SET c.content = 'Tiberius Sempronius Gracchus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076838Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd70e78d56f33a8a9c5df7405ec79005e7a2b9bf850396dbf1f029b20675df691'})
  SET c.content = 'Cleopatra held office pharaoh'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076869Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q37110'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '88f4d3c7f1d3bf5b3f2da94745463fddfed68a0fdd4369eca17c71a6fea6d3f1'})
  SET c.content = 'Gaius Aurelius Cotta held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076898Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '435910098468db967ea125f7f9a999c4202e371f28d7864ba61aba65bdbda972'})
  SET c.content = 'Gaius Aurelius Cotta held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076929Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '204c93c45a59474b6ebe325911a8bf0bf066253bdc7b3cfb6ca001e1ca6c4269'})
  SET c.content = 'Gaius Aurelius Cotta held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076961Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fb97883d54712d283a4f5f92d670c40f8730c685ffd69412bce77da8d0c0ebab'})
  SET c.content = 'Gaius Laelius held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.076991Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '16254f49bd30611f453af3dbb13f5343a66b4787f1664e03371ad54de8a1dcd4'})
  SET c.content = 'Gaius Laelius held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077020Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3aaded08012252ca49c4cbaf46285d84eed8e619d53c8a64343b287f0b6c5bfb'})
  SET c.content = 'Decimus Junius Brutus Callaicus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077051Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5d69e60d7d51b30db64a4e18422cc77efea9c65a951a28f78715f393cd55e633'})
  SET c.content = 'Decimus Junius Brutus Callaicus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077081Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '36f0c9ec4e925326e5929da802c66d936058cbf69dc832dca6c008334a78a280'})
  SET c.content = 'Decimus Junius Brutus Callaicus held office proconsul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077110Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q2912782'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aaaff6a4f24c7630730503124ea3946f2b7dd3821d447803afaef89296549541'})
  SET c.content = 'Decimus Junius Brutus Callaicus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077141Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '896628df423b8eebe77565d101bdc3a7ae6816eb1eec8e1a5586c06e26a9cf46'})
  SET c.content = 'Marcus Aurelius Cotta held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077171Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '238990d74a9406bb504bcfefc5ca1441421132d26c3f10720215a57b5854cf16'})
  SET c.content = 'Marcus Aurelius Cotta held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077201Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c5a985d100853e7a370b0c4be8e88325f206702c5451b37fa15c6a388dd647de'})
  SET c.content = 'Lucius Cornelius Balbus held office moneyer'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077231Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q1861571'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5504ba7b23fa762d2d07f8f51a50fa8e456dd730b592db629cd4f9503bafc2cc'})
  SET c.content = 'Julius Caesar is parent of Augustus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077261Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q1405'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e15a9381bbca65f30dc4fd0a4c385d2c5eabb4f26d72c257aa5948607620e1b0'})
  SET c.content = 'Julius Caesar is parent of Caesarion'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077292Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q39589'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e2fa2781a63af570d97ee0cda6625163ea490c779474783e082a5020f08168a6'})
  SET c.content = 'Julius Caesar is parent of Julia'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077320Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q235087'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'efc56bd40f06106a3cd6e312061ef6c708ce47633d06789dabbbcc79dd2e7d38'})
  SET c.content = 'Pompey is parent of Gnaeus Pompeius Magnus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077349Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q473280'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a214ca7c5356d8680e837a1bbeadd6b733298a38847ec9501872d90e48dab767'})
  SET c.content = 'Pompey is parent of Sextus Pompey'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077377Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q295228'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b39f30d7bf4036594fa99d6c480edd062ad8ec99522053f96d86886755ccd006'})
  SET c.content = 'Cato the Elder is parent of Marcus Porcius Cato Salonianus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077411Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q1181865'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b17b196207c08e39098aa5160b7f814cb15b0777ad6e28a6cc01c6025d4478ac'})
  SET c.content = 'Cato the Elder is parent of Marcus Porcius Cato Licinianus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077442Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q1275684'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '24cf47f29d9222558d2ec33776e14f4f221922e1b9df89f3e60a0e01b57cfed5'})
  SET c.content = 'Lucullus is parent of Marcus Licinius Lucullus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077473Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q11934113'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f1fe91ceac07ba4e8e307093f663fc02408f0941db6afd9272821a8fd66c51e4'})
  SET c.content = 'Quintus Caecilius Metellus Pius is parent of Quintus Caecilius Metellus Pius Scipio Nasica'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077506Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q316825'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cb2b5e4d4a8ba478c174091a90262c6602fc6d33d716b03da6ca0f37a10d04f1'})
  SET c.content = 'Massinissa is parent of Gulussa'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077536Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q376669'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a82f90becb448b25c66ceed9459e9f9e8564925efb4530d6c73d913292ffcf05'})
  SET c.content = 'Massinissa is parent of Micipsa'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077565Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q54223'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e4102d4f82b5cd1f5f3239041361afff1f070d6696cf7b5cdbea9d24521f054d'})
  SET c.content = 'Massinissa is parent of Mastanabal'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077592Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q94621'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bd11ed78062a3a673bdb86f9c8c3661e65499256ad45b8a0c37158e2e846be52'})
  SET c.content = 'Tiberius Sempronius Longus is parent of Tiberius Sempronius Longus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077632Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q1275151'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '24a8ca7b6a8629f645ac07f90d76366a8da1b5baafb160932880e1c3e6c0f1ba'})
  SET c.content = 'Cleopatra is parent of Alexander Helios'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077668Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q351538'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6846859943daf177eab946e321343283743e9c665303c3389eb2076f61d0fdc9'})
  SET c.content = 'Cleopatra is parent of Cleopatra Selene II'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077701Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q40058'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5a876bbc1207816bb5e150a219ad7472bdaee87f18f2e28696794b167b9f8d11'})
  SET c.content = 'Cleopatra is parent of Caesarion'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.077887Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q39589'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4a74c41d155041319fe8d1bd5b2c1a47303f07cf8a98b6eb1ec784869788d6fa'})
  SET c.content = 'Mago fought in Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078013Z'
MERGE (subj:Entity {qid: 'Q335604'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0a1a55c009bfd0e12a532f3093772b0f4804c70385763a68669bfd54c031e0bc'})
  SET c.content = 'Punic Wars had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078147Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a7d8ba485990e92ec0d0b3d9882b2846c8f81010a45f9458aa1447ffa19a3abf'})
  SET c.content = 'Battle of the Axona had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078269Z'
MERGE (subj:Entity {qid: 'Q1260622'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.79
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1aca65c4150dd109be63f2e11303c56ac9edde548b1478de60158f2c69165a70'})
  SET c.content = 'Battle of New Carthage is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078370Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.74
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '75d446a94d6e476ab4daa2dc3e38f7ddd0f2bd8ee053c844bdd7bc3c8d73d193'})
  SET c.content = 'Roman Republic —[BASIC_FORM_OF_GOVERNMENT]→ aristocratic republic'
  SET c.source_id = 'wikidata:Q17167:P122'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078423Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q666680'})
MERGE (subj)-[r:BASIC_FORM_OF_GOVERNMENT]->(obj)
  SET r.confidence = 0.73
  SET r.source_id = 'wikidata:P122'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f1209acb5e05ad5bdadb59a40963dd0d67424e5e6342af89e66ce80621ebf4fb'})
  SET c.content = 'Roman Republic —[CONVERTED_BY]→ ancient Roman religion'
  SET c.source_id = 'wikidata:Q17167:P140'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078474Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q337547'})
MERGE (subj)-[r:CONVERTED_BY]->(obj)
  SET r.confidence = 0.73
  SET r.source_id = 'wikidata:P140'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5f45c1196f50686a8c2ac47c3a4706dbaa99fab538fc0827fac9487900a04779'})
  SET c.content = 'Roman Republic —[LANGUAGE_OF_WORK_OR_NAME]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P2936'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078511Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF_WORK_OR_NAME]->(obj)
  SET r.confidence = 0.73
  SET r.source_id = 'wikidata:P2936'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bbcc1a01ee6428e32d906b56144e8f9b67c149ae775dfef232dfdc79981d2388'})
  SET c.content = 'Roman Republic —[LANGUAGE_OF_WORK_OR_NAME]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P2936'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078549Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF_WORK_OR_NAME]->(obj)
  SET r.confidence = 0.73
  SET r.source_id = 'wikidata:P2936'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8c767341f8028e2c5e2390e05a873ed12b23172d4c404f2e0ff25a9a76ae796d'})
  SET c.content = 'Roman Republic is instance of historical period'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078589Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q11514315'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.73
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7b98fbe0e553eda35829b4779397cdfcd90ce1af3af7b6edfce0a778d7b0f1b2'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ poet'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078675Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q49757'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c89e6bb3b39bb666936ac9a62d4fae8983a9412447d39dffb55ce68a0dc114d4'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ ruler'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078711Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q1097498'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '56beae2a0c1ab20fbf23bd657ecb005e36a7bdbac75ab957f1c91c30ab25762f'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078743Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7ba11289c6c6d1f7c1aa16fa4e7c8378e43f55560524644b89cf78d1fe7fd1b8'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ historian'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078782Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q201788'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'faece412dce528000fbd27ce31abce8fba8caf17236ac9f417295d7f84221fe2'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078813Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cf4926b2f92144a03c549a9c4e804bb9bd49d872b67423a133864249964f4e64'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ writer'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078844Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q36180'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4f4c0782bd57e4c5011e7b8cbe026833e43cd343b6e1f291ef7b71b8b74984b4'})
  SET c.content = 'Gaius Memmius —[OCCUPATION_OF]→ mintmaster'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078874Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q1463475'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd22d698ec794fe8b5bd73aeb956911a8929d48c2b023caa0d2a2d5f6d89b38ae'})
  SET c.content = 'Lucius Thorius Balbus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078909Z'
MERGE (subj:Entity {qid: 'Q1247730'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dd96535f75b5a08bee162ff1e331c7175d19c07c201fac3e43f1b05cb4861808'})
  SET c.content = 'Pompey —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078940Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '499141d39d0a84223b8ad87b48779656e91d4674f963bb0e267acccbc01cde89'})
  SET c.content = 'Ganymedes —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.078970Z'
MERGE (subj:Entity {qid: 'Q1493701'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9277d663420dcd8b5fe90733b2addc4cb1106deb88117fdd54a58a8c9a0b555f'})
  SET c.content = 'Marcus Junius Silanus —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079002Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bd082edaf1156687fc90ea3582e600310a13e0d16c5ec448792001400c4a1df6'})
  SET c.content = 'Jugurtha —[OCCUPATION_OF]→ sovereign'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079034Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q2304859'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '071292792079bbe4c0548a269c57c481783b3e53fe3c48c6422c08e78c1b637f'})
  SET c.content = 'Gaius Marius —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079066Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8cc65a65de206463d8b6ae3a405900586df68e2586822e3341324ffb46d66ab1'})
  SET c.content = 'Gaius Marius —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079099Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cdcf2c1e38955cf03a9f5b8e12bbadf262ae31743113c65ea116f29e47dd3a90'})
  SET c.content = 'Cato the Elder —[OCCUPATION_OF]→ writer'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079130Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q36180'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '39756715111a0c8df2912d88353f7ab580bca00fcb3d5547ef058dc9c86f7aad'})
  SET c.content = 'Cato the Elder —[OCCUPATION_OF]→ philosopher'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079162Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q4964182'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8073444eedf52a6d41afe34b724bb3cf762423fb4a36d989821ad09dc82221ee'})
  SET c.content = 'Cato the Elder —[OCCUPATION_OF]→ orator'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079194Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q12859263'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2c7ae09e58eabd1d1cbc76a0d4a659f6cf425209278f9773c11d842d34bf0dbc'})
  SET c.content = 'Cato the Elder —[OCCUPATION_OF]→ soldier'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079225Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q4991371'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1d10997dd5cf565d59349eb599f78c001cf8a414ec8d7b9f568f985eebbc83fc'})
  SET c.content = 'Cato the Elder —[OCCUPATION_OF]→ historian'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079257Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q201788'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b78efb2dcb2b5e6157a15b1b0bab7d391b24b6076efc9acc24a3a9425368494a'})
  SET c.content = 'Cato the Elder —[OCCUPATION_OF]→ poet'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079289Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q49757'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f15c92969716fb538f6500480366d0a36b71774f4aa583e2a4177c3565b09db8'})
  SET c.content = 'Cato the Elder —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079318Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '985321bee0788a348a36a3c4eb938c766f1a3c8f26b7caeb067d8216f7e66c88'})
  SET c.content = 'Mithridates VI of Pontus —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079352Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '296618cb370d312a70593e585f69ab37e7b10b8b53aaf2a329f00e71c1f9981e'})
  SET c.content = 'Mago the Samnite —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079386Z'
MERGE (subj:Entity {qid: 'Q18668725'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '21f55ebd049d0de566240a9b41d3524a4b87560b1bfd4e7d3fa5da89924f9671'})
  SET c.content = 'Scipio Africanus —[OCCUPATION_OF]→ genealogist'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079421Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q8963721'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '898b9bf3893911dcf42f4a0fba7e5c671f92d685d01c1e9b75f133ca464a2fca'})
  SET c.content = 'Scipio Africanus —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079452Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e3a60e6134fe969230b94105210a61e8bb96361cbc703fe9aef2a64fa4f6cdfe'})
  SET c.content = 'Scipio Africanus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079483Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4b57fe0aaceed36ef44b93c7d3be4a7e3d35654eeb3f50252aadf6decd62d9d4'})
  SET c.content = 'Lucullus —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079515Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5e1c99ce7c3ee53b00ed10e5871b34a73ea7f68feef1d34aacdbaf0b080c71a0'})
  SET c.content = 'Lucullus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079544Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '92ca498c4a52cfcb87768ec93d06445cb3dfb73344a99bd3c730cbe35a9f7240'})
  SET c.content = 'Hanno —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079576Z'
MERGE (subj:Entity {qid: 'Q2525841'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '627b474e1fcb4dc075f64b2e5dc43da6d50a1d6c9bab491d16b065de741c5189'})
  SET c.content = 'Cincinnatus —[OCCUPATION_OF]→ farmer'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079633Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q131512'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd5aa973702de7b869fe840758c08cd0dacc7c5edb8c9608ab19fd1a8961d77d9'})
  SET c.content = 'Hasdrubal Barca —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079697Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1fb7f01e6bbc6eafd3843709583275ac6b6e7cdf4e6b2b7dfd2719b048a80f96'})
  SET c.content = 'Marcus Claudius Marcellus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079752Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '391f6e179b05b83bcb1e9aa9a2508272b4b9920d4fb627932da898aabb1d2b32'})
  SET c.content = 'Marcus Claudius Marcellus —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079792Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '21ca98dcf6f6f7e9e11eaff0e6badf0ee8092c45288599d49a9c000e3077a82b'})
  SET c.content = 'Massinissa —[OCCUPATION_OF]→ monarch'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079826Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q116'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '63f3d9a4d0ba0b1673453f5effa55dee2a66558891e6d7ab214d7454f1819ec0'})
  SET c.content = 'Publius Cornelius Scipio —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.079862Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3fdf653d0dc775d161fa573df873fb0dd4b077ed6b36dd5e99716fd80692a449'})
  SET c.content = 'Publius Cornelius Scipio —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080066Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0531822404d9b9a5eadbcf2a87f9a6e0e60ad82f669c29a208ee7f8cf246b607'})
  SET c.content = 'Publius Cornelius Scipio —[OCCUPATION_OF]→ Roman magistrate'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080103Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q20778343'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1601c1b7a19119ff17cb8faa6ab9332df3c488fdd678e7cf95e9611ff44db594'})
  SET c.content = 'Mago —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080137Z'
MERGE (subj:Entity {qid: 'Q335604'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0bf50d2e24bee5551bb0622a5ab66ccdf9de6fcd2dc131a61b68357a3a7148c6'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080173Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd42b4ebc41af6872757557d4eb4ef8ee07925aa6b2d774c5ed1ff341ca2e9958'})
  SET c.content = 'Pacorus I of Parthia —[OCCUPATION_OF]→ sovereign'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080207Z'
MERGE (subj:Entity {qid: 'Q358097'})
MERGE (obj:Entity {qid: 'Q2304859'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a7cdd0ee13ce397ef57fcdec504e0aaf6c1fbe61bd18127bf1f4ea1f694f8ceb'})
  SET c.content = 'Andriscus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080300Z'
MERGE (subj:Entity {qid: 'Q362068'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5896f36c1b98ad0a3aa265c45edc3ab487bf320f81367c63c069d3d49e8cecc4'})
  SET c.content = 'Hannibal —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080341Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '837a2eab5e73a6065919133099b7738228401244786b10e951eaa260b0c4adc1'})
  SET c.content = 'Hannibal —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080379Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7b8e88a67e17b94f10c5689c85ced4c64c993e47480121daecaa32e4d3915f28'})
  SET c.content = 'Ptolemy XIII Theos Philopator —[OCCUPATION_OF]→ sovereign'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080419Z'
MERGE (subj:Entity {qid: 'Q39938'})
MERGE (obj:Entity {qid: 'Q2304859'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd6585a39409c8d4ac34c7b797e6dfd563d216723ab75caba84a11b090f27f51b'})
  SET c.content = 'Hasdrubal Gisco —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080453Z'
MERGE (subj:Entity {qid: 'Q452048'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bac159638158963cb8e49d37b73c7989864db05f1625e9d6ca096a63265cde97'})
  SET c.content = 'Quintus Labienus —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080488Z'
MERGE (subj:Entity {qid: 'Q551516'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '053dfc66f85706c0e026470f8a2b6b85a07f9ad0af9723a3ec6c6e3ad8506643'})
  SET c.content = 'Lucius Marcius Septimus —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080519Z'
MERGE (subj:Entity {qid: 'Q5759209'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b7461f53516fbe8654c58fd17fac79f910c0cc58d87484b204e210076498735e'})
  SET c.content = 'Indibilis —[OCCUPATION_OF]→ traditional leader or chief'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080549Z'
MERGE (subj:Entity {qid: 'Q604308'})
MERGE (obj:Entity {qid: 'Q1259323'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e7e229ea5b59eba31c6c259e30dc7039815b072ac7ab4ed766f9e152d3599eb2'})
  SET c.content = 'Cleopatra —[OCCUPATION_OF]→ sovereign'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080579Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q2304859'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7d81c436eaf0516a54d7d993f84c695fb18697bd25c363a387e6b26863543e28'})
  SET c.content = 'Cleopatra —[OCCUPATION_OF]→ monarch'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080607Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q116'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '66e9c8263118c1cff9a614f7e16923653d83689607425bbe64ad1d7985d33dfb'})
  SET c.content = 'Lucius Hirtuleius —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080654Z'
MERGE (subj:Entity {qid: 'Q6456490'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '34f9d0b72bec9648810add02c121a9d33cdb326530f72a57761aaa7306f5cc56'})
  SET c.content = 'Lucius Cornelius Balbus —[OCCUPATION_OF]→ writer'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080689Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q36180'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bdb4b2241e604ede8ca02f58855cc0cd9d22818d31bf89afda2aa2b190f0ab47'})
  SET c.content = 'Mithridates I of the Bosporus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080724Z'
MERGE (subj:Entity {qid: 'Q878437'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8af07d0fbdb83201b27f3eb1adb676b1383f45f3a1dbbec574a3744b7fa7ee56'})
  SET c.content = 'Mithridates I of the Bosporus —[OCCUPATION_OF]→ sovereign'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080757Z'
MERGE (subj:Entity {qid: 'Q878437'})
MERGE (obj:Entity {qid: 'Q2304859'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '02a5e08c8a4cf534ae2720a3c6f23001476065bd9ffaedfcaf53dc22e2d98b8c'})
  SET c.content = 'Apellicon of Teos —[OCCUPATION_OF]→ patron of the arts'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080792Z'
MERGE (subj:Entity {qid: 'Q9158420'})
MERGE (obj:Entity {qid: 'Q15472169'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c77b4a1233070ee6a9d533ed0e1f26d6cc20a69568fbbbeacd3f6ece68270433'})
  SET c.content = 'Apellicon of Teos —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080824Z'
MERGE (subj:Entity {qid: 'Q9158420'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5bbc0424c57898051457572bc8d7e03d4f3452367ea50a1ce0cb98f579f38419'})
  SET c.content = 'Julius Caesar —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080858Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a184db4ba6ff4c49f8ac6437bb5275e61f0c54b555fd55498d9db755400c0367'})
  SET c.content = 'Gaius Marius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080889Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9433747eab4c675f536acdd3718ac60880c8713d9b89282d053be29ff777e1e1'})
  SET c.content = 'Cato the Elder —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080923Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b00fc5647df94cdf35851586fbc7df37a46ec4913b49acb40d180121da02af32'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080955Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7ee335f0ef20c6c164594d20dbecbabc09df90f0a281ab4a153b5a6b252afceb'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Koine Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.080985Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q107358'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dd6f828c6e83c72646298b05fbfb3bb9cfcaaa74c746cf9f2595ceb9f9e98745'})
  SET c.content = 'Spartacus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081015Z'
MERGE (subj:Entity {qid: 'Q83406'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '927ba284d583be1ab7728b3cb2d1294fac36c88f351b38e843f5ef60ee0ad7e5'})
  SET c.content = 'Ambiorix\'s Revolt was under country Belgium'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081053Z'
MERGE (subj:Entity {qid: 'Q2505574'})
MERGE (obj:Entity {qid: 'Q31'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5414598b0119ac24ffcf6584f7add78419744fe96502ed25542cd28062bebc1'})
  SET c.content = 'Ancient Rome is birthplace of Lucius Minucius Esquilinus Augurinus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081091Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '41bfb73e9d4db394b842c9612338d44a7a1152ee6fe75e5beb35b4a12a839dc8'})
  SET c.content = 'Cirta is birthplace of Jugurtha'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081123Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q1093156'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '264c8b36b375203c76524824868da1a4505b5659508d13496b5adf2c69587289'})
  SET c.content = 'Tusculum is birthplace of Cato the Elder'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081156Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q754314'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6a36ce2fdc7b5fe42f33c69e5779c8f9c33f657fd09bea8eefed234dbf2e1c9b'})
  SET c.content = 'Pella is birthplace of Perseus of Macedon'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081189Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q213679'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f9e9d00a7e219e13035b9f86ac4ce5e04bb97d660074af9ea2a992c5b952e433'})
  SET c.content = 'Norcia is birthplace of Quintus Sertorius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081218Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q20494'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1ca0cb5edbbb1fee805f93a242afaff7925febfef0d449deaa673078e7edd883'})
  SET c.content = 'Carthage is birthplace of Hasdrubal Barca'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081248Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q6343'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6876d5e179e40c0dbdd80c69cd4b168be2d4bc95ed1af0d557aa25399c1a23d9'})
  SET c.content = 'Mysia is birthplace of Andriscus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081277Z'
MERGE (subj:Entity {qid: 'Q362068'})
MERGE (obj:Entity {qid: 'Q622319'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fb92bedc28668ecbdf0c9f748dc07410118a491b2955f2e4aef3ebb6916c0b52'})
  SET c.content = 'Egypt is birthplace of Ptolemy XIII Theos Philopator'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081307Z'
MERGE (subj:Entity {qid: 'Q39938'})
MERGE (obj:Entity {qid: 'Q79'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4d6fe06e3c3af5059c7e997bd2db1a2fcab6b76cba52681fc8c0bd7ece0a80a3'})
  SET c.content = 'Alexandria is birthplace of Arsinoe IV of Egypt'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081340Z'
MERGE (subj:Entity {qid: 'Q40013'})
MERGE (obj:Entity {qid: 'Q87'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cf44b14717351a55ab8f5d794c1ea61ec400b6b1a01a0905d9e942acbc2b0ac3'})
  SET c.content = 'Cossignano is birthplace of Lucius Afranius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081372Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q56053'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '42061c65544eb01384d287cd027f8c375a4ffd0bc1ce435e0922e084d8366520'})
  SET c.content = 'Lusitania is birthplace of Caesarus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081404Z'
MERGE (subj:Entity {qid: 'Q60695198'})
MERGE (obj:Entity {qid: 'Q188650'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b1ba4b3e6f85aba225f394ca0c89768cd70df3f21974f269b55eb1ae583dca55'})
  SET c.content = 'Thrace is birthplace of Spartacus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081433Z'
MERGE (subj:Entity {qid: 'Q83406'})
MERGE (obj:Entity {qid: 'Q41741'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b63d727758f6e54145ced3168ce71f26bc93c13e9ba52d8ef5555ba8546e9b09'})
  SET c.content = 'Teos is birthplace of Apellicon of Teos'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081462Z'
MERGE (subj:Entity {qid: 'Q9158420'})
MERGE (obj:Entity {qid: 'Q17586'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c8961ba4228c8f2341c7cc9ae0e59b8cad71acd561bdca03ccacb4c47ca21e3c'})
  SET c.content = 'Gaius Memmius —[DEATH_PLACE_OF]→ Sagunto'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081494Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q47483'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '292c26c83d7d34e8cb4e3147c246e579ebd6f1c661035b007e0f21bbd8c73900'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus —[DEATH_PLACE_OF]→ Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081531Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c18b6eb61a30c1432f9047d0686577aecc6dd35d36c3cf15ee82b26e0320e96e'})
  SET c.content = 'Jugurtha —[DEATH_PLACE_OF]→ Rome'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081561Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q220'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '20b374bcf9debac4412ba0a88de244aba6ff5a3bd56541ce9e0e24577aca6ae7'})
  SET c.content = 'Cato the Elder —[DEATH_PLACE_OF]→ Rome'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081591Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q220'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3414d181d1d098d85dbfbc039a8251cedf8bf932f4253f3bda995c744666023e'})
  SET c.content = 'Mithridates VI of Pontus —[DEATH_PLACE_OF]→ Bosporan Kingdom'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081623Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q321371'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4b1f0fae7bb810c798dce9e8fda588620f3d9a2cf20c5ba5bdff43c9d9e6d534'})
  SET c.content = 'Perseus of Macedon —[DEATH_PLACE_OF]→ Alba Fucens'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081659Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q944515'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '67015e1905275c1abe6f1da36f221e9011d183cf5d4862e93808f1193d3cc0e4'})
  SET c.content = 'Gaius Cassius Longinus —[DEATH_PLACE_OF]→ Philippi'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081700Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q379652'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ab730f7320846be13aedf5b42f1ad4797845c8da4becc3ac4a5b156b4441a12c'})
  SET c.content = 'Scipio Africanus —[DEATH_PLACE_OF]→ Liternum'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081731Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q898417'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1ee44c4c31fa736657a0bb9d58a42605bdfab16637dcd722fd20e7cbfe0f7f7e'})
  SET c.content = 'Quintus Sertorius —[DEATH_PLACE_OF]→ Huesca'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081763Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q11967'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7c02b3988d8be25d77c8caf7b07808d3660af373fee1defc8d79e475769a7dcc'})
  SET c.content = 'Cincinnatus —[DEATH_PLACE_OF]→ Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081796Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7cc7b8cd9d4232348cdc43021c660c0c7926057a8cf1ea96f903bd5b7174518c'})
  SET c.content = 'Marcus Claudius Marcellus —[DEATH_PLACE_OF]→ Venosa'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081828Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q52691'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e27b3938407b55da1e6e66d594410389ab6a916afe1f753beb1ebfeaec33099c'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus —[DEATH_PLACE_OF]→ Hispania'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081862Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q186513'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e79f0ce33b8cc52406f22cf63d44403de4f01595dc523cea426b9e90da79c2f0'})
  SET c.content = 'Publius Cornelius Scipio —[DEATH_PLACE_OF]→ Hispania'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081897Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q186513'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5e9c40113a8dd7231dea746e1730cbb69d9adfe630ba4e91498b04be0ef8a9cd'})
  SET c.content = 'Publius Cornelius Scipio —[DEATH_PLACE_OF]→ Iberian Peninsula'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081929Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q12837'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0fa001540105b1ef1387001ccb3fb4e1bc7f90af4b99768ac4274dfd2ba402f0'})
  SET c.content = 'Mago —[DEATH_PLACE_OF]→ Mediterranean Sea'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.081976Z'
MERGE (subj:Entity {qid: 'Q335604'})
MERGE (obj:Entity {qid: 'Q4918'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9ba84f3a85bbf76e9d56ffd496b556352d0a02295b86d346a9efba1c567b4084'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus —[DEATH_PLACE_OF]→ Rome'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082008Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q220'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7a88b755790a33d8e45bc569042de2a9066ce0fa63182919de1029880b2da133'})
  SET c.content = 'Andriscus —[DEATH_PLACE_OF]→ Rome'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082039Z'
MERGE (subj:Entity {qid: 'Q362068'})
MERGE (obj:Entity {qid: 'Q220'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '79ccca40d5a1e2bcc9c1197818aa2893a8d61b027039b7c32c5d4985edaf1ae8'})
  SET c.content = 'Ptolemy XIII Theos Philopator —[DEATH_PLACE_OF]→ Nile'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082070Z'
MERGE (subj:Entity {qid: 'Q39938'})
MERGE (obj:Entity {qid: 'Q3392'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f8e6e23cedd186f4520c71ffac2f1921cbe0321b78744dbb0fb5b66c1a1c90d9'})
  SET c.content = 'Arsinoe IV of Egypt —[DEATH_PLACE_OF]→ Ephesus'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082100Z'
MERGE (subj:Entity {qid: 'Q40013'})
MERGE (obj:Entity {qid: 'Q47611'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3cab606d1e16c0650c254d92f0eaa37726a678d06e804e816845ded0a306a679'})
  SET c.content = 'Lucius Afranius —[DEATH_PLACE_OF]→ Thapsus'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082129Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q948682'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '40b364c84f4c5d84ee4a3ff9c6ae3f5706d39e1a58349cee0836207fa9e6f263'})
  SET c.content = 'Quintus Labienus —[DEATH_PLACE_OF]→ Cilicia'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082160Z'
MERGE (subj:Entity {qid: 'Q551516'})
MERGE (obj:Entity {qid: 'Q620864'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3069aa5f0ee76771de781bd2cb10b0bc4f8deba19285630b0ea7d5005706aad8'})
  SET c.content = 'Spartacus —[DEATH_PLACE_OF]→ Lucania'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082189Z'
MERGE (subj:Entity {qid: 'Q83406'})
MERGE (obj:Entity {qid: 'Q1131978'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'af4d9f5ecda60a1843c89f883300950a9211aad0fc2d2003b1e2d508296e8820'})
  SET c.content = 'Marcus Perperna Veiento —[DEATH_PLACE_OF]→ Hispania'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082220Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q186513'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a2c7df77fed44c177fd0f65292775e7833e1f887564d22a58dc37e8dcb8670b0'})
  SET c.content = 'Jugurtha —[MARRIED_INTO]→ Bocchus\' daughter'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082283Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q108954123'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cfdc73c39d65d304acf2de16ca4b876a87786242519dacb22c82706e345ffb8a'})
  SET c.content = 'Gaius Marius —[MARRIED_INTO]→ Julia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082317Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q255870'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4803c5bc91026850f983993ecdf4ccf0c6454c7fe018a20cc9701775064bafde'})
  SET c.content = 'Mithridates VI of Pontus —[MARRIED_INTO]→ Laodice'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082349Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q446544'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fcab2e65a02ce98a42aa99c290cb008274e880ca790da00b84734fb760e3c067'})
  SET c.content = 'Gaius Cassius Longinus —[MARRIED_INTO]→ Junia Tertia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082380Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q442599'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '842c0dbe9179f885d800d362253574ca07f0a0fefc7781d7b564927478d620e4'})
  SET c.content = 'Scipio Africanus —[MARRIED_INTO]→ Aemilia Tertia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082411Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q380862'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'df158f5b8ae032fc3acbe228000f6c6969b7e4b8ef266c60e1ad372b54657157'})
  SET c.content = 'Massinissa —[MARRIED_INTO]→ Sophonisba'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082441Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q241210'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e4096ff411f7d9ec87fab389239c9b81add107e764993f9e0a29ec6db0bf7f36'})
  SET c.content = 'Publius Cornelius Scipio —[MARRIED_INTO]→ Pomponia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082474Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q20499663'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '91e65f95472604c7b142c6c2ab54aaf10c605acbf0b699535af3a503e477cb7c'})
  SET c.content = 'Decimus Junius Brutus Callaicus —[MARRIED_INTO]→ Clodia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082507Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q112085883'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b97733601803bd9abaeb50d68f3afbe840c138434b309fe6ae21514c3780a984'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082540Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e780c58c435c33423daff1193815d1daf1b64eec0f6ea041d0d7138801eded17'})
  SET c.content = 'Pompey is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082570Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd2da4401fa6ee6e31495fbd6be763bdc1fa7def09e30fda34a09cfa96c17a7a0'})
  SET c.content = 'Lucius Decidius Saxa is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082602Z'
MERGE (subj:Entity {qid: 'Q1289301'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '65cfdf72a30f87ab938ed1cb854c21d6d3618afd873e135389eba19b3865d40b'})
  SET c.content = 'Marcus Junius Silanus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082632Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ba8aff377b1ff90733f7abb01add243d5a4aa8f5430a5a069e036df911f6de83'})
  SET c.content = 'Jugurtha is citizen of Kingdom of Numidia'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082662Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q102679'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '04bc5a04120620fbb8a75605976a749a3356aa27a5df069b8d54e2c4ca9e75e5'})
  SET c.content = 'Cato the Elder is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082692Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2ce9f249d1da8bbf35a3ba42ad0cc4bc8b8e5eb22d0d299fe04e6314967ce2a7'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082722Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '04c89596b66ca0a177312bf78218dfe2c3e174f85df7156512345893f13f12bb'})
  SET c.content = 'Quintus Sertorius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082750Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a04448f7190a332ba542a29222a8a65d1ecbf7e1beb2fd5f9e074a4fa40dd1ca'})
  SET c.content = 'Cincinnatus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082778Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b6623430461b5712c69790b1e88da54dc81867c39ef78af44ec60364af5717db'})
  SET c.content = 'Hasdrubal Barca is citizen of Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082809Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5bd95a2353c9f00ee639c23747d8b32fc06d50a1cc324f173d458de4b979c7c8'})
  SET c.content = 'Marcus Claudius Marcellus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082838Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '60da4cb7c7a8325a1882fe495b114d6c3a6bdfa84ef544ccd8081e3af1a3d6cb'})
  SET c.content = 'Quintus Caecilius Metellus Pius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082867Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2925405649867db7a3f7ec6707f4ec38fb9355654ecc259e5789d9959e8ea4a3'})
  SET c.content = 'Massinissa is citizen of Kingdom of Numidia'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082898Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q102679'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '05bb41619b3a94d5f703606f81e9326e0cc8ded427108aaea204794e5aeadcdd'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082931Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0cfe81838b5b18b7d9719a1608e4686c9dc84ec53e7c198545c709fa23f2a9c1'})
  SET c.content = 'Publius Cornelius Scipio is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082961Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '180484cee82ada6bacb17fadc0c46f55789c779088c731a6551eb652489436ca'})
  SET c.content = 'Mago is citizen of Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.082989Z'
MERGE (subj:Entity {qid: 'Q335604'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '02f9592564774b2b4e2e8b4894233c360cda6bac8c8e1d78ae5074d380d245e2'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083020Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5c9327814561b60772af08fe7566e482b8fb679e90332854c9a72534d1f59f38'})
  SET c.content = 'Hannibal is citizen of Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083048Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '02d27f21afb75fb8e42d8fb15f0a08d3ee20ab9ca0d0b63348b396d050fcc6b1'})
  SET c.content = 'Ptolemy XIII Theos Philopator is citizen of Ancient Egypt'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083078Z'
MERGE (subj:Entity {qid: 'Q39938'})
MERGE (obj:Entity {qid: 'Q11768'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8c27715425b65c88b35d07232462e7ef3b634171caeb192fbd3e07e1acdfc553'})
  SET c.content = 'Quintus Labienus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083108Z'
MERGE (subj:Entity {qid: 'Q551516'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b999789cd06840dbb5efe7d06fd8a1eb832ed006042a59aedcf61fd9a3924ec2'})
  SET c.content = 'Lucius Marcius Septimus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083138Z'
MERGE (subj:Entity {qid: 'Q5759209'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '26215126ffe8d3c3b0dd2b3dc7782656a95f59eb33d4b7778c29a7214561f51b'})
  SET c.content = 'Cleopatra is citizen of Ptolemaic Kingdom'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083167Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q2320005'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '428e79dda0c867f2f15fc055211e884d1e49b3e4d5a431a1f9383571229e3173'})
  SET c.content = 'Gaius Aurelius Cotta is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083197Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd4e9042a0af7abac9cd449decd0b4f174ce037e1019081280b689ba0c0199ef0'})
  SET c.content = 'Gaius Laelius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083224Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '28a17f880599d9cb5bbaa0efa5b9571aee3ca75e76a98708f9a45b3815ec6f12'})
  SET c.content = 'Decimus Junius Brutus Callaicus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083254Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1f4ef988c937e04bc7099ec87bfd597e40c4bd81783ccc374ec652afd2a3f3d5'})
  SET c.content = 'Marcus Perperna Veiento is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083283Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '83ffdb29c7cb1f500f04eee65439cbf32b525eb60cf45580971b1e621bf25054'})
  SET c.content = 'Caesar\'s Civil War —[LOCATION_OF_EVENT]→ Hispania'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083313Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q186513'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5af277d7e4212bba7d85bb39b8a3ad4f3c6537873265bd71d662b1accb123b4'})
  SET c.content = 'Battle of Plaisance —[LOCATION_OF_EVENT]→ Piacenza'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083342Z'
MERGE (subj:Entity {qid: 'Q124714225'})
MERGE (obj:Entity {qid: 'Q13329'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a6e40edcef59ab01c21ed686321f371fd0561b83fde4602507c4d4b0a47e7ff4'})
  SET c.content = 'Battle of the Axona —[LOCATION_OF_EVENT]→ Aisne'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083374Z'
MERGE (subj:Entity {qid: 'Q1260622'})
MERGE (obj:Entity {qid: 'Q3093'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c5e6d48b5878629857cf5bc596159e4dd7775939adcc5132df0435df98ee7bc4'})
  SET c.content = 'Battle of Halys —[LOCATION_OF_EVENT]→ Kızılırmak River'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083405Z'
MERGE (subj:Entity {qid: 'Q17277303'})
MERGE (obj:Entity {qid: 'Q257785'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b6c0eb036269e977d524a65a62de40e0ebbf1a84289a914b103b78b7355ca66b'})
  SET c.content = 'Battle of the Nile —[LOCATION_OF_EVENT]→ Nile Delta'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083434Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q179528'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2c77d4c575bb0651fd0a94e2c5bec9adb84f8f1f938b40037252881231d7e6bc'})
  SET c.content = 'Battle of Chalcedon —[LOCATION_OF_EVENT]→ Chalcedon'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083464Z'
MERGE (subj:Entity {qid: 'Q2331925'})
MERGE (obj:Entity {qid: 'Q337381'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bb4c673d9c031c6b7e0019e0f61cc5f5e22ad376f6ed876a8a83af0b2131a513'})
  SET c.content = 'Battle of Nola —[LOCATION_OF_EVENT]→ Nola'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083494Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q72288'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd062646e0288b6b228a9a56d08d8e4d99f01a9d1bfb7a3b00e9f0edbbf75696d'})
  SET c.content = 'Ambiorix\'s Revolt —[LOCATION_OF_EVENT]→ Tongeren'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083524Z'
MERGE (subj:Entity {qid: 'Q2505574'})
MERGE (obj:Entity {qid: 'Q190113'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9818d3427140d73451c78e040ac746b6551b4df9196fe2a5287750dce38f0484'})
  SET c.content = 'Battle of Mount Algidus —[LOCATION_OF_EVENT]→ Mount Algidus'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083556Z'
MERGE (subj:Entity {qid: 'Q2705449'})
MERGE (obj:Entity {qid: 'Q989650'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2808862db93112a18ee599b1cde6b8e3a1a7a029b19bec77ec0c02f46c1ca9c7'})
  SET c.content = 'Battle of the Lycus —[LOCATION_OF_EVENT]→ Kelkit Brook'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083585Z'
MERGE (subj:Entity {qid: 'Q2707112'})
MERGE (obj:Entity {qid: 'Q3045328'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1f6539ff1630c462e58bf35e20868f172197891f926622494d117d158009e167'})
  SET c.content = 'Social War of 91-87 BCE —[LOCATION_OF_EVENT]→ Italy'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083616Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q38'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ba9a5069908e31e77806521346b1a4d883efa80a2c61189b6e203247d715fad4'})
  SET c.content = 'Macedonian Wars —[LOCATION_OF_EVENT]→ Macedonia'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083644Z'
MERGE (subj:Entity {qid: 'Q75813'})
MERGE (obj:Entity {qid: 'Q83958'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '42c1126f114a6db43f56082125769e71aac9b8170f8875e96df9c99ab0c9885e'})
  SET c.content = 'Julius Caesar is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083677Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7768744cec951f6ebd61b5d819f3a1219e73b2cd56050196c983e23011fb7fa9'})
  SET c.content = 'Battle of Numistro is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083709Z'
MERGE (subj:Entity {qid: 'Q1184835'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '42a6262775a8d506717a47f00d0773d428f90275f2754393bec7247c2ebed0de'})
  SET c.content = 'Quintus Calidius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083741Z'
MERGE (subj:Entity {qid: 'Q11944244'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9ed371a5e1ef431b594ac36449e826e18642dfec967d72fe0c92a19ba64300a3'})
  SET c.content = 'Battle of Plaisance is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083773Z'
MERGE (subj:Entity {qid: 'Q124714225'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c8fe32d0952c53bf46ec1b3c32a7aeb4ebeac188d371151816708e7cfd68a94c'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083804Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '528a80f5c92f8cb6d8d3a73529ddd8dcc5c53e6c5b46861708855d8ef1a19264'})
  SET c.content = 'Punic Wars is instance of war'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083836Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q198'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a9c51895db1c89333cf4b6b793f0cf378831bd56feff66fc0a77a2dfb234f447'})
  SET c.content = 'Pompey is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083873Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9164229d965c07249421e4fbc3aecdd6232aac90c2fb1339c2517292ee18d465'})
  SET c.content = 'Battle of the Axona is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083905Z'
MERGE (subj:Entity {qid: 'Q1260622'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1f5249eea2815a91778a6feb8257addcc0d8eda2e930d6f7173fa12112bfbf56'})
  SET c.content = 'Lucius Decidius Saxa is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083933Z'
MERGE (subj:Entity {qid: 'Q1289301'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '45fc954fe0705ee0199f5ee50ff9c5d0b17bcdc7e39dd9162a9d418b97e24ff7'})
  SET c.content = 'Marcus Junius Silanus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.083978Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a62774975aa0681cf7752a49abaa8562d474195de52fc37c8450aa91f3fd5527'})
  SET c.content = 'Jugurtha is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084007Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dea509332a2b6a75b9e5a1f4569e5064376f1410f8d572c58c4b3baf386b05b9'})
  SET c.content = 'Gaius Marius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084036Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5981f6e158e29931691731ab9aaeb791c82eb834049ac9d18f8d68d94a11e5e0'})
  SET c.content = 'Cato the Elder is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084064Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f3ead12724eb412d61ccdd99719b7e3b6ba49d874b6519c01730f2e37b84b9b2'})
  SET c.content = 'Mithridates VI of Pontus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084096Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8599382cc2da9af9cdcc692b7926db1f5c3cdcc06be635109df54eae216f261a'})
  SET c.content = 'Mago the Samnite is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084125Z'
MERGE (subj:Entity {qid: 'Q18668725'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a401631744fb3fc70a0680114a47f3486529aa57334bc4ab5fa772a0a1c52b4a'})
  SET c.content = 'Perseus of Macedon is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084153Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '45f70c4b64eb42f6d39459133620747d9997ed959d76ddb7362c615a64e0f80d'})
  SET c.content = 'Scipio Africanus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084181Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7cc212472793fdbb2f4910924c405437924ec88318047472588b89a8a21a8424'})
  SET c.content = 'Lucullus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084210Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '77b8dd0a7e6b559e0d535635f5e31408294f235dc4b8d0402bc94f2c67c23717'})
  SET c.content = 'Ambiorix\'s Revolt is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084239Z'
MERGE (subj:Entity {qid: 'Q2505574'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '480983608da793791bc0e348f1c5f1fecb47f86a3cd75199e08fc00d82703c79'})
  SET c.content = 'Hanno is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084265Z'
MERGE (subj:Entity {qid: 'Q2525841'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8f444e51e01d6b853ac0edbf1d556bad3533d77851eff0c30b76d235c66022ed'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084296Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c8942e72134c3c55b55ef93642908dc93b861408f99297d21686b49647ba95de'})
  SET c.content = 'Quintus Sertorius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084325Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b66c7c7af5ba36b802e5634ef3ccd5c0263757b7e2c44b7c4d6f97235699170c'})
  SET c.content = 'Cincinnatus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084351Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c47f6ef69e98db02a45b036febd8bd01f5af630c963cecfcd11467c8d068f6a5'})
  SET c.content = 'Hasdrubal Barca is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084381Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f1aa993a1523124d3854ad362f8ed8c126e9b46454e7f4d45714af04779ea9ab'})
  SET c.content = 'Marcus Claudius Marcellus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084407Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2b27ae0fba879ab87a25762b2affa6bc2d4c65bf6100e4dafd429c8c088e6b6a'})
  SET c.content = 'Quintus Caecilius Metellus Pius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084437Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8324aae3981bcdc02c9535908a5c9f97fd11849deb6d25cc99294970cbde7ae8'})
  SET c.content = 'Massinissa is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084463Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '115b802a066e5cef97c59e8b1ef7d78c6ae2b4a2550e27a6a821f49ae0038f3f'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084492Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5393541a4a90f31850fd48e2d9fffa8d6049aa8a2d1733962b8f12e559a1fa73'})
  SET c.content = 'Antipater the Idumaean is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084519Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '949c4423891b729065bbf08e2658c7a370320c401f46d8ef4bf64ded4a1c8612'})
  SET c.content = 'Publius Cornelius Scipio is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084547Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2e4722876c475230ceb141b04482e277e6283f6411492b1bbdc50bc6de712d1f'})
  SET c.content = 'Mago is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084573Z'
MERGE (subj:Entity {qid: 'Q335604'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '49f3e902e8fa2dcf0e66c95132c052f3aee0a9164ff4a94efc3e18bf8825eef6'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084601Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f05d5b5b3bdd41ddd4d5a95bf354abef65bdd80a835a71554423b497ffb49b91'})
  SET c.content = 'Andriscus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084627Z'
MERGE (subj:Entity {qid: 'Q362068'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '68ad9afc83c26580e33e77d6d71cc8c325352682b944ca023c7e4d90cba89590'})
  SET c.content = 'Hannibal is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084656Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '790fa77e7f1118d760fb34451f06d1e99af7dfe3e2a6f2ef44763ed4f738822c'})
  SET c.content = 'Ptolemy XIII Theos Philopator is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084684Z'
MERGE (subj:Entity {qid: 'Q39938'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '94d93e263a0f52e5162b315ed9eab6b1b9f8733c23cff327bc7b1b73f2a85d40'})
  SET c.content = 'Arsinoe IV of Egypt is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084711Z'
MERGE (subj:Entity {qid: 'Q40013'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd4c06e4b0ae6eac44d018fd533195705bff01ec896a3b042d185a0df9497ff2b'})
  SET c.content = 'Hasdrubal Gisco is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084741Z'
MERGE (subj:Entity {qid: 'Q452048'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '522a2de886764c18169245506ddcfc5bb3fb61d985083e08b48dba33c8d1e17b'})
  SET c.content = 'Lucius Afranius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084770Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9ce2cb59e8f6ff88398da90b429d88d188b39e54db95615547366e138c2d627c'})
  SET c.content = 'Quintus Labienus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084800Z'
MERGE (subj:Entity {qid: 'Q551516'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2d768400b4e20254e4310493222259606b2670b9eca3a35eba4933d60a121601'})
  SET c.content = 'Pyrrhic War is instance of war'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084830Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q198'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '27cad45f38ef99e703436d5d3d136a45740844ad2a95a245552e41b5eff97243'})
  SET c.content = 'Caesarus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084860Z'
MERGE (subj:Entity {qid: 'Q60695198'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a7ff2addec2b8afb01f861f7320a45111b7aa600b1c7905b91cd8ebfab205c70'})
  SET c.content = 'Cleopatra is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084893Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '050878e47b81c88c4c3ce423a5e04b8340dda2a26e7d08034c92fc4ed7af63f3'})
  SET c.content = 'Gaius Aurelius Cotta is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084926Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a3b34d463265f0696e04f65b95d0d282992ca8169ffe376e2a6d90261a50e2db'})
  SET c.content = 'Gaius Laelius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084954Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '19496ba4021c09e2df9a9e680b681f04dd270640c9ecf60f5f41899fdeb3a650'})
  SET c.content = 'Decimus Junius Brutus Callaicus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.084984Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1f588fb5dc8a763e1ab2f09a9e3c87e4c9760da7b99c138be8aeabd488d4564f'})
  SET c.content = 'Marcus Aurelius Cotta is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085013Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8f89686bdbddc20f25d74b8f832a03089ac623adb77d480f536d961edaa18367'})
  SET c.content = 'Lucius Cornelius Balbus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085040Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '466de58b88d036027036111d2a02e8eb7eed67e1cb4e614c00fba841c75e35bc'})
  SET c.content = 'Spartacus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085067Z'
MERGE (subj:Entity {qid: 'Q83406'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6ba1206565f49b7e2d9a5c00f883f98cb60248afc3c29c16d44cd8f7423349f7'})
  SET c.content = 'Mithridates I of the Bosporus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085096Z'
MERGE (subj:Entity {qid: 'Q878437'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5791811a53bb0cb3b9c3b123a917e6088d66825544a7fa2a7fd0bb51e3d1304'})
  SET c.content = 'Apellicon of Teos is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085123Z'
MERGE (subj:Entity {qid: 'Q9158420'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e9b47b21d5e55e366d7549697f9d86a5e80fbf81094f767c05ddc0ebc6cdc4f7'})
  SET c.content = 'Marcus Perperna Veiento is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085150Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '24643951c4fd94b187d4f73fc384639054e1b06c34ed5b0714407c18825eb5a3'})
  SET c.content = 'Battle of Numistro is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085181Z'
MERGE (subj:Entity {qid: 'Q1184835'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ebb5c42413f6a849615227a522e4080bd79e9ed64d95f427a70257abf8d33a30'})
  SET c.content = 'Caesar\'s Civil War is part of list of Roman civil wars and revolts'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085218Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q1747183'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '425014fd4afb77d6d77556fa1ef3db751b21f818e85181e2bc7bef22f2433697'})
  SET c.content = 'Battle of the Axona is part of Gallic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085251Z'
MERGE (subj:Entity {qid: 'Q1260622'})
MERGE (obj:Entity {qid: 'Q202161'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '66bba48547ad55ceddfad5e1f8fcb7f2d41b206f4db17dfc5274a1d742265a93'})
  SET c.content = 'Battle of Chalcedon is part of Third Mithridatic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085282Z'
MERGE (subj:Entity {qid: 'Q2331925'})
MERGE (obj:Entity {qid: 'Q1764124'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c9e7d332339947f0011f4ad23e1a08f120c229b6822c261f544bd2724dd32201'})
  SET c.content = 'Ambiorix\'s Revolt is part of Gallic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085312Z'
MERGE (subj:Entity {qid: 'Q2505574'})
MERGE (obj:Entity {qid: 'Q202161'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '060bacb8f46b2f4c1e6c4df8f494cfef1da51d153600596093be73a31179e42e'})
  SET c.content = 'Battle of the Lycus is part of Third Mithridatic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085345Z'
MERGE (subj:Entity {qid: 'Q2707112'})
MERGE (obj:Entity {qid: 'Q1764124'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0ce9c08fb7bb5ebd3e6bb38e3c81671ff7edc2079d4ebb572890028df15236df'})
  SET c.content = 'Gaius Herennius held office tribune of the plebs'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085378Z'
MERGE (subj:Entity {qid: 'Q11923586'})
MERGE (obj:Entity {qid: 'Q11704729'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a42032b2af9e1aef1febdf198fc300b16894b800a7e4b45015a8802346d0357c'})
  SET c.content = 'Indibilis held office king'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085406Z'
MERGE (subj:Entity {qid: 'Q604308'})
MERGE (obj:Entity {qid: 'Q12097'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd874bf5a9e4ebe0c641754213412ca61849875e0fa1802769198b8ae48749c9c'})
  SET c.content = 'Quintus Calidius is parent of Marcus Calidius'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085436Z'
MERGE (subj:Entity {qid: 'Q11944244'})
MERGE (obj:Entity {qid: 'Q4281777'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '469f4dbded33f8209232144990bc7f578f8163078470987d1055fb4605a39cff'})
  SET c.content = 'Marcus Junius Silanus is parent of Marcus Junius Silanus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085469Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q1894209'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '66a6b90e5380b2bebc45cc8c29fa58308632697364a4c95d20ed8e9e7c5aec7e'})
  SET c.content = 'Marcus Junius Silanus is parent of Decimus Junius Silanus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085500Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q102390583'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a19d63b94a16c8e5ee3bbcedcfc3950c7e4ff5eb744249c5c89fa3134002701e'})
  SET c.content = 'Jugurtha is parent of Oxyntas'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085530Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q7116043'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '27ca5a65796503a3a1fe1fc11db542025314dad4f08f4e7b5a5da249aecde5e5'})
  SET c.content = 'Gaius Marius is parent of Gaius Marius the Younger'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085559Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q462978'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f5c64ad350b37fab2df2995435ec145ac916c4a17c142ab817e00d8f011ee89c'})
  SET c.content = 'Mithridates VI of Pontus is parent of Mithridates I of the Bosporus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085593Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q878437'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4bee91db2d15d79a751b40062ee4e8686f403aa7bfae4854850e5e690c7cbf33'})
  SET c.content = 'Mithridates VI of Pontus is parent of Drypetina'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085624Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q5307778'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5d3223ac19f27fe88cc1436f91019a657fccd764b0c7aef166dbb804022c1274'})
  SET c.content = 'Mithridates VI of Pontus is parent of Mithridates of Colchis'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085654Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q11783606'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c018ddf4ded74496ba37c906d8b33c54b15a06d389dd0b18c6262e900a49ef2e'})
  SET c.content = 'Mithridates VI of Pontus is parent of Xiphares'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085694Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q2003480'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7a71e92e8c6b32380b0ffaf5f7d75855f63f0e36d8fc7b7085c8d3e9ca1fee1b'})
  SET c.content = 'Scipio Africanus is parent of Publius Cornelius Scipio'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085729Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q1241388'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9b7b435229326f74685d44d0abd0b8e1312ba4475b68c54f67eefbdd55f2300d'})
  SET c.content = 'Scipio Africanus is parent of Lucius Cornelius Scipio'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085767Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q1680048'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b8ab982b76cd942bdc5c3f48f852eae6e34444f97c10cccb38aa329bb1ea4da7'})
  SET c.content = 'Scipio Africanus is parent of Cornelia'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085797Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q234533'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '44b28f6e668d2b3b7ceb92e593b1df0972eb6b11c7c583b3f4618797f25e038b'})
  SET c.content = 'Scipio Africanus is parent of Gnaeus Cornelius Scipio'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085831Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q11934195'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8c7005053b12358b8dcd03bfa44ce4bf5ae91ba663842957f728a79d587a31ff'})
  SET c.content = 'Scipio Africanus is parent of Cornelia Africana Major'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085863Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q5171151'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '627d38a63d619f9a6f4954eea583c874ad7464fcf2df2bcdf6ae3ee1c5b04781'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus is parent of Quintus Caecilius Metellus Pius'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085900Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q313680'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cc2dc616168d57479c47cc6a44e549cf954a9bcfef7c8ec844362114bcc0a44b'})
  SET c.content = 'Cincinnatus is parent of Lucius Quinctius Cincinnatus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085933Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q1231761'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '05644800dea145fc3da151dc795d6d3e4a14e7a5b10f523eed9b18600ae3817f'})
  SET c.content = 'Cincinnatus is parent of Titus Quinctius Poenus Cincinnatus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085966Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q1230271'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '278b83e0c2dec670c8837dbf87632cf8ad8c44efd6aef93d132db3e4d64ce6f5'})
  SET c.content = 'Cincinnatus is parent of Quintus Quinctius Cincinnatus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.085996Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q680246'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '93a4cd1cb898d2751f4527ea72f64a3412dac6d3031f9ee1c4a72f37757e37c1'})
  SET c.content = 'Cincinnatus is parent of Caeso Quinctius'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086026Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q617349'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '18d872829027691a52d592bdd4f32436bc4e2fcbaf40195f173afe88990540a4'})
  SET c.content = 'Marcus Claudius Marcellus is parent of Marcus Claudius Marcellus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086058Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q709926'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd841cd288ff4546c309905e8d38f788ae173907183f8f7bffae94c5e1db2a7af'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus is parent of Publius Cornelius Scipio Nasica'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086090Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q453860'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '815921451f0666f62e37a646b87ea7a2b3dacc8ae32f63046e7d4d64aadbfa86'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus is parent of Gnaeus Cornelius Scipio Hispallus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086126Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q122321'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5e579dd542360481be20111c9ca6abc84d835f58387efe194de6c1bcac1093f7'})
  SET c.content = 'Publius Cornelius Scipio is parent of Scipio Africanus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086159Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q2253'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c9872b4d3db55296baf6cb731e69a45ca3a8b78189a699c039ab3deeb2e45c97'})
  SET c.content = 'Publius Cornelius Scipio is parent of Lucius Cornelius Scipio Asiaticus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086192Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q361377'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '25f55f3b335cf017ef6b7bcdcb0d7272c82120fbaea351e2c85019bd33fc3f6b'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is parent of Marcus Caecilius Metellus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086228Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q521435'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e8d93b291a7dbf655a090d71a35820c8a4d47afa4566006200f1222a023e4481'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is parent of Lucius Caecilius Metellus Diadematus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086260Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q220978'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '08d449b0682ab2ccace8cc6e2a5bea87d8d0d7ae507855c83b36e6ae340f76ed'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is parent of Caecilia Metella'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086291Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q544816'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '443f8c44acb81e9138699d51a89b44c7d0781d487a39dfceb1e839c5af981a31'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is parent of Quintus Caecilius Metellus Balearicus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086323Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q459870'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c9d9a6844168c7c8a13037e254e6dfb888526994a2867f4363cfc742a3bd35d3'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is parent of Gaius Caecilius Metellus Caprarius'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086356Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q459853'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd0f0a30f6b1074803c4ad49cc1d647ac6601a27505be44a18f5d8f43e25d3fab'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is parent of Caecilia Metella'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086386Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q1025358'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '70776b900840571a4a79fb64ee0b32291bdc737a54e3a3256d3e0d0cd5fb5bd3'})
  SET c.content = 'Hasdrubal Gisco is parent of Sophonisba'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086416Z'
MERGE (subj:Entity {qid: 'Q452048'})
MERGE (obj:Entity {qid: 'Q241210'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e4117ae4aec4758d415e27c7b68cd9533397d189a9a51b5b3550cece004e37bc'})
  SET c.content = 'Lucius Afranius is parent of Lucius Afranius'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086445Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q15671782'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '11a4a1fe1b45b6be4c179c5c822d748ce1e394210bc4aebe00abea0e6023a277'})
  SET c.content = 'Tiberius Sempronius Gracchus is parent of Tiberius Sempronius Gracchus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086480Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q443505'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '76dad950b03491d970a15baf52f0c4966316093097f9150d916727daecff0709'})
  SET c.content = 'Tiberius Sempronius Gracchus is parent of Tiberius Veturius Gracchus Sempronianus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086513Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q20102191'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '34d28f2f63432f2240099978ca569b873d1db2eee8f02b60797a035a1a918802'})
  SET c.content = 'Tiberius Sempronius Gracchus is parent of Tiberius Sempronius Gracchus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086544Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q20101780'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4f63e11ffc4be91608095387299ddd9a956d2b2aca0849e158a32e663759c7d9'})
  SET c.content = 'Gaius Laelius is parent of Gaius Laelius Sapiens'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086573Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q1283514'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0d1c069c0e7c26e74f0d82521ce9326bd8318a0840b727f5106a46ca23a49cbf'})
  SET c.content = 'Decimus Junius Brutus Callaicus is parent of Decimus Junius Brutus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086606Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q1181848'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '76c344812741793ff7c65f63a3028bc516eeb360ca649c521846aea9e4c010be'})
  SET c.content = 'Hasdrubal Barca fought in Battle of Cannae'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086637Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q179591'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3a5af1c61cf93e52e73c25ce34864f2709feb5437dcebb93cce5f1cf08364e73'})
  SET c.content = 'Hasdrubal Barca fought in Battle of Cissa'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086669Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q1500211'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '06ded05e4cd9b80eac24399cb0fd552ce8f8af640a45703458f3ba2e156f67ad'})
  SET c.content = 'Hasdrubal Barca fought in Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086704Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5fb954782b83a07adc0039bff1b10f7f174376de873b36f6e2140bc54c486374'})
  SET c.content = 'Hasdrubal Barca fought in Battle of Baecula'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086739Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q728550'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '11af11d8f23a61bc899290617e15afc755f9e16f0d1101fb614162fcbf8fc160'})
  SET c.content = 'Hasdrubal Barca fought in Battle of the Metaurus'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086772Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q848056'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '019bda9ed847999590298f01520c9420fa45c9e55e55b0b74ab056e975035375'})
  SET c.content = 'Hasdrubal Barca fought in Battle of Ebro River'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086807Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q2286942'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8e0e18608b1a394ea966ebc0474434a1b8ddc3849098dbab821b6dd2aea9027e'})
  SET c.content = 'Hasdrubal Gisco fought in Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086839Z'
MERGE (subj:Entity {qid: 'Q452048'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1c4be03c8d04be9699d3329097397fbc632b085e0fea49edd7a2b8cc983fab8f'})
  SET c.content = 'Punic Wars had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086874Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.69
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e1d8cc40f3cc967523af3026b01e4906a55af6cdc98bf323783c4b03f7ffe795'})
  SET c.content = 'Roman Republic —[DIFFERENT_FROM]→ Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P1889'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086906Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q346629'})
MERGE (subj)-[r:DIFFERENT_FROM]->(obj)
  SET r.confidence = 0.68
  SET r.source_id = 'wikidata:P1889'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '884aa98bc41e291621348078f5dfcbd49d57c8fedf0917b53a7970f093ea1bb0'})
  SET c.content = 'Julius Caesar —[AWARDED_TO]→ Roman triumph'
  SET c.source_id = 'wikidata:Q17167:P166'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086938Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q657438'})
MERGE (subj)-[r:AWARDED_TO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P166'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cb0c37bd6c62dab6cff2a375422b45915b43b6813ea9d95d21b8db176e79741f'})
  SET c.content = 'Julius Caesar —[AWARDED_TO]→ Consecratio'
  SET c.source_id = 'wikidata:Q17167:P166'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.086970Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q106648268'})
MERGE (subj)-[r:AWARDED_TO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P166'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd9afc32c4c6b3ba4a07b1fe69bfa02a4bb9d97221a7d19f11ca22dc58d63a6a6'})
  SET c.content = 'Lucius Mummius Achaicus —[AWARDED_TO]→ Roman triumph'
  SET c.source_id = 'wikidata:Q17167:P166'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087004Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q657438'})
MERGE (subj)-[r:AWARDED_TO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P166'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8d39f22e36622a618998223fb4c69ae3f2d1d300a9ed18490cf229ca6dfb0000'})
  SET c.content = 'Batlle of Emporion was under country Spain'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087038Z'
MERGE (subj:Entity {qid: 'Q11908712'})
MERGE (obj:Entity {qid: 'Q29'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '49df3a018dfbd26923500212c9965b517eeb68156981b6fb326371a320fdeea4'})
  SET c.content = 'Batlle of Emporion was under country Hispania'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087071Z'
MERGE (subj:Entity {qid: 'Q11908712'})
MERGE (obj:Entity {qid: 'Q186513'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1072a67efe4da53d9be348de61ac6ef15131071d23448ad2c8bf2a33110c0fa1'})
  SET c.content = 'Battle of New Carthage was under country Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087105Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e0a0cd070acdebe6a72ba4169529fe8fcbc0426935075ad3d7465f3c6e8e9e16'})
  SET c.content = 'Battle of New Carthage was under country Spain'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087137Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q29'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7320ebe9987abb69d73284da489e88ebbbdd0c93a9a438acc26935192f0db3ec'})
  SET c.content = 'Battle of the Nile was under country Ptolemaic Kingdom'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087169Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q2320005'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd14d0858ffd92d530551bf61d912e0b8b3e5f40468fd6a6cae00beb6e8cccfdc'})
  SET c.content = 'Battle of the Nile was under country Egypt'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087199Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q79'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6b0047567d4b5f0184f956c26d769b9f1960a70e762de8ba020eb1e634f3df7b'})
  SET c.content = 'Battle of Nola was under country Italy'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087230Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q38'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6f8fcd21842de9c9d052ab70d24590c1afefa1448e402705fcb73d19f0b88506'})
  SET c.content = 'Battle of Nola was under country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087262Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd57eb750d942d94ac02ae2b0368de19aa5aebc663c563155b248043f471c4ab3'})
  SET c.content = 'Sertorian War was under country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087295Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '23d14733900916574e51b5983c2115112fe2e5117fe7e2d3a68aabb35f44669c'})
  SET c.content = 'Battle of Apamea was under country Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087328Z'
MERGE (subj:Entity {qid: 'Q9172749'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f49b02c1abc168f0736833199c8c5421f260d201389f0201d3c8d1b2cfe6ca8d'})
  SET c.content = 'Arpino is birthplace of Gaius Marius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087363Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q116440'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5dcc0cd782f7218a67f823b9023022ba778393e43617a7ca2a37ad13c774c2d5'})
  SET c.content = 'Lucullus —[MARRIED_INTO]→ Servilia Minor'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087414Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q2090689'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '89e4d9d61d6bd3c8eae8f775ba44dc964e261dd2cc56c5a4f2ea0a5bfb5ee08a'})
  SET c.content = 'Lucullus —[MARRIED_INTO]→ Clodia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087458Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q16542257'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f17f8be2925789b0944a78a1bdaee76ae8ab1585cff8dfde7d7960df27fd8825'})
  SET c.content = 'Ptolemy XIII Theos Philopator —[MARRIED_INTO]→ Cleopatra'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087493Z'
MERGE (subj:Entity {qid: 'Q39938'})
MERGE (obj:Entity {qid: 'Q635'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0277c263dcce634df9949f49bf9c95f9081bab3b03ccf3fa28e3bd361e3485d5'})
  SET c.content = 'Cleopatra —[MARRIED_INTO]→ Ptolemy XIII Theos Philopator'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087529Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q39938'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '74844424e80af0e45aa3470fc9015aabe63ea2b3bf4521f9c74e459566e5fe2e'})
  SET c.content = 'Cleopatra —[MARRIED_INTO]→ Ptolemy XIV of Egypt'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087562Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q40017'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '34f995dbd5615466f4efb19653714609cf4857f84016626abac2573e4e14b378'})
  SET c.content = 'Cleopatra —[MARRIED_INTO]→ Mark Antony'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087593Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q51673'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'be377bff09d88d32b549de3e1964aa6bbf8377edb0b99ce59f897afe8fdb4b34'})
  SET c.content = 'Battle of Ilipa —[LOCATION_OF_EVENT]→ Ilipa'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087646Z'
MERGE (subj:Entity {qid: 'Q1055755'})
MERGE (obj:Entity {qid: 'Q5998362'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '520cb1193c2003ab8c3427613bd7d1e4694fb43d85f0e95749670fef8717d9ed'})
  SET c.content = 'Battle of the Tagus —[LOCATION_OF_EVENT]→ Tagus River'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087684Z'
MERGE (subj:Entity {qid: 'Q131686739'})
MERGE (obj:Entity {qid: 'Q14294'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '66f4e4c3b2e51eba43c6c4249374da165183cd096a95e7bd61925310e8ea3809'})
  SET c.content = 'Battle of Cissa —[LOCATION_OF_EVENT]→ Kesse'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087716Z'
MERGE (subj:Entity {qid: 'Q1500211'})
MERGE (obj:Entity {qid: 'Q135643324'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cd6371df219621082babdcf2b4cdd9eb594e5daebf854b5fcd094df6c7cbe4cf'})
  SET c.content = 'Battle of Munda —[LOCATION_OF_EVENT]→ Munda'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087751Z'
MERGE (subj:Entity {qid: 'Q18649505'})
MERGE (obj:Entity {qid: 'Q20089083'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2d1c372e754d482e96c7d9798bd3d74d6f0a83e3ca57c8e8353bf701ae54b99e'})
  SET c.content = 'Battle of Chaeronea —[LOCATION_OF_EVENT]→ Chaeronea'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087783Z'
MERGE (subj:Entity {qid: 'Q25414978'})
MERGE (obj:Entity {qid: 'Q13574678'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '519b0f36c666720b33de40b978531b7d6db417b4fc3a3136691a9640fb0e9579'})
  SET c.content = 'Battle of Pydna —[LOCATION_OF_EVENT]→ Pydna'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087818Z'
MERGE (subj:Entity {qid: 'Q2617894'})
MERGE (obj:Entity {qid: 'Q41581937'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9a80a56f96c91e4f271e3f40b1577fb99beeb40498b0797b99c08e70e02c59bd'})
  SET c.content = 'Battle of the Granicus —[LOCATION_OF_EVENT]→ Biga River'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087853Z'
MERGE (subj:Entity {qid: 'Q28665781'})
MERGE (obj:Entity {qid: 'Q1268444'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8482992f067b5cffc9154f9a00dcb6f77977c7e364a7ee5d28115d2fe721096c'})
  SET c.content = 'Battle of Apamea —[LOCATION_OF_EVENT]→ Apamea'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087885Z'
MERGE (subj:Entity {qid: 'Q9172749'})
MERGE (obj:Entity {qid: 'Q617550'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f653726db87338b5103c68b323afe8b1c5b2f64ea38dd1d0b4fc45c96e4b89c1'})
  SET c.content = 'Julius Caesar held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087922Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c135fa31a057eb5c1ac0dde9d6f558b18ee95186f4687b8a78af7581e1d0018e'})
  SET c.content = 'Julius Caesar held office pontifex maximus'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087958Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q212943'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ad1918c8d468a64a63fc5e8fb2d66ad132ce7fe5e7264554acd50a31bcc2f218'})
  SET c.content = 'Julius Caesar held office curule aedile'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.087989Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q5413489'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '62c2a42949ae91425bd8bd19528f2e12498511e56c14685706ed3e34f124feb4'})
  SET c.content = 'Julius Caesar held office Roman dictator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088017Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q236885'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ad8b06e5abc0e391363dbcbc8b1c9223eccb431880845b7e7eab07893ea62ad2'})
  SET c.content = 'Julius Caesar held office quaestor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088047Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q189430'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '269a01168fdb2c53ffced958433af834eb20328584abc77c1eeaebc1fcdfbb9a'})
  SET c.content = 'Julius Caesar held office pontifex'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088076Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q952844'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '023126c8be0319629de701e715bae2b6fd6bcdec261c7cfc8a7dbfc20b141873'})
  SET c.content = 'Julius Caesar held office Flamen Dialis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088229Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q1426927'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '85cd411bc6ffcdd4dc7aa2735af13c44e366fa80652c0526a9227f1de8233d15'})
  SET c.content = 'Julius Caesar held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088348Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cab77ce491770568d327553397f88b8213783a58f7ad538338d3eb6487b55f77'})
  SET c.content = 'Lucius Decidius Saxa held office tribune of the plebs'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088411Z'
MERGE (subj:Entity {qid: 'Q1289301'})
MERGE (obj:Entity {qid: 'Q11704729'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '32c404c848b558c542594a52fc995f5826b8af7a442713063fd909093f50b762'})
  SET c.content = 'Lucius Decidius Saxa held office proconsul de Syrie'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088443Z'
MERGE (subj:Entity {qid: 'Q1289301'})
MERGE (obj:Entity {qid: 'Q133099489'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '10e929e872df127f707bd6b41859030c8acea73f3068e9308e20bf8df5bee33b'})
  SET c.content = 'Gaius Marius held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088473Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6f4e7807a9b1cd4fe2d96c451b3d7a26ca7cca9c7dd51cf81a2ec38fcb4c628a'})
  SET c.content = 'Gaius Marius held office augur'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088531Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q215909'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '07c36ec725434c7b3f71171c856da1f93045c33cdd02c887761c9b9e9da81887'})
  SET c.content = 'Gaius Marius held office quaestor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088593Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q189430'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '530e20b7cc81ee08ecb92ade3100dfda68b716cba0e71e13bae0a8e136f768fc'})
  SET c.content = 'Cato the Elder held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088772Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '25cad146772169b16764722321c0a2838dff1382a6341aac509f146ca9948626'})
  SET c.content = 'Mithridates VI of Pontus held office list of kings of Pontus'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088808Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q890038'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b81e6100fb8dff53f4d374cb7b89b8ce1b78e42735c98c38d23f1a780156ccc8'})
  SET c.content = 'Gaius Afranius Stellio held office triumvir coloniis deducendis'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088841Z'
MERGE (subj:Entity {qid: 'Q20002133'})
MERGE (obj:Entity {qid: 'Q98108218'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9d09ed075662fd0316b640e73d10d6d20066a2916b9d21fe3b3222a4874031f2'})
  SET c.content = 'Perseus of Macedon held office king of Macedonia'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088872Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q622602'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a8a1483589eb36b4560656e1711ab831e2fd838005e1853b5ad1e315cfea7c7e'})
  SET c.content = 'Gaius Cassius Longinus held office quaestor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088900Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q189430'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b8d985586de936c0f06d6d0a218242f626f04dab054af8e57c5434a5fec5cffc'})
  SET c.content = 'Gaius Cassius Longinus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088930Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '68a253e495888cb1f437caed9169e0c6c771df7a882bc0942b59d7063cab6422'})
  SET c.content = 'Gaius Cassius Longinus held office tribune of the plebs'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.088961Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q11704729'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8d4b86a4e12f5111299c5042a5c79798bb46639637a3768f580a3f6b4bf0f127'})
  SET c.content = 'Tiberius Sempronius Longus held office legatus'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089017Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q212624'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f3709e00bf01fd7c2d5c40b92836f17689c0cbd4226c392e9dcb08d066d05d9e'})
  SET c.content = 'Arsinoe IV of Egypt held office monarch'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089046Z'
MERGE (subj:Entity {qid: 'Q40013'})
MERGE (obj:Entity {qid: 'Q116'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4048ffc730b37986503a95d91cd02395e3a3ae66eb85e989d78910aee5654c2f'})
  SET c.content = 'Lucius Mummius Achaicus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089075Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5bbbb35ae40c866a5a5aec3aa0f8c0f49f5da7ea5abc982e979afc9f29b22521'})
  SET c.content = 'Lucius Mummius Achaicus held office proconsul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089105Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q2912782'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '89cd23784d7165146af9770569b1587ff01b1301410e6a0035c1ebdaa5d6f6e3'})
  SET c.content = 'Lucius Mummius Achaicus held office Propraetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089134Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q12799592'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e50c4d3aa12505552361abb87d92c510c11fc31a3cd9e8a00002769c5150c20f'})
  SET c.content = 'Lucius Mummius Achaicus held office Roman censor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089169Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q189851'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2b5ab16155ca0174a7e305fef1db6e78013b02ce8165e167d0e17f88774bedfa'})
  SET c.content = 'Lucius Afranius held office proconsul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089202Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q2912782'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9b79fe3850b26050d81f0ec266982c466459536ca32885f60e978eaf83a00daf'})
  SET c.content = 'Tiberius Sempronius Gracchus held office magister equitum'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089234Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q109960'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'de3b9d7aa32ade72efc4961fdf96596cc41e75c5045c9d9442827df2061db007'})
  SET c.content = 'Tiberius Sempronius Gracchus held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089266Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e1662d7b4450b55bc8f94227399a1a76cec0108aef58450cc75d59e06632bd16'})
  SET c.content = 'Tiberius Sempronius Gracchus held office curule aedile'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089296Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q5413489'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c31fa5695a5fb4bc9832914431af168f6ef4400325d595d373d74f2ceddeece1'})
  SET c.content = 'Lucius Cornelius Balbus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089393Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4a0903d2f5e6131f2adb3316fd94f230f3bc19c26c4376bbb897f4f3706c1a95'})
  SET c.content = 'Pompey is parent of Pompeia Magna'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089425Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q442503'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '484969eb4e5228dfe20ac3a2db79cc2191eb063b8148f1fc6a2f61bbbcb8db54'})
  SET c.content = 'Pompey is parent of Pompeia'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089455Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q55832253'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd5ad2f25ba5b0c8149894cd4a3cd6d717d371a5b574771abda03c69e0b8b9d47'})
  SET c.content = 'Mithridates VI of Pontus is parent of Orsabaris'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089486Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q7104122'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3a772d2bd65550b3bb258ae4b010cfcf18c90a06c6e80144295b9023747970b8'})
  SET c.content = 'Perseus of Macedon is parent of Philippus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089517Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q4357331'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '83c904137f48bc3c8547f391b7ee9eb54fcf7305a2d1d3215c141327f5123f46'})
  SET c.content = 'Lucullus is parent of Licinia'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089548Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q113376428'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '96adbd21a6f0d4650968590e35bdf44e1cf0dd2b9219ec40491dd00329a9ea4d'})
  SET c.content = 'Tiberius Sempronius Longus is parent of Publius Sempronius Longus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089581Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q11943276'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ad0af0ea0ee2d483af366c38924e54b42209964fee30b5543ddf2cb610929ae4'})
  SET c.content = 'Cleopatra is parent of Ptolemy Philadelphus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089610Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q350246'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4c4f1e0a1c0d9cf24ba35232417913975733708f4d3e325cd006c58e5abfff3f'})
  SET c.content = 'Gaius Marius —[HAS_MEMBER]→ populares'
  SET c.source_id = 'wikidata:Q17167:P463'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089641Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q271108'})
MERGE (subj)-[r:HAS_MEMBER]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P463'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'df5d9a03ec64b0192faef5237de3e0d0ba115ce8c496ec195a0415f2611cda44'})
  SET c.content = 'Punic Wars —[CONTAINS_PERIOD]→ Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089673Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aaa1d46f434961351bec02aa771e63026fa65dfcdcacae79d5d7ecb88841a3a7'})
  SET c.content = 'Punic Wars —[CONTAINS_PERIOD]→ Third Punic War'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089705Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q6334'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f43e68d480bff45ed17ea661cb72a71fd74850462d17d8f08ef943727ea698ae'})
  SET c.content = 'Punic Wars —[CONTAINS_PERIOD]→ First Punic War'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089735Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q6286'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9bd65b6aea1cdddc8973b43d87249af850079ff05c1646bab78c73e08c018d0a'})
  SET c.content = 'Pyrrhic War —[CONTAINS_PERIOD]→ The scene of the Apennine Peninsula in the Pyrrhic War'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089774Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q129059100'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '52d8442dd81edf4ec44c3b6ab174b1dfd89bfe724e5ca0cbc2013b2029cb769c'})
  SET c.content = 'Pyrrhic War —[CONTAINS_PERIOD]→ Pyrrhus\' campaign in Sicily'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089809Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q5742664'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0d9d120dd136283aa862f1c8b21fcd18c98b9d93f50e6d95df39fa9a24bd63b4'})
  SET c.content = 'Social War of 91-87 BCE —[CONTAINS_PERIOD]→ Battle of Canusium'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089846Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q85745822'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3796a07da5cb6a276a6710c4a39b0edbba145b04c0777cdabc2674a2e5a3f4c1'})
  SET c.content = 'Social War of 91-87 BCE —[CONTAINS_PERIOD]→ Battle of Acerrae'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089883Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q85745805'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '72368a61e39f2e7923488970f1c07ec750224c228a15a1c8e96230f0bdb8c696'})
  SET c.content = 'Battle of Ilipa had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089919Z'
MERGE (subj:Entity {qid: 'Q1055755'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b7776e0bfb0c74e4c897751b46a931e09bbf52f14d9831e2a7a3464998b8997f'})
  SET c.content = 'Battle of Ilipa had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089952Z'
MERGE (subj:Entity {qid: 'Q1055755'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8dec4e927823079a5ab23e551b5bdf138a654e72c99ae6914044cbd89331b5e3'})
  SET c.content = 'Siege of Antioch had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.089982Z'
MERGE (subj:Entity {qid: 'Q109377210'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '17c70942c6726792c7f3f3fb9957d6ba533bdfa4bea8f72c853e8f1533346f83'})
  SET c.content = 'Siege of Antioch had participant Parthian Empire'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090013Z'
MERGE (subj:Entity {qid: 'Q109377210'})
MERGE (obj:Entity {qid: 'Q1986139'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '487edaec7f14f9b017595dcc5f79cedca99d608c7ff9ed186feaf583bfa48382'})
  SET c.content = 'Battle of Numistro had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090044Z'
MERGE (subj:Entity {qid: 'Q1184835'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fbdb0b3c687bd40313bcb569ba5215fd7bbe7f4ab4f9fcf02e6fc9b967ac1d41'})
  SET c.content = 'Battle of Numistro had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090075Z'
MERGE (subj:Entity {qid: 'Q1184835'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '51a3e5ceb5201ce4f904403b649e7f13817dc1f9abc49eb4c79a6fb72db016b8'})
  SET c.content = 'Batlle of Emporion had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090104Z'
MERGE (subj:Entity {qid: 'Q11908712'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd144fd042ffd89ca85a4998f6689937c7367e89a8cdc373afd418ca2d2221044'})
  SET c.content = 'Battle of Rhode had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090134Z'
MERGE (subj:Entity {qid: 'Q11908765'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1544e93495731bccd2482153fe9e5a8ca23f277714b1dccb630e52cf7cbb91b4'})
  SET c.content = 'Battle of Plaisance had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090162Z'
MERGE (subj:Entity {qid: 'Q124714225'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fa725b3d043c2720286944ecf064e2b2a533b54f079d7a73851c065beb892ea8'})
  SET c.content = 'Battle of Plaisance had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090192Z'
MERGE (subj:Entity {qid: 'Q124714225'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '16c5a92a25dee74bc1ea4631fe234c41e2caa4371a254407bd69e2b6f89bf361'})
  SET c.content = 'Battle of Delos had participant Classical Athens'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090220Z'
MERGE (subj:Entity {qid: 'Q130857859'})
MERGE (obj:Entity {qid: 'Q844930'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a54c156094ac371c644ec432b8b21799942d57f57fd805ae89eeab11a5ea9210'})
  SET c.content = 'Battle of the Tagus had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090251Z'
MERGE (subj:Entity {qid: 'Q131686739'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '97efedc4588cc2a9e9b8a2182daf409639a619eedc77b91b457007200c475d4e'})
  SET c.content = 'Battle of the Tagus had participant Lusitanians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090282Z'
MERGE (subj:Entity {qid: 'Q131686739'})
MERGE (obj:Entity {qid: 'Q837549'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bb7ad9a301d4aad7d2ea9c7e04bb109276ec1a7f3ce20313b3cf2bb1c1dde753'})
  SET c.content = 'Battle of Uskana had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090313Z'
MERGE (subj:Entity {qid: 'Q133480177'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4ead78cdb028c73fed72170de2e1ac1c0763a55d954c48fc0c5dcdecb6e254de'})
  SET c.content = 'Battle of Uskana had participant Macedonia'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090343Z'
MERGE (subj:Entity {qid: 'Q133480177'})
MERGE (obj:Entity {qid: 'Q83958'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '333be484bc1ef5b847cca95704e01548a88005ae7e2178ad84bb5117d41c58b2'})
  SET c.content = 'Battle of Cissa had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090372Z'
MERGE (subj:Entity {qid: 'Q1500211'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4bf89477fc8d3da4d18890dc2876c04816a016895b1ab35ecd5c35055b70d783'})
  SET c.content = 'Battle of Cissa had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090402Z'
MERGE (subj:Entity {qid: 'Q1500211'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '756b9979c245e45ce151737b2a111e7f85ea0e18032fd0655211a078adde612e'})
  SET c.content = 'Battle of Cissa had participant Ilergetes'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090433Z'
MERGE (subj:Entity {qid: 'Q1500211'})
MERGE (obj:Entity {qid: 'Q510579'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '190fb69efce8bde9ba33c94c8fd09d17141a95c984adbae3166ad4e024e30624'})
  SET c.content = 'Battle of New Carthage had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090462Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4a65453dc8b4942b2ead21a32bab8805037f1df0f12c368b9eebb49cf2246e27'})
  SET c.content = 'Battle of New Carthage had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090491Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd0c097eded0a861a2d17508bdb228d6bf3c88a650f373a039a16a8ccd0590722'})
  SET c.content = 'Battle of Orongis had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090520Z'
MERGE (subj:Entity {qid: 'Q18649467'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9b520f00fac004e489643cf23a85c01f1bb29ac7f2345a075bf4661300418b46'})
  SET c.content = 'Battle of Orongis had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090551Z'
MERGE (subj:Entity {qid: 'Q18649467'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '98919ac7fe3897649f4dec6d279e0565e79e1f12c118cd772fee1342a7d90b25'})
  SET c.content = 'Battle of Munda had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090580Z'
MERGE (subj:Entity {qid: 'Q18649505'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '561d50b08cc240769f43c9b9f9b2d81083db556efe20baae00d8bd4c4f902cde'})
  SET c.content = 'Battle of Munda had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090608Z'
MERGE (subj:Entity {qid: 'Q18649505'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd61485e71d2fad5005e628d78c7fbf963c34a23cc3c9c8c72bdc8739b1d41b8e'})
  SET c.content = 'Battle of Campi Veteres had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090639Z'
MERGE (subj:Entity {qid: 'Q18667552'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0d875b2902be793d699fedd361a28178d308d7c286a2dab3797af67f29caa919'})
  SET c.content = 'Battle of Campi Veteres had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090672Z'
MERGE (subj:Entity {qid: 'Q18667552'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2e91c623953d13b09348fa3608c543f7f3d7a3fab814131f49e0106ae94af47d'})
  SET c.content = 'Battle of the Nile had participant Pergamon'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090702Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q18986'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4cb3761506125eb0286d362d79094e49755064c0a4f44240067352149b63768c'})
  SET c.content = 'Battle of the Nile had participant Ptolemaic Kingdom'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090731Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q2320005'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7abae6683f40c6c1a2978971e3504610864d81cc2d30538e74c8a1dc95c005a0'})
  SET c.content = 'Battle of the Nile had participant Hasmonean Judea'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090763Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q10359001'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5c5035d4be7d5f49a52b917e4a6e47d448661159816c9c7266f30c43b6c4f005'})
  SET c.content = 'Battle of the Nile had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090794Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'efa86132b096568753bc36d1b00f50562221721a7a9869adad641938b4234d72'})
  SET c.content = 'Gallic War had participant Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090853Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '31d6633b23363e1f662436d45378a2ac3ada66b215e5681e2ff09754c507a936'})
  SET c.content = 'Battle of Chalcedon had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090884Z'
MERGE (subj:Entity {qid: 'Q2331925'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2999224c92aff5dd9733afeeedd0f73dadac38b5e021d082ada5f36ad0645485'})
  SET c.content = 'Battle of Chalcedon had participant Kingdom of Pontus'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090920Z'
MERGE (subj:Entity {qid: 'Q2331925'})
MERGE (obj:Entity {qid: 'Q7380487'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '223c279133f60cd72a6245c835832525d7c46bf0032844ada2dd2ef53c10c087'})
  SET c.content = 'Battle of Nola had participant Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090954Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '073e005890b062654eb416fe02587288cf35c0f9dc389c0347e7382759c46b48'})
  SET c.content = 'Battle of Nola had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.090986Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6497561616ce7da8257b25d31b249eca9d40df55177c9d9e91457fe0126b4cbc'})
  SET c.content = 'Battle of Petilia had participant slave'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091019Z'
MERGE (subj:Entity {qid: 'Q24045885'})
MERGE (obj:Entity {qid: 'Q12773225'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ecb3e79689b60977b36a82e7c3e597e4d750fe13526460f0208257b1bfa089b0'})
  SET c.content = 'Ambiorix\'s Revolt had participant Eburones'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091048Z'
MERGE (subj:Entity {qid: 'Q2505574'})
MERGE (obj:Entity {qid: 'Q323500'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9905f7a7ea6477b12777ac8ad5c3e1d9468f47ff6a065518e54d6fa2e5369bab'})
  SET c.content = 'Battle of Chaeronea had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091077Z'
MERGE (subj:Entity {qid: 'Q25414978'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '87c066ad60f5f5698a5a9605ffb1fbe119222d2a0bfe8245a9061bf6e2b3366e'})
  SET c.content = 'Battle of the Douro had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091110Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9a280797476edafde1c2765b2c55f4a41ed300a34c76b3299815e85533744305'})
  SET c.content = 'Battle of Pydna had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091141Z'
MERGE (subj:Entity {qid: 'Q2617894'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd859f40c5a3f92e4e2094c2f451507bac1a225001b8eee41f4e8eb6beebc1849'})
  SET c.content = 'Battle of Pydna had participant Macedonia'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091172Z'
MERGE (subj:Entity {qid: 'Q2617894'})
MERGE (obj:Entity {qid: 'Q83958'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '53b5d5f79ccae81e0e85c0029aa2ed09585744a70ddc8d3b4e7edf461b25f0ca'})
  SET c.content = 'Battle of Mount Algidus had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091202Z'
MERGE (subj:Entity {qid: 'Q2705449'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4381de9987350824c92d57af411ec2466904488bce280dbccf22fa997193da46'})
  SET c.content = 'Battle of Mount Algidus had participant Aequi'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091233Z'
MERGE (subj:Entity {qid: 'Q2705449'})
MERGE (obj:Entity {qid: 'Q381053'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7d52272748a56078a4f9190f60dd1d8719b91d5f3c76dc7fe56139fdbb19fca4'})
  SET c.content = 'Battle of the Lycus had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091263Z'
MERGE (subj:Entity {qid: 'Q2707112'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3e083db6aa25c130a5a640411fb706ed846b46f46aec90f825469632fd56f530'})
  SET c.content = 'Battle of the Lycus had participant Kingdom of Pontus'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091294Z'
MERGE (subj:Entity {qid: 'Q2707112'})
MERGE (obj:Entity {qid: 'Q7380487'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '37b62b7140d5c9cbc43f66517856d1e08a7de84e0d89e1695368d58ea0f35e51'})
  SET c.content = 'Battle of the Granicus had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091323Z'
MERGE (subj:Entity {qid: 'Q28665781'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c82dc082012fac860092224878c1116c58400fc38efc37ada57c082b954671e1'})
  SET c.content = 'Battle of Zama had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091353Z'
MERGE (subj:Entity {qid: 'Q2890429'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '46624f4caed7301c4e2c3ba397158864bdc3b13c6fc3ac8747086d04d1b5365a'})
  SET c.content = 'Battle of Zama had participant Kingdom of Numidia'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091386Z'
MERGE (subj:Entity {qid: 'Q2890429'})
MERGE (obj:Entity {qid: 'Q102679'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '67b4dc011c6d7e59f6b2b82f00a0d5f95afa0317883435130e9c353c102dcb8d'})
  SET c.content = 'Sertorian War had participant optimates'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091415Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q309155'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '81e82c2f21a245fdf258de3530dc39df5f57e7c284e808294117309a9bd3c816'})
  SET c.content = 'Sertorian War had participant populares'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091444Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q271108'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f7dd97ddbdffbbb035096dd9f242e6e0e1a69832783e0739f22f3c7783b6413e'})
  SET c.content = 'Battle of Apamea had participant Parthian Empire'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091473Z'
MERGE (subj:Entity {qid: 'Q9172749'})
MERGE (obj:Entity {qid: 'Q1986139'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cacda6ac0e11ee1791e99b91f218905747d7469a3055cfce176273f9502c90e1'})
  SET c.content = 'Battle of Apamea had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091505Z'
MERGE (subj:Entity {qid: 'Q9172749'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.64
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1c668ce3a153d0fa6cb3941535bdb016d9e583d26d06d596954b977d574aca11'})
  SET c.content = 'Roman Republic —[LOCATED_IN_CONTINENT]→ Europe'
  SET c.source_id = 'wikidata:Q17167:P30'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091543Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q46'})
MERGE (subj)-[r:LOCATED_IN_CONTINENT]->(obj)
  SET r.confidence = 0.63
  SET r.source_id = 'wikidata:P30'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '034c39732266cd9c70eeedd43d1dce76c60ae5b56ef05829dab72eed9b6273c3'})
  SET c.content = 'Roman Republic is instance of historical country'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091574Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q3024240'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.63
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f9648940d0c1fd4db3c7e0fecc3d4d3a78288fadfb08b50941966022db8f4213'})
  SET c.content = 'Quintus Sertorius —[DEATH_PLACE_OF]→ Osca'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091605Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q100707898'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.59
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e66d64b8012a9e86acbc49b4bb98e71c52ed335d4d6d84db3ca64e8394fac765'})
  SET c.content = 'Punic Wars is instance of series of wars'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091635Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q104212151'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.59
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3a5c93fb09df891a5725bff33ac10d64291a3ca047c40e24cebd5e17f625fcd2'})
  SET c.content = 'Pyrrhic War is instance of series of wars'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091663Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q104212151'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.59
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2e88eba7cf00c8ba3ce065b56caf6bfa7fb8032af9161b53315b72ac9c8132f0'})
  SET c.content = 'Roman Republic —[SUCCESSOR_OF]→ Roman Kingdom'
  SET c.source_id = 'wikidata:Q17167:P1365'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091692Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q201038'})
MERGE (subj)-[r:SUCCESSOR_OF]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P1365'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5d67f064fc43044452c70343e5c7bcec877bd1963c8dc383588414723e0b283e'})
  SET c.content = 'Roman Republic —[REPLACED_BY]→ Principate'
  SET c.source_id = 'wikidata:Q17167:P1366'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091723Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q206414'})
MERGE (subj)-[r:REPLACED_BY]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P1366'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '19934ee0b8c99c5e06f71b4438bff86ccd40eba8c7b52337a27af5a1947bd532'})
  SET c.content = 'Roman Republic —[REPLACED_BY]→ Roman Empire'
  SET c.source_id = 'wikidata:Q17167:P1366'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091756Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q2277'})
MERGE (subj)-[r:REPLACED_BY]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P1366'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4c538bbec1a753811b3e82311ceec9581d6f1a0e866d8aa5d3b64fc595ed1bd6'})
  SET c.content = 'Roman Republic —[LOCATED_IN_CONTINENT]→ Africa'
  SET c.source_id = 'wikidata:Q17167:P30'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091798Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q15'})
MERGE (subj)-[r:LOCATED_IN_CONTINENT]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P30'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a81b3bf9b873ee98a87bbf27bad58f5de5b62a3cb6bc16b670ffd1da4b4a7688'})
  SET c.content = 'Roman Republic —[LOCATED_IN_CONTINENT]→ Asia'
  SET c.source_id = 'wikidata:Q17167:P30'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091829Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q48'})
MERGE (subj)-[r:LOCATED_IN_CONTINENT]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P30'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dea0bdf5c4e0c8c1d0bda1fcb1a317738015d075e399f85deb86486337c90917'})
  SET c.content = 'Roman Republic is instance of form of government'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091863Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q1307214'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '190914a394f9443c6e49b9a85a9b6e760b05f136471ff1e5a1a3e6592e46f3a7'})
  SET c.content = 'Roman Republic is instance of empire'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091893Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q48349'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6bdb77abe6f0aa8b315f0f3c19110f3de0651f0c0da35fb76d8a49cf68323fad'})
  SET c.content = 'Roman Republic is part of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091928Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f5f77494bab6ae0ca2f97adfa18da5b3f9534053a05c6d15574a746b2c1a9679'})
  SET c.content = 'Roman Republic —[OFFICIAL_LANGUAGE]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P37'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091961Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:OFFICIAL_LANGUAGE]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P37'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6698ccdddb4ab7b162263fade6af42f102140efd9e1c46a5684d6ae4b67a437f'})
  SET c.content = 'Roman Republic —[CONTAINS_PERIOD]→ Early Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.091999Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q2839628'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5d93b7868872a99db7d0abc4483d87511602e70ed8693a01b9159a30e6de52cd'})
  SET c.content = 'Roman Republic —[CONTAINS_PERIOD]→ Late Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092034Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q2815472'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4d74944559c3fd31659d1150ccde782b6f7b558c7b3f154e308e8447d2578808'})
  SET c.content = 'Roman Republic —[CONTAINS_PERIOD]→ Middle Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092065Z'
MERGE (subj:Entity {qid: 'Q17167'})
MERGE (obj:Entity {qid: 'Q6106068'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.58
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '16743701e41c41dbe12ad02e6017bff94117f76c5be08682862701ffa936a945'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ ancient Roman priest'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092107Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q3409374'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e26889cd63ed12bd7193647ca10e52c07993cd8082811253fd6e212920d1a8ab'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ memoirist'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092138Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q11774156'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1aed6c156cd24fdcf21d34be16571c2b3d89cee483e5918c953df3b9b0dcc22b'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092168Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd7d93c2ca8492e179ec52f5ff4d9ab3def88d10c0181fe21effffff8493e049f'})
  SET c.content = 'Julius Caesar —[OCCUPATION_OF]→ orator'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092200Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q12859263'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ddbe77b8f0a661399c7bc93d3ad6cff2c6143fac01032b31e7a570526922e978'})
  SET c.content = 'Cloelius Gracchus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092231Z'
MERGE (subj:Entity {qid: 'Q11914149'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '00542d654446c74fbfced233a5908b77a486290018e7480e8e186a5aafb5aeef'})
  SET c.content = 'Lucius Fufidius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092263Z'
MERGE (subj:Entity {qid: 'Q11923219'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '54ce73fa877ebcd17cd64f313c782ec1df455a95f1685bfa52231ec23f96364a'})
  SET c.content = 'Lucius Fufidius —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092294Z'
MERGE (subj:Entity {qid: 'Q11923219'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9a472adf9b2b57b85f59a0721d3b759623dc3e52e3b210297b3a3a7a116ab3cf'})
  SET c.content = 'Gaius Herennius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092326Z'
MERGE (subj:Entity {qid: 'Q11923586'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0c820b81c4e1264fa7018902cc154d2755ced7122bc713e0c2c2656b3b98f64f'})
  SET c.content = 'Gaius Memmius —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092358Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cdad0bcb28df5a2575844b47280facfd7fa74892ab0136ba76b80dcdf7ac6500'})
  SET c.content = 'Quintus Calidius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092390Z'
MERGE (subj:Entity {qid: 'Q11944244'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9cbbd6980c13a43f87f6eba00fb8895f1f24b15978869038ebfc94cf36a37399'})
  SET c.content = 'Gaius Tarquitius Priscus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092423Z'
MERGE (subj:Entity {qid: 'Q11950924'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f8a83a5f6d1dab2f52246c76574d8dffa99872aa662dca452613731484cb437c'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092457Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'eb427c500ce4856989756e169a5b064036f9b1372c8bd04de8e576d22db1e59f'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092489Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f048da56c739f56264af50d5314de27c5371b8fbc8c2827b1c8ef087dd1ea43c'})
  SET c.content = 'Pompey —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092519Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f07dfc644c0a3661924ddca90d0d43955ba5aca9ebaad73cbf0a455d730686d9'})
  SET c.content = 'Lucius Decidius Saxa —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092549Z'
MERGE (subj:Entity {qid: 'Q1289301'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8bfa3ef6d54b15bf32046ca6c678c6c42486d324a7c8e7c911615c6482db913b'})
  SET c.content = 'Ganymedes —[OCCUPATION_OF]→ eunuch'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092582Z'
MERGE (subj:Entity {qid: 'Q1493701'})
MERGE (obj:Entity {qid: 'Q179294'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '01f1ecb0d4eba07038bbba20621cd3c76b545febd560ac629e9133462f29f839'})
  SET c.content = 'Marcus Junius Silanus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092612Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4c93dba6e758a7b807f752538a37731bf53b46e19536b80158a064d9151a6940'})
  SET c.content = 'Marcus Junius Silanus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092651Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8bfe19f9c5668e4c021a557f6a23f8aa88d7014bd64c41f03fce82387c07c3fe'})
  SET c.content = 'Jugurtha —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092684Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5fb34a8e77920a3ca6385fda920bcb8ba51c32806395155b6291d86065516c24'})
  SET c.content = 'Gaius Marius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092717Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '37ea0a0d185b7f02ef332de0d5d6ca75511a8f7605c9c5d33ff8ef3bf67c94be'})
  SET c.content = 'Gaius Marius —[OCCUPATION_OF]→ ancient Roman priest'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092750Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q3409374'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3fb36f645ebe94035ace538ed4d36a20c42e91f4c3de66d300ae83de16564161'})
  SET c.content = 'Cato the Elder —[OCCUPATION_OF]→ economist'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092782Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q188094'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0536e39b5bdeb7867044695d803274802a373fd404a2389ac9a0a5cad39935b8'})
  SET c.content = 'Gaius Afranius Stellio —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092881Z'
MERGE (subj:Entity {qid: 'Q20002133'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8ec6685d064c8f519ce69bf48c39c12127ff131d23aa30a44d331366a2a157bb'})
  SET c.content = 'Perseus of Macedon —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092948Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6a946b51b30bef5200beb025f845b6e0b0963e6bbf3dc195c1817f30c66e2c6c'})
  SET c.content = 'Gaius Cassius Longinus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.092989Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '67e92f1b2bef6af845d16399aad897bd132bbd5351ee3f31b3569038dff2091e'})
  SET c.content = 'Gaius Cassius Longinus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093023Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6b07c9d0b44619a386bd575a7f247cf9f49b8aa75f84c185f9688559829a2072'})
  SET c.content = 'Scipio Africanus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093056Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8519264bef6bbba18c4be07062263968dfb2ce1e9e09886c13fbb4bcff38e630'})
  SET c.content = 'Lucullus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093087Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '024efe547670b372c7eff173636d97c23f6d47665f22d8acf5b99dfcaf7db0f0'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093123Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f591693533a695d81ce34c6afb9be458e135804a6dec8b3848b582a0326fec87'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093156Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8b5b2930a5e18d46c8c00d7f4f3b40c163198b59ed5bf8fa105228219ec41f27'})
  SET c.content = 'Quintus Sertorius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093186Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '85551ad2c162b1117552458e5e70dadf08b692df2f741c0bad1b5f9969769835'})
  SET c.content = 'Quintus Sertorius —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093217Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '54cf12ed55777085fc70a2d5ff7eb679835e728c6e8f7199a7cb37638574ae8d'})
  SET c.content = 'Cincinnatus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093247Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '31d61cc39d9731f3a7fa602bf73b42902e49c7353ee293ba1411f55ebbb63452'})
  SET c.content = 'Cincinnatus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093275Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2464d1ccb148527ba83ed5a7b7b145823f218225e0abc983a36fac04038e544c'})
  SET c.content = 'Hasdrubal Barca —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093306Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q12090790'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '80909dff59fc3ac38896e6f1cb30bf2ed079aef208e6275e077a612ece92b11b'})
  SET c.content = 'Marcus Claudius Marcellus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093338Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7891a10e47a3fb0915f36929840319f72d2006cec4cdbdc7ddc9aa619a395659'})
  SET c.content = 'Quintus Caecilius Metellus Pius —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093395Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9d9721c3de37b190beedab85b969d5a6d25babfdacc363331df3d06981c1bf83'})
  SET c.content = 'Quintus Caecilius Metellus Pius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093432Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e51d38ccae8a8473db9bf97539c1c73f7d65bf64b46b231724648cd42aa377c8'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093464Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e827296c89874a578b5f46309a09e23c32475546c6645c0f1bc12ecdb1e02292'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093494Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '31c4e2b6eecabb4768acd473f4bed65452398276f6390d8e6d977f800322de96'})
  SET c.content = 'Antipater the Idumaean —[OCCUPATION_OF]→ statesperson'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093527Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q372436'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '69ac24dc4cb992a38d672b89812703ea34e5d437bcb6c4f177eb560816aec165'})
  SET c.content = 'Publius Cornelius Scipio —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093559Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c9c9ac4194c06f10077d210c0383b7394000804f5e04e88f47780cd6669c4dfb'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093590Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bf1111a967a06a23c7f9ba357ea9ff4d71286a6be2f7cb3d7b87921842f1128e'})
  SET c.content = 'Marcus Marius —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093619Z'
MERGE (subj:Entity {qid: 'Q3622239'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5eb447b7318f1b048bee8bf3f2ff382aaea0452bc170edd974611a924997eb6a'})
  SET c.content = 'Marcus Marius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093651Z'
MERGE (subj:Entity {qid: 'Q3622239'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4e3c1f9abfd7c2d94df93a8a0d890590a67209706a71be6c0da39aa6c026f6cd'})
  SET c.content = 'Tiberius Sempronius Longus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093683Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bc71da71d31b744a5a3fe6c0c1ead0995c0b405acfd8536a038f84b4eba6f1e0'})
  SET c.content = 'Tiberius Sempronius Longus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093715Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ab09b52f7e19f65773f16e9411afb574941576d133b1dc8a4dae604861b5ade5'})
  SET c.content = 'Arsinoe IV of Egypt —[OCCUPATION_OF]→ queen regnant'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093747Z'
MERGE (subj:Entity {qid: 'Q40013'})
MERGE (obj:Entity {qid: 'Q19643'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '789251c4ee1f39de8c824598596c296e58053a34217b87230f50f31233ef0853'})
  SET c.content = 'Lucius Mummius Achaicus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093779Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '439c322cf2239658b507fb02a0b218ca94d0645b6bf62ff319ed6c63397faac6'})
  SET c.content = 'Lucius Mummius Achaicus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093808Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0bf60ecb13ffa2267f5d5d5b8b5606e8926b450e747fbef2b0ff7df00bc58ff0'})
  SET c.content = 'Hasdrubal Gisco —[OCCUPATION_OF]→ military officer'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093839Z'
MERGE (subj:Entity {qid: 'Q452048'})
MERGE (obj:Entity {qid: 'Q189290'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bde3b118ac15cbe9d38a0e97af367df1d55902498e3d8e4862284617e29b1df7'})
  SET c.content = 'Lucius Afranius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093869Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6a89b170a742d8d110002947ff79ce22002d811142c1882d56d0e01901191bfa'})
  SET c.content = 'Lucius Afranius —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093899Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2557e9aa8036a03862cfb0f75747b7937c2ec4c8b718bacde419ba36ace8c423'})
  SET c.content = 'Mago —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093929Z'
MERGE (subj:Entity {qid: 'Q5393550'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b98f44a4c4db8c12ee03f11a4e816aee2dcc15d926c147718fbd77a54e619f73'})
  SET c.content = 'Quintus Labienus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093960Z'
MERGE (subj:Entity {qid: 'Q551516'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f1fb97e74569ec036cbf07480e47f3e555aca91eb7e13ba12ce937731d8776d3'})
  SET c.content = 'Gaius Carvilius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.093994Z'
MERGE (subj:Entity {qid: 'Q5517426'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b52a37d8e522fb08aa2fd2dd35666878586641ff305a577b631a4e673d2b32ed'})
  SET c.content = 'Tiberius Sempronius Gracchus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094027Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5f3bf14c9d89e9f2448b083c8d3b364c9e3c7231c36c7f6a56849b0bb9bf7093'})
  SET c.content = 'Tiberius Sempronius Gracchus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094058Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'feb359e8047daa20b03ec5f38071b18e0a8521adb621433b7989d76566a26d1e'})
  SET c.content = 'Lucius Marcius Septimus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094346Z'
MERGE (subj:Entity {qid: 'Q5759209'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd2eb3d14fa698c9d3b8760784c6c21f482b53be4cda5273990bd63a138f3b8b6'})
  SET c.content = 'Gaius Aurelius Cotta —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094481Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '301ab028fdc4ec3de2a12876190861630022af6deccdb1fdf68273a0bfab49ad'})
  SET c.content = 'Gaius Aurelius Cotta —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094550Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cad347b7ff7b055f2879b5493874934981b056fc596a9163314a66c36b8a3350'})
  SET c.content = 'Gaius Laelius —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094589Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ae681301febe2ac303e64661a76370b2a6bd93c051dfa5c1bfc9666dd2c6f888'})
  SET c.content = 'Gaius Laelius —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094625Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cbf4f5097b63812e84448e641b49080d0901fc77619950a96d9e3443977d4b61'})
  SET c.content = 'Decimus Junius Brutus Callaicus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094661Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e1d995ceb9780fa62c1b6ebed19208e2aa16f74682b2d907dd868a697e642ac2'})
  SET c.content = 'Decimus Junius Brutus Callaicus —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094783Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '458ef769b57668da68164316c1a79bfa3e4c4ad7d1242f8e9d27d297b603be60'})
  SET c.content = 'Marcus Aurelius Cotta —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094823Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8fc86364bcc98257507b12fdc3ea340ba42bb8c54fcdd2499fdae68ef21b507f'})
  SET c.content = 'Marcus Aurelius Cotta —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094858Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bdc5d8b31851dc977257867f74658914a393337d8b86b16e9ccd46ea989e6365'})
  SET c.content = 'Lucius Cornelius Balbus —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094894Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a23522e78e1b0f6fcdef4e82747e8fada871b405d37fec363c13d422b17cc49e'})
  SET c.content = 'Spartacus —[OCCUPATION_OF]→ gladiator'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094927Z'
MERGE (subj:Entity {qid: 'Q83406'})
MERGE (obj:Entity {qid: 'Q482999'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0f0cf436540a97ec4b239f0244d3d0ebf8f6982759f778754d0719b4d6889636'})
  SET c.content = 'Spartacus —[OCCUPATION_OF]→ military leader'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094960Z'
MERGE (subj:Entity {qid: 'Q83406'})
MERGE (obj:Entity {qid: 'Q1402561'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '829e3b3d1799d342d9c866013eabe0d8ddb919326b80f5acb347efcc0de9f12a'})
  SET c.content = 'Apellicon of Teos —[OCCUPATION_OF]→ mintmaster'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.094995Z'
MERGE (subj:Entity {qid: 'Q9158420'})
MERGE (obj:Entity {qid: 'Q1463475'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f706f3229b2ca424fd281b38069955ad07419ece37cfa718feba7ae3fe5629f2'})
  SET c.content = 'Apellicon of Teos —[OCCUPATION_OF]→ book collector'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095035Z'
MERGE (subj:Entity {qid: 'Q9158420'})
MERGE (obj:Entity {qid: 'Q28776412'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '681c9162c13c63d63bed176c02be0a9cd4498abacbe14991899c87cdf6ecf2f8'})
  SET c.content = 'Marcus Perperna Veiento —[OCCUPATION_OF]→ politician'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095068Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q82955'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8c713e1e9b77ad24f32574bce2917c148a90f5e0ccb70507cf195ed55d147cd5'})
  SET c.content = 'Marcus Perperna Veiento —[OCCUPATION_OF]→ military personnel'
  SET c.source_id = 'wikidata:Q17167:P106'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095101Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q47064'})
MERGE (subj)-[r:OCCUPATION_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P106'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bc83fbc8ad5345af72dd823710189c658d61cc3b450da1e2a0c29b98be8ed300'})
  SET c.content = 'Pompey —[INVOLVED_IN_EVENT]→ Hasmonean Civil War'
  SET c.source_id = 'wikidata:Q17167:P1344'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095140Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q1588511'})
MERGE (subj)-[r:INVOLVED_IN_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1344'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd110c7318e80064fd47d3dc1be46db17ee6be5b7bc108e5af06781d31600a1e6'})
  SET c.content = 'Gaius Cassius Longinus —[INVOLVED_IN_EVENT]→ assassination of Julius Caesar'
  SET c.source_id = 'wikidata:Q17167:P1344'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095179Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q1025466'})
MERGE (subj)-[r:INVOLVED_IN_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1344'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'da6e11c7405bc4da0735fd58d9ff122508ac7bd6effca2117fbe9a36996b9470'})
  SET c.content = 'Antipater the Idumaean —[INVOLVED_IN_EVENT]→ Hasmonean Civil War'
  SET c.source_id = 'wikidata:Q17167:P1344'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095214Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q1588511'})
MERGE (subj)-[r:INVOLVED_IN_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1344'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b0b455da1ce17630d66bc6e7951d0ead9c66b26b82e3a619f94a82d0a340d097'})
  SET c.content = 'Cleopatra —[INVOLVED_IN_EVENT]→ banquet of Antony and Cleopatra'
  SET c.source_id = 'wikidata:Q17167:P1344'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095294Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q107305091'})
MERGE (subj)-[r:INVOLVED_IN_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1344'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '71a1d96da69c90c327009e4b8a4fc5e2571a28d7d6d1632b9da1a4050490b60e'})
  SET c.content = 'Sertorian War —[NAMED_AFTER]→ Quintus Sertorius'
  SET c.source_id = 'wikidata:Q17167:P138'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095351Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q296238'})
MERGE (subj)-[r:NAMED_AFTER]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P138'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9678b08b767a038fb49e6715625bb22a58eb0939d57f2e66e0131d5c1f1f45e7'})
  SET c.content = 'Social War of 91-87 BCE —[NAMED_AFTER]→ allies'
  SET c.source_id = 'wikidata:Q17167:P138'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095387Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q3612401'})
MERGE (subj)-[r:NAMED_AFTER]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P138'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'afed3912f43405a078e2cf0b4931621f8e606b47d97cb78ea90b813fe17e0476'})
  SET c.content = 'Julius Caesar —[LANGUAGE_OF]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095421Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '841a3d9968f7bdae47933dffd03a17fa1316c1749286709f39fcc25da73869f5'})
  SET c.content = 'Cloelius Gracchus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095454Z'
MERGE (subj:Entity {qid: 'Q11914149'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5a8d629b978064a5a86922caaa2973f81b102b5d48990ee2fb3a700810d39dd4'})
  SET c.content = 'Lucius Fufidius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095486Z'
MERGE (subj:Entity {qid: 'Q11923219'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6d93e6ac4c658ffc7d5486a8a8d23ad75e5015eabc8dcba51b05d249277c5281'})
  SET c.content = 'Gaius Herennius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095521Z'
MERGE (subj:Entity {qid: 'Q11923586'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b5af418786e9c9e75f68ae469c7dce9a7e1d63be75dd48439c9dc632ff30a92a'})
  SET c.content = 'Gaius Memmius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095552Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0d2c7ab8deb59444a0ec85ed2b5be34623e22f0f7a267e8e5e8230b3ac9b2ed9'})
  SET c.content = 'Quintus Calidius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095581Z'
MERGE (subj:Entity {qid: 'Q11944244'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a9fd485568eb9fbcd2da867f30c3d8e5919d7d9f6cb1cca495bfe155f3703655'})
  SET c.content = 'Gaius Tarquitius Priscus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095614Z'
MERGE (subj:Entity {qid: 'Q11950924'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aa116db9eaffe1dbc9817e0f6852a9602d61a83899cf29865089b89ce43b9a8d'})
  SET c.content = 'Lucius Thorius Balbus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095644Z'
MERGE (subj:Entity {qid: 'Q1247730'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0c1814360bc49ce89064d65a1a70a79b8ae7a74d296a02405a3379b311c18983'})
  SET c.content = 'Lucius Minucius Esquilinus Augurinus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095678Z'
MERGE (subj:Entity {qid: 'Q1248143'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'af1a114923d7266bde3c9b5e45a52c3a0d4207fb5cbb7c325d249f5ee45cfa0f'})
  SET c.content = 'Pompey —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095708Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f9b3d520631f19b90ab0b644818828d712351aec212b334119edff95b922a5b4'})
  SET c.content = 'Marcus Junius Silanus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095740Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '96718abec69950f4cc9fc9457d6ba242ccbb0b3a1e64b9ebfe56fcdf2830383e'})
  SET c.content = 'Mithridates VI of Pontus —[LANGUAGE_OF]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095775Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8e2b07a6bc14bc3d744c9a447f52d798a2f7e126c58d9060ae48e59f27073d1b'})
  SET c.content = 'Perseus of Macedon —[LANGUAGE_OF]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095808Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8a9d48b389b5c774a423e43abd390b234a35748bc62cd8250dad41ea2c6b6df4'})
  SET c.content = 'Gaius Cassius Longinus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095839Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c5a4645db3cfca7c68d6a559b49a378aba6711d9681a55e42a1ccd92bbca9568'})
  SET c.content = 'Scipio Africanus —[LANGUAGE_OF]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095872Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd66fcf6007bf88b004270c3160ea4a21de51808edf84a1e2ba4660cb13cce804'})
  SET c.content = 'Scipio Africanus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095904Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3c9bba3ac50b9265e14607a27c46988b17be8fa6e0f383bdb4be1389e7bf00a0'})
  SET c.content = 'Lucullus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095935Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c9c55b9d8947e4a85aeb385d248b55c5478e268cdddedbed526e4bedabf075b6'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.095968Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f71514151cefdfad0255565e4c81f2bbaf8d3fc42122c338645c7ca7998d13a5'})
  SET c.content = 'Quintus Sertorius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096001Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ffd19eabbc545d393293c6c17daf608adde6c2a7a707240686ec1b0d15932f3a'})
  SET c.content = 'Cincinnatus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096031Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f010dd17089288b9301d2186b437b957946177cf6492820a31d14640cf183971'})
  SET c.content = 'Marcus Claudius Marcellus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096061Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '45b7e706f617a772a966c529db9b8347da15fb090cc4d353a9a9604bfbc36088'})
  SET c.content = 'Quintus Caecilius Metellus Pius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096092Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5cfae23d640b2dfea7dca07fdbc28164e7fca1618ca6f23157c71f7003de3261'})
  SET c.content = 'Andriscus —[LANGUAGE_OF]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096121Z'
MERGE (subj:Entity {qid: 'Q362068'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '00c3bb5213a30562eb309f0ec7d6a3cafbec5edfff85a12e1665fdf827cb8ad3'})
  SET c.content = 'Marcus Marius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096149Z'
MERGE (subj:Entity {qid: 'Q3622239'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fce64ff0646b16a0c63f05b2d8e2d2ab08a52b65f4ca23040a239dde305e4219'})
  SET c.content = 'Ptolemy XIII Theos Philopator —[LANGUAGE_OF]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096182Z'
MERGE (subj:Entity {qid: 'Q39938'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '379b906d0f540f5b24f4d1341663da8dc8d7e4a31e48fc3487a988424e50928b'})
  SET c.content = 'Lucius Mummius Achaicus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096214Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2f052e178208eb5d47ba09938dd46b3a8943554a6409ab11853f108fdfbb5273'})
  SET c.content = 'Lucius Afranius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096246Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '33dd87fd86b7bf17691804cfd6e84d3c23ab879189ade8a37aacc6dcb5fe8282'})
  SET c.content = 'Mago —[LANGUAGE_OF]→ Punic'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096277Z'
MERGE (subj:Entity {qid: 'Q5393550'})
MERGE (obj:Entity {qid: 'Q535958'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f32c71c2627009b9c067edfdc551483fd0529ddb4a952c08223a9bc51895425f'})
  SET c.content = 'Quintus Labienus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096307Z'
MERGE (subj:Entity {qid: 'Q551516'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ccb5c2a97ba0a04fcb4d6276ab46f7f17e74f562063a63e49b1a95a139ae6f68'})
  SET c.content = 'Gaius Carvilius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096370Z'
MERGE (subj:Entity {qid: 'Q5517426'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a413b05fc0538e3c679468288afea2dde6f7b5c9de2448e95f75857692b764ac'})
  SET c.content = 'Tiberius Sempronius Gracchus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096414Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1a6a29430c00859ec51cbe47ebf5f6d004a4d4a1a0cc20e1e450563fefa8e678'})
  SET c.content = 'Lucius Marcius Septimus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096450Z'
MERGE (subj:Entity {qid: 'Q5759209'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd0dfbc1831f6d2a2c0dbcccc2631ddcb46034931a3707b6862bbe8279508ab5f'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Meroitic'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096483Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q13366'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '19ee9320f47f0fb460300003c798f236a49377ac5990b1aeb2b2e57d4eaeb0dd'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Egyptian'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096515Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q50868'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '37f472b2059762201404a94fb664feb1179318c1d9fa787c2be26e94b58844b6'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Old Arabic'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096547Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q21661186'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '06e2174a2341eded332da3df5f626e74b1072c36b46d6bf07ba0e72f8dac2508'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Parthian'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096577Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q25953'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a03ede1ca93ab60349086d0d2431cbb402f78aeca2038c59ef88216724f40243'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Syriac'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096608Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q33538'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '52cc8a4f22f2ab65dac5ada929add9666739c01f654c8678817b92015b6f7a12'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096646Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0fbbe3c9a2f935260b3015715729418106c2754f45f4419609c94804b0c65d8f'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Median'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096679Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q36461'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6350fb37571910d0ae51bebd70bcc3fade2fedf83b048b3e434cd6ed74ee3a81'})
  SET c.content = 'Cleopatra —[LANGUAGE_OF]→ Aramaic'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096710Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q28602'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0351c156e05ce90414488e0f0bb3ec88ad851a9c2e0824861a853b443f5fa86a'})
  SET c.content = 'Lucius Hirtuleius —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096741Z'
MERGE (subj:Entity {qid: 'Q6456490'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e29f8773329428781b99a386aaf4956e49d25c103c119e719c7a39c91accf631'})
  SET c.content = 'Gaius Aurelius Cotta —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096772Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd89fad644f467715a7b9dbf3c1fe0496720eba0d4d8e27eb96d9fe3de3565fc3'})
  SET c.content = 'Decimus Junius Brutus Callaicus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096808Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd60f4d298922a30a453403804b8133d61bfcce68ef098102f9237bd67d7d2b71'})
  SET c.content = 'Marcus Aurelius Cotta —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096841Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e604fd74dee7f46d4cfdfe36edf62ae276865d1ab00164e7d02ff0ad3c58ce73'})
  SET c.content = 'Lucius Cornelius Balbus —[LANGUAGE_OF]→ Latin'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.096874Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q397'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e75509950faec069bccb7711f98738d3eca07579b49dc1002d9ca026122fd608'})
  SET c.content = 'Mithridates I of the Bosporus —[LANGUAGE_OF]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097031Z'
MERGE (subj:Entity {qid: 'Q878437'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '532f23604650cd7c9a7309ccc27e282620923424391442def2ff7ecfbaaf3a39'})
  SET c.content = 'Apellicon of Teos —[LANGUAGE_OF]→ Ancient Greek'
  SET c.source_id = 'wikidata:Q17167:P1412'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097070Z'
MERGE (subj:Entity {qid: 'Q9158420'})
MERGE (obj:Entity {qid: 'Q35497'})
MERGE (subj)-[r:LANGUAGE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1412'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7a883d935462f71f53c2e1bd1b64b0bd20eab52465818ff4943e50fc801179fb'})
  SET c.content = 'Quintus Sertorius —[AWARDED_TO]→ Grass Crown'
  SET c.source_id = 'wikidata:Q17167:P166'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097112Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q869184'})
MERGE (subj)-[r:AWARDED_TO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P166'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '23f2ce8eb65f56b7863a4c0f21ebf48c7b51180525491909b73ba24a2e7a5183'})
  SET c.content = 'Marcus Claudius Marcellus —[AWARDED_TO]→ Spolia opima'
  SET c.source_id = 'wikidata:Q17167:P166'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097148Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q1570496'})
MERGE (subj)-[r:AWARDED_TO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P166'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1e36ea6c8a7da59225c244d9039e733d772b48cbbdea16fe7a3e76c758bf83c1'})
  SET c.content = 'Battle of Ilipa was under country Spain'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097269Z'
MERGE (subj:Entity {qid: 'Q1055755'})
MERGE (obj:Entity {qid: 'Q29'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '71cc7a814747993faab51529e6f7c6d3d07efdb30f85a609a5e0855101dce2b8'})
  SET c.content = 'Siege of Antioch was under country Turkey'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097323Z'
MERGE (subj:Entity {qid: 'Q109377210'})
MERGE (obj:Entity {qid: 'Q43'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9d6cddb0baf224746d6e1f869628355b0dd8987b55389242ec99094e1ac45692'})
  SET c.content = 'Battle of Numistro was under country Italy'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097365Z'
MERGE (subj:Entity {qid: 'Q1184835'})
MERGE (obj:Entity {qid: 'Q38'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4241788e7bc7fc8e9a44fdcb28e666ff577b6c7ee91471ba2acd6258da9bfb15'})
  SET c.content = 'Battle of Rhode was under country Spain'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097423Z'
MERGE (subj:Entity {qid: 'Q11908765'})
MERGE (obj:Entity {qid: 'Q29'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '90f4725737c4986b116c040daaa75086a91a0f7bc026fbd9a76150f73f201c1a'})
  SET c.content = 'Battle of Andagoste was under country Spain'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097471Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q29'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ebf607c46992c61cc2d1afe1129ae8ce20ac4e36dbcb5ffe12627bbf10beb97d'})
  SET c.content = 'Battle of Plaisance was under country Italy'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097505Z'
MERGE (subj:Entity {qid: 'Q124714225'})
MERGE (obj:Entity {qid: 'Q38'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c492e4bd1cca7550fbcfd745c483b4e5950539d4c473b22d06e40825c1852749'})
  SET c.content = 'Battle of the Axona was under country France'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097540Z'
MERGE (subj:Entity {qid: 'Q1260622'})
MERGE (obj:Entity {qid: 'Q142'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3ee98cd60327fc629d04087f9c2fd7f3dd6463c915c49692adb03f2c7670cfaf'})
  SET c.content = 'Battle of Uskana was under country North Macedonia'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097576Z'
MERGE (subj:Entity {qid: 'Q133480177'})
MERGE (obj:Entity {qid: 'Q221'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '033af1a9cee7beda28689e097a81d1be5368dadf6738fc6fbfdabda6b8b2b55a'})
  SET c.content = 'Battle of Cissa was under country Spain'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097610Z'
MERGE (subj:Entity {qid: 'Q1500211'})
MERGE (obj:Entity {qid: 'Q29'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c567ef7029959109aeccbc351eb7a5b416ba5423002fea8f8aee66dac8a14898'})
  SET c.content = 'Battle of Chalcedon was under country Turkey'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097646Z'
MERGE (subj:Entity {qid: 'Q2331925'})
MERGE (obj:Entity {qid: 'Q43'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3edc546421588774fb03e2f8bd4e8a26535fb82fcea9e96382937b6dd2b0287c'})
  SET c.content = 'Battle of Chaeronea was under country Greece'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097678Z'
MERGE (subj:Entity {qid: 'Q25414978'})
MERGE (obj:Entity {qid: 'Q41'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1f4e542279f625484a30d38dfc3229d0f806e063722d58d5e90815b9b325e55e'})
  SET c.content = 'Battle of the Douro was under country Portugal'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097712Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q45'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '141323d5dede84cda681b75883f69e54603d7c4339399b993088fcd5108a27a6'})
  SET c.content = 'Battle of Pydna was under country Greece'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097746Z'
MERGE (subj:Entity {qid: 'Q2617894'})
MERGE (obj:Entity {qid: 'Q41'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bcfd9d8a3c4d904a341755cc446e9a33830ddecb4fd9105046d245547118b807'})
  SET c.content = 'Battle of Mount Algidus was under country Italy'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097778Z'
MERGE (subj:Entity {qid: 'Q2705449'})
MERGE (obj:Entity {qid: 'Q38'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '392c33bdd5fd16330c549dc6bd4419dbfd918d12ff17b502b7da920050d30aab'})
  SET c.content = 'Social War of 91-87 BCE was under country Italy'
  SET c.source_id = 'wikidata:Q17167:P17'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097813Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q38'})
MERGE (subj)-[r:CONTROLLED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P17'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '45858d8e8fa66eb4df70381cbbd68504f92c77cbabe5d0cc7c9f80169d326b98'})
  SET c.content = 'Battle of the Douro —[DIFFERENT_FROM]→ Second Battle of Porto'
  SET c.source_id = 'wikidata:Q17167:P1889'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097849Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q233405'})
MERGE (subj)-[r:DIFFERENT_FROM]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1889'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f3106b711fc3649f7c70978057a12f35721d6878161a61d28c1262b8c90167c0'})
  SET c.content = 'Battle of the Lycus —[DIFFERENT_FROM]→ Battle of the Lycus'
  SET c.source_id = 'wikidata:Q17167:P1889'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097882Z'
MERGE (subj:Entity {qid: 'Q2707112'})
MERGE (obj:Entity {qid: 'Q139039894'})
MERGE (subj)-[r:DIFFERENT_FROM]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P1889'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2d678bf1e3534e8f5b05274698ab996eb2198d0efefcf089a05f8a825d7a24eb'})
  SET c.content = 'Ancient Rome is birthplace of Gaius Herennius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097926Z'
MERGE (subj:Entity {qid: 'Q11923586'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6a16c3e4eb2a4b01f2db9eb5cec45df90af7067b033386afc69d6c2da63be458'})
  SET c.content = 'Ancient Rome is birthplace of Gaius Memmius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097956Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e2c19ae387455a78e9b880bccfa2bb89a6cada87378a8827556adf7bcdd56af9'})
  SET c.content = 'Ancient Rome is birthplace of Lucius Decidius Saxa'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.097987Z'
MERGE (subj:Entity {qid: 'Q1289301'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8152f7b5dc738ac9167a86f9b01296a1206b67084bcb6a377b7dadb1b345beb6'})
  SET c.content = 'Ancient Rome is birthplace of Marcus Junius Silanus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098023Z'
MERGE (subj:Entity {qid: 'Q1528929'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b79b28e46d0cc2708a435dd1441e3879f0b2b15a7fbcdfad9d2262cc774cf3af'})
  SET c.content = 'Ancient Rome is birthplace of Gaius Cassius Longinus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098054Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5e81cfec7e0c4ce10c9805325fd6c256dedb3f2b78f52e03815a9e93ecf67c16'})
  SET c.content = 'Ancient Rome is birthplace of Scipio Africanus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098083Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5aa88fc5b24018a7952538a3b4c6cc0ebbfe1c8fa6e15755581c02746b1fb2da'})
  SET c.content = 'Ancient Rome is birthplace of Lucullus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098114Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a28c4c4cfc172ebdd1ae8d95a036e1e7dccec564834585da8d2094fc0b9873a6'})
  SET c.content = 'Ancient Rome is birthplace of Quintus Caecilius Metellus Numidicus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098145Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a2aeb1a126f0081bfea945c6984da4c07510f4207fbb3ee8b75de327fb2a3ddd'})
  SET c.content = 'Ancient Rome is birthplace of Marcus Claudius Marcellus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098174Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f3c275ec7de212dfbc9565f94f6d182f08b77418cc0b8bcd2d69a98689410c1f'})
  SET c.content = 'Ancient Rome is birthplace of Quintus Caecilius Metellus Pius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098205Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f6ca8ef7f88ef28f9fde8fbd96184a81c87ca5a86bc47c16e4d4a0489523d1b8'})
  SET c.content = 'Ancient Rome is birthplace of Gnaeus Cornelius Scipio Calvus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098239Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '13e6a820c69914ad9de80a8cadb36c1b8e4f960e76d0aa51ff5fec9ae0731aaf'})
  SET c.content = 'Edom is birthplace of Antipater the Idumaean'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098269Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q208475'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '41fc8595404ac462f8ddb2b3ef85f046809dd8de184039a4723db8eb7b193a4e'})
  SET c.content = 'Ancient Rome is birthplace of Quintus Caecilius Metellus Macedonicus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098301Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '017b90eeec04947c3acb0eee911c1290cd7254f6e1f932013b034640eb52ba6e'})
  SET c.content = 'Ancient Rome is birthplace of Marcus Marius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098332Z'
MERGE (subj:Entity {qid: 'Q3622239'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b1c06b6978b85e378c3c3c7ba9252e068651a996ba0ee8b6d977ed18fa889f9f'})
  SET c.content = 'Ancient Rome is birthplace of Gaius Carvilius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098365Z'
MERGE (subj:Entity {qid: 'Q5517426'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ff8b3c74aeef87d3fb15e38254546057536dc94f1554fb0b54b9d08f19786e63'})
  SET c.content = 'Roman Republic is birthplace of Gaius Aurelius Cotta'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098396Z'
MERGE (subj:Entity {qid: 'Q705425'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3f744644d9ae48b37e741b937b5ea7e34a929d03655379fa6e22ae68fd2cb1b7'})
  SET c.content = 'Ancient Rome is birthplace of Gaius Laelius'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098428Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ddd9c01f4aae2742c8c34aea43ec6aa3a321977a441c87d9762ec00f1e111672'})
  SET c.content = 'Ancient Rome is birthplace of Decimus Junius Brutus Callaicus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098461Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e037c10bef6b44b7dc687258389622fc7b6a5614f0b1123594435a7a176bc897'})
  SET c.content = 'Ancient Rome is birthplace of Marcus Aurelius Cotta'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098495Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a2bc31d24678e244430009df9d8f63a1151b2cebcb2c26c80e4bb041e97d4c63'})
  SET c.content = 'Gades is birthplace of Lucius Cornelius Balbus'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098529Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q3094251'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fb0b85d49afd5acf8260332cb89d22604ad76ffd35f3552433afba0ca4126309'})
  SET c.content = 'Ancient Rome is birthplace of Marcus Perperna Veiento'
  SET c.source_id = 'wikidata:Q17167:P19'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098562Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:BIRTHPLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P19'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '15b5b658a15f06de0cf7f007296920220d2b8b4fd214007029dad5bde01b5dd3'})
  SET c.content = 'Tiberius Sempronius Gracchus —[DEATH_PLACE_OF]→ Lucania'
  SET c.source_id = 'wikidata:Q17167:P20'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098596Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q1131978'})
MERGE (subj)-[r:DEATH_PLACE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P20'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '40df9833dd2e7b6dd4bbd6d8318948ab7b384c6a010a5778dc2e00c2ac96c3af'})
  SET c.content = 'Gaius Memmius —[MARRIED_INTO]→ Pompeia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098645Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q435946'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c6e365018363e156b2b3bb394571cdbf6e4ebaa7765346dca1ea922dfea8281c'})
  SET c.content = 'Mithridates VI of Pontus —[MARRIED_INTO]→ Monime'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098678Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q6900291'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5f9572e684c62e96856a679cdafad22c372206c02ab2738af028693b1c7fe4c9'})
  SET c.content = 'Mithridates VI of Pontus —[MARRIED_INTO]→ Berenice of Chios'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098712Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q512689'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '75b474d4322217a2f88c7f783ebce6c69037bc5e02af84395910ae37737ac8ee'})
  SET c.content = 'Mithridates VI of Pontus —[MARRIED_INTO]→ Hypsicratea'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098748Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q5961731'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3daac9c8dc76ee84b10bdd63f7e38eb765a282ecd7280f82e23f0c5035ff7978'})
  SET c.content = 'Mithridates VI of Pontus —[MARRIED_INTO]→ Stratonice of Pontus'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098786Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q4893357'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '228506cf964ec2cdca130974feaeff47d9ba747d18b2cb3c1631ddfba720bd56'})
  SET c.content = 'Perseus of Macedon —[MARRIED_INTO]→ Laodice V'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098816Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q433363'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '28923a0b397eb15be292377a99c2f5271fe984785d50b295aff095e418ee5230'})
  SET c.content = 'Cincinnatus —[MARRIED_INTO]→ Racilia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098847Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q118108456'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '940085510d76335857af6c2734c8b3e86095a604a578e2893a1a38ccf2b47951'})
  SET c.content = 'Quintus Caecilius Metellus Pius —[MARRIED_INTO]→ Licinia'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098878Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q12284966'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '16ea5cf75311d1b72ce08add268a37853c91bf50b3cd9a1a62fbfe66e1bcc024'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus —[MARRIED_INTO]→ unknown'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098912Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q24238356'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8e2a6d5078d993dccee752a27f6a9dba0132d9cce21fc0a93f03f7152bf01c6a'})
  SET c.content = 'Pacorus I of Parthia —[MARRIED_INTO]→ sister of Artavasdes'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098946Z'
MERGE (subj:Entity {qid: 'Q358097'})
MERGE (obj:Entity {qid: 'Q138349146'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9431fa29165299d8147d18653f9228e5777bca43c1de7a192fa976752caa7dce'})
  SET c.content = 'Hannibal —[MARRIED_INTO]→ Imilce'
  SET c.source_id = 'wikidata:Q17167:P26'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.098975Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q3135736'})
MERGE (subj)-[r:MARRIED_INTO]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P26'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9b36ef50afcd7fa6429fa67fbc180ab611b69a3c475123cc3b44ee76681fabe5'})
  SET c.content = 'Julius Caesar is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099008Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5777fcc745c819895df6e94b9498ccb4f4bcdd79c193755122e93fb30a0cc3d'})
  SET c.content = 'Lucius Fufidius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099037Z'
MERGE (subj:Entity {qid: 'Q11923219'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ba477bd8da7f406c424daf9273cd801753e38a05113c7bea63eadeef9a792725'})
  SET c.content = 'Gaius Herennius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099065Z'
MERGE (subj:Entity {qid: 'Q11923586'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5a5056a46136be3dbd6f335d21672291d210a687cd72423e221670941a427862'})
  SET c.content = 'Gaius Memmius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099092Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '76e8d9f5408a2cd4cd225cfb34d6f433e3acf1242af399793b0f94dfdea439d8'})
  SET c.content = 'Quintus Calidius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099122Z'
MERGE (subj:Entity {qid: 'Q11944244'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1ca35c287dfc693d65c838bf79a7090e28ca98258c2aca42a0d0ba5e11e7de0e'})
  SET c.content = 'Gaius Tarquitius Priscus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099158Z'
MERGE (subj:Entity {qid: 'Q11950924'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '212a169c060d30218891c5cc110888dbe34deff8c821ee3c1f6b61dbec855c30'})
  SET c.content = 'Lucius Manlius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099189Z'
MERGE (subj:Entity {qid: 'Q12285214'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f51b111d98c2d4ac1d39afda7fa466bb59bf994aa3f8f0a8bb26865b45edcfc7'})
  SET c.content = 'Lucius Thorius Balbus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099217Z'
MERGE (subj:Entity {qid: 'Q1247730'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1f5dce54c5f9689c73f000093aae371d8a8dbae147c0023cac34c1b3b13b3907'})
  SET c.content = 'Ganymedes is citizen of Ancient Egypt'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099247Z'
MERGE (subj:Entity {qid: 'Q1493701'})
MERGE (obj:Entity {qid: 'Q11768'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5734d78daa475d07e3450cacb67cf4ef5b28e27a84819cb28191498c58a63295'})
  SET c.content = 'Gaius Marius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099276Z'
MERGE (subj:Entity {qid: 'Q177975'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '49fc8f9ee006620d7d4d56f3c27c2f10900bbd2b8aa7134bd6b5da08b2a7e176'})
  SET c.content = 'Mithridates VI of Pontus is citizen of Kingdom of Pontus'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099307Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q7380487'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '841a07bd2b8ca7868b60c6bcafaca1a3b406bc84190e7afb402333a73d5c42e6'})
  SET c.content = 'Gaius Afranius Stellio is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099337Z'
MERGE (subj:Entity {qid: 'Q20002133'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7f68c629ab5712427ef30df536b8640d916f7eabef09ffd202b608e8a8c98412'})
  SET c.content = 'Gaius Cassius Longinus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099366Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ad35223ced6de44b53c043a0c40cbf103c0a8a2390be3ee05c48d772643b4871'})
  SET c.content = 'Scipio Africanus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099394Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '57409e635589914600194236be2fa851a67c3fc3fe11a8835e1e52b853eb969e'})
  SET c.content = 'Lucullus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099423Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '031fb4c6b2d5a47af2f6807a2aa6b0884284853dde0557ed5837346d1e1eadec'})
  SET c.content = 'Marcus Marius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099452Z'
MERGE (subj:Entity {qid: 'Q3622239'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '737f6ed5aa6cd611483c6f844a102aa4202f660cb872663ec303d5d47868bc79'})
  SET c.content = 'Tiberius Sempronius Longus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099482Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ffd2d65bed8d4dc4a847de498bc724e0e6831a88af527289f78335459f55d8fc'})
  SET c.content = 'Arsinoe IV of Egypt is citizen of Ptolemaic Kingdom'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099511Z'
MERGE (subj:Entity {qid: 'Q40013'})
MERGE (obj:Entity {qid: 'Q2320005'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '26cdd1a10a39b871ea2c83aa63fd9e99c72b4ad40c8e1623fd01020a27358761'})
  SET c.content = 'Lucius Mummius Achaicus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099540Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b5c96587cde3be5e623fb53d951977f64b1a55821affe5e67c02841c2054c5bd'})
  SET c.content = 'Hasdrubal Gisco is citizen of Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099571Z'
MERGE (subj:Entity {qid: 'Q452048'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c5961e7e5ebed55ac85fa36cfaa77ac331ec9e0d336527e1a5b0f13232416fd3'})
  SET c.content = 'Lucius Afranius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099602Z'
MERGE (subj:Entity {qid: 'Q472219'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bbb38f7e29dfa6418352e1d676db4cdf137256a13964b9e1c7a830174de3a7d8'})
  SET c.content = 'Decimus Laelius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099631Z'
MERGE (subj:Entity {qid: 'Q5249189'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6f682170b2db3ab33b85738d3c45f009eea31ecb64978b109e2678aff7a96010'})
  SET c.content = 'Mago is citizen of Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099661Z'
MERGE (subj:Entity {qid: 'Q5393550'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1ae44eca3e20284dccebfcb438221a38c1b1473a6e843c5b22e87463ea54bef4'})
  SET c.content = 'Gaius Carvilius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099690Z'
MERGE (subj:Entity {qid: 'Q5517426'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2d730bfd8f3276e6d875faf5bebe182ce59eb08be222ec8b6df3c4f1708a0e2a'})
  SET c.content = 'Tiberius Sempronius Gracchus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099720Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '65c6504a7dd03c35a72fdd9add544b2dbf3ac8a015b0b4cf53f364b92e664bee'})
  SET c.content = 'Lucius Hirtuleius is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099747Z'
MERGE (subj:Entity {qid: 'Q6456490'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '79e6516990a0e0029d520638f8d41c94a193ea4c9242add94fef322773a23df9'})
  SET c.content = 'Marcus Domitius Calvinus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099776Z'
MERGE (subj:Entity {qid: 'Q6758133'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f295fffc00995bbb7fe2f8ad6d02de0bd00f6792ceb095dd24478c41e3ca67e5'})
  SET c.content = 'Marcus Aurelius Cotta is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099807Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4338a4cc53da59fbed607f94901a7925dc0f36fa16630ece4cf74f04d56ed569'})
  SET c.content = 'Lucius Cornelius Balbus is citizen of Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099836Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '79cd3fb567bd3d28f4b7c2a762d398ff9f92a27bdd16f32883046d13777b7fd5'})
  SET c.content = 'Apellicon of Teos is citizen of Classical Athens'
  SET c.source_id = 'wikidata:Q17167:P27'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099864Z'
MERGE (subj:Entity {qid: 'Q9158420'})
MERGE (obj:Entity {qid: 'Q844930'})
MERGE (subj)-[r:CITIZEN_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P27'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '739930035102a1af22cc33a9b79b043fd9a180f0a5dfe44437a338494a14aaae'})
  SET c.content = 'Siege of Antioch —[LOCATION_OF_EVENT]→ Antigonia'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099896Z'
MERGE (subj:Entity {qid: 'Q109377210'})
MERGE (obj:Entity {qid: 'Q2853228'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '750f96178f601c22cc4094a5d58e77e83d110d0eb4047e69f6a448d54fe979e9'})
  SET c.content = 'Battle of Numistro —[LOCATION_OF_EVENT]→ Numistro'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099929Z'
MERGE (subj:Entity {qid: 'Q1184835'})
MERGE (obj:Entity {qid: 'Q11939048'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f7f126d710712c7dceb23aba6b6c0a11c61a917375c47514fed39f04b6a8a3d5'})
  SET c.content = 'Batlle of Emporion —[LOCATION_OF_EVENT]→ Empúries'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099961Z'
MERGE (subj:Entity {qid: 'Q11908712'})
MERGE (obj:Entity {qid: 'Q1229367'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4475165985fb469da8609e6e4e159e9f81082e398b7971d487cdd2f712319915'})
  SET c.content = 'Battle of Rhode —[LOCATION_OF_EVENT]→ Ciutadella de Roses'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.099991Z'
MERGE (subj:Entity {qid: 'Q11908765'})
MERGE (obj:Entity {qid: 'Q1094405'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '04bb10b1f25b5e8f767cfac4ff4f08b8fcddec695e74c11fbfe832c2abc1b2ce'})
  SET c.content = 'Battle of Andagoste —[LOCATION_OF_EVENT]→ Kuartango'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100020Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q1368846'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd7f3d9d935a119175c2115c4d532c3a713514bc20d49f2e64b9b43cc65e8f296'})
  SET c.content = 'Caesar\'s Civil War —[LOCATION_OF_EVENT]→ Balkans'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100052Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q23522'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b2d6212b021e69484170229968366d6e4eab75d110b18d06e1e490c3cc267f83'})
  SET c.content = 'Caesar\'s Civil War —[LOCATION_OF_EVENT]→ Africa'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100085Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q15'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e88221af57cbd45c0f38c1b2efda98181ead88fb319bdf89f322be20d5307e86'})
  SET c.content = 'Caesar\'s Civil War —[LOCATION_OF_EVENT]→ Roman Egypt'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100115Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q202311'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0805454528f98537aba84d9a7dabe8bb0a20f0107ebb6511b671d7072f8ad0a2'})
  SET c.content = 'Caesar\'s Civil War —[LOCATION_OF_EVENT]→ Italian Peninsula'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100146Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q145694'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fff85ae3fd6b662ce5ecbb4ef2c517894e47d3ef86b73b4325f60b310627c9f8'})
  SET c.content = 'Caesar\'s Civil War —[LOCATION_OF_EVENT]→ Illyria'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100176Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q32047'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '252f64796b3c7843fd2bccebfcfc8c586bcbc87985ee432111c86d7fe899f73f'})
  SET c.content = 'Punic Wars —[LOCATION_OF_EVENT]→ Ancient Carthage'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100206Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q2429397'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5d05b9d13700ab71a33fe0157d4224d4a99d20e1c51e71a13527846ba67bd3a'})
  SET c.content = 'Punic Wars —[LOCATION_OF_EVENT]→ Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100234Z'
MERGE (subj:Entity {qid: 'Q124988'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '25f1c212c7002810d805e7732670a897b5973e69b089a3ae03d1c74eb090cf24'})
  SET c.content = 'Battle of Delos —[LOCATION_OF_EVENT]→ Delos'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100264Z'
MERGE (subj:Entity {qid: 'Q130857859'})
MERGE (obj:Entity {qid: 'Q173148'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '32ef7963fd540500e22745012b15b34f1b53d125336930e22991675999722d11'})
  SET c.content = 'Battle of Uskana —[LOCATION_OF_EVENT]→ Uscana'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100292Z'
MERGE (subj:Entity {qid: 'Q133480177'})
MERGE (obj:Entity {qid: 'Q46187190'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '12ab266969591f1650544ccd391c25bc9ea8cc433ad5b9e61badc7f2f7744603'})
  SET c.content = 'Battle of New Carthage —[LOCATION_OF_EVENT]→ Qart Hadasht'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100324Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q3412434'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '427f04af7efe56aaa713403abfb66c37b5292f8e5e5461936e16e62929bce0f2'})
  SET c.content = 'Battle of Orongis —[LOCATION_OF_EVENT]→ Western Andalusia'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100357Z'
MERGE (subj:Entity {qid: 'Q18649467'})
MERGE (obj:Entity {qid: 'Q5694697'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b98aed8e02035b2708007e3aca405285befd5fba75f42ba24225ff67f1eda499'})
  SET c.content = 'Battle of Campi Veteres —[LOCATION_OF_EVENT]→ Campi Veteres'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100388Z'
MERGE (subj:Entity {qid: 'Q18667552'})
MERGE (obj:Entity {qid: 'Q11911076'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'af360a43ed38967f53573197b4cf0cf0d1fc75fd0c243add5a24a339e44531a3'})
  SET c.content = 'Gallic War —[LOCATION_OF_EVENT]→ Gaul'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100419Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q38060'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ac78b9c94d0031019294e762590df1067ab5340fcfa4cae5dc5a5bfa48cb8ce1'})
  SET c.content = 'Battle of Petilia —[LOCATION_OF_EVENT]→ Calabria'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100448Z'
MERGE (subj:Entity {qid: 'Q24045885'})
MERGE (obj:Entity {qid: 'Q1458'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '114121ebda758c642abf46e308807f1d82778d08387ca3040e20a092253ed531'})
  SET c.content = 'Battle of the Douro —[LOCATION_OF_EVENT]→ Douro River'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100479Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q14299'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7b4f96552f369c01c55dcc9353b0902725c3414c159f40bf4775a963ca4936a6'})
  SET c.content = 'Battle of Zama —[LOCATION_OF_EVENT]→ Zama Regia'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100510Z'
MERGE (subj:Entity {qid: 'Q2890429'})
MERGE (obj:Entity {qid: 'Q1892445'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '615c8f2a0227507221e90befd8611afb74f7e92ba181add26ca8c7e1daa083f5'})
  SET c.content = 'Sertorian War —[LOCATION_OF_EVENT]→ Hispania'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100540Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q186513'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b159dc4408e22fa50eee4691a6fe050951a298177983e887bc7d780847db30af'})
  SET c.content = 'Pyrrhic War —[LOCATION_OF_EVENT]→ Roman Italy'
  SET c.source_id = 'wikidata:Q17167:P276'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100569Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q913582'})
MERGE (subj)-[r:LOCATION_OF_EVENT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P276'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '87e8b3c1122628c132df10454ca6ddb62902be72dbe405c269349076f0c4fce2'})
  SET c.content = 'Battle of Ilipa is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100599Z'
MERGE (subj:Entity {qid: 'Q1055755'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2fbee2a215fad45f1d872c5ad7758c86e6a474f17f01834ef49be377b0b67f0f'})
  SET c.content = 'Siege of Antioch is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100627Z'
MERGE (subj:Entity {qid: 'Q109377210'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '49fdbb3debba775bbf1026ea301eb46d7217666d10ba5f55741dfd2b2860ba54'})
  SET c.content = 'Batlle of Emporion is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100656Z'
MERGE (subj:Entity {qid: 'Q11908712'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c7a2c194005c3cd856e0b9c43adae0af81f2b28410a5489974420df8bc4034f4'})
  SET c.content = 'Battle of Rhode is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100684Z'
MERGE (subj:Entity {qid: 'Q11908765'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e64ae2c817ce43c28bee647d6579f34c73ff83f9d5f7a8f103f3182d33c87d83'})
  SET c.content = 'Cloelius Gracchus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100711Z'
MERGE (subj:Entity {qid: 'Q11914149'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '937e542bde738bd3ae2c29d2dfa4585736f79518aa25fae0d4586bf12272cd12'})
  SET c.content = 'Lucius Fufidius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100740Z'
MERGE (subj:Entity {qid: 'Q11923219'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b5393e2fabd16a9f4684f36db8ccdca52aa4bc1b34abcdb10c459b59435604bb'})
  SET c.content = 'Gaius Herennius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100769Z'
MERGE (subj:Entity {qid: 'Q11923586'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '13229d61634f936a8bb8e1339a58aa18aa4318942570ec315554657e275f2546'})
  SET c.content = 'Gaius Memmius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100797Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '608db28c593799d8e7c4feac0b52d8edb5c1d7f6e92955371b8696be021db98f'})
  SET c.content = 'Hanno is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100824Z'
MERGE (subj:Entity {qid: 'Q11925197'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '27a6b6b483ca4852993955852f12d22b93f419ef897a633e9e61db46a61f6208'})
  SET c.content = 'Gaius Tarquitius Priscus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100853Z'
MERGE (subj:Entity {qid: 'Q11950924'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9773aa1ca1541e3d20d08daf6f6dc117d19e9780136ce3bfd7611083b2780fe6'})
  SET c.content = 'Battle of Andagoste is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100889Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '473a7e75f32fc30381fb49b7ae033e54d17c8b4ff5e7956e348b06da0aaf56ea'})
  SET c.content = 'Lucius Manlius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100918Z'
MERGE (subj:Entity {qid: 'Q12285214'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a6fea7648b77140a293b34d8964d19904ef248b760eb9a564b3d9fd23db183df'})
  SET c.content = 'Caesar\'s Civil War is instance of civil war'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100947Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q8465'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '31bbdc980c3c68e920a6a68db347c7204184df8fdca34507eb599810d45b2f8a'})
  SET c.content = 'Lucius Thorius Balbus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.100976Z'
MERGE (subj:Entity {qid: 'Q1247730'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fa9bbea9202c54ee34a7aa9041f823bcef808d67f0159fed479d9642f5bbf746'})
  SET c.content = 'Battle of Delos is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101004Z'
MERGE (subj:Entity {qid: 'Q130857859'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '68a775c8264d42eee5379b52064d0f9fe11b3fdea87653cc3ab8a88863a465c8'})
  SET c.content = 'Battle of the Tagus is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101034Z'
MERGE (subj:Entity {qid: 'Q131686739'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd40f69aa5987086e6d051b1be8c8e3fec0ce1e8920ea9617f26909a191e45e18'})
  SET c.content = 'Battle of Uskana is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101060Z'
MERGE (subj:Entity {qid: 'Q133480177'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '06650af6df2e508f539a52b66265ba1e781f2d45b8134ab65b4f7fa71821ed15'})
  SET c.content = 'Ganymedes is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101088Z'
MERGE (subj:Entity {qid: 'Q1493701'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b533b118e0e970b9da2e87750b0b5773a0ce113906a870dc1fc3fea003cc0c74'})
  SET c.content = 'Battle of Cissa is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101114Z'
MERGE (subj:Entity {qid: 'Q1500211'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1b71aa26765e13cdf185968f90d218fc68176723a59f3fa63f504abc7ea24c8d'})
  SET c.content = 'Battle of New Carthage is instance of siege'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101144Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q188055'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6705921df40d67d7e4f949b22c1dedcfa82dddb9cdd4da5f088bf9bfb0392cb1'})
  SET c.content = 'Battle of Halys is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101171Z'
MERGE (subj:Entity {qid: 'Q17277303'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c2ec0f4ecf73dbe26208989293f8f1518c4c98fb171931f58069d2f6613ba397'})
  SET c.content = 'Battle of Orongis is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101200Z'
MERGE (subj:Entity {qid: 'Q18649467'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e4b71949492eb359e9ea6058b4b28afb463c2b6c15c9fbc9036f72494c959bec'})
  SET c.content = 'Battle of Munda is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101227Z'
MERGE (subj:Entity {qid: 'Q18649505'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '471f129af6228a1367c34814a8af4228a51e85bd15488f9686420c7084e6ec53'})
  SET c.content = 'Battle of Campi Veteres is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101256Z'
MERGE (subj:Entity {qid: 'Q18667552'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fda0e21bc6ed5ef9dc5711a4fe4fa0bf86b5edb8a57d416be40aa8b9ad36cbcb'})
  SET c.content = 'Battle of the Nile is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101285Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3467e8167bbd82eafbe77eb0baeb86899cacbd4249a818ac088a929296a90861'})
  SET c.content = 'Gaius Afranius Stellio is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101313Z'
MERGE (subj:Entity {qid: 'Q20002133'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c125714344efc516c0222c17b9a1504bf5be9fccb069cc23eb2be2e2d896e1b8'})
  SET c.content = 'Gallic War is instance of war'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101341Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q198'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '64c70386077b953ef9f33d97507a37a0ffb98d82d2b344a61a2a6fcf7adbfa20'})
  SET c.content = 'Gaius Cassius Longinus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101367Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3b6f850e1102aad8296a7a0b89a94bd87fba4c43265c44c0032bfc0ef6bef35e'})
  SET c.content = 'Battle of Chalcedon is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101394Z'
MERGE (subj:Entity {qid: 'Q2331925'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '48dfd26ad2e47b7685b9eb501c3283575ffdbfa3376918a35a45db86f8003d9a'})
  SET c.content = 'Battle of Nola is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101423Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd631f0f2c1eb0950bf52b068f124454d7e0f7416a4aca31a6dfc8f29e4067fe0'})
  SET c.content = 'Battle of Petilia is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101450Z'
MERGE (subj:Entity {qid: 'Q24045885'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ce428a6a6baf34c0884a85c9d4dfac360aafa7eaea3fb67bc688f1aef105e667'})
  SET c.content = 'Battle of Chaeronea is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101478Z'
MERGE (subj:Entity {qid: 'Q25414978'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e29ccb436002f2e3fb62f15471c5321c196c00c06b94ab66c7f92fa808b31695'})
  SET c.content = 'Battle of the Douro is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101505Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f061ebd97e5760ef6a49b1128803de3f3529c59816e8b5ba6ffba1bc15080720'})
  SET c.content = 'Battle of Pydna is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101617Z'
MERGE (subj:Entity {qid: 'Q2617894'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3652429561c2a8fdab5d18b594f160fd1db2c675a8eddac11e49cf6af5be6eec'})
  SET c.content = 'Battle of Mount Algidus is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101680Z'
MERGE (subj:Entity {qid: 'Q2705449'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b0fb4f5f4af1bd75ac696f9fb50909f60ee20ed834bdba87c714c094d918139d'})
  SET c.content = 'Battle of the Lycus is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101718Z'
MERGE (subj:Entity {qid: 'Q2707112'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '442fa53fb53edc955f434352cf804a00adfdeb8dc243bd14eb46f693720aaedb'})
  SET c.content = 'Battle of the Granicus is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101753Z'
MERGE (subj:Entity {qid: 'Q28665781'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5c588f423e5e282f79ae49fc671455bd3f1906916c360ab3e9d85efea82b3810'})
  SET c.content = 'Battle of Zama is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101788Z'
MERGE (subj:Entity {qid: 'Q2890429'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e621643029f6cfee89ea7628c8a19e915c388b24b6d476538c2b0368bcb798bd'})
  SET c.content = 'Pacorus I of Parthia is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101819Z'
MERGE (subj:Entity {qid: 'Q358097'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b201f249b4fdba9039baba3f287b7b6aa97a98390344ad4b67448ec5e857faee'})
  SET c.content = 'Marcus Marius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101848Z'
MERGE (subj:Entity {qid: 'Q3622239'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '45502a2d1ea98d37a68e597de988b4c8fe8aaca284689457191603a1c7cd0516'})
  SET c.content = 'Sertorian War is instance of civil war'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101877Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q8465'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd716c461e148fbb9a83219264f00e21bb201c53881f0ebf4d6ba8e3b06310914'})
  SET c.content = 'Tiberius Sempronius Longus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101910Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e496a247e3034f4059c46dd9947e330a5045f3202819db2dee6fa2c88e52f983'})
  SET c.content = 'Lucius Mummius Achaicus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101941Z'
MERGE (subj:Entity {qid: 'Q445455'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3909762da566bd7a8abca347b0b501b2755a9f6fc4ca1fbe14e9329ab4cf12ea'})
  SET c.content = 'Decimus Laelius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.101970Z'
MERGE (subj:Entity {qid: 'Q5249189'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd0bcb7ef084293967098f849af6876eac8f6d0d45f4dec511e4a6658d30b36cb'})
  SET c.content = 'Mago is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102001Z'
MERGE (subj:Entity {qid: 'Q5393550'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '41e12cbc85bd5216559b0899c1c5048b5b1ac30591367d7fc12be993b7da5ee6'})
  SET c.content = 'Gaius Carvilius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102031Z'
MERGE (subj:Entity {qid: 'Q5517426'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '476a29fa89243f3bf3b6a1fa01e555cb7b76231cf4e2e001293ab80679acdc66'})
  SET c.content = 'Tiberius Sempronius Gracchus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102061Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6a90203011b45334e11f915dffd23802dfacdbe8ade76600252c63bf57ff6e12'})
  SET c.content = 'Lucius Marcius Septimus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102089Z'
MERGE (subj:Entity {qid: 'Q5759209'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7ca52b8a044cd6d9f95535961be5820f912fcadfd2bec31f9a829b31eed6c4d8'})
  SET c.content = 'Indibilis is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102118Z'
MERGE (subj:Entity {qid: 'Q604308'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aaeb7e6f9a0dc30c19d9774bd1bf971f8d58695d236f16683bf924b46c8e4e4e'})
  SET c.content = 'Lucius Hirtuleius is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102145Z'
MERGE (subj:Entity {qid: 'Q6456490'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1c3ceb87bdc123028e7d4fd45818938fbf550c2f0380fb3f8a73c1ed8aa96b7d'})
  SET c.content = 'Marcus Domitius Calvinus is instance of human'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102173Z'
MERGE (subj:Entity {qid: 'Q6758133'})
MERGE (obj:Entity {qid: 'Q5'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1949db03b4fd980e3c6242a0b68a38c6072a97854dc7babfb9c9246481ec6601'})
  SET c.content = 'Social War of 91-87 BCE is instance of war'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102204Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q198'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6cacad3c58a151c4d4f6dc2c0f552c3d4fff5fd3b8e6f0d1532691e860a0f2d8'})
  SET c.content = 'Macedonian Wars is instance of series of wars'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102234Z'
MERGE (subj:Entity {qid: 'Q75813'})
MERGE (obj:Entity {qid: 'Q104212151'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '49339efc2232878e8417f087b532f1d614b973089093cc2bcb8cb96cdf13e9d2'})
  SET c.content = 'Battle of Apamea is instance of battle'
  SET c.source_id = 'wikidata:Q17167:P31'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102262Z'
MERGE (subj:Entity {qid: 'Q9172749'})
MERGE (obj:Entity {qid: 'Q178561'})
MERGE (subj)-[r:INSTANCE_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P31'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '660e35c77071e1e6333ff1b7283da799ad4e1d57f088c2fecf1bd6a30f993034'})
  SET c.content = 'Battle of Ilipa is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102297Z'
MERGE (subj:Entity {qid: 'Q1055755'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '582e4fdb3154c35337b3e1a6855dd36b8c952acc63631c49a2e484955f6617df'})
  SET c.content = 'Siege of Antioch is part of Roman–Parthian Wars'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102620Z'
MERGE (subj:Entity {qid: 'Q109377210'})
MERGE (obj:Entity {qid: 'Q1192043'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'faaa9b68a03b39ae31df38b57cc38774199e76bc0dcc7cc028feeb96d46fee60'})
  SET c.content = 'Batlle of Emporion is part of Iberian revolt'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102672Z'
MERGE (subj:Entity {qid: 'Q11908712'})
MERGE (obj:Entity {qid: 'Q11945466'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a235cdbcc3c3436ab33918a31d0ad92004b9462057db30a84eada132858315a5'})
  SET c.content = 'Battle of Rhode is part of Iberian revolt'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102707Z'
MERGE (subj:Entity {qid: 'Q11908765'})
MERGE (obj:Entity {qid: 'Q11945466'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'df6e90861834acf6aab467fc927b76d0ce9699fa774a78d79eecf558e85fb047'})
  SET c.content = 'Battle of Andagoste is part of Roman conquest of Hispania'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102741Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q2422375'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f1b73b573812bd27ca6cc9f04994dccd7b9d89262db4535e634889deabec03db'})
  SET c.content = 'Battle of Plaisance is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102772Z'
MERGE (subj:Entity {qid: 'Q124714225'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fc2bc17e271326addca92e61dde0c3958f2b856287c2025bfd65e503fc943457'})
  SET c.content = 'Battle of Delos is part of First Mithridatic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102804Z'
MERGE (subj:Entity {qid: 'Q130857859'})
MERGE (obj:Entity {qid: 'Q1647768'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '50f374aa5582a18ffb32bf41f4861f07583a76222a69bb88609ee5a93bcfaec7'})
  SET c.content = 'Battle of the Tagus is part of Lusitanian War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102837Z'
MERGE (subj:Entity {qid: 'Q131686739'})
MERGE (obj:Entity {qid: 'Q1202928'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b9e4556de0644c9e656113dea59dc0eb8ba064761102ef969187791c752595a7'})
  SET c.content = 'Battle of Uskana is part of Third Macedonian War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102869Z'
MERGE (subj:Entity {qid: 'Q133480177'})
MERGE (obj:Entity {qid: 'Q76118'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3585558378c9706d74003e937c0fd2ea6c1de084cc35520bcbcadae27c0184e2'})
  SET c.content = 'Battle of Cissa is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102900Z'
MERGE (subj:Entity {qid: 'Q1500211'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cf3e8f8c2ca99e98722cca4de42b5426ff0ff7e7cf12efb9ebebb932a983e21e'})
  SET c.content = 'Battle of New Carthage is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102933Z'
MERGE (subj:Entity {qid: 'Q1591145'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c4701b23763b3a4fd2b9c89f69ade83b0e2d1185ceeb13c460d755a65b04a4ac'})
  SET c.content = 'Battle of Halys is part of Second Mithridatic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102964Z'
MERGE (subj:Entity {qid: 'Q17277303'})
MERGE (obj:Entity {qid: 'Q1991765'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '05cce54d3a5ce875226059a884d71560fbb95c8bde37b62e62e4269cdd9a42cc'})
  SET c.content = 'Battle of Orongis is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.102994Z'
MERGE (subj:Entity {qid: 'Q18649467'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6d50fcae8c0e34ccea89f28ea7ac770c47a0a18217807b16504a5dcb2eb64b4e'})
  SET c.content = 'Battle of Munda is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103022Z'
MERGE (subj:Entity {qid: 'Q18649505'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'daa54ccb22646b6ec4c0db4d5062d8e578b8e3bf0b24b60ab289ec6732e9b401'})
  SET c.content = 'Battle of Campi Veteres is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103052Z'
MERGE (subj:Entity {qid: 'Q18667552'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '52621e87bf3b25af3ea1341d2bbb7196313001c177d5d50bc8b279c29b7af7bf'})
  SET c.content = 'Battle of the Nile is part of Alexandrian War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103081Z'
MERGE (subj:Entity {qid: 'Q1975400'})
MERGE (obj:Entity {qid: 'Q9377266'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fbdf141063a89bcdf7c74c4a13e7e18b9e485066530a87c36191cba974a759d9'})
  SET c.content = 'Battle of Nola is part of Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103113Z'
MERGE (subj:Entity {qid: 'Q233402'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '611cca383e51e427841a0820afadb88bc4cd19b8cd931c866d1c9d96e75b885d'})
  SET c.content = 'Battle of Petilia is part of Third Servile War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103145Z'
MERGE (subj:Entity {qid: 'Q24045885'})
MERGE (obj:Entity {qid: 'Q194378'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ad3cc52a8ca92979ac639f4d24864c5cb6524b33fc4c945b273feb4f709de140'})
  SET c.content = 'Battle of Chaeronea is part of Achaean War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103175Z'
MERGE (subj:Entity {qid: 'Q25414978'})
MERGE (obj:Entity {qid: 'Q6861027'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0409b19a237478d9d74c781eed5baad0682d81cff0f01bd8e74e207d82973706'})
  SET c.content = 'Battle of the Douro is part of Roman conquest of Gallaecia'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103206Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q107342906'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '020c1c638764b3908ffe7592198f726a31e4ea6f873ccb35a1d1fe5d433938ce'})
  SET c.content = 'Battle of Pydna is part of Fourth Macedonian War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103236Z'
MERGE (subj:Entity {qid: 'Q2617894'})
MERGE (obj:Entity {qid: 'Q552373'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'afb66fd3a912dd5c20e34707159ed65337df280da441ca5965c1ce4921222d62'})
  SET c.content = 'Battle of Mount Algidus is part of Roman expansion in Italy'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103267Z'
MERGE (subj:Entity {qid: 'Q2705449'})
MERGE (obj:Entity {qid: 'Q7362293'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a29d2647010269fba84814db194642c34c4a17981ed67ab0fcf8ec6e995671ff'})
  SET c.content = 'Battle of the Granicus is part of Third Mithridatic War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103297Z'
MERGE (subj:Entity {qid: 'Q28665781'})
MERGE (obj:Entity {qid: 'Q1764124'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7c9ad4d6817ed6c58fc27a4f7c8ba389776fa2a4f47055273b3b94e64d1aba2c'})
  SET c.content = 'Battle of Zama is part of Jugurthine War'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103325Z'
MERGE (subj:Entity {qid: 'Q2890429'})
MERGE (obj:Entity {qid: 'Q827612'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f4ba3d10b565a568c8011bab9ab37c8eac0c9cb3c3fe3462b05598a1caa18508'})
  SET c.content = 'Sertorian War is part of Crisis of the Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103355Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q3395322'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f8e6b10f39f924ea8ffa4f10460e18993698cc420deb6eebb6d949a3059bdb40'})
  SET c.content = 'Battle of Apamea is part of Pompeian–Parthian Invasion of 40 BCE'
  SET c.source_id = 'wikidata:Q17167:P361'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103393Z'
MERGE (subj:Entity {qid: 'Q9172749'})
MERGE (obj:Entity {qid: 'Q55630237'})
MERGE (subj)-[r:PART_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P361'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '879b0c3b7bd001fa6eb7e7af1d4a8ad27553e8906cd75efe3150864925f897d0'})
  SET c.content = 'Lucius Fufidius held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103427Z'
MERGE (subj:Entity {qid: 'Q11923219'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2b94aa2b396dcd8415bfabf2ad24b341349481369205263e167ea73f46787247'})
  SET c.content = 'Gaius Memmius held office quaestor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103458Z'
MERGE (subj:Entity {qid: 'Q11923620'})
MERGE (obj:Entity {qid: 'Q189430'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '032d1e6e89abcadcd5a5b0dfd35727f2942f0114cc9350766cf5ce2bd1df59a9'})
  SET c.content = 'Quintus Calidius held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103491Z'
MERGE (subj:Entity {qid: 'Q11944244'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ec04e154ff9bd881eaed560f42ec17ac43bd9b671430b5ce3a58a7c3afd4888d'})
  SET c.content = 'Quintus Calidius held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103523Z'
MERGE (subj:Entity {qid: 'Q11944244'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a9b02339864597f3ca6ee5b8e3e1ade35f48fdc75189a0270c796cd4ab7aff5f'})
  SET c.content = 'Jugurtha held office King of Numidia'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103554Z'
MERGE (subj:Entity {qid: 'Q156173'})
MERGE (obj:Entity {qid: 'Q2738140'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3ea99a9704d46b1a3a8d24ec5900e80f3754e9d1c19de31e6601becd35a6e214'})
  SET c.content = 'Cato the Elder held office quaestor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103585Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q189430'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6863aedbc7a31a540ce35291796fd264c324e2042abc1ff33149c35e5b6183ae'})
  SET c.content = 'Cato the Elder held office Roman censor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103614Z'
MERGE (subj:Entity {qid: 'Q180081'})
MERGE (obj:Entity {qid: 'Q189851'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b5eb557812de1ff70aa38f88d037a7ca46d9530fb071c5b0b027bbdaa94de955'})
  SET c.content = 'Perseus of Macedon held office strategos'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103642Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q335954'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '579b6b8442643260920505690b3a162a1a98111c4fd792eefcafee0597dec6f2'})
  SET c.content = 'Gaius Cassius Longinus held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103671Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b339ccc73d65b71335b311b16be9a12a0466e8e0a05950b4bfcb4ae20fc14520'})
  SET c.content = 'Lucullus held office quaestor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103700Z'
MERGE (subj:Entity {qid: 'Q242819'})
MERGE (obj:Entity {qid: 'Q189430'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '802a8774c07d953bcaaa4108bb799fe27d61c6552989fda70303ca00bfc40f6c'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103733Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ebed01d5d1dfe4b70b4c6447e58a6457630858854379014fa8e7ae1ab8916574'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus held office Roman censor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103765Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q189851'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'eaf68ce3340cefecfe6b02cddd0e96e0c4b3e5709fcfe5c7d0490387aad6e2f1'})
  SET c.content = 'Quintus Caecilius Metellus Numidicus held office tribune of the plebs'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103805Z'
MERGE (subj:Entity {qid: 'Q281025'})
MERGE (obj:Entity {qid: 'Q11704729'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '05f96def15a42979d7996b2c043660162c4dfddc78474fddeb988379fa17dd71'})
  SET c.content = 'Quintus Sertorius held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103836Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '38322d55c6060e7dd5cc936f279bc6e352445ec276453693d5f0a721a8f60851'})
  SET c.content = 'Quintus Sertorius held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103865Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '039e6236f4fa18a31103b30d2aad70592f40b113a764220a77ed233d454990c6'})
  SET c.content = 'Quintus Sertorius held office quaestor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103894Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q189430'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9e26f8c98eaf3af3e97f7c09828c54bc8d45b68729344f361ae17aa32d68d8be'})
  SET c.content = 'Cincinnatus held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103923Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '35a466baf8f80480f70317669076fba6a0f2e7f1545a07056800b7b099d187d0'})
  SET c.content = 'Cincinnatus held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103953Z'
MERGE (subj:Entity {qid: 'Q309637'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e311d5bcce36ae7c8e25455645871778d2c93ccd81f068daeef3b5162f1a07a5'})
  SET c.content = 'Marcus Claudius Marcellus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.103982Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4c5f611579adc191a64561660ef70f1dadab85e9c1775bb544eb21f939c1e686'})
  SET c.content = 'Marcus Claudius Marcellus held office aedile'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104011Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q205757'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9a15d65c4b3ce8b5db2b406176858300281bbf451ca357c46da2ec4d44208893'})
  SET c.content = 'Quintus Caecilius Metellus Pius held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104041Z'
MERGE (subj:Entity {qid: 'Q313680'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5a79588a0b1ab95b38d2865943af390b25d9f6df4eab84899ed8567a79d27466'})
  SET c.content = 'Massinissa held office King of Numidia'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104072Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q2738140'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dacb63349bd701d4dc9063e10290f9b8912d1cf19d4c4aa46df4119331e046b7'})
  SET c.content = 'Gnaeus Cornelius Scipio Calvus held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104103Z'
MERGE (subj:Entity {qid: 'Q316475'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '68a282b7060f7ba80c1e1f62b9142c53f4abf5697ba9224e13730d75dd391042'})
  SET c.content = 'Publius Cornelius Scipio held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104132Z'
MERGE (subj:Entity {qid: 'Q3293507'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4877f6d92d4b287e670333109340dcde99931d6a10f3a2f9614bdc1d7b506889'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104163Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '161e4aaf54d8c8ca91e95e7d8129af71301845b15a9e2c67c0176008b17ef811'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104192Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c5f1fcee2b0bcdf6895b902748f4600ae4476908d5b0f413757f359a434edcb4'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus held office Roman censor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104222Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q189851'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5733a2bcd09e0cefdc0a066ad69488a5a92b9bcfd082e6d57bb2f8381f8bff17'})
  SET c.content = 'Marcus Marius held office ancient Roman senator'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104251Z'
MERGE (subj:Entity {qid: 'Q3622239'})
MERGE (obj:Entity {qid: 'Q20056508'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9a7d9ccb751c044592d0780003e9d982cd8ac93f5b30576fda4872d9e8f34d34'})
  SET c.content = 'Ptolemy XIII Theos Philopator held office pharaoh'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104291Z'
MERGE (subj:Entity {qid: 'Q39938'})
MERGE (obj:Entity {qid: 'Q37110'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e4584a9c7537442130b866bccd60054ca69a0a75ca0c704bd86f0af26a6bf187'})
  SET c.content = 'Decimus Laelius held office tribune of the plebs'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104324Z'
MERGE (subj:Entity {qid: 'Q5249189'})
MERGE (obj:Entity {qid: 'Q11704729'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1fddf0f108b379e44e2ffe5913eec08626c865e9871848e631300677636451fc'})
  SET c.content = 'Lucius Marcius Septimus held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104354Z'
MERGE (subj:Entity {qid: 'Q5759209'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '67a6aea79b210da7164e3eb91a042a4aed7941cdd9671906446a100dfc8e02b9'})
  SET c.content = 'Lucius Hirtuleius held office quaestor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104383Z'
MERGE (subj:Entity {qid: 'Q6456490'})
MERGE (obj:Entity {qid: 'Q189430'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8d1607057814e688884f23419735f0d9da04b76280925d26e316e9074db541de'})
  SET c.content = 'Gaius Laelius held office aedile'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104413Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q205757'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c112c7417416482bfb581334fc6ddc138aff12c02fadbe0378be64aa232dd31c'})
  SET c.content = 'Gaius Laelius held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104444Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0b5da7f73356f64a3fd8482d0a641dd6dbb1973ec239304f9dd933dcae7a58c1'})
  SET c.content = 'Gaius Laelius held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104477Z'
MERGE (subj:Entity {qid: 'Q706305'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b8d4142bcfc1d463c413e3aed0d082ee605248b59efecbe9d93438f9c9853eb3'})
  SET c.content = 'Lucius Cornelius Balbus held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104509Z'
MERGE (subj:Entity {qid: 'Q766552'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f462c18e17e953657dfd13e9ce6cde38020d010e27d7303c6c7f4e92c72ff1f5'})
  SET c.content = 'Marcus Perperna Veiento held office Roman consul'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104541Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q40779'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f51db3a64c1c29e20a5bd55c7405dbd11e483c1293f3f7f8eeafe3d2a222853a'})
  SET c.content = 'Marcus Perperna Veiento held office Roman governor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104576Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q1190123'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a1de8a1556ff44bd9b96a3f9f16fc6a1090419d43a82ee7e6306bbfd08dba19b'})
  SET c.content = 'Marcus Perperna Veiento held office praetor'
  SET c.source_id = 'wikidata:Q17167:P39'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104604Z'
MERGE (subj:Entity {qid: 'Q922459'})
MERGE (obj:Entity {qid: 'Q172907'})
MERGE (subj)-[r:APPOINTED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P39'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '36b20bf1c3c08870c5698342d1d077bfb59f1627411883d2bca89ac3f18bb452'})
  SET c.content = 'Mithridates VI of Pontus is parent of Arcathius'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104637Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q2349623'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5b5407de3277b2075a9ddcccbe49c66e51bc8024b3a41d67c6b431479c30132b'})
  SET c.content = 'Mithridates VI of Pontus is parent of Eupatra'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104666Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q20100534'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '50f0912d1e8c914185657a2af8e4838bdc469e15ea6a01b2b076acff6a5b688d'})
  SET c.content = 'Mithridates VI of Pontus is parent of Nysa'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104695Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q11938849'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4e79ada9485303cb12753e59b999344b570068f9aabf943d465e8282693d2f0b'})
  SET c.content = 'Mithridates VI of Pontus is parent of Pharnaces II of Pontus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104727Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q313052'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd5cef02d1c6cf44f1145862e89010e3f1a209c5b5dfeaeb79515f71beceee1ae'})
  SET c.content = 'Mithridates VI of Pontus is parent of Athenais Philostorgos II'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104758Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q4813408'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a9279dba0a13fc51ca6f38ca9a38c6d23291af9b48df11826769a99feb051234'})
  SET c.content = 'Mithridates VI of Pontus is parent of Cleopatra of Pontus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104789Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q461784'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '582ea2541650510df5bd7d3d6706127a88f08472700b4b8bea944fd6fd0846fe'})
  SET c.content = 'Mithridates VI of Pontus is parent of Ariarathes IX of Cappadocia'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104820Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q1259636'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '54868356639fdded0ccb2b38503fd0ba662d27babd66df6b6ae108abbe2ecd19'})
  SET c.content = 'Mithridates VI of Pontus is parent of Adobogiona the Younger'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104851Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q18639401'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'dcc5f872bf87b542d65868bcb811a4a262664c1baca5064292d1990c88d287d4'})
  SET c.content = 'Mithridates VI of Pontus is parent of Machares'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104880Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q2064634'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b2bdb1d9595e62efb56eb5fba933622746aa93213eb86990227853128f523a53'})
  SET c.content = 'Mithridates VI of Pontus is parent of Cleopatra the Younger'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104913Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q109490629'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '94cf63e2834dcf7452b851f683389071235bdce3b22c309f864c29bcbb424780'})
  SET c.content = 'Mithridates VI of Pontus is parent of Xerxes of Pontus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104945Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q18224605'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '19b69e9c49c1e8cab3345abab5db921c20472d4f7f0643dedc8779b373d1353f'})
  SET c.content = 'Perseus of Macedon is parent of Andriscus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.104975Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q362068'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c950379e97f944246a59a1c4bd77beb7bf202d4ddfd5958cb5977412ea7a6655'})
  SET c.content = 'Perseus of Macedon is parent of Pseudo-Alexander'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105004Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q113394546'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6f72b702d285b38816ebe64a17baac0162697622dea11b619158113e4ede8fa1'})
  SET c.content = 'Perseus of Macedon is parent of Alexander'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105033Z'
MERGE (subj:Entity {qid: 'Q207363'})
MERGE (obj:Entity {qid: 'Q4718158'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '763c78adbb12071d0f47917b6a1c6faf5853a4f00bdc0495b07b2eeaaf83dc6d'})
  SET c.content = 'Gaius Cassius Longinus is parent of Cassius'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105066Z'
MERGE (subj:Entity {qid: 'Q207370'})
MERGE (obj:Entity {qid: 'Q111288376'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1c899066ef6e2aabac55a393319072d74d01c0a4d69b1ebdfff9d2dd7c9d9784'})
  SET c.content = 'Massinissa is parent of Misagenes'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105094Z'
MERGE (subj:Entity {qid: 'Q314685'})
MERGE (obj:Entity {qid: 'Q11937080'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c148e62952b41e8ded8b8ddce824ebd18ea92cb3231013d9bda5e90001870264'})
  SET c.content = 'Antipater the Idumaean is parent of Phasael'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105123Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q2778094'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '31b5913dece9a7ffd859ac28d0dfdc53002d2794abfbfc8c0b1fd06534c44d22'})
  SET c.content = 'Antipater the Idumaean is parent of Salome I'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105152Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q254920'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a02516dc4fc4a6709f01cbf7fc07bc5ebfad24b8036db4aaefc6fc6d0a94e210'})
  SET c.content = 'Antipater the Idumaean is parent of Joseph'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105183Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q10308667'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '098fbc33dff4102a334a7f21d96cb4b9c9f9b440fe92483352e63031a1f3fc51'})
  SET c.content = 'Antipater the Idumaean is parent of Pheroras'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105211Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q2085552'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6c53258ebca842a9cf505177c73e9a1faa10257517ae545079fa94ecc327a890'})
  SET c.content = 'Antipater the Idumaean is parent of Herod the Great'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105241Z'
MERGE (subj:Entity {qid: 'Q319075'})
MERGE (obj:Entity {qid: 'Q51672'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c16bcf93e0775ebcef92f060f1d7eaad08d75d04d78068673f09e6a6cf76193a'})
  SET c.content = 'Quintus Caecilius Metellus Macedonicus is parent of Caecilia Metella'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105274Z'
MERGE (subj:Entity {qid: 'Q355768'})
MERGE (obj:Entity {qid: 'Q99844311'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'cba417de0896014feab1ee63bd38210193449a7bb09204430b389055b821cf06'})
  SET c.content = 'Hannibal is parent of Haspar Barca'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105304Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q42056070'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ebbf3beefa88c4d6e024b8a37a8ca7fa786d3f3105974e461005c9d9d57667ac'})
  SET c.content = 'Decimus Laelius is parent of Decimus Laelius Balbus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105426Z'
MERGE (subj:Entity {qid: 'Q5249189'})
MERGE (obj:Entity {qid: 'Q113639333'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5d353cc11a35d0c86c57c231e5a8b1504bdc92d193a67a5ddbb4688042d7d9e4'})
  SET c.content = 'Marcus Domitius Calvinus is parent of Gnaeus Domitius Calvinus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105459Z'
MERGE (subj:Entity {qid: 'Q6758133'})
MERGE (obj:Entity {qid: 'Q383846'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c8285d1bf637ce3088f24f17a0c7d4618b2944b56249adf3c4e6c76912bc31cb'})
  SET c.content = 'Decimus Junius Brutus Callaicus is parent of Junia'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105490Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q11929531'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '205cbabb5bdf404c32925f6368382740f0336a507d3a47b218dc610b5f29a133'})
  SET c.content = 'Decimus Junius Brutus Callaicus is parent of Lucius Junius Brutus Damasippus'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105526Z'
MERGE (subj:Entity {qid: 'Q718090'})
MERGE (obj:Entity {qid: 'Q11934108'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '26a2641bec47ad72749588c2381d414feeb6dae7020e9a9cc8aa3a1304c79e22'})
  SET c.content = 'Marcus Aurelius Cotta is parent of Marcus Aurelius Cotta'
  SET c.source_id = 'wikidata:Q17167:P40'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105559Z'
MERGE (subj:Entity {qid: 'Q720859'})
MERGE (obj:Entity {qid: 'Q24855318'})
MERGE (subj)-[r:FATHER_OF]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P40'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1b833a717c8a7e9d49180ff827a55421a0792b7c4c9ab5be7e64210c8bdad573'})
  SET c.content = 'Julius Caesar —[HAS_MEMBER]→ First Triumvirate'
  SET c.source_id = 'wikidata:Q17167:P463'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105599Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q715380'})
MERGE (subj)-[r:HAS_MEMBER]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P463'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '349f47e430c36226a435d1bde90bd41299c41894188fedf1aa17ee935ea2244f'})
  SET c.content = 'Pompey —[HAS_MEMBER]→ First Triumvirate'
  SET c.source_id = 'wikidata:Q17167:P463'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105632Z'
MERGE (subj:Entity {qid: 'Q125414'})
MERGE (obj:Entity {qid: 'Q715380'})
MERGE (subj)-[r:HAS_MEMBER]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P463'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2fd459dce4434958767eb9bcd1dfa1b9b191578ef663fd1b4dcfeab984f998a8'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Zela'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105670Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q971507'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3559a041d0a02962510768d2c9c1f912a7feb475e98a628dd5cd73ec336f5754'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Hippo Regius'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105705Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q28662986'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1c0d7fddf8c0600a7ca80019ff6ec629a5398b0aa8e79c59bf534b401d8ffe8a'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Lauro'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105736Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q29513472'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'e8fb9151eab86c8fe6181dd64a0b2c71301100caa20c6d339e7bfe96919b854e'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of the Baetis'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105766Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q54864961'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2b5bbcac10015f68145a94b0a639a427da591c12292e0c4dc67dd0a4ad8651fb'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Corduba'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105797Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q9352344'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '58420146ed9e4a1377e4100248a94230fbf4dd04296fabe6ea8b7cb8d1d8a001'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of the Bagradas River'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105830Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q619030'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fd1b4a31c34096afe905a748cd65f00c345c97eb8e4d35651bfa79f4a4daefde'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Brundisium'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105863Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q25444447'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c891cffb15087d8074cd56a87a992c0a8876605975055d7bb8c08ebd650e2ff9'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Munda'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105893Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q516760'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5377dd2d0599506c5a9032b175070b49dbb0f2330a6104610989b0fab3382bca'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Tauris'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105924Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q11688130'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '62119ecfff8ba0c8dfadc8b2298d4b57be3068bd29e1656608b345c358943914'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Pharsalus'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105955Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q203681'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b90c12acfa6875ad3bf2d3aaa04dc44b1887800e357738bdfbbd8f4b077295be'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Nicopolis'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.105986Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q2889520'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'bf5c6144a10fbba8ae08ec1414731e47763caac8d537f9508ccb20b1897fee1c'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Apamea'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106017Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q28662992'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ec9cb213c729ebff1cb779282d8e8ee5056b9d7fb0cc087fff5685da09b38715'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Curicta'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106048Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q107304813'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5796c9eb38774c66b4f3195c39097a33b9fd9910438bfc9eaacfee20254f35cd'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Oricum'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106078Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q28531438'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3837cd74069dcfd6d09e1caced040ace4a5e8692909ceba57e9f4fbbe1db6408'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Corfinium'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106109Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q18001862'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aa82e05802f2811bf4d544fa08134e5eef8a900c1b61a499195a3641fd7b59a7'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Dyrrhachium'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106144Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q525325'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b6df3e1ebfcd7d71887f0cc76e247314bfad5a5059db70e55703f39bcabf1e80'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Alexandria'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106175Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q16208146'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c76bac76ec105642489331143a08fa8a6a7b3de2ed4c89b65480c68e05350044'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Ruspina'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106206Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q762458'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6dcd734d4af580aab3899a01d3cc6bb08fef6340b5e3e6a472496658a5b53c58'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Ilerda'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106236Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q2291971'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8780eaccd356d0beed4316f2b3363f89a3cf31570ad124b96ede96d6ff88d67a'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Thapsus'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106278Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q849653'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd6e3afa463b59fff768ec4ba4a97bde27155f28d3c262589827001abc86352a7'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Massilia'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106312Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q2127400'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4d75f6ceabf10862d8af1a99b0972a59eeb8ff1a790eb3f877c3e737384cfd49'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of the Nile'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106344Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q1975400'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '077f81bf375d35fa2b779e8076aa416180c43c6835457d05607caa6cbedd1a81'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Gomphi'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106374Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q54864606'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd8b6c9cdadb332db24bee0a78c982d01b11b614760d994e2614a940dd4e6ef17'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Carteia'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106405Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q9173074'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '011e4b4d6ce19f4032d3aa96083f0c091ef1c3cf568fa8beb0e824a8df0cbfa0'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Battle of Utica'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106439Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q2416094'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3aad38a59adb89478afc812c4a6cf54b2fc85564eb3b5c0e218778a25a128592'})
  SET c.content = 'Caesar\'s Civil War —[CONTAINS_PERIOD]→ Siege of Salona'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106471Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q54864605'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '67db4d512c76a35b9a2223f57e4e47809fa32b90fab4184108324d7061f86197'})
  SET c.content = 'Macedonian Wars —[CONTAINS_PERIOD]→ Second Macedonian War'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106504Z'
MERGE (subj:Entity {qid: 'Q75813'})
MERGE (obj:Entity {qid: 'Q75665'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0f3fc39d8e7c62cfc2fed653b1594450b1b98bc9e5d66dd6cd9eca5592709910'})
  SET c.content = 'Macedonian Wars —[CONTAINS_PERIOD]→ First Macedonian War'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106537Z'
MERGE (subj:Entity {qid: 'Q75813'})
MERGE (obj:Entity {qid: 'Q75626'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4ab0dcd1c1a906100d50e6b9fd150c96fb3372343a764e02ec20f4c0bbf717a1'})
  SET c.content = 'Macedonian Wars —[CONTAINS_PERIOD]→ Third Macedonian War'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106569Z'
MERGE (subj:Entity {qid: 'Q75813'})
MERGE (obj:Entity {qid: 'Q76118'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6c7a8b7796daada69e4f12debc7e3abf9fd2ccfc64a397e88df3c2c239d166da'})
  SET c.content = 'Macedonian Wars —[CONTAINS_PERIOD]→ Fourth Macedonian War'
  SET c.source_id = 'wikidata:Q17167:P527'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106602Z'
MERGE (subj:Entity {qid: 'Q75813'})
MERGE (obj:Entity {qid: 'Q552373'})
MERGE (subj)-[r:CONTAINS_PERIOD]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P527'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '56cedd1e14c13d48525ae65fab7ed1ac47fcfa5d2d51b8c113a537de7c6cb838'})
  SET c.content = 'Julius Caesar fought in Gallic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106636Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q202161'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '21d86e5b5cf58edf5ca917855b67d9c2f9abdd9363b12ed7e645a11561e3ca5f'})
  SET c.content = 'Julius Caesar fought in Caesar\'s Civil War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106669Z'
MERGE (subj:Entity {qid: 'Q1048'})
MERGE (obj:Entity {qid: 'Q1238338'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8d9d62aadd29d34a7376f40b1ecfb8aa4c0d85acb93284b4220a252ba656dc6f'})
  SET c.content = 'Mithridates VI of Pontus fought in Mithridatic Wars'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106702Z'
MERGE (subj:Entity {qid: 'Q185126'})
MERGE (obj:Entity {qid: 'Q1616064'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f1657c2fafd4b03e4b1e307fe15ea0a2232518bfae6428d0fdc56ad8ff72507a'})
  SET c.content = 'Scipio Africanus fought in Roman–Seleucid War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106736Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q486831'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ca56236075953d00b443749af46bb6e9a55c30e0c3ab4a6d5d69576205fdaef4'})
  SET c.content = 'Scipio Africanus fought in Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106765Z'
MERGE (subj:Entity {qid: 'Q2253'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4790d0e4c0eb5f146231043deaa345e06c3892435ce70115339a9ce8b316706b'})
  SET c.content = 'Quintus Sertorius fought in Sertorian War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106795Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q3778726'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '01b7299d93ec757957f1f8ba61e26e58847f3029634da091efab104d16fa18de'})
  SET c.content = 'Quintus Sertorius fought in Battle of Arausio'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106825Z'
MERGE (subj:Entity {qid: 'Q296238'})
MERGE (obj:Entity {qid: 'Q776215'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1c5116b228418fd75a30be23299b48acc9dd6140142ad9de287bcaa56b973ba4'})
  SET c.content = 'Hasdrubal Barca fought in Battle of the Upper Baetis'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106855Z'
MERGE (subj:Entity {qid: 'Q311702'})
MERGE (obj:Entity {qid: 'Q1458235'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3e12dd24f34965f6f7be3be5615c80a250ca2ab3b09b0de23408f7102b4a8346'})
  SET c.content = 'Marcus Claudius Marcellus fought in Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106887Z'
MERGE (subj:Entity {qid: 'Q312306'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2c3e2b6d05c0b4853a793cb4161ae7c361d7215c33b2b6cdbf5dccbd8da832ca'})
  SET c.content = 'Hannibal fought in Barcid conquest of Hispania'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106918Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q11915292'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0f66f2e39dffc990d0994a477c1d85cd556cb55473cf2510df2ad75ff7449d77'})
  SET c.content = 'Hannibal fought in Roman–Seleucid War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106948Z'
MERGE (subj:Entity {qid: 'Q36456'})
MERGE (obj:Entity {qid: 'Q486831'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2840690db4504f724aff14968922dc2313c7ccaeaa1e7a8140f6bfe9d4c8f156'})
  SET c.content = 'Tiberius Sempronius Longus fought in Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.106979Z'
MERGE (subj:Entity {qid: 'Q382276'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '58f27d1aaa97d97bc633c5e3a72ced98cf916e07c9edb83cf86f12642a426fc3'})
  SET c.content = 'Mago fought in Battle of New Carthage'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107010Z'
MERGE (subj:Entity {qid: 'Q5393550'})
MERGE (obj:Entity {qid: 'Q1591145'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '74f816e464d5b938aeae312d5fdcd0d0a622a6eae985e5405449a73986d6207c'})
  SET c.content = 'Tiberius Sempronius Gracchus fought in Second Punic War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107048Z'
MERGE (subj:Entity {qid: 'Q561677'})
MERGE (obj:Entity {qid: 'Q6271'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '27b4c806f193d94bd00459cb55260b6f215dce844f4b2fd5df31957760bc9575'})
  SET c.content = 'Cleopatra fought in Battle of Actium'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107079Z'
MERGE (subj:Entity {qid: 'Q635'})
MERGE (obj:Entity {qid: 'Q160387'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5ad0101f1ab1b14fa6e6589c52113bdae5afabf6cea30645281fd1766abbc76'})
  SET c.content = 'Spartacus fought in Battle of Mount Vesuvius'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107111Z'
MERGE (subj:Entity {qid: 'Q83406'})
MERGE (obj:Entity {qid: 'Q4087418'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd4b4acc69c547f47248c8e2b6c5d115e27a1271fde804ee41246683d04563b37'})
  SET c.content = 'Spartacus fought in Third Servile War'
  SET c.source_id = 'wikidata:Q17167:P607'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107144Z'
MERGE (subj:Entity {qid: 'Q83406'})
MERGE (obj:Entity {qid: 'Q194378'})
MERGE (subj)-[r:BATTLED_IN]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P607'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8ae8af13bdbac59a8ebc0faf2244ea9689df47a43125824d91793d8e0dca301b'})
  SET c.content = 'Batlle of Emporion had participant Iberians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107181Z'
MERGE (subj:Entity {qid: 'Q11908712'})
MERGE (obj:Entity {qid: 'Q190992'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '051483c4a275ee95496b02a5062f53a7f87793e2a45c782fa9241fbbe37daafa'})
  SET c.content = 'Battle of Rhode had participant Iberians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107216Z'
MERGE (subj:Entity {qid: 'Q11908765'})
MERGE (obj:Entity {qid: 'Q190992'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd1ab9891c3c6027c88da66b6718c2ebeb4098a15a034e5a2a38df09ab2529476'})
  SET c.content = 'Battle of Andagoste had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107249Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6bd41402e614bbb996f033f70134bd528938becc920f114dcc582a4d5ab1a8d2'})
  SET c.content = 'Battle of Andagoste had participant Caristii'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107282Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q2938858'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '97f78d96e5639cac116dc37009f79f58d049fb10ae7cd89fe2e9877779660a59'})
  SET c.content = 'Battle of Andagoste had participant Cantabri'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107313Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q855140'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd72d950787cf1d85f7c58ec1b3ac281ea9b98f36b56754f44e47f5339292de0a'})
  SET c.content = 'Battle of Andagoste had participant Autrigones'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107348Z'
MERGE (subj:Entity {qid: 'Q12253460'})
MERGE (obj:Entity {qid: 'Q789372'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5f09726d956572734fecd2f36e5a31cc48666646791db699a282acd91b56add5'})
  SET c.content = 'Caesar\'s Civil War had participant Julius Caesar'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107380Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q1048'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8ec72277bd99cbda9d172e28ebb68fb71dfd15b648c9d1b05d14c32d32972003'})
  SET c.content = 'Battle of the Axona had participant Belgae'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107414Z'
MERGE (subj:Entity {qid: 'Q1260622'})
MERGE (obj:Entity {qid: 'Q337104'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '5a828e16dc2055145c228085b43a0e6636cf52ed91cc4adc8783e3d424282547'})
  SET c.content = 'Battle of Delos had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107447Z'
MERGE (subj:Entity {qid: 'Q130857859'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c17a0d550e00de0a08f1e59d34ed53d9f07b79adff762e5ff1b2451add818918'})
  SET c.content = 'Battle of Uskana had participant Illyrians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107480Z'
MERGE (subj:Entity {qid: 'Q133480177'})
MERGE (obj:Entity {qid: 'Q146715'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c1eb1582b8a53141f80fef898e585ecfb0057efd5e0932c8b2bf7ebacdc2ea9f'})
  SET c.content = 'Battle of Halys had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107508Z'
MERGE (subj:Entity {qid: 'Q17277303'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '766fad66695fbe25964aeab8991d3f139cd592efcc4a79ecc32d7480132bb5f3'})
  SET c.content = 'Battle of Halys had participant Kingdom of Pontus'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107540Z'
MERGE (subj:Entity {qid: 'Q17277303'})
MERGE (obj:Entity {qid: 'Q7380487'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '75d91b3889f68171004c8a72365486f149ecf8ce34123329d4a784ec861a0502'})
  SET c.content = 'Gallic War had participant Julius Caesar'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107570Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q1048'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '505698c25eab459322f1149bb2fe70db215bec92c125f710ae4287b0b4b4381e'})
  SET c.content = 'Gallic War had participant Aquitani'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107599Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q1255605'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c0fe19feb3e6da174b09a0a7d2240a9b7027cb4764335095ba740b9e21883b7a'})
  SET c.content = 'Gallic War had participant Gauls'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107628Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q273854'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '67f970ce757c285f36e030db2d0db95cb8fe45a5a855fa0c833b582590f819ac'})
  SET c.content = 'Gallic War had participant Celtic Britons'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107658Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q849967'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '0909798ff87371075943bcc44f978c0b32ae2e1facd48d0325ae5f22b9312aa9'})
  SET c.content = 'Gallic War had participant Belgae'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107687Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q337104'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'aad5617b32ff56a2e2c640132fcaa0e2154e48ca18a153289a956c2994fec317'})
  SET c.content = 'Gallic War had participant Iberians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107715Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q190992'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fe8c4fe648d5528cf95857ff35181da342823e61605a09ec7a0972deeda7bb33'})
  SET c.content = 'Gallic War had participant Germanic people'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107744Z'
MERGE (subj:Entity {qid: 'Q202161'})
MERGE (obj:Entity {qid: 'Q22633'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '365dd16f38dfcf1580cfbf42082a3da6523d5de4df9803e0a9998ca8e2fed519'})
  SET c.content = 'Battle of Petilia had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107774Z'
MERGE (subj:Entity {qid: 'Q24045885'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd29123afd531b487728c47df8386a668c869762bf133fc4dea4e238d149a57e4'})
  SET c.content = 'Ambiorix\'s Revolt had participant Roman Republic'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107803Z'
MERGE (subj:Entity {qid: 'Q2505574'})
MERGE (obj:Entity {qid: 'Q17167'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6b9965f6ef77f6fd79811b7e5c5cbedfc7acd7d2b611d768e11b26ff17f3b7ab'})
  SET c.content = 'Battle of Chaeronea had participant Arcadians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107834Z'
MERGE (subj:Entity {qid: 'Q25414978'})
MERGE (obj:Entity {qid: 'Q11906401'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7ea2d5ce3052aaf17e252eb474f0dcbdf874a0821092e5970583ae637023b6dd'})
  SET c.content = 'Battle of the Douro had participant Lusitanians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107864Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q837549'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd15ed2114ac3ca964506fbb0e3e50f9c4ec5b1b2f56835c4106ce748b78da758'})
  SET c.content = 'Battle of the Douro had participant Gallaeci'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107895Z'
MERGE (subj:Entity {qid: 'Q25421066'})
MERGE (obj:Entity {qid: 'Q1007723'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5ec93531019b18e63ecf19d5a30b7f1c96bb65517824c81dfd769349b95d021'})
  SET c.content = 'Battle of the Granicus had participant Kingdom of Pontus'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107928Z'
MERGE (subj:Entity {qid: 'Q28665781'})
MERGE (obj:Entity {qid: 'Q7380487'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b8d32fb0095298431566c65b3bfa71a7db7990f775fde3384123c6484766acc4'})
  SET c.content = 'Sertorian War had participant Kingdom of Mauretania'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107960Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q31723'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ff90157ae6dc962e3e86944475792722edba362a51c1304b3b4c5367061650ab'})
  SET c.content = 'Sertorian War had participant Cilician pirates'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.107992Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q1741306'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1fd713c197fd8e7e510abde9d5386d396537aebd95ca4d9e29758ab4cfaae312'})
  SET c.content = 'Sertorian War had participant Iberians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108026Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q190992'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'f709111beb9fd1c8880f3772f51db73c2a85835af0960c9282f6c15aa8d2ad84'})
  SET c.content = 'Sertorian War had participant Celtiberians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108060Z'
MERGE (subj:Entity {qid: 'Q3778726'})
MERGE (obj:Entity {qid: 'Q5011445'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '3d77650730802164eab5e865833e6bc6193e2d0e81782eaa6a5142e16b0671d7'})
  SET c.content = 'Pyrrhic War had participant Acarnania'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108091Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q416070'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9abc082f7a070879409795c915148d58ae5ba0cf045fc956b5543b44368554b9'})
  SET c.content = 'Pyrrhic War had participant Epirus'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108122Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q11266977'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '8256e1e7ab475e1da12610ec1ab958afbca7611a43f54b869256e5fd8b99bbdb'})
  SET c.content = 'Pyrrhic War had participant Daunians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108152Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q1172997'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '857096caa26d20877f5d7281e483caeb0027dbdd1f951235b152f2fbb124c357'})
  SET c.content = 'Pyrrhic War had participant Bruttii'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108184Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q994847'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '1c47b9b530d5630d2f6544d60bcd78be4558687708b4ca07fa74bc8cd0e045dc'})
  SET c.content = 'Pyrrhic War had participant Taranto'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108213Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q13498'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '991bc4b07084736ec66e4e0794f35f4979af2ab56a5158c55fcfaa48f0e77f6f'})
  SET c.content = 'Pyrrhic War had participant Umbri'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108241Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q389236'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '650eb8f4be4980fe44ad6d25e568a6d658ecc810c28783877abf00990372ede3'})
  SET c.content = 'Pyrrhic War had participant Thessaly'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108278Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q166919'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '2c05e0aeef68e0d807b3f3789126375ffcc1d5ddf0b760b2bdd46a687a42bfa9'})
  SET c.content = 'Pyrrhic War had participant Lucanians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108314Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q1264391'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '99d8d97ae7a01854a0c19124e017bb7a3d229306b45e1736e9b6411996b492d8'})
  SET c.content = 'Pyrrhic War had participant Samnites'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108345Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q500272'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7b77a217e6775538a3c74aa0481020b68351bbda1b1a1c7882bc3bb32ec5ec13'})
  SET c.content = 'Pyrrhic War had participant Aetolia'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108376Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q26857'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c21d500961cb861afc62f4f3a5f34770d3701a379db0df42a3b2a8c46904bba6'})
  SET c.content = 'Pyrrhic War had participant Paeligni'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108407Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q941821'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '70bef9dab8f8775158cfc6de2a8e59816786bb455cdbc9087a1202a9d7c96cae'})
  SET c.content = 'Pyrrhic War had participant Carthage'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108440Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q6343'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6a8242b27af6e19552858b3fef40756eeceae7c4aec9f026bd8fed72f5c09b30'})
  SET c.content = 'Pyrrhic War had participant Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108473Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'b0d5ddf1afed516483a661fa27c9d41c2f16f96bb751c1cff5a2e91eb80af557'})
  SET c.content = 'Pyrrhic War had participant Marrucini'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108519Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q1165749'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '7394386f9c410811bc47cf375c8806502e73f02a27be3857c496e58cd7d3772d'})
  SET c.content = 'Pyrrhic War had participant Marsi'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108554Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q1265446'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fd6b37707386206429db639071dc8de6c029dac273bb774681b7d3192a1f5b6c'})
  SET c.content = 'Pyrrhic War had participant Athamanians'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108586Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q754691'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '441d7824096fc4803545c859e5c1c810ad0964dba48eba7d7ac533953657c341'})
  SET c.content = 'Pyrrhic War had participant Frentani'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108621Z'
MERGE (subj:Entity {qid: 'Q596373'})
MERGE (obj:Entity {qid: 'Q2479252'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '27abb5e5dac417c1aed885a070b343ce59167cb37f9ec26efd00c5ba983983af'})
  SET c.content = 'Social War of 91-87 BCE had participant Samnium'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108658Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q463459'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '62fdd733b0f1c3b9c3beaacb24b90408a9bf4283ffa1815c2fab99eb0153bef3'})
  SET c.content = 'Social War of 91-87 BCE had participant Marrucini'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108692Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q1165749'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'ba5498f962ed46574fff889736979b3de9b078d478b6b6f86e593f25c402f694'})
  SET c.content = 'Social War of 91-87 BCE had participant Picentes'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108728Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q1754393'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '4e771b9f83d39171bf7ae7250344c1a9e026d0090bb7e89e38dc0b4e384fbea4'})
  SET c.content = 'Social War of 91-87 BCE had participant Marsi'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108763Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q1265446'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '6be3e20152b185f5a648b905c56dab83c7112fb44e51a1f1d2363efe5242bcdb'})
  SET c.content = 'Social War of 91-87 BCE had participant Socii'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108801Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q733149'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'fafac50d8f04d8a37d0aebb4ced58c7616adbab3090d94c81303a8c0cf8c58b6'})
  SET c.content = 'Social War of 91-87 BCE had participant Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108836Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '9651bb2a3a341a30e3406e56adcdfa6b606eda4ce01115277b0b04efd3b5c8dc'})
  SET c.content = 'Social War of 91-87 BCE had participant Lucania'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108871Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q1131978'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '48b1fe8129b1dd3fd07289b9960a7fe0064e3c4c0d708dd6056ac09142329dd1'})
  SET c.content = 'Social War of 91-87 BCE had participant Paeligni'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108904Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q941821'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'd79fcd0a41d6c56e32a469448d5fcfea9381e5972fa580623dd64ededde70694'})
  SET c.content = 'Social War of 91-87 BCE had participant Venosa'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108940Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q52691'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'a5a451dd1d2b40964ece59b583edb8ce0d0d1c1d5db5640f1cde60cf94e90429'})
  SET c.content = 'Social War of 91-87 BCE had participant Iapyges'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.108974Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q841576'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '78abea81d2617103e8f133a1ad80c0ba706d121f62fd3c9ba03abca18f90454f'})
  SET c.content = 'Social War of 91-87 BCE had participant Hirpini'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.109009Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q1036791'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '15b8bc5a65f25e93511e66665b2ae4a18770927c34566347db5e86f323d3ed26'})
  SET c.content = 'Social War of 91-87 BCE had participant Pompeii'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.109044Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q43332'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c90c14933f4e6ac3e24a298ece63f145e4520ce81c7f86b6deb595049d1b217c'})
  SET c.content = 'Social War of 91-87 BCE had participant Vestini'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.109082Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q2341546'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: 'c8a23db68392247c15c47ca74719be6406b8cf3af52a5b3bf75d5cd9f3032c32'})
  SET c.content = 'Social War of 91-87 BCE had participant Frentani'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.109121Z'
MERGE (subj:Entity {qid: 'Q677316'})
MERGE (obj:Entity {qid: 'Q2479252'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '85db18931a426912097db2336062ddfe75b02574ce9c26f2f662d94861404b0f'})
  SET c.content = 'Macedonian Wars had participant Ancient Rome'
  SET c.source_id = 'wikidata:Q17167:P710'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.109159Z'
MERGE (subj:Entity {qid: 'Q75813'})
MERGE (obj:Entity {qid: 'Q1747689'})
MERGE (subj)-[r:HAD_PARTICIPANT]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P710'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)

MERGE (c:Claim {cipher: '75be97acd8e55a9d2d1d4ace8916e2a3b3635ee38f39d709b554bde1b2265c46'})
  SET c.content = 'Caesar\'s Civil War was caused by crossing the Rubicon'
  SET c.source_id = 'wikidata:Q17167:P828'
  SET c.created_by = 'wikidata_harvester_001'
  SET c.created_at = '2026-07-14T22:30:23.109490Z'
MERGE (subj:Entity {qid: 'Q1238338'})
MERGE (obj:Entity {qid: 'Q25238182'})
MERGE (subj)-[r:CAUSED]->(obj)
  SET r.confidence = 0.54
  SET r.source_id = 'wikidata:P828'
MERGE (c)-[:ASSERTS_RELATIONSHIP]->(r)
