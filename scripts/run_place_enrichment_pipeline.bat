@echo off
REM Place Enrichment Pipeline — run from project root
REM Fixes sparse Place attributes by enriching from crosswalk and linking hierarchy

cd /d "%~dp0\.."

echo ============================================
echo Place Enrichment Pipeline
echo ============================================
echo.
echo Prerequisites:
echo   - Place nodes in Neo4j (import_pleiades_to_neo4j.py)
echo   - Pleiades_Place nodes (load_federation_survey.py --survey output/nodes/pleiades_roman_republic.json)
echo   - CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv
echo.

if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM 1. Enrich Place from crosswalk (qid, geonames_id, tgn_id)
echo [1/3] Enriching Place nodes from crosswalk...
python scripts\backbone\geographic\enrich_places_from_crosswalk.py
if errorlevel 1 (
    echo ERROR: enrich_places_from_crosswalk failed
    pause
    exit /b 1
)
echo.

REM 2. Link Pleiades_Place -> Place (geo backbone)
echo [2/3] Linking Pleiades_Place to Place backbone...
python scripts\backbone\subject\link_pleiades_place_to_geo_backbone.py
if errorlevel 1 (
    echo ERROR: link_pleiades_place_to_geo_backbone failed
    pause
    exit /b 1
)
echo.

REM 3. Place hierarchy (optional — requires GeoNames allCountries.txt)
echo [3/3] Place admin hierarchy (GeoNames)...
if exist "scripts\backbone\geographic\link_place_admin_hierarchy_geonames.py" (
    python scripts\backbone\geographic\link_place_admin_hierarchy_geonames.py
) else (
    echo Skipping — link_place_admin_hierarchy_geonames.py not found
)
echo.

echo ============================================
echo Place enrichment pipeline complete
echo ============================================
pause
