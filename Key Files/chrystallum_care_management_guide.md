# Chrystallum Care Management Guide
## For Human Care Managers and LLM Agents

**Version 1.0 · Transition of Care Domain · Snowflake → Neo4j Integration**

---

## Who This Guide Is For

This document has two audiences and is written explicitly for both.

**Human care managers** — nurses, social workers, and care coordinators who use the Chrystallum system to manage post-discharge members. You do not need to understand the graph database or the code. You need to understand what the system does for you, what it cannot do, and when your judgment is required.

**LLM agents** — automated agents operating within the Chrystallum pipeline. This document is your operating contract. It defines your scope, your data sources, your decision authority, and the hard boundaries beyond which you must escalate to a human.

---

## Part One: What Chrystallum Does

Chrystallum is a knowledge graph that connects hospital discharge data, member clinical history, coverage rules, provider quality scores, and social determinants of health into a single queryable structure. For care management, this means three things:

**It detects.** When a member is discharged from a hospital, SNF, or rehab facility, a record appears in Snowflake within minutes. Chrystallum harvests that record automatically, identifies the member, expands the diagnosis codes, computes a risk score, and creates a care management workflow task — all before a care manager opens a dashboard.

**It organizes.** Every piece of information relevant to a member's post-discharge needs — their payer mix, ADL functional score, caregiver availability, prior admissions, open HEDIS gaps, assigned home health agency, pending authorizations — is linked in the graph and queryable in one place.

**It routes.** Based on what it knows about the member, Chrystallum determines which agents should act and in what order. A member with dementia, no caregiver, and a LACE score of 12 gets a different pathway than a member with a clean discharge after a knee replacement. The system encodes that difference as a capability cipher — a hash that drives agent routing without hardcoded rules.

What Chrystallum does not do: it does not make final coverage decisions, it does not replace clinical judgment, and it does not call members. Those actions require a human in the loop.

---

## Part Two: The Discharge Pipeline — Step by Step

### How a discharge becomes a care management task

**Step 1 — Hospital writes the discharge.**
When a member is discharged, the hospital's interface engine translates the ADT message (HL7 ADT^A03) into a row in the Snowflake table `CLINICAL_OPS.DISCHARGES.ADT_DISCHARGE_EVENTS`. This row contains the member's identifiers (MBI, Medicaid ID, plan member ID), the discharge setting, all diagnosis codes, the LACE readmission risk score, whether home health was ordered, and the discharge ADL score if the sending facility captured it.

**Step 2 — Chrystallum detects the discharge.**
The harvest agent polls Snowflake every 15 minutes, or consumes a Snowflake Stream for near-real-time detection. It fetches all rows where `PROCESSED = FALSE`.

**Step 3 — Member matching.**
The system attempts to match the discharge to an existing member node using member ID, Medicare Beneficiary Identifier (MBI), or Medicaid ID — whichever is present. If no match is found, the discharge is flagged `member_unmatched` and enters an identity resolution queue for human review.

**Step 4 — Diagnosis expansion.**
All ICD-10 codes in the discharge array are expanded into individual diagnosis nodes. Two codes trigger automatic flags: any `Z74.x` code sets `member.adl_need = true`. The specific code `Z74.2` (need for assistance at home, no able caregiver in household) sets `member.no_caregiver = true` and escalates the member's institutionalization risk.

**Step 5 — Risk tier assignment.**
The system computes a risk tier from 1 to 5:

| Tier | Criteria | Priority |
|------|----------|----------|
| 5 | LACE ≥ 10 AND no caregiver (Z74.2) | URGENT — same-day outreach |
| 4 | LACE ≥ 10 OR no caregiver | URGENT — within 4 hours |
| 3 | 30-day readmit risk ≥ 25% OR ADL need documented | STANDARD — within 24 hours |
| 2 | LACE ≥ 7 | STANDARD — within 48 hours |
| 1 | All other discharges | STANDARD — within 48 hours |

**Step 6 — Workflow trigger created.**
A `WorkflowTrigger` node is created in the graph with a `due_by` timestamp 48 hours after discharge, a risk tier, and a priority flag. This is what appears in the care manager's worklist.

**Step 7 — Snowflake marked processed.**
Only after the graph write succeeds does the system mark `PROCESSED = TRUE` in Snowflake. If the graph write fails for any reason, the row remains unprocessed and is retried on the next poll cycle.

---

## Part Three: For Human Care Managers

### Your dashboard

Your worklist shows all `WorkflowTrigger` nodes with status `PENDING`, sorted by priority (URGENT first) then by `due_by`. Each item shows:

- Member ID and name
- Risk tier (1–5) and priority flag
- Discharge setting (hospital, SNF, IRF, home with HHA)
- Discharge date and time remaining in the 48-hour window
- Key flags: ADL need, no caregiver, open HEDIS gaps
- Whether home health was ordered at discharge

### What the system has already done for you

When you open a member's care management record, Chrystallum will have already:

- Identified all active diagnoses from the discharge
- Pulled the member's ADL score from the discharge record or from prior OASIS/Katz/Barthel assessments on file
- Determined the member's payer mix (Medicare, Medicaid, MA supplemental)
- Identified the applicable coverage pathway
- Flagged any HEDIS gaps (TFL 7-day window, TFL 30-day window, COA functional assessment)
- If home health was ordered: checked the referring HHA's quality scores and identified alternatives if the ordered agency scores below regional benchmark
- If Z74.2 is present: identified available community resources (Area Agency on Aging, HCBS waiver slots, Meals on Wheels)

### What requires your judgment

The system will not act on any of the following without your review:

**Coverage denials.** If the authorization agent determines a service does not meet medical necessity criteria under the applicable LCD, it flags the case as `PENDING_INFO` rather than issuing a denial. You review the criteria gap, gather additional clinical information, and make the determination.

**Unmatched members.** If a discharge cannot be matched to a plan member, it enters your identity resolution queue. This may mean the member is not enrolled, was enrolled under a different ID, or the Snowflake data has an error.

**Tier 5 members.** Any member with tier 5 risk (high LACE + no caregiver) requires a same-day human touchpoint. The system will generate an outreach task and a care plan stub, but the member call is yours.

**Hospice and AMA discharges.** Members discharged to hospice (disposition code 50) or who left against medical advice (code 07) require clinical judgment that the system does not attempt to substitute.

**SDOH escalations.** When Z74.2 is flagged alongside housing instability (Z59.x) or other social determinants, the system surfaces available resources, but connecting the member to those resources — a conversation about their living situation, their support network, their willingness to accept help — is a human conversation.

**Provider disputes.** If a member refuses the system-recommended HHA or requests a specific provider not in the recommended list, you make that call.

### The 48-hour clock

Every TOC workflow has a due-by timestamp. For HEDIS purposes, the 7-day TFL window begins at the moment of discharge. Missing this window has a direct impact on STAR ratings.

The system tracks the window automatically and will auto-close the HEDIS gap when a qualifying follow-up claim is received. But if the window is approaching and no follow-up has been scheduled, it will surface the gap in your worklist with the remaining days highlighted.

### Reading a member's care management record

The key fields you will encounter:

| Field | What it means |
|-------|--------------|
| `risk_tier` | 1–5, computed from LACE + Z74.2 + readmit model |
| `adl_need` | True if any Z74.x code is in the discharge |
| `no_caregiver` | True if Z74.2 specifically is present |
| `adl_score` | Numeric score from most recent assessment (Katz, Barthel, OASIS, MDS) |
| `adl_tool` | Which instrument produced the score |
| `coverage_pathway` | Medicare HH / Medicaid PCS / MA Supplemental |
| `hh_ordered` | Whether the discharging physician ordered home health |
| `lace_score` | 0–19, readmission risk (≥10 = high) |
| `readmit_risk` | Model-predicted 30-day readmission probability (0.0–1.0) |
| `institutionalization_risk` | "elevated" if Z74.2 is flagged |
| `cipher` | Capability cipher — same value means same care pathway as another member |

### Assessment tools reference

The ADL score on a member's record comes from one of five instruments. The threshold for LTSS eligibility varies by state and payer:

| Tool | Scale | High-dependency threshold | Typical use |
|------|-------|--------------------------|-------------|
| Katz ADL | 0–6 | ≤ 3 (most Medicaid states) | Medicaid LTSS eligibility |
| Barthel | 0–100 | < 60 | Rehab, post-acute |
| MDS 3.0 Section G | 0–4 per domain | 3–4 = extensive/total assist | SNF discharge |
| OASIS-E M1800 | 0–6 | ≥ 3 | Home health start of care |
| LACE Index | 0–19 | ≥ 10 | Readmission risk (not ADL) |

If a member has no ADL score on file, the COA HEDIS gap will be open and completing a Katz or Barthel assessment is the highest-priority clinical action.

---

## Part Four: For LLM Agents

### Your operating contract

You are an agent operating within the Chrystallum care management pipeline. This section defines your scope precisely. Operating outside this scope without escalation is a failure mode, not a feature.

### Identity and initialization

On startup, you must:

1. Read `INSTANCE_DATA` from the domain constitution to confirm you are operating in the correct domain (Health Plan · Care Management · LTSS).
2. Run `SQ-04` (72-hour Snowflake backfill) to recover any discharges missed during downtime.
3. Query the graph for any `WorkflowTrigger {status: "PENDING"}` nodes older than 4 hours — these indicate a previous agent run that did not complete and must be escalated to a human supervisor.
4. Verify connectivity to all `operational` federation sources before beginning harvest.

### The harvest loop (AW-01)

Your primary loop runs on Snowflake poll (SQ-01, every 15 minutes) or Stream consume (SQ-02, preferred).

For each discharge row:

```
1. Run CQ-01  — MERGE :DischargeEvent, match :Member, wire :Provider
2. Run CQ-02  — UNWIND DX_CODES, create :Diagnosis nodes, set Z74 flags
3. Run CQ-03  — Compute risk_tier, MERGE :WorkflowTrigger, stamp HEDIS gaps
4. Run SQ-05  — Mark PROCESSED=TRUE in Snowflake
               ONLY after steps 1–3 commit successfully
               If any step fails: do NOT mark processed, log error, continue to next row
```

Step 4 is conditional. You must not mark a row processed unless the graph write confirmed success. This is the idempotency guarantee. Violating it causes missed members.

### The TOC workflow loop (AW-02)

Query pending TOC triggers (CQ-04). Process URGENT priority first, then STANDARD.

For each trigger:

```
1. Pull member coverage — payer mix, benefit limits, prior auth history
2. Resolve coverage pathway (R-06):
   - Medicare Part A/B: requires homebound status + skilled service need + physician order
   - Medicaid PCS: requires ADL score at or below state threshold (typically Katz ≤ 3)
   - MA Supplemental: requires SSBCI benefit in plan design + chronic illness criteria
3. If HOME_HEALTH_ORDERED = TRUE:
   - Fetch LCD for member's MAC jurisdiction from CMS_LCD_NCD
   - Check all medical necessity criteria
   - If all criteria met: SET auth_decision = APPROVED
   - If criteria gap: SET auth_decision = PENDING_INFO, escalate to human
   - If criteria fail: SET auth_decision = DENIED, escalate to human for review
4. If HOME_HEALTH_ORDERED = FALSE:
   - Evaluate clinical need from DX codes + ADL score
   - If criteria met: generate referral recommendation, escalate for human auth initiation
   - If criteria not met: document rationale, no action
5. Assign HCPCS code per payer (R-08):
   - Medicare/MA: 99509 (home visit ADL), G0151/G0152 (PT/OT)
   - Medicaid: T1019 (PCS per 15 min), S5125 (attendant care)
   CRITICAL: T1019 is Medicaid-only. Using it on a Medicare claim generates a denial.
6. Run quality-matched HHA selection (R-10):
   - Query NPI Registry for type-2 providers, taxonomy 376J00000X, member ZIP
   - Filter to in-network only
   - Join CMS OASIS scores, rank by ADL improvement rate DESC, hospitalization rate ASC
   - MERGE :HHAAssignment to top-ranked in-network provider
7. Close WorkflowTrigger: SET status = COMPLETED, completed_at = datetime()
```

### Authorization decision authority

You have authority to:

- Set `auth_decision = APPROVED` when all LCD criteria are demonstrably met from data in the graph
- Set `auth_decision = PENDING_INFO` when a required data element is missing or ambiguous
- Generate HHA referral recommendations and assignment suggestions

You do not have authority to:

- Issue a final coverage denial — set `PENDING_INFO` and escalate
- Override an LCD medical necessity determination that returned a criteria failure
- Approve services outside the member's active benefit period
- Approve services for a member whose coverage pathway is ambiguous (multiple active payer spans without clear hierarchy)

When you escalate, you must write a structured escalation note to the `WorkflowTrigger` node:

```cypher
SET wf.escalation_reason = "<specific criterion that could not be resolved>",
    wf.escalated_at = datetime(),
    wf.status = "ESCALATED"
```

### SDOH escalation trigger (AW-05)

Any discharge containing `Z74.2` in the DX_CODES array triggers the SDOH agent path regardless of risk tier. This is not optional — Z74.2 is the single strongest predictor of avoidable SNF admission and must always surface.

When Z74.2 is detected:

```
1. MERGE :SDOHFlag {type: "NO_CAREGIVER"} on member
2. SET member.institutionalization_risk = "elevated"
3. Query Gravity SDOH value sets for co-occurring Z59.x (housing), Z55–Z65 (social determinants)
4. Re-compute risk tier: if Z74.2 + any Z74.x → minimum tier 4, regardless of LACE
5. Identify eligible community resources: HCBS waiver slots, Area Agency on Aging, Medicaid LTSS
6. Write structured action list to WorkflowTrigger escalation note
7. SET wf.priority = "URGENT" if not already set
```

### HEDIS gap management (AW-04)

HEDIS gap tracking is automatic. Your responsibilities:

**TFL (Transitions of Care):** A gap flag is created on every qualifying discharge. You do not create it — CQ-03 does. Your job is to monitor the window.

- Every night, query for open TFL gaps where `date.today() >= window_7d - 2 days` — surface to care manager worklist with days remaining
- When a qualifying follow-up claim is received for a member, run CQ-05 to auto-close the gap. A qualifying follow-up is an E&M visit (CPT 99202–99215) with any provider within the window
- A gap is only closable by a claim — scheduling alone does not close it

**COA (Care for Older Adults):** For members age 65 and older, if no Katz or Barthel assessment has a claim in the current measurement year, the COA gap is open. This cannot be auto-closed. A care manager must complete the assessment and a claim must be submitted with the corresponding LOINC code (72133-2 for Katz, 44177-1 for Barthel).

### Capability cipher

Every member's care pathway is encoded in a capability cipher:

```
SHA-256(entity_qid || p31_type_qids || code_set_ids || fed_source_ids || primary_facets)
```

The cipher is computed and stored on the member node. You use it in two ways:

**Cohort routing:** When a new member's cipher matches an existing cohort, inherit that cohort's care plan template without re-evaluation. This is not a shortcut — it is the intended behavior. The cipher encodes enough information that identical ciphers genuinely represent identical pathways.

**Change detection:** Run CQ-06 nightly to find members whose cipher was last computed before their last update. Any change in diagnosis codes, payer, or SDOH flags invalidates the cipher. Recompute it, and if the new cipher differs from the old one, flag the member for care manager review — their pathway has changed.

### Corpus fit gate (R-16)

Before any entity is processed, verify it belongs in this graph:

```
corpus_fit = has_icd10_code OR has_hcpcs_code OR has_npi OR has_member_id OR has_snomed_code
```

If `corpus_fit < 0.15`, set `corpus_rejected = true` and do not process further. Log the entity QID and rejection reason. This gate exists to prevent non-healthcare entities — ingested incidentally through broad Wikidata harvests — from consuming graph resources or generating false care management signals.

### Federation source status

Before each harvest cycle, verify that required federation sources are reachable. Sources that must be operational for the harvest loop to proceed:

| Source | Required for |
|--------|-------------|
| SNOWFLAKE_DISCHARGES | All harvest — primary event source |
| ICD10_API | Diagnosis enrichment |
| NPI_REGISTRY | Provider matching |

Sources that can be degraded without halting the loop (flag for human review):

| Source | Degraded behavior |
|--------|------------------|
| CMS_LCD_NCD | Auth decisions set to PENDING_INFO — do not attempt APPROVED |
| CMS_OASIS | HHA quality matching skipped — assign to first in-network provider, flag for human quality review |
| LOINC | Assessment instrument enrichment skipped — score stored, tool string stored, LOINC code null |
| GRAVITY_SDOH | SDOH community resource lookup skipped — Z74.2 flag still set, resource list empty |

### Error handling

Every Cypher write must be wrapped in error handling. If `CQ-01` fails for a discharge row, do not proceed to `CQ-02` or `CQ-03`. Do not mark the row processed in Snowflake. Log the error with the encounter ID and requeue for the next cycle.

Do not silently swallow failures. A failed write that is marked processed is unrecoverable — the member will not appear in the care management worklist and will miss their 48-hour window.

### What you must never do

- Issue a final authorization denial without human review
- Set `PROCESSED = TRUE` in Snowflake before graph writes confirm
- Process a member whose identity could not be resolved — enter identity resolution queue instead
- Auto-close a HEDIS gap without a qualifying claim as evidence
- Override a corpus fit rejection — if an entity fails the gate, do not re-score it
- Infer member clinical status from general knowledge — use only what is in the graph or returned from a federation source call
- Cache federation source responses for more than 24 hours — coverage rules and provider data change

---

## Part Five: Key Reference

### ICD-10 codes that trigger care management actions

| Code | Meaning | Action triggered |
|------|---------|-----------------|
| Z74.01 | Bed confinement status | ADL need flag, tier ≥ 3 |
| Z74.1 | Need for assistance with personal care | ADL need flag |
| Z74.2 | Need for assistance at home, no able caregiver | ADL need + no caregiver flag, minimum tier 4, SDOH agent |
| Z74.3 | Need for continuous supervision | ADL need flag, tier escalation |
| Z74.9 | Care provider dependency NOS | ADL need flag |

### HCPCS codes by payer

| Code | Service | Payer | Notes |
|------|---------|-------|-------|
| T1019 | Personal care services, per 15 min | Medicaid only | #1 home health code nationally |
| S5125 | Attendant care services, per 15 min | Medicaid / MA | |
| S5130 | Homemaker service, per 15 min | Medicaid | |
| 99509 | Home visit for ADL / personal care | Medicare / MA | |
| G0151 | PT services, home health, per 15 min | Medicare | |
| G0152 | OT services, home health, per 15 min | Medicare | |

### Coverage pathway decision tree

```
Member has discharge with ADL need
│
├── Active Medicare + homebound + physician order + skilled need?
│   └── YES → Medicare Home Health (Part A/B)
│       └── LCD medical necessity check required
│
├── Active Medicaid + ADL score ≤ state threshold?
│   └── YES → Medicaid PCS (state plan or 1915c waiver)
│       └── Prior auth from MCO required
│
├── Medicare Advantage + plan has SSBCI + chronic illness criteria met?
│   └── YES → MA Supplemental Benefit
│       └── Plan-specific benefit design applies
│
└── None of the above → PENDING_INFO, escalate to human
```

### Discharge disposition codes

| Code | Setting | TOC action |
|------|---------|-----------|
| 01 | Home | Evaluate for HH if ADL need flagged |
| 03 | SNF | Monitor for SNF → home transition |
| 06 | Home with home health | Validate auth, quality-match HHA |
| 07 | AMA (against medical advice) | Urgent outreach within 24h |
| 20 | Expired | Exclude from pipeline |
| 50 | Hospice — home | Route to hospice workflow |
| 62 | IRF (inpatient rehab) | Monitor for IRF → home transition |

### HEDIS measure quick reference

| Measure | Population | Numerator | Window |
|---------|-----------|-----------|--------|
| TFL — 7 day | All acute/SNF/IRF discharges | Outpatient visit within 7 days | 7 days post-discharge |
| TFL — 30 day | All acute/SNF/IRF discharges | Outpatient visit within 30 days | 30 days post-discharge |
| COA — Functional status | Members age 65+ | Katz or Barthel assessment with claim | Measurement year |

---

## Part Six: Architecture Notes for Implementers

### Graph node types introduced by this pipeline

| Node type | Created by | Primary key |
|-----------|-----------|-------------|
| `:DischargeEvent` | CQ-01 | `encounter_id` |
| `:Diagnosis` | CQ-02 | `icd10_code` |
| `:WorkflowTrigger` | CQ-03 | `type + encounter_id` |
| `:HEDISGapFlag` | CQ-03 | `measure + year + member_id` |
| `:SDOHFlag` | AW-05 | `type + member_id` |
| `:HHAAssignment` | AW-02 step 6 | `encounter_id` |
| `:ServiceAuth` | AW-03 | `encounter_id + service_type` |
| `:AssessmentResult` | CQ-01 (if score present) | `encounter_id + tool` |

### Relationships introduced

| Relationship | From → To | Set by |
|-------------|-----------|--------|
| `HAS_DISCHARGE` | `:Member → :DischargeEvent` | CQ-01 |
| `DISCHARGED_FROM` | `:DischargeEvent → :Provider` | CQ-01 |
| `HAS_DIAGNOSIS` | `:DischargeEvent → :Diagnosis` | CQ-02 |
| `HAS_WORKFLOW` | `:Member → :WorkflowTrigger` | CQ-03 |
| `HAS_HEDIS_GAP` | `:Member → :HEDISGapFlag` | CQ-03 |
| `HAS_SDOH_FLAG` | `:Member → :SDOHFlag` | AW-05 |
| `ASSIGNED_TO` | `:WorkflowTrigger → :Provider` | AW-02 |

### Snowflake write permissions

The harvest agent requires `SELECT` on `ADT_DISCHARGE_EVENTS` and `UPDATE` on the `PROCESSED` and `PROCESSED_AT` columns. If write access cannot be granted, use the Snowflake Stream pattern (SQ-02) — the stream offset advances only on committed consumption, providing equivalent idempotency without a flag column.

### Adding a new domain (instantiation instructions)

The TOC constitution is one instance of a reusable architecture. To instantiate for a new domain (behavioral health, pharmacy, oncology):

1. Copy `INSTANCE_DATA` and replace all domain-specific fields: seed entities, P31 types, subclass signals, disciplines, assessment tools
2. Review all 16 rules — most are domain-agnostic, but R-03 (ICD-10 Z74 flagging) and R-08 (HCPCS assignment) need domain-specific code logic
3. Add domain-specific federation sources if needed; existing sources (ICD10_API, NPI_REGISTRY, LOINC) are reusable
4. Recompute the corpus fit gate criteria for the new domain's code sets
5. The capability cipher spec does not change — only the component values change

The Roman Republic constitution and the TOC constitution share identical cipher architecture, identical rule structure, and identical federation source patterns. The domain is encoded in the data, not in the infrastructure.

---

*Chrystallum Care Management Guide · Version 1.0*
*Transition of Care Domain · Snowflake → Neo4j → Agent Pipeline*
