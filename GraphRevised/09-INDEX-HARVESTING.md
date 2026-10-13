# Machine-Readable Index Harvesting

> **Note (2026-10-13).** Still deferred (E5). Where this document routes passages to
> subject facet agents, read enrichers by kind and facets as lenses
> ([25](25-LIVES-AND-PLAYGROUND.md) §11-12).

## 1. Purpose

A machine-readable scholarly index can be a high-value source-ingestion
artifact for Chrystallum. It is a human-curated map from concepts to
substantive passages, not merely a keyword list.

The index can preserve preferred and alternate terms, main entries and
subentries, people, places, events, objects, works, `see` and `see also`
references, page or section locators, locator ranges, repeated locators,
and scope notes.

The index is authoritative about how that edition was organized by its
indexer. It is not automatically authoritative about the truth of claims in
the book.

## 2. Harvest sequence

```text
Machine-readable book and index
        ↓
Deterministic index parsing
        ↓
Preserve index structure as source artifacts
        ↓
Resolve locators to passages
        ↓
Create SourceObservations
        ↓
Extract candidate entities and claims
        ↓
SFA proposes normalized claims
        ↓
SCA reconciles and decides
        ↓
Commit service persists accepted changes
```

The index should ordinarily guide where and why harvesting begins. Full-text
search and entity recognition enrich indexed regions; they do not replace the
indexer's structure when a trustworthy machine-readable index exists.

## 3. Preserve the index before interpreting it

An index entry must first be preserved as a source-specific artifact:

```text
Book
  ── HAS_INDEX ──> Index

Index
  ── HAS_ENTRY ──> IndexEntry

IndexEntry
  ├── INDEX_TERM ──> "purple dye"
  ├── HAS_SUBENTRY ──> "production"
  ├── HAS_LOCATOR ──> pages 142–147
  ├── SEE ──> "Tyrian purple"
  └── SEE_ALSO ──> "textiles; status; trade"
```

Only afterward should interpretive mappings be proposed:

```text
IndexEntry
  ├── CANDIDATE_MATCH ──> SubjectConcept
  ├── MENTIONS_ENTITY ──> Entity
  └── LOCATES_DISCUSSION_OF ──> Passage
```

This preserves the distinction between:

```text
Index entry
  What this publication's indexer considered important

SubjectConcept
  Chrystallum's reusable organization of knowledge

Entity
  The historical or conceptual thing being discussed

Assertion
  A proposition extracted from a located passage
```

An index entry establishes that the indexer associated a passage with a term.
It does not prove that every claim in that passage is correct, nor that the
indexer's framing is the only valid interpretation.

## 4. Index signals

| Index feature | Harvest interpretation |
|---|---|
| Main entry | Candidate major subject |
| Subentry | Candidate scoped subject or relationship |
| Page locator | Passage retrieval target |
| Page range | Extended treatment and higher extraction priority |
| Repeated locators | Subject distributed across contexts |
| `See` reference | Preferred-term candidate, not automatic equivalence |
| `See also` reference | Related-concept or bridge candidate |
| Person index | Entity-resolution queue |
| Place index | Geographic-resolution queue |
| Object index | Material-culture resolution queue |
| Work/source index | Bibliographic and evidence-resolution queue |

For example:

```text
sugar
  Caribbean, 211–245
  consumption, 301–318
  refining, 88–103
  slavery and, 190–267
  taxation of, 275–281
  see also plantations; rum; sugarcane
```

could produce provisional inquiry frames including sugar in the Caribbean,
consumption, refining technology, slavery, taxation, plantation production,
rum production, and sugarcane. These remain source-derived candidates until
reconciled with passages and existing SubjectConcepts.

## 5. Future Index Harvest Agent

A future Index Harvest Agent may sit between deterministic parsing and SFA
workflows:

```text
Deterministic Index Parser
    extracts structure

Index Harvest Agent
    interprets entries and proposes mappings

Resolution Agents
    resolve people, places, concepts, and works

SFAs
    investigate located passages by facet

SCA
    reconciles SubjectConcept and claim proposals

Commit Service
    persists accepted changes
```

It must:

- preserve entries, subentries, locators, and cross-references;
- distinguish index terms from entities and SubjectConcepts;
- follow locators before proposing factual claims;
- preserve index language and original term form;
- identify the edition and indexer when available;
- propose mappings with confidence;
- route located passages to relevant SFAs;
- retain rights and provenance metadata.

It must not:

- treat an index entry as proof of a historical claim;
- promote every index term to a durable SubjectConcept;
- infer that omission means absence or unimportance;
- detach locators from their edition;
- treat `see` or `see also` as automatic SKOS equivalence;
- mutate committed knowledge directly.

## 6. Source and edition identity

An index must never float independently of the publication edition:

```yaml
indexArtifact:
  sourceWork: chr:work:...
  edition: chr:edition:...
  indexer: chr:person-or-role:...
  format: EPUB_INDEX
  language: en
  contentHash: ...
  rightsPolicy: chr:rights:...
  retrievedAt: ...
```

Pagination, terminology, and index structure may change across editions.
Locators therefore remain edition-specific and should resolve against the
corresponding book representation.

## 7. Supported source forms

Future ingestion may support TEI XML, EPUB structured indexes, BITS or
JATS-derived XML, HTML with stable anchors, JSON or JSON-LD indexes, CSV
term-locator exports, OCR-derived PDF indexes with lower confidence, and IIIF
annotations linked to pages or image regions.

The parser should preserve the original artifact and record parsing version,
content hash, retrieval time, and confidence.

## 8. Rights and reproducibility

Before harvesting, the ingestion service must determine:

- whether full text may be retained;
- whether passages may be displayed;
- whether the index may be redistributed;
- whether extracted metadata may be stored;
- whether embeddings may be created and retained;
- whether access is limited to licensed users;
- which edition and index version were processed.

“Train the SFA on the book” is not an adequate architecture term. The system
must distinguish:

```text
Model training
  Changes model weights

Retrieval grounding
  Supplies authorized passages during an invocation

Domain-pack enrichment
  Preserves reusable terms, mappings, and extraction rules
```

The reproducible flow is:

```text
Book and index
  → source repository
Index entries and passages
  → retrieval layer
Extracted observations
  → provenance graph
Validated vocabulary and mappings
  → domain pack
Accepted claims
  → committed knowledge graph
```

## 9. Facet routing

Index entries can be routed to facet workflows without requiring one giant
SubjectConcept:

```text
Economic SFA       taxation, trade, prices, labor, plantations
Technological SFA  mills, refining, crystallization, processing
Social SFA         slavery, indenture, consumption, status
Geographic SFA     Caribbean, Brazil, India, Mediterranean
Environmental SFA  land conversion, irrigation, soil, fuel
```

This is a future capability. It does not expand the Phase 1 node set or
authorize direct writes to Neo4j.

## 10. Implementation status

This capability is intentionally deferred until the minimal graph, source
observations, assertions, proposals, deterministic validation, and commit
path are proven.

The first acceptance test should verify that a machine-readable index can be
ingested while preserving:

1. the edition-specific index artifact;
2. entry and subentry structure;
3. locators and cross-references;
4. source observations from cited passages;
5. proposals separate from accepted claims;
6. rights and retrieval metadata;
7. an explanation of which index entry and passage supported each proposal.
