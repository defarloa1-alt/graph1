#!/bin/bash
# Place Enrichment Pipeline — run from project root
# Federation to GeoNames and Wikidata. See Geographic/FEDERATION_HAPPY_PATH.md for full flow and unhappy-path discussion.

cd "$(dirname "$0")/.."

echo "============================================"
echo "Place Enrichment Pipeline"
echo "============================================"
echo ""
echo "Prerequisites:"
echo "  - Place nodes in Neo4j (import_pleiades_to_neo4j.py)"
echo "  - Pleiades_Place nodes (load_federation_survey.py --survey output/nodes/pleiades_roman_republic.json)"
echo "  - CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv"
echo ""

[ -n "$VIRTUAL_ENV" ] || { echo "Activating virtual environment..."; source .venv/bin/activate 2>/dev/null || true; }

# 1. Enrich Place from crosswalk (qid, geonames_id, tgn_id)
echo "[1/5] Enriching Place nodes from crosswalk..."
python scripts/backbone/geographic/enrich_places_from_crosswalk.py || exit 1
echo ""

# 2. Place admin hierarchy — GeoNames (requires geonames_allCountries.zip)
echo "[2/5] Place admin hierarchy (GeoNames)..."
python scripts/backbone/geographic/link_place_admin_hierarchy_geonames.py || exit 1
echo ""

# 3. Place admin hierarchy — Wikidata (P131/P17)
echo "[3/5] Place admin hierarchy (Wikidata)..."
python scripts/backbone/geographic/link_place_admin_hierarchy.py || exit 1
echo ""

# 4. Wikidata geo enrichment (P625, P3896, P131, P17)
echo "[4/5] Wikidata geo enrichment..."
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py || exit 1
echo ""

# 5. Link Pleiades_Place -> Place (geo backbone)
echo "[5/5] Linking Pleiades_Place to Place backbone..."
python scripts/backbone/geographic/link_pleiades_place_to_geo_backbone.py || exit 1
echo ""

echo "============================================"
echo "Place enrichment pipeline complete"
echo "============================================"
