// Simpler Table View of All Periods

MATCH (p:Period)
OPTIONAL MATCH (p)-[:LOCATED_IN]->(place:Place)
OPTIONAL MATCH (p)-[facet_rel]->(f:Facet)
OPTIONAL MATCH (p)-[:PART_OF]->(parent:Period)
RETURN 
    substring(p.qid, size(p.qid)-15, 15) as QID,
    p.label as Period,
    p.start_year as Start,
    p.end_year as End,
    count(DISTINCT place) as Locations,
    labels(f)[0] as FacetType,
    parent.label as ParentPeriod
ORDER BY p.start_year;

