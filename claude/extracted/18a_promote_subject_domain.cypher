// ============================================================
// Script 18a — Promote SubjectDomain node (Roman Republic)
// ============================================================
// The existing SubjectDomain node (seed_qid=Q17167) was created
// by the DI pipeline as a scratch/working node. It has no label,
// no domain_id, no schema-compliant properties, and no structural
// edges. This script promotes it to a proper CCS backbone node.
//
// After this script the SubjectDomain:
//   - Has full schema properties (domain_id, label, temporal_scope,
//     primary_lcc, status, governed_by)
//   - OCCURS_DURING → Roman Republic Period node (Q17167)
//   - ALIGNED_WITH_LCC → 4 LCC ranges in graph
//   - COVERS_DOMAIN ← 5 backbone Disciplines
//
// SubjectConcepts will attach via HAS_SUBJECT_CONCEPT in script 18b.
// ============================================================

// ── 1. Set schema properties on existing SubjectDomain node ──────────────────
MATCH (sd:SubjectDomain {seed_qid: 'Q17167'})
SET sd.domain_id       = 'domain_roman_republic'
  , sd.label           = 'Roman Republic'
  , sd.description     = 'The Roman Republic period (-509 to -27), covering political, military, social, legal, religious, and cultural history of Rome from the expulsion of the kings to the principate of Augustus.'
  , sd.temporal_scope  = '-0509/-0027'
  , sd.geographic_scope = 'Italian peninsula and Roman territorial expansion'
  , sd.primary_lcc     = 'DG1-365, KJA2-3660, PA6000-6971'
  , sd.status          = 'active'
  , sd.governed_by     = 'ADR-020'
  , sd.updated_at      = date()
RETURN sd.domain_id AS domain_id, sd.label AS label, sd.status AS status;

// ── 2. Wire OCCURS_DURING → Roman Republic Period node ───────────────────────
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (rr:Period {qid: 'Q17167'})
MERGE (sd)-[r:OCCURS_DURING]->(rr)
SET r.basis      = 'domain_seed'
  , r.note       = 'Domain is bounded by the Roman Republic period (-509 to -27)'
RETURN sd.label AS domain, rr.label AS period;

// ── 3. Wire ALIGNED_WITH_LCC → primary LCC ranges ────────────────────────────
// DG1-365: Ancient Italy. Ancient Rome (broadest container)
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (lcc:LCC_Class {code: 'DG1-365'})
MERGE (sd)-[r:ALIGNED_WITH_LCC]->(lcc)
SET r.role = 'primary'
  , r.note = 'Core historical range for ancient Rome'
RETURN sd.label AS domain, lcc.label AS lcc_label, lcc.code AS lcc_code;

// DG21-190: Ancient Rome (General) — thematic cross-cutting topics
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (lcc:LCC_Class {code: 'DG21-190'})
MERGE (sd)-[r:ALIGNED_WITH_LCC]->(lcc)
SET r.role = 'thematic'
  , r.note = 'Cross-cutting thematic topics: constitution, army, law, religion, economy, society'
RETURN sd.label AS domain, lcc.label AS lcc_label, lcc.code AS lcc_code;

// KJA2-3660: Roman Law
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (lcc:LCC_Class {code: 'KJA2-3660'})
MERGE (sd)-[r:ALIGNED_WITH_LCC]->(lcc)
SET r.role = 'cross_class'
  , r.note = 'Roman law as living legal system — cross-class scatter from DG history range'
RETURN sd.label AS domain, lcc.label AS lcc_label, lcc.code AS lcc_code;

// KJA190-2152: Roman law primary sources
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (lcc:LCC_Class {code: 'KJA190-2152'})
MERGE (sd)-[r:ALIGNED_WITH_LCC]->(lcc)
SET r.role = 'cross_class'
  , r.note = 'Roman legal primary sources: Digest, Institutes, Twelve Tables'
RETURN sd.label AS domain, lcc.label AS lcc_label, lcc.code AS lcc_code;

// PA6000-6971: Roman literature
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (lcc:LCC_Class {code: 'PA6000-6971'})
MERGE (sd)-[r:ALIGNED_WITH_LCC]->(lcc)
SET r.role = 'cross_class'
  , r.note = 'Roman literary corpus — Cicero, Livy, Sallust, Caesar as primary sources'
RETURN sd.label AS domain, lcc.label AS lcc_label, lcc.code AS lcc_code;

// ── 4. Wire COVERS_DOMAIN ← backbone Disciplines ─────────────────────────────
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (d:Discipline) WHERE d.qid IN [
  'Q646206',  // history of Rome
  'Q783287',  // prosopography
  'Q495527',  // classical philology
  'Q23498',   // archaeology
  'Q134435'   // topography
]
MERGE (d)-[r:COVERS_DOMAIN]->(sd)
SET r.basis = 'domain_primary'
RETURN d.label AS discipline, sd.label AS domain;

// ── 5. Verify ─────────────────────────────────────────────────────────────────
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
OPTIONAL MATCH (sd)-[:OCCURS_DURING]->(p:Period)
OPTIONAL MATCH (sd)-[:ALIGNED_WITH_LCC]->(lcc:LCC_Class)
OPTIONAL MATCH (d:Discipline)-[:COVERS_DOMAIN]->(sd)
RETURN sd.label AS domain
     , sd.temporal_scope AS temporal
     , sd.primary_lcc AS lcc_ranges
     , count(DISTINCT lcc) AS lcc_edges
     , count(DISTINCT d) AS discipline_edges
     , p.label AS period;
