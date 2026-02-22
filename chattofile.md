
Yes. Here’s a consolidated, detail‑preserving snapshot of everything we’ve built up since that “BRILLIANT observation” message, organized around how SCA/SFAs, federations, and claims all interlock.

***

## 1. SCA + SFA: Upward trawling and meta-layers

- For any concrete subject (e.g., economic history, Roman Republic), SCA **trawls up** each authority’s hierarchy (Wikidata `subclass of`/`part of`, FAST `skos:broader`, ANZSRC Field→Group→Division, LCSH broader terms). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
- It **materializes** not only the leaf SubjectConcept but also intermediate nodes that:
  - Have strong authority IDs (LCSH, FAST, ANZSRC, Dewey, Wikidata, etc.).  
  - Represent **disciplinary or super‑disciplinary concepts** (History, Economics, Social science, etc.). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
- These promoted nodes become:
  - **Topic Spine** anchors and discipline roots (`discipline = true`).  
  - Routing anchors for agent domains and facet assignment. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

Result: SCA can see the **full ontological context** from leaf up through discipline/meta‑discipline and use that to drive SFA initialization, routing, and claim evaluation.

***

## 2. Multi‑authority model and added sources

Your SubjectConcept authority stack now explicitly includes: [ijcai](https://www.ijcai.org/proceedings/2021/0620.pdf)

- **Tier 1 (preferred):**
  - LCSH (authority_id)  
  - FAST (fast_id)
- **Tier 2 (secondary):**
  - LCC (lcc_class, lcc_subclass)  
  - CIP (cip_code)  
  - **ANZSRC FoR** (e.g., 380103 Economic history, 38 ECONOMICS Division – now explicitly added).
- **Tier 3 (tertiary):**
  - Wikidata QID (qid)  
  - Dewey, VIAF, GND, etc.

Additional alignment layers we discussed:

- **BabelNet**: `babelnet_id` on SubjectConcept:
  - Multilingual, sense-level labels and glosses.  
  - Sense‑aware semantic relations (hypernyms/related).  
  - Acts as a **lexical bridge** across languages for SFAs and query parsing. [w3](https://www.w3.org/community/bpmlod/wiki/Converting_BabelNet_as_Linguistic_Linked_Data)
- **Domain vocabularies:**
  - **Getty AAT** (`aat_id`): art, architecture, material culture, techniques, periods; SKOS hierarchy and microthesauri. [getty](https://www.getty.edu/research/tools/vocabularies/lod/index.html)
  - **MeSH** (`mesh_id`): biomedical topics, tree numbers, qualifiers (e.g., `/history`, `/economics` → facet hints). [id.nlm.nih](https://id.nlm.nih.gov/mesh/)
  - Other thesauri (PSH, AGROVOC, etc.) via `external_vocab_ids` plus crosswalks (e.g., LCSH↔MeSH projects). [galter.northwestern](https://galter.northwestern.edu/about-us/northwestern-university-libraries-lcsh-mesh-mapping-project)

All of these enrich SubjectConcepts and help SFAs get **discipline‑ and facet‑specific vocabularies**.

***

## 3. Time and space: PeriodO + Pleiades + TGN

You now have a clean **time–space–subject** triple for Roman Republic and similar domains:

- **PeriodO in Neo4j**: [perio](https://perio.do)
  - Multiple scholarly **period definitions** (PeriodO URIs) for “Roman Republic”:
    - Each with temporal bounds (with uncertainty) and spatial coverage.  
    - Each with explicit scholarly provenance (work/author).
  - Pattern in Neo4j:
    - `(:PeriodDefinition {periodo_id, ...})-[:DEFINES_PERIOD]->(:Period)`  
    - `(:PeriodDefinition)-[:HAS_TEMPORAL_EXTENT]->(:TemporalExtent)`  
    - `(:PeriodDefinition)-[:HAS_SPATIAL_COVERAGE]->(:Place)`  
    - `(:SubjectConcept)-[:ABOUT_PERIOD]->(:Period)` [peerj](https://peerj.com/articles/cs-44.pdf)
- **Pleiades** gazetteer: [github](https://github.com/isawnyu/pleiades.datasets)
  - Places and regions with ancient/modern names, coordinates, time attestations.  
  - Concordances to GeoNames, TGN, etc. [lod-cloud](https://lod-cloud.net/dataset/pleiades)
  - Used via `pleiades_id` on Place / Region nodes and linked from PeriodO coverage.

- **TGN** (via Getty service you already consume): [groups.google](https://groups.google.com/g/dspace-tech/c/u42DAtdJJjQ)
  - Hierarchical place authority, used alongside Pleiades for broader geographic authority.

Net result for Roman Republic: for each period definition you can say **“this definition, with these dates, covering these Pleiades/TGN regions, and these SubjectConcepts talk about it”**. [journals.ub.uni-heidelberg](https://journals.ub.uni-heidelberg.de/index.php/dco/article/download/104105/102505/274362)

***

## 4. Getty AAT specifics (beyond TGN)

AAT gives you SKOS‑based, LOD‑published **concept trees** for what/which kinds of things, complementing TGN’s where: [getty](https://www.getty.edu/research/tools/vocabularies/microthesauri_zeng.pdf)

- **Concept content:**
  - `skos:prefLabel` + `skos:altLabel` in multiple languages.  
  - `skos:broader` / `skos:narrower` / `skos:related`.  
  - Membership in **facets/microthesauri** such as “Objects”, “Styles and periods”, “Materials”, “Techniques”. [metadataetc](https://metadataetc.org/LOD/6hands-on-Microthesauri-from-AAT.pdf)

- **Use in Chrystallum:**
  - `aat_id` on SubjectConcepts and relevant entities (MaterialObject, Structure).  
  - Import selected microthesauri (e.g., Roman architecture, pigments) as SubjectConcept hierarchies with:
    - `BROADER_THAN` mirroring AAT broader.  
    - Facet hints:
      - Styles/periods → CULTURAL/ARCHAEOLOGICAL.  
      - Materials/techniques → TECHNOLOGICAL/ARCHAEOLOGICAL. [zenodo](https://zenodo.org/records/15487726/files/Report-2025-D05-Getty%20AAT%20in%20SSH%20DS.pdf?download=1)
  - SFAs (ARCHAEOLOGICAL, ARTISTIC, CULTURAL, TECHNOLOGICAL) use these as **domain taxonomies** when building their ontologies and validating claims.

This means for Roman Republican material culture you have **authoritative vocabularies** for building types, artifacts, materials, and styles, not just ad‑hoc labels. [isprs-archives.copernicus](https://isprs-archives.copernicus.org/articles/XLII-2-W11/3/2019/isprs-archives-XLII-2-W11-3-2019.pdf)

***

## 5. SCA/SFA workflow towards “learning mode with texts”

From the consolidated architecture, the agent workflow is now: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

1. **Phase 1 – Initialize Mode (SCA)**  
   - `executeinitializemode(anchor_qid=Q17167 "Roman Republic", depth=...)`  
   - Uses Wikidata federation (`bootstrapfromqid`, `discoverhierarchyfromentity`) plus authority mappings to build **scaffold SubjectConcepts** with QIDs, LCSH/FAST/etc., PeriodO/pleiades where applicable. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

2. **Phase 2 – Subject Ontology Proposal (SCA, unfaceted)**  
   - `proposesubjectontology()`:
     - Analyzes P31/P279/P361, plus authority hierarchies.  
     - Identifies conceptual clusters and candidate classes (e.g., Senate, consulship, dictatorship).  
     - Proposes relationships and validation rules. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
   - Your new **meta-layer promotion rule** ensures discipline/meta‑discipline nodes (History, Social science, etc.) with authority IDs are **kept as canonical SubjectConcepts**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

3. **Phase 3 – Discipline root detection & marking**  
   - `detectandmarkdisciplineroots(discovered_nodes, facet)` finds nodes with high BROADER_THAN reachability or facet‑specific heuristics and sets `discipline = true`, `disciplinetrainingseed = true`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

4. **Phase 4 – Training Mode (per SFA)**  
   - `executetrainingmode(maxiterations, targetclaims, minconfidence, ...)`:
     - Loads session context, prioritized SubjectConcepts under roots.  
     - For each node with a Wikidata QID:
       - `fetchwikidataentity` → validate completeness → `generateclaimsfromwikidata`.  
       - Auto‑enrich claims with CRMinf and CIDOC mappings. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
     - Produces abstract, discipline‑level claims (e.g., “Legion composed of cohorts and maniples”), accepted as‑is without cross‑facet routing. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

5. **Phase 5 – Operational mode (selective multi‑facet collaboration)**  
   - When SFAs create **concrete** claims (events, specific persons, dated facts), SCA:
     - Scores multi‑facet relevance.  
     - Queues only to relevant SFAs.  
     - Aggregates FacetPerspectives around a **single content‑only cipher Claim**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

6. **Links to texts (for full “learning from text”)**  
   - Already specified: `(:Work)-[:ABOUT]->(:SubjectConcept)` as aboutness links. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
   - Planned: **Wikipedia Training Mode** to discover articles and extract line‑by‑line claims, validating via your registry and feeding the same claim/CRMinf pipeline. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
   - Once `Work-ABOUT-SubjectConcept` edges are populated (for Roman Republic, etc.), SFAs in Training Mode can:
     - Use Wikidata + federations for structured facts.  
     - Use Wikipedia/other texts for **claim extraction**, grounded in the same SubjectConcepts and federated IDs.

***

## 6. Claims, ciphers, and CRMinf

Your claims layer is consistent and fully wired to support this:

- **Content‑only claim cipher (ADR‑001)**: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
  - Includes: source work ID, passage hash, subject entity, object entity, relationship type, temporal data, facetid (for facet‑aware assertions).  
  - Excludes: confidence, agent, timestamp, and other provenance.  
  - Ensures:
    - Automatic **deduplication** when multiple agents extract the same assertion.  
    - Stable IDs for cryptographic verification across institutions.  
    - Provenance stored in `FacetPerspective` nodes (agent, time, rationale, confidence). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

- **CRMinf alignment**: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)
  - Claims → I2Belief (via Claim node), with J4that (claim label), J5holdstobe (confidence).  
  - Enables multi‑agent argumentation, belief adoption, and inference tracking using CRMinf semantics. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

- **ProposedEdge nodes** for canonical relationship materialization (Claim→ProposedEdge→entities) and promotion from scaffold to canonical graph edges. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

Thus, when SFAs “learn” from federated data + texts, they always emit **deduplicated, CIDOC/CRMinf‑aligned claims** with rich provenance, rather than loose triples.

***

## 7. Roman Republic “all federations” picture

For Roman Republic specifically, once wired:

- **Subject layer**:
  - SubjectConcept(s) for Roman Republic history, politics, military, economy:
    - LCSH/FAST/LCC/CIP/ANZSRC/Wikidata/BabelNet IDs.  
    - AAT IDs for styles/periods and built environment where relevant. [ijcai](https://www.ijcai.org/proceedings/2021/0620.pdf)

- **Time & space**:
  - PeriodO period definitions linked to Period and to spatial coverage regions.  
  - Pleiades/TGN/GeoNames for places; coverage regions tied to those gazetteers. [zenodo](https://zenodo.org/records/15540082)

- **Domain vocabularies**:
  - AAT object/style/material hierarchies for Roman architecture and artifacts.  
  - MeSH etc. for history of medicine in the Republic when needed. [getty](https://www.getty.edu/research/tools/vocabularies/lod/index.html)

- **Agents**:
  - SCA as concierge over this spine, SFAs per facet operating in Training Mode and Operational Mode, with Wikidata + domain vocabularies + PeriodO/Pleiades as their **federated evidence graph**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/2ba00010-fe4e-4f6a-a9db-825cb6f8b619/2-12-26-Chrystallum-Architecture-CONSOLIDATED.md)

That’s the consolidated, still‑detailed picture you’ve built up since that first “ontological goldmine” remark.