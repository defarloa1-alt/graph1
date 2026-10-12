# Temporal Year Backbone

## 1. Purpose

At Phase 0 the local Neo4j `neo4j` database contained only the temporal
year backbone. That was the correct starting point for the revised graph;
later phases added data on top of it without changing the backbone.

The separate local `historical` database is empty and is not used by this
clean-start design.

The Phase 0 snapshot records the observed properties. In particular, each
`Year` node has both `year` and `year_value`, along with `label`,
`iso8601_start`, `iso8601_end`, `created`, and `temporal_backbone`.
`Year.year` was chosen as the canonical numeric property (Phase 1); new writes
must not depend on `year_value`.

The year backbone gives the graph a stable, queryable way to attach entities to
calendar years without prematurely introducing a large period ontology.

```text
Year
  └─ provides temporal anchor for ─ Entity
```

## 2. What the year backbone means

A year node represents a temporal coordinate in the graph.

It does not, by itself, assert:

- that a person lived for the whole year;
- that an event occurred on a particular day;
- that a place existed unchanged throughout the year;
- that the year belongs to one universally accepted historical period;
- that a date is certain.

Those meanings require a qualified assertion.

## 3. Initial representation

The minimal representation is:

```text
(:Year {
  year: -31,
  label: "31 BCE"
})
```

The live local database confirms this convention:

```text
positive integer = CE
negative integer = BCE
zero = reserved and absent from the backbone
```

The `FOLLOWED_BY` chain therefore has one deliberate cross-era transition:

```text
1 BCE (-1)
  -[:FOLLOWED_BY]->
1 CE (1)
```

All other links advance by one numeric year. Backbone validation must account
for this zero skip rather than incorrectly treating it as a broken sequence.

## 4. Initial relationship

For the first graph slice:

```text
(:Entity)-[:IN_YEAR]->(:Year)
```

Examples:

```text
Battle of Actium -[:IN_YEAR]-> 31 BCE
```

For a person, the same relationship should not be used to imply lifespan
without a clear predicate. Prefer more specific predicates when needed:

```text
(:Entity)-[:BORN_IN_YEAR]->(:Year)
(:Entity)-[:DIED_IN_YEAR]->(:Year)
(:Entity)-[:ACTIVE_IN_YEAR]->(:Year)
(:Event)-[:OCCURRED_IN_YEAR]->(:Year)
```

An Assertion whose object is a dated event inherits that event's temporal
context for display and navigation. For example, “Agrippa participated in
Battle of Actium” is shown with “Battle of Actium, 31 BCE” from the event's
`IN_YEAR` relationship. This is contextual display, not a second date claim
on the Assertion.

The first implementation may use a single generic relationship if the database
is only validating the backbone. Once different temporal meanings are present,
they should be separated or represented through qualified assertions.

## 5. Precision and uncertainty

Historical dates have different precision:

```text
year
month
day
circa year
before year
after year
range
```

Do not encode uncertainty by changing the year label. Use an assertion:

```yaml
assertion:
  predicate: occurredOn
  subject: chr:entity:actium
  temporalValue:
    earliestYear: -31
    latestYear: -31
    precision: year
    certainty: high
  source: ...
```

If an entity has competing dates, retain both assertions with their sources
and statuses rather than overwriting one date with another.

## 6. Periods are separate

The year backbone should not be turned into a universal historical-period
hierarchy.

For example:

```text
Battle of Actium
  OCCURRED_IN_YEAR
    31 BCE

Battle of Actium
  CONTEXTUALIZED_BY
    a particular PeriodO definition
```

The first is a date claim. The second is a scholarly contextualization claim.
Their sources, meanings, and uncertainty are different.

## 7. First validation queries

The first database validation should answer these questions:

1. How many year nodes exist?
2. Is each year value unique?
3. Are there duplicate year labels or conflicting sign conventions?
4. Can an entity be linked to a year using the intended relationship?
5. Can a query retrieve all entities in a selected year?
6. Can the graph distinguish BCE from CE without relying only on display text?

Example Cypher shape:

```cypher
MATCH (e:Entity)-[:IN_YEAR]->(y:Year {year: -31})
RETURN e
ORDER BY e.label
```

The exact labels, relationship names, and canonical year property should be
confirmed against the live database before implementation code is written.

## 8. Expansion rule

The year backbone is foundational infrastructure, not a reason to preload every
temporal concept.

Add a richer temporal model only when a concrete use case requires:

- date ranges;
- uncertain or competing dates;
- month or day precision;
- PeriodO alignment;
- place-specific temporal applicability;
- time-dependent roles or relationships.

Each addition should preserve the simple year query and explain how the richer
assertion relates to it.
