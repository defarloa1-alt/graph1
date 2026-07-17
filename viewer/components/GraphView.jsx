import React, { useEffect, useRef, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";

const GraphView = ({ entity, onNodeClick }) => {
  const cyRef = useRef(null);
  const [elements, setElements] = useState([]);
  const [layout, setLayout] = useState("cose");
  const [loading, setLoading] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  // Cytoscape stylesheet
  const stylesheet = [
    {
      selector: "node",
      style: {
        "background-color": "#4361ee",
        label: "data(label)",
        "text-valign": "center",
        "text-halign": "center",
        color: "#fff",
        "text-outline-color": "#4361ee",
        "text-outline-width": 2,
        "font-size": 12,
        width: 40,
        height: 40,
      },
    },
    {
      selector: "node[type='PERSON']",
      style: {
        "background-color": "#e63946",
      },
    },
    {
      selector: "node[type='PLACE']",
      style: {
        "background-color": "#06a77d",
      },
    },
    {
      selector: "node[type='EVENT']",
      style: {
        "background-color": "#f77f00",
      },
    },
    {
      selector: "node[type='PERIOD']",
      style: {
        "background-color": "#9d4edd",
      },
    },
    {
      selector: "node[type='CONCEPT']",
      style: {
        "background-color": "#4361ee",
      },
    },
    {
      selector: "node[type='WORK']",
      style: {
        "background-color": "#2a9d8f",
      },
    },
    {
      selector: "node:selected",
      style: {
        "border-width": 4,
        "border-color": "#ffd60a",
      },
    },
    {
      selector: "node.highlighted",
      style: {
        "background-color": "#ffd60a",
        "text-outline-color": "#ffd60a",
      },
    },
    {
      selector: "edge",
      style: {
        width: 2,
        "line-color": "#999",
        "target-arrow-color": "#999",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        label: "data(label)",
        "font-size": 10,
        color: "#666",
        "text-rotation": "autorotate",
        "text-margin-y": -10,
      },
    },
    {
      selector: "edge.highlighted",
      style: {
        "line-color": "#ffd60a",
        "target-arrow-color": "#ffd60a",
        width: 3,
      },
    },
  ];

  // Layout configurations
  const layoutConfigs = {
    cose: {
      name: "cose",
      animate: true,
      animationDuration: 500,
      nodeRepulsion: 8000,
      idealEdgeLength: 100,
      edgeElasticity: 100,
      nestingFactor: 1.2,
      gravity: 1,
      numIter: 1000,
      fit: true,
      padding: 30,
    },
    breadthfirst: {
      name: "breadthfirst",
      directed: true,
      spacingFactor: 1.5,
      animate: true,
      animationDuration: 500,
      fit: true,
      padding: 30,
    },
    circle: {
      name: "circle",
      animate: true,
      animationDuration: 500,
      fit: true,
      padding: 30,
    },
    concentric: {
      name: "concentric",
      animate: true,
      animationDuration: 500,
      fit: true,
      padding: 30,
      concentric: (node) => node.data("federation_score") || 1,
      levelWidth: () => 2,
    },
    grid: {
      name: "grid",
      animate: true,
      animationDuration: 500,
      fit: true,
      padding: 30,
    },
  };

  // Fetch entity neighborhood from API
  const fetchNeighborhood = async (entityId) => {
    try {
      setLoading(true);
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cypher: `
            MATCH (n)-[r]-(m)
            WHERE n.entity_cipher = $id OR n.qid = $id
            RETURN n, type(r) as relType, r, m
            LIMIT 50
          `,
          params: { id: entityId || null },
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return data.records;
      }
    } catch (err) {
      console.error("Failed to fetch neighborhood:", err);
    } finally {
      setLoading(false);
    }
    return [];
  };

  // Convert Neo4j data to Cytoscape elements
  const buildGraphElements = (records, centerNode) => {
    const nodes = new Map();
    const edges = [];

    // Add center node
    if (centerNode) {
      const nodeId = centerNode.entity_cipher || centerNode.qid;
      nodes.set(nodeId, {
        data: {
          id: nodeId,
          label: centerNode.label || centerNode.qid || "Unknown",
          type: centerNode.entity_type || "CONCEPT",
          qid: centerNode.qid,
          entity_cipher: centerNode.entity_cipher,
          federation_score: centerNode.federation_score || 0,
        },
      });
    }

    // Add connected nodes and edges
    records.forEach((record, idx) => {
      const sourceNode = record.n;
      const targetNode = record.m;
      const relType = record.relType;

      if (sourceNode && targetNode) {
        const sourceId = sourceNode.entity_cipher || sourceNode.qid || `node_${idx}_s`;
        const targetId = targetNode.entity_cipher || targetNode.qid || `node_${idx}_t`;

        // Add source node
        if (!nodes.has(sourceId)) {
          nodes.set(sourceId, {
            data: {
              id: sourceId,
              label: sourceNode.label || sourceNode.qid || "Unknown",
              type: sourceNode.entity_type || "CONCEPT",
              qid: sourceNode.qid,
              entity_cipher: sourceNode.entity_cipher,
              federation_score: sourceNode.federation_score || 0,
            },
          });
        }

        // Add target node
        if (!nodes.has(targetId)) {
          nodes.set(targetId, {
            data: {
              id: targetId,
              label: targetNode.label || targetNode.qid || "Unknown",
              type: targetNode.entity_type || "CONCEPT",
              qid: targetNode.qid,
              entity_cipher: targetNode.entity_cipher,
              federation_score: targetNode.federation_score || 0,
            },
          });
        }

        // Add edge
        edges.push({
          data: {
            id: `edge_${idx}`,
            source: sourceId,
            target: targetId,
            label: relType || "RELATED_TO",
          },
        });
      }
    });

    return [...Array.from(nodes.values()), ...edges];
  };

  // Load initial graph when entity changes
  useEffect(() => {
    if (entity) {
      const loadGraph = async () => {
        const records = await fetchNeighborhood(
          entity.entity_cipher || entity.qid
        );
        const graphElements = buildGraphElements(records, entity);
        setElements(graphElements);
        setExpandedNodes(new Set([entity.entity_cipher || entity.qid]));
      };
      loadGraph();
    }
  }, [entity]);

  // Apply layout when it changes
  useEffect(() => {
    if (cyRef.current && elements.length > 0) {
      const cy = cyRef.current;
      const layoutConfig = layoutConfigs[layout];
      cy.layout(layoutConfig).run();
    }
  }, [layout, elements]);

  // Setup Cytoscape event handlers
  const handleCyInit = (cy) => {
    cyRef.current = cy;

    // Node click handler
    cy.on("tap", "node", async (evt) => {
      const node = evt.target;
      const nodeData = node.data();

      // Notify parent component
      if (onNodeClick) {
        onNodeClick({
          qid: nodeData.qid,
          entity_cipher: nodeData.entity_cipher,
          label: nodeData.label,
          entity_type: nodeData.type,
        });
      }

      // Highlight connected elements
      cy.elements().removeClass("highlighted");
      node.addClass("highlighted");
      node.connectedEdges().addClass("highlighted");
    });

    // Double-click to expand node
    cy.on("dbltap", "node", async (evt) => {
      const node = evt.target;
      const nodeId = node.data("id");

      if (expandedNodes.has(nodeId)) {
        return; // Already expanded
      }

      // Fetch and add neighborhood
      const records = await fetchNeighborhood(nodeId);
      if (records.length > 0) {
        const newElements = buildGraphElements(records, null);
        
        // Merge with existing elements (avoid duplicates)
        const existingIds = new Set(elements.map(el => el.data.id));
        const uniqueNewElements = newElements.filter(
          el => !existingIds.has(el.data.id)
        );

        setElements([...elements, ...uniqueNewElements]);
        setExpandedNodes(new Set([...expandedNodes, nodeId]));
      }
    });

    // Apply initial layout
    if (elements.length > 0) {
      cy.layout(layoutConfigs[layout]).run();
    }
  };

  const handleFitGraph = () => {
    if (cyRef.current) {
      cyRef.current.fit(null, 30);
    }
  };

  const handleCenterNode = () => {
    if (cyRef.current && entity) {
      const nodeId = entity.entity_cipher || entity.qid;
      const node = cyRef.current.getElementById(nodeId);
      if (node) {
        cyRef.current.center(node);
        cyRef.current.zoom(1.5);
      }
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Controls */}
      <div
        style={{
          padding: 12,
          background: "#f5f5f5",
          borderBottom: "1px solid #ddd",
          display: "flex",
          gap: 12,
          alignItems: "center",
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 600 }}>Graph View</div>

        <select
          value={layout}
          onChange={(e) => setLayout(e.target.value)}
          style={{
            padding: "6px 10px",
            border: "1px solid #ddd",
            borderRadius: 4,
            fontSize: 13,
          }}
        >
          <option value="cose">Force Directed (COSE)</option>
          <option value="breadthfirst">Hierarchical (Tree)</option>
          <option value="circle">Circle</option>
          <option value="concentric">Concentric (by Federation)</option>
          <option value="grid">Grid</option>
        </select>

        <button
          onClick={handleFitGraph}
          style={{
            padding: "6px 12px",
            background: "#fff",
            border: "1px solid #ddd",
            borderRadius: 4,
            cursor: "pointer",
            fontSize: 13,
          }}
        >
          Fit to View
        </button>

        <button
          onClick={handleCenterNode}
          style={{
            padding: "6px 12px",
            background: "#fff",
            border: "1px solid #ddd",
            borderRadius: 4,
            cursor: "pointer",
            fontSize: 13,
          }}
        >
          Center Selected
        </button>

        {loading && (
          <div style={{ marginLeft: "auto", fontSize: 13, color: "#666" }}>
            Loading...
          </div>
        )}
      </div>

      {/* Legend */}
      <div
        style={{
          padding: "8px 12px",
          background: "#fff",
          borderBottom: "1px solid #ddd",
          display: "flex",
          gap: 16,
          fontSize: 12,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 16, height: 16, background: "#4361ee", borderRadius: "50%" }} />
          <span>Concept</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 16, height: 16, background: "#e63946", borderRadius: "50%" }} />
          <span>Person</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 16, height: 16, background: "#06a77d", borderRadius: "50%" }} />
          <span>Place</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 16, height: 16, background: "#f77f00", borderRadius: "50%" }} />
          <span>Event</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 16, height: 16, background: "#9d4edd", borderRadius: "50%" }} />
          <span>Period</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 16, height: 16, background: "#2a9d8f", borderRadius: "50%" }} />
          <span>Work</span>
        </div>
        <div style={{ marginLeft: "auto", fontStyle: "italic", color: "#666" }}>
          Double-click to expand node • Click to select • Drag to pan
        </div>
      </div>

      {/* Cytoscape Graph */}
      <div style={{ flex: 1, position: "relative" }}>
        {elements.length === 0 ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "#999",
              fontSize: 14,
            }}
          >
            {loading ? "Loading graph..." : "Select an entity to view its graph"}
          </div>
        ) : (
          <CytoscapeComponent
            elements={elements}
            style={{ width: "100%", height: "100%" }}
            stylesheet={stylesheet}
            cy={handleCyInit}
            layout={layoutConfigs[layout]}
          />
        )}
      </div>
    </div>
  );
};

export default GraphView;
