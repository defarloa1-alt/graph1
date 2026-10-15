# Session Handoff — 2026-10-15

**Branch:** `graph-revised-clean-start`, pushed to `origin` (2026-10-13, with the curator's go-ahead; push only with it).
**Read first:** [25-LIVES-AND-PLAYGROUND.md](25-LIVES-AND-PLAYGROUND.md), sections 5-13 especially. Decided late on 2026-10-13: the Institutions response (sections Registry v9, Powers, Membership), [24](24-PERIODS-AND-TRANSFORMATION.md) §2 note and §9 (PeriodO or Wikidata), [21](21-REVIEW-DELEGATION.md) §5 (the second delegated review).
**New 2026-10-15:** depicted events built and read for the battle from four sources ([23](23-NARRATIVE-AND-NOTES.md) pilot, [29](29-EVENT-CENTRED-INQUIRY.md) §9a; walk them with [views/actium-walk.cypher](views/actium-walk.cypher)); [29-EVENT-CENTRED-INQUIRY.md](29-EVENT-CENTRED-INQUIRY.md) (the event is the inquiry; Chrystallum's account on the stage; Wikipedia as starting point; the source registry; the new order in §6), [26](26-UI-DATA-CONTRACT.md) §4a (the notes stage), [views/actium-annotations.cypher](views/actium-annotations.cypher).
**New 2026-10-14:** [27-GAZETTEER.md](27-GAZETTEER.md) (the geographic backbone, next to build), [28-SUBJECT-BUCKETS.md](28-SUBJECT-BUCKETS.md) (every entity in a bucket), 25 §11 (SCA and SFA retired).
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
  GraphRevised.tests.test_library_headings GraphRevised.tests.test_wikidata_harvest \
  GraphRevised.tests.test_registry_v9 GraphRevised.tests.test_depicted_events  # expect 241 tests, OK
python -m GraphRevised.export.cytoscape            # then open GraphRevised/exports/graph.html
python -m GraphRevised.harvest.apply Q51673 --expand   # dry run: what the next expansion would do
```

- Local Neo4j only: `neo4j://127.0.0.1:7687`, database `neo4j`. Never the legacy Aura instance; never run legacy scripts against the local database.
- **Do not load the repo `.env` wholesale**: it holds the legacy Aura `NEO4J_URI`. Code reads only `ANTHROPIC_API_KEY` from it.
- `Connections.txt` holds the local password; it is git-ignored. Never print or commit it.
- Live tests run in rolled-back transactions with synthetic fixtures; they never change the graph.
- `.obsidian/` and the curator's Obsidian edits to the `.md` files are theirs (`00`, `01`, `README` have uncommitted edits of theirs): never touch the folder, and stage only your own hunks.
- **Data is not in git** (25 §13): harvest payloads are git-ignored; the local disk holds the only copy of the graph and payloads.

## 2. Graph state (2026-10-15, after the depicted-event runs)

8,373 nodes, 11,853 relationships (4,025 Year nodes from 2000 BCE to 2025).

| Label | Count | Notes |
|---|---:|---|
| Entity | 464 | 269 depicted events (Plutarch 28, Dio 76, Hale 77, Weigall 88), all proposed; 427 proposed in all |
| Assertion | 1,160 | 68 accepted, 1,083 proposed, 1 rejected, 8 superseded |
| Proposal | 1,342 | 125 accepted, 30 rejected, 1,187 submitted (the harvest's and the depicted events') |
| SourceObservation | 670 | passages (Plutarch, Dio, Weigall, Hale), PeriodO records, Wikidata statements |
| AuthorityRecord | 258 | Wikidata identities, the crosswalk, LCSH and FAST (one record per system and identifier) |
| Annotation | 453 | passages of note (117 endorsed, 56 new flagged), entity mentions (each depicted event's first naming) |
| Subject | 1 | History of the Battle of Actium, with LCSH sh85000736 and FAST 796265 |

## 3. What exists

| Area | Artifact |
|---|---|
| Graph operations | [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher), loaded by name through [operations.py](operations.py), 41 operations; new on 2026-10-14: `link_authority`, `rename_authority_system`, `merge_authority_into` (migration 007); new on 2026-10-13: `set_work_form`, `upsert_subject_authority`, `record_statement_time`, `renormalize_statement_time` and `unlink_assertion_years` (migration 005); `upsert_qualified_assertion` stores a quantity and no longer insists the context is an Event; `link_assertion_years` takes `{year, as}` links |
| Depicted events (2026-10-15) | Registry [predicates.v10.json](proposals/predicates.v10.json): `happenedBefore` (Event to Event, the source's order), `occurred` with an optional context event (a time marker's anchor). Reader prompt `passage-reader-v13`: `depicted_events`, turned into proposed Events and attributed claims by `to_depicted` and `depicted_drafts`; optional reader text is an empty string, not null (the output grammar limit). Event inquiries: `sources` (one event, several Works, each with `voice` and guidance); the reader takes `--source` and `--chapters`; a dry run keeps a source in one rolled-back transaction. [inquiries/actium-battle.json](inquiries/actium-battle.json); [views/actium-walk.cypher](views/actium-walk.cypher), [views/actium-annotations.cypher](views/actium-annotations.cypher) |
| Draft contract | [proposals/schema.py](proposals/schema.py), `proposal-draft-v6`: `TimeQualifier.mode` (during, within); v6 `QuantityQualifier` (minimum, maximum, typical, the source's words), part of a claim's identity by its figures |
| Predicates | [proposals/predicates.v9.json](proposals/predicates.v9.json), 33 predicates: v7 `opposed` and Work forms; v8 `born` and `died`; **v9** kinds Type and Polity, `instanceOf`, `precedes`, `electedBy`, `exercisedPower`, `heldPower`, `servedUnder`, `memberOf`, `partOf` for Groups and Types (`kindPairs`), quantity on `partOf` and `electedBy`, context and role kinds per predicate; P361 chosen by kind, P463 to `memberOf` |
| Validator and store | [proposals/validator.py](proposals/validator.py): derives `imaginative` from the attributed Work's form; refuses fiction as evidence for an asserted claim; compares a Wikidata statement's recorded time with the claim's (refuses a mismatch; Wikidata's "unknown value" leaves the claim undated); v9: paired kinds (`kindPairs`), context and role kinds per predicate, a quantity shown by its own quotation. [proposals/store.py](proposals/store.py): a stored claim's time mode and quantity round-trip at review (before the fix, a claim dated within a window could not be accepted). [proposals/wikidata_proposer.py](proposals/wikidata_proposer.py): drafts only the predicates whose kinds fit the endpoints |
| Time | [proposals/temporal.py](proposals/temporal.py), the only year converter: `wikidata_time` (precision day to century; BCE decades and centuries counted down), `year_links` (during, earliest/latest for a window, start/end for spans over 200 years; outside the backbone named in a note) |
| Harvest (L3, increments 1-4) | [harvest/wikidata_harvest.py](harvest/wikidata_harvest.py) `<QID>`: a report, no writes. [harvest/apply.py](harvest/apply.py) `<QID> [--expand] [--limit 50] [--apply]`, dry run by default: one-hop targets become proposed Entities by kind (the P31 table in [harvest/wikidata_rules.v1.json](harvest/wikidata_rules.v1.json), one level of superclasses, disambiguation pages dropped, unknown kinds wait for the agent); mapped and dated statements become proposed claims "according to Wikidata"; federation identifiers become crosswalk records; `--expand` harvests the surfaced people, events, and places within a budget of new entities; v9: kind Polity (historical country, empire, Hellenistic kingdom; before Period), P361 by kind, P463 to `memberOf`, a date known only to its decade or century read as sometime within it |
| Library headings | [adapters/library_headings.py](adapters/library_headings.py): LCSH and FAST records preserved, labels read from the record; [curation/subjects.json](curation/subjects.json) |
| Attestation | [export/confidence.py](export/confidence.py): computed at read time, in words, from the claim family and its distinct authors; a fact that happens once (registry `once`) is disputed by differing times, contexts, or roles, any other fact only by different figures for one time |
| Export | [export/cytoscape.py](export/cytoscape.py): one edge per fact with its voices (time, role, context, quantity), attestation, and review history; the shapes of [26](26-UI-DATA-CONTRACT.md); Polity and Type styled |
| Neo4j view | [views/explorer-view.cypher](views/explorer-view.cypher): the explorer's picture in Neo4j Desktop (the canvas, a focus, its card, a year's synchronism; an APOC variant with true lines) and a Browser style |
| Reader | [proposals/passage_reader.py](proposals/passage_reader.py), prompt `passage-reader-v12` (rule 14: opposition); its predicate guide is built from the registry, so it now lists the v9 predicates (recorded through `predicateRegistryVersion`); no structure rules yet (v13, next steps) |
| Wikidata HTTP | `polite_get` in [adapters/wikidata_identity.py](adapters/wikidata_identity.py): retries 429 and 5xx with backoff |
| Migrations | [004](migrations/004_tether_dated_claims.py): tethered the 11 period claims spans over 200 years had left unlinked. [005](migrations/005_window_dates.py) (applied 2026-10-13): eight births and deaths known only to their decade or century, stored as true throughout it (710 Year links), superseded by claims dated sometime within it (16 links); the observations' reading corrected (`renormalize_statement_time`, the former mode kept), the old claims' Year links removed (`unlink_assertion_years`). [006](migrations/006_annotation_labels.py) (applied 2026-10-14): the 128 annotations relabelled by what and where ("Anecdote · Weigall 17.11") instead of repeating their note; new ones are labelled so by `capture.core.annotation_label`; [007](migrations/007_lc_systems_and_ranks.py) (applied 2026-10-14): Wikidata's LC identifier (P244) named by its file, sh as LCSH and n as LCNAF (harvest rule `byPrefix`), so the Battle of Actium's heading is one record linked from the Event and the Subject; the harvest links an existing record without relabelling it; every crosswalk link records the statement's rank and references, and the export shows one record per system, the best-supported first (Cleopatra: VIAF 67762941 "and 7 more") |
| Unchanged | review commands, inquiries, proposed entities, period survey, sources, capture, curation, identity |

## 4. Rules that are easy to break

1. **Visibility (L1).** Agents never accept anything, but nothing they find is hidden: proposed claims and entities appear at once, labelled with status and source. The curator promotes rather than gates. Rejected, superseded, deprecated, and dismissed appear only with `--audit`. Identity merges and splits are always curator decisions.
2. Every Proposal holds its evidence on `PROPOSES_EVIDENCE` until it is accepted. Rejecting, superseding, and retracting need a reason code.
3. A guarded write that returns zero rows was refused; `run_write` raises `RefusedWrite`.
4. Editors' notes are never cited as the source's own words; neither are PeriodO's editorial notes.
5. Preserved payloads are hashed as bytes: write them with `write_bytes`.
6. Reusable code (`proposals/`, `identity/`, `adapters/`, `discovery/`, `slices/`, `export/`, `capture/`, `harvest/`) names no source or subject; a test enforces it. So do the registry's predicate definitions, which the reader's prompt shows.
7. Tests never depend on live graph contents.
8. **Shell:** heredocs containing `\n` escapes, triple quotes, or nested quotes have failed repeatedly here. Write edit scripts to the scratchpad with the editor and run them, or edit files directly.
9. Delegated review follows [21](21-REVIEW-DELEGATION.md), per request; the curator may widen its scope explicitly, as on 2026-10-13 (21 §5). Delegated decisions are signed `Claude (delegated by Tony DeFarlo)`.
10. Readers find passages themselves; inquiries name whole works. Agents choose those works (25 §13): confirmed at a catalogue, rights checked by rule, within a budget, the plan kept and visible.
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

Settled this session (2026-10-13), recorded where named: the actors and their chronological order, Hannibal next (25 §13); agents choose the sources (25 §13); Work forms on the five Works; powers are kind Type and Antony a member of the Second Triumvirate (Institutions response); the Roman Republic, Kingdom, and Empire are Polities (24 §2); facts that happen once are the only ones disputed by differing times (registry `once`); the period "Empire" relabelled **Roman Empire**; PeriodO and Wikidata both kept, in different roles (24 §9); the delegated review of the `authorOf` claims, the design-mode `commanded` claims, and the reader's claims and notes ([21](21-REVIEW-DELEGATION.md) §5).

Settled 2026-10-14: the actors as data ([curation/actors.json](curation/actors.json), each Wikidata identity checked); the SCA and SFA retired, their ideas kept as rules for the harvest and enrichers (25 §11); one record per authority system and identifier (migration 007); **the geographic backbone first**, a gazetteer layer from Pleiades and the GeoNames administrative tree, TGN as identifiers only ([27](27-GAZETTEER.md)); **every entity in a subject bucket**, our own hierarchy anchored to LCSH and FAST, membership computed from claims, Wikidata's main subject (P921) not used ([28](28-SUBJECT-BUCKETS.md)).

Settled 2026-10-15 ([29](29-EVENT-CENTRED-INQUIRY.md) §2): the event is the inquiry, not a Work; Chrystallum's account on the stage beside the event, every statement citing a preserved passage; Wikipedia as a starting point (discovery, the card's link, a labelled tertiary voice); facets as lens steps in the drill-down path; the event-centred research run after the gazetteer and before the subject buckets; a notes stage beside the facts stage (26 §4a).

Open:

1. **Twelve claims the delegated review left open** ([21](21-REVIEW-DELEGATION.md) §5): Publicola as Lucius Gellius Poplicola (identity, three proposals); Plutarch's pronouns resolved only by the neighbouring passage (65.3 Antony; 65.4 Caesar, three proposals); our own single-source command statements (Insteius's centre, Antony's right wing, Antony's fleet, Taurus); Dio's near-duplicate date of Actium, to supersede by its twin.
2. **The two proposed periods** (Roman Republic, Roman Empire) and the **11 PeriodO Works** of the survey, with its 11 flagged mentions: accept, link, or reject (`review entities`). The Wikidata QIDs of the Roman periods now identify Polities, so the reader's periods take no QID.
3. **The three PeriodO changes** proposed in 24 §9 (P9350 as an identity candidate; PeriodO's QIDs shown as places covered; world bands from general definitions).
4. The Wikidata harvest's proposed claims (about 440) await promotion; none is delegated.

## 6. Next steps

**2026-10-15:** the depicted-event pilot (23 §5) is done for the battle's chapters in all four sources; next for it: review (the 269 events are visible, proposed), Hale's inferences arriving as factual events, shorter labels. Registry v9 is built (kinds Type and Polity, the structure predicates, quantity; see section 3). In order (the backbones first, curator, 2026-10-14; **revised 2026-10-15**: after the gazetteer comes the event-centred research run for the Battle of Actium, [29](29-EVENT-CENTRED-INQUIRY.md) §9, which absorbs item 3 below; then the subject buckets):

1. **The gazetteer** ([27](27-GAZETTEER.md)): the dumps are downloaded to `cache/geonames/` and `cache/pleiades/` (2026-10-14, with `metadata.json` beside each: source, retrieval time, Last-Modified, SHA-256, licence). Build: constraint and point index for `Location`; batched operations; the loader (dry run by default) for the GeoNames tree (about 462,000 units), all 42,399 Pleiades places with their ancient `WITHIN` links, the bridge (Pleiades' GeoNames references, else the nearest populated place within 50 km, curator 2026-10-14); then the 13 Place entities linked by the identifiers they hold.
2. **Subject buckets** ([28](28-SUBJECT-BUCKETS.md)): `BROADER` from the headings' broader terms, membership computed from claims (registry data says which predicates carry it), the Punic Wars as the first hierarchy (headings checked 2026-10-14).
3. **The agent's source choice** (25 §13): the source plan's last step, now the curator's, becomes the agent's, with its guardrails (each candidate confirmed at a catalogue before fetching; rights by rule, copyrighted works curator capture only; a cost budget; the plan and its reasons kept and visible). Needed first, because Polybius and Hannibal's sources are the agent's to find.
4. **The first structure enricher: Polybius 6** (constitution and army; design in the Institutions response and 25 §12). Needs: the reader may propose Type entities (local-first, like periods and depicted events); reader prompt v13 with rules for `partOf` between Types with a quantity and its quantity quotation, `instanceOf`, `electedBy`, `exercisedPower`, `precedes`; an inquiry naming the whole Work. Whole-work cost about $1-4 on Sonnet 5.5.
5. **Notes that stand in for claims.** A passage of note is a pointer into the literature and asserts nothing; the facts of its passage belong in claims beside it. On the Actium works the reader often had no predicate or entity for those facts, so a note is all the graph holds (Weigall 16.6: nineteen Roman legions and the contingents assembled at Ephesus, no claim; twelve notes say outright that no predicate fitted). Needs: reader v13 to use the v9 predicates (`partOf` with a quantity between forces); the reader proposing Place, Person, and Group entities (L3, local-first, visible at once), so Ephesus and the contingents can exist; a force placed somewhere at a time through a depicted event (an assembly that `occurredAt` a Place, the forces `participatedIn` it) with today's predicates. Then re-read the passages whose notes stand in for claims, keeping the notes for colour only.
6. **Hannibal**, the first actor in chronological order (25 §13): harvest and expand, enrich the structures his life touches, the agent's source plan, then the reader. Then Scipio, the Gracchi, and on.
7. Smaller items: the agent's choice of what to expand first (now mechanical: people, events, places, then label); window labels should read "sometime 68–50 BCE"; predicates for the unmapped Wikidata relationships (gens, unmarried partner, stepparent, relative with kinship, allegiance); names over time through an alias property showing the common name (Octavian, not "Augustus", in 31 BCE); Subject coverage and reading state (25 §8); L2b CIDOC CRM mappings; motives (`sought`, `influenced`, parked).
8. Held: option B (folding Proposals into claims). Later: the read API, the Figma explorer, the growth loop beyond one hop.

## 7. Known gaps

- Persons in the graph are proposed from Wikidata only; no reader has read their lives yet.
- Facts the reader found but could not state (no predicate, no entity) survive only as passages of note; see next step 3.
- A Wikidata span whose start or end is known only to its decade (a marriage "from the 70s BCE") is still read from that decade's first or last year as a definite bound; its uncertainty is not yet a window on that end.
- A Wikidata "part of" pointing at a class (Q83204 *triumvirate*) waits as "kind unknown"; the agent step that finds the instance (Q212079 *Second Triumvirate*) is not built. Antony `memberOf` the Second Triumvirate has no Wikidata evidence (Q212079 lists no members): it will come from the reader.
- Wikidata statements without references are weak voices but count as one source in attestation.
- Disputes across claim families (Dio and Hale naming different commanders) are not detected.
- The scope rule for reader inquiries is fixed in code; person inquiries need it widened.
- Entity context is Wikidata-only and English-only.
- Neo4j Bloom is for smoke tests only; the product is the custom React and Cytoscape.js explorer.
- `Temporal/Neo4j-f7b612a3-Created-2026-02-19.txt` is the legacy Aura credentials export, tracked and pushed earlier; the curator is taking the instance down.
