# Session Handoff — 2026-10-11

**Supersedes:** [17-PHASE-5-HANDOFF.md](17-PHASE-5-HANDOFF.md).
**Branch:** `graph-revised-clean-start`, public on GitHub (`origin`) up to `c19aceb`; later commits are local until pushed (`git status -sb` shows how many).
**Updated 2026-10-12:** command split part 1 done (section 5a).
**Detail of everything below:** [18-PHASE-5-PROPOSALS.md](18-PHASE-5-PROPOSALS.md), sections 1–16.

## 1. Start here

```bash
cd C:/Projects/Graph1
export NEO4J_PASSWORD="$(sed -n 's/^neo4j pw is //p' GraphRevised/Connections.txt | tr -d '\r')"
python -m unittest GraphRevised.tests.test_prompt_version GraphRevised.tests.test_wikidata_identity GraphRevised.tests.test_temporal \
  GraphRevised.tests.test_direct_operations_live GraphRevised.tests.test_proposals_offline \
  GraphRevised.tests.test_proposals_live          # expect 106 tests, OK
python -m GraphRevised.proposals.review list --status submitted
```

- Local Neo4j only: `neo4j://127.0.0.1:7687`, database `neo4j`. Never the legacy Aura instance.
- **Do not load the repo `.env` wholesale**: it holds the legacy Aura `NEO4J_URI`. Code reads only
  `ANTHROPIC_API_KEY` from it (`passage_reader.anthropic_client`).
- `Connections.txt` holds the local password; it is git-ignored. Never print or commit it.
- Live tests run in rolled-back transactions with synthetic fixtures; they never change the graph.

## 2. Verified graph state

4,142 nodes, 4,178 relationships (4,025 Year nodes + 117 others), after the 2026-10-12 review.

| Label | Count | Notes |
|---|---:|---|
| Entity | 24 | 11 Person, 11 Group (local force entities), 1 Event, 1 Place |
| AuthorityRecord | 13 | Wikidata identity links, each with a preserved payload |
| SourceObservation | 18 | 2 Wikidata statements, 16 Plutarch passages |
| Assertion | 19 | 10 accepted, 8 proposed, 1 rejected |
| Proposal | 42 | 20 accepted, 9 rejected, **13 submitted (all `commanded`)** |
| Subject | 1 | History of the Battle of Actium |

Accepted claims:

| Claim | Evidence |
|---|---|
| Augustus participated in Battle of Actium | Wikidata P710 · Plutarch 65.2, 65.4, 65.5, 68.1 |
| Agrippa participated in Battle of Actium | Wikidata P710 · Plutarch 65.2, 66.3 |
| Mark Antony participated in Battle of Actium | Plutarch 65.1, 66.5, 67.2 (text-only claim) |
| Lucius Gellius Poplicola participated in Battle of Actium | Plutarch 65.1, 66.3 |
| Marcus Insteius participated in Battle of Actium | Plutarch 65.1 |
| Lucius Arruntius participated in Battle of Actium | Plutarch 66.3 |
| Gaius Julius Eurycles participated in Battle of Actium | Plutarch 67.2 (the pursuit of Antony's flight) |
| Antony's fleet at Actium participated in Battle of Actium | Plutarch 66.1, 68.1 |
| Octavian's fleet at Actium participated in Battle of Actium | Plutarch 66.1 |
| Battle of Actium occurred at Actium promontory | Plutarch 68.1 |

Still proposed: Cleopatra participatedIn (evidence 66.3 rejected as
`unsupported`; claim open) and the seven `commanded` claims (13 Proposals).
The seven claims added on 2026-10-12 rest on Plutarch alone and were decided
by "Claude (delegated by Tony DeFarlo)". The promontory Entity was relabelled
from Wikidata's "Akri" to "Actium promontory" (curator decision); its
AuthorityRecord keeps Wikidata's wording.

## 3. What exists

| Area | Artifact |
|---|---|
| Graph operations | [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher) — 27 guarded, retry-safe operations; [operations.py](operations.py) loads them by name |
| Draft contract | [proposals/schema.py](proposals/schema.py) — `proposal-draft-v4` (quotations, inquiry, relevance, ambiguities; mode, context, role, time, qualifier quotations) |
| Predicates | [proposals/predicates.v4.json](proposals/predicates.v4.json) — 16 predicates, each declaring its qualifiers and modes; `heldAuthorityOver` (needs a time) and `commanded` (needs a time when it has a role), both Person → Group; unary `occurred`; `authorOf` |
| Time | [proposals/temporal.py](proposals/temporal.py) — year conversion (no year zero ↔ astronomical), EDTF to Julian Day Number bounds |
| Validator | [proposals/validator.py](proposals/validator.py) — deterministic; Wikidata statement evidence must state the claim; passage quotes must be verbatim (whitespace and quote style tolerated only) |
| Storage and review | [proposals/store.py](proposals/store.py), [proposals/review.py](proposals/review.py) — `list`, `accept`, `reject --reason` (evidence only), `reject --claim`, `reopen`, `supersede --replacement --reason`, `retract --reason`, `promote` |
| Passage reader | [proposals/passage_reader.py](proposals/passage_reader.py) — Claude Sonnet 5.5, inquiry-scoped, prompt `passage-reader-v7` (predicate definitions in the task packet) |
| Inquiry | [inquiries/actium-plutarch-antony.json](inquiries/actium-plutarch-antony.json) (v10) — Subject, source, scope, guidance |
| Identity queue | [identity/queue.py](identity/queue.py), queue file [queues/identity-actium-plutarch-antony.json](queues/identity-actium-plutarch-antony.json) |
| Adapters | Wikidata identity, statements, context (aliases/dates); Perseus TEI passages |
| Curation slices | [slices/add_entity.py](slices/add_entity.py), [slices/actium_forces.py](slices/actium_forces.py), [slices/octavian_actium.py](slices/octavian_actium.py) |
| Migration | [migrations/001-pending-evidence-for-open-proposals.cypher](migrations/001-pending-evidence-for-open-proposals.cypher) (applied) |
| Preserved sources | `phase-2-source/`, `phase-4-source/`, `phase-5-source/` — hashed byte-for-byte; `.gitattributes` keeps them `-text` |
| Run traces | [runs/](runs) — one JSONL per reader run, with inquiry, scope, prompt version, model |

## 4. Rules that are easy to break

1. Agents propose; only a curator accepts. The reader never creates Entities; identity is a curator decision via the queue.
2. Every Proposal holds evidence on `PROPOSES_EVIDENCE` until acceptance. `reject` rejects evidence and leaves the claim open; `reject --claim` rejects the claim; `reopen` restores a rejected claim; `supersede` replaces a proposed or accepted claim; `retract` rejects an accepted claim found wrong. Rejections, supersessions, and retractions need a reason code.
3. A guarded write returning zero rows was refused; `run_write` raises `RefusedWrite`.
4. Editorial notes in editions (for example Perrin's dates) are never cited as the ancient source.
5. Preserved payloads are hashed as bytes. Write files with `write_bytes`, never text mode on Windows.
6. Reusable code (`proposals/`, `identity/`, `adapters/`) must not name a source or subject; a test enforces it. Subject knowledge belongs in the inquiry.
7. Tests must not depend on live graph contents; use synthetic fixtures in the rolled-back transaction.
8. Shell note: long `python - <<'EOF'` heredocs containing triple-quoted strings have failed in this environment; write edit scripts to the scratchpad and run them instead.
9. Delegated review follows [21-REVIEW-DELEGATION.md](21-REVIEW-DELEGATION.md): Claude may accept only claims a verbatim quote plainly shows, records itself as `Claude (delegated by …)`, and leaves identity, predicates, roles, command, and uncertain cases to the curator.

## 5. Open decisions (for the curator)

1. **13 submitted `commanded` proposals** (7 claims) stay open (5a, design-mode policy); review them against the v3 definition when convenient. The 10 non-command proposals were decided on 2026-10-12 (the earlier count of 14 non-command and 9 command was wrong). *Mark Antony commanded Antony's fleet* (the whole fleet) is the borderline case between authority held and command exercised.
2. **Cleopatra 67.1**: whether to submit a curator-authored claim citing "Cleopatra recognized him and raised a signal on her ship".
3. **Unresolved commanders** with no Wikidata record: Coelius (Antony's left wing), Marcus Octavius (Antony's centre), Alexas. Option: local entities, like the forces.
4. **33 peripheral mentions** in the identity queue (allies, places); deferred because most would need dated `alliedWith` claims.

## 5a. Decision: split command (first task of the next session)

Agreed with the curator on 2026-10-12. `commanded` conflates authority held
with command exercised. At Actium this hides the central question: Octavian
held supreme authority, while much of the tradition credits Agrippa with
directing the fleet.

- **Registry v3:** `heldAuthorityOver` (Person → Group, formal or supreme
  authority) and `commanded` (Person → Group, command actually exercised).
  Evidence for one never counts for the other.
- **Claim qualifiers:** an event context (`ASSERTION_CONTEXT` → Event) and a
  **role** (`ASSERTION_ROLE` → the Entity for the office or post, in the
  source's own term), not modern strategic/operational/tactical labels. Role
  replaced the earlier `capacity` on 2026-10-12; legal basis (*imperium*) is
  not a role. Rules in
  [docs/Response - Roman Republican Army Structure.md](docs/Response%20-%20Roman%20Republican%20Army%20Structure.md).
  The same qualifier mechanism serves Phase 7 time and E12 depiction.
- **Planning is an action** (E11), not a command predicate.
- **Reason codes** for rejection and supersession: false, unsupported,
  malformed, underspecified, superseded-by-model.
- **Supersede with links:** a recorded supersede operation with
  `SUPERSEDED_BY` edges to the precise claims that replace a coarser one.
- **Design-mode policy (curator, 2026-10-12):** while the model is still being
  designed, claims are not rejected or superseded merely because a predicate
  was redesigned. The open `commanded` proposals stay open, and the already
  rejected *Augustus commanded Battle of Actium* stays rejected (its basis
  records why). Then rerun the reader for command claims with guidance
  separating the two senses.

**Progress (2026-10-12).** Done: registry v3, reason codes, and the supersede
operation ([18 §17](18-PHASE-5-PROPOSALS.md)). Curator decisions: supersession
is allowed from `proposed` (and `accepted`); claims tied to an event get no
exemption from the date-span requirement, so `heldAuthorityOver` drafts are
deferred until Phase 7. Capacity became role (above). Next: implement the
event-context and role qualifiers. Open: whether a role-qualified claim needs
a date span.

## 6. Next steps (agreed order)

1. **Finish the command split** (5a): registry v3, reason codes, supersede,
   and the qualifier mechanism ([22](22-CLAIM-QUALIFIERS.md): context, role,
   time, mode, promotion) and the Plutarch / *Life of Antony* entities
   (Q41523, Q12902608; passages linked `IN_WORK`) are done. Remaining: the
   curator's decision on *Plutarch author of Life of Antony* (submitted from
   Wikidata P50), reader prompt v8
   (attributed and unary claims), source discovery, a second-source adapter,
   then the reader rerun.
2. **Finish the review** (5, item 1): the non-command proposals are done;
   the command proposals whenever convenient.
3. **E12 design doc** (attributed claims and depicted events: "according to
   Plutarch"), then the micro-event pilot on *Antony* 65–68 (Phase A).
   Principle agreed with the curator: narrative detail is the author's
   depiction, not fact.
4. **Fair evaluation**: run the reader unchanged on chapters it has not seen;
   measure curator acceptance. Prompts v3–v6 were tuned on *Antony* 61–68.
5. **Phase 7 temporal qualification**: unblocks marriages, offices, and
   source dating.
6. **Second source** (for E10): add `source.type` and an adapter interface;
   move the context window and scope rule into the inquiry; turn slice scripts
   into data.

**Roadmap:** [docs/Response - Use Cases.md](docs/Response%20-%20Use%20Cases.md)
(Chrystallum is for exploring and discovering connections, not an
encyclopedia; phases A–F, with gates before multi-agent fan-out). Product UI:
[20-EXPLORER-UI.md](20-EXPLORER-UI.md).

**Backlog** in [04-IMPLEMENTATION-PLAN.md](04-IMPLEMENTATION-PLAN.md): E8
evidence stance and contested claims; E9 research-API acquisition; E10 source
discovery and chronology (earlier witnesses to Actium: Augustan poets,
Velleius Paterculus, Augustus's lost memoir cited at *Antony* 68.1); E11 actor
actions (IGAR) and causal context; E12 attributed claims and depicted events;
E13 geography and space-time exploration; E14 entity images (with Phase B);
E15 graph change governance (impact-routed review, pairs with the Phase C
review policy); E16 frontier expansion (leaf nodes to clusters).

## 7. Known gaps

- The reader reads only Perseus TEI by chapter.section; context window and scope rule are fixed in code.
- Entity context is Wikidata-only and English-only.
- Force hierarchy (a wing is part of a fleet) has no predicate yet; labels carry it. Backlog: a Group → Group predicate (`SUBUNIT_OF` in the army-structure response).
- Neo4j Bloom is for smoke testing only (status colouring via rule-based styling on `status`). The product UI is a custom React + Cytoscape.js explorer designed in Figma: [20-EXPLORER-UI.md](20-EXPLORER-UI.md).
