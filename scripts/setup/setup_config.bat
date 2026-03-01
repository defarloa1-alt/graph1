@echo off
REM Chrystallum Quick Configuration Setup (Windows)
cd /d "%~dp0\..\.."

echo.
echo ============================================================
echo   Chrystallum Configuration Setup
echo ============================================================
echo.

REM Check if config.py exists
if not exist "config.py" (
    echo [1/3] Creating config.py from example...
    copy config.py.example config.py >nul
    echo      DONE - Please edit config.py with your API keys
    echo.
    echo NEXT STEPS:
    echo   1. Open config.py in your editor
    echo   2. Add your OPENAI_API_KEY
    echo   3. Add your PERPLEXITY_API_KEY
    echo   4. Add your NEO4J_PASSWORD
    echo   5. Run this script again to verify
    echo.
    pause
    exit /b 0
)

echo [1/3] config.py found - checking configuration...
echo.

REM Run configuration verification
python scripts\config_loader.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [2/3] Testing Neo4j connection...
    python -c "from neo4j import GraphDatabase; from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD; driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)); driver.verify_connectivity(); driver.close(); print('  Neo4j connected successfully')"
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo [3/3] All systems ready!
        echo.
        echo ============================================================
        echo   CONFIGURATION COMPLETE
        echo ============================================================
        echo.
        echo You can now run:
        echo   - Single agent:     python scripts\agents\facet_agent_framework.py
        echo   - Book discovery:   python scripts\agents\book_discovery_agent.py
        echo   - Phase 2.5 Runner: python scripts\phase_2_5_discovery_runner.py
        echo.
    ) else (
        echo.
        echo   WARNING: Neo4j connection failed
        echo   Check NEO4J_URI and NEO4J_PASSWORD in config.py
        echo.
    )
) else (
    echo.
    echo   Configuration validation failed
    echo   Please check the error messages above
    echo.
)

pause
