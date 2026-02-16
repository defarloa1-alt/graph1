"""
Simple Flask-based Debate Stepper
Alternative to Streamlit for even simpler deployment
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
from datetime import datetime

app = Flask(__name__)

# Configuration
API_BASE_URL = "http://localhost:5001"
PROJECT_ID = "p-001"
DEFAULT_SERIES_ID = "d-001"

@app.route('/')
def index():
    """Main debate stepper page."""
    # Get current debate state
    try:
        resp = requests.get(f"{API_BASE_URL}/api/project_container", 
                          params={"id": PROJECT_ID}, 
                          timeout=10)
        if resp.status_code == 200:
            container = resp.json().get("project_container", {})
            debate_series = container.get("debate_series", [])
        else:
            debate_series = []
    except:
        debate_series = []
    
    return render_template('debate_stepper.html', 
                         debate_series=debate_series,
                         api_base_url=API_BASE_URL,
                         project_id=PROJECT_ID)

@app.route('/advance/<series_id>', methods=['POST'])
def advance_debate(series_id):
    """Advance the specified debate series."""
    try:
        # Get current step from form
        current_step = int(request.form.get('current_step', 1))
        
        # Call advance API
        payload = {"step_number": current_step}
        resp = requests.post(f"{API_BASE_URL}/api/debates/{series_id}/advance", 
                           json=payload,
                           timeout=10)
        
        if resp.status_code == 200:
            result = resp.json()
            return jsonify({
                'success': True,
                'message': f"Advanced to step {result.get('step_number', current_step + 1)}",
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'message': f"API returned {resp.status_code}"
            }), resp.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500

@app.route('/api/health')
def health_check():
    """Check if the debate API is available."""
    try:
        resp = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if resp.status_code == 200:
            return jsonify({'status': 'healthy', 'api_status': 'connected'})
        else:
            return jsonify({'status': 'warning', 'api_status': f'api_error_{resp.status_code}'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'api_status': 'disconnected', 'error': str(e)}), 200

if __name__ == '__main__':
    print("🚀 Starting Simple Debate Stepper (Flask)")
    print("📊 Available at: http://localhost:8503")
    print("🎯 Features: Simple Y button, real-time state, no Streamlit complexity")
    app.run(host='0.0.0.0', port=8503, debug=True)