import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — DISCIPLINE TAXONOMY CONSTITUTION                            ║
// ║  Integration: Wikidata (Q11862829 academic discipline) → authority IDs     ║
// ║  Two-tier: backbone (addressable) + expanded (navigable)                   ║
// ║  Self-describing: data constants below are mirrored as SYS_ nodes in Neo4j ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  wikidata:"#006699", lcsh:"#8E44AD", lcc:"#B5860D",
  neo:"#00C2A8", cypher:"#B5860D",
  backbone:"#1E6B3C", expanded:"#5A7A94",
  pass:"#2ECC71", warn:"#F5A623", fail:"#E74C3C",
};

const STATUS_COL = { operational:C.pass, planned:C.warn, bootstrap:C.warn, blocked:C.fail };

// ══════════════════════════════════════════════════════════════════════════════
// DISCIPLINE BACKBONE — two-tier model
// ══════════════════════════════════════════════════════════════════════════════
const DISCIPLINE_BACKBONE = {
  definition: "Wikidata items P31 = Q11862829 (academic discipline), expanded via P279/P527",
  seed_class: "Q11862829",
  seed_label: "academic discipline",
  expansion_properties: ["P279 (subclass of)", "P527 (has parts)"],
  expansion_levels: 2,
  harvest_script: "scripts/backbone/subject/build_discipline_taxonomy.py",
  harvest_output: "output/discipline_taxonomy.csv",

  total: 5866,
  seed_count: 4370,
  expanded_count: 1496,

  two_tier: {
    backbone: {
      count: 2026,
      pct: "34.5%",
      definition: "Has >= 1 bibliographic authority ID (LCSH, FAST, LCC, GND, DDC, AAT)",
      role: "Addressable — cipher key, corpus query, federation routing, HAS_LCSH/HAS_LCC edges",
      principle: "If the bibliographic control universe recognizes it, it can be addressed by cipher and queried against corpus endpoints",
    },
    expanded: {
      count: 3840,
      pct: "65.5%",
      definition: "Reached via P279/P527 expansion but no bibliographic authority ID",
      role: "Navigable — hierarchy context, SFA working vocabulary, reachable via SUBCLASS_OF/HAS_PART from backbone parent",
      principle: "Sub-disciplinary structure (methods, topics, approaches) that libraries don't catalog separately but SFAs need for granular routing",
    },
  },

  authority_coverage: [
    { id:"LCSH",  pid:"P244",  col:"lcsh_id",  count:1435, note:"Library of Congress Subject Headings — primary corpus query key" },
    { id:"GND",   pid:"P227",  col:"gnd_id",   count:1406, note:"German National Library — broad, includes abstract concepts" },
    { id:"FAST",  pid:"P2163", col:"fast_id",   count:469,  note:"OCLC Faceted Application — most selective, major subjects only" },
    { id:"LCC",   pid:"P1149", col:"lcc",       count:300,  note:"Library of Congress Classification — call number ranges" },
    { id:"DDC",   pid:"P1036", col:"ddc",       count:0,    note:"Dewey Decimal Classification" },
    { id:"AAT",   pid:"P1014", col:"aat_id",    count:0,    note:"Getty Art & Architecture Thesaurus" },
    { id:"BabelNet", pid:"P2581", col:"babelnet_id", count:0, note:"Multilingual lexical database" },
    { id:"KBpedia",  pid:"P8408", col:"kbpedia_id",  count:0, note:"Knowledge graph integrator" },
    { id:"World History", pid:"P9000", col:"world_history_id", count:0, note:"World History Encyclopedia" },
  ],
  no_english_label: 155,
};

// ══════════════════════════════════════════════════════════════════════════════
// DESIGN PRINCIPLES — agent reads these to understand discipline architecture
// ══════════════════════════════════════════════════════════════════════════════
const PRINCIPLES = [
  { id:"DP-01", name:"Backbone = addressable, expanded = navigable",
    desc:"Backbone disciplines (with authority IDs) are cipher-addressable: QID + PID + authority_value = deterministic jump key. Expanded disciplines are navigable only via SUBCLASS_OF/HAS_PART traversal from a backbone parent. Both are Discipline nodes in Neo4j, differentiated by backbone:true/false." },
  { id:"DP-02", name:"Authority IDs are corpus query keys",
    desc:"Each backbone discipline's LCSH/FAST/LCC/DDC is a direct query key into OpenAlex, Open Library, WorldCat, HathiTrust, LoC. The more backbone disciplines, the more granular the corpus surface. 1,435 LCSH IDs = 1,435 addressable corpus entry points." },
  { id:"DP-03", name:"P279 builds hierarchy, P527 builds vocabulary",
    desc:"P279 (subclass of) edges form the academic discipline tree. P527 (has parts) edges add sub-disciplinary topics (methods, approaches, specializations) that don't have their own LCSH but are valuable SFA working vocabulary." },
  { id:"DP-04", name:"Seed is Q11862829 only — no field-of-study filter",
    desc:"The harvest seeds from P31 = Q11862829 (academic discipline) only. The previous intersection with Q2267705 (field of study) was too narrow. Field of study items are caught by expansion if they're P279/P527 children of a discipline." },
  { id:"DP-05", name:"Facet classification is a separate reasoning step",
    desc:"The CSV contains no facet assignments. Facets are assigned by classify_discipline_facets.py (deterministic QID matching + Claude LLM) and stored as HAS_FACET relationships. The harvest is facet-agnostic." },
  { id:"DP-06", name:"Suspect flagging is the curation checkpoint",
    desc:"flag_discipline_suspects.py catches non-disciplines (persons, taxa, tech specs, occupational roles) that slip through P279/P527 expansion. The wider seed means more noise — the flag script is the filter, not the seed query." },
];

// ══════════════════════════════════════════════════════════════════════════════
// NODE TYPE SCHEMA — maps to SYS_NodeType in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const NODE_TYPES = [
  { name:"Discipline", status:"operational", color:C.wikidata,
    desc:"Academic discipline or sub-disciplinary topic from Wikidata. Two-tier: backbone (authority IDs) or expanded (hierarchy only).",
    required_props:[
      { name:"qid",       type:"string", pattern:"Q[0-9]+", desc:"Wikidata QID — primary key" },
      { name:"label",     type:"string", desc:"English label from Wikidata" },
    ],
    optional_props:[
      { name:"backbone",  type:"boolean", desc:"true if has >= 1 authority ID" },
      { name:"tier",      type:"string",  desc:"'seed' (P31 Q11862829) or 'expanded' (reached via P279/P527)" },
      { name:"lcsh_id",   type:"string",  desc:"LoC Subject Heading ID. 1,435 disciplines." },
      { name:"lcsh_label",type:"string",  desc:"Human-readable LCSH label (enriched from id.loc.gov)" },
      { name:"gnd_id",    type:"string",  desc:"GND ID. 1,406 disciplines." },
      { name:"fast_id",   type:"string",  desc:"FAST ID. 469 disciplines." },
      { name:"fast_label",type:"string",  desc:"Human-readable FAST label" },
      { name:"lcc",       type:"string",  desc:"LCC classification code. 300 disciplines." },
      { name:"lcc_label", type:"string",  desc:"Human-readable LCC label" },
      { name:"ddc",       type:"string",  desc:"Dewey Decimal code" },
      { name:"aat_id",    type:"string",  desc:"Getty AAT ID" },
      { name:"aat_label", type:"string",  desc:"Human-readable AAT label" },
      { name:"babelnet_id",     type:"string", desc:"BabelNet synset ID" },
      { name:"kbpedia_id",      type:"string", desc:"KBpedia concept ID" },
      { name:"world_history_id", type:"string", desc:"World History Encyclopedia ID" },
      { name:"primary_facet",    type:"string", desc:"Assigned by classify_discipline_facets.py (not from harvest)" },
    ],
    current_count: 5866,
  },
  { name:"LCSH_Heading", status:"operational", color:C.lcsh,
    desc:"Library of Congress Subject Heading node. Created from backbone disciplines with lcsh_id. Source: subjects_simplified.csv (LoC SKOS dump).",
    required_props:[
      { name:"sh_id",  type:"string", desc:"LCSH identifier (sh-prefix)" },
      { name:"label",  type:"string", desc:"Authorized heading text" },
    ],
    optional_props:[
      { name:"uri",    type:"string", desc:"id.loc.gov URI" },
      { name:"source", type:"string", desc:"Always 'loc_skos'" },
    ],
    current_count: 628,
  },
  { name:"LCC_Class", status:"operational", color:C.lcc,
    desc:"Library of Congress Classification node. Hierarchical call number system.",
    required_props:[
      { name:"code",  type:"string", desc:"LCC code (e.g. 'DG', 'U', 'QA')" },
      { name:"label", type:"string", desc:"Class description" },
    ],
    current_count: 4496,
  },
  { name:"ClassificationAnchor", status:"operational", color:C.lcsh,
    desc:"Bibliographic classification coordinate linking a discipline to its authority system position. Bridges discipline backbone to LoC/FAST/GND.",
    required_props:[
      { name:"qid",         type:"string", desc:"Wikidata QID of the discipline" },
      { name:"label",       type:"string", desc:"Discipline label" },
      { name:"anchor_type", type:"string", desc:"e.g. 'DisciplineSubject'" },
      { name:"federation",  type:"string", desc:"Providing federation source" },
    ],
    current_count: 595,
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// RELATIONSHIP TYPES — maps to SYS_RelationshipType in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const REL_TYPES = [
  // ── Hierarchy ──
  { name:"SUBCLASS_OF",    source:"Discipline", target:"Discipline", status:"operational",
    desc:"P279 hierarchy. Child discipline is a specialization of parent. Primary tree structure.",
    category:"hierarchy", temporal:false },
  { name:"PART_OF",        source:"Discipline", target:"Discipline", status:"operational",
    desc:"P361 relationship. Discipline is part of a larger discipline.",
    category:"hierarchy", temporal:false },
  { name:"HAS_PART",       source:"Discipline", target:"Discipline", status:"operational",
    desc:"P527 relationship. Discipline contains this sub-topic/method/specialization. Key source of expanded-tier items.",
    category:"hierarchy", temporal:false },

  // ── Facet classification ──
  { name:"HAS_FACET",      source:"Discipline", target:"Facet", status:"operational",
    desc:"Discipline classified into facet. Props: primary (bool), weight (0.3-1.0). Deterministic + LLM assigned.",
    category:"classification", temporal:false },

  // ── Authority linking ──
  { name:"HAS_LCSH",       source:"Discipline", target:"LCSH_Heading", status:"operational",
    desc:"Backbone discipline linked to its LCSH heading node. Backbone only.",
    category:"authority", temporal:false },
  { name:"HAS_LCC",        source:"Discipline", target:"LCC_Class", status:"operational",
    desc:"Backbone discipline linked to its LCC classification node. Backbone only.",
    category:"authority", temporal:false },

  // ── Federation routing ──
  { name:"FEDERATED_BY",   source:"Discipline", target:"SYS_FederationSource", status:"operational",
    desc:"Discipline has authority ID from this federation. Props: id_property (which ID column).",
    category:"federation", temporal:false },
  { name:"ROUTES_TO",      source:"Discipline", target:"SYS_FederationSource", status:"operational",
    desc:"Scope-based routing. Props: scope_basis ('seed match'|'pattern'|'descendant'). 4 universal + 13 domain federations.",
    category:"federation", temporal:false },
  { name:"ANCHORED_IN",    source:"Discipline", target:"SYS_FederationSource", status:"operational",
    desc:"Discipline anchored to federation via authority ID presence.",
    category:"federation", temporal:false },

  // ── Cross-backbone bridges ──
  { name:"FIELD_OF_WORK",  source:"Person", target:"Discipline", status:"operational",
    desc:"Person's field of work maps to discipline. Source: P101 + P106 matched against Discipline QIDs. 128 edges (78 persons -> 59 disciplines).",
    category:"bridge", temporal:false, current_count:128 },
];

// ══════════════════════════════════════════════════════════════════════════════
// PIPELINE — harvest → filter → load → enrich → classify → wire
// ══════════════════════════════════════════════════════════════════════════════
const PIPELINE = [
  { phase:"A", step:1, name:"Harvest",
    script:"scripts/backbone/subject/build_discipline_taxonomy.py",
    input:"Wikidata SPARQL (Q11862829)",
    output:"output/discipline_taxonomy.csv",
    desc:"Seed P31=Q11862829 (academic discipline only). Expand 2 levels via P279+P527. Fetch 9 authority IDs per item. 4,370 seeds → 5,866 after expansion." },
  { phase:"B", step:2, name:"Authority filter (independent)",
    script:"scripts/tools/fetch_disciplines_with_authority.py",
    input:"Wikidata SPARQL (Q11862829)",
    output:"Disciplines/disciplines_with_authority.csv",
    desc:"Independent SPARQL. Flat list filtered to items with LCSH|FAST|LCC|DDC. ~970 → ~2,026 with wider seed." },
  { phase:"B", step:3, name:"Backbone filter",
    script:"scripts/backbone/subject/filter_discipline_backbone.py",
    input:"output/discipline_taxonomy.csv (A1)",
    output:"output/discipline_taxonomy_backbone.csv",
    desc:"CSV filter: keep rows with any of fast_id, lcsh_id, ddc, lcc, gnd_id, aat_id. Tags backbone tier." },
  { phase:"B", step:4, name:"Suspect flagging",
    script:"scripts/backbone/subject/flag_discipline_suspects.py",
    input:"Consolidated CSV",
    output:"output/discipline_suspects_flagged.csv + _review.csv",
    desc:"Curation checkpoint. Flags non-disciplines: known bad QIDs, occupational -ist/-ologist, universities, tech specs, malformed labels." },
  { phase:"B", step:5, name:"Connected subset",
    script:"scripts/tools/extract_connected_disciplines.py",
    input:"Disciplines/disciplines_with_authority.csv (B2)",
    output:"Disciplines/disciplines_connected.csv",
    desc:"Extracts items whose P279 parent is also in the set. Treeable hierarchy subset." },
  { phase:"D", step:6, name:"Replace & load",
    script:"scripts/neo4j/replace_disciplines.py + scripts/backbone/subject/load_discipline_taxonomy.py",
    input:"Disciplines/disciplines_connected.csv + backbone CSV",
    output:"Neo4j (Discipline nodes + SUBCLASS_OF/PART_OF/HAS_PART + ANCHORED_IN)",
    desc:"Clean slate: DETACH DELETE old Discipline + SubjectConcept. MERGE new Discipline nodes with hierarchy rels. Both tiers loaded, differentiated by backbone:true/false." },
  { phase:"E", step:7, name:"Enrich authority labels",
    script:"scripts/backbone/subject/enrich_discipline_authority_labels.py",
    input:"Neo4j Discipline nodes",
    output:"Neo4j (lcsh_label, lcc_label, aat_label, fast_label)",
    desc:"Fetches human-readable labels from id.loc.gov, vocab.getty.edu, worldcat.org/fast." },
  { phase:"E", step:8, name:"Enrich external IDs",
    script:"scripts/neo4j/enrich_discipline_external_ids.py",
    input:"Disciplines/disciplines_external_ids.csv",
    output:"Neo4j (OpenAlex/VIAF/AAT IDs + FEDERATED_BY)",
    desc:"Adds OpenAlex, VIAF, Getty AAT identifiers. Creates FEDERATED_BY relationships." },
  { phase:"E", step:9, name:"Classify facets",
    script:"scripts/neo4j/classify_discipline_facets.py",
    input:"Neo4j Discipline + Facet nodes",
    output:"Neo4j (HAS_FACET) + Disciplines/discipline_facet_assignments.csv",
    desc:"Phase 1: deterministic QID matching + SUBCLASS_OF descendant propagation. Phase 2: Claude LLM classifies remainder. 18 facets." },
  { phase:"F", step:10, name:"Link to LCSH",
    script:"scripts/neo4j/link_disciplines_to_lcsh.py",
    input:"subjects/subjects_simplified.csv (LoC SKOS)",
    output:"Neo4j (LCSH_Heading nodes + HAS_LCSH edges)",
    desc:"MERGE LCSH_Heading nodes from LoC dump. Wire HAS_LCSH from backbone disciplines." },
  { phase:"F", step:11, name:"Link to LCC",
    script:"scripts/neo4j/link_disciplines_to_lcc.py",
    input:"Neo4j Discipline + LCC_Class nodes",
    output:"Neo4j (HAS_LCC edges)",
    desc:"Wire backbone disciplines to existing LCC_Class nodes." },
  { phase:"F", step:12, name:"Link to federations",
    script:"scripts/neo4j/link_disciplines_to_federations.py",
    input:"Neo4j Discipline + SYS_FederationSource",
    output:"Neo4j (FEDERATED_BY edges)",
    desc:"All disciplines → wikidata. Disciplines with lcsh_id|fast_id|lcc → lcsh_fast_lcc." },
  { phase:"F", step:13, name:"Wire federation scope",
    script:"scripts/neo4j/wire_discipline_federation_scope.py",
    input:"Neo4j Discipline + SYS_FederationSource",
    output:"Neo4j (ROUTES_TO edges)",
    desc:"4 universal federations (wikidata, lcsh_fast_lcc, open_alex, open_library) → all disciplines. 13 domain federations via seed labels + pattern matching + descendant propagation." },
  { phase:"F", step:14, name:"Export facets to CSV",
    script:"scripts/neo4j/export_discipline_facets_to_csv.py",
    input:"Neo4j HAS_FACET relationships",
    output:"output/discipline_taxonomy.csv (updated) + viewer/public/discipline_taxonomy.csv",
    desc:"Merges facet assignments back into CSV. Copies to viewer for live tree display." },
];

// ══════════════════════════════════════════════════════════════════════════════
// FEDERATION SOURCES — discipline-relevant
// ══════════════════════════════════════════════════════════════════════════════
const DISCIPLINE_FED = [
  { id:"wikidata", name:"Wikidata", color:C.wikidata, status:"operational",
    role:"identity_layer",
    routing:"universal — all 5,866 disciplines have QID",
    desc:"Source of all discipline QIDs, hierarchy (P279/P527), and authority ID properties." },
  { id:"lcsh_fast_lcc", name:"LCSH/FAST/LCC", color:C.lcsh, status:"operational",
    role:"authority_layer",
    routing:"backbone only — 1,435 LCSH + 469 FAST + 300 LCC",
    desc:"Library of Congress bibliographic system. Primary corpus query keys for OpenAlex, Open Library, WorldCat, HathiTrust." },
  { id:"open_alex", name:"OpenAlex", color:"#2E8B57", status:"operational",
    role:"corpus_source",
    routing:"universal — query by concept ID or LCSH",
    desc:"7,309 works for Q17167 domain. Free API (key since Feb 2026). Concepts, works, journals." },
  { id:"open_library", name:"Open Library", color:"#1A3A5C", status:"operational",
    role:"corpus_source",
    routing:"universal — query by subject slug",
    desc:"121 books for Q17167 domain. No auth. Books by subject." },
];

// ══════════════════════════════════════════════════════════════════════════════
// VERIFIED ENDPOINTS — agent-tested, structured data back
// ══════════════════════════════════════════════════════════════════════════════
const ENDPOINTS = [
  { name:"OpenAlex",          status:"KEY",  api:"api.openalex.org/concepts/{oa_id}",
    note:"Free API key since Feb 2026. 100k req/day." },
  { name:"Open Library",      status:"OPEN", api:"openlibrary.org/subjects/{slug}.json",
    note:"No auth. 1-3 req/sec." },
  { name:"LCSH Authority",    status:"OPEN", api:"id.loc.gov/authorities/subjects/{lcsh}.json",
    note:"No auth. SKOS linked data. Broader/narrower terms." },
  { name:"DOAJ",              status:"OPEN", api:"doaj.org/api/search/journals/{query}",
    note:"No auth. OA journals. 2 req/sec." },
  { name:"Zenodo",            status:"OPEN", api:"zenodo.org/api/records?q={query}",
    note:"No auth. Research records, datasets, preprints." },
  { name:"Europeana",         status:"KEY",  api:"api.europeana.eu/record/v2/search.json",
    note:"Free API key. 50M+ cultural heritage objects." },
  { name:"Internet Archive",  status:"OPEN", api:"archive.org/metadata/{identifier}",
    note:"Metadata only (no auth). Full-text varies by rights." },
  { name:"Perseus (CTS)",     status:"OPEN", api:"scaife-cts.perseus.org/api/cts",
    note:"XML only. Classical texts. GitHub TEI dumps more reliable." },
  { name:"HathiTrust",        status:"OPEN", api:"catalog.hathitrust.org/api/volumes/brief/oclc/{oclc}.json",
    note:"Bib lookup by OCLC/LCCN/ISBN. No keyword search." },
];

const REMOVED_ENDPOINTS = [
  { name:"Google Scholar",  reason:"No API. CAPTCHA." },
  { name:"JSTOR",           reason:"Institutional paywall." },
  { name:"Open Syllabus",   reason:"403 on API." },
  { name:"WorldCat Search", reason:"API shut down Jan 2025." },
];

// ══════════════════════════════════════════════════════════════════════════════
// RENDERING
// ══════════════════════════════════════════════════════════════════════════════
const S = { fontFamily:"'Segoe UI',system-ui,sans-serif" };

function Pill({ label, color, s=9, w=null }) {
  return <span style={{ background:color+"18", border:`1px solid ${color}`, borderRadius:10,
    padding:"2px 10px", fontSize:s, color, fontWeight:"bold", display:"inline-block",
    margin:"1px 2px", width:w }}>{label}</span>;
}
function Mono({ children, col=C.neo }) {
  return <code style={{ fontFamily:"monospace", color:col, fontSize:10, background:col+"12",
    padding:"1px 5px", borderRadius:3 }}>{children}</code>;
}
function Stat({ n, label, color, sub="" }) {
  return <div style={{ background:C.panel, border:`2px solid ${color}`, borderRadius:8,
    padding:"10px 14px", textAlign:"center", minWidth:100 }}>
    <div style={{ fontSize:22, fontWeight:"bold", color }}>{n}</div>
    <div style={{ fontSize:10, fontWeight:"bold", color:C.bright }}>{label}</div>
    {sub && <div style={{ fontSize:8, color:C.dim }}>{sub}</div>}
  </div>;
}
function SectionTitle({ children, color=C.bright }) {
  return <div style={{ fontSize:13, fontWeight:"bold", color, borderBottom:`2px solid ${color}30`,
    paddingBottom:4, marginBottom:10, marginTop:20, letterSpacing:0.5 }}>{children}</div>;
}

function PropRow({ name, type, desc, pattern }) {
  return <div style={{ display:"flex", gap:8, padding:"3px 0", borderBottom:`1px solid ${C.border}`,
    fontSize:10 }}>
    <Mono col={C.neo}>{name}</Mono>
    <span style={{ color:C.dim, minWidth:50 }}>{type}</span>
    {pattern && <Mono col={C.dim}>{pattern}</Mono>}
    <span style={{ color:C.bright }}>{desc}</span>
  </div>;
}

// ── TABS ──────────────────────────────────────────────────────────────────────
const TABS = ["Overview", "Schema", "Pipeline", "Endpoints"];

export default function DisciplineConstitution() {
  const [tab, setTab] = useState("Overview");

  return (
    <div style={{ ...S, background:C.bg, color:C.bright, minHeight:"100vh", padding:16 }}>
      {/* header */}
      <div style={{ borderBottom:`2px solid ${C.wikidata}`, paddingBottom:8, marginBottom:14 }}>
        <div style={{ display:"flex", alignItems:"baseline", gap:12 }}>
          <span style={{ fontSize:11, fontWeight:"bold", color:C.dim, letterSpacing:3 }}>CHRYSTALLUM</span>
          <span style={{ fontSize:16, fontWeight:"bold", color:C.bright }}>Discipline Taxonomy Constitution</span>
          <span style={{ fontSize:9, color:C.dim, marginLeft:"auto" }}>
            {DISCIPLINE_BACKBONE.total.toLocaleString()} disciplines · two-tier model · {DISCIPLINE_BACKBONE.two_tier.backbone.count.toLocaleString()} backbone
          </span>
        </div>
        <div style={{ fontSize:9, color:C.dim, marginTop:4, fontStyle:"italic" }}>
          Source: Wikidata Q11862829 (academic discipline) · P279/P527 expansion · 9 authority ID types · NO LLM-generated data
        </div>
      </div>

      {/* tabs */}
      <div style={{ display:"flex", gap:0, marginBottom:14, borderBottom:`2px solid ${C.border}` }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            border:"none", padding:"7px 16px", fontSize:10, cursor:"pointer", ...S,
            background:"transparent", fontWeight:tab === t ? "bold" : "normal",
            color:tab === t ? C.bright : C.dim,
            borderBottom:tab === t ? `3px solid ${C.wikidata}` : "3px solid transparent",
          }}>{t}</button>
        ))}
      </div>

      {/* ── OVERVIEW ─────────────────────────────────────────────────────── */}
      {tab === "Overview" && <>
        {/* stats bar */}
        <div style={{ display:"flex", gap:10, flexWrap:"wrap", marginBottom:16 }}>
          <Stat n={DISCIPLINE_BACKBONE.total.toLocaleString()} label="Total Disciplines" color={C.wikidata} sub="from Wikidata SPARQL" />
          <Stat n={DISCIPLINE_BACKBONE.seed_count.toLocaleString()} label="Seeds (P31)" color={C.wikidata} sub="Q11862829 direct" />
          <Stat n={DISCIPLINE_BACKBONE.expanded_count.toLocaleString()} label="Expanded" color={C.dim} sub="via P279 + P527" />
          <Stat n={DISCIPLINE_BACKBONE.two_tier.backbone.count.toLocaleString()} label="Backbone" color={C.backbone} sub="has authority IDs" />
          <Stat n={DISCIPLINE_BACKBONE.two_tier.expanded.count.toLocaleString()} label="Navigable" color={C.expanded} sub="hierarchy context" />
          <Stat n="18" label="Facets" color={C.lcsh} sub="classification target" />
          <Stat n="128" label="FIELD_OF_WORK" color={C.neo} sub="Person → Discipline" />
        </div>

        {/* two-tier model */}
        <SectionTitle color={C.backbone}>Two-Tier Model</SectionTitle>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12, marginBottom:16 }}>
          <div style={{ background:C.panel, border:`2px solid ${C.backbone}`, borderRadius:8, padding:14 }}>
            <div style={{ fontSize:12, fontWeight:"bold", color:C.backbone, marginBottom:6 }}>
              BACKBONE ({DISCIPLINE_BACKBONE.two_tier.backbone.count.toLocaleString()}) — Addressable
            </div>
            <div style={{ fontSize:9, color:C.bright, marginBottom:8 }}>{DISCIPLINE_BACKBONE.two_tier.backbone.definition}</div>
            <div style={{ fontSize:9, color:C.dim, lineHeight:1.6 }}>
              <div>Cipher addressable: QID + PID + authority_value</div>
              <div>Corpus query keys (LCSH → OpenAlex, Open Library, etc.)</div>
              <div>Federation routing (FEDERATED_BY, ROUTES_TO)</div>
              <div>HAS_LCSH / HAS_LCC edges to authority nodes</div>
              <div>Direct SFA entry point</div>
            </div>
          </div>
          <div style={{ background:C.panel, border:`2px solid ${C.expanded}`, borderRadius:8, padding:14 }}>
            <div style={{ fontSize:12, fontWeight:"bold", color:C.expanded, marginBottom:6 }}>
              EXPANDED ({DISCIPLINE_BACKBONE.two_tier.expanded.count.toLocaleString()}) — Navigable
            </div>
            <div style={{ fontSize:9, color:C.bright, marginBottom:8 }}>{DISCIPLINE_BACKBONE.two_tier.expanded.definition}</div>
            <div style={{ fontSize:9, color:C.dim, lineHeight:1.6 }}>
              <div>Reachable via SUBCLASS_OF / HAS_PART from backbone parent</div>
              <div>SFA working vocabulary (methods, topics, approaches)</div>
              <div>Hierarchy context for tree navigation</div>
              <div>Inherits parent's facet classification</div>
              <div>No direct corpus query — traversal only</div>
            </div>
          </div>
        </div>

        {/* authority coverage */}
        <SectionTitle color={C.lcsh}>Authority Coverage</SectionTitle>
        <div style={{ background:C.panel, borderRadius:8, padding:12 }}>
          {DISCIPLINE_BACKBONE.authority_coverage.filter(a => a.count > 0).map(a => (
            <div key={a.id} style={{ display:"flex", alignItems:"center", gap:8, padding:"4px 0",
              borderBottom:`1px solid ${C.border}` }}>
              <Pill label={a.id} color={C.lcsh} s={8} w={60} />
              <Mono col={C.dim}>{a.pid}</Mono>
              <div style={{ fontSize:14, fontWeight:"bold", color:C.backbone, minWidth:60, textAlign:"right" }}>
                {a.count.toLocaleString()}
              </div>
              <div style={{ fontSize:9, color:C.dim }}>{a.note}</div>
            </div>
          ))}
        </div>

        {/* principles */}
        <SectionTitle>Design Principles</SectionTitle>
        {PRINCIPLES.map(p => (
          <div key={p.id} style={{ background:C.panel, borderRadius:6, padding:10, marginBottom:6,
            borderLeft:`3px solid ${C.wikidata}` }}>
            <div style={{ fontSize:10, fontWeight:"bold", color:C.bright }}>
              <Mono col={C.wikidata}>{p.id}</Mono> {p.name}
            </div>
            <div style={{ fontSize:9, color:C.dim, marginTop:4 }}>{p.desc}</div>
          </div>
        ))}
      </>}

      {/* ── SCHEMA ───────────────────────────────────────────────────────── */}
      {tab === "Schema" && <>
        <SectionTitle>Node Types</SectionTitle>
        {NODE_TYPES.map(nt => (
          <div key={nt.name} style={{ background:C.panel, borderRadius:8, padding:12, marginBottom:10,
            borderLeft:`4px solid ${nt.color}` }}>
            <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
              <span style={{ fontSize:12, fontWeight:"bold", color:nt.color }}>:{nt.name}</span>
              <Pill label={nt.status} color={STATUS_COL[nt.status] || C.dim} s={8} />
              <span style={{ fontSize:10, color:C.dim, marginLeft:"auto" }}>{nt.current_count?.toLocaleString()} nodes</span>
            </div>
            <div style={{ fontSize:9, color:C.dim, marginBottom:8 }}>{nt.desc}</div>
            {nt.required_props && <>
              <div style={{ fontSize:8, color:C.backbone, fontWeight:"bold", marginBottom:2 }}>Required</div>
              {nt.required_props.map(p => <PropRow key={p.name} {...p} />)}
            </>}
            {nt.optional_props && <>
              <div style={{ fontSize:8, color:C.dim, fontWeight:"bold", marginTop:6, marginBottom:2 }}>Optional</div>
              {nt.optional_props.map(p => <PropRow key={p.name} {...p} />)}
            </>}
          </div>
        ))}

        <SectionTitle>Relationship Types</SectionTitle>
        {REL_TYPES.map(r => (
          <div key={r.name} style={{ display:"flex", alignItems:"center", gap:8, padding:"5px 0",
            borderBottom:`1px solid ${C.border}`, fontSize:10 }}>
            <Mono col={C.neo}>{r.name}</Mono>
            <span style={{ color:C.dim }}>{r.source} → {r.target}</span>
            <Pill label={r.category} color={C.dim} s={7} />
            {r.current_count && <span style={{ color:C.backbone, fontSize:9 }}>{r.current_count.toLocaleString()}</span>}
            <span style={{ color:C.bright, fontSize:9, marginLeft:"auto", maxWidth:400 }}>{r.desc}</span>
          </div>
        ))}
      </>}

      {/* ── PIPELINE ─────────────────────────────────────────────────────── */}
      {tab === "Pipeline" && <>
        <SectionTitle>Harvest → Filter → Load → Enrich → Classify → Wire</SectionTitle>
        {PIPELINE.map((p, i) => (
          <div key={i} style={{ background:C.panel, borderRadius:6, padding:10, marginBottom:6,
            borderLeft:`3px solid ${p.phase === "A" ? C.wikidata : p.phase === "B" ? C.lcsh
              : p.phase === "D" ? C.neo : p.phase === "E" ? C.backbone : C.dim}` }}>
            <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:4 }}>
              <Pill label={`${p.phase}${p.step}`} color={C.wikidata} s={9} />
              <span style={{ fontSize:11, fontWeight:"bold", color:C.bright }}>{p.name}</span>
            </div>
            <div style={{ fontSize:9, color:C.dim, marginBottom:4 }}>{p.desc}</div>
            <div style={{ fontSize:8, color:C.dim }}>
              <Mono col={C.dim}>{p.script}</Mono>
              {p.input && <span style={{ marginLeft:8 }}>← {p.input}</span>}
              {p.output && <span style={{ marginLeft:8 }}>→ {p.output}</span>}
            </div>
          </div>
        ))}
      </>}

      {/* ── ENDPOINTS ────────────────────────────────────────────────────── */}
      {tab === "Endpoints" && <>
        <SectionTitle color={C.backbone}>Verified Agent Endpoints ({ENDPOINTS.length} usable)</SectionTitle>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(3, 1fr)", gap:10, marginBottom:16 }}>
          {ENDPOINTS.map(ep => (
            <div key={ep.name} style={{ background:C.panel, borderRadius:6, padding:10,
              borderLeft:`3px solid ${ep.status === "OPEN" ? C.backbone : C.warn}` }}>
              <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:4 }}>
                <span style={{ fontSize:10, fontWeight:"bold", color:C.bright }}>{ep.name}</span>
                <Pill label={ep.status} color={ep.status === "OPEN" ? C.backbone : C.warn} s={7} />
              </div>
              <div style={{ fontSize:8, color:C.dim, marginBottom:2 }}>{ep.note}</div>
              <Mono col={C.dim}>{ep.api}</Mono>
            </div>
          ))}
        </div>

        <SectionTitle color={C.fail}>Removed (not agent-accessible)</SectionTitle>
        {REMOVED_ENDPOINTS.map(ep => (
          <div key={ep.name} style={{ fontSize:9, color:C.dim, padding:"3px 0" }}>
            <span style={{ textDecoration:"line-through" }}>{ep.name}</span> — {ep.reason}
          </div>
        ))}
      </>}
    </div>
  );
}
