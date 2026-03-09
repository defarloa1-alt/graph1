// ============================================================
// Script 17c — Set backbone boolean on all Discipline nodes
// ============================================================
// backbone was never written during load. Two rules:
//   backbone = true  if has >= 1 of: lcsh_id, fast_id, lcc, gnd_id, aat_id, ddc
//   backbone = false otherwise (expanded-tier, navigable only)
// ============================================================

// ── 1. Set backbone = true ────────────────────────────────────────────────────
MATCH (d:Discipline)
WHERE d.lcsh_id IS NOT NULL
   OR d.fast_id  IS NOT NULL
   OR d.lcc      IS NOT NULL
   OR d.gnd_id   IS NOT NULL
   OR d.aat_id   IS NOT NULL
   OR d.ddc      IS NOT NULL
SET d.backbone = true
RETURN count(d) AS backbone_true;

// ── 2. Set backbone = false ───────────────────────────────────────────────────
MATCH (d:Discipline)
WHERE d.backbone IS NULL
SET d.backbone = false
RETURN count(d) AS backbone_false;

// ── 3. Verify ─────────────────────────────────────────────────────────────────
MATCH (d:Discipline)
RETURN d.backbone AS backbone, count(d) AS count
ORDER BY count DESC;
