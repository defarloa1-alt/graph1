# LCSH Subject Backbone Implementation Guide
## Complete End-to-End Strategy with Historical Name Binding

**Date:** January 15, 2026  
**Purpose:** Build a canonical subject backbone for Neo4j KG with temporal awareness

---

## Part 1: Core Subject Node Schema

```cypher
// CANONICAL SUBJECT NODE (LCSH-based)
CREATE (subject:Subject {
  // ========== LCSH IDENTIFICATION ==========
  lcsh_id: "sh85036288",                    // Primary key (base ID, no suffix)
  unique_id: "SUBJECT_LCSH_sh85036288",
  
  // ========== PRIMARY LABEL (Current LCSH Form) ==========
  lcsh_heading: "Denali, Mount",            // Authoritative LCSH heading
  label: "Denali, Mount",
  
  // ========== AUTHORITY FEDERATION ==========
  wikidata_qid: "Q131407",                  // Wikidata link
  wikipedia_link: true,                     // Has Wikipedia article
  geographic_entity_id: "geo_denali",      // Link to GeographicEntity
  
  // ========== VARIANT IDENTIFICATION ==========
  variant_lcsh_ids: [],                     // Geographic subdivisions (-781, -780)
  variant_headings: [],                     // Auto-generated geographic forms
  
  // ========== TEMPORAL NAME VARIANTS (HISTORICAL ACCURACY) ==========
  named_variants: [
    {
      name: "Mount McKinley",
      valid_from: 1896,
      valid_until: 2015,
      is_preferred: false,
      is_official: true,
      source: "U.S. Board on Geographic Names",
      reason: "Official name 1896-2015"
    },
    {
      name: "Denali, Mount",
      valid_from: 2015,
      valid_until: 9999,
      is_preferred: true,
      is_official: true,
      source: "U.S. Board on Geographic Names",
      reason: "Official name from 2015 onwards"
    },
    {
      name: "Denali",
      valid_from: 2015,
      valid_until: 9999,
      is_preferred: true,
      is_official: true,
      source: "U.S. Board on Geographic Names",
      reason: "Common name from 2015 onwards"
    }
  ],
  
  // ========== SUBDIVISION METADATA ==========
  subdivision_type: null,                   // geographic, topical, chronological, form
  pattern_category: null,                   // Animals, Diseases, Chemicals, etc.
  
  // ========== AUTHORITY STATUS ==========
  authority_tier: "TIER_1",                 // TIER_1, TIER_2, TIER_3
  authority_confidence: 0.98,               // 0.7-1.0
  is_active: true,                          // Not deprecated
  is_deprecated: false,
  replaced_by: null,                        // LCSH ID of replacement, if deprecated
  
  // ========== LCSH VERSIONING ==========
  created_date: datetime("1896-01-01"),     // First LCSH record
  last_revised: datetime("2015-09-01"),     // Most recent revision
  revision_history: [
    {
      date: "1896-01-01",
      reason: "new",
      label: "Mount McKinley"
    },
    {
      date: "2015-09-01",
      reason: "revised",
      label: "Denali, Mount",
      change_note: "Name changed to match official USGS designation"
    }
  ],
  
  // ========== GEOGRAPHIC METADATA ==========
  gac_code: "n-us-ak",                      // Geographic Area Code
  coordinates: [63.0685, -151.0074],
  country: "United States",
  region: "Alaska",
  
  // ========== FACET SCORES (LLM Assessment) ==========
  facet_scores: {
    PoliticalFacet: 0.3,
    CulturalFacet: 0.5,
    TechnologicalFacet: 0.0,
    ReligiousFacet: 0.0,
    EconomicFacet: 0.2,
    MilitaryFacet: 0.1,
    EnvironmentalFacet: 0.95,                // Mountains, nature
    DemographicFacet: 0.4,                   // Indigenous peoples
    IntellectualFacet: 0.5,
    ScientificFacet: 0.8,                    // Geology, glaciology
    ArtisticFacet: 0.7,                      // Depicted in art
    SocialFacet: 0.4,
    LinguisticFacet: 0.6,                    // Name change itself
    ArchaeologicalFacet: 0.3,
    DiplomaticFacet: 0.0
  },
  
  // ========== AUTHORITY CROSSWALK ==========
  fast_id: "fst01210191",                    // OCLC FAST
  dewey: "915.64",                           // Dewey Decimal (Alaska geography)
  lcc_code: "G398-399",                      // LC Classification (Alaska)
  viaf_id: null,
  gnd_id: null,
  
  // ========== HIERARCHICAL RELATIONSHIPS ==========
  broader_lcsh_id: "sh85000611",             // Alaska (broader term)
  broader_heading: "Alaska",
  narrower_ids: [],                          // Narrower LCSH terms
  related_terms: ["Denali National Park"],
  
  // ========== NAVIGATION METADATA ==========
  lcsh_url: "https://id.loc.gov/authorities/subjects/sh85036288",
  wikidata_url: "https://www.wikidata.org/wiki/Q131407",
  
  // ========== DEPRECATION HANDLING ==========
  status: "active",                          // active, deprecated, dissolved, superseded
  successor_entities: [],                    // If place dissolved/merged
  
  // ========== IMPLEMENTATION TAGS ==========
  marked_for_review: false,
  notes: "Subject was revised 2015 due to official USGS name change. Maintain temporal variants for historical accuracy."
})
```

---

## Part 2: Processing Pipeline

### Step 1: Parse LCSH JSON-LD

```python
import re
from datetime import datetime
from typing import Dict, List, Optional

class LCSHProcessor:
    """Process LCSH JSON-LD records into Subject nodes."""
    
    def __init__(self):
        self.processed = []
        self.skipped = []
        self.flagged = []
    
    def parse_lcsh_id(self, lcsh_id: str) -> Dict:
        """Extract base ID and suffix from LCSH ID."""
        match = re.match(r'(sh\d{8})(-\d+)?', lcsh_id)
        if match:
            return {
                'full_id': lcsh_id,
                'base_id': match.group(1),
                'suffix': match.group(2).lstrip('-') if match.group(2) else None,
                'is_variant': match.group(2) is not None
            }
        return None
    
    def is_deprecated(self, record: Dict) -> bool:
        """Check if subject heading was deleted/canceled."""
        change_notes = record.get('skos:changeNote', [])
        
        for note in change_notes:
            reason = note.get('cs:changeReason', '').lower()
            if reason in ['deleted', 'canceled', 'cancelled']:
                return True
        
        return False
    
    def get_replacement_heading(self, record: Dict) -> Optional[str]:
        """If heading was superseded, get replacement LCSH ID."""
        editorial_note = record.get('skos:editorialNote', '')
        
        patterns = [
            r'replaced by (sh\d{8})',
            r'use (sh\d{8}) instead',
            r'cancelled.*use (sh\d{8})',
            r'superseded by (sh\d{8})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, editorial_note, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_latest_revision(self, record: Dict) -> Dict:
        """Get most recent change."""
        change_notes = record.get('skos:changeNote', [])
        
        sorted_notes = sorted(
            change_notes,
            key=lambda x: x.get('cs:createdDate', ''),
            reverse=True
        )
        
        if sorted_notes:
            latest = sorted_notes[0]
            return {
                'date': latest.get('cs:createdDate'),
                'reason': latest.get('cs:changeReason'),
                'label': record.get('skos:prefLabel')
            }
        
        return None
    
    def build_named_variants(self, record: Dict, lcsh_id: str) -> List[Dict]:
        """
        Extract temporal name variants from LCSH record.
        Uses change history to infer when names were valid.
        """
        variants = []
        change_notes = record.get('skos:changeNote', [])
        alt_labels = record.get('skos:altLabel', [])
        
        # Group changes chronologically
        changes_sorted = sorted(
            change_notes,
            key=lambda x: x.get('cs:createdDate', '')
        )
        
        # Build timeline of name changes
        current_label = record.get('skos:prefLabel')
        
        for i, change in enumerate(changes_sorted):
            date = change.get('cs:createdDate', '2000-01-01')
            reason = change.get('cs:changeReason', '')
            
            # Determine valid date range
            valid_from = date
            valid_until = changes_sorted[i+1].get('cs:createdDate') if i+1 < len(changes_sorted) else '9999-12-31'
            
            if reason == 'new':
                # First creation - infer from external sources or use creation date
                variants.append({
                    'name': current_label,
                    'valid_from': self._extract_year(valid_from),
                    'valid_until': self._extract_year(valid_until),
                    'is_preferred': True,
                    'is_official': True,
                    'source': 'LCSH',
                    'reason': 'Heading created'
                })
            
            elif reason == 'revised':
                # Label changed - old form becomes variant
                for alt in alt_labels:
                    if alt != current_label:
                        variants.append({
                            'name': alt,
                            'valid_from': self._extract_year(valid_from),
                            'valid_until': self._extract_year(valid_until),
                            'is_preferred': False,
                            'is_official': True,
                            'source': 'LCSH',
                            'reason': f'Previous form (revised {date})'
                        })
        
        # Add current label as final variant
        if changes_sorted:
            last_change = changes_sorted[-1]
            variants.append({
                'name': current_label,
                'valid_from': self._extract_year(last_change.get('cs:createdDate', '2000-01-01')),
                'valid_until': 9999,
                'is_preferred': True,
                'is_official': True,
                'source': 'LCSH',
                'reason': 'Current form'
            })
        
        return variants
    
    def _extract_year(self, date_str: str) -> int:
        """Extract year from ISO datetime string."""
        if isinstance(date_str, str):
            try:
                return int(date_str[:4])
            except:
                return 2000
        return 2000
    
    def process_record(self, record: Dict) -> Optional[Dict]:
        """Main processing logic."""
        
        lcsh_id = record.get('@id', '').split('/')[-1]
        parsed_id = self.parse_lcsh_id(lcsh_id)
        
        if not parsed_id:
            self.skipped.append({
                'reason': 'Invalid LCSH ID format',
                'record': record
            })
            return None
        
        # STEP 1: Check if deprecated
        if self.is_deprecated(record):
            replacement = self.get_replacement_heading(record)
            self.skipped.append({
                'reason': 'Deprecated/Canceled',
                'lcsh_id': lcsh_id,
                'replacement': replacement
            })
            return None
        
        # STEP 2: Check if geographic variant
        if parsed_id['is_variant']:
            if parsed_id['suffix'] in ['780', '781']:
                self.processed.append({
                    'action': 'COLLAPSE',
                    'lcsh_id': lcsh_id,
                    'primary_id': parsed_id['base_id'],
                    'variant_heading': record.get('skos:prefLabel')
                })
                return None
        
        # STEP 3: Build subject node
        base_id = parsed_id['base_id']
        subject_node = {
            'lcsh_id': base_id,
            'unique_id': f"SUBJECT_LCSH_{base_id}",
            'lcsh_heading': record.get('skos:prefLabel'),
            'label': record.get('skos:prefLabel'),
            
            # Named variants with temporal bounds
            'named_variants': self.build_named_variants(record, base_id),
            
            # Authority tier
            'authority_tier': self._determine_authority_tier(record),
            
            # Wikidata/Wikipedia federation
            'wikidata_qid': record.get('wikidata_qid'),
            'wikipedia_link': record.get('wikipedia_link', False),
            
            # Change history
            'created_date': self._get_first_change_date(record),
            'last_revised': self._get_latest_change_date(record),
            'is_deprecated': False,
            
            # Geographic metadata
            'gac_code': record.get('skos:notation', {}).get('@value'),
            
            # Broader term
            'broader_lcsh_id': record.get('skos:broader', {}).get('@id', '').split('/')[-1] or None,
        }
        
        self.processed.append(subject_node)
        return subject_node
    
    def _determine_authority_tier(self, record: Dict) -> str:
        """Determine authority confidence tier."""
        # TIER 1: LCSH + Wikidata + Wikipedia
        if record.get('wikidata_qid') and record.get('wikipedia_link'):
            return 'TIER_1'
        # TIER 2: LCSH + Wikidata
        elif record.get('wikidata_qid'):
            return 'TIER_2'
        # TIER 3: LCSH only
        else:
            return 'TIER_3'
    
    def _get_first_change_date(self, record: Dict) -> str:
        """Get creation date from change log."""
        changes = record.get('skos:changeNote', [])
        if changes:
            sorted_changes = sorted(changes, key=lambda x: x.get('cs:createdDate', ''))
            return sorted_changes[0].get('cs:createdDate', '2000-01-01')
        return '2000-01-01'
    
    def _get_latest_change_date(self, record: Dict) -> str:
        """Get most recent revision date."""
        changes = record.get('skos:changeNote', [])
        if changes:
            sorted_changes = sorted(changes, key=lambda x: x.get('cs:createdDate', ''), reverse=True)
            return sorted_changes[0].get('cs:createdDate', '2000-01-01')
        return '2000-01-01'

# Usage
processor = LCSHProcessor()

for record in lcsh_jsonld:
    result = processor.process_record(record)
    if result:
        # Create node in Neo4j
        create_subject_node_cypher(result)

print(f"✅ Processed: {len(processor.processed)}")
print(f"⚠️  Skipped: {len(processor.skipped)}")
```

---

## Part 3: Contextual Query Functions

```python
def resolve_historical_name(db, lcsh_id: str, year: int) -> Optional[str]:
    """
    Query: "What was this subject called in a given year?"
    Returns the historically accurate name for that period.
    """
    query = """
    MATCH (s:Subject {lcsh_id: $lcsh_id})
    UNWIND s.named_variants AS variant
    WHERE $year >= variant.valid_from 
      AND $year <= variant.valid_until
    RETURN variant.name
    ORDER BY variant.is_preferred DESC
    LIMIT 1
    """
    
    result = db.run(query, {
        'lcsh_id': lcsh_id,
        'year': year
    })
    
    if result:
        return result[0]['variant.name']
    return None

def find_subject_by_historical_name(db, name: str, year: int) -> Optional[str]:
    """
    Query: "Find the LCSH ID for a name as it was used in a given year."
    Inverse of above - used during claim ingestion.
    """
    query = """
    MATCH (s:Subject)
    UNWIND s.named_variants AS variant
    WHERE variant.name = $name
      AND $year >= variant.valid_from 
      AND $year <= variant.valid_until
    RETURN s.lcsh_id, variant.is_preferred
    ORDER BY variant.is_preferred DESC
    LIMIT 1
    """
    
    result = db.run(query, {
        'name': name,
        'year': year
    })
    
    if result:
        return result[0]['s.lcsh_id']
    return None

def get_all_names_for_subject(db, lcsh_id: str) -> Dict:
    """
    Query: "All names this subject was ever known by (with date ranges)."
    Useful for disambiguation and historical context.
    """
    query = """
    MATCH (s:Subject {lcsh_id: $lcsh_id})
    RETURN {
        current_name: s.lcsh_heading,
        all_variants: s.named_variants
    }
    """
    
    result = db.run(query, {'lcsh_id': lcsh_id})
    
    if result:
        data = result[0]
        return {
            'current': data['current_name'],
            'history': sorted(
                data['all_variants'],
                key=lambda x: x['valid_from']
            )
        }
    return None

# Usage in claim processing
claim = {
    'text': 'Edmund Hillary climbed Mount McKinley',
    'subject_label': 'Mount McKinley',
    'date': 1952
}

# Find canonical LCSH ID
lcsh_id = find_subject_by_historical_name(db, 'Mount McKinley', 1952)
# Returns: 'sh85036288'

# Verify the name is historically accurate
historical_name = resolve_historical_name(db, lcsh_id, 1952)
# Returns: 'Mount McKinley' ✅

# Show what it's called now
current_name = resolve_historical_name(db, lcsh_id, 2024)
# Returns: 'Denali, Mount'

print(f"✅ Claim correctly uses 1952 name: {historical_name}")
print(f"📖 Subject is now called: {current_name}")
```

---

## Part 4: Neo4j Index Strategy

```cypher
// Create indexes for efficient querying

// PRIMARY KEY INDEX
CREATE INDEX subject_lcsh_id FOR (s:Subject) ON (s.lcsh_id);

// FEDERATION INDEXES
CREATE INDEX subject_wikidata FOR (s:Subject) ON (s.wikidata_qid);
CREATE INDEX subject_unique_id FOR (s:Subject) ON (s.unique_id);

// TEMPORAL QUERIES (for historical name resolution)
// Note: Named variants are stored as properties, not separate nodes
// So we can't index into the array directly with standard Neo4j
// Use UNWIND in queries instead (shown above)

// FACET SCORING INDEXES (for agent routing)
CREATE INDEX subject_authority_tier FOR (s:Subject) ON (s.authority_tier);
CREATE INDEX subject_deprecated FOR (s:Subject) ON (s.is_deprecated);

// HIERARCHICAL NAVIGATION
CREATE INDEX subject_broader FOR (s:Subject) ON (s.broader_lcsh_id);

// GAG CODE (for geographic grouping)
CREATE INDEX subject_gac_code FOR (s:Subject) ON (s.gac_code);
```

---

## Part 5: Agent Routing Rules

```cypher
// Route to agents based on facet scores

// ENVIRONMENTAL AGENT (mountains, geography, climate)
MATCH (s:Subject)
WHERE s.facet_scores.EnvironmentalFacet > 0.75
SET s.assigned_agents = ['EnvironmentalAgent', 'GeographicAgent']
CREATE (s)-[:ROUTED_TO {priority: 1}]->(:Agent {type: 'EnvironmentalAgent'});

// SCIENTIFIC AGENT (geology, glaciology)
MATCH (s:Subject)
WHERE s.facet_scores.ScientificFacet > 0.75
SET s.assigned_agents = s.assigned_agents + ['ScientificAgent']
CREATE (s)-[:ROUTED_TO {priority: 2}]->(:Agent {type: 'ScientificAgent'});

// DEMOGRAPHIC AGENT (Indigenous peoples, settlement)
MATCH (s:Subject)
WHERE s.facet_scores.DemographicFacet > 0.5
SET s.assigned_agents = s.assigned_agents + ['DemographicAgent'];

// ARTIST AGENT (depicted in art, cultural significance)
MATCH (s:Subject)
WHERE s.facet_scores.ArtisticFacet > 0.5
SET s.assigned_agents = s.assigned_agents + ['ArtisticAgent'];
```

---

## Part 6: Sample Data Insert

```cypher
// Mount Denali / Mount McKinley
CREATE (denali:Subject {
  lcsh_id: "sh85036288",
  unique_id: "SUBJECT_LCSH_sh85036288",
  lcsh_heading: "Denali, Mount",
  label: "Denali, Mount",
  
  named_variants: [
    {
      name: "Mount McKinley",
      valid_from: 1896,
      valid_until: 2015,
      is_preferred: false,
      is_official: true,
      source: "USGS",
      reason: "Official name 1896-2015"
    },
    {
      name: "Denali, Mount",
      valid_from: 2015,
      valid_until: 9999,
      is_preferred: true,
      is_official: true,
      source: "USGS",
      reason: "Official name from 2015 onwards"
    }
  ],
  
  authority_tier: "TIER_1",
  authority_confidence: 0.98,
  is_deprecated: false,
  created_date: datetime("1896-01-01"),
  last_revised: datetime("2015-09-01"),
  
  gac_code: "n-us-ak",
  coordinates: [63.0685, -151.0074],
  country: "United States",
  region: "Alaska",
  
  facet_scores: {
    EnvironmentalFacet: 0.95,
    ScientificFacet: 0.8,
    ArtisticFacet: 0.7,
    DemographicFacet: 0.4,
    CulturalFacet: 0.5
  },
  
  dewey: "915.64",
  lcc_code: "G398-399",
  broader_lcsh_id: "sh85000611",
  
  assigned_agents: ["EnvironmentalAgent", "ScientificAgent", "ArtisticAgent"]
});

// Broader term: Alaska
CREATE (alaska:Subject {
  lcsh_id: "sh85000611",
  lcsh_heading: "Alaska",
  label: "Alaska"
});

// Link them
CREATE (denali)-[:NARROWER_OF]->(alaska);

// Create Period for Mount McKinley era
CREATE (era_mckinley:Period {
  start_year: 1896,
  end_year: 2015,
  label: "Mount McKinley Era",
  description: "The period when the mountain was officially called Mount McKinley"
});

// Link subject to period
CREATE (denali)-[:NAMED_AS_DURING {
  name: "Mount McKinley"
}]->(era_mckinley);
```

---

## Part 7: Testing & Validation

```python
# Test 1: Historical name resolution
assert resolve_historical_name(db, "sh85036288", 1952) == "Mount McKinley"
assert resolve_historical_name(db, "sh85036288", 2024) == "Denali, Mount"

# Test 2: Find subject by historical name
assert find_subject_by_historical_name(db, "Mount McKinley", 1952) == "sh85036288"
assert find_subject_by_historical_name(db, "Mount McKinley", 2016) is None  # Not valid after 2015

# Test 3: Authority tier
result = db.run("MATCH (s:Subject {lcsh_id: 'sh85036288'}) RETURN s.authority_tier")
assert result[0]['s.authority_tier'] == 'TIER_1'

# Test 4: Variant counting
result = db.run("""
  MATCH (s:Subject {lcsh_id: 'sh85036288'})
  RETURN size(s.named_variants) as count
""")
assert result[0]['count'] >= 2

print("✅ All tests passed!")
```

---

## Summary: Your Implementation Checklist

- [ ] **Parse LCSH JSON-LD** using LCSHProcessor class
- [ ] **Build temporal variants** from change history
- [ ] **Collapse geographic variants** (-781, -780 suffixes)
- [ ] **Skip deprecated headings** (deleted/canceled status)
- [ ] **Create Subject nodes** with all required properties
- [ ] **Add indexes** for efficient querying
- [ ] **Implement contextual queries** (resolve_historical_name, etc.)
- [ ] **Set up agent routing** based on facet scores
- [ ] **Test historical accuracy** with date-sensitive queries

---

## Result: A Knowledge Graph That Knows History

Your system can now:

✅ **Store subjects with temporal accuracy**  
✅ **Answer "what was it called in 1952?"**  
✅ **Route claims to the right agents**  
✅ **Preserve historical authenticity**  
✅ **Track authority changes**  
✅ **Support library section discovery**  

The attached guide is not yet SKOS-complete; it needs explicit field mappings from the JSON‑LD. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)

Here is the **schema section you can paste into `lcsh-implementation-guide.md`** under “Core Subject Node Schema” to make it SKOS-aware:

***

## SKOS‑Derived Subject Schema (from LCSH JSON‑LD)

Every `skos:Concept` in `subjects_sample_valid.jsonld` becomes one `Subject` node with these fields. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)

### Identification

- `lcsh_uri`  
  - Source: record `@id` (e.g. `http://id.loc.gov/authorities/subjects/sh00000016`). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `lcsh_id`  
  - Source: last segment of `lcsh_uri` (e.g. `sh00000016`, `sh00000016-781`). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `base_lcsh_id`  
  - Logic: `lcsh_id.split('-')[0]` (e.g. `sh00000016`). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `suffix`  
  - Logic: part after `-` if present (e.g. `"781"`), otherwise `null`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)

### Labeling (SKOS + SKOS‑XL)

- `pref_label_en`  
  - Source: `skos:prefLabel` where `@language = "en"`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `pref_labels` (array)  
  - Source: all `skos:prefLabel` objects:  
    - `[{ language, value }]` from `@language`, `@value`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `alt_labels` (array)  
  - Source: all `skos:altLabel.@value` (any language). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `xl_alt_labels` (array)  
  - Source: all `skosxl:altLabel.skosxl:literalForm`:  
    - `[{ language, value }]`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)

### Scheme membership and notations

- `in_scheme_uri`  
  - Source: `skos:inScheme.@id` (typically `http://id.loc.gov/authorities/subjects`). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `notations` (array)  
  - Source: each `skos:notation` object:  
    - `datatype` ← `@type` (e.g. `http://id.loc.gov/datatypes/codes/gac`).  
    - `value` ← `@value` (e.g. `"n-us-or"`, `"s-ag---"`). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)

### Hierarchy (for second‑pass edges)

- `broader_ids` (array)  
  - Source: each `skos:broader.@id`, trimmed to `sh…` where applicable. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `narrower_ids` (array)  
  - Source: any `skos:narrower.@id` (not in this small sample but present in full dumps).  
- `related_ids` (array)  
  - Source: any `skos:related.@id`.  

These arrays will later become `:BROADER_THAN`, `:NARROWER_THAN`, `:RELATED_TO` relationships.

### Notes and documentation

- `editorial_notes` (array of strings)  
  - Source: all `skos:editorialNote` values, e.g.  
    - `"Resource automatically generated from LCCN sh00000016"`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `scope_notes` (array)  
  - Source: `skos:scopeNote` (if present in the full data).  
- `history_notes` (array)  
  - Source: `skos:historyNote` (if present).  

These stay as properties; individual notes can be reified later if needed.

### Change history (cs:ChangeSet)

From each `skos:changeNote` blank node of type `cs:ChangeSet`: [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)

- `change_sets` (array of objects):  
  - `id` ← blank node `@id`.  
  - `type` ← `@type` (e.g. `cs:ChangeSet`).  
  - `change_reason` ← `cs:changeReason` (`"new"`, `"revised"`, etc.).  
  - `created` ← `cs:createdDate.@value` (ISO datetime).  
  - `creator_uri` ← `cs:creatorName.@id` (e.g. DLC organization URI).  
  - `subject_of_change_uri` ← `cs:subjectOfChange.@id`.  

Derived convenience fields:

- `created_date` ← earliest `created` where `change_reason = "new"`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `last_revised_date` ← latest `created` where `change_reason = "revised"`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `is_deprecated` ← `true` if any `change_reason ∈ {"deleted","canceled","cancelled"}`, else `false`.  

### Geographic variant detection (‑781, auto‑generated entries)

- `is_geographic_variant` (bool)  
  - `true` if:  
    - `suffix` is `"781"` (or `"780"`), **or**  
    - any `editorial_notes` contains `"Resource automatically generated from LCCN"`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)
- `primary_lcsh_id`  
  - If `is_geographic_variant = true`, set to `base_lcsh_id`; else `null`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)

When loading the full dataset:

- Group concepts by `base_lcsh_id`.  
- For the **base** concept (no suffix), attach:  
  - `variant_lcsh_ids` ← IDs of all grouped variants.  
  - `variant_headings` ← their `pref_label_en` (or raw `skos:prefLabel`) values. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/0a7d0609-d586-49c1-b805-f4dff83e2aeb/subjects_sample_valid.jsonld)

Variant concepts can be dropped after consolidation or later modeled as separate `NameVariant` nodes.

### Named variants with temporal spans

To support historically accurate naming:

- `named_variants` (array of objects):  
  - `name` ← label form (from `pref_labels`, `alt_labels`, `xl_alt_labels`, or external sources).  
  - `valid_from_year` / `valid_until_year` ← derived from `change_sets` and any curated historical info.  
  - `is_preferred` ← preferred in that period.  
  - `is_official` ← endorsed by an authority.  
  - `source` ← e.g. `"LCSH"`, `"USGS"`.  
  - `reason` ← e.g. `"Heading created"`, `"Revised 2011"`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/bdc9e5b9-8d9b-4d0b-9b10-9e9c84799210/unified-mapping-with-reification.md)

Initial script strategy:

- Use earliest `change_sets` entry to seed the initial variant.  
- Use latest revision to seed the current variant.  
- Allow manual enrichment for known name changes (e.g. McKinley/Denali).

### Authority crosswalk placeholders

Kept from the earlier guide, filled by other pipelines:

- `wikidata_qid`  
- `wikipedia_url`  
- `fast_id`  
- `dewey`  
- `lcc_code`  

### Facet scores and tiers

Also from earlier work:

- `facet_scores` object (PoliticalFacet, MilitaryFacet, etc.). [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/bdc9e5b9-8d9b-4d0b-9b10-9e9c84799210/unified-mapping-with-reification.md)
- `authority_tier` (`"TIER_1"`, `"TIER_2"`, `"TIER_3"`) based on LCSH + Wikidata + Wikipedia.  
- `authority_confidence` (0.7–1.0).  

***

If you paste this section into `lcsh-implementation-guide.md` (replacing or augmenting the existing Part 1 schema block), you will have an implementation guide that fully reflects the SKOS JSON‑LD fields and is ready to drive your final loader script. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/fbe637ae-17f5-4351-9926-c42f950ad1bf/lcsh-implementation-guide.md)
