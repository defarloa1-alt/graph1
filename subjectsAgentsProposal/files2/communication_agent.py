"""
CommunicationAgent - Meta-Facet Specialist

Analyzes the communication dimension of subjects across all domain facets.

Works collaboratively with domain agents (Military, Political, etc.) to understand
HOW information within those domains is transmitted, for what purpose, to whom,
and using what strategies.

Author: Chrystallum Project
Date: 2026-02-15
Version: 1.0.0
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommunicationDimension:
    """
    Represents the communication dimension of a subject
    """
    primacy: float  # 0-1 score: how central is communication to this subject?
    medium: List[str]  # oral, written, visual, performative, architectural
    purpose: List[str]  # propaganda, persuasion, legitimation, etc.
    audience: List[str]  # Senate, Roman people, military, etc.
    strategy: List[str]  # ethos, pathos, logos, invective, etc.
    
    def is_significant(self, threshold: float = 0.75) -> bool:
        """Check if communication dimension is significant enough for analysis"""
        return self.primacy >= threshold


class CommunicationAgent:
    """
    Meta-facet specialist agent for analyzing communication dimensions
    
    The CommunicationAgent doesn't compete with domain agents. Instead, it
    works alongside them to analyze HOW information is communicated within
    each domain.
    
    Example:
        Subject: "Punic Wars"
        Domain Agents: MilitaryAgent, PoliticalAgent
        Communication Agent: Analyzes HOW military/political info about wars
                            was communicated (propaganda, monuments, etc.)
    """
    
    def __init__(self, agent_id: str = "communication_agent"):
        """
        Initialize CommunicationAgent
        
        Args:
            agent_id: Unique identifier for this agent instance
        """
        self.agent_id = agent_id
        self.facet = "Communication"
        self.facet_type = "meta"  # Not a domain facet
        
        # Communication analysis thresholds
        self.primacy_threshold = 0.75  # Minimum primacy to assign this agent
        self.confidence_weights = {
            'lcc': 0.40,
            'keywords': 0.30,
            'patterns': 0.30
        }
    
    def should_analyze(self, subject: Dict) -> bool:
        """
        Determine if this subject warrants communication analysis
        
        Args:
            subject: Subject with communication dimension detected
        
        Returns:
            True if communication primacy >= threshold
        """
        comm = subject.get('communication', {})
        primacy = comm.get('primacy', 0.0)
        return primacy >= self.primacy_threshold
    
    def analyze_subject(self, subject: Dict) -> Optional[Dict]:
        """
        Analyze communication dimension of a subject
        
        This method performs deep analysis of HOW information about this
        subject was communicated in the Roman Republic.
        
        Args:
            subject: SubjectConcept with domain_facets and communication dimension
        
        Returns:
            Communication analysis or None if not applicable
        """
        
        # Check if communication analysis is warranted
        if not self.should_analyze(subject):
            return None
        
        comm = subject.get('communication', {})
        
        # Analyze each dimension
        medium_analysis = self._analyze_medium(comm.get('medium', []), subject)
        purpose_analysis = self._analyze_purpose(comm.get('purpose', []), subject)
        audience_analysis = self._analyze_audience(comm.get('audience', []), subject)
        strategy_analysis = self._analyze_strategy(comm.get('strategy', []), subject)
        
        # Generate insights
        insights = self._generate_insights(subject, comm)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(comm, subject)
        
        return {
            'agent_id': self.agent_id,
            'facet': self.facet,
            'facet_type': self.facet_type,
            'primacy': comm.get('primacy', 0.0),
            'dimensions': {
                'medium': medium_analysis,
                'purpose': purpose_analysis,
                'audience': audience_analysis,
                'strategy': strategy_analysis
            },
            'insights': insights,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _analyze_medium(self, media: List[str], subject: Dict) -> Dict:
        """
        Deep analysis of communication medium
        
        Args:
            media: List of detected media (oral, written, visual, etc.)
            subject: Full subject context
        
        Returns:
            Medium analysis with characteristics and implications
        """
        
        medium_catalog = {
            'oral': {
                'characteristics': [
                    'immediacy', 'emotional impact', 'ephemeral', 
                    'requires co-presence', 'allows interaction'
                ],
                'limitations': [
                    'no permanence without recording', 
                    'limited geographic reach',
                    'requires audience assembly'
                ],
                'roman_forms': [
                    'contiones (public assemblies)', 
                    'Senate speeches',
                    'law court orations',
                    'rumors (fama)',
                    'military exhortations'
                ],
                'effectiveness_factors': [
                    'oratorical skill',
                    'audience mood',
                    'timing and context',
                    'speaker reputation (auctoritas)'
                ]
            },
            
            'written': {
                'characteristics': [
                    'permanence', 'editability', 'portability',
                    'enables wide distribution', 'allows careful composition'
                ],
                'limitations': [
                    'literacy required',
                    'slower dissemination than oral',
                    'lacks emotional immediacy'
                ],
                'roman_forms': [
                    'letters (epistulae)',
                    'edicts (edicta)',
                    'commentarii (memoirs)',
                    'inscriptions (tituli)',
                    'acta diurna (daily gazette)',
                    'laws (leges)'
                ],
                'effectiveness_factors': [
                    'literacy rates',
                    'distribution networks',
                    'preservation and copying',
                    'textual authority'
                ]
            },
            
            'visual': {
                'characteristics': [
                    'crosses literacy barriers',
                    'monumental presence',
                    'wide public reach',
                    'symbolic power'
                ],
                'limitations': [
                    'static message',
                    'interpretation can vary',
                    'expensive to produce'
                ],
                'roman_forms': [
                    'coinage (nummi)',
                    'monuments (monumenta)',
                    'triumphal arches',
                    'statues (statuae)',
                    'relief sculptures',
                    'ancestor masks (imagines)'
                ],
                'effectiveness_factors': [
                    'visibility and placement',
                    'iconographic clarity',
                    'cultural literacy',
                    'repetition and ubiquity'
                ]
            },
            
            'performative': {
                'characteristics': [
                    'embodied experience',
                    'spectacle and awe',
                    'collective participation',
                    'ritualized meaning'
                ],
                'limitations': [
                    'ephemeral unless commemorated',
                    'limited to participants/witnesses',
                    'expensive to stage'
                ],
                'roman_forms': [
                    'triumphs (triumphi)',
                    'religious rituals (sacra)',
                    'gladiatorial games (munera)',
                    'theater performances',
                    'funeral processions',
                    'military parades'
                ],
                'effectiveness_factors': [
                    'scale and splendor',
                    'emotional engagement',
                    'cultural resonance',
                    'public accessibility'
                ]
            },
            
            'architectural': {
                'characteristics': [
                    'permanent presence',
                    'spatial control',
                    'functional and symbolic',
                    'shapes daily experience'
                ],
                'limitations': [
                    'very expensive',
                    'long construction time',
                    'message can be contested or reinterpreted'
                ],
                'roman_forms': [
                    'forums (fora)',
                    'temples (aedes)',
                    'basilicas',
                    'aqueducts',
                    'triumphal arches',
                    'public baths (thermae)'
                ],
                'effectiveness_factors': [
                    'scale and visibility',
                    'functional utility',
                    'symbolic associations',
                    'durability'
                ]
            }
        }
        
        analysis = {}
        for medium in media:
            if medium in medium_catalog:
                analysis[medium] = medium_catalog[medium]
        
        # Add multi-medium insights
        if len(media) > 1:
            analysis['multi_medium_strategy'] = {
                'description': f'Uses {len(media)} communication media for redundancy and broad reach',
                'advantages': [
                    'Reaches diverse audiences',
                    'Reinforces message through repetition',
                    'Compensates for limitations of each medium'
                ],
                'roman_context': 'Elite Romans typically used multiple media simultaneously (speeches + letters + monuments) for maximum effect'
            }
        
        return analysis
    
    def _analyze_purpose(self, purposes: List[str], subject: Dict) -> Dict:
        """
        Deep analysis of communication purpose
        
        Args:
            purposes: List of detected purposes
            subject: Full subject context
        
        Returns:
            Purpose analysis
        """
        
        purpose_catalog = {
            'propaganda': {
                'definition': 'Shape public opinion to legitimize power or policy',
                'techniques': [
                    'selective presentation of facts',
                    'emotional appeals',
                    'repetition and ubiquity',
                    'demonization of enemies',
                    'glorification of achievements'
                ],
                'roman_examples': [
                    "Caesar's Commentarii (glorifying Gallic conquest)",
                    "Augustan visual program (legitimizing principate)",
                    "Coin iconography (promoting imperial virtues)"
                ],
                'effectiveness_factors': [
                    'message clarity and consistency',
                    'audience receptivity',
                    'credibility of source',
                    'media saturation'
                ]
            },
            
            'persuasion': {
                'definition': 'Change beliefs or actions through rational/emotional argument',
                'techniques': [
                    'logical argumentation (logos)',
                    'ethical appeal (ethos)',
                    'emotional appeal (pathos)',
                    'use of precedent (exempla)',
                    'anticipating counterarguments'
                ],
                'roman_examples': [
                    "Cicero's judicial speeches (persuading juries)",
                    "Senate debates (convincing senators to vote)",
                    "Contio rhetoric (swaying public opinion)"
                ],
                'effectiveness_factors': [
                    'rhetorical skill',
                    'audience predisposition',
                    'strength of evidence',
                    'speaker authority (auctoritas)'
                ]
            },
            
            'incitement': {
                'definition': 'Provoke immediate action or mobilization',
                'techniques': [
                    'inflammatory language',
                    'appeals to fear or anger',
                    'calls to action',
                    'identification of enemies',
                    'invocation of crisis'
                ],
                'roman_examples': [
                    "Catiline's alleged conspiracy rhetoric",
                    "Clodius's contiones (mob mobilization)",
                    "Military exhortations before battle"
                ],
                'effectiveness_factors': [
                    'audience volatility',
                    'perceived urgency',
                    'charismatic delivery',
                    'social context and grievances'
                ]
            },
            
            'legitimation': {
                'definition': 'Justify authority, position, or actions',
                'techniques': [
                    'appeals to tradition (mos maiorum)',
                    'divine sanction',
                    'legal/constitutional justification',
                    'demonstration of virtus',
                    'genealogical claims'
                ],
                'roman_examples': [
                    "Triumph ceremonies (legitimating military authority)",
                    "Funeral orations (legitimating family status)",
                    "Consular edicts (asserting constitutional power)"
                ],
                'effectiveness_factors': [
                    'alignment with values',
                    'legal/religious grounding',
                    'precedent availability',
                    'opposition weakness'
                ]
            },
            
            'memory': {
                'definition': 'Preserve events and shape historical narrative',
                'techniques': [
                    'monumental construction',
                    'written commemoration',
                    'ritual reenactment',
                    'oral tradition',
                    'selective emphasis'
                ],
                'roman_examples': [
                    "Triumphal monuments (preserving military victories)",
                    "Funeral orations (shaping family memory)",
                    "Annalistic histories (recording yearly events)"
                ],
                'effectiveness_factors': [
                    'material durability',
                    'cultural transmission',
                    'political utility',
                    'absence of counter-narratives'
                ]
            }
        }
        
        analysis = {}
        for purpose in purposes:
            if purpose in purpose_catalog:
                analysis[purpose] = purpose_catalog[purpose]
        
        return analysis
    
    def _analyze_audience(self, audiences: List[str], subject: Dict) -> Dict:
        """
        Analyze intended audience and reception
        
        Args:
            audiences: List of detected audiences
            subject: Full subject context
        
        Returns:
            Audience analysis
        """
        
        audience_catalog = {
            'Senate': {
                'characteristics': [
                    'Elite (300-600 men)',
                    'Highly educated',
                    'Factional divisions',
                    'Decision-making power',
                    'Values precedent and dignitas'
                ],
                'communication_strategies': [
                    'Formal oratory with classical references',
                    'Appeals to tradition (mos maiorum)',
                    'Legal and constitutional arguments',
                    'Peer pressure and dignitas concerns',
                    'Private lobbying alongside public speeches'
                ],
                'roman_context': 'Senate debates were the primary arena for elite political competition'
            },
            
            'Roman people': {
                'characteristics': [
                    'Diverse social classes',
                    'Varying literacy levels',
                    'Vote in assemblies',
                    'Subject to popular appeals',
                    'Value practical benefits and spectacle'
                ],
                'communication_strategies': [
                    'Simplified messaging',
                    'Emotional appeals',
                    'Visual spectacle (triumphs, games)',
                    'Promises of material benefits',
                    'Populist rhetoric against elite'
                ],
                'roman_context': 'Popular assemblies (contiones) were non-deliberative - designed for persuasion, not debate'
            },
            
            'Military': {
                'characteristics': [
                    'Legionaries and veterans',
                    'Value honor (virtus) and loyalty',
                    'Expect material rewards',
                    'Susceptible to charismatic leadership',
                    'Form voting bloc in assemblies'
                ],
                'communication_strategies': [
                    'Appeals to shared hardship and glory',
                    'Promises of booty and land',
                    'Display of military virtus',
                    'Reminders of past victories',
                    'Personal relationship with commander'
                ],
                'roman_context': 'Military loyalty increasingly important in Late Republic - armies became personal to generals'
            },
            
            'Posterity': {
                'characteristics': [
                    'Future generations',
                    'Historical judgment',
                    'Memory and fame (gloria)',
                    'Cultural transmission'
                ],
                'communication_strategies': [
                    'Monumental construction',
                    'Written memoirs and histories',
                    'Inscriptions for permanence',
                    'Shaping narrative for favorable judgment',
                    'Investment in material durability'
                ],
                'roman_context': 'Roman elite obsessed with posthumous fame - immortality through memory'
            }
        }
        
        analysis = {}
        for audience in audiences:
            if audience in audience_catalog:
                analysis[audience] = audience_catalog[audience]
        
        # Multi-audience insights
        if len(audiences) > 1:
            analysis['multi_audience_challenge'] = {
                'description': f'Message must resonate with {len(audiences)} distinct audiences simultaneously',
                'tensions': self._identify_audience_tensions(audiences),
                'roman_solution': 'Elite Romans often crafted different messages for different audiences, or used ambiguous language allowing multiple interpretations'
            }
        
        return analysis
    
    def _identify_audience_tensions(self, audiences: List[str]) -> List[str]:
        """Identify potential tensions between different audiences"""
        
        tensions = []
        
        if 'Senate' in audiences and 'Roman people' in audiences:
            tensions.append(
                "Senate/People tension: Elite senators value precedent and dignitas; "
                "people value material benefits and emotional appeals. "
                "Balancing both requires careful rhetoric."
            )
        
        if 'Senate' in audiences and 'Military' in audiences:
            tensions.append(
                "Senate/Military tension: Senate suspicious of military commanders' power; "
                "soldiers loyal to generals over state. "
                "Commander must reassure Senate while maintaining troop loyalty."
            )
        
        return tensions
    
    def _analyze_strategy(self, strategies: List[str], subject: Dict) -> Dict:
        """
        Analyze rhetorical/communicative strategies
        
        Args:
            strategies: List of detected strategies
            subject: Full subject context
        
        Returns:
            Strategy analysis
        """
        
        strategy_catalog = {
            'ethos': {
                'definition': 'Appeal based on speaker credibility, character, authority',
                'techniques': [
                    'Demonstrating expertise or experience',
                    'Invoking social status (dignitas)',
                    'Citing past achievements',
                    'Displaying moral virtue',
                    'Associating with respected figures'
                ],
                'roman_context': 'Ethos was paramount - auctoritas (personal authority) often trumped legal/logical arguments',
                'effectiveness': 'Highly effective in hierarchical Roman society'
            },
            
            'pathos': {
                'definition': 'Appeal to emotions - fear, pity, anger, joy',
                'techniques': [
                    'Vivid description (enargeia)',
                    'Personal anecdotes',
                    'Appeals to shared values/identity',
                    'Invocation of threats or crises',
                    'Display of grief or joy'
                ],
                'roman_context': 'Romans valued emotional control (gravitas) but recognized power of well-timed emotional appeals',
                'effectiveness': 'Very effective in contiones and jury trials, less so in Senate'
            },
            
            'logos': {
                'definition': 'Rational argument based on logic, evidence, precedent',
                'techniques': [
                    'Citing laws and precedents',
                    'Logical deduction',
                    'Historical examples (exempla)',
                    'Statistical/quantitative evidence',
                    'Reductio ad absurdum'
                ],
                'roman_context': 'Logos especially valued in Senate; precedent (exempla) more persuasive than abstract logic',
                'effectiveness': 'Effective with educated elite, less so with popular audiences'
            },
            
            'invective': {
                'definition': 'Character assassination, mockery, vituperation',
                'techniques': [
                    'Sexual slander',
                    'Accusations of unmanly behavior',
                    'Attacks on family/ancestry',
                    'Questioning courage or loyalty',
                    'Ridicule and sarcasm'
                ],
                'roman_context': 'Invective central to Roman political rhetoric - attacking opponent dignitas',
                'effectiveness': 'Very effective in Roman shame culture; could destroy political careers'
            },
            
            'exemplarity': {
                'definition': 'Use of historical/ancestral examples as models',
                'techniques': [
                    'Citing exempla maiorum (ancestral examples)',
                    'Referencing historical parallels',
                    'Invoking mythological models',
                    'Family genealogy and achievements',
                    'Comparative reasoning'
                ],
                'roman_context': 'Romans obsessed with precedent - past validated present',
                'effectiveness': 'Highly persuasive; appealed to conservative values and tradition'
            },
            
            'spectacle': {
                'definition': 'Visual overwhelm, awe, sensory experience',
                'techniques': [
                    'Monumental scale',
                    'Rich visual display',
                    'Ceremonial processions',
                    'Crowd participation',
                    'Symbolic imagery'
                ],
                'roman_context': 'Spectacle fundamental to Roman power - triumphs, games, architecture',
                'effectiveness': 'Extremely effective; bypassed rational argument through sensory impact'
            }
        }
        
        analysis = {}
        for strategy in strategies:
            if strategy in strategy_catalog:
                analysis[strategy] = strategy_catalog[strategy]
        
        return analysis
    
    def _generate_insights(self, subject: Dict, comm: Dict) -> List[str]:
        """
        Generate communication-specific insights about the subject
        
        Args:
            subject: Full subject data
            comm: Communication dimension data
        
        Returns:
            List of analytical insights
        """
        
        insights = []
        
        media = comm.get('medium', [])
        purposes = comm.get('purpose', [])
        audiences = comm.get('audience', [])
        strategies = comm.get('strategy', [])
        primacy = comm.get('primacy', 0)
        
        # Primacy insights
        if primacy >= 0.9:
            insights.append(
                "Communication is central to this subject (primacy ≥ 0.9). "
                "The primary historical interest is HOW information was transmitted, "
                "not just WHAT was transmitted."
            )
        elif primacy >= 0.75:
            insights.append(
                "Communication dimension is significant (primacy ≥ 0.75). "
                "Understanding this subject requires analyzing its communicative strategies."
            )
        
        # Multi-medium insights
        if len(media) > 1:
            if 'written' in media and 'oral' in media:
                insights.append(
                    "Dual-medium strategy (written + oral) suggests comprehensive campaign. "
                    "Written form provides permanence and precision; "
                    "oral form provides immediacy and emotional impact. "
                    "Typical of elite Roman political communication."
                )
            
            if 'visual' in media and ('written' in media or 'oral' in media):
                insights.append(
                    "Visual medium combined with text/speech indicates effort to reach "
                    "both literate elite and broader public. Visual crosses literacy barriers."
                )
        
        # Purpose combinations
        if 'propaganda' in purposes and 'legitimation' in purposes:
            insights.append(
                "Combination of propaganda and legitimation suggests defensive posture. "
                "Not just promoting achievements, but justifying contested actions. "
                "Indicates political opposition or questionable legitimacy."
            )
        
        if 'persuasion' in purposes and 'incitement' in purposes:
            insights.append(
                "Dual purpose of persuasion + incitement suggests urgent mobilization. "
                "Not just changing minds but provoking immediate action. "
                "Typical of crisis rhetoric or factional conflict."
            )
        
        # Audience tensions
        if 'Senate' in audiences and 'Roman people' in audiences:
            insights.append(
                "Dual audience (Senate + people) requires rhetorical balancing act. "
                "Senate values dignitas and precedent; people value material benefits. "
                "Message must work on multiple levels - characteristic of Late Republican politics."
            )
        
        # Strategy combinations
        if 'ethos' in strategies and 'spectacle' in strategies:
            insights.append(
                "Ethos + spectacle combination leverages both personal authority and visual power. "
                "Roman elite strategy: establish credibility, then overwhelm with display. "
                "Examples: triumph ceremony, where military virtus validated by spectacle."
            )
        
        # Domain-specific insights
        domain_facets = subject.get('domain_facets', [])
        
        if 'Military' in domain_facets and primacy >= 0.75:
            insights.append(
                "High communication primacy for military subject suggests this is about "
                "representation of war, not just war itself. Examples: triumph propaganda, "
                "battle narratives, military memoirs. Communication of military glory was "
                "often more important than the military events themselves."
            )
        
        if 'Political' in domain_facets and 'contio' in subject.get('label', '').lower():
            insights.append(
                "Contio (public assembly) was non-deliberative - designed for persuasion, not debate. "
                "Speakers aimed to sway voters before formal assembly vote. "
                "Rhetoric was more emotional and populist than Senate speeches."
            )
        
        return insights
    
    def _calculate_confidence(self, comm: Dict, subject: Dict) -> float:
        """
        Calculate confidence in communication analysis
        
        Args:
            comm: Communication dimension data
            subject: Full subject data
        
        Returns:
            Confidence score (0-1)
        """
        
        confidence = 0.0
        
        # Base confidence from primacy
        confidence += comm.get('primacy', 0) * 0.50
        
        # Boost for detected dimensions
        if comm.get('medium'):
            confidence += 0.15
        if comm.get('purpose'):
            confidence += 0.15
        if comm.get('audience'):
            confidence += 0.10
        if comm.get('strategy'):
            confidence += 0.10
        
        # Normalize to 0-1
        return min(confidence, 1.0)
    
    def generate_claims(self, subject: Dict, analysis: Dict) -> List[Dict]:
        """
        Generate claims based on communication analysis
        
        Args:
            subject: Subject data
            analysis: Communication analysis output
        
        Returns:
            List of claim objects
        """
        
        claims = []
        
        # Generate claims from insights
        for insight in analysis.get('insights', []):
            claim = {
                'text': insight,
                'domain_facets': subject.get('domain_facets', []),
                'communication_dimension': True,
                'communication_primacy': analysis.get('primacy', 0),
                'confidence': analysis.get('confidence', 0),
                'agent_id': self.agent_id,
                'facet': 'Communication',
                'evidence': [subject.get('label', 'Unknown subject')],
                'timestamp': datetime.utcnow().isoformat()
            }
            claims.append(claim)
        
        return claims


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    
    # Example subject with communication dimension
    subject = {
        'subject_id': 'fast:fst01234567',
        'label': "Caesar's Gallic War commentaries",
        'lcc': 'DG62',
        'domain_facets': ['Military', 'Political', 'Literary'],
        'communication': {
            'has_dimension': True,
            'primacy': 0.90,
            'medium': ['written'],
            'purpose': ['propaganda', 'legitimation'],
            'audience': ['Senate', 'Roman people'],
            'strategy': ['objectivity pose', 'exemplarity']
        }
    }
    
    # Initialize agent
    agent = CommunicationAgent()
    
    # Check if analysis warranted
    print(f"Should analyze? {agent.should_analyze(subject)}")
    print(f"  Primacy: {subject['communication']['primacy']}")
    print(f"  Threshold: {agent.primacy_threshold}")
    
    # Analyze subject
    analysis = agent.analyze_subject(subject)
    
    if analysis:
        print(f"\n{'='*60}")
        print(f"COMMUNICATION ANALYSIS")
        print(f"{'='*60}")
        print(f"Subject: {subject['label']}")
        print(f"Domain Facets: {', '.join(subject['domain_facets'])}")
        print(f"Communication Primacy: {analysis['primacy']}")
        print(f"Confidence: {analysis['confidence']:.2f}")
        
        print(f"\n{'='*60}")
        print(f"DIMENSIONS")
        print(f"{'='*60}")
        
        # Medium
        print(f"\nMEDIUM:")
        for medium, details in analysis['dimensions']['medium'].items():
            if medium != 'multi_medium_strategy':
                print(f"  {medium.upper()}:")
                print(f"    Roman forms: {', '.join(details['roman_forms'][:3])}")
        
        # Purpose
        print(f"\nPURPOSE:")
        for purpose, details in analysis['dimensions']['purpose'].items():
            print(f"  {purpose.upper()}: {details['definition']}")
        
        # Insights
        print(f"\n{'='*60}")
        print(f"INSIGHTS")
        print(f"{'='*60}")
        for i, insight in enumerate(analysis['insights'], 1):
            print(f"\n{i}. {insight}")
        
        # Generate claims
        claims = agent.generate_claims(subject, analysis)
        print(f"\n{'='*60}")
        print(f"GENERATED CLAIMS: {len(claims)}")
        print(f"{'='*60}")
