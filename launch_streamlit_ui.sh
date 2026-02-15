#!/bin/bash
# Launch Streamlit Agent UI
# Linux/Mac shell script

echo "======================================"
echo "Chrystallum Agent UI - Streamlit Launch"
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

# Check if streamlit is installed
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Streamlit not found. Installing..."
    pip install streamlit
    if [ $? -ne 0 ]; then
        echo "ERROR: Could not install Streamlit"
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

# Launch Streamlit app
echo ""
echo "======================================"
echo "Launching Streamlit UI..."
echo "Open browser to: http://localhost:8501"
echo "Press Ctrl+C to stop"
echo "======================================"
echo ""

streamlit run scripts/ui/agent_streamlit_app.py
