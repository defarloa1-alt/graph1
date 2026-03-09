import React, { useState } from "react";
import { createRoot } from "react-dom/client";

// Import Chrystallum JSX components from Key Files
import ChrystallumSystemMap from "../Key Files/chrystallum_system_map.jsx";
import ChrystallumArchitecture from "../Key Files/chrystallum_architecture.jsx";
import DisciplineUniverse from "../Key Files/chrystallum_discipline_universe.jsx";
const APPS = [
  ["systemmap", "System Map (live)", ChrystallumSystemMap],
  ["architecture", "Architecture", ChrystallumArchitecture],
  ["discipline", "Discipline Universe", DisciplineUniverse],
];

function App() {
  const [active, setActive] = useState("systemmap");
  const Current = APPS.find(([k]) => k === active)?.[2] || DisciplineUniverse;

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", minHeight: "100vh" }}>
      <div
        style={{
          background: "#1a1a2e",
          color: "#eee",
          padding: "8px 16px",
          display: "flex",
          gap: 8,
          alignItems: "center",
        }}
      >
        <span style={{ fontWeight: "bold", marginRight: 16 }}>
          Chrystallum Viewer
        </span>
        {APPS.map(([k, label]) => (
          <button
            key={k}
            onClick={() => setActive(k)}
            style={{
              padding: "6px 12px",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
              background: active === k ? "#4361ee" : "#333",
              color: "#fff",
              fontSize: 13,
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <div style={{ padding: 0 }}>
        <Current />
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
