# Graph Navigation and Visual Read Model

## 1. Purpose

Graph navigation is a central user experience in Chrystallum. The user should
be able to see a visual map, select a node, inspect its relationships, and
expand the graph into a relevant neighborhood.

The revised data model supports this directly. The important distinction is:

```text
Durable graph
  = complete, provenance-preserving source of knowledge

Navigation projection
  = bounded, readable view for the current screen or inquiry
```

The UI should not attempt to draw the entire Neo4j database. It should request
an inquiry-specific subgraph and expand it deliberately.

## 2. What the user sees

The initial visual map should show:

- entities such as people, places, events, groups, objects, works, and periods;
- subjects connected to their focus entities;
- meaningful relationships between entities;
- authority records when the user requests source context;
- claims or proposals when the user turns on those layers;
- years or temporal ranges when temporal context is selected.

Example:

```text
Battle of Actium
  ├─ participant → Octavian
  ├─ participant → Mark Antony
  ├─ occurred in → 31 BCE
  ├─ located near → Actium promontory
  ├─ part of → Final War of the Roman Republic
  └─ has subject → Battle of Actium research subject
```

The map is a way to explore relationships, not merely a display of database
nodes.

## 3. Durable graph versus display projection

The durable graph may contain more structure than the first visual map needs:

```text
Entity
  → Assertion
      → SourceObservation
          → raw source payload
```

Rendering every assertion and observation as a visible node would make the
map difficult to read. The read API should therefore support two projections.

### Compact projection

The default map renders an assertion as a labeled edge:

```text
Agrippa ── participated in [accepted] ──> Battle of Actium
```

The edge metadata should include:

- canonical predicate;
- display label;
- direction;
- status;
- confidence or evidence assessment;
- number of supporting sources;
- whether the edge is imported, inferred, or locally proposed.

### Evidence projection

When the user expands an edge, the UI may reveal:

```text
Assertion
  ├─ source observation
  ├─ source authority
  ├─ passage or locator
  ├─ decision
  ├─ agent or curator
  └─ revision and retrieval information
```

This keeps ordinary navigation readable while preserving full auditability.

## 4. Node display types

The UI should visually distinguish node roles:

| Node kind | Suggested display meaning |
|---|---|
| Entity | A historical, physical, social, or analytical thing |
| Subject | A body of knowledge or inquiry about one or more entities |
| Year | A temporal coordinate |
| AuthorityRecord | An external identification or classification |
| SourceObservation | What an external source asserted |
| Assertion | A local claim or relationship with context |
| Proposal | A not-yet-accepted graph change |

The user should be able to filter these layers. The default view should
prioritize entities and accepted relationships, with subjects and temporal
anchors available as first-class navigation targets.

## 5. Expansion model

Navigation should be incremental:

```text
Open a root node
  → load first neighborhood
  → select a node or edge
  → expand one relationship family
  → inspect evidence if needed
  → pin useful nodes
  → continue or return
```

Every expansion request should declare:

```yaml
navigationRequest:
  rootId: chr:entity:actium-31-bce
  depth: 1
  relationshipFamilies:
    - participation
    - temporal
    - location
  include:
    subjects: true
    authorities: false
    proposals: false
  statusFilter:
    - accepted
  maxNodes: 75
  maxEdges: 150
```

The API should enforce node, edge, and traversal budgets. This protects the UI
from accidental full-graph queries and keeps expansion responsive.

## 6. Query-specific maps

The same entity can have many useful maps. The UI should support a map context:

```yaml
mapContext:
  root: chr:entity:actium-31-bce
  subject: chr:subject:battle-of-actium
  activeFacet: POLITICAL
  temporalFilter:
    yearFrom: -32
    yearTo: -30
  relationshipFamilies:
    - coalition
    - leadership
    - consequence
  statusFilter:
    - accepted
    - contested
```

This means the user can view Actium as:

- a military event;
- a political transition;
- a geographic setting;
- an archaeological subject;
- a communication and commemoration problem.

The underlying graph does not change when the user changes the map context.
Only the projection changes.

## 7. Accepted, proposed, and contested graph

The visual map must make epistemic status visible.

Suggested display conventions:

```text
accepted:
  solid edge, normal opacity

proposed:
  dashed edge, muted color

contested:
  double or warning edge, visible disagreement marker

rejected:
  hidden by default, available in audit mode

superseded:
  hidden by default, available through history
```

The UI should never make a proposed relationship look identical to an accepted
one.

Facet colors should indicate the active inquiry lens, not permanent ontology.
For example, a Political view may color political proposals without implying
that the event belongs exclusively to the Political facet.

## 8. Navigation operations

The first read API should support a small set of operations:

```text
getNode(id)
getNeighborhood(id, filters, budget)
expandRelationshipFamily(id, family, budget)
getAssertionEvidence(assertionId)
getSubjectFocus(subjectId)
getTemporalContext(id, range)
getAuthorityContext(id)
getProposalOverlay(subjectId or inquiryId)
```

These are read operations. They do not create or modify durable knowledge.

Write actions from the UI should be commands:

```text
submitProposal
acceptProposal
rejectProposal
mergeNodes
addCuratorNote
```

Each command must use the same validation and commit path as agent-generated
changes.

## 9. Stable navigation identifiers

Every visible node and edge must have a stable local identifier:

```text
nodeId: chr:entity:actium-31-bce
assertionId: chr:assertion:...
proposalId: chr:proposal:...
```

External identifiers may be shown as badges or used to open source records, but
they must not replace the local identifiers used for navigation, bookmarks,
history, or saved maps.

## 10. Saved maps and replay

A saved map should store the query context, not a copied graph snapshot:

```yaml
savedMap:
  id: chr:map:...
  root: chr:entity:actium-31-bce
  subject: chr:subject:battle-of-actium
  filters: ...
  layout: ...
  pinnedNodes: [...]
  createdAt: ...
  graphVersion: ...
```

When the graph changes, the saved map can be re-run and the UI can show what
was added, removed, superseded, or newly contested.

## 11. First vertical-slice UI

The first visual slice should not wait for the full agent architecture. It
should provide:

1. a root-node search or direct ID entry;
2. a one-hop neighborhood query;
3. clickable nodes;
4. labeled directional edges;
5. node detail panel;
6. accepted/proposed status styling;
7. temporal year display;
8. authority and evidence expansion;
9. bounded expansion;
10. a clear distinction between read and write actions.

Use the temporal year backbone as the first non-entity expansion target. Once a
sample entity is connected to a year, the UI should be able to navigate from
the entity to the year and from the year back to related entities.

## 12. Design rule

The graph model supports visual navigation when the read path treats the graph
as a set of bounded, typed neighborhoods rather than one undifferentiated
diagram.

The governing rule is:

> Store the complete evidence graph; display the smallest useful projection;
> let the user expand relationships deliberately; never hide epistemic status
> or provenance behind an indistinguishable edge.

## 13. Long-range tracing

The ultimate navigation test is whether a user can begin with one kind of
entity and trace a meaningful path to a very different kind of entity.

For example, the point of tracing a Roman senator to a mollusk is the
conceptual chain through **purple**:

```text
Roman senator
  → held social/political rank marked by
  → senatorial dress convention
  → included
  → broad purple stripe
  → could be colored using
  → shellfish or Tyrian purple
  → produced from secretions of
  → muricid sea-snail species
  → taxonomically belongs to
  → Mollusca
```

The answer should be yes, provided the graph contains the relevant assertions.
The model does not require all nodes in a path to have the same kind. People,
events, places, objects, works, subjects, periods, and biological or material
entities may be connected by typed relationships.

One possible historical path might be:

```text
Roman senator
  ── status marked by ──> senatorial dress convention
  ── included ──> broad purple stripe
  ── could use colorant ──> shellfish purple
  ── produced from secretion of ──> Muricidae
  ── subclass of ──> Mollusca
```

The wording “could use colorant” is intentional. The graph must not universalize
the claim that every senatorial purple stripe used Tyrian purple. The path may
contain generalizations, exceptions, or proposed hops, and the UI must expose
those qualifications.

That is only a valid historical explanation if each edge is supported. The UI
must not imply that a path is meaningful merely because Neo4j can find a route
between two nodes.

## 14. Two trace modes

The navigation service should support two different operations:

```text
TRACE_EXISTING_PATH
  Given endpoints and committed graph edges, find and explain admissible paths.

DISCOVER_SEMANTIC_BRIDGE
  Given endpoints that appear unrelated, propose intermediate concepts,
  investigate missing relationships, and validate a coherent explanation.
```

The second mode is not ordinary navigation. A shortest-path algorithm may find
an accidental route through generic or unrelated edges. Semantic bridge
discovery must prefer explanatory continuity and typed predicates.

For the senator-to-mollusk example, likely investigative facets include:

```text
SOCIAL
POLITICAL
ARTISTIC
TECHNOLOGICAL
ECONOMIC
SCIENTIFIC
```

The bridge workflow may ask those facets to investigate separate hops. It
should not require a new permanent “Bridge Agent”; a bounded path planner and
an SCA-coordinated bridge workflow are sufficient at first.

## 15. Path hypotheses are not claims

A discovered path is initially a query artifact:

```text
TraceRequest
  → TraceResult
      → PathHypothesis
          → TraceHop
```

Each hop may point to:

- an accepted assertion;
- a contested assertion;
- an authority mapping;
- an inferred relation;
- a proposed relationship requiring research.

Finding a path does not make the path true. Only missing or improved
relationships should enter the proposal and decision workflow.

A semantic bridge result should report:

```yaml
pathType: CROSS_DOMAIN_EXPLANATORY
historicallyMeaningful: true
causal: false
containsGeneralizations: true
weakestHop: 3
requiresResearch: true
```

The path type matters. A path through purple is a mixed status-material-
production-taxonomy explanation, not a causal chain in which the mollusk
caused the senator.

## 16. Path ranking

Do not rank paths primarily by shortest distance. Rank them using:

1. predicate specificity;
2. evidence completeness;
3. assertion status;
4. temporal compatibility;
5. spatial compatibility;
6. type consistency;
7. explanatory continuity;
8. number of inferred hops;
9. number of generic edges;
10. path length.

This is a retrieval and explanation ranking, not an objective historical
probability.

## 17. SubjectConcept consequence

A bridge investigation may reveal a useful temporary subject frame such as:

```text
Purple as a marker of Roman political status
Murex dye and Roman elite dress
```

These should initially remain ephemeral. They may become durable SubjectConcepts
only if they develop a coherent claim cluster, recur across inquiries, map to
relevant literature, or receive curator approval.

This gives the clean-start model a disciplined way to discover new subjects:

```text
Remote endpoints
  → candidate semantic bridge
  → facet investigation
  → validated claim cluster
  → possible SubjectConcept promotion
```

### 13.1 Path tracing requirements

A trace request should specify:

```yaml
traceRequest:
  start: chr:entity:senator-...
  target: chr:entity:mollusk-...
  maxHops: 6
  allowedRelationshipFamilies:
    - office
    - participation
    - place
    - object
    - type
  statusFilter:
    - accepted
    - contested
  requireEvidence: true
  maxPaths: 10
```

The response should contain paths, not just a list of reachable nodes:

```yaml
path:
  nodes:
    - id: chr:entity:senator-...
      label: ...
    - id: chr:entity:office-...
      label: ...
    - id: chr:event:...
      label: ...
    - id: chr:place:...
      label: ...
    - id: chr:entity:mollusk-...
      label: ...
  edges:
    - assertionId: chr:assertion:...
      predicate: heldOffice
      status: accepted
      evidenceCount: 2
    - assertionId: chr:assertion:...
      predicate: participatedIn
      status: accepted
      evidenceCount: 3
  explanation: ...
```

### 13.2 Path quality

The system should rank or filter paths using:

- maximum hop count;
- allowed relationship families;
- accepted versus contested status;
- evidence availability;
- temporal compatibility;
- spatial compatibility;
- duplicate or circular path suppression;
- whether the path crosses an authority mapping or a SubjectConcept;
- whether any edge is inferred rather than directly sourced.

An inferred path must be visibly different from a directly documented path.
The UI should be able to say:

```text
This path contains two directly sourced assertions and one inferred
relationship. It is offered as a research lead, not as an established fact.
```

### 13.3 Path explanation

Every displayed path should be expandable into a hop-by-hop explanation:

```text
1. The senator held office X.
2. Office X is associated with event Y.
3. Event Y occurred at place Z.
4. Place Z has an excavated shell deposit.
5. The deposit is classified by the relevant authority as a mollusk.
```

Each sentence must link to the assertion and evidence that support it. If the
path crosses a SubjectConcept, the UI should label that transition as an
organizational or research connection rather than presenting it as a direct
historical relationship.

The governing rule for long-range navigation is:

> The graph may discover a path across many entity types, but the UI may only
> present it as an explanation when every hop is typed, bounded, status-aware,
> and traceable to evidence.
