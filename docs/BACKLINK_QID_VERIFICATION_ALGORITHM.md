# Backlink Harvest: QID Verification Algorithm

## Problem

Harvest reports showed junk in the delta (entities dropped by the 500 cap):
- **Q3952** (labeled "Late Republic") → German streets, Plauen city
- **Q8434** (labeled "Government") → Education, modern academics
- **Q207640** (labeled "Public ritual") → Robert Howard fiction, Conan stories
- **Q2067294** (labeled "Republican ideals") → Alan Rufus (Norman magnate)

## Root Cause: QID Mismatch

Our anchor labels did not match Wikidata's actual entities:

| Our label | Our QID | Wikidata actual | Property path |
|-----------|---------|-----------------|---------------|
| Late Republic (periodization) | Q3952 | **Plauen, Germany** (city) | P131 (located in) |
| Government and Constitutional Structure | Q8434 | **Education** | P101, P921, etc. |
| Public ritual, auspices, legitimacy | Q207640 | **Robert E. Howard** (author) | P921 (main subject) |

The harvest is correct; the anchor file had wrong QIDs.

## Algorithm: Verify Before Harvest

1. **Pre-harvest**: For each anchor, fetch Wikidata label for the QID.
2. **Compare**: If `wikidata_label` does not semantically match `anchor_label`, flag as suspect.
3. **Resolve**: Curate correct QID or remove anchor before harvesting.

### Correct QIDs (verified 2026-02)

| Intended concept | Wrong QID | Correct QID | Wikidata label |
|------------------|-----------|-------------|----------------|
| Late Republic (periodization) | Q3952 | **Q2815472** | Late Roman Republic |
| Government and Constitutional Structure | Q8434 | **Q7188** | government |
| Public ritual, auspices, legitimacy | Q207640 | **Q337547** | ancient Roman religion |
| Republican ideals (virtus, mos maiorum, liberty) | Q2067294 | **Q1887031** | Mos maiorum |

## Implementation

- **Script**: `scripts/analysis/verify_anchor_qids.py` — fetches Wikidata labels and reports mismatches.
- **Fix**: Update `subject_concept_anchors_qid_canonical.json` and `subject_concept_hierarchy.json` with correct QIDs.
- **Re-harvest**: After fixing, remove old reports for wrong QIDs from `output/backlinks/` and from `harvest_progress.json`, then run `harvest_all_anchors.py` — the new QIDs (Q2815472, Q7188, Q337547) will be harvested fresh.

## Why Q899409 and Q2277 Are Valuable

- **Q899409** (Families, Gentes): Correct QID; delta contains Roman gentes (Horatia, Aternia, etc.).
- **Q2277** (Transition to Empire): Correct QID; delta is mixed but includes relevant entities (battles, Roman-Sasanian wars).

These anchors have correct QIDs; their deltas are worth expanding (e.g. raise cap for Q899409).
