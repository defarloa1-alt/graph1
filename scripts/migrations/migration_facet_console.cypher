// ============================================================
// MIGRATION: Facet Console - per-facet harvest state, HarvestJob, SYS_FacetPolicy
// File: scripts/migrations/migration_facet_console.cypher
// Purpose: Support Subject Facet Agent console workflow
// ============================================================

// 1. HarvestJob node type
MERGE (nt:SYS_NodeType {name: "HarvestJob"})
ON CREATE SET
  nt.description = "Harvest job for a facet+discipline+repo combination. Append-only; status transitions.",
  nt.layer = "SYS",
  nt.created_at = datetime();

// 2. SYS_FacetPolicy - facet-level config
MERGE (fp:SYS_FacetPolicy {facet_label: "Political"})
ON CREATE SET
  fp.harvest_priority = 1,
  fp.min_discipline_coverage = 3,
  fp.preferred_repos = ["OPENALEX_WORKS", "OPEN_LIBRARY", "OPEN_SYLLABUS", "PERSEUS"],
  fp.notes = "Core facet for Roman Republic; high priority for discipline harvest";

MERGE (fp:SYS_FacetPolicy {facet_label: "Biographic"})
ON CREATE SET
  fp.harvest_priority = 1,
  fp.min_discipline_coverage = 2,
  fp.preferred_repos = ["OPENALEX_WORKS", "PERSEUS", "HATHI_TRUST", "INTERNET_ARCHIVE"],
  fp.notes = "Person-centric; overlaps with Political, Military for ancient history";

MERGE (fp:SYS_FacetPolicy {facet_label: "Military"})
ON CREATE SET
  fp.harvest_priority = 1,
  fp.min_discipline_coverage = 2,
  fp.preferred_repos = ["OPENALEX_WORKS", "PERSEUS", "JSTOR_SEARCH", "WORLDCAT"],
  fp.notes = "Campaigns, battles, commanders; ancient history primary";

// 3. Register SYS_FacetPolicy in SYS_NodeType
MERGE (nt:SYS_NodeType {name: "SYS_FacetPolicy"})
ON CREATE SET
  nt.description = "Per-facet harvest policy: priority, preferred repos, thresholds",
  nt.layer = "SYS",
  nt.created_at = datetime();
