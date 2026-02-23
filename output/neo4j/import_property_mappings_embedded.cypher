// ============================================================================
// PROPERTY FACET MAPPING - NEO4J IMPORT (Embedded Data)
// ============================================================================
// Generated from: property_facet_mapping_HYBRID.csv
// Total properties: 500
// Coverage: 100%
// For Neo4j Aura (no CSV file import)
// ============================================================================

// STEP 1: CREATE INDEXES
CREATE INDEX property_mapping_pid_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.property_id);
CREATE INDEX property_mapping_facet_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.primary_facet);
CREATE INDEX property_mapping_confidence_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.confidence);

// STEP 2: CREATE PROPERTY MAPPING NODES

// 1. P179 - part of the series
CREATE (:PropertyMapping {
  property_id: 'P179',
  property_label: 'part of the series',
  property_description: 'series which contains the subject',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 2. P180 - depicts
CREATE (:PropertyMapping {
  property_id: 'P180',
  property_label: 'depicts',
  property_description: 'entity visually depicted in an image, literarily described in a work, or otherwise incorporated into an audiovisual or other medium; see also P921, \'main subject\'',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'CULTURAL,INTELLECTUAL',
  all_facets: 'ARTISTIC,CULTURAL,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 3. P181 - taxon range map image
CREATE (:PropertyMapping {
  property_id: 'P181',
  property_label: 'taxon range map image',
  property_description: 'range map of a taxon',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'ENVIRONMENTAL',
  all_facets: 'SCIENTIFIC,ENVIRONMENTAL',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 4. P183 - endemic to
CREATE (:PropertyMapping {
  property_id: 'P183',
  property_label: 'endemic to',
  property_description: 'sole location or habitat type where the taxon lives',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'ENVIRONMENTAL',
  all_facets: 'SCIENTIFIC,ENVIRONMENTAL',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 5. P184 - doctoral advisor
CREATE (:PropertyMapping {
  property_id: 'P184',
  property_label: 'doctoral advisor',
  property_description: 'person who supervised the doctorate or PhD thesis of the subject',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 6. P185 - doctoral student
CREATE (:PropertyMapping {
  property_id: 'P185',
  property_label: 'doctoral student',
  property_description: 'doctoral student(s) of a professor',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 7. P186 - made from material
CREATE (:PropertyMapping {
  property_id: 'P186',
  property_label: 'made from material',
  property_description: 'material the subject or the object is made of or derived from (do not confuse with P10672 which is used for processes)',
  primary_facet: 'ARCHAEOLOGICAL',
  secondary_facets: 'CULTURAL,TECHNOLOGICAL',
  all_facets: 'ARCHAEOLOGICAL,CULTURAL,TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 8. P189 - location of discovery
CREATE (:PropertyMapping {
  property_id: 'P189',
  property_label: 'location of discovery',
  property_description: 'where the item was located when discovered',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'ARCHAEOLOGICAL,SCIENTIFIC',
  all_facets: 'GEOGRAPHIC,ARCHAEOLOGICAL,SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 9. P190 - twinned administrative body
CREATE (:PropertyMapping {
  property_id: 'P190',
  property_label: 'twinned administrative body',
  property_description: 'twin towns, sister cities, twinned municipalities and other localities that have a partnership or cooperative agreement, either legally or informally acknowledged by their governments',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 10. P193 - main building contractor
CREATE (:PropertyMapping {
  property_id: 'P193',
  property_label: 'main building contractor',
  property_description: 'the main organization (or person) responsible for construction of this structure or building',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'CULTURAL',
  all_facets: 'TECHNOLOGICAL,CULTURAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 11. P194 - legislative body
CREATE (:PropertyMapping {
  property_id: 'P194',
  property_label: 'legislative body',
  property_description: 'legislative body governing this entity; political institution with elected representatives, such as a parliament/legislature or council',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 12. P195 - collection
CREATE (:PropertyMapping {
  property_id: 'P195',
  property_label: 'collection',
  property_description: 'art, museum, archival, or bibliographic collection of which the subject is part (item is in the collection of X)',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 13. P196 - minor planet group
CREATE (:PropertyMapping {
  property_id: 'P196',
  property_label: 'minor planet group',
  property_description: 'is in grouping of minor planets according to similar orbital characteristics',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 14. P197 - adjacent station
CREATE (:PropertyMapping {
  property_id: 'P197',
  property_label: 'adjacent station',
  property_description: 'the stations next to this station, sharing the same line(s)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 15. P199 - has organizational division
CREATE (:PropertyMapping {
  property_id: 'P199',
  property_label: 'has organizational division',
  property_description: 'organizational divisions of this organization (which are not independent legal entities)',
  primary_facet: 'POLITICAL',
  secondary_facets: 'ECONOMIC',
  all_facets: 'POLITICAL,ECONOMIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 16. P200 - inflows
CREATE (:PropertyMapping {
  property_id: 'P200',
  property_label: 'inflows',
  property_description: 'major inflow sources — rivers, aquifers, glacial runoff, etc. Some terms may not be place names, e.g. none',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'ENVIRONMENTAL',
  all_facets: 'GEOGRAPHIC,ENVIRONMENTAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 17. P201 - outflows
CREATE (:PropertyMapping {
  property_id: 'P201',
  property_label: 'outflows',
  property_description: 'rivers and other outflows waterway names. If evaporation or seepage are notable outflows, they may be included. Some terms may not be place names, e.g. evaporation',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'ENVIRONMENTAL',
  all_facets: 'GEOGRAPHIC,ENVIRONMENTAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 18. P205 - basin country
CREATE (:PropertyMapping {
  property_id: 'P205',
  property_label: 'basin country',
  property_description: 'country that have drainage to/from or border the body of water',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'ENVIRONMENTAL',
  all_facets: 'GEOGRAPHIC,ENVIRONMENTAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 19. P206 - located in or next to body of water
CREATE (:PropertyMapping {
  property_id: 'P206',
  property_label: 'located in or next to body of water',
  property_description: 'body of water on or next to which a place is located',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 20. P207 - bathymetry image
CREATE (:PropertyMapping {
  property_id: 'P207',
  property_label: 'bathymetry image',
  property_description: 'image showing bathymetric chart, bathymetric map',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'SCIENTIFIC',
  all_facets: 'GEOGRAPHIC,SCIENTIFIC',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 21. P208 - executive body
CREATE (:PropertyMapping {
  property_id: 'P208',
  property_label: 'executive body',
  property_description: 'branch of government for the daily administration of the territorial entity',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 22. P209 - highest judicial authority
CREATE (:PropertyMapping {
  property_id: 'P209',
  property_label: 'highest judicial authority',
  property_description: 'supreme judicial body within a country, administrative division, or other organization',
  primary_facet: 'POLITICAL',
  secondary_facets: 'DIPLOMATIC',
  all_facets: 'POLITICAL,DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 23. P210 - party chief representative
CREATE (:PropertyMapping {
  property_id: 'P210',
  property_label: 'party chief representative',
  property_description: 'chief representative of a party in an institution or an administrative unit (use qualifier to identify the party)',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 24. P212 - ISBN-13
CREATE (:PropertyMapping {
  property_id: 'P212',
  property_label: 'ISBN-13',
  property_description: 'identifier for a book (edition), thirteen digit',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 25. P213 - ISNI
CREATE (:PropertyMapping {
  property_id: 'P213',
  property_label: 'ISNI',
  property_description: 'International Standard Name Identifier for an identity. Starting with 0000.',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 6,
  imported_at: datetime()
});

// 26. P214 - VIAF cluster ID
CREATE (:PropertyMapping {
  property_id: 'P214',
  property_label: 'VIAF cluster ID',
  property_description: 'identifier for the Virtual International Authority File database [format: up to 22 digits]; please note: VIAF is a cluster, the ID can include multiple items',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'INTELLECTUAL,BIOGRAPHIC',
  all_facets: 'GEOGRAPHIC,INTELLECTUAL,BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 10,
  imported_at: datetime()
});

// 27. P215 - spectral class
CREATE (:PropertyMapping {
  property_id: 'P215',
  property_label: 'spectral class',
  property_description: 'spectral class of an astronomical object',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 28. P217 - inventory number
CREATE (:PropertyMapping {
  property_id: 'P217',
  property_label: 'inventory number',
  property_description: 'identifier for a physical object or a set of physical objects in a collection',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 29. P218 - ISO 639-1 code
CREATE (:PropertyMapping {
  property_id: 'P218',
  property_label: 'ISO 639-1 code',
  property_description: '2-letter identifier for language or family of languages defined in ISO 639-1 standard',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 30. P219 - ISO 639-2 code
CREATE (:PropertyMapping {
  property_id: 'P219',
  property_label: 'ISO 639-2 code',
  property_description: '3-letter identifier for language, macro-language or language family, defined in ISO 639-2 standard',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 31. P220 - ISO 639-3 code
CREATE (:PropertyMapping {
  property_id: 'P220',
  property_label: 'ISO 639-3 code',
  property_description: '3-letter identifier for language defined in ISO 639-3, extension of ISO 639-2',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 32. P221 - ISO 639-6 code
CREATE (:PropertyMapping {
  property_id: 'P221',
  property_label: 'ISO 639-6 code',
  property_description: '4-letter identifier for language variants per ISO 639-6, standard between 2009-2014',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 33. P223 - galaxy morphological type
CREATE (:PropertyMapping {
  property_id: 'P223',
  property_label: 'galaxy morphological type',
  property_description: 'galaxy morphological classification code',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 34. P225 - taxon name
CREATE (:PropertyMapping {
  property_id: 'P225',
  property_label: 'taxon name',
  property_description: 'correct scientific name of a taxon (according to the reference given)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 35. P227 - GND ID
CREATE (:PropertyMapping {
  property_id: 'P227',
  property_label: 'GND ID',
  property_description: 'identifier from the Gemeinsame Normdatei authority file of names, subjects, and organizations',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'INTELLECTUAL,BIOGRAPHIC',
  all_facets: 'GEOGRAPHIC,INTELLECTUAL,BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 8,
  imported_at: datetime()
});

// 36. P229 - IATA airline designator
CREATE (:PropertyMapping {
  property_id: 'P229',
  property_label: 'IATA airline designator',
  property_description: 'two-character identifier for an airline',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'ECONOMIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 37. P230 - ICAO airline designator
CREATE (:PropertyMapping {
  property_id: 'P230',
  property_label: 'ICAO airline designator',
  property_description: 'three letter identifier for an airline (two letters only until 1982) (for airports, see P239)',
  primary_facet: 'DIPLOMATIC',
  secondary_facets: '',
  all_facets: 'DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 38. P231 - CAS Registry Number
CREATE (:PropertyMapping {
  property_id: 'P231',
  property_label: 'CAS Registry Number',
  property_description: 'identifier for a chemical substance or compound per Chemical Abstract Service\'s Registry database',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 39. P232 - EC number
CREATE (:PropertyMapping {
  property_id: 'P232',
  property_label: 'EC number',
  property_description: 'identifier for a chemical compound per EINECS or ELINCS',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 40. P233 - canonical SMILES
CREATE (:PropertyMapping {
  property_id: 'P233',
  property_label: 'canonical SMILES',
  property_description: 'Simplified Molecular Input Line Entry Specification (canonical format)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 41. P234 - InChI
CREATE (:PropertyMapping {
  property_id: 'P234',
  property_label: 'InChI',
  property_description: 'International Chemical Identifier',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 42. P235 - InChIKey
CREATE (:PropertyMapping {
  property_id: 'P235',
  property_label: 'InChIKey',
  property_description: 'a hashed version of the full standard InChI',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 43. P236 - ISSN
CREATE (:PropertyMapping {
  property_id: 'P236',
  property_label: 'ISSN',
  property_description: 'International Standard Serial Number (print or electronic)',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 44. P237 - coat of arms
CREATE (:PropertyMapping {
  property_id: 'P237',
  property_label: 'coat of arms',
  property_description: 'subject\'s coat of arms',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 45. P238 - IATA airport code
CREATE (:PropertyMapping {
  property_id: 'P238',
  property_label: 'IATA airport code',
  property_description: 'three-letter identifier for designating airports, railway stations or cities (for airlines, see P229)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 46. P239 - ICAO airport code
CREATE (:PropertyMapping {
  property_id: 'P239',
  property_label: 'ICAO airport code',
  property_description: 'four-character alphanumeric identifier for designating airports (for airlines, see P230)',
  primary_facet: 'DIPLOMATIC',
  secondary_facets: '',
  all_facets: 'DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 47. P240 - FAA airport code
CREATE (:PropertyMapping {
  property_id: 'P240',
  property_label: 'FAA airport code',
  property_description: 'three-letter or four-letter alphanumeric code identifying United States airports',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 48. P241 - military branch
CREATE (:PropertyMapping {
  property_id: 'P241',
  property_label: 'military branch',
  property_description: 'branch to which this military unit, award, office, or person belongs, e.g. Royal Navy',
  primary_facet: 'MILITARY',
  secondary_facets: '',
  all_facets: 'MILITARY',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 49. P242 - locator map image
CREATE (:PropertyMapping {
  property_id: 'P242',
  property_label: 'locator map image',
  property_description: 'geographic map image which highlights the location of the subject within some larger entity',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 50. P243 - OCLC number
CREATE (:PropertyMapping {
  property_id: 'P243',
  property_label: 'OCLC number',
  property_description: 'identifier for a bibliographic record in OCLC WorldCat',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 51. P244 - Library of Congress authority ID
CREATE (:PropertyMapping {
  property_id: 'P244',
  property_label: 'Library of Congress authority ID',
  property_description: 'Library of Congress name authority (persons, families, corporate bodies, events, places, works and expressions) and subject authority identifier [Format: 1-2 specific letters followed by 8-10 digits (see regex). For manifestations, use P1144]',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 5,
  imported_at: datetime()
});

// 52. P245 - Union List of Artist Names ID
CREATE (:PropertyMapping {
  property_id: 'P245',
  property_label: 'Union List of Artist Names ID',
  property_description: 'identifier from the Getty Union List of Artist Names',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 53. P246 - element symbol
CREATE (:PropertyMapping {
  property_id: 'P246',
  property_label: 'element symbol',
  property_description: 'identifier for a chemical element',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 54. P247 - COSPAR ID
CREATE (:PropertyMapping {
  property_id: 'P247',
  property_label: 'COSPAR ID',
  property_description: 'international satellite designation, administered by the UN Committee on Space Research (COSPAR), similar but not synonymous with the NSSDCA ID (P8913)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'SCIENTIFIC,TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 55. P248 - stated in
CREATE (:PropertyMapping {
  property_id: 'P248',
  property_label: 'stated in',
  property_description: 'to be used in the references field to refer to the information document or database in which a claim is made; for qualifiers use P805; for the type of document in which a claim is made use P3865',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 56. P249 - ticker symbol
CREATE (:PropertyMapping {
  property_id: 'P249',
  property_label: 'ticker symbol',
  property_description: 'identifier for a publicly traded share of a particular stock on a particular stock market or that of a cryptocurrency (qualifier for P414)',
  primary_facet: 'ECONOMIC',
  secondary_facets: '',
  all_facets: 'ECONOMIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 57. P263 - official residence
CREATE (:PropertyMapping {
  property_id: 'P263',
  property_label: 'official residence',
  property_description: 'the residence at which heads of government and other senior figures officially reside',
  primary_facet: 'POLITICAL',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'POLITICAL,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 58. P264 - record label
CREATE (:PropertyMapping {
  property_id: 'P264',
  property_label: 'record label',
  property_description: 'brand and trademark associated with the marketing of subject music recordings and music videos',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 59. P267 - ATC code
CREATE (:PropertyMapping {
  property_id: 'P267',
  property_label: 'ATC code',
  property_description: 'therapeutic chemical identification code per ATC',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 60. P268 - Bibliothèque nationale de France ID
CREATE (:PropertyMapping {
  property_id: 'P268',
  property_label: 'Bibliothèque nationale de France ID',
  property_description: 'identifier for the subject issued by BNF (Bibliothèque nationale de France). Format: 8 digits followed by a check-digit or letter, do not include the initial \'cb\'.',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'INTELLECTUAL,BIOGRAPHIC',
  all_facets: 'GEOGRAPHIC,INTELLECTUAL,BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 6,
  imported_at: datetime()
});

// 61. P269 - IdRef ID
CREATE (:PropertyMapping {
  property_id: 'P269',
  property_label: 'IdRef ID',
  property_description: 'identifier for authority control in the French collaborative library catalog (see also P1025). Format: 8 digits followed by a digit or \"X\"',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'GEOGRAPHIC,BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 4,
  imported_at: datetime()
});

// 62. P270 - CALIS ID
CREATE (:PropertyMapping {
  property_id: 'P270',
  property_label: 'CALIS ID',
  property_description: 'identifier for authority control per CALIS (China Academic Library & Information System)',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 63. P271 - NACSIS-CAT author ID
CREATE (:PropertyMapping {
  property_id: 'P271',
  property_label: 'NACSIS-CAT author ID',
  property_description: 'identifier for book authors in NACSIS-CAT, the union catalog for university libraries and research institutions in Japan',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 4,
  imported_at: datetime()
});

// 64. P272 - production company
CREATE (:PropertyMapping {
  property_id: 'P272',
  property_label: 'production company',
  property_description: 'company that produced this film, audio or performing arts work',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 65. P274 - chemical formula
CREATE (:PropertyMapping {
  property_id: 'P274',
  property_label: 'chemical formula',
  property_description: 'description of chemical compound giving element symbols and counts',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 66. P275 - copyright license
CREATE (:PropertyMapping {
  property_id: 'P275',
  property_label: 'copyright license',
  property_description: 'license under which this copyrighted work is released',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 67. P276 - location
CREATE (:PropertyMapping {
  property_id: 'P276',
  property_label: 'location',
  property_description: 'location of the object, structure or event; use P131 to indicate the containing administrative entity, P8138 for statistical entities, or P706 for geographic entities; use P7153 for locations associated with the object',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 68. P277 - programmed in
CREATE (:PropertyMapping {
  property_id: 'P277',
  property_label: 'programmed in',
  property_description: 'the programming language(s) in which the software is developed',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 69. P278 - GOST 7.75–97 code
CREATE (:PropertyMapping {
  property_id: 'P278',
  property_label: 'GOST 7.75–97 code',
  property_description: 'identifier for a language according to GOST 7.75–97',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 70. P279 - subclass of
CREATE (:PropertyMapping {
  property_id: 'P279',
  property_label: 'subclass of',
  property_description: 'this item is a subclass (subset) of that item; ALL instances of this item are instances of that item; different from P31 (instance of), e.g.: volcano is a subclass of mountain; Everest is an instance of mountain',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 71. P281 - postal code
CREATE (:PropertyMapping {
  property_id: 'P281',
  property_label: 'postal code',
  property_description: 'code assigned by postal authorities for the subject area or building for the purpose of sorting and routing mail',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 72. P282 - writing system
CREATE (:PropertyMapping {
  property_id: 'P282',
  property_label: 'writing system',
  property_description: 'alphabet, character set or other system of writing used by a language, word, or text, supported by a typeface',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 73. P286 - head coach
CREATE (:PropertyMapping {
  property_id: 'P286',
  property_label: 'head coach',
  property_description: 'on-field manager or head coach of a sports club (not to be confused with a general manager P505, which is not a coaching position) or person',
  primary_facet: 'SOCIAL',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'SOCIAL,BIOGRAPHIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 74. P287 - designed by
CREATE (:PropertyMapping {
  property_id: 'P287',
  property_label: 'designed by',
  property_description: 'person or organization which designed the object. For buildings use \"architect\" (Property:P84)',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 75. P289 - vessel class
CREATE (:PropertyMapping {
  property_id: 'P289',
  property_label: 'vessel class',
  property_description: 'series of vessels or other watercraft built to the same design of which this vessel is a member',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'MILITARY',
  all_facets: 'TECHNOLOGICAL,MILITARY',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 76. P291 - place of publication
CREATE (:PropertyMapping {
  property_id: 'P291',
  property_label: 'place of publication',
  property_description: 'geographical place of publication of the edition (use 1st edition when referring to works)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'GEOGRAPHIC,INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 77. P296 - station code
CREATE (:PropertyMapping {
  property_id: 'P296',
  property_label: 'station code',
  property_description: 'generic identifier for a railway station, when possible, use specific property on certain coding system (e.g. P1378 for China Railway TMIS codes)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 78. P297 - ISO 3166-1 alpha-2 code
CREATE (:PropertyMapping {
  property_id: 'P297',
  property_label: 'ISO 3166-1 alpha-2 code',
  property_description: 'identifier for a country in two-letter format per ISO 3166-1',
  primary_facet: 'POLITICAL',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'POLITICAL,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 79. P298 - ISO 3166-1 alpha-3 code
CREATE (:PropertyMapping {
  property_id: 'P298',
  property_label: 'ISO 3166-1 alpha-3 code',
  property_description: 'identifier for a country in three-letter format per ISO 3166-1',
  primary_facet: 'POLITICAL',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'POLITICAL,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 80. P299 - ISO 3166-1 numeric code
CREATE (:PropertyMapping {
  property_id: 'P299',
  property_label: 'ISO 3166-1 numeric code',
  property_description: 'identifier for a country in numeric format per ISO 3166-1',
  primary_facet: 'POLITICAL',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'POLITICAL,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 81. P300 - ISO 3166-2 code
CREATE (:PropertyMapping {
  property_id: 'P300',
  property_label: 'ISO 3166-2 code',
  property_description: 'identifier for a country subdivision per ISO 3166-2 (include country code)',
  primary_facet: 'POLITICAL',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'POLITICAL,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 82. P301 - category\'s main topic
CREATE (:PropertyMapping {
  property_id: 'P301',
  property_label: 'category\'s main topic',
  property_description: 'primary topic of the subject Wikimedia category',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 83. P303 - EE breed number
CREATE (:PropertyMapping {
  property_id: 'P303',
  property_label: 'EE breed number',
  property_description: 'breed identification number per the EE list of the breeds of fancy pigeons (ELFP)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 84. P304 - page(s)
CREATE (:PropertyMapping {
  property_id: 'P304',
  property_label: 'page(s)',
  property_description: 'page number of source referenced for statement. Note \"column(s)\" (P3903) and \"folio(s)\" (P7416) for other numbering systems',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 85. P305 - IETF language tag
CREATE (:PropertyMapping {
  property_id: 'P305',
  property_label: 'IETF language tag',
  property_description: 'identifier for language or languoid per the Internet Engineering Task Force; can include a primary language subtag, subtags for script, region, variant, extension, or private-use. Format: 2 or 3 letters, followed by \"-\" if subtags present',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 86. P306 - operating system
CREATE (:PropertyMapping {
  property_id: 'P306',
  property_label: 'operating system',
  property_description: 'operating system (OS) on which a software works or the OS installed on hardware',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 87. P344 - director of photography
CREATE (:PropertyMapping {
  property_id: 'P344',
  property_label: 'director of photography',
  property_description: 'person responsible for the framing, lighting, and filtration of the subject work',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'ARTISTIC,TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 88. P345 - IMDb ID
CREATE (:PropertyMapping {
  property_id: 'P345',
  property_label: 'IMDb ID',
  property_description: 'identifier for the IMDb (with prefix \'tt\', \'nm\', \'co\', \'ev\', \'ch\' or \'ni\')',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 6,
  imported_at: datetime()
});

// 89. P347 - Joconde work ID
CREATE (:PropertyMapping {
  property_id: 'P347',
  property_label: 'Joconde work ID',
  property_description: 'identifier in the Joconde database of the French Ministry of Culture',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 90. P348 - software version identifier
CREATE (:PropertyMapping {
  property_id: 'P348',
  property_label: 'software version identifier',
  property_description: 'numeric or nominal identifier of a version of a software program or file format, current or past',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 91. P349 - NDL Authority ID
CREATE (:PropertyMapping {
  property_id: 'P349',
  property_label: 'NDL Authority ID',
  property_description: 'identifier for authority control per the National Diet Library of Japan',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'INTELLECTUAL,BIOGRAPHIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 92. P350 - RKDimages ID
CREATE (:PropertyMapping {
  property_id: 'P350',
  property_label: 'RKDimages ID',
  property_description: 'identifier per RKDimages of the Netherlands Institute for Art History',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 93. P351 - Entrez Gene ID
CREATE (:PropertyMapping {
  property_id: 'P351',
  property_label: 'Entrez Gene ID',
  property_description: 'identifier for a gene per the NCBI Entrez database',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 94. P352 - UniProt protein ID
CREATE (:PropertyMapping {
  property_id: 'P352',
  property_label: 'UniProt protein ID',
  property_description: 'identifier for a protein per the UniProt database',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 95. P353 - HGNC gene symbol
CREATE (:PropertyMapping {
  property_id: 'P353',
  property_label: 'HGNC gene symbol',
  property_description: 'the official gene symbol approved by the HGNC, which is typically a short form of the gene name',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 96. P354 - HGNC ID
CREATE (:PropertyMapping {
  property_id: 'P354',
  property_label: 'HGNC ID',
  property_description: 'a unique ID provided by the HGNC for each gene with an approved symbol. HGNC IDs remain stable even if a name or symbol changes',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 97. P355 - child organization or unit
CREATE (:PropertyMapping {
  property_id: 'P355',
  property_label: 'child organization or unit',
  property_description: 'child organization/unit of a organization/unit; for companies, generally a fully owned separate corp., see business division (P199); opposite of parent org./unit (P749); use instance of (P31) to distinguish org. (Q43229) and org. unit (Q10387680)',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'ECONOMIC,POLITICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 98. P356 - DOI
CREATE (:PropertyMapping {
  property_id: 'P356',
  property_label: 'DOI',
  property_description: 'serial code used to uniquely identify digital objects like academic papers (use upper case letters only)',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 99. P358 - discography
CREATE (:PropertyMapping {
  property_id: 'P358',
  property_label: 'discography',
  property_description: 'item for list pages with discography of artist or band',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 100. P359 - Rijksmonument ID
CREATE (:PropertyMapping {
  property_id: 'P359',
  property_label: 'Rijksmonument ID',
  property_description: 'identifier for a monument assigned by the Rijksdienst voor het Cultureel Erfgoed',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 101. P360 - is a list of
CREATE (:PropertyMapping {
  property_id: 'P360',
  property_label: 'is a list of',
  property_description: 'common element between all listed items',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 102. P361 - part of
CREATE (:PropertyMapping {
  property_id: 'P361',
  property_label: 'part of',
  property_description: 'object of which the subject is a part (if this subject is already part of object A which is a part of object B, then please only make the subject part of object A), inverse property of \"has part\" (P527, see also \"has parts of the class\" (P2670))',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 103. P364 - original language of film or TV show
CREATE (:PropertyMapping {
  property_id: 'P364',
  property_label: 'original language of film or TV show',
  property_description: 'language in which a film or a performance work was originally created. Deprecated for written works and songs; use P407 (\"language of work or name\") instead.',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 104. P366 - has use
CREATE (:PropertyMapping {
  property_id: 'P366',
  property_label: 'has use',
  property_description: 'main use of the subject (includes current and former usage)',
  primary_facet: 'CULTURAL',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'CULTURAL,TECHNOLOGICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 105. P367 - astronomic symbol image
CREATE (:PropertyMapping {
  property_id: 'P367',
  property_label: 'astronomic symbol image',
  property_description: 'image of the symbol that identifies a planet, asteroid, or other object in the Solar System',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 106. P368 - Sandbox-CommonsMediaFile
CREATE (:PropertyMapping {
  property_id: 'P368',
  property_label: 'Sandbox-CommonsMediaFile',
  property_description: 'Sandbox property for value of type \"Commons Media File\"',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.50,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 107. P369 - Sandbox-Item
CREATE (:PropertyMapping {
  property_id: 'P369',
  property_label: 'Sandbox-Item',
  property_description: 'Sandbox property for value of type \"Item\"',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.50,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 108. P370 - Sandbox-String
CREATE (:PropertyMapping {
  property_id: 'P370',
  property_label: 'Sandbox-String',
  property_description: 'Sandbox property for the data value type \"String\"',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.50,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 109. P371 - presenter
CREATE (:PropertyMapping {
  property_id: 'P371',
  property_label: 'presenter',
  property_description: 'main role in presenting a radio or television program or a performing arts show',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'ARTISTIC,CULTURAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 110. P373 - Commons category
CREATE (:PropertyMapping {
  property_id: 'P373',
  property_label: 'Commons category',
  property_description: 'name of the Wikimedia Commons category containing files related to this item (without the prefix \"Category:\")',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'CULTURAL',
  all_facets: 'INTELLECTUAL,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 111. P374 - Insee municipality code
CREATE (:PropertyMapping {
  property_id: 'P374',
  property_label: 'Insee municipality code',
  property_description: 'identifier/code with five digits or letters for a municipality or a municipal arrondissement in France, per the National Institute of Statistics and Economic Studies',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 112. P375 - space launch vehicle
CREATE (:PropertyMapping {
  property_id: 'P375',
  property_label: 'space launch vehicle',
  property_description: 'type of rocket or other vehicle for launching subject payload into outer space',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'SCIENTIFIC',
  all_facets: 'TECHNOLOGICAL,SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 113. P376 - located on astronomical body
CREATE (:PropertyMapping {
  property_id: 'P376',
  property_label: 'located on astronomical body',
  property_description: 'single astronomical body on which features or places are situated',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'SCIENTIFIC',
  all_facets: 'GEOGRAPHIC,SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 114. P377 - SCN
CREATE (:PropertyMapping {
  property_id: 'P377',
  property_label: 'SCN',
  property_description: 'Satellite Catalog Number, 5-digit-number including leading zeros (e.g. \'00266\')',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'SCIENTIFIC',
  all_facets: 'TECHNOLOGICAL,SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 115. P380 - Mérimée ID
CREATE (:PropertyMapping {
  property_id: 'P380',
  property_label: 'Mérimée ID',
  property_description: 'identifier for a monument in the Mérimée database of French cultural heritage',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 116. P381 - PCP reference number
CREATE (:PropertyMapping {
  property_id: 'P381',
  property_label: 'PCP reference number',
  property_description: 'identifier for cultural properties in Switzerland',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 117. P382 - CBS municipality code
CREATE (:PropertyMapping {
  property_id: 'P382',
  property_label: 'CBS municipality code',
  property_description: 'identifier for a Dutch municipality as defined by Statistics Netherlands (CBS)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 118. P393 - edition number
CREATE (:PropertyMapping {
  property_id: 'P393',
  property_label: 'edition number',
  property_description: 'number of an edition (first, second, ... as 1, 2, ...) or event',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 119. P395 - licence plate code
CREATE (:PropertyMapping {
  property_id: 'P395',
  property_label: 'licence plate code',
  property_description: 'distinguishing signs or parts of license plate associated with the subject. For countries: international licence plate country code or distinguishing sign of vehicles',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 120. P396 - SBN author ID
CREATE (:PropertyMapping {
  property_id: 'P396',
  property_label: 'SBN author ID',
  property_description: 'identifier issued by National Library Service (SBN) of Italy',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 4,
  imported_at: datetime()
});

// 121. P397 - parent astronomical body
CREATE (:PropertyMapping {
  property_id: 'P397',
  property_label: 'parent astronomical body',
  property_description: 'major astronomical body the item belongs to',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 122. P398 - child astronomical body
CREATE (:PropertyMapping {
  property_id: 'P398',
  property_label: 'child astronomical body',
  property_description: 'minor body that belongs to the item',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 123. P399 - companion of
CREATE (:PropertyMapping {
  property_id: 'P399',
  property_label: 'companion of',
  property_description: 'two or more astronomic bodies of the same type relating to each other',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 124. P400 - platform
CREATE (:PropertyMapping {
  property_id: 'P400',
  property_label: 'platform',
  property_description: 'platform for which a work was developed or released, or the specific platform version of a software product',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 125. P402 - OpenStreetMap relation ID
CREATE (:PropertyMapping {
  property_id: 'P402',
  property_label: 'OpenStreetMap relation ID',
  property_description: 'identifier for a relation in OpenStreetMap',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 126. P403 - mouth of the watercourse
CREATE (:PropertyMapping {
  property_id: 'P403',
  property_label: 'mouth of the watercourse',
  property_description: 'the body of water to which the watercourse drains',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 127. P404 - game mode
CREATE (:PropertyMapping {
  property_id: 'P404',
  property_label: 'game mode',
  property_description: 'video game\'s available playing mode(s)',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 128. P405 - taxon author
CREATE (:PropertyMapping {
  property_id: 'P405',
  property_label: 'taxon author',
  property_description: 'the author(s) that (optionally) may be cited with the scientific name',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'SCIENTIFIC,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 129. P406 - soundtrack release
CREATE (:PropertyMapping {
  property_id: 'P406',
  property_label: 'soundtrack release',
  property_description: 'music release that incorporates music directly recorded from the soundtrack of an audiovisual work',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'ARTISTIC,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 130. P407 - language of work or name
CREATE (:PropertyMapping {
  property_id: 'P407',
  property_label: 'language of work or name',
  property_description: 'language associated with this creative work (such as books, shows, songs, broadcasts or websites) or a name (for persons use \"native language\" (P103) and \"languages spoken, written or signed\" (P1412))',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'LINGUISTIC',
  all_facets: 'INTELLECTUAL,LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 131. P408 - software engine
CREATE (:PropertyMapping {
  property_id: 'P408',
  property_label: 'software engine',
  property_description: 'software engine employed by the subject item',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 132. P409 - Libraries Australia ID
CREATE (:PropertyMapping {
  property_id: 'P409',
  property_label: 'Libraries Australia ID',
  property_description: 'identifier issued by the National Library of Australia (see also P1315 for the newer People Australia identifier). VIAF component. Format: 1-12 digits, removing leading zero-padding.',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 133. P410 - military, police or special rank
CREATE (:PropertyMapping {
  property_id: 'P410',
  property_label: 'military, police or special rank',
  property_description: 'military or police rank achieved by a person (should usually have a \"start time\" qualifier), or military or police rank associated with a position',
  primary_facet: 'MILITARY',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'MILITARY,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 134. P411 - canonization status
CREATE (:PropertyMapping {
  property_id: 'P411',
  property_label: 'canonization status',
  property_description: 'formal stage in the process of attaining sainthood per the subject\'s religious organization',
  primary_facet: 'RELIGIOUS',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'RELIGIOUS,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 135. P412 - voice type
CREATE (:PropertyMapping {
  property_id: 'P412',
  property_label: 'voice type',
  property_description: 'person\'s voice type. expected values: soprano, mezzo-soprano, contralto, countertenor, tenor, baritone, bass (and derivatives)',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 136. P413 - position played on team / speciality
CREATE (:PropertyMapping {
  property_id: 'P413',
  property_label: 'position played on team / speciality',
  property_description: 'position or specialism of a player on a team',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 137. P414 - stock exchange
CREATE (:PropertyMapping {
  property_id: 'P414',
  property_label: 'stock exchange',
  property_description: 'exchange on which this company is traded',
  primary_facet: 'ECONOMIC',
  secondary_facets: '',
  all_facets: 'ECONOMIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 138. P415 - radio format
CREATE (:PropertyMapping {
  property_id: 'P415',
  property_label: 'radio format',
  property_description: 'describes the overall content broadcast on a radio station',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 139. P416 - quantity symbol (string)
CREATE (:PropertyMapping {
  property_id: 'P416',
  property_label: 'quantity symbol (string)',
  property_description: 'symbol for a mathematical or physical quantity',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 140. P417 - patron saint
CREATE (:PropertyMapping {
  property_id: 'P417',
  property_label: 'patron saint',
  property_description: 'patron saint adopted by the subject',
  primary_facet: 'RELIGIOUS',
  secondary_facets: '',
  all_facets: 'RELIGIOUS',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 141. P418 - has seal, badge, or sigil
CREATE (:PropertyMapping {
  property_id: 'P418',
  property_label: 'has seal, badge, or sigil',
  property_description: 'links to the item for the subject\'s seal',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 142. P421 - located in time zone
CREATE (:PropertyMapping {
  property_id: 'P421',
  property_label: 'located in time zone',
  property_description: 'time zone for this item',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 143. P423 - shooting handedness
CREATE (:PropertyMapping {
  property_id: 'P423',
  property_label: 'shooting handedness',
  property_description: 'whether the hockey player passes or shoots left- or right-handed',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'SOCIAL',
  all_facets: 'BIOGRAPHIC,SOCIAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 144. P424 - Wikimedia language code
CREATE (:PropertyMapping {
  property_id: 'P424',
  property_label: 'Wikimedia language code',
  property_description: 'identifier for a language or variant as used by Wikimedia projects',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 145. P425 - field of this occupation
CREATE (:PropertyMapping {
  property_id: 'P425',
  property_label: 'field of this occupation',
  property_description: 'field corresponding to this occupation or profession (use only for occupations/professions - for people use Property:P101, for companies use P452)',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'ECONOMIC',
  all_facets: 'INTELLECTUAL,ECONOMIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 146. P426 - aircraft registration
CREATE (:PropertyMapping {
  property_id: 'P426',
  property_label: 'aircraft registration',
  property_description: 'identifier assigned to an individual aircraft by civil aircraft registry',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 147. P427 - taxonomic type
CREATE (:PropertyMapping {
  property_id: 'P427',
  property_label: 'taxonomic type',
  property_description: 'type genus or species: [in zoology:] nominal genus or species that is the name-bearing type of this nominal family or genus (or family-group ranked taxon or subgenus); type specimen that is the name-bearing type of this nominal species or subspecies',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 148. P428 - botanist author abbreviation
CREATE (:PropertyMapping {
  property_id: 'P428',
  property_label: 'botanist author abbreviation',
  property_description: 'standard form (official abbreviation) of a personal name for use in an author citation (only for names of algae, fungi and plants)',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 149. P429 - dantai code
CREATE (:PropertyMapping {
  property_id: 'P429',
  property_label: 'dantai code',
  property_description: '6-digit identifier for an administrative division of Japan, assigned by Ministry of Internal Affairs and Communications',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 150. P432 - callsign of airline
CREATE (:PropertyMapping {
  property_id: 'P432',
  property_label: 'callsign of airline',
  property_description: 'identifier used in radio transmissions to refer to the subject airline',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'ECONOMIC',
  all_facets: 'TECHNOLOGICAL,ECONOMIC',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 151. P433 - issue
CREATE (:PropertyMapping {
  property_id: 'P433',
  property_label: 'issue',
  property_description: 'issue of a newspaper, a scientific journal or magazine for reference purpose',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 152. P434 - MusicBrainz artist ID
CREATE (:PropertyMapping {
  property_id: 'P434',
  property_label: 'MusicBrainz artist ID',
  property_description: 'identifier for an artist in the MusicBrainz open music encyclopedia',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'ARTISTIC,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 153. P435 - MusicBrainz work ID
CREATE (:PropertyMapping {
  property_id: 'P435',
  property_label: 'MusicBrainz work ID',
  property_description: 'identifier for a work per the MusicBrainz open music encyclopedia',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'ARTISTIC,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 154. P436 - MusicBrainz release group ID
CREATE (:PropertyMapping {
  property_id: 'P436',
  property_label: 'MusicBrainz release group ID',
  property_description: 'identifier for a release group per the MusicBrainz open music encyclopedia (album, single, etc.)',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'ARTISTIC,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 155. P437 - distribution format
CREATE (:PropertyMapping {
  property_id: 'P437',
  property_label: 'distribution format',
  property_description: 'method (or type) of distribution for the subject',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 156. P439 - German municipality key
CREATE (:PropertyMapping {
  property_id: 'P439',
  property_label: 'German municipality key',
  property_description: 'numerical code for municipalities and independent towns in Germany',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 157. P440 - German district key
CREATE (:PropertyMapping {
  property_id: 'P440',
  property_label: 'German district key',
  property_description: 'numerical code for districts (Landkreise) and independent towns in Germany',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 158. P442 - China division code for Statistics
CREATE (:PropertyMapping {
  property_id: 'P442',
  property_label: 'China division code for Statistics',
  property_description: 'identifier for divisions of People\'s Republic of China for Statistics (with spaces)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 159. P443 - pronunciation audio
CREATE (:PropertyMapping {
  property_id: 'P443',
  property_label: 'pronunciation audio',
  property_description: 'audio file with pronunciation',
  primary_facet: 'LINGUISTIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'LINGUISTIC,CULTURAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 160. P444 - review score
CREATE (:PropertyMapping {
  property_id: 'P444',
  property_label: 'review score',
  property_description: 'review score received by a creative work or other entity',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 161. P447 - review score by
CREATE (:PropertyMapping {
  property_id: 'P447',
  property_label: 'review score by',
  property_description: 'issuer of a review score',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 162. P449 - original broadcaster
CREATE (:PropertyMapping {
  property_id: 'P449',
  property_label: 'original broadcaster',
  property_description: 'network(s) or service(s) that originally broadcast a radio or television program',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 163. P450 - astronaut mission
CREATE (:PropertyMapping {
  property_id: 'P450',
  property_label: 'astronaut mission',
  property_description: 'space mission that the subject is or has been a member of (do not include future missions)',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 164. P451 - unmarried partner
CREATE (:PropertyMapping {
  property_id: 'P451',
  property_label: 'unmarried partner',
  property_description: 'someone with whom the person is in a relationship without being married. Use \"spouse\" (P26) for married couples',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'SOCIAL',
  all_facets: 'BIOGRAPHIC,SOCIAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 165. P452 - industry
CREATE (:PropertyMapping {
  property_id: 'P452',
  property_label: 'industry',
  property_description: 'specific industry of company or organization',
  primary_facet: 'ECONOMIC',
  secondary_facets: '',
  all_facets: 'ECONOMIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 166. P453 - character role
CREATE (:PropertyMapping {
  property_id: 'P453',
  property_label: 'character role',
  property_description: 'specific role played or filled by subject -- use only as qualifier of \"cast member\" (P161), \"voice actor\" (P725)',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'ARTISTIC,CULTURAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 167. P454 - Structurae structure ID
CREATE (:PropertyMapping {
  property_id: 'P454',
  property_label: 'Structurae structure ID',
  property_description: 'identifier for a building in the Structurae database',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 168. P455 - Emporis building ID
CREATE (:PropertyMapping {
  property_id: 'P455',
  property_label: 'Emporis building ID',
  property_description: 'former identifier for a building in the defunct Emporis database (for building complexes, see P2270)',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'TECHNOLOGICAL,GEOGRAPHIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 169. P457 - foundational text
CREATE (:PropertyMapping {
  property_id: 'P457',
  property_label: 'foundational text',
  property_description: 'text through which an institution or object has been created or established',
  primary_facet: 'DIPLOMATIC',
  secondary_facets: '',
  all_facets: 'DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 170. P458 - IMO ship number
CREATE (:PropertyMapping {
  property_id: 'P458',
  property_label: 'IMO ship number',
  property_description: 'identifier for a ship, ship owner or ship manager per the International Maritime Organization',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'ECONOMIC',
  all_facets: 'TECHNOLOGICAL,ECONOMIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 171. P459 - determination method or standard
CREATE (:PropertyMapping {
  property_id: 'P459',
  property_label: 'determination method or standard',
  property_description: 'how a value is determined, or the standard by which it is declared',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'SCIENTIFIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 172. P460 - said to be the same as
CREATE (:PropertyMapping {
  property_id: 'P460',
  property_label: 'said to be the same as',
  property_description: 'this item is said to be the same as that item, though this may be uncertain or disputed',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 173. P461 - opposite of
CREATE (:PropertyMapping {
  property_id: 'P461',
  property_label: 'opposite of',
  property_description: 'item that is in some way the opposite of this item',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 174. P462 - color
CREATE (:PropertyMapping {
  property_id: 'P462',
  property_label: 'color',
  property_description: 'color of subject',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'ARTISTIC,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 175. P463 - member of
CREATE (:PropertyMapping {
  property_id: 'P463',
  property_label: 'member of',
  property_description: 'organization, club or musical group to which the subject belongs. Do not use for membership in ethnic or social groups, nor for holding a political position, such as a member of parliament (use P39 for that)',
  primary_facet: 'SOCIAL',
  secondary_facets: 'POLITICAL',
  all_facets: 'SOCIAL,POLITICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 176. P464 - NOR numbering ID
CREATE (:PropertyMapping {
  property_id: 'P464',
  property_label: 'NOR numbering ID',
  property_description: 'identifier for French official texts',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'DIPLOMATIC',
  all_facets: 'INTELLECTUAL,DIPLOMATIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 177. P465 - sRGB color hex triplet
CREATE (:PropertyMapping {
  property_id: 'P465',
  property_label: 'sRGB color hex triplet',
  property_description: 'sRGB hex triplet format for subject color (e.g. 7FFFD4) specifying the 8-bit red, green and blue components',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'ARTISTIC',
  all_facets: 'TECHNOLOGICAL,ARTISTIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 178. P466 - occupant
CREATE (:PropertyMapping {
  property_id: 'P466',
  property_label: 'occupant',
  property_description: 'person or organization occupying property',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'ECONOMIC',
  all_facets: 'BIOGRAPHIC,ECONOMIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 179. P467 - legislated by
CREATE (:PropertyMapping {
  property_id: 'P467',
  property_label: 'legislated by',
  property_description: 'indicates that an act or bill was passed by a legislature. The value can be a particular session of the legislature',
  primary_facet: 'DIPLOMATIC',
  secondary_facets: '',
  all_facets: 'DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 180. P468 - dan/kyu rank
CREATE (:PropertyMapping {
  property_id: 'P468',
  property_label: 'dan/kyu rank',
  property_description: 'rank system used in several board games (e.g. go, shogi, renju), martial arts (e.g. judo, kendo, wushu) and some other games',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 181. P469 - lake on watercourse
CREATE (:PropertyMapping {
  property_id: 'P469',
  property_label: 'lake on watercourse',
  property_description: 'lake or reservoir through which the river or stream flows',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'ENVIRONMENTAL',
  all_facets: 'GEOGRAPHIC,ENVIRONMENTAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 182. P470 - Eight Banner register
CREATE (:PropertyMapping {
  property_id: 'P470',
  property_label: 'Eight Banner register',
  property_description: 'Manchu household register for people of the Qing Dynasty',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 183. P473 - local dialing code
CREATE (:PropertyMapping {
  property_id: 'P473',
  property_label: 'local dialing code',
  property_description: 'identifier dedicated to subject city by the area communication network',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 184. P474 - telephone country code
CREATE (:PropertyMapping {
  property_id: 'P474',
  property_label: 'telephone country code',
  property_description: 'identifier for a country - dialed on phone after the international dialing prefix (precede value by +)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 185. P476 - CELEX number
CREATE (:PropertyMapping {
  property_id: 'P476',
  property_label: 'CELEX number',
  property_description: 'identifier for European legal texts in EUR-Lex database',
  primary_facet: 'DIPLOMATIC',
  secondary_facets: '',
  all_facets: 'DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 186. P477 - Canadian Register of Historic Places ID
CREATE (:PropertyMapping {
  property_id: 'P477',
  property_label: 'Canadian Register of Historic Places ID',
  property_description: 'identifier in the Canadian Register of Historic Places',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 187. P478 - volume
CREATE (:PropertyMapping {
  property_id: 'P478',
  property_label: 'volume',
  property_description: 'volume of a book or music release in a collection/series or a published collection of journal issues in a serial publication',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 188. P479 - input device
CREATE (:PropertyMapping {
  property_id: 'P479',
  property_label: 'input device',
  property_description: 'input device used to interact with a software or a device',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 189. P480 - FilmAffinity film ID
CREATE (:PropertyMapping {
  property_id: 'P480',
  property_label: 'FilmAffinity film ID',
  property_description: 'FilmAffinity identification number of a creative work',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'ARTISTIC,INTELLECTUAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 190. P481 - Palissy ID
CREATE (:PropertyMapping {
  property_id: 'P481',
  property_label: 'Palissy ID',
  property_description: 'identifier in the Palissy database of moveable objects of French cultural heritage',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'ARTISTIC,CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 191. P483 - recorded at studio or venue
CREATE (:PropertyMapping {
  property_id: 'P483',
  property_label: 'recorded at studio or venue',
  property_description: 'studio or location where a musical composition/release was recorded',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 192. P484 - IMA Number, broad sense
CREATE (:PropertyMapping {
  property_id: 'P484',
  property_label: 'IMA Number, broad sense',
  property_description: 'identifier for a mineral per the International Mineralogical Association - Commission on New Minerals, Nomenclature and Classification (IMA-CNMNC)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 193. P485 - archives at
CREATE (:PropertyMapping {
  property_id: 'P485',
  property_label: 'archives at',
  property_description: 'the institution holding the subject\'s archives',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'BIOGRAPHIC,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 194. P486 - MeSH descriptor ID
CREATE (:PropertyMapping {
  property_id: 'P486',
  property_label: 'MeSH descriptor ID',
  property_description: 'identifier for Descriptor or Supplementary concept in the Medical Subject Headings controlled vocabulary',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 4,
  imported_at: datetime()
});

// 195. P487 - Unicode character
CREATE (:PropertyMapping {
  property_id: 'P487',
  property_label: 'Unicode character',
  property_description: 'Unicode character representing the item (only if this is not a control character or a compatiblity character: in that case, use only P4213)',
  primary_facet: 'LINGUISTIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'LINGUISTIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 196. P488 - chairperson
CREATE (:PropertyMapping {
  property_id: 'P488',
  property_label: 'chairperson',
  property_description: 'presiding member of an organization, group or body',
  primary_facet: 'POLITICAL',
  secondary_facets: 'SOCIAL',
  all_facets: 'POLITICAL,SOCIAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 197. P489 - currency symbol description
CREATE (:PropertyMapping {
  property_id: 'P489',
  property_label: 'currency symbol description',
  property_description: 'item with description of currency symbol',
  primary_facet: 'ECONOMIC',
  secondary_facets: '',
  all_facets: 'ECONOMIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 198. P490 - provisional designation
CREATE (:PropertyMapping {
  property_id: 'P490',
  property_label: 'provisional designation',
  property_description: 'designation of an astronomical body after its discovery and before its official name',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 199. P491 - orbit diagram
CREATE (:PropertyMapping {
  property_id: 'P491',
  property_label: 'orbit diagram',
  property_description: 'image with the diagram of the orbit of an astronomical body',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 200. P492 - OMIM ID
CREATE (:PropertyMapping {
  property_id: 'P492',
  property_label: 'OMIM ID',
  property_description: 'Online \"Mendelian Inheritance in Man\" catalogue codes for diseases, genes, or phenotypes',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 201. P6 - head of government
CREATE (:PropertyMapping {
  property_id: 'P6',
  property_label: 'head of government',
  property_description: 'head of the executive power of this town, city, municipality, state, country, or other governmental body',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 202. P10 - video
CREATE (:PropertyMapping {
  property_id: 'P10',
  property_label: 'video',
  property_description: 'relevant video; use property P18 for images; for film trailers, qualify with \"object has role\" (P3831)=\"trailer\" (Q622550); for films, qualify with \"object has role\" (P3831)=\"full video available on Wikimedia Commons\" (Q89347362)',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'ARTISTIC,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 203. P14 - traffic sign
CREATE (:PropertyMapping {
  property_id: 'P14',
  property_label: 'traffic sign',
  property_description: 'graphic symbol describing the item, used at the side of or above roads to give instructions or provide information to road users',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 204. P15 - route map
CREATE (:PropertyMapping {
  property_id: 'P15',
  property_label: 'route map',
  property_description: 'image of route map at Wikimedia Commons',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 205. P16 - transport network
CREATE (:PropertyMapping {
  property_id: 'P16',
  property_label: 'transport network',
  property_description: 'network the infrastructure is a part of',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 206. P17 - country
CREATE (:PropertyMapping {
  property_id: 'P17',
  property_label: 'country',
  property_description: 'sovereign state that this item is in (not to be used for human beings)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 207. P18 - image
CREATE (:PropertyMapping {
  property_id: 'P18',
  property_label: 'image',
  property_description: 'image of relevant illustration of the subject; if available, also use more specific properties (sample: coat of arms image, locator map, flag image, signature image, logo image, collage image)',
  primary_facet: 'CULTURAL',
  secondary_facets: 'ARTISTIC',
  all_facets: 'CULTURAL,ARTISTIC',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 6,
  imported_at: datetime()
});

// 208. P19 - place of birth
CREATE (:PropertyMapping {
  property_id: 'P19',
  property_label: 'place of birth',
  property_description: 'most specific known birth location of a person, animal or fictional character',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'DEMOGRAPHIC,BIOGRAPHIC',
  all_facets: 'GEOGRAPHIC,DEMOGRAPHIC,BIOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 209. P20 - place of death
CREATE (:PropertyMapping {
  property_id: 'P20',
  property_label: 'place of death',
  property_description: 'most specific known (e.g. city instead of country, or hospital instead of city) death location of a person, animal or fictional character',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'GEOGRAPHIC,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 210. P21 - sex or gender
CREATE (:PropertyMapping {
  property_id: 'P21',
  property_label: 'sex or gender',
  property_description: 'sex or gender identity of human or animal. For human: male, female, non-binary, intersex, transgender female, transgender male, agender, etc. For animal: male organism, female organism. Groups of same gender use subclass of (P279)',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 6,
  imported_at: datetime()
});

// 211. P22 - father
CREATE (:PropertyMapping {
  property_id: 'P22',
  property_label: 'father',
  property_description: 'male parent of the subject. For stepfather, use \"stepparent\" (P3448)',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'BIOGRAPHIC,DEMOGRAPHIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 212. P25 - mother
CREATE (:PropertyMapping {
  property_id: 'P25',
  property_label: 'mother',
  property_description: 'female parent of the subject. For stepmother, use \"stepparent\" (P3448)',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'BIOGRAPHIC,DEMOGRAPHIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 213. P26 - spouse
CREATE (:PropertyMapping {
  property_id: 'P26',
  property_label: 'spouse',
  property_description: 'the subject has the object as their spouse (husband, wife, partner, etc.). Use \"unmarried partner\" (P451) for non-married companions',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'SOCIAL',
  all_facets: 'BIOGRAPHIC,SOCIAL',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 214. P27 - country of citizenship
CREATE (:PropertyMapping {
  property_id: 'P27',
  property_label: 'country of citizenship',
  property_description: 'the object is a country that recognizes the subject as its citizen',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 215. P30 - continent
CREATE (:PropertyMapping {
  property_id: 'P30',
  property_label: 'continent',
  property_description: 'continent of which the subject is a part',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 216. P31 - instance of
CREATE (:PropertyMapping {
  property_id: 'P31',
  property_label: 'instance of',
  property_description: 'type to which this subject corresponds/belongs. Different from P279 (subclass of); for example: K2 is an instance of mountain; volcano is a subclass of mountain',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 217. P35 - head of state
CREATE (:PropertyMapping {
  property_id: 'P35',
  property_label: 'head of state',
  property_description: 'official with the highest formal authority in a country/state',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 218. P36 - capital
CREATE (:PropertyMapping {
  property_id: 'P36',
  property_label: 'capital',
  property_description: 'seat of government of a country, province, state or other type of administrative territorial entity',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 219. P37 - official language
CREATE (:PropertyMapping {
  property_id: 'P37',
  property_label: 'official language',
  property_description: 'language designated as official by this item',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 220. P38 - currency
CREATE (:PropertyMapping {
  property_id: 'P38',
  property_label: 'currency',
  property_description: 'currency used by item',
  primary_facet: 'ECONOMIC',
  secondary_facets: '',
  all_facets: 'ECONOMIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 221. P39 - position held
CREATE (:PropertyMapping {
  property_id: 'P39',
  property_label: 'position held',
  property_description: 'subject currently or formerly holds the object position or public office',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 222. P40 - child
CREATE (:PropertyMapping {
  property_id: 'P40',
  property_label: 'child',
  property_description: 'subject has object as child. Do not use for stepchildren—use \"relative\" (P1038), qualified with \"kinship to subject\" (P1039)',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'BIOGRAPHIC,DEMOGRAPHIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 223. P41 - flag image
CREATE (:PropertyMapping {
  property_id: 'P41',
  property_label: 'flag image',
  property_description: 'image of the item\'s flag',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 224. P47 - shares border with
CREATE (:PropertyMapping {
  property_id: 'P47',
  property_label: 'shares border with',
  property_description: 'countries or administrative subdivisions, of equal level, that this item borders, either by land or water. A single common point is enough.',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 225. P50 - author
CREATE (:PropertyMapping {
  property_id: 'P50',
  property_label: 'author',
  property_description: 'main creator(s) of a written work (use on works, not humans); use P2093 (author name string) when Wikidata item is unknown or does not exist',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'INTELLECTUAL,BIOGRAPHIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 226. P51 - audio
CREATE (:PropertyMapping {
  property_id: 'P51',
  property_label: 'audio',
  property_description: 'relevant sound. If available, use a more specific property. Samples: \"spoken text audio\" (P989), \"pronunciation audio\" (P443)',
  primary_facet: 'CULTURAL',
  secondary_facets: 'LINGUISTIC',
  all_facets: 'CULTURAL,LINGUISTIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 227. P53 - family
CREATE (:PropertyMapping {
  property_id: 'P53',
  property_label: 'family',
  property_description: 'family, including dynasty and nobility houses. Not family name (use P734 for family name).',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 228. P54 - member of sports team
CREATE (:PropertyMapping {
  property_id: 'P54',
  property_label: 'member of sports team',
  property_description: 'sports teams or clubs that the subject represents or represented',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 229. P57 - director
CREATE (:PropertyMapping {
  property_id: 'P57',
  property_label: 'director',
  property_description: 'director(s) of film, TV-series, stageplay, video game or similar',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 230. P58 - screenwriter
CREATE (:PropertyMapping {
  property_id: 'P58',
  property_label: 'screenwriter',
  property_description: 'person(s) who wrote the script for subject item',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'ARTISTIC,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 231. P59 - constellation
CREATE (:PropertyMapping {
  property_id: 'P59',
  property_label: 'constellation',
  property_description: 'the area of the celestial sphere of which the subject is a part (from a scientific standpoint, not an astrological one)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 232. P61 - discoverer or inventor
CREATE (:PropertyMapping {
  property_id: 'P61',
  property_label: 'discoverer or inventor',
  property_description: 'subject who discovered, first described, invented, or developed this discovery or invention or scientific hypothesis or theory',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'SCIENTIFIC',
  all_facets: 'GEOGRAPHIC,SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 233. P65 - site of astronomical discovery
CREATE (:PropertyMapping {
  property_id: 'P65',
  property_label: 'site of astronomical discovery',
  property_description: 'the place where an astronomical object was discovered (observatory, satellite)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'SCIENTIFIC',
  all_facets: 'GEOGRAPHIC,SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 234. P66 - ancestral home
CREATE (:PropertyMapping {
  property_id: 'P66',
  property_label: 'ancestral home',
  property_description: 'place of origin for ancestors of subject',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'GEOGRAPHIC,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 235. P69 - educated at
CREATE (:PropertyMapping {
  property_id: 'P69',
  property_label: 'educated at',
  property_description: 'educational institution attended by subject',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 236. P78 - top-level Internet domain
CREATE (:PropertyMapping {
  property_id: 'P78',
  property_label: 'top-level Internet domain',
  property_description: 'Internet domain name system top-level code',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 237. P81 - connecting line
CREATE (:PropertyMapping {
  property_id: 'P81',
  property_label: 'connecting line',
  property_description: 'railway line(s) subject is directly connected to',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 238. P84 - architect
CREATE (:PropertyMapping {
  property_id: 'P84',
  property_label: 'architect',
  property_description: 'person or architectural firm responsible for designing this building',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 239. P85 - anthem
CREATE (:PropertyMapping {
  property_id: 'P85',
  property_label: 'anthem',
  property_description: 'subject\'s official anthem',
  primary_facet: 'CULTURAL',
  secondary_facets: 'POLITICAL',
  all_facets: 'CULTURAL,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 240. P86 - composer
CREATE (:PropertyMapping {
  property_id: 'P86',
  property_label: 'composer',
  property_description: 'person(s) who wrote the music [for lyricist, use \"lyrics by\" (P676)]',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 241. P87 - librettist
CREATE (:PropertyMapping {
  property_id: 'P87',
  property_label: 'librettist',
  property_description: 'author of the libretto (words) of an opera, operetta, oratorio or cantata, or of the book of a musical',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'ARTISTIC,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 242. P88 - commissioned by
CREATE (:PropertyMapping {
  property_id: 'P88',
  property_label: 'commissioned by',
  property_description: 'person or organization that commissioned this work',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'ECONOMIC',
  all_facets: 'ARTISTIC,ECONOMIC',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 243. P91 - sexual orientation
CREATE (:PropertyMapping {
  property_id: 'P91',
  property_label: 'sexual orientation',
  property_description: 'the sexual orientation of the person relative to their declared gender — use ONLY IF they have stated it themselves, unambiguously, or it has been widely agreed upon by historians after their death',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 244. P92 - main regulatory text
CREATE (:PropertyMapping {
  property_id: 'P92',
  property_label: 'main regulatory text',
  property_description: 'text setting the main rules by which the subject is regulated',
  primary_facet: 'DIPLOMATIC',
  secondary_facets: '',
  all_facets: 'DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 245. P94 - coat of arms image
CREATE (:PropertyMapping {
  property_id: 'P94',
  property_label: 'coat of arms image',
  property_description: 'image of the item\'s coat of arms - for the shield part only use P4004',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 246. P97 - noble title
CREATE (:PropertyMapping {
  property_id: 'P97',
  property_label: 'noble title',
  property_description: 'titles held by the person',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 247. P98 - editor
CREATE (:PropertyMapping {
  property_id: 'P98',
  property_label: 'editor',
  property_description: 'person who checks and corrects a work (such as a book, newspaper, academic journal, etc.) to comply with a rules of certain genre. Also applies to person who establishes the text of an ancient written work or manuscript.',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 248. P101 - field of work
CREATE (:PropertyMapping {
  property_id: 'P101',
  property_label: 'field of work',
  property_description: 'specialization of a person or organization; see P106 for the occupation',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 249. P102 - member of political party
CREATE (:PropertyMapping {
  property_id: 'P102',
  property_label: 'member of political party',
  property_description: 'the political party of which a person is or has been a member or otherwise affiliated',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 250. P103 - native language
CREATE (:PropertyMapping {
  property_id: 'P103',
  property_label: 'native language',
  property_description: 'language or languages a person (or group) has learned from early childhood',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: 'LINGUISTIC',
  all_facets: 'DEMOGRAPHIC,LINGUISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 251. P105 - taxon rank
CREATE (:PropertyMapping {
  property_id: 'P105',
  property_label: 'taxon rank',
  property_description: 'level in a taxonomic hierarchy',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 252. P106 - occupation
CREATE (:PropertyMapping {
  property_id: 'P106',
  property_label: 'occupation',
  property_description: 'occupation of a person. See also \"field of work\" (Property:P101), \"position held\" (Property:P39). Not for groups of people. There, use \"field of work\" (Property:P101), \"industry\" (Property:P452), \"members have occupation\" (Property:P3989).',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 253. P108 - employer
CREATE (:PropertyMapping {
  property_id: 'P108',
  property_label: 'employer',
  property_description: 'person or organization for which the subject works or worked',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 254. P109 - signature
CREATE (:PropertyMapping {
  property_id: 'P109',
  property_label: 'signature',
  property_description: 'image of a person\'s signature',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 255. P110 - illustrator
CREATE (:PropertyMapping {
  property_id: 'P110',
  property_label: 'illustrator',
  property_description: 'person drawing the pictures or taking the photographs in a book or similar work',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 256. P111 - measured physical quantity
CREATE (:PropertyMapping {
  property_id: 'P111',
  property_label: 'measured physical quantity',
  property_description: 'value of a physical property expressed as number multiplied by a unit',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 257. P112 - founded by
CREATE (:PropertyMapping {
  property_id: 'P112',
  property_label: 'founded by',
  property_description: 'founder or co-founder of this organization, religion, place or entity',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'POLITICAL,ECONOMIC',
  all_facets: 'BIOGRAPHIC,POLITICAL,ECONOMIC',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 258. P113 - airline hub
CREATE (:PropertyMapping {
  property_id: 'P113',
  property_label: 'airline hub',
  property_description: 'airport that serves as a hub for an airline',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 259. P114 - airline alliance
CREATE (:PropertyMapping {
  property_id: 'P114',
  property_label: 'airline alliance',
  property_description: 'alliance the airline belongs to',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'ECONOMIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 260. P115 - home venue
CREATE (:PropertyMapping {
  property_id: 'P115',
  property_label: 'home venue',
  property_description: 'home stadium or venue of a sports team or performing arts organization',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 261. P117 - chemical structure
CREATE (:PropertyMapping {
  property_id: 'P117',
  property_label: 'chemical structure',
  property_description: 'image of a representation of the structure for a chemical compound',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 262. P118 - league or competition
CREATE (:PropertyMapping {
  property_id: 'P118',
  property_label: 'league or competition',
  property_description: 'league or competition in which team or player has played, or in which an event occurs',
  primary_facet: 'SOCIAL',
  secondary_facets: '',
  all_facets: 'SOCIAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 263. P119 - place of burial
CREATE (:PropertyMapping {
  property_id: 'P119',
  property_label: 'place of burial',
  property_description: 'location of grave, resting place, place of ash-scattering, etc. (e.g., town/city or cemetery) for a person or animal. There may be several places: e.g., re-burials, parts of body buried separately.',
  primary_facet: 'RELIGIOUS',
  secondary_facets: 'GEOGRAPHIC,ARCHAEOLOGICAL,BIOGRAPHIC',
  all_facets: 'RELIGIOUS,GEOGRAPHIC,ARCHAEOLOGICAL,BIOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 264. P121 - item operated
CREATE (:PropertyMapping {
  property_id: 'P121',
  property_label: 'item operated',
  property_description: 'equipment, installation or service operated by the subject',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 265. P122 - basic form of government
CREATE (:PropertyMapping {
  property_id: 'P122',
  property_label: 'basic form of government',
  property_description: 'subject\'s government',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 266. P123 - publisher
CREATE (:PropertyMapping {
  property_id: 'P123',
  property_label: 'publisher',
  property_description: 'organization or person responsible for publishing a work, such as a book, periodical, printed music, podcast, game or software',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'INTELLECTUAL,TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 267. P126 - maintained by
CREATE (:PropertyMapping {
  property_id: 'P126',
  property_label: 'maintained by',
  property_description: 'person or organization in charge of keeping the subject (for instance an infrastructure) in functioning order',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 268. P127 - owned by
CREATE (:PropertyMapping {
  property_id: 'P127',
  property_label: 'owned by',
  property_description: 'owner of the subject',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'ECONOMIC,POLITICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 269. P128 - regulates (molecular biology)
CREATE (:PropertyMapping {
  property_id: 'P128',
  property_label: 'regulates (molecular biology)',
  property_description: 'process regulated by a protein or RNA in molecular biology',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 270. P129 - physically interacts with
CREATE (:PropertyMapping {
  property_id: 'P129',
  property_label: 'physically interacts with',
  property_description: 'physical entity that the subject interacts with',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 271. P131 - located in the administrative territorial entity
CREATE (:PropertyMapping {
  property_id: 'P131',
  property_label: 'located in the administrative territorial entity',
  property_description: 'the item is located on the territory of the following administrative entity. Use P276 for specifying locations that are non-administrative places and for items about events. Use P1382 if the item falls only partially into the administrative entity',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 272. P135 - movement
CREATE (:PropertyMapping {
  property_id: 'P135',
  property_label: 'movement',
  property_description: 'literary, artistic, scientific or philosophical movement or scene associated with this person or work. For political ideologies use P1142.',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'INTELLECTUAL,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 273. P136 - genre
CREATE (:PropertyMapping {
  property_id: 'P136',
  property_label: 'genre',
  property_description: 'creative work\'s genre or an artist\'s field of work (P101). Use main subject (P921) to relate creative works to their topic',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'INTELLECTUAL,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 274. P137 - operator
CREATE (:PropertyMapping {
  property_id: 'P137',
  property_label: 'operator',
  property_description: 'person, profession, organization or entity that operates the equipment, facility, or service',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'ECONOMIC,TECHNOLOGICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 275. P138 - named after
CREATE (:PropertyMapping {
  property_id: 'P138',
  property_label: 'named after',
  property_description: 'entity or event that inspired the subject\'s name, or namesake (in at least one language). Qualifier \"applies to name\" (P5168) can be used to indicate which one',
  primary_facet: 'CULTURAL',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'CULTURAL,BIOGRAPHIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 276. P140 - religion or worldview
CREATE (:PropertyMapping {
  property_id: 'P140',
  property_label: 'religion or worldview',
  property_description: 'religion of a person, organization or religious building, or associated with this subject',
  primary_facet: 'RELIGIOUS',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'RELIGIOUS,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 277. P141 - IUCN conservation status
CREATE (:PropertyMapping {
  property_id: 'P141',
  property_label: 'IUCN conservation status',
  property_description: 'conservation status assigned by the International Union for Conservation of Nature',
  primary_facet: 'ENVIRONMENTAL',
  secondary_facets: 'SCIENTIFIC',
  all_facets: 'ENVIRONMENTAL,SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 278. P143 - imported from Wikimedia project
CREATE (:PropertyMapping {
  property_id: 'P143',
  property_label: 'imported from Wikimedia project',
  property_description: 'source of this claim\'s value; used in references section by bots or humans importing data from Wikimedia projects',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 279. P144 - based on
CREATE (:PropertyMapping {
  property_id: 'P144',
  property_label: 'based on',
  property_description: 'the work(s) or inputs used as the basis for subject item; for fictional analog use P1074',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 280. P149 - architectural style
CREATE (:PropertyMapping {
  property_id: 'P149',
  property_label: 'architectural style',
  property_description: 'architectural style of a structure',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'ARTISTIC',
  all_facets: 'INTELLECTUAL,ARTISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 281. P150 - contains the administrative territorial entity
CREATE (:PropertyMapping {
  property_id: 'P150',
  property_label: 'contains the administrative territorial entity',
  property_description: '(list of) direct subdivisions of an administrative territorial entity',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 282. P154 - logo image
CREATE (:PropertyMapping {
  property_id: 'P154',
  property_label: 'logo image',
  property_description: 'graphic mark or emblem commonly used by commercial enterprises, organizations and products',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'ECONOMIC,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 7,
  imported_at: datetime()
});

// 283. P155 - follows
CREATE (:PropertyMapping {
  property_id: 'P155',
  property_label: 'follows',
  property_description: 'immediately prior item in a series of which the subject is a part, preferably use as qualifier of P179 [if the subject has replaced the preceding item, e.g. political offices, use \"replaces\" (P1365)]',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 284. P156 - followed by
CREATE (:PropertyMapping {
  property_id: 'P156',
  property_label: 'followed by',
  property_description: 'immediately following item in a series of which the subject is a part, preferably use as qualifier of P179 [if the subject has been replaced, e.g. political offices, use \"replaced by\" (P1366)]',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 285. P157 - killed by
CREATE (:PropertyMapping {
  property_id: 'P157',
  property_label: 'killed by',
  property_description: 'person or organization who killed the subject',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'DIPLOMATIC',
  all_facets: 'BIOGRAPHIC,DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 286. P158 - seal image
CREATE (:PropertyMapping {
  property_id: 'P158',
  property_label: 'seal image',
  property_description: 'image of subject\'s seal (emblem)',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 287. P159 - headquarters location
CREATE (:PropertyMapping {
  property_id: 'P159',
  property_label: 'headquarters location',
  property_description: 'city or town where an organization\'s headquarters is or has been situated. Use P276 qualifier for specific building',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 288. P161 - cast member
CREATE (:PropertyMapping {
  property_id: 'P161',
  property_label: 'cast member',
  property_description: 'actor in the subject production [use \"character role\" (P453) and/or \"name of the character role\" (P4633) as qualifiers] [use \"voice actor\" (P725) for voice-only role] - [use \"recorded participant\" (P11108) for non-fiction productions]',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'ARTISTIC,BIOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 289. P162 - producer
CREATE (:PropertyMapping {
  property_id: 'P162',
  property_label: 'producer',
  property_description: 'person(s) who produced the film, musical work, theatrical production, etc. (for film, this does not include executive producers, associate producers, etc.) [for production company, use P272, video games - use P178]',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'ECONOMIC',
  all_facets: 'ARTISTIC,ECONOMIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 290. P163 - flag
CREATE (:PropertyMapping {
  property_id: 'P163',
  property_label: 'flag',
  property_description: 'subject\'s flag',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 291. P166 - award received
CREATE (:PropertyMapping {
  property_id: 'P166',
  property_label: 'award received',
  property_description: 'award or recognition received by a person, organization or creative work',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 292. P167 - structure replaced by
CREATE (:PropertyMapping {
  property_id: 'P167',
  property_label: 'structure replaced by',
  property_description: 'the item which replaced this building or structure, at the same geographic location',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'TECHNOLOGICAL,GEOGRAPHIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 293. P169 - chief executive officer
CREATE (:PropertyMapping {
  property_id: 'P169',
  property_label: 'chief executive officer',
  property_description: 'highest-ranking corporate officer appointed as the CEO within an organization',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'ECONOMIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 294. P170 - creator
CREATE (:PropertyMapping {
  property_id: 'P170',
  property_label: 'creator',
  property_description: 'maker of this creative work or other object (where no more specific property exists)',
  primary_facet: 'ARTISTIC',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'ARTISTIC,INTELLECTUAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 295. P171 - parent taxon
CREATE (:PropertyMapping {
  property_id: 'P171',
  property_label: 'parent taxon',
  property_description: 'closest parent taxon of the taxon in question',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 296. P172 - ethnic group
CREATE (:PropertyMapping {
  property_id: 'P172',
  property_label: 'ethnic group',
  property_description: 'subject\'s ethnicity (consensus is that a VERY high standard of proof is needed for this field to be used. In general this means 1) the subject claims it themselves, or 2) it is widely agreed on by scholars, or 3) is fictional and portrayed as such)',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 297. P175 - performer
CREATE (:PropertyMapping {
  property_id: 'P175',
  property_label: 'performer',
  property_description: 'actor, musician, band or other performer associated with this role or musical work',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 298. P176 - manufacturer
CREATE (:PropertyMapping {
  property_id: 'P176',
  property_label: 'manufacturer',
  property_description: '(main or final) manufacturer or producer of this product',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'ECONOMIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 299. P177 - crosses
CREATE (:PropertyMapping {
  property_id: 'P177',
  property_label: 'crosses',
  property_description: 'obstacle (body of water, road, railway...) which this bridge (ferry, ford) crosses over or this tunnel goes under',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 300. P178 - developer
CREATE (:PropertyMapping {
  property_id: 'P178',
  property_label: 'developer',
  property_description: 'organization or person that developed the item',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'INTELLECTUAL,TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 301. P717 - Minor Planet Center observatory code
CREATE (:PropertyMapping {
  property_id: 'P717',
  property_label: 'Minor Planet Center observatory code',
  property_description: 'identifier for an astronomical observatory assigned by the Minor Planet Center',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 302. P718 - Canmore ID
CREATE (:PropertyMapping {
  property_id: 'P718',
  property_label: 'Canmore ID',
  property_description: 'identifier in the Royal Commission on the Ancient and Historical Monuments of Scotland\'s Canmore database',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'GEOGRAPHIC,CULTURAL',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 303. P720 - asteroid spectral type
CREATE (:PropertyMapping {
  property_id: 'P720',
  property_label: 'asteroid spectral type',
  property_description: 'spectral classifications of asteroids based on spectral shape, color, and albedo',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 304. P721 - OKATO ID
CREATE (:PropertyMapping {
  property_id: 'P721',
  property_label: 'OKATO ID',
  property_description: 'identifier for every administrative unit in Russia',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 305. P722 - UIC station code
CREATE (:PropertyMapping {
  property_id: 'P722',
  property_label: 'UIC station code',
  property_description: 'identifier for a railway station in Europe, CIS countries, the Far East (China, Mongolia, Japan, Korea, Vietnam), North Africa and the Middle East',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 5,
  imported_at: datetime()
});

// 306. P723 - Digitale Bibliotheek voor de Nederlandse Letteren 
CREATE (:PropertyMapping {
  property_id: 'P723',
  property_label: 'Digitale Bibliotheek voor de Nederlandse Letteren author ID',
  property_description: 'identifier for an author on the DBNL-website for Dutch language authors',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'INTELLECTUAL,BIOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 307. P724 - Internet Archive ID
CREATE (:PropertyMapping {
  property_id: 'P724',
  property_label: 'Internet Archive ID',
  property_description: 'identifier for an item on the Internet Archive',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 1,
  imported_at: datetime()
});

// 308. P725 - voice actor
CREATE (:PropertyMapping {
  property_id: 'P725',
  property_label: 'voice actor',
  property_description: 'performer of a spoken role in a creative work such as animation, video game, radio drama, or dubbing over [use \"character role\" (P453) as qualifier] [use \"cast member\" (P161) for live acting]',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 309. P726 - candidate
CREATE (:PropertyMapping {
  property_id: 'P726',
  property_label: 'candidate',
  property_description: 'person or party that is an option for an office in this election',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 310. P729 - service entry
CREATE (:PropertyMapping {
  property_id: 'P729',
  property_label: 'service entry',
  property_description: 'date or point in time on which a piece or class of equipment entered operational service',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 311. P730 - service retirement
CREATE (:PropertyMapping {
  property_id: 'P730',
  property_label: 'service retirement',
  property_description: 'date or point in time on which a piece or class of equipment was retired from operational service ; use P2669 for end of a public service',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 312. P731 - Litholex ID
CREATE (:PropertyMapping {
  property_id: 'P731',
  property_label: 'Litholex ID',
  property_description: 'identifier in the Lithostratigraphic database of Germany maintained by the BGR',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'SCIENTIFIC,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 313. P732 - BGS Lexicon of Named Rock Units ID
CREATE (:PropertyMapping {
  property_id: 'P732',
  property_label: 'BGS Lexicon of Named Rock Units ID',
  property_description: 'identifier for a stratigraphic unit given by the British Geological Survey',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'SCIENTIFIC,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 314. P733 - DINOloket ID
CREATE (:PropertyMapping {
  property_id: 'P733',
  property_label: 'DINOloket ID',
  property_description: 'identifier from database of geologic units in the Netherlands (Data Informatie Nederlandse Ondergrond)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'SCIENTIFIC,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 315. P734 - family name
CREATE (:PropertyMapping {
  property_id: 'P734',
  property_label: 'family name',
  property_description: 'part of full name of person',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 316. P735 - given name
CREATE (:PropertyMapping {
  property_id: 'P735',
  property_label: 'given name',
  property_description: 'first name or another given name of this person; values used with the property should not link disambiguations nor family names',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 317. P736 - cover art by
CREATE (:PropertyMapping {
  property_id: 'P736',
  property_label: 'cover art by',
  property_description: 'name of person or team creating cover artwork for book, record album, single record etc.',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 318. P737 - influenced by
CREATE (:PropertyMapping {
  property_id: 'P737',
  property_label: 'influenced by',
  property_description: 'the subject (person, idea, etc.) was influenced or inspired by this object entity, e.g. \"Heidegger was influenced by Aristotle\"',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'INTELLECTUAL,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 319. P739 - ammunition
CREATE (:PropertyMapping {
  property_id: 'P739',
  property_label: 'ammunition',
  property_description: 'cartridge or other ammunition used by the subject firearm',
  primary_facet: 'MILITARY',
  secondary_facets: '',
  all_facets: 'MILITARY',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 320. P740 - location of formation
CREATE (:PropertyMapping {
  property_id: 'P740',
  property_label: 'location of formation',
  property_description: 'location where a group or organization was formed',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 321. P741 - playing hand
CREATE (:PropertyMapping {
  property_id: 'P741',
  property_label: 'playing hand',
  property_description: 'hand used to play a racket sport, cricket, fencing, or curling',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'SOCIAL',
  all_facets: 'BIOGRAPHIC,SOCIAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 322. P742 - pseudonym
CREATE (:PropertyMapping {
  property_id: 'P742',
  property_label: 'pseudonym',
  property_description: 'alias used by someone (for nickname use P1449)',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 323. P744 - asteroid family
CREATE (:PropertyMapping {
  property_id: 'P744',
  property_label: 'asteroid family',
  property_description: 'population of asteroids that share similar proper orbital elements',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 324. P745 - Low German Bibliography and Biography ID
CREATE (:PropertyMapping {
  property_id: 'P745',
  property_label: 'Low German Bibliography and Biography ID',
  property_description: 'identifier',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'INTELLECTUAL,BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 4,
  imported_at: datetime()
});

// 325. P746 - date of disappearance
CREATE (:PropertyMapping {
  property_id: 'P746',
  property_label: 'date of disappearance',
  property_description: 'date or point of time a missing person was seen or otherwise known to be alive for the last time',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 326. P747 - has edition or translation
CREATE (:PropertyMapping {
  property_id: 'P747',
  property_label: 'has edition or translation',
  property_description: 'item that is an edition or translation of this item',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 327. P748 - appointed by
CREATE (:PropertyMapping {
  property_id: 'P748',
  property_label: 'appointed by',
  property_description: 'who appointed the person to the position, can be used as a qualifier',
  primary_facet: 'POLITICAL',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'POLITICAL,BIOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 328. P749 - parent organization or unit
CREATE (:PropertyMapping {
  property_id: 'P749',
  property_label: 'parent organization or unit',
  property_description: 'parent organization or unit of an organization or unit, opposite of child organization or unit (P355); use instance of (P31) to distinguish organization (Q43229) and organization unit (Q10387680)',
  primary_facet: 'ECONOMIC',
  secondary_facets: '',
  all_facets: 'ECONOMIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 329. P750 - distributed by
CREATE (:PropertyMapping {
  property_id: 'P750',
  property_label: 'distributed by',
  property_description: 'distributor of a creative work; distributor for a record label; news agency; film distributor',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 330. P751 - introduced feature
CREATE (:PropertyMapping {
  property_id: 'P751',
  property_label: 'introduced feature',
  property_description: 'feature introduced by this version of a product item',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 331. P756 - removed feature
CREATE (:PropertyMapping {
  property_id: 'P756',
  property_label: 'removed feature',
  property_description: 'which feature was removed by this version of a product item',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 332. P757 - World Heritage Site ID
CREATE (:PropertyMapping {
  property_id: 'P757',
  property_label: 'World Heritage Site ID',
  property_description: 'the identifier for a site as assigned by UNESCO. Use on one item per site, link parts with property \"has part\" (P527)',
  primary_facet: 'CULTURAL',
  secondary_facets: 'DIPLOMATIC',
  all_facets: 'CULTURAL,DIPLOMATIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 333. P758 - Kulturminne ID
CREATE (:PropertyMapping {
  property_id: 'P758',
  property_label: 'Kulturminne ID',
  property_description: 'Norwegian heritage property identification number of Riksantikvaren (the Directorate for Cultural Heritage)',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 334. P759 - Alberta Register of Historic Places ID
CREATE (:PropertyMapping {
  property_id: 'P759',
  property_label: 'Alberta Register of Historic Places ID',
  property_description: 'identifier of historic resources in the Alberta Register of Historic Places',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 335. P760 - DPLA ID
CREATE (:PropertyMapping {
  property_id: 'P760',
  property_label: 'DPLA ID',
  property_description: 'identifier for books, paintings, films, museum objects and archival records that have been digitised throughout United States',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'CULTURAL',
  all_facets: 'INTELLECTUAL,CULTURAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 336. P761 - Lake ID (Sweden)
CREATE (:PropertyMapping {
  property_id: 'P761',
  property_label: 'Lake ID (Sweden)',
  property_description: 'Identification code for lakes in Sweden, for lakes important enough also used, with SE- prefix, as EU_CD',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 337. P762 - Czech cultural heritage ID
CREATE (:PropertyMapping {
  property_id: 'P762',
  property_label: 'Czech cultural heritage ID',
  property_description: 'identifier for cultural heritage properties in the Czech Republic',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 338. P763 - PEI Register of Historic Places ID
CREATE (:PropertyMapping {
  property_id: 'P763',
  property_label: 'PEI Register of Historic Places ID',
  property_description: 'identifier of a historic place in Prince Edward Island, Canada',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 339. P764 - OKTMO ID
CREATE (:PropertyMapping {
  property_id: 'P764',
  property_label: 'OKTMO ID',
  property_description: 'identifier in Classification on Objects territory of municipal formations (Russia)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 340. P765 - surface played on
CREATE (:PropertyMapping {
  property_id: 'P765',
  property_label: 'surface played on',
  property_description: 'the surface on which a sporting event is played',
  primary_facet: 'SOCIAL',
  secondary_facets: '',
  all_facets: 'SOCIAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 341. P767 - contributor to the creative work or subject
CREATE (:PropertyMapping {
  property_id: 'P767',
  property_label: 'contributor to the creative work or subject',
  property_description: 'person or organization that contributed to a subject: co-creator of a creative work or subject',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 342. P768 - electoral district
CREATE (:PropertyMapping {
  property_id: 'P768',
  property_label: 'electoral district',
  property_description: 'electoral district this person is representing, or of the office that is being contested. Use as qualifier for \"position held\" (P39) or \"office contested\" (P541) or \"candidacy in election\" (P3602)',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 343. P769 - significant drug interaction
CREATE (:PropertyMapping {
  property_id: 'P769',
  property_label: 'significant drug interaction',
  property_description: 'clinically significant interaction between two pharmacologically active substances (i.e., drugs and/or active metabolites) where concomitant intake can lead to altered effectiveness or adverse drug events.',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 344. P770 - cause of destruction
CREATE (:PropertyMapping {
  property_id: 'P770',
  property_label: 'cause of destruction',
  property_description: 'item which caused the destruction of the subject item',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 345. P771 - Swiss municipality code
CREATE (:PropertyMapping {
  property_id: 'P771',
  property_label: 'Swiss municipality code',
  property_description: 'identifier for a municipality in Switzerland',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 346. P772 - INE code
CREATE (:PropertyMapping {
  property_id: 'P772',
  property_label: 'INE code',
  property_description: 'identifier for Spanish populated entities, by the Spanish Statistical Office (INE)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 347. P773 - ISO 3166-3
CREATE (:PropertyMapping {
  property_id: 'P773',
  property_label: 'ISO 3166-3',
  property_description: 'identifier for a country name that has been deleted from ISO 3166-1 since its first publication in 1974',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 348. P774 - FIPS 55-3 (locations in the US)
CREATE (:PropertyMapping {
  property_id: 'P774',
  property_label: 'FIPS 55-3 (locations in the US)',
  property_description: 'identifier for places in the United States per former Federal Information Processing Standard FIPS 55-3',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 349. P775 - Swedish urban area code
CREATE (:PropertyMapping {
  property_id: 'P775',
  property_label: 'Swedish urban area code',
  property_description: 'alphanumeric code for an urban area in Sweden',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 350. P776 - Swedish minor urban area code
CREATE (:PropertyMapping {
  property_id: 'P776',
  property_label: 'Swedish minor urban area code',
  property_description: 'alphanumeric code for a minor urban area in Sweden',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 351. P777 - Swedish civil parish code/ATA code
CREATE (:PropertyMapping {
  property_id: 'P777',
  property_label: 'Swedish civil parish code/ATA code',
  property_description: 'identifier for a civil parish in Sweden',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 352. P778 - Church of Sweden parish code
CREATE (:PropertyMapping {
  property_id: 'P778',
  property_label: 'Church of Sweden parish code',
  property_description: 'identifier for a parish of the Church of Sweden',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 353. P779 - Church of Sweden Pastoratskod
CREATE (:PropertyMapping {
  property_id: 'P779',
  property_label: 'Church of Sweden Pastoratskod',
  property_description: 'identifier for a pastoral district of the Church of Sweden',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 354. P780 - symptoms and signs
CREATE (:PropertyMapping {
  property_id: 'P780',
  property_label: 'symptoms and signs',
  property_description: 'possible symptoms or signs of a medical condition',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 355. P781 - SIKART person ID
CREATE (:PropertyMapping {
  property_id: 'P781',
  property_label: 'SIKART person ID',
  property_description: 'identifier in SIKART, a biographical dictionary and a database on visual art in Switzerland and Liechtenstein',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 356. P782 - LAU
CREATE (:PropertyMapping {
  property_id: 'P782',
  property_label: 'LAU',
  property_description: 'alphanumeric code for a local administrative unit, comprising the municipalities and communes of the European Statistical System (ESS); renamed from NUTS 4 and NUTS 5',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 357. P783 - hymenium type
CREATE (:PropertyMapping {
  property_id: 'P783',
  property_label: 'hymenium type',
  property_description: 'type of spore-bearing surface of a mushroom',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 358. P784 - mushroom cap shape
CREATE (:PropertyMapping {
  property_id: 'P784',
  property_label: 'mushroom cap shape',
  property_description: 'property classifying the shape of the cap of a mushroom',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 359. P785 - hymenium attachment
CREATE (:PropertyMapping {
  property_id: 'P785',
  property_label: 'hymenium attachment',
  property_description: 'how the hymenium of the mushroom attaches to the stem',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 360. P786 - stipe character
CREATE (:PropertyMapping {
  property_id: 'P786',
  property_label: 'stipe character',
  property_description: 'indicates whether a mushroom has a universal or partial veil',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 361. P787 - spore print color
CREATE (:PropertyMapping {
  property_id: 'P787',
  property_label: 'spore print color',
  property_description: 'color of a mushroom spore print (see documentation for allowed values)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 362. P788 - mushroom ecological type
CREATE (:PropertyMapping {
  property_id: 'P788',
  property_label: 'mushroom ecological type',
  property_description: 'property classifying the ecological type of a mushroom',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 363. P789 - edibility
CREATE (:PropertyMapping {
  property_id: 'P789',
  property_label: 'edibility',
  property_description: 'whether a mushroom can be eaten or not',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 364. P790 - approved by
CREATE (:PropertyMapping {
  property_id: 'P790',
  property_label: 'approved by',
  property_description: 'item is approved by other item(s) [qualifier: statement is approved by other item(s)]',
  primary_facet: 'POLITICAL',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'POLITICAL,INTELLECTUAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 365. P791 - ISIL
CREATE (:PropertyMapping {
  property_id: 'P791',
  property_label: 'ISIL',
  property_description: 'identifier for a library or related organization',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 366. P792 - chapter
CREATE (:PropertyMapping {
  property_id: 'P792',
  property_label: 'chapter',
  property_description: 'title or number of the chapter where a claim is made',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 367. P793 - significant event
CREATE (:PropertyMapping {
  property_id: 'P793',
  property_label: 'significant event',
  property_description: 'significant or notable events associated with the subject',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 368. P795 - located on linear feature
CREATE (:PropertyMapping {
  property_id: 'P795',
  property_label: 'located on linear feature',
  property_description: 'linear feature along which distance is specified from a specified datum point',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 369. P797 - authority
CREATE (:PropertyMapping {
  property_id: 'P797',
  property_label: 'authority',
  property_description: 'entity having executive power on given entity',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 370. P798 - military designation
CREATE (:PropertyMapping {
  property_id: 'P798',
  property_label: 'military designation',
  property_description: 'officially assigned designation for a vehicle in military service',
  primary_facet: 'MILITARY',
  secondary_facets: '',
  all_facets: 'MILITARY',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 371. P799 - Air Ministry specification ID
CREATE (:PropertyMapping {
  property_id: 'P799',
  property_label: 'Air Ministry specification ID',
  property_description: 'identifier for an aircraft specification issued by the United Kingdom Air Ministry',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: 'MILITARY',
  all_facets: 'TECHNOLOGICAL,MILITARY',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 372. P800 - notable work
CREATE (:PropertyMapping {
  property_id: 'P800',
  property_label: 'notable work',
  property_description: 'notable scientific, artistic or literary work, or other work of significance among subject\'s works',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'INTELLECTUAL,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 373. P802 - student
CREATE (:PropertyMapping {
  property_id: 'P802',
  property_label: 'student',
  property_description: 'notable student(s) of the subject individual',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 374. P803 - professorship
CREATE (:PropertyMapping {
  property_id: 'P803',
  property_label: 'professorship',
  property_description: 'professorship position held by this academic person',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 375. P804 - GNIS Antarctica ID
CREATE (:PropertyMapping {
  property_id: 'P804',
  property_label: 'GNIS Antarctica ID',
  property_description: 'identifier for geographic objects in Antarctica, used in the US Geological Survey\'s Geographic Names Information System. For U.S. IDs, use Property:P590',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 376. P805 - statement is subject of
CREATE (:PropertyMapping {
  property_id: 'P805',
  property_label: 'statement is subject of',
  property_description: '(qualifying) item that describes the relation identified in this statement',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 377. P806 - Italian cadastre code (municipality)
CREATE (:PropertyMapping {
  property_id: 'P806',
  property_label: 'Italian cadastre code (municipality)',
  property_description: 'alphanumeric code for an Italian comune in the Codice catastale',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 378. P807 - separated from
CREATE (:PropertyMapping {
  property_id: 'P807',
  property_label: 'separated from',
  property_description: 'subject was founded or started by separating from identified object',
  primary_facet: 'POLITICAL',
  secondary_facets: 'SOCIAL',
  all_facets: 'POLITICAL,SOCIAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 379. P808 - Asset of cultural interest code
CREATE (:PropertyMapping {
  property_id: 'P808',
  property_label: 'Asset of cultural interest code',
  property_description: 'identifier for an item in the Spanish heritage register (included RI/ARI)',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 380. P809 - WDPA ID
CREATE (:PropertyMapping {
  property_id: 'P809',
  property_label: 'WDPA ID',
  property_description: 'identifier in World Database on Protected Areas',
  primary_facet: 'ENVIRONMENTAL',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'ENVIRONMENTAL,GEOGRAPHIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 381. P811 - academic minor
CREATE (:PropertyMapping {
  property_id: 'P811',
  property_label: 'academic minor',
  property_description: 'minor someone studied at college/university',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 382. P812 - academic major
CREATE (:PropertyMapping {
  property_id: 'P812',
  property_label: 'academic major',
  property_description: 'major someone studied at college/university',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 383. P813 - retrieved
CREATE (:PropertyMapping {
  property_id: 'P813',
  property_label: 'retrieved',
  property_description: 'date or point in time that information was retrieved from a database or website (for use in online sources)',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 384. P814 - IUCN protected areas category
CREATE (:PropertyMapping {
  property_id: 'P814',
  property_label: 'IUCN protected areas category',
  property_description: 'protected areas category by the World Commission on Protected Areas. Used with dedicated items for each category.',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 385. P815 - ITIS TSN
CREATE (:PropertyMapping {
  property_id: 'P815',
  property_label: 'ITIS TSN',
  property_description: 'identifier for a taxon in the Integrated Taxonomic Information System',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 386. P816 - decays to
CREATE (:PropertyMapping {
  property_id: 'P816',
  property_label: 'decays to',
  property_description: 'what isotope does this radioactive isotope decay to',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 387. P817 - decay mode
CREATE (:PropertyMapping {
  property_id: 'P817',
  property_label: 'decay mode',
  property_description: 'type of decay that a radioactive isotope undergoes (should be used as a qualifier for \"decays to\")',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 388. P818 - arXiv ID
CREATE (:PropertyMapping {
  property_id: 'P818',
  property_label: 'arXiv ID',
  property_description: 'identifier of a document in arXiv pre-print archive',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 389. P819 - ADS bibcode
CREATE (:PropertyMapping {
  property_id: 'P819',
  property_label: 'ADS bibcode',
  property_description: 'bibcode in the Astrophysics Data System',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 4,
  imported_at: datetime()
});

// 390. P820 - arXiv classification
CREATE (:PropertyMapping {
  property_id: 'P820',
  property_label: 'arXiv classification',
  property_description: 'arXiv classification of pre-print articles',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 391. P821 - CGNDB unique ID
CREATE (:PropertyMapping {
  property_id: 'P821',
  property_label: 'CGNDB unique ID',
  property_description: 'identifier(s) for a geographical feature contained in the Canadian Geographical Names Database (CGNDB)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 1,
  imported_at: datetime()
});

// 392. P822 - mascot
CREATE (:PropertyMapping {
  property_id: 'P822',
  property_label: 'mascot',
  property_description: 'mascot of an organization, e.g. a sports team or university',
  primary_facet: 'CULTURAL',
  secondary_facets: 'SOCIAL',
  all_facets: 'CULTURAL,SOCIAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 393. P823 - speaker
CREATE (:PropertyMapping {
  property_id: 'P823',
  property_label: 'speaker',
  property_description: 'person who is speaker for this event, ceremony, keynote, presentation or in a literary work',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 394. P824 - Meteoritical Bulletin Database ID
CREATE (:PropertyMapping {
  property_id: 'P824',
  property_label: 'Meteoritical Bulletin Database ID',
  property_description: 'identifier for a meteorite in the database of the Meteoritical Society',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 395. P825 - dedicated to
CREATE (:PropertyMapping {
  property_id: 'P825',
  property_label: 'dedicated to',
  property_description: 'person or organization to whom the subject was dedicated',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 396. P826 - tonality
CREATE (:PropertyMapping {
  property_id: 'P826',
  property_label: 'tonality',
  property_description: 'key of a musical composition',
  primary_facet: 'ARTISTIC',
  secondary_facets: '',
  all_facets: 'ARTISTIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 397. P827 - BBC programme ID
CREATE (:PropertyMapping {
  property_id: 'P827',
  property_label: 'BBC programme ID',
  property_description: 'identifier for the corresponding item on the BBC website and internal systems',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 398. P828 - has cause
CREATE (:PropertyMapping {
  property_id: 'P828',
  property_label: 'has cause',
  property_description: 'underlying cause, entity that ultimately resulted in this effect',
  primary_facet: 'CULTURAL',
  secondary_facets: 'POLITICAL,SOCIAL',
  all_facets: 'CULTURAL,POLITICAL,SOCIAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 399. P829 - OEIS ID
CREATE (:PropertyMapping {
  property_id: 'P829',
  property_label: 'OEIS ID',
  property_description: 'identifier on the On-Line Encyclopedia of Integer Sequences',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 400. P830 - Encyclopedia of Life ID
CREATE (:PropertyMapping {
  property_id: 'P830',
  property_label: 'Encyclopedia of Life ID',
  property_description: 'eol.org item reference number',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 401. P493 - ICD-9 ID
CREATE (:PropertyMapping {
  property_id: 'P493',
  property_label: 'ICD-9 ID',
  property_description: 'identifier in the ICD catalogue codes for diseases – Version 9',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 402. P494 - ICD-10 ID
CREATE (:PropertyMapping {
  property_id: 'P494',
  property_label: 'ICD-10 ID',
  property_description: 'identifier in the ICD Terminology of Diseases - Version 10',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 403. P495 - country of origin
CREATE (:PropertyMapping {
  property_id: 'P495',
  property_label: 'country of origin',
  property_description: 'country of origin of this item (creative work, food, phrase, product, etc.)',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 404. P496 - ORCID iD
CREATE (:PropertyMapping {
  property_id: 'P496',
  property_label: 'ORCID iD',
  property_description: 'identifier for a person',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'SCIENTIFIC,BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 5,
  imported_at: datetime()
});

// 405. P497 - CBDB ID
CREATE (:PropertyMapping {
  property_id: 'P497',
  property_label: 'CBDB ID',
  property_description: 'identifier for a person in the China Biographical Database',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 406. P498 - ISO 4217 code
CREATE (:PropertyMapping {
  property_id: 'P498',
  property_label: 'ISO 4217 code',
  property_description: 'identifier for a currency per ISO 4217',
  primary_facet: 'ECONOMIC',
  secondary_facets: '',
  all_facets: 'ECONOMIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 407. P500 - exclave of
CREATE (:PropertyMapping {
  property_id: 'P500',
  property_label: 'exclave of',
  property_description: 'territory is legally or politically attached to a main territory with which it is not physically contiguous because of surrounding alien territory. It may also be an enclave.',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 408. P501 - enclave within
CREATE (:PropertyMapping {
  property_id: 'P501',
  property_label: 'enclave within',
  property_description: 'territory is entirely surrounded (enclaved) by the other territory',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 409. P502 - HURDAT ID
CREATE (:PropertyMapping {
  property_id: 'P502',
  property_label: 'HURDAT ID',
  property_description: 'identifier per HURDAT (North Atlantic hurricane database)',
  primary_facet: 'ENVIRONMENTAL',
  secondary_facets: '',
  all_facets: 'ENVIRONMENTAL',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 410. P503 - ISO standard
CREATE (:PropertyMapping {
  property_id: 'P503',
  property_label: 'ISO standard',
  property_description: 'numeric identifier of this ISO standard',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 1,
  imported_at: datetime()
});

// 411. P504 - shipping port
CREATE (:PropertyMapping {
  property_id: 'P504',
  property_label: 'shipping port',
  property_description: 'shipping port of the vessel (if different from \"ship registry\"): For civilian ships, the primary port from which the ship operates. Port of registry →P532 should be listed in \"Ship registry\". For warships, this will be the ship\'s assigned naval base',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 412. P505 - general manager
CREATE (:PropertyMapping {
  property_id: 'P505',
  property_label: 'general manager',
  property_description: 'general manager of a sports team. If they are also an on-field manager use P286 instead',
  primary_facet: 'ECONOMIC',
  secondary_facets: 'SOCIAL',
  all_facets: 'ECONOMIC,SOCIAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 413. P506 - ISO 15924 alpha-4 code
CREATE (:PropertyMapping {
  property_id: 'P506',
  property_label: 'ISO 15924 alpha-4 code',
  property_description: '4-letter identifier for a script, writing system, or typeface/style used in one or more languages',
  primary_facet: 'LINGUISTIC',
  secondary_facets: '',
  all_facets: 'LINGUISTIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 414. P507 - Swedish county code
CREATE (:PropertyMapping {
  property_id: 'P507',
  property_label: 'Swedish county code',
  property_description: 'two-digit numeric identifier for a county in Sweden \"länskod\"',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 415. P508 - BNCF Thesaurus ID
CREATE (:PropertyMapping {
  property_id: 'P508',
  property_label: 'BNCF Thesaurus ID',
  property_description: 'identifier in the subject indexing tool of the National Central Library of Florence',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 416. P509 - cause of death
CREATE (:PropertyMapping {
  property_id: 'P509',
  property_label: 'cause of death',
  property_description: 'underlying or immediate cause of death. Underlying cause (e.g. car accident, stomach cancer) preferred. Use \'manner of death\' (P1196) for broadest category, e.g. natural causes, accident, homicide, suicide',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'BIOGRAPHIC,DEMOGRAPHIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 417. P511 - honorific prefix
CREATE (:PropertyMapping {
  property_id: 'P511',
  property_label: 'honorific prefix',
  property_description: 'word or expression used before a name, in addressing or referring to a person',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 418. P512 - academic degree
CREATE (:PropertyMapping {
  property_id: 'P512',
  property_label: 'academic degree',
  property_description: 'academic degree that the person holds',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 419. P514 - interleaves with
CREATE (:PropertyMapping {
  property_id: 'P514',
  property_label: 'interleaves with',
  property_description: 'stratigraphic relation in which two units overlap each other marginally',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'SCIENTIFIC,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 420. P515 - phase of matter
CREATE (:PropertyMapping {
  property_id: 'P515',
  property_label: 'phase of matter',
  property_description: 'state or phase of the matter at which the measure was made',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 421. P516 - powered by
CREATE (:PropertyMapping {
  property_id: 'P516',
  property_label: 'powered by',
  property_description: 'equipment or engine used by the subject to convert a source or energy into mechanical energy',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 422. P517 - interaction
CREATE (:PropertyMapping {
  property_id: 'P517',
  property_label: 'interaction',
  property_description: 'subset of the four fundamental forces (strong (Q11415), electromagnetic (Q849919), weak (Q11418), and gravitation (Q11412) with which a particle interacts',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 423. P518 - applies to part
CREATE (:PropertyMapping {
  property_id: 'P518',
  property_label: 'applies to part',
  property_description: 'part, aspect, or form of the item to which the claim applies',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 424. P520 - armament
CREATE (:PropertyMapping {
  property_id: 'P520',
  property_label: 'armament',
  property_description: 'equippable weapon item for the subject',
  primary_facet: 'MILITARY',
  secondary_facets: '',
  all_facets: 'MILITARY',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 425. P521 - scheduled service destination
CREATE (:PropertyMapping {
  property_id: 'P521',
  property_label: 'scheduled service destination',
  property_description: 'airport or station connected by regular direct service to the subject; for the destination of a trip see P1444',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 426. P522 - type of orbit
CREATE (:PropertyMapping {
  property_id: 'P522',
  property_label: 'type of orbit',
  property_description: 'orbit a satellite has around its central body',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 427. P523 - temporal range start
CREATE (:PropertyMapping {
  property_id: 'P523',
  property_label: 'temporal range start',
  property_description: 'the start of a process or appearance of a life form or geological unit relative to the geologic time scale',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'ENVIRONMENTAL',
  all_facets: 'SCIENTIFIC,ENVIRONMENTAL',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 428. P524 - temporal range end
CREATE (:PropertyMapping {
  property_id: 'P524',
  property_label: 'temporal range end',
  property_description: 'the end of a process such as a geological unit or extinction of a life form relative to the geologic time scale',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'ENVIRONMENTAL',
  all_facets: 'SCIENTIFIC,ENVIRONMENTAL',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 429. P525 - Swedish municipality code
CREATE (:PropertyMapping {
  property_id: 'P525',
  property_label: 'Swedish municipality code',
  property_description: 'four-digit numeric identifier for a municipality in Sweden \"kommunkod\"',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 430. P527 - has part(s)
CREATE (:PropertyMapping {
  property_id: 'P527',
  property_label: 'has part(s)',
  property_description: 'part of this subject; inverse property of \"part of\" (P361). See also \"has parts of the class\" (P2670).',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 431. P528 - catalog code
CREATE (:PropertyMapping {
  property_id: 'P528',
  property_label: 'catalog code',
  property_description: 'catalog name of an object, use with qualifier P972',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 432. P529 - runway
CREATE (:PropertyMapping {
  property_id: 'P529',
  property_label: 'runway',
  property_description: 'name (direction) of runway at airport/airfield/airstrip',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'TECHNOLOGICAL',
  all_facets: 'GEOGRAPHIC,TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 433. P530 - diplomatic relation
CREATE (:PropertyMapping {
  property_id: 'P530',
  property_label: 'diplomatic relation',
  property_description: 'diplomatic relations of the country',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 434. P531 - diplomatic mission sent
CREATE (:PropertyMapping {
  property_id: 'P531',
  property_label: 'diplomatic mission sent',
  property_description: 'location of diplomatic mission, i.e. consulate of A in the capital city of B',
  primary_facet: 'POLITICAL',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'POLITICAL,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 435. P532 - port of registry
CREATE (:PropertyMapping {
  property_id: 'P532',
  property_label: 'port of registry',
  property_description: 'ship\'s port of registry. This is generally painted on the ship\'s stern (for the \"home port\", see Property:P504)',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'ECONOMIC',
  all_facets: 'GEOGRAPHIC,ECONOMIC',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 436. P533 - target
CREATE (:PropertyMapping {
  property_id: 'P533',
  property_label: 'target',
  property_description: 'target of an attack or military operation',
  primary_facet: 'MILITARY',
  secondary_facets: '',
  all_facets: 'MILITARY',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 437. P534 - streak color
CREATE (:PropertyMapping {
  property_id: 'P534',
  property_label: 'streak color',
  property_description: 'color of a mineral or material when abraded',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 438. P535 - Find a Grave memorial ID
CREATE (:PropertyMapping {
  property_id: 'P535',
  property_label: 'Find a Grave memorial ID',
  property_description: 'identifier of an individual\'s burial place in the Find a Grave database',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 4,
  imported_at: datetime()
});

// 439. P536 - Association of Tennis Professionals player ID
CREATE (:PropertyMapping {
  property_id: 'P536',
  property_label: 'Association of Tennis Professionals player ID',
  property_description: 'identifier for a male tennis player at the website of the Association of Tennis Professionals (ATP)',
  primary_facet: 'SOCIAL',
  secondary_facets: '',
  all_facets: 'SOCIAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 440. P537 - twinning
CREATE (:PropertyMapping {
  property_id: 'P537',
  property_label: 'twinning',
  property_description: 'type of twins a crystal forms',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 441. P538 - mineral fracture
CREATE (:PropertyMapping {
  property_id: 'P538',
  property_label: 'mineral fracture',
  property_description: 'fracture types in a mineral',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 442. P539 - Museofile ID
CREATE (:PropertyMapping {
  property_id: 'P539',
  property_label: 'Museofile ID',
  property_description: 'identifier for a museum in the Museofile database of the French ministry of culture',
  primary_facet: 'CULTURAL',
  secondary_facets: 'INTELLECTUAL',
  all_facets: 'CULTURAL,INTELLECTUAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 443. P541 - office contested
CREATE (:PropertyMapping {
  property_id: 'P541',
  property_label: 'office contested',
  property_description: 'title of office which election will determine the next holder of',
  primary_facet: 'POLITICAL',
  secondary_facets: '',
  all_facets: 'POLITICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 444. P542 - officially opened by
CREATE (:PropertyMapping {
  property_id: 'P542',
  property_label: 'officially opened by',
  property_description: 'person that officially opened the event or place',
  primary_facet: 'POLITICAL',
  secondary_facets: 'CULTURAL',
  all_facets: 'POLITICAL,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 445. P543 - oath made by
CREATE (:PropertyMapping {
  property_id: 'P543',
  property_label: 'oath made by',
  property_description: 'person(s) that made the oath at an event, like the Olympic Games',
  primary_facet: 'SOCIAL',
  secondary_facets: 'CULTURAL',
  all_facets: 'SOCIAL,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 446. P545 - torch lit by
CREATE (:PropertyMapping {
  property_id: 'P545',
  property_label: 'torch lit by',
  property_description: 'person that lit the torch at an event, like the Olympic Games',
  primary_facet: 'SOCIAL',
  secondary_facets: 'CULTURAL',
  all_facets: 'SOCIAL,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 447. P546 - docking port
CREATE (:PropertyMapping {
  property_id: 'P546',
  property_label: 'docking port',
  property_description: 'intended docking port for a spacecraft',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 448. P547 - commemorates
CREATE (:PropertyMapping {
  property_id: 'P547',
  property_label: 'commemorates',
  property_description: 'what or whom is commemorated by the place, monument, memorial, or holiday',
  primary_facet: 'ARCHAEOLOGICAL',
  secondary_facets: '',
  all_facets: 'ARCHAEOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 449. P548 - version type
CREATE (:PropertyMapping {
  property_id: 'P548',
  property_label: 'version type',
  property_description: 'type of version (qualifier for P348, software version), e.g. alpha, beta, stable',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 450. P549 - Mathematics Genealogy Project ID
CREATE (:PropertyMapping {
  property_id: 'P549',
  property_label: 'Mathematics Genealogy Project ID',
  property_description: 'identifier for mathematicians and computer scientists at the Mathematics Genealogy Project',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 451. P550 - chivalric order
CREATE (:PropertyMapping {
  property_id: 'P550',
  property_label: 'chivalric order',
  property_description: 'the chivalric order which a person belongs to',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 452. P551 - residence
CREATE (:PropertyMapping {
  property_id: 'P551',
  property_label: 'residence',
  property_description: 'the place where the person is or has been, resident',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'GEOGRAPHIC,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 453. P552 - handedness
CREATE (:PropertyMapping {
  property_id: 'P552',
  property_label: 'handedness',
  property_description: 'handedness of the person',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 454. P553 - website account on
CREATE (:PropertyMapping {
  property_id: 'P553',
  property_label: 'website account on',
  property_description: 'website that the person or organization has an account on (use with P554) Note: only used with reliable source or if the person or organization disclosed it.',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 455. P554 - website username or ID
CREATE (:PropertyMapping {
  property_id: 'P554',
  property_label: 'website username or ID',
  property_description: 'username or identifier on a website that the person or movement has an account on, for use as qualifier of \"website account on\" (P553)',
  primary_facet: 'SOCIAL',
  secondary_facets: '',
  all_facets: 'SOCIAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 456. P555 - doubles record
CREATE (:PropertyMapping {
  property_id: 'P555',
  property_label: 'doubles record',
  property_description: 'win/lose balance for a player in doubles tournaments',
  primary_facet: 'SOCIAL',
  secondary_facets: '',
  all_facets: 'SOCIAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 457. P556 - crystal system
CREATE (:PropertyMapping {
  property_id: 'P556',
  property_label: 'crystal system',
  property_description: 'type of crystal for minerals and/or for crystal compounds',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 458. P557 - DiseasesDB
CREATE (:PropertyMapping {
  property_id: 'P557',
  property_label: 'DiseasesDB',
  property_description: 'identifier sourced on the Diseases Database',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 459. P559 - terminus
CREATE (:PropertyMapping {
  property_id: 'P559',
  property_label: 'terminus',
  property_description: 'the feature (intersecting road, train station, etc.) at the end of a linear feature',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 460. P560 - direction
CREATE (:PropertyMapping {
  property_id: 'P560',
  property_label: 'direction',
  property_description: 'relative direction of an entity',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 461. P561 - NATO reporting name
CREATE (:PropertyMapping {
  property_id: 'P561',
  property_label: 'NATO reporting name',
  property_description: 'official reporting name assigned by the ASCC for NATO use',
  primary_facet: 'MILITARY',
  secondary_facets: '',
  all_facets: 'MILITARY',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 462. P562 - central bank/issuer
CREATE (:PropertyMapping {
  property_id: 'P562',
  property_label: 'central bank/issuer',
  property_description: 'central bank or other issuing authority for the currency',
  primary_facet: 'ECONOMIC',
  secondary_facets: '',
  all_facets: 'ECONOMIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 463. P563 - ICD-O
CREATE (:PropertyMapping {
  property_id: 'P563',
  property_label: 'ICD-O',
  property_description: 'International Classification of Diseases for Oncology',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 464. P564 - singles record
CREATE (:PropertyMapping {
  property_id: 'P564',
  property_label: 'singles record',
  property_description: 'win/lose balance for a player in singles tournaments',
  primary_facet: 'SOCIAL',
  secondary_facets: '',
  all_facets: 'SOCIAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 465. P565 - crystal habit
CREATE (:PropertyMapping {
  property_id: 'P565',
  property_label: 'crystal habit',
  property_description: 'the form and proportions of a crystal or mineral',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 466. P566 - has basionym
CREATE (:PropertyMapping {
  property_id: 'P566',
  property_label: 'has basionym',
  property_description: 'the legitimate, previously published name on which a new combination or name at new rank is based',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 467. P567 - underlies
CREATE (:PropertyMapping {
  property_id: 'P567',
  property_label: 'underlies',
  property_description: 'stratigraphic unit that this unit lies under (i.e. the overlying unit)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'SCIENTIFIC,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 468. P568 - overlies
CREATE (:PropertyMapping {
  property_id: 'P568',
  property_label: 'overlies',
  property_description: 'stratigraphic unit that this unit lies over (i.e. the underlying unit)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'GEOGRAPHIC',
  all_facets: 'SCIENTIFIC,GEOGRAPHIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 469. P569 - date of birth
CREATE (:PropertyMapping {
  property_id: 'P569',
  property_label: 'date of birth',
  property_description: 'date on which the subject was born',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: 'BIOGRAPHIC',
  all_facets: 'DEMOGRAPHIC,BIOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 6,
  imported_at: datetime()
});

// 470. P570 - date of death
CREATE (:PropertyMapping {
  property_id: 'P570',
  property_label: 'date of death',
  property_description: 'date on which the subject died',
  primary_facet: 'DEMOGRAPHIC',
  secondary_facets: '',
  all_facets: 'DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 471. P571 - inception
CREATE (:PropertyMapping {
  property_id: 'P571',
  property_label: 'inception',
  property_description: 'time when an entity begins to exist; for date of official opening use P1619',
  primary_facet: 'CULTURAL',
  secondary_facets: 'POLITICAL,ECONOMIC',
  all_facets: 'CULTURAL,POLITICAL,ECONOMIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 472. P574 - year of publication of scientific name for taxon
CREATE (:PropertyMapping {
  property_id: 'P574',
  property_label: 'year of publication of scientific name for taxon',
  property_description: 'year when this taxon was formally described (for animals); year when this taxon name was formally established (for plants)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 473. P575 - time of discovery or invention
CREATE (:PropertyMapping {
  property_id: 'P575',
  property_label: 'time of discovery or invention',
  property_description: 'date or point in time when the item was discovered or invented',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: 'CULTURAL',
  all_facets: 'SCIENTIFIC,CULTURAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 474. P576 - dissolved, abolished or demolished date
CREATE (:PropertyMapping {
  property_id: 'P576',
  property_label: 'dissolved, abolished or demolished date',
  property_description: 'point in time at which the subject (organisation, building) ceased to exist; see \"date of official closure\" (P3999) for closing a facility, \"service retirement\" (P730) for retiring equipment, \"discontinued date\" (P2669) for stopping a product',
  primary_facet: 'CULTURAL',
  secondary_facets: 'POLITICAL,ECONOMIC',
  all_facets: 'CULTURAL,POLITICAL,ECONOMIC',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 475. P577 - publication date
CREATE (:PropertyMapping {
  property_id: 'P577',
  property_label: 'publication date',
  property_description: 'date or point in time when a work or product was first published or released',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: '',
  all_facets: 'INTELLECTUAL',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 476. P578 - Sandbox-TimeValue
CREATE (:PropertyMapping {
  property_id: 'P578',
  property_label: 'Sandbox-TimeValue',
  property_description: 'Sandbox property for value of type \"TimeValue\"',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.50,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 477. P579 - IMA status and/or rank
CREATE (:PropertyMapping {
  property_id: 'P579',
  property_label: 'IMA status and/or rank',
  property_description: 'status given to each mineral by the IMA (International Mineralogical Association)',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 478. P580 - start time
CREATE (:PropertyMapping {
  property_id: 'P580',
  property_label: 'start time',
  property_description: 'time an entity begins to exist or a statement starts being valid',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'POLITICAL,CULTURAL',
  all_facets: 'BIOGRAPHIC,POLITICAL,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 479. P582 - end time
CREATE (:PropertyMapping {
  property_id: 'P582',
  property_label: 'end time',
  property_description: 'moment when an entity ceases to exist and a statement stops being entirely valid or no longer be true',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: 'POLITICAL,CULTURAL',
  all_facets: 'BIOGRAPHIC,POLITICAL,CULTURAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 480. P585 - point in time
CREATE (:PropertyMapping {
  property_id: 'P585',
  property_label: 'point in time',
  property_description: 'date something took place, existed or a statement was true; for providing time use the \"refine date\" property (P4241)',
  primary_facet: 'CULTURAL',
  secondary_facets: '',
  all_facets: 'CULTURAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 481. P586 - IPNI author ID
CREATE (:PropertyMapping {
  property_id: 'P586',
  property_label: 'IPNI author ID',
  property_description: 'numerical identifier for a person in the International Plant Names Index',
  primary_facet: 'BIOGRAPHIC',
  secondary_facets: '',
  all_facets: 'BIOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 2,
  imported_at: datetime()
});

// 482. P587 - MMSI
CREATE (:PropertyMapping {
  property_id: 'P587',
  property_label: 'MMSI',
  property_description: 'identifier for a maritime VHF radio user, typically a ship or an inland radio station. Format 8 or 9 digits',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: true,
  type_count: 3,
  imported_at: datetime()
});

// 483. P588 - coolant
CREATE (:PropertyMapping {
  property_id: 'P588',
  property_label: 'coolant',
  property_description: 'substance used by the subject to dissipate excess thermal energy',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 484. P589 - point group
CREATE (:PropertyMapping {
  property_id: 'P589',
  property_label: 'point group',
  property_description: 'crystal subdivision',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 485. P590 - GNIS Feature ID
CREATE (:PropertyMapping {
  property_id: 'P590',
  property_label: 'GNIS Feature ID',
  property_description: 'identifier for geographic objects in the United States and U.S. territories issued by the USGS. For objects in Antarctica, use Property:P804',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 1.0,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: true,
  type_count: 1,
  imported_at: datetime()
});

// 486. P591 - EC enzyme number
CREATE (:PropertyMapping {
  property_id: 'P591',
  property_label: 'EC enzyme number',
  property_description: 'classification scheme for enzymes',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 487. P592 - ChEMBL ID
CREATE (:PropertyMapping {
  property_id: 'P592',
  property_label: 'ChEMBL ID',
  property_description: 'identifier from a chemical database of bioactive molecules with drug-like properties',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 488. P593 - HomoloGene ID
CREATE (:PropertyMapping {
  property_id: 'P593',
  property_label: 'HomoloGene ID',
  property_description: 'identifier in the HomoloGene database',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 489. P594 - Ensembl gene ID
CREATE (:PropertyMapping {
  property_id: 'P594',
  property_label: 'Ensembl gene ID',
  property_description: 'identifier for a gene as per the Ensembl (European Bioinformatics Institute and the Wellcome Trust Sanger Institute) database',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.95,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 1,
  imported_at: datetime()
});

// 490. P595 - Guide to Pharmacology Ligand ID
CREATE (:PropertyMapping {
  property_id: 'P595',
  property_label: 'Guide to Pharmacology Ligand ID',
  property_description: 'ligand identifier of the Guide to Pharmacology database',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.90,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 491. P597 - Women\'s Tennis Association player ID
CREATE (:PropertyMapping {
  property_id: 'P597',
  property_label: 'Women\'s Tennis Association player ID',
  property_description: 'identifier for a female tennis player at the website of the Women\'s Tennis Association (WTA)',
  primary_facet: 'SOCIAL',
  secondary_facets: '',
  all_facets: 'SOCIAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 492. P598 - commander of (DEPRECATED)
CREATE (:PropertyMapping {
  property_id: 'P598',
  property_label: 'commander of (DEPRECATED)',
  property_description: 'for persons who are notable as commanding officers, the units they commanded',
  primary_facet: 'MILITARY',
  secondary_facets: 'POLITICAL,DEMOGRAPHIC',
  all_facets: 'MILITARY,POLITICAL,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 4,
  imported_at: datetime()
});

// 493. P599 - International Tennis Federation player ID before 2
CREATE (:PropertyMapping {
  property_id: 'P599',
  property_label: 'International Tennis Federation player ID before 2020 (archived)',
  property_description: 'identifier for a tennis player at the International Tennis Federation (ITF) website before 2020 (current identifier is P8618)',
  primary_facet: 'SOCIAL',
  secondary_facets: '',
  all_facets: 'SOCIAL',
  confidence: 0.75,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 494. P600 - Wine AppDB ID
CREATE (:PropertyMapping {
  property_id: 'P600',
  property_label: 'Wine AppDB ID',
  property_description: 'identifier for an application in the AppDB of WineHQ',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.70,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 3,
  imported_at: datetime()
});

// 495. P604 - MedlinePlus ID
CREATE (:PropertyMapping {
  property_id: 'P604',
  property_label: 'MedlinePlus ID',
  property_description: 'health information from U.S. government agencies, and health-related organizations',
  primary_facet: 'SCIENTIFIC',
  secondary_facets: '',
  all_facets: 'SCIENTIFIC',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 496. P605 - NUTS code
CREATE (:PropertyMapping {
  property_id: 'P605',
  property_label: 'NUTS code',
  property_description: 'code for a region per NUTS (Nomenclature des unités territoriales statistiques), a geocode standard for referencing the administrative divisions of countries for statistical purposes',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: 'POLITICAL',
  all_facets: 'GEOGRAPHIC,POLITICAL',
  confidence: 0.85,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 497. P606 - first flight
CREATE (:PropertyMapping {
  property_id: 'P606',
  property_label: 'first flight',
  property_description: 'date or point in time on which aircraft, rocket, or airline first flew',
  primary_facet: 'TECHNOLOGICAL',
  secondary_facets: '',
  all_facets: 'TECHNOLOGICAL',
  confidence: 0.80,
  resolved_by: 'claude',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 498. P607 - participated in conflict
CREATE (:PropertyMapping {
  property_id: 'P607',
  property_label: 'participated in conflict',
  property_description: 'battles, wars or other military engagements in which the person or item participated',
  primary_facet: 'MILITARY',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'MILITARY,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 499. P608 - exhibition history
CREATE (:PropertyMapping {
  property_id: 'P608',
  property_label: 'exhibition history',
  property_description: 'exhibitions where the item is or was displayed',
  primary_facet: 'INTELLECTUAL',
  secondary_facets: 'DEMOGRAPHIC',
  all_facets: 'INTELLECTUAL,DEMOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});

// 500. P609 - terminus location
CREATE (:PropertyMapping {
  property_id: 'P609',
  property_label: 'terminus location',
  property_description: 'location of the terminus of a linear feature',
  primary_facet: 'GEOGRAPHIC',
  secondary_facets: '',
  all_facets: 'GEOGRAPHIC',
  confidence: 0.8,
  resolved_by: 'base_mapping',
  is_historical: false,
  is_authority_control: false,
  type_count: 2,
  imported_at: datetime()
});


// STEP 3: LINK TO FACET NODES

MATCH (pm:PropertyMapping)
WHERE pm.primary_facet IS NOT NULL AND pm.primary_facet <> 'UNKNOWN'
MATCH (f:Facet {key: pm.primary_facet})
MERGE (pm)-[:HAS_PRIMARY_FACET]->(f);


MATCH (pm:PropertyMapping)
WHERE pm.secondary_facets IS NOT NULL AND pm.secondary_facets <> ''
UNWIND split(pm.secondary_facets, ',') AS facet_key
MATCH (f:Facet {key: facet_key})
MERGE (pm)-[:HAS_SECONDARY_FACET]->(f);
