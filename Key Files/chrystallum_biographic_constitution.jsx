import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — BIOGRAPHIC PROSOPOGRAPHICAL CONSTITUTION                    ║
// ║  Integration: DPRR (identity) → Wikidata (bridge + enrichment)            ║
// ║  Self-describing: data constants below are mirrored as SYS_ nodes in Neo4j ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  dprr:"#C0392B", wikidata:"#006699", lcnaf:"#8E44AD",
  neo:"#00C2A8", cypher:"#B5860D",
  political:"#E74C3C", military:"#2980B9", religious:"#9B59B6",
  legal:"#F39C12", intellectual:"#1ABC9C", economic:"#27AE60",
  pass:"#2ECC71", warn:"#F5A623", fail:"#E74C3C",
};

const STATUS_COL = { operational:C.pass, planned:C.warn, bootstrap:C.warn, blocked:C.fail };

// ══════════════════════════════════════════════════════════════════════════════
// BIO BACKBONE — DPRR Person nodes as identity layer
// ══════════════════════════════════════════════════════════════════════════════
const BIO_BACKBONE = {
  definition: "Person nodes with dprr_id — the Roman prosopographical core",
  identity_source: "Digital Prosopography of the Roman Republic (DPRR)",
  enrichment_source: "Wikidata (authority IDs, occupation, gender, citizenship, temporal)",
  total_persons: 5248,
  with_dprr: 4685,
  with_qid: 3336,
  with_both: 2773,
  sc_candidates: {
    total: 848,
    pct: "16.2%",
    principle: "Entity with ≥1 bibliographic authority ID (VIAF, GND, LoC, FAST, ISNI, BnF) is recognized by the bibliographic control universe → SubjectConcept candidate",
    biblio_distribution: [
      { biblio_ids:0, count:4400, note:"Not a subject — just a graph node" },
      { biblio_ids:1, count:62 }, { biblio_ids:2, count:313 },
      { biblio_ids:3, count:95 }, { biblio_ids:4, count:86 },
      { biblio_ids:5, count:80 }, { biblio_ids:6, count:65 },
      { biblio_ids:7, count:83 }, { biblio_ids:8, count:64 },
    ],
    avg_biblio_ids: 3.8,
    candidate_facets: ["BIOGRAPHIC"],
    script: "scripts/neo4j/compute_sc_candidates.py",
  },
  query: "MATCH (p:Person) RETURN p",
};

// ══════════════════════════════════════════════════════════════════════════════
// DESIGN PRINCIPLES — agent reads these to understand biographic architecture
// ══════════════════════════════════════════════════════════════════════════════
const PRINCIPLES = [
  { id:"BP-01", name:"Person is prosopographical identity",
    desc:"A Person node represents a historical individual confirmed by at least one prosopographical authority (DPRR, Wikidata, LGPN). The node persists through conflicting identifications — disputed existence is a property, not a reason to delete." },
  { id:"BP-02", name:"Two sources, two roles",
    desc:"DPRR provides the prosopographical identity layer: positions held, temporal bounds, political career structure. Wikidata bridges to global authority IDs (VIAF, GND, LoC, ISNI) and enriches with occupation, gender, citizenship." },
  { id:"BP-03", name:"Positions are temporal edges, not properties",
    desc:"A person's career is encoded as POSITION_HELD edges with year_start/year_end to Position nodes. This is the temporal backbone — not flat strings. 7,342 position edges cover 3,448 persons with dated careers spanning -509 to -13." },
  { id:"BP-04", name:"Occupation classifies, position narrates",
    desc:"Wikidata occupation (P106) is the classification signal — it routes persons to SubjectConcepts. DPRR POSITION_HELD provides the temporal narrative — when they held which offices. Together they give both the 'what kind' and the 'when exactly'." },
  { id:"BP-05", name:"MEMBER_OF has temporal and multiplicity dimensions",
    desc:"A person belongs to multiple SubjectConcepts simultaneously (political + military + religious). Each MEMBER_OF carries: rank (primary/secondary/inferred), earliest_year, latest_year, position_count. Derived from POSITION_HELD edges, not just occupation strings." },
];

// ══════════════════════════════════════════════════════════════════════════════
// NODE TYPE SCHEMAS — maps to SYS_NodeType in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const NODE_TYPES = [
  { name:"Person", status:"operational", color:C.dprr,
    desc:"Prosopographical identity anchor for a historical individual. Confirmed by DPRR and/or Wikidata.",
    required_props:[
      { name:"entity_id",    type:"string",  pattern:"per_{dprr_id} or per_{qid}", desc:"Unique identifier" },
      { name:"label",        type:"string",  desc:"Current preferred display name (Latin praenomen + nomen + cognomen)" },
    ],
    optional_props:[
      { name:"qid",               type:"string",  pattern:"Q[0-9]+", desc:"Wikidata QID (3,336 Persons)" },
      { name:"dprr_id",           type:"string",  desc:"DPRR prosopographical ID (4,685 Persons)" },
      { name:"dprr_uri",          type:"string",  desc:"Full DPRR URI" },
      { name:"label_latin",       type:"string",  desc:"Canonical Latin name form" },
      { name:"label_dprr",        type:"string",  desc:"DPRR display name" },
      { name:"label_sort",        type:"string",  desc:"Sort key (nomen-first)" },
      { name:"birth_year",        type:"integer", desc:"Year of birth (negative for BCE). 2,114 Persons." },
      { name:"death_year",        type:"integer", desc:"Year of death (negative for BCE). 1,820 Persons." },
      { name:"floruit_start",     type:"integer", desc:"DPRR-derived start of active career" },
      { name:"floruit_end",       type:"integer", desc:"DPRR-derived end of active career" },
      { name:"gender",            type:"string",  desc:"Wikidata P21 (male/female). 3,336 Persons." },
      { name:"occupation",        type:"string",  desc:"Wikidata P106 pipe-separated labels. 2,521 Persons. E.g. 'politician|military personnel'" },
      { name:"citizenship",       type:"string",  desc:"Wikidata P27 pipe-separated labels. 3,147 Persons." },
      { name:"instance_of",       type:"string",  desc:"Wikidata P31 — almost always 'human'. 3,336 Persons." },
      { name:"viaf_id",           type:"string",  desc:"VIAF cluster ID (P214). 847 Persons." },
      { name:"gnd_id",            type:"string",  desc:"GND ID (P227). 698 Persons." },
      { name:"loc_authority_id",  type:"string",  desc:"LoC authority ID (P244). 218 Persons. n-prefix = LCNAF." },
      { name:"lcnaf_id",          type:"string",  desc:"LCNAF ID (legacy path). 176 Persons." },
      { name:"fast_id",           type:"string",  desc:"FAST ID (P2163). 246 Persons." },
      { name:"isni",              type:"string",  desc:"ISNI (P213). 467 Persons." },
      { name:"bnf_id",            type:"string",  desc:"BnF ID (P268). 189 Persons." },
      { name:"idref_id",          type:"string",  desc:"IdRef ID (P269). 280 Persons." },
      { name:"nli_id",            type:"string",  desc:"NLI ID (P949). 79 Persons." },
      { name:"federation_score",  type:"integer", desc:"D22 v1 score (0-100). 11 rules: qid(20)+dprr(15)+loc(10)+viaf(10)+gnd(5)+isni(5)+temporal(10)+occupation(10)+instance_of(5)+gender(5)+citizenship(5)" },
      { name:"federation_score_version", type:"string", desc:"Scoring rubric version (D22_v1_11rule)" },
      { name:"birth_place_qid",   type:"string",  desc:"QID of birth place (for BORN_IN_PLACE edge)" },
      { name:"death_place_qid",   type:"string",  desc:"QID of death place (for DIED_IN_PLACE edge)" },
    ],
    current_count: 5248,
    enrichment_stats: {
      with_qid: 3336, with_dprr: 4685, with_viaf: 847, with_gnd: 698,
      with_loc: 218, with_fast: 246, with_isni: 467, with_bnf: 189,
      with_occupation: 2521, with_gender: 3336, with_citizenship: 3147,
      with_birth_year: 2114, with_death_year: 1820, scored: 5248,
    },
  },
  { name:"Position", status:"operational", color:C.political,
    desc:"Roman political, military, or religious office. From DPRR. 171 distinct positions with label_name enrichment.",
    required_props:[
      { name:"label",      type:"string", desc:"Position name (e.g. consul, praetor, tribunus plebis)" },
    ],
    optional_props:[
      { name:"label_name", type:"string", desc:"Enriched full name from DPRR Turtle dump" },
      { name:"dprr_id",    type:"string", desc:"DPRR position identifier" },
    ],
    current_count: 171,
    note: "All 171 positions enriched with label_name from static JSON (scripts/federation/dprr_office_labels.json). Formerly 'Office' — relabeled to Position for P39 alignment.",
  },
  { name:"ClassificationAnchor", status:"operational", color:C.lcnaf,
    desc:"Bibliographic classification coordinate for a Person with an LCNAF authority ID. Bridges prosopographical backbone to LoC/VIAF/GND authority system.",
    required_props:[
      { name:"qid",          type:"string",  pattern:"Q[0-9]+", desc:"Wikidata QID (same as owning Person)" },
      { name:"label",        type:"string",  desc:"Person label" },
      { name:"anchor_type",  type:"string",  desc:"Always 'BiographicPerson'" },
      { name:"federation",   type:"string",  desc:"Always 'wikidata'" },
    ],
    optional_props:[
      { name:"lcnaf_id",     type:"string", desc:"LCNAF name authority ID (n-prefix)" },
      { name:"fast_id",      type:"string", desc:"FAST ID" },
      { name:"gnd_id",       type:"string", desc:"GND ID" },
      { name:"source_type",  type:"string", desc:"Always 'biographic_lcnaf'" },
    ],
    current_count: 394,
    note: "Created from Person nodes with loc_authority_id or lcnaf_id + qid. 394 persons have LoC authority IDs.",
  },
  { name:"SubjectConcept", status:"operational", color:"#9B59B6",
    desc:"Biographic subject classification node. 7 concepts bootstrapped from occupation analysis. Persons wired via MEMBER_OF with temporal and multiplicity dimensions.",
    required_props:[
      { name:"subject_id",    type:"string", desc:"e.g. BIO_POLITICAL_FIGURES, BIO_MILITARY_FIGURES" },
      { name:"label",         type:"string", desc:"Human-readable label" },
      { name:"seed_domain",   type:"string", desc:"Always 'biographic' for these" },
    ],
    optional_props:[
      { name:"scope_note",    type:"string", desc:"Description of what this concept covers" },
      { name:"lcsh_heading",  type:"string", desc:"Canonical LCSH heading" },
      { name:"lcsh_id",       type:"string", desc:"LCSH ID" },
      { name:"lcc_primary",   type:"string", desc:"Primary LCC class" },
      { name:"entity_count",  type:"integer", desc:"Number of MEMBER_OF Person nodes" },
    ],
    current_count: 7,
    subjects: [
      { id:"BIO_POLITICAL_FIGURES",   members:3035, anchors:35,  label:"Political Figures & Magistrates",
        temporal:"2,804 primary, 26 secondary — position-derived temporal bounds" },
      { id:"BIO_GENERAL_PERSONS",     members:2807, anchors:33,  label:"General Biographical Persons",
        temporal:"All inferred — no position data for temporal bounds" },
      { id:"BIO_MILITARY_FIGURES",    members:1884, anchors:85,  label:"Military Figures & Commanders",
        temporal:"712 primary, 494 secondary — many secondary to political" },
      { id:"BIO_ECONOMIC_FIGURES",    members:385,  anchors:5,   label:"Economic & Financial Figures",
        temporal:"241 primary, 126 secondary — moneyers often secondary to political career" },
      { id:"BIO_INTELLECTUAL_FIGURES", members:323, anchors:219, label:"Writers, Philosophers & Scholars",
        temporal:"All inferred — Wikidata-only population, no DPRR position data" },
      { id:"BIO_RELIGIOUS_FIGURES",   members:324,  anchors:4,   label:"Religious & Sacerdotal Figures",
        temporal:"95 primary, 197 secondary — priesthoods often held alongside political offices" },
      { id:"BIO_LEGAL_FIGURES",       members:78,   anchors:13,  label:"Legal Scholars & Jurists",
        temporal:"15 position-derived, 63 inferred from occupation" },
    ],
    note: "8,836 MEMBER_OF edges total (many-to-many). 4,710 enriched with temporal bounds from POSITION_HELD. rank: primary(3,852) / secondary(858) / inferred(4,126).",
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// RELATIONSHIP TYPES — maps to SYS_RelationshipType in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const REL_TYPES = [
  // ── Core prosopographical edges ──
  { name:"POSITION_HELD",     source:"Person",  target:"Position", status:"operational",
    desc:"Person held this office. Temporal: year_start, year_end. 7,342 edges across 3,448 persons (-509 to -13 BCE).",
    category:"prosopographical", temporal:true, current_count:7342 },
  { name:"PART_OF_GENS",      source:"Person",  target:"Gens",     status:"operational",
    desc:"Person belongs to this Roman gens/clan", category:"prosopographical", temporal:false },
  // ── Cross-backbone (Person↔Place) ──
  { name:"BORN_IN_PLACE",     source:"Person",  target:"Place",    status:"operational",
    desc:"Person born at this place", category:"biographic", temporal:false, current_count:1635 },
  { name:"DIED_IN_PLACE",     source:"Person",  target:"Place",    status:"operational",
    desc:"Person died at this place", category:"biographic", temporal:false, current_count:313 },
  { name:"BURIED_AT",         source:"Person",  target:"Place",    status:"operational",
    desc:"Person buried at this place", category:"biographic", temporal:false, current_count:15 },
  // ── Classification (Person↔SubjectConcept) ──
  { name:"MEMBER_OF",         source:"Person",  target:"SubjectConcept", status:"operational",
    desc:"Person classified into SubjectConcept. Props: rank (primary/secondary/inferred), earliest_year, latest_year, position_count.",
    category:"classification", temporal:true, current_count:8836 },
  { name:"POSITIONED_AS",     source:"Person",  target:"ClassificationAnchor", status:"operational",
    desc:"Person self-anchored to ClassificationAnchor (hops=0, confidence=1.0)",
    category:"classification", temporal:false, current_count:394 },
  { name:"PROVIDES_ANCHOR",   source:"SYS_FederationSource", target:"ClassificationAnchor", status:"operational",
    desc:"Wikidata federation source provides this classification anchor",
    category:"federation", temporal:false, current_count:394 },
  { name:"ANCHORS",           source:"ClassificationAnchor", target:"SubjectConcept", status:"operational",
    desc:"ClassificationAnchor grounds a SubjectConcept via occupation-derived mapping",
    category:"classification", temporal:false, current_count:394 },
  { name:"HAS_PRIMARY_FACET", source:"SubjectConcept", target:"Facet", status:"operational",
    desc:"SubjectConcept belongs to Biographic facet",
    category:"classification", temporal:false, current_count:7 },
  { name:"MANAGES_FACET",     source:"SYS_SFAAgent", target:"Facet", status:"operational",
    desc:"Biographic SFA agent manages the Biographic facet",
    category:"system", temporal:false, current_count:1 },
];

// ══════════════════════════════════════════════════════════════════════════════
// FEDERATION SOURCES — biographic layer
// ══════════════════════════════════════════════════════════════════════════════
const BIO_FED = [
  { id:"dprr", name:"DPRR", color:C.dprr, status:"operational",
    role:"identity_layer",
    desc:"Digital Prosopography of the Roman Republic. Master prosopographical authority for Roman political figures. Provides positions held with temporal bounds, inter-personal relationships, gens membership.",
    endpoint:"https://romanrepublic.ac.uk/",
    provides:["Person nodes (4,685 with dprr_id)", "Position nodes (171 office types)", "POSITION_HELD edges (7,342 with year_start/year_end)", "PART_OF_GENS edges", "floruit_start/floruit_end derived temporal bounds"],
    current_state:"4,685 Person nodes imported from DPRR Turtle dump. 171 Position nodes with enriched label_name. 7,342 POSITION_HELD edges with year_start/year_end backfilled from dprr_post_years.json.",
    ingestion_notes:"Static import from Turtle dump (gillisandrew/dprr-mcp). SPARQL endpoint blocked. Post-import: year_start/year_end backfilled from scripts/federation/dprr_post_years.json (9,807 entries, range -509 to -13)." },
  { id:"wikidata_bio", name:"Wikidata (biographic)", color:C.wikidata, status:"operational",
    role:"bridge_layer",
    desc:"Universal knowledge bridge for persons. Cross-references (VIAF, GND, LoC, ISNI, FAST, BnF). Occupation, gender, citizenship classification. Birth/death years where DPRR lacks them.",
    endpoint:"https://www.wikidata.org/w/api.php",
    provides:["External authority IDs (VIAF, GND, LoC, FAST, ISNI, BnF, IdRef, NLI)", "P106 occupation classification", "P21 gender", "P27 citizenship", "P31 instance_of", "P569/P570 birth/death years", "ClassificationAnchor nodes (LCNAF-grounded)"],
    current_state:"3,336 Persons with QID. All 3,336 enriched (2026-03-08). VIAF: 847 | GND: 698 | LoC: 218 | FAST: 246 | ISNI: 467 | BnF: 189 | occupation: 2,521 | gender: 3,336 | citizenship: 3,147 | birth_year: +379 fills | death_year: +355 fills.",
    ingestion_notes:"Enrichment via Wikidata API (wbgetentities, 50/batch). Script: enrich_person_external_ids.py. Item-valued properties (P31, P106, P27) resolved to labels via batch fetch. 394 ClassificationAnchors from LCNAF IDs." },
];

// ══════════════════════════════════════════════════════════════════════════════
// RULES — biographic domain rules
// ══════════════════════════════════════════════════════════════════════════════
const BIO_RULES = [
  { id:"BR-01", name:"D22 Federation Scoring (11-rule)",
    facets:["Biographic"],
    trigger:"Person node exists (any Person, scored on write/rescore)",
    action:"Apply D22_SCORE_person_federation: qid(+20) + dprr(+15) + loc(+10) + viaf(+10) + gnd(+5) + isni(+5) + temporal(+10) + occupation(+10) + instance_of(+5) + gender(+5) + citizenship(+5) = max 100.",
    rationale:"Quantifies Person data richness. DPRR-weight (15) second only to QID (20) because DPRR is the domain authority. Library authority IDs (LoC, VIAF) weighted for classification anchor potential." },
  { id:"BR-02", name:"LCNAF Classification Anchor Wiring",
    facets:["Biographic"],
    trigger:"Person has loc_authority_id or lcnaf_id (n-prefix LCNAF name authority) AND qid",
    action:"Create ClassificationAnchor node. Wire POSITIONED_AS (Person→Anchor, hops=0, confidence=1.0). Wire PROVIDES_ANCHOR (Wikidata→Anchor).",
    rationale:"394 Persons have LCNAF authority IDs — they exist in the Library of Congress authority file. These anchors bridge prosopography to the bibliographic classification system." },
  { id:"BR-03", name:"SubjectConcept Membership by Occupation",
    facets:["Biographic"],
    trigger:"Person has occupation property (from Wikidata P106 enrichment)",
    action:"Pattern-match occupation labels against 7 SubjectConcept definitions. Wire MEMBER_OF to matching SubjectConcepts (many-to-many). Unmatched Persons fall back to BIO_GENERAL_PERSONS.",
    rationale:"Occupation-based classification routes 2,441 Persons into 6 specialized categories. The 2,807 fallback includes DPRR-only persons without Wikidata occupation data." },
  { id:"BR-04", name:"Temporal MEMBER_OF Enrichment from POSITION_HELD",
    facets:["Biographic"],
    trigger:"Person has POSITION_HELD edges with year_start",
    action:"Map each Position to SubjectConcepts. Compute per-SC: earliest_year, latest_year, position_count, rank (primary = most positions in that SC). Ensure MEMBER_OF edges exist. Set rank='inferred' on non-temporal memberships.",
    rationale:"A flat occupation string like 'politician|military personnel' loses the temporal story. Caesar was military -71 to -44, political -81 to -44, religious -85 to -47. The MEMBER_OF temporal properties capture this career trajectory." },
  { id:"BR-05", name:"Position-to-SubjectConcept Mapping",
    facets:["Biographic"],
    trigger:"POSITION_HELD edge exists",
    action:"Map Position label to SubjectConcept(s): consul→POLITICAL, tribunus militum→MILITARY, augur→RELIGIOUS, monetalis→ECONOMIC, iudex quaestionis→POLITICAL+LEGAL. Unmapped positions default to POLITICAL.",
    rationale:"60+ position types are explicitly mapped. Some positions cross categories (tribunus militum consulari potestate = MILITARY + POLITICAL). 115 rare/variant positions defaulted to POLITICAL as the safest assumption for Roman magistracies." },
  { id:"BR-06", name:"Cross-Backbone Spatial Wiring",
    facets:["Biographic","Geographic"],
    trigger:"Person has birth_place_qid or death_place_qid",
    action:"MATCH Place node with matching QID. MERGE BORN_IN_PLACE or DIED_IN_PLACE. 1,635 born-in + 313 died-in = 1,963 cross-backbone edges.",
    rationale:"These edges bridge the biographic and geographic backbones. A query like 'all persons born in Tusculum' traverses from Place to Person via BORN_IN_PLACE." },
];

// ══════════════════════════════════════════════════════════════════════════════
// SFA AGENT & CLASSIFICATION INFRASTRUCTURE
// ══════════════════════════════════════════════════════════════════════════════
const BIO_SFA = {
  agent_id: "sfa_biographic",
  label: "Biographic SFA",
  status: "bootstrap",
  facet: "Biographic",
  entity_types: ["Person"],
  description: "Subject Facet Agent for the Biographic facet. Manages Person entities, prosopographical data, and biographical classification anchors. Covers 7 SubjectConcepts with temporal MEMBER_OF from POSITION_HELD edges.",
  decision_tables: [
    { id:"D22_SCORE_person_federation", rules:11, max_score:100,
      desc:"Component scoring rubric for Person nodes. Created 2026-03-08 from Wikidata enrichment survey of 3,336 entities.",
      dimensions:["wikidata_alignment(20)","domain_authority(15)","library_authority(10)","crosswalk_authority(20)","temporal_bounds(10)","class_signal(10)","type_signal(5)","demographic_signal(5)","affiliation_signal(5)"] },
  ],
  classification_pipeline: {
    step_1: "enrich_person_external_ids.py — bulk Wikidata API harvest of authority IDs, occupation, gender, citizenship for Persons with QIDs",
    step_2: "create_d22_person_scoring.py — create D22 decision table (11 rules) + rescore all 5,248 Persons",
    step_3: "bootstrap_bio_subject_concepts.py — create ClassificationAnchors (394), SubjectConcepts (7), wire MEMBER_OF, register SFA, enrich Facet",
    step_4: "enrich_bio_membership_temporal.py — derive temporal/multiplicity dimensions on MEMBER_OF from 7,342 POSITION_HELD edges",
    step_5: "compute_sc_candidates.py — flag 848 Persons as sc_candidate=true based on biblio authority ID presence, route to BIOGRAPHIC facet",
  },
  coverage: {
    total_persons: 5248,
    classified_persons: 5248,
    with_temporal_membership: 3448,
    without_temporal: 1800,
    without_temporal_reason: "DPRR-only or Wikidata-only persons without POSITION_HELD edges. Classified by occupation or fallback.",
    classification_anchors: 394,
    subject_concepts: 7,
    member_of_edges: 8836,
    member_of_temporal: 4710,
    member_of_primary: 3852,
    member_of_secondary: 858,
    member_of_inferred: 4126,
  },
  score_distribution: {
    avg: 48.6, min: 15, max: 100,
    perfect_score: 124,
    bands: [
      { range:"15", count:1912, desc:"DPRR-only, no QID" },
      { range:"35-55", count:475, desc:"QID + partial enrichment" },
      { range:"60-75", count:2303, desc:"QID + DPRR + strong enrichment" },
      { range:"80-100", count:558, desc:"Full authority coverage" },
    ],
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// NAMED QUERIES
// ══════════════════════════════════════════════════════════════════════════════
const BIO_QUERIES = [
  { id:"BQ-01", label:"Cypher", name:"Person full career profile",
    purpose:"All positions held with temporal bounds, sorted chronologically.",
    code:`MATCH (p:Person {qid: $qid})-[r:POSITION_HELD]->(pos:Position)
RETURN p.label AS person,
       pos.label AS position,
       r.year_start AS year_start,
       r.year_end AS year_end
ORDER BY r.year_start` },

  { id:"BQ-02", label:"Cypher", name:"Who held this office in year X?",
    purpose:"Temporal office lookup — all persons holding a given position at a specific year.",
    code:`MATCH (p:Person)-[r:POSITION_HELD]->(pos:Position {label: $position})
WHERE r.year_start <= $year
  AND (r.year_end IS NULL OR r.year_end >= $year)
RETURN p.label, p.qid, r.year_start, r.year_end
ORDER BY r.year_start` },

  { id:"BQ-03", label:"Cypher", name:"Persons by SubjectConcept with temporal bounds",
    purpose:"Members of a SubjectConcept ordered by primary rank and earliest career start.",
    code:`MATCH (p:Person)-[r:MEMBER_OF]->(sc:SubjectConcept {subject_id: $sc_id})
RETURN p.label, p.qid, r.rank, r.earliest_year, r.latest_year,
       r.position_count, p.federation_score
ORDER BY r.rank, r.earliest_year` },

  { id:"BQ-04", label:"Cypher", name:"Cross-backbone: persons born at a place",
    purpose:"All persons born at a specific place, with their career summaries.",
    code:`MATCH (p:Person)-[:BORN_IN_PLACE]->(pl:Place {qid: $place_qid})
OPTIONAL MATCH (p)-[r:POSITION_HELD]->(pos:Position)
WITH p, pl, min(r.year_start) AS career_start, max(r.year_start) AS career_end,
     count(r) AS positions
RETURN p.label, p.qid, p.birth_year, p.death_year,
       career_start, career_end, positions
ORDER BY p.birth_year` },

  { id:"BQ-05", label:"Cypher", name:"Contemporary figures (active in same decade)",
    purpose:"Find all persons active (POSITION_HELD) in a given decade.",
    code:`MATCH (p:Person)-[r:POSITION_HELD]->(pos:Position)
WHERE r.year_start >= $decade_start AND r.year_start < $decade_start + 10
WITH p, collect(DISTINCT pos.label) AS positions, min(r.year_start) AS first_pos
RETURN p.label, p.qid, first_pos, positions
ORDER BY first_pos` },

  { id:"BQ-06", label:"Cypher", name:"D22 score distribution",
    purpose:"Score histogram for Person federation scores.",
    code:`MATCH (p:Person)
WHERE p.federation_score IS NOT NULL
WITH p.federation_score AS score, count(p) AS cnt
RETURN score, cnt ORDER BY score` },

  { id:"BQ-07", label:"Cypher", name:"Persons with highest authority coverage",
    purpose:"Persons with perfect or near-perfect D22 scores (multi-authority cross-referenced).",
    code:`MATCH (p:Person)
WHERE p.federation_score >= 90
RETURN p.label, p.qid, p.federation_score,
       p.viaf_id IS NOT NULL AS has_viaf,
       p.gnd_id IS NOT NULL AS has_gnd,
       p.loc_authority_id IS NOT NULL AS has_loc,
       p.isni IS NOT NULL AS has_isni
ORDER BY p.federation_score DESC, p.label` },
];

// ══════════════════════════════════════════════════════════════════════════════
// POSITION TYPE MAPPING — which SubjectConcept a position maps to
// ══════════════════════════════════════════════════════════════════════════════
const POSITION_MAP = [
  { category:"POLITICAL", color:C.political,
    positions:["consul","praetor","quaestor","tribunus plebis","censor","aedilis curulis","dictator","magister equitum","interrex","princeps senatus","proconsul","propraetor","promagistrate"],
    count:2830 },
  { category:"MILITARY", color:C.military,
    positions:["tribunus militum","legatus (lieutenant)","praefectus","praefectus equitum","triumphator","officer (title not preserved)"],
    count:1206 },
  { category:"RELIGIOUS", color:C.religious,
    positions:["augur","pontifex","pontifex maximus","flamen Dialis","salius","decemvir sacris faciundis","rex sacrorum","epulo","fetialis","Vestal Virgin"],
    count:292 },
  { category:"ECONOMIC", color:C.economic,
    positions:["monetalis","moneyer","curator restituendi Capitolii"],
    count:367 },
  { category:"LEGAL", color:C.legal,
    positions:["iudex quaestionis","duovir perduellionis"],
    count:15, note:"Most cross-listed with POLITICAL" },
];

// ══════════════════════════════════════════════════════════════════════════════
// SYS_ NODE CYPHER — creates self-describing metadata in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const SYS_CYPHER = `// Biographic Prosopographical SYS_ Node Registration
// Run to register biographic node types, relationships, and federation sources

// ── Register/update Person node type ──
MERGE (nt:SYS_NodeType {name: 'Person'})
SET nt.description = 'Prosopographical identity anchor. Confirmed by DPRR and/or Wikidata. Career encoded as POSITION_HELD edges.',
    nt.domain = 'biographic',
    nt.status = 'operational',
    nt.required_properties = ['entity_id', 'label'],
    nt.optional_properties = ['qid', 'dprr_id', 'birth_year', 'death_year', 'gender', 'occupation', 'citizenship', 'viaf_id', 'gnd_id', 'loc_authority_id', 'fast_id', 'isni', 'bnf_id', 'federation_score'],
    nt.updated_at = datetime();

// ── Register Position node type ──
MERGE (nt:SYS_NodeType {name: 'Position'})
SET nt.description = 'Roman office/position from DPRR. 171 types with enriched label_name.',
    nt.domain = 'biographic',
    nt.status = 'operational',
    nt.required_properties = ['label'],
    nt.optional_properties = ['label_name', 'dprr_id'],
    nt.updated_at = datetime();

// ── Register biographic relationship types ──
MERGE (rt:SYS_RelationshipType {name: 'POSITION_HELD'})
SET rt.source_label = 'Person', rt.target_label = 'Position',
    rt.description = 'Person held this office with temporal bounds (year_start, year_end)',
    rt.category = 'prosopographical', rt.temporal = true,
    rt.kernel_category = 'biographic';

MERGE (rt:SYS_RelationshipType {name: 'PART_OF_GENS'})
SET rt.source_label = 'Person', rt.target_label = 'Gens',
    rt.description = 'Person belongs to this Roman gens/clan',
    rt.category = 'prosopographical', rt.temporal = false,
    rt.kernel_category = 'biographic';

// ── Register DPRR federation source ──
MERGE (fs:SYS_FederationSource {source_id: 'dprr'})
SET fs.description = 'Digital Prosopography of the Roman Republic. Identity layer for Roman political figures.',
    fs.scoping_role = 'biographic_identity',
    fs.ingestion_note = 'Static import from Turtle dump. POSITION_HELD year_start/year_end backfilled.';
`;

// ══════════════════════════════════════════════════════════════════════════════
// AGENT BOOTSTRAP QUERY — how a new agent discovers the biographic schema
// ══════════════════════════════════════════════════════════════════════════════
const AGENT_BOOTSTRAP = {
  description:"A newly instantiated agent runs these queries to understand the biographic architecture from Neo4j itself.",
  queries:[
    { step:1, name:"Discover biographic node types",
      query:`MATCH (nt:SYS_NodeType)
WHERE nt.domain = 'biographic'
RETURN nt.name, nt.description, nt.required_properties, nt.optional_properties, nt.status` },
    { step:2, name:"Discover biographic relationships",
      query:`MATCH (rt:SYS_RelationshipType)
WHERE rt.kernel_category = 'biographic'
RETURN rt.name, rt.source_label, rt.target_label, rt.description, rt.temporal` },
    { step:3, name:"Discover biographic SubjectConcepts",
      query:`MATCH (sc:SubjectConcept {seed_domain: 'biographic'})
OPTIONAL MATCH (sc)<-[r:MEMBER_OF]-(p:Person)
RETURN sc.subject_id, sc.label, sc.entity_count,
  count(CASE WHEN r.rank = 'primary' THEN 1 END) AS primary_members,
  count(CASE WHEN r.rank = 'secondary' THEN 1 END) AS secondary_members,
  count(CASE WHEN r.rank = 'inferred' THEN 1 END) AS inferred_members
ORDER BY sc.entity_count DESC` },
    { step:4, name:"Check D22 scoring state",
      query:`MATCH (p:Person)
RETURN count(p) AS total,
  count(p.federation_score) AS scored,
  avg(p.federation_score) AS avg_score,
  count(p.qid) AS with_qid,
  count(p.dprr_id) AS with_dprr` },
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// UI HELPERS
// ══════════════════════════════════════════════════════════════════════════════
function Tag({ label, color, size=8 }) {
  return <span style={{background:color+"20",border:`1px solid ${color}`,borderRadius:10,
    padding:"1px 7px",fontSize:size,color,fontWeight:"bold",margin:"1px",display:"inline-block"}}>{label}</span>;
}
function SHead({ children, col=C.dim }) {
  return <div style={{fontSize:7.5,fontWeight:"bold",color:col,letterSpacing:"0.1em",
    textTransform:"uppercase",marginBottom:6}}>{children}</div>;
}
function Mono({ children, col=C.neo, s=8.5 }) {
  return <span style={{fontFamily:"'Courier New',monospace",fontSize:s,color:col}}>{children}</span>;
}
function CopyBtn({ text }) {
  const [ok,setOk]=useState(false);
  return <button onClick={()=>{navigator.clipboard?.writeText(text);setOk(true);setTimeout(()=>setOk(false),1200);}}
    style={{background:ok?C.pass+"30":C.border,color:ok?C.pass:C.dim,
      border:`1px solid ${ok?C.pass:C.border}`,borderRadius:3,
      padding:"1px 8px",fontSize:7.5,cursor:"pointer",transition:"all .2s"}}>{ok?"copied":"copy"}</button>;
}

// ── PRINCIPLES TAB ───────────────────────────────────────────────────────────
function PrinciplesTab() {
  return (
    <div>
      {PRINCIPLES.map(p=>(
        <div key={p.id} style={{borderLeft:`3px solid ${C.neo}`,padding:"8px 12px",
          marginBottom:8,background:C.panel,borderRadius:"0 4px 4px 0"}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <Mono col={C.neo}>{p.id}</Mono>
            <span style={{fontWeight:"bold",color:C.bright,fontSize:10}}>{p.name}</span>
          </div>
          <div style={{fontSize:8.5,color:C.dim,lineHeight:1.5}}>{p.desc}</div>
        </div>
      ))}
    </div>
  );
}

// ── NODE TYPES TAB ───────────────────────────────────────────────────────────
function NodeTypesTab() {
  const [sel,setSel]=useState("Person");
  const nt = NODE_TYPES.find(n=>n.name===sel);
  return (
    <div style={{display:"grid",gridTemplateColumns:"180px 1fr",gap:12}}>
      <div>
        {NODE_TYPES.map(n=>(
          <div key={n.name} onClick={()=>setSel(n.name)}
            style={{border:`1px solid ${sel===n.name?n.color:C.border}`,
              borderLeft:`3px solid ${n.color}`,borderRadius:4,
              padding:"6px 10px",marginBottom:5,cursor:"pointer",
              background:sel===n.name?n.color+"10":C.panel}}>
            <div style={{display:"flex",gap:6,alignItems:"center"}}>
              <span style={{fontWeight:"bold",color:n.color,fontSize:9.5}}>:{n.name}</span>
              <div style={{marginLeft:"auto",width:6,height:6,borderRadius:"50%",
                background:STATUS_COL[n.status]||C.dim}}/>
            </div>
            {n.current_count>0 && <div style={{fontSize:7.5,color:C.dim}}>{n.current_count.toLocaleString()} nodes</div>}
          </div>
        ))}
      </div>
      {nt&&(
        <div style={{border:`1px solid ${nt.color}40`,borderLeft:`3px solid ${nt.color}`,
          borderRadius:6,padding:12,background:C.panel}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:6}}>
            <span style={{fontWeight:"bold",color:nt.color,fontSize:13}}>:{nt.name}</span>
            <Tag label={nt.status} color={STATUS_COL[nt.status]||C.dim}/>
            {nt.current_count>0 && <Tag label={`${nt.current_count.toLocaleString()} nodes`} color={C.dim}/>}
          </div>
          <div style={{fontSize:9,color:C.dim,marginBottom:10,lineHeight:1.5}}>{nt.desc}</div>

          <SHead col={nt.color}>REQUIRED PROPERTIES</SHead>
          {nt.required_props.map(p=>(
            <div key={p.name} style={{display:"flex",gap:8,marginBottom:3,paddingLeft:8,
              borderLeft:`2px solid ${nt.color}`}}>
              <Mono col={nt.color} s={8}>{p.name}</Mono>
              <span style={{fontSize:8,color:C.dim}}>{p.type}{p.pattern?` (${p.pattern})`:""}</span>
              <span style={{fontSize:8,color:C.dim,marginLeft:"auto"}}>{p.desc}</span>
            </div>
          ))}

          {nt.optional_props?.length>0 && <>
            <SHead col={C.dim}>OPTIONAL PROPERTIES</SHead>
            {nt.optional_props.map(p=>(
              <div key={p.name} style={{display:"flex",gap:8,marginBottom:3,paddingLeft:8,
                borderLeft:`2px solid ${C.border}`}}>
                <Mono col={C.dim} s={8}>{p.name}</Mono>
                <span style={{fontSize:8,color:C.dim}}>{p.type}{p.values?` [${p.values.join(", ")}]`:""}</span>
                <span style={{fontSize:8,color:C.dim,marginLeft:"auto"}}>{p.desc}</span>
              </div>
            ))}
          </>}

          {nt.source_data && <div style={{marginTop:8,background:nt.color+"10",borderRadius:3,
            padding:"4px 8px",fontSize:7.5,color:nt.color}}>{nt.source_data}</div>}
          {nt.note && <div style={{marginTop:4,fontSize:7.5,color:C.dim,fontStyle:"italic"}}>{nt.note}</div>}
        </div>
      )}
    </div>
  );
}

// ── RELATIONSHIPS TAB ────────────────────────────────────────────────────────
function RelsTab() {
  return (
    <div>
      {REL_TYPES.map(r=>(
        <div key={r.name} style={{display:"flex",gap:8,marginBottom:5,
          borderLeft:`3px solid ${r.status==='operational'?C.pass:C.warn}`,
          padding:"6px 10px",background:C.panel,borderRadius:"0 4px 4px 0",
          alignItems:"center"}}>
          <div style={{width:6,height:6,borderRadius:"50%",
            background:STATUS_COL[r.status]||C.dim,flexShrink:0}}/>
          <Mono col={C.neo} s={9}>{r.name}</Mono>
          <Tag label={`:${r.source}`} color={C.dprr} size={7}/>
          <span style={{color:C.dim,fontSize:8}}>-&gt;</span>
          <Tag label={`:${r.target}`} color={C.wikidata} size={7}/>
          {r.temporal && <Tag label="temporal" color={C.religious} size={7}/>}
          <span style={{fontSize:8,color:C.dim,flex:1,marginLeft:8}}>{r.desc}</span>
          {r.current_count && <span style={{fontSize:7.5,color:C.dim}}>{r.current_count.toLocaleString()}</span>}
        </div>
      ))}
    </div>
  );
}

// ── FEDERATION TAB ───────────────────────────────────────────────────────────
function FedTab() {
  const [sel,setSel]=useState(null);
  return (
    <div>
      {BIO_FED.map(src=>(
        <div key={src.id} style={{border:`1px solid ${src.color}30`,
          borderLeft:`3px solid ${src.color}`,borderRadius:4,marginBottom:6}}>
          <div onClick={()=>setSel(sel===src.id?null:src.id)}
            style={{padding:"8px 12px",cursor:"pointer",display:"flex",
              gap:8,alignItems:"center",background:C.panel}}>
            <div style={{width:8,height:8,borderRadius:"50%",
              background:STATUS_COL[src.status],flexShrink:0}}/>
            <span style={{fontWeight:"bold",color:src.color,fontSize:10,flex:1}}>{src.name}</span>
            <Tag label={src.role} color={src.color} size={7.5}/>
            <Tag label={src.status} color={STATUS_COL[src.status]} size={7}/>
            <span style={{color:C.dim}}>{sel===src.id?"\u25B2":"\u25BC"}</span>
          </div>
          {sel===src.id&&(
            <div style={{padding:"10px 12px",background:C.bg,borderTop:`1px solid ${C.border}`}}>
              <div style={{fontSize:8.5,color:C.dim,marginBottom:8,lineHeight:1.5}}>{src.desc}</div>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
                <div>
                  <SHead col={src.color}>PROVIDES</SHead>
                  {src.provides.map(p=>(
                    <div key={p} style={{fontSize:8,color:C.bright,marginBottom:2,
                      paddingLeft:8,borderLeft:`2px solid ${src.color}`}}>{p}</div>
                  ))}
                </div>
                <div>
                  <SHead col={C.dim}>CURRENT STATE</SHead>
                  <div style={{fontSize:8,color:C.warn,marginBottom:6,lineHeight:1.5}}>{src.current_state}</div>
                  <SHead col={C.dim}>ENDPOINT</SHead>
                  <Mono col={src.color} s={7.5}>{src.endpoint}</Mono>
                </div>
              </div>
              {src.ingestion_notes && <div style={{marginTop:8,background:src.color+"10",
                borderRadius:3,padding:"5px 8px",fontSize:7.5,color:src.color}}>{src.ingestion_notes}</div>}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── RULES TAB ────────────────────────────────────────────────────────────────
function RulesTab() {
  const [sel,setSel]=useState(null);
  return (
    <div>
      {BIO_RULES.map(r=>(
        <div key={r.id} style={{border:`1px solid ${sel===r.id?C.neo:C.border}`,
          borderLeft:`3px solid ${C.neo}`,borderRadius:4,marginBottom:5}}>
          <div onClick={()=>setSel(sel===r.id?null:r.id)}
            style={{padding:"6px 10px",cursor:"pointer",display:"flex",
              gap:8,alignItems:"center",background:C.panel}}>
            <Mono col={C.neo} s={8.5}>{r.id}</Mono>
            <span style={{fontWeight:"bold",color:C.bright,fontSize:9.5,flex:1}}>{r.name}</span>
            {r.facets.map(f=><Tag key={f} label={f} color={C.dprr} size={7}/>)}
            <span style={{color:C.dim}}>{sel===r.id?"\u25B2":"\u25BC"}</span>
          </div>
          {sel===r.id&&(
            <div style={{padding:"8px 10px",background:C.bg,borderTop:`1px solid ${C.border}`,
              display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
              <div>
                <SHead col={C.warn}>TRIGGER</SHead>
                <div style={{fontSize:8.5,color:C.dim,marginBottom:8,lineHeight:1.5}}>{r.trigger}</div>
                <SHead col={C.neo}>ACTION</SHead>
                <div style={{fontFamily:"'Courier New',monospace",fontSize:8,color:C.neo,
                  background:C.neo+"08",borderRadius:3,padding:"5px 7px",lineHeight:1.5}}>{r.action}</div>
              </div>
              <div>
                <SHead col={C.dim}>RATIONALE</SHead>
                <div style={{fontSize:8.5,color:C.dim,lineHeight:1.5}}>{r.rationale}</div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── QUERIES TAB ──────────────────────────────────────────────────────────────
function QueriesTab() {
  const [sel,setSel]=useState("BQ-01");
  const q=BIO_QUERIES.find(q=>q.id===sel);
  return (
    <div style={{display:"grid",gridTemplateColumns:"220px 1fr",gap:12}}>
      <div>
        {BIO_QUERIES.map(q=>(
          <div key={q.id} onClick={()=>setSel(q.id)}
            style={{border:`1px solid ${sel===q.id?C.neo:C.border}`,
              borderLeft:`3px solid ${sel===q.id?C.neo:C.border}`,
              borderRadius:3,padding:"5px 8px",marginBottom:3,cursor:"pointer",
              background:sel===q.id?C.neo+"12":C.panel}}>
            <div style={{fontWeight:"bold",color:sel===q.id?C.neo:C.dim,fontSize:8.5}}>{q.id}</div>
            <div style={{fontSize:7.5,color:C.dim,marginTop:1}}>{q.name}</div>
          </div>
        ))}
      </div>
      {q&&(
        <div>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <Tag label={q.label} color={C.neo}/>
            <span style={{fontWeight:"bold",color:C.neo,fontSize:11}}>{q.name}</span>
          </div>
          <div style={{fontSize:8.5,color:C.dim,marginBottom:8,
            background:C.neo+"08",borderRadius:3,padding:"4px 8px"}}>{q.purpose}</div>
          <div style={{display:"flex",justifyContent:"flex-end",marginBottom:4}}>
            <CopyBtn text={q.code}/>
          </div>
          <pre style={{fontFamily:"'Courier New',monospace",fontSize:8.5,color:C.neo,
            background:C.neo+"08",borderRadius:4,padding:10,margin:0,
            overflow:"auto",maxHeight:400,whiteSpace:"pre-wrap",lineHeight:1.6}}>{q.code}</pre>
        </div>
      )}
    </div>
  );
}

// ── POSITION MAP TAB ────────────────────────────────────────────────────────
function PositionMapTab() {
  return (
    <div>
      <div style={{fontSize:9,color:C.dim,marginBottom:12,lineHeight:1.5}}>
        Maps 60+ DPRR Position types to biographic SubjectConcepts. Some positions cross categories
        (e.g. tribunus militum consulari potestate = MILITARY + POLITICAL). 115 rare/variant positions
        default to POLITICAL.
      </div>
      {POSITION_MAP.map(cat=>(
        <div key={cat.category} style={{border:`1px solid ${cat.color}30`,
          borderLeft:`3px solid ${cat.color}`,borderRadius:4,padding:"8px 12px",
          marginBottom:6,background:C.panel}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <span style={{fontWeight:"bold",color:cat.color,fontSize:10}}>BIO_{cat.category}_FIGURES</span>
            <Tag label={`${cat.count} position-derived memberships`} color={cat.color} size={7}/>
            {cat.note && <span style={{fontSize:7.5,color:C.dim,fontStyle:"italic"}}>{cat.note}</span>}
          </div>
          <div style={{display:"flex",gap:4,flexWrap:"wrap"}}>
            {cat.positions.map(p=>(
              <span key={p} style={{background:cat.color+"15",border:`1px solid ${cat.color}30`,
                borderRadius:3,padding:"1px 6px",fontSize:7.5,color:cat.color}}>{p}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ── SFA TAB ─────────────────────────────────────────────────────────────────
function SfaTab() {
  return (
    <div>
      <div style={{border:`1px solid ${C.neo}40`,borderLeft:`3px solid ${C.neo}`,
        borderRadius:6,padding:12,background:C.panel,marginBottom:12}}>
        <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:6}}>
          <span style={{fontWeight:"bold",color:C.neo,fontSize:13}}>{BIO_SFA.label}</span>
          <Tag label={BIO_SFA.status} color={C.warn}/>
          <Tag label={`agent_id: ${BIO_SFA.agent_id}`} color={C.dim}/>
        </div>
        <div style={{fontSize:9,color:C.dim,marginBottom:8,lineHeight:1.5}}>{BIO_SFA.description}</div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
          <div>
            <SHead col={C.neo}>DECISION TABLES</SHead>
            {BIO_SFA.decision_tables.map(dt=>(
              <div key={dt.id} style={{marginBottom:6,paddingLeft:8,borderLeft:`2px solid ${C.neo}`}}>
                <Mono col={C.neo} s={8.5}>{dt.id}</Mono>
                <span style={{fontSize:8,color:C.dim,marginLeft:6}}>{dt.rules} rules, max {dt.max_score}</span>
                <div style={{fontSize:7.5,color:C.dim}}>{dt.desc}</div>
                {dt.dimensions && <div style={{marginTop:2,display:"flex",gap:3,flexWrap:"wrap"}}>
                  {dt.dimensions.map(d=><Tag key={d} label={d} color={C.neo} size={6.5}/>)}
                </div>}
              </div>
            ))}
          </div>
          <div>
            <SHead col={C.wikidata}>CLASSIFICATION PIPELINE</SHead>
            {Object.entries(BIO_SFA.classification_pipeline).map(([step,desc])=>(
              <div key={step} style={{fontSize:8,color:C.dim,marginBottom:4,paddingLeft:8,
                borderLeft:`2px solid ${C.wikidata}`}}>
                <Mono col={C.wikidata} s={7.5}>{step}</Mono>
                <span style={{marginLeft:6}}>{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <SHead col={C.dprr}>COVERAGE</SHead>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8,marginBottom:12}}>
        {[["Total Persons",BIO_SFA.coverage.total_persons,C.dprr],
          ["With Temporal",BIO_SFA.coverage.with_temporal_membership,C.pass],
          ["MEMBER_OF edges",BIO_SFA.coverage.member_of_edges,C.neo],
          ["Anchors",BIO_SFA.coverage.classification_anchors,C.wikidata],
          ["SubjectConcepts",BIO_SFA.coverage.subject_concepts,C.lcnaf],
          ["Perfect Score",BIO_SFA.score_distribution.perfect_score,C.pass],
        ].map(([label,val,col])=>(
          <div key={label} style={{background:col+"10",border:`1px solid ${col}30`,borderRadius:4,
            padding:"6px 10px",textAlign:"center"}}>
            <div style={{fontSize:16,fontWeight:"bold",color:col}}>{val.toLocaleString()}</div>
            <div style={{fontSize:7.5,color:C.dim}}>{label}</div>
          </div>
        ))}
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8,marginBottom:12}}>
        {[["Primary rank",BIO_SFA.coverage.member_of_primary,C.pass],
          ["Secondary rank",BIO_SFA.coverage.member_of_secondary,C.warn],
          ["Inferred rank",BIO_SFA.coverage.member_of_inferred,C.dim],
        ].map(([label,val,col])=>(
          <div key={label} style={{background:col+"10",border:`1px solid ${col}30`,borderRadius:4,
            padding:"6px 10px",textAlign:"center"}}>
            <div style={{fontSize:14,fontWeight:"bold",color:col}}>{val.toLocaleString()}</div>
            <div style={{fontSize:7.5,color:C.dim}}>{label}</div>
          </div>
        ))}
      </div>
      <SHead col="#9B59B6">SUBJECT CONCEPTS</SHead>
      <div style={{borderRadius:4,overflow:"hidden",border:`1px solid ${C.border}`}}>
        <div style={{display:"grid",gridTemplateColumns:"200px 80px 80px 1fr",
          background:C.border,padding:"4px 8px",fontSize:7.5,fontWeight:"bold",color:C.dim}}>
          <span>Subject ID</span><span>Members</span><span>Anchors</span><span>Temporal Detail</span>
        </div>
        {NODE_TYPES.find(n=>n.name==="SubjectConcept")?.subjects?.map(s=>(
          <div key={s.id} style={{display:"grid",gridTemplateColumns:"200px 80px 80px 1fr",
            padding:"3px 8px",borderTop:`1px solid ${C.border}`,fontSize:8}}>
            <Mono col="#9B59B6" s={8}>{s.id}</Mono>
            <span style={{color:C.bright}}>{s.members.toLocaleString()}</span>
            <span style={{color:C.wikidata}}>{s.anchors}</span>
            <span style={{color:C.dim,fontSize:7}}>{s.temporal}</span>
          </div>
        ))}
      </div>
      <div style={{marginTop:8,fontSize:7.5,color:C.warn,fontStyle:"italic"}}>
        Score distribution: avg={BIO_SFA.score_distribution.avg}, min={BIO_SFA.score_distribution.min}, max={BIO_SFA.score_distribution.max}.
        {" "}{BIO_SFA.coverage.without_temporal_reason}
      </div>
    </div>
  );
}

// ── BOOTSTRAP TAB ────────────────────────────────────────────────────────────
function BootstrapTab() {
  return (
    <div>
      <div style={{fontSize:9,color:C.dim,marginBottom:12,lineHeight:1.5}}>
        {AGENT_BOOTSTRAP.description}
      </div>
      {AGENT_BOOTSTRAP.queries.map(q=>(
        <div key={q.step} style={{marginBottom:10}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <div style={{background:C.neo,color:"white",borderRadius:"50%",
              width:20,height:20,display:"flex",alignItems:"center",justifyContent:"center",
              fontSize:9,fontWeight:"bold",flexShrink:0}}>{q.step}</div>
            <span style={{fontWeight:"bold",color:C.bright,fontSize:9.5}}>{q.name}</span>
            <div style={{marginLeft:"auto"}}><CopyBtn text={q.query}/></div>
          </div>
          <pre style={{fontFamily:"'Courier New',monospace",fontSize:8,color:C.neo,
            background:C.neo+"08",borderRadius:4,padding:8,margin:0,
            whiteSpace:"pre-wrap",lineHeight:1.5}}>{q.query}</pre>
        </div>
      ))}
      <div style={{marginTop:12}}>
        <SHead col={C.cypher}>SYS_ REGISTRATION CYPHER</SHead>
        <div style={{fontSize:8,color:C.dim,marginBottom:6}}>
          Run to register biographic node types, relationships, and federation sources in Neo4j.
        </div>
        <div style={{display:"flex",justifyContent:"flex-end",marginBottom:4}}>
          <CopyBtn text={SYS_CYPHER}/>
        </div>
        <pre style={{fontFamily:"'Courier New',monospace",fontSize:7.5,color:C.cypher,
          background:C.cypher+"08",borderRadius:4,padding:10,margin:0,
          overflow:"auto",maxHeight:400,whiteSpace:"pre-wrap",lineHeight:1.5}}>{SYS_CYPHER}</pre>
      </div>
    </div>
  );
}

// ── ROOT ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [view,setView]=useState("principles");
  const VIEWS=[
    ["principles",  "Principles"],
    ["nodes",       `Node Types (${NODE_TYPES.length})`],
    ["rels",        `Relationships (${REL_TYPES.length})`],
    ["rules",       `Rules (${BIO_RULES.length})`],
    ["queries",     `Queries (${BIO_QUERIES.length})`],
    ["fed",         `Federation (${BIO_FED.length})`],
    ["sfa",         "SFA Agent"],
    ["positions",   `Position Map (${POSITION_MAP.length})`],
    ["bootstrap",   "Agent Bootstrap"],
  ];
  return (
    <div style={{background:C.bg,minHeight:"100vh",padding:16,
      fontFamily:"'Courier New',monospace",color:C.bright}}>
      <div style={{borderBottom:`1px solid ${C.border}`,paddingBottom:12,marginBottom:14}}>
        <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:4}}>
          <span style={{fontSize:8,color:C.dim,letterSpacing:"0.15em"}}>CHRYSTALLUM - AGENT CONSTITUTION</span>
          {[["DPRR",C.dprr],["Wikidata",C.wikidata],["LCNAF",C.lcnaf],["Neo4j",C.neo]].map(([l,c])=>(
            <span key={l} style={{background:c,color:"white",borderRadius:4,
              padding:"1px 8px",fontSize:8,fontWeight:"bold"}}>{l}</span>
          ))}
        </div>
        <div style={{fontSize:18,fontWeight:"bold",color:C.bright,marginBottom:2}}>
          Biographic Prosopographical Constitution
        </div>
        <div style={{fontSize:9,color:C.dim,marginBottom:6}}>
          Prosopographical identity with temporal career structure from POSITION_HELD edges.
          5,248 Persons | 394 ClassificationAnchors | 7 SubjectConcepts | 8,836 MEMBER_OF (4,710 temporal) | D22 scored.
        </div>
        <div style={{display:"flex",gap:8,flexWrap:"wrap",fontSize:8,color:C.dim}}>
          <span>{NODE_TYPES.length} node types</span>
          <span>-</span><span>{REL_TYPES.length} relationships</span>
          <span>-</span><span>{BIO_RULES.length} rules</span>
          <span>-</span><span>{BIO_QUERIES.length} named queries</span>
          <span>-</span><span>{BIO_FED.length} federation sources</span>
          <span>-</span><span>{POSITION_MAP.length} position categories</span>
          <span>-</span><span>1 SFA agent</span>
        </div>
        <div style={{marginTop:8,background:C.neo+"10",border:`1px solid ${C.neo}30`,
          borderRadius:4,padding:"5px 10px",fontSize:8,color:C.neo}}>
          AGENT INSTRUCTION: This is the biographic domain constitution.
          Bio backbone = Person nodes confirmed by DPRR (identity) + Wikidata (enrichment).
          Two source layers: DPRR (prosopographical identity, positions, temporal career), Wikidata (authority IDs, occupation, gender, citizenship).
          Career structure encoded as POSITION_HELD edges with year_start/year_end — NOT flat properties.
          MEMBER_OF carries temporal and multiplicity dimensions: rank (primary/secondary/inferred), earliest_year, latest_year, position_count.
          SFA agent: sfa_biographic (status=bootstrap). 7 SubjectConcepts. D22 scoring (11 rules, max 100).
          Query SYS_NodeType WHERE domain='biographic' to bootstrap.
        </div>
      </div>
      <div style={{display:"flex",gap:0,borderBottom:`1px solid ${C.border}`,marginBottom:14,flexWrap:"wrap"}}>
        {VIEWS.map(([k,l])=>(
          <button key={k} onClick={()=>setView(k)}
            style={{border:"none",background:"transparent",padding:"6px 12px",fontSize:8.5,
              cursor:"pointer",color:view===k?C.neo:C.dim,fontWeight:view===k?"bold":"normal",
              borderBottom:view===k?`2px solid ${C.neo}`:"2px solid transparent"}}>
            {l}
          </button>
        ))}
      </div>
      {view==="principles" && <PrinciplesTab/>}
      {view==="nodes"      && <NodeTypesTab/>}
      {view==="rels"       && <RelsTab/>}
      {view==="rules"      && <RulesTab/>}
      {view==="queries"    && <QueriesTab/>}
      {view==="fed"        && <FedTab/>}
      {view==="sfa"        && <SfaTab/>}
      {view==="positions"  && <PositionMapTab/>}
      {view==="bootstrap"  && <BootstrapTab/>}
    </div>
  );
}
