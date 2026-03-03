@echo off
REM SFA QID Explorer - Simple Gradio UI for QID to Rich Data
REM Launch: launch_sfa_qid_explorer.bat
REM Wait for "Running on local URL" then open: http://127.0.0.1:7862

cd /d "%~dp0\..\.."
python -c "import gradio" 2>nul
if errorlevel 1 (
    echo Installing gradio...
    pip install gradio
)
echo Starting SFA QID Explorer... Wait for "Running on local URL" before opening browser.
python scripts\ui\sfa_qid_explorer.py
pause
