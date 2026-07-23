# StreamSentinel - AI Operations Platform with E-commerce

A production-ready AI-powered Kubernetes Operations Platform integrated with a comprehensive E-commerce system.

## Features

### E-commerce
- ✅ Product Management (CRUD, Search, Filtering)
- ✅ Shopping Cart & Wishlist
- ✅ User Reviews & Ratings
- ✅ Orders & Payments
- ✅ Inventory Management
- ✅ Coupons & Discounts
- 🆕 Order Returns & Refunds
- 🆕 Shipping Management
- 🆕 Multiple Addresses
- 🆕 Sales Dashboard & Analytics
- 🆕 Customer Segmentation
- 🆕 AI Product Recommendations

### Kubernetes Operations & Monitoring
- ✅ Real-time Kubernetes Cluster Monitoring
- ✅ Pod, Deployment, Node, and Service Management
- ✅ Metrics Collection (CPU, Memory, Disk, Network)
- ✅ Log Collection & Analysis
- ✅ Alert Rules Engine
- ✅ Incident Management
- ✅ AI-powered Root Cause Analysis (RCA)
- ✅ Knowledge Base
- ✅ AI Chat for Operations
- ✅ Prometheus Integration
- ✅ Grafana Dashboards
- ✅ Event Tracking

### Authentication & Security
- ✅ JWT Authentication
- ✅ OAuth2 Integration
- ✅ Role-Based Access Control (Admin, User)
- ✅ Email Verification
- ✅ Password Hashing with Bcrypt

## Project Structure

```
StreamSentinel/
├── shopping-backend/          # FastAPI Backend
│   ├── app/
│   │   ├── api/              # API Routes
│   │   │   ├── auth_api.py
│   │   │   ├── product_api.py
│   │   │   ├── order_api.py
│   │   │   ├── kubernetes_api.py
│   │   │   ├── alert_api.py
│   │   │   ├── ai_chat_api.py
│   │   │   ├── ecommerce_extension_api.py
│   │   │   └── ...
│   │   ├── services/         # Business Logic
│   │   │   ├── kubernetes_service.py
│   │   │   ├── prometheus_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── alert_engine.py
│   │   │   └── ...
│   │   ├── database/         # ORM Models
│   │   │   ├── kubernetes_model.py
│   │   │   ├── alert_model.py
│   │   │   ├── ecommerce_extension_model.py
│   │   │   ├── models.py
│   │   │   ├── user_model.py
│   │   │   ├── order_model.py
│   │   │   └── ...
│   │   ├── schemas/          # Pydantic Schemas
│   │   ├── auth/             # Authentication
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── shopping-frontend/        # React Frontend
├── k8s/                      # Kubernetes Manifests
│   ├── 01-backend-deployment.yaml
│   ├── 02-postgres-deployment.yaml
│   ├── 03-prometheus-deployment.yaml
│   ├── 04-grafana-deployment.yaml
│   └── 05-ingress.yaml
├── monitoring/               # Monitoring Configuration
│   ├── prometheus.yml
│   ├── alert_rules.yml
│   └── grafana/
└── docker-compose.yml        # Local Development
```

## Quick Start

### 1. Local Development with Docker Compose

```bash
cd StreamSentinel

# Create .env file
cp shopping-backend/.env.example shopping-backend/.env

# Update .env with your configuration
# OPENAI_API_KEY=sk-xxx

# Start all services
docker-compose up -d

# Wait for services to be ready
docker-compose logs -f

# Database migrations
docker exec streamsentinel-backend alembic upgrade head

# Access services
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

### 2. Kubernetes Deployment

```bash
# Build Docker image
cd shopping-backend
docker build -t streamsentinel-backend:latest .
docker tag streamsentinel-backend:latest <your-registry>/streamsentinel-backend:latest
docker push <your-registry>/streamsentinel-backend:latest

# Create namespaces and deploy
cd ../k8s
kubectl apply -f 01-backend-deployment.yaml
kubectl apply -f 02-postgres-deployment.yaml
kubectl apply -f 03-prometheus-deployment.yaml
kubectl apply -f 04-grafana-deployment.yaml
kubectl apply -f 05-ingress.yaml

# Verify deployments
kubectl get deployments -n streamsentinel
kubectl get pods -n streamsentinel
kubectl get svc -n streamsentinel

# Check logs
kubectl logs -f deployment/streamsentinel-backend -n streamsentinel
```

### 3. Running Backend Locally

```bash
cd shopping-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

### Authentication
```bash
# Register
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "password123"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### E-commerce
```bash
# Get products
GET /api/products

# Create order
POST /api/orders
{
  "items": [{"product_id": 1, "quantity": 2}],
  "shipping_address_id": 1
}

# Track order
GET /api/orders/{order_id}

# Request return
POST /api/orders/{order_id}/returns
{
  "reason": "Product is defective",
  "description": "Product stopped working after 2 days",
  "quantity": 1
}
```

### Kubernetes Management
```bash
# Get clusters
GET /api/kubernetes/clusters

# Register cluster
POST /api/kubernetes/clusters
{
  "name": "production",
  "context": "production-context",
  "api_server": "https://api.example.com"
}

# Sync cluster data
POST /api/kubernetes/clusters/{cluster_id}/sync

# Get pods
GET /api/kubernetes/clusters/{cluster_id}/pods

# Get deployments
GET /api/kubernetes/clusters/{cluster_id}/deployments
```

### Alerts & Incidents
```bash
# Get alert rules
GET /api/alerts/rules

# Create alert rule
POST /api/alerts/rules
{
  "name": "High CPU Usage",
  "rule_type": "cpu_usage",
  "metric_name": "cpu",
  "operator": ">",
  "threshold": 90,
  "severity": "CRITICAL"
}

# Get incidents
GET /api/alerts/incidents

# Update incident
PUT /api/alerts/incidents/{incident_id}
{
  "status": "IN_PROGRESS",
  "assigned_to": "admin@example.com"
}

# Generate AI RCA
POST /api/alerts/incidents/{incident_id}/rcas/ai-generate
{
  "logs": "container logs here"
}
```

### AI Chat
```bash
# Create chat
POST /api/ai/chats
{
  "title": "Debugging Pod Crash",
  "context": {"namespace": "default", "pod_name": "api-server"}
}

# Send message
POST /api/ai/chats/{chat_id}/messages
{
  "role": "user",
  "content": "Why did my pod crash?"
}
```

### Sales Dashboard
```bash
# Get sales metrics
GET /api/dashboard/sales

# Get customer analytics
GET /api/dashboard/customers
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-xxx

# Kubernetes
KUBERNETES_CONTEXT=docker-desktop
KUBECONFIG_PATH=/path/to/kubeconfig

# Prometheus
PROMETHEUS_URL=http://localhost:9090

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=app-password
```

## Admin Features

1. **User Management**: Create, update, delete users, manage roles
2. **Product Management**: CRUD operations, inventory tracking
3. **Order Management**: View orders, process returns, manage refunds
4. **Kubernetes Monitoring**: Register clusters, sync data, view metrics
5. **Alert Management**: Create alert rules, manage incidents
6. **Analytics Dashboard**: Sales metrics, customer analytics, trends
7. **Knowledge Base**: Create articles, manage documentation
8. **AI Analysis**: Generate RCA, analyze logs, suggest solutions

## User Features

1. **Shopping**: Browse products, search, filter by category
2. **Cart & Wishlist**: Add items, manage cart
3. **Checkout**: Multiple addresses, payment options
4. **Orders**: View order history, track shipping, request returns
5. **Reviews**: Leave reviews and ratings
6. **Notifications**: Order updates, shipment tracking
7. **Profile**: Manage addresses, view wishlist
8. **Recommendations**: AI-powered product suggestions

## Monitoring & Metrics

### Prometheus Metrics
- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request duration
- `http_requests_errors_total`: Total errors
- `pod_cpu_usage_seconds_total`: Pod CPU usage
- `pod_memory_usage_bytes`: Pod memory usage
- `node_memory_MemAvailable_bytes`: Node memory available
- `node_filesystem_avail_bytes`: Node disk space available

### Grafana Dashboards
- Kubernetes Cluster Status
- Pod Performance
- Deployment Health
- Node Metrics
- HTTP Request Metrics
- Error Rates

## Alert Rules

Predefined alert rules:
- **Critical**: Node not ready, pod OOM killed, disk full
- **High**: Pod crash looping, deployment down
- **Medium**: High CPU usage, high memory usage
- **Low**: Pod pending, deployment replicas mismatch

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_auth.py -v
```

## Deployment Checklist

- [ ] Update `.env` with production values
- [ ] Set `DEBUG=False`
- [ ] Configure database URL
- [ ] Set `SECRET_KEY` to strong random value
- [ ] Configure OpenAI API key
- [ ] Set up email credentials
- [ ] Configure Kubernetes context
- [ ] Update ALLOWED_ORIGINS for CORS
- [ ] Build Docker images
- [ ] Push images to registry
- [ ] Update image references in Kubernetes manifests
- [ ] Deploy to Kubernetes cluster
- [ ] Verify all services are running
- [ ] Configure monitoring and alerts
- [ ] Set up backups for database
- [ ] Configure ingress certificates

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker logs streamsentinel-backend

# Database connection issue
# Verify DATABASE_URL in .env
# Check if PostgreSQL is running
docker exec streamsentinel-postgres pg_isready
```

### Kubernetes pods not running
```bash
# Check pod status
kubectl describe pod <pod-name> -n streamsentinel

# Check events
kubectl get events -n streamsentinel

# Check logs
kubectl logs <pod-name> -n streamsentinel
```

### AI features not working
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Check if AI service can connect to OpenAI
python -c "from openai import OpenAI; OpenAI(api_key='$OPENAI_API_KEY').models.list()"
```

## Performance Tuning

### Database
- Enable connection pooling
- Create indexes on frequently queried columns
- Archive old logs and metrics

### Kubernetes
- Set resource requests and limits
- Enable Horizontal Pod Autoscaler
- Use Pod Disruption Budgets

### Monitoring
- Adjust scrape intervals based on needs
- Set retention policies for metrics
- Archive old Grafana dashboards

## Security Considerations

1. **Secrets**: Store in secure vault (e.g., Vault, AWS Secrets Manager)
2. **TLS**: Use HTTPS for all external communications
3. **RBAC**: Implement fine-grained role-based access control
4. **Input Validation**: Validate all user inputs
5. **Rate Limiting**: Implement rate limiting on APIs
6. **Audit Logging**: Log all admin actions
7. **Backup**: Regular database backups
8. **Updates**: Keep dependencies up to date

## Support & Documentation

- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- GitHub: [Repository URL]

## License

MIT License - see LICENSE file for details

## Contributors

- AI Team
- Backend Team
- DevOps Team

---

**Last Updated**: July 2026
**Version**: 1.0.0
