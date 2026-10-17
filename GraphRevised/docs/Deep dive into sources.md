Deep dive into sources
The sources divide into four practical access patterns: **live APIs/linked data, versioned bulk downloads, record-level browser consultation, and external annotation tools**. The important architectural point is that every adapter should convert the source’s native response into one common `SourceRecord` envelope without discarding the original representation. [Agent resources.md](Agent%20resources.md)

The attached inventory is a starting point rather than a verified endpoint registry. Exact URLs, authentication, schemas, releases, and item-level licenses should therefore be tested before an adapter is marked operational. [Agent resources.md](Agent%20resources.md)

## Authority and geography

| Source | Preferred access | Request or operation | Native response | Agent receives |
|---|---|---|---|---|
| **Wikidata**  [Agent resources.md](Agent%20resources.md) | SPARQL and entity API | Search label; retrieve QID; request statements and qualifiers | SPARQL JSON/XML; entity JSON; RDF | Candidate entity, QID, labels, aliases, descriptions, properties, references, and match confidence |
| **Pleiades**  [Agent resources.md](Agent%20resources.md) | Stable record URI; machine-readable record; approved bulk release where available | Resolve ancient place name or identifier | Place metadata, coordinates, names, temporal attestations, and authority links; exact serialization should be verified in the registry | `PlaceCandidate` with Pleiades ID, names, geometry, dates, place types, and external matches |
| **World Historical Gazetteer**  [Agent resources.md](Agent%20resources.md) | Documented API and reconciliation service; browser fallback | Submit place name, variants, temporal interval, or dataset identifier | API reconciliation results; exact current serialization requires endpoint verification | Ranked place matches with coordinates, temporal bounds, names, geometries, source dataset, and confidence |
| **PeriodO**  [Agent resources.md](Agent%20resources.md) | Linked-data record and dataset download | Retrieve named historical period or chronology definition | Structured period authority data; exact endpoint format should be tested | `PeriodCandidate` with authority URI, label, temporal bounds, geography, source definition, and mapping status |
| **Nomisma.org**  [Agent resources.md](Agent%20resources.md) | URI lookup, API, SPARQL, RDF, or bulk download | Query ruler, mint, denomination, material, region, or coin concept | RDF and SPARQL results; bulk linked data | Numismatic concept with Nomisma URI, labels, concept type, broader concepts, and external authorities |
| **Syriaca.org**  [Agent resources.md](Agent%20resources.md) | Stable web records, TEI, RDF, JSON-LD, GeoJSON, KML, plain text, and linked-data services | Retrieve person, place, Work, saint, author, or institution | Format depends on requested representation | Authority candidate plus names, relationships, bibliography, geography, dates, and provenance |
| **Syriac Gazetteer**  [Agent resources.md](Agent%20resources.md) | Syriaca linked-data representations | Search or dereference a place identifier | TEI, RDF, JSON-LD, GeoJSON, KML, or HTML | Place identity with Syriaca URI, names, coordinates, historical relationships, and authority matches |
| **ORBIS**  [Agent resources.md](Agent%20resources.md) | Interactive model plus approved network downloads | Submit origin, destination, season, transport mode, and cost preference | Interactive route calculation; downloadable nodes and edges commonly circulated as CSV or GeoJSON | `RouteObservation` with nodes, path, modeled duration, modeled cost, season, mode, model version, and caveats |
| **Mapping Past Societies**  [Agent resources.md](Agent%20resources.md) | Interactive atlas and layer-specific downloads | Select a geographic layer or dataset | Shapefile, geodatabase, spreadsheet, and related GIS formats | Spatial features normalized to GeoJSON plus layer metadata, original geometry reference, chronology, and rights |
| **Seshat**  [Agent resources.md](Agent%20resources.md) | Selected spreadsheets, GitHub/Zenodo releases, and documented API workflows | Request polity, variable, region, or period | Spreadsheet/tabular data, release files, or API payload | Secondary-data observation with polity, variable, value, temporal interval, coding notes, release, and citation |
| **Recogito**  [Agent resources.md](Agent%20resources.md) | Upload lawful text or image; export annotations | Submit document, annotate mentions and places, export results | CSV, JSON, RDF, or GeoJSON | Annotations connected to source offsets, candidate authorities, places, annotator, and confidence |

## Greek and Roman sources

| Source | Preferred access | Request or operation | Native response | Agent receives |
|---|---|---|---|---|
| **Open Greek and Latin**  [Agent resources.md](Agent%20resources.md) | Official Git repositories, downloadable editions, and available text services | Retrieve an edition, Work, or passage by repository/CTS identifier | Machine-readable edition, commonly structured text; format and license vary by component | `TextEdition` containing Work identity, edition, language, passage hierarchy, text, citation scheme, license, and repository version |
| **Digital Latin Library**  [Agent resources.md](Agent%20resources.md) | Open edition repository | Download a selected critical edition | TEI-XML | Edition metadata, structured divisions, Latin text, critical/editorial markup, named elements, TEI header, and license |
| **DigilibLT**  [Agent resources.md](Agent%20resources.md) | Search interface and direct downloads | Search author/Work or download approved text | TEI-XML and, depending on the Work/interface, TXT, HTML, PDF, or EPUB | Preferred TEI parsing into passages, normalized text, tokens, editorial features, Work metadata, and citation anchors |
| **Musisque Deoque**  [Agent resources.md](Agent%20resources.md) | Versioned CLARIN deposit rather than scraping the website | Download the approved corpus release | ZIP archive; internal corpus representation should be verified against the deposit manifest | Latin poetic texts, Work/author metadata, meter or critical information when encoded, release ID, and license |
| **Papyri.info**  [Agent resources.md](Agent%20resources.md) | Browser/search for discovery; Git repository for reproducible ingestion | Search a papyrus or retrieve an EpiDoc record by identifier | TEI/EpiDoc XML; pages may combine DDbDP, HGV, APIS, translations, bibliography, and institutional images | Separate `PhysicalObject`, `Document`, `Edition`, `Passage`, `Translation`, and `ImageReference` records with gaps, supplied text, provenance, date, and rights |
| **PHI Greek Inscriptions**  [Agent resources.md](Agent%20resources.md) | Browser search and record consultation only | Search region, corpus, word, phrase, or operator expression | Human-readable HTML record/search results | Citation, inscription identifier, brief permitted extraction, candidate entities, and link back to PHI; no mirrored corpus |
| **Coinage of the Roman Republic Online**  [Agent resources.md](Agent%20resources.md) | Web facets and linked-data services through the ANS/Nomisma ecosystem | Search type, magistrate, mint, date, denomination, legend, or iconography | Web records and linked data; related SPARQL results through Nomisma | `CoinType` plus authority, magistrate, mint, date range, denomination, material, legends, iconography, references, and specimen links |
| **Online Coins of the Roman Empire**  [Agent resources.md](Agent%20resources.md) | Search/facets, linked-data interfaces, and Nomisma/SPARQL ecosystem | Query type-level or specimen-level attributes | Linked records, RDF/SPARQL-compatible data, and web records | Type and specimen records kept separate; images remain external unless individually licensed |
| **Nomisma-linked coin portals**  [Agent resources.md](Agent%20resources.md) | URI dereferencing, RDF, API, SPARQL, or bulk data | Query rulers, mints, materials, types, symbols, and measurements | RDF, structured query results, or bulk linked data | Numismatic entities and relationships with source-level provenance and separate image-rights metadata |
| **Ancient inscriptions generally**  [Agent resources.md](Agent%20resources.md) | Prefer EpiDoc download; otherwise consult record pages | Retrieve inscription edition and metadata | TEI/EpiDoc when available; otherwise HTML/PDF | Physical monument, surface, inscription text, edition, restoration, translation, current location, and bibliography remain separate |

## Eastern Mediterranean sources

| Source | Preferred access | Request or operation | Native response | Agent receives |
|---|---|---|---|---|
| **Coptic SCRIPTORIUM**  [Agent resources.md](Agent%20resources.md) | GitHub/Zenodo releases; ANNIS for analytical search | Download an approved corpus or query linguistic annotations | CoNLL-U, relANNIS, PAULA XML, TEI-XML, TreeTagger formats, or ANNIS results | Document hierarchy, tokens, lemmas, morphology, syntax, named entities, corpus metadata, and document-specific license |
| **Digital Syriac Corpus**  [Agent resources.md](Agent%20resources.md) | Official Git repository; CTS-oriented retrieval where supported | Retrieve edition, Work, or passage | TEI-XML and CTS-addressable text | Syriac passage with edition metadata, language/script, structure, citation, encoder attribution, and license |
| **Sefaria**  [Agent resources.md](Agent%20resources.md) | Version 3 JSON Text API for targeted use; complete exports for local databases | Request textual reference and selected language/version; use `return_format=text_only` where appropriate | Structured JSON API response; per-version TXT, CSV, or JSON downloads; complete exports | Text segments with canonical reference, language, version title, source, license, attribution, and translation relationship |
| **Dead Sea Scrolls portals**  [Agent resources.md](Agent%20resources.md) | Searchable record and image interfaces | Search manuscript, cave, text, language, or script | HTML metadata and high-resolution image delivery | Manuscript metadata and canonical image links; image binaries remain consultative unless explicit rights permit storage |
| **OCIANA**  [Agent resources.md](Agent%20resources.md) | Website search and record-level consultation | Search inscription, script, provenance, personal name, deity, or place | HTML record containing transliteration, commentary, bibliography, metadata, and images; downloadable image where offered | Inscription identifier, script/language, provenance, date, text type, names, gods, places, citation, and external image reference |
| **Chicago Demotic Dictionary**  [Agent resources.md](Agent%20resources.md) | Online lexical consultation | Search Demotic word or form | Browser-rendered lexical entry | Lexical observation, citation, interpretation, and link; no automatic corpus ingestion until reuse terms are verified |

## Mesopotamian and Iranian sources

| Source | Preferred access | Request or operation | Native response | Agent receives |
|---|---|---|---|---|
| **CDLI**  [Agent resources.md](Agent%20resources.md) | Versioned daily bulk packages and GitHub snapshots; API/client exports for selective retrieval | Request artifacts, periods, proveniences, inscriptions, rulers, languages, transliterations, or translations | Bulk data; CSV or N-Triples from supported exports; structured catalog records | Separate artifact, text, edition, provenance, period, ruler, language, and image-reference records |
| **ORACC**  [Agent resources.md](Agent%20resources.md) | Project download or structured export, after checking the individual project license | Retrieve an ORACC project, text, corpus, transliteration, or annotation set | Project-specific structured data, including cuneiform-oriented representations where supplied | Lines, transliteration, signs, language, lemmas, damage markers, translation, glossary links, project code, and license |
| **ETCSL**  [Agent resources.md](Agent%20resources.md) | Browser search and reading | Retrieve Sumerian composition or passage | HTML text and translation pages | Citation and brief source extraction only until conflicting reuse claims are resolved |
| **Achemenet/Korp**  [Agent resources.md](Agent%20resources.md) | Online corpus search with result download where enabled | Submit Babylonian word, lemma, or corpus query | Korp search results and downloadable result set; exact export format needs verification | Concordance hit, source text identifier, context, lemma, annotations, corpus name, and retrieval details |
| **Persepolis Fortification Archive**  [Agent resources.md](Agent%20resources.md) | OCHRE web database and linked records | Search tablet, seal, text, language, official, or administrative concept | Interactive linked database records and high-resolution images | Record-level metadata, relationships, identifiers, and citation; systematic local ingestion withheld pending rights confirmation |
| **TITUS Avestan Corpus**  [Agent resources.md](Agent%20resources.md) | Browser and direct HTTP file download where enabled | Retrieve a selected Avestan text or file | Source-specific downloadable text file | Text, language/encoding, source attribution, citation, and scholarly-use restriction |
| **Avesta.org**  [Agent resources.md](Agent%20resources.md) | Browser, selected PDF, and EPUB download | Select Work or edition | HTML, PDF, or EPUB | Consultative text with edition-level rights, bibliographic identity, and citation; no assumption of uniform corpus rights |
| **GRETIL**  [Agent resources.md](Agent%20resources.md) | Individual files or cumulative archive download | Select language, Work, author, or cumulative package | Machine-readable files in several legacy and standardized encodings | Text plus source encoding, Work metadata, original terms, composition/edition distinction, and normalization log |

## Islamic and Asian sources

| Source | Preferred access | Request or operation | Native response | Agent receives |
|---|---|---|---|---|
| **OpenITI**  [Agent resources.md](Agent%20resources.md) | Active Git repositories for current data; Zenodo for citable release snapshots | Clone/download release or retrieve a text by OpenITI URI | OpenITI mARkdown files and release metadata | Work/author URI, structural sections, page markers, normalized Arabic/Persian text, release, license, and parser version |
| **Quranic Arabic Corpus**  [Agent resources.md](Agent%20resources.md) | Online interface and project repository | Query verse, token, lemma, morphology, syntax, or ontology concept | Web results and repository datasets in project-specific forms | Verse/token identifiers, Arabic form, lemma, morphology, syntactic relations, concepts, and dataset provenance |
| **Corpus Coranicum**  [Agent resources.md](Agent%20resources.md) | Online database consultation | Search manuscript, textual history, contextual text, chronology, or commentary | Browser records; GitHub primarily exposes website software rather than blanket-licensed content | Citation, identifiers, brief observations, and links; editorial records and images remain consultative pending rights review |
| **Thesaurus d’Épigraphie Islamique**  [Agent resources.md](Agent%20resources.md) | Browser search and reading | Search language, region, date, ruler, or inscription | HTML record/search result | Citation and record-level factual extraction only; no bulk ingestion without explicit permission |
| **Chinese Text Project**  [Agent resources.md](Agent%20resources.md) | JSON API and textual URNs for targeted retrieval; browser for discovery | Request corpus subset, Work, chapter, or passage | Machine-readable JSON | Canonical textual reference, Chinese text, structural hierarchy, edition/transcription metadata, and separate translation-rights status |
| **CHANT**  [Agent resources.md](Agent%20resources.md) | Institutionally licensed browser interface | Search traditional or excavated text | Controlled web display | Consultative citation and manually reviewed observation; no automated derivative corpus without written permission |

## Native-response handling

The attached document recommends a bulk-first hierarchy:

1. Versioned institutional or Zenodo release.
2. Official Git repository with release tags.
3. Documented bulk dump.
4. Documented API or SPARQL endpoint.
5. Stable record-level TEI, RDF, JSON-LD, IIIF, or comparable representation.
6. Browser reading and citation.
7. Scraping only when expressly permitted. [Agent resources.md](Agent%20resources.md)

The ingestion service should preserve the native response rather than reducing everything immediately to plain text.

| Native format | Preserve | Normalized output |
|---|---|---|
| **TEI/EpiDoc XML** | TEI header, divisions, named elements, supplied text, gaps, restorations, line numbers, bibliography | Edition, passage, entity mention, editorial intervention, evidence span |
| **RDF/JSON-LD** | Source URIs, predicates, named graphs, provenance, identity assertions | Entity candidates and relationship candidates without treating `closeMatch` as `sameAs` |
| **SPARQL results** | Query text, endpoint, execution date, bindings, datatypes | Source records plus reproducible query provenance |
| **JSON API** | Complete response, request parameters, pagination, API version | Field-mapped records with unmapped fields retained |
| **CSV/spreadsheet** | Original columns, data types, row identifiers, formulas/notes where relevant | Observations or entities with row-level provenance |
| **CoNLL-U** | Token IDs, forms, lemmas, morphology, dependencies, sentence/document boundaries | Linguistic evidence and entity mentions |
| **ATF/cuneiform formats** | Signs, transliteration, line numbering, damage, restorations, language shifts | Passage and linguistic records without erasing uncertainty |
| **OpenITI mARkdown** | Page markers, headers, structural tags, URI, release | Structured Work, section, page, and passage records |
| **GeoJSON/shapefile** | Original geometry, CRS, feature identifiers, layer metadata | Place/route geometry in a common spatial representation |
| **IIIF** | Manifest, canvas, annotation, rights, attribution, image-service URLs | `ImageReference`; binary image stored only when rights permit |
| **HTML browser record** | URL, access date, title, visible citation, permitted excerpt | Consultative `SourceObservation`, not a locally ingested corpus |
| **PDF/EPUB** | Original file, edition metadata, page anchors, extraction method | Passages only when structured alternatives are unavailable and extraction is permitted |

## Common response envelope

Every source adapter should return the same top-level structure even though `nativePayload` differs:

```json
{
  "fetch": {
    "sourceId": "papyri-info",
    "adapterId": "papyri-epidoc-v1",
    "accessMode": "git_bulk",
    "requestedAt": "2026-10-17T14:00:00Z",
    "releaseId": "repository-commit-or-release",
    "request": {
      "recordId": "source-record-identifier"
    },
    "rightsDecision": {
      "sourceClass": "A",
      "allowedUses": ["index", "rag", "extract"],
      "storeRaw": true,
      "storeImages": false
    }
  },
  "nativePayload": {
    "mediaType": "application/tei+xml",
    "checksum": "sha256-value",
    "storagePointer": "object-store-reference"
  },
  "records": [
    {
      "sourceRecordId": "source-record-identifier",
      "canonicalUrl": "stable-record-url",
      "recordType": "documentary_text",
      "labels": [],
      "dates": [],
      "places": [],
      "persons": [],
      "works": [],
      "passages": [],
      "externalIdentifiers": [],
      "citations": [],
      "rights": {},
      "provenance": {},
      "unmappedNativeFields": {}
    }
  ],
  "warnings": [],
  "errors": []
}
```

## Agent-facing response

The source adapter should not directly return graph nodes and claims as accepted facts. It should return an evidence packet:

```json
{
  "evidencePacketId": "ep-123",
  "inquiryId": "inq-actium-001",
  "sourceRecords": ["papyri:record-x", "nomisma:record-y"],
  "entityCandidates": [],
  "identityMatches": [],
  "observations": [],
  "claimCandidates": [],
  "conflicts": [],
  "uncertainties": [],
  "rightsRestrictions": [],
  "coverageContribution": {
    "newEntities": 0,
    "newClaimFamilies": 0,
    "newEvidenceClasses": 0,
    "gapsClosed": []
  }
}
```

This creates a clean boundary:

```text
Native source response
    → source-specific adapter
    → normalized SourceRecord
    → evidence extraction
    → EvidencePacket
    → claim reconciliation
    → proposed graph
    → review and promotion
```

The most development-ready sources in the inventory are those with versioned structured downloads: Papyri.info, DigilibLT, Digital Latin Library, Coptic SCRIPTORIUM, Digital Syriac Corpus, Syriaca.org, Sefaria’s licensed versions, Nomisma, CDLI, approved ORACC projects, OpenITI’s noncommercial partition, and the Chinese Text Project’s targeted JSON service. [Agent resources.md](Agent%20resources.md)

Browser-only or rights-uncertain resources—such as PHI, ETCSL, Persepolis Fortification Archive, parts of OCIANA, Corpus Coranicum, the Islamic epigraphic thesaurus, and CHANT—should initially return only consultative observations, identifiers, citations, and links rather than reusable corpus records. [Agent resources.md](Agent%20resources.md)