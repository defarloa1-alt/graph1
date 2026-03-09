// ============================================================
// Script 17 — DOAJ rights oracle + OpenAlex discipline IDs
// ============================================================
// 1. Update DOAJ SYS_FederationSource → rights_oracle role
// 2. Add DOAJGoldOAByDefinition policy
// 3. Add corpus tier thresholds (for SFA reference)
// 4. Load validated openalex_id / openalex_status onto Discipline nodes
//    (from output/discipline_taxonomy_openalex_final.csv via LOAD CSV)
// ============================================================

// ── 1. DOAJ FederationSource ─────────────────────────────────────────────────
MERGE (doaj:SYS_FederationSource {source_id: 'doaj'})
SET   doaj.name               = 'DOAJ'
    , doaj.label              = 'Directory of Open Access Journals'
    , doaj.role               = 'rights_oracle'
    , doaj.scoping_role       = 'gold_oa_corpus'
    , doaj.status             = 'operational'
    , doaj.scoping_weight     = 1.0
    , doaj.harvest_mode       = 'journal_index'
    , doaj.rights_guarantee   = 'gold_oa_by_definition'
    , doaj.per_article_check  = false
    , doaj.endpoint           = 'https://doaj.org/api/search/journals/{query}'
    , doaj.rate_limit         = '2 req/sec'
    , doaj.auth_required      = false
    , doaj.pid                = 'Q1227538'
    , doaj.phase              = 'A'
    , doaj.note               = 'Certification rides inside OpenAlex work response (source.is_in_doaj). No per-work DOAJ lookup needed.'
RETURN doaj.source_id AS updated;

// ── 2. DOAJGoldOAByDefinition policy ─────────────────────────────────────────
MERGE (p:SYS_Policy {name: 'DOAJGoldOAByDefinition'})
SET   p.active        = true
    , p.rule          = 'Any work where primary_location.source.is_in_doaj=true (from OpenAlex response) may be harvested, abstracted, and cited without per-article rights check. DOAJ inclusion = permanent gold OA certification.'
    , p.authority     = 'doaj.org inclusion criteria'
    , p.caveat        = 'Gold OA != unrestricted license. CC-BY preferred; CC-BY-NC acceptable for non-commercial scholarly graph. Verify license before redistribution.'
    , p.source_id     = 'doaj'
WITH p
MATCH (doaj:SYS_FederationSource {source_id: 'doaj'})
MERGE (p)-[:GOVERNED_BY]->(doaj)
RETURN p.name AS policy;

// ── 3. Corpus tier thresholds (SFA reads these) ───────────────────────────────
MERGE (t1:SYS_Threshold {name: 'corpus_tier_gold_oa'})
SET   t1.value         = 'is_in_doaj=true'
    , t1.unit          = 'openalexfield'
    , t1.permission    = 'harvest+abstract+cite'
    , t1.decision_table = null;

MERGE (t2:SYS_Threshold {name: 'corpus_tier_green_oa'})
SET   t2.value         = 'oa_status=green'
    , t2.unit          = 'openalexfield'
    , t2.permission    = 'metadata+abstract'
    , t2.decision_table = null;

MERGE (t3:SYS_Threshold {name: 'corpus_tier_closed'})
SET   t3.value         = 'all_other'
    , t3.unit          = 'openalexfield'
    , t3.permission    = 'cite_only'
    , t3.decision_table = null;

// ── 4-5. OpenAlex IDs + ROUTES_TO wiring ─────────────────────────────────────
// NOTE: LOAD CSV cannot run on Aura (no local file access).
// Run the Python companion instead:
//   python scripts/neo4j/load_openalex_ids_to_graph.py
//
// That script sets openalex_id / openalex_status on all 972 disciplines
// and wires ROUTES_TO open_alex for the 605 verified ones.

// ── 6. Verify ─────────────────────────────────────────────────────────────────
MATCH (d:Discipline)
RETURN d.openalex_status AS status, count(d) AS count
ORDER BY count DESC;
