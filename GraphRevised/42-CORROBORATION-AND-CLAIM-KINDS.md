---
status: decided 2026-11-15 (D-148); built: standing, basis, line counting; rests-on proposals still to build
authority: 41-ENDGAME-PLAN.md §3.1 and §3.2 (D-146)
depends_on: [25-LIVES-AND-PLAYGROUND.md, 26-UI-DATA-CONTRACT.md, 41-ENDGAME-PLAN.md]
superseded_by: null
last_reviewed: 2026-11-14
---

# 42 — Independent Corroboration and What a Modern Claim Is Doing

## 1. The problem, measured

Attestation today ([export/confidence.py](export/confidence.py)) counts
**authors**: a fact with two or more distinct authors behind it is "well
attested". A modern book that retells Plutarch counts as a second author.

Measured on the graph (2026-11-14), the live factual claims that cite a
source:

|                                                 | Facts  |
| ----------------------------------------------- | ------ |
| Shown as "well attested" today                  | **33** |
| backed by two or more ancient sources           | 8      |
| backed by one ancient source, plus modern works | 17     |
| backed by modern or reference works only        | 8      |

For a public graph that researchers rely on, 25 of the 33 overstate the
evidence. Plutarch plus three books retelling him is one witness, not four.

## 2. Three kinds of Work (a property of the Work)

| Stored `standing` | Shown as | Examples in the graph |
|---|---|---|
| `primary` | ancient source | Plutarch, Cassius Dio, Velleius, Strabo, Res Gestae, Virgil (still imaginative) |
| `secondary` | modern study | Weigall, Hale, Strauss |
| `tertiary` | reference work | Wikipedia, Wikidata, LCSH, the period gazetteers |

The rule: a Work is primary when it was written in the period or by an
ancient author drawing on what is now lost. Code proposes the standing from a
composition date (a new `composed` year on the Work, from Wikidata's inception
or the LC record), accepted by rule (D-145) when the date settles it; the
curator settles anything borderline (a late-antique epitome, a Byzantine
excerpt of Dio).

## 3. What a modern claim is doing (a property of the claim)

Every live claim attributed to a secondary or tertiary Work gets a `basis`:

| `basis` | Meaning | Adds an independent line of evidence? |
|---|---|---|
| `reports` | retells an ancient source; carries a **rests-on** link to it | no: it counts as the source it rests on |
| `reconstructs` | the author's own argument where the sources are silent or unclear (a date, a site, a number) | yes, labelled as a modern reconstruction |
| `unknown` | not yet traced (the default for every existing claim) | no |

Interpretation stays the existing category (`interpretive`), unchanged.
Disagreement between scholars is already detected when values differ
(`disputed`); an explicit "X disputes Y" link is left for later. (Drafted 2026-11-15 in [44](44-HISTORIOGRAPHY-AND-DEBATES.md): Questions, Positions, and the Works that hold or reject them.)

**Rests-on** is a link from the modern claim to what it retells: the ancient
source's own claim where we have it, else the ancient Work ("per Plutarch",
no passage in the graph yet). A rests-on link is agent or curator reasoning,
so it is proposed and reviewed like any claim (D-145), with the modern
passage quoted as evidence.

Ancient sources can depend on each other too (Plutarch and Dio may share a
lost source). The same rests-on link can record it, but only when the
curator enters it; nothing infers it.

## 4. Attestation, counted by lines of evidence

A **line of evidence** is a primary source, or a modern reconstruction.
Reports join the line they rest on; `unknown` and tertiary claims add none.

| Words shown | When |
|---|---|
| well attested (2 ancient sources) | two or more independent primary lines |
| attested (1 ancient source) | one primary line |
| a modern reconstruction (Strauss) | no primary line; one or more reconstructions |
| modern sources only (3 works, not traced) | secondary claims with `unknown` basis only |
| reference only (Wikidata) | tertiary claims only |
| disputed (…) | unchanged: members state the same qualifier differently |

The modern works are never hidden: a suffix lists them ("attested (1 ancient
source); retold by Weigall, Hale"). The reader UI shows the line structure
in the side panel: each ancient passage as a card, with the modern works
that retell it nested under it, footnote style.

**Built 2026-11-15** (migration 012): every Work has a standing (15 primary,
5 secondary, 36 tertiary; Claude's first classification, **confirmed by the
curator 2026-11-15**, `standingConfirmedBy` on each Work), and 1,180 modern and reference claims start
`unknown`. Over all facts, including our own claims backed by ancient
passages: 16 well attested, 649 attested (1 ancient source), 768 modern
sources only, 575 reference only. A Work added later counts as reference
until it is given a standing.

## 5. How the links get filled

1. **Work standing:** code, from composition dates; about 20 Works, the rest by
   the curator. No model cost.
2. **Rests-on from the text:** when a modern passage names its source ("Plutarch
   says…", "according to Dio…"), the passage reader proposes the link to the
   matching ancient claim. The curator reviews it in the review desk.
3. **Rests-on from Wikipedia footnotes (built 2026-11-15, D-150):** `python -m
   GraphRevised.harvest.wikipedia_footnotes <Wikipedia Work id> [--apply]` follows the footnote after
   each quotation to the ancient passage it cites; on the Actium article, 155 links on 23 claims
   (15 facts moved from reference only to attested). A reference work's retelling joins the ancient
   line it rests on, as a modern study's does.
4. **Rests-on from book footnotes:** the curator's Obsidian notes carry the book's
   footnotes; a cited ancient locator matched to a passage in the graph is
   proposed the same way.
5. **Reconstruction:** the reader marks a modern claim `reconstructs` only
   when the passage argues it ("the date must therefore be…"); reviewed.
6. Anything left stays `unknown`, and is shown as "not traced", never counted.

## 6. What changes in the code

- Work: `standing`, `composed` (data dictionary rows).
- Assertion: `basis` (attributed claims from secondary and tertiary Works).
- New relation: Assertion `RESTS_ON` Assertion or Work, carried by a reviewed
  Proposal.
- `confidence.py`: count lines, not authors; new wording (26 UI contract).
- Passage reader: a rests-on and basis field in its output for secondary Works.
- Review desk: show the rests-on link as reasoning to check.
- A migration: standing for existing Works; every existing modern claim
  starts `unknown`.

## 7. Decisions for the curator

1. The three standings and their names (primary / secondary / tertiary,
   shown as ancient source / modern study / reference work).
2. `unknown` modern claims do not count toward attestation until traced.
3. Wikidata and Wikipedia are tertiary: they never add a line on their own.
4. Ancient-on-ancient dependence only when the curator enters it.
5. The wording in §4.
