"""
Entity Cipher Generation for Chrystallum Knowledge Graph

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
    "CONCEPT": "con",  # Abstract concepts
}

FACET_PREFIXES = {
    "ARCHAEOLOGICAL": "arc",
    "ARTISTIC": "art",
    "BIOGRAPHIC": "bio",
    "COMMUNICATION": "com",
    "CULTURAL": "cul",
    "DEMOGRAPHIC": "dem",
    "DIPLOMATIC": "dip",
    "ECONOMIC": "eco",
    "ENVIRONMENTAL": "env",
    "GEOGRAPHIC": "geo",
    "INTELLECTUAL": "int",
    "LINGUISTIC": "lin",
    "MILITARY": "mil",
    "POLITICAL": "pol",
    "RELIGIOUS": "rel",
    "SCIENTIFIC": "sci",
    "SOCIAL": "soc",
    "TECHNOLOGICAL": "tec",
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
        
    Examples:
        >>> generate_entity_cipher("Q1048", "PERSON", "wd")
        'ent_per_Q1048'
        >>> generate_entity_cipher("bn:14792761n", "PERSON", "bn")
        'ent_per_bn:14792761n'
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
        
    Examples:
        >>> generate_faceted_cipher("ent_per_Q1048", "POLITICAL", "Q17167")
        'fent_pol_Q1048_Q17167'
        >>> generate_faceted_cipher("ent_per_Q1048", "MILITARY", "Q17167")
        'fent_mil_Q1048_Q17167'
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

    Args:
        entity_cipher: Tier 1 cipher
        subjectconcept_id: Anchoring SubjectConcept QID

    Returns:
        Dict mapping facet_id → faceted_cipher
        
    Example:
        >>> ciphers = generate_all_faceted_ciphers("ent_per_Q1048", "Q17167")
        >>> len(ciphers)
        18
        >>> ciphers["POLITICAL"]
        'fent_pol_Q1048_Q17167'
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
        
    Example:
        >>> # Jump Caesar from MILITARY to POLITICAL
        >>> target = vertex_jump("ent_per_Q1048", "MILITARY", "POLITICAL", "Q17167")
        >>> target
        'fent_pol_Q1048_Q17167'
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

    Args:
        canonical_name: Entity name
        entity_type: Entity type (PERSON, EVENT, etc.)
        qid: Wikidata QID if known
        temporal: Temporal scope for synthetic ID disambiguation
        search_lang: Language code for BabelNet lookup
        babelnet_api_key: BabelNet API key

    Returns:
        (resolved_id, namespace) tuple
        
    Examples:
        >>> # Has QID
        >>> resolve_entity_id("Julius Caesar", "PERSON", qid="Q1048")
        ('Q1048', 'wd')
        
        >>> # No QID, falls back to synthetic
        >>> id, ns = resolve_entity_id("Obscure Centurion", "PERSON", temporal="-0100")
        >>> ns
        'crys'
        >>> id.startswith('crys:PERSON:')
        True
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

    Args:
        entity_data: Entity dict from SCA
        subjectconcept_id: Anchoring SubjectConcept QID
        babelnet_api_key: Optional BabelNet API key

    Returns:
        Entity data enriched with ciphers
        
    Example:
        >>> entity = {"qid": "Q1048", "label": "Julius Caesar", "entity_type": "PERSON"}
        >>> enriched = enrich_entity_with_ciphers(entity, "Q17167")
        >>> enriched["entity_cipher"]
        'ent_per_Q1048'
        >>> len(enriched["faceted_ciphers"])
        18
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
    entity_data["resolved_id"] = resolved_id

    # Generate Tier 2 faceted ciphers (all 18 facets)
    entity_data["faceted_ciphers"] = generate_all_faceted_ciphers(
        entity_cipher, subjectconcept_id
    )

    return entity_data


# ──────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────

def classify_entity_type(p31_values: List[str]) -> str:
    """
    Determine entity type from P31 (instance of) values.
    
    Args:
        p31_values: List of QIDs from P31 property
        
    Returns:
        Entity type (PERSON, EVENT, PLACE, etc.)
        
    Examples:
        >>> classify_entity_type(["Q5"])
        'PERSON'
        >>> classify_entity_type(["Q11514315"])
        'SUBJECTCONCEPT'
    """
    TYPE_CLASSIFICATIONS = {
        'PERSON': ['Q5'],
        'PLACE': ['Q515', 'Q486972', 'Q2221906', 'Q1549591'],
        'EVENT': ['Q1190554', 'Q198', 'Q178561'],
        'SUBJECTCONCEPT': ['Q11514315', 'Q6428674', 'Q186081'],
        'ORGANIZATION': ['Q43229', 'Q4830453'],
        'WORK': ['Q47461344', 'Q234460'],
    }
    
    for entity_type, qids in TYPE_CLASSIFICATIONS.items():
        if any(p31 in qids for p31 in p31_values):
            return entity_type
    
    return 'CONCEPT'  # Default


if __name__ == "__main__":
    # Example usage
    print("Entity Cipher Examples:\n")
    
    # Tier 1
    ec = generate_entity_cipher("Q1048", "PERSON", "wd")
    print(f"Tier 1: {ec}")
    
    # Tier 2
    fc = generate_faceted_cipher(ec, "POLITICAL", "Q17167")
    print(f"Tier 2: {fc}")
    
    # All facets
    all_fc = generate_all_faceted_ciphers(ec, "Q17167")
    print(f"\nAll 18 faceted ciphers generated:")
    for facet, cipher in sorted(all_fc.items())[:5]:
        print(f"  {facet}: {cipher}")
    print(f"  ... and {len(all_fc)-5} more")
    
    # Vertex jump
    target = vertex_jump(ec, "MILITARY", "POLITICAL", "Q17167")
    print(f"\nVertex jump MILITARY to POLITICAL: {target}")
