// Clear bogus lgpn_id values (D-023)
// P1838 on Wikidata is PSS-archi (building IDs), not LGPN.
// Values like FR-75056-20 are French administrative codes, not LGPN person IDs.
// Run this once after the P1838 mapping fix.
MATCH (e:Entity)
WHERE e.lgpn_id IS NOT NULL
  AND e.lgpn_id =~ '^[A-Z]{2}-\\d+-\\d+$'  // PSS-archi format: FR-75056-20
REMOVE e.lgpn_id
RETURN count(e) AS cleared;
