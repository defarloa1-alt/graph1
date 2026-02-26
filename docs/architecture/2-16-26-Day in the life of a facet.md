#Day in the life of a facet
A newly instantiated SubjectFacetAgent (SFA) has a very structured “day.” It always moves through schema introspection → state loading → federation bootstrap → ontology proposal (via SCA) → training, with validation and logging wrapped around everything.

***

## 1. Wake‑up and self‑orientation

1. **Instantiate agent via factory**

```python
from scripts.agents.facetagentframework import FacetAgentFactory
factory = FacetAgentFactory()
agent = factory.get_agent("military")  # or any facet
```

2. **Schema introspection (Step 1)**  
   - Call `introspect_nodelabel("SubjectConcept")` to see required properties, tier, etc. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/81085e9a-39e1-47af-bf4e-42957bbe0252/STEP_1_COMPLETE.md)
   - Call `get_layer25_properties()` to know which Wikidata properties (P31, P279, P361, etc.) are allowed for hierarchy traversal. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/81085e9a-39e1-47af-bf4e-42957bbe0252/STEP_1_COMPLETE.md)
   - Optionally `discover_relationships_between("Human","Event")` to recall valid edge types (e.g., `PARTICIPATED_IN`). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/81085e9a-39e1-47af-bf4e-42957bbe0252/STEP_1_COMPLETE.md)

This gives the SFA “what is allowed” at the schema level before touching data.

***

## 2. Session start: load current state

3. **State introspection (Step 2):**

```python
context = agent.get_session_context()
```

- Learns: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b2ea8c97-b349-4d97-9cc0-9a710730d6d6/STEP_2_COMPLETE.md)
  - Sample of current `SubjectConcept` nodes and relationships in its domain.  
  - Its own pending claims, recent promotions, and track record.  
  - Meta‑schema version sanity check.

4. **Subgraph and provenance checks**  
   - `get_subjectconcept_subgraph(limit=200)` to see if a planned anchor node (e.g., Roman Republic) already exists. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b2ea8c97-b349-4d97-9cc0-9a710730d6d6/STEP_2_COMPLETE.md)
   - If it finds an existing node, `find_claims_for_node(nodeid)` and `get_node_provenance(nodeid)` to avoid duplicate claims. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b2ea8c97-b349-4d97-9cc0-9a710730d6d6/STEP_2_COMPLETE.md)

Now the SFA knows “what already exists” and “what I myself have done before.”

***

## 3. Initialize mode: bootstrap a domain from Wikidata

5. **Switch to Initialize mode and start logging (Step 5)**

```python
result_init = agent.execute_initializemode(
    anchor_qid="Q17167",  # Roman Republic
    depth=2,
    autosubmitclaims=False,
    uicallback=ui_log_callback
)
```

- Workflow: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5b19dcd3-a9ee-42b9-b9ea-c638e20ee4a9/STEP_5_COMPLETE.md)
  - Fetch Q17167 from Wikidata (`fetch_wikidata_entity`).  
  - Auto‑enrich/create root `SubjectConcept` node via `enrich_node_from_wikidata` (label, description, aliases, statementcount). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4fcddbd6-a04f-46da-8376-d5a132e53b7d/STEP_3_COMPLETE.md)
  - Validate completeness (Step 3.5), log a completeness score; abort if below threshold. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5b19dcd3-a9ee-42b9-b9ea-c638e20ee4a9/STEP_5_COMPLETE.md)
  - Enrich with CIDOC‑CRM alignment (`enrich_with_ontology_alignment`), storing e.g. `cidoccrm_class`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a4714de-a0de-4427-8f35-64d297ab7766/STEP_4_COMPLETE.md)
  - Traverse P31/P279/P361 hierarchies with `discover_hierarchy_from_entity` at chosen depth, collecting related entities and relationships. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4fcddbd6-a04f-46da-8376-d5a132e53b7d/STEP_3_COMPLETE.md)
  - Turn those into claims via `generate_claims_from_wikidata` with base confidence 0.90, tagged to this facet, and auto‑enriched with CRMinf belief metadata. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a4714de-a0de-4427-8f35-64d297ab7766/STEP_4_COMPLETE.md)
  - Optionally auto‑submit high‑confidence claims.  
  - Log all actions via `AgentLogger` (INITIALIZE, REASONING, QUERY events). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5b19dcd3-a9ee-42b9-b9ea-c638e20ee4a9/STEP_5_COMPLETE.md)

Outputs: `nodes_created`, `relationships_discovered`, `claims_generated`, `completeness_score`, `cidoccrm_class`, and a log file path. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5b19dcd3-a9ee-42b9-b9ea-c638e20ee4a9/STEP_5_COMPLETE.md)

***

## 4. Subject Ontology Proposal (bridge step, via SCA component)

6. **Call Subject Ontology Proposal (Step 5 bridge)**

```python
result_onto = agent.propose_subject_ontology(uicallback=ui_log_callback)
```

- Uses the nodes discovered in Initialize Mode. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- For each, it fetches full Wikidata entity and extracts P31/P279/P361 chains. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- Runs an LLM clustering pass over types to identify **conceptual clusters** (e.g., Military Leadership, Military Operations, Military Organization). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- Converts clusters into **ontology classes** with `classname`, `parentclass`, `membercount`, `characteristics`, and example members. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- Produces **claim templates** (e.g., “All Military Commanders have rank; subject commanded legion value”). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- Defines **validation rules** (within‑class membership, cardinality, temporal consistency, cross‑facet alignment). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
- Computes a `strength_score` and logs reasoning. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)

The ontology is then stored on the SFA instance (`self.proposed_ontology`), ready for Training Mode. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)

***

## 5. Training Mode: extended claim generation

7. **Run Training Mode with ontology guidance**

```python
result_train = agent.execute_trainingmode(
    maxiterations=50,
    targetclaims=300,
    minconfidence=0.80,
    autosubmithighconfidence=False,
    uicallback=ui_log_callback
)
```

- Workflow per node: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4fcddbd6-a04f-46da-8376-d5a132e53b7d/STEP_3_COMPLETE.md)
  - Reload context (`get_session_context`) to pick up any inter‑agent changes. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b2ea8c97-b349-4d97-9cc0-9a710730d6d6/STEP_2_COMPLETE.md)
  - Use `self.proposed_ontology` to prioritize which SubjectConcepts to process first (e.g., Military Leadership class). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/c2899d5c-1cde-4fcc-a482-d3563797de62/STEP_5_SUBJECT_ONTOLOGY_PROPOSAL.md)
  - For each node:
    - Ensure it has a QID; if missing, skip or enrich via `enrich_node_from_wikidata`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4fcddbd6-a04f-46da-8376-d5a132e53b7d/STEP_3_COMPLETE.md)
    - Validate completeness again (Step 3.5) and log.  
    - Fetch Wikidata entity, generate additional claims from its statements (`generate_claims_from_wikidata`), now filtered through ontology templates and rules. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/4fcddbd6-a04f-46da-8376-d5a132e53b7d/STEP_3_COMPLETE.md)
    - Auto‑enrich each claim with CRMinf (`enrich_claim_with_crminf`) and ensure CIDOC alignment still holds. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a4714de-a0de-4427-8f35-64d297ab7766/STEP_4_COMPLETE.md)
    - Filter by `minconfidence`; optionally auto‑submit ≥0.90 confidence claims.  
    - Log each `CLAIM_PROPOSED` with label, confidence, rationale. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5b19dcd3-a9ee-42b9-b9ea-c638e20ee4a9/STEP_5_COMPLETE.md)

- Metrics: `nodes_processed`, `claims_proposed`, `avg_confidence`, `avg_completeness`, `claims_per_second`, and log file path. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5b19dcd3-a9ee-42b9-b9ea-c638e20ee4a9/STEP_5_COMPLETE.md)

By the end of Training Mode, the SFA has produced a **disciplined set of claims** shaped by its ontology, all traced back to federation sources and validated by schema + property patterns.

***

## 6. Between tasks: collaboration and introspection

Throughout the “day,” the SFA can:

- Use `list_pending_claims(facet=self.facetkey)` to see its own backlog and adjust behavior (e.g., reduce new proposals if validation is lagging). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b2ea8c97-b349-4d97-9cc0-9a710730d6d6/STEP_2_COMPLETE.md)
- Use `find_agent_contributions()` to monitor its promotion rate and perhaps lower confidence when error rates are high. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b2ea8c97-b349-4d97-9cc0-9a710730d6d6/STEP_2_COMPLETE.md)
- For any node, `get_node_provenance` and `get_claim_history` help it understand what other facets have asserted, enabling cross‑facet awareness even before SCA orchestration comes fully online. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/b2ea8c97-b349-4d97-9cc0-9a710730d6d6/STEP_2_COMPLETE.md)

***

## 7. End of “day”

When the session finishes:

- The logger writes a summary with counts of actions, reasoning steps, queries, errors, and claim stats. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5b19dcd3-a9ee-42b9-b9ea-c638e20ee4a9/STEP_5_COMPLETE.md)
- The SFA’s ontology and session metrics can be persisted (future work) to support longer‑term evaluation and tuning. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/5b19dcd3-a9ee-42b9-b9ea-c638e20ee4a9/STEP_5_COMPLETE.md)

Net effect: a newly instantiated SFA never free‑wheels. It:

1. Learns the schema.  
2. Reloads graph state.  
3. Bootstraps from a trusted QID.  
4. Lets the SCA/ontology‑proposal step structure its discipline.  
5. Generates and validates claims in Training Mode, with CIDOC/CRMinf enrichment and full provenance at each step. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/81085e9a-39e1-47af-bf4e-42957bbe0252/STEP_1_COMPLETE.md)