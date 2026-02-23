@echo off
REM Launch Gradio Agent UI
REM Windows batch script

echo ======================================
echo Chrystallum Agent UI - Gradio Launch
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

REM Check if gradio is installed
python -c "import gradio" 2>nul
if errorlevel 1 (
    echo Gradio not found. Installing...
    pip install gradio
    if errorlevel 1 (
        echo ERROR: Could not install Gradio
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

REM Launch Gradio app
echo.
echo ======================================
echo Launching Gradio UI...
echo Open browser to: http://localhost:7860
echo Press Ctrl+C to stop
echo ======================================
echo.

python scripts\ui\agent_gradio_app.py

pause
