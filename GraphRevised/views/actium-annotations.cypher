// Annotations related to the Battle of Actium, in reading order.
// Related = concerns the battle, or anything tied to it by a live claim
// (participants, forces, commanders, places, concepts).
MATCH (b:Entity {id: 'chr:entity:battle-of-actium'})
OPTIONAL MATCH (b)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]-(x:Assertion)
               -[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(e:Entity)
WHERE NOT x.status IN ['rejected', 'superseded']
WITH b, collect(DISTINCT e) AS linked
WITH linked + [b] AS scope
MATCH (a:Annotation)-[:CONCERNS]->(s:Entity)
WHERE s IN scope AND a.status <> 'dismissed'
WITH DISTINCT a
OPTIONAL MATCH (a)-[an:ANNOTATES]->(o:SourceObservation)
OPTIONAL MATCH (o)-[:IN_WORK]->(w:Entity)
OPTIONAL MATCH (a)-[:CONCERNS]->(c:Entity)
WITH a, an, o, w, collect(DISTINCT c.label) AS concerns
// claims drawn from the same passage, to see notes beside facts
OPTIONAL MATCH (o)<-[:SUPPORTED_BY|PROPOSES_EVIDENCE]-(src)
OPTIONAL MATCH (src)-[:PROPOSES]->(pa:Assertion)
WITH a, an, o, w, concerns,
     collect(DISTINCT CASE WHEN src:Assertion THEN src.label ELSE pa.label END) AS claimsFromPassage
WITH a, an, o, w, concerns, [l IN claimsFromPassage WHERE l IS NOT NULL] AS claimsFromPassage,
     split(split(coalesce(o.shortLabel, ''), ' ')[-1], '.') AS ref
RETURN coalesce(w.label, '(no passage)')      AS work,
       o.shortLabel                            AS passage,
       a.noteType                              AS type,
       a.kind                                  AS kind,
       a.note                                  AS note,
       an.quotation                            AS quotation,
       concerns,
       claimsFromPassage,
       a.status                                AS status
ORDER BY work, toInteger(ref[0]), toInteger(ref[1]), type
