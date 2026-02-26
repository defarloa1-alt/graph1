#!/usr/bin/env python3
"""
Load Roman Republic SubjectConcept Ontology to Neo4j Aura

Creates 94 SubjectConcept nodes with PART_OF hierarchy based on
the approved SCA ontology proposal.
"""
from neo4j import GraphDatabase

# Aura connection
URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"
DATABASE = "neo4j"

# Roman Republic Ontology Structure (importable without side effects)
ONTOLOGY = {
    # Root
    'subj_roman_republic_q17167': {
        'label': 'Roman Republic',
        'qid': 'Q17167',
        'primary_facet': 'POLITICAL',
        'parent': None,
        'level': 0
    },
    
    # Level 1: Major Branches
    'subj_rr_governance': {
        'label': 'Government and Constitutional Structure',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    'subj_rr_military': {
        'label': 'Warfare and Military Systems',
        'primary_facet': 'MILITARY',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    'subj_rr_society': {
        'label': 'Society and Social Structure',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    'subj_rr_economy': {
        'label': 'Economy and Resource Systems',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    'subj_rr_geography': {
        'label': 'Geography, Provinces, and Expansion',
        'primary_facet': 'GEOGRAPHIC',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    'subj_rr_diplomacy': {
        'label': 'Diplomacy and International Relations',
        'primary_facet': 'DIPLOMATIC',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    'subj_rr_religion': {
        'label': 'Religion and Public Cult',
        'primary_facet': 'RELIGIOUS',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    'subj_rr_culture_ideas': {
        'label': 'Culture, Ideas, and Communication',
        'primary_facet': 'CULTURAL',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    'subj_rr_periodization': {
        'label': 'Chronology and Periodization',
        'primary_facet': 'TEMPORAL',
        'parent': 'subj_roman_republic_q17167',
        'level': 1
    },
    
    # Level 2: Governance subdivisions
    'subj_rr_gov_institutions': {
        'label': 'Institutions: Senate, Assemblies, Magistracies',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_governance',
        'level': 2
    },
    'subj_rr_gov_offices': {
        'label': 'Offices and Magistracies (Cursus Honorum)',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_governance',
        'level': 2
    },
    'subj_rr_gov_law': {
        'label': 'Law, Citizenship, and Constitutional Practice',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_governance',
        'level': 2
    },
    'subj_rr_gov_factions': {
        'label': 'Factions, Patronage Power, and Civil Conflict',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_governance',
        'level': 2
    },
    
    # Level 3: Governance details
    'subj_rr_gov_senate': {
        'label': 'The Senate (structure, procedure, power)',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_institutions',
        'level': 3
    },
    'subj_rr_gov_assemblies': {
        'label': 'Popular assemblies and voting',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_institutions',
        'level': 3
    },
    'subj_rr_gov_magistracies': {
        'label': 'Magistracies (powers, term limits, imperium)',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_institutions',
        'level': 3
    },
    'subj_rr_off_consul_praetor': {
        'label': 'Senior offices: Consul, Praetor, Censor',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_offices',
        'level': 3
    },
    'subj_rr_off_tribune_aedile': {
        'label': 'Popular/admin offices: Tribune, Aedile, Quaestor',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_offices',
        'level': 3
    },
    'subj_rr_off_dictatorship': {
        'label': 'Dictatorship & extraordinary commands',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_offices',
        'level': 3
    },
    'subj_rr_law_citizenship_status': {
        'label': 'Citizenship, rights, legal status',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_law',
        'level': 3
    },
    'subj_rr_law_courts_procedure': {
        'label': 'Courts, trials, legal procedure',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_law',
        'level': 3
    },
    'subj_rr_law_reforms': {
        'label': 'Reforms and constitutional change',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_law',
        'level': 3
    },
    'subj_rr_factions_optimates_populares': {
        'label': 'Factional politics (Optimates/Populares framing)',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_factions',
        'level': 3
    },
    'subj_rr_factions_civil_wars': {
        'label': 'Civil wars and internal conflicts',
        'primary_facet': 'POLITICAL',
        'related_facets': ['MILITARY'],
        'parent': 'subj_rr_gov_factions',
        'level': 3
    },
    'subj_rr_factions_proscriptions': {
        'label': 'Political violence, proscriptions, purges',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_gov_factions',
        'level': 3
    },
    
    # Level 2: Military subdivisions
    'subj_rr_mil_wars_campaigns': {
        'label': 'Wars and Campaigns',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_military',
        'level': 2
    },
    'subj_rr_mil_battles_ops': {
        'label': 'Battles and Operations',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_military',
        'level': 2
    },
    'subj_rr_mil_command_roles': {
        'label': 'Command, Leadership, and Military Roles',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_military',
        'level': 2
    },
    'subj_rr_mil_org_logistics': {
        'label': 'Army Organization, Recruitment, and Logistics',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_military',
        'level': 2
    },
    
    # Level 3: Military details
    'subj_rr_wars_external': {
        'label': 'External wars (interstate/expansionary)',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_mil_wars_campaigns',
        'level': 3
    },
    'subj_rr_wars_internal': {
        'label': 'Internal wars (civil/social/rebellion)',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_mil_wars_campaigns',
        'level': 3
    },
    'subj_rr_battles_land': {
        'label': 'Land battles and field operations',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_mil_battles_ops',
        'level': 3
    },
    'subj_rr_battles_naval': {
        'label': 'Naval warfare and sea operations',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_mil_battles_ops',
        'level': 3
    },
    'subj_rr_command_imperium': {
        'label': 'Imperium, command authority, delegation',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_mil_command_roles',
        'level': 3
    },
    'subj_rr_command_roles_registry': {
        'label': 'Military roles & command structure',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_mil_command_roles',
        'level': 3
    },
    'subj_rr_logistics_recruitment': {
        'label': 'Recruitment, conscription, service obligations',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_mil_org_logistics',
        'level': 3
    },
    'subj_rr_logistics_supply': {
        'label': 'Supply, pay, and military economy',
        'primary_facet': 'MILITARY',
        'parent': 'subj_rr_mil_org_logistics',
        'level': 3
    },
    
    # Level 2: Social subdivisions
    'subj_rr_soc_orders_status': {
        'label': 'Orders, Status, and Citizenship',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_rr_society',
        'level': 2
    },
    'subj_rr_soc_patronage': {
        'label': 'Patronage, Clientage, and Elite Networks',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_rr_society',
        'level': 2
    },
    'subj_rr_soc_family_gentes': {
        'label': 'Families, Gentes, and Prosopography',
        'primary_facet': 'BIOGRAPHIC',
        'parent': 'subj_rr_society',
        'level': 2
    },
    'subj_rr_soc_slavery_labor': {
        'label': 'Slavery, Labor, and Dependency',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_rr_society',
        'level': 2
    },
    
    # Level 3: Social details
    'subj_rr_social_orders': {
        'label': 'Social orders (Patrician, Plebeian, Equites)',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_rr_soc_orders_status',
        'level': 3
    },
    'subj_rr_social_citizenship': {
        'label': 'Citizenship expansion and integration',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_rr_soc_orders_status',
        'level': 3
    },
    'subj_rr_patronage_mechanisms': {
        'label': 'Mechanisms of patronage',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_rr_soc_patronage',
        'level': 3
    },
    'subj_rr_patronage_elite_competition': {
        'label': 'Elite competition and network power',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_rr_soc_patronage',
        'level': 3
    },
    'subj_rr_family_gentes': {
        'label': 'Gentes, lineages, naming systems',
        'primary_facet': 'BIOGRAPHIC',
        'parent': 'subj_rr_soc_family_gentes',
        'level': 3
    },
    'subj_rr_family_alliances': {
        'label': 'Marriage alliances and political kinship',
        'primary_facet': 'BIOGRAPHIC',
        'parent': 'subj_rr_soc_family_gentes',
        'level': 3
    },
    'subj_rr_slavery_institutions': {
        'label': 'Institutions of slavery and manumission',
        'primary_facet': 'SOCIAL',
        'parent': 'subj_rr_soc_slavery_labor',
        'level': 3
    },
    'subj_rr_labor_economy': {
        'label': 'Labor systems (free/enslaved/dependent)',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_soc_slavery_labor',
        'level': 3
    },
    
    # Level 2: Economic subdivisions
    'subj_rr_econ_land_agriculture': {
        'label': 'Landholding, Agriculture, and Estates',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_economy',
        'level': 2
    },
    'subj_rr_econ_tax_revenue': {
        'label': 'Taxation, Tribute, and Provincial Revenue',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_economy',
        'level': 2
    },
    'subj_rr_econ_trade_markets': {
        'label': 'Trade, Markets, and Mediterranean Networks',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_economy',
        'level': 2
    },
    
    # Level 3: Economic details
    'subj_rr_econ_land_reform': {
        'label': 'Land reform, redistribution, agrarian policy',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_econ_land_agriculture',
        'level': 3
    },
    'subj_rr_econ_finance_contracts': {
        'label': 'Finance, contracts, and publicani',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_econ_tax_revenue',
        'level': 3
    },
    'subj_rr_trade_routes': {
        'label': 'Trade routes and maritime networks',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_econ_trade_markets',
        'level': 3
    },
    'subj_rr_markets_money': {
        'label': 'Markets, money, and exchange',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_econ_trade_markets',
        'level': 3
    },
    
    # Level 2: Geographic subdivisions
    'subj_rr_geo_rome_italy': {
        'label': 'Rome and Italy (Republic Context)',
        'primary_facet': 'GEOGRAPHIC',
        'parent': 'subj_rr_geography',
        'level': 2
    },
    'subj_rr_geo_provinces_admin': {
        'label': 'Provinces and Administration',
        'primary_facet': 'GEOGRAPHIC',
        'parent': 'subj_rr_geography',
        'level': 2
    },
    'subj_rr_geo_frontiers_theaters': {
        'label': 'Frontiers and Theaters of War',
        'primary_facet': 'GEOGRAPHIC',
        'parent': 'subj_rr_geography',
        'level': 2
    },
    
    # Level 3: Geographic details
    'subj_rr_geo_provincial_governance': {
        'label': 'Provincial governance and administration',
        'primary_facet': 'POLITICAL',
        'parent': 'subj_rr_geo_provinces_admin',
        'level': 3
    },
    'subj_rr_geo_provincial_economy': {
        'label': 'Provincial extraction, tribute, local economies',
        'primary_facet': 'ECONOMIC',
        'parent': 'subj_rr_geo_provinces_admin',
        'level': 3
    },
    
    # Level 2: Diplomatic subdivisions
    'subj_rr_dip_treaties': {
        'label': 'Treaties, Negotiations, and Envoys',
        'primary_facet': 'DIPLOMATIC',
        'parent': 'subj_rr_diplomacy',
        'level': 2
    },
    'subj_rr_dip_clients': {
        'label': 'Client Kingdoms, Alliances, and Hegemony',
        'primary_facet': 'DIPLOMATIC',
        'parent': 'subj_rr_diplomacy',
        'level': 2
    },
    
    # Level 3: Diplomatic details
    'subj_rr_dip_envoys': {
        'label': 'Envoys, embassies, negotiation practice',
        'primary_facet': 'DIPLOMATIC',
        'parent': 'subj_rr_dip_treaties',
        'level': 3
    },
    'subj_rr_dip_treaty_systems': {
        'label': 'Treaty systems, guarantees, hostages',
        'primary_facet': 'DIPLOMATIC',
        'parent': 'subj_rr_dip_treaties',
        'level': 3
    },
    
    # Level 2: Religious subdivisions
    'subj_rr_rel_offices': {
        'label': 'Religious Offices, Priesthoods, and Authority',
        'primary_facet': 'RELIGIOUS',
        'parent': 'subj_rr_religion',
        'level': 2
    },
    'subj_rr_rel_rituals': {
        'label': 'Ritual Practice, Omens, and Public Ceremony',
        'primary_facet': 'RELIGIOUS',
        'parent': 'subj_rr_religion',
        'level': 2
    },
    
    # Level 3: Religious details
    'subj_rr_rel_priesthoods': {
        'label': 'Priesthoods and sacred colleges',
        'primary_facet': 'RELIGIOUS',
        'parent': 'subj_rr_rel_offices',
        'level': 3
    },
    'subj_rr_rel_public_ritual': {
        'label': 'Public ritual, auspices, legitimacy',
        'primary_facet': 'RELIGIOUS',
        'parent': 'subj_rr_rel_rituals',
        'level': 3
    },
    
    # Level 2: Ideas/Culture subdivisions
    'subj_rr_ideas_oratory': {
        'label': 'Oratory, Rhetoric, and Propaganda',
        'primary_facet': 'COMMUNICATION',
        'parent': 'subj_rr_culture_ideas',
        'level': 2
    },
    'subj_rr_ideas_historiography': {
        'label': 'Historiography, Sources, and Historical Method',
        'primary_facet': 'INTELLECTUAL',
        'parent': 'subj_rr_culture_ideas',
        'level': 2
    },
    'subj_rr_ideas_political_thought': {
        'label': 'Republicanism and Political Thought',
        'primary_facet': 'INTELLECTUAL',
        'parent': 'subj_rr_culture_ideas',
        'level': 2
    },
    'subj_rr_cult_identity': {
        'label': 'Civic Culture, Identity, and Romanitas',
        'primary_facet': 'CULTURAL',
        'parent': 'subj_rr_culture_ideas',
        'level': 2
    },
    
    # Level 3: Ideas details
    'subj_rr_oratory_forums': {
        'label': 'Forums, public speech, persuasion',
        'primary_facet': 'COMMUNICATION',
        'parent': 'subj_rr_ideas_oratory',
        'level': 3
    },
    'subj_rr_propaganda_symbols': {
        'label': 'Symbols, memory, persuasive narratives',
        'primary_facet': 'COMMUNICATION',
        'parent': 'subj_rr_ideas_oratory',
        'level': 3
    },
    'subj_rr_hist_sources': {
        'label': 'Primary sources and traditions',
        'primary_facet': 'INTELLECTUAL',
        'parent': 'subj_rr_ideas_historiography',
        'level': 3
    },
    'subj_rr_hist_method': {
        'label': 'Historical method, bias, source criticism',
        'primary_facet': 'INTELLECTUAL',
        'parent': 'subj_rr_ideas_historiography',
        'level': 3
    },
    'subj_rr_thought_republicanism': {
        'label': 'Republican ideals (virtus, mos maiorum, liberty)',
        'primary_facet': 'INTELLECTUAL',
        'parent': 'subj_rr_ideas_political_thought',
        'level': 3
    },
    'subj_rr_thought_constitutionalism': {
        'label': 'Constitutionalism and mixed government models',
        'primary_facet': 'INTELLECTUAL',
        'parent': 'subj_rr_ideas_political_thought',
        'level': 3
    },
    
    # Level 2: Temporal subdivisions
    'subj_rr_time_early': {
        'label': 'Early Republic (periodization)',
        'primary_facet': 'TEMPORAL',
        'parent': 'subj_rr_periodization',
        'level': 2
    },
    'subj_rr_time_middle': {
        'label': 'Middle Republic (periodization)',
        'primary_facet': 'TEMPORAL',
        'parent': 'subj_rr_periodization',
        'level': 2
    },
    'subj_rr_time_late': {
        'label': 'Late Republic (periodization)',
        'primary_facet': 'TEMPORAL',
        'parent': 'subj_rr_periodization',
        'level': 2
    },
    'subj_rr_time_transition': {
        'label': 'Transition to Empire',
        'primary_facet': 'TEMPORAL',
        'parent': 'subj_rr_periodization',
        'level': 2
    },
    
    # Level 3: Temporal details
    'subj_rr_time_early_events': {
        'label': 'Early Republic: institutional formation',
        'primary_facet': 'TEMPORAL',
        'parent': 'subj_rr_time_early',
        'level': 3
    },
    'subj_rr_time_middle_imperialism': {
        'label': 'Middle Republic: expansion and imperialism',
        'primary_facet': 'TEMPORAL',
        'parent': 'subj_rr_time_middle',
        'level': 3
    },
    'subj_rr_time_late_crisis': {
        'label': 'Late Republic: crisis, reform, civil war',
        'primary_facet': 'TEMPORAL',
        'parent': 'subj_rr_time_late',
        'level': 3
    },
}


def _get_driver():
    return GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def create_nodes_batch(tx, batch):
    """Create SubjectConcept nodes in batch.
    QID-less concepts get authority_federation_state: FS0_SYNTHETIC (honest provenance).
    """
    query = """
    UNWIND $batch AS row
    MERGE (s:SubjectConcept {subject_id: row.subject_id})
    SET s.label = row.label,
        s.qid = row.qid,
        s.primary_facet = row.primary_facet,
        s.level = row.level,
        s.status = 'approved',
        s.created_date = datetime(),
        s.authority_federation_state = CASE WHEN row.qid IS NULL OR row.qid = '' 
            THEN 'FS0_SYNTHETIC' ELSE null END,
        s.source = CASE WHEN row.qid IS NULL OR row.qid = '' 
            THEN 'synthetic' ELSE 'wikidata' END
    """
    tx.run(query, batch=batch)

def create_hierarchy_batch(tx, batch):
    """Create PART_OF relationships in batch"""
    query = """
    UNWIND $batch AS row
    MATCH (child:SubjectConcept {subject_id: row.child})
    MATCH (parent:SubjectConcept {subject_id: row.parent})
    MERGE (child)-[:PART_OF]->(parent)
    """
    tx.run(query, batch=batch)


def main():
    driver = _get_driver()
    print("=" * 80)
    print("LOADING ROMAN REPUBLIC ONTOLOGY TO NEO4J")
    print("=" * 80)
    print()
    # Step 1: Create all nodes
    print("[1/3] Creating SubjectConcept nodes...")
    batch = []

    for subject_id, data in ONTOLOGY.items():
        batch.append({
            'subject_id': subject_id,
            'label': data['label'],
            'qid': data.get('qid'),
            'primary_facet': data['primary_facet'],
            'level': data['level']
        })

    with driver.session(database=DATABASE) as session:
        session.execute_write(create_nodes_batch, batch)

    print(f"  Created {len(batch)} SubjectConcept nodes")
    print()

    # Step 2: Create hierarchy
    print("[2/3] Creating PART_OF hierarchy...")
    hierarchy_batch = []

    for subject_id, data in ONTOLOGY.items():
        if data['parent']:
            hierarchy_batch.append({
                'child': subject_id,
                'parent': data['parent']
            })

    with driver.session(database=DATABASE) as session:
        session.execute_write(create_hierarchy_batch, hierarchy_batch)

    print(f"  Created {len(hierarchy_batch)} PART_OF relationships")
    print()

    # Step 3: Create cross-links
    print("[3/3] Creating RELATED_TO cross-links...")

    cross_links = [
        ('subj_rr_factions_civil_wars', 'subj_rr_mil_wars_campaigns', 'Civil conflict spans political and military'),
        ('subj_rr_soc_patronage', 'subj_rr_gov_institutions', 'Patronage networks interact with institutions'),
        ('subj_rr_econ_tax_revenue', 'subj_rr_geo_provinces_admin', 'Revenue depends on provincial administration'),
        ('subj_rr_ideas_oratory', 'subj_rr_gov_factions', 'Rhetoric serves factional politics'),
        ('subj_rr_rel_offices', 'subj_rr_gov_offices', 'Religious authority overlaps with political office'),
    ]

    with driver.session(database=DATABASE) as session:
        for from_id, to_id, rationale in cross_links:
            session.run("""
                MATCH (a:SubjectConcept {subject_id: $from_id})
                MATCH (b:SubjectConcept {subject_id: $to_id})
                MERGE (a)-[r:RELATED_TO]->(b)
                SET r.rationale = $rationale
            """, from_id=from_id, to_id=to_id, rationale=rationale)

    print(f"  Created {len(cross_links)} RELATED_TO relationships")
    print()

    # Verification
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    with driver.session(database=DATABASE) as session:
        # Count nodes
        result = session.run("""
            MATCH (s:SubjectConcept)
            WHERE s.subject_id STARTS WITH 'subj_rr_' OR s.subject_id = 'subj_roman_republic_q17167'
            RETURN count(s) AS total
        """)
        total_nodes = result.single()['total']

        # Count by level
        result = session.run("""
            MATCH (s:SubjectConcept)
            WHERE s.subject_id STARTS WITH 'subj_rr_' OR s.subject_id = 'subj_roman_republic_q17167'
            RETURN s.level AS level, count(s) AS count
            ORDER BY level
        """)

        print(f"\nSubjectConcept nodes created: {total_nodes}")
        print("\nBy level:")
        for record in result:
            print(f"  Level {record['level']}: {record['count']} nodes")

        # Count relationships
        result = session.run("""
            MATCH ()-[r:PART_OF]->(:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
            RETURN count(r) AS direct_children
        """)
        direct_children = result.single()['direct_children']

        result = session.run("""
            MATCH (s:SubjectConcept)-[r:PART_OF]->()
            WHERE s.subject_id STARTS WITH 'subj_rr_'
            RETURN count(r) AS total_part_of
        """)
        total_part_of = result.single()['total_part_of']

        result = session.run("""
            MATCH ()-[r:RELATED_TO]->()
            RETURN count(r) AS cross_links
        """)
        cross_links_count = result.single()['cross_links']

        print(f"\nRelationships:")
        print(f"  Direct children of root: {direct_children}")
        print(f"  Total PART_OF: {total_part_of}")
        print(f"  Cross-links (RELATED_TO): {cross_links_count}")

        # Sample nodes
        print("\nSample L1 branches:")
        result = session.run("""
            MATCH (s:SubjectConcept)-[:PART_OF]->(root:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
            RETURN s.label AS label, s.primary_facet AS facet
            ORDER BY s.label
        """)
        for record in result:
            print(f"  - {record['label']} ({record['facet']})")

        # Show vertex jump hubs
        print("\nCross-link hubs (vertex jump nodes):")
        result = session.run("""
            MATCH (s:SubjectConcept)-[r:RELATED_TO]-()
            WITH s, count(r) AS link_count
            WHERE link_count > 0
            RETURN s.label AS label, link_count
            ORDER BY link_count DESC
        """)
        for record in result:
            print(f"  - {record['label']} ({record['link_count']} cross-links)")

    driver.close()

    print()
    print("=" * 80)
    print("ROMAN REPUBLIC ONTOLOGY LOADED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print(f"Total nodes: {total_nodes}")
    print(f"Total hierarchy links: {total_part_of}")
    print(f"Total cross-links: {cross_links_count}")
    print()
    print("Next steps:")
    print("  1. Verify in Neo4j Browser")
    print("  2. Spawn SFA agents (Political, Military, Social first)")
    print("  3. Begin entity/claim loading")
    print()


if __name__ == "__main__":
    main()

