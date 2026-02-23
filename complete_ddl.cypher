// Roman Republic: organization that ALSO defines a temporal scope
(:Entity:Organization:TemporalAnchor {
  entity_cipher: "ent_org_Q17167",
  entity_type: "ORGANIZATION",          // Primary classification
  qid: "Q17167",
  
  // Temporal anchor properties
  is_temporal_anchor: true,              // Application-layer flag
  temporal_scope: "-0509/-0027",         // ISO 8601 interval (canonical)
  temporal_start_year: -509,             // Integer for range queries
  temporal_end_year: -27,                // Integer for range queries
  temporal_calendar: "julian",           // Calendar system metadata
  
  // Standard entity properties
  label_en: "Roman Republic",
  namespace: "wd"
})

// Stone Age: purely a temporal designation (not an institution)
(:Entity:Period:TemporalAnchor {
  entity_cipher: "ent_prd_Q6813",
  entity_type: "PERIOD",                 // Primary classification
  qid: "Q6813",
  
  is_temporal_anchor: true,
  temporal_scope: "-3300/-1200",
  temporal_start_year: -3300,
  temporal_end_year: -1200,
  temporal_calendar: "gregorian_approx"
})
