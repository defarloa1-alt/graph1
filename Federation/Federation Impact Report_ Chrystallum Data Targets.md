# Federation Impact Report: Chrystallum Data Targets

Status: technical reference (federation catalog)
Canonical architecture anchor: `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
Governance anchor: `md/Architecture/ADR-002-Policy-Gate-and-Update-Operator-Separation.md`

## 1. Wikidata (The Central Hub)

### 1.1. Role: Primary "Backbone"

### 1.2. API Endpoint

#### 1.2.1. Action API: https://www.wikidata.org/w/api.php

#### 1.2.2. SPARQL: https://query.wikidata.org/sparql

### 1.3. Data Elements Provided

#### 1.3.1. Core Identity: Labels, Aliases, Descriptions

#### 1.3.2. Ontology: Instance Of (P31), Subclass Of (P279)

#### 1.3.3. External IDs: Links to other federations

### 1.4. Federations it has: Links to everything

#### 1.4.1. VIAF (Virtual International Authority File)

##### 1.4.1.1. ISNI (International Standard Name Identifier)

###### 1.4.1.1.1. ORCID (Open Researcher and Contributor ID)

###### 1.4.1.1.2. Research Organization Registry (ROR)

##### 1.4.1.2. LCCN (Library of Congress Control Number)

###### 1.4.1.2.1. MARC (Machine-Readable Cataloging)

###### 1.4.1.2.2. NACO (Name Authority Cooperative Program)

##### 1.4.1.3. WorldCat (OCLC)

###### 1.4.1.3.1. Library Catalogs

###### 1.4.1.3.2. ISBN Databases

#### 1.4.2. GND (Gemeinsame Normdatei)

##### 1.4.2.1. DNB (Deutsche Nationalbibliothek)

###### 1.4.2.1.1. German National Bibliography

###### 1.4.2.1.2. ZDB (Zeitschriftendatenbank)

##### 1.4.2.2. KVK (Karlsruhe Virtual Catalog)

###### 1.4.2.2.1. Academic Library Catalogs

###### 1.4.2.2.2. Union Catalogues

#### 1.4.3. Library of Congress (LoC)

##### 1.4.3.1. MARC (Machine-Readable Cataloging)

###### 1.4.3.1.1. Library Automation Systems

###### 1.4.3.1.2. Cataloging Standards

##### 1.4.3.2. NACO (Name Authority Cooperative Program)

###### 1.4.3.2.1. Authority File Contributions

###### 1.4.3.2.2. LC Name Authority File (LCNAF)

#### 1.4.4. ISNI (International Standard Name Identifier)

##### 1.4.4.1. ORCID (Open Researcher and Contributor ID)

###### 1.4.4.1.1. Scopus Author ID

###### 1.4.4.1.2. Web of Science ResearcherID

##### 1.4.4.2. Research Organization Registry (ROR)

###### 1.4.4.2.1. GRID (Global Research Identifier Database)

###### 1.4.4.2.2. Crossref Funder Registry

#### 1.4.5. ORCID (Open Researcher and Contributor ID)

##### 1.4.5.1. Scopus Author ID

###### 1.4.5.1.1. Elsevier Publications

###### 1.4.5.1.2. Citation Indexes

##### 1.4.5.2. Web of Science ResearcherID

###### 1.4.5.2.1. Clarivate Analytics

###### 1.4.5.2.2. Journal Impact Factors

#### 1.4.6. GeoNames

##### 1.4.6.1. OpenStreetMap

###### 1.4.6.1.1. OSM Data API

###### 1.4.6.1.2. Overpass API

##### 1.4.6.2. Google Maps

###### 1.4.6.2.1. Google Places API

###### 1.4.6.2.2. Google Earth

#### 1.4.7. Pleiades

##### 1.4.7.1. Digital Atlas of the Roman Empire (DARE)

###### 1.4.7.1.1. Period Maps

###### 1.4.7.1.2. Historical GIS

##### 1.4.7.2. AWMC (Ancient World Mapping Center)

###### 1.4.7.2.1. Barrington Atlas

###### 1.4.7.2.2. Pelagios Network

## 2. Pleiades (Gazetteer of Ancient World)

### 2.1. Role: "Authority" for Ancient Places

### 2.2. API / Data

#### 2.2.1. JSON API: https://pleiades.stoa.org/places/[ID]/json

#### 2.2.2. Bulk CSV: https://github.com/isawnyu/pleiades.datasets

### 2.3. Data Elements

#### 2.3.1. Coordinates: Precise lat/long

#### 2.3.2. Time Periods: Validated temporal scopes

#### 2.3.3. Name Variants: Ancient vs. Modern

### 2.4. Federations it has

#### 2.4.1. Geonames: Modern mapping

##### 2.4.1.1. Wikipedia

###### 2.4.1.1.1. Wikidata

###### 2.4.1.1.2. Wikimedia Commons

##### 2.4.1.2. OpenStreetMap

###### 2.4.1.2.1. OSM Data API

###### 2.4.1.2.2. Mapbox

#### 2.4.2. Trismegistos: Papyrology/Epigraphy

##### 2.4.2.1. DDbDP (Duke Databank of Documentary Papyri)

###### 2.4.2.1.1. Papyri.info

###### 2.4.2.1.2. APIS (Advanced Papyrological Information System)

##### 2.4.2.2. HGV (Heidelberger Gesamtverzeichnis)

###### 2.4.2.2.1. Papyri.info

###### 2.4.2.2.2. DDbDP (Duke Databank of Documentary Papyri)

#### 2.4.3. Digital Atlas of the Roman Empire (DARE)

##### 2.4.3.1. Google Maps

###### 2.4.3.1.1. Google Earth

###### 2.4.3.1.2. Google Places API

##### 2.4.3.2. Vici.org

###### 2.4.3.2.1. OpenStreetMap

###### 2.4.3.2.2. Wikipedia

#### 2.4.4. ORBIS: The Stanford Geospatial Network Model of the Roman World

##### 2.4.4.1. Classical Atlas Project

###### 2.4.4.1.1. Ancient Geography Databases

###### 2.4.4.1.2. Historical Maps

#### 2.4.5. AWMC (Ancient World Mapping Center)

##### 2.4.5.1. Pelagios Network

###### 2.4.5.1.1. Recogito (annotation tool)

###### 2.4.5.1.2. Peripleo (discovery engine)

## 3. Trismegistos (Epigraphic/Papyrological Hub)

### 3.1. Role: "Authority" for Texts, Collections, People

### 3.2. API Endpoint: https://www.trismegistos.org/api/

### 3.3. Data Elements

#### 3.3.1. TM_Geo: IDs for places in texts

#### 3.3.2. TM_People: Prosopography of non-elites

#### 3.3.3. TM_Texts: Metadata on papyri/inscriptions

### 3.4. Federations it has

#### 3.4.1. Pleiades

##### 3.4.1.1. Geonames

###### 3.4.1.1.1. Wikipedia

###### 3.4.1.1.2. OpenStreetMap

##### 3.4.1.2. DARE

###### 3.4.1.2.1. Google Maps

###### 3.4.1.2.2. Vici.org

#### 3.4.2. Heidelberg (EDH)

##### 3.4.2.1. Clauss-Slaby (EDCS)

###### 3.4.2.1.1. CIL (Corpus Inscriptionum Latinarum)

###### 3.4.2.1.2. Epigraphik-Datenbank

##### 3.4.2.2. CIL (Corpus Inscriptionum Latinarum)

###### 3.4.2.2.1. EDH (Epigraphic Database Heidelberg)

###### 3.4.2.2.2. EDCS (Epigraphik-Datenbank Clauss-Slaby)

#### 3.4.3. Leuven Database of Ancient Books (LDAB)

##### 3.4.3.1. TLG (Thesaurus Linguae Graecae)

###### 3.4.3.1.1. Greek Text Corpora

###### 3.4.3.1.2. Lexica

##### 3.4.3.2. PHI (Packard Humanities Institute)

###### 3.4.3.2.1. Latin Text Corpora

###### 3.4.3.2.2. Greek Text Corpora

#### 3.4.4. Papyri.info (umbrella database)

##### 3.4.4.1. APIS (Advanced Papyrological Information System)

###### 3.4.4.1.1. Papyrological Collections

###### 3.4.4.1.2. Digital Images

##### 3.4.4.2. Checklist of Greek, Latin, Demotic and Coptic Papyri, Ostraca and Tablets

###### 3.4.4.2.1. Papyrological Bibliographies

###### 3.4.4.2.2. Online Catalogues

#### 3.4.5. DDbDP (Duke Databank of Documentary Papyri)

##### 3.4.5.1. HGV (Heidelberger Gesamtverzeichnis)

###### 3.4.5.1.1. Papyri.info

###### 3.4.5.1.2. DDbDP (Duke Databank of Documentary Papyri)

##### 3.4.5.2. Papyri.info

###### 3.4.5.2.1. APIS

###### 3.4.5.2.2. HGV

#### 3.4.6. HGV (Heidelberger Gesamtverzeichnis der griechischen Papyrusurkunden)

##### 3.4.6.1. DDbDP (Duke Databank of Documentary Papyri)

###### 3.4.6.1.1. Papyri.info

###### 3.4.6.1.2. APIS

##### 3.4.6.2. Papyri.info

###### 3.4.6.2.1. APIS

###### 3.4.6.2.2. DDbDP

## 4. Epigraphic Database Heidelberg (EDH)

### 4.1. Role: Source for Latin Inscriptions

### 4.2. API Endpoint: https://edh.ub.uni-heidelberg.de/data/api

### 4.3. Data Elements

#### 4.3.1. Inscriptions: Full text, material, dimensions

#### 4.3.2. Findspots: Where the stone was found

#### 4.3.3. Dating: Epigraphic dating ranges

### 4.4. Federations it has

#### 4.4.1. Clauss-Slaby (EDCS)

##### 4.4.1.1. CIL (Corpus Inscriptionum Latinarum)

###### 4.4.1.1.1. EDH (Epigraphic Database Heidelberg)

###### 4.4.1.1.2. RIB (Roman Inscriptions of Britain)

##### 4.4.1.2. Epigraphik-Datenbank

###### 4.4.1.2.1. German Epigraphic Projects

###### 4.4.1.2.2. International Epigraphic Resources

#### 4.4.2. Trismegistos

##### 4.4.2.1. DDbDP (Duke Databank of Documentary Papyri)

###### 4.4.2.1.1. Papyri.info

###### 4.4.2.1.2. APIS

##### 4.4.2.2. HGV (Heidelberger Gesamtverzeichnis)

###### 4.4.2.2.1. Papyri.info

###### 4.4.2.2.2. DDbDP

#### 4.4.3. Roman Inscriptions of Britain (RIB)

##### 4.4.3.1. CIL (Corpus Inscriptionum Latinarum)

###### 4.4.3.1.1. EDH (Epigraphic Database Heidelberg)

###### 4.4.3.1.2. EDCS (Epigraphik-Datenbank Clauss-Slaby)

##### 4.4.3.2. EPNet (Epigraphic Project Network)

###### 4.4.3.2.1. International Epigraphic Projects

###### 4.4.3.2.2. Digital Epigraphy

#### 4.4.4. CIL (Corpus Inscriptionum Latinarum)

##### 4.4.4.1. EDH (Epigraphic Database Heidelberg)

###### 4.4.4.1.1. EDCS (Epigraphik-Datenbank Clauss-Slaby)

###### 4.4.4.1.2. Trismegistos

##### 4.4.4.2. EDCS (Epigraphik-Datenbank Clauss-Slaby)

###### 4.4.4.2.1. CIL (Corpus Inscriptionum Latinarum)

###### 4.4.4.2.2. Epigraphik-Datenbank

#### 4.4.5. EAGLE (Europeana Archaeology: Gathering, Linking, Exploring)

##### 4.4.5.1. Europeana

###### 4.4.5.1.1. Digital Cultural Heritage Aggregators

###### 4.4.5.1.2. Museum and Archive Collections

##### 4.4.5.2. ARIADNE (Advanced Research Infrastructure for Archaeological Data Networking in Europe)

###### 4.4.5.2.1. Archaeological Data Repositories

###### 4.4.5.2.2. National Archaeology Services

## 5. VIAF (Virtual International Authority File)

### 5.1. Role: "Authority" for People and Works

### 5.2. API Endpoint: https://viaf.org/viaf/[ID]/viaf.json

### 5.3. Data Elements

#### 5.3.1. Name Authorities: How "Caesar" is spelled

#### 5.3.2. Works: Lists of authored texts

### 5.4. Federations it has

#### 5.4.1. WorldCat (OCLC)

##### 5.4.1.1. Library Holdings

###### 5.4.1.1.1. Member Libraries

###### 5.4.1.1.2. Interlibrary Loan Networks

##### 5.4.1.2. ISBNs (International Standard Book Numbers)

###### 5.4.1.2.1. Book Publishing Industry

###### 5.4.1.2.2. National Bibliographies

#### 5.4.2. ISNI (International Standard Name Identifier)

##### 5.4.2.1. ORCID (Open Researcher and Contributor ID)

###### 5.4.2.1.1. Scopus Author ID

###### 5.4.2.1.2. Web of Science ResearcherID

##### 5.4.2.2. Research Organization Registry (ROR)

###### 5.4.2.2.1. GRID (Global Research Identifier Database)

###### 5.4.2.2.2. Crossref Funder Registry

#### 5.4.3. National Libraries (US, Germany, France)

##### 5.4.3.1. Library of Congress (LoC)

###### 5.4.3.1.1. MARC (Machine-Readable Cataloging)

###### 5.4.3.1.2. NACO (Name Authority Cooperative Program)

##### 5.4.3.2. DNB (Deutsche Nationalbibliothek)

###### 5.4.3.2.1. German National Bibliography

###### 5.4.3.2.2. ZDB (Zeitschriftendatenbank)

##### 5.4.3.3. BnF (Bibliotheque nationale de France)

###### 5.4.3.3.1. Gallica

###### 5.4.3.3.2. Data.bnf.fr

#### 5.4.4. GND (Gemeinsame Normdatei)

##### 5.4.4.1. DNB (Deutsche Nationalbibliothek)

###### 5.4.4.1.1. German National Bibliography

###### 5.4.4.1.2. ZDB (Zeitschriftendatenbank)

##### 5.4.4.2. KVK (Karlsruhe Virtual Catalog)

###### 5.4.4.2.1. Academic Library Catalogs

###### 5.4.4.2.2. Union Catalogues

#### 5.4.5. BnF (Bibliotheque nationale de France)

##### 5.4.5.1. Gallica

###### 5.4.5.1.1. Digital Collections

###### 5.4.5.1.2. Bibliographic Data

##### 5.4.5.2. Data.bnf.fr

###### 5.4.5.2.1. Linked Open Data Portal

###### 5.4.5.2.2. RDF Triple Store

#### 5.4.6. NLI (National Library of Israel)

##### 5.4.6.1. National Library of Israel Catalog

###### 5.4.6.1.1. Hebrew & Jewish Collections

###### 5.4.6.1.2. Digitized Manuscripts

#### 5.4.7. JPNO (Japan National Library Online)

##### 5.4.7.1. National Diet Library (NDL)

###### 5.4.7.1.1. NDL Online

###### 5.4.7.1.2. NDL Digital Collections

## 6. Summary Table for Ingestion Config

### 6.1. Pleiades

#### 6.1.1. Key Property (Wikidata): P1584

#### 6.1.2. Primary Entity Type: Place

#### 6.1.3. API Style: JSON / Bulk CSV

### 6.2. Trismegistos

#### 6.2.1. Key Property (Wikidata): P1958 (Place), P4230 (Text)

#### 6.2.2. Primary Entity Type: Place, Text, Person

#### 6.2.3. API Style: REST / Lookup

### 6.3. Heidelberg

#### 6.3.1. Key Property (Wikidata): P2192

#### 6.3.2. Primary Entity Type: Inscription / Event Evidence

#### 6.3.3. API Style: REST JSON

### 6.4. VIAF

#### 6.4.1. Key Property (Wikidata): P214

#### 6.4.2. Primary Entity Type: Person, Work

#### 6.4.3. API Style: Linked Data JSON

### 6.5. GeoNames

#### 6.5.1. Key Property (Wikidata): P1566

#### 6.5.2. Primary Entity Type: Modern Location

#### 6.5.3. API Style: REST

## 7. Governance Overlay (Mandatory Before Canonical Write)

### 7.1. Canonical write policy

#### 7.1.1. Federation harvest does not write canonical graph directly.

#### 7.1.2. All mutation paths follow U -> Pi -> Commit.

#### 7.1.3. Rejections are persisted with machine-readable reason codes.

### 7.2. Required proposal artifact fields

#### 7.2.1. source_system

#### 7.2.2. source_uri

#### 7.2.3. target_label

#### 7.2.4. match_type

#### 7.2.5. mapping_confidence

#### 7.2.6. evidence

#### 7.2.7. analysis_run_id

#### 7.2.8. review_status

### 7.3. Gate checks

#### 7.3.1. Schema and policy conformance

#### 7.3.2. Provenance completeness and run scope

#### 7.3.3. Threshold and reviewer gate evaluation

#### 7.3.4. Commit only approved candidates

## 8. Implementation Status Snapshot (2026-02-18)

### 8.1. Active adapters/scripts in repository

#### 8.1.1. Wikidata discovery/profile pipeline in scripts/tools/wikidata_*

#### 8.1.2. Pleiades ingest pipeline in scripts/backbone/geographic/

### 8.2. Planned adapters (architecture-defined, not yet first-class scripts)

#### 8.2.1. Trismegistos

#### 8.2.2. EDH

#### 8.2.3. VIAF

#### 8.2.4. GeoNames

### 8.3. Implementation guidance

#### 8.3.1. Treat this document as a federation target catalog.

#### 8.3.2. Use md/Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md for executable entry points.
