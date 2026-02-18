#!/bin/bash
set -e

echo "=== Enhanced Federated Graph Framework Deployment ==="
echo "Environment: ${ENVIRONMENT:-production}"
echo "Version: ${VERSION:-latest}"
echo ""

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

# Validate required environment variables
required_vars=("DB_PASSWORD" "GRAFANA_PASSWORD" "API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

# Build and deploy
echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 30

# Health checks
echo "Running health checks..."
./scripts/health-check.sh

echo "Running deployment validation..."
docker-compose exec framework-api python deployment_automation_system.py --validate

echo ""
echo "=== Deployment Complete ==="
echo "Framework API: http://localhost:8080"
echo "Governance Dashboard: http://localhost:8081"
echo "Grafana Monitoring: http://localhost:3000"
echo "Prometheus Metrics: http://localhost:9090"
echo ""
echo "Run './scripts/validate-deployment.sh' to perform comprehensive validation"
