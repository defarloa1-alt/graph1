# Session Handoff — 2026-10-13

**Branch:** `graph-revised-clean-start`. Private on GitHub (`origin`) up to `c19aceb`; 35+ local commits are not pushed (push only with the curator's go-ahead).
**Next phase:** [25-LIVES-AND-PLAYGROUND.md](25-LIVES-AND-PLAYGROUND.md) — read it first. It changes the direction agreed in earlier sessions.
**History:** [18-PHASE-5-PROPOSALS.md](18-PHASE-5-PROPOSALS.md) (Phase 5), [22](22-CLAIM-QUALIFIERS.md) (qualifiers), [23](23-NARRATIVE-AND-NOTES.md) (notes, interpretation, capture), [24](24-PERIODS-AND-TRANSFORMATION.md) (periods, the PeriodO survey in §3b).

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
python -m GraphRevised.proposals.review list --status submitted
python -m GraphRevised.proposals.review entities
```

- Local Neo4j only: `neo4j://127.0.0.1:7687`, database `neo4j`. Never the legacy Aura instance; never run legacy scripts against the local database.
- **Do not load the repo `.env` wholesale**: it holds the legacy Aura `NEO4J_URI`. Code reads only `ANTHROPIC_API_KEY` from it.
- `Connections.txt` holds the local password; it is git-ignored. Never print or commit it.
- Live tests run in rolled-back transactions with synthetic fixtures; they never change the graph.
- `.obsidian/` and the curator's Obsidian edits to the `.md` files are theirs: never touch the folder, and stage only your own hunks.

## 2. Graph state (2026-10-13)

4,645 nodes, 5,449 relationships (4,025 Year nodes from 2000 BCE to 2025).

| Label | Count | Notes |
|---|---:|---|
| Entity | 50 | 16 Person, 11 Group (Actium forces), 3 Concept, 1 Event, 1 Place (provisional); 5 Works provisional; **11 Works and 2 Periods proposed** |
| AuthorityRecord | 19 | Wikidata identity links, each with a preserved payload |
| SourceObservation | 153 | passages: 19 Perseus (Plutarch), 11 LacusCurtius (Dio), 106 Gutenberg (Weigall, Hale); 13 PeriodO records; 4 Wikidata statements |
| Assertion | 97 | 10 accepted, 86 proposed (2 interpretive), 1 rejected |
| Proposal | 172 | 20 accepted, 9 rejected, **143 submitted** |
| Annotation | 128 | 115 passages of note, 13 entity mentions (all flagged) |
| Subject | 1 | History of the Battle of Actium |

Works read: Plutarch *Life of Antony*, Cassius Dio *Roman History* 50–51 (Cary), Weigall *The Life and Times of Cleopatra*, Hale *Famous Sea Fights* ch. 2. Strauss's *The War That Made the Roman Empire* exists for curator capture only.

## 3. What exists

| Area | Artifact |
|---|---|
| Graph operations | [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher) — 33 guarded, retry-safe operations, loaded by name through [operations.py](operations.py) |
| Draft contract | [proposals/schema.py](proposals/schema.py) — `proposal-draft-v4`: quotations; mode (asserted or attributed); context, role, and time qualifiers with qualifier quotations |
| Predicates | [proposals/predicates.v8.json](proposals/predicates.v8.json) — 26 predicates (v8 adds `born` and `died`, dated unary claims; P1344 maps to participatedIn). Factual: participation, command and authority, alliance, opposition (`opposed`, symmetric, time required, optional war or battle as context; no Wikidata mapping), family, offices, birth and death places, event structure, `occurred` (Event or Period), period order. Interpretive, attributed only: `depictsSameAs`, `exemplifies`, `ledTo`. v7 also lists Work forms; a claim attributed to a Work of a creative form (poem, play, novel, film, painting, …) is stored as `imaginative`, derived by the validator, and fiction never supports an asserted claim |
| Validator and store | [proposals/validator.py](proposals/validator.py) (deterministic; verbatim quotes; outcomes valid, adds_evidence, duplicate, deferred, invalid; notes such as UNDATED; related claims: parallel, refines, refined-by, conflicts) and [proposals/store.py](proposals/store.py) |
| Review | [proposals/review.py](proposals/review.py) — `list`, `accept`, `reject --reason`, `reopen`, `supersede`, `retract`, `promote`, `entities`, `entity-accept [--qid]`, `entity-reject` |
| Reader | [proposals/passage_reader.py](proposals/passage_reader.py) — prompt `passage-reader-v12` (rule 14: opposition), Claude Sonnet 5.5 with server-side fallback; outputs claims, passages of note, and periods (`--outputs`); prompt caching (about 92% cache reads) |
| Inquiries | [inquiries/](inquiries) — Plutarch, Dio, Weigall, Hale. Whole works, no locators or source wording in the guidance |
| Proposed entities | [proposals/entities.py](proposals/entities.py) — local-first reuse, mentions recorded as Annotations |
| Period survey | [discovery/period_survey.py](discovery/period_survey.py) and [adapters/periodo.py](adapters/periodo.py), configured by [curation/authorities.json](curation/authorities.json); runs on its own when the reader proposes a period (24 §3b) |
| Time | [proposals/temporal.py](proposals/temporal.py) — the only year converter (Chrystallum has no year zero; EDTF and PeriodO are astronomical; Wikidata is historical); EDTF to Julian Day Number bounds; spans over 200 years get no Year links |
| Sources | [adapters/sources.py](adapters/sources.py) — Perseus TEI, LacusCurtius HTML, Gutenberg HTML behind one interface; Scaife catalogue; source plans in [discovery/](discovery) and [plans/](plans) |
| Capture | [capture/](capture) — the curator's own passages (manual, Kindle, Readwise) as private transcriptions with Annotations |
| Curation | Data, not code: manifests in [curation/](curation), applied by [slices/apply_curation.py](slices/apply_curation.py) (`--dry-run` shows duplicates) |
| Identity | [identity/local_candidates.py](identity/local_candidates.py) — local candidates before any new entity; Wikidata identity adapters |
| Harvest (L3, increments 1-2) | [harvest/apply.py](harvest/apply.py) `<QID> [--apply]` writes the harvest (dry run by default): one-hop targets become proposed Entities by kind (P31 table in the rules; unknown kinds wait for the agent), mapped and dated statements become proposed claims "according to Wikidata" with their time and qualifiers recorded on the observation (`record_statement_time`), and federation identifiers become crosswalk AuthorityRecords. Applied to Mark Antony 2026-10-13: 43 entities proposed, 51 claims, 10 crosswalk records. Report: [harvest/wikidata_harvest.py](harvest/wikidata_harvest.py) `<QID>` — report only, no graph writes: every statement of the preserved Wikidata record classed (identifier, attribute, dated, relationship, housekeeping) by [harvest/wikidata_rules.v1.json](harvest/wikidata_rules.v1.json) and the registry; qualifiers mapped; dates read with precision (`temporal.wikidata_time`) and tethered to Years (during, within, start and end); every code shown with its label (cache/wikidata-labels.json). Output in exports/harvest-<QID>.md |
| Export | [export/cytoscape.py](export/cytoscape.py) — `.cyjs` and a Cytoscape.js smoke page (git-ignored output). Every entity (also proposed and unlinked ones); **one edge per fact** (all sources' claims with the same subject, predicate, and object; imagined versions apart), with its attestation and one voice per source (quotations, locators, review history); passages of note on each entity's card; `--audit` adds rejected, superseded, deprecated, dismissed. The shapes are the UI data contract, [26](26-UI-DATA-CONTRACT.md) |
| Caches | `cache/` (git-ignored): Scaife catalogue, PeriodO dataset (version 301), each with its hash and retrieval time |
| Run logs | [runs/](runs) — one JSONL per reader run with versions, tokens, notes, and periods |

## 4. Rules that are easy to break

1. **Visibility (L1, doc 25).** Agents never accept anything, but nothing they find is hidden: proposed claims and entities appear in exploration at once, labelled with status and source (`proposed · according to <Work>` for an attribution, `proposed · from <Work>` for evidence). The curator promotes rather than gates. Rejected and superseded claims, deprecated entities, and dismissed notes appear only in audit mode (`export.cytoscape --audit`). Identity merges and splits are always curator decisions.
2. Every Proposal holds its evidence on `PROPOSES_EVIDENCE` until it is accepted. Rejecting, superseding, and retracting need a reason code (false, unsupported, malformed, underspecified, superseded-by-model).
3. A guarded write that returns zero rows was refused; `run_write` raises `RefusedWrite`.
4. Editors' notes in editions are never cited as the source's own words; neither are PeriodO's editorial notes.
5. Preserved payloads are hashed as bytes. Write them with `write_bytes`, never in text mode on Windows.
6. Reusable code (`proposals/`, `identity/`, `adapters/`, `discovery/`, `slices/`, `export/`, `capture/`) names no source or subject; a test enforces it. Subject knowledge lives in inquiries and in `curation/`.
7. Tests never depend on live graph contents.
8. **Shell:** heredocs that contain triple quotes or `\n` have failed here; write edit scripts to the scratchpad, or use the editor. On Windows, strip `\r` when passing lists from a file to a command: a trailing carriage return made the last section of each reader run fail.
9. Delegated review follows [21-REVIEW-DELEGATION.md](21-REVIEW-DELEGATION.md) and is recorded as "Claude (delegated by Tony DeFarlo)". It is on hold until the curator says go.
10. Readers find passages themselves: inquiries name whole works, and guidance gives conventions and predicate rules only, never locators or the source's words (a test enforces it).
11. A missing date never excludes a claim: it is stored as UNDATED. Unary claims such as `occurred` still need their time.
12. Interpretations are content, not noise: attributed `exemplifies` and `ledTo` claims, plus passages of note.
13. Periods have fuzzy edges and are discovered, never seeded by hand. Each source's bounds are an attributed claim.
14. Strip any Perplexity signed (`X-Amz`) links from docs before committing.
15. `imaginative` is never chosen: it follows from the attributed Work's `form`, which is fixed once a claim rests on the Work. A passage of a creative Work can never support an asserted claim, so fiction cannot be promoted to fact.
16. Attestation (`export/confidence.py`) is computed when the graph is read, in words, from the claim family and its distinct authors. Never store a confidence score.
17. Never display a code alone (QID, LCSH, FAST): always the authority's own label with the code beside it. Library headings are checked against their authority and their labels read from the preserved record ([adapters/library_headings.py](adapters/library_headings.py)). LCC is not used; never load the legacy `Subjects/LCC/dg_schedule.csv`.

## 5. Waiting for the curator

Under doc 25 these are promotions, not gates; none blocks the Lives phase.

1. Two proposed periods from Hale 2.34: *Roman Republic* (Wikidata Q17167 is the obvious match) and *Empire* (the Roman Empire, Q2277). Accepting with `--qid` lets a survey re-run match on the Wikidata names.
2. 11 proposed Works, one for each PeriodO source (Library of Congress, Heidelberg, British Museum, PACTOLS and others), and 13 PeriodO `occurred` claims.
3. *Plutarch author of Life of Antony* and *Cassius Dio author of Roman History* (from Wikidata P50).
4. 13 submitted `commanded` proposals: keep them open in design mode, then review them against the split between `commanded` and `heldAuthorityOver`.
5. The remaining reader claims and 115 passages of note from the four works.

## 6. Next steps

**The Lives phase, [25](25-LIVES-AND-PLAYGROUND.md) §3:** L1 visibility (done 2026-10-13, in the export; the Phase B read API will apply the same rule); L2 registry v7 (done 2026-10-13: `opposed`, Work forms and derived `imaginative`, attestation in words; motives parked, see 25 §6); L2b CIDOC CRM mappings in the registry (quiet; export later); L3 person inquiries in which the reader proposes Person, Event, and Place entities; L4 Plutarch's *Caesar* first, then Marius, Sulla, Pompey, and Cicero; L5 world context.

Waiting until after the Lives phase: the period consensus and the regional/general split (24 §3), Wikidata and LCSH/FAST as survey sources, the two failed `ledTo` readings, the transformation pilot (24 §4–7), depicted events, the Batch API, the read API (`getInterpretations`), index-led reading, a `check_draft` tool for agents, E8 stance.

## 7. Known gaps

- The scope rule (focus, linked entities, declared candidates) is fixed in code; person inquiries will need it widened (L3).
- Entity context is Wikidata-only and English-only.
- Force hierarchy (a wing is part of a fleet) has no predicate yet.
- PeriodO matching misses names whose stems differ across languages (German *Römische*, *Kaiserzeit*); such definitions are listed as related or not at all.
- Neo4j Bloom is for smoke tests only. The product is a custom React and Cytoscape.js explorer ([20-EXPLORER-UI.md](20-EXPLORER-UI.md)).
- The old `Temporal/` folder: only `periodo-dataset.csv` was useful, and the PeriodO cache replaces it. **`Temporal/Neo4j-f7b612a3-Created-2026-02-19.txt` is the legacy Aura instance's credentials export** (URI, user, password). It is tracked (commit `a82fcb1`) and on several branches on `origin`, so it was exposed while the repo was public: the curator should rotate that password or delete the instance; removing the file from git does not undo the exposure.
