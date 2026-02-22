# SysML Contract Artifacts

This folder contains JSON Schema contracts and one sequence diagram generated from the SysML v2 review workstream.

## Scope and status

- Canonical model source: `Key Files/2-13-26 SysML v2 System Model - Blocks and Ports (Starter).md`
- Contract status: draft-to-operational artifacts
- Current enforcement: schema validation via `scripts/tools/validate_sysml_contracts.py`
- Runtime wiring status: partial (contracts exist, only some are currently reflected in executable paths)

## Lifecycle note (important)

There are two different status layers:

- `Claim` lifecycle state in graph: `proposed|validated|disputed|rejected`
- API operation result status in ingest responses: `created|promoted|error`

These are complementary and should not be conflated.

## File crosswalk

- `claim_scope_validation_in.json`: input contract for spatiotemporal claim scope validation.
- `spatiotemporal_validation_out.json`: output contract for geographic-temporal validation result.
- `dispatcher_decision_out.json`: output contract for federation dispatcher routing decision.
- `error_envelope.json`: reusable error envelope pattern for port outputs.
- `observability_event_in.json`: input contract for structured observability events.
- `period_import_job_in.json`: input contract for period import/enrichment job requests.
- `period_triage_decision_out.json`: output contract for period triage decisions.
- `tgn_lookup_in.json`: input contract for single TGN lookup requests.
- `tgn_batch_lookup_in.json`: input contract for batch TGN lookup requests.
- `tgn_mapping_out.json`: output contract for TGN-to-Wikidata mapping results.
- `period_workflow_sequence.png`: visual sequence diagram from review.

## Validation

Run:

```powershell
python scripts/tools/validate_sysml_contracts.py
```

Checks include:

- valid JSON parsing
- duplicate filename/artifact detection
- duplicate `$id` detection
- strict object schema enforcement (`additionalProperties: false`)
- optional JSON Schema meta-schema checks when `jsonschema` is installed
