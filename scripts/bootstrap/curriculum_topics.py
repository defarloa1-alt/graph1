#!/usr/bin/env python3
"""Bootstrap CurriculumTopic nodes from DisciplineSource content.

Schema:
  (Facet)-[:HAS_TOPIC]->(CurriculumTopic)
  (CurriculumTopic)-[:GROUNDED_IN]->(DisciplineSource)

Run one facet at a time:
  python scripts/bootstrap/curriculum_topics.py --facet military
  python scripts/bootstrap/curriculum_topics.py --facet all
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

# ---------------------------------------------------------------------------
# Curriculum topics derived from actual source content
# Each topic: key, label, description, grounded_in (DisciplineSource URL)
# ---------------------------------------------------------------------------

CURRICULUM = {
    "archaeological": {
        "topics": [
            {
                "key": "arch_excavation_methods",
                "label": "Excavation Methods & Field Techniques",
                "description": "Systematic approaches to uncovering and recording buried remains: stratigraphy, survey, sampling strategies, and documentation protocols.",
                "grounded_in": [
                    "https://learn.mit.edu/c/unit/mitx?resource=4473",
                    "https://www.archaeological.org/programs/public/archaeology-101/",
                ],
            },
            {
                "key": "arch_material_culture",
                "label": "Material Culture Analysis",
                "description": "Interpretation of artifacts, ceramics, lithics, architecture, and ecofacts to reconstruct past lifeways, technology, and social organization.",
                "grounded_in": ["https://www.archaeological.org/programs/public/archaeology-101/"],
            },
            {
                "key": "arch_human_origins",
                "label": "Human Origins & Prehistory",
                "description": "The deep human past from hominid evolution through the Upper Palaeolithic: stone tool industries, cognitive development, anatomical modernity, and dispersal from Africa.",
                "grounded_in": ["https://learn.mit.edu/c/unit/mitx?resource=4473"],
            },
            {
                "key": "arch_early_complex_societies",
                "label": "Early Complex Societies & State Formation",
                "description": "Rise of cities, writing, and political complexity in Mesopotamia, Egypt, the Indus Valley, China, and Mesoamerica: settlement hierarchies, palaces, temples.",
                "grounded_in": ["https://learn.mit.edu/c/unit/mitx?resource=4473"],
            },
            {
                "key": "arch_landscape_environment",
                "label": "Landscape Archaeology & Environmental Context",
                "description": "Reading the land: GIS and remote sensing, field survey, palaeoenvironmental reconstruction, and the relationship between human settlement and ecological change.",
                "grounded_in": [
                    "https://learn.mit.edu/c/unit/mitx?resource=4473",
                    "https://www.archaeological.org/programs/public/archaeology-101/",
                ],
            },
            {
                "key": "arch_theory_interpretation",
                "label": "Archaeological Theory & Interpretation",
                "description": "History of the discipline, processualism vs post-processualism, agency theory, contextual archaeology, and the ethics of excavation and repatriation.",
                "grounded_in": ["https://www.archaeological.org/programs/public/archaeology-101/"],
            },
        ]
    },
    "artistic": {
        "topics": [
            {
                "key": "art_periods_movements",
                "label": "Art Historical Periods & Movements",
                "description": "Chronological survey from Ancient to Modern: Antiquity, Byzantine, Medieval, Renaissance, Baroque, Neoclassicism, Romanticism, Modernism, and contemporary art.",
                "grounded_in": [
                    "https://www.learnoutloud.com/Catalog/Arts-and-Entertainment/Painting_-Architecture_-and-Sculpture/Art-History-Survey/73967",
                    "https://www.openculture.com/art-history-free-courses",
                ],
            },
            {
                "key": "art_visual_analysis",
                "label": "Visual Analysis & Formal Description",
                "description": "How to read a work of art: line, color, composition, space, light, and iconography; the vocabulary of formal and stylistic analysis.",
                "grounded_in": ["https://www.learnoutloud.com/Catalog/Arts-and-Entertainment/Painting_-Architecture_-and-Sculpture/Art-History-Survey/73967"],
            },
            {
                "key": "art_patronage_context",
                "label": "Patronage, Context & Social Function",
                "description": "Who commissioned art, why, and for what purpose: religious, political, and private patronage; the role of guilds, academies, and the art market.",
                "grounded_in": ["https://www.openculture.com/art-history-free-courses"],
            },
            {
                "key": "art_architecture",
                "label": "Architecture & Built Environment",
                "description": "The history of architectural form from temples and cathedrals to civic buildings: orders, structural systems, urban planning, and the built expression of power.",
                "grounded_in": ["https://www.learnoutloud.com/Catalog/Arts-and-Entertainment/Painting_-Architecture_-and-Sculpture/Art-History-Survey/73967"],
            },
            {
                "key": "art_media_technique",
                "label": "Media, Technique & Materials",
                "description": "How things are made: fresco, oil painting, sculpture in bronze and marble, printmaking, mosaic, tapestry — and what material choices reveal about period and place.",
                "grounded_in": ["https://www.openculture.com/art-history-free-courses"],
            },
        ]
    },
    "biographic": {
        "topics": [
            {
                "key": "bio_life_writing_methods",
                "label": "Life-Writing Methods & Sources",
                "description": "How to reconstruct a life from ancient and modern sources: epitaphs, letters, legal records, portraits, prosopographical databases, and critical use of ancient biographers.",
                "grounded_in": [
                    "https://plato.stanford.edu",
                    "https://www.oxforddnb.com",
                ],
            },
            {
                "key": "bio_prosopography",
                "label": "Prosopography & Collective Biography",
                "description": "Systematic study of groups of historical persons: family networks, career patterns, office-holding sequences, and the statistical analysis of lives in aggregate.",
                "grounded_in": ["https://www.oxforddnb.com"],
            },
            {
                "key": "bio_identity_selfhood",
                "label": "Identity, Self-Presentation & Memory",
                "description": "How individuals constructed public and private identities: honorifics, commemorative practices, funerary monuments, autobiography, and posthumous reputation.",
                "grounded_in": ["https://plato.stanford.edu"],
            },
            {
                "key": "bio_career_office",
                "label": "Careers, Office-Holding & Social Mobility",
                "description": "The cursus honorum, career ladders, patronage networks, social advancement and decline, and the biographical significance of public roles.",
                "grounded_in": ["https://www.oxforddnb.com"],
            },
            {
                "key": "bio_gender_age",
                "label": "Gender, Age & the Life Course",
                "description": "How ancient and modern societies structured biography by gender, life stage, and social role: childhood, education, marriage, old age, and death.",
                "grounded_in": ["https://plato.stanford.edu"],
            },
        ]
    },
    "communication": {
        "topics": [
            {
                "key": "comm_rhetoric_persuasion",
                "label": "Rhetoric & Persuasion",
                "description": "Classical and modern theories of persuasive communication: Aristotelian logos/ethos/pathos, argument structure, public speaking, and political oratory.",
                "grounded_in": ["https://openoregon.pressbooks.pub/commrealworld/"],
            },
            {
                "key": "comm_interpersonal",
                "label": "Interpersonal & Group Communication",
                "description": "How individuals communicate in dyadic and group settings: active listening, conflict resolution, nonverbal cues, and the dynamics of small groups.",
                "grounded_in": ["https://openoregon.pressbooks.pub/commrealworld/"],
            },
            {
                "key": "comm_written_oral",
                "label": "Written & Oral Traditions",
                "description": "The interplay of literacy and orality across cultures: scribal traditions, letters and inscriptions, oral formulaic composition, and the transition to print.",
                "grounded_in": ["https://openoregon.pressbooks.pub/commrealworld/"],
            },
            {
                "key": "comm_media_channels",
                "label": "Media, Channels & Information Spread",
                "description": "How messages move through social networks and institutions: rumor, propaganda, the ancient news cycle, pamphlets, and mass media from printing to digital.",
                "grounded_in": ["https://openoregon.pressbooks.pub/commrealworld/"],
            },
        ]
    },
    "cultural": {
        "topics": [
            {
                "key": "cul_mentalites_worldview",
                "label": "Mentalités & Collective Worldview",
                "description": "The assumptions, beliefs, and cognitive frameworks of a historical period: how contemporaries understood time, nature, the body, death, and social order.",
                "grounded_in": ["https://www.openculture.com/history_free_courses"],
            },
            {
                "key": "cul_nationalism_identity",
                "label": "Nationalism, Ethnicity & Cultural Identity",
                "description": "The construction and contestation of collective identities: ethnic origin myths, language politics, national symbols, and the invention of tradition.",
                "grounded_in": [
                    "https://www.openculture.com/history_free_courses",
                    "https://www.khanacademy.org/humanities/world-history",
                ],
            },
            {
                "key": "cul_popular_culture",
                "label": "Popular Culture & Everyday Life",
                "description": "Food, dress, festivals, games, entertainment, and the material culture of ordinary people; cultural history from below.",
                "grounded_in": ["https://www.khanacademy.org/humanities/world-history"],
            },
            {
                "key": "cul_cultural_exchange",
                "label": "Cultural Exchange, Transmission & Hybridization",
                "description": "How cultures borrow, adapt, and transform practices, technologies, and ideas through trade, conquest, migration, and diplomacy.",
                "grounded_in": ["https://www.khanacademy.org/humanities/world-history"],
            },
            {
                "key": "cul_intellectual_movements",
                "label": "Intellectual & Artistic Movements",
                "description": "Major cultural watersheds — Renaissance, Reformation, Enlightenment, Romanticism — understood as shifts in collective sensibility rather than just elite thought.",
                "grounded_in": ["https://www.openculture.com/history_free_courses"],
            },
        ]
    },
    "demographic": {
        "topics": [
            {
                "key": "dem_population_dynamics",
                "label": "Population Dynamics & Growth",
                "description": "Birth rates, death rates, natural increase, and the demographic transition model; how and why populations grow, stagnate, or collapse.",
                "grounded_in": [
                    "https://www.elevify.com/en-er/courses/business-and-economics/economics/demography-course-15471",
                    "https://www.un.org/development/desa/pd/",
                ],
            },
            {
                "key": "dem_mortality_life",
                "label": "Mortality, Life Expectancy & Health",
                "description": "Age-specific mortality, causes of death, epidemic disease, infant mortality, and the reconstruction of ancient and modern life tables.",
                "grounded_in": ["https://www.un.org/development/desa/pd/"],
            },
            {
                "key": "dem_migration_mobility",
                "label": "Migration, Mobility & Settlement",
                "description": "Internal and external migration, colonization, diaspora communities, forced displacement, and how movements of people reshape societies.",
                "grounded_in": [
                    "https://www.elevify.com/en-er/courses/business-and-economics/economics/demography-course-15471",
                    "https://www.un.org/development/desa/pd/",
                ],
            },
            {
                "key": "dem_family_household",
                "label": "Family Structure & Household Organization",
                "description": "Marriage patterns, household size, kinship systems, gender ratios, and how family organization mediates between individual lives and macro demographic trends.",
                "grounded_in": ["https://www.elevify.com/en-er/courses/business-and-economics/economics/demography-course-15471"],
            },
            {
                "key": "dem_sources_methods",
                "label": "Demographic Sources & Methods",
                "description": "Using censuses, epitaphs, tax records, and skeletal evidence to reconstruct ancient and historical populations; the challenges of pre-statistical demography.",
                "grounded_in": ["https://www.un.org/development/desa/pd/"],
            },
        ]
    },
    "diplomatic": {
        "topics": [
            {
                "key": "dip_treaty_negotiation",
                "label": "Treaty-Making & Negotiation",
                "description": "The practice of inter-state agreement: how treaties were negotiated, ratified, and broken; the role of heralds, envoys, and permanent ambassadors.",
                "grounded_in": [
                    "https://avalon.law.yale.edu",
                    "https://www.coursera.org/learn/global-diplomacy",
                ],
            },
            {
                "key": "dip_foreign_policy",
                "label": "Foreign Policy & State Interests",
                "description": "How states formulate and pursue external goals: realist and liberal frameworks, interest-group politics, intelligence, and the domestic sources of foreign policy.",
                "grounded_in": ["https://www.coursera.org/learn/global-diplomacy"],
            },
            {
                "key": "dip_international_law",
                "label": "International Law & Norms",
                "description": "The evolution of rules governing relations between states: the laws of war, diplomatic immunity, territorial sovereignty, and treaty obligations in antiquity and modernity.",
                "grounded_in": [
                    "https://avalon.law.yale.edu",
                    "https://www.coursera.org/learn/global-diplomacy",
                ],
            },
            {
                "key": "dip_diplomatic_institutions",
                "label": "Diplomatic Institutions & Protocol",
                "description": "The machinery of diplomacy: embassies, consular services, international organizations, summitry, and the ceremonial dimensions of inter-state relations.",
                "grounded_in": ["https://www.coursera.org/learn/global-diplomacy"],
            },
            {
                "key": "dip_primary_sources",
                "label": "Primary Sources in Diplomatic History",
                "description": "Reading treaties, dispatches, and diplomatic correspondence: how to use the Avalon Project, national archives, and published document series for diplomatic research.",
                "grounded_in": ["https://avalon.law.yale.edu"],
            },
        ]
    },
    "economic": {
        "topics": [
            {
                "key": "eco_growth_industrialization",
                "label": "Long-Run Growth & Industrialization",
                "description": "Why the Industrial Revolution happened when and where it did: factor endowments, institutions, technology, and the great divergence between rich and poor nations.",
                "grounded_in": [
                    "https://ocw.mit.edu/courses/14-731-economic-history-fall-2006/",
                    "https://eh.net",
                ],
            },
            {
                "key": "eco_trade_markets",
                "label": "Trade, Markets & Commercial Networks",
                "description": "The history of exchange from ancient emporia to modern global markets: merchant networks, price integration, commercial law, and the economics of empire.",
                "grounded_in": [
                    "https://ocw.mit.edu/courses/14-731-economic-history-fall-2006/",
                    "https://eh.net",
                ],
            },
            {
                "key": "eco_institutions_property",
                "label": "Institutions, Property Rights & the State",
                "description": "How property rights, contract enforcement, and fiscal institutions shape economic outcomes: New Institutional Economics applied to historical cases.",
                "grounded_in": ["https://ocw.mit.edu/courses/14-731-economic-history-fall-2006/"],
            },
            {
                "key": "eco_labor_living_standards",
                "label": "Labor, Wages & Living Standards",
                "description": "Real wages, inequality, and the material welfare of ordinary people across time; slavery, serfdom, free labor, and how labor markets worked before industrialization.",
                "grounded_in": [
                    "https://ocw.mit.edu/courses/14-731-economic-history-fall-2006/",
                    "https://eh.net",
                ],
            },
            {
                "key": "eco_finance_monetary",
                "label": "Finance, Money & Fiscal Systems",
                "description": "The history of money, banking, and public finance: coinage and currency, credit instruments, state debt, taxation, and financial crises.",
                "grounded_in": ["https://eh.net"],
            },
        ]
    },
    "environmental": {
        "topics": [
            {
                "key": "env_climate_history",
                "label": "Climate, Weather & Environmental Change",
                "description": "How climate shaped and was shaped by human societies: climate reconstructions, the Little Ice Age, drought cycles, and anthropogenic environmental change.",
                "grounded_in": [
                    "https://oyc.yale.edu/geology-and-geophysics/gg-140",
                    "https://www.openculture.com/environment-free-online-courses",
                ],
            },
            {
                "key": "env_land_resources",
                "label": "Land Use, Resources & Deforestation",
                "description": "How human societies transformed landscapes through agriculture, pastoralism, mining, and deforestation; soil degradation and resource exhaustion as historical forces.",
                "grounded_in": ["https://oyc.yale.edu/geology-and-geophysics/gg-140"],
            },
            {
                "key": "env_disease_ecology",
                "label": "Disease Ecology & Epidemic History",
                "description": "The environmental conditions that produce epidemic disease: climate, animal reservoirs, trade routes, urbanization, and the biological consequences of empire.",
                "grounded_in": ["https://www.openculture.com/environment-free-online-courses"],
            },
            {
                "key": "env_water_systems",
                "label": "Water, Irrigation & Hydraulic Systems",
                "description": "Rivers, floods, irrigation canals, aqueducts, and drainage: how ancient and pre-modern societies managed water and how water shaped political power.",
                "grounded_in": ["https://oyc.yale.edu/geology-and-geophysics/gg-140"],
            },
            {
                "key": "env_human_earth_systems",
                "label": "Human-Earth Systems Interaction",
                "description": "Earth as a system: atmosphere, hydrosphere, biosphere, and lithosphere as interconnected domains within which human history unfolds.",
                "grounded_in": ["https://oyc.yale.edu/geology-and-geophysics/gg-140"],
            },
        ]
    },
    "geographic": {
        "topics": [
            {
                "key": "geo_place_topography",
                "label": "Places, Topography & Settlement Patterns",
                "description": "Identifying and mapping ancient places: the Pleiades gazetteer, ancient place-names, topographical description, and the relationship between terrain and settlement.",
                "grounded_in": [
                    "https://pleiades.stoa.org",
                    "https://www.coursera.org/learn/landscape-archaeology",
                ],
            },
            {
                "key": "geo_historical_cartography",
                "label": "Historical Cartography & Spatial Representation",
                "description": "Ancient and pre-modern maps as historical documents: Ptolemy's Geography, medieval mappamundi, portolan charts, and the history of representing the world.",
                "grounded_in": ["https://pleiades.stoa.org"],
            },
            {
                "key": "geo_landscape_change",
                "label": "Landscape Change & Human Geography",
                "description": "How landscapes were transformed by agriculture, urbanization, road-building, and colonization; field systems, centuriation, and reading the countryside.",
                "grounded_in": [
                    "https://www.coursera.org/learn/landscape-archaeology",
                    "https://pleiades.stoa.org",
                ],
            },
            {
                "key": "geo_territory_empire",
                "label": "Territory, Frontiers & Imperial Geography",
                "description": "How ancient and pre-modern states organized space: administrative districts, border zones, frontier limes, provinces, and the geography of empire.",
                "grounded_in": ["https://pleiades.stoa.org"],
            },
            {
                "key": "geo_routes_connectivity",
                "label": "Routes, Networks & Connectivity",
                "description": "Roads, sea lanes, river systems, and portage routes as the infrastructure of trade, communication, and military movement; network analysis in historical geography.",
                "grounded_in": ["https://www.coursera.org/learn/landscape-archaeology"],
            },
        ]
    },
    "intellectual": {
        "topics": [
            {
                "key": "int_ancient_philosophy",
                "label": "Ancient Philosophy & the Pre-Socratics",
                "description": "From Thales through the Pre-Socratics to Plato and Aristotle: the origins of philosophical inquiry, natural philosophy, ethics, politics, and metaphysics.",
                "grounded_in": [
                    "https://historyofphilosophy.net",
                    "https://plato.stanford.edu",
                ],
            },
            {
                "key": "int_hellenistic_medieval",
                "label": "Hellenistic, Islamic & Medieval Thought",
                "description": "Stoics, Epicureans, Neoplatonists; the transmission of Greek learning through Arabic philosophy; scholasticism, theology, and medieval natural philosophy.",
                "grounded_in": ["https://historyofphilosophy.net"],
            },
            {
                "key": "int_history_of_ideas",
                "label": "History of Ideas & Intellectual Transmission",
                "description": "How ideas travel across time and culture: commentary traditions, translation, the role of schools and academies, censorship, and intellectual genealogies.",
                "grounded_in": [
                    "https://historyofphilosophy.net",
                    "https://plato.stanford.edu",
                ],
            },
            {
                "key": "int_political_social_thought",
                "label": "Political & Social Thought",
                "description": "The history of ideas about justice, governance, the state, and society: from Plato's Republic through Cicero, Machiavelli, Hobbes, Locke, and Rousseau.",
                "grounded_in": ["https://plato.stanford.edu"],
            },
            {
                "key": "int_science_natural_philosophy",
                "label": "Natural Philosophy & History of Science as Intellectual History",
                "description": "Scientific ideas as intellectual history: Aristotelian natural philosophy, early modern mechanism, the Scientific Revolution as a transformation of concepts.",
                "grounded_in": ["https://plato.stanford.edu"],
            },
        ]
    },
    "linguistic": {
        "topics": [
            {
                "key": "ling_historical_change",
                "label": "Language Change & Historical Linguistics",
                "description": "Sound shifts, grammatical evolution, semantic change, and the comparative method: how linguists reconstruct proto-languages and trace language families.",
                "grounded_in": [
                    "https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/267",
                    "https://www.coursera.org/courses?query=linguistics",
                ],
            },
            {
                "key": "ling_writing_epigraphy",
                "label": "Writing Systems, Epigraphy & Decipherment",
                "description": "The invention and spread of writing: cuneiform, hieroglyphics, alphabets, syllabaries; reading ancient inscriptions and the history of decipherment.",
                "grounded_in": ["https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/267"],
            },
            {
                "key": "ling_multilingualism_contact",
                "label": "Multilingualism, Language Contact & Bilingualism",
                "description": "What happens when languages meet: borrowing, code-switching, pidgins and creoles, diglossia, and the sociolinguistics of empire and trade.",
                "grounded_in": ["https://www.coursera.org/courses?query=linguistics"],
            },
            {
                "key": "ling_oral_literacy",
                "label": "Orality, Literacy & Text Transmission",
                "description": "The transition from oral to literate cultures; manuscript traditions, textual criticism, scribal practice, and how texts were copied, corrected, and corrupted.",
                "grounded_in": ["https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/267"],
            },
            {
                "key": "ling_phonology_grammar",
                "label": "Phonology, Morphology & Grammar",
                "description": "Core linguistic structures: how sounds are organized into systems, how words are built from morphemes, and how sentences are structured across languages.",
                "grounded_in": ["https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/267"],
            },
        ]
    },
    "military": {
        "topics": [
            {
                "key": "mil_theory_strategy",
                "label": "Military Theory & Strategy",
                "description": "Foundational concepts of military strategy, the war-politics nexus (Clausewitz), principles of war, and why universal rules cannot govern warfare.",
                "grounded_in": ["https://www.gutenberg.org/ebooks/1946"],
            },
            {
                "key": "mil_ancient_warfare",
                "label": "Ancient & Classical Warfare",
                "description": "Military history of the ancient world: Greek hoplite warfare, Persian Wars, Peloponnesian War, city-state armies, and the tactical evolution from Bronze Age to classical period.",
                "grounded_in": ["https://oyc.yale.edu/classics/clcv-205"],
            },
            {
                "key": "mil_grand_strategy",
                "label": "Grand Strategy & Defense Policy",
                "description": "How states translate political objectives into military force: grand strategy, defense planning, deterrence, nuclear strategy, and the institutional structures of military power.",
                "grounded_in": ["https://press.armywarcollege.edu"],
            },
            {
                "key": "mil_maritime_sea_power",
                "label": "Naval & Maritime Warfare",
                "description": "Sea power theory, fleet operations, sealift and logistics, naval aviation, and the historical development of maritime strategy from antiquity to the modern era.",
                "grounded_in": ["https://digital-commons.usnwc.edu/nwc-review/"],
            },
            {
                "key": "mil_leadership_ethics",
                "label": "Military Leadership & Ethics",
                "description": "Strategic leadership and decision-making under uncertainty, military ethics, the professional military identity, and command responsibility.",
                "grounded_in": ["https://press.armywarcollege.edu"],
            },
            {
                "key": "mil_political_nexus",
                "label": "War & Political Power",
                "description": "The relationship between military force and political authority: war as instrument of policy, military-political integration, triumph and legitimacy, constitutional constraints on armies.",
                "grounded_in": [
                    "https://www.gutenberg.org/ebooks/1946",
                    "https://oyc.yale.edu/classics/clcv-205",
                ],
            },
            {
                "key": "mil_historical_analysis",
                "label": "Military Historical Analysis",
                "description": "Methodology for studying warfare: how scholars reconstruct battles, evaluate sources, assess command decisions, and draw historical lessons for doctrine.",
                "grounded_in": [
                    "https://digital-commons.usnwc.edu/nwc-review/",
                    "https://press.armywarcollege.edu",
                ],
            },
        ]
    },
    "political": {
        "topics": [
            {
                "key": "pol_state_formation",
                "label": "State Formation & Political Authority",
                "description": "How states emerge and consolidate power: the polis, monarchy, republic, empire, and the constitutional frameworks that regulate authority.",
                "grounded_in": [
                    "https://oyc.yale.edu/political-science/plsc-118",
                    "https://www.coursera.org/courses?query=political+science",
                ],
            },
            {
                "key": "pol_political_thought",
                "label": "Political Thought & Ideologies",
                "description": "Foundational texts and traditions of political theory: natural rights, social contract, Marxism, liberalism, republicanism, and their historical contexts.",
                "grounded_in": ["https://oyc.yale.edu/political-science/plsc-118"],
            },
            {
                "key": "pol_governance_institutions",
                "label": "Governance, Institutions & Law",
                "description": "How constitutions, assemblies, magistracies, and legal codes organize political life; the institutions that distribute power and manage conflict.",
                "grounded_in": [
                    "https://oyc.yale.edu/history/hist-276",
                    "https://www.coursera.org/courses?query=political+science",
                ],
            },
            {
                "key": "pol_political_movements",
                "label": "Political Movements, Parties & Revolution",
                "description": "How political change happens from below: mass movements, parties, elections, revolutionary crises, and the transition between political regimes.",
                "grounded_in": ["https://oyc.yale.edu/history/hist-276"],
            },
            {
                "key": "pol_empire_sovereignty",
                "label": "Empire, Sovereignty & International Order",
                "description": "The political dimensions of empire: tributary systems, provincial administration, citizenship, sovereignty claims, and the ordering of inter-state relations.",
                "grounded_in": [
                    "https://oyc.yale.edu/political-science/plsc-118",
                    "https://oyc.yale.edu/history/hist-276",
                ],
            },
        ]
    },
    "religious": {
        "topics": [
            {
                "key": "rel_scripture_canon",
                "label": "Scripture, Canon & Textual Tradition",
                "description": "How sacred texts were composed, compiled, and canonized: the Documentary Hypothesis, synoptic problem, oral tradition behind written texts, and textual criticism.",
                "grounded_in": [
                    "https://oyc.yale.edu/religious-studies/rlst-145",
                    "https://oyc.yale.edu/religious-studies/rlst-152",
                ],
            },
            {
                "key": "rel_ritual_practice",
                "label": "Ritual, Cult & Religious Practice",
                "description": "How religion is lived: sacrifice, prayer, pilgrimage, festivals, divination, and the material culture of worship from temples to household shrines.",
                "grounded_in": [
                    "https://oyc.yale.edu/religious-studies/rlst-145",
                    "https://www.coursera.org/courses?query=world+religions",
                ],
            },
            {
                "key": "rel_theology_belief",
                "label": "Theology, Cosmology & Belief Systems",
                "description": "What people believed: concepts of god, creation, afterlife, sin, salvation, and the intellectual elaboration of doctrine in different religious traditions.",
                "grounded_in": [
                    "https://oyc.yale.edu/religious-studies/rlst-152",
                    "https://www.coursera.org/courses?query=world+religions",
                ],
            },
            {
                "key": "rel_religion_politics",
                "label": "Religion & Political Power",
                "description": "The entanglement of religion and political authority: state cults, priestly offices, religious legitimation of rulership, and religious conflict as political conflict.",
                "grounded_in": ["https://oyc.yale.edu/religious-studies/rlst-145"],
            },
            {
                "key": "rel_conversion_spread",
                "label": "Conversion, Missionary Activity & Religious Spread",
                "description": "How religions expand: missionary movements, syncretism, forced conversion, the spread of Christianity and Islam, and the dynamics of religious change.",
                "grounded_in": ["https://www.coursera.org/courses?query=world+religions"],
            },
        ]
    },
    "scientific": {
        "topics": [
            {
                "key": "sci_scientific_revolution",
                "label": "The Scientific Revolution",
                "description": "Copernicus through Newton: the heliocentric revolution, Galileo's mechanics, Kepler's planetary laws, and the transformation of natural philosophy into modern science.",
                "grounded_in": ["https://ocw.mit.edu/courses/sts-003-the-rise-of-modern-science-fall-2010/"],
            },
            {
                "key": "sci_ancient_medieval_science",
                "label": "Ancient & Medieval Natural Philosophy",
                "description": "Greek natural philosophy (Aristotle, atomists), Hellenistic science (Archimedes, Ptolemy), Islamic transmission, and medieval scholastic natural philosophy.",
                "grounded_in": [
                    "https://ocw.mit.edu/courses/sts-003-the-rise-of-modern-science-fall-2010/",
                    "https://hssonline.org",
                ],
            },
            {
                "key": "sci_method_practice",
                "label": "Scientific Method & the Practice of Science",
                "description": "How science is done: experiment, observation, mathematical modeling, peer review, laboratory culture, and the sociology of scientific knowledge.",
                "grounded_in": [
                    "https://ocw.mit.edu/courses/sts-003-the-rise-of-modern-science-fall-2010/",
                    "https://hssonline.org",
                ],
            },
            {
                "key": "sci_society_culture",
                "label": "Science, Society & Culture",
                "description": "Science in its social context: patronage, institutions (academies, universities), science and religion, science and empire, and the public understanding of science.",
                "grounded_in": ["https://hssonline.org"],
            },
            {
                "key": "sci_key_disciplines",
                "label": "Development of Scientific Disciplines",
                "description": "How separate sciences emerged: the history of physics, chemistry, biology, medicine, astronomy, and geology as distinct professional disciplines.",
                "grounded_in": ["https://hssonline.org"],
            },
        ]
    },
    "social": {
        "topics": [
            {
                "key": "soc_classical_theory",
                "label": "Classical Social Theory",
                "description": "Marx on class and capitalism, Durkheim on solidarity and anomie, Weber on rationalization and the Protestant ethic: the founding frameworks of sociology.",
                "grounded_in": [
                    "https://oyc.yale.edu/sociology/socy-151",
                    "https://openstax.org/books/introduction-sociology-3e/pages/1-introduction",
                ],
            },
            {
                "key": "soc_class_inequality",
                "label": "Class, Stratification & Social Inequality",
                "description": "How societies rank individuals and groups by wealth, status, and power: orders, estates, classes, castes, and the mechanisms of social mobility and exclusion.",
                "grounded_in": [
                    "https://oyc.yale.edu/sociology/socy-151",
                    "https://openstax.org/books/introduction-sociology-3e/pages/1-introduction",
                ],
            },
            {
                "key": "soc_community_institutions",
                "label": "Communities, Institutions & Social Organization",
                "description": "Families, clans, guilds, voluntary associations, neighborhoods, and civic institutions: the intermediate structures between individuals and the state.",
                "grounded_in": ["https://openstax.org/books/introduction-sociology-3e/pages/1-introduction"],
            },
            {
                "key": "soc_modernity_change",
                "label": "Modernity, Social Change & Rationalization",
                "description": "What makes modern society distinctive: urbanization, bureaucratization, individualism, secularization, and the Weberian thesis of disenchantment.",
                "grounded_in": ["https://oyc.yale.edu/sociology/socy-151"],
            },
            {
                "key": "soc_gender_family",
                "label": "Gender, Family & Domestic Life",
                "description": "The social construction of gender roles, marriage systems, household economics, and the history of private life from Roman familia to the modern nuclear family.",
                "grounded_in": ["https://openstax.org/books/introduction-sociology-3e/pages/1-introduction"],
            },
        ]
    },
    "technological": {
        "topics": [
            {
                "key": "tech_innovation_diffusion",
                "label": "Invention, Innovation & Diffusion",
                "description": "How new technologies are invented, spread, and adopted: the conditions for innovation, the role of networks and institutions, and technology transfer across cultures.",
                "grounded_in": [
                    "https://www.futurelearn.com/courses/industrial-revolution",
                    "https://ocw.mit.edu/courses/sts-042j-einstein-oppenheimer-feynman-physics-in-the-20th-century-spring-2011/",
                ],
            },
            {
                "key": "tech_industrial_revolution",
                "label": "Industrialization & the Industrial Revolution",
                "description": "The transformation from agrarian to industrial economies: steam power, factory system, textile industry, coal and iron, and the social consequences of industrialization.",
                "grounded_in": ["https://www.futurelearn.com/courses/industrial-revolution"],
            },
            {
                "key": "tech_military_technology",
                "label": "Military Technology & Weapons Development",
                "description": "From the bronze sword to nuclear weapons: how military technology drove and was driven by social and political change; arms races and the revolution in military affairs.",
                "grounded_in": ["https://ocw.mit.edu/courses/sts-042j-einstein-oppenheimer-feynman-physics-in-the-20th-century-spring-2011/"],
            },
            {
                "key": "tech_infrastructure_engineering",
                "label": "Infrastructure, Engineering & Built Systems",
                "description": "Roads, aqueducts, harbors, bridges, and fortifications as technological achievements; the organization of engineering labor and the management of large-scale projects.",
                "grounded_in": ["https://www.futurelearn.com/courses/industrial-revolution"],
            },
            {
                "key": "tech_science_technology",
                "label": "Science-Technology Relations",
                "description": "How pure science and applied technology interact: from ancient mechanics through 20th-century physics (relativity, quantum, nuclear) to the industrial lab.",
                "grounded_in": ["https://ocw.mit.edu/courses/sts-042j-einstein-oppenheimer-feynman-physics-in-the-20th-century-spring-2011/"],
            },
        ]
    },
}


def run(facet_keys):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as s:
        for facet_key in facet_keys:
            data = CURRICULUM.get(facet_key)
            if not data:
                print(f"  No curriculum defined for: {facet_key}")
                continue

            topics = data["topics"]
            print(f"\n  Facet: {facet_key} ({len(topics)} topics)")

            for t in topics:
                # Create CurriculumTopic + HAS_TOPIC from Facet
                s.run("""
                    MERGE (ct:CurriculumTopic {key: $key})
                    SET ct.label       = $label,
                        ct.description = $description,
                        ct.facet_key   = $facet_key
                    WITH ct
                    MATCH (f:Facet {key: $facet_key})
                    MERGE (f)-[:HAS_TOPIC]->(ct)
                """, key=t["key"], label=t["label"],
                     description=t["description"], facet_key=facet_key)

                # GROUNDED_IN edges to DisciplineSources
                for url in t.get("grounded_in", []):
                    s.run("""
                        MATCH (ct:CurriculumTopic {key: $key})
                        MATCH (ds:DisciplineSource {url: $url})
                        MERGE (ct)-[:GROUNDED_IN]->(ds)
                    """, key=t["key"], url=url)

                print(f"    + {t['label']}")

        # Verify
        print()
        result = s.run("""
            MATCH (f:Facet)-[:HAS_TOPIC]->(ct:CurriculumTopic)
            RETURN f.key AS facet, count(ct) AS topics
            ORDER BY f.key
        """)
        print(f"  {'Facet':<20} Topics")
        print("  " + "-" * 30)
        for row in result:
            print(f"  {row['facet']:<20} {row['topics']}")

        ct_count = s.run("MATCH (ct:CurriculumTopic) RETURN count(ct) AS n").single()["n"]
        gi_count = s.run("MATCH ()-[:GROUNDED_IN]->() RETURN count(*) AS n").single()["n"]
        print(f"\n  CurriculumTopic nodes: {ct_count}")
        print(f"  GROUNDED_IN edges:     {gi_count}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--facet", default="military",
                        help="Facet key to process, or 'all'")
    args = parser.parse_args()

    if args.facet == "all":
        keys = list(CURRICULUM.keys())
    else:
        keys = [args.facet.strip().lower()]

    run(keys)
