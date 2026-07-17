// Script 19a — Facet audit properties
// Sets di_trainable, facet_type, skip_reason on all 18 Facet nodes.
// facet_type values: subject_domain | method | epistemic_dimension | covered
// di_trainable=false means batch_train.py skips this facet by default.

// Subject domains — trainable
MATCH (f:Facet) WHERE f.key IN ['ARCHAEOLOGICAL','ARTISTIC','COMMUNICATION','DEMOGRAPHIC',
  'DIPLOMATIC','ECONOMIC','ENVIRONMENTAL','INTELLECTUAL','LINGUISTIC','MILITARY',
  'POLITICAL','RELIGIOUS','SCIENTIFIC','SOCIAL','TECHNOLOGICAL']
SET f.facet_type = 'subject_domain',
    f.di_trainable = true,
    f.skip_reason = null;

// BIOGRAPHIC — method, not subject domain
MATCH (f:Facet {key: 'BIOGRAPHIC'})
SET f.facet_type = 'method',
    f.di_trainable = false,
    f.skip_reason = 'Prosopography is a methodology for studying persons, not a subject domain';

// CULTURAL — epistemic dimension, cross-cutting
MATCH (f:Facet {key: 'CULTURAL'})
SET f.facet_type = 'epistemic_dimension',
    f.di_trainable = false,
    f.skip_reason = 'Cross-cutting epistemic lens; too broad to produce coherent subject SCs';

// GEOGRAPHIC — covered by geo_bootstrap
MATCH (f:Facet {key: 'GEOGRAPHIC'})
SET f.facet_type = 'covered',
    f.di_trainable = false,
    f.skip_reason = 'Covered by geo_bootstrap (7 SCs, 50k+ Place members already populated)';
