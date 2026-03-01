@echo off
REM Test Neo4j MCP Server Connection
cd /d "%~dp0\.."

echo ========================================
echo Testing Neo4j MCP Server Connection
echo ========================================
echo.

REM Check if Node.js is installed
echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Download from: https://nodejs.org/
    exit /b 1
)
echo     Node.js version:
node --version
echo.

REM Check if MCP server is built
echo [2/4] Checking if MCP server is built...
if not exist "mcp\neo4j-server\dist\index.js" (
    echo ERROR: MCP server not built
    echo Run: cd mcp\neo4j-server ^&^& npm run build
    exit /b 1
)
echo     Found: mcp\neo4j-server\dist\index.js
echo.

REM Check if Neo4j is running (attempt connection test)
echo [3/4] Checking Neo4j connection...
python -c "from neo4j import GraphDatabase; import sys; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum')); driver.verify_connectivity(); print('     Neo4j is accessible at bolt://localhost:7687'); driver.close()" 2>nul
if errorlevel 1 (
    echo WARNING: Could not connect to Neo4j at bolt://localhost:7687
    echo Please ensure Neo4j Desktop is running
    echo Or update credentials in config.py
) else (
    echo     Neo4j connection successful!
)
echo.

REM Display configuration
echo [4/4] Current configuration:
echo     URI: bolt://localhost:7687
echo     Username: neo4j
echo     Password: Chrystallum
echo     Database: neo4j
echo.

echo ========================================
echo MCP Server Status: READY
echo ========================================
echo.
echo Next steps:
echo 1. Configure Cursor settings (see CURSOR_MCP_SETUP.md)
echo 2. Restart Cursor IDE
echo 3. Test with: @neo4j RETURN 'MCP is working!' AS status
echo.

pause




