// Display All Periods with Current Data
// Shows: QID, Label, Dates, Locations, Facets

MATCH (p:Period)
OPTIONAL MATCH (p)-[:LOCATED_IN]->(place:Place)
OPTIONAL MATCH (p)-[facet_rel]->(f:Facet)
WITH p, 
     collect(DISTINCT substring(place.qid, size(place.qid)-15, 15)) as location_ids,
     collect(DISTINCT {
         facet_type: labels(f)[0],
         relationship: type(facet_rel)
     }) as facet_info
RETURN 
    substring(p.qid, size(p.qid)-12, 12) as QID,
    p.label as Period,
    p.start_year as Start,
    p.end_year as End,
    size(location_ids) as LocationCount,
    location_ids as Locations,
    [f IN facet_info | f.facet_type][0] as FacetType,
    [f IN facet_info | f.relationship][0] as FacetRelationship
ORDER BY p.start_year;

