// Where we are: the curator's review view of the Battle of Actium after the phases (2026-10-16).
// Neo4j Desktop, Query or Browser. Read-only. Proposed and accepted are shown together; rejected and
// superseded claims are left out (25 decision 2).
//
// Set once before the queries:
//   :param event => 'chr:entity:battle-of-actium'
//   :param phase => 'breakout'
//
// The graphs (1, 2) draw each claim as a small Assertion node between two Entities, as
// explorer-view.cypher does: Entity captions are labels, Assertion captions predicates. Run the
// :style block at the end once. Phases read "(Chrystallum)", depicted events "(Plutarch)" and so on.
// The tables (3-5) are the review lists.


// 1. The spine: the battle, its 11 phases, and a few of each phase's events --------------------
// Each phase is shown with the first event from each of its three best-represented sources.
MATCH spine = (ph:Entity)<-[:ASSERTION_SUBJECT]-(a:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(:Entity {id: $event})
WHERE ph.id STARTS WITH 'chr:entity:phase:' AND NOT a.status IN ['rejected', 'superseded']
MATCH (e:Entity)<-[:ASSERTION_SUBJECT]-(pl:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph)
WHERE NOT pl.status IN ['rejected', 'superseded']
WITH spine, ph, split(e.id, ':')[3] AS work, e, pl ORDER BY e.id
WITH spine, ph, work, collect({e: e, pl: pl})[0] AS first, count(*) AS placed
ORDER BY placed DESC
WITH spine, ph, collect(first)[..3] AS shown
UNWIND shown AS s
WITH spine, ph, s.e AS e, s.pl AS pl
MATCH member = (e)<-[:ASSERTION_SUBJECT]-(pl)-[:ASSERTION_OBJECT]->(ph)
RETURN spine, member;


// 2. One phase in full: every event placed in it, each tied to the Work that depicts it --------
// The Work hubs show at a glance how the sources share the phase.
MATCH (ph:Entity)
WHERE ph.id STARTS WITH 'chr:entity:phase:' AND ph.id ENDS WITH ':' + $phase
MATCH member = (e:Entity)<-[:ASSERTION_SUBJECT]-(pl:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph)
WHERE NOT pl.status IN ['rejected', 'superseded']
MATCH (e)<-[:ASSERTION_SUBJECT]-(c:Assertion)-[:ATTRIBUTED_TO]->(w:Entity)
WITH member, e, w, head(collect(c)) AS claim
MATCH voice = (e)<-[:ASSERTION_SUBJECT]-(claim)-[:ATTRIBUTED_TO]->(w)
RETURN member, voice;


// 3. The phases to approve, in the spine's order -----------------------------------------------
// One row per phase: its review state, how many events were placed and from which sources, and the
// agent's one-line description. Approve the phases (their partOf claims) before the placements.
UNWIND range(0, 10) AS position
WITH position, ['road-to-war', 'isolation', 'attrition', 'council', 'deployment', 'engagement', 'breakout',
                'antony-follows', 'fleet-defeat', 'army-surrender', 'meaning-memory'][position] AS key
MATCH (ph:Entity) WHERE ph.id STARTS WITH 'chr:entity:phase:' AND ph.id ENDS WITH ':' + key
MATCH (ph)<-[:ASSERTION_SUBJECT]-(a:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(:Entity {id: $event})
MATCH (p:Proposal)-[:PROPOSES]->(a)
OPTIONAL MATCH (e:Entity)<-[:ASSERTION_SUBJECT]-(pl:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph)
WHERE NOT pl.status IN ['rejected', 'superseded']
OPTIONAL MATCH (w:Entity {id: 'chr:entity:' + split(e.id, ':')[3]})
WITH position, ph, a, p, coalesce(w.label, '?') AS source, count(e) AS n,
     sum(CASE pl.status WHEN 'accepted' THEN 1 ELSE 0 END) AS accepted
ORDER BY n DESC
WITH position, ph, a, p, sum(n) AS placed, sum(accepted) AS placementsAccepted,
     collect(split(source, ',')[0] + ' ' + n) AS bySource
RETURN position + 1 AS `#`, ph.shortLabel AS phase, ph.status AS entity, a.status AS claim, p.status AS proposal,
       placed, placementsAccepted, bySource, ph.description AS description
ORDER BY `#`;


// 4. What is not in any phase ----------------------------------------------------------------
// Depicted events of the battle's sources that no live placement puts in a phase: those the agent
// judged outside the battle, and those of creative Works, which cannot be placed (handoff rule 15).
MATCH (e:Entity {kind: 'Event'})
WHERE e.id STARTS WITH 'chr:entity:depicted:' AND e.status <> 'deprecated'
  AND NOT EXISTS {
    MATCH (e)<-[:ASSERTION_SUBJECT]-(pl:Assertion {predicate: 'partOf'})-[:ASSERTION_OBJECT]->(ph:Entity)
    WHERE ph.id STARTS WITH 'chr:entity:phase:' AND NOT pl.status IN ['rejected', 'superseded'] }
MATCH (w:Entity {id: 'chr:entity:' + split(e.id, ':')[3]})
RETURN w.label AS source, w.form AS form,
       CASE WHEN w.form IN ['poem', 'play', 'novel', 'short story', 'film', 'television series', 'painting',
                          'sculpture', 'opera', 'song', 'video game'] THEN 'creative: never placed'
            ELSE 'judged outside the phases' END AS why,
       coalesce(e.shortLabel, e.label) AS event
ORDER BY why, source, event;


// 5. The review queue as a whole ----------------------------------------------------------------
// Submitted Proposals by who made them and what they propose: where the curator's work lies.
MATCH (p:Proposal)-[:PROPOSES]->(a:Assertion)
WITH coalesce(p.createdBy, '?') AS createdBy, a.predicate AS predicate, p.status AS status, count(*) AS n
ORDER BY n DESC
WITH createdBy, status, sum(n) AS proposals, collect(predicate + ' ' + n) AS byPredicate
RETURN createdBy, status, proposals, byPredicate[..8] AS topPredicates
ORDER BY status DESC, proposals DESC;


// Browser style (paste once into the Browser command line) ---------------------------------------
// :style node.Entity { caption: '{label}'; diameter: 55px; }
//        node.Assertion { caption: '{predicate}'; diameter: 18px; color: #DDDDDD; border-color: #999999; }
//        relationship { caption: ''; }
