The source inventory gives an agent **substantial practical research capability**, but not the ability to “know ancient history” autonomously. Properly implemented, it could orient an inquiry, resolve entities, assemble diverse evidence, identify graph gaps, and propose well-sourced subgraphs; it could not reliably determine historical truth or build a book-quality graph without claim review and additional modern scholarship. [Agent resources.md](Agent%20resources.md)

## What it really provides

The document is best understood as a **source-routing architecture**, not a corpus. It tells an agent where different kinds of evidence may be found, how they can be retrieved, which lenses they support, and what rights restrictions apply. [Agent resources.md](Agent%20resources.md)

That is valuable because an agent could choose sources based on the inquiry:

| Need | Likely resources | Practical capability |
|---|---|---|
| Identity and authority | Wikidata, Pleiades, WHG, Syriaca, Nomisma | Resolve entities and attach stable identifiers |
| Literary evidence | Open Greek and Latin, DigilibLT, Digital Latin Library | Retrieve passages and identify people, places, events, and stated relationships |
| Documentary evidence | Papyri.info, CDLI, ORACC, Sefaria | Extract transactions, offices, petitions, taxes, households, and administrative activity |
| Epigraphic evidence | PHI, OCIANA, Papyri.info | Find named people, offices, dedications, decrees, units, and places |
| Numismatic evidence | CRRO, OCRE, Nomisma | Connect authorities, mints, denominations, materials, iconography, and political messaging |
| Geography and movement | Pleiades, WHG, ORBIS, MAPS | Normalize places and reason about routes, distance, cost, and connectivity |
| Linguistic evidence | Coptic SCRIPTORIUM, ORACC, DigilibLT | Use morphology, lemmas, syntax, and named-entity annotations |
| Cross-cultural inquiry | Syriaca, OpenITI, CDLI, Sefaria, GRETIL | Follow relationships beyond a conventional Greece-and-Rome boundary |

The strongest feature is not the number of resources. It is the combination of **evidence classes**: texts, inscriptions, papyri, coins, objects, places, routes, authority records, and structured modern datasets.

## Capability levels

### Strong capability

An agent should perform these tasks reliably once source adapters are implemented:

- Find likely authority records.
- Identify candidate people, places, institutions, Works, events, objects, and concepts.
- Retrieve machine-readable TEI, RDF, JSON-LD, CSV, CoNLL-U, or linked-data records where available.
- Preserve source identifiers and edition metadata.
- Map material into a common evidence structure.
- Identify existing graph objects that may be reused.
- Detect straightforward duplicate entities and claims.
- Recommend applicable lenses and source families.
- Construct an initial chronology or thematic structure.
- Produce evidence-linked proposals for curator review.
- Identify obvious disagreements between sources.

These are realistic agent tasks because much of the inventory exposes structured records, stable identifiers, documented APIs, bulk files, repositories, or linked-data services. [Agent resources.md](Agent%20resources.md)

### Moderate capability

These tasks are possible, but results will vary:

- Extract historical assertions from ancient prose.
- Distinguish event phases.
- Identify indirect relationships.
- Compare accounts across sources.
- Interpret coin iconography or political language.
- Associate an inscription with a historical episode.
- Decide whether new evidence enhances or conflicts with an existing claim.
- Determine whether two references denote the same poorly documented person.
- Find non-obvious multi-hop research paths.

These require historical reasoning rather than simple extraction. The agent can propose interpretations, but genre, rhetoric, chronology, translation, damaged texts, editorial restoration, and uncertain identification create failure risks.

### Weak capability

The resource list alone does not make an agent reliable at:

- Establishing which disputed reconstruction is most persuasive.
- Assessing an ancient author’s testimony in full historiographical context.
- Reconstructing missing events from silence.
- Evaluating specialist archaeological arguments.
- Distinguishing independent corroboration from dependence on a common lost source.
- Recognizing every anachronism introduced by a translation.
- Determining scholarly consensus.
- Producing an exhaustive bibliography.
- Declaring a complex subgraph historically complete.
- Promoting interpretive claims without human review.

Those are exactly the areas where the proposed reviewer, provenance model, uncertainty representation, and curator decision remain necessary.

## The critical distinction

The file sometimes uses **training** broadly, but the architecture should use more precise terminology. [Agent resources.md](Agent%20resources.md)

| Activity | Meaning |
|---|---|
| Corpus ingestion | Store legally reusable source material |
| Indexing | Make source records searchable |
| Embedding | Support semantic retrieval |
| RAG | Retrieve evidence for a particular inquiry |
| Agent consultation | Read or search a source without ingesting it |
| Fine-tuning | Alter model behavior or weights using a prepared dataset |
| Graph learning | Reuse prior dossiers, mappings, and approved graph content |

Most of the immediate value lies in **retrieval, structured extraction, entity reconciliation, and graph proposal—not fine-tuning**. Fine-tuning on these collections would create much greater licensing, provenance, evaluation, and deletion problems while providing no guarantee of accurate historical reasoning.

## Source classes matter

The A/B/C classification is one of the document’s strongest design choices:

- **Class A:** Suitable for approved ingestion.
- **Class B:** Usable only after record-, edition-, or component-level review.
- **Class C:** Consultative; the agent may search, read, and cite, but should not build a local corpus from it.

This means a Class C source is not useless to the agent. It means the agent uses the source more like a human researcher visiting a controlled database: search it, inspect records, record identifiers and citations, and avoid bulk copying.

The document correctly separates:

- Text rights from image rights.
- Software licenses from content licenses.
- Website access from reuse permission.
- Ancient public-domain works from copyrighted modern editions and translations.
- Corpus-level statements from item-level rights.
- Open data from noncommercial or share-alike data. [Agent resources.md](Agent%20resources.md)

That legal awareness makes the design more operationally credible than a simple list of “free historical websites.”

## Actium example

For an Actium inquiry, the inventory could support a meaningful first research cycle:

1. **Authority resolution:** Identify Actium, Nicopolis, the Ambracian Gulf, Octavian, Agrippa, Antony, Cleopatra, relevant polities, and vessel types.
2. **Literary orientation:** Locate available Greek and Latin accounts or open editions.
3. **Geographic modeling:** Connect places through Pleiades and WHG; use suitable route and transport datasets cautiously.
4. **Numismatic context:** Examine coin types, authorities, mints, denominations, materials, and political iconography through CRRO and Nomisma.
5. **Epigraphic discovery:** Search controlled epigraphic resources for relevant dedications, titles, people, and places.
6. **Material inquiry:** Connect bronze, timber, shipbuilding, naval rams, artillery, and vessel classes where suitable object or archaeological records exist.
7. **Proposal generation:** Create candidate entities and claims with passages, identifiers, provenance, uncertainty, and source classifications.
8. **Review:** Compare each proposal against the approved and proposed graph.

That could produce a good **orientation dossier and first-round subgraph**. It would not yet produce a defensible reconstruction of the battle.

## Important gaps

### Modern scholarship

The inventory is strongest in open primary texts, structured corpora, authorities, and specialized datasets. It appears weaker in systematic access to recent monographs, journal articles, excavation reports, specialist commentaries, and scholarly debates. [Agent resources.md](Agent%20resources.md)

For Actium, this matters greatly. Ancient accounts alone will not adequately handle:

- Archaeological interpretations.
- Naval architecture.
- Monument reconstruction.
- Fleet composition.
- Landscape and harbor studies.
- Source dependence.
- Modern debate over battle versus breakout.
- Augustan memory and propaganda.

A commercially realistic system needs a **modern-scholarship lane**, even if many sources are consultative, abstract-only, library-supplied, or entered manually by the curator.

### Uneven civilizations

Coverage quality is highly uneven. Roman, Greek, Egyptian, Syriac, Mesopotamian, Jewish, and some early Islamic resources are comparatively well represented, while Punic, North African, Armenian, Iranian, Central Asian, South Asian, and Chinese coverage is more fragmented or rights-constrained. [Agent resources.md](Agent%20resources.md)

The agent must surface that imbalance. It should never make “few accessible results” appear equivalent to “little historical evidence existed.”

### Translation dependence

An English-language agent will often depend on modern translations. Those translations may be copyrighted, interpretive, abridged, dated, or unavailable under reusable terms.

The data model should therefore distinguish:

```text
Ancient Work
Edition
Ancient-language Text
Modern Translation
Passage
Editorial Restoration
Agent Interpretation
```

Otherwise, the graph may attribute a translator’s wording or an editor’s restoration directly to an ancient author.

### Source dependence

Finding the same assertion in five web resources does not establish five independent witnesses. They may all derive from one ancient passage, one catalog record, or one modern reference work.

The agent therefore needs both:

```text
Claim --SUPPORTED_BY--> Evidence
Evidence --DERIVED_FROM--> SourceTradition
```

Diminishing returns should measure **new independent evidence**, not merely additional URLs.

## Required infrastructure

The inventory becomes operational only when each source has a tested adapter or documented consultation workflow.

A source registry should record:

- Source and adapter identifiers.
- Retrieval method.
- Supported record types.
- Rights class.
- Item-level rights behavior.
- Rate limits and access requirements.
- Stable identifier patterns.
- Current schema version.
- Mapping into the graph model.
- Evidentiary strengths and weaknesses.
- Last successful test.
- Failure behavior.
- Permitted storage and quotation.
- Required attribution.
- Removal procedure.

Without that infrastructure, the document remains an excellent research guide but does not yet constitute agent capability.

## Agent workflow

A realistic source-driven agent should work like this:

```text
Inquiry
  → determine scope and lenses
  → inspect graph coverage
  → select source classes
  → allocate research budget
  → retrieve a diverse first batch
  → normalize records
  → resolve identities
  → create evidence objects
  → propose claims
  → compare with approved and proposed graph
  → external review
  → curator decision
  → evaluate marginal yield
  → continue or stop
```

Every proposal should retain:

- Exact source.
- Exact edition or dataset release.
- Exact passage or record.
- Retrieval date.
- Rights status.
- Extraction method.
- Entity-resolution method.
- Confidence.
- Uncertainty.
- Agent and model version.
- Review verdict.
- Curator disposition.

## A realistic product claim

A defensible product description would be:

> **The agent can research a bounded historical inquiry across approved structured and consultative sources, reconcile entities, organize evidence, identify graph gaps and disagreements, and propose provenance-rich additions for curator review.**

An indefensible description would be:

> **The agent autonomously researches history and builds an authoritative knowledge graph.**

The difference is important. The resources make the system potentially powerful at **discovery, organization, connection, and proposal**. They do not eliminate historiography, source criticism, rights review, or human judgment.

## Recommended first test

Do not initially test the system by asking whether it can “graph Actium.” Test it against a bounded evaluation set:

- 10 known people.
- 10 known places.
- 5 institutions or collective actors.
- 10 events or campaign phases.
- 10 material or technological entities.
- 20 straightforward claims.
- 10 qualified claims.
- 5 disputed claims.
- 5 identity ambiguities.
- 5 deliberate duplicates.
- 5 claims unsupported by the available sources.

Measure:

- Entity precision.
- Identity-resolution accuracy.
- Citation correctness.
- Evidence-to-claim entailment.
- Duplicate classification.
- Conflict preservation.
- Source diversity.
- Rights-policy compliance.
- Unsupported-claim rejection.
- Curator acceptance and modification rates.
- New claim families per source batch.
- Cost and time per accepted proposal.

The most important evaluation is not how many nodes the agent creates. It is **how often its evidence packets allow you to make a correct decision quickly**.

## Bottom line

The source inventory is sufficient to support a serious **historical graph-research agent prototype**. Its strongest achievable role is that of a tireless research assistant that searches across evidence types, resolves entities, preserves provenance, exposes uncertainty, and proposes connections.

Its weakest—and most dangerous—possible role would be an autonomous historian that turns retrieved statements directly into approved graph truth. The architecture you have been developing, with bounded inquiries, source budgets, persistent dossiers, visible proposals, an independent reviewer, and curator promotion, is therefore not excessive governance. It is what converts this source inventory into a credible research system.