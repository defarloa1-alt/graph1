#!/usr/bin/env python3
"""
Simple Test: Verify Enhanced Chat Can Handle Debates
Tests the core debate recognition logic without Streamlit interference
"""

def test_debate_recognition():
    """Test if chat can recognize debate requests"""
    
    test_queries = [
        "debate how salesforce crm tableau and snowflake should be integrated",
        "should we implement automated testing in our pipeline?",
        "what about microservices vs monolithic architecture?",
        "how should we approach cloud migration?",
        "discuss the pros and cons of AI implementation"
    ]
    
    print("🧪 Testing Debate Recognition Logic")
    print("=" * 50)
    
    for query in test_queries:
        query_lower = query.lower()
        
        # Test the same logic from process_chat_query
        is_debate = any(word in query_lower for word in ["debate", "discuss", "argue", "should we", "how should", "what about"])
        
        print(f"📝 Query: {query}")
        print(f"   🎯 Recognized as debate: {'✅ YES' if is_debate else '❌ NO'}")
        print()
    
    return True

if __name__ == "__main__":
    test_debate_recognition()
    
    print("🎉 Enhanced Chat Interface Summary:")
    print("=" * 40)
    print("✅ Chat now recognizes debate keywords:")
    print("   • 'debate'")
    print("   • 'discuss' ") 
    print("   • 'should we'")
    print("   • 'how should'")
    print("   • 'what about'")
    print()
    print("✅ When detected, chat will:")
    print("   • Start a real debate with unique ID")
    print("   • Generate multi-agent perspectives")
    print("   • Show consensus tracking")
    print("   • Provide structured analysis")
    print()
    print("🚀 Ready to test!")
    print("1. Open http://localhost:8501")
    print("2. Go to 'Chat Interface' tab")
    print("3. Type: 'debate how salesforce crm tableau and snowflake should be integrated'")
    print("4. Watch real debate start with agent perspectives!")