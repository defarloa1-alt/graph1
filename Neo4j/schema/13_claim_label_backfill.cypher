// ============================================================================
// CHRYSTALLUM NEO4J: CLAIM LABEL BACKFILL
// ============================================================================
// File: 13_claim_label_backfill.cypher
// Purpose: Populate Claim.label for existing claims before enabling NOT NULL
//          constraint on Claim.label.
// ============================================================================

MATCH (c:Claim)
WHERE c.label IS NULL OR trim(toString(c.label)) = ''
SET c.label = CASE
  WHEN c.text IS NOT NULL AND trim(toString(c.text)) <> '' THEN
    CASE
      WHEN size(toString(c.text)) > 80 THEN substring(toString(c.text), 0, 80) + '...'
      ELSE toString(c.text)
    END
  ELSE c.claim_id
END;

