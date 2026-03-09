// ============================================================
// Script 18b — Rebuild SubjectConcepts under CCS rules
// ============================================================
// ADR-020 (CCS) governs. Two passes:
//
//   PASS 1: Delete 7 bio_bootstrap type-bucket SCs
//           These fail CCS validity (entity type containers,
//           no topic grounding, contaminated membership).
//           The 7 geo_bootstrap SCs are structurally valid —
//           kept but wired to SubjectDomain and given secondary facets.
//
//   PASS 2: Create 15 proper CCS SubjectConcepts (12 thematic + 3 period)
//           Each has:
//             - sc_id (stable internal key)
//             - lcsh_id or lcc_primary (authority tether)
//             - ANCHORS → LCC_Class nodes already in graph
//             - HAS_FACET {weight, is_primary} → Facet nodes
//             - HAS_SUBJECT_CONCEPT ← SubjectDomain
// ============================================================

// ── PASS 1a. Delete bio_bootstrap type-bucket SCs ────────────────────────────
MATCH (sc:SubjectConcept)
WHERE sc.source = 'bio_bootstrap'
DETACH DELETE sc
RETURN count(*) AS bio_bootstrap_deleted;

// ── PASS 1b. Wire surviving geo SCs to SubjectDomain ─────────────────────────
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MATCH (sc:SubjectConcept) WHERE sc.source = 'geo_bootstrap'
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
RETURN count(sc) AS geo_scs_wired_to_domain;

// ── PASS 2. Create 15 CCS SubjectConcepts ────────────────────────────────────
// Each MERGE uses sc_id as the stable key.
// lcsh_id anchors where known; lcc_primary records the primary LCC range.
// ─────────────────────────────────────────────────────────────────────────────

// SC-01: Republican Constitution & Political Institutions
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_constitution'})
SET sc.label        = 'Republican Constitution & Political Institutions'
  , sc.lcsh_id      = 'sh85115171'
  , sc.lcc_primary  = 'DG89'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'POLITICAL'})  MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'INTELLECTUAL'}) MERGE (sc)-[:HAS_FACET {weight:0.70, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'SOCIAL'})     MERGE (sc)-[:HAS_FACET {weight:0.40, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG89','DG91','DG95','DG99','DG101']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-02: Roman Army & Military Campaigns
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_military'})
SET sc.label        = 'Roman Army & Military Campaigns'
  , sc.lcsh_id      = 'sh85115130'
  , sc.lcc_primary  = 'DG105'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'MILITARY'})   MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'GEOGRAPHIC'}) MERGE (sc)-[:HAS_FACET {weight:0.60, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'BIOGRAPHIC'}) MERGE (sc)-[:HAS_FACET {weight:0.50, is_primary:false}]->(f3)
WITH sc
MATCH (f4:Facet {key:'SOCIAL'})     MERGE (sc)-[:HAS_FACET {weight:0.40, is_primary:false}]->(f4)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG105','DG109']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-03: Roman Economy, Finance & Trade
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_economy'})
SET sc.label        = 'Roman Economy, Finance & Trade'
  , sc.lcc_primary  = 'DG113'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'ECONOMIC'})   MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'SOCIAL'})     MERGE (sc)-[:HAS_FACET {weight:0.60, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'GEOGRAPHIC'}) MERGE (sc)-[:HAS_FACET {weight:0.50, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG113','DG115']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-04: Roman Society — Classes, Slavery & Family
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_society'})
SET sc.label        = 'Roman Society — Classes, Slavery & Family'
  , sc.lcc_primary  = 'DG59'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'SOCIAL'})       MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'BIOGRAPHIC'})   MERGE (sc)-[:HAS_FACET {weight:0.60, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'DEMOGRAPHIC'})  MERGE (sc)-[:HAS_FACET {weight:0.40, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG59','DG61','DG119','DG121','DG125','DG129','DG131']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-05: Roman Religion, Cults & Priesthoods
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_religion'})
SET sc.label        = 'Roman Religion, Cults & Priesthoods'
  , sc.lcc_primary  = 'DG171'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'RELIGIOUS'})  MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'SOCIAL'})     MERGE (sc)-[:HAS_FACET {weight:0.60, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'POLITICAL'})  MERGE (sc)-[:HAS_FACET {weight:0.40, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG65','DG69','DG171','DG175','DG179','DG183','DG187']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-06: Roman Law & Legal Institutions (cross-class: DG + KJA)
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_law'})
SET sc.label        = 'Roman Law & Legal Institutions'
  , sc.lcc_primary  = 'KJA2-3660'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.cross_class  = true
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'INTELLECTUAL'}) MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'POLITICAL'})    MERGE (sc)-[:HAS_FACET {weight:0.80, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'SOCIAL'})       MERGE (sc)-[:HAS_FACET {weight:0.50, is_primary:false}]->(f3)
WITH sc
MATCH (f4:Facet {key:'BIOGRAPHIC'})   MERGE (sc)-[:HAS_FACET {weight:0.40, is_primary:false}]->(f4)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG87','DG155','DG159','DG163','DG167','KJA2-3660','KJA190-2152']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-07: Roman Topography & Urban Space
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_topography'})
SET sc.label        = 'Roman Topography & Urban Space'
  , sc.lcc_primary  = 'DG41'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'GEOGRAPHIC'})     MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'ARCHAEOLOGICAL'}) MERGE (sc)-[:HAS_FACET {weight:0.70, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'ARTISTIC'})       MERGE (sc)-[:HAS_FACET {weight:0.30, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG41','DG42','DG45','DG51','DG55','DG78']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-08: Roman Historiography & Primary Sources
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_historiography'})
SET sc.label        = 'Roman Historiography & Primary Sources'
  , sc.lcc_primary  = 'DG35'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'INTELLECTUAL'})   MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'ARCHAEOLOGICAL'}) MERGE (sc)-[:HAS_FACET {weight:0.40, is_primary:false}]->(f2)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG31','DG35']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-09: Roman Material Culture, Art & Inscriptions
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_material_culture'})
SET sc.label        = 'Roman Material Culture, Art & Inscriptions'
  , sc.lcc_primary  = 'DG37'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'ARCHAEOLOGICAL'}) MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'ARTISTIC'})       MERGE (sc)-[:HAS_FACET {weight:0.70, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'LINGUISTIC'})     MERGE (sc)-[:HAS_FACET {weight:0.40, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG37','DG75','DG78','DG79']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-10: Roman Literature, Philosophy & Intellectual Life (cross-class: DG + PA)
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_literature'})
SET sc.label        = 'Roman Literature, Philosophy & Intellectual Life'
  , sc.lcc_primary  = 'PA6000-6971'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.cross_class  = true
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'INTELLECTUAL'}) MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'ARTISTIC'})     MERGE (sc)-[:HAS_FACET {weight:0.70, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'LINGUISTIC'})   MERGE (sc)-[:HAS_FACET {weight:0.50, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG83','DG143','DG147','DG151','PA6000-6971']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-11: Roman Diplomacy & Foreign Relations
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_diplomacy'})
SET sc.label        = 'Roman Diplomacy & Foreign Relations'
  , sc.lcc_primary  = 'DG21-190'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'DIPLOMATIC'})  MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'MILITARY'})    MERGE (sc)-[:HAS_FACET {weight:0.60, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'GEOGRAPHIC'})  MERGE (sc)-[:HAS_FACET {weight:0.50, is_primary:false}]->(f3)
WITH sc
MATCH (f4:Facet {key:'POLITICAL'})   MERGE (sc)-[:HAS_FACET {weight:0.40, is_primary:false}]->(f4)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG21-190']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-12: Roman Science, Technology & Medicine
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_science'})
SET sc.label        = 'Roman Science, Technology & Medicine'
  , sc.lcc_primary  = 'DG135'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'SCIENTIFIC'})     MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'TECHNOLOGICAL'})  MERGE (sc)-[:HAS_FACET {weight:0.70, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'SOCIAL'})         MERGE (sc)-[:HAS_FACET {weight:0.30, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG135','DG139']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// ── Period sub-divisions ──────────────────────────────────────────────────────

// SC-13: Early Republic (509–264 BC)
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_early_republic'})
SET sc.label        = 'Early Republic (509–264 BC)'
  , sc.lcc_primary  = 'DG221-239'
  , sc.lcsh_id      = 'sh85115114'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.period_start = -509
  , sc.period_end   = -264
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'POLITICAL'})  MERGE (sc)-[:HAS_FACET {weight:0.80, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'MILITARY'})   MERGE (sc)-[:HAS_FACET {weight:0.70, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'SOCIAL'})     MERGE (sc)-[:HAS_FACET {weight:0.50, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG221-239']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-14: Middle Republic (264–133 BC)
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_middle_republic'})
SET sc.label        = 'Middle Republic (264–133 BC)'
  , sc.lcc_primary  = 'DG241-259'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.period_start = -264
  , sc.period_end   = -133
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'MILITARY'})   MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'POLITICAL'})  MERGE (sc)-[:HAS_FACET {weight:0.70, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'GEOGRAPHIC'}) MERGE (sc)-[:HAS_FACET {weight:0.60, is_primary:false}]->(f3)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG241-259']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// SC-15: Late Republic (133–27 BC)
MERGE (sc:SubjectConcept {subject_id: 'sc_rr_late_republic'})
SET sc.label        = 'Late Republic (133–27 BC)'
  , sc.lcc_primary  = 'DG261-269'
  , sc.source       = 'ccs_bootstrap'
  , sc.domain       = 'roman_republic'
  , sc.period_start = -133
  , sc.period_end   = -27
  , sc.created_at   = date()
WITH sc
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})
MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
WITH sc
MATCH (f1:Facet {key:'POLITICAL'})  MERGE (sc)-[:HAS_FACET {weight:0.90, is_primary:true}]->(f1)
WITH sc
MATCH (f2:Facet {key:'BIOGRAPHIC'}) MERGE (sc)-[:HAS_FACET {weight:0.80, is_primary:false}]->(f2)
WITH sc
MATCH (f3:Facet {key:'MILITARY'})   MERGE (sc)-[:HAS_FACET {weight:0.60, is_primary:false}]->(f3)
WITH sc
MATCH (f4:Facet {key:'SOCIAL'})     MERGE (sc)-[:HAS_FACET {weight:0.50, is_primary:false}]->(f4)
WITH sc
MATCH (lcc:LCC_Class) WHERE lcc.code IN ['DG261-269']
MERGE (sc)-[:ANCHORS]->(lcc)
RETURN sc.label AS created, count(lcc) AS lcc_anchors;

// ── Verify ────────────────────────────────────────────────────────────────────
MATCH (sd:SubjectDomain {domain_id: 'domain_roman_republic'})-[:HAS_SUBJECT_CONCEPT]->(sc:SubjectConcept)
OPTIONAL MATCH (sc)-[:HAS_FACET]->(f:Facet)
OPTIONAL MATCH (sc)-[:ANCHORS]->(lcc:LCC_Class)
RETURN sc.label AS subject_concept
     , sc.source AS source
     , count(DISTINCT f) AS facets
     , count(DISTINCT lcc) AS lcc_anchors
ORDER BY sc.source, sc.label;
