# Periods and Transformation

**Status:** agreed with the curator, 2026-10-12 (§8). Implementation in progress.
**Builds on:** [03](03-TEMPORAL-YEAR-BACKBONE.md) §6 (periods are not the year
backbone), [22](22-CLAIM-QUALIFIERS.md) (time spans with bounds, attributed
claims), [23](23-NARRATIVE-AND-NOTES.md) (interpretation, Concepts), [07](07-DOMAIN-ADAPTATION.md) §3
(subject constellations), E17 (DPRR offices).

## 1. Principle

No one woke up one morning in a new period. A period is a category historians
draw in hindsight around a transformation that was gradual and contested. The
graph therefore stores two things, and keeps them apart:

1. **The period as a construct**: a conventional name with a fuzzy edge, where
   the sources' disagreement is shown, not resolved.
2. **The transformation itself**: the dated changes in political structures,
   laws, the army, and society that led people to call the result a new kind
   of state, and the scholars' readings of which change was decisive.

Being off by a year in a period's edge is unimportant. Showing what changed,
when, and who says it mattered, is the point.

## 2. A period with a fuzzy edge

A Period is an `Entity {kind: Period}`, with a Wikidata identity where one
exists. **Periods are not seeded by hand: the reader discovers them** (§3a),
which tests whether the sources' own periodization can be recovered; the
Wikidata periods (Roman Kingdom Q201038, Roman Republic Q17167, Roman Empire
Q2277, Principate Q206414) are the identities the curator is expected to link
them to. A Period's dates are never a property of the entity. They come in three
layers, all made of existing parts:

| Layer | Representation | Example (Republic) |
|---|---|---|
| **Definitions** | one attributed `occurred` claim per defining source, with a time span | according to the Epigraphische Datenbank Heidelberg, 509–27 BC; according to the British Museum, about 509–27 BC; according to Pleiades, ...–30 BC |
| **Consensus** | one asserted `occurred` claim, promoted by the curator from the survey (§3), with earliest and latest bounds on each end | start `-0508`, end `-0048/-0026` (49–27 BC) |
| **Transition span** | the end bounds of the consensus, where the definitions disagree | 49–27 BC, drawn as a fade on the timeline, not a line |

- `occurred` (unary, time required) is extended to `subjectKinds: Event,
  Period`. A definition is attributed to its Work or authority, like any
  depiction; a PeriodO record is preserved as the SourceObservation behind it.
- **Membership is computed, not asserted.** Whether Actium (31 BC) falls in
  the Republic, the Empire, or the transition span follows from its date and
  the period's bounds, in the read API. Storing "Actium during the Republic"
  would freeze one definition as fact.
- Period relations, two predicates: `subperiodOf` (Period → Period: the
  Principate within the Empire) and `followedBy` (Period → Period, the
  conventional sequence). Both are attributed or asserted like any claim.
  (`partOf` stays Event → Event, so it can never assert that an event belongs
  to a period.)

## 3. The period survey

A worker, mostly deterministic, gathers definitions and proposes the
consensus:

1. **Sources:** PeriodO (definitions with bounds, by authority and region;
   years are astronomical there), Wikidata (inception and dissolution;
   historical numbering), library headings (LCSH and FAST chronological
   subdivisions, LCC class ranges), and scholarship read by the reader.
2. **Each definition** becomes a preserved observation and an attributed
   `occurred` claim on the Period. Regional or archaeological phases
   ("Roman Republican" pottery in Slovenia from 350 BC) are kept but marked
   regional and excluded from the consensus for the city and state.
3. **Consensus:** for each end, the most common year across general
   (non-regional) definitions; the **transition span** runs from the
   earliest to the latest year that more than one authority uses. The survey
   proposes; the curator accepts or adjusts, with a recorded basis.
4. All years pass through `proposals/temporal.py`, since PeriodO and Wikidata
   number BCE years differently.

### 3a. Periods discovered by the reader

The reader reports each period a passage names, in the author's words, with
the bounds only as the passage states them. A period not yet in the graph
becomes a **proposed entity** (`status: proposed`, kind Period): hidden from
exploration until the curator accepts it, links it to a Wikidata identity,
or rejects it. Before one is created, local candidates are checked (an exact
match reuses the existing entity), and at review the curator sees local and
Wikidata candidates side by side. Where the passage dates the period, an
attributed `occurred` claim records that author's bounds. The same mechanism
carries depicted events (23 §2).

## 4. The transformation as a subject constellation

*The transformation of the Roman Republic into the Principate* is a Subject,
with strands that are read with facet lenses (Phase D):

| Strand | What is graphed | Examples |
|---|---|---|
| Political structures | offices and powers, their holders, over time | consulships in succession; tribunician power without the tribunate; *imperium maius* |
| Laws and settlements | enactments as Events, and what they established, conferred, or abolished | the law creating the triumvirate (43 BC); the settlements of 27 and 23 BC |
| Army and fleet | who commanded and held authority over the forces | the oath of the legions; Actium |
| Society | the Senate, the assemblies, the elite | the proscriptions; the reshaped Senate |
| Interpretation | where scholars place the turn, and why | according to Hale, the day of Actium; Syme's *Roman Revolution* framing 60 BC–AD 14 |

The transition band on the timeline is then filled with these dated,
sourced changes, and the interpretive claims explain why each scholar's
boundary falls where it does: one weighing constitutional form chooses 27 BC,
one weighing military reality chooses 31 BC.

### Predicates (registry v6, added only as the pilot needs them)

| Predicate | Subject → object | Notes |
|---|---|---|
| `established` | Event → Office/Concept/Group | an enactment created an office, power, or body |
| `abolished` | Event → Office/Concept/Group | |
| `conferred` | Event → Person | role qualifier: the office or power conferred; time from the event |
| `followedBy` | Period → Period | conventional sequence |
| `subperiodOf` | Period → Period | narrower period |
| `occurred` (extended) | Period, no object | definitions and consensus (§2) |

Existing predicates carry the rest: `heldPosition` with spans,
`heldAuthorityOver` and `commanded` with roles, and `ledTo` and
`exemplifies` for readings ("Actium led to the Principate", according to
Hale).

## 5. Sources for the pilot

- Ancient: Dio 51–56 (Cary, LacusCurtius), Suetonius *Augustus* (Perseus),
  Velleius Paterculus (LacusCurtius), the *Res Gestae* (public-domain
  translation), Plutarch's *Antony* (already read).
- Modern, public domain: Shuckburgh's *Augustus* (1903, with an index: the
  first index-led test), Ferrero's volumes if a complete scan is confirmed.
- Modern, in copyright: Syme, *The Roman Revolution*, and Strauss, by curator
  capture (23 §7).
- Offices: DPRR (E17), once its licence is confirmed.

## 6. In the explorer

- The timeline shows each Period as a band whose edges fade across the
  transition span; hovering shows the definitions and who holds each.
- Selecting the transition span opens the transformation constellation: the
  enactments, offices, and commands inside it, and the scholars' readings of
  the turning point side by side.
- An event's card says "in the transition from Republic to Principate"
  rather than forcing one period.

## 7. Order

1. Proposed entities (reader-proposed, curator-accepted) and the reader's
   period output (§3a); registry v6: `occurred` extended to Period,
   `subperiodOf`, `followedBy`.
2. A test run: the reader discovers the periods in the works already read.
3. The period survey, starting with PeriodO, Wikidata, and LCSH/FAST.
4. The two failed `ledTo` readings pointed at the Principate.
5. The transformation pilot: `established`, `abolished`, `conferred`;
   enactments and offices; a reading of Dio 51–53 and the *Res Gestae* with
   political and legal lenses.

## 8. Curator decisions (2026-10-12)

All five accepted as recommended below, with one change: periods are not
seeded by hand; the reader discovers them (§3a), as a test.

### As drafted

1. **Period dates as claims**, never entity properties: definitions
   attributed, consensus asserted, transition span from the consensus bounds?
   Recommended: yes.
2. **Membership computed** in the read API rather than stored? Recommended:
   yes.
3. **Consensus rule**: the most common year per end across general
   definitions, with the transition span from the earliest to the latest
   year used by more than one authority? Recommended: yes, adjustable by the
   curator.
4. **Powers** (tribunician power, *imperium maius*): kind `Office`, so they
   can be role qualifiers, or kind `Concept`? Recommended: `Office`, with the
   definition saying it is a power rather than a magistracy.
5. **First Period entities**: Roman Kingdom, Roman Republic, Roman Empire,
   Principate, with the Wikidata identities in §2? Recommended: yes.
