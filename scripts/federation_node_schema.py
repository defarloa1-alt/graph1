#!/usr/bin/env python3
"""
federation_node_schema.py
─────────────────────────
Shared contract for all federation survey scripts.

DESIGN PRINCIPLE
─────────────────
Adjacency emerges from shared alignment fields — not from manually
assigned dimension labels.

Every FederationNode carries up to six alignment fields:

    temporal_range   (start_year, end_year) in integer years, BCE negative
    spatial_anchor   Pleiades URI or coordinates string
    concept_ref      LCSH sh… URI
    person_ref       VIAF URI or DPRR URI
    text_ref         WorldCat work URI
    event_ref        Wikidata event QID

Two nodes from different federations are NEIGHBOURS if they share
a populated alignment field with compatible values:

    temporal_range overlap  → TEMPORAL neighbours
    same spatial_anchor     → GEOGRAPHIC neighbours
    same concept_ref        → INTELLECTUAL neighbours
    same person_ref         → SOCIAL/BIOGRAPHIC neighbours
    same text_ref           → BIBLIOGRAPHIC neighbours
    same event_ref          → EVENT neighbours

Dimensions are DERIVED from which alignment fields are present,
plus federation-default signals (DPRR always evidences POLITICAL, etc).

Survey scripts report what they know.
Schema structure determines adjacency.
Rules run on adjacency counts.

USAGE
─────
In survey scripts:
    from federation_node_schema import (
        Federation, FederationNode, FederationSurvey,
        new_survey, new_node, validate_survey
    )

In pipeline stages:
    survey = FederationSurvey.load("output/nodes/lcsh_roman_republic.json")
    for node in survey.nodes:
        print(node.id, node.active_dimensions)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# ENUMERATIONS
# ─────────────────────────────────────────────

class Federation(str, Enum):
    LCSH          = "lcsh"
    LCC           = "lcc"
    FAST          = "fast"
    PLEIADES      = "pleiades"
    PERIODO       = "periodo"
    DPRR          = "dprr"
    WORLDCAT      = "worldcat"
    WIKIDATA      = "wikidata"
    VIAF          = "viaf"
    GEONAMES      = "geonames"
    GETTY_TGN     = "getty_tgn"
    GETTY_AAT     = "getty_aat"
    TRISMEGISTOS  = "trismegistos"
    LGPN          = "lgpn"
    OTHER         = "other"


class Dimension(str, Enum):
    """
    The 18 canonical facets plus TEMPORAL.
    Derived from alignment fields + federation defaults.
    Never manually assigned by survey scripts.
    """
    ARCHAEOLOGICAL = "ARCHAEOLOGICAL"
    ARTISTIC       = "ARTISTIC"
    BIOGRAPHIC     = "BIOGRAPHIC"
    COMMUNICATION  = "COMMUNICATION"
    CULTURAL       = "CULTURAL"
    DEMOGRAPHIC    = "DEMOGRAPHIC"
    DIPLOMATIC     = "DIPLOMATIC"
    ECONOMIC       = "ECONOMIC"
    ENVIRONMENTAL  = "ENVIRONMENTAL"
    GEOGRAPHIC     = "GEOGRAPHIC"
    INTELLECTUAL   = "INTELLECTUAL"
    LINGUISTIC     = "LINGUISTIC"
    MILITARY       = "MILITARY"
    POLITICAL      = "POLITICAL"
    RELIGIOUS      = "RELIGIOUS"
    SCIENTIFIC     = "SCIENTIFIC"
    SOCIAL         = "SOCIAL"
    TECHNOLOGICAL  = "TECHNOLOGICAL"
    TEMPORAL       = "TEMPORAL"


class NodeStatus(str, Enum):
    RAW      = "raw"
    ALIGNED  = "aligned"
    ALIVE    = "alive"
    STUB     = "stub"
    DEAD     = "dead"
    MERGED   = "merged"
    SPAWN    = "spawn"


class PatternType(str, Enum):
    POLITY            = "POLITY"
    CONFLICT          = "CONFLICT"
    INSTITUTION       = "INSTITUTION"
    PERSON_POLITICAL  = "PERSON_POLITICAL"
    PERSON_CULTURAL   = "PERSON_CULTURAL"
    PLACE_POLITICAL   = "PLACE_POLITICAL"
    PLACE_SACRED      = "PLACE_SACRED"
    MOVEMENT          = "MOVEMENT"
    PRACTICE          = "PRACTICE"
    LEGAL_INSTRUMENT  = "LEGAL_INSTRUMENT"
    ECONOMIC_SYSTEM   = "ECONOMIC_SYSTEM"
    CULTURAL_PRODUCT  = "CULTURAL_PRODUCT"
    CRISIS            = "CRISIS"
    TRANSITION        = "TRANSITION"
    UNKNOWN           = "UNKNOWN"


# ─────────────────────────────────────────────
# ALIGNMENT FIELD → DIMENSION DERIVATION
# ─────────────────────────────────────────────

ALIGNMENT_FIELD_DIMENSIONS: dict[str, list[Dimension]] = {
    "temporal_range": [Dimension.TEMPORAL],
    "spatial_anchor": [Dimension.GEOGRAPHIC],
    "concept_ref":    [Dimension.INTELLECTUAL],
    "person_ref":     [Dimension.SOCIAL, Dimension.BIOGRAPHIC],
    "text_ref":       [Dimension.INTELLECTUAL],
    "event_ref":      [],   # resolved at alignment pass
}

FEDERATION_DEFAULT_DIMENSIONS: dict[str, list[Dimension]] = {
    Federation.LCSH.value:         [Dimension.INTELLECTUAL],
    Federation.LCC.value:          [Dimension.INTELLECTUAL],
    Federation.FAST.value:         [Dimension.INTELLECTUAL],
    Federation.PLEIADES.value:     [Dimension.GEOGRAPHIC],
    Federation.PERIODO.value:      [Dimension.TEMPORAL],
    Federation.DPRR.value:         [Dimension.POLITICAL, Dimension.SOCIAL],
    Federation.WORLDCAT.value:     [Dimension.INTELLECTUAL],
    Federation.WIKIDATA.value:     [],
    Federation.VIAF.value:         [Dimension.BIOGRAPHIC],
    Federation.GEONAMES.value:     [Dimension.GEOGRAPHIC],
    Federation.GETTY_TGN.value:    [Dimension.GEOGRAPHIC],
    Federation.GETTY_AAT.value:    [Dimension.CULTURAL, Dimension.ARTISTIC],
    Federation.TRISMEGISTOS.value: [Dimension.ARCHAEOLOGICAL, Dimension.LINGUISTIC],
    Federation.LGPN.value:         [Dimension.BIOGRAPHIC, Dimension.SOCIAL],
}

SURVIVAL_FLOOR_DIMS = {Dimension.POLITICAL.value, Dimension.GEOGRAPHIC.value}
SURVIVAL_MIN_TOTAL  = 4


# ─────────────────────────────────────────────
# FEDERATION NODE
# ─────────────────────────────────────────────

@dataclass
class FederationNode:
    """
    A single concept node returned by a federation survey.

    Required fields: id, label, federation
    Alignment fields: temporal_range, spatial_anchor, concept_ref,
                      person_ref, text_ref, event_ref
    Dimensions are derived — never set manually.
    """

    # Required
    id:          str
    label:       str
    federation:  str

    # Recommended
    uri:         str = ""
    domain:      str = ""
    alt_labels:  list = field(default_factory=list)
    scope_note:  str = ""

    # Alignment fields — the Game of Life grid coordinates
    temporal_range: Optional[tuple] = None   # (start_year, end_year)
    spatial_anchor: Optional[str]   = None   # Pleiades URI or "lat,lon"
    concept_ref:    Optional[str]   = None   # LCSH sh… URI
    person_ref:     Optional[str]   = None   # VIAF or DPRR URI
    text_ref:       Optional[str]   = None   # WorldCat work URI
    event_ref:      Optional[str]   = None   # Wikidata event QID

    # Wikidata hub
    wikidata_qid:   Optional[str]   = None

    # Federation-specific raw data
    properties:    dict = field(default_factory=dict)

    # Pipeline-assigned — not set by survey scripts
    aligned_ids:   dict = field(default_factory=dict)
    status:        str  = NodeStatus.RAW.value
    pattern_type:  str  = PatternType.UNKNOWN.value
    survey_depth:  int  = 0
    is_seed:       bool = False

    # ── Derived properties ────────────────────

    @property
    def active_alignment_fields(self) -> list[str]:
        out = []
        if self.temporal_range is not None: out.append("temporal_range")
        if self.spatial_anchor is not None: out.append("spatial_anchor")
        if self.concept_ref    is not None: out.append("concept_ref")
        if self.person_ref     is not None: out.append("person_ref")
        if self.text_ref       is not None: out.append("text_ref")
        if self.event_ref      is not None: out.append("event_ref")
        return out

    @property
    def active_dimensions(self) -> set[str]:
        dims: set[str] = set()
        for f in self.active_alignment_fields:
            for d in ALIGNMENT_FIELD_DIMENSIONS.get(f, []):
                dims.add(d.value)
        for d in FEDERATION_DEFAULT_DIMENSIONS.get(self.federation, []):
            dims.add(d.value)
        return dims

    @property
    def dimension_score(self) -> int:
        return len(self.active_dimensions)

    @property
    def has_floor(self) -> bool:
        return SURVIVAL_FLOOR_DIMS.issubset(self.active_dimensions)

    @property
    def survives(self) -> bool:
        return self.has_floor and self.dimension_score >= SURVIVAL_MIN_TOTAL

    # ── Adjacency ─────────────────────────────

    def adjacency(self, other: FederationNode) -> list[str]:
        """
        Shared alignment dimensions with another node.
        Non-empty = they are neighbours in the Game of Life grid.
        """
        shared = []

        if self.temporal_range and other.temporal_range:
            s1, e1 = self.temporal_range
            s2, e2 = other.temporal_range
            if s1 <= e2 and s2 <= e1:
                shared.append("TEMPORAL")

        if self.spatial_anchor and other.spatial_anchor:
            if _spatial_match(self.spatial_anchor, other.spatial_anchor):
                shared.append("GEOGRAPHIC")

        if self.concept_ref and other.concept_ref:
            if _norm_uri(self.concept_ref) == _norm_uri(other.concept_ref):
                shared.append("INTELLECTUAL")

        if self.person_ref and other.person_ref:
            if _norm_uri(self.person_ref) == _norm_uri(other.person_ref):
                shared.append("SOCIAL")

        if self.text_ref and other.text_ref:
            if _norm_uri(self.text_ref) == _norm_uri(other.text_ref):
                shared.append("BIBLIOGRAPHIC")

        if self.event_ref and other.event_ref:
            if self.event_ref == other.event_ref:
                shared.append("EVENT")

        return shared

    # ── Serialisation ─────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "label":          self.label,
            "federation":     self.federation,
            "uri":            self.uri,
            "domain":         self.domain,
            "alt_labels":     self.alt_labels,
            "scope_note":     self.scope_note,
            "temporal_range": list(self.temporal_range) if self.temporal_range else None,
            "spatial_anchor": self.spatial_anchor,
            "concept_ref":    self.concept_ref,
            "person_ref":     self.person_ref,
            "text_ref":       self.text_ref,
            "event_ref":      self.event_ref,
            "wikidata_qid":   self.wikidata_qid,
            "properties":     self.properties,
            "aligned_ids":    self.aligned_ids,
            "status":         self.status,
            "pattern_type":   self.pattern_type,
            "survey_depth":   self.survey_depth,
            "is_seed":        self.is_seed,
            # Derived — informational only, recomputed on load
            "_active_dimensions": sorted(self.active_dimensions),
            "_dimension_score":   self.dimension_score,
            "_survives":          self.survives,
            "_semantic_facet":    self.properties.get("semantic_facet"),
        }

    @classmethod
    def from_dict(cls, d: dict) -> FederationNode:
        d = {k: v for k, v in d.items() if not k.startswith("_")}
        tr = d.get("temporal_range")
        if tr and isinstance(tr, list):
            d["temporal_range"] = tuple(tr)
        return cls(**d)

    def __repr__(self):
        return (f"FederationNode({self.federation}:{self.id} "
                f"'{self.label[:35]}' "
                f"dims={self.dimension_score} "
                f"survives={self.survives})")


# ─────────────────────────────────────────────
# FEDERATION SURVEY
# ─────────────────────────────────────────────

@dataclass
class FederationSurvey:
    federation:  str
    domain:      str
    seed_id:     str
    seed_label:  str
    surveyed_at: str
    node_count:  int = 0
    nodes:       list = field(default_factory=list)
    meta:        dict = field(default_factory=dict)

    def add_node(self, node: FederationNode):
        self.nodes.append(node)
        self.node_count = len(self.nodes)

    def summary(self) -> dict:
        fields = ["temporal_range", "spatial_anchor", "concept_ref",
                  "person_ref", "text_ref", "event_ref", "wikidata_qid"]
        coverage = {f: sum(1 for n in self.nodes if getattr(n, f, None) is not None)
                    for f in fields}
        survivors = sum(1 for n in self.nodes if n.survives)
        return {
            "total_nodes":    self.node_count,
            "survivors":      survivors,
            "survival_rate":  round(survivors / self.node_count, 3) if self.node_count else 0,
            "field_coverage": coverage,
        }

    def to_dict(self) -> dict:
        return {
            "federation":  self.federation,
            "domain":      self.domain,
            "seed_id":     self.seed_id,
            "seed_label":  self.seed_label,
            "surveyed_at": self.surveyed_at,
            "node_count":  self.node_count,
            "meta":        self.meta,
            "summary":     self.summary(),
            "nodes":       [n.to_dict() for n in self.nodes],
        }

    @classmethod
    def from_dict(cls, d: dict) -> FederationSurvey:
        nodes = [FederationNode.from_dict(n) for n in d.get("nodes", [])]
        return cls(
            federation  = d["federation"],
            domain      = d["domain"],
            seed_id     = d["seed_id"],
            seed_label  = d["seed_label"],
            surveyed_at = d["surveyed_at"],
            node_count  = d.get("node_count", len(nodes)),
            nodes       = nodes,
            meta        = d.get("meta", {}),
        )

    def save(self, path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        s = self.summary()
        print(f"[{self.federation}] {p.name} — "
              f"{s['total_nodes']} nodes, "
              f"{s['survivors']} survive, "
              f"coverage: {s['field_coverage']}")

    @classmethod
    def load(cls, path) -> FederationSurvey:
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def __repr__(self):
        return (f"FederationSurvey({self.federation}/{self.domain} "
                f"{self.node_count} nodes @ {self.surveyed_at[:10]})")


# ─────────────────────────────────────────────
# FACTORIES
# ─────────────────────────────────────────────

def new_survey(federation: Federation, domain: str,
               seed_id: str, seed_label: str,
               meta: dict = None) -> FederationSurvey:
    return FederationSurvey(
        federation  = federation.value,
        domain      = domain,
        seed_id     = seed_id,
        seed_label  = seed_label,
        surveyed_at = datetime.now(timezone.utc).isoformat(),
        meta        = meta or {},
    )


def new_node(id: str, label: str, federation: Federation, domain: str,
             uri: str = "", depth: int = 0, is_seed: bool = False,
             wikidata_qid: str = None, properties: dict = None,
             scope_note: str = "", alt_labels: list = None,
             temporal_range: tuple = None, spatial_anchor: str = None,
             concept_ref: str = None, person_ref: str = None,
             text_ref: str = None, event_ref: str = None) -> FederationNode:
    return FederationNode(
        id=id, label=label, federation=federation.value, domain=domain,
        uri=uri, survey_depth=depth, is_seed=is_seed,
        wikidata_qid=wikidata_qid, properties=properties or {},
        scope_note=scope_note, alt_labels=alt_labels or [],
        temporal_range=temporal_range, spatial_anchor=spatial_anchor,
        concept_ref=concept_ref, person_ref=person_ref,
        text_ref=text_ref, event_ref=event_ref,
    )


# ─────────────────────────────────────────────
# ALIGNMENT HELPERS
# ─────────────────────────────────────────────

def _norm_uri(uri: str) -> str:
    return (uri or "").replace("https://", "http://").rstrip("/").lower()


def _spatial_match(a: str, b: str, threshold: float = 0.5) -> bool:
    if _norm_uri(a) == _norm_uri(b):
        return True
    try:
        lat1, lon1 = map(float, a.split(","))
        lat2, lon2 = map(float, b.split(","))
        return abs(lat1 - lat2) < threshold and abs(lon1 - lon2) < threshold
    except Exception:
        return False


def parse_temporal_from_lcsh(label: str) -> Optional[tuple]:
    bc_bc = re.search(r'(\d+)-(\d+)\s*B\.C\.', label)
    bc_ad = re.search(r'(\d+)\s*B\.C\.-(\d+)\s*A\.D\.', label)
    ad_ad = re.search(r'(\d+)-(\d+)\s*A\.D\.', label)
    single_bc = re.search(r'(\d+)\s*B\.C\.', label)
    if bc_bc:  return (-int(bc_bc.group(1)), -int(bc_bc.group(2)))
    if bc_ad:  return (-int(bc_ad.group(1)),  int(bc_ad.group(2)))
    if ad_ad:  return ( int(ad_ad.group(1)),  int(ad_ad.group(2)))
    if single_bc: return (-int(single_bc.group(1)), -int(single_bc.group(1)))
    return None


def validate_survey(survey: FederationSurvey) -> list[str]:
    warnings = []
    if not survey.nodes:
        warnings.append("Survey contains no nodes")
    if not survey.domain:
        warnings.append("Survey has no domain set")
    for node in survey.nodes:
        if not node.id:    warnings.append(f"Node missing id: '{node.label}'")
        if not node.label: warnings.append(f"Node {node.id} missing label")
        if not node.active_alignment_fields and not FEDERATION_DEFAULT_DIMENSIONS.get(node.federation):
            warnings.append(f"Node {node.id} has no alignment fields and no federation defaults")
    return warnings


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("Federation Node Schema v2 — alignment-field-first")
    print("=" * 55)
    print()

    ROME_PLEIADES = "https://pleiades.stoa.org/places/423025"

    # LCSH — provides temporal from label, concept from URI
    lcsh_node = new_node(
        id="sh85115114", label="Rome--History--Republic, 510-30 B.C.",
        federation=Federation.LCSH, domain="roman_republic",
        uri="https://id.loc.gov/authorities/subjects/sh85115114",
        is_seed=True,
        concept_ref   = "https://id.loc.gov/authorities/subjects/sh85115114",
        temporal_range = parse_temporal_from_lcsh("Rome--History--Republic, 510-30 B.C."),
        # spatial_anchor not set — LCSH can't self-provide Pleiades URI
    )

    # Pleiades — provides spatial + temporal from attestation
    pleiades_node = new_node(
        id="423025", label="Roma",
        federation=Federation.PLEIADES, domain="roman_republic",
        uri=ROME_PLEIADES,
        spatial_anchor = ROME_PLEIADES,
        temporal_range = (-753, 476),
        wikidata_qid   = "Q220",
    )

    # DPRR — provides political + social defaults + spatial (Rome) + temporal
    dprr_node = new_node(
        id="off-0001", label="Consul",
        federation=Federation.DPRR, domain="roman_republic",
        uri="http://romanrepublic.ac.uk/office/1",
        spatial_anchor = ROME_PLEIADES,
        temporal_range = (-509, -27),
        properties     = {"office_latin": "consul", "holders": 1038},
    )

    # PeriodO — provides temporal definition
    periodo_node = new_node(
        id="p0rl7n", label="Roman Republic",
        federation=Federation.PERIODO, domain="roman_republic",
        uri="http://n2t.net/ark:/99152/p0rl7n",
        temporal_range = (-509, -27),
        spatial_anchor = ROME_PLEIADES,
    )

    print("NODE DIMENSIONS (derived from alignment fields + defaults):")
    for node in [lcsh_node, pleiades_node, dprr_node, periodo_node]:
        print(f"\n  {node.federation.upper():12} {node.label[:40]}")
        print(f"  align fields: {node.active_alignment_fields}")
        print(f"  dimensions:   {sorted(node.active_dimensions)}")
        print(f"  score={node.dimension_score}  floor={node.has_floor}  survives={node.survives}")

    print("\nADJACENCY MATRIX:")
    nodes = [lcsh_node, pleiades_node, dprr_node, periodo_node]
    names = ["LCSH", "Pleiades", "DPRR", "PeriodO"]
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if j <= i: continue
            adj = a.adjacency(b)
            if adj:
                print(f"  {names[i]:10} ↔ {names[j]:10}  {adj}")

    print("\nKEY FINDING:")
    print("  LCSH alone: no floor (missing POLITICAL from alignment fields)")
    print("  LCSH + DPRR: temporal overlap → TEMPORAL neighbour")
    print("  Pleiades + DPRR: same spatial_anchor → GEOGRAPHIC neighbour")
    print("  Pleiades + DPRR + temporal overlap → 2 shared dimensions")
    print("  DPRR survives because defaults give POLITICAL + GEOGRAPHIC via spatial_anchor")
    print()

    # Round-trip
    survey = new_survey(Federation.LCSH, "roman_republic",
                        "sh85115114", "Rome--History--Republic, 510-30 B.C.")
    survey.add_node(lcsh_node)
    survey.save("/tmp/test_v2.json")
    reloaded = FederationSurvey.load("/tmp/test_v2.json")
    rn = reloaded.nodes[0]
    print(f"Round-trip: temporal_range={rn.temporal_range}  dims={sorted(rn.active_dimensions)}")
    print("\nSchema v2 ready.")
