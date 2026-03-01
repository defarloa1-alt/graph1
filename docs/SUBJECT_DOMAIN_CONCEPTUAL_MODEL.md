# Subject Domain Conceptual Model

**Date:** February 2026  
**Status:** Conceptual — integrates LCC, LCSH, facets, holistic mapping, and recent design decisions

---

## 1. Subject Domain Authorities

Seven systems participate in the subject domain. They interconnect; no single system is complete alone.

```
                    Wikidata (hub)
                    P244, P1149, P2163, P1036, sitelinks
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
      LCSH            LCC             FAST
    (headings)    (classification)  (faceted)
         │               │               │
         └───────────────┼───────────────┘
                         │
                    MARC record
                         │
                         ▼
                    WorldCat
                  (500M+ records)
                         │
                         ▼
                   Wikipedia
              (articles, scope notes)
```

| System | Role | Wikidata link | Notes |
|--------|------|---------------|-------|
| **LCC** | Shelf location, hierarchy | P1149 | DG241-269, KJA190-2152 |
| **LCSH** | Topical headings | P244 | sh85115114, primary backbone |
| **Wikidata** | Hub, entity IDs | — | One query → LCSH, FAST, LCC, Dewey |
| **Wikipedia** | Scope, narrative | Sitelinks | Full articles, related topics |
| **FAST** | Faceted subjects | P2163 | Derived from LCSH |
| **MARC** | Record format | — | Carries LCC, LCSH in catalog records |
| **WorldCat** | Union catalog | — | Real catalog usage, MARC |

---

## 2. Facets (18 canonical)

Research dimensions for routing and characterization. ADR-004.

| Facet | Domain | Examples |
|-------|--------|----------|
| ARCHAEOLOGICAL | Material culture | Archaeology, antiquities, inscriptions |
| ARTISTIC | Arts | Art, sculpture, literature, poetry |
| BIOGRAPHIC | People | Biography, family, prosopography |
| COMMUNICATION | Rhetoric | Oratory, speech, propaganda |
| CULTURAL | Culture | Customs, identity, ideology |
| DEMOGRAPHIC | Population | Census, migration |
| DIPLOMATIC | International | Treaty, embassy, alliance |
| ECONOMIC | Economy | Trade, finance, land |
| ENVIRONMENTAL | Environment | Climate, geography |
| GEOGRAPHIC | Space | Province, territory, expansion |
| INTELLECTUAL | Scholarship | Philosophy, historiography, law |
| LINGUISTIC | Language | Latin, Greek |
| MILITARY | Warfare | Army, navy, battle, legion |
| POLITICAL | Governance | Senate, magistrate, constitution |
| RELIGIOUS | Religion | Cult, ritual, temple |
| SCIENTIFIC | Science | Medicine, astronomy |
| SOCIAL | Society | Patronage, slavery, class |
| TECHNOLOGICAL | Technology | Engineering, construction |

---

## 3. Holistic Context Gathering

**Principle:** Do not map each system in isolation. Gather all available context, then reason once.

### Layer 1: Wikidata (one call)

For concepts with QID, a single Wikidata query returns:

| Property | System | Example |
|----------|--------|---------|
| P244 | LCSH | sh85115114 |
| P2163 | FAST | fst01204885 |
| P1149 | LCC | DG241-269 |
| P1036 | Dewey | 937.04 |
| Sitelinks | Wikipedia | en.wikipedia.org/wiki/Roman_Republic |
| Description | — | "period of ancient Roman civilization" |

### Layer 2: Beyond Wikidata

Wikidata is a hub but not exhaustive. Augment with:

| Source | Adds | When |
|--------|------|------|
| **LoC id.loc.gov** | LCSH scope notes, LCC hierarchy | Need richer metadata |
| **WorldCat** | MARC subjects, catalog usage | Need real-world usage |
| **Wikipedia** | Full article, structure | Need narrative scope |
| **FAST** | Direct headings, hierarchy | When P2163 missing |
| **Pleiades, PeriodO, DPRR** | Domain place/period/person data | Roman Republic context |

### Layer 3: LCC-only concepts

LCC classes (e.g. DG105, KJA190) may lack QIDs. For these:

- Use LCC label + optional Wikipedia search by label
- Use LoC classification API for hierarchy
- Use WorldCat for catalog usage of that LCC range

---

## 4. Primary vs. Secondary

In LCC and related systems, **"Sources"** means primary materials (original texts), not bibliographic citations.

| Label pattern | Material type | Example |
|---------------|---------------|---------|
| Sources, Documents, Inscriptions | Primary | DG31, KJA190-2152 |
| Historiography, Criticism, Commentaries | Secondary | DG35 |
| General works, Handbooks | Secondary | DG21 |

**Persist:** `material_type: "primary" | "secondary" | "both"` on mappings for agent routing and filtering.

---

## 5. Mapping Agent (Specialist)

A dedicated **LCC classification agent** (or broader **subject characterization agent**) that the SCA uses as a tool.

### Input

- Concept identifier (LCC code, QID, LCSH ID, or combination)
- Context bundle (from Layers 1–3)

### Output

- Facets with weights and reasons
- `material_type`
- Discovered links (Wikipedia URL, etc.)

### Design

- **Single call:** One agent call with full context, not sequential per-source
- **LLM:** OpenAI or Perplexity (no keyword heuristics)
- **Batch:** Map many concepts in one or few calls
- **Cache:** Persist results; avoid repeated API calls

---

## 6. Persistence

| Discovery | Where to store |
|-----------|----------------|
| Wikipedia URL | `SubjectConcept.wikipedia_url` or `(:Concept)-[:HAS_WIKIPEDIA]->(:WikipediaArticle)` |
| Wikidata description | `SubjectConcept.wikidata_description` |
| LCC → Facet | `(:LCC_Class)-[:MAPS_TO_FACET {weight, reason}]->(:Facet)` |
| LCSH → Facet | Same pattern for LCSH-backed concepts |
| Material type | `material_type` on node or relationship |
| LCSH, FAST, LCC, Dewey | On SubjectConcept node (from Wikidata or LoC) |

---

## 7. End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  CONCEPT (LCC class, SubjectConcept, QID, or LCSH heading)       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  GATHER CONTEXT                                                  │
│  • Wikidata (if QID): P244, P2163, P1149, P1036, sitelinks      │
│  • LoC: scope notes, hierarchy (if LCSH/LCC)                    │
│  • WorldCat: MARC subjects (optional)                            │
│  • Wikipedia: summary or full article (if sitelink)             │
│  • Domain: Pleiades, PeriodO, DPRR (if relevant)                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  MAPPING AGENT (LLM)                                             │
│  • Input: aggregated context                                    │
│  • Prompt: "What is this about? Which facets?"                  │
│  • Output: facets, weights, material_type, reasoning             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  PERSIST                                                         │
│  • MAPS_TO_FACET edges                                           │
│  • Wikipedia URL, Wikidata description                          │
│  • LCSH, FAST, LCC, Dewey on nodes                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Agent Prompt (Holistic)

### System message

```
You are a subject-domain expert for the Chrystallum knowledge graph. You characterize concepts using context from LCC, LCSH, Wikidata, Wikipedia, FAST, and related sources. Your job is to answer: "What is this about?" and assign research facets. Respond ONLY with valid JSON.
```

### User prompt template

```
## Task
Characterize this concept: assign Chrystallum facets, material type, and note any Wikipedia match.

## Context (aggregated from multiple sources)

**Identifier:** {identifier}  // e.g. DG105, Q17167, sh85115114

**LCC:** {lcc_code}: {lcc_label}
**LCSH:** {lcsh_heading} (ID: {lcsh_id})
**FAST:** {fast_heading} (ID: {fast_id})
**Dewey:** {dewey}
**Wikidata:** {qid} — {wikidata_description}
**Wikipedia:** {wikipedia_url}
{wikipedia_summary}

**Domain context:** Roman Republic (509 BCE – 27 BCE)

## Facets (choose one or more with weight 0.0–1.0)
ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL

## Material type
- "primary" = original texts, laws, inscriptions, source documents
- "secondary" = scholarship, historiography, commentaries
- "both" = mixes primary and secondary
- "unclear" = cannot determine

## Output format
Return ONLY this JSON structure. No other text.

{
  "identifier": "{identifier}",
  "facets": [
    {"facet": "MILITARY", "weight": 0.95, "reason": "Core military organization topic"}
  ],
  "material_type": "secondary",
  "material_reason": "Scholarly works on Roman army, not primary sources",
  "wikipedia_url": "https://en.wikipedia.org/wiki/Roman_army",
  "summary": "One-sentence characterization of what this concept is about"
}
```

### Batch variant (multiple concepts)

```
## Task
Characterize each concept below. Use all provided context. Assign facets, material type, and note Wikipedia matches.

## Concepts (with aggregated context)

### Concept 1
- Identifier: DG105
- LCC: DG105 — Army
- LCSH: Rome—History, Military (sh85115123)
- Wikidata: Q7278 — military force of ancient Rome
- Wikipedia: https://en.wikipedia.org/wiki/Roman_army — "The Roman army was the armed forces deployed by the Romans..."

### Concept 2
- Identifier: KJA190-2152
- LCC: KJA190-2152 — Sources
- LCSH: (none)
- Wikidata: (none)
- Wikipedia: (none)
...

## Facets
ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL

## Output
Return ONLY a JSON array. One object per concept. Include identifier, facets, material_type, material_reason, wikipedia_url (if found), summary.

[
  {"identifier": "DG105", "facets": [{"facet": "MILITARY", "weight": 0.95, "reason": "..."}], "material_type": "secondary", "material_reason": "...", "wikipedia_url": "https://...", "summary": "..."},
  ...
]
```

### Few-shot examples (include in prompt when helpful)

```
Example 1:
- DG105 Army → facets: [MILITARY 0.95], material_type: secondary
- Reason: Military organization; secondary scholarship

Example 2:
- DG31 Sources → facets: [INTELLECTUAL 0.85], material_type: primary
- Reason: Primary historical materials (ancient texts, inscriptions)

Example 3:
- KJA190-2152 Sources → facets: [INTELLECTUAL 0.8], material_type: primary
- Reason: Primary legal materials (laws, edicts, juristic texts)

Example 4:
- DG155 Law (general) → facets: [INTELLECTUAL 0.6, POLITICAL 0.5], material_type: secondary
- Reason: Legal scholarship + institutional governance
```

---

## 9. Summary

| Principle | Implementation |
|-----------|----------------|
| **Wikidata as hub** | One query → LCSH, FAST, LCC, Dewey, Wikipedia |
| **Beyond Wikidata** | LoC, WorldCat, Wikipedia, domain sources |
| **Holistic** | Gather all context before agent call |
| **Single agent** | One call with full context, not sequential per-source |
| **Persist discoveries** | Wikipedia URL, description, mappings |
| **Primary vs secondary** | Distinguish source materials from scholarship |
| **Facets** | 18 research dimensions for routing and characterization |
