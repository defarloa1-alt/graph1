# Chrystallum Clean-Start Handoff

## Completed work

- Phase 0: validated the local Neo4j Year backbone.
- Phase 1: applied eight minimum uniqueness constraints.
- Phase 2: created and verified the Battle of Actium vertical slice.
- Phase 3: implemented and replay-validated 15 parameterized direct Cypher
  operations.
- Phase 4: implemented and live-validated a candidate-only Wikidata identity
  adapter with raw payload preservation.
- Phase 4.5: created a non-destructive legacy triage/adoption boundary.

## Database state

Local endpoint: `neo4j://127.0.0.1:7687`

Database: `neo4j`

Current verified counts after Phase 3 replay:

```text
4,033 nodes
4,032 relationships
```

Credentials are in `Connections.txt`; do not display, copy, or commit them.

## Actium slice

The graph has:

```text
Subject: History of the Battle of Actium
  → HAS_SUBJECT_FOCUS → Battle of Actium Entity
  → IN_YEAR → 31 BCE

Assertion:
  Marcus Vipsanius Agrippa participated in Battle of Actium
  → ASSERTION_SUBJECT → Agrippa Entity
  → ASSERTION_OBJECT → Actium Entity
  → SUPPORTED_BY → Wikidata SourceObservation

Proposal
  → PROPOSES → Assertion
```

The existing Actium Entity and its linked Wikidata AuthorityRecord now both
have the reviewed description:

```text
31 BCE decisive confrontation of the Final War of the Roman Republic
```

The Entity description is locally adopted display text; the AuthorityRecord
description preserves Wikidata's source wording.

## Important artifacts

- [10-PHASE-1-SCHEMA.cypher](10-PHASE-1-SCHEMA.cypher) — applied constraints.
- [12-PHASE-2-ACTIUM.md](12-PHASE-2-ACTIUM.md) — Actium model and source limitation.
- [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher) — 15 direct reads/writes.
- [14-PHASE-3-RESULTS.md](14-PHASE-3-RESULTS.md) — validation result.
- [adapters/wikidata_identity.py](adapters/wikidata_identity.py) — bounded candidate-only adapter.
- [15-PHASE-4-WIKIDATA-IDENTITY.md](15-PHASE-4-WIKIDATA-IDENTITY.md) — Phase 4 contract and validation.
- [16-LEGACY-TRIAGE.md](16-LEGACY-TRIAGE.md) — active/legacy boundary.

Phase 4 payloads are in [phase-4-source](phase-4-source). The current Actium
lookup returned candidates `Q160387` (31 BCE) and `Q9173813` (435 BCE).
Only `Q160387` is locally associated with the existing Actium Entity.

## Validation

Passed:

```text
python -m unittest GraphRevised.tests.test_wikidata_identity -v
python -m unittest GraphRevised.tests.test_direct_operations_live -v   # needs NEO4J_PASSWORD
git diff --check -- GraphRevised
```

The live suite replays all 15 Cypher operations and their refusal cases inside
rolled-back transactions; the database is never changed.

Phase 5 must use the hardened decision operation: a Proposal is created
`submitted`, must pass through `validating`, and only then may be `accepted`
or `rejected`. Zero rows from any write means the request was refused.

## Next work: Phase 5

Do not reuse the legacy agent chain directly. Build a new bounded proposal
workflow:

```text
SourceObservation + bounded local candidate context
  → Proposal Agent prompt
  → typed ProposalDraft
  → deterministic validator
  → stored Proposal
  → human review
  → explicit accept/reject operation
```

The first test should replay the existing Actium/Agrippa source observation.
The agent may propose; it may not create accepted Entities, Assertions, or
AuthorityRecords, execute arbitrary Cypher, silently resolve ambiguity, or
invent evidence.

Phase 5 needs:

1. `ProposalDraft` schema;
2. a versioned narrow agent prompt;
3. deterministic validator;
4. proposal storage/review integration using Phase 3 operations;
5. a replay test using the existing Actium source observation.

## Vertex jump guidance

Vertex jump is a direct deterministic lookup from known canonical identity or
an approved versioned property bundle. It complements, rather than replaces,
graph traversal.

Use immediately for stable keys:

```text
Entity.id
Subject.id
AuthorityRecord(system, identifier)
Assertion.id
Proposal.id
```

Do not hash all mutable node properties. A future composite jump key requires
an explicit, versioned canonicalization contract and must not silently resolve
ambiguous identities.

## Repository safety

The worktree was already heavily dirty. Do not revert unrelated changes.
`GraphRevised` is untracked in the current worktree, so `git status` will show
it as `?? GraphRevised/`. No files were moved, deleted, or bulk-archived as
part of Phase 4.5.
