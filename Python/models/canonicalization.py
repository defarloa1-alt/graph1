"""
Canonicalization utilities for reproducible claim ciphers

Ensures that claim content hashes (ciphers) are reproducible across systems
by normalizing inputs before hashing. Critical for federated claim identity.

Key transformations:
- Unicode normalization (NFC)
- Whitespace normalization
- Date/time standardization (ISO 8601)
- Floating point precision control
- Deterministic serialization

Usage:
    from canonicalization import canonicalize_claim_content, compute_cipher
    
    canonical = canonicalize_claim_content({
        "content": "Julius Caesar crossed the Rubicon",
        "confidence": 0.95,
        "timestamp": "2024-01-15 10:30:00"
    })
    
    cipher = compute_cipher(canonical)
    # SHA256 hash is now reproducible across systems
"""

import unicodedata
import re
import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Union
import hashlib


# ============================================================================
# Unicode Normalization
# ============================================================================

def normalize_unicode(text: str, form: str = "NFC") -> str:
    """
    Normalize Unicode text to ensure consistent representation.
    
    Args:
        text: Input text (may have different Unicode representations)
        form: Normalization form (NFC, NFD, NFKC, NFKD)
              - NFC: Canonical decomposition followed by canonical composition (RECOMMENDED)
              - NFD: Canonical decomposition
              - NFKC: Compatibility decomposition followed by canonical composition
              - NFKD: Compatibility decomposition
    
    Returns:
        Normalized text
    
    Examples:
        >>> normalize_unicode("café")  # é can be 1 char or e + ́
        'café'  # Always normalized to same form
        
        >>> normalize_unicode("Å")  # Can be U+00C5 or U+0041 U+030A
        'Å'  # Always normalized to same form
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Normalize to requested form (default NFC - most compact)
    normalized = unicodedata.normalize(form, text)
    
    return normalized


# ============================================================================
# Whitespace Normalization
# ============================================================================

def normalize_whitespace(text: str, preserve_paragraphs: bool = True) -> str:
    """
    Normalize whitespace to ensure consistent spacing.
    
    Args:
        text: Input text with potentially inconsistent whitespace
        preserve_paragraphs: If True, preserve paragraph breaks (double newline)
    
    Returns:
        Text with normalized whitespace
    
    Transformations:
        - Replace all whitespace chars (space, tab, NBSP, zero-width, etc.) with regular space
        - Collapse multiple spaces to single space
        - Remove leading/trailing whitespace
        - Optionally preserve paragraph breaks
    
    Examples:
        >>> normalize_whitespace("  Hello   world  ")
        'Hello world'
        
        >>> normalize_whitespace("Line1\\n\\nLine2", preserve_paragraphs=True)
        'Line1\\n\\nLine2'
        
        >>> normalize_whitespace("Line1\\n\\nLine2", preserve_paragraphs=False)
        'Line1 Line2'
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Replace all Unicode whitespace categories with regular space
    # This includes: space, tab, newline, NBSP, zero-width space, etc.
    text = re.sub(r'[\s\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000\uFEFF]+', ' ', text)
    
    if preserve_paragraphs:
        # Restore paragraph breaks (double newline)
        text = re.sub(r' {2,}', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


# ============================================================================
# Date/Time Normalization
# ============================================================================

def normalize_datetime(dt: Union[str, datetime], target_format: str = "ISO8601") -> str:
    """
    Normalize date/time to standard format.
    
    Args:
        dt: Input datetime (string or datetime object)
        target_format: Output format (ISO8601, UNIX_TIMESTAMP)
    
    Returns:
        Standardized datetime string
    
    Examples:
        >>> normalize_datetime("2024-01-15 10:30:00")
        '2024-01-15T10:30:00Z'
        
        >>> normalize_datetime("Jan 15, 2024")
        '2024-01-15T00:00:00Z'
    """
    # Parse if string
    if isinstance(dt, str):
        # Try ISO 8601 first
        try:
            dt_obj = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            # Try common formats
            for fmt in [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%B %d, %Y",
                "%b %d, %Y",
            ]:
                try:
                    dt_obj = datetime.strptime(dt, fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Unable to parse datetime: {dt}")
    else:
        dt_obj = dt
    
    # Format to ISO 8601 (UTC)
    if target_format == "ISO8601":
        return dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif target_format == "UNIX_TIMESTAMP":
        return str(int(dt_obj.timestamp()))
    else:
        raise ValueError(f"Unknown target format: {target_format}")


# ============================================================================
# Numeric Normalization
# ============================================================================

def normalize_float(value: Union[float, str, int], precision: int = 6) -> str:
    """
    Normalize floating point numbers to consistent precision.
    
    Args:
        value: Input number (float, int, or string)
        precision: Number of decimal places (default: 6)
    
    Returns:
        Normalized string representation
    
    Examples:
        >>> normalize_float(0.95)
        '0.950000'
        
        >>> normalize_float("0.9500000000001", precision=2)
        '0.95'
        
        >>> normalize_float(0.123456789, precision=6)
        '0.123457'
    """
    # Convert to Decimal for precise arithmetic
    if isinstance(value, str):
        decimal_value = Decimal(value)
    else:
        decimal_value = Decimal(str(value))
    
    # Round to requested precision
    format_str = f"{{:.{precision}f}}"
    return format_str.format(float(decimal_value))


# ============================================================================
# Deterministic JSON Serialization
# ============================================================================

def canonicalize_dict(data: Dict[str, Any], sort_keys: bool = True) -> Dict[str, Any]:
    """
    Canonicalize dictionary for deterministic serialization.
    
    Args:
        data: Input dictionary
        sort_keys: Sort keys alphabetically (ensures deterministic order)
    
    Returns:
        Canonicalized dictionary with sorted keys and normalized values
    
    Examples:
        >>> canonicalize_dict({"b": 1, "a": 2})
        {'a': 2, 'b': 1}
    """
    result = {}
    
    keys = sorted(data.keys()) if sort_keys else data.keys()
    
    for key in keys:
        value = data[key]
        
        # Recursively canonicalize nested structures
        if isinstance(value, dict):
            result[key] = canonicalize_dict(value, sort_keys=sort_keys)
        elif isinstance(value, list):
            result[key] = [canonicalize_dict(v, sort_keys=sort_keys) if isinstance(v, dict) else v for v in value]
        elif isinstance(value, str):
            # Normalize strings
            result[key] = normalize_unicode(normalize_whitespace(value))
        elif isinstance(value, float):
            # Normalize floats
            result[key] = normalize_float(value, precision=6)
        else:
            result[key] = value
    
    return result


def to_canonical_json(data: Dict[str, Any], **kwargs) -> str:
    """
    Serialize data to canonical JSON string.
    
    Args:
        data: Input data
        **kwargs: Additional arguments for json.dumps
    
    Returns:
        Canonical JSON string (deterministic, reproducible)
    
    Examples:
        >>> to_canonical_json({"content": "test", "confidence": 0.95})
        '{"confidence": "0.950000", "content": "test"}'
    """
    canonical = canonicalize_dict(data, sort_keys=True)
    
    # Serialize with deterministic settings
    return json.dumps(
        canonical,
        sort_keys=True,
        ensure_ascii=False,  # Preserve Unicode characters
        separators=(',', ':'),  # Compact format (no extra spaces)
        **kwargs
    )


# ============================================================================
# Claim Content Canonicalization
# ============================================================================

def canonicalize_claim_content(
    content: str,
    metadata: Dict[str, Any] = None,
    normalize_unicode_form: str = "NFC",
    float_precision: int = 6
) -> Dict[str, Any]:
    """
    Canonicalize claim content for cipher computation.
    
    This is the PRIMARY function for preparing claim content before hashing.
    Ensures reproducible ciphers across systems regardless of input variations.
    
    Args:
        content: Main claim text
        metadata: Optional metadata (facets, relationships, confidence, etc.)
        normalize_unicode_form: Unicode normalization form (NFC recommended)
        float_precision: Precision for floating point numbers
    
    Returns:
        Canonicalized claim data ready for hashing
    
    Example:
        >>> canonicalize_claim_content(
        ...     "Julius Caesar crossed the Rubicon",
        ...     metadata={"confidence": 0.95, "facets": ["military", "political"]}
        ... )
        {
            'content': 'Julius Caesar crossed the Rubicon',
            'metadata': {
                'confidence': '0.950000',
                'facets': ['military', 'political']
            }
        }
    """
    # Normalize content text
    normalized_content = normalize_unicode(content, form=normalize_unicode_form)
    normalized_content = normalize_whitespace(normalized_content, preserve_paragraphs=True)
    
    result = {"content": normalized_content}
    
    # Normalize metadata if provided
    if metadata:
        normalized_metadata = {}
        
        for key, value in sorted(metadata.items()):
            if isinstance(value, str):
                normalized_metadata[key] = normalize_unicode(normalize_whitespace(value))
            elif isinstance(value, float):
                normalized_metadata[key] = normalize_float(value, precision=float_precision)
            elif isinstance(value, datetime):
                normalized_metadata[key] = normalize_datetime(value)
            elif isinstance(value, dict):
                normalized_metadata[key] = canonicalize_dict(value)
            elif isinstance(value, list):
                # Sort lists of primitives for deterministic ordering
                if all(isinstance(x, (str, int, float)) for x in value):
                    normalized_metadata[key] = sorted(value)
                else:
                    normalized_metadata[key] = value
            else:
                normalized_metadata[key] = value
        
        result["metadata"] = normalized_metadata
    
    return result


# ============================================================================
# Cipher Computation
# ============================================================================

def compute_cipher(canonical_data: Dict[str, Any], algorithm: str = "sha256") -> str:
    """
    Compute cryptographic hash (cipher) of canonicalized claim data.
    
    Args:
        canonical_data: Canonicalized claim data from canonicalize_claim_content()
        algorithm: Hash algorithm (sha256, sha512, sha3_256)
    
    Returns:
        Hex-encoded hash (cipher)
    
    Example:
        >>> canonical = canonicalize_claim_content("Test claim")
        >>> cipher = compute_cipher(canonical)
        >>> len(cipher)  # SHA256 produces 64 hex characters
        64
    """
    # Serialize to canonical JSON
    json_bytes = to_canonical_json(canonical_data).encode('utf-8')
    
    # Compute hash
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha512":
        hasher = hashlib.sha512()
    elif algorithm == "sha3_256":
        hasher = hashlib.sha3_256()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    hasher.update(json_bytes)
    return hasher.hexdigest()


# ============================================================================
# Convenience Function
# ============================================================================

def compute_claim_cipher(
    content: str,
    metadata: Dict[str, Any] = None,
    algorithm: str = "sha256"
) -> str:
    """
    One-step function to canonicalize content and compute cipher.
    
    Args:
        content: Claim text
        metadata: Optional metadata
        algorithm: Hash algorithm
    
    Returns:
        Claim cipher (hex-encoded hash)
    
    Example:
        >>> cipher = compute_claim_cipher(
        ...     "Julius Caesar crossed the Rubicon in 49 BCE",
        ...     metadata={"confidence": 0.95}
        ... )
        >>> len(cipher)
        64
    """
    canonical = canonicalize_claim_content(content, metadata=metadata)
    return compute_cipher(canonical, algorithm=algorithm)
