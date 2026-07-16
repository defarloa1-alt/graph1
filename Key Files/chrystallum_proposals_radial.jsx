import React, { useState, useMemo } from "react";
import proposalsData from "../output/di_proposals/Q17167_proposals.json";
import aggregationData from "../output/di_proposals/Q17167_aggregation.json";
import graphData from "../viewer/public/graph_data.json";

const W = 620, H = 620, CX = 310, CY = 310;
const R_FACET = 130;
const R_SC = 240;
const GAP = 0.03;

const FACET_COLORS = {
  military:      "#E74C3C",
  political:     "#3F51B5",
  religious:     "#795548",
  social:        "#FF5722",
  economic:      "#2ECC71",
  intellectual:  "#1ABC9C",
  scientific:    "#00BCD4",
  linguistic:    "#F39C12",
  communication: "#3498DB",
  artistic:      "#9B59B6",
  archaeological:"#8B4513",
  cultural:      "#E91E63",
  demographic:   "#FF9800",
};

const FACET_ORDER = [
  "military","political","religious","social","economic","intellectual",
  "scientific","linguistic","communication","artistic","archaeological",
  "cultural","demographic",
];

// Build curriculum index from graph_data.json
function buildCurriculumIndex() {
  const nodes = graphData.nodes || [];
  const edges = graphData.edges || [];

  const byId = {};
  for (const n of nodes) byId[n.id] = n;

  // edge maps
  const edgesFrom = {};
  for (const e of edges) {
    if (!edgesFrom[e.source]) edgesFrom[e.source] = [];
    edgesFrom[e.source].push(e);
  }
  const edgesTo = {};
  for (const e of edges) {
    if (!edgesTo[e.target]) edgesTo[e.target] = [];
    edgesTo[e.target].push(e);
  }

  // facet → CTs
  const facetToCTs = {};
  for (const e of edges) {
    if (e.type === "HAS_TOPIC") {
      const facetNode = byId[e.source];
      const ctNode = byId[e.target];
      if (!facetNode || !ctNode) continue;
      const fLabel = (facetNode.label || "").toLowerCase();
      if (!facetToCTs[fLabel]) facetToCTs[fLabel] = [];
      facetToCTs[fLabel].push(ctNode);
    }
  }

  // CT → lectures
  const ctToLectures = {};
  for (const e of edges) {
    if (e.type === "COVERS_TOPIC") {
      const lNode = byId[e.source];
      const ctNode = byId[e.target];
      if (!lNode || !ctNode) continue;
      if (!ctToLectures[ctNode.id]) ctToLectures[ctNode.id] = [];
      ctToLectures[ctNode.id].push(lNode);
    }
  }

  // lecture → course (via HAS_LECTURE or HAS_MODULE→HAS_LECTURE)
  const lectureToCourse = {};
  for (const e of edges) {
    if (e.type === "HAS_LECTURE") {
      const parent = byId[e.source];
      const lec = byId[e.target];
      if (!parent || !lec) continue;
      // parent may be module or syllabus
      if (parent.type === "CourseSyllabus") {
        lectureToCourse[lec.id] = parent;
      } else if (parent.type === "CourseModule") {
        // find syllabus of module
        const sylEdge = (edgesTo[parent.id] || []).find(x => x.type === "HAS_MODULE");
        if (sylEdge) lectureToCourse[lec.id] = byId[sylEdge.source];
      }
    }
  }

  return { facetToCTs, ctToLectures, lectureToCourse };
}

function buildFacetData() {
  const decomposed = {};
  for (const p of proposalsData.proposals) {
    const f = p.source_facet;
    if (!decomposed[f]) decomposed[f] = [];
    decomposed[f].push(p);
  }
  const corpusStats = aggregationData.corpus_stats || {};
  const facets = {};
  for (const f of FACET_ORDER) {
    if (decomposed[f]) {
      facets[f] = decomposed[f];
    } else {
      const stats = corpusStats[f] || {};
      facets[f] = [{
        label: f.charAt(0).toUpperCase() + f.slice(1) + " (single SC)",
        description: "Managed as a single SubjectConcept — below decomposition threshold",
        confidence: stats.avg_confidence || 0.83,
        candidate_qids: [],
        estimated_concepts: stats.total_works || 0,
        needs: "Single-domain coverage",
        source_facet: f,
        scope_key: f + "_single",
        single: true,
      }];
    }
  }
  return facets;
}

function computeAngles(facets) {
  const counts = FACET_ORDER.map(f => facets[f].length);
  const total = counts.reduce((a, b) => a + b, 0);
  const available = 2 * Math.PI - GAP * FACET_ORDER.length;
  const angles = {};
  let cursor = -Math.PI / 2;
  FACET_ORDER.forEach((f, i) => {
    const span = (counts[i] / total) * available;
    angles[f] = { start: cursor, end: cursor + span, mid: cursor + span / 2 };
    cursor += span + GAP;
  });
  return angles;
}

function polarToXY(r, theta) {
  return { x: CX + r * Math.cos(theta), y: CY + r * Math.sin(theta) };
}

function arcPath(r, s, e) {
  const p1 = polarToXY(r, s), p2 = polarToXY(r, e);
  return `M ${p1.x} ${p1.y} A ${r} ${r} 0 ${e - s > Math.PI ? 1 : 0} 1 ${p2.x} ${p2.y}`;
}

function crossLinkPath(a1, a2) {
  const p1 = polarToXY(R_FACET, a1), p2 = polarToXY(R_FACET, a2);
  return `M ${p1.x} ${p1.y} Q ${CX} ${CY} ${p2.x} ${p2.y}`;
}

export default function ProposalsRadial() {
  const [hovered, setHovered] = useState(null);
  const [selectedSC, setSelectedSC] = useState(null);
  const [selectedFacet, setSelectedFacet] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const curriculum = useMemo(() => buildCurriculumIndex(), []);
  const facets = useMemo(() => buildFacetData(), []);
  const angles = useMemo(() => computeAngles(facets), [facets]);
  const crossLinks = aggregationData.cross_facet_links || [];

  const scNodes = [];
  for (const f of FACET_ORDER) {
    const { start, end } = angles[f];
    const scs = facets[f];
    scs.forEach((sc, i) => {
      const theta = scs.length === 1
        ? (start + end) / 2
        : start + (i + 0.5) * (end - start) / scs.length;
      const pos = polarToXY(R_SC, theta);
      scNodes.push({ ...sc, theta, x: pos.x, y: pos.y, facet: f });
    });
  }

  const highlighted = selectedFacet
    ? new Set(crossLinks
        .filter(l => l.source_facet === selectedFacet || l.target_facet === selectedFacet)
        .map(l => l.source_facet === selectedFacet ? l.target_facet : l.source_facet))
    : null;

  // Build curriculum panel data for selected SC
  const panelData = useMemo(() => {
    if (!selectedSC) return null;
    const facetKey = selectedSC.facet.toLowerCase();
    const cts = curriculum.facetToCTs[facetKey] || [];
    const courseMap = {};
    for (const ct of cts) {
      const lectures = curriculum.ctToLectures[ct.id] || [];
      for (const lec of lectures) {
        const course = curriculum.lectureToCourse[lec.id];
        if (!course) continue;
        if (!courseMap[course.id]) courseMap[course.id] = { course, lectures: [], cts: new Set() };
        courseMap[course.id].lectures.push(lec);
        courseMap[course.id].cts.add(ct.label);
      }
    }
    return {
      cts,
      courses: Object.values(courseMap).sort((a, b) => b.lectures.length - a.lectures.length),
    };
  }, [selectedSC, curriculum]);

  const color = selectedSC ? FACET_COLORS[selectedSC.facet] : "#666";

  return (
    <div
      style={{ background: "#0d0d1a", minHeight: "100vh", color: "#eee", padding: "16px 20px" }}
      onMouseMove={e => setMousePos({ x: e.clientX, y: e.clientY })}
    >
      <div style={{ textAlign: "center", marginBottom: 8 }}>
        <span style={{ fontSize: 16, fontWeight: 700, color: "#a0c4ff" }}>
          Q17167 — Roman Republic: SC Proposals
        </span>
        <span style={{ marginLeft: 12, color: "#555", fontSize: 12 }}>
          {scNodes.length} proposals · click SC node for curriculum · click arc for connections
        </span>
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        {/* Radial SVG */}
        <svg width={W} height={H} style={{ flexShrink: 0 }}>
          {crossLinks.map((link, i) => {
            const sf = angles[link.source_facet], tf = angles[link.target_facet];
            if (!sf || !tf) return null;
            const active = !selectedFacet || link.source_facet === selectedFacet || link.target_facet === selectedFacet;
            return (
              <path key={i} d={crossLinkPath(sf.mid, tf.mid)} fill="none"
                stroke={FACET_COLORS[link.source_facet] || "#555"}
                strokeWidth={active ? 1.5 : 0.3}
                strokeOpacity={active ? link.confidence * 0.7 : 0.06}
                strokeDasharray={link.role === "causal" ? "none" : "4 3"} />
            );
          })}

          {FACET_ORDER.map(f => {
            const { start, end, mid } = angles[f];
            const c = FACET_COLORS[f];
            const isSel = selectedFacet === f;
            const isDim = selectedFacet && !isSel && !highlighted?.has(f);
            const lp = polarToXY(R_FACET + 26, mid);
            const anchor = Math.cos(mid) > 0.1 ? "start" : Math.cos(mid) < -0.1 ? "end" : "middle";
            return (
              <g key={f} onClick={() => setSelectedFacet(selectedFacet === f ? null : f)} style={{ cursor: "pointer" }}>
                <path d={arcPath(R_FACET, start + GAP / 2, end - GAP / 2)} fill="none"
                  stroke={c} strokeWidth={isSel ? 10 : 6}
                  strokeOpacity={isDim ? 0.12 : isSel ? 1 : 0.65} />
                <text x={lp.x} y={lp.y} textAnchor={anchor} dominantBaseline="middle"
                  fontSize={10} fill={c} opacity={isDim ? 0.2 : 1} fontWeight={isSel ? 700 : 400}>
                  {f}
                </text>
              </g>
            );
          })}

          {scNodes.map((sc, i) => {
            const c = FACET_COLORS[sc.facet];
            const r = 5 + (sc.confidence || 0.8) * 9;
            const hasCands = sc.candidate_qids?.length > 0;
            const isDim = selectedFacet && sc.facet !== selectedFacet && !highlighted?.has(sc.facet);
            const isHov = hovered === i;
            const isSel = selectedSC === sc;
            return (
              <g key={i}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
                onClick={() => setSelectedSC(selectedSC === sc ? null : sc)}
                style={{ cursor: "pointer" }}>
                {/* transparent hit area — captures clicks regardless of fill */}
                <circle cx={sc.x} cy={sc.y} r={r + 6} fill="transparent" />
                <circle cx={sc.x} cy={sc.y} r={isHov || isSel ? r + 3 : r}
                  fill={hasCands ? c : "none"} stroke={c}
                  strokeWidth={hasCands ? (isSel ? 2 : 1) : 1.5}
                  opacity={isDim ? 0.08 : sc.single ? 0.45 : 0.85} />
                {(isHov || isSel) && (
                  <circle cx={sc.x} cy={sc.y} r={r + 7}
                    fill="none" stroke={c} strokeWidth={isSel ? 2 : 1} opacity={0.5} />
                )}
              </g>
            );
          })}

          <circle cx={CX} cy={CY} r={26} fill="#1a1a3e" stroke="#a0c4ff" strokeWidth={2} />
          <text x={CX} y={CY - 5} textAnchor="middle" fontSize={8} fill="#a0c4ff" fontWeight={700}>Q17167</text>
          <text x={CX} y={CY + 6} textAnchor="middle" fontSize={7} fill="#8888aa">Roman</text>
          <text x={CX} y={CY + 15} textAnchor="middle" fontSize={7} fill="#8888aa">Republic</text>
        </svg>

        {/* Curriculum panel */}
        <div style={{ flex: 1, minWidth: 0, maxHeight: H, overflowY: "auto" }}>
          {!selectedSC ? (
            <div style={{ color: "#444", padding: "60px 20px", textAlign: "center", fontSize: 13 }}>
              click a node to see curriculum coverage
            </div>
          ) : (
            <div style={{ fontSize: 12 }}>
              <div style={{ borderBottom: `2px solid ${color}`, paddingBottom: 10, marginBottom: 12 }}>
                <div style={{ fontSize: 15, fontWeight: 700, color }}>{selectedSC.label}</div>
                <div style={{ color: "#888", marginTop: 4 }}>{selectedSC.description}</div>
                <div style={{ display: "flex", gap: 14, marginTop: 6, color: "#555", fontSize: 11 }}>
                  <span>conf <span style={{ color: "#ccc" }}>{(selectedSC.confidence || 0).toFixed(2)}</span></span>
                  <span>facet <span style={{ color }}>{selectedSC.facet}</span></span>
                </div>

                {/* Wikidata candidate QIDs */}
                {selectedSC.candidate_qids?.length > 0 && (
                  <div style={{ marginTop: 8 }}>
                    <div style={{ color: "#555", fontSize: 10, textTransform: "uppercase", letterSpacing: 1, marginBottom: 3 }}>Wikidata</div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                      {selectedSC.candidate_qids.map(qid => (
                        <a key={qid} href={`https://www.wikidata.org/wiki/${qid}`} target="_blank" rel="noreferrer"
                          style={{ color, fontSize: 11, textDecoration: "none", background: "#1a1a2e",
                                   padding: "2px 6px", borderRadius: 3, border: `1px solid ${color}44` }}>
                          {qid} ↗
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {/* LCSH anchor */}
                {selectedSC.lcsh_id && (
                  <div style={{ marginTop: 6 }}>
                    <div style={{ color: "#555", fontSize: 10, textTransform: "uppercase", letterSpacing: 1, marginBottom: 3 }}>LCSH</div>
                    <a href={`https://id.loc.gov/authorities/subjects/${selectedSC.lcsh_id}`} target="_blank" rel="noreferrer"
                      style={{ color: "#a0c4ff", fontSize: 11, textDecoration: "none" }}>
                      {selectedSC.lcsh_label || selectedSC.lcsh_id} ({selectedSC.lcsh_id}) ↗
                    </a>
                  </div>
                )}

                {selectedSC.needs && (
                  <div style={{ color: "#555", marginTop: 6, fontStyle: "italic", fontSize: 11 }}>
                    needs: {selectedSC.needs}
                  </div>
                )}
              </div>

              {/* CurriculumTopics in facet */}
              <div style={{ marginBottom: 12 }}>
                <div style={{ color: "#666", fontSize: 11, marginBottom: 6, textTransform: "uppercase", letterSpacing: 1 }}>
                  CurriculumTopics ({panelData?.cts.length || 0})
                </div>
                {(panelData?.cts || []).map((ct, i) => {
                  const lecs = curriculum.ctToLectures[ct.id] || [];
                  return (
                    <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "3px 0", borderBottom: "1px solid #1a1a2e" }}>
                      <span style={{ color: lecs.length > 0 ? "#ccc" : "#444" }}>{ct.label}</span>
                      <span style={{ color: lecs.length > 0 ? color : "#333", fontSize: 11 }}>
                        {lecs.length} lec{lecs.length !== 1 ? "s" : ""}
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Courses */}
              <div>
                <div style={{ color: "#666", fontSize: 11, marginBottom: 6, textTransform: "uppercase", letterSpacing: 1 }}>
                  Courses ({panelData?.courses.length || 0})
                </div>
                {panelData?.courses.length === 0 && (
                  <div style={{ color: "#444", fontStyle: "italic" }}>no curriculum coverage yet</div>
                )}
                {(panelData?.courses || []).map(({ course, lectures, cts }, i) => (
                  <div key={i} style={{ marginBottom: 10, padding: "8px 10px", background: "#111122", borderRadius: 4, borderLeft: `3px solid ${color}` }}>
                    <div style={{ fontWeight: 600, color: "#ddd", marginBottom: 4 }}>{course.label}</div>
                    <div style={{ color: "#666", fontSize: 11, marginBottom: 4 }}>
                      {lectures.length} lecture{lectures.length !== 1 ? "s" : ""} · topics: {[...cts].join(", ")}
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                      {lectures.slice(0, 5).map((l, j) => (
                        <div key={j} style={{ color: "#888", fontSize: 11, paddingLeft: 8 }}>· {l.label}</div>
                      ))}
                      {lectures.length > 5 && (
                        <div style={{ color: "#555", fontSize: 11, paddingLeft: 8 }}>+ {lectures.length - 5} more</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Hover tooltip (not when SC is selected) */}
      {hovered !== null && !selectedSC && scNodes[hovered] && (
        <div style={{
          position: "fixed", left: mousePos.x + 14, top: mousePos.y - 10,
          background: "#1a1a2e", border: `1px solid ${FACET_COLORS[scNodes[hovered].facet]}`,
          borderRadius: 6, padding: "8px 12px", maxWidth: 280,
          pointerEvents: "none", zIndex: 100, fontSize: 12,
        }}>
          <div style={{ fontWeight: 700, color: FACET_COLORS[scNodes[hovered].facet], marginBottom: 3 }}>
            {scNodes[hovered].label}
          </div>
          <div style={{ color: "#888" }}>{scNodes[hovered].description}</div>
        </div>
      )}
    </div>
  );
}
