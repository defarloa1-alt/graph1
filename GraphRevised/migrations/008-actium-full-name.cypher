// Migration 008 (2026-10-19): the Battle of Actium loses its short caption (D-115).
// Its shortLabel "Actium" read as the place (the graph has "Actium promontory")
// and hid that a second, 435 BC "Battle of Actium" is in the graph too. Without
// a shortLabel every view shows its label, "Battle of Actium" (curator, 2026-10-19).
// Idempotent.
MATCH (e:Entity {id: 'chr:entity:battle-of-actium'})
REMOVE e.shortLabel
RETURN e.id AS id, e.label AS label, e.shortLabel AS shortLabel;
