# Biographic SFA Ontology Building Methodology

**Document Status:** Implementation Guide  
**Date:** February 16, 2026  
**Context:** Training Phase - Independent Domain Ontology Building  
**Related:** [SCA_SFA_ROLES_DISCUSSION.md](../md/Agents/SCA/SCA_SFA_ROLES_DISCUSSION.md) - Training Phase  
**Cross-Reference:** [MILITARY_SFA_ONTOLOGY_METHODOLOGY.md](MILITARY_SFA_ONTOLOGY_METHODOLOGY.md)

---

## Overview

This document defines the **filtering methodology** for the Biographic Specialist Facet Agent (SFA) to extract a clean prosopographic ontology from Wikidata and external databases during the **Training Phase** (independent domain study).

**Goal:** Build a semantically coherent prosopographic ontology grounded in biographical and prosopographic studies as academic disciplines, focusing on person identity, careers, status, and networks.

**Scope:** Generic prosopography → Roman Republic specialization (DPRR integration)

**Key Insight:** Biographic facet is **producer** of person nodes that other facets (Military, Political, etc.) **consume** as references.

### Primary Responsibilities

The Biographic SFA has three critical producer roles:

1. **Person Identity & Career Structure**
   - Creates person nodes (Q5 instances) with canonical IDs
   - Builds career sequences (office progressions)
   - Defines status markers (senatorial, equestrian, plebeian)
   - Enforces temporal constraints (cursus honorum requirements)

2. **Family Tree & Relationship Network Construction** 🔥 CRITICAL
   - Constructs family trees (genealogical stemma)
   - Maps kinship relations (parent-child, sibling, spouse)
   - Identifies gens membership (clan structures)
   - Models adoption patterns (critical in Roman society)
   - Maps marriage alliances (political marriages)
   - Defines **canonical relationship types** (see Section 2.F)
   - Creates relationship claims with proper directionality

3. **Biographical Event Proposal** 🔥 NEW ROLE
   - **Proposes event claims** that other facets analyze:
     * Birth/death events (with dates, locations)
     * Office appointments (consulship, praetorship, etc.)
     * Marriage events (alliance formation)
     * Adoption events (status/inheritance changes)
   - Other facets consume these events for their analyses:
     * Political SFA: "Caesar's consulship in 59 BCE" (power structure)
     * Military SFA: "Caesar's proconsulship in Gaul" (command authority)
     * Social SFA: "Pompey-Julia marriage" (class alliance)
   - **Seeder role:** Biographic events are **temporal anchors** for multi-facet analysis

---

## 1. Anchor: Prosopography as Discipline

### Disciplinary Root

**Start Node:** `prosopography (Q783287)`  
**Rationale:** Treat prosopography as the scholarly discipline root - the systematic study of persons within a defined historical context through structured biographical data.

**Wikidata:** https://www.wikidata.org/wiki/Q783287  
**Wikipedia:** https://en.wikipedia.org/wiki/Prosopography  
**Scholarly Reference:** [Digital Prosopography of the Roman Republic (DPRR)](https://romanrepublic.ac.uk)

### Secondary Anchors

| Anchor QID | Label | Purpose |
|------------|-------|---------|
| **Q36180** | writer biography | Biographical narrative methodology |
| **Q2990593** | career | Office sequences, professional trajectories |
| **Q4164871** | life history | Chronological life events |
| **Q5** | human | Entity type root (all persons) |
| **Q294414** | social class | Status markers (senatorial, equestrian, plebeian) |

### Key Properties from Discipline Root

| Property | Purpose | Example Targets |
|----------|---------|-----------------|
| **P31** (instance of) | Person identification | Q5 (human) |
| **P39** (position held) | Offices, magistracies | consul, praetor, quaestor |
| **P106** (occupation) | Professional roles | politician, general, orator |
| **P27** (country of citizenship) | Polity membership | Roman Republic, Roman Empire |
| **P53** (family) | Lineage, gens | gens Julia, gens Cornelia |
| **P22/P25** (father/mother) | Parentage | Family trees |
| **P26** (spouse) | Marriage alliances | Political marriages |
| **P103** (native language) | Cultural identity | Latin, Greek |
| **P945** (allegiance) | Political/military loyalty | Roman Republic |

**Navigation Pattern:**
```
Q783287 (prosopography)
  ├─[P31]→ Q5 (human) [ALL PERSONS]
  │   ├─[P39]→ offices/magistracies
  │   ├─[P106]→ occupations
  │   ├─[P53]→ family/gens
  │   └─[P569/P570]→ birth/death dates
  ├─[P527]→ Q2990593 (career)
  │   └─[components]→ career stages
  └─[P279]→ biographical methods
```

---

## 2. Inclusion Criteria for Ontology Nodes

A Wikidata item should be **included** in the biographic ontology if it satisfies **most** of:

### A. Person-Centric Entities

**Criteria:**
- Is `P31` (instance of) = `Q5` (human) OR subclasses:
  * politician
  * military personnel
  * magistrate
  * senator
  * orator
  * historian
  * priest
- Has biographical data relevant to historical reconstruction:
  * Offices held (P39)
  * Family relations (P22, P25, P26, P53)
  * Birth/death dates (P569, P570)
  * Place of birth/death (P19, P20)
  * Social status markers

**Example:**
```cypher
// Good: Person with prosopographic data
(Q1048:Human {label: "Julius Caesar"})
  -[:P39]-> (Q20056508:Office {label: "Roman consul", year: -59})
  -[:P53]-> (Q188646:Gens {label: "gens Julia"})
  -[:P569]-> (date: "-0100-07-12")

// Bad: Person without historical context
(Q12345678:Human {label: "Modern person"})
  -[:P31]-> (Q5:human)
  // No historical offices, no ancient context
```

### B. Status and Social Structure

**Criteria:**
- Defines social hierarchy or status categories:
  * Orders: senatorial order (ordo senatorius), equestrian order (ordo equester)
  * Classes: patrician, plebeian, freedman, slave
  * Citizenship: Roman citizen, Latin right, peregrinus
  * Tribal membership: tribus (voting districts)

**Example:**
```cypher
// Social status ontology
(Q2912932:SocialClass {label: "senatorial order"})
  -[:P279]-> (Q294414:social_class)
  -[:P361]-> (Q17167:Roman_social_structure)
```

### C. Offices and Magistracies

**Criteria:**
- Political or military positions within defined polity:
  * Cursus honorum: quaestor → aedile → praetor → consul
  * Military commands: legatus, tribune, proconsul
  * Priesthoods: pontifex, augur, flamen
  * Special offices: dictator, censor, tribune of the plebs

**Test:** Does this office appear in standard prosopographic references (Broughton's *Magistrates of the Roman Republic*, DPRR)?

**Example:**
```cypher
// Office hierarchy
(Q20056508:Office {label: "Roman consul"})
  -[:P279]-> (Q83307:magistrate)
  -[:P361]-> (Q1747689:cursus_honorum)
  -[:term_length]-> "1 year"
  -[:eligibility]-> (Q2912932:senatorial_order)
```

### D. Family and Kinship Structures

**Criteria:**
- Family units relevant to prosopographic networks:
  * Gentes (clans): gens Julia, gens Cornelia, gens Claudia
  * Marriage alliances (political marriages)
  * Adoption patterns (e.g., Caesar adopted Octavian)
  * Lineages (stemma, family trees)

**Example:**
```cypher
// Family network
(Q188646:Gens {label: "gens Julia"})
  -[:P527]-> (Q1048:Human {label: "Julius Caesar"})
  -[:P527]-> (Q1405:Human {label: "Augustus"})  // adopted
  -[:alliance_via_marriage]-> (Q188437:Gens {label: "gens Pompeia"})
```

### F. Canonical Relationship Types (Biographic Ontology)

**Criteria:**
- BiographicSFA defines **standardized relationship types** that all agents use:

**Family Relationships (Blood/Legal):**
- `CHILD_OF` / `PARENT_OF` (directionality matters!)
- `SIBLING_OF` (symmetric)
- `SPOUSE_OF` (symmetric, with temporal scope for marriages)
- `ADOPTED_BY` / `ADOPTED` (Roman adoption was legally equivalent to birth)
- `GRANDPARENT_OF` / `GRANDCHILD_OF`
- `COUSIN_OF` (various degrees)

**Clan/Gens Relationships:**
- `MEMBER_OF_GENS` (membership in patrician/plebeian clan)
- `FOUNDER_OF_GENS` (legendary/historical founder)
- `COGNOMEN_BRANCH` (sub-branch within gens, e.g., Cornelii Scipiones)

**Social/Political Relationships:**
- `PATRON_OF` / `CLIENT_OF` (patron-client relationship, critical in Roman society)
- `POLITICAL_ALLY_OF` (temporary/permanent alliances)
- `POLITICAL_RIVAL_OF` (factional opposition)
- `MENTOR_OF` / `MENTORED_BY` (educational/political mentorship)
- `FRIEND_OF` (amicitia, with political implications)
- `ENEMY_OF` (inimicitia, declared enmity)

**Marriage Alliances:**
- `MARRIED` (with start/end dates, divorce tracking)
- `BETROTHED_TO` (engagement, politically significant)
- `FATHER_IN_LAW_OF` / `SON_IN_LAW_OF` (affinal relationships)

**Example:**
```cypher
// Canonical relationship claim
(C_bio_rel:FacetClaim {
  cipher: "fclaim_bio_rel_001...",
  facet: "biographic",
  subject_node_id: "Q1048",  // Caesar
  property_path_id: "CHILD_OF",  // Canonical type
  object_node_id: "Q????",  // C. Julius Caesar (father)
  temporal_scope: "-0100",  // Birth year
  source_document_id: "Q1385",  // Suetonius
  assertion: "Caesar son of C. Julius Caesar (praetor)"
})

// Marriage alliance (political significance)
(C_bio_marriage:FacetClaim {
  cipher: "fclaim_bio_rel_002...",
  facet: "biographic",
  subject_node_id: "Q1048",  // Caesar
  property_path_id: "MARRIED",
  object_node_id: "Q230677",  // Cornelia Cinna
  temporal_scope: "-0084",  // Marriage year
  end_temporal_scope: "-0069",  // Her death
  source_document_id: "Q1385"
})

// Adoption (legally creates parent-child bond)
(C_bio_adoption:FacetClaim {
  cipher: "fclaim_bio_rel_003...",
  facet: "biographic",
  subject_node_id: "Q1405",  // Octavian/Augustus
  property_path_id: "ADOPTED_BY",
  object_node_id: "Q1048",  // Caesar
  temporal_scope: "-0044",  // In Caesar's will
  source_document_id: "Q1385",
  assertion: "Octavian adopted by Caesar in will, became C. Julius Caesar Octavianus"
})
```

### E. Career Sequencing and Eligibility

**Criteria:**
- Concepts that define **temporal constraints** on career progression:
  * Minimum ages for offices (cursus honorum requirements)
  * Prerequisites (must hold X before Y)
  * Term limits (consul: 1 year, restrictions on iteration)
  * Promagistracies (proconsul, propraetor)

**Example:**
```cypher
// Career constraints
(Q20056508:Office {label: "Roman consul"})
  -[:minimum_age]-> "42 years"
  -[:prerequisite]-> (Q40779:Office {label: "praetor"})
  -[:interval_required]-> "2 years minimum between consulships"
```

---

## 3. Exclusion Criteria (Noise Filtering)

A Wikidata item should be **excluded** if it matches:

### A. Modern Biographical Artifacts

**Exclude:**
- Wikipedia categories: `Category:Roman Republic people`, `Category:1st-century BC Romans`
- Wikimedia projects: Wikipedia articles, Wikibooks, Commons files
- Modern scholarship: Books *about* Romans (not primary sources)

**Example:**
```cypher
// ❌ Exclude: Wikipedia category
(Q4167836:Wikimedia_category {label: "Category:Roman Republic"})

// ❌ Exclude: Modern book
(Q12345:Book {label: "A History of Rome", author: "Modern Scholar"})

// ✅ Include: Ancient source
(Q47461:Work {label: "The Histories", author: "Polybius"})
```

### B. Anachronistic Concepts

**Exclude:**
- Modern nation-states: Italy, France (as modern polities)
- Contemporary terms: "democracy" (anachronistic for Roman Republic)
- Modern academic concepts without ancient equivalents

**Test:** Would an ancient Roman recognize this concept? If no → exclude from prosopographic ontology.

### C. Media and Popular Culture

**Exclude:**
- Films, TV shows, video games about Romans
- Modern artistic representations
- Tourist sites (modern context)

**Example:**
```cypher
// ❌ Exclude: Film
(Q34079:Film {label: "Julius Caesar", year: 1953})

// ✅ Include: Ancient representation
(Q12345:Sculpture {label: "Bust of Caesar", date: "-44"})
```

### D. Cross-Domain Clutter

**Exclude from biographic ontology** (but may be relevant to other facets):
- Military tactics (belongs to Military facet)
- Economic systems (belongs to Economic facet)
- Religious rituals (belongs to Religious facet)

**Biographic facet focus:** WHO the person was, WHAT positions they held, WHEN they lived, WHO they were related to.

**Other facets focus:** WHAT the person DID in their domain (military campaigns, economic policy, religious reforms).

---

## 4. Wikidata Query Patterns for Training

### A. Person Discovery (Roman Republic Scope)

```sparql
# Find all persons associated with Roman Republic
SELECT DISTINCT ?person ?personLabel ?birth ?death WHERE {
  # Person entity
  ?person wdt:P31 wd:Q5 .  # instance of human
  
  # Temporal constraint: Born before end of Republic (-27 BCE)
  ?person wdt:P569 ?birth .
  FILTER(YEAR(?birth) < -26 && YEAR(?birth) > -600)
  
  # Geographic/polity constraint
  {
    ?person wdt:P27 wd:Q17167 .  # country: Roman Republic
  } UNION {
    ?person wdt:P39 ?office .
    ?office wdt:P361 wd:Q1747689 .  # office part of cursus honorum
  } UNION {
    ?person wdt:P39 wd:Q20056508 .  # position held: Roman consul
  }
  
  # Deduplication and labeling
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT 5000
```

### B. Office Hierarchy Discovery

```sparql
# Find all Roman magistracies and their relationships
SELECT ?office ?officeLabel ?superclass ?superclassLabel WHERE {
  # Magistracy identification
  ?office wdt:P31/wdt:P279* wd:Q83307 .  # instance/subclass of magistrate
  
  # Roman context
  {
    ?office wdt:P361 wd:Q1747689 .  # part of cursus honorum
  } UNION {
    ?office wdt:P17 wd:Q17167 .  # country: Roman Republic
  }
  
  # Hierarchy
  OPTIONAL { ?office wdt:P279 ?superclass }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
```

### C. Family Network Discovery

```sparql
# Find gens (clan) structures and family relationships
SELECT ?gens ?gensLabel ?member ?memberLabel ?father ?mother ?spouse WHERE {
  # Gens identification
  ?gens wdt:P31 wd:Q177251 .  # instance of gens (Roman clan)
  
  # Members
  ?member wdt:P53 ?gens .  # family: belongs to gens
  ?member wdt:P31 wd:Q5 .   # is human
  
  # Family relationships
  OPTIONAL { ?member wdt:P22 ?father }  # father
  OPTIONAL { ?member wdt:P25 ?mother }  # mother
  OPTIONAL { ?member wdt:P26 ?spouse }  # spouse
  
  # Temporal constraint (Republican era)
  ?member wdt:P569 ?birth .
  FILTER(YEAR(?birth) < -26 && YEAR(?birth) > -600)
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT 1000
```

### D. Biographical Event Discovery

```sparql
# Find key biographical events (birth, death, marriage, office appointments)
SELECT ?person ?personLabel ?eventType ?eventDate ?eventLocation WHERE {
  # Person from Roman Republic
  ?person wdt:P31 wd:Q5 .
  ?person wdt:P27 wd:Q17167 .  # citizen of Roman Republic
  
  # Event types
  {
    # Birth event
    ?person wdt:P569 ?eventDate .
    OPTIONAL { ?person wdt:P19 ?eventLocation }  # place of birth
    BIND("birth" AS ?eventType)
  } UNION {
    # Death event
    ?person wdt:P570 ?eventDate .
    OPTIONAL { ?person wdt:P20 ?eventLocation }  # place of death
    BIND("death" AS ?eventType)
  } UNION {
    # Office appointment
    ?person wdt:P39 ?office .
    ?office wdt:P580 ?eventDate .  # start time of position
    BIND("office_appointment" AS ?eventType)
  }
  
  # Temporal constraint
  FILTER(YEAR(?eventDate) < -26 && YEAR(?eventDate) > -600)
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT 2000
```

---

## 5. Roman Republic Specialization

### A. DPRR Integration (Digital Prosopography of the Roman Republic)

**External Database:** https://romanrepublic.ac.uk

**DPRR provides:**
- Person IDs (DPRR_n format): Unique identifiers for ~10,000 individuals
- Office attestations: Every recorded magistracy with sources
- Family relationships: Stemma reconstructions
- Status markers: Senatorial/equestrian classifications
- Chronological sequences: Career timelines

**Integration Pattern:**
```python
# BiographicSFA queries DPRR API
person_data = dprr_client.get_person(dprr_id="DPRR_1")  # Caesar

# Returns:
{
    "dprr_id": "DPRR_1",
    "name": "C. Iulius Caesar",
    "wikidata_qid": "Q1048",
    "offices": [
        {"office": "quaestor", "year": -69, "source": "Broughton MRR II.132"},
        {"office": "aedile", "year": -65, "source": "Broughton MRR II.156"},
        {"office": "praetor", "year": -62, "source": "Broughton MRR II.174"},
        {"office": "consul", "year": -59, "source": "Broughton MRR II.188"}
    ],
    "gens": "Julia",
    "father": "DPRR_2",
    "status": "senatorial",
    "birth_year": -100,
    "death_year": -44
}
```

**Claim Creation from DPRR:**
```python
# BiographicSFA creates facet claims
for office in person_data["offices"]:
    claim_cipher = calculate_facet_claim_cipher(
        subject_node_id=person_data["wikidata_qid"],  # Q1048
        property_path_id="HELD_OFFICE",
        object_node_id=office_qid_map[office["office"]],  # Q20056508 (consul)
        facet_id="biographic",
        temporal_scope=str(office["year"]),
        source_document_id="Q47461",  # Broughton
        passage_locator=office["source"]
    )
    # Result: "fclaim_bio_abc123..."
```

### B. Broughton's *Magistrates of the Roman Republic* (MRR)

**Canonical Reference:** T. Robert S. Broughton, *The Magistrates of the Roman Republic* (1951-1986)

**MRR provides:**
- Year-by-year listing of all magistrates (509-31 BCE)
- Source citations for each attestation
- Uncertainty markers (?, probably, possibly)
- Prosopographic notes (family, career sequences)

**Integration:**
```python
# BiographicSFA indexes Broughton entries
broughton_index = {
    "-59": {
        "consuls": ["C. Iulius Caesar", "M. Calpurnius Bibulus"],
        "praetors": [...],
        "aediles": [...],
        "source": "MRR II.188"
    },
    # ... for all years 509-31 BCE
}

# Cross-reference with Wikidata
for year, magistrates in broughton_index.items():
    for consul in magistrates["consuls"]:
        qid = resolve_name_to_qid(consul)  # Q1048
        create_biographic_claim(qid, "HELD_OFFICE", year, source="Broughton")
```

### C. Prosopographic Constraints and Validation

**Career Sequencing Rules:**
```python
# BiographicSFA enforces cursus honorum constraints
cursus_honorum_rules = {
    "quaestor": {"minimum_age": 30, "prerequisite": None},
    "aedile": {"minimum_age": 36, "prerequisite": "quaestor"},
    "praetor": {"minimum_age": 39, "prerequisite": "quaestor"},
    "consul": {"minimum_age": 42, "prerequisite": "praetor"},
    "censor": {"minimum_age": None, "prerequisite": "consul"}
}

# Validation query
def validate_career_claim(person_qid, office, year):
    """Check if office claim violates cursus honorum"""
    birth_year = get_birth_year(person_qid)
    age_at_office = year - birth_year
    
    rule = cursus_honorum_rules[office]
    if rule["minimum_age"] and age_at_office < rule["minimum_age"]:
        return False, f"Too young: {age_at_office} < {rule['minimum_age']}"
    
    if rule["prerequisite"]:
        prior_offices = get_prior_offices(person_qid, year)
        if rule["prerequisite"] not in prior_offices:
            return False, f"Missing prerequisite: {rule['prerequisite']}"
    
    return True, "Valid"
```

---

## 6. Cross-Facet Dependencies

### A. BiographicSFA as Producer

**Biographic facet OWNS:**
- Person nodes (Q5 instances)
- Career structure (office sequences)
- Status markers (senatorial, equestrian)
- Family relationships (gens, parentage, marriage)
- Life chronology (birth, death, major life events)

**Creates claims like:**
```cypher
(C_bio:FacetClaim {
  cipher: "fclaim_bio_abc123...",
  facet: "biographic",
  subject_node_id: "Q1048",  // Caesar
  property_path_id: "HELD_OFFICE",
  object_node_id: "Q20056508",  // Roman consul
  temporal_scope: "-0059",
  source_document_id: "Q47461"  // Broughton
})
```

### A1. BiographicSFA as Event Producer (Event Proposals)

**🔥 CRITICAL ROLE:** BiographicSFA proposes biographical events that **seed multi-facet analysis**.

**Event Types Owned by BiographicSFA:**

1. **Birth Events** (temporal anchor for all person activities)
   ```cypher
   (C_bio_birth:FacetClaim {
     cipher: "fclaim_bio_birth_001...",
     facet: "biographic",
     subject_node_id: "Q1048",
     property_path_id: "BORN",
     object_value: "-0100-07-12",  // Date as value
     temporal_scope: "-0100-07-12",
     spatial_scope: "Q220",  // Rome
     source_document_id: "Q1385",  // Suetonius
     passage_locator: "Jul. 88"
   })
   ```

2. **Death Events** (terminal boundary for person)
   ```cypher
   (C_bio_death:FacetClaim {
     cipher: "fclaim_bio_death_001...",
     facet: "biographic",
     subject_node_id: "Q1048",
     property_path_id: "DIED",
     object_value: "-0044-03-15",
     temporal_scope: "-0044-03-15",
     spatial_scope: "Q220",  // Rome
     source_document_id: "Q1043",  // Plutarch
     passage_locator: "Caes. 66"
   })
   ```

3. **Marriage Events** (alliance formation)
   ```cypher
   (C_bio_marriage:FacetClaim {
     cipher: "fclaim_bio_marriage_001...",
     facet: "biographic",
     subject_node_id: "Q1048",  // Caesar
     property_path_id: "MARRIED",
     object_node_id: "Q230677",  // Cornelia Cinna
     temporal_scope: "-0084",  // Marriage year
     end_temporal_scope: "-0069",  // Her death
     source_document_id: "Q1385"
   })
   ```

4. **Office Appointment Events** (career milestones)
   ```cypher
   (C_bio_office:FacetClaim {
     cipher: "fclaim_bio_office_001...",
     facet: "biographic",
     subject_node_id: "Q1048",
     property_path_id: "APPOINTED_TO",
     object_node_id: "Q20056508",  // Roman consul
     temporal_scope: "-0059-01-01",  // Office start
     end_temporal_scope: "-0059-12-31",  // Office end
     source_document_id: "Q47461",  // Broughton MRR
     passage_locator: "II.188"
   })
   ```

5. **Adoption Events** (legal identity change)
   ```cypher
   (C_bio_adoption:FacetClaim {
     cipher: "fclaim_bio_adoption_001...",
     facet: "biographic",
     subject_node_id: "Q1405",  // Octavian
     property_path_id: "ADOPTED_BY",
     object_node_id: "Q1048",  // Caesar
     temporal_scope: "-0044-03-15",  // In Caesar's will
     source_document_id: "Q1385",
     assertion: "Octavian adopted posthumously via Caesar's will, became C. Julius Caesar Octavianus"
   })
   ```

**Event Proposal Workflow:**

```python
# Step 1: BiographicSFA creates event proposal
bio_event = {
    "event_type": "office_appointment",
    "person": "Q1048",  # Caesar
    "office": "Q20056508",  # Consul
    "start_date": "-0059-01-01",
    "end_date": "-0059-12-31",
    "source": "Q47461"  # Broughton
}

# Step 2: BiographicSFA creates FacetClaim
bio_claim = create_facet_claim(
    facet="biographic",
    subject="Q1048",
    property="APPOINTED_TO",
    object="Q20056508",
    temporal_scope="-0059-01-01",
    source="Q47461"
)

# Step 3: SCA evaluates if event warrants multi-facet analysis
sca_evaluation = sca.evaluate_event_relevance(bio_event)
# Returns: {"political": 0.98, "military": 0.85, "religious": 0.60}

# Step 4: SCA queues to Political & Military SFAs
sca.queue_for_perspective("political", bio_event)
sca.queue_for_perspective("military", bio_event)

# Step 5: Other facets create THEIR OWN claims referencing the event
# PoliticalSFA:
pol_claim = create_facet_claim(
    facet="political",
    subject="Q1048",
    property="HELD_SUPREME_AUTHORITY",
    object="Q17167",  # Roman Republic
    temporal_scope="-0059",
    source="Q7825",  # Cicero's letters
    context_claims=[bio_claim.cipher]  # References bio event
)

# MilitarySFA:
mil_claim = create_facet_claim(
    facet="military",
    subject="Q1048",
    property="ELIGIBLE_FOR_COMMAND",
    object="Q17167",
    temporal_scope="-0059",
    source="Q47461",
    context_claims=[bio_claim.cipher]  # References bio event
)
```

**Key Pattern: BiographicSFA proposes, others analyze**

- ✅ BiographicSFA: "Caesar appointed consul 59 BCE" (factual event)
- ✅ PoliticalSFA: "Caesar held supreme authority 59 BCE" (political analysis)
- ✅ MilitarySFA: "Caesar eligible for army command 59 BCE" (military implication)
- ❌ MilitarySFA does NOT create "Caesar appointed consul" claim (that's BiographicSFA's domain)

**Temporal Constraint Enforcement:**

BiographicSFA's events serve as **boundary conditions** for other facets:

```cypher
// Example: Check if military claim violates birth constraint
MATCH (mil_claim:FacetClaim {
  facet: "military",
  subject_node_id: "Q1048",
  property_path_id: "COMMANDED_AT"
})
MATCH (bio_birth:FacetClaim {
  facet: "biographic",
  subject_node_id: "Q1048",
  property_path_id: "BORN"
})
WHERE mil_claim.temporal_scope < bio_birth.temporal_scope
RETURN "❌ VIOLATION: Military claim predates birth" AS error

// Example: Check if office claim violates minimum age requirement
MATCH (office_claim:FacetClaim {
  facet: "biographic",
  property_path_id: "APPOINTED_TO",
  object_node_id: "Q20056508"  // Consul (minimum age 43)
})
MATCH (birth:FacetClaim {
  facet: "biographic",
  subject_node_id: office_claim.subject_node_id,
  property_path_id: "BORN"
})
WITH office_claim, birth, 
     (toInteger(substring(office_claim.temporal_scope, 1, 4)) - 
      toInteger(substring(birth.temporal_scope, 1, 4))) AS age
WHERE age < 43
RETURN "⚠️ WARNING: Consul appointed under minimum age (cursus honorum violation)" AS warning
```

### B. Other Facets as Consumers

**Military facet REFERENCES persons created by Biographic:**
```cypher
// MilitarySFA creates military claim
(C_mil:FacetClaim {
  cipher: "fclaim_mil_def456...",
  facet: "military",
  subject_node_id: "Q1048",  // References Caesar (owned by BiographicSFA)
  property_path_id: "COMMANDED_AT",
  object_node_id: "Q181314",  // Battle of Alesia
  temporal_scope: "-0052"
})

// Constraint checking via BiographicSFA
MATCH (bio:FacetClaim {
  facet: "biographic",
  subject_node_id: "Q1048",
  property_path_id: "HELD_OFFICE",
  object_node_id: "Q23438"  // Proconsul of Gaul
})
WHERE bio.temporal_scope <= "-0052" <= bio.end_temporal_scope
RETURN "✅ Caesar was proconsul of Gaul in 52 BCE (eligible for command)"
```

**Political facet REFERENCES offices defined by Biographic:**
```cypher
// PoliticalSFA analyzes authority relationships
(C_pol:FacetClaim {
  cipher: "fclaim_pol_ghi789...",
  facet: "political",
  subject_node_id: "Q1048",
  property_path_id: "HELD_AUTHORITY_OVER",
  object_node_id: "Q17167",  // Roman Republic
  temporal_scope: "-0059"
})

// References biographic claim about consulship
-[:CONTEXTUALIZED_BY]-> (C_bio:FacetClaim {facet: "biographic"})
```

### C. SCA Coordination

**SCA evaluates biographic claims for relevance:**
```python
# SCA receives biographic claim
bio_claim = {
    "subject": "Q1048",
    "property": "HELD_OFFICE",
    "object": "Q20056508",  // Consul
    "facet": "biographic"
}

# SCA evaluates: Does this warrant multi-facet analysis?
relevance_scores = sca.evaluate_relevance(bio_claim)
# {
#     "political": 0.95,  // Consulship is highly political
#     "military": 0.75,   // Consul could command armies
#     "religious": 0.40,  // Consul performed religious duties
#     "economic": 0.30    // Below threshold
# }

# SCA queues for Political and Military SFAs only
if relevance_scores["political"] > 0.70:
    queue_for_perspective("political", bio_claim)
if relevance_scores["military"] > 0.70:
    queue_for_perspective("military", bio_claim)
```

---

## 7. Training Phase Workflow

### Phase 1: Build Person Ontology (Abstract Concepts)

**Week 1: Person Categories**
```python
concepts = [
    "Q5",          # human
    "Q82955",      # politician
    "Q47064",      # military personnel
    "Q83307",      # magistrate
    "Q332711",     # Roman senator
]
# Creates abstract SubjectConcept nodes
```

**Week 2: Office Hierarchy**
```python
concepts = [
    "Q20056508",   # Roman consul
    "Q40779",      # praetor
    "Q174174",     # quaestor
    "Q193621",     # aedile
    "Q83307",      # magistrate (superclass)
]
# Creates office taxonomy
```

**Week 3: Status and Class**
```python
concepts = [
    "Q2912932",    # senatorial order
    "Q3302272",    # equestrian order
    "Q1115580",    # patrician
    "Q864186",     # plebeian
]
# Creates social structure
```

**Week 4: Family Structures**
```python
concepts = [
    "Q177251",     # gens (Roman clan)
    "Q188646",     # gens Julia
    "Q188437",     # gens Pompeia
    "Q459337",     # gens Cornelia
]
# Creates kinship ontology
```

### Phase 2: Populate Concrete Persons (Operational)

**Triggered by:** SCA provides subject_concept (Roman Republic)

```python
# BiographicSFA operational mode
def analyze_roman_republic_persons():
    # Query DPRR for all known individuals
    dprr_persons = dprr_client.get_all_persons(
        start_year=-509,
        end_year=-27
    )
    
    for person in dprr_persons:
        # Create person node (if not exists)
        person_qid = resolve_dprr_to_wikidata(person["dprr_id"])
        
        # Create biographic claims for each office
        for office in person["offices"]:
            create_facet_claim(
                subject=person_qid,
                property="HELD_OFFICE",
                object=office["office_qid"],
                facet="biographic",
                temporal=office["year"],
                source="Broughton"
            )
        
        # Create family claims
        if person["father"]:
            create_facet_claim(
                subject=person_qid,
                property="CHILD_OF",
                object=resolve_dprr_to_wikidata(person["father"]),
                facet="biographic"
            )
```

---

## 8. Quality Metrics

### A. Coverage Metrics

**Target for Roman Republic:**
- ~10,000 persons identified (DPRR baseline)
- ~2,000 with detailed prosopographic data
- ~500 with complete career sequences
- ~100 major figures with full family networks

**Validation:**
```cypher
// Count persons with biographic claims
MATCH (p:Human)-[:SUBJECT_OF]->(c:FacetClaim {facet: "biographic"})
RETURN count(DISTINCT p) AS persons_with_biographic_data

// Count complete careers (3+ offices)
MATCH (p:Human)-[:SUBJECT_OF]->(c:FacetClaim {
  facet: "biographic",
  property_path_id: "HELD_OFFICE"
})
WITH p, count(c) AS office_count
WHERE office_count >= 3
RETURN count(p) AS persons_with_careers
```

### B. Accuracy Metrics

**Source Attribution:**
```cypher
// All biographic claims must cite sources
MATCH (c:FacetClaim {facet: "biographic"})
WHERE c.source_document_id IS NULL
RETURN count(c) AS claims_without_sources  // Should be 0
```

**Temporal Coherence:**
```cypher
// No office held before birth or after death
MATCH (p:Human)-[:SUBJECT_OF]->(birth:FacetClaim {property_path_id: "BORN"})
MATCH (p)-[:SUBJECT_OF]->(office:FacetClaim {property_path_id: "HELD_OFFICE"})
WHERE office.temporal_scope < birth.temporal_scope
RETURN count(office) AS temporal_violations  // Should be 0
```

### C. Network Metrics

**Family Connectivity:**
```cypher
// Gens networks: How many persons per gens?
MATCH (g:Gens)<-[:MEMBER_OF_GENS]-(p:Human)
RETURN g.label, count(p) AS members
ORDER BY members DESC
LIMIT 20
```

**Career Completeness:**
```cypher
// Cursus honorum sequences: How many follow expected pattern?
MATCH (p:Human)-[:SUBJECT_OF]->(c:FacetClaim {property_path_id: "HELD_OFFICE"})
WITH p, collect(c.object_node_id) AS offices
WHERE "quaestor" IN offices 
  AND "praetor" IN offices 
  AND "consul" IN offices
RETURN count(p) AS complete_cursus_honorum
```

---

## 9. Implementation Checklist

### Phase 1: Setup (Week 1)
- [ ] Add BiographicFacet to facet_registry_master.csv ✅
- [ ] Create BiographicSubjectFacetAgent class
- [ ] Implement DPRR API client
- [ ] Index Broughton's Magistrates data
- [ ] Define cursus honorum validation rules
- [ ] **Define canonical relationship type taxonomy** 🔥 NEW
  * Document all relationship types (CHILD_OF, MARRIED, ADOPTED_BY, etc.)
  * Map to Wikidata properties where applicable
  * Define directionality rules (parent-child vs child-parent)
  * Add relationship qualifiers (biological, adoptive, step-, etc.)

### Phase 2: Training (Weeks 2-4)
- [ ] Query Wikidata for person categories (Q5, magistrate, etc.)
- [ ] Query Wikidata for office hierarchy (consul, praetor, etc.)
- [ ] Query Wikidata for social structure (senatorial order, etc.)
- [ ] Query Wikidata for family structures (gens, kinship)
- [ ] Create abstract SubjectConcept nodes for all categories
- [ ] **Query Wikidata for biographical events** 🔥 NEW
  * Birth events (P569 date of birth)
  * Death events (P570 date of death)
  * Marriage events (P26 with start time)
  * Office appointments (P39 with start time)
  * Adoption events (inferred from name changes)

### Phase 3: Operational (Weeks 5+)
- [ ] Integrate DPRR person data (10,000 individuals)
- [ ] Create FacetClaim nodes for all office attestations
- [ ] Create FacetClaim nodes for family relationships
- [ ] **Construct family trees (stemma) for major figures** 🔥 NEW
  * Build multi-generational gens structures
  * Track marriage alliances between gentes
  * Identify adoption patterns (critical for inheritance)
  * Validate relationship consistency (no circular parentage)
- [ ] **Propose biographical event claims** 🔥 NEW
  * Birth/death events → seed temporal constraints
  * Office appointments → seed political/military analysis
  * Marriage events → seed social/political alliance analysis
  * Adoption events → seed inheritance/succession analysis
- [ ] Validate temporal coherence (birth/death constraints)
- [ ] Cross-reference with Military/Political SFAs

### Phase 4: Quality Assurance
- [ ] Verify source citations (all claims have sources)
- [ ] Check career sequences (cursus honorum validation)
- [ ] Validate family networks (gens membership)
- [ ] **Validate canonical relationship types** 🔥 NEW
  * Ensure only canonical types used (no ad-hoc relationships)
  * Check directionality (CHILD_OF vs PARENT_OF consistency)
  * Verify adoption properly marked (not confused with biological)
  * Test family tree queries (stemma construction works)
- [ ] **Test event proposal workflow** 🔥 NEW
  * Verify BiographicSFA creates event claims
  * Verify other facets reference (not recreate) biographic events
  * Test temporal constraint enforcement (no claims before birth)
  * Test age requirement validation (cursus honorum minimums)
- [ ] Test constraint enforcement (age requirements)
- [ ] Generate coverage report (persons, offices, families)
- [ ] **Generate family tree coverage report** 🔥 NEW
  * % of major figures with complete stemma
  * % of gens with multi-generational trees
  * % of marriages with alliance claims
  * % of adoptions properly tracked

---

## 10. Example: Complete Biographic Profile

**Subject:** Julius Caesar (Q1048)

**Biographic Claims Created:**

```cypher
// Identity
(Caesar:Human {qid: "Q1048", dprr_id: "DPRR_1"})

// Birth
(C_bio_1:FacetClaim {
  cipher: "fclaim_bio_001...",
  facet: "biographic",
  subject_node_id: "Q1048",
  property_path_id: "BORN",
  temporal_scope: "-0100-07-12",
  source_document_id: "Q1385",  // Suetonius
  assertion: "Caesar born July 12, 100 BCE"
})

// Family
(C_bio_2:FacetClaim {
  cipher: "fclaim_bio_002...",
  facet: "biographic",
  subject_node_id: "Q1048",
  property_path_id: "MEMBER_OF_GENS",
  object_node_id: "Q188646",  // gens Julia
  source_document_id: "Q47461"
})

// Family Tree Construction (Stemma)
// -- Father relationship
(C_bio_2a:FacetClaim {
  cipher: "fclaim_bio_002a...",
  facet: "biographic",
  subject_node_id: "Q1048",  // Caesar
  property_path_id: "CHILD_OF",  // Canonical relationship type
  object_node_id: "Q????",  // C. Julius Caesar (father, praetor 92 BCE)
  temporal_scope: "-0100",  // From birth
  source_document_id: "Q47461",
  assertion: "Caesar son of C. Julius Caesar, praetor 92 BCE"
})

// -- Mother relationship
(C_bio_2b:FacetClaim {
  cipher: "fclaim_bio_002b...",
  facet: "biographic",
  subject_node_id: "Q1048",  // Caesar
  property_path_id: "CHILD_OF",
  object_node_id: "Q????",  // Aurelia (mother)
  temporal_scope: "-0100",
  source_document_id: "Q1385",  // Suetonius
  assertion: "Caesar son of Aurelia"
})

// -- First marriage (political alliance)
(C_bio_2c:FacetClaim {
  cipher: "fclaim_bio_002c...",
  facet: "biographic",
  subject_node_id: "Q1048",  // Caesar
  property_path_id: "MARRIED",
  object_node_id: "Q230677",  // Cornelia Cinna
  temporal_scope: "-0084",  // Marriage year
  end_temporal_scope: "-0069",  // Her death
  source_document_id: "Q1385",
  assertion: "Caesar married Cornelia, daughter of L. Cornelius Cinna (consul 87-84)"
})
  -[:CREATES_ALLIANCE]-> (C_bio_2c_alliance:FacetClaim {
    facet: "biographic",
    subject_node_id: "Q188646",  // gens Julia
    property_path_id: "ALLIED_TO",
    object_node_id: "Q????",  // gens Cornelia
    temporal_scope: "-0084",
    assertion: "Marriage alliance between gens Julia and gens Cornelia (Cinna's faction)"
  })

// -- Daughter (from Cornelia)
(C_bio_2d:FacetClaim {
  cipher: "fclaim_bio_002d...",
  facet: "biographic",
  subject_node_id: "Q????",  // Julia (Caesar's daughter)
  property_path_id: "CHILD_OF",
  object_node_id: "Q1048",  // Caesar (father)
  temporal_scope: "-0076",
  source_document_id: "Q1385"
})
(C_bio_2d2:FacetClaim {
  cipher: "fclaim_bio_002d2...",
  facet: "biographic",
  subject_node_id: "Q????",  // Julia
  property_path_id: "CHILD_OF",
  object_node_id: "Q230677",  // Cornelia (mother)
  temporal_scope: "-0076"
})

// -- Grandchild (Julia's marriage to Pompey - critical political alliance)
(C_bio_2e:FacetClaim {
  cipher: "fclaim_bio_002e...",
  facet: "biographic",
  subject_node_id: "Q????",  // Julia
  property_path_id: "MARRIED",
  object_node_id: "Q82675",  // Pompey the Great
  temporal_scope: "-0059",  // First Triumvirate alliance
  end_temporal_scope: "-0054",  // Her death
  source_document_id: "Q1043",  // Plutarch
  assertion: "Julia married Pompey 59 BCE (First Triumvirate alliance)"
})
  -[:SEALS_ALLIANCE]-> (C_bio_2e_triumvirate:FacetClaim {
    facet: "biographic",
    subject_node_id: "Q1048",  // Caesar
    property_path_id: "POLITICAL_ALLY_OF",
    object_node_id: "Q82675",  // Pompey
    temporal_scope: "-0059",
    end_temporal_scope: "-0054",  // Until Julia's death
    assertion: "Caesar-Pompey alliance sealed by marriage (Julia to Pompey)"
  })

// -- Adoption (posthumous, legally creates parent-child bond)
(C_bio_2f:FacetClaim {
  cipher: "fclaim_bio_002f...",
  facet: "biographic",
  subject_node_id: "Q1405",  // Octavian (later Augustus)
  property_path_id: "ADOPTED_BY",  // Canonical relationship type
  object_node_id: "Q1048",  // Caesar
  temporal_scope: "-0044-03-15",  // In Caesar's will
  source_document_id: "Q1385",
  assertion: "Octavian adopted posthumously via Caesar's will, became C. Julius Caesar Octavianus"
})
  -[:CREATES_LEGAL_BOND]-> (C_bio_2f_parent:FacetClaim {
    facet: "biographic",
    subject_node_id: "Q1405",  // Octavian
    property_path_id: "CHILD_OF",  // Legal parent (not biological)
    object_node_id: "Q1048",  // Caesar
    temporal_scope: "-0044-03-15",
    relationship_type: "adoptive",  // Qualifier
    assertion: "Octavian legally Caesar's son via adoption"
  })

// -- Gens membership (clan structure)
(C_bio_2g:FacetClaim {
  cipher: "fclaim_bio_002g...",
  facet: "biographic",
  subject_node_id: "Q1405",  // Octavian
  property_path_id: "MEMBER_OF_GENS",
  object_node_id: "Q188646",  // gens Julia (via adoption)
  temporal_scope: "-0044-03-15",
  source_document_id: "Q1385",
  assertion: "Octavian became member of gens Julia via adoption"
})

// Family Tree Visualization (Cypher)
// Caesar's immediate family network
MATCH path = (Caesar:Human {qid: "Q1048"})
  -[:CHILD_OF|MARRIED|ADOPTED_BY*1..3]- (relative:Human)
RETURN path

// Multi-generational gens Julia tree
MATCH (gens:Gens {qid: "Q188646"})
MATCH (member:Human)-[:MEMBER_OF_GENS]->(gens)
OPTIONAL MATCH (member)-[r:CHILD_OF|MARRIED|ADOPTED_BY]-(relative:Human)
RETURN member, r, relative

// Offices (career sequence)
(C_bio_3:FacetClaim {
  cipher: "fclaim_bio_003...",
  facet: "biographic",
  subject_node_id: "Q1048",
  property_path_id: "HELD_OFFICE",
  object_node_id: "Q174174",  // quaestor
  temporal_scope: "-0069",
  source_document_id: "Q47461",
  passage_locator: "MRR II.132"
})

(C_bio_4:FacetClaim {
  cipher: "fclaim_bio_004...",
  facet: "biographic",
  subject_node_id: "Q1048",
  property_path_id: "HELD_OFFICE",
  object_node_id: "Q20056508",  // consul
  temporal_scope: "-0059",
  source_document_id: "Q47461",
  passage_locator: "MRR II.188"
})

// Status
(C_bio_5:FacetClaim {
  cipher: "fclaim_bio_005...",
  facet: "biographic",
  subject_node_id: "Q1048",
  property_path_id: "MEMBER_OF_ORDER",
  object_node_id: "Q2912932",  // senatorial order
  temporal_scope: "-0069",  // From quaestorship
  source_document_id: "Q47461"
})

// Death
(C_bio_6:FacetClaim {
  cipher: "fclaim_bio_006...",
  facet: "biographic",
  subject_node_id: "Q1048",
  property_path_id: "DIED",
  temporal_scope: "-0044-03-15",
  source_document_id: "Q1385",
  assertion: "Caesar assassinated March 15, 44 BCE"
})
```

**Other Facets Reference These Claims:**

```cypher
// Military SFA references Caesar (person owned by BiographicSFA)
(C_mil:FacetClaim {
  cipher: "fclaim_mil_007...",
  facet: "military",
  subject_node_id: "Q1048",  // References Caesar
  property_path_id: "COMMANDED_AT",
  object_node_id: "Q181314",  // Battle of Alesia
  temporal_scope: "-0052"
})
  -[:CONSTRAINED_BY]-> (C_bio_3)  // Eligible due to quaestorship

// Political SFA references Caesar's authority
(C_pol:FacetClaim {
  cipher: "fclaim_pol_008...",
  facet: "political",
  subject_node_id: "Q1048",
  property_path_id: "HELD_AUTHORITY_OVER",
  object_node_id: "Q17167",  // Roman Republic
  temporal_scope: "-0059"
})
  -[:CONTEXTUALIZED_BY]-> (C_bio_4)  // Authority via consulship
```

---

## 11. References

### Primary Databases
- [Digital Prosopography of the Roman Republic (DPRR)](https://romanrepublic.ac.uk)
- [Broughton's Magistrates of the Roman Republic (MRR)](https://archive.org/details/broughton-magistrates-roman-republic)
- [Wikidata Prosopography](https://www.wikidata.org/wiki/Q783287)

### Scholarly Methods
- [Introduction to Prosopography (DARIAH)](https://campus.dariah.eu/resources/hosted/an-introduction-to-prosopography)
- [Prosopography of ancient Rome (Wikipedia)](https://en.wikipedia.org/wiki/Prosopography_of_ancient_Rome)
- [Roman Prosopography (Academia.edu)](https://www.academia.edu/Documents/in/Roman_Prosopography)

### Technical References
- [CLAIM_ID_ARCHITECTURE.md](../Key%20Files/CLAIM_ID_ARCHITECTURE.md) - Nanopublication-aligned claim ciphers
- [SCA_SFA_ROLES_DISCUSSION.md](../md/Agents/SCA/SCA_SFA_ROLES_DISCUSSION.md) - Agent coordination patterns
- [MILITARY_SFA_ONTOLOGY_METHODOLOGY.md](MILITARY_SFA_ONTOLOGY_METHODOLOGY.md) - Parallel methodology

---

**Document Status:** ✅ Complete Implementation Guide  
**Last Updated:** February 16, 2026  
**Next Review:** After Phase 1 implementation (Week 4)
