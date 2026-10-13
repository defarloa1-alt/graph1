# 25 — Lives First, and a Playground for Exploration

**Date:** 2026-10-13. **Status:** agreed with the curator; nothing in it is built yet.
**Changes the plan in:** [24-PERIODS-AND-TRANSFORMATION.md](24-PERIODS-AND-TRANSFORMATION.md) §7 (the transformation pilot waits) and the review rule in [19-SESSION-HANDOFF.md](19-SESSION-HANDOFF.md) §4.

## 1. Why

Looking back over the Actium work, the curator restated what Chrystallum is for:

- It is a **playground for exploration**, not a CMM-level-5 application.
  Rigor in how we record things must not make the system sterile.
- The AI vision is still discipline agents: facet agents that know their
  sources and keep drilling down and out until the literature is in the
  graph. Eighteen facets weighing in on one subject is a complication, but
  possibly a productive one.
- The **backbone** of a history is better built from its **people** first:
  family, events, roles and offices, allies and enemies, motivations, goals,
  and actions. For the Republic: Marius, Sulla, Pompey, Caesar, Cicero,
  Antony, Octavian, Scipio, Hannibal.
- A life should be seen against the **world**: when Caesar died, what else
  of significance was happening elsewhere.
- **Provenance stays strict**, but there must be room for **artistic
  freedom** that stirs the imagination.

## 2. Decisions

1. **People first, facets after.** Lives are read first. Facets then become
   lenses on that backbone ("Caesar's life through the economic lens"),
   which keeps the discipline-agent vision but runs it second.
2. **Everything is visible at once.** Whatever a reader finds appears in
   exploration straight away, labelled with its status and source
   ("proposed · according to Plutarch"). The curator **promotes** what they
   want (to accepted, or into the narrative) and is not a gate. Agents still
   never accept anything; identity merges and splits stay curator decisions.
   Provenance is unchanged: every claim keeps its source and verbatim quote.
3. **Imaginative works are a third category**, beside factual and
   interpretive: always attributed to a creative Work (novels such as
   McCullough's *Masters of Rome*, films and series, paintings), labelled as
   such, never mixed into the factual layer, and explorable side by side
   with the sources and the scholars.
4. **World context comes from the Year backbone.** A Year and a span around
   it gather whatever else is dated there. Two cheap sources for the world
   beyond Rome: PeriodO's periods for every region (already cached), and
   Wikidata's dated events, loaded as reference data rather than as claims
   read from sources.
5. **The transformation pilot waits.** It is easier once the lives are in
   the graph: the Republic-to-Principate question is largely the question of
   what these people did with offices, armies, and laws.

## 3. The Lives phase

| Step | What | Notes |
|---|---|---|
| L1 | **Visibility** (done 2026-10-13) | Exploration and the Cytoscape export include proposed claims and entities, styled by status; review commands stay, as promotion. Rewrite rule 1 in the handoff and the matching text in [05](05-AGENT-BOUNDARIES.md) and [21](21-REVIEW-DELEGATION.md). As built: the export shows every entity (also unlinked ones), a status and source line on each claim, and passages of note on each entity's card; `--audit` adds rejected, superseded, deprecated, and dismissed content. The read API does not exist yet and will apply the same rule. |
| L2 | **Registry v7** | Already present: `childOf`, `siblingOf`, `spouseOf` (time), `heldPosition` (time), `alliedWith` (time), `participatedIn`, `bornAt`, `diedAt`. To add: enmity or opposition (time), and motivations and goals as **interpretive** claims attributed to an author ("according to Plutarch, Caesar sought…"); `category: imaginative`. |
| L3 | **Person inquiries** | The subject is a person, not a battle. Reading a life names hundreds of people, places, and events, so the reader must be able to propose Person, Event, and Place entities (local-first, with Wikidata candidates), as it already does for periods; under decision 2 they are visible at once. |
| L4 | **Sources** | Plutarch's *Lives* in Perrin's translation (Perseus): Marius, Sulla, Pompey, Caesar, Cicero, with *Antony* already preserved. Find the editions through the Scaife catalogue and source plan; never guess identifiers. Later: Suetonius and the *Res Gestae* for Octavian; Livy and Polybius for Scipio and Hannibal; DPRR for offices and family once its licence is confirmed. |
| L5 | **World context** | A synchronism query (a Year or span → what else is dated there, by region), PeriodO's world periods as background bands, and Wikidata dated events as a reference tier. |
| L6 | **Cost** | Whole-work runs cost about $1–4 each on Sonnet 5.5; six *Lives* should cost about $10–20, and about half that through the Batch API. |

Order: L1 and L2 first (small); then L3 with one life (*Caesar*) as the
test; then the other five; then L5.

## 4. What carries over

Nothing built so far is thrown away. The reader, attributed claims,
qualifiers (role, time, context), interpretations, passages of note,
proposed entities, the period survey, the source adapters, and curation as
data are the parts a Lives reader needs. What changes is the subject of an
inquiry (a person), how much the reader may propose (entities of more
kinds), and how the results are shown (all at once, labelled).
