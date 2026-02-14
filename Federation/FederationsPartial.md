#FederationsPartial
I do not have access to your local file `2-13-26-federation-impact.md`, so I cannot generate a report *directly based on its contents*.

However, based on our previous work on the "Caesar" graph and the standard "Federation" targets for Roman History (which are almost certainly the subject of your file), I have reconstructed the likely report below.

This report covers the **Big 5 Federations** that your "backlinks" JSON was hitting (e.g., `federation_id` counts for Pleiades, VIAF, etc.).

***

# Federation Impact Report: Chrystallum Data Targets

This report details the external knowledge graphs (federations) currently integrated or targeted by the Chrystallum ingestion engine. Each entry includes the API details, data elements provided, and their own downstream federations.

## 1. Wikidata (The Central Hub)
*   **Role:** The primary "Backbone" for Chrystallum. It provides the initial `QID` and the "Backlinks" that trigger the ingestion agents.
*   **API Endpoint:** `https://www.wikidata.org/w/api.php` (Action API) or `https://query.wikidata.org/sparql` (SPARQL)
*   **Data Elements Provided:**
    *   **Core Identity:** Labels, Aliases, Descriptions in multiple languages.
    *   **Ontology:** `Instance Of` (P31), `Subclass Of` (P279).
    *   **External IDs:** The "Rosetta Stone" links to all other federations below.
*   **Federations it has:** Links to *everything* (VIAF, Pleiades, GeoNames, Library of Congress, etc.).

## 2. Pleiades (The Gazetteer of the Ancient World)
*   **Role:** The "Authority" for Ancient Places. Used to validate `City`, `Region`, and `Site` nodes.
*   **API / Data:**
    *   **JSON API:** `https://pleiades.stoa.org/places/[ID]/json`
    *   **Bulk CSV:** `https://github.com/isawnyu/pleiades.datasets`
*   **Data Elements:**
    *   **Coordinates:** Precise lat/long for ancient sites.
    *   **Time Periods:** Validated temporal scopes (e.g., "Roman Republic", "Late Antique").
    *   **Name Variants:** Ancient names (Latin, Greek) vs. Modern names.
*   **Federations it has:**
    *   **Geonames:** Modern mapping.
    *   **Trismegistos:** Papyrology/Epigraphy.
    *   **Digital Atlas of the Roman Empire (DARE).**

## 3. Trismegistos (The Epigraphic/Papyrological Hub)
*   **Role:** The "Authority" for Texts, Collections, and People mentioned in ancient documents.
*   **API Endpoint:** `https://www.trismegistos.org/api/` (Requires Key/Permission usually, or bulk data).
*   **Data Elements:**
    *   **TM_Geo:** IDs for places mentioned in texts (more granular than Pleiades for Egypt).
    *   **TM_People:** Prosopography of non-elites (common people in papyri).
    *   **TM_Texts:** Metadata on papyri/inscriptions (dates, materials).
*   **Federations it has:**
    *   **Pleiades**
    *   **Heidelberg (EDH)**
    *   **Leuven Database of Ancient Books (LDAB)**

## 4. Epigraphic Database Heidelberg (EDH)
*   **Role:** The source for Latin Inscriptions. Essential for validating "Event Participants" (e.g., verifying a Legate was in a province via a stone inscription).
*   **API Endpoint:** `https://edh.ub.uni-heidelberg.de/data/api`
*   **Data Elements:**
    *   **Inscriptions:** Full text (Latin), material, dimensions.
    *   **Findspots:** Where the stone was found (linked to Pleiades/GeoNames).
    *   **Dating:** Epigraphic dating ranges (e.g., "70 AD - 90 AD").
*   **Federations it has:**
    *   **Clauss-Slaby (EDCS)**
    *   **Trismegistos**
    *   **Roman Inscriptions of Britain (RIB)**

## 5. VIAF (Virtual International Authority File)
*   **Role:** The "Authority" for People and Works. Used to disambiguate "Cicero" the person from "Cicero" the author.
*   **API Endpoint:** `https://viaf.org/viaf/[ID]/viaf.json`
*   **Data Elements:**
    *   **Name Authorities:** How "Caesar" is spelled in Library of Congress, Deutsche Nationalbibliothek, BnF, etc.
    *   **Works:** Lists of authored texts (e.g., *De Bello Gallico*).
*   **Federations it has:**
    *   **WorldCat (OCLC)**
    *   **ISNI (International Standard Name Identifier)**
    *   **National Libraries** (US, Germany, France, etc.)

### Summary Table for Ingestion Config

| Federation | Key Property (Wikidata) | Primary Entity Type | API Style |
| :--- | :--- | :--- | :--- |
| **Pleiades** | `P1584` | Place | JSON / Bulk CSV |
| **Trismegistos** | `P1958` (Place), `P4230` (Text) | Place, Text, Person | REST / Lookup |
| **Heidelberg** | `P2192` | Inscription / Event Evidence | REST JSON |
| **VIAF** | `P214` | Person, Work | Linked Data JSON |
| **GeoNames** | `P1566` | Modern Location | REST |

*If you paste the content of `2-13-26-federation-impact.md`, I can refine this to match your specific notes exactly.*