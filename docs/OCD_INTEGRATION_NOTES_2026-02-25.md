# OCD Integration — Design Notes and Open Issues

**Date:** 2026-02-25 (recovered from main chat, Feb 24 session)
**Source:** https://archive.org/details/in.ernet.dli.2015.461705
**Status:** Design agreed; extraction script drafted; Wikidata mapping queries identified but not yet run.

---

## What the OCD Is (for Chrystallum)

Oxford Classical Dictionary, 1949 edition. Editors: Cary (primary), Denniston (Greek linguistics), Nock (religion/mystery cults), Ross (philosophy). 988 pages, ~3,500–4,500 entries. Public domain. ABBYY FineReader OCR at 600 PPI — high quality.

**Four roles in Chrystallum:**

1. **Reference source for agents** — canonical authority that changes SFA confidence posture. An SFA grounding a claim against an OCD entry can say "Wikidata asserts X, OCD 1949 asserts Y, they diverge on Z." Grounded reasoning, not parametric recall.

2. **Taxonomy enrichment** — OCD entry structure encodes decades of scholarly consensus about conceptual organization. Legal concepts (provocatio, lex, intercessio, imperium), religious institutions (flamines, Vestals, Lupercalia), material culture (toga praetexta, fasces, corona triumphalis) — all SubjectConcept candidates with BROADER_THAN hierarchy built in.

3. **Cross-reference graph** — every (q.v.) is a directed edge in a scholar-curated knowledge graph. OCD's cross-reference structure is a salience signal: the connections the 1949 editors considered essential for understanding an entity.

4. **Browser extension anchor** — OCD → Wikipedia → Wikidata QID → Chrystallum node. The authority chain that makes the extension useful: user reads Wikipedia on Sulla, extension resolves to Wikidata QID, Chrystallum node links back to OCD entry as source.

---

## OCR Quality Assessment (from sample)

**Entry delimiter:** `}` after headword — e.g. `ABDERA}`, `ABACUS}`. Reliable and consistent. Entry segmentation is straightforward.

**Cross-references:** Appear as `(q.v.)` — machine-readable. Every `(q.v.)` is an extractable edge. Example: ABARIS cross-references ARISTEAS and HYPERBOREAN.

**Author attribution:** Initials at end of each entry — W. D. R. (Ross), W. K. C. G. (Guthrie), M. C. (Cary), H. J. R. (Rose), G. C. F. (Field). Editor attribution is metadata on the bibliography node — entries on religious topics carry Nock's authority, Greek linguistics carry Denniston's.

**Greek characters:** Transliterated cleanly — no garbled sequences.

**Noise:** Abbreviations section at front before entries begin. `ABACUS}` marks start of dictionary content.

---

## Extraction Pipeline (First Pass Script)

```python
import re

def parse_ocd_entries(text):
    pattern = r'([A-Z][A-Z\s,]+})'
    parts = re.split(pattern, text)

    entries = []
    for i in range(1, len(parts), 2):
        headword = parts[i].replace('}', '').strip()
        body = parts[i+1].strip() if i+1 < len(parts) else ''

        # Extract cross-references — term immediately before (q.v.)
        xref_terms = re.findall(r'(\w[\w\s]+?)\s*\(q\.v\.\)', body)

        # Extract author initials (last token pattern X. X. X.)
        author = re.search(r'([A-Z]\.\s*){2,}$', body.strip())

        entries.append({
            'headword': headword,
            'body': body,
            'cross_references': xref_terms,
            'author_initials': author.group(0).strip() if author else None
        })

    return entries
```

**Known limitations to address in v2:**
- Multi-word headwords need tuning
- Entries spanning page breaks
- Author initials regex needs validation against known editor list

**Full text URL:** https://archive.org/download/in.ernet.dli.2015.461705/2015.461705.The-Oxford_djvu.txt

---

## Wikidata Mapping Strategy

### Path 1 — P9106 (OCD online ID)
Explicit OCD-to-entity mapping. 4th edition online identifier.

```sparql
SELECT ?item ?itemLabel ?ocdId WHERE {
  ?item wdt:P9106 ?ocdId .
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
  }
}
LIMIT 1000
```

### Path 2 — P1343 with Q430486 (described by source)

```sparql
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P1343 wd:Q430486 .
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en".
  }
}
```

**Run both at:** https://query.wikidata.org — **neither query has been run yet.**

---

## Key QIDs

- `Q430486` — Oxford Classical Dictionary (general work / 1949 anchor)
- `Q20078571` — OCD 3rd revised edition (1996)
- `Q69525831` — OCD 4th revised edition (online)
- `P9106` — "Oxford Classical Dictionary ID" (4th edition online)
- `P1343` — "described by source"

**Note:** P9106 is 4th edition, not 1949. Mapping strategy: use P9106 to confirm OCD coverage, match to 1949 headword by label normalization.

---

## Epistemic Limitations (document on bibliography node)

- 1949 edition predates significant epigraphic discoveries
- Predates systematic prosopography as a method (LGPN, PIR post-date it)
- Metadata properties to set: `authority_scope`, `superseded_by` (Q69525831), `date_limitations`
- Epistemic stance: one taxonomy signal and scholarly salience source — not privileged over domain authorities (DPRR, Pleiades, Trismegistos, LGPN) or later scholarship

---

## Immediate Outputs (before SFA layer is ready)

1. **Headword list** — cross-reference against 45 current SubjectConcepts and ~6,000 entities → surfaces taxonomy gaps
2. **Cross-reference edge list** — every (q.v.) pair as directed edges
3. **Wikidata seed mapping** — run P9106 and P1343 queries, merge with headword list

---

## Open Issues / Next Actions

| Item | Status | Notes |
|------|--------|-------|
| Download full text | **Pending** | Archive.org URL above |
| Run P9106 SPARQL query | **Pending** | query.wikidata.org |
| Run P1343/Q430486 query | **Pending** | Softer bibliographic links |
| Run entry segmentation script | **Pending** | Produce headword list + cross-ref edge list |
| SubjectConcept gap analysis | **Pending** | Requires headword list first |
| OCD bibliography node in graph | **Pending** | `MERGE (:BibliographySource {title: "Oxford Classical Dictionary", edition: "1st", year: 1949, qid: "Q430486"})` |

---

## Taxonomy Gaps OCD Will Fill (Known)

- **Legal concepts:** provocatio, lex, senatus consultum, intercessio, imperium
- **Religious institutions:** flamines, Vestals, Lupercalia, specific cults and priesthoods
- **Material culture / status markers:** toga praetexta, fasces, corona triumphalis, lituus — missing SIGNIFIES relationship to status/office

---

## Relationship to Other Docs

| This doc | Other doc | Relationship |
|----------|-----------|--------------|
| OCD as bibliography node | `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN_2026-02-25.md` | BibliographyRegistry branch is where OCD node lives |
| P9106/P1343 mapping | `AI_CONTEXT.md` Pipeline Contract | P1343 canonicalization already run (3,226 edges) |
| Taxonomy gaps | `KANBAN.md` OCD Parsing and Alignment (Ready) | KANBAN item exists; this doc gives it detail |
