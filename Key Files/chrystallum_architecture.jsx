import { useState } from "react";

const C = {
  navy: "#1F3864", blue: "#2E75B6", teal: "#17A589",
  amber: "#D4A017", green: "#1E8449", red: "#C0392B",
  slate: "#4A5568", light: "#EBF0F7", white: "#FFFFFF",
  mid: "#BDC3C7", dark: "#2C3E50", purple: "#6B46C1",
};

// ── tiny primitives ────────────────────────────────────────────────────────────
const Box = ({ x, y, w, h, fill = C.light, stroke = C.slate, rx = 4, opacity = 1 }) => (
  <rect x={x} y={y} width={w} height={h} rx={rx} fill={fill} stroke={stroke}
    strokeWidth={1.5} opacity={opacity} />
);
const Txt = ({ x, y, s = 11, fill = C.dark, bold = false, center = false, italic = false, children }) => (
  <text x={x} y={y} fontSize={s} fill={fill}
    fontWeight={bold ? "bold" : "normal"}
    fontStyle={italic ? "italic" : "normal"}
    fontFamily="Arial, sans-serif"
    textAnchor={center ? "middle" : "start"}>{children}</text>
);
const Pill = ({ x, y, w = 80, h = 20, fill, stroke, label, textColor = C.white, s = 9 }) => (
  <g>
    <rect x={x} y={y} width={w} height={h} rx={10} fill={fill} stroke={stroke || fill} strokeWidth={1} />
    <Txt x={x + w / 2} y={y + 13} s={s} fill={textColor} center>{label}</Txt>
  </g>
);
const Line = ({ x1, y1, x2, y2, stroke = C.mid, dashed = false, width = 1.2 }) => (
  <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={stroke} strokeWidth={width}
    strokeDasharray={dashed ? "5,3" : undefined} />
);
const Arrow = ({ x1, y1, x2, y2, stroke = C.blue, dashed = false, width = 1.5 }) => {
  const dx = x2 - x1, dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  const ux = dx / len, uy = dy / len;
  const ax = x2 - ux * 8, ay = y2 - uy * 8;
  const px = -uy * 4, py = ux * 4;
  return (
    <g>
      <line x1={x1} y1={y1} x2={ax} y2={ay} stroke={stroke} strokeWidth={width}
        strokeDasharray={dashed ? "5,3" : undefined} />
      <polygon points={`${x2},${y2} ${ax + px},${ay + py} ${ax - px},${ay - py}`}
        fill={stroke} />
    </g>
  );
};

// ── layer header ──────────────────────────────────────────────────────────────
const LayerHeader = ({ x, y, w, label, sub, fill }) => (
  <g>
    <rect x={x} y={y} width={w} height={30} rx={4} fill={fill} />
    <Txt x={x + 10} y={y + 19} s={12} fill={C.white} bold>{label}</Txt>
    {sub && <Txt x={x + w - 8} y={y + 19} s={9} fill="rgba(255,255,255,0.75)"
      style={{ textAnchor: "end" }}>{sub}</Txt>}
  </g>
);

// ── status dot ────────────────────────────────────────────────────────────────
const Dot = ({ x, y, status }) => {
  const col = status === "operational" ? C.green
    : status === "blocked" ? C.red
      : status === "partial" ? C.amber : C.mid;
  return <circle cx={x} cy={y} r={4} fill={col} />;
};

// ── section box with title bar ────────────────────────────────────────────────
const Section = ({ x, y, w, h, title, fill = C.light, titleFill = C.slate }) => (
  <g>
    <Box x={x} y={y} w={w} h={h} fill={fill} stroke={titleFill} rx={5} />
    <rect x={x} y={y} width={w} height={18} rx={4} fill={titleFill} />
    <rect x={x} y={y + 14} width={w} height={4} fill={titleFill} />
    <Txt x={x + w / 2} y={y + 12} s={9} fill={C.white} bold center>{title}</Txt>
  </g>
);

// ── node type chip ─────────────────────────────────────────────────────────────
const NodeChip = ({ x, y, label, count, fill = C.blue }) => (
  <g>
    <rect x={x} y={y} width={90} height={22} rx={3} fill={fill} opacity={0.15}
      stroke={fill} strokeWidth={1} />
    <Txt x={x + 5} y={y + 14} s={8.5} fill={fill} bold>{label}</Txt>
    {count && <Txt x={x + 85} y={y + 14} s={8} fill={fill}
      style={{ textAnchor: "end" }} italic>{count}</Txt>}
  </g>
);

export default function ChrystallumArchitecture() {
  const [hover, setHover] = useState(null);
  const W = 1100, H = 1480;

  const federationSources = [
    { id: "Wikidata", status: "operational", x: 30 },
    { id: "DPRR", status: "blocked", x: 115 },
    { id: "Pleiades", status: "operational", x: 200 },
    { id: "PeriodO", status: "operational", x: 285 },
    { id: "LCSH/FAST", status: "operational", x: 370 },
    { id: "Trismegistos", status: "operational", x: 455 },
    { id: "LGPN", status: "operational", x: 560 },
    { id: "VIAF", status: "partial", x: 645 },
    { id: "Getty AAT", status: "partial", x: 730 },
    { id: "Nomisma", status: "future", x: 825 },
    { id: "OCD", status: "planned", x: 910 },
    { id: "OpenAlex", status: "planned", x: 995 },
  ];

  return (
    <div style={{ background: "#F8F9FA", padding: 16, fontFamily: "Arial, sans-serif" }}>
      {/* title */}
      <div style={{ marginBottom: 8 }}>
        <span style={{ fontSize: 20, fontWeight: "bold", color: C.navy }}>CHRYSTALLUM</span>
        <span style={{ fontSize: 13, color: C.slate, marginLeft: 12 }}>
          Logical Architecture — Top-Down View
        </span>
        <span style={{ float: "right", fontSize: 11, color: C.mid }}>2026-03-08</span>
      </div>

      {/* legend */}
      <div style={{ display: "flex", gap: 16, marginBottom: 10, fontSize: 10, color: C.slate }}>
        {[["operational", C.green], ["partial", C.amber], ["blocked", C.red], ["planned", C.mid], ["future", C.mid]].map(([l, c]) => (
          <span key={l} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: c, display: "inline-block" }} />
            {l}
          </span>
        ))}
        <span style={{ marginLeft: 16, display: "flex", alignItems: "center", gap: 4 }}>
          <svg width={30} height={12}><line x1={0} y1={6} x2={20} y2={6} stroke={C.blue} strokeWidth={1.5} /><polygon points="20,6 14,3 14,9" fill={C.blue} /></svg>
          data flow
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <svg width={30} height={12}><line x1={0} y1={6} x2={20} y2={6} stroke={C.slate} strokeWidth={1.2} strokeDasharray="4,2" /><polygon points="20,6 14,3 14,9" fill={C.slate} /></svg>
          reference / config
        </span>
      </div>

      <svg width="100%" viewBox={`0 0 ${W} ${H}`}
        style={{ border: `1px solid ${C.mid}`, borderRadius: 6, background: C.white }}>

        {/* ── LAYER 0: Federation Sources ───────────────────────────────────── */}
        <LayerHeader x={10} y={10} w={W - 20} label="LAYER 0 — Federation Sources"
          sub="17 registered · 6 operational · 2 partial · 1 blocked · 8 planned · 1 future" fill={C.navy} />

        {/* source boxes */}
        {federationSources.map((src, i) => {
          const bx = src.x, by = 48, bw = 78, bh = 34;
          return (
            <g key={src.id}
              onMouseEnter={() => setHover(src.id)}
              onMouseLeave={() => setHover(null)}
              style={{ cursor: "pointer" }}>
              <rect x={bx} y={by} width={bw} height={bh} rx={3}
                fill={hover === src.id ? "#EBF5FB" : C.light}
                stroke={src.status === "blocked" ? C.red
                  : src.status === "partial" ? C.amber
                    : src.status === "planned" || src.status === "future" ? C.mid : C.teal}
                strokeWidth={1.5}
                strokeDasharray={src.status === "planned" || src.status === "future" ? "4,2" : undefined} />
              <Dot x={bx + bw - 8} y={by + 8} status={src.status} />
              <Txt x={bx + bw / 2} y={by + 20} s={8} fill={C.dark} center bold>{src.id}</Txt>
              <Txt x={bx + bw / 2} y={by + 31} s={7} fill={C.mid} center italic>
                {src.status === "blocked" ? "snapshot" : src.status === "future" ? "future" : src.status}
              </Txt>
            </g>
          );
        })}

        {/* ── LAYER 1: Harvest Pipeline ─────────────────────────────────────── */}
        <LayerHeader x={10} y={100} w={W - 20} label="LAYER 1 — Harvest Pipeline  (Deterministic Pre-processing)"
          fill={C.blue} />

        {/* L1 boxes */}
        {[
          { x: 20, label: "DPRR Label\nParser", sub: "grammar-based\ntria nomina extract" },
          { x: 160, label: "P-code → Rel\nMapper", sub: "17 canonical\nmappings" },
          { x: 300, label: "Date\nNormaliser", sub: "ISO 8601\nBCE offset" },
          { x: 440, label: "WD Backlink\nCapture", sub: "10-bucket\ntaxonomy" },
          { x: 580, label: "Federation\nStatus Check", sub: "blocked→local\nfallback" },
          { x: 720, label: "QID\nValidator", sub: "format + graph\ncollision check" },
          { x: 860, label: "Context Packet\nAssembler", sub: "fixed snapshot\nfor agent" },
        ].map(({ x, label, sub }) => (
          <g key={x}>
            <Box x={x} y={118} w={128} h={48} fill="#EBF5FB" stroke={C.blue} rx={4} />
            <Txt x={x + 64} y={134} s={9} fill={C.navy} bold center>{label.split("\n")[0]}</Txt>
            <Txt x={x + 64} y={145} s={9} fill={C.navy} bold center>{label.split("\n")[1]}</Txt>
            <Txt x={x + 64} y={157} s={7.5} fill={C.slate} center italic>{sub.split("\n")[0]}</Txt>
            <Txt x={x + 64} y={167} s={7.5} fill={C.slate} center italic>{sub.split("\n")[1]}</Txt>
          </g>
        ))}

        {/* ── LAYER 2: Agent Reasoning ──────────────────────────────────────── */}
        <LayerHeader x={10} y={180} w={W - 20} label="LAYER 2 — Agent Reasoning  (LLM-orchestrated)"
          sub="PersonHarvestPlan · never writes to graph" fill={C.teal} />

        <Box x={20} y={198} w={500} h={100} fill="#EAFAF1" stroke={C.teal} rx={5} />
        <Txt x={270} y={214} s={10} fill={C.green} bold center>LLM Agent</Txt>

        {[
          "Cross-federation name reconciliation",
          "Conflict type classification (Types 1–4)",
          "Authority tier weighting per attribute",
          "Filiation chain disambiguation",
          "Federation scope mismatch vs genuine absence",
          "Mythological / legendary classification",
          "ConflictNote drafting for human review",
          "backlink_significance_note",
        ].map((task, i) => {
          const col = i < 4 ? 30 : 270;
          const row = i < 4 ? i : i - 4;
          return (
            <g key={task}>
              <circle cx={col + 6} cy={226 + row * 17} r={3} fill={C.teal} />
              <Txt x={col + 14} y={230 + row * 17} s={8.5} fill={C.dark}>{task}</Txt>
            </g>
          );
        })}

        {/* PersonHarvestPlan output */}
        <Box x={540} y={198} w={210} h={100} fill="#EAFAF1" stroke={C.teal} rx={5} />
        <Txt x={645} y={214} s={10} fill={C.green} bold center>PersonHarvestPlan</Txt>
        {["plan_id, harvest_mode", "identity_resolution_decisions[]", "attribute_claims[]", "conflict_notes[]",
          "onomastic_parse", "domain_scope + threshold_override", "execution_status (resumable)", "agent_model (auditable)"
        ].map((f, i) => (
          <Txt key={f} x={548} y={227 + i * 11} s={7.5} fill={C.dark}>{f}</Txt>
        ))}

        {/* Constraints box */}
        <Box x={765} y={198} w={320} h={100} fill="#FEF9E7" stroke={C.amber} rx={5} />
        <Txt x={925} y={214} s={10} fill={C.amber} bold center>Agent Constraints</Txt>
        {[
          "✗  Cannot write nodes or edges",
          "✗  Cannot query live graph during reasoning",
          "✗  Cannot evaluate numeric thresholds",
          "✗  Cannot generate freeform Cypher",
          "✗  Cannot make claim promotion decisions",
          "✓  Receives fixed context packet only",
          "✓  Plan is auditable + re-runnable",
          "✓  Can use any LLM — model versioned",
        ].map((c, i) => (
          <Txt key={c} x={775} y={227 + i * 11} s={8} fill={i < 5 ? C.red : C.green}>{c}</Txt>
        ))}

        {/* ── LAYER 3: Deterministic Execution ─────────────────────────────── */}
        <LayerHeader x={10} y={310} w={W - 20} label="LAYER 3 — Deterministic Execution  (Schema-validated Cypher)"
          sub="13-step sequence · idempotent · ADR-006 ScaffoldNode/ScaffoldEdge compliant" fill={C.slate} />

        {[
          ["1", "Write SYS_\nHarvestPlan", C.slate],
          ["2", "Merge Gens /\nTribe / Polity", C.blue],
          ["3", "Merge Praenomen\nNomen Cognomen", C.blue],
          ["4", "Apply :Person /\n:Mythological label", C.teal],
          ["5", "Write literal\nproperties", C.slate],
          ["6", "Write onomastic\nrelationships", C.blue],
          ["7", "Write civic /\npolitical rels", C.teal],
          ["8", "Write family\nrel enrichments", C.blue],
          ["9", "Write office /\nmilitary rels", C.teal],
          ["10", "Write authority\nrecord links", C.slate],
          ["11", "Write conflict\nstructures", C.red],
          ["12", "Evaluate D10\nthreshold", C.amber],
          ["13", "Set execution_\nstatus COMPLETE", C.green],
        ].map(([n, label, col], i) => {
          const bx = 12 + i * 82, by = 328, bw = 76, bh = 48;
          return (
            <g key={n}>
              <rect x={bx} y={by} width={bw} height={bh} rx={3}
                fill={col + "18"} stroke={col} strokeWidth={1.2} />
              <Txt x={bx + 4} y={by + 11} s={8} fill={col} bold>{n}</Txt>
              <Txt x={bx + bw / 2} y={by + 27} s={8} fill={C.dark} center>
                {label.split("\n")[0]}</Txt>
              <Txt x={bx + bw / 2} y={by + 38} s={8} fill={C.dark} center>
                {label.split("\n")[1]}</Txt>
              {i < 12 && <Arrow x1={bx + bw} y1={by + 24} x2={bx + bw + 5} y2={by + 24}
                stroke={C.mid} width={1} />}
            </g>
          );
        })}

        {/* ── NEO4J GRAPH ───────────────────────────────────────────────────── */}
        <LayerHeader x={10} y={390} w={W - 20} label="NEO4J GRAPH  (~110k nodes · 113 relationship types)"
          sub="Single source of truth · ADR-001 cipher architecture · ADR-006 provenance" fill={C.navy} />

        {/* SYS layer */}
        <Section x={15} y={410} w={340} h={210} title="SYSTEM LAYER  (self-describing)" titleFill={C.navy} />
        {[
          ["SYS_FederationSource", "17", C.blue],
          ["SYS_AuthorityTier", "6", C.blue],
          ["SYS_ConfidenceTier", "8", C.blue],
          ["SYS_DecisionTable + DecisionRow", "23 + 128", C.teal],
          ["SYS_Policy", "20", C.teal],
          ["SYS_Threshold", "27", C.teal],
          ["SYS_FacetRouter", "38", C.teal],
          ["SYS_CurationDecision", "15", C.teal],
          ["SYS_RelationshipType", "113", C.slate],
          ["SYS_NodeType", "10", C.slate],
          ["SYS_ADR + OnboardingProtocol", "5 + 2", C.navy],
          ["Framework (HAS_FRAMEWORK)", "3", C.purple],
          ["Fallacy + TaskType (Fischer)", "6 + 11", C.purple],
          ["DigitalPrinciple (Milligan)", "6", C.purple],
          ["RepertoirePattern + Mechanism (PRH)", "12 + 7", C.purple],
        ].map(([label, count, col], i) => (
          <g key={label}>
            <NodeChip x={20} y={428 + i * 8} label={label} count={count} fill={col} />
          </g>
        ))}

        {/* Domain layer */}
        <Section x={365} y={410} w={490} h={210} title="DOMAIN LAYER  (knowledge)" titleFill={C.blue} />

        {/* Person cluster */}
        <Section x={372} y={428} w={155} h={108} title=":Person cluster" titleFill={C.teal} fill="#EAFAF1" />
        {[
          [":Person", "5,248", C.teal],
          [":MythologicalPerson", "3", C.teal],
          [":Gens", "585", C.blue],
          [":Nomen", "917", C.blue],
          [":Cognomen", "993", C.blue],
          [":Praenomen", "24", C.blue],
          [":Tribe", "29", C.blue],
          [":HistoricalPolity", "9", C.amber],
        ].map(([label, count, col], i) => (
          <NodeChip key={label} x={375} y={446 + i * 11} label={label} count={count} fill={col} />
        ))}

        {/* Place cluster */}
        <Section x={532} y={428} w={155} h={108} title=":Place cluster" titleFill={C.teal} fill="#EAFAF1" />
        {[
          [":Place", "43,958", C.teal],
          [":Pleiades_Place", "32,572", C.blue],
          [":HistoricalPolity", "(overlap)", C.amber],
        ].map(([label, count, col], i) => (
          <NodeChip key={label} x={535} y={446 + i * 11} label={label} count={count} fill={col} />
        ))}

        {/* Knowledge cluster */}
        <Section x={692} y={428} w={158} h={108} title="Knowledge / Taxonomy" titleFill={C.slate} fill="#F8F9FA" />
        {[
          [":Discipline", "675", C.navy],
          [":LCC_Class", "4,490", C.navy],
          [":Periodo_Period", "1,118", C.teal],
          [":LCSH_Heading", "15", C.blue],
          [":WorldCat_Work", "196", C.slate],
          [":Year", "4,025", C.mid],
          [":Position", "171", C.slate],
          [":Facet", "18", C.blue],
          [":SubjectConcept", "61", C.blue],
        ].map(([label, count, col], i) => (
          <NodeChip key={label} x={695} y={446 + i * 11} label={label} count={count} fill={col} />
        ))}

        {/* Person External ID Nodes */}
        <Section x={372} y={540} w={238} h={76} title="Person External IDs  (16 types · 4,232 nodes)"
          titleFill={C.purple} fill="#F3F0FF" />
        {[
          ["VIAF_Cluster", "843"],
          ["GND_Person", "699"],
          ["ISNI_Record", "467"],
          ["BritishMuseum_Person", "460"],
          ["LCNAF_Authority", "395"],
          ["OCD_Entry", "341"],
        ].map(([label, count], i) => (
          <g key={label}>
            <Txt x={378} y={560 + i * 10} s={7.5} fill={C.purple}>{label}</Txt>
            <Txt x={500} y={560 + i * 10} s={7.5} fill={C.slate}>{count}</Txt>
          </g>
        ))}
        <Txt x={520} y={570} s={7.5} fill={C.purple} italic>+ 10 more types</Txt>
        <Txt x={520} y={582} s={7} fill={C.slate} italic>cipher: QID:PID:value</Txt>

        {/* Discipline External ID Nodes */}
        <Section x={616} y={540} w={238} h={76} title="Discipline External IDs  (12 types · 3,028 nodes)"
          titleFill={C.purple} fill="#F3F0FF" />
        {[
          ["FAST_Heading", "675"],
          ["Getty_AAT_Concept", "618"],
          ["OpenAlex_Concept", "592"],
          ["GND_Concept", "462"],
          ["BnF_Concept", "189"],
          ["MeSH_Descriptor", "167"],
        ].map(([label, count], i) => (
          <g key={label}>
            <Txt x={622} y={560 + i * 10} s={7.5} fill={C.purple}>{label}</Txt>
            <Txt x={744} y={560 + i * 10} s={7.5} fill={C.slate}>{count}</Txt>
          </g>
        ))}
        <Txt x={764} y={570} s={7.5} fill={C.purple} italic>+ 6 more types</Txt>
        <Txt x={764} y={582} s={7} fill={C.slate} italic>cipher: QID:PID:value</Txt>

        {/* FIELD_OF_WORK bridge annotation */}
        <Arrow x1={450} y1={536} x2={450} y2={540} stroke={C.purple} width={1.2} />
        <Arrow x1={735} y1={536} x2={735} y2={540} stroke={C.purple} width={1.2} />
        <Txt x={528} y={536} s={7.5} fill={C.teal} bold center>FIELD_OF_WORK (128)</Txt>
        <Arrow x1={500} y1={530} x2={530} y2={530} stroke={C.teal} width={1} dashed />
        <Arrow x1={555} y1={530} x2={620} y2={530} stroke={C.teal} width={1} dashed />

        {/* Claim / provenance layer */}
        <Section x={860} y={410} w={228} h={210} title="CLAIM & PROVENANCE LAYER" titleFill={C.amber} />
        {[
          ["Claim status cycle:", "", C.amber],
          ["  Proposed → Under Review", "", C.amber],
          ["  → Accepted / Rejected", "", C.amber],
          ["ScaffoldNode (stub)", "", C.slate],
          ["ScaffoldEdge + FROM/TO", "", C.slate],
          ["ConflictNote", "", C.red],
          ["source_authority_tier", "", C.blue],
          ["confidence (0–1)", "", C.blue],
          ["D10 threshold: 0.75 / 0.90", "", C.teal],
        ].map(([label, count, col], i) => (
          <Txt key={label} x={867} y={428 + i * 12} s={8.5} fill={col}>{label}</Txt>
        ))}

        {/* ── CIPHER ARCHITECTURE ───────────────────────────────────────────── */}
        <Section x={15} y={633} w={1074} h={54} title="CIPHER ARCHITECTURE  (ADR-001)" titleFill={C.navy} />
        {[
          "entity_cipher: SHA-256 hash of (entity_type + canonical_id + source_namespace)",
          "→ O(1) vertex lookup · content-addressable storage · deduplication without graph traversal",
          "→ cross-federation merge: same cipher = same entity regardless of source label",
          "edge_cipher: hash of (source_entity_id + rel_type + target_entity_id) · idempotent MERGE",
          "external_id_cipher: QID:PID:value — deterministic jump address (e.g. Q2263:P214:27062070 = Cicero's VIAF)",
        ].map((t, i) => (
          <Txt key={t} x={22} y={652 + i * 11} s={8} fill={i === 0 ? C.navy : i === 4 ? C.purple : C.slate}
            bold={i === 0}>{t}</Txt>
        ))}

        {/* ── QUERY / ACCESS LAYER ──────────────────────────────────────────── */}
        <LayerHeader x={10} y={698} w={W - 20} label="QUERY & ACCESS LAYER" fill={C.slate} />

        {[
          { x: 20, w: 200, title: "Cypher Query Patterns", fill: "#F8F9FA", stroke: C.slate,
            items: ["SYS_QueryPattern registry (5)", "Onboarding: 26-step protocol", "Subgraph traversal", "Cross-domain synthesis"] },
          { x: 230, w: 200, title: "MCP (Model Context Protocol)", fill: "#EAFAF1", stroke: C.teal,
            items: ["read-only + write tools", "Claude direct access", "run_cypher_readonly", "Agent tool binding"] },
          { x: 440, w: 200, title: "Neo4j Bloom / Browser", fill: "#EBF0F7", stroke: C.blue,
            items: ["Visual exploration", "Subgraph rendering", "Relationship inspection", "Ad-hoc Cypher"] },
          { x: 650, w: 200, title: "Planned: React UI", fill: "#FEF9E7", stroke: C.amber,
            items: ["Context-driven surfacing", "Temporal decay relevance", "Bookmark portals", "Person family trees"] },
          { x: 860, w: 228, title: "Planned: GEDCOM 7.0 Export", fill: "#FDEDEC", stroke: C.red,
            items: ["OI-008-05", "FAM derived at export", "BCE year offset applied", "Custom _GENS _TRIBE tags"] },
        ].map(({ x, w, title, fill, stroke, items }) => (
          <g key={title}>
            <Box x={x} y={716} w={w} h={72} fill={fill} stroke={stroke} rx={4} />
            <Txt x={x + w / 2} y={730} s={9} fill={stroke} bold center>{title}</Txt>
            {items.map((item, i) => (
              <g key={item}>
                <circle cx={x + 10} cy={740 + i * 12} r={2.5} fill={stroke} opacity={0.6} />
                <Txt x={x + 16} y={744 + i * 12} s={8} fill={C.dark}>{item}</Txt>
              </g>
            ))}
          </g>
        ))}

        {/* ── STANDARDS ALIGNMENT ───────────────────────────────────────────── */}
        <LayerHeader x={10} y={798} w={W - 20} label="STANDARDS ALIGNMENT" fill={C.navy} />

        {[
          { x: 20, label: "CIDOC-CRM\n(ISO 21127)", role: "Internal ontological anchor", status: "E74_Group · E53_Place · E21_Person", col: C.navy },
          { x: 230, label: "GEDCOM 7.0", role: "Export target (derived)", status: "OI-008-05 — not yet built", col: C.blue },
          { x: 440, label: "LOD / RDF", role: "Future public URI publication", status: "planned", col: C.mid },
          { x: 650, label: "SPARQL", role: "Federation query protocol", status: "Wikidata · DPRR(blocked)", col: C.teal },
          { x: 860, label: "OpenAlex / FAST\nLCNAF / VIAF", role: "Authority record IDs", status: "Partial — via Wikidata", col: C.amber },
        ].map(({ x, label, role, status, col }) => (
          <g key={label}>
            <Box x={x} y={816} w={200} h={52} fill={C.light} stroke={col} rx={4} />
            <Txt x={x + 100} y={830} s={10} fill={col} bold center>{label.split("\n")[0]}</Txt>
            {label.includes("\n") && <Txt x={x + 100} y={841} s={10} fill={col} bold center>{label.split("\n")[1]}</Txt>}
            <Txt x={x + 100} y={label.includes("\n") ? 853 : 843} s={8} fill={C.slate} center>{role}</Txt>
            <Txt x={x + 100} y={label.includes("\n") ? 864 : 854} s={7.5} fill={C.mid} center italic>{status}</Txt>
          </g>
        ))}

        {/* ── NEO4J COMPARISON ──────────────────────────────────────────────── */}
        <LayerHeader x={10} y={880} w={W - 20}
          label="CHRYSTALLUM vs. NATIVE NEO4J — Where the Architecture Diverges"
          fill={C.dark} />

        {/* left: native neo4j */}
        <Box x={15} y={898} w={520} h={200} fill="#F8F9FA" stroke={C.mid} rx={5} />
        <rect x={15} y={898} width={520} height={20} rx={4} fill={C.mid} />
        <Txt x={275} y={912} s={10} fill={C.white} bold center>Native Neo4j / Property Graph</Txt>

        {[
          ["Node labels", "Ontology defined in application code, not in graph"],
          ["Relationships", "Schema-free — any rel type between any node types"],
          ["Provenance", "Not native — requires custom properties or separate audit DB"],
          ["Confidence", "Not native — application-layer convention"],
          ["Schema", "Schema optional — graph.db.schema() advisory only"],
          ["Merges", "MERGE on arbitrary key — no canonical dedup mechanism"],
          ["Agent integration", "None native — custom integration required"],
          ["Temporal scoping", "Not native — application property convention"],
          ["Standards alignment", "None — pure property graph model"],
          ["Self-description", "Not native — no registry of node/rel types in graph"],
        ].map(([k, v], i) => (
          <g key={k}>
            <Txt x={22} y={924 + i * 17} s={9} fill={C.red} bold>{k}:</Txt>
            <Txt x={130} y={924 + i * 17} s={8.5} fill={C.dark}>{v}</Txt>
          </g>
        ))}

        {/* right: chrystallum */}
        <Box x={555} y={898} w={535} h={200} fill="#EAFAF1" stroke={C.teal} rx={5} />
        <rect x={555} y={898} width={535} height={20} rx={4} fill={C.teal} />
        <Txt x={822} y={912} s={10} fill={C.white} bold center>Chrystallum (on Neo4j)</Txt>

        {[
          ["Node labels", "Declared in SYS_NodeType registry within the graph itself"],
          ["Relationships", "All 113 types registered in SYS_RelationshipType with domain/range"],
          ["Provenance", "ADR-006: every ScaffoldEdge carries FROM/TO dprr_assertion_uri"],
          ["Confidence", "SYS_ConfidenceTier + per-claim confidence property (0–1)"],
          ["Schema", "SYS_ValidationRule + SYS_FacetRouter — schema is data"],
          ["Merges", "entity_cipher + edge_cipher — O(1) SHA-256 content-address"],
          ["Agent integration", "Three-layer: det. pre → LLM reason → det. execute"],
          ["Temporal scoping", "IN_PERIOD → :Periodo_Period · :HistoricalPolity → STARTS_IN_YEAR/ENDS_IN_YEAR → :Year"],
          ["Standards alignment", "CIDOC-CRM internal · GEDCOM 7.0 export target"],
          ["Self-description", "26-step onboarding protocol; graph explains itself to agents"],
        ].map(([k, v], i) => (
          <g key={k}>
            <Txt x={562} y={924 + i * 17} s={9} fill={C.teal} bold>{k}:</Txt>
            <Txt x={670} y={924 + i * 17} s={8.5} fill={C.dark}>{v}</Txt>
          </g>
        ))}

        {/* centre divider arrow */}
        <Txt x={540} y={1002} s={20} fill={C.mid} center>→</Txt>

        {/* ── METRICS BAR ───────────────────────────────────────────────────── */}
        <Box x={10} y={1108} w={W - 20} h={58} fill={C.navy} stroke={C.navy} rx={5} />
        {[
          ["~110k", "total nodes"],
          ["113", "rel types"],
          ["5,248", "Person nodes"],
          ["4,232", "Person ext ID nodes"],
          ["3,028", "Discipline ext IDs"],
          ["43,958", ":Place nodes"],
          ["675", ":Discipline nodes"],
          ["18", "Facets"],
          ["128", "FIELD_OF_WORK"],
        ].map(([n, l], i) => {
          const bx = 22 + i * 119;
          return (
            <g key={n}>
              <Txt x={bx} y={1129} s={14} fill={C.white} bold>{n}</Txt>
              <Txt x={bx} y={1142} s={8} fill="rgba(255,255,255,0.65)">{l}</Txt>
              {i < 8 && <line x1={bx + 110} y1={1112} x2={bx + 110} y2={1162}
                stroke="rgba(255,255,255,0.2)" strokeWidth={1} />}
            </g>
          );
        })}

        {/* ── FLOW ARROWS between layers ────────────────────────────────────── */}
        {/* Fed sources → L1 */}
        <Arrow x1={550} y1={83} x2={550} y2={100} stroke={C.blue} width={2} />
        {/* L1 → L2 */}
        <Arrow x1={550} y1={167} x2={550} y2={180} stroke={C.teal} width={2} />
        {/* L2 → L3 */}
        <Arrow x1={550} y1={302} x2={550} y2={310} stroke={C.slate} width={2} />
        {/* L3 → Graph */}
        <Arrow x1={550} y1={378} x2={550} y2={390} stroke={C.navy} width={2} />
        {/* Graph → Cipher */}
        <Arrow x1={550} y1={622} x2={550} y2={633} stroke={C.navy} width={2} />
        {/* Cipher → Query */}
        <Arrow x1={550} y1={688} x2={550} y2={698} stroke={C.slate} width={2} />

        {/* SYS layer ref arrow back into L1 */}
        <Line x1={185} y1={622} x2={185} y2={330} stroke={C.slate} dashed width={1.2} />
        <Txt x={188} y={490} s={7.5} fill={C.slate} italic>policies +</Txt>
        <Txt x={188} y={500} s={7.5} fill={C.slate} italic>thresholds</Txt>
        <polygon points="185,330 182,338 188,338" fill={C.slate} />

        {/* ── GLASS BEAD GAME footnote ─────────────────────────────────────── */}
        <Box x={10} y={1174} w={W - 20} h={36} fill="#FDFEFE" stroke={C.mid} rx={4} />
        <Txt x={W / 2} y={1189} s={9} fill={C.slate} center italic>
          &quot;An accessible implementation of Hermann Hesse&apos;s Glass Bead Game — cross-domain knowledge synthesis&quot;
        </Txt>
        <Txt x={W / 2} y={1202} s={9} fill={C.slate} center italic>
          from bookmark organisation (Level 1) to transcendent synthesis (Level 5)  ·  RAND systems analysis lineage
        </Txt>

      </svg>
    </div>
  );
}
