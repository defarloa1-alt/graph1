// List all relationship types that are raw PIDs (P31, P279, P6379, etc.)
// or WIKIDATA_P* prefixed types — i.e. edges that lack human-readable names.
//
// Run in Neo4j Browser to audit which edges need label enrichment.
// Then run: python scripts/maintenance/enrich_edge_labels.py

// All PID-like relationship types with edge counts
MATCH ()-[r]->()
WITH type(r) AS rel_type, count(r) AS edge_count
WHERE rel_type STARTS WITH 'P' OR rel_type STARTS WITH 'WIKIDATA_P'
RETURN rel_type, edge_count
ORDER BY edge_count DESC;

// Edges still missing label (after enrich_edge_labels.py)
// MATCH ()-[r]->()
// WHERE (type(r) STARTS WITH 'P' OR type(r) STARTS WITH 'WIKIDATA_P')
//   AND r.label IS NULL
// RETURN type(r) AS rel_type, count(r) AS missing_label_count
// ORDER BY missing_label_count DESC;
