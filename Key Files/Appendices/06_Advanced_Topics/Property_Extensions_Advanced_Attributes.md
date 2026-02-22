# Appendix N: Property Extensions Advanced Attributes

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

# **Appendix N: Property Extensions and Advanced Attributes**

## **N.1 Purpose**

Defines optional-but-supported extension properties that enrich entities without breaking base schema compatibility.

## **N.2 Authoritative Files**

- `md/Reference/Entity_Property_Extensions.md`
- `md/Reference/Property_Extensions_Implementation_Guide.md`
- `md/Reference/Property_Extensions_Summary.md`

## **N.3 Extension Groups**

### Place Extensions

- `geo_coordinates`
- `pleiades_id`, `pleiades_link`
- `google_earth_link`
- optional geometry payload (`geo_json`)

### Temporal Extensions

- `end_date`
- `date_precision`
- `temporal_uncertainty`

### Backbone Extensions

- `backbone_fast`
- `backbone_lcc`
- `backbone_lcsh`
- `backbone_marc`

### Person/Work Discovery Extensions

- image metadata (`image_url`, `image_source`, `image_license`)
- related works arrays (`related_fiction`, `related_art`, `related_nonfiction`)
- online text availability metadata

## **N.4 Validation Rules**

1. Extension properties must not replace core required properties.
2. Keep external IDs as atomic strings.
3. Validate URL and coordinate formats before write.
4. Treat extension blocks as forward-compatible optional schema.

## **N.5 Recommended Rollout**

- Phase 1: temporal and backbone extensions
- Phase 2: geographic extension enrichment
- Phase 3: person/work media and online text extensions

---

**(End of Appendix N)**

---

