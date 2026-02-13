geo chat 2
You can treat each high‑level demographic anchor as a small subclass/vocabulary that is also explicitly aligned to CIDOC‑CRM patterns (mainly `E55 Type` for the concept and `E54 Dimension` where it is quantitatively measured).[1][2][3]

Below is Cypher that:

- Creates a Demographic facet category (if not already present).  
- Creates each DemographicFacet anchor.  
- Adds a linked CRM‑alignment node that says how it should be realized in a CIDOC‑CRM‑style graph (as `E55 Type`, `E54 Dimension`, or both).

## Cypher for Demographic facet subclasses with CRM alignment

```cypher
// Demographic facet category (anchor)
MERGE (demCat:FacetCategory {
  key: 'DEMOGRAPHIC'
})
SET demCat.label = 'Demographic',
    demCat.definition = 'Population structure, migration, urbanization waves';

// Helper: create one DemographicFacet with CRM mapping
WITH demCat
UNWIND [
  {
    unique_id: 'DEMOGRAPHICFACET_Q37732',
    label: 'Demography',
    definition: 'Study of human populations, especially size, structure, and distribution, and how they change.',
    source_qid: 'Q37732',
    crm_realization: ['E55_Type'],
    crm_notes: 'Use as a high-level E55 Type to classify demographic descriptions, datasets, or events (via P2 has type).'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q1318257',
    label: 'Fertility',
    definition: 'Patterns and levels of childbearing and reproduction.',
    source_qid: 'Q1318257',
    crm_realization: ['E55_Type','E54_Dimension'],
    crm_notes: 'Concept as E55 Type; quantitative measures (e.g. total fertility rate) as E54 Dimension typed by this.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q11879590',
    label: 'Mortality',
    definition: 'Patterns and levels of death in a population.',
    source_qid: 'Q11879590',
    crm_realization: ['E55_Type','E54_Dimension'],
    crm_notes: 'Use as E55 Type; life expectancy or mortality rates as E54 Dimension with P2 has type = Mortality.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q29667',
    label: 'Migration',
    definition: 'Movement of people across regions or borders.',
    source_qid: 'Q29667',
    crm_realization: ['E55_Type'],
    crm_notes: 'Migration events modeled as E5 Event (or extension) with P2 has type = Migration; flows can be dimensions.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q2989643',
    label: 'Demographic transition',
    definition: 'Long-term change in birth and death rates and population growth.',
    source_qid: 'Q2989643',
    crm_realization: ['E55_Type'],
    crm_notes: 'Treat as E55 Type to classify time-spans, scenarios, or historical periods by stage of demographic transition.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q12097886',
    label: 'Population size',
    definition: 'Total number of people in a defined unit and time.',
    source_qid: 'Q12097886',
    crm_realization: ['E54_Dimension'],
    crm_notes: 'Model as E54 Dimension with P90 has value; attached via P43 has dimension to a Group or Place proxy.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q5086',
    label: 'Population density',
    definition: 'Number of people per unit area of land.',
    source_qid: 'Q5086',
    crm_realization: ['E54_Dimension'],
    crm_notes: 'E54 Dimension with P91 has unit = persons_per_km2 (E58 Measurement Unit), typed via P2 has type.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q603644',
    label: 'Age structure',
    definition: 'Distribution of a population by age groups.',
    source_qid: 'Q603644',
    crm_realization: ['E55_Type','E54_Dimension'],
    crm_notes: 'Concept as E55 Type; particular age-structure indicators (e.g. median age) as E54 Dimension.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q182484',
    label: 'Population ageing',
    definition: 'Process in which the proportion of older persons in the population increases.',
    source_qid: 'Q182484',
    crm_realization: ['E55_Type'],
    crm_notes: 'Use as E55 Type to classify time-spans, places, or groups characterized by ageing populations.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q1143039',
    label: 'Population composition',
    definition: 'Composition of a population by characteristics such as sex, age, ethnicity, or education.',
    source_qid: 'Q1143039',
    crm_realization: ['E55_Type'],
    crm_notes: 'High-level E55 Type; specific compositions realized via multiple E54 Dimensions (shares, ratios).'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q1549591',
    label: 'Urbanization',
    definition: 'Increase in the proportion of people living in urban areas.',
    source_qid: 'Q1549591',
    crm_realization: ['E55_Type','E54_Dimension'],
    crm_notes: 'Concept as E55 Type; urbanization level (% urban) as E54 Dimension attached to a region/time-span.'
  },
  {
    unique_id: 'DEMOGRAPHICFACET_Q570116',
    label: 'Geographical distribution of population',
    definition: 'Spatial distribution of population across regions, cities, and rural areas.',
    source_qid: 'Q570116',
    crm_realization: ['E55_Type'],
    crm_notes: 'E55 Type used to classify spatial distribution descriptions; detailed values via spatialized dimensions.'
  }
] AS cfg

MERGE (f:DemographicFacet:Facet {unique_id: cfg.unique_id})
SET f.label = cfg.label,
    f.definition = cfg.definition,
    f.source_qid = cfg.source_qid
MERGE (f)-[:IN_FACET_CATEGORY]->(demCat)

// Optional: explicit CRM alignment node per facet
MERGE (crmMap:CRMAlignment {
  facet_unique_id: cfg.unique_id
})
SET crmMap.crm_realization = cfg.crm_realization,
    crmMap.crm_notes = cfg.crm_notes

MERGE (f)-[:ALIGNS_TO_CIDOC]->(crmMap);
```

This pattern keeps your DemographicFacet layer clean while making the CIDOC‑CRM alignment explicit and machine‑readable:

- Agents can read `crm_realization` to know whether to spawn `E55 Type` terms, `E54 Dimension` measurements, or both.  
- A CRM‑aware export pipeline can traverse `(:DemographicFacet)-[:ALIGNS_TO_CIDOC]->(:CRMAlignment)` and emit correct CIDOC‑style RDF (`P2 has type`, `E16 Measurement` → `E54 Dimension` → `P90 has value`, etc.).[4][2][1]

[1](https://cidoc-crm.org/html/cidoc_crm_v7.1.3.html)
[2](https://ontome.net/class/52/namespace/1)
[3](https://ontome.net/class/53/namespace/188)
[4](https://cidoc-crm.org/Issue/ID-511-measurements-and-dimensions)
[5](https://cidoc-crm.org/taxonomy/term/26)
[6](https://ontome.net/ontology/p2)
[7](https://cidoc-crm.org/Issue/ID-496-types-for-p2-has-type)
[8](https://linked.art/model/profile/class_analysis/)
[9](https://ontome.net/property/2/namespace/187)
[10](https://cidoc-crm.org/Issue/ID-536-properties-for-assigning-dimensions-to-places-and-temporal-entities)
[11](https://www.ics.forth.gr/isl/CRMext/CRMsci/docs/CRMsci1.2.1.pdf)
[12](https://www.ics.forth.gr/isl/CRMext/CRMsci/docs/CRMsci1.0.pdf)
[13](https://csrc.nist.gov/files/pubs/ir/8214/a/final/docs/nistir-8214a-diff-comments-received.pdf)
[14](https://cidoc-crm.org/html/cidoc_crm_v4.0.html)
[15](https://pmc.ncbi.nlm.nih.gov/articles/PMC11603854/)