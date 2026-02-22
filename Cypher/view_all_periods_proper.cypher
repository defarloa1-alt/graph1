// Display All Periods with QID, Label, Dates, Locations, Facets, Parent/Child

MATCH (p:Period)
OPTIONAL MATCH (p)-[:LOCATED_IN]->(place:Place)
OPTIONAL MATCH (p)-[facet_rel]->(f:Facet)
OPTIONAL MATCH (p)-[:PART_OF]->(parent:Period)
OPTIONAL MATCH (child:Period)-[:PART_OF]->(p)
WITH p, 
     collect(DISTINCT place.qid) as location_qids,
     collect(DISTINCT [label IN labels(f) WHERE label <> 'Facet'][0]) as specific_facets,
     parent,
     collect(DISTINCT child.label) as child_labels
RETURN 
    p.qid as QID,
    p.label as Label,
    p.start_year as Start,
    p.end_year as End,
    size(location_qids) as LocationCount,
    location_qids as Locations,
    specific_facets[0] as PrimaryFacet,
    parent.label as Parent,
    size(child_labels) as ChildCount,
    child_labels as Children
ORDER BY p.start_year;

