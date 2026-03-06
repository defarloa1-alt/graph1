# SFA — Subject Facet Agent

Proposes SubjectConcepts and scopes federated views for facets (Political, Military, etc.).

## What it does

1. **propose** — Consumes SCA landscape output, proposes concrete SubjectConcepts for a facet. Output: `output/sfa_proposals/`. POLITICAL has full evidence (DPRR magistracies, LCC, WorldCat).
2. **scope** — Reasons over full federated export, produces facet-scoped list. Output: `output/sfa_scoped/`.

## Usage

```bash
# From project root

# Propose SubjectConcepts for Political facet (requires SCA landscape first)
python -m scripts.agents.sfa propose --facet POLITICAL --seed Q17167

# Scope federated view for Political facet (requires federated export first)
python -m scripts.agents.sfa scope --facet POLITICAL --seed Q17167
```

## Package structure

```
scripts/agents/sfa/
├── __init__.py              # Exports propose, scope
├── subject_concept_proposer.py  # Propose SubjectConcepts (Political full evidence)
├── scope_federated_view.py     # Scope federated view for facet
├── cli.py                      # argparse + main
├── __main__.py                 # python -m entry point
└── README.md
```

## Pipeline

1. Run SCA landscape: `python -m scripts.agents.sca landscape Q17167 --taxonomy ... --lateral ...`
2. Run SFA propose: `python -m scripts.agents.sfa propose --facet POLITICAL`
3. (Optional) Run SFA scope: `python -m scripts.agents.sfa scope --facet POLITICAL`
4. (Optional) Enrich with bibliography: `python scripts/agents/sfa_enrich_scoped_with_bibliography.py --input output/sfa_scoped/POLITICAL_Q17167_*.json`

## Requirements

- `ANTHROPIC_API_KEY` in `.env`
- `pip install anthropic`
- Neo4j (for DPRR magistracy data in Political evidence)
