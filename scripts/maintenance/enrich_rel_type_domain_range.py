#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch-annotate SYS_RelationshipType nodes with domain, range, facet.
Only patches nodes that are missing domain. Idempotent (SET only if needed).
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

# domain/range use the general type token (Entity, Person, Place, Event, Period,
# Work, Organization, Position, Claim, Agent, Year — or "any" for infra)
# facet = one of the 18 canonical facets, or None for infrastructure rels

ANNOTATIONS = {
    # ── INFRASTRUCTURE (no facet) ─────────────────────────────────────────────
    "ABOUT_SUBJECT":      {"domain": "Claim",   "range": "SubjectConcept", "facet": None},
    "ASSIGNED_TO_FACET":  {"domain": "Agent",   "range": "Facet",          "facet": None},
    "EVIDENCED_BY":       {"domain": "Entity",  "range": "Claim",          "facet": None},
    "PROPOSED_BY":        {"domain": "Claim",   "range": "Agent",          "facet": None},
    "REFERENCES":         {"domain": "Claim",   "range": "Entity",         "facet": None},
    "NARROWER_THAN":      {"domain": "Entity",  "range": "Entity",         "facet": None},
    "IS_PART_OF":         {"domain": "Entity",  "range": "Entity",         "facet": None},
    "HAS_PART":           {"domain": "Entity",  "range": "Entity",         "facet": None},
    "DESCRIBES":          {"domain": "Work",    "range": "Entity",         "facet": "INTELLECTUAL"},

    # ── TEMPORAL ─────────────────────────────────────────────────────────────
    "BORN_IN_YEAR":       {"domain": "Person",  "range": "Year",           "facet": "BIOGRAPHICAL"},
    "DIED_IN_YEAR":       {"domain": "Person",  "range": "Year",           "facet": "BIOGRAPHICAL"},
    "STARTS_IN_YEAR":     {"domain": "Period",  "range": "Year",           "facet": "TEMPORAL"},
    "ENDS_IN_YEAR":       {"domain": "Period",  "range": "Year",           "facet": "TEMPORAL"},
    "DURING_PERIOD":      {"domain": "Event",   "range": "Period",         "facet": "TEMPORAL"},
    "PRECEDED_BY":        {"domain": "Entity",  "range": "Entity",         "facet": "TEMPORAL"},
    "SUCCEEDED_BY":       {"domain": "Entity",  "range": "Entity",         "facet": "TEMPORAL"},
    "FOLLOWED_BY":        {"domain": "Entity",  "range": "Entity",         "facet": "TEMPORAL"},

    # ── BIOGRAPHICAL ─────────────────────────────────────────────────────────
    "BIRTHPLACE_OF":      {"domain": "Place",   "range": "Person",         "facet": "BIOGRAPHICAL"},
    "DEATH_PLACE_OF":     {"domain": "Place",   "range": "Person",         "facet": "BIOGRAPHICAL"},
    "BORN_IN":            {"domain": "Person",  "range": "Place",          "facet": "BIOGRAPHICAL"},
    "DIED_IN":            {"domain": "Person",  "range": "Place",          "facet": "BIOGRAPHICAL"},
    "CHILD_OF":           {"domain": "Person",  "range": "Person",         "facet": "BIOGRAPHICAL"},
    "FATHER_OF":          {"domain": "Person",  "range": "Person",         "facet": "BIOGRAPHICAL"},
    "SIBLING_OF":         {"domain": "Person",  "range": "Person",         "facet": "SOCIAL"},
    "WIFE_OF":            {"domain": "Person",  "range": "Person",         "facet": "SOCIAL"},
    "PART_OF_GENS":       {"domain": "Person",  "range": "Organization",   "facet": "SOCIAL"},
    "EXILED":             {"domain": "Person",  "range": "Place",          "facet": "POLITICAL"},
    "FLED_TO":            {"domain": "Person",  "range": "Place",          "facet": "POLITICAL"},

    # ── POLITICAL ─────────────────────────────────────────────────────────────
    "ADHERES_TO":         {"domain": "Entity",       "range": "Entity",      "facet": "POLITICAL"},
    "APPOINTED":          {"domain": "Entity",       "range": "Entity",      "facet": "POLITICAL"},
    "APPOINTED_BY":       {"domain": "Entity",       "range": "Entity",      "facet": "POLITICAL"},
    "CAUSED_COLLAPSE_OF": {"domain": "Entity",       "range": "Organization","facet": "POLITICAL"},
    "COLLAPSED":          {"domain": "Organization", "range": "Entity",      "facet": "POLITICAL"},
    "CONTROLLED":         {"domain": "Entity",       "range": "Place",       "facet": "POLITICAL"},
    "CONTROLLED_BY":      {"domain": "Place",        "range": "Entity",      "facet": "POLITICAL"},
    "DECLARED_FOR":       {"domain": "Entity",       "range": "Entity",      "facet": "POLITICAL"},
    "FOUNDED":            {"domain": "Person",       "range": "Organization","facet": "POLITICAL"},
    "FOUNDED_BY":         {"domain": "Organization", "range": "Person",      "facet": "POLITICAL"},
    "LED":                {"domain": "Person",       "range": "Organization","facet": "POLITICAL"},
    "LED_BY":             {"domain": "Organization", "range": "Person",      "facet": "POLITICAL"},
    "POSITION_HELD":      {"domain": "Person",       "range": "Position",    "facet": "POLITICAL"},
    "RULED":              {"domain": "Person",       "range": "Place",       "facet": "POLITICAL"},
    "RULED_BY":           {"domain": "Place",        "range": "Person",      "facet": "POLITICAL"},
    "SUCCEEDED":          {"domain": "Entity",       "range": "Entity",      "facet": "POLITICAL"},

    # ── MILITARY ─────────────────────────────────────────────────────────────
    "BATTLE_PARTICIPANT":  {"domain": "Entity",  "range": "Event",          "facet": "MILITARY"},
    "BESIEGED":            {"domain": "Entity",  "range": "Place",          "facet": "MILITARY"},
    "BESIEGED_BY":         {"domain": "Place",   "range": "Entity",         "facet": "MILITARY"},
    "CONQUERED":           {"domain": "Entity",  "range": "Place",          "facet": "MILITARY"},
    "CONQUERED_BY":        {"domain": "Place",   "range": "Entity",         "facet": "MILITARY"},
    "DEFEATED":            {"domain": "Entity",  "range": "Entity",         "facet": "MILITARY"},
    "DEFEATED_BY":         {"domain": "Entity",  "range": "Entity",         "facet": "MILITARY"},
    "KILLED":              {"domain": "Person",  "range": "Person",         "facet": "MILITARY"},
    "KILLED_BY":           {"domain": "Person",  "range": "Person",         "facet": "MILITARY"},
    "TOOK_PART_IN":        {"domain": "Entity",  "range": "Event",          "facet": "MILITARY"},

    # ── SOCIAL ────────────────────────────────────────────────────────────────
    "HAS_MEMBER":          {"domain": "Organization", "range": "Person",    "facet": "SOCIAL"},
    "MEMBER_OF":           {"domain": "Person",       "range": "Organization","facet": "SOCIAL"},
    "RELATED_TO":          {"domain": "Entity",       "range": "Entity",    "facet": "SOCIAL"},

    # ── INTELLECTUAL / WORKS ──────────────────────────────────────────────────
    "AUTHOR":              {"domain": "Person",  "range": "Work",           "facet": "INTELLECTUAL"},
    "CREATION_OF":         {"domain": "Work",    "range": "Person",         "facet": "INTELLECTUAL"},
    "CREATOR":             {"domain": "Person",  "range": "Work",           "facet": "INTELLECTUAL"},
    "SUBJECT_IN":          {"domain": "Entity",  "range": "Work",           "facet": "INTELLECTUAL"},
    "WROTE":               {"domain": "Person",  "range": "Work",           "facet": "INTELLECTUAL"},

    # ── GEOGRAPHIC ────────────────────────────────────────────────────────────
    "IN_PLACE":            {"domain": "Event",   "range": "Place",          "facet": "GEOGRAPHIC"},
    "IN_REGION":           {"domain": "Place",   "range": "Place",          "facet": "GEOGRAPHIC"},
    "LOCATED_IN":          {"domain": "Place",   "range": "Place",          "facet": "GEOGRAPHIC"},

    # ── ARCHAEOLOGICAL ───────────────────────────────────────────────────────
    "DISCOVERED_BY":       {"domain": "Entity",  "range": "Entity",         "facet": "ARCHAEOLOGICAL"},
    "INSCRIBED_IN":        {"domain": "Work",    "range": "Place",          "facet": "ARCHAEOLOGICAL"},

    # ── SECOND PASS (remaining 35) ────────────────────────────────────────────

    # Infrastructure / ADR-006 scaffold rels
    "FROM":               {"domain": "Entity",  "range": "Entity",         "facet": None},
    "TO":                 {"domain": "Entity",  "range": "Entity",         "facet": None},
    "PROMOTED_FROM":      {"domain": "Entity",  "range": "Entity",         "facet": None},
    "HAS_TRACE":          {"domain": "Claim",   "range": "Entity",         "facet": None},
    "PERFORMED":          {"domain": "Agent",   "range": "Entity",         "facet": None},
    "PRODUCED":           {"domain": "Entity",  "range": "Entity",         "facet": None},

    # Temporal
    "OCCURRED_IN_YEAR":   {"domain": "Event",   "range": "Year",           "facet": "TEMPORAL"},
    "PART_OF":            {"domain": "Entity",  "range": "Entity",         "facet": "TEMPORAL"},
    "LIVED_DURING":       {"domain": "Person",  "range": "Period",         "facet": "BIOGRAPHICAL"},

    # Biographical / Social
    "GRANDCHILD_OF":      {"domain": "Person",  "range": "Person",         "facet": "BIOGRAPHICAL"},
    "GRANDPARENT_OF":     {"domain": "Person",  "range": "Person",         "facet": "BIOGRAPHICAL"},
    "MOTHER_OF":          {"domain": "Person",  "range": "Person",         "facet": "BIOGRAPHICAL"},
    "PARENT_OF":          {"domain": "Person",  "range": "Person",         "facet": "BIOGRAPHICAL"},
    "SPOUSE_OF":          {"domain": "Person",  "range": "Person",         "facet": "SOCIAL"},
    "LIVED_IN":           {"domain": "Person",  "range": "Place",          "facet": "BIOGRAPHICAL"},
    "RESIDENCE_OF":       {"domain": "Place",   "range": "Person",         "facet": "BIOGRAPHICAL"},
    "NAMED_AFTER":        {"domain": "Entity",  "range": "Entity",         "facet": "SOCIAL"},
    "NAMESAKE_OF":        {"domain": "Entity",  "range": "Entity",         "facet": "SOCIAL"},
    "MIGRATED_FROM":      {"domain": "Entity",  "range": "Place",          "facet": "SOCIAL"},
    "MIGRATED_TO":        {"domain": "Entity",  "range": "Place",          "facet": "SOCIAL"},
    "HAS_GENS_MEMBER":    {"domain": "Organization", "range": "Person",    "facet": "SOCIAL"},

    # Military / Political
    "FOUGHT_IN":          {"domain": "Entity",  "range": "Event",          "facet": "MILITARY"},
    "HAD_PARTICIPANT":    {"domain": "Event",   "range": "Entity",         "facet": "MILITARY"},
    "PARTICIPATED_IN":    {"domain": "Entity",  "range": "Event",          "facet": "MILITARY"},
    "WITNESSED_BY":       {"domain": "Event",   "range": "Person",         "facet": "POLITICAL"},
    "WITNESSED_EVENT":    {"domain": "Person",  "range": "Event",          "facet": "POLITICAL"},
    "IDEOLOGY_OF":        {"domain": "Entity",  "range": "Entity",         "facet": "POLITICAL"},
    "LEGITIMATED":        {"domain": "Organization", "range": "Entity",    "facet": "POLITICAL"},
    "LEGITIMATED_BY":     {"domain": "Entity",  "range": "Organization",   "facet": "POLITICAL"},
    "REFORMED":           {"domain": "Entity",  "range": "Organization",   "facet": "POLITICAL"},

    # Geographic
    "LOCATION_OF":        {"domain": "Place",   "range": "Entity",         "facet": "GEOGRAPHIC"},
    "HAS_GEO_SEMANTIC_TYPE": {"domain": "Place", "range": "Entity",        "facet": "GEOGRAPHIC"},
    "INSTANCE_OF_PLACE_TYPE": {"domain": "Place", "range": "Entity",       "facet": "GEOGRAPHIC"},

    # Intellectual / Works
    "MENTIONS":           {"domain": "Work",    "range": "Entity",         "facet": "INTELLECTUAL"},
    "WORK_OF":            {"domain": "Work",    "range": "Person",         "facet": "INTELLECTUAL"},
}


def run():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    patched = 0
    skipped = 0
    not_found = 0

    with driver.session() as s:
        for rel_type, ann in ANNOTATIONS.items():
            result = s.run(
                """
                MATCH (r:SYS_RelationshipType {rel_type: $rt})
                WITH r
                WHERE r.domain IS NULL
                SET r.domain = $domain,
                    r.range  = $range,
                    r.facet  = $facet
                RETURN r.rel_type AS rt
                """,
                rt=rel_type,
                domain=ann["domain"],
                range=ann["range"],
                facet=ann["facet"],
            )
            rec = result.single()
            if rec:
                patched += 1
                facet_str = ann["facet"] or "None"
                print(f"  PATCH  {rel_type:<30} {ann['domain']:<15} -> {ann['range']:<20} [{facet_str}]")
            else:
                # Either not in graph, or already had domain
                check = s.run(
                    "MATCH (r:SYS_RelationshipType {rel_type: $rt}) RETURN r.domain AS d",
                    rt=rel_type
                ).single()
                if check is None:
                    not_found += 1
                    print(f"  SKIP   {rel_type:<30} (not in graph)")
                else:
                    skipped += 1
                    print(f"  EXIST  {rel_type:<30} (already has domain='{check['d']}')")

    print(f"\nDone: {patched} patched, {skipped} already set, {not_found} not found in graph")
    driver.close()


if __name__ == "__main__":
    run()
