@echo off
REM Launch Streamlit Agent UI (run from project root)
cd /d "%~dp0\..\.."

echo ======================================
echo Chrystallum Agent UI - Streamlit Launch
echo ======================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Could not activate virtual environment
        echo Please run: python -m venv .venv
        pause
        exit /b 1
    )
)

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found. Installing...
    pip install streamlit
    if errorlevel 1 (
        echo ERROR: Could not install Streamlit
        pause
        exit /b 1
    )
)

REM Validate configuration
echo.
echo Checking configuration...
python scripts\config_loader.py
if errorlevel 1 (
    echo.
    echo WARNING: Configuration incomplete
    echo The UI will show setup instructions
    echo.
    timeout /t 3 >nul
)

REM Launch Streamlit app
echo.
echo ======================================
echo Launching Streamlit UI...
echo Open browser to: http://localhost:8501
echo Press Ctrl+C to stop
echo ======================================
echo.

streamlit run scripts\ui\agent_streamlit_app.py

pause
