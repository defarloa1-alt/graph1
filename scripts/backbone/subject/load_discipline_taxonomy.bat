@echo off
REM Load discipline taxonomy registry into Neo4j
cd /d "%~dp0\..\..\.."

if not defined VIRTUAL_ENV call .venv\Scripts\activate.bat 2>nul

echo Loading discipline taxonomy...
python scripts\backbone\subject\load_discipline_taxonomy.py %*
pause
