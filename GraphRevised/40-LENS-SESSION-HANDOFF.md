---
status: history
authority: none; decisions remain in 33-DECISIONS.md (D-137 to D-140)
superseded_by: CURRENT-STATE.md
last_reviewed: 2026-11-12
---

# Session handoff: lens specialists, event roles, entity review (2026-11-12)

**History.** This handoff is superseded by [CURRENT-STATE.md](CURRENT-STATE.md) (2026-11-13), which carries what is still open. Read this one only for the record of its session.

## Start here

Read [39-LENS-SPECIALISTS.md](39-LENS-SPECIALISTS.md) first. §9 is the build
order and §10 lists the open questions, including what this session settled.
The decisions are D-137 to D-140 in [33](33-DECISIONS.md). Every graph write
below went to the live local Neo4j (`neo4j://127.0.0.1:7687`) through the
guarded operations. **Nothing from this session is committed.** Commit only
when the curator asks, and keep the curator's Obsidian highlights and
`.obsidian/` out of commits.

Set the password without printing it:

```bash
export NEO4J_PASSWORD=$(python -c 'from GraphRevised.connector.server import neo4j_password as p; print(p())' 2>/dev/null)
```

**First:** the curator's review of 2026-11-13, in the
[README](README.md) section "Address first". It puts review volume, the
unfinished items, and backups ahead of new building.

**Next build step (39 §9, step 2):** build the lens specialist's dossier, seeded
from the grounding and the Actium lens run. Before that, or alongside it,
the curator has three items to settle (see "Waiting for the curator").

## Graph state (counted 2026-11-12, end of session)

- **729 Entities:** Event 483, Person 97, Work 55, Place 25, Type 23, Group 19,
  Office 18, Concept 3, Period 3, Polity 3. The graph has no Objects yet.
- **2,187 Assertions:** proposed 2,098, accepted 79, superseded 8, rejected 2.
- **48 guarded operations.** This session added `set_entity_kind` and
  `retire_entity_identity` ([13](13-PHASE-3-DIRECT-OPERATIONS.cypher),
  [operations.py](operations.py)).
- **Predicate registry v14** ([proposals/predicates.v14.json](proposals/predicates.v14.json)).

## What this session built

1. **Lens specialists return** (D-137). See 39, with the lens reader, the
   predicate-needs queue, and lens readings that draft depicted events (39 §9,
   steps 1 to 1b).
2. **Predicate or event** (D-138). An act is a depicted event; a state between
   two entities is a predicate. All 30 predicate requests carry a shape
   ([curation/predicate-needs.json](curation/predicate-needs.json)).
3. **Event roles** (D-139). There are 22 provisional role Types
   (`chr:entity:role-*`), ten of them linked to Wikidata, defined in
   [curation/event-roles.json](curation/event-roles.json) (an approved
   apply_curation manifest).
   - Registry v14 adds `involvedIn` (Object to Event, with a role such as
     seized).
   - The passage reader drafts `objects` beside the participants, and each
     becomes an `involvedIn` claim. Every inquiry that may depict events has
     the roles in scope, with the curator's aliases.
   - `informedBy` (Work to Person; Plutarch's great-grandfather Nicarchus,
     *Antony* 68.4) is a queued state request, not yet a predicate.
4. **Entity review** (D-140).
   [discovery/entity_review.py](discovery/entity_review.py) is read-only and
   needs `--authorize-sharing` to call the model; `--prepare-only` runs
   offline. Its first full run is
   [queues/entity-review-20261112.json](queues/entity-review-20261112.json):
   256 entities, 250 ok, about 205k input tokens. New review commands go with
   it: `entity-kind` and `entity-identity` (see
   [proposals/review.py](proposals/review.py) docstring).
5. **Corrections applied with the curator's approval:**
   - **matrona:**
     - The claim that Fulvia held the position of matrona is rejected as
       malformed.
     - Matrona is now a Type, not an Office.
   - **consul and Master of the Horse:** both deprecated, because they were
     wrong Wikidata identities. Each basis names the right entity, Roman
     consul or magister equitum.
     - New mentions point at the right entities.
     - Wikipedia's own link mentions are kept.
   - **The Augustus title:** relabelled "Augustus (title)". This change has
     **no decision record**, because `upsert_entity` stores none.
   - **Tarentum:** now linked to Taras (the port city, Pleiades 442810). The
     link to the precinct in the Campus Martius is kept as rejected history.
   - **British Museum:** moved to Group by mistake, then restored to Work. It
     is the museum's thesaurus, the source PeriodO cites, and a claim cites
     it.

## Waiting for the curator

- **Campsite Memorial of Augustus:** Place (the site) or Object (the monument)?
- **King consort and King of Kings:** the entity audit raised them: king
  consort is a possible wrong identity (it is used for Mark Antony's
  `heldPosition`), and King of Kings is unsure. They come up again in the
  next Office review.
- **Predicate-request shapes:** confirm them, including `informedBy`.
  Claude proposed them.
- **Still open from 39 §10:** review volume (flagging by rule), adding CIDOC
  mappings when a predicate is created, the lens set, lens notes, and
  budgets.
- **Raised 2026-11-13, not yet answered:**
  - **Type (D-039):** set `typeCategory` on every Type (role, unit type,
    pattern, power, status), add status as a category, and queue a
    `hadStatus` request with Fulvia the matrona as evidence (Claude's
    recommendation).
  - **Polities (D-040):** none of the three is dated. Propose their dates
    from Wikidata's inception and dissolution, attributed to Wikidata?
  - **Periods (D-040):** put the period survey's consensus for the Republic
    and the Empire to the curator now? No Period has a consensus claim yet.
  - **Year links:** two old period definitions (EAMENA, Levantine Ceramics)
    link every Year without the start, end, or during label. A small
    migration would fix them.
  - **24 §10:** the period-or-not leads and where a period applies, both
    proposed from the archived February period files.
- **Old Aura credentials, settled 2026-11-13:** the instance is deleted
  (curator), so the password still in pushed history is dead.
  `Temporal/Neo4j-f7b612a3-Created-2026-02-19.txt` is untracked (the removal
  is staged) and ignored by `.gitignore`. The local copy is kept.
- **Set aside as trivial for now (curator):**
  - renaming the British Museum Work;
  - museum objects as a source: Roman Republican coins through CRRO and
    Nomisma, with British Museum numbers as one ID system.

## Rules that are easy to break

- **Paid model calls:** never run one without explicit authorization
  covering scope, sharing, and budget.
- **Authority codes:** never show a Wikidata, LCSH, or FAST code without its
  label, and verify identifiers at the authority.
- **Changing an entity's kind:** use `entity-kind`, never relabel by hand.
  `upsert_entity` refuses a kind not already on the node.
- **Wikidata identities:** `persist_identity` overwrites an entity's label
  and shortLabel with Wikidata's. To keep our name, pass label and
  shortLabel, or use `entity-identity`.
- **Required qualifiers:** a "required" qualifier in the registry means
  expected. A claim missing one stays valid, with a note.
- **Prompt versions:** prompt edits change the reader's `prompt_version`.
  That is intended.

## Tests

The last full suite run, before the two new operations, had 438 tests and 3
known failures, all from before this session:

- `test_registry_v7` live: `set_work_form` is refused.
- `test_cytoscape_export`: the curator's work in progress.
- `test_prompt_version`: "Actium" is hardcoded in
  `adapters/commons_images.py`.

Since then these pass: `test_entity_kind_live` (5), `test_entity_identity_live`
(2), and `test_entity_review` (5). Rerun the full suite before committing.

## Known gaps (to do, not waiting on the curator)

- **The Augustus relabel has no decision record.** Either record its basis,
  or give `upsert_entity` label changes a decision trail.
- **Objects in the reader are untested on a real source.** `objects` and
  `involvedIn` drafts have offline tests only; no reader run has used them
  yet.
- **Three tests fail, all from before this session** (see Tests).
  `test_prompt_version` needs "Actium" removed from
  `adapters/commons_images.py`. `test_registry_v7` needs its
  `set_work_form` refusal looked into. `test_cytoscape_export` waits on the
  curator's work in progress.
- **Reruns of the entity review:** run it for Offices after any Office
  change. King consort and King of Kings will come up then.
- **Open lists from earlier sessions still stand:**
  - [38](38-REASONING-SESSION-HANDOFF.md): the reasoning-led passage review
    is unfinished.
  - [19](19-SESSION-HANDOFF.md) §5 to §7: the explorer UI next steps,
    rotating the MCP token, and the known gaps.

## Not working at session end

The claude.ai connector for the graph (Chrystal MCP) returned 404. The quick
tunnel gives a new URL each run
([connector/CONNECTOR.md](connector/CONNECTOR.md)). Restart it with
`--tunnel` and paste the new URL into claude.ai's connector settings.
Claude Code's own connector (`.mcp.json`) is unaffected.
