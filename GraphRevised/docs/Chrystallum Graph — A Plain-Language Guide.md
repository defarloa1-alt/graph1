# Chrystallum Graph — A Plain-Language Guide

First written 17 November 2026; brought up to date 20 November 2026 (predicate registry v20).

## What this guide is

Chrystallum is a graph of the ancient world: people, places, events and the books that tell us about them, joined by lines that say how they relate. This guide explains, in plain words, what each kind of thing in the graph is, what its details mean, and what each kind of line means.

It is written for a reader who wants to explore or review the graph without knowing databases. It follows the technical data dictionary ([36-DATA-DICTIONARY.md](../36-DATA-DICTIONARY.md)) and the live graph as of 20 November 2026, which holds 894 entities, 2,867 claims and 1,073 source passages and records.

## The big idea

The graph keeps what happened apart from who says so. Entities are joined by **fact lines** you can walk in one step; each fact line is a summary of one or more **claims**, and each claim points to the **source passage** that backs it.

```text
Agrippa ──COMMANDED──> Left wing of Octavian's fleet        (the fact line you walk)
              │
              ├── claim: our own statement ─────> Plutarch, Antony 65.2 "Caesar posted Agrippa on the left"
              ├── claim: according to Plutarch ─> the same passage
              └── claim: according to Weigall ──> Weigall 17.18 "the left wing being commanded by Agrippa…"
```

A claim made in our own voice is *asserted*; one given "according to" a source is *attributed* to that Work. Proposed and accepted claims both appear, always labelled. Claims from fiction are *imaginative* and are never shown as history.

## The kinds of things (nodes)

Every dot in the graph is a node, and its label says what kind of thing it is. There are three families: the things history is about (entities), the paperwork that says what we know about them (claims, proposals, sources, notes), and the background grids of time and space (years and locations).

### Things history is about: entities

Every entity carries the label Entity plus exactly one kind. The kind tells you what it is.

| Kind | What it is | Example |
| --- | --- | --- |
| Person | One human being | Mark Antony |
| Place | A named place as historians speak of it | Actium |
| Event | Something that happened, from a war to one phase of a battle | Battle of Actium |
| Group | A collective that acts together: a fleet, an army, a faction, a Roman family (gens) | Antony's fleet; gens Pinaria |
| Polity | A state or political body | Ptolemaic Kingdom |
| Office | A post someone can hold | Roman consul |
| Period | A stretch of history historians name | Roman Republic (the era) |
| Work | A source of any kind: an ancient text, a modern book or article, a coin series, a dataset, a film | Plutarch, *Life of Antony*; Antony's legionary coins |
| Object | A physical thing | the Campsite Memorial of Augustus; the purple sails of Cleopatra's ship |
| Concept | An idea historians use to explain things | Propaganda |
| Type | A pattern something belongs to: a role, a unit type, a ship type, a material, a colour | Quinquereme; silver |
| Question | A historical question scholars answer differently | Was Antony's aim in the battle of Actium victory, or withdrawal by sea? |
| Position | One answer to a Question, which Works argue for or against | Antony fought for victory until Cleopatra fled |
| Other | Anything not yet classified | — |

The Roman Republic appears twice on purpose: once as a Polity (the state, which acts and is acted on) and once as a Period (the historians' name for an era, whose dates differ by source).

Two special kinds of Event exist. A **depicted event** is an event as one source narrates it, kept apart until the curator decides two sources describe the same action. A **phase** is a slice of an event that Chrystallum defines for its own analysis, such as the opening moves of a battle.

### The paperwork: what we know and how

| Node | What it is, in plain words |
| --- | --- |
| Assertion (a claim) | One statement about entities, such as "Antony commanded the left wing at Actium". It records who says so, when, and its status. |
| Proposal | A request to add a claim, add evidence to one, or add a name to an entity, with the reason. A proposal waits for the curator to accept or reject it. |
| SourceObservation | A piece of evidence we hold: a passage of an ancient text, a transcription, a database record, a coin record, or an image's details. It is kept exactly as found. |
| AuthorityRecord | A record from an outside reference system, such as Wikidata, Pleiades or the Library of Congress. It tells us how others identify a thing; it is not our verdict. |
| Annotation | A note someone wrote: a highlight on a passage, a comment, an observation. A note is never a claim. |
| Subject | A topic or research bucket that gathers entities, such as "Battle of Actium: meaning and memory". |

### The background grids

| Node | What it is |
| --- | --- |
| Year | One year on a single timeline from deep past to future, linked in order. Negative numbers are BCE, and there is no year zero (1 BCE is followed by 1 CE). |
| Location | A point or area from the Pleiades ancient gazetteer or the modern GeoNames gazetteer. About 505,000 of them sit in the background; a Place connects to one when we know where it is. |

## The lines between things (relationships)

A relationship is a line from one node to another, and its name says what the connection means. Lines have a direction: "Antony COMMANDED the fleet" runs from Antony to the fleet. They fall into five groups.

### 1. Fact lines: what you see when you explore

These join one entity straight to another, so you can walk from Antony to Actium in one step. Each one is a summary of the claims behind it and is rebuilt from them automatically; nobody edits it by hand. There is one line per live fact, named after what the fact says.

| Line | Reads as |
| --- | --- |
| PARTICIPATED\_IN, INVOLVED\_IN | a person or group took part in an event; a thing was involved in it (a seized ship) |
| COMMANDED | the person actually led the force in action |
| HELD\_AUTHORITY\_OVER | the person had formal command, whether or not they led in battle |
| ALLIED\_WITH, OPPOSED | two sides were allies, or rivals or enemies |
| OCCURRED\_AT | the event happened at this place |
| PART\_OF | a smaller event within a larger one, or a unit within a larger force |
| TRIGGERED\_BY, RESULTED\_IN, HAPPENED\_BEFORE | how one event leads to or precedes another, as a source tells it |
| LED\_TO | a long-range consequence, in one author's reading |
| BORN\_AT, DIED\_AT, CHILD\_OF, SPOUSE\_OF, SIBLING\_OF | life and family |
| OF\_GENS | a person belongs to a Roman family (gens), according to a source |
| HELD\_POSITION | a person held an office |
| AUTHOR\_OF, DESCRIBED\_BY | a person wrote a work; a thing is described in a work |
| INSTANCE\_OF, SUBTYPE\_OF, EXEMPLIFIES | a thing is of a type; a type sits under a broader type (silver under metal); something is an example of a concept |
| MADE\_OF, MADE\_FROM, PRODUCED\_AT, STRUCK\_IN, HAD\_COLOUR | materials and making: a coin is made of silver, a dye made from a shellfish, a series struck in a metal, sails that were purple |
| DEPICTS\_SAME\_AS | two sources' depicted events are the same real action (the curator's call) |
| DISTINCT\_FROM | two similar-looking entities are not the same |
| ABOUT, ANSWERS, HOLDS, REJECTS | a question is about something; a position answers it; a work argues for or against a position |
| SUCCEEDED\_BY | one period conventionally comes after another |
| OCCURRED, BORN, DIED | these run from an entity to a Year: when it happened |

The full list holds 51 kinds of fact (the predicate registry, version 20), including some not yet used by any claim, such as the military ones (strength, captured, surrendered to, defected to). The table shows the ones in the graph today.

### 2. Claim lines: the claim and its parts

| Line | Means |
| --- | --- |
| ASSERTION\_SUBJECT | the claim is about this entity (who did it) |
| ASSERTION\_OBJECT | the other entity in the claim (what was done to, or with) |
| ASSERTION\_CONTEXT | the setting of the claim, usually an event: "opposed, in the Actium campaign" |
| ASSERTION\_ROLE | the capacity in which someone acted, usually an office or a role: "as consul", "as defector" |
| ATTRIBUTED\_TO | the Work that says it, when the claim is given "according to" a source |
| IN\_YEAR | the year or years the claim falls in, each saying how (during, start, end, earliest, latest) |
| SUPERSEDED\_BY | this claim was replaced by a better one |
| PROMOTED\_FROM | this claim grew out of an earlier one |

### 3. Evidence lines: why we believe it

| Line | Means |
| --- | --- |
| SUPPORTED\_BY | an accepted claim rests on this passage or record, with the quotation that backs it |
| PROPOSES | a proposal asks for this claim |
| PROPOSES\_EVIDENCE | a proposal offers this passage as evidence, still waiting for review |
| RESTS\_ON | a modern scholar's claim retells this ancient claim or passage |
| IN\_WORK | the passage comes from this Work |
| ANNOTATES | a note comments on this passage or image |
| CONCERNS | a note is about this entity |

### 4. Identity and topic lines

| Line | Means |
| --- | --- |
| HAS\_AUTHORITY\_RECORD | this entity is identified by this outside record (for example its Wikidata entry). A link still proposed is shown as proposed; a rejected one is kept only as history |
| HAS\_SUBJECT\_HEADING | the Library of Congress catalog files this book under this heading |
| BROADER\_HEADING, RELATED\_HEADING | how two Library of Congress headings relate |
| HAS\_SUBJECT\_FOCUS | a topic covers this entity |
| IN\_SUBJECT | an event is placed in this topic section |
| NARROWER\_THAN | a smaller topic sits inside a larger one |

### 5. Time and space lines

| Line | Means |
| --- | --- |
| FOLLOWED\_BY | between Years, the next year (periods use SUCCEEDED\_BY, a fact line) |
| AT\_LOCATION | a Place is at this gazetteer location |
| WITHIN | a location lies inside a larger one (a city in a province) |
| MODERN\_LOCATION | an ancient location's modern counterpart |

## The details stored on things (properties)

A property is a named detail on a node or line, like a field on a form. Most readers only need the handful below.

### On every entity

| Property | Means |
| --- | --- |
| id | A permanent machine name, such as chr:entity:…; it never changes even if the name does |
| label | The name shown to readers |
| shortLabel | A shorter name for tight spaces |
| alternativeNames | Other names the entity is found by, such as "Scarpus" for Pinarius Scarpus. Each one is proposed with its reason and joins only when the curator accepts it |
| labelHistory | When a name was changed: the old name, who changed it, when and why |
| status | How settled the entity is: proposed, provisional, resolved, or deprecated (retired) |
| description | A short description we have adopted |
| when, where, partOf | Ready-made summaries such as "31 BCE, according to Plutarch", rebuilt from the claims; for display only |
| history | On a Position only: its story in one line, such as "held by Cassius Dio; dominant ever since (according to Lange)". Who held or rejected it, when, and how it was received; rebuilt from the claims |

A few kinds add their own details:

- A **Work** has a **standing**: primary (an ancient source), secondary (a modern study) or tertiary (a reference work); a Work with none is treated as reference. It also has a **form**, such as history, biography, letters, inscription, coinage, play or film.
- A **Type** has a **typeCategory**: role, unit type, organizational pattern, power, status, ship type, naval fitting, taxon, material, product, denomination or colour.
- A **Group** may have a **groupCategory**; so far the one category is gens, a Roman family.
- A **Person** may carry the parts of a Roman name (praenomen, nomen, cognomen, agnomen), with the source they were read from. The parts are details of the person, not separate nodes.
- An **Event** has an **eventType**.

Dates, family ties, offices and places are never stored on the entity itself. They are claims, because sources disagree about them.

### On a claim (Assertion)

| Property | Means |
| --- | --- |
| predicate | What kind of fact it is, such as commanded or bornAt |
| label | The claim as a readable sentence, rebuilt from its parts when an entity is renamed |
| status | proposed, accepted, rejected, contested, or superseded |
| category | factual (history), interpretive (an author's reading), or imaginative (from a play, poem or film; never history) |
| mode | asserted (we say it) or attributed (a source says it) |
| basis | For a modern or reference work's claim: reports (retells an ancient source), reconstructs (the author's own argument) or unknown |
| assertedBy | The person or agent who drafted it |
| time… properties | The date as the source words it ("in the consulship of…"), the normalized date, how precise, and whether approximate or uncertain |
| …Jdn properties | The earliest and latest possible day, as day numbers, so uncertain dates can still be sorted |
| quantity… properties | A number the source gives, such as fleet size, with its minimum, maximum, wording, and whether it is exact, approximate, round or rhetorical |
| stance | On holds only: whether the work originates, adopts or modifies a position |
| reception | On hadReception only: whether a position was dominant, contested, minority or abandoned. A reception is a claim about one Position, so it draws no line; you read it in the Position's history |
| superseded…, restored…, reopened…, retracted… | The audit trail when a claim is replaced, brought back, reopened or withdrawn |

### On the fact lines

| Property | Means |
| --- | --- |
| attestation | How well the fact is supported, in words, computed from its sources |
| sentence | The fact as a sentence |
| accordingTo | Which works say it |
| when, role | The time and capacity, if known |
| assertions | The claims this line summarizes |
| derived | Always "fact-layer": a reminder that the line is computed |

### On a source passage (SourceObservation)

| Property | Means |
| --- | --- |
| sourceSystem | Where it came from (a translation, Wikidata, Wikipedia, a catalog, a coin database) |
| observationKind | passage, transcription, record or image |
| passageText, locator | The words, and where in the work they are (book and chapter, page, coin type) |
| workTitle, author, translator, editionCitation | Which edition we read |
| retrievedAt, contentHash | When we captured it, and a fingerprint that proves it has not changed |
| footnotes | For a transcription, the book's footnotes as printed |

### On a proposal

| Property | Means |
| --- | --- |
| operation | create (a new claim), addEvidence (more support for an existing one) or addAlias (another name for an entity) |
| rationale | Why the change is asked for |
| status | submitted, validating, accepted, rejected or deferred |
| createdBy, modelId, promptVersion | Who or which agent made it, and with what instructions |
| decidedAt, decidedBy, decisionReason | The curator's decision and why |

### On a note (Annotation)

| Property | Means |
| --- | --- |
| kind | passage-of-note, entity-mention, note, or image-note |
| note | The comment itself |
| author, visibility | Who wrote it, and who may see it: private, team or public |
| status | flagged, endorsed or dismissed |

Notes come from the curator's reading notes in Obsidian. Two things keep them honest. The book's own footnotes are kept with the book's words (the passage), never with the curator's thoughts. And a note's list of what it concerns may arrive filled in by an agent, each entry marked *suggested* with its reason, for the curator to confirm or change before the note is added to the graph.

## Lenses: ways of reading

A lens is one way of looking at anything in the graph: military, political, economic, geographic, religious, and so on, eighteen in all, plus a general lens that looks across them. A lens is never a node in the graph. It decides which questions an agent asks when it reads a source ("how was the army supplied?") and which lens tags a reading note carries. Five lenses are in full use today (military, political, economic, social, religious), with the general lens beside them; the other thirteen are catalogued and tag notes, but read sources only once their grounding for the Roman Republic is written and reviewed.

## How trust and review work

Nothing becomes a fact without a source and a decision. Agents and people draft claims; the curator decides which stand. Today 677 claims are accepted, 1,815 are proposed and waiting, 363 have been replaced by better ones, and 12 were rejected.

1. **A claim is proposed.** An agent reading a passage, or a person, writes a Proposal: the claim, the passage that backs it, the quotation, and the reason.
2. **The curator reviews the reasoning.** Copying words straight from a source, or a fact read straight from a database record, needs little checking and may be accepted by rule; an inference drawn from them is what gets reviewed.
3. **The claim is accepted or rejected.** An accepted claim gains SUPPORTED\_BY lines to its evidence. A rejected one stays in the record, marked rejected, so the decision can be seen later.
4. **The fact line is rebuilt.** Accepted and proposed claims are summarized into the one-step lines between entities, each labelled with its status so you can tell them apart.
5. **Claims can be replaced, never quietly changed.** A corrected claim is a new claim; the old one is marked superseded and points to its replacement. A replacement made in error can be undone, and the record shows that too.

**Attestation** is the word you will see on fact lines. It says how the fact is supported, in plain words: which ancient sources say it, and which modern works retell them. It is never a made-up confidence score. A modern book that only retells Plutarch does not count as a second independent witness; it counts through Plutarch.

**Wikidata is a voice**, not our own statement. What it says appears "according to Wikidata", beside the other sources.

**Imaginative claims**, from plays, poems and films, sit in their own category. They show how a story has been told, and are never presented as history.

## Worked example: Agrippa commanded the left wing

One line in the graph, "Marcus Vipsanius Agrippa commanded Left wing of Octavian's fleet at Actium", is backed by five live claims (voices). Here is how to read it, taken from the live graph on 20 November 2026.

**The fact line.** A COMMANDED line runs from Agrippa (a Person) to the left wing (a Group). Its status is accepted, its category factual. Its attestation reads: "attested (1 ancient source); retold by Wikipedia; also in Lange, Weigall".

**The voices behind it.**

| Voice | Who says it | Evidence | Status |
| --- | --- | --- | --- |
| Our own claim (asserted) | Chrystallum | Plutarch, *Antony* 65.2: "Caesar posted Agrippa on the left"; and 66.3 | accepted |
| According to Plutarch | Plutarch, *Life of Antony* | the same two passages | accepted |
| According to Weigall | Weigall, *Life and Times of Cleopatra* 17.18 | "the left wing being commanded by Agrippa…" | accepted |
| According to Lange | Lange, *The Battle of Actium: A Reconsideration* | p. 617 (a licensed article: cited, not quoted) | proposed |
| According to Wikipedia | Wikipedia, *Battle of Actium* | "…commanding from the left wing of the fleet"; retells Plutarch | proposed |

**How to read it.** Only one ancient source, Plutarch, is counted as a witness. Wikipedia's version is marked as retelling Plutarch (a RESTS\_ON line to his Work), so it does not count as a second ancient witness. Weigall and Lange are modern authors who say the same, listed with "also in". The Lange and Wikipedia voices are still waiting for review, but the fact stands on its accepted voices. (A sixth voice, a second copy of Weigall's passage, was rejected as a duplicate; it stays in the record and no longer counts.)

## Glossary

| Term | Meaning |
| --- | --- |
| Accepted | The curator has approved the claim |
| Alias | Another name an entity is found by, accepted by the curator |
| Asserted | A claim we make in our own voice, backed by evidence |
| Attestation | How a fact is supported, in words, from its sources |
| Attributed | A claim given "according to" a particular Work |
| Authority record | Another system's record for a thing (Wikidata, Pleiades, Library of Congress) |
| BCE / CE | Before / of the Common Era; the graph stores BCE years as negative numbers |
| Claim (Assertion) | One statement about entities, with its source and status |
| Curator | The person who decides which claims stand |
| Depicted event | An event as one source tells it, kept separate until matched with others |
| EDTF | A standard way to write uncertain or approximate dates |
| Entity | A person, place, event or other thing history is about |
| Fact line | The one-step line between two entities that summarizes their claims |
| Gens | A Roman family name group, such as the Pinarii; a Group in the graph |
| Imaginative | From fiction, drama, poetry or film; never presented as history |
| Julian Day Number (JDN) | A plain count of days used to sort dates across calendars |
| Node | A dot in the graph: one thing |
| Predicate | The kind of fact a claim states, such as commanded or bornAt |
| Primary / secondary / tertiary | Ancient source / modern study / reference work |
| Proposal | A request to add a claim, evidence or a name, awaiting the curator |
| Proposed | Drafted but not yet reviewed |
| Relationship | A line between two nodes |
| Superseded | Replaced by a newer, better claim |
| Voice | One claim behind a fact: one source's version of it |

## The architecture review of 17 November 2026

When this guide was first written, a review compared the data dictionary with the live graph, the predicate registry (then v17) and the code. All ten findings are now closed:

| # | Finding | Status |
| --- | --- | --- |
| 1 | The integrity check did not know Question or Position | Fixed: no untyped entities |
| 2 | Most kind-specific properties in the dictionary do not exist in the graph | Fixed: the dictionary says which are built and which only designed; coordinates live on Location |
| 3 | IN\_SUBJECT missing from the dictionary | Fixed |
| 4 | 27 undocumented property keys | Fixed: the audit fields are documented; the strays hold no data (names Neo4j keeps after old data was deleted) |
| 5 | Period followedBy shared the name FOLLOWED\_BY with the Year chain | Fixed: period succession is drawn as SUCCEEDED\_BY |
| 6 | Type categories: registry and dictionary disagreed | Fixed |
| 7 | The logical model's counts were a month old | Fixed: remaining figures are marked as a dated snapshot |
| 8 | The dictionary's review date was stale | Fixed |
| 9 | Weigall 17.18 appeared as two voices on Agrippa's left-wing fact | Fixed: the duplicate is rejected |
| 10 | Subject code still looked for a retired BROADER relationship | Fixed |
