---
status: informational
authority: none; the one current-state page. Decisions are in 33-DECISIONS.md; meaning and storage in 02
depends_on: [33-DECISIONS.md, 02-GRAPH-MODEL.md]
supersedes: [19-SESSION-HANDOFF.md, 38-REASONING-SESSION-HANDOFF.md, 40-LENS-SESSION-HANDOFF.md]
last_reviewed: 2026-11-16
---

# Current state

This page replaces the session handoffs (19, 38, 40), which are now history.
Each session updates this page in place, and does not start a new handoff.
Which document governs what is [33](33-DECISIONS.md) §1: 02 for meaning and
storage, 31 for behaviour, then 29, 32, 26. This page governs nothing.

## 1. Start here

```bash
cd C:/Projects/Graph1
export NEO4J_PASSWORD=$(python -c 'from GraphRevised.connector.server import neo4j_password as p; print(p())' 2>/dev/null)
python -m pytest GraphRevised/tests -q   # about 7 minutes; see §6 for the expected result
```

- **Local Neo4j only:** `neo4j://127.0.0.1:7687`, database `neo4j`. Never the
  legacy Aura instance (deleted), and never legacy scripts against this database.
- **Do not load the repo `.env` wholesale.** It holds the legacy Aura
  `NEO4J_URI`. Code reads only `ANTHROPIC_API_KEY` from it.
- `Connections.txt` holds the local password and the MCP token. It is
  git-ignored: never print it or commit it.
- **The graph is a sandbox** (curator, 2026-11-13): its purpose now is to check
  that claims are comprehensive and understandable. Review volume is not a
  concern for now. Claude may write through the guarded operations as needed.
- **Commits:** only when the curator asks. Keep `.obsidian/` and the curator's
  own Obsidian edits to the `.md` files out of commits. Push only with the
  curator's go-ahead.
- **Data is not in git** (25 §13). Harvest payloads are git-ignored, so the
  local disk holds the only copy of the graph and its payloads. There is no
  scheduled backup yet (§5).

## 2. Graph state (counted 2026-11-16)

| Label | Count | Notes |
|---|---:|---|
| Entity | 784 | Event 483, Person 97, Work 65, Group 45, Type 41, Place 25, Office 18, Concept 3, Period 3, Polity 3, Object 1 |
| Assertion | 2,662 | proposed 1,754, accepted 544, superseded 362, rejected 2 |
| Proposal | 2,963 | submitted 1,820, accepted 688, rejected 455 |
| SourceObservation | 856 | passages, PeriodO records, Wikidata statements, 39 coin records (CRRO) |
| AuthorityRecord | 325 | Wikidata identities, the crosswalk, LCSH and LCNAF headings, FAST |
| Annotation | 928 | passages of note, entity mentions |
| Subject | 20 | |
| Fact-layer edges | 2,126 | derived (D-144) |
| Year, Location | 4,025, 505,546 | the backbones, off the canvas |

- **59 guarded operations** in
  [13-PHASE-3-DIRECT-OPERATIONS.cypher](13-PHASE-3-DIRECT-OPERATIONS.cypher),
  loaded by name through [operations.py](operations.py).
- **The database enforces the logical model** (D-158, D-159, D-161, 2026-11-18): a
  Cypher 25 graph type set by
  [migrations/018_graph_type.py](migrations/018_graph_type.py), 694
  constraints. A write that breaks the model (a Person without `Entity`, an
  `ATTRIBUTED_TO` to a non-Work, a `BORN_AT` from an Event) now fails at
  commit. 018 is the schema: change its tables and re-run it, never add a
  constraint by hand. The registry is also in the graph (`Predicate`,
  `EntityKind`, `PredicateRegistry`; [proposals/registry_graph.py](proposals/registry_graph.py)).
  **After a registry bump:** `python -m GraphRevised.proposals.registry_graph --apply`,
  then `python -m GraphRevised.migrations.018_graph_type --apply`, then
  `python -m GraphRevised.export.fact_layer --apply`.
- **Predicate registry v17**
  ([proposals/predicates.v17.json](proposals/predicates.v17.json)); draft schema v8
  (2026-11-16: Question, Position and the historiography predicates; no Question or
  Position in the graph yet).
- 483 events against 97 people, though D-030 says people first: most of the
  difference is depicted events, one set per source. The curator is reviewing
  whether this is intended (2026-11-13).

## 3b. What changed later on 2026-11-16: historiography built (D-156)

Doc 44 steps 1 to 4, from the curator's go-ahead; details in [44](44-HISTORIOGRAPHY-AND-DEBATES.md) §7.
Nothing was written to the graph and no model was called.

- **Registry v17, draft v8:** kinds `Question`, `Position` (also in the operations'
  kind lists, the connector, entity review, contracts, explorer and Cytoscape styles);
  `about`, `answers`, `holds` (stance), `rejects`, `hadReception` (reception), all
  interpretive. Choices for the curator to check are in D-156.
- **Wording:** a Position's `history` (held by, rejected by, when, reception, whose
  report) in `export/confidence.py`; a `holds` line says "in its own words" or
  "reported by". The fact layer writes `history` on Position nodes; a Question is
  one hop from its event by its ABOUT edge. The explorer has the data shapes only.
- **Lens prompt and storing:** rule 18 and `proposals/historiography.py` (output
  section, conversion, `store_historiography`). Runner:
  `python -m GraphRevised.proposals.article_reader lange-2011 --inquiry
  GraphRevised/inquiries/actium-battle.json --pages 608-609 [--show] [--read [--submit]]`.
  The default is a dry run: worst case $0.90 for two pages (Sonnet, before caching).
  Licensed pages are cited by transcriptions of at most 600 characters (curator: fine).
- **First paid reading, Lange p. 608** (curator's go-ahead; `--read`, rolled back,
  nothing stored; $0.30, almost all the cache write): 1 Question (Antony's aim), 2
  Positions (fought to win until Cleopatra fled; meant to break out), Dio `holds` the
  breakout view, both receptions "dominant" over their spans; 6 holders not held as
  Works (Kromayer 1899, "Gilles" (doc 44 has Gillies; check the page), Leake, Merivale, Gravière, "the
  ancient writers"); no lens claims. Log in `runs/article-reader-lange-2011-*`.
- **Stored: Lange pp. 608-609** (`--read --submit`, curator's go-ahead; $0.35; $0.65 in
  all on budget `actium`). 15 claims, all proposed, attributed to Lange; 3 Questions
  and 5 Positions, proposed; fact layer rebuilt. **Near-duplicates to review** (a bug,
  since fixed: page 609 was not shown page 608's entities): two Questions on Antony's
  aim; "Antony fought for victory until Cleopatra fled" / "Antonius was fighting to
  win"; "Antony aimed to withdraw by sea, not to win" / "Antonius aimed to withdraw
  with much of his force". Merges are the curator's (D-152). Holders not held as Works,
  in the run log: Kromayer (1899), Ferrabino (1924), Tarn (two positions), Leake,
  Merivale, Gravière, "Gilles", "the ancient writers apart from Dio". Lange's own
  position is not on these pages.
- **Fix: known Questions and Positions per page.** They are now in the per-passage
  message (not the cached packet), refreshed after each page.
- **Output grammar limit** (found 2026-11-16): the API refuses an output schema whose
  compiled grammar is too large (a 400, not billed). `LensReaderOutput` had passed it;
  fixed by giving a predicate need its kinds as one text field ("Person/Group ->
  Office", split by code), probed to compile. The article reading asks for claims and
  historiography only. The general reader's output was probed and compiles.
- **Spend meter:** a billed reply that fails to parse is now logged at its ceiling,
  marked `estimated` (two earlier 16-token probes went unlogged, negligible).
- **Stored: Lange pp. 610-623** (2026-11-17, `--read --submit`, curator's go-ahead;
  $1.14; $1.79 in all on `actium`). 155 drafts, 152 stored, all proposed; 1 refused (a
  Position on a Question not proposed: did Cleopatra plan the flight beforehand). The
  graph now has 13 Questions and 27 Positions for Actium, Lange's own thesis among them
  (Antony fought to win until Cleopatra fled; a hard-fought, well-matched battle;
  Cleopatra's flight, not defection, decided it). **To review:** "Antonius was fighting
  to win" and "Antonius had 500 warships" are each both held and rejected by Lange
  (likely a misread); the ships Question has 7 overlapping Positions; "Antony aimed to
  withdraw by sea" answers both duplicate aim Questions. **Unresolved holders** (in the
  run log, not stored): Kromayer, Tarn, Pelling, Carter, Murray, Mommsen, Syme (The
  Roman Revolution, not the Work held), Orosius, Florus, Livy, Augustus' lost
  autobiography.
- **Book footnotes in notes** (2026-11-17): `capture/notes.py` reads `[^n]` marks and
  footnotes, keeps them on the transcription (`footnotes`; new operation
  `add_transcription_footnotes`), never in the curator's text (32 §2.1a). `check` no longer
  crashes on a Windows console. `notes suggest` lists candidate `concerns` for an unfilled
  note (label words matched, code only; it cannot tell two Cleopatras apart).
- **Note reader built** (D-157; `capture/note_reader.py`; not yet run for pay). `triage`:
  one small call per unfilled note (~$0.03) picks `concerns` from the code's candidates and
  lens tags from `curation/lenses.json`, and writes them into the note, marked
  `# suggested`. `read`: the lens reader on an applied note's transcription, the curator's
  text as a prompt only (`Inquiry.curator_note`); `--submit` stores, all proposed. Both are
  dry runs by default. The lens catalogue has six lenses (general, military, political,
  economic, social, religious): no geography lens, which the triage reports as missing. Next: follow footnotes to held passages (`RESTS_ON`), and
  a paid, metered note reader (claims from the quote, suggested `concerns`, links to held
  events, lens tags and Questions from the curator's thought; all proposed).
- **Debates in the event snapshot** (2026-11-17): `add_debates` in
  `discovery/subject_view.py` (Question -> Position -> holders, receptions, history);
  explorer does not display it yet.
- **`.gitignore`:** `data/` had hidden `explorer/app/src/data/types.ts` (never
  committed); the folder is now excepted.

## 3a. What changed 2026-11-14 to 2026-11-16

Decisions D-147 to D-155 ([33](33-DECISIONS.md)). Plans:
[41](41-ENDGAME-PLAN.md) (end game), [42](42-CORROBORATION-AND-CLAIM-KINDS.md)
(corroboration, built), [43](43-ACTIUM-MILITARY-FRAME.md) (military frame),
[44](44-HISTORIOGRAPHY-AND-DEBATES.md) (historiography, decided, **not built**).

- **Spend meter** (41 §3.8): every model call is metered and capped; see §4 rule 1.
- **Corroboration** (D-148, 42): Works have a `standing` (primary, secondary,
  tertiary; the 56 then present confirmed by the curator); modern claims a `basis`
  (reports, reconstructs, unknown); `RESTS_ON` links a modern claim to the ancient
  passage it retells. Attestation counts lines of evidence, not authors.
- **Wikipedia footnotes** (D-150): `harvest/wikipedia_footnotes.py` follows the
  Actium article's footnotes to our passages: 155 rests-on links, 15 facts moved
  from reference only to attested.
- **Coverage report** against "done" (41 §4): items 1, 5, 7 met; 2 (lens reads),
  3, 4 (442 open placements) not; 6 not built.
- **Military frame** (43): registry v16 (`hadStrength`, `captured`,
  `surrenderedTo`, `defectedTo`; Type categories ship type and naval fitting;
  Work form coinage; quantity `precision`). 17 Types seeded
  (`slices/seed_types.py`, curation/military-types.json).
- **Coins** (D-151): CRRO's dump (ODbL 1.0, in `crro/`, the dump git-ignored);
  `harvest/crro_coins.py rrc-544`: Antony's legionary series as a primary Work,
  39 coin records, 25 unit Groups, each `partOf` Antony's land forces (for review)
  and `instanceOf` legion or cohort (by rule).
- **First merge** (D-152): titled legions (12 Antiqua, 17 Classica, 18 Libyca)
  merged into their numbers, the title kept as an alternative name
  ([migrations/013](migrations/013_merge_titled_legions.py), operation
  `merge_unreviewed_entity`, code-made duplicates only). The general merge
  mechanism is still to be designed.
- **Lange 2011** (Classical Quarterly; the Actium debate): the curator's JSTOR PDF
  in `docs/actium/` (git-ignored: copyright, and the downloader's IP on every
  page; never store its text). Registered as a secondary Work
  ([migrations/014](migrations/014_register_lange_2011.py)).
  `harvest/article_citations.py lange-2011 [--save]` lists its 67 ancient
  citations: 37 held, 12 in held Works but not held (to fetch), 15 in Works not
  held (Orosius 6.19, Florus 2.21, Horace Epode 9, Suetonius Aug. 17.2, and
  others), 3 unresolved; and about 44 modern works (by pattern). Report in `runs/`.
- **Historical thinking is a focus** (curator, 2026-11-15; D-153, doc 44):
  Questions, Positions held or rejected by Works (ancient authors too), reception
  over time. Decided, not built.
- **Wikidata references as voices** (D-154): `harvest/wikidata_references.py`;
  works classed in curation/wikidata-reference-works.json. 80 claims gained a
  voice (DPRR 66, Syme 6, Broughton 4, Britannica 3, Roller 1). Six single
  encyclopedia entries wait on resolving their encyclopedia (`_pending` in that file).
- **LC subjects** (D-155): `harvest/lc_subjects.py`: every subject heading of a
  book's LC record (Strauss: 5), and each held LCSH heading's broader and related
  headings, one hop. Actium and Philippi now share LC's campaign heading.
- **Review desk** fixed: the part and other-end jumps no longer error.

## 3. What changed on 2026-11-13

The README's review of 2026-11-13, item 3 (close the unfinished items):

- **Type categories** (D-141). Every Type now has a `typeCategory` from the
  registry's `typeCategories`: role, unit type, organizational pattern, power,
  or status. Status is new. The 22 event roles are role, and matrona is
  status. The new operation `set_type_category` keeps who set the category,
  when, the basis, and the category it replaced.
  ([migrations/009](migrations/009_type_categories.py)).
- **`hadStatus` requested** (Person to Type, shape state), with Fulvia the
  matrona as evidence
  ([curation/predicate-needs.json](curation/predicate-needs.json)).
- **Polity dates** (D-142). Each Polity has one proposed `occurred` span from
  its Wikidata record. Registry v15 lets a Wikidata mapping evidence one
  **bound** of an interval: inception (P571) or start time (P580) for the
  start, and dissolved (P576) or end time (P582) for the end. So one span
  claim rests on two statements, and the validator checks each end against
  its own statement. The deterministic proposer never drafts from a bound
  alone. Built by [slices/polity_spans.py](slices/polity_spans.py):
  - Roman Republic: 509 BCE to 16 January 27 BCE;
  - Ptolemaic Kingdom: 305 BCE to 30 BCE;
  - Roman Empire: January 27 BCE (start time, since there is no inception) to
    17 January 395 CE (the preferred rank). The rationale names 476 and 1453.
- **The Campsite Memorial of Augustus is an Object** (curator, 2026-11-13),
  the graph's first. Strauss says Octavian "dedicated the monument on the site
  of his headquarters", so:
  - the dedication now `occurredAt` a new local Place, Octavian's camp at
    Actium ([curation/campsite-memorial.json](curation/campsite-memorial.json));
  - the old claim, which named the monument as the place, is superseded;
  - the memorial is `involvedIn` the dedication, with the new role Type
    **dedicated** (added to
    [curation/event-roles.json](curation/event-roles.json); category role).

  Where the memorial stands waits for `locatedAt` (Object to Place, a state),
  now queued. Done with
  [pilots/campsite_memorial.py](pilots/campsite_memorial.py).
- **Period edges** (D-143). Your criterion: a period's edges are where its
  political structure formally changes, so the Republic ends in 27 BC, not 30
  BC. The dates come from the PeriodO definition that meets it. The Epigraphic
  Database Heidelberg's definitions were accepted and promoted as our claims,
  each linked back to the definition it came from:
  - Roman Republic: 509 BC to 27 BC;
  - Roman Empire: 27 BC to AD 476.

  Doc 24's counted consensus and transition span are dropped. The other
  definitions stay as voices on the card. One problem found on the way:
  PeriodO converts years written the same way inconsistently. ArkeoGIS "-25"
  becomes 25 BC, but INRAP "-509" becomes 510 BC, and the Levantine Ceramics
  and EAMENA years are converted the same way, so some regional definitions
  may be a year off.
- **Year links.** Four older claims had Year links without `as`, including
  the EAMENA and Levantine Ceramics definitions of the Republic. They were
  tethered again by the current rule
  ([migrations/010](migrations/010_label_year_links.py); new operation
  `drop_unlabelled_year_links`). Every Year link now says how it applies.
- **Tests.** Two of the three old failures are fixed:
  - `test_registry_v7`: the fixture lacked the `:Work` label.
  - `test_prompt_version`: source names were hardcoded in reusable code. The
    two Actium Meaning-and-memory pilots moved to
    [pilots/](pilots/__init__.py), where code may name its inquiry. The generic
    view is now [discovery/subject_view.py](discovery/subject_view.py), behind
    the CLI `discovery.event_subject_view`. The evidence report is now
    [discovery/event_evidence_report.py](discovery/event_evidence_report.py),
    which takes the inquiry as an argument; Actium's stopwords moved into
    [inquiries/actium-battle.json](inquiries/actium-battle.json)
    (`leadStopwords`).

- **Fact layer for graph navigation** (D-144): the curator walks the graph
  node by node, and an event showed only its id and label, with its when,
  where and part of hidden behind Assertion nodes.
  [export/fact_layer.py](export/fact_layer.py) now draws 1,887 direct fact
  edges and 189 Year edges, and writes `when`, `where`, `partOf` on 476
  nodes. In the Neo4j browser, hide Assertion, Proposal and Annotation nodes
  for a clean walk; open them to see the voices.

- **Review reasoning, not extraction; Wikidata is a voice** (D-145):
  migration 011 created the Wikidata Work, re-filed 353 open claims resting on
  Wikidata alone as "according to Wikidata", and accepted 434 code-made
  proposals by rule (`python -m GraphRevised.proposals.rule_accept`, which
  harvests now run). The open queue is now reasoning only: passage reader
  1,337, phase agent 442, and 19 others (6 `depictsSameAs` by TD, 4 LC catalog
  claims still in our own voice, 3 Wikidata statements adding evidence to
  claims already accepted, 6 curator-capture drafts).
- **Coverage against "done"** (41 §4): `python -m GraphRevised.discovery.coverage_report
  GraphRevised/inquiries/actium-battle.json [--save]`, read-only, no model calls. One line per
  checklist item, met or not, with the counts behind it.
- **Review desk** (interim, curator's tool only): a local Gradio page,
  `python -m GraphRevised.review_desk.app --entity chr:entity:battle-of-actium --by "<name>"`,
  on http://127.0.0.1:7860. Find an entity, read each claim's quotations and
  passages, accept or reject. Decisions run `proposals/store` (the same checks
  as the review CLI) and rebuild the fact layer in one transaction. The reader
  stack stays Neo4j -> Cytoscape -> React, designed in Figma.

- **End-game plan** (D-146): [41-ENDGAME-PLAN.md](41-ENDGAME-PLAN.md). The
  late Republic first, proved on Actium reaching "done"; ultimately public;
  $50–100 for Actium's model runs. Phase 0 (code) comes first.

## 4. Rules that are easy to break

1. **Paid model calls:** never without explicit authorization covering scope,
   provider sharing, and budget. Every model path now goes through the spend
   meter (`spend_meter.py`, 41 §3.8): a call needs `CHRYSTALLUM_BUDGET` set to a
   budget in `curation/budgets.json`, is refused if its worst case would pass
   the cap, and is logged to `runs/spend-ledger.jsonl`
   (`python -m GraphRevised.spend_meter` reports). The cap is our estimate,
   not a provider-side limit. Budget `actium`: $50 cap (curator set $50–100).
2. **Never show an authority code alone** (QID, PID, LCSH, FAST, LCNAF): show
   the authority's own label with the code beside it. Verify every identifier
   and class at its authority, never from memory. LCC is not used.
3. **Visibility:** agents never accept anything, but nothing they find is
   hidden. Proposed claims and entities appear at once, labelled with their
   status and source. Identity merges and splits are always the curator's.
4. A Proposal holds its evidence on `PROPOSES_EVIDENCE` until it is accepted.
   Rejecting, superseding, and retracting need a reason code.
5. A guarded write that returns zero rows was refused: `run_write` raises
   `RefusedWrite`. When a write tool is added, check what depends on the thing
   it changes (claims, attributions, observations, mentions).
6. **Changing an entity's kind:** use `entity-kind`, never relabel by hand.
   `upsert_entity` refuses a kind not already on the node.
7. **Wikidata identities:** `persist_identity` overwrites an entity's label
   and shortLabel with Wikidata's. To keep our name, pass label and
   shortLabel, or use `entity-identity`.
8. **Reusable code names no source or subject** (`proposals/`, `identity/`,
   `adapters/`, `discovery/`, `slices/`, `export/`, `harvest/`,
   `orchestration/`, `capture/`, `narrative/`). A test enforces it. Code tied
   to one inquiry goes in `pilots/`.
9. A "required" qualifier in the registry means expected: a claim missing one
   stays valid, with a note. A missing date never excludes a claim, but unary
   claims (`occurred`, `born`, `died`) need their time.
10. **Every date tethers to the Year backbone**, and each link says how
    (`as`: during, start, end, earliest, latest). There are no bare date
    properties.
11. `imaginative` is never chosen: it follows from the attributed Work's
    form. Fiction can never support an asserted claim.
12. Attestation is computed in words at read time. Never store a confidence.
13. Periods are discovered, never seeded by hand. A Period's dates are claims
    (24 §2). Its edges are where the political structure formally changes,
    taken from the PeriodO definition that meets that test (D-143). The other
    definitions, Wikidata's included, are attributed voices, never presented
    as a dispute. Check a bound's own wording before trusting PeriodO's
    converted year.
13a. **Wikidata is a voice, never our own statement** (D-145). Code-made
    extractions are accepted by rule; anything an agent reasoned waits for
    the curator. Never accept a passage reading or a phase placement by rule.
13b. **The fact layer is derived** (D-144). Edges marked
    `derived: "fact-layer"` and the node summaries `when`, `where`, `partOf`
    are redrawn from the claims by
    `python -m GraphRevised.export.fact_layer --apply`. Never edit them, and
    never read them as claims. Rerun after reviewing or proposing, or they go
    stale.
13c. **Attestation counts lines of evidence, not authors** (D-148, 42). Every new
    Work needs a `standing` (primary, secondary, tertiary) or it counts as a
    reference work; a modern claim counts only once its `basis` is traced
    (`reports` with a `RESTS_ON` link, or `reconstructs`). Never show a modern
    retelling as a second source.
13d. **Licensed texts** (JSTOR and the like) stay out of git and out of the graph's
    passages: cite by page with short quotations. Check `git status` after a
    curator download.
13e. **Merges are the curator's** (D-152): agents propose with reasons, never on a
    label alone. `merge_unreviewed_entity` handles only code-made duplicates that
    no person has decided on.
14. Prompt edits change the reader's `prompt_version`, which is intended. The
    open predicate requests are shown to lens readings, so the queue is part
    of the prompt too.
15. Editors' notes (and PeriodO's) are never cited as the source's own words.
16. Preserved payloads are hashed as bytes: write them with `write_bytes`.
17. Tests never depend on live graph contents. Live tests run in
    rolled-back transactions.
18. Suggestions pasted from other AIs often arrive in the legacy vocabulary.
    Check them against [02](02-GRAPH-MODEL.md) and [33](33-DECISIONS.md)
    before discussing them.
19. Strip Perplexity signed (`X-Amz`) links from docs before committing.
20. **Shell:** heredocs with `\n` escapes, backslashes, or nested quotes have
    failed here repeatedly. Write edit scripts to a file, or edit directly.

## 5. Waiting for the curator

- **In the review desk:** the 442 phase placements on the Battle of Actium. (The 24
  coin units were accepted 2026-11-18 on the curator's instruction; legion 12's RRC 544/9
  evidence link had lost its time quotation in migration 013 and was repaired from the
  coin's own date line first.)
- **López Sánchez 2010** (INR 5, 123-138; migration 015, secondary, for the curator to
  check; PDF in docs/Actium/, git-ignored): pp. 123-131 read by the military lens
  2026-11-18 ($0.67). Proposed: 7 Questions (coin series as evidence; Imp IIII; a Corcyra
  squadron; Antony's praetorians at Actium; Scarpus's forces; why Scarpus went to
  Cyrenaica; Corcyra as the turning point) and 10 Positions. To check: López Sánchez's
  holdings on the two Scarpus Positions were refused (unknown position), and two p. 129
  quotations ran across the page break; `about` Corcyra is refused (a Place); "Lucius
  Pinarius" is taken to be Pinarius Scarpus. Unresolved holders: Schmitthenner 1958,
  Keppie 2000, Southern 1998. The paper swaps Classica/Lybica twice on p. 130; the
  coins (RRC 544/10, 544/11) settle it.
- **Imp IIII** (2026-11-18, curator's request): RRC 546 (Scarpus's coins of 31 BC)
  harvested as a primary coinage Work, 13 types (legion 8 gains a second voice from
  546/1). Migration 016 proposed the Events "Antony hailed imperator for the fourth
  time" and "Pinarius Scarpus hailed imperator" (participatedIn, from the legends, no
  time: the coin is a date by which), the Question `about` Antony's acclamation, and
  Sear's Position "the occasion ... is unknown" (via López Sánchez p. 126 n. 5; Sear 1998
  unresolved). Reject "Imp IIII victory was earlier and elsewhere than Southern
  proposed" as underspecified. 546/4-8, Scarpus striking for Octavian, are evidence for
  his defection, not yet used.
- **Scarpus's refusal** (2026-11-18): Dio 51.5.6 gives no date and "autumn 31 BC" is a
  modern inference, so no time is stored. Migration 017 proposed the refusal `partOf`
  "Antony follows Cleopatra" (beside the Dio events either side of it) and `triggeredBy`
  "Antony sails to Scarpus" (according to Dio): its place is its order, after the battle
  and before Alexandria. A season needs a modern voice we hold (CAH 10, if acquired).
  Gallus at Paraetonium (30 BC) is a separate episode, not linked.
- **Standings set by Claude, to check:** Lange 2011 (secondary); the Works the
  Wikidata references created (Broughton, Syme, Roller secondary; DPRR,
  Britannica Online, Treccani tertiary).
- **The first historiography Questions** for Actium (44 §5): from Lange, Antony's
  aim and what decided the battle; the lens may propose more.
- **Still pinned:** acquiring the cited sources (Shuckburgh 1917, Eck and Takacs,
  Pelling 1988, Murray and Petsas 1989, Zachos 2003, Orosius, Florus, Horace,
  Suetonius; and the debate's modern works: Kromayer 1899 and 1933, Tarn 1931 and
  1938, Richardson 1937); AI synthesis as a Work (D-149), not built.

- **Pinned (2026-11-13): Velleius 2.84.1 is under-read.** Only its first
  sentence became claims; the comparison of the two sides went into one
  interpretation note. To do: (1) draft the depicted event "deserters go over
  from Antony to Caesar daily (Velleius)" in *Attrition and desertion*; (2)
  queue a predicate request for an interpretive, attributed-only
  `characterizedAs` (a Group, Person or Place described by a source as having
  a quality: ardour, dejection, weakened rowers, ships formidable in
  appearance only); (3) then "the victory was a certainty long before the
  battle" as `ledTo`, once (2) gives it something to point to.

From the review of 2026-11-13 ([README](README.md), "Address first"):

- **Item 2, vetoes:** whether to track the curator's veto rate per agent
  (to be decided).
- **Item 4, backups:** where the second copy lives, and whether a weekly
  scheduled dump is acceptable (to be decided).
- **Item 6, show the result:** Actium in the explorer from live data, in front
  of one real reader (to be decided).
- **Item 7:** 483 events against 97 people (the curator is reviewing it).

Raised and not yet settled:

- **`locatedAt`** (Object to Place): requested 2026-11-13. Once it is in the
  registry, the memorial is located at Octavian's camp at Actium, on Strauss's
  passage.
- **King consort and King of Kings:** possible wrong identities (king consort
  is used in Mark Antony's `heldPosition`). They come up in the next Office
  review.
- **Still open from 39 §10:** adding CIDOC mappings when a predicate is
  created, the lens set, lens notes, and budgets. Review volume is set aside
  for now (sandbox).
- **24 §10:** the period-or-not leads, and where a period applies.
- **Set aside as trivial for now:** renaming the British Museum Work, and
  museum objects as a source (Roman Republican coins through CRRO and Nomisma).
- **Carried from 19 §5** (not blocking):
  - mentions on the passage or on each note's link;
  - identity for Farsala (Pharsalus) and İzmir (Smyrna);
  - the source briefs, to veto;
  - the 30 linked items Wikipedia's first contact left to the agent;
  - the twelve claims the delegated review left open (21 §5);
  - the three PeriodO changes in 24 §9;
  - the root README notice;
  - a `review check` that every accepted claim has evidence;
  - CI for the offline tests.

Settled 2026-11-13: the Campsite Memorial is an Object, and the period edges (D-143) (§3); predicate-request shapes confirmed for now, `informedBy`
included; the Type categories and Polity dates as above; the old Aura instance
deleted (its password in pushed history is dead).

## 6. Tests

Last full run, 2026-11-17, after footnotes, the note reader, the 18-lens catalogue and the
architecture-review fixes: **587 passed** (580 before; 28 minutes this time, against about 9
usually, the machine being busy).

If many live tests fail at once, check that Neo4j is running before reading
the failures: a stopped Neo4j looked like 92 failures on 2026-11-15.

## 7. Next steps

**Start here next session:** all of Lange (pp. 608-623) is read and stored (§3b). Next:
(a) propose the unresolved holders as Works, from Lange's footnotes, and attach the
logged `holds` links; (b) a debate panel in the explorer from the snapshot's `debates`;
(c) the curator's review of the Lange Positions (§3b "To review"). The historiography
steps as planned, for reference:

1. registry v17: kinds `Question` and `Position`; predicates `about`, `answers`,
   `holds` (with stance), `rejects`, `hadReception` (time span, reception value);
2. attestation wording for positions (who held and rejected, when; never
   "well attested") in export/confidence.py;
3. the fact layer and explorer: a Question one hop from its event; a position's
   timeline;
4. a historiography section in the lens prompt, and a dry run on Lange's first
   pages (no model call).

Then, **only with the curator's go-ahead for that run**, the paid Lange reading
under budget `actium`. Before it, optionally fetch the 12 passages Lange cites
from Works we hold (free).

Also open (offered, not chosen): the consistency checks (41 §3.4), the merge
proposer (D-152), the lens run (ancient sources first), resolving the six
Wikidata encyclopedia entries, committing (only when asked).

**Designed, waiting on the curator (2026-11-18): animals, plants, metals and materials**
([45](45-NATURAL-KINDS-AND-MATERIALS.md), D-160). Scope, authorities (GBIF, Getty AAT)
and the first slice (coin metals, then Pliny's purple and the murex) are decided, and
so is the model (45 §6: Types by category, authority hierarchy accepted by rule,
denominations made of their metal, colour as `hadColour`). **Built 2026-11-18:** registry
v18 (synced, graph type re-applied), the Getty AAT harvest (14 Types, 12 parent links
accepted by rule), the coin metals (denominations made of silver and gold, the two series
struck in them, accepted by rule); Pliny's purple (migration 020: five passages, Tyrian
purple from AAT, Tyre, Pliny's purpura and buccinum; three claims for the desk). Registry v19
(colour, `hadColour`, `about` a Type); migration 021: the purple sails at Actium (involved
in, purple, linen) and the Question "which species are Pliny's purpura and buccinum?".
Eight claims for the desk (020, 021); the new role "distinguishing mark" to review. The chrystallum connector must be restarted to word the v18 predicates.

**Queued (curator agreed 2026-11-18, not started): an Obsidian plugin**, after the
review queue and the explorer's graph navigation. Terms:

- read-only, local, against the curator's own Neo4j; database credentials never in the
  plugin (it calls the connector's queries, or a thin local API over them);
- first: hover cards (description, attestation, voices; codes shown with labels) and
  "create note from entity" (frontmatter with the `chr:entity:` id; the plugin refreshes
  only a fenced "from Chrystallum" block, never the curator's text);
- then a sidebar with the current note's entities and their neighbourhood;
- later a path finder showing each step's voices and attestation, with imaginative facts
  marked as such; a plain shortest-path query, not Neo4j's Graph Data Science library;
- not wanted: credits, public writes, automatic promotion. Any expansion makes proposals
  for the desk. The Perplexity design's facets, DPRR ids and decision tables are the
  Aura-era model, not this one.

Older items:

1. Settle the README review items still open (§5), then the **lens
   specialist's dossier** (39 §9, step 2), seeded from the grounding and the
   Actium lens run.
2. **The reasoning-led passage review is unfinished** (from 38). The reader
   supports depicted events, relationships, and unresolved mentions, but the
   integrated review of coverage, graph connections, open questions, and
   overstatement is not built. Do not describe it as delivered. Regression
   case: Plutarch, *Antony* 68.3 (the passage does not say what Caesar's
   messages contained; leave that unknown). Confirm the output contract with
   the curator before building.
3. **Rerun the entity review for Offices** after any Office change.
4. **Objects in the reader are untested on a real source.** `objects` and
   `involvedIn` drafts have offline tests only.
5. The explorer UI's next steps (19 §5 to §7, now history): re-import the
   Figma screens, composite cards, the order of battle's data gaps, the image
   review, and the lens icon licence. Also rotate the MCP token.

## 8. Known gaps

- **The Augustus relabel has no decision record**, because `upsert_entity`
  stores none for a label change. Either record its basis, or give label
  changes a decision trail.
- **Types made later get no category automatically.** `apply_curation` and
  the reader create Types without one. Set it with `set_type_category`, or
  rerun migration 009 for roles.
- **Duplicates:** the Plutarch seven-day holdout has two proposed `occurred`
  claims that differ only in the wording of their time expression
  (`qualifier_signature` uses the unnormalized expression). A paid review
  called them redundant, but that is not a curator decision. Do not merge on
  a label, a shared observation, or matching endpoints (38).
- Persons are proposed from Wikidata only; no reader has read their lives.
- A Wikidata span whose end is known only to its decade is read from the
  decade's outer year, as a definite bound.
- Disputes across claim families (two sources naming different commanders)
  are not detected.
- Depicted events are one source's units until the curator links them with
  `depictsSameAs`.
- `surface` reuses an Entity only through its Wikidata identity.

## 9. Connector

The claude.ai connector (Chrystal MCP) returns 404 while the quick tunnel is
down. Each run of the tunnel gets a new URL
([connector/CONNECTOR.md](connector/CONNECTOR.md)): restart it with `--tunnel`
and paste the new URL into claude.ai's connector settings. Claude Code's own
connector (`.mcp.json`) is unaffected.

## 10. The documents

| Role | Documents |
|---|---|
| **Governing** | [02](02-GRAPH-MODEL.md) meaning and storage; [31](31-ONE-COMMAND.md) behaviour; [29](29-EVENT-CENTRED-INQUIRY.md), [32](32-RESEARCH-WORKSPACE.md), [26](26-UI-DATA-CONTRACT.md); [33](33-DECISIONS.md), the decision register |
| **Descriptive** | [30](30-LOGICAL-MODEL.md) the model in UML; [36](36-DATA-DICTIONARY.md) the data dictionary; [37](37-CANONICAL-EXPORT-REQUIREMENTS.md) export requirements |
| **Draft or decided plans** | [39](39-LENS-SPECIALISTS.md) lens specialists; [41](41-ENDGAME-PLAN.md) end game; [42](42-CORROBORATION-AND-CLAIM-KINDS.md) corroboration (built); [43](43-ACTIUM-MILITARY-FRAME.md) military frame; [44](44-HISTORIOGRAPHY-AND-DEBATES.md) historiography (decided, not built) |
| **Reference** (design reasoning that decisions cite) | 01, 03, 05 to 09, 16, 21 to 25, 27, 28 |
| **Executable** | [10](10-PHASE-1-SCHEMA.cypher), [13](13-PHASE-3-DIRECT-OPERATIONS.cypher) (the operations), [34](34-ENTITY-SUBTYPE-MIGRATION.cypher) |
| **History** (as of their date; do not act on them) | 00 (the Phase 0 snapshot), 04, 11, 12, 14, 15, 17, 18, [19](19-SESSION-HANDOFF.md), 20, 35, [38](38-REASONING-SESSION-HANDOFF.md), [40](40-LENS-SESSION-HANDOFF.md) |
