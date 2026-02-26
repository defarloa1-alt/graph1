# Entity Cipher for Vertex Jumps: Three-Tier Identity Architecture

**Created:** February 21, 2026  
**Status:** Canonical Reference  
**Revision:** 1.0  
**Companion Document:** CLAIM_ID_ARCHITECTURE.md (Tier 3 Claim Ciphers)

---

## 1. Purpose & Design Rationale

### 1.1 The Problem

Graph traversal via pattern matching (e.g., `MATCH (a)-[:REL]->(b) WHERE b.qid = "Q1048"`) is expensive. It requires Neo4j to walk edges, filter properties, and evaluate conditions at every hop. As the Chrystallum graph grows across 18 facets, thousands of SubjectConcepts, and millions of claims, traversal-based queries become the bottleneck.

### 1.2 The Solution: Cipher as Computed Address

Every vertex in Chrystallum gets a **deterministic, content-addressable cipher** — a pre-computed key that enables direct index seeks (O(1) lookup) instead of traversal. The cipher is built from Wikidata QIDs, PIDs, and qualifiers, making it inherently **multilingual** — all natural language is a rendering layer on top of language-neutral identifiers.

### 1.3 Three-Tier Model

| Tier | Name | Purpose | Scope |
|------|------|---------|-------|
| **Tier 1** | Entity Cipher | Identify a *thing* across all subgraphs | One per entity in the graph |
| **Tier 2** | Faceted Entity Cipher | Identify a *thing in a facet context* | Up to 18 per entity (one per facet) |

**Multi-facet verification:** An entity appearing in 3+ facets (e.g. Caesar in POLITICAL, MILITARY, BIOGRAPHIC) receives three separate faceted ciphers (`fent_pol_Q1048_Q17167`, `fent_mil_Q1048_Q17167`, `fent_bio_Q1048_Q17167`). Each SubjectConcept × Facet × Entity combination is a distinct Tier 2 address.
| **Tier 3** | Claim Cipher | Identify a *specific assertion* about a thing | Many per entity per facet |

**Relationship to CLAIM_ID_ARCHITECTURE.md:**
- Tier 3 (Claim Cipher) is fully specified in CLAIM_ID_ARCHITECTURE.md
- This document specifies Tier 1 and Tier 2, and shows how all three tiers compose

---

## 2. Tier 1: Entity Cipher

### 2.1 Definition

The Entity Cipher is the **cross-subgraph join key** — the single identifier that connects all faceted views, claims, and relationships for one entity. It answers: "What is this thing, regardless of which facet I'm looking at?"

### 2.2 Formula

```python
entity_cipher = f"ent_{type_prefix}_{resolved_id}"
```

**Components:**

| Component | Source | Example |
|-----------|--------|---------|
| `ent_` | Fixed prefix (entity namespace) | `ent_` |
| `type_prefix` | 3-char entity type code (see §2.3) | `per_` (Person) |
| `resolved_id` | QID, BabelNet synset, or Chrystallum synthetic (see §5) | `Q1048` |

### 2.3 Entity Type Prefix Registry

| Entity Type | Prefix | Example Cipher |
|-------------|--------|----------------|
| PERSON | `per` | `ent_per_Q1048` (Julius Caesar) |
| EVENT | `evt` | `ent_evt_Q25238182` (Crossing of the Rubicon) |
| PLACE | `plc` | `ent_plc_Q220` (Rome) |
| SUBJECTCONCEPT | `sub` | `ent_sub_Q17167` (Roman Republic) |
| WORK | `wrk` | `ent_wrk_Q644312` (Plutarch, Life of Caesar) |
| ORGANIZATION | `org` | `ent_org_Q193236` (Roman Senate) |
| PERIOD | `prd` | `ent_prd_Q6813` (Hellenistic period - purely temporal) |
| MATERIAL | `mat` | `ent_mat_Q753` (Copper) |
| OBJECT | `obj` | `ent_obj_Q34379` (Sword) |

**CRITICAL: PERIOD vs TemporalAnchor Distinction (ADR-002 Alignment)**

**TemporalAnchor is a LABEL, not an entity type.**

**Decision Rules:**

| Entity | P31 Classes | Primary Type | Cipher | TemporalAnchor Label? |
|--------|-------------|--------------|--------|--------------------|
| Q17167 (Roman Republic) | Q11514315 (period) + Q41156 (polity) | **ORGANIZATION** | `ent_org_Q17167` | ✅ Yes (add label) |
| Q2277 (Roman Empire) | Q11514315 (period) + Q112099 (empire) | **ORGANIZATION** | `ent_org_Q2277` | ✅ Yes (add label) |
| Q6813 (Hellenistic period) | Q11514315 (period) ONLY | **PERIOD** | `ent_prd_Q6813` | ✅ Yes (add label) |
| Q11768 (Stone Age) | Q11514315 (period) ONLY | **PERIOD** | `ent_prd_Q11768` | ✅ Yes (add label) |

**Classification Rule:**
- If entity has BOTH temporal (Q11514315) AND institutional (Q41156, Q112099, Q43229) P31 classes → Primary type is **institutional** (ORGANIZATION, not PERIOD)
- If entity has ONLY temporal P31 → Type is **PERIOD**
- **Both cases:** Add `:TemporalAnchor` label + temporal properties

**Example:**
```cypher
// Roman Republic (polity + period)
(:Entity:Organization:TemporalAnchor {
  entity_cipher: "ent_org_Q17167",    // ORGANIZATION is primary
  entity_type: "ORGANIZATION",
  is_temporal_anchor: true,           // Flag + label both present
  temporal_scope: "-0509/-0027"
})

// Hellenistic period (purely temporal)
(:Entity:Period:TemporalAnchor {
  entity_cipher: "ent_prd_Q6813",     // PERIOD is primary
  entity_type: "PERIOD",
  is_temporal_anchor: true,
  temporal_scope: "-0323/-0031"
})
```

**Rules:**
- Prefix is **always 3 characters**, lowercase
- Entity type determined by SCA using P31 classification (see decision table above)
- TemporalAnchor is a **capability** (label + properties), not a type
- New entity types require registry update (locked list, like facets)

### 2.4 Properties

| Property | Description |
|----------|-------------|
| Deterministic | Same entity → same cipher, always |
| Namespace-aware | Encodes authority source (wd/bn/crys) via resolved_id format |
| Human-readable | `ent_per_Q1048` is immediately parseable |
| Index-seekable | Neo4j composite index on `(entity_cipher)` enables O(1) lookup |

### 2.5 Neo4j Node Schema

```cypher
(:Entity {
  entity_cipher: "ent_per_Q1048",          // Tier 1 (PRIMARY KEY)
  qid: "Q1048",                            // Wikidata QID (if available)
  entity_type: "PERSON",                   // Canonical type
  namespace: "wd",                         // Authority: "wd" | "bn" | "crys"
  label_en: "Julius Caesar",               // English label (display only)
  label_la: "Gaius Iulius Caesar",         // Latin label (display only)
  instance_of: ["Q5"],                     // P31 values (Person)
  created_at: "2026-02-21T10:00:00Z",
  created_by_agent: "sca_001"
})
```

### 2.6 Index

```cypher
CREATE INDEX entity_cipher_idx IF NOT EXISTS
FOR (n:Entity) ON (n.entity_cipher);

CREATE INDEX entity_qid_idx IF NOT EXISTS
FOR (n:Entity) ON (n.qid);

CREATE INDEX entity_type_idx IF NOT EXISTS
FOR (n:Entity) ON (n.entity_type, n.entity_cipher);
```

---

## 3. Tier 2: Faceted Entity Cipher

### 3.1 Definition

The Faceted Entity Cipher is the **subgraph address** — it identifies a specific entity evaluated from a specific facet perspective, anchored to a specific SubjectConcept. It answers: "What does this entity look like from the POLITICAL perspective within the Roman Republic?"

### 3.2 Formula

```python
faceted_cipher = f"fent_{facet_prefix}_{base_qid}_{subjectconcept_id}"
```

**Components:**

| Component | Source | Example |
|-----------|--------|---------|
| `fent_` | Fixed prefix (faceted entity namespace) | `fent_` |
| `facet_prefix` | 3-char facet code (see §3.3) | `pol_` (POLITICAL) |
| `base_qid` | Entity QID extracted from Tier 1 cipher | `Q1048` |
| `subjectconcept_id` | QID of the anchoring SubjectConcept | `Q17167` |

### 3.3 Facet Prefix Registry (18 Canonical Facets)

| Facet | Prefix | Example Faceted Cipher |
|-------|--------|----------------------|
| ARCHAEOLOGICAL | `arc` | `fent_arc_Q1048_Q17167` |
| ARTISTIC | `art` | `fent_art_Q1048_Q17167` |
| BIOGRAPHIC | `bio` | `fent_bio_Q1048_Q17167` |
| COMMUNICATION | `com` | `fent_com_Q1048_Q17167` |
| CULTURAL | `cul` | `fent_cul_Q1048_Q17167` |
| DEMOGRAPHIC | `dem` | `fent_dem_Q1048_Q17167` |
| DIPLOMATIC | `dip` | `fent_dip_Q1048_Q17167` |
| ECONOMIC | `eco` | `fent_eco_Q1048_Q17167` |
| ENVIRONMENTAL | `env` | `fent_env_Q1048_Q17167` |
| GEOGRAPHIC | `geo` | `fent_geo_Q1048_Q17167` |
| INTELLECTUAL | `int` | `fent_int_Q1048_Q17167` |
| LINGUISTIC | `lin` | `fent_lin_Q1048_Q17167` |
| MILITARY | `mil` | `fent_mil_Q1048_Q17167` |
| POLITICAL | `pol` | `fent_pol_Q1048_Q17167` |
| RELIGIOUS | `rel` | `fent_rel_Q1048_Q17167` |
| SCIENTIFIC | `sci` | `fent_sci_Q1048_Q17167` |
| SOCIAL | `soc` | `fent_soc_Q1048_Q17167` |
| TECHNOLOGICAL | `tec` | `fent_tec_Q1048_Q17167` |

### 3.4 Vertex Jump Pattern

The Tier 2 cipher enables **direct facet-to-facet jumps** without graph traversal:

```cypher
// Jump from Caesar's MILITARY subgraph to POLITICAL subgraph
// Two index seeks — no traversal, no pattern matching on edges

MATCH (mil:FacetClaim {
  subject_entity_cipher: "ent_per_Q1048",
  facet_id: "MILITARY"
})

MATCH (pol:FacetClaim {
  subject_entity_cipher: "ent_per_Q1048",
  facet_id: "POLITICAL"
})

RETURN mil, pol
// Both queries hit composite index: O(1) per seek
```

**Cross-SubjectConcept jump:**

```cypher
// Caesar in Roman Republic vs Caesar in Gallic Wars
MATCH (rr:FacetClaim {
  subject_entity_cipher: "ent_per_Q1048",
  facet_id: "MILITARY",
  subjectconcept_cipher: "ent_sub_Q17167"    // Roman Republic
})

MATCH (gw:FacetClaim {
  subject_entity_cipher: "ent_per_Q1048",
  facet_id: "MILITARY",
  subjectconcept_cipher: "ent_sub_Q190498"   // Gallic Wars
})

RETURN rr, gw
```

### 3.5 Neo4j Node Schema (Option: Materialized Hub Nodes)

**Decision: Materialize Tier 2 as Hub Nodes**

Each `SubjectConcept × Facet × Entity` combination creates a FacetedEntity hub node. All FacetClaims within that context connect to it.

```cypher
(:FacetedEntity {
  faceted_cipher: "fent_pol_Q1048_Q17167",   // Tier 2 (PRIMARY KEY)
  entity_cipher: "ent_per_Q1048",            // Tier 1 (join key)
  facet_id: "POLITICAL",                     // Facet dimension
  subjectconcept_id: "Q17167",               // Anchoring SubjectConcept
  claim_count: 47,                           // Number of claims in this context
  avg_confidence: 0.87,                      // Aggregate confidence
  last_updated: "2026-02-21T10:00:00Z",
  evaluated_by_agent: "political_sfa_001"
})

// Relationships
(:Entity {entity_cipher: "ent_per_Q1048"})
  -[:HAS_FACETED_VIEW]->
(:FacetedEntity {faceted_cipher: "fent_pol_Q1048_Q17167"})
  -[:CONTAINS_CLAIM]->
(:FacetClaim {cipher: "fclaim_pol_b22020c0..."})
```

### 3.6 Index

```cypher
CREATE INDEX faceted_cipher_idx IF NOT EXISTS
FOR (n:FacetedEntity) ON (n.faceted_cipher);

CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS
FOR (n:FacetedEntity) ON (n.entity_cipher, n.facet_id);

CREATE INDEX faceted_subj_idx IF NOT EXISTS
FOR (n:FacetedEntity) ON (n.subjectconcept_id, n.facet_id);
```

---

## 4. Cipher-Eligible Qualifiers (Option B)

### 4.1 Problem

Wikidata statements carry qualifiers that add context (time, location, ordinal). Some qualifiers define the **identity** of what is being asserted (e.g., start time distinguishes 1st consulship from 2nd). Others are **metadata** (determination method, reference URL). Only identity qualifiers belong in the cipher.

### 4.2 Cipher-Eligible Qualifier Registry (Locked List)

| PID | Label | Who/What/When/Where/How | Why Cipher-Eligible |
|-----|-------|-------------------------|---------------------|
| P580 | start time | WHEN | Distinguishes repeated relationships (1st vs 2nd consulship) |
| P582 | end time | WHEN | Bounds the temporal scope of the assertion |
| P585 | point in time | WHEN | Specific date assertions (battle dates, death dates) |
| P276 | location | WHERE | Same event at different locations = different assertions |
| P1545 | series ordinal | WHICH | Distinguishes 1st, 2nd, 3rd instance of same relationship |

### 4.3 Qualifiers NOT in Cipher (Metadata — Excluded)

| PID | Label | Why Excluded |
|-----|-------|-------------|
| P1480 | sourcing circumstances | Provenance metadata |
| P459 | determination method | How we know, not what we know |
| P3831 | object has role | Contextual role, may change |
| P1810 | subject named as | Language-dependent string |
| P2241 | reason for deprecated rank | Wikidata lifecycle |
| P1932 | object stated as | Language-dependent string |

### 4.4 Usage in Tier 3 Claim Cipher

```python
def build_claim_cipher_with_qualifiers(
    subject_qid: str,
    property_pid: str,
    object_qid: str,
    facet_id: str,
    qualifiers: dict,
    source_qid: str,
    passage_locator: str
) -> str:
    """
    Build claim cipher including cipher-eligible qualifiers.

    Only qualifiers in CIPHER_ELIGIBLE_QUALIFIERS are included.
    All others are stored as mutable metadata on the claim node.
    """
    CIPHER_ELIGIBLE_QUALIFIERS = {"P580", "P582", "P585", "P276", "P1545"}

    # Extract and normalize eligible qualifiers
    eligible = {}
    for pid, value in qualifiers.items():
        if pid in CIPHER_ELIGIBLE_QUALIFIERS:
            eligible[pid] = normalize_qualifier_value(pid, value)

    # Sort by PID for deterministic ordering
    qualifier_string = "|".join(
        f"{pid}:{eligible[pid]}" 
        for pid in sorted(eligible.keys())
    )

    # Build cipher input
    data = (
        f"{subject_qid}|"
        f"{property_pid}|"
        f"{object_qid}|"
        f"{facet_id.upper()}|"
        f"{qualifier_string}|"
        f"{source_qid}|"
        f"{passage_locator}"
    )

    hash_value = hashlib.sha256(data.encode()).hexdigest()
    facet_prefix = FACET_PREFIXES[facet_id.upper()]

    return f"fclaim_{facet_prefix}_{hash_value[:16]}"


def normalize_qualifier_value(pid: str, value) -> str:
    """Normalize qualifier values to canonical form before hashing."""
    if pid in ("P580", "P582", "P585"):
        # Temporal: ISO 8601 with 5-digit zero-padded year
        if isinstance(value, int):
            return f"{value:+06d}"
        return str(value)  # Already ISO formatted

    elif pid == "P276":
        # Location: use QID
        if isinstance(value, str) and value.startswith("Q"):
            return value
        return str(value)

    elif pid == "P1545":
        # Series ordinal: zero-padded integer
        return f"{int(value):03d}"

    return str(value)
```

### 4.5 Example: Distinguishing Caesar's Two Consulships

```python
# First consulship (59 BCE)
cipher_1 = build_claim_cipher_with_qualifiers(
    subject_qid="Q1048",          # Caesar
    property_pid="P39",           # position held
    object_qid="Q39686",          # consul
    facet_id="POLITICAL",
    qualifiers={
        "P580": -59,              # start time: 59 BCE
        "P582": -58,              # end time: 58 BCE
        "P1545": 1                # series ordinal: 1st
    },
    source_qid="Q47461",          # Polybius
    passage_locator="Hist.2.14"
)
# Result: "fclaim_pol_a1b2c3d4e5f6g7h8"

# Second consulship (48 BCE)
cipher_2 = build_claim_cipher_with_qualifiers(
    subject_qid="Q1048",          # Caesar (SAME)
    property_pid="P39",           # position held (SAME)
    object_qid="Q39686",          # consul (SAME)
    facet_id="POLITICAL",         # (SAME)
    qualifiers={
        "P580": -48,              # start time: 48 BCE (DIFFERENT!)
        "P582": -47,              # end time: 47 BCE (DIFFERENT!)
        "P1545": 2                # series ordinal: 2nd (DIFFERENT!)
    },
    source_qid="Q47461",
    passage_locator="Hist.5.32"
)
# Result: "fclaim_pol_x9y8z7w6v5u4t3s2" (DIFFERENT cipher!)

assert cipher_1 != cipher_2  # ✅ Two consulships = two distinct claims
```

---

## 5. QID-less Entity Resolution: Authority Cascade

### 5.1 The Problem

Not all entities have Wikidata QIDs. Obscure historical figures, provisional entities from LLM extraction, and domain-specific concepts may lack a QID. The cipher model requires a stable identifier regardless.

### 5.2 Authority Cascade (Priority Order)

```
┌─────────────────────────────────────────┐
│  Priority 1: Wikidata QID              │
│  ✅ Q1048 → namespace: "wd"            │
│  Most authoritative, globally unique    │
├─────────────────────────────────────────┤
│  Priority 2: BabelNet Synset           │
│  ✅ bn:14792761n → namespace: "bn"     │
│  Multilingual, 500+ languages           │
│  Maps back to QID when available        │
├─────────────────────────────────────────┤
│  Priority 3: Chrystallum Synthetic ID  │
│  ✅ crys:PERSON:a4f8c2d1 → ns: "crys" │
│  Deterministic hash of properties       │
│  Reconciliation hook for future QID     │
└─────────────────────────────────────────┘
```

### 5.3 Implementation

```python
import hashlib
import requests
from typing import Optional, Tuple

BABELNET_API_KEY = "YOUR_KEY"  # From environment variable
BABELNET_API_URL = "https://babelnet.io/v9/getSynsetIds"

def resolve_entity_id(
    canonical_name: str,
    entity_type: str,
    qid: Optional[str] = None,
    temporal: Optional[str] = None,
    search_lang: str = "EN"
) -> Tuple[str, str]:
    """
    Resolve entity to stable identifier using authority cascade.

    Returns:
        (resolved_id, namespace) tuple

    Cascade:
        1. Wikidata QID (if provided and valid)
        2. BabelNet synset (API lookup by lemma)
        3. Chrystallum synthetic (deterministic hash)
    """
    # Priority 1: Wikidata QID
    if qid and qid.startswith("Q") and qid[1:].isdigit():
        return (qid, "wd")

    # Priority 2: BabelNet lookup
    bn_id = _lookup_babelnet(canonical_name, search_lang)
    if bn_id:
        return (bn_id, "bn")

    # Priority 3: Chrystallum synthetic ID
    content = f"{entity_type.upper()}|{canonical_name.lower().strip()}|{temporal or '_NONE_'}"
    hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
    crys_id = f"crys:{entity_type.upper()}:{hash_val}"

    return (crys_id, "crys")


def _lookup_babelnet(lemma: str, lang: str = "EN") -> Optional[str]:
    """Query BabelNet API for synset ID."""
    try:
        response = requests.get(
            BABELNET_API_URL,
            params={
                "lemma": lemma,
                "searchLang": lang,
                "key": BABELNET_API_KEY
            },
            timeout=5
        )
        if response.status_code == 200:
            synsets = response.json()
            if synsets:
                return synsets[0]["id"]
    except Exception:
        pass
    return None
```

### 5.4 Reconciliation: When QID Becomes Available

When a QID is later discovered for a Chrystallum synthetic entity:

```cypher
// Step 1: Find the synthetic entity
MATCH (old:Entity {entity_cipher: "ent_per_crys:PERSON:a4f8c2d1"})

// Step 2: Create canonical entity with QID
MERGE (new:Entity {entity_cipher: "ent_per_Q999999"})
SET new.qid = "Q999999",
    new.namespace = "wd",
    new.entity_type = old.entity_type,
    new.label_en = old.label_en

// Step 3: Create SAME_AS bridge (preserves old cipher references)
CREATE (old)-[:SAME_AS {
  reconciled_at: datetime(),
  reconciled_by: "federation_mapper"
}]->(new)

// Step 4: Redirect all relationships to new entity
MATCH (old)-[r:HAS_FACETED_VIEW]->(fe:FacetedEntity)
CREATE (new)-[:HAS_FACETED_VIEW]->(fe)

// Step 5: Update faceted ciphers
MATCH (fe:FacetedEntity)
WHERE fe.entity_cipher = old.entity_cipher
SET fe.entity_cipher = new.entity_cipher,
    fe.faceted_cipher = replace(fe.faceted_cipher, "crys:PERSON:a4f8c2d1", "Q999999")

// Step 6: Archive old entity (keep for audit trail)
SET old:ArchivedEntity,
    old.superseded_by = new.entity_cipher,
    old.archived_at = datetime()
```

---

## 6. SCA Output Format (Updated)

### 6.1 Entity Output with Ciphers

Every entity produced by the SCA must include Tier 1 and Tier 2 ciphers:

```json
{
  "qid": "Q1048",
  "label": "Julius Caesar",
  "entity_type": "PERSON",
  "namespace": "wd",
  "entity_cipher": "ent_per_Q1048",
  "instance_of": [
    {"qid": "Q5", "label": "human"}
  ],
  "classification": {
    "primary_categories": ["PERSON"],
    "subjectConcept": false
  },
  "faceted_ciphers": {
    "ARCHAEOLOGICAL": "fent_arc_Q1048_Q17167",
    "ARTISTIC": "fent_art_Q1048_Q17167",
    "BIOGRAPHIC": "fent_bio_Q1048_Q17167",
    "COMMUNICATION": "fent_com_Q1048_Q17167",
    "CULTURAL": "fent_cul_Q1048_Q17167",
    "DEMOGRAPHIC": "fent_dem_Q1048_Q17167",
    "DIPLOMATIC": "fent_dip_Q1048_Q17167",
    "ECONOMIC": "fent_eco_Q1048_Q17167",
    "ENVIRONMENTAL": "fent_env_Q1048_Q17167",
    "GEOGRAPHIC": "fent_geo_Q1048_Q17167",
    "INTELLECTUAL": "fent_int_Q1048_Q17167",
    "LINGUISTIC": "fent_lin_Q1048_Q17167",
    "MILITARY": "fent_mil_Q1048_Q17167",
    "POLITICAL": "fent_pol_Q1048_Q17167",
    "RELIGIOUS": "fent_rel_Q1048_Q17167",
    "SCIENTIFIC": "fent_sci_Q1048_Q17167",
    "SOCIAL": "fent_soc_Q1048_Q17167",
    "TECHNOLOGICAL": "fent_tec_Q1048_Q17167"
  },
  "properties": {
    "P31": [{"qid": "Q5", "label": "human"}],
    "P569": [{"value": "-0100-07-12", "precision": "day"}],
    "P570": [{"value": "-0044-03-15", "precision": "day"}],
    "P27": [{"qid": "Q17167", "label": "Roman Republic"}]
  }
}
```

### 6.2 SubjectConcept Output with Ciphers

```json
{
  "qid": "Q17167",
  "label": "Roman Republic",
  "entity_type": "SUBJECTCONCEPT",
  "namespace": "wd",
  "entity_cipher": "ent_sub_Q17167",
  "classification": {
    "primary_categories": ["historicalTimePeriod", "subjectConcept"],
    "subjectConcept": true
  },
  "faceted_ciphers": {
    "ARCHAEOLOGICAL": "fent_arc_Q17167_Q17167",
    "ARTISTIC": "fent_art_Q17167_Q17167",
    "BIOGRAPHIC": "fent_bio_Q17167_Q17167",
    "COMMUNICATION": "fent_com_Q17167_Q17167",
    "CULTURAL": "fent_cul_Q17167_Q17167",
    "DEMOGRAPHIC": "fent_dem_Q17167_Q17167",
    "DIPLOMATIC": "fent_dip_Q17167_Q17167",
    "ECONOMIC": "fent_eco_Q17167_Q17167",
    "ENVIRONMENTAL": "fent_env_Q17167_Q17167",
    "GEOGRAPHIC": "fent_geo_Q17167_Q17167",
    "INTELLECTUAL": "fent_int_Q17167_Q17167",
    "LINGUISTIC": "fent_lin_Q17167_Q17167",
    "MILITARY": "fent_mil_Q17167_Q17167",
    "POLITICAL": "fent_pol_Q17167_Q17167",
    "RELIGIOUS": "fent_rel_Q17167_Q17167",
    "SCIENTIFIC": "fent_sci_Q17167_Q17167",
    "SOCIAL": "fent_soc_Q17167_Q17167",
    "TECHNOLOGICAL": "fent_tec_Q17167_Q17167"
  },
  "properties": { "..." : "..." }
}
```

---

## 7. Complete Neo4j Index Strategy

### 7.1 Tier 1 Indexes (Entity Lookups)

```cypher
// Primary entity cipher index
CREATE INDEX entity_cipher_idx IF NOT EXISTS
FOR (n:Entity) ON (n.entity_cipher);

// QID lookup (for Wikidata-anchored queries)
CREATE INDEX entity_qid_idx IF NOT EXISTS
FOR (n:Entity) ON (n.qid);

// Type-scoped lookup ("all Person entities")
CREATE INDEX entity_type_cipher_idx IF NOT EXISTS
FOR (n:Entity) ON (n.entity_type, n.entity_cipher);
```

### 7.2 Tier 2 Indexes (Faceted Lookups)

```cypher
// Primary faceted cipher index
CREATE INDEX faceted_cipher_idx IF NOT EXISTS
FOR (n:FacetedEntity) ON (n.faceted_cipher);

// Cross-facet jump index (entity + facet)
CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS
FOR (n:FacetedEntity) ON (n.entity_cipher, n.facet_id);

// SubjectConcept-scoped facet lookup
CREATE INDEX faceted_subj_facet_idx IF NOT EXISTS
FOR (n:FacetedEntity) ON (n.subjectconcept_id, n.facet_id);

// All facets for a SubjectConcept
CREATE INDEX faceted_subj_idx IF NOT EXISTS
FOR (n:FacetedEntity) ON (n.subjectconcept_id);
```

### 7.3 Tier 3 Indexes (Claim Lookups)

```cypher
// Primary claim cipher index (from CLAIM_ID_ARCHITECTURE.md)
CREATE INDEX claim_cipher_idx IF NOT EXISTS
FOR (c:FacetClaim) ON (c.cipher);

// Pattern matching: all claims for an entity
CREATE INDEX claim_entity_idx IF NOT EXISTS
FOR (c:FacetClaim) ON (c.subject_entity_cipher);

// Pattern matching: all claims for entity in a facet
CREATE INDEX claim_entity_facet_idx IF NOT EXISTS
FOR (c:FacetClaim) ON (c.subject_entity_cipher, c.facet_id);

// Pattern matching: all claims in a SubjectConcept
CREATE INDEX claim_subj_idx IF NOT EXISTS
FOR (c:FacetClaim) ON (c.subjectconcept_cipher);
```

---

## 8. Vertex Jump Patterns (Complete Reference)

### 8.1 Same Entity, Cross-Facet Jump

```cypher
// "Show me Caesar's MILITARY and POLITICAL claims"
WITH "ent_per_Q1048" AS caesar

MATCH (mil:FacetClaim {subject_entity_cipher: caesar, facet_id: "MILITARY"})
MATCH (pol:FacetClaim {subject_entity_cipher: caesar, facet_id: "POLITICAL"})
RETURN mil, pol
```

### 8.2 Same Entity, Cross-SubjectConcept Jump

```cypher
// "Caesar in Roman Republic context vs Gallic Wars context"
WITH "ent_per_Q1048" AS caesar

MATCH (rr:FacetedEntity {entity_cipher: caesar, subjectconcept_id: "Q17167"})
MATCH (gw:FacetedEntity {entity_cipher: caesar, subjectconcept_id: "Q190498"})
RETURN rr, gw
```

### 8.3 Same Facet, Cross-Entity Jump

```cypher
// "All POLITICAL actors in Roman Republic"
MATCH (pol:FacetedEntity {
  subjectconcept_id: "Q17167",
  facet_id: "POLITICAL"
})
RETURN pol.entity_cipher, pol.faceted_cipher
// Returns: Caesar, Pompey, Crassus, Cicero, etc.
```

### 8.4 Full Subgraph Retrieval

```cypher
// "Everything about Caesar in the Roman Republic"
WITH "ent_per_Q1048" AS caesar, "Q17167" AS rr

MATCH (e:Entity {entity_cipher: caesar})
OPTIONAL MATCH (e)-[:HAS_FACETED_VIEW]->(fe:FacetedEntity {subjectconcept_id: rr})
OPTIONAL MATCH (fe)-[:CONTAINS_CLAIM]->(c:FacetClaim)
RETURN e, fe, c
ORDER BY fe.facet_id, c.temporal_scope
```

### 8.5 Cipher-to-Cipher Navigation (Agent Pattern)

```python
def vertex_jump(
    entity_cipher: str,
    from_facet: str,
    to_facet: str,
    subjectconcept_id: str
) -> str:
    """
    Compute target faceted cipher for a vertex jump.
    No graph query needed — pure computation.
    """
    base_qid = entity_cipher.split("_")[-1]
    target_prefix = FACET_PREFIXES[to_facet.upper()]
    return f"fent_{target_prefix}_{base_qid}_{subjectconcept_id}"

# Example: Jump Caesar from MILITARY to POLITICAL
target = vertex_jump("ent_per_Q1048", "MILITARY", "POLITICAL", "Q17167")
# Returns: "fent_pol_Q1048_Q17167"
# Agent can now do: MATCH (n {faceted_cipher: target})
```

---

## 9. Python Implementation Module

### 9.1 Complete Cipher Generation Module

**File:** `scripts/tools/entity_cipher.py`

```python
"""
Entity Cipher Generation for Chrystallum Knowledge Graph.

Three-tier cipher model:
  Tier 1: Entity Cipher (cross-subgraph join key)
  Tier 2: Faceted Entity Cipher (subgraph address)
  Tier 3: Claim Cipher (see claim_ingestion_pipeline.py)

Usage:
  from scripts.tools.entity_cipher import (
      generate_entity_cipher,
      generate_faceted_cipher,
      generate_all_faceted_ciphers,
      resolve_entity_id,
      vertex_jump
  )
"""

import hashlib
import requests
from typing import Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────
# REGISTRIES (Locked Lists)
# ──────────────────────────────────────────────────────

ENTITY_TYPE_PREFIXES = {
    "PERSON": "per",
    "EVENT": "evt",
    "PLACE": "plc",
    "SUBJECTCONCEPT": "sub",
    "WORK": "wrk",
    "ORGANIZATION": "org",
    "PERIOD": "prd",
    "MATERIAL": "mat",
    "OBJECT": "obj",
}

FACET_PREFIXES = {
    "ARCHAEOLOGICAL": "arc", "ARTISTIC": "art", "BIOGRAPHIC": "bio",
    "COMMUNICATION": "com", "CULTURAL": "cul", "DEMOGRAPHIC": "dem",
    "DIPLOMATIC": "dip", "ECONOMIC": "eco", "ENVIRONMENTAL": "env",
    "GEOGRAPHIC": "geo", "INTELLECTUAL": "int", "LINGUISTIC": "lin",
    "MILITARY": "mil", "POLITICAL": "pol", "RELIGIOUS": "rel",
    "SCIENTIFIC": "sci", "SOCIAL": "soc", "TECHNOLOGICAL": "tec",
}

CANONICAL_FACETS = list(FACET_PREFIXES.keys())

CIPHER_ELIGIBLE_QUALIFIERS = {
    "P580",   # start time
    "P582",   # end time
    "P585",   # point in time
    "P276",   # location
    "P1545",  # series ordinal
}


# ──────────────────────────────────────────────────────
# TIER 1: ENTITY CIPHER
# ──────────────────────────────────────────────────────

def generate_entity_cipher(
    resolved_id: str,
    entity_type: str,
    namespace: str = "wd"
) -> str:
    """
    Generate Tier 1 entity cipher — cross-subgraph join key.

    Args:
        resolved_id: QID, BabelNet synset, or Chrystallum ID
        entity_type: Canonical type (PERSON, EVENT, PLACE, etc.)
        namespace: Authority source ("wd", "bn", "crys")

    Returns:
        Entity cipher string (e.g., "ent_per_Q1048")
    """
    entity_type_upper = entity_type.upper()
    if entity_type_upper not in ENTITY_TYPE_PREFIXES:
        raise ValueError(
            f"Unknown entity_type: {entity_type}. "
            f"Valid: {list(ENTITY_TYPE_PREFIXES.keys())}"
        )

    prefix = ENTITY_TYPE_PREFIXES[entity_type_upper]
    return f"ent_{prefix}_{resolved_id}"


# ──────────────────────────────────────────────────────
# TIER 2: FACETED ENTITY CIPHER
# ──────────────────────────────────────────────────────

def generate_faceted_cipher(
    entity_cipher: str,
    facet_id: str,
    subjectconcept_id: str
) -> str:
    """
    Generate Tier 2 faceted entity cipher — subgraph address.

    Args:
        entity_cipher: Tier 1 cipher (e.g., "ent_per_Q1048")
        facet_id: One of 18 canonical facets
        subjectconcept_id: QID of anchoring SubjectConcept

    Returns:
        Faceted cipher string (e.g., "fent_pol_Q1048_Q17167")
    """
    facet_upper = facet_id.upper()
    if facet_upper not in FACET_PREFIXES:
        raise ValueError(
            f"Unknown facet_id: {facet_id}. "
            f"Valid: {CANONICAL_FACETS}"
        )

    facet_prefix = FACET_PREFIXES[facet_upper]
    base_id = entity_cipher.split("_", 2)[-1]  # "ent_per_Q1048" → "Q1048"

    return f"fent_{facet_prefix}_{base_id}_{subjectconcept_id}"


def generate_all_faceted_ciphers(
    entity_cipher: str,
    subjectconcept_id: str
) -> Dict[str, str]:
    """
    Generate Tier 2 ciphers for all 18 canonical facets.

    Returns:
        Dict mapping facet_id → faceted_cipher
    """
    return {
        facet: generate_faceted_cipher(entity_cipher, facet, subjectconcept_id)
        for facet in CANONICAL_FACETS
    }


# ──────────────────────────────────────────────────────
# VERTEX JUMP (Pure Computation — No Graph Query)
# ──────────────────────────────────────────────────────

def vertex_jump(
    entity_cipher: str,
    from_facet: str,
    to_facet: str,
    subjectconcept_id: str
) -> str:
    """
    Compute target faceted cipher for a vertex jump.

    This is a pure computation — no database query required.
    The agent computes the target address, then does a single
    index seek to reach it.

    Args:
        entity_cipher: Tier 1 cipher of the entity
        from_facet: Source facet (for documentation, not used in computation)
        to_facet: Target facet
        subjectconcept_id: SubjectConcept context

    Returns:
        Target faceted cipher (Tier 2)
    """
    return generate_faceted_cipher(entity_cipher, to_facet, subjectconcept_id)


# ──────────────────────────────────────────────────────
# QID-LESS ENTITY RESOLUTION (Authority Cascade)
# ──────────────────────────────────────────────────────

BABELNET_API_URL = "https://babelnet.io/v9/getSynsetIds"

def resolve_entity_id(
    canonical_name: str,
    entity_type: str,
    qid: Optional[str] = None,
    temporal: Optional[str] = None,
    search_lang: str = "EN",
    babelnet_api_key: Optional[str] = None
) -> Tuple[str, str]:
    """
    Resolve entity to stable identifier via authority cascade.

    Cascade:
        1. Wikidata QID → ("Q1048", "wd")
        2. BabelNet synset → ("bn:14792761n", "bn")
        3. Chrystallum synthetic → ("crys:PERSON:a4f8c2d1", "crys")

    Returns:
        (resolved_id, namespace) tuple
    """
    # Priority 1: Wikidata QID
    if qid and qid.startswith("Q") and qid[1:].isdigit():
        return (qid, "wd")

    # Priority 2: BabelNet lookup
    if babelnet_api_key:
        bn_id = _lookup_babelnet(canonical_name, search_lang, babelnet_api_key)
        if bn_id:
            return (bn_id, "bn")

    # Priority 3: Chrystallum synthetic ID
    content = f"{entity_type.upper()}|{canonical_name.lower().strip()}|{temporal or '_NONE_'}"
    hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
    crys_id = f"crys:{entity_type.upper()}:{hash_val}"

    return (crys_id, "crys")


def _lookup_babelnet(
    lemma: str,
    lang: str,
    api_key: str
) -> Optional[str]:
    """Query BabelNet API for synset ID."""
    try:
        response = requests.get(
            BABELNET_API_URL,
            params={"lemma": lemma, "searchLang": lang, "key": api_key},
            timeout=5
        )
        if response.status_code == 200:
            synsets = response.json()
            if synsets:
                return synsets[0]["id"]
    except Exception:
        pass
    return None


# ──────────────────────────────────────────────────────
# SCA OUTPUT ENRICHMENT
# ──────────────────────────────────────────────────────

def enrich_entity_with_ciphers(
    entity_data: dict,
    subjectconcept_id: str,
    babelnet_api_key: Optional[str] = None
) -> dict:
    """
    Add Tier 1 and Tier 2 ciphers to SCA entity output.

    Modifies entity_data in-place and returns it.
    """
    qid = entity_data.get("qid")
    entity_type = entity_data.get("entity_type", "SUBJECTCONCEPT")
    canonical_name = entity_data.get("label", "")
    temporal = entity_data.get("temporal_scope")

    # Resolve ID via authority cascade
    resolved_id, namespace = resolve_entity_id(
        canonical_name=canonical_name,
        entity_type=entity_type,
        qid=qid,
        temporal=temporal,
        babelnet_api_key=babelnet_api_key
    )

    # Generate Tier 1 cipher
    entity_cipher = generate_entity_cipher(resolved_id, entity_type, namespace)
    entity_data["entity_cipher"] = entity_cipher
    entity_data["namespace"] = namespace

    # Generate Tier 2 faceted ciphers (all 18 facets)
    entity_data["faceted_ciphers"] = generate_all_faceted_ciphers(
        entity_cipher, subjectconcept_id
    )

    return entity_data
```

---

## 10. Testing & Validation

### 10.1 Test Suite

**File:** `tests/test_entity_cipher.py`

```python
import pytest
from scripts.tools.entity_cipher import (
    generate_entity_cipher,
    generate_faceted_cipher,
    generate_all_faceted_ciphers,
    vertex_jump,
    resolve_entity_id,
    CANONICAL_FACETS,
)


class TestTier1EntityCipher:

    def test_person_cipher(self):
        cipher = generate_entity_cipher("Q1048", "PERSON", "wd")
        assert cipher == "ent_per_Q1048"

    def test_event_cipher(self):
        cipher = generate_entity_cipher("Q25238182", "EVENT", "wd")
        assert cipher == "ent_evt_Q25238182"

    def test_subjectconcept_cipher(self):
        cipher = generate_entity_cipher("Q17167", "SUBJECTCONCEPT", "wd")
        assert cipher == "ent_sub_Q17167"

    def test_babelnet_entity(self):
        cipher = generate_entity_cipher("bn:14792761n", "PERSON", "bn")
        assert cipher == "ent_per_bn:14792761n"

    def test_chrystallum_synthetic(self):
        cipher = generate_entity_cipher("crys:PERSON:a4f8c2d1", "PERSON", "crys")
        assert cipher == "ent_per_crys:PERSON:a4f8c2d1"

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError):
            generate_entity_cipher("Q1048", "INVALID_TYPE")

    def test_deterministic(self):
        c1 = generate_entity_cipher("Q1048", "PERSON")
        c2 = generate_entity_cipher("Q1048", "PERSON")
        assert c1 == c2


class TestTier2FacetedCipher:

    def test_political_facet(self):
        cipher = generate_faceted_cipher("ent_per_Q1048", "POLITICAL", "Q17167")
        assert cipher == "fent_pol_Q1048_Q17167"

    def test_military_facet(self):
        cipher = generate_faceted_cipher("ent_per_Q1048", "MILITARY", "Q17167")
        assert cipher == "fent_mil_Q1048_Q17167"

    def test_different_facets_different_ciphers(self):
        pol = generate_faceted_cipher("ent_per_Q1048", "POLITICAL", "Q17167")
        mil = generate_faceted_cipher("ent_per_Q1048", "MILITARY", "Q17167")
        assert pol != mil

    def test_different_subjectconcepts_different_ciphers(self):
        rr = generate_faceted_cipher("ent_per_Q1048", "POLITICAL", "Q17167")
        gw = generate_faceted_cipher("ent_per_Q1048", "POLITICAL", "Q190498")
        assert rr != gw

    def test_all_18_facets(self):
        ciphers = generate_all_faceted_ciphers("ent_per_Q1048", "Q17167")
        assert len(ciphers) == 18
        assert set(ciphers.keys()) == set(CANONICAL_FACETS)
        assert len(set(ciphers.values())) == 18  # All unique

    def test_invalid_facet_raises(self):
        with pytest.raises(ValueError):
            generate_faceted_cipher("ent_per_Q1048", "TEMPORAL", "Q17167")


class TestVertexJump:

    def test_jump_military_to_political(self):
        target = vertex_jump("ent_per_Q1048", "MILITARY", "POLITICAL", "Q17167")
        assert target == "fent_pol_Q1048_Q17167"

    def test_jump_is_pure_computation(self):
        # Same result regardless of call order
        t1 = vertex_jump("ent_per_Q1048", "MILITARY", "POLITICAL", "Q17167")
        t2 = vertex_jump("ent_per_Q1048", "ECONOMIC", "POLITICAL", "Q17167")
        assert t1 == t2  # from_facet doesn't affect target

    def test_jump_cross_subjectconcept(self):
        rr = vertex_jump("ent_per_Q1048", "MILITARY", "MILITARY", "Q17167")
        gw = vertex_jump("ent_per_Q1048", "MILITARY", "MILITARY", "Q190498")
        assert rr != gw


class TestAuthorityCascade:

    def test_qid_priority(self):
        resolved_id, ns = resolve_entity_id("Julius Caesar", "PERSON", qid="Q1048")
        assert resolved_id == "Q1048"
        assert ns == "wd"

    def test_synthetic_fallback(self):
        resolved_id, ns = resolve_entity_id(
            "Obscure Roman Centurion",
            "PERSON",
            temporal="-0100"
        )
        assert ns == "crys"
        assert resolved_id.startswith("crys:PERSON:")

    def test_synthetic_deterministic(self):
        id1, _ = resolve_entity_id("Lucius Merula", "PERSON", temporal="-0087")
        id2, _ = resolve_entity_id("Lucius Merula", "PERSON", temporal="-0087")
        assert id1 == id2

    def test_synthetic_name_normalization(self):
        id1, _ = resolve_entity_id("Lucius Merula", "PERSON")
        id2, _ = resolve_entity_id("lucius merula", "PERSON")
        id3, _ = resolve_entity_id("  Lucius Merula  ", "PERSON")
        assert id1 == id2 == id3  # Case/whitespace normalized
```

### 10.2 Validation Script (300-Entity Test)

```python
def validate_cipher_suite(entities: list) -> dict:
    """
    Run against 300-entity test set to validate:
    - Zero Tier 1 collisions
    - 18x Tier 2 ciphers per entity, all unique
    - Authority cascade coverage metrics
    """
    tier1_ciphers = set()
    tier2_ciphers = set()
    ns_counts = {"wd": 0, "bn": 0, "crys": 0}

    for entity in entities:
        ec = entity["entity_cipher"]
        ns = entity["namespace"]

        # Check Tier 1 uniqueness
        assert ec not in tier1_ciphers, f"Tier 1 collision: {ec}"
        tier1_ciphers.add(ec)
        ns_counts[ns] += 1

        # Check Tier 2 uniqueness
        for facet, fc in entity["faceted_ciphers"].items():
            assert fc not in tier2_ciphers, f"Tier 2 collision: {fc}"
            tier2_ciphers.add(fc)

    total = len(entities)
    return {
        "total_entities": total,
        "unique_tier1": len(tier1_ciphers),
        "unique_tier2": len(tier2_ciphers),
        "expected_tier2": total * 18,
        "tier1_collisions": total - len(tier1_ciphers),
        "tier2_collisions": (total * 18) - len(tier2_ciphers),
        "qid_coverage": f"{ns_counts['wd']/total:.1%}",
        "bn_coverage": f"{ns_counts['bn']/total:.1%}",
        "crys_synthetic": f"{ns_counts['crys']/total:.1%}",
    }
```

---

## 11. Migration from Current SCA Output

### 11.1 Files to Modify

| File | Change |
|------|--------|
| `scripts/sca_clean_labels.py` | Add `enrich_entity_with_ciphers()` call to output pipeline |
| `scripts/sca_enhanced_with_details.py` | Same — add cipher enrichment after entity classification |
| `scripts/federation_mapper.py` | Add `resolve_entity_id()` for BabelNet cascade |
| Neo4j schema | Create indexes from §7 |
| SCA agent prompt | Add instruction: "Include entity_cipher and faceted_ciphers in output" |

### 11.2 Backward Compatibility

Existing entities without ciphers can be backfilled:

```cypher
// Backfill Tier 1 ciphers for existing entities
MATCH (n:Entity)
WHERE n.entity_cipher IS NULL AND n.qid IS NOT NULL
SET n.entity_cipher = "ent_" + 
  CASE n.entity_type
    WHEN "PERSON" THEN "per"
    WHEN "EVENT" THEN "evt"
    WHEN "PLACE" THEN "plc"
    WHEN "SUBJECTCONCEPT" THEN "sub"
    WHEN "WORK" THEN "wrk"
    WHEN "ORGANIZATION" THEN "org"
    WHEN "PERIOD" THEN "prd"
    ELSE "ent"
  END + "_" + n.qid
RETURN count(n) AS backfilled
```

---

## 12. Architecture Decision Record

**ADR-001: Three-Tier Entity Cipher Model**

**Status:** Accepted (February 21, 2026)

**Context:**
Chrystallum requires efficient cross-subgraph navigation across 18 facets, multiple SubjectConcepts, and millions of claims. Pattern-matching traversal does not scale.

**Decision:**
Adopt a three-tier cipher model:
- Tier 1: Entity Cipher (cross-subgraph join key)
- Tier 2: Faceted Entity Cipher (subgraph address, materialized as hub nodes)
- Tier 3: Claim Cipher (assertion identity, per CLAIM_ID_ARCHITECTURE.md)

Use Option B qualifier depth (5 cipher-eligible qualifiers).
Use BabelNet authority cascade for QID-less entities.

**Consequences:**
- All SCA output must include entity_cipher and faceted_ciphers
- Neo4j indexes must be created before bulk import
- BabelNet API key required for federation_mapper.py
- Reconciliation workflow needed when synthetic entities gain QIDs

---

## 13. References

### 13.1 Internal Documents
- **CLAIM_ID_ARCHITECTURE.md** — Tier 3 Claim Cipher specification
- **ADR_001_Claim_Identity_Ciphers.md** — Architecture Decision Record for claim ciphers
- **ARCHITECTURE_ONTOLOGY.md** — Entity, Subject, and Relationship layers
- **ARCHITECTURE_CORE.md** — System overview and principles

### 13.2 External Standards
- [Wikidata Statement Model](https://www.wikidata.org/wiki/Help:Statements) — QIDs, PIDs, qualifiers
- [Wikidata Ranking](https://www.wikidata.org/wiki/Help:Ranking) — Preferred/normal/deprecated
- [BabelNet API](https://babelnet.org/guide) — Multilingual synset resolution
- [Neo4j Composite Indexes](https://neo4j.com/docs/cypher-manual/current/indexes/) — Index seek optimization

### 13.3 Revision History

| Date | Version | Changes |
|------|---------|---------|
| **Feb 21, 2026** | **1.0** | **Initial specification: Three-tier cipher model, Option B qualifiers, BabelNet cascade, Neo4j index strategy, vertex jump patterns** |

---

**Document Status:** ✅ Canonical Reference (Feb 2026)  
**Maintainers:** Chrystallum Architecture Team  
**Last Updated:** February 21, 2026
