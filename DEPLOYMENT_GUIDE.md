# Deployment Guide - Research Funding & Innovation Platform

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database backups tested
- [ ] SSL certificates obtained
- [ ] Domain name configured
- [ ] Monitoring & alerting setup
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation reviewed

## Development Environment

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd Research-Funding-PlatformCC

# Setup backend
cd backend
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# In new terminal - Setup frontend
cd frontend
cp .env.example .env
npm install
npm run dev

# Services available at:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Docker Deployment

### Using Docker Compose (Recommended for Development)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up (including volumes)
docker-compose down -v
```

### Using Kubernetes (Production)

```bash
# Build images
docker build -t funding-platform:backend backend/
docker build -t funding-platform:frontend frontend/

# Push to registry
docker tag funding-platform:backend your-registry/funding-platform:backend
docker push your-registry/funding-platform:backend

# Deploy
kubectl apply -f k8s/
```

## AWS Deployment

### RDS Setup

```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
  --db-instance-identifier funding-platform-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password <password> \
  --allocated-storage 100
```

### ElastiCache Setup

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id funding-platform-cache \
  --cache-node-type cache.t3.micro \
  --engine redis
```

### EC2 Deployment

```bash
# Connect to EC2
ssh -i your-key.pem ec2-user@your-instance

# Install dependencies
sudo yum update
sudo yum install python3 python3-venv nodejs npm

# Clone and deploy
git clone <repository-url>
cd Research-Funding-PlatformCC
./scripts/deploy.sh
```

## Azure Deployment

### App Service Deployment

```bash
# Create resource group
az group create --name funding-platform --location eastus

# Create App Service
az appservice plan create \
  --name funding-platform-plan \
  --resource-group funding-platform \
  --sku B2

# Deploy backend
az webapp create \
  --resource-group funding-platform \
  --plan funding-platform-plan \
  --name funding-platform-api \
  --runtime "PYTHON|3.10"

# Deploy frontend
az staticwebapp create \
  --name funding-platform-web \
  --resource-group funding-platform
```

## Google Cloud Deployment

### Cloud Run Deployment

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/funding-platform

# Deploy backend
gcloud run deploy funding-platform-api \
  --image gcr.io/PROJECT_ID/funding-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend to Cloud Storage
gsutil mb gs://funding-platform-web
gcloud storage cp -r frontend/dist/* gs://funding-platform-web/
```

## Manual Server Deployment

### Ubuntu/Debian Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-venv python3-pip git

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Redis
sudo apt install redis-server

# Install Nginx
sudo apt install nginx

# Clone repository
git clone <repository-url>
cd Research-Funding-PlatformCC

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# Setup frontend (in new terminal)
cd frontend
npm install
npm run build
```

### Nginx Configuration

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        root /var/www/funding-platform/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## SSL/TLS Setup

### Using Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renew
sudo certbot renew --dry-run
```

## Monitoring & Logging

### Prometheus Setup

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'funding-platform'
    static_configs:
      - targets: ['localhost:8000']
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

```bash
# Docker Compose for ELK
docker-compose -f docker-compose.elk.yml up -d
```

## Database Backups

### Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="funding_platform"

mkdir -p $BACKUP_DIR

# PostgreSQL Backup
pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.sql.gz s3://your-bucket/backups/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

### Restore from Backup

```bash
# Restore PostgreSQL
gunzip < backup_20240803_120000.sql.gz | psql -U postgres funding_platform
```

## Performance Optimization

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_funding_agency ON funding_opportunities(agency);
CREATE INDEX idx_funding_deadline ON funding_opportunities(deadline);
CREATE INDEX idx_user_profile ON research_profiles(user_id);

-- Analyze
ANALYZE funding_opportunities;
ANALYZE research_profiles;
```

### Caching Strategy

```python
# Redis cache configuration
from redis import Redis

redis_client = Redis(host='localhost', port=6379, db=0)

# Cache funding opportunities
redis_client.setex('funding:opportunities:list', 3600, json.dumps(opportunities))

# Cache user recommendations
redis_client.setex(f'recommendations:user:{user_id}', 7200, json.dumps(recommendations))
```

## Scaling Strategies

### Horizontal Scaling

- Use load balancer (NGINX, HAProxy, AWS LB)
- Deploy multiple backend instances
- Use database replication
- Implement connection pooling

### Vertical Scaling

- Upgrade server resources
- Optimize database queries
- Increase cache size
- Upgrade network bandwidth

## Troubleshooting Deployment

### Common Issues

**Database Connection Fails**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U postgres -d funding_platform
```

**API Not Responding**
```bash
# Check process
ps aux | grep gunicorn

# View logs
tail -f /var/log/gunicorn/error.log
```

**Frontend Not Loading**
```bash
# Check Nginx
sudo systemctl status nginx

# View error log
sudo tail -f /var/log/nginx/error.log
```

## Maintenance

### Regular Tasks

- [ ] Monitor disk space
- [ ] Review error logs
- [ ] Update dependencies
- [ ] Backup databases
- [ ] Security updates
- [ ] Performance tuning

### Monthly

- [ ] Database optimization
- [ ] Log rotation
- [ ] Certificate renewal check
- [ ] Security audit

## Rollback Procedure

```bash
# If deployment fails
git revert <commit-hash>
docker-compose down
docker-compose up -d
```

## Monitoring Commands

```bash
# System resources
htop

# Disk usage
df -h

# PostgreSQL connections
SELECT count(*) FROM pg_stat_activity;

# Redis memory
redis-cli INFO memory

# Nginx connections
netstat -an | grep ESTABLISHED | wc -l
```

## Support

For deployment issues:
- Check logs: `/var/log/`
- Review documentation: `/docs/`
- Contact support: support@example.com
