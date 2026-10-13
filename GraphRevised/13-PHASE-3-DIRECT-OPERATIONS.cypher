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
  assertion.category = $category,
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
  ON CREATE SET support.quotation = evidence.quotation, support.addedByProposal = proposal.id,
                support.qualifierQuotations = evidence.qualifierQuotations
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

// ---------------------------------------------------------------------------
// Qualified claims (22-CLAIM-QUALIFIERS.md)
// ---------------------------------------------------------------------------

// Create or reuse a qualified Assertion: one with a mode other than asserted,
// a context, a role, a time, or no object (a unary predicate). Like
// upsert_assertion, it is created `proposed`, and its predicate, endpoints,
// mode, qualifier links, and normalized time are fixed at creation: a retry
// that changes any of them is refused. Every named node must exist with the
// right kind: context an Event, attribution a Work.
OPTIONAL MATCH (existing:Assertion {id: $id})
OPTIONAL MATCH (existing)-[:ASSERTION_SUBJECT]->(existingSubject)
OPTIONAL MATCH (existing)-[:ASSERTION_OBJECT]->(existingObject)
OPTIONAL MATCH (existing)-[:ASSERTION_CONTEXT]->(existingContext)
OPTIONAL MATCH (existing)-[:ASSERTION_ROLE]->(existingRole)
OPTIONAL MATCH (existing)-[:ATTRIBUTED_TO]->(existingWork)
WITH existing,
     collect(DISTINCT existingSubject.id) AS subjectIds,
     collect(DISTINCT existingObject.id) AS objectIds,
     collect(DISTINCT existingContext.id) AS contextIds,
     collect(DISTINCT existingRole.id) AS roleIds,
     collect(DISTINCT existingWork.id) AS workIds
WHERE existing IS NULL
   OR (existing.predicate = $predicate
       AND coalesce(existing.mode, "asserted") = $mode
       AND subjectIds = [$subjectId]
       AND objectIds = CASE WHEN $objectId IS NULL THEN [] ELSE [$objectId] END
       AND contextIds = CASE WHEN $contextId IS NULL THEN [] ELSE [$contextId] END
       AND roleIds = CASE WHEN $roleId IS NULL THEN [] ELSE [$roleId] END
       AND workIds = CASE WHEN $attributedToId IS NULL THEN [] ELSE [$attributedToId] END
       AND coalesce(existing.timeEdtf, "") = coalesce($timeEdtf, "")
       AND coalesce(existing.timeCalendar, "") = coalesce($timeCalendar, "")
       AND coalesce(existing.timeSourceExpression, "") = coalesce($timeSourceExpression, "")
       AND coalesce(existing.timeRelativeOffset, "") = coalesce($timeRelativeOffset, ""))
OPTIONAL MATCH (subjectNode:Entity {id: $subjectId})
OPTIONAL MATCH (objectNode:Entity {id: $objectId})
OPTIONAL MATCH (contextNode:Entity {id: $contextId, kind: "Event"})
OPTIONAL MATCH (roleNode:Entity {id: $roleId})
OPTIONAL MATCH (workNode:Entity {id: $attributedToId, kind: "Work"})
WITH subjectNode, objectNode, contextNode, roleNode, workNode
WHERE subjectNode IS NOT NULL
  AND ($objectId IS NULL OR objectNode IS NOT NULL)
  AND ($contextId IS NULL OR contextNode IS NOT NULL)
  AND ($roleId IS NULL OR roleNode IS NOT NULL)
  AND (($mode = "asserted" AND $attributedToId IS NULL)
       OR ($mode = "attributed" AND workNode IS NOT NULL))
MERGE (assertion:Assertion {id: $id})
ON CREATE SET
  assertion.label = $label,
  assertion.shortLabel = $shortLabel,
  assertion.predicate = $predicate,
  assertion.category = $category,
  assertion.status = "proposed",
  assertion.assertedBy = $assertedBy,
  assertion.mode = $mode,
  assertion.contextBasis = $contextBasis,
  assertion.timeEdtf = $timeEdtf,
  assertion.timeCalendar = $timeCalendar,
  assertion.timePrecision = $timePrecision,
  assertion.timeApproximate = $timeApproximate,
  assertion.timeUncertain = $timeUncertain,
  assertion.timeSourceExpression = $timeSourceExpression,
  assertion.timeNormalizationBasis = $timeNormalizationBasis,
  assertion.timeRelativeOffset = $timeRelativeOffset,
  assertion.startEarliestJdn = $startEarliestJdn,
  assertion.startLatestJdn = $startLatestJdn,
  assertion.endEarliestJdn = $endEarliestJdn,
  assertion.endLatestJdn = $endLatestJdn
ON MATCH SET
  assertion.label = coalesce($label, assertion.label),
  assertion.shortLabel = coalesce($shortLabel, assertion.shortLabel)
MERGE (assertion)-[:ASSERTION_SUBJECT]->(subjectNode)
FOREACH (node IN CASE WHEN objectNode IS NULL THEN [] ELSE [objectNode] END |
  MERGE (assertion)-[:ASSERTION_OBJECT]->(node))
FOREACH (node IN CASE WHEN contextNode IS NULL THEN [] ELSE [contextNode] END |
  MERGE (assertion)-[:ASSERTION_CONTEXT]->(node))
FOREACH (node IN CASE WHEN roleNode IS NULL THEN [] ELSE [roleNode] END |
  MERGE (assertion)-[:ASSERTION_ROLE]->(node))
FOREACH (node IN CASE WHEN workNode IS NULL THEN [] ELSE [workNode] END |
  MERGE (assertion)-[:ATTRIBUTED_TO]->(node))
RETURN assertion;

// Record the qualifier quotations of one piece of pending evidence, each as
// "<role|time|context>:<verbatim span>". Fixed once set; refused unless the
// Proposal is submitted and already proposes that evidence.
MATCH (proposal:Proposal {id: $proposalId, status: "submitted"})
      -[evidence:PROPOSES_EVIDENCE]->(:SourceObservation {id: $observationId})
WHERE evidence.qualifierQuotations IS NULL OR evidence.qualifierQuotations = $qualifierQuotations
SET evidence.qualifierQuotations = $qualifierQuotations
RETURN proposal, evidence;

// Link an Assertion to every backbone Year its time touches: the derived
// navigation projection of its time qualifier. Never creates a Year; refused
// unless every Year exists.
MATCH (assertion:Assertion {id: $assertionId})
OPTIONAL MATCH (year:Year) WHERE year.year IN $years
WITH assertion, collect(year) AS years
WHERE size($years) > 0 AND size(years) = size($years)
FOREACH (year IN years | MERGE (assertion)-[:IN_YEAR]->(year))
RETURN assertion, [year IN years | year.year] AS years;

// Link a passage observation to the Work it is a passage of. One Work per
// observation: refused if it is already in another Work.
MATCH (observation:SourceObservation {id: $observationId, observationKind: "passage"})
MATCH (work:Entity {id: $workId, kind: "Work"})
OPTIONAL MATCH (observation)-[:IN_WORK]->(other:Entity)
WITH observation, work, collect(other.id) AS otherIds
WHERE all(id IN otherIds WHERE id = $workId)
MERGE (observation)-[:IN_WORK]->(work)
RETURN observation, work;

// Link a promoted asserted Assertion to the accepted attributed Assertions it
// rests on. Refused unless every source claim is accepted and attributed.
MATCH (promoted:Assertion {id: $assertionId})
WHERE coalesce(promoted.mode, "asserted") = "asserted"
OPTIONAL MATCH (source:Assertion {mode: "attributed", status: "accepted"})
WHERE source.id IN $sourceIds
WITH promoted, collect(source) AS sources
WHERE size($sourceIds) > 0 AND size(sources) = size($sourceIds)
FOREACH (source IN sources | MERGE (promoted)-[:PROMOTED_FROM]->(source))
RETURN promoted, [source IN sources | source.id] AS sourceIds;

// ---------------------------------------------------------------------------
// Annotations and curator transcriptions (23-NARRATIVE-AND-NOTES.md §3, §7)
// ---------------------------------------------------------------------------

// Create or reuse a curator transcription: a short quotation of a Work as the
// curator or a highlight import recorded it, with its edition and locator.
// Linked IN_WORK to its Work, which must exist. Source facts are fixed at
// creation; only display text and status may change.
MATCH (work:Entity {id: $workId, kind: "Work"})
MERGE (observation:SourceObservation {id: $id})
ON CREATE SET
  observation.label = $label,
  observation.shortLabel = $shortLabel,
  observation.observationKind = "transcription",
  observation.sourceSystem = $sourceSystem,
  observation.locator = $locator,
  observation.locatorType = $locatorType,
  observation.passageText = $passageText,
  observation.passageHash = $passageHash,
  observation.editorialNotes = [],
  observation.language = $language,
  observation.workTitle = $workTitle,
  observation.author = $author,
  observation.editionCitation = $editionCitation,
  observation.rights = $rights,
  observation.visibility = $visibility,
  observation.capturedBy = $capturedBy,
  observation.capturedAt = $capturedAt,
  observation.retrievedAt = $capturedAt,
  observation.contentHash = $contentHash,
  observation.rawPayloadUri = $rawPayloadUri,
  observation.status = "observed"
ON MATCH SET
  observation.label = coalesce($label, observation.label),
  observation.shortLabel = coalesce($shortLabel, observation.shortLabel)
MERGE (observation)-[:IN_WORK]->(work)
RETURN observation;

// Create or reuse an Annotation: commentary, never a claim. It may annotate a
// passage (with the verbatim quotation) and concerns one or more Entities.
// Refused if the passage or any concerned Entity is missing, or if a retry
// names a different set of concerned Entities. New Annotations are `flagged`.
OPTIONAL MATCH (existing:Annotation {id: $id})
OPTIONAL MATCH (existing)-[:CONCERNS]->(concerned:Entity)
WITH collect(concerned.id) AS existingConcerns, count(existing) > 0 AS exists
OPTIONAL MATCH (target:Entity) WHERE target.id IN $concerns
WITH existingConcerns, exists, collect(target) AS targets
OPTIONAL MATCH (observation:SourceObservation {id: $observationId})
WITH existingConcerns, exists, targets, observation
WHERE size($concerns) > 0
  AND size(targets) = size($concerns)
  AND ($observationId IS NULL OR observation IS NOT NULL)
  AND (NOT exists OR (size(existingConcerns) = size($concerns)
                      AND all(id IN existingConcerns WHERE id IN $concerns)))
  AND $visibility IN ["private", "team", "public"]
MERGE (annotation:Annotation {id: $id})
ON CREATE SET
  annotation.label = $label,
  annotation.kind = $kind,
  annotation.noteType = $noteType,
  annotation.note = $note,
  annotation.author = $author,
  annotation.visibility = $visibility,
  annotation.status = "flagged",
  annotation.createdAt = $createdAt
ON MATCH SET
  annotation.label = coalesce($label, annotation.label)
FOREACH (item IN CASE WHEN observation IS NULL THEN [] ELSE [observation] END |
  MERGE (annotation)-[link:ANNOTATES]->(item)
  ON CREATE SET link.quotation = $quotation)
FOREACH (item IN targets | MERGE (annotation)-[:CONCERNS]->(item))
RETURN annotation;

// Endorse, dismiss, or re-flag an Annotation, recording who and when.
MATCH (annotation:Annotation {id: $id})
WHERE $status IN ["flagged", "endorsed", "dismissed"]
SET annotation.status = $status, annotation.decidedBy = $decidedBy, annotation.decidedAt = $decidedAt
RETURN annotation;

// Delete an Annotation. Annotations are commentary and may be removed freely;
// the passages and Entities they pointed to are untouched.
MATCH (annotation:Annotation {id: $id})
WITH annotation, annotation.id AS deleted
DETACH DELETE annotation
RETURN deleted;

// ---------------------------------------------------------------------------
// Proposed entities (24-PERIODS-AND-TRANSFORMATION.md §3a; 23 §2)
// ---------------------------------------------------------------------------

// Decide a proposed Entity: accept it (provisional) or reject it (deprecated),
// recording who, when, and why. Refused unless the Entity is still proposed;
// repeating the same decision is a no-op that keeps the original record.
MATCH (entity:Entity {id: $id})
WHERE $status IN ["provisional", "deprecated"]
  AND (entity.status = "proposed" OR (entity.status = $status AND entity.decidedAt IS NOT NULL))
WITH entity, entity.status = $status AS isRetry
SET entity.decidedAt = CASE WHEN isRetry THEN entity.decidedAt ELSE $decidedAt END,
    entity.decidedBy = CASE WHEN isRetry THEN entity.decidedBy ELSE $decidedBy END,
    entity.decisionBasis = CASE WHEN isRetry THEN entity.decisionBasis ELSE $decisionBasis END,
    entity.status = $status
RETURN entity;

// ---------------------------------------------------------------------------
// Authority records (24-PERIODS-AND-TRANSFORMATION.md §7)
// ---------------------------------------------------------------------------

// Create or reuse a record observation: one entry of a reference dataset (a
// PeriodO period definition) as published by a Work. The passage text holds
// only the record's own wording, so quotations stay verbatim; the dataset's
// editorial notes are kept apart. Linked IN_WORK to its Work, which must
// exist. Source facts are fixed at creation.
MATCH (work:Entity {id: $workId, kind: "Work"})
MERGE (observation:SourceObservation {id: $id})
ON CREATE SET
  observation.label = $label,
  observation.shortLabel = $shortLabel,
  observation.observationKind = "record",
  observation.sourceSystem = $sourceSystem,
  observation.sourceEntityId = $sourceEntityId,
  observation.locator = $locator,
  observation.passageText = $passageText,
  observation.passageHash = $passageHash,
  observation.editorialNotes = $editorialNotes,
  observation.language = $language,
  observation.workTitle = $workTitle,
  observation.author = $author,
  observation.editionCitation = $editionCitation,
  observation.rights = $rights,
  observation.sourceUri = $sourceUri,
  observation.sourceRevision = $sourceRevision,
  observation.retrievedAt = $retrievedAt,
  observation.contentHash = $contentHash,
  observation.rawPayloadUri = $rawPayloadUri,
  observation.status = "observed"
ON MATCH SET
  observation.label = coalesce($label, observation.label),
  observation.shortLabel = coalesce($shortLabel, observation.shortLabel)
MERGE (observation)-[:IN_WORK]->(work)
RETURN observation;

// Set a Work's form (history, biography, play, novel, ...), one of the
// registry's work forms (25-LIVES-AND-PLAYGROUND.md section 6, decision 3).
// A claim attributed to a Work of a creative form is stored as imaginative,
// so once any claim is attributed to the Work its form is fixed: a retry
// with the same form succeeds, a different form is refused.
MATCH (work:Entity {id: $workId, kind: "Work"})
WHERE $form IN $allowedForms
  AND (work.form IS NULL OR work.form = $form OR NOT EXISTS { (:Assertion)-[:ATTRIBUTED_TO]->(work) })
SET work.form = $form
RETURN work;

// Create or reuse an AuthorityRecord and attach it to a Subject: a library
// subject heading (LCSH, FAST) with role subject_access. Keyed by (system,
// identifier) like Entity authority records; a retry under a different
// local ID is refused. The label comes from the authority's own record, so a
// code is never stored without its words.
MATCH (subject:Subject {id: $subjectId})
OPTIONAL MATCH (existing:AuthorityRecord {system: $system, identifier: $identifier})
WITH subject, existing
WHERE (existing IS NULL OR existing.id = $id) AND $label IS NOT NULL
MERGE (record:AuthorityRecord {system: $system, identifier: $identifier})
ON CREATE SET
  record.id = $id,
  record.label = $label,
  record.shortLabel = $shortLabel,
  record.description = $description,
  record.retrievedAt = $retrievedAt,
  record.sourceUri = $sourceUri,
  record.contentHash = $contentHash,
  record.rawPayloadUri = $rawPayloadUri,
  record.license = $license
ON MATCH SET
  record.label = coalesce($label, record.label),
  record.shortLabel = coalesce($shortLabel, record.shortLabel),
  record.retrievedAt = coalesce($retrievedAt, record.retrievedAt)
MERGE (subject)-[relationship:HAS_AUTHORITY_RECORD]->(record)
ON CREATE SET
  relationship.role = $role,
  relationship.relation = $relation,
  relationship.status = $linkStatus
RETURN subject, relationship, record;
