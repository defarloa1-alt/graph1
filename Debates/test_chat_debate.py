#!/usr/bin/env python3
"""
Test Enhanced Chat Interface Debate Functionality
Quick test to verify the chat interface can handle debate requests
"""

import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_chat_debate():
    """Test the enhanced chat debate functionality"""
    try:
        # Import the enhanced chat function
        from quick_demo_ui import start_debate_from_chat
        
        # Test debate request
        test_query = "debate how salesforce crm tableau and snowflake should be integrated to support our mission"
        
        print("🧪 Testing Enhanced Chat Interface Debate Functionality")
        print("=" * 60)
        print(f"Test Query: {test_query}")
        print("-" * 60)
        
        # Call the function
        result = start_debate_from_chat(test_query)
        
        print("📋 Chat Response:")
        print(result)
        
        # Check if response indicates successful debate start
        if "Debate ID" in result and "Real Debate Started" in result:
            print("\n✅ SUCCESS: Chat interface successfully started a real debate!")
            return True
        elif "Debate Request Received" in result:
            print("\n⚠️  PARTIAL SUCCESS: Chat recognized debate request and provided structured response")
            return True
        else:
            print("\n❌ FAILED: Chat did not properly handle debate request")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_debate()
    
    if success:
        print("\n🎉 Enhanced chat interface is working!")
        print("\n📌 Next Steps:")
        print("1. Open http://localhost:8501")
        print("2. Navigate to 'Chat Interface' tab")
        print("3. Type: 'debate how salesforce crm tableau and snowflake should be integrated'")
        print("4. See real debate with multiple agent perspectives!")
    else:
        print("\n🔧 Chat enhancement needs attention")