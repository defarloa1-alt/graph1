# SHACL/RDFS-Lite Validation Scope (2026-02-18)

Status: `ARB-REAS-001` scope definition.

## Objective
Define a deterministic semantic-validation baseline that adds SHACL-style constraints and limited RDFS-lite checks without introducing non-deterministic reasoning paths.

## Scope Boundary
- This is a validation scope, not a full OWL entailment stack.
- Checks are advisory for proposal/promotion gates and must not bypass `U -> Pi -> Commit`.
- RDFS-lite means constrained subclass/type closure for approved vocab slices only.

## v1 Constraint Families
1. Identity integrity
- unique and non-null node identifiers for core entities and claims.
- identifier format checks for authority IDs where regex-safe rules exist.

2. Temporal bounds
- start/end ordering checks on temporalized entities.
- claim/event temporal overlap sanity checks where both sides expose bounded ranges.

3. Authority consistency
- one namespace policy per authority link (no mixed semantics per edge).
- canonical URI/ID consistency checks for mapped external authorities.

## Initial Constraint Catalog (Deterministic)

| Constraint ID | Family | Rule (v1) | Result on Fail |
|---|---|---|---|
| `SHACL-IDENT-001` | Identity | `Human.id_hash` must be present and unique. | `ERROR` |
| `SHACL-IDENT-002` | Identity | `Claim.claim_id` must be present and unique. | `ERROR` |
| `SHACL-IDENT-003` | Identity | `SubjectConcept.subject_id` must be present and unique. | `ERROR` |
| `SHACL-TEMP-001` | Temporal | If both bounds exist, `start_year <= end_year`. | `ERROR` |
| `SHACL-TEMP-002` | Temporal | Event-year and linked Period bounds must not be disjoint when both are bounded. | `WARN` |
| `SHACL-AUTH-001` | Authority | Wikidata IDs must match `^Q[1-9][0-9]*$` when present. | `ERROR` |
| `SHACL-AUTH-002` | Authority | Authority-alignment edges must preserve namespace-to-edge-type mapping policy. | `WARN` |

## RDFS-Lite Checks (v1)
- `RDFS-LITE-001`: approved subclass closure for constrained type hierarchies used by routing and validation.
- `RDFS-LITE-002`: inferred parent-type consistency check for selected node cohorts.

Implementation note:
- Inference outputs are validation artifacts only in v1; they do not write back inferred canonical labels automatically.

## Output Contract for Validator Runner (`ARB-REAS-002`)
Runner must emit JSON with:
- deterministic metadata header:
  - `contract_version`
  - `validator_version`
  - `constraint_pack_id`
  - `run_fingerprint` (hash of sorted inputs/check IDs)
- summary counts:
  - `checks_executed`
  - `errors`
  - `warnings`
  - `passes`
- per-check rows with stable IDs and machine-readable reason codes.

## Execution Order (v1)
1. Identity checks
2. Temporal checks
3. Authority checks
4. RDFS-lite closure checks

Reason:
- front-load hard failures that can invalidate downstream interpretation.

## Non-Goals (v1)
- full SHACL shapes coverage for all labels/edges.
- open-world reasoning across every external authority ontology.
- auto-repair writes.

## Acceptance Criteria Mapping (`ARB-REAS-001`)
- Identity constraints listed: yes.
- Temporal-bound constraints listed: yes.
- Authority-consistency constraints listed: yes.
- Scope is deterministic and governance-safe: yes.

## Implementation Link (`ARB-REAS-002`)
- Initial validator runner scaffold:
  - `scripts/tools/validate_semantic_constraints.py`
