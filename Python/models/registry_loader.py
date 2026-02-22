"""
Registry Loader for Chrystallum

Loads canonical facet and relationship registries from JSON and CSV, with caching.
Enables runtime validation of facet keys, relationship types, and allowed values.

Usage:
    loader = RegistryLoader(facet_json_path, relationship_csv_path)
    facet_keys = loader.get_canonical_facet_keys()
    rel_types = loader.get_canonical_relationship_types()
    facet_config = loader.get_facet(key="archaeological")
"""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FacetConfig:
    """Represents a single facet from the registry."""
    key: str
    facet_class: str
    label: str
    definition: str
    lifecycle_status: str
    anchor_count: int
    anchors: List[Dict[str, str]]
    quality_flags: Optional[List[str]] = None
    source_priority: str = "latest"

    @classmethod
    def from_json(cls, obj: dict) -> "FacetConfig":
        """Create from JSON registry entry."""
        return cls(
            key=obj["key"],
            facet_class=obj["facet_class"],
            label=obj["label"],
            definition=obj["definition"],
            lifecycle_status=obj.get("lifecycle_status", "active"),
            anchor_count=obj.get("anchor_count", 0),
            anchors=obj.get("anchors", []),
            quality_flags=obj.get("quality_flags", []),
            source_priority=obj.get("source_priority", "latest"),
        )


@dataclass
class RelationshipConfig:
    """Represents a single relationship type from the registry."""
    relationship_type: str
    category: str
    description: str
    directionality: str
    lifecycle_status: str
    wikidata_property: Optional[str] = None
    parent_relationship: Optional[str] = None
    cidoc_crm_code: Optional[str] = None
    crminf_applicable: bool = False
    status: str = "candidate"

    @classmethod
    def from_csv_row(cls, row: dict) -> "RelationshipConfig":
        """Create from CSV registry row."""
        return cls(
            relationship_type=row["relationship_type"],
            category=row.get("category", "Unknown"),
            description=row.get("description", ""),
            directionality=row.get("directionality", "forward"),
            lifecycle_status=row.get("lifecycle_status", "candidate"),
            wikidata_property=row.get("wikidata_property") or None,
            parent_relationship=row.get("parent_relationship") or None,
            cidoc_crm_code=row.get("cidoc_crm_code") or None,
            crminf_applicable=row.get("crminf_applicable", "false").lower() == "true",
            status=row.get("status", "candidate"),
        )


class RegistryLoader:
    """
    Loads and caches canonical registries for facets and relationship types.
    
    Provides fast lookups and validation methods for Pydantic models.
    """

    def __init__(
        self,
        facet_json_path: Path,
        relationship_csv_path: Path,
    ):
        """
        Initialize registry loader.
        
        Args:
            facet_json_path: Path to facet_registry_master.json
            relationship_csv_path: Path to relationship_types_registry_master.csv
        """
        self.facet_json_path = Path(facet_json_path)
        self.relationship_csv_path = Path(relationship_csv_path)

        # Internal caches
        self._facets: Optional[Dict[str, FacetConfig]] = None
        self._relationships: Optional[Dict[str, RelationshipConfig]] = None
        self._facet_keys_canonical: Optional[Set[str]] = None
        self._relationship_types_canonical: Optional[Set[str]] = None

    def load_facets(self) -> Dict[str, FacetConfig]:
        """Load facet registry from JSON (cached)."""
        if self._facets is not None:
            return self._facets

        try:
            with open(self.facet_json_path, "r") as f:
                data = json.load(f)

            self._facets = {}
            for facet_obj in data.get("facets", []):
                config = FacetConfig.from_json(facet_obj)
                self._facets[config.key] = config

            logger.info(
                f"Loaded {len(self._facets)} facets from {self.facet_json_path.name}"
            )
            return self._facets
        except Exception as e:
            logger.error(f"Failed to load facet registry: {e}")
            raise

    def load_relationships(self) -> Dict[str, RelationshipConfig]:
        """Load relationship registry from CSV (cached)."""
        if self._relationships is not None:
            return self._relationships

        try:
            self._relationships = {}
            with open(self.relationship_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    config = RelationshipConfig.from_csv_row(row)
                    self._relationships[config.relationship_type] = config

            logger.info(
                f"Loaded {len(self._relationships)} relationship types from "
                f"{self.relationship_csv_path.name}"
            )
            return self._relationships
        except Exception as e:
            logger.error(f"Failed to load relationship registry: {e}")
            raise

    def get_canonical_facet_keys(self) -> Set[str]:
        """Get set of all canonical (UPPERCASE) facet keys."""
        if self._facet_keys_canonical is None:
            facets = self.load_facets()
            self._facet_keys_canonical = set(facets.keys())
        return self._facet_keys_canonical

    def get_canonical_facet_keys_uppercase(self) -> Set[str]:
        """Get set of canonical facet keys in UPPERCASE."""
        return {k.upper() for k in self.get_canonical_facet_keys()}

    def get_canonical_relationship_types(self) -> Set[str]:
        """Get set of all canonical relationship types."""
        if self._relationship_types_canonical is None:
            relationships = self.load_relationships()
            self._relationship_types_canonical = set(relationships.keys())
        return self._relationship_types_canonical

    def get_facet(self, key: str) -> Optional[FacetConfig]:
        """Get facet config by lowercase key."""
        facets = self.load_facets()
        return facets.get(key.lower())

    def is_valid_facet_key(self, key: str) -> bool:
        """Check if facet key is canonical (case-insensitive)."""
        return key.lower() in self.get_canonical_facet_keys()

    def is_valid_relationship_type(self, rel_type: str) -> bool:
        """Check if relationship type is canonical."""
        return rel_type.upper() in {r.upper() for r in self.get_canonical_relationship_types()}

    def get_facet_count(self) -> int:
        """Get total number of canonical facets."""
        return len(self.get_canonical_facet_keys())

    def get_relationship_count(self) -> int:
        """Get total number of canonical relationship types."""
        return len(self.get_canonical_relationship_types())

    def get_facets_by_category(self, category: str) -> List[str]:
        """Get facet keys by category (not currently used, placeholder)."""
        # Currently facets don't have category field in registry
        # but this is here for future extensibility
        return []

    def get_relationships_by_category(self, category: str) -> List[str]:
        """Get relationship types by category."""
        relationships = self.load_relationships()
        return [
            rel_type
            for rel_type, config in relationships.items()
            if config.category == category
        ]

    def get_relationships_by_status(self, status: str) -> List[str]:
        """Get relationship types by implementation status (e.g., 'implemented')."""
        relationships = self.load_relationships()
        return [
            rel_type
            for rel_type, config in relationships.items()
            if config.status == status
        ]

    def validate_and_normalize_facet(self, facet: str) -> str:
        """
        Validate facet and return normalized (lowercase) key.
        
        Raises ValueError if facet is not canonical.
        """
        normalized = facet.lower()
        if not self.is_valid_facet_key(normalized):
            valid_facets = sorted(self.get_canonical_facet_keys())
            raise ValueError(
                f"Invalid facet '{facet}'. Must be one of: {', '.join(valid_facets)}"
            )
        return normalized

    def validate_and_normalize_relationship_type(self, rel_type: str) -> str:
        """
        Validate relationship type and return normalized (uppercase) key.
        
        Raises ValueError if relationship type is not canonical.
        """
        normalized = rel_type.upper()
        valid_types = self.get_canonical_relationship_types()
        if normalized not in valid_types:
            raise ValueError(
                f"Invalid relationship type '{rel_type}'. "
                f"Must be a canonical type from relationship_types_registry_master.csv"
            )
        return normalized

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics about loaded registries."""
        return {
            "facet_count": self.get_facet_count(),
            "relationship_count": self.get_relationship_count(),
            "facet_keys": sorted(self.get_canonical_facet_keys()),
            "facets_loaded": self._facets is not None,
            "relationships_loaded": self._relationships is not None,
        }
