@echo off
REM ============================================================================
REM REBUILD LCSH CLASS D BACKBONE FROM WIKIDATA
REM ============================================================================

cd /d "%~dp0\.."

echo.
echo ============================================================================
echo REBUILD LCSH CLASS D (HISTORY) BACKBONE
echo ============================================================================
echo.

REM Step 1: Retrieve from Wikidata
echo [STEP 1/2] Retrieving ALL Class D subjects from Wikidata...
echo.
python python\lcsh\scripts\retrieve_lcsh_class_d_complete.py
if errorlevel 1 (
    echo [ERROR] Failed to retrieve subjects from Wikidata
    pause
    exit /b 1
)

echo.
echo [WAITING] 2 seconds...
timeout /t 2 /nobreak >nul

REM Step 2: Import to Neo4j
echo.
echo [STEP 2/2] Importing to Neo4j...
echo.
python python\lcsh\scripts\import_lcsh_class_d.py
if errorlevel 1 (
    echo [ERROR] Failed to import to Neo4j
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo [SUCCESS] Class D backbone rebuilt!
echo ============================================================================
echo.
echo You now have ALL LCC Class D (History) subjects in Neo4j with:
echo   - Clean LCSH IDs
echo   - LCC codes (100%%)
echo   - Dewey codes (where available)
echo   - FAST IDs (where available)
echo   - Hierarchical relationships (BROADER_THAN)
echo.
pause

