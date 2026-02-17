"""
Verify Pleiades Import to Neo4j
================================

Runs test queries from PLEIADES_QUICK_START.md to verify import succeeded.
"""

import sys
from pathlib import Path
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class PleiadesVerifier:
    """Verify Pleiades import with test queries."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def test_find_rome(self):
        """Test 1: Find Rome."""
        logger.info("\n[Test 1] Finding Rome...")
        
        query = """
        MATCH (p:Place) 
        WHERE p.label CONTAINS 'Rom' AND p.authority = 'Pleiades'
        RETURN p.pleiades_id, p.label, p.lat, p.long, p.min_date, p.max_date
        LIMIT 5
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            count = 0
            for record in result:
                count += 1
                logger.info(f"  ✓ {record['p.label']} (ID: {record['p.pleiades_id']})")
                logger.info(f"    Coords: ({record['p.lat']}, {record['p.long']})")
                logger.info(f"    Dates: {record['p.min_date']} to {record['p.max_date']}")
            
            if count > 0:
                logger.info(f"  ✅ PASS: Found {count} places matching 'Rom'")
                return True
            else:
                logger.error("  ❌ FAIL: No places found matching 'Rom'")
                return False
    
    def test_greek_names(self):
        """Test 2: Places with Greek names."""
        logger.info("\n[Test 2] Finding places with Greek names...")
        
        query = """
        MATCH (p:Place)-[:HAS_NAME]->(n:PlaceName)
        WHERE n.language = 'grc'
        RETURN p.label, n.name_attested, n.romanized
        LIMIT 10
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            count = 0
            for record in result:
                count += 1
                logger.info(f"  ✓ {record['p.label']}: {record['n.name_attested']} ({record['n.romanized']})")
            
            if count > 0:
                logger.info(f"  ✅ PASS: Found {count} Greek names")
                return True
            else:
                logger.warning("  ⚠️  WARN: No Greek names found (HAS_NAME relationships may not be created)")
                return False
    
    def test_italy_bounding_box(self):
        """Test 3: Places in Italy (bounding box)."""
        logger.info("\n[Test 3] Finding places in Italy (bounding box)...")
        
        query = """
        MATCH (p:Place)
        WHERE p.lat > 36 AND p.lat < 47
          AND p.long > 6 AND p.long < 19
          AND p.authority = 'Pleiades'
        RETURN p.label, p.place_type, p.lat, p.long
        LIMIT 10
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            count = 0
            for record in result:
                count += 1
                logger.info(f"  ✓ {record['p.label']} ({record['p.place_type']}) - ({record['p.lat']}, {record['p.long']})")
            
            if count > 0:
                logger.info(f"  ✅ PASS: Found {count} places in Italy bounding box")
                return True
            else:
                logger.error("  ❌ FAIL: No places found in Italy bounding box")
                return False
    
    def test_ancient_places(self):
        """Test 4: Ancient places (before 500 CE)."""
        logger.info("\n[Test 4] Finding ancient places (before 500 CE)...")
        
        query = """
        MATCH (p:Place)
        WHERE p.max_date IS NOT NULL AND p.max_date < 500
          AND p.authority = 'Pleiades'
        RETURN p.label, p.min_date, p.max_date, p.place_type
        ORDER BY p.min_date
        LIMIT 10
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            count = 0
            for record in result:
                count += 1
                logger.info(f"  ✓ {record['p.label']} ({record['p.place_type']}) - {record['p.min_date']} to {record['p.max_date']}")
            
            if count > 0:
                logger.info(f"  ✅ PASS: Found {count} ancient places")
                return True
            else:
                logger.error("  ❌ FAIL: No ancient places found")
                return False
    
    def test_statistics(self):
        """Test 5: Statistics."""
        logger.info("\n[Test 5] Collecting statistics...")
        
        queries = {
            "Total places": "MATCH (p:Place {authority: 'Pleiades'}) RETURN count(p) as count",
            "Places with coordinates": "MATCH (p:Place {authority: 'Pleiades'}) WHERE p.lat IS NOT NULL RETURN count(p) as count",
            "Places with temporal bounds": "MATCH (p:Place {authority: 'Pleiades'}) WHERE p.min_date IS NOT NULL RETURN count(p) as count",
            "Place types": "MATCH (p:Place {authority: 'Pleiades'}) WHERE p.place_type <> '' RETURN count(DISTINCT p.place_type) as count",
        }
        
        all_passed = True
        with self.driver.session() as session:
            for label, query in queries.items():
                result = session.run(query)
                count = result.single()["count"]
                logger.info(f"  ✓ {label}: {count:,}")
                
                if label == "Total places" and count < 40000:
                    logger.warning(f"    ⚠️  Expected ~42,000 places, got {count:,}")
                    all_passed = False
        
        if all_passed:
            logger.info("  ✅ PASS: Statistics look good")
        return all_passed
    
    def test_specific_places(self):
        """Test 6: Find specific well-known places."""
        logger.info("\n[Test 6] Finding well-known ancient places...")
        
        places_to_find = [
            "Athens",
            "Sparta",
            "Alexandria",
            "Carthage",
            "Roma"
        ]
        
        found = 0
        for place_name in places_to_find:
            query = """
            MATCH (p:Place {authority: 'Pleiades'})
            WHERE p.label CONTAINS $name
            RETURN p.label, p.pleiades_id
            LIMIT 1
            """
            
            with self.driver.session() as session:
                result = session.run(query, name=place_name)
                record = result.single()
                if record:
                    logger.info(f"  ✓ Found {record['p.label']} (ID: {record['p.pleiades_id']})")
                    found += 1
                else:
                    logger.warning(f"  ⚠️  Could not find {place_name}")
        
        if found >= 4:
            logger.info(f"  ✅ PASS: Found {found}/{len(places_to_find)} well-known places")
            return True
        else:
            logger.error(f"  ❌ FAIL: Only found {found}/{len(places_to_find)} places")
            return False

def main():
    """Run all verification tests."""
    logger.info("=" * 70)
    logger.info("Pleiades Import Verification")
    logger.info("=" * 70)
    
    verifier = PleiadesVerifier(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    try:
        results = []
        
        # Run all tests
        results.append(("Find Rome", verifier.test_find_rome()))
        results.append(("Greek names", verifier.test_greek_names()))
        results.append(("Italy bounding box", verifier.test_italy_bounding_box()))
        results.append(("Ancient places", verifier.test_ancient_places()))
        results.append(("Statistics", verifier.test_statistics()))
        results.append(("Well-known places", verifier.test_specific_places()))
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("Test Summary")
        logger.info("=" * 70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"  {status}: {test_name}")
        
        logger.info("=" * 70)
        logger.info(f"Results: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("✅ All tests passed! Pleiades import verified.")
        elif passed >= total - 1:
            logger.info("⚠️  Most tests passed. Check warnings above.")
        else:
            logger.error("❌ Multiple tests failed. Review import.")
        
        logger.info("=" * 70)
        
        return passed == total
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        verifier.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
