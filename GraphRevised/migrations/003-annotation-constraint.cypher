// Migration 003 (2026-10-12): Annotation, the eighth core label (23-NARRATIVE-AND-NOTES.md).
// Annotations are commentary, not claims: passages of note (agent or curator)
// and curator notes. Their local ID is unique. Idempotent.
CREATE CONSTRAINT annotation_id_unique IF NOT EXISTS
FOR (node:Annotation)
REQUIRE node.id IS UNIQUE;
