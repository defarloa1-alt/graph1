// The Battle of Actium as each source tells it: its depicted events (23 §2, 29),
// with the source's time words, what each follows from, and who took part.
// `passage` is where the source first narrates the event: narration order, shown
// for orientation only; the order of events comes from `after` and `time`.
MATCH (battle:Entity {id: 'chr:entity:battle-of-actium'})
MATCH (e:Entity {kind: 'Event'})
WHERE e.id STARTS WITH 'chr:entity:depicted:' AND e.status <> 'deprecated'
// the Work is in the id: chr:entity:depicted:<work>:<event>
WITH battle, e, 'chr:entity:' + split(e.id, ':')[3] AS workId
MATCH (w:Entity {id: workId})
OPTIONAL MATCH (m:Annotation {kind: 'entity-mention'})-[:CONCERNS]->(e)
OPTIONAL MATCH (m)-[:ANNOTATES]->(o:SourceObservation)
WITH battle, e, w, min(o.shortLabel) AS passage
OPTIONAL MATCH (e)<-[:ASSERTION_SUBJECT]-(t:Assertion {predicate: 'occurred'})
WHERE NOT t.status IN ['rejected', 'superseded']
OPTIONAL MATCH (e)<-[:ASSERTION_OBJECT]-(link:Assertion)-[:ASSERTION_SUBJECT]->(before:Entity)
WHERE link.predicate = 'happenedBefore' AND NOT link.status IN ['rejected', 'superseded']
OPTIONAL MATCH (e)<-[:ASSERTION_SUBJECT]-(cause:Assertion {predicate: 'triggeredBy'})-[:ASSERTION_OBJECT]->(trigger:Entity)
WHERE NOT cause.status IN ['rejected', 'superseded']
OPTIONAL MATCH (e)<-[:ASSERTION_OBJECT]-(p:Assertion {predicate: 'participatedIn'})-[:ASSERTION_SUBJECT]->(who:Entity)
WHERE NOT p.status IN ['rejected', 'superseded']
OPTIONAL MATCH (e)<-[:ASSERTION_SUBJECT]-(part:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(battle)
WITH w, e, passage, collect(DISTINCT t.timeSourceExpression) AS time,
     collect(DISTINCT coalesce(before.shortLabel, before.label)) AS after,
     collect(DISTINCT coalesce(trigger.shortLabel, trigger.label)) AS triggeredBy,
     collect(DISTINCT who.label) AS who, count(part) > 0 AS duringBattle,
     split(split(coalesce(passage, ''), ' ')[-1], '.') AS ref
RETURN w.label AS source, passage, coalesce(e.shortLabel, e.label) AS event,
       CASE WHEN duringBattle THEN 'during' ELSE 'around' END AS battle,
       time, after, triggeredBy, who
ORDER BY source, toInteger(ref[0]), toInteger(ref[1]), coalesce(toInteger(ref[2]), 0), event
