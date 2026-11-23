---
status: draft 2026-11-22, for the curator's choices (§7); built 2026-11-22: laws, decrees and assemblies (D-171, registry v21, §4); the six shapes confirmed and patronOf adopted (§3)
authority: curator, 2026-11-22 (chat): roll up the ChatGPT review in chats/Agents and Exploration.yml against what the repo holds, for both the user and a developer
depends_on: [05-AGENT-BOUNDARIES.md, 06-GRAPH-NAVIGATION.md, 39-LENS-SPECIALISTS.md, 45-NATURAL-KINDS-AND-MATERIALS.md, 46-ROMAN-NAMES-AND-GENS.md]
superseded_by: null
last_reviewed: 2026-11-22
---

# 48 — The Political Lens, Laws and Assemblies, and Paths Across Domains

## 1. Why

On 2026-11-21 ChatGPT read four of our design documents and answered four
questions: what a Roman Republic political specialist needs, which predicates
and fields are missing, whether the model fits CIDOC CRM, and how agents should
behave if the goal is paths ("senator to mollusk") rather than an encyclopedia.
The chat is kept in [chats/Agents and Exploration.yml](chats/Agents%20and%20Exploration.yml).

It saw only part of the repo, so much of what it calls missing is built or
decided. This doc separates the two, records what was added from it, and lists
what is left for the curator to decide.

**In one paragraph, for the user.** The review is right that the political lens
lacks patronage, political friendship, laws, trials and vetoes, and right that
the senator-to-mollusk goal changes how agents should behave. We already had a
plan for those paths (docs 05 and 06), the gens (46), and the materials and
animals on the way to the mollusk (45). We take its political relationships into
the request queue, give laws a place of their own and assemblies a place among
groups, and keep our rule that a claim needs a source, however far from home the
agent has travelled. We do not take its confidence percentages or stored "bridge
scores".

## 2. What the review asked for, and where it already stands

| The review said | Where it stands |
|---|---|
| A gens predicate is missing | `ofGens`, registry v20 (D-166, 46): Person to a Group of category `gens`, for life, so no time; an adopted person has two. |
| Materials, dye, mollusk predicates | Registry v18 and v19 (D-160, 45): taxa, materials, products and colours as Types; `subtypeOf`, `madeOf`, `madeFrom`, `producedAt`, `hadColour`. Pliny's purple (migration 020) and Cleopatra's purple sails (021) are loaded. |
| `electedBy`, `memberOf`, `exercisedPower`, `heldPower` | In the registry since v9. Some have little data, which is a gap in harvesting, not in the model. |
| Questions and Positions for debates | Registry v17 (D-153, 44). |
| Align to CIDOC CRM | Decided: CRM is an interoperability profile for export, never the native schema (16, 37); CRMinf for attributed claims and lens readings. |
| Acts should be Events with roles, states predicates | D-138 (39 §10). The review reaches the same rule in its CRM answer. |
| Path discovery from senator to mollusk | 05 §1 routes it as `DISCOVER_SEMANTIC_BRIDGE`, not a shortest-path query; 06 §13 to §16: a path is a hypothesis (`PathHypothesis`, `TraceHop`), never a claim; separate lenses test separate hops; no permanent Bridge Agent; paths ranked by predicate specificity and evidence, not length. 39 §8 has the specialist's "test one hop" call. |
| Political families to add | Already listed as open in 39 §10, from the lens run and the Gracchus narrative: patron and client, mentor, amicitia and inimicitia, legal acts, Law as a kind. |

## 3. Political relationships: what was added

Six requests are in [curation/predicate-needs.json](curation/predicate-needs.json),
each with its precedents from the legacy registry and a shape under D-138
(proposed by Claude, confirmed by the curator 2026-11-22). `patronOf` is adopted
in registry v21, and `adoptedBy` with it as a predicate (D-170); the other four
stay `open`: the three acts are depicted as Events, never added as predicates,
and `amicusOf` waits on §7, choice 2.

| Request | Shape | Why |
|---|---|---|
| `patronOf` | state, time required | Patron and client (a person, a town, a community). The client's side is the same claim read the other way, so there is no `clientOf`. Legacy precedent: `PATRON_OF`, `CLIENT_OF`. |
| `amicusOf` | state, time required | Amicitia, political friendship with duties of support. Narrower than `alliedWith`. See §7, choice 2. |
| `prosecuted` | event | A trial: accuser, defendant, presiding magistrate as roles; the verdict as outcome. Covers charged, convicted, acquitted. |
| `adoptedBy` | state (D-170) | Person to Person, time required, its form (adoptio, adrogatio, by will) as a role Type; `childOf` stays for birth; the new gens is a separate `ofGens` claim (46). Proposed here as an event; D-170 had already made it a predicate, and the curator kept D-170. |
| `vetoed` | event | Intercessio: the vetoer and the measure blocked, as roles. |
| `proposedLaw` | event | A rogatio: proposer, assembly and law as roles; passage or rejection by `resultedIn`. |

For a developer: the shape `event` means a lens reading should **depict** an
Event with `participatedIn` and roles, not request a predicate; the reader shows
these to every lens reading (`open_requests_text`). Adding them through
`merge()` also refreshed the precedents and similar-request lists of nine older
open requests, as every collection does.

Not added:

- **Inimicitia.** `opposed` already covers "rivals or enemies, in politics or
  at war", with a required time. Only if the curator wants the Roman bond
  distinguished from any opposition does it need its own predicate.
- **`influenced`, `endorsed`, `mentorOf`, Person-to-Person `succeeded`.** Too
  loose to be evidenced by a passage. `influenced` is parked with motives (19,
  open item 6; 25 §6). Who succeeded whom in an office already follows from each
  holder's dated `heldPosition`.
- **The fields `authorityBasis`, `relationshipBasis` and
  direct / inferred / reconstructed.** The basis of authority is already a power
  Type (`heldPower`, `exercisedPower`). Attestation is computed from the voices,
  in words (D-033); how directly a source states something is the parked
  evidence-stance question (E8, 29 §10 item 5).

## 4. Laws, decrees and assemblies (decided 2026-11-22, D-171)

Decided by the curator: **a specific law is an entity of a new kind, `Law`; a
decree of the Senate is an entity of a second new kind, `Decree`; the
assemblies and the Senate are Groups of category `assembly`.** Built in
registry v21 (§4.4).

### 4.1 Law

A law such as the *lex Sempronia agraria* is a thing that lasts: it is
proposed, passed, cited, enforced, challenged and repealed, and the life of
Tiberius Gracchus turns on it. That makes it an entity, not an act. The acts
around it are Events.

Decided:

- A new entity kind **`Law`**: a lex, a plebiscitum.
- Its acts are Events with roles (D-138): the proposal (`proposedLaw`), the vote,
  the veto (`vetoed`), the repeal. The Event's outcome links the Law by
  `resultedIn`.
- Its standing is ordinary claims: `occurred` for the span it was in force, each
  source's dates an attributed claim, as for a Period or Polity.
- A debate about a law is a Question `about` the Law. What a law is about
  (land, citizenship, debt) has no predicate yet: `about` runs from a Question,
  and a subject-matter link for Laws waits until a reading needs one.
- Why not a Work: a Work is a text we cite as a source. A law's text, where it
  survives (an inscription), is a Work *of* the Law; the Law is the enactment.

### 4.2 Decree (senatus consultum)

A *senatus consultum* was the Senate's formal advice to a magistrate or the
people. A presiding magistrate put a question, the senators voted by moving to
one side, and if no consul or tribune vetoed the motion it became a decree,
written up and deposited in the aerarium. Under the Republic it was not law:
carrying it out was the magistrate's duty in custom, not in law, and a *lex* that
clashed with it won. In practice it was nearly always obeyed, above all on war,
finance, provinces and foreign affairs; under the emperors it became a way to
make law. (Sources the curator gave: Britannica, "senatus consultum"; Wikipedia,
"Senate of the Roman Republic", "Senatus consultum", "Senatus consultum
ultimum"; Bret Devereaux, ACOUP, "How to Roman Republic, Part IV: The Senate",
2023; Smith's *Dictionary of Greek and Roman Antiquities* (1875) on LacusCurtius.
Smith is public domain and quotable; the others are for orientation.)

Decided:

- A new entity kind **`Decree`**, not a Law, because the sources say it was not
  one. It takes the same acts and claims as a Law: proposed, voted, vetoed,
  `occurred`, `resultedIn`. The name fits imperial edicts and other bodies'
  decrees later.
- **A vetoed motion is a senatus auctoritas**: the recorded outcome of the vote
  Event, not a Decree.
- **A recurring form is a Type, each use a Decree.** The *senatus consultum
  ultimum* is a Type; its first use, in 121 BCE against Gaius Gracchus and
  Fulvius Flaccus, is a Decree of that Type, and a key event in the Gracchi lives.
- **A surviving text is a Work.** The SC de Bacchanalibus (186 BCE) survives in
  an inscription: the inscription is a Work, the decree is the Decree.

### 4.3 Assembly and the Senate

`electedBy` already runs from an Office to a Group, "the assembly". So the
assemblies (comitia centuriata, comitia tributa, concilium plebis) **and the
Senate** are **Groups with a new `groupCategory` value, `assembly`**, beside
`gens` (v20). A Person's seat in the Senate is `memberOf` with a time; a vote by
an assembly is an Event with the assembly as participant.

### 4.4 Built: registry v21 (2026-11-22)

- Kinds `Law` and `Decree`; `groupCategories` adds `assembly`.
- `occurred` reaches Law and Decree (the span in force); `resultedIn` may end at
  one (the vote that made it); `about` may end at one (a Question about a law).
- `involvedIn` extends from Object to Law and Decree: the measure in a vote,
  veto or repeal, always through a required role (vetoed measure, repealed
  law). `participatedIn` stays for agents (v14), so a law never "takes part".
- `instanceOf` extends from Group to Decree (a use of the senatus consultum
  ultimum, a Type).
- `patronOf` (§3), and from D-170 `adoptedBy` and an optional role (suffect,
  pro consule) and context (the province) on `heldPosition`.
- The two subtype labels in the operations file (13), the graph type
  (migration 018, re-applied), the connector, the entity reviewer, the export's
  kind words and colours, the explorer's kinds and placeholder icons, and docs
  02, 30 and 36. Test: `tests/test_registry_v21.py`.

The three acts (`prosecuted`, `vetoed`, `proposedLaw`) need no registry
change: a reader depicts them as Events with roles, and the role Types
(accuser, defendant, vetoer, proposer) are entities reviewed
before use, as for any role (v13).

## 5. Paths across domains, and how agents behave

### 5.1 The goal changes the reward

The review's main point stands: if the graph is for exploring paths, a claim that
joins two domains (purple stripe to the dye, dye to the murex) does more than
another claim inside one. This is already the purpose of 06 §13. What it changes
is how a specialist chooses what to read next, not what counts as a claim.

### 5.2 Do agents stay in their lane or travel?

The review offered three answers: a relay (each specialist stays in its field
and hands off), free wandering, and travelling with authority that falls with
distance from home. Ours is simpler, and follows rules we already have:

1. **Anyone may read the whole graph, any number of hops.** Reading changes
   nothing.
2. **Any agent may draft what the passage in front of it says,** whatever the
   field. If the political specialist is reading Pliny on purple, it drafts
   `madeFrom` from Pliny's words. Verbatim extraction needs no approval (curator,
   2026-11-13).
3. **Reasoning is reviewed, extraction is not,** and the reviewer is whichever
   specialist owns the question, not the field. Which modern species Pliny's
   *purpura* is, is an interpretive `about` claim on a Type (v19): the natural
   kinds lens reviews it however it was drafted.
4. **A path is never a claim.** It is a `PathHypothesis` whose hops each point
   to an accepted claim, a contested one, or a gap (06 §15).
5. **A hop with no claim becomes a gap**: a work order to the frontier planner
   (39 §7), which sends it to the specialist whose sources can answer it (39 §8,
   "test one hop").

So authority follows **the kind of evidence**, not the distance from home: a
quoted passage is as good four hops out as one, and an inference is reviewed
even on home ground.

### 5.3 Bridge leads

The review proposed rewarding agents for bridges. That would reward making
connections up. Instead, a specialist that meets an outward link in its reading
(a passage that mentions purple dye while it reads about senators' dress)
records a **bridge lead**: the passage, the two domains, and the hop it suggests.
A lead is a gap, not a claim; it goes to the planner like any other gap. Whether
leads need their own field in the lens output or are ordinary gaps with a
domain pair is §7, choice 3.

## 6. What we do not take from the review

- **Confidence percentages** ("politics 95 %, biology 20 %"): stored confidence
  numbers are ruled out (D-033); attestation is computed from the voices and
  stated in words.
- **A stored `bridgePotential` on predicates.** A ranking of paths is computed
  when a trace runs (06 §16), from predicate specificity and evidence; it is
  never stored on the predicate or the claim.
- **CRM as the native schema** (decided in 16 and 37; §2).
- **Person-to-Person predicates for acts** (`elected`, `convicted`, `exiled`,
  `declaredHostis`): acts are Events with roles (D-138). The legal acts join
  `prosecuted` as roles and outcomes of trials, or as Events of their own.
- **A separate "Roman politics" subsystem.** The political lens is a specialist
  like the others (39): a dossier, a grounding pack, questions it owns.

## 7. The curator's choices

1. ~~Confirm the six shapes~~: confirmed 2026-11-22, `adoptedBy` as a predicate
   per D-170; `patronOf` and `adoptedBy` adopted in v21.
2. **Amicitia:** its own predicate (`amicusOf`), or `alliedWith` as it is?
3. **Bridge leads:** a field of their own in the lens output, or ordinary gaps
   tagged with the two domains?
4. **Political lens dossier:** start it from the source-by-source targets the
   review suggests (Polybius VI on institutions, Cicero on auctoritas and
   legitimacy, Sallust on faction, Livy on offices and laws), with its central
   question being *what mechanism of authority does this passage describe?*
