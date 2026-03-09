#!/usr/bin/env python3
"""
Link Discipline nodes to LCC_Class nodes via HAS_LCC_CLASS relationship.

Strategy:
1. For each Discipline with lcc, extract prefix (letters) from first code
2. Match LCC_Class nodes with same prefix
3. Find the tightest-fitting range that contains the discipline's LCC code
4. Create HAS_LCC_CLASS relationship
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase


def extract_prefix(code):
    """Extract letter prefix from LCC code: 'QH541.5' -> 'QH'"""
    m = re.match(r'^([A-Z]+)', code.strip())
    return m.group(1) if m else None


def extract_number(code):
    """Extract first numeric value from LCC code: 'QH541.5' -> 541.5"""
    m = re.match(r'^[A-Z]+(\d+(?:\.\d+)?)', code.strip())
    if m:
        return float(m.group(1))
    return None


def parse_lcc_range(code_str):
    """Parse LCC_Class code like 'QH540-549.5' into (prefix, start, end).
    Also handles 'QH540-QH549.5', 'QH1-(199.5)', single codes like 'QH332'."""
    code_str = code_str.strip().replace('(', '').replace(')', '')

    # Try range: PREFIX_NUM-NUM or PREFIX_NUM-PREFIX_NUM
    m = re.match(r'^([A-Z]+)(\d+(?:\.\d+)?)\s*-\s*(?:[A-Z]+)?(\d+(?:\.\d+)?)$', code_str)
    if m:
        return m.group(1), float(m.group(2)), float(m.group(3))

    # Single code: PREFIX_NUM
    m = re.match(r'^([A-Z]+)(\d+(?:\.\d+)?)$', code_str)
    if m:
        return m.group(1), float(m.group(2)), float(m.group(2))

    # Just prefix: 'N', 'QB'
    m = re.match(r'^([A-Z]+)$', code_str)
    if m:
        return m.group(1), 0, 99999

    return None, None, None


def find_best_match(disc_lcc, lcc_classes_by_prefix):
    """Find the tightest LCC_Class range containing the discipline's LCC code."""
    # Take first code if pipe-separated
    first_code = disc_lcc.split('|')[0].strip()

    # Handle range: take start of range
    if '-' in first_code:
        parts = first_code.split('-')
        first_code = parts[0].strip()

    prefix = extract_prefix(first_code)
    if not prefix:
        return None

    num = extract_number(first_code)

    candidates = lcc_classes_by_prefix.get(prefix, [])
    if not candidates:
        return None

    # If no number (just prefix like "N"), match broadest range
    if num is None:
        broadest = max(candidates, key=lambda c: c['end'] - c['start'])
        return broadest

    # Find all ranges that contain this number
    containing = []
    for c in candidates:
        if c['start'] <= num <= c['end']:
            containing.append(c)

    if not containing:
        # Try exact match on start number
        for c in candidates:
            if c['start'] == num:
                containing.append(c)

    if not containing:
        return None

    # Pick tightest range (smallest span)
    best = min(containing, key=lambda c: c['end'] - c['start'])
    return best


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Load all LCC_Class nodes
        result = session.run("MATCH (n:LCC_Class) RETURN n.code as code, n.label as label, n.prefix as prefix, elementId(n) as eid")
        lcc_classes = []
        for record in result:
            code = record["code"]
            prefix_parsed, start, end = parse_lcc_range(code)
            if prefix_parsed:
                lcc_classes.append({
                    "code": code,
                    "label": record["label"],
                    "prefix": prefix_parsed,
                    "start": start,
                    "end": end,
                    "eid": record["eid"],
                })
        print(f"Loaded {len(lcc_classes)} LCC_Class nodes")

        # Index by prefix
        by_prefix = {}
        for c in lcc_classes:
            by_prefix.setdefault(c["prefix"], []).append(c)

        # 2. Load disciplines with LCC
        result = session.run("MATCH (d:Discipline) WHERE d.lcc IS NOT NULL AND d.lcc <> '' RETURN d.qid as qid, d.label as label, d.lcc as lcc")
        disciplines = []
        for record in result:
            disciplines.append({"qid": record["qid"], "label": record["label"], "lcc": record["lcc"]})
        print(f"Disciplines with LCC: {len(disciplines)}")

        # 3. Match and create relationships
        matched = 0
        unmatched = []
        for disc in disciplines:
            best = find_best_match(disc["lcc"], by_prefix)
            if best:
                session.run("""
                    MATCH (d:Discipline {qid: $qid})
                    MATCH (lcc:LCC_Class {code: $lcc_code})
                    MERGE (d)-[:HAS_LCC_CLASS]->(lcc)
                """, qid=disc["qid"], lcc_code=best["code"])
                matched += 1
                print(f"  {disc['label']:40s} {disc['lcc']:25s} -> {best['code']:20s} {best['label']}")
            else:
                unmatched.append(disc)

        print(f"\nMatched: {matched}/{len(disciplines)}")
        if unmatched:
            print(f"Unmatched ({len(unmatched)}):")
            for d in unmatched:
                print(f"  {d['label']:40s} {d['lcc']}")

        # 4. Verify
        result = session.run("MATCH (:Discipline)-[r:HAS_LCC_CLASS]->(:LCC_Class) RETURN count(r) as count")
        print(f"\nFinal: {result.single()['count']} HAS_LCC_CLASS relationships")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
