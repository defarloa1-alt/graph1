// Display All Periods with Complete Information (Fixed Facet Display)

MATCH (p:Period)
OPTIONAL MATCH (p)-[:LOCATED_IN]->(place:Place)
OPTIONAL MATCH (p)-[facet_rel]->(f:Facet)
WITH p, 
     collect(DISTINCT place.qid) as location_qids,
     collect(DISTINCT {
         relationship: type(facet_rel),
         facet_labels: labels(f),
         specific_type: [label IN labels(f) WHERE label <> 'Facet'][0]
     }) as facet_details
RETURN 
    p.qid as QID,
    p.label as Label,
    p.start_year as Start,
    p.end_year as End,
    size(location_qids) as LocationCount,
    location_qids as Locations,
    [f IN facet_details | f.specific_type] as FacetTypes,
    [f IN facet_details | f.relationship] as FacetRelationships
ORDER BY p.start_year;

