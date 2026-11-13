---
status: requirements
authority: requirements for a future portable export; not an implemented format
depends_on: [02-GRAPH-MODEL.md, 33-DECISIONS.md]
superseded_by: null
last_reviewed: 2026-11-11
---

# Canonical portable export requirements

Neo4j remains the operational source of truth (D-135). A canonical portable
export is a versioned, restorable representation of a declared graph scope,
not the current Actium explorer snapshot. This document states requirements;
it does not define an implemented schema, backup procedure, or importer.

## Required contract

- Declare schema version, export time, exact graph/database identity, scope,
  completeness, software versions, and consistent database snapshot boundary.
  A partial export must say so and must not claim to be a complete backup.
- Preserve stable identifiers, labels, properties, relationship types and
  directions, including typed values, all statuses, qualifiers, provenance,
  proposal decisions, evidence links and source-observation identifiers.
  Preserve distinct evidence and proposal records even when they reference
  the same observation. No duplicate record is independent corroboration.
- Include all entities and references within the declared scope, with explicit
  handling of dependencies outside it. A full export must include accepted,
  proposed, rejected, superseded and other stored states, not just the live
  subset used by the explorer.
- Account for source payloads, private notes, external files and workflow
  state separately from graph records. Record paths or content-addressed
  references and hashes, indicate missing or withheld content, and specify
  whether each is included. Respect rights and privacy: a shareable export
  cannot silently redistribute restricted text. A graph export alone is not a
  complete research archive.
- Define validation, error reporting, collision behavior, atomic import,
  idempotence, migration between versions, and integrity checks before an
  importer is offered. Restore into an isolated database, never implicitly
  overwrite the operational graph.
- Verify export/import round trips against node and relationship identity,
  property types, references, review history and evidence, including
  withheld/missing payloads. Test a real representative graph and restore
  procedure, not only a small fixture.

Open design decisions include the serialization and packaging format, exact
scope and dependency rules, payload inclusion policy, trusted backup versus
shareable export, database consistency mechanism, and compatible import
versions. These require design and approval before implementation.
