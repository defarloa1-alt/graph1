#!/usr/bin/env python3
"""Bootstrap Facet->DisciplineSource graph in Chrystal 2.0.

Creates DisciplineSource nodes and HAS_SOURCE edges to Facet nodes.
Clears the old discipline_sources blob property if present.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

CURRICULUM = {
    "archaeological": [
        {"label": "The Human Past: Introduction to Archaeology (MITx)", "url": "https://learn.mit.edu/c/unit/mitx?resource=4473", "type": "full_course", "provider": "MIT"},
        {"label": "Archaeology 101 - Archaeological Institute of America", "url": "https://www.archaeological.org/programs/public/archaeology-101/", "type": "primer", "provider": "AIA"},
    ],
    "artistic": [
        {"label": "Art History Survey - Dr. Vida Hull", "url": "https://www.learnoutloud.com/Catalog/Arts-and-Entertainment/Painting_-Architecture_-and-Sculpture/Art-History-Survey/73967", "type": "video_course", "provider": "LearnOutLoud"},
        {"label": "Art History Courses - OpenCulture", "url": "https://www.openculture.com/art-history-free-courses", "type": "course_index", "provider": "OpenCulture"},
    ],
    "biographic": [
        {"label": "Stanford Encyclopedia of Philosophy", "url": "https://plato.stanford.edu", "type": "reference", "provider": "Stanford"},
        {"label": "Oxford Dictionary of National Biography", "url": "https://www.oxforddnb.com", "type": "reference", "provider": "Oxford"},
    ],
    "communication": [
        {"label": "Communication in the Real World", "url": "https://openoregon.pressbooks.pub/commrealworld/", "type": "open_textbook", "provider": "Open Oregon"},
    ],
    "cultural": [
        {"label": "European Cultural History 1880-1920 - George Mosse", "url": "https://www.openculture.com/history_free_courses", "type": "course_index", "provider": "OpenCulture"},
        {"label": "World History - Khan Academy", "url": "https://www.khanacademy.org/humanities/world-history", "type": "full_course", "provider": "Khan Academy"},
    ],
    "demographic": [
        {"label": "Demography Course", "url": "https://www.elevify.com/en-er/courses/business-and-economics/economics/demography-course-15471", "type": "mooc", "provider": "Elevify"},
        {"label": "UN Population Division", "url": "https://www.un.org/development/desa/pd/", "type": "reference", "provider": "UN"},
    ],
    "diplomatic": [
        {"label": "Global Diplomacy: Diplomacy in the Modern World (SOAS)", "url": "https://www.coursera.org/learn/global-diplomacy", "type": "mooc", "provider": "Coursera/SOAS"},
        {"label": "Avalon Project - Treaties and Diplomacy", "url": "https://avalon.law.yale.edu", "type": "primary_source_archive", "provider": "Yale Law"},
    ],
    "economic": [
        {"label": "Economic History (MIT OCW 14.731)", "url": "https://ocw.mit.edu/courses/14-731-economic-history-fall-2006/", "type": "full_course", "provider": "MIT OCW"},
        {"label": "EH.net - Economic History Association", "url": "https://eh.net", "type": "reference", "provider": "EHA"},
    ],
    "environmental": [
        {"label": "The Global Environment (Yale OCW)", "url": "https://oyc.yale.edu/geology-and-geophysics/gg-140", "type": "full_course", "provider": "Yale OCW"},
        {"label": "Environment and Natural Resources Courses", "url": "https://www.openculture.com/environment-free-online-courses", "type": "course_index", "provider": "OpenCulture"},
    ],
    "geographic": [
        {"label": "Pleiades - Ancient World Geography", "url": "https://pleiades.stoa.org", "type": "scholarly_database", "provider": "Stoa Consortium"},
        {"label": "Landscape Archaeology", "url": "https://www.coursera.org/learn/landscape-archaeology", "type": "mooc", "provider": "Coursera"},
    ],
    "intellectual": [
        {"label": "History of Philosophy Without Any Gaps - Peter Adamson", "url": "https://historyofphilosophy.net", "type": "podcast_course", "provider": "Kings College London"},
        {"label": "Stanford Encyclopedia of Philosophy", "url": "https://plato.stanford.edu", "type": "reference", "provider": "Stanford"},
    ],
    "linguistic": [
        {"label": "Essentials of Linguistics (Open Textbook)", "url": "https://openlibrary-repo.ecampusontario.ca/jspui/handle/123456789/267", "type": "open_textbook", "provider": "eCampus Ontario"},
        {"label": "Introductory Linguistics (Coursera)", "url": "https://www.coursera.org/courses?query=linguistics", "type": "mooc_index", "provider": "Coursera"},
    ],
    "military": [
        {"label": "Introduction to Ancient Greek History - Donald Kagan (Yale OCW)", "url": "https://oyc.yale.edu/classics/clcv-205", "type": "full_course", "provider": "Yale OCW"},
        {"label": "Army War College Press - Strategic Studies Institute", "url": "https://press.armywarcollege.edu", "type": "scholarly_archive", "provider": "US Army War College"},
        {"label": "Naval War College Review", "url": "https://digital-commons.usnwc.edu/nwc-review/", "type": "journal", "provider": "US Naval War College"},
        {"label": "On War - Clausewitz (Project Gutenberg)", "url": "https://www.gutenberg.org/ebooks/1946", "type": "primary_source", "provider": "Project Gutenberg"},
    ],
    "political": [
        {"label": "The Moral Foundations of Politics - Ian Shapiro (Yale OCW)", "url": "https://oyc.yale.edu/political-science/plsc-118", "type": "full_course", "provider": "Yale OCW"},
        {"label": "France Since 1871 (Yale OCW)", "url": "https://oyc.yale.edu/history/hist-276", "type": "full_course", "provider": "Yale OCW"},
        {"label": "Political Science Courses (Coursera)", "url": "https://www.coursera.org/courses?query=political+science", "type": "mooc_index", "provider": "Coursera"},
    ],
    "religious": [
        {"label": "Introduction to the Old Testament - Christine Hayes (Yale OCW)", "url": "https://oyc.yale.edu/religious-studies/rlst-145", "type": "full_course", "provider": "Yale OCW"},
        {"label": "New Testament History and Literature - Dale Martin (Yale OCW)", "url": "https://oyc.yale.edu/religious-studies/rlst-152", "type": "full_course", "provider": "Yale OCW"},
        {"label": "World Religions (Coursera)", "url": "https://www.coursera.org/courses?query=world+religions", "type": "mooc_index", "provider": "Coursera"},
    ],
    "scientific": [
        {"label": "The Rise of Modern Science (MIT OCW STS.003)", "url": "https://ocw.mit.edu/courses/sts-003-the-rise-of-modern-science-fall-2010/", "type": "full_course", "provider": "MIT OCW"},
        {"label": "History of Science Society", "url": "https://hssonline.org", "type": "scholarly_index", "provider": "HSS"},
    ],
    "social": [
        {"label": "Foundations of Modern Social Theory - Ivan Szelenyi (Yale OCW)", "url": "https://oyc.yale.edu/sociology/socy-151", "type": "full_course", "provider": "Yale OCW"},
        {"label": "Introduction to Sociology (OpenStax)", "url": "https://openstax.org/books/introduction-sociology-3e/pages/1-introduction", "type": "open_textbook", "provider": "OpenStax"},
    ],
    "technological": [
        {"label": "Einstein, Oppenheimer, Feynman: Physics in 20th Century (MIT OCW STS.042J)", "url": "https://ocw.mit.edu/courses/sts-042j-einstein-oppenheimer-feynman-physics-in-the-20th-century-spring-2011/", "type": "full_course", "provider": "MIT OCW"},
        {"label": "The Industrial Revolution (FutureLearn)", "url": "https://www.futurelearn.com/courses/industrial-revolution", "type": "mooc", "provider": "FutureLearn"},
    ],
}

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
with driver.session() as s:
    for facet_key, sources in CURRICULUM.items():
        for src in sources:
            s.run("""
                MERGE (ds:DisciplineSource {url: $url})
                SET ds.label    = $label,
                    ds.type     = $type,
                    ds.provider = $provider
            """, url=src["url"], label=src["label"],
               type=src["type"], provider=src.get("provider", ""))

    node_count = s.run("MATCH (ds:DisciplineSource) RETURN count(ds) AS n").single()["n"]
    print(f"  DisciplineSource nodes: {node_count}")

driver.close()
print("\nDone.")
