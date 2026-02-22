#!/usr/bin/env python3
"""
FACET REFERENCE SUBGRAPH SCHEMA & LOADER
=========================================

Each of 17 facets has canonical concept categories (from discipline knowledge).

Example:
  Facet: Economic
    ├─ Supply & Demand (core economic principle)
    ├─ Production & Resource Allocation (fundamental mechanism)
    ├─ Macroeconomic Systems (aggregate level frameworks)
    ├─ Microeconomic Actors (individual agents)
    └─ Trade & Commerce (cross-boundary exchange)

  Facet: Military
    ├─ Tactics & Strategy
    ├─ Logistics & Supply
    ├─ Weaponry & Technology
    ├─ Battles & Campaigns
    └─ Military Leadership & Organization

This becomes canonical reference subgraph in Neo4j.

Agent initialization:
1. Load facet (e.g., "Economic")
2. Query FacetReference.CONTAINS → ConceptCategories
3. Agent understands discipline's major themes
4. Analyzes findings within these frameworks
5. Proposes sub-concepts aligned with canonical categories
"""

import json
from typing import Dict, List
from neo4j import GraphDatabase


# ============================================================================
# FACET CONCEPT CATEGORIES - CANONICAL DISCIPLINE KNOWLEDGE
# ============================================================================

FACET_CANONICAL_CATEGORIES = {
    "Economic": {
        "concept_categories": [
            {
                "id": "econ_001",
                "label": "Supply & Demand",
                "description": "Market mechanisms, scarcity, price signals",
                "key_topics": ["supply", "demand", "price", "scarcity", "equilibrium"],
                "related_authorities": ["LCSH: Economics--Supply and demand", "LCC: HB501-HB843"]
            },
            {
                "id": "econ_002",
                "label": "Production & Resource Allocation",
                "description": "Manufacturing, agriculture, resource distribution",
                "key_topics": ["production", "manufacturing", "agriculture", "resources", "allocation"],
                "related_authorities": ["LCSH: Production (Economic theory)"]
            },
            {
                "id": "econ_003",
                "label": "Macroeconomic Systems",
                "description": "Aggregate economy, trade, monetary systems, taxation",
                "key_topics": ["macroeconomics", "gdp", "trade", "money", "taxation", "inflation"],
                "related_authorities": ["LCSH: Macroeconomics"]
            },
            {
                "id": "econ_004",
                "label": "Microeconomic Actors",
                "description": "Merchants, craftspeople, labor, business",
                "key_topics": ["merchants", "craftspeople", "labor", "business", "consumers"],
                "related_authorities": ["LCSH: Microeconomics"]
            },
            {
                "id": "econ_005",
                "label": "Trade & Commerce",
                "description": "Exchange networks, commercial routes, merchant guilds",
                "key_topics": ["trade", "commerce", "merchants", "routes", "exchange"],
                "related_authorities": ["LCSH: Commerce"]
            }
        ]
    },
    
    "Military": {
        "concept_categories": [
            {
                "id": "mil_001",
                "label": "Strategy & Tactics",
                "description": "Military planning, battlefield tactics, campaign strategy",
                "key_topics": ["strategy", "tactics", "planning", "maneuvers", "campaigns"],
                "related_authorities": ["LCSH: Military art and science"]
            },
            {
                "id": "mil_002",
                "label": "Logistics & Supply",
                "description": "Supplies, transportation, provisions, bases",
                "key_topics": ["logistics", "supplies", "transportation", "provisions", "bases"],
                "related_authorities": ["LCSH: Military supplies and stores"]
            },
            {
                "id": "mil_003",
                "label": "Weaponry & Technology",
                "description": "Weapons, fortifications, military innovations",
                "key_topics": ["weapons", "fortifications", "technology", "armor", "siege"],
                "related_authorities": ["LCSH: Weaponry"]
            },
            {
                "id": "mil_004",
                "label": "Battles & Combat",
                "description": "Individual battles, engagements, military operations",
                "key_topics": ["battle", "combat", "engagement", "operation", "campaign"],
                "related_authorities": ["LCSH: Battles--History"]
            },
            {
                "id": "mil_005",
                "label": "Leadership & Organization",
                "description": "Command structure, military hierarchy, leadership",
                "key_topics": ["leadership", "command", "hierarchy", "general", "organization"],
                "related_authorities": ["LCSH: Military leadership"]
            }
        ]
    },
    
    "Political": {
        "concept_categories": [
            {
                "id": "pol_001",
                "label": "Governance Structures",
                "description": "Forms of government, institutions, administrative divisions",
                "key_topics": ["government", "institutions", "administration", "structure", "bureaucracy"],
                "related_authorities": ["LCSH: Political science--History"]
            },
            {
                "id": "pol_002",
                "label": "Legal & Constitutional Frameworks",
                "description": "Laws, legal systems, constitutions, rights",
                "key_topics": ["law", "legal", "constitution", "rights", "regulations"],
                "related_authorities": ["LCSH: Constitutional history"]
            },
            {
                "id": "pol_003",
                "label": "Power & Succession",
                "description": "Political authority, succession, accession, coups",
                "key_topics": ["power", "succession", "authority", "reign", "coup"],
                "related_authorities": ["LCSH: Political history"]
            },
            {
                "id": "pol_004",
                "label": "Factions & Political Movements",
                "description": "Political parties, factions, movements, alliances",
                "key_topics": ["faction", "party", "movement", "alliance", "opposition"],
                "related_authorities": ["LCSH: Political factions"]
            },
            {
                "id": "pol_005",
                "label": "International Relations",
                "description": "Diplomacy, treaties, foreign relations, alliances",
                "key_topics": ["diplomacy", "treaty", "relations", "alliance", "conflict"],
                "related_authorities": ["LCSH: International relations--History"]
            }
        ]
    },
    
    "Social": {
        "concept_categories": [
            {
                "id": "soc_001",
                "label": "Class & Status Systems",
                "description": "Social hierarchy, class structure, status",
                "key_topics": ["class", "status", "hierarchy", "rank", "caste"],
                "related_authorities": ["LCSH: Social classes"]
            },
            {
                "id": "soc_002",
                "label": "Kinship & Family",
                "description": "Family structures, kinship, marriage, inheritance",
                "key_topics": ["family", "kinship", "marriage", "inheritance", "lineage"],
                "related_authorities": ["LCSH: Family--History"]
            },
            {
                "id": "soc_003",
                "label": "Gender & Roles",
                "description": "Gender roles, women, men, social expectations",
                "key_topics": ["gender", "women", "men", "roles", "expectations"],
                "related_authorities": ["LCSH: Women--History"]
            },
            {
                "id": "soc_004",
                "label": "Ethnicity & Identity",
                "description": "Ethnic groups, identity, immigration, minorities",
                "key_topics": ["ethnicity", "identity", "minorities", "nationalism"],
                "related_authorities": ["LCSH: Ethnology"]
            },
            {
                "id": "soc_005",
                "label": "Labor & Occupations",
                "description": "Work, occupations, crafts, guilds, slavery",
                "key_topics": ["labor", "work", "occupation", "guild", "slavery"],
                "related_authorities": ["LCSH: Labor--History"]
            }
        ]
    },
    
    "Religious": {
        "concept_categories": [
            {
                "id": "rel_001",
                "label": "Theology & Belief Systems",
                "description": "Doctrines, theology, religious philosophy",
                "key_topics": ["theology", "doctrine", "belief", "philosophy", "faith"],
                "related_authorities": ["LCSH: Theology"]
            },
            {
                "id": "rel_002",
                "label": "Religious Institutions",
                "description": "Temples, monasteries, clergy, religious hierarchy",
                "key_topics": ["temple", "monastery", "church", "clergy", "hierarchy"],
                "related_authorities": ["LCSH: Monasticism"]
            },
            {
                "id": "rel_003",
                "label": "Ritual & Practice",
                "description": "Ceremonies, rituals, worship, festivals",
                "key_topics": ["ritual", "ceremony", "worship", "festival", "prayer"],
                "related_authorities": ["LCSH: Rituals"]
            },
            {
                "id": "rel_004",
                "label": "Religious Movements",
                "description": "Reformations, sects, cults, religious change",
                "key_topics": ["reformation", "sect", "cult", "movement", "heresy"],
                "related_authorities": ["LCSH: Reformation"]
            },
            {
                "id": "rel_005",
                "label": "Sacred Texts & Knowledge",
                "description": "Scriptures, theology, religious knowledge systems",
                "key_topics": ["scripture", "text", "knowledge", "interpretation"],
                "related_authorities": ["LCSH: Sacred books"]
            }
        ]
    },
    
    "Artistic": {
        "concept_categories": [
            {
                "id": "art_001",
                "label": "Visual Arts",
                "description": "Painting, sculpture, architecture",
                "key_topics": ["painting", "sculpture", "drawing", "art", "visual"],
                "related_authorities": ["LCSH: Art--History"]
            },
            {
                "id": "art_002",
                "label": "Performing Arts",
                "description": "Theater, music, dance",
                "key_topics": ["theater", "music", "dance", "performance"],
                "related_authorities": ["LCSH: Theater--History"]
            },
            {
                "id": "art_003",
                "label": "Literary Arts",
                "description": "Literature, poetry, writing",
                "key_topics": ["literature", "poetry", "writing", "author"],
                "related_authorities": ["LCSH: Literature--History"]
            },
            {
                "id": "art_004",
                "label": "Artistic Movements",
                "description": "Schools, styles, artistic movements",
                "key_topics": ["movement", "style", "school", "period"],
                "related_authorities": ["LCSH: Art movements"]
            },
            {
                "id": "art_005",
                "label": "Artists & Patrons",
                "description": "Artists, craftspeople, patronage",
                "key_topics": ["artist", "craftsperson", "patron", "workshop"],
                "related_authorities": ["LCSH: Artists--History"]
            }
        ]
    },
    
    "Technological": {
        "concept_categories": [
            {
                "id": "tech_001",
                "label": "Tools & Implements",
                "description": "Technology, tools, equipment",
                "key_topics": ["tool", "implement", "equipment", "technology"],
                "related_authorities": ["LCSH: Tools--History"]
            },
            {
                "id": "tech_002",
                "label": "Agricultural Technology",
                "description": "Farming techniques, irrigation, crops",
                "key_topics": ["agriculture", "farming", "irrigation", "crops", "technology"],
                "related_authorities": ["LCSH: Agriculture--History"]
            },
            {
                "id": "tech_003",
                "label": "Construction & Engineering",
                "description": "Building techniques, infrastructure, aqueducts",
                "key_topics": ["construction", "engineering", "building", "infrastructure"],
                "related_authorities": ["LCSH: Engineering--History"]
            },
            {
                "id": "tech_004",
                "label": "Manufacturing Processes",
                "description": "Production techniques, crafts, manufacturing",
                "key_topics": ["manufacturing", "production", "craft", "process"],
                "related_authorities": ["LCSH: Manufactures--History"]
            },
            {
                "id": "tech_005",
                "label": "Transportation",
                "description": "Ships, roads, vehicles, movement",
                "key_topics": ["transportation", "ship", "road", "vehicle", "travel"],
                "related_authorities": ["LCSH: Transportation--History"]
            }
        ]
    },
    
    "Geographic": {
        "concept_categories": [
            {
                "id": "geo_001",
                "label": "Physical Geography",
                "description": "Terrain, climate, geography, natural features",
                "key_topics": ["terrain", "climate", "geography", "mountain", "river"],
                "related_authorities": ["LCSH: Physical geography"]
            },
            {
                "id": "geo_002",
                "label": "Political Geography",
                "description": "Borders, territories, regions, cities",
                "key_topics": ["territory", "region", "city", "boundary", "settlement"],
                "related_authorities": ["LCSH: Political geography"]
            },
            {
                "id": "geo_003",
                "label": "Population & Settlement",
                "description": "Settlements, urbanization, demographics",
                "key_topics": ["settlement", "city", "urban", "population", "demographics"],
                "related_authorities": ["LCSH: Demography"]
            },
            {
                "id": "geo_004",
                "label": "Resources & Environment",
                "description": "Natural resources, ecology, environmental history",
                "key_topics": ["resource", "ecology", "environment", "nature"],
                "related_authorities": ["LCSH: Natural resources"]
            },
            {
                "id": "geo_005",
                "label": "Exploration & Trade Routes",
                "description": "Exploration, trade routes, travel, navigation",
                "key_topics": ["exploration", "route", "trade", "travel", "navigation"],
                "related_authorities": ["LCSH: Trade routes"]
            }
        ]
    }
}

# Continue for remaining 9 facets in production...
# (Biographical, Chronological, Diplomatic, Legal, Literary, Philosophical, Technological-extended)


class FacetReferenceLoader:
    """Load canonical facet concept categories into Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_facet_schema(self):
        """Create Neo4j schema for FacetReference subgraph"""
        with self.driver.session() as session:
            session.run("""
                CREATE CONSTRAINT facet_reference_unique IF NOT EXISTS
                ON (f:FacetReference) ASSERT f.facet IS UNIQUE;
                
                CREATE CONSTRAINT concept_category_unique IF NOT EXISTS
                ON (c:ConceptCategory) ASSERT c.id IS UNIQUE;
                
                CREATE INDEX facet_reference_facet IF NOT EXISTS
                FOR (f:FacetReference) ON (f.facet);
                
                CREATE INDEX concept_category_facet IF NOT EXISTS
                FOR (c:ConceptCategory) ON (c.facet);
            """)
            print("✓ Facet reference schema created")
    
    def load_all_facets(self):
        """Load all facet canonical categories"""
        for facet_name, facet_data in FACET_CANONICAL_CATEGORIES.items():
            self.load_facet(facet_name, facet_data)
    
    def load_facet(self, facet_name: str, facet_data: Dict):
        """
        Load one facet with its canonical concept categories.
        
        Creates:
          FacetReference(facet_name)
            ├─ CONTAINS → ConceptCategory(category_1)
            ├─ CONTAINS → ConceptCategory(category_2)
            └─ etc.
        """
        with self.driver.session() as session:
            # Create FacetReference node
            session.run("""
                MERGE (f:FacetReference { facet: $facet })
                SET f.created_date = datetime.now()
                SET f.source = "Canonical discipline knowledge"
            """, facet=facet_name)
            
            # Create ConceptCategory nodes + relationships
            for category in facet_data["concept_categories"]:
                session.run("""
                    MATCH (f:FacetReference { facet: $facet })
                    
                    MERGE (cat:ConceptCategory {
                        id: $category_id,
                        label: $label
                    })
                    SET cat.description = $description
                    SET cat.key_topics = $key_topics
                    SET cat.facet = $facet
                    SET cat.created_date = datetime.now()
                    
                    MERGE (f)-[:CONTAINS]->(cat)
                """,
                facet=facet_name,
                category_id=category["id"],
                label=category["label"],
                description=category["description"],
                key_topics=category["key_topics"]
                )
            
            print(f"✓ Loaded {facet_name} facet ({len(facet_data['concept_categories'])} categories)")
    
    def get_facet_categories(self, facet: str) -> List[Dict]:
        """
        Query canonical categories for a facet (used by agents).
        
        Returns: List of concept categories
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (f:FacetReference { facet: $facet })
                -[:CONTAINS]-> (cat:ConceptCategory)
                RETURN 
                    cat.id as id,
                    cat.label as label,
                    cat.description as description,
                    cat.key_topics as topics
                ORDER BY cat.label
            """, facet=facet)
            
            categories = []
            for record in result:
                categories.append({
                    "id": record["id"],
                    "label": record["label"],
                    "description": record["description"],
                    "key_topics": record["topics"]
                })
            
            return categories


# ============================================================================
# AGENT INITIALIZATION WITH FACET REFERENCE
# ============================================================================

class FacetAgentWithReference:
    """Agent initialized with canonical facet categories"""
    
    def __init__(self, facet: str, civilization: str, concept_categories: List[Dict]):
        """
        Initialize agent with discipline knowledge.
        
        Args:
            facet: e.g., "Economic"
            civilization: e.g., "Roman Republic"
            concept_categories: Canonical categories loaded from FacetReference
        """
        self.facet = facet
        self.civilization = civilization
        self.canonical_categories = concept_categories
        
        print(f"\n✓ Initialized {facet}Agent for {civilization}")
        print(f"  Canonical concept categories ({len(concept_categories)}):")
        for cat in concept_categories:
            print(f"    • {cat['label']}: {cat['description']}")
    
    def categorize_finding(self, finding_text: str) -> Dict:
        """
        Analyze finding and categorize within canonical framework.
        
        Returns: {
            "primary_category": "...",
            "category_matches": [...],
            "confidence": 0.82,
            "evidence_keywords": [...]
        }
        """
        # Simple keyword matching (in production, use LLM embeddings)
        text_lower = finding_text.lower()
        
        matches = []
        for category in self.canonical_categories:
            matched_topics = [
                topic for topic in category["key_topics"]
                if topic in text_lower
            ]
            
            if matched_topics:
                confidence = len(matched_topics) / len(category["key_topics"])
                matches.append({
                    "category": category["label"],
                    "matched_topics": matched_topics,
                    "confidence": confidence
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        result = {
            "finding_text": finding_text,
            "facet": self.facet,
            "primary_category": matches[0]["category"] if matches else "Uncategorized",
            "category_matches": matches,
            "categorization_confidence": matches[0]["confidence"] if matches else 0.0
        }
        
        return result


if __name__ == "__main__":
    # Example: Load facet references to Neo4j
    
    print("""
    ╔═════════════════════════════════════════════════════════╗
    ║   FACET REFERENCE SUBGRAPH LOADER                       ║
    ║   Canonical Concept Categories per Discipline           ║
    ╚═════════════════════════════════════════════════════════╝
    """)
    
    # Show example
    print("\nExample: Economic Facet Categories")
    print("-" * 50)
    
    econ_data = FACET_CANONICAL_CATEGORIES["Economic"]
    for cat in econ_data["concept_categories"]:
        print(f"\n{cat['id']}: {cat['label']}")
        print(f"  Description: {cat['description']}")
        print(f"  Key Topics: {', '.join(cat['key_topics'])}")
    
    # Example: Initialize agent
    print("\n" + "="*50)
    print("\nExample: Agent Initialization")
    print("-" * 50)
    
    categories = econ_data["concept_categories"]
    agent = FacetAgentWithReference(
        facet="Economic",
        civilization="Roman Republic",
        concept_categories=categories
    )
    
    # Test finding categorization
    print("\nExample: Categorize Finding")
    print("-" * 50)
    
    finding = "Evidence of large-scale taxation, tribute collection, and resource allocation across provinces"
    result = agent.categorize_finding(finding)
    
    print(f"\nFinding: {result['finding_text']}")
    print(f"Primary Category: {result['primary_category']}")
    print(f"Confidence: {result['categorization_confidence']:.2f}")
    print(f"\nMatched Categories:")
    for match in result['category_matches']:
        print(f"  • {match['category']}: {match['confidence']:.2f}")
        print(f"    Topics: {', '.join(match['matched_topics'])}")
    
    # Neo4j loading (when ready)
    print("""
    
    ╔═════════════════════════════════════════════════════════╗
    ║  TO LOAD TO NEO4J:                                      ║
    ║                                                         ║
    ║  loader = FacetReferenceLoader(uri, user, password)    ║
    ║  loader.create_facet_schema()                          ║
    ║  loader.load_all_facets()                              ║
    ║  categories = loader.get_facet_categories("Economic") ║
    ║  loader.close()                                        ║
    ╚═════════════════════════════════════════════════════════╝
    """)
