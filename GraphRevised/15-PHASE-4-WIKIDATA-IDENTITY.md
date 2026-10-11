# Phase 4: Wikidata Identity Discovery

## Scope

The first authority adapter is limited to **identity discovery**. It:

1. searches Wikidata for a bounded set of entity candidates;
2. preserves the raw search response outside Neo4j;
3. retrieves and preserves the leading candidate's entity response;
4. returns a `SourceObservationDraft` with revision, retrieval time, content
   hash, and file URI;
5. returns candidates as candidates only.

It does not create an `Entity`, `AuthorityRecord`, `Assertion`, `Proposal`, or
accepted authority mapping. A caller must explicitly review a candidate and
then use the Phase 3 direct operations to persist any local graph change.

## Artifact

[adapters/wikidata_identity.py](adapters/wikidata_identity.py) provides
`WikidataIdentityAdapter`. Its preserved payload directory is supplied by the
caller, keeping raw source material outside the domain graph.

The adapter accepts one query, a language, and a maximum of ten candidates.
Its deterministic observation ID includes the Wikidata identifier, revision,
and payload hash. The same source revision therefore produces the same
observation ID.

The draft maps onto the Phase 3 SourceObservation operation as `revision` →
`sourceRevision` and `payload_uri` → `rawPayloadUri`; the statement-specific
parameters are null. Its ID uses the identity-record form described in
[02-GRAPH-MODEL.md](02-GRAPH-MODEL.md), which deliberately differs from the
statement-observation ID used for the Phase 2 participation claim.

## Failure behavior

Network failures, HTTP errors, invalid JSON, and Wikidata API errors raise
`WikidataAdapterError`. Empty search results return an explicit result with no
candidates and no source observation. The adapter never substitutes a
successful-looking fallback.

## Validation

[tests/test_wikidata_identity.py](tests/test_wikidata_identity.py) uses
fixture responses to verify candidate extraction, raw payload preservation,
revision capture, deterministic observation data, and the empty-result path.

The fixture test suite passed with two tests. A bounded live lookup for
`Battle of Actium` also passed on 2026-10-11:

- candidates returned: 2;
- leading candidate: `Q160387`, Battle of Actium;
- entity revision: `2555342002`;
- observation ID:
  `chr:observation:wikidata:Q160387:r2555342002:101c0257ee07cbaf1b50`;
- preserved entity payload:
  [wikidata-entity-Q160387-r2555342002.json](phase-4-source/wikidata-entity-Q160387-r2555342002.json);
- preserved metadata:
  [wikidata-entity-Q160387-r2555342002.metadata.json](phase-4-source/wikidata-entity-Q160387-r2555342002.metadata.json);
- payload SHA-256:
  `d191188caf79df818ead0e9ee669046cc68bea4cc89863f1f94b9c0f4623041f`.

The live validation persisted no nodes or relationships. In particular, it
did not create an accepted identity mapping or historical assertion.

## Reviewed adoption

After human review, the leading candidate's Wikidata description was adopted
as display text on the existing local Battle of Actium Entity and preserved
unchanged on its linked Wikidata AuthorityRecord:

```text
31 BCE decisive confrontation of the Final War of the Roman Republic
```

The Entity property is the locally adopted description. The AuthorityRecord
property remains explicitly source-derived, with the preserved payload,
revision, and SourceObservation retaining its provenance.
