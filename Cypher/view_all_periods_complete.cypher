// Display All Periods with Complete Information
// Shows: QID, Label, Dates, Locations, Facets, Parent/Child Relationships

MATCH (p:Period)
OPTIONAL MATCH (p)-[:LOCATED_IN]->(place:Place)
OPTIONAL MATCH (p)-[facet_rel]->(f:Facet)
OPTIONAL MATCH (p)-[:PART_OF]->(parent:Period)
OPTIONAL MATCH (child:Period)-[:PART_OF]->(p)
WITH p, 
     collect(DISTINCT place.qid) as locations,
     collect(DISTINCT {type: type(facet_rel), label: f.label}) as facets,
     parent.label as parent_period,
     collect(DISTINCT child.label) as child_periods
RETURN 
    p.qid as QID,
    p.label as Label,
    p.start_year as Start,
    p.end_year as End,
    locations as Locations,
    facets as Facets,
    parent_period as Parent,
    child_periods as Children
ORDER BY p.start_year;

