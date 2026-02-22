# md/reference Consolidation

## Scope
- Reviewed `md/reference` (44 files originally).
- Ran two-pass cleanup.
- Pass 1: archived clearly outdated/historical files.
- Pass 2: collapsed remaining analysis docs into one backlog and archived originals.

## Final Keep Set
- `md/reference/REFERENCE_CONSOLIDATION_2026-02-12.md`
- `md/reference/REFERENCE_BACKLOG.md`
- `md/reference/IDENTIFIER_ATOMICITY_AUDIT.md`
- `md/reference/IDENTIFIER_CHEAT_SHEET.md`
- `md/reference/Entity_Property_Extensions.md`
- `md/reference/Property_Extensions_Implementation_Guide.md`
- `md/reference/Property_Extensions_Summary.md`
- `md/reference/Action_Structure_Vocabularies.md`

## Archived (Total)
- Archived to `Archive/md/reference`: 38 files.

## Archived In Pass 1
- `Archive/md/reference/ac_for_basic_backbone.txt`
- `Archive/md/reference/Answer_To_Consolidate_Schema_Question.md`
- `Archive/md/reference/Archive_Fact_Validation_Lessons.md`
- `Archive/md/reference/Archive_LLM_Extraction_Experiment.md`
- `Archive/md/reference/Archive_Problem_Solution_Analysis.md`
- `Archive/md/reference/Archive_Source_Citations_Analysis.md`
- `Archive/md/reference/Archive_Triple_Plus_Narrative_Format.md`
- `Archive/md/reference/Archive_Unique_ID_Approach_Comparison.md`
- `Archive/md/reference/Archive_Wikidata_Alignment_Analysis.md`
- `Archive/md/reference/Identifying_Great_Writing_AI_Approach.md`
- `Archive/md/reference/LLM_Degradation.md`
- `Archive/md/reference/OpenAI_Model_Spec.md`
- `Archive/md/reference/Persisting_Relationship_Types_as_Registry.md`
- `Archive/md/reference/Relations_Deprecation_Notice.md`
- `Archive/md/reference/Relations_README.md`
- `Archive/md/reference/Relationship_Count_Clarification.md`
- `Archive/md/reference/Relationship_Types.md`
- `Archive/md/reference/SCHEMA_CLEANUP_2026-01-08.md`
- `Archive/md/reference/Schema_Update_Instructions.md`
- `Archive/md/reference/SESSION_TRACKING_GUIDE.md`

## Archived In Pass 2
- `Archive/md/reference/Action_Structure_Wikidata_Alignment.md`
- `Archive/md/reference/Action_Structure_Wikidata_Mapping_Complete.md`
- `Archive/md/reference/Action_Structure_With_Wikidata_Example.md`
- `Archive/md/reference/Action_Type_Hierarchy_Analysis.md`
- `Archive/md/reference/Appendix_New_Relationships_From_Extraction.md`
- `Archive/md/reference/DISCOVERY_RELATIONSHIPS_WIKIDATA_ALIGNMENT.md`
- `Archive/md/reference/RELATIONSHIP_DISCOVERY_SCHEMA.md`
- `Archive/md/reference/Material_Object_Schema_Analysis.md`
- `Archive/md/reference/WIKIDATA_ALIGNMENT_COVERAGE.md`
- `Archive/md/reference/Reasoning_Model_for_Chrystallum.md`
- `Archive/md/reference/Recommended_Reasoning_Model.md`
- `Archive/md/reference/MCP_Code_Reduction_Analysis.md`
- `Archive/md/reference/MCP_Integration_Analysis.md`
- `Archive/md/reference/MCP_Migration_Plan.md`
- `Archive/md/reference/MCP_Reasoning_Models_Cursor.md`
- `Archive/md/reference/MCP_Role_in_Chrystallum_Architecture.md`
- `Archive/md/reference/Open_Source_Reasoning_Models_with_MCP.md`
- `Archive/md/reference/Wikidata_MCP_Impact_Analysis.md`

## Evidence of Outdated State (Why Archived)
- Multiple files referenced old relationship totals (`191`, `235`, `236`) that conflict with current consolidated registry.
- Multiple files referenced deprecated/nonexistent paths (`Reference/...`, `relations/canonical_relationship_types.csv`) instead of current canonical files under `Relationships/`.
- Several files were explicitly historical (`Archive_*`) or already superseded by domain consolidations.

## Captured Forward Work
- All non-canonical ideas are consolidated in `md/reference/REFERENCE_BACKLOG.md`.
- This includes relationship-governance follow-up, action-structure normalization, MCP scope decisions, material/object modeling decisions, and reasoning/Wikidata coverage refresh.

## Validation Note
- Discovery/extraction relationship proposals in this folder were checked against `Relationships/relationship_types_registry_master.csv`; the sampled candidates are already present in the current consolidated registry.
