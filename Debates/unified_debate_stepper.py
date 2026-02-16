"""
Unified Debate Stepper Server
Combines API and UI in one Flask app to avoid CORS issues
"""

from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Mock debate data with actual debate content
DEBATE_DATA = {
    "project_container": {
        "project_id": "p-001",
        "title": "Enhanced Federated Graph Framework Demo",
        "status": "active",
        "debate_series": [
            {
                "series_id": "d-001",
                "topic": "Salesforce-Tableau-Snowflake Integration Strategy",
                "mode": "ORDER-CARE",
                "status": "active",
                "last_step": "Agent consensus building in progress",
                "step_number": 3,
                "participants": ["Data Architect", "Integration Engineer", "Business Analyst"],
                "created_at": "2025-10-01T10:00:00Z",
                "updated_at": datetime.now().isoformat(),
                "debate_history": [
                    {
                        "step": 1,
                        "agent": "Data Architect",
                        "content": "Initial proposal: We should implement a hub-and-spoke architecture with Snowflake as the central data warehouse, Salesforce as the CRM spoke, and Tableau connecting directly to Snowflake for analytics.",
                        "timestamp": "2025-10-01T10:00:00Z"
                    },
                    {
                        "step": 2,
                        "agent": "Integration Engineer", 
                        "content": "I challenge the direct Tableau-Snowflake connection. We need an integration layer using Salesforce Connect or MuleSoft to ensure data governance and real-time sync. Direct connections create data silos.",
                        "timestamp": "2025-10-01T10:05:00Z"
                    },
                    {
                        "step": 3,
                        "agent": "Business Analyst",
                        "content": "Both perspectives have merit. I propose a hybrid approach: real-time operational data flows through Salesforce Connect for immediate CRM needs, while analytical workloads use scheduled ETL to Snowflake with Tableau visualization.",
                        "timestamp": "2025-10-01T10:10:00Z"
                    }
                ]
            },
            {
                "series_id": "d-002",
                "topic": "Graph Database Architecture Optimization",
                "mode": "SOCRATIC",
                "status": "paused",
                "last_step": "Waiting for stakeholder input",
                "step_number": 1,
                "participants": ["Graph Specialist", "Performance Engineer"],
                "created_at": "2025-10-01T11:30:00Z",
                "updated_at": datetime.now().isoformat(),
                "debate_history": [
                    {
                        "step": 1,
                        "agent": "Graph Specialist",
                        "content": "Question: What are the fundamental performance bottlenecks in our current Neo4j implementation when handling 10M+ nodes with complex relationship queries?",
                        "timestamp": "2025-10-01T11:30:00Z"
                    }
                ]
            }
        ],
        "metadata": {
            "total_debates": 2,
            "active_debates": 1,
            "paused_debates": 1
        }
    }
}

# Agent response templates for generating new debate content
AGENT_RESPONSES = {
    "d-001": {
        "Data Architect": [
            "Let me refine the architecture: We need separate data lakes for raw data ingestion and a curated data warehouse layer in Snowflake for analytics.",
            "I'm seeing consensus on the hybrid approach. We should implement data contracts between systems to ensure schema consistency.",
            "Final recommendation: Three-tier architecture with bronze (raw), silver (cleansed), and gold (business-ready) data layers in Snowflake."
        ],
        "Integration Engineer": [
            "The integration layer must handle both batch and streaming data patterns. I suggest implementing Apache Kafka for event streaming.",
            "We need to consider data lineage tracking. Every data transformation should be logged for compliance and debugging.",
            "Security concern: All data movement must be encrypted in transit and at rest, with proper RBAC in each system."
        ],
        "Business Analyst": [
            "From a business perspective, we need sub-5-minute data freshness for sales dashboards and same-day accuracy for executive reporting.",
            "The solution must support our quarterly business reviews with historical trend analysis going back 5 years.",
            "Cost consideration: Snowflake compute costs can spiral. We need automated scaling policies based on usage patterns."
        ]
    },
    "d-002": {
        "Graph Specialist": [
            "Deeper question: How do we optimize Cypher queries for graph traversals that span more than 4 hops in our relationship network?",
            "Consider this: Should we denormalize frequently-accessed relationship paths into materialized views for faster lookups?",
            "What indexing strategies work best for our mixed read-heavy and write-intensive workloads?"
        ],
        "Performance Engineer": [
            "Memory allocation is critical. Current heap size may be insufficient for large graph algorithms. We need to profile memory usage.",
            "Database warming strategies: How do we pre-load frequently accessed subgraphs into memory after restarts?",
            "Connection pooling optimization: Current pool sizes may not match our concurrent query patterns."
        ]
    }
}

# HTML template embedded in Python
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚡ Unified Debate Stepper</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        .header h1 {
            color: #2d3748;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #718096;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }
        .status-bar {
            background: #48bb78;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
        }
        .debate-card {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        .debate-card.active {
            border-color: #48bb78;
            background: #f0fff4;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(72, 187, 120, 0.15);
        }
        .debate-card.paused {
            border-color: #ed8936;
            background: #fffaf0;
        }
        .debate-title {
            font-size: 1.4em;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 15px;
        }
        .debate-meta {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .meta-item {
            text-align: center;
            padding: 10px;
            background: #f7fafc;
            border-radius: 8px;
        }
        .meta-label {
            font-size: 0.8em;
            color: #718096;
            text-transform: uppercase;
            font-weight: 500;
            margin-bottom: 5px;
        }
        .meta-value {
            font-size: 1.2em;
            font-weight: 600;
            color: #2d3748;
        }
        .last-step {
            background: #edf2f7;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-style: italic;
            color: #4a5568;
            border-left: 4px solid #4299e1;
        }
        .participants {
            margin-bottom: 20px;
        }
        .participants-label {
            font-size: 0.9em;
            color: #718096;
            margin-bottom: 8px;
            font-weight: 500;
        }
        .participant {
            display: inline-block;
            background: #4299e1;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            margin: 3px 5px 3px 0;
            font-weight: 500;
        }
        .pause-indicator {
            text-align: center;
            font-family: 'Courier New', monospace;
            background: #2d3748;
            color: #48bb78;
            padding: 12px;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: bold;
            font-size: 1.1em;
        }
        .advance-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 35px;
            font-size: 1.2em;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        .advance-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        .advance-button:disabled {
            background: #a0aec0;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .advance-button:active {
            transform: translateY(-1px);
        }
        .debate-content {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
        }
        .debate-history {
            padding: 0;
        }
        .debate-step {
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
            position: relative;
        }
        .debate-step:last-child {
            border-bottom: none;
        }
        .step-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 10px;
        }
        .step-number {
            background: #4299e1;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 10px;
        }
        .agent-name {
            font-weight: 600;
            color: #2d3748;
            flex-grow: 1;
        }
        .step-time {
            font-size: 0.8em;
            color: #718096;
        }
        .step-content {
            margin-left: 35px;
            line-height: 1.6;
            color: #4a5568;
        }
        .no-content {
            text-align: center;
            color: #718096;
            font-style: italic;
            padding: 20px;
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-weight: 500;
        }
        .message.success {
            background: #c6f6d5;
            color: #276749;
            border: 1px solid #9ae6b4;
        }
        .message.error {
            background: #fed7d7;
            color: #c53030;
            border: 1px solid #feb2b2;
        }
        .refresh-button {
            background: #4299e1;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 20px;
            font-weight: 500;
        }
        .refresh-button:hover {
            background: #3182ce;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Unified Debate Stepper</h1>
            <p>Single Server Solution - No CORS Issues</p>
        </div>

        <div class="status-bar">
            ✅ Server Running on Port {{ port }} - All Systems Operational
        </div>

        <button class="refresh-button" onclick="location.reload()">🔄 Refresh Data</button>

        <div id="message"></div>

        {% for debate in debates %}
        <div class="debate-card {{ debate.status }}">
            <div class="debate-title">{{ debate.topic }}</div>
            
            <div class="debate-meta">
                <div class="meta-item">
                    <div class="meta-label">Series ID</div>
                    <div class="meta-value">{{ debate.series_id }}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Mode</div>
                    <div class="meta-value">{{ debate.mode }}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Step</div>
                    <div class="meta-value">{{ debate.step_number }}</div>
                </div>
            </div>
            
            <div class="last-step">
                <strong>Last Step:</strong> {{ debate.last_step }}
            </div>
            
            <div class="participants">
                <div class="participants-label">Participants:</div>
                {% for participant in debate.participants %}
                <span class="participant">{{ participant }}</span>
                {% endfor %}
            </div>

            <div class="debate-content">
                {% if debate.debate_history %}
                <div class="debate-history">
                    {% for step in debate.debate_history %}
                    <div class="debate-step">
                        <div class="step-header">
                            <div class="step-number">{{ step.step }}</div>
                            <div class="agent-name">{{ step.agent }}</div>
                            <div class="step-time">{{ step.timestamp[:16] }}</div>
                        </div>
                        <div class="step-content">{{ step.content }}</div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="no-content">No debate content yet. Click "Advance" to begin.</div>
                {% endif %}
            </div>
            
            <div class="pause-indicator">--PAUSE (type Y to advance)</div>
            
            <button class="advance-button" 
                    onclick="advanceDebate('{{ debate.series_id }}', {{ debate.step_number }})"
                    {% if debate.status != 'active' %}disabled{% endif %}>
                🚀 Advance Debate (Y)
            </button>
        </div>
        {% endfor %}
    </div>

    <script>
        function showMessage(text, type) {
            const messageEl = document.getElementById('message');
            messageEl.innerHTML = `<div class="message ${type}">${text}</div>`;
            setTimeout(() => {
                messageEl.innerHTML = '';
            }, 5000);
        }

        function advanceDebate(seriesId, currentStep) {
            const button = event.target;
            button.disabled = true;
            button.textContent = '⏳ Advancing...';

            fetch('/advance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    series_id: seriesId,
                    step_number: currentStep
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ ${data.message}`, 'success');
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    showMessage(`❌ ${data.message}`, 'error');
                    button.disabled = false;
                    button.textContent = '🚀 Advance Debate (Y)';
                }
            })
            .catch(error => {
                showMessage(`❌ Network error: ${error.message}`, 'error');
                button.disabled = false;
                button.textContent = '🚀 Advance Debate (Y)';
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main debate stepper page."""
    debates = DEBATE_DATA["project_container"]["debate_series"]
    return render_template_string(HTML_TEMPLATE, debates=debates, port=6001)

@app.route('/advance', methods=['POST'])
def advance_debate():
    """Advance the specified debate series with new content."""
    try:
        data = request.json
        series_id = data.get('series_id')
        current_step = data.get('step_number', 1)
        
        # Find and update the debate
        for debate in DEBATE_DATA["project_container"]["debate_series"]:
            if debate["series_id"] == series_id:
                new_step = current_step + 1
                debate["step_number"] = new_step
                debate["updated_at"] = datetime.now().isoformat()
                
                # Generate new debate content
                if series_id in AGENT_RESPONSES:
                    agents = list(AGENT_RESPONSES[series_id].keys())
                    # Rotate through agents
                    agent_index = (new_step - 1) % len(agents)
                    current_agent = agents[agent_index]
                    
                    # Get response for this agent
                    responses = AGENT_RESPONSES[series_id][current_agent]
                    response_index = min((new_step - 1) // len(agents), len(responses) - 1)
                    response_text = responses[response_index]
                    
                    # Add new step to debate history
                    if "debate_history" not in debate:
                        debate["debate_history"] = []
                    
                    new_step_content = {
                        "step": new_step,
                        "agent": current_agent,
                        "content": response_text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    debate["debate_history"].append(new_step_content)
                    debate["last_step"] = f"{current_agent}: {response_text[:50]}..."
                    
                    return jsonify({
                        'success': True,
                        'message': f"🎯 {current_agent} responded in step {new_step}",
                        'new_step': new_step,
                        'agent': current_agent,
                        'content_preview': response_text[:100] + "..."
                    })
                else:
                    debate["last_step"] = f"Step {new_step}: Waiting for agent responses"
                    return jsonify({
                        'success': True,
                        'message': f"Advanced to step {new_step}",
                        'new_step': new_step
                    })
        
        return jsonify({
            'success': False,
            'message': f"Debate series {series_id} not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Unified Debate Stepper',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Unified Debate Stepper...")
    print("📊 Features:")
    print("   ✅ No CORS issues (single server)")
    print("   ✅ Embedded HTML interface")
    print("   ✅ Real-time debate advancement")
    print("   ✅ Persistent state between advances")
    print()
    print("🎯 Access the interface at: http://localhost:6001")
    print("🔧 API endpoint: http://localhost:6001/api/health")
    print()
    
    app.run(host='0.0.0.0', port=6001, debug=True)