import React, { useState, useEffect } from "react";

const Neo4jExplorer = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState("label"); // label, qid, property
  const [entities, setEntities] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [relationships, setRelationships] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({ totalEntities: 0, entityTypes: {} });
  const [filters, setFilters] = useState({
    entityType: "all",
    minFederationScore: 0,
    facet: "all"
  });

  // Fetch stats on component mount
  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch("/api/stats");
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  };

  const executeQuery = async (cypher, params = {}) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cypher, params }),
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const data = await response.json();
      setLoading(false);
      return data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return null;
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      // Load recent entities if no search query
      await loadRecentEntities();
      return;
    }

    let cypher = "";
    let params = {};

    switch (searchType) {
      case "label":
        cypher = `
          MATCH (n)
          WHERE n.label CONTAINS $query
          RETURN n
          LIMIT 50
        `;
        params = { query: searchQuery };
        break;
      case "qid":
        cypher = `
          MATCH (n)
          WHERE n.qid = $qid
          RETURN n
        `;
        params = { qid: searchQuery.toUpperCase() };
        break;
      case "property":
        cypher = `
          MATCH (n)
          WHERE n.property_summary CONTAINS $query
          RETURN n
          LIMIT 50
        `;
        params = { query: searchQuery };
        break;
    }

    // Apply filters
    if (filters.entityType !== "all") {
      cypher = cypher.replace(
        "MATCH (n)",
        `MATCH (n:${filters.entityType})`
      );
    }

    if (filters.minFederationScore > 0) {
      cypher = cypher.replace(
        "RETURN n",
        `AND n.federation_score >= ${filters.minFederationScore}\nRETURN n`
      );
    }

    const result = await executeQuery(cypher, params);
    if (result && result.records) {
      setEntities(result.records.map(r => r.n));
    }
  };

  const loadRecentEntities = async () => {
    let cypher = `
      MATCH (n)
      RETURN n
      ORDER BY n.created_at DESC
      LIMIT 50
    `;

    if (filters.entityType !== "all") {
      cypher = cypher.replace("MATCH (n)", `MATCH (n:${filters.entityType})`);
    }

    const result = await executeQuery(cypher);
    if (result && result.records) {
      setEntities(result.records.map(r => r.n));
    }
  };

  const loadEntityDetails = async (entity) => {
    setSelectedEntity(entity);

    // Load relationships
    const cypher = `
      MATCH (n)-[r]-(m)
      WHERE n.entity_cipher = $cipher
      RETURN type(r) as relType, r, m
      LIMIT 100
    `;

    const result = await executeQuery(cypher, {
      cipher: entity.entity_cipher,
    });

    if (result && result.records) {
      setRelationships(result.records);
    }
  };

  return (
    <div style={{ display: "flex", height: "calc(100vh - 48px)", background: "#f5f5f5" }}>
      {/* Left Sidebar - Search & Filters */}
      <div
        style={{
          width: 320,
          background: "#fff",
          borderRight: "1px solid #ddd",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Search Section */}
        <div style={{ padding: 16, borderBottom: "1px solid #eee" }}>
          <h2 style={{ margin: "0 0 16px 0", fontSize: 20, fontWeight: 600 }}>
            Neo4j Explorer
          </h2>

          {/* Stats */}
          <div
            style={{
              padding: 12,
              background: "#f9f9f9",
              borderRadius: 6,
              marginBottom: 16,
              fontSize: 13,
            }}
          >
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Database Stats</div>
            <div>Total Entities: {stats.totalEntities.toLocaleString()}</div>
          </div>

          {/* Search Type */}
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: "block", marginBottom: 4, fontSize: 13, fontWeight: 500 }}>
              Search by:
            </label>
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value)}
              style={{
                width: "100%",
                padding: 8,
                border: "1px solid #ddd",
                borderRadius: 4,
                fontSize: 13,
              }}
            >
              <option value="label">Label</option>
              <option value="qid">QID</option>
              <option value="property">Property Content</option>
            </select>
          </div>

          {/* Search Input */}
          <div style={{ marginBottom: 12 }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder={`Search by ${searchType}...`}
              style={{
                width: "100%",
                padding: 8,
                border: "1px solid #ddd",
                borderRadius: 4,
                fontSize: 13,
              }}
            />
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            style={{
              width: "100%",
              padding: 10,
              background: loading ? "#ccc" : "#4361ee",
              color: "#fff",
              border: "none",
              borderRadius: 4,
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: 14,
              fontWeight: 500,
            }}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Filters Section */}
        <div style={{ padding: 16, borderBottom: "1px solid #eee" }}>
          <h3 style={{ margin: "0 0 12px 0", fontSize: 15, fontWeight: 600 }}>
            Filters
          </h3>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: "block", marginBottom: 4, fontSize: 13 }}>
              Entity Type
            </label>
            <select
              value={filters.entityType}
              onChange={(e) =>
                setFilters({ ...filters, entityType: e.target.value })
              }
              style={{
                width: "100%",
                padding: 6,
                border: "1px solid #ddd",
                borderRadius: 4,
                fontSize: 13,
              }}
            >
              <option value="all">All Types</option>
              <option value="CONCEPT">Concept</option>
              <option value="PERSON">Person</option>
              <option value="PLACE">Place</option>
              <option value="EVENT">Event</option>
              <option value="PERIOD">Period</option>
              <option value="WORK">Work</option>
            </select>
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: "block", marginBottom: 4, fontSize: 13 }}>
              Min Federation Score: {filters.minFederationScore}
            </label>
            <input
              type="range"
              min="0"
              max="20"
              value={filters.minFederationScore}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  minFederationScore: parseInt(e.target.value),
                })
              }
              style={{ width: "100%" }}
            />
          </div>
        </div>

        {/* Results List */}
        <div style={{ flex: 1, overflow: "auto", padding: "8px 0" }}>
          {error && (
            <div
              style={{
                margin: 16,
                padding: 12,
                background: "#fee",
                border: "1px solid #fcc",
                borderRadius: 4,
                color: "#c33",
                fontSize: 13,
              }}
            >
              {error}
            </div>
          )}

          {entities.length === 0 && !loading && (
            <div
              style={{
                padding: 24,
                textAlign: "center",
                color: "#999",
                fontSize: 13,
              }}
            >
              No entities found. Try searching or adjusting filters.
            </div>
          )}

          {entities.map((entity, idx) => (
            <div
              key={entity.entity_cipher || idx}
              onClick={() => loadEntityDetails(entity)}
              style={{
                padding: "12px 16px",
                cursor: "pointer",
                borderBottom: "1px solid #f0f0f0",
                background:
                  selectedEntity?.entity_cipher === entity.entity_cipher
                    ? "#f0f7ff"
                    : "transparent",
                transition: "background 0.15s",
              }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.background = "#f9f9f9")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.background =
                  selectedEntity?.entity_cipher === entity.entity_cipher
                    ? "#f0f7ff"
                    : "transparent")
              }
            >
              <div style={{ fontWeight: 500, fontSize: 14, marginBottom: 4 }}>
                {entity.label || entity.qid || "Unknown"}
              </div>
              <div style={{ fontSize: 12, color: "#666" }}>
                {entity.qid && <span style={{ marginRight: 8 }}>{entity.qid}</span>}
                {entity.entity_type && (
                  <span
                    style={{
                      background: "#e8e8e8",
                      padding: "2px 6px",
                      borderRadius: 3,
                      fontSize: 11,
                      marginRight: 8,
                    }}
                  >
                    {entity.entity_type}
                  </span>
                )}
                {entity.federation_score > 0 && (
                  <span style={{ color: "#4361ee", fontSize: 11 }}>
                    Fed: {entity.federation_score}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content - Entity Details */}
      <div style={{ flex: 1, overflow: "auto", background: "#fff" }}>
        {!selectedEntity ? (
          <div
            style={{
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#999",
              fontSize: 16,
            }}
          >
            Select an entity to view details
          </div>
        ) : (
          <div style={{ padding: 32 }}>
            {/* Entity Header */}
            <div style={{ marginBottom: 32 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                <h1 style={{ margin: 0, fontSize: 32, fontWeight: 600 }}>
                  {selectedEntity.label || selectedEntity.qid || "Unknown Entity"}
                </h1>
                {selectedEntity.entity_type && (
                  <span
                    style={{
                      background: "#4361ee",
                      color: "#fff",
                      padding: "4px 12px",
                      borderRadius: 4,
                      fontSize: 14,
                      fontWeight: 500,
                    }}
                  >
                    {selectedEntity.entity_type}
                  </span>
                )}
              </div>

              <div style={{ display: "flex", gap: 24, color: "#666", fontSize: 14 }}>
                {selectedEntity.qid && (
                  <div>
                    <strong>QID:</strong>{" "}
                    <a
                      href={`https://www.wikidata.org/wiki/${selectedEntity.qid}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "#4361ee", textDecoration: "none" }}
                    >
                      {selectedEntity.qid}
                    </a>
                  </div>
                )}
                {selectedEntity.entity_cipher && (
                  <div>
                    <strong>Cipher:</strong> <code style={{ fontSize: 12 }}>{selectedEntity.entity_cipher}</code>
                  </div>
                )}
                {selectedEntity.federation_score !== undefined && (
                  <div>
                    <strong>Federation Score:</strong> {selectedEntity.federation_score}
                  </div>
                )}
                {selectedEntity.properties_count && (
                  <div>
                    <strong>Properties:</strong> {selectedEntity.properties_count}
                  </div>
                )}
              </div>

              {selectedEntity.description && (
                <p style={{ marginTop: 16, fontSize: 15, lineHeight: 1.6, color: "#444" }}>
                  {selectedEntity.description}
                </p>
              )}
            </div>

            {/* Properties Section */}
            {selectedEntity.property_summary && (
              <div style={{ marginBottom: 32 }}>
                <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>
                  Properties
                </h2>
                <div
                  style={{
                    background: "#f9f9f9",
                    padding: 16,
                    borderRadius: 6,
                    fontSize: 13,
                    fontFamily: "monospace",
                    whiteSpace: "pre-wrap",
                    maxHeight: 300,
                    overflow: "auto",
                  }}
                >
                  {selectedEntity.property_summary}
                </div>
              </div>
            )}

            {/* Relationships Section */}
            {relationships.length > 0 && (
              <div style={{ marginBottom: 32 }}>
                <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>
                  Relationships ({relationships.length})
                </h2>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {relationships.map((rel, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: 16,
                        border: "1px solid #e0e0e0",
                        borderRadius: 6,
                        display: "flex",
                        alignItems: "center",
                        gap: 12,
                      }}
                    >
                      <div
                        style={{
                          background: "#4361ee",
                          color: "#fff",
                          padding: "4px 10px",
                          borderRadius: 4,
                          fontSize: 12,
                          fontWeight: 500,
                          minWidth: 120,
                          textAlign: "center",
                        }}
                      >
                        {rel.relType}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 500, fontSize: 14 }}>
                          {rel.m.label || rel.m.qid || "Unknown"}
                        </div>
                        {rel.m.qid && (
                          <div style={{ fontSize: 12, color: "#666" }}>
                            {rel.m.qid}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => loadEntityDetails(rel.m)}
                        style={{
                          padding: "6px 12px",
                          background: "#f0f0f0",
                          border: "none",
                          borderRadius: 4,
                          cursor: "pointer",
                          fontSize: 12,
                        }}
                      >
                        View
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Status and Metadata */}
            <div style={{ marginTop: 32, padding: 16, background: "#f9f9f9", borderRadius: 6 }}>
              <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>
                Metadata
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "150px 1fr", gap: 8, fontSize: 13 }}>
                {selectedEntity.status && (
                  <>
                    <div style={{ fontWeight: 500 }}>Status:</div>
                    <div>{selectedEntity.status}</div>
                  </>
                )}
                {selectedEntity.created_at && (
                  <>
                    <div style={{ fontWeight: 500 }}>Created:</div>
                    <div>{new Date(selectedEntity.created_at).toLocaleString()}</div>
                  </>
                )}
                {selectedEntity.entity_id && (
                  <>
                    <div style={{ fontWeight: 500 }}>Entity ID:</div>
                    <div style={{ fontFamily: "monospace", fontSize: 12 }}>
                      {selectedEntity.entity_id}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Neo4jExplorer;
