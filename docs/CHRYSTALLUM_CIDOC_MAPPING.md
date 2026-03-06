# Chrystallum → CIDOC-CRM / CRMinf Mapping

**Purpose:** Formal mapping for standards compliance. Enables export to CRM/CRMinf RDF and interoperability with museum/GLAM systems.

**References:**
- [CIDOC-CRM](https://cidoc-crm.org/cidoc-crm/)
- [CRMinf (Argumentation Model)](https://cidoc-crm.org/sites/default/files/CRMinf%20v1.1%20(2024.12.09).pdf)
- [CRM Primer](https://cidoc-crm.org/sites/default/files/CRMPrimer_v1.1.pdf)

---

## 1. Event and Repertoire Layer (PRH)

| Chrystallum Node | Chrystallum Property | CRM/CRMinf Class | CRM Property | Notes |
|------------------|----------------------|------------------|--------------|-------|
| `:Event` | `id`, `label`, `date_iso8601` | `E5 Event` | — | Historical event (contio, riot, strike, procession) |
| `:RepertoirePattern` | `id`, `label` | `E55 Type` | — | Pattern type (e.g. RP_CONTENTIOUS_ASSEMBLY, RP_URBAN_RIOT) |
| `(:Event)-[:INSTANCES_PATTERN]->(:RepertoirePattern)` | — | — | `P2 has type` | Event classified by repertoire pattern |
| `:Mechanism` | `id`, `label` | `E55 Type` | — | Mechanism type (M_ESCALATION, M_DIFFUSION, etc.) |
| `(:Event)-[:OPERATES_VIA]->(:Mechanism)` | — | — | `P2 has type` or `P9 consists of` | Event operates via mechanism; alternative: mechanism as sub-event |
| `:RepertoireFamily` | `id`, `label` | `E55 Type` (broader) | — | Grouping of patterns (RF_ASSEMBLY_DEMONSTRATION, RF_CONFLICT) |
| `(:RepertoirePattern)-[:USES_MECHANISM]->(:Mechanism)` | — | — | `P2 has type` (on event) | Pattern implies mechanisms; in CRM, assign types to E5 Event |

**RDF URI patterns (CRM):**
```
http://www.cidoc-crm.org/cidoc-crm/E5_Event
http://www.cidoc-crm.org/cidoc-crm/E55_Type
http://www.cidoc-crm.org/cidoc-crm/P2_has_type
http://www.cidoc-crm.org/cidoc-crm/P9_consists_of
```

---

## 2. Methodology Overlay (Fischer)

| Chrystallum Node | Chrystallum Property | CRM/CRMinf Class | Notes |
|------------------|----------------------|------------------|-------|
| `:MethodologyText` | `id`, `title`, `author` | `E31 Document` | Source work (e.g. DH_FISCHER_HF) |
| `:MethodologicalDomain` | `id`, `label` | `E55 Type` | Inquiry, Explanation, Argument |
| `:FallacyFamily` | `id`, `label` | `E55 Type` | Fallacy family (e.g. F_FSIGNIF) |
| `:Fallacy` | `id`, `label`, `diagnostic_pattern` | `E55 Type` | Fallacy type (HOLIST_FALLACY, ESSENCE_FALLACY, etc.) |
| `:TaskType` | `id`, `label` | `E55 Type` | Task classification (QUESTION_FRAMING, FACT_VERIFICATION, etc.) |
| `(:Fallacy)-[:GUARDS_TASKTYPE]->(:TaskType)` | — | — | Fallacy constrains task type; in CRMinf, used to type I1 Argumentation |

**RDF URI patterns:**
```
http://www.cidoc-crm.org/cidoc-crm/E31_Document
http://www.cidoc-crm.org/cidoc-crm/E55_Type
```

---

## 3. Methodology Overlay (Milligan)

| Chrystallum Node | Chrystallum Property | CRM/CRMinf Class | Notes |
|------------------|----------------------|------------------|-------|
| `:DigitalPrinciple` | `id`, `label`, `constraint` | `E73 Information Object` | Methodological prescription (SEARCH_BIAS_AWARENESS, etc.) |
| `(:DigitalPrinciple)-[:IMPOSES_CONSTRAINT_ON]->(:TaskType)` | — | — | Principle constrains task; in CRMinf, annotates I1 Argumentation |
| `(:DigitalPrinciple)-[:INTENSIFIES_RISK_OF]->(:Fallacy)` | — | — | Principle amplifies fallacy risk |

**RDF URI patterns:**
```
http://www.cidoc-crm.org/cidoc-crm/E73_Information_Object
```

---

## 4. Argumentation and Belief (CRMinf)

| Chrystallum Node/Concept | CRMinf Class | CRMinf Property | Notes |
|-------------------------|--------------|-----------------|-------|
| `:Claim` (proposed/accepted) | `I2 Belief` or `I4 Proposition Set` | — | Proposition about the world |
| `:ReasoningTrace` | `I1 Argumentation` | — | How the belief was derived |
| Fallacy detection (linter output) | `I1 Argumentation` | `P2 has type` → Fallacy E55 Type | Objection typed with fallacy |
| Digital constraint check | `I1 Argumentation` | — | Annotates argumentation that relies on digital evidence |
| Confidence on claim | — | `P140 assigned attribute to` | Confidence value on belief |
| `sca_lint_claim` / `narrative_lint_section` | `I1 Argumentation` | — | Produces argumentation that objects to or qualifies a belief |

**RDF URI patterns (CRMinf):**
```
http://www.cidoc-crm.org/crminf/I1_Argumentation
http://www.cidoc-crm.org/crminf/I2_Belief
http://www.cidoc-crm.org/crminf/I4_Proposition_Set
http://www.cidoc-crm.org/cidoc-crm/P140_assigned_attribute_to
```

---

## 5. Framework and Chrystallum Root

| Chrystallum Node | CRM/CRMinf Class | Notes |
|------------------|------------------|-------|
| `:Chrystallum` | Custom / `E73 Information Object` | Root; system description |
| `:Framework` | `E55 Type` or `E73 Information Object` | FISCHER_LOGIC, MILLIGAN_DIGITAL, PRH_REPERTOIRE |
| `(:Chrystallum)-[:HAS_FRAMEWORK]->(:Framework)` | — | Structural; Framework contains methodology nodes |
| `(:Framework)-[:CONTAINS]->(n)` | — | n = Fallacy, TaskType, RepertoirePattern, Mechanism, DigitalPrinciple, MethodologyText |

---

## 6. Summary Table (Quick Reference)

| Chrystallum | CRM | CRMinf |
|-------------|-----|--------|
| `:Event` | `E5 Event` | — |
| `:RepertoirePattern` | `E55 Type` | — |
| `:Mechanism` | `E55 Type` | — |
| `:Fallacy` | `E55 Type` | Qualifies I1 Argumentation |
| `:TaskType` | `E55 Type` | — |
| `:DigitalPrinciple` | `E73 Information Object` | — |
| `:MethodologyText` | `E31 Document` | — |
| `:Claim` | — | `I2 Belief` / `I4 Proposition Set` |
| Agent reasoning / lint | — | `I1 Argumentation` |
| `INSTANCES_PATTERN` | `P2 has type` | — |
| `OPERATES_VIA` | `P2 has type` or `P9 consists of` | — |

---

## 7. Export Notes

- **RDF export:** Map Chrystallum nodes to CRM/CRMinf URIs; use `P2 has type` for `INSTANCES_PATTERN` and `OPERATES_VIA` where the target is an E55 Type.
- **Bidirectional:** This mapping supports Chrystallum ↔ CIDOC-CRM/CRMinf translation; no schema changes required in Neo4j.
- **Incremental:** Can be extended with additional node types (e.g. `:Person`, `:Place`) using standard CRM classes E21 Person, E53 Place.
