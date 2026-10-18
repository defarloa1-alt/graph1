// Everything the graph holds about one event, from a summary down to pictures (2026-10-18).
// Neo4j Browser or Desktop, read-only. Set once:
//   :param event => 'chr:entity:battle-of-actium'
//   :param phase => 'meaning-memory'        (query 4: any phase key)
//   :param curator => 'Tony DeFarlo'        (query 8)
// Then run any query below on its own. Proposed and accepted content are shown together;
// rejected and superseded claims are left out (25 decision 2). The Browser draws about 300 nodes
// by default (:config initialNodeDisplay: 1000 raises it); the tables have no such limit.


// 1. The summary: what the graph holds about the event, counted --------------------------------
// One row per kind of thing, with how many are accepted and how many proposed.
MATCH (ev:Entity {id: $event})
CALL (ev) {
  MATCH (a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]->(ev)
  WHERE NOT a.status IN ['rejected', 'superseded']
  RETURN 'claims on the event' AS what, count(a) AS total, sum(CASE a.status WHEN 'accepted' THEN 1 ELSE 0 END) AS accepted
  UNION ALL
  MATCH (ph:Entity)-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ev)
  WHERE ph.id STARTS WITH 'chr:entity:phase:'
  RETURN 'phases' AS what, count(DISTINCT ph) AS total, sum(CASE ph.status WHEN 'provisional' THEN 1 ELSE 0 END) AS accepted
  UNION ALL
  MATCH (e:Entity {kind: 'Event'})<-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph:Entity)
        -[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ev)
  WHERE ph.id STARTS WITH 'chr:entity:phase:'
  RETURN 'depicted events placed in a phase' AS what, count(DISTINCT e) AS total, 0 AS accepted
  UNION ALL
  MATCH (n:Entity)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(ev)
  WHERE n <> ev AND NOT a.status IN ['rejected', 'superseded']
  RETURN 'entities linked to it by a claim' AS what, count(DISTINCT n) AS total,
         count(DISTINCT CASE WHEN n.status IN ['provisional', 'resolved'] THEN n END) AS accepted
  UNION ALL
  MATCH (w:Entity {kind: 'Work'})<-[:ATTRIBUTED_TO]-(a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(x:Entity)
  WHERE NOT a.status IN ['rejected', 'superseded']
    AND (x = ev OR EXISTS { (x)-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph:Entity)
                            -[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ev) })
  RETURN 'works that speak of it (attributed claims)' AS what, count(DISTINCT w) AS total, 0 AS accepted
  UNION ALL
  MATCH (n:Annotation)-[:CONCERNS]->(ev)
  RETURN 'notes and passages of note on it' AS what, count(n) AS total, sum(CASE n.status WHEN 'endorsed' THEN 1 ELSE 0 END) AS accepted
  UNION ALL
  MATCH (ev)-[:HAS_AUTHORITY_RECORD]->(r:AuthorityRecord)
  RETURN 'authority records (Wikidata, LCSH, ...)' AS what, count(r) AS total, count(r) AS accepted
}
RETURN what, total, accepted;


// 2. The event's own facts: one row per claim with the event as subject, object, or context -------
// Sentence, status, whose voice, and the words that support it (pending or accepted).
MATCH (a:Assertion)-[role:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]->(:Entity {id: $event})
WHERE NOT a.status IN ['rejected', 'superseded']
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity)
OPTIONAL MATCH (a)-[s:SUPPORTED_BY]->(:SourceObservation)
OPTIONAL MATCH (:Proposal)-[:PROPOSES]->(a)
WITH a, type(role) AS as, w, collect(DISTINCT left(s.quotation, 90))[..1] AS quote
RETURN a.predicate AS predicate, as, a.label AS claim, a.status AS status,
       coalesce(w.label, 'Chrystallum (asserted)') AS voice, a.category AS category, quote
ORDER BY predicate, voice;


// 3. Picture: the event, its phases, and the people, forces, and places tied to it ------------------
// Claims are drawn as small Assertion nodes between Entities, as in explorer-view.cypher.
MATCH p = (n:Entity)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(:Entity {id: $event})
WHERE NOT a.status IN ['rejected', 'superseded']
  AND (n.kind IN ['Person', 'Group', 'Place', 'Polity', 'Concept', 'Work'] OR n.id STARTS WITH 'chr:entity:phase:')
RETURN p;


// 4. Picture: one phase in full (set :param phase => 'meaning-memory', or any key) --------------------
// The phase, every depicted event placed in it, and the Work each comes from.
MATCH (ph:Entity) WHERE ph.id STARTS WITH 'chr:entity:phase:' AND ph.id ENDS WITH ':' + $phase
MATCH p = (e:Entity)<-[:ASSERTION_SUBJECT]-(pl:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph)
WHERE NOT pl.status IN ['rejected', 'superseded']
OPTIONAL MATCH q = (e)<-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'occurred'})
RETURN p, q;


// 5. The sources: each Work behind the event, how many passages and claims it gives -----------------
MATCH (w:Entity {kind: 'Work'})<-[:IN_WORK]-(o:SourceObservation)
WHERE EXISTS { (o)<-[:SUPPORTED_BY|PROPOSES_EVIDENCE]-()-[:PROPOSES*0..1]->(a:Assertion)
               WHERE EXISTS { (a)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]->(:Entity {id: $event}) }
                  OR EXISTS { (a)-[:ASSERTION_SUBJECT]->(:Entity)<-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})
                              -[:ASSERTION_OBJECT]->(:Entity)-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})
                              -[:ASSERTION_OBJECT]->(:Entity {id: $event}) } }
   OR EXISTS { (o)<-[:ANNOTATES]-(:Annotation)-[:CONCERNS]->(:Entity {id: $event}) }
WITH w, count(DISTINCT o) AS passages
OPTIONAL MATCH (a:Assertion)-[:ATTRIBUTED_TO]->(w)
WHERE NOT a.status IN ['rejected', 'superseded']
RETURN w.label AS work, w.form AS form, w.status AS status, passages,
       count(DISTINCT a) AS claimsAttributed
ORDER BY passages DESC;


// 6. The timeline: what is dated, in which year (the event and its parts and their sources) -----------
MATCH (a:Assertion {predicate: 'occurred'})-[:ASSERTION_SUBJECT]->(e:Entity)
WHERE NOT a.status IN ['rejected', 'superseded']
  AND (e.id = $event OR EXISTS { (e)<-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT*1..1]->(x:Entity)
                                  WHERE x.id = $event OR EXISTS { (x)<-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})
                                                                 -[:ASSERTION_OBJECT]->(:Entity {id: $event}) } })
OPTIONAL MATCH (a)-[y:IN_YEAR]->(yr:Year)
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(w:Entity)
RETURN min(yr.year) AS year, collect(DISTINCT yr.label)[0] AS label, e.label AS event,
       a.timeSourceExpression AS inTheSourcesWords, coalesce(w.label, 'Chrystallum') AS voice, a.status AS status
ORDER BY year, event;


// 7. Notes: every Annotation on the event or on anything linked to it by a claim ----------------------
// Passages of note from the readers, and the curator's own notes from Obsidian (kind note, image-note).
MATCH (ev:Entity {id: $event})
MATCH (n:Annotation)-[:CONCERNS]->(t:Entity)
WHERE t = ev OR EXISTS { (t)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(a:Assertion)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(ev)
                          WHERE NOT a.status IN ['rejected', 'superseded'] }
OPTIONAL MATCH (n)-[an:ANNOTATES]->(o:SourceObservation)
RETURN n.kind AS kind, n.noteType AS type, n.label AS note, n.author AS author, n.status AS status,
       collect(DISTINCT t.label) AS concerns, left(coalesce(an.quotation, n.note), 120) AS words
ORDER BY kind, author, note;


// 8. The curator's work: each of the curator's notes and images, and what was proposed from them ----
// Set :param curator => 'Tony DeFarlo' (the author the sync records on the curator's notes).
MATCH (n:Annotation) WHERE n.kind IN ['note', 'image-note'] OR n.author = $curator
OPTIONAL MATCH (n)-[:ANNOTATES]->(o:SourceObservation)
OPTIONAL MATCH (n)-[:CONCERNS]->(t:Entity)
WITH n, o, collect(DISTINCT t.label) AS concerns
OPTIONAL MATCH (p:Proposal)-[:PROPOSES_EVIDENCE]->(o)
OPTIONAL MATCH (p)-[:PROPOSES]->(a:Assertion)
RETURN n.kind AS kind, coalesce(o.workTitle + ', ' + o.locator, o.depicts) AS source,
       left(o.passageText, 80) AS words, concerns, collect(DISTINCT a.label) AS claimsFromIt
ORDER BY source;


// 9. Identity and place: the event's authority records, and its places in the gazetteer ----------------
MATCH (ev:Entity {id: $event})
OPTIONAL MATCH (ev)-[l:HAS_AUTHORITY_RECORD]->(r:AuthorityRecord)
WITH ev, collect(r.system + ' ' + r.identifier + ': ' + r.label) AS records
OPTIONAL MATCH (ev)<-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'occurredAt'})-[:ASSERTION_OBJECT]->(pl:Entity)
OPTIONAL MATCH (pl)-[:AT_LOCATION]->(loc:Location)
RETURN records, collect(DISTINCT pl.label) AS places, collect(DISTINCT loc.system + ' ' + loc.identifier + ' ' + loc.label) AS gazetteer;


// 10. The review queue for the event: what awaits the curator, by who proposed it ----------------------
MATCH (p:Proposal {status: 'submitted'})-[:PROPOSES]->(a:Assertion)
WHERE EXISTS { (a)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ASSERTION_CONTEXT]->(:Entity {id: $event}) }
   OR EXISTS { (a)-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(:Entity)<-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})
               -[:ASSERTION_OBJECT]->(:Entity)-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(:Entity {id: $event}) }
   OR EXISTS { (a)-[:ASSERTION_OBJECT]->(:Entity)-[:ASSERTION_SUBJECT]-(:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(:Entity {id: $event}) }
RETURN p.createdBy AS proposedBy, a.predicate AS predicate, count(*) AS waiting
ORDER BY proposedBy, waiting DESC;


// Browser style (paste once into the Browser command line) -----------------------------------------
// :style node.Entity { caption: '{label}'; diameter: 55px; }
//        node.Assertion { caption: '{predicate}'; diameter: 18px; color: #DDDDDD; border-color: #999999; }
//        relationship { caption: ''; }
