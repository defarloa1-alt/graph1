// D-029: Add SYS properties and relabel Policy, Threshold, PropertyMapping, KnowledgeDomain
// Run each section separately. Do not delete FederationRoot edges.

// ---------------------------------------------------------------------------
// 1. Add properties to Policy nodes
// ---------------------------------------------------------------------------
MATCH (p:Policy {name: 'LocalFirstCanonicalAuthorities'})
SET p.decision_table = 'D4_DETERMINE_federation_route',
    p.active = true,
    p.system = true;

MATCH (p:Policy {name: 'HubForDisambiguationOnly'})
SET p.decision_table = 'D5_DETERMINE_federation_scope_match',
    p.active = true,
    p.system = true;

MATCH (p:Policy {name: 'NoTemporalFacet'})
SET p.decision_table = 'D8_DETERMINE_SFA_facet_assignment',
    p.active = true,
    p.system = true;

MATCH (p:Policy {name: 'NoClassificationFacet'})
SET p.decision_table = 'D8_DETERMINE_SFA_facet_assignment',
    p.active = true,
    p.system = true;

MATCH (p:Policy {name: 'ApprovalRequired'})
SET p.decision_table = 'D10_DETERMINE_claim_promotion_eligibility',
    p.active = true,
    p.system = true;

// ---------------------------------------------------------------------------
// 2. Add properties to Threshold nodes
// ---------------------------------------------------------------------------
MATCH (t:Threshold {name: 'crosslink_ratio_split'})
SET t.decision_table = 'D12_DETERMINE_SubjectConcept_split_trigger',
    t.unit = 'ratio',
    t.rationale = 'Domain judgment: when crosslink ratio exceeds 30%, SubjectConcept is candidate for splitting',
    t.last_reviewed = '2026-02-25',
    t.system = true;

MATCH (t:Threshold {name: 'level2_child_overload'})
SET t.decision_table = 'D12_DETERMINE_SubjectConcept_split_trigger',
    t.unit = 'count',
    t.rationale = 'Domain judgment: when L2 node has >12 children, flag for review',
    t.last_reviewed = '2026-02-25',
    t.system = true;

MATCH (t:Threshold {name: 'facet_drift_alert'})
SET t.decision_table = 'D13_DETERMINE_SFA_drift_alert',
    t.unit = 'ratio',
    t.rationale = 'When SFA proposal set diverges from SCA baseline by >20%, flag before promotion',
    t.last_reviewed = '2026-02-25',
    t.system = true;

// ---------------------------------------------------------------------------
// 3. Add system: true to PropertyMapping nodes
// ---------------------------------------------------------------------------
MATCH (pm:PropertyMapping)
SET pm.system = true;

// ---------------------------------------------------------------------------
// 4. Add system: true to KnowledgeDomain, prepare for SYS_SubjectConceptRoot
// ---------------------------------------------------------------------------
MATCH (kd:KnowledgeDomain {qid: 'Q17167'})
SET kd.system = true;

// ---------------------------------------------------------------------------
// 5. Relabel: Policy -> SYS_Policy, Threshold -> SYS_Threshold, etc.
// Add new label first, then remove old
// ---------------------------------------------------------------------------
MATCH (p:Policy)
SET p:SYS_Policy
REMOVE p:Policy;

MATCH (t:Threshold)
SET t:SYS_Threshold
REMOVE t:Threshold;

MATCH (pm:PropertyMapping)
SET pm:SYS_PropertyMapping
REMOVE pm:PropertyMapping;

MATCH (kd:KnowledgeDomain)
SET kd:SYS_SubjectConceptRoot
REMOVE kd:KnowledgeDomain;
