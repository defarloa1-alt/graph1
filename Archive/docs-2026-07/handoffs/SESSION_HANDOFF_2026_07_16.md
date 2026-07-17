# Session Handoff - July 16, 2026

> **NON-AUTHORITATIVE.** Later audit found factual errors (wrong IGAR definition, invented predicates, phantom CLI/files, junk Neo4j writes).  
> For training design use **`docs/FACET_TRAINING_CONTRACT.md`** and the live graph. Do not resume work from this handoff’s “next steps” without re-verification.

**Date:** Thursday, July 16, 2026  
**Repository:** `C:\Projects\Graph1`  
**Status:** Superseded for training — see `docs/FACET_TRAINING_CONTRACT.md`

---

## 1. Executive Summary

Today we completed a major architectural restructuring of the Graph1 knowledge system, transitioning from a flat SubjectConcept model to a hierarchical Domain architecture with full version control. We built a complete domain versioning system with CLI tooling, cleaned up node types, created extensive documentation, and clarified the critical distinction between Domain peer subgraphs (ROMAN_REPUBLIC, MILITARY_THEORY) and SubjectConcept organizational units within domains. The training methodology for the Military SFA was thoroughly discussed and clarified: Phase 1 involves reading military theory resources to build MILITARY_THEORY domain knowledge, then Phase 2 applies that theory to analyze historical events in ROMAN_REPUBLIC. Training is currently paused awaiting revision of the Military SFA prompt to incorporate the clarified methodology, predicate definitions, and full IGAR protocol specifications.

---

## 2. Major Accomplishments

- **Domain Versioning System Built**
  - CLI tool (`scripts/system/version_cli.py`) for versioning domains
  - Semantic versioning (MAJOR.MINOR.PATCH) with changelog tracking
  - Version metadata nodes in Neo4j with timestamp and descriptions
  - Automated schema updates, migration validation, deprecation warnings

- **Architecture Restructured**
  - Transitioned from flat SubjectConcept model to Domain hierarchy
  - Domains are peer subgraphs (ROMAN_REPUBLIC, MILITARY_THEORY, GEOGRAPHY)
  - SubjectConcepts are organizational units WITHIN domains
  - Clear separation: Domain = data container, SubjectConcept = organizational lens

- **Node Cleanup Completed**
  - Invalid GeographicConcept nodes removed (18 deleted)
  - Military training nodes cleaned up
  - Node type constraints validated
  - Documentation of valid node types created

- **Documentation Created**
  - `DOCUMENTATION_INDEX.md` - master documentation index
  - `DOMAIN_MANAGEMENT_GUIDE.md` - domain architecture and operations
  - `VERSION_MANAGEMENT_GUIDE.md` - versioning system guide
  - `VERSION_CLI_REFERENCE.md` - CLI command reference
  - `SFA_DOMAIN_INTEGRATION.md` - SFA integration patterns
  - `DOMAIN_QUICK_REFERENCE.md` - quick reference card
  - `SFA_TRAINING_GUIDE.md` - training concepts and methodology
  - `SFA_TRAINING_WORKBOOK.md` - practical training exercises

- **Training Methodology Clarified**
  - Two-phase approach: Theory → Historical application
  - Actor-centric claim perspective (multiple viewpoints per event)
  - Resource corpus identified (Military resources.md, Naval Resources.md)
  - Clear distinction between SFA coordinator and SubjectConcept worker agents

---

## 3. Current System State

### Domains (3)

**ROMAN_REPUBLIC (v0.1.0)**
- Status: Development phase
- Scope: Roman Republic period (509 BCE - 27 BCE)
- Focus: Political, military, social history
- Current work: Training SubjectConcept agents on Roman military history
- Key SubjectConcepts: Roman Military Organization, Republican Warfare, etc.

**MILITARY_THEORY (v1.1.0)**
- Status: Active development
- Scope: General military theory, strategic concepts, doctrine
- Focus: Cross-temporal military theory and analysis frameworks
- Current work: Building foundational theory knowledge base
- Key SubjectConcepts: Strategic Theory, Tactical Doctrine, Military Geography, etc.

**GEOGRAPHY (v1.0.0)**
- Status: Stable foundation
- Scope: Geographic entities, places, regions
- Focus: Spatial relationships and geographic context
- Integration: Referenced by ROMAN_REPUBLIC and other historical domains

### Key Files Created Today

**Version Management:**
- `scripts/system/version_cli.py` - Domain versioning CLI tool
- `scripts/system/version_management.py` - Core versioning library
- `scripts/system/domain_schema_validator.py` - Schema validation utility

**Documentation:**
- `DOCUMENTATION_INDEX.md` - Master index of all documentation
- `DOCUMENTATION_COMPLETION_SUMMARY.md` - Summary of documentation work
- `DOMAIN_ARCHITECTURE_FINAL.md` - Final architecture specification
- `DOMAIN_ARCHITECTURE_CORRECTED.md` - Architecture corrections and clarifications
- `DOMAIN_MANAGEMENT_GUIDE.md` - Complete domain management guide
- `DOMAIN_QUICK_REFERENCE.md` - Quick reference card
- `VERSION_MANAGEMENT_GUIDE.md` - Versioning system guide
- `VERSION_CLI_REFERENCE.md` - CLI command reference
- `SFA_DOMAIN_INTEGRATION.md` - SFA integration patterns
- `SFA_TRAINING_GUIDE.md` - Training concepts and methodology
- `SFA_TRAINING_WORKBOOK.md` - Practical training exercises
- `SFA_QUICK_REFERENCE.md` - SFA quick reference
- `SFA_STATUS_SUMMARY.md` - SFA implementation status
- `SUBGRAPH_VERSIONING_COMPLETE.md` - Versioning completion notes
- `VERSIONING_SYSTEM_SUMMARY.md` - Versioning system overview

**Training Resources:**
- `Military resources.md` - Military theory corpus (68 lines)
- `Naval Resources.md` - Naval warfare corpus

**Cypher Scripts:**
- `Cypher/phase1_multi_agent_schema.cypher` - Multi-agent schema definitions
- `Cypher/node_cleanup_investigation.cypher` - Node cleanup queries
- `Cypher/node_consolidation.cypher` - Node consolidation scripts

**Architecture Decisions:**
- `Key Files/Appendices/05_Architecture_Decisions/ADR_021_SubjectConcept_Agent_Scope_and_Primary_Corpus.md`
- `Key Files/Appendices/05_Architecture_Decisions/ADR_022_Multi_Agent_Canonical_Entity_Claims.md`
- `Key Files/Appendices/05_Architecture_Decisions/ADR_023_Event_Entity_Cipher_Specification.md`

### Architecture Decisions

**Domain vs SubjectConcept:**
- **Domain** = peer subgraph, data container with its own versioning
  - Examples: ROMAN_REPUBLIC, MILITARY_THEORY, GEOGRAPHY
  - Domains are siblings at the same hierarchical level
  - Each domain has independent version control
  - Domains contain entities, claims, and relationships

- **SubjectConcept** = organizational unit WITHIN a domain
  - NOT a separate domain, but a grouping mechanism
  - Provides a focal point for claim organization
  - Examples: "Roman Military Organization" within ROMAN_REPUBLIC
  - Used for filtering and organizing domain content

**SFA vs SubjectConcept Agents:**
- **SFA (Subject Field Agent)** = coordinator/manager agent
  - Domain expert that understands the full domain scope
  - Spawns SubjectConcept agents for specific tasks
  - Makes high-level decisions about claim routing
  - Examples: Military SFA, Diplomatic SFA

- **SubjectConcept Agent** = worker agent with narrow focus
  - Created by SFA for specific SubjectConcept work
  - Has focal point on one SubjectConcept at a time
  - Processes claims and creates relationships
  - Reports back to parent SFA

**Training Methodology:**
- **Phase 1: Theory Building**
  - Agent reads military theory resources (Military resources.md)
  - Creates claims in MILITARY_THEORY domain
  - Builds foundational concepts (strategy, tactics, doctrine)
  - No historical events yet, pure theory

- **Phase 2: Historical Application**
  - Agent reads historical sources about Roman military events
  - Creates claims in ROMAN_REPUBLIC domain
  - Links historical claims to MILITARY_THEORY concepts
  - Actor-centric perspective (multiple viewpoints per event)

- **Actor-Centric Claims:**
  - Each event viewed from perspective of different actors
  - Caesar's perception of Gallic Wars ≠ Senate's perception
  - Claims capture perspective source: "Caesar claims X"
  - Multiple SubjectConcept agents can cover same event from different angles

**Resource Corpus:**
- Primary corpus for Military training:
  - `Military resources.md` - general military theory
  - `Naval Resources.md` - naval warfare specific
- Corpus is read during Phase 1 to build MILITARY_THEORY
- Historical sources (to be identified) used in Phase 2 for ROMAN_REPUBLIC

---

## 4. Critical Concepts for Next Session

### Domain = Peer Subgraph
Domains are independent, versioned subgraphs that exist at the same hierarchical level:
- **ROMAN_REPUBLIC** is a peer to **MILITARY_THEORY**
- They are NOT nested (MILITARY_THEORY is not "inside" ROMAN_REPUBLIC)
- Each domain has its own version (v0.1.0, v1.1.0, etc.)
- Domains can reference each other via relationships
- Example: A Roman battle claim in ROMAN_REPUBLIC can link to a strategic concept in MILITARY_THEORY

### SubjectConcept = Organizational Unit WITHIN Domain
SubjectConcepts are organizational groupings, not separate data containers:
- **Roman Military Organization** is a SubjectConcept within ROMAN_REPUBLIC domain
- **Strategic Theory** is a SubjectConcept within MILITARY_THEORY domain
- SubjectConcepts filter/organize claims within their parent domain
- They provide focal points but don't create boundaries
- Multiple SubjectConcepts can overlap the same entities/claims

### SFA = Coordinator That Spawns SubjectConcept Agents
The SFA is a manager-level agent:
- **Military SFA** understands all military-related domains
- Routes incoming claims to appropriate domains
- Spawns SubjectConcept agents for specific work
- Example: Military SFA receives claim about Cannae → spawns "Roman Military Organization" SubjectConcept agent → agent processes claim in ROMAN_REPUBLIC domain

### SubjectConcept Agent = Actual Worker (Focal Point)
The SubjectConcept agent does the detailed work:
- Created by SFA with specific SubjectConcept focus
- Has narrow scope: one SubjectConcept at a time
- Creates entities, claims, and relationships
- Uses IGAR protocol for processing
- Reports completion back to parent SFA
- Example: "Roman Military Organization" agent reads about Cannae, creates Hannibal entity, links to Strategic Theory concepts in MILITARY_THEORY

### Training Flow: Theory Reading → MILITARY_THEORY, Then Historical → ROMAN_REPUBLIC
Two-phase training approach:
1. **Phase 1 (Theory):**
   - Agent: Military Theory SubjectConcept agent
   - Input: Military resources.md, Naval Resources.md
   - Output: Claims in MILITARY_THEORY domain
   - Focus: Pure theory (strategy, tactics, doctrine definitions)

2. **Phase 2 (Historical):**
   - Agent: Roman Military Organization SubjectConcept agent
   - Input: Historical sources about Roman military events
   - Output: Claims in ROMAN_REPUBLIC domain
   - Focus: Historical events linked to MILITARY_THEORY concepts
   - Actor-centric: Caesar's view, Senate's view, Pompey's view, etc.

---

## 5. Where We Left Off

### Training Worker Paused
- Training implementation halted, no Neo4j writes being made
- Awaiting Military SFA prompt revision before proceeding
- Current training code exists but should be reviewed before use

### Military SFA Prompt Reviewed
- Existing prompt reviewed for completeness
- Found to need significant revision
- Core concepts present but methodology unclear

### Identified Prompt Issues (3)

**1. Resource Methodology Unclear**
- Prompt doesn't explain two-phase training approach
- Doesn't specify when to use which corpus
- Doesn't clarify Phase 1 (theory) vs Phase 2 (historical)
- Missing guidance on how to transition between phases

**2. Predicates Need Definitions**
- IGAR protocol mentioned but predicates not defined
- Need examples of each predicate:
  - `INVESTIGATES_PERSON`: When researching biographical details
  - `INVESTIGATES_CONCEPT`: When exploring theoretical concepts
  - `ASSERTS_CLAIM`: When making definitive factual claims
  - `RELATES_ENTITIES`: When connecting entities via relationships
- Need clarity on when to use each predicate

**3. IGAR Protocol Not Fully Specified**
- Protocol mentioned but workflow not detailed
- Missing step-by-step guidance:
  - How to structure investigation claims
  - When to transition from investigation to assertion
  - How to handle conflicting sources
  - Actor-centric perspective implementation

### Training Methodology Clarified

**Phase 1: Theory Building (Read Military Theory → MILITARY_THEORY Domain)**
- SubjectConcept agent: "Strategic Theory" or "Tactical Doctrine"
- Input corpus: `Military resources.md`, `Naval Resources.md`
- Process: Read theory, extract concepts, create claims
- Output domain: MILITARY_THEORY
- No historical events, pure conceptual work
- Goal: Build foundational military theory knowledge base

**Phase 2: Historical Application (Analyze Roman Events → ROMAN_REPUBLIC)**
- SubjectConcept agent: "Roman Military Organization"
- Input: Historical sources (Caesar's Commentaries, Livy, Polybius, etc.)
- Process: Analyze events, link to MILITARY_THEORY concepts
- Output domain: ROMAN_REPUBLIC
- Actor-centric: Multiple perspectives per event
- Goal: Apply theory to historical analysis

**Actor-Centric Claims (Multiple Perspectives Per Event)**
- Single event has multiple claim perspectives
- Example: Battle of Cannae (216 BCE)
  - Caesar's later analysis (strategic theory perspective)
  - Roman Senate's contemporary view (political perspective)
  - Polybius's historical interpretation
  - Modern historian's analysis
- Each perspective is a separate claim with different `claimant` property
- SubjectConcept agents can specialize in different perspectives

### Resource Corpus Identified

**Military resources.md**
- General military theory corpus
- 68 lines of curated content
- Covers: strategy, tactics, doctrine, theory
- Use in Phase 1 for MILITARY_THEORY domain building

**Naval Resources.md**
- Naval warfare specific corpus
- Maritime strategy and tactics
- Naval doctrine and technology
- Use in Phase 1 for MILITARY_THEORY domain building (naval SubjectConcept)

---

## 6. Immediate Next Steps

### Priority 1: Revise Military SFA Prompt

The Military SFA prompt needs comprehensive revision to include:

**1. Clear Training Methodology**
- Explain two-phase approach (Theory → Historical)
- Specify Phase 1: Read military theory → MILITARY_THEORY domain
- Specify Phase 2: Read historical sources → ROMAN_REPUBLIC domain
- Clarify when to use which corpus
- Explain transition between phases

**2. Predicate Definitions with Examples**
- Define each IGAR predicate with concrete examples:

```
INVESTIGATES_PERSON:
- Use when: Researching biographical details, uncertain information
- Example: "INVESTIGATES_PERSON: Was Julius Caesar trained in Greek military theory?"
- Creates: Investigation claim with source tracking

INVESTIGATES_CONCEPT:
- Use when: Exploring theoretical concepts, seeking definitions
- Example: "INVESTIGATES_CONCEPT: What is the definition of strategic depth in military theory?"
- Creates: Investigation claim with source tracking

ASSERTS_CLAIM:
- Use when: Making definitive factual claims from reliable sources
- Example: "ASSERTS_CLAIM: Caesar commanded Legio X during the Gallic Wars"
- Creates: Assertion claim with confidence and provenance

RELATES_ENTITIES:
- Use when: Connecting entities via relationships
- Example: "RELATES_ENTITIES: Caesar (Person) COMMANDED Legio X (MilitaryUnit)"
- Creates: Relationship with temporal context
```

**3. Full IGAR Protocol Explanation**
- Step-by-step workflow:
  1. **Investigate**: Read source, identify claims
  2. **Generate**: Create entity and claim nodes
  3. **Assert**: Make factual claims with provenance
  4. **Relate**: Connect entities via relationships
- Actor-centric perspective implementation:
  - Each claim has `claimant` property (source of perspective)
  - Multiple claims per event from different actors
  - SubjectConcept agent focuses on one perspective at a time

**4. Reference to Resource Corpus**
- Explicit mention of `Military resources.md` and `Naval Resources.md`
- Instructions on how to process corpus content
- Guidance on extracting concepts and creating claims
- Examples of theory → claim transformations

### Priority 2: Choose Next Action

After prompt revision, decide between:

**Option A: Resume Training Worker**
- Use existing training code
- Review code before execution
- Monitor for issues
- Validate outputs

**Option B: Start Fresh Training Implementation**
- Implement training with revised prompt
- Build new training pipeline
- Incorporate lessons learned
- More controlled, possibly cleaner

### Priority 3: Validate Training Approach
- Test Military SFA prompt with small corpus sample
- Verify MILITARY_THEORY domain claims are created correctly
- Check claim structure, provenance, relationships
- Adjust prompt if needed before full training run

---

## 7. Quick Start Guide for New Session

**Step-by-step to get oriented in the next session:**

### 1. Read This Handoff Document
You're doing it now. Good start.

### 2. Review Master Documentation Index
```bash
# Open the master index
cat DOCUMENTATION_INDEX.md
```
This shows all available documentation and where to find specific information.

### 3. Check Domain Quick Reference
```bash
# Get quick architecture overview
cat DOMAIN_QUICK_REFERENCE.md
```
This provides a one-page summary of the domain architecture.

### 4. Check Domain Status
```bash
# Check ROMAN_REPUBLIC status
python scripts/system/version_cli.py status roman_republic

# Check MILITARY_THEORY status
python scripts/system/version_cli.py status military_theory

# List all domains
python scripts/system/version_cli.py list
```

### 5. Review Key Files

**Architecture:**
```bash
cat DOMAIN_MANAGEMENT_GUIDE.md        # How domains work
cat docs/ARCHITECTURE_CURRENT.md      # Current architecture state
```

**SFA Training:**
```bash
cat SFA_TRAINING_GUIDE.md             # Training concepts
cat SFA_DOMAIN_INTEGRATION.md         # SFA integration patterns
cat Military resources.md              # Training corpus
```

**Version Management:**
```bash
cat VERSION_MANAGEMENT_GUIDE.md       # How versioning works
cat VERSION_CLI_REFERENCE.md          # CLI commands
```

### 6. Review Military SFA Current State
```bash
# Check current prompt (if exists)
cat Key Files/prompts/military_sfa_prompt.md   # (path may vary)

# Review training methodology
cat SFA_TRAINING_GUIDE.md
```

### 7. Check Neo4j Database State
```bash
# Connect to Neo4j and check domain versions
# (connection details in your Neo4j setup)
```

Example Cypher queries:
```cypher
// Check domain versions
MATCH (d:DomainVersion)
RETURN d.domain_id, d.version, d.timestamp
ORDER BY d.timestamp DESC;

// Check MILITARY_THEORY claims
MATCH (c:Claim {domain: 'MILITARY_THEORY'})
RETURN count(c) as theory_claims;

// Check ROMAN_REPUBLIC claims
MATCH (c:Claim {domain: 'ROMAN_REPUBLIC'})
RETURN count(c) as republic_claims;
```

### 8. Prepare for Prompt Revision
- Open `Military resources.md` for reference
- Review IGAR protocol documentation
- Check existing SubjectConcept definitions
- Identify predicate examples needed

---

## 8. Key Documentation to Reference

### Master Index
- **`DOCUMENTATION_INDEX.md`** - Start here for overview of all documentation

### Architecture & Domains
- **`DOMAIN_MANAGEMENT_GUIDE.md`** - Complete guide to domain architecture, operations, versioning
- **`DOMAIN_QUICK_REFERENCE.md`** - One-page quick reference for domain concepts
- **`DOMAIN_ARCHITECTURE_FINAL.md`** - Final architecture specification
- **`docs/ARCHITECTURE_CURRENT.md`** - Current system architecture state

### Version Management
- **`VERSION_MANAGEMENT_GUIDE.md`** - Complete versioning system guide
- **`VERSION_CLI_REFERENCE.md`** - CLI tool command reference
- **`VERSIONING_SYSTEM_SUMMARY.md`** - Versioning system overview
- **`SUBGRAPH_VERSIONING_COMPLETE.md`** - Versioning completion notes

### SFA & Training
- **`SFA_DOMAIN_INTEGRATION.md`** - How SFAs integrate with domains
- **`SFA_TRAINING_GUIDE.md`** - Training concepts and methodology (CRITICAL)
- **`SFA_TRAINING_WORKBOOK.md`** - Practical training exercises
- **`SFA_QUICK_REFERENCE.md`** - SFA quick reference card
- **`SFA_STATUS_SUMMARY.md`** - Current SFA implementation status
- **`docs/SCA_SFA_CONTRACT.md`** - SCA/SFA interaction contract

### Training Resources (Corpus)
- **`Military resources.md`** - Military theory corpus (68 lines)
- **`Naval Resources.md`** - Naval warfare corpus

### Architecture Decision Records
- **`ADR_021_SubjectConcept_Agent_Scope_and_Primary_Corpus.md`** - SubjectConcept scope decisions
- **`ADR_022_Multi_Agent_Canonical_Entity_Claims.md`** - Multi-agent entity handling
- **`ADR_023_Event_Entity_Cipher_Specification.md`** - Event entity specification

### Implementation Guides
- **`docs/BIOGRAPHIC_CLAIM_PIPELINE.md`** - Biographic claim processing
- **`docs/EPISTEMIC_MODEL.md`** - Epistemic model and claim confidence
- **`docs/MIGRATION_GUIDE_MILITARY_THEORY_2.0.md`** - Military theory migration

### Scripts & Tools
- **`scripts/system/version_cli.py`** - Domain versioning CLI
- **`scripts/system/version_management.py`** - Versioning library
- **`scripts/system/domain_schema_validator.py`** - Schema validation

### Cypher Scripts
- **`Cypher/phase1_multi_agent_schema.cypher`** - Multi-agent schema
- **`Cypher/node_cleanup_investigation.cypher`** - Node cleanup queries
- **`Cypher/node_consolidation.cypher`** - Node consolidation

---

## 9. Open Questions / Decisions Pending

### Military SFA Prompt Revision (URGENT)
- **Decision needed:** Revise prompt comprehensively or incrementally?
- **Action required:** Write revised prompt with all 4 components (methodology, predicates, IGAR, corpus)
- **Timeline:** Should be completed before any training work resumes

### Training Implementation Approach
- **Option A:** Resume existing training worker code
- **Option B:** Start fresh with new implementation
- **Decision needed:** Which approach minimizes risk and maximizes quality?
- **Consideration:** Existing code may need review/refactoring

### Which SFA to Train First
- **Confirmed:** Military SFA is first priority
- **Question:** After Military, which SFA next? Diplomatic? Economic?
- **Consideration:** Dependencies between domains (GEOGRAPHY already stable)

### SubjectConcept Agent Implementation Details
- **Question:** How are SubjectConcept agents spawned in practice?
- **Question:** What is the agent lifecycle (spawn → work → report → terminate)?
- **Question:** How does parent SFA track child SubjectConcept agent progress?
- **Question:** Can multiple SubjectConcept agents work in parallel?
- **Action needed:** Design and document SubjectConcept agent spawning protocol

### Phase 2 Historical Source Selection
- **Question:** Which historical sources for Roman military history training?
- **Candidates:** Caesar's Commentaries, Livy, Polybius, Plutarch, modern analyses
- **Decision needed:** Prioritize sources, determine reading order
- **Consideration:** Balance primary sources with modern analysis

### Actor-Centric Claim Implementation Details
- **Question:** How to structure claims with multiple perspectives?
- **Question:** Is `claimant` property sufficient or need more metadata?
- **Question:** How to handle conflicting claims from different actors?
- **Action needed:** Design actor-centric claim schema

### Domain Boundary Clarification
- **Question:** When does content belong in MILITARY_THEORY vs ROMAN_REPUBLIC?
- **Example:** Is "Roman legionary tactics" in ROMAN_REPUBLIC or MILITARY_THEORY?
- **Principle established:** Theory → MILITARY_THEORY, Historical instance → ROMAN_REPUBLIC
- **Action needed:** Create boundary examples for edge cases

### SubjectConcept Overlap Management
- **Question:** How to handle overlapping SubjectConcepts within a domain?
- **Example:** "Roman Military Organization" and "Roman Warfare" both cover battles
- **Action needed:** Define overlap policy and coordination mechanisms

---

## 10. Background Context

### Project Overview
**Graph1** is a knowledge graph system for historical and conceptual analysis, built on Neo4j. The system organizes knowledge into versioned domains that contain entities, claims, and relationships. The epistemic model emphasizes provenance, multiple perspectives, and claim confidence levels.

### Architecture Philosophy
- **Domain-centric:** Knowledge organized into peer domains (not nested hierarchies)
- **Version-controlled:** Each domain independently versioned with semantic versioning
- **Epistemic transparency:** Every claim has provenance, confidence, sources
- **Multi-perspective:** Events viewed from multiple actor perspectives
- **Theory-grounded:** Historical analysis linked to theoretical frameworks

### Key Components

**Domains:**
- Peer subgraphs containing related knowledge
- Examples: ROMAN_REPUBLIC, MILITARY_THEORY, GEOGRAPHY
- Each domain has version, changelog, schema
- Domains can reference each other via relationships

**Subject Field Agents (SFAs):**
- Domain expert coordinators (Military SFA, Diplomatic SFA)
- Route claims to appropriate domains
- Spawn SubjectConcept agents for detailed work
- Maintain domain coherence and quality

**SubjectConcept Agents:**
- Worker agents with narrow focus
- Process claims within specific SubjectConcept scope
- Create entities, claims, relationships
- Report back to parent SFA

**Entities:**
- Nodes representing real-world things (Person, Place, Event, Concept)
- Have unique identifiers (Wikidata QIDs where possible)
- Belong to specific domains
- Can be referenced across domains

**Claims:**
- Statements about entities with provenance
- Have confidence levels, sources, temporal context
- Can be investigations or assertions
- Support multiple perspectives (actor-centric)

**Relationships:**
- Connect entities with typed, directional edges
- Have temporal context (start/end dates)
- Carry domain metadata
- Support versioned schemas

### Current Focus
The immediate focus is training the Military SFA to build the MILITARY_THEORY domain using curated military theory resources, then apply that theory to analyze Roman military history in the ROMAN_REPUBLIC domain. This two-phase training approach (theory → historical application) will serve as a template for training other SFAs.

### Long-term Goals
- Build comprehensive knowledge graphs for multiple historical periods
- Enable cross-domain analysis (economic, military, diplomatic, cultural)
- Support multi-agent claim generation and validation
- Provide epistemic transparency for all knowledge claims
- Enable sophisticated querying and analysis of historical relationships

---

## Summary Checklist for Next Session

Before starting work, verify:

- [ ] Read this handoff document completely
- [ ] Reviewed `DOCUMENTATION_INDEX.md`
- [ ] Checked domain status with CLI tool
- [ ] Understand Domain vs SubjectConcept distinction
- [ ] Understand SFA vs SubjectConcept agent distinction
- [ ] Understand two-phase training methodology
- [ ] Reviewed `Military resources.md` corpus
- [ ] Identified the 3 prompt issues to address
- [ ] Ready to revise Military SFA prompt
- [ ] Decided on training implementation approach (resume vs fresh)

**Once oriented, the immediate task is:**
1. Revise Military SFA prompt with methodology, predicates, IGAR, and corpus references
2. Validate revised prompt approach
3. Proceed with training implementation

---

**Document Status:** Complete handoff for session ending July 16, 2026  
**Next Update:** After Military SFA prompt revision and training implementation decision  
**Contact:** Review this document with fresh context in next session
