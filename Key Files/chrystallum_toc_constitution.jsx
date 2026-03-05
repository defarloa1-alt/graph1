import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — TRANSITION OF CARE AGENT CONSTITUTION                       ║
// ║  Integration: Snowflake discharge feed → Neo4j → TOC Agent                 ║
// ║  Equivalent depth to Roman Republic domain constitution                     ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  sf:"#29B5E8", neo:"#00C2A8", cypher:"#B5860D",
  clinical:"#00C2A8", benefits:"#4B9FE1", regulatory:"#F5A623",
  financial:"#7ED321", member:"#9B6DFF", quality:"#50E3C2",
  sdoh:"#FFB347", provider:"#FF6B6B", behavioral:"#D4A5FF",
  pass:"#2ECC71", warn:"#F5A623", fail:"#E74C3C",
  amber:"#B5860D", navy:"#1A3A5C", teal:"#00C2A8",
};

const STATUS_COL = { operational:C.pass, planned:C.warn, partial:C.warn, blocked:C.fail };
const FACET_COL  = {
  Clinical:C.clinical, Benefits:C.benefits, Regulatory:C.regulatory,
  Financial:C.financial, Member:C.member, Quality:C.quality,
  SDOH:C.sdoh, Provider:C.provider, Behavioral:C.behavioral,
};

// ══════════════════════════════════════════════════════════════════════════════
// INSTANCE DATA
// ══════════════════════════════════════════════════════════════════════════════
const INSTANCE = {
  domain: "Transition of Care · Hospital Discharge · Post-Acute Care Management",
  description: "Agent constitution for the 0–48h post-discharge window. Snowflake discharge feed drives real-time member risk stratification, coverage determination, HHA matching, and HEDIS gap flagging.",
  corpus_scope: "US Health Plan · Medicaid LTSS · Medicare Part A/B · Medicare Advantage · Acute + Post-Acute continuum",

  seed_entities: [
    { qid:"Q22906178", label:"activities of daily living assistance", etype:"SERVICE",   primary:true  },
    { qid:"Q179388",   label:"home care",                             etype:"SERVICE",   primary:true  },
    { qid:"Q189603",   label:"care management",                       etype:"CONCEPT",   primary:true  },
    { qid:"Q1662799",  label:"long-term care",                        etype:"SERVICE",   primary:false },
    { qid:"Q1323436",  label:"activities of daily living",            etype:"CONCEPT",   primary:false },
    { qid:"Q179132",   label:"Medicaid",                              etype:"PROGRAM",   primary:false },
    { qid:"Q308963",   label:"Medicare",                              etype:"PROGRAM",   primary:false },
    { qid:"Q929220",   label:"instrumental activities of daily living",etype:"CONCEPT",  primary:false },
  ],

  p31_types: [
    { qid:"Q4006979",  label:"service activity",     color:C.clinical,
      role:"Primary — ADL assistance and home care are delivered services",
      chrystallum_nodes:[":ServiceConcept",":SubjectConcept"],
      relationships:["DELIVERED_BY","BILLED_AS","AUTHORIZED_UNDER","ASSESSED_BY"],
      facets:["Clinical","Benefits","Provider"],
      harvest_trigger:"P31=Q4006979 → harvest P366 (use), P2175 (medical condition), HCPCS code",
      promotion_rule:"P31=Q4006979 AND has_hcpcs_code → :ServiceConcept",
      in_corpus:[
        { qid:"Q22906178", label:"ADL assistance",   etype:"SERVICE"  },
        { qid:"Q179388",   label:"home care",         etype:"SERVICE"  },
        { qid:"Q929220",   label:"IADL assistance",   etype:"SERVICE"  },
      ]},
    { qid:"Q12136",    label:"disease / condition",  color:C.fail,
      role:"Diagnosis driving TOC need — ICD-10 linkage, risk stratification trigger",
      chrystallum_nodes:[":Diagnosis",":ClinicalConcept"],
      relationships:["CAUSES_ADL_NEED","COMPLICATES","MANAGED_BY","CODED_AS"],
      facets:["Clinical","Behavioral","Member"],
      harvest_trigger:"P31=Q12136 AND ICD-10 code present → :Diagnosis. High signal for Clinical+Member.",
      promotion_rule:"has_icd10_code → :Diagnosis. Z74.x → SET member.adl_need=true",
      in_corpus:[
        { qid:"Q11085",    label:"dementia",          etype:"DIAGNOSIS"  },
        { qid:"Q181923",   label:"heart failure",     etype:"DIAGNOSIS"  },
        { qid:"Q166902",   label:"COPD",              etype:"DIAGNOSIS"  },
        { qid:"Q133823",   label:"diabetes mellitus", etype:"DIAGNOSIS"  },
        { qid:"Q175111",   label:"stroke",            etype:"DIAGNOSIS"  },
      ]},
    { qid:"Q179132",   label:"government program",   color:C.regulatory,
      role:"Payer/program — Medicaid, Medicare, CHIP, waiver programs",
      chrystallum_nodes:[":PayerProgram",":WaiverProgram"],
      relationships:["COVERS","REQUIRES_ELIGIBILITY","HAS_BENEFIT","REGULATED_BY"],
      facets:["Regulatory","Benefits","Financial"],
      harvest_trigger:"P31=Q179132 AND P17=Q30 (US) → :PayerProgram",
      promotion_rule:"P31=Q179132 AND P17=Q30 → :PayerProgram",
      in_corpus:[
        { qid:"Q179132",   label:"Medicaid",         etype:"PROGRAM"  },
        { qid:"Q308963",   label:"Medicare",         etype:"PROGRAM"  },
      ]},
    { qid:"Q4830453",  label:"business process",     color:C.quality,
      role:"Workflows and care processes — TOC, care plan, authorization, assessment",
      chrystallum_nodes:[":WorkflowTrigger",":CarePlan",":ServiceAuth"],
      relationships:["TRIGGERED_BY","PRODUCES","ASSIGNED_TO","DUE_BY"],
      facets:["Quality","Benefits","Member"],
      harvest_trigger:"P31=Q4830453 → harvest P366 (use), P2275 (standard/guideline)",
      promotion_rule:"has_workflow_type → :WorkflowTrigger",
      in_corpus:[
        { qid:null,  label:"TOC Workflow",          etype:"WORKFLOW"  },
        { qid:null,  label:"Prior Authorization",   etype:"WORKFLOW"  },
        { qid:null,  label:"HEDIS Gap Closure",     etype:"WORKFLOW"  },
      ]},
  ],

  subclass_signals: [
    { qid:"Q784794",   label:"home health service",           signal:"HIGH",   reason:"Core post-discharge service. Ordered at discharge, authorized by plan." },
    { qid:"Q1662799",  label:"long-term care",                signal:"HIGH",   reason:"Escalation pathway when home health fails — SNF admission." },
    { qid:"Q11085",    label:"dementia",                      signal:"HIGH",   reason:"#1 ADL-impacting diagnosis. Z74.x almost always co-present." },
    { qid:"Q26721",    label:"disability",                    signal:"HIGH",   reason:"Primary ADL need driver in working-age members." },
    { qid:"Q865588",   label:"occupational therapy",          signal:"MEDIUM", reason:"Ordered alongside home health for ADL retraining." },
    { qid:"Q180516",   label:"physical therapy",              signal:"MEDIUM", reason:"Functional rehabilitation — PT → ADL improvement." },
    { qid:"Q179387",   label:"respite care",                  signal:"MEDIUM", reason:"Caregiver relief — co-authorized with ADL assistance." },
    { qid:"Q2140784",  label:"discharge planning",            signal:"HIGH",   reason:"Direct precursor process to TOC workflow trigger." },
    { qid:"Q858490",   label:"nursing home / SNF",            signal:"MEDIUM", reason:"Institutional alternative — ADL failure pathway." },
    { qid:"Q484767",   label:"palliative care",               signal:"LOW",    reason:"End-of-life ADL — separate benefit (hospice)." },
    { qid:"Q15062",    label:"hospital",                      signal:"LOW",    reason:"Origin setting — not primary domain." },
    { qid:"Q179719",   label:"surgery",                       signal:"IGNORE", reason:"Procedural trigger only — not in TOC scope." },
    { qid:"Q11190",    label:"medicine (discipline)",         signal:"IGNORE", reason:"Too broad — not a useful subclass signal." },
  ],

  disciplines: [
    { label:"nursing science",    lcc:"RT",       lcsh:"sh85093034", dewey:"610.73", primary_for:["Clinical","Member"],     repos:["PUBMED","CINAHL","OPENALEX"] },
    { label:"social work",        lcc:"HV",       lcsh:"sh85123836", dewey:"361",    primary_for:["SDOH","Member"],         repos:["OPEN_LIBRARY","JSTOR"] },
    { label:"health informatics", lcc:"R858",     lcsh:"sh85059782", dewey:"610.285",primary_for:["Quality","Clinical"],    repos:["PUBMED","OPENALEX"] },
    { label:"public health",      lcc:"RA",       lcsh:"sh85108028", dewey:"614",    primary_for:["Quality","Regulatory"],  repos:["CDC_DATA","PUBMED"] },
    { label:"health economics",   lcc:"RA410",    lcsh:"sh85059732", dewey:"338.4",  primary_for:["Financial","Benefits"],  repos:["OPENALEX","WORLDCAT"] },
    { label:"gerontology",        lcc:"HQ1060",   lcsh:"sh85054068", dewey:"305.26", primary_for:["Member","Clinical"],     repos:["PUBMED","OPENALEX"] },
    { label:"epidemiology",       lcc:"RA648",    lcsh:"sh85044228", dewey:"614.4",  primary_for:["Quality","Regulatory"],  repos:["CDC_DATA","PUBMED"] },
    { label:"law (health)",       lcc:"KF",       lcsh:"sh85074484", dewey:"344.04", primary_for:["Regulatory","Benefits"], repos:["WORLDCAT","OPEN_LIBRARY"] },
  ],

  assessment_tools: [
    { name:"LACE Index",   range:"0–19",  threshold:"≥10 = high readmit risk", loinc:null,       fields:["LOS","Acute admit","Charlson","ED visits"],      use:"Set on DischargeEvent" },
    { name:"Katz ADL",     range:"0–6",   threshold:"≤3 = LTSS eligible (most states)", loinc:"72133-2",  fields:["Bathing","Dressing","Toileting","Transfer","Continence","Feeding"], use:"Member.adl_score" },
    { name:"Barthel",      range:"0–100", threshold:"<60 = functional dependency", loinc:"44177-1",  fields:["10 ADL domains"],                            use:"Member.adl_score" },
    { name:"MDS 3.0 §G",   range:"0–4/domain", threshold:"Score 3–4 = extensive/total assist", loinc:null, fields:["Bed mobility","Transfer","Walk","Dressing","Eating","Toilet","Bathing"], use:"Discharge from SNF" },
    { name:"OASIS-E M1800",range:"0–6",   threshold:"≥3 = requires assistance",  loinc:"46522-4",  fields:["Grooming","Dressing upper","Dressing lower","Bathing","Toileting","Transferring","Ambulation"], use:"HHA OASIS at start of care" },
  ],

  // discharge dispositions — UB-04 codes, determines post-discharge pathway
  discharge_dispositions: [
    { code:"01", label:"Home",                      pathway:"Evaluate for home health if HH ordered or ADL need",    color:C.pass    },
    { code:"02", label:"Short-term hospital",       pathway:"Transfer — no TOC window triggered (not discharge)",    color:C.dim     },
    { code:"03", label:"SNF",                       pathway:"SNF stay initiated — monitor for SNF→home transition",  color:C.warn    },
    { code:"06", label:"Home + home health",        pathway:"HH ordered — validate auth, quality-match HHA",        color:C.pass    },
    { code:"07", label:"AMA (left against advice)", pathway:"High-risk flag — outreach within 24h",                 color:C.fail    },
    { code:"20", label:"Expired",                   pathway:"Exclude from TOC pipeline",                            color:C.dim     },
    { code:"50", label:"Hospice — home",            pathway:"Route to hospice benefit — separate workflow",         color:C.behavioral },
    { code:"62", label:"Rehab facility (IRF)",      pathway:"IRF stay — monitor for IRF→home transition",           color:C.warn    },
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// RULES — 16 declarative rules
// ══════════════════════════════════════════════════════════════════════════════
const TOC_RULES = [
  { id:"R-01", name:"Discharge Event Detection",      facets:["Member","Clinical"],
    trigger:"New row in Snowflake ADT_DISCHARGE_EVENTS with PROCESSED=FALSE and DISCHARGE_DT within polling window",
    action:"MERGE :DischargeEvent. Link to :Member via member_id/MBI/Medicaid_ID. Wire DISCHARGED_FROM to :Provider (facility NPI). SET created_at.",
    rationale:"Every care management action depends on discharge detection. The Snowflake row is the atomic trigger unit. Missed rows = missed TOC windows." },
  { id:"R-02", name:"Member Identity Resolution",     facets:["Member"],
    trigger:"MEMBER_ID or MBI or MEDICAID_ID present in discharge row",
    action:"MATCH :Member on any of the three IDs (OR logic). If no match: SET discharge.member_unmatched=true, flag for identity resolution queue.",
    rationale:"Members may be identifiable by plan ID, Medicare MBI, or state Medicaid ID. OR match prevents missed connections when one ID is absent." },
  { id:"R-03", name:"ICD-10 Array Expansion",         facets:["Clinical","Member"],
    trigger:"DX_CODES array on discharge row (up to 25 codes)",
    action:"UNWIND DX_CODES. MERGE :Diagnosis per code. Wire HAS_DIAGNOSIS from DischargeEvent. Check STARTS WITH 'Z74' — SET member.adl_need=true. Check 'Z74.2' — SET member.no_caregiver=true.",
    rationale:"Diagnosis array is the richest clinical signal in the discharge record. Z74.x is high-precision ADL need. Must expand before any downstream agent runs." },
  { id:"R-04", name:"Risk Tier Assignment",           facets:["Financial","Member","Quality"],
    trigger:"After R-01 and R-03 complete for encounter",
    action:"Compute tier 1–5: Tier 5 = LACE≥10 AND no_caregiver. Tier 4 = LACE≥10 OR no_caregiver. Tier 3 = readmit_risk≥0.25 OR adl_need. Tier 2 = LACE≥7. Tier 1 = all else. SET member.risk_tier. Tier 4–5 = URGENT priority.",
    rationale:"5-tier risk model concentrates care manager attention. Tier 4–5 represents ~15% of discharges but ~70% of avoidable costs. Must be computed within minutes of discharge detection." },
  { id:"R-05", name:"TOC Workflow Trigger",           facets:["Quality","Member"],
    trigger:"R-04 complete — any risk tier",
    action:"MERGE :WorkflowTrigger {type:TOC, encounter_id}. SET due_by = discharge_dt + 48h. SET priority = URGENT (tier 4–5) or STANDARD (tier 1–3). MERGE (member)-[:HAS_WORKFLOW]->(wf).",
    rationale:"48h window is CMS-defined standard for TOC interventions. Workflow node enables agent queue management and SLA tracking across the care manager team." },
  { id:"R-06", name:"Coverage Pathway Resolution",    facets:["Benefits","Regulatory"],
    trigger:"TOC workflow triggered — member has active eligibility",
    action:"Determine payer mix: Medicare (homebound + skilled need required), Medicaid PCS (functional threshold), MA supplemental (SSBCI + chronic illness). SET coverage_pathway on :WorkflowTrigger.",
    rationale:"Wrong pathway = denial. Medicare home health requires physician order + homebound status. Medicaid PCS requires functional threshold (Katz ≤3 in most states). Must resolve before auth." },
  { id:"R-07", name:"LCD Medical Necessity Gate",     facets:["Benefits","Regulatory"],
    trigger:"HOME_HEALTH_ORDERED=TRUE or post-TOC evaluation recommends HH",
    action:"Fetch LCD from CMS_LCD_NCD for member's MAC jurisdiction. Validate: homebound status, skilled need, physician certification. SET auth_decision = APPROVED/DENIED/PENDING_INFO.",
    rationale:"Medicare LCD defines medical necessity criteria by MAC jurisdiction. Failing to check LCD before auth submission generates denials and delays. Agent can resolve 80% without human review." },
  { id:"R-08", name:"HCPCS Code Assignment",          facets:["Benefits","Financial"],
    trigger:"Coverage pathway and service type resolved",
    action:"Assign primary HCPCS: 99509 (Medicare home visit/ADL), T1019 (Medicaid PCS per 15 min), S5125 (Medicaid attendant care), G0151/G0152 (PT/OT home health). Wire BILLED_AS to :ProcedureCode.",
    rationale:"Code selection is revenue-critical. T1019 is Medicaid-only (#1 home health code nationally, $2B+/yr). 99509 is Medicare/MA. Mismatch → claim denial." },
  { id:"R-09", name:"ADL Score Capture",              facets:["Clinical","Member"],
    trigger:"DISCHARGE_ADL_SCORE or ADL_TOOL present on discharge row OR OASIS on prior claims",
    action:"MERGE :AssessmentResult {encounter_id, tool}. SET score, assessed_at. Wire HAS_ASSESSMENT from DischargeEvent and from Member. Tag with source = DISCHARGE or PRIOR_CLAIMS.",
    rationale:"Discharge ADL score is the functional baseline for post-acute care planning. Without it, coverage determination for Medicaid PCS cannot be completed." },
  { id:"R-10", name:"HHA Quality Matching",           facets:["Provider","Quality"],
    trigger:"Home health authorized or ordered",
    action:"Query NPI_REGISTRY for type-2 HHAs in member ZIP. Pull CMS_OASIS scores. Filter in-network. Rank by ADL improvement rate DESC, hospitalization rate ASC. MERGE :HHAAssignment. Wire ASSIGNED_TO.",
    rationale:"HHA quality predicts member outcomes. CMS OASIS public data enables quality-adjusted matching. Preferred HHAs with above-benchmark improvement rates reduce readmissions and close HEDIS gaps." },
  { id:"R-11", name:"HEDIS TFL Gap Flag",             facets:["Quality","Member"],
    trigger:"Any discharge from acute, SNF, or IRF setting",
    action:"MERGE :HEDISGapFlag {measure:TFL, year, member_id}. SET window_7d = discharge_dt + 7d. SET window_30d = discharge_dt + 30d. SET status=OPEN. Wire to :Member.",
    rationale:"HEDIS Transitions of Care (TFL) requires follow-up within 7 and 30 days post-discharge. Each open gap affects STAR rating. Agent tracks window and auto-closes when follow-up claim received." },
  { id:"R-12", name:"HEDIS COA Gap Flag",             facets:["Quality","Member"],
    trigger:"Member age ≥65 AND no Katz/Barthel assessment in measurement year",
    action:"MERGE :HEDISGapFlag {measure:COA, year, member_id}. Wire to :Member. Add to HEDIS Gap Closure agent worklist.",
    rationale:"HEDIS Care for Older Adults (COA) requires annual functional status assessment for members 65+. Discharge is the highest-leverage moment to close this gap — member is already in the health system." },
  { id:"R-13", name:"SDOH-to-Clinical Bridge",        facets:["SDOH","Clinical","Member"],
    trigger:"Z74.2 (no caregiver) OR Z59.x (housing) OR Z55-Z65 (social determinants) in DX_CODES",
    action:"MERGE :SDOHFlag per Z-code. Wire to :Member. Identify community resources. Elevate risk tier if SDOH + Z74.x co-present. Alert care manager: SDOH intervention required before home care can succeed.",
    rationale:"Social factors independently predict ADL decline and institutionalization. A member with no caregiver (Z74.2) discharged home without support will readmit. The graph surfaces this before it happens." },
  { id:"R-14", name:"Mark Processed in Snowflake",    facets:["ALL"],
    trigger:"All three Cypher ingestion queries (CQ-01/02/03) committed successfully",
    action:"Execute SF-05: UPDATE ADT_DISCHARGE_EVENTS SET PROCESSED=TRUE, PROCESSED_AT=NOW() WHERE ENCOUNTER_ID IN (...). Only after Chrystallum confirms success — transactional integrity.",
    rationale:"PROCESSED flag prevents double-ingestion on next poll. Only set after graph MERGE succeeds. If graph write fails, row remains unprocessed and is retried on next poll cycle." },
  { id:"R-15", name:"Capability Cipher Construction", facets:["ALL"],
    trigger:"Any new :DischargeEvent, :Member update, or :CoveragePolicy change",
    action:"Compute cipher = SHA256(entity_qid || p31_type_qids || code_set_ids || fed_source_ids || primary_facets). Store on node. Invalidate when any component changes.",
    rationale:"Cipher enables cohort-level intervention design. Members with identical cipher share the same care pathway and can be batch-processed by the same agent configuration." },
  { id:"R-16", name:"Corpus Fit Gate",                facets:["ALL"],
    trigger:"Any entity entering graph",
    action:"corpus_fit = has_icd10_code OR has_hcpcs_code OR has_npi OR has_member_id OR has_snomed_code. If corpus_fit < 0.15: SET corpus_rejected=true, corpus_rejection_reason.",
    rationale:"Prevents non-healthcare entities from polluting the graph. A Roman Republic entity (Q17167) would score 0.0 and be rejected. An ADL service entity (Q22906178) scores 1.0." },
];

// ══════════════════════════════════════════════════════════════════════════════
// AGENT WORKFLOWS
// ══════════════════════════════════════════════════════════════════════════════
const TOC_WORKFLOWS = [
  { id:"AW-01", name:"Discharge Harvest Agent",        icon:"❄️",  color:C.sf,
    trigger:"Every 15 min (poll) or on Snowflake Stream commit (real-time)",
    latency:"< 2 min from discharge commit to graph ingestion",
    rules:["R-01","R-02","R-03","R-04","R-05","R-14"],
    fed:["SNOWFLAKE_DISCHARGES","ICD10_API"],
    outputs:[":DischargeEvent",":Diagnosis[]",":WorkflowTrigger",":RiskScore"],
    steps:[
      "Run SF-01 poll or consume SF-02 Stream — fetch unprocessed discharge rows",
      "Apply SF-03 high-risk filter — flag LACE≥10, Z74.x, prior_admits≥2",
      "Run CQ-01: MERGE :DischargeEvent, match :Member by MBI/Medicaid_ID/member_id, wire facility :Provider",
      "Run CQ-02: UNWIND DX_CODES → :Diagnosis nodes, flag Z74.x, set member.no_caregiver if Z74.2",
      "Run CQ-03: Compute risk_tier, MERGE :WorkflowTrigger {status:PENDING, due_by:+48h}",
      "Run SF-05: mark PROCESSED=TRUE in Snowflake only after Chrystallum confirms commit",
    ]},
  { id:"AW-02", name:"TOC Care Management Agent",      icon:"🏥",  color:C.quality,
    trigger:":WorkflowTrigger {type:TOC, status:PENDING} detected — processes URGENT first",
    latency:"< 30 min from trigger creation to auth decision",
    rules:["R-06","R-07","R-08","R-09","R-10","R-11","R-12"],
    fed:["CMS_LCD_NCD","HCPCS_API","NPI_REGISTRY","CMS_OASIS","NCQA_HEDIS","LOINC"],
    outputs:[":ServiceAuth",":HHAAssignment",":HEDISGapFlag","CarePlan stub","48h call task"],
    steps:[
      "Pull member coverage: Medicare/Medicaid/MA mix, benefit limits, prior auth history",
      "Resolve coverage pathway (R-06): Medicare HH requires homebound + skilled; Medicaid PCS requires functional threshold",
      "If HOME_HEALTH_ORDERED: validate against LCD (R-07); if not ordered: evaluate clinical need from DX + ADL score",
      "Assign HCPCS code per payer (R-08): T1019 Medicaid, 99509 Medicare/MA, G0151/G0152 PT/OT",
      "Quality-match HHA (R-10): NPI Registry → in-network filter → OASIS outcome ranking → ASSIGNED_TO edge",
      "Stamp HEDIS TFL gap (R-11) with 7d/30d windows; stamp COA gap if age≥65 and no ADL assessment (R-12)",
      "Generate care plan stub: HHA referral, medication reconciliation flag, 48h telephonic call task, care manager assignment",
    ]},
  { id:"AW-03", name:"Prior Authorization Agent",      icon:"📋",  color:C.benefits,
    trigger:"Auth request for home health or PCS service; also invoked by AW-02",
    latency:"< 30 seconds vs 45 min manual review",
    rules:["R-06","R-07","R-08"],
    fed:["CMS_LCD_NCD","HCPCS_API","ICD10_API","MEDICAID_LTSS"],
    outputs:[":ServiceAuth {status:APPROVED|DENIED|PENDING_INFO}"],
    steps:[
      "Resolve payer: Medicare HH (Part A/B), Medicaid PCS (state plan or 1915c waiver), MA supplemental (SSBCI)",
      "Fetch LCD for member's MAC jurisdiction from CMS Coverage DB",
      "Check all criteria: homebound status, physician certification, skilled service need, ADL score vs state threshold",
      "Verify HCPCS code validity for payer type — T1019 is Medicaid-only, 99509 is Medicare/MA",
      "Check benefit limits remaining (authorized hours vs plan maximum for period)",
      "Generate auth decision with evidence citations; flag for human review if PENDING_INFO",
    ]},
  { id:"AW-04", name:"HEDIS Gap Closure Agent",        icon:"⭐",  color:C.quality,
    trigger:"HEDIS gap flag created (R-11/R-12) OR monthly measurement year scan",
    latency:"Real-time flag; gap closure tracked continuously",
    rules:["R-11","R-12"],
    fed:["NCQA_HEDIS","LOINC","ICD10_API","CMS_OASIS"],
    outputs:[":HEDISGapFlag {status:CLOSED}","STAR rating projection update"],
    steps:[
      "TFL: Monitor 7-day and 30-day post-discharge windows for follow-up claim or scheduled appointment",
      "TFL: Auto-close gap when qualifying follow-up claim received (PCP/specialist E&M within window)",
      "COA: Identify members 65+ missing functional status assessment — add to care manager worklist",
      "COA: Close gap when Katz/Barthel/OASIS assessment completed and claim received with LOINC code",
      "Track gap closure rate vs STAR measure threshold — flag plan if trending below contract target",
    ]},
  { id:"AW-05", name:"SDOH + Risk Escalation Agent",   icon:"🏘️",  color:C.sdoh,
    trigger:"Z74.2 detected in DX_CODES OR SDOH screen positive OR risk_tier changes to 4–5",
    latency:"Real-time on Z-code detection",
    rules:["R-04","R-13"],
    fed:["GRAVITY_SDOH","ICD10_API","MEDICAID_LTSS"],
    outputs:[":SDOHFlag",":CommunityResourceReferral","Risk tier escalation","Urgent outreach task"],
    steps:[
      "Detect Z74.2 (no able caregiver) — immediate escalation: home care cannot succeed without support plan",
      "Check Gravity SDOH value sets for Z59.x (housing) and Z55–Z65 (social determinants) in DX_CODES",
      "Identify eligible community resources: Area Agency on Aging, Meals on Wheels, HCBS waiver slots",
      "Adjust risk tier upward if SDOH flag + Z74.x co-present (R-04 re-computation)",
      "Alert care manager with structured action plan: resource referral + outreach timeline",
    ]},
];

// ══════════════════════════════════════════════════════════════════════════════
// CIPHER SPEC
// ══════════════════════════════════════════════════════════════════════════════
const CIPHER_SPEC = {
  algorithm:"SHA-256",
  description:"Stable hash of five canonical components. Same cipher = same care pathway. Enables cohort batching, change detection, and agent routing without hardcoded rules.",
  components:[
    { pos:1, name:"entity_qid",     example:"Q22906178",                                              desc:"Wikidata QID or internal UUID" },
    { pos:2, name:"p31_type_qids",  example:"Q4006979,Q784794",                                       desc:"Comma-sorted P31 type QIDs" },
    { pos:3, name:"code_set_ids",   example:"HCPCS:T1019,ICD10:Z74.1,LOINC:72133-2,SNOMED:129005007", desc:"Sorted code set identifiers" },
    { pos:4, name:"fed_source_ids", example:"CMS_LCD_NCD,HCPCS_API,ICD10_API,LOINC,NPI_REGISTRY",     desc:"Sorted active federation source IDs" },
    { pos:5, name:"primary_facets", example:"Benefits,Clinical,Member,Regulatory",                    desc:"Comma-sorted primary facet labels" },
  ],
  toc_use_cases:[
    { use:"Cohort batching",    desc:"Members with same cipher share care pathway — batch-authorize same services, apply same HEDIS measures, assign same HHA cohort" },
    { use:"Change detection",   desc:"If cipher changes between weekly runs, something material changed — new diagnosis, new payer, coverage pathway shift — trigger care manager review" },
    { use:"Template matching",  desc:"New discharge cipher matches existing high-risk cohort → immediately inherit care plan template without re-evaluation" },
    { use:"Agent routing",      desc:"Cipher encodes which agents process this member — no hardcoded routing tables needed; cipher drives workflow selection" },
    { use:"SLA tracking",       desc:"Workflow triggers carry cipher → SLA compliance aggregated by care pathway, not just by individual member" },
  ],
  worked_example:{
    label:"Member discharged from SNF with dementia + Z74.2",
    raw:"MEMBER:M10042|Q12136,Q4006979|ICD10:F01.50,ICD10:Z74.2,HCPCS:T1019,LOINC:72133-2|CMS_LCD_NCD,GRAVITY_SDOH,ICD10_API,LOINC,NPI_REGISTRY|Clinical,Member,Regulatory,SDOH",
    cipher:"SHA256(above) → distinct hash — no collision with standard home health member whose cipher excludes Z74.2 and GRAVITY_SDOH",
    note:"This cipher is distinct from a standard home health discharge because Z74.2 adds GRAVITY_SDOH to fed_source_ids and SDOH to primary_facets. The cipher change triggers SDOH escalation agent automatically.",
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// NAMED QUERIES (10)
// ══════════════════════════════════════════════════════════════════════════════
const TOC_QUERIES = [
  { id:"SQ-01", label:"SF", name:"Poll — unprocessed discharges",
    purpose:"Primary 15-min Snowflake harvest. Returns all unprocessed rows ordered by discharge time.",
    lang:"snowflake",
    code:`SELECT ENCOUNTER_ID, MEMBER_ID, MBI, MEDICAID_ID,
  FACILITY_NPI, ADMIT_DT, DISCHARGE_DT,
  DISCHARGE_SETTING, DISCHARGE_DISP, LOS_DAYS,
  PRIMARY_DX_ICD10, DX_CODES, MS_DRG,
  DISCHARGE_ADL_SCORE, ADL_TOOL,
  LACE_SCORE, PRIOR_ADMITS_90D, THIRTY_DAY_READMIT_RISK,
  HOME_HEALTH_ORDERED, HH_AGENCY_NPI, FOLLOWUP_DT
FROM CLINICAL_OPS.DISCHARGES.ADT_DISCHARGE_EVENTS
WHERE DISCHARGE_DT >= DATEADD('minute', -15, CURRENT_TIMESTAMP)
  AND PROCESSED = FALSE
  AND DISCHARGE_DISP != '20'
ORDER BY DISCHARGE_DT ASC` },

  { id:"SQ-02", label:"SF", name:"Stream CDC setup + consume",
    purpose:"Preferred over polling. Near-real-time on INSERT. Wrap consume in transaction — only commit after Chrystallum success.",
    lang:"snowflake",
    code:`-- One-time setup:
CREATE OR REPLACE STREAM CLINICAL_OPS.DISCHARGES.DISCHARGE_STREAM
  ON TABLE CLINICAL_OPS.DISCHARGES.ADT_DISCHARGE_EVENTS
  APPEND_ONLY = TRUE;

-- Agent consume loop (run in transaction):
BEGIN;
  SELECT ENCOUNTER_ID, MEMBER_ID, MBI, MEDICAID_ID,
    FACILITY_NPI, ADMIT_DT, DISCHARGE_DT,
    DISCHARGE_SETTING, DISCHARGE_DISP, LOS_DAYS,
    PRIMARY_DX_ICD10, DX_CODES, MS_DRG,
    DISCHARGE_ADL_SCORE, ADL_TOOL, LACE_SCORE,
    PRIOR_ADMITS_90D, THIRTY_DAY_READMIT_RISK,
    HOME_HEALTH_ORDERED, HH_AGENCY_NPI,
    METADATA\\\$ACTION, METADATA\\\$ROW_ID
  FROM CLINICAL_OPS.DISCHARGES.DISCHARGE_STREAM
  WHERE METADATA\\\$ACTION = 'INSERT'
    AND DISCHARGE_DISP != '20';
COMMIT;` },

  { id:"SQ-03", label:"SF", name:"High-risk filter with RISK_FLAG",
    purpose:"Secondary filter on poll results. ARRAY_CONTAINS detects Z74.x in DX_CODES array.",
    lang:"snowflake",
    code:`SELECT e.*,
  CASE
    WHEN e.LACE_SCORE >= 10 AND
         ARRAY_CONTAINS('Z74.2'::VARIANT, e.DX_CODES) THEN 'TIER_5_CRITICAL'
    WHEN e.LACE_SCORE >= 10                            THEN 'HIGH_READMIT'
    WHEN ARRAY_CONTAINS('Z74.2'::VARIANT, e.DX_CODES) THEN 'NO_CAREGIVER'
    WHEN ARRAY_CONTAINS('Z74.1'::VARIANT, e.DX_CODES) THEN 'ADL_NEED'
    WHEN e.PRIOR_ADMITS_90D >= 2                       THEN 'HIGH_UTILIZER'
    WHEN e.THIRTY_DAY_READMIT_RISK >= 0.25             THEN 'MODEL_FLAG'
    ELSE 'STANDARD'
  END AS RISK_FLAG
FROM CLINICAL_OPS.DISCHARGES.ADT_DISCHARGE_EVENTS e
WHERE e.DISCHARGE_DT >= DATEADD('hour', -48, CURRENT_TIMESTAMP)
  AND e.PROCESSED = FALSE
  AND DISCHARGE_DISP != '20'
ORDER BY e.DISCHARGE_DT ASC` },

  { id:"SQ-04", label:"SF", name:"Mark processed (post-ingestion)",
    purpose:"Called ONLY after Chrystallum MERGE confirmed. Prevents reprocessing. Pass encounter IDs as list.",
    lang:"snowflake",
    code:`UPDATE CLINICAL_OPS.DISCHARGES.ADT_DISCHARGE_EVENTS
SET PROCESSED = TRUE,
    PROCESSED_AT = CURRENT_TIMESTAMP
WHERE ENCOUNTER_ID IN (%(encounter_ids)s)
  AND PROCESSED = FALSE` },

  { id:"CQ-01", label:"Cypher", name:"Ingest discharge + member match",
    purpose:"Core ingestion. MERGE on encounter_id. Links to :Member via MBI/Medicaid_ID/member_id.",
    lang:"cypher",
    code:`MERGE (de:DischargeEvent {encounter_id: $enc_id})
ON CREATE SET
  de.admit_dt       = datetime($admit_dt),
  de.discharge_dt   = datetime($discharge_dt),
  de.setting        = $setting,
  de.disposition    = $disposition,
  de.los_days       = $los_days,
  de.ms_drg         = $ms_drg,
  de.lace_score     = $lace_score,
  de.readmit_risk   = $readmit_risk,
  de.hh_ordered     = $hh_ordered,
  de.source         = 'SNOWFLAKE',
  de.created_at     = datetime()
WITH de
OPTIONAL MATCH (m:Member)
  WHERE m.member_id = $member_id
     OR m.mbi = $mbi
     OR m.medicaid_id = $medicaid_id
FOREACH (_ IN CASE WHEN m IS NOT NULL THEN [1] ELSE [] END |
  MERGE (m)-[:HAS_DISCHARGE {encounter_id: de.encounter_id}]->(de)
  SET m.last_discharge_dt = de.discharge_dt
)
WITH de
MERGE (fac:Provider {npi: $facility_npi})
  ON CREATE SET fac.type='FACILITY', fac.source='SNOWFLAKE'
MERGE (de)-[:DISCHARGED_FROM]->(fac)
RETURN de.encounter_id, de.discharge_dt` },

  { id:"CQ-02", label:"Cypher", name:"Expand DX_CODES → :Diagnosis, flag Z74.x",
    purpose:"UNWIND array per encounter. Flags ADL need and no-caregiver on :Member.",
    lang:"cypher",
    code:`MATCH (de:DischargeEvent {encounter_id: $enc_id})
UNWIND $dx_codes AS icd
MERGE (dx:Diagnosis {icd10_code: icd})
  ON CREATE SET dx.source='ICD10_API', dx.enriched=false
MERGE (de)-[:HAS_DIAGNOSIS]->(dx)
WITH de, icd
OPTIONAL MATCH (m:Member)-[:HAS_DISCHARGE]->(de)
FOREACH (_ IN CASE WHEN m IS NOT NULL AND icd STARTS WITH 'Z74' THEN [1] ELSE [] END |
  SET m.adl_need=true, m.adl_icd10=icd
)
FOREACH (_ IN CASE WHEN m IS NOT NULL AND icd = 'Z74.2' THEN [1] ELSE [] END |
  SET m.no_caregiver=true,
      m.institutionalization_risk='elevated'
)` },

  { id:"CQ-03", label:"Cypher", name:"Risk tier + WorkflowTrigger + HEDIS gap",
    purpose:"Computes tier 1–5, creates TOC workflow trigger, stamps TFL and COA HEDIS gaps.",
    lang:"cypher",
    code:`MATCH (m:Member)-[:HAS_DISCHARGE]->(de:DischargeEvent {encounter_id: $enc_id})
WITH m, de,
  CASE
    WHEN de.lace_score >= 10 AND m.no_caregiver = true THEN 5
    WHEN de.lace_score >= 10 OR  m.no_caregiver = true THEN 4
    WHEN de.readmit_risk >= 0.25 OR m.adl_need = true  THEN 3
    WHEN de.lace_score >= 7                            THEN 2
    ELSE 1
  END AS tier
SET m.risk_tier = tier, m.risk_computed_at = datetime()
MERGE (wf:WorkflowTrigger {type:'TOC', encounter_id: de.encounter_id})
ON CREATE SET
  wf.triggered_at = datetime(),
  wf.due_by       = datetime() + duration('PT48H'),
  wf.risk_tier    = tier,
  wf.status       = 'PENDING',
  wf.priority     = CASE WHEN tier >= 4 THEN 'URGENT' ELSE 'STANDARD' END
MERGE (m)-[:HAS_WORKFLOW]->(wf)
MERGE (tfl:HEDISGapFlag {measure:'TFL', year:date().year, member_id:m.member_id})
ON CREATE SET
  tfl.index_dt   = de.discharge_dt,
  tfl.window_7d  = date(de.discharge_dt) + duration('P7D'),
  tfl.window_30d = date(de.discharge_dt) + duration('P30D'),
  tfl.status     = 'OPEN'
MERGE (m)-[:HAS_HEDIS_GAP]->(tfl)
RETURN m.member_id, tier, wf.priority` },

  { id:"CQ-04", label:"Cypher", name:"Pending TOC worklist — URGENT first",
    purpose:"Care manager dashboard query. All pending TOC workflows ordered by priority and due_by.",
    lang:"cypher",
    code:`MATCH (m:Member)-[:HAS_WORKFLOW]->(wf:WorkflowTrigger {type:'TOC', status:'PENDING'})
OPTIONAL MATCH (m)-[:HAS_DISCHARGE]->(de:DischargeEvent {encounter_id: wf.encounter_id})
OPTIONAL MATCH (m)-[:HAS_DIAGNOSIS]->(dx:Diagnosis)
  WHERE dx.icd10_code STARTS WITH 'Z74'
RETURN m.member_id, m.risk_tier, wf.priority, wf.due_by,
       de.setting, de.lace_score, m.no_caregiver,
       collect(DISTINCT dx.icd10_code) AS adl_codes
ORDER BY
  CASE wf.priority WHEN 'URGENT' THEN 0 ELSE 1 END,
  wf.due_by ASC` },

  { id:"CQ-05", label:"Cypher", name:"HEDIS TFL gap auto-close on follow-up",
    purpose:"Runs when follow-up claim received. Closes gap if within 7d or 30d window.",
    lang:"cypher",
    code:`MATCH (m:Member {member_id: $member_id})-[:HAS_HEDIS_GAP]->(gap:HEDISGapFlag {measure:'TFL', status:'OPEN'})
WHERE date($followup_date) <= gap.window_30d
SET gap.status        = 'CLOSED',
    gap.closed_at     = datetime(),
    gap.followup_date = date($followup_date),
    gap.window_met    = CASE
      WHEN date($followup_date) <= gap.window_7d  THEN '7_DAY'
      ELSE '30_DAY'
    END
RETURN gap.measure, gap.window_met, m.member_id` },

  { id:"CQ-06", label:"Cypher", name:"Cipher invalidation + recompute queue",
    purpose:"Find members whose care pathway changed since last cipher computation.",
    lang:"cypher",
    code:`MATCH (m:Member)
WHERE m.cipher_computed_at < m.last_updated
   OR m.cipher IS NULL
RETURN m.member_id, m.risk_tier, m.cipher_computed_at, m.last_updated
ORDER BY m.last_updated DESC
LIMIT 500` },
];

// ══════════════════════════════════════════════════════════════════════════════
// FEDERATION SOURCES (13)
// ══════════════════════════════════════════════════════════════════════════════
const TOC_FED = [
  { id:"SNOWFLAKE_DISCHARGES", name:"Snowflake — Hospital Discharge Feed", color:C.sf,
    status:"planned",  role:"discharge_events",  prop:"encounter_id", node_type:"DischargeEvent",
    access:"api/stream", format:"SQL/JSON",
    url:"https://<account>.snowflakecomputing.com/api/v2/statements",
    url_template:"POST SQL: SELECT * FROM ADT_DISCHARGE_EVENTS WHERE PROCESSED=FALSE",
    note:"Primary ingestion source. REST API for polling; Snowflake Streams for CDC. Key-pair auth. PROCESSED flag prevents reprocessing." },
  { id:"ICD10_API",      name:"ICD-10-CM (NLM)",         color:C.clinical, status:"operational",
    role:"diagnosis_codes", prop:"icd10_code", node_type:"Diagnosis",
    access:"api", format:"JSON",
    url_template:"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms={code}",
    note:"Free, no key. Enriches :Diagnosis nodes with description and hierarchy. Z74 block = ADL dependency signal." },
  { id:"SNOMED_CT",      name:"SNOMED CT (NLM)",          color:C.clinical, status:"operational",
    role:"clinical_concepts", prop:"snomed_code", node_type:"ClinicalConcept",
    access:"api", format:"JSON",
    url_template:"https://browser.ihtsdotools.org/snowstorm/snomed-ct/MAIN/concepts?term={term}&limit=25",
    note:"SNOMED 129005007 = ADL. Hierarchy traversal gives clinical context depth for SCA scoring." },
  { id:"LOINC",          name:"LOINC (Regenstrief)",      color:C.clinical, status:"operational",
    role:"assessment_instruments", prop:"loinc_code", node_type:"AssessmentInstrument",
    access:"api", format:"JSON/FHIR",
    url_template:"https://fhir.loinc.org/CodeSystem/\$lookup?system=http://loinc.org&code={loinc_code}",
    note:"Katz: 72133-2. Barthel: 44177-1. OASIS M1800: 46522-4. Maps assessment tool items to computable scores for CQ-02 ADL capture." },
  { id:"HCPCS_API",      name:"HCPCS (CMS)",              color:C.benefits, status:"operational",
    role:"procedure_codes", prop:"hcpcs_code", node_type:"ProcedureCode",
    access:"download", format:"XLSX",
    url_template:"https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets/Alpha-Numeric-HCPCS",
    note:"T1019 = #1 home health code (18M+ units/yr). S5125 = attendant care. 99509 = home visit ADL. G0151/G0152 = PT/OT home health." },
  { id:"CMS_LCD_NCD",    name:"CMS Coverage Database",    color:C.benefits, status:"operational",
    role:"coverage_policy", prop:"lcd_id", node_type:"CoveragePolicy",
    access:"api", format:"JSON",
    url_template:"https://www.cms.gov/medicare-coverage-database/api/articles?keyword={term}&type=lcd",
    note:"LCD = Local Coverage Determination by MAC jurisdiction. Source of medical necessity criteria for R-07. Required for every Medicare home health auth." },
  { id:"NPI_REGISTRY",   name:"NPI Registry (NPPES)",     color:C.provider, status:"operational",
    role:"provider_identity", prop:"npi", node_type:"Provider",
    access:"api", format:"JSON",
    url_template:"https://npiregistry.cms.hhs.gov/api/?taxonomy_description=Home+Health+Aide&state={state}&limit=200",
    note:"Free public API. Taxonomy 376J00000X = Home Health Aide. Used for both facility NPI (from Snowflake) and HHA matching (R-10)." },
  { id:"CMS_OASIS",      name:"CMS OASIS (Home Health Compare)", color:C.quality, status:"operational",
    role:"provider_quality", prop:"oasis_agency_id", node_type:"QualityReport",
    access:"api", format:"JSON",
    url_template:"https://data.cms.gov/provider-data/api/1/datastore/query/97z8-de96/0",
    note:"Public HHA quality metrics: ADL improvement rate, hospitalization rate, ED utilization. Powers R-10 quality-adjusted HHA matching." },
  { id:"MEDICAID_LTSS",  name:"Medicaid LTSS (CMS)",      color:C.regulatory, status:"operational",
    role:"program_rules", prop:"medicaid_waiver_id", node_type:"WaiverProgram",
    access:"download", format:"PDF/HTML",
    url_template:"https://www.medicaid.gov/medicaid/long-term-services-supports/home-community-based-services/",
    note:"State 1915(c) HCBS waivers. Each state has own ADL eligibility threshold — Katz ≤3 in most. 56 state programs each a :WaiverProgram node." },
  { id:"GRAVITY_SDOH",   name:"Gravity Project / VSAC",   color:C.sdoh, status:"operational",
    role:"sdoh_concepts", prop:"sdoh_code", node_type:"SDOHConcept",
    access:"api", format:"JSON/FHIR",
    url_template:"https://vsac.nlm.nih.gov/valueset/2.16.840.1.113762.1.4.1247.126/expansion",
    note:"SDOH value sets: caregiver availability, housing instability, food insecurity. Z-code mapping. Powers R-13 SDOH-to-clinical bridge." },
  { id:"NCQA_HEDIS",     name:"NCQA / HEDIS",             color:C.quality, status:"planned",
    role:"quality_measures", prop:"hedis_measure_id", node_type:"QualityMeasure",
    access:"licensed", format:"PDF/Spec",
    url_template:"https://www.ncqa.org/hedis/measures/",
    note:"Licensed. TFL (Transitions of Care) — 7-day and 30-day follow-up windows. COA (Care for Older Adults) — functional assessment. Powers R-11/R-12." },
  { id:"RXNORM_API",     name:"RxNorm (NLM)",             color:C.behavioral, status:"operational",
    role:"drug_concepts", prop:"rxnorm_code", node_type:"Drug",
    access:"api", format:"JSON",
    url_template:"https://rxnav.nlm.nih.gov/REST/rxcui/{rxnorm_code}/allProperties.json",
    note:"Polypharmacy risk in discharge population: 5+ meds = elevated fall/cognitive risk. Med reconciliation is standard TOC care plan component." },
  { id:"CMS_OPEN_DATA",  name:"CMS Open Data",            color:C.financial, status:"operational",
    role:"utilization_benchmarks", prop:"cms_dataset_id", node_type:"UtilizationBenchmark",
    access:"api", format:"JSON",
    url_template:"https://data.cms.gov/provider-summary-by-type-of-service/",
    note:"Medicare utilization by service and geography. Enables PMPM benchmarking and regional cost variation analysis for R-04 risk scoring calibration." },
];

// ══════════════════════════════════════════════════════════════════════════════
// UI HELPERS
// ══════════════════════════════════════════════════════════════════════════════
function Tag({ label, color, size=8 }) {
  return <span style={{background:color+"20",border:`1px solid \${color}`,borderRadius:10,
    padding:"1px 7px",fontSize:size,color,fontWeight:"bold",margin:"1px",display:"inline-block"}}>{label}</span>;
}
function CopyBtn({ text }) {
  const [ok,setOk]=useState(false);
  return <button onClick={()=>{navigator.clipboard?.writeText(text);setOk(true);setTimeout(()=>setOk(false),1200);}}
    style={{background:ok?C.pass+"30":C.border,color:ok?C.pass:C.dim,
      border:`1px solid \${ok?C.pass:C.border}`,borderRadius:3,
      padding:"1px 8px",fontSize:7.5,cursor:"pointer",transition:"all .2s"}}>{ok?"✓":"copy"}</button>;
}
function SHead({ children, col=C.dim }) {
  return <div style={{fontSize:7.5,fontWeight:"bold",color:col,letterSpacing:"0.1em",
    textTransform:"uppercase",marginBottom:6}}>{children}</div>;
}
function Mono({ children, col=C.sf, s=8.5 }) {
  return <span style={{fontFamily:"'Courier New',monospace",fontSize:s,color:col}}>{children}</span>;
}
function Signal({ level }) {
  const c={HIGH:C.pass,MEDIUM:C.warn,LOW:C.dim,IGNORE:"#2A3A4A"};
  return <span style={{background:c[level]+"25",color:c[level],border:`1px solid \${c[level]}50`,
    borderRadius:3,padding:"1px 6px",fontSize:7.5,fontWeight:"bold"}}>{level}</span>;
}

// ── DOMAIN MAP TAB ─────────────────────────────────────────────────────────────
function DomainTab() {
  const [selP31, setSelP31] = useState(0);
  const pt = INSTANCE.p31_types[selP31];
  return (
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
      <div>
        <SHead col={C.sf}>SEED ENTITIES</SHead>
        {INSTANCE.seed_entities.map(e=>(
          <div key={e.qid||e.label} style={{display:"flex",gap:6,alignItems:"center",
            marginBottom:4,borderLeft:`2px solid \${e.primary?C.sf:C.border}`,paddingLeft:8}}>
            <Mono col={e.primary?C.sf:C.dim} s={8}>{e.qid}</Mono>
            <span style={{fontSize:9,color:e.primary?C.bright:C.dim,flex:1}}>{e.label}</span>
            <Tag label={e.etype} color={e.primary?C.sf:C.dim}/>
            {e.primary&&<Tag label="seed" color={C.warn}/>}
          </div>
        ))}
        <div style={{marginTop:12}}>
          <SHead col={C.regulatory}>CORPUS SCOPE</SHead>
          <div style={{background:C.panel,borderLeft:`3px solid \${C.regulatory}`,
            borderRadius:4,padding:"6px 10px",fontSize:8.5,color:C.bright}}>{INSTANCE.corpus_scope}</div>
        </div>
        <div style={{marginTop:12}}>
          <SHead col={C.benefits}>DISCHARGE DISPOSITIONS</SHead>
          {INSTANCE.discharge_dispositions.map(d=>(
            <div key={d.code} style={{display:"flex",gap:6,marginBottom:4,
              borderLeft:`2px solid \${d.color}`,paddingLeft:8,alignItems:"flex-start"}}>
              <Mono col={d.color} s={8.5}>{d.code}</Mono>
              <div>
                <span style={{fontSize:8.5,color:C.bright,fontWeight:"bold"}}>{d.label}</span>
                <div style={{fontSize:7.5,color:C.dim,marginTop:1}}>{d.pathway}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div>
        <SHead col={C.clinical}>P31 TYPE MAP</SHead>
        <div style={{display:"flex",gap:3,marginBottom:8,flexWrap:"wrap"}}>
          {INSTANCE.p31_types.map((t,i)=>(
            <button key={i} onClick={()=>setSelP31(i)}
              style={{border:`1px solid \${selP31===i?t.color:C.border}`,
                background:selP31===i?t.color+"20":C.panel,color:selP31===i?t.color:C.dim,
                borderRadius:4,padding:"3px 9px",fontSize:8,cursor:"pointer"}}>{t.label}</button>
          ))}
        </div>
        <div style={{border:`1px solid \${pt.color}40`,borderLeft:`3px solid \${pt.color}`,
          borderRadius:5,padding:10,marginBottom:10,background:C.panel}}>
          <div style={{fontWeight:"bold",color:pt.color,fontSize:10,marginBottom:2}}>{pt.label}</div>
          <div style={{fontSize:8,color:C.dim,marginBottom:8}}>{pt.role}</div>
          <div style={{display:"flex",gap:8,flexWrap:"wrap",marginBottom:8}}>
            <div><SHead>Nodes</SHead>{pt.chrystallum_nodes.map(n=><Tag key={n} label={n} color={pt.color}/>)}</div>
            <div><SHead>Facets</SHead>{pt.facets.map(f=><Tag key={f} label={f} color={FACET_COL[f]||C.dim}/>)}</div>
          </div>
          <SHead>In-corpus instances</SHead>
          {pt.in_corpus.map(inst=>(
            <div key={inst.qid||inst.label} style={{display:"flex",gap:5,marginBottom:3}}>
              {inst.qid&&<Mono col={pt.color} s={7.5}>{inst.qid}</Mono>}
              <span style={{fontSize:8.5,color:C.bright}}>{inst.label}</span>
              <Tag label={inst.etype} color={C.dim} size={7}/>
            </div>
          ))}
          <div style={{marginTop:8,background:pt.color+"10",borderRadius:3,
            padding:"4px 7px",fontSize:7.5,color:pt.color}}>{pt.promotion_rule}</div>
        </div>
        <SHead col={C.quality}>SUBCLASS SIGNAL MAP</SHead>
        {INSTANCE.subclass_signals.map(s=>(
          <div key={s.qid||s.label} style={{display:"flex",gap:6,marginBottom:3,
            opacity:s.signal==="IGNORE"?0.35:1,alignItems:"flex-start"}}>
            <Signal level={s.signal}/>
            <div>
              <Mono col={C.dim} s={7.5}>{s.qid}</Mono>
              <span style={{fontSize:8.5,color:C.bright,marginLeft:5}}>{s.label}</span>
              <div style={{fontSize:7.5,color:C.dim,marginTop:1}}>{s.reason}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── WORKFLOWS TAB ──────────────────────────────────────────────────────────────
function WorkflowsTab() {
  const [sel,setSel]=useState("AW-01");
  const wf=TOC_WORKFLOWS.find(w=>w.id===sel);
  return (
    <div style={{display:"grid",gridTemplateColumns:"220px 1fr",gap:12}}>
      <div>
        {TOC_WORKFLOWS.map(w=>(
          <div key={w.id} onClick={()=>setSel(w.id)}
            style={{border:`1px solid \${sel===w.id?w.color:C.border}`,
              borderLeft:`3px solid \${w.color}`,borderRadius:4,
              padding:"8px 10px",marginBottom:6,cursor:"pointer",
              background:sel===w.id?w.color+"10":C.panel}}>
            <div style={{fontWeight:"bold",color:w.color,fontSize:9.5}}>{w.icon} {w.name}</div>
            <div style={{fontSize:7.5,color:C.dim,marginTop:2}}>{w.trigger}</div>
          </div>
        ))}
      </div>
      {wf&&(
        <div style={{border:`1px solid \${wf.color}40`,borderLeft:`3px solid \${wf.color}`,
          borderRadius:6,padding:12,background:C.panel}}>
          <div style={{fontWeight:"bold",color:wf.color,fontSize:13,marginBottom:6}}>{wf.icon} {wf.name}</div>
          <div style={{display:"flex",gap:6,flexWrap:"wrap",marginBottom:10}}>
            <div style={{background:wf.color+"15",borderRadius:4,padding:"3px 10px",
              fontSize:8,color:wf.color}}>⚡ {wf.latency}</div>
            {wf.rules.map(r=><Tag key={r} label={r} color={wf.color}/>)}
          </div>
          <SHead col={C.dim}>STEPS</SHead>
          {wf.steps.map((s,i)=>(
            <div key={i} style={{display:"flex",gap:8,marginBottom:6,alignItems:"flex-start"}}>
              <div style={{background:wf.color,color:"white",borderRadius:"50%",
                width:18,height:18,display:"flex",alignItems:"center",justifyContent:"center",
                fontSize:8,fontWeight:"bold",flexShrink:0,marginTop:1}}>{i+1}</div>
              <div style={{fontSize:9,color:C.bright,lineHeight:1.5}}>{s}</div>
            </div>
          ))}
          <div style={{marginTop:10,display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
            <div><SHead col={C.dim}>FEDERATION</SHead>
              <div style={{display:"flex",flexWrap:"wrap",gap:2}}>
                {wf.fed.map(f=><Tag key={f} label={f} color={wf.color} size={7.5}/>)}
              </div>
            </div>
            <div><SHead col={C.dim}>OUTPUTS</SHead>
              <div style={{display:"flex",flexWrap:"wrap",gap:2}}>
                {wf.outputs.map(o=><Tag key={o} label={o} color={C.benefits} size={7.5}/>)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── RULES TAB ─────────────────────────────────────────────────────────────────
function RulesTab() {
  const [sel,setSel]=useState(null);
  return (
    <div>
      {TOC_RULES.map(r=>(
        <div key={r.id} style={{border:`1px solid \${sel===r.id?C.clinical:C.border}`,
          borderLeft:`3px solid \${C.clinical}`,borderRadius:4,marginBottom:5}}>
          <div onClick={()=>setSel(sel===r.id?null:r.id)}
            style={{padding:"6px 10px",cursor:"pointer",display:"flex",
              gap:8,alignItems:"center",background:C.panel}}>
            <Mono col={C.clinical} s={8.5}>{r.id}</Mono>
            <span style={{fontWeight:"bold",color:C.bright,fontSize:9.5,flex:1}}>{r.name}</span>
            <div style={{display:"flex",gap:2}}>
              {r.facets.slice(0,3).map(f=><Tag key={f} label={f} color={FACET_COL[f]||C.dim} size={7}/>)}
            </div>
            <span style={{color:C.dim}}>{sel===r.id?"▲":"▼"}</span>
          </div>
          {sel===r.id&&(
            <div style={{padding:"8px 10px",background:C.bg,borderTop:`1px solid \${C.border}`,
              display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
              <div>
                <SHead col={C.warn}>TRIGGER</SHead>
                <div style={{fontSize:8.5,color:C.dim,marginBottom:8,lineHeight:1.5}}>{r.trigger}</div>
                <SHead col={C.clinical}>ACTION</SHead>
                <div style={{fontFamily:"'Courier New',monospace",fontSize:8,color:C.clinical,
                  background:C.clinical+"08",borderRadius:3,padding:"5px 7px",lineHeight:1.5}}>{r.action}</div>
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

// ── QUERIES TAB ────────────────────────────────────────────────────────────────
function QueriesTab() {
  const [sel,setSel]=useState("SQ-01");
  const q=TOC_QUERIES.find(q=>q.id===sel);
  const col = q?.lang==="snowflake" ? C.sf : C.neo;
  return (
    <div style={{display:"grid",gridTemplateColumns:"200px 1fr",gap:12}}>
      <div>
        {["SF","Cypher"].map(group=>(
          <div key={group} style={{marginBottom:8}}>
            <div style={{fontSize:7.5,color:C.dim,fontWeight:"bold",
              letterSpacing:"0.1em",marginBottom:4}}>{group==="SF"?"SNOWFLAKE SQL":"NEO4J CYPHER"}</div>
            {TOC_QUERIES.filter(q=>q.label===group).map(q=>(
              <div key={q.id} onClick={()=>setSel(q.id)}
                style={{border:`1px solid \${sel===q.id?(group==="SF"?C.sf:C.neo):C.border}`,
                  borderLeft:`3px solid \${sel===q.id?(group==="SF"?C.sf:C.neo):C.border}`,
                  borderRadius:3,padding:"5px 8px",marginBottom:3,cursor:"pointer",
                  background:sel===q.id?(group==="SF"?C.sf:C.neo)+"12":C.panel}}>
                <div style={{fontWeight:"bold",
                  color:sel===q.id?(group==="SF"?C.sf:C.neo):C.dim,fontSize:8.5}}>{q.id}</div>
                <div style={{fontSize:7.5,color:C.dim,marginTop:1}}>{q.name}</div>
              </div>
            ))}
          </div>
        ))}
      </div>
      {q&&(
        <div>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <Tag label={q.label} color={col}/>
            <span style={{fontWeight:"bold",color:col,fontSize:11}}>{q.name}</span>
          </div>
          <div style={{fontSize:8.5,color:C.dim,marginBottom:8,
            background:col+"08",borderRadius:3,padding:"4px 8px"}}>{q.purpose}</div>
          <div style={{display:"flex",justifyContent:"flex-end",marginBottom:4}}>
            <CopyBtn text={q.code}/>
          </div>
          <pre style={{fontFamily:"'Courier New',monospace",fontSize:8.5,color:col,
            background:col+"08",borderRadius:4,padding:10,margin:0,
            overflow:"auto",maxHeight:400,whiteSpace:"pre-wrap",lineHeight:1.6}}>{q.code}</pre>
        </div>
      )}
    </div>
  );
}

// ── CIPHER TAB ─────────────────────────────────────────────────────────────────
function CipherTab() {
  return (
    <div>
      <div style={{background:C.panel,border:`1px solid \${C.sf}40`,borderRadius:8,padding:12,marginBottom:12}}>
        <SHead col={C.sf}>CIPHER SPECIFICATION — {CIPHER_SPEC.algorithm}</SHead>
        <div style={{fontSize:8.5,color:C.dim,marginBottom:10,lineHeight:1.5}}>{CIPHER_SPEC.description}</div>
        {CIPHER_SPEC.components.map(c=>(
          <div key={c.pos} style={{display:"flex",gap:10,marginBottom:5,
            borderLeft:`2px solid \${C.sf}`,paddingLeft:8}}>
            <div style={{fontWeight:"bold",color:C.sf,minWidth:16,fontSize:9}}>{c.pos}</div>
            <div>
              <Mono col={C.sf}>{c.name}</Mono>
              <span style={{fontSize:8,color:C.dim,marginLeft:8}}>{c.desc}</span>
              <div style={{fontSize:7.5,color:C.financial,marginTop:1}}>e.g. {c.example}</div>
            </div>
          </div>
        ))}
      </div>
      <div style={{background:C.panel,border:`1px solid \${C.border}`,borderRadius:6,padding:12,marginBottom:12}}>
        <SHead>TOC-SPECIFIC USE CASES</SHead>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8}}>
          {CIPHER_SPEC.toc_use_cases.map(u=>(
            <div key={u.use} style={{border:`1px solid \${C.border}`,borderRadius:4,padding:"7px 10px"}}>
              <div style={{fontWeight:"bold",color:C.sf,fontSize:9,marginBottom:3}}>{u.use}</div>
              <div style={{fontSize:8.5,color:C.dim,lineHeight:1.4}}>{u.desc}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{background:C.bg,border:`1px solid \${C.border}`,borderRadius:6,padding:10}}>
        <SHead>WORKED EXAMPLE — {CIPHER_SPEC.worked_example.label}</SHead>
        <div style={{fontFamily:"monospace",fontSize:7.5,color:C.sf,
          background:C.sf+"08",borderRadius:4,padding:8,marginBottom:6,
          wordBreak:"break-all",lineHeight:1.6}}>{CIPHER_SPEC.worked_example.raw}</div>
        <div style={{fontFamily:"monospace",fontSize:7.5,color:C.neo,
          background:C.neo+"10",borderRadius:4,padding:"5px 8px",marginBottom:6}}>{CIPHER_SPEC.worked_example.cipher}</div>
        <div style={{fontSize:8,color:C.sdoh,fontStyle:"italic"}}>{CIPHER_SPEC.worked_example.note}</div>
      </div>
    </div>
  );
}

// ── FEDERATION TAB ─────────────────────────────────────────────────────────────
function FedTab() {
  const [sel,setSel]=useState(null);
  return (
    <div>
      {TOC_FED.map(src=>(
        <div key={src.id} style={{border:`1px solid \${src.color}30`,
          borderLeft:`3px solid \${src.color}`,borderRadius:4,marginBottom:5}}>
          <div onClick={()=>setSel(sel===src.id?null:src.id)}
            style={{padding:"6px 10px",cursor:"pointer",display:"flex",
              gap:8,alignItems:"center",background:C.panel}}>
            <div style={{width:8,height:8,borderRadius:"50%",
              background:STATUS_COL[src.status],flexShrink:0}}/>
            <span style={{fontWeight:"bold",color:src.color,fontSize:9.5,flex:1}}>{src.name}</span>
            <Tag label={src.role} color={C.dim} size={7}/>
            <Tag label={`:\${src.node_type}`} color={src.color} size={7.5}/>
            <Tag label={src.access} color={C.dim} size={7}/>
            <span style={{color:C.dim}}>{sel===src.id?"▲":"▼"}</span>
          </div>
          {sel===src.id&&(
            <div style={{padding:"8px 10px",background:C.bg,borderTop:`1px solid \${C.border}`,
              display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
              <div>
                <SHead>URL TEMPLATE</SHead>
                <div style={{fontFamily:"monospace",fontSize:7.5,color:src.color,
                  wordBreak:"break-all",marginBottom:5}}>{src.url_template}</div>
                <div style={{display:"flex",gap:4,flexWrap:"wrap"}}>
                  <CopyBtn text={src.url_template}/>
                  <Tag label={`prop: \${src.prop}`} color={C.dim} size={7.5}/>
                </div>
              </div>
              <div style={{fontSize:8.5,color:C.dim,fontStyle:"italic",lineHeight:1.5}}>{src.note}</div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── ASSESSMENT TOOLS TAB ───────────────────────────────────────────────────────
function AssessmentTab() {
  const [sel,setSel]=useState(0);
  const t=INSTANCE.assessment_tools[sel];
  return (
    <div>
      <div style={{display:"flex",gap:4,marginBottom:10,flexWrap:"wrap"}}>
        {INSTANCE.assessment_tools.map((tool,i)=>(
          <button key={i} onClick={()=>setSel(i)}
            style={{border:`1px solid \${sel===i?C.clinical:C.border}`,
              background:sel===i?C.clinical+"20":C.panel,color:sel===i?C.clinical:C.dim,
              borderRadius:4,padding:"3px 10px",fontSize:8.5,cursor:"pointer"}}>{tool.name}</button>
        ))}
      </div>
      <div style={{background:C.panel,border:`1px solid \${C.clinical}40`,
        borderLeft:`3px solid \${C.clinical}`,borderRadius:6,padding:12}}>
        <div style={{fontWeight:"bold",color:C.clinical,fontSize:11,marginBottom:6}}>{t.name}</div>
        <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:10,marginBottom:10}}>
          {[["SCALE",t.range,"bright"],["THRESHOLD",t.threshold,"warn"],["USE",t.use,"dim"],
            ["LOINC",t.loinc||"—","clinical"]].map(([l,v,c])=>(
            <div key={l} style={{borderLeft:`2px solid \${C[c]||C.dim}`,paddingLeft:8}}>
              <div style={{fontSize:7.5,color:C.dim}}>{l}</div>
              <div style={{fontSize:8.5,color:C[c]||C.dim,marginTop:1}}>{v}</div>
            </div>
          ))}
        </div>
        <SHead col={C.dim}>DOMAINS ({t.fields.length})</SHead>
        <div style={{display:"flex",flexWrap:"wrap",gap:4}}>
          {t.fields.map(f=>(
            <div key={f} style={{background:C.clinical+"15",border:`1px solid \${C.clinical}40`,
              borderRadius:4,padding:"3px 8px",fontSize:8,color:C.clinical}}>{f}</div>
          ))}
        </div>
      </div>
      <div style={{marginTop:12,background:C.panel,border:`1px solid \${C.border}`,
        borderRadius:6,padding:10}}>
        <SHead>SNOWFLAKE COLUMN MAPPING</SHead>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:8,fontSize:8.5}}>
          {[
            ["DISCHARGE_ADL_SCORE","Numeric score at discharge","→ AssessmentResult.score"],
            ["ADL_TOOL","Tool name: MDS|OASIS|KATZ…","→ AssessmentResult.tool"],
            ["LACE_SCORE","Readmission risk proxy","→ DischargeEvent.lace_score"],
          ].map(([col,desc,maps])=>(
            <div key={col} style={{borderLeft:`2px solid \${C.sf}`,paddingLeft:8}}>
              <Mono col={C.sf} s={8}>{col}</Mono>
              <div style={{color:C.dim,marginTop:1}}>{desc}</div>
              <div style={{color:C.neo,marginTop:1,fontSize:7.5}}>{maps}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── ROOT ───────────────────────────────────────────────────────────────────────
export default function App() {
  const [view,setView]=useState("domain");
  const VIEWS=[
    ["domain",    "Domain Map"],
    ["workflows", `Workflows (\${TOC_WORKFLOWS.length})`],
    ["rules",     `Rules (\${TOC_RULES.length})`],
    ["queries",   `Queries (\${TOC_QUERIES.length})`],
    ["cipher",    "Cipher"],
    ["fed",       `Federation (\${TOC_FED.length})`],
    ["assess",    "Assessment Tools"],
  ];
  return (
    <div style={{background:C.bg,minHeight:"100vh",padding:16,
      fontFamily:"'Courier New',monospace",color:C.bright}}>
      <div style={{borderBottom:`1px solid \${C.border}`,paddingBottom:12,marginBottom:14}}>
        <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:4}}>
          <span style={{fontSize:8,color:C.dim,letterSpacing:"0.15em"}}>CHRYSTALLUM · AGENT CONSTITUTION</span>
          {[["Snowflake",C.sf],["→ Neo4j",C.neo],["→ TOC Agent",C.quality]].map(([l,c])=>(
            <span key={l} style={{background:c,color:"white",borderRadius:4,
              padding:"1px 8px",fontSize:8,fontWeight:"bold"}}>{l}</span>
          ))}
        </div>
        <div style={{fontSize:18,fontWeight:"bold",color:C.bright,marginBottom:2}}>
          Transition of Care — Agent Constitution
        </div>
        <div style={{fontSize:9,color:C.dim,marginBottom:6}}>{INSTANCE.description}</div>
        <div style={{display:"flex",gap:8,flexWrap:"wrap",fontSize:8,color:C.dim}}>
          <span>🌱 {INSTANCE.seed_entities.length} seed entities</span>
          <span>·</span><span>🤖 {TOC_WORKFLOWS.length} agent workflows</span>
          <span>·</span><span>📋 {TOC_RULES.length} rules</span>
          <span>·</span><span>🔍 {TOC_QUERIES.length} named queries</span>
          <span>·</span><span>🔗 {TOC_FED.length} federation sources</span>
          <span>·</span><span>📏 {INSTANCE.assessment_tools.length} assessment tools</span>
        </div>
        <div style={{marginTop:8,background:C.sf+"10",border:`1px solid \${C.sf}30`,
          borderRadius:4,padding:"5px 10px",fontSize:8,color:C.sf}}>
          AGENT INSTRUCTION: This is your domain constitution. 
          Snowflake discharge feed is the primary event source. 
          Replace INSTANCE to instantiate for any post-acute care domain.
          All rules, cipher, and federation sources are reusable infrastructure.
        </div>
      </div>
      <div style={{display:"flex",gap:0,borderBottom:`1px solid \${C.border}`,marginBottom:14,flexWrap:"wrap"}}>
        {VIEWS.map(([k,l])=>(
          <button key={k} onClick={()=>setView(k)}
            style={{border:"none",background:"transparent",padding:"6px 12px",fontSize:8.5,
              cursor:"pointer",color:view===k?C.sf:C.dim,fontWeight:view===k?"bold":"normal",
              borderBottom:view===k?`2px solid \${C.sf}`:"2px solid transparent"}}>
            {l}
          </button>
        ))}
      </div>
      {view==="domain"    && <DomainTab/>}
      {view==="workflows" && <WorkflowsTab/>}
      {view==="rules"     && <RulesTab/>}
      {view==="queries"   && <QueriesTab/>}
      {view==="cipher"    && <CipherTab/>}
      {view==="fed"       && <FedTab/>}
      {view==="assess"    && <AssessmentTab/>}
    </div>
  );
}
