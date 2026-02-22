# LOD Baseline Spec (2026-02-18)

Status: `ARB-LOD-001` baseline design.

## Objective
Define the minimum Linked Open Data baseline for Chrystallum so data can be exported in standard RDF form with stable identifiers and dataset metadata.

## In-Scope (Baseline)
- RDF export for a controlled subset of graph data.
- Stable URI pattern policy.
- Minimal mapping profile (Neo4j labels/properties -> RDF classes/properties).
- VoID descriptor generation.

## Out-of-Scope (Baseline)
- Full public SPARQL endpoint.
- Full OWL reasoning profile.
- Full dereference/content-negotiation infrastructure.

## Dataset Scope (v1)
Export these node families first:
- `Human`
- `Event`
- `Place`
- `Period`
- `SubjectConcept`
- `Claim`

Export these edge families first:
- identity/alignment links (for example `owl:sameAs` to Wikidata/LCSH/FAST where available)
- core event participation/location/period relations
- claim-to-entity and claim provenance edges used in current workflow

## Namespace Policy
Use these baseline prefixes:
- `chr:` -> `https://data.chrystallum.org/ontology/`
- `chrid:` -> `https://data.chrystallum.org/id/`
- `prov:` -> `http://www.w3.org/ns/prov#`
- `void:` -> `http://rdfs.org/ns/void#`
- `dct:` -> `http://purl.org/dc/terms/`
- `owl:` -> `http://www.w3.org/2002/07/owl#`
- `rdf:` -> `http://www.w3.org/1999/02/22-rdf-syntax-ns#`
- `rdfs:` -> `http://www.w3.org/2000/01/rdf-schema#`

Note:
- Base domain is treated as provisional until deployment domain is finalized.

## URI Strategy (Baseline)
- Entity URIs:
  - `chrid:human/{id_hash}`
  - `chrid:event/{id_hash}`
  - `chrid:place/{id_hash}`
  - `chrid:period/{id_hash}`
  - `chrid:subject/{subject_id}`
- Claim URIs:
  - `chrid:claim/{claim_id}`
- Use existing immutable IDs (`id_hash`, `claim_id`, `subject_id`) whenever available.

## Serialization Targets
- Required:
  - Turtle (`.ttl`)
- Optional:
  - N-Triples (`.nt`)

## Mapping Baseline
- Node class mapping:
  - `:Human` -> `chr:Human`
  - `:Event` -> `chr:Event`
  - `:Place` -> `chr:Place`
  - `:Period` -> `chr:Period`
  - `:SubjectConcept` -> `chr:SubjectConcept`
  - `:Claim` -> `chr:Claim`
- Label mapping:
  - `label` -> `rdfs:label`
- Identity alignment:
  - `qid`/authority IDs -> `owl:sameAs` or explicit `chr:hasAuthorityId` (if direct URI not available)
- Provenance baseline:
  - claim source and run metadata -> `prov:wasDerivedFrom`, `prov:generatedAtTime`, `prov:wasAttributedTo` (when available)

## Export Profiles
- `core_graph_v1.ttl`
  - core entities + core relations
- `claims_provenance_v1.ttl`
  - claim nodes + provenance links
- `alignments_v1.ttl`
  - authority alignment links
- `void.ttl`
  - dataset description and linkset metadata

## Pipeline Shape
1. Extract:
- read-only Cypher queries over selected labels/edges.
2. Transform:
- apply mapping profile and URI strategy.
3. Serialize:
- write `.ttl` (and optional `.nt`) exports.
4. Describe:
- emit VoID dataset descriptor.
5. Validate:
- syntax validation and triple-count checks.

## Validation Checks (Baseline)
- RDF syntax passes parser checks.
- URI pattern checks pass for exported entities/claims.
- Export includes all scoped labels from v1 dataset scope.
- Triple count and node count summaries are emitted.
- No canonical graph mutation occurs in export workflow.

## Acceptance Criteria for ARB-LOD-001
- This spec exists and is linked in architecture indexes/backlogs.
- v1 scope and target formats are explicit (`ttl` required, `nt` optional).
- URI strategy and namespace policy are explicit.
- Baseline mapping/profile and validation checks are explicit.

## Next Step
- Implement `ARB-LOD-002` with initial VoID descriptor:
  - `md/Architecture/VOID_DATASET_DRAFT_2026-02-18.ttl`
