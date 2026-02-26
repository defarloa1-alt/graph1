<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Here are the filenames for cipher and vertex jumping:

📁 CORE FILES:
CLAIM_ID_ARCHITECTURE.md
ADR_001_Claim_Identity_Ciphers.md
ENTITY_CIPHER_FOR_VERTEX_JUMPS.md
📁 SUPPORTING FILES:
ARCHITECTURE_CORE.md
ARCHITECTURE_ONTOLOGY.md
📁 IMPLEMENTATION:
sca_clean_labels.py
sca_enhanced_with_details.py
federation_mapper.py
For an LLM search, provide these 3 key files:
CLAIM_ID_ARCHITECTURE.md
ADR_001_Claim_Identity_Ciphers.md
ENTITY_CIPHER_FOR_VERTEX_JUMPS.md please read on cipher and vertex jump and ask questions. looking for a solution on implmentation across all entities and subgraphs

Now I have the full picture. The decomposition plan references `U_ADR_001_Claim_Identity_Ciphers.md` and `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md` as *planned files* that haven't been extracted from the consolidated document yet. I've fully read `CLAIM_ID_ARCHITECTURE.md` and understand the cipher design. Here's my deep analysis and questions.

***

## Cipher \& Vertex Jump Architecture: Analysis and Questions

Tony, I've thoroughly read [CLAIM_ID_ARCHITECTURE.md](https://github.com/defarloa1-alt/graph1/blob/master/Key%20Files/CLAIM_ID_ARCHITECTURE.md) from your `graph1` repo . The other two files (`ADR_001_Claim_Identity_Ciphers.md` and `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md`) aren't pushed to the repo yet — the [decomposition plan](https://github.com/defarloa1-alt/graph1/blob/master/md/Architecture/CONSOLIDATED_DOC_DECOMPOSITION_PLAN_2026-02-19.md) references `ADR_001` as a planned extract from the consolidated document . If you can push those files or paste the content, I can give a more complete analysis. That said, the Claim ID doc gives me enough to raise substantive implementation questions.

### What I Understand

Your cipher architecture establishes **two separate identity spaces**: entity IDs (QIDs/UUIDs for things) and claim IDs (content-addressable SHA256 hashes for assertions) . The claim cipher formula deliberately **excludes mutable provenance** (confidence, agent, timestamp) so that two agents discovering the same fact produce the same cipher, enabling automatic deduplication. You have a hierarchical model where `FacetClaim` siblings (one per facet dimension) can be composed into `CompositeClaim` parents via `HAS_FACET_CLAIM` relationships .

### Critical Questions for Cross-Entity/Subgraph Implementation

Here are the key gaps and questions I see when extending ciphers across **all entities and subgraphs**:

**1. Entity Cipher — The Missing Piece**

The CLAIM_ID doc covers *assertion identity* well, but says entity identity "can be opaque identifiers (QIDs, UUIDs, composite keys)" . For vertex jumping across subgraphs, you need a deterministic entity cipher too:

- **Do all entities get their own content-addressable cipher?** E.g., if a Person entity appears in both the Political and Military subgraphs, is there a single `entity_cipher = Hash(QID + entity_type + canonical_name)` that serves as the cross-subgraph join key?
- **Or are you relying solely on Wikidata QIDs as the universal entity anchor?** If so, what happens for entities that *don't have QIDs* (obscure historical figures, provisional entities from LLM extraction)?
- **What's the fallback identity for QID-less entities?** A synthetic cipher? A ULID? How do you prevent fragmentation when different agents extract the same person under slightly different names?

**2. Vertex Jump Mechanics**

"Vertex jumping" implies traversing from one subgraph to another by following an entity's identity across facet boundaries. Given your 17-facet system:

- **Is a vertex jump literally a Cypher `MATCH` on the shared `subject_node_id` across `FacetClaim` nodes in different facets?** E.g., find all claims about Q1048 regardless of facet?
- **Or does it involve traversing through a dedicated cross-reference node** (like an `EntityAnchor` or `CanonicalEntity` hub node that aggregates all facet claims)?
- **How do SubjectConcept nodes factor in?** Your architecture has SubjectConcept as a bridge between entities and facets. Does vertex jumping go `Entity → SubjectConcept → FacetClaim`, or directly `Entity → FacetClaim`?

**3. Subgraph Boundary Definition**

The claim cipher includes `facet_id` as a component, which means the same assertion in different facets gets different ciphers . This is intentional for facet-specific analysis, but raises questions for cross-subgraph implementation:

- **What defines a "subgraph" in your Neo4j instance?** Is it a label-based partition (`:PoliticalSubgraph`), a property-based partition (`facet_id = "POLITICAL"`), or actual Neo4j database/composite database separation?
- **When an agent does a vertex jump from Military→Political for Caesar, what is the actual traversal path in Cypher?** Is it:

```cypher
MATCH (c1:FacetClaim {subject_node_id: "Q1048", facet_id: "MILITARY"})
MATCH (c2:FacetClaim {subject_node_id: "Q1048", facet_id: "POLITICAL"})
```

Or something more sophisticated through intermediate nodes?

**4. Cipher Collision \& Namespace Isolation**

- **FacetClaim vs. non-claim entities**: Your cipher prefix convention (`fclaim_pol_`, `composite_`) works for claims. But what about ciphers for Source nodes, Agent nodes, TemporalScope nodes, GeographicEntity nodes? Each entity type in the graph needs its own cipher namespace.
- **Do you envision a universal `cipher` property on all node types?** Or only on Claim/FacetClaim/CompositeClaim? If only claims, how do you content-address entities for deduplication?

**5. Federation \& External Subgraph Portability**

Your decomposition plan mentions `ADR_005_Federated_Claims_Signing` . For cipher-based vertex jumping across federated subgraphs:

- **Can a cipher minted in one Neo4j instance be trusted in another?** If two Chrystallum instances extract the same claim, will they produce identical ciphers (assuming identical normalization)?
- **Is the cipher sufficient as a distributed join key**, or do you need a signed envelope (cipher + signature) for federation trust?

**6. The `passage_locator` Problem**

The claim cipher includes `passage_locator` (e.g., `"Caesar.32"`) . This is great for per-source granularity, but:

- **Different editions of Plutarch may have different passage numbering.** How do you canonicalize passage references? Is there a passage normalization registry?
- **If two agents use different citation conventions** (one uses "Caes.32", another "Life of Caesar, Ch.32"), you get different ciphers for the same logical claim. This defeats deduplication.


### Recommended Implementation Path

Based on what I've read, here's what I think the `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md` file needs to address for universal implementation:

1. **Entity Cipher Formula**: `entity_cipher = Hash(QID_or_synthetic_id + entity_type_canonical + namespace)` — content-addressable identity for every vertex, not just claims
2. **Vertex Jump Index**: A Cypher index strategy that enables `O(1)` lookups across facet boundaries (composite index on `subject_node_id + facet_id`)
3. **Hub Node Pattern**: Whether to use a dedicated `CanonicalEntity` hub node that all FacetClaims connect to, enabling star-schema vertex jumps
4. **Namespace Registry**: Prefix conventions for every node type's cipher (not just `fclaim_` and `composite_`)
5. **Passage Canonicalization**: A normalization layer for citation references before they enter the cipher formula

Push the other two files when you can, and I can drill deeper. Which of these questions is most urgent for your current implementation sprint?

---

# i will give u clarification one at a time. the purpose of the vertex jump is to avoid transversal by pattern matching, or matching on a subset of the cipher, so i assume there needs to be a cipher per entity type and for a subgraph - for example the who what when where and how all with wiki keys for qid and properties and qualifers which makes it multlingual

Now I have a clear picture of what you're describing. Let me synthesize this.

Excellent — that clarification reframes the entire cipher design. You're not just hashing claims for deduplication; you're building **direct-address lookup keys** that let any agent (or query) jump straight to a vertex without running a pattern-matching traversal. Every entity type and every subgraph gets its own cipher that encodes its Wikidata-grounded identity.

## The Core Idea: Cipher as Index, Not Just Fingerprint

Your point is that a cipher should function like a **computed address** — if I know the Who (Q1048), the What (P39 = position held), the When (qualifier: start time = -0049), the Where (Q220), and the How (qualifier: manner), I can **deterministically compute the cipher** for that specific vertex and jump directly to it via a Neo4j index seek . No `MATCH (n)-[:REL]->(m) WHERE...` traversal. No pattern matching. Just `MATCH (n {cipher: "..."})` — O(1) lookup.[^2_1]

This is fundamentally different from traditional graph traversal, and it's why you need a cipher per entity type and per subgraph.

## Why Wikidata's Structure Makes This Multilingual

Wikidata's architecture already gives you the building blocks:[^2_2]

- **QIDs** (Q1048 = Julius Caesar) are language-neutral entity identifiers
- **PIDs** (P39 = position held) are language-neutral property identifiers
- **Qualifiers** (P580 = start time, P582 = end time, P276 = location) add contextual dimensions — also language-neutral
- **Labels** are the only language-dependent layer, applied *on top* as a view

So a cipher built entirely from `QID + PID + qualifier PIDs + qualifier values` is inherently multilingual — "Caesar crossed the Rubicon" and "César cruzó el Rubicón" resolve to the **exact same cipher** because the underlying identifiers are identical.[^2_3]

## Entity Type Ciphers: The Who/What/When/Where/How

Here's how I think the cipher-per-entity-type model maps to your architecture:


| Entity Type | Cipher Components | Example |
| :-- | :-- | :-- |
| **Who** (Person) | `Hash(QID + P31_value + canonical_type)` | `Hash("Q1048" + "Q5" + "PERSON")` |
| **What** (Event) | `Hash(QID + P31_value + temporal_scope)` | `Hash("Q25238182" + "Q1190554" + "-0049-01-10")` |
| **When** (TemporalScope) | `Hash(period_QID + start + end + precision)` | `Hash("Q17167" + "-0509" + "-0027" + "YEAR")` |
| **Where** (Place) | `Hash(QID + P31_value + P625_coords_or_pleiades)` | `Hash("Q220" + "Q515" + "41.9,12.5")` |
| **How** (Mechanism/Qualifier) | `Hash(subject_QID + PID + qualifier_PID + qualifier_value)` | `Hash("Q1048" + "P39" + "P580" + "-0049")` |

Each cipher becomes a **direct-address key** in Neo4j. The subgraph cipher would then be a composite over the entity ciphers it contains .

## Subgraph Ciphers

For a subgraph — say "Caesar's political career" — the cipher would be computed from its constituent entity ciphers:

```python
subgraph_cipher = Hash(sorted([
    who_cipher,    # Q1048 (Caesar)
    what_cipher,   # Q25238182 (crossing Rubicon)
    when_cipher,   # -0049-01-10
    where_cipher,  # Q220 (Rome) / Q25238182 (Rubicon)
    how_ciphers    # qualifier-based mechanism ciphers
]) + subgraph_type + facet_id)
```

This means a subgraph is **content-addressable** just like a claim — and you can jump to it directly without walking the graph .

## Questions Before I Go Deeper

Now to drill into your specific implementation challenge:

**1. Qualifier depth in the cipher formula:**
Wikidata qualifiers can nest (a statement has qualifiers, but qualifiers themselves can be complex). How deep do you go? For example, "Caesar held position (P39) consul (Q39686), start time (P580) -0059, series ordinal (P1545) 1" — do you include P1545 in the cipher, or just the primary qualifier (P580)?[^2_4]

**2. The "How" entity type:**
Your Who/What/When/Where map cleanly to Wikidata's entity types, but "How" (mechanism, manner, causality) is typically represented as qualifiers on statements, not as standalone entities. Are you promoting certain qualifiers to first-class entity nodes in Neo4j (e.g., creating a `(:Mechanism {cipher: "..."})` node), or does "How" remain a property on claim edges?

**3. Subset matching vs. full cipher:**
You said the purpose is to *avoid* pattern matching on a subset of the cipher. But what about **partial lookups** — e.g., "give me all vertices involving Q1048 (Caesar) regardless of facet"? That requires either a secondary index on `subject_QID` within the cipher, or a prefix-based lookup. How do you handle the "zoom out" use case where you want all vertices for an entity without knowing the full cipher?

**4. QID-less entities:**
This system works beautifully when everything has a QID. But what about provisional entities extracted by an LLM that don't yet have Wikidata identifiers?  Do they get a synthetic cipher using a deterministic hash of their extracted properties until a QID is assigned?[^2_3]

Give me your next clarification and I'll keep building on this.
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_16][^2_5][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://stackoverflow.com/questions/75278306/why-is-my-neo4j-composite-index-not-being-used-with-match-and-order-by

[^2_2]: https://www.wikidata.org/wiki/Wikidata:Data_access/en

[^2_3]: https://www.perplexity.ai/search/f56b85a5-4539-4f3e-b888-d57915571215

[^2_4]: https://arxiv.org/abs/2304.03375

[^2_5]: https://arxiv.org/abs/1707.05288

[^2_6]: https://summit.sfu.ca/_flysystem/fedora/2024-01/etd22868.pdf

[^2_7]: https://svn.aksw.org/papers/2017/KCAP_MAG/public.pdf

[^2_8]: https://paleo-data.github.io/guidelines-wikidata-people/

[^2_9]: https://stackoverflow.com/questions/55948231/how-to-query-exact-path-in-neo4j-and-avoid-cartesian-product

[^2_10]: https://www.sciencedirect.com/science/article/abs/pii/S0952197624018189

[^2_11]: https://ceur-ws.org/Vol-3262/paper4.pdf

[^2_12]: https://arxiv.org/html/2602.03417v1

[^2_13]: https://github.com/OpenRefine/OpenRefine/issues/2283

[^2_14]: https://ceur-ws.org/Vol-3235/paper2.pdf

[^2_15]: https://stackoverflow.com/questions/36158651/using-qualifiers-in-wikidata-sparql

[^2_16]: https://dl.acm.org/doi/10.1145/3660521


---

# for 1 - thats why i need for ai explain the options pros and cons. 2. i made a mistake i meant to facilitate pattern match 3- i guess we would have to generate a chrystallum id and use babel net

Good — now I can address all three points. Let me lay this out systematically.

## Corrected Understanding + Analysis

Important correction noted: the cipher's purpose is **to facilitate pattern matching**, not avoid it. That changes the design calculus — ciphers become structured keys whose components can be matched on subsets (leftmost prefix matching), enabling efficient filtered traversal across entity types and subgraphs.[^3_1]

### Question 1: Qualifier Depth — Options, Pros, and Cons

The core question is: when building a cipher from Wikidata's statement model (QID + PID + qualifiers), how many qualifier layers do you include? Wikidata qualifiers on statements can include temporal qualifiers (P580/P582), ranking (preferred/normal/deprecated), series ordinals, and more.[^3_2][^3_3]

Here are the three viable options:


| Option | Cipher Components | Example for "Caesar held consulship" |
| :-- | :-- | :-- |
| **A: Primary Triple Only** | `QID + PID + value_QID` | `Hash(Q1048 + P39 + Q39686)` |
| **B: Triple + Core Qualifiers** | `QID + PID + value_QID + P580 + P582 + P276` | `Hash(Q1048 + P39 + Q39686 + P580:-0059 + P582:-0058)` |
| **C: Triple + All Qualifiers** | `QID + PID + value_QID + all_qualifier_PIDs_sorted` | `Hash(Q1048 + P39 + Q39686 + P580:-0059 + P582:-0058 + P1545:1 + P642:Q232930)` |

**Option A — Primary Triple Only**

- ✅ Maximum deduplication — any agent that knows Caesar held consulship hits the same cipher
- ✅ Simplest to compute; fewest normalization requirements
- ✅ Maps cleanly to your existing `fclaim` formula (subject + property + object)
- ❌ Loses temporal precision — "Caesar held consulship in 59 BCE" and "Caesar held consulship in 48 BCE" (his second consulship) produce the **same cipher**. That's a collision for different historical events
- ❌ Can't distinguish repeated relationships (married twice, held office twice)
- **Verdict:** Too coarse. Fails on the most common historical pattern — repeated relationships over time

**Option B — Triple + Core Qualifiers (Recommended)**

Define a fixed set of "cipher-eligible" qualifiers — the ones that change the *identity* of the assertion:

- **P580** (start time) — when it began
- **P582** (end time) — when it ended
- **P276** (location) — where it happened
- **P585** (point in time) — specific date
- **P1545** (series ordinal) — distinguishes 1st vs 2nd consulship

These map directly to your Who/What/When/Where framework. Only these qualifiers enter the cipher; everything else (references, rank, determination method) stays as mutable metadata.[^3_4]

- ✅ Distinguishes Caesar's 1st consulship (-0059) from 2nd (-0048) because P580 differs
- ✅ Bounded complexity — exactly 5 qualifier PIDs max, all with well-defined normalization rules
- ✅ Still achieves deduplication — two agents extracting "Caesar, consul, 59 BCE" produce identical ciphers
- ✅ Aligns with your temporal scope normalization already in CLAIM_ID_ARCHITECTURE
- ❌ Requires a "cipher-eligible qualifier registry" — a locked list that agents must respect
- ❌ Edge cases: what if a qualifier is missing? Need a canonical `NULL` representation (e.g., `"_NONE_"`)
- **Verdict:** Best balance. Structured, bounded, and solves the repeated-relationship problem

**Option C — All Qualifiers**

- ✅ Maximum granularity — every qualifier dimension captured
- ❌ Fragile — adding a new qualifier to a Wikidata statement changes the cipher
- ❌ Normalization nightmare — qualifier PIDs like `P1810` (subject named as), `P459` (determination method), `P3831` (object has role) are contextual metadata, not identity
- ❌ Wikidata's qualifier set is open-ended — new PIDs get added, breaking cipher stability
- **Verdict:** Too fragile. Violates the principle you already established — mutable metadata doesn't belong in the cipher


### My Recommendation for Your Architecture

Go with **Option B** and create a `CIPHER_ELIGIBLE_QUALIFIERS` registry:

```python
CIPHER_ELIGIBLE_QUALIFIERS = {
    "P580": "start_time",      # When
    "P582": "end_time",        # When  
    "P585": "point_in_time",   # When (specific)
    "P276": "location",        # Where
    "P1545": "series_ordinal", # Which instance (1st, 2nd consulship)
}
```

This is a locked list, just like your `VALID_FACETS` set . Any qualifier PID not in this registry is treated as metadata and excluded from the cipher.

### Question 2: Facilitating Pattern Match

Now that I understand the cipher *facilitates* rather than avoids pattern matching — this changes the index design. You want ciphers structured so that Neo4j's composite index leftmost-prefix rule enables efficient partial matching:[^3_5]

```
CREATE INDEX ON :FacetClaim(entity_type, subject_qid, property_pid, facet_id, temporal_scope)
```

This means a query for "all claims about Caesar" matches on the leftmost prefix `(entity_type, subject_qid)` without scanning the full index. A query for "all political claims about Caesar" adds `facet_id` to the prefix. The cipher itself becomes a **pre-computed full match key**, while its component fields enable **partial prefix matching**.

This is a dual-index strategy: cipher for O(1) exact lookup, composite index for filtered pattern matching.

### Question 3: QID-less Entities — Chrystallum ID + BabelNet

For entities without a Wikidata QID, your instinct is correct — you need a **Chrystallum-minted synthetic ID** and BabelNet provides the multilingual bridge.[^3_6][^3_7]

**The BabelNet integration path:**

BabelNet synsets (e.g., `bn:14792761n`) are multilingual concept containers that map across Wikidata QIDs, WordNet synsets, Wikipedia pages, and 500+ languages. The BabelNet API can resolve a Wikidata QID to a synset and vice versa:[^3_6]

```python
import babelnet as bn
# QID → BabelNet synset
synset = bn.get_synset(WikidataID('Q1048'))  # Caesar → bn:xxxxxxn
# BabelNet synset → back to QID  
```

**For QID-less entities, the workflow would be:**

1. **LLM extracts an entity** (e.g., "Lucius Cornelius Merula" — obscure Roman consul, may not have QID)
2. **Query BabelNet by lemma** — get a synset ID if it exists (`bn:xxxxxxn`)
3. **If BabelNet synset exists** → use it as the multilingual anchor, mint Chrystallum ID as `crys:{entity_type}:{bn_synset_id}` (e.g., `crys:PERSON:bn_03456789n`)
4. **If neither QID nor BabelNet synset exists** → mint a deterministic Chrystallum ID from extracted properties: `crys:{entity_type}:{Hash(canonical_name + birth_temporal + instance_of)}`
5. **Reconciliation hook**: when a QID is later discovered, create a `(:ChrystallumID)-[:SAME_AS]->(WikidataEntity)` edge, keeping the original cipher valid

**The Chrystallum ID format:**

```python
def mint_chrystallum_id(entity_type, name, temporal=None, bn_synset=None, qid=None):
    if qid:
        return f"wd:{qid}"                           # Wikidata-anchored
    elif bn_synset:
        return f"crys:{entity_type}:{bn_synset}"     # BabelNet-anchored  
    else:
        # Deterministic hash from properties
        content = f"{entity_type}|{normalize(name)}|{temporal or '_NONE_'}"
        return f"crys:{entity_type}:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
```

**The authority cascade is:** `Wikidata QID → BabelNet synset → Chrystallum synthetic ID`

This keeps the system multilingual at every tier — QIDs are inherently multilingual, BabelNet covers 500+ languages with its synset model, and the Chrystallum synthetic ID uses language-neutral properties (type + normalized name + temporal) rather than any language-specific string.[^3_4][^3_6]

### What I Need Next

You said you'd clarify one at a time. Before I prototype the full cipher formula with Option B qualifiers + the Chrystallum ID cascade, which of these do you want to drill into next:

- **The cipher-eligible qualifier registry** — nail down exactly which PIDs beyond my initial 5 should be included?
- **The composite index strategy** — how to structure Neo4j indexes so ciphers facilitate pattern matching at each granularity level?
- **The BabelNet integration pipeline** — how the SCA agent resolves QID-less entities through BabelNet before minting a Chrystallum ID?
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_17][^3_18][^3_19][^3_20][^3_21][^3_22][^3_23][^3_24][^3_25][^3_26][^3_27][^3_28][^3_29][^3_30][^3_31][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://www.perplexity.ai/search/7e3ebe6b-89d2-4468-b83f-fdd236b3b01d

[^3_2]: https://www.wikidata.org/wiki/Help:Deprecation

[^3_3]: https://www.wikidata.org/wiki/Help:Ranking

[^3_4]: https://www.perplexity.ai/search/f56b85a5-4539-4f3e-b888-d57915571215

[^3_5]: https://memgraph.com/docs/fundamentals/indexes

[^3_6]: https://www.ijcai.org/proceedings/2021/0620.pdf

[^3_7]: https://babelnet.org/pydoc/1.0/babelnet.api.html

[^3_8]: http://www.w3.org/2015/09/bpmlod-reports/multilingual-dictionaries/

[^3_9]: https://www.youtube.com/watch?v=DAlWoamQ41Q

[^3_10]: https://www.wikidata.org/wiki/Help:Deprecation/List_of_Reasons_for_Deprecation

[^3_11]: https://archives.iw3c2.org/www2012/proceedings/companion/p393.pdf

[^3_12]: https://docs.spring.io/spring-data/neo4j/docs/3.3.2.RELEASE/reference/html/

[^3_13]: https://www.wikidata.org/wiki/Property:P2241

[^3_14]: https://arxiv.org/pdf/2602.03417.pdf

[^3_15]: https://stackoverflow.com/questions/58339790/importing-deprecated-statements-in-wikidata

[^3_16]: https://aclanthology.org/2022.acl-long.121.pdf

[^3_17]: https://meta.wikimedia.org/wiki/Community_Wishlist_Survey_2019/Wikidata

[^3_18]: https://www.sciencedirect.com/science/article/pii/S0004370216300820

[^3_19]: https://seosolutionstexas.com/wikidata-qids-for-entity-seo/

[^3_20]: https://babelnet.org/pydoc/1.1/babelnet.resources.WikidataID.html

[^3_21]: https://methodshub.gesis.org/library/tutorials/method-hub-linkage/1/

[^3_22]: https://www.wikidata.org/wiki/Wikidata_talk:Identifiers

[^3_23]: https://babelnet.org/guide

[^3_24]: https://www.wikidata.org/wiki/Wikidata:Tools/Enhance_user_interface

[^3_25]: https://aclanthology.org/2021.gwc-1.29.pdf

[^3_26]: https://en.wikipedia.org/wiki/Wikidata

[^3_27]: https://www.w3.org/community/bpmlod/wiki/Converting_BabelNet_as_Linguistic_Linked_Data

[^3_28]: https://github.com/open-energy-transition/wikidata_qid_generator

[^3_29]: https://arxiv.org/pdf/1803.04349.pdf

[^3_30]: https://www.sciencedirect.com/science/article/pii/S0099133321000173

[^3_31]: https://blogs.bodleian.ox.ac.uk/digital/2017/10/12/reconciling-database-identifiers-with-wikidata/


---

# 18 CANONICAL FACETS (UPPERCASE):

ARCHAEOLOGICAL
ARTISTIC
BIOGRAPHIC
COMMUNICATION
CULTURAL
DEMOGRAPHIC
DIPLOMATIC
ECONOMIC
ENVIRONMENTAL
GEOGRAPHIC
INTELLECTUAL
LINGUISTIC
MILITARY
POLITICAL
RELIGIOUS
SCIENTIFIC
SOCIAL
TECHNOLOGICAL
are our facets, each subjectConcept is evaluated from these perspective by subject+facet agent

Good — I now have the full facet context mapped against your prior architecture discussions. Let me lock this in precisely.

## 18 Canonical Facets + Cipher Implications

Confirmed: your system has exactly **18 canonical facets**, each serving as a lens through which a Subject Facet Agent (SFA) evaluates every SubjectConcept. This is the locked list, previously evolved from 15→16→18 across your architecture iterations. Temporal was removed as a standalone facet and instead treated as a structural backbone (year backbone for Roman facts).[^4_1][^4_2][^4_3]

### How Facets Shape the Cipher

Every `SubjectConcept × Facet` combination produces a **unique evaluation context** — this is where the SFA operates. That means the facet is a **first-class cipher component**, not metadata. Your CLAIM_ID_ARCHITECTURE already encodes this correctly with `facet_id` in the cipher formula .[^4_4]

But here's the critical implication for cross-entity/subgraph implementation: the 18 facets define **18 possible subgraph dimensions** per entity. Caesar (Q1048) doesn't live in one subgraph — he lives in up to 18 faceted subgraphs, each evaluated by a different SFA:


| Facet | SFA Evaluates | Example Claim |
| :-- | :-- | :-- |
| POLITICAL | Power structures, governance | "Caesar held consulship" |
| MILITARY | Warfare, command, logistics | "Caesar commanded Legio XIII" |
| ECONOMIC | Trade, finance, resources | "Caesar's land reform policy" |
| SOCIAL | Class, patronage, networks | "Caesar as patron of clients" |
| RELIGIOUS | Ritual, priesthood, belief | "Caesar as Pontifex Maximus" |
| DIPLOMATIC | Treaties, alliances, negotiations | "Caesar's alliance with Pompey" |
| GEOGRAPHIC | Location, territory, movement | "Caesar's Gallic campaigns" |
| BIOGRAPHIC | Life events, prosopography | "Caesar born 100 BCE" |
| ... | *(remaining 10 facets)* | ... |

### The Cipher Architecture Per Layer

This gives us a **three-tier cipher model** that maps to your entity types and subgraphs:

**Tier 1 — Entity Cipher (the vertex itself)**

```python
entity_cipher = Hash(
    QID_or_crys_id +           # "Q1048" or "crys:PERSON:bn_xxxxx"
    entity_type +              # "PERSON" | "EVENT" | "PLACE" | ...
    namespace                  # "wd" | "crys" | "bn"
)
# Result: "ent_per_a4f8c2..." (entity type prefix)
```

This is the **Who/What/Where** — the thing itself. One per entity in the graph. This is what you jump to when you want "everything about Caesar".

**Tier 2 — Faceted Entity Cipher (SubjectConcept × Facet)**

```python
faceted_cipher = Hash(
    entity_cipher +            # Tier 1 cipher
    facet_id +                 # "POLITICAL" (from 18 canonical)
    subjectconcept_id          # The SubjectConcept anchor
)
# Result: "fent_pol_7b3d1e..." (faceted entity prefix)
```

This is the **subgraph address** — it identifies "Caesar evaluated from the POLITICAL perspective anchored to SubjectConcept X." This is what the SFA produces. Up to 18 of these per entity.[^4_4]

**Tier 3 — Claim Cipher (the assertion)**

```python
claim_cipher = Hash(
    subject_entity_cipher +    # Tier 1 (Who)
    property_PID +             # P39 (What relationship)
    object_entity_cipher +     # Tier 1 (To whom/what)
    facet_id +                 # "POLITICAL" (Which lens)
    temporal_scope +           # "-0059" (When)
    source_QID +               # Q47461 (Polybius)
    passage_locator            # "Caes.32"
)
# Result: "fclaim_pol_b22020c0..." (already defined in your doc)
```

This is what CLAIM_ID_ARCHITECTURE already specifies . It builds on Tier 1 entity ciphers.

### Pattern Matching Facilitated by Ciphers

Since the cipher **facilitates** pattern matching, the composite index strategy maps directly to these tiers:

```cypher
// Tier 1: Jump to entity — "everything about Caesar"
CREATE INDEX ent_cipher_idx FOR (n:Entity) ON (n.entity_cipher)
MATCH (n:Entity {entity_cipher: "ent_per_a4f8c2..."})

// Tier 2: Jump to faceted subgraph — "Caesar's political dimension"  
CREATE INDEX fent_cipher_idx FOR (n:FacetedEntity) ON (n.faceted_cipher)
MATCH (n:FacetedEntity {faceted_cipher: "fent_pol_7b3d1e..."})

// Tier 3: Jump to specific claim — exact assertion
CREATE INDEX fclaim_cipher_idx FOR (c:FacetClaim) ON (c.cipher)
MATCH (c:FacetClaim {cipher: "fclaim_pol_b22020c0..."})

// Pattern match across facets — "all of Caesar's claims in any facet"
CREATE INDEX entity_facet_idx FOR (c:FacetClaim) ON (c.subject_entity_cipher, c.facet_id)
MATCH (c:FacetClaim {subject_entity_cipher: "ent_per_a4f8c2..."})
// Returns all 18 faceted dimensions
```

The key insight: **Tier 1 cipher is the cross-subgraph join key.** When you want to vertex-jump from Caesar's MILITARY subgraph to his POLITICAL subgraph, you don't traverse — you take his `entity_cipher`, swap the `facet_id`, and compute the Tier 2 `faceted_cipher` for the target facet. Direct index seek, no traversal.[^4_5]

### What This Means for the SFA Workflow

When an SFA (say, POLITICAL_SFA) evaluates a SubjectConcept:

1. It receives the `entity_cipher` (Tier 1) and `subjectconcept_id`
2. It computes the `faceted_cipher` (Tier 2) for its assigned facet — `POLITICAL`
3. It produces `FacetClaim` nodes (Tier 3) with claim ciphers that reference the Tier 1 entity ciphers of both subject and object
4. Every claim is anchored to the SubjectConcept via `[:SUBJECT]` edge[^4_4]
5. Cross-facet vertex jumping is possible because the `entity_cipher` in the claim is the same across all 18 facets

### Outstanding Question

The **Tier 2 faceted cipher** is the new concept here that isn't in your current CLAIM_ID_ARCHITECTURE doc. Do you want this as an explicit node in Neo4j (a `(:FacetedEntity)` or `(:SubgraphAnchor)` node that all claims within that facet connect to), or as a **computed virtual address** that agents use for routing but doesn't materialize as a node?

That decision determines whether a vertex jump crosses through a hub node or goes direct to claims.
<span style="display:none">[^4_6][^4_7]</span>

<div align="center">⁂</div>

[^4_1]: projects.chrystallum.ontology_facets

[^4_2]: https://www.perplexity.ai/search/5db330ea-a753-4487-bdf4-178df8cbedcd

[^4_3]: https://www.perplexity.ai/search/02a53286-9df9-4405-ae8f-218fdeecb772

[^4_4]: https://www.perplexity.ai/search/95c39fa0-df39-4ddc-80bd-012b60786525

[^4_5]: https://www.perplexity.ai/search/325a1f10-c226-4bec-aeac-8fa2e2193386

[^4_6]: projects.knowledge_graph.vertex_jumps

[^4_7]: https://www.perplexity.ai/search/7fbb0485-ddda-4937-9e84-7c3b856c2556

