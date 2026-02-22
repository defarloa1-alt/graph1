# Chrystallum Architecture - Appendices Index

**Version:** 3.2 Decomposed  
**Date:** February 19, 2026  
**Status:** Current

---

## Overview

This directory contains 26 detailed appendices from the Chrystallum Architecture Specification, organized into 6 thematic clusters for easier navigation and maintenance.

**Main Architecture Documents:**
- [ARCHITECTURE_CORE.md](../ARCHITECTURE_CORE.md) - Executive summary & overview
- [ARCHITECTURE_ONTOLOGY.md](../ARCHITECTURE_ONTOLOGY.md) - Core ontology layers
- [ARCHITECTURE_IMPLEMENTATION.md](../ARCHITECTURE_IMPLEMENTATION.md) - Technology & workflows
- [ARCHITECTURE_GOVERNANCE.md](../ARCHITECTURE_GOVERNANCE.md) - QA & governance

---

## Cluster Organization

### 01_Domain_Ontology/ (4 appendices)

Defines what entities, relationships, and concepts exist in the system.

| File | Appendix | Description |
|------|----------|-------------|
| [Canonical_Relationship_Types.md](01_Domain_Ontology/Canonical_Relationship_Types.md) | A | 311 canonical relationship types with Wikidata/CIDOC-CRM alignment |
| [Action_Structure_Vocabularies.md](01_Domain_Ontology/Action_Structure_Vocabularies.md) | B | Goal, trigger, action, result type vocabularies |
| [Entity_Type_Taxonomies.md](01_Domain_Ontology/Entity_Type_Taxonomies.md) | C | 127 entity types across 14 categories |
| [Subject_Facet_Classification.md](01_Domain_Ontology/Subject_Facet_Classification.md) | D | 18-facet system with enforcement rules |

### 02_Authority_Integration/ (3 appendices)

How we federate with external authority sources.

| File | Appendix | Description |
|------|----------|-------------|
| [Temporal_Authority_Alignment.md](02_Authority_Integration/Temporal_Authority_Alignment.md) | E | PeriodO, LCSH period alignment, uncertain dates |
| [Geographic_Authority_Integration.md](02_Authority_Integration/Geographic_Authority_Integration.md) | F | TGN, Pleiades, GeoNames integration |
| [Wikidata_Integration_Patterns.md](02_Authority_Integration/Wikidata_Integration_Patterns.md) | K | Wikidata QID mapping, property alignment, SPARQL federation |

### 03_Standards_Alignment/ (4 appendices)

How we align with international standards.

| File | Appendix | Description |
|------|----------|-------------|
| [CIDOC_CRM_Integration_Guide.md](03_Standards_Alignment/CIDOC_CRM_Integration_Guide.md) | L | ISO 21127:2023 compliance, class mappings |
| [Semantic_Enrichment_Ontology_Alignment.md](03_Standards_Alignment/Semantic_Enrichment_Ontology_Alignment.md) | P | CIDOC-CRM/CRMinf ontology alignment |
| [Federation_Strategy_Multi_Authority.md](03_Standards_Alignment/Federation_Strategy_Multi_Authority.md) | R | Multi-authority integration strategy |
| BabelNet_Lexical_Authority.md | S | BabelNet integration (⚠️ not found - may be embedded in R) |

### 04_Implementation_Patterns/ (4 appendices)

How to build it - code patterns and workflows.

| File | Appendix | Description |
|------|----------|-------------|
| [Legacy_Implementation_Patterns.md](04_Implementation_Patterns/Legacy_Implementation_Patterns.md) | G | Deprecated patterns and migration guides |
| [Implementation_Examples.md](04_Implementation_Patterns/Implementation_Examples.md) | J | Working code examples and use cases |
| [Facet_Training_Resources_Registry.md](04_Implementation_Patterns/Facet_Training_Resources_Registry.md) | O | Agent training resources and ontology bootstrapping |
| Subject_Facet_Agent_Workflow.md | T | "Day in the Life" of a facet agent (⚠️ not found - may be embedded) |

### 05_Architecture_Decisions/ (6 appendices)

Why we made key architectural choices - ADRs (Architecture Decision Records).

| File | Appendix | Description |
|------|----------|-------------|
| [Architectural_Decision_Records_Overview.md](05_Architecture_Decisions/Architectural_Decision_Records_Overview.md) | H | ADR process and index |
| [ADR_001_Claim_Identity_Ciphers.md](05_Architecture_Decisions/ADR_001_Claim_Identity_Ciphers.md) | U | Content-addressable claim identification |
| [ADR_002_Function_Driven_Relationships.md](05_Architecture_Decisions/ADR_002_Function_Driven_Relationships.md) | V | 311 relationship types catalog |
| [ADR_004_Canonical_18_Facet_System.md](05_Architecture_Decisions/ADR_004_Canonical_18_Facet_System.md) | W | 18-facet system with enforcement |
| [ADR_005_Federated_Claims_Signing.md](05_Architecture_Decisions/ADR_005_Federated_Claims_Signing.md) | X | Cryptographic trust model for federated claims |
| [ADR_006_Bootstrap_Scaffold_Contract.md](05_Architecture_Decisions/ADR_006_Bootstrap_Scaffold_Contract.md) | Y | v0 bootstrap scaffolding contract |

### 06_Advanced_Topics/ (4 appendices)

Deep dives for specialists.

| File | Appendix | Description |
|------|----------|-------------|
| [Mathematical_Formalization.md](06_Advanced_Topics/Mathematical_Formalization.md) | I | Mathematical foundations (optional) |
| [Identifier_Safety_Reference.md](06_Advanced_Topics/Identifier_Safety_Reference.md) | M | ID collision prevention, safety rules |
| [Property_Extensions_Advanced_Attributes.md](06_Advanced_Topics/Property_Extensions_Advanced_Attributes.md) | N | Advanced entity properties and extensions |
| [Operational_Modes_Agent_Orchestration.md](06_Advanced_Topics/Operational_Modes_Agent_Orchestration.md) | Q | Agent modes: query, proposal, training, validation |

---

## Missing Appendices

**Appendix S (BabelNet)** and **Appendix T (SFA Workflow)** were not found as separate sections in the consolidated file. They may be:
- Embedded within other appendices
- Mentioned in the table of contents but not yet written
- Located elsewhere in the project

**Action needed:** Search for content or mark as TODO for future implementation.

---

## Usage

### Finding Specific Topics

**Need to know about...** → **Read this file:**
- Relationship types → `01_Domain_Ontology/Canonical_Relationship_Types.md`
- Entity types → `01_Domain_Ontology/Entity_Type_Taxonomies.md`
- Temporal periods → `02_Authority_Integration/Temporal_Authority_Alignment.md`
- Geographic places → `02_Authority_Integration/Geographic_Authority_Integration.md`
- CIDOC-CRM compliance → `03_Standards_Alignment/CIDOC_CRM_Integration_Guide.md`
- Claim ciphers → `05_Architecture_Decisions/ADR_001_Claim_Identity_Ciphers.md`
- 18-facet system → `05_Architecture_Decisions/ADR_004_Canonical_18_Facet_System.md`
- Agent orchestration → `06_Advanced_Topics/Operational_Modes_Agent_Orchestration.md`

---

## Statistics

| Cluster | Appendices | Total Lines |
|---------|-----------|-------------|
| 01_Domain_Ontology | 4 | 241 |
| 02_Authority_Integration | 3 | 8,229 |
| 03_Standards_Alignment | 3 | 4,371 |
| 04_Implementation_Patterns | 3 | 260 |
| 05_Architecture_Decisions | 6 | 2,003 |
| 06_Advanced_Topics | 4 | 1,256 |
| **TOTAL** | **23** | **16,360** |

**Note:** Some appendices (S, T) were listed in TOC but not found as separate sections.

---

**Extracted:** February 19, 2026  
**Source:** `2-12-26 Chrystallum Architecture - CONSOLIDATED.md` (15,910 lines)  
**Automation:** `scripts/tools/extract_appendices.py`

