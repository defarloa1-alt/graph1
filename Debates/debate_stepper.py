# Debate Stepper - Local Debate Control Interface
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional

def init_session_state():
    """Initialize session state variables."""
    if 'step_count' not in st.session_state:
        st.session_state.step_count = 0
    if 'debate_history' not in st.session_state:
        st.session_state.debate_history = []

def get_debate_state(base_url: str, project_id: str, series_id: str) -> Optional[Dict]:
    """Fetch the latest debate series info from the project container."""
    try:
        resp = requests.get(f"{base_url}/api/project_container", 
                          params={"id": project_id}, 
                          timeout=10)
        resp.raise_for_status()
        
        container = resp.json().get("project_container", {})
        for item in container.get("debate_series", []):
            if item.get("series_id") == series_id:
                return item
        return None
        
    except requests.RequestException as e:
        st.error(f"Failed to fetch debate state: {e}")
        return None

def advance_debate(base_url: str, series_id: str, current_step: int) -> Optional[Dict]:
    """Send the equivalent of typing Y to advance the debate."""
    try:
        payload = {"step_number": current_step}
        resp = requests.post(f"{base_url}/api/debates/{series_id}/advance", 
                           json=payload,
                           timeout=10)
        resp.raise_for_status()
        return resp.json()
        
    except requests.RequestException as e:
        st.error(f"Failed to advance debate: {e}")
        return None

def display_debate_status(debate_state: Dict):
    """Display current debate status in a formatted panel."""
    if not debate_state:
        st.warning("No debate state available")
        return
    
    # Main status panel
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"🎯 {debate_state.get('topic', 'Unknown Topic')}")
        st.write(f"**Series ID:** `{debate_state.get('series_id', 'N/A')}`")
        st.write(f"**Mode:** {debate_state.get('mode', 'N/A')}")
    
    with col2:
        status = debate_state.get('status', 'unknown')
        status_color = "🟢" if status == "active" else "🟡" if status == "paused" else "🔴"
        st.metric("Status", f"{status_color} {status.title()}")
    
    with col3:
        step_num = debate_state.get('step_number', 0)
        st.metric("Current Step", step_num)
    
    # Progress info
    st.write("**Last Step:**", debate_state.get('last_step', 'No information available'))
    
    # Participants
    participants = debate_state.get('participants', [])
    if participants:
        st.write("**Participants:**", " • ".join(participants))
    
    # Timestamps
    col1, col2 = st.columns(2)
    with col1:
        created = debate_state.get('created_at', '')
        if created:
            st.caption(f"Created: {created}")
    with col2:
        updated = debate_state.get('updated_at', '')
        if updated:
            st.caption(f"Updated: {updated}")

def main():
    # Set page config first
    st.set_page_config(
        page_title="Debate Stepper", 
        page_icon="⚡", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    st.title("⚡ Debate Stepper")
    st.markdown("**Local Debate Control Interface** - Simulate typing `Y` to advance debates")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        base_url = st.text_input(
            "API Base URL", 
            value="http://localhost:5001",
            help="URL of the Project Context API server"
        )
        
        project_id = st.text_input(
            "Project ID", 
            value="p-001",
            help="Project identifier"
        )
        
        series_id = st.selectbox(
            "Debate Series ID",
            ["d-001", "d-002"],
            help="Select debate series to control"
        )
        
        st.divider()
        
        # API Health Check
        if st.button("🔍 Test API Connection"):
            try:
                resp = requests.get(f"{base_url}/api/health", timeout=5)
                if resp.status_code == 200:
                    st.success("✅ API is healthy")
                else:
                    st.error(f"❌ API returned {resp.status_code}")
            except requests.RequestException as e:
                st.error(f"❌ Connection failed: {e}")
        
        st.divider()
        st.caption(f"Step Count: {st.session_state.step_count}")
    
    # Main content area
    st.header("📊 Current Debate State")
    
    # Fetch and display current state
    debate_state = get_debate_state(base_url, project_id, series_id)
    
    if debate_state:
        display_debate_status(debate_state)
        
        st.divider()
        
        # Advance controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 **Advance Debate (Y)**", 
                        type="primary", 
                        use_container_width=True,
                        help="Simulate pressing 'Y' to advance the debate"):
                
                current_step = debate_state.get('step_number', 0)
                
                with st.spinner("Advancing debate..."):
                    advance_result = advance_debate(base_url, series_id, current_step)
                
                if advance_result:
                    st.session_state.step_count += 1
                    st.session_state.debate_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': 'advance',
                        'result': advance_result
                    })
                    
                    st.success(f"✅ Debate advanced to step {advance_result.get('step_number', current_step + 1)}")
                    st.rerun()
        
        # Pause indicator
        st.info("💭 **--PAUSE (type Y to advance)**")
        
        # Optional feedback input
        st.divider()
        st.subheader("💬 Human Feedback (Optional)")
        feedback = st.text_area(
            "Add feedback for this debate step:",
            placeholder="Enter any observations, concerns, or guidance for the debate participants...",
            height=100
        )
        
        if feedback and st.button("📝 Submit Feedback"):
            st.success("Feedback recorded (demo mode - not sent to API)")
    
    else:
        st.error("❌ Could not load debate state. Check API connection and configuration.")
    
    # History section
    if st.session_state.debate_history:
        st.divider()
        st.subheader("📝 Debate History")
        
        with st.expander("View Advance History", expanded=False):
            for i, entry in enumerate(reversed(st.session_state.debate_history[-10:]), 1):
                st.write(f"**{i}.** {entry['timestamp']} - Advanced to step {entry['result'].get('step_number', 'N/A')}")
                if entry['result'].get('next_step'):
                    st.caption(f"   Next: {entry['result']['next_step']}")
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.caption("🔧 Enhanced Federated Graph Framework • Local Debate Control")

if __name__ == "__main__":
    main()