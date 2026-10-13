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
| L2 | **Registry v7** (done 2026-10-13, motives parked) | Already present: `childOf`, `siblingOf`, `spouseOf` (time), `heldPosition` (time), `alliedWith` (time), `participatedIn`, `bornAt`, `diedAt`. To add: enmity or opposition (time), and motivations and goals as **interpretive** claims attributed to an author ("according to Plutarch, Caesar sought…"); `category: imaginative`. |
| L2b | **CIDOC CRM mappings** | A `crm` mapping on each predicate and entity kind in the registry, beside the `wikidata` mapping (for example Person E21, Event E5, Place E53, Period E4, Concept and Office E55, Work E73; `participatedIn` P11, `occurredAt` P7, time qualifiers E52 Time-Span P4; attributed claims as CRMinf I2 Belief). Predicates that CRM expresses through events (`heldPosition` as E85 Joining, `bornAt` as E67 Birth) record that full path; predicates with no CRM property (`opposed`) say so. Quiet: nothing users see changes. CRM stays an interoperability profile, never the native schema ([01](01-ARCHITECTURE.md) §5); the JSON-LD / Linked Art export waits for a consumer, after the read API. Reuse the legacy `CIDOC/` folder: CRM v7.1.2 JSON-LD context, CRMinf, CIDOC-Wikidata mapping. |
| L3 | **Person inquiries, harvest first** | Opens with the agent-driven first-contact harvest (section 10): the deterministic part fetches and preserves the Wikidata record, classes every statement (identifier, attribute, relationship, housekeeping), maps qualifiers, tethers every date to the Year backbone, and proposes one-hop entities and claims "according to Wikidata"; the agent decides what to follow beyond that (which forward links and backlinks, which federations the external identifiers open, when a branch is a leaf), within a budget. Legacy rules and tables to adapt are listed in 16-LEGACY-TRIAGE.md. The reader then adds the ancient and modern voices. |
| L3 (reader) | **Person inquiries** | The subject is a person, not a battle. Reading a life names hundreds of people, places, and events, so the reader must be able to propose Person, Event, and Place entities (local-first, with Wikidata candidates), as it already does for periods; under decision 2 they are visible at once. |
| L4 | **Sources** | Plutarch's *Lives* in Perrin's translation (Perseus): Marius, Sulla, Pompey, Caesar, Cicero, with *Antony* already preserved. Find the editions through the Scaife catalogue and source plan; never guess identifiers. Later: Suetonius and the *Res Gestae* for Octavian; Livy and Polybius for Scipio and Hannibal; DPRR for offices and family once its licence is confirmed. |
| L5 | **World context** | A synchronism query (a Year or span → what else is dated there, by region), PeriodO's world periods as background bands, and Wikidata dated events as a reference tier. |
| L6 | **Cost** | Whole-work runs cost about $1–4 each on Sonnet 5.5; six *Lives* should cost about $10–20, and about half that through the Batch API. |

Order: L1, L2, and L2b first (small); then L3 with one life (*Caesar*) as the
test; then the other five; then L5.

## 4. What carries over

Nothing built so far is thrown away. The reader, attributed claims,
qualifiers (role, time, context), interpretations, passages of note,
proposed entities, the period survey, the source adapters, and curation as
data are the parts a Lives reader needs. What changes is the subject of an
inquiry (a person), how much the reader may propose (entities of more
kinds), and how the results are shown (all at once, labelled).

## 5. Quiet provenance (curator, 2026-10-13)

Authority, federation, and governance are the bedrock that lets any domain
stand, but they are ours, not the user's. The user sees:

- **themselves at the centre**, with **signposts** they choose to follow into
  a particular maze, leaving **breadcrumbs** behind them;
- a **simple, easy-to-read narrative** about whatever they stand on, with
  sources, authority records, and federation details as **sidebar
  properties**, never as relationships on the canvas.

The user does not care whether a fact came from Wikidata, DPRR, or PeriodO;
we do, quietly. Voices are different: "according to Plutarch" or "in
McCullough's novel" is content the user wants, so authors and Works stay
visible while source systems stay in the sidebar. The canvas shows
historical relations only; SourceObservation, AuthorityRecord, Proposal, and
Year stay off it, as they already do in the export.

## 6. Registry v7 design log (L2)

| # | Question | State |
|---|---|---|
| 1 | Opposition: name and shape | **Decided 2026-10-13.** One symmetric predicate `opposed` (Person or Group, either way round), time required, optional Event context (the war or battle), asserted or attributed. No Wikidata mapping: P7047 ("enemy") is defined for fictive characters only, and Wikidata has no property for historical opposition (checked 2026-10-13). No split into political, military, or personal: the context Event, other predicates (offices, kinship), and interpretations carry those. Worked case: Antony and Octavian, 44–30 BCE. |
| 2 | What a motivation points to | **Open, parked by the curator.** Proposal on the table: interpretive, attributed-only `sought` (Person or Group → Concept or Office, optional Event context) and `influenced` (Person → Person, optional Event context); the source's words stay in the required quotation; feelings, and professed versus real aims, stay passages of note. |
| 3 | How imaginative Works are marked | **Decided 2026-10-13.** The Work carries a `form` (history, biography, poem, play, novel, film, painting, …; from Wikidata P31/P136 where present, else the curator). Every claim attributed to a creative Work is `imaginative`, derived, never chosen by the reader; the validator refuses any other category for it. Nonfiction stays factual or interpretive (an author's speculation presented as probably true, such as Weigall's reconstructions, is interpretive). Imaginative claims use the ordinary predicates, are always attributed, and form their own visual lane. Worked case: Actium in Virgil *Aeneid* 8, Horace *Odes* 1.37, Shakespeare, Dryden, Castro's painting; copyrighted works (McCullough, films) by metadata and curator capture only. Queued sub-questions: (a) characters, the same node as the historical person or a character node linked by `depictsSameAs`; (b) which forms count as creative (historical novel versus dramatized popular history). |
| 4 | Confidence: computed or assigned, built or only designed in L2 | **Decided 2026-10-13; built in L2.** Computed at read time, never stored, shown in words, never as a number: well attested (two or more authors), attested (one author), disputed (open conflicts), one author's reading (interpretive), imagined (imaginative), no evidence yet. Inputs: the claim family (same predicate, subject, and object: the asserted claim and its attributed versions together, grouped at read time), the number of distinct authors behind it (Work → author through the existing `authorOf` predicate), conflicting qualifiers within the family, category, and status. The curator chose not to classify Works as ancient/modern or primary/secondary: authorship alone. Known limit: a modern author who builds on an ancient one counts as a second author. Neither the reader nor the curator assigns a score. Worked case: Cleopatra at Actium is unsupported as a lone asserted claim but attested by Plutarch, Dio, Hale, and Weigall as a family. |

**As built (2026-10-13).** [predicates.v7.json](proposals/predicates.v7.json) adds `opposed`
and the Work forms; the validator derives `imaginative` from the attributed
Work's `form` (set by the `set_work_form` operation, through a `form` on a
curation `works` entry) and refuses fiction as evidence for an asserted claim;
reader prompt v12 adds a rule for opposition; [export/confidence.py](export/confidence.py)
computes the attestation shown in the export. Details that follow from the code:

- An author is the Person of the Work's `authorOf` claim, else the Work
  itself, else the source system for evidence outside any Work (Wikidata
  statements count as one source).
- A dispute is two family members giving a context or role that differ, or
  normalized time bounds that do not overlap. A time given in different words
  is not a dispute. Disagreement across families (Dio has Augustus command
  Octavian's fleet, Hale has Agrippa) is not detected: `commanded` is not
  exclusive, so both can hold.
- Not yet done: forms are not set on any Work in the graph (the curator's
  call); forms are not read from Wikidata; Weigall and Hale have no
  `authorOf` claim (each counts as its own author meanwhile).

## 7. Narratives and personas (test, 2026-10-13)

An agent wrote Mark Antony's centre-stage narrative twice, from the graph
alone (four works, claims, passages of note, the Wikidata description): once
for a researcher (quotations, footnoted locators, voices side by side) and
once for an explorer who knows nothing of Rome (a hook, a cast list, the
dispute over Antony's flight told as a mystery, no visible citations). The
curator found the researcher version matched the intended centre stage.

Rules the test produced:

1. **A persona changes the presentation, not the data.** Both versions used
   the same passages and nothing from outside the graph.
2. **Passages of note carry most of a narrative.** Claims gave the skeleton
   (who, where, when, command); notes gave the why, the mood, and the
   disputes. The narrative reads both.
3. **Quote sources, never the reader's summaries.** A note's summary said
   "for three days"; the quotation did not, so it was left out.
4. **State something flatly only where the sources agree; otherwise name who
   says it.** Simplifying for an explorer pushes towards flat statement.
5. **Disagreement is the hook.** Four voices on one flight engage more than
   one smoothed account.
6. **Where the graph ends, the narrative says so and offers a signpost**
   ("not yet read: Antony before 32 BC"), which is the natural trigger for
   the next reading run.

**Personas, open (TBD).** The curator leans towards a brief questionnaire in
which users say what they need, and finds it attractive that a user can
switch persona at will. Candidate personas: researcher, explorer,
high-school student, graduate student, novelist or curious reader.

## 8. Subjects and library headings (curator, 2026-10-13)

The single Subject (*History of the Battle of Actium*) looked like a copy of
the event. The distinction kept: the event is what happened; the Subject is
what has been written about it, which is where bibliographic sources belong.

- **Decided.** A Subject carries its library subject headings, LCSH and FAST,
  where they exist, as AuthorityRecords with role `subject_access`
  (`curation/subjects.json`, applied through `upsert_subject_authority`).
  Each identifier is checked against its authority first; the label is read
  from the preserved record, never typed.
- **Decided.** Never display a code alone: always the authority's words with
  the code beside them, "Battle of Actium (31 B.C.) (FAST 796265)".
- **Decided.** LCC is skipped for now. The legacy `Subjects/LCC/dg_schedule.csv`
  proved largely invented (16-LEGACY-TRIAGE.md).
- **As applied.** LCSH sh85000736 *Actium, Battle of, 31 B.C.* and FAST 796265
  *Battle of Actium (31 B.C.)* (ODC-By, attribution required). The FAST
  identifier is 796265; OCLC marks the fst00796265 form deprecated. LC
  cancelled the heading's LCC number DG269 in 2002, which a pasted research
  summary had read as a confirmation.
- **Open.** Works covering a Subject (coverage such as chapters or pages, and
  kind: ancient account, modern history, imaginative), reading state per
  Work, and parent Subjects from the headings' broader terms (LCSH
  *Rome--History--Civil War, 43-31 B.C.--Campaigns*; FAST *Roman Civil War
  (Rome : 43-31 B.C.)*). These feed the "Read more" list on a card and the
  growth loop's reading list.

## 9. Open items and holds (curator, 2026-10-13)

- **Open, to take up:** Subject coverage, reading state, and parent Subjects
  (section 8); Work forms for the five Works in the graph; L2b CIDOC CRM
  mappings; motives (`sought`, `influenced`, section 6).
- **Held:** option B, folding Proposals into their claims as review history
  (the review records add about 170 nodes; users never see them).
- **Names over time (for L3):** an alias property shows the common name, so
  Octavian is not shown as "Augustus" in 31 BC. Details to settle when
  person inquiries begin.

## 10. First-contact harvest and dates (curator, 2026-10-13)

**Vision (curator).** When a subject or person is first met in Wikidata, the
agent harvests its whole record: properties, external identifiers
(federations), and forward and back links as the agent judges useful. A
person with a QID then has everything Wikidata gives (birth place with
coordinates, family, offices) from the start. The full record is already
preserved for every identity (Antony: 219 statements, 160 properties, 120
external identifiers); almost none of it is used yet.

**Decided: four kinds of Wikidata statement**, classed in the registry as data
(default by datatype, explicit overrides):

| Kind | Becomes |
|---|---|
| Identifier (external-id) | a labelled AuthorityRecord, the quiet federation crosswalk |
| Attribute (non-date literals, classifying values: gender, occupation, manner of death) | a property shown on the card, "from Wikidata" |
| Relationship (item-valued, to another historical entity; often date-spanned and with a role: position held, spouse, conflict, place of birth) | a claim with qualifiers, "according to Wikidata" |
| Housekeeping (Commons category and the like) | ignored; kept in the preserved record |

Qualifiers map onto claim qualifiers: start and end time, point in time,
earliest and latest date (an uncertain window), together with (colleague),
applies to jurisdiction (context), series ordinal, end cause. Building this
is the first L3 step: the Wikidata proposer currently defers every statement
with qualifiers.

**Decided: every date tethers to the Year backbone.** No date is a bare
property: birth, death, office terms, and marriages are dated claims, and the
card reads them from those claims. A claim tethers by what its date means:
*during* (true throughout: `IN_YEAR` to each year), *sometime within* (an
uncertain window: its earliest and latest years), or a long span (its start
and end years; today spans over 200 years get no Year link, which leaves 11
of 15 dated claims untethered). Relative times borrow their context event's
year, marked as derived. A date outside the backbone (2000 BCE to 2025)
extends the backbone or is flagged, never skipped silently. Undated claims
stay undated and appear in the slider's undated tray.

## 11. Surfacing entities and enrichment (curator, 2026-10-13)

**Decided: the one-hop rule, for every agent.** Whenever any agent meets an
entity (the harvest, the passage reader, a curator capture: a place, a
parent, a participant, an office), it proposes people, places, events,
offices, groups, and periods as entities (visible at once, labelled);
reference works go to the bibliography as catalogued Works for the Subject's
"Read more" list, not to the canvas; noise is dropped by rule (collections,
copyright status, writing language); the agent judges the rest within a
budget. Antony's harvest reached 69 entities this way: about 28 people, 8
offices, 7 events and periods, 2 places, 4 groups, 14 reference works, and 5
noise.

**Decided: in a sparse graph, early agents populate beyond the focus.** That
was the purpose of the subject facet agents (SFAs), and it returns as
**enrichment by kind**: when an entity surfaces, its kind and its external
identifiers route it to an enricher (a place with a Pleiades ID to a
geographic enricher: coordinates, ancient names, neighbours; an office with
DPRR and Wikidata records to an institutional one: rank, terms, holders by
year; a battle to a military one: sides, commanders, date, place; a coin type
with a Nomisma ID to an economic one). Facets become enrichers run on what
surfaces, demand-driven and budgeted, rather than standing agents per
Subject: people first, facets after (decision 1).

**Dates at day or month precision** are stored on the claim (`timeEdtf`, for
example -0082-01-14, with calendar, precision, and Julian Day Number bounds)
and tethered to their Year; Year nodes hold the year only. Antony's two birth
claims (83 BCE, preferred and referenced; 14 January 83 BCE, unreferenced)
do not conflict. A day-exact date before the Julian reform of 46 BCE is a
modern conversion and a weak voice.

## 12. Structure: types, institutions, and facets as lenses (curator, 2026-10-13)

**Decided.** Unit types, organizational patterns, roles, and powers are a new
Entity kind **Type**, and states such as the Roman Republic or the Ptolemaic
Kingdom a new kind **Polity**. They are nodes, so hierarchies and relations
can be drawn: `partOf`, `instanceOf`, `precedes`, each a dated, sourced claim.
Facets stay lenses that filter Types and claims (military, political); they
are not nodes. Offices stay kind Office; institutions (Senate, assemblies)
are Groups; a historical legion or fleet is a Group that is an instance of a
Type. This is the structure the subject facet agents used to build, now built
by the enrichers by kind (section 11). The full mapping and the registry v9
plan are in [docs/Response - Roman Republican Institutions and Military
Hierarchies.md](docs/Response%20-%20Roman%20Republican%20Institutions%20and%20Military%20Hierarchies.md).
The budget for increment 3: harvest the surfaced people, events, and places
(not reference works or offices), about 50 new entities per run, the agent
choosing when there are more.

