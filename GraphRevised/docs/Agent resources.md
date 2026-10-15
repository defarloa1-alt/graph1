Agent resources
# Free Online Text Sources for Ancient-History Agents

This report treats “training” broadly—corpus ingestion, retrieval-augmented generation, fine-tuning, and agent-directed online consultation—but recommends admitting each source only for uses explicitly allowed by its license and terms. It emphasizes resources beyond the federation and authority infrastructure already in place: Wikidata, Pleiades, Trismegistos, PeriodO, LCC, LCSH, FAST, and related hubs.

## Operating recommendation

Do not equate **free access** with permission to download, reproduce, mine, or train. Maintain three operational source classes:

| Class | Agent use | Admission rule |
|---|---|---|
| **A: ingestible** | Bulk indexing, embeddings, RAG, linguistic analysis, and potentially model training | Machine-readable delivery plus an explicit compatible license; preserve attribution, version, and share-alike/noncommercial obligations |
| **B: conditional** | Ingest only approved records or versions | Rights vary by text, collection, image, translation, or contributor; evaluate each asset individually |
| **C: consultative** | Agent reads or searches online and records citations, identifiers, or brief factual extractions | Free-to-read but copying, reuse, automation, or derivative works are restricted or unclear |

A source registry should record at least:

- Canonical source and record URLs
- Polity, region, and date interval
- Ancient language, script, modern translation language, and edition
- Retrieval method: browser, API, Git, SPARQL, dump, IIIF, TEI/XML, RDF, CSV, JSON, or PDF
- License at the **item/version level**, not merely the website level
- Whether commercial use, redistribution, derivatives, or model training are permitted
- Attribution string, access date, release identifier, checksum, and local transformations
- Lenses supported: political, economic, religious, social, artistic, scientific, legal, military, linguistic, geographic, and environmental
- Evidentiary type: literary text, inscription, papyrus, administrative document, coin, manuscript, map, or modern scholarly metadata

## Cross-polity infrastructure

These resources should enrich and route the corpus rather than normally serve as the principal prose-training layer.

| Source | Coverage and lenses | Retrieval | Rights and recommendation |
|---|---|---|---|
| [World Historical Gazetteer](https://whgazetteer.org/) | Historical places, names, coordinates, temporal bounds, geometries, and authority links; geographic, political, economic, and military lenses | Web exploration; documented API and reconciliation service; account required for some dataset functions | Use for entity reconciliation and spatial enrichment. The platform has API documentation and supports programmatic spatial queries; its software release is BSD-3-Clause, but contributed datasets may retain their own rights, so preserve dataset-level provenance. [whgazetteer](https://whgazetteer.org/) |
| [Nomisma.org](https://nomisma.org/) | Rulers, mints, denominations, materials, coin types, places, and numismatic concepts across Rome and interacting polities; political, economic, artistic, religious, and metallurgical lenses | Linked-data URIs, APIs, SPARQL, and bulk formats | Nomisma concepts are available under CC BY, with bulk downloads and SPARQL access. Treat specimen images and records supplied by museums separately because their licenses can differ. [reviewsindh.pubpub](https://reviewsindh.pubpub.org/pub/nomisma) |
| [Seshat](https://seshatdatabank.info/) | Coded descriptions of political organization, complexity, religion, warfare, agriculture, and institutions | Web browsing; selected downloadable spreadsheets, snapshots, GitHub/Zenodo datasets, and documented API workflows | Valuable as structured secondary evidence, not as a substitute for primary text. Published datasets are commonly identified as CC BY-NC-SA, but repository metadata has shown inconsistencies; pin each release and retain its accompanying license. [github](https://github.com/datasets/seshat) |
| [ORBIS](https://orbis.stanford.edu/) | Roman transport routes, travel time, cost, seasonality, and connectivity; economic, military, administrative, and geographic lenses | Interactive online model; sites, routes, nodes, and edges are also circulated as CSV/GeoJSON downloads | Use as a quantitative contextual layer rather than textual ground truth. The model represents transport time and expense, while external dataset directories expose downloadable network components; confirm current license at the download location. [orbis.stanford](https://orbis.stanford.edu/) |
| [Mapping Past Societies](https://darmc.harvard.edu/) | GIS layers for Roman and later societies, ports, roads, settlements, religion, disease, migration, and economic geography | Interactive atlas; selected shapefile, geodatabase, spreadsheet, and related downloads | Downloadable MAPS datasets are generally offered under CC BY-NC-SA 4.0, with attribution and noncommercial conditions; examine the record for each layer and its original creator. [darmc.harvard](https://darmc.harvard.edu/) |
| [Recogito](https://recogito.pelagios.org/) | Annotation and entity-linking environment for texts and images; geographic, social, prosopographic, political, and event lenses | Upload TXT or TEI/XML; annotate in browser; export annotations as CSV, JSON, RDF, and GeoJSON | The software is Apache-2.0, but uploaded documents retain their original rights. Use it as a processing environment; do not infer that a document becomes reusable merely because its annotations can be exported. [recogito.pelagios](https://recogito.pelagios.org/help/faq) |

## Rome: Republic

### Priority sources

| Source | Principal material | Retrieval | Rights class | Lens alignment |
|---|---|---|---|---|
| [Coinage of the Roman Republic Online](https://numismatics.org/crro/) | Republican coin typologies and linked specimens, including rulers, magistrates, mints, dates, denominations, legends, iconography, and measurements | Web facets and linked-data services through the ANS/Nomisma ecosystem; derive bulk queries through Nomisma SPARQL where appropriate | **A/B**: typology data are designed as linked open data, but museum specimen records and images can carry separate terms | Economic, political, military, artistic, religious, social |
| [Papyri.info](https://papyri.info/) | Greek, Latin, Demotic, Coptic, and other documentary texts; contracts, petitions, receipts, accounts, letters, administrative records, and legal instruments | Read/search online; TEI/EpiDoc data are downloadable through the project’s GitHub data repository; individual pages combine DDbDP transcription, HGV metadata, APIS records, translations, and images | **A/B**: DDbDP editions commonly state CC BY 3.0; APIS images follow the owning institution’s policy | Legal, economic, social, administrative, religious, linguistic |
| [PHI Greek Inscriptions](https://inscriptions.packhum.org/) | Greek inscriptions from Italy and the wider Greek world, including decrees, treaties, dedications, epitaphs, laws, and civic records | Browser search and reading by region/corpus | **C**: the site requires agreement to personal-study and fair-use terms and does not authorize corpus copying or reuse | Political, legal, religious, social, military, artistic |
| [Online Coins of the Roman Empire](https://numismatics.org/ocre/) | Begins principally with the imperial period but is useful for continuity from late Republican monetary and iconographic systems | Web facets and linked-data interfaces | **A/B**: OCRE states that its database is under the Open Database License; component images and contributing museum records remain item-specific | Economic, political, artistic, religious |

CRRO is particularly useful for agents studying the political communication of magistrates, monetary expansion, military finance, and changing iconographic language. Its linked-data method permits type-level information to be joined to Nomisma authorities and specimens from multiple institutions. [numismaticnews](https://www.numismaticnews.net/world-coins/coinage-of-roman-republic-online-aids-numismatic-research)

For documentary evidence, Papyri.info should be treated as a major corpus even when the surviving material is concentrated in Egypt. Its pages combine transcription, metadata, translations, and institutional images, while its underlying EpiDoc data are suitable for local parsing and citation-aware RAG. [papyri](https://papyri.info/docs/apis)

### Agent use

- **Political and legal agents:** prioritize decrees, treaties, laws, civic inscriptions, petitions, and trial or administrative documents.
- **Economic agents:** combine coin typologies with receipts, accounts, taxes, leases, price references, and transport layers.
- **Religious and artistic agents:** extract deities, cult titles, temple dedications, monument types, coin legends, and iconographic descriptions.
- **Social agents:** emphasize epitaphs, manumission records, household documents, names, status terminology, occupations, and associations.
- **Guardrail:** PHI Greek Inscriptions is a high-value search and discovery source, but its stated terms support personal study rather than bulk reuse. Agents may consult and cite it; it should not be mirrored or used as an unlicensed training corpus. [inscriptions.packhum](https://inscriptions.packhum.org/)

## Rome: Principate

### Core literary and documentary layer

| Source | Principal material | Retrieval | Rights class | Lens alignment |
|---|---|---|---|---|
| [Open Greek and Latin](https://opengreekandlatin.org/) and associated repositories | Greek and Latin literary editions, translations, and text services | Git repositories and downloadable machine-readable editions; availability varies by component | **A/B**: the initiative supports downloading, modification, and redistribution subject to each text’s applicable license | All literary lenses, especially political, religious, philosophical, scientific, legal, and artistic |
| [Papyri.info](https://papyri.info/) | Everyday documentary evidence from Roman Egypt and connected regions | Browser, search, Git/EpiDoc downloads, record-level links to images | **A/B** by component | Legal, economic, social, administrative, religious |
| [OCRE](https://numismatics.org/ocre/) | Imperial coin types and aggregated specimens | Search, facets, linked data, Nomisma/SPARQL ecosystem | **A/B** | Economic, political, artistic, religious, military |
| [ORBIS](https://orbis.stanford.edu/) | Transport network and modeled movement costs | Interactive modeling plus downloadable network data through related repositories | **B** pending current dataset terms | Economic, military, administrative, geographic |
| [MAPS](https://darmc.harvard.edu/) | GIS layers, including ports, harbors, roads, settlements, and regional datasets | Browser and layer-specific downloads | **A/B**, commonly CC BY-NC-SA 4.0 | Geographic, economic, military, environmental |
| [Musisque Deoque](https://www.mqdq.it/) | Latin poetry from the beginnings of Latin through Late Antiquity, with critical and metrical information | Online consultation; a corpus ZIP is available through CLARIN-IT | **A** for the cited CLARIN deposit, CC BY-SA 4.0 | Artistic, religious, political, social, linguistic |
| [Digital Latin Library](https://digitallatin.org/) | Born-digital critical Latin editions encoded in TEI | Open TEI/XML editions and project repositories | **A/B**: editions are published on an open basis; inspect the `<availability>` and license statement in each TEI header | Literary, legal, political, scientific, linguistic |

Open Greek and Latin materials are suitable for local corpus workflows only after the agent checks the license attached to the particular edition or repository; “open project” does not guarantee identical rights across all constituent texts. Library guidance confirms that its materials are downloadable and reusable according to applicable licenses. [guides.library.illinois](https://guides.library.illinois.edu/c.php?g=1002538&p=7260298)

Musisque Deoque is especially useful for poetic language, meter, intertext, myth, religion, political praise, identity, and elite social representation. A CLARIN-IT deposit supplies a downloadable ZIP under CC BY-SA 4.0, making that identified release preferable to scraping the public interface. [dspace-clarin-it.ilc.cnr](https://dspace-clarin-it.ilc.cnr.it/items/861c199b-a0ff-448e-9101-8acbff7d6586)

The Digital Latin Library publishes critical editions as TEI/XML specifically to enable reuse. Agents should read the edition’s TEI header because the project’s encoding guidelines explicitly provide for public-domain, free, restricted, and publisher-licensed availability statements. [tei-c](https://tei-c.org/activities/projects/the-digital-latin-librarys-library-of-digital-latin-texts/)

### Numismatic workflow

OCRE should be queried at two levels:

1. **Type level:** emperor, authority, mint, denomination, date, obverse/reverse legend, deity, personification, and iconography.
2. **Specimen level:** collection, find information where supplied, weight, diameter, axis, and image.

The OCRE database itself states that it is available under the Open Database License. Museum-supplied images should remain external references unless their individual licenses permit local storage or model use. [numismatics](https://numismatics.org/ocre/search)

## Rome: Late Empire

### Latin, Christian, and administrative sources

| Source | Coverage | Retrieval | Rights class | Best lenses |
|---|---|---|---|---|
| [DigilibLT](https://digiliblt.uniupo.it/) | Secular Latin prose from approximately the second through seventh centuries CE | Search and read online; download in TEI/XML and, depending on work/interface, TXT, HTML, PDF, or EPUB; repository derivatives also exist | **A**: project materials are identified as CC BY-SA 4.0, though preserve work-level metadata | Political, legal, scientific, grammatical, administrative, literary |
| [Coptic SCRIPTORIUM](https://copticscriptorium.org/) | Coptic biblical, monastic, hagiographic, documentary, and literary corpora with linguistic annotation | Online reading and ANNIS search; GitHub/Zenodo downloads in CoNLL-U, relANNIS, PAULA XML, TEI/XML, and TreeTagger formats | **A/B**: most documents CC BY 3.0 or 4.0, with specified exceptions such as CC BY-SA texts and a separate Sahidica New Testament license | Religious, social, linguistic, institutional, legal |
| [Digital Syriac Corpus](https://syriaccorpus.org/) | Classical Syriac texts, including literature created within and across Roman, Byzantine, and Persian spheres | Online reader; Git repository containing TEI editions; CTS-based access can support embedding or targeted retrieval | **A** for the project repository: CC BY 4.0; base Syriac texts described as public domain | Religious, political, social, philosophical, scientific, linguistic |
| [Syriaca.org](https://syriaca.org/) | People, places, works, authors, saints, institutions, and bibliographic relations in Syriac culture | Web records; TEI/XML, RDF, JSON-LD, GeoJSON, KML, plain text, and linked-data services depending on module | **A**: major datasets use CC BY licenses | Political, religious, social, geographic, prosopographic |
| [Sefaria](https://www.sefaria.org/) | Hebrew and Aramaic biblical, Second Temple, rabbinic, legal, liturgical, and commentary traditions | Web reader, v3 JSON Text API, per-version TXT/CSV/JSON downloads, and complete structured exports | **B**: rights are attached to each language-version; public domain, CC0, CC BY, CC BY-NC, and unverified versions coexist | Religious, legal, social, political, linguistic |
| [Papyri.info](https://papyri.info/) | Late Roman and Byzantine documentary papyri alongside earlier records | Browser/search plus Git/EpiDoc | **A/B** | Legal, economic, social, administrative |

DigilibLT is one of the strongest ingestion candidates because it combines explicit open licensing, TEI encoding, free downloads, and period-specific coverage. The project describes hundreds of secular prose texts from the second through seventh centuries, while its repository identifies CC BY-SA 4.0 licensing. [github](https://github.com/CIRCSE/digilibLT)

Coptic SCRIPTORIUM is unusually valuable for agent training because the same documents are distributed in several NLP-friendly formats with morphology, syntax, named entities, and corpus metadata. Its repository specifies CC BY as the norm but names exceptions, so an automated loader should evaluate the manifest before admitting a document. [github](https://github.com/CopticScriptorium/corpora)

The Digital Syriac Corpus makes TEI editions available through GitHub under CC BY 4.0 and supports a reader-oriented interface. The project states that its base Syriac texts are public domain while the encoded editions carry CC BY 4.0. [github](https://github.com/srophe/syriac-corpus)

## Greek polities and Hellenistic kingdoms

This period includes Macedon and successor kingdoms such as the Ptolemies, Seleucids, Antigonids, Attalids, Greco-Bactrians, and other Greek-speaking political communities that later interacted with Rome.

| Source | Material and polity use | Retrieval | Rights and agent mode |
|---|---|---|---|
| PHI Greek Inscriptions | Civic decrees, royal correspondence, dedications, treaties, honorifics, laws, and funerary texts across Greece, Asia Minor, Syria, Egypt, North Africa, and related regions | Browser search by region, corpus, word, phrase, and operators | **C** only under stated personal-study/fair-use terms; use for discovery and human-like consultation, not bulk ingestion. [inscriptions.packhum](https://inscriptions.packhum.org/) |
| Papyri.info | Ptolemaic and Roman Egypt; governmental, fiscal, legal, military, household, commercial, and religious documentation | Browser and machine-readable EpiDoc data | **A/B** by component; DDbDP texts commonly CC BY 3.0, images institution-specific. [papyri](https://papyri.info/current/5496) |
| Nomisma and Hellenistic coin portals | Rulers, mints, denominations, types, symbols, portraits, gods, and specimen measurements | URIs, RDF, API, SPARQL, and bulk data | **A/B**; Nomisma concepts CC BY, specimen assets source-specific. [reviewsindh.pubpub](https://reviewsindh.pubpub.org/pub/nomisma) |
| Open Greek and Latin | Historians, geographers, philosophers, physicians, poets, orators, and other Greek textual traditions | Repository download and text-service access | **A/B** per edition |
| Recogito | Geotagging of itineraries, historians, decrees, and inscriptions obtained lawfully elsewhere | Upload text; export annotations and linked places | Tool is Apache-2.0; document rights remain separate. [recogito.pelagios](https://recogito.pelagios.org/help/faq) |

For the **political lens**, connect royal names and titles across inscriptions, coins, literary witnesses, and Wikidata. For the **economic lens**, prioritize Ptolemaic papyri and Hellenistic coins. For the **scientific lens**, prioritize open editions of medical, mathematical, astronomical, geographical, and mechanical texts, while recording whether a modern translation is independently copyrighted.

## Ptolemaic and Roman Egypt

Egypt deserves a separate corpus lane because papyri, ostraca, inscriptions, Coptic literature, and multilingual administrative traditions offer unusually direct evidence.

### Recommended source stack

- **Papyri.info/DDbDP/HGV/APIS:** central transcription and metadata layer. APIS includes descriptions, provenance, dates, bibliographies, images, and some English translations, but image rights remain with participating institutions. [papyri](https://papyri.info/current/5390)
- **Coptic SCRIPTORIUM:** Late Antique Coptic text and linguistic annotation layer, with downloadable corpora in several machine-readable forms. [github](https://github.com/CopticScriptorium/corpora)
- **Chicago Demotic Dictionary and related institutional resources:** use primarily as lexical and interpretive aids until text-reuse terms are separately verified.
- **Nomisma:** Ptolemaic and Roman-Egyptian rulers, mints, coin types, and monetary concepts.
- **MAPS/WHG/Pleiades:** geographic normalization and temporal place alignment.

The University of Michigan’s APIS collection describes its own openly available images and catalog records as public-domain material for educational and research access, but this should not be generalized to other APIS institutions. Preserve the owning collection and rights statement for every image. [quod.lib.umich](https://quod.lib.umich.edu/a/apis)

## Judaea and Jewish communities

### Sefaria

Sefaria is the most technically convenient free source for structured Jewish texts, but it must be treated as a **versioned rights container**, not as one uniformly licensed corpus.

- Retrieve passages through the current v3 endpoint: `https://www.sefaria.org/api/v3/texts/{tref}`.
- Request source language, translation, primary version, all versions, or a named language/version.
- Use `return_format=text_only` when a clean text representation is appropriate.
- For large-scale use, prefer Sefaria’s full export rather than repeatedly harvesting the live API.
- Retain the `license`, version title, language, source, and attribution of every imported version.

Sefaria’s documentation says each language-version has its own copyright status; texts may be public domain, CC-licensed, or have no verified license. It provides text-level downloads in TXT, CSV, or JSON, and community translations may be CC0 while printed editions can be more restrictive. The API supplies structured JSON access, but Sefaria instructs users seeking a local database to use the complete data dump instead of crawling the API. [developers.sefaria](https://developers.sefaria.org/docs/usage-of-our-name-and-logo)

### Dead Sea Scrolls

The Leon Levy and Israel Museum projects are valuable for manuscript inspection, material culture, paleography, and variant readings, but their online availability should not be interpreted as blanket permission for image training. The Leon Levy library supplies searchable high-resolution images of hundreds of manuscripts, while the Israel Museum project offers detailed imagery of selected scrolls. [dtl2.libguides](https://dtl2.libguides.com/c.php?g=1145818)

Recommended mode:

- **C: consultative** for images unless a specific record provides machine-learning-compatible rights.
- Store manuscript identifier, cave/site, language, script, composition type, date, and canonical image URL.
- Use openly licensed scholarly transcriptions from another source when available rather than attempting OCR-based corpus extraction from controlled images.

## Parthian and Sasanian Persia

### Persian and Mesopotamian evidence

| Source | Material | Retrieval | Rights and use |
|---|---|---|---|
| [CDLI](https://cdli.earth/) | Cuneiform artifacts, catalog metadata, transliterations, some translations, provenances, periods, rulers, genres, and images | Daily bulk packages; GitHub data; API/client exports in CSV or N-Triples; online search | **A/B**: public catalogue/transliteration data are distributed in bulk, while individual images or contributed editions may need record-level checking |
| [ORACC](http://oracc.museum.upenn.edu/) | Richly annotated editions of cuneiform texts across many subprojects | Online search/read; project data and structured exports where supplied | **A/B**: default ORACC project license is CC BY-SA 3.0, but project-specific notices control |
| [Achemenet](http://www.achemenet.com/) | Achaemenid inscriptions, Babylonian materials, images, archaeological publications, and research resources | Web reading; the Babylonian text snapshot is searchable in Korp with result downloads | **B/C** until the selected corpus’s reuse statement is captured |
| [Persepolis Fortification Archive](https://voices.uchicago.edu/ochre/project/pfa/) | Administrative tablets in Elamite and Aramaic, seals, glossaries, catalogues, and high-resolution imagery | OCHRE web database; linked records and imagery; related records in CDLI and Achemenet | **B/C**: extensive online availability, but confirm rights for texts and images before ingestion |
| [TITUS Avestan Corpus](http://titus.uni-frankfurt.de/) | Avestan religious texts and linguistic corpus | Browser and HTTP-downloadable files where enabled | **B/C**: stated as freely usable for scholarly purposes with source citation; this is not necessarily unrestricted commercial or general model-training permission |
| [Avesta.org](https://www.avesta.org/) | Avestan, Pahlavi, and English religious materials from public-domain and permission-based editions | HTML reading; selected PDF and EPUB downloads | **B/C**: rights vary by edition; some modern materials are expressly used with permission |

CDLI offers daily catalogue and transliteration packages both from its bulk-data service and GitHub. Its API client can export entities such as artifacts, periods, proveniences, inscriptions, rulers, and languages as CSV or N-Triples and can search by transliteration or translation. This makes CDLI highly suitable for economic, administrative, political, legal, linguistic, and scientific agents, provided that images remain under a separate rights check. [cdli](https://cdli.earth/postings/201)

ORACC’s default policy is CC BY-SA 3.0 because the project favors reusable scholarly data, but individual ORACC projects can publish distinct terms. Store the ORACC project code and its license alongside every text. [oracc.ub.uni-muenchen](http://oracc.ub.uni-muenchen.de/doc/about/aboutoracc/index.html)

The Persepolis Fortification Archive is an exceptional economic and administrative source: its records connect texts, languages, scripts, tablets, seals, and institutional practices. The project reports thousands of text editions and seal records, delivered through OCHRE’s relational environment. Treat the interface as a discovery and consultation source until permission for systematic export and reuse has been confirmed. [voices.uchicago](https://voices.uchicago.edu/ochre/project/pfa/)

TITUS states that HTTP-downloadable texts may be used freely for scholarly purposes if cited. Because “scholarly purposes” may be narrower than commercial model development, route TITUS through legal review rather than automatically assigning it to unrestricted ingestion. [titus.uni-frankfurt](http://titus.uni-frankfurt.de/texte/etcs/iran/airan/avesta/avest180.htm)

## Mesopotamian kingdoms and empires

These sources cover earlier traditions that persisted into the Hellenistic, Parthian, and Roman environments, as well as Babylonian and Assyrian records directly relevant to Persian and Seleucid governance.

| Source | Best use | Retrieval and status |
|---|---|---|
| CDLI | Administrative archives, economy, law, astronomy, scholarship, kingship, religion, material objects | Prefer versioned daily bulk packages and GitHub snapshots; use API export for selected entity classes. [cdli](https://cdli.earth/postings/201) |
| ORACC | Annotated editions and language-aware corpora, including royal, scholarly, lexical, literary, and administrative material | Inspect each subproject’s license; default is CC BY-SA 3.0. [oracc.ub.uni-muenchen](http://oracc.ub.uni-muenchen.de/doc/about/aboutoracc/index.html) |
| [ETCSL](https://etcsl.orinst.ox.ac.uk/) | Sumerian literary compositions in transliteration and English translation; useful background for later Mesopotamian religion and scribal culture | Read and search online. The site asserts project copyright and moral rights; third-party descriptions of Creative Commons status conflict, so classify as **C** until rights are clarified. [etcsl.orinst.ox.ac](https://etcsl.orinst.ox.ac.uk/) |
| Achemenet Babylonian/Korp | Babylonian texts in the Achaemenid setting, with automatic lemmatization and concordance facilities | Query online; download search results. Confirm corpus-level terms before building a local copy. [achemenet](http://www.achemenet.com/en/tree/?/textual-sources/texts-by-languages-and-scripts/babylonian) |

ETCSL illustrates why license verification must examine the originating site rather than an aggregator. Oxford’s pages contain copyright assertions, while an external repository describes a CC license; the discrepancy should block bulk admission pending clarification. [etcsl.orinst.ox.ac](https://etcsl.orinst.ox.ac.uk/credits.htm)

## Syriac communities

Syriac textual culture crosses the Roman–Persian frontier and later the Byzantine, Sasanian, and early Islamic worlds. It therefore supports agents studying diplomacy, Christianity, philosophy, medicine, translation, monasticism, education, and minority communities.

### Primary recommendations

- **Digital Syriac Corpus:** download TEI/XML directly from the project repository under CC BY 4.0; preserve encoder and edition attribution. [github](https://github.com/srophe/syriac-corpus)
- **Syriaca.org:** use stable identifiers for authors, saints, persons, places, works, and relationships. The New Handbook of Syriac Literature uses TEI/XML and RDF and licenses its data under CC BY 4.0. [syriaca](https://syriaca.org/nhsl)
- **Syriac Gazetteer:** integrate its place records with Pleiades and WHG. It is released under CC BY and expressly permits distribution, remixing, and commercial reuse with attribution. [syriaca](https://syriaca.org/geo/about.html)
- **ETCBC Syriac Corpus:** useful morphologically processed material, but CC BY-NC 4.0 limits commercial use. [github](https://github.com/etcbc/syriac)

The Syriaca software framework supports HTML, TEI, JSON-LD, GeoJSON, KML, RDF/XML, RDF/Turtle, and plain-text representations. This makes it a strong source for entity resolution and knowledge-graph enrichment as well as textual retrieval. [github](https://github.com/srophe/syriaca)

## North Arabia and Nabataea

### OCIANA

The [Online Corpus of the Inscriptions of Ancient North Arabia](https://ociana.osu.edu/) is directly relevant to Nabataean, Roman-Arabian, caravan, nomadic, religious, linguistic, and social history.

Recommended handling:

- Use the website for record-level reading, search, transliteration, commentary, bibliography, and imagery.
- Download images only where the interface expressly provides a download.
- Record inscription identifier, script/language, provenance, date, text type, personal names, divine names, and geographic references.
- Do not infer a corpus-wide training license solely from free access or downloadable images.

OCIANA states that images are freely downloadable at publishable resolution where the original is adequate. This statement concerns images and resolution; the license governing transcriptions, translations, annotations, and bulk automated acquisition should be confirmed separately before ingestion. [ociana.osu](https://ociana.osu.edu/)

### Additional gap

A dedicated follow-up pass should evaluate Nabataean, Palmyrene, Safaitic, Ancient South Arabian, and pre-Islamic Arabian epigraphic projects individually. They are central to political frontiers, caravan commerce, religion, language contact, military recruitment, and Roman provincial administration, but many mix open metadata with more controlled editions or photographs.

## Early Islamic successor polities

Although chronologically post-Roman in the West, early Islamic sources are essential for studying continuity from the Eastern Roman, Sasanian, Syriac, Coptic, Jewish, and Arabian worlds.

| Source | Material | Retrieval | Rights and use |
|---|---|---|---|
| [OpenITI](https://openiti.org/) | Premodern Arabic and Persian texts, including histories, biography, geography, law, theology, Qurʾanic sciences, medicine, and literature | Complete versioned releases through GitHub and Zenodo; active Git repositories; searchable metadata interface; OpenITI mARkdown | **A with restriction**: CC BY-NC-SA 4.0; suitable for noncommercial workflows with attribution and share-alike compliance |
| [Quranic Arabic Corpus](https://corpus.quran.com/) | Qurʾanic morphology, syntax, grammar, and concept ontology | Online interface; source and datasets through the project repository | **A/B**: GPL-3.0 repository; distinguish software/data obligations and verify the included text edition |
| [Corpus Coranicum](https://corpuscoranicum.de/) | Manuscript and oral textual history, contextual Jewish/Christian/Arabian texts, chronology, and literary commentary | Online database; website software on GitHub | **B**: website software is GPL-3.0, but software licensing does not automatically determine the rights in every database record, image, or editorial text |
| [Thesaurus d’Épigraphie Islamique](https://www.epigraphie-islamique.uliege.be/Thesaurus/) | Arabic, Persian, Turkish, and other inscriptions across the Islamic world | Free online search and reading | **C/B**: free access, but an independent resource registry reports no identified reuse license; seek permission or formal terms before bulk ingestion |
| Coptic SCRIPTORIUM | Egyptian Christian continuities and Arabic-linked corpora | GitHub, Zenodo, ANNIS, TEI/XML, CoNLL-U | **A/B** by document |
| Digital Syriac Corpus and Syriaca.org | Syriac continuities under early Islamic rule | Git/TEI/API/linked data | **A** under CC BY for identified datasets |

OpenITI’s documentation identifies GitHub as the active corpus and Zenodo as the home of citable release snapshots; it licenses releases under CC BY-NC-SA 4.0. Prefer Zenodo releases for reproducibility and keep OpenITI URIs for individual files. [openiti](http://openiti.org/documentation/)

The Quranic Arabic Corpus describes itself as open source under the GNU public license, and its repository is GPL-3.0. Because GPL was designed principally for software, the ingestion policy should separately identify the license and provenance of the Qurʾanic base text and annotations. [corpus.quran](https://corpus.quran.com/)

Corpus Coranicum’s interface includes manuscript history, contextual texts, and chronological-literary commentary. Its website code is GPL-3.0, but agents should not treat that software license as blanket authorization to train on manuscript images or editorial content. [corpuscoranicum](https://corpuscoranicum.de/en/faq)

The Thesaurus d’Épigraphie Islamique is free online and covers inscriptions across the Muslim world through 1000 AH. Since a specialist registry lists its license as unidentified, keep it consultative until explicit reuse terms are obtained. [maxvanberchem](https://maxvanberchem.org/en/thesaurus-d-epigraphie-islamique)

## Carthage and Punic networks

No single source in the present inventory should be presumed to provide a uniformly open, bulk Punic corpus. A practical interim stack is:

- PHI Greek Inscriptions for Greek evidence concerning Punic and North African communities, in consultative mode
- Papyri.info for connected Egyptian and Mediterranean documentary evidence
- Nomisma and coin portals for Carthaginian, Punic, Numidian, and Roman North African monetary evidence
- Pleiades, WHG, and MAPS for place and route normalization
- Museum APIs and institutional collections only after record-level license review

For political agents, emphasize treaties, war, diplomacy, civic institutions, and Roman provincial reorganization. Economic agents should prioritize coinage, harbor networks, amphorae and trade metadata, while religious and linguistic agents require a future dedicated review of Phoenician/Punic inscription corpora.

## Armenia, Pontus, Commagene, Palmyra

These contact-zone polities require multilingual evidence distributed among Greek, Latin, Syriac, Aramaic, Persian, and numismatic resources.

Recommended source combination:

- PHI Greek Inscriptions for search and consultation
- Nomisma-linked coin corpora for rulers, dynasties, mints, and iconography
- Syriaca.org for places, persons, works, and communities in the eastern frontier
- Digital Syriac Corpus for Syriac literary witnesses
- CDLI/ORACC and Achemenet where Mesopotamian or Persian evidence intersects
- Pleiades and WHG for changing names, jurisdictions, and temporal geography

The absence of a single ingestible corpus should be represented to the agent as an evidentiary condition, not filled by silently substituting modern summaries.

## Kushan and Indian Ocean connections

Rome intersected indirectly and commercially with South Asian states through Indian Ocean trade, diplomacy, coin circulation, luxury commodities, and cultural transmission.

### GRETIL

The [Göttingen Register of Electronic Texts in Indian Languages](http://gretil.sub.uni-goettingen.de/) provides machine-readable texts in Sanskrit, Pali, Prakrit, Tamil, and other languages.

- Texts can be read or downloaded individually, and cumulative downloads are available.
- The archive standardizes materials in several encodings.
- It is particularly useful for religion, philosophy, medicine, astronomy, grammar, law, literature, and social thought.
- Date texts and textual layers carefully: the date of a surviving edition or manuscript is not necessarily the date of composition.

GRETIL states that it registers texts freely available for scholarly purposes and that archived files are for reference purposes. A separate description confirms both individual and cumulative downloads. Because these formulations do not amount to a uniform open-content license, classify files as **B/C** and retain each source text’s originating terms. [gretil.sub.uni-goettingen](http://gretil.sub.uni-goettingen.de/gretinfobk.htm)

### Recommended links

Combine approved GRETIL texts with:

- Nomisma-linked Kushan and Indo-Greek numismatic records
- Papyri.info documents concerning Red Sea and Indian Ocean commerce
- MAPS port datasets
- WHG/Pleiades place reconciliation
- ORBIS for the Roman-side transport network

## Han China and indirect Eurasian contact

The Han world belongs in scope only if “intersection” includes indirect exchange, geographical knowledge, diplomatic chains, and Silk Road connectivity.

### Chinese Text Project

The [Chinese Text Project](https://ctext.org/) is a major digital library for pre-Qin and Han texts, including classics, histories, philosophy, and collected works.

- Browse and search online.
- Use its JSON API and textual URNs for targeted retrieval.
- The API is explicitly designed for both offline text mining and live integration.
- Record the edition, transcription status, and translation rights separately.

The project’s scholarly description explains that the API retrieves arbitrary corpus subsets in machine-readable JSON and was designed to support offline text mining as well as online applications. Open access to the platform should not be interpreted as a uniform license for all scans, transcriptions, or translations; perform item-level rights checks. [academic.oup](https://academic.oup.com/dsh/article/36/Supplement_1/i101/5556365)

### CHANT

CHANT contains searchable traditional and excavated texts, including bronze inscriptions and wood, bamboo, and silk manuscripts, but it is institutionally licensed and prohibits derivative works without written permission. It should therefore be excluded from automatic corpus ingestion unless the operator obtains an appropriate license. [guides.lib.unc](https://guides.lib.unc.edu/go23609235)

## Lens-to-source guide

| Agent lens | Highest-priority sources | Typical evidence |
|---|---|---|
| Political | PHI inscriptions as consultative evidence; Open Greek and Latin; Syriaca; CDLI/ORACC; Seshat; coins | Decrees, royal titles, diplomacy, administrative offices, political narrative, boundaries |
| Economic | Papyri.info; CDLI; OCRE/CRRO; Nomisma; ORBIS; MAPS; Persepolis Archive | Accounts, receipts, tax, wages, leases, coinage, transport cost, ports, supply systems |
| Religious | Sefaria; Coptic SCRIPTORIUM; Digital Syriac Corpus; Quranic Arabic Corpus; Corpus Coranicum; OCIANA; Avestan resources | Scripture, commentary, liturgy, dedications, divine names, monastic rules, ritual |
| Social | Papyri.info; Coptic SCRIPTORIUM; inscriptions; Sefaria; OpenITI | Household documents, letters, epitaphs, status, occupation, gender, slavery, associations |
| Artistic | OCRE/CRRO; Nomisma; Musisque Deoque; inscriptions and monument records | Iconography, portraiture, poetic form, visual programs, dedications, material description |
| Scientific | Open Greek and Latin; DigilibLT; OpenITI; GRETIL; CDLI/ORACC | Medicine, astronomy, mathematics, geography, grammar, natural philosophy |
| Legal | Papyri.info; Sefaria; Roman legal texts in open Latin repositories; inscriptions; OpenITI | Contracts, petitions, statutes, responsa, legal compilations, administrative decisions |
| Military | OCRE/CRRO; ORBIS; inscriptions; literary historians; MAPS | Campaign narrative, units, recruitment, forts, roads, logistics, military titulature |
| Linguistic | Coptic SCRIPTORIUM; Digital Syriac Corpus; Quranic Arabic Corpus; CDLI/ORACC; DigilibLT | Morphology, syntax, lemmata, named entities, parallel editions, linguistic change |
| Geographic | Pleiades; WHG; Syriac Gazetteer; ORBIS; MAPS; Recogito | Toponyms, routes, temporal names, coordinates, place relations, transport networks |

## Retrieval policy for agents

### Bulk-first hierarchy

Agents should prefer retrieval in this order:

1. Versioned institutional or Zenodo release
2. Official Git repository with release tags
3. Documented bulk dump
4. Documented API or SPARQL endpoint
5. Stable record-level machine representation such as TEI/XML, RDF, JSON-LD, or IIIF
6. Browser reading and citation
7. Scraping only where terms expressly permit it and no supported retrieval mechanism exists

This avoids placing unnecessary load on scholarly services and yields reproducible corpora. Sefaria, for example, explicitly recommends complete data dumps rather than using its API to reconstruct a local database. OpenITI similarly distinguishes active GitHub data from citable Zenodo snapshots. [github](https://github.com/Sefaria/Sefaria-Project/wiki/API-Documentation/948bb3dcf283653163a2d0a6b88dca152cabaf76)

### Format preferences

- **TEI/EpiDoc:** retain both source XML and normalized plain text; map `<persName>`, `<placeName>`, dates, bibliographic references, supplied text, gaps, and editorial restorations.
- **RDF/JSON-LD:** preserve source URIs and provenance; do not collapse asserted identity and approximate matching.
- **CoNLL-U:** retain token identifiers, lemmas, morphology, syntactic relations, and sentence/document boundaries.
- **OpenITI mARkdown:** use the official parser and preserve page markers and structural tags.
- **ATF/cuneiform formats:** preserve signs, transliteration conventions, line numbers, damage markers, and language metadata.
- **Images/IIIF:** store manifests and rights metadata separately from image binaries; do not train on images whose rights only permit viewing.
- **PDF/EPUB/HTML:** use only when structured source files are unavailable and automated extraction is permitted.

## Evidentiary safeguards

Ancient-history agents should receive explicit uncertainty features rather than only normalized prose:

- Original text versus modern translation
- Diplomatic transcription versus normalized text
- Restored, supplied, damaged, or uncertain characters
- Approximate, disputed, or inferred date
- Findspot versus presumed origin
- Ancient polity versus modern country
- Contemporary evidence versus later retrospective narrative
- Object-level evidence versus scholarly interpretation
- Named individual versus reconstructed prosopographic identity
- Text composition date versus manuscript or inscription date
- Modern editorial edition and version lineage

For coins, distinguish **type**, **specimen**, and **hoard/find**. For papyri, distinguish **object**, **document**, **edition**, **translation**, and **image**. For inscriptions, distinguish the physical monument, text-bearing surface, edition, restoration, translation, and current location.

## Licensing controls

Every ingestion job should implement:

- **Deny by default** when no explicit license or permission is present.
- **Version-level checks** for Sefaria, museum records, translations, and contributed corpora.
- **Noncommercial partitioning** for OpenITI, MAPS, Seshat, and other NC material.
- **Share-alike partitioning** for ORACC defaults, Musisque Deoque, DigilibLT, and other SA resources.
- **Software/content separation** for Corpus Coranicum, Quranic Arabic Corpus, Recogito, Syriaca frameworks, and similar projects.
- **Image/text separation** for papyri, manuscripts, inscriptions, coins, and museum objects.
- **Attribution manifests** generated with every corpus release and downstream model.
- **Removal capability** keyed to source and item identifiers.
- **No license laundering:** a copy found in GitHub, an aggregator, or a research repository does not override the originating edition’s terms.

## Recommended initial ingestion set

A relatively low-friction first corpus would include:

1. DigilibLT’s approved TEI/XML under CC BY-SA 4.0. [github](https://github.com/CIRCSE/digilibLT)
2. Coptic SCRIPTORIUM documents whose manifests identify CC BY or compatible CC BY-SA terms. [github](https://github.com/CopticScriptorium/corpora)
3. Digital Syriac Corpus TEI under CC BY 4.0. [github](https://github.com/srophe/syriac-corpus)
4. Syriaca.org and Syriac Gazetteer linked data under CC BY. [syriaca](https://syriaca.org/nhsl)
5. Nomisma concepts and approved bulk data under CC BY. [reviewsindh.pubpub](https://reviewsindh.pubpub.org/pub/nomisma)
6. OCRE type data under ODbL, with museum images excluded unless separately approved. [numismatics](https://numismatics.org/ocre/search)
7. CDLI catalogue and transliteration dumps after confirming the rights notice attached to the selected release. [cdli-gh.github](https://cdli-gh.github.io/guides/guide_tools_list.html)
8. ORACC projects whose project page confirms CC BY-SA or another compatible license. [oracc.ub.uni-muenchen](http://oracc.ub.uni-muenchen.de/doc/about/aboutoracc/index.html)
9. Papyri.info DDbDP/EpiDoc content carrying CC BY 3.0, with APIS images evaluated separately. [papyri](https://papyri.info/current/5496)
10. Musisque Deoque’s identified CLARIN release under CC BY-SA 4.0. [dspace-clarin-it.ilc.cnr](https://dspace-clarin-it.ilc.cnr.it/items/861c199b-a0ff-448e-9101-8acbff7d6586)
11. OpenITI only inside a noncommercial/share-alike partition. [zenodo](https://zenodo.org/records/6808108)
12. Sefaria texts only after filtering each version by its embedded license field. [github](https://github.com/Sefaria/Sefaria-Export-Archive/blob/master/LICENSE.md)

Keep PHI Greek Inscriptions, ETCSL, TITUS, OCIANA’s non-image content, Achemenet, the Persepolis Archive, Dead Sea Scrolls image portals, Thesaurus d’Épigraphie Islamique, GRETIL, Chinese Text Project materials lacking an explicit item license, and CHANT in consultative or conditional lanes until their relevant permissions are verified.