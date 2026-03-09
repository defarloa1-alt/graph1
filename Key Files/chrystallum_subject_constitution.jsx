import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — SUBJECT / TEMPORAL / GEOGRAPHIC BACKBONE CONSTITUTION        ║
// ║  SysML v2 style: block definitions + interconnection diagram                ║
// ║  CCS = AI-powered rationalization of library shelving into facet space      ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  subject:"#D4A017",   // gold — subject backbone
  temporal:"#9B59B6",  // purple — temporal backbone
  geo:"#2E8B57",       // green — geographic backbone
  facet:"#4ECDC4",     // teal — facets
  lcc:"#E07C3E",       // orange — LCC anchors
  ccs:"#4361EE",       // blue — CCS layer
  rel:"#5A7A94",       // dimmed — relationships
  pass:"#2ECC71", warn:"#F5A623", fail:"#E74C3C",
};

// ══════════════════════════════════════════════════════════════════════════════
// BACKBONE STATISTICS — ground truth as of 2026-03-09
// ══════════════════════════════════════════════════════════════════════════════
const STATS = {
  subject: {
    domains: 1,
    ccs_bootstrap: 15,
    geo_bootstrap: 7,
    total_scs: 22,
    lcc_anchor_edges: 52,
    facet_edges: 62,
    total_member_of: 67969,  // persons + places across all SCs (incl. multi-SC)
    status: "scaffold — DI batch_train pending",
  },
  temporal: {
    period_nodes: 1,        // Q17167 Roman Republic (-509 to -27)
    persons_in_period: 3447,
    places_in_period: 32565,
    total_in_period: 36012,
    period_property: "start / end (integer, NOT start_year/end_year)",
    status: "operational",
  },
  geo: {
    total_places: 44193,
    in_period: 32565,
    geo_scs: 7,
    scoped_to_disciplines: 2,  // archaeology + topography
    status: "operational",
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// CCS ARCHITECTURE — 3 steps
// ══════════════════════════════════════════════════════════════════════════════
const CCS_STEPS = [
  {
    step: 1,
    name: "Authority Harvest",
    desc: "Start from Wikidata QID. Collect all external identifier PIDs (P244=LCSH, P2163=FAST, P1149=LCC, P1036=Dewey, P8814=Nomisma, P9842=PACTOLS, P1584=Pleiades, …). Each identifier = cipher key: QID+PID+value → SFA vertex address.",
    output: "Authority tether set on SubjectConcept node",
    example: "Q17167 → sh85115114 (LCSH) + fst01204885 (FAST) + DG241-269 (LCC) + roman_republic (Nomisma)",
  },
  {
    step: 2,
    name: "Cross-Class Aggregation",
    desc: "One concept is scattered across multiple LCC branches. AI recognises the scatter and collapses them into a single SubjectConcept with multiple ANCHORS edges. The LCC nodes remain unchanged; the SC is the aggregation point.",
    output: "SC -[:ANCHORS]-> multiple LCC_Class nodes",
    example: "Roman Law: DG87 (history) + KJA2-3660 (legal system) + KJA190-2152 (primary sources) + PA6000-6971 (literary context)",
  },
  {
    step: 3,
    name: "Facet Inference",
    desc: "Given all authority IDs, LCSH scope notes, LCC hierarchy, Wikipedia structure, and WorldCat catalog usage — an LLM infers a weighted facet vector across all 18 canonical facets. Weights are evidence-derived, not asserted by convention.",
    output: "SC -[:HAS_FACET {weight: float, is_primary: bool}]-> Facet nodes",
    example: "Roman Law: INTELLECTUAL(0.90) + POLITICAL(0.80) + SOCIAL(0.50) + BIOGRAPHIC(0.40)",
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// CCS VALIDITY RULES
// ══════════════════════════════════════════════════════════════════════════════
const CCS_RULES = [
  { id:"CCS-1", name:"Authority tether", desc:"≥1 external authority ID: QID, LCSH (sh…), FAST (fst…), LCC code, or domain-specific (Nomisma, PACTOLS, EAGLE, Pleiades, BnF)", pass:"All 22 SCs", fail:"0" },
  { id:"CCS-2", name:"Multidimensional", desc:"≥2 HAS_FACET edges with {weight: float, is_primary: bool}", pass:"All 22 SCs", fail:"0 (GEO_GENERAL fixed: +CULTURAL)" },
  { id:"CCS-3", name:"Populatable", desc:"≥1 SYS_FederationSource can supply MEMBER_OF members for this SC", pass:"15 thematic + 7 geo", fail:"0 (Pleiades covers geo; DPRR covers thematic)" },
  { id:"CCS-4", name:"Topic-grounded", desc:"Named historical/scholarly topic, NOT an entity type. 'Roman Army' valid. 'Military Figures' not.", pass:"All 22 SCs", fail:"7 bio_bootstrap deleted" },
];

// ══════════════════════════════════════════════════════════════════════════════
// BLOCK DEFINITIONS — SysML v2 style node schemas
// ══════════════════════════════════════════════════════════════════════════════
const BLOCKS = [
  {
    name: "SubjectDomain",
    color: C.subject,
    backbone: "Subject",
    count: "1 (domain_roman_republic)",
    desc: "Container/backbone for all SubjectConcepts in a domain. Anchors domain to a temporal Period, LCC ranges, and Disciplines.",
    attributes: [
      { name:"domain_id",       type:"String",  mult:"1",    example:"domain_roman_republic" },
      { name:"label",           type:"String",  mult:"1",    example:"Roman Republic" },
      { name:"temporal_scope",  type:"String",  mult:"1",    example:"-0509/-0027" },
      { name:"primary_lcc",     type:"String",  mult:"1",    example:"DG1-365, KJA2-3660, PA6000-6971" },
      { name:"status",          type:"String",  mult:"1",    example:"active" },
      { name:"governed_by",     type:"String",  mult:"1",    example:"ADR-020" },
    ],
    relations: [
      { rel:"OCCURS_DURING",      target:"Period",     mult:"1",    dir:"out" },
      { rel:"ALIGNED_WITH_LCC",   target:"LCC_Class",  mult:"1..*", dir:"out" },
      { rel:"HAS_SUBJECT_CONCEPT",target:"SubjectConcept", mult:"1..*", dir:"out" },
      { rel:"COVERS_DOMAIN",      target:"Discipline", mult:"1..*", dir:"in" },
    ],
  },
  {
    name: "SubjectConcept",
    color: C.subject,
    backbone: "Subject",
    count: "22 (15 ccs_bootstrap + 7 geo_bootstrap)",
    desc: "CCS-valid thematic anchor. Aggregates cross-class LCC scatter into one addressable node with a weighted 18-dimensional facet vector.",
    attributes: [
      { name:"subject_id",    type:"String",  mult:"1",    example:"sc_rr_constitution" },
      { name:"label",         type:"String",  mult:"1",    example:"Republican Constitution & Political Institutions" },
      { name:"lcc_primary",   type:"String",  mult:"1",    example:"DG89" },
      { name:"lcsh_id",       type:"String",  mult:"0..1", example:"sh85115171" },
      { name:"source",        type:"String",  mult:"1",    example:"ccs_bootstrap" },
      { name:"domain",        type:"String",  mult:"1",    example:"roman_republic" },
      { name:"cross_class",   type:"Boolean", mult:"0..1", example:"true (sc_rr_law, sc_rr_literature)" },
    ],
    relations: [
      { rel:"HAS_FACET {weight,is_primary}", target:"Facet",    mult:"2..*", dir:"out" },
      { rel:"ANCHORS",                       target:"LCC_Class", mult:"1..*", dir:"out" },
      { rel:"MEMBER_OF",                     target:"SubjectConcept", mult:"0..*", dir:"in", note:"from Person/Place" },
    ],
  },
  {
    name: "Period",
    color: C.temporal,
    backbone: "Temporal",
    count: "1 (Q17167 Roman Republic)",
    desc: "Temporal identity anchor. Persons and Places point INTO it via IN_PERIOD. Property names are start/end (integer), not start_year/end_year.",
    attributes: [
      { name:"qid",    type:"String",  mult:"1",    example:"Q17167" },
      { name:"label",  type:"String",  mult:"1",    example:"Roman Republic" },
      { name:"start",  type:"Integer", mult:"1",    example:"-509" },
      { name:"end",    type:"Integer", mult:"1",    example:"-27" },
    ],
    relations: [
      { rel:"IN_PERIOD",      target:"Person",  mult:"0..*", dir:"in", note:"3,447 persons" },
      { rel:"IN_PERIOD",      target:"Place",   mult:"0..*", dir:"in", note:"32,565 places" },
      { rel:"OCCURS_DURING",  target:"SubjectDomain", mult:"0..*", dir:"in" },
    ],
  },
  {
    name: "Place",
    color: C.geo,
    backbone: "Geographic",
    count: "44,193 (Pleiades)",
    desc: "Historical geographic identity anchor. Pleiades provides identity + temporal bounds. GeoNames provides modern containment hierarchy. 32,565 are in the Roman Republic period.",
    attributes: [
      { name:"pleiades_id",  type:"String",  mult:"0..1", example:"423025" },
      { name:"label",        type:"String",  mult:"1",    example:"Roma" },
      { name:"place_type",   type:"String",  mult:"0..1", example:"settlement" },
      { name:"min_date",     type:"Integer", mult:"0..1", example:"-753" },
      { name:"max_date",     type:"Integer", mult:"0..1", example:"640" },
    ],
    relations: [
      { rel:"IN_PERIOD",    target:"Period",     mult:"0..1", dir:"out", note:"32,565 wired" },
      { rel:"SCOPED_TO",    target:"Discipline", mult:"2",    dir:"out", note:"archaeology + topography" },
      { rel:"MEMBER_OF",    target:"SubjectConcept", mult:"0..*", dir:"out", note:"→ geo SCs" },
    ],
  },
  {
    name: "LCC_Class",
    color: C.lcc,
    backbone: "Classification",
    count: "~141 nodes in graph",
    desc: "Library of Congress Classification node. Authority anchor for SubjectConcepts. Multiple SCs can ANCHOR to the same LCC node; one SC can ANCHOR to multiple LCC nodes (cross-class).",
    attributes: [
      { name:"code",   type:"String", mult:"1", example:"DG89" },
      { name:"label",  type:"String", mult:"1", example:"Constitutional history — Rome" },
      { name:"class",  type:"String", mult:"1", example:"DG (History: Italy)" },
    ],
    relations: [
      { rel:"ANCHORS",          target:"SubjectConcept", mult:"0..*", dir:"in" },
      { rel:"ALIGNED_WITH_LCC", target:"SubjectDomain",  mult:"0..*", dir:"in" },
    ],
  },
  {
    name: "Facet",
    color: C.facet,
    backbone: "Classification",
    count: "18 nodes",
    desc: "One dimension of the 18-facet classification system. SubjectConcepts connect to Facets with weighted edges. Each SC has a primary facet (is_primary=true) and 1–3 secondaries.",
    attributes: [
      { name:"key",   type:"String", mult:"1", example:"POLITICAL" },
      { name:"label", type:"String", mult:"1", example:"Political" },
    ],
    relations: [
      { rel:"HAS_FACET {weight,is_primary}", target:"SubjectConcept", mult:"0..*", dir:"in" },
    ],
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// SUBJECT CONCEPT GALLERY — all 22 SCs
// ══════════════════════════════════════════════════════════════════════════════
const SC_GALLERY = [
  // ccs_bootstrap — thematic  (members = MEMBER_OF count as of 2026-03-09)
  { id:"sc_rr_constitution",    label:"Republican Constitution & Political Institutions", primary:"POLITICAL",    secondary:["ECONOMIC","SOCIAL"],             lcc:"DG89",       source:"ccs_bootstrap", members:4863 },
  { id:"sc_rr_military",        label:"Roman Army & Military Campaigns",                  primary:"MILITARY",     secondary:["GEOGRAPHIC","ECONOMIC","SOCIAL"], lcc:"DG105",      source:"ccs_bootstrap", members:1322 },
  { id:"sc_rr_religion",        label:"Roman Religion, Cults & Priesthoods",              primary:"RELIGIOUS",    secondary:["SOCIAL","POLITICAL"],            lcc:"DG171",      source:"ccs_bootstrap", members:248 },
  { id:"sc_rr_diplomacy",       label:"Roman Diplomacy & Foreign Relations",              primary:"DIPLOMATIC",   secondary:["MILITARY","GEOGRAPHIC","POLITICAL"],lcc:"DG21-190", source:"ccs_bootstrap", members:368 },
  { id:"sc_rr_economy",         label:"Roman Economy, Finance & Trade",                   primary:"ECONOMIC",     secondary:["SOCIAL","GEOGRAPHIC"],           lcc:"DG113",      source:"ccs_bootstrap", members:293 },
  { id:"sc_rr_late_republic",   label:"Late Republic (133–27 BC)",                        primary:"POLITICAL",    secondary:["MILITARY","SOCIAL"],             lcc:"DG261-269",  source:"ccs_bootstrap", members:1855 },
  { id:"sc_rr_middle_republic", label:"Middle Republic (264–133 BC)",                     primary:"MILITARY",     secondary:["POLITICAL","GEOGRAPHIC"],        lcc:"DG241-259",  source:"ccs_bootstrap", members:971 },
  { id:"sc_rr_early_republic",  label:"Early Republic (509–264 BC)",                      primary:"POLITICAL",    secondary:["MILITARY","SOCIAL"],             lcc:"DG221-239",  source:"ccs_bootstrap", members:683 },
  { id:"sc_rr_law",             label:"Roman Law & Legal Institutions",                   primary:"INTELLECTUAL", secondary:["POLITICAL","SOCIAL","BIOGRAPHIC"],lcc:"KJA2-3660",  source:"ccs_bootstrap", members:0,   cross:true },
  { id:"sc_rr_topography",      label:"Roman Topography & Urban Space",                   primary:"GEOGRAPHIC",   secondary:["ARCHAEOLOGICAL","ARTISTIC"],     lcc:"DG41",       source:"ccs_bootstrap", members:0 },
  { id:"sc_rr_society",         label:"Roman Society — Classes, Slavery & Family",        primary:"SOCIAL",       secondary:["POLITICAL","DEMOGRAPHIC"],        lcc:"DG59",       source:"ccs_bootstrap", members:0 },
  { id:"sc_rr_historiography",  label:"Roman Historiography & Primary Sources",           primary:"INTELLECTUAL", secondary:["ARCHAEOLOGICAL"],                lcc:"DG35",       source:"ccs_bootstrap", members:0 },
  { id:"sc_rr_material_culture",label:"Roman Material Culture, Art & Inscriptions",       primary:"ARCHAEOLOGICAL",secondary:["ARTISTIC","LINGUISTIC"],         lcc:"DG37",       source:"ccs_bootstrap", members:0 },
  { id:"sc_rr_literature",      label:"Roman Literature, Philosophy & Intellectual Life", primary:"INTELLECTUAL", secondary:["BIOGRAPHIC","LINGUISTIC"],        lcc:"PA6000-6971",source:"ccs_bootstrap", members:0,   cross:true },
  { id:"sc_rr_science",         label:"Roman Science, Technology & Medicine",             primary:"SCIENTIFIC",   secondary:["INTELLECTUAL"],                  lcc:"DG135",      source:"ccs_bootstrap", members:0 },
  // geo_bootstrap — spatial
  { id:"GEO_SETTLEMENTS",       label:"Settlements & Urban Places",                       primary:"GEOGRAPHIC",   secondary:["SOCIAL","ARCHAEOLOGICAL"],       lcc:"—",          source:"geo_bootstrap",  members:17521 },
  { id:"GEO_HIST_PLACES",       label:"Historical Places & Archaeological Sites",         primary:"ARCHAEOLOGICAL",secondary:["GEOGRAPHIC"],                    lcc:"—",          source:"geo_bootstrap",  members:11390 },
  { id:"GEO_GENERAL",           label:"General Geographic Places",                        primary:"GEOGRAPHIC",   secondary:["CULTURAL"],                      lcc:"—",          source:"geo_bootstrap",  members:11360 },
  { id:"GEO_PHYS_FEATURES",     label:"Physical Geography & Landforms",                   primary:"GEOGRAPHIC",   secondary:["ENVIRONMENTAL"],                 lcc:"—",          source:"geo_bootstrap",  members:2216 },
  { id:"GEO_HYDROGRAPHY",       label:"Hydrography & Water Bodies",                       primary:"GEOGRAPHIC",   secondary:["ENVIRONMENTAL"],                 lcc:"—",          source:"geo_bootstrap",  members:2115 },
  { id:"GEO_POLITICAL_ENTITIES",label:"States, Empires & Political Entities",             primary:"POLITICAL",    secondary:["GEOGRAPHIC","MILITARY"],          lcc:"—",          source:"geo_bootstrap",  members:1596 },
  { id:"GEO_ADMIN_DIVISIONS",   label:"Administrative & Political Divisions",             primary:"GEOGRAPHIC",   secondary:["POLITICAL","SOCIAL"],            lcc:"—",          source:"geo_bootstrap",  members:1126 },
];

const FACET_COLORS = {
  POLITICAL:"#E74C3C", MILITARY:"#2980B9", ECONOMIC:"#27AE60", SOCIAL:"#8E44AD",
  RELIGIOUS:"#9B59B6", INTELLECTUAL:"#1ABC9C", GEOGRAPHIC:"#2E8B57", ARCHAEOLOGICAL:"#E07C3E",
  ARTISTIC:"#F39C12", LINGUISTIC:"#006699", DIPLOMATIC:"#00C2A8", SCIENTIFIC:"#4ECDC4",
  BIOGRAPHIC:"#C0392B", DEMOGRAPHIC:"#16A085", ENVIRONMENTAL:"#1E8449", CULTURAL:"#D35400",
  TECHNOLOGICAL:"#7F8C8D", COMMUNICATION:"#BDC3C7",
};

// ══════════════════════════════════════════════════════════════════════════════
// RENDERING HELPERS
// ══════════════════════════════════════════════════════════════════════════════

function SysMLBlock({ block }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ border:`1px solid ${block.color}`, borderRadius:6, marginBottom:12, overflow:"hidden" }}>
      {/* Header — «block» stereotype + name */}
      <div
        onClick={() => setOpen(o => !o)}
        style={{ background:block.color+"22", borderBottom:`1px solid ${block.color}44`,
          padding:"8px 12px", cursor:"pointer", display:"flex", justifyContent:"space-between", alignItems:"center" }}
      >
        <span>
          <span style={{ color:block.color, fontSize:11, fontStyle:"italic", marginRight:6 }}>«block»</span>
          <span style={{ color:C.bright, fontWeight:"bold", fontSize:14 }}>{block.name}</span>
          <span style={{ color:C.dim, fontSize:11, marginLeft:10 }}>{block.count}</span>
          <span style={{ background:block.color+"33", color:block.color, fontSize:10, padding:"1px 6px",
            borderRadius:10, marginLeft:8 }}>{block.backbone}</span>
        </span>
        <span style={{ color:C.dim, fontSize:12 }}>{open ? "▲" : "▼"}</span>
      </div>
      {/* Description */}
      <div style={{ padding:"6px 12px", color:C.dim, fontSize:12, borderBottom:`1px solid ${C.border}` }}>
        {block.desc}
      </div>
      {open && (
        <>
          {/* Attributes compartment */}
          <div style={{ padding:"8px 12px", borderBottom:`1px solid ${C.border}` }}>
            <div style={{ color:C.dim, fontSize:10, fontStyle:"italic", marginBottom:4 }}>attributes</div>
            {block.attributes.map(a => (
              <div key={a.name} style={{ display:"flex", gap:8, fontSize:12, marginBottom:3 }}>
                <span style={{ color:C.facet, width:160 }}>{a.name}</span>
                <span style={{ color:C.dim, width:65 }}>{a.type}[{a.mult}]</span>
                <span style={{ color:C.bright+"88" }}>{a.example}</span>
              </div>
            ))}
          </div>
          {/* Relations compartment */}
          <div style={{ padding:"8px 12px" }}>
            <div style={{ color:C.dim, fontSize:10, fontStyle:"italic", marginBottom:4 }}>connections</div>
            {block.relations.map((r, i) => (
              <div key={i} style={{ display:"flex", gap:8, fontSize:12, marginBottom:3, alignItems:"center" }}>
                <span style={{ color:C.dim }}>{r.dir === "out" ? "→" : "←"}</span>
                <span style={{ color:C.subject, fontFamily:"monospace" }}>[:{r.rel}]</span>
                <span style={{ color:C.bright }}>{r.target}</span>
                <span style={{ color:C.dim }}>[{r.mult}]</span>
                {r.note && <span style={{ color:C.dim, fontSize:11 }}>({r.note})</span>}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function FacetPill({ facet, weight }) {
  const col = FACET_COLORS[facet] || C.dim;
  return (
    <span style={{ background:col+"22", color:col, border:`1px solid ${col}44`,
      fontSize:10, padding:"1px 6px", borderRadius:10, marginRight:3, whiteSpace:"nowrap" }}>
      {facet}{weight ? ` ${weight}` : ""}
    </span>
  );
}

function SCCard({ sc }) {
  const isCcs = sc.source === "ccs_bootstrap";
  return (
    <div style={{ border:`1px solid ${isCcs ? C.subject+"44" : C.geo+"44"}`, borderRadius:6,
      padding:"8px 10px", marginBottom:8, background:C.panel }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:4 }}>
        <div>
          <span style={{ color:isCcs ? C.subject : C.geo, fontWeight:"bold", fontSize:13 }}>
            {sc.label}
          </span>
          {sc.cross && <span style={{ color:C.warn, fontSize:10, marginLeft:6 }}>cross-class</span>}
        </div>
        <div style={{ textAlign:"right" }}>
          {sc.members > 0
            ? <span style={{ color:C.pass, fontSize:12, fontWeight:"bold" }}>{sc.members.toLocaleString()}</span>
            : <span style={{ color:C.fail, fontSize:11 }}>0 — needs SFA</span>}
          <div style={{ color:C.dim, fontSize:9 }}>members</div>
        </div>
      </div>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <div style={{ display:"flex", flexWrap:"wrap", gap:3 }}>
          <FacetPill facet={sc.primary} weight="★" />
          {sc.secondary.map(f => <FacetPill key={f} facet={f} />)}
        </div>
        <span style={{ color:C.lcc, fontSize:10, fontFamily:"monospace", marginLeft:8 }}>{sc.lcc}</span>
      </div>
      <div style={{ color:C.dim, fontSize:10, marginTop:4, fontFamily:"monospace" }}>{sc.id}</div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// BACKBONE INTERCONNECTION — IBD (Internal Block Diagram) style
// ══════════════════════════════════════════════════════════════════════════════
function BackboneIBD() {
  const box = (label, color, lines, bottom) => (
    <div style={{ border:`2px solid ${color}`, borderRadius:8, padding:"10px 14px",
      background:color+"0D", minWidth:190, maxWidth:220 }}>
      <div style={{ color, fontWeight:"bold", fontSize:13, marginBottom:6 }}>{label}</div>
      {lines.map((l, i) => (
        <div key={i} style={{ color:C.dim, fontSize:11, marginBottom:2 }}>
          {typeof l === "string" ? l : <span style={{ color:l[1] }}>{l[0]}</span>}
        </div>
      ))}
      {bottom && <div style={{ color:C.warn, fontSize:10, marginTop:6, fontStyle:"italic" }}>{bottom}</div>}
    </div>
  );

  const arrow = (label, color) => (
    <div style={{ display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center",
      padding:"0 8px", color:color || C.rel, fontSize:11, minWidth:110 }}>
      <div style={{ borderTop:`1px dashed ${color || C.rel}`, width:"100%", marginBottom:3 }} />
      <div style={{ color:color || C.rel, fontSize:10 }}>{label}</div>
    </div>
  );

  return (
    <div style={{ background:C.panel, borderRadius:8, padding:16, marginBottom:16 }}>
      <div style={{ color:C.dim, fontSize:11, marginBottom:12, fontStyle:"italic" }}>
        «ibd» Chrystallum Domain Backbone — Roman Republic
      </div>

      {/* Row 1: Temporal + Subject + Geo */}
      <div style={{ display:"flex", alignItems:"center", gap:0, flexWrap:"wrap", gap:8, marginBottom:12 }}>
        {box("«block» Period", C.temporal, [
          ["Q17167 Roman Republic", C.bright],
          "start = -509 | end = -27",
          "← IN_PERIOD: 3,447 persons",
          "← IN_PERIOD: 32,565 places",
        ])}
        {arrow("OCCURS_DURING →", C.temporal)}
        {box("«block» SubjectDomain", C.subject, [
          ["domain_roman_republic", C.bright],
          "governed_by = ADR-020",
          "→ 5 ALIGNED_WITH_LCC",
          "← 5 COVERS_DOMAIN",
        ])}
        {arrow("← COVERS_DOMAIN", C.subject)}
        {box("«block» Discipline", C.subject+"88", [
          ["972 backbone nodes", C.bright],
          "history of Rome",
          "prosopography",
          "classical philology",
          "+ 2 more",
        ])}
      </div>

      {/* Row 2: SubjectConcepts */}
      <div style={{ display:"flex", alignItems:"center", gap:8, flexWrap:"wrap", marginBottom:12 }}>
        {box("«block» SubjectConcept ×22", C.subject, [
          ["15 ccs_bootstrap (thematic)", C.subject],
          ["7 geo_bootstrap (spatial)", C.geo],
          "all: ≥2 HAS_FACET edges",
          "all: ≥1 ANCHORS → LCC_Class",
          "source of truth: ADR-020",
        ], "scaffold — batch_train pending")}
        {arrow("HAS_FACET {weight} →", C.facet)}
        {box("«block» Facet ×18", C.facet, [
          ["POLITICAL, MILITARY, …", C.bright],
          "primary (is_primary=true)",
          "secondary weights: 0.3–0.8",
          "key + label only",
          "(no facet_id)",
        ])}
        {arrow("ANCHORS →", C.lcc)}
        {box("«block» LCC_Class ~141", C.lcc, [
          ["DG1-365 (Ancient Rome)", C.bright],
          "KJA2-3660 (Roman Law)",
          "PA6000-6971 (Roman Lit)",
          "cross-class: 2 SCs",
        ])}
      </div>

      {/* Row 3: People and Places */}
      <div style={{ display:"flex", alignItems:"center", gap:8, flexWrap:"wrap" }}>
        {box("«block» Person ×5,248", C.temporal, [
          ["4,863 DPRR (in-domain)", C.bright],
          "385 QID-only (out-of-domain)",
          "→ IN_PERIOD (3,447)",
          "→ SCOPED_TO disciplines",
        ])}
        {arrow("MEMBER_OF →", C.subject)}
        {box("«block» SubjectConcept", C.subject, [
          "← population source",
          "MEMBER_OF from persons",
          "MEMBER_OF from places",
          "entity_count tracked",
        ])}
        {arrow("← MEMBER_OF", C.subject)}
        {box("«block» Place ×44,193", C.geo, [
          ["42,065 Pleiades", C.bright],
          "32,565 IN_PERIOD (RR)",
          "→ SCOPED_TO: archaeology",
          "→ SCOPED_TO: topography",
        ])}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ══════════════════════════════════════════════════════════════════════════════
const TABS = ["ibd", "blocks", "ccs", "gallery"];
const TAB_LABELS = { ibd:"Interconnection Diagram", blocks:"Block Definitions", ccs:"CCS Architecture", gallery:"SC Gallery" };

export default function SubjectConstitution() {
  const [tab, setTab] = useState("ibd");

  return (
    <div style={{ background:C.bg, minHeight:"100vh", color:C.bright, fontFamily:"system-ui, sans-serif" }}>
      {/* Header */}
      <div style={{ background:C.panel, borderBottom:`1px solid ${C.border}`, padding:"12px 20px" }}>
        <div style={{ fontSize:16, fontWeight:"bold", color:C.subject, marginBottom:2 }}>
          Subject · Temporal · Geographic Backbone Constitution
        </div>
        <div style={{ fontSize:12, color:C.dim }}>
          CCS (Chrystallum Classification System) — SysML v2 structure view — ADR-020 — domain_roman_republic
        </div>
        {/* Stats row */}
        <div style={{ display:"flex", gap:20, marginTop:10, flexWrap:"wrap" }}>
          {[
            ["SubjectConcepts", STATS.subject.total_scs, C.subject],
            ["ccs_bootstrap", STATS.subject.ccs_bootstrap, C.subject],
            ["geo_bootstrap", STATS.subject.geo_bootstrap, C.geo],
            ["MEMBER_OF edges", STATS.subject.total_member_of.toLocaleString(), C.pass],
            ["HAS_FACET edges", STATS.subject.facet_edges, C.facet],
            ["LCC ANCHORS", STATS.subject.lcc_anchor_edges, C.lcc],
            ["Persons in Period", STATS.temporal.persons_in_period.toLocaleString(), C.temporal],
            ["Places in Period", STATS.temporal.places_in_period.toLocaleString(), C.geo],
          ].map(([k, v, col]) => (
            <div key={k} style={{ textAlign:"center" }}>
              <div style={{ fontSize:20, fontWeight:"bold", color:col }}>{v}</div>
              <div style={{ fontSize:10, color:C.dim }}>{k}</div>
            </div>
          ))}
        </div>
        {/* Tabs */}
        <div style={{ display:"flex", gap:6, marginTop:12 }}>
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding:"5px 14px", border:"none", borderRadius:4, cursor:"pointer", fontSize:12,
              background: tab === t ? C.subject : "#222", color: tab === t ? "#000" : C.dim,
              fontWeight: tab === t ? "bold" : "normal",
            }}>{TAB_LABELS[t]}</button>
          ))}
        </div>
      </div>

      <div style={{ padding:"16px 20px", maxWidth:1200 }}>

        {/* ── IBD TAB ── */}
        {tab === "ibd" && (
          <div>
            <BackboneIBD />
            {/* Validity rules */}
            <div style={{ background:C.panel, borderRadius:8, padding:16 }}>
              <div style={{ color:C.subject, fontWeight:"bold", marginBottom:10 }}>CCS Validity Rules (ADR-020)</div>
              {CCS_RULES.map(r => (
                <div key={r.id} style={{ display:"flex", gap:12, marginBottom:8, alignItems:"flex-start" }}>
                  <span style={{ color:C.subject, fontSize:11, width:50, flexShrink:0 }}>{r.id}</span>
                  <span style={{ color:C.bright, width:130, flexShrink:0 }}>{r.name}</span>
                  <span style={{ color:C.dim, fontSize:12, flex:1 }}>{r.desc}</span>
                  <span style={{ color:C.pass, fontSize:11, width:90, flexShrink:0, textAlign:"right" }}>✓ {r.pass}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── BLOCKS TAB ── */}
        {tab === "blocks" && (
          <div>
            <div style={{ color:C.dim, fontSize:12, marginBottom:12, fontStyle:"italic" }}>
              Click any block to expand attributes and connections. Multiplicity notation: 1=exactly one, 0..1=optional, 1..*=one or more, 0..*=many.
            </div>
            {BLOCKS.map(b => <SysMLBlock key={b.name} block={b} />)}
          </div>
        )}

        {/* ── CCS TAB ── */}
        {tab === "ccs" && (
          <div>
            <div style={{ background:C.panel, borderRadius:8, padding:16, marginBottom:16 }}>
              <div style={{ color:C.ccs, fontWeight:"bold", fontSize:15, marginBottom:6 }}>
                Chrystallum Classification System (CCS)
              </div>
              <div style={{ color:C.dim, fontSize:13, lineHeight:1.6, marginBottom:12 }}>
                CCS is an AI-powered rationalization layer over LCC/LCSH/FAST/Dewey. It does not replace those systems —
                they remain the authority backbone. CCS makes their inherently scattered, monodimensional representation
                navigable as a multidimensional knowledge structure by: harvesting authority tethers, aggregating
                cross-class scatter into a single node, and inferring a weighted 18-dimensional facet vector.
              </div>
              <div style={{ display:"flex", gap:12, flexWrap:"wrap" }}>
                <div style={{ background:"#162330", padding:8, borderRadius:4, fontSize:11, color:C.dim }}>
                  <span style={{ color:C.warn }}>Problem 1:</span> Cross-class scatter — Roman Law at DG87 + KJA2-3660 + KJA190-2152 + PA6000-6971
                </div>
                <div style={{ background:"#162330", padding:8, borderRadius:4, fontSize:11, color:C.dim }}>
                  <span style={{ color:C.warn }}>Problem 2:</span> Monodimensional — one heading per book; reality is multi-faceted
                </div>
                <div style={{ background:"#162330", padding:8, borderRadius:4, fontSize:11, color:C.dim }}>
                  <span style={{ color:C.warn }}>Problem 3:</span> Type buckets — "Military Figures" not a topic; "Roman Army" is
                </div>
              </div>
            </div>

            {CCS_STEPS.map(s => (
              <div key={s.step} style={{ border:`1px solid ${C.ccs}44`, borderRadius:8, padding:16, marginBottom:12 }}>
                <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:8 }}>
                  <div style={{ background:C.ccs, color:"#fff", borderRadius:"50%", width:28, height:28,
                    display:"flex", alignItems:"center", justifyContent:"center", fontWeight:"bold", fontSize:14, flexShrink:0 }}>
                    {s.step}
                  </div>
                  <span style={{ color:C.ccs, fontWeight:"bold", fontSize:14 }}>{s.name}</span>
                  <span style={{ color:C.pass, fontSize:11, fontFamily:"monospace" }}>→ {s.output}</span>
                </div>
                <div style={{ color:C.dim, fontSize:13, lineHeight:1.6, marginBottom:8 }}>{s.desc}</div>
                <div style={{ background:C.bg, borderRadius:4, padding:"6px 10px", fontSize:11,
                  color:C.bright+"88", fontFamily:"monospace" }}>
                  Example: {s.example}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── GALLERY TAB ── */}
        {tab === "gallery" && (
          <div>
            <div style={{ display:"flex", gap:8, marginBottom:12, flexWrap:"wrap", alignItems:"center" }}>
              <span style={{ color:C.dim, fontSize:12 }}>22 SubjectConcepts — ★ = primary facet |</span>
              <span style={{ background:C.subject+"22", color:C.subject, padding:"2px 8px", borderRadius:10, fontSize:11 }}>
                ● ccs_bootstrap (thematic, LCC-anchored)
              </span>
              <span style={{ background:C.geo+"22", color:C.geo, padding:"2px 8px", borderRadius:10, fontSize:11 }}>
                ● geo_bootstrap (spatial, Pleiades-populated)
              </span>
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(340px, 1fr))", gap:4 }}>
              {SC_GALLERY.map(sc => <SCCard key={sc.id} sc={sc} />)}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
