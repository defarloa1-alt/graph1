@echo off
REM Neo4j Aura Connection Setup for Fresh Chrystallum Instance
REM Instance: f7b612a3

echo ========================================
echo Neo4j Aura Connection Setup
echo Instance: f7b612a3
echo ========================================
echo.

REM Set connection URI
set NEO4J_URI=neo4j+s://f7b612a3.databases.neo4j.io
set NEO4J_USERNAME=neo4j
set NEO4J_DATABASE=neo4j

REM Prompt for password
set /p NEO4J_PASSWORD="Enter your Neo4j Aura password: "

echo.
echo Connection details set:
echo   URI: %NEO4J_URI%
echo   Username: %NEO4J_USERNAME%
echo   Database: %NEO4J_DATABASE%
echo   Password: [hidden]
echo.

REM Test connection
echo Testing connection...
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('%NEO4J_URI%', auth=('%NEO4J_USERNAME%', '%NEO4J_PASSWORD%')); driver.verify_connectivity(); print('SUCCESS: Connected to Neo4j Aura!'); driver.close()"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo CONNECTION SUCCESSFUL!
    echo ========================================
    echo.
    echo Environment variables are set for this session.
    echo You can now run rebuild scripts.
    echo.
    echo To persist for future sessions, add to config.py:
    echo   NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
    echo   NEO4J_USERNAME = "neo4j"
    echo   NEO4J_PASSWORD = "your-password"
    echo   NEO4J_DATABASE = "neo4j"
    echo.
) else (
    echo.
    echo ========================================
    echo CONNECTION FAILED
    echo ========================================
    echo.
    echo Check:
    echo   1. Password is correct
    echo   2. Instance is running in Aura console
    echo   3. Firewall allows Neo4j connections
    echo.
)

pause

