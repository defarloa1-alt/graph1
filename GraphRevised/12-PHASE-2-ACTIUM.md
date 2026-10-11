# Phase 2: Battle of Actium Vertical Slice

## 1. Purpose

This is the first direct, bounded demonstration of the revised graph contract.
No SCA, SFA, CCA, or other agent created the graph data.

It proves that the local graph can distinguish an event, a Subject, an
external authority record, a preserved source observation, a local Assertion,
and an accepted Proposal.

## 2. Preserved source

The source is the Wikidata entity record for the Battle of Actium:

- source entity: `Q160387`;
- label: `Battle of Actium`;
- source revision: `2555342002`;
- retrieved: `2026-10-11T11:25:35+00:00`;
- raw payload:
  [wikidata-Q160387-r2555342002.json](phase-2-source/wikidata-Q160387-r2555342002.json);
- payload metadata:
  [wikidata-Q160387-r2555342002.metadata.json](phase-2-source/wikidata-Q160387-r2555342002.metadata.json);
- SHA-256:
  `8523c2b5e440b6e35a12a6bca3e602c3697b0ddfb03644a09164cf0f978235db`.

Agrippa's identity tether is preserved separately:

- source entity: `Q48174`;
- label: `Marcus Vipsanius Agrippa`;
- source revision: `2532899584`;
- raw payload:
  [wikidata-Q48174-r2532899584.json](phase-2-source/wikidata-Q48174-r2532899584.json);
- payload metadata:
  [wikidata-Q48174-r2532899584.metadata.json](phase-2-source/wikidata-Q48174-r2532899584.metadata.json);
- SHA-256:
  `379d9408a5bb2d4d253b39299dffc9cd25fab1333987a8dffdb98332b84773a0`.

The selected Wikidata statement is:

```text
Q160387$32bdfa2f-497d-fb83-169f-f9567f3152ec
P710 (participant)
Q48174 (Marcus Vipsanius Agrippa)
```

The statement has normal rank but no statement-level Wikidata references.
It is adequate to demonstrate source preservation and governed graph shape;
it is not sufficient scholarly corroboration for a production historical
claim. A future enrichment must add independent source observations before
relying on this assertion beyond the Phase 2 demonstration.

## 3. Created graph slice

```text
(:Subject {
  id: chr:subject:history-of-battle-of-actium,
  label: History of the Battle of Actium,
  status: provisional
})
  -[:HAS_SUBJECT_FOCUS]->
(:Entity {
  id: chr:entity:battle-of-actium,
  description: 31 BCE decisive confrontation of the Final War of the Roman Republic,
  kind: Event,
  status: resolved
})
  -[:IN_YEAR]->
(:Year {year: -31})

(:Entity {id: chr:entity:battle-of-actium})
  -[:HAS_AUTHORITY_RECORD {
    role: entity_identity,
    relation: closeMatch,
    status: accepted
  }]->
(:AuthorityRecord {
  id: chr:authority:wikidata:Q160387,
  label: Wikidata record: Battle of Actium (Q160387),
  description: 31 BCE decisive confrontation of the Final War of the Roman Republic,
  system: Wikidata,
  identifier: Q160387
})

(:Proposal {
  id: chr:proposal:accept-marcus-vipsanius-agrippa-participation-at-actium,
  label: Proposal to accept: Marcus Vipsanius Agrippa participated in Battle of Actium,
  operation: create,
  status: accepted
})
  -[:PROPOSES]->
(:Assertion {
  id: chr:assertion:marcus-vipsanius-agrippa:participated-in:battle-of-actium,
  label: Marcus Vipsanius Agrippa participated in Battle of Actium,
  predicate: participatedIn,
  status: accepted
})
  -[:ASSERTION_SUBJECT]->
(:Entity {id: chr:entity:marcus-vipsanius-agrippa})
  -[:HAS_AUTHORITY_RECORD {
    role: entity_identity,
    relation: closeMatch,
    status: accepted
  }]->
(:AuthorityRecord {
  id: chr:authority:wikidata:Q48174,
  label: Wikidata record: Marcus Vipsanius Agrippa (Q48174),
  system: Wikidata,
  identifier: Q48174
})

(:Assertion)
  -[:ASSERTION_SUBJECT]->
(:Entity {id: chr:entity:marcus-vipsanius-agrippa})

(:Assertion)
  -[:ASSERTION_OBJECT]->
(:Entity {id: chr:entity:battle-of-actium})

(:Assertion)
  -[:SUPPORTED_BY]->
(:SourceObservation {
  id: chr:observation:wikidata:Q160387:P710:32bdfa2f:r2555342002,
  label: Wikidata observation: Marcus Vipsanius Agrippa participated in Battle of Actium,
  sourceSystem: Wikidata,
  sourceEntityId: Q160387,
  predicateExternalId: P710,
  objectExternalId: Q48174,
  externalStatementId: Q160387$32bdfa2f-497d-fb83-169f-f9567f3152ec,
  status: observed
})
```

The Proposal was accepted by the bounded `direct_phase_2_review` workflow. It
means “the system was asked to create this Assertion and the request was
accepted.” It is workflow history, not a second historical statement, and
should normally be hidden outside review/audit views.

The SourceObservation means “Wikidata published this particular statement at
this revision, and Chrystallum preserved what it said.” Its QIDs, predicate
ID, statement ID, revision, and hash are retained so the observation can be
reproduced exactly. The readable `label` is the default graph caption; the
technical identifiers are provenance metadata. QIDs are also represented by
AuthorityRecords connected to the Actium and Agrippa entities.

The participation Assertion has no direct relationship to `Year`. Its date
context is derived through its object:

```text
Agrippa participated in Battle of Actium
  → Battle of Actium
  → IN_YEAR
  → 31 BCE
```

This avoids duplicating the event's date as a second claim on the Assertion.
The navigation projection should display the derived context as “Battle of
Actium, 31 BCE.”

The graph retains full `label` values for details and uses concise
`shortLabel` values for crowded visual maps:

| Node type | Full label | Short caption |
|---|---|---|
| Subject | History of the Battle of Actium | History of Actium |
| Assertion | Marcus Vipsanius Agrippa participated in Battle of Actium | Agrippa -> Battle of Actium |
| Proposal | Proposal to accept: Marcus Vipsanius Agrippa participated in Battle of Actium | Agrippa -> Battle of Actium |
| SourceObservation | Wikidata observation: Marcus Vipsanius Agrippa participated in Battle of Actium | Wikidata: Agrippa -> Actium |
| Actium AuthorityRecord | Wikidata record: Battle of Actium (Q160387) | Wikidata: Actium |
| Agrippa AuthorityRecord | Wikidata record: Marcus Vipsanius Agrippa (Q48174) | Wikidata: Agrippa |

## 4. Verification

The write created exactly:

| Graph item | Count |
|---|---:|
| Nodes | 8 |
| Relationships | 8 |

The database now contains:

| Measure | Count |
|---|---:|
| Nodes | 4,033 |
| Relationships | 4,032 |

The expected graph shape was read back and verified:

- the Subject focuses on the Actium Entity;
- Actium links to Year `-31`;
- Actium has the Wikidata authority record;
- the Assertion links Agrippa to Actium with `participatedIn`;
- both Actium and Agrippa have readable Wikidata AuthorityRecords;
- the Assertion is supported by the preserved source observation;
- the Proposal and Assertion are both `accepted`;
- the persisted statement ID and payload hash match the preserved source
  metadata.

The structural `MERGE` operations were replayed. Node and relationship counts
remained unchanged, demonstrating retry safety for this slice.

## 5. What this proves and what it does not

This proves the minimum graph/provenance/write contract. It does not prove:

- that one Wikidata statement is adequate historical evidence;
- a general entity-resolution workflow for historical people;
- a complete Battle of Actium model;
- agent orchestration;
- a user-facing graph view;
- a multi-source or contested-claim review workflow.

Those remain later phases. Phase 3 should now turn the demonstrated direct
operations into explicit, reusable commands and read queries before any agent
is introduced.
