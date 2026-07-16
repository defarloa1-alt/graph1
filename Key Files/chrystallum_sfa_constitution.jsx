import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — SUBJECT-FACET AGENT (SFA) CONSTITUTION                      ║
// ║  Role: Per-facet specialist — interpret training insights, produce SC       ║
// ║        proposals, hand off cross-facet signals to sibling SFAs             ║
// ║  Current as of: 2026-03-09                                                 ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  sfa:"#1A7A6E",        // teal — SFA identity
  insight:"#B45309",    // orange — insight nodes
  within:"#2ECC71",     // green — within_facet_addition
  cross:"#9B59B6",      // purple — cross_facet_link
  refine:"#F5A623",     // amber — concept_refinement
  propose:"#4361EE",    // blue — proposals
  pass:"#2ECC71", warn:"#F5A623", fail:"#E74C3C",
};

// ══════════════════════════════════════════════════════════════════════════════
// SFA ROLE
// ══════════════════════════════════════════════════════════════════════════════
const ROLE = {
  name: "Subject-Facet Agent (SFA_{FACET})",
  summary: "One SFA per facet. Owns the scholarly interpretation of its facet within the domain. Reads SFA_TrainingInsight nodes produced by train.py, interprets them, produces SubjectConcept proposals for within-facet topics, and hands off cross-facet signals to sibling SFAs. Does not run corpus fetching — that is train.py (Layer 2).",
  scope_rule: "An SFA is responsible for ONE facet key (e.g. MILITARY). It proposes SCs with that facet as primary. It does NOT propose SCs where its facet is only secondary — those belong to the SC's primary facet's SFA.",
  does_not_do: [
    "Does not fetch OpenAlex corpus — that is train.py Layer 2",
    "Does not validate CCS rules — that is SCA",
    "Does not write MEMBER_OF edges — that is populate_member_of.py",
    "Does not propose SCs owned by another facet (cross_facet_link = signal only, not proposal)",
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// TRAINING INSIGHT TYPES — schema from train.py output
// ══════════════════════════════════════════════════════════════════════════════
const INSIGHT_TYPES = [
  {
    type:"within_facet_addition",
    col: C.within,
    meaning:"A concept that belongs squarely within this SFA's facet but was missing from the classify.py candidates. Evidence: corpus papers discuss it as a distinct scholarly sub-topic.",
    sfa_action:"Convert to SC proposal. Set this facet as primary. Assign secondary facets based on evidence. Submit to SCA for CCS validation.",
    example:{ label:"Roman legion", confidence:0.9, evidence:"Polybius commentary discusses legion organization extensively; candidates include Fimbrian legions showing specific legion types were significant" },
  },
  {
    type:"cross_facet_link",
    col: C.cross,
    meaning:"A concept that surfaces in this facet's corpus but is primarily another facet's topic. The SFA has identified it as relevant context but not its core responsibility.",
    sfa_action:"Do NOT create SC proposal. Write a handoff signal to the target SFA: {from_facet, to_facet, label, evidence, confidence}. Target SFA decides whether to create the SC.",
    example:{ label:"Pyrrhic War", confidence:0.8, target_facet:"Diplomatic", evidence:"Wars necessarily involve diplomatic aspects — alliances, treaties, negotiations with Greek states" },
  },
  {
    type:"concept_refinement",
    col: C.refine,
    meaning:"A clarification or scope correction on an existing concept in the candidates or existing SCs. Often identifies anachronistic inclusions, scope creep, or mislabeled entities.",
    sfa_action:"If targeting an existing SC: update sc.scope_note in graph. If targeting a candidate: add exclusion signal to classification. Do NOT create a new SC.",
    example:{ label:"Praetorian Guard", confidence:0.75, evidence:"Listed as Republican candidate but Praetorian Guard was primarily Imperial institution; Republican equivalents were different" },
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// PRE-FLIGHT — per-facet SFA on spawn
// ══════════════════════════════════════════════════════════════════════════════
const PREFLIGHT = [
  { step:1, action:"Read own training run",
    query:`MATCH (tr:SFA_TrainingRun {facet_key: $MY_FACET})
RETURN tr.run_id, tr.status, tr.works_consulted,
       tr.insights_produced, tr.should_decompose,
       tr.decomposition_reason, tr.training_summary
ORDER BY tr.run_id`,
    decide:[
      { condition:"0 runs", action:"No training data — SCA must trigger train.py for this facet first. Cannot proceed." },
      { condition:">1 run", action:"Multiple runs — read all insights but flag duplicates. Report to SCA for cleanup." },
      { condition:"1 run, status=completed", action:"Proceed to insight interpretation" },
      { condition:"should_decompose=true", action:"Strong signal: this facet warrants multiple SCs. Prioritise within_facet_addition insights." },
    ],
  },
  { step:2, action:"Read own training insights",
    query:`MATCH (tr:SFA_TrainingRun {facet_key: $MY_FACET})-[:PRODUCED]->(ti:SFA_TrainingInsight)
RETURN ti.insight_type AS type, ti.label AS label,
       ti.confidence AS conf, ti.evidence AS evidence,
       ti.target_facet AS target_facet, ti.status AS status
ORDER BY ti.confidence DESC`,
    decide:[
      { condition:"0 insights", action:"Training produced no insights — corpus was too weak. Flag to SCA: this facet needs better corpus keywords." },
      { condition:"All insights are cross_facet_link", action:"This SFA's facet may not be a primary domain topic. Report to SCA — may not need own SC." },
      { condition:"within_facet_addition insights present", action:"Core work: convert each to SC proposal following output contract." },
      { condition:"concept_refinement insights present", action:"Secondary work: update existing SC scope notes or classify.py exclusions." },
    ],
  },
  { step:3, action:"Check existing SCs for this facet",
    query:`MATCH (sc:SubjectConcept)-[:HAS_FACET {is_primary: true}]->(f:Facet {key: $MY_FACET})
OPTIONAL MATCH (sc)<-[m:MEMBER_OF]-()
RETURN sc.subject_id, sc.label, sc.source, count(m) AS members`,
    decide:[
      { condition:"0 SCs with this facet as primary", action:"Full gap — all within_facet_addition insights become new SC proposals." },
      { condition:"Existing scaffold SC (source='ccs_bootstrap')", action:"Replace scaffold with evidence-derived proposal. Use same subject_id to maintain routing rules." },
      { condition:"Existing active SC matches insight label", action:"Update sc.scope_note only — do not duplicate." },
    ],
  },
  { step:4, action:"Read routing rules for own facet",
    query:`MATCH (r:SYS_RoutingRule {domain: 'roman_republic'})
WHERE r.sc_id IN [
  sc.subject_id WHERE (sc)-[:HAS_FACET {is_primary:true}]->(:Facet {key: $MY_FACET})
]
RETURN r.match_mode, r.match_value, r.sc_id, r.rank`,
    decide:[
      { condition:"Routing rules exist for proposed SC", action:"CCS-3 satisfied — SCA can accept proposal without adding new rules." },
      { condition:"No routing rules for proposed SC", action:"Must propose a SYS_RoutingRule alongside the SC proposal for CCS-3 compliance." },
    ],
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// OUTPUT CONTRACT — what SFA writes back
// ══════════════════════════════════════════════════════════════════════════════
const OUTPUT_CONTRACT = {
  sc_proposal: {
    desc:"One JSON object per within_facet_addition insight that passes SFA's own quality check.",
    fields:[
      { name:"subject_id",     type:"string",   example:"sc_military_organization", rule:"snake_case, prefixed sc_, unique within domain" },
      { name:"label",          type:"string",   example:"Military Organization & Legion Structure", rule:"Named scholarly topic, not entity type" },
      { name:"primary_facet",  type:"string",   example:"MILITARY", rule:"Must be this SFA's own facet" },
      { name:"secondary_facets",type:"[{key,weight}]",example:"[{key:'POLITICAL',weight:0.4}]", rule:"From evidence in training corpus" },
      { name:"lcc_primary",    type:"string",   example:"DG105", rule:"Library of Congress code — required for CCS-1" },
      { name:"authority_ids",  type:"object",   example:"{lcsh:'sh85115176', lcc:'DG105'}", rule:"At least one required for CCS-1" },
      { name:"scope_note",     type:"string",   example:"Covers the organizational structure of Republican armies...", rule:"What this SC covers AND excludes" },
      { name:"source_insight", type:"string",   example:"train_Q17167_MILITARY_20260307T135452", rule:"Provenance — which training run produced this" },
      { name:"confidence",     type:"float",    example:"0.9", rule:"From insight.confidence — do not inflate" },
    ],
  },
  cross_facet_handoff: {
    desc:"Signal to SCA for routing to target SFA. SFA does not create the SC itself.",
    fields:[
      { name:"from_facet",   type:"string", example:"MILITARY" },
      { name:"to_facet",     type:"string", example:"DIPLOMATIC" },
      { name:"label",        type:"string", example:"Pyrrhic War" },
      { name:"evidence",     type:"string", example:"Wars involve diplomatic aspects — alliances with Greek states" },
      { name:"confidence",   type:"float",  example:"0.8" },
    ],
  },
  refinement: {
    desc:"Scope update for existing SC. No new node created.",
    fields:[
      { name:"target_sc",    type:"string", example:"sc_military" },
      { name:"update_type",  type:"enum",   example:"exclusion | scope_note | period_bound" },
      { name:"value",        type:"string", example:"Exclude Imperial institutions (Praetorian Guard = post-Republican)" },
      { name:"evidence",     type:"string", example:"Training insight: Praetorian Guard primarily Imperial..." },
    ],
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// NAMED QUERIES
// ══════════════════════════════════════════════════════════════════════════════
const SFA_QUERIES = [
  { id:"FQ-01", name:"All insights for my facet",
    cypher:`MATCH (tr:SFA_TrainingRun {facet_key: 'MILITARY'})-[:PRODUCED]->(ti:SFA_TrainingInsight)
RETURN ti.insight_type AS type, ti.label AS label,
       ti.confidence AS conf, ti.evidence AS evidence,
       ti.target_facet AS target_facet
ORDER BY ti.confidence DESC` },
  { id:"FQ-02", name:"CorpusWork titles for my facet",
    cypher:`MATCH (cw:CorpusWork {facet_key: 'MILITARY'})
RETURN cw.title AS title, cw.year AS year,
       cw.citation_count AS citations, cw.facet_relevance AS relevance
ORDER BY cw.citation_count DESC LIMIT 20` },
  { id:"FQ-03", name:"Existing SCs with my facet as primary",
    cypher:`MATCH (sc:SubjectConcept)-[:HAS_FACET {is_primary: true}]->(f:Facet {key: 'MILITARY'})
OPTIONAL MATCH (sc)<-[m:MEMBER_OF]-()
RETURN sc.subject_id, sc.label, sc.source,
       count(m) AS members ORDER BY members DESC` },
  { id:"FQ-04", name:"Cross-facet handoffs pending for my facet",
    cypher:`MATCH (ti:SFA_TrainingInsight {insight_type: 'cross_facet_link', target_facet: 'MILITARY'})
RETURN ti.label AS label, ti.facet_key AS from_facet,
       ti.confidence AS conf, ti.evidence AS evidence
ORDER BY ti.confidence DESC` },
];

// ══════════════════════════════════════════════════════════════════════════════
// UI
// ══════════════════════════════════════════════════════════════════════════════

function InsightTypesTab() {
  const [selected, setSelected] = useState("within_facet_addition");
  const type = INSIGHT_TYPES.find(t => t.type === selected);
  return (
    <div>
      <div style={{ background:C.panel, borderRadius:6, padding:"10px 14px", marginBottom:12,
        fontSize:10, color:C.dim, lineHeight:1.6 }}>
        <strong style={{ color:C.bright }}>train.py</strong> (Layer 3) produces three insight types.
        Each type requires a different SFA action. The type field is the decision key.
      </div>
      <div style={{ display:"flex", gap:6, marginBottom:12 }}>
        {INSIGHT_TYPES.map(t => (
          <button key={t.type} onClick={() => setSelected(t.type)} style={{
            border:`1px solid ${t.col}`, borderRadius:4, padding:"5px 12px",
            cursor:"pointer", fontSize:10, fontFamily:"monospace",
            background: selected === t.type ? t.col+"22" : "transparent",
            color: t.col, fontWeight: selected === t.type ? "bold" : "normal",
          }}>{t.type}</button>
        ))}
      </div>
      {type && (
        <div style={{ border:`1px solid ${type.col}44`, borderRadius:6, overflow:"hidden" }}>
          <div style={{ background:type.col+"18", padding:"10px 14px" }}>
            <span style={{ background:type.col, color:"#fff", borderRadius:4,
              padding:"2px 8px", fontSize:9, fontWeight:"bold", fontFamily:"monospace" }}>
              {type.type}
            </span>
          </div>
          <div style={{ padding:"12px 14px" }}>
            <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:3 }}>meaning</div>
            <div style={{ color:C.bright+"CC", fontSize:11, lineHeight:1.6, marginBottom:10 }}>
              {type.meaning}
            </div>
            <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:3 }}>SFA action</div>
            <div style={{ background:type.col+"11", border:`1px solid ${type.col}33`,
              borderRadius:4, padding:"8px 10px", fontSize:10, color:C.bright, marginBottom:10 }}>
              {type.sfa_action}
            </div>
            <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:3 }}>
              example insight (from MILITARY run)
            </div>
            <pre style={{ fontFamily:"monospace", fontSize:8.5, color:type.col,
              background:type.col+"08", borderRadius:3, padding:"8px 10px",
              margin:0, whiteSpace:"pre-wrap" }}>
              {JSON.stringify(type.example, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function PreflightTab() {
  return (
    <div>
      <div style={{ background:C.panel, borderRadius:6, padding:"10px 14px", marginBottom:12 }}>
        <div style={{ display:"flex", gap:10, alignItems:"flex-start", marginBottom:8 }}>
          <div style={{ background:C.sfa, color:"#fff", borderRadius:6,
            padding:"4px 10px", fontSize:10, fontWeight:"bold", flexShrink:0 }}>
            SFA_{"{FACET}"}
          </div>
          <div>
            <div style={{ color:C.bright, fontWeight:"bold", fontSize:12, marginBottom:2 }}>{ROLE.name}</div>
            <div style={{ color:C.dim, fontSize:10, lineHeight:1.5 }}>{ROLE.summary}</div>
          </div>
        </div>
        <div style={{ borderTop:`1px solid ${C.border}`, paddingTop:6 }}>
          <div style={{ color:C.warn, fontSize:9, fontWeight:"bold", marginBottom:3 }}>Scope rule</div>
          <div style={{ color:C.dim, fontSize:9.5 }}>{ROLE.scope_rule}</div>
        </div>
      </div>

      {PREFLIGHT.map(p => (
        <div key={p.step} style={{ border:`1px solid ${C.border}`, borderRadius:6,
          marginBottom:10, overflow:"hidden" }}>
          <div style={{ background:C.panel, padding:"8px 12px", display:"flex", gap:10, alignItems:"center" }}>
            <div style={{ background:C.sfa, color:"#fff", borderRadius:"50%",
              width:22, height:22, display:"flex", alignItems:"center", justifyContent:"center",
              fontWeight:"bold", fontSize:11, flexShrink:0 }}>{p.step}</div>
            <span style={{ color:C.bright, fontWeight:"bold", fontSize:12 }}>{p.action}</span>
          </div>
          <div style={{ padding:"6px 12px 4px", borderBottom:`1px solid ${C.border}` }}>
            <pre style={{ fontFamily:"monospace", fontSize:8.5, color:C.sfa,
              background:C.sfa+"08", margin:0, padding:"4px 6px", borderRadius:3,
              whiteSpace:"pre-wrap" }}>{p.query}</pre>
          </div>
          <div style={{ padding:"6px 12px 8px" }}>
            {p.decide.map((d,i) => (
              <div key={i} style={{ display:"flex", gap:8, marginBottom:5, alignItems:"flex-start" }}>
                <span style={{ color:C.warn, fontSize:9, flexShrink:0 }}>if</span>
                <span style={{ background:C.border, borderRadius:3, padding:"1px 6px",
                  fontSize:9, color:C.bright+"AA", fontFamily:"monospace" }}>{d.condition}</span>
                <span style={{ color:C.dim, fontSize:9 }}>→</span>
                <span style={{ color:C.pass, fontSize:9 }}>{d.action}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function OutputContractTab() {
  const [section, setSection] = useState("sc_proposal");
  const sections = [
    { key:"sc_proposal", label:"SC Proposal", col:C.propose },
    { key:"cross_facet_handoff", label:"Cross-Facet Handoff", col:C.cross },
    { key:"refinement", label:"Refinement", col:C.refine },
  ];
  const contract = OUTPUT_CONTRACT[section];

  return (
    <div>
      <div style={{ background:C.panel, borderRadius:6, padding:"10px 14px", marginBottom:12,
        fontSize:10, color:C.dim }}>
        Every within_facet_addition → SC Proposal.
        Every cross_facet_link → Cross-Facet Handoff (not a proposal).
        Every concept_refinement → Refinement (scope update only).
      </div>
      <div style={{ display:"flex", gap:6, marginBottom:12 }}>
        {sections.map(s => (
          <button key={s.key} onClick={() => setSection(s.key)} style={{
            border:`1px solid ${s.col}`, borderRadius:4, padding:"5px 12px",
            cursor:"pointer", fontSize:10, background: section === s.key ? s.col+"22" : "transparent",
            color: s.col, fontWeight: section === s.key ? "bold" : "normal",
          }}>{s.label}</button>
        ))}
      </div>
      <div style={{ color:C.dim, fontSize:10, marginBottom:8 }}>{contract.desc}</div>
      <div style={{ border:`1px solid ${C.border}`, borderRadius:4, overflow:"hidden" }}>
        <div style={{ display:"grid", gridTemplateColumns:"130px 120px 1fr 1fr",
          background:C.panel, padding:"4px 8px", fontSize:8, color:C.dim,
          fontWeight:"bold", gap:6 }}>
          <span>field</span><span>type</span><span>example</span><span>rule</span>
        </div>
        {contract.fields.map((f,i) => (
          <div key={f.name} style={{
            display:"grid", gridTemplateColumns:"130px 120px 1fr 1fr",
            padding:"4px 8px", gap:6, fontSize:8.5,
            borderTop:`1px solid ${C.border}`,
            background: i % 2 === 0 ? "transparent" : C.panel }}>
            <code style={{ fontFamily:"monospace", color:C.sfa, fontSize:8 }}>{f.name}</code>
            <span style={{ color:C.dim, fontSize:8 }}>{f.type}</span>
            <code style={{ fontFamily:"monospace", fontSize:7.5, color:C.bright+"88" }}>{f.example}</code>
            <span style={{ color:C.warn, fontSize:8 }}>{f.rule}</span>
          </div>
        ))}
      </div>

      <div style={{ marginTop:16 }}>
        <div style={{ color:C.dim, fontSize:10, fontWeight:"bold", marginBottom:8 }}>Named Queries</div>
        {SFA_QUERIES.map(q => (
          <div key={q.id} style={{ border:`1px solid ${C.border}`, borderRadius:4,
            marginBottom:8, overflow:"hidden" }}>
            <div style={{ background:C.panel, padding:"5px 10px",
              display:"flex", gap:8, alignItems:"center" }}>
              <span style={{ color:C.sfa, fontFamily:"monospace", fontSize:9 }}>{q.id}</span>
              <span style={{ color:C.bright, fontSize:10, fontWeight:"bold" }}>{q.name}</span>
            </div>
            <pre style={{ fontFamily:"monospace", fontSize:8.5, color:C.sfa,
              background:C.sfa+"08", margin:0, padding:"8px 10px",
              overflow:"auto", whiteSpace:"pre-wrap" }}>{q.cypher}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}

const TABS = ["preflight", "insights", "contract"];
const TAB_LABELS = { preflight:"Pre-Flight", insights:"Insight Types", contract:"Output Contract & Queries" };

export default function SFAConstitution() {
  const [tab, setTab] = useState("preflight");

  return (
    <div style={{ background:C.bg, minHeight:"100vh", color:C.bright,
      fontFamily:"system-ui, sans-serif" }}>
      <div style={{ background:C.panel, borderBottom:`1px solid ${C.border}`, padding:"12px 20px" }}>
        <div style={{ fontSize:16, fontWeight:"bold", color:C.sfa, marginBottom:2 }}>
          Subject-Facet Agent (SFA) Constitution
        </div>
        <div style={{ fontSize:12, color:C.dim }}>
          Per-facet specialist — training insights → SC proposals → cross-facet handoffs
        </div>
        <div style={{ display:"flex", gap:6, marginTop:10 }}>
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding:"5px 14px", border:"none", borderRadius:4,
              cursor:"pointer", fontSize:12,
              background: tab === t ? C.sfa : "#222",
              color: tab === t ? "#fff" : C.dim,
              fontWeight: tab === t ? "bold" : "normal",
            }}>{TAB_LABELS[t]}</button>
          ))}
        </div>
      </div>
      <div style={{ padding:"16px 20px", maxWidth:1100 }}>
        {tab === "preflight" && <PreflightTab />}
        {tab === "insights"  && <InsightTypesTab />}
        {tab === "contract"  && <OutputContractTab />}
      </div>
    </div>
  );
}
