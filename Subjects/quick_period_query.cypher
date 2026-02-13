// Quick Query: See All Periods and Their Edges

MATCH (p:Period)
OPTIONAL MATCH (p)-[r]->(target)
RETURN 
    p.label as Period,
    p.start_year as Start,
    p.end_year as End,
    type(r) as Relationship,
    labels(target)[0] as TargetType,
    COALESCE(target.label, target.value, substring(target.qid, size(target.qid)-10, 10)) as Target
ORDER BY p.start_year
;

