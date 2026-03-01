// Fix LCC BROADER_THAN direction: was (narrower)->(broader), should be (broader)->(narrower)
// 1. Run this to delete existing LCC BROADER_THAN edges
// 2. Re-run: python scripts/backbone/subject/load_lcc_nodes.py --survey output/nodes/lcc_full.json

MATCH (a:LCC_Class)-[r:BROADER_THAN]->(b:LCC_Class)
DELETE r;
