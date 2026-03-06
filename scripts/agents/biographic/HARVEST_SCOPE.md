# Biographic Agent — What We Capture

## Data source: Wikidata only

The Biographic agent fetches from **Wikidata** (query.wikidata.org/sparql). It does **not** query LCSH, LCC, WorldCat, or other bibliographic sources.

---

## What IS captured (and written to graph)

| Wikidata property | Stored as | Notes |
|-------------------|-----------|-------|
| P569 (birth date) | birth_year, BORN_IN_YEAR→Year | Parsed to integer year |
| P570 (death date) | death_year, DIED_IN_YEAR→Year | Parsed to integer year |
| P19 (birth place) | birth_place_qid, BORN_IN_PLACE→Place | QID + label; Pleiades resolved when available |
| P20 (death place) | death_place_qid, DIED_IN_PLACE→Place | Same |
| P119 (burial place) | burial_place_qid, BURIED_AT→Place | Same |
| P509 (cause of death) | cause_of_death_qid | QID only |
| P214 (VIAF) | viaf_id | Authority ID |
| P227 (GND) | gnd_id | Authority ID — stored when present |
| P244 (LCNAF) | lcnaf_id | Authority ID — stored when present |
| P1415 (OCD) | ocd_id | Oxford Classical Dictionary — stored when present |
| P3348 (Nomisma) | nomisma_id | Numismatic ID |
| P607 (conflict) | PARTICIPATED_IN→Event | Requires start_date; we use person's birth/death year as proxy |
| P793 (significant event) | PARTICIPATED_IN→Event | Same |
| P1344 (participated in) | PARTICIPATED_IN→Event | Same |
| P166 (award) | PARTICIPATED_IN→Event | Same |
| P26 (spouse) + qualifiers | SPOUSE_OF with start_year, end_year, place_qid | P580, P582, P1545, P1534, P2842 |
| Backlinks (P22, P25, P26, etc.) | Entity stubs + SFA_QUEUE edges | Items that reference this person |

---

## What is NOT captured

- **LCSH** (Library of Congress Subject Headings) — not on Wikidata person entities
- **LCC** (Library of Congress Classification) — not on Wikidata person entities
- **LCSH/LCC temporal** — would come from bibliographic records, not from Wikidata
- **GND/OCD resolution** — we store the IDs only; no lookup to fetch labels or related data

---

## GND, OCD, LCNAF — "not implemented"?

We **do** store these when Wikidata has them:
- `gnd_id`, `ocd_id`, `lcnaf_id` are written to Person nodes
- A "-" in the log means Wikidata returned no value for that person

"Not implemented" might mean: we don't *resolve* them (e.g. fetch GND record, map OCD to a concept). We only persist the raw IDs for linking.

---

## Temporal backbone

- **Year nodes** — BORN_IN_YEAR, DIED_IN_YEAR link Person→Year
- **Event nodes** — PARTICIPATED_IN links Person→Event; Event requires `start_date` (schema constraint)
- We derive `start_date` from the person's birth_year or death_year when the event has no date

---

## Known issues

1. **504 Gateway Timeout** — Wikidata can time out; we retry with backoff
2. **Event constraint** — Event nodes require start_date; we skip events when person has no birth/death year
3. **Blank spouse** — When spouse is a Wikidata blank node (genid), we display the URI; no human label
