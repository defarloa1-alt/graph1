// ============================================================
// Script 19a — Clean up duplicate MILITARY training runs
// ============================================================
// Problem:
//   train.py was run 3x for MILITARY on 2026-03-07, creating:
//     - 3 SFA_TrainingRun nodes (different run_ids)
//     - 13 SFA_TrainingInsight nodes (accumulated, not deduped)
//     - 48 CorpusWork nodes (facet_key=null bug, now fixed in train.py)
//   The corpus content was also low-quality (generic anthropology works,
//   not Roman Republic military history).
//
// Fix: delete all MILITARY training data. Re-run train.py fresh.
// ============================================================

// ── 1. Count before delete (verify scope) ────────────────────────────────────
MATCH (tr:SFA_TrainingRun {facet_key: 'MILITARY'})
OPTIONAL MATCH (tr)-[:PRODUCED]->(ti:SFA_TrainingInsight)
OPTIONAL MATCH (tr)-[:CONSULTED]->(cw:CorpusWork)
RETURN count(DISTINCT tr) AS training_runs,
       count(DISTINCT ti) AS insights,
       count(DISTINCT cw) AS corpus_works;

// ── 2. Detach and delete SFA_TrainingInsight nodes ────────────────────────────
MATCH (tr:SFA_TrainingRun {facet_key: 'MILITARY'})-[:PRODUCED]->(ti:SFA_TrainingInsight)
DETACH DELETE ti;

// ── 3. Detach and delete CorpusWork nodes consulted only by MILITARY runs ─────
// Guard: only delete CorpusWork nodes that are EXCLUSIVELY connected to
// MILITARY training runs (not shared with other facets).
MATCH (cw:CorpusWork)
WHERE NOT exists {
    MATCH (tr2:SFA_TrainingRun)-[:CONSULTED]->(cw)
    WHERE tr2.facet_key <> 'MILITARY'
}
DETACH DELETE cw;

// ── 4. Detach and delete SFA_TrainingRun nodes ────────────────────────────────
MATCH (tr:SFA_TrainingRun {facet_key: 'MILITARY'})
DETACH DELETE tr;

// ── 5. Verify clean ──────────────────────────────────────────────────────────
MATCH (tr:SFA_TrainingRun)
RETURN tr.facet_key AS facet, count(tr) AS runs
ORDER BY tr.facet_key;

MATCH (cw:CorpusWork)
RETURN count(cw) AS corpus_works_remaining;
