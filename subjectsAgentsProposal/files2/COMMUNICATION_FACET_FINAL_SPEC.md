# Communication Facet - Final Implementation Specification

## Design Decisions (Approved)

### ✅ **Decision 1: Communication vs. Literary Boundary**
**Rule: Function/Persuasion = Communication**

If the primary analytical interest is the **functional/persuasive** aspect → Communication facet
If the primary analytical interest is **form/aesthetics** → Literary facet

**Hybrid assignments are allowed when both interests are significant:**
```python
# Cicero's De Oratore (rhetorical treatise)
{
    'primary': ['Communication'],      # Teaching persuasion techniques
    'secondary': ['Literary'],          # Literary dialogue form
    'confidence': 0.90
}

# Virgil's Aeneid
{
    'primary': ['Literary'],            # Epic poetry, aesthetic masterpiece
    'secondary': ['Communication'],     # Augustan propaganda
    'confidence': 0.95
}

# Caesar's Commentarii
{
    'primary': ['Communication'],       # Propaganda purpose dominates
    'secondary': ['Military', 'Literary'],
    'confidence': 0.95
}
```

**Decision tree for assignment:**
```
Is the primary reason someone studies this text/artifact:
  ├─ To understand persuasive strategies? → Communication (primary)
  ├─ To appreciate artistic form/style? → Literary (primary)
  └─ Both equally? → Both as primary (rare)
```

### ✅ **Decision 2: Meta-facet Architecture**
**Communication is a META-FACET that applies across all other facets**

**Implementation:** Communication is NOT a peer facet competing with Military, Political, etc. Instead, it's a **cross-cutting dimension** that describes HOW information within any domain is transmitted.

**Data Model:**
```python
subject_concept = {
    # Primary domain facets (1-16)
    'domain_facets': ['Military', 'Political'],
    
    # Communication meta-layer (applies to domains)
    'communication': {
        'active': True,  # Does this subject have communicative dimension?
        'medium': ['written', 'oral'],
        'purpose': ['propaganda', 'legitimation'],
        'audience': ['Senate', 'Roman people'],
        'strategy': ['objectivity pose', 'exemplarity'],
        'primacy': 0.85  # How central is communication to this subject? (0-1)
    }
}
```

**Routing Logic:**
```python
# If communication primacy >= 0.75, route to CommunicationAgent
if subject.communication.primacy >= 0.75:
    agents.append('CommunicationAgent')
    
# CommunicationAgent works WITH domain agents
# Example: Punic Wars
domain_agents = ['MilitaryAgent', 'PoliticalAgent']  # Primary domain
communication_agent = ['CommunicationAgent']  # Meta-layer analysis

# CommunicationAgent analyzes HOW military/political info was communicated
```

**Neo4j Schema:**
```cypher
CREATE (s:SubjectConcept {
  subject_id: "fast:fst01754978",
  
  // Domain facets (original 16)
  domain_facets: ["Military", "Political", "Diplomatic"],
  
  // Communication meta-layer
  has_communication_dimension: true,
  communication_primacy: 0.85,  // How central is communication?
  communication_medium: ["written", "visual"],
  communication_purpose: ["propaganda", "legitimation"],
  communication_audience: ["Senate", "Roman people"],
  communication_strategy: ["objectivity pose", "exemplarity"],
  
  // Standard properties
  label: "Punic Wars",
  lcc: "DG247"
})
```

### ✅ **Decision 3: Effectiveness Tracking**
**NO - Too subjective**

Do NOT track whether communication "worked" (e.g., "Did Cicero's speech persuade the Senate?")

**Rationale:**
- Too interpretive/subjective
- Ancient evidence often insufficient
- Creates false precision

**Alternative:** Note effectiveness claims as regular Claims (subject to review/validation)

```cypher
// WRONG - Don't do this:
CREATE (speech:CommunicationEvent {
  effectiveness: "high",  // ❌ Too subjective
  persuaded: true         // ❌ Unprovable
})

// RIGHT - Do this instead:
CREATE (claim:Claim {
  text: "Cicero's First Catilinarian successfully isolated Catiline politically",
  evidence: ["Catiline fled Rome", "Senate passed emergency decree"],
  confidence: 0.75,
  facets: ["Communication", "Political"],
  fallacy_flags: []  // Let validation process assess this
})
```

### ✅ **Decision 4: Failed/Suppressed Communication**
**Note in claims, not separate tracking**

Handle censored/failed/suppressed communication through regular Claim mechanism:

```cypher
// Suppressed monument example
CREATE (claim:Claim {
  text: "After Sejanus's fall, his monuments were destroyed through damnatio memoriae",
  facets: ["Communication", "Political"],
  communication_outcome: "suppressed",  // Descriptive note
  evidence: ["Tacitus Annals", "Archaeological absence"],
  confidence: 0.90
})

// Failed persuasion example
CREATE (claim:Claim {
  text: "Cato's speech against the Lex Gabinia failed to prevent its passage",
  facets: ["Communication", "Political"],
  communication_outcome: "unsuccessful",  // Descriptive note
  evidence: ["Plutarch, Pompey 25", "Law passed despite opposition"],
  confidence: 0.85
})
```

**No special properties needed** - outcome is just descriptive context in the claim text.

### ✅ **Decision 5: 4-Dimensional Model Approved**

**Medium, Purpose, Audience, Strategy** framework is approved for implementation.

---

## Revised Facet Architecture

### **16 Domain Facets** (Original)
1. Military
2. Political  
3. Social
4. Diplomatic
5. Economic
6. Legal
7. Religious
8. Cultural
9. Demographic
10. Technological
11. Architectural
12. Literary
13. Philosophical
14. Scientific
15. Geographic
16. Temporal

### **Communication Meta-Facet** (New)
**Not a 17th peer facet, but a cross-cutting dimension**

Communication describes HOW information within domain facets is transmitted, for what purpose, to whom, and using what strategies.

---

## Implementation Details

### **1. Agent Assignment Logic**

```python
class AgentAssignmentService:
    """
    Assigns agents based on domain facets + communication dimension
    """
    
    def assign_agents(self, subject: dict) -> dict:
        """
        1. Assign domain agents (Military, Political, etc.)
        2. Check communication primacy
        3. Add CommunicationAgent if primacy >= threshold
        """
        
        # Step 1: Domain facet assignment (existing logic)
        domain_assignment = self._assign_domain_facets(subject)
        # Returns: {'domain_facets': ['Military', 'Political'], 'confidence': 0.85}
        
        # Step 2: Detect communication dimension
        comm_dimension = self._detect_communication_dimension(subject)
        # Returns: {
        #   'has_communication': True,
        #   'primacy': 0.85,
        #   'medium': ['written'],
        #   'purpose': ['propaganda'],
        #   'audience': ['Senate'],
        #   'strategy': ['exemplarity']
        # }
        
        # Step 3: Determine if CommunicationAgent needed
        agents = []
        
        # Add domain agents
        for facet in domain_assignment['domain_facets']:
            agents.append(f"{facet}Agent")
        
        # Add CommunicationAgent if communication is central
        if comm_dimension['primacy'] >= 0.75:
            agents.append('CommunicationAgent')
        
        return {
            'agents': agents,
            'domain_facets': domain_assignment['domain_facets'],
            'communication': comm_dimension,
            'confidence': domain_assignment['confidence']
        }
    
    def _detect_communication_dimension(self, subject: dict) -> dict:
        """
        Detect if subject has significant communication dimension
        
        Returns:
            {
                'has_communication': bool,
                'primacy': float (0-1),  # How central is communication?
                'medium': list,
                'purpose': list,
                'audience': list,
                'strategy': list
            }
        """
        
        primacy_score = 0.0
        
        # Signal 1: LCC-based detection
        if subject.get('lcc'):
            lcc_comm_score = self._lcc_communication_score(subject['lcc'])
            primacy_score += lcc_comm_score * 0.40  # 40% weight
        
        # Signal 2: Keyword detection
        keyword_score = self._keyword_communication_score(subject['label'])
        primacy_score += keyword_score * 0.30  # 30% weight
        
        # Signal 3: FAST facet
        if subject.get('fast_facet'):
            fast_score = self._fast_communication_score(subject)
            primacy_score += fast_score * 0.30  # 30% weight
        
        # Normalize primacy to 0-1
        primacy = min(primacy_score, 1.0)
        
        # Extract dimensions if communication is present
        if primacy >= 0.5:
            medium = self._detect_medium(subject)
            purpose = self._detect_purpose(subject)
            audience = self._infer_audience(subject)
            strategy = self._detect_strategy(subject)
            
            return {
                'has_communication': True,
                'primacy': primacy,
                'medium': medium,
                'purpose': purpose,
                'audience': audience,
                'strategy': strategy
            }
        else:
            return {
                'has_communication': False,
                'primacy': primacy,
                'medium': [],
                'purpose': [],
                'audience': [],
                'strategy': []
            }
    
    def _lcc_communication_score(self, lcc: str) -> float:
        """
        Score communication primacy based on LCC
        
        Returns: 0.0-1.0 score
        """
        
        # Direct communication LCC ranges
        DIRECT_COMMUNICATION_LCC = {
            'PN4001-PN4355': 1.0,   # Oratory - pure communication
            'PN4400-PN4500': 1.0,   # Journalism - pure communication
            'PA6087-PA6099': 1.0,   # Latin rhetoric - pure communication
            'HM1206-HM1211': 0.95,  # Social influence - communication-heavy
            'JF1525.P8': 0.95,      # Public opinion - communication-heavy
            'JF2112': 0.95,         # Political campaigns - communication-heavy
        }
        
        # Check exact matches
        for lcc_range, score in DIRECT_COMMUNICATION_LCC.items():
            if self._in_lcc_range(lcc, lcc_range):
                return score
        
        # Domain ranges with communication aspects
        COMMUNICATION_DIMENSION_LCC = {
            'DG341-DG345': 0.70,  # Intellectual life - has communication dimension
            'DG346-DG350': 0.60,  # Religion - ritual communication
            'DG351-DG355': 0.65,  # Art - visual messaging
            'PA8001-PA8595': 0.50, # Latin literature - has communication purpose
        }
        
        for lcc_range, score in COMMUNICATION_DIMENSION_LCC.items():
            if self._in_lcc_range(lcc, lcc_range):
                return score
        
        return 0.0  # No communication dimension detected
    
    def _keyword_communication_score(self, label: str) -> float:
        """
        Score communication primacy based on keywords
        """
        
        label_lower = label.lower()
        score = 0.0
        
        # Direct communication terms (very high primacy)
        DIRECT_TERMS = [
            'rhetoric', 'oratory', 'propaganda', 'persuasion',
            'speech', 'oration', 'discourse', 'communication'
        ]
        
        for term in DIRECT_TERMS:
            if term in label_lower:
                return 1.0  # Immediate high score
        
        # Medium indicators
        MEDIUM_TERMS = ['oral', 'written', 'visual', 'inscription', 
                       'letter', 'edict', 'proclamation', 'coin', 'monument']
        
        # Purpose indicators  
        PURPOSE_TERMS = ['propaganda', 'incite', 'persuade', 'legitimize',
                        'justify', 'denounce', 'praise', 'promote', 'condemn']
        
        has_medium = any(term in label_lower for term in MEDIUM_TERMS)
        has_purpose = any(term in label_lower for term in PURPOSE_TERMS)
        
        # Medium + Purpose pattern suggests communication
        if has_medium and has_purpose:
            score = 0.80
        elif has_medium:
            score = 0.40
        elif has_purpose:
            score = 0.50
        
        return score
    
    def _detect_medium(self, subject: dict) -> list:
        """
        Detect communication medium from subject
        """
        media = []
        label_lower = subject['label'].lower()
        
        MEDIUM_PATTERNS = {
            'oral': ['speech', 'oration', 'oratory', 'oral', 'spoken', 'rumor', 'fama'],
            'written': ['letter', 'edict', 'inscription', 'text', 'written', 'commentari'],
            'visual': ['coin', 'monument', 'statue', 'relief', 'image', 'visual', 'triumph'],
            'performative': ['ritual', 'ceremony', 'spectacle', 'theater', 'game', 'performance'],
            'architectural': ['building', 'temple', 'forum', 'arch', 'column', 'structure']
        }
        
        for medium, keywords in MEDIUM_PATTERNS.items():
            if any(kw in label_lower for kw in keywords):
                media.append(medium)
        
        # Fallback: infer from LCC
        if not media and subject.get('lcc'):
            lcc = subject['lcc']
            if lcc.startswith('PN4'):  # Oratory
                media.append('oral')
            elif lcc.startswith('PA'):  # Literature
                media.append('written')
            elif lcc.startswith('CJ'):  # Numismatics
                media.append('visual')
            elif lcc.startswith('NA'):  # Architecture
                media.append('architectural')
        
        return media if media else ['unknown']
    
    def _detect_purpose(self, subject: dict) -> list:
        """
        Detect communication purpose
        """
        purposes = []
        label_lower = subject['label'].lower()
        
        PURPOSE_KEYWORDS = {
            'propaganda': ['propaganda', 'promote', 'glorify', 'celebrate'],
            'persuasion': ['persuade', 'convince', 'argue', 'debate'],
            'incitement': ['incite', 'provoke', 'rouse', 'mobilize'],
            'legitimation': ['legitimize', 'justify', 'authorize', 'validate'],
            'information': ['inform', 'report', 'announce', 'communicate'],
            'memory': ['commemorate', 'memorialize', 'remember', 'preserve'],
            'ideology': ['ideology', 'belief', 'doctrine', 'worldview']
        }
        
        for purpose, keywords in PURPOSE_KEYWORDS.items():
            if any(kw in label_lower for kw in keywords):
                purposes.append(purpose)
        
        return purposes if purposes else ['unknown']
    
    def _infer_audience(self, subject: dict) -> list:
        """
        Infer intended audience
        """
        audiences = []
        label_lower = subject['label'].lower()
        
        AUDIENCE_INDICATORS = {
            'Senate': ['senate', 'senatorial', 'senator'],
            'Roman people': ['people', 'popular', 'public', 'citizen', 'contio'],
            'Military': ['army', 'legion', 'soldier', 'troop', 'veteran'],
            'Posterity': ['monument', 'inscription', 'commemorate', 'memory']
        }
        
        for audience, keywords in AUDIENCE_INDICATORS.items():
            if any(kw in label_lower for kw in keywords):
                audiences.append(audience)
        
        # Default inference from domain facets
        if not audiences and subject.get('domain_facets'):
            facets = subject['domain_facets']
            if 'Political' in facets:
                audiences.append('Senate')
                audiences.append('Roman people')
            if 'Military' in facets:
                audiences.append('Military')
        
        return audiences if audiences else ['general public']
    
    def _detect_strategy(self, subject: dict) -> list:
        """
        Detect rhetorical/communicative strategy
        """
        strategies = []
        label_lower = subject['label'].lower()
        
        STRATEGY_KEYWORDS = {
            'ethos': ['authority', 'credibility', 'character', 'reputation'],
            'pathos': ['emotion', 'fear', 'pity', 'anger', 'grief'],
            'logos': ['argument', 'logic', 'reason', 'evidence', 'proof'],
            'invective': ['attack', 'denounce', 'condemn', 'abuse', 'mock'],
            'exemplarity': ['example', 'precedent', 'ancestor', 'model'],
            'spectacle': ['display', 'show', 'spectacle', 'triumph', 'ceremony']
        }
        
        for strategy, keywords in STRATEGY_KEYWORDS.items():
            if any(kw in label_lower for kw in keywords):
                strategies.append(strategy)
        
        return strategies if strategies else []
```

### **2. Neo4j Schema**

```cypher
// ============================================================
// UPDATED SUBJECTCONCEPT NODE STRUCTURE
// ============================================================

CREATE CONSTRAINT subject_concept_id_unique IF NOT EXISTS
FOR (s:SubjectConcept) REQUIRE s.subject_id IS UNIQUE;

// Communication meta-layer indexes
CREATE INDEX subject_communication_primacy IF NOT EXISTS
FOR (s:SubjectConcept) ON (s.communication_primacy);

CREATE INDEX subject_communication_medium IF NOT EXISTS
FOR (s:SubjectConcept) ON (s.communication_medium);

CREATE INDEX subject_communication_purpose IF NOT EXISTS
FOR (s:SubjectConcept) ON (s.communication_purpose);

// ============================================================
// EXAMPLE SUBJECTCONCEPT NODE
// ============================================================

CREATE (s:SubjectConcept {
  // Identity
  subject_id: "fast:fst01754978",
  label: "Punic Wars",
  
  // Authority IDs
  fast_id: "fst01754978",
  lcsh_id: "sh85109214",
  lcc: "DG247",
  qid: "Q47043",
  tier: 2,
  
  // DOMAIN FACETS (original 16)
  domain_facets: ["Military", "Political", "Diplomatic"],
  domain_confidence: 0.85,
  lcc_range: "DG247",
  lcc_range_label: "Punic Wars",
  
  // COMMUNICATION META-LAYER
  has_communication_dimension: true,
  communication_primacy: 0.85,  // How central is communication? (0-1)
  communication_medium: ["written", "visual", "oral"],
  communication_purpose: ["propaganda", "legitimation", "memory"],
  communication_audience: ["Senate", "Roman people", "posterity"],
  communication_strategy: ["exemplarity", "spectacle"],
  
  // Metadata
  created_at: datetime(),
  mapping_method: "lcc_range_specific"
})

// ============================================================
// CLAIM WITH COMMUNICATION DIMENSION
// ============================================================

CREATE (claim:Claim {
  claim_id: "claim_12345",
  cipher: "abc123xyz",
  text: "Caesar's Gallic War commentaries served as propaganda to legitimize his conquests",
  
  // Domain facets
  domain_facets: ["Communication", "Military", "Political"],
  
  // Communication dimension (detailed)
  communication_analysis: {
    medium: "written",
    purpose: ["propaganda", "legitimation"],
    audience: ["Senate", "Roman people"],
    strategy: ["objectivity pose", "exemplarity", "third-person narrative"],
    primacy: 0.90  // Communication is central to this claim
  },
  
  // Standard claim properties
  confidence: 0.85,
  fallacy_flags: [],
  evidence: ["Commentarii de Bello Gallico text", "Plutarch Caesar"],
  status: "validated"
})

// ============================================================
// RELATIONSHIP: COMMUNICATED_VIA
// ============================================================

// Connect entities to communication events
CREATE (caesar:Human {name: "Julius Caesar"})-[:COMMUNICATED_VIA {
  medium: "written",
  work: "Commentarii de Bello Gallico",
  purpose: ["propaganda", "legitimation"],
  audience: ["Senate", "Roman people"],
  date_start: -58,
  date_end: -50
}]->(gallic_wars:Event {name: "Gallic Wars"})
```

### **3. CommunicationAgent Implementation**

```python
class CommunicationAgent:
    """
    Meta-facet agent that analyzes communication dimensions
    Works alongside domain agents (Military, Political, etc.)
    """
    
    def __init__(self):
        self.agent_id = "communication_agent"
        self.facet = "Communication (meta)"
    
    def analyze_subject(self, subject: dict) -> dict:
        """
        Analyze communication dimension of a subject
        
        Works with domain facets to understand HOW information
        within those domains is transmitted
        
        Args:
            subject: SubjectConcept with domain_facets already assigned
        
        Returns:
            Communication dimension analysis
        """
        
        # Check if communication is relevant
        if subject.get('communication_primacy', 0) < 0.5:
            return None  # Communication not central to this subject
        
        # Analyze 4 dimensions
        analysis = {
            'medium': self._analyze_medium(subject),
            'purpose': self._analyze_purpose(subject),
            'audience': self._analyze_audience(subject),
            'strategy': self._analyze_strategy(subject)
        }
        
        # Generate communication-specific insights
        insights = self._generate_insights(subject, analysis)
        
        return {
            'agent_id': self.agent_id,
            'facet': 'Communication',
            'dimensions': analysis,
            'insights': insights,
            'confidence': self._calculate_confidence(analysis)
        }
    
    def _analyze_medium(self, subject: dict) -> dict:
        """
        Deep analysis of communication medium
        """
        
        media = subject.get('communication_medium', [])
        
        # Medium-specific characteristics
        medium_analysis = {}
        
        for medium in media:
            if medium == 'written':
                medium_analysis['written'] = {
                    'characteristics': ['permanence', 'editability', 'portability'],
                    'limitations': ['literacy required', 'slower dissemination'],
                    'roman_forms': ['letters', 'edicts', 'commentarii', 'inscriptions']
                }
            elif medium == 'oral':
                medium_analysis['oral'] = {
                    'characteristics': ['immediacy', 'emotional impact', 'ephemeral'],
                    'limitations': ['no permanence', 'limited reach'],
                    'roman_forms': ['contiones', 'senate speeches', 'rumors']
                }
            elif medium == 'visual':
                medium_analysis['visual'] = {
                    'characteristics': ['wide reach', 'crosses literacy barriers', 'monumental'],
                    'limitations': ['static', 'interpretation varies'],
                    'roman_forms': ['coins', 'monuments', 'triumphs', 'statues']
                }
        
        return medium_analysis
    
    def _analyze_purpose(self, subject: dict) -> dict:
        """
        Deep analysis of communication purpose
        """
        
        purposes = subject.get('communication_purpose', [])
        
        purpose_analysis = {}
        
        for purpose in purposes:
            if purpose == 'propaganda':
                purpose_analysis['propaganda'] = {
                    'definition': 'Shape public opinion to legitimize power',
                    'techniques': ['selective facts', 'emotional appeals', 'repetition'],
                    'effectiveness_factors': ['message clarity', 'audience receptivity', 'media choice']
                }
            elif purpose == 'legitimation':
                purpose_analysis['legitimation'] = {
                    'definition': 'Justify authority or actions',
                    'techniques': ['precedent', 'divine sanction', 'popular mandate'],
                    'effectiveness_factors': ['credibility', 'social context', 'timing']
                }
            # ... other purposes
        
        return purpose_analysis
    
    def _generate_insights(self, subject: dict, analysis: dict) -> list:
        """
        Generate communication-specific insights
        
        Example insights:
        - "Written medium suggests intent for permanence and posterity"
        - "Multiple audiences indicate broad propaganda campaign"
        - "Use of spectacle suggests appeal to emotions over reason"
        """
        
        insights = []
        
        # Medium insights
        if 'written' in analysis['medium'] and 'oral' in analysis['medium']:
            insights.append(
                "Multi-medium approach (written + oral) suggests comprehensive "
                "communication strategy targeting both elite and popular audiences"
            )
        
        # Purpose insights
        purposes = subject.get('communication_purpose', [])
        if 'propaganda' in purposes and 'legitimation' in purposes:
            insights.append(
                "Combination of propaganda and legitimation suggests defensive posture - "
                "justifying contested actions to multiple stakeholders"
            )
        
        # Audience insights
        audiences = subject.get('communication_audience', [])
        if 'Senate' in audiences and 'Roman people' in audiences:
            insights.append(
                "Dual audience (Senate + people) indicates need to balance elite "
                "and popular opinion - characteristic of Late Republican politics"
            )
        
        return insights
```

---

## Migration Guide

### **From v1.0 (17 peer facets) to v1.1 (16 + meta)**

**Old Structure (v1.0):**
```python
{
    'facets': ['Communication', 'Military', 'Political'],  # Communication as peer
    'confidence': 0.85
}
```

**New Structure (v1.1):**
```python
{
    'domain_facets': ['Military', 'Political'],  # Original 16
    'communication': {  # Meta-layer
        'primacy': 0.85,
        'medium': ['written'],
        'purpose': ['propaganda'],
        'audience': ['Senate'],
        'strategy': ['exemplarity']
    },
    'confidence': 0.85
}
```

### **Database Migration Cypher**

```cypher
// Migrate existing SubjectConcept nodes from v1.0 to v1.1
MATCH (s:SubjectConcept)
WHERE 'Communication' IN s.facets  // Old structure

// Extract Communication from facets list
WITH s, 
     [f IN s.facets WHERE f <> 'Communication'] AS domain_facets,
     CASE WHEN 'Communication' IN s.facets THEN true ELSE false END AS has_comm

// Update to new structure
SET s.domain_facets = domain_facets,
    s.has_communication_dimension = has_comm,
    s.communication_primacy = CASE WHEN has_comm THEN 0.80 ELSE 0.0 END,
    s.schema_version = '1.1'

// Remove old facets property
REMOVE s.facets

RETURN count(s) AS migrated_nodes
```

---

## Testing Plan

### **Test Case 1: Pure Communication Subject**
```python
subject = {
    'label': 'Ciceronian rhetoric',
    'lcc': 'PA6087',  # Latin rhetoric
    'fast_facet': 'topical'
}

expected = {
    'domain_facets': ['Literary'],  # Rhetoric is also literary art
    'communication': {
        'primacy': 1.0,  # Pure communication
        'medium': ['oral', 'written'],
        'purpose': ['persuasion'],
        'audience': ['Senate', 'law courts'],
        'strategy': ['ethos', 'pathos', 'logos']
    }
}
```

### **Test Case 2: Domain Subject with Communication Dimension**
```python
subject = {
    'label': 'Punic Wars',
    'lcc': 'DG247',
    'fast_facet': 'topical'
}

expected = {
    'domain_facets': ['Military', 'Political', 'Diplomatic'],
    'communication': {
        'primacy': 0.60,  # Moderate - wars were subject of much communication
        'medium': ['written', 'visual', 'oral'],
        'purpose': ['propaganda', 'memory'],
        'audience': ['Roman people', 'posterity'],
        'strategy': ['spectacle', 'exemplarity']
    }
}
```

### **Test Case 3: Domain Subject without Communication Dimension**
```python
subject = {
    'label': 'Roman architecture',
    'lcc': 'NA310',
    'fast_facet': 'topical'
}

expected = {
    'domain_facets': ['Architectural', 'Technological'],
    'communication': {
        'primacy': 0.30,  # Low - architecture has messaging but not primary
        'medium': ['architectural'],
        'purpose': [],
        'audience': [],
        'strategy': []
    }
}
# CommunicationAgent NOT assigned (primacy < 0.5)
```

---

## Summary of Changes

### ✅ **Decisions Implemented:**

1. **Communication/Literary boundary:** Function/persuasion → Communication
2. **Meta-facet architecture:** Communication is cross-cutting, not peer facet
3. **No effectiveness tracking:** Too subjective
4. **Failed communication:** Note in claims, not separate tracking
5. **4-dimensional model:** Approved (Medium, Purpose, Audience, Strategy)

### 📊 **Final Architecture:**

- **16 Domain Facets** (Military through Temporal)
- **1 Meta-Facet** (Communication)
- **Communication Primacy Score** (0-1) determines agent assignment
- **4 Dimensions** captured for all communication-relevant subjects

### 🎯 **Key Benefits:**

1. **No competing facets:** Communication doesn't compete with Military, Political, etc.
2. **Flexible application:** Communication can apply to any domain
3. **Clear primacy metric:** Objective score (0-1) determines when CommunicationAgent activates
4. **Rich analysis:** 4 dimensions capture full communicative context
5. **Roman Republic optimized:** Designed for rhetoric-heavy political culture

---

## Next Implementation Steps

1. ✅ Update JSON mapping (completed)
2. ⬜ Update Python mapper with meta-facet logic
3. ⬜ Implement CommunicationAgent class
4. ⬜ Update Neo4j schema with communication properties
5. ⬜ Migrate existing v1.0 nodes to v1.1 structure
6. ⬜ Test on 100 Roman Republic subjects
7. ⬜ Document edge cases and examples

**Ready to proceed with implementation?**
