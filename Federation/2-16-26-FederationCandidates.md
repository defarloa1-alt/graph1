#FederationCandidates
Here’s a “how to best use each federation” map in the same spirit as the BabelNet answer, but now grounded in your federation files. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)

***

## Wikidata – central hub

**Role in Chrystallum**

- Broad **identity hub** and router: first stop for QIDs, basic facts, and external IDs. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/e258096f-73f6-40e1-9e05-1bf4f8112484/2-12-26-federations.md)
- Lives at **Layer 2 Federation** with confidence floor 0.90. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/81085e9a-39e1-47af-bf4e-42957bbe0252/STEP_1_COMPLETE.md)

**How to leverage**

- Always resolve candidate entities (people, places, periods, concepts) to a Wikidata QID first.  
- Use:
  - Labels, descriptions, aliases, P31/P279/P361, and key properties as **event/period seeds**.  
  - External IDs (P214, P1584, P1566, P2950, etc.) as jump‑off points into domain authorities (VIAF, Pleiades, GeoNames, Nomisma…). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)
- Treat as **discovery + routing**, not final authority; let deeper federations set hard constraints. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)

***

## Pleiades – ancient places backbone

**Role**

- Authority for **ancient geographic concepts**, not just points. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
- Key for `Place` and `PlaceVersion` nodes.

**How to leverage**

- For any ancient place:
  - Resolve to Pleiades ID (via Wikidata P1584 where available). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)
  - Pull:
    - Coordinate ranges.  
    - Ancient/modern name variants.  
    - Validity periods (which periods the place “exists” in). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
- Use temporal validity to:
  - Constrain events: events at that place must fall within its active period unless explicitly marked anachronistic. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
  - Support **geo‑temporal federation** (your future joint layer). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/e258096f-73f6-40e1-9e05-1bf4f8112484/2-12-26-federations.md)

***

## Trismegistos – texts, people, local geo

**Role**

- Epigraphic/papyrological hub for **people, places, and texts** in documents. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)

**How to leverage**

- People:
  - Use TMPeople to check whether a name appears in documentary sources.  
  - Combine with PIR/PLRE to distinguish **well‑attested elites vs. purely textual figures**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
- Places:
  - Use TMGeo for village/quarter‑level geography, especially in Egypt/Eastern Mediterranean. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
  - Map TMGeo → Pleiades to anchor micro‑places in global ancient map.
- Texts:
  - Use TMTexts to create **Communication/Evidence nodes** (papyrus, inscription) with date, material, and findspot. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
- Use Trismegistos presence as a **confidence bump**: an entity or event with papyrological/epigraphic evidence is structurally stronger than one only in Wikidata. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)

***

## Epigraphic Database Heidelberg (EDH) – Latin inscription evidence

**Role**

- Authority for **Latin inscriptions** and their findspots/dates. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)

**How to leverage**

- For Events and Persons:
  - Search EDH inscriptions mentioning them.  
  - Create `Evidence` / `Communication` nodes for each inscription:
    - Full text, material, dimensions, findspot, date range. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
  - Link to Events with roles like `PRIMARY_EPIGRAPHIC_EVIDENCE` and to Places (via Pleiades/GeoNames). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
- Raise Event confidence when:
  - At least one EDH record corroborates the event’s participants/date/place. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)

***

## VIAF – people and works disambiguation

**Role**

- Name authority for **persons and works**, especially for later reception and authorship. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)

**How to leverage**

- After QID resolution for a person:
  - Follow P214 (VIAF) to retrieve canonical name forms and linked national authority records. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)
  - Use:
    - As **identity confirmation** for major figures (Cicero, Caesar, etc.).  
    - To separate Person vs. Author vs. Subject roles through work lists. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)
- Treat:
  - “Only in Wikidata, not in VIAF/Trismegistos” as **textual/unconfirmed**.  
  - “In VIAF + Trismegistos + PIR” as **strongly attested historical person**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)

***

## GeoNames / OpenStreetMap – modern coordinates

**Role**

- Modern geographic ground truth for visualization and rough spatial indexing. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)

**How to leverage**

- Given a Pleiades place or ancient location:
  - Follow its federation links to GeoNames / OSM. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)
  - Pull:
    - Precise modern coordinates, admin units, bounding boxes. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
- Use:
  - Only for **UI maps and modern context**, never as primary historical geography; your ontology remains Pleiades/DARE/PeriodO‑driven. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/e258096f-73f6-40e1-9e05-1bf4f8112484/2-12-26-federations.md)

***

## PeriodO – periods semantics

**Role**

- Authority for **named historical periods** and their temporal intervals. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/e258096f-73f6-40e1-9e05-1bf4f8112484/2-12-26-federations.md)

**How to leverage**

- For labels like “Late Republic,” “Augustan Age”:
  - Resolve to PeriodO IDs with explicit start–end bounds. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
  - Attach Period nodes to:
    - Events (envelope).  
    - Persons (active period).  
    - Places (valid period).
- Use:
  - To check **temporal plausibility** (no Event outside its named period).  
  - To support period‑based “lensing” (show only Late Republic events). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/e258096f-73f6-40e1-9e05-1bf4f8112484/2-12-26-federations.md)

***

## Getty AAT + LCSH/FAST – concepts and institutions

**Role**

- **Getty AAT:** deep hierarchy for abstract concepts, objects, and institutions. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
- **LCSH/FAST:** library‑grade topic hierarchies, already core to your Subject backbone. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b10de236-be04-49aa-8e2d-c697638a64ac/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

**How to leverage**

- For `Concept`, `Institution`, `LegalRestriction`, `Organization`, `Subject` nodes: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b10de236-be04-49aa-8e2d-c697638a64ac/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
  - Assign:
    - AAT ID for ontological concept type (e.g., “colony,” “tax,” “senate”).  
    - LCSH/FAST subject headings for bibliographic crosswalk. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/e258096f-73f6-40e1-9e05-1bf4f8112484/2-12-26-federations.md)
- Use:
  - For **facet queries** (“all events involving colonial institutions”).  
  - As a **concept spine** for SFAs building discipline ontologies.

***

## Overall pattern: stacked evidence ladder

From `FederationUsage.txt` and `2-12-26-federations.md` you already have the key pattern: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/e258096f-73f6-40e1-9e05-1bf4f8112484/2-12-26-federations.md)

- Start with **Wikidata (broad identity hint)** →  
- Follow to **domain authorities**:
  - Places: Pleiades → Trismegistos Geo → DARE → GeoNames/OSM.  
  - People: VIAF → Trismegistos People → PIR/PLRE → LGPN, DDbDP.  
  - Events: Wikidata event → Trismegistos Texts, EDH → law corpora, etc. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/70a78c9c-f188-4df3-b38d-bc0a592b4f8c/FederationsPartial.md)
- Use depth down this chain as:
  - **Confidence score input** in your Claim. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)
  - UI “federation badge” to show how well‑supported a node/event is. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cab0e78a-8943-4cca-a92d-282771444bc6/FederationUsage.txt)

Chrystallum’s job is to push each candidate node as far down this ladder as is feasible, then treat that depth as epistemic weight in validation and lensing. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/e258096f-73f6-40e1-9e05-1bf4f8112484/2-12-26-federations.md)