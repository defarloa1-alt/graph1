// OPS-001: Immediate actions before harvest agent runs
// 1. SYS_FederationSource DPRR status update
// 2. StatusType relabelling (1->eques, 2->senator)

// --- 1. SYS_FederationSource ---
MATCH (n:SYS_FederationSource)
WHERE n.name = 'DPRR' OR n.source_id = 'dprr'
SET n.source_id = 'dprr',
    n.status = 'blocked',
    n.block_reason = 'Anubis bot protection on SPARQL endpoint',
    n.block_type = 'bot_challenge',
    n.blocked_since = '2026-03-01',
    n.last_successful_access = '2026-02-25',
    n.snapshot_date = '2026-02-25',
    n.snapshot_complete = true,
    n.snapshot_persons = 4772,
    n.snapshot_posts = 7342,
    n.snapshot_relationships = 4682,
    n.snapshot_status_assertions = 1919,
    n.update_path = 'contact_kdl_for_dump',
    n.update_path_alt = 'wikidata_p6863_proxy',
    n.update_path_url = 'https://github.com/kingsdigitallab/dprr-django',
    n.kdl_contact = "King's Digital Lab, King's College London",
    n.notes = 'Full snapshot in graph as of 2026-02-25. Endpoint blocked by Anubis. Browser interface at romanrepublic.ac.uk may still be accessible. Request Turtle/N-Triples dump from KDL for future updates.';

// --- 2. StatusType relabelling ---
MATCH (n:StatusType {label: "1"})
SET n.label = "eques", n.label_latin = "eques", n.dprr_status_id = 1,
    n.description = "Equestrian order — DPRR Status authority list";

MATCH (n:StatusType {label: "2"})
SET n.label = "senator", n.label_latin = "senator", n.dprr_status_id = 2,
    n.description = "Senatorial order — includes ex-officio per DPRR office-holding rules";
