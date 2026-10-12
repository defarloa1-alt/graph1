// Phase 3 direct operations.
//
// Run each statement independently against the local `neo4j` database.
// Callers must provide deterministic IDs and parameters. Every write is
// retry-safe under the Phase 1 uniqueness constraints.
//
// Guarded writes return zero rows, and write nothing, when the request is
// refused (unknown endpoint, conflicting identity, illegal transition, Year
// outside the backbone). Callers must treat zero rows from a write as failure.
//
// Optional display parameters may be null. On a retry, null never erases an
// existing value, and identity-defining properties are never rewritten.

// ---------------------------------------------------------------------------
// Reads
// ---------------------------------------------------------------------------

// Get one node by its stable local ID.
MATCH (node:Entity {id: $id}) RETURN node, labels(node) AS nodeTypes
UNION MATCH (node:Subject {id: $id}) RETURN node, labels(node) AS nodeTypes
UNION MATCH (node:AuthorityRecord {id: $id}) RETURN node, labels(node) AS nodeTypes
UNION MATCH (node:SourceObservation {id: $id}) RETURN node, labels(node) AS nodeTypes
UNION MATCH (node:Assertion {id: $id}) RETURN node, labels(node) AS nodeTypes
UNION MATCH (node:Proposal {id: $id}) RETURN node, labels(node) AS nodeTypes;

// Get a subject and its focus entity.
MATCH (subject:Subject {id: $subjectId})
OPTIONAL MATCH (subject)-[:HAS_SUBJECT_FOCUS]->(focus:Entity)
RETURN subject, focus;

// Get an entity's compact accepted assertion neighborhood.
MATCH (subjectEntity:Entity {id: $entityId})
OPTIONAL MATCH (assertion:Assertion {status: "accepted"})
  -[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(subjectEntity)
OPTIONAL MATCH (assertion)-[:ASSERTION_SUBJECT]->(assertionSubject)
OPTIONAL MATCH (assertion)-[:ASSERTION_OBJECT]->(assertionObject)
WHERE assertionSubject IS NOT NULL AND assertionObject IS NOT NULL
RETURN
  assertionSubject,
  assertion.predicate AS predicate,
  assertion.label AS assertionLabel,
  assertion.status AS assertionStatus,
  assertionObject;

// Get a complete evidence trail for one assertion.
MATCH (assertion:Assertion {id: $assertionId})
OPTIONAL MATCH (assertion)-[:ASSERTION_SUBJECT]->(assertionSubject)
OPTIONAL MATCH (assertion)-[:ASSERTION_OBJECT]->(assertionObject)
OPTIONAL MATCH (assertion)-[:SUPPORTED_BY]->(observation:SourceObservation)
OPTIONAL MATCH (proposal:Proposal)-[:PROPOSES]->(assertion)
RETURN
  assertion,
  assertionSubject,
  assertionObject,
  collect(DISTINCT observation) AS sourceObservations,
  collect(DISTINCT proposal) AS proposals;

// Derive temporal context for an assertion through its object entity.
MATCH (assertion:Assertion {id: $assertionId})
      -[:ASSERTION_OBJECT]->(event:Entity)
OPTIONAL MATCH (event)-[:IN_YEAR]->(year:Year)
RETURN
  assertion,
  event,
  year.year AS eventYear,
  CASE
    WHEN year.year IS NULL THEN event.label
    WHEN year.year < 0 THEN event.label + ", " + toString(abs(year.year)) + " BCE"
    WHEN year.year > 0 THEN event.label + ", " + toString(year.year) + " CE"
    ELSE event.label
  END AS temporalContext;

// ---------------------------------------------------------------------------
// Idempotent writes
// ---------------------------------------------------------------------------

// Create or reuse an Entity. `kind` is fixed at creation; a retry with a
// different kind is refused.
OPTIONAL MATCH (existing:Entity {id: $id})
WITH existing
WHERE existing IS NULL OR existing.kind = $kind
MERGE (node:Entity {id: $id})
ON CREATE SET
  node.kind = $kind,
  node.label = $label,
  node.description = $description,
  node.status = $status,
  node.shortLabel = $shortLabel
ON MATCH SET
  node.label = coalesce($label, node.label),
  node.description = coalesce($description, node.description),
  node.status = coalesce($status, node.status),
  node.shortLabel = coalesce($shortLabel, node.shortLabel)
RETURN node;

// Create or reuse a Subject.
MERGE (subject:Subject {id: $id})
ON CREATE SET
  subject.label = $label,
  subject.status = $status,
  subject.shortLabel = $shortLabel
ON MATCH SET
  subject.label = coalesce($label, subject.label),
  subject.status = coalesce($status, subject.status),
  subject.shortLabel = coalesce($shortLabel, subject.shortLabel)
RETURN subject;

// Link a Subject to its focus Entity.
MATCH (subject:Subject {id: $subjectId})
MATCH (entity:Entity {id: $entityId})
MERGE (subject)-[relationship:HAS_SUBJECT_FOCUS]->(entity)
RETURN subject, relationship, entity;

// Link an Entity to an existing backbone Year. Never creates a Year: a year
// outside the backbone, including year zero, is refused.
MATCH (entity:Entity {id: $entityId})
MATCH (year:Year {year: $year})
MERGE (entity)-[relationship:IN_YEAR]->(year)
RETURN entity, relationship, year;

// Create or reuse an AuthorityRecord and attach it to an Entity. The record is
// keyed by (system, identifier); a retry under a different local ID is refused.
MATCH (entity:Entity {id: $entityId})
OPTIONAL MATCH (existing:AuthorityRecord {system: $system, identifier: $identifier})
WITH entity, existing
WHERE existing IS NULL OR existing.id = $id
MERGE (record:AuthorityRecord {system: $system, identifier: $identifier})
ON CREATE SET
  record.id = $id,
  record.label = $label,
  record.shortLabel = $shortLabel,
  record.description = $description,
  record.retrievedAt = $retrievedAt,
  record.sourceUri = $sourceUri,
  record.sourceRevision = $sourceRevision,
  record.contentHash = $contentHash,
  record.rawPayloadUri = $rawPayloadUri
ON MATCH SET
  record.label = coalesce($label, record.label),
  record.shortLabel = coalesce($shortLabel, record.shortLabel),
  record.description = coalesce($description, record.description),
  record.retrievedAt = coalesce($retrievedAt, record.retrievedAt)
MERGE (entity)-[relationship:HAS_AUTHORITY_RECORD]->(record)
ON CREATE SET
  relationship.role = $role,
  relationship.relation = $relation,
  relationship.status = $linkStatus
RETURN entity, relationship, record;

// Create or reuse a preserved SourceObservation. Source facts are immutable
// after creation; only display text and observed/superseded status may change.
MERGE (observation:SourceObservation {id: $id})
ON CREATE SET
  observation.label = $label,
  observation.shortLabel = $shortLabel,
  observation.sourceSystem = $sourceSystem,
  observation.sourceEntityId = $sourceEntityId,
  observation.predicateExternalId = $predicateExternalId,
  observation.objectExternalId = $objectExternalId,
  observation.externalStatementId = $externalStatementId,
  observation.qualifierPropertyIds = $qualifierPropertyIds,
  observation.sourceRevision = $sourceRevision,
  observation.retrievedAt = $retrievedAt,
  observation.contentHash = $contentHash,
  observation.rawPayloadUri = $rawPayloadUri,
  observation.status = $status
ON MATCH SET
  observation.label = coalesce($label, observation.label),
  observation.shortLabel = coalesce($shortLabel, observation.shortLabel),
  observation.status = coalesce($status, observation.status)
RETURN observation;

// Create or reuse a preserved passage SourceObservation: a located span of a
// specific edition. The passage text excludes editorial notes, which are kept
// separately so a modern editor's note is never cited as the source.
MERGE (observation:SourceObservation {id: $id})
ON CREATE SET
  observation.label = $label,
  observation.shortLabel = $shortLabel,
  observation.observationKind = "passage",
  observation.sourceSystem = $sourceSystem,
  observation.locator = $locator,
  observation.passageText = $passageText,
  observation.passageHash = $passageHash,
  observation.editorialNotes = $editorialNotes,
  observation.language = $language,
  observation.workTitle = $workTitle,
  observation.author = $author,
  observation.translator = $translator,
  observation.editionCitation = $editionCitation,
  observation.rights = $rights,
  observation.sourceUri = $sourceUri,
  observation.sourceRevision = $sourceRevision,
  observation.retrievedAt = $retrievedAt,
  observation.contentHash = $contentHash,
  observation.rawPayloadUri = $rawPayloadUri,
  observation.status = $status
ON MATCH SET
  observation.label = coalesce($label, observation.label),
  observation.shortLabel = coalesce($shortLabel, observation.shortLabel),
  observation.status = coalesce($status, observation.status)
RETURN observation;

// Create or reuse a normalized Assertion and connect its endpoints. A new
// Assertion is always `proposed`; status changes only through a Proposal
// decision. Predicate and endpoints are fixed at creation; a retry with a
// different predicate or endpoint is refused.
OPTIONAL MATCH (existing:Assertion {id: $id})
OPTIONAL MATCH (existing)-[:ASSERTION_SUBJECT]->(existingSubject)
OPTIONAL MATCH (existing)-[:ASSERTION_OBJECT]->(existingObject)
WITH existing,
     collect(DISTINCT existingSubject.id) AS existingSubjectIds,
     collect(DISTINCT existingObject.id) AS existingObjectIds
WHERE existing IS NULL
   OR (existing.predicate = $predicate
       AND existingSubjectIds = [$subjectId]
       AND existingObjectIds = [$objectId])
OPTIONAL MATCH (subjectEntity:Entity {id: $subjectId})
OPTIONAL MATCH (subjectSubject:Subject {id: $subjectId})
OPTIONAL MATCH (objectEntity:Entity {id: $objectId})
OPTIONAL MATCH (objectSubject:Subject {id: $objectId})
OPTIONAL MATCH (objectAuthority:AuthorityRecord {id: $objectId})
WITH coalesce(subjectEntity, subjectSubject) AS assertionSubject,
     coalesce(objectEntity, objectSubject, objectAuthority) AS assertionObject
WHERE assertionSubject IS NOT NULL AND assertionObject IS NOT NULL
MERGE (assertion:Assertion {id: $id})
ON CREATE SET
  assertion.label = $label,
  assertion.shortLabel = $shortLabel,
  assertion.predicate = $predicate,
  assertion.status = "proposed",
  assertion.assertedBy = $assertedBy
ON MATCH SET
  assertion.label = coalesce($label, assertion.label),
  assertion.shortLabel = coalesce($shortLabel, assertion.shortLabel)
MERGE (assertion)-[:ASSERTION_SUBJECT]->(assertionSubject)
MERGE (assertion)-[:ASSERTION_OBJECT]->(assertionObject)
RETURN assertion, assertionSubject, assertionObject;

// Attach a SourceObservation to an Assertion. `quotation` is the verbatim
// supporting span for passage evidence (null for structured evidence); it is
// fixed when the link is created.
MATCH (assertion:Assertion {id: $assertionId})
MATCH (observation:SourceObservation {id: $observationId})
MERGE (assertion)-[support:SUPPORTED_BY]->(observation)
ON CREATE SET support.quotation = $quotation
RETURN assertion, observation;

// Create or reuse a Proposal for an Assertion. A new Proposal is always
// `submitted`; status changes only through the decision operation below. A
// Proposal proposes exactly one Assertion; a retry naming another is refused.
// Rationale and version provenance are fixed at creation.
MATCH (assertion:Assertion {id: $assertionId})
OPTIONAL MATCH (existing:Proposal {id: $id})
OPTIONAL MATCH (existing)-[:PROPOSES]->(existingTarget:Assertion)
WITH assertion, existing, collect(existingTarget.id) AS existingTargetIds
WHERE existing IS NULL OR existingTargetIds = [$assertionId]
MERGE (proposal:Proposal {id: $id})
ON CREATE SET
  proposal.label = $label,
  proposal.shortLabel = $shortLabel,
  proposal.operation = $operation,
  proposal.status = "submitted",
  proposal.createdBy = $createdBy,
  proposal.rationale = $rationale,
  proposal.draftSchemaVersion = $draftSchemaVersion,
  proposal.predicateRegistryVersion = $predicateRegistryVersion,
  proposal.promptVersion = $promptVersion,
  proposal.modelId = $modelId,
  proposal.inquiryId = $inquiryId,
  proposal.relevance = $relevance,
  proposal.ambiguities = $ambiguities
ON MATCH SET
  proposal.label = coalesce($label, proposal.label),
  proposal.shortLabel = coalesce($shortLabel, proposal.shortLabel)
MERGE (proposal)-[:PROPOSES]->(assertion)
RETURN proposal, assertion;

// Create or reuse an addEvidence Proposal: new evidence for an existing
// Assertion. The evidence waits on PROPOSES_EVIDENCE and becomes SUPPORTED_BY
// only after acceptance. A retry naming another
// Assertion is refused.
MATCH (assertion:Assertion {id: $assertionId})
MATCH (observation:SourceObservation {id: $observationId})
OPTIONAL MATCH (existing:Proposal {id: $id})
OPTIONAL MATCH (existing)-[:PROPOSES]->(existingTarget:Assertion)
WITH assertion, observation, existing, collect(existingTarget.id) AS existingTargetIds
WHERE existing IS NULL
   OR (existing.operation = "addEvidence" AND existingTargetIds = [$assertionId])
MERGE (proposal:Proposal {id: $id})
ON CREATE SET
  proposal.label = $label,
  proposal.shortLabel = $shortLabel,
  proposal.operation = "addEvidence",
  proposal.status = "submitted",
  proposal.createdBy = $createdBy,
  proposal.rationale = $rationale,
  proposal.draftSchemaVersion = $draftSchemaVersion,
  proposal.predicateRegistryVersion = $predicateRegistryVersion,
  proposal.promptVersion = $promptVersion,
  proposal.modelId = $modelId,
  proposal.inquiryId = $inquiryId,
  proposal.relevance = $relevance,
  proposal.ambiguities = $ambiguities
MERGE (proposal)-[:PROPOSES]->(assertion)
MERGE (proposal)-[evidence:PROPOSES_EVIDENCE]->(observation)
ON CREATE SET evidence.quotation = $quotation
RETURN proposal, assertion, observation;

// Attach pending evidence to a submitted Proposal. Evidence on a Proposal is
// attached to the Assertion only when the Proposal is accepted.
MATCH (proposal:Proposal {id: $proposalId, status: "submitted"})-[:PROPOSES]->(:Assertion)
MATCH (observation:SourceObservation {id: $observationId})
MERGE (proposal)-[evidence:PROPOSES_EVIDENCE]->(observation)
ON CREATE SET evidence.quotation = $quotation
RETURN proposal, observation;

// Move a Proposal through its lifecycle and, on a decision, synchronize its
// Assertion.
//
//   submitted  -> validating | rejected | deferred
//   validating -> accepted | rejected | deferred
//   deferred   -> validating | rejected
//   accepted, rejected: terminal
//
// Accepting requires a `proposed` or `accepted` Assertion and accepts a
// `proposed` one. Rejecting rejects the Proposal's evidence and leaves the
// Assertion open, unless `rejectClaim` is true: then the Assertion, which must
// still be `proposed`, is rejected as well. A rejection needs a reason code:
// false, unsupported, malformed, underspecified, or superseded-by-model.
// Repeating the current status is an idempotent no-op that preserves the
// original decision metadata.
MATCH (proposal:Proposal {id: $proposalId})-[:PROPOSES]->(assertion:Assertion)
WITH proposal, assertion,
     proposal.status = $proposalStatus AS isRetry,
     {
       submitted: ["validating", "rejected", "deferred"],
       validating: ["accepted", "rejected", "deferred"],
       deferred: ["validating", "rejected"]
     } AS allowedTransitions
WHERE isRetry
   OR $proposalStatus IN coalesce(allowedTransitions[proposal.status], [])
WITH proposal, assertion, isRetry,
     NOT isRetry AND $proposalStatus IN ["accepted", "rejected"] AS isDecision
WHERE isRetry
   OR $proposalStatus <> "accepted"
   OR assertion.status IN ["proposed", "accepted"]
WITH proposal, assertion, isRetry, isDecision
WHERE isRetry
   OR NOT ($proposalStatus = "rejected" AND $rejectClaim)
   OR assertion.status = "proposed"
WITH proposal, assertion, isRetry, isDecision
WHERE isRetry
   OR $proposalStatus <> "rejected"
   OR $reason IN ["false", "unsupported", "malformed", "underspecified", "superseded-by-model"]
SET
  proposal.status = $proposalStatus,
  proposal.decidedAt = CASE WHEN isDecision THEN $decidedAt ELSE proposal.decidedAt END,
  proposal.decidedBy = CASE WHEN isDecision THEN $decidedBy ELSE proposal.decidedBy END,
  proposal.decisionBasis = CASE WHEN isDecision THEN $decisionBasis ELSE proposal.decisionBasis END,
  proposal.rejectedClaim = CASE
    WHEN isDecision AND $proposalStatus = "rejected" THEN $rejectClaim
    ELSE proposal.rejectedClaim
  END,
  proposal.decisionReason = CASE
    WHEN isDecision AND $proposalStatus = "rejected" THEN $reason
    ELSE proposal.decisionReason
  END,
  assertion.acceptedAt = CASE
    WHEN isDecision AND $proposalStatus = "accepted" AND assertion.status = "proposed" THEN $decidedAt
    ELSE assertion.acceptedAt
  END,
  assertion.status = CASE
    WHEN NOT isDecision THEN assertion.status
    WHEN $proposalStatus = "accepted" THEN "accepted"
    WHEN $proposalStatus = "rejected" AND $rejectClaim THEN "rejected"
    ELSE assertion.status
  END
RETURN proposal, assertion;

// Attach the pending evidence of an accepted Proposal to its Assertion.
// Idempotent; refused unless the Proposal is accepted. A Proposal stored
// before evidence became pending has none to attach and returns an empty list.
MATCH (proposal:Proposal {id: $proposalId, status: "accepted"})-[:PROPOSES]->(assertion:Assertion)
OPTIONAL MATCH (proposal)-[evidence:PROPOSES_EVIDENCE]->(observation:SourceObservation)
FOREACH (_ IN CASE WHEN observation IS NULL THEN [] ELSE [1] END |
  MERGE (assertion)-[support:SUPPORTED_BY]->(observation)
  ON CREATE SET support.quotation = evidence.quotation, support.addedByProposal = proposal.id
)
RETURN assertion, collect(observation.id) AS observationIds;

// Reopen a rejected Assertion so new evidence can be proposed for it. An
// explicit, recorded curator act; refused unless the Assertion is rejected.
MATCH (assertion:Assertion {id: $assertionId, status: "rejected"})
SET
  assertion.status = "proposed",
  assertion.reopenedAt = $decidedAt,
  assertion.reopenedBy = $decidedBy,
  assertion.reopenBasis = $decisionBasis
RETURN assertion;

// Supersede an Assertion by the Assertions that replace it. An explicit,
// recorded curator act with a reason code. Refused unless the Assertion is
// proposed or accepted and has no open Proposal (decide those first), every
// replacement exists, differs from it, and is proposed or accepted, and the
// reason is a known code. A retry naming the same replacements is a no-op that
// preserves the original decision metadata; any other retry is refused.
MATCH (old:Assertion {id: $assertionId})
OPTIONAL MATCH (old)-[:SUPERSEDED_BY]->(prior:Assertion)
WITH old, collect(prior.id) AS priorIds
OPTIONAL MATCH (replacement:Assertion)
WHERE replacement.id IN $replacementIds
  AND replacement.id <> old.id
  AND replacement.status IN ["proposed", "accepted"]
WITH old, priorIds, collect(replacement) AS replacements, old.status = "superseded" AS isRetry
WHERE size($replacementIds) > 0
  AND size(replacements) = size($replacementIds)
  AND $reason IN ["false", "unsupported", "malformed", "underspecified", "superseded-by-model"]
  AND (
    (isRetry AND size(priorIds) = size($replacementIds) AND all(id IN priorIds WHERE id IN $replacementIds))
    OR (old.status IN ["proposed", "accepted"]
        AND NOT EXISTS {
          MATCH (open:Proposal)-[:PROPOSES]->(old)
          WHERE open.status IN ["submitted", "validating", "deferred"]
        })
  )
SET
  old.supersededFrom = CASE WHEN isRetry THEN old.supersededFrom ELSE old.status END,
  old.supersededAt = CASE WHEN isRetry THEN old.supersededAt ELSE $decidedAt END,
  old.supersededBy = CASE WHEN isRetry THEN old.supersededBy ELSE $decidedBy END,
  old.supersedeBasis = CASE WHEN isRetry THEN old.supersedeBasis ELSE $decisionBasis END,
  old.supersedeReason = CASE WHEN isRetry THEN old.supersedeReason ELSE $reason END,
  old.status = "superseded"
FOREACH (item IN replacements | MERGE (old)-[:SUPERSEDED_BY]->(item))
RETURN old AS assertion, [item IN replacements | item.id] AS replacementIds;

// Retract an accepted Assertion: the curator finds an accepted claim wrong.
// An explicit, recorded act with a reason code; the claim becomes rejected and
// keeps its evidence links as audit history (reopen_assertion can return it to
// proposed). Refused unless the Assertion is accepted, has no open Proposal,
// and the reason is a known code. A retry is a no-op that preserves the
// original metadata.
MATCH (assertion:Assertion {id: $assertionId})
WITH assertion, assertion.status = "rejected" AND assertion.retractedAt IS NOT NULL AS isRetry
WHERE $reason IN ["false", "unsupported", "malformed", "underspecified", "superseded-by-model"]
  AND (
    isRetry
    OR (assertion.status = "accepted"
        AND NOT EXISTS {
          MATCH (open:Proposal)-[:PROPOSES]->(assertion)
          WHERE open.status IN ["submitted", "validating", "deferred"]
        })
  )
SET
  assertion.retractedAt = CASE WHEN isRetry THEN assertion.retractedAt ELSE $decidedAt END,
  assertion.retractedBy = CASE WHEN isRetry THEN assertion.retractedBy ELSE $decidedBy END,
  assertion.retractBasis = CASE WHEN isRetry THEN assertion.retractBasis ELSE $decisionBasis END,
  assertion.retractReason = CASE WHEN isRetry THEN assertion.retractReason ELSE $reason END,
  assertion.status = "rejected"
RETURN assertion;
