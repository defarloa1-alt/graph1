# Domain Adaptation and Broad Historical Inquiries

## 1. Why this matters

A request such as:

```text
Graph the history of the Aztecs
```

is not the same kind of request as:

```text
Graph the Battle of Actium
```

The first is a broad historical inquiry. It does not identify one entity and
should not be handled by replacing “Roman” search terms with “Aztec” terms.
It tests whether Chrystallum can adapt its research profile to a different
historical domain.

The stable parts of the system should remain stable:

```text
local identity
SubjectConcept lifecycle
assertions and provenance
proposal and decision workflow
temporal and spatial qualification
navigation and path tracing
```

The variable parts should be selected for the inquiry:

```text
terminology
source languages
authority providers
place reconciliation
period definitions
source traditions
facet emphasis
evidence practices
```

## 2. Resolve the scope before graphing

“Aztec” may refer to several overlapping but non-identical subjects:

- the Mexica people;
- Mexico-Tenochtitlan;
- the Triple Alliance;
- the wider Nahua world;
- Late Postclassic central Mexico;
- Spanish-Indigenous warfare and the fall of Tenochtitlan;
- colonial Nahua history;
- modern scholarly or political uses of the category “Aztec.”

The CCA should not silently choose one interpretation. It should produce a
provisional scope and expose alternatives:

```yaml
inquiryPlan:
  command: GRAPH_SUBJECT
  originalText: Graph the history of the Aztecs
  resolvedFrame:
    preferredLabel: History of the Mexica and the Triple Alliance
    status: provisional
  interpretations:
    - id: chr:frame:mexica-history
      relevance: primary
    - id: chr:frame:triple-alliance-history
      relevance: primary
    - id: chr:frame:nahua-history
      relevance: broader
    - id: chr:frame:spanish-conquest-central-mexico
      relevance: intersecting
    - id: chr:frame:modern-aztec-reception
      relevance: deferred
  temporalScope:
    start: provisional
    end: provisional
  geographicScope:
    primary:
      - Basin of Mexico
      - central Mexico
    expandable: true
```

The user may accept this provisional frame, narrow it, or expand it. The
system should not treat “Aztec” as a homogeneous nation-state by default.

## 3. Subject constellation, not one giant subject

A broad inquiry should initially produce a **subject constellation**:

```text
History of the Mexica and Triple Alliance
  ├─ migration and foundation traditions
  ├─ Mexico-Tenochtitlan
  ├─ formation of the Triple Alliance
  ├─ Tenochtitlan, Tetzcoco, and Tlacopan
  ├─ expansion and warfare
  ├─ tribute and political administration
  ├─ relations with independent and subject polities
  ├─ religion and ritual institutions
  ├─ trade and material production
  ├─ codices and historical memory
  ├─ Spanish-Indigenous invasion and alliances
  ├─ fall of Tenochtitlan
  └─ early colonial Nahua transformation
```

Some branches focus on entities, some on processes, and some on documentary
or historiographical subjects. They begin as provisional frames and are
promoted to durable SubjectConcepts only when they develop coherent claim
clusters, recur in inquiry, map to useful literature, or receive curator
approval.

## 4. Domain packs

A domain pack is configuration and guidance for a historical domain. It is not
an assertion of historical truth and it must not alter the core provenance or
commit model.

```yaml
domainPack:
  id: chr:domain-pack:mesoamerica-v1
  preferredEntityKinds:
    - Altepetl
    - PoliticalAlliance
    - Ruler
    - Deity
    - TributeProvince
    - Codex
    - PictorialManuscript
    - Glyph
    - ArchaeologicalSite
    - TempleComplex
    - ConquestEvent
  preferredPredicates:
    - memberOfAlliance
    - ruledAltepetl
    - paidTributeTo
    - depictedInCodex
    - namedByGlyph
    - attestedInLanguage
    - locatedInBasin
  sourceLanguages:
    - Classical Nahuatl
    - Spanish
  federationProfile:
    - Wikidata
    - World Historical Gazetteer
    - Getty TGN
    - Getty AAT
    - Mexican heritage sources
    - codex and manuscript sources
  disabledByDefault:
    - Pleiades
    - Roman prosopographies
```

The domain pack supplies candidate vocabulary, routing, and validation
guidance. It does not make a candidate predicate true.

## 5. Federation profiles by capability

The CCA should request capabilities rather than hard-code provider names:

```yaml
requiredCapabilities:
  - multilingual_entity_resolution
  - mesoamerican_historical_places
  - Nahuatl_name_resolution
  - archaeological_site_resolution
  - pictorial_manuscript_analysis
  - historical_period_alignment
  - bibliographic_subject_resolution
  - source_passage_retrieval
  - image_region_annotation
```

A federation registry can select providers by:

- domain coverage;
- geographic coverage;
- chronological coverage;
- language support;
- authority and scholarly role;
- data accessibility;
- licensing;
- service health;
- expected precision.

The registry should distinguish technical access modes:

```text
API
downloadable dataset
SPARQL or linked data
reconciliation endpoint
IIIF manifest
searchable scholarly website
catalog requiring an adapter
manual curatorial source
```

A source can be intellectually essential even when it has no convenient API.

## 6. Source perspective

For historical domains with multilingual, colonial, pictorial, or
collaborative sources, `primary` versus `secondary` is not enough.

A source observation may need:

```yaml
sourcePerspective:
  creatorCommunity: Nahua | Spanish | mixed-collaborative | modern-scholarly
  productionContext: preconquest | conquest-era | early-colonial | modern
  expressionMode: alphabetic-text | pictorial-writing | material-evidence
  language: Classical-Nahuatl | Spanish | English
  mediation: original | colonial-gloss | transcription | translation | interpretation
```

For a complex codex or edition, evidence should point as precisely as
possible:

```text
work
  → book
  → chapter
  → folio
  → text column or image region
  → language version
  → transcription or translation
```

This prevents a whole work from being treated as a single undifferentiated
“source.”

## 7. Do not force foreign categories into local concepts

Domain adaptation must preserve Indigenous or source-specific concepts.

For example, the system must not silently translate:

```text
tlatoani → king
altepetl → city-state
Triple Alliance → empire
```

An English gloss may help discovery, but the local record should preserve the
original term and mark any cross-cultural mapping as approximate, interpretive,
or contested.

The same rule applies to Roman, Greek, Chinese, African, Indigenous, and
modern domains. A domain pack may offer mappings; it must not erase the
concepts being mapped.

## 8. Facet activation

The canonical facets remain stable, but their relative importance and prompts
change by domain:

```text
Political:
  altepetl, rulers, alliances, tribute, administration

Military:
  conquests, campaigns, resistance, Spanish-Indigenous warfare

Geographic:
  basin settlements, routes, lakes, provinces, changing place names

Economic:
  tribute, markets, agriculture, craft production, trade

Religious:
  deities, temples, rituals, calendars

Linguistic:
  Nahuatl names, titles, glyph readings, Spanish transformations

Artistic / Archaeological:
  codices, sculpture, architecture, sites, objects, building phases
```

The domain pack changes routing and evidence expectations. It does not create
a second incompatible SCA/SFA architecture.

## 9. Implementation boundary

This is future work, not Phase 1. The clean-start implementation should first
prove the core model using the temporal backbone and one small historical
example.

When domain portability is tested, the order should be:

```text
CCA detects domain shift
  → resolve provisional scope
  → select or propose DomainPack
  → build capability-based FederationPlan
  → create subject constellation
  → activate relevant facets
  → collect source observations and proposals
  → reconcile and commit through the unchanged core workflow
```

The core architecture remains stable while the domain package changes.
