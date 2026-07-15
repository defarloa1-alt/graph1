# SFA Constitution — Design Notes

**Date:** 2026-02-25 (recovered from main chat, Feb 24 session)  
**Status:** Architecture settled. KANBAN task needed. No code, no graph touches — preparatory work for SFA implementation sprint.

---

## Architecture Decision: No Methods Agent

**Retired framing:** A standalone Methods Agent that produces a Lens vocabulary.  
**Correct framing:** Each SFA has methodological self-awareness built in as constitution documents. The lens is constitutive of the SFA, not a service it calls.

---

## Three-Layer SFA Model (Confirmed)

Every SFA has three layers of constitutive knowledge:

| Layer | Content | Source |
|-------|---------|--------|
| Layer 1 | Domain data — what the graph contains | DPRR, Pleiades, Wikidata entities, POSITION_HELD/familial edges |
| Layer 2 | Primary sources — what the ancient authors say | Livy, Polybius, Appian, Cicero — retrieved via Perseus citation resolution |
| Layer 3 | Methodological stance — how to reason about Layers 1 and 2 | SFA-specific constitution documents |

**F001–F005 schema nodes** are the graph representation of each SFA's Layer 3 stance. They are not outputs of a Methods Agent.

---

## SFA Constitution Documents (by SFA)

### Universal base (Layer 3 for all SFAs)
- **How History Is Made** (Open Textbook Library) — source criticism, historical reasoning fundamentals, quantitative and digital methods. Open access PDF. Download and store as bibliography node.

### Prosopographer SFA
- Metahistory Roman Historiography — what prosopography is as a method
- DPRR technical documentation — structured prosopography computationally
- Syme index (pages 535–568) — prosopographic salience in practice
- Relevant sections of How History Is Made on biography and collective history

### Economic Historian SFA
- OxRep methodology documentation
- How History Is Made — quantitative and economic methods sections
- Finley, Politics in the Ancient World — ancient economy debates
- Weber, Agrarian Sociology of Ancient Civilizations (in reading list)

### Military Historian SFA
- Fuller, Julius Caesar methodology
- Goldsworthy and Delbrück on ancient warfare
- How History Is Made — military history as a discipline sections

### Legal/Institutional SFA
- Raaflaub, Social Struggles in Archaic Rome — Conflict of the Orders
- Gargola, Shape of the Roman Order — Roman institutional spaces
- Roman law methodology sources

### Literary/Source Critic SFA
- Metahistory Roman Historiography — annalistic vs monographic traditions, reliability problem with Livy, narrative construction in Tacitus
- Rüpke on narrative construction in Roman sources (Fasti Sacerdotum + historiography work)
- How History Is Made — source criticism sections

---

## Open Access Resources to Download Now

| Resource | URL | Purpose |
|----------|-----|---------|
| How History Is Made | Open Textbook Library | Universal Layer 3 base |
| Metahistory Roman Historiography | UNM digital project | Literary/source critic SFA + universal vocabulary on why sources disagree |
| Wikipedia Roman Historiography | Wikipedia | High-level map of ancient historiographical forms |
| AHA Digital History Resources | AHA hub | Digital methods vocabulary (GIS, network analysis, text mining) |

**Metahistory Roman Historiography is worth fetching immediately** — open access, short, gives the vocabulary for reasoning about source disagreement (not just detecting it). Relevant to every SFA.

---

## Reading List as SFA Constitution Library

The reading list (~4,000 entries, 396 Roman-relevant, 32 Tier 1–2 index candidates) reframed:

**These books are Layer 3 source material, not just personal reading:**

| Book | SFA | Layer 3 role |
|------|-----|-------------|
| Syme, Roman Revolution | Prosopographer | Primary constitution document |
| Weber, Agrarian Sociology | Economic Historian | Economic lens constitution |
| Finley, Politics in the Ancient World | Economic Historian | Ancient economy debates |
| Fuller, Julius Caesar | Military Historian | Military methodology |
| Goldsworthy / Delbrück | Military Historian | Ancient warfare analysis |
| Raaflaub, Social Struggles | Legal/Institutional | Conflict of the Orders |
| Gargola, Shape of the Roman Order | Legal/Institutional | Institutional spaces |
| Rüpke, Fasti Sacerdotum | Prosopographer + Literary | Priesthood data + narrative construction |

Index photography sessions serve dual purpose: Chrystallum prosopographic data AND SFA constitution material.

---

## Syme Index Extraction Plan

**Source:** Syme, Roman Revolution (1939). Index pages 535–568 (34 pages).  
**Copyright note:** Prose text is in copyright (UK, life+70, until 2059). Index extraction = facts extraction (names, dates, page refs, short relationship phrases) — different copyright character than prose reproduction. Document this distinction explicitly.

### Why Syme's Index Is High Value

- Disambiguation format: `Nomen Cognomen, Praenomen (cos. YEAR B.C.)` — maps directly to DPRR PostAssertion format
- Sub-entries are pre-parsed relationship candidates: `in alliance with Antonius, 109` → ALLIED_WITH claim with page citation
- Salience signal: entry density reflects Syme's editorial judgment about who matters. Multiple sub-entries = high-salience node for late Republic narrative. Maps to serious reader persona salience weights.
- Alignment path: Syme consular date → DPRR PostAssertion → DPRR person URI → Wikidata QID

### Output Format Per Entry

```json
{
  "headword": "Aemilius Lepidus, M.",
  "disambiguator": "cos. 46 B.C.",
  "page_refs": [69, 94, 96, 97],
  "sub_entries": [
    {"topic": "in alliance with Antonius", "pages": [109]},
    {"topic": "his provinces", "pages": [110]},
    {"topic": "proscribes his brother", "pages": [192]},
    {"topic": "remains pontifex maximus", "pages": [447]}
  ],
  "source": "Syme_Roman_Revolution_1939"
}
```

### Photography Protocol

- Flat pages critical — press spine firmly or use book weight
- Straight on, no angle, even lighting, no shadows
- Resolution high enough for smallest text (page numbers, italic `cos.` abbreviations)
- Both columns fully in frame with margin
- Upload in batches of 4–6 pages; Claude extracts JSON per batch

### Parsing Challenges

- Two-column layout — OCR reads left-to-right across full width, mangles columns. Need column separation (image regions or OCR split detection)
- Entry boundaries: new entry starts with capitalized surname at left margin; continuation lines indented/wrapped
- Sub-entry parsing: semicolons separate sub-entries; page numbers at end; text before page numbers = relationship/topic label
- Disambiguator extraction: `(cos. YEAR B.C.)`, `(cos. suff.)`, `(cos. A.D. X)`, cases with no office

### Status

**Not started.** Book is physically available. Ready to begin photography session when scheduled.

---

## Index Tier List (from reading list analysis)

### Tier 1 — Photograph first
| Book | Pages | Value |
|------|-------|-------|
| Syme, Roman Revolution | 535–568 (34pp) | Gold standard — late Republic prosopographic salience |
| Astin, Scipio Aemilianus | ~8–10pp est. | Mid-Republican period (185–129 BC), deep single-figure network |
| Scullard, History of the Roman World 753–146 BC | est. 10–15pp | Early and middle Republic systematic coverage |
| Greenidge, History of Rome During the Later Republic | est. 10–15pp | 133–44 BC, 1904 scholarly, high entity density |
| Oman, Seven Roman Statesmen | est. 8–10pp | Gracchi, Sulla, Crassus, Cato, Pompey, Caesar networks |
| Raaflaub, Social Struggles in Archaic Rome | est. 8pp | Conflict of the Orders, early Republic institutional entities |

### Tier 2 — After Tier 1
- Meier, Caesar
- Forsythe, Critical History of Early Rome
- Sampson, Rome Blood and Politics + Crisis of Rome
- Gargola, Shape of the Roman Order

Together Tier 1 covers the entire Republican period: Conflict of the Orders → mid-Republic → late Republic → Augustus.

---

## KANBAN Task

**Add:** "SFA Constitution Documents" — parallel background work alongside Project Mercury.
- No graph touches, no code
- Identify and download open access texts (How History Is Made, Metahistory, AHA resources)
- Note bibliography references for physical books
- Schedule Syme index photography session
- Assign downloaded texts to SFA constitution profiles

---

## Relationship to Other Docs

| This doc | Other doc | Relationship |
|----------|-----------|--------------|
| Layer 3 constitution | `docs/OCD_INTEGRATION_NOTES_2026-02-25.md` | OCD is Layer 3 source material for multiple SFAs |
| F001–F005 nodes | `AI_CONTEXT.md` Schema section | F-nodes are graph representation of these stances |
| Reading list | `Reading List - 2025-04-23 09-30.csv` | Source for Tier 1–2 index candidates |
| Syme alignment path | `Federation/CHRYSTALLUM_HANDOFF.md` (legacy) | DPRR PostAssertion format documented there |
