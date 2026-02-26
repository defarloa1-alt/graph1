# Pipeline Read-Back Principle

## Problem

Every step in the pipeline — harvester, migration, cluster assignment, SCA scoring — is **write-only**. Data flows in, nothing reads back what's already there to inform what comes next.

For a linear single-run pipeline that's fine. But with multiple harvest runs, a second domain, or incremental cluster assignment, the pipeline must ask **"what's already here?"** before deciding what to do.

## Principle

**Every agent that writes to Neo4j should also read from it before writing.**

The graph is the source of truth, not the JSON files. JSON files are pipeline artifacts. Once something is in Neo4j it should be the authoritative version, and subsequent steps should treat it that way.

## Concrete Gaps (SCA)

1. **Entity density** — SCA needs `entity_count` per SubjectConcept. It was computed from `member_of_edges.json` each time. Now it reads from Neo4j when available.

2. **Cross-run consistency** — If the harvester runs again and gets different entities, nothing compares the new harvest against what's already in the graph. Read-back enables that comparison.

3. **Unconfirmed SubjectConcepts** — A node with 200 MEMBER_OF edges in Neo4j is de facto confirmed, even if `harvest_status` says unconfirmed. Read-back surfaces that.

## Implementation

### SCA Salience (`sca_salience_doors.py`)

Before scoring, the SCA:

1. Connects to Neo4j (when `NEO4J_URI`, `NEO4J_PASSWORD` set)
2. Runs a single query:
   ```cypher
   MATCH (sc:SubjectConcept)
   OPTIONAL MATCH (e:Entity)-[:MEMBER_OF]->(sc)
   WITH sc, count(e) AS entity_count
   RETURN sc.qid, sc.harvest_status, entity_count
   ```
3. Uses `entity_count` and treats `entity_count > 0` as de facto confirmed
4. Falls back to JSON (`member_of_edges.json`, `harvest_progress.json`) when Neo4j unavailable

Use `--no-neo4j` to force JSON-only (e.g. testing without Neo4j).

### Future: Other Steps

- **Cluster assignment** — Before writing, read existing MEMBER_OF counts to support incremental merge vs full replace
- **Harvester** — Compare new harvest against existing entity set for delta reporting
- **SFA** — Must read current entity counts and confidence states before generating narrative

## Why It Matters for SFA

An SFA that generates a narrative about the Roman Republic without first reading current entity counts and confidence states from Neo4j is reasoning over stale data. The read-back isn't optional at that point, it's the whole mechanism.
