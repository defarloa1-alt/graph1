# SCA Agent — Claude Session Instructions

**Subject Concept Alignment (SCA)** is a Claude agent session that builds the skeleton structure of a subject domain (e.g. Roman Republic) and persists it to the graph. New sessions ground themselves by reading from the graph via MCP.

## Prerequisites

- **Claude** with MCP connected to Chrystallum (Cursor or Claude Desktop)
- **Neo4j** running with Chrystallum schema
- **ANTHROPIC_API_KEY** for any LLM calls from scripts

## Flow

1. **Ground** — Call `get_domain_structure` with the subject QID. If structure exists, you have the full domain context (types, training QIDs, structural props). If not, you start fresh.

2. **Traverse** — Run `sca_traversal_engine.py` to discover P31/P279 types, backlinks, categorization by instance-of. Recurses until metalevel.

3. **Persist** — Run `sca_persist.py` to write findings to Neo4j (WikidataType, SubjectDomain, edges).

4. **Propose** — Use the graph context + traversal output to propose edges to backbones (LCC, LCSH, facets, bibliography). LLM can suggest; validate against graph before persisting.

5. **Extend** — Add P527 (has part), P361 (part of), P131, P17 from the seed. These are already in the traversal output.

## MCP Tools (use these to stay grounded)

| Tool | Purpose |
|------|---------|
| `get_domain_structure` | Get SubjectDomain + WikidataTypes for a QID. **Call first** to ground. |
| `get_subject_concepts` | List all SubjectConcepts (qid, label, facets) |
| `run_cypher_readonly` | MATCH queries to inspect graph state |
| `get_federation_sources` | SYS_FederationSource nodes |

## Scripts (run from project root)

```bash
# 1. Traverse (fetches from Wikidata)
python scripts/sca/sca_traversal_engine.py --qid Q17167 --max-depth 3 -o output/sca/Q17167_domain.json

# 2. Persist (writes to Neo4j)
python scripts/sca/sca_persist.py -i output/sca/Q17167_domain.json
```

## Session Rules

- **Always ground first** — Before reasoning, call `get_domain_structure(qid)` to see what exists.
- **Refer to graph** — Propose edges that reference real nodes (LCC_Class, SubjectConcept, etc.). Validate with `run_cypher_readonly`.
- **Don't drift** — If the graph says X, don't propose Y that contradicts it. Stay anchored.
- **Persist findings** — After traversal, run `sca_persist.py` so the next session can ground.

## Output

- **SubjectDomain** — One per subject. Holds types_count, backlinks_total, training_qids, structural_props.
- **WikidataType** — Ontology lookup nodes. qid, label, tier, depth, backlink_count.
- **Training QIDs** — Curated set for SFAs. Collected during traversal.

## Order of Work

SCA runs **before** SFA work. The skeleton and training QIDs feed the SFAs (Biographical, Political, Geographic, etc.).
