import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — DOMAIN INITIATOR (DI) CONSTITUTION                          ║
// ║  Pipeline: QID → LCSH Resolution → SubjectConcept → Facet Wiring          ║
// ║  Self-describing: data constants below are mirrored as SYS_ nodes in Neo4j ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  loc:"#003366", wikidata:"#006699", facet:"#D4A017",
  neo:"#00C2A8", cypher:"#B5860D",
  concept:"#6B46C1", router:"#2E8B57", curation:"#E07C3E",
  pass:"#2ECC71", warn:"#F5A623", fail:"#E74C3C",
};

const STATUS_COL = { operational:C.pass, planned:C.warn, verified:C.pass, lcsh_ceiling:C.warn };

// ══════════════════════════════════════════════════════════════════════════════
// DESIGN PRINCIPLES — agent reads these to understand DI architecture
// ══════════════════════════════════════════════════════════════════════════════
const PRINCIPLES = [
  { id:"DI-01", name:"Code = I/O shell; reasoning = LLM; data = graph",
    desc:"The DI agent's code should contain ONLY I/O (API calls, file reads, graph writes). All reasoning belongs to LLM calls. All data (patches, thresholds, patterns, policies) belongs in the graph as SYS_ nodes. Target: 906 lines of code reducible to ~50 lines of I/O." },
  { id:"DI-02", name:"LLM cannot generate sh-IDs",
    desc:"LCSH subject heading IDs (sh85115176, sh2008106708) are opaque numeric codes with no semantic pattern. LLMs hallucinate them 100% of the time. The correct pipeline: LLM outputs heading STRINGS only, LoC suggest2 API resolves IDs atomically, SKOS endpoint verifies." },
  { id:"DI-03", name:"Cipher = deterministic vertex address",
    desc:"SHA-256(\"SUBJECT_CONCEPT|{concept_qid}|{lcsh_sh_id}\") produces a deterministic cipher. Given any QID+LCSH pair, any agent can compute the cipher and jump directly to the vertex — no graph traversal needed. Uses the CONCEPT's QID, never the seed QID." },
  { id:"DI-04", name:"LCSH ceiling — QID differentiates",
    desc:"Some concepts (Senate, Assemblies) lack dedicated LCSH headings — they share a parent heading (Rome--Politics and government). The cipher is still unique because each concept has a distinct Wikidata QID. Status = lcsh_ceiling." },
  { id:"DI-05", name:"Demographic is inherently secondary",
    desc:"Demography is an analytical lens applied across facets, not a primary library subject. No LCSH heading routes to Demographic as primary. It appears as secondary on Social, Political, and Economic concepts." },
  { id:"DI-06", name:"FacetRouter replaces all pattern-matching code",
    desc:"The SYS_FacetRouter nodes in the graph contain LCSH heading patterns with match_type (contains/exact) and facet assignments. An agent classifies a heading by querying the graph — no if/elif chains in code." },
  { id:"DI-07", name:"CurationDecision replaces KNOWN_PATCHES",
    desc:"Every human override decision (mapping a concept to a specific LCSH heading) is stored as a SYS_CurationDecision node wired to its SubjectConcept. An agent queries these before attempting automated resolution." },
];

// ══════════════════════════════════════════════════════════════════════════════
// NODE TYPE SCHEMAS — maps to SYS_NodeType in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const NODE_TYPES = [
  { name:"SubjectConcept", status:"operational", color:C.concept,
    desc:"A domain-specific thematic anchor — one facet of a domain's knowledge. MERGE key is subject_id. Each concept is wired to Facet nodes and optionally to CurationDecision nodes.",
    required_props:[
      { name:"subject_id",      type:"string",  pattern:"subj_{qid_lowercase}", desc:"Unique MERGE key" },
      { name:"concept_cipher",  type:"string",  pattern:"SHA-256 hex", desc:"Deterministic address: SHA-256(SUBJECT_CONCEPT|{qid}|{lcsh_id})" },
      { name:"label",           type:"string",  desc:"Human-readable concept name" },
      { name:"wikidata_qid",    type:"string",  pattern:"Q[0-9]+", desc:"Wikidata QID for this concept (NOT the seed domain)" },
      { name:"lcsh_id",         type:"string",  pattern:"sh[0-9]+", desc:"LoC Subject Heading ID" },
      { name:"lcsh_id_status",  type:"enum",    values:["verified","lcsh_ceiling","not_found"], desc:"Verification status against LoC API" },
      { name:"seed_qid",        type:"string",  pattern:"Q[0-9]+", desc:"Domain seed QID (e.g. Q17167 for Roman Republic)" },
      { name:"source",          type:"string",  desc:"'domain_initiator' for DI-written concepts" },
    ],
    optional_props:[
      { name:"lcsh_heading",     type:"string",  desc:"LoC heading string" },
      { name:"lcsh_resolved",    type:"string",  desc:"Heading string as resolved by LoC API" },
      { name:"lcc_primary",      type:"string",  desc:"Primary Library of Congress Classification code" },
      { name:"lcc_codes",        type:"string[]",desc:"All applicable LCC codes" },
      { name:"scope_note",       type:"string",  desc:"What this concept covers and excludes" },
    ],
    current_count: 21,
    note:"21 for Q17167 (Roman Republic): 1 seed + 20 DI-written. All have verified QIDs and LCSH IDs (18 verified, 2 lcsh_ceiling).",
  },
  { name:"SYS_FacetRouter", status:"operational", color:C.router,
    desc:"LCSH heading pattern with facet assignment. Replaces all pattern-matching code. An agent classifies a heading by querying: MATCH (r:SYS_FacetRouter) WHERE heading CONTAINS r.pattern.",
    required_props:[
      { name:"pattern",          type:"string",  desc:"LCSH heading substring to match (e.g. 'Army', 'Coins', 'Religion')" },
      { name:"match_type",       type:"enum",    values:["contains","exact"], desc:"How to apply the pattern" },
      { name:"primary_facet",    type:"string",  desc:"Primary facet assignment" },
      { name:"secondary_facets", type:"string[]",desc:"Secondary facet assignments" },
    ],
    current_count: 38,
    note:"38 patterns covering 16 of 18 facets as primary. Demographic and one other are secondary-only.",
  },
  { name:"SYS_CurationDecision", status:"operational", color:C.curation,
    desc:"Human override decision mapping a concept to a specific LCSH heading. Wired to SubjectConcept via HAS_CURATION_DECISION. Replaces KNOWN_PATCHES dict in code.",
    required_props:[
      { name:"decision_key",     type:"string",  pattern:"di_lcsh|{seed_qid}|{concept_label}", desc:"Unique key" },
      { name:"concept_label",    type:"string",  desc:"Label of the SubjectConcept this decision applies to" },
      { name:"lcsh_id",          type:"string",  desc:"The confirmed LCSH ID" },
      { name:"lcsh_heading",     type:"string",  desc:"The confirmed LCSH heading string" },
      { name:"lcsh_id_status",   type:"enum",    values:["verified","lcsh_ceiling"], desc:"Verification status" },
      { name:"rationale",        type:"string",  desc:"Why this mapping was chosen" },
      { name:"decided_by",       type:"string",  desc:"'human' for manual curation" },
    ],
    current_count: 15,
    note:"15 decisions for Q17167: 13 verified + 2 lcsh_ceiling (Senate, Assemblies share sh85115178).",
  },
  { name:"Facet", status:"operational", color:C.facet,
    desc:"One of 18 canonical facets in the Chrystallum model. SubjectConcepts wire to Facets via HAS_PRIMARY_FACET and HAS_SECONDARY_FACET.",
    required_props:[
      { name:"label", type:"string", desc:"Facet name (Political, Military, Economic, etc.)" },
    ],
    current_count: 18,
    note:"18 canonical facets. Political(5 primary concepts), Social(4), Military(2), Intellectual(3), Economic(2), Religious(1), Artistic(1), Archaeological(1), Linguistic(1), Scientific(1). 7 secondary-only: Geographic, Diplomatic, Biographic, Cultural, Demographic, Environmental, Technological, Communication.",
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// RELATIONSHIP TYPES
// ══════════════════════════════════════════════════════════════════════════════
const REL_TYPES = [
  { name:"HAS_PRIMARY_FACET",      source:"SubjectConcept",     target:"Facet",              status:"operational",
    desc:"Primary facet assignment — one per concept", category:"subject", current_count: 21 },
  { name:"HAS_SECONDARY_FACET",    source:"SubjectConcept",     target:"Facet",              status:"operational",
    desc:"Secondary facet assignment — zero or more per concept", category:"subject", current_count: 91 },
  { name:"HAS_CURATION_DECISION",  source:"SubjectConcept",     target:"SYS_CurationDecision", status:"operational",
    desc:"Links concept to human override decision", category:"subject", current_count: 15 },
  { name:"HAS_PRIMARY_FACET",      source:"SYS_FacetRouter",    target:"Facet",              status:"operational",
    desc:"Router pattern primary facet assignment", category:"system", current_count: 38 },
  { name:"HAS_SECONDARY_FACET",    source:"SYS_FacetRouter",    target:"Facet",              status:"operational",
    desc:"Router pattern secondary facet assignments", category:"system", current_count: 68 },
  { name:"MEMBER_OF",              source:"SubjectConcept",     target:"SubjectConcept",     status:"operational",
    desc:"Concept belongs to seed domain (e.g. Roman Law MEMBER_OF Roman Republic)", category:"subject" },
];

// ══════════════════════════════════════════════════════════════════════════════
// FEDERATION SOURCES — subject backbone layer
// ══════════════════════════════════════════════════════════════════════════════
const DI_FED = [
  { id:"loc", name:"Library of Congress", color:C.loc, status:"operational",
    role:"subject_backbone",
    desc:"LCSH heading resolution. suggest2 API for search, SKOS endpoint for verification. Provides sh-IDs, broader/narrower terms, LCC codes.",
    endpoint:"https://id.loc.gov/authorities/subjects/",
    api_suggest:"https://id.loc.gov/authorities/subjects/suggest2?q={term}&searchType=keyword",
    api_skos:"https://id.loc.gov/authorities/subjects/{sh_id}.skos.json",
    provides:["LCSH heading IDs (sh-codes)", "Heading strings", "Broader/narrower term hierarchy", "LCC classification codes"],
    current_state:"All 21 Q17167 concepts have LoC-verified LCSH IDs. 18 verified, 2 lcsh_ceiling.",
  },
  { id:"wikidata_di", name:"Wikidata (DI layer)", color:C.wikidata, status:"operational",
    role:"concept_identity",
    desc:"Provides QIDs for subject concepts. Each SubjectConcept maps to a Wikidata entity. QID + LCSH ID = cipher key.",
    endpoint:"https://query.wikidata.org/sparql",
    api_search:"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={term}&language=en&format=json",
    provides:["Concept QIDs", "Labels and descriptions", "External identifier PIDs (Nomisma, PACTOLS, BnF, etc.)"],
    current_state:"All 21 Q17167 concepts have verified QIDs. Zero NEEDS_LOOKUP remaining.",
  },
  { id:"nomisma", name:"Nomisma", color:"#8B4513", status:"planned",
    role:"economic_sfa_anchor",
    desc:"Numismatic authority data. Provides controlled vocabulary for Roman Republican coinage. Federation anchor for Economic SFA numismatics.",
    endpoint:"http://nomisma.org/",
    provides:["Coin type URIs", "Mint identifiers", "Denomination vocabulary", "Hoard data"],
    current_state:"nomisma.org/id/roman_republic exists. Not yet harvested.",
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// POLICIES — mirrors SYS_Policy in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const DI_POLICIES = [
  { name:"DI_CipherFormula",
    rule:'SHA-256("SUBJECT_CONCEPT|{concept_qid}|{lcsh_sh_id}")',
    desc:"Deterministic cipher for SubjectConcept identity. Uses the CONCEPT's QID, never the seed QID." },
  { name:"DI_LCSHResolution",
    rule:"f(heading)->hits (LoC suggest2 API) | g(heading,hits)->id (LLM reasoning) | h(qid,id)->cipher (SHA-256)",
    desc:"Three-step LCSH resolution: I/O fetches candidates, LLM picks best match, math computes cipher." },
  { name:"DI_SubjectIdPattern",
    rule:"subj_{qid_lowercase}; fallback subj_{cipher[:12]} if QID unknown",
    desc:"MERGE key pattern for SubjectConcept nodes." },
  { name:"DI_LCSHCeiling",
    rule:"Use nearest parent heading. Set lcsh_id_status=lcsh_ceiling. Cipher unique via distinct concept QID.",
    desc:"Handling for concepts without dedicated LCSH headings." },
];

// ══════════════════════════════════════════════════════════════════════════════
// THRESHOLDS — mirrors SYS_Threshold in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const DI_THRESHOLDS = [
  { name:"di_max_concepts_per_domain", value:25, unit:"count",
    desc:"Maximum SubjectConcepts per domain seed before splits required",
    decision_table:"D12_DETERMINE_SubjectConcept_split_trigger" },
  { name:"di_lcsh_token_overlap_floor", value:0.3, unit:"score",
    desc:"Minimum Jaccard token overlap to accept LoC API match",
    decision_table:null },
];

// ══════════════════════════════════════════════════════════════════════════════
// NAMED QUERIES
// ══════════════════════════════════════════════════════════════════════════════
const DI_QUERIES = [
  { id:"DQ-01", label:"Cypher", name:"All SubjectConcepts for a domain",
    purpose:"Returns all concepts for a seed QID with facet assignments.",
    code:`MATCH (sc:SubjectConcept {seed_qid: $seed_qid})
OPTIONAL MATCH (sc)-[:HAS_PRIMARY_FACET]->(pf:Facet)
OPTIONAL MATCH (sc)-[:HAS_SECONDARY_FACET]->(sf:Facet)
RETURN sc.label, sc.subject_id, sc.lcsh_id, sc.lcsh_id_status,
       pf.label AS primary_facet,
       collect(DISTINCT sf.label) AS secondary_facets
ORDER BY sc.label` },

  { id:"DQ-02", label:"Cypher", name:"Classify heading via FacetRouter",
    purpose:"Given an LCSH heading, find the best facet assignment from graph data.",
    code:`MATCH (r:SYS_FacetRouter)
WHERE CASE r.match_type
  WHEN 'contains' THEN $heading CONTAINS r.pattern
  WHEN 'exact' THEN $heading = r.pattern
  ELSE false END
RETURN r.pattern, r.primary_facet, r.secondary_facets, r.match_type
ORDER BY size(r.pattern) DESC
LIMIT 1` },

  { id:"DQ-03", label:"Cypher", name:"Check existing curation decisions",
    purpose:"Before automated resolution, check if a human decision already exists.",
    code:`MATCH (cd:SYS_CurationDecision {seed_qid: $seed_qid})
RETURN cd.concept_label, cd.lcsh_id, cd.lcsh_heading,
       cd.lcsh_id_status, cd.rationale
ORDER BY cd.concept_label` },

  { id:"DQ-04", label:"Cypher", name:"Read DI policies from graph",
    purpose:"Agent discovers its own governance by querying SYS_Policy.",
    code:`MATCH (p:SYS_Policy)
WHERE p.scope = 'domain_initiator'
RETURN p.name, p.rule, p.description, p.active` },

  { id:"DQ-05", label:"Cypher", name:"Read DI thresholds from graph",
    purpose:"Agent discovers its operating limits from SYS_Threshold.",
    code:`MATCH (t:SYS_Threshold)
WHERE t.system = 'domain_initiator'
RETURN t.name, t.value, t.unit, t.description, t.decision_table` },

  { id:"DQ-06", label:"Cypher", name:"Facet coverage report",
    purpose:"How many primary concepts does each facet have? Identifies overloaded or empty facets.",
    code:`MATCH (f:Facet)
OPTIONAL MATCH (sc:SubjectConcept {seed_qid: $seed_qid})-[:HAS_PRIMARY_FACET]->(f)
OPTIONAL MATCH (sc2:SubjectConcept {seed_qid: $seed_qid})-[:HAS_SECONDARY_FACET]->(f)
RETURN f.label AS facet,
       count(DISTINCT sc) AS primary_count,
       count(DISTINCT sc2) AS secondary_count
ORDER BY primary_count DESC, f.label` },

  { id:"DQ-07", label:"Cypher", name:"Domain bootstrap readiness",
    purpose:"Pre-flight check: does this domain have all required governance nodes?",
    code:`RETURN {
  policies: size([(p:SYS_Policy) WHERE p.scope = 'domain_initiator' | p]),
  thresholds: size([(t:SYS_Threshold) WHERE t.system = 'domain_initiator' | t]),
  routers: size([(r:SYS_FacetRouter) | r]),
  facets: size([(f:Facet) | f]),
  concepts: size([(sc:SubjectConcept {seed_qid: $seed_qid}) | sc]),
  curations: size([(cd:SYS_CurationDecision {seed_qid: $seed_qid}) | cd])
} AS readiness` },
];

// ══════════════════════════════════════════════════════════════════════════════
// THE DI PIPELINE — code reduction proof
// ══════════════════════════════════════════════════════════════════════════════
const PIPELINE = {
  description: "The DI pipeline reduces to three functions: I/O, LLM reasoning, and math. Everything else is graph data.",
  before: { lines: 906, files: 3, what: "verify_and_patch_lcsh.py (289) + build_subject_schema.py (502) + resolve_lcsh_gaps.py (115)" },
  after:  { lines: 50,  files: 1, what: "di_bootstrap.py — I/O shell only" },
  steps: [
    { step:1, name:"Read policies from graph",     type:"I/O",       code:"MATCH (p:SYS_Policy {scope:'domain_initiator'}) RETURN p" },
    { step:2, name:"Read existing curations",       type:"I/O",       code:"MATCH (cd:SYS_CurationDecision {seed_qid:$qid}) RETURN cd" },
    { step:3, name:"LLM generates heading strings", type:"LLM",       code:"prompt(domain_context) -> [{label, heading_string, qid, scope_note}]" },
    { step:4, name:"LoC API resolves sh-IDs",       type:"I/O",       code:"suggest2(heading) -> hits[]; skos(sh_id) -> verified_label" },
    { step:5, name:"LLM picks best match",          type:"LLM",       code:"prompt(heading, hits) -> best_sh_id" },
    { step:6, name:"Compute cipher",                type:"math",      code:"SHA-256('SUBJECT_CONCEPT|{qid}|{sh_id}')" },
    { step:7, name:"Classify via FacetRouter",       type:"I/O",       code:"MATCH (r:SYS_FacetRouter) WHERE heading CONTAINS r.pattern RETURN r" },
    { step:8, name:"Write SubjectConcept + edges",  type:"I/O",       code:"MERGE (sc:SubjectConcept {subject_id:$sid}) SET ... MERGE (sc)-[:HAS_PRIMARY_FACET]->(f)" },
  ],
  what_moved_to_graph: [
    { was: "KNOWN_PATCHES dict (15 entries)",           now: "SYS_CurationDecision (15 nodes, queryable)" },
    { was: "token_overlap() + 3-strategy resolver",     now: "SYS_Policy {name:'DI_LCSHResolution'}" },
    { was: "Hardcoded cipher formula in make_cipher()", now: "SYS_Policy {name:'DI_CipherFormula'}" },
    { was: "Pattern-matching if/elif chains",           now: "SYS_FacetRouter (38 nodes, queryable)" },
    { was: "Hardcoded thresholds (0.3, 25)",            now: "SYS_Threshold (2 DI-specific nodes)" },
    { was: "Prompt template strings",                   now: "SYS_AgentPrompt (planned)" },
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// Q17167 DOMAIN STATE — current completion
// ══════════════════════════════════════════════════════════════════════════════
const Q17167_STATE = {
  seed_qid: "Q17167",
  seed_label: "Roman Republic",
  concepts: 21,
  facet_edges: 112,
  facet_router_patterns: 38,
  curation_decisions: 15,
  policies: 4,
  thresholds: 2,
  lcsh_verified: 19,
  lcsh_ceiling: 2,
  needs_lookup: 0,
  gaps_remaining: 3,
  gap_labels: ["Diplomacy and Foreign Relations", "Patron-Client Relations", "Pre-Roman Italy and Italic Peoples"],
};

// ══════════════════════════════════════════════════════════════════════════════
// AGENT BOOTSTRAP QUERY — how a new agent discovers the DI schema
// ══════════════════════════════════════════════════════════════════════════════
const AGENT_BOOTSTRAP = {
  description:"A newly instantiated DI agent runs these queries to discover its own governance, operating limits, and existing work from the graph itself.",
  queries:[
    { step:1, name:"Discover DI policies",
      query:`MATCH (p:SYS_Policy)
WHERE p.scope = 'domain_initiator' AND p.active = true
RETURN p.name, p.rule, p.description` },
    { step:2, name:"Discover DI thresholds",
      query:`MATCH (t:SYS_Threshold)
WHERE t.system = 'domain_initiator'
RETURN t.name, t.value, t.unit, t.description` },
    { step:3, name:"Load FacetRouter patterns",
      query:`MATCH (r:SYS_FacetRouter)-[:HAS_PRIMARY_FACET]->(f:Facet)
RETURN r.pattern, r.match_type, f.label AS primary_facet, r.secondary_facets
ORDER BY size(r.pattern) DESC` },
    { step:4, name:"Check existing concepts for this domain",
      query:`MATCH (sc:SubjectConcept {seed_qid: $seed_qid})
RETURN count(sc) AS concept_count,
  count(CASE WHEN sc.lcsh_id_status = 'verified' THEN 1 END) AS verified,
  count(CASE WHEN sc.lcsh_id_status = 'lcsh_ceiling' THEN 1 END) AS ceiling` },
    { step:5, name:"Load existing curation decisions",
      query:`MATCH (cd:SYS_CurationDecision {seed_qid: $seed_qid})
RETURN cd.concept_label, cd.lcsh_id, cd.lcsh_heading, cd.lcsh_id_status, cd.rationale` },
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// UI HELPERS (same pattern as geographic constitution)
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
        <div key={p.id} style={{borderLeft:`3px solid ${C.concept}`,padding:"8px 12px",
          marginBottom:8,background:C.panel,borderRadius:"0 4px 4px 0"}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <Mono col={C.concept}>{p.id}</Mono>
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
  const [sel,setSel]=useState("SubjectConcept");
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
              <span style={{fontSize:8,color:C.dim}}>{p.type}{p.pattern?` (${p.pattern})`:""}{p.values?` [${p.values.join(", ")}]`:""}</span>
              <span style={{fontSize:8,color:C.dim,marginLeft:"auto"}}>{p.desc}</span>
            </div>
          ))}
          {nt.optional_props?.length>0 && <>
            <SHead col={C.dim}>OPTIONAL PROPERTIES</SHead>
            {nt.optional_props.map(p=>(
              <div key={p.name} style={{display:"flex",gap:8,marginBottom:3,paddingLeft:8,
                borderLeft:`2px solid ${C.border}`}}>
                <Mono col={C.dim} s={8}>{p.name}</Mono>
                <span style={{fontSize:8,color:C.dim}}>{p.type}</span>
                <span style={{fontSize:8,color:C.dim,marginLeft:"auto"}}>{p.desc}</span>
              </div>
            ))}
          </>}
          {nt.note && <div style={{marginTop:8,fontSize:7.5,color:C.dim,fontStyle:"italic"}}>{nt.note}</div>}
        </div>
      )}
    </div>
  );
}

// ── RELATIONSHIPS TAB ────────────────────────────────────────────────────────
function RelsTab() {
  return (
    <div>
      {REL_TYPES.map((r,i)=>(
        <div key={`${r.name}-${r.source}-${i}`} style={{display:"flex",gap:8,marginBottom:5,
          borderLeft:`3px solid ${C.pass}`,
          padding:"6px 10px",background:C.panel,borderRadius:"0 4px 4px 0",
          alignItems:"center"}}>
          <Mono col={C.neo} s={9}>{r.name}</Mono>
          <Tag label={`:${r.source}`} color={C.concept} size={7}/>
          <span style={{color:C.dim,fontSize:8}}>-&gt;</span>
          <Tag label={`:${r.target}`} color={C.facet} size={7}/>
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
      {DI_FED.map(src=>(
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
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── POLICIES TAB ─────────────────────────────────────────────────────────────
function PoliciesTab() {
  return (
    <div>
      <SHead col={C.concept}>POLICIES (SYS_Policy WHERE scope='domain_initiator')</SHead>
      {DI_POLICIES.map(p=>(
        <div key={p.name} style={{borderLeft:`3px solid ${C.concept}`,padding:"8px 12px",
          marginBottom:6,background:C.panel,borderRadius:"0 4px 4px 0"}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <Mono col={C.concept}>{p.name}</Mono>
          </div>
          <div style={{fontFamily:"'Courier New',monospace",fontSize:8,color:C.neo,
            background:C.neo+"08",borderRadius:3,padding:"4px 8px",marginBottom:4}}>{p.rule}</div>
          <div style={{fontSize:8,color:C.dim}}>{p.desc}</div>
        </div>
      ))}
      <div style={{marginTop:16}}/>
      <SHead col={C.facet}>THRESHOLDS (SYS_Threshold WHERE system='domain_initiator')</SHead>
      {DI_THRESHOLDS.map(t=>(
        <div key={t.name} style={{display:"flex",gap:10,marginBottom:5,
          borderLeft:`3px solid ${C.facet}`,padding:"6px 10px",background:C.panel,
          borderRadius:"0 4px 4px 0",alignItems:"center"}}>
          <Mono col={C.facet}>{t.name}</Mono>
          <Tag label={`${t.value} ${t.unit}`} color={C.facet}/>
          <span style={{fontSize:8,color:C.dim,flex:1}}>{t.desc}</span>
          {t.decision_table && <Mono col={C.dim} s={7}>{t.decision_table}</Mono>}
        </div>
      ))}
    </div>
  );
}

// ── PIPELINE TAB ─────────────────────────────────────────────────────────────
function PipelineTab() {
  const typeCol = { "I/O":C.neo, "LLM":C.concept, "math":C.facet };
  return (
    <div>
      <div style={{display:"flex",gap:12,marginBottom:12}}>
        <div style={{background:C.fail+"15",border:`1px solid ${C.fail}30`,borderRadius:4,
          padding:"6px 10px",flex:1}}>
          <SHead col={C.fail}>BEFORE</SHead>
          <div style={{fontSize:10,color:C.fail,fontWeight:"bold"}}>{PIPELINE.before.lines} lines</div>
          <div style={{fontSize:7.5,color:C.dim}}>{PIPELINE.before.what}</div>
        </div>
        <div style={{background:C.pass+"15",border:`1px solid ${C.pass}30`,borderRadius:4,
          padding:"6px 10px",flex:1}}>
          <SHead col={C.pass}>AFTER</SHead>
          <div style={{fontSize:10,color:C.pass,fontWeight:"bold"}}>~{PIPELINE.after.lines} lines</div>
          <div style={{fontSize:7.5,color:C.dim}}>{PIPELINE.after.what}</div>
        </div>
      </div>

      <SHead col={C.neo}>PIPELINE STEPS</SHead>
      {PIPELINE.steps.map(s=>(
        <div key={s.step} style={{display:"flex",gap:8,marginBottom:4,
          borderLeft:`3px solid ${typeCol[s.type]||C.dim}`,padding:"5px 10px",
          background:C.panel,borderRadius:"0 4px 4px 0",alignItems:"center"}}>
          <div style={{background:typeCol[s.type],color:"white",borderRadius:"50%",
            width:18,height:18,display:"flex",alignItems:"center",justifyContent:"center",
            fontSize:8,fontWeight:"bold",flexShrink:0}}>{s.step}</div>
          <span style={{fontSize:9,color:C.bright,width:200}}>{s.name}</span>
          <Tag label={s.type} color={typeCol[s.type]} size={7}/>
          <Mono col={typeCol[s.type]} s={7}>{s.code}</Mono>
        </div>
      ))}

      <div style={{marginTop:14}}>
        <SHead col={C.curation}>WHAT MOVED FROM CODE TO GRAPH</SHead>
        {PIPELINE.what_moved_to_graph.map(m=>(
          <div key={m.was} style={{display:"grid",gridTemplateColumns:"1fr 20px 1fr",gap:4,
            marginBottom:4,fontSize:8,alignItems:"center"}}>
            <div style={{color:C.fail,background:C.fail+"10",borderRadius:3,padding:"3px 8px",textDecoration:"line-through"}}>{m.was}</div>
            <span style={{color:C.dim,textAlign:"center"}}>-&gt;</span>
            <div style={{color:C.pass,background:C.pass+"10",borderRadius:3,padding:"3px 8px"}}>{m.now}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── QUERIES TAB ──────────────────────────────────────────────────────────────
function QueriesTab() {
  const [sel,setSel]=useState("DQ-01");
  const q=DI_QUERIES.find(q=>q.id===sel);
  return (
    <div style={{display:"grid",gridTemplateColumns:"220px 1fr",gap:12}}>
      <div>
        {DI_QUERIES.map(q=>(
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
            <div style={{background:C.concept,color:"white",borderRadius:"50%",
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
    </div>
  );
}

// ── DOMAIN STATE TAB ─────────────────────────────────────────────────────────
function StateTab() {
  const s = Q17167_STATE;
  const stats = [
    ["SubjectConcepts", s.concepts, C.concept],
    ["Facet edges", s.facet_edges, C.facet],
    ["FacetRouter patterns", s.facet_router_patterns, C.router],
    ["CurationDecisions", s.curation_decisions, C.curation],
    ["DI Policies", s.policies, C.concept],
    ["DI Thresholds", s.thresholds, C.facet],
    ["LCSH verified", s.lcsh_verified, C.pass],
    ["LCSH ceiling", s.lcsh_ceiling, C.warn],
    ["NEEDS_LOOKUP", s.needs_lookup, s.needs_lookup===0?C.pass:C.fail],
    ["Gaps remaining", s.gaps_remaining, C.warn],
  ];
  return (
    <div>
      <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:12}}>
        <Mono col={C.concept} s={12}>{s.seed_qid}</Mono>
        <span style={{fontWeight:"bold",color:C.bright,fontSize:14}}>{s.seed_label}</span>
        <Tag label="complete" color={C.pass}/>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(5, 1fr)",gap:8,marginBottom:16}}>
        {stats.map(([label, val, col])=>(
          <div key={label} style={{background:col+"12",border:`1px solid ${col}30`,
            borderRadius:4,padding:"8px 10px",textAlign:"center"}}>
            <div style={{fontSize:16,fontWeight:"bold",color:col}}>{val}</div>
            <div style={{fontSize:7.5,color:C.dim}}>{label}</div>
          </div>
        ))}
      </div>
      {s.gaps_remaining > 0 && <>
        <SHead col={C.warn}>REMAINING GAPS (absorbed into existing concepts)</SHead>
        {s.gap_labels.map(g=>(
          <div key={g} style={{fontSize:8.5,color:C.warn,marginBottom:3,paddingLeft:8,
            borderLeft:`2px solid ${C.warn}`}}>{g}</div>
        ))}
      </>}
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
    ["policies",    `Policies & Thresholds`],
    ["pipeline",    "Pipeline"],
    ["queries",     `Queries (${DI_QUERIES.length})`],
    ["fed",         `Federation (${DI_FED.length})`],
    ["state",       "Q17167 State"],
    ["bootstrap",   "Agent Bootstrap"],
  ];
  return (
    <div style={{background:C.bg,minHeight:"100vh",padding:16,
      fontFamily:"'Courier New',monospace",color:C.bright}}>
      <div style={{borderBottom:`1px solid ${C.border}`,paddingBottom:12,marginBottom:14}}>
        <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:4}}>
          <span style={{fontSize:8,color:C.dim,letterSpacing:"0.15em"}}>CHRYSTALLUM - AGENT CONSTITUTION</span>
          {[["LoC",C.loc],["Wikidata",C.wikidata],["Neo4j",C.neo],["Nomisma","#8B4513"]].map(([l,c])=>(
            <span key={l} style={{background:c,color:"white",borderRadius:4,
              padding:"1px 8px",fontSize:8,fontWeight:"bold"}}>{l}</span>
          ))}
        </div>
        <div style={{fontSize:18,fontWeight:"bold",color:C.bright,marginBottom:2}}>
          Domain Initiator (DI) Constitution
        </div>
        <div style={{fontSize:9,color:C.dim,marginBottom:6}}>
          QID seed to SubjectConcept graph via LCSH resolution and facet wiring.
          Code = I/O shell. Reasoning = LLM. Data = graph. 906 lines to ~50.
        </div>
        <div style={{display:"flex",gap:8,flexWrap:"wrap",fontSize:8,color:C.dim}}>
          <span>{NODE_TYPES.length} node types</span>
          <span>-</span><span>{REL_TYPES.length} relationships</span>
          <span>-</span><span>{DI_POLICIES.length} policies</span>
          <span>-</span><span>{DI_THRESHOLDS.length} thresholds</span>
          <span>-</span><span>{DI_QUERIES.length} named queries</span>
          <span>-</span><span>{DI_FED.length} federation sources</span>
        </div>
        <div style={{marginTop:8,background:C.concept+"10",border:`1px solid ${C.concept}30`,
          borderRadius:4,padding:"5px 10px",fontSize:8,color:C.concept}}>
          AGENT INSTRUCTION: This is the Domain Initiator constitution.
          DI takes a QID, builds SubjectConcept schema with LCSH anchors, and writes to graph.
          All governance (policies, thresholds, curation decisions) is queryable from SYS_ nodes.
          Query SYS_Policy WHERE scope='domain_initiator' to bootstrap.
        </div>
      </div>
      <div style={{display:"flex",gap:0,borderBottom:`1px solid ${C.border}`,marginBottom:14,flexWrap:"wrap"}}>
        {VIEWS.map(([k,l])=>(
          <button key={k} onClick={()=>setView(k)}
            style={{border:"none",background:"transparent",padding:"6px 12px",fontSize:8.5,
              cursor:"pointer",color:view===k?C.concept:C.dim,fontWeight:view===k?"bold":"normal",
              borderBottom:view===k?`2px solid ${C.concept}`:"2px solid transparent"}}>
            {l}
          </button>
        ))}
      </div>
      {view==="principles" && <PrinciplesTab/>}
      {view==="nodes"      && <NodeTypesTab/>}
      {view==="rels"       && <RelsTab/>}
      {view==="policies"   && <PoliciesTab/>}
      {view==="pipeline"   && <PipelineTab/>}
      {view==="queries"    && <QueriesTab/>}
      {view==="fed"        && <FedTab/>}
      {view==="state"      && <StateTab/>}
      {view==="bootstrap"  && <BootstrapTab/>}
    </div>
  );
}
