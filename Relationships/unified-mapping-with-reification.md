# Canonical Relationship Types: Complete Ontology Mapping with Reification Analysis

**Version:** 3.0 - UNIFIED (Reification + CRM + CRMinf + Wikidata)  
**Date:** January 13, 2026  
**Scope:** 211 canonical relationship types across 18 semantic categories

**IMPORTANT CLARIFICATIONS:**
1. **CRMinf applies ONLY to Attribution & Citation** - tracks scholarly knowledge provenance
2. **Reification is critical** - 60-77% of relationships deserve first-class event nodes
3. **CIDOC CRM is universal** - provides ontology for all factual relationships

---

## Overview: The Three-Layer Architecture

### Layer 1: Factual Historical Relationships (CIDOC CRM)
Maps **what actually happened**: events, activities, states, relationships between entities

### Layer 2: Reified Event Nodes (High-Value Modeling)
Transforms 127+ canonical relationships from properties into event/activity nodes with:
- Temporal bounds (date, duration)
- Spatial location
- Multiple participants with roles
- Causes, motivations, outcomes
- Documentary sources

### Layer 3: Scholarly Attribution (CRMinf - Attribution Only)
Tracks **how we know** and **why we believe** historical claims:
- I7_Belief_Adoption - Citation of sources
- I5_Inference_Making - Scholarly reasoning
- J7 is_based_on_evidence - Evidentiary grounding

---

## TIER 1: MUST REIFY AS FIRST-CLASS EVENT NODES (127 relationships)

### Military Events (23 relationships)

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| FOUGHT_IN | Event Node | E7_Activity | participants, time, place, outcome | P17 (country) |
| BATTLED_IN | Event Node | E7_Activity | battlename, date, location, forces | — |
| DEFEATED | Event Node | E7_Activity | victor, vanquished, battle_ref, terms | — |
| DEFEATED_BY | Event Node | E7_Activity | (inverse: defeated) | — |
| BESIEGED | Event Node | E7_Activity | location, start_date, end_date, participants | — |
| BESIEGED_BY | Event Node | E7_Activity | (inverse: besieged) | — |
| CONQUERED | Event Node | E8_Acquisition | territory, date, conqueror, method, treaty | — |
| CONQUERED_BY | Event Node | E8_Acquisition | (inverse: conquered) | — |
| MASSACRED | Event Node | E7_Activity | location, victims, perpetrators, date | — |
| MASSACRED_BY | Event Node | E7_Activity | (inverse: massacred) | — |
| LEVELLED | Event Node | E6_Destruction | target, date, method, extent | — |
| LEVELLED_BY | Event Node | E6_Destruction | (inverse: levelled) | — |
| SACKED | Event Node | E7_Activity | location, date, pillage_extent, participants | — |
| SACKED_BY | Event Node | E7_Activity | (inverse: sacked) | — |
| COMMANDED_BY | Event Node | E7_Activity | commander, subordinate, period, authority | — |
| SERVED_UNDER | Event Node | E7_Activity | subordinate, commander, period, rank, unit | — |
| BETRAYED | Event Node | E7_Activity | actor, victim, date, circumstances | — |
| BETRAYED_BY | Event Node | E7_Activity | (inverse: betrayed) | — |
| DEFECTED_TO | Event Node | E85_Joining | defector, new_allegiance, date, from_allegiance | — |
| DEFECTED_FROM | Event Node | E86_Leaving | defector, old_allegiance, date, to_allegiance | — |
| GARRISONED | Event Node | E7_Activity | location, garrison_size, start_date, end_date | — |
| GARRISONED_BY | Event Node | E7_Activity | (inverse: garrisoned) | — |
| SALLIED_FROM | Event Node | E9_Move | origin, participants, date, destination, purpose | — |
| MILITARY_ACTION | Event Node | E7_Activity | participants, type_of_action, context | — |
| BATTLE_PARTICIPANT | Event Node | E7_Activity | (links actor to battle event) | — |

**Implementation Example (Reified Node):**
```turtle
:battle_actium a crm:E7_Activity ;
    rdfs:label "Battle of Actium" ;
    crm:P2_has_type :naval_battle ;
    crm:P4_has_time-span :timespan_31_09_02 ;
    crm:P7_took_place_at :actium ;
    crm:P11_had_participant :octavian, :mark_antony, :cleopatra ;
    crm:P14_carried_out_by :octavian ;
    crm:P123_resulted_in :octavian_supremacy ;
    crm:P70i_is_documented_in :plutarch_antony, :dio_cassius .
```

---

### Political Events (31 relationships)

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| APPOINTED | Event Node | E13_Attribute_Assignment | appointee, office, appointer, date, term | P39 (position held) |
| APPOINTED_BY | Event Node | E13_Attribute_Assignment | (inverse: appointed) | — |
| DEPOSED | Event Node | E86_Leaving | deposed_person, date, authority, successor | — |
| GOVERNED | Event Node | E7_Activity | governor, jurisdiction, start_date, end_date, policies | — |
| ALLIED_WITH | Event Node | E7_Activity | parties, date, treaty_type, terms, duration | — |
| ALLIED_VIA_MARRIAGE | Event Node | E7_Activity | bride, groom, date, tribes/states, terms | — |
| MARRIAGE_ALLIANCE_WITH | Event Node | E7_Activity | (political marriage as alliance event) | — |
| NEGOTIATED_WITH | Event Node | E7_Activity | negotiators, topics, date, location, outcome | — |
| NEGOTIATED_AGAINST | Event Node | E7_Activity | opposing_negotiators, context | — |
| COLLAPSED | Event Node | E64_End_of_Existence | polity, date, causes, successor_states | P576 (dissolved, abolished or demolished date) |
| CAUSED_COLLAPSE_OF | Event Node | E64_End_of_Existence | (inverse: collapsed) | — |
| CONTROLLED | Event Node | E7_Activity | controller, territory, start_date, end_date, type | P17 (country) |
| CONTROLLED_BY | Event Node | E7_Activity | (inverse: controlled) | — |
| DECLARED_FOR | Event Node | E7_Activity | declarer, recipient, date, context, publicity | — |
| DECLARED_FOR_BY | Event Node | E7_Activity | (inverse: declared_for) | — |
| OPPOSED | Event Node | E7_Activity | opponent1, opponent2, period, methods, issues | — |
| COMPETED_WITH | Event Node | E7_Activity | competitors, arena, period, outcomes | — |
| OUTLAWED | Event Node | E13_Attribute_Assignment | outlaw_person, authority, date, charges | — |
| OUTLAWED_BY | Event Node | E13_Attribute_Assignment | (inverse: outlawed) | — |
| PROSCRIBED | Event Node | E13_Attribute_Assignment | proscribed_person, proscription_list, date, property_confiscated | — |
| MANIPULATED | Event Node | E7_Activity | manipulator, manipulated_entity, date, methods, outcomes | — |
| MANIPULATED_BY | Event Node | E7_Activity | (inverse: manipulated) | — |
| ADVISED | Event Node | E7_Activity | advisor, advisee, topics, period, influence | — |
| LEGITIMATED | Event Node | E13_Attribute_Assignment | authority, legitimating_agent, date, mechanism | — |
| LEGITIMATED_BY | Event Node | E13_Attribute_Assignment | (inverse: legitimated) | — |
| GAINED_SOVEREIGNTY_OVER | Event Node | E7_Activity | entity, date, treaty, recognition | — |
| LOST_SOVEREIGNTY | Event Node | E7_Activity | entity, date, to_whom, treaty | — |
| DESIGNATED_HEIR_OF | Event Node | E13_Attribute_Assignment | heir, designator, date, announcement | — |
| HEIR_TO | Event Node | E13_Attribute_Assignment | (inverse: designated_heir_of) | — |
| HAS_TRIBUTARY | Event Node | E7_Activity | empire, tributary_state, date_range, tribute_type | — |
| APPLIES_TO_JURISDICTION | State Node | E3_Condition_State | law_or_office, jurisdiction, start_date, end_date | P1001 (applies to jurisdiction) |
| POLITICAL_CHANGE | Event Node | E5_Event | type_of_change, date, actors, outcomes | — |
| POLITICAL_CONTROL | State Node | E3_Condition_State | controller, territory, period | — |
| POLITICAL_STATUS | Property | P2_has_type | — | — |

---

### Diplomatic Events (12 relationships)

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| NEGOTIATED_WITH | Event Node | E7_Activity | negotiators, topics, date, location, outcome | — |
| SENT_ENVOYS_TO | Event Node | E7_Activity | sender, envoys, recipient, date, message | — |
| RECEIVED_ENVOYS_FROM | Event Node | E7_Activity | receiver, envoys, sender, date, message | — |
| APPEALED_TO | Event Node | E7_Activity | appellant, appealed_to, date, request, result | — |
| RECEIVED_APPEAL_FROM | Event Node | E7_Activity | recipient, appellant, date, request, result | — |
| ACCEPTED_OFFER | Event Node | E7_Activity | acceptor, offer_details, date, terms | — |
| OFFER_ACCEPTED_BY | Event Node | E7_Activity | (inverse: accepted_offer) | — |
| REJECTED_OFFER | Event Node | E7_Activity | rejector, offer_details, date, reasons | — |
| OFFER_REJECTED_BY | Event Node | E7_Activity | (inverse: rejected_offer) | — |
| OFFERED_SELF_TO | Event Node | E7_Activity | offeror, offered_to, date, terms, result | — |
| RECEIVED_OFFER_FROM | Event Node | E7_Activity | recipient, offeror, date, terms, result | — |
| DIPLOMATIC_ACTION | Event Node | E7_Activity | participants, type, date, context | — |

---

### Economic Events (12 relationships)

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| CONFISCATED_LAND_FROM | Event Node | E8_Acquisition | confiscator, owner, property, date, justification, value | — |
| LAND_CONFISCATED_BY | Event Node | E8_Acquisition | (inverse: confiscated_land_from) | — |
| DISTRIBUTED_LAND_TO | Event Node | E8_Acquisition | distributor, recipients, parcels, date, terms | — |
| LAND_DISTRIBUTED_BY | Event Node | E8_Acquisition | (inverse: distributed_land_to) | — |
| SOLD_INTO_SLAVERY | Event Node | E8_Acquisition | seller, buyer, enslaved, date, location, price | — |
| SOLD_INTO_SLAVERY_BY | Event Node | E8_Acquisition | (inverse: sold_into_slavery) | — |
| TAXED | Event Node | E7_Activity | taxer, taxed_entity, rate, period, enforcement | — |
| ECONOMIC_ACTION | Event Node | E7_Activity | participants, type_of_action, date, context | — |
| PRODUCED_BY | Event Node | E12_Production | producer, goods, quantity, period | P1056 (produced) |
| PRODUCES_GOOD | Event Node | E12_Production | (inverse: produced_by) | — |
| EXPERIENCED_RECESSION | Event Node | E5_Event | economy, period, severity, causes | — |
| RECESSION_IN | Event Node | E5_Event | (inverse: experienced_recession) | — |

---

### Legal Events (13 relationships)

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| CHARGED_WITH | Event Node | E13_Attribute_Assignment | accused, charges, court, date, prosecutor | — |
| CHARGES_AGAINST | Event Node | E13_Attribute_Assignment | (inverse: charged_with) | — |
| CONVICTED_OF | Event Node | E13_Attribute_Assignment | convicted, crime, court, date, evidence | P1399 (convicted of) |
| CONVICTION_OF | Event Node | E13_Attribute_Assignment | (inverse: convicted_of) | — |
| SENTENCED_TO | Event Node | E13_Attribute_Assignment | sentenced, punishment, judge, date, duration | — |
| SENTENCE_OF | Event Node | E13_Attribute_Assignment | (inverse: sentenced_to) | — |
| CONDEMNED_WITHOUT_TRIAL | Event Node | E13_Attribute_Assignment | condemned, authority, date, grounds | — |
| CONDEMNATION_OF | Event Node | E13_Attribute_Assignment | (inverse: condemned_without_trial) | — |
| EXECUTED | Event Node | E69_Death | executed, executor, date, method, location, authority | — |
| EXECUTED_BY | Event Node | E69_Death | (inverse: executed) | — |
| IMPRISONED_IN | Event Node | E7_Activity | prisoner, facility, start_date, end_date, conditions | — |
| IMPRISONMENT_OF | Event Node | E7_Activity | (inverse: imprisoned_in) | — |
| LEGAL_ACTION | Event Node | E7_Activity | participants, legal_action_type, date, context | — |

---

### Geographic Events (18 relationships)

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| BORN_IN | Event Node | E67_Birth | person, location, date, parents | P19 (place of birth) |
| BIRTHPLACE_OF | Event Node | E67_Birth | (inverse: born_in) | — |
| DIED_IN | Event Node | E69_Death | person, location, date, cause | P20 (place of death) |
| DEATH_PLACE_OF | Event Node | E69_Death | (inverse: died_in) | — |
| FOUNDED | Event Node | E63_Beginning_of_Existence | place, founder, date, charter, context | P112 (founded by) |
| MIGRATED_TO | Event Node | E9_Move | group, destination, date, route, causes | — |
| MIGRATED_FROM | Event Node | E9_Move | group, origin, date, route, causes | — |
| EXILED | Event Node | E9_Move | exiled_person, destination, authority, date, duration | — |
| EXILED_BY | Event Node | E9_Move | authority, exiled_person, (inverse: exiled) | — |
| FLED_TO | Event Node | E9_Move | fleeing_person, destination, date, cause | — |
| FLED_FROM | Event Node | E9_Move | fleeing_person, origin, date, cause | — |
| LIVED_IN | State Node | E7_Activity | resident, location, start_date, end_date, status | — |
| RESIDENCE_OF | State Node | E7_Activity | (inverse: lived_in) | — |
| LOCATED_IN | Property | P53_has_former_or_current_location | — | — |
| LOCATION_OF | Property | P53i_is_former_or_current_location_of | — | — |
| CAMPAIGN_IN | Event Node | E7_Activity | campaign, location, date, participant | — |
| RENAMED | Event Node | E15_Identifier_Assignment | entity, old_name, new_name, date, authority | P1448 (official name) |
| RENAMED_TO | Event Node | E15_Identifier_Assignment | (inverse: renamed) | — |

---

### Authorship Events (12 relationships) - SELECTIVE Reification

| Canonical Relationship | Reify As | CIDOC CRM Class | Keep Simple When | Wikidata |
|---|---|---|---|---|
| AUTHOR | Property | P94_has_created | Simple attribution | P50 (author) |
| WORK_OF | Property | P94i_was_created_by | Simple attribution | — |
| CREATOR | Property | P94_has_created | Simple attribution | P170 (creator) |
| CREATION_OF | Property | P94i_was_created_by | Simple attribution | — |
| COMPOSER | Property | P94_has_created | Simple attribution | P86 (composer) |
| COMPOSITION_OF | Property | P94i_was_created_by | Simple attribution | — |
| ARCHITECT | Property | P94_has_created | Simple attribution | P84 (architect) |
| DESIGNED | Property | P94i_was_created_by | Simple attribution | — |
| DISCOVERED_BY | Event Node | E13_Attribute_Assignment | **Reify when significant** - has date, discoverer, method | P61 (discoverer) |
| DISCOVERER_OF | Event Node | E13_Attribute_Assignment | (inverse: discovered_by) | — |
| COMMISSIONED | Event Node | E7_Activity | **Reify when important** - has contract, date, terms, payment | — |
| COMMISSIONED_BY | Event Node | E7_Activity | (inverse: commissioned) | — |

**Rationale:** Creation is typically attributed to a person (property), but discovery and commissioning are events with dates and context.

---

### Honorific Events (8 relationships) - Reify When Ceremonial

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| AWARDED_TO | Event Node | E13_Attribute_Assignment | award, recipient, awarder, date, location, citation | P166 (award received) |
| AWARD_RECEIVED | Event Node | E13_Attribute_Assignment | (inverse: awarded_to) | — |
| GRANTED_TITLE | Event Node | E13_Attribute_Assignment | title, grantee, grantor, date, patent, ceremony | — |
| TITLE_GRANTED_BY | Event Node | E13_Attribute_Assignment | (inverse: granted_title) | — |
| DECORATED_WITH | Event Node | E13_Attribute_Assignment | decoration, recipient, date, battle/service, authority | — |
| DECORATION_OF | Event Node | E13_Attribute_Assignment | (inverse: decorated_with) | — |
| HONORED | Event Node | E13_Attribute_Assignment | honored_person, honor_type, date, occasion | — |
| HONORED_BY | Event Node | E13_Attribute_Assignment | (inverse: honored) | — |

---

### Institutional Events (9 relationships)

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| APPOINTED (institutional) | Event Node | E13_Attribute_Assignment | (office appointment) | P39 |
| APPOINTED_BY | Event Node | E13_Attribute_Assignment | (inverse) | — |
| REFORMED | Event Node | E11_Modification | institution, reformer, date, changes, legislation, effects | — |
| REFORMED_BY | Event Node | E11_Modification | (inverse: reformed) | — |
| REINSTATED | Event Node | E63_Beginning_of_Existence | institution, date, authority, prior_abolition | — |
| REINSTATED_BY | Event Node | E63_Beginning_of_Existence | (inverse: reinstated) | — |
| LEGITIMATED | Event Node | E13_Attribute_Assignment | authority, legitimating_agent, date, mechanism | — |
| LEGITIMATED_BY | Event Node | E13_Attribute_Assignment | (inverse: legitimated) | — |
| INSTITUTIONAL_ACTION | Event Node | E7_Activity | participants, action_type, date, context | — |

---

### Membership Events (2 relationships)

| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties | Wikidata |
|---|---|---|---|---|
| MEMBER_OF | Event Node | E85_Joining | member, group, date_joined, admission_process, duration | — |
| HAS_MEMBER | Event Node | E85_Joining | (inverse: member_of) | — |

**Note:** Membership changes are best modeled as E85_Joining (entry) and E86_Leaving (exit) events.

---

### Familial Events (2 relationships as EVENTS; 28 as PROPERTIES)

#### Reify as Events (when ceremonial/legal):
| Canonical Relationship | Reify As | CIDOC CRM Class | Key Node Properties |
|---|---|---|---|
| ADOPTED | Event Node | E85_Joining | adoptee, adoptive_parents, date, court, legal_basis |
| ADOPTED_BY | Event Node | E85_Joining | (inverse: adopted) |

#### Keep as Simple Properties (biological):
| Canonical Relationship | Keep As | CIDOC CRM Property | Justification |
|---|---|---|---|
| PARENT_OF | Property | P152_has_parent | Biological fact |
| CHILD_OF | Property | P152i_is_parent_of | Biological fact |
| FATHER_OF | Property | P97_from_father | Biological fact |
| MOTHER_OF | Property | P96_by_mother | Biological fact |
| SIBLING_OF | Property | P107_has_member (family) | Biological/structural fact |
| SPOUSE_OF | Property | P107_has_member (family) | Relational (unless marriage event is important) |
| GRANDPARENT_OF | Property | P152_has_parent_chain | Derived from parent relations |
| GRANDCHILD_OF | Property | P152_has_parent_chain | Derived from parent relations |
| [All in-law relations] | Property | P107_has_member (family group) | Family structure |
| STEPPARENT_OF, STEPCHILD_OF | Property | P107_has_member (family) | Legal/social fact (or reify adoption) |
| FATHER_IN_LAW_OF, etc. | Property | P107_has_member (family) | Relational through marriage |
| UNCLE_OF, AUNT_OF, COUSIN_OF, NEPHEW_OR_NIECE_OF | Property | P107_has_member (family) | Extended family structure |
| HALF_SIBLING_OF | Property | P107_has_member (family) | Biological structure |

---

## TIER 2: OPTIONAL REIFICATION (Context-Dependent) - 36 relationships

### Attribution & Citation (15 relationships) - Reify for Scholarly Context Only

| Canonical Relationship | Reify As | CRMinf Usage | When to Reify | Wikidata |
|---|---|---|---|---|
| ANALYZES | Optional Event Node | I5_Inference_Making + J3 | When tracking scholarly interpretations | — |
| ATTRIBUTED_TO | Optional Event Node | I7_Belief_Adoption + J6 | When tracking source attribution | — |
| DESCRIBES | Optional Event Node | I7_Belief_Adoption + J7 | When linking source document | — |
| EXTRACTED_FROM | Optional Event Node | I7_Belief_Adoption + J6 | When tracking textual quotation | — |
| INTERPRETS | Optional Event Node | I5_Inference_Making + J3 | When tracking hermeneutic chains | — |
| MENTIONS | Optional Event Node | I7_Belief_Adoption + J7 | When source is reference point | — |
| QUOTES | Optional Event Node | I7_Belief_Adoption + J7 | Always reify (direct quotation) | — |
| SUMMARIZES | Optional Event Node | I7_Belief_Adoption + J7 | When summarizing source | — |
| NAME | Property | — | Keep as P1_is_identified_by | P2561 (name) |
| NAMED_AFTER | Property | — | Keep as P138_represents | P138 (named after) |
| NAMESAKE_OF | Property | — | Keep as P138i_has_representation | — |

**CRMinf Pattern (When Reifying Attribution):**
```turtle
:scholar_claim a crminf:I2_Belief ;
    crminf:J4_that :historical_proposition_set ;
    crminf:J5_holds_to_be "true"^^xsd:boolean ;
    crminf:J2i_was_concluded_by :scholarly_analysis .

:scholarly_analysis a crminf:I7_Belief_Adoption ;
    crminf:J6_adopted :source_belief ;
    crminf:J7_is_based_on_evidence :primary_source_document ;
    crm:P14_carried_out_by :historian .
```

---

### Cultural Events (8 relationships) - Selective Reification

| Canonical Relationship | Reify As | CIDOC CRM Class | When to Reify | Wikidata |
|---|---|---|---|---|
| ASSIMILATED_TO | Event Node | E7_Activity | **Reify for historical process** - has timeline | — |
| ASSIMILATED | Event Node | E7_Activity | (inverse: assimilated_to) | — |
| EVOLVED_FROM | Event Node | E81_Transformation | **Reify for form development** - genealogy | — |
| EVOLVED_INTO | Event Node | E81_Transformation | (inverse: evolved_from) | — |
| CLAIMS_HERITAGE_FROM | Event Node | E7_Activity | **Reify for political act** - date, declaration | — |
| HERITAGE_OF | Event Node | E7_Activity | (inverse: claims_heritage_from) | — |
| ORIGIN_MYTH | Property | P67_refers_to | Keep as simple reference | — |
| MYTHIC_ORIGIN_OF | Property | P67i_is_referred_to_by | Keep as simple reference | — |

---

## TIER 3: KEEP AS SIMPLE PROPERTIES (48 relationships)

### Application & Material (4 relationships)
| Canonical Relationship | Keep As | CIDOC CRM Property | Wikidata |
|---|---|---|---|
| MATERIAL_IN | Property | P45_consists_of | — |
| MATERIAL_USED | Property | P45i_is_incorporated_in | P186 (made from) |
| USE | Property | P101_had_as_general_use | P366 (has use) |
| USED_BY | Property | P101i_was_use_of | — |

---

### Causality (8 relationships)
| Canonical Relationship | Keep As | CIDOC CRM Property | Justification |
|---|---|---|---|
| CAUSED_BY | Property | P15_was_influenced_by | Causal link (simple) |
| CONTRIBUTED_BY | Property | P15i_influenced | Contributing factor |
| CONTRIBUTED_TO | Property | P15i_influenced | Contributing outcome |
| CAUSED | Property | P15i_influenced | (Inverse causality) |
| ACTION_JUSTIFIED_BY | Property | P17_was_motivated_by | Motivation |
| JUSTIFIED_ACTION | Property | P17i_motivated | (Inverse motivation) |
| MARKED_START | Property | P134_continued | Continuity relation |
| START_MARKED_BY | Property | P134i_was_continued_by | (Inverse continuity) |

---

### Ideological (2 relationships)
| Canonical Relationship | Keep As | CIDOC CRM Property | Wikidata |
|---|---|---|---|
| ADHERES_TO | Property | P2_has_type | P1142 (ideology) |
| IDEOLOGY_OF | Property | P2i_is_type_of | — |

---

### Linguistic (2 relationships)
| Canonical Relationship | Keep As | CIDOC CRM Property | Wikidata |
|---|---|---|---|
| SPOKE_LANGUAGE | Property | P72_has_language | P1412 (languages) |
| LANGUAGE_OF | Property | P72i_is_language_of | — |

---

### Measurement (2 relationships)
| Canonical Relationship | Keep As | CIDOC CRM Property | Justification |
|---|---|---|---|
| HAS_INDICATOR | Property | P43_has_dimension | Quantitative property |
| INDICATOR_OF | Property | P43i_is_dimension_of | (Inverse) |

---

### Familial - Biological Only (28 relationships)
| Canonical Relationship | Keep As | CIDOC CRM Property | Wikidata |
|---|---|---|---|
| PARENT_OF | Property | P152_has_parent | — |
| CHILD_OF | Property | P152i_is_parent_of | — |
| FATHER_OF | Property | P97_from_father | — |
| MOTHER_OF | Property | P96_by_mother | — |
| SIBLING_OF | Property | P107_has_member | — |
| SPOUSE_OF (biological only) | Property | P107_has_member | — |
| [All extended family] | Property | P107_has_member (family group) | — |

---

## Summary Statistics

| Tier | Category | Count | Must Reify | Optional | Keep as Property |
|---|---|---|---|---|---|
| 1 | Military | 23 | 23 | 0 | 0 |
| 1 | Political | 31 | 31 | 0 | 0 |
| 1 | Diplomatic | 12 | 12 | 0 | 0 |
| 1 | Economic | 12 | 12 | 0 | 0 |
| 1 | Legal | 13 | 13 | 0 | 0 |
| 1 | Geographic | 18 | 18 | 0 | 0 |
| 1 | Honorific | 8 | 8 | 0 | 0 |
| 1 | Institutional | 9 | 9 | 0 | 0 |
| 1 | Membership | 2 | 2 | 0 | 0 |
| 1 | Authorship | 12 | 0 | 4 | 8 |
| 2 | Attribution | 15 | 0 | 15 | 0 |
| 2 | Cultural | 8 | 0 | 8 | 0 |
| 3 | Familial (events) | 2 | 0 | 0 | 28 |
| 3 | Application | 4 | 0 | 0 | 4 |
| 3 | Causality | 8 | 0 | 0 | 8 |
| 3 | Ideological | 2 | 0 | 0 | 2 |
| 3 | Linguistic | 2 | 0 | 0 | 2 |
| 3 | Measurement | 2 | 0 | 0 | 2 |
| 3 | Moral | 2 | 0 | 0 | 2 |
| — | **TOTAL** | **211** | **139** | **27** | **45** |

**Reification Rate: 66% MUST REIFY + 13% OPTIONAL = 79% Event-Centric Design**

---

## Implementation Patterns for Web Application

### Pattern 1: Event-Centric Query (Reified Node)
```sparql
# Find all battles where person was a commander
SELECT ?battle ?date ?opponent ?location WHERE {
  ?battle a crm:E7_Activity ;
          crm:P2_has_type :battle ;
          crm:P14_carried_out_by ?commander ;
          crm:P11_had_participant ?opponent ;
          crm:P4_has_time-span ?date ;
          crm:P7_took_place_at ?location .
  FILTER(?commander = :octavian)
  FILTER(?opponent != :octavian)
}
```

### Pattern 2: State Node Query (Lived-In)
```sparql
# Find all periods person lived in a location
SELECT ?location ?start_date ?end_date WHERE {
  ?residence a crm:E7_Activity ;
             crm:P14_carried_out_by :person ;
             crm:P7_took_place_at ?location ;
             crm:P4_has_time-span ?timespan .
  ?timespan crm:P82_at_some_time_within ?start_date ;
            crm:P82_at_some_time_within ?end_date .
}
```

### Pattern 3: Simple Property Query (Biological Kinship)
```sparql
# Find all parents of a person (simple property)
SELECT ?parent WHERE {
  ?person crm:P152_has_parent ?parent .
}
```

### Pattern 4: Attribution with CRMinf (Citation Tracking)
```sparql
# Find scholarly claims about events with sources
SELECT ?claim ?event ?source ?author WHERE {
  ?claim a crminf:I2_Belief ;
         crminf:J4_that ?propositions ;
         crminf:J2i_was_concluded_by ?analysis .
  ?analysis a crminf:I7_Belief_Adoption ;
            crminf:J7_is_based_on_evidence ?source ;
            crm:P14_carried_out_by ?author .
  # Link belief to historical event if available
  ?propositions crm:P67_refers_to ?event .
}
```

---

## Choosing Between Reification and Properties

### Decision Tree:

**Q1: Does the relationship have a date?**
- YES → Likely an EVENT (reify)
- NO → Continue to Q2

**Q2: Does it have a location?**
- YES → Likely an EVENT (reify)
- NO → Continue to Q3

**Q3: Does it have multiple participants with different roles?**
- YES → Reify as EVENT
- NO → Continue to Q4

**Q4: Does it have context, causes, or consequences?**
- YES → Reify as EVENT
- NO → Q5

**Q5: Is it inherent/definitional (material, biological, type)?**
- YES → Keep as PROPERTY
- NO → Reify as EVENT

### Examples:
- ✅ **BESIEGED** (date: specific day, location: city, participants: defender/attacker, duration: months) → REIFY
- ✅ **GOVERNED** (date range: years, location: jurisdiction, actions: laws/policies) → REIFY
- ❌ **CHILD_OF** (no date needed, inherent biological fact) → PROPERTY
- ❌ **MATERIAL_IN** (composition doesn't change, timeless) → PROPERTY
- ✓ **AUTHOR** (simple attribution; reify only if creation process is important) → DEFAULT PROPERTY

---

## Recommendations for Your World-Building Application

**For Historical Model Railroads & Knowledge Bases:**

1. **Always reify military, political, and diplomatic events** - These are queryable narrative arcs
2. **Reify geographic movements** (migration, founding, exile) - Central to world building
3. **Keep biological relationships as properties** - More efficient for kinship queries
4. **Use CRMinf sparingly** - Only when scholarly interpretation matters
5. **Leverage reified nodes for timeline visualization** - Sort by P4_has_time-span for chronology
6. **Enable source attribution on critical events** - Link to P70_documents for provenance
7. **Use state nodes for occupations, residencies, and administrative control** - E7_Activity with start/end dates

This hybrid approach gives you:
- **Semantic richness** for complex historical events
- **Query efficiency** for genealogical and geographical lookups
- **Narrative power** for timeline and causation analysis
- **Scholarly accountability** through CRMinf on critical claims

---

**Document Version:** 3.0  
**Last Updated:** January 13, 2026  
**Status:** Complete & Unified (Reification + Ontology + Scholarly Attribution)
