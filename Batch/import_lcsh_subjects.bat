@echo off
REM Import LCSH Subjects Cypher into Neo4j using cypher-shell
REM Usage: import_lcsh_subjects.bat <NEO4J_USERNAME> <NEO4J_PASSWORD> <NEO4J_BOLT_URL>
REM Example: import_lcsh_subjects.bat neo4j mypassword bolt://localhost:7687

set NEO4J_USER=%1
set NEO4J_PASS=%2
set NEO4J_URL=%3
set CYPHER_FILE="LCSH/skos subject/subjects_full.cypher"

if "%NEO4J_USER%"=="" goto usage
if "%NEO4J_PASS%"=="" goto usage
if "%NEO4J_URL%"=="" goto usage

type %CYPHER_FILE% | cypher-shell -u %NEO4J_USER% -p %NEO4J_PASS% -a %NEO4J_URL%

echo Import complete.
goto end

:usage
echo Usage: import_lcsh_subjects.bat ^<NEO4J_USERNAME^> ^<NEO4J_PASSWORD^> ^<NEO4J_BOLT_URL^>
goto end

:end
