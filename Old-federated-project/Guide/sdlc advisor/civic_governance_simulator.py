"""
Implementation Addendum: From Theory to Practice
Governance Simulation and Pedagogical Engine Extensions

This module demonstrates the practical translation of the federated graph framework
from abstract mathematical formulation to executable governance simulation.
"""

import time
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from universal_spatial_graph import *


class GovernancePressureType(Enum):
    """Types of governance pressures that can be encoded in edges"""
    REGULATORY = "regulatory"
    CIVIC = "civic" 
    ECONOMIC = "economic"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    TECHNICAL = "technical"


@dataclass
class GovernancePressure:
    """Governance pressure vector for edge weighting"""
    pressure_type: GovernancePressureType
    intensity: float  # 0.0 to 1.0
    source_stakeholder: str
    target_outcome: str
    temporal_urgency: float  # 0.0 to 1.0
    
    def calculate_influence_weight(self) -> float:
        """Calculate governance influence on graph dynamics"""
        return (self.intensity * 0.4) + (self.temporal_urgency * 0.6)


@dataclass 
class MismatchEvent:
    """Detected mismatch between agents for pedagogical simulation"""
    mismatch_type: str
    agent_a: str
    agent_b: str 
    context: str
    severity: float = 0.5
    timestamp: float = field(default_factory=time.time)
    resolution_options: List[str] = field(default_factory=list)


@dataclass
class ResolutionPath:
    """Possible resolution pathway for governance conflicts"""
    path_id: str
    steps: List[str]
    stakeholders_involved: List[str]
    estimated_duration: float
    success_probability: float
    civic_impact_score: float


class EnrichedGovernanceEdge(RichGraphEdge):
    """Enhanced edge with governance pressure encoding"""
    
    def __init__(self, id: str, source_id: str, target_id: str, edge_type: EdgeType,
                 label: str, properties: Dict[str, Any] = None, **kwargs):
        super().__init__(id, source_id, target_id, edge_type, label, properties, **kwargs)
        self.governance_pressures: List[GovernancePressure] = []
        self.civic_weight: float = 1.0
        
    def add_governance_pressure(self, pressure: GovernancePressure):
        """Add governance pressure that affects edge dynamics"""
        self.governance_pressures.append(pressure)
        self._recalculate_civic_weight()
    
    def _recalculate_civic_weight(self):
        """Update edge weight based on accumulated governance pressures"""
        if not self.governance_pressures:
            self.civic_weight = 1.0
            return
            
        total_influence = sum(p.calculate_influence_weight() for p in self.governance_pressures)
        self.civic_weight = min(total_influence / len(self.governance_pressures), 2.0)
    
    def get_dominant_pressure(self) -> Optional[GovernancePressure]:
        """Get the governance pressure with highest influence"""
        if not self.governance_pressures:
            return None
        return max(self.governance_pressures, key=lambda p: p.calculate_influence_weight())


class MismatchDetectionEngine:
    """Detects and analyzes agent conflicts for educational simulation"""
    
    def __init__(self):
        self.detection_rules = {
            'role_conflict': self._detect_role_conflict,
            'authority_dispute': self._detect_authority_dispute,
            'resource_competition': self._detect_resource_competition,
            'policy_disagreement': self._detect_policy_disagreement
        }
    
    def detect_agent_mismatches(self, agents: List[SpatialGraphNode], 
                               context: str) -> List[MismatchEvent]:
        """Detect potential conflicts between agents in given context"""
        mismatches = []
        
        for i, agent_a in enumerate(agents):
            for agent_b in agents[i+1:]:
                for rule_name, detection_func in self.detection_rules.items():
                    if detection_func(agent_a, agent_b, context):
                        mismatch = MismatchEvent(
                            mismatch_type=rule_name,
                            agent_a=agent_a.id,
                            agent_b=agent_b.id,
                            context=context,
                            severity=self._calculate_severity(agent_a, agent_b, rule_name),
                            resolution_options=self._generate_resolution_options(rule_name)
                        )
                        mismatches.append(mismatch)
        
        return mismatches
    
    def _detect_role_conflict(self, agent_a: SpatialGraphNode, 
                             agent_b: SpatialGraphNode, context: str) -> bool:
        """Check if agents have conflicting roles in context"""
        role_a = agent_a.properties.get('governance_role', 'citizen')
        role_b = agent_b.properties.get('governance_role', 'citizen')
        
        # Define conflicting role pairs
        conflicts = {
            ('developer', 'environmental_advocate'),
            ('city_planner', 'business_owner'),
            ('regulator', 'industry_representative')
        }
        
        return (role_a, role_b) in conflicts or (role_b, role_a) in conflicts
    
    def _detect_authority_dispute(self, agent_a: SpatialGraphNode,
                                 agent_b: SpatialGraphNode, context: str) -> bool:
        """Check for overlapping authority domains"""
        authority_a = set(agent_a.properties.get('authority_domains', []))
        authority_b = set(agent_b.properties.get('authority_domains', []))
        
        # Authority overlap indicates potential dispute
        return len(authority_a.intersection(authority_b)) > 0
    
    def _detect_resource_competition(self, agent_a: SpatialGraphNode,
                                   agent_b: SpatialGraphNode, context: str) -> bool:
        """Check if agents compete for same resources"""
        resources_a = set(agent_a.properties.get('required_resources', []))
        resources_b = set(agent_b.properties.get('required_resources', []))
        
        # Resource overlap with limited availability
        overlap = resources_a.intersection(resources_b)
        limited_resources = {'funding', 'land_use', 'permits', 'staff_time'}
        
        return len(overlap.intersection(limited_resources)) > 0
    
    def _detect_policy_disagreement(self, agent_a: SpatialGraphNode,
                                   agent_b: SpatialGraphNode, context: str) -> bool:
        """Check for fundamental policy disagreements"""
        policy_a = agent_a.properties.get('policy_position', {})
        policy_b = agent_b.properties.get('policy_position', {})
        
        # Check for opposing positions on key issues
        for issue in policy_a.keys():
            if issue in policy_b and policy_a[issue] != policy_b[issue]:
                return True
        return False
    
    def _calculate_severity(self, agent_a: SpatialGraphNode, 
                          agent_b: SpatialGraphNode, mismatch_type: str) -> float:
        """Calculate conflict severity based on agent influence and mismatch type"""
        influence_a = agent_a.properties.get('influence_level', 0.5)
        influence_b = agent_b.properties.get('influence_level', 0.5)
        
        severity_multipliers = {
            'role_conflict': 0.7,
            'authority_dispute': 0.9,
            'resource_competition': 0.6,
            'policy_disagreement': 0.8
        }
        
        base_severity = (influence_a + influence_b) / 2
        return min(base_severity * severity_multipliers.get(mismatch_type, 0.5), 1.0)
    
    def _generate_resolution_options(self, mismatch_type: str) -> List[str]:
        """Generate possible resolution pathways for mismatch type"""
        resolution_templates = {
            'role_conflict': [
                'Mediated stakeholder dialogue',
                'Role boundary clarification',
                'Joint working group formation',
                'Third-party arbitration'
            ],
            'authority_dispute': [
                'Authority mapping workshop',
                'Jurisdictional agreement',
                'Escalation to higher authority',
                'Collaborative governance model'
            ],
            'resource_competition': [
                'Resource sharing agreement',
                'Alternative resource identification',
                'Phased resource allocation',
                'Joint resource procurement'
            ],
            'policy_disagreement': [
                'Policy alignment workshop',
                'Compromise position development',
                'Pilot program testing',
                'Stakeholder impact assessment'
            ]
        }
        
        return resolution_templates.get(mismatch_type, ['Generic mediation process'])


class GovernanceNarrator:
    """Translates complex graph operations into civic-accessible narratives"""
    
    def __init__(self):
        self.civic_vocabulary = {
            'node_creation': 'new stakeholder joins',
            'edge_creation': 'relationship established',
            'node_modification': 'stakeholder role changes',
            'edge_modification': 'relationship strengthens/weakens',
            'consensus_formation': 'agreement reached',
            'debate_resolution': 'conflict resolved'
        }
    
    def narrate_governance_update(self, before_graph: UniversalGraphEngine,
                                 after_graph: UniversalGraphEngine,
                                 update_events: List[Dict[str, Any]]) -> str:
        """Create accessible narrative of governance changes"""
        narrative_parts = []
        
        # Analyze structural changes
        nodes_added = len(after_graph.nodes) - len(before_graph.nodes)
        edges_added = len(after_graph.edges) - len(before_graph.edges)
        
        if nodes_added > 0:
            narrative_parts.append(f"{nodes_added} new stakeholders joined the governance process")
        
        if edges_added > 0:
            narrative_parts.append(f"{edges_added} new relationships were established")
        
        # Analyze specific update events
        for event in update_events:
            civic_description = self._translate_technical_event(event)
            if civic_description:
                narrative_parts.append(civic_description)
        
        return ". ".join(narrative_parts) + "."
    
    def explain_mismatch_resolution(self, mismatch: MismatchEvent, 
                                   resolution: ResolutionPath) -> str:
        """Explain conflict resolution in civic terms"""
        stakeholder_a = self._get_stakeholder_description(mismatch.agent_a)
        stakeholder_b = self._get_stakeholder_description(mismatch.agent_b)
        
        resolution_explanation = (
            f"A {mismatch.mismatch_type.replace('_', ' ')} between {stakeholder_a} "
            f"and {stakeholder_b} was resolved through {len(resolution.steps)} steps: "
            f"{', '.join(resolution.steps[:2])}{'...' if len(resolution.steps) > 2 else ''}. "
            f"This process involved {len(resolution.stakeholders_involved)} stakeholders "
            f"and is expected to have a {resolution.civic_impact_score:.1f}/10 positive impact "
            f"on community governance."
        )
        
        return resolution_explanation
    
    def _translate_technical_event(self, event: Dict[str, Any]) -> str:
        """Convert technical graph events to civic language"""
        event_type = event.get('type', 'unknown')
        
        if event_type == 'agent_debate_resolution':
            return f"Community discussion on {event.get('topic', 'governance issue')} reached consensus"
        elif event_type == 'framework_overlay_change':
            return f"Governance perspective shifted to emphasize {event.get('new_focus', 'different priorities')}"
        elif event_type == 'spatial_relationship_added':
            return f"Geographic connection established between {event.get('locations', 'community areas')}"
        
        return None
    
    def _get_stakeholder_description(self, agent_id: str) -> str:
        """Get human-readable stakeholder description"""
        # This would typically look up agent details from the graph
        return f"stakeholder {agent_id}"


class CivicGovernanceSimulator:
    """Educational framework for governance simulation and civic literacy"""
    
    def __init__(self, base_framework: UniversalGraphEngine):
        self.framework = base_framework
        self.mismatch_detector = MismatchDetectionEngine()
        self.narrator = GovernanceNarrator()
        self.simulation_scenarios = {}
        
    def create_civic_scenario(self, scenario_name: str, 
                             complexity_level: str = "intermediate") -> Dict[str, Any]:
        """Create educational governance scenario"""
        
        # Define scenario complexity parameters
        complexity_params = {
            "beginner": {"agents": 3, "issues": 1, "time_pressure": 0.3},
            "intermediate": {"agents": 5, "issues": 2, "time_pressure": 0.6},
            "advanced": {"agents": 8, "issues": 3, "time_pressure": 0.9}
        }
        
        params = complexity_params.get(complexity_level, complexity_params["intermediate"])
        
        # Create scenario agents with diverse roles
        agents = self._create_scenario_agents(params["agents"])
        
        # Generate governance issues
        issues = self._generate_governance_issues(params["issues"])
        
        # Inject potential conflicts
        mismatches = self.mismatch_detector.detect_agent_mismatches(agents, scenario_name)
        
        scenario = {
            'name': scenario_name,
            'complexity': complexity_level,
            'agents': agents,
            'issues': issues,
            'potential_conflicts': mismatches,
            'time_pressure': params["time_pressure"],
            'learning_objectives': self._generate_learning_objectives(complexity_level),
            'success_criteria': self._define_success_criteria(complexity_level)
        }
        
        self.simulation_scenarios[scenario_name] = scenario
        return scenario
    
    def simulate_student_intervention(self, scenario_name: str,
                                    student_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process student governance decisions and provide feedback"""
        scenario = self.simulation_scenarios.get(scenario_name)
        if not scenario:
            return {"error": "Scenario not found"}
        
        results = []
        
        for action in student_actions:
            # Simulate action impact on framework
            action_result = self._process_governance_action(action, scenario)
            
            # Generate educational feedback
            feedback = self._generate_pedagogical_feedback(action, action_result, scenario)
            
            results.append({
                'action': action,
                'result': action_result,
                'feedback': feedback,
                'narrative': self.narrator.narrate_governance_update(
                    scenario['framework_state'], 
                    action_result['new_framework_state'],
                    [action_result]
                )
            })
        
        return {
            'scenario': scenario_name,
            'student_performance': self._assess_student_performance(results),
            'action_results': results,
            'next_steps': self._suggest_next_steps(results, scenario)
        }
    
    def _create_scenario_agents(self, num_agents: int) -> List[SpatialGraphNode]:
        """Create diverse stakeholder agents for scenario"""
        agent_templates = [
            {"role": "mayor", "influence": 0.8, "authorities": ["policy", "budget"]},
            {"role": "business_owner", "influence": 0.6, "authorities": ["economic"]},
            {"role": "environmental_advocate", "influence": 0.4, "authorities": ["environmental"]},
            {"role": "community_leader", "influence": 0.5, "authorities": ["social"]},
            {"role": "city_planner", "influence": 0.7, "authorities": ["zoning", "development"]},
            {"role": "resident_representative", "influence": 0.3, "authorities": ["community"]},
            {"role": "regulator", "influence": 0.9, "authorities": ["compliance", "permits"]},
            {"role": "developer", "influence": 0.6, "authorities": ["construction", "investment"]}
        ]
        
        agents = []
        for i in range(min(num_agents, len(agent_templates))):
            template = agent_templates[i]
            agent = SpatialGraphNode(
                f"agent_{i}_{template['role']}",
                NodeType.AGENT,
                f"{template['role'].replace('_', ' ').title()}"
            )
            agent.properties.update({
                'governance_role': template['role'],
                'influence_level': template['influence'],
                'authority_domains': template['authorities'],
                'scenario_agent': True
            })
            agents.append(agent)
        
        return agents
    
    def _generate_governance_issues(self, num_issues: int) -> List[Dict[str, Any]]:
        """Generate governance challenges for scenario"""
        issue_templates = [
            {
                'type': 'development_proposal',
                'title': 'New Shopping Center Development',
                'stakeholders': ['developer', 'environmental_advocate', 'city_planner'],
                'resources_required': ['land_use', 'permits', 'funding'],
                'complexity': 0.7
            },
            {
                'type': 'budget_allocation',
                'title': 'Public Transportation Funding',
                'stakeholders': ['mayor', 'resident_representative', 'business_owner'],
                'resources_required': ['funding', 'political_support'],
                'complexity': 0.6
            },
            {
                'type': 'regulatory_change',
                'title': 'Environmental Protection Standards',
                'stakeholders': ['regulator', 'business_owner', 'environmental_advocate'],
                'resources_required': ['regulatory_authority', 'compliance_resources'],
                'complexity': 0.8
            }
        ]
        
        return issue_templates[:num_issues]
    
    def _generate_learning_objectives(self, complexity_level: str) -> List[str]:
        """Define educational goals based on complexity"""
        objectives_by_level = {
            "beginner": [
                "Identify key stakeholders in governance scenario",
                "Understand basic conflict resolution strategies",
                "Recognize impact of governance decisions on community"
            ],
            "intermediate": [
                "Analyze multi-stakeholder conflicts and dependencies",
                "Design collaborative governance solutions",
                "Evaluate trade-offs in policy decisions",
                "Understand role of process in democratic outcomes"
            ],
            "advanced": [
                "Navigate complex multi-issue governance scenarios",
                "Design institutional mechanisms for conflict resolution",
                "Optimize governance processes for efficiency and legitimacy",
                "Analyze systemic governance challenges and reforms"
            ]
        }
        
        return objectives_by_level.get(complexity_level, objectives_by_level["intermediate"])
    
    def _define_success_criteria(self, complexity_level: str) -> Dict[str, Any]:
        """Define measurable success metrics"""
        criteria_by_level = {
            "beginner": {
                "stakeholder_engagement": 0.6,
                "conflict_resolution": 0.5,
                "process_efficiency": 0.4
            },
            "intermediate": {
                "stakeholder_engagement": 0.7,
                "conflict_resolution": 0.6,
                "process_efficiency": 0.6,
                "outcome_quality": 0.5
            },
            "advanced": {
                "stakeholder_engagement": 0.8,
                "conflict_resolution": 0.7,
                "process_efficiency": 0.7,
                "outcome_quality": 0.6,
                "systemic_improvement": 0.5
            }
        }
        
        return criteria_by_level.get(complexity_level, criteria_by_level["intermediate"])
    
    def _process_governance_action(self, action: Dict[str, Any], 
                                  scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate impact of student governance decision"""
        # This would integrate with the actual framework update mechanism
        # For now, return a simulated result
        
        action_type = action.get('type', 'unknown')
        effectiveness = self._calculate_action_effectiveness(action, scenario)
        
        return {
            'action_type': action_type,
            'effectiveness': effectiveness,
            'stakeholder_reactions': self._simulate_stakeholder_reactions(action, scenario),
            'system_changes': self._simulate_system_changes(action, scenario),
            'new_framework_state': scenario.get('framework_state', {})  # Would be actual updated state
        }
    
    def _calculate_action_effectiveness(self, action: Dict[str, Any],
                                      scenario: Dict[str, Any]) -> float:
        """Calculate how effective the student's action was"""
        # Simplified effectiveness calculation
        base_effectiveness = 0.5
        
        # Bonus for stakeholder consideration
        if action.get('stakeholders_consulted', 0) > 2:
            base_effectiveness += 0.2
        
        # Bonus for process consideration
        if action.get('process_designed', False):
            base_effectiveness += 0.2
        
        # Penalty for ignoring conflicts
        unaddressed_conflicts = len(scenario.get('potential_conflicts', [])) - action.get('conflicts_addressed', 0)
        base_effectiveness -= unaddressed_conflicts * 0.1
        
        return max(0.0, min(1.0, base_effectiveness))
    
    def _simulate_stakeholder_reactions(self, action: Dict[str, Any],
                                      scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate how different stakeholders react to action"""
        reactions = {}
        
        for agent in scenario.get('agents', []):
            role = agent.properties.get('governance_role', 'citizen')
            
            # Simplified reaction based on action alignment with agent interests
            if role in action.get('favored_roles', []):
                reactions[role] = 'positive'
            elif role in action.get('opposed_roles', []):
                reactions[role] = 'negative'
            else:
                reactions[role] = 'neutral'
        
        return reactions
    
    def _simulate_system_changes(self, action: Dict[str, Any],
                                scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate systemic changes from governance action"""
        return {
            'new_relationships': action.get('relationships_created', 0),
            'resolved_conflicts': action.get('conflicts_resolved', 0),
            'process_improvements': action.get('process_changes', []),
            'resource_efficiency': action.get('resource_optimization', 0.0)
        }
    
    def _generate_pedagogical_feedback(self, action: Dict[str, Any],
                                      result: Dict[str, Any],
                                      scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate educational feedback for student action"""
        feedback = {
            'strengths': [],
            'areas_for_improvement': [],
            'concept_reinforcement': [],
            'next_learning_steps': []
        }
        
        effectiveness = result.get('effectiveness', 0.5)
        
        # Provide targeted feedback based on performance
        if effectiveness > 0.7:
            feedback['strengths'].append("Demonstrated strong stakeholder engagement")
            feedback['concept_reinforcement'].append("Collaborative governance principles")
        elif effectiveness < 0.4:
            feedback['areas_for_improvement'].append("Consider more comprehensive stakeholder analysis")
            feedback['next_learning_steps'].append("Review stakeholder mapping techniques")
        
        # Specific feedback on conflict resolution
        conflicts_in_scenario = len(scenario.get('potential_conflicts', []))
        conflicts_addressed = action.get('conflicts_addressed', 0)
        
        if conflicts_addressed >= conflicts_in_scenario:
            feedback['strengths'].append("Proactively addressed all identified conflicts")
        elif conflicts_addressed == 0:
            feedback['areas_for_improvement'].append("Conflict identification and resolution")
            feedback['next_learning_steps'].append("Study conflict analysis frameworks")
        
        return feedback
    
    def _assess_student_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall student performance in scenario"""
        total_effectiveness = sum(r['result']['effectiveness'] for r in results)
        avg_effectiveness = total_effectiveness / len(results) if results else 0
        
        performance_level = "novice"
        if avg_effectiveness > 0.7:
            performance_level = "proficient"
        elif avg_effectiveness > 0.5:
            performance_level = "developing"
        
        return {
            'overall_effectiveness': avg_effectiveness,
            'performance_level': performance_level,
            'actions_taken': len(results),
            'governance_competencies_demonstrated': self._identify_competencies(results)
        }
    
    def _suggest_next_steps(self, results: List[Dict[str, Any]], 
                           scenario: Dict[str, Any]) -> List[str]:
        """Suggest next learning activities based on performance"""
        suggestions = []
        
        avg_effectiveness = sum(r['result']['effectiveness'] for r in results) / len(results)
        
        if avg_effectiveness < 0.5:
            suggestions.append("Practice stakeholder identification exercises")
            suggestions.append("Review democratic governance principles")
        elif avg_effectiveness < 0.7:
            suggestions.append("Explore advanced conflict resolution techniques")
            suggestions.append("Study collaborative governance case studies")
        else:
            suggestions.append("Try more complex multi-issue scenarios")
            suggestions.append("Design governance process improvements")
        
        return suggestions
    
    def _identify_competencies(self, results: List[Dict[str, Any]]) -> List[str]:
        """Identify governance competencies demonstrated by student"""
        competencies = []
        
        for result in results:
            action = result['action']
            effectiveness = result['result']['effectiveness']
            
            if effectiveness > 0.6:
                if action.get('stakeholders_consulted', 0) > 2:
                    competencies.append("stakeholder_engagement")
                if action.get('conflicts_addressed', 0) > 0:
                    competencies.append("conflict_resolution")
                if action.get('process_designed', False):
                    competencies.append("process_design")
        
        return list(set(competencies))


def create_civic_governance_demo():
    """Demonstrate the civic governance simulation capabilities"""
    print("=== Civic Governance Simulation Demo ===\n")
    
    # Create base framework
    base_framework = UniversalGraphEngine()
    
    # Create civic simulator
    simulator = CivicGovernanceSimulator(base_framework)
    
    # Create educational scenario
    scenario = simulator.create_civic_scenario(
        "downtown_development_project", 
        complexity_level="intermediate"
    )
    
    print(f"Created scenario: {scenario['name']}")
    print(f"Complexity: {scenario['complexity']}")
    print(f"Agents: {len(scenario['agents'])}")
    print(f"Issues: {len(scenario['issues'])}")
    print(f"Potential conflicts: {len(scenario['potential_conflicts'])}")
    
    # Show potential conflicts
    print(f"\n=== Potential Governance Conflicts ===")
    for mismatch in scenario['potential_conflicts']:
        print(f"  - {mismatch.mismatch_type} between {mismatch.agent_a} and {mismatch.agent_b}")
        print(f"    Severity: {mismatch.severity:.2f}")
        print(f"    Resolution options: {', '.join(mismatch.resolution_options[:2])}")
    
    # Simulate student actions
    print(f"\n=== Student Action Simulation ===")
    student_actions = [
        {
            'type': 'stakeholder_consultation',
            'stakeholders_consulted': 3,
            'conflicts_addressed': 1,
            'process_designed': True,
            'description': 'Organized multi-stakeholder workshop to discuss development concerns'
        },
        {
            'type': 'mediation_session',
            'stakeholders_consulted': 2,
            'conflicts_addressed': 2,
            'process_designed': False,
            'description': 'Facilitated direct negotiation between conflicting parties'
        }
    ]
    
    # Process student interventions
    results = simulator.simulate_student_intervention(scenario['name'], student_actions)
    
    print(f"Student performance level: {results['student_performance']['performance_level']}")
    print(f"Overall effectiveness: {results['student_performance']['overall_effectiveness']:.2f}")
    print(f"Competencies demonstrated: {', '.join(results['student_performance']['governance_competencies_demonstrated'])}")
    
    # Show action results
    for i, action_result in enumerate(results['action_results']):
        print(f"\n--- Action {i+1} Results ---")
        print(f"Action: {action_result['action']['description']}")
        print(f"Effectiveness: {action_result['result']['effectiveness']:.2f}")
        print(f"Narrative: {action_result['narrative']}")
        
        feedback = action_result['feedback']
        if feedback['strengths']:
            print(f"Strengths: {', '.join(feedback['strengths'])}")
        if feedback['areas_for_improvement']:
            print(f"Areas for improvement: {', '.join(feedback['areas_for_improvement'])}")
    
    print(f"\n=== Recommended Next Steps ===")
    for step in results['next_steps']:
        print(f"  - {step}")
    
    print(f"\n=== Governance Simulation Complete ===")


if __name__ == "__main__":
    create_civic_governance_demo()