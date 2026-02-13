// Simple View: All Periods with Key Info

MATCH (p:Period)
OPTIONAL MATCH (p)-[:LOCATED_IN]->(place:Place)
OPTIONAL MATCH (p)-[:HAS_CULTURAL_FACET|HAS_POLITICAL_FACET|HAS_ARCHAEOLOGICAL_FACET|HAS_ARTISTIC_FACET]->(f:Facet)
RETURN 
    p.qid as QID,
    p.label as Period,
    p.start_year as Start,
    p.end_year as End,
    count(DISTINCT place) as Locations,
    labels(f)[0] as Facet
ORDER BY p.start_year
LIMIT 50;

