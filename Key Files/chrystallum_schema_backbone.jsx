import React, { useEffect, useRef, useState, useCallback } from "react";

/*
  DEPRECATED — Chrystal 2.0 schema viewer (Aura 0da8c4a3). Do not use for production.
  See docs/DEPRECATED_CHRYSTAL_2.0.md. Canonical graph: ac63a8e5 + chrystallum_system_map.jsx.

  Chrystal 2.0 — Schema Backbone Viewer
  Newtonian mechanics: Coulomb repulsion + Hooke spring attraction + Verlet integration.
  548 nodes, 1218 edges — 7 node types.
*/

const TYPE_STYLE = {
  FacetRegistry: { color: "#ff6b6b", mass: 50, radius: 16 },
  Facet:         { color: "#ffa94d", mass: 20, radius: 10 },
  CurriculumTopic: { color: "#51cf66", mass: 5, radius: 5 },
  DisciplineSource: { color: "#74c0fc", mass: 8, radius: 6 },
  CourseSyllabus: { color: "#b197fc", mass: 10, radius: 7 },
  CourseModule:   { color: "#e599f7", mass: 3, radius: 4 },
  Lecture:        { color: "#868e96", mass: 1, radius: 2.5 },
};

const EDGE_COLOR = {
  CONTAINS: "#ffa94d",
  HAS_TOPIC: "#82c91e",
  GROUNDED_IN: "#4dabf7",
  BROADER_THAN: "#51cf66",
  RELATED_TO: "#a9e34b",
  HAS_SYLLABUS: "#b197fc",
  HAS_MODULE: "#e599f7",
  HAS_LECTURE: "#555",
  COVERS_TOPIC: "#ff922b",
};

// Physics constants — tuned for 548 nodes, 1218 edges
const COULOMB_K = 120;      // repulsion strength (low: 548 nodes = ~150k pairs)
const SPRING_K = 0.02;      // spring stiffness (high enough to counteract repulsion)
const SPRING_REST = 35;     // rest length
const DAMPING = 0.85;       // velocity damping per step (aggressive to prevent explosion)
const DT = 0.8;             // timestep (sub-unit for stability)
const GRAVITY_CENTER = 0.002; // pull to center (stronger to contain the system)

function initPhysics(nodes, edges, W, H) {
  const idxMap = {};

  // Stratify by type into concentric rings to avoid initial overlap
  const ringRadius = {
    FacetRegistry: 0,
    Facet: 80,
    CurriculumTopic: 200,
    DisciplineSource: 300,
    CourseSyllabus: 340,
    CourseModule: 390,
    Lecture: 420,
  };
  // Count per type for angular spacing
  const typeCounts = {};
  const typeIdx = {};
  nodes.forEach((n) => {
    typeCounts[n.type] = (typeCounts[n.type] || 0) + 1;
    typeIdx[n.type] = 0;
  });

  const bodies = nodes.map((n, i) => {
    idxMap[n.id] = i;
    const style = TYPE_STYLE[n.type] || TYPE_STYLE.Lecture;
    const r = (ringRadius[n.type] || 350) + (Math.random() - 0.5) * 30;
    const count = typeCounts[n.type] || 1;
    const idx = typeIdx[n.type]++;
    const angle = (idx / count) * Math.PI * 2 + (Math.random() - 0.5) * 0.3;
    return {
      ...n,
      x: W / 2 + Math.cos(angle) * r,
      y: H / 2 + Math.sin(angle) * r,
      vx: 0,
      vy: 0,
      mass: style.mass,
      radius: style.radius,
      color: style.color,
    };
  });

  // Build adjacency as index pairs for O(1) lookup
  const springs = edges.map((e) => ({
    a: idxMap[e.src],
    b: idxMap[e.tgt],
    type: e.type,
    rest: e.type === "HAS_LECTURE" ? 25 : e.type === "COVERS_TOPIC" ? 80 : SPRING_REST,
    k: e.type === "COVERS_TOPIC" ? SPRING_K * 0.3 : SPRING_K,
  })).filter((s) => s.a !== undefined && s.b !== undefined);

  return { bodies, springs, W, H };
}

function step(sim) {
  const { bodies, springs, W, H } = sim;
  const N = bodies.length;
  const cx = W / 2, cy = H / 2;

  // Reset forces
  for (let i = 0; i < N; i++) {
    bodies[i].fx = 0;
    bodies[i].fy = 0;
  }

  // Coulomb repulsion (use Barnes-Hut approximation for large N)
  // For 548 nodes, brute force O(N²) = 300k ops — fine at 60fps if we skip distant pairs
  for (let i = 0; i < N; i++) {
    const bi = bodies[i];
    for (let j = i + 1; j < N; j++) {
      const bj = bodies[j];
      const dx = bi.x - bj.x;
      const dy = bi.y - bj.y;
      const distSq = dx * dx + dy * dy;
      if (distSq > 250000) continue; // skip pairs > 500px apart
      const clampedSq = Math.max(distSq, 100); // floor at 10px — prevents singularity
      const dist = Math.sqrt(distSq) || 10;
      const F = COULOMB_K / clampedSq;
      const fx = (dx / dist) * F;
      const fy = (dy / dist) * F;
      bi.fx += fx * bj.mass;
      bi.fy += fy * bj.mass;
      bj.fx -= fx * bi.mass;
      bj.fy -= fy * bi.mass;
    }
  }

  // Hooke springs (edge attraction)
  for (const s of springs) {
    const a = bodies[s.a];
    const b = bodies[s.b];
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const displacement = dist - s.rest;
    const F = s.k * displacement;
    const fx = (dx / dist) * F;
    const fy = (dy / dist) * F;
    a.fx += fx;
    a.fy += fy;
    b.fx -= fx;
    b.fy -= fy;
  }

  // Gravity toward center (prevents drift)
  for (let i = 0; i < N; i++) {
    const b = bodies[i];
    b.fx += (cx - b.x) * GRAVITY_CENTER * b.mass;
    b.fy += (cy - b.y) * GRAVITY_CENTER * b.mass;
  }

  // Velocity Verlet integration
  for (let i = 0; i < N; i++) {
    const b = bodies[i];
    if (b.pinned) continue;
    const ax = b.fx / b.mass;
    const ay = b.fy / b.mass;
    b.vx = (b.vx + ax * DT) * DAMPING;
    b.vy = (b.vy + ay * DT) * DAMPING;
    b.x += b.vx * DT;
    b.y += b.vy * DT;
    // Boundary
    b.x = Math.max(b.radius, Math.min(W - b.radius, b.x));
    b.y = Math.max(b.radius, Math.min(H - b.radius, b.y));
  }
}

function kineticEnergy(bodies) {
  let ke = 0;
  for (const b of bodies) ke += 0.5 * b.mass * (b.vx * b.vx + b.vy * b.vy);
  return ke;
}

export default function SchemaBackbone() {
  const canvasRef = useRef(null);
  const simRef = useRef(null);
  const rafRef = useRef(null);
  const dragRef = useRef(null);
  const [loaded, setLoaded] = useState(false);
  const [filter, setFilter] = useState("all");
  const [hovered, setHovered] = useState(null);
  const [ke, setKe] = useState(0);
  const [paused, setPaused] = useState(false);
  const filterRef = useRef(filter);
  const hoveredRef = useRef(hovered);
  const pausedRef = useRef(paused);

  useEffect(() => { filterRef.current = filter; }, [filter]);
  useEffect(() => { hoveredRef.current = hovered; }, [hovered]);
  useEffect(() => { pausedRef.current = paused; }, [paused]);

  useEffect(() => {
    fetch("/graph_data.json")
      .then((r) => r.json())
      .then((data) => {
        const W = 1400, H = 900;
        simRef.current = initPhysics(data.nodes, data.edges, W, H);
        setLoaded(true);
      });
  }, []);

  useEffect(() => {
    if (!loaded) return;

    let frame = 0;
    function loop() {
      const sim = simRef.current;
      if (!sim) return;

      if (!pausedRef.current) {
        step(sim);
        if (frame % 30 === 0) setKe(kineticEnergy(sim.bodies));
      }

      draw(sim);
      frame++;
      rafRef.current = requestAnimationFrame(loop);
    }

    loop();
    return () => cancelAnimationFrame(rafRef.current);
  }, [loaded]);

  function draw(sim) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const { bodies, springs, W, H } = sim;

    canvas.width = W;
    canvas.height = H;

    ctx.fillStyle = "#0a0a14";
    ctx.fillRect(0, 0, W, H);

    const f = filterRef.current;
    const visTypes = f === "all" ? null
      : f === "taxonomy" ? new Set(["FacetRegistry", "Facet", "CurriculumTopic"])
      : f === "curriculum" ? new Set(["DisciplineSource", "CourseSyllabus", "CourseModule", "Lecture"])
      : f === "bridge" ? new Set(["CurriculumTopic", "DisciplineSource", "CourseSyllabus", "Lecture"])
      : null;

    const visSet = new Set();
    bodies.forEach((b, i) => {
      if (!visTypes || visTypes.has(b.type)) visSet.add(i);
    });

    // Edges
    for (const s of springs) {
      if (!visSet.has(s.a) || !visSet.has(s.b)) continue;
      const a = bodies[s.a];
      const b = bodies[s.b];
      ctx.strokeStyle = (EDGE_COLOR[s.type] || "#333") + (s.type === "COVERS_TOPIC" ? "60" : "25");
      ctx.lineWidth = s.type === "COVERS_TOPIC" ? 1.2 : 0.4;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    }

    // Nodes
    const hov = hoveredRef.current;
    for (let i = 0; i < bodies.length; i++) {
      if (!visSet.has(i)) continue;
      const b = bodies[i];
      const isH = hov === i;

      ctx.fillStyle = isH ? "#ffffff" : b.color;
      ctx.globalAlpha = isH ? 1 : 0.85;
      ctx.beginPath();
      ctx.arc(b.x, b.y, isH ? b.radius + 3 : b.radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1;

      // Labels for big nodes or hovered
      if (b.radius >= 7 || isH) {
        ctx.fillStyle = "#ccc";
        ctx.font = `${isH ? 11 : 9}px system-ui`;
        ctx.textAlign = "center";
        const lbl = b.label.length > 25 ? b.label.slice(0, 22) + "..." : b.label;
        ctx.fillText(lbl, b.x, b.y + b.radius + 13);
      }
    }

    // HUD
    ctx.fillStyle = "#eee";
    ctx.font = "bold 15px system-ui";
    ctx.textAlign = "left";
    ctx.fillText("Chrystal 2.0 — Schema Backbone", 14, 24);
    ctx.font = "11px system-ui";
    ctx.fillStyle = "#777";
    ctx.fillText(`${bodies.length} nodes · ${springs.length} edges · KE: ${ke.toFixed(0)}`, 14, 40);
  }

  function getNodeAt(ex, ey) {
    if (!simRef.current) return -1;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = ex - rect.left;
    const y = ey - rect.top;
    const bodies = simRef.current.bodies;
    for (let i = bodies.length - 1; i >= 0; i--) {
      const b = bodies[i];
      if ((b.x - x) ** 2 + (b.y - y) ** 2 < (b.radius + 4) ** 2) return i;
    }
    return -1;
  }

  function onMouseDown(e) {
    const idx = getNodeAt(e.clientX, e.clientY);
    if (idx >= 0) {
      dragRef.current = idx;
      simRef.current.bodies[idx].pinned = true;
    }
  }

  function onMouseMove(e) {
    if (dragRef.current !== null && dragRef.current >= 0) {
      const rect = canvasRef.current.getBoundingClientRect();
      const b = simRef.current.bodies[dragRef.current];
      b.x = e.clientX - rect.left;
      b.y = e.clientY - rect.top;
      b.vx = 0;
      b.vy = 0;
    } else {
      const idx = getNodeAt(e.clientX, e.clientY);
      setHovered(idx >= 0 ? idx : null);
    }
  }

  function onMouseUp() {
    if (dragRef.current !== null && dragRef.current >= 0) {
      simRef.current.bodies[dragRef.current].pinned = false;
    }
    dragRef.current = null;
  }

  const hovBody = hovered !== null && simRef.current ? simRef.current.bodies[hovered] : null;

  return (
    <div style={{ padding: 12, background: "#0a0a14", minHeight: "100vh" }}>
      <div style={{ marginBottom: 8, display: "flex", gap: 8, alignItems: "center" }}>
        {["all", "taxonomy", "curriculum", "bridge"].map((v) => (
          <button
            key={v}
            onClick={() => setFilter(v)}
            style={{
              padding: "4px 14px",
              background: filter === v ? "#4dabf7" : "#1a1a2e",
              color: "#fff",
              border: "1px solid #333",
              borderRadius: 4,
              cursor: "pointer",
              fontSize: 12,
            }}
          >
            {v}
          </button>
        ))}
        <button
          onClick={() => setPaused((p) => !p)}
          style={{
            marginLeft: 12,
            padding: "4px 14px",
            background: paused ? "#e03131" : "#1a1a2e",
            color: "#fff",
            border: "1px solid #333",
            borderRadius: 4,
            cursor: "pointer",
            fontSize: 12,
          }}
        >
          {paused ? "▶ resume" : "⏸ pause"}
        </button>
        <span style={{ marginLeft: 16, fontSize: 11, color: "#666" }}>
          drag nodes · scroll to explore
        </span>
      </div>

      {/* Legend */}
      <div style={{ marginBottom: 6, display: "flex", gap: 14, fontSize: 11, color: "#999" }}>
        {Object.entries(TYPE_STYLE).map(([type, s]) => (
          <span key={type}>
            <span style={{ color: s.color, fontSize: 13 }}>●</span> {type}
          </span>
        ))}
      </div>

      {!loaded ? (
        <div style={{ color: "#888", padding: 40 }}>Loading graph data...</div>
      ) : (
        <canvas
          ref={canvasRef}
          style={{ borderRadius: 8, cursor: dragRef.current !== null ? "grabbing" : "crosshair" }}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseUp}
        />
      )}

      {hovBody && (
        <div style={{
          marginTop: 6, padding: "6px 12px",
          background: "#111", borderRadius: 6, fontSize: 12, color: "#ccc",
          display: "inline-block",
        }}>
          <span style={{ color: hovBody.color, fontWeight: "bold" }}>{hovBody.type}</span>
          {" "}{hovBody.label}
          <span style={{ color: "#555", marginLeft: 12 }}>
            mass={hovBody.mass} r={hovBody.radius}
          </span>
        </div>
      )}
    </div>
  );
}
