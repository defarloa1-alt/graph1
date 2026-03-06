# Biographic Backlink Reversal Plan

After `--all` completes, we want to **reverse** the backlink approach: instead of fetching backlinks inline during person harvest (which causes SPARQL timeouts on heavy persons), run backlinks as a **separate pass** using existing traversal code.

## Current State

### 1. Biographic agent (inline, per-person)
**Location:** `scripts/agents/biographic/agent.py` → `fetch_backlinks(qid)`

- **When:** During `harvest_person()` — step [3/3]
- **How:** Single SPARQL query per person: `?item ?pred wd:{qid}` with `VALUES ?pred { wdt:P22 wdt:P25 wdt:P26 ... }`
- **Predicates:** Fixed `BACKLINK_PREDICATE_MAP` (P22, P25, P26, P3373, P40, P1038, P3448, P1066, P802, P737, P710, P664, P748, P1308, P488, P6, P112, P138, P176, P1344)
- **Output:** Writes directly to `BIO_CANDIDATE_REL` via `WRITE_BACKLINK_CANDIDATE`
- **Problem:** SPARQL timeouts on persons with many backlinks (famous people)

### 2. wikidata_backlink_harvest (standalone, SubjectConcept seeds)
**Location:** `scripts/tools/wikidata_backlink_harvest.py`

- **Designed for:** SubjectConcept seeds (e.g. Q1048 Roman Republic), not persons
- **How:** `?source ?prop ?target` with property allowlist, class allowlist, P31/P279 filtering
- **Output:** JSON report (`{seed}_backlink_harvest_report.json`) — no Neo4j write
- **Features:** SYS_Threshold integration, federation scoping, datatype profiling, budget caps
- **Property allowlist:** Configurable; discovery mode uses `DISCOVERY_PROPERTY_BOOTSTRAP` (P710, P1441, P138, P112, P737, P828, P31, P279, etc.)

### 3. Legacy extract_wikidata_backlinks
**Location:** `scripts/legacy/extract_wikidata_backlinks.py`

- **Query:** `?item ?prop wd:{qid}` — **unrestricted** (any property)
- **Loads:** All `Entity` nodes from Neo4j
- **Output:** JSON file only
- **Issues:** Hardcoded credentials, unbounded query (timeout risk on famous people)

---

## Reversal Strategy

**Decouple backlinks from harvest:**
1. Biographic harvest: bio anchors + events + marriages only (no backlinks)
2. Separate backlink pass: traverse Wikidata backlinks for Person QIDs, write to graph

**Options for the backlink pass:**

| Option | Pros | Cons |
|-------|-----|------|
| **A. Extend wikidata_backlink_harvest** | Reuse thresholds, class filtering, report format | Designed for SubjectConcepts; person-specific routing (BacklinkRouting) lives in bio agent |
| **B. New person_backlink_harvest.py** | Clean separation, person-specific predicates + BacklinkRouting | Duplicate SPARQL logic |
| **C. Extract shared module** | Single backlink fetch logic; bio + subject both use it | Refactor effort |

---

## Recommended: Option B + Shared Fetch

1. **Add `scripts/agents/biographic/backlink_harvest.py`** (or `scripts/tools/person_backlink_harvest.py`):
   - Accept `--persons` (list) or `--from-graph` (MATCH Person WHERE bio_harvested_at IS NOT NULL)
   - Use `BACKLINK_PREDICATE_MAP` predicates (same as current agent)
   - Reuse `_fetch_backlink_rows` pattern from wikidata_backlink_harvest (SPARQL with retries, limits)
   - Load `BacklinkRouting` from graph (decision_loader) for sfa_queue/edge_type
   - Write to `BIO_CANDIDATE_REL` (same Cypher as agent)
   - Run as batch: `python -m scripts.agents.biographic.backlink_harvest --from-graph --limit 100`

2. **Update biographic agent:**
   - Add `--no-backlinks` (or make it default when running full harvest)
   - Document: "Run backlink_harvest separately after harvest"

3. **Optional: Use Wikidata API for backlinks?**
   - Wikidata has no direct "backlinks" API. SPARQL is the only way.
   - Mitigations: lower LIMIT, retries, batch persons with sleep, capture timeouts to `biographic_failures.jsonl` for retry

---

## Code to Review/Update

| File | Action |
|------|--------|
| `scripts/agents/biographic/agent.py` | Add `--skip-backlinks` (or default True); remove inline fetch when skipped |
| `scripts/agents/biographic/cli.py` | Add `--backlinks` flag to run backlink pass, or separate command |
| `scripts/tools/wikidata_backlink_harvest.py` | Consider: add `--seed-type person` to use BACKLINK_PREDICATE_MAP + BacklinkRouting when seed is Person |
| `scripts/legacy/extract_wikidata_backlinks.py` | Remove hardcoded creds; use .env; restrict to property allowlist; could be basis for person pass |

---

## Implementation Checklist

- [x] Create `scripts/agents/biographic/backlink_harvest.py`
- [x] Reuse BACKLINK_PREDICATE_MAP + BacklinkRouting from bio agent
- [x] Add `--from-graph` to iterate Person nodes with bio_harvested_at
- [x] Add `--limit`, `--qids`, `--dry`, `--verbose`
- [x] Write to BIO_CANDIDATE_REL (same Cypher)
- [x] Log timeouts to biographic_failures.jsonl for retry
- [x] Update biographic agent: default skip_backlinks=True
- [x] Add `--backlinks` to main CLI for inline backlinks when desired

## Usage

```bash
# Phase 1: Harvest bio + events + marriages (no backlinks)
python -m scripts.agents.biographic --all --limit 25

# Phase 2: Backlink harvest (separate pass)
python -m scripts.agents.biographic.backlink_harvest --from-graph --limit 25 --verbose

# Or with explicit QIDs
python -m scripts.agents.biographic.backlink_harvest --qids Q125414 Q1048 --dry -v
```
