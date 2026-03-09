#!/usr/bin/env python3
"""
Dump the academic discipline taxonomy from Wikidata as a markdown tree.
Uses P31 (instance of) to filter to actual disciplines, P279 (subclass of) for hierarchy.
No P527 expansion — that pulls in non-discipline junk.
"""
import requests
import time

SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "ChrystallumBot/1.0 (research project)"
OUTPUT = "output/discipline_taxonomy_tree.md"
AUTH_PROPS = {"P244": "lcsh_id", "P2163": "fast_id", "P227": "gnd_id", "P1149": "lcc", "P1036": "ddc"}


def sparql_query(sparql):
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    for attempt in range(3):
        r = requests.get(SPARQL_URL, params={"query": sparql}, headers=headers, timeout=120)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            time.sleep((attempt + 1) * 10)
        else:
            time.sleep(5)
    return None


def main():
    # 1. All academic disciplines + fields of study, with P279 parent
    print("1. Fetching disciplines from Wikidata...")
    data = sparql_query("""
        SELECT ?item ?itemLabel ?parent ?parentLabel WHERE {
          { ?item wdt:P31 wd:Q11862829 . }
          UNION
          { ?item wdt:P31 wd:Q2267705 . }
          OPTIONAL { ?item wdt:P279 ?parent . }
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
    """)
    if not data:
        print("SPARQL failed")
        return

    bindings = data["results"]["bindings"]
    print(f"  {len(bindings)} bindings")

    items = {}
    for b in bindings:
        uri = b.get("item", {}).get("value", "")
        qid = uri.split("/")[-1]
        label = b.get("itemLabel", {}).get("value", "")
        if label.startswith("http://"):
            label = ""
        parent_uri = b.get("parent", {}).get("value", "")
        parent_qid = parent_uri.split("/")[-1] if parent_uri else ""
        parent_label = b.get("parentLabel", {}).get("value", "")
        if parent_label.startswith("http://"):
            parent_label = ""

        if qid not in items:
            items[qid] = {"qid": qid, "label": label or qid, "parents": []}
        if parent_qid and parent_qid not in [p for p, _ in items[qid]["parents"]]:
            items[qid]["parents"].append((parent_qid, parent_label or parent_qid))

    print(f"  {len(items)} unique disciplines")

    # 2. Fetch authority IDs in batches
    print("2. Fetching authority IDs...")
    all_qids = list(items.keys())
    for i in range(0, len(all_qids), 50):
        batch = all_qids[i : i + 50]
        try:
            r = requests.get(
                WIKIDATA_API,
                params={"action": "wbgetentities", "ids": "|".join(batch), "props": "claims", "format": "json"},
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            if r.status_code == 200:
                entities = r.json().get("entities", {})
                for qid, ent in entities.items():
                    if qid not in items:
                        continue
                    claims = ent.get("claims", {})
                    for pid, col in AUTH_PROPS.items():
                        cl = claims.get(pid, [])
                        vals = []
                        for c in cl:
                            snak = c.get("mainsnak", {})
                            if snak.get("snaktype") == "value":
                                v = snak["datavalue"]["value"]
                                if isinstance(v, str):
                                    vals.append(v)
                        if vals:
                            items[qid][col] = "|".join(vals)
        except Exception as e:
            print(f"  Error batch {i}: {e}")
        time.sleep(0.3)
        if (i // 50) % 20 == 0 and i > 0:
            print(f"  batch {i // 50}/{len(all_qids) // 50}")

    # 3. Build tree — add synthetic parents for items whose P279 target is outside the set
    qid_set = set(items.keys())
    ext_parents = {}
    for item in items.values():
        for pq, pl in item["parents"]:
            if pq not in qid_set and pq not in ext_parents:
                ext_parents[pq] = pl

    for pq, pl in ext_parents.items():
        items[pq] = {"qid": pq, "label": pl, "parents": [], "synthetic": True}

    children_of = {}
    parent_of = {}
    for item in items.values():
        for pq, _ in item.get("parents", []):
            if pq in items and pq != item["qid"]:
                children_of.setdefault(pq, []).append(item["qid"])
                parent_of[item["qid"]] = pq
                break

    roots = sorted(
        [q for q in items if q not in parent_of],
        key=lambda q: items[q]["label"].lower(),
    )
    for k in children_of:
        children_of[k].sort(key=lambda q: items[q]["label"].lower())

    # Stats
    total_real = sum(1 for v in items.values() if not v.get("synthetic"))
    has_lcsh = sum(1 for v in items.values() if v.get("lcsh_id") and not v.get("synthetic"))
    has_lcc = sum(1 for v in items.values() if v.get("lcc") and not v.get("synthetic"))
    has_gnd = sum(1 for v in items.values() if v.get("gnd_id") and not v.get("synthetic"))
    has_fast = sum(1 for v in items.values() if v.get("fast_id") and not v.get("synthetic"))

    # 4. Write markdown
    lines = []
    lines.append("# Chrystallum Discipline Taxonomy")
    lines.append("")
    lines.append("**Source:** Wikidata SPARQL (live query)")
    lines.append("**Filter:** `?item wdt:P31 wd:Q11862829` (academic discipline) UNION `?item wdt:P31 wd:Q2267705` (field of study)")
    lines.append("**Hierarchy:** P279 (subclass of) only — no P527 expansion")
    lines.append("**Authority IDs:** P244 (LCSH), P2163 (FAST), P227 (GND), P1149 (LCC), P1036 (DDC)")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Disciplines | {total_real} |")
    lines.append(f"| Have LCSH | {has_lcsh} |")
    lines.append(f"| Have LCC | {has_lcc} |")
    lines.append(f"| Have GND | {has_gnd} |")
    lines.append(f"| Have FAST | {has_fast} |")
    lines.append(f"| Synthetic parents (not disciplines) | {len(ext_parents)} |")
    lines.append(f"| Root nodes | {len(roots)} |")
    lines.append("")

    def badges(qid):
        r = items[qid]
        parts = []
        if r.get("lcsh_id"):
            parts.append(f'LCSH:`{r["lcsh_id"]}`')
        if r.get("lcc"):
            parts.append(f'LCC:`{r["lcc"]}`')
        if r.get("gnd_id"):
            parts.append(f'GND:`{r["gnd_id"]}`')
        if r.get("fast_id"):
            parts.append(f'FAST:`{r["fast_id"]}`')
        if r.get("ddc"):
            parts.append(f'DDC:`{r["ddc"]}`')
        return " ".join(parts)

    def print_tree(qid, depth, max_depth=8):
        r = items[qid]
        indent = "    " * depth
        b = badges(qid)
        b_str = f"  {b}" if b else ""
        synth = " *(structural parent — not itself a discipline)*" if r.get("synthetic") else ""
        child_count = len(children_of.get(qid, []))
        cc = f" **[{child_count}]**" if child_count > 0 else ""
        lines.append(f'{indent}- **{r["label"]}** `{qid}`{cc}{synth}{b_str}')
        if depth < max_depth:
            for kid in children_of.get(qid, []):
                print_tree(kid, depth + 1, max_depth)

    big_roots = [q for q in roots if len(children_of.get(q, [])) > 0]
    leaf_roots = [q for q in roots if len(children_of.get(q, [])) == 0]

    lines.append("## Taxonomy Tree")
    lines.append("")
    for qid in big_roots:
        print_tree(qid, 0)
        lines.append("")

    if leaf_roots:
        # Split into real disciplines and synthetic
        real_leaves = [q for q in leaf_roots if not items[q].get("synthetic")]
        synth_leaves = [q for q in leaf_roots if items[q].get("synthetic")]

        lines.append(f"## Leaf Disciplines ({len(real_leaves)} — no sub-disciplines)")
        lines.append("")
        for qid in real_leaves:
            b = badges(qid)
            lines.append(f'- **{items[qid]["label"]}** `{qid}`  {b}')

        if synth_leaves:
            lines.append("")
            lines.append(f"## Structural Parents ({len(synth_leaves)} — not disciplines, no children in set)")
            lines.append("")
            for qid in synth_leaves:
                lines.append(f'- {items[qid]["label"]} `{qid}`')

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nWrote {len(lines)} lines to {OUTPUT}")
    print(f"Tree roots with children: {len(big_roots)}")
    print(f"Leaf disciplines: {len(real_leaves)}")


if __name__ == "__main__":
    main()
