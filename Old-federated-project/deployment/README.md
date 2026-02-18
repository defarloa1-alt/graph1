# Enhanced Federated Graph Framework - Production Deployment

## Quick Start

1. **Environment Setup**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

2. **Docker Deployment**
   ```bash
   cd deployment/docker
   ./scripts/deploy.sh
   ```

3. **Kubernetes Deployment**
   ```bash
   cd deployment/kubernetes
   kubectl apply -f namespace.yaml
   kubectl apply -f configmap.yaml
   kubectl apply -f secret.yaml
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   kubectl apply -f ingress.yaml
   ```

## Services

- **Framework API**: http://localhost:8080
- **Governance Dashboard**: http://localhost:8081
- **Prometheus Monitoring**: http://localhost:9090
- **Grafana Dashboards**: http://localhost:3000

## Validation

Run comprehensive validation:
```bash
./scripts/validate-deployment.sh
```

## Monitoring

- Prometheus metrics at `/metrics`
- Grafana dashboards for visualization
- Health checks at `/health` and `/ready`
- Log aggregation in `/app/logs`

## Security

- TLS/SSL encryption enabled
- API key authentication required
- Rate limiting configured
- Security scanning with Bandit

## Compliance

- SOC2 Type II compliance
- GDPR Article 25 compliance
- ISO 27001:2013 compliance
- NIST Cybersecurity Framework compliance

## Support

For technical support, contact: framework-team@company.com
