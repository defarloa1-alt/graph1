#!/bin/bash
set -e

echo "=== Comprehensive Deployment Validation ==="

# Run CI validation
echo "1. Running CI validation framework..."
docker-compose exec framework-api python ci_validation_framework.py

# Run automated tests
echo "2. Running automated test suite..."
docker-compose exec framework-api python automated_test_framework.py

# Run compliance validation
echo "3. Running compliance validation..."
docker-compose exec framework-api python compliance_validation_system.py

# Run regression tests
echo "4. Running regression tests..."
docker-compose exec framework-api python regression_testing_system.py

# Generate reports
echo "5. Generating test reports..."
docker-compose exec framework-api python test_reporting_system.py

# Commercial readiness assessment
echo "6. Running commercial readiness assessment..."
docker-compose exec framework-api python commercial_readiness_assessment.py

echo ""
echo "=== Validation Complete ==="
echo "Check the reports/ directory for detailed results"
