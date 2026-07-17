import React, { useState } from "react";
import { createRoot } from "react-dom/client";

// Import Chrystallum JSX components from Key Files
import ChrystallumSystemMap from "../Key Files/chrystallum_system_map.jsx";
import ChrystallumArchitecture from "../Key Files/chrystallum_architecture.jsx";
import DisciplineUniverse from "../Key Files/chrystallum_discipline_universe.jsx";
import BiographicConstitution from "../Key Files/chrystallum_biographic_constitution.jsx";
import DisciplineConstitution from "../Key Files/chrystallum_discipline_constitution.jsx";
import DIConstitution from "../Key Files/chrystallum_di_constitution.jsx";
import GeographicConstitution from "../Key Files/chrystallum_geographic_constitution.jsx";
import SubjectConstitution from "../Key Files/chrystallum_subject_constitution.jsx";
import SCAConstitution from "../Key Files/chrystallum_sca_constitution.jsx";
import SFAConstitution from "../Key Files/chrystallum_sfa_constitution.jsx";
import SchemaBackbone from "../Key Files/chrystallum_schema_backbone.jsx";
import ProposalsRadial from "../Key Files/chrystallum_proposals_radial.jsx";
import ProposalReview from "../Key Files/chrystallum_proposal_review.jsx";
import ClaimReview from "../Key Files/chrystallum_claim_review.jsx";
import Neo4jExplorer from "./components/Neo4jExplorer.jsx";

const APPS = [
  ["neo4j", "Neo4j Explorer", Neo4jExplorer],
  ["review", "Review Queue", ProposalReview],
  ["claims", "Claims", ClaimReview],
  ["proposals", "SC Proposals", ProposalsRadial],
  ["schema", "Schema Backbone", SchemaBackbone],
  ["systemmap", "System Map", ChrystallumSystemMap],
  ["di-constitution", "DI", DIConstitution],
  ["sca-constitution", "SCA", SCAConstitution],
  ["sfa-constitution", "SFA", SFAConstitution],
  ["subject-constitution", "Subject Backbone", SubjectConstitution],
  ["architecture", "Architecture", ChrystallumArchitecture],
  ["discipline", "Discipline Universe", DisciplineUniverse],
  ["bio-constitution", "Bio Constitution", BiographicConstitution],
  ["discipline-constitution", "Discipline Constitution", DisciplineConstitution],
  ["geo-constitution", "Geo Constitution", GeographicConstitution],
];

function App() {
  const [active, setActive] = useState("neo4j");
  const Current = APPS.find(([k]) => k === active)?.[2] || Neo4jExplorer;

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
