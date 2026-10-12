// Migration 002 (2026-10-12): every Assertion records its claim category.
//
// Registry v5 gives each predicate a category, factual or interpretive, and
// new Assertions record it when created. Every Assertion stored before v5
// uses a factual predicate (participatedIn, commanded, heldAuthorityOver,
// occurredAt, occurred, authorOf). Idempotent: only Assertions without a
// category are touched.
MATCH (assertion:Assertion)
WHERE assertion.category IS NULL
  AND assertion.predicate IN ["participatedIn", "commanded", "heldAuthorityOver", "occurredAt", "occurred",
                              "authorOf", "partOf", "bornAt", "diedAt", "childOf", "spouseOf", "siblingOf",
                              "heldPosition", "describedBy", "distinctFrom", "alliedWith"]
SET assertion.category = "factual"
RETURN count(assertion) AS categorized;
