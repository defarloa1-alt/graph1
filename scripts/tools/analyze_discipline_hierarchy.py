#!/usr/bin/env python3
"""Analyze hierarchy structure of the 970 authority-linked disciplines."""
import csv

rows = []
with open("c:/Projects/Graph1/Disciplines/disciplines_with_authority.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append(r)

qid_set = set(r["qid"] for r in rows)
by_qid = {r["qid"]: r for r in rows}
print(f"Total: {len(rows)}")

# Build parent relationships (only within the 970)
children_of = {}
parent_of = {}
has_parent_in_set = 0
orphans = 0
no_parent = 0

for r in rows:
    parents = [p.strip() for p in (r["subclass_of"] or "").split("|") if p.strip()]
    placed = False
    for p in parents:
        if p in qid_set and p != r["qid"]:
            children_of.setdefault(p, []).append(r["qid"])
            parent_of[r["qid"]] = p
            has_parent_in_set += 1
            placed = True
            break
    if not placed:
        if parents:
            orphans += 1
        else:
            no_parent += 1

# Find roots
all_children = set()
for kids in children_of.values():
    all_children.update(kids)
roots = [r["qid"] for r in rows if r["qid"] not in all_children]

# Tree depth
def depth(qid, seen=None):
    if seen is None:
        seen = set()
    if qid in seen:
        return 0
    seen.add(qid)
    kids = children_of.get(qid, [])
    if not kids:
        return 0
    return 1 + max(depth(k, seen) for k in kids)

max_d = max(depth(q) for q in roots) if roots else 0

# In-tree vs isolated
in_tree = all_children | set(q for q in qid_set if children_of.get(q))
isolated = qid_set - in_tree

root_items = [(q, by_qid[q]["label"], len(children_of.get(q, []))) for q in roots]
root_items.sort(key=lambda x: -x[2])

print(f"\nHierarchy stats:")
print(f"  Has parent in set:    {has_parent_in_set}")
print(f"  Orphan (parent outside set): {orphans}")
print(f"  No P279 parent:       {no_parent}")
print(f"  Root nodes:           {len(roots)}")
print(f"  Max tree depth:       {max_d}")
print(f"  In tree (parent or child): {len(in_tree)}")
print(f"  Isolated (leaf, no parent in set): {len(isolated)}")

print(f"\nTop 30 roots by child count:")
for qid, label, cc in root_items[:30]:
    print(f"  {qid:12s} {label:45s} [{cc} children]")

# External parents
external_parents = {}
for r in rows:
    parents = [p.strip() for p in (r["subclass_of"] or "").split("|") if p.strip()]
    for p in parents:
        if p not in qid_set:
            pl = (r.get("subclass_of_label") or "").split("|")
            pi = [x.strip() for x in (r["subclass_of"] or "").split("|")]
            idx = pi.index(p) if p in pi else -1
            plabel = pl[idx].strip() if idx >= 0 and idx < len(pl) else p
            external_parents.setdefault((p, plabel), []).append(r["label"])

ext_sorted = sorted(external_parents.items(), key=lambda x: -len(x[1]))
print(f"\nExternal parents (outside the 970) — {len(external_parents)} unique:")
print(f"Top 30:")
for (pqid, plabel), kids in ext_sorted[:30]:
    print(f"  {pqid:12s} {plabel:40s} [{len(kids)} children]")
