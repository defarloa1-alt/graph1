# Facet Node Schema Proposal for Chrystallum Knowledge Graph
#
Facet Class Definitions (from Anchor List)
#
The following facet subclasses are defined, each with a clear domain and example Wikidata QIDs:
#
| Facet Class         | Label          | Definition                                                  | Example Wikidata QIDs        |
| ------------------- | -------------- | ----------------------------------------------------------- | ---------------------------- |
| PoliticalFacet      | Political      | Periods defined by states, regimes, dynasties, governance   | Q11514315, Q3624078, Q164950 |
| CulturalFacet       | Cultural       | Cultural eras, shared practices, identity, literature, arts | Q185363, Q735, Q11042        |
| TechnologicalFacet  | Technological  | Tool regimes, production technologies, industrial phases    | Q11016, Q255, Q33767         |
| ReligiousFacet      | Religious      | Religious movements, institutions, doctrinal eras           | Q9174, Q432, Q5043           |
| EconomicFacet       | Economic       | Economic systems, trade regimes, financial structures       | Q8134, Q7406919, Q184754     |
| MilitaryFacet       | Military       | Warfare, conquests, military systems, strategic eras        | Q8473, Q198, Q40231          |
| EnvironmentalFacet  | Environmental  | Climate regimes, ecological shifts, environmental phases    | Q756, Q2715388, Q629         |
| DemographicFacet    | Demographic    | Population structure, migration, urbanization waves         | Q37577, Q208188, Q7937       |
| IntellectualFacet   | Intellectual   | Schools of thought, philosophical or scholarly movements    | Q5891, Q5893, Q333           |
| ScientificFacet     | Scientific     | Scientific paradigms, revolutions, epistemic frameworks     | Q336, Q309, Q170058          |
| ArtisticFacet       | Artistic       | Art movements, architectural styles, aesthetic regimes      | Q968159, Q32880, Q735        |
| SocialFacet         | Social         | Social norms, class structures, social movements            | Q2695280, Q49773, Q8436      |
| LinguisticFacet     | Linguistic     | Language families, scripts, linguistic shifts               | Q315, Q8192, Q8196           |
| ArchaeologicalFacet | Archaeological | Material-culture periods, stratigraphy, typologies          | Q1190554, Q23442, Q11767     |
| DiplomaticFacet     | Diplomatic     | International systems, alliances, treaty regimes            | Q186509, Q1065, Q3624078     |
| CommunicationFacet  | Communication  | Use of media to communicate messages                        | Q11024                       |
#
Each facet class is a subclass of `:Facet` and can be linked to any entity via a `HAS_[FACET_TYPE]_FACET` relationship.


## Overview
This schema introduces explicit facet nodes and relationships for all major node types, supporting universal filtering, navigation, and semantic enrichment.

---

## 1. Facet Node Types

### :Facet (Abstract)
- **Purpose:** Base label for all facet types (not instantiated directly)

### Subclasses (examples):
  - :TemporalFacet
  - :GeographicFacet
  - :PoliticalFacet
  - :CulturalFacet
  - :TechnologicalFacet
  - :ReligiousFacet
  - :EconomicFacet
  - :MilitaryFacet
  - :EnvironmentalFacet
  - :DemographicFacet
  - :IntellectualFacet
  - :ScientificFacet
  - :ArtisticFacet
  - :SocialFacet
  - :LinguisticFacet
  - :ArchaeologicalFacet
  - :DiplomaticFacet
- CommunicationFacet
### Example Properties (per facet type):

#### :TemporalFacet
  - `unique_id`: "TEMPORALFACET_{start}_{end}_{label}"
  - `label`: e.g., "Bronze Age (Middle East)"
  - `start_year`: integer (ISO, BCE negative)
  - `end_year`: integer (ISO, BCE negative)
  - `precision`: string (e.g., "century", "year", "fuzzy")
  - `source_qid`: Wikidata QID if available

#### :GeographicFacet
  - `unique_id`: "GEOFACET_{region_qid}"
  - `label`: e.g., "Middle East"
  - `region_qid`: Wikidata QID
  - `lat`: float (optional)
  - `lon`: float (optional)

#### :PoliticalFacet (and other anchor facets)
  - `unique_id`: "POLITICALFACET_{qid}"
  - `label`: e.g., "Empire"
  - `definition`: e.g., "Periods defined by states, regimes, dynasties, governance structures"
  - `source_qid`: Wikidata QID
-
	#### CommunicationFacet
		unique_id
		label
		definition
		source_qid
			
		
		
- 

// Repeat for other anchor facets as needed

---

## 2. Relationships

- `HAS_TEMPORAL_FACET` (Period, Event, Dynasty, etc.) → TemporalFacet
- `HAS_GEOGRAPHIC_FACET` (Period, Event, Place, Dynasty, etc.) → GeographicFacet
- `HAS_[FACET_TYPE]_FACET` (any node) → [Facet Subclass] (e.g., HAS_POLITICAL_FACET, HAS_TECHNOLOGICAL_FACET)

Each entity can point to multiple facets of different types, supporting multi-dimensional classification.

---

## 3. Example Cypher Templates

### Create Facet Nodes
```cypher
CREATE (tf:TemporalFacet:Facet {
  unique_id: "TEMPORALFACET_-3300_-1200_Bronze_Age_Middle_East",
  label: "Bronze Age (Middle East)",
  start_year: -3300,
  end_year: -1200,
  precision: "century",
  source_qid: "Q11761"
})

CREATE (gf:GeographicFacet:Facet {
  unique_id: "GEOFACET_Q7204",
  label: "Middle East",
  region_qid: "Q7204",
  lat: 28,
  lon: 45
})

CREATE (topf:TopicalFacet:Facet {
  unique_id: "TOPICFACET_sh85115055",
  label: "Roman Republic",
  lcsh_id: "sh85115055",
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  qid: "Q17167"
})
```

### Link Facets to Entities
```cypher
// Example for a Period node
MATCH (p:Period {qid: "Q11761"}), (tf:TemporalFacet {unique_id: "TEMPORALFACET_-3300_-1200_Bronze_Age_Middle_East"})
MERGE (p)-[:HAS_TEMPORAL_FACET]->(tf)

MATCH (p:Period {qid: "Q11761"}), (gf:GeographicFacet {unique_id: "GEOFACET_Q7204"})
MERGE (p)-[:HAS_GEOGRAPHIC_FACET]->(gf)

MATCH (p:Period {qid: "Q11761"}), (topf:TopicalFacet {unique_id: "TOPICFACET_sh85115055"})
MERGE (p)-[:HAS_TOPICAL_FACET]->(topf)
```

---

## 4. Integration Notes
- All major node types should link to at least one facet node of each relevant type.
- Facet nodes are reusable: multiple entities can point to the same facet.
- Facet nodes can be extended (e.g., :ChronologicalFacet, :CulturalFacet) as needed.
- This system supports universal filtering, faceted search, and semantic navigation across the graph.

---

## 5. Next Steps
- Add facet node creation and linking to all import/enrichment scripts.
- Update schema documentation and validators to require facet relationships.
- Optionally, add a `Facet` registry for deduplication and lookup.
