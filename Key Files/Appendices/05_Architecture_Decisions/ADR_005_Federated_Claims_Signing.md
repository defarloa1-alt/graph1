# Appendix X: ADR 005 Federated Claims Signing

**Version:** 3.2 Decomposed  
**Date:** February 19, 2026  
**Source:** Extracted from Consolidated Architecture Document

---

## Navigation

**Main Architecture:**
- [ARCHITECTURE_CORE.md](../../ARCHITECTURE_CORE.md)
- [ARCHITECTURE_ONTOLOGY.md](../../ARCHITECTURE_ONTOLOGY.md)
- [ARCHITECTURE_IMPLEMENTATION.md](../../ARCHITECTURE_IMPLEMENTATION.md)
- [ARCHITECTURE_GOVERNANCE.md](../../ARCHITECTURE_GOVERNANCE.md)

**Appendices Index:** [README.md](../README.md)

---

# **Appendix X: Federated Claims Signing & Cryptographic Trust Model (ADR-005)**

**Status**: ACCEPTED (2026-02-16, Architecture Review Issue #6)

**Context & Problem**

The system currently describes **content-addressable claims** (`cipher` = SHA256 of claim content) and **Merkle trees** for verifying claim integrity. However, the architecture underspecifies **how institutions establish trust across boundaries** when exchanging claims:

- Who signs claims? (Institution? Individual agents? Query endpoints?)
- How do external institutions discover/verify a signing key? (Centralized registry? DNSSEC? DHT?)
- What happens when two institutions provide conflicting signed claims? (Competing signatures, same cipher)
- How are compromised keys handled? (Revocation, rotation, retroactive audit)
- Can a single institution operate without signing? (Personal research tool vs. federated authority)

**Current state**: Cryptographic verification works for integrity (cipher + Merkle root) but not for **provenance authentication** across institutional boundaries. A claim could be valid content (matches cipher) but falsely attributed to the wrong endpoint.

**Evidence of underspecification**:

1. Section 6.4.2 discusses "institutional signature" but doesn't specify format
2. Section 6.4 mentions "state_root" (Merkle tree) but not cryptographic signatures
3. Appendix R (Federation Strategy) describes authority layers but not institutional key distribution
4. No dispute resolution model for conflicting signed claims

---

## **X.1 Decision & Solution**

**Adopt a three-tier federated trust model** combining institutional signing, transparency logging, and cryptographic verification:

### **X.1.1 Signing Model: Institutional Claims Authority**

**Principle**: Each institution that publishes claims must operate an **institutional signing authority** with:

1. **Long-term key pair** (Ed25519 or RSA-4096):
   - Public key: Published in institutional registry (DNS TXT record or `.well-known/chrystallum.json`)
   - Private key: Stored in hardware security module (HSM) or trusted key management service
   - Key ID: Calculated from public key fingerprint (first 16 chars of SHA256)

2. **Per-claim signature**:
   - Signs the content hash (cipher), not the full claim data
   - Format: `<institution_key_id>.<timestamp>.<proof_chain_root>`
   - Proof chain root: Merkle root of all claims signed in same batch (~5min window)

3. **Institutional registry entry**:
   ```json
   {
     "institution": "University of Oxford",
     "endpoint": "https://claims-api.ox.ac.uk",
     "public_key_id": "ox_2026_0a1b",
     "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...",
     "key_algorithm": "Ed25519",
     "key_rotated_at": "2026-01-15T00:00:00Z",
     "transparency_log": "https://claims-transparency.ox.ac.uk",
     "signing_policy": "https://claims-api.ox.ac.uk/.well-known/signing-policy.txt",
     "contact": "claims-admin@ox.ac.uk"
   }
   ```

**Benefits**:
- Verifiable without centralized certificate authority (DIY PublicKeyInfrastructure)
- Key rotation via timestamp (old signatures still valid with historical key)
- Accountability: Signed claims tied to institution, not individual agents

**Limitations**:
- Institutions must operate key management infrastructure
- DNS/registry poisoning possible (recommend DNSSEC + pinning)
- No online revocation (timestamp-based keys don't support instant revocation)

---

### **X.1.2 Claim Signing Structure**

**Every signed claim contains**:

```json
{
  "claim_id": "claim_00456",
  "cipher": "sha256_abc123def456...",
  "content": { /* claim data */ },
  
  // CRYPTOGRAPHIC PROVENANCE
  "signatures": [
    {
      "institution_key_id": "ox_2026_0a1b",
      "timestamp": "2026-02-16T10:30:00Z",
      "algorithm": "Ed25519",
      "value": "30450220_0761_43d0_8c67_8a3a9c2d1b4f...",
      
      // PROOF CHAIN (enables transparency verification)
      "proof_chain_root": "merkle_root_batch_2026_02_16_10_30",
      "proof_chain_path": ["leaf_hash_1", "parent_hash_2", "parent_hash_3"],
      
      // BATCH CONTEXT (links to transparency log entry)
      "batch_id": "batch_2026_02_16_10_30_001",
      "batch_index": 23,  // This claim is #23 in batch
      "batch_log_url": "https://claims-transparency.ox.ac.uk/batch/2026_02_16_10_30_001"
    }
  ],
  
  // VERIFICATION RECEIPT (used to re-fetch key + signature proof)
  "verification_receipt": {
    "institution": "University of Oxford",
    "key_registry_url": "https://claims-api.ox.ac.uk/.well-known/chrystallum.json",
    "verified_at": "2026-02-16T10:30:05Z"
  }
}
```

**Signature verification algorithm**:

```python
def verify_claim_signature(claim: dict, institutional_registry: dict) -> bool:
    """
    Verify a claim's cryptographic signature.
    
    Args:
        claim: Claim with signatures field
        institutional_registry: Dict mapping institution_key_id → public_key
    
    Returns:
        True if signature valid, False otherwise
    """
    for sig in claim.get("signatures", []):
        key_id = sig["institution_key_id"]
        pub_key = institutional_registry.get(key_id)
        
        if not pub_key:
            logger.warning(f"Unknown key ID: {key_id}")
            continue
        
        # Re-hash the cipher to verify signature wasn't tampered
        signed_data = f"{claim['cipher']}.{sig['timestamp']}.{sig['proof_chain_root']}"
        
        try:
            # Import public key and verify
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(
                base64.b64decode(pub_key)
            )
            public_key.verify(
                base64.b64decode(sig["value"]),
                signed_data.encode()
            )
            logger.info(f"✓ Signature valid for key {key_id}")
            return True
        except cryptography.exceptions.InvalidSignature:
            logger.error(f"✗ Signature invalid for key {key_id}")
            return False
    
    logger.warning("No valid signatures found")
    return False
```

---

### **X.1.3 Institutional Registry & Key Distribution**

**Institutions publish public keys via**:

1. **DNS TXT record** (DNSSEC-protected):
   ```
   _chrystallum.ox.ac.uk. IN TXT "v=chrys1; key_id=ox_2026_0a1b; pubkey=MIIBIjANBgk... ; endpoint=https://claims-api.ox.ac.uk"
   ```

2. **`.well-known/chrystallum.json`** (served over HTTPS with HSTS):
   ```json
   {
     "institution": "University of Oxford",
     "keys": [
       {
         "key_id": "ox_2026_0a1b",
         "public_key": "-----BEGIN PUBLIC KEY-----\n...",
         "valid_from": "2026-01-15T00:00:00Z",
         "valid_until": "2027-01-15T00:00:00Z",
         "algorithm": "Ed25519",
         "rotate_next": "2027-01-01T00:00:00Z"
       },
       {
         "key_id": "ox_2025_1c2d",
         "public_key": "-----BEGIN PUBLIC KEY-----\n...",
         "valid_from": "2025-01-15T00:00:00Z",
         "valid_until": "2026-01-15T00:00:00Z",
         "algorithm": "Ed25519",
         "retired": true
       }
     ],
     "transparency_log": "https://claims-transparency.ox.ac.uk",
     "policy": "https://claims-api.ox.ac.uk/.well-known/signing-policy.txt"
   }
   ```

3. **Federated registry service** (optional, maintained by consortium):
   - Gossip protocol to sync key updates
   - Prevents DNS-only dependency
   - Enables pin/revocation signaling

**Key rotation**: 
- Short-lived keys (12 months), new key added 3 months before expiry
- Old keys kept in registry for 2+ years to verify historical signatures
- Revocation via "revoked" flag + reasoning field (compromise, transition, etc.)

---

### **X.1.4 Transparency Logging for Dispute Resolution**

**Problem**: If two institutions claim to have authored the same content (same cipher), which signature is authoritative?

**Solution**: Each institution maintains an **append-only transparency log** of all claims it signs, enabling:
- Auditability: "Did institution X sign this claim on date Y?"
- Consistency: Proving no clock skew (same cipher never signed twice in 24h)
- Repudiation resistance: Institution can't deny signing a claim once in public log

**Transparency log structure** (similar to Certificate Transparency [RFC 6962]):

```json
{
  "version": "chrystallum_ct/2026-01-01",
  "batch_id": "batch_2026_02_16_10_30_001",
  "batch_timestamp": "2026-02-16T10:30:00Z",
  "batch_root": "merkle_root_abc123",
  "entries": [
    {
      "index": 1,
      "claim_id": "claim_00123",
      "cipher": "sha256_xyz789",
      "timestamp": "2026-02-16T10:30:01Z",
      "facet": "DIPLOMATIC",
      "geographic_scope": "Rome",
      "temporal_scope": "-27/14",
      "source_id": "source_001_plb_001",
      "signature": "30450220_...",
      "leaf_hash": "hash_of_this_entry"
    },
    ...
  ],
  "batch_proof": {
    "tree_size_before": 45678,
    "tree_size_after": 45800,
    "tree_root": "merkle_root_post_batch",
    "consistency_proof": ["proof_hash_1", "proof_hash_2"]
  }
}
```

**Dispute resolution using transparency logs**:

```python
def resolve_signature_conflict(cipher: str, sig1: dict, sig2: dict) -> str:
    """
    When two institutions claim to have signed the same content (same cipher),
    determine which signature should be trusted.
    
    Algorithm:
    1. Both signatures must be in respective transparency logs
    2. Earlier timestamp wins (first publisher)
    3. If timestamps identical, institution_key_id alphabetically first wins
    4. If institution disputes entry in log, requires cryptographic proof
       of log tampering (detectable via tree hash consistency mismatches)
    """
    
    # Verify both signatures are in respective transparency logs
    log1_valid = fetch_from_transparency_log(
        sig1["institution_key_id"], 
        sig1["batch_id"], 
        sig1["batch_index"]
    )
    log2_valid = fetch_from_transparency_log(
        sig2["institution_key_id"], 
        sig2["batch_id"], 
        sig2["batch_index"]
    )
    
    if not (log1_valid and log2_valid):
        raise ConflictResolutionError(
            f"Cannot resolve: one signature not in transparency log"
        )
    
    t1 = datetime.fromisoformat(sig1["timestamp"])
    t2 = datetime.fromisoformat(sig2["timestamp"])
    
    if t1 < t2:
        return "sig1"  # Sig1 has earlier timestamp, sig1 wins
    elif t2 < t1:
        return "sig2"
    else:
        # Timestamps identical (should be rare, within same batch)
        # Break tie alphabetically
        return "sig1" if sig1["institution_key_id"] < sig2["institution_key_id"] else "sig2"
```

**Transparency log verification** (client-side audit):

```python
def audit_transparency_log(batch_data: dict, previous_root: str) -> bool:
    """
    Verify a transparency log batch hasn't been tampered with.
    
    Uses merkle tree consistency proofs to ensure:
    1. No entries were removed from previous batches
    2. No entries were added out-of-order
    3. Tree structure matches announced root
    """
    
    # Compute tree root from entries
    computed_root = merkle_tree_from_entries(batch_data["entries"])
    
    if computed_root != batch_data["batch_root"]:
        raise LogTamperDetected("Batch root mismatch")
    
    # Verify consistency proof (linking to previous tree)
    if not verify_merkle_consistency_proof(
        previous_root=previous_root,
        new_root=batch_data["batch_root"],
        consistency_proof=batch_data["batch_proof"]["consistency_proof"],
        tree_size_before=batch_data["batch_proof"]["tree_size_before"],
        tree_size_after=batch_data["batch_proof"]["tree_size_after"]
    ):
        raise LogTamperDetected("Consistency proof verification failed")
    
    logger.info(f"✓ Transparency log batch {batch_data['batch_id']} verified")
    return True
```

---

### **X.1.5 Verification Flow for External Institutions**

**Harvard researcher wants to verify a claim published by Oxford:**

```python
def verify_external_claim(claim_url: str) -> dict:
    """
    Full verification flow for a claim published by external institution.
    """
    
    # Step 1: Fetch claim from external endpoint
    claim = requests.get(claim_url).json()
    cipher = claim["cipher"]
    
    # Step 2: Verify cipher matches content (integrity check)
    computed_cipher = sha256(json.dumps(claim["content"])).hexdigest()
    if computed_cipher != cipher:
        raise IntegrityError("Content doesn't match cipher")
    
    # Step 3: Fetch institutional public key
    institution = claim["verification_receipt"]["institution"]
    key_registry_url = claim["verification_receipt"]["key_registry_url"]
    registry = requests.get(key_registry_url).json()
    
    pub_key = None
    for sig in claim["signatures"]:
        key_id = sig["institution_key_id"]
        for key_entry in registry["keys"]:
            if key_entry["key_id"] == key_id:
                pub_key = key_entry["public_key"]
                break
    
    if not pub_key:
        raise KeyNotFoundError(f"Public key not found for claim")
    
    # Step 4: Verify cryptographic signature
    if not verify_claim_signature(claim, {key_id: pub_key}):
        raise SignatureError("Signature verification failed")
    
    # Step 5: Audit transparency log entry
    for sig in claim["signatures"]:
        batch = requests.get(sig["batch_log_url"]).json()
        if not audit_transparency_log(batch, previous_root):
            raise LogTamperDetected("Transparency log tampered")
    
    logger.info(f"✓ Claim {claim['claim_id']} verified with institutional signature")
    return {
        "verified": True,
        "institution": institution,
        "signatures": len(claim["signatures"]),
        "timestamp": claim["signatures"][0]["timestamp"]
    }
```

---

## **X.2 Rationale & Evidence**

**Why this approach?**

1. **Verifiable without central authority**: Each institution is responsible for its own keys (like DNSSEC)
2. **Enables dispute resolution**: Transparency logs provide immutable audit trail
3. **Compatible with existing cipher model**: Signatures are separate from content hash
4. **Scales to consortiums**: Multiple institutions can sign same claim (consensus) or conflicting claims (logged)
5. **Supports anonymous research**: Single-institution queries don't require signing

**Precedent**:
- **Certificate Transparency** (RFC 6962): Transparency logs for X.509 certificates, detects unauthorized certificates
- **Sigsum** (formerly Trillian fork): Alternative to CT for verifiable transparency logs
- **HyperLedger Fabric**: Multi-organization signing with cryptographic proofs

**Evidence of feasibility**:
- OpenSSL/cryptography libraries support Ed25519 + Merkle trees
- DNSSEC infrastructure exists (institutions with .well-known already trusted)
- Transparency logs proven in production (Google, DigiCert, Let's Encrypt)

---

## **X.3 Consequences**

### **Positive**:
- ✅ **Verifiable provenance**: Claims cryptographically tied to institutions, not forgers
- ✅ **Dispute resolution**: Transparency logs provide evidence of "who signed first"
- ✅ **Retroactive audit**: Historical claims auditable even after key rotation
- ✅ **Consortium operations**: Multiple institutions can sign same claim for consensus
- ✅ **Enables federation trust**: Solves "how do we trust external claims?" without central authority

### **Negative**:
- ⚠️ **Key management complexity**: Institutions must operate HSM or equivalent (support burden)
- ⚠️ **DNS dependency**: Key distribution requires DNSSEC or alternative (not all registrars support)
- ⚠️ **Transparency log scaling**: Append-only logs grow continuously (mitigated by log rotation + archival)
- ⚠️ **No real-time revocation**: Compromised keys can't be instantly revoked (timestamp-based keys expire naturally)

### **Neutral**:
- ○ Single-institution deployments can operate without external signing
- ○ Claim cipher remains unchanged (backward compatible)
- ○ Batch signing reduces per-claim overhead

---

## **X.4 Implementation Requirements**

### **X.4.1 Backend: Institutional Signing Authority**

**Required changes to claim creation workflow**:

```python
# Python pseudocode for claim creation with signing

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import hashes, serialization
from datetime import datetime, timedelta
import hashlib
import json

class InstitutionalSigningAuthority:
    """Manages institutional claim signing."""
    
    def __init__(self, private_key_path: str, institution_id: str):
        with open(private_key_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None
            )
        self.institution_id = institution_id
        self.batch_claims = []
        self.batch_timestamp = None
    
    def sign_claim(self, claim: dict, facet: str, source_id: str) -> dict:
        """
        Sign a claim and add to current batch.
        
        Args:
            claim: Claim dictionary with 'cipher' field
            facet: Facet classification (e.g., 'DIPLOMATIC')
            source_id: Source passage ID
        
        Returns:
            Claim with signatures field populated
        """
        
        # Create batch if needed
        if self.batch_timestamp is None:
            self.batch_timestamp = datetime.utcnow()
            self.batch_id = f"batch_{self.batch_timestamp.isoformat().replace(':', '').replace('.', '_')}"
        
        # Build signature input
        timestamp = datetime.utcnow().isoformat() + "Z"
        proof_chain_root = self.compute_batch_merkle_root()  # Recomputed as batch grows
        
        signed_data = f"{claim['cipher']}.{timestamp}.{proof_chain_root}".encode()
        signature = self.private_key.sign(signed_data)
        
        # Generate key ID from public key
        pub_key_bytes = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        key_fingerprint = hashlib.sha256(pub_key_bytes).hexdigest()[:16]
        key_id = f"{self.institution_id}_2026_{key_fingerprint}"
        
        # Add signature
        sig_entry = {
            "institution_key_id": key_id,
            "timestamp": timestamp,
            "algorithm": "Ed25519",
            "value": signature.hex(),
            "proof_chain_root": proof_chain_root,
            "proof_chain_path": self.compute_merkle_path(len(self.batch_claims)),
            "batch_id": self.batch_id,
            "batch_index": len(self.batch_claims),
            "batch_log_url": f"https://claims-transparency.{self.institution_id}.edu/batch/{self.batch_id}"
        }
        
        # Add metadata
        claim["signatures"] = [sig_entry]
        claim["verification_receipt"] = {
            "institution": self.institution_id,
            "key_registry_url": f"https://claims-api.{self.institution_id}.edu/.well-known/chrystallum.json",
            "verified_at": timestamp
        }
        
        # Buffer for transparency log
        self.batch_claims.append({
            "claim": claim,
            "facet": facet,
            "source_id": source_id
        })
        
        # Flush batch if it reaches size threshold or time limit
        if len(self.batch_claims) >= 100 or \
           (datetime.utcnow() - self.batch_timestamp).total_seconds() > 300:
            self.flush_batch()
        
        return claim
    
    def compute_batch_merkle_root(self) -> str:
        """Compute Merkle root of current batch claims."""
        if not self.batch_claims:
            return hashlib.sha256(b"empty_batch").hexdigest()
        
        leaves = [
            hashlib.sha256(entry["claim"]["cipher"].encode()).digest()
            for entry in self.batch_claims
        ]
        
        while len(leaves) > 1:
            if len(leaves) % 2 == 1:
                leaves.append(leaves[-1])  # Duplicate last for odd trees
            leaves = [
                hashlib.sha256(leaves[i] + leaves[i+1]).digest()
                for i in range(0, len(leaves), 2)
            ]
        
        return leaves[0].hex() if leaves else hashlib.sha256(b"empty").hexdigest()
    
    def compute_merkle_path(self, leaf_index: int) -> list:
        """Compute Merkle path from leaf to root."""
        # Simplified; full implementation would track tree structure
        # Returns list of sibling hashes needed to compute root
        return ["sibling_hash_1", "sibling_hash_2"]  # Placeholder
    
    def flush_batch(self):
        """Publish batch to transparency log and reset."""
        if not self.batch_claims:
            return
        
        batch_log_entry = {
            "batch_id": self.batch_id,
            "batch_timestamp": self.batch_timestamp.isoformat() + "Z",
            "batch_root": self.compute_batch_merkle_root(),
            "entries": [
                {
                    "claim_id": entry["claim"]["claim_id"],
                    "cipher": entry["claim"]["cipher"],
                    "timestamp": entry["claim"]["signatures"][0]["timestamp"],
                    "facet": entry["facet"],
                    "source_id": entry["source_id"]
                }
                for entry in self.batch_claims
            ]
        }
        
        # POST to transparency log endpoint
        requests.post(
            f"https://claims-transparency.{self.institution_id}.edu/batch",
            json=batch_log_entry,
            timeout=30
        )
        
        logger.info(f"Flushed batch {self.batch_id} with {len(self.batch_claims)} claims")
        self.batch_claims = []
        self.batch_timestamp = None
```

### **X.4.2 Configuration: Institutional Signing Setup**

**New config file: `config_signing.yaml`**

```yaml
# Institutional Signing Configuration
institution:
  name: "University of Oxford"
  domain: "ox.ac.uk"
  endpoint: "https://claims-api.ox.ac.uk"
  contact: "claims-admin@ox.ac.uk"

signing:
  # Path to Ed25519 private key (must be protected by permissions 0600)
  private_key_path: "/etc/chrystallum/secrets/ox_signing_key_2026.pem"
  
  # Key metadata
  key_id: "ox_2026_0a1b"
  algorithm: "Ed25519"
  valid_from: "2026-01-15T00:00:00Z"
  valid_until: "2027-01-15T00:00:00Z"
  rotate_next: "2027-01-01T00:00:00Z"
  
  # Batch settings
  batch_size_threshold: 100  # Flush after 100 claims
  batch_time_threshold_seconds: 300  # Flush after 5 minutes
  
transparency_log:
  # Append-only log of all signed claims
  endpoint: "https://claims-transparency.ox.ac.uk"
  storage_type: "postgresql"  # postgresql, sqlite, s3
  storage_connection: "postgresql://tlog:secret@tlog.ox.ac.uk/chrystallum_tlog"
  
key_registry:
  # Published at .well-known/chrystallum.json
  publish_url: "https://claims-api.ox.ac.uk/.well-known/chrystallum.json"
  include_retired_keys: true  # Keep old keys for historical verification
  retired_key_retention_days: 730  # 2 years
```

### **X.4.3 Deployment: Key Generation & Rotation**

**Script: `scripts/setup_institutional_signing.sh`**

```bash
#!/bin/bash
# Initialize institutional signing authority

INSTITUTION=$1
PRIVATE_KEY_PATH="/etc/chrystallum/secrets/${INSTITUTION}_signing_key.pem"
YEARS_VALID=1

if [ -z "$INSTITUTION" ]; then
    echo "Usage: setup_institutional_signing.sh <institution_domain>"
    exit 1
fi

# Generate Ed25519 private key
openssl genpkey -algorithm ed25519 -out "$PRIVATE_KEY_PATH"
chmod 0600 "$PRIVATE_KEY_PATH"

# Extract public key
PUBKEY_PATH="/etc/chrystallum/secrets/${INSTITUTION}_pubkey.pem"
openssl pkey -in "$PRIVATE_KEY_PATH" -pubout -out "$PUBKEY_PATH"

# Calculate key ID (first 16 chars of key fingerprint)
KEY_ID=$(openssl pkey -pubin -in "$PUBKEY_PATH" -text -noout | \
         grep -A1 "pub:" | tail -1 | \
         tr -d ' :' | \
         head -c 16)

echo "✓ Generated signing key for $INSTITUTION"
echo "  Private key: $PRIVATE_KEY_PATH"
echo "  Public key: $PUBKEY_PATH"
echo "  Key ID: ${INSTITUTION}_2026_${KEY_ID}"
echo ""
echo "Next steps:"
echo "1. Publish public key at: https://${INSTITUTION}/.well-known/chrystallum.json"
echo "2. Configure config_signing.yaml with private_key_path and key_id"
echo "3. Set up transparency log database"
echo "4. Test signing with: python -m chrystallum.signing test-sign"
```

### **X.4.4 Validation: Signature Verification Tests**

**Unit tests in `tests/test_signing.py`**:

```python
import pytest
from chrystallum.signing import verify_claim_signature, InstitutionalSigningAuthority

def test_claim_signature_verification():
    """Test that signed claims can be verified."""
    authority = InstitutionalSigningAuthority(
        private_key_path="tests/fixtures/test_key.pem",
        institution_id="test_institution"
    )
    
    claim = {
        "claim_id": "test_001",
        "cipher": "sha256_abc123",
        "content": {"subject": "Q1048", "object": "Q5"}
    }
    
    # Sign claim
    signed_claim = authority.sign_claim(claim, facet="DIPLOMATIC", source_id="test_src")
    
    # Verify signature
    registry = {
        signed_claim["signatures"][0]["institution_key_id"]: 
            "-----BEGIN PUBLIC KEY-----\n..."
    }
    
    assert verify_claim_signature(signed_claim, registry) is True

def test_signature_tampering_detection():
    """Test that tampered signatures are rejected."""
    # Modify cipher after signing
    signed_claim["cipher"] = "sha256_different"
    
    assert verify_claim_signature(signed_claim, registry) is False

def test_transparency_log_consistency():
    """Test that transparency log consistency proofs work."""
    batch1 = create_batch([claim1, claim2, claim3])
    batch2 = create_batch([claim4, claim5])
    
    # Verify batch1 and batch2 form consistent append-only log
    assert verify_merkle_consistency_proof(
        batch1["batch_root"],
        batch2["batch_root"],
        batch2["batch_proof"]["consistency_proof"],
        tree_size_before=3,
        tree_size_after=5
    ) is True
```

---

## **X.5 Related Decisions**

- **ADR-001** (Appendix U): Content-Only Cipher - signatures separate from cipher
- **ADR-002** (Appendix V): Function-Driven Relationship Catalog - organizing claim types
- **ADR-004** (Appendix W): Canonical 18-Facet System - classifying signed claims
- **Section 6.4**: Cryptographic Verification (cipher + Merkle tree)
- **Appendix R**: Federation Strategy (institutional authorities, confidence layers)

---

## **X.6 References**

- RFC 6962: Certificate Transparency (transparency log pattern)
- Sigsum: Verifiable Transparency Logs (alternative CT design)
- HyperLedger Fabric: Multi-org signing (consortium signing model)
- DNSSEC RFC 4033-4035: Securing DNS (key distribution via DNS TXT)
- Ed25519 (RFC 8037): Elliptic curve signing (cryptographic algorithm)
- Merkle Tree Consistency Proofs: RFC 6962 Section 2.1.4

---

**(End of Appendix X - ADR-005: Federated Claims Signing & Cryptographic Trust Model)**

---

