@echo off
REM Batch script to import a large Cypher file into Neo4j using cypher-shell
REM Adjust NEO4J_HOME and credentials as needed

pushd %~dp0

set CYPHER_SHELL=..\..\cypher-shell.bat
set CYPHER_FILE=..\output\subjects_full.cypher
set NEO4J_USER=neo4j
set /p NEO4J_PASS=Enter Neo4j password: 

"%CYPHER_SHELL%" -u %NEO4J_USER% -p %NEO4J_PASS% --file "%CYPHER_FILE%"

popd
pause
