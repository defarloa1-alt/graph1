"""GeoNames, read from the preserved dumps: the modern administrative tree, and the
populated places that bridge ancient places to it.

One pass over allCountries keeps the continents, the administrative units of the
strict tree, the features Pleiades names, and the populated places in the grid
cells around ancient places (for the nearest-place bridge). Countries and their
continents come from countryInfo; ADM1 and ADM2 units are the ones the code lists
name; a unit's parent is the nearest higher level its codes name, and ADM5 units,
whose code is not in allCountries, take their parent from hierarchy.txt.
"""

from __future__ import annotations

import io
import math
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

LEVELS = ("ADM1", "ADM2", "ADM3", "ADM4")  # the levels allCountries carries codes for


@dataclass
class Feature:
    id: str
    name: str
    lat: float
    lon: float
    feature_class: str
    code: str
    country: str
    admin: tuple[str, str, str, str]  # admin1..admin4 codes
    population: int


@dataclass
class ModernTree:
    units: dict[str, Feature] = field(default_factory=dict)  # geonameid -> unit (continents, countries, ADM*)
    kinds: dict[str, str] = field(default_factory=dict)  # geonameid -> continent, country, ADM1 ...
    parents: dict[str, str] = field(default_factory=dict)  # geonameid -> parent geonameid
    by_codes: dict[tuple, str] = field(default_factory=dict)  # (country, a1, ...) -> geonameid
    referenced: dict[str, Feature] = field(default_factory=dict)  # features Pleiades names, any kind
    populated: dict[tuple[int, int], list[Feature]] = field(default_factory=dict)  # grid cell -> places
    report: dict[str, Any] = field(default_factory=dict)

    def most_specific_unit(self, feature: Feature) -> str | None:
        """The most specific unit a feature's admin codes name (ADM4 ... country)."""
        for depth in range(4, -1, -1):
            key = (feature.country, *feature.admin[:depth])
            if depth and not key[-1]:
                continue
            if key in self.by_codes:
                return self.by_codes[key]
        return None


def parse_line(line: str) -> Feature:
    f = line.rstrip("\n").split("\t")
    return Feature(id=f[0], name=f[1], lat=float(f[4]), lon=float(f[5]), feature_class=f[6], code=f[7],
                   country=f[8], admin=(f[10], f[11], f[12], f[13]), population=int(f[14] or 0))


def country_info(path: Path) -> dict[str, dict[str, str]]:
    """countryInfo rows: ISO code -> {geonameid, name, continent}."""
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        f = line.split("\t")
        if f[16]:
            rows[f[0]] = {"geonameid": f[16], "name": f[4], "continent": f[8]}
    return rows


def code_list(path: Path) -> dict[str, str]:
    """admin1CodesASCII / admin2Codes: geonameid -> code ("GR.ESYE31")."""
    return {line.split("\t")[3].strip(): line.split("\t")[0]
            for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def hierarchy(path: Path) -> list[tuple[str, str]]:
    """hierarchy.txt ADM links: (parent, child)."""
    with zipfile.ZipFile(path) as archive, archive.open("hierarchy.txt") as raw:
        return [(f[0], f[1]) for f in (line.split("\t") for line in io.TextIOWrapper(raw, encoding="utf-8"))
                if len(f) > 2 and f[2].strip() == "ADM"]


def cell(lat: float, lon: float) -> tuple[int, int]:
    return math.floor(lat), math.floor(lon)


def cells_around(lat: float, lon: float, km: float) -> set[tuple[int, int]]:
    """The one-degree cells that hold every point within km of (lat, lon)."""
    dlat = math.ceil(km / 111.0)
    dlon = math.ceil(km / max(111.0 * math.cos(math.radians(min(abs(lat) + dlat, 89.0))), 1.0))
    c = cell(lat, lon)
    return {(c[0] + i, c[1] + j) for i in range(-dlat, dlat + 1) for j in range(-dlon, dlon + 1)}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * 6371.0088 * math.asin(math.sqrt(a))


def build_tree(directory: Path, rules: dict[str, Any], referenced_ids: set[str],
               needed_cells: set[tuple[int, int]], lines: Iterable[str] | None = None) -> ModernTree:
    """Read allCountries once into the modern tree, the referenced features, and the
    populated places of the needed cells. `lines` replaces the dump (tests)."""
    g = rules["geonames"]
    admin_codes = set(g["modernTree"]["admin"])
    countries = country_info(directory / "countryInfo.txt")
    country_ids = {row["geonameid"]: code for code, row in countries.items()}
    listed = {**code_list(directory / "admin1CodesASCII.txt"), **code_list(directory / "admin2Codes.txt")}
    tree = ModernTree()
    continents: dict[str, str] = {}
    candidates: dict[tuple, list[Feature]] = {}
    adm5: list[Feature] = []
    if lines is None:
        archive = zipfile.ZipFile(directory / "allCountries.zip")
        lines = io.TextIOWrapper(archive.open("allCountries.txt"), encoding="utf-8")
    continent_code, populated_class = g["modernTree"]["continentCode"], g["populatedPlaceClass"]
    for line in lines:
        # Most of the 13 million lines are dropped: test the raw fields before building a Feature.
        raw = line.split("\t", 9)
        keep = (raw[0] in referenced_ids or raw[7] == continent_code or raw[0] in country_ids
                or raw[7] in admin_codes
                or (raw[6] == populated_class and cell(float(raw[4]), float(raw[5])) in needed_cells))
        if not keep:
            continue
        f = parse_line(line)
        if f.id in referenced_ids:
            tree.referenced[f.id] = f
        if f.code == continent_code:
            continents[f.name] = f.id
            tree.units[f.id], tree.kinds[f.id] = f, "continent"
        elif f.id in country_ids:
            tree.units[f.id], tree.kinds[f.id] = f, "country"
        elif f.code in admin_codes:
            if f.code == "ADM5":
                adm5.append(f)
            else:
                depth = LEVELS.index(f.code) + 1
                candidates.setdefault((f.country, *f.admin[:depth]), []).append(f)
        elif f.feature_class == populated_class:
            c = cell(f.lat, f.lon)
            if c in needed_cells:
                tree.populated.setdefault(c, []).append(f)

    # Continents and countries
    by_name = {name: continents.get(name) for name in g["continents"].values()}
    for code, row in countries.items():
        unit_id = row["geonameid"]
        if unit_id not in tree.units:
            continue
        tree.by_codes[(code,)] = unit_id
        continent = by_name.get(g["continents"].get(row["continent"], ""))
        if continent:
            tree.parents[unit_id] = continent

    # ADM1..ADM4: one unit per code path; ADM1 and ADM2 as the code lists name them
    duplicates = 0
    for key, found in candidates.items():
        if not key[-1]:  # a unit needs its own code; an empty code above it is a skipped level
            continue
        listed_id = next((f.id for f in found if listed.get(f.id) == ".".join(key[:3])), None)
        chosen = next((f for f in found if f.id == listed_id), None) or max(found, key=lambda f: (f.population, -int(f.id)))
        duplicates += len(found) - 1
        tree.units[chosen.id], tree.kinds[chosen.id] = chosen, chosen.code
        tree.by_codes[key] = chosen.id
    for unit_id, kind in list(tree.kinds.items()):
        if kind in LEVELS:
            f = tree.units[unit_id]
            depth = LEVELS.index(kind) + 1
            for up in range(depth - 1, -1, -1):
                parent = tree.by_codes.get((f.country, *f.admin[:up]))
                if parent:
                    tree.parents[unit_id] = parent
                    break

    # ADM5 from hierarchy.txt, cross-checking the code-derived parents
    links = hierarchy(directory / "hierarchy.zip")
    hierarchy_parent: dict[str, set[str]] = {}
    for parent, child in links:
        hierarchy_parent.setdefault(child, set()).add(parent)
    adm5_linked = 0
    for f in adm5:
        parents = [p for p in hierarchy_parent.get(f.id, ()) if tree.kinds.get(p) in LEVELS]
        if parents:
            tree.units[f.id], tree.kinds[f.id] = f, "ADM5"
            tree.parents[f.id] = sorted(parents)[0]
            adm5_linked += 1
    disagree = sum(1 for child, parent in tree.parents.items()
                   if child in hierarchy_parent and parent not in hierarchy_parent[child])
    tree.report = {
        "continents": sum(1 for k in tree.kinds.values() if k == "continent"),
        "countries": sum(1 for k in tree.kinds.values() if k == "country"),
        **{level: sum(1 for k in tree.kinds.values() if k == level) for level in (*LEVELS, "ADM5")},
        "duplicateCodePaths": duplicates, "adm5WithoutParent": len(adm5) - adm5_linked,
        "withoutParent": sum(1 for u in tree.units if u not in tree.parents and tree.kinds[u] != "continent"),
        "parentDiffersFromHierarchy": disagree,
        "referencedFound": len(tree.referenced), "referencedMissing": len(referenced_ids - set(tree.referenced)),
        "populatedPlacesKept": sum(len(v) for v in tree.populated.values()),
    }
    return tree


def nearest_populated(tree: ModernTree, lat: float, lon: float, km: float) -> tuple[Feature, float] | None:
    best = None
    for c in cells_around(lat, lon, km):
        for f in tree.populated.get(c, ()):
            d = haversine_km(lat, lon, f.lat, f.lon)
            if d <= km and (best is None or d < best[1]):
                best = (f, d)
    return best
