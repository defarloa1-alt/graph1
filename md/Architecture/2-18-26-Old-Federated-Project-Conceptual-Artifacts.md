# 2-18-26 Legacy Conceptual Artifacts (Markdown Harvest)

Status: completed conceptual pass over legacy markdown files in `Old-federated-project` (read from Git history, not restored to working tree).

## Scope
- Reviewed 26 legacy `.md` files.
- Extracted architecture-level concepts (not implementation code).
- Triaged each concept as:
1. already covered in current docs,
2. worth integrating as a focused ADR/spec note,
3. archive only (low signal / high noise).

## High-Value Conceptual Artifacts
1. Agent statelessness + graph-persisted state
- Legacy source: `Old-federated-project/Guide/base documentation/agent-architecture-persistence-ontology.md:330`
- Value: strong execution principle for agent architecture boundaries.
- Current coverage: already present in `md/Architecture/1-13-26-Baseline_Core_3.2.md:514`.
- Action: no new core spec needed; keep as supporting reference only.

2. 5W1H completeness framing as ontology quality signal
- Legacy source: `Old-federated-project/Guide/base documentation/agent-architecture-persistence-ontology.md:30`
- Value: practical authoring/validation rubric for claim completeness.
- Current coverage: already represented in `md/Architecture/1-13-26-Baseline_Core_3.2.md:127`.
- Action: optional refinement as QA checklist artifact, not as ontology rewrite.

3. Hybrid identity framing (QID + local + composite) with semantic jump emphasis
- Legacy source: `Old-federated-project/Guide/base documentation/Chrystallum-Complete-Reference-v3.0.md:312`
- Value: clear operator-facing narrative for identity modes.
- Current coverage: already present in `md/Architecture/1-13-26-Baseline_Core_3.2.md:74`.
- Action: no net-new architecture change required.

4. Shell nodes + lazy expansion + dormancy economics
- Legacy source: `Old-federated-project/Guide/base documentation/Chrystallum-Complete-Reference-v3.0.md:83`
- Value: explicit cost/operational framing for expansion policy.
- Current coverage: already present in `md/Architecture/1-13-26-Baseline_Core_3.2.md:73`.
- Action: optional addendum to ops playbook, not core model change.

5. PLAO + Agent ESB pattern (intent -> strategy -> adapter orchestration)
- Legacy source: `Old-federated-project/Guide/base documentation/presentation-layer-agent-esb.md:1`
- Value: useful front-end orchestration pattern and adapter contract concepts.
- Current coverage: partial/informal; no clear current standalone spec.
- Action: recommend promoting to a focused v1 doc:
  `md/Architecture/Presentation_Orchestration_PLAO_ESB_v1.md`
  with message contracts, adapter interface, and failure modes.

6. Scenario generation thresholds (completeness/minimality) as explicit QA gates
- Legacy source: `Old-federated-project/docs/SCENARIO_GENERATION_INTEGRATION.md:128`
- Value: concrete threshold/gate language can improve reproducibility.
- Current coverage: implicit in multiple docs, but not consolidated.
- Action: recommend one QA note consolidating threshold semantics and acceptance tests.

7. Debate kernel decomposition and policy/state split (`Phi = pi o alpha o beta`)
- Legacy source: `Old-federated-project/docs/Archv2/Graph theory modification impact (3).md:24`
- Value: good conceptual decomposition for governance-aware update flow.
- Risk: file includes heavy mixed-quality generated text.
- Action: salvage concept only; do not import prose directly.

## Archive-Only / Low-Signal Conceptual Files
1. `Old-federated-project/docs/Archv2/Graph theory modification impact.md`
2. `Old-federated-project/docs/Archv2/Graph theory modification impact revised.md`
3. `Old-federated-project/docs/Archv2/Graph theory modification impact (3).md`

Reason:
- large mixed-content generated blocks,
- low traceability to implemented code,
- high risk of importing contradictory or speculative statements.

## Recommended Integration Backlog (Conceptual Only)
1. Write a compact PLAO/ESB spec with explicit interfaces:
- `IntentClassifier`, `StrategySelector`, `AdapterRegistry`, `ResponseComposer`.
2. Add a scenario-generation QA spec:
- define completeness/minimality thresholds per test class,
- add deterministic validation query/report template.
3. Add one ADR on governance-aware update decomposition:
- separate policy gate from update operator,
- keep as conceptual boundary (not full equation-level rewrite).

## Backlog Execution Status (2026-02-18)
Completed:
1. `md/Architecture/Presentation_Orchestration_PLAO_ESB_v1.md`
2. `md/Architecture/Scenario_Generation_QA_Gates_v1.md`
3. `md/Architecture/ADR-002-Policy-Gate-and-Update-Operator-Separation.md`

Next recommended step:
1. Wire these docs into implementation tickets and conformance tests.

## Files Reviewed (Legacy Markdown)
1. `Old-federated-project/Guide/Archi/ARCHITECTURE_GUIDE.md`
2. `Old-federated-project/Guide/ai cognitive architecture/AI_COGNITIVE_ARCHITECTURE.md`
3. `Old-federated-project/Guide/ai cognitive architecture/AI_REASONING_INTEGRATION.md`
4. `Old-federated-project/Guide/ask_custom_gpt.md`
5. `Old-federated-project/Guide/base documentation/Chrystallum-Complete-Reference-v3.0.md`
6. `Old-federated-project/Guide/base documentation/agent-architecture-persistence-ontology.md`
7. `Old-federated-project/Guide/base documentation/chrystallum-complete-reference.md`
8. `Old-federated-project/Guide/base documentation/presentation-layer-agent-esb.md`
9. `Old-federated-project/Guide/base documentation/section-4-revised.md`
10. `Old-federated-project/Guide/base documentation/status-summary.md`
11. `Old-federated-project/Guide/base documentation/use-cases-realistic-md-combined.md`
12. `Old-federated-project/Guide/lcc/Building a Universal Subject Taxonomy Framework fo.md`
13. `Old-federated-project/Guide/sdlc advisor/ADVISOR_ACTION_REQUIRED.md`
14. `Old-federated-project/Guide/sdlc advisor/ADVISOR_FEEDBACK_COMPLETE.md`
15. `Old-federated-project/Guide/sdlc advisor/ADVISOR_REVIEW_PACKAGE.md`
16. `Old-federated-project/Guide/sdlc advisor/ASSET_PUBLICATION_SUMMARY.md`
17. `Old-federated-project/Guide/sdlc advisor/CI_COMPLETION_SUMMARY.md`
18. `Old-federated-project/Guide/sdlc advisor/CI_USAGE_GUIDE.md`
19. `Old-federated-project/deployment/README.md`
20. `Old-federated-project/deployment/config/subject_taxonomy/README.md`
21. `Old-federated-project/docs/Archv2/Graph theory modification impact (3).md`
22. `Old-federated-project/docs/Archv2/Graph theory modification impact revised.md`
23. `Old-federated-project/docs/Archv2/Graph theory modification impact.md`
24. `Old-federated-project/docs/Archv2/gexf files.md`
25. `Old-federated-project/docs/Archv2/yes that is my problem too many versions, too many.md`
26. `Old-federated-project/docs/SCENARIO_GENERATION_INTEGRATION.md`
