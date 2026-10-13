// Explorer view in Neo4j Desktop (Query / Browser): the closest the database can show to what
// a user of the explorer sees (26-UI-DATA-CONTRACT.md). A smoke view, not the product.
//
// What the user sees, and how these queries approximate it:
//   - people, places, events, works, groups, offices, polities: Entity nodes
//   - one line per fact (every source's claim of it drawn once): each fact is stored as an
//     Assertion node between its two entities, so one Assertion per fact is returned, the one
//     best placed (accepted before proposed, our own statement before a source's)
//   - proposed and accepted together, never rejected, superseded, or deprecated (25 decision 2)
//   - historical relations only: no SourceObservation, AuthorityRecord, Proposal, Year,
//     or Annotation on the canvas, and no bibliography (describedBy) or housekeeping (distinctFrom)
//   - facts with no object (born, died, occurred) belong on the node's card, not on the canvas
//
// Captions: run the :style block at the end once (Browser), so an Entity shows its label and a
// fact node shows its predicate. Browser colours by label, not by kind; in Explore (Bloom) add a
// rule-based colour on Entity.kind.
//
// Parameters: set before queries 2-4, for example
//   :param focus => 'Mark Antony'
//   :param year => -31


// 1. The canvas: every live fact, one line each ------------------------------------------------
MATCH (s:Entity)<-[:ASSERTION_SUBJECT]-(a:Assertion)-[:ASSERTION_OBJECT]->(o:Entity)
WHERE a.status IN ['accepted', 'proposed']
  AND NOT a.predicate IN ['describedBy', 'distinctFrom']
  AND coalesce(s.status, '') <> 'deprecated' AND coalesce(o.status, '') <> 'deprecated'
WITH s, o, a ORDER BY CASE a.status WHEN 'accepted' THEN 0 ELSE 1 END, coalesce(a.mode, 'asserted'), a.id
WITH s, o, a.predicate AS predicate, coalesce(a.category, 'factual') AS category, head(collect(a)) AS fact
MATCH path = (s)<-[:ASSERTION_SUBJECT]-(fact)-[:ASSERTION_OBJECT]->(o)
RETURN path;


// 2. Standing at the centre: one person (or any entity) and the facts that touch them -----------
MATCH (focus:Entity {label: $focus})
MATCH (s:Entity)<-[:ASSERTION_SUBJECT]-(a:Assertion)-[:ASSERTION_OBJECT]->(o:Entity)
WHERE (s = focus OR o = focus)
  AND a.status IN ['accepted', 'proposed']
  AND NOT a.predicate IN ['describedBy', 'distinctFrom']
  AND coalesce(s.status, '') <> 'deprecated' AND coalesce(o.status, '') <> 'deprecated'
WITH s, o, a ORDER BY CASE a.status WHEN 'accepted' THEN 0 ELSE 1 END, coalesce(a.mode, 'asserted'), a.id
WITH s, o, a.predicate AS predicate, coalesce(a.category, 'factual') AS category, head(collect(a)) AS fact
MATCH path = (s)<-[:ASSERTION_SUBJECT]-(fact)-[:ASSERTION_OBJECT]->(o)
RETURN path;


// 3. The card beside it: what the canvas leaves out for the focus -------------------------------
// facts with no object (born, died, occurred), with each voice's time; and passages of note.
MATCH (focus:Entity {label: $focus})
OPTIONAL MATCH (focus)<-[:ASSERTION_SUBJECT]-(u:Assertion)
WHERE u.status IN ['accepted', 'proposed'] AND NOT (u)-[:ASSERTION_OBJECT]->()
OPTIONAL MATCH (u)-[:ATTRIBUTED_TO]->(work:Entity)
WITH focus, collect(DISTINCT CASE WHEN u IS NULL THEN null ELSE
       u.predicate + ' ' + coalesce(u.timeSourceExpression, 'undated') + ' (' + u.status +
       coalesce(', according to ' + work.label, '') + ')' END) AS facts
OPTIONAL MATCH (note:Annotation)-[:CONCERNS]->(focus)
WHERE coalesce(note.status, '') <> 'dismissed'
RETURN focus.label AS label, focus.kind AS kind, focus.status AS status, focus.description AS description,
       facts, collect(note.noteType + ': ' + note.note)[..15] AS notesOfPassages;


// 4. Elsewhere in the same year: the synchronism around one Year --------------------------------
// facts dated to the year, with whatever they connect.
MATCH (:Year {year: $year})<-[:IN_YEAR]-(a:Assertion)-[:ASSERTION_SUBJECT]->(s:Entity)
WHERE a.status IN ['accepted', 'proposed'] AND coalesce(s.status, '') <> 'deprecated'
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(o:Entity)
WITH s, o, a ORDER BY CASE a.status WHEN 'accepted' THEN 0 ELSE 1 END, a.id
WITH s, o, a.predicate AS predicate, head(collect(a)) AS fact
MATCH path = (s)<-[:ASSERTION_SUBJECT]-(fact)
OPTIONAL MATCH objectPath = (fact)-[:ASSERTION_OBJECT]->(o)
RETURN path, objectPath;


// 5. With APOC installed (Neo4j Desktop: the database's Plugins tab): true lines -----------------
// Each fact becomes one virtual relationship from subject to object, named by its predicate
// and carrying status, mode, category, and how many claims (voices) stand behind it. Nothing is
// written. Not run here: the local database has no APOC.
MATCH (s:Entity)<-[:ASSERTION_SUBJECT]-(a:Assertion)-[:ASSERTION_OBJECT]->(o:Entity)
WHERE a.status IN ['accepted', 'proposed']
  AND NOT a.predicate IN ['describedBy', 'distinctFrom']
  AND coalesce(s.status, '') <> 'deprecated' AND coalesce(o.status, '') <> 'deprecated'
WITH s, o, a.predicate AS predicate, coalesce(a.category, 'factual') AS category, collect(a) AS claims
WITH s, o, predicate, category, claims,
     CASE WHEN any(c IN claims WHERE c.status = 'accepted') THEN 'accepted' ELSE 'proposed' END AS status,
     CASE WHEN any(c IN claims WHERE coalesce(c.mode, 'asserted') = 'asserted') THEN 'asserted' ELSE 'attributed' END AS mode
RETURN s, o, apoc.create.vRelationship(s, predicate, {status: status, mode: mode, category: category,
                                                      voices: size(claims)}, o) AS fact;


// Browser style (paste once into the Browser command line) --------------------------------------
// :style node.Entity { caption: '{label}'; diameter: 50px; }
//        node.Assertion { caption: '{predicate}'; diameter: 18px; color: #DDDDDD; border-color: #999999; }
//        relationship { caption: ''; }
