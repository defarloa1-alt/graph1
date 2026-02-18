#!/bin/bash
set -e

echo "Running health checks..."

# Check if services are running
services=("framework-api" "governance-dashboard" "framework-postgres" "framework-redis")
for service in "${services[@]}"; do
    if docker ps | grep -q "$service"; then
        echo "✅ $service: Running"
    else
        echo "❌ $service: Not running"
        exit 1
    fi
done

# Check HTTP endpoints
endpoints=(
    "http://localhost:8080/health:Framework API"
    "http://localhost:8081:Governance Dashboard"
    "http://localhost:9090:Prometheus"
    "http://localhost:3000:Grafana"
)

for endpoint in "${endpoints[@]}"; do
    url=$(echo $endpoint | cut -d: -f1-2)
    name=$(echo $endpoint | cut -d: -f3)
    
    if curl -f -s "$url" > /dev/null; then
        echo "✅ $name: Healthy"
    else
        echo "❌ $name: Unhealthy"
        exit 1
    fi
done

echo ""
echo "All health checks passed!"
