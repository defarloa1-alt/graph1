# Communication SFA Ontology Building Methodology

**Document Status:** Implementation Guide  
**Date:** February 16, 2026  
**Context:** Training Phase - Independent Domain Ontology Building  
**Related:** [SCA_SFA_ROLES_DISCUSSION.md](../md/Agents/SCA/SCA_SFA_ROLES_DISCUSSION.md) - Training Phase  
**Cross-Reference:** [BIOGRAPHIC_SFA_ONTOLOGY_METHODOLOGY.md](BIOGRAPHIC_SFA_ONTOLOGY_METHODOLOGY.md), [MILITARY_SFA_ONTOLOGY_METHODOLOGY.md](MILITARY_SFA_ONTOLOGY_METHODOLOGY.md)

---

## Overview

This document defines the **filtering methodology** for the Communication Specialist Facet Agent (SFA) to extract a clean communication and rhetoric ontology from Wikidata during the **Training Phase** (independent domain study).

**Goal:** Build a semantically coherent communication ontology grounded in rhetoric, media studies, and information theory as academic disciplines, focusing on **HOW** information is transmitted, not just **WHAT** is said.

**Scope:** Generic communication theory → Roman Republic specialization (oratory, rhetoric, propaganda)

**Key Insight:** Communication facet is a **meta-facet** - it analyzes the **transmission layer** of other facets' content (political speeches, military signals, religious rituals, etc.).

---

## 1. Anchor: Communication as Discipline

### Disciplinary Root

**Start Node:** `communication (Q11024)`  
**Rationale:** Treat communication as the scholarly discipline root - the systematic study of information transmission, encoding, channels, and reception.

**Wikidata:** https://www.wikidata.org/wiki/Q11024  
**Wikipedia:** https://en.wikipedia.org/wiki/Communication

### Secondary Anchors

| Anchor QID | Label | Purpose |
|------------|-------|---------|
| **Q81009** | rhetoric | Persuasive communication, classical oratory |
| **Q8134** | oratory | Public speaking, speeches |
| **Q11633** | writing | Written communication, literacy |
| **Q1156402** | propaganda | Strategic information dissemination |
| **Q11028** | information | Information theory, content vs. medium |
| **Q34049** | mass media | Broadcasting, public communication |

### Key Properties from Discipline Root

| Property | Purpose | Example Targets |
|----------|---------|-----------------|
| **P527** (has part) | Communication components | encoding, channel, decoding, feedback |
| **P279** (subclass of) | Communication types | verbal, non-verbal, written, oral |
| **P921** (main subject) | Topic of communication | politics, religion, military |
| **P407** (language of work) | Linguistic medium | Latin, Greek |
| **P136** (genre) | Communication format | oration, epistle, edict, inscription |
| **P50** (author) | Communicator | Cicero, Caesar |
| **P585** (point in time) | When communication occurred | specific dates |

**Navigation Pattern:**
```
Q11024 (communication)
  ├─[P527]→ Q11028 (information)
  │   └─[encoding]→ language, symbols, rhetoric
  ├─[P527]→ Q34049 (mass media)
  │   └─[channels]→ oral, written, monumental
  ├─[P279]→ Q81009 (rhetoric)
  │   ├─[techniques]→ ethos, pathos, logos
  │   └─[genres]→ deliberative, forensic, epideictic
  └─[P279]→ Q8134 (oratory)
      └─[contexts]→ Senate, contio (public assembly), law courts
```

---

## 2. Inclusion Criteria for Ontology Nodes

A Wikidata item should be **included** in the communication ontology if it satisfies **most** of:

### A. Communication Media and Channels

**Criteria:**
- Defines how information is transmitted:
  * **Oral:** speeches, public announcements, heralds, town criers
  * **Written:** inscriptions, letters, law tablets, graffiti
  * **Visual:** monuments, coins, triumphal arches
  * **Performative:** theater, rituals, spectacles
  * **Military signals:** standards, trumpets, smoke signals

**Example:**
```cypher
// Good: Communication medium
(Q170238:Medium {label: "public speech"})
  -[:P279]-> (Q8134:oratory)
  -[:P361]-> (Q11024:communication)

// Good: Roman-specific medium
(Q2029919:Medium {label: "Roman inscription"})
  -[:P279]-> (Q47071:epigraphy)
  -[:context]-> (Q17167:Roman_Republic)
```

### B. Rhetorical Theory and Technique

**Criteria:**
- Concepts from classical rhetoric:
  * **Persuasion strategies:** ethos (credibility), pathos (emotion), logos (logic)
  * **Rhetorical genres:** deliberative (policy), forensic (legal), epideictic (praise/blame)
  * **Figures of speech:** metaphor, synecdoche, anaphora, chiasmus
  * **Organization:** exordium, narratio, argumentatio, peroratio
  * **Style levels:** grand, middle, plain

**Test:** Does this concept appear in Aristotle's *Rhetoric*, Cicero's *De Oratore*, or Quintilian's *Institutio Oratoria*?

**Example:**
```cypher
// Rhetorical technique
(Q81009_pathos:RhetoricalDevice {label: "pathos"})
  -[:P279]-> (Q81009:rhetoric)
  -[:definition]-> "Appeal to emotion"
  -[:P361]-> (Q classical_rhetoric)

// Rhetorical structure
(Q123456:SpeechPart {label: "exordium"})
  -[:P361]-> (Q oration_structure)
  -[:purpose]-> "Introduction to establish credibility"
```

### C. Information Flow and Audience

**Criteria:**
- Analyzes the **transmission dynamic**, not just content:
  * **Sender:** who communicates (orator, writer, herald)
  * **Message:** what is transmitted (policy, news, propaganda)
  * **Medium:** how it's transmitted (speech, inscription, coin)
  * **Channel:** where transmission occurs (Senate, Forum, law court)
  * **Receiver:** who receives (senators, plebs, soldiers)
  * **Feedback:** response mechanisms (voting, applause, riots)

**Example:**
```cypher
// Communication context
(Q41614:Context {label: "Roman Senate session"})
  -[:sender_type]-> (Q332711:senator)
  -[:medium]-> (Q8134:oratory)
  -[:receiver_type]-> (Q332711:senators)
  -[:feedback_mechanism]-> (Q1096752:voting)

// Public communication
(Q2048319:Context {label: "contio (public assembly)"})
  -[:sender_type]-> (Q82955:politician)
  -[:medium]-> (Q8134:public_speech)
  -[:receiver_type]-> (Q17167_people:Roman_citizens)
  -[:feedback_mechanism]-> (Q123456:applause_or_jeers)
```

### D. Literacy, Language, and Translation

**Criteria:**
- Concepts related to linguistic encoding:
  * **Literacy rates:** who could read/write
  * **Language registers:** formal Latin, colloquial, Greek
  * **Translation:** Greek texts → Latin adaptations
  * **Bilingualism:** Latin-Greek code-switching among elites
  * **Writing systems:** Roman cursive, monumental capitals

**Example:**
```cypher
// Linguistic analysis
(Q397:Language {label: "Latin"})
  -[:P5831]-> (Q vernacular_latin)  // has dialect
  -[:registers]-> ["formal", "colloquial", "legal", "literary"]
  -[:literacy_context]-> "Elite males primary literate class"

// Translation practice
(Q809:Translation {label: "Greek-Latin translation"})
  -[:P31]-> (Q linguisic_practice)
  -[:context]-> "Roman elite education required Greek"
```

### E. Propaganda and Strategic Communication

**Criteria:**
- Intentional shaping of public perception:
  * **Political messaging:** slogans, epithets, nicknames
  * **Visual propaganda:** triumphal monuments, coin imagery
  * **Narrative control:** selective history, enemy demonization
  * **Legitimation strategies:** divine favor, ancestral authority
  * **Rumor and gossip:** informal information networks

**Example:**
```cypher
// Propaganda technique
(Q1156402:Propaganda {label: "Roman triumph propaganda"})
  -[:P279]-> (Q strategic_communication)
  -[:medium]-> ["triumphal procession", "monument", "coins"]
  -[:purpose]-> "Legitimize military conquest"
  -[:audience]-> (Q17167_people:Roman_population)

// Messaging strategy
(Q epithet:Messaging {label: "cognomen propaganda"})
  -[:example]-> "Africanus (Scipio's victory title)"
  -[:function]-> "Associate individual with achievement"
```

---

## 3. Exclusion Criteria (Noise Filtering)

A Wikidata item should be **excluded** if it matches:

### A. Content vs. Medium Confusion

**Exclude:** The **what** of communication (that's other facets' domain)  
**Include:** The **how** of communication (that's Communication facet's domain)

**Examples:**
```cypher
// ❌ Exclude: Political content (belongs to Political facet)
(Q7188:Policy {label: "lex agraria"})
// This is WHAT was communicated, not HOW

// ✅ Include: Communication about the policy
(Q speech:Speech {label: "Tiberius Gracchus's speech on land reform"})
  -[:medium]-> (Q8134:oratory)
  -[:audience]-> (Q2048319:contio)
  -[:rhetorical_strategy]-> (Q pathos:appeal_to_poor)
// This is HOW the policy was communicated
```

### B. Modern Communication Technology

**Exclude:**
- Printing press (post-ancient)
- Radio, television, internet (anachronistic)
- Modern advertising (post-ancient concepts)
- Social media (anachronistic)

**Test:** Did this communication technology or concept exist in antiquity? If no → exclude.

### C. Non-Communicative Language Phenomena

**Exclude:**
- Linguistic evolution (historical linguistics)
- Phonology, morphology (unless tied to rhetoric)
- Etymology (unless tied to propaganda/messaging)

**Communication facet focuses on:** Language **in use** (pragmatics, rhetoric, persuasion), not language structure.

### D. Cross-Domain Content Duplication

**Communication facet does NOT:**
- Create claims about **WHAT** military orders were given (Military facet)
- Create claims about **WHAT** political decisions were made (Political facet)
- Create claims about **WHAT** religious beliefs were held (Religious facet)

**Communication facet DOES:**
- Create claims about **HOW** military orders were transmitted (signals, heralds)
- Create claims about **HOW** political decisions were communicated (Senate speeches)
- Create claims about **HOW** religious beliefs were propagated (rituals, inscriptions)

---

## 4. Wikidata Query Patterns for Training

### A. Rhetoric and Oratory Discovery

```sparql
# Find classical rhetorical concepts
SELECT DISTINCT ?concept ?conceptLabel ?type ?typeLabel WHERE {
  # Rhetorical concepts
  {
    ?concept wdt:P31/wdt:P279* wd:Q81009 .  # instance/subclass of rhetoric
  } UNION {
    ?concept wdt:P361 wd:Q81009 .  # part of rhetoric
  } UNION {
    ?concept wdt:P31 wd:Q1002697 .  # instance of rhetorical device
  }
  
  # Type classification
  OPTIONAL { ?concept wdt:P31 ?type }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,la" }
}
LIMIT 1000
```

### B. Ancient Speeches and Orations

```sparql
# Find speeches from Roman Republic
SELECT ?speech ?speechLabel ?author ?authorLabel ?date WHERE {
  # Speech/oration entities
  ?speech wdt:P31/wdt:P279* wd:Q861911 .  # instance of speech/oration
  
  # Ancient Roman context
  {
    ?speech wdt:P50 ?author .  # has author
    ?author wdt:P27 wd:Q17167 .  # author from Roman Republic
  } UNION {
    ?speech wdt:P921 ?subject .  # main subject
    ?subject wdt:P361 wd:Q17167 .  # subject related to Roman Republic
  }
  
  # Temporal constraint
  OPTIONAL { ?speech wdt:P577 ?date }
  FILTER(!BOUND(?date) || YEAR(?date) < -26)
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,la" }
}
LIMIT 500
```

### C. Communication Media Discovery

```sparql
# Find ancient communication media
SELECT ?medium ?mediumLabel ?type ?typeLabel WHERE {
  # Communication media/channels
  ?medium wdt:P31/wdt:P279* wd:Q340169 .  # media/communication channel
  
  # Filter for ancient media (exclude modern)
  FILTER NOT EXISTS {
    ?medium wdt:P31/wdt:P279* wd:Q11030 .  # not newspaper
    ?medium wdt:P31/wdt:P279* wd:Q1110794 .  # not television
    ?medium wdt:P31/wdt:P279* wd:Q1692 .  # not internet
  }
  
  OPTIONAL { ?medium wdt:P31 ?type }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
LIMIT 500
```

---

## 5. Roman Republic Specialization

### A. Cicero as Canonical Source

**Primary corpus:** Cicero's speeches (58 surviving orations)

**Cicero's works provide:**
- Exemplars of all rhetorical genres:
  * **Forensic (legal):** *Pro Milone*, *Pro Caelio*, *In Verrem*
  * **Deliberative (political):** *In Catilinam*, *Philippics*
  * **Epideictic (ceremonial):** *Pro Marcello*, *Pro Archia*
- Rhetorical theory: *De Oratore*, *Brutus*, *Orator*
- Real communication contexts (Senate, law courts, *contio*)

**Integration Pattern:**
```python
# CommunicationSFA analyzes Cicero's speeches
speech_data = cicero_corpus.get_speech("In_Catilinam_1")

# Returns:
{
    "title": "In Catilinam I",
    "author": "Cicero",
    "wikidata_qid": "Q1393664",
    "date": "-63-11-08",
    "context": "Senate deliberation",
    "rhetorical_analysis": {
        "genre": "deliberative",
        "primary_appeal": "pathos",
        "opening_strategy": "rhetorical_question",
        "structure": ["exordium", "narratio", "argumentatio", "peroratio"],
        "audience": "Roman Senate"
    },
    "communication_claim": {
        "medium": "oral speech",
        "channel": "Senate session",
        "purpose": "Persuade Senate to act against Catiline",
        "strategy": ["emotional appeal", "direct address", "fear-mongering"]
    }
}
```

**Claim Creation from Cicero:**
```python
# CommunicationSFA creates facet claim
claim_cipher = calculate_facet_claim_cipher(
    subject_node_id="Q1393664",  # In Catilinam I (speech)
    property_path_id="EMPLOYED_RHETORICAL_STRATEGY",
    object_node_id="Q???",  # pathos (emotional appeal)
    facet_id="communication",
    temporal_scope="-63-11-08",
    source_document_id="Q1393664",  # The speech itself
    passage_locator="Catil. 1.1-2"
)
# Result: "fclaim_com_abc123..."
```

### B. Quintilian's *Institutio Oratoria*

**Theoretical foundation:** Quintilian (35-100 CE) codifies Roman rhetorical education

**Quintilian provides:**
- Five canons of rhetoric: invention, arrangement, style, memory, delivery
- Training curriculum for orators
- Analysis of figures of speech
- Historical examples from Republican orators

**Integration:**
```python
# CommunicationSFA indexes rhetorical theory
quintilian_theory = {
    "five_canons": [
        "inventio",      # finding arguments
        "dispositio",    # organizing arguments
        "elocutio",      # style/expression
        "memoria",       # memorization
        "actio"          # delivery/performance
    ],
    "speech_parts": [
        "exordium",      # introduction
        "narratio",      # statement of facts
        "divisio",       # outline of argument
        "confirmatio",   # proof
        "refutatio",     # refutation
        "peroratio"      # conclusion
    ],
    "style_registers": [
        "grand",         # elevated, emotional
        "middle",        # moderate, pleasant
        "plain"          # simple, instructive
    ]
}

# Creates abstract SubjectConcept nodes
for canon in quintilian_theory["five_canons"]:
    create_subject_concept(
        label=canon,
        parent="rhetorical_education",
        source="Quintilian_Inst_Orat"
    )
```

### C. Communication Contexts in Roman Republic

**Primary contexts for communication analysis:**

1. **Senate Sessions (Deliberative Communication)**
   - Formal speeches to ~300-600 senators
   - Strict protocols (senatorial rank order)
   - Feedback: voting, consensus-building
   - Examples: Cicero's *In Catilinam*

2. **Contio (Public Assembly Communication)**
   - Popular speeches to Roman citizens
   - No voting (information-only)
   - Feedback: applause, jeers, riots
   - Examples: Tiberius Gracchus's land reform speeches

3. **Law Courts (Forensic Communication)**
   - Prosecution and defense speeches
   - Jury persuasion
   - Feedback: verdict
   - Examples: Cicero's *Pro Milone*

4. **Triumphal Propaganda (Visual Communication)**
   - Processions displaying captives and loot
   - Monuments commemorating victories
   - Coin imagery spreading messages
   - Examples: Pompey's triple triumph (61 BCE)

5. **Inscriptions (Written Public Communication)**
   - Laws on bronze tablets (Twelve Tables)
   - Funerary inscriptions (*elogia*)
   - Building dedications
   - Examples: *Res Gestae* (Augustus, but model predates him)

**Context Modeling:**
```cypher
// Communication context node
(senate_context:CommunicationContext {
  label: "Roman Senate deliberation",
  sender_type: "senator",
  receiver_type: "senators",
  medium: "oral_speech",
  channel: "Senate_house",
  feedback: "voting",
  formality: "high",
  language: "formal_Latin"
})

// Specific instance
(catiline_speech:Speech {
  qid: "Q1393664",
  author: "Q1541",  // Cicero
  date: "-63-11-08"
})
  -[:OCCURRED_IN_CONTEXT]-> (senate_context)
```

---

## 6. Cross-Facet Coordination

### A. Communication as Meta-Facet

**Communication facet analyzes the transmission of OTHER facets' content:**

**Political facet creates:** "Caesar crossed Rubicon to challenge Senate authority"  
**Communication facet analyzes:** "Caesar announced this via military signals to legions + public edict to cities"

**Religious facet creates:** "Augurs interpreted auspices before battle"  
**Communication facet analyzes:** "Augural interpretation communicated through ritual gestures + verbal formulas"

**Military facet creates:** "Legion XIII marched into Italy"  
**Communication facet analyzes:** "March signal given via cornicen (horn) + vexillum (standard)"

### B. Example: Multi-Facet Claim with Communication Overlay

**Scenario:** Tiberius Gracchus's land reform (133 BCE)

**Political SFA creates:**
```cypher
(C_pol:FacetClaim {
  cipher: "fclaim_pol_abc...",
  facet: "political",
  subject_node_id: "Q202003",  // Tiberius Gracchus
  property_path_id: "PROPOSED_LEGISLATION",
  object_node_id: "Q???",  // lex agraria
  assertion: "Gracchus proposed land redistribution law"
})
```

**Communication SFA creates (analyzes HOW it was proposed):**
```cypher
(C_com:FacetClaim {
  cipher: "fclaim_com_def...",
  facet: "communication",
  subject_node_id: "Q???",  // Gracchus's contio speech
  property_path_id: "EMPLOYED_RHETORICAL_STRATEGY",
  object_node_id: "Q???",  // pathos (appeal to poor)
  assertion: "Gracchus used emotional appeals to landless poor in public assembly"
})
  -[:ANALYZES_COMMUNICATION_OF]-> (C_pol)
```

**Social SFA creates:**
```cypher
(C_soc:FacetClaim {
  cipher: "fclaim_soc_ghi...",
  facet: "social",
  subject_node_id: "Q???",  // Land redistribution
  property_path_id: "AFFECTED_CLASS",
  object_node_id: "Q???",  // landless poor
  assertion: "Reform targeted dispossessed farmers"
})
```

**Communication SFA creates (analyzes audience reception):**
```cypher
(C_com2:FacetClaim {
  cipher: "fclaim_com_jkl...",
  facet: "communication",
  subject_node_id: "Q???",  // Public response
  property_path_id: "AUDIENCE_FEEDBACK",
  object_node_id: "Q???",  // popular support
  assertion: "Contio audience responded with strong approval (Plutarch)"
})
  -[:FEEDBACK_TO]-> (C_com)
```

### C. SCA Coordination with Communication Facet

**SCA recognizes communication claims are cross-cutting:**

```python
# SCA receives Political claim about Gracchus's law
pol_claim = {
    "subject": "Q202003",
    "property": "PROPOSED_LEGISLATION",
    "facet": "political"
}

# SCA evaluates: Does this involve significant communication?
communication_relevance = sca.evaluate_communication_aspect(pol_claim)
# {
#     "communication": 0.90,  // High: Public oratory was key to proposal
#     "social": 0.85,          // High: Class conflict involved
#     "economic": 0.75,        // High: Land economics
#     "legal": 0.70            // Medium: Legal reform
# }

# SCA queues for Communication SFA with special context
queue_for_perspective("communication", pol_claim, context={
    "analyze": "transmission_strategy",
    "focus": ["rhetoric", "audience", "medium"],
    "sources": ["Plutarch_Life_of_Tiberius_Gracchus", "Appian"]
})
```

---

## 7. Training Phase Workflow

### Phase 1: Build Communication Ontology (Abstract Concepts)

**Week 1: Rhetorical Theory**
```python
concepts = [
    "Q81009",      # rhetoric
    "Q8134",       # oratory
    "Q1002697",    # rhetorical device
    "Q861911",     # speech
]
# Creates abstract SubjectConcept nodes for genre, technique
```

**Week 2: Communication Media**
```python
concepts = [
    "Q11024",      # communication
    "Q11633",      # writing
    "Q47071",      # epigraphy (inscriptions)
    "Q41176",      # monument
]
# Creates media/channel taxonomy
```

**Week 3: Rhetorical Strategies**
```python
concepts = [
    "Q???",        # ethos (credibility)
    "Q???",        # pathos (emotion)
    "Q???",        # logos (logic)
    "Q1156402",    # propaganda
]
# Creates persuasion strategy concepts
```

**Week 4: Communication Contexts**
```python
concepts = [
    "Q???",        # Senate session
    "Q2048319",    # contio (public assembly)
    "Q???",        # law court
    "Q???",        # triumph
]
# Creates context/setting concepts
```

### Phase 2: Analyze Concrete Communications (Operational)

**Triggered by:** SCA provides claims from other facets with communication dimension

```python
# CommunicationSFA operational mode
def analyze_political_communication(claim):
    """Analyze HOW political content was communicated"""
    
    # Extract communication aspects
    if claim["property"] == "PROPOSED_LEGISLATION":
        # This was communicated somehow
        speech_ref = find_related_speeches(claim["subject"], claim["temporal"])
        
        if speech_ref:
            # Analyze rhetorical strategy
            create_facet_claim(
                subject=speech_ref["qid"],
                property="EMPLOYED_RHETORICAL_STRATEGY",
                object=determine_primary_appeal(speech_ref["text"]),
                facet="communication",
                source=speech_ref["source"]
            )
            
            # Analyze audience
            create_facet_claim(
                subject=speech_ref["qid"],
                property="ADDRESSED_AUDIENCE",
                object=determine_audience_type(speech_ref["context"]),
                facet="communication",
                source=speech_ref["source"]
            )
```

---

## 8. Quality Metrics

### A. Coverage Metrics

**Target for Roman Republic communication:**
- ~100 analyzed speeches (Ciceronian corpus primary)
- ~50 rhetorical concepts (from Aristotle, Cicero, Quintilian)
- ~20 communication contexts (Senate, contio, courts, etc.)
- ~500 communication claims analyzing other facets' content

**Validation:**
```cypher
// Count speeches with communication analysis
MATCH (speech:Speech)-[:SUBJECT_OF]->(c:FacetClaim {facet: "communication"})
WHERE speech.temporal_scope < "-26"  // Republican era
RETURN count(DISTINCT speech) AS analyzed_speeches

// Count cross-facet communication analyses
MATCH (c_com:FacetClaim {facet: "communication"})-[:ANALYZES_COMMUNICATION_OF]->(c_other:FacetClaim)
WHERE c_other.facet <> "communication"
RETURN c_other.facet, count(c_com) AS communication_analyses
```

### B. Cross-Facet Integration

**Communication claims should reference other facets:**
```cypher
// Ensure communication claims aren't isolated
MATCH (c:FacetClaim {facet: "communication"})
WHERE NOT (c)-[:ANALYZES_COMMUNICATION_OF|:FEEDBACK_TO|:CONTEXTUALIZED_BY]->()
RETURN count(c) AS isolated_communication_claims  // Should be low
```

### C. Rhetorical Accuracy

**Source Attribution for Rhetorical Strategies:**
```cypher
// Communication claims about rhetoric must cite ancient sources
MATCH (c:FacetClaim {facet: "communication"})
WHERE c.property_path_id = "EMPLOYED_RHETORICAL_STRATEGY"
  AND c.source_document_id IS NULL
RETURN count(c) AS unsourced_rhetorical_claims  // Should be 0
```

---

## 9. Implementation Checklist

### Phase 1: Setup (Week 1)
- [ ] Add CommunicationFacet to facet_registry_master.csv ✅
- [ ] Create CommunicationSubjectFacetAgent class
- [ ] Index Cicero's speeches (58 orations)
- [ ] Index Quintilian's rhetorical theory
- [ ] Define rhetorical strategy taxonomy

### Phase 2: Training (Weeks 2-4)
- [ ] Query Wikidata for rhetorical concepts (rhetoric, oratory, etc.)
- [ ] Query Wikidata for communication media (writing, speaking, monuments)
- [ ] Query Wikidata for speeches (Cicero, Caesar, etc.)
- [ ] Create abstract SubjectConcept nodes for all rhetorical genres
- [ ] Create context nodes (Senate, contio, law courts)

### Phase 3: Operational (Weeks 5+)
- [ ] Integrate with Political SFA (analyze political speeches)
- [ ] Integrate with Military SFA (analyze command signals)
- [ ] Integrate with Religious SFA (analyze ritual communication)
- [ ] Create FacetClaim nodes for all analyzed speeches
- [ ] Link communication claims to other facets' claims

### Phase 4: Quality Assurance
- [ ] Verify rhetorical analysis accuracy (cite Quintilian/Aristotle)
- [ ] Check cross-facet integration (communication analyzes others)
- [ ] Validate source citations (all claims cite ancient sources)
- [ ] Test meta-facet pattern (communication about content, not content itself)
- [ ] Generate coverage report (speeches, strategies, contexts)

---

## 10. Example: Complete Communication Analysis

**Subject:** Cicero's First Catiline Oration (Q1393664)

**Communication Claims Created:**

```cypher
// Speech entity
(speech:Speech {
  qid: "Q1393664",
  title: "In Catilinam I",
  author_qid: "Q1541",  // Cicero
  date: "-63-11-08"
})

// Rhetorical strategy
(C_com_1:FacetClaim {
  cipher: "fclaim_com_001...",
  facet: "communication",
  subject_node_id: "Q1393664",
  property_path_id: "EMPLOYED_RHETORICAL_STRATEGY",
  object_node_id: "Q???",  // pathos (emotional appeal)
  temporal_scope: "-63-11-08",
  source_document_id: "Q1393664",
  passage_locator: "Catil. 1.1-6",
  assertion: "Cicero employed emotional appeal (pathos) via repeated rhetorical questions"
})

// Rhetorical device
(C_com_2:FacetClaim {
  cipher: "fclaim_com_002...",
  facet: "communication",
  subject_node_id: "Q1393664",
  property_path_id: "EMPLOYED_RHETORICAL_DEVICE",
  object_node_id: "Q???",  // anaphora (repetition)
  source_document_id: "Q1393664",
  passage_locator: "Catil. 1.1",
  assertion: "Opening uses anaphora ('Quo usque tandem...')"
})

// Communication context
(C_com_3:FacetClaim {
  cipher: "fclaim_com_003...",
  facet: "communication",
  subject_node_id: "Q1393664",
  property_path_id: "DELIVERED_IN_CONTEXT",
  object_node_id: "Q???",  // Senate session
  temporal_scope: "-63-11-08",
  source_document_id: "Q1385",  // Sallust as secondary source
  assertion: "Speech delivered in Senate session with Catiline present"
})

// Audience analysis
(C_com_4:FacetClaim {
  cipher: "fclaim_com_004...",
  facet: "communication",
  subject_node_id: "Q1393664",
  property_path_id: "ADDRESSED_AUDIENCE",
  object_node_id: "Q332711",  // Roman senators
  source_document_id: "Q1393664",
  assertion: "Primary audience: Senate; secondary audience: Roman people (published later)"
})

// Strategic purpose
(C_com_5:FacetClaim {
  cipher: "fclaim_com_005...",
  facet: "communication",
  subject_node_id: "Q1393664",
  property_path_id: "COMMUNICATION_PURPOSE",
  object_node_id: "Q???",  // persuade to act
  source_document_id: "Q1393664",
  passage_locator: "Catil. 1.27-33",
  assertion: "Purpose: persuade Senate to declare Catiline public enemy"
})

// Analyzes Political claim
(C_com_1)-[:ANALYZES_COMMUNICATION_OF]->(C_pol:FacetClaim {
  facet: "political",
  assertion: "Cicero opposed Catiline conspiracy"
})
```

---

## 11. References

### Primary Sources
- [Cicero's Speeches (Loeb Classical Library)](https://www.loebclassics.com)
- [Quintilian, Institutio Oratoria](https://www.loebclassics.com)
- [Aristotle, Rhetoric](https://www.perseus.tufts.edu)

### Scholarly Methods
- [Classical Rhetoric (Wikipedia)](https://en.wikipedia.org/wiki/Rhetoric)
- [Roman Oratory (Oxford Classical Dictionary)](https://oxfordre.com)
- [Communication Studies (Wikidata)](https://www.wikidata.org/wiki/Q11024)

### Technical References
- [CLAIM_ID_ARCHITECTURE.md](../Key%20Files/CLAIM_ID_ARCHITECTURE.md) - Nanopublication-aligned claim ciphers
- [SCA_SFA_ROLES_DISCUSSION.md](../md/Agents/SCA/SCA_SFA_ROLES_DISCUSSION.md) - Meta-facet coordination patterns
- [BIOGRAPHIC_SFA_ONTOLOGY_METHODOLOGY.md](BIOGRAPHIC_SFA_ONTOLOGY_METHODOLOGY.md) - Person-centric methodology
- [MILITARY_SFA_ONTOLOGY_METHODOLOGY.md](MILITARY_SFA_ONTOLOGY_METHODOLOGY.md) - Parallel methodology

---

**Document Status:** ✅ Complete Implementation Guide  
**Facet Type:** Meta-Facet (analyzes communication of other facets' content)  
**Last Updated:** February 16, 2026  
**Next Review:** After Phase 1 implementation (Week 4)
