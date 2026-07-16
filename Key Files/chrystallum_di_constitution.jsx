import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — DOMAIN INITIATOR (DI) CONSTITUTION                          ║
// ║  Pipeline: QID → Harvest → Classify → Route → Train → Propose             ║
// ║  Supersedes: LCSH-based v1 (2026-02-xx) — that pipeline is RETIRED        ║
// ║  Current as of: 2026-03-09 (post scripts 18a–18k)                         ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  harvest:"#B45309",    // orange — harvest step
  classify:"#5B2D8E",   // purple — classify step
  route:"#0E7490",      // cyan — route step
  train:"#1A7A6E",      // teal — train step
  propose:"#1E6B3C",    // green — propose step
  ccs:"#4361EE",        // blue — CCS validity
  warn:"#F5A623", pass:"#2ECC71", fail:"#E74C3C",
  lcc:"#B45309",
};

// ══════════════════════════════════════════════════════════════════════════════
// CURRENT STATE — Q17167 Roman Republic, as of 2026-03-09
// ══════════════════════════════════════════════════════════════════════════════
const STATE = {
  seed_qid: "Q17167",
  seed_label: "Roman Republic",
  total_facets: 15,
  corpus_ready: 15,       // all 15 corpus JSON files exist
  trained: 1,             // MILITARY only (2026-03-07)
  pending_training: 14,   // batch_train running fetch-only as of 2026-03-09
  proposals_produced: 5,  // from MILITARY
  scs_in_graph: 22,       // 15 ccs_bootstrap + 7 geo_bootstrap (scaffolds)
  status: "corpus complete — full training pending",
};

// ══════════════════════════════════════════════════════════════════════════════
// DESIGN PRINCIPLES
// ══════════════════════════════════════════════════════════════════════════════
const PRINCIPLES = [
  { id:"DI-01", name:"Layer 2 / 3 / 4 separation",
    col: C.train,
    desc:"Layer 2 = deterministic I/O (fetch, parse, file write). Layer 3 = Claude reasoning over corpus (never writes graph). Layer 4 = deterministic graph write (MERGE, idempotent). Code never mixes these." },
  { id:"DI-02", name:"One-run bootstrap per QID",
    col: C.harvest,
    desc:"DI runs once per domain QID. Its output is proposals — not final SCs. Human reviews proposals before graph write. Re-runs are safe (all file outputs are versioned, graph writes are MERGE)." },
  { id:"DI-03", name:"Rules-in-graph, not in code",
    col: C.classify,
    desc:"Facet assignments come from SYS_RoutingRule nodes (81 rules). Thresholds (D12: child_overload=12, crosslink=0.3) live in SYS_Threshold. Python reads these at runtime — no routing logic is hardcoded." },
  { id:"DI-04", name:"Corpus = OpenAlex + Wikidata, not LCSH",
    col: C.route,
    desc:"Training corpus is fetched from OpenAlex (gold OA academic papers by facet keywords) + Internet Archive + Wikidata P921. LCSH IDs are NOT used as routing keys. The v1 LCSH-based pipeline is retired." },
  { id:"DI-05", name:"Proposals must pass CCS validity before graph write",
    col: C.propose,
    desc:"Every proposed SC must satisfy all 4 CCS rules (ADR-020): authority tether, multidimensional, populatable, topic-grounded. propose.py validates these before --write is safe." },
  { id:"DI-06", name:"Scaffold SCs are placeholders, not targets",
    col: C.ccs,
    desc:"The 15 ccs_bootstrap SCs in the graph are scaffolds — hand-defined, not evidence-derived. DI proposals will replace them (or expand them). 7 have zero members and are explicitly awaiting DI output." },
];

// ══════════════════════════════════════════════════════════════════════════════
// PIPELINE STEPS
// ══════════════════════════════════════════════════════════════════════════════
const STEPS = [
  {
    n: 1, key:"harvest", name:"harvest.py", col: C.harvest,
    tagline:"Wikidata statements → JSON bundle",
    input:"--seed Q17167",
    output:"output/di_harvest/Q17167_di_harvest.json",
    sources:["Wikidata SPARQL (forward links)", "Wikidata API (backlinks via P31/P279/P361/P1344)", "Neo4j backbone (discipline traversal)"],
    what:"Fetches ALL Wikidata statements for the seed QID — forward links (entities the seed points to), backlinks (entities pointing to seed), external IDs (P244=LCSH, P2163=FAST, P1149=LCC, Nomisma, PACTOLS, Pleiades). Rule: never pass PID or QID without its label.",
    key_output_fields:["seed: {qid, label, external_ids}", "forward_links: [{qid, label, pids}]", "backlinks: [{qid, label, relation}]", "discipline_traversal: [{qid, label, authority_ids}]"],
    status:"done", status_note:"Q17167_di_harvest.json exists",
  },
  {
    n: 2, key:"classify", name:"classify.py", col: C.classify,
    tagline:"Harvest → 18-facet classification",
    input:"output/di_harvest/Q17167_di_harvest.json",
    output:"output/di_classify/Q17167_di_classify.json",
    sources:["Tier 1: instance_of/subclass_of QIDs → facet via TYPE_EXTENSIONS registry", "Tier 2: PIDs on candidates → facet via facet_registry_master.json", "Tier 3: external ID PIDs → federation source activation"],
    what:"Assigns each harvested entity to 1+ facets using a 3-tier routing system. No LCSH. No LLM. Pure deterministic matching: type QID → facet, property PID → facet, external ID PID → SFA activation signal.",
    key_output_fields:["per_facet: {military: [{qid, label, role, score, signals}], economic: [...], ...}", "facet_vector: {military: 0.82, political: 0.71, ...}", "federation_signals: {nomisma: true, pactols: false, ...}"],
    status:"done", status_note:"Q17167_di_classify.json exists",
  },
  {
    n: 3, key:"route", name:"route.py", col: C.route,
    tagline:"Classify → per-facet corpus packs",
    input:"output/di_classify/Q17167_di_classify.json + output/di_harvest/Q17167_di_harvest.json",
    output:"output/di_route/Q17167_{facet}_pack.json (15 files)",
    sources:["classify output (facet_delta)", "harvest output (discipline_traversal, domain_context)", "graph (SYS_RoutingRule, SubjectConcept backbone)"],
    what:"Assembles one pack per facet. Each pack contains: facet_delta (classified candidates), discipline_traversal (academic disciplines with authority IDs = OpenAlex query keys), corpus_endpoints (14 source APIs with live counts), domain_context (seed metadata, existing SCs for this facet).",
    key_output_fields:["facet_delta: [{qid, label, role, score}]", "discipline_traversal: [{label, openalex_id, lcsh_id, lcc}]", "corpus_endpoints: [{source, query, count}]", "domain_context: {seed_qid, existing_scs, routing_rules}"],
    status:"done", status_note:"15 pack files in output/di_route/",
  },
  {
    n: 4, key:"train", name:"train.py", col: C.train,
    tagline:"Corpus pack → Claude decomposition → SFA_TrainingRun",
    input:"output/di_route/Q17167_{facet}_pack.json",
    output:"output/di_training/Q17167_{FACET}_training.json + SFA_TrainingRun node in Neo4j",
    sources:["OpenAlex API (gold OA papers by facet keywords)", "Internet Archive (digitized primary sources)", "Wikidata P921 (main subject links)"],
    what:"Layer 2: fetches ~17 paper abstracts per facet from OpenAlex. Saves to _corpus.json. Layer 3: Claude multi-turn reasoning — given corpus + candidates + graph context, decomposes the facet into named scholarly sub-topics (SC proposals). Layer 4: writes SFA_TrainingRun + SFA_TrainingInsight nodes to Neo4j.",
    key_output_fields:["training_insights: [{label, evidence, confidence, facet_key}]", "training_summary: str", "should_decompose: bool", "decomposition_reason: str", "works_consulted: int"],
    status:"partial", status_note:"1/15 done (MILITARY). 14 corpus files ready. Full training run pending.",
    mode_note:"--fetch-only skips Claude, builds corpus only (free). Full run: ~17 Claude API calls per facet.",
  },
  {
    n: 5, key:"propose", name:"propose.py", col: C.propose,
    tagline:"All training outputs → validated SC proposals",
    input:"output/di_training/Q17167_*_training.json (all facets)",
    output:"output/di_propose/Q17167_proposals.json",
    sources:["All 15 _training.json files", "Claude (cross-facet synthesis)", "CCS validity rules (ADR-020)"],
    what:"Layer 2: deterministic aggregation of all training outputs — deduplicates, groups, computes cross-facet overlap. Layer 3: Claude synthesizes across facets, assigns authority tethers, infers facet vectors. Layer 4 (--write): MERGEs approved SubjectConcept nodes, HAS_FACET edges, ANCHORS to LCC — replacing scaffold SCs.",
    key_output_fields:["proposals: [{subject_id, label, lcc_primary, facets: [{key, weight, is_primary}], authority_ids, member_sources}]", "validation: {ccs_pass: bool, failures: []}"],
    status:"not_started", status_note:"Waiting for full training run to complete.",
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// FACET STATUS — Q17167, as of 2026-03-09
// ══════════════════════════════════════════════════════════════════════════════
const FACETS = [
  { key:"military",      label:"Military",       corpus:true,  trained:true,  proposals:5,
    proposal_labels:["Roman Wars", "Military Organization", "Civil Wars", "Battles & Sieges", "Command Structure"] },
  { key:"archaeological",label:"Archaeological", corpus:true,  trained:false, proposals:0 },
  { key:"artistic",      label:"Artistic",       corpus:true,  trained:false, proposals:0 },
  { key:"biographic",    label:"Biographic",     corpus:true,  trained:false, proposals:0 },
  { key:"communication", label:"Communication",  corpus:true,  trained:false, proposals:0 },
  { key:"cultural",      label:"Cultural",       corpus:true,  trained:false, proposals:0 },
  { key:"demographic",   label:"Demographic",    corpus:true,  trained:false, proposals:0 },
  { key:"economic",      label:"Economic",       corpus:true,  trained:false, proposals:0 },
  { key:"geographic",    label:"Geographic",     corpus:true,  trained:false, proposals:0 },
  { key:"intellectual",  label:"Intellectual",   corpus:true,  trained:false, proposals:0 },
  { key:"linguistic",    label:"Linguistic",     corpus:true,  trained:false, proposals:0 },
  { key:"political",     label:"Political",      corpus:true,  trained:false, proposals:0 },
  { key:"religious",     label:"Religious",      corpus:true,  trained:false, proposals:0 },
  { key:"scientific",    label:"Scientific",     corpus:true,  trained:false, proposals:0 },
  { key:"social",        label:"Social",         corpus:true,  trained:false, proposals:0 },
];

// ══════════════════════════════════════════════════════════════════════════════
// CCS VALIDITY RULES — proposals must pass all 4 (ADR-020)
// ══════════════════════════════════════════════════════════════════════════════
const CCS_RULES = [
  { id:"CCS-1", name:"Authority tether",
    desc:"≥1 external authority ID: LCSH (sh…), FAST (fst…), LCC code, or domain-specific (Nomisma, PACTOLS, EAGLE, Pleiades, BnF).",
    how_di_satisfies:"propose.py assigns LCC code from discipline_traversal; Claude maps to LCSH via training insights." },
  { id:"CCS-2", name:"Multidimensional",
    desc:"≥2 HAS_FACET edges with {weight: float, is_primary: bool}.",
    how_di_satisfies:"Every proposal inherits a facet vector from training. propose.py enforces ≥2 facets or rejects." },
  { id:"CCS-3", name:"Populatable",
    desc:"≥1 SYS_FederationSource can supply MEMBER_OF members. Checked against routing rules.",
    how_di_satisfies:"Route pack includes federation_signals. If no source can supply members, proposal is flagged." },
  { id:"CCS-4", name:"Topic-grounded",
    desc:"Named historical/scholarly topic, NOT an entity-type container. 'Roman Army' valid. 'Military Figures' invalid.",
    how_di_satisfies:"Claude's training prompt explicitly rejects entity-type containers. Validated in propose.py by label heuristics." },
];

// ══════════════════════════════════════════════════════════════════════════════
// NAMED QUERIES — DI can run these to inspect its own state
// ══════════════════════════════════════════════════════════════════════════════
const DI_QUERIES = [
  { id:"DQ-01", name:"Training run status",
    purpose:"Which facets have completed training runs in Neo4j?",
    cypher:`MATCH (tr:SFA_TrainingRun)
RETURN tr.facet_key AS facet, tr.status AS status,
       tr.works_consulted AS works, tr.insights_produced AS insights,
       tr.should_decompose AS decompose
ORDER BY tr.facet_key` },
  { id:"DQ-02", name:"Current scaffold SCs (pending replacement)",
    purpose:"Which SCs are scaffolds with zero members? These are DI's primary targets.",
    cypher:`MATCH (sc:SubjectConcept {source: 'ccs_bootstrap'})
OPTIONAL MATCH (sc)<-[m:MEMBER_OF]-()
WITH sc, count(m) AS members
RETURN sc.subject_id AS sc_id, sc.label AS label, members
ORDER BY members ASC` },
  { id:"DQ-03", name:"Routing rules for a facet",
    purpose:"What routing rules exist for the facet's source_type? Used to check CCS-3 (populatable).",
    cypher:`MATCH (r:SYS_RoutingRule {domain: 'roman_republic'})
RETURN r.source_type AS source, r.match_mode AS mode,
       r.sc_id AS sc_id, count(r) AS rules
ORDER BY r.source_type, r.match_mode` },
  { id:"DQ-04", name:"D12 thresholds",
    purpose:"Split/merge limits that govern when a proposed SC is too large or too small.",
    cypher:`MATCH (t:SYS_Threshold)
WHERE t.decision_table = 'D12' OR t.threshold_id STARTS WITH 'D12'
RETURN t.name AS name, t.value AS value, t.unit AS unit, t.description AS desc` },
  { id:"DQ-05", name:"Existing SC facet coverage",
    purpose:"Which facets are already primary on a ccs_bootstrap SC? Avoid proposing duplicates.",
    cypher:`MATCH (sc:SubjectConcept {source: 'ccs_bootstrap'})-[hf:HAS_FACET {is_primary: true}]->(f:Facet)
RETURN f.key AS facet, collect(sc.subject_id) AS existing_scs
ORDER BY f.key` },
];

// ══════════════════════════════════════════════════════════════════════════════
// PRE-FLIGHT PROTOCOL — DI agent decision tree on spawn
// ══════════════════════════════════════════════════════════════════════════════
const PREFLIGHT = [
  { step:1, action:"Inspect existing TrainingRuns",
    query:"MATCH (tr:SFA_TrainingRun) RETURN tr.facet_key, tr.run_id, tr.status, tr.insights_produced ORDER BY tr.facet_key",
    decide:[
      { condition:"0 runs found", action:"Clean state — proceed to Step 3" },
      { condition:"1 run per facet, facet_key set on CorpusWork", action:"Partial state — resume from last trained facet" },
      { condition:">1 run for same facet", action:"Duplicate runs — run 19a cleanup pattern, then start fresh" },
      { condition:"runs exist but CorpusWork.facet_key = null", action:"Bug from pre-fix train.py — run cleanup, re-fetch corpus, re-train" },
    ],
  },
  { step:2, action:"Inspect corpus files (file system)",
    query:"ls output/di_training/*_corpus.json — count files, check timestamps",
    decide:[
      { condition:"< 15 corpus files", action:"Fetch-only first: batch_train.py --fetch-only" },
      { condition:"15 corpus files, all recent (< 7 days)", action:"Corpus ready — proceed to full training" },
      { condition:"Corpus files exist but stale (> 7 days)", action:"Re-fetch: batch_train.py --fetch-only --force" },
    ],
  },
  { step:3, action:"Identify untrained facets",
    query:"Compare FACETS list against SFA_TrainingRun nodes — facets with no run are untrained",
    decide:[
      { condition:"0 untrained facets", action:"All trained — proceed to propose.py" },
      { condition:"N untrained facets", action:"Run: batch_train.py (no flags) — trains only untrained" },
      { condition:"Training timeout (exit code 1)", action:"Increase timeout in batch_train.py (line ~80: timeout=300 → 600). Do NOT re-run indefinitely." },
    ],
  },
  { step:4, action:"Run propose.py",
    query:"python scripts/agents/domain_initiator/propose.py --seed Q17167",
    decide:[
      { condition:"CCS validation failures in output", action:"Review failed proposals — fix authority tether or facet vector before --write" },
      { condition:"All proposals pass CCS-1 through CCS-4", action:"Run propose.py --write to commit to graph" },
      { condition:"Duplicate labels with existing ccs_bootstrap SCs", action:"Merge or replace — do not create duplicates" },
    ],
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// UI
// ══════════════════════════════════════════════════════════════════════════════

function StepBadge({ n, col, small }) {
  return (
    <div style={{ background:col, color:"#fff", borderRadius:"50%",
      width: small ? 18 : 26, height: small ? 18 : 26,
      display:"flex", alignItems:"center", justifyContent:"center",
      fontWeight:"bold", fontSize: small ? 9 : 12, flexShrink:0 }}>
      {n}
    </div>
  );
}

function StatusBadge({ status, note }) {
  const cfg = {
    done:       { col:C.pass,  label:"done" },
    partial:    { col:C.warn,  label:"partial" },
    not_started:{ col:C.fail,  label:"not started" },
  }[status] || { col:C.dim, label:status };
  return (
    <span title={note} style={{ background:cfg.col+"22", color:cfg.col,
      border:`1px solid ${cfg.col}44`, borderRadius:8,
      padding:"1px 7px", fontSize:9, fontWeight:"bold", cursor:note?"help":"default" }}>
      {cfg.label}{note ? " ⓘ" : ""}
    </span>
  );
}

function PipelineIBD() {
  const arrow = (col) => (
    <div style={{ display:"flex", flexDirection:"column", alignItems:"center",
      justifyContent:"center", padding:"0 4px", minWidth:32 }}>
      <div style={{ borderTop:`1px dashed ${col}`, width:"100%" }} />
      <div style={{ color:col, fontSize:10, marginTop:2 }}>▶</div>
    </div>
  );

  return (
    <div style={{ background:C.panel, borderRadius:8, padding:16, marginBottom:16 }}>
      <div style={{ color:C.dim, fontSize:11, marginBottom:12, fontStyle:"italic" }}>
        «pipeline» Domain Initiator — Q17167 Roman Republic
      </div>
      <div style={{ display:"flex", alignItems:"center", flexWrap:"wrap", gap:4, marginBottom:12 }}>
        {STEPS.map((s, i) => (
          <div key={s.key} style={{ display:"flex", alignItems:"center", gap:4 }}>
            <div style={{ border:`1px solid ${s.col}`, borderRadius:6, padding:"8px 12px",
              background:s.col+"11", minWidth:130 }}>
              <div style={{ display:"flex", gap:6, alignItems:"center", marginBottom:4 }}>
                <StepBadge n={s.n} col={s.col} />
                <span style={{ color:s.col, fontWeight:"bold", fontSize:11 }}>{s.name}</span>
              </div>
              <div style={{ color:C.dim, fontSize:9, marginBottom:4 }}>{s.tagline}</div>
              <StatusBadge status={s.status} note={s.status_note} />
            </div>
            {i < STEPS.length - 1 && arrow(s.col)}
          </div>
        ))}
      </div>

      {/* State summary */}
      <div style={{ display:"flex", gap:16, flexWrap:"wrap", marginTop:8 }}>
        {[
          [`${STATE.corpus_ready}/15`, "corpus ready", C.route],
          [`${STATE.trained}/15`, "trained", C.train],
          [`${STATE.proposals_produced}`, "proposals (MILITARY)", C.propose],
          [`${STATE.scs_in_graph}`, "SCs in graph (scaffolds)", C.warn],
        ].map(([v, l, col]) => (
          <div key={l} style={{ textAlign:"center" }}>
            <div style={{ fontSize:20, fontWeight:"bold", color:col }}>{v}</div>
            <div style={{ fontSize:9, color:C.dim }}>{l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StepsTab() {
  const [open, setOpen] = useState(null);
  return (
    <div>
      {STEPS.map(s => {
        const isOpen = open === s.key;
        return (
          <div key={s.key} style={{ border:`1px solid ${s.col}44`, borderRadius:6,
            marginBottom:8, overflow:"hidden" }}>
            <div onClick={() => setOpen(isOpen ? null : s.key)}
              style={{ background:s.col+"18", borderBottom:`1px solid ${s.col}33`,
                padding:"10px 14px", cursor:"pointer",
                display:"flex", justifyContent:"space-between", alignItems:"center" }}>
              <div style={{ display:"flex", gap:10, alignItems:"center" }}>
                <StepBadge n={s.n} col={s.col} />
                <span style={{ color:s.col, fontWeight:"bold", fontSize:13 }}>{s.name}</span>
                <span style={{ color:C.dim, fontSize:11 }}>{s.tagline}</span>
              </div>
              <div style={{ display:"flex", gap:6, alignItems:"center" }}>
                <StatusBadge status={s.status} note={s.status_note} />
                <span style={{ color:C.dim, fontSize:11 }}>{isOpen ? "▲" : "▼"}</span>
              </div>
            </div>
            {isOpen && (
              <div style={{ padding:"12px 14px" }}>
                <div style={{ color:C.bright, fontSize:12, lineHeight:1.6, marginBottom:10 }}>
                  {s.what}
                </div>
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10, marginBottom:10 }}>
                  <div>
                    <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:3 }}>input</div>
                    <code style={{ fontFamily:"monospace", fontSize:9, color:C.route }}>{s.input}</code>
                  </div>
                  <div>
                    <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:3 }}>output</div>
                    <code style={{ fontFamily:"monospace", fontSize:9, color:C.propose }}>{s.output}</code>
                  </div>
                </div>
                <div style={{ marginBottom:10 }}>
                  <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:3 }}>sources</div>
                  {s.sources.map((src, i) => (
                    <div key={i} style={{ fontSize:10, color:C.bright+"88", marginBottom:2 }}>
                      • {src}
                    </div>
                  ))}
                </div>
                <div>
                  <div style={{ color:C.dim, fontSize:9, fontStyle:"italic", marginBottom:3 }}>key output fields</div>
                  {s.key_output_fields.map((f, i) => (
                    <code key={i} style={{ display:"block", fontFamily:"monospace", fontSize:8.5,
                      color:s.col, background:s.col+"11", borderRadius:3,
                      padding:"2px 6px", marginBottom:2 }}>{f}</code>
                  ))}
                </div>
                {s.mode_note && (
                  <div style={{ marginTop:8, background:C.warn+"11", border:`1px solid ${C.warn}44`,
                    borderRadius:4, padding:"6px 10px", fontSize:9, color:C.warn }}>
                    ⚠ {s.mode_note}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function FacetStatusTab() {
  const trainedCount = FACETS.filter(f => f.trained).length;
  const corpusCount = FACETS.filter(f => f.corpus).length;

  return (
    <div>
      <div style={{ background:C.panel, borderRadius:6, padding:"10px 14px", marginBottom:12 }}>
        <div style={{ color:C.dim, fontSize:11, marginBottom:8 }}>
          Seed: <span style={{ color:C.bright }}>{STATE.seed_label}</span>
          {" "}(<span style={{ color:C.route, fontFamily:"monospace" }}>{STATE.seed_qid}</span>)
          {" — "}<span style={{ color:C.dim }}>{STATE.status}</span>
        </div>
        <div style={{ display:"flex", gap:16 }}>
          {[
            [corpusCount+"/"+STATE.total_facets, "corpus fetched", C.route],
            [trainedCount+"/"+STATE.total_facets, "trained", C.train],
            [STATE.proposals_produced, "proposals produced", C.propose],
          ].map(([v,l,col]) => (
            <div key={l} style={{ textAlign:"center" }}>
              <div style={{ fontSize:18, fontWeight:"bold", color:col }}>{v}</div>
              <div style={{ fontSize:9, color:C.dim }}>{l}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ border:`1px solid ${C.border}`, borderRadius:4, overflow:"hidden" }}>
        <div style={{ display:"grid", gridTemplateColumns:"140px 70px 70px 1fr",
          background:C.panel, padding:"4px 10px", fontSize:9, color:C.dim,
          fontWeight:"bold", gap:6 }}>
          <span>facet</span><span>corpus</span><span>trained</span><span>proposals</span>
        </div>
        {FACETS.map((f, i) => (
          <div key={f.key} style={{
            display:"grid", gridTemplateColumns:"140px 70px 70px 1fr",
            padding:"5px 10px", gap:6, fontSize:10,
            borderTop:`1px solid ${C.border}`,
            background: f.trained ? C.train+"08" : "transparent" }}>
            <span style={{ color:f.trained ? C.train : C.bright, fontWeight: f.trained ? "bold" : "normal" }}>
              {f.label}
            </span>
            <span style={{ color: f.corpus ? C.pass : C.fail }}>
              {f.corpus ? "✓ ready" : "—"}
            </span>
            <span style={{ color: f.trained ? C.train : C.dim }}>
              {f.trained ? "✓ done" : "pending"}
            </span>
            <div>
              {f.trained && f.proposals > 0 ? (
                <div style={{ display:"flex", flexWrap:"wrap", gap:3 }}>
                  {f.proposal_labels.map(p => (
                    <span key={p} style={{ background:C.propose+"22", color:C.propose,
                      border:`1px solid ${C.propose}44`, borderRadius:8,
                      padding:"1px 6px", fontSize:8.5 }}>{p}</span>
                  ))}
                </div>
              ) : f.trained ? (
                <span style={{ color:C.dim, fontSize:9 }}>no decomposition</span>
              ) : (
                <span style={{ color:C.dim, fontSize:9 }}>—</span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop:12, background:C.panel, borderRadius:6, padding:"10px 14px",
        fontSize:10, color:C.dim }}>
        <strong style={{ color:C.bright }}>Next step: </strong>
        Run <code style={{ color:C.train, fontFamily:"monospace" }}>
          python scripts/agents/domain_initiator/batch_train.py
        </code> (without --fetch-only) to train the 14 remaining facets (~238 Claude API calls).
        Then run <code style={{ color:C.propose, fontFamily:"monospace" }}>
          python scripts/agents/domain_initiator/propose.py --seed Q17167
        </code> to synthesize proposals.
      </div>
    </div>
  );
}

function PrinciplesTab() {
  return (
    <div>
      <div style={{ background:C.panel, borderRadius:6, padding:"10px 14px", marginBottom:12,
        fontSize:10, color:C.dim, lineHeight:1.6 }}>
        DI runs <strong style={{ color:C.bright }}>once per domain QID</strong>.
        Its output is <em>proposals</em> — not final SubjectConcepts. Human reviews.
        The 15 <code style={{ color:C.warn }}>ccs_bootstrap</code> SCs in the graph are scaffolds
        awaiting replacement by DI evidence-derived proposals.
      </div>

      {PRINCIPLES.map(p => (
        <div key={p.id} style={{ border:`1px solid ${p.col}44`, borderRadius:6,
          padding:"10px 14px", marginBottom:8 }}>
          <div style={{ display:"flex", gap:10, alignItems:"center", marginBottom:6 }}>
            <span style={{ background:p.col, color:"#fff", borderRadius:4,
              padding:"1px 7px", fontSize:9, fontWeight:"bold", fontFamily:"monospace" }}>
              {p.id}
            </span>
            <span style={{ color:p.col, fontWeight:"bold", fontSize:12 }}>{p.name}</span>
          </div>
          <div style={{ color:C.bright+"CC", fontSize:11, lineHeight:1.6 }}>{p.desc}</div>
        </div>
      ))}

      <div style={{ marginTop:16 }}>
        <div style={{ color:C.dim, fontSize:10, fontWeight:"bold", marginBottom:8 }}>
          CCS Validity — all 4 must pass before propose.py --write
        </div>
        {CCS_RULES.map(r => (
          <div key={r.id} style={{ display:"flex", gap:10, marginBottom:8, alignItems:"flex-start",
            border:`1px solid ${C.ccs}22`, borderRadius:4, padding:"8px 10px" }}>
            <span style={{ color:C.ccs, fontSize:10, width:50, flexShrink:0, fontFamily:"monospace" }}>{r.id}</span>
            <div style={{ flex:1 }}>
              <div style={{ color:C.bright, fontSize:11, fontWeight:"bold", marginBottom:3 }}>{r.name}</div>
              <div style={{ color:C.dim, fontSize:10, marginBottom:3 }}>{r.desc}</div>
              <div style={{ color:C.propose, fontSize:9.5, fontStyle:"italic" }}>
                → DI: {r.how_di_satisfies}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop:16 }}>
        <div style={{ color:C.dim, fontSize:10, fontWeight:"bold", marginBottom:8 }}>
          Named Queries — inspect DI state
        </div>
        {DI_QUERIES.map(q => (
          <div key={q.id} style={{ border:`1px solid ${C.border}`, borderRadius:4,
            marginBottom:8, overflow:"hidden" }}>
            <div style={{ background:C.panel, padding:"5px 10px", display:"flex", gap:8, alignItems:"center" }}>
              <span style={{ color:C.train, fontFamily:"monospace", fontSize:9 }}>{q.id}</span>
              <span style={{ color:C.bright, fontSize:10, fontWeight:"bold" }}>{q.name}</span>
              <span style={{ color:C.dim, fontSize:9 }}>{q.purpose}</span>
            </div>
            <pre style={{ fontFamily:"monospace", fontSize:8.5, color:C.route,
              background:C.route+"08", margin:0, padding:"8px 10px",
              overflow:"auto", whiteSpace:"pre-wrap" }}>{q.cypher}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// MAIN
// ══════════════════════════════════════════════════════════════════════════════
function PreflightTab() {
  return (
    <div>
      <div style={{ background:C.panel, borderRadius:6, padding:"10px 14px", marginBottom:12,
        fontSize:10, color:C.dim, lineHeight:1.6 }}>
        <strong style={{ color:C.bright }}>On spawn:</strong> Run these steps in order before
        executing any pipeline scripts. The graph may have partial or corrupted state from prior runs.
      </div>
      {PREFLIGHT.map(p => (
        <div key={p.step} style={{ border:`1px solid ${C.border}`, borderRadius:6,
          marginBottom:10, overflow:"hidden" }}>
          <div style={{ background:C.panel, padding:"8px 12px",
            display:"flex", gap:10, alignItems:"center" }}>
            <div style={{ background:C.train, color:"#fff", borderRadius:"50%",
              width:22, height:22, display:"flex", alignItems:"center", justifyContent:"center",
              fontWeight:"bold", fontSize:11, flexShrink:0 }}>{p.step}</div>
            <span style={{ color:C.bright, fontWeight:"bold", fontSize:12 }}>{p.action}</span>
          </div>
          <div style={{ padding:"6px 12px 4px", borderBottom:`1px solid ${C.border}` }}>
            <div style={{ color:C.dim, fontSize:8.5, fontStyle:"italic", marginBottom:3 }}>inspect</div>
            <code style={{ fontFamily:"monospace", fontSize:8.5, color:C.route }}>{p.query}</code>
          </div>
          <div style={{ padding:"6px 12px 8px" }}>
            <div style={{ color:C.dim, fontSize:8.5, fontStyle:"italic", marginBottom:4 }}>decide</div>
            {p.decide.map((d, i) => (
              <div key={i} style={{ display:"flex", gap:8, marginBottom:5, alignItems:"flex-start" }}>
                <span style={{ color:C.warn, fontSize:9, flexShrink:0, marginTop:1 }}>if</span>
                <span style={{ background:C.border, borderRadius:3, padding:"1px 6px",
                  fontSize:9, color:C.bright+"AA", fontFamily:"monospace", flexShrink:0 }}>
                  {d.condition}
                </span>
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

const TABS = ["preflight", "pipeline", "steps", "status", "principles"];
const TAB_LABELS = {
  preflight:"Pre-Flight",
  pipeline:"Pipeline Overview",
  steps:"Script Reference",
  status:"Facet Status",
  principles:"Principles & Queries",
};

export default function DIConstitution() {
  const [tab, setTab] = useState("pipeline");

  return (
    <div style={{ background:C.bg, minHeight:"100vh", color:C.bright,
      fontFamily:"system-ui, sans-serif" }}>
      {/* Header */}
      <div style={{ background:C.panel, borderBottom:`1px solid ${C.border}`, padding:"12px 20px" }}>
        <div style={{ fontSize:16, fontWeight:"bold", color:C.train, marginBottom:2 }}>
          Domain Initiator (DI) Constitution
        </div>
        <div style={{ fontSize:12, color:C.dim }}>
          QID → Harvest → Classify → Route → Train → Propose — domain_roman_republic — Q17167
        </div>
        <div style={{ display:"flex", gap:16, marginTop:8, flexWrap:"wrap" }}>
          {[
            ["Q17167", "seed", C.route],
            [STATE.total_facets, "facets", C.classify],
            [STATE.corpus_ready+"/"+STATE.total_facets, "corpus ready", C.route],
            [STATE.trained+"/"+STATE.total_facets, "trained", C.train],
            [STATE.proposals_produced, "proposals (MILITARY)", C.propose],
            [STATE.scs_in_graph, "SCs in graph", C.warn],
          ].map(([v,l,col]) => (
            <div key={l} style={{ textAlign:"center" }}>
              <div style={{ fontSize:18, fontWeight:"bold", color:col }}>{v}</div>
              <div style={{ fontSize:9, color:C.dim }}>{l}</div>
            </div>
          ))}
        </div>
        <div style={{ display:"flex", gap:6, marginTop:10 }}>
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding:"5px 14px", border:"none", borderRadius:4,
              cursor:"pointer", fontSize:12,
              background: tab === t ? C.train : "#222",
              color: tab === t ? "#000" : C.dim,
              fontWeight: tab === t ? "bold" : "normal",
            }}>{TAB_LABELS[t]}</button>
          ))}
        </div>
      </div>

      <div style={{ padding:"16px 20px", maxWidth:1100 }}>
        {tab === "preflight"  && <PreflightTab />}
        {tab === "pipeline"   && <><PipelineIBD /><StepsTab /></>}
        {tab === "steps"      && <StepsTab />}
        {tab === "status"     && <FacetStatusTab />}
        {tab === "principles" && <PrinciplesTab />}
      </div>
    </div>
  );
}
