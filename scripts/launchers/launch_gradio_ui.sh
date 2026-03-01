#!/bin/bash
# Launch Gradio Agent UI (run from project root)
cd "$(cd "$(dirname "$0")/../.." && pwd)"

echo "======================================"
echo "Chrystallum Agent UI - Gradio Launch"
echo "======================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "ERROR: Could not activate virtual environment"
        echo "Please run: python -m venv .venv"
        exit 1
    fi
fi

# Check if gradio is installed
python -c "import gradio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Gradio not found. Installing..."
    pip install gradio
    if [ $? -ne 0 ]; then
        echo "ERROR: Could not install Gradio"
        exit 1
    fi
fi

# Validate configuration
echo ""
echo "Checking configuration..."
python scripts/config_loader.py
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Configuration incomplete"
    echo "The UI will show setup instructions"
    echo ""
    sleep 3
fi

# Launch Gradio app
echo ""
echo "======================================"
echo "Launching Gradio UI..."
echo "Open browser to: http://localhost:7860"
echo "Press Ctrl+C to stop"
echo "======================================"
echo ""

python scripts/ui/agent_gradio_app.py
