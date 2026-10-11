# Phase 3: Direct Operations

## Purpose

Phase 3 turns the successful Actium write into a small reusable direct-query
surface before any agent is introduced.

The executable artifact is
[13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher).
Each statement is intended to be run independently against the local Neo4j
database `neo4j` with parameters supplied by the caller.

## Operations

### Read operations

- retrieve a node by stable local ID;
- retrieve a Subject and its focus Entity;
- retrieve an Entity's accepted assertion neighborhood;
- retrieve an Assertion's source observations and proposals;
- derive an assertion's event-year context through its assertion object.

### Write operations

- create or reuse an Entity;
- create or reuse a Subject;
- link a Subject to its focus Entity;
- create or reuse a Year and link an Entity to it;
- create or reuse an AuthorityRecord and attach it to an Entity;
- create or reuse a SourceObservation;
- create or reuse an Assertion and connect its endpoints;
- attach a SourceObservation to an Assertion;
- create or reuse a Proposal;
- accept or reject a Proposal and synchronize the Assertion status.

All writes use deterministic caller-supplied IDs and `MERGE`. The Phase 1
uniqueness constraints provide the database-level duplicate protection.
Updates intentionally change only the properties owned by each operation.

### Guarded writes (hardened 2026-10-11)

A write returns zero rows, and writes nothing, when the request is refused.
Callers must treat zero rows as failure. Refusals:

| Operation | Refused when |
|---|---|
| Entity | a retry changes `kind` |
| Year link | the Year is not in the backbone (including year zero); Years are never created |
| AuthorityRecord | the Entity does not exist, or `(system, identifier)` already belongs to another local ID |
| Assertion | an endpoint does not exist, or a retry changes the predicate or endpoints |
| Proposal | the Assertion does not exist, or a retry names a different Assertion |
| Decision | the transition is not in the Proposal lifecycle, or acceptance targets a non-`proposed` Assertion |

Phase 5 added two creation-only parameter groups: `qualifierPropertyIds` on
SourceObservations, and `rationale`, `draftSchemaVersion`,
`predicateRegistryVersion`, `promptVersion`, and `modelId` on Proposals.
[operations.py](operations.py) loads the statements by name.

Optional display parameters may be null; null never erases an existing value.
SourceObservation source facts are immutable after creation. Property names
match the live graph (`sourceRevision`, `rawPayloadUri`).

## Status semantics

An accepted Proposal records workflow history. It does not create a second
historical assertion. New Assertions are created `proposed` and new Proposals
`submitted`; neither status can be set through the create operation.

The decision operation enforces:

```text
submitted  -> validating | rejected | deferred
validating -> accepted | rejected | deferred
deferred   -> validating | rejected
accepted, rejected: terminal
```

Acceptance sets the Assertion to `accepted` and records `acceptedAt`;
rejection sets a `proposed` Assertion to `rejected`. A terminal decision sets
`decidedAt`, `decidedBy`, and `decisionBasis` once. Repeating the current
status is a no-op that preserves them.

## Validation

[tests/test_direct_operations_live.py](tests/test_direct_operations_live.py)
runs against local Neo4j database `neo4j`. Every test executes inside a
transaction that is rolled back, so the database is never changed. It checks:

- the artifact contains 15 statements (checked by the loader in [operations.py](operations.py));
- all reads return the Actium slice, including `Battle of Actium, 31 BCE`;
- replaying all 11 write operations with Actium parameters leaves every node,
  relationship, and property unchanged;
- each refusal case above returns zero rows and changes nothing;
- a new Proposal moves `submitted -> validating -> accepted`, cannot skip
  `validating`, keeps its decision metadata on retry, and a second Proposal's
  rejection leaves the accepted Assertion intact.

All 12 tests passed on 2026-10-11. The pre-hardening operations were also run
in a rolled-back transaction to confirm the defects were real: the Year
operation created a Year `0`, and the decision operation reversed the accepted
Actium Proposal to `rejected`. Database counts remained 4,033 nodes and 4,032
relationships.

Credentials are read from `NEO4J_PASSWORD`; the suite is skipped when it is
unset. They are not copied into the repository artifacts or command output.
