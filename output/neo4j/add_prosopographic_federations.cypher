// ============================================================
// NEW FEDERATION NODES — Prosopographic Authorities
// Generated: 2026-02-23
//
// Adds three new entries to the Federation layer:
//   1. Trismegistos  (mode: api)      — live JSON/RDF person API
//   2. LGPN          (mode: api)      — live OpenAPI person authority
//   3. SNAP:DRGN     (mode: standard) — interchange standard (NOT an endpoint)
//
// Run after existing federation setup.
// MERGE semantics: safe to re-run.
// ============================================================

// -- 1. Trismegistos --------------------------------------------------
MATCH (fr:FederationRoot {name: "Federations"})
MERGE (fr)-[:HAS_FEDERATION]->(f:Federation {name: "Trismegistos"})
SET
  f.type                = "prosopographic",
  f.mode                = "api",
  f.source              = "https://www.trismegistos.org/dataservices/",
  f.coverage            = 575000,
  f.coverage_type       = "person_attestations",
  f.license             = "CC BY-SA 4.0",
  f.entity_types        = ["PERSON", "PLACE", "TEXT"],
  f.geographic_scope    = "Eastern Mediterranean, BC 800 – AD 800",
  f.crosswalk_standard  = "SNAP:DRGN",
  f.identifier_prefix   = "TM_PER_",
  f.stable_uri_pattern  = "https://www.trismegistos.org/person/{id}",

  // API endpoints
  f.api_person_json     = "https://www.trismegistos.org/dataservices/per/index.php?id={id}&format=json",
  f.api_person_rdf      = "https://www.trismegistos.org/dataservices/rdf/per/index.php?id={id}",
  f.api_geo_crossmatch  = "https://www.trismegistos.org/dataservices/georelations/{id}",
  f.api_tex_crossmatch  = "https://www.trismegistos.org/dataservices/texrelations/{id}",

  // Crossmatch partners (from GeoRelations — links to these federated sources)
  f.crossmatch_partners = ["Pleiades", "GeoNames", "Wikipedia", "DARE", "Syriaca"],

  // Chrystallum integration notes
  f.federation_state    = "FS1_REGISTERED",
  f.authority_jump_enabled = false,
  f.notes               = "Primary prosopographic authority for non-elite persons. Complements Wikidata coverage of elites. GeoRelations crossmatcher links TM place IDs to Pleiades (already federated).",
  f.added_at            = datetime()
RETURN f.name AS federation, f.mode AS mode, f.coverage AS coverage;

// -- 2. LGPN ----------------------------------------------------------
MATCH (fr:FederationRoot {name: "Federations"})
MERGE (fr)-[:HAS_FEDERATION]->(f:Federation {name: "LGPN"})
SET
  f.type                = "prosopographic",
  f.mode                = "api",
  f.source              = "https://search.lgpn.ox.ac.uk/",
  f.coverage            = 400000,
  f.coverage_type       = "greek_personal_names",
  f.license             = "Non-commercial research use",
  f.entity_types        = ["PERSON"],
  f.geographic_scope    = "Greek-speaking world, 8th c BCE – 6th c CE",
  f.crosswalk_standard  = "SNAP:DRGN",
  f.identifier_prefix   = "LGPN_",
  f.stable_uri_pattern  = "http://www.lgpn.ox.ac.uk/id/{volume}-{id}",

  // API endpoints
  f.api_base            = "http://clas-lgpn5.classics.ox.ac.uk:8080/exist/apps/lgpn-api/",
  f.api_spec            = "OpenAPI",
  f.data_format         = "TEI/XML",

  // Chrystallum integration notes
  f.federation_state    = "FS1_REGISTERED",
  f.authority_jump_enabled = false,
  f.notes               = "400,000 ancient Greeks, 8 volumes by region. Covers literary + documentary + epigraphic sources. Stable URIs per person by volume+ID. Complements Trismegistos (stronger on papyrological/documentary; LGPN stronger on literary/epigraphic Greek sources).",
  f.added_at            = datetime()
RETURN f.name AS federation, f.mode AS mode, f.coverage AS coverage;

// -- 3. SNAP:DRGN (standard, not endpoint) ----------------------------
MATCH (fr:FederationRoot {name: "Federations"})
MERGE (fr)-[:HAS_FEDERATION]->(f:Federation {name: "SNAP:DRGN"})
SET
  f.type                = "prosopographic",
  f.mode                = "standard",        // NOT an api or local — it is an interchange standard
  f.source              = "https://snapdrgn.net/cookbook.html",
  f.coverage            = 0,                 // no live endpoint
  f.license             = "Open",
  f.entity_types        = ["PERSON"],
  f.geographic_scope    = "Greco-Roman antiquity",
  f.identifier_prefix   = "SNAP_",
  f.stable_uri_pattern  = null,              // triplestore defunct, no live URIs

  // What SNAP:DRGN actually provides
  f.provides            = "Interchange format and ontology for prosopographical data exchange between projects",
  f.ontology_namespace  = "http://data.snapdrgn.net/ontology/snap#",
  f.key_classes         = ["snap:Person", "snap:Bond", "snap:PersonalRelationship"],
  f.used_by_federations = ["Trismegistos", "LGPN"],  // projects that implement SNAP format

  // Chrystallum integration notes
  f.federation_state    = "FS0_STANDARD_ONLY",
  f.authority_jump_enabled = false,
  f.notes               = "SNAP:DRGN triplestore is defunct (service agreement expired 2023). SNAP lives in Chrystallum as a crosswalk standard used by Trismegistos and LGPN federations, NOT as a queryable endpoint. Used for aligning person identifiers across prosopographic sources.",
  f.added_at            = datetime()
RETURN f.name AS federation, f.mode AS mode, f.notes AS notes;

// -- Update FederationRoot count --------------------------------------
MATCH (fr:FederationRoot {name: "Federations"})
MATCH (fr)-[:HAS_FEDERATION]->(f:Federation)
WITH fr, count(f) AS total
SET fr.count = total
RETURN fr.name, fr.count AS updated_count;

// -- Verify all federations -------------------------------------------
MATCH (fr:FederationRoot {name: "Federations"})-[:HAS_FEDERATION]->(f:Federation)
RETURN f.name AS name, f.type AS type, f.mode AS mode, f.coverage AS coverage
ORDER BY f.type, f.name;
