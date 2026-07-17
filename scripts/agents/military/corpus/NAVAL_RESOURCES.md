Yes — for a naval-warfare subgraph in Neo4j, direct the LLM first to authoritative, openly accessible corpora that expose **claims with provenance**, not just narrative summaries. Given your Chrystallum/MILITARY-facet workflow and Neo4j-first architecture, the best stack is a mix of official doctrine, naval history primary-source collections, open scholarly repositories, and a few high-quality practitioner venues for modern interpretation.[[perplexity](https://www.perplexity.ai/search/c8b352f7-2f63-4eb9-aae0-23214af10c7f)]

## Best sources

The strongest free core is: Naval History and Heritage Command, Naval War College materials, CIMSEC doctrine PDFs and analysis, Internet Archive/HathiTrust for older naval classics, and open museum or government collections for ship logs, fleet histories, and technical vocabularies. These sources are useful because they give you extractable entities such as ship, fleet, commander, theater, engagement, doctrine, weapon system, and operational concept, along with dates and documentary context.[[history.navy](https://www.history.navy.mil/)]

- **Naval History and Heritage Command (NHHC)** — best official open corpus for U.S. naval history, ship histories, documentary editions, subject guides, and reading-room materials.[[history.navy](https://www.history.navy.mil/research/publications/publications-by-subject.html)]
    
- **DANFS** — ideal for structured ship-level extraction; each entry can seed `Ship`, `Class`, `ServicePeriod`, `BattleParticipation`, and `NamedAfter` nodes.[[history.navy](https://www.history.navy.mil/research/histories/ship-histories/danfs.html)]
    
- **NHHC documentary collections** — especially useful because they expose letters, logs, orders, official reports, and muster rolls rather than polished secondary prose.[[history.navy](https://www.history.navy.mil/research/publications/publications-by-subject/naval-documents-of-the-american-revolution.html)]
    
- **CIMSEC** — useful for modern naval analysis and, critically, for hosting openly accessible doctrine PDFs.[[cimsec](https://cimsec.org/wp-content/uploads/2020/08/NDP1_April2020.pdf)]
    
- **Proceedings / USNI** — valuable but only partially free, so use it as a secondary enrichment source rather than a core ingestion stream.[[usni](https://www.usni.org/magazines/proceedings/1916/january/general-problem-naval-warfare)]
    

## Ancient and early-modern

For ancient naval warfare, you will need more than one source class: open scans of classic works, open encyclopedic references, and authority files for people, places, and periods. Internet Archive is especially good for older naval monographs and general naval histories, including long-run surveys that bridge ancient galleys to modern fleets.[[archive](https://archive.org/details/navalwarfareillu0000humb)]

I would structure the ancient side like this:

- **Internet Archive / HathiTrust / Google Books public-domain works** — best for classic naval-history texts and older translations of ancient sources; useful for extracting claims, but every claim should carry edition metadata and confidence flags.[[archive](https://archive.org/details/battle-at-sea-3000-years-of-naval-warfare_202404)]
    
- **Perseus Digital Library** — for ancient authors on Greek, Roman, and Mediterranean warfare; good for claim extraction from primary texts, though you should separate author-claim from historical-fact claim.
    
- **Pleiades + PeriodO + Wikidata** — not naval corpora per se, but essential authority layers for places, periods, and cross-linking in your subgraph, consistent with your existing federation pattern.[[perplexity](https://www.perplexity.ai/search/ed62661d-2a10-4b6d-9d7b-435b654da694)]
    
- **Wikipedia only as a recall layer** — acceptable for candidate discovery, but not for final claim authority in a research-grade subgraph.
    

A good ancient example is to treat “Battle of Salamis” as an `Event`, then attach claims from Herodotus, later modern historians, and authority IDs separately, rather than flattening them into one canonical narrative.

## Modern and doctrinal

For modern naval warfare, doctrine is the cleanest extraction target because it defines terms explicitly and is already semi-structured. CIMSEC links to _Naval Warfare_ and _Fleet Warfare_ doctrine texts, which are excellent for building concept nodes such as `SeaControl`, `PowerProjection`, `FleetWarfare`, `MaritimeSecurity`, `DistributedMaritimeOperations`, and `CommandRelationship`.[[cimsec](https://cimsec.org/wp-content/uploads/2023/01/NWP_3March2021-1.pdf)]

Use these source types differently:

|Source type|Best use in Neo4j|Why it matters|
|---|---|---|
|Official doctrine PDFs|Concept graph, definitions, doctrine lineage|Definitions are explicit and stable. [[cimsec](https://cimsec.org/wp-content/uploads/2020/08/NDP1_April2020.pdf)]|
|Official historical collections|Event, ship, unit, order, log, report claims|Strong provenance and document type metadata. [[history.navy](https://www.history.navy.mil/research/publications/publications-by-subject.html)]|
|Ship-history corpora|Ship/fleet/service subgraphs|Highly regular and entity-rich. [[history.navy](https://www.history.navy.mil/research/histories/ship-histories/danfs.html)]|
|Practitioner analysis|Interpretive claims, debate edges, modern analogies|Good for contested or evolving concepts. [[cimsec](https://cimsec.org/)]|
|Public-domain books|Long-span historical synthesis, especially ancient to early modern|Broad coverage, but variable scholarly currency. [[archive](https://archive.org/details/navalwarfareillu0000humb)]|

## Extraction design

I would not “train” the LLM in the fine-tuning sense first; I would ground it with a retrieval-and-extraction pipeline that emits claim objects into Neo4j. That fits your subgraph method better and lets you preserve disagreement, source genre, and temporal layering.[[perplexity](https://www.perplexity.ai/search/78b4a3d6-947d-4933-b354-52a6ae83e13f)]

Recommended node and edge pattern:

- `SourceWork`
    
- `SourcePassage`
    
- `Claim`
    
- `Entity` subclasses: `Ship`, `Fleet`, `Commander`, `Polity`, `Port`, `SeaZone`, `Battle`, `Campaign`, `DoctrineConcept`, `WeaponSystem`
    
- Edges:
    
    - `(:Claim)-[:ASSERTED_IN]->(:SourcePassage)`
        
    - `(:SourcePassage)-[:PART_OF]->(:SourceWork)`
        
    - `(:Claim)-[:ABOUT]->(:Entity)`
        
    - `(:Claim)-[:RELATES_TO]->(:Event)`
        
    - `(:Claim)-[:USES_CONCEPT]->(:DoctrineConcept)`
        
    - `(:Claim)-[:CONTRADICTS|SUPPORTS]->(:Claim)`
        

Also add extraction metadata per claim:

- `source_type` = doctrine, primary, memoir, official history, secondary, practitioner essay
    
- `time_scope` = ancient, early modern, industrial, world war, cold war, contemporary
    
- `claim_mode` = descriptive, causal, evaluative, doctrinal, quantitative
    
- `confidence`
    
- `anachronism_risk`
    

That last field is especially important for your Roman and ancient material, where later texts often project backward.[[perplexity](https://www.perplexity.ai/search/42534b31-ea52-4da8-a4d6-f8ace0c0311a)]

## Starter corpus

If you want the shortest high-value ingestion queue, start with these:

1. NHHC Publications by Subject.[[history.navy](https://www.history.navy.mil/research/publications/publications-by-subject.html)]
    
2. NHHC DANFS.[[history.navy](https://www.history.navy.mil/research/histories/ship-histories/danfs.html)]
    
3. NHHC online reading-room subject and title lists.[[history.navy](https://www.history.navy.mil/research/library/online-reading-room/subject-list.html)]
    
4. _Naval Documents of the American Revolution_ for document-level extraction patterns.[[history.navy](https://www.history.navy.mil/research/publications/publications-by-subject/naval-documents-of-the-american-revolution.html)]
    
5. _Naval Warfare_ doctrine PDF.[[cimsec](https://cimsec.org/wp-content/uploads/2020/08/NDP1_April2020.pdf)]
    
6. _Fleet Warfare_ doctrine PDF.[[cimsec](https://cimsec.org/wp-content/uploads/2023/01/NWP_3March2021-1.pdf)]
    
7. CIMSEC essays for contemporary analytical vocabulary.[[cimsec](https://cimsec.org/)]
    
8. Internet Archive public-domain naval histories for ancient-to-modern bridge coverage.[[archive](https://archive.org/details/bub_gb_Fb1CAAAAYAAJ)]
    

For your use case, I would make the first pass **document-centric**, not topic-centric: ingest source metadata, split into passages, extract claims, then link claims to naval entities and concepts. That will produce a cleaner, provenance-rich subgraph than asking the LLM to “learn naval warfare” from raw web pages.[[history.navy](https://www.history.navy.mil/research/publications/publications-by-subject.html)]

