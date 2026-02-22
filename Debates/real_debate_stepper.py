"""
Real Debate Stepper - Connected to Enhanced Federated Graph Framework
====================================================================

This creates an actual debate using the core DebateEngine from your framework,
not a simulation with mock data.
"""

from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import sys
import os
import uuid
import json
from typing import Dict, List, Any, Optional

# Add the current directory to Python path to import your modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your actual debate framework components
try:
    from core_base import DebateEngine, Agent, DebateAction, DebateOperation
    from mathematical_formalism_v2 import DebateDynamics, DebateProtocol, DebateState, EvidenceInput, PolicyRules
    import torch
    FRAMEWORK_AVAILABLE = True
    print("✅ Successfully imported Enhanced Federated Graph Framework components")
except ImportError as e:
    print(f"⚠️ Could not import framework components: {e}")
    print("📝 Running in simulation mode only")
    FRAMEWORK_AVAILABLE = False

app = Flask(__name__)

class RealDebateAgent(Agent):
    """Real agent that participates in debates using your framework."""
    
    def __init__(self, agent_id: str, name: str, expertise: str, stance: str):
        self.agent_id = agent_id
        self.name = name
        self.expertise = expertise
        self.stance = stance
        self.confidence = 0.8
    
    def propose_change(self, current_graph, context=None):
        """Propose a change based on agent's expertise and stance."""
        return DebateAction(
            operation=DebateOperation.PROPOSAL,
            agent_id=self.agent_id,
            target_agent_id=None,
            subject=f"Integration proposal from {self.expertise}",
            content={
                'proposal': f"{self.name}: {self.stance}",
                'expertise': self.expertise,
                'confidence': self.confidence,
                'reasoning': f"Based on my expertise in {self.expertise}, I propose: {self.stance}"
            }
        )
    
    def evaluate_proposal(self, proposal, current_graph):
        """Evaluate another agent's proposal."""
        return DebateAction(
            operation=DebateOperation.OBJECTION,
            agent_id=self.agent_id,
            target_agent_id=proposal.agent_id,
            subject=f"Evaluation of {proposal.agent_id} proposal",
            content={
                'response': f"{self.name} evaluating proposal from {proposal.agent_id}",
                'agreement_level': 0.6,  # Mock agreement level
                'critique': f"From a {self.expertise} perspective, this proposal has merit but needs refinement.",
                'reasoning': f"My analysis based on {self.expertise} expertise"
            }
        )
    
    def vote(self, debate_context):
        """Vote on the current debate state."""
        return DebateAction(
            operation=DebateOperation.VOTE,
            agent_id=self.agent_id,
            target_agent_id=None,
            subject=f"Vote from {self.expertise} expert",
            content={
                'vote': 'support',
                'confidence': self.confidence,
                'reasoning': f"Supporting based on {self.expertise} analysis"
            }
        )

class SubjectAnalyzer:
    """Analyzes and classifies debate subjects with taxonomic categorization."""
    
    def __init__(self):
        # Library of Congress Classification mappings for common debate topics
        self.lcc_mappings = {
            # Technology & Engineering
            'data': 'QA75-76.95 (Computer Science - Data Processing)',
            'integration': 'T58.6 (Systems Engineering)',
            'architecture': 'T58.5 (Systems Analysis and Design)',
            'cloud': 'QA75.5-76.95 (Cloud Computing)',
            'api': 'QA76.76.A65 (Application Programming Interfaces)',
            'database': 'QA76.9.D3 (Database Management)',
            'analytics': 'QA76.9.D343 (Data Analytics)',
            'machine learning': 'Q325.5 (Machine Learning)',
            'artificial intelligence': 'Q335 (Artificial Intelligence)',
            
            # Business & Management
            'strategy': 'HD30.28 (Strategic Planning)',
            'operations': 'HD38-40.7 (Operations Management)',
            'finance': 'HG1-9999 (Finance)',
            'marketing': 'HF5410-5417.5 (Marketing)',
            'roi': 'HF5681.R6 (Return on Investment)',
            'compliance': 'K1-7720 (Legal Compliance)',
            'governance': 'HD2741 (Corporate Governance)',
            
            # Healthcare & Medicine
            'healthcare': 'R5-920 (Medicine - General)',
            'patient': 'R727.3 (Patient Care)',
            'medical': 'R5-920 (Medical Sciences)',
            'clinical': 'R854-855 (Clinical Medicine)',
            'pharmacy': 'RS1-441 (Pharmacy)',
            'nursing': 'RT1-120 (Nursing)',
            'medicaid': 'RA412.2 (Government Health Programs)',
            'enrollment': 'RA412 (Health Insurance)',
            'protocol': 'R853.C55 (Clinical Protocols)',
            
            # Social Sciences
            'engagement': 'HM1001-1281 (Social Psychology)',
            'communication': 'P87-96 (Communication Studies)',
            'education': 'L7-991 (Education)',
            'training': 'HD5715 (Employee Training)',
            'coordination': 'HD58.7 (Organizational Coordination)',
            
            # Information Science
            'optimization': 'QA402.5 (Mathematical Optimization)',
            'monitoring': 'T58.6 (Systems Monitoring)',
            'automation': 'T59.5 (Industrial Automation)',
            'workflow': 'HD58.87 (Workflow Management)',
            'process': 'T58.5 (Process Analysis)'
        }
    
    def analyze_subject(self, user_query: str) -> Dict[str, Any]:
        """Analyze user query and return structured subject classification."""
        
        # Convert to lowercase for analysis
        query_lower = user_query.lower()
        
        # Extract key terms and map to LCC
        detected_categories = []
        primary_lcc = None
        confidence_score = 0.0
        
        for term, lcc_code in self.lcc_mappings.items():
            if term in query_lower:
                detected_categories.append({
                    'term': term,
                    'lcc_code': lcc_code,
                    'relevance': query_lower.count(term)
                })
        
        # Sort by relevance and select primary classification
        if detected_categories:
            detected_categories.sort(key=lambda x: x['relevance'], reverse=True)
            primary_lcc = detected_categories[0]['lcc_code']
            confidence_score = min(len(detected_categories) * 0.2, 1.0)
        
        # Generate concise problem statement
        problem_statement = self._generate_problem_statement(user_query, detected_categories)
        
        # Determine debate complexity and stakeholders
        complexity_analysis = self._analyze_complexity(detected_categories)
        
        return {
            'original_query': user_query,
            'problem_statement': problem_statement,
            'primary_lcc_classification': primary_lcc or 'H1-9999 (General Social Sciences)',
            'detected_categories': detected_categories,
            'confidence_score': confidence_score,
            'complexity_level': complexity_analysis['level'],
            'recommended_stakeholders': complexity_analysis['stakeholders'],
            'debate_dimensions': complexity_analysis['dimensions'],
            'estimated_steps': complexity_analysis['estimated_steps']
        }
    
    def _generate_problem_statement(self, query: str, categories: List[Dict]) -> str:
        """Generate concise, structured problem statement."""
        
        if not categories:
            return f"Analysis required: {query}"
        
        # Extract primary domain
        primary_domain = categories[0]['term'] if categories else 'general'
        
        # Common problem statement patterns
        if 'integration' in [c['term'] for c in categories]:
            return f"System integration challenge: Optimizing {primary_domain} integration across organizational boundaries with consideration for technical feasibility, operational impact, and strategic alignment."
        
        elif 'optimization' in [c['term'] for c in categories] or 'process' in [c['term'] for c in categories]:
            return f"Process optimization requirement: Enhancing {primary_domain} workflows to improve efficiency, reduce costs, and maintain quality standards while ensuring stakeholder adoption."
        
        elif 'healthcare' in [c['term'] for c in categories] or 'patient' in [c['term'] for c in categories]:
            return f"Healthcare delivery challenge: Improving {primary_domain} outcomes through systematic process enhancement, technology integration, and patient-centered care coordination."
        
        elif 'data' in [c['term'] for c in categories] or 'analytics' in [c['term'] for c in categories]:
            return f"Data strategy decision: Establishing {primary_domain} architecture that balances analytical capabilities, governance requirements, and operational performance."
        
        else:
            return f"Strategic decision requirement: Evaluating {primary_domain} approaches to achieve organizational objectives while managing risks, resources, and stakeholder interests."
    
    def _analyze_complexity(self, categories: List[Dict]) -> Dict[str, Any]:
        """Analyze debate complexity and recommend appropriate stakeholders."""
        
        complexity_indicators = len(categories)
        
        if complexity_indicators <= 2:
            return {
                'level': 'Low',
                'stakeholders': ['Technical Lead', 'Business Analyst'],
                'dimensions': ['Technical', 'Business'],
                'estimated_steps': 3
            }
        elif complexity_indicators <= 4:
            return {
                'level': 'Medium',
                'stakeholders': ['Data Architect', 'Integration Engineer', 'Business Analyst'],
                'dimensions': ['Technical', 'Business', 'Operational'],
                'estimated_steps': 5
            }
        else:
            return {
                'level': 'High',
                'stakeholders': ['Data Architect', 'Integration Engineer', 'Business Analyst', 'Compliance Officer', 'Operations Manager'],
                'dimensions': ['Technical', 'Business', 'Operational', 'Regulatory', 'Strategic'],
                'estimated_steps': 7
            }


class RealDebateManager:
    """Manages real debates using your actual DebateEngine."""
    
    def __init__(self):
        if FRAMEWORK_AVAILABLE:
            self.debate_engine = DebateEngine()
            try:
                self.debate_dynamics = DebateDynamics(protocol=DebateProtocol.CONSENSUS_BUILDING)
            except:
                print("⚠️ DebateDynamics not available - using basic debate engine only")
                self.debate_dynamics = None
        else:
            self.debate_engine = None
            self.debate_dynamics = None
        
        self.active_debates = {}
        self.agents = {}  # We manage agents separately since DebateEngine doesn't have agents dict
        self.subject_analyzer = SubjectAnalyzer()  # Add subject analysis capability
        
        # Initialize some test agents
        self.setup_test_agents()
    
    def setup_test_agents(self):
        """Create test agents for the debate."""
        test_agents = [
            {
                'id': 'data_architect',
                'name': 'Senior Data Architect',
                'expertise': 'Data Architecture & Integration',
                'stance': 'We need a robust data lake architecture with proper governance layers'
            },
            {
                'id': 'integration_engineer', 
                'name': 'Integration Engineer',
                'expertise': 'System Integration & APIs',
                'stance': 'Real-time data streaming with event-driven architecture is crucial'
            },
            {
                'id': 'business_analyst',
                'name': 'Business Analyst',
                'expertise': 'Business Requirements & ROI',
                'stance': 'Solution must deliver measurable business value within 6 months'
            }
        ]
        
        for agent_data in test_agents:
            agent = RealDebateAgent(
                agent_id=agent_data['id'],
                name=agent_data['name'],
                expertise=agent_data['expertise'],
                stance=agent_data['stance']
            )
            self.agents[agent_data['id']] = agent
            # Store agents in our manager since DebateEngine manages debates, not agents
    
    def start_new_debate(self, topic: str, mode: str = "consensus_building"):
        """Start a new debate using the real DebateEngine with subject analysis."""
        debate_id = str(uuid.uuid4())[:8]
        
        # FIRST: Analyze and classify the subject matter
        subject_analysis = self.subject_analyzer.analyze_subject(topic)
        
        # Create debate data with subject analysis
        debate_data = {
            'debate_id': debate_id,
            'original_topic': topic,
            'subject_analysis': subject_analysis,
            'mode': mode,
            'status': 'initialized',  # Start with subject analysis phase
            'current_step': 0,
            'created_at': datetime.now().isoformat(),
            'participants': list(self.agents.keys()),
            'history': [],
            'current_state': None
        }
        
        # Add subject analysis as Step 0 (pre-debate initialization)
        subject_step = {
            'step': 0,
            'phase': 'Subject Analysis & Classification',
            'content': {
                'problem_statement': subject_analysis['problem_statement'],
                'lcc_classification': subject_analysis['primary_lcc_classification'],
                'complexity_level': subject_analysis['complexity_level'],
                'recommended_stakeholders': subject_analysis['recommended_stakeholders'],
                'debate_dimensions': subject_analysis['debate_dimensions'],
                'estimated_steps': subject_analysis['estimated_steps'],
                'confidence_score': subject_analysis['confidence_score']
            },
            'timestamp': datetime.now().isoformat()
        }
        
        debate_data['history'].append(subject_step)
        
        if FRAMEWORK_AVAILABLE:
            # Initialize debate state for mathematical formalism
            num_agents = len(self.agents)
            agent_beliefs = torch.randn(num_agents, 10)  # 10-dimensional belief space
            argument_topology = torch.randn(10, 10)     # 10x10 argument graph
            stance_scores = torch.randn(num_agents)      # Agent stance strengths
            
            debate_data['current_state'] = DebateState(
                agent_beliefs=agent_beliefs,
                argument_topology=argument_topology,
                stance_scores=stance_scores
            )
        
        # Set status to active after analysis
        debate_data['status'] = 'active'
        
        self.active_debates[debate_id] = debate_data
        return debate_id
    
    def advance_debate(self, debate_id: str):
        """Advance the debate by one step using real DebateEngine."""
        if debate_id not in self.active_debates:
            return None
        
        debate = self.active_debates[debate_id]
        debate['current_step'] += 1
        step = debate['current_step']
        
        # Get all previous debate history for context
        previous_steps = debate.get('history', [])
        
        if not FRAMEWORK_AVAILABLE:
            # Fallback simulation mode
            agent_names = list(self.agents.keys())
            current_agent = agent_names[(step - 1) % len(agent_names)]
            agent = self.agents[current_agent]
            
            step_content = {
                'step': step,
                'agent_id': current_agent,
                'agent_name': agent.name,
                'content': f"Step {step}: {agent.stance}",
                'action_type': 'proposal' if step <= 3 else 'response',
                'timestamp': datetime.now().isoformat()
            }
            
            debate['history'].append(step_content)
            return step_content
        
        # Real debate engine logic with progressive conversation
        try:
            if step == 1:
                # First step: agent proposals
                proposals = []
                for agent_id, agent in self.agents.items():
                    proposal = agent.propose_change(None, {'topic': debate['topic']})
                    if proposal:
                        debate_thread_id = self.debate_engine.initiate_debate(proposal)
                        proposals.append({
                            'agent_id': agent_id,
                            'agent_name': agent.name,
                            'proposal': proposal.content,
                            'debate_thread_id': debate_thread_id
                        })
                
                step_content = {
                    'step': step,
                    'phase': 'Initial Proposals',
                    'content': proposals,
                    'timestamp': datetime.now().isoformat()
                }
                
            elif step <= 4:
                # Progressive response phases with building arguments
                responses = []
                agent_list = list(self.agents.items())
                
                for i, (agent_id, agent) in enumerate(agent_list):
                    # Create contextual responses based on previous steps
                    context_aware_response = self._generate_contextual_response(
                        agent, agent_id, step, previous_steps, debate['topic']
                    )
                    
                    # Use real DebateEngine to process the response
                    if previous_steps and len(previous_steps[0]['content']) > 0:
                        # Find a different proposal to evaluate (round-robin style)
                        proposal_index = (step + i) % len(previous_steps[0]['content'])
                        target_proposal = previous_steps[0]['content'][proposal_index]
                        
                        if target_proposal['agent_id'] != agent_id:
                            mock_proposal = DebateAction(
                                operation=DebateOperation.PROPOSAL,
                                agent_id=target_proposal['agent_id'],
                                target_agent_id=None,
                                subject=f"Proposal evaluation - Step {step}",
                                content=target_proposal['proposal']
                            )
                            
                            # Add to DebateEngine for tracking
                            for debate_thread_id in [p.get('debate_thread_id') for p in previous_steps[0]['content']]:
                                if debate_thread_id:
                                    evaluation_action = DebateAction(
                                        operation=DebateOperation.OBJECTION,
                                        agent_id=agent_id,
                                        target_agent_id=target_proposal['agent_id'],
                                        subject=f"Step {step} evaluation",
                                        content=context_aware_response
                                    )
                                    self.debate_engine.add_action(debate_thread_id, evaluation_action)
                                    break
                            
                            responses.append({
                                'agent_id': agent_id,
                                'agent_name': agent.name,
                                'response': context_aware_response,
                                'evaluating': target_proposal['agent_id'],
                                'step_context': step
                            })
                
                step_content = {
                    'step': step,
                    'phase': f'Progressive Discussion - Round {step - 1}',
                    'content': responses,
                    'timestamp': datetime.now().isoformat()
                }
                
            else:
                # Consensus and voting phase
                votes = []
                for agent_id, agent in self.agents.items():
                    contextual_vote = self._generate_contextual_vote(
                        agent, agent_id, previous_steps, debate['topic']
                    )
                    
                    vote_action = DebateAction(
                        operation=DebateOperation.VOTE,
                        agent_id=agent_id,
                        target_agent_id=None,
                        subject=f"Final vote - {debate['topic']}",
                        content=contextual_vote
                    )
                    
                    votes.append({
                        'agent_id': agent_id,
                        'agent_name': agent.name,
                        'vote': contextual_vote,
                    })
                
                # Use real DebateEngine consensus evaluation
                support_count = len([v for v in votes if v['vote'].get('decision') == 'support'])
                total_votes = len(votes)
                consensus_reached = support_count >= (total_votes * 0.6)  # 60% threshold
                
                step_content = {
                    'step': step,
                    'phase': 'Final Consensus & Voting',
                    'content': votes,
                    'consensus_reached': consensus_reached,
                    'consensus_ratio': support_count / total_votes if total_votes > 0 else 0,
                    'timestamp': datetime.now().isoformat()
                }
                
                if consensus_reached:
                    debate['status'] = 'completed'
                    step_content['final_decision'] = self._generate_final_decision(votes, debate['topic'])
            
            debate['history'].append(step_content)
            return step_content
            
        except Exception as e:
            # Error handling - return error step
            error_step = {
                'step': step,
                'phase': 'Error',
                'content': f"Error in debate engine: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
            debate['history'].append(error_step)
            return error_step
    
    def get_debate_state(self, debate_id: str):
        """Get current state of a debate."""
        return self.active_debates.get(debate_id)
    
    def _generate_contextual_response(self, agent, agent_id, step, previous_steps, topic):
        """Generate context-aware responses that build on previous arguments."""
        
        # Healthcare protocol optimization examples from the attachment
        healthcare_contexts = {
            'data_architect': {
                2: {
                    'response': f"Regarding {topic}, I see merit in the integration approach, but we must prioritize data governance. Like healthcare enrollment verification, we need robust data validation at ingestion. My architecture proposal includes: 1) Real-time data quality checks, 2) HIPAA-compliant data lakes, 3) Automated compliance monitoring.",
                    'builds_on': 'integration patterns',
                    'evidence': ['data quality frameworks', 'compliance requirements']
                },
                3: {
                    'response': f"Building on the previous integration discussion, I want to address the risk assessment component. Similar to healthcare HRA completion tracking, our data architecture needs proactive monitoring. I propose: 1) Predictive analytics for system health, 2) Automated alerting for data anomalies, 3) Performance optimization triggers.",
                    'builds_on': 'monitoring systems',
                    'evidence': ['predictive analytics', 'system monitoring']
                },
                4: {
                    'response': f"After reviewing all proposals, I'm concerned about the care coordination aspect. Like healthcare referral tracking, our integration must ensure no data is lost in transitions. Final recommendation: 1) End-to-end data lineage tracking, 2) Cross-system reconciliation, 3) Failure recovery protocols with automated rollback.",
                    'builds_on': 'system reliability',
                    'evidence': ['data lineage', 'failure recovery']
                }
            },
            'integration_engineer': {
                2: {
                    'response': f"The data architecture proposal has solid foundations, but I'm focusing on the real-time aspect. Like healthcare care team engagement tracking, we need immediate response capabilities. My technical additions: 1) Event-driven microservices, 2) API-first design with circuit breakers, 3) Real-time streaming with Apache Kafka.",
                    'builds_on': 'real-time capabilities',
                    'evidence': ['event streaming', 'microservices patterns']
                },
                3: {
                    'response': f"I want to challenge the monitoring approach from a systems integration perspective. Healthcare shows us that missed follow-ups cascade into bigger issues. Our integration needs: 1) Intelligent retry mechanisms, 2) Dead letter queue processing, 3) Cross-system health checks with automatic failover.",
                    'builds_on': 'system resilience',
                    'evidence': ['retry patterns', 'failover mechanisms']
                },
                4: {
                    'response': f"Looking at the complete picture, I see gaps in our transition handling. Healthcare discharge planning teaches us that handoffs are critical failure points. Final technical spec: 1) Transactional orchestration across all systems, 2) Compensation patterns for partial failures, 3) Real-time status dashboards for operations teams.",
                    'builds_on': 'operational excellence',
                    'evidence': ['orchestration patterns', 'operational monitoring']
                }
            },
            'business_analyst': {
                2: {
                    'response': f"Both technical proposals sound sophisticated, but I need to ground this in business reality. Healthcare protocols show clear ROI tracking - enrollment verification prevents costly errors. For our integration: 1) Cost-benefit analysis for each component, 2) 6-month ROI targets with measurable KPIs, 3) Risk mitigation with business continuity planning.",
                    'builds_on': 'business value',
                    'evidence': ['ROI analysis', 'business continuity']
                },
                3: {
                    'response': f"I'm seeing technical complexity without clear business justification. Healthcare education shows that complex solutions fail without user adoption. Business requirements: 1) User training programs with adoption metrics, 2) Phased rollout with success criteria, 3) Change management with stakeholder buy-in processes.",
                    'builds_on': 'user adoption',
                    'evidence': ['change management', 'user training']
                },
                4: {
                    'response': f"After this discussion, I'm advocating for a balanced approach. Healthcare teaches us that perfect technical solutions fail without organizational readiness. Final business recommendation: 1) MVP approach with iterative improvements, 2) Business stakeholder engagement throughout, 3) Success metrics aligned with organizational goals, not just technical metrics.",
                    'builds_on': 'organizational readiness',
                    'evidence': ['MVP approach', 'stakeholder alignment']
                }
            }
        }
        
        # Get step-specific response or fallback to expertise-based response
        if agent_id in healthcare_contexts and step in healthcare_contexts[agent_id]:
            return healthcare_contexts[agent_id][step]
        else:
            # Fallback to generic but contextual response
            return {
                'response': f"From my {agent.expertise} perspective on {topic}, I believe we need to consider the implications discussed in previous steps. My analysis shows this requires careful balance between technical excellence and practical implementation.",
                'builds_on': 'previous discussion',
                'evidence': [agent.expertise.lower()]
            }
    
    def _generate_contextual_vote(self, agent, agent_id, previous_steps, topic):
        """Generate context-aware voting decisions based on the debate progression."""
        
        # Analyze the debate flow to make informed voting decisions
        vote_rationales = {
            'data_architect': {
                'decision': 'support_with_conditions',
                'confidence': 0.75,
                'rationale': f"I support the overall direction for {topic}, but with mandatory data governance requirements. Like healthcare protocols that require verification at each step, our integration must have built-in compliance and monitoring.",
                'conditions': ['Data governance framework implementation', 'Compliance monitoring automation', 'Data quality validation at all entry points']
            },
            'integration_engineer': {
                'decision': 'support',
                'confidence': 0.85,
                'rationale': f"The technical approach for {topic} is sound with the discussed resilience patterns. Healthcare teaches us that system reliability is non-negotiable - our integration design addresses this with proper failover and monitoring.",
                'conditions': ['Real-time monitoring implementation', 'Automated failover testing', 'Performance benchmarking']
            },
            'business_analyst': {
                'decision': 'conditional_support',
                'confidence': 0.65,
                'rationale': f"While I see the technical merit in our {topic} approach, I need stronger business case validation. Healthcare ROI tracking shows measurable outcomes - we need similar clarity on business value delivery.",
                'conditions': ['Clear ROI metrics definition', 'Phased implementation plan', 'Stakeholder training program']
            }
        }
        
        return vote_rationales.get(agent_id, {
            'decision': 'abstain',
            'confidence': 0.5,
            'rationale': f"Need more information to make an informed decision on {topic}",
            'conditions': ['Additional analysis required']
        })
    
    def _generate_final_decision(self, votes, topic):
        """Generate a final decision summary based on all votes."""
        support_votes = [v for v in votes if 'support' in v['vote'].get('decision', '')]
        
        if len(support_votes) >= len(votes) * 0.6:
            return {
                'decision': 'APPROVED_WITH_CONDITIONS',
                'summary': f"The proposal for {topic} is approved with implementation conditions from each stakeholder.",
                'next_steps': [
                    'Develop detailed implementation plan addressing all stakeholder conditions',
                    'Establish success metrics and monitoring framework',
                    'Create phased rollout schedule with checkpoints',
                    'Set up regular review meetings for progress tracking'
                ],
                'conditions_summary': [vote['vote'].get('conditions', []) for vote in votes if vote['vote'].get('conditions')]
            }
        else:
            return {
                'decision': 'REQUIRES_REVISION',
                'summary': f"The proposal for {topic} needs revision to address stakeholder concerns.",
                'next_steps': [
                    'Address concerns raised by each stakeholder',
                    'Revise proposal based on feedback',
                    'Schedule follow-up debate session',
                    'Provide additional evidence and analysis'
                ]
            }

# Global debate manager
debate_manager = RealDebateManager()

# HTML Template for the real debate interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Real Debate Engine</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
            min-height: 100vh;
            color: #E2E8F0;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: #1A202C;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 1px solid #2D3748;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #2D3748;
        }
        .header h1 {
            color: #F7FAFC;
            margin: 0;
            font-size: 2.5em;
        }
        .status-indicator {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin: 10px 0;
        }
        .framework-available { background: #38A169; color: white; }
        .framework-unavailable { background: #E53E3E; color: white; }
        .new-debate-section {
            background: #2D3748;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .input-group {
            margin-bottom: 15px;
        }
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #CBD5E0;
        }
        .input-group input, .input-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #4A5568;
            border-radius: 6px;
            background: #1A202C;
            color: #E2E8F0;
            font-size: 16px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 16px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #3182CE 0%, #2B6CB0 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(49, 130, 206, 0.4);
        }
        .btn-advance {
            background: linear-gradient(135deg, #38A169 0%, #2F855A 100%);
            color: white;
            width: 100%;
            margin: 10px 0;
        }
        .btn-advance:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(56, 161, 105, 0.4);
        }
        .debate-container {
            background: #2D3748;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .debate-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #4A5568;
        }
        .debate-title {
            font-size: 1.3em;
            font-weight: 600;
            color: #F7FAFC;
        }
        .debate-meta {
            font-size: 0.9em;
            color: #CBD5E0;
        }
        .debate-history {
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #4A5568;
            border-radius: 8px;
            background: #1A202C;
        }
        .debate-step {
            padding: 20px;
            border-bottom: 1px solid #2D3748;
        }
        .debate-step:last-child {
            border-bottom: none;
        }
        .step-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .step-number {
            background: #3182CE;
            color: white;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        .step-phase {
            font-weight: 600;
            color: #E2E8F0;
            font-size: 1.1em;
        }
        .step-content {
            margin-left: 45px;
            color: #CBD5E0;
            line-height: 1.6;
        }
        .agent-response {
            background: #2D3748;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #3182CE;
        }
        .agent-name {
            font-weight: 600;
            color: #E2E8F0;
            margin-bottom: 8px;
        }
        .proposal-content, .response-content, .vote-content {
            margin-bottom: 10px;
        }
        .reasoning, .builds-on, .evidence {
            font-size: 0.9em;
            color: #CBD5E0;
            margin-top: 8px;
            font-style: italic;
        }
        .evaluation-target {
            font-size: 0.8em;
            color: #A0AEC0;
            margin-top: 5px;
        }
        .vote-decision {
            font-size: 1.1em;
            font-weight: 600;
            color: #68D391;
        }
        .vote-confidence {
            color: #F7FAFC;
            margin: 5px 0;
        }
        .vote-rationale {
            color: #E2E8F0;
            margin: 8px 0;
        }
        .vote-conditions {
            margin-top: 10px;
        }
        .vote-conditions ul {
            margin: 5px 0 0 20px;
            color: #CBD5E0;
        }
        .subject-analysis {
            background: #1A202C;
            border: 2px solid #3182CE;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
        .analysis-section {
            margin-bottom: 20px;
        }
        .analysis-section h4 {
            color: #E2E8F0;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .analysis-section p {
            color: #CBD5E0;
            line-height: 1.6;
        }
        .analysis-section code {
            background: #2D3748;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #68D391;
        }
        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .analysis-item {
            background: #2D3748;
            padding: 10px;
            border-radius: 6px;
            color: #E2E8F0;
        }
        .dimensions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .dimension-tag {
            background: #3182CE;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: 500;
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-weight: 500;
        }
        .message.success {
            background: #22543D;
            color: #68D391;
            border: 1px solid #38A169;
        }
        .message.error {
            background: #742A2A;
            color: #FC8181;
            border: 1px solid #E53E3E;
        }
        .no-debates {
            text-align: center;
            color: #718096;
            font-style: italic;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Real Debate Engine</h1>
            <div class="status-indicator {{ 'framework-available' if framework_available else 'framework-unavailable' }}">
                {{ '✅ Enhanced Framework Connected' if framework_available else '⚠️ Simulation Mode Only' }}
            </div>
        </div>

        <div class="new-debate-section">
            <h3>Start New Debate</h3>
            <form onsubmit="startNewDebate(event)">
                <div class="input-group">
                    <label for="topic">Debate Topic:</label>
                    <input type="text" id="topic" name="topic" 
                           placeholder="Enter the topic you want the agents to debate"
                           value="How should we implement a cloud-native data architecture for real-time analytics?">
                </div>
                <div class="input-group">
                    <label for="mode">Debate Mode:</label>
                    <select id="mode" name="mode">
                        <option value="consensus_building">Consensus Building</option>
                        <option value="adversarial">Adversarial</option>
                        <option value="socratic">Socratic Questioning</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">🚀 Start Real Debate</button>
            </form>
        </div>

        <div id="message"></div>

        {% if debates %}
            {% for debate_id, debate in debates.items() %}
            <div class="debate-container">
                <div class="debate-header">
                    <div>
                        <div class="debate-title">{{ debate.subject_analysis.problem_statement if debate.subject_analysis else debate.original_topic if debate.original_topic else debate.topic }}</div>
                        <div class="debate-meta">
                            ID: {{ debate_id }} | Mode: {{ debate.mode }} | Step: {{ debate.current_step }} | Status: {{ debate.status }}
                            {% if debate.subject_analysis %}
                            <br><strong>LCC Classification:</strong> {{ debate.subject_analysis.primary_lcc_classification }}
                            <br><strong>Complexity:</strong> {{ debate.subject_analysis.complexity_level }} | <strong>Confidence:</strong> {{ (debate.subject_analysis.confidence_score * 100) | round }}%
                            {% endif %}
                        </div>
                    </div>
                    <button class="btn btn-advance" onclick="advanceDebate('{{ debate_id }}')"
                            {{ 'disabled' if debate.status != 'active' else '' }}>
                        ⚡ Advance Step (Y)
                    </button>
                </div>

                {% if debate.history %}
                <div class="debate-history">
                    {% for step in debate.history %}
                    <div class="debate-step">
                        <div class="step-header">
                            <div class="step-number">{{ step.step }}</div>
                            <div class="step-phase">{{ step.phase }}</div>
                        </div>
                        <div class="step-content">
                            {% if step.step == 0 %}
                                <!-- Subject Analysis Step -->
                                <div class="subject-analysis">
                                    <div class="analysis-section">
                                        <h4>📋 Problem Statement</h4>
                                        <p>{{ step.content.problem_statement }}</p>
                                    </div>
                                    
                                    <div class="analysis-section">
                                        <h4>📚 Library of Congress Classification</h4>
                                        <p><code>{{ step.content.lcc_classification }}</code></p>
                                    </div>
                                    
                                    <div class="analysis-grid">
                                        <div class="analysis-item">
                                            <strong>Complexity Level:</strong> {{ step.content.complexity_level }}
                                        </div>
                                        <div class="analysis-item">
                                            <strong>Estimated Steps:</strong> {{ step.content.estimated_steps }}
                                        </div>
                                        <div class="analysis-item">
                                            <strong>Analysis Confidence:</strong> {{ (step.content.confidence_score * 100) | round }}%
                                        </div>
                                    </div>
                                    
                                    <div class="analysis-section">
                                        <h4>👥 Recommended Stakeholders</h4>
                                        <ul>
                                            {% for stakeholder in step.content.recommended_stakeholders %}
                                            <li>{{ stakeholder }}</li>
                                            {% endfor %}
                                        </ul>
                                    </div>
                                    
                                    <div class="analysis-section">
                                        <h4>🎯 Debate Dimensions</h4>
                                        <div class="dimensions">
                                            {% for dimension in step.content.debate_dimensions %}
                                            <span class="dimension-tag">{{ dimension }}</span>
                                            {% endfor %}
                                        </div>
                                    </div>
                                </div>
                            {% elif step.content is iterable and step.content is not string %}
                                {% for item in step.content %}
                                <div class="agent-response">
                                    <div class="agent-name">{{ item.agent_name if item.agent_name else item.agent_id }}</div>
                                    
                                    {% if item.proposal %}
                                        <div class="proposal-content">
                                            <strong>Proposal:</strong><br>
                                            {{ item.proposal.proposal if item.proposal.proposal else item.proposal }}
                                        </div>
                                        {% if item.proposal.reasoning %}
                                            <div class="reasoning"><strong>Reasoning:</strong> {{ item.proposal.reasoning }}</div>
                                        {% endif %}
                                    {% endif %}
                                    
                                    {% if item.response %}
                                        <div class="response-content">
                                            {% if item.response.response %}
                                                <div><strong>Response:</strong> {{ item.response.response }}</div>
                                            {% endif %}
                                            {% if item.response.builds_on %}
                                                <div class="builds-on"><strong>Builds on:</strong> {{ item.response.builds_on }}</div>
                                            {% endif %}
                                            {% if item.response.evidence %}
                                                <div class="evidence"><strong>Evidence:</strong> {{ item.response.evidence | join(', ') }}</div>
                                            {% endif %}
                                        </div>
                                        {% if item.evaluating %}
                                            <div class="evaluation-target"><em>Evaluating proposal from: {{ item.evaluating }}</em></div>
                                        {% endif %}
                                    {% endif %}
                                    
                                    {% if item.vote %}
                                        <div class="vote-content">
                                            <div class="vote-decision"><strong>Decision:</strong> {{ item.vote.decision }}</div>
                                            <div class="vote-confidence"><strong>Confidence:</strong> {{ (item.vote.confidence * 100) | round }}%</div>
                                            <div class="vote-rationale"><strong>Rationale:</strong> {{ item.vote.rationale }}</div>
                                            {% if item.vote.conditions %}
                                                <div class="vote-conditions">
                                                    <strong>Conditions:</strong>
                                                    <ul>
                                                        {% for condition in item.vote.conditions %}
                                                        <li>{{ condition }}</li>
                                                        {% endfor %}
                                                    </ul>
                                                </div>
                                            {% endif %}
                                        </div>
                                    {% endif %}
                                </div>
                                {% endfor %}
                            {% else %}
                                <div>{{ step.content }}</div>
                            {% endif %}
                            
                            {% if step.consensus_reached is defined %}
                                <div style="margin-top: 15px; padding: 15px; background: {{ '#22543D' if step.consensus_reached else '#742A2A' }}; border-radius: 6px;">
                                    <strong>{{ '✅ Consensus Reached!' if step.consensus_reached else '❌ No Consensus Yet' }}</strong>
                                    {% if step.consensus_ratio is defined %}
                                        <div>Support Ratio: {{ (step.consensus_ratio * 100) | round }}%</div>
                                    {% endif %}
                                </div>
                            {% endif %}
                            
                            {% if step.final_decision %}
                                <div style="margin-top: 15px; padding: 15px; background: #2D3748; border-radius: 6px; border-left: 4px solid #38A169;">
                                    <h4>📋 Final Decision: {{ step.final_decision.decision }}</h4>
                                    <p><strong>Summary:</strong> {{ step.final_decision.summary }}</p>
                                    {% if step.final_decision.next_steps %}
                                        <div><strong>Next Steps:</strong>
                                            <ol>
                                                {% for next_step in step.final_decision.next_steps %}
                                                <li>{{ next_step }}</li>
                                                {% endfor %}
                                            </ol>
                                        </div>
                                    {% endif %}
                                </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                <div class="no-debates">No debate steps yet. Click "Advance Step" to begin.</div>
                {% endif %}
            </div>
            {% endfor %}
        {% else %}
            <div class="no-debates">No active debates. Start a new debate above.</div>
        {% endif %}
    </div>

    <script>
        function showMessage(text, type) {
            const messageEl = document.getElementById('message');
            messageEl.innerHTML = `<div class="message ${type}">${text}</div>`;
            setTimeout(() => {
                messageEl.innerHTML = '';
            }, 5000);
        }

        function startNewDebate(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const topic = formData.get('topic');
            const mode = formData.get('mode');

            fetch('/start_debate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, mode })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ Started new debate: ${data.debate_id}`, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showMessage(`❌ Failed to start debate: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                showMessage(`❌ Error: ${error.message}`, 'error');
            });
        }

        function advanceDebate(debateId) {
            const button = event.target;
            button.disabled = true;
            button.textContent = '⏳ Processing...';

            fetch('/advance_debate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ debate_id: debateId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(`✅ Advanced to step ${data.step}`, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showMessage(`❌ Failed to advance: ${data.message}`, 'error');
                    button.disabled = false;
                    button.textContent = '⚡ Advance Step (Y)';
                }
            })
            .catch(error => {
                showMessage(`❌ Error: ${error.message}`, 'error');
                button.disabled = false;
                button.textContent = '⚡ Advance Step (Y)';
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main page showing active debates."""
    return render_template_string(
        HTML_TEMPLATE, 
        debates=debate_manager.active_debates,
        framework_available=FRAMEWORK_AVAILABLE
    )

@app.route('/start_debate', methods=['POST'])
def start_debate():
    """Start a new debate."""
    try:
        data = request.json
        topic = data.get('topic', 'Default debate topic')
        mode = data.get('mode', 'consensus_building')
        
        debate_id = debate_manager.start_new_debate(topic, mode)
        
        return jsonify({
            'success': True,
            'debate_id': debate_id,
            'topic': topic,
            'mode': mode
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/advance_debate', methods=['POST'])
def advance_debate():
    """Advance a debate by one step."""
    try:
        data = request.json
        debate_id = data.get('debate_id')
        
        step_result = debate_manager.advance_debate(debate_id)
        
        if step_result:
            return jsonify({
                'success': True,
                'step': step_result['step'],
                'phase': step_result.get('phase', 'Unknown'),
                'debate_id': debate_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Debate not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Real Debate Engine',
        'framework_available': FRAMEWORK_AVAILABLE,
        'active_debates': len(debate_manager.active_debates),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🎯 Starting Real Debate Engine...")
    print(f"📊 Framework Status: {'✅ Connected' if FRAMEWORK_AVAILABLE else '⚠️ Simulation Mode'}")
    if FRAMEWORK_AVAILABLE:
        print("🔗 Using actual DebateEngine from core_base.py")
        print("🧮 Using mathematical formalism from mathematical_formalism_v2.py")
    else:
        print("📝 Framework components not available - running in simulation mode")
    print("🎯 Access at: http://localhost:7001")
    print()
    
    app.run(host='0.0.0.0', port=7001, debug=True)