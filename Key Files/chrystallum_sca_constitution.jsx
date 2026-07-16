import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — SUBJECT CONCEPT AGENT (SCA) CONSTITUTION                    ║
// ║  Role: Receive DI proposals → Validate CCS → Manage SC lifecycle           ║
// ║       → Dispatch to SFAs → Govern split/merge via D12                      ║
// ║  Current as of: 2026-03-09                                                 ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  sca:"#4361EE",       // blue — SCA identity
  di:"#B45309",        // orange — DI inputs
  sfa:"#1A7A6E",       // teal — SFA dispatch
  ccs:"#9B59B6",       // purple — CCS rules
  d12:"#C9A227",       // gold — D12 thresholds
  pass:"#2ECC71", warn:"#F5A623", fail:"#E74C3C",
};

// ══════════════════════════════════════════════════════════════════════════════
// SCA ROLE
// ══════════════════════════════════════════════════════════════════════════════
const ROLE = {
  name: "Subject Concept Agent (SCA)",
  summary: "Coordinator between DI and SFAs. Receives evidence-derived SC proposals from DI, validates them against CCS rules, manages the SC lifecycle in the graph, applies D12 thresholds for split/merge decisions, and dispatches per-facet work to SFAs.",
  does_not_do: [
    "Does not fetch corpus or run training (that is DI + SFA)",
    "Does not write raw claims or evidence nodes (that is SFA)",
    "Does not resolve QIDs or fetch from Wikidata/Pleiades (that is federation scripts)",
    "Does not hardcode facet assignments — all routing via SYS_RoutingRule",
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// PRE-FLIGHT — inspect graph state on spawn
// ══════════════════════════════════════════════════════════════════════════════
const PREFLIGHT = [
  { step:1, action:"Count and classify existing SubjectConcepts",
    query:`MATCH (sc:SubjectConcept)
OPTIONAL MATCH (sc)<-[m:MEMBER_OF]-()
RETURN sc.subject_id, sc.source, sc.label, count(m) AS members
ORDER BY sc.source, members DESC`,
    decide:[
      { condition:"source='ccs_bootstrap', members=0", action:"Priority targets — these 7 SCs need DI proposals or SFA wiring" },
      { condition:"source='ccs_bootstrap', members>0", action:"Scaffold populated — will be replaced by DI proposals if they pass CCS" },
      { condition:"source='di_proposal'", action:"DI proposals already written — check CCS validation status before accepting" },
    ],
  },
  { step:2, action:"Check for pending DI proposals",
    query:"ls output/di_propose/Q17167_proposals.json — check if propose.py has run",
    decide:[
      { condition:"File missing", action:"DI not complete — wait for batch_train.py + propose.py to finish" },
      { condition:"File exists, proposals.json has ccs_pass: false entries", action:"Review failures before --write" },
      { condition:"File exists, all proposals ccs_pass: true", action:"Ready to evaluate — proceed to CCS validation step" },
    ],
  },
  { step:3, action:"Check D12 thresholds from graph",
    query:`MATCH (t:SYS_Threshold)
WHERE t.decision_table = 'D12' OR t.threshold_id STARTS WITH 'D12'
RETURN t.name, t.value, t.unit`,
    decide:[
      { condition:"child_overload threshold present", action:"Use value as split trigger (current: 12)" },
      { condition:"crosslink threshold present", action:"Use value as merge trigger (current: 0.3)" },
      { condition:"Thresholds missing", action:"Run 18k_graph_rules_complete.cypher to restore D12 nodes" },
    ],
  },
  { step:4, action:"Check SFA training state",
    query:`MATCH (tr:SFA_TrainingRun)
RETURN tr.facet_key, tr.status, tr.insights_produced
ORDER BY tr.facet_key`,
    decide:[
      { condition:"0 runs", action:"SFAs not trained — SCA cannot dispatch until at least some facets have training data" },
      { condition:"Some facets trained", action:"Dispatch to trained SFAs; defer untrained facets" },
      { condition:"All 15 facets trained", action:"Full dispatch available — proceed to SFA coordination" },
    ],
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// CCS VALIDATION PROTOCOL — run on every DI proposal before accepting
// ══════════════════════════════════════════════════════════════════════════════
const CCS_VALIDATION = [
  { rule:"CCS-1", name:"Authority tether",
    check:"proposal.authority_ids is non-empty AND at least one of: lcc_primary, lcsh_id, fast_id, nomisma_id, pactols_id",
    pass_action:"Accept tether — wire ANCHORS edge to LCC_Class node",
    fail_action:"Request DI to supply at least one authority ID. Check: does the concept have a Wikidata QID with P244/P2163/P1149?",
  },
  { rule:"CCS-2", name:"Multidimensional",
    check:"proposal.facets.length >= 2 AND at least one has is_primary=true AND all have weight: float",
    pass_action:"Write HAS_FACET edges with weight + is_primary",
    fail_action:"If only 1 facet: ask DI to add secondary facets from training insights. If weights missing: set primary=0.9, secondary=0.5 as defaults.",
  },
  { rule:"CCS-3", name:"Populatable",
    check:"At least 1 SYS_RoutingRule {domain:'roman_republic'} has sc_id matching this proposal's subject_id OR proposal has a clear entity type that maps to existing routing rules",
    pass_action:"Accept — MEMBER_OF edges can be created by populate_member_of.py",
    fail_action:"Add a SYS_RoutingRule before accepting. Cannot create an SC that nothing routes to.",
  },
  { rule:"CCS-4", name:"Topic-grounded",
    check:"proposal.label does NOT contain: 'Figures', 'People', 'Persons', 'Characters', 'Individuals', 'Leaders'. Must be a scholarly topic, not an entity container.",
    pass_action:"Accept label as-is",
    fail_action:"Reject proposal. Return to DI with: 'reframe as scholarly topic, not entity type'. Example: 'Military Commanders' → reject; 'Roman Command Structure' → accept.",
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// D12 SPLIT/MERGE PROTOCOL
// ══════════════════════════════════════════════════════════════════════════════
const D12 = {
  child_overload: 12,    // SC with >12 members per child SC candidate → split
  crosslink_thresh: 0.3, // >30% of members shared between two SCs → merge candidates
  split_protocol: [
    "Query: MATCH (sc:SubjectConcept)<-[m:MEMBER_OF]-() WITH sc, count(m) AS n WHERE n > 12",
    "For each overloaded SC: examine SFA_TrainingInsight nodes for decomposition signals",
    "Propose child SCs, each covering a distinct sub-topic with clear scholarly grounding",
    "Apply CCS validation to each child before creating",
    "Redirect existing MEMBER_OF edges to appropriate child SC",
  ],
  merge_protocol: [
    "Query member overlap: MATCH (sc1)<-[:MEMBER_OF]-(e)-[:MEMBER_OF]->(sc2) WITH sc1, sc2, count(e) AS shared",
    "If shared/min(sc1.members, sc2.members) > 0.3: merge candidates",
    "Evaluate: are the two SCs actually the same scholarly topic?",
    "If yes: MERGE the SC nodes, redirect all edges, delete duplicate",
    "If no: shared membership is expected (multi-faceted entities) — do not merge",
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// SC LIFECYCLE STATES
// ══════════════════════════════════════════════════════════════════════════════
const LIFECYCLE = [
  { state:"scaffold",   col:"#F5A623", desc:"Hand-defined placeholder. No evidence basis. 15 ccs_bootstrap SCs are in this state. Zero-member scaffolds are priority targets." },
  { state:"proposed",   col:"#4361EE", desc:"DI or SFA has produced a proposal. Not yet CCS-validated. Exists in proposals.json or as SFA_TrainingInsight node." },
  { state:"validated",  col:"#9B59B6", desc:"Passes all 4 CCS rules. SCA has written SubjectConcept node to graph with HAS_FACET + ANCHORS edges. Not yet populated with MEMBER_OF edges." },
  { state:"active",     col:"#2ECC71", desc:"Has MEMBER_OF edges (members > 0). Routing rules exist. Temporal bounds on edges. Full CCS compliance." },
  { state:"split",      col:"#E74C3C", desc:"Was active but exceeded D12 child_overload. Parent SC demoted; children created and populated." },
];

// ══════════════════════════════════════════════════════════════════════════════
// SFA DISPATCH TABLE — which SFAs to activate per facet
// ══════════════════════════════════════════════════════════════════════════════
const SFA_DISPATCH = [
  { facet:"MILITARY",      sfa:"SFA_MILITARY",      zero_member_sc:"sc_military",       status:"trained" },
  { facet:"POLITICAL",     sfa:"SFA_POLITICAL",     zero_member_sc:null,                status:"corpus_ready" },
  { facet:"SOCIAL",        sfa:"SFA_SOCIAL",        zero_member_sc:"sc_society",        status:"corpus_ready" },
  { facet:"ECONOMIC",      sfa:"SFA_ECONOMIC",      zero_member_sc:"sc_economy",        status:"corpus_ready" },
  { facet:"RELIGIOUS",     sfa:"SFA_RELIGIOUS",     zero_member_sc:"sc_religion",       status:"corpus_ready" },
  { facet:"INTELLECTUAL",  sfa:"SFA_INTELLECTUAL",  zero_member_sc:"sc_historiography", status:"corpus_ready" },
  { facet:"GEOGRAPHIC",    sfa:"SFA_GEOGRAPHIC",    zero_member_sc:"sc_topography",     status:"corpus_ready" },
  { facet:"ARCHAEOLOGICAL",sfa:"SFA_ARCHAEOLOGICAL",zero_member_sc:"sc_material_culture",status:"corpus_ready"},
  { facet:"LINGUISTIC",    sfa:"SFA_LINGUISTIC",    zero_member_sc:"sc_literature",     status:"corpus_ready" },
  { facet:"SCIENTIFIC",    sfa:"SFA_SCIENTIFIC",    zero_member_sc:"sc_science",        status:"corpus_ready" },
  { facet:"BIOGRAPHIC",    sfa:"SFA_BIOGRAPHIC",    zero_member_sc:null,                status:"corpus_ready" },
  { facet:"CULTURAL",      sfa:"SFA_CULTURAL",      zero_member_sc:null,                status:"corpus_ready" },
  { facet:"DEMOGRAPHIC",   sfa:"SFA_DEMOGRAPHIC",   zero_member_sc:null,                status:"corpus_ready" },
  { facet:"ARTISTIC",      sfa:"SFA_ARTISTIC",      zero_member_sc:null,                status:"corpus_ready" },
  { facet:"COMMUNICATION", sfa:"SFA_COMMUNICATION", zero_member_sc:null,                status:"corpus_ready" },
];

// ══════════════════════════════════════════════════════════════════════════════
// NAMED QUERIES
// ══════════════════════════════════════════════════════════════════════════════
const SCA_QUERIES = [
  { id:"SQ-01", name:"Zero-member scaffold SCs",
    purpose:"Priority targets — these need DI proposals or direct SFA wiring.",
    cypher:`MATCH (sc:SubjectConcept {source: 'ccs_bootstrap'})
WHERE NOT (sc)<-[:MEMBER_OF]-()
RETURN sc.subject_id AS sc_id, sc.label AS label,
       sc.lcc_primary AS lcc ORDER BY sc.label` },
  { id:"SQ-02", name:"SC member counts + temporal coverage",
    purpose:"Health check — what % of MEMBER_OF edges carry temporal bounds?",
    cypher:`MATCH (sc:SubjectConcept)
OPTIONAL MATCH (sc)<-[m:MEMBER_OF]-()
WITH sc, count(m) AS members,
     sum(CASE WHEN m.earliest_year IS NOT NULL THEN 1 ELSE 0 END) AS timed
RETURN sc.subject_id, sc.label, members,
       CASE WHEN members>0 THEN round(100.0*timed/members) ELSE null END AS timed_pct
ORDER BY members DESC` },
  { id:"SQ-03", name:"Routing rules per SC",
    purpose:"CCS-3 check — does each SC have at least one routing rule?",
    cypher:`MATCH (sc:SubjectConcept)
OPTIONAL MATCH (r:SYS_RoutingRule {sc_id: sc.subject_id})
RETURN sc.subject_id AS sc_id, sc.label AS label,
       count(r) AS routing_rules
ORDER BY routing_rules ASC` },
  { id:"SQ-04", name:"D12 overload candidates",
    purpose:"Which SCs exceed child_overload=12? Split candidates.",
    cypher:`MATCH (sc:SubjectConcept)<-[m:MEMBER_OF]-()
WITH sc, count(m) AS members
WHERE members > 12
RETURN sc.subject_id, sc.label, members
ORDER BY members DESC` },
  { id:"SQ-05", name:"SFA training coverage",
    purpose:"Which facets have training data? Only dispatch to trained SFAs.",
    cypher:`MATCH (tr:SFA_TrainingRun)
RETURN tr.facet_key AS facet, count(tr) AS runs,
       sum(tr.insights_produced) AS total_insights
ORDER BY tr.facet_key` },
];

// ══════════════════════════════════════════════════════════════════════════════
// UI
// ══════════════════════════════════════════════════════════════════════════════

function RoleBanner() {
  return (
    <div style={{ background:C.panel, borderRadius:8, padding:16, marginBottom:14 }}>
      <div style={{ display:"flex", gap:12, alignItems:"flex-start", marginBottom:10 }}>
        <div style={{ background:C.sca, color:"#fff", borderRadius:6,
          padding:"4px 10px", fontSize:10, fontWeight:"bold", flexShrink:0 }}>SCA</div>
        <div>
          <div style={{ color:C.bright, fontWeight:"bold", fontSize:13, marginBottom:3 }}>{ROLE.name}</div>
          <div style={{ color:C.dim, fontSize:11, lineHeight:1.6 }}>{ROLE.summary}</div>
        </div>
      </div>
      <div style={{ borderTop:`1px solid ${C.border}`, paddingTop:8 }}>
        <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:4 }}>scope boundaries — SCA does NOT:</div>
        {ROLE.does_not_do.map((d,i) => (
          <div key={i} style={{ color:C.fail+"AA", fontSize:9.5, marginBottom:2 }}>✗ {d}</div>
        ))}
      </div>
    </div>
  );
}

function PreflightTab() {
  return (
    <div>
      <RoleBanner />
      {PREFLIGHT.map(p => (
        <div key={p.step} style={{ border:`1px solid ${C.border}`, borderRadius:6,
          marginBottom:10, overflow:"hidden" }}>
          <div style={{ background:C.panel, padding:"8px 12px", display:"flex", gap:10, alignItems:"center" }}>
            <div style={{ background:C.sca, color:"#fff", borderRadius:"50%",
              width:22, height:22, display:"flex", alignItems:"center", justifyContent:"center",
              fontWeight:"bold", fontSize:11, flexShrink:0 }}>{p.step}</div>
            <span style={{ color:C.bright, fontWeight:"bold", fontSize:12 }}>{p.action}</span>
          </div>
          <div style={{ padding:"6px 12px 4px", borderBottom:`1px solid ${C.border}` }}>
            <pre style={{ fontFamily:"monospace", fontSize:8.5, color:C.sca,
              background:C.sca+"08", margin:0, padding:"4px 6px", borderRadius:3,
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

function CCSTab() {
  return (
    <div>
      <div style={{ background:C.panel, borderRadius:6, padding:"10px 14px", marginBottom:12,
        fontSize:10, color:C.dim, lineHeight:1.6 }}>
        Run all 4 checks on every DI proposal before writing to graph.
        A single failure = reject. Return to DI with specific fix instruction.
      </div>
      {CCS_VALIDATION.map(r => (
        <div key={r.rule} style={{ border:`1px solid ${C.ccs}33`, borderRadius:6,
          marginBottom:10, overflow:"hidden" }}>
          <div style={{ background:C.ccs+"18", padding:"8px 12px",
            display:"flex", gap:10, alignItems:"center" }}>
            <span style={{ background:C.ccs, color:"#fff", borderRadius:4,
              padding:"1px 8px", fontSize:9, fontWeight:"bold", fontFamily:"monospace" }}>
              {r.rule}
            </span>
            <span style={{ color:C.ccs, fontWeight:"bold", fontSize:12 }}>{r.name}</span>
          </div>
          <div style={{ padding:"8px 12px" }}>
            <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:3 }}>check</div>
            <div style={{ fontFamily:"monospace", fontSize:9, color:C.bright+"CC",
              background:C.border, borderRadius:3, padding:"4px 8px", marginBottom:8 }}>
              {r.check}
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:8 }}>
              <div>
                <div style={{ color:C.pass, fontSize:9, fontWeight:"bold", marginBottom:2 }}>✓ pass</div>
                <div style={{ fontSize:9.5, color:C.dim }}>{r.pass_action}</div>
              </div>
              <div>
                <div style={{ color:C.fail, fontSize:9, fontWeight:"bold", marginBottom:2 }}>✗ fail</div>
                <div style={{ fontSize:9.5, color:C.dim }}>{r.fail_action}</div>
              </div>
            </div>
          </div>
        </div>
      ))}

      <div style={{ marginTop:16, border:`1px solid ${C.d12}44`, borderRadius:6, overflow:"hidden" }}>
        <div style={{ background:C.d12+"18", padding:"8px 12px" }}>
          <span style={{ color:C.d12, fontWeight:"bold", fontSize:12 }}>D12 Split/Merge Thresholds</span>
          <span style={{ color:C.dim, fontSize:9, marginLeft:8 }}>
            child_overload={D12.child_overload} | crosslink={D12.crosslink_thresh}
          </span>
        </div>
        <div style={{ padding:"8px 12px", display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
          <div>
            <div style={{ color:C.fail, fontSize:9, fontWeight:"bold", marginBottom:4 }}>Split protocol (members &gt; {D12.child_overload})</div>
            {D12.split_protocol.map((s,i) => (
              <div key={i} style={{ fontSize:8.5, color:C.dim, marginBottom:2 }}>
                {i+1}. {s}
              </div>
            ))}
          </div>
          <div>
            <div style={{ color:C.warn, fontSize:9, fontWeight:"bold", marginBottom:4 }}>Merge protocol (overlap &gt; {D12.crosslink_thresh})</div>
            {D12.merge_protocol.map((s,i) => (
              <div key={i} style={{ fontSize:8.5, color:C.dim, marginBottom:2 }}>
                {i+1}. {s}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function LifecycleTab() {
  return (
    <div>
      <div style={{ marginBottom:14 }}>
        <div style={{ color:C.dim, fontSize:10, fontWeight:"bold", marginBottom:8 }}>SC Lifecycle States</div>
        {LIFECYCLE.map(l => (
          <div key={l.state} style={{ display:"flex", gap:10, marginBottom:8, alignItems:"flex-start",
            border:`1px solid ${l.col}33`, borderRadius:4, padding:"8px 10px" }}>
            <span style={{ background:l.col, color:"#fff", borderRadius:4,
              padding:"2px 8px", fontSize:9, fontWeight:"bold", flexShrink:0 }}>
              {l.state}
            </span>
            <span style={{ color:C.dim, fontSize:10, lineHeight:1.5 }}>{l.desc}</span>
          </div>
        ))}
      </div>

      <div style={{ marginBottom:14 }}>
        <div style={{ color:C.dim, fontSize:10, fontWeight:"bold", marginBottom:8 }}>SFA Dispatch Table</div>
        <div style={{ border:`1px solid ${C.border}`, borderRadius:4, overflow:"hidden" }}>
          <div style={{ display:"grid", gridTemplateColumns:"110px 160px 1fr 90px",
            background:C.panel, padding:"4px 8px", fontSize:8, color:C.dim,
            fontWeight:"bold", gap:6 }}>
            <span>facet</span><span>SFA</span><span>zero-member SC target</span><span>status</span>
          </div>
          {SFA_DISPATCH.map((d,i) => (
            <div key={d.facet} style={{
              display:"grid", gridTemplateColumns:"110px 160px 1fr 90px",
              padding:"4px 8px", gap:6, fontSize:8.5,
              borderTop:`1px solid ${C.border}`,
              background: d.status === "trained" ? C.sfa+"08" : "transparent" }}>
              <span style={{ color:C.bright }}>{d.facet}</span>
              <span style={{ fontFamily:"monospace", fontSize:8, color:C.sfa }}>{d.sfa}</span>
              <span style={{ color: d.zero_member_sc ? C.fail : C.dim, fontSize:8 }}>
                {d.zero_member_sc || "—"}
              </span>
              <span style={{ color: d.status === "trained" ? C.pass : C.warn, fontSize:8 }}>
                {d.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <div style={{ color:C.dim, fontSize:10, fontWeight:"bold", marginBottom:8 }}>Named Queries</div>
        {SCA_QUERIES.map(q => (
          <div key={q.id} style={{ border:`1px solid ${C.border}`, borderRadius:4,
            marginBottom:8, overflow:"hidden" }}>
            <div style={{ background:C.panel, padding:"5px 10px",
              display:"flex", gap:8, alignItems:"center" }}>
              <span style={{ color:C.sca, fontFamily:"monospace", fontSize:9 }}>{q.id}</span>
              <span style={{ color:C.bright, fontSize:10, fontWeight:"bold" }}>{q.name}</span>
              <span style={{ color:C.dim, fontSize:9 }}>{q.purpose}</span>
            </div>
            <pre style={{ fontFamily:"monospace", fontSize:8.5, color:C.sca,
              background:C.sca+"08", margin:0, padding:"8px 10px",
              overflow:"auto", whiteSpace:"pre-wrap" }}>{q.cypher}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}

const TABS = ["preflight", "ccs", "lifecycle"];
const TAB_LABELS = { preflight:"Pre-Flight", ccs:"CCS + D12", lifecycle:"Lifecycle & Dispatch" };

export default function SCAConstitution() {
  const [tab, setTab] = useState("preflight");

  return (
    <div style={{ background:C.bg, minHeight:"100vh", color:C.bright,
      fontFamily:"system-ui, sans-serif" }}>
      <div style={{ background:C.panel, borderBottom:`1px solid ${C.border}`, padding:"12px 20px" }}>
        <div style={{ fontSize:16, fontWeight:"bold", color:C.sca, marginBottom:2 }}>
          Subject Concept Agent (SCA) Constitution
        </div>
        <div style={{ fontSize:12, color:C.dim }}>
          DI proposals → CCS validation → SC lifecycle → SFA dispatch — domain_roman_republic
        </div>
        <div style={{ display:"flex", gap:6, marginTop:10 }}>
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding:"5px 14px", border:"none", borderRadius:4,
              cursor:"pointer", fontSize:12,
              background: tab === t ? C.sca : "#222",
              color: tab === t ? "#fff" : C.dim,
              fontWeight: tab === t ? "bold" : "normal",
            }}>{TAB_LABELS[t]}</button>
          ))}
        </div>
      </div>
      <div style={{ padding:"16px 20px", maxWidth:1100 }}>
        {tab === "preflight" && <PreflightTab />}
        {tab === "ccs"       && <CCSTab />}
        {tab === "lifecycle" && <LifecycleTab />}
      </div>
    </div>
  );
}
