# Quick Reference: Claim Canonicalization

**Purpose**: Ensure reproducible claim ciphers across federated systems

---

## TL;DR

```python
from chrystallum.models import Claim, FacetAssignment, initialize_registry

# Initialize once at startup
initialize_registry("JSON/facets.json", "CSV/relationship_types.csv")

# Create claim with auto-computed canonical cipher
claim = Claim.create_with_cipher(
    claim_id="claim_001",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="extraction_agent"
)

# Cipher is automatically computed and guaranteed valid
assert claim.verify_cipher()  # ✅ True
```

---

## Common Use Cases

### 1. Create Claim with Auto-Cipher

**Recommended** for all new claims:

```python
claim = Claim.create_with_cipher(
    claim_id="claim_001",
    content="Julius Caesar crossed the Rubicon in 49 BCE",
    source_id="plutarch_lives_caesar_ch32",
    created_by="agent_001",
    facets=[
        FacetAssignment(facet="military", confidence=0.95)
    ]
)

print(f"Cipher: {claim.cipher}")  # 64-char SHA256 hash
```

### 2. Verify Claim Cipher

Check if stored cipher matches computed cipher:

```python
# Load claim from database
claim = Claim(**claim_data)

# Verify integrity
if claim.verify_cipher():
    print("✓ Cipher is valid")
else:
    print("✗ WARNING: Cipher is invalid - possible tampering")
```

### 3. Detect Duplicate Claims

Use ciphers to detect duplicate claims across systems:

```python
# System A discovers a fact
claim_a = Claim.create_with_cipher(
    claim_id="a_001",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_a"
)

# System B independently discovers the same fact
claim_b = Claim.create_with_cipher(
    claim_id="b_001",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_b"
)

# Check for duplicates
if claim_a.cipher == claim_b.cipher:
    print("✓ Duplicate detected - can merge")
    # Deduplication logic here
```

### 4. Manual Cipher Computation

For advanced use cases:

```python
from chrystallum.models import compute_claim_cipher

# Compute cipher manually
cipher = compute_claim_cipher(
    content="Julius Caesar crossed the Rubicon",
    metadata={
        "source_id": "source_001",
        "facets": ["military"],
        "relationships": []
    }
)

print(f"Cipher: {cipher}")  # 64-char SHA256
```

---

## API Reference

### Claim Methods

#### `Claim.create_with_cipher(...)`

Factory method to create claim with auto-computed cipher.

**Parameters**:
- `claim_id` (str): Unique claim identifier
- `content` (str): Main claim text
- `source_id` (str): Source document ID
- `created_by` (str): Agent that created the claim
- `facets` (List[FacetAssignment], optional): Facet assignments
- `relationships` (List[RelationshipAssertion], optional): Relationship assertions
- `confidence` (float, optional): Overall confidence (default: 0.70)
- `status` (LifecycleStatus, optional): Lifecycle status (default: DRAFT)
- `algorithm` (str, optional): Hash algorithm (default: "sha256")

**Returns**: Claim instance with valid cipher

**Example**:
```python
claim = Claim.create_with_cipher(
    claim_id="claim_001",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_001"
)
```

#### `claim.compute_canonical_cipher(algorithm="sha256")`

Compute canonical cipher for existing claim.

**Parameters**:
- `algorithm` (str, optional): Hash algorithm (sha256, sha512, sha3_256)

**Returns**: str (64-char hex string for SHA256)

**Example**:
```python
cipher = claim.compute_canonical_cipher()
print(f"Computed cipher: {cipher}")
```

#### `claim.verify_cipher(algorithm="sha256")`

Verify that stored cipher matches computed cipher.

**Parameters**:
- `algorithm` (str, optional): Hash algorithm (must match what was used to create cipher)

**Returns**: bool (True if cipher is valid, False otherwise)

**Example**:
```python
if claim.verify_cipher():
    print("✓ Cipher is valid")
else:
    print("✗ Cipher is invalid")
```

### Canonicalization Functions

#### `normalize_unicode(text, form="NFC")`

Normalize Unicode representation.

**Handles**:
- `café` (é as 1 char) vs `café` (e + combining accent) → same
- `Å` (Angstrom) vs `Å` (A + ring) → same

**Example**:
```python
from chrystallum.models import normalize_unicode

text1 = "café"  # NFC form
text2 = "café"  # NFD form
assert normalize_unicode(text1) == normalize_unicode(text2)
```

#### `normalize_whitespace(text, preserve_paragraphs=True)`

Normalize whitespace.

**Handles**:
- Multiple spaces → single space
- Tabs → spaces
- NBSP → regular space
- Preserves paragraph breaks (double newline)

**Example**:
```python
from chrystallum.models import normalize_whitespace

text = "  Hello   world  "
result = normalize_whitespace(text)
# Result: "Hello world"
```

#### `normalize_float(value, precision=6)`

Normalize floating point numbers.

**Handles**:
- `0.95` vs `0.9500000001` → same
- Fixed precision (6 decimals by default)

**Example**:
```python
from chrystallum.models import normalize_float

assert normalize_float(0.95) == normalize_float(0.9500000001)
# Both return "0.950000"
```

#### `canonicalize_dict(data, sort_keys=True)`

Canonicalize dictionary (sorted keys, normalized values).

**Handles**:
- `{"b":2,"a":1}` vs `{"a":1,"b":2}` → same
- Recursively normalizes nested structures

**Example**:
```python
from chrystallum.models import canonicalize_dict

dict1 = {"b": 2, "a": 1}
dict2 = {"a": 1, "b": 2}
assert canonicalize_dict(dict1) == canonicalize_dict(dict2)
```

#### `compute_claim_cipher(content, metadata, algorithm="sha256")`

One-step cipher computation.

**Parameters**:
- `content` (str): Main claim text
- `metadata` (dict): Claim metadata (source_id, facets, relationships)
- `algorithm` (str, optional): Hash algorithm (default: sha256)

**Returns**: str (64-char hex string for SHA256)

**Example**:
```python
from chrystallum.models import compute_claim_cipher

cipher = compute_claim_cipher(
    content="Julius Caesar crossed the Rubicon",
    metadata={
        "source_id": "source_001",
        "facets": ["military"],
        "relationships": []
    }
)
print(f"Cipher: {cipher}")
```

---

## Content-Addressability

### What's Included in Cipher

The cipher is computed from **content-relevant fields only**:

✅ Included:
- `content`: Main claim text
- `source_id`: Source document identifier
- `facets`: List of facet keys (sorted)
- `relationships`: List of relationship assertions (sorted)

❌ Excluded:
- `claim_id`: Generated identifier (not content)
- `created_by`: Agent identifier (metadata)
- `created_at`: Timestamp (metadata)
- `confidence`: Assessment score (metadata)
- `status`: Lifecycle status (metadata)

**Rationale**: Two agents discovering the same fact from the same source should produce **identical ciphers**, regardless of:
- When they discovered it (`created_at`)
- Who discovered it (`created_by`)
- How confident they are (`confidence`)
- What claim ID they assigned (`claim_id`)

### Example: Content-Addressability

```python
# Agent A discovers a fact at time T1
claim_a = Claim.create_with_cipher(
    claim_id="agent_a_claim_123",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_a",
    confidence=0.95,
    # created_at: 2026-02-17T10:00:00Z
)

# Agent B discovers the SAME fact at time T2
claim_b = Claim.create_with_cipher(
    claim_id="agent_b_claim_456",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_b",
    confidence=0.88,
    # created_at: 2026-02-17T15:00:00Z
)

# Different metadata (claim_id, created_by, confidence, created_at)
# BUT same logical content
assert claim_a.cipher == claim_b.cipher  # ✅ True

# This enables:
# 1. Deduplication across systems
# 2. Content verification
# 3. Canonical claim identity
```

---

## Cross-System Reproducibility

The canonicalization framework ensures **identical ciphers** across systems despite:

- Unicode variations
- Whitespace differences
- Float precision errors
- Key ordering differences

### Example: Cross-System Reproducibility

```python
# System 1: Clean input
claim_1 = Claim.create_with_cipher(
    claim_id="sys1_001",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_1"
)

# System 2: Extra whitespace, Unicode variants
claim_2 = Claim.create_with_cipher(
    claim_id="sys2_001",
    content="  Julius   Caesar crossed the Rubicon  ",  # Extra spaces
    source_id="source_001",
    created_by="agent_2"
)

# System 3: Float precision differences
claim_3 = Claim.create_with_cipher(
    claim_id="sys3_001",
    content="Julius Caesar crossed the Rubicon",
    source_id="source_001",
    created_by="agent_3",
    facets=[
        FacetAssignment(facet="military", confidence=0.9500000001)  # Precision error
    ]
)

# All produce IDENTICAL ciphers
assert claim_1.cipher == claim_2.cipher == claim_3.cipher  # ✅ True

print("✓ Federation-ready: reproducible ciphers across systems")
```

---

## Testing

### Run Canonicalization Tests

```bash
# Canonicalization module tests (10 tests)
python Python/models/test_canonicalization.py

# Claim cipher integration tests (6 tests)
python Python/models/test_claim_cipher.py
```

### Expected Output

```
======================================================================
CANONICALIZATION TEST SUITE
======================================================================
✓ PASS: Unicode Normalization
✓ PASS: Whitespace Normalization
✓ PASS: DateTime Normalization
✓ PASS: Float Normalization
✓ PASS: Dict Canonicalization
✓ PASS: Canonical JSON
✓ PASS: Claim Canonicalization
✓ PASS: Cipher Reproducibility
✓ PASS: Edge Cases
✓ PASS: Cross-System Reproducibility

RESULTS: 10 passed, 0 failed
✅ Ready for federation
```

---

## Best Practices

### ✅ DO

- **Use `create_with_cipher()`** for all new claims (recommended)
- **Verify ciphers** when loading claims from untrusted sources
- **Use ciphers for deduplication** across systems
- **Include source_id** in cipher computation (claims from different sources are different)

### ❌ DON'T

- Don't manually compute ciphers unless necessary
- Don't include metadata (claim_id, created_by, confidence) in cipher computation
- Don't use ciphers for security/authentication (use ADR-005 signing instead)
- Don't modify claim content without recomputing cipher

---

## Troubleshooting

### Q: Cipher verification fails for valid-looking claim

**A**: Claim content or metadata was modified after cipher was computed.

**Solution**:
```python
# Recompute cipher
new_cipher = claim.compute_canonical_cipher()
claim.cipher = new_cipher

# Verify
assert claim.verify_cipher()  # ✅ True
```

### Q: Two "identical" claims have different ciphers

**A**: Check if source_id, facets, or relationships differ.

**Solution**:
```python
# Debug what's included in cipher computation
print(f"Content: {claim.content}")
print(f"Source: {claim.source_id}")
print(f"Facets: {sorted([f.facet for f in claim.facets])}")
print(f"Relationships: {[(r.rel_type, r.subject_id, r.object_id) for r in claim.relationships]}")
```

### Q: Need to migrate existing claims to use canonical ciphers

**A**: Recompute ciphers for all existing claims.

**Solution**:
```python
# For each claim in database
for claim_data in database.get_all_claims():
    claim = Claim(**claim_data)
    
    # Recompute canonical cipher
    new_cipher = claim.compute_canonical_cipher()
    
    # Update database
    database.update_cipher(claim.claim_id, new_cipher)
    
    print(f"✓ Updated {claim.claim_id}")
```

---

## References

- Full documentation: [Python/models/README.md](README.md)
- Completion report: [PRIORITY_4_COMPLETION_REPORT.md](../../PRIORITY_4_COMPLETION_REPORT.md)
- Architecture: ADR-001 Claim Identity (Chrystallum Architecture, Appendix U)

---

**Version**: 0.2.0  
**Status**: Production-Ready  
**Last Updated**: 2026-02-17
