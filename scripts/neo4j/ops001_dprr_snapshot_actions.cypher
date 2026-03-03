// OPS-001: DPRR Snapshot — SYS_FederationSource status update
// Run after StatusType resolution (OI-01). Matches by name or source_id.
// See Person/chrystallum_ops001_dprr_snapshot.docx

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
    n.snapshot_posts = 6934,
    n.snapshot_relationships = 4682,
    n.snapshot_status_assertions = 1919,
    n.update_path = 'contact_kdl_for_dump',
    n.update_path_alt = 'wikidata_p6863_proxy',
    n.update_path_url = 'https://github.com/kingsdigitallab/dprr-django',
    n.kdl_contact = "King's Digital Lab, King's College London",
    n.notes = 'Full snapshot in graph as of 2026-02-25. Endpoint blocked by Anubis. Browser interface at romanrepublic.ac.uk may still be accessible. Request Turtle/N-Triples dump from KDL for future updates.'
