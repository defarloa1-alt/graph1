For each time period determine the following
    which facets is the primary facet for the time period and populate the primary has facet relationship
    PoliticalFacet      | Political    | Periods defined by states, regimes, dynasties, governance         | Q11514315, Q3624078, Q164950    |
    | CulturalFacet       | Cultural     | Cultural eras, shared practices, identity, literature, arts       | Q185363, Q735, Q11042           |
    | TechnologicalFacet  | Technological| Tool regimes, production technologies, industrial phases          | Q11016, Q255, Q33767            |
    | ReligiousFacet      | Religious    | Religious movements, institutions, doctrinal eras                 | Q9174, Q432, Q5043              |
    | EconomicFacet       | Economic     | Economic systems, trade regimes, financial structures             | Q8134, Q7406919, Q184754        |
    | MilitaryFacet       | Military     | Warfare, conquests, military systems, strategic eras              | Q8473, Q198, Q40231             |
    | EnvironmentalFacet  | Environmental| Climate regimes, ecological shifts, environmental phases          | Q756, Q2715388, Q629            |
    | DemographicFacet    | Demographic  | Population structure, migration, urbanization waves               | Q37577, Q208188, Q7937          |
    | IntellectualFacet   | Intellectual | Schools of thought, philosophical or scholarly movements          | Q5891, Q5893, Q333              |
    | ScientificFacet     | Scientific   | Scientific paradigms, revolutions, epistemic frameworks           | Q336, Q309, Q170058             |
    | ArtisticFacet       | Artistic     | Art movements, architectural styles, aesthetic regimes            | Q968159, Q32880, Q735           |
    | SocialFacet         | Social       | Social norms, class structures, social movements                  | Q2695280, Q49773, Q8436         |
    | LinguisticFacet     | Linguistic   | Language families, scripts, linguistic shifts                     | Q315, Q8192, Q8196              |
    | ArchaeologicalFacet | Archaeological| Material-culture periods, stratigraphy, typologies               | Q1190554, Q23442, Q11767        |
    | DiplomaticFacet     | Diplomatic   | International systems, alliances, treaty regimes   
        | Q186509, Q1065, Q3624078        |

    remove anything that is an event not really a  time period
    it must have a start  end date and location. remove those that do not.
        the location should be a place node.
        the start and end date should be a year node.
        the primary facet should be a facet node.
        the period should be a period node.
        if the end date is before 2000 bce delete the item
        

