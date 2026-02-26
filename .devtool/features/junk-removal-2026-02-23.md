---
id: "junk-removal-2026-02-23"
status: "todo"
priority: "high"
assignee: null
dueDate: null
created: "2026-02-24T00:43:36.639Z"
modified: "2026-02-24T13:18:13.230Z"
completedAt: null
labels: ["Core"]
order: "a3"
---
# junk removal

## **1. Harvester P31 denylist**

**Location:** scripts/tools/wikidata_backlink\_[harvest.py](http://harvest.py)

- **Mechanism:** --p31-denylist-qid (repeatable) rejects candidates whose P31 matches any listed QID.


- **Default:** No denylist; p31_denylist is empty unless passed explicitly.


- **Q4167410 (Wikimedia disambiguation page):** Not in the default denylist.

**Current reports:** p31_denylist: \[\] in harvest reports.

---

## **2. Disambiguation filtering status**

AspectStatus**Q4167410 (Wikimedia disambiguation page**)Not filtered by default**Harvester support**Present via --p31-denylist-qid**harvest_all_anchors**Does not pass denylist; no extra_args for it**Documentation**ARCHITECTURE\_[IMPLEMENTATION.md](http://IMPLEMENTATION.md) mentions P31 denylist as optional

---

## **3. Other junk types (not filtered)**

Likely candidates for a denylist:

- **Q4167410** – Wikimedia disambiguation page


- **Q13442814** – scholarly article (often low value for entity graph)


- **Q17362920** – Wikimedia list article


- **Q1980247** – Wikimedia category

---

## **4. Duplicate cleanup**

**Location:** cleanup_duplicates.cypher

- **Purpose:** Remove duplicate Entity nodes (same QID imported more than once).


- **Status:** Script exists; QA found 50 duplicates (20 QIDs imported twice).


- **Action:** Run the script and add uniqueness constraints to avoid future duplicates.

---

## **5. LCSH disambiguation (Subjects)**

**Location:** Subjects/subject [decisions.md](http://decisions.md)

- **Scope:** LCSH geographic subdivision variants (e.g. sh00000016 vs sh00000016-781).


- **Approach:** Treat as variants, not duplicates; collapse into primary subject.


- **Status:** Documented; implementation not verified.

---

## **6. Architecture doc cleanup**

**Location:** .devtool/features/[arch-doc-cleanup-2026-02-23.md](http://arch-doc-cleanup-2026-02-23.md)

- **Status:** Todo – “ontology not updated probably others”.


- **Scope:** General architecture doc cleanup.

---

## **Summary and recommendations**

AreaStatusAction**Disambiguation pages (Q4167410**)Not filteredAdd --p31-denylist-qid Q4167410 to harvester invocations or a default denylist**Other junk types**Not filteredDefine and add to denylist if desired**Duplicate entities**Script existsRun cleanup_duplicates.cypher and add constraints**harvest_all_anchors**No denylist wiringAdd extra_args support for --p31-denylist-qid

---

## **Minimal change to filter disambiguation pages**

Add a default denylist in wikidata_backlink\_[harvest.py](http://harvest.py):

DEFAULT_P31_DENYLIST = {"Q4167410"}  # Wikimedia disambiguation page

Or pass it from harvest_all\_[anchors.py](http://anchors.py):

cmd += \["--p31-denylist-qid", "Q4167410"\]