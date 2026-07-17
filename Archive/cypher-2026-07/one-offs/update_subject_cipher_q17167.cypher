// Update subject (Q17167 Roman Republic) with content-addressable entity_cipher
//
// The cipher is computed by: scripts/sca/compute_subject_cipher_q17167.py
// Format: Q17167|P31:val1,val2|P36:val|... (readable, IDs the subgraph; SFA updates it)
//
// Run the Python script first to get the cipher value, then set :param cipher

MATCH (e:Entity {qid: 'Q17167'})
SET e.entity_cipher = $cipher,
    e.subject_cipher_computed_at = datetime()
RETURN e.qid AS qid, e.entity_cipher AS entity_cipher;
