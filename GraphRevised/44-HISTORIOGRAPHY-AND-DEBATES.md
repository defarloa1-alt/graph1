---
status: decided 2026-11-15 (D-153; §5 answers recorded); nothing built
authority: curator, 2026-11-15: "the focus is not only on classic texts, but in historical thinking about it"
depends_on: [42-CORROBORATION-AND-CLAIM-KINDS.md, 39-LENS-SPECIALISTS.md, 43-ACTIUM-MILITARY-FRAME.md]
superseded_by: null
last_reviewed: 2026-11-15
---

# 44 — Historical Thinking: Questions, Positions, and Who Held Them

## 1. Why

The graph records what the sources say happened, and since D-148 whether a modern
claim retells a source or reconstructs. It cannot yet show **how historians have
thought about a question**: that the ancient writers agree on one account and Dio
differs; that Kromayer revived Dio's view in 1899 and it became the dominant one;
that Tarn answered in 1931 with a defection relying on one passage of Horace; that
Kromayer and Richardson replied; that Lange reconsidered it all in 2011. That
story is content in its own right for researchers, teachers and students, and
not only a route back to the ancient passages.

Today an interpretation is an `interpretive` claim attributed to a Work, and
disagreement shows only as `disputed` when two voices give different values
(42 §3). This records *that* someone held a view, but not the question it
answers, that the same view was held by an ancient author and a modern scholar
1,900 years apart, who answered whom, or which passage a view rests on.

## 2. A worked example (Lange 2011, pp. 608–609)

**Question:** What was Antony's aim in the battle?

| Position | Held by (as Lange reports it) | Rests on |
|---|---|---|
| **He fought to win; Cleopatra's flight lost the battle** (the ancient consensus) | the ancient writers "with one exception"; most scholars until the late 19th century | Plutarch *Antony* 63–68, Velleius 2.85, ... |
| **He meant to break out by sea** | Dio (50.15, 50.30.3–4; though not consistently, 50.33); Gillies 1807, Leake, Merivale 1851, Gravière 1885; **Kromayer 1899**, "the dominant view ever since"; "almost all recent accounts" | Dio 50.15; the size of Octavian's fleet |
| **He fought to win, but was ready to flee if beaten** | Ferrabino 1924; Tarn 1931 (with Syme 1939 in support); rejected by Kromayer 1933 and Richardson 1937 | Tarn's reading of Horace *Epode* 9.17–20 |
| Lange's own position | Lange 2011 | *to be read* |

A second question in the same pages: **What decided the battle?** The ancient
account says Cleopatra's flight; Tarn says the defection of part of Antony's fleet.

What this example shows the model must hold:

1. A **question**, about an event or a person, that scholars answer differently.
2. A **position**, one answer, **shared** by holders across centuries (Dio and Kromayer).
3. **Who held it, when, and who rejected it**, each as a claim with its own voice:
   "Kromayer held it" is something Lange *reports*, so the claim is attributed to Lange
   (basis `reports`) until we read Kromayer himself.
4. **What a position rests on**: the passages its holders rely on, and how they read them.
5. **Its reception over time**: "the dominant view since 1899".

## 3. The proposal

### Two new kinds of entity

| Kind | What it is | Example | Linked to |
|---|---|---|---|
| `Question` | A historical question scholars answer differently | "What was Antony's aim at Actium?" | `about` an Event, Person or Group: one hop from the entity, so it shows on the battle's own page (D-144) |
| `Position` | One answer to a Question, held by one or more voices | "Antony meant to break out by sea" | `answers` its Question |

A Position is an entity rather than a single claim because it is shared: Dio,
Merivale and Kromayer hold the same one, and the interesting fact is that they do.
The lens questions an inquiry already asks (39) are the natural source of
Questions: a debate question is a lens question that the sources answer
differently.

### Predicates (all `interpretive`, registry v17)

| Name | Endpoints | Qualifiers | Meaning |
|---|---|---|---|
| `about` | Question → Event, Person, Group, Polity, Period | none | the question concerns this entity |
| `answers` | Position → Question | none | this is one answer to the question |
| `holds` | **Work** → Position | time (when argued); stance optional: `originates`, `adopts`, `modifies` | the work argues this position. The subject is the Work, not the person, because a scholar can change position (Tarn 1931 and 1938; Dio inconsistent within one history). The author is one hop away through `authorOf` |
| `rejects` | Work → Position | time | the work argues against this position |
| `hadReception` | Position (unary) | time span required; reception: `dominant`, `contested`, `minority`, `abandoned` | how the position stood in scholarship over a span ("dominant since 1899"); always a voice's claim, never ours |

Each is attributed to the Work that says it, like any claim. A Work can state its
own position (Lange's `holds`, basis `reconstructs`) or report another's (Lange
says Kromayer `holds` it: attributed to Lange, basis `reports`; when we read
Kromayer, his own claim joins it as a second voice).

**What a position rests on** reuses the D-148 `RESTS_ON` link: from the `holds`
claim to the passages its holder relies on (Tarn's `holds` rests on Horace
*Epode* 9.17–20), with the quotation of how he reads it. Nothing new.

**Ancient authors are holders too.** Dio `holds` the breakout position. An ancient
interpretation is still an interpretation: Dio's view of Antony's intent is not
evidence of his intent in the way Dio's account of the fleet's movements is
evidence of those movements.

### What attestation says

A Position is **never "well attested"**. How many scholars held a view is not
evidence that it is true, so positions get their own wording, a history rather
than a confidence: "held by Dio; Gillies (1807), Merivale (1851), Kromayer (1899)
and most since; rejected by Tarn (1931)". Factual attestation (42 §4) is unchanged:
interpretive claims never add a line of evidence to a fact.

### How it gets filled

- The **lens reading** of a modern work (the Lange run, 41 phase 1) gets a
  historiography section in its prompt: the questions the work treats, the
  positions it describes, who it says held or rejected each, when, on which
  passages, and its own position. A Question or Position it proposes is a new
  entity, reviewed like any other; every `holds` and `rejects` is reasoning, so
  the curator reviews it (feedback: review reasoning, not extraction).
- The **citation tool** (harvest/article_citations.py) already lists the modern
  works a scholar cites; a work named as a holder becomes a Work entity (not held
  until we read it) with its author as a Person, seeded from Wikidata where it has
  an item, by code (D-145).
- **No extra paid calls**: it is a section of the lens run already planned.

### What the explorer shows

On the battle's page, one hop: its Questions. On a Question: its Positions, each
with a timeline of holders and rejecters (Dio, 1807, 1851, 1899, 1924, 1931, 1933,
1937, 2011) and the passages each rests on. On a scholar or a Work: the positions
it took. That timeline is the historiography.

## 4. Turned down

| Alternative | Why not |
|---|---|
| Positions as claims only (no Position entity) | Cannot say that Dio and Kromayer hold the *same* view, nor give the view a page |
| A `respondsTo` link between Works (Tarn → Kromayer) | It follows from `holds` and `rejects` on one Position, with dates; stored, it would need its own review. Can be derived for display |
| A debate as one node with sides | Debates are rarely two-sided (§2 has three positions); Questions with Positions cover it |
| Scoring positions (stronger, weaker) | Not our judgment to store; reception is a voice's claim (`hadReception`) |

## 5. Curator decisions (2026-11-15, D-153)

| Question | Answer |
|---|---|
| Position as its own entity, or claims only | **Its own entity**, shared by its holders |
| The holder: the Work or the person | **The Work**; the person one hop away (`authorOf`) |
| Ancient authors as holders | **Yes**: an ancient interpretation is an interpretation, never evidence for a fact |
| Reception (`hadReception`) now or later | **Now** |

Still open: **the first Questions** for Actium. From Lange: Antony's aim; what
decided the battle. Others the lens may find: where the battle was fought, why
Cleopatra withdrew. (The fleets' sizes are a numbers dispute, already `disputed`
facts, so perhaps not a Question.) The lens proposes them; the curator reviews.

## 6. What it would take to build

Registry v17 (kinds Question and Position; five predicates; the stance and
reception values); the lens prompt's historiography section; the attestation
wording for positions in export/confidence.py; Question and Position in the
fact layer and the explorer; the seeding of cited scholars and their works. Then
the Lange reading (paid, small, with the curator's go-ahead).
