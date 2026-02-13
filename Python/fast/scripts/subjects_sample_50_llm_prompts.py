import json

PROMPT_TEMPLATE = """
LLM Prompt for subject scoring
using this list of facets
Facet nodes provide a universal, reusable classification system for all major node types (Period, Event, Place, etc.), supporting faceted search, filtering, and semantic enrichment. Each facet is a node with a specific type and properties, and is linked to entities via explicit relationships.

### Facet Class Table
| Facet Class         | Label         | Definition                                                        | Example Wikidata QIDs           |
|---------------------|--------------|-------------------------------------------------------------------|---------------------------------|
| PoliticalFacet      | Political    | Periods defined by states, regimes, dynasties, governance         | Q11514315, Q3624078, Q164950    |
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
| DiplomaticFacet     | Diplomatic   | International systems, alliances, treaty regimes                  | Q186509, Q1065, Q3624078        |

### Facet Node Labels
- :Facet (abstract, not instantiated)
- :PoliticalFacet, :CulturalFacet, :TechnologicalFacet, :ReligiousFacet, :EconomicFacet, :MilitaryFacet, :EnvironmentalFacet, :DemographicFacet, :IntellectualFacet, :ScientificFacet, :ArtisticFacet, :SocialFacet, :LinguisticFacet, :ArchaeologicalFacet, :DiplomaticFacet

For each subject determine whether based on the subject, broader than narrower then and any other info in the record, score confidence in  each facet as it may be related to the subject. give the confidence score and then a assess code for each facet of H if confidence is >.75 L if <.5 and the rest M. in final assessment concatenate all the h m l into a string. You can and should have more than 1 facet identified for the subject.

Subject record:
{subject_json}
"""

input_file = "../key/subjects_sample_50.jsonld"
output_file = "../output/subjects_sample_50_llm_prompts.json"

with open(input_file, encoding="utf-8") as f:
    data = json.load(f)

subjects = data.get("@graph", [])
results = []

for subj in subjects:
    prompt = PROMPT_TEMPLATE.replace("{subject_json}", json.dumps(subj, ensure_ascii=False, indent=2))
    results.append({
        "subject_id": subj.get("@id", ""),
        "llm_prompt": prompt
    })

with open(output_file, "w", encoding="utf-8") as out:
    json.dump(results, out, ensure_ascii=False, indent=2)

print(f"Wrote LLM prompts for {len(results)} subjects to {output_file}")
