#!/usr/bin/env python3
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum'))
session = driver.session()

try:
    constraints = session.run('SHOW CONSTRAINTS').data()
    print("Current constraints:")
    for c in constraints:
        print(f"  {c}")
finally:
    session.close()
    driver.close()
