# 29 — Event-Centred Inquiry and Chrystallum's Account

**Date:** 2026-10-15. **Status:** decisions agreed with the curator (§2); the
design below is proposed, nothing is built.
**Changes:** [25](25-LIVES-AND-PLAYGROUND.md) §7 rule "from the graph only"
(§4 here), the legacy lesson "Wikipedia is orientation only"
([16](16-LEGACY-TRIAGE.md), biographic row; §5 here), and the order of next
steps in [19](19-SESSION-HANDOFF.md) §6 (§9 here).
**Builds on:** 25 §13 (agents choose the sources), [26](26-UI-DATA-CONTRACT.md)
§4 (signposts) and §5 (narrative), [28](28-SUBJECT-BUCKETS.md) (buckets),
[docs/Agent resources.md](docs/Agent%20resources.md) (the seed list), and two
Perplexity documents: [Weaving Neo4j Work Annotations into an Actium
Narrative](docs/Weaving%20Neo4j%20Work%20Annotations%20into%20an%20Actium%20Narrative.md)
and [Perplexity Session on Architecture](docs/Perplexity%20Session%20on%20Architecture.md).

## 1. Why

The graph has been driven by works. Every inquiry names one Work (Plutarch's
*Antony*, Dio 50–51, Hale, Weigall), its guidance is written for that Work,
and the battle is what is left when the four are put side by side. That was
the right way to test the reader one source at a time. It is not how a user
meets history: they start from the battle.

The curator (2026-10-15): with the Battle of Actium on the centre stage, the
user should also see an **agent-generated account** of it, well written, that
references the works properly, built from Wikipedia and from as many sources
as the agent finds on its own.

## 2. Decisions (curator, 2026-10-15)

1. **The event is the inquiry.** An inquiry names an event (later a person or
   a subject), not a Work. The agent gathers the works for it.
2. **Chrystallum's account sits on the stage beside the event**: a narrative
   written by the agent, labelled as ours, every statement citing a passage.
3. **Wikipedia is a starting point**: for the agent, to surface the high-level
   people, places, and events; for the user, as a link from the event's card
   to its Wikipedia article.
4. **Facets are lens steps in the drill-down path**, never stored nodes (as
   decided in 25 §12). The breadcrumbs may read "Roman Republic › Military ›
   Civil War › Battle of Actium", where "Military" is the lens the user chose.
   A node reachable through several lenses (a civil war is political and
   military) belongs to none of them.
5. **Order:** the event-centred research run comes after the gazetteer and
   before the subject buckets (§9).

## 3. The research run for an event

```text
Event (Battle of Actium)
  1. first contact     Wikidata harvest (exists) + the Wikipedia article
  2. surface entities  people, places, events, offices, groups: proposed, visible at once
  3. source plan       the registry's seed sources + the agent's own discovery
  4. preserve          each chosen source fetched, hashed, rights recorded
  5. read              the reader on each source, with the event as the inquiry
  6. account           Chrystallum's account, citing what was preserved and read
```

1. **First contact.** The Wikidata harvest already exists
   ([harvest/](harvest)). New: the event's Wikipedia article, found through
   the Wikidata record's sitelink (the preserved record of Q160387 already
   lists the English article *Battle of Actium* among 66), fetched at a fixed
   revision and preserved with its hash and licence like any source.
2. **Surfacing entities from Wikipedia.** The article's internal links name
   Wikipedia pages; each page resolves to a Wikidata item through its
   sitelink, deterministically and without a model. Those items then go
   through the existing harvest rules: kind from the checked class table,
   noise dropped by rule, proposed and visible at once, within the budget
   (the one-hop rule, 25 §11). Prose without a link surfaces nothing by this
   route; the reader handles it in step 5.
3. **Source plan for the event.** The existing plan
   ([discovery/source_plan.py](discovery/source_plan.py)) takes the event,
   not a Work. Candidates come from: the source registry (§6), citations in
   the Wikipedia article's references and in passages already read, Wikidata
   "described by source", catalogues (Scaife, Gutenberg, LacusCurtius), and
   the agent's own search. The agent chooses within a budget and records why
   (25 §13).
4. **Preserve.** Only a fetched, preserved, hashed document can be evidence;
   a search result or a model's answer never is (model-choice response,
   amendment 1).
5. **Read.** The reader runs on each source with the event as its inquiry,
   locating the relevant passages itself (whole works, 18 §20).
6. **The account** (§4).

## 4. Chrystallum's account

- **Citation rule.** Every statement in the account cites a passage the
  system has preserved, by its locator. Nothing is cited from the model's
  memory or from a search result. A statement that no preserved passage
  supports is left out, or appears as a signpost ("not yet read: …", 25 §7
  rule 6).
- **This replaces "from the graph only"** (25 §7). The account may draw on
  passages the reader has not turned into claims, so it can be richer than
  the claims; but the run also proposes the claims and notes it finds (step
  5), so the story and the graph stay in step.
- **A voice, labelled as ours.** Shown as "Chrystallum's account", beside the
  sources' own voices, never as fact. It records the model, the prompt
  version, the date, and the sources it used.
- **Not a witness.** It is never counted as an author in attestation
  ([export/confidence.py](export/confidence.py)): it restates its sources, so
  counting it would let the agent corroborate what it summarised.
- **Rules from the persona test carry over** (25 §7): quote sources, never
  the reader's summaries; state flatly only what the sources agree on,
  otherwise name who says it; disagreement is the hook.
- **Personas** change the telling, not the sources (26 §5).

## 5. Wikipedia's three roles

| Role | What | Rule |
|---|---|---|
| Link for the user | "Read on Wikipedia" on the event's card | From the Wikidata sitelink already preserved; no new data |
| Discovery | Its links surface entities (§3 step 2); its references are candidate sources (§3 step 3) | Deterministic link-to-QID resolution; the harvest rules decide kind and noise |
| Evidence | A tertiary voice, "according to Wikipedia", at a fixed revision | A Work of form encyclopedia; preserved and hashed; its licence (CC BY-SA) recorded from the page itself; counts as one author, like Wikidata |

This revises the legacy lesson "Wikipedia is orientation only"
([16](16-LEGACY-TRIAGE.md)): orientation and discovery remain its main use;
as evidence it is one labelled voice, never a substitute for the sources it
cites.

## 6. The source registry and source statuses

From the review of the agent resources and the Perplexity session:

- **A registry file** (`curation/sources.json`, name to settle) as the
  machine-readable companion to [docs/Agent resources.md](docs/Agent%20resources.md):
  per source system, what it covers (polities, periods, languages, lenses),
  how to discover and fetch from it, the identifier scheme, the rights policy
  as stated by the source itself and when it was checked, limitations, and
  the adapter that reads it. The systems already read (Perseus/Scaife,
  LacusCurtius, Gutenberg) are its first entries; others are added after
  their licence is checked at the source (handoff rule 17).
- **A starting point, not a whitelist.** The agent consults the registry
  first and may propose sources beyond it; discovery is not acceptance. A
  governing paragraph to this effect goes at the head of the resources
  document.
- **Separate statuses, in words, instead of one "confidence"** on a plan
  candidate: *found* (proposed by the agent), *identified* (the work
  confirmed at a catalogue), *located* (a copy found, its rights recorded),
  *chosen* (with the agent's reason), *read*, and the claims' own review
  after that. The model's own certainty stays a note, never a status.
- **Work, edition, and copy** are separate fields in the plan, since one work
  may sit on Perseus, LacusCurtius, Gutenberg, and Internet Archive. Edition
  nodes in the graph still wait for a work read in two editions (the Review
  response).
- Candidates stay in the plan file (workflow state is not graph data, 02); a
  chosen source becomes a proposed Work entity, as the period survey already
  does.

## 7. Domain rules out of the inquiries

Each inquiry restates what `commanded`, `heldAuthorityOver`, and
`participatedIn` mean in practice (presence versus preparation, a wing versus
the fleet). Those rules belong once, in shared data beside the predicate
registry, so they cannot drift between inquiries; an inquiry keeps only what
is particular to its event or source. With event inquiries this becomes
necessary rather than tidy: one inquiry will read many works.

## 8. On the stage

- **Centre:** the event, Chrystallum's account beside it, the facts around it
  (shape 2), styled by status.
- **Signposts** (26 §4) such as *Participants (14)*, *Commands*, *Places*,
  *Sources*: computed from claims, not stored. Selecting *Participants* puts
  every participant around the battle on the stage, each line with its
  voices.
- **Drill-down** from the top: subject buckets (28) for Ancient History,
  Roman periods, the Roman Republic, the civil war; lens steps where the user
  chooses one; then the event. The curator's sketch of 2026-10-15 is the
  intended path.
- The notes stage (26 §4a) for any node on the stage.

## 9. Order (curator, 2026-10-15)

1. The gazetteer ([27](27-GAZETTEER.md)), as planned.
2. **The event-centred research run** for the Battle of Actium: the registry
   (§6), Wikipedia first contact (§3 steps 1–2), the event source plan,
   then the account.
3. The subject buckets ([28](28-SUBJECT-BUCKETS.md)).
4. Then the remaining steps in [19](19-SESSION-HANDOFF.md) §6 (Polybius 6,
   notes that stand in for claims, Hannibal).

## 9a. As built (2026-10-15)

Step 5 of §3 runs event-first for the Battle of Actium: one inquiry,
[inquiries/actium-battle.json](inquiries/actium-battle.json), with four sources
(`sources`, each with its `voice` and its own guidance; the shared guidance once),
read with depicted events ([23](23-NARRATIVE-AND-NOTES.md), pilot). The reader
takes `--source` and `--chapters`; a dry run keeps a source in one rolled-back
transaction. Not built yet: the registry file (§6), Wikipedia first contact
(§3 steps 1–2), the event source plan, the account (§4), and moving the domain
rules out of the inquiry (§7: the battle inquiry already holds them once for all
four sources).

The spine test (2026-10-15, before this run) found phases 4–8 present only as
"took part" claims and phases 1–3 and 9 only as notes. After it, Dio's chapters
give the council, the plan, and the burning of the ships as events, and all four
sources give the flight, pursuit, and surrender as ordered events.

## 10. Open

1. **Stored or generated?** Whether the account is kept as a versioned
   artifact (a file outside the graph with its citations, regenerated when
   the sources change) or written fresh for each viewing. Recommended: kept,
   because the research behind it is costly and its citations must be
   reviewable.
2. **The event's phases.** The Weaving document proposes a spine of nine
   phases for Actium (isolation, attrition, the council, deployment,
   engagement, the squadron's breakout, Antony following, the fleet's
   defeat, the army's surrender). Whether these become our own asserted
   sub-events of the battle, approved by the curator, with each source's
   depicted events (23 §2) linked to them.
3. **Mentions** (the words in a passage that refer to an entity): on the
   passage, with their own status, or on each note's link (26 §4a, `mentions`).
4. **Nested attribution**: "Plutarch reports that Octavian wrote that 300
   ships were captured" cannot be said in the model yet.
5. **A source that contradicts a claim** (backlog E8, stance on the evidence
   link) becomes pressing once one inquiry reads many works.
