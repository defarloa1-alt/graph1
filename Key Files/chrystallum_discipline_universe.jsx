import { useState, useMemo, useEffect } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — DISCIPLINE TAXONOMY TREE                                    ║
// ║  Source: output/discipline_taxonomy.csv (Wikidata SPARQL harvest)           ║
// ║  1,611 disciplines · subclass_of hierarchy · verified authority IDs         ║
// ║                                                                             ║
// ║  NO LLM-generated data. Every QID, LCSH, LCC, GND comes from Wikidata.    ║
// ║  Facet assignments are NOT baked in — that's a separate reasoning step.    ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  ink:"#0D1117", paper:"#F7F4EF", dim:"#8B8680", rule:"#D4CEC6",
  teal:"#1A7A6E", amber:"#B5860D", crimson:"#8B1A1A", navy:"#1A3A5C",
  green:"#1E6B3C", purple:"#5B2D8E", gold:"#C9A227", slate:"#4A5568",
  orange:"#B45309", rose:"#9B2335", cyan:"#0E7490", lime:"#3D6B21",
};

// ── FACET COLORS ────────────────────────────────────────────────────────────
const FACET_COLORS = {
  ARCHAEOLOGICAL: "#8B4513", ARTISTIC: "#9B2335", BIOGRAPHIC: "#6B46C1",
  COMMUNICATION: "#0E7490", CULTURAL: "#B45309", DEMOGRAPHIC: "#3D6B21",
  DIPLOMATIC: "#1A3A5C", ECONOMIC: "#B5860D", ENVIRONMENTAL: "#1E6B3C",
  GEOGRAPHIC: "#1A7A6E", INTELLECTUAL: "#5B2D8E", LINGUISTIC: "#0E7490",
  MILITARY: "#8B1A1A", POLITICAL: "#1A3A5C", RELIGIOUS: "#C9A227",
  SCIENTIFIC: "#1A7A6E", SOCIAL: "#B45309", TECHNOLOGICAL: "#4A5568",
};

// ── VERIFIED ENDPOINTS — agent-tested, structured data back ─────────────────
// Status: OPEN = no auth needed, KEY = free registration, RESTRICTED = blocked
const ENDPOINTS = [
  { name:"OpenAlex",       status:"KEY",   color:C.teal,
    api:"https://api.openalex.org/concepts/{oa_id}",
    note:"Free API key required since Feb 2026. Concepts, works, journals. 100k req/day." },
  { name:"Open Library",   status:"OPEN",  color:C.navy,
    api:"https://openlibrary.org/subjects/{slug}.json?limit=50",
    note:"No auth. Books by subject. Rate: 1-3 req/sec." },
  { name:"LCSH Authority", status:"OPEN",  color:C.purple,
    api:"https://id.loc.gov/authorities/subjects/{lcsh}.json",
    note:"No auth. SKOS linked data. Subject headings, broader/narrower terms." },
  { name:"DOAJ",           status:"OPEN",  color:C.amber,
    api:"https://doaj.org/api/search/journals/{query}",
    note:"No auth. OA journals and articles. 2 req/sec." },
  { name:"Zenodo",         status:"OPEN",  color:C.lime,
    api:"https://zenodo.org/api/records?q={query}&type=publication",
    note:"No auth for reads. Research records, datasets, preprints." },
  { name:"Europeana",      status:"KEY",   color:C.orange,
    api:"https://api.europeana.eu/record/v2/search.json?query={query}",
    note:"Free API key. 50M+ cultural heritage objects." },
  { name:"Internet Archive", status:"OPEN", color:C.amber,
    api:"https://archive.org/metadata/{identifier}",
    note:"Metadata only (no auth). Full-text access varies by item rights." },
  { name:"Perseus (CTS)",  status:"OPEN",  color:C.crimson,
    api:"https://scaife-cts.perseus.org/api/cts?request=GetPassage&urn={urn}",
    note:"XML only. Classical texts. Server can be flaky — GitHub TEI dumps more reliable." },
  { name:"HathiTrust",     status:"OPEN",  color:C.orange,
    api:"https://catalog.hathitrust.org/api/volumes/brief/oclc/{oclc}.json",
    note:"Bib lookup only (by OCLC/LCCN/ISBN). No keyword search. No full-text without auth." },
];

const REMOVED_ENDPOINTS = [
  { name:"Google Scholar",  reason:"No API. CAPTCHA. Hostile to agents." },
  { name:"JSTOR",           reason:"Institutional paywall. No public API." },
  { name:"Open Syllabus",   reason:"403 on API. Auth required, not publicly documented." },
  { name:"WorldCat Search", reason:"Search API shut down Jan 2025. Entities API has limited free tier." },
];

// ── NEO4J CONFIG ─────────────────────────────────────────────────────────────
const NEO4J_CONFIG = {
  url: import.meta.env?.VITE_NEO4J_URL || "neo4j+s://your-aura-instance.databases.neo4j.io",
  user: import.meta.env?.VITE_NEO4J_USER || "neo4j",
  password: import.meta.env?.VITE_NEO4J_PASSWORD || "",
};
const CYPHER_API_URL = import.meta.env?.VITE_CYPHER_API_URL || null;

async function fetchCypher(query, params = {}) {
  if (CYPHER_API_URL) {
    const resp = await fetch(CYPHER_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, params }),
    });
    if (resp.ok) {
      const json = await resp.json();
      return json.rows || [];
    }
    console.warn(`Railway API ${resp.status}, falling back to Neo4j proxy`);
  }
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

// ── CYPHER QUERY ─────────────────────────────────────────────────────────────
const Q_DISCIPLINES = `MATCH (d:Discipline) WHERE d.tier = 'backbone'
OPTIONAL MATCH (d)-[hf:HAS_FACET]->(f:Facet) WHERE hf.primary = true
RETURN d.qid AS qid, d.label AS label,
       d.lcsh_id AS lcsh_id, d.lcc AS lcc, d.gnd_id AS gnd_id,
       d.fast_id AS fast_id, d.ddc AS ddc, d.aat_id AS aat_id,
       d.kbpedia_id AS kbpedia_id, d.babelnet_id AS babelnet_id,
       d.subclass_of AS subclass_of, d.subclass_of_label AS subclass_of_label,
       f.label AS primary_facet
ORDER BY d.label`;

// ── HOOKS ────────────────────────────────────────────────────────────────────
function useCypher(query) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCypher(query)
      .then(rows => { setData(rows); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  return { data, loading, error };
}

// ── TREE BUILDER ─────────────────────────────────────────────────────────────
function buildTree(rows) {
  const byQid = {};
  rows.forEach(r => { byQid[r.qid] = { ...r, children: [] }; });

  const trueRoots = [];
  const orphans = [];

  rows.forEach(r => {
    const parentQids = (r.subclass_of || "").split("|").map(s => s.trim()).filter(Boolean);
    let placed = false;
    for (const pq of parentQids) {
      if (byQid[pq] && pq !== r.qid) { // avoid self-reference
        byQid[pq].children.push(byQid[r.qid]);
        placed = true;
        break;
      }
    }
    if (!placed) {
      if (parentQids.length === 0) {
        trueRoots.push(byQid[r.qid]);
      } else {
        orphans.push(byQid[r.qid]);
      }
    }
  });

  // Sort children alphabetically, recursively
  const sortChildren = (node) => {
    node.children.sort((a, b) => (a.label || "").localeCompare(b.label || ""));
    node.children.forEach(sortChildren);
  };
  trueRoots.sort((a, b) => (a.label || "").localeCompare(b.label || ""));
  trueRoots.forEach(sortChildren);
  orphans.sort((a, b) => (a.label || "").localeCompare(b.label || ""));
  orphans.forEach(sortChildren);

  // Count nested nodes
  const countDescendants = (node) => {
    let c = node.children.length;
    node.children.forEach(ch => { c += countDescendants(ch); });
    return c;
  };
  const nestedCount = trueRoots.reduce((s, r) => s + countDescendants(r), 0) +
                      orphans.reduce((s, r) => s + countDescendants(r), 0);

  return { trueRoots, orphans, byQid, nestedCount };
}

// ── UI PRIMITIVES ────────────────────────────────────────────────────────────
function Tag({ label, fill, s = 8 }) {
  return <span style={{ background: fill + "18", border: `1px solid ${fill}`, borderRadius: 10,
    padding: "1px 8px", fontSize: s, color: fill, fontWeight: "bold", whiteSpace: "nowrap",
    display: "inline-block", margin: 1 }}>{label}</span>;
}
function Mono({ children, col = C.teal }) {
  return <code style={{ fontFamily: "monospace", color: col, fontSize: 9.5, background: col + "12",
    padding: "1px 5px", borderRadius: 3 }}>{children}</code>;
}

// ── AUTHORITY BADGES ─────────────────────────────────────────────────────────
function AuthBadges({ row }) {
  const badges = [];
  if (row.primary_facet) badges.push({ label: row.primary_facet, col: FACET_COLORS[row.primary_facet] || C.slate, isFacet: true });
  if (row.lcsh_id) badges.push({ label: `LCSH: ${row.lcsh_id.split("|")[0]}`, col: C.purple });
  if (row.lcc) badges.push({ label: `LCC: ${row.lcc.split("|")[0]}`, col: C.amber });
  if (row.gnd_id) badges.push({ label: `GND: ${row.gnd_id}`, col: C.teal });
  if (row.fast_id) badges.push({ label: `FAST: ${row.fast_id}`, col: C.navy });
  if (row.ddc) badges.push({ label: `DDC: ${row.ddc.split("|")[0]}`, col: C.slate });
  if (row.aat_id) badges.push({ label: `AAT: ${row.aat_id}`, col: C.orange });
  if (row.kbpedia_id) badges.push({ label: `KBpedia: ${row.kbpedia_id}`, col: C.cyan });
  if (badges.length === 0) return null;
  return (
    <span style={{ display: "inline-flex", gap: 3, marginLeft: 6 }}>
      {badges.map(b => <Tag key={b.label} label={b.label} fill={b.col} s={7} />)}
    </span>
  );
}

// ── TREE NODE ────────────────────────────────────────────────────────────────
function TreeNode({ node, depth = 0, expanded, toggleExpand, searchMatch }) {
  const hasChildren = node.children.length > 0;
  const isOpen = expanded[node.qid];
  const isMatch = searchMatch ? searchMatch.has(node.qid) : true;
  const hasAuthority = node.lcsh_id || node.lcc || node.gnd_id || node.fast_id;

  if (!isMatch && !hasChildren) return null;
  // If searching, only show nodes that match or have matching descendants
  if (searchMatch && !isMatch) {
    const hasMatchingChild = node.children.some(c =>
      searchMatch.has(c.qid) || c.children.some(gc => searchMatch.has(gc.qid))
    );
    if (!hasMatchingChild) return null;
  }

  return (
    <div style={{ marginLeft: depth * 16 }}>
      <div
        onClick={() => hasChildren && toggleExpand(node.qid)}
        style={{
          padding: "3px 8px", display: "flex", alignItems: "center", gap: 6,
          cursor: hasChildren ? "pointer" : "default",
          borderLeft: `2px solid ${hasAuthority ? C.green : C.rule}`,
          background: isMatch && searchMatch ? C.teal + "08" : "transparent",
          borderRadius: 2, marginBottom: 1,
        }}
      >
        {/* expand arrow */}
        <span style={{ width: 12, fontSize: 9, color: C.dim, fontFamily: "monospace" }}>
          {hasChildren ? (isOpen ? "▼" : "▶") : " "}
        </span>

        {/* QID */}
        <Mono col={C.slate}>{node.qid}</Mono>

        {/* label */}
        <span style={{
          fontWeight: hasChildren ? "bold" : "normal",
          color: hasAuthority ? C.ink : C.dim,
          fontSize: 10.5,
        }}>
          {node.label || node.qid}
        </span>

        {/* child count */}
        {hasChildren && (
          <span style={{ fontSize: 8, color: C.dim, background: C.dim + "12",
            borderRadius: 8, padding: "0 5px" }}>
            {node.children.length}
          </span>
        )}

        {/* authority badges */}
        <AuthBadges row={node} />

        {/* parent info */}
        {node.subclass_of_label && (
          <span style={{ fontSize: 8, color: C.dim, marginLeft: "auto" }}>
            ⊂ {node.subclass_of_label.split("|")[0]}
          </span>
        )}
      </div>

      {/* children */}
      {isOpen && node.children.map(child => (
        <TreeNode key={child.qid} node={child} depth={depth + 1}
          expanded={expanded} toggleExpand={toggleExpand} searchMatch={searchMatch} />
      ))}
    </div>
  );
}

// ── STATS PANEL ──────────────────────────────────────────────────────────────
function Stats({ rows }) {
  const hasLcsh = rows.filter(r => r.lcsh_id).length;
  const hasLcc = rows.filter(r => r.lcc).length;
  const hasGnd = rows.filter(r => r.gnd_id).length;
  const hasFast = rows.filter(r => r.fast_id).length;
  const hasParent = rows.filter(r => r.subclass_of).length;
  const hasFacet = rows.filter(r => r.primary_facet).length;

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 8, marginBottom: 14 }}>
      {[
        [rows.length, "Total Disciplines", C.navy, "backbone tier (live)"],
        [hasFacet, "Have Facet", C.purple, "HAS_FACET primary"],
        [hasLcsh, "Have LCSH", C.purple, "verified sh-IDs"],
        [hasLcc, "Have LCC", C.amber, "classification codes"],
        [hasGnd, "Have GND", C.teal, "German authority"],
        [hasFast, "Have FAST", C.navy, "OCLC faceted"],
        [hasParent, "In Hierarchy", C.green, "subclass_of linked"],
      ].map(([n, l, col, sub]) => (
        <div key={l} style={{ background: "white", border: `2px solid ${col}`, borderRadius: 8,
          padding: 10, textAlign: "center" }}>
          <div style={{ fontSize: 22, fontWeight: "bold", color: col }}>{n}</div>
          <div style={{ fontSize: 10, fontWeight: "bold", color: C.ink }}>{l}</div>
          <div style={{ fontSize: 8, color: C.dim }}>{sub}</div>
        </div>
      ))}
    </div>
  );
}

// ── ENDPOINT PANEL ───────────────────────────────────────────────────────────
function EndpointPanel() {
  return (
    <div style={{ background: "white", border: `1.5px solid ${C.purple}`, borderRadius: 8,
      padding: 14, marginBottom: 14 }}>
      <div style={{ fontWeight: "bold", color: C.purple, fontSize: 12, marginBottom: 10 }}>
        Verified Agent Endpoints ({ENDPOINTS.length} usable)
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, marginBottom: 12 }}>
        {ENDPOINTS.map(ep => (
          <div key={ep.name} style={{ borderLeft: `3px solid ${ep.color}`, paddingLeft: 8 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
              <span style={{ fontSize: 10, fontWeight: "bold", color: ep.color }}>{ep.name}</span>
              <Tag label={ep.status} fill={ep.status === "OPEN" ? C.green : C.amber} s={7} />
            </div>
            <div style={{ fontSize: 8, color: C.slate, marginBottom: 2 }}>{ep.note}</div>
            <code style={{ fontSize: 7.5, color: C.dim }}>{ep.api.replace("https://", "").split("/")[0]}</code>
          </div>
        ))}
      </div>

      <div style={{ borderTop: `1px solid ${C.rule}`, paddingTop: 8 }}>
        <div style={{ fontSize: 9, fontWeight: "bold", color: C.crimson, marginBottom: 4 }}>
          Removed (not agent-accessible)
        </div>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {REMOVED_ENDPOINTS.map(ep => (
            <div key={ep.name} style={{ fontSize: 8.5, color: C.dim }}>
              <span style={{ textDecoration: "line-through" }}>{ep.name}</span>
              {" — "}{ep.reason}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── MAIN COMPONENT ───────────────────────────────────────────────────────────
export default function DisciplineUniverse_Root() {
  const { data, loading, error } = useCypher(Q_DISCIPLINES);
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState({});
  const [view, setView] = useState("tree");
  const [facetFilter, setFacetFilter] = useState("");
  const [defaultExpanded, setDefaultExpanded] = useState(false);

  const tree = useMemo(() => data ? buildTree(data) : null, [data]);

  // Default: expand top 2 levels on first load
  useEffect(() => {
    if (tree && !defaultExpanded) {
      const toExpand = {};
      [...tree.trueRoots, ...tree.orphans].forEach(r => {
        toExpand[r.qid] = true;
        r.children.forEach(c => { toExpand[c.qid] = true; });
      });
      toExpand.__orphans = true;
      setExpanded(toExpand);
      setDefaultExpanded(true);
    }
  }, [tree, defaultExpanded]);

  // Facet list from data
  const facetList = useMemo(() => {
    if (!data) return [];
    const counts = {};
    data.forEach(r => {
      if (r.primary_facet) {
        counts[r.primary_facet] = (counts[r.primary_facet] || 0) + 1;
      }
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [data]);

  // Search: find matching QIDs (text search + facet filter)
  const searchMatch = useMemo(() => {
    const hasSearch = search && search.length > 0;
    const hasFacet = facetFilter && facetFilter.length > 0;
    if (!hasSearch && !hasFacet) return null;
    if (!data) return null;
    const s = (search || "").toLowerCase();
    const matches = new Set();
    data.forEach(r => {
      const textMatch = !hasSearch || (
        (r.label || "").toLowerCase().includes(s) ||
        (r.qid || "").toLowerCase().includes(s) ||
        (r.lcsh_id || "").toLowerCase().includes(s) ||
        (r.gnd_id || "").toLowerCase().includes(s) ||
        (r.primary_facet || "").toLowerCase().includes(s)
      );
      const facetMatch = !hasFacet || (r.primary_facet === facetFilter);
      if (textMatch && facetMatch) {
        matches.add(r.qid);
      }
    });
    return matches;
  }, [search, facetFilter, data]);

  // Auto-expand parents of search matches
  useMemo(() => {
    if (!searchMatch || !tree) return;
    const toExpand = {};
    const expandParentsOf = (qid) => {
      for (const row of data) {
        if (row.qid === qid && row.subclass_of) {
          const parents = row.subclass_of.split("|").map(s => s.trim());
          for (const p of parents) {
            if (tree.byQid[p]) {
              toExpand[p] = true;
              expandParentsOf(p);
            }
          }
        }
      }
    };
    searchMatch.forEach(qid => expandParentsOf(qid));
    if (Object.keys(toExpand).length > 0) {
      setExpanded(prev => ({ ...prev, ...toExpand }));
    }
  }, [searchMatch, tree, data]);

  const toggleExpand = (qid) => {
    setExpanded(prev => ({ ...prev, [qid]: !prev[qid] }));
  };

  const expandAll = () => {
    if (!data) return;
    const all = {};
    data.forEach(r => {
      if ((r.subclass_of || "").split("|").some(p => p.trim())) return;
      // Only expand roots initially — or expand all
    });
    data.forEach(r => { all[r.qid] = true; });
    setExpanded(all);
  };

  const collapseAll = () => setExpanded({});

  // Expand just top 2 levels
  const expandTopLevels = () => {
    if (!tree) return;
    const toExpand = {};
    [...tree.trueRoots, ...tree.orphans].forEach(r => {
      toExpand[r.qid] = true;
      r.children.forEach(c => { toExpand[c.qid] = true; });
    });
    setExpanded(toExpand);
  };

  if (loading) return (
    <div style={{ padding: 40, color: C.dim, fontSize: 12, fontStyle: "italic" }}>
      Loading disciplines from Neo4j...
    </div>
  );

  if (error || !data || !tree) return (
    <div style={{ padding: 20, fontFamily: "system-ui" }}>
      <div style={{ color: C.crimson, fontSize: 12, marginBottom: 10, background: C.crimson + "10",
        border: `1px solid ${C.crimson}`, borderRadius: 6, padding: 12 }}>
        Could not load disciplines from Neo4j.
        {error && <div style={{ marginTop: 4, fontSize: 10 }}>{error}</div>}
      </div>
    </div>
  );

  const VIEWS = [
    ["tree", "Taxonomy Tree"],
    ["facets", "By Facet (18)"],
    ["endpoints", "Verified Endpoints"],
    ["flat", "Flat List (authority coverage)"],
  ];

  return (
    <div style={{ fontFamily: "Georgia,'Times New Roman',serif", background: "#F7F4EF",
      minHeight: "100vh", padding: 16 }}>
      {/* header */}
      <div style={{ borderBottom: `2px solid ${C.ink}`, paddingBottom: 10, marginBottom: 14 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
          <span style={{ fontSize: 11, fontWeight: "bold", color: C.dim, letterSpacing: 3,
            textTransform: "uppercase", fontFamily: "Arial,sans-serif" }}>CHRYSTALLUM</span>
          <span style={{ fontSize: 16, fontWeight: "bold", color: C.ink }}>
            Discipline Taxonomy
          </span>
          <span style={{ color: C.dim, fontSize: 9, marginLeft: "auto", fontFamily: "Arial,sans-serif" }}>
            {data.length} disciplines · Neo4j live · verified authority IDs
          </span>
        </div>
        <div style={{ fontSize: 9, color: C.slate, marginTop: 4, fontStyle: "italic",
          fontFamily: "Arial,sans-serif" }}>
          Source: Neo4j Aura (live) — backbone Discipline nodes (Q11862829 academic discipline,
          P279/P527 subclass expansion). Facet assignments from HAS_FACET edges (primary=true).
        </div>
      </div>

      {/* tabs */}
      <div style={{ display: "flex", gap: 0, marginBottom: 14, borderBottom: `2px solid ${C.ink}`,
        fontFamily: "Arial,sans-serif" }}>
        {VIEWS.map(([k, l]) => (
          <button key={k} onClick={() => setView(k)} style={{
            border: "none", padding: "7px 16px", fontSize: 10, cursor: "pointer",
            background: "transparent", fontWeight: view === k ? "bold" : "normal",
            color: view === k ? C.ink : C.dim,
            borderBottom: view === k ? `3px solid ${C.ink}` : "3px solid transparent",
            letterSpacing: .4,
          }}>{l}</button>
        ))}
      </div>

      {/* stats */}
      <Stats rows={data} />

      {view === "endpoints" && <EndpointPanel />}

      {view === "tree" && (
        <div>
          {/* controls */}
          <div style={{ display: "flex", gap: 8, marginBottom: 10, alignItems: "center",
            fontFamily: "Arial,sans-serif" }}>
            <input value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Search by name, QID, LCSH, LCC..."
              style={{ border: `1px solid ${C.rule}`, borderRadius: 6, padding: "5px 10px",
                fontSize: 10, fontFamily: "inherit", width: 240 }} />
            {(search || facetFilter) && (
              <span style={{ fontSize: 9, color: C.teal }}>
                {searchMatch ? searchMatch.size : 0} matches
              </span>
            )}
            <select value={facetFilter} onChange={e => setFacetFilter(e.target.value)}
              style={{ border: `1px solid ${C.rule}`, borderRadius: 6, padding: "4px 8px",
                fontSize: 10, fontFamily: "Arial,sans-serif", background: facetFilter ? FACET_COLORS[facetFilter] + "18" : "white",
                color: facetFilter ? FACET_COLORS[facetFilter] || C.ink : C.dim }}>
              <option value="">All facets</option>
              {facetList.map(([f, cnt]) => (
                <option key={f} value={f}>{f} ({cnt})</option>
              ))}
            </select>
            {facetFilter && (
              <button onClick={() => setFacetFilter("")} style={{ ...btnStyle, color: C.crimson }}>✕</button>
            )}
            <div style={{ marginLeft: "auto", display: "flex", gap: 4 }}>
              <button onClick={expandTopLevels} style={btnStyle}>Top 2 levels</button>
              <button onClick={expandAll} style={btnStyle}>Expand all</button>
              <button onClick={collapseAll} style={btnStyle}>Collapse all</button>
            </div>
          </div>

          {/* tree */}
          <div style={{ background: "white", border: `1px solid ${C.rule}`, borderRadius: 6,
            padding: 8, maxHeight: "70vh", overflow: "auto" }}>
            <div style={{ fontSize: 8, color: C.dim, marginBottom: 6 }}>
              {tree.trueRoots.length} root nodes · {tree.orphans.length} orphans
              (parent outside harvest) · {tree.nestedCount} nested · green border = has authority IDs
            </div>

            {/* True roots — no parent in Wikidata */}
            {tree.trueRoots.map(root => (
              <TreeNode key={root.qid} node={root} depth={0}
                expanded={expanded} toggleExpand={toggleExpand} searchMatch={searchMatch} />
            ))}

            {/* Orphans — have parent but parent not in CSV */}
            {tree.orphans.length > 0 && (
              <div style={{ marginTop: 8, borderTop: `1px solid ${C.rule}`, paddingTop: 6 }}>
                <div
                  onClick={() => setExpanded(prev => ({ ...prev, __orphans: !prev.__orphans }))}
                  style={{ fontSize: 9, fontWeight: "bold", color: C.dim, cursor: "pointer",
                    marginBottom: 4 }}>
                  {expanded.__orphans ? "▼" : "▶"} Orphans — parent QID outside harvest
                  ({tree.orphans.length})
                </div>
                {expanded.__orphans && tree.orphans.map(root => (
                  <TreeNode key={root.qid} node={root} depth={0}
                    expanded={expanded} toggleExpand={toggleExpand} searchMatch={searchMatch} />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {view === "facets" && (
        <div>
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 8, fontFamily: "Arial,sans-serif" }}>
            {facetList.reduce((s, [, c]) => s + c, 0)} disciplines grouped by primary facet assignment.
            {" "}{data.length - facetList.reduce((s, [, c]) => s + c, 0)} unassigned.
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
            {facetList.map(([facet, cnt]) => {
              const col = FACET_COLORS[facet] || C.slate;
              const discs = data.filter(r => r.primary_facet === facet)
                .sort((a, b) => (a.label || "").localeCompare(b.label || ""));
              return (
                <div key={facet} style={{ background: "white", border: `2px solid ${col}`,
                  borderRadius: 8, padding: 10, maxHeight: 320, overflow: "auto" }}>
                  <div style={{ fontWeight: "bold", color: col, fontSize: 12, marginBottom: 6,
                    borderBottom: `1px solid ${col}30`, paddingBottom: 4 }}>
                    {facet} <span style={{ fontWeight: "normal", fontSize: 10 }}>({cnt})</span>
                  </div>
                  {discs.map(r => (
                    <div key={r.qid} style={{ padding: "2px 0", display: "flex", alignItems: "center",
                      gap: 6, borderBottom: `1px solid ${C.rule}40` }}>
                      <Mono col={C.slate}>{r.qid}</Mono>
                      <span style={{ fontSize: 10, color: C.ink }}>{r.label}</span>
                      {r.lcsh_id && <Tag label="LCSH" fill={C.purple} s={6} />}
                      {r.gnd_id && <Tag label="GND" fill={C.teal} s={6} />}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {view === "flat" && (
        <div>
          <div style={{ fontSize: 9, color: C.dim, marginBottom: 8, fontFamily: "Arial,sans-serif" }}>
            All {data.length} disciplines sorted by authority coverage (most identifiers first).
            Green border = has LCSH + LCC.
          </div>
          <div style={{ background: "white", border: `1px solid ${C.rule}`, borderRadius: 6,
            padding: 8, maxHeight: "70vh", overflow: "auto" }}>
            {data
              .map(r => ({
                ...r,
                score: (r.lcsh_id ? 2 : 0) + (r.lcc ? 2 : 0) + (r.gnd_id ? 1 : 0) +
                       (r.fast_id ? 1 : 0) + (r.ddc ? 1 : 0) + (r.aat_id ? 1 : 0),
              }))
              .sort((a, b) => b.score - a.score || (a.label || "").localeCompare(b.label || ""))
              .map(r => (
                <div key={r.qid} style={{ padding: "3px 8px", display: "flex", alignItems: "center",
                  gap: 6, borderLeft: `2px solid ${r.lcsh_id && r.lcc ? C.green : r.lcsh_id ? C.amber : C.rule}`,
                  marginBottom: 1 }}>
                  <Mono col={C.slate}>{r.qid}</Mono>
                  <span style={{ fontSize: 10.5, color: C.ink, minWidth: 180 }}>{r.label}</span>
                  <AuthBadges row={r} />
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

const btnStyle = {
  border: `1px solid ${C.rule}`, background: "white", borderRadius: 4,
  padding: "3px 10px", fontSize: 9, cursor: "pointer", color: C.slate,
  fontFamily: "Arial,sans-serif",
};
