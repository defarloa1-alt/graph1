import { useState, useEffect, useMemo, useRef, useCallback } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — SYSTEM MAP (realtime from Neo4j)                           ║
// ║  Replaces: chrystallum_architecture.jsx + chrystallum_discipline_universe  ║
// ║  All data loaded via Cypher — zero hardcoded counts or node lists          ║
// ║  Tabs: Root Tree | Schema | Federation | Facets | Disciplines | Metrics   ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

// ── PALETTE ──────────────────────────────────────────────────────────────────
const C = {
  ink: "#0D1117", paper: "#F7F4EF", dim: "#8B8680", rule: "#D4CEC6",
  teal: "#1A7A6E", amber: "#B5860D", crimson: "#8B1A1A", navy: "#1A3A5C",
  green: "#1E6B3C", purple: "#5B2D8E", gold: "#C9A227", slate: "#4A5568",
  orange: "#B45309", rose: "#9B2335", cyan: "#0E7490", lime: "#3D6B21",
  bg2: "#EDEAE3",
};
const FACET_COLOR = {
  Political: C.navy, Military: C.crimson, Economic: C.amber, Social: C.teal,
  Cultural: C.purple, Biographic: C.rose, Diplomatic: C.cyan, Geographic: C.lime,
  Archaeological: C.orange, Religious: C.gold, Intellectual: C.navy,
  Linguistic: C.teal, Artistic: C.purple, Demographic: C.green,
  Environmental: C.lime, Communication: C.orange, Scientific: C.cyan,
  Technological: C.slate,
};
const STATUS_COL = {
  operational: C.green, partial: C.amber, planned: C.slate,
  blocked: C.crimson, spec_only: C.dim,
};

// ══════════════════════════════════════════════════════════════════════════════
// NEO4J DATA LAYER
// ══════════════════════════════════════════════════════════════════════════════
//
// fetchCypher(query, params) -> Promise<Record[]>
//
// Default: Neo4j HTTP Transaction API (works with Aura + self-hosted).
// Override NEO4J_URL / NEO4J_AUTH below, or replace fetchCypher entirely
// with your MCP bridge / Bolt wrapper / REST proxy.
//
// To use with MCP instead:
//   const fetchCypher = async (q, p) => await mcp.run_cypher_readonly({query:q, params:p});

const NEO4J_CONFIG = {
  // Aura or local — adjust to your instance
  url: import.meta.env?.VITE_NEO4J_URL || "neo4j+s://your-aura-instance.databases.neo4j.io",
  user: import.meta.env?.VITE_NEO4J_USER || "neo4j",
  password: import.meta.env?.VITE_NEO4J_PASSWORD || "",
};

// When set, use Railway MCP /api/cypher (no Neo4j creds needed). Otherwise use Neo4j HTTP proxy.
const CYPHER_API_URL = import.meta.env?.VITE_CYPHER_API_URL || null;

async function fetchCypher(query, params = {}) {
  if (CYPHER_API_URL) {
    const resp = await fetch(CYPHER_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, params }),
    });
    if (!resp.ok) {
      // Railway down or 404 — fall through to Neo4j proxy
      console.warn(`Railway API ${resp.status}, falling back to Neo4j proxy`);
    } else {
      const json = await resp.json();
      return json.rows || [];
    }
  }
  // Aura Query API v2 via Vite proxy (avoids CORS).
  const resp = await fetch("/neo4j-api/db/neo4j/query/v2", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Basic " + btoa(`${NEO4J_CONFIG.user}:${NEO4J_CONFIG.password}`),
    },
    body: JSON.stringify({ statement: query, parameters: params }),
  });
  if (!resp.ok) throw new Error(`Neo4j ${resp.status}: ${await resp.text()}`);
  const json = await resp.json();
  if (json.errors?.length) throw new Error(json.errors[0].message);
  const { fields, values } = json.data;
  return values.map((row) => {
    const obj = {};
    fields.forEach((col, i) => { obj[col] = row[i]; });
    return obj;
  });
}

// ── Query cache hook ────────────────────────────────────────────────────────
function useCypher(query, params = {}, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const key = JSON.stringify([query, params]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchCypher(query, params)
      .then((rows) => { if (!cancelled) { setData(rows); setLoading(false); } })
      .catch((err) => { if (!cancelled) { setError(err.message); setLoading(false); } });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, ...deps]);

  return { data, loading, error };
}

// ── Tiny UI primitives ──────────────────────────────────────────────────────
const Mono = ({ children, col = C.teal, s = 9 }) => (
  <code style={{ fontFamily: "'Courier New',monospace", color: col, fontSize: s,
    background: col + "12", padding: "1px 5px", borderRadius: 3 }}>{children}</code>
);
const Tag = ({ label, fill, s = 8 }) => (
  <span style={{ background: fill + "18", border: `1px solid ${fill}`, borderRadius: 10,
    padding: "1px 7px", fontSize: s, color: fill, fontWeight: "bold",
    display: "inline-block", margin: 1 }}>{label}</span>
);
const CopyBtn = ({ text }) => {
  const [ok, setOk] = useState(false);
  return (
    <button onClick={() => { navigator.clipboard?.writeText(text); setOk(true); setTimeout(() => setOk(false), 1400); }}
      style={{ background: ok ? C.green : C.slate, color: "white", border: "none",
        borderRadius: 3, padding: "1px 8px", fontSize: 8, cursor: "pointer", fontWeight: "bold" }}>
      {ok ? "copied" : "copy"}
    </button>
  );
};
const Loader = ({ msg = "Loading..." }) => (
  <div style={{ padding: 20, color: C.dim, fontSize: 11, fontStyle: "italic" }}>{msg}</div>
);
const Err = ({ msg }) => (
  <div style={{ padding: 12, color: C.crimson, fontSize: 10, background: C.crimson + "10",
    border: `1px solid ${C.crimson}`, borderRadius: 6 }}>Error: {msg}</div>
);
const CypherBlock = ({ query, label }) => (
  <div style={{ marginBottom: 10 }}>
    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
      <span style={{ fontSize: 8, color: C.dim, fontWeight: "bold" }}>{label || "CYPHER"}</span>
      <CopyBtn text={query} />
    </div>
    <pre style={{ fontFamily: "'Courier New',monospace", fontSize: 8.5, color: C.teal,
      background: C.teal + "08", borderRadius: 4, padding: 8, margin: 0,
      overflow: "auto", maxHeight: 180, whiteSpace: "pre-wrap" }}>{query}</pre>
  </div>
);

// ══════════════════════════════════════════════════════════════════════════════
// TAB 1: ROOT TREE — Chrystallum node outward
// ══════════════════════════════════════════════════════════════════════════════
const Q_ROOT_FANOUT = `MATCH (c:Chrystallum)-[r]->(t)
RETURN type(r) AS rel, labels(t) AS labels,
       coalesce(t.label, t.name, t.title, t.adr_id, t.table_id, t.threshold_id,
         t.policy_id, t.rule_id, t.layer_name, t.modifier_id, t.decision_key,
         t.pattern, t.facet_label, t.contract_id, t.pack_id, t.protocol_id, '') AS name,
       keys(t) AS props
ORDER BY type(r), name`;

const Q_SECOND_HOP = `MATCH (c:Chrystallum)-[r1]->(mid)-[r2]->(leaf)
WHERE type(r1) = $rel_type AND coalesce(mid.label, mid.name, '') = $mid_name
RETURN type(r2) AS rel, labels(leaf) AS labels,
       coalesce(leaf.label, leaf.name, leaf.source_id, '') AS name
ORDER BY type(r2), name
LIMIT 50`;

function RootTreeTab() {
  const { data, loading, error } = useCypher(Q_ROOT_FANOUT);
  const [expanded, setExpanded] = useState({});
  const [secondHop, setSecondHop] = useState({});

  const grouped = useMemo(() => {
    if (!data) return {};
    const g = {};
    data.forEach((row) => {
      if (!g[row.rel]) g[row.rel] = [];
      g[row.rel].push(row);
    });
    return g;
  }, [data]);

  const loadSecondHop = useCallback(async (relType, midName) => {
    const key = `${relType}::${midName}`;
    if (secondHop[key]) return;
    try {
      const rows = await fetchCypher(Q_SECOND_HOP, { rel_type: relType, mid_name: midName });
      setSecondHop((prev) => ({ ...prev, [key]: rows }));
    } catch (e) {
      setSecondHop((prev) => ({ ...prev, [key]: [{ rel: "ERROR", labels: [], name: e.message }] }));
    }
  }, [secondHop]);

  if (loading) return <Loader msg="Loading root tree from Neo4j..." />;
  if (error) return <Err msg={error} />;

  const totalEdges = data.length;
  const relTypes = Object.keys(grouped).length;

  return (
    <div>
      <div style={{ fontSize: 9, color: C.slate, marginBottom: 10, background: "white",
        border: `1px solid ${C.rule}`, borderRadius: 6, padding: "6px 10px" }}>
        <strong style={{ color: C.navy }}>(:Chrystallum:Root)</strong> fans out via{" "}
        <strong>{relTypes}</strong> edge types to <strong>{totalEdges}</strong> targets.
        Click any node to load its children (second hop).
      </div>

      <CypherBlock query={Q_ROOT_FANOUT} label="ROOT FANOUT QUERY" />

      {Object.entries(grouped).map(([rel, rows]) => {
        const isOpen = expanded[rel] !== false; // default open
        return (
          <div key={rel} style={{ border: `1px solid ${C.rule}`, borderRadius: 5,
            marginBottom: 4, borderLeft: `3px solid ${C.navy}` }}>
            <div onClick={() => setExpanded((p) => ({ ...p, [rel]: !isOpen }))}
              style={{ padding: "5px 10px", cursor: "pointer", background: "white",
                display: "flex", gap: 8, alignItems: "center" }}>
              <Mono col={C.navy}>{rel}</Mono>
              <span style={{ fontSize: 9, color: C.dim }}>({rows.length})</span>
              <span style={{ marginLeft: "auto", color: C.dim, fontSize: 9 }}>{isOpen ? "v" : ">"}</span>
            </div>
            {isOpen && (
              <div style={{ borderTop: `1px solid ${C.rule}`, background: "#FAFAF8", padding: "4px 10px" }}>
                {rows.map((row, i) => {
                  const hopKey = `${rel}::${row.name}`;
                  const children = secondHop[hopKey];
                  return (
                    <div key={i} style={{ marginBottom: 3 }}>
                      <div style={{ display: "flex", gap: 6, alignItems: "center", cursor: "pointer" }}
                        onClick={() => { loadSecondHop(rel, row.name); }}>
                        <span style={{ fontSize: 8, color: C.purple }}>
                          {row.labels.map((l) => `:${l}`).join("")}
                        </span>
                        <span style={{ fontSize: 9, color: C.ink, fontWeight: "bold" }}>{row.name || "(unnamed)"}</span>
                        <span style={{ fontSize: 7.5, color: C.dim }}>
                          [{row.props?.length || 0} props]
                        </span>
                        {children && <span style={{ fontSize: 7.5, color: C.teal }}>
                          {children.length} children loaded
                        </span>}
                      </div>
                      {children && children.length > 0 && (
                        <div style={{ marginLeft: 20, borderLeft: `1px dashed ${C.rule}`, paddingLeft: 8, marginTop: 2 }}>
                          {children.map((ch, j) => (
                            <div key={j} style={{ fontSize: 8, color: C.slate, marginBottom: 1 }}>
                              <Mono col={C.teal} s={7.5}>{ch.rel}</Mono>{" "}
                              <span style={{ color: C.purple }}>{ch.labels.map((l) => `:${l}`).join("")}</span>{" "}
                              <span style={{ color: C.ink }}>{ch.name}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 2: SCHEMA — SYS_NodeType + SYS_EdgeType + gap detection
// ══════════════════════════════════════════════════════════════════════════════
const Q_NODE_TYPES = `MATCH (nt:SYS_NodeType)
RETURN nt.name AS name, nt.description AS desc
ORDER BY name`;

const Q_ACTUAL_LABELS = `MATCH (n)
RETURN DISTINCT labels(n) AS labels, count(*) AS cnt
ORDER BY cnt DESC`;

const Q_REL_TYPE_REGISTRY = `MATCH (rt:SYS_RelationshipType)
RETURN rt.rel_type AS rel_type, rt.name AS name, rt.domain AS domain, rt.range AS range_
ORDER BY rt.rel_type`;

const Q_ACTUAL_RELS = `MATCH ()-[r]->()
WITH DISTINCT type(r) AS rel_type, count(*) AS cnt
RETURN rel_type, cnt ORDER BY cnt DESC`;

function SchemaTab() {
  const nodeTypes = useCypher(Q_NODE_TYPES);
  const actualLabels = useCypher(Q_ACTUAL_LABELS);
  const relRegistry = useCypher(Q_REL_TYPE_REGISTRY);
  const actualRels = useCypher(Q_ACTUAL_RELS);
  const [view, setView] = useState("nodes"); // nodes | rels | gaps

  const loading = nodeTypes.loading || actualLabels.loading || relRegistry.loading || actualRels.loading;
  const err = nodeTypes.error || actualLabels.error || relRegistry.error || actualRels.error;
  if (loading) return <Loader msg="Loading schema from Neo4j..." />;
  if (err) return <Err msg={err} />;

  // Flatten actual labels to a set of unique label strings
  const actualLabelSet = new Set();
  const labelCounts = {};
  actualLabels.data.forEach((row) => {
    row.labels.forEach((l) => {
      actualLabelSet.add(l);
      labelCounts[l] = (labelCounts[l] || 0) + row.cnt;
    });
  });

  const registeredNames = new Set(nodeTypes.data.map((r) => r.name));
  const unregisteredLabels = [...actualLabelSet].filter((l) => !registeredNames.has(l)).sort();

  const registeredRels = new Set(relRegistry.data.map((r) => r.rel_type));
  const actualRelSet = new Set(actualRels.data.map((r) => r.rel_type));
  const unregisteredRels = actualRels.data.filter((r) => !registeredRels.has(r.rel_type));

  return (
    <div>
      <div style={{ display: "flex", gap: 0, marginBottom: 12, borderBottom: `1.5px solid ${C.rule}` }}>
        {[["nodes", `Node Types (${nodeTypes.data.length} registered)`],
          ["rels", `Rel Types (${relRegistry.data.length} registered)`],
          ["gaps", `Gaps (${unregisteredLabels.length} labels + ${unregisteredRels.length} rels)`],
        ].map(([k, l]) => (
          <button key={k} onClick={() => setView(k)}
            style={{ border: "none", padding: "5px 14px", fontSize: 9.5, cursor: "pointer",
              background: "transparent", fontWeight: view === k ? "bold" : "normal",
              color: view === k ? C.navy : C.dim,
              borderBottom: view === k ? `2px solid ${C.navy}` : "2px solid transparent" }}>
            {l}
          </button>
        ))}
      </div>

      {view === "nodes" && (
        <div>
          <CypherBlock query={Q_NODE_TYPES} label="REGISTERED NODE TYPES" />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 4 }}>
            {nodeTypes.data.map((nt) => (
              <div key={nt.name} style={{ border: `1px solid ${C.rule}`, borderRadius: 4,
                padding: "4px 8px", borderLeft: `3px solid ${actualLabelSet.has(nt.name) ? C.green : C.amber}` }}>
                <div style={{ display: "flex", gap: 4, alignItems: "baseline" }}>
                  <Mono col={C.navy} s={8.5}>:{nt.name}</Mono>
                  <span style={{ fontSize: 8, color: C.dim, marginLeft: "auto" }}>
                    {labelCounts[nt.name] ? `${labelCounts[nt.name].toLocaleString()}` : "0"}
                  </span>
                </div>
                {nt.desc && <div style={{ fontSize: 7.5, color: C.slate, marginTop: 2 }}>{nt.desc}</div>}
              </div>
            ))}
          </div>
        </div>
      )}

      {view === "rels" && (
        <div>
          <CypherBlock query={Q_REL_TYPE_REGISTRY} label="REGISTERED RELATIONSHIP TYPES" />
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 6 }}>
            {relRegistry.data.length} registered | {actualRelSet.size} actual in graph
          </div>
          <div style={{ maxHeight: 400, overflow: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 8.5 }}>
              <thead>
                <tr style={{ background: C.navy, color: "white" }}>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>rel_type</th>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>domain</th>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>range</th>
                  <th style={{ padding: "3px 6px", textAlign: "right" }}>in graph</th>
                </tr>
              </thead>
              <tbody>
                {relRegistry.data.map((rt) => {
                  const actual = actualRels.data.find((a) => a.rel_type === rt.rel_type);
                  return (
                    <tr key={rt.rel_type} style={{ borderBottom: `1px solid ${C.rule}`,
                      background: actual ? "white" : C.amber + "10" }}>
                      <td style={{ padding: "2px 6px", fontFamily: "monospace", color: C.teal }}>{rt.rel_type}</td>
                      <td style={{ padding: "2px 6px", color: C.slate }}>{rt.domain || "-"}</td>
                      <td style={{ padding: "2px 6px", color: C.slate }}>{rt.range_ || "-"}</td>
                      <td style={{ padding: "2px 6px", textAlign: "right", color: actual ? C.green : C.amber }}>
                        {actual ? actual.cnt.toLocaleString() : "0"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {view === "gaps" && (
        <div>
          <div style={{ fontWeight: "bold", fontSize: 11, color: C.crimson, marginBottom: 8 }}>
            Labels in graph but NOT in SYS_NodeType ({unregisteredLabels.length})
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 3, marginBottom: 16 }}>
            {unregisteredLabels.map((l) => (
              <Tag key={l} label={`${l} (${(labelCounts[l] || 0).toLocaleString()})`}
                fill={l.startsWith("SYS_") ? C.amber : C.crimson} s={7.5} />
            ))}
          </div>

          <div style={{ fontWeight: "bold", fontSize: 11, color: C.amber, marginBottom: 8 }}>
            Rel types in graph but NOT in SYS_RelationshipType ({unregisteredRels.length})
          </div>
          <div style={{ maxHeight: 300, overflow: "auto" }}>
            {unregisteredRels.map((r) => (
              <div key={r.rel_type} style={{ display: "flex", gap: 8, alignItems: "baseline",
                marginBottom: 2, fontSize: 8.5 }}>
                <Mono col={C.amber} s={8}>{r.rel_type}</Mono>
                <span style={{ color: C.dim }}>{r.cnt.toLocaleString()} edges</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 3: FEDERATION — SYS_FederationSource from registry
// ══════════════════════════════════════════════════════════════════════════════
const Q_FEDERATION = `MATCH (fr:SYS_FederationRegistry)-[:CONTAINS]->(fs:SYS_FederationSource)
RETURN fs.source_id AS sid, fs.label AS label, fs.status AS status,
       fs.scoping_weight AS weight, fs.endpoint AS endpoint,
       fs.phase AS phase, fs.scoping_role AS role,
       keys(fs) AS props
ORDER BY fs.scoping_weight DESC, fs.label`;

function FederationTab() {
  const { data, loading, error } = useCypher(Q_FEDERATION);
  const [open, setOpen] = useState(null);
  const [filter, setFilter] = useState("ALL");

  if (loading) return <Loader msg="Loading federation sources from Neo4j..." />;
  if (error) return <Err msg={error} />;

  const statuses = [...new Set(data.map((d) => d.status).filter(Boolean))];
  const shown = filter === "ALL" ? data : data.filter((d) => d.status === filter);

  return (
    <div>
      <CypherBlock query={Q_FEDERATION} label="FEDERATION SOURCES QUERY" />

      <div style={{ display: "flex", gap: 6, marginBottom: 10, flexWrap: "wrap" }}>
        {["ALL", ...statuses].map((s) => {
          const col = s === "ALL" ? C.navy : (STATUS_COL[s] || C.dim);
          const cnt = s === "ALL" ? data.length : data.filter((d) => d.status === s).length;
          return (
            <button key={s} onClick={() => setFilter(s)}
              style={{ border: `1.5px solid ${col}`, background: filter === s ? col : "white",
                color: filter === s ? "white" : col, borderRadius: 12,
                padding: "2px 10px", fontSize: 9, cursor: "pointer", fontWeight: "bold" }}>
              {s} ({cnt})
            </button>
          );
        })}
      </div>

      {shown.map((src) => {
        const col = STATUS_COL[src.status] || C.dim;
        return (
          <div key={src.sid} style={{ border: `1.5px solid ${col}33`, borderLeft: `4px solid ${col}`,
            borderRadius: 5, marginBottom: 4 }}>
            <div onClick={() => setOpen(open === src.sid ? null : src.sid)}
              style={{ padding: "5px 10px", cursor: "pointer", background: "white",
                display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <Tag label={src.status || "unknown"} fill={col} />
              <span style={{ fontWeight: "bold", fontSize: 11, color: C.ink, minWidth: 100 }}>{src.label}</span>
              <Mono col={C.slate} s={8}>{src.sid}</Mono>
              {src.weight && <Mono col={C.amber} s={8}>w={src.weight}</Mono>}
              {src.role && <span style={{ fontSize: 8.5, color: C.dim }}>{src.role}</span>}
              {src.phase && <Tag label={`phase ${src.phase}`} fill={C.purple} s={7} />}
              <span style={{ marginLeft: "auto", color: C.dim, fontSize: 9 }}>{open === src.sid ? "v" : ">"}</span>
            </div>
            {open === src.sid && (
              <div style={{ padding: "6px 10px", background: "#FAFAF8", borderTop: `1px solid ${C.rule}`,
                fontSize: 8.5, color: C.slate }}>
                {src.endpoint && <div><strong>Endpoint:</strong> <Mono col={C.teal} s={8}>{src.endpoint}</Mono></div>}
                <div style={{ marginTop: 4 }}><strong>Properties:</strong> {src.props?.join(", ")}</div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 4: FACETS — from FacetRoot
// ══════════════════════════════════════════════════════════════════════════════
const Q_FACETS = `MATCH (f:Facet)
OPTIONAL MATCH (f)<-[:HAS_PRIMARY_FACET]-(sc:SubjectConcept)
WITH f, count(sc) AS primary_concepts
OPTIONAL MATCH (f)<-[:RELEVANT_TO_FACET]-(cw:CorpusWork)
WITH f, primary_concepts, count(cw) AS corpus_works
OPTIONAL MATCH (f)<-[hf:HAS_FACET]-(d:Discipline) WHERE hf.primary = true
RETURN f.label AS label, f.description AS desc,
       primary_concepts, corpus_works, count(d) AS discipline_count,
       keys(f) AS props
ORDER BY f.label`;

const Q_FACET_DETAIL = `MATCH (f:Facet {label: $facet})
OPTIONAL MATCH (f)<-[:HAS_PRIMARY_FACET]-(router:SYS_FacetRouter)
RETURN router.label AS prop_label, router.pid AS pid, router.rule_type AS auth
ORDER BY router.label LIMIT 30`;

const Q_FACET_SC = `MATCH (f:Facet {label: $facet})<-[:HAS_PRIMARY_FACET]-(sc:SubjectConcept)
RETURN sc.label AS label, sc.entity_count AS entity_count, sc.split_candidate AS split
ORDER BY sc.label`;

const Q_FACET_SC_SECONDARY = `MATCH (f:Facet {label: $facet})<-[:HAS_SECONDARY_FACET]-(sc:SubjectConcept)
RETURN sc.label AS label ORDER BY sc.label`;

const Q_FACET_CORPUS = `MATCH (f:Facet {label: $facet})<-[:RELEVANT_TO_FACET]-(cw:CorpusWork)
RETURN cw.title AS title, cw.year AS year, cw.abstract IS NOT NULL AS has_abstract
ORDER BY cw.title LIMIT 50`;

const Q_FACET_OA = `MATCH (oa:SYS_OASourcePack)
WHERE oa.pack_id CONTAINS toUpper($facet) OR oa.label CONTAINS $facet
RETURN oa.pack_id AS id, oa.label AS label, oa.scope_note AS scope,
       oa.priority_texts AS texts, oa.sources AS sources`;

const Q_FACET_AGENT = `MATCH (a:Agent)
WHERE a.scope CONTAINS $facet OR a.name CONTAINS toUpper($facet)
RETURN a.name AS name, a.status AS status, a.scope AS scope`;

function FacetTab() {
  const { data, loading, error } = useCypher(Q_FACETS);
  const [selected, setSelected] = useState(null);
  const [detailView, setDetailView] = useState("mappings");

  const noop = "MATCH (n) RETURN null AS x LIMIT 0";
  const params = selected ? { facet: selected } : {};
  const deps = [selected];

  const detail = useCypher(selected ? Q_FACET_DETAIL : noop, params, deps);
  const scs = useCypher(selected ? Q_FACET_SC : noop, params, deps);
  const scsSecondary = useCypher(selected ? Q_FACET_SC_SECONDARY : noop, params, deps);
  const corpus = useCypher(selected ? Q_FACET_CORPUS : noop, params, deps);
  const oaPack = useCypher(selected ? Q_FACET_OA : noop, params, deps);
  const agent = useCypher(selected ? Q_FACET_AGENT : noop, params, deps);

  if (loading) return <Loader msg="Loading facets from Neo4j..." />;
  if (error) return <Err msg={error} />;

  const col = FACET_COLOR[selected] || C.slate;

  return (
    <div>
      <CypherBlock query={Q_FACETS} label="FACET QUERY" />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 6, marginBottom: 12 }}>
        {data.map((f) => {
          const fc = FACET_COLOR[f.label] || C.slate;
          const isSelected = selected === f.label;
          return (
            <div key={f.label} onClick={() => { setSelected(isSelected ? null : f.label); setDetailView("mappings"); }}
              style={{ border: `1.5px solid ${fc}`, borderRadius: 6, padding: "8px 10px",
                cursor: "pointer", background: isSelected ? fc + "15" : "white" }}>
              <div style={{ fontWeight: "bold", fontSize: 11, color: fc }}>{f.label}</div>
              {f.desc && <div style={{ fontSize: 8, color: C.slate, marginTop: 2 }}>{f.desc}</div>}
              <div style={{ display: "flex", gap: 8, marginTop: 4, fontSize: 8, color: C.dim }}>
                <span>{f.discipline_count} disciplines</span>
                <span>{f.primary_concepts} concepts</span>
                <span>{f.corpus_works} corpus</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Facet drill-down ── */}
      {selected && (
        <div style={{ border: `1.5px solid ${col}`, borderRadius: 6, overflow: "hidden", marginTop: 4 }}>
          <div style={{ background: col, padding: "6px 12px", display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ fontSize: 12, fontWeight: "bold", color: "white" }}>{selected}</span>
            {agent.data?.[0] && (
              <Tag label={`${agent.data[0].name} (${agent.data[0].status})`}
                fill="rgba(255,255,255,0.3)" s={7} />
            )}
          </div>

          {/* Sub-tabs */}
          <div style={{ display: "flex", gap: 0, borderBottom: `1px solid ${C.rule}`, background: "white" }}>
            {[
              ["mappings", `Routers (${detail.data?.length || 0})`],
              ["concepts", `SubjectConcepts (${(scs.data?.length || 0) + (scsSecondary.data?.length || 0)})`],
              ["corpus", `Corpus (${corpus.data?.length || 0})`],
              ["oa", `OA Packs (${oaPack.data?.length || 0})`],
            ].map(([k, l]) => (
              <button key={k} onClick={() => setDetailView(k)}
                style={{ border: "none", padding: "4px 12px", fontSize: 8.5, cursor: "pointer",
                  background: "transparent", fontWeight: detailView === k ? "bold" : "normal",
                  color: detailView === k ? col : C.dim,
                  borderBottom: detailView === k ? `2px solid ${col}` : "2px solid transparent" }}>
                {l}
              </button>
            ))}
          </div>

          <div style={{ padding: "8px 12px", background: "white" }}>
            {/* FacetRouter rules */}
            {detailView === "mappings" && detail.data && (
              <div>
                {detail.data.length === 0
                  ? <div style={{ fontSize: 9, color: C.dim, fontStyle: "italic" }}>No facet router rules</div>
                  : detail.data.map((r, i) => (
                    <div key={i} style={{ display: "flex", gap: 8, fontSize: 8.5, marginBottom: 2 }}>
                      <Mono col={C.purple} s={8}>{r.pid}</Mono>
                      <span style={{ color: C.ink }}>{r.prop_label}</span>
                      {r.auth && <Tag label={r.auth} fill={C.green} s={7} />}
                    </div>
                  ))}
              </div>
            )}

            {/* SubjectConcepts */}
            {detailView === "concepts" && (
              <div>
                {scs.data?.length > 0 && (
                  <div style={{ marginBottom: 8 }}>
                    <div style={{ fontSize: 9, fontWeight: "bold", color: col, marginBottom: 4 }}>Primary</div>
                    {scs.data.map((sc) => (
                      <div key={sc.label} style={{ display: "flex", gap: 8, fontSize: 9, marginBottom: 3,
                        padding: "3px 8px", border: `1px solid ${C.rule}`, borderRadius: 4,
                        borderLeft: `3px solid ${col}` }}>
                        <span style={{ fontWeight: "bold", color: C.ink }}>{sc.label}</span>
                        {sc.entity_count != null && <Mono col={C.dim} s={7.5}>{sc.entity_count} entities</Mono>}
                        {sc.split && <Tag label="split candidate" fill={C.amber} s={7} />}
                      </div>
                    ))}
                  </div>
                )}
                {scsSecondary.data?.length > 0 && (
                  <div>
                    <div style={{ fontSize: 9, fontWeight: "bold", color: C.dim, marginBottom: 4 }}>Secondary</div>
                    {scsSecondary.data.map((sc) => (
                      <div key={sc.label} style={{ fontSize: 8.5, color: C.slate, marginBottom: 2,
                        paddingLeft: 8, borderLeft: `2px dashed ${C.rule}` }}>
                        {sc.label}
                      </div>
                    ))}
                  </div>
                )}
                {(!scs.data?.length && !scsSecondary.data?.length) && (
                  <div style={{ fontSize: 9, color: C.dim, fontStyle: "italic" }}>No SubjectConcepts linked to this facet</div>
                )}
              </div>
            )}

            {/* Corpus */}
            {detailView === "corpus" && (
              <div>
                {corpus.data?.length > 0 ? (
                  <div style={{ maxHeight: 300, overflow: "auto" }}>
                    {corpus.data.map((cw, i) => (
                      <div key={i} style={{ display: "flex", gap: 6, fontSize: 8.5, marginBottom: 2,
                        alignItems: "center" }}>
                        <span style={{ width: 14, fontSize: 7, color: cw.has_abstract ? C.green : C.amber }}>
                          {cw.has_abstract ? "\u2713" : "\u2717"}
                        </span>
                        <span style={{ color: C.ink }}>{cw.title}</span>
                        {cw.year && <Mono col={C.dim} s={7}>{cw.year}</Mono>}
                      </div>
                    ))}
                    <div style={{ fontSize: 8, color: C.dim, marginTop: 6 }}>
                      {"\u2713"} = has abstract | {"\u2717"} = abstract missing (training data gap)
                    </div>
                  </div>
                ) : (
                  <div style={{ fontSize: 9, color: C.dim, fontStyle: "italic" }}>No CorpusWork linked to this facet</div>
                )}
              </div>
            )}

            {/* OA Packs */}
            {detailView === "oa" && (
              <div>
                {oaPack.data?.length > 0 ? oaPack.data.map((oa) => (
                  <div key={oa.id} style={{ border: `1px solid ${col}`, borderRadius: 5, padding: 8, marginBottom: 6 }}>
                    <div style={{ fontWeight: "bold", fontSize: 10, color: col }}>{oa.label}</div>
                    <Mono col={C.dim} s={7.5}>{oa.id}</Mono>
                    {oa.scope && <div style={{ fontSize: 8.5, color: C.slate, marginTop: 4 }}><strong>Scope:</strong> {oa.scope}</div>}
                    {oa.texts && <div style={{ fontSize: 8.5, color: C.slate, marginTop: 2 }}><strong>Priority texts:</strong> {oa.texts}</div>}
                    {oa.sources && <div style={{ fontSize: 8.5, color: C.slate, marginTop: 2 }}><strong>Sources:</strong> {oa.sources}</div>}
                  </div>
                )) : (
                  <div style={{ fontSize: 9, color: C.dim, fontStyle: "italic" }}>No OA Source Pack for this facet</div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 5: DECISION TABLES — from Chrystallum root
// ══════════════════════════════════════════════════════════════════════════════
const Q_DECISION_TABLES = `MATCH (c:Chrystallum)-[:HAS_DECISION_TABLE]->(dt:SYS_DecisionTable)
OPTIONAL MATCH (dt)-[:HAS_ROW]->(dr:SYS_DecisionRow)
RETURN dt.table_id AS table_id, dt.label AS label, dt.description AS desc,
       count(dr) AS row_count
ORDER BY dt.table_id`;

const Q_DECISION_ROWS = `MATCH (dt:SYS_DecisionTable {table_id: $tid})-[:HAS_ROW]->(dr:SYS_DecisionRow)
RETURN dr ORDER BY dr.row_id LIMIT 50`;

function DecisionTableTab() {
  const { data, loading, error } = useCypher(Q_DECISION_TABLES);
  const [openTable, setOpenTable] = useState(null);
  const [rows, setRows] = useState({});

  const loadRows = useCallback(async (tid) => {
    if (rows[tid]) return;
    try {
      const r = await fetchCypher(
        `MATCH (dt:SYS_DecisionTable {table_id: $tid})-[:HAS_ROW]->(dr:SYS_DecisionRow)
         RETURN properties(dr) AS props ORDER BY dr.priority, dr.row_id LIMIT 50`,
        { tid }
      );
      setRows((prev) => ({ ...prev, [tid]: r }));
    } catch (e) {
      setRows((prev) => ({ ...prev, [tid]: [{ props: { error: e.message } }] }));
    }
  }, [rows]);

  // Also fetch table-level metadata (inputs, outputs, hit_policy, conditions, actions, depends_on)
  const [meta, setMeta] = useState({});
  const loadMeta = useCallback(async (tid) => {
    if (meta[tid]) return;
    try {
      const r = await fetchCypher(
        `MATCH (dt:SYS_DecisionTable {table_id: $tid})
         OPTIONAL MATCH (dt)-[:FEEDS_INTO]->(dep:SYS_DecisionTable)
         RETURN dt.hit_policy AS hit_policy, dt.inputs AS inputs, dt.outputs AS outputs,
                dt.conditions AS conditions, dt.actions AS actions, dt.status AS status,
                dt.depends_on AS depends_on, dt.consumers AS consumers,
                collect(dep.table_id) AS feeds_into`,
        { tid }
      );
      setMeta((prev) => ({ ...prev, [tid]: r[0] || {} }));
    } catch (e) {
      setMeta((prev) => ({ ...prev, [tid]: {} }));
    }
  }, [meta]);

  if (loading) return <Loader msg="Loading decision tables..." />;
  if (error) return <Err msg={error} />;

  // Detect table type from row properties
  const isScoring = (rws) => rws?.some((r) => r.props?.score_points != null || r.props?.dimension);
  const hasScoreRange = (rws) => rws?.some((r) => r.props?.score_min != null);

  // Parse conditions — could be JSON string or plain string
  const parseConds = (raw) => {
    if (!raw) return null;
    if (typeof raw === "object") return raw;
    try { return JSON.parse(raw); } catch { return raw; }
  };

  // Render conditions as readable badges
  const CondCell = ({ raw }) => {
    const parsed = parseConds(raw);
    if (!parsed) return <span style={{ color: C.dim, fontStyle: "italic" }}>—</span>;
    if (typeof parsed === "string") return <span style={{ fontFamily: "monospace", fontSize: 8, color: C.navy }}>{parsed}</span>;
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
        {Object.entries(parsed).map(([k, v]) => (
          <div key={k} style={{ fontSize: 7.5 }}>
            <span style={{ color: C.dim }}>{k}</span>{" "}
            <span style={{ color: C.navy, fontFamily: "monospace" }}>{String(v)}</span>
          </div>
        ))}
      </div>
    );
  };

  // Action color coding
  const actionColor = (act) => {
    if (!act) return C.dim;
    if (act.includes("reject") || act.includes("keep_separate")) return C.crimson;
    if (act.includes("promote") || act.includes("merge") || act.includes("accept") || act.includes("assign")) return C.green;
    if (act.includes("flag") || act.includes("alert")) return C.amber;
    if (act.includes("add_score") || act.includes("set_flag")) return C.teal;
    if (act.includes("create_edge")) return C.purple;
    return C.navy;
  };

  const thStyle = { padding: "4px 8px", textAlign: "left", fontSize: 8, color: C.dim,
    fontWeight: "bold", borderBottom: `2px solid ${C.rule}`, whiteSpace: "nowrap",
    fontFamily: "Arial,sans-serif", textTransform: "uppercase", letterSpacing: 0.5 };
  const tdStyle = { padding: "4px 8px", fontSize: 8.5, borderBottom: `1px solid ${C.rule}`,
    verticalAlign: "top" };

  return (
    <div>
      <CypherBlock query={Q_DECISION_TABLES} label="DECISION TABLES QUERY" />

      <div style={{ display: "flex", gap: 8, marginBottom: 10, alignItems: "center", flexWrap: "wrap" }}>
        <span style={{ fontSize: 10, fontWeight: "bold", color: C.ink }}>{data.length} Decision Tables</span>
        <span style={{ fontSize: 8.5, color: C.dim }}>Click to expand rules. All data live from graph.</span>
      </div>

      {data.map((dt) => {
        const isOpen = openTable === dt.table_id;
        const tid = dt.table_id;
        const shortId = tid.split("_")[0]; // e.g. "D10"
        const rws = rows[tid];
        const m = meta[tid] || {};

        // Detect table category for color-coding
        const isScoringTable = tid.includes("SCORE");
        const isNormalize = tid.includes("NORMALIZE");
        const isDetermine = tid.includes("DETERMINE");
        const barColor = isScoringTable ? C.amber : isNormalize ? C.purple : C.teal;

        return (
          <div key={tid} style={{ border: `1px solid ${C.rule}`, borderRadius: 5,
            marginBottom: 5, borderLeft: `4px solid ${barColor}`, background: "white" }}>
            {/* Header */}
            <div onClick={() => { setOpenTable(isOpen ? null : tid); loadRows(tid); loadMeta(tid); }}
              style={{ padding: "6px 12px", cursor: "pointer",
                display: "flex", gap: 8, alignItems: "center" }}>
              <span style={{ background: barColor, color: "white", fontSize: 9, fontWeight: "bold",
                padding: "2px 8px", borderRadius: 3, fontFamily: "monospace" }}>{shortId}</span>
              <span style={{ fontWeight: "bold", fontSize: 10.5, color: C.ink }}>{dt.label}</span>
              <span style={{ fontSize: 8, color: C.dim, marginLeft: "auto" }}>
                {dt.row_count} rule{dt.row_count !== 1 ? "s" : ""}
              </span>
              <span style={{ color: C.dim, fontSize: 10, fontFamily: "monospace" }}>{isOpen ? "\u25BC" : "\u25B6"}</span>
            </div>

            {/* Expanded detail */}
            {isOpen && (
              <div style={{ borderTop: `1px solid ${C.rule}`, background: "#FAFAF8" }}>
                {/* Description + metadata bar */}
                <div style={{ padding: "8px 12px", borderBottom: `1px solid ${C.rule}` }}>
                  {dt.desc && <div style={{ fontSize: 9, color: C.slate, marginBottom: 6 }}>{dt.desc}</div>}
                  <div style={{ display: "flex", gap: 10, flexWrap: "wrap", fontSize: 8, color: C.dim }}>
                    {m.hit_policy && <span><b style={{ color: C.ink }}>Hit policy:</b> {m.hit_policy}</span>}
                    {m.status && <span><b style={{ color: C.ink }}>Status:</b> {m.status}</span>}
                    {m.inputs && <span><b style={{ color: C.ink }}>Inputs:</b> {m.inputs.join(", ")}</span>}
                    {m.outputs && <span><b style={{ color: C.ink }}>Outputs:</b> {m.outputs.join(", ")}</span>}
                    {m.conditions && <span><b style={{ color: C.ink }}>Conditions:</b> {m.conditions.join(", ")}</span>}
                    {m.actions && <span><b style={{ color: C.ink }}>Actions:</b> {m.actions.join(", ")}</span>}
                    {m.consumers && <span><b style={{ color: C.ink }}>Consumers:</b> {m.consumers.join(", ")}</span>}
                    {m.feeds_into?.length > 0 && (
                      <span><b style={{ color: C.ink }}>Feeds into:</b> {m.feeds_into.join(", ")}</span>
                    )}
                  </div>
                </div>

                {/* Rules table */}
                {rws ? (
                  <div style={{ overflow: "auto", maxHeight: 400 }}>
                    {rws.length === 0 ? (
                      <div style={{ padding: 12, fontSize: 9, color: C.dim, fontStyle: "italic" }}>
                        No rules attached to this table yet.
                      </div>
                    ) : isScoring(rws) && !hasScoreRange(rws) ? (
                      /* ── Scoring rubric table (D16, D17, D18, D20) ── */
                      <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                          <tr style={{ background: C.bg2 }}>
                            <th style={thStyle}>#</th>
                            <th style={thStyle}>Condition</th>
                            <th style={thStyle}>Dimension</th>
                            <th style={thStyle}>Points</th>
                            <th style={thStyle}>Action</th>
                            <th style={thStyle}>Detail</th>
                          </tr>
                        </thead>
                        <tbody>
                          {rws.map((r, i) => {
                            const p = r.props;
                            return (
                              <tr key={i} style={{ background: i % 2 === 0 ? "white" : "#FCFBF9" }}>
                                <td style={{ ...tdStyle, fontFamily: "monospace", color: C.dim, width: 30 }}>{p.priority || i + 1}</td>
                                <td style={tdStyle}><CondCell raw={p.conditions} /></td>
                                <td style={tdStyle}>
                                  {p.dimension && <Tag label={p.dimension} fill={C.navy} s={7} />}
                                </td>
                                <td style={{ ...tdStyle, fontFamily: "monospace", fontWeight: "bold",
                                  color: C.teal, textAlign: "center", width: 50 }}>
                                  {p.score_points != null ? `+${p.score_points}` : "—"}
                                </td>
                                <td style={tdStyle}>
                                  <span style={{ color: actionColor(p.action), fontWeight: "bold", fontSize: 8 }}>{p.action || "—"}</span>
                                </td>
                                <td style={{ ...tdStyle, fontSize: 8, color: C.slate, maxWidth: 200 }}>{p.action_detail || "—"}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    ) : hasScoreRange(rws) ? (
                      /* ── Score-range table (D15) ── */
                      <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                          <tr style={{ background: C.bg2 }}>
                            <th style={thStyle}>#</th>
                            <th style={thStyle}>Score Range</th>
                            <th style={thStyle}>Condition</th>
                            <th style={thStyle}>Action</th>
                            <th style={thStyle}>State Assigned</th>
                          </tr>
                        </thead>
                        <tbody>
                          {rws.map((r, i) => {
                            const p = r.props;
                            return (
                              <tr key={i} style={{ background: i % 2 === 0 ? "white" : "#FCFBF9" }}>
                                <td style={{ ...tdStyle, fontFamily: "monospace", color: C.dim, width: 30 }}>{p.priority || i + 1}</td>
                                <td style={{ ...tdStyle, fontFamily: "monospace", fontWeight: "bold", color: C.teal }}>
                                  {p.score_min != null ? `${p.score_min}–${p.score_max}` : "—"}
                                </td>
                                <td style={tdStyle}><CondCell raw={p.conditions} /></td>
                                <td style={tdStyle}>
                                  <span style={{ color: actionColor(p.action), fontWeight: "bold", fontSize: 8 }}>{p.action || "—"}</span>
                                </td>
                                <td style={tdStyle}>
                                  <Mono col={C.green} s={8}>{p.action_detail || "—"}</Mono>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    ) : (
                      /* ── Standard condition→action table (D1-D14, D19) ── */
                      <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                          <tr style={{ background: C.bg2 }}>
                            <th style={thStyle}>#</th>
                            <th style={{ ...thStyle, minWidth: 160 }}>Conditions</th>
                            <th style={thStyle}>Action</th>
                            <th style={{ ...thStyle, minWidth: 180 }}>Detail</th>
                          </tr>
                        </thead>
                        <tbody>
                          {rws.map((r, i) => {
                            const p = r.props;
                            return (
                              <tr key={i} style={{ background: i % 2 === 0 ? "white" : "#FCFBF9" }}>
                                <td style={{ ...tdStyle, fontFamily: "monospace", color: C.dim, width: 30 }}>{p.priority || i + 1}</td>
                                <td style={tdStyle}><CondCell raw={p.conditions} /></td>
                                <td style={tdStyle}>
                                  <span style={{ color: actionColor(p.action), fontWeight: "bold",
                                    fontSize: 8.5, padding: "1px 6px", borderRadius: 3,
                                    background: actionColor(p.action) + "15" }}>
                                    {p.action || "—"}
                                  </span>
                                </td>
                                <td style={{ ...tdStyle, fontSize: 8.5, color: C.slate }}>{p.action_detail || "—"}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    )}
                  </div>
                ) : <Loader msg="Loading rules..." />}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 6: METRICS — live counts, never stale
// ══════════════════════════════════════════════════════════════════════════════
const Q_TOTAL_NODES = "MATCH (n) RETURN count(n) AS total";
const Q_TOTAL_RELS = "MATCH ()-[r]->() RETURN count(r) AS total";
const Q_LABEL_COUNTS = `MATCH (n)
RETURN DISTINCT labels(n) AS labels, count(*) AS cnt
ORDER BY cnt DESC LIMIT 30`;
const Q_REL_COUNTS = `MATCH ()-[r]->()
RETURN DISTINCT type(r) AS rel, count(*) AS cnt
ORDER BY cnt DESC LIMIT 30`;

function MetricsTab() {
  const nodes = useCypher(Q_TOTAL_NODES);
  const rels = useCypher(Q_TOTAL_RELS);
  const labels = useCypher(Q_LABEL_COUNTS);
  const relCounts = useCypher(Q_REL_COUNTS);

  const loading = nodes.loading || rels.loading || labels.loading || relCounts.loading;
  const err = nodes.error || rels.error || labels.error || relCounts.error;
  if (loading) return <Loader msg="Counting nodes and relationships..." />;
  if (err) return <Err msg={err} />;

  const totalNodes = nodes.data[0]?.total || 0;
  const totalRels = rels.data[0]?.total || 0;

  return (
    <div>
      {/* Hero metrics */}
      <div style={{ display: "flex", gap: 0, marginBottom: 16, borderRadius: 8, overflow: "hidden" }}>
        {[
          [totalNodes.toLocaleString(), "total nodes", C.navy],
          [totalRels.toLocaleString(), "total relationships", C.teal],
          [labels.data.length + "+", "distinct label combos", C.purple],
          [relCounts.data.length + "+", "distinct rel types", C.amber],
        ].map(([val, label, col]) => (
          <div key={label} style={{ flex: 1, background: col, padding: "12px 16px", textAlign: "center" }}>
            <div style={{ fontSize: 18, fontWeight: "bold", color: "white" }}>{val}</div>
            <div style={{ fontSize: 8.5, color: "rgba(255,255,255,0.7)" }}>{label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Top labels */}
        <div>
          <div style={{ fontWeight: "bold", fontSize: 10, color: C.navy, marginBottom: 6 }}>Top 30 Label Combos</div>
          {labels.data.map((row, i) => (
            <div key={i} style={{ display: "flex", gap: 4, marginBottom: 2, fontSize: 8.5 }}>
              <span style={{ color: C.dim, width: 60, textAlign: "right", fontFamily: "monospace" }}>
                {row.cnt.toLocaleString()}
              </span>
              <span style={{ color: C.purple }}>{row.labels.map((l) => `:${l}`).join(" ")}</span>
            </div>
          ))}
        </div>
        {/* Top rels */}
        <div>
          <div style={{ fontWeight: "bold", fontSize: 10, color: C.teal, marginBottom: 6 }}>Top 30 Rel Types</div>
          {relCounts.data.map((row, i) => (
            <div key={i} style={{ display: "flex", gap: 4, marginBottom: 2, fontSize: 8.5 }}>
              <span style={{ color: C.dim, width: 60, textAlign: "right", fontFamily: "monospace" }}>
                {row.cnt.toLocaleString()}
              </span>
              <Mono col={C.teal} s={8}>{row.rel}</Mono>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 7: DISCIPLINES — live from Neo4j Discipline nodes
// ══════════════════════════════════════════════════════════════════════════════
const Q_DISCIPLINES = `MATCH (d:Discipline) WHERE d.tier = 'backbone'
OPTIONAL MATCH (d)-[hf:HAS_FACET]->(f:Facet) WHERE hf.primary = true
RETURN d.qid AS qid, d.label AS label,
       d.lcsh_id AS lcsh_id, d.gnd_id AS gnd_id,
       d.ddc AS ddc, d.aat_id AS aat_id, d.kbpedia_id AS kbpedia_id,
       d.subclass_of_label AS parent_label,
       collect(f.label) AS primary_facets
ORDER BY d.label LIMIT 200`;

const Q_DISC_STATS = `MATCH (d:Discipline) WHERE d.tier = 'backbone'
RETURN count(d) AS total,
       count(d.lcsh_id) AS has_lcsh,
       count(d.gnd_id) AS has_gnd,
       count(d.ddc) AS has_ddc,
       count(d.aat_id) AS has_aat,
       count(d.subclass_of) AS has_parent`;

function DisciplineTab() {
  const { data, loading, error } = useCypher(Q_DISCIPLINES);
  const stats = useCypher(Q_DISC_STATS);
  const [search, setSearch] = useState("");

  if (loading) return <Loader msg="Loading disciplines from Neo4j..." />;
  if (error) return <Err msg={error} />;

  const filtered = data.filter((d) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (d.label || "").toLowerCase().includes(s) ||
           (d.qid || "").toLowerCase().includes(s) ||
           (d.lcsh_id || "").toLowerCase().includes(s) ||
           (d.gnd_id || "").toLowerCase().includes(s);
  });

  const st = stats.data?.[0];

  return (
    <div>
      <CypherBlock query={Q_DISCIPLINES} label="DISCIPLINES QUERY" />

      {/* Stats bar */}
      {st && (
        <div style={{ display: "flex", gap: 12, marginBottom: 10, flexWrap: "wrap" }}>
          {[
            [st.total, "total", C.ink],
            [st.has_lcsh, "LCSH", C.purple],
            [st.has_gnd, "GND", C.teal],
            [st.has_ddc, "DDC", C.slate],
            [st.has_aat, "AAT", C.orange],
            [st.has_parent, "in hierarchy", C.green],
          ].map(([n, l, col]) => (
            <div key={l} style={{ fontSize: 9, color: col }}>
              <strong>{n}</strong> <span style={{ color: C.dim }}>{l}</span>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginBottom: 8, alignItems: "center" }}>
        <input value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by label, QID, LCSH, GND..." style={{ border: `1px solid ${C.rule}`,
            borderRadius: 6, padding: "4px 10px", fontSize: 10, width: 260 }} />
        <span style={{ fontSize: 9, color: C.dim }}>{filtered.length} of {data.length} shown</span>
      </div>

      <div style={{ maxHeight: 520, overflow: "auto" }}>
        {filtered.map((d) => {
          const hasAuth = d.lcsh_id || d.gnd_id || d.ddc || d.aat_id;
          return (
            <div key={d.qid || d.label} style={{
              border: `1px solid ${hasAuth ? C.green : C.rule}`,
              borderLeft: `3px solid ${hasAuth ? C.green : C.rule}`,
              borderRadius: 4, marginBottom: 3, padding: "4px 10px",
              display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap",
              background: "white" }}>
              {d.qid && <Mono col={C.dim} s={7.5}>{d.qid}</Mono>}
              <span style={{ fontWeight: "bold", fontSize: 10, color: C.ink }}>{d.label}</span>
              {d.primary_facets?.map((f) => (
                <Tag key={f} label={f} fill={FACET_COLOR[f] || C.slate} s={7} />
              ))}
              {d.lcsh_id && <Mono col={C.purple} s={7.5}>LCSH: {d.lcsh_id.split("|")[0]}</Mono>}
              {d.gnd_id && <Mono col={C.teal}   s={7.5}>GND: {d.gnd_id}</Mono>}
              {d.ddc    && <Mono col={C.slate}  s={7.5}>DDC: {d.ddc.split("|")[0]}</Mono>}
              {d.aat_id && <Mono col={C.orange} s={7.5}>AAT: {d.aat_id}</Mono>}
              {d.kbpedia_id && <Mono col={C.cyan} s={7.5}>KBpedia: {d.kbpedia_id}</Mono>}
              {d.parent_label && (
                <span style={{ fontSize: 7.5, color: C.dim, marginLeft: "auto" }}>
                  ⊂ {d.parent_label.split("|")[0]}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 8: AGENTS + WORKFLOW
// ══════════════════════════════════════════════════════════════════════════════
const Q_AGENTS = `MATCH (c:Chrystallum)-[:HAS_AGENT]->(a:Agent)
RETURN a.name AS name, a.status AS status, a.description AS desc, keys(a) AS props
ORDER BY a.name`;

const Q_AGENT_TYPES = `MATCH (c:Chrystallum)-[:HAS_AGENT_TYPE]->(at:SYS_AgentType)
RETURN at.name AS name, at.description AS desc
ORDER BY at.name`;

const Q_WORKFLOW = `MATCH (w:SYS_Workflow)-[:HAS_STEP]->(s:SYS_WorkflowStep)
RETURN w.label AS workflow, s.step_id AS step_id, s.label AS step_label,
       s.description AS step_desc
ORDER BY s.step_id`;

function AgentTab() {
  const agents = useCypher(Q_AGENTS);
  const agentTypes = useCypher(Q_AGENT_TYPES);
  const workflow = useCypher(Q_WORKFLOW);

  const loading = agents.loading || agentTypes.loading || workflow.loading;
  const err = agents.error || agentTypes.error || workflow.error;
  if (loading) return <Loader msg="Loading agents and workflow..." />;
  if (err) return <Err msg={err} />;

  return (
    <div>
      {/* Agent Types */}
      <div style={{ fontWeight: "bold", fontSize: 11, color: C.navy, marginBottom: 6 }}>
        Agent Types ({agentTypes.data.length})
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 4, marginBottom: 16 }}>
        {agentTypes.data.map((at) => (
          <div key={at.name} style={{ border: `1px solid ${C.rule}`, borderRadius: 4,
            padding: "6px 10px", borderLeft: `3px solid ${C.purple}` }}>
            <div style={{ fontWeight: "bold", fontSize: 10, color: C.purple }}>{at.name}</div>
            {at.desc && <div style={{ fontSize: 8, color: C.slate, marginTop: 2 }}>{at.desc}</div>}
          </div>
        ))}
      </div>

      {/* Registered Agents */}
      <div style={{ fontWeight: "bold", fontSize: 11, color: C.teal, marginBottom: 6 }}>
        Registered Agents ({agents.data.length})
      </div>
      {agents.data.map((a) => (
        <div key={a.name} style={{ border: `1px solid ${C.rule}`, borderRadius: 4,
          marginBottom: 3, padding: "5px 10px", display: "flex", gap: 8,
          alignItems: "center", background: "white" }}>
          <span style={{ fontWeight: "bold", fontSize: 10, color: C.ink }}>{a.name}</span>
          {a.status && <Tag label={a.status} fill={STATUS_COL[a.status] || C.dim} />}
          {a.desc && <span style={{ fontSize: 8.5, color: C.slate }}>{a.desc}</span>}
        </div>
      ))}

      {/* Workflow */}
      {workflow.data.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontWeight: "bold", fontSize: 11, color: C.amber, marginBottom: 8 }}>
            SFA Workflow: {workflow.data[0]?.workflow}
          </div>
          {workflow.data.map((s, i) => (
            <div key={s.step_id} style={{ display: "flex", gap: 10, marginBottom: 8, alignItems: "flex-start" }}>
              <div style={{ background: C.amber, color: "white", borderRadius: "50%", width: 20, height: 20,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 9, fontWeight: "bold", flexShrink: 0 }}>{i + 1}</div>
              <div>
                <div style={{ fontWeight: "bold", fontSize: 9.5, color: C.amber }}>{s.step_label}</div>
                <div style={{ fontSize: 8, color: C.slate }}>{s.step_id}</div>
                {s.step_desc && <div style={{ fontSize: 8, color: C.dim, marginTop: 1 }}>{s.step_desc}</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 9: PIPELINE — L0→L1→L2→L3→Graph + Chrystallum vs Native Neo4j
// (Absorbs architecture.jsx — all counts live)
// ══════════════════════════════════════════════════════════════════════════════

const Q_PIPELINE_FED = `MATCH (fr:SYS_FederationRegistry)-[:CONTAINS]->(fs:SYS_FederationSource)
RETURN fs.source_id AS sid, fs.label AS label, fs.status AS status
ORDER BY fs.label`;

const Q_PIPELINE_ADRS = `MATCH (c:Chrystallum)-[:HAS_ADR]->(a:SYS_ADR)
RETURN a.adr_id AS id, a.title AS title, a.status AS status
ORDER BY a.adr_id`;

const Q_PIPELINE_ONBOARDING = `MATCH (op:SYS_OnboardingProtocol)-[:HAS_STEP]->(s:SYS_OnboardingStep)
RETURN op.label AS protocol, s.step_id AS step_id, s.label AS label
ORDER BY s.step_id`;

const Q_PIPELINE_TOTALS = `MATCH (n) WITH count(n) AS nodes
MATCH ()-[r]->() WITH nodes, count(r) AS rels
MATCH (:SYS_RelationshipType) WITH nodes, rels, count(*) AS rel_types
MATCH (:SYS_FederationSource) WITH nodes, rels, rel_types, count(*) AS fed_sources
MATCH (:Person) WITH nodes, rels, rel_types, fed_sources, count(*) AS persons
MATCH (:Place) WITH nodes, rels, rel_types, fed_sources, persons, count(*) AS places
MATCH ()-[:POSITION_HELD]->()
RETURN nodes, rels, rel_types, fed_sources, persons, places, count(*) AS pos_held`;

function PipelineTab() {
  const fed = useCypher(Q_PIPELINE_FED);
  const adrs = useCypher(Q_PIPELINE_ADRS);
  const onboarding = useCypher(Q_PIPELINE_ONBOARDING);
  const totals = useCypher(Q_PIPELINE_TOTALS);

  const loading = fed.loading || adrs.loading || onboarding.loading || totals.loading;
  const err = fed.error || adrs.error || onboarding.error || totals.error;
  if (loading) return <Loader msg="Loading pipeline data..." />;
  if (err) return <Err msg={err} />;

  const t = totals.data?.[0] || {};
  const fedByStatus = {};
  (fed.data || []).forEach((f) => { fedByStatus[f.status] = (fedByStatus[f.status] || 0) + 1; });
  const fedSummary = Object.entries(fedByStatus).map(([s, c]) => `${c} ${s}`).join(" + ");

  const LAYERS = [
    {
      name: "L0 — Federation Sources", col: C.navy,
      desc: `${fed.data?.length || 0} registered (${fedSummary})`,
      detail: (fed.data || []).map((f) => ({
        label: f.label, status: f.status, col: STATUS_COL[f.status] || C.dim
      })),
    },
    {
      name: "L1 — Harvest Pipeline (Deterministic)", col: "#2E75B6",
      desc: "Grammar-based parsing, P-code mapping, date normalisation, backlink capture, federation status check, QID validation, context packet assembly",
      steps: ["DPRR Label Parser", "P-code Rel Mapper", "Date Normaliser", "WD Backlink Capture",
        "Federation Status Check", "QID Validator", "Context Packet Assembler"],
    },
    {
      name: "L2 — Agent Reasoning (LLM)", col: C.teal,
      desc: "Cross-federation reconciliation, conflict classification, authority weighting, filiation disambiguation. Produces PersonHarvestPlan. Never writes to graph.",
      constraints: [
        ["Cannot write nodes or edges", false],
        ["Cannot query live graph during reasoning", false],
        ["Cannot evaluate numeric thresholds", false],
        ["Cannot generate freeform Cypher", false],
        ["Receives fixed context packet only", true],
        ["Plan is auditable + re-runnable", true],
        ["Can use any LLM — model versioned", true],
      ],
    },
    {
      name: "L3 — Deterministic Execution", col: C.slate,
      desc: "13-step schema-validated Cypher sequence. Idempotent. ADR-006 compliant.",
      steps: ["Write HarvestPlan", "Merge Gens/Tribe/Polity", "Merge Praenomen/Nomen/Cognomen",
        "Apply :Person label", "Write literal props", "Write onomastic rels",
        "Write civic/political rels", "Write family rels", "Write office/military rels",
        "Write authority links", "Write conflict structures", "Evaluate D10 threshold", "Set COMPLETE"],
    },
  ];

  return (
    <div>
      {/* Metrics bar */}
      <div style={{ display: "flex", gap: 0, marginBottom: 16, borderRadius: 8, overflow: "hidden" }}>
        {[
          [t.nodes?.toLocaleString(), "total nodes", C.navy],
          [t.rels?.toLocaleString(), "total rels", C.teal],
          [t.rel_types?.toString(), "reg. rel types", C.purple],
          [t.fed_sources?.toString(), "fed sources", C.amber],
          [t.persons?.toLocaleString(), ":Person", C.rose],
          [t.places?.toLocaleString(), ":Place", C.lime],
          [t.pos_held?.toLocaleString(), "POSITION_HELD", C.crimson],
        ].map(([val, label, col]) => (
          <div key={label} style={{ flex: 1, background: col, padding: "10px 12px", textAlign: "center" }}>
            <div style={{ fontSize: 16, fontWeight: "bold", color: "white" }}>{val}</div>
            <div style={{ fontSize: 7.5, color: "rgba(255,255,255,0.65)" }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Pipeline layers */}
      {LAYERS.map((layer, li) => (
        <div key={layer.name} style={{ border: `1.5px solid ${layer.col}`, borderRadius: 6,
          marginBottom: 10, overflow: "hidden" }}>
          <div style={{ background: layer.col, padding: "6px 12px" }}>
            <span style={{ fontSize: 11, fontWeight: "bold", color: "white" }}>{layer.name}</span>
          </div>
          <div style={{ padding: "8px 12px", background: "white" }}>
            <div style={{ fontSize: 9, color: C.slate, marginBottom: 6 }}>{layer.desc}</div>

            {/* L0: federation source pills */}
            {layer.detail && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 3 }}>
                {layer.detail.map((f) => (
                  <Tag key={f.label} label={f.label} fill={f.col} s={7.5} />
                ))}
              </div>
            )}

            {/* L1/L3: step boxes */}
            {layer.steps && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 0, alignItems: "center" }}>
                {layer.steps.map((step, i) => (
                  <div key={step} style={{ display: "flex", alignItems: "center" }}>
                    <div style={{ background: layer.col + "15", border: `1px solid ${layer.col}`,
                      borderRadius: 4, padding: "4px 8px", fontSize: 8, fontWeight: "bold",
                      color: layer.col, textAlign: "center" }}>
                      <div style={{ fontSize: 7, color: C.dim }}>{li === 3 ? i + 1 : ""}</div>
                      {step}
                    </div>
                    {i < layer.steps.length - 1 && (
                      <span style={{ color: layer.col, margin: "0 3px", fontSize: 12 }}>{"\u2192"}</span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* L2: constraints */}
            {layer.constraints && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 2 }}>
                {layer.constraints.map(([text, ok]) => (
                  <div key={text} style={{ fontSize: 8.5, color: ok ? C.green : C.crimson }}>
                    {ok ? "\u2713" : "\u2717"}{"  "}{text}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Flow arrows */}
      <div style={{ textAlign: "center", margin: "8px 0 16px", fontSize: 9, color: C.dim }}>
        L0 {"\u2192"} L1 {"\u2192"} L2 {"\u2192"} L3 {"\u2192"} Neo4j Graph
        {"  "}|{"  "}SYS layer feeds back config into L1 + L2 (dashed reference)
      </div>

      {/* Chrystallum vs Native Neo4j */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 16 }}>
        <div style={{ border: `1.5px solid ${C.dim}`, borderRadius: 6, padding: 10, background: "#F8F9FA" }}>
          <div style={{ fontWeight: "bold", fontSize: 11, color: C.crimson, marginBottom: 8 }}>
            Native Neo4j / Property Graph
          </div>
          {[
            ["Node labels", "Ontology in application code, not graph"],
            ["Relationships", "Schema-free, any type between any nodes"],
            ["Provenance", "Not native, requires custom properties"],
            ["Confidence", "Application-layer convention"],
            ["Schema", "graph.db.schema() advisory only"],
            ["Merges", "MERGE on arbitrary key, no canonical dedup"],
            ["Agent integration", "None native"],
            ["Temporal scoping", "Application property convention"],
            ["Self-description", "Not native, no registry of types in graph"],
          ].map(([k, v]) => (
            <div key={k} style={{ marginBottom: 3, fontSize: 8.5 }}>
              <span style={{ color: C.crimson, fontWeight: "bold" }}>{k}: </span>
              <span style={{ color: C.slate }}>{v}</span>
            </div>
          ))}
        </div>
        <div style={{ border: `1.5px solid ${C.teal}`, borderRadius: 6, padding: 10, background: C.teal + "05" }}>
          <div style={{ fontWeight: "bold", fontSize: 11, color: C.teal, marginBottom: 8 }}>
            Chrystallum (on Neo4j)
          </div>
          {[
            ["Node labels", `Declared in SYS_NodeType registry (${t.nodes ? "live" : "..."})`],
            ["Relationships", `${t.rel_types || "..."} types registered in SYS_RelationshipType with domain/range`],
            ["Provenance", "ADR-006: ScaffoldEdge carries FROM/TO assertion URI"],
            ["Confidence", "SYS_ConfidenceTier + per-claim confidence (0-1)"],
            ["Schema", "SYS_ValidationRule + SYS_PropertyMapping — schema is data"],
            ["Merges", "entity_cipher + edge_cipher — O(1) SHA-256 content-address"],
            ["Agent integration", "Three-layer: det. pre > LLM reason > det. execute"],
            ["Temporal scoping", "IN_PERIOD > :Periodo_Period + STARTS/ENDS_IN_YEAR > :Year"],
            ["Self-description", `${onboarding.data?.length || 0}-step onboarding; graph explains itself`],
          ].map(([k, v]) => (
            <div key={k} style={{ marginBottom: 3, fontSize: 8.5 }}>
              <span style={{ color: C.teal, fontWeight: "bold" }}>{k}: </span>
              <span style={{ color: C.slate }}>{v}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ADRs */}
      {adrs.data?.length > 0 && (
        <div style={{ border: `1px solid ${C.rule}`, borderRadius: 6, padding: 10, marginBottom: 10, background: "white" }}>
          <div style={{ fontWeight: "bold", fontSize: 10, color: C.navy, marginBottom: 6 }}>
            ADRs ({adrs.data.length})
          </div>
          {adrs.data.map((a) => (
            <div key={a.id} style={{ display: "flex", gap: 8, fontSize: 8.5, marginBottom: 2 }}>
              <Mono col={C.navy} s={8}>{a.id}</Mono>
              <span style={{ color: C.ink }}>{a.title}</span>
              {a.status && <Tag label={a.status} fill={a.status === "accepted" ? C.green : C.amber} s={7} />}
            </div>
          ))}
        </div>
      )}

      {/* Standards */}
      <div style={{ border: `1px solid ${C.rule}`, borderRadius: 6, padding: 10, background: "white" }}>
        <div style={{ fontWeight: "bold", fontSize: 10, color: C.slate, marginBottom: 6 }}>Standards Alignment</div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {[
            ["CIDOC-CRM (ISO 21127)", "Internal ontological anchor", C.navy],
            ["GEDCOM 7.0", "Export target (planned)", C.amber],
            ["LOD / RDF", "Future public URI", C.dim],
            ["SPARQL", "Federation query protocol", C.teal],
            ["OpenAlex / FAST / VIAF", "Authority record IDs", C.purple],
          ].map(([name, role, col]) => (
            <div key={name} style={{ border: `1px solid ${col}`, borderRadius: 4, padding: "4px 8px",
              flex: "1 1 160px" }}>
              <div style={{ fontSize: 9, fontWeight: "bold", color: col }}>{name}</div>
              <div style={{ fontSize: 7.5, color: C.dim }}>{role}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 12, textAlign: "center", fontSize: 8.5, color: C.dim, fontStyle: "italic" }}>
        "An accessible implementation of Hermann Hesse's Glass Bead Game — cross-domain knowledge synthesis"
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 10: CONTRACT — DI → SCA → SFA → Graph loop (from SCA_SFA_CONTRACT.md)
// ══════════════════════════════════════════════════════════════════════════════

// Live counts for each stage of the contract loop
const Q_CONTRACT_AGENTS = `MATCH (c:Chrystallum)-[:HAS_AGENT]->(a:Agent)
RETURN a.name AS name, a.status AS status, a.description AS desc
ORDER BY a.name`;

const Q_CONTRACT_COUNTS = `
MATCH (sc:SubjectConcept) WITH count(sc) AS subjects
MATCH ()-[pf:HAS_PRIMARY_FACET]->() WITH subjects, count(pf) AS primary_facet_edges
MATCH ()-[sf:HAS_SECONDARY_FACET]->() WITH subjects, primary_facet_edges, count(sf) AS secondary_facet_edges
MATCH (cd:SYS_CurationDecision) WITH subjects, primary_facet_edges, secondary_facet_edges, count(cd) AS curations
MATCH (fr:SYS_FacetRouter) WITH subjects, primary_facet_edges, secondary_facet_edges, curations, count(fr) AS routers
MATCH (cl:Claim) WITH subjects, primary_facet_edges, secondary_facet_edges, curations, routers, count(cl) AS claims
MATCH (pe:ProposedEdge) WITH subjects, primary_facet_edges, secondary_facet_edges, curations, routers, claims, count(pe) AS proposals
MATCH (oc:SYS_OutputContract)
RETURN subjects, primary_facet_edges, secondary_facet_edges, curations, routers, claims, proposals, oc.label AS contract_label`;

const Q_WORKFLOW_STEPS = `MATCH (w:SYS_Workflow)-[:HAS_STEP]->(s:SYS_WorkflowStep)
RETURN s.step_id AS step_id, s.label AS label, s.description AS desc
ORDER BY s.step_id`;

const Q_OUTPUT_CONTRACT = `MATCH (oc:SYS_OutputContract)
RETURN oc.contract_id AS id, oc.label AS label, oc.description AS desc,
       oc.op_types AS op_types, oc.required_fields AS required_fields,
       oc.facet_weight_spec AS facet_weight_spec`;

const Q_TRAINING = `MATCH (tr:SFA_TrainingRun)
OPTIONAL MATCH (tr)-[:PRODUCED]->(ti:SFA_TrainingInsight)
RETURN tr.facet AS facet, tr.status AS status, count(ti) AS insights
ORDER BY tr.facet`;

function ContractTab() {
  const agents = useCypher(Q_CONTRACT_AGENTS);
  const counts = useCypher(Q_CONTRACT_COUNTS);
  const workflow = useCypher(Q_WORKFLOW_STEPS);
  const training = useCypher(Q_TRAINING);
  const outputContract = useCypher(Q_OUTPUT_CONTRACT);

  const loading = agents.loading || counts.loading || workflow.loading || training.loading || outputContract.loading;
  const err = agents.error || counts.error || workflow.error || training.error || outputContract.error;
  if (loading) return <Loader msg="Loading contract data..." />;
  if (err) return <Err msg={err} />;

  const c = counts.data?.[0] || {};
  const di = agents.data?.find((a) => a.name === "DOMAIN_INITIATOR");
  const sca = agents.data?.find((a) => a.name === "SCA");
  const sfas = agents.data?.filter((a) => a.name?.startsWith("SFA_")) || [];

  // Group contract stages
  const STAGES = [
    {
      id: "DI", label: "Domain Initiator", col: C.amber, agent: di,
      desc: "Harvests a domain QID once. Classifies entities by facet. Feeds structured output to SCA.",
      outputs: [
        ["SubjectConcepts", c.subjects],
        ["Primary facet edges", c.primary_facet_edges],
        ["Secondary facet edges", c.secondary_facet_edges],
        ["CurationDecisions", c.curations],
        ["FacetRouter patterns", c.routers],
      ],
    },
    {
      id: "SCA", label: "Subject Concept Agent", col: C.navy, agent: sca,
      desc: "Coordinates SFAs. Routes DI output. Manages SubjectConcept lifecycle. Re-scores when SFA proposals return.",
      outputs: [
        ["SubjectConcepts managed", c.subjects],
        ["CurationDecisions", c.curations],
        ["FacetRouter patterns", c.routers],
      ],
    },
    {
      id: "SFA", label: "Subject-Facet Agents", col: C.teal, agent: null,
      desc: "Per-facet specialists. Add within-facet concepts the harvest missed, cross-facet relationships, framework overlays.",
      outputs: [
        ["Active SFAs", sfas.filter((s) => s.status === "active").length],
        ["Claims produced", c.claims],
        ["ProposedEdges", c.proposals],
        ["Training runs", training.data?.length || 0],
        ["Training insights", training.data?.reduce((s, t) => s + t.insights, 0) || 0],
      ],
    },
    {
      id: "GRAPH", label: "Neo4j Graph", col: C.purple, agent: null,
      desc: "SFA proposals enter as Claims (not truth). Confidence <= T_SFA_CONFIDENCE_CEILING. Contestable by other SFAs.",
      outputs: [
        ["OutputContract", c.contract_label || "missing"],
      ],
    },
  ];

  return (
    <div>
      {/* Contract loop diagram */}
      <div style={{ background: C.ink, borderRadius: 8, padding: 16, marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 0, flexWrap: "wrap" }}>
          {STAGES.map((stage, i) => (
            <div key={stage.id} style={{ display: "flex", alignItems: "center" }}>
              <div style={{ background: stage.col, borderRadius: 8, padding: "10px 16px",
                minWidth: 140, textAlign: "center" }}>
                <div style={{ fontSize: 12, fontWeight: "bold", color: "white" }}>{stage.label}</div>
                <div style={{ fontSize: 9, color: "rgba(255,255,255,0.7)", marginTop: 2 }}>{stage.id}</div>
                {stage.agent && (
                  <Tag label={stage.agent.status} fill={STATUS_COL[stage.agent.status] || C.dim} s={7} />
                )}
                {stage.id === "SFA" && (
                  <div style={{ marginTop: 4, display: "flex", gap: 2, justifyContent: "center", flexWrap: "wrap" }}>
                    {sfas.map((s) => (
                      <Tag key={s.name} label={s.name.replace("SFA_", "").replace("_RR", "")}
                        fill={STATUS_COL[s.status] || C.dim} s={6} />
                    ))}
                  </div>
                )}
              </div>
              {i < STAGES.length - 1 && (
                <div style={{ color: C.teal, fontSize: 18, margin: "0 8px", fontWeight: "bold" }}>
                  {"\u2192"}
                </div>
              )}
            </div>
          ))}
          {/* Loop-back arrow */}
          <div style={{ color: C.amber, fontSize: 14, margin: "0 12px", fontWeight: "bold" }}>
            {"\u21BA"} re-score
          </div>
        </div>
        <div style={{ textAlign: "center", marginTop: 10, fontSize: 8.5, color: C.dim, fontStyle: "italic" }}>
          "The self-describing system completes its loop when SFA proposals flow back into the graph and SCA re-scores with those additions."
        </div>
      </div>

      {/* Stage detail cards */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 16 }}>
        {STAGES.map((stage) => (
          <div key={stage.id} style={{ border: `1.5px solid ${stage.col}`, borderRadius: 6,
            padding: 10, background: "white" }}>
            <div style={{ fontWeight: "bold", fontSize: 11, color: stage.col, marginBottom: 4 }}>
              {stage.label}
            </div>
            <div style={{ fontSize: 8.5, color: C.slate, marginBottom: 8 }}>{stage.desc}</div>
            <div style={{ fontSize: 8, color: C.dim, fontWeight: "bold", marginBottom: 4 }}>LIVE COUNTS</div>
            {stage.outputs.map(([label, val]) => (
              <div key={label} style={{ display: "flex", justifyContent: "space-between",
                marginBottom: 2, fontSize: 8.5 }}>
                <span style={{ color: C.slate }}>{label}</span>
                <span style={{ fontWeight: "bold", color: stage.col, fontFamily: "monospace" }}>
                  {typeof val === "number" ? val.toLocaleString() : val}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* SFA Workflow */}
      {workflow.data?.length > 0 && (
        <div style={{ border: `1px solid ${C.rule}`, borderRadius: 6, padding: 10, marginBottom: 16, background: "white" }}>
          <div style={{ fontWeight: "bold", fontSize: 11, color: C.amber, marginBottom: 8 }}>
            SFA Self-Directed Workflow ({workflow.data.length} steps)
          </div>
          <div style={{ display: "flex", gap: 0, flexWrap: "wrap", alignItems: "flex-start" }}>
            {workflow.data.map((s, i) => (
              <div key={s.step_id} style={{ display: "flex", alignItems: "center" }}>
                <div style={{ background: C.amber + "15", border: `1px solid ${C.amber}`,
                  borderRadius: 6, padding: "6px 10px", minWidth: 90, textAlign: "center" }}>
                  <div style={{ fontSize: 9, fontWeight: "bold", color: C.amber }}>{s.label}</div>
                  <div style={{ fontSize: 7, color: C.dim }}>{s.step_id}</div>
                </div>
                {i < workflow.data.length - 1 && (
                  <span style={{ color: C.amber, margin: "0 4px", fontSize: 14 }}>{"\u2192"}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SFA Training Runs */}
      {training.data?.length > 0 && (
        <div style={{ border: `1px solid ${C.rule}`, borderRadius: 6, padding: 10, background: "white" }}>
          <div style={{ fontWeight: "bold", fontSize: 11, color: C.teal, marginBottom: 6 }}>
            SFA Training Runs
          </div>
          {training.data.map((tr, i) => (
            <div key={i} style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 3 }}>
              <Tag label={tr.facet || "unknown"} fill={FACET_COLOR[tr.facet] || C.slate} />
              <Tag label={tr.status || "unknown"} fill={STATUS_COL[tr.status] || C.dim} />
              <span style={{ fontSize: 8.5, color: C.slate }}>{tr.insights} insights</span>
            </div>
          ))}
        </div>
      )}

      {/* Output Contract */}
      {outputContract.data?.length > 0 && (
        <div style={{ marginTop: 16, border: `1.5px solid ${C.teal}`, borderRadius: 6, overflow: "hidden" }}>
          <div style={{ background: C.teal, padding: "6px 12px" }}>
            <span style={{ fontSize: 11, fontWeight: "bold", color: "white" }}>
              SFA Output Contract
            </span>
          </div>
          {outputContract.data.map((oc) => (
            <div key={oc.id} style={{ padding: "8px 12px", background: "white" }}>
              <div style={{ display: "flex", gap: 8, alignItems: "baseline", marginBottom: 6 }}>
                <Mono col={C.teal} s={8}>{oc.id}</Mono>
                <span style={{ fontWeight: "bold", fontSize: 10, color: C.ink }}>{oc.label}</span>
              </div>
              {oc.desc && <div style={{ fontSize: 8.5, color: C.slate, marginBottom: 8 }}>{oc.desc}</div>}
              <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "4px 12px", fontSize: 8.5 }}>
                <span style={{ fontWeight: "bold", color: C.dim }}>Op types:</span>
                <span style={{ fontFamily: "monospace", color: C.teal, fontSize: 8 }}>{oc.op_types}</span>
                <span style={{ fontWeight: "bold", color: C.dim }}>Required fields:</span>
                <span style={{ color: C.slate, fontSize: 8 }}>{oc.required_fields}</span>
                <span style={{ fontWeight: "bold", color: C.dim }}>Facet weights:</span>
                <span style={{ color: C.slate, fontSize: 8 }}>{oc.facet_weight_spec}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Contract terms */}
      <div style={{ marginTop: 16, border: `1px solid ${C.navy}`, borderRadius: 6,
        padding: 10, background: C.navy + "08" }}>
        <div style={{ fontWeight: "bold", fontSize: 10, color: C.navy, marginBottom: 6 }}>
          Contract Terms (from SCA_SFA_CONTRACT.md)
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "auto 1fr 1fr", gap: "4px 12px", fontSize: 8.5 }}>
          <span style={{ fontWeight: "bold", color: C.dim }}></span>
          <span style={{ fontWeight: "bold", color: C.navy }}>SCA</span>
          <span style={{ fontWeight: "bold", color: C.teal }}>SFA</span>

          <span style={{ color: C.dim }}>Role</span>
          <span style={{ color: C.slate }}>Grounded empirical structure</span>
          <span style={{ color: C.slate }}>Historical interpretive judgment</span>

          <span style={{ color: C.dim }}>Provides</span>
          <span style={{ color: C.slate }}>Harvest evidence, confidence, entry doors, pre-computed paths</span>
          <span style={{ color: C.slate }}>Within-facet additions, cross-facet proposals, framework overlays</span>

          <span style={{ color: C.dim }}>Does not</span>
          <span style={{ color: C.slate }}>Validate taxonomy</span>
          <span style={{ color: C.slate }}>Discover paths at query time</span>

          <span style={{ color: C.dim }}>Provenance</span>
          <span style={{ color: C.slate }}>source: "sca_harvest"</span>
          <span style={{ color: C.slate }}>source: "sfa_inference", confidence: 0.75</span>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 11: TRAINING — SFA Training Depth, Subgraph Ownership, Structured Sources
// ══════════════════════════════════════════════════════════════════════════════

// Workflow chain via NEXT_STEP traversal (correct ordering)
const Q_WORKFLOW_CHAIN = `MATCH (w:SYS_Workflow)-[:HAS_STEP]->(s:SYS_WorkflowStep)
OPTIONAL MATCH (s)-[:NEXT_STEP]->(ns:SYS_WorkflowStep)
RETURN s.step_id AS id, s.label AS label, s.description AS desc, ns.step_id AS next_id
ORDER BY s.step_id`;

// Training runs with full stats
const Q_TRAINING_RUNS = `MATCH (tr:SFA_TrainingRun)
RETURN tr.run_id AS run_id, tr.facet_key AS facet, tr.status AS status,
       tr.works_consulted AS works, tr.insights_produced AS insights,
       tr.candidates_confirmed AS confirmed, tr.candidates_rejected AS rejected,
       tr.candidates_rerouted AS rerouted, tr.corpus_gaps AS gaps,
       tr.training_summary AS summary, tr.should_decompose AS decompose,
       tr.decomposition_reason AS decomp_reason, tr.model AS model
ORDER BY tr.run_id`;

// Training insights with evidence
const Q_TRAINING_INSIGHTS = `MATCH (tr:SFA_TrainingRun)-[:PRODUCED]->(ti:SFA_TrainingInsight)
RETURN ti.insight_id AS id, ti.insight_type AS type, ti.label AS label,
       ti.evidence AS evidence, ti.confidence AS conf, ti.status AS status,
       ti.facet_key AS facet, tr.run_id AS run_id
ORDER BY ti.confidence DESC`;

// Per-SFA agent info
const Q_SFA_AGENTS = `MATCH (a:Agent) WHERE a.name STARTS WITH 'SFA_'
RETURN a.name AS agent, a.status AS status,
       a.scope_description AS scope, a.confidence_ceiling AS ceiling,
       a.domain_label AS domain
ORDER BY a.name`;

// Per-facet asset counts (separate, no cartesian)
const Q_FACET_ASSETS = `MATCH (f:Facet)
OPTIONAL MATCH (sc:SubjectConcept)-[:HAS_PRIMARY_FACET]->(f)
WITH f, count(sc) AS pri
OPTIONAL MATCH (sc2:SubjectConcept)-[:HAS_SECONDARY_FACET]->(f)
WITH f, pri, count(sc2) AS sec
OPTIONAL MATCH (cw:CorpusWork)-[:RELEVANT_TO_FACET]->(f)
WITH f, pri, sec, count(cw) AS corpus
OPTIONAL MATCH (op:SYS_OASourcePack)-[:COVERS_FACET]->(f)
RETURN f.label AS facet, pri, sec, corpus, count(op) AS oa
ORDER BY f.label`;

// Training run counts per facet
const Q_TRAINING_BY_FACET = `MATCH (tr:SFA_TrainingRun)
RETURN tr.facet_key AS facet, count(tr) AS runs,
       sum(tr.insights_produced) AS insights
ORDER BY tr.facet_key`;

// OA source packs detail
const Q_OA_PACKS = `MATCH (op:SYS_OASourcePack)
OPTIONAL MATCH (op)-[:COVERS_FACET]->(f:Facet)
RETURN op.pack_id AS pack_id, op.label AS label, op.description AS desc,
       op.priority_texts AS texts, op.source_domains AS domains,
       f.label AS facet
ORDER BY op.pack_id`;

function TrainingTab() {
  const [selectedRun, setSelectedRun] = useState(null);
  const [section, setSection] = useState("overview");

  const chain = useCypher(Q_WORKFLOW_CHAIN);
  const runs = useCypher(Q_TRAINING_RUNS);
  const insights = useCypher(Q_TRAINING_INSIGHTS);
  const sfaAgents = useCypher(Q_SFA_AGENTS);
  const facetAssets = useCypher(Q_FACET_ASSETS);
  const trainByFacet = useCypher(Q_TRAINING_BY_FACET);
  const oaPacks = useCypher(Q_OA_PACKS);

  const loading = chain.loading || runs.loading || insights.loading || sfaAgents.loading || facetAssets.loading || trainByFacet.loading || oaPacks.loading;
  const err = chain.error || runs.error || insights.error || sfaAgents.error || facetAssets.error || trainByFacet.error || oaPacks.error;
  if (loading) return <Loader msg="Loading training depth data..." />;
  if (err) return <Err msg={err} />;

  // Build ordered chain from NEXT_STEP
  const ordered = [];
  if (chain.data?.length) {
    const byId = {};
    const nexts = new Set();
    chain.data.forEach((s) => { byId[s.id] = s; if (s.next_id) nexts.add(s.next_id); });
    // Find start: step not pointed to by any NEXT_STEP
    let start = chain.data.find((s) => !nexts.has(s.id));
    let cur = start;
    const seen = new Set();
    while (cur && !seen.has(cur.id)) {
      seen.add(cur.id);
      ordered.push(cur);
      cur = cur.next_id ? byId[cur.next_id] : null;
    }
    // Add any orphans
    chain.data.forEach((s) => { if (!seen.has(s.id)) ordered.push(s); });
  }

  // Group insights by type
  const insightsByType = {};
  (insights.data || []).forEach((i) => {
    const t = i.type || "unclassified";
    if (!insightsByType[t]) insightsByType[t] = [];
    insightsByType[t].push(i);
  });
  const TYPE_COL = {
    within_facet_addition: C.teal, cross_facet_link: C.purple,
    concept_refinement: C.amber, unclassified: C.dim,
  };

  const SECTIONS = [
    ["overview", "Overview"], ["runs", "Training Runs"],
    ["insights", "Insights"], ["ownership", "Subgraph Ownership"],
    ["guidance", "Structured Source Guidance"],
  ];

  return (
    <div>
      {/* Section nav */}
      <div style={{ display: "flex", gap: 0, marginBottom: 12, borderBottom: `1px solid ${C.rule}` }}>
        {SECTIONS.map(([k, l]) => (
          <button key={k} onClick={() => setSection(k)}
            style={{ border: "none", padding: "4px 12px", fontSize: 9, cursor: "pointer",
              background: "transparent", fontWeight: section === k ? "bold" : "normal",
              color: section === k ? C.teal : C.dim,
              borderBottom: section === k ? `2px solid ${C.teal}` : "2px solid transparent" }}>
            {l}
          </button>
        ))}
      </div>

      {/* ── Overview ── */}
      {section === "overview" && (
        <div>
          {/* Workflow chain — correct traversal order */}
          <div style={{ border: `1.5px solid ${C.amber}`, borderRadius: 6, padding: 12, marginBottom: 16, background: "white" }}>
            <div style={{ fontWeight: "bold", fontSize: 11, color: C.amber, marginBottom: 8 }}>
              SFA Workflow Chain (from NEXT_STEP edges)
            </div>
            <CypherBlock query={Q_WORKFLOW_CHAIN} label="WORKFLOW CHAIN" />
            <div style={{ display: "flex", gap: 0, flexWrap: "wrap", alignItems: "flex-start" }}>
              {ordered.map((s, i) => (
                <div key={s.id} style={{ display: "flex", alignItems: "center" }}>
                  <div style={{ background: C.amber + "15", border: `1px solid ${C.amber}`,
                    borderRadius: 6, padding: "6px 10px", minWidth: 90, textAlign: "center" }}>
                    <div style={{ fontSize: 9, fontWeight: "bold", color: C.amber }}>{s.label}</div>
                    <div style={{ fontSize: 6.5, color: C.dim, fontFamily: "monospace" }}>{s.id}</div>
                  </div>
                  {i < ordered.length - 1 && (
                    <span style={{ color: C.amber, margin: "0 4px", fontSize: 16 }}>{"\u2192"}</span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Quick stats */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 16 }}>
            {[
              ["Training Runs", runs.data?.length || 0, C.teal],
              ["Insights Produced", insights.data?.length || 0, C.amber],
              ["Active SFAs", (sfaAgents.data || []).filter((o) => o.status === "active").length, C.green],
              ["OA Packs", oaPacks.data?.length || 0, C.purple],
            ].map(([label, val, col]) => (
              <div key={label} style={{ border: `1.5px solid ${col}`, borderRadius: 6, padding: 10,
                textAlign: "center", background: "white" }}>
                <div style={{ fontSize: 20, fontWeight: "bold", color: col, fontFamily: "monospace" }}>{val}</div>
                <div style={{ fontSize: 8, color: C.slate }}>{label}</div>
              </div>
            ))}
          </div>

          {/* Training depth assessment */}
          <div style={{ border: `1px solid ${C.crimson}`, borderRadius: 6, padding: 12, background: C.crimson + "06" }}>
            <div style={{ fontWeight: "bold", fontSize: 11, color: C.crimson, marginBottom: 6 }}>
              Training Depth Assessment
            </div>
            <div style={{ fontSize: 8.5, color: C.slate, lineHeight: 1.6 }}>
              <strong>What the Military SFA run revealed:</strong> The agent completed the workflow but remained shallow.
              It read graph metadata and counted nodes, but never exercised the cipher mechanism (QID + PID + value),
              never queried DPRR's 7,335 nodes, never used the cipher mechanism to route through military PIDs,
              and generated claims from parametric knowledge instead of federation evidence.
            </div>
            <div style={{ fontSize: 8.5, color: C.slate, lineHeight: 1.6, marginTop: 8 }}>
              <strong>Three gaps in SFA guidance:</strong>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "4px 10px", fontSize: 8.5, marginTop: 4 }}>
              <Mono col={C.crimson} s={8}>1.</Mono>
              <span style={{ color: C.ink }}><strong>Indexes & TOCs as structured sources:</strong> Book indexes and tables of contents
                provide the author's own decomposition of their subject. Use these as scaffolding for concept extraction
                before reading narrative text.</span>
              <Mono col={C.crimson} s={8}>2.</Mono>
              <span style={{ color: C.ink }}><strong>Subgraph ownership:</strong> The agent does not just propose claims — it builds
                and maintains a persistent subgraph. Every run should read its owned subgraph state first, then extend it.
                The graph IS the agent's long-term memory.</span>
              <Mono col={C.crimson} s={8}>3.</Mono>
              <span style={{ color: C.ink }}><strong>Federation queries, not just inventory:</strong> The workflow says "inventory"
                but the agent must actually use the cipher key (QID + PID + value) to jump to Wikidata vertices,
                query DPRR for position data, and cross-reference Pleiades for geography.</span>
            </div>
          </div>
        </div>
      )}

      {/* ── Training Runs ── */}
      {section === "runs" && (
        <div>
          <CypherBlock query={Q_TRAINING_RUNS} label="TRAINING RUNS QUERY" />
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 8 }}>
            Each run records works consulted, insights produced, candidate assessments, and corpus gaps.
          </div>
          {(runs.data || []).map((tr) => {
            const isSelected = selectedRun === tr.run_id;
            const gaps = tr.gaps ? (typeof tr.gaps === "string" ? JSON.parse(tr.gaps) : tr.gaps) : [];
            return (
              <div key={tr.run_id} style={{ border: `1.5px solid ${C.teal}`, borderRadius: 6,
                marginBottom: 10, overflow: "hidden", background: "white" }}>
                <div onClick={() => setSelectedRun(isSelected ? null : tr.run_id)}
                  style={{ padding: "8px 12px", cursor: "pointer", display: "flex", gap: 8,
                    alignItems: "center", flexWrap: "wrap", background: isSelected ? C.teal + "08" : "white" }}>
                  <Tag label={tr.facet || "?"} fill={FACET_COLOR[tr.facet] || C.slate} s={7} />
                  <Tag label={tr.status} fill={tr.status === "completed" ? C.green : C.amber} s={7} />
                  <Mono col={C.dim} s={7}>{tr.run_id}</Mono>
                  <span style={{ fontSize: 8.5, color: C.slate, marginLeft: "auto" }}>
                    {tr.works} works · {tr.insights} insights · {tr.confirmed} confirmed · {tr.rejected} rejected
                  </span>
                </div>
                {isSelected && (
                  <div style={{ padding: "8px 12px", borderTop: `1px solid ${C.rule}`, background: "#FAFAF8" }}>
                    {tr.summary && (
                      <div style={{ fontSize: 8.5, color: C.ink, marginBottom: 8, lineHeight: 1.5 }}>
                        <strong>Summary:</strong> {tr.summary}
                      </div>
                    )}
                    {tr.model && (
                      <div style={{ fontSize: 8, color: C.dim, marginBottom: 4 }}>
                        <strong>Model:</strong> <Mono col={C.purple} s={7.5}>{tr.model}</Mono>
                      </div>
                    )}
                    {tr.decompose && (
                      <div style={{ fontSize: 8.5, color: C.crimson, marginBottom: 4 }}>
                        <strong>Decomposition recommended:</strong> {tr.decomp_reason}
                      </div>
                    )}
                    {gaps.length > 0 && (
                      <div style={{ marginTop: 6 }}>
                        <div style={{ fontSize: 8, fontWeight: "bold", color: C.crimson, marginBottom: 3 }}>
                          Corpus Gaps ({gaps.length})
                        </div>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 3 }}>
                          {gaps.map((g, i) => (
                            <span key={i} style={{ background: C.crimson + "12", color: C.crimson,
                              padding: "2px 6px", borderRadius: 3, fontSize: 7.5 }}>{g}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 6, marginTop: 8 }}>
                      {[
                        ["Works", tr.works, C.navy],
                        ["Insights", tr.insights, C.teal],
                        ["Confirmed", tr.confirmed, C.green],
                        ["Rejected", tr.rejected, C.crimson],
                      ].map(([l, v, col]) => (
                        <div key={l} style={{ textAlign: "center", padding: 4, background: col + "08",
                          borderRadius: 4 }}>
                          <div style={{ fontSize: 14, fontWeight: "bold", color: col }}>{v}</div>
                          <div style={{ fontSize: 7, color: C.dim }}>{l}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ── Insights ── */}
      {section === "insights" && (
        <div>
          <CypherBlock query={Q_TRAINING_INSIGHTS} label="TRAINING INSIGHTS QUERY" />
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 8 }}>
            Insights extracted from training runs, classified by type. Each carries evidence provenance.
          </div>
          {Object.entries(insightsByType).map(([type, items]) => (
            <div key={type} style={{ marginBottom: 12 }}>
              <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 6 }}>
                <Tag label={type.replace(/_/g, " ")} fill={TYPE_COL[type] || C.dim} s={8} />
                <span style={{ fontSize: 8, color: C.dim }}>{items.length} insights</span>
              </div>
              {items.map((ins) => (
                <div key={ins.id} style={{ border: `1px solid ${C.rule}`, borderRadius: 5,
                  marginBottom: 4, background: "white", borderLeft: `3px solid ${TYPE_COL[type] || C.dim}` }}>
                  <div style={{ padding: "6px 10px" }}>
                    <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 3 }}>
                      <span style={{ fontWeight: "bold", fontSize: 10, color: C.ink }}>{ins.label}</span>
                      <Mono col={C.dim} s={7}>{ins.id.slice(0, 8)}</Mono>
                      <span style={{ fontSize: 8, color: C.teal, fontWeight: "bold", marginLeft: "auto" }}>
                        {ins.conf?.toFixed(2)}
                      </span>
                      <Tag label={ins.status || "proposed"} fill={ins.status === "proposed" ? C.amber : C.green} s={6.5} />
                    </div>
                    {ins.evidence && (
                      <div style={{ fontSize: 8, color: C.slate, lineHeight: 1.5, marginTop: 2,
                        background: "#F5F3EE", padding: "4px 8px", borderRadius: 3 }}>
                        {ins.evidence}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* ── Subgraph Ownership ── */}
      {section === "ownership" && (() => {
        // Build facet lookup from separate queries
        const assetMap = {};
        (facetAssets.data || []).forEach((f) => { assetMap[f.facet?.toUpperCase()] = f; });
        const trainMap = {};
        (trainByFacet.data || []).forEach((t) => { trainMap[t.facet] = t; });
        // Derive facet key from agent name: SFA_MILITARY_RR → MILITARY
        const agentCards = (sfaAgents.data || []).map((a) => {
          const facetKey = a.agent.replace("SFA_", "").replace("_RR", "");
          const assets = assetMap[facetKey] || {};
          const train = trainMap[facetKey] || {};
          const total = (assets.pri || 0) + (assets.sec || 0) + (assets.corpus || 0) + (assets.oa || 0);
          const depth = total === 0 ? "empty" : total < 5 ? "shallow" : total < 20 ? "developing" : "rich";
          return { ...a, facetKey, facetLabel: assets.facet || facetKey, assets, train, depth };
        });
        const depthCol = { empty: C.crimson, shallow: C.amber, developing: C.teal, rich: C.green };

        return (
          <div>
            <CypherBlock query={Q_SFA_AGENTS} label="SFA AGENTS" />
            <div style={{ fontSize: 9, color: C.dim, marginBottom: 8 }}>
              Each SFA owns a persistent subgraph. The graph IS the agent's long-term memory.
            </div>

            {/* Agent cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 8, marginBottom: 16 }}>
              {agentCards.map((a) => {
                const col = FACET_COLOR[a.facetLabel] || C.slate;
                return (
                  <div key={a.agent} style={{ border: `1.5px solid ${col}`, borderRadius: 6, overflow: "hidden", background: "white" }}>
                    <div style={{ background: col, padding: "5px 8px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontSize: 9, fontWeight: "bold", color: "white" }}>{a.agent}</span>
                      <Tag label={a.depth} fill={depthCol[a.depth]} s={6.5} />
                    </div>
                    <div style={{ padding: "6px 8px" }}>
                      <div style={{ display: "flex", gap: 4, alignItems: "center", marginBottom: 4 }}>
                        <Tag label={a.status} fill={STATUS_COL[a.status] || C.dim} s={6.5} />
                        {a.ceiling && <Mono col={C.dim} s={7}>ceil: {a.ceiling}</Mono>}
                        {a.domain && <Mono col={C.slate} s={7}>{a.domain}</Mono>}
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: "2px 6px", fontSize: 8 }}>
                        {[
                          ["Primary SC", a.assets.pri],
                          ["Secondary SC", a.assets.sec],
                          ["Corpus Works", a.assets.corpus],
                          ["OA Packs", a.assets.oa],
                          ["Training Runs", a.train.runs],
                          ["Insights", a.train.insights],
                        ].map(([l, v]) => [
                          <span key={l + "l"} style={{ color: C.slate }}>{l}</span>,
                          <span key={l + "v"} style={{ fontWeight: "bold", textAlign: "right",
                            color: (v || 0) > 0 ? C.ink : C.dim, fontFamily: "monospace" }}>{v || 0}</span>,
                        ])}
                      </div>
                      {a.scope && <div style={{ fontSize: 7, color: C.dim, marginTop: 4, fontStyle: "italic" }}>{a.scope}</div>}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Facet asset table */}
            <div style={{ border: `1px solid ${C.rule}`, borderRadius: 6, overflow: "hidden", marginBottom: 16 }}>
              <div style={{ background: C.navy, padding: "5px 8px" }}>
                <span style={{ fontSize: 9, fontWeight: "bold", color: "white" }}>All Facets — Asset Counts</span>
              </div>
              <div style={{ maxHeight: 300, overflow: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 8 }}>
                  <thead>
                    <tr style={{ background: "#F5F3EE" }}>
                      <th style={{ padding: "3px 6px", textAlign: "left" }}>Facet</th>
                      <th style={{ padding: "3px 6px", textAlign: "right" }}>Primary SC</th>
                      <th style={{ padding: "3px 6px", textAlign: "right" }}>Secondary SC</th>
                      <th style={{ padding: "3px 6px", textAlign: "right" }}>Corpus</th>
                      <th style={{ padding: "3px 6px", textAlign: "right" }}>OA</th>
                      <th style={{ padding: "3px 6px", textAlign: "right" }}>Runs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(facetAssets.data || []).map((f) => {
                      const t = trainMap[f.facet?.toUpperCase()] || {};
                      return (
                        <tr key={f.facet} style={{ borderBottom: `1px solid ${C.rule}` }}>
                          <td style={{ padding: "3px 6px" }}>
                            <Tag label={f.facet} fill={FACET_COLOR[f.facet] || C.slate} s={7} />
                          </td>
                          {[f.pri, f.sec, f.corpus, f.oa, t.runs || 0].map((v, i) => (
                            <td key={i} style={{ padding: "3px 6px", textAlign: "right", fontFamily: "monospace",
                              fontWeight: "bold", color: v > 0 ? C.ink : C.dim }}>{v}</td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* OA Source Packs */}
            {oaPacks.data?.length > 0 && (
              <div style={{ border: `1px solid ${C.purple}`, borderRadius: 6, overflow: "hidden" }}>
                <div style={{ background: C.purple, padding: "5px 8px" }}>
                  <span style={{ fontSize: 9, fontWeight: "bold", color: "white" }}>
                    OA Source Packs ({oaPacks.data.length})
                  </span>
                </div>
                <div style={{ padding: "6px 8px", background: "white" }}>
                  {oaPacks.data.map((p) => (
                    <div key={p.pack_id} style={{ borderBottom: `1px solid ${C.rule}`, padding: "4px 0" }}>
                      <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                        <Mono col={C.purple} s={7.5}>{p.pack_id}</Mono>
                        <span style={{ fontWeight: "bold", fontSize: 9, color: C.ink }}>{p.label}</span>
                        {p.facet && <Tag label={p.facet} fill={FACET_COLOR[p.facet] || C.slate} s={6.5} />}
                      </div>
                      {p.texts && <div style={{ fontSize: 7, color: C.dim, marginTop: 1 }}>Texts: {p.texts}</div>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })()}

      {/* ── Structured Source Guidance ── */}
      {section === "guidance" && (() => {
        const GUIDANCE = [
          { title: "Indexes as Structured Data Sources", col: C.navy,
            text: "Book indexes provide the author's own decomposition. \"cos. 46 B.C.\" = compound key resolving a person uniquely. Extract index structure BEFORE reading narrative. SFA_INDEX_READER: ~70 claims/page, entity resolution via POSITION_HELD + year." },
          { title: "TOC as Decomposition Scaffold", col: C.amber,
            text: "A TOC from a domain authority gives a grounded decomposition — not invented from parametric knowledge. Cite chapter structure as evidence when proposing SubjectConcepts. E.g. CAH Vol IX: People & Generals → Senate & Enemies → Social War → Leges Sulpiciae → Sulla." },
          { title: "Subgraph Ownership & Persistence", col: C.teal,
            text: "The agent's learning MUST be written to the graph — the graph IS its long-term memory. Every run: (1) read owned subgraph state, (2) extend with claim nodes + rich edges, (3) write in graph-ready format per output contract. Claim → SUPPORTS_CREATE → SC, SUPPORTED_BY → Evidence, HAS_FACET_WEIGHT → Facet, OWNED_BY_FACET → steward." },
          { title: "Federation Queries, Not Just Inventory", col: C.purple,
            text: "Use the cipher mechanism (QID + PID + value) to jump to Wikidata vertices. Query DPRR for positions/temporal patterns. Cross-reference Pleiades for geography. Don't just count property mappings — pull actual statements from federation sources." },
          { title: "Claim-as-Subgraph Write Format", col: C.crimson,
            text: "A claim is not a string — it's a node with rich edges. Required: SUPPORTS_CREATE/REFINES → target concept, SUPPORTED_BY → evidence (provenance_type), HAS_FACET_WEIGHT → Facet (0.0-1.0), TAGGED_WITH → RepertoirePattern, OWNED_BY_FACET → steward agent." },
        ];
        return (
          <div>
            <div style={{ fontSize: 9, color: C.dim, marginBottom: 8 }}>
              Lessons from the first Military SFA run. Encode into onboarding so future agents train deeply.
            </div>
            {GUIDANCE.map((g, i) => (
              <div key={i} style={{ border: `1px solid ${g.col}`, borderRadius: 5, marginBottom: 6,
                background: "white", borderLeft: `3px solid ${g.col}` }}>
                <div style={{ padding: "6px 10px" }}>
                  <div style={{ fontWeight: "bold", fontSize: 9.5, color: g.col, marginBottom: 3 }}>
                    {i + 1}. {g.title}
                  </div>
                  <div style={{ fontSize: 8, color: C.slate, lineHeight: 1.5 }}>{g.text}</div>
                </div>
              </div>
            ))}
          </div>
        );
      })()}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB 12: GOVERNANCE — Thresholds, Policies, Validation Rules, Onboarding
// ══════════════════════════════════════════════════════════════════════════════

const Q_THRESHOLDS = `MATCH (t:SYS_Threshold)
RETURN coalesce(t.threshold_id, t.name) AS id, t.name AS name,
       t.value AS value, t.unit AS unit, t.description AS desc,
       t.rationale AS rationale, t.decision_table AS dt
ORDER BY coalesce(t.threshold_id, t.name)`;

const Q_POLICIES = `MATCH (p:SYS_Policy)
RETURN p.name AS name, p.description AS desc, p.active AS active,
       p.priority AS priority, p.rule AS rule, p.definition AS definition,
       p.decision_table AS dt, p.facet_key AS facet
ORDER BY p.name`;

const Q_VALIDATION_RULES = `MATCH (v:SYS_ValidationRule)
RETURN v.rule_id AS rid, v.name AS name, v.check_description AS check_desc,
       v.severity AS severity, v.applies_to AS applies_to,
       v.rationale AS rationale, v.adr_reference AS adr
ORDER BY v.rule_id`;

const Q_ONBOARDING = `MATCH (op:SYS_OnboardingProtocol)-[:HAS_STEP]->(s:SYS_OnboardingStep)
RETURN op.label AS protocol, op.protocol_id AS pid,
       s.step_id AS step_id, s.label AS label, s.description AS desc
ORDER BY op.protocol_id, s.step_id`;

const Q_CLAIM_STATES = `MATCH (cs:SYS_ClaimStatus)
OPTIONAL MATCH (cs)-[:CAN_TRANSITION_TO]->(next:SYS_ClaimStatus)
RETURN cs.label AS status, cs.terminal AS terminal, cs.phase AS phase,
       cs.description AS desc, collect(next.label) AS transitions
ORDER BY cs.label`;

function GovernanceTab() {
  const thresholds = useCypher(Q_THRESHOLDS);
  const policies = useCypher(Q_POLICIES);
  const rules = useCypher(Q_VALIDATION_RULES);
  const onboarding = useCypher(Q_ONBOARDING);
  const claimStates = useCypher(Q_CLAIM_STATES);
  const [section, setSection] = useState("thresholds");

  const loading = thresholds.loading || policies.loading || rules.loading || onboarding.loading || claimStates.loading;
  const err = thresholds.error || policies.error || rules.error || onboarding.error || claimStates.error;
  if (loading) return <Loader msg="Loading governance data..." />;
  if (err) return <Err msg={err} />;

  // Group onboarding by protocol
  const onboardingByProtocol = {};
  (onboarding.data || []).forEach((s) => {
    if (!onboardingByProtocol[s.protocol]) onboardingByProtocol[s.protocol] = [];
    onboardingByProtocol[s.protocol].push(s);
  });

  const SECTIONS = [
    ["thresholds", `Thresholds (${thresholds.data?.length || 0})`],
    ["policies", `Policies (${policies.data?.length || 0})`],
    ["rules", `Validation Rules (${rules.data?.length || 0})`],
    ["onboarding", `Onboarding (${onboarding.data?.length || 0} steps)`],
    ["claims", `Claim Lifecycle (${claimStates.data?.length || 0} states)`],
  ];

  return (
    <div>
      {/* Section nav */}
      <div style={{ display: "flex", gap: 0, marginBottom: 12, borderBottom: `1.5px solid ${C.rule}` }}>
        {SECTIONS.map(([k, l]) => (
          <button key={k} onClick={() => setSection(k)}
            style={{ border: "none", padding: "5px 14px", fontSize: 9.5, cursor: "pointer",
              background: "transparent", fontWeight: section === k ? "bold" : "normal",
              color: section === k ? C.navy : C.dim,
              borderBottom: section === k ? `2px solid ${C.navy}` : "2px solid transparent" }}>
            {l}
          </button>
        ))}
      </div>

      {/* ── Thresholds ── */}
      {section === "thresholds" && (
        <div>
          <CypherBlock query={Q_THRESHOLDS} label="THRESHOLDS QUERY" />
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 8 }}>
            Numeric thresholds govern agent decisions — confidence ceilings, split triggers, drift alerts, SPARQL limits.
          </div>
          <div style={{ maxHeight: 500, overflow: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 8.5 }}>
              <thead>
                <tr style={{ background: C.navy, color: "white" }}>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>ID</th>
                  <th style={{ padding: "3px 6px", textAlign: "right" }}>Value</th>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>Unit</th>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>Description / Rationale</th>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>Decision Table</th>
                </tr>
              </thead>
              <tbody>
                {thresholds.data.map((t, i) => {
                  const isSFA = (t.id || "").includes("SFA") || (t.id || "").includes("sfa");
                  return (
                    <tr key={i} style={{ borderBottom: `1px solid ${C.rule}`,
                      background: isSFA ? C.teal + "08" : "white" }}>
                      <td style={{ padding: "3px 6px", fontFamily: "monospace", color: C.teal, fontSize: 8 }}>
                        {t.id || t.name || "(unnamed)"}
                      </td>
                      <td style={{ padding: "3px 6px", textAlign: "right", fontWeight: "bold",
                        fontFamily: "monospace", color: C.ink }}>
                        {t.value != null ? t.value : "-"}
                      </td>
                      <td style={{ padding: "3px 6px", color: C.dim, fontSize: 7.5 }}>{t.unit || ""}</td>
                      <td style={{ padding: "3px 6px", color: C.slate, maxWidth: 300 }}>
                        {t.desc || t.rationale || ""}
                      </td>
                      <td style={{ padding: "3px 6px", fontFamily: "monospace", color: C.purple, fontSize: 7.5 }}>
                        {t.dt || ""}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── Policies ── */}
      {section === "policies" && (
        <div>
          <CypherBlock query={Q_POLICIES} label="POLICIES QUERY" />
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 8 }}>
            Hard rules that constrain agent behavior. Active policies are enforced; inactive are advisory.
          </div>
          {policies.data.map((p) => {
            const isActive = p.active === true || p.active === "true";
            return (
              <div key={p.name} style={{ border: `1px solid ${C.rule}`, borderRadius: 5,
                marginBottom: 4, borderLeft: `3px solid ${isActive ? C.green : C.dim}` }}>
                <div style={{ padding: "5px 10px", background: "white",
                  display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                  <Tag label={isActive ? "active" : "inactive"}
                    fill={isActive ? C.green : C.dim} s={7} />
                  <span style={{ fontWeight: "bold", fontSize: 10, color: C.ink }}>{p.name}</span>
                  {p.priority && <Mono col={C.amber} s={7.5}>P{p.priority}</Mono>}
                  {p.facet && <Tag label={p.facet} fill={FACET_COLOR[p.facet] || C.slate} s={7} />}
                  {p.dt && <Mono col={C.purple} s={7.5}>{p.dt}</Mono>}
                </div>
                {(p.desc || p.rule || p.definition) && (
                  <div style={{ padding: "4px 10px", background: "#FAFAF8",
                    borderTop: `1px solid ${C.rule}`, fontSize: 8.5, color: C.slate }}>
                    {p.desc && <div>{p.desc}</div>}
                    {p.rule && <div style={{ marginTop: 2 }}><strong>Rule:</strong> {p.rule}</div>}
                    {p.definition && <div style={{ marginTop: 2 }}><strong>Definition:</strong> {p.definition}</div>}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ── Validation Rules ── */}
      {section === "rules" && (
        <div>
          <CypherBlock query={Q_VALIDATION_RULES} label="VALIDATION RULES QUERY" />
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 8 }}>
            Validation rules that SFA output is checked against before graph writes.
          </div>
          {rules.data.map((r) => {
            const sevCol = r.severity === "error" ? C.crimson
              : r.severity === "warning" ? C.amber : C.dim;
            return (
              <div key={r.rid} style={{ border: `1px solid ${C.rule}`, borderRadius: 5,
                marginBottom: 4, borderLeft: `3px solid ${sevCol}` }}>
                <div style={{ padding: "5px 10px", background: "white",
                  display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                  <Mono col={C.teal} s={8}>{r.rid}</Mono>
                  <span style={{ fontWeight: "bold", fontSize: 10, color: C.ink }}>{r.name}</span>
                  {r.severity && <Tag label={r.severity} fill={sevCol} s={7} />}
                  {r.applies_to && <Mono col={C.purple} s={7.5}>{r.applies_to}</Mono>}
                  {r.adr && <Mono col={C.navy} s={7.5}>{r.adr}</Mono>}
                </div>
                {(r.check_desc || r.rationale) && (
                  <div style={{ padding: "4px 10px", background: "#FAFAF8",
                    borderTop: `1px solid ${C.rule}`, fontSize: 8.5, color: C.slate }}>
                    {r.check_desc && <div><strong>Check:</strong> {r.check_desc}</div>}
                    {r.rationale && <div style={{ marginTop: 2 }}><strong>Rationale:</strong> {r.rationale}</div>}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ── Onboarding ── */}
      {section === "onboarding" && (
        <div>
          <CypherBlock query={Q_ONBOARDING} label="ONBOARDING QUERY" />
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 8 }}>
            Step-by-step protocols for new agents and discipline bootstrapping. Follow in order.
          </div>
          {Object.entries(onboardingByProtocol).map(([protocol, steps]) => (
            <div key={protocol} style={{ border: `1.5px solid ${C.amber}`, borderRadius: 6,
              marginBottom: 12, overflow: "hidden" }}>
              <div style={{ background: C.amber, padding: "6px 12px" }}>
                <span style={{ fontSize: 11, fontWeight: "bold", color: "white" }}>{protocol}</span>
                <span style={{ fontSize: 9, color: "rgba(255,255,255,0.7)", marginLeft: 8 }}>
                  {steps.length} steps
                </span>
              </div>
              <div style={{ padding: "8px 12px", background: "white" }}>
                {steps.map((s, i) => (
                  <div key={s.step_id} style={{ display: "flex", gap: 10, marginBottom: 8,
                    alignItems: "flex-start" }}>
                    <div style={{ background: C.amber, color: "white", borderRadius: "50%",
                      width: 22, height: 22, display: "flex", alignItems: "center",
                      justifyContent: "center", fontSize: 9, fontWeight: "bold", flexShrink: 0 }}>
                      {i + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: "bold", fontSize: 9.5, color: C.ink }}>{s.label}</div>
                      <div style={{ fontSize: 7.5, color: C.dim, fontFamily: "monospace" }}>{s.step_id}</div>
                      {s.desc && <div style={{ fontSize: 8, color: C.slate, marginTop: 2 }}>{s.desc}</div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Claim Lifecycle ── */}
      {section === "claims" && (
        <div>
          <CypherBlock query={Q_CLAIM_STATES} label="CLAIM STATE MACHINE QUERY" />
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 10 }}>
            Every SFA output enters as a Claim with status "Proposed". Transitions are governed by decision tables
            and human review. Terminal states have no outgoing transitions.
          </div>

          {/* Visual state machine */}
          <div style={{ background: C.ink, borderRadius: 8, padding: 16, marginBottom: 12 }}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
              {(claimStates.data || []).map((cs) => {
                const isTerminal = cs.terminal === true || cs.terminal === "true";
                const stCol = cs.status?.includes("Rejected") || cs.status === "Retracted" ? C.crimson
                  : cs.status === "Promoted" ? C.green
                  : cs.status === "Superseded" ? C.dim
                  : cs.status === "Reviewed (Approved)" ? C.teal
                  : C.amber;
                return (
                  <div key={cs.status} style={{ background: stCol, borderRadius: 8, padding: "8px 12px",
                    minWidth: 120, textAlign: "center", border: isTerminal ? "2px solid white" : "none" }}>
                    <div style={{ fontSize: 9, fontWeight: "bold", color: "white" }}>{cs.status}</div>
                    {isTerminal && <div style={{ fontSize: 7, color: "rgba(255,255,255,0.6)" }}>terminal</div>}
                    {cs.transitions?.length > 0 && (
                      <div style={{ marginTop: 4 }}>
                        {cs.transitions.filter(Boolean).map((t) => (
                          <div key={t} style={{ fontSize: 7, color: "rgba(255,255,255,0.7)" }}>
                            {"\u2192"} {t}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            <div style={{ textAlign: "center", marginTop: 10, fontSize: 8, color: C.dim, fontStyle: "italic" }}>
              White border = terminal state (no further transitions)
            </div>
          </div>

          {/* Table view */}
          <div style={{ maxHeight: 300, overflow: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 8.5 }}>
              <thead>
                <tr style={{ background: C.navy, color: "white" }}>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>Status</th>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>Phase</th>
                  <th style={{ padding: "3px 6px", textAlign: "center" }}>Terminal</th>
                  <th style={{ padding: "3px 6px", textAlign: "left" }}>Can transition to</th>
                </tr>
              </thead>
              <tbody>
                {(claimStates.data || []).map((cs) => (
                  <tr key={cs.status} style={{ borderBottom: `1px solid ${C.rule}` }}>
                    <td style={{ padding: "3px 6px", fontWeight: "bold", color: C.ink }}>{cs.status}</td>
                    <td style={{ padding: "3px 6px", color: C.slate }}>{cs.phase || ""}</td>
                    <td style={{ padding: "3px 6px", textAlign: "center", color: cs.terminal ? C.crimson : C.green }}>
                      {cs.terminal ? "yes" : "no"}
                    </td>
                    <td style={{ padding: "3px 6px", color: C.teal, fontFamily: "monospace", fontSize: 8 }}>
                      {cs.transitions?.filter(Boolean).join(", ") || "(none)"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// ROOT APP
// ══════════════════════════════════════════════════════════════════════════════
const TABS = [
  ["root", "Root Tree"],
  ["schema", "Schema"],
  ["federation", "Federation"],
  ["facets", "Facets"],
  ["decisions", "Decision Tables"],
  ["disciplines", "Disciplines"],
  ["agents", "Agents"],
  ["governance", "Governance"],
  ["pipeline", "Pipeline"],
  ["contract", "Contract"],
  ["training", "Training"],
  ["metrics", "Metrics"],
];

export default function ChrystallumSystemMap() {
  const [tab, setTab] = useState("root");

  return (
    <div style={{ fontFamily: "Georgia,serif", background: C.paper, minHeight: "100vh", padding: 16 }}>
      {/* Header */}
      <div style={{ borderBottom: `2px solid ${C.ink}`, paddingBottom: 10, marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 10, flexWrap: "wrap" }}>
          <span style={{ fontSize: 10, fontWeight: "bold", color: C.dim, letterSpacing: 3,
            textTransform: "uppercase", fontFamily: "Arial,sans-serif" }}>CHRYSTALLUM</span>
          <span style={{ fontSize: 15, fontWeight: "bold", color: C.ink }}>System Map</span>
          <span style={{ fontSize: 9, color: C.teal, fontFamily: "Arial,sans-serif" }}>realtime from Neo4j</span>
        </div>
        <div style={{ fontSize: 9, color: C.slate, marginTop: 3, fontFamily: "Arial,sans-serif" }}>
          Self-describing federated knowledge graph. All data below is live — queried at render time.
          Every Cypher query shown and copyable. No hardcoded counts.
        </div>
      </div>

      {/* Nav */}
      <div style={{ display: "flex", gap: 0, marginBottom: 12, borderBottom: `2px solid ${C.ink}`,
        fontFamily: "Arial,sans-serif", flexWrap: "wrap" }}>
        {TABS.map(([k, l]) => (
          <button key={k} onClick={() => setTab(k)}
            style={{ border: "none", padding: "6px 14px", fontSize: 10, cursor: "pointer",
              background: "transparent", fontWeight: tab === k ? "bold" : "normal",
              color: tab === k ? C.ink : C.dim,
              borderBottom: tab === k ? `3px solid ${C.ink}` : "3px solid transparent" }}>
            {l}
          </button>
        ))}
      </div>

      {/* Content */}
      {tab === "root" && <RootTreeTab />}
      {tab === "schema" && <SchemaTab />}
      {tab === "federation" && <FederationTab />}
      {tab === "facets" && <FacetTab />}
      {tab === "decisions" && <DecisionTableTab />}
      {tab === "disciplines" && <DisciplineTab />}
      {tab === "agents" && <AgentTab />}
      {tab === "governance" && <GovernanceTab />}
      {tab === "pipeline" && <PipelineTab />}
      {tab === "contract" && <ContractTab />}
      {tab === "training" && <TrainingTab />}
      {tab === "metrics" && <MetricsTab />}
    </div>
  );
}
