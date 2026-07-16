// ============================================================
// MIGRATION: Bio Harvest Decision Model
// File: scripts/migrations/bio_decision_model.cypher
// Purpose: Externalise all hard-coded rules from
//          bio_context_harvest.py into graph-resident decision
//          nodes. Script reads these before executing.
// ============================================================


// ── 0. Prerequisites ─────────────────────────────────────────────────────────
// Assumes SYS_Policy, SYS_Threshold, SYS_WikidataProperty
// node types already registered in SYS_NodeType.


// ============================================================
// 1. SYS_WikidataProperty
//    Classification of each harvested P-code:
//      fetch_method  : truthy | statement_traversal
//      sfa_primary   : canonical facet label owning this prop
//      canonical_key : key name in harvest JSON / PersonHarvestPlan
// ============================================================

// ── Scalar / truthy props ─────────────────────────────────────────────────────
MERGE (p:SYS_WikidataProperty {pid: "P569"})
SET p.label          = "date of birth",
    p.fetch_method   = "truthy",
    p.canonical_key  = "birth_date",
    p.sfa_primary    = "Biographic",
    p.value_type     = "date";

MERGE (p:SYS_WikidataProperty {pid: "P570"})
SET p.label          = "date of death",
    p.fetch_method   = "truthy",
    p.canonical_key  = "death_date",
    p.sfa_primary    = "Biographic",
    p.value_type     = "date";

MERGE (p:SYS_WikidataProperty {pid: "P19"})
SET p.label          = "place of birth",
    p.fetch_method   = "truthy",
    p.canonical_key  = "birth_place_qid",
    p.sfa_primary    = "Biographic",
    p.value_type     = "item";

MERGE (p:SYS_WikidataProperty {pid: "P20"})
SET p.label          = "place of death",
    p.fetch_method   = "truthy",
    p.canonical_key  = "death_place_qid",
    p.sfa_primary    = "Biographic",
    p.value_type     = "item";

MERGE (p:SYS_WikidataProperty {pid: "P509"})
SET p.label          = "cause of death",
    p.fetch_method   = "truthy",
    p.canonical_key  = "cause_of_death_qid",
    p.sfa_primary    = "Biographic",
    p.value_type     = "item";

MERGE (p:SYS_WikidataProperty {pid: "P119"})
SET p.label          = "place of burial",
    p.fetch_method   = "truthy",
    p.canonical_key  = "burial_place_qid",
    p.sfa_primary    = "Biographic",
    p.value_type     = "item";

// ── External IDs (truthy, string values) ─────────────────────────────────────
MERGE (p:SYS_WikidataProperty {pid: "P214"})
SET p.label="VIAF", p.fetch_method="truthy",
    p.canonical_key="viaf_id", p.sfa_primary="Biographic", p.value_type="external_id";

MERGE (p:SYS_WikidataProperty {pid: "P227"})
SET p.label="GND", p.fetch_method="truthy",
    p.canonical_key="gnd_id", p.sfa_primary="Biographic", p.value_type="external_id";

MERGE (p:SYS_WikidataProperty {pid: "P244"})
SET p.label="LCNAF", p.fetch_method="truthy",
    p.canonical_key="lcnaf_id", p.sfa_primary="Biographic", p.value_type="external_id";

MERGE (p:SYS_WikidataProperty {pid: "P1415"})
SET p.label="OCD", p.fetch_method="truthy",
    p.canonical_key="ocd_id", p.sfa_primary="Biographic", p.value_type="external_id";

MERGE (p:SYS_WikidataProperty {pid: "P3348"})
SET p.label="Nomisma", p.fetch_method="truthy",
    p.canonical_key="nomisma_id", p.sfa_primary="Biographic", p.value_type="external_id";

MERGE (p:SYS_WikidataProperty {pid: "P1047"})
SET p.label="LGPN", p.fetch_method="truthy",
    p.canonical_key="lgpn_id", p.sfa_primary="Biographic", p.value_type="external_id";

MERGE (p:SYS_WikidataProperty {pid: "P11252"})
SET p.label="Trismegistos author ID", p.fetch_method="truthy",
    p.canonical_key="trismeg_id", p.sfa_primary="Biographic", p.value_type="external_id",
    p.notes="Author-specific ID. Distinct from P1696 (person/inscription ID).";

MERGE (p:SYS_WikidataProperty {pid: "P10382"})
SET p.label="PIR online", p.fetch_method="truthy",
    p.canonical_key="pir_id", p.sfa_primary="Biographic", p.value_type="external_id",
    p.notes="Prosopographia Imperii Romani Online (pir.bbaw.de). Covers Augustus–Diocletian.";

// ── Event / participation props — REQUIRE statement traversal ─────────────────
// Wikidata stores these with qualifiers, making them invisible to wdt:.
// fetch_method = "statement_traversal" signals the fetcher to use p:/ps:.

MERGE (p:SYS_WikidataProperty {pid: "P607"})
SET p.label          = "conflict",
    p.fetch_method   = "statement_traversal",
    p.canonical_key  = "conflict_qid",
    p.sfa_primary    = "Military",
    p.value_type     = "item";

MERGE (p:SYS_WikidataProperty {pid: "P793"})
SET p.label          = "significant event",
    p.fetch_method   = "statement_traversal",
    p.canonical_key  = "significant_event_qid",
    p.sfa_primary    = "Military",
    p.value_type     = "item";

MERGE (p:SYS_WikidataProperty {pid: "P1344"})
SET p.label          = "participant in",
    p.fetch_method   = "statement_traversal",
    p.canonical_key  = "participated_in_qid",
    p.sfa_primary    = "Military",
    p.value_type     = "item";

MERGE (p:SYS_WikidataProperty {pid: "P166"})
SET p.label          = "award received",
    p.fetch_method   = "statement_traversal",
    p.canonical_key  = "award_qid",
    p.sfa_primary    = "Biographic",
    p.value_type     = "item";

// ── Onomastic props — promote to first-class nodes ───────────────────────────
// promotes_first_class_node = true signals executor to MERGE a node, not just
// write a property on Person.

MERGE (p:SYS_WikidataProperty {pid: "P2358"})
SET p.label="praenomen", p.fetch_method="truthy",
    p.canonical_key="praenomen_qid", p.sfa_primary="Biographic",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="Praenomen", p.edge_type="HAS_PRAENOMEN";

MERGE (p:SYS_WikidataProperty {pid: "P2359"})
SET p.label="nomen gentilicium", p.fetch_method="truthy",
    p.canonical_key="nomen_qid", p.sfa_primary="Biographic",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="Nomen", p.edge_type="HAS_NOMEN";

MERGE (p:SYS_WikidataProperty {pid: "P2365"})
SET p.label="cognomen", p.fetch_method="truthy",
    p.canonical_key="cognomen_qid", p.sfa_primary="Biographic",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="Cognomen", p.edge_type="HAS_COGNOMEN";

MERGE (p:SYS_WikidataProperty {pid: "P5025"})
SET p.label="gens", p.fetch_method="truthy",
    p.canonical_key="gens_qid", p.sfa_primary="Biographic",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="Gens", p.edge_type="MEMBER_OF_GENS",
    p.notes="Central to Roman elite network analysis. Reused across thousands of persons.";

MERGE (p:SYS_WikidataProperty {pid: "P11491"})
SET p.label="member of Roman tribe", p.fetch_method="truthy",
    p.canonical_key="tribe_qid", p.sfa_primary="Biographic",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="Tribe", p.edge_type="MEMBER_OF_TRIBE",
    p.notes="Voting tribe — supports comitial and regional analysis.";

MERGE (p:SYS_WikidataProperty {pid: "P1559"})
SET p.label="name in native language", p.fetch_method="truthy",
    p.canonical_key="native_name", p.sfa_primary="Biographic",
    p.value_type="string", p.promotes_first_class_node=false,
    p.notes="Full Latin tria nomina. Drives epigraphic and textual matching.";

// ── Political / social / military props ──────────────────────────────────────

MERGE (p:SYS_WikidataProperty {pid: "P102"})
SET p.label="member of political party", p.fetch_method="truthy",
    p.canonical_key="faction_qid", p.sfa_primary="Political",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="PoliticalFaction", p.edge_type="MEMBER_OF_FACTION",
    p.notes="optimates, populares, First Triumvirate etc.";

MERGE (p:SYS_WikidataProperty {pid: "P463"})
SET p.label="member of", p.fetch_method="truthy",
    p.canonical_key="org_member_qid", p.sfa_primary="Political",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="Organization", p.edge_type="MEMBER_OF";

MERGE (p:SYS_WikidataProperty {pid: "P3716"})
SET p.label="social classification", p.fetch_method="truthy",
    p.canonical_key="social_order_qid", p.sfa_primary="Social",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="SocialOrder", p.edge_type="IN_SOCIAL_ORDER",
    p.notes="nobilis, eques, freedman, slave etc.";

MERGE (p:SYS_WikidataProperty {pid: "P410"})
SET p.label="military rank", p.fetch_method="truthy",
    p.canonical_key="rank_qid", p.sfa_primary="Military",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="MilitaryRank", p.edge_type="HELD_RANK";

MERGE (p:SYS_WikidataProperty {pid: "P241"})
SET p.label="military branch", p.fetch_method="truthy",
    p.canonical_key="branch_qid", p.sfa_primary="Military",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="MilitaryBranch", p.edge_type="SERVED_IN";

MERGE (p:SYS_WikidataProperty {pid: "P140"})
SET p.label="religion or worldview", p.fetch_method="truthy",
    p.canonical_key="religion_qid", p.sfa_primary="Religious",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="Religion", p.edge_type="HAS_RELIGION";

MERGE (p:SYS_WikidataProperty {pid: "P1196"})
SET p.label="manner of death", p.fetch_method="truthy",
    p.canonical_key="manner_of_death_qid", p.sfa_primary="Biographic",
    p.value_type="item", p.promotes_first_class_node=false;

MERGE (p:SYS_WikidataProperty {pid: "P2348"})
SET p.label="time period", p.fetch_method="truthy",
    p.canonical_key="period_qid", p.sfa_primary="Biographic",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="Period", p.edge_type="IN_PERIOD",
    p.notes="Historiographical period (Late Roman Republic). Align to PeriodO when available.";

MERGE (p:SYS_WikidataProperty {pid: "P1343"})
SET p.label="described by source", p.fetch_method="statement_traversal",
    p.canonical_key="described_by_qid", p.sfa_primary="Intellectual",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="ReferenceWork", p.edge_type="HAS_ENTRY_IN",
    p.notes="Pauly-Wissowa, Britannica 1911, etc. Core of INTELLECTUAL facet.";

// P39 position held — staged for Political SFA; not harvested here
MERGE (p:SYS_WikidataProperty {pid: "P39"})
SET p.label="position held", p.fetch_method="qualifier_harvest",
    p.canonical_key="office_held_qid", p.sfa_primary="Political",
    p.value_type="item", p.promotes_first_class_node=true,
    p.target_node_type="OfficeHolding", p.edge_type="HELD_OFFICE",
    p.harvested_by="political_sfa",
    p.notes="OfficeHolding event node: Person->OfficeHolding->OfficeType. Qualifiers: P580 start, P582 end, P1706 together_with. Not harvested by bio agent — staged as BIO_CANDIDATE_REL for Political SFA.";

// ── Marriage qualifier prop ────────────────────────────────────────────────────
MERGE (p:SYS_WikidataProperty {pid: "P26"})
SET p.label          = "spouse",
    p.fetch_method   = "qualifier_harvest",
    p.canonical_key  = "spouse_claims",
    p.sfa_primary    = "Biographic",
    p.value_type     = "item",
    p.notes          = "Harvested via fetch_spouse_qualifiers(); qualifiers P580/P582/P1545/P1534/P2842";


// ============================================================
// 2. SYS_Policy : BacklinkRouting
//    Decision table: (pred_pid, item_type_class) → (sfa_queue, edge_type)
//    item_type_class is a coarsened P31 category applied by the
//    harvester after fetching the backlink item's P31 label.
//    Rows are ordered; first matching row wins.
// ============================================================

MERGE (pol:SYS_Policy {name: "BacklinkRouting"})
SET pol.description  = "Routes BIO_CANDIDATE_REL staging edges to the owning SFA queue based on Wikidata predicate and backlink item type class. Replaces hardcoded BACKLINK_PREDICATE_MAP sfa_queue values.",
    pol.active       = true,
    pol.version      = 1,
    pol.decision_table = '
[
  {"row":1,  "pred_pid":"P22",   "item_type_class":"*",       "edge_type":"CHILD_OF",        "direction":"inbound",  "qualifier":"father",  "sfa_queue":"Biographic"},
  {"row":2,  "pred_pid":"P25",   "item_type_class":"*",       "edge_type":"CHILD_OF",        "direction":"inbound",  "qualifier":"mother",  "sfa_queue":"Biographic"},
  {"row":3,  "pred_pid":"P26",   "item_type_class":"*",       "edge_type":"SPOUSE_OF",       "direction":"inbound",  "qualifier":null,      "sfa_queue":"Biographic"},
  {"row":4,  "pred_pid":"P3373", "item_type_class":"*",       "edge_type":"SIBLING_OF",      "direction":"inbound",  "qualifier":null,      "sfa_queue":"Biographic"},
  {"row":5,  "pred_pid":"P40",   "item_type_class":"*",       "edge_type":"PARENT_OF",       "direction":"outbound", "qualifier":null,      "sfa_queue":"Biographic"},
  {"row":6,  "pred_pid":"P1038", "item_type_class":"*",       "edge_type":"RELATED_TO",      "direction":"inbound",  "qualifier":"kinship", "sfa_queue":"Biographic"},
  {"row":7,  "pred_pid":"P3448", "item_type_class":"*",       "edge_type":"STEPPARENT_OF",   "direction":"inbound",  "qualifier":null,      "sfa_queue":"Biographic"},
  {"row":8,  "pred_pid":"P1066", "item_type_class":"*",       "edge_type":"TEACHER_OF",      "direction":"outbound", "qualifier":null,      "sfa_queue":"Biographic"},
  {"row":9,  "pred_pid":"P802",  "item_type_class":"*",       "edge_type":"STUDENT_OF",      "direction":"inbound",  "qualifier":null,      "sfa_queue":"Biographic"},
  {"row":10, "pred_pid":"P737",  "item_type_class":"*",       "edge_type":"INFLUENCED",      "direction":"outbound", "qualifier":null,      "sfa_queue":"Biographic"},
  {"row":11, "pred_pid":"P710",  "item_type_class":"*",       "edge_type":"PARTICIPATED_IN", "direction":"outbound", "qualifier":null,      "sfa_queue":"Military"},
  {"row":12, "pred_pid":"P664",  "item_type_class":"*",       "edge_type":"ORGANIZED",       "direction":"outbound", "qualifier":null,      "sfa_queue":"Military"},
  {"row":13, "pred_pid":"P748",  "item_type_class":"*",       "edge_type":"APPOINTED_BY",    "direction":"inbound",  "qualifier":null,      "sfa_queue":"Military"},
  {"row":14, "pred_pid":"P1308", "item_type_class":"*",       "edge_type":"HAD_ROLE",        "direction":"outbound", "qualifier":"role",    "sfa_queue":"Military"},
  {"row":15, "pred_pid":"P112",  "item_type_class":"legion",  "edge_type":"RAISED_LEGION",   "direction":"outbound", "qualifier":null,      "sfa_queue":"Military"},
  {"row":16, "pred_pid":"P112",  "item_type_class":"settlement","edge_type":"FOUNDED",       "direction":"outbound", "qualifier":null,      "sfa_queue":"Geographic"},
  {"row":17, "pred_pid":"P112",  "item_type_class":"*",       "edge_type":"FOUNDED",         "direction":"outbound", "qualifier":null,      "sfa_queue":"Political"},
  {"row":18, "pred_pid":"P488",  "item_type_class":"*",       "edge_type":"CHAIRED",         "direction":"outbound", "qualifier":null,      "sfa_queue":"Political"},
  {"row":19, "pred_pid":"P6",    "item_type_class":"*",       "edge_type":"HEADED",          "direction":"outbound", "qualifier":null,      "sfa_queue":"Political"},
  {"row":20, "pred_pid":"P138",  "item_type_class":"settlement","edge_type":"NAMESAKE_OF",   "direction":"outbound", "qualifier":null,      "sfa_queue":"Geographic"},
  {"row":21, "pred_pid":"P138",  "item_type_class":"*",       "edge_type":"NAMESAKE_OF",     "direction":"outbound", "qualifier":null,      "sfa_queue":"Cultural"},
  {"row":22, "pred_pid":"P176",  "item_type_class":"*",       "edge_type":"COMMISSIONED",    "direction":"outbound", "qualifier":null,      "sfa_queue":"Geographic"},
  {"row":23, "pred_pid":"P1344", "item_type_class":"*",       "edge_type":"PARTICIPATED_IN", "direction":"outbound", "qualifier":null,      "sfa_queue":"Social"}
]';


// ============================================================
// 3. SYS_Policy : PlaceResolution
//    Decision table: (place_resolved, sfa_context) → action
// ============================================================

MERGE (pol:SYS_Policy {name: "PlaceResolution"})
SET pol.description  = "Governs what to do when a place QID cannot be resolved to a Pleiades ID. Action varies by SFA context.",
    pol.active       = true,
    pol.version      = 1,
    pol.decision_table = '
[
  {"row":1, "place_resolved":true,  "sfa_context":"*",           "action":"write_resolved",  "notes":"Normal path — MERGE Place {pleiades_id}, resolved:true"},
  {"row":2, "place_resolved":false, "sfa_context":"Biographic",  "action":"write_stub",      "notes":"Birth/death place stubs acceptable for bio; write Place {qid, resolved:false}"},
  {"row":3, "place_resolved":false, "sfa_context":"Geographic",  "action":"flag_review",     "notes":"Geographic SFA requires resolution; set needs_geo_review:true, do not write Place node"},
  {"row":4, "place_resolved":false, "sfa_context":"Military",    "action":"write_stub",      "notes":"Campaign locations often regions; stub acceptable for military SFA"},
  {"row":5, "place_resolved":false, "sfa_context":"*",           "action":"write_stub",      "notes":"Default fallback — write stub, set resolved:false"}
]';


// ============================================================
// 4. SYS_Policy : SnapIdAuthority
//    Decision table: which federation source ID to use as the
//    SNAP:DRGN candidate key, given person temporal period.
//    Condition columns: period (Republic | Imperial | Greek | *)
//    and which IDs are present (boolean).
// ============================================================

MERGE (pol:SYS_Policy {name: "SnapIdAuthority"})
SET pol.description  = "Priority order for deriving snap_id candidate key from available federation source IDs. SNAP:DRGN is the universal crosswalk; this policy selects the most authoritative seed ID by person type and temporal period.",
    pol.active       = true,
    pol.version      = 1,
    pol.decision_table = '
[
  {"row":1, "period":"Republic", "has_dprr":true,                                                  "snap_id_prefix":"dprr",     "notes":"DPRR authoritative for Roman Republic persons"},
  {"row":2, "period":"Republic", "has_dprr":false, "has_lgpn":true,                              "snap_id_prefix":"lgpn",     "notes":"LGPN fallback for Greek-named Republican persons"},
  {"row":3, "period":"Republic", "has_dprr":false, "has_lgpn":false, "has_trismeg":true,          "snap_id_prefix":"trismeg",  "notes":"Trismegistos for inscribed/documented non-elites"},
  {"row":4, "period":"Imperial",                   "has_pir":true,                               "snap_id_prefix":"pir",      "notes":"PIR authoritative for Imperial persons (Augustus-Diocletian). P10382."},
  {"row":5, "period":"Imperial",                   "has_pir":false,  "has_lgpn":true,             "snap_id_prefix":"lgpn",     "notes":"LGPN fallback for Greek-named Imperial persons"},
  {"row":6, "period":"Greek",                      "has_lgpn":true,                              "snap_id_prefix":"lgpn",     "notes":"LGPN authoritative for Greek persons"},
  {"row":7, "period":"*",                          "has_trismeg":true,                           "snap_id_prefix":"trismeg",  "notes":"Trismegistos as universal fallback — widest coverage. P11252."},
  {"row":8, "period":"*",        "has_dprr":false, "has_lgpn":false, "has_trismeg":false, "has_pir":false, "snap_id_prefix":null, "notes":"No candidate key available; snap_id null, flag for manual review"}
]';


// ============================================================
// 5. Register SYS_WikidataProperty in SYS_NodeType
//    (if not already present)
// ============================================================

MERGE (nt:SYS_NodeType {name: "SYS_WikidataProperty"})
ON CREATE SET
  nt.description    = "Registry of Wikidata property IDs harvested by federation agents. Defines fetch_method, canonical_key, and owning SFA for each P-code.",
  nt.layer          = "SYS",
  nt.created_at     = datetime();


// ============================================================
// 6. Verification queries (run after migration)
// ============================================================
// MATCH (p:SYS_WikidataProperty) RETURN p.pid, p.label, p.fetch_method, p.sfa_primary ORDER BY p.pid;
// MATCH (p:SYS_Policy) RETURN p.name, p.active, p.version;
// MATCH (p:SYS_WikidataProperty {fetch_method:"statement_traversal"}) RETURN p.pid, p.label;

