@echo off
REM Fresh Chrystallum Rebuild - Temporal First, Then Geographic
cd /d "%~dp0\.."

echo ========================================
echo FRESH CHRYSTALLUM REBUILD
echo ========================================
echo.
echo Order: Temporal (Years + Periods) then Geographic (Places)
echo Instance: f7b612a3 (Neo4j Aura)
echo.
echo Prerequisites:
echo   - Environment variables set (run setup_aura_connection.bat first)
echo   - Connection tested successfully
echo.

REM Verify env vars are set
if "%NEO4J_URI%"=="" (
    echo ERROR: NEO4J_URI not set
    echo Run scripts\setup\setup_aura_connection.bat first
    pause
    exit /b 1
)

echo Using:
echo   URI: %NEO4J_URI%
echo   Database: %NEO4J_DATABASE%
echo.
pause

REM ============================================================================
echo.
echo ========================================
echo STAGE 1: SCHEMA ^& CONSTRAINTS
echo ========================================
echo.

python Neo4j/schema/run_cypher_file.py Neo4j/schema/01_schema_constraints_neo5_compatible.cypher
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Schema constraints failed
    pause
    exit /b 1
)

python Neo4j/schema/run_cypher_file.py Neo4j/schema/02_schema_indexes.cypher
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Schema indexes failed
    pause
    exit /b 1
)

echo Schema and constraints created successfully!
echo.
pause

REM ============================================================================
echo.
echo ========================================
echo STAGE 2: TEMPORAL BACKBONE - YEARS
echo ========================================
echo Creating 4,025 Year nodes (-2000 to 2025)...
echo.

python scripts/backbone/temporal/genYearsToNeo.py ^
  --uri %NEO4J_URI% ^
  --user %NEO4J_USERNAME% ^
  --password %NEO4J_PASSWORD% ^
  --database %NEO4J_DATABASE% ^
  --start -2000 ^
  --end 2025

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Year backbone creation failed
    pause
    exit /b 1
)

echo Year backbone created successfully!
echo.
pause

REM ============================================================================
echo.
echo ========================================
echo STAGE 2.5: TEMPORAL HIERARCHY (OPTIONAL)
echo ========================================
echo Creating Decade/Century/Millennium hierarchy...
echo.

set /p DO_HIERARCHY="Create temporal hierarchy? (Y/N): "
if /i "%DO_HIERARCHY%"=="Y" (
    python Neo4j/schema/run_cypher_file.py Neo4j/schema/05_temporal_hierarchy_levels.cypher
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: Hierarchy creation failed, continuing...
    ) else (
        echo Temporal hierarchy created successfully!
    )
)
echo.
pause

REM ============================================================================
echo.
echo ========================================
echo STAGE 3: PERIODS FROM PERIODO
echo ========================================
echo Creating ~1,077 Period nodes...
echo.

python scripts/backbone/temporal/import_enriched_periods.py ^
  --uri %NEO4J_URI% ^
  --user %NEO4J_USERNAME% ^
  --password %NEO4J_PASSWORD% ^
  --database %NEO4J_DATABASE%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Period import failed
    pause
    exit /b 1
)

echo Periods imported successfully!
echo TEMPORAL BACKBONE COMPLETE!
echo.
pause

REM ============================================================================
echo.
echo ========================================
echo STAGE 4: GEOGRAPHIC BACKBONE - PLACES
echo ========================================
echo.

set /p PLACE_LIMIT="Load test (1000 places) or full (42000 places)? (test/full): "

if /i "%PLACE_LIMIT%"=="test" (
    echo Loading 1,000 test places...
    python scripts/backbone/geographic/import_pleiades_to_neo4j.py ^
      --uri %NEO4J_URI% ^
      --user %NEO4J_USERNAME% ^
      --password %NEO4J_PASSWORD% ^
      --database %NEO4J_DATABASE% ^
      --limit 1000
) else (
    echo Loading full Pleiades corpus (~42,000 places)...
    echo This will take 10-15 minutes...
    python scripts/backbone/geographic/import_pleiades_to_neo4j.py ^
      --uri %NEO4J_URI% ^
      --user %NEO4J_USERNAME% ^
      --password %NEO4J_PASSWORD% ^
      --database %NEO4J_DATABASE%
)

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Place import failed
    pause
    exit /b 1
)

echo Places imported successfully!
echo.
pause

REM ============================================================================
echo.
echo ========================================
echo STAGE 5: GEOGRAPHIC TYPE HIERARCHY
echo ========================================
echo Creating PlaceType taxonomy...
echo.

python scripts/backbone/geographic/build_place_type_hierarchy.py ^
  --no-wikidata ^
  --load-neo4j ^
  --neo4j-mode core ^
  --force-http ^
  --uri %NEO4J_URI% ^
  --user %NEO4J_USERNAME% ^
  --password %NEO4J_PASSWORD% ^
  --database %NEO4J_DATABASE%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Place type hierarchy failed
    pause
    exit /b 1
)

echo Geographic type hierarchy created successfully!
echo GEOGRAPHIC BACKBONE COMPLETE!
echo.
pause

REM ============================================================================
echo.
echo ========================================
echo REBUILD COMPLETE!
echo ========================================
echo.
echo Your fresh Chrystallum instance now has:
echo   - Temporal backbone: Years + Periods
echo   - Geographic backbone: Places + Types
echo.
echo Next steps:
echo   1. Run verification queries in Neo4j Browser
echo   2. Add Subject concepts
echo   3. Implement federation scoring
echo   4. Load entities (Human, Event, etc.)
echo.
echo Verification guide: md/Guides/FRESH_CHRYSTALLUM_REBUILD_2026-02-19.md
echo.
pause

