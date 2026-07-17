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
      vertex_jump,
      construct_cipher_from_text,  # LLM-friendly interface
      construct_vertex_jump
  )

LLM-Friendly Natural Language Interface:
  # Direct cipher construction from text
  result = construct_cipher_from_text(
      "Julius Caesar",
      facet_hint="political",
      subjectconcept_id="Q17167"
  )
  # Returns ready-to-use Cypher query for vertex jumping
"""

import hashlib
import requests
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


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
    "STUB": "stb",     # Backlink candidates awaiting resolution
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

# Canonical properties for content-hash generation (ADR 023)
CANONICAL_PROPERTIES = {
    "PERSON": ['name', 'birth_date', 'birth_place'],
    "PLACE": ['name', 'latitude', 'longitude', 'feature_type'],
    "EVENT": ['name', 'date', 'location', 'participants'],
    "PERIOD": ['name', 'start_date', 'end_date', 'geographic_scope'],
    "CONCEPT": ['label', 'definition', 'domain'],
    "WORK": ['title', 'author', 'date', 'work_type'],
    "SUBJECTCONCEPT": ['label', 'definition', 'domain'],
    "ORGANIZATION": ['name', 'founded_date', 'location'],
    "MATERIAL": ['name', 'composition', 'source'],
    "OBJECT": ['name', 'type', 'provenance'],
}


# ──────────────────────────────────────────────────────
# DATE NORMALIZATION (Year-level precision, ADR 023)
# ──────────────────────────────────────────────────────

def normalize_year(date_str: Optional[str]) -> str:
    """
    Normalize date to year-level precision for IGAR temporal validation.
    
    Format: ISO year with BCE as negative, circa with ~
    
    Args:
        date_str: Date string (various formats)
    
    Returns:
        Normalized year string
        
    Examples:
        >>> normalize_year("-49-01-10")
        '-49'
        >>> normalize_year("49 BCE")
        '-49'
        >>> normalize_year("circa 100 CE")
        '~100'
        >>> normalize_year(None)
        ''
    """
    if not date_str:
        return ""
    
    date_str = str(date_str).strip().lower()
    
    # Already in year format
    if date_str.startswith('-') and date_str[1:].replace('~','').isdigit():
        return date_str.split('-')[0] + '-' + date_str.split('-')[1][:len(date_str.split('-')[1].split('-')[0])]
    
    # Circa handling
    if 'circa' in date_str or date_str.startswith('~'):
        year = ''.join(c for c in date_str if c.isdigit())
        if year:
            return f"~{year}" if 'bce' in date_str or 'bc' in date_str else f"~{year}"
    
    # BCE/BC handling
    if 'bce' in date_str or 'bc' in date_str:
        year = ''.join(c for c in date_str if c.isdigit())
        if year:
            return f"-{year}"
    
    # Extract year from ISO date
    if '-' in date_str:
        parts = date_str.split('-')
        if len(parts) >= 2 and parts[1].isdigit():
            return f"-{parts[1]}"  # BCE
        elif parts[0].isdigit():
            return parts[0]  # CE
    
    # Plain year
    if date_str.isdigit():
        return date_str
    
    return ""


# ──────────────────────────────────────────────────────
# TIER 1: ENTITY CIPHER
# ──────────────────────────────────────────────────────

def generate_entity_cipher(
    entity_type: str,
    qid: Optional[str] = None,
    canonical_properties: Optional[Dict] = None,
    namespace: str = "wd"
) -> str:
    """
    Generate Tier 1 entity cipher — cross-subgraph join key.
    
    Priority:
    1. If qid provided: ent_{type_prefix}_{qid}
    2. If canonical_properties provided: ent_{type_prefix}_{content_hash}
    3. Otherwise: raise ValueError

    Args:
        entity_type: Canonical type (PERSON, EVENT, PLACE, etc.)
        qid: Wikidata QID if available
        canonical_properties: Dict of identifying properties for content hash
        namespace: Authority source ("wd", "bn", "crys")

    Returns:
        Entity cipher string (e.g., "ent_per_Q1048" or "ent_evt_a4f8c2d1...")
        
    Examples:
        >>> # With QID
        >>> generate_entity_cipher("PERSON", qid="Q1048")
        'ent_per_Q1048'
        
        >>> # Without QID, content hash
        >>> props = {'name': 'Caesar crossing Rubicon', 'date': '-49-01-10', 
        ...          'location': 'Rubicon River', 'participants': 'Caesar'}
        >>> cipher = generate_entity_cipher("EVENT", canonical_properties=props)
        >>> cipher.startswith('ent_evt_')
        True
    """
    entity_type_upper = entity_type.upper()
    if entity_type_upper not in ENTITY_TYPE_PREFIXES:
        raise ValueError(
            f"Unknown entity_type: {entity_type}. "
            f"Valid: {list(ENTITY_TYPE_PREFIXES.keys())}"
        )

    prefix = ENTITY_TYPE_PREFIXES[entity_type_upper]
    
    # Priority 1: QID
    if qid:
        return f"ent_{prefix}_{qid}"
    
    # Priority 2: Content hash
    if canonical_properties:
        hash_id = generate_content_hash(entity_type_upper, canonical_properties)
        return f"ent_{prefix}_{hash_id}"
    
    raise ValueError("Must provide either qid or canonical_properties")


def generate_content_hash(entity_type: str, canonical_properties: Dict) -> str:
    """
    Generate content-based hash for entities without QIDs.
    
    Uses SHA256 hash of canonical properties (sorted for determinism).
    
    Args:
        entity_type: Entity type (PERSON, EVENT, etc.)
        canonical_properties: Dict of identifying properties
    
    Returns:
        First 16 characters of SHA256 hash
        
    Example:
        >>> props = {'name': 'Caesar crossing Rubicon', 'date': '-49', 
        ...          'location': 'Rubicon', 'participants': 'Caesar'}
        >>> hash_id = generate_content_hash('EVENT', props)
        >>> len(hash_id)
        16
        >>> hash_id == generate_content_hash('EVENT', props)
        True
    """
    if entity_type not in CANONICAL_PROPERTIES:
        raise ValueError(f"No canonical properties defined for {entity_type}")
    
    keys = CANONICAL_PROPERTIES[entity_type]
    
    # Extract values in sorted key order for determinism
    values = []
    for key in sorted(keys):
        value = canonical_properties.get(key, '')
        # Normalize dates if present
        if 'date' in key.lower() and value:
            value = normalize_year(value)
        values.append(str(value))
    
    # Generate hash
    content = '|'.join(values).encode('utf-8')
    hash_digest = hashlib.sha256(content).hexdigest()[:16]
    
    return hash_digest


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
# CIPHER CONSTRUCTOR (LLM-Friendly Natural Language Interface)
# ──────────────────────────────────────────────────────

def construct_cipher_from_text(
    entity_name: str,
    facet_hint: Optional[str] = None,
    subjectconcept_id: Optional[str] = None,
    entity_type_hint: Optional[str] = None
) -> Dict:
    """
    Construct cipher from natural language description.
    
    This is the LLM-friendly interface for vertex jumping.
    Enables: "Caesar political Roman Republic" → direct cipher → direct query
    
    Args:
        entity_name: Natural language entity name (e.g., "Julius Caesar")
        facet_hint: Optional facet keyword (e.g., "political", "military")
        subjectconcept_id: Optional SubjectConcept QID (e.g., "Q17167")
        entity_type_hint: Optional type hint (e.g., "person", "event")
    
    Returns:
        Dict with cipher info and ready-to-use Cypher query
        
    Examples:
        >>> # Simple entity lookup
        >>> result = construct_cipher_from_text("Julius Caesar")
        >>> result['entity_cipher']
        'ent_per_Q1048'
        
        >>> # Faceted lookup
        >>> result = construct_cipher_from_text(
        ...     "Julius Caesar",
        ...     facet_hint="political",
        ...     subjectconcept_id="Q17167"
        ... )
        >>> result['faceted_cipher']
        'fent_pol_Q1048_Q17167'
        >>> result['cypher_query']
        'MATCH (n {faceted_cipher: "fent_pol_Q1048_Q17167"}) RETURN n'
    """
    # Step 1: Resolve entity to QID
    qid = _resolve_entity_name_to_qid(entity_name)
    
    if not qid:
        return {
            'success': False,
            'error': f'Could not resolve entity: {entity_name}',
            'entity_name': entity_name
        }
    
    # Step 2: Determine entity type
    entity_type = entity_type_hint or _infer_entity_type_from_qid(qid)
    
    # Step 3: Generate Tier 1 cipher
    entity_cipher = generate_entity_cipher(entity_type, qid=qid)
    
    result = {
        'success': True,
        'entity_name': entity_name,
        'qid': qid,
        'entity_type': entity_type,
        'entity_cipher': entity_cipher,
        'tier1_cypher': f'MATCH (n {{entity_cipher: "{entity_cipher}"}}) RETURN n'
    }
    
    # Step 4: Generate Tier 2 cipher (if context provided)
    if facet_hint and subjectconcept_id:
        facet = _normalize_facet_hint(facet_hint)
        if facet:
            faceted_cipher = generate_faceted_cipher(
                entity_cipher, 
                facet, 
                subjectconcept_id
            )
            result.update({
                'facet': facet,
                'subjectconcept_id': subjectconcept_id,
                'faceted_cipher': faceted_cipher,
                'tier2_cypher': f'MATCH (n {{faceted_cipher: "{faceted_cipher}"}}) RETURN n',
                'recommended_query': f'MATCH (n {{faceted_cipher: "{faceted_cipher}"}}) RETURN n'
            })
        else:
            result['facet_warning'] = f'Could not normalize facet hint: {facet_hint}'
    
    # If no faceted context, recommend Tier 1 query
    if 'recommended_query' not in result:
        result['recommended_query'] = result['tier1_cypher']
    
    return result


def construct_vertex_jump(
    from_entity: str,
    to_entity: str,
    via_facet: str,
    subjectconcept_id: str
) -> Dict:
    """
    Construct a cross-entity vertex jump within a facet.
    
    Args:
        from_entity: Source entity name (e.g., "Julius Caesar")
        to_entity: Target entity name (e.g., "Pompey")
        via_facet: Facet to jump through (e.g., "political")
        subjectconcept_id: SubjectConcept context
    
    Returns:
        Dict with both ciphers and jump query
        
    Example:
        >>> jump = construct_vertex_jump(
        ...     "Julius Caesar",
        ...     "Pompey",
        ...     "political",
        ...     "Q17167"
        ... )
        >>> jump['cypher_query']
        'MATCH (from {faceted_cipher: "fent_pol_Q1048_Q17167"})-[r]-(to {faceted_cipher: "fent_pol_Q168811_Q17167"}) RETURN from, r, to'
    """
    # Resolve both entities
    from_result = construct_cipher_from_text(from_entity, via_facet, subjectconcept_id)
    to_result = construct_cipher_from_text(to_entity, via_facet, subjectconcept_id)
    
    if not from_result['success'] or not to_result['success']:
        return {
            'success': False,
            'error': 'Could not resolve entities',
            'from_result': from_result,
            'to_result': to_result
        }
    
    # Build jump query
    from_cipher = from_result.get('faceted_cipher', from_result['entity_cipher'])
    to_cipher = to_result.get('faceted_cipher', to_result['entity_cipher'])
    
    return {
        'success': True,
        'from_entity': from_entity,
        'to_entity': to_entity,
        'from_cipher': from_cipher,
        'to_cipher': to_cipher,
        'facet': _normalize_facet_hint(via_facet),
        'subjectconcept_id': subjectconcept_id,
        'cypher_query': (
            f'MATCH (from {{faceted_cipher: "{from_cipher}"}})'
            f'-[r]-(to {{faceted_cipher: "{to_cipher}"}}) '
            f'RETURN from, r, to'
        )
    }


def _resolve_entity_name_to_qid(entity_name: str) -> Optional[str]:
    """
    Resolve natural language entity name to Wikidata QID.
    
    Uses Wikidata search API.
    
    Args:
        entity_name: Natural language name (e.g., "Julius Caesar")
    
    Returns:
        QID if found, None otherwise
    """
    try:
        # Wikidata search API
        url = "https://www.wikidata.org/w/api.php"
        params = {
            'action': 'wbsearchentities',
            'search': entity_name,
            'language': 'en',
            'format': 'json',
            'limit': 1
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('search'):
                return data['search'][0]['id']
    except Exception as e:
        logger.warning(f"Wikidata search failed for '{entity_name}': {e}")
    
    return None


def _infer_entity_type_from_qid(qid: str) -> str:
    """
    Infer entity type from Wikidata QID by querying P31 (instance of).
    
    Args:
        qid: Wikidata QID
    
    Returns:
        Entity type (PERSON, PLACE, EVENT, etc.)
    """
    try:
        # Wikidata SPARQL query for P31
        url = "https://query.wikidata.org/sparql"
        query = f"""
        SELECT ?type WHERE {{
          wd:{qid} wdt:P31 ?type .
        }}
        LIMIT 5
        """
        
        response = requests.get(
            url,
            params={'query': query, 'format': 'json'},
            timeout=5,
            headers={'User-Agent': 'Chrystallum/1.0'}
        )
        
        if response.status_code == 200:
            data = response.json()
            p31_values = [
                item['type']['value'].split('/')[-1] 
                for item in data['results']['bindings']
            ]
            return classify_entity_type(p31_values)
    except Exception as e:
        logger.warning(f"Entity type inference failed for {qid}: {e}")
    
    # Default fallback
    return 'CONCEPT'


def _normalize_facet_hint(facet_hint: str) -> Optional[str]:
    """
    Normalize natural language facet hint to canonical facet ID.
    
    Args:
        facet_hint: Natural language facet (e.g., "political", "military affairs")
    
    Returns:
        Canonical facet ID or None
        
    Examples:
        >>> _normalize_facet_hint("political")
        'POLITICAL'
        >>> _normalize_facet_hint("military affairs")
        'MILITARY'
        >>> _normalize_facet_hint("archaeology")
        'ARCHAEOLOGICAL'
    """
    hint_lower = facet_hint.lower().strip()
    
    # Direct matches
    FACET_KEYWORDS = {
        'archaeological': 'ARCHAEOLOGICAL',
        'archaeology': 'ARCHAEOLOGICAL',
        'artistic': 'ARTISTIC',
        'art': 'ARTISTIC',
        'biographic': 'BIOGRAPHIC',
        'biographical': 'BIOGRAPHIC',
        'biography': 'BIOGRAPHIC',
        'bio': 'BIOGRAPHIC',
        'communication': 'COMMUNICATION',
        'communications': 'COMMUNICATION',
        'cultural': 'CULTURAL',
        'culture': 'CULTURAL',
        'demographic': 'DEMOGRAPHIC',
        'demographics': 'DEMOGRAPHIC',
        'population': 'DEMOGRAPHIC',
        'diplomatic': 'DIPLOMATIC',
        'diplomacy': 'DIPLOMATIC',
        'economic': 'ECONOMIC',
        'economics': 'ECONOMIC',
        'economy': 'ECONOMIC',
        'environmental': 'ENVIRONMENTAL',
        'environment': 'ENVIRONMENTAL',
        'geographic': 'GEOGRAPHIC',
        'geographical': 'GEOGRAPHIC',
        'geography': 'GEOGRAPHIC',
        'geo': 'GEOGRAPHIC',
        'intellectual': 'INTELLECTUAL',
        'ideas': 'INTELLECTUAL',
        'linguistic': 'LINGUISTIC',
        'language': 'LINGUISTIC',
        'languages': 'LINGUISTIC',
        'military': 'MILITARY',
        'warfare': 'MILITARY',
        'war': 'MILITARY',
        'political': 'POLITICAL',
        'politics': 'POLITICAL',
        'religious': 'RELIGIOUS',
        'religion': 'RELIGIOUS',
        'scientific': 'SCIENTIFIC',
        'science': 'SCIENTIFIC',
        'social': 'SOCIAL',
        'society': 'SOCIAL',
        'technological': 'TECHNOLOGICAL',
        'technology': 'TECHNOLOGICAL',
        'tech': 'TECHNOLOGICAL',
    }
    
    return FACET_KEYWORDS.get(hint_lower)


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
