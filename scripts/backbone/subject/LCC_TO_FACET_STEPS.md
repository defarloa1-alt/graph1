# LCC → Facet Mapping: Step-by-Step Plan

**Domain:** Roman Republic (LCC, LCSH, Wikidata, Wikipedia, FAST, MARC, WorldCat)

---

## Step 1: LLM batch mapping (this script)

- **Input:** `output/nodes/lcc_roman_republic.csv` (143 classes)
- **Process:** Batch call OpenAI or Perplexity; map each LCC class to facet(s) + material_type
- **Output:** `output/subject_concepts/lcc_facet_mappings.json`
- **Review:** Human spot-check before loading

## Step 2: Run and review

```bash
python scripts/backbone/subject/map_lcc_to_facets_llm.py --provider openai
# or --provider perplexity
```

Inspect `output/subject_concepts/lcc_facet_mappings.json`. Fix any obvious errors.

## Step 3: Load into Neo4j

Create/update `(:LCC_Class)-[:MAPS_TO_FACET {weight}]->(:Facet)` edges.
Replace or augment heuristic mappings from `load_lcc_nodes.py`.

## Step 4 (future): SCA tool

Wrap as `lcc_classification_agent` tool for SCA to invoke on demand.
