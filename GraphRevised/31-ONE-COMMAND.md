# 31 — One Command: a Methodology for Any Subject

**Date:** 2026-10-16. **Status:** proposed for the curator's veto; nothing is
built. **Order:** after Chrystallum's account for the Battle of Actium
([29](29-EVENT-CENTRED-INQUIRY.md) §4, the last step of the event
methodology), before Hannibal ([19](19-SESSION-HANDOFF.md) §6).
**Builds on:** [29](29-EVENT-CENTRED-INQUIRY.md) (the event-centred run),
[25](25-LIVES-AND-PLAYGROUND.md) §10-13 (first contact, the one-hop rule,
enrichers by kind, agents choose the sources), [05](05-AGENT-BOUNDARIES.md)
(the boundaries that stand), backlog E1 and acceptance criterion 14 in
[04](04-IMPLEMENTATION-PLAN.md).

## 1. Why

The curator (2026-10-16): when development is done and a user wants to
explore ancient Greece, it should not take a person and an agent writing
scripts and logic. A command such as *Graph Alexander the Great* should
invoke one methodology, whatever the command names.

The Battle of Actium was built step by step. Most steps are already generic
code (a test enforces that reusable code names no source or subject), but
the run was held together by judgement between steps and by files written by
hand. That judgement is the methodology, and it is not yet written down
where the system can follow it.

## 2. What is generic already, and what is not

| Step | State |
|---|---|
| Wikidata first contact, harvest and budgeted expansion | generic ([harvest/](harvest)) |
| Wikipedia first contact | generic, by QID |
| Source registry, event source plan, inquiry builder | generic, for an event |
| Source briefs, passage finder, reader | generic, for an event |
| Gazetteer links for Places | generic |
| Phases: placing depicted events in a spine | generic code; the spine is a hand-written file ([curation/phases.json](curation/phases.json)) |
| Chrystallum's account | not built |

What breaks the single command:

1. **No front door.** Nothing turns a name into an identity and a plan. The
   concierge agent was retired with the SCA and SFA (25 §11); its job, scope
   and disambiguation, was left unbuilt (E1).
2. **No orchestrator.** Each step is its own command; someone runs them in
   order, reads the dry runs, and submits.
3. **Hand-written seeds.** The phases spine, the Subject, the actors list,
   the Works' forms: each is authored per subject.
4. **Events only.** The reader's scope rule is fixed for event inquiries
   (19 §7); a person's life is not broken into its events by any agent.
5. **One domain.** No second domain has run on the unchanged core
   (acceptance criterion 14).

## 3. The design

```text
graph "<anything>"
  1. resolve    the name to a Wikidata identity (search; the curator is asked only when ambiguous)
  2. scope      the scope decision (08): in scope, out of scope, or reframe; a broad subject
                becomes a constellation of narrower inquiries (07 §3)
  3. classify   the kind from the checked class table: Person, Event, Polity, Place, Concept, ...
  4. recipe     the recipe for that kind, read from data
  5. run        the recipe's steps in order, within a budget, each recorded
  6. present    everything visible at once, labelled; the curator promotes afterwards
```

### 3.1 Recipes are data

A recipe lists the steps for a kind, their order, what each consumes and
produces, its budget share, and its stopping rule. It names no subject. A
first set:

| Kind | Recipe |
|---|---|
| Event | first contact (Wikidata, Wikipedia) → surfaced entities → event source plan → builder (preserve, brief) → finder → reader → phases (spine discovered, §3.3) → account |
| Person | first contact → harvest and expansion (the person whole, then family: 25 §11) → **the life's events** (§3.2), each run as an Event recipe within the budget → the reader on the life's own sources (person scope) → the life's account |
| Polity, period, broad subject | first contact → a constellation of narrower inquiries (07 §3) proposed for the curator → each run by its own kind's recipe |

Enrichers by kind (25 §11) are steps any recipe may call when an entity of
their kind surfaces.

### 3.2 A life becomes its events

For a Person, an agent proposes the events of the life worth an inquiry:
from the harvest's claims (participant in, conflict), the Wikipedia article's
links, and the life's sources, ranked by how much the sources say, within a
budget. Each chosen event is run with the Event recipe; the rest stay
proposed entities, doors for later. The person scope that the reader lacks
(19 §7) is built here.

### 3.3 The spine is discovered

The phases of an event are proposed by an agent from its depicted events,
with a reason and the passages that show each phase, then placed as today.
`curation/phases.json` becomes agent output with the curator's veto, as the
reader's periods are discovered, never seeded (rule 13). A curator-decided
spine (Actium's) stays valid and is used when present.

### 3.4 Seeds become output

Every file now written by hand per subject is produced by a step and kept for
veto: the Subject and its headings (checked at the authority), the actors
for a polity, the Works' forms (from Wikidata, then the catalogue), the
phases. The curator edits or vetoes; the curator does not author.

### 3.5 The orchestrator

- **State outside the graph** (02 §1): a run file per command in `runs/`,
  with each step's inputs, outputs, cost, and status, so a run can stop and
  resume.
- **Dry run first, then submit, by rule.** Each step stores what its own dry
  run produced (as `--from-plan` does for the phases), so what was checked is
  what is stored. The checks are the deterministic validators; the curator is
  not asked between steps.
- **Budget.** A cost cap per command, split across steps; a step that would
  exceed its share stops and says what it would do next.
- **Curator touchpoints, only two:** an ambiguous identity at step 1, and
  promotion afterwards. Everything else is visible at once and vetoable.

### 3.6 The test: a second domain

*Graph Alexander the Great*, run from the single command with no file
written by hand. It meets acceptance criterion 14: Greek and Persian
sources, a different region of the gazetteer, a Person recipe, and a life's
battles as event inquiries. Its identity and sources are found at run time
(Wikidata, the registry's catalogues), never from memory (rule 17). Done
when the run ends with proposed entities, claims, phases, and an account for
at least one of his battles, and every hand-off between steps is in the run
file.

## 4. Order

1. Chrystallum's account for the Battle of Actium (19 §6 step 1d), so the
   Event recipe is complete.
2. This design, built in increments: the run file and orchestrator over the
   Event recipe (re-running Actium end to end as its test); the front door;
   the discovered spine; the Person recipe; then *Graph Alexander the Great*.
3. Hannibal and the other actors (25 §13), each through the command.

## 5. Open, for the curator

1. **Ambiguity.** Ask whenever there is more than one candidate, or only when
   no candidate clearly fits (a ranked list shown either way)?
2. **Budget.** The default cost cap per command, and whether the run asks
   before exceeding it.
3. **A life's events.** How many of a person's events become inquiries in
   the first run (all battles, or the agent's top few by sources)?
4. **Seeds.** Confirm that the actors list, the Subject, the Works' forms,
   and the phases become agent output with the curator's veto (§3.4).
5. **Accounts.** One per event in every run, or only on request?
