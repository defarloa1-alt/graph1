Facets creation

1. **creates one `:FacetCategory` per facet type**, and
2. **creates/merges facet value nodes** (the example QIDs), and
3. **ties each facet value to its category** via `[:IN_FACET_CATEGORY]`.

It uses the same working pattern you already validated (MERGE + SET), just with category wiring built in.

---

## One-time constraints (recommended)

```cypher
CREATE CONSTRAINT facet_unique_id IF NOT EXISTS
FOR (f:Facet)
REQUIRE f.unique_id IS UNIQUE;

CREATE CONSTRAINT facet_category_key IF NOT EXISTS
FOR (c:FacetCategory)
REQUIRE c.key IS UNIQUE;
```

---

## PoliticalFacet

```cypher
MERGE (cat:FacetCategory {key:"GEOGRAPHIC"})
SET cat.label="Geographic",
    cat.definition="Spatial/regional classification for entities (regions, continents, basins, seas, etc.)"
WITH cat
UNWIND [
  {qid:"Q82794", label:"Region"},
  {qid:"Q5107",  label:"Continent"},
  {qid:"Q6256",  label:"Country"}
] AS row
MERGE (f:Facet:GeographicFacet { unique_id: "GEOGRAPHICFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## CulturalFacet

```cypher
MERGE (cat:FacetCategory {key:"CULTURAL"})
SET cat.label="Cultural",
    cat.definition="Cultural eras, shared practices, identity, literature, arts"
WITH cat
UNWIND [
  {qid:"Q11042",   label:"Culture"},
  {qid:"Q2198855", label:"Cultural movement"},
  {qid:"Q4692",    label:"Renaissance"}
] AS row
MERGE (f:Facet:CulturalFacet { unique_id: "CULTURALFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## TechnologicalFacet

```cypher
MERGE (cat:FacetCategory {key:"TECHNOLOGICAL"})
SET cat.label="Technological",
    cat.definition="Tool regimes, production technologies, industrial phases"
WITH cat
UNWIND [
  {qid:"Q11016",  label:"Technology"},
  {qid:"Q2269",   label:"Industrial Revolution"},
  {qid:"Q144334", label:"Printing press"}
] AS row
MERGE (f:Facet:TechnologicalFacet { unique_id: "TECHNOLOGICALFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## ReligiousFacet

```cypher
MERGE (cat:FacetCategory {key:"RELIGIOUS"})
SET cat.label="Religious",
    cat.definition="Religious movements, institutions, doctrinal eras"
WITH cat
UNWIND [
  {qid:"Q9174", label:"Religion"},
  {qid:"Q5043", label:"Christianity"},
  {qid:"Q432",  label:"Islam"}
] AS row
MERGE (f:Facet:ReligiousFacet { unique_id: "RELIGIOUSFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## EconomicFacet

```cypher
MERGE (cat:FacetCategory {key:"ECONOMIC"})
SET cat.label="Economic",
    cat.definition="Economic systems, trade regimes, financial structures"
WITH cat
UNWIND [
  {qid:"Q273005", label:"Economic system"},
  {qid:"Q6206",   label:"Capitalism"},
  {qid:"Q7272",   label:"Socialism"}
] AS row
MERGE (f:Facet:EconomicFacet { unique_id: "ECONOMICFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## MilitaryFacet

```cypher
MERGE (cat:FacetCategory {key:"MILITARY"})
SET cat.label="Military",
    cat.definition="Warfare, conquests/campaigns, military systems, strategic eras"
WITH cat
UNWIND [
  {qid:"Q198",    label:"War"},
  {qid:"Q8473",   label:"Military"},
  {qid:"Q831663", label:"Military campaign"}
] AS row
MERGE (f:Facet:MilitaryFacet { unique_id: "MILITARYFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## EnvironmentalFacet

```cypher
MERGE (cat:FacetCategory {key:"ENVIRONMENTAL"})
SET cat.label="Environmental",
    cat.definition="Climate regimes, ecological shifts, environmental phases"
WITH cat
UNWIND [
  {qid:"Q43619",  label:"Natural environment"},
  {qid:"Q7937",   label:"Climate"},
  {qid:"Q101998", label:"Biome"}
] AS row
MERGE (f:Facet:EnvironmentalFacet { unique_id: "ENVIRONMENTALFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## DemographicFacet

```cypher
MERGE (cat:FacetCategory {key:"DEMOGRAPHIC"})
SET cat.label="Demographic",
    cat.definition="Population structure, migration, urbanization waves"
WITH cat
UNWIND [
  {qid:"Q37732",  label:"Demography"},
  {qid:"Q177626", label:"Human migration"},
  {qid:"Q161078", label:"Urbanization"}
] AS row
MERGE (f:Facet:DemographicFacet { unique_id: "DEMOGRAPHICFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## IntellectualFacet

```cypher
MERGE (cat:FacetCategory {key:"INTELLECTUAL"})
SET cat.label="Intellectual",
    cat.definition="Schools of thought, philosophical or scholarly movements"
WITH cat
UNWIND [
  {qid:"Q5891",    label:"Philosophy"},
  {qid:"Q1387659", label:"School of thought"},
  {qid:"Q7257",    label:"Ideology"}
] AS row
MERGE (f:Facet:IntellectualFacet { unique_id: "INTELLECTUALFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## ScientificFacet

```cypher
MERGE (cat:FacetCategory {key:"SCIENTIFIC"})
SET cat.label="Scientific",
    cat.definition="Scientific paradigms, revolutions, epistemic frameworks"
WITH cat
UNWIND [
  {qid:"Q336",    label:"Science"},
  {qid:"Q46857",  label:"Scientific method"},
  {qid:"Q214078", label:"Scientific Revolution"}
] AS row
MERGE (f:Facet:ScientificFacet { unique_id: "SCIENTIFICFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## ArtisticFacet

```cypher
MERGE (cat:FacetCategory {key:"ARTISTIC"})
SET cat.label="Artistic",
    cat.definition="Art movements, architectural styles, aesthetic regimes"
WITH cat
UNWIND [
  {qid:"Q735",    label:"Art"},
  {qid:"Q968159", label:"Art movement"},
  {qid:"Q4692",   label:"Renaissance"}
] AS row
MERGE (f:Facet:ArtisticFacet { unique_id: "ARTISTICFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## SocialFacet

```cypher
MERGE (cat:FacetCategory {key:"SOCIAL"})
SET cat.label="Social",
    cat.definition="Social norms, class structures, social movements"
WITH cat
UNWIND [
  {qid:"Q49773",  label:"Social movement"},
  {qid:"Q205665", label:"Social norm"},
  {qid:"Q187588", label:"Social class"}
] AS row
MERGE (f:Facet:SocialFacet { unique_id: "SOCIALFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## LinguisticFacet

```cypher
MERGE (cat:FacetCategory {key:"LINGUISTIC"})
SET cat.label="Linguistic",
    cat.definition="Language families, scripts, linguistic shifts"
WITH cat
UNWIND [
  {qid:"Q8162",  label:"Linguistics"},
  {qid:"Q25295", label:"Language family"},
  {qid:"Q8192",  label:"Writing system"}
] AS row
MERGE (f:Facet:LinguisticFacet { unique_id: "LINGUISTICFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## ArchaeologicalFacet

```cypher
MERGE (cat:FacetCategory {key:"ARCHAEOLOGICAL"})
SET cat.label="Archaeological",
    cat.definition="Material-culture periods, stratigraphy, typologies"
WITH cat
UNWIND [
  {qid:"Q23498",  label:"Archaeology"},
  {qid:"Q465299", label:"Archaeological culture"}
] AS row
MERGE (f:Facet:ArchaeologicalFacet { unique_id: "ARCHAEOLOGICALFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## DiplomaticFacet

```cypher
MERGE (cat:FacetCategory {key:"DIPLOMATIC"})
SET cat.label="Diplomatic",
    cat.definition="International systems, alliances, treaty regimes"
WITH cat
UNWIND [
  {qid:"Q1889", label:"Diplomacy"}
] AS row
MERGE (f:Facet:DiplomaticFacet { unique_id: "DIPLOMATICFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

## GeographicFacet (NEW)

```cypher
MERGE (cat:FacetCategory {key:"GEOGRAPHIC"})
SET cat.label="Geographic",
    cat.definition="Spatial/regional classification for entities (regions, continents, basins, seas, etc.)"
WITH cat
UNWIND [
  {qid:"Q82794", label:"Region"},
  {qid:"Q5107",  label:"Continent"},
  {qid:"Q6256",  label:"Country"}
] AS row
MERGE (f:Facet:GeographicFacet { unique_id: "GEOGRAPHICFACET_" + row.qid })
SET f.label = row.label,
    f.definition = cat.definition,
    f.source_qid = row.qid
MERGE (f)-[:IN_FACET_CATEGORY]->(cat);
```

---

## Quick verification query

```cypher
MATCH (cat:FacetCategory)<-[:IN_FACET_CATEGORY]-(f:Facet)
RETURN cat.key AS category, count(f) AS facets
ORDER BY category;
```

If you want, I can also generate a **cleanup query** that finds facet nodes missing a category relationship and auto-attaches them based on their labels (`PoliticalFacet`, `CulturalFacet`, etc.).
