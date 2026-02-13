# LCC Automation Guide - Complete Step-by-Step Instructions

## Overview

This guide provides detailed instructions for processing Library of Congress Classification (LCC) schedules into hierarchical JSON structures.

## Prerequisites

- Python 3.7+
- `jq` command-line tool (optional, for JSON manipulation)
- Text editor
- LCC PDF schedules from Library of Congress

## File Structure

```
lcc-hierarchy-parser/
├── parse_lcc_outline.py          # Main automation script
├── lcc_processing_progress.md    # Status tracker
├── extracted_text/               # Raw text from PDFs
│   ├── lcc_ds-dx_raw.txt
│   ├── lcc_n_raw.txt
│   └── lcc_z_raw.txt
└── output/                       # Generated JSON hierarchies
    ├── lcc_DS-DX_hierarchy.json
    ├── lcc_N_hierarchy.json
    └── lcc_Z_hierarchy.json
```

## Step-by-Step Workflow

### Step 1: Extract Text from PDF

**Manual Process (for now):**

1. Open LCC PDF in a viewer
2. Navigate to the outline/table of contents section
3. Select all outline text (Ctrl+A or Cmd+A)
4. Copy to clipboard
5. Paste into a text editor
6. Save as `extracted_text/lcc_[class]_raw.txt`

**Expected format:**
```
DS1-937     History of Asia
DS5.95-10     Description and travel
DS11          Antiquities
DS13-28       Ethnography
```

**Quality checks:**
- One entry per line
- Code (with range) followed by label
- Indentation preserved (helps with manual review)
- No page numbers or headers mixed in

### Step 2: Run Parser

```bash
python parse_lcc_outline.py \
    extracted_text/lcc_ds-dx_raw.txt \
    -o output/lcc_DS-DX_hierarchy.json \
    --validate \
    --verbose
```

**Output:**
```
Parsing extracted_text/lcc_ds-dx_raw.txt...
Found 403 entries
Building hierarchy...
Created 403 nodes
Validating structure...
✅ Validation passed

Statistics:
  Roots: 4
    - DS1-937: History of Asia (38 children)
    - DT1-3415: History of Africa (25 children)
    - DU1-950: History of Oceania (7 children)
    - DX101-301: History of Romanies (0 children)
  Max depth: 5
  Prefixes: DS, DT, DU, DX
  
  Nodes by prefix:
    DS: 126
    DT: 237
    DU: 39
    DX: 1

✅ Done! Wrote 403 nodes to output/lcc_DS-DX_hierarchy.json
```

### Step 3: Inspect Output

**View structure:**
```bash
# See first few nodes
jq '.[:3]' output/lcc_DS-DX_hierarchy.json

# View all roots
jq '.[] | select(.primary_parent == null)' output/lcc_DS-DX_hierarchy.json

# Count nodes
jq 'length' output/lcc_DS-DX_hierarchy.json
```

**Verify node structure:**
```bash
jq '.[0]' output/lcc_DS-DX_hierarchy.json
```

Should show:
```json
{
  "id": "DS1-937",
  "code": "DS1-937",
  "prefix": "DS",
  "start": 1.0,
  "end": 937.0,
  "label": "History of Asia",
  "note": null,
  "primary_parent": null,
  "secondary_parents": [],
  "children": ["DS5.95-10", "DS11", ...],
  "depth": 0,
  "child_count": 38
}
```

### Step 4: Update Progress Tracker

Edit `lcc_processing_progress.md`:

```markdown
- [x] **DS-DX**: Asia, Africa, Oceania, Romanies
  - Status: ✅ Complete
  - Nodes: 403
  - File: `output/lcc_DS-DX_hierarchy.json`
  - Processed: 2026-02-04
```

### Step 5: Repeat for Other Classes

Process N (Fine Arts) and Z (Bibliography) next:

```bash
# N - Fine Arts
python parse_lcc_outline.py \
    extracted_text/lcc_n_raw.txt \
    -o output/lcc_N_hierarchy.json \
    --validate --verbose

# Z - Bibliography
python parse_lcc_outline.py \
    extracted_text/lcc_z_raw.txt \
    -o output/lcc_Z_hierarchy.json \
    --validate --verbose
```

### Step 6: Merge All Hierarchies

Once all classes are processed:

```bash
jq -s 'add' output/lcc_*_hierarchy.json > lcc_complete_hierarchy.json
```

**Verify merged file:**
```bash
# Count total nodes
jq 'length' lcc_complete_hierarchy.json

# Check prefixes
jq 'map(.prefix) | unique | sort' lcc_complete_hierarchy.json

# Find all roots
jq 'map(select(.primary_parent == null)) | length' lcc_complete_hierarchy.json
```

## Troubleshooting

### Issue: "Could not parse code"

**Symptoms:**
```
Warning: Could not parse code 'DS11.A1-.A3' - skipping
```

**Causes:**
- Unsupported notation format
- Typo in extracted text

**Solutions:**
1. Check if it's a Cutter range - pattern should handle it
2. Manually fix in input text file
3. Report pattern to improve parser

### Issue: "Orphaned parent reference"

**Symptoms:**
```
⚠️  Found 3 validation errors:
  - Orphaned parent: DS730-731 → DS700-799
```

**Causes:**
- Parent range not in input file
- Parsing error created invalid parent link

**Solutions:**
1. Check if parent range exists in source PDF
2. Add missing parent to input text
3. Rerun parser

### Issue: "Depth inconsistency"

**Symptoms:**
```
Depth inconsistency: DS733-779.32 (depth 3) → parent DS701-799.9 (depth 1)
```

**Causes:**
- Bug in depth calculation
- Cycle in parent-child relationships

**Solutions:**
1. Check for cycles using visualization
2. Report to developer for algorithm fix

### Issue: Empty children array expected

**Symptoms:**
Leaf nodes have empty `children: []` arrays

**This is correct behavior** - leaf nodes naturally have no children.

## Advanced Usage

### Generate Tree Visualization

```bash
# Simple ASCII tree (first 2 levels)
jq -r '.[] | select(.depth <= 1) | 
       ("  " * .depth) + "└─ " + .code + " " + .label' \
       output/lcc_DS-DX_hierarchy.json | head -50
```

Output:
```
└─ DS1-937 History of Asia
  └─ DS5.95-10 Description and travel
  └─ DS11 Antiquities
  └─ DS13-28 Ethnography
```

### Find Deepest Branches

```bash
jq '[.[] | {code, label, depth}] | sort_by(.depth) | reverse | .[0:10]' \
   output/lcc_DS-DX_hierarchy.json
```

### Extract Specific Subtree

```bash
# Get all descendants of China (DS701-799.9)
jq '
  . as $all |
  "DS701-799.9" as $root_id |
  
  # Recursive function to get all descendants
  def descendants($id):
    $all[] | select(.primary_parent == $id) |
    ., (descendants(.id));
  
  # Get root and all descendants
  [$all[] | select(.id == $root_id)], [descendants($root_id)]
' output/lcc_DS-DX_hierarchy.json > china_hierarchy.json
```

### Count Nodes by Depth

```bash
jq 'group_by(.depth) | 
    map({depth: .[0].depth, count: length})' \
    output/lcc_DS-DX_hierarchy.json
```

Output:
```json
[
  {"depth": 0, "count": 4},
  {"depth": 1, "count": 89},
  {"depth": 2, "count": 201},
  {"depth": 3, "count": 87},
  {"depth": 4, "count": 19},
  {"depth": 5, "count": 3}
]
```

## Quality Assurance Checklist

Before considering a class "complete":

- [ ] Input text file formatted correctly
- [ ] Parser runs without warnings
- [ ] Validation passes (no errors)
- [ ] Statistics look reasonable
  - [ ] Root count matches expected (usually 1-5)
  - [ ] Max depth reasonable (usually 2-6)
  - [ ] Node count matches source outline
- [ ] Spot check: sample nodes have correct parents
- [ ] JSON file valid (loads in jq)
- [ ] Progress tracker updated

## Performance Notes

- **Parse time**: <1 second for 400 nodes
- **Memory**: ~5 MB for 400 nodes
- **Scalability**: Tested up to 400 nodes, estimated <5 seconds for full LCC (~5000 nodes)

## Next Steps After Data Collection

1. **Merge all hierarchies** into single file
2. **Create Neo4j import script**
3. **Load into Neo4j** for graph querying
4. **Build agent instantiation heuristic**
5. **Implement LangGraph controller**

See `README_LCC_PROJECT.md` for complete roadmap.

## References

- Library of Congress Classification: https://www.loc.gov/aba/cataloging/classification/
- Free LCC Schedules: https://www.loc.gov/aba/publications/FreeLCC/freelcc.html
- Project README: `README_LCC_PROJECT.md`
- Progress Tracker: `lcc_processing_progress.md`
