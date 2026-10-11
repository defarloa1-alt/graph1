// Migration 001 (2026-10-11): evidence of open create Proposals becomes pending.
//
// Before this change a create Proposal attached its evidence to its proposed
// Assertion immediately, so rejecting weak evidence also closed the claim.
// Evidence now waits on PROPOSES_EVIDENCE until acceptance. This moves the
// evidence of still-open create Proposals whose Assertion is still proposed;
// accepted Assertions and decided Proposals are not touched. Idempotent.
MATCH (proposal:Proposal {operation: "create"})-[:PROPOSES]->(assertion:Assertion {status: "proposed"})
WHERE proposal.status IN ["submitted", "validating", "deferred"]
MATCH (assertion)-[support:SUPPORTED_BY]->(observation:SourceObservation)
MERGE (proposal)-[evidence:PROPOSES_EVIDENCE]->(observation)
ON CREATE SET evidence.quotation = support.quotation, evidence.migratedBy = "001-pending-evidence-for-open-proposals"
DELETE support
RETURN proposal.id AS proposal, observation.id AS observation;
