
**Current federations**

1. **Subject Authority Federation (most mature)**  
    LCC/LCSH/FAST/Wikidata are being stitched into one subject spine for routing and classification.  
    Evidence: Python/lcsh/scripts, Python/fast/scripts, [query_lcsh_enriched.tsv](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "Subjects/query_lcsh_enriched.tsv"), [LCC_AGENT_ROUTING.md](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "md/Architecture/LCC_AGENT_ROUTING.md").
    
2. **Temporal Federation (strong)**  
    Year backbone + curated periods + PeriodO alignment + period classification tiers.  
    Evidence: [time_periods.csv](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "Temporal/time_periods.csv"), [periodo-dataset.csv](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "Temporal/periodo-dataset.csv"), scripts/backbone/temporal.
    
3. **Facet Federation (strong conceptual, moderate automation)**  
    Shared facet registry used across subject and temporal layers.  
    Evidence: [facet_registry_master.json](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "Facets/facet_registry_master.json"), [period_facet_tagger.py](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "Facets/Scripts/period_facet_tagger.py").
    
4. **Relationship Semantics Federation (in progress)**  
    Canonical relationship vocabulary aligned to standards (CIDOC/CRMinf and Wikidata mappings).  
    Evidence: [action_structure_vocabularies.csv](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "CSV/action_structure_vocabularies.csv"), [action_structure_wikidata_mapping.csv](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "CSV/action_structure_wikidata_mapping.csv"), architecture draft relationship sections.
    
5. **Geographic Federation (early/transition)**  
    You have a geographic registry and large authority extracts, but this area is still stabilizing due source-selection issues (Getty language vs place pull).  
    Evidence: [geographic_registry_master.csv](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "Geographic/geographic_registry_master.csv"), [*.out](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "Geographic/*.out").
    
6. **Agent/Claims Federation (architecturally defined, partially implemented)**  
    Strong model exists (specialist agents, reviews, synthesis), but less script-level operationalization than subject/temporal pipelines.  
    Evidence: [2-12-26 Chrystallum Architecture - DRAFT.md](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/defar/.vscode/extensions/openai.chatgpt-0.4.73-win32-x64/webview/# "Key Files/2-12-26 Chrystallum Architecture - DRAFT.md").
    

**Potential federations (next logical moves)**

1. **Evidence Federation**  
    Unify source docs/passages/citations into first-class nodes linked to claims/reviews.
    
2. **Identity Federation**  
    Crosswalk people/places/events across VIAF, GND, Wikidata, LoC identifiers (not just subjects).
    
3. **Authority Conflict Federation**  
    Formal conflict-resolution layer when LCSH/FAST/Wikidata/PeriodO disagree, with stored adjudication rules.
    
4. **Geo-Temporal Federation**  
    Joint layer for place-time validity (historical boundaries/names per period), not just separate place and period links.
    
5. **Agent Capability Federation**  
    Explicit machine-readable mapping from agent scope -> LCC ranges/facets/periods for deterministic routing and coverage audits.
Exactly. If we frame federation as “external systems reachable via Wikidata + their own outbound links,” your strongest model is:

**Wikidata as federation broker, not final authority.**

**Practical external federation map**
1. **Subject/Classifications**
- Wikidata -> LCSH/LCC/FAST/Dewey (you already use this heavily).
- Then branch out to LoC/FAST authority endpoints for richer hierarchy, notes, and variants.

2. **Geographic**
- Wikidata -> Getty TGN / GeoNames / Pleiades / Wikipedia.
- Then exploit each provider’s own hierarchy, alternates, and coordinates for place identity over time.

3. **Temporal/Period**
- Wikidata + PeriodO alignments -> period definitions, scope, and temporal boundaries.
- Then use PeriodO and your year backbone for normalization and conflict checks.

4. **Identity/Authority (people, orgs, works)**
- Wikidata -> VIAF / GND / BnF / ISNI / other national authority IDs.
- Then pull canonical labels and cross-authority reconciliation from those systems.

5. **Evidence/Bibliographic**
- Wikidata -> WorldCat/DOI/Crossref/OpenAlex/OpenLibrary links (where present).
- Then resolve to source records for citations and claim provenance.

**How to exploit this well**
1. Store a first-class `authority_links` map on Subject/Place/Period/Entity nodes (not just one ID).
2. Treat Wikidata as discovery and routing; treat domain authorities as canonical for their specialty.
3. Add federation edges like `ALIGNED_WITH`, `SAME_AS`, `DERIVED_FROM`, `CONFLICTS_WITH`.
4. Persist `source`, `retrieved_at`, `confidence`, and `resolution_rule` for every imported assertion.
5. Build “two-hop enrichment”: `QID -> external ID -> provider graph`.

This gives you a true multi-hop federation network rather than a single-hop Wikidata dependency.