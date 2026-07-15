@echo off
REM Chrystallum Proposal Review — API + Viewer
cd /d "%~dp0..\.."

echo Starting Proposal Review API on http://127.0.0.1:8765 ...
start "Chrystallum Proposal Review API" cmd /c "python scripts\ui\proposal_review_api.py --seed Q17167"

timeout /t 2 /nobreak >nul

echo Starting Viewer on http://localhost:5173 ...
echo Open the "Review Queue" tab.
cd viewer
npm run dev
