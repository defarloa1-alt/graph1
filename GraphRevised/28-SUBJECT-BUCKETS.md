# 28 — Subject Buckets

**Date:** 2026-10-14. **Status:** agreed with the curator; nothing built yet.
**Changes:** [02](02-GRAPH-MODEL.md) §1 (Subject), which said most Entities have no Subject of their own.
**Builds on:** [25](25-LIVES-AND-PLAYGROUND.md) §8 (Subjects and library headings), [24](24-PERIODS-AND-TRANSFORMATION.md) §2 (membership computed, not asserted), [docs/#vision.md](docs/%23vision.md) (the subject backbone).
**Order:** after the gazetteer ([27](27-GAZETTEER.md)).

## 1. Decision

**Every entity sits in at least one subject bucket** (curator, 2026-10-14).
A bucket is conceptual, not bibliographic: it answers "what is this part
of?", not "what has been written about it?". Bibliography stays where 25 §8
put it: on the Subject, through its headings, for the "Read more" list.

A Subject is still created intentionally, and it is still never a shadow of
an Entity. What changes is coverage: the buckets together cover everything.

## 2. What a bucket is

A **Subject** node in our own hierarchy:

- **Anchored** to a library heading where one exists: LCSH and FAST as
  AuthorityRecords with role `subject_access`, checked at the authority, the
  label read from the record, never typed (25 §8).
- **Ordered** by `(:Subject)-[:BROADER]->(:Subject)`, read from the headings'
  broader terms where they exist, otherwise proposed by an agent with a
  reason. A bucket may have **several parents**: a graph is not a shelf.
- **About something** through the existing
  `(:Subject)-[:HAS_SUBJECT_FOCUS]->(:Entity)`: the Event *Second Punic War*
  is what happened; the Subject *Punic War, 2nd* is the bucket around it.

Worked case (headings checked at id.loc.gov and FAST on 2026-10-14; the
broader links are to be read from LC's records when built, not yet checked):

```text
Punic wars                         LCSH sh85109114 · FAST fst01084102
├── Punic War, 1st, 264-241 B.C.   LCSH sh85109111
├── Punic War, 2nd, 218-201 B.C.   LCSH sh85109112   ← Hannibal, Scipio Africanus
└── Punic War, 3rd, 149-146 B.C.   LCSH sh85109113
```

## 3. How an entity gets into a bucket

1. **Computed from claims, not stored.** An entity is in a bucket when a
   live claim ties it to the bucket's focus, or to an event that is `partOf`
   the focus (followed through `partOf`). "Hannibal commanded at Cannae" and
   "Cannae part of the Second Punic War" put Hannibal in *Punic War, 2nd*.
   The bucket needs no quotation of its own: it inherits from claims that
   have one, and it cannot go stale.
2. **Which predicates carry membership is data**, in the predicate registry,
   never code. First set: `participatedIn`, `commanded`,
   `heldAuthorityOver`, `servedUnder` (through its context), and `partOf`
   between Events.
3. **The most specific bucket wins.** Hannibal is placed in the 2nd war, not
   directly in *Punic wars*; he is under *Punic wars* through `BROADER`.
4. **Stored only where no claim can carry it.** An agent or the curator
   places the entity with a written reason; the placement is visible at once
   (25 decision 2) and the curator promotes it.

## 4. Wikidata

Wikidata never decides membership. **P921 (main subject) is not used**: it
sits on Works and is bibliographic. Wikidata is used three narrower ways:

1. **Anchors:** an event's own LC (P244) and FAST (P2163) identifiers name
   its bucket's heading. Since migration 007 a harvested LC subject
   identifier lands on the same LCSH record the bucket uses.
2. **Structure:** "part of" and "has part" between events arrive as proposed
   `partOf` claims through the harvest, as today.
3. **People:** "conflict" (P607) and "participant in" (P1344) arrive as
   proposed participation claims, which place people only through §3.

## 5. Legacy lessons

The legacy graph scoped every person to *prosopography* and every place to
*archaeology*; bulk ties carry no information. Hence: no generic buckets, the
most specific bucket, several allowed, every stored placement with a reason.
Buckets are not facets: facets stay lenses ([25](25-LIVES-AND-PLAYGROUND.md) §12).

## 6. Open

- Which predicates carry membership for Places, Works, and Types (Rome would
  sit in every war's bucket through `occurredAt`).
- Buckets where no heading exists (Roman institutions are thin in FAST): our
  own Subjects, labelled as ours.
- How a card shows buckets ("In: Punic War, 2nd").
