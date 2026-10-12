# Session Handoff — 2026-10-11

**Supersedes:** [17-PHASE-5-HANDOFF.md](17-PHASE-5-HANDOFF.md).
**Branch:** `graph-revised-clean-start` (last commit `d5d40ba`). Nothing pushed.
**Detail of everything below:** [18-PHASE-5-PROPOSALS.md](18-PHASE-5-PROPOSALS.md), sections 1–16.

## 1. Start here

```bash
cd C:/Projects/Graph1
export NEO4J_PASSWORD="$(sed -n 's/^neo4j pw is //p' GraphRevised/Connections.txt | tr -d '\r')"
python -m unittest GraphRevised.tests.test_prompt_version GraphRevised.tests.test_wikidata_identity \
  GraphRevised.tests.test_direct_operations_live GraphRevised.tests.test_proposals_offline \
  GraphRevised.tests.test_proposals_live          # expect 64 tests, OK
python -m GraphRevised.proposals.review list --status submitted
```

- Local Neo4j only: `neo4j://127.0.0.1:7687`, database `neo4j`. Never the legacy Aura instance.
- **Do not load the repo `.env` wholesale**: it holds the legacy Aura `NEO4J_URI`. Code reads only
  `ANTHROPIC_API_KEY` from it (`passage_reader.anthropic_client`).
- `Connections.txt` holds the local password; it is git-ignored. Never print or commit it.
- Live tests run in rolled-back transactions with synthetic fixtures; they never change the graph.

## 2. Verified graph state

4,142 nodes, 4,169 relationships (4,025 Year nodes + 117 others).

| Label | Count | Notes |
|---|---:|---|
| Entity | 24 | 11 Person, 11 Group (local force entities), 1 Event, 1 Place |
| AuthorityRecord | 13 | Wikidata identity links, each with a preserved payload |
| SourceObservation | 18 | 2 Wikidata statements, 16 Plutarch passages |
| Assertion | 19 | 3 accepted, 15 proposed, 1 rejected |
| Proposal | 42 | 11 accepted, 8 rejected, **23 submitted (awaiting review)** |
| Subject | 1 | History of the Battle of Actium |

Accepted claims:

| Claim | Evidence |
|---|---|
| Augustus participated in Battle of Actium | Wikidata P710 · Plutarch 65.2, 65.4, 65.5, 68.1 |
| Agrippa participated in Battle of Actium | Wikidata P710 · Plutarch 65.2, 66.3 |
| Mark Antony participated in Battle of Actium | Plutarch 65.1, 66.5, 67.2 (text-only claim) |

## 3. What exists

| Area | Artifact |
|---|---|
| Graph operations | [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher) — 20 guarded, retry-safe operations; [operations.py](operations.py) loads them by name |
| Draft contract | [proposals/schema.py](proposals/schema.py) — `proposal-draft-v3` (quotations, inquiry, relevance, ambiguities) |
| Predicates | [proposals/predicates.v2.json](proposals/predicates.v2.json) — 13 predicates; `commanded` is Person → Group (a force) |
| Validator | [proposals/validator.py](proposals/validator.py) — deterministic; Wikidata statement evidence must state the claim; passage quotes must be verbatim (whitespace and quote style tolerated only) |
| Storage and review | [proposals/store.py](proposals/store.py), [proposals/review.py](proposals/review.py) — `list`, `accept`, `reject` (evidence only), `reject --claim`, `reopen` |
| Passage reader | [proposals/passage_reader.py](proposals/passage_reader.py) — Claude Sonnet 5.5, inquiry-scoped, prompt `passage-reader-v6-006ea47f` |
| Inquiry | [inquiries/actium-plutarch-antony.json](inquiries/actium-plutarch-antony.json) (v10) — Subject, source, scope, guidance |
| Identity queue | [identity/queue.py](identity/queue.py), queue file [queues/identity-actium-plutarch-antony.json](queues/identity-actium-plutarch-antony.json) |
| Adapters | Wikidata identity, statements, context (aliases/dates); Perseus TEI passages |
| Curation slices | [slices/add_entity.py](slices/add_entity.py), [slices/actium_forces.py](slices/actium_forces.py), [slices/octavian_actium.py](slices/octavian_actium.py) |
| Migration | [migrations/001-pending-evidence-for-open-proposals.cypher](migrations/001-pending-evidence-for-open-proposals.cypher) (applied) |
| Preserved sources | `phase-2-source/`, `phase-4-source/`, `phase-5-source/` — hashed byte-for-byte; `.gitattributes` keeps them `-text` |
| Run traces | [runs/](runs) — one JSONL per reader run, with inquiry, scope, prompt version, model |

## 4. Rules that are easy to break

1. Agents propose; only a curator accepts. The reader never creates Entities; identity is a curator decision via the queue.
2. Every Proposal holds evidence on `PROPOSES_EVIDENCE` until acceptance. `reject` rejects evidence and leaves the claim open; `reject --claim` rejects the claim; `reopen` restores a rejected claim.
3. A guarded write returning zero rows was refused; `run_write` raises `RefusedWrite`.
4. Editorial notes in editions (for example Perrin's dates) are never cited as the ancient source.
5. Preserved payloads are hashed as bytes. Write files with `write_bytes`, never text mode on Windows.
6. Reusable code (`proposals/`, `identity/`, `adapters/`) must not name a source or subject; a test enforces it. Subject knowledge belongs in the inquiry.
7. Tests must not depend on live graph contents; use synthetic fixtures in the rolled-back transaction.
8. Shell note: long `python - <<'EOF'` heredocs containing triple-quoted strings have failed in this environment; write edit scripts to the scratchpad and run them instead.

## 5. Open decisions (for the curator)

1. **23 submitted proposals** (Actium v6 run). Recommendation recorded in the session: accept 22; reject the Cleopatra 66.3 *evidence* (`…7059319b3457`) with plain `reject` so her claim stays open.
2. **Cleopatra 67.1**: whether to submit a curator-authored claim citing "Cleopatra recognized him and raised a signal on her ship".
3. **Unresolved commanders** with no Wikidata record: Coelius (Antony's left wing), Marcus Octavius (Antony's centre), Alexas. Option: local entities, like the forces.
4. **33 peripheral mentions** in the identity queue (allies, places); deferred because most would need dated `alliedWith` claims.

## 6. Next steps (agreed order)

1. Finish the review above.
2. **Fair evaluation**: run the reader unchanged on chapters it has not seen; measure curator acceptance. Prompts v3–v6 were tuned on *Antony* 61–68.
3. **Phase 7 temporal qualification**: unblocks marriages, offices, and source dating.
4. **Second source** (for E10): add `source.type` and an adapter interface; move the context window and scope rule into the inquiry; turn slice scripts into data.
5. **Roadmap agreed in principle:** [docs/Response - Use Cases.md](docs/Response%20-%20Use%20Cases.md)
   (Chrystallum is for exploring and discovering connections, not an
   encyclopedia; phases A–F, with gates before multi-agent fan-out).
   **Proposed first task for the next session:** a design doc for E12
   (attributed claims and depicted events: "according to Plutarch"), then the
   micro-event pilot on *Antony* 65–68. Principle agreed with the curator:
   narrative detail is the author's depiction, not fact.
6. Backlog in [04-IMPLEMENTATION-PLAN.md](04-IMPLEMENTATION-PLAN.md): E8 evidence stance and contested claims; E9 research-API acquisition; **E10 source discovery and chronology** (earlier witnesses to Actium: Augustan poets, Velleius Paterculus, Augustus's lost memoir cited at *Antony* 68.1); **E11 actor actions (IGAR) and causal context**; **E12 attributed claims and depicted events**; **E13 geography and space-time exploration**; **E14 entity images** (with Phase B); **E15 graph change governance** (impact-routed review; pairs with the Phase C review policy).

## 7. Known gaps

- The reader reads only Perseus TEI by chapter.section; context window and scope rule are fixed in code.
- Entity context is Wikidata-only and English-only.
- Force hierarchy (a wing is part of a fleet) has no predicate yet; labels carry it.
- Neo4j Bloom is for smoke testing only (status colouring via rule-based styling on `status`). The product UI is a custom React + Cytoscape.js explorer designed in Figma: [20-EXPLORER-UI.md](20-EXPLORER-UI.md).
