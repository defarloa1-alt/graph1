# Chrystallum UI Implementation Plan

## Phase 1: Cytoscape (real-time graph)

- [ ] Add cytoscape + cytoscape-fcose to viewer
- [ ] Create GraphView component with Cytoscape.js (replace d3-force)
- [ ] Add buildElements + CYTOSCAPE_STYLE from Key Files
- [ ] Wire useCypher to Chrystallum subgraph query
- [ ] Add Vite proxy for Aura (or MCP) - CORS-free Neo4j
- [ ] Mount graph in system map tab
- [ ] Node click → detail panel

## Phase 2: Hybrid C (design system + Figma)

- [ ] Extract C, FACET_COLOR, STATUS_COL to design-tokens.js
- [ ] Create Figma variables from tokens
- [ ] Build Figma components (Mono, Tag, CopyBtn, Loader, Err)
- [ ] Build shell frame in Figma (tabs, sidebar, graph area)
- [ ] Add graph reference frame in Figma (node shapes, edge styles)
- [ ] Cursor Implement design for shell refinements
- [ ] Code Connect: Figma ↔ primitives
