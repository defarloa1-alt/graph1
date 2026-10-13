# Session Handoff — 2026-10-13 (evening)

**Branch:** `graph-revised-clean-start`, pushed to `origin` (2026-10-13, with the curator's go-ahead; push only with it).
**Read first:** [25-LIVES-AND-PLAYGROUND.md](25-LIVES-AND-PLAYGROUND.md), sections 5-13 especially. They record this session's decisions in order.
**Also new:** [26-UI-DATA-CONTRACT.md](26-UI-DATA-CONTRACT.md) (what the Figma explorer receives), [docs/Response - Roman Republican Institutions and Military Hierarchies.md](docs/Response%20-%20Roman%20Republican%20Institutions%20and%20Military%20Hierarchies.md) (the structure design).
**History:** [18](18-PHASE-5-PROPOSALS.md) (Phase 5), [22](22-CLAIM-QUALIFIERS.md), [23](23-NARRATIVE-AND-NOTES.md), [24](24-PERIODS-AND-TRANSFORMATION.md).

## 1. Start here

```bash
cd C:/Projects/Graph1
export NEO4J_PASSWORD="$(sed -n 's/^neo4j pw is //p' GraphRevised/Connections.txt | tr -d '\r')"
python -m unittest GraphRevised.tests.test_prompt_version GraphRevised.tests.test_wikidata_identity GraphRevised.tests.test_temporal \
  GraphRevised.tests.test_direct_operations_live GraphRevised.tests.test_proposals_offline \
  GraphRevised.tests.test_proposals_live GraphRevised.tests.test_passage_reader_offline \
  GraphRevised.tests.test_source_plan GraphRevised.tests.test_lacuscurtius \
  GraphRevised.tests.test_curation_live GraphRevised.tests.test_inquiries GraphRevised.tests.test_capture \
  GraphRevised.tests.test_gutenberg GraphRevised.tests.test_related_and_candidates \
  GraphRevised.tests.test_proposed_entities GraphRevised.tests.test_period_survey \
  GraphRevised.tests.test_cytoscape_export GraphRevised.tests.test_registry_v7 \
  GraphRevised.tests.test_library_headings GraphRevised.tests.test_wikidata_harvest  # expect 204 tests, OK
python -m GraphRevised.export.cytoscape            # then open GraphRevised/exports/graph.html
python -m GraphRevised.harvest.apply Q51673 --expand   # dry run: what the next expansion would do
```

- Local Neo4j only: `neo4j://127.0.0.1:7687`, database `neo4j`. Never the legacy Aura instance; never run legacy scripts against the local database.
- **Do not load the repo `.env` wholesale**: it holds the legacy Aura `NEO4J_URI`. Code reads only `ANTHROPIC_API_KEY` from it.
- `Connections.txt` holds the local password; it is git-ignored. Never print or commit it.
- Live tests run in rolled-back transactions with synthetic fixtures; they never change the graph.
- `.obsidian/` and the curator's Obsidian edits to the `.md` files are theirs (`00`, `01`, `README` have uncommitted edits of theirs): never touch the folder, and stage only your own hunks.
- **Data is not in git** (25 §13): harvest payloads are git-ignored; the local disk holds the only copy of the graph and payloads.

## 2. Graph state (2026-10-13, after the second Antony expansion)

6,258 nodes, 8,095 relationships (4,025 Year nodes from 2000 BCE to 2025).

| Label | Count | Notes |
|---|---:|---|
| Entity | 195 | 92 Person, 44 Work, 17 Group, 15 Office, 13 Place, 9 Event, 3 Concept, 2 Period; mostly proposed (the harvests) |
| Assertion | 447 | 10 accepted, 436 proposed, 1 rejected; every dated one tethered to Years |
| Proposal | 596 | |
| SourceObservation | 607 | passages (Plutarch, Dio, Weigall, Hale), PeriodO records, Wikidata statements (with their time and qualifiers recorded) |
| AuthorityRecord | 259 | Wikidata identities, the crosswalk (role `crosswalk`: DPRR, Nomisma, Trismegistos, LC, FAST, GND, VIAF), LCSH and FAST on the Subject |
| Annotation | 128 | passages of note and entity mentions |
| Subject | 1 | History of the Battle of Actium, with LCSH sh85000736 and FAST 796265 |

## 3. What exists

| Area | Artifact |
|---|---|
| Graph operations | [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher), loaded by name through [operations.py](operations.py); new today: `set_work_form`, `upsert_subject_authority`, `record_statement_time`; `link_assertion_years` takes `{year, as}` links |
| Draft contract | [proposals/schema.py](proposals/schema.py), `proposal-draft-v5`: `TimeQualifier.mode` (during, within) |
| Predicates | [proposals/predicates.v8.json](proposals/predicates.v8.json), 26 predicates: v7 `opposed` (symmetric, time required, no Wikidata mapping) and Work forms; v8 `born` and `died` (dated unary claims), P1344 to `participatedIn` |
| Validator and store | [proposals/validator.py](proposals/validator.py): derives `imaginative` from the attributed Work's form; refuses fiction as evidence for an asserted claim; compares a Wikidata statement's recorded time with the claim's (refuses a mismatch; Wikidata's "unknown value" leaves the claim undated). [proposals/store.py](proposals/store.py) |
| Time | [proposals/temporal.py](proposals/temporal.py), the only year converter: `wikidata_time` (precision day to century; BCE decades and centuries counted down), `year_links` (during, earliest/latest for a window, start/end for spans over 200 years; outside the backbone named in a note) |
| Harvest (L3, increments 1-3) | [harvest/wikidata_harvest.py](harvest/wikidata_harvest.py) `<QID>`: a report, no writes. [harvest/apply.py](harvest/apply.py) `<QID> [--expand] [--limit 50] [--apply]`, dry run by default: one-hop targets become proposed Entities by kind (the P31 table in [harvest/wikidata_rules.v1.json](harvest/wikidata_rules.v1.json), one level of superclasses, disambiguation pages dropped, unknown kinds wait for the agent); mapped and dated statements become proposed claims "according to Wikidata"; federation identifiers become crosswalk records; `--expand` harvests the surfaced people, events, and places within a budget of new entities |
| Library headings | [adapters/library_headings.py](adapters/library_headings.py): LCSH and FAST records preserved, labels read from the record; [curation/subjects.json](curation/subjects.json) |
| Attestation | [export/confidence.py](export/confidence.py): computed at read time, in words, from the claim family and its distinct authors |
| Export | [export/cytoscape.py](export/cytoscape.py): one edge per fact with its voices, attestation, and review history; the shapes of [26](26-UI-DATA-CONTRACT.md) |
| Reader | [proposals/passage_reader.py](proposals/passage_reader.py), prompt `passage-reader-v12` (rule 14: opposition) |
| Wikidata HTTP | `polite_get` in [adapters/wikidata_identity.py](adapters/wikidata_identity.py): retries 429 and 5xx with backoff |
| Migration | [migrations/004_tether_dated_claims.py](migrations/004_tether_dated_claims.py): tethered the 11 period claims spans over 200 years had left unlinked |
| Unchanged | review commands, inquiries, proposed entities, period survey, sources, capture, curation, identity |

## 4. Rules that are easy to break

1. **Visibility (L1).** Agents never accept anything, but nothing they find is hidden: proposed claims and entities appear at once, labelled with status and source. The curator promotes rather than gates. Rejected, superseded, deprecated, and dismissed appear only with `--audit`. Identity merges and splits are always curator decisions.
2. Every Proposal holds its evidence on `PROPOSES_EVIDENCE` until it is accepted. Rejecting, superseding, and retracting need a reason code.
3. A guarded write that returns zero rows was refused; `run_write` raises `RefusedWrite`.
4. Editors' notes are never cited as the source's own words; neither are PeriodO's editorial notes.
5. Preserved payloads are hashed as bytes: write them with `write_bytes`.
6. Reusable code (`proposals/`, `identity/`, `adapters/`, `discovery/`, `slices/`, `export/`, `capture/`, `harvest/`) names no source or subject; a test enforces it.
7. Tests never depend on live graph contents.
8. **Shell:** heredocs containing `\n` escapes, triple quotes, or nested quotes have failed repeatedly here. Write edit scripts to the scratchpad with the editor and run them, or edit files directly.
9. Delegated review follows [21](21-REVIEW-DELEGATION.md); on hold until the curator says go.
10. Readers find passages themselves; inquiries name whole works.
11. A missing date never excludes a claim (UNDATED). Unary claims such as `occurred` and `born` need their time.
12. Interpretations are content: attributed `exemplifies` and `ledTo`, passages of note.
13. Periods are discovered, never seeded by hand.
14. Strip Perplexity signed (`X-Amz`) links from docs before committing.
15. `imaginative` is never chosen: it follows from the attributed Work's `form`. Fiction can never support an asserted claim.
16. Attestation is computed in words at read time; never store a confidence score.
17. **Never display a code alone** (QID, PID, LCSH, FAST): the authority's own label with the code beside it. Check every identifier and class at its authority before storing it; never from memory (this session found LC's cancelled DG269, the legacy P1415 error, and a P7047 for fictive characters only). LCC is not used.
18. **Every date tethers to the Year backbone**: no bare date properties; during, within, or start/end (25 §10).
19. Harvest kinds come only from classes checked against their Wikidata labels; anything else waits for the agent. US city classes stay out (Alexandria, Virginia).

## 5. Waiting for the curator

Settled 2026-10-13 (late): the actor list (25 §13, with the Gracchi, Cleopatra, and Agrippa added); the second Antony expansion ran (25 harvested, 50 new entities, 19 waiting for the budget); Work forms set on the five Works (Plutarch and Weigall biography; Dio, Hale, Strauss history); local commits pushed.

1. **Which actor comes next**: Caesar (the test life) or Hannibal (strict chronology).
2. Powers such as *imperium*: kind Type (Institutions response) replacing kind Office (24 §8 decision 4)?
3. The harvest maps Wikidata P361 "part of" on a Person (Antony → triumvirate) to `partOf, subperiodOf`; proposed: leave it unmapped on a Person until a membership predicate exists.
4. Notes in 04, 06, and the Use Cases response pointing to 25 where they predate "everything visible" and enrichers by kind.
5. From earlier: two proposed periods (Roman Republic, Empire), 11 PeriodO Works, the `authorOf` claims, the 13 `commanded` claims in design mode, the reader's remaining claims and notes.

## 6. Next steps

1. **Increment 4: registry v9 and the first structure enricher.** Kinds **Type** and **Polity**; predicates `partOf` for Groups and Types, `instanceOf`, `precedes`, `electedBy`, `exercisedPower`, `heldPower`, `servedUnder`; a quantity qualifier (min, max, typical). Then Polybius 6 as a structure inquiry (constitution and army). Design: the Response doc above and 25 §12.
2. **The actor-centred build** (25 §13): per actor, harvest and expand, enrich structures, read the life (Plutarch's *Caesar* among the first).
3. Smaller items: the agent's choice of what to expand first (now mechanical: people, events, places, then label); window labels should read "sometime 68–50 BCE"; predicates for the unmapped Wikidata relationships (gens, unmarried partner, stepparent, relative with kinship, allegiance, member of); names over time through an alias property showing the common name (Octavian, not "Augustus", in 31 BCE); Subject coverage and reading state (25 §8); L2b CIDOC CRM mappings; motives (`sought`, `influenced`, parked).
4. Held: option B (folding Proposals into claims). Later: the read API, the Figma explorer, the growth loop beyond one hop.

## 7. Known gaps

- Persons in the graph are proposed from Wikidata only; no reader has read their lives yet.
- Wikidata statements without references are weak voices but count as one source in attestation.
- Disputes across claim families (Dio and Hale naming different commanders) are not detected.
- The scope rule for reader inquiries is fixed in code; person inquiries need it widened.
- Entity context is Wikidata-only and English-only.
- Neo4j Bloom is for smoke tests only; the product is the custom React and Cytoscape.js explorer.
- `Temporal/Neo4j-f7b612a3-Created-2026-02-19.txt` is the legacy Aura credentials export, tracked and pushed earlier; the curator is taking the instance down.
