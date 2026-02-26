# Backlink Entity Type: Beyond P31

## P31 (instance of)

**What it tells us:** Direct type of the entity — human, street, battle, work of art.

**Current use:** We aggregate P31 across harvest reports (globally and per anchor) to see entity type distribution. Junk anchors show street-heavy or photograph-heavy mixes; good anchors show domain-coherent types.

**Limitation:** P31 is the primary classifier but not the only useful signal.

---

## Other Properties That Could Help

### P279 (subclass of)

**Applies to:** Classes (the *values* of P31), not entities directly.

**What it tells us:** Type hierarchy. An entity has P31→Qx; Qx has P279→parent. We already use P279 in the harvester for class allowlist expansion (ancestors_map). For *distribution* purposes, P279 doesn't add a new axis — it enriches the P31 axis (e.g. "Q79007 is subclass of road" helps us group streets with other roads).

**Use case:** Roll up P31 counts by P279 ancestry — e.g. "all geographic features" = streets + buildings + settlements under a common ancestor.

---

### P361 (part of)

**Applies to:** Entities that are components of larger things.

**What it tells us:** Structural context — part of a work, part of a series, part of an organization, part of an event. An entity with P361→Q386724 (work) is likely a chapter, scene, or section. P361→Q23442 (organization) = subunit.

**Use case:** Distinguish *standalone* entities (no P361 or P361→broad container) from *fragments* (part of a specific work). Fragments may be less useful for graph expansion.

**Capture:** Would require adding P361 to the SPARQL or parsing entity claims. Not currently in harvest report.

---

### P106 (occupation)

**Applies to:** People (P31=Q5).

**What it tells us:** Role — historian, politician, soldier, artist. Per-anchor: "Government" pulling historians vs politicians vs educators gives different signals.

**Use case:** For people-heavy anchors, occupation distribution validates domain fit. "Families/Gentes" with many historians = prosopographic sources; "Government" with many educators = possible QID mismatch (education).

**Capture:** Entity claims; we fetch full entities but don't currently extract P106 distribution.

---

### P136 (genre)

**Applies to:** Creative works (books, films, etc.).

**What it tells us:** Fiction vs non-fiction, history vs biography vs novel. High fiction share may indicate noise (e.g. Robert Howard stories).

**Use case:** Flag anchors with high fiction/literary character share as potentially noisy.

**Capture:** Entity claims.

---

### P131 (located in)

**Applies to:** Geographic entities.

**What it tells us:** Place hierarchy — city, region, country. For places, P131 distribution shows *where* the backlinks are concentrated (e.g. all in Plauen vs spread across Roman world).

**Use case:** Geographic coherence check. "Late Republic" with P131→Plauen-heavy = wrong anchor (Plauen city).

**Capture:** We have P131 in the backlink *property* (what linked the entity to the seed) but not as entity's own P131 values. Would need to parse entity claims.

---

### P585 (point in time) / P580–P582 (start/end)

**Applies to:** Events, works, offices.

**What it tells us:** Temporal distribution. Are backlinks concentrated in the right period? "Roman Republic" entities from 1800s = modern scholarship; from -200 = ancient.

**Use case:** Temporal coherence. Anchors that pull mostly modern entities may need different handling.

**Capture:** Entity claims; we profile temporal precision but don't aggregate by period.

---

## Implementation Options

1. **Extend harvester:** Add optional property extraction (P106, P136, P361) to the report for accepted entities. Store per-entity and aggregate in analysis script.
2. **Post-hoc fetch:** Analysis script re-fetches entity claims for a sample — expensive, use sparingly.
3. **SPARQL extension:** Add OPTIONAL bindings for P106, P136 in the backlink query — only works for entities that have these properties; increases result size.

**Recommendation:** Start with P31 (done). Add P106 and P136 extraction to the harvester for *accepted* entities only (we already fetch them) — no extra API calls, just parsing the claims we have. That would enable "occupation distribution for people" and "genre distribution for works" in a future analysis run.
