<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# does this have any value \# Roman Republic Federation Synthesis — SubjectConcept Proposal

## Context

The Chrystallum project has federated nodes from multiple authorities (DPRR, Pleiades, LCSH, LCC, WorldCat).
Nodes are connected when they share alignment dimensions: TEMPORAL (overlapping dates), GEOGRAPHIC (same place),
INTELLECTUAL (same concept), SOCIAL (same person), BIBLIOGRAPHIC (same text), EVENT (same event).

## Matrix Summary

- **Total nodes:** 40259
- **Total edges:** 26904781


### Nodes by federation

- pleiades: 32572
- dprr: 7335
- worldcat: 196
- lcc: 141
- lcsh: 15


### Edge dimensions (neighbour-dim pairs)

- GEOGRAPHIC: 53809560
- TEMPORAL: 1397002
- SOCIAL: 21710
- INTELLECTUAL: 2


### Cross-federation edges

- Found: 0 in sample of 50000 edges
- Sample (first 200):


### Top 30 nodes by neighbour count

- **pleiades:423025** — Roma
14670 neighbours (TEMPORAL:7335, GEOGRAPHIC:7335)
- **dprr:7373** — aedilis
14649 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313, SOCIAL:1)
- **dprr:8413** — praetor
14649 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313, SOCIAL:1)
- **dprr:10207** — praetor
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7371** — aedilis
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7433** — quaestor
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7543** — praefectus
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7554** — triumvir - unspecified
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7680** — senator - office unknown
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7692** — senator - office unknown
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7812** — praetor
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7872** — senator - office unknown
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:9069** — praetor
14648 neighbours (GEOGRAPHIC:7335, TEMPORAL:7313)
- **dprr:7381** — tribunus plebis
14580 neighbours (GEOGRAPHIC:7335, TEMPORAL:7245)
- **dprr:7389** — tribunus plebis
14580 neighbours (GEOGRAPHIC:7335, TEMPORAL:7245)
- **dprr:7390** — tribunus plebis
14580 neighbours (GEOGRAPHIC:7335, TEMPORAL:7245)
- **dprr:7392** — tribunus plebis
14580 neighbours (GEOGRAPHIC:7335, TEMPORAL:7245)
- **dprr:7397** — tribunus plebis
14580 neighbours (GEOGRAPHIC:7335, TEMPORAL:7245)
- **dprr:7400** — tribunus plebis
14580 neighbours (GEOGRAPHIC:7335, TEMPORAL:7245)
- **dprr:7407** — tribunus plebis
14580 neighbours (GEOGRAPHIC:7335, TEMPORAL:7245)
- **dprr:7414** — tribunus plebis
14580 neighbours (GEOGRAPHIC:7335, TEMPORAL:7245)
- **dprr:7555** — viocurus
14161 neighbours (GEOGRAPHIC:7335, TEMPORAL:6826)
- **dprr:7565** — viocurus
14161 neighbours (GEOGRAPHIC:7335, TEMPORAL:6826)
- **dprr:9318** — quaestor pro praetore
13665 neighbours (GEOGRAPHIC:7335, TEMPORAL:6330)
- **dprr:7502** — proconsul
13474 neighbours (GEOGRAPHIC:7335, TEMPORAL:6139)
- **dprr:7313** — praetor
12751 neighbours (GEOGRAPHIC:7335, TEMPORAL:5416)
- **dprr:7883** — senator - office unknown
12751 neighbours (GEOGRAPHIC:7335, TEMPORAL:5416)
- **dprr:7514** — proquaestor pro propraetore
12729 neighbours (GEOGRAPHIC:7335, TEMPORAL:5394)
- **dprr:8978** — aedilis curulis
11908 neighbours (GEOGRAPHIC:7335, TEMPORAL:4573)
- **dprr:7512** — proconsul
11827 neighbours (GEOGRAPHIC:7335, TEMPORAL:4492)

---

## Your Task

Propose **SubjectConcepts** for the Roman Republic domain (Q17167) based on this federation evidence.

For each proposed SubjectConcept:

1. **Name** — A short label (e.g. 'Offices and Magistracies', 'Rome and Italy')
2. **Evidence** — Which federation nodes or clusters support it? Cite node keys (e.g. dprr:7373, pleiades:423025)
3. **Dimensions** — Which alignment dimensions connect the evidence? (GEOGRAPHIC, TEMPORAL, etc.)
4. **Primary facet** — POLITICAL, MILITARY, SOCIAL, ECONOMIC, RELIGIOUS, CULTURAL, GEOGRAPHIC, etc.

Prioritise clusters that:

- Span multiple federations (cross-federation edges)
- Have strong GEOGRAPHIC or TEMPORAL coherence
- Could serve as thematic anchors for entity organisation

Output your proposals as a structured list. Each proposal must cite specific federation evidence from the matrix above.

Yes, it has value, but the value is diagnostic: it shows that your current edge-generation is overwhelmingly intra-federation and dominated by “everything-in-Rome, everything-in-period” links, so you can use it to define a small set of robust SubjectConcepts and to redesign how cross-federation anchors are created.[^1_1][^1_2][^1_3]

Below are SubjectConcept proposals grounded only in the evidence you gave (plus what DPRR/Pleiades/WorldCat are, as authorities).[^1_2][^1_4][^1_3][^1_1]

***

### 1. Roman Republican Offices and Magistracies

1. **Name**
Roman Republican Offices and Magistracies
2. **Evidence**
    - DPRR explicitly is a prosopographical database of office-holders in the Roman Republic, built from Broughton’s *Magistrates of the Roman Republic*.[^1_5][^1_1]
    - Extremely high-degree DPRR nodes representing offices:
        - dprr:7373 — *aedilis* (14,649 neighbours)
        - dprr:8413 — *praetor* (14,649)
        - dprr:10207 — *praetor* (14,648)
        - dprr:7433 — *quaestor* (14,648)
        - dprr:7543 — *praefectus* (14,648)
        - dprr:7554 — *triumvir – unspecified* (14,648)
        - dprr:7680, 7692, 7872, 7883 — *senator – office unknown* (12–14k neighbours)
        - dprr:7502, 7512 — *proconsul* (13–11k neighbours)
    - These office nodes connect to essentially the entire DPRR person set (7335), via shared TEMPORAL and GEOGRAPHIC links centered on Rome.[^1_1]
3. **Dimensions**
    - GEOGRAPHIC: all these offices are anchored to Rome, typically via Roma/Pleiades and DPRR’s “office at Rome” data (e.g., every office-holder is an inhabitant or magistrate at Rome).[^1_3][^1_2][^1_1]
    - TEMPORAL: strong coherence across the Republican time-span; office nodes link to many persons whose tenures fall within overlapping date ranges.[^1_1]
    - SOCIAL: implicit SOCIAL dimension where offices connect to classes and orders (senatorial, equestrian) through DPRR person nodes, even if your matrix currently counts SOCIAL edges sparsely (e.g., the SOCIAL:1 on dprr:7373, 8413).[^1_1]
4. **Primary facet**
    - **POLITICAL** (with a strong SOCIAL secondary).

***

### 2. Rome as Spatial-Temporal Hub (Roma / Urbs)

1. **Name**
Rome as Spatial-Temporal Hub
2. **Evidence**
    - pleiades:423025 — Roma, with 14,670 neighbours (TEMPORAL:7335, GEOGRAPHIC:7335).
    - Getty TGN explicitly cross-links Rome to Pleiades 423025 as the inhabited place that served as capital of the Roman Republic.[^1_2][^1_3]
    - The neighbour counts indicate that essentially the entire DPRR set (7335) and all other Roman Republic entities are being pulled into a Roma-centric star, with one GEOGRAPHIC and one TEMPORAL edge per DPRR node.[^1_3][^1_2][^1_1]
3. **Dimensions**
    - GEOGRAPHIC: Roma is the central place for Republican institutions; Pleiades and TGN both encode Rome as an inhabited place at precise coordinates.[^1_2][^1_3]
    - TEMPORAL: Roma’s temporal coverage in your graph corresponds to the full Republic span as defined in DPRR and allied works.[^1_1]
    - SOCIAL (latent): via DPRR, almost all elite political careers converge on Rome.[^1_1]
4. **Primary facet**
    - **GEOGRAPHIC** (with POLITICAL as secondary).

***

### 3. Roman Republican Political Constitution and Institutions

1. **Name**
Political Constitution and Institutions of the Roman Republic
2. **Evidence**
    - High-degree DPRR office nodes as institutional “slots”:
        - dprr:7373, 7371 — *aedilis*
        - dprr:7381–7414 — *tribunus plebis* (multiple nodes, 14,580 neighbours each)
        - dprr:8413, 10207, 7812, 7313 — *praetor*
        - dprr:7502, 7512 — *proconsul*
        - dprr:7514 — *proquaestor pro propraetore*
    - DPRR as a whole encodes a mixed constitution of magistrates, Senate, and popular assemblies; this is the same constitutional structure described in standard syntheses of Republican government.[^1_6][^1_7][^1_1]
    - WorldCat titles such as *The Roman Republic* and related monographs are catalogued under subjects like “Roman Republic – Politics and government”, ensuring an intellectual/bibliographic cluster around institutional history.[^1_4][^1_8]
3. **Dimensions**
    - TEMPORAL: the constitutional offices cohere around a shared period (roughly 509–31 BCE, with DPRR’s own working range).[^1_1]
    - GEOGRAPHIC: all key institutions are geographically anchored to Rome (pleiades:423025).[^1_3][^1_2]
    - INTELLECTUAL: WorldCat records with subject strings like “Roman Republic – Politics and government” connect bibliographic works to this same institutional cluster (even though your matrix shows INTELLECTUAL:2 so far, the conceptual link is clear).[^1_8][^1_4]
    - BIBLIOGRAPHIC: DPRR cites Broughton, and WorldCat catalogs Broughton’s *Magistrates of the Roman Republic* and other core political-institutional works.[^1_4][^1_8][^1_1]
4. **Primary facet**
    - **POLITICAL**.

***

### 4. Careers of Republican Office-Holders (Elite Political-Social Strata)

1. **Name**
Careers of Republican Elite Office-Holders
2. **Evidence**
    - DPRR is a prosopography: it encodes individuals, offices held, dates, and locations, enabling reconstruction of elite careers.[^1_5][^1_1]
    - High-degree nodes for generic office types are proxies for clusters of career trajectories:
        - dprr:7680, 7692, 7872, 7883 — *senator – office unknown*; extremely high neighbour counts indicate many persons linked by shared tenure in the Senate and Rome.
        - dprr:7555, 7565 — *viocurus* (14,161 neighbours) indicating less famous but numerous municipal or local administrative roles still tied into the Roman system.
    - SOCIAL edges are currently sparse (21710 total vs millions of GEOGRAPHIC edges), but DPRR’s data model supports reconstructing social orders, patronage networks, and class membership.[^1_1]
3. **Dimensions**
    - TEMPORAL: sequences of offices over time define career paths.[^1_1]
    - GEOGRAPHIC: offices and honours are concentrated in Rome (pleiades:423025) but also potentially extend to provincial postings.[^1_2][^1_3][^1_1]
    - SOCIAL: senators, equites, magistrates, and other elites are linked through institutional membership and familial relationships inside DPRR.[^1_1]
4. **Primary facet**
    - **SOCIAL** (with POLITICAL as secondary).

***

### 5. Rome-Centred Republican Historiography (Textual/Scholarly Layer)

1. **Name**
Rome-Centred Republican Historiography
2. **Evidence**
    - worldcat:* nodes (196 total) include monographs like *The Roman Republic* catalogued under subjects and time spans focusing on the Republic’s history.[^1_8][^1_4]
    - LCSH/LCC codes for the Roman Republic tend to combine “Rome – History – Republic, 510–30 B.C.” with sub-headings like politics and government, law, social conditions, etc., giving a structured intellectual map over your DPRR/Pleiades backbone.[^1_9][^1_4][^1_8]
    - The near-zero INTELLECTUAL edge count (2) in your matrix indicates that intellectual/bibliographic alignment has barely been exploited yet; worldcat: nodes and lcsh:/lcc: nodes are ideal anchors for that dimension once you create explicit mappings.[^1_9][^1_4][^1_8]
3. **Dimensions**
    - INTELLECTUAL: LCSH/LCC subject strings and classification numbers align conceptual treatments of the Roman Republic with your entity graph (e.g., “Roman Republic – Politics and government”).[^1_4][^1_8][^1_9]
    - BIBLIOGRAPHIC: WorldCat work records connect specific titles, authors, and editions to DPRR and Pleiades entities they describe.[^1_8][^1_4]
    - TEMPORAL: subject time spans (e.g., “265–30 B.C.”) overlap the DPRR date ranges, creating potential TEMPORAL alignment between textual and prosopographical data.[^1_8]
4. **Primary facet**
    - **INTELLECTUAL** (with COMMUNICATION/BIBLIOGRAPHIC as secondary).

***

### 6. Rome and Italy During the Republic

1. **Name**
Rome and Italy During the Republic
2. **Evidence**
    - pleiades:423025 — Roma as the central place.[^1_3][^1_2]
    - The neighbour statistics (GEOGRAPHIC: 53,809,560 edges vs 1,397,002 TEMPORAL) indicate that your place-based alignment is extremely dense and could encompass not just Rome but all Pleiades Italian places associated with Republican events and magistracies.[^1_2][^1_1]
    - DPRR’s office and career data includes posts in Italian municipalities and colonies, which in principle can be geocoded to Pleiades places beyond Rome, even if your current sampling shows only the Roma super-hub.[^1_1]
3. **Dimensions**
    - GEOGRAPHIC: Rome as hub plus Italian cities, colonies, and roads; Pleiades and TGN supply the spatial gazetteer armature.[^1_3][^1_2]
    - TEMPORAL: Italian municipal integration and citizenship expansion occur across well-defined chronological phases (e.g., pre– and post–Social War), which DPRR careers can mark.[^1_1]
    - SOCIAL: extension of Roman citizenship and elite office-holding into Italian communities via DPRR person-place relationships.[^1_1]
4. **Primary facet**
    - **GEOGRAPHIC** (with SOCIAL as secondary).

***

### 7. Roman Republican Legal-Political Offices (Law as Practised Through Magistracies)

1. **Name**
Legal-Political Offices of the Roman Republic
2. **Evidence**
    - Many DPRR office types are explicitly juridical or mixed magistracies: *praetor* (jurisdiction), *quaestor* (financial administration), *tribunus plebis* (veto and sacrosanctity), *aedilis* (market and urban regulation).[^1_7][^1_6][^1_1]
    - The high-degree office nodes (dprr:7373, 7381–7414, 7433, 7812, 7313, etc.) indicate that these offices connect to large sets of individuals and events, which can stand in for the functioning of Roman law and administration in practice.[^1_1]
    - WorldCat subject strings often distinguish general political history from works specifically on “Roman law”, “Roman civil procedure”, or “Roman criminal law”, which can be mapped to these magistracies as practice nodes.[^1_4][^1_8]
3. **Dimensions**
    - POLITICAL/TEMPORAL: offices are defined by tenure cycles, electoral laws, and constitutional reforms.[^1_6][^1_1]
    - SOCIAL: legal authority is concentrated in specific orders and magistracies as encoded in DPRR.[^1_7][^1_1]
    - INTELLECTUAL/BIBLIOGRAPHIC: legal-historical scholarship (WorldCat titles) can be tied to specific magistracies and reforms.[^1_7][^1_4][^1_8]
4. **Primary facet**
    - **POLITICAL** (with LEGAL as a domain-specific subfacet you could model under POLITICAL or ECONOMIC/RELIGIOUS depending on your facet ontology).

***

### How this helps you

- These SubjectConcepts give you **thematic anchors** that are already strongly supported by GEOGRAPHIC and TEMPORAL coherence (Roma + DPRR period), even though your current matrix shows no cross-federation edges in the sample.[^1_2][^1_1]
- They also expose where you need to **actively manufacture cross-federation links** (especially INTELLECTUAL/BIBLIOGRAPHIC) by mapping DPRR places and people to WorldCat/LCSH/LCC, instead of relying on automatic neighbour overlap alone.[^1_9][^1_4][^1_8][^1_1]

If you’d like, I can next suggest concrete Cypher patterns or alignment rules to force at least one cross-federation anchor per SubjectConcept (e.g., “every DPRR office that is Rome-based gets an explicit `INTELLECTUAL` edge to the top N WorldCat ‘Roman Republic – politics and government’ works”).[^1_4][^1_8][^1_1]
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15]</span>

<div align="center">⁂</div>

[^1_1]: https://romanrepublic.ac.uk

[^1_2]: https://www.carc.ox.ac.uk/record/CEAF5A8D-DAAE-4281-A423-F17761D28DD2

[^1_3]: https://www.getty.edu/vow/TGNFullDisplay?find=\&place=\&nation=\&subjectid=7000874

[^1_4]: https://search.worldcat.org/oclc/27770244?tab=details

[^1_5]: https://www.cambridge.org/core/books/making-the-middle-republic/historical-sources/58F48D8181447D77396B6A3F33E15327

[^1_6]: https://www.cambridge.org/core/books/cambridge-ancient-history/roman-government-and-politics-200134-bc/70BF874CACE4B27C870BB27FF513777A

[^1_7]: https://chicagounbound.uchicago.edu/law_and_economics/497/

[^1_8]: https://search.worldcat.org/title/The-storm-before-the-storm-:-the-beginning-of-the-end-of-the-Roman-Republic/oclc/972386931

[^1_9]: https://lib.guides.umd.edu/c.php?g=326472\&p=2197960

[^1_10]: https://www.armyresilience.army.mil/ard/materials.html

[^1_11]: https://decima-map.net/decima-datasets/

[^1_12]: https://catalog.data.gov/dataset/ppr-program-districts-80d92/resource/0e608241-cad7-4534-8abc-81f440d43fdd

[^1_13]: https://www.ictj.org/sites/default/files/ICTJ_Report_Hybrid_Tribunals.pdf

[^1_14]: https://hub.arcgis.com/api/v3/datasets/f459cdd5d648476b978acaed560d11a2_33/downloads/data?format=csv\&spatialRefId=26985\&where=1%3D1

[^1_15]: https://romaninscriptionsofbritain.org/place/3203


---

# sure

Here are concrete patterns you can drop into Cypher (or adapt) so each SubjectConcept gets at least one deliberate cross-federation anchor, instead of relying on emergent overlap.[^2_1][^2_2][^2_3][^2_4]

***

## 1. Offices \& Magistracies ↔ Roma ↔ Broughton / “Politics \& government”

**Goal:** For each DPRR *office* that is Rome‑based, create explicit links to (a) Roma in Pleiades and (b) at least one key work on magistrates / political constitution (WorldCat/OpenLibrary).[^2_5][^2_6][^2_3][^2_4][^2_1]

Assumptions (rename as needed):

- `(:Office {federation:'dprr'})` for dprr:7373, 7433, 8413, etc.
- `(:Place {federation:'pleiades', key:'423025'})` is Roma.
- `(:Work {federation:'worldcat'|'openlibrary'})` holds Broughton and other core titles. [^2_4][^2_7][^2_6][^2_3]

```cypher
// 1A. Ensure DPRR Rome-based offices are explicitly GEOGRAPHIC to Roma
MATCH (o:Office {federation:'dprr'})
WHERE o.key IN ['7373','7371','7433','7543','7554','7680','7692','7812','7883','7502','7512','7514','7381','7389','7390','7392','7397','7400','7407','7414']
MATCH (r:Place {federation:'pleiades', key:'423025'})   // Roma
MERGE (o)-[g:GEOGRAPHIC {source:'chrystallum_manual'}]->(r);

// 1B. Attach each Rome-based office to a core magistrates work (INTELLECTUAL/BIBLIOGRAPHIC)
MATCH (o:Office {federation:'dprr'})
WHERE o.key IN ['7373','7371','7433','7543','7554','7680','7692','7812','7883','7502','7512','7514','7381','7389','7390','7392','7397','7400','7407','7414']
MATCH (w:Work)
WHERE w.title CONTAINS 'Magistrates of the Roman Republic'
   OR w.title CONTAINS 'Roman Republic'
   AND w.subject CONTAINS 'Politics and government'
MERGE (o)-[i:INTELLECTUAL {source:'subjectConcept:OfficesMagistracies'}]->(w)
MERGE (o)-[b:BIBLIOGRAPHIC {source:'subjectConcept:OfficesMagistracies'}]->(w);
```

This gives your **Offices and Magistracies** SubjectConcept at least one INTELLECTUAL + BIBLIOGRAPHIC edge per office, crossing DPRR → Pleiades → WorldCat/OpenLibrary.[^2_6][^2_3][^2_4][^2_1][^2_5]

***

## 2. Roma as Spatial Hub ↔ Library Records (Pleiades URIs in MARC)

**Goal:** Use the fact that LoC has approved Pleiades as an authority to create cross‑federation geographic anchors: any Work whose metadata mentions the Pleiades URI for Rome gets a GEOGRAPHIC edge to pleiades:423025.[^2_1]

Assumptions:

- You ingest Pleiades URIs into `Work.uriSet` or a `:URI` node.[^2_1]

```cypher
// 2A. Works that explicitly reference the Pleiades URI for Roma
MATCH (r:Place {federation:'pleiades', key:'423025'})
MATCH (w:Work)
WHERE any(u IN w.uris WHERE u CONTAINS 'https://pleiades.stoa.org/places/423025')
MERGE (w)-[:GEOGRAPHIC {source:'MARC_Pleiades'}]->(r);

// 2B. Fallback: match on subject strings mentioning "Rome -- History -- Republic"
MATCH (r:Place {federation:'pleiades', key:'423025'})
MATCH (w:Work)
WHERE w.subject CONTAINS 'Rome -- History -- Republic'
MERGE (w)-[:GEOGRAPHIC {source:'LCSH_subject'}]->(r);
```

This creates real **cross‑federation** edges from library catalogues into your Roma hub.[^2_8][^2_1]

***

## 3. Political Constitution \& Institutions ↔ LCSH/LCC Subject Strings

**Goal:** Turn LCSH/LCC records into INTELLECTUAL concept nodes aligned with DPRR’s institutional graph.[^2_3][^2_8]

Assumptions:

- `(:Subject {federation:'lcsh'})` with `heading` like `"Rome -- Politics and government -- 510-30 B.C."`.
- `(:Office {federation:'dprr'})`.[^2_4][^2_8]

```cypher
// 3A. Link political-institutional subjects to DPRR offices
MATCH (s:Subject {federation:'lcsh'})
WHERE s.heading CONTAINS 'Rome -- Politics and government'
  AND s.heading CONTAINS 'B.C.'
MATCH (o:Office {federation:'dprr'})
WHERE o.label IN ['consul','praetor','quaestor','tribunus plebis','aedilis','proconsul','proquaestor pro propraetore']
MERGE (o)-[:INTELLECTUAL {source:'LCSH_politics_government'}]->(s);

// 3B. Lift that subject into a SubjectConcept anchor node
MERGE (sc:SubjectConcept {key:'RR_PoliticalConstitution'})
  ON CREATE SET sc.label = 'Political Constitution and Institutions of the Roman Republic',
                sc.primaryFacet = 'POLITICAL';

MATCH (s:Subject {federation:'lcsh'})
WHERE s.heading CONTAINS 'Rome -- Politics and government'
MERGE (sc)-[:HAS_SUBJECT]->(s);
```

This makes the **Political Constitution and Institutions** SubjectConcept explicitly sit at the junction of DPRR offices and LCSH intellectual treatment.[^2_9][^2_4][^2_8]

***

## 4. Elite Careers ↔ Broughton ↔ Prosopography

**Goal:** Cross-link DPRR career paths to Broughton’s *Magistrates of the Roman Republic* as the canonical prosopographical reference.[^2_5][^2_6][^2_3][^2_4]

Assumptions:

- `(:Person {federation:'dprr'})` and `(:Office)` linked by `:HELD_OFFICE`.
- Broughton work node exists.[^2_6][^2_3][^2_4][^2_5]

```cypher
// 4A. Find persons with rich careers (e.g., held >= N magistracies)
MATCH (p:Person {federation:'dprr'})-[:HELD_OFFICE]->(o:Office {federation:'dprr'})
WITH p, collect(DISTINCT o) AS offices
WHERE size(offices) >= 3     // threshold for "elite career"
MATCH (w:Work)
WHERE w.title CONTAINS 'Magistrates of the Roman Republic'
MERGE (p)-[:BIBLIOGRAPHIC {source:'Broughton_prosopography'}]->(w);

// 4B. Attach careers SubjectConcept
MERGE (sc:SubjectConcept {key:'RR_EliteCareers'})
  ON CREATE SET sc.label = 'Careers of Republican Elite Office-Holders',
                sc.primaryFacet = 'SOCIAL';

MATCH (p:Person {federation:'dprr'})-[:HELD_OFFICE]->(o:Office)
WHERE o.label IN ['consul','praetor','quaestor','tribunus plebis','aedilis']
MERGE (sc)-[:HAS_EXAMPLE]->(p);
```

Now **Elite Careers** is concretely tied to a bibliographic authority (Broughton) and to high-degree DPRR persons.[^2_3][^2_4][^2_5][^2_6]

***

## 5. Rome and Italy During the Republic ↔ Pleiades Italian Places

**Goal:** Force cross‑federation geographic coherence beyond Roma by linking DPRR provincial/municipal offices to Pleiades places in Italy.[^2_2][^2_10][^2_11][^2_4]

Assumptions:

- `Person` or `Office` carries a string place name (e.g. `o.placeName`), and you have a set of Pleiades Italian places.[^2_10][^2_11][^2_2]

```cypher
// 5A. Match DPRR offices to Italian Pleiades places by name
MATCH (o:Office {federation:'dprr'})
WHERE o.placeName IS NOT NULL
MATCH (pl:Place {federation:'pleiades'})
WHERE pl.region = 'Italy'            // or bounding box attributes
  AND toLower(pl.name) = toLower(o.placeName)
MERGE (o)-[:GEOGRAPHIC {source:'nameMatch_Italy'}]->(pl);

// 5B. Attach SubjectConcept
MERGE (sc:SubjectConcept {key:'RR_RomeAndItaly'})
  ON CREATE SET sc.label = 'Rome and Italy During the Republic',
                sc.primaryFacet = 'GEOGRAPHIC';

MATCH (pl:Place {federation:'pleiades'})
WHERE pl.region = 'Italy'
MERGE (sc)-[:HAS_PLACE]->(pl);
```

This lets queries like “SubjectConcept: RR_RomeAndItaly” pull coherent Italian spatial slices of the DPRR + Pleiades federation.[^2_11][^2_4][^2_10]

***

## 6. Historiography \& Legal-Political Offices ↔ Subject Headings \& Law Works

**Goal:** Give the **Historiography** and **Legal-Political Offices** concepts their own cross-federation “package” via LCSH subject strings and law-focused works.[^2_7][^2_12][^2_9][^2_8]

```cypher
// 6A. Historiography: link RR history subjects to generic RR entities
MERGE (scHist:SubjectConcept {key:'RR_Historiography'})
  ON CREATE SET scHist.label = 'Rome-Centred Republican Historiography',
                scHist.primaryFacet = 'INTELLECTUAL';

MATCH (s:Subject {federation:'lcsh'})
WHERE s.heading CONTAINS 'Rome -- History -- Republic'
MERGE (scHist)-[:HAS_SUBJECT]->(s);

MATCH (w:Work)
WHERE w.subject CONTAINS 'Rome -- History -- Republic'
MERGE (w)-[:INTELLECTUAL {source:'LCSH_history'}]->(scHist);

// 6B. Legal-political offices: map law-focused works to DPRR magistracies
MERGE (scLaw:SubjectConcept {key:'RR_LegalPoliticalOffices'})
  ON CREATE SET scLaw.label = 'Legal-Political Offices of the Roman Republic',
                scLaw.primaryFacet = 'POLITICAL';

MATCH (w:Work)
WHERE w.subject CONTAINS 'Roman law'
   OR w.title  CONTAINS 'Roman law'
MATCH (o:Office {federation:'dprr'})
WHERE o.label IN ['praetor','quaestor','tribunus plebis','aedilis']
MERGE (o)-[:INTELLECTUAL {source:'Roman_law_scholarship'}]->(w)
MERGE (scLaw)-[:HAS_EXAMPLE]->(o);
```

This turns cataloguing practice (LCSH + legal titles) into explicit INTELLECTUAL and BIBLIOGRAPHIC edges in your graph.[^2_12][^2_9][^2_7][^2_8]

***

If you share your current label/property conventions, I can reshape these into exactly runnable Cypher tailored to your Neo4j schema and your existing federation tags.
<span style="display:none">[^2_13][^2_14][^2_15][^2_16][^2_17][^2_18][^2_19][^2_20][^2_21]</span>

<div align="center">⁂</div>

[^2_1]: https://isaw.nyu.edu/library/blog/MARC-Pleiades

[^2_2]: http://pelagios-project.blogspot.com/2012/06/improving-arachne-pleiades-matching.html

[^2_3]: https://onlinebooks.library.upenn.edu/webbin/book/lookupid?key=olbp73024

[^2_4]: https://romanrepublic.ac.uk

[^2_5]: https://archive.org/details/broughton-magistrates-roman-republic

[^2_6]: https://openlibrary.org/books/OL6090096M/The_magistrates_of_the_Roman_Republic

[^2_7]: https://search.worldcat.org/oclc/27770244?tab=details

[^2_8]: https://lib.guides.umd.edu/c.php?g=326472\&p=2197960

[^2_9]: https://chicagounbound.uchicago.edu/law_and_economics/497/

[^2_10]: https://www.carc.ox.ac.uk/record/CEAF5A8D-DAAE-4281-A423-F17761D28DD2

[^2_11]: https://www.getty.edu/vow/TGNFullDisplay?find=\&place=\&nation=\&subjectid=7000874

[^2_12]: https://search.worldcat.org/title/The-storm-before-the-storm-:-the-beginning-of-the-end-of-the-Roman-Republic/oclc/972386931

[^2_13]: https://github.com/stacks-network/pybitcoin/blob/master/pybitcoin/passphrases/english_words.py

[^2_14]: https://snap.berkeley.edu/project/14165954

[^2_15]: https://knowledge.uchicago.edu/record/1379/files/Hodgkin_uchicago_0330D_14575.pdf

[^2_16]: https://www.cs.princeton.edu/courses/archive/spring20/cos226/assignments/autocomplete/files/words-333333.txt

[^2_17]: https://www.youtube.com/watch?v=hDHW9aj_8tg

[^2_18]: http://ndl.ethernet.edu.et/bitstream/123456789/32706/1/305.Emmanouel Garoufallou.pdf

[^2_19]: http://resourcesforhistoryteachers.pbworks.com/w/page/124780659/Government of the Roman Republic

[^2_20]: https://radar.inria.fr/rapportsactivite/RA2017/pleiade/pleiade.pdf

[^2_21]: https://www.loc.gov/aba/publications/FreeLCSH/SUBDIVISIONS.pdf


---

# here is wikidata for pompey. in general, for a graph representation of a person, provide a profile table for each attribute and external id, what it means and how it can be used  and suggest a core person schema, indicate which attributes should be considered as a first class node. Statements

[instance of](https://www.wikidata.org/wiki/Property:P31)
[human](https://www.wikidata.org/wiki/Q5)
[1 reference]()
[image](https://www.wikidata.org/wiki/Property:P18)
[](https://commons.wikimedia.org/wiki/File:Pompey_the_Great.jpg)
[Pompey the Great.jpg](https://commons.wikimedia.org/wiki/File:Pompey_the_Great.jpg)
1,110 × 1,617; 189 KB
[0 references]()
[sex or gender](https://www.wikidata.org/wiki/Property:P21)
[male](https://www.wikidata.org/wiki/Q6581097)
[2 references]()
[country of citizenship](https://www.wikidata.org/wiki/Property:P27)
[Ancient Rome](https://www.wikidata.org/wiki/Q1747689)
[3 references]()
[name in native language](https://www.wikidata.org/wiki/Property:P1559)
Cn. Pompeius Cn.f.Sex.n. Clu. Magnus (Latin)
[0 references]()
[praenomen](https://www.wikidata.org/wiki/Property:P2358)
[Gnaeus](https://www.wikidata.org/wiki/Q5574029)
[0 references]()
[nomen gentilicium](https://www.wikidata.org/wiki/Property:P2359)
[Pompeius](https://www.wikidata.org/wiki/Q32979356)
[0 references]()
[cognomen](https://www.wikidata.org/wiki/Property:P2365)
[Magnus](https://www.wikidata.org/wiki/Q2939969)
[0 references]()
[date of birth](https://www.wikidata.org/wiki/Property:P569)
29 September 106 BCE
[earliest date](https://www.wikidata.org/wiki/Property:P1319)
29 September 106 BCE
[latest date](https://www.wikidata.org/wiki/Property:P1326)
30 September 106 BCE
[2 references]()
106 BCEGregorian
[1 reference]()
[place of birth](https://www.wikidata.org/wiki/Property:P19)
[Regio V Picenum](https://www.wikidata.org/wiki/Q510990)
[country](https://www.wikidata.org/wiki/Property:P17)
[Roman Republic](https://www.wikidata.org/wiki/Q17167)
[4 references]()
[date of death](https://www.wikidata.org/wiki/Property:P570)
28 September 48 BCE
[1 reference]()
48 BCEGregorian
[1 reference]()
[place of death](https://www.wikidata.org/wiki/Property:P20)
[Pelusium](https://www.wikidata.org/wiki/Q1145715)
[country](https://www.wikidata.org/wiki/Property:P17)
[Ptolemaic Kingdom](https://www.wikidata.org/wiki/Q2320005)
[1 reference]()
[manner of death](https://www.wikidata.org/wiki/Property:P1196)
[homicide](https://www.wikidata.org/wiki/Q149086)
 
[0 references]()
[cause of death](https://www.wikidata.org/wiki/Property:P509)
[stab wound](https://www.wikidata.org/wiki/Q4228595)
[1 reference]()
[father](https://www.wikidata.org/wiki/Property:P22)
[Gnaeus Pompeius Strabo](https://www.wikidata.org/wiki/Q336538)
[1 reference]()
[mother](https://www.wikidata.org/wiki/Property:P25)
[Lucilia](https://www.wikidata.org/wiki/Q56259966)
[1 reference]()
[sibling](https://www.wikidata.org/wiki/Property:P3373)
[Pompeia](https://www.wikidata.org/wiki/Q435946)
[1 reference]()
[Pompeia](https://www.wikidata.org/wiki/Q123700690)
[1 reference]()
[spouse](https://www.wikidata.org/wiki/Property:P26)
[Antistia](https://www.wikidata.org/wiki/Q518068)
[start time](https://www.wikidata.org/wiki/Property:P580)
86 BCE
[end time](https://www.wikidata.org/wiki/Property:P582)
82 BCE
[series ordinal](https://www.wikidata.org/wiki/Property:P1545)
1
[2 references]()
[Aemilia Scaura](https://www.wikidata.org/wiki/Q380857)
[start time](https://www.wikidata.org/wiki/Property:P580)
82 BCE
[end time](https://www.wikidata.org/wiki/Property:P582)
82 BCE
[series ordinal](https://www.wikidata.org/wiki/Property:P1545)
2
[2 references]()
[Mucia Tertia](https://www.wikidata.org/wiki/Q273616)
[start time](https://www.wikidata.org/wiki/Property:P580)
79 BCE
[end time](https://www.wikidata.org/wiki/Property:P582)
59 BCE
[series ordinal](https://www.wikidata.org/wiki/Property:P1545)
3
[2 references]()
[Julia](https://www.wikidata.org/wiki/Q235087)
[start time](https://www.wikidata.org/wiki/Property:P580)
59 BCE
[end time](https://www.wikidata.org/wiki/Property:P582)
54 BCE
[series ordinal](https://www.wikidata.org/wiki/Property:P1545)
4
[3 references]()
[Cornelia Metella](https://www.wikidata.org/wiki/Q270384)
[start time](https://www.wikidata.org/wiki/Property:P580)
52 BCE
[end time](https://www.wikidata.org/wiki/Property:P582)
48 BCE
[series ordinal](https://www.wikidata.org/wiki/Property:P1545)
5
[2 references]()
[child](https://www.wikidata.org/wiki/Property:P40)
[Gnaeus Pompeius Magnus](https://www.wikidata.org/wiki/Q473280)
[mother](https://www.wikidata.org/wiki/Property:P25)
[Mucia Tertia](https://www.wikidata.org/wiki/Q273616)
[3 references]()
[Sextus Pompey](https://www.wikidata.org/wiki/Q295228)
[mother](https://www.wikidata.org/wiki/Property:P25)
[Mucia Tertia](https://www.wikidata.org/wiki/Q273616)
[2 references]()
[Pompeia Magna](https://www.wikidata.org/wiki/Q442503)
[mother](https://www.wikidata.org/wiki/Property:P25)
[Mucia Tertia](https://www.wikidata.org/wiki/Q273616)
[0 references]()
[Pompeia](https://www.wikidata.org/wiki/Q55832253)
[mother](https://www.wikidata.org/wiki/Property:P25)
[Julia](https://www.wikidata.org/wiki/Q235087)
[0 references]()
[gens](https://www.wikidata.org/wiki/Property:P5025)
[Pompeia gens](https://www.wikidata.org/wiki/Q1507713)
[0 references]()
[native language](https://www.wikidata.org/wiki/Property:P103)
[Latin](https://www.wikidata.org/wiki/Q397)
[0 references]()
[languages spoken, written or signed](https://www.wikidata.org/wiki/Property:P1412)
[Latin](https://www.wikidata.org/wiki/Q397)
[0 references]()
[occupation](https://www.wikidata.org/wiki/Property:P106)
[politician](https://www.wikidata.org/wiki/Q82955)
[1 reference]()
[military personnel](https://www.wikidata.org/wiki/Q47064)
[0 references]()
[position held](https://www.wikidata.org/wiki/Property:P39)
[praetor](https://www.wikidata.org/wiki/Q172907)
[0 references]()
[quaestor](https://www.wikidata.org/wiki/Q189430)
[0 references]()
[ancient Roman senator](https://www.wikidata.org/wiki/Q20056508)
[start time](https://www.wikidata.org/wiki/Property:P580)
unknown value
[end time](https://www.wikidata.org/wiki/Property:P582)
unknown value
[1 reference]()
[Roman consul](https://www.wikidata.org/wiki/Q40779)
[start time](https://www.wikidata.org/wiki/Property:P580)
70 BCEGregorian
[end time](https://www.wikidata.org/wiki/Property:P582)
70 BCEGregorian
[together with](https://www.wikidata.org/wiki/Property:P1706)
[Marcus Licinius Crassus](https://www.wikidata.org/wiki/Q175121)
[1 reference]()
[moneyer](https://www.wikidata.org/wiki/Q1861571)
[series ordinal](https://www.wikidata.org/wiki/Property:P1545)
1
[start time](https://www.wikidata.org/wiki/Property:P580)
71 BCE
[end time](https://www.wikidata.org/wiki/Property:P582)
71 BCE
[1 reference]()
[moneyer](https://www.wikidata.org/wiki/Q1861571)
[series ordinal](https://www.wikidata.org/wiki/Property:P1545)
2
[start time](https://www.wikidata.org/wiki/Property:P580)
49 BCE
[end time](https://www.wikidata.org/wiki/Property:P582)
49 BCE
[1 reference]()
[member of political party](https://www.wikidata.org/wiki/Property:P102)
[optimates](https://www.wikidata.org/wiki/Q309155)
[1 reference]()
[social classification](https://www.wikidata.org/wiki/Property:P3716)
[noble](https://www.wikidata.org/wiki/Q16744001)
[1 reference]()
[equites](https://www.wikidata.org/wiki/Q122166)
[1 reference]()
[religion or worldview](https://www.wikidata.org/wiki/Property:P140)
[ancient Roman religion](https://www.wikidata.org/wiki/Q337547)
[1 reference]()
[military, police or special rank](https://www.wikidata.org/wiki/Property:P410)
[legatus](https://www.wikidata.org/wiki/Q212624)
[1 reference]()
[military branch](https://www.wikidata.org/wiki/Property:P241)
[Roman army](https://www.wikidata.org/wiki/Q1114493)
[1 reference]()
[member of](https://www.wikidata.org/wiki/Property:P463)
[First Triumvirate](https://www.wikidata.org/wiki/Q715380)
[0 references]()
[present in work](https://www.wikidata.org/wiki/Property:P1441)
[Euskal Herriaren historia nafarra](https://www.wikidata.org/wiki/Q64992248)
[0 references]()
[time period](https://www.wikidata.org/wiki/Property:P2348)
[Late Roman Republic](https://www.wikidata.org/wiki/Q2815472)
[1 reference]()
[depicted by](https://www.wikidata.org/wiki/Property:P1299)
[Pompey dreams of Julia](https://www.wikidata.org/wiki/Q133232276)
[0 references]()
[described by source](https://www.wikidata.org/wiki/Property:P1343)
[Sytin Military Encyclopedia](https://www.wikidata.org/wiki/Q4114391)
[statement is subject of](https://www.wikidata.org/wiki/Property:P805)
[Pompeius, Gnaeus](https://www.wikidata.org/wiki/Q25417283)
[0 references]()
[Jewish Encyclopedia of Brockhaus and Efron](https://www.wikidata.org/wiki/Q4173137)
[statement is subject of](https://www.wikidata.org/wiki/Property:P805)
[Pompeius Magnus](https://www.wikidata.org/wiki/Q24922234)
[0 references]()
[Parallel Lives](https://www.wikidata.org/wiki/Q842337)
[0 references]()
[Pauly–Wissowa](https://www.wikidata.org/wiki/Q1138524)
[statement is subject of](https://www.wikidata.org/wiki/Property:P805)
[Pompeius 31 (Pauly-Wissowa)](https://www.wikidata.org/wiki/Q34405250)
[0 references]()
[Russian translation of Lübker's Antiquity Lexicon](https://www.wikidata.org/wiki/Q30059240)
[statement is subject of](https://www.wikidata.org/wiki/Property:P805)
[RSCD / Pompeii (ii)](https://www.wikidata.org/wiki/Q45258177)
[0 references]()
[Brockhaus and Efron Encyclopedic Dictionary](https://www.wikidata.org/wiki/Q602358)
[statement is subject of](https://www.wikidata.org/wiki/Property:P805)
[Gnejus Pompeius Magnus](https://www.wikidata.org/wiki/Q24488957)
[0 references]()
[Dictionary of African Biography](https://www.wikidata.org/wiki/Q46002746)
[URL](https://www.wikidata.org/wiki/Property:P2699)
[http://www.oxfordreference.com/abstract/10.1093/acref/9780195382075.001.0001/acref-9780195382075-e-1692?rskey=YbEPGf\&result=1692](http://www.oxfordreference.com/abstract/10.1093/acref/9780195382075.001.0001/acref-9780195382075-e-1692?rskey=YbEPGf&result=1692)
[0 references]()
[Obálky knih](https://www.wikidata.org/wiki/Q67311526)
[URL](https://www.wikidata.org/wiki/Property:P2699)
[https://www.obalkyknih.cz/view_auth?auth_id=jn20000701429](https://www.obalkyknih.cz/view_auth?auth_id=jn20000701429)
[0 references]()
[Granat Encyclopedic Dictionary](https://www.wikidata.org/wiki/Q4532138)
[statement is subject of](https://www.wikidata.org/wiki/Property:P805)
[Pompeius, Gnaeus, Magnus](https://www.wikidata.org/wiki/Q96360791)
[0 references]()
[Encyclopædia Britannica 11th edition](https://www.wikidata.org/wiki/Q867541)
[statement is subject of](https://www.wikidata.org/wiki/Property:P805)
[1911 Encyclopædia Britannica/Pompey](https://www.wikidata.org/wiki/Q84674976)
[0 references]()
[The Nuttall Encyclopædia](https://www.wikidata.org/wiki/Q3181656)
[subject named as](https://www.wikidata.org/wiki/Property:P1810)
Pompey, Cneius
[0 references]()
[Small Brockhaus and Efron Encyclopedic Dictionary](https://www.wikidata.org/wiki/Q19180675)
[statement is subject of](https://www.wikidata.org/wiki/Property:P805)
[Q24820738](https://www.wikidata.org/wiki/Q24820738)
[0 references]()
[on focus list of Wikimedia project](https://www.wikidata.org/wiki/Property:P5008)
[Wikipedia:Vital articles/Level/4](https://www.wikidata.org/wiki/Q6173448)
[point in time](https://www.wikidata.org/wiki/Property:P585)
31 October 2022
[0 references]()
[member of Roman tribe](https://www.wikidata.org/wiki/Property:P11491)
[Clustumina](https://www.wikidata.org/wiki/Q3538785)
[1 reference]()
[different from](https://www.wikidata.org/wiki/Property:P1889)
[Pompeii](https://www.wikidata.org/wiki/Q15880843)
 
[1 reference]()
[Commons gallery](https://www.wikidata.org/wiki/Property:P935)
[Gnaeus Pompeius Magnus](https://commons.wikimedia.org/wiki/Gnaeus%20Pompeius%20Magnus)
[1 reference]()
[Commons category](https://www.wikidata.org/wiki/Property:P373)
[Gnaeus Pompeius Magnus](https://commons.wikimedia.org/wiki/Category:Gnaeus%20Pompeius%20Magnus)
[0 references]()
[topic's main category](https://www.wikidata.org/wiki/Property:P910)
[Category:Pompey](https://www.wikidata.org/wiki/Q8968997)
[1 reference]()
Identifiers
[VIAF cluster ID](https://www.wikidata.org/wiki/Property:P214)
[6224297](https://viaf.org/viaf/6224297)
[2 references]()
[32151776763518011915](https://viaf.org/viaf/32151776763518011915)
[0 references]()
[305418913](https://viaf.org/viaf/305418913)
[0 references]()
[ISNI](https://www.wikidata.org/wiki/Property:P213)
[0000000374485904](https://isni.org/isni/0000000374485904)
[1 reference]()
[Vatican Library VcBA ID](https://www.wikidata.org/wiki/Property:P8034)
[495/26673](https://wikidata-externalid-url.toolforge.org/?p=8034&url_prefix=https://opac.vatlib.it/auth/detail/&id=495/26673)
[0 references]()
[NORAF ID](https://www.wikidata.org/wiki/Property:P1015)
[90756998](https://authority.bibsys.no/authority/rest/authorities/html/90756998)
[1 reference]()
[National Library of Spain SpMaBN ID (BNE v1.0)](https://www.wikidata.org/wiki/Property:P950)
[XX1074073](https://datos.bne.es/resource/XX1074073)
[0 references]()
[Bibliothèque nationale de France ID](https://www.wikidata.org/wiki/Property:P268)
[11938643b](https://catalogue.bnf.fr/ark:/12148/cb11938643b)
[1 reference]()
[Canadiana Name Authority ID](https://www.wikidata.org/wiki/Property:P8179)
[ncf11182817](https://viaf.org/processed/CAOONLncf11182817)
[1 reference]()
[GND ID](https://www.wikidata.org/wiki/Property:P227)
[118595636](https://d-nb.info/gnd/118595636)
[1 reference]()
[Deutsche Biographie (GND) ID](https://www.wikidata.org/wiki/Property:P7902)
[118595636](https://www.deutsche-biographie.de/118595636.html)
[0 references]()
[DDB person (GND) ID](https://www.wikidata.org/wiki/Property:P13049)
[118595636](https://www.deutsche-digitale-bibliothek.de/person/gnd/118595636)
[0 references]()
[Kalliope-Verbund (GND) ID](https://www.wikidata.org/wiki/Property:P9964)
[118595636](https://kalliope-verbund.info/gnd/118595636)
[0 references]()
[ELNET ID](https://www.wikidata.org/wiki/Property:P6394)
[a11409368](https://viaf.org/processed/ERRRa11409368)
[1 reference]()
[FAST ID](https://www.wikidata.org/wiki/Property:P2163)
[1841849](https://id.worldcat.org/fast/1841849)
[0 references]()
[National Library of Israel J9U ID](https://www.wikidata.org/wiki/Property:P8189)
[987007266498105171](https://www.nli.org.il/en/authorities/987007266498105171)
[1 reference]()
[Union List of Artist Names ID](https://www.wikidata.org/wiki/Property:P245)
[500355380](https://www.getty.edu/vow/ULANFullDisplay?find=500355380&role=&nation=&prev_page=1&subjectid=500355380)
 
[1 reference]()
[Library of Congress authority ID](https://www.wikidata.org/wiki/Property:P244)
[n80013395](https://id.loc.gov/authorities/n80013395)
[1 reference]()
[National Library of Lithuania ID](https://www.wikidata.org/wiki/Property:P7699)
[LNB:V*342247;=BI](https://wikidata-externalid-url.toolforge.org/?p=7699&url_prefix=https://viaf.org/processed/LIH%7C&id=LNB%3AV%2A342247%3B%3DBI)
[1 reference]()
[National Library of Ireland ID](https://www.wikidata.org/wiki/Property:P10227)
[vtls001142003](https://viaf.org/processed/N6Ivtls001142003)
[1 reference]()
[NDL Authority ID](https://www.wikidata.org/wiki/Property:P349)
[001147360](https://id.ndl.go.jp/auth/ndlna/001147360)
[0 references]()
[NACSIS-CAT author ID](https://www.wikidata.org/wiki/Property:P271)
[DA08934415](https://ci.nii.ac.jp/author/DA08934415)
[1 reference]()
[NL CR AUT ID](https://www.wikidata.org/wiki/Property:P691)
[jn20000701429](https://aleph.nkp.cz/F/?func=find-c&local_base=aut&ccl_term=ica=jn20000701429)
[1 reference]()
[National Library of Russia ID](https://www.wikidata.org/wiki/Property:P7029)
[7790496](https://webservices.nlr.ru/semweb/?method=afnlr&query=NLR10%3A%3ARU%5CNLR%5CAUTH%5C7790496)
 
[1 reference]()
[7792391](https://webservices.nlr.ru/semweb/?method=afnlr&query=NLR10%3A%3ARU%5CNLR%5CAUTH%5C7792391)
 
[1 reference]()
[Nationale Thesaurus voor Auteursnamen ID](https://www.wikidata.org/wiki/Property:P1006)
[070070881](https://data.bibliotheken.nl/id/thes/p070070881)
[1 reference]()
[NUKAT ID](https://www.wikidata.org/wiki/Property:P1207)
[n2004092995](https://wikidata-externalid-url.toolforge.org/?p=1207&url_prefix=http://nukat.edu.pl/aut/&id=n2004092995)
[0 references]()
[National Library of Poland MMS ID](https://www.wikidata.org/wiki/Property:P7293)
[9810653882305606](https://dbn.bn.org.pl/descriptor-details/9810653882305606)
[0 references]()
[Libris-URI](https://www.wikidata.org/wiki/Property:P5587)
[zw9cgvlh2d5j2nh](https://libris.kb.se/zw9cgvlh2d5j2nh)
[1 reference]()
[SELIBR ID](https://www.wikidata.org/wiki/Property:P906)
[253005](https://libris.kb.se/auth/253005)
[1 reference]()
[IdRef ID](https://www.wikidata.org/wiki/Property:P269)
[027318001](https://www.idref.fr/027318001)
[1 reference]()
[WorldCat Entities ID](https://www.wikidata.org/wiki/Property:P10832)
[E39PBJmXJkhwB9FYp6kV6wD6rq](https://id.oclc.org/worldcat/entity/E39PBJmXJkhwB9FYp6kV6wD6rq)
[1 reference]()
[Alvin ID](https://www.wikidata.org/wiki/Property:P6821)
[alvin-person:61601](https://www.alvin-portal.org/alvin/view.jsf?pid=alvin-person%3A61601)
[0 references]()
[American Academy in Rome ID](https://www.wikidata.org/wiki/Property:P9097)
[12380202](https://library.aarome.org/cgi-bin/koha/opac-authoritiesdetail.pl?marc=1&authid=12380202)
[0 references]()
[ARAE ID](https://www.wikidata.org/wiki/Property:P9226)
[pompeyo-106-48-c](https://archivo.rae.es/pompeyo-106-48-c)
[0 references]()
[Auñamendi ID](https://www.wikidata.org/wiki/Property:P3218)
[115946](http://www.euskomedia.org/aunamendi/115946)
[0 references]()
[BHCL UUID](https://www.wikidata.org/wiki/Property:P9037)
[b69c3427-2985-4dcb-b31f-9b426d4d7d05](https://biblio.hiu.cas.cz/records/b69c3427-2985-4dcb-b31f-9b426d4d7d05)
[1 reference]()
[British Museum person or institution ID](https://www.wikidata.org/wiki/Property:P1711)
[148402](https://www.britishmuseum.org/collection/term/BIOG148402)
[0 references]()
[CERL Thesaurus ID](https://www.wikidata.org/wiki/Property:P1871)
[cnp00396166](https://data.cerl.org/thesaurus/cnp00396166)
[1 reference]()
[CiNii Research ID](https://www.wikidata.org/wiki/Property:P11496)
[1140563741517931008](https://cir.nii.ac.jp/crid/1140563741517931008)
[0 references]()
[CIRIS author ID](https://www.wikidata.org/wiki/Property:P8065)
[1771](https://ciris.huma-num.fr/noticeauteur.php?id=1771)
[0 references]()
[Comic Vine ID](https://www.wikidata.org/wiki/Property:P5905)
[4005-128191](https://comicvine.gamespot.com/wd/4005-128191/)
[0 references]()
[De Agostini ID](https://www.wikidata.org/wiki/Property:P6706)
[Pompèo+Magno,+Gnèo](https://www.sapere.it/enciclopedia/Pomp%C3%A8o%2BMagno%2C%2BGn%C3%A8o.html)
[subject named as](https://www.wikidata.org/wiki/Property:P1810)
Pompèo Magno, Gnèo
[0 references]()
[Digital Prosopography of the Roman Republic ID](https://www.wikidata.org/wiki/Property:P6863)
[1976](https://romanrepublic.ac.uk/person/1976/)
[0 references]()
[DLL Catalog author ID](https://www.wikidata.org/wiki/Property:P8122)
[A3148](https://catalog.digitallatin.org/dll-author/A3148)
[0 references]()
[Enciclopedia di Roma person ID](https://www.wikidata.org/wiki/Property:P10031)
[1876](https://www.info.roma.it/personaggi_dettaglio.asp?ID_personaggi=1876)
[0 references]()
[Encyclopædia Britannica Online ID](https://www.wikidata.org/wiki/Property:P1417)
[biography/Pompey-the-Great](https://www.britannica.com/biography/Pompey-the-Great)
[subject named as](https://www.wikidata.org/wiki/Property:P1810)
Pompey the Great
[author name string](https://www.wikidata.org/wiki/Property:P2093)
Eric William Gray
[1 reference]()
[biography/Gnaeus-Pompey](https://www.britannica.com/biography/Gnaeus-Pompey)
[subject named as](https://www.wikidata.org/wiki/Property:P1810)
Gnaeus Pompey
[0 references]()
[Encyclopædia Universalis ID](https://www.wikidata.org/wiki/Property:P3219)
[pompee-lat-cneius-pompeius-magnus](https://www.universalis.fr/encyclopedie/pompee-lat-cneius-pompeius-magnus/)
[0 references]()
[Freebase ID](https://www.wikidata.org/wiki/Property:P646)
[/m/05z3r](https://www.google.com/search?kgmid=/m/05z3r)
[1 reference]()
[Gran Enciclopèdia Catalana ID](https://www.wikidata.org/wiki/Property:P12385)
[gneu-pompeu-magne](https://www.enciclopedia.cat/gran-enciclopedia-catalana/gneu-pompeu-magne)
[0 references]()
[Gran Enciclopèdia Catalana ID (former scheme)](https://www.wikidata.org/wiki/Property:P1296)
[0051892](https://www.enciclopedia.cat/ec-gec-0051892.xml)
[0 references]()
[Great Encyclopedia of Navarre ID](https://www.wikidata.org/wiki/Property:P7388)
[16919](http://www.enciclopedianavarra.com/?page_id=16919)
[0 references]()
[Great Russian Encyclopedia Online ID (old version)](https://www.wikidata.org/wiki/Property:P2924)
[3157729](https://old.bigenc.ru/text/v/3157729)
[subject named as](https://www.wikidata.org/wiki/Property:P1810)
ПОМПЕЙ
[0 references]()
[Historia Hispánica ID](https://www.wikidata.org/wiki/Property:P13371)
[biografias/36371](https://historia-hispanica.rah.es/biografias/36371)
[0 references]()
[Hrvatska enciklopedija ID](https://www.wikidata.org/wiki/Property:P7982)
[49372](https://www.enciklopedija.hr/clanak/49372)
[0 references]()
[Interlingual Index ID](https://www.wikidata.org/wiki/Property:P5063)
[i96604](https://en-word.net/ili/i96604)
[0 references]()
[IxTheo authority ID](https://www.wikidata.org/wiki/Property:P10553)
[079388221](https://ixtheo.de/Authority/079388221)
[0 references]()
[Jewish Encyclopedia ID (Russian)](https://www.wikidata.org/wiki/Property:P1438)
[13279](https://eleven.co.il/article/13279)
[0 references]()
[Joconde author ID](https://www.wikidata.org/wiki/Property:P7711)
[T513-44866](http://data.culture.fr/thesaurus/page/ark:/67717/T513-44866/)
[0 references]()
[KANTO ID](https://www.wikidata.org/wiki/Property:P8980)
[000230156](https://urn.fi/URN:NBN:fi:au:finaf:000230156)
[1 reference]()
[Krugosvet article (archived)](https://www.wikidata.org/wiki/Property:P6385)
[istoriya/POMPE_GNE.html](https://web.archive.org/web/2025/https://www.krugosvet.ru/enc/istoriya/POMPE_GNE.html)
[0 references]()
[Larousse ID](https://www.wikidata.org/wiki/Property:P6058)
[personnage/wd/138672](https://www.larousse.fr/encyclopedie/personnage/wd/138672)
[0 references]()
[LBT person ID](https://www.wikidata.org/wiki/Property:P2977)
[GnPompe](https://www.lordbyron.org/persRec.php?&selectPerson=GnPompe)
[0 references]()
[Lex ID](https://www.wikidata.org/wiki/Property:P8313)
[Gnaeus_Pompejus](https://wikidata-externalid-url.toolforge.org/?p=8313&url_prefix=https://lex.dk/&id=Gnaeus_Pompejus)
[0 references]()
[Münzkabinett ID](https://www.wikidata.org/wiki/Property:P13030)
[person/2511](https://ikmk.smb.museum/ndp/person/2511)
[0 references]()
[Museo Galileo authority ID](https://www.wikidata.org/wiki/Property:P8947)
[184797](https://opac.museogalileo.it/imss/authResource?uri=184797)
[0 references]()
[museum-digital person ID](https://www.wikidata.org/wiki/Property:P12597)
[7022](https://term.museum-digital.de/md-de/persinst/7022)
[0 references]()
[National Library of Wales Authority ID](https://www.wikidata.org/wiki/Property:P2966)
[pompey-great-106-48-b-c](https://archives.library.wales/index.php/pompey-great-106-48-b-c)
[0 references]()
[NE.se ID](https://www.wikidata.org/wiki/Property:P3222)
[pompejus](https://www.ne.se/uppslagsverk/encyklopedi/l%C3%A5ng/pompejus)
[0 references]()
[Nomisma ID](https://www.wikidata.org/wiki/Property:P2950)
[pompey](https://nomisma.org/id/pompey)
[0 references]()
[Notable Names Database ID](https://www.wikidata.org/wiki/Property:P1263)
[842/000092566](https://www.nndb.com/people/842/000092566/)
[0 references]()
[Online PWN Encyclopedia ID](https://www.wikidata.org/wiki/Property:P7305)
[3960260](https://encyklopedia.pwn.pl/haslo/;3960260.html)
[0 references]()
[PACTOLS thesaurus ID](https://www.wikidata.org/wiki/Property:P4212)
[pcrtVl86Dcsi63](https://ark.frantiq.fr/ark:/26678/pcrtVl86Dcsi63/)
[0 references]()
[Parsifal cluster ID](https://www.wikidata.org/wiki/Property:P12458)
[107868](https://parsifal.urbe.it/parsifal/searchNames?n_cluster_id=107868)
[0 references]()
[Pontifical University of Salamanca ID](https://www.wikidata.org/wiki/Property:P9247)
[475250](https://koha.upsa.es/cgi-bin/koha/opac-authoritiesdetail.pl?marc=1&authid=475250)
[0 references]()
[Proleksis enciklopedija ID](https://www.wikidata.org/wiki/Property:P8349)
[41068](https://proleksis.lzmk.hr/41068)
[0 references]()
[Prosopographia Imperii Romani online ID](https://www.wikidata.org/wiki/Property:P10382)
[10708](https://pir.bbaw.de/id/10708)
[0 references]()
[SAIA authority ID](https://www.wikidata.org/wiki/Property:P9536)
[5a1d4d054ab9d081344cacf8](https://saia.openabekt.gr/en/authorities/5a1d4d054ab9d081344cacf8/show)
[0 references]()
[Sandrart.net person ID](https://www.wikidata.org/wiki/Property:P1422)
[251](http://ta.sandrart.net/en/person/view/251)
[0 references]()
[SEARCH on line catalogue ID](https://www.wikidata.org/wiki/Property:P9081)
[9994](https://www.search-libnet.org/cgi-bin/koha/opac-authoritiesdetail.pl?marc=1&authid=9994)
 
[0 references]()
[17034](https://www.search-libnet.org/cgi-bin/koha/opac-authoritiesdetail.pl?marc=1&authid=17034)
 
[0 references]()
[SNARC ID](https://www.wikidata.org/wiki/Property:P12749)
[Q57568](https://snarc-llgc.wikibase.cloud/wiki/Item:Q57568)
[0 references]()
[Spanish Biographical Dictionary ID](https://www.wikidata.org/wiki/Property:P4459)
[17106/pompeyo-magno](https://dbe.rah.es/biografias/17106/pompeyo-magno)
[0 references]()
[Great Norwegian Encyclopedia ID](https://www.wikidata.org/wiki/Property:P4342)
[Gnaeus_Pompeius_-_den_eldre](https://wikidata-externalid-url.toolforge.org/?p=4342&url_prefix=https://snl.no/&id=Gnaeus_Pompeius_-_den_eldre)
[0 references]()
[Svenska Institutet i Rom ID](https://www.wikidata.org/wiki/Property:P9164)
[4542](https://biblio.isvroma.it/cgi-bin/koha/opac-authoritiesdetail.pl?marc=1&authid=4542)
[0 references]()
[ToposText person ID](https://www.wikidata.org/wiki/Property:P8069)
[7](https://topostext.org/people/7)
[0 references]()
[Treccani's Dizionario di Storia ID](https://www.wikidata.org/wiki/Property:P6404)
[gneo-pompeo-magno](https://www.treccani.it/enciclopedia/gneo-pompeo-magno_(Dizionario-di-Storia))
[subject named as](https://www.wikidata.org/wiki/Property:P1810)
Pompeo Magno, Gneo
[publication date](https://www.wikidata.org/wiki/Property:P577)
2011
[0 references]()
[Trismegistos author ID](https://www.wikidata.org/wiki/Property:P11252)
[8063](https://www.trismegistos.org/author/8063)
[0 references]()
[Unione Romana Biblioteche Scientifiche ID](https://www.wikidata.org/wiki/Property:P8750)
[1414](http://koha-urbs.reteurbs.org/cgi-bin/koha/opac-authoritiesdetail.pl?marc=1&authid=1414)
[0 references]()
[V\&A person ID](https://www.wikidata.org/wiki/Property:P6764)
[N397](https://collections.vam.ac.uk/name/wd/N397/)
[0 references]()
[Vatican Library ID (former scheme)](https://www.wikidata.org/wiki/Property:P1017)
[ADV12566798](https://web.archive.org/web/*/https://viaf.org/processed/BAV%7CADV12566798)
[1 reference]()
[Vikidia article ID](https://www.wikidata.org/wiki/Property:P12800)
[fr:Pompée](https://central.vikidia.org/wiki/fr%3APomp%C3%A9e)
 
[0 references]()
[Visuotinė lietuvių enciklopedija ID](https://www.wikidata.org/wiki/Property:P7666)
[pompejus-didysis](https://www.vle.lt/straipsnis/pompejus-didysis/)
[0 references]()
[Wolfram Language entity code](https://www.wikidata.org/wiki/Property:P4839)
[Entity["Concept", "GnaeusPompeiusMagnus::fq5bb"]](https://www.wolframalpha.com/input/?i=Entity%5B%22Concept%22%2C%20%22GnaeusPompeiusMagnus%3A%3Afq5bb%22%5D)
[0 references]()
[WordNet 3.1 Synset ID](https://www.wikidata.org/wiki/Property:P8814)
[11261844-n](https://en-word.net/id/oewn-11261844-n)
[0 references]()
[World History Encyclopedia ID](https://www.wikidata.org/wiki/Property:P9000)
[pompey](https://www.worldhistory.org/pompey/)
[0 references]()
[‎Yale LUX ID](https://www.wikidata.org/wiki/Property:P13591)
[person/06acfdf5-030c-4f8c-aef5-c1d19878026a](https://lux.collections.yale.edu/view/person/06acfdf5-030c-4f8c-aef5-c1d19878026a)
[0 references]()
[genealogics.org person ID](https://www.wikidata.org/wiki/Property:P1819)
[I00446750](https://www.genealogics.org/getperson.php?personID=I00446750&tree=LEO)
[0 references]()
[Geni.com profile ID](https://www.wikidata.org/wiki/Property:P2600)
[6000000005933238750](https://www.geni.com/profile/index/6000000005933238750)
[0 references]()
[Rodovid ID](https://www.wikidata.org/wiki/Property:P1185)
[86084](https://en.rodovid.org/wk/Person:86084)
[0 references]()
[WeRelate person ID](https://www.wikidata.org/wiki/Property:P4159)
[Pompey_(1)](https://www.werelate.org/wiki/Person:Pompey_%281%29)
[0 references]()
[Arab Encyclopedia concept ID](https://www.wikidata.org/wiki/Property:P13750)
[3203](https://arab-ency.com.sy/details/3203)
[0 references]()
Wikipedia(87 entries)
 
af[Pompeius](https://af.wikipedia.org/wiki/Pompeius)
am[ፖምፐይ](https://am.wikipedia.org/wiki/%E1%8D%96%E1%88%9D%E1%8D%90%E1%8B%AD)
ang[Gnaeus Pompeius Magnus](https://ang.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
an[Gneu Pompeyo Magno](https://an.wikipedia.org/wiki/Gneu_Pompeyo_Magno)
ar[بومبيوس الكبير](https://ar.wikipedia.org/wiki/%D8%A8%D9%88%D9%85%D8%A8%D9%8A%D9%88%D8%B3_%D8%A7%D9%84%D9%83%D8%A8%D9%8A%D8%B1)
arz[بومبيوس الكبير](https://arz.wikipedia.org/wiki/%D8%A8%D9%88%D9%85%D8%A8%D9%8A%D9%88%D8%B3_%D8%A7%D9%84%D9%83%D8%A8%D9%8A%D8%B1)
ast[Cneu Pompeyu Magnu](https://ast.wikipedia.org/wiki/Cneu_Pompeyu_Magnu)
az[Qney Pompey](https://az.wikipedia.org/wiki/Qney_Pompey)
be_x_old[Гнэй Пампэй](https://be-tarask.wikipedia.org/wiki/%D0%93%D0%BD%D1%8D%D0%B9_%D0%9F%D0%B0%D0%BC%D0%BF%D1%8D%D0%B9)
be[Гней Пампей Вялікі](https://be.wikipedia.org/wiki/%D0%93%D0%BD%D0%B5%D0%B9_%D0%9F%D0%B0%D0%BC%D0%BF%D0%B5%D0%B9_%D0%92%D1%8F%D0%BB%D1%96%D0%BA%D1%96)
bg[Помпей Велики](https://bg.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D0%B9_%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%B8)
bn[পম্পে](https://bn.wikipedia.org/wiki/%E0%A6%AA%E0%A6%AE%E0%A7%8D%E0%A6%AA%E0%A7%87)
bo[ཕང་ཕེ་](https://bo.wikipedia.org/wiki/%E0%BD%95%E0%BD%84%E0%BC%8B%E0%BD%95%E0%BD%BA%E0%BC%8B)
br[Gnaeus Pompeius Magnus](https://br.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
bs[Pompej](https://bs.wikipedia.org/wiki/Pompej)
ca[Gneu Pompeu Magne](https://ca.wikipedia.org/wiki/Gneu_Pompeu_Magne)
cs[Pompeius](https://cs.wikipedia.org/wiki/Pompeius)
cv[Аслă Гней Помпей](https://cv.wikipedia.org/wiki/%D0%90%D1%81%D0%BB%C4%83_%D0%93%D0%BD%D0%B5%D0%B9_%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D0%B9)
cy[Gnaeus Pompeius Magnus](https://cy.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
da[Pompejus](https://da.wikipedia.org/wiki/Pompejus)
de[Gnaeus Pompeius Magnus](https://de.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
el[Πομπήιος](https://el.wikipedia.org/wiki/%CE%A0%CE%BF%CE%BC%CF%80%CE%AE%CE%B9%CE%BF%CF%82)
en[Pompey](https://en.wikipedia.org/wiki/Pompey)
eo[Pompeo](https://eo.wikipedia.org/wiki/Pompeo)
es[Pompeyo](https://es.wikipedia.org/wiki/Pompeyo)
et[Pompeius](https://et.wikipedia.org/wiki/Pompeius)
eu[Ponpeio](https://eu.wikipedia.org/wiki/Ponpeio)
fa[پومپه](https://fa.wikipedia.org/wiki/%D9%BE%D9%88%D9%85%D9%BE%D9%87)
fi[Pompeius](https://fi.wikipedia.org/wiki/Pompeius)
fr[Pompée](https://fr.wikipedia.org/wiki/Pomp%C3%A9e)
fy[Pompejus](https://fy.wikipedia.org/wiki/Pompejus)
ga[Gnaeus Pompeius Magnus](https://ga.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
gl[Cneo Pompeio Magno](https://gl.wikipedia.org/wiki/Cneo_Pompeio_Magno)
he[גנאיוס פומפיוס מגנוס](https://he.wikipedia.org/wiki/%D7%92%D7%A0%D7%90%D7%99%D7%95%D7%A1_%D7%A4%D7%95%D7%9E%D7%A4%D7%99%D7%95%D7%A1_%D7%9E%D7%92%D7%A0%D7%95%D7%A1)
hr[Pompej Veliki](https://hr.wikipedia.org/wiki/Pompej_Veliki)
hu[Cnaeus Pompeius Magnus](https://hu.wikipedia.org/wiki/Cnaeus_Pompeius_Magnus)
hy[Գնեոս Պոմպեոս](https://hy.wikipedia.org/wiki/%D4%B3%D5%B6%D5%A5%D5%B8%D5%BD_%D5%8A%D5%B8%D5%B4%D5%BA%D5%A5%D5%B8%D5%BD)
ia[Pompeio Magne](https://ia.wikipedia.org/wiki/Pompeio_Magne)
id[Pompeius](https://id.wikipedia.org/wiki/Pompeius)
is[Pompeius](https://is.wikipedia.org/wiki/Pompeius)
it[Gneo Pompeo Magno](https://it.wikipedia.org/wiki/Gneo_Pompeo_Magno)
ja[グナエウス・ポンペイウス](https://ja.wikipedia.org/wiki/%E3%82%B0%E3%83%8A%E3%82%A8%E3%82%A6%E3%82%B9%E3%83%BB%E3%83%9D%E3%83%B3%E3%83%9A%E3%82%A4%E3%82%A6%E3%82%B9)
ka[გნეუს პომპეუს მაგნუსი](https://ka.wikipedia.org/wiki/%E1%83%92%E1%83%9C%E1%83%94%E1%83%A3%E1%83%A1_%E1%83%9E%E1%83%9D%E1%83%9B%E1%83%9E%E1%83%94%E1%83%A3%E1%83%A1_%E1%83%9B%E1%83%90%E1%83%92%E1%83%9C%E1%83%A3%E1%83%A1%E1%83%98)
kk[Гней Помпей Магнус](https://kk.wikipedia.org/wiki/%D0%93%D0%BD%D0%B5%D0%B9_%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D0%B9_%D0%9C%D0%B0%D0%B3%D0%BD%D1%83%D1%81)
ko[그나이우스 폼페이우스 마그누스](https://ko.wikipedia.org/wiki/%EA%B7%B8%EB%82%98%EC%9D%B4%EC%9A%B0%EC%8A%A4_%ED%8F%BC%ED%8E%98%EC%9D%B4%EC%9A%B0%EC%8A%A4_%EB%A7%88%EA%B7%B8%EB%88%84%EC%8A%A4)
kw[Pompi](https://kw.wikipedia.org/wiki/Pompi)
ky[Помпей Гней](https://ky.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D0%B9_%D0%93%D0%BD%D0%B5%D0%B9)
la[Gnaeus Pompeius Magnus](https://la.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
lo[ປອມເປ (Pompey)](https://lo.wikipedia.org/wiki/%E0%BA%9B%E0%BA%AD%E0%BA%A1%E0%BB%80%E0%BA%9B_(Pompey))
lt[Gnėjus Pompėjus Didysis](https://lt.wikipedia.org/wiki/Gn%C4%97jus_Pomp%C4%97jus_Didysis)
lv[Gnejs Pompejs](https://lv.wikipedia.org/wiki/Gnejs_Pompejs)
mg[Pômpeio](https://mg.wikipedia.org/wiki/P%C3%B4mpeio)
ml[പോംപി](https://ml.wikipedia.org/wiki/%E0%B4%AA%E0%B5%8B%E0%B4%82%E0%B4%AA%E0%B4%BF)
mn[Гней Помпей Магн](https://mn.wikipedia.org/wiki/%D0%93%D0%BD%D0%B5%D0%B9_%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D0%B9_%D0%9C%D0%B0%D0%B3%D0%BD)
mr[पोम्पे](https://mr.wikipedia.org/wiki/%E0%A4%AA%E0%A5%8B%E0%A4%AE%E0%A5%8D%E0%A4%AA%E0%A5%87)
ms[Pompeius](https://ms.wikipedia.org/wiki/Pompeius)
nds[Gnaeus Pompeius Magnus](https://nds.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
nl[Pompeius](https://nl.wikipedia.org/wiki/Pompeius)
nn[Pompeius](https://nn.wikipedia.org/wiki/Pompeius)
no[Pompeius](https://no.wikipedia.org/wiki/Pompeius)
oc[Pompèu](https://oc.wikipedia.org/wiki/Pomp%C3%A8u)
pa[ਪੋਂਪੀ](https://pa.wikipedia.org/wiki/%E0%A8%AA%E0%A9%8B%E0%A8%82%E0%A8%AA%E0%A9%80)
pl[Pompejusz](https://pl.wikipedia.org/wiki/Pompejusz)
pt[Pompeu](https://pt.wikipedia.org/wiki/Pompeu)
ro[Cneus Pompeius Magnus](https://ro.wikipedia.org/wiki/Cneus_Pompeius_Magnus)
ru[Гней Помпей Великий](https://ru.wikipedia.org/wiki/%D0%93%D0%BD%D0%B5%D0%B9_%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D0%B9_%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%B8%D0%B9)
sh[Pompej](https://sh.wikipedia.org/wiki/Pompej)
simple[Pompey](https://simple.wikipedia.org/wiki/Pompey)
sk[Gnaeus Pompeius Magnus](https://sk.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
sl[Pompej Veliki](https://sl.wikipedia.org/wiki/Pompej_Veliki)
sq[Pompeu](https://sq.wikipedia.org/wiki/Pompeu)
sr[Гнеј Помпеј Велики](https://sr.wikipedia.org/wiki/%D0%93%D0%BD%D0%B5%D1%98_%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D1%98_%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%B8)
stq[Gnaeus Pompeius Magnus](https://stq.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
sv[Pompejus](https://sv.wikipedia.org/wiki/Pompejus)
ta[பாம்பே (உரோம்)](https://ta.wikipedia.org/wiki/%E0%AE%AA%E0%AE%BE%E0%AE%AE%E0%AF%8D%E0%AE%AA%E0%AF%87_(%E0%AE%89%E0%AE%B0%E0%AF%8B%E0%AE%AE%E0%AF%8D))
th[ปอมปีย์](https://th.wikipedia.org/wiki/%E0%B8%9B%E0%B8%AD%E0%B8%A1%E0%B8%9B%E0%B8%B5%E0%B8%A2%E0%B9%8C)
tl[Pompeyo](https://tl.wikipedia.org/wiki/Pompeyo)
tr[Gnaeus Pompeius Magnus](https://tr.wikipedia.org/wiki/Gnaeus_Pompeius_Magnus)
uk[Гней Помпей](https://uk.wikipedia.org/wiki/%D0%93%D0%BD%D0%B5%D0%B9_%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D0%B9)
ur[پومپی](https://ur.wikipedia.org/wiki/%D9%BE%D9%88%D9%85%D9%BE%DB%8C)
uz[Gney Pompey](https://uz.wikipedia.org/wiki/Gney_Pompey)
vi[Pompey](https://vi.wikipedia.org/wiki/Pompey)
war[Pompeyo](https://war.wikipedia.org/wiki/Pompeyo)
wuu[格奈乌斯·庞培](https://wuu.wikipedia.org/wiki/%E6%A0%BC%E5%A5%88%E4%B9%8C%E6%96%AF%C2%B7%E5%BA%9E%E5%9F%B9)
xmf[გნეუს პომპეუსი](https://xmf.wikipedia.org/wiki/%E1%83%92%E1%83%9C%E1%83%94%E1%83%A3%E1%83%A1_%E1%83%9E%E1%83%9D%E1%83%9B%E1%83%9E%E1%83%94%E1%83%A3%E1%83%A1%E1%83%98)
zh_yue[龐培](https://zh-yue.wikipedia.org/wiki/%E9%BE%90%E5%9F%B9)
zh[格奈乌斯·庞培](https://zh.wikipedia.org/wiki/%E6%A0%BC%E5%A5%88%E4%B9%8C%E6%96%AF%C2%B7%E5%BA%9E%E5%9F%B9)
Wikibooks(0 entries)
 
Wikinews(0 entries)
 
Wikiquote(11 entries)
 
de[Gnaeus Pompeius Magnus](https://de.wikiquote.org/wiki/Gnaeus_Pompeius_Magnus)
en[Pompey](https://en.wikiquote.org/wiki/Pompey)
fr[Pompée](https://fr.wikiquote.org/wiki/Pomp%C3%A9e)
it[Gneo Pompeo Magno](https://it.wikiquote.org/wiki/Gneo_Pompeo_Magno)
la[Gnaeus Pompeius Magnus](https://la.wikiquote.org/wiki/Gnaeus_Pompeius_Magnus)
lt[Gnėjus Pompėjus Didysis](https://lt.wikiquote.org/wiki/Gn%C4%97jus_Pomp%C4%97jus_Didysis)
pl[Pompejusz](https://pl.wikiquote.org/wiki/Pompejusz)
pt[Pompeu](https://pt.wikiquote.org/wiki/Pompeu)
sr[Гнеј Помпеј Велики](https://sr.wikiquote.org/wiki/%D0%93%D0%BD%D0%B5%D1%98_%D0%9F%D0%BE%D0%BC%D0%BF%D0%B5%D1%98_%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%B8)
sv[Pompejus](https://sv.wikiquote.org/wiki/Pompejus)
tr[Pompey](https://tr.wikiquote.org/wiki/Pompey)
Wikisource(1 entry)
 
it[Autore:Gneo Pompeo Magno](https://it.wikisource.org/wiki/Autore:Gneo_Pompeo_Magno)
Wikiversity(0 entries)
 
Wikivoyage(0 entries)
 
Wiktionary(0 entries)
 
Multilingual sites(1 entry)
 
commons[Gnaeus Pompeius Magnus](https://commons.wikimedia.org/wiki/Gnaeus_Pompeius_Magnus)
This page was last edited on 10 December 2025, at 15:48.

Below is a compact “profile table” of Pompey’s attributes and external IDs, plus a suggested core person schema and which things should be promoted to first‑class nodes.[^3_1][^3_2][^3_3][^3_4][^3_5]

***

## 1. Core biographical attributes

| Attribute / property | Meaning | How to use in a graph |
| :-- | :-- | :-- |
| instance of (P31) = human (Q5) | Declares the item is a human being. [^3_1] | Type the node as `:Person` and separate it from places, works, etc. |
| sex or gender (P21) = male | Biological sex / gender identity. [^3_1] | Simple property on `Person`; useful for demographic, prosopographical stats. |
| country of citizenship (P27) = Ancient Rome (Q1747689) | Political belonging in life. [^3_1][^3_6] | Edge `(:Person)-[:CITIZEN_OF]->(:Polity)`; links to Roman Republic polity for political/legal queries. |
| name in native language (P1559) | Full Roman name in Latin. [^3_1][^3_2] | Store as `nativeName`; drives epigraphic/textual matching, language‑aware display. |
| praenomen / nomen / cognomen (P2358/2359/2365) | Components of tria nomina. [^3_1][^3_6] | First‑class nodes for Roman onomastics and gens networks (e.g. `:Praenomen`, `:Gens`, `:Cognomen`), plus literal string properties on `Person`. |
| date of birth / death (P569/P570) + earliest (P1319) / latest (P1326) | Life span with uncertainty windows. [^3_1][^3_2] | Model as interval node or value with bounds; critical for temporal faceting, overlap with events and offices. |
| place of birth (P19) = Regio V Picenum (Q510990) | Birth region. [^3_1] | Edge `BORN_IN` to a place node (aligned to Pleiades if possible). Anchors regional origins. |
| place of death (P20) = Pelusium (Q1145715) | Where he died. [^3_1][^3_2] | Edge `DIED_IN` to place; used for spatial trajectories and end‑of‑life events. |
| manner of death (P1196) = homicide / cause of death (P509) = stab wound | Circumstances of death. [^3_1][^3_2] | Either properties on a `DeathEvent` node or direct attributes, useful for event modelling (assassinations, executions, battle deaths). |
| time period (P2348) = Late Roman Republic (Q2815472) | Historiographical period classification. [^3_1][^3_6][^3_2] | Edge to a `:Period` node (ideally PeriodO), giving high‑level temporal context for clustering. |


***

## 2. Family and social relations

| Property | Meaning | How to use |
| :-- | :-- | :-- |
| father (P22), mother (P25) | Parents. [^3_1][^3_6] | `(:Person)-[:CHILD_OF]->(:Person)`; enables family trees and elite lineage analysis. |
| sibling (P3373) | Siblings. [^3_1] | Derivable from sharing parents, but can be explicitly stored as `SIBLING_OF` edges. |
| spouse (P26) + start/end time (P580/P582) + series ordinal (P1545) | Marriages with chronology and ordering. [^3_1][^3_6][^3_2] | First‑class `:Marriage` event node with edges to both spouses and time interval; supports marital networks and alliance patterns. |
| child (P40) + mother (P25) on child | Children and maternal link. [^3_1][^3_6][^3_2] | Parent–child edges; plus maternal lines for gens and inheritance studies. |
| gens (P5025) = Pompeia gens | Roman clan. [^3_1][^3_6] | `(:Person)-[:MEMBER_OF_GENS]->(:Gens)`; major first‑class node for elite network structure. |
| member of Roman tribe (P11491) = Clustumina | Voting tribe. [^3_1] | `MEMBER_OF_TRIBE` edge to `:Tribe`; supports comitial and regional analysis. |
| social classification (P3716) = noble, equites (Q122166) | Social orders. [^3_1][^3_3][^3_4] | `(:Person)-[:IN_SOCIAL_ORDER]->(:Order)`; key for SOCIAL facet queries. |
| member of (P463) = First Triumvirate (Q715380) | Membership in a political grouping. [^3_1][^3_6][^3_2] | `(:Person)-[:MEMBER_OF]->(:PoliticalGroup)`; central to modelling coalitions and factions. |


***

## 3. Political, military, religious roles

| Property | Meaning | How to use |
| :-- | :-- | :-- |
| occupation (P106) = politician, military personnel | Generic roles. [^3_1][^3_6][^3_2][^3_3] | Light‑weight tagging; can be inferred from specific offices but useful for filtering. |
| position held (P39) = praetor, quaestor, senator, consul, moneyer | Offices with some time qualifiers and colleagues. [^3_1][^3_6][^3_2][^3_3] | Model each as an `OfficeHolding` node: `Person-[:HELD_OFFICE]->OfficeHolding-[:OF_OFFICE_TYPE]->OfficeType`, with `start`, `end`, `togetherWith`, `location`. Connect `OfficeType` to DPRR and your magistracies SubjectConcept. |
| member of political party (P102) = optimates | Faction. [^3_1][^3_6][^3_2] | `MEMBER_OF_FACTION` edge to `:PoliticalFaction`; supports POLITICAL facet queries and clustering. |
| military, police or special rank (P410) = legatus | Rank. [^3_1][^3_6][^3_2] | `HELD_RANK` relationships to `:Rank` nodes; crosswalk to DPRR and epigraphic ranks. |
| military branch (P241) = Roman army | Arm of service. [^3_1][^3_6] | `SERVED_IN` edge to `:MilitaryBranch`. |
| religion or worldview (P140) = ancient Roman religion | Cultic context. [^3_1] | `HAS_RELIGION` edge to `:Religion`; useful for RELIGIOUS facet but simple model. |


***

## 4. Intellectual / textual / reference layer

| Property | Meaning | How to use |
| :-- | :-- | :-- |
| described by source (P1343) + statement is subject of (P805) | Canonical reference works (Pauly‑Wissowa, Britannica 1911, etc.) that have articles on Pompey. [^3_1][^3_2] | Each source is a `:Work` node; edge `(:Person)-[:HAS_ENTRY_IN]->(:ReferenceWork)` with optional page/article IDs; this is the backbone of your INTELLECTUAL facet. |
| present in work (P1441) | Appears as a character in a work. [^3_1] | `PRESENT_IN` edges to narrative/visual works (`:Work`); useful for reception / cultural memory queries. |
| depicted by (P1299) | Depictions (paintings, etc.). [^3_1] | `DEPICTED_BY` edges to `:VisualWork` nodes (link to ULAN / museum IDs). |
| URL (P2699) | Deep links to encyclopedia entries (Oxford, etc.). [^3_1][^3_2] | Attach as identifiers on the `ReferenceWork` or `AuthorityRecord` nodes; use for outbound navigation. |
| topic’s main category (P910), Commons gallery/category, Wikipedia/Wikiquote/Wikisource sitelinks | Aggregated content hubs. [^3_1][^3_6] | `HAS_TOPIC_CATEGORY` edges to category nodes; from your perspective, they’re “entrypoint” or UI/UX metadata rather than analytic core. |


***

## 5. Authority and identifier layer (VIAF, FAST, DPRR, Nomisma, etc.)

All these are *bridges* into external authority systems. For your federation, they typically become **AuthorityRecord** nodes, one per authority, all linked back to the core `Person` and sometimes to each other via VIAF/WorldCat Entities.[^3_3][^3_7][^3_4][^3_5][^3_1]


| ID type | Example here | Meaning / role | How you use it |
| :-- | :-- | :-- | :-- |
| VIAF (P214), WorldCat Entities (P10832), FAST (P2163) | VIAF 6224297; WorldCat entity ID; FAST 1841849. [^3_1] | Cluster of library authority records and subject heading for Pompey. | Create `AuthorityRecord` nodes for VIAF, WorldCat, FAST; use them to attach bibliographic corpora and subject‑based works to Pompey, and to unify national library IDs via VIAF. |
| National library \& authority IDs (LOCSH P244, BNF P268, GND P227, NDL P349, etc.) | n80013395 (LC); 11938643b (BNF); 118595636 (GND)… [^3_1] | Local authority files from many libraries. | Model as additional `AuthorityRecord` nodes keyed by scheme; connect them to VIAF/WorldCat cluster and to person. Use to pull in catalogue data, subject strings, and editions. |
| ULAN ID (P245) | 500355380 (Getty ULAN). [^3_1] | Art / museum authority. | Connect to visual/monumental depictions; bridges to AAT and object records. |
| DPRR ID (P6863) | 1976 (DPRR person). [^3_1][^3_3][^3_4] | Direct bridge into Digital Prosopography of the Roman Republic. | First‑class `AuthorityRecord` that you *also* map to your own DPRR `:Person` node; this is your most important prosopographical cross‑walk. |
| Nomisma ID (P2950) | pompey. [^3_1][^3_5] | Numismatic authority; cluster of coin types, mints, legends. | Node `NomismaPerson` linked to Pompey; from there, connect to `CoinType` nodes for economic / propaganda analysis. |
| Prosopographia Imperii Romani (P10382), Trismegistos author (P11252), etc. | IDs in specialized prosopographies. [^3_1] | Domain authority systems. | Map to additional `AuthorityRecord`s; unify through `SAME_AS` edges; ideal for cross‑corpus person reconciliation. |
| Genealogical IDs (Geni, Rodovid, genealogics, WeRelate) | Person IDs in genealogical sites. [^3_1] | Modern genealogical trees. | Optional; can backfill extended family relations but are secondary for scholarly KG. |
| Encyclopedia \& dictionary IDs (Britannica, Treccani, Larousse, etc.) | `P1417`, `P6404`, etc. [^3_1][^3_2] | Cross‑lingual reference entries. | Nodes `ReferenceWorkEntry` with language + URL; connect to `Person` for multilingual coverage and as starting points for text ingestion. |


***

## 6. Suggested core person schema (for Chrystallum)

For a **Roman elite person** like Pompey, I’d treat the schema in three layers:

### 6.1 Core `Person` node (Pompey himself)

Properties (lightweight, mostly literals):

- `id_local` (your internal ID)
- `id_wikidata = Q125414`[^3_1]
- `label_en = 'Gnaeus Pompeius Magnus'`[^3_2][^3_1]
- `nativeName = 'Cn. Pompeius Cn.f.Sex.n. Clu. Magnus'`[^3_1]
- `gender = 'male'`
- `birth_earliest = -0106-09-29`, `birth_latest = -0106-09-30`[^3_2][^3_1]
- `death_date = -0048-09-28`[^3_2][^3_1]

Relations (edges to first‑class nodes):

- `(:Person)-[:CITIZEN_OF]->(:Polity)` (Roman Republic / Ancient Rome).[^3_6][^3_1]
- `CHILD_OF`, `SIBLING_OF`, `SPOUSE_IN` (event), `PARENT_OF`.
- `MEMBER_OF_GENS` → `:Gens(Pompeia)`; `MEMBER_OF_TRIBE` → `:Tribe(Clustumina)`.[^3_1]
- `IN_SOCIAL_ORDER` → `:Order(nobilis), :Order(eques)` etc.[^3_3][^3_1]
- `HELD_OFFICE` → `:OfficeHolding` nodes (see below).[^3_3][^3_1]
- `SERVED_IN` → `:MilitaryBranch(Roman army)`; `HELD_RANK` → `:Rank(legatus)`.[^3_6][^3_1]
- `HAS_RELIGION` → `:Religion(ancient Roman religion)`.[^3_1]
- `LINKED_VIA_AUTHORITY` → `AuthorityRecord` nodes (VIAF, DPRR, Nomisma, LC, BNF, FAST, etc.).[^3_4][^3_5][^3_3][^3_1]
- `HAS_ENTRY_IN` → `ReferenceWorkEntry` nodes (Pauly‑Wissowa article, Britannica, etc.).[^3_2][^3_1]
- `BORN_IN` / `DIED_IN` → `:Place` nodes that themselves are mapped to Pleiades / TGN.[^3_2][^3_1]
- `IN_PERIOD` → `:Period(Late Roman Republic)` (sourced from PeriodO, eventually).[^3_6][^3_1][^3_2]


### 6.2 First‑class nodes (strongly recommended)

These deserve their own nodes because they are reused heavily across persons and sit at the intersection of multiple facets:

- `:Gens` (Pompeia), `:Praenomen` (Gnaeus), `:Cognomen` (Magnus).[^3_6][^3_1]
- `:Polity` (Roman Republic, Ancient Rome).[^3_6][^3_1]
- `:Period` (Late Roman Republic and other scholarly period definitions).[^3_1][^3_6][^3_2]
- `:Place` (Regio V Picenum, Pelusium, Roma).[^3_2][^3_1]
- `:OfficeType` (consul, praetor, quaestor, senator, moneyer).[^3_3][^3_1]
- `:OfficeHolding` event nodes (Pompey’s consulate of 70, his praetorship, etc.).[^3_3][^3_1][^3_2]
- `:SocialOrder` (nobilis, eques).[^3_4][^3_3][^3_1]
- `:PoliticalFaction` (optimates, First Triumvirate).[^3_6][^3_1][^3_2]
- `:Religion`.[^3_1]
- `:AuthorityRecord` (VIAF, LC, BNF, GND, DPRR, Nomisma, etc.).[^3_7][^3_5][^3_4][^3_3][^3_1]
- `:ReferenceWork` / `:ReferenceWorkEntry`.[^3_2][^3_1]
- `:CoinType` and `:NomismaPerson` (for numismatic links).[^3_5]
- `:Marriage` and (optionally) `:DeathEvent` nodes for detailed temporal modelling.[^3_1][^3_2]


### 6.3 Second‑class / attached data (properties or small nodes)

More optional, often modelled as properties unless you need full event semantics:

- `mannerOfDeath`, `causeOfDeath` (can be properties on `DeathEvent`).[^3_2][^3_1]
- Language competence (Latin); native language.[^3_1]
- Generic `occupation` tags (“politician”, “military personnel”).[^3_6][^3_2][^3_1]
- Sitelinks (Wikipedia, Wikiquote, Commons); keep as outbound links or a single `WebPresence` node.[^3_6][^3_1]

***

If you want, next step I can sketch a JSON/labelled‑property schema for a “Pompey bundle” that could be auto‑generated from Wikidata + DPRR + Nomisma for any Roman elite you ingest.[^3_5][^3_4][^3_3][^3_1]
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://www.wikidata.org/wiki/Q125414

[^3_2]: https://www.britannica.com/biography/Pompey-the-Great

[^3_3]: https://kdl.kcl.ac.uk/projects/dprr/

[^3_4]: https://wiki.digitalclassicist.org/Digital_Prosopography_of_the_Roman_Republic

[^3_5]: https://github.com/nomisma/data/blob/master/id/pompey.rdf

[^3_6]: https://en.wikipedia.org/wiki/Pompey

[^3_7]: http://ancientworldonline.blogspot.com/2024/05/digital-prosopography-of-roman-republic.html

[^3_8]: https://www.wikidata.org/wiki/Q473280

[^3_9]: https://www.wikidata.org/wiki/Q1338377

[^3_10]: https://coinweek.com/the-ancient-coins-of-pompey-the-great/

[^3_11]: https://www.nps.gov/people/pompey-factor.htm

[^3_12]: https://www.ebsco.com/research-starters/history/pompey-great

[^3_13]: https://silver.kbr.be/Sextus_Pompeius_Magnus_Pius

[^3_14]: https://chscp.org.uk/wp-content/uploads/2019/01/FAST-operational-protocol.pdf

[^3_15]: https://spartacus.fandom.com/wiki/Gnaeus_Pompeius_Magnus

