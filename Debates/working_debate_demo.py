#!/usr/bin/env python3
"""
Working Real Debate Demo - Enhanced Federated Graph Framework
Simplified version that actually works for starting debates
"""

import time
from typing import Dict, List, Any
import torch

# Simplified imports to avoid dependency issues
from core_base import DebateEngine, DebateAction, DebateOperation
from mathematical_formalism_v2 import DebateDynamics, DebateState, DebateProtocol, EvidenceInput, PolicyRules

class WorkingDebateDemo:
    """Working demonstration of real debate capabilities"""
    
    def __init__(self):
        self.debate_engine = DebateEngine()
        print("🎯 Working Real Debate Demo Initialized")
        print("✅ Core Debate Engine Ready")
    
    def start_simple_debate(self, topic: str) -> str:
        """Start a simple debate that actually works"""
        print(f"\n🔥 Starting Real Debate: '{topic}'")
        
        # Create working debate proposal
        proposal = DebateAction(
            operation=DebateOperation.PROPOSAL,
            agent_id="demo_starter",
            target_agent_id=None,
            subject=topic,
            content={
                "topic": topic,
                "initiated_by": "working_demo",
                "debate_type": "real_debate"
            },
            evidence=[f"User initiated real debate: {topic}"]
        )
        
        # Start the debate
        debate_id = self.debate_engine.initiate_debate(proposal)
        print(f"✅ Real Debate Started - ID: {debate_id}")
        
        # Add some follow-up actions to show it's working
        self._demonstrate_debate_actions(debate_id, topic)
        
        return debate_id
    
    def _demonstrate_debate_actions(self, debate_id: str, topic: str):
        """Add some demonstration actions to show debate is active"""
        print(f"\n📝 Adding debate actions to demonstrate real functionality...")
        
        # Add objection
        objection = DebateAction(
            operation=DebateOperation.OBJECTION,
            agent_id="critic_agent",
            target_agent_id="demo_starter",
            subject=f"Concerns about: {topic}",
            content={
                "objection": f"We need to consider potential risks and challenges with: {topic}",
                "reasoning": "Risk assessment is crucial for any major decision"
            },
            evidence=["Industry best practices suggest thorough evaluation"]
        )
        
        self.debate_engine.add_action(debate_id, objection)
        print(f"  ✅ Added objection from critic_agent")
        
        # Add support
        support = DebateAction(
            operation=DebateOperation.ACCEPT,
            agent_id="supporter_agent", 
            target_agent_id="demo_starter",
            subject=f"Support for: {topic}",
            content={
                "support": f"Strong evidence supports the benefits of: {topic}",
                "reasoning": "The advantages outweigh potential concerns"
            },
            evidence=["Research data shows positive outcomes"]
        )
        
        self.debate_engine.add_action(debate_id, support)
        print(f"  ✅ Added support from supporter_agent")
        
        # Check consensus
        has_consensus, consensus_data = self.debate_engine.evaluate_consensus(debate_id)
        print(f"  📊 Consensus check: {'Reached' if has_consensus else 'In progress'}")
        
        return debate_id
    
    def start_mathematical_debate(self, topic: str) -> Dict[str, Any]:
        """Start a debate using mathematical formalism"""
        print(f"\n🔬 Starting Mathematical Debate: '{topic}'")
        
        # Initialize mathematical debate components
        print("  📊 Initializing mathematical debate state...")
        
        # 3 agents, 5-dimensional belief space
        agent_beliefs = torch.randn(3, 5)
        argument_topology = torch.eye(3) * 0.5  # Weak initial connections
        stance_scores = torch.zeros(3)
        
        debate_state = DebateState(
            agent_beliefs=agent_beliefs,
            argument_topology=argument_topology,
            stance_scores=stance_scores
        )
        
        # Create evidence
        evidence = EvidenceInput(
            evidence_vector=torch.randn(5),
            credibility_weight=0.8,
            relevance_score=0.9
        )
        
        # Set policy
        policy = PolicyRules(
            turn_limits=5,
            evidence_standards=0.7,
            fairness_constraints={"balanced_participation": True},
            termination_criteria={"convergence_threshold": 0.1}
        )
        
        # Initialize debate dynamics
        dynamics = DebateDynamics(DebateProtocol.CONSENSUS_BUILDING)
        
        print(f"  ✅ Mathematical state initialized:")
        print(f"    - {agent_beliefs.shape[0]} agents with {agent_beliefs.shape[1]}D beliefs")
        print(f"    - Evidence credibility: {evidence.credibility_weight}")
        print(f"    - Protocol: {DebateProtocol.CONSENSUS_BUILDING.value}")
        
        # Run debate transitions
        print(f"\n  🔄 Running mathematical debate transitions...")
        
        states = [debate_state]
        for round_num in range(3):
            print(f"    Round {round_num + 1}:")
            
            # Run transition
            new_state = dynamics.transition(states[-1], evidence, policy)
            states.append(new_state)
            
            # Calculate changes
            belief_change = torch.norm(new_state.agent_beliefs - states[-2].agent_beliefs)
            stance_change = torch.norm(new_state.stance_scores - states[-2].stance_scores)
            
            print(f"      📈 Belief evolution: {belief_change:.3f}")
            print(f"      📈 Stance change: {stance_change:.3f}")
            
            # Check for equilibrium
            if dynamics.check_equilibrium(new_state, threshold=0.05):
                print(f"      🎯 Equilibrium reached!")
                break
        
        print(f"  ✅ Mathematical debate complete with {len(states)} states")
        
        return {
            "topic": topic,
            "protocol": DebateProtocol.CONSENSUS_BUILDING.value,
            "states": states,
            "evidence": evidence,
            "policy": policy,
            "rounds": len(states) - 1
        }

def demo_real_debates():
    """Run complete demonstration of real debate capabilities"""
    print("="*70)
    print("🎯 REAL DEBATE DEMONSTRATION - Enhanced Federated Graph Framework")
    print("="*70)
    
    demo = WorkingDebateDemo()
    
    # Demo 1: Simple Real Debate
    print(f"\n{'='*50}")
    print("🚀 DEMO 1: Simple Real Debate")
    print("="*50)
    
    topic1 = "Should our organization implement automated testing in our CI/CD pipeline?"
    debate_id = demo.start_simple_debate(topic1)
    
    # Demo 2: Mathematical Debate
    print(f"\n{'='*50}")
    print("🔬 DEMO 2: Mathematical Debate Dynamics")
    print("="*50)
    
    topic2 = "Adopting microservices vs monolithic architecture"
    math_result = demo.start_mathematical_debate(topic2)
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 DEMONSTRATION SUMMARY")
    print("="*50)
    print(f"✅ Simple debate started with ID: {debate_id}")
    print(f"✅ Mathematical debate completed {math_result['rounds']} rounds")
    print(f"✅ Both debates demonstrate real working functionality")
    
    print(f"\n🎯 Next Steps to Continue Debates:")
    print(f"  1. Use debate ID '{debate_id}' to add more actions")
    print(f"  2. Access mathematical states for further analysis")
    print(f"  3. Open http://localhost:8501 for Streamlit UI")
    print(f"  4. Use API endpoints at http://localhost:5001/api/")
    
    return {
        "simple_debate_id": debate_id,
        "mathematical_result": math_result
    }

if __name__ == "__main__":
    try:
        results = demo_real_debates()
        print(f"\n🎉 Real debate demonstration completed successfully!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()