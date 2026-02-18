#!/usr/bin/env python3
"""
AI Cognitive Engine Examples for Federated Graph Framework
=========================================================

This demonstrates how GPT, Perplexity, and OpenAI APIs serve as the cognitive
engines for live agents in your federated graph network. Each AI system
provides different reasoning capabilities for agent decision-making.

Author: Enhanced Federated Graph Framework
Date: 2025-10-01
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Import AI clients
try:
    from openai import OpenAI
    import requests
    HAS_AI = True
except ImportError:
    HAS_AI = False


class AIBackend(Enum):
    """Available AI cognitive backends"""
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT35 = "openai_gpt35"
    PERPLEXITY_SONAR = "perplexity_sonar"
    PERPLEXITY_LLAMA = "perplexity_llama"


@dataclass
class AgentContext:
    """Context information for AI reasoning"""
    agent_id: str
    lcc_domain: str
    marc_knowledge: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    relationships: Dict[str, float]
    current_debates: List[str]
    expertise_level: float = 0.8


class AICognitiveEngine:
    """Multi-backend AI cognitive engine for agent reasoning"""
    
    def __init__(self):
        self.openai_client = None
        self.perplexity_session = None
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize AI clients"""
        # OpenAI setup
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            print("✅ OpenAI client initialized")
        
        # Perplexity setup  
        perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        if perplexity_key:
            self.perplexity_session = requests.Session()
            self.perplexity_key = perplexity_key
            print("✅ Perplexity client initialized")
    
    async def agent_reasoning(self, 
                            context: AgentContext, 
                            reasoning_task: str,
                            backend: AIBackend = AIBackend.OPENAI_GPT4) -> Dict[str, Any]:
        """
        Core agent reasoning using specified AI backend
        
        This is where agents "think" using AI cognition
        """
        
        # Build reasoning prompt based on agent context
        prompt = self._build_reasoning_prompt(context, reasoning_task)
        
        # Route to appropriate AI backend
        if backend in [AIBackend.OPENAI_GPT4, AIBackend.OPENAI_GPT35]:
            return await self._openai_reasoning(prompt, backend)
        elif backend in [AIBackend.PERPLEXITY_SONAR, AIBackend.PERPLEXITY_LLAMA]:
            return await self._perplexity_reasoning(prompt, backend)
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def _build_reasoning_prompt(self, context: AgentContext, task: str) -> str:
        """Build sophisticated reasoning prompt with full agent context"""
        
        # Extract MARC knowledge for reasoning
        subject_headings = context.marc_knowledge.get("subject_headings", [])
        authority_records = context.marc_knowledge.get("authority_records", [])
        expert_vocabulary = context.marc_knowledge.get("expert_vocabulary", [])
        
        # Build relationship context
        trusted_agents = [agent_id for agent_id, trust in context.relationships.items() if trust > 0.7]
        
        # Recent conversation context
        recent_messages = context.conversation_history[-5:] if context.conversation_history else []
        
        prompt = f"""
You are Agent {context.agent_id}, an expert AI agent in the federated graph network.

DOMAIN EXPERTISE:
- LCC Classification: {context.lcc_domain}
- Subject Headings: {', '.join(subject_headings)}
- Authority Records: {', '.join(authority_records)}
- Expert Vocabulary: {', '.join(expert_vocabulary)}
- Expertise Level: {context.expertise_level}/1.0

NETWORK CONTEXT:
- Active Relationships: {len(context.relationships)} agents
- Trusted Collaborators: {', '.join(trusted_agents) if trusted_agents else 'None yet'}
- Current Debates: {len(context.current_debates)} active

RECENT INTERACTIONS:
{self._format_conversation_history(recent_messages)}

REASONING TASK:
{task}

You must reason as an expert in your domain, using your MARC knowledge and considering your network relationships. Respond with structured JSON containing your reasoning process and conclusions.

Expected JSON format:
{{
    "reasoning_process": [
        "Step 1: Analysis of...",
        "Step 2: Consideration of...",
        "Step 3: Synthesis of..."
    ],
    "domain_analysis": "Your expert analysis using MARC knowledge",
    "network_considerations": "How relationships influence your decision",
    "confidence_level": 0.85,
    "evidence_sources": ["MARC:123", "Authority:LC456"],
    "conclusion": "Your final reasoned conclusion",
    "recommended_actions": ["action1", "action2"],
    "collaboration_needs": ["Which agents would help with this"]
}}
"""
        return prompt
    
    def _format_conversation_history(self, messages: List[Dict[str, Any]]) -> str:
        """Format conversation history for prompt"""
        if not messages:
            return "No recent interactions"
        
        formatted = []
        for msg in messages:
            sender = msg.get('sender', 'unknown')
            msg_type = msg.get('type', 'message')
            content = str(msg.get('content', ''))[:100] + "..." if len(str(msg.get('content', ''))) > 100 else str(msg.get('content', ''))
            formatted.append(f"- {sender} ({msg_type}): {content}")
        
        return "\n".join(formatted)
    
    async def _openai_reasoning(self, prompt: str, backend: AIBackend) -> Dict[str, Any]:
        """OpenAI-powered reasoning"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not available")
        
        # Select model based on backend
        model = "gpt-4o" if backend == AIBackend.OPENAI_GPT4 else "gpt-3.5-turbo"
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert AI agent in a federated graph network. Provide detailed, structured reasoning using your domain expertise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            reasoning_result = json.loads(content)
            
            # Add metadata
            reasoning_result["ai_backend"] = backend.value
            reasoning_result["model"] = model
            reasoning_result["tokens_used"] = response.usage.total_tokens
            
            return reasoning_result
            
        except Exception as e:
            return {
                "error": f"OpenAI reasoning failed: {str(e)}",
                "ai_backend": backend.value,
                "fallback_reasoning": "Unable to complete advanced reasoning"
            }
    
    async def _perplexity_reasoning(self, prompt: str, backend: AIBackend) -> Dict[str, Any]:
        """Perplexity-powered reasoning with web knowledge"""
        if not self.perplexity_session:
            raise RuntimeError("Perplexity client not available")
        
        # Select model
        model = "llama-3.1-sonar-large-128k-online" if backend == AIBackend.PERPLEXITY_SONAR else "llama-3.1-70b-instruct"
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert AI agent. Provide structured JSON reasoning with current web knowledge when relevant."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            response = self.perplexity_session.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON from response
                try:
                    reasoning_result = json.loads(content)
                except json.JSONDecodeError:
                    # Extract JSON if embedded in text
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        reasoning_result = json.loads(json_match.group())
                    else:
                        reasoning_result = {"raw_response": content}
                
                # Add metadata
                reasoning_result["ai_backend"] = backend.value
                reasoning_result["model"] = model
                reasoning_result["web_enhanced"] = "sonar" in model
                
                # Add citations if available
                if result.get("citations"):
                    reasoning_result["web_sources"] = result["citations"]
                
                return reasoning_result
            
            else:
                return {
                    "error": f"Perplexity API error: {response.status_code}",
                    "ai_backend": backend.value
                }
                
        except Exception as e:
            return {
                "error": f"Perplexity reasoning failed: {str(e)}",
                "ai_backend": backend.value
            }


# Demonstration Functions

async def demo_debate_reasoning():
    """Demo: Agent reasoning for debate participation"""
    print("🧠 AI Cognitive Engine Demo: Debate Reasoning")
    print("=" * 50)
    
    engine = AICognitiveEngine()
    
    # Create agent context
    context = AgentContext(
        agent_id="supply_chain_expert",
        lcc_domain="HF5001",
        marc_knowledge={
            "subject_headings": ["Business logistics", "Supply chain management", "Procurement"],
            "authority_records": ["LC:sh85018285", "LC:sh2006002083"],
            "expert_vocabulary": ["inventory optimization", "vendor management", "procurement strategy"]
        },
        conversation_history=[
            {
                "sender": "blockchain_expert",
                "type": "debate_proposal",
                "content": {"topic": "Blockchain transparency vs privacy", "position": "Full transparency"}
            }
        ],
        relationships={
            "blockchain_expert": 0.6,
            "business_analyst": 0.8
        },
        current_debates=["debate_12345"]
    )
    
    # Reasoning task
    task = """
    A blockchain expert has proposed a debate about implementing full blockchain transparency 
    in supply chains. They argue for complete visibility of all transactions. As a supply 
    chain expert, should you engage in this debate? What position should you take considering 
    vendor privacy concerns and business practicalities?
    """
    
    print("🤔 Agent Context:")
    print(f"   Domain: {context.lcc_domain}")
    print(f"   Expertise: {', '.join(context.marc_knowledge['subject_headings'])}")
    print(f"   Relationships: {len(context.relationships)} agents")
    
    print("\n🎯 Reasoning Task:")
    print(f"   {task[:100]}...")
    
    # Test different AI backends
    backends = [AIBackend.OPENAI_GPT4]
    
    if os.getenv('PERPLEXITY_API_KEY'):
        backends.append(AIBackend.PERPLEXITY_SONAR)
    
    for backend in backends:
        print(f"\n🔮 Reasoning with {backend.value}...")
        
        try:
            result = await engine.agent_reasoning(context, task, backend)
            
            if "error" in result:
                print(f"   ❌ {result['error']}")
                continue
            
            print(f"   ✅ Reasoning completed")
            print(f"   🎯 Conclusion: {result.get('conclusion', 'No conclusion')}")
            print(f"   📊 Confidence: {result.get('confidence_level', 'Unknown')}")
            print(f"   🔗 Actions: {', '.join(result.get('recommended_actions', []))}")
            
            if result.get('web_enhanced'):
                print(f"   🌐 Enhanced with web knowledge")
            
            if result.get('tokens_used'):
                print(f"   💰 Tokens used: {result['tokens_used']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def demo_courtship_reasoning():
    """Demo: Agent reasoning for relationship formation"""
    print("\n💕 AI Cognitive Engine Demo: Courtship Reasoning")
    print("=" * 50)
    
    engine = AICognitiveEngine()
    
    # Create context for courtship decision
    context = AgentContext(
        agent_id="crypto_expert",
        lcc_domain="QA76.9",
        marc_knowledge={
            "subject_headings": ["Cryptography", "Computer security", "Distributed systems"],
            "authority_records": ["LC:sh85034740", "LC:sh85029553"],
            "expert_vocabulary": ["encryption", "blockchain", "consensus algorithms", "smart contracts"]
        },
        conversation_history=[],
        relationships={
            "supply_chain_expert": 0.3  # Weak existing relationship
        },
        current_debates=[]
    )
    
    task = """
    Another agent (fintech_specialist in domain HG4501) has sent you a courtship signal. 
    Their expertise includes "digital payments", "financial technology", and "regulatory compliance".
    They've shown interest in collaborating on cryptocurrency regulation topics.
    
    Should you form a stronger relationship with this agent? Consider domain synergy,
    potential collaboration benefits, and network growth strategy.
    """
    
    print("🤔 Agent Context:")
    print(f"   Domain: {context.lcc_domain} (Cryptography)")
    print(f"   Current relationships: {len(context.relationships)}")
    
    print("\n💘 Courtship Decision:")
    print("   Evaluating potential relationship with fintech_specialist...")
    
    try:
        result = await engine.agent_reasoning(context, task, AIBackend.OPENAI_GPT4)
        
        if "error" not in result:
            print(f"   ✅ Decision: {result.get('conclusion', 'No decision')}")
            print(f"   📊 Confidence: {result.get('confidence_level', 'Unknown')}")
            
            domain_analysis = result.get('domain_analysis', '')
            if domain_analysis:
                print(f"   🔬 Domain Analysis: {domain_analysis[:100]}...")
            
            network_considerations = result.get('network_considerations', '')
            if network_considerations:
                print(f"   🕸️  Network Strategy: {network_considerations[:100]}...")
        else:
            print(f"   ❌ {result['error']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def demo_knowledge_synthesis():
    """Demo: Agent reasoning for knowledge synthesis"""
    print("\n🧬 AI Cognitive Engine Demo: Knowledge Synthesis")
    print("=" * 50)
    
    engine = AICognitiveEngine()
    
    # Context for knowledge synthesis
    context = AgentContext(
        agent_id="business_analyst",
        lcc_domain="HD28",
        marc_knowledge={
            "subject_headings": ["Business analysis", "Strategic planning", "Risk assessment"],
            "authority_records": ["LC:sh85017987", "LC:sh85113862"],
            "expert_vocabulary": ["cost-benefit analysis", "stakeholder management", "business intelligence"]
        },
        conversation_history=[
            {
                "sender": "supply_chain_expert",
                "type": "knowledge_share",
                "content": {"insight": "Blockchain reduces inventory discrepancies by 30%"}
            },
            {
                "sender": "crypto_expert", 
                "type": "knowledge_share",
                "content": {"insight": "Smart contracts can automate compliance checking"}
            }
        ],
        relationships={
            "supply_chain_expert": 0.9,
            "crypto_expert": 0.7
        },
        current_debates=[]
    )
    
    task = """
    You've received knowledge from two trusted agents about blockchain in supply chains.
    Synthesize this information with your business analysis expertise to:
    1. Identify the business value proposition
    2. Assess implementation risks
    3. Recommend next steps for the organization
    
    Consider both technical feasibility and business impact.
    """
    
    print("🤔 Knowledge Synthesis Task:")
    print("   Combining supply chain + crypto insights...")
    print(f"   Trusted sources: {len([r for r in context.relationships.values() if r > 0.7])}")
    
    try:
        result = await engine.agent_reasoning(context, task, AIBackend.OPENAI_GPT4)
        
        if "error" not in result:
            print(f"   ✅ Synthesis completed")
            
            reasoning_steps = result.get('reasoning_process', [])
            if reasoning_steps:
                print("   🔬 Reasoning Process:")
                for i, step in enumerate(reasoning_steps[:3]):
                    print(f"      {i+1}. {step[:80]}...")
            
            actions = result.get('recommended_actions', [])
            if actions:
                print(f"   🎯 Recommended Actions:")
                for action in actions[:3]:
                    print(f"      • {action}")
            
            collaboration_needs = result.get('collaboration_needs', [])
            if collaboration_needs:
                print(f"   🤝 Collaboration Needs: {', '.join(collaboration_needs)}")
        else:
            print(f"   ❌ {result['error']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")


async def main():
    """Run all AI cognitive engine demonstrations"""
    print("🚀 AI Cognitive Engine Examples for Federated Graph Framework")
    print("🧠 Showing how GPT, Perplexity, and OpenAI power agent reasoning")
    print("=" * 70)
    
    # Check API availability
    if not HAS_AI:
        print("❌ Missing AI dependencies. Install with: pip install openai requests")
        return
    
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('PERPLEXITY_API_KEY'):
        print("❌ No AI API keys found. Set OPENAI_API_KEY or PERPLEXITY_API_KEY")
        return
    
    print("✅ AI backends available:")
    if os.getenv('OPENAI_API_KEY'):
        print("   • OpenAI GPT-4 & GPT-3.5")
    if os.getenv('PERPLEXITY_API_KEY'):
        print("   • Perplexity Sonar & Llama")
    
    print("\n" + "🔮 COGNITIVE REASONING DEMONSTRATIONS" + "=" * 20)
    
    # Run demonstrations
    await demo_debate_reasoning()
    await demo_courtship_reasoning() 
    await demo_knowledge_synthesis()
    
    print("\n" + "=" * 70)
    print("🎉 AI Cognitive Engine Demonstrations Complete!")
    print("\n💡 Key Insights:")
    print("   • AI provides sophisticated reasoning for agent decisions")
    print("   • MARC knowledge enhances domain-specific reasoning")  
    print("   • Different AI backends offer different capabilities")
    print("   • Agents use AI to evaluate relationships and collaborations")
    print("   • Knowledge synthesis enables emergent intelligence")


if __name__ == "__main__":
    asyncio.run(main())