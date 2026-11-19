// Migration 022 (2026-11-19): a description that is only a web address is no description (fix 5b, D-162).
// Two AuthorityRecords from the Phase 5 subject import, the LCSH and FAST headings for the Battle of
// Actium, carry their own URI as `description`. The address is already kept in `sourceUri`
// (and the payload in `rawPayloadUri`), so nothing is lost. Today's importers set no description
// on an authority record, and the projection never shows one that is only a link. Idempotent.
MATCH (n)
WHERE (n:AuthorityRecord OR n:Entity OR n:Subject)
  AND n.description =~ '\\s*https?://\\S+\\s*'
REMOVE n.description
RETURN labels(n) AS labels, n.id AS id, n.sourceUri AS keptAt;
