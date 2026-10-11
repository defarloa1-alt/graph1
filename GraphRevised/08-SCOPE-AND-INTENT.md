# Scope and Intent Boundary

## 1. Product charter

Chrystallum is a historical knowledge-graph system.

> **Chrystallum can graph the history of nearly anything, but it does not
> instruct the user how to do anything merely because that activity can be
> represented as a graph.**

This boundary is about the user's primary purpose, not about which subjects
are allowed. Apple pie, sugar, mollusks, medicine, mathematics, clothing,
weather, agriculture, animals, plants, tools, and chemicals can all be valid
historical subjects.

## 2. Scope decision before entity resolution

The CCA must classify intent before it resolves entities or activates subject
workflows.

```text
User request
  → ScopeDecision
  → candidate interpretation
  → InquiryPlan
  → graph workflow
```

This prevents an ordinary noun such as “sugar” or “apple pie” from being
mistaken for a historical graph request.

## 3. Decision outcomes

Use three outcomes rather than a binary classifier:

```text
IN_SCOPE
OUT_OF_SCOPE
REFRAME_REQUIRED
```

### IN_SCOPE

The principal goal is to construct, extend, interrogate, compare, or explain
historically situated knowledge.

Examples:

```text
Graph the history of sugar.
Graph the spread of sugarcane cultivation.
Graph the historical production of Tyrian purple.
Graph the development of Roman voting institutions.
How were Roman aqueducts repaired?
```

### OUT_OF_SCOPE

The principal goal is procedural instruction, current advice, or general task
completion.

Examples:

```text
Graph how to bake an apple pie.
How do I grow sugarcane?
Graph insulin dosage.
Graph the best modern voting strategy.
```

The system should not answer the procedural question. It should state the
boundary briefly and offer historically framed alternatives.

### REFRAME_REQUIRED

Historical intent is plausible but materially ambiguous.

Examples:

```text
Graph sugar.
Graph apple pie.
Graph mollusks.
```

The CCA should suggest likely historical frames and ask for clarification
when the alternatives would produce materially different graphs.

## 4. ScopeDecision contract

```yaml
scopeDecision:
  decision: IN_SCOPE
  primaryIntent: HISTORICAL_GRAPH_CONSTRUCTION
  domain: COMMODITY_HISTORY
  historicalOrientation: EXPLICIT
  suggestedHistoricalFrames:
    - sugar cultivation and diffusion
    - sugar production and technology
    - sugar trade, labor, and consumption
  explanation: Historical subject graph construction
  nextAction: CREATE_INQUIRY_PLAN
```

Permitted `primaryIntent` values include:

```text
HISTORICAL_GRAPH_CONSTRUCTION
HISTORICAL_TRACE
HISTORICAL_COMPARISON
HISTORIOGRAPHICAL_ANALYSIS
SOURCE_ANALYSIS
PROCEDURAL_INSTRUCTION
CURRENT_ADVICE
NONHISTORICAL_FACT_LOOKUP
UNSUPPORTED_OPERATION
```

Permitted `nextAction` values include:

```text
CREATE_INQUIRY_PLAN
REQUEST_SCOPE_SELECTION
RETURN_SCOPE_REDIRECT
```

## 5. Historical admissibility

A request is historically admissible when its main output would be one or
more of:

- historical entities and authority links;
- events or processes;
- temporal developments and transformations;
- historical places, routes, regions, and spatial change;
- actors, institutions, communities, and roles;
- material culture, technologies, commodities, or practices in context;
- primary or secondary sources;
- historiographical claims or scholarly disagreement;
- provenance-bearing relationships;
- historically meaningful cross-domain paths.

The test is not:

```text
Is this thing intrinsically historical?
```

The test is:

```text
Is the requested graph intended to explain its existence, transformation,
use, meaning, movement, or interpretation through historical time?
```

## 6. Sugar as a stress test

“Graph the history of sugar” is an excellent future test because it requires
cross-domain expansion:

```text
Sugar
  ├─ botanical: sugarcane and sugar beet
  ├─ technological: cultivation, milling, refining, crystallization
  ├─ geographic: origins, diffusion, plantation zones
  ├─ economic: markets, taxation, commodity chains
  ├─ political: empire, colonial regulation, trade policy
  ├─ social: slavery, indenture, labor, consumption
  ├─ environmental: land conversion, irrigation, soil, water
  ├─ scientific: classification, chemistry, nutrition
  └─ cultural: cuisine, ritual, luxury, taste
```

The SCA should distinguish:

```text
Sugar
  material, substance, or commodity entity

History of sugar
  SubjectConcept

Sugarcane
  biological taxon or crop

Sugar production
  historical-technological process

Sugar trade
  historical-economic process

Sugar consumption
  social and cultural process
```

This should become a subject constellation, not one undifferentiated node.

## 7. Routing consequences

An in-scope historical request may select a domain-specific federation profile.
For sugar, the profile might retain:

```text
Wikidata
LCSH and FAST
Getty AAT and TGN
World Historical Gazetteer
PeriodO
VIAF and LCNAF
library and archival catalogs
```

It may add, when justified:

```text
botanical taxonomies
agricultural datasets
commodity-trade datasets
plantation and labor databases
shipping and port datasets
colonial archives
historical statistics
museum collections
historical cookbooks
```

Historical cookbooks may support claims about changing uses and meanings of
sugar. They must not be used to answer a modern recipe or cooking question.

## 8. Redirect behavior

For an out-of-scope request:

1. state the boundary briefly;
2. do not answer the procedural or current-advice question;
3. offer no more than three historical reframings.

Example:

```text
I graph historically situated knowledge rather than provide recipes.
I can instead graph:
1. the history of apple pie;
2. changes in apple-pie ingredients and recipes;
3. sugar, apples, and pastry in food history.
```

## 9. Implementation priority

The scope classifier belongs at the CCA front door but does not need to be
implemented before the Phase 1 database inspection and first direct graph
operations. It should be implemented before autonomous agent routing.

The minimum test set should include:

```text
IN_SCOPE:
  Graph the history of sugar.
  Graph the spread of sugarcane cultivation.

OUT_OF_SCOPE:
  Graph how to bake an apple pie.
  How do I grow sugarcane?

REFRAME_REQUIRED:
  Graph sugar.
  Graph apple pie.
```
