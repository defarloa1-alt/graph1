// 05_temporal_hierarchy_levels.cypher
// Create Decade, Century, Millennium nodes and link hierarchy
// Year -> Decade -> Century -> Millennium

// 1. Create Decades and link Years
MATCH (y:Year)
WHERE y.year IS NOT NULL
WITH y, 
     y.year - (y.year % 10) as decade_start
MERGE (d:Decade {start_year: decade_start})
ON CREATE SET 
    d.label = toString(decade_start) + 's',
    d.end_year = decade_start + 9,
    d.temporal_backbone = true
MERGE (y)-[:PART_OF]->(d);

// 2. Create Centuries and link Decades
MATCH (d:Decade)
WITH d,
     d.start_year - (d.start_year % 100) as century_start
MERGE (c:Century {start_year: century_start})
ON CREATE SET
    c.label = toString(abs(century_start / 100) + 1) + 
              CASE 
                WHEN century_start < 0 THEN ' BCE'
                ELSE ' CE'
              END + ' Century',
    c.end_year = century_start + 99,
    c.temporal_backbone = true
MERGE (d)-[:PART_OF]->(c);

// 3. Create Millenniums and link Centuries
MATCH (c:Century)
WITH c,
     c.start_year - (c.start_year % 1000) as millennium_start
MERGE (m:Millennium {start_year: millennium_start})
ON CREATE SET
    m.label = toString(abs(millennium_start / 1000) + 1) + 
              CASE 
                WHEN millennium_start < 0 THEN ' BCE'
                ELSE ' CE'
              END + ' Millennium',
    m.end_year = millennium_start + 999,
    m.temporal_backbone = true
MERGE (c)-[:PART_OF]->(m);
