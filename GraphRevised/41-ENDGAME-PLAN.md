---
status: draft
authority: D-146 (33-DECISIONS.md); this document holds the plan and its reasoning
depends_on: [25-LIVES-AND-PLAYGROUND.md, 29-EVENT-CENTRED-INQUIRY.md, 31-ONE-COMMAND.md, 37-CANONICAL-EXPORT-REQUIREMENTS.md, 39-LENS-SPECIALISTS.md, CURRENT-STATE.md]
superseded_by: null
last_reviewed: 2026-11-13
---

# 41 — End-Game Plan: the Late Republic, proved on Actium

**Date:** 2026-11-13. **From:** the curator's answers on the end game, and a
review of [Approach.md](Approach.md) (a discussion with an agent that did not
know the schema) against what the graph already does.

## 1. The goal (curator, 2026-11-13)

| Question | Answer |
|---|---|
| Target | **The late Republic first**: 133 BC (the Gracchi) to 27 BC (the Republic's end, D-143), the common textbook scheme (curator, confirmed). The whole Republic follows. |
| Proof point | **Actium reaches "done"** (§4) before anything scales. |
| Audience | **Ultimately public**, for researchers, institutions and museums. |
| Model budget | **$50 to $100 for Actium.** Later phases get their own budget, set from what Actium actually cost. |

A public audience of researchers and institutions raises three bars that a
private sandbox does not: every statement must be traceable to its evidence,
corroboration must not be inflated, and anything shown must be safe to show.
Gaps 3.1, 3.2 and 3.7 below follow from that.

## 2. What already holds (no change)

Approach.md's main recommendations are already in the schema under other
names: all three seed approaches run together (people first D-030, events by
inquiry 29, texts by the passage reader); every claim cites a verbatim
quotation with a locator; voices are kept, never merged, and attestation is
computed in words; interpretations are their own category, attributed only
(D-021); creative Works make claims imaginative; lenses are standing
specialists, never nodes (D-039, D-137), whose questions can be answered,
thin, contested or open; lens grounding per polity is the structural layer;
the Location backbone (Pleiades and GeoNames) is loaded; Wikidata is a voice,
and code-made extractions are accepted by rule (D-145); the curator reviews
reasoning, not extraction.

Turned down from Approach.md: new `Passage` and `Lens` nodes (passages are
SourceObservations with Annotations; lenses are never nodes), a 25-word
quotation cap and a per-book passage ceiling (the curator: reasonably sized
quotations are fine; the 1,500-character cap and `visibility` cover it),
reader "resonance" votes (no users yet), and adopting 18 lenses at once
(lenses grow as specialists need them; religion first, §3.6).

## 3. Gaps to close

### 3.1 Independent corroboration (public bar)

Today a modern author who restates an ancient one counts as a second author
([export/confidence.py](export/confidence.py) says so). For a public graph
that inflates attestation: Plutarch plus three books repeating him is one
chain of evidence, not four. Needed: a link from a modern claim to the
ancient passage it rests on, and attestation that counts **independent
chains**, not authors.

### 3.2 What a modern claim is doing (public bar)

A modern work *reports* an ancient source, *reconstructs* (a date, a site, a
number the sources lack), *interprets* (cause, significance), or *disputes*
another scholar. Only reconstruction and interpretation add a voice of their
own; a report adds nothing new and must point back (3.1). We distinguish
only factual and interpretive today.

### 3.3 Evidence that is not text

Coins, inscriptions, excavation and survey reports. A passage observation
cannot hold a coin type or a find. Needed: evidence kinds beyond passage,
transcription, record and image, each with its own required fields.

### 3.4 Consistency checks

Cheap code over the people and the Year backbone: nobody acts after their
death or before their birth, nobody holds two incompatible offices in one
year, nobody is in two distant places in one moment. Violations go to the
curator as reasoning to check (an identity merged wrongly, a date misread).

### 3.5 The late-Republic spine from structured sources

Persons and offices year by year from the Fasti, through **DPRR** (Digital
Prosopography of the Roman Republic; curator's choice, built on Broughton), seeded by code like
Wikidata and accepted by rule (D-145). Places are already backed by
Pleiades. This gives every agent a period-correct frame (who was consul,
what office existed) before it reads, and costs almost no model calls. The
legacy system had DPRR; GraphRevised does not yet.

### 3.6 Lenses grown as needed

Six lenses exist (general, military, political, economic, social,
religious). Religion is cross-cutting in the Republic (auspices on political
acts, vows on campaign): the religious specialist's grounding comes early. New
lenses (diplomatic, legal, logistical, kinship) are added when a specialist's
open questions need them, not in advance.

### 3.7 Safe to publish

Quotation visibility by Work and edition (copyright differs between a Greek
text and a modern translation of it); citations built from the Work, its
catalog record and the locator (the footnote work, pinned); a canonical export
(37) with stable identifiers and permalinks that institutions can cite;
backups (open since the handoff). **Formats (curator):** the export maps to
**CIDOC CRM** (the museum reference model; Linked Art is a profile of it),
and types, places and people cross-reference the **Getty** vocabularies (AAT
for types, TGN for places, ULAN for modern authors and artists) alongside
Wikidata, Pleiades and LC.

### 3.8 A spend meter

The model-enabled paths have no spending cap (CURRENT-STATE rule 1). Before
the Actium budget is spent, every model run records its tokens and cost, and
a run stops at a stated cap. **Built 2026-11-14:** `spend_meter.py`, the
budgets in `curation/budgets.json` (`actium`, $50 cap to start), the ledger in
`runs/spend-ledger.jsonl`.

## 4. When an event is "done"

Drafted for the curator to confirm, Actium first:

1. **Who, what, where, when** each have at least one accepted claim, or an
   accepted "nothing attested" for that question.
2. **Every core source has been read through**: each assigned passage is
   read by the general reader and by each applicable lens specialist, and
   the run log shows it.
3. **Every lens question** for the event is marked answered, thin, contested
   or open, with the claims it rests on; none is unmarked.
4. **The phase spine is reviewed**: every phase placement (our own voice) is
   accepted or rejected.
5. **Why** is recorded as voices (interpretive claims and passages of note),
   never as one answer.
6. **No consistency check fails** (3.4), or each failure is explained.
7. **Corroboration is independent** (3.1) for every claim shown as well
   attested.

## 5. Phases

| Phase | What | Model cost |
|---|---|---|
| **0. Foundations** | 3.8 spend meter; 3.1 and 3.2 claim kinds and rests-on links; 3.4 consistency checks; §4 "done" as a coverage report on the event; the pinned items (Velleius, footnotes) | none (code) |
| **1. Actium to done** | Lens specialists read Actium's core passages; the curator reviews reasoning in the review desk (phase placements first); gaps go back to the specialists as open questions. Record cost per passage and per event. | **$50–100** |
| **2. Late-Republic spine** | 3.5 Fasti through DPRR; offices and Polities with period-correct structure; consistency checks run over it | near none (code, accepted by rule) |
| **3. Late-Republic events** | Inquiries over the period's events, people first, sized from phase 1's measured cost; lenses added as needed (3.6) | budget set after phase 1 |
| **4. Public release** | 3.3 non-text evidence; 3.7 publication safety; the reader UI (Neo4j → Cytoscape → React, designed in Figma); the canonical export | none to modest |

Phase 0 comes first because 3.1 and 3.2 change how claims are counted: easier
to build before thousands more claims exist than to backfill after.

## 6. What stays the curator's

Reviewing agent reasoning (D-145); boundaries by stated criteria (D-143);
identity merges and splits; the budget for each phase after Actium;
confirming new predicates and lenses; what is published.

## 7. Risks

- **Identity.** Namesakes are common (three Fulvias, three Antonias, two Lucii
  Antonii in the graph, each with its own Wikidata item). A merge is the
  curator's decision on an agent's proposal (curator, 2026-11-15): an agent
  proposes merges with its reasons, never by label alone, and nothing merges
  without review. Not built yet.
- **Review volume.** About 1,800 reasoned proposals are open for Actium alone.
  The late Republic is far larger. Mitigations: the rule for code-made
  extractions (D-145), review by phase in the review desk, and specialists
  that reuse existing events rather than duplicating them (39 §9 item 1b).
- **Cost drift.** Opus-class runs or full rereads multiply cost. Mitigated by
  the spend meter (3.8) and the default reader model.
- **Source bias.** The late Republic is told largely by Augustan-era and
  later writers. Voices and stances must stay visible, never smoothed.

## 8. First steps

1. Build the spend meter (3.8).
2. Draft the claim kinds and rests-on design (3.1, 3.2) for the curator: [42](42-CORROBORATION-AND-CLAIM-KINDS.md) (draft, 2026-11-14).
3. Build the coverage report for "done" (§4), and run it on Actium to see the
   distance to go. **Built 2026-11-15:** `python -m GraphRevised.discovery.coverage_report
   GraphRevised/inquiries/actium-battle.json [--save]`. Actium: items 1, 5, 7 met; 2 (no lens
   specialist has read a passage), 3 (one general question unmarked; analysis of 2026-10-21),
   4 (442 phase placements open) not met; 6 not built.
4. Then spend the Actium budget against the coverage report's gaps.

## 9. Curator's answers (2026-11-13)

1. **Start year:** 133 BC (the Gracchi), to 27 BC.
2. **"Done" checklist (§4):** not yet amended; treated as the working
   definition until the curator changes it.
3. **Spine:** DPRR.
4. **Public formats:** CIDOC CRM and the Getty vocabularies (AAT, TGN, ULAN).
